"""Queue the 33 corrected-bin LIFE Proxima A1/A3 homologous retrievals."""

from __future__ import annotations

import argparse
import csv
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

import numpy as np

from run_life_retrieval_a1_a3_corrected_matrix import (
    CAMPAIGN as RUNNER_CAMPAIGN,
    DATASETS,
    MPI_RANKS,
    OPERATOR_DESCRIPTION,
    PROJECT,
    ROOT,
    SCRATCH,
    case_identity,
    output_tag,
    sha256,
    validate_resolved_config,
)


PROJECT_REL = Path("Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1")
CAMPAIGN = RUNNER_CAMPAIGN
CAMPAIGN_REL = CAMPAIGN.relative_to(ROOT)
RETRIEVALS = PROJECT / "retrievals"
RUNNER = ROOT / "Thermal_Emission_Spectroscopy/scripts/run_life_retrieval_a1_a3_corrected_matrix.py"
OPERATOR_SOURCE = ROOT / "Thermal_Emission_Spectroscopy/scripts/life_bin_operator_diagnostic.py"
LEGACY_RUNNER = ROOT / "Thermal_Emission_Spectroscopy/scripts/run_life_retrieval.py"
CONDA_PREFIX = Path("/home/dasan/anaconda3/envs/POSEIDON")
CONDA_INIT = "/home/dasan/anaconda3/etc/profile.d/conda.sh"
POSEIDON_INPUT_DATA = "/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs"
PYSYN_CDBS = "/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids"
BINNED_REFERENCE = PROJECT / "lifesim/life_classic_binned_products.npz"
BASELINE_A3_SHORT = RETRIEVALS / "a3_1_10h_binning_corrected_loo_20261020_r03"
BASELINE_A3_100 = RETRIEVALS / "a3_100h_binning_corrected_mpi14_resume_20261018"

RANKS_PER_RUN = 4
MAX_PARALLEL = 3
TOTAL_RANK_LIMIT = 12
MIN_LOGICAL_CPUS = 16
MIN_MEM_AVAILABLE_GIB = 24
MIN_SWAP_FREE_GIB = 2
MIN_PROJECT_DISK_FREE_GIB = 80
MIN_SCRATCH_DISK_FREE_GIB = 80
MEM_GIB = 1024 * 1024
MODEL_TAGS = {
    None: "full",
    "H2O": "no_H2O",
    "CO2": "no_CO2",
    "CH4": "no_CH4",
    "O3": "no_O3",
    "N2O": "no_N2O",
    "NH3": "no_NH3",
}
DATASET_SEEDS = {
    ("A1", 1): 2125532119,
    ("A1", 10): 1099171982,
    ("A1", 100): 460512527,
    ("A3", 1): 1376328125,
    ("A3", 10): 1469409748,
    ("A3", 100): 129315834,
}
LOO_SPECIES = ("H2O", "CO2", "CH4", "O3", "N2O", "NH3")
A3_LOO_SPECIES = ("H2O", "CO2", "CH4", "O3")
BASELINE_A3_RUNS = {
    1: (BASELINE_A3_SHORT, "A3_1h_full"),
    10: (BASELINE_A3_SHORT, "A3_10h_full"),
    100: (BASELINE_A3_100, "A3_100h_full"),
}
OPERATOR_HASH = ""

