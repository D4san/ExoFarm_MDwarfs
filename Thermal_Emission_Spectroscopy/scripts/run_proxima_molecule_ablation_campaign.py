"""Run the 36 official Proxima LIFE leave-one-molecule-out retrievals.

The campaign reuses the six frozen A1/A3 1/10/100 h datasets.  It changes only
the requested molecular species per retrieval, keeps each MultiNest run in an
isolated Linux-filesystem directory, and archives complete outputs only after
exit code zero. The supervisor refuses to relaunch an existing campaign by
default. An explicit resume mode reloads durable state, verifies frozen inputs,
preserves failed attempts, resumes stale interrupted cells from their saved
MultiNest checkpoints, and schedules only interrupted/failed/pending cells.
"""

import argparse
import csv
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


SPECIES_ORDER = ("N2O", "NH3", "CH4", "O3", "CO2", "H2O")
HOURS_ORDER = (100, 10, 1)
SCENARIOS = ("A1", "A3")
MPI_RANKS = 6
N_LIVE = 800
EXPECTED_ABLATED_DIMENSION = 14
CONDA_PREFIX = Path("/home/dasan/anaconda3/envs/POSEIDON")
CONDA_INIT = "/home/dasan/anaconda3/etc/profile.d/conda.sh"
POSEIDON_INPUT_DATA = "/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs"
PYSYN_CDBS = (
    "/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids"
)

# Hashes freeze the exact six official observations selected for this analysis.
# In particular, A1-1 h uses the promoted independent realization (seed
# 2125532119), not the superseded seed 368516754 sensitivity dataset.
DATASETS = {
    ("A1", 1): {
        "file": "LIFE_proxima_A1_1h_O2_fixedBlack1bar_noiseRepeat2.dat",
        "seed": 2125532119,
        "sha256": "93fb65765101950063d5aa9a3dafae4df38273292cb0e3349e94b8a34516cfcc",
        "full_results": (
            "proxima_A1_1h_O2_fixedBlack1bar_noxtol_MPI6_NOISE2_results.txt"
        ),
    },
    ("A3", 1): {
        "file": "LIFE_proxima_A3_1h_O2_fixedBlack1bar_official.dat",
        "seed": 1376328125,
        "sha256": "a3043e5de76a834983949e6eca12636ea4de174ebdb2db0853155282c100dee2",
        "full_results": (
            "proxima_A3_1h_O2_fixedBlack1bar_noxtol_MPI6_OFFICIAL1h_results.txt"
        ),
    },
    ("A1", 10): {
        "file": "LIFE_proxima_A1_10h.dat",
        "seed": 1099171982,
        "sha256": "ed39ae6dc5b8ff0d5c8aca3d126a2945343a289be30f3b8d9e8e72c434ee9b8f",
        "full_results": (
            "proxima_A1_10h_O2_fixedBlack1bar_noxtol_MPI6R1_results.txt"
        ),
    },
    ("A3", 10): {
        "file": "LIFE_proxima_A3_10h.dat",
        "seed": 1469409748,
        "sha256": "46a026504b9b9521fa29407a501169b9d3cfc433de40a91b8ade86d7767abb5b",
        "full_results": (
            "proxima_A3_10h_O2_fixedBlack1bar_noxtol_"
            "proxima_A3_10h_O2_fixedBlack1bar_noxtol_results.txt"
        ),
    },
    ("A1", 100): {
        "file": "LIFE_proxima_A1_100h_O2_fixedBlack1bar_noxtol_audit.dat",
        "seed": 460512527,
        "sha256": "d66c886238a2916312c645589be8601828fbf0a7cd2f02a383ef1d6a3454b5e3",
        "full_results": (
            "proxima_A1_100h_O2_fixedBlack1bar_noxtol_MPI6R1_results.txt"
        ),
    },
    ("A3", 100): {
        "file": "LIFE_proxima_A3_100h.dat",
        "seed": 129315834,
        "sha256": "78662546181a5b74391a14b7b73ae80d879200a74db6a4bc5338e3ce7eee4705",
        "full_results": (
            "proxima_A3_100h_O2_fixedBlack1bar_noxtol_"
            "proxima_A3_100h_O2_fixedBlack1bar_noxtol_results.txt"
        ),
    },
}

