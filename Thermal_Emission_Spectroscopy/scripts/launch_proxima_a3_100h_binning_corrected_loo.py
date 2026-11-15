"""Run the two authorized corrected-bin A3-100 h molecular ablations.

This scoped supervisor performs MPI8/MPI7 setup-only preflights, checks their
shared priors against the corrected full retrieval, then starts both samplers
at once (15 ranks total). It never resumes or automatically retries a run.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[2]
PROJECT = Path("Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1")
CAMPAIGN_REL = PROJECT / "retrievals/a3_100h_binning_corrected_loo_20261019"
CAMPAIGN = ROOT / CAMPAIGN_REL
SCRATCH = Path("/home/dasan/exofarm_a3_100h_binning_corrected_loo_20261019")
DATASET_REL = PROJECT / "life_data/LIFE_proxima_A3_100h.dat"
DATASET_SHA256 = "78662546181a5b74391a14b7b73ae80d879200a74db6a4bc5338e3ce7eee4705"
FULL_CAMPAIGN_REL = PROJECT / "retrievals/a3_100h_binning_corrected_mpi14_resume_20261018"
FULL_STEM = "proxima_A3_100h_O2_fixedBlack1bar_noxtol_BIN1_20261017"
FULL_RESULT_REL = FULL_CAMPAIGN_REL / "products/results" / f"{FULL_STEM}_results.txt"
FULL_STATS_REL = FULL_CAMPAIGN_REL / "products/MultiNest_raw" / f"{FULL_STEM}-stats.dat"
FULL_CONFIG_REL = FULL_CAMPAIGN_REL / "resolved_configuration.json"
FULL_STATE_REL = FULL_CAMPAIGN_REL / "campaign_state.json"
CONDA_PREFIX = Path("/home/dasan/anaconda3/envs/POSEIDON")
CONDA_INIT = "/home/dasan/anaconda3/etc/profile.d/conda.sh"
POSEIDON_INPUT_DATA = "/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs"
PYSYN_CDBS = "/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids"
RUNNER = ROOT / "Thermal_Emission_Spectroscopy/scripts/run_life_retrieval_a3_100h_binning_corrected_loo.py"
TAGS = {
    "NH3": "_O2_fixedBlack1bar_noxtol_BIN1_20261019_noNH3",
    "N2O": "_O2_fixedBlack1bar_noxtol_BIN1_20261019_noN2O",
}
RANKS = {"NH3": 8, "N2O": 7}
MEM_GIB = 1024 * 1024  # /proc/meminfo reports KiB.


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n",
                         encoding="utf-8")
    os.replace(temporary, path)


MANIFEST_FIELDS = (
    "run_id", "excluded_species", "mpi_ranks", "dataset_rel",
    "dataset_sha256_expected", "baseline_full_results", "output_tag",
    "model_name", "run_dir", "archive_dir", "configuration_json",
    "launch_record_json",
    "operator_preflight", "operator_runtime", "preflight_status",
    "preflight_return_code", "status", "pid", "pid_file", "launch_log",
    "start_utc", "end_utc", "elapsed_seconds", "return_code",
    "replacements", "evaluations", "posterior_samples", "error",
)


def save_state(state: dict, cases: list[dict]) -> None:
    state["updated_utc"] = utc_now()
    write_json(CAMPAIGN / "campaign_state.json", state)
    temporary = CAMPAIGN / "manifest.csv.tmp"
    with temporary.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=MANIFEST_FIELDS,
                                extrasaction="ignore")
        writer.writeheader()
        writer.writerows(cases)
    os.replace(temporary, CAMPAIGN / "manifest.csv")


def parse_stats(path: Path) -> tuple[float, float]:
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(
        r"Nested Sampling Global Log-Evidence\s*:\s*"
        r"([-+\d.eE]+)\s*\+/-\s*([-+\d.eE]+)", text, re.IGNORECASE,
    )
    if not match:
        raise ValueError(f"MultiNest evidence not found in {path}")
    return float(match.group(1)), float(match.group(2))


def verify_full_baseline() -> dict:
    dataset = ROOT / DATASET_REL
    result_path = ROOT / FULL_RESULT_REL
    stats_path = ROOT / FULL_STATS_REL
    config_path = ROOT / FULL_CONFIG_REL
    state_path = ROOT / FULL_STATE_REL
    for path in (dataset, result_path, stats_path, config_path, state_path):
        if not path.is_file() or path.stat().st_size == 0:
            raise FileNotFoundError(f"Required corrected full-model evidence missing: {path}")
    if sha256(dataset) != DATASET_SHA256:
        raise ValueError("A3-100 h dataset SHA-256 differs from the frozen realization")
    full_state = json.loads(state_path.read_text(encoding="utf-8"))
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if full_state.get("exit_code") != 0 or full_state.get("preflight") != "PASS_MPI14_MPICH_HYDRA":
        raise ValueError("Corrected full retrieval has no successful final run/retry")
    if (
        config.get("dataset_sha256") != DATASET_SHA256
        or config.get("n_live") != 800
        or config.get("declared_dimension") != 15
        or config.get("effective_free_dimension") != 14
        or config.get("R") != 10000
        or config.get("wl_min") != 3.0
        or config.get("wl_max") != 20.0
        or config.get("surface_pressure_mode") != "fixed-black"
        or config.get("error_inflation") != "none"
        or config.get("x_profile") != "isochem"
    ):
        raise ValueError("Corrected full retrieval configuration does not match this scope")
    text = result_path.read_text(encoding="utf-8", errors="replace")
    if f"Model: {FULL_STEM}" not in text or "N_params = 15" not in text or "N_live = 800" not in text:
        raise ValueError("Corrected full retrieval result metadata is inconsistent")
    result_evidence = re.search(r"->\s*ln\s*Z\s*=\s*([-+\d.eE]+)\s*\+/-\s*([-+\d.eE]+)", text)
    if not result_evidence:
        raise ValueError("Corrected full retrieval result has no ln Z")
    chi2_evidence = re.search(r"->\s*chi\^2_red\s*=\s*([-+\d.eE]+)", text)
    if not chi2_evidence:
        raise ValueError("Corrected full retrieval result has no reduced chi-square")
    lnz_stats, err_stats = parse_stats(stats_path)
    if abs(lnz_stats - float(result_evidence.group(1))) > 0.01:
        raise ValueError("Corrected full result and MultiNest stats ln Z disagree")
    if abs(err_stats - float(result_evidence.group(2))) > 0.01:
        raise ValueError("Corrected full result and MultiNest stats errors disagree")
    return {
        "campaign": FULL_CAMPAIGN_REL.as_posix(),
        "result": FULL_RESULT_REL.as_posix(),
        "stats": FULL_STATS_REL.as_posix(),
        "configuration": FULL_CONFIG_REL.as_posix(),
        "state_status": full_state.get("status"),
        "acceptance": full_state.get("acceptance"),
        "dataset_sha256": DATASET_SHA256,
        "lnz": lnz_stats,
        "lnz_error": err_stats,
        "chi2_red": float(chi2_evidence.group(1)),
        "n_params_declared": 15,
        "effective_free_parameters": 14,
        "n_live": 800,
        "note": "Completed matched baseline; independent full audit remains pending.",
    }


def build_cases() -> list[dict]:
    cases = []
    for species in ("NH3", "N2O"):
        run_id = f"A3_100h_no_{species}"
        model_name = f"proxima_A3_100h{TAGS[species]}"
        cases.append({
            "run_id": run_id,
            "scenario": "A3",
            "hours": 100,
            "excluded_species": species,
            "mpi_ranks": RANKS[species],
            "dataset_rel": DATASET_REL.as_posix(),
            "dataset_sha256_expected": DATASET_SHA256,
            "baseline_full_results": FULL_RESULT_REL.as_posix(),
            "output_tag": TAGS[species],
            "model_name": model_name,
            "run_dir": str(SCRATCH / "runs" / run_id),
            "archive_dir": str(CAMPAIGN_REL / "runs" / run_id),
            "configuration_json": str(CAMPAIGN_REL / "resolved" / f"{run_id}.json"),
            "launch_record_json": str(CAMPAIGN_REL / "launch_records" / f"{run_id}.json"),
            "operator_preflight": str(CAMPAIGN_REL / "preflight" / "operators" / f"{run_id}.json"),
            "operator_runtime": str(CAMPAIGN_REL / "runtime" / "operators" / f"{run_id}.json"),
            "preflight_log": str(CAMPAIGN_REL / "preflight" / f"{run_id}.log"),
            "preflight_status": "not_run",
            "preflight_return_code": "",
            "preflight_parameters": "",
            "preflight_effective_free": "",
            "status": "pending",
            "pid": "",
            "pid_file": str(CAMPAIGN_REL / "pids" / f"{run_id}.pid"),
            "launch_log": str(CAMPAIGN_REL / "logs" / f"{run_id}.launch.log"),
            "start_utc": "",
            "end_utc": "",
            "elapsed_seconds": "",
            "return_code": "",
            "replacements": "",
            "evaluations": "",
            "posterior_samples": "",
            "error": "",
            "resume_checkpoint": False,
        })
    return cases


def linux_command(case: dict, *, setup_only: bool) -> str:
    python = CONDA_PREFIX / "bin/python"
    mpiexec = CONDA_PREFIX / "bin/mpiexec"
    run_dir = (
        SCRATCH / "preflight" / case["run_id"]
        if setup_only else Path(case["run_dir"])
    )
    operator_record = Path(case["operator_preflight"] if setup_only
                           else case["operator_runtime"])
    arguments = [
        str(python), "-u", str(RUNNER),
        "--operator-record", str(operator_record),
        "--campaign", "proxima", "--scenario", "A3", "--hours", "100",
        "--n-live", "800", "--error-inflation", "none",
        "--surface-pressure-mode", "fixed-black", "--include-o2",
        "--exclude-species", case["excluded_species"],
        "--x-profile", "isochem", "--output-tag", case["output_tag"],
        "--R", "10000", "--wl-min", "3.0", "--wl-max", "20.0",
        "--dataset-file", str(ROOT / DATASET_REL),
        "--run-dir", str(run_dir),
        "--configuration-json", str(ROOT / Path(case["configuration_json"])),
    ]
    if setup_only:
        arguments.append("--setup-only")
    command = [str(mpiexec), "-n", str(case["mpi_ranks"]), *arguments]
    exports = [
        "export POSEIDON_input_data=" + shlex.quote(POSEIDON_INPUT_DATA),
        "export PYSYN_CDBS=" + shlex.quote(PYSYN_CDBS),
        "export OMP_NUM_THREADS=1",
        "export OPENBLAS_NUM_THREADS=1",
        "export MKL_NUM_THREADS=1",
        "export NUMEXPR_NUM_THREADS=1",
    ]
    return "; ".join([
        "set -euo pipefail",
        "source " + shlex.quote(CONDA_INIT),
        "conda activate POSEIDON",
        *exports,
        "cd " + shlex.quote(str(ROOT)),
        "exec " + shlex.join(command),
    ])


def validate_preflight(case: dict, output: str, return_code: int) -> None:
    if return_code != 0 or "[setup-only] corrected operator, matched model and priors PASS" not in output:
        raise RuntimeError(f"setup-only preflight failed for {case['run_id']} (exit {return_code})")
    operator = json.loads((ROOT / Path(case["operator_preflight"])).read_text(encoding="utf-8"))
    if operator.get("status") != "PASS" or not operator.get("actual_poseidon_callback_bound"):
        raise RuntimeError(f"corrected operator callback did not pass for {case['run_id']}")
    if operator.get("mpi_size") != case["mpi_ranks"] or len(operator.get("mpi_rank_pids", [])) != case["mpi_ranks"]:
        raise RuntimeError(f"MPI rank-count preflight failed for {case['run_id']}")
    if operator.get("dataset_sha256") != DATASET_SHA256:
        raise RuntimeError(f"operator preflight dataset mismatch for {case['run_id']}")
    config = json.loads((ROOT / Path(case["configuration_json"])).read_text(encoding="utf-8"))
    if config.get("declared_dimension") != 14 or config.get("effective_free_dimension") != 13:
        raise RuntimeError(f"wrong model dimension in preflight for {case['run_id']}")
    case["preflight_parameters"] = config["declared_dimension"]
    case["preflight_effective_free"] = config["effective_free_dimension"]
    case["preflight_status"] = "PASS_MPI_OPERATOR_AND_MATCHED_PRIORS"
    case["preflight_return_code"] = return_code


def run_preflights(cases: list[dict], state: dict) -> None:
    for index, case in enumerate(cases, start=1):
        log_path = ROOT / Path(case["preflight_log"])
        operator_path = ROOT / Path(case["operator_preflight"])
        config_path = ROOT / Path(case["configuration_json"])
        for path in (log_path, operator_path):
            if path.exists():
                raise FileExistsError(f"Refusing to overwrite preflight evidence: {path}")
        if config_path.exists():
            raise FileExistsError(f"Refusing to overwrite resolved config: {config_path}")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        command = linux_command(case, setup_only=True)
        result = subprocess.run(
            ["/bin/bash", "-lc", command], cwd=str(ROOT),
            capture_output=True, text=True,
        )
        output = result.stdout + result.stderr
        log_path.write_text(
            f"[preflight_utc] {utc_now()}\n[command] {command}\n{output}",
            encoding="utf-8", errors="replace",
        )
        try:
            validate_preflight(case, output, result.returncode)
        except Exception as exc:
            case["preflight_status"] = "FAIL"
            case["preflight_return_code"] = result.returncode
            case["error"] = f"{type(exc).__name__}: {exc}"
            state["campaign_status"] = "PREFLIGHT_FAILED"
            state["halt_reason"] = case["error"]
            save_state(state, cases)
            raise
        save_state(state, cases)
        print(f"[preflight {index}/2 PASS] {case['run_id']} "
              f"MPI{case['mpi_ranks']} declared=14 free=13", flush=True)


def read_meminfo() -> dict[str, int]:
    values = {}
    for line in Path("/proc/meminfo").read_text(encoding="ascii").splitlines():
        key, _, rest = line.partition(":")
        fields = rest.split()
        if fields and fields[0].isdigit():
            values[key] = int(fields[0])
    return values


def resource_gate() -> dict:
    info = read_meminfo()
    snapshot = {
        "logical_cpus": os.cpu_count() or 0,
        "mem_available_kib": info.get("MemAvailable", 0),
        "swap_free_kib": info.get("SwapFree", 0),
        "observed_utc": utc_now(),
    }
    if snapshot["logical_cpus"] < 16:
        raise RuntimeError("resource gate requires 16 visible logical CPUs for 15 MPI ranks plus supervisor")
    if snapshot["mem_available_kib"] < 12 * MEM_GIB:
        raise RuntimeError("resource gate requires at least 12 GiB MemAvailable")
    if snapshot["swap_free_kib"] < 1 * MEM_GIB:
        raise RuntimeError("resource gate requires at least 1 GiB free swap")
    return snapshot


def process_tree(root_pid: int) -> list[int]:
    children: dict[int, list[int]] = {}
    try:
        entries = list(Path("/proc").iterdir())
    except OSError:
        return []
    for entry in entries:
        if not entry.name.isdigit():
            continue
        try:
            stat = (entry / "stat").read_text(encoding="ascii")
            tail = stat[stat.rfind(")") + 2:].split()
            parent = int(tail[1])
            children.setdefault(parent, []).append(int(entry.name))
        except (OSError, ValueError, IndexError):
            continue
    result = []
    stack = [root_pid]
    seen = set()
    while stack:
        pid = stack.pop()
        if pid in seen:
            continue
        seen.add(pid)
        result.append(pid)
        stack.extend(children.get(pid, []))
    return result


def pss_kib(pid: int) -> int:
    try:
        for line in Path(f"/proc/{pid}/smaps_rollup").read_text(encoding="ascii").splitlines():
            if line.startswith("Pss:"):
                return int(line.split()[1])
    except (OSError, ValueError, IndexError):
        pass
    return 0


def read_multinest_progress(case: dict) -> tuple[int | None, int | None, int]:
    raw = Path(case["run_dir"]) / "POSEIDON_output/proxima_b_earthlike/retrievals/MultiNest_raw"
    resume = raw / f"{case['model_name']}-resume.dat"
    samples = raw / f"{case['model_name']}-post_equal_weights.dat"
    replacements = evaluations = None
    if resume.is_file():
        lines = [line.split() for line in resume.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()]
        if len(lines) > 1 and len(lines[1]) >= 2:
            try:
                replacements, evaluations = int(lines[1][0]), int(lines[1][1])
            except ValueError:
                pass
    sample_rows = 0
    if samples.is_file():
        try:
            with samples.open("rb") as stream:
                sample_rows = sum(1 for _ in stream)
        except OSError:
            pass
    return replacements, evaluations, max(0, sample_rows - 1)


def resource_sample(running: dict[str, tuple[dict, subprocess.Popen, float]]) -> dict:
    info = read_meminfo()
    cases = {}
    for run_id, (case, process, _) in running.items():
        pids = process_tree(process.pid)
        cases[run_id] = {
            "pid_tree_count": len(pids),
            "pss_kib": sum(pss_kib(pid) for pid in pids),
            "replacements": read_multinest_progress(case)[0],
            "evaluations": read_multinest_progress(case)[1],
            "posterior_rows": read_multinest_progress(case)[2],
        }
    return {
        "observed_utc": utc_now(),
        "mem_available_kib": info.get("MemAvailable", 0),
        "swap_free_kib": info.get("SwapFree", 0),
        "cases": cases,
    }


def launch_case(case: dict, state: dict, cases: list[dict]) -> tuple[subprocess.Popen, float]:
    run_dir = Path(case["run_dir"])
    archive = ROOT / Path(case["archive_dir"])
    for path in (run_dir, archive):
        if path.exists():
            raise FileExistsError(f"Refusing to reuse existing run output: {path}")
    run_dir.mkdir(parents=True, exist_ok=False)
    log_path = ROOT / Path(case["launch_log"])
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if log_path.exists():
        raise FileExistsError(f"Refusing to overwrite launch log: {log_path}")
    command = linux_command(case, setup_only=False)
    config_record = {
        "run_id": case["run_id"],
        "scenario": "A3",
        "hours": 100,
        "excluded_species": case["excluded_species"],
        "mpi_ranks": case["mpi_ranks"],
        "dataset_sha256": DATASET_SHA256,
        "baseline_full_lnZ": state["baseline_full"]["lnz"],
        "baseline_full_lnZ_error": state["baseline_full"]["lnz_error"],
        "n_live": 800,
        "evidence_tolerance": 0.5,
        "R": 10000,
        "wavelength_range_um": [3.0, 20.0],
        "x_profile": "isochem",
        "surface": "explicit opaque black surface fixed at 1 bar",
        "error_inflation": "none",
        "declared_parameters": 14,
        "effective_free_parameters": 13,
        "resume_checkpoint": False,
        "operator": "midpoint-edge photon overlap; energy conversion at exact channel centre",
        "command": command,
        "created_utc": utc_now(),
    }
    launch_record_path = ROOT / Path(case["launch_record_json"])
    launch_record_path.parent.mkdir(parents=True, exist_ok=True)
    with launch_record_path.open("x", encoding="utf-8") as stream:
        json.dump(config_record, stream, indent=2, sort_keys=True)
        stream.write("\n")
    with log_path.open("x", encoding="utf-8") as log:
        log.write(f"[launch_utc] {utc_now()}\n[run_id] {case['run_id']}\n"
                  f"[MPI ranks] {case['mpi_ranks']}\n[dataset SHA-256] {DATASET_SHA256}\n"
                  f"[command] {command}\n")
        log.flush()
        process = subprocess.Popen(
            ["/bin/bash", "-lc", command], cwd=str(ROOT), stdout=log,
            stderr=subprocess.STDOUT, start_new_session=True,
        )
    case["status"] = "running"
    case["pid"] = str(process.pid)
    case["start_utc"] = utc_now()
    pid_path = ROOT / Path(case["pid_file"])
    pid_path.parent.mkdir(parents=True, exist_ok=True)
    with pid_path.open("x", encoding="ascii") as stream:
        stream.write(f"{process.pid}\n")
    state["active_run_ids"].append(case["run_id"])
    save_state(state, cases)
    print(f"[launched] {case['run_id']} MPI{case['mpi_ranks']} pid={process.pid}", flush=True)
    return process, time.monotonic()


def harvest_case(case: dict) -> None:
    source = Path(case["run_dir"])
    target = ROOT / Path(case["archive_dir"])
    if not source.is_dir() or not any(source.iterdir()):
        raise RuntimeError(f"Successful process has no products in scratch: {source}")
    if target.exists():
        raise FileExistsError(f"Refusing to overwrite archived run: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, symlinks=True)


def finish_runs(cases: list[dict], state: dict, running: dict,
                started_by_run: dict[str, float]) -> None:
    sample_path = CAMPAIGN / "resources.jsonl"
    last_sample = 0.0
    halt_reason = ""
    while running:
        now = time.monotonic()
        if now - last_sample >= 60:
            sample = resource_sample(running)
            with sample_path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(sample, sort_keys=True) + "\n")
            state["latest_resources"] = sample
            for run_id, metrics in sample["cases"].items():
                case = next(item for item in cases if item["run_id"] == run_id)
                for key in ("replacements", "evaluations", "posterior_rows"):
                    if metrics[key] is not None:
                        case[key] = metrics[key]
            save_state(state, cases)
            last_sample = now

        completed = []
        for run_id, (case, process, started) in list(running.items()):
            return_code = process.poll()
            if return_code is None:
                continue
            completed.append(run_id)
            case["end_utc"] = utc_now()
            case["elapsed_seconds"] = f"{now - started:.1f}"
            case["return_code"] = return_code
            if run_id in state["active_run_ids"]:
                state["active_run_ids"].remove(run_id)
            if return_code == 0:
                case["status"] = "harvesting"
                save_state(state, cases)
                try:
                    harvest_case(case)
                    case["status"] = "complete_pending_validation"
                    print(f"[completed+archived] {run_id}", flush=True)
                except Exception as exc:
                    case["status"] = "harvest_failed"
                    case["error"] = f"{type(exc).__name__}: {exc}"
                    halt_reason = f"harvest failure for {run_id}: {case['error']}"
            else:
                case["status"] = "failed"
                case["error"] = f"MPI retrieval exited {return_code}; scratch and logs preserved; no retry"
                halt_reason = f"{run_id}: {case['error']}"
                print(f"[FAILED] {halt_reason}", flush=True)
            if halt_reason:
                state["halt_reason"] = halt_reason
                state["campaign_status"] = "HALTED_FAILURE"
            save_state(state, cases)
        for run_id in completed:
            running.pop(run_id, None)
        if running:
            time.sleep(20)

    if halt_reason:
        state["campaign_status"] = "HALTED_FAILURE"
    elif all(case["status"] == "complete_pending_validation" for case in cases):
        state["campaign_status"] = "COMPLETE_PENDING_VALIDATION"
        state["completed_utc"] = utc_now()
    else:
        state["campaign_status"] = "INCOMPLETE"
    save_state(state, cases)


def main() -> int:
    state_path = CAMPAIGN / "campaign_state.json"
    if state_path.exists():
        raise SystemExit(f"Refusing to launch duplicate campaign: {state_path}")
    if not CAMPAIGN.is_dir():
        raise SystemExit(f"Campaign directory must be pre-created: {CAMPAIGN}")
    baseline = verify_full_baseline()
    runtime_pid_path = CAMPAIGN / "supervisor.runtime.pid"
    if runtime_pid_path.exists():
        raise SystemExit(f"Refusing to overwrite supervisor PID record: {runtime_pid_path}")
    with runtime_pid_path.open("x", encoding="ascii") as stream:
        stream.write(f"{os.getpid()}\n")
    dataset = ROOT / DATASET_REL
    cases = build_cases()
    state = {
        "campaign_id": "proxima_A3_100h_corrected_bin_NH3_N2O_ablations_20261019",
        "campaign_status": "PREFLIGHT_RUNNING",
        "acceptance": "PENDING",
        "objective": (
            "Compare corrected-bin A3-100 h full retrieval against the matched "
            "no-NH3 and no-N2O models on the same LIFE realization."
        ),
        "created_utc": utc_now(),
        "supervisor_pid": os.getpid(),
        "dataset_rel": DATASET_REL.as_posix(),
        "dataset_sha256": DATASET_SHA256,
        "dataset_seed": 129315834,
        "baseline_full": baseline,
        "n_live": 800,
        "evidence_tolerance": 0.5,
        "R": 10000,
        "native_wavelength_range_um": [3.0, 20.0],
        "operator": "midpoint-edge photon overlap; energy conversion at exact channel centre",
        "x_profile": "isochem",
        "surface": "explicit black surface fixed at 1 bar",
        "error_inflation": "none",
        "declared_parameters_full": 15,
        "effective_free_parameters_full": 14,
        "declared_parameters_ablations": 14,
        "effective_free_parameters_ablations": 13,
        "rank_allocation": {"A3_100h_no_NH3": 8, "A3_100h_no_N2O": 7},
        "total_mpi_ranks": 15,
        "checkpoint_reuse": False,
        "max_parallel": 2,
        "active_run_ids": [],
        "runs": cases,
        "code_sha256": {
            "supervisor": sha256(Path(__file__).resolve()),
            "corrected_ablation_runner": sha256(RUNNER),
        },
    }
    selected_scope = {
        "campaign": state["campaign_id"],
        "authorized_runs": [
            {"run_id": case["run_id"], "excluded_species": case["excluded_species"],
             "mpi_ranks": case["mpi_ranks"], "declared_parameters": 14,
             "effective_free_parameters": 13}
            for case in cases
        ],
        "dataset": DATASET_REL.as_posix(),
        "dataset_sha256": DATASET_SHA256,
        "dataset_seed": 129315834,
        "matched_baseline": baseline,
        "operator": state["operator"],
        "checkpoint_reuse": False,
    }
    if (CAMPAIGN / "selected_scope.json").exists():
        raise SystemExit("Refusing to overwrite existing selected_scope.json")
    write_json(CAMPAIGN / "selected_scope.json", selected_scope)
    save_state(state, cases)
    try:
        print("[campaign] corrected-bin A3 100 h; preflight MPI8 then MPI7", flush=True)
        run_preflights(cases, state)
        state["preflight_status"] = "PASS_BOTH_MPI_OPERATOR_PRIORS"
        state["campaign_status"] = "RESOURCE_GATE"
        state["resource_gate"] = resource_gate()
        state["campaign_status"] = "RUNNING"
        state["launch_utc"] = utc_now()
        save_state(state, cases)
        running = {}
        started = {}
        for case in cases:
            process, started_at = launch_case(case, state, cases)
            running[case["run_id"]] = (case, process, started_at)
            started[case["run_id"]] = started_at
        state["all_variants_launched_utc"] = utc_now()
        save_state(state, cases)
        print("[sampling] both variants launched; 15 MPI ranks total", flush=True)
        finish_runs(cases, state, running, started)
    except Exception as exc:
        state["error"] = f"{type(exc).__name__}: {exc}"
        if state.get("campaign_status") not in {"PREFLIGHT_FAILED", "HALTED_FAILURE"}:
            state["campaign_status"] = "HALTED_FAILURE"
        state["halt_reason"] = state.get("halt_reason") or state["error"]
        save_state(state, cases)
        print(f"[SUPERVISOR_ERROR] {state['error']}", file=sys.stderr, flush=True)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