MANIFEST_FIELDS = (
    "run_id", "scenario", "hours", "model", "excluded_species", "mpi_ranks",
    "declared_parameters", "effective_free_parameters", "dataset_rel",
    "dataset_seed", "dataset_sha256_expected", "matched_full_run",
    "matched_full_campaign", "output_tag", "model_name", "run_dir",
    "archive_dir", "configuration_json", "operator_preflight", "operator_runtime",
    "preflight_log", "preflight_status", "preflight_return_code", "status",
    "pid", "pid_file", "launch_log", "start_utc", "sampling_confirmed_utc",
    "end_utc", "elapsed_seconds", "return_code", "replacements", "evaluations",
    "posterior_rows", "preliminary_acceptance", "error",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


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
    # Establish the three new A1 matched baselines before launching their LOO runs.
    identities = [("A1", hours, None) for hours in (1, 10, 100)]
    identities.extend(("A1", hours, species)
                      for hours in (1, 10, 100) for species in LOO_SPECIES)
    identities.extend(("A3", hours, species)
                      for hours in (1, 10, 100) for species in A3_LOO_SPECIES)
    for scenario, hours, excluded in identities:
        run_id = case_identity(scenario, hours, excluded)
        dataset_name, dataset_hash = DATASETS[(scenario, hours)]
        full_id = case_identity(scenario, hours, None)
        if scenario == "A1":
            full_campaign = CAMPAIGN_REL.as_posix()
        else:
            full_campaign = BASELINE_A3_RUNS[hours][0].relative_to(ROOT).as_posix()
        run_tag = output_tag(scenario, hours, excluded)
        model_name = f"proxima_{scenario}_{hours}h{run_tag}"
        declared, free = (15, 14) if excluded is None else (14, 13)
        cases.append({
            "run_id": run_id,
            "scenario": scenario,
            "hours": hours,
            "model": MODEL_TAGS[excluded],
            "excluded_species": excluded or "",
            "mpi_ranks": RANKS_PER_RUN,
            "declared_parameters": declared,
            "effective_free_parameters": free,
            "dataset_rel": (PROJECT_REL / "life_data" / dataset_name).as_posix(),
            "dataset_seed": DATASET_SEEDS[(scenario, hours)],
            "dataset_sha256_expected": dataset_hash,
            "matched_full_run": full_id,
            "matched_full_campaign": full_campaign,
            "output_tag": run_tag,
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
            "sampling_confirmed_utc": "",
            "end_utc": "",
            "elapsed_seconds": "",
            "return_code": "",
            "replacements": "",
            "evaluations": "",
            "posterior_rows": "",
            "preliminary_acceptance": "PENDING",
            "error": "",
            "resume_checkpoint": False,
        })
    if len(cases) != 33 or len({case["run_id"] for case in cases}) != 33:
        raise RuntimeError("The frozen matrix must contain exactly 33 unique fresh runs")
    return cases


def resource_snapshot() -> dict:
    values: dict[str, int] = {}
    for line in Path("/proc/meminfo").read_text(encoding="ascii").splitlines():
        key, _, rest = line.partition(":")
        fields = rest.split()
        if fields and fields[0].isdigit():
            values[key] = int(fields[0])
    project_disk = shutil.disk_usage(str(ROOT)).free // (1024 ** 3)
    scratch_parent = SCRATCH.parent
    scratch_parent.mkdir(parents=True, exist_ok=True)
    scratch_disk = shutil.disk_usage(str(scratch_parent)).free // (1024 ** 3)
    return {
        "logical_cpus": os.cpu_count() or 0,
        "mem_available_kib": values.get("MemAvailable", 0),
        "swap_free_kib": values.get("SwapFree", 0),
        "project_disk_free_gib": int(project_disk),
        "scratch_disk_free_gib": int(scratch_disk),
        "observed_utc": utc_now(),
    }


def resource_problems(snapshot: dict) -> list[str]:
    problems = []
    if snapshot["logical_cpus"] < MIN_LOGICAL_CPUS:
        problems.append(f"requires {MIN_LOGICAL_CPUS} visible logical CPUs")
    if snapshot["mem_available_kib"] < MIN_MEM_AVAILABLE_GIB * MEM_GIB:
        problems.append(f"requires {MIN_MEM_AVAILABLE_GIB} GiB MemAvailable")
    if snapshot["swap_free_kib"] < MIN_SWAP_FREE_GIB * MEM_GIB:
        problems.append(f"requires {MIN_SWAP_FREE_GIB} GiB free swap")
    if snapshot["project_disk_free_gib"] < MIN_PROJECT_DISK_FREE_GIB:
        problems.append(f"requires {MIN_PROJECT_DISK_FREE_GIB} GiB free on project volume")
    if snapshot["scratch_disk_free_gib"] < MIN_SCRATCH_DISK_FREE_GIB:
        problems.append(f"requires {MIN_SCRATCH_DISK_FREE_GIB} GiB free on scratch volume")
    return problems


def foreign_sampler_processes() -> list[str]:
    patterns = ("[m]piexec", "[m]pirun", "[p]ython.*run_life_retrieval.py")
    found: list[str] = []
    for pattern in patterns:
        result = subprocess.run(["pgrep", "-af", pattern], capture_output=True,
                                text=True)
        if result.returncode == 0:
            found.extend(line for line in result.stdout.splitlines()
                         if f"{os.getpid()} " not in line)
    return found


def check_dataset_inputs() -> dict:
    records = {}
    for identity, (name, expected_hash) in DATASETS.items():
        path = PROJECT / "life_data" / name
        if not path.is_file():
            raise FileNotFoundError(f"Required frozen dataset missing: {path}")
        actual = sha256(path)
        if actual != expected_hash:
            raise ValueError(f"Dataset SHA mismatch for {identity}: {actual}")
        records[f"{identity[0]}_{identity[1]}h"] = {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": actual,
            "bytes": path.stat().st_size,
            "seed": DATASET_SEEDS[identity],
            "noise_realization_reused": True,
        }
    for path in (BINNED_REFERENCE, PROJECT / "forward_emission/A1_emission.npz",
                 PROJECT / "forward_emission/A3_emission.npz", OPERATOR_SOURCE,
                 LEGACY_RUNNER):
        if not path.is_file() or path.stat().st_size == 0:
            raise FileNotFoundError(f"Required input/source missing: {path}")
    return records


def configuration_path_for_a3(hours: int) -> Path:
    if hours in (1, 10):
        return BASELINE_A3_SHORT / "resolved" / f"A3_{hours}h_full.json"
    return BASELINE_A3_100 / "resolved_configuration.json"


def read_csv_row(path: Path, run_id: str) -> dict:
    with path.open("r", newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            if row.get("run_id") == run_id:
                return row
    raise KeyError(f"Missing baseline row {run_id} in {path}")


def retrieval_products(root: Path) -> Path:
    nested = root / "POSEIDON_output/proxima_b_earthlike/retrievals"
    if nested.is_dir():
        return nested
    if all((root / directory).is_dir()
           for directory in ("results", "samples", "MultiNest_raw")):
        return root
    products = root / "products"
    if products.is_dir():
        return products
    raise FileNotFoundError(f"No archived POSEIDON products under {root}")


def quick_validate_full_products(root: Path, model_name: str) -> dict:
    products = retrieval_products(root)
    result = products / "results" / f"{model_name}_results.txt"
    sample_dir = products / "samples"
    raw_dir = products / "MultiNest_raw"
    required = [
        result,
        sample_dir / f"{model_name}_samples.txt",
        sample_dir / f"{model_name}_spectrum_retrieved.txt",
        sample_dir / f"{model_name}_PT_retrieved.txt",
        sample_dir / f"{model_name}_log_X_retrieved.txt",
        raw_dir / f"{model_name}-stats.dat",
        raw_dir / f"{model_name}-resume.dat",
        raw_dir / f"{model_name}-post_equal_weights.dat",
        raw_dir / f"{model_name}-live.points",
        raw_dir / f"{model_name}-phys_live.points",
    ]
    for path in required:
        if not path.is_file() or path.stat().st_size == 0:
            raise FileNotFoundError(f"Matched full model lacks a required product: {path}")
    result_text = result.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"->\s*ln\s*Z\s*=\s*([-+\d.eE]+)\s*\+/-\s*([-+\d.eE]+)",
                      result_text)
    if not match or "N_live = 800" not in result_text:
        raise ValueError("Full-model results do not contain lnZ/error and N_live=800")
    lnz, lnz_err = map(float, match.groups())
    if not (math.isfinite(lnz) and math.isfinite(lnz_err) and lnz_err >= 0):
        raise ValueError("Full-model evidence is not finite")
    posterior = np.loadtxt(raw_dir / f"{model_name}-post_equal_weights.dat")
    if posterior.ndim != 2 or posterior.shape[0] < 1 or not np.all(np.isfinite(posterior)):
        raise ValueError("Full-model MultiNest posterior is empty or non-finite")
    if "N_params = 15" not in result_text:
        raise ValueError("Matched full model did not retrieve the frozen 15-coordinate model")
    return {
        "status": "PASS_PRELIMINARY_FULL_BASELINE_GATE",
        "products_root": products.as_posix(),
        "lnz": lnz,
        "lnz_error": lnz_err,
        "posterior_rows": int(posterior.shape[0]),
        "result_sha256": sha256(result),
        "multiNest_stats_sha256": sha256(raw_dir / f"{model_name}-stats.dat"),
        "required_products": [path.name for path in required],
        "independent_final_audit": "PENDING",
    }


def validate_a3_reference(hours: int) -> dict:
    campaign, run_id = BASELINE_A3_RUNS[hours]
    config_path = configuration_path_for_a3(hours)
    dataset_name, expected_hash = DATASETS[("A3", hours)]
    dataset = PROJECT / "life_data" / dataset_name
    config = json.loads(config_path.read_text(encoding="utf-8"))
    validate_resolved_config(config_path, "A3", hours, None)
    if config.get("dataset_sha256") != expected_hash:
        raise ValueError(f"A3-{hours}h full baseline dataset does not match frozen input")

    if hours in (1, 10):
        manifest = campaign / "manifest.csv"
        row = read_csv_row(manifest, run_id)
        if (row.get("preflight_status", "").startswith("PASS") is False
                or row.get("return_code") != "0" or row.get("audit_status") != "PASS"):
            raise ValueError(f"A3-{hours}h full baseline is not audited PASS in manifest")
        runtime_path = ROOT / row["operator_runtime"]
        operator = json.loads(runtime_path.read_text(encoding="utf-8"))
        if (operator.get("actual_poseidon_callback_bound") is not True
                or operator.get("dataset_sha256") != expected_hash):
            raise ValueError(f"A3-{hours}h baseline callback/dataset validation failed")
        archive = ROOT / row["archive_dir"]
        preliminary = quick_validate_full_products(archive, row["model_name"])
        return {
            "campaign": campaign.relative_to(ROOT).as_posix(),
            "run_id": run_id,
            "dataset_sha256": expected_hash,
            "configuration": config,
            "operator_record": runtime_path.relative_to(ROOT).as_posix(),
            "preliminary_products": preliminary,
            "independent_acceptance": "PASS_FROM_PRIOR_AUDIT",
        }

    state_path = campaign / "campaign_state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if (state.get("status") != "COMPLETE_VALIDATED" or state.get("exit_code") != 0
            or state.get("validation", {}).get("status") != "PASS"):
        raise ValueError("A3-100 h corrected full model lacks complete audited acceptance")
    products = campaign / "products"
    model_name = config["model_name"]
    preliminary = quick_validate_full_products(products, model_name)
    return {
        "campaign": campaign.relative_to(ROOT).as_posix(),
        "run_id": run_id,
        "dataset_sha256": expected_hash,
        "configuration": config,
        "preliminary_products": preliminary,
        "independent_acceptance": "PASS_FROM_PRIOR_AUDIT",
    }


