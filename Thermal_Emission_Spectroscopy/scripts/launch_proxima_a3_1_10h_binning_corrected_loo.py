"""Run six fresh A3 1 h/10 h corrected-bin models in two MPI5 waves."""

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
PROJECT_REL = Path("Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1")
PROJECT = ROOT / PROJECT_REL
CAMPAIGN_REL = PROJECT_REL / "retrievals/a3_1_10h_binning_corrected_loo_20261020_r03"
CAMPAIGN = ROOT / CAMPAIGN_REL
RETRIEVALS = ROOT / PROJECT_REL / "retrievals"
SCRATCH = Path("/home/dasan/exofarm_a3_1_10h_binning_corrected_loo_20261020_r03")
RUNNER = ROOT / "Thermal_Emission_Spectroscopy/scripts/run_life_retrieval_a3_short_binning_corrected.py"
SUPERVISOR = Path(__file__).resolve()
OPERATOR_SOURCE = ROOT / "Thermal_Emission_Spectroscopy/scripts/life_bin_operator_diagnostic.py"
LEGACY_RUNNER = ROOT / "Thermal_Emission_Spectroscopy/scripts/run_life_retrieval.py"
CONDA_PREFIX = Path("/home/dasan/anaconda3/envs/POSEIDON")
CONDA_INIT = "/home/dasan/anaconda3/etc/profile.d/conda.sh"
POSEIDON_INPUT_DATA = "/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs"
PYSYN_CDBS = "/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids"
NATIVE_EMISSION = PROJECT / "forward_emission/A3_emission.npz"
LIFE_BINNED = PROJECT / "lifesim/life_classic_binned_products.npz"
BASELINE_100H = CAMPAIGN.parents[0] / "a3_100h_binning_corrected_mpi14_resume_20261018"
BASELINE_100H_REL = BASELINE_100H.relative_to(ROOT)
BASELINE_STEM = "proxima_A3_100h_O2_fixedBlack1bar_noxtol_BIN1_20261017"
BASELINE_DATASET_SHA256 = "78662546181a5b74391a14b7b73ae80d879200a74db6a4bc5338e3ce7eee4705"
DATASETS = {
    1: ("LIFE_proxima_A3_1h_O2_fixedBlack1bar_official.dat",
        "a3043e5de76a834983949e6eca12636ea4de174ebdb2db0853155282c100dee2"),
    10: ("LIFE_proxima_A3_10h.dat",
         "46a026504b9b9521fa29407a501169b9d3cfc433de40a91b8ade86d7767abb5b"),
}
RANKS_PER_RUN = 5
MAX_PARALLEL = 3
MEM_GIB = 1024 * 1024
MIN_MEM_AVAILABLE_GIB = 24
MIN_SWAP_FREE_GIB = 2
OPERATOR_DESCRIPTION = (
    "midpoint-edge photon overlap; energy conversion at exact channel centre"
)
MODEL_TAGS = {
    "full": "full",
    "NH3": "noNH3",
    "N2O": "noN2O",
}

MANIFEST_FIELDS = (
    "run_id", "scenario", "hours", "model", "excluded_species", "mpi_ranks",
    "declared_parameters", "effective_free_parameters", "dataset_rel",
    "dataset_sha256_expected", "matched_full_run", "output_tag", "model_name",
    "run_dir", "archive_dir", "configuration_json", "operator_preflight",
    "operator_runtime", "preflight_log", "preflight_status", "preflight_return_code",
    "status", "pid", "pid_file", "launch_log", "start_utc", "end_utc",
    "elapsed_seconds", "return_code", "replacements", "evaluations",
    "posterior_rows", "error",
)


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