PROJECT_REL = Path("Thermal_Emission_Spectroscopy") / "outputs" / (
    "life_proxima_b_earthlike_v1"
)
RESULTS_REL = PROJECT_REL / "retrievals" / "POSEIDON_output" / (
    "proxima_b_earthlike/retrievals/results"
)


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_cases(repo_root, campaign_root, scratch_root):
    data_root = repo_root / PROJECT_REL / "life_data"
    full_results_root = repo_root / RESULTS_REL
    cases = []

    # Prioritize the central N2O/NH3 hypotheses at 100 h, then 10 h and 1 h;
    # continue with contextual species at all three exposures.
    priority = [("N2O", 100), ("NH3", 100)]
    priority += [("N2O", 10), ("NH3", 10), ("N2O", 1), ("NH3", 1)]
    for species in ("CH4", "O3", "CO2", "H2O"):
        priority.extend((species, hours) for hours in HOURS_ORDER)

    for species, hours in priority:
        for scenario in SCENARIOS:
            source = DATASETS[(scenario, hours)]
            run_id = f"{scenario}_{hours}h_no_{species}"
            dataset_path = data_root / source["file"]
            full_results = full_results_root / source["full_results"]
            output_tag = f"_LOO_no{species}_MPI6_v1"
            run_dir = scratch_root / "runs" / run_id
            log_path = campaign_root / "logs" / f"{run_id}.launch.log"
            cases.append({
                "run_id": run_id,
                "scenario": scenario,
                "hours": hours,
                "excluded_species": species,
                "dataset": str(dataset_path),
                "dataset_rel": str(dataset_path.relative_to(repo_root)),
                "dataset_sha256_expected": source["sha256"],
                "dataset_seed": source["seed"],
                "full_results": str(full_results),
                "comparison_contract": (
                    "same dataset and noise realization; compare the matched "
                    "full-model lnZ with this one-species-absent model only"
                ),
                "output_tag": output_tag,
                "run_dir": str(run_dir),
                "launch_log": str(log_path),
                "pid_file": str(campaign_root / "pids" / f"{run_id}.pid"),
                "archive_dir": str(campaign_root / "runs" / run_id),
                "preflight_status": "not_run",
                "status": "pending",
                "pid": "",
                "start_utc": "",
                "end_utc": "",
                "return_code": "",
                "elapsed_seconds": "",
                "preflight_log": str(
                    campaign_root / "preflight" / f"{run_id}.log"
                ),
                "resume_checkpoint": False,
                "continuation_number": 0,
            })
    return cases


def write_manifest(path, cases):
    fields = [
        "run_id", "scenario", "hours", "excluded_species", "dataset_rel",
        "dataset_seed", "dataset_sha256_expected", "full_results",
        "output_tag", "run_dir", "archive_dir", "preflight_status",
        "preflight_log", "status", "pid", "pid_file", "launch_log",
        "start_utc", "end_utc", "return_code", "elapsed_seconds",
        "attempt_number", "config_path", "resume_checkpoint",
        "continuation_number", "interruption_reason", "interrupted_utc",
    ]
    temporary = path.with_suffix(".csv.tmp")
    with temporary.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(cases)
    os.replace(temporary, path)


def save_state(path, state, cases):
    state["updated_utc"] = utc_now()
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)
    write_manifest(path.with_name("manifest.csv"), cases)


def base_command(repo_root, case, python, setup_only=False):
    script = repo_root / "Thermal_Emission_Spectroscopy" / "scripts" / (
        "run_life_retrieval.py"
    )
    args = [
        str(python), "-u", str(script),
        "--campaign", "proxima",
        "--scenario", case["scenario"],
        "--hours", str(case["hours"]),
        "--n-live", str(N_LIVE),
        "--error-inflation", "none",
        "--surface-pressure-mode", "fixed-black",
        "--include-o2",
        "--exclude-species", case["excluded_species"],
        "--x-profile", "isochem",
        "--output-tag", case["output_tag"],
        "--R", "10000",
        "--dataset-file", case["dataset"],
        "--run-dir", case["run_dir"] if not setup_only else str(
            Path(case["run_dir"]).parent / "preflight" / case["run_id"]
        ),
    ]
    if setup_only:
        args.append("--setup-only")
    if not setup_only and case.get("resume_checkpoint"):
        args.append("--resume")
    return args