def verify_prior_match(full: dict, model: dict, excluded: str, run_id: str) -> None:
    global_keys = (
        "dataset_sha256", "R", "wl_min", "wl_max", "n_live", "ev_tol",
        "surface_pressure_mode", "error_inflation", "x_profile", "likelihood",
        "fixed_parameters", "fixed_log10_abundances",
    )
    for key in global_keys:
        if model.get(key) != full.get(key):
            raise ValueError(f"{run_id}: matched full differs on {key}")
    excluded_parameter = f"log_{excluded}"
    expected_parameters = [name for name in full["parameters"]
                           if name != excluded_parameter]
    expected_species = [name for name in full["param_species"] if name != excluded]
    if model.get("parameters") != expected_parameters or model.get("param_species") != expected_species:
        raise ValueError(f"{run_id}: excluded parameter/species did not match the LOO design")
    if excluded_parameter in model.get("prior_types", {}) or excluded_parameter in model.get("prior_ranges", {}):
        raise ValueError(f"{run_id}: excluded parameter prior remains active")
    for parameter in expected_parameters:
        if model["prior_types"].get(parameter) != full["prior_types"].get(parameter):
            raise ValueError(f"{run_id}: shared prior type differs for {parameter}")
        if model["prior_ranges"].get(parameter) != full["prior_ranges"].get(parameter):
            raise ValueError(f"{run_id}: shared prior range differs for {parameter}")