def build_cases() -> list[dict]:
    cases: list[dict] = []
    for hours in (1, 10):
        dataset_name, dataset_hash = DATASETS[hours]
        for excluded in (None, "NH3", "N2O"):
            model_key = excluded or "full"
            model_label = MODEL_TAGS[model_key]
            run_id = f"A3_{hours}h_{'full' if excluded is None else 'no_' + excluded}"
            output_tag = (
                f"_O2_fixedBlack1bar_noxtol_BIN1_20261020_{hours}h_{model_label}"
            )
            model_name = f"proxima_A3_{hours}h{output_tag}"
            declared, free = (15, 14) if excluded is None else (14, 13)
            cases.append({
                "run_id": run_id,
                "scenario": "A3",
                "hours": hours,
                "model": model_label,
                "excluded_species": excluded or "",
                "mpi_ranks": RANKS_PER_RUN,
                "declared_parameters": declared,
                "effective_free_parameters": free,
                "dataset_rel": (PROJECT_REL / "life_data" / dataset_name).as_posix(),
                "dataset_sha256_expected": dataset_hash,
                "matched_full_run": f"A3_{hours}h_full",
                "output_tag": output_tag,
                "model_name": model_name,
                "run_dir": str(SCRATCH / "runs" / run_id),
                "archive_dir": (CAMPAIGN_REL / "runs" / run_id).as_posix(),
                "configuration_json": (CAMPAIGN_REL / "resolved" / f"{run_id}.json").as_posix(),
                "operator_preflight": (CAMPAIGN_REL / "preflight/operators" / f"{run_id}.json").as_posix(),
                "operator_runtime": (CAMPAIGN_REL / "runtime/operators" / f"{run_id}.json").as_posix(),
                "preflight_log": (CAMPAIGN_REL / "preflight" / f"{run_id}.log").as_posix(),
                "preflight_status": "not_run",
                "preflight_return_code": "",
                "status": "pending",
                "pid": "",
                "pid_file": (CAMPAIGN_REL / "pids" / f"{run_id}.pid").as_posix(),
                "launch_log": (CAMPAIGN_REL / "logs" / f"{run_id}.launch.log").as_posix(),
                "start_utc": "",
                "end_utc": "",
                "elapsed_seconds": "",
                "return_code": "",
                "replacements": "",
                "evaluations": "",
                "posterior_rows": "",
                "error": "",
                "resume_checkpoint": False,
            })
    return cases


def verify_corrected_100h_reference() -> dict:
    paths = {
        "dataset": PROJECT / "life_data/LIFE_proxima_A3_100h.dat",
        "result": BASELINE_100H / "products/results" / f"{BASELINE_STEM}_results.txt",
        "stats": BASELINE_100H / "products/MultiNest_raw" / f"{BASELINE_STEM}-stats.dat",
        "configuration": BASELINE_100H / "resolved_configuration.json",
        "state": BASELINE_100H / "campaign_state.json",
    }
    for name, path in paths.items():
        if not path.is_file() or path.stat().st_size == 0:
            raise FileNotFoundError(f"Corrected A3-100 h reference missing {name}: {path}")
    if sha256(paths["dataset"]) != BASELINE_DATASET_SHA256:
        raise ValueError("Corrected A3-100 h baseline dataset hash changed")
    state = json.loads(paths["state"].read_text(encoding="utf-8"))
    config = json.loads(paths["configuration"].read_text(encoding="utf-8"))
    if state.get("exit_code") != 0 or state.get("preflight") != "PASS_MPI14_MPICH_HYDRA":
        raise ValueError("Corrected A3-100 h reference lacks successful final execution")
    expected = {
        "dataset_sha256": BASELINE_DATASET_SHA256, "n_live": 800,
        "declared_dimension": 15, "effective_free_dimension": 14,
        "R": 10000, "wl_min": 3.0, "wl_max": 20.0,
        "surface_pressure_mode": "fixed-black", "error_inflation": "none",
        "x_profile": "isochem",
    }
    for key, value in expected.items():
        if config.get(key) != value:
            raise ValueError(f"Corrected A3-100 h reference configuration mismatch: {key}")
    text = paths["result"].read_text(encoding="utf-8", errors="replace")
    match = re.search(r"->\s*ln\s*Z\s*=\s*([-+\d.eE]+)\s*\+/-\s*([-+\d.eE]+)", text)
    if not match or "N_params = 15" not in text or "N_live = 800" not in text:
        raise ValueError("Corrected A3-100 h result metadata/evidence is inconsistent")
    return {
        "campaign": BASELINE_100H_REL.as_posix(),
        "dataset_sha256": BASELINE_DATASET_SHA256,
        "configuration": config,
        "lnz": float(match.group(1)),
        "lnz_error": float(match.group(2)),
        "acceptance": state.get("acceptance"),
    }


def make_command(case: dict, setup_only: bool) -> str:
    python = CONDA_PREFIX / "bin/python"
    mpiexec = CONDA_PREFIX / "bin/mpiexec"
    run_dir = (SCRATCH / "preflight" / case["run_id"] if setup_only
               else Path(case["run_dir"]))
    operator_record = Path(case["operator_preflight"] if setup_only
                           else case["operator_runtime"])
    dataset = ROOT / Path(case["dataset_rel"])
    config = ROOT / Path(case["configuration_json"])
    arguments = [
        str(python), "-u", str(RUNNER), "--operator-record", str(operator_record),
        "--campaign", "proxima", "--scenario", "A3", "--hours", str(case["hours"]),
        "--n-live", "800", "--error-inflation", "none",
        "--surface-pressure-mode", "fixed-black", "--include-o2",
        "--x-profile", "isochem", "--output-tag", case["output_tag"],
        "--R", "10000", "--wl-min", "3.0", "--wl-max", "20.0",
        "--dataset-file", str(dataset), "--run-dir", str(run_dir),
        "--configuration-json", str(config),
    ]
    if case["excluded_species"]:
        arguments.extend(("--exclude-species", case["excluded_species"]))
    if setup_only:
        arguments.append("--setup-only")
    exports = [
        "export POSEIDON_input_data=" + shlex.quote(POSEIDON_INPUT_DATA),
        "export PYSYN_CDBS=" + shlex.quote(PYSYN_CDBS),
        "export OMP_NUM_THREADS=1", "export OPENBLAS_NUM_THREADS=1",
        "export MKL_NUM_THREADS=1", "export NUMEXPR_NUM_THREADS=1",
    ]
    command = [str(mpiexec), "-n", str(RANKS_PER_RUN), *arguments]
    return "; ".join([
        "set -euo pipefail", "source " + shlex.quote(CONDA_INIT),
        "conda activate POSEIDON", *exports, "cd " + shlex.quote(str(ROOT)),
        "exec " + shlex.join(command),
    ])