def shell_command(repo_root, case, setup_only=False, use_mpi=True):
    python = CONDA_PREFIX / "bin" / "python"
    args = base_command(repo_root, case, python, setup_only=setup_only)
    if use_mpi:
        mpiexec = CONDA_PREFIX / "bin" / "mpiexec"
        args = [str(mpiexec), "-n", str(MPI_RANKS)] + args
    env_exports = [
        "export POSEIDON_input_data=" + shlex.quote(POSEIDON_INPUT_DATA),
        "export PYSYN_CDBS=" + shlex.quote(PYSYN_CDBS),
        "export OMP_NUM_THREADS=1",
        "export OPENBLAS_NUM_THREADS=1",
        "export MKL_NUM_THREADS=1",
        "export NUMEXPR_NUM_THREADS=1",
    ]
    pieces = [
        "set -euo pipefail",
        "source " + shlex.quote(CONDA_INIT),
        "conda activate POSEIDON",
        *env_exports,
        "cd " + shlex.quote(str(repo_root)),
        "exec " + shlex.join(args),
    ]
    return "; ".join(pieces)


def verify_inputs(repo_root, cases):
    problems = []
    seen = set()
    for case in cases:
        dataset = Path(case["dataset"])
        reference = Path(case["full_results"])
        if not dataset.is_file():
            problems.append(f"missing dataset: {dataset}")
            continue
        actual = sha256_file(dataset)
        if actual != case["dataset_sha256_expected"]:
            problems.append(
                f"dataset hash mismatch for {case['run_id']}: "
                f"expected {case['dataset_sha256_expected']}, got {actual}"
            )
        if not reference.is_file():
            problems.append(f"missing full-model baseline results: {reference}")
        key = (case["scenario"], case["hours"], case["excluded_species"])
        if key in seen:
            problems.append(f"duplicate campaign cell: {key}")
        seen.add(key)
    if len(cases) != 36 or len(seen) != 36:
        problems.append(f"campaign grid has {len(seen)} unique cells, expected 36")
    return problems


def run_preflight(repo_root, cases, campaign_root, scratch_root, state):
    python = CONDA_PREFIX / "bin" / "python"
    failed = []
    for case in cases:
        log_path = Path(case["preflight_log"])
        log_path.parent.mkdir(parents=True, exist_ok=True)
        command = shell_command(repo_root, case, setup_only=True, use_mpi=False)
        result = subprocess.run(
            ["/bin/bash", "-lc", command],
            cwd=str(repo_root), capture_output=True, text=True,
        )
        output = result.stdout + result.stderr
        log_path.write_text(output, encoding="utf-8", errors="replace")
        match = re.search(r"\[parameters\]\s+(\d+):\s*(.*)", output)
        parameter_count = int(match.group(1)) if match else None
        parameter_names = match.group(2) if match else ""
        removed_parameter = f"log_{case['excluded_species']}"
        if result.returncode == 0 and "[setup-only]" in output:
            if parameter_count != EXPECTED_ABLATED_DIMENSION:
                result_status = "failed_wrong_dimension"
            elif re.search(r"\b" + re.escape(removed_parameter) + r"\b", parameter_names):
                result_status = "failed_species_still_active"
            elif (
                f"excluded_species={case['excluded_species']}" not in output
                or "surface_pressure_mode=fixed-black" not in output
                or "error_inflation=none" not in output
                or "X_profile=isochem" not in output
            ):
                result_status = "failed_configuration_mismatch"
            else:
                result_status = "pass"
        else:
            result_status = "failed_setup"
        case["preflight_status"] = result_status
        case["preflight_parameters"] = parameter_count
        case["preflight_parameter_names"] = parameter_names
        case["preflight_return_code"] = result.returncode
        save_state(campaign_root / "campaign_state.json", state, cases)
        print(
            f"[preflight {len([c for c in cases if c['preflight_status'] != 'not_run'])}/36] "
            f"{case['run_id']}: {result_status}"
        )
        if result_status != "pass":
            failed.append(case["run_id"])
    return failed