def validate_all_matches(cases: list[dict], state: dict) -> None:
    matched = {}
    for scenario in ("A1", "A3"):
        for hours in (1, 10, 100):
            if scenario == "A1":
                full_case = next(case for case in cases if case["run_id"] ==
                                 case_identity("A1", hours, None))
                full = json.loads((ROOT / full_case["configuration_json"]).read_text(encoding="utf-8"))
                full_source = full_case["configuration_json"]
            else:
                reference = validate_a3_reference(hours)
                full = reference["configuration"]
                full_source = str(configuration_path_for_a3(hours))
                state.setdefault("existing_a3_full_references", {})[str(hours)] = reference
            for case in cases:
                if case["scenario"] != scenario or int(case["hours"]) != hours or not case["excluded_species"]:
                    continue
                model = json.loads((ROOT / case["configuration_json"]).read_text(encoding="utf-8"))
                validate_resolved_config(ROOT / case["configuration_json"], scenario, hours,
                                         case["excluded_species"])
                verify_prior_match(full, model, case["excluded_species"], case["run_id"])
                case["matched_full_campaign"] = (
                    CAMPAIGN_REL.as_posix() if scenario == "A1"
                    else BASELINE_A3_RUNS[hours][0].relative_to(ROOT).as_posix()
                )
                case["preliminary_acceptance"] = "PRELIGHT_MATCHED_FULL_PRIORS_PASS"
                matched[case["run_id"]] = {
                    "full_configuration": full_source,
                    "model_configuration": case["configuration_json"],
                    "excluded_species": case["excluded_species"],
                    "dataset_sha256": model["dataset_sha256"],
                    "shared_priors_identical": True,
                }
    state["matched_model_preflight"] = matched
    state["matched_model_preflight_status"] = "PASS_ALL_33_CASES"
    save_state(state, cases)


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
        "--campaign", "proxima", "--scenario", case["scenario"],
        "--hours", str(case["hours"]), "--n-live", "800",
        "--error-inflation", "none", "--surface-pressure-mode", "fixed-black",
        "--include-o2", "--x-profile", "isochem", "--output-tag", case["output_tag"],
        "--R", "10000", "--wl-min", "3.0", "--wl-max", "20.0",
        "--dataset-file", str(dataset), "--run-dir", str(run_dir),
        "--configuration-json", str(config),
    ]
    if case["excluded_species"]:
        arguments.extend(("--exclude-species", case["excluded_species"]))
    if setup_only:
        arguments.append("--setup-only")
    command = [str(mpiexec), "-n", str(RANKS_PER_RUN), *arguments]
    exports = [
        "export POSEIDON_input_data=" + shlex.quote(POSEIDON_INPUT_DATA),
        "export PYSYN_CDBS=" + shlex.quote(PYSYN_CDBS),
        "export OMP_NUM_THREADS=1", "export OPENBLAS_NUM_THREADS=1",
        "export MKL_NUM_THREADS=1", "export NUMEXPR_NUM_THREADS=1",
    ]
    return "; ".join([
        "set -euo pipefail", "source " + shlex.quote(CONDA_INIT),
        "conda activate POSEIDON", *exports, "cd " + shlex.quote(str(ROOT)),
        "exec " + shlex.join(command),
    ])


def run_preflights(cases: list[dict], state: dict) -> None:
    state["campaign_status"] = "PREFLIGHTING_33_CASES"
    save_state(state, cases)
    for index, case in enumerate(cases, start=1):
        paths = [ROOT / case["preflight_log"], ROOT / case["operator_preflight"],
                 ROOT / case["configuration_json"]]
        if any(path.exists() for path in paths):
            raise FileExistsError(f"Refusing to overwrite preflight evidence for {case['run_id']}")
        log_path = ROOT / case["preflight_log"]
        log_path.parent.mkdir(parents=True, exist_ok=True)
        run_dir = SCRATCH / "preflight" / case["run_id"]
        if run_dir.exists():
            raise FileExistsError(f"Refusing to reuse preflight scratch: {run_dir}")
        command = make_command(case, setup_only=True)
        state["preflight_current_run"] = case["run_id"]
        state["preflight_completed_count"] = index - 1
        save_state(state, cases)
        try:
            result = subprocess.run(
                ["/bin/bash", "-lc", command], cwd=str(ROOT),
                capture_output=True, text=True, timeout=3600,
            )
        except subprocess.TimeoutExpired as exc:
            output = (exc.stdout or "") + (exc.stderr or "")
            log_path.write_text(
                f"[preflight_utc] {utc_now()}\n[command] {command}\n{output}\n[timeout]\n",
                encoding="utf-8", errors="replace",
            )
            case.update(preflight_status="TIMEOUT", error="MPI4 setup-only preflight exceeded 3600 s")
            state.update(campaign_status="HALTED_PREFLIGHT_FAILURE",
                         halt_reason=f"{case['run_id']}: {case['error']}")
            save_state(state, cases)
            raise RuntimeError(state["halt_reason"]) from exc
        output = result.stdout + result.stderr
        log_path.write_text(
            f"[preflight_utc] {utc_now()}\n[command] {command}\n{output}",
            encoding="utf-8", errors="replace",
        )
        try:
            marker = "[setup-only] corrected operator, model, dataset and priors PASS"
            if result.returncode != 0 or marker not in output:
                raise RuntimeError(f"MPI4 setup-only preflight failed (exit {result.returncode})")
            operator_path = ROOT / case["operator_preflight"]
            operator = json.loads(operator_path.read_text(encoding="utf-8"))
            config_path = ROOT / case["configuration_json"]
            config = validate_resolved_config(
                config_path, case["scenario"], int(case["hours"]),
                case["excluded_species"] or None,
            )
            if (operator.get("status") != "PASS"
                    or operator.get("actual_poseidon_callback_bound") is not True
                    or operator.get("mpi_size") != RANKS_PER_RUN
                    or len(set(operator.get("mpi_rank_pids", []))) != RANKS_PER_RUN
                    or operator.get("dataset_sha256") != case["dataset_sha256_expected"]
                    or operator.get("operator_source_sha256") != OPERATOR_HASH):
                raise RuntimeError("Operator, MPI4, callback, or dataset preflight record mismatch")
            case.update(preflight_status="PASS_MPI4_OPERATOR_MODEL_PRIORS",
                        preflight_return_code=result.returncode,
                        preliminary_acceptance="PREFLIGHT_PASS")
            state["preflight_completed_count"] = index
        except Exception as exc:
            case.update(preflight_status="FAIL", preflight_return_code=result.returncode,
                        error=f"{type(exc).__name__}: {exc}")
            state.update(campaign_status="HALTED_PREFLIGHT_FAILURE",
                         halt_reason=f"{case['run_id']}: {case['error']}")
            save_state(state, cases)
            raise
        save_state(state, cases)
        print(f"[preflight {index}/33 PASS] {case['run_id']} MPI4 "
              f"declared={case['declared_parameters']} free={case['effective_free_parameters']}",
              flush=True)
    validate_all_matches(cases, state)
    state["campaign_status"] = "PREFLIGHT_PASS_ALL_33"
    state["preflight_completed_utc"] = utc_now()
    save_state(state, cases)