def resource_snapshot() -> dict:
    values: dict[str, int] = {}
    for line in Path("/proc/meminfo").read_text(encoding="ascii").splitlines():
        key, _, rest = line.partition(":")
        fields = rest.split()
        if fields and fields[0].isdigit():
            values[key] = int(fields[0])
    return {
        "logical_cpus": os.cpu_count() or 0,
        "mem_available_kib": values.get("MemAvailable", 0),
        "swap_free_kib": values.get("SwapFree", 0),
        "observed_utc": utc_now(),
    }


def resource_gate() -> dict:
    snapshot = resource_snapshot()
    limits = []
    if snapshot["logical_cpus"] < 16:
        limits.append("requires 16 visible logical CPUs for 15 MPI ranks plus supervisor")
    if snapshot["mem_available_kib"] < MIN_MEM_AVAILABLE_GIB * MEM_GIB:
        limits.append(f"requires at least {MIN_MEM_AVAILABLE_GIB} GiB MemAvailable for three samplers")
    if snapshot["swap_free_kib"] < MIN_SWAP_FREE_GIB * MEM_GIB:
        limits.append(f"requires at least {MIN_SWAP_FREE_GIB} GiB free swap")
    if limits:
        raise RuntimeError("; ".join(limits))
    return snapshot


def foreign_sampler_processes() -> list[str]:
    patterns = ("[m]piexec", "[m]pirun", "[p]ython.*run_life_retrieval.py")
    found: list[str] = []
    for pattern in patterns:
        result = subprocess.run(["pgrep", "-af", pattern], capture_output=True, text=True)
        if result.returncode == 0:
            found.extend(line for line in result.stdout.splitlines()
                         if f"{os.getpid()} " not in line)
    return found


def wait_for_resource_gate(state: dict, cases: list[dict], wave: int) -> dict:
    while True:
        try:
            snapshot = resource_gate()
            state["resource_gate"][str(wave)] = snapshot
            state["campaign_status"] = f"RESOURCE_GATE_PASS_WAVE_{wave}"
            save_state(state, cases)
            print(f"[resource-gate PASS] wave={wave} {snapshot}", flush=True)
            return snapshot
        except RuntimeError as exc:
            snapshot = resource_snapshot()
            state["latest_resource_gate"] = {
                **snapshot, "status": "WAITING", "reason": str(exc), "wave": wave,
            }
            state["campaign_status"] = f"WAITING_FOR_RESOURCES_WAVE_{wave}"
            save_state(state, cases)
            print(f"[resource-gate waiting] wave={wave}: {exc}", flush=True)
            time.sleep(60)


def group_cases(cases: list[dict], hours: int) -> list[dict]:
    return [case for case in cases if int(case["hours"]) == hours]


def validate_config_group(cases: list[dict], hours: int) -> None:
    group = group_cases(cases, hours)
    configs = {
        case["run_id"]: json.loads((ROOT / Path(case["configuration_json"])).read_text(encoding="utf-8"))
        for case in group
    }
    full = configs[f"A3_{hours}h_full"]
    for case in group:
        excluded = case["excluded_species"]
        actual = configs[case["run_id"]]
        expected_parameters = list(full["parameters"])
        expected_species = list(full["param_species"])
        if excluded:
            expected_parameters.remove(f"log_{excluded}")
            expected_species.remove(excluded)
        if actual["parameters"] != expected_parameters or actual["param_species"] != expected_species:
            raise ValueError(f"{case['run_id']} differs from its matched full model")
        if actual["declared_dimension"] != case["declared_parameters"]:
            raise ValueError(f"Unexpected declared dimension for {case['run_id']}")
        if actual["effective_free_dimension"] != case["effective_free_parameters"]:
            raise ValueError(f"Unexpected free dimension for {case['run_id']}")
        for key in ("R", "wl_min", "wl_max", "n_live", "ev_tol",
                    "surface_pressure_mode", "error_inflation", "x_profile", "likelihood"):
            if actual.get(key) != full.get(key):
                raise ValueError(f"Matched setting {key} differs for {case['run_id']}")
        if actual["fixed_parameters"] != full["fixed_parameters"]:
            raise ValueError(f"Fixed surface parameter differs for {case['run_id']}")
        for section in ("prior_types", "prior_ranges"):
            for parameter in expected_parameters:
                if actual[section].get(parameter) != full[section].get(parameter):
                    raise ValueError(f"Shared prior {parameter} differs for {case['run_id']}")
            if excluded and f"log_{excluded}" in actual[section]:
                raise ValueError(f"Excluded prior remains in {case['run_id']}")