def launch_case(repo_root, case, campaign_root, state, cases):
    run_dir = Path(case["run_dir"])
    resume_checkpoint = bool(case.get("resume_checkpoint"))
    if resume_checkpoint:
        if not multinest_checkpoint_files(case):
            raise RuntimeError(
                f"checkpoint files are missing or empty for {case['run_id']}"
            )
    elif run_dir.exists() and any(run_dir.iterdir()):
        raise RuntimeError(
            f"refusing to overwrite non-empty scratch directory: {run_dir}"
        )
    if Path(case["archive_dir"]).exists():
        raise RuntimeError(
            f"refusing to overwrite archived output: {case['archive_dir']}"
        )

    config_path = Path(case.get(
        "config_path",
        campaign_root / "configs" / f"{case['run_id']}.json",
    ))
    if config_path.exists():
        raise RuntimeError(
            f"refusing to overwrite run configuration: {config_path}"
        )
    config_path.parent.mkdir(parents=True, exist_ok=True)
    command = shell_command(repo_root, case, setup_only=False, use_mpi=True)
    config = {
        "run_id": case["run_id"],
        "scenario": case["scenario"],
        "hours": case["hours"],
        "excluded_species": case["excluded_species"],
        "dataset": case["dataset"],
        "dataset_sha256": case["dataset_sha256_expected"],
        "dataset_seed": case["dataset_seed"],
        "full_model_results": case["full_results"],
        "command": command,
        "mpi_ranks": MPI_RANKS,
        "n_live": N_LIVE,
        "X_profile": "isochem",
        "error_inflation": "none",
        "x_tol": "disabled",
        "surface": "explicit opaque black surface at 1 bar",
        "R": 10000,
        "n_bins": 31,
        "resume_checkpoint": resume_checkpoint,
        "created_utc": utc_now(),
    }
    config_path.write_text(
        json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    log_path = Path(case["launch_log"])
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("x", encoding="utf-8") as log:
        log.write(f"[launch_utc] {utc_now()}\n")
        log.write(f"[run_id] {case['run_id']}\n")
        log.write(f"[dataset_sha256] {case['dataset_sha256_expected']}\n")
        log.write(f"[config] {config_path}\n")
        log.write(f"[command] {command}\n")
        log.flush()
        process = subprocess.Popen(
            ["/bin/bash", "-lc", command],
            cwd=str(repo_root), stdout=log, stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    case["status"] = "running"
    case["pid"] = str(process.pid)
    case["start_utc"] = utc_now()
    Path(case["pid_file"]).parent.mkdir(parents=True, exist_ok=True)
    Path(case["pid_file"]).write_text(f"{process.pid}\n", encoding="ascii")
    state["active_run_ids"].append(case["run_id"])
    save_state(campaign_root / "campaign_state.json", state, cases)
    print(f"[launched] {case['run_id']} pid={process.pid}", flush=True)
    return process


def harvest_case(case):
    source = Path(case["run_dir"])
    target = Path(case["archive_dir"])
    if not source.is_dir() or not any(source.iterdir()):
        raise RuntimeError(f"successful run has no output directory: {source}")
    if target.exists():
        raise RuntimeError(f"refusing to overwrite archive: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, symlinks=True)


def run_queue(repo_root, cases, campaign_root, state, max_parallel):
    pending = [case for case in cases if case["status"] == "pending"]
    pending.sort(key=lambda case: (
        not bool(case.get("resume_checkpoint")),
        -int(case.get("attempt_number", 1)),
    ))
    running = {}
    halted = False
    while pending or running:
        # Do not leave an idle supervisor sleeping forever after a failed run.
        if halted and not running:
            break
        while pending and len(running) < max_parallel and not halted:
            case = pending.pop(0)
            process = launch_case(repo_root, case, campaign_root, state, cases)
            running[case["run_id"]] = (case, process, time.monotonic())

        finished_ids = []
        for run_id, (case, process, started) in list(running.items()):
            return_code = process.poll()
            if return_code is None:
                continue
            finished_ids.append(run_id)
            case["end_utc"] = utc_now()
            case["return_code"] = str(return_code)
            case["elapsed_seconds"] = f"{time.monotonic() - started:.1f}"
            state["active_run_ids"].remove(run_id)
            if return_code == 0:
                case["status"] = "harvesting"
                save_state(campaign_root / "campaign_state.json", state, cases)
                try:
                    harvest_case(case)
                    case["status"] = "completed"
                    print(f"[completed+archived] {run_id}", flush=True)
                except Exception as exc:  # Preserve the scratch and stop queue.
                    case["status"] = "harvest_failed"
                    case["error"] = str(exc)
                    state["halt_reason"] = f"harvest failure: {run_id}: {exc}"
                    halted = True
                    print(f"[HALT] {state['halt_reason']}", flush=True)
            else:
                case["status"] = "failed"
                state["halt_reason"] = (
                    f"nonzero exit {return_code} for {run_id}; "
                    "scratch/logs preserved; no automatic retry"
                )
                halted = True
                print(f"[HALT] {state['halt_reason']}", flush=True)
            save_state(campaign_root / "campaign_state.json", state, cases)

        for run_id in finished_ids:
            running.pop(run_id, None)

        if not finished_ids:
            time.sleep(10)

    if halted:
        state["campaign_status"] = "halted_failure"
    elif all(case["status"] == "completed" for case in cases):
        state["campaign_status"] = "completed"
        state["completed_utc"] = utc_now()
    else:
        state["campaign_status"] = "incomplete"
    save_state(campaign_root / "campaign_state.json", state, cases)


def print_status(state_path):
    if not state_path.is_file():
        raise SystemExit(f"campaign state not found: {state_path}")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    cases = state.get("runs", [])
    counts = {}
    for case in cases:
        counts[case["status"]] = counts.get(case["status"], 0) + 1
    print(json.dumps({
        "campaign_status": state.get("campaign_status"),
        "updated_utc": state.get("updated_utc"),
        "halt_reason": state.get("halt_reason"),
        "active_run_ids": state.get("active_run_ids", []),
        "counts": counts,
        "n_runs": len(cases),
    }, indent=2))


def multinest_checkpoint_files(case):
    run_dir = Path(case["run_dir"])
    basename = (
        f"proxima_{case['scenario']}_{int(case['hours'])}h"
        f"{case['output_tag']}"
    )
    raw_dir = (
        run_dir / "POSEIDON_output" / "proxima_b_earthlike" / "retrievals"
        / "MultiNest_raw"
    )
    required = [
        raw_dir / f"{basename}-resume.dat",
        raw_dir / f"{basename}-live.points",
        raw_dir / f"{basename}-phys_live.points",
    ]
    if any(not path.is_file() or path.stat().st_size == 0 for path in required):
        return []
    return required


def pid_is_alive(pid):
    try:
        os.kill(int(pid), 0)
    except (ProcessLookupError, ValueError):
        return False
    except PermissionError:
        return True
    return True


def validate_resume_state(repo_root, campaign_root):
    state_path = campaign_root / "campaign_state.json"
    manifest_path = campaign_root / "manifest.csv"
    if not state_path.is_file() or not manifest_path.is_file():
        raise SystemExit("resume requires the existing campaign state and manifest")

    state = json.loads(state_path.read_text(encoding="utf-8"))
    cases = state.get("runs", [])
    expected_id = "proxima_a1_a3_molecule_ablation_loo_20261004"
    if state.get("campaign_id") != expected_id:
        raise SystemExit("campaign_id does not match the approved Proxima LOO campaign")
    if len(cases) != 36 or len({case.get("run_id") for case in cases}) != 36:
        raise SystemExit("resume requires the unchanged 36-cell campaign grid")
    if state.get("max_parallel") != 2 or state.get("mpi_ranks_per_run") != MPI_RANKS:
        raise SystemExit("resume refuses changed parallelism or MPI rank count")
    if state.get("canonical_8of8_modified") is not False:
        raise SystemExit("resume refuses a campaign that modified the canonical 8/8")
    with manifest_path.open(newline="", encoding="utf-8") as stream:
        manifest_rows = list(csv.DictReader(stream))
    if len(manifest_rows) != 36:
        raise SystemExit("saved manifest does not contain exactly 36 rows")
    manifest_by_id = {row.get("run_id"): row for row in manifest_rows}
    if len(manifest_by_id) != 36:
        raise SystemExit("saved manifest contains duplicate or missing run IDs")
    for case in cases:
        row = manifest_by_id.get(case["run_id"])
        if row is None or row.get("status") != case.get("status"):
            raise SystemExit(
                f"state/manifest mismatch for {case['run_id']}; refusing resume"
            )

    running_cases = [case for case in cases if case.get("status") == "running"]
    running_ids = {case["run_id"] for case in running_cases}
    active_ids = set(state.get("active_run_ids", []))
    if active_ids != running_ids:
        raise SystemExit(
            "resume found inconsistent active_run_ids and running records; "
            "inspect state and manifest before recovery"
        )
    for case in running_cases:
        pid = case.get("pid", "")
        if not pid or pid_is_alive(pid):
            raise SystemExit(
                f"resume refuses live or unverifiable PID for "
                f"{case['run_id']}: {pid or '<missing>'}"
            )
        if not Path(case["launch_log"]).is_file():
            raise SystemExit(
                f"interrupted run log is missing for {case['run_id']}"
            )
        if not multinest_checkpoint_files(case):
            raise SystemExit(
                f"complete MultiNest checkpoint set is missing for "
                f"{case['run_id']}; scratch preserved"
            )
        case["status"] = "interrupted"
        case["interruption_reason"] = (
            "recorded run PID absent during explicit checkpoint recovery"
        )
        case["interrupted_utc"] = utc_now()
    if running_cases:
        state["active_run_ids"] = []

    allowed_statuses = {"completed", "failed", "pending", "interrupted"}
    unexpected = [
        f"{case.get('run_id')}={case.get('status')}"
        for case in cases if case.get("status") not in allowed_statuses
    ]
    if unexpected:
        raise SystemExit("resume found non-terminal run states: " + ", ".join(unexpected))
    if any(
        case.get("preflight_status") != "pass"
        or case.get("preflight_parameters") != EXPECTED_ABLATED_DIMENSION
        or case.get("preflight_return_code") != 0
        for case in cases
    ):
        raise SystemExit("resume requires all 36 saved 14-parameter preflights to pass")

    problems = verify_inputs(repo_root, cases)
    if problems:
        raise SystemExit("resume input audit failed:\n- " + "\n- ".join(problems))

    for case in cases:
        archive_dir = Path(case["archive_dir"])
        run_dir = Path(case["run_dir"])
        if case["status"] == "completed":
            if not archive_dir.is_dir() or not any(archive_dir.iterdir()):
                raise SystemExit(f"completed archive is missing or empty: {archive_dir}")
        elif case["status"] == "pending":
            if archive_dir.exists():
                raise SystemExit(
                    f"pending run already has an archive; inspect before resume: {archive_dir}"
                )
            if (
                run_dir.exists() and any(run_dir.iterdir())
                and not case.get("resume_checkpoint")
            ):
                raise SystemExit(
                    f"pending run has non-empty scratch; preserving and refusing: {run_dir}"
                )
            if case.get("resume_checkpoint"):
                if not multinest_checkpoint_files(case):
                    raise SystemExit(
                        f"pending checkpoint continuation lacks MultiNest files: {run_dir}"
                    )
            elif Path(case["launch_log"]).exists():
                raise SystemExit(
                    "pending run already has a launch log; inspect before resume: "
                    + case["launch_log"]
                )
        elif case["status"] == "interrupted":
            if archive_dir.exists():
                raise SystemExit(
                    f"interrupted run unexpectedly has an archive: {archive_dir}"
                )
            if not run_dir.is_dir() or not any(run_dir.iterdir()):
                raise SystemExit(
                    f"interrupted scratch is missing or empty: {run_dir}"
                )
            if not multinest_checkpoint_files(case):
                raise SystemExit(
                    f"interrupted run lacks a complete MultiNest checkpoint: {run_dir}"
                )
            if not Path(case["launch_log"]).is_file():
                raise SystemExit(
                    f"interrupted run log is missing: {case['launch_log']}"
                )
        else:
            if archive_dir.exists():
                raise SystemExit(f"failed run unexpectedly has an archive: {archive_dir}")
            if case.get("attempt_history"):
                raise SystemExit(
                    f"{case['run_id']} already has a retry; refusing automatic repeat"
                )
            failed_log = Path(case["launch_log"])
            if not failed_log.is_file():
                raise SystemExit(f"failed run log is missing: {failed_log}")
            log_text = failed_log.read_text(encoding="utf-8", errors="replace")
            if (
                case["run_id"] != "A1_100h_no_CO2"
                or "[Errno 19] No such device" not in log_text
                or "/stellar_grids/grid/phoenix/catalog.fits" not in log_text
            ):
                raise SystemExit(
                    f"failed run is not the diagnosed transient D: mount failure: "
                    f"{case['run_id']}"
                )
            if not run_dir.exists():
                raise SystemExit(f"failed scratch is missing; preserving and refusing: {run_dir}")

    failed = [case for case in cases if case["status"] == "failed"]
    interrupted = [case for case in cases if case["status"] == "interrupted"]
    pending = [case for case in cases if case["status"] == "pending"]
    if not failed and not interrupted and not pending:
        raise SystemExit("campaign has no failed or pending cells to resume")
    return state, cases, failed, interrupted, pending


def resume_existing_campaign(repo_root, campaign_root, max_parallel, dry_run=False):
    if max_parallel != 2:
        raise SystemExit("the approved LOO plan is fixed at two concurrent MPI6 jobs")
    state, cases, failed, interrupted, pending = validate_resume_state(
        repo_root, campaign_root
    )
    scheduled = interrupted + failed + pending
    print(
        f"[resume-plan] completed={sum(c['status'] == 'completed' for c in cases)}; "
        f"checkpoint_continuations={len(interrupted)}; retry={len(failed)}; "
        f"pending={len(pending)}; parallel=2; ranks={MPI_RANKS}"
    )
    for case in scheduled:
        action = (
            "continue checkpoint" if case["status"] == "interrupted"
            else "schedule"
        )
        print(f"[resume-plan] {case['status']} -> {action}: {case['run_id']}")
    if dry_run:
        return

    for case in interrupted:
        continuation_number = int(case.get("continuation_number", 0)) + 1
        while True:
            suffix = f"_continuation{continuation_number:02d}"
            next_log = campaign_root / "logs" / (
                case["run_id"] + suffix + ".launch.log"
            )
            next_pid = campaign_root / "pids" / (
                case["run_id"] + suffix + ".pid"
            )
            next_config = campaign_root / "configs" / (
                case["run_id"] + suffix + ".json"
            )
            if not any(path.exists() for path in (next_log, next_pid, next_config)):
                break
            continuation_number += 1
        checkpoint_manifest = {
            path.name: {
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in multinest_checkpoint_files(case)
        }
        case.setdefault("continuation_history", []).append({
            "continuation_number": continuation_number,
            "previous_pid": case.get("pid", ""),
            "previous_start_utc": case.get("start_utc", ""),
            "interrupted_utc": case.get("interrupted_utc", ""),
            "interruption_reason": case.get("interruption_reason", ""),
            "run_dir": case["run_dir"],
            "previous_launch_log": case["launch_log"],
            "checkpoint_files": checkpoint_manifest,
        })
        case.update({
            "status": "pending",
            "resume_checkpoint": True,
            "continuation_number": continuation_number,
            "launch_log": str(next_log),
            "pid_file": str(next_pid),
            "config_path": str(next_config),
            "pid": "",
            "start_utc": "",
            "end_utc": "",
            "return_code": "",
            "elapsed_seconds": "",
        })

    for case in failed:
        history = case.setdefault("attempt_history", [])
        previous_attempt = int(case.get("attempt_number", 1))
        previous_config = case.get(
            "config_path",
            str(campaign_root / "configs" / f"{case['run_id']}.json"),
        )
        history.append({
            "attempt_number": previous_attempt,
            "status": case["status"],
            "pid": case.get("pid", ""),
            "start_utc": case.get("start_utc", ""),
            "end_utc": case.get("end_utc", ""),
            "return_code": case.get("return_code", ""),
            "elapsed_seconds": case.get("elapsed_seconds", ""),
            "run_dir": case["run_dir"],
            "launch_log": case["launch_log"],
            "pid_file": case["pid_file"],
            "config_path": previous_config,
        })
        attempt = previous_attempt + 1
        while True:
            suffix = f"_attempt{attempt:02d}"
            next_run_dir = Path(case["run_dir"]).parent / (case["run_id"] + suffix)
            next_log = campaign_root / "logs" / (case["run_id"] + suffix + ".launch.log")
            next_pid = campaign_root / "pids" / (case["run_id"] + suffix + ".pid")
            next_config = campaign_root / "configs" / (case["run_id"] + suffix + ".json")
            if not any(path.exists() for path in (next_run_dir, next_log, next_pid, next_config)):
                break
            attempt += 1
        case.update({
            "status": "pending",
            "attempt_number": attempt,
            "run_dir": str(next_run_dir),
            "launch_log": str(next_log),
            "pid_file": str(next_pid),
            "config_path": str(next_config),
            "pid": "",
            "start_utc": "",
            "end_utc": "",
            "return_code": "",
            "elapsed_seconds": "",
        })

    original_halt = state.get("halt_reason", "")
    state.setdefault("resume_history", []).append({
        "resume_utc": utc_now(),
        "previous_status": state.get("campaign_status"),
        "previous_halt_reason": original_halt,
        "scheduled_run_ids": [case["run_id"] for case in scheduled],
        "checkpoint_continuation_run_ids": [
            case["run_id"] for case in interrupted
        ],
        "max_parallel": max_parallel,
        "mpi_ranks_per_run": MPI_RANKS,
        "resume_code_sha256": sha256_file(Path(__file__).resolve()),
    })
    state["campaign_status"] = "resuming"
    state["halt_reason"] = ""
    state["active_run_ids"] = []
    save_state(campaign_root / "campaign_state.json", state, cases)
    state["campaign_status"] = "running"
    save_state(campaign_root / "campaign_state.json", state, cases)
    print(
        "[resume] continuing interrupted checkpoints and starting only "
        "failed/pending runs; completed archives untouched",
        flush=True,
    )
    run_queue(repo_root, cases, campaign_root, state, max_parallel)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-parallel", type=int, choices=(1, 2), default=2)
    parser.add_argument(
        "--scratch-root", type=Path,
        default=Path("/home/dasan/exofarm_proxima_molecule_loo_20261004"),
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--status-only", action="store_true")
    parser.add_argument(
        "--resume-existing", action="store_true",
        help=(
            "resume validated interrupted checkpoints and failed/pending cells "
            "from the existing campaign"
        ),
    )
    parser.add_argument(
        "--resume-dry-run", action="store_true",
        help="validate and print the resume plan without changing campaign files",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    campaign_root = repo_root / PROJECT_REL / "retrievals" / (
        "molecule_ablation_loo_20261004"
    )
    state_path = campaign_root / "campaign_state.json"
    if args.status_only:
        print_status(state_path)
        return

    if args.resume_existing and args.resume_dry_run:
        raise SystemExit("choose either --resume-existing or --resume-dry-run")
    if args.resume_existing or args.resume_dry_run:
        if args.dry_run:
            raise SystemExit("--dry-run cannot be combined with campaign resume options")
        resume_existing_campaign(
            repo_root, campaign_root, args.max_parallel,
            dry_run=args.resume_dry_run,
        )
        return

    cases = build_cases(repo_root, campaign_root, args.scratch_root)
    if args.dry_run:
        for case in cases:
            print(
                f"{case['run_id']}: data={case['dataset_rel']} "
                f"sha256={case['dataset_sha256_expected']} "
                f"tag={case['output_tag']}"
            )
        return

    if state_path.exists():
        raise SystemExit(
            f"campaign already initialized at {state_path}; refusing to "
            "relaunch or duplicate it. Inspect the manifest/status first."
        )
    problems = verify_inputs(repo_root, cases)
    if problems:
        raise SystemExit("preflight input audit failed:\n- " + "\n- ".join(problems))

    if args.max_parallel != 2:
        raise SystemExit("this approved run plan is fixed at two concurrent MPI6 jobs")
    if MPI_RANKS != 6:
        raise SystemExit("MPI rank count is frozen at six per retrieval for comparability")

    campaign_root.mkdir(parents=True, exist_ok=False)
    method_report = repo_root / "docs" / (
        "life_proxima_molecular_ablation_loo_2026-10-04.md"
    )
    if method_report.is_file():
        shutil.copy2(method_report, campaign_root / "README.md")
    state = {
        "campaign_id": "proxima_a1_a3_molecule_ablation_loo_20261004",
        "objective": (
            "For each of the six official A1/A3 1/10/100 h LIFE datasets, "
            "compare the full retrieval to a retrieval omitting exactly one "
            "of H2O, CO2, CH4, O3, N2O, or NH3, to assess conditional "
            "molecular evidence on the same noisy spectrum."
        ),
        "created_utc": utc_now(),
        "code_sha256": {
            "supervisor": sha256_file(Path(__file__).resolve()),
            "retrieval_runner": sha256_file(
                repo_root / "Thermal_Emission_Spectroscopy" / "scripts"
                / "run_life_retrieval.py"
            ),
        },
        "campaign_status": "preflight_running",
        "official_full_model_runs_reused": True,
        "canonical_8of8_modified": False,
        "max_parallel": args.max_parallel,
        "mpi_ranks_per_run": MPI_RANKS,
        "n_live": N_LIVE,
        "active_run_ids": [],
        "runs": cases,
    }
    save_state(state_path, state, cases)
    print(
        f"[campaign] {state['campaign_id']} 36 cells; "
        f"queue limit={args.max_parallel}"
    )
    print("[preflight] checking all data hashes, baselines, priors and 14-D variants")
    failures = run_preflight(
        repo_root, cases, campaign_root, args.scratch_root, state
    )
    if failures:
        state["campaign_status"] = "preflight_failed"
        state["halt_reason"] = "setup-only failed for: " + ", ".join(failures)
        save_state(state_path, state, cases)
        raise SystemExit(state["halt_reason"])
    state["preflight_status"] = "passed_36_of_36"
    state["campaign_status"] = "queued"
    save_state(state_path, state, cases)
    state["campaign_status"] = "running"
    state["launch_utc"] = utc_now()
    save_state(state_path, state, cases)
    run_queue(repo_root, cases, campaign_root, state, args.max_parallel)


if __name__ == "__main__":
    main()