def wait_for_resources(state: dict, cases: list[dict], wave: int) -> dict:
    while True:
        snapshot = resource_snapshot()
        problems = resource_problems(snapshot)
        foreign = foreign_sampler_processes()
        if not problems and not foreign:
            state.setdefault("resource_gate", {})[str(wave)] = snapshot
            state["campaign_status"] = f"RESOURCE_GATE_PASS_WAVE_{wave}"
            save_state(state, cases)
            print(f"[resource-gate PASS] wave={wave} {snapshot}", flush=True)
            return snapshot
        reason = "; ".join(problems)
        if foreign:
            reason = "; ".join(filter(None, [reason, "other sampler process(es) active: " +
                                               " | ".join(foreign)]))
        state["latest_resource_gate"] = {
            **snapshot, "status": "WAITING", "reason": reason, "wave": wave,
        }
        state["campaign_status"] = f"WAITING_FOR_RESOURCES_WAVE_{wave}"
        save_state(state, cases)
        print(f"[resource-gate waiting] wave={wave}: {reason}", flush=True)
        time.sleep(60)


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


def resource_sample(running: dict) -> dict:
    snapshot = resource_snapshot()
    sample = {
        **snapshot,
        "active_mpi_ranks": sum(item[0]["mpi_ranks"] for item in running.values()),
        "cases": {},
    }
    for run_id, (case, process, _) in running.items():
        pids = process_tree(process.pid)
        replacements, evaluations, rows = progress(case)
        sample["cases"][run_id] = {
            "pid": process.pid,
            "pid_tree_count": len(pids),
            "pss_kib": sum(pss_kib(pid) for pid in pids),
            "replacements": replacements,
            "evaluations": evaluations,
            "posterior_rows": rows,
        }
    return sample


def launch_case(case: dict, state: dict, cases: list[dict]) -> tuple[subprocess.Popen, float]:
    run_dir = Path(case["run_dir"])
    archive = ROOT / case["archive_dir"]
    log_path = ROOT / case["launch_log"]
    if run_dir.exists() or archive.exists() or log_path.exists():
        raise FileExistsError(f"Refusing to reuse any run artifact for {case['run_id']}")
    run_dir.mkdir(parents=True, exist_ok=False)
    command = make_command(case, setup_only=False)
    record = {
        "run_id": case["run_id"], "scenario": case["scenario"],
        "hours": case["hours"], "model": case["model"],
        "excluded_species": case["excluded_species"] or None,
        "mpi_ranks": RANKS_PER_RUN, "dataset_rel": case["dataset_rel"],
        "dataset_sha256": case["dataset_sha256_expected"],
        "dataset_seed": case["dataset_seed"], "n_live": 800, "ev_tol": 0.5,
        "R": 10000, "wavelength_range_um": [3.0, 20.0],
        "x_profile": "isochem", "PT_profile": "Madhu",
        "surface": "opaque black fixed at 1 bar", "error_inflation": "none",
        "declared_parameters": case["declared_parameters"],
        "effective_free_parameters": case["effective_free_parameters"],
        "resume_checkpoint": False, "operator": OPERATOR_DESCRIPTION,
        "operator_source_sha256": OPERATOR_HASH,
        "matched_full_run": case["matched_full_run"],
        "matched_full_campaign": case["matched_full_campaign"],
        "command": command, "created_utc": utc_now(),
    }
    record_path = CAMPAIGN / "launch_records" / f"{case['run_id']}.json"
    record_path.parent.mkdir(parents=True, exist_ok=True)
    with record_path.open("x", encoding="utf-8") as stream:
        json.dump(record, stream, indent=2, sort_keys=True)
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
    pid_path = ROOT / case["pid_file"]
    pid_path.parent.mkdir(parents=True, exist_ok=True)
    with pid_path.open("x", encoding="ascii") as stream:
        stream.write(f"{process.pid}\n")
    state["active_run_ids"].append(case["run_id"])
    save_state(state, cases)
    print(f"[launched] {case['run_id']} MPI4 pid={process.pid}", flush=True)
    return process, time.monotonic()