def run_preflights(cases: list[dict], state: dict, wave: int) -> None:
    group = group_cases(cases, (1, 10)[wave - 1])
    state["campaign_status"] = f"PREFLIGHT_RUNNING_WAVE_{wave}"
    save_state(state, cases)
    for index, case in enumerate(group, start=1):
        log_path = ROOT / Path(case["preflight_log"])
        operator_path = ROOT / Path(case["operator_preflight"])
        config_path = ROOT / Path(case["configuration_json"])
        for path in (log_path, operator_path, config_path):
            if path.exists():
                raise FileExistsError(f"Refusing to overwrite preflight evidence: {path}")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        command = make_command(case, setup_only=True)
        try:
            result = subprocess.run(
                ["/bin/bash", "-lc", command], cwd=str(ROOT),
                capture_output=True, text=True, timeout=3600,
            )
        except subprocess.TimeoutExpired as exc:
            case["preflight_status"] = "TIMEOUT"
            case["error"] = "MPI5 setup-only preflight exceeded 3600 seconds"
            log_path.write_text(
                f"[preflight_utc] {utc_now()}\n[command] {command}\n"
                f"{exc.stdout or ''}{exc.stderr or ''}\n[timeout]\n",
                encoding="utf-8", errors="replace",
            )
            state.update(campaign_status="HALTED_PREFLIGHT_FAILURE",
                         halt_reason=case["error"])
            save_state(state, cases)
            raise RuntimeError(case["error"]) from exc
        output = result.stdout + result.stderr
        log_path.write_text(
            f"[preflight_utc] {utc_now()}\n[command] {command}\n{output}",
            encoding="utf-8", errors="replace",
        )
        try:
            if result.returncode != 0 or "[setup-only] corrected operator, model and priors PASS" not in output:
                raise RuntimeError(f"MPI5 setup-only preflight failed (exit {result.returncode})")
            operator = json.loads(operator_path.read_text(encoding="utf-8"))
            config = json.loads(config_path.read_text(encoding="utf-8"))
            if operator.get("status") != "PASS" or not operator.get("actual_poseidon_callback_bound"):
                raise RuntimeError("Corrected POSEIDON callback did not pass")
            if operator.get("mpi_size") != RANKS_PER_RUN or len(operator.get("mpi_rank_pids", [])) != RANKS_PER_RUN:
                raise RuntimeError("MPI5 rank-count preflight did not pass")
            if operator.get("dataset_sha256") != case["dataset_sha256_expected"]:
                raise RuntimeError("Preflight dataset hash mismatch")
            if config.get("declared_dimension") != case["declared_parameters"] or config.get("effective_free_dimension") != case["effective_free_parameters"]:
                raise RuntimeError("Resolved dimensions differ from campaign scope")
            case["preflight_status"] = "PASS_MPI5_OPERATOR_PRIORS"
            case["preflight_return_code"] = result.returncode
        except Exception as exc:
            case["preflight_status"] = "FAIL"
            case["preflight_return_code"] = result.returncode
            case["error"] = f"{type(exc).__name__}: {exc}"
            state.update(campaign_status="HALTED_PREFLIGHT_FAILURE",
                         halt_reason=f"{case['run_id']}: {case['error']}")
            save_state(state, cases)
            raise
        save_state(state, cases)
        print(f"[preflight {index}/3 PASS] {case['run_id']} MPI5 "
              f"declared={case['declared_parameters']} free={case['effective_free_parameters']}",
              flush=True)
    validate_config_group(cases, int(group[0]["hours"]))
    state["preflight_waves"][str(wave)] = "PASS_ALL_THREE_MATCHED_MODELS"
    save_state(state, cases)


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
            parent = int(stat[stat.rfind(")") + 2:].split()[1])
            children.setdefault(parent, []).append(int(entry.name))
        except (OSError, ValueError, IndexError):
            continue
    result: list[int] = []
    stack = [root_pid]
    while stack:
        pid = stack.pop()
        if pid in result:
            continue
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