def wait_for_wave_start(cases: list[dict], wave: int,
                        running: dict[str, tuple[dict, subprocess.Popen, float]],
                        state: dict) -> None:
    expected = set(running)
    started: set[str] = set()
    deadline = time.monotonic() + 1800
    while expected - started and time.monotonic() < deadline:
        for run_id, (case, process, _) in running.items():
            if run_id in started:
                continue
            operator_path = ROOT / case["operator_runtime"]
            raw = Path(case["run_dir"]) / "POSEIDON_output/proxima_b_earthlike/retrievals/MultiNest_raw"
            resume = raw / f"{case['model_name']}-resume.dat"
            log_path = ROOT / case["launch_log"]
            log_text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.is_file() else ""
            if (operator_path.is_file() and resume.is_file() and resume.stat().st_size > 0
                    and "[corrected-operator-active]" in log_text):
                case["status"] = "sampling"
                case["sampling_confirmed_utc"] = utc_now()
                started.add(run_id)
                print(f"[sampling confirmed] {run_id} MPI4", flush=True)
            elif process.poll() is not None:
                break
        state["sampling_start_confirmation"] = {
            "wave": wave, "confirmed_run_ids": sorted(started),
            "pending_run_ids": sorted(expected - started), "observed_utc": utc_now(),
        }
        save_state(state, cases)
        if any(process.poll() is not None for _, process, _ in running.values()):
            break
        if expected - started:
            time.sleep(10)
    if expected - started:
        state["sampling_start_confirmation"] = {
            "wave": wave, "confirmed_run_ids": sorted(started),
            "pending_run_ids": sorted(expected - started),
            "status": "START_PENDING_OR_EARLY_EXIT; logs and return codes retained",
            "observed_utc": utc_now(),
        }
        save_state(state, cases)