def progress(case: dict) -> tuple[int | None, int | None, int]:
    raw = Path(case["run_dir"]) / "POSEIDON_output/proxima_b_earthlike/retrievals/MultiNest_raw"
    resume = raw / f"{case['model_name']}-resume.dat"
    equal = raw / f"{case['model_name']}-post_equal_weights.dat"
    replacements = evaluations = None
    if resume.is_file():
        lines = [line.split() for line in resume.read_text(encoding="utf-8", errors="replace").splitlines()
                 if line.strip()]
        if len(lines) > 1:
            numbers = [int(float(value)) for value in lines[1]
                       if re.fullmatch(r"[-+]?\d+(?:\.0*)?", value)]
            if numbers:
                replacements = numbers[0]
                if len(numbers) > 1:
                    evaluations = numbers[1]
    rows = 0
    if equal.is_file():
        try:
            with equal.open("r", encoding="utf-8", errors="replace") as stream:
                rows = sum(1 for line in stream if line.strip())
        except OSError:
            rows = 0
    return replacements, evaluations, rows


def wait_for_wave_start(cases: list[dict], wave: int,
                        running: dict[str, tuple[dict, subprocess.Popen, float]],
                        state: dict) -> None:
    expected = {case["run_id"] for case, _, _ in running.values()}
    started: set[str] = set()
    deadline = time.monotonic() + 1800
    while expected - started and time.monotonic() < deadline:
        for run_id, (case, process, _) in running.items():
            if run_id in started:
                continue
            runtime_operator = ROOT / Path(case["operator_runtime"])
            raw = Path(case["run_dir"]) / "POSEIDON_output/proxima_b_earthlike/retrievals/MultiNest_raw"
            resume = raw / f"{case['model_name']}-resume.dat"
            launch_log = ROOT / Path(case["launch_log"])
            try:
                log_text = launch_log.read_text(encoding="utf-8", errors="replace")
            except OSError:
                log_text = ""
            if (runtime_operator.is_file() and resume.is_file() and resume.stat().st_size > 0
                    and "[corrected-operator-active]" in log_text):
                case["status"] = "sampling"
                case["sampling_confirmed_utc"] = utc_now()
                started.add(run_id)
                print(f"[sampling confirmed] {run_id} MPI5", flush=True)
            elif process.poll() is not None:
                break
        if not (expected - started):
            break
        state["sampling_start_confirmation"] = {
            "wave": wave, "confirmed_run_ids": sorted(started),
            "pending_run_ids": sorted(expected - started),
            "observed_utc": utc_now(),
        }
        save_state(state, cases)
        if any(process.poll() is not None for _, process, _ in running.values()):
            break
        time.sleep(10)
    if expected - started:
        state["sampling_start_confirmation"] = {
            "wave": wave, "confirmed_run_ids": sorted(started),
            "pending_run_ids": sorted(expected - started),
            "status": "PENDING_OR_EARLY_EXIT; monitor logs and return codes",
            "observed_utc": utc_now(),
        }
        save_state(state, cases)


def resource_sample(running: dict) -> dict:
    snapshot = resource_snapshot()
    sample = {"observed_utc": snapshot["observed_utc"],
              "logical_cpus": snapshot["logical_cpus"],
              "mem_available_kib": snapshot["mem_available_kib"],
              "swap_free_kib": snapshot["swap_free_kib"],
              "active_mpi_ranks": sum(item[0]["mpi_ranks"] for item in running.values()),
              "cases": {}}
    for run_id, (case, process, _) in running.items():
        pids = process_tree(process.pid)
        replacements, evaluations, rows = progress(case)
        sample["cases"][run_id] = {
            "pid": process.pid, "pid_tree_count": len(pids),
            "pss_kib": sum(pss_kib(pid) for pid in pids),
            "replacements": replacements, "evaluations": evaluations,
            "posterior_rows": rows,
        }
    return sample


def launch_case(case: dict, state: dict, cases: list[dict]) -> tuple[subprocess.Popen, float]:
    run_dir = Path(case["run_dir"])
    archive = ROOT / Path(case["archive_dir"])
    if run_dir.exists() or archive.exists():
        raise FileExistsError(f"Refusing to reuse run output: {run_dir} or {archive}")
    run_dir.mkdir(parents=True, exist_ok=False)
    log_path = ROOT / Path(case["launch_log"])
    if log_path.exists():
        raise FileExistsError(f"Refusing to overwrite launch log: {log_path}")
    command = make_command(case, setup_only=False)
    launch_record = {
        "run_id": case["run_id"], "scenario": "A3", "hours": case["hours"],
        "model": case["model"], "excluded_species": case["excluded_species"] or None,
        "mpi_ranks": RANKS_PER_RUN, "dataset_rel": case["dataset_rel"],
        "dataset_sha256": case["dataset_sha256_expected"], "n_live": 800,
        "evidence_tolerance": 0.5, "R": 10000, "wavelength_range_um": [3.0, 20.0],
        "x_profile": "isochem", "surface": "opaque black, fixed at 1 bar",
        "error_inflation": "none", "declared_parameters": case["declared_parameters"],
        "effective_free_parameters": case["effective_free_parameters"],
        "resume_checkpoint": False, "operator": OPERATOR_DESCRIPTION,
        "matched_full_run": case["matched_full_run"], "command": command,
        "created_utc": utc_now(),
    }
    launch_record_path = ROOT / Path(case["configuration_json"]).parent.parent / "launch_records" / f"{case['run_id']}.json"
    launch_record_path.parent.mkdir(parents=True, exist_ok=True)
    with launch_record_path.open("x", encoding="utf-8") as stream:
        json.dump(launch_record, stream, indent=2, sort_keys=True)
        stream.write("\n")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("x", encoding="utf-8") as log:
        log.write(f"[launch_utc] {utc_now()}\n[run_id] {case['run_id']}\n"
                  f"[MPI ranks] {RANKS_PER_RUN}\n[dataset SHA-256] {case['dataset_sha256_expected']}\n"
                  f"[command] {command}\n")
        log.flush()
        process = subprocess.Popen(
            ["/bin/bash", "-lc", command], cwd=str(ROOT), stdout=log,
            stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True,
        )
    case.update(status="sampling_pending", pid=str(process.pid), start_utc=utc_now())
    pid_path = ROOT / Path(case["pid_file"])
    pid_path.parent.mkdir(parents=True, exist_ok=True)
    with pid_path.open("x", encoding="ascii") as stream:
        stream.write(f"{process.pid}\n")
    state["active_run_ids"].append(case["run_id"])
    save_state(state, cases)
    print(f"[launched] {case['run_id']} MPI5 pid={process.pid}", flush=True)
    return process, time.monotonic()