def harvest(case: dict) -> Path:
    source = Path(case["run_dir"])
    target = ROOT / case["archive_dir"]
    if not source.is_dir() or not any(source.iterdir()):
        raise RuntimeError(f"Successful run has no scratch products: {source}")
    if target.exists():
        raise FileExistsError(f"Refusing to overwrite archived products: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, symlinks=True)
    return target


def monitor_wave(cases: list[dict], state: dict, wave: int,
                 running: dict) -> None:
    resources_path = CAMPAIGN / "resources.jsonl"
    last_sample = 0.0
    halt_reason = ""
    completed = []
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
                try:
                    case["status"] = "harvesting"
                    save_state(state, cases)
                    archive = harvest(case)
                    if case["scenario"] == "A1" and not case["excluded_species"]:
                        case["preliminary_acceptance"] = json.dumps(
                            quick_validate_full_products(archive, case["model_name"]),
                            sort_keys=True,
                        )
                    else:
                        case["preliminary_acceptance"] = "RETURN_CODE_0_PRODUCTS_ARCHIVED; FINAL_AUDIT_PENDING"
                    case["status"] = "complete_pending_validation"
                    print(f"[completed+archived] {run_id}", flush=True)
                except Exception as exc:
                    case["status"] = "product_gate_failed"
                    case["error"] = f"{type(exc).__name__}: {exc}"
                    halt_reason = f"{run_id}: {case['error']}"
                    print(f"[PRODUCT_GATE_FAILED] {halt_reason}", flush=True)
            else:
                case["status"] = "failed"
                case["error"] = f"MPI4 retrieval exit {return_code}; scratch/logs preserved; no retry"
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
    wave_cases = state["wave_active_runs"].get(str(wave), [])
    if halt_reason:
        state["campaign_status"] = "HALTED_FAILURE"
    elif all(next(case for case in cases if case["run_id"] == run_id)["status"] ==
             "complete_pending_validation" for run_id in wave_cases):
        state.setdefault("waves_completed", []).append(wave)
        state["campaign_status"] = f"WAVE_{wave}_COMPLETE_PENDING_VALIDATION"
    else:
        state["campaign_status"] = "INCOMPLETE"
    save_state(state, cases)


def build_waves(cases: list[dict]) -> list[list[dict]]:
    baselines = [case for case in cases if case["scenario"] == "A1"
                 and not case["excluded_species"]]
    if len(baselines) != 3:
        raise RuntimeError("Expected exactly three A1 full baselines")
    remaining = [case for case in cases if case not in baselines]
    waves = [baselines] + [remaining[index:index + MAX_PARALLEL]
                           for index in range(0, len(remaining), MAX_PARALLEL)]
    if len(waves) != 11 or sum(len(wave) for wave in waves) != 33:
        raise RuntimeError("Queue must comprise 11 waves covering all 33 models")
    return waves


def run_wave(cases: list[dict], state: dict, wave: int,
             group: list[dict]) -> None:
    if not (1 <= len(group) <= MAX_PARALLEL) or len(group) * RANKS_PER_RUN > TOTAL_RANK_LIMIT:
        raise RuntimeError("Requested wave exceeds three MPI4 jobs/12 ranks")
    foreign = foreign_sampler_processes()
    if foreign:
        raise RuntimeError("Unexpected sampler exists before wave: " + " | ".join(foreign))
    wait_for_resources(state, cases, wave)
    if wave > 1:
        foreign = foreign_sampler_processes()
        if foreign:
            raise RuntimeError("Foreign sampler appeared between waves: " + " | ".join(foreign))
    if wave > 1 and not all(
            next(case for case in cases if case["run_id"] == run_id)["status"] ==
            "complete_pending_validation"
            for run_id in state.get("wave_active_runs", {}).get(str(wave - 1), [])):
        raise RuntimeError("Previous queue wave is not fully complete")
    if wave == 2:
        for hours in (1, 10, 100):
            baseline = next(case for case in cases
                            if case["run_id"] == case_identity("A1", hours, None))
            if baseline["status"] != "complete_pending_validation":
                raise RuntimeError(f"A1-{hours}h full baseline did not pass its product gate")
            baseline_gate = json.loads(baseline["preliminary_acceptance"])
            if baseline_gate.get("status") != "PASS_PRELIMINARY_FULL_BASELINE_GATE":
                raise RuntimeError(f"A1-{hours}h baseline gate has no PASS")

    state["campaign_status"] = f"RUNNING_WAVE_{wave}"
    state.setdefault("wave_started_utc", {})[str(wave)] = utc_now()
    state["wave_active_runs"][str(wave)] = [case["run_id"] for case in group]
    state["wave_mpi_ranks"][str(wave)] = len(group) * RANKS_PER_RUN
    save_state(state, cases)
    running = {}
    for case in group:
        process, started = launch_case(case, state, cases)
        running[case["run_id"]] = (case, process, started)
    print(f"[sampling wave] {wave}/11; {len(group)} retrieval(s), "
          f"MPI4 each, {len(group) * RANKS_PER_RUN} ranks total", flush=True)
    wait_for_wave_start(cases, wave, running, state)
    monitor_wave(cases, state, wave, running)
    if state.get("campaign_status") == "HALTED_FAILURE":
        raise RuntimeError(state["halt_reason"])


def verify_a3_baselines(state: dict) -> None:
    results = {}
    for hours in (1, 10, 100):
        results[str(hours)] = validate_a3_reference(hours)
        print(f"[A3 full reference PASS] {hours}h corrected baseline accepted", flush=True)
    state["existing_a3_full_references"] = results


def run_supervisor() -> int:
    if sys.platform != "linux":
        raise RuntimeError("Run the supervisor from Ubuntu/WSL POSEIDON")
    state_path = CAMPAIGN / "campaign_state.json"
    manifest_path = CAMPAIGN / "manifest.csv"
    if not state_path.is_file() or not manifest_path.is_file():
        raise FileNotFoundError("Campaign must be initialized before start")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if state.get("campaign_status") != "INITIALIZED":
        raise RuntimeError(f"Refusing duplicate/restarted supervisor at status {state.get('campaign_status')}")
    lock_handle = (CAMPAIGN / "supervisor.lock").open("a+", encoding="utf-8")
    try:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        raise RuntimeError("Another supervisor owns the campaign lock") from exc

    cases = build_cases()
    with manifest_path.open("r", newline="", encoding="utf-8") as stream:
        manifest_cases = list(csv.DictReader(stream))
    if [case["run_id"] for case in manifest_cases] != [case["run_id"] for case in cases]:
        raise RuntimeError("Initialized manifest differs from the frozen 33-run scope")
    if SCRATCH.exists():
        raise FileExistsError(f"Scratch root already exists; refusing reuse: {SCRATCH}")
    foreign = foreign_sampler_processes()
    if foreign:
        raise RuntimeError("Sampler active at supervisor start; not launching: " + " | ".join(foreign))

    state.update({"supervisor_pid": os.getpid(), "supervisor_start_utc": utc_now(),
                  "campaign_status": "PREFLIGHTING_33_CASES", "active_run_ids": [],
                  "sampling_start_confirmation": {"status": "NOT_STARTED"}})
    (CAMPAIGN / "supervisor.pid").write_text(f"{os.getpid()}\n", encoding="ascii")
    SCRATCH.mkdir(parents=True, exist_ok=False)
    save_state(state, cases)
    try:
        verify_a3_baselines(state)
        for path in (PROJECT / "life_data", PROJECT / "forward_emission",
                     PROJECT / "lifesim", ROOT / "Thermal_Emission_Spectroscopy/scripts"):
            if not path.exists():
                raise FileNotFoundError(f"Required project input tree missing: {path}")
        run_preflights(cases, state)
        state["preflight_all_33_status"] = "PASS"
        state["campaign_status"] = "QUEUED_AFTER_PREFLIGHT"
        save_state(state, cases)

        for wave, group in enumerate(build_waves(cases), start=1):
            run_wave(cases, state, wave, group)
        state.update(campaign_status="COMPLETE_PENDING_INDEPENDENT_AUDIT",
                     sampling_completed_utc=utc_now(),
                     acceptance="PENDING_INDEPENDENT_AUDIT",
                     supervisor_exit_code=0)
        save_state(state, cases)
        print("[campaign complete] 33 fresh corrected-bin models; independent audit pending",
              flush=True)
        return 0
    except Exception as exc:
        state["error"] = f"{type(exc).__name__}: {exc}"
        if state.get("campaign_status") not in {
                "HALTED_FAILURE", "HALTED_PREFLIGHT_FAILURE"}:
            state["campaign_status"] = "HALTED_FAILURE"
            state["halt_reason"] = state["error"]
        state["supervisor_exit_code"] = 2
        save_state(state, cases)
        print(f"[SUPERVISOR_ERROR] {state['error']}", file=sys.stderr, flush=True)
        return 2
    finally:
        lock_handle.close()


def initialize_campaign() -> None:
    if sys.platform != "linux":
        raise RuntimeError("Initialize from Ubuntu/WSL POSEIDON")
    if CAMPAIGN.exists():
        raise FileExistsError(f"Refusing to overwrite campaign: {CAMPAIGN}")
    if SCRATCH.exists():
        raise FileExistsError(f"Refusing to reuse scratch root: {SCRATCH}")
    if foreign_sampler_processes():
        raise RuntimeError("Active sampler detected; campaign was not initialized")
    datasets = check_dataset_inputs()
    resource = resource_snapshot()
    problems = resource_problems(resource)
    if problems:
        raise RuntimeError("Initial resource gate failed: " + "; ".join(problems))
    if not BASELINE_A3_SHORT.is_dir() or not BASELINE_A3_100.is_dir():
        raise FileNotFoundError("Validated corrected A3 full references are missing")
    a3_baselines = {str(hours): validate_a3_reference(hours)
                    for hours in (1, 10, 100)}
    cases = build_cases()
    CAMPAIGN.mkdir(parents=True, exist_ok=False)
    for directory in ("preflight/operators", "resolved", "runtime/operators", "logs",
                      "pids", "launch_records", "runs"):
        (CAMPAIGN / directory).mkdir(parents=True, exist_ok=False)
    selected_scope = {
        "campaign_id": "proxima_A1_A3_corrected_bin_matrix_33_20261021_r01",
        "created_utc": utc_now(),
        "authorized_run_count": 33,
        "scope": {
            "scenarios": ["A1", "A3"], "exposures_hours": [1, 10, 100],
            "A1_models": ["full", "no_H2O", "no_CO2", "no_CH4", "no_O3", "no_N2O", "no_NH3"],
            "A3_models": ["no_H2O", "no_CO2", "no_CH4", "no_O3"],
            "A3_full_baselines": "Reuse only previously audited corrected-bin full retrievals at 1/10/100 h",
            "excluded_from_scope": ["three A3-100h A0-fixed cases", "A3-1/10h A0-fixed cases",
                                    "A3-1000h cases", "A0/A2 scenarios"],
        },
        "execution": {
            "ranks_per_retrieval": RANKS_PER_RUN,
            "max_parallel_retrievals": MAX_PARALLEL,
            "max_active_mpi_ranks": TOTAL_RANK_LIMIT,
            "threads_per_rank": 1,
            "logical_cpu_requirement": MIN_LOGICAL_CPUS,
            "queue_waves": 11,
            "queue_order": "Three A1 full baselines first; then A1 and A3 LOO models in waves of at most three.",
            "checkpoint_reuse": False,
            "retry_on_failure": False,
        },
        "configuration": {
            "PT_profile": "Madhu", "abundance_profile": "isochem", "include_O2": True,
            "N_live": 800, "ev_tol": 0.5, "R": 10000,
            "wavelength_range_um": [3.0, 20.0],
            "surface": "opaque black fixed at 1 bar", "error_inflation": "none",
            "corrected_bin_operator": OPERATOR_DESCRIPTION,
            "model_dimensions": {"full": "15 declared / 14 free", "LOO": "14 declared / 13 free"},
        },
        "datasets": datasets,
        "operator_source_sha256": OPERATOR_HASH,
        "baseline_A3_campaigns": {
            str(hours): {"campaign": campaign.relative_to(ROOT).as_posix(),
                         "run_id": run_id}
            for hours, (campaign, run_id) in BASELINE_A3_RUNS.items()
        },
        "baseline_A3_acceptance": a3_baselines,
        "historical_A1_fulls": "Not used as evidence comparators; fresh matched A1 full runs are included above.",
    }
    write_json(CAMPAIGN / "selected_scope.json", selected_scope)
    write_json(CAMPAIGN / "preserved_inputs.json", {
        "datasets": datasets,
        "operator_source_sha256": OPERATOR_HASH,
        "native_A1_sha256": sha256(PROJECT / "forward_emission/A1_emission.npz"),
        "native_A3_sha256": sha256(PROJECT / "forward_emission/A3_emission.npz"),
        "binned_reference_sha256": sha256(BINNED_REFERENCE),
        "runner_sha256": sha256(RUNNER),
        "legacy_runner_sha256": sha256(LEGACY_RUNNER),
        "checkpoint_reuse": False,
    })
    state = {
        "campaign_status": "INITIALIZED",
        "campaign_id": selected_scope["campaign_id"],
        "authorized_run_count": 33,
        "created_utc": utc_now(),
        "supervisor_pid": None,
        "supervisor_exit_code": None,
        "acceptance": "NOT_STARTED",
        "preflight_completed_count": 0,
        "preflight_all_33_status": "PENDING",
        "active_run_ids": [],
        "waves_completed": [],
        "wave_active_runs": {},
        "wave_mpi_ranks": {},
        "matched_model_preflight_status": "PENDING",
        "latest_resources": resource,
        "checkpoint_reuse": False,
        "canonical_8of8_modified": False,
        "legacy_products_modified": False,
    }
    save_state(state, cases)
    (CAMPAIGN / "README.md").write_text(
        "# A1/A3 corrected-bin homologous LIFE retrieval matrix\n\n"
        "Status: `INITIALIZED`; preflight and sampling have not started. This isolated campaign contains 33 fresh retrievals: "
        "three A1 full baselines, 18 A1 molecular ablations, and 12 A3 ablations for H2O/CO2/CH4/O3. "
        "Each sampled retrieval uses MPI4, at most three in parallel (12 ranks total), one thread per rank. "
        "A3 full references are reused only from the independently audited corrected-bin 1/10/100 h campaigns.\n\n"
        "No checkpoints are reused. The queue preflights all 33 configurations before sampling, runs A1 full baselines first, "
        "then the matched LOO models. Evidence comparisons are restricted to the same scenario, exposure, dataset hash, "
        "operator, prior and likelihood. Final independent audit and ΔlnZ tables remain pending.\n\n"
        "Source of truth: `selected_scope.json`, `campaign_state.json`, `manifest.csv`, per-run logs, runtime operator records, "
        "and archived products under `runs/`. Scratch is separate under `/home/dasan/exofarm_a1_a3_corrected_binning_matrix_20261021_r01/`.\n",
        encoding="utf-8",
    )
    print(f"[initialized] {CAMPAIGN_REL.as_posix()} with 33 runs; no sampling started", flush=True)


def main() -> int:
    global OPERATOR_HASH
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--initialize", action="store_true")
    mode.add_argument("--start", action="store_true")
    args = parser.parse_args()
    OPERATOR_HASH = sha256(OPERATOR_SOURCE)
    if args.initialize:
        initialize_campaign()
        return 0
    return run_supervisor()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[LAUNCH_ERROR] {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
        raise