def harvest(case: dict) -> None:
    source = Path(case["run_dir"])
    target = ROOT / Path(case["archive_dir"])
    if not source.is_dir() or not any(source.iterdir()):
        raise RuntimeError(f"Successful run has no scratch products: {source}")
    if target.exists():
        raise FileExistsError(f"Refusing to overwrite archived products: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, symlinks=True)


def monitor_wave(cases: list[dict], state: dict, wave: int,
                 running: dict) -> None:
    resources_path = CAMPAIGN / "resources.jsonl"
    last_sample = 0.0
    halt_reason = ""
    while running:
        now = time.monotonic()
        if now - last_sample >= 60:
            sample = resource_sample(running)
            with resources_path.open("a", encoding="utf-8") as stream:
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
                    harvest(case)
                    case["status"] = "complete_pending_validation"
                    print(f"[completed+archived] {run_id}", flush=True)
                except Exception as exc:
                    case["status"] = "harvest_failed"
                    case["error"] = f"{type(exc).__name__}: {exc}"
                    halt_reason = f"harvest failure {run_id}: {case['error']}"
            else:
                case["status"] = "failed"
                case["error"] = (
                    f"MPI5 retrieval exited {return_code}; scratch/logs preserved; no retry"
                )
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
    elif all(case["status"] == "complete_pending_validation"
             for case in group_cases(cases, (1, 10)[wave - 1])):
        state["waves_completed"].append(wave)
        state["campaign_status"] = f"WAVE_{wave}_COMPLETE_PENDING_VALIDATION"
    else:
        state["campaign_status"] = "INCOMPLETE"
    save_state(state, cases)


def run_wave(cases: list[dict], state: dict, wave: int) -> None:
    hours = (1, 10)[wave - 1]
    group = group_cases(cases, hours)
    foreign = foreign_sampler_processes()
    if foreign:
        raise RuntimeError("Unexpected active sampler before wave: " + " | ".join(foreign))
    run_preflights(cases, state, wave)
    state["baseline_by_hours"][str(hours)] = next(
        case["configuration_json"] for case in group if not case["excluded_species"]
    )
    wait_for_resource_gate(state, cases, wave)
    state["campaign_status"] = f"RUNNING_WAVE_{wave}"
    state["wave_started_utc"][str(wave)] = utc_now()
    save_state(state, cases)
    running: dict[str, tuple[dict, subprocess.Popen, float]] = {}
    started_by_run: dict[str, float] = {}
    for case in group:
        if len(running) >= MAX_PARALLEL or (len(running) + 1) * RANKS_PER_RUN > 15:
            raise RuntimeError("MPI resource ceiling would be exceeded")
        process, started = launch_case(case, state, cases)
        running[case["run_id"]] = (case, process, started)
        started_by_run[case["run_id"]] = started
    state["wave_active_runs"][str(wave)] = list(running)
    state["wave_mpi_ranks"][str(wave)] = sum(
        case["mpi_ranks"] for case, _, _ in running.values()
    )
    save_state(state, cases)
    print(f"[sampling] wave={wave} hours={hours}; 3 MPI5 samplers, 15 ranks total",
          flush=True)
    wait_for_wave_start(cases, wave, running, state)
    monitor_wave(cases, state, wave, running)
    if state["campaign_status"] == "HALTED_FAILURE":
        raise RuntimeError(state["halt_reason"])


def worker() -> int:
    state_path = CAMPAIGN / "campaign_state.json"
    if not state_path.is_file():
        raise FileNotFoundError(f"Campaign state missing: {state_path}")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    cases = build_cases()
    try:
        for wave in (1, 2):
            run_wave(cases, state, wave)
        state["campaign_status"] = "COMPLETE_PENDING_VALIDATION"
        state["sampling_completed_utc"] = utc_now()
        state["acceptance"] = "PENDING_INDEPENDENT_AUDIT"
        save_state(state, cases)
        print("[campaign complete] six fresh corrected-bin retrievals; audit pending",
              flush=True)
        return 0
    except Exception as exc:
        state["error"] = f"{type(exc).__name__}: {exc}"
        if state.get("campaign_status") not in {"HALTED_FAILURE", "HALTED_PREFLIGHT_FAILURE"}:
            state["campaign_status"] = "HALTED_FAILURE"
            state["halt_reason"] = state["error"]
        save_state(state, cases)
        print(f"[SUPERVISOR_ERROR] {state['error']}", file=sys.stderr, flush=True)
        return 2


def launch() -> None:
    if sys.platform != "linux":
        raise RuntimeError("Launch this campaign from Ubuntu/WSL")
    if CAMPAIGN.exists():
        raise RuntimeError(f"Refusing to overwrite existing campaign: {CAMPAIGN}")
    if SCRATCH.exists():
        raise RuntimeError("Existing scratch; refusing duplicate launch")
    foreign = foreign_sampler_processes()
    if foreign:
        raise RuntimeError("Unexpected active sampler; preserve it and do not launch: "
                           + " | ".join(foreign))
    baseline = verify_corrected_100h_reference()
    for hours, (name, expected_hash) in DATASETS.items():
        dataset = PROJECT / "life_data" / name
        if not dataset.is_file() or sha256(dataset) != expected_hash:
            raise ValueError(f"Frozen A3 {hours} h dataset is missing or changed")

    campaign_lock = CAMPAIGN / "launch.lock"
    CAMPAIGN.mkdir(parents=True, exist_ok=False)
    campaign_lock.mkdir()
    cases = build_cases()
    tracked_inputs = [
        RUNNER, SUPERVISOR, OPERATOR_SOURCE, LEGACY_RUNNER,
        NATIVE_EMISSION, LIFE_BINNED,
        BASELINE_100H / "resolved_configuration.json",
        BASELINE_100H / "campaign_state.json",
        BASELINE_100H / "products/results" / f"{BASELINE_STEM}_results.txt",
        BASELINE_100H / "products/MultiNest_raw" / f"{BASELINE_STEM}-stats.dat",
    ] + [PROJECT / "life_data" / name for name, _ in DATASETS.values()]
    preserved_inputs = {
        str(path.relative_to(ROOT)): sha256(path) for path in tracked_inputs
    }
    write_json(CAMPAIGN / "preserved_inputs.json", preserved_inputs)
    scope = {
        "campaign_id": "proxima_A3_1h_10h_corrected_bin_full_noNH3_noN2O_20261020_r03",
        "authorized_hours": [1, 10],
        "models_per_exposure": ["full", "no_NH3", "no_N2O"],
        "wave_plan": [
            {"wave": 1, "hours": 1, "runs": [case["run_id"] for case in cases if case["hours"] == 1],
             "parallel_runs": 3, "mpi_ranks_per_run": 5, "total_mpi_ranks": 15},
            {"wave": 2, "hours": 10, "runs": [case["run_id"] for case in cases if case["hours"] == 10],
             "parallel_runs": 3, "mpi_ranks_per_run": 5, "total_mpi_ranks": 15},
        ],
        "datasets": {
            str(hours): {"path": (PROJECT_REL / "life_data" / name).as_posix(),
                         "sha256": digest, "reuse_existing_noise_realization": True}
            for hours, (name, digest) in DATASETS.items()
        },
        "configuration": {
            "n_live": 800, "evidence_tolerance": 0.5, "R": 10000,
            "wavelength_range_um": [3.0, 20.0], "PT_profile": "Madhu",
            "abundance_profile": "isochem", "include_O2": True,
            "surface": "opaque black fixed at 1 bar", "error_inflation": "none",
            "declared_free_dimensions": {"full": "15/14", "ablations": "14/13"},
            "operator": OPERATOR_DESCRIPTION,
        },
        "matched_100h_corrected_reference": baseline,
        "checkpoint_reuse": False,
        "execution_order": "complete the full 1 h wave before preflighting/launching the 10 h wave",
        "previous_launch_attempts": [
            {
                "log": (PROJECT_REL / "retrievals/"
                        "a3_1_10h_binning_corrected_loo_20261020.supervisor.log").as_posix(),
                "outcome": "launcher self-check rejected its own log/PID before creating a campaign or starting MPI; evidence preserved",
            },
            {
                "campaign": (PROJECT_REL / "retrievals/"
                             "a3_1_10h_binning_corrected_loo_20261020_r02").as_posix(),
                "outcome": "MPI5 setup-only preflight exited 1 because the runner campaign path did not match the supervisor path; no sampler launched",
            },
        ],
    }
    write_json(CAMPAIGN / "selected_scope.json", scope)
    state = {
        "campaign_id": scope["campaign_id"],
        "campaign_status": "STARTING",
        "acceptance": "PENDING_INDEPENDENT_AUDIT",
        "created_utc": utc_now(), "supervisor_pid": os.getpid(),
        "campaign_rel": CAMPAIGN_REL.as_posix(), "scratch": str(SCRATCH),
        "dataset_sha256_by_hours": {str(k): v[1] for k, v in DATASETS.items()},
        "baseline_100h_corrected": baseline,
        "wave_plan": scope["wave_plan"], "active_run_ids": [], "runs": cases,
        "wave_started_utc": {}, "wave_active_runs": {}, "wave_mpi_ranks": {},
        "waves_completed": [], "baseline_by_hours": {}, "preflight_waves": {},
        "resource_gate": {}, "code_sha256": preserved_inputs,
        "max_parallel": MAX_PARALLEL, "mpi_ranks_per_run": RANKS_PER_RUN,
        "checkpoint_reuse": False,
    }
    write_json(CAMPAIGN / "campaign_state.json", state)
    save_state(state, cases)
    runtime_pid = CAMPAIGN / "supervisor.runtime.pid"
    with runtime_pid.open("x", encoding="ascii") as stream:
        stream.write(f"{os.getpid()}\n")
    readme = CAMPAIGN / "README.md"
    readme.write_text(
        "# A3 1 h y 10 h: retrievals con bineado corregido\n\n"
        "Campaña nueva y aislada para comparar, a cada exposición, el modelo completo "
        "con las ablaciones sin NH3 y sin N2O. El supervisor ejecuta tres MPI5 en paralelo "
        "(15 ranks totales), termina primero la tanda de 1 h y luego la de 10 h. No reutiliza "
        "checkpoints ni modifica datasets históricos.\n\n"
        "La realización LIFE existente de cada duración se mantiene congelada por SHA-256; "
        "el callback de likelihood se enlaza al operador corregido durante muestreo y "
        "postproceso. Cada ΔlnZ se calculará frente al modelo completo nuevo de la misma "
        "duración. Estado vivo: campaign_state.json y manifest.csv.\n\n"
        "Se preservaron dos intentos de arranque previos en el directorio retrievals: el "
        "primero fue rechazado por el guardado del supervisor antes de crear campaña; el "
        "segundo llegó al preflight MPI5 y detectó una ruta de campaña incoherente. Ambos "
        "terminaron antes de iniciar samplers y sus logs permanecen intactos.\n",
        encoding="utf-8",
    )
    print(f"[supervisor start] pid={os.getpid()} campaign={CAMPAIGN}", flush=True)
    raise SystemExit(worker())


def start_background() -> None:
    log_path = RETRIEVALS / "a3_1_10h_binning_corrected_loo_20261020_r03.supervisor.log"
    pid_path = RETRIEVALS / "a3_1_10h_binning_corrected_loo_20261020_r03.supervisor.pid"
    if log_path.exists() or pid_path.exists():
        raise SystemExit("Supervisor log/PID already exists; refusing duplicate")
    if CAMPAIGN.exists() or SCRATCH.exists():
        raise SystemExit("Campaign or scratch already exists; refusing duplicate")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("x", encoding="utf-8") as log:
        process = subprocess.Popen(
            [str(CONDA_PREFIX / "bin/python"), "-u", str(SUPERVISOR), "--worker-launch"],
            cwd=str(ROOT), stdout=log, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL, start_new_session=True,
        )
    with pid_path.open("x", encoding="ascii") as stream:
        stream.write(f"{process.pid}\n")
    time.sleep(3)
    if process.poll() is not None:
        raise RuntimeError(f"Supervisor exited early ({process.returncode}); inspect {log_path}")
    print(json.dumps({"supervisor_pid": process.pid, "campaign": str(CAMPAIGN),
                      "log": str(log_path), "pid_file": str(pid_path)}))


if __name__ == "__main__":
    if "--worker-launch" in sys.argv:
        launch()
    elif "--launch" in sys.argv:
        start_background()
    else:
        raise SystemExit("Use --launch from Ubuntu/WSL; worker launch is supervisor-owned")
