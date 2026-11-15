"""Launch one fresh, audited A3-100 h retrieval with corrected LIFE binning."""

import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1"
RETRIEVALS = PROJECT / "retrievals"
CAMPAIGN = RETRIEVALS / "a3_100h_binning_corrected_20261017"
SCRATCH = Path("/home/dasan/exofarm_a3_100h_binning_corrected_20261017")
DATASET = PROJECT / "life_data/LIFE_proxima_A3_100h.dat"
DATASET_REL = DATASET.relative_to(ROOT)
EXPECTED_HASH = "78662546181a5b74391a14b7b73ae80d879200a74db6a4bc5338e3ce7eee4705"
BASELINE_MANIFEST = (
    RETRIEVALS / "POSEIDON_output/proxima_b_earthlike/retrievals/results"
    / "proxima_A3_100h_O2_fixedBlack1bar_noxtol_proxima_A3_100h_O2_fixedBlack1bar_noxtol_postprocess_manifest.json"
)
RUNNER = ROOT / "Thermal_Emission_Spectroscopy/scripts/run_life_retrieval_a3_100h_binning_corrected.py"
BASE_RUNNER = ROOT / "Thermal_Emission_Spectroscopy/scripts/run_life_retrieval.py"
OPERATOR = ROOT / "Thermal_Emission_Spectroscopy/scripts/life_bin_operator_diagnostic.py"
PREFIX = Path("/home/dasan/anaconda3/envs/POSEIDON")
PYTHON = PREFIX / "bin/python"
LOG = RETRIEVALS / "a3_100h_binning_corrected_20261017.supervisor.log"
PIDFILE = RETRIEVALS / "a3_100h_binning_corrected_20261017.supervisor.pid"
STATE = CAMPAIGN / "campaign_state.json"
MANIFEST = CAMPAIGN / "manifest.csv"
RUN_ID = "A3_100h_full_BIN1_20261017"
TAG = "_O2_fixedBlack1bar_noxtol_BIN1_20261017"


def utc_now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def record(state):
    state["updated_utc"] = utc_now()
    write_json(STATE, state)


def process_lines():
    output = subprocess.check_output(["ps", "-eo", "pid,args"], text=True)
    return output.splitlines()[1:]


def active_retrievals():
    tokens = (
        "mpiexec", "mpirun", "run_life_retrieval.py",
        "run_life_retrieval_binning_corrected.py",
        "run_life_retrieval_a3_100h_binning_corrected.py",
    )
    return [line for line in process_lines()
            if any(token in line for token in tokens)]


def mem_available_kib():
    text = Path("/proc/meminfo").read_text(encoding="utf-8")
    match = re.search(r"^MemAvailable:\s+(\d+)\s+kB", text, re.MULTILINE)
    if not match:
        raise RuntimeError("MemAvailable is absent from /proc/meminfo")
    return int(match.group(1))


def pss_kib(pid):
    path = Path(f"/proc/{pid}/smaps_rollup")
    if not path.exists():
        return 0
    match = re.search(r"^Pss:\s+(\d+)\s+kB", path.read_text(), re.MULTILINE)
    return int(match.group(1)) if match else 0


def environment():
    env = os.environ.copy()
    env.update({
        "POSEIDON_input_data": "/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs",
        "PYSYN_CDBS": "/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids",
        "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1",
    })
    return env


def run_preflight(command, log_path):
    peak_pss = 0
    minimum_available = mem_available_kib()
    with log_path.open("x", encoding="utf-8") as stream:
        process = subprocess.Popen(
            command, cwd=RUNNER.parent, env=environment(),
            stdout=stream, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
        )
        while process.poll() is None:
            peak_pss = max(peak_pss, pss_kib(process.pid))
            minimum_available = min(minimum_available, mem_available_kib())
            time.sleep(1)
        return_code = process.wait()
    return return_code, peak_pss, minimum_available


def runner_arguments(operator_record, run_dir, configuration, setup_only):
    result = [
        "--operator-record", str(operator_record),
        "--campaign", "proxima", "--scenario", "A3", "--hours", "100",
        "--n-live", "800", "--error-inflation", "none",
        "--surface-pressure-mode", "fixed-black", "--include-o2",
        "--x-profile", "isochem", "--output-tag", TAG,
        "--R", "10000", "--wl-min", "3.0", "--wl-max", "20.0",
        "--dataset-file", str(DATASET_REL), "--run-dir", str(run_dir),
        "--configuration-json", str(configuration),
    ]
    if setup_only:
        result += ["--setup-only", "--validate-forward"]
    return result


def validate_resolved(configuration):
    baseline = json.loads(BASELINE_MANIFEST.read_text(encoding="utf-8"))
    resolved = json.loads(configuration.read_text(encoding="utf-8"))
    old = baseline["configuration"]
    checks = {
        "dataset_hash": (baseline["dataset_sha256"], EXPECTED_HASH),
        "parameters": (baseline["parameter_names"], resolved["parameters"]),
        "n_live": (old["N_live"], resolved["n_live"]),
        "error_inflation": (old["error_inflation"], resolved["error_inflation"]),
        "R": (old["R"], resolved["R"]),
        "x_profile": (old["X_profile"], resolved["x_profile"]),
    }
    mismatches = {name: values for name, values in checks.items()
                  if values[0] != values[1]}
    expected_species = ["H2O", "CO2", "CH4", "O2", "O3", "N2O", "NH3"]
    if resolved["param_species"] != expected_species:
        mismatches["param_species"] = [expected_species, resolved["param_species"]]
    if resolved["declared_dimension"] != 15 or resolved["effective_free_dimension"] != 14:
        mismatches["dimensions"] = [
            "15 declared / 14 free",
            [resolved["declared_dimension"], resolved["effective_free_dimension"]],
        ]
    if resolved["fixed_parameters"] != ["log_P_surf"]:
        mismatches["fixed_parameters"] = [["log_P_surf"], resolved["fixed_parameters"]]
    if resolved["prior_ranges"].get("log_P_surf") != [0.0, 0.0]:
        mismatches["surface_prior"] = [
            [0.0, 0.0], resolved["prior_ranges"].get("log_P_surf")
        ]
    if "x_tol" in resolved["parameters"]:
        mismatches["x_tol"] = ["absent", "present"]
    if resolved["dataset_sha256"] != EXPECTED_HASH:
        mismatches["resolved_dataset_hash"] = [EXPECTED_HASH, resolved["dataset_sha256"]]
    if resolved["wl_min"] != 3.0 or resolved["wl_max"] != 20.0:
        mismatches["native_wavelength_range"] = [
            [3.0, 20.0], [resolved["wl_min"], resolved["wl_max"]]
        ]
    if mismatches:
        raise RuntimeError(
            f"Resolved scope differs from the frozen comparison: {mismatches}"
        )
    return {
        "status": "PASS",
        "matched_to_previous_A3_100h": [
            "same dataset hash and 31-channel observation",
            "same 15 parameter coordinates / 14 effective free parameters",
            "same species, N_live, no-inflation likelihood, R, and isochemical profile",
            "same fixed black surface at 1 bar and O2-inclusive model",
        ],
        "historical_prior_record": (
            "the previous run's postprocess manifest records the prior family, "
            "but not a full machine-readable resolved prior table"
        ),
        "intentional_operator_scope_difference": {
            "historical_native_range_um": [3.8, 19.0],
            "corrected_native_range_um": [3.0, 20.0],
            "reason": "cover complete photon-overlap channel edges",
        },
        "resolved_configuration": str(configuration),
    }


def write_manifest(row):
    columns = [
        "run_id", "scenario", "hours", "operator", "status", "mpi_ranks",
        "n_live", "declared_dimension", "effective_free_dimension",
        "dataset_sha256", "run_dir", "archive_dir", "log", "return_code",
    ]
    with MANIFEST.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerow({key: row.get(key, "") for key in columns})


def worker():
    state = json.loads(STATE.read_text(encoding="utf-8"))
    row = None
    try:
        state.update(status="PREFLIGHT", supervisor_pid=os.getpid())
        record(state)
        if sha256(DATASET) != EXPECTED_HASH:
            raise ValueError("100 h observed dataset SHA-256 changed")
        if not BASELINE_MANIFEST.is_file():
            raise FileNotFoundError(
                f"Missing 100 h baseline manifest: {BASELINE_MANIFEST}"
            )
        conflicts = active_retrievals()
        if conflicts:
            raise RuntimeError(f"Other retrieval/MPI processes are active: {conflicts}")

        setup_command = [
            str(PYTHON), "-u", str(RUNNER),
            *runner_arguments(
                CAMPAIGN / "operator_preflight.json", SCRATCH / "preflight",
                CAMPAIGN / "resolved_configuration.json", True,
            ),
        ]
        return_code, peak_pss, minimum_available = run_preflight(
            setup_command, CAMPAIGN / "preflight.log"
        )
        if return_code != 0:
            raise RuntimeError(f"Corrected operator preflight exited {return_code}")
        preflight = json.loads(
            (CAMPAIGN / "operator_preflight.json").read_text(encoding="utf-8")
        )
        if preflight.get("status") != "PASS":
            raise RuntimeError("Operator record is not PASS")
        matched = validate_resolved(CAMPAIGN / "resolved_configuration.json")
        required_kib = peak_pss + int(4.5 * 1024 * 1024)
        resource_record = {
            "execution": "serial, one Python process / one BLAS thread",
            "peak_preflight_PSS_KiB": peak_pss,
            "minimum_MemAvailable_KiB": minimum_available,
            "required_MemAvailable_KiB": required_kib,
            "reserve_KiB": int(4.5 * 1024 * 1024),
            "status": "PASS" if minimum_available >= required_kib else "FAIL",
        }
        write_json(CAMPAIGN / "resource_gate.json", resource_record)
        if minimum_available < required_kib:
            raise RuntimeError(f"Memory gate failed: {resource_record}")
        if active_retrievals():
            raise RuntimeError("A competing retrieval/MPI process appeared after preflight")

        row = {
            "run_id": RUN_ID, "scenario": "A3", "hours": 100,
            "operator": "corrected midpoint-edge photon overlap",
            "status": "RUNNING", "mpi_ranks": 1, "n_live": 800,
            "declared_dimension": 15, "effective_free_dimension": 14,
            "dataset_sha256": EXPECTED_HASH,
            "run_dir": str(SCRATCH / "run"),
            "archive_dir": str(CAMPAIGN / "products"),
            "log": str(CAMPAIGN / "retrieval.log"), "return_code": "",
        }
        write_manifest(row)
        state.update(status="RUNNING", preflight="PASS",
                     baseline_configuration=matched,
                     resources=resource_record, run_id=RUN_ID,
                     mpi_ranks=1, run_pid=None, start_utc=utc_now())
        record(state)
        command = [
            str(PYTHON), "-u", str(RUNNER),
            *runner_arguments(
                CAMPAIGN / "operator_preflight.json", SCRATCH / "run",
                CAMPAIGN / "resolved_configuration.json", False,
            ),
        ]
        with (CAMPAIGN / "retrieval.log").open("x", encoding="utf-8") as stream:
            process = subprocess.Popen(
                command, cwd=RUNNER.parent, env=environment(),
                stdout=stream, stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL, start_new_session=True,
            )
            state["run_pid"] = process.pid
            record(state)
            return_code = process.wait()
        row["return_code"] = return_code
        if return_code != 0:
            row["status"] = "FAILED"
            write_manifest(row)
            raise RuntimeError(f"Retrieval exited {return_code}; scratch preserved")

        source = SCRATCH / "run/POSEIDON_output/proxima_b_earthlike/retrievals"
        for folder in ("MultiNest_raw", "results", "samples"):
            if not (source / folder).is_dir():
                raise RuntimeError(f"Missing expected output directory: {source / folder}")
        shutil.copytree(source, CAMPAIGN / "products")
        row["status"] = "COMPLETE_PENDING_VALIDATION"
        write_manifest(row)
        state.update(status="COMPLETE_PENDING_VALIDATION", exit_code=0,
                     products="products", acceptance="PENDING_INDEPENDENT_AUDIT",
                     scratch_preserved=True, end_utc=utc_now())
        record(state)
    except Exception as error:
        state.update(status="FAILED", error=f"{type(error).__name__}: {error}",
                     scratch_preserved=True)
        record(state)
        if row is not None:
            row["status"] = "FAILED"
            write_manifest(row)
        elif MANIFEST.exists():
            rows = list(csv.DictReader(
                MANIFEST.open(encoding="utf-8", newline="")
            ))
            if rows:
                rows[0]["status"] = "FAILED"
                write_manifest(rows[0])
        traceback.print_exc()
        raise


def launch():
    if sys.platform != "linux":
        raise RuntimeError("Launch this retrieval from Ubuntu/WSL POSEIDON")
    if Path(sys.executable).resolve() != PYTHON.resolve():
        raise RuntimeError(f"Unexpected interpreter: {sys.executable}")
    if any(path.exists() for path in (CAMPAIGN, LOG, PIDFILE, SCRATCH)):
        raise RuntimeError("Campaign, log, PID, or scratch exists; refusing overwrite")
    if sha256(DATASET) != EXPECTED_HASH:
        raise ValueError("A3-100 h dataset hash changed")
    baseline = json.loads(BASELINE_MANIFEST.read_text(encoding="utf-8"))
    if baseline.get("dataset_sha256") != EXPECTED_HASH:
        raise ValueError("Existing 100 h baseline uses a different observation")
    conflicts = active_retrievals()
    if conflicts:
        raise RuntimeError(f"Retrieval/MPI processes already active: {conflicts}")

    CAMPAIGN.mkdir(parents=True)
    (CAMPAIGN / "launch.lock").mkdir()
    SCRATCH.mkdir(parents=True)
    preserved = {
        "dataset": str(DATASET.relative_to(ROOT)),
        "dataset_sha256": EXPECTED_HASH,
        "baseline_manifest": str(BASELINE_MANIFEST.relative_to(ROOT)),
        "baseline_manifest_sha256": sha256(BASELINE_MANIFEST),
        "base_runner": str(BASE_RUNNER.relative_to(ROOT)),
        "base_runner_sha256": sha256(BASE_RUNNER),
        "corrected_runner": str(RUNNER.relative_to(ROOT)),
        "corrected_runner_sha256": sha256(RUNNER),
        "operator": str(OPERATOR.relative_to(ROOT)),
        "operator_sha256": sha256(OPERATOR),
    }
    write_json(CAMPAIGN / "preserved_inputs.json", preserved)
    scope = {
        "campaign": CAMPAIGN.name,
        "authorized_runs": 1,
        "scenario": "A3",
        "hours": 100,
        "variant": "full",
        "dataset": str(DATASET.relative_to(ROOT)),
        "dataset_sha256": EXPECTED_HASH,
        "channels": 31,
        "seed": 129315834,
        "n_live": 800,
        "evidence_tolerance": 0.5,
        "R": 10000,
        "wavelength_range_um": [3.0, 20.0],
        "x_profile": "isochem",
        "param_species": ["H2O", "CO2", "CH4", "O2", "O3", "N2O", "NH3"],
        "surface": "explicit black surface fixed at 1 bar",
        "error_inflation": "none",
        "declared_coordinates": 15,
        "effective_free_coordinates": 14,
        "execution": "one serial Python process; one BLAS thread; no MPI",
        "checkpoint_reuse": False,
        "comparison_baseline": str(BASELINE_MANIFEST.relative_to(ROOT)),
        "scientific_change": (
            "generator-compatible photon-overlap observation operator; same data "
            "realization; extend native model grid to 3-20 um to cover full channel edges"
        ),
        "previous_operator": "POSEIDON historical energy-space bin_spectrum_to_data",
        "authorization_utc": utc_now(),
    }
    write_json(CAMPAIGN / "selected_scope.json", scope)
    state = {
        "status": "STARTING",
        "authorized_runs": 1,
        "scenario": "A3",
        "hours": 100,
        "dataset_sha256": EXPECTED_HASH,
        "mpi_ranks": 1,
        "n_live": 800,
        "acceptance": "PENDING",
        "scratch": str(SCRATCH),
        "model_name": "proxima_A3_100h" + TAG,
        "operator": "corrected midpoint-edge photon overlap",
        "checkpoint_reuse": False,
        "baseline": str(BASELINE_MANIFEST.relative_to(ROOT)),
        "selected_scope": "selected_scope.json",
        "created_utc": utc_now(),
    }
    record(state)
    row = {
        "run_id": RUN_ID, "scenario": "A3", "hours": 100,
        "operator": "corrected midpoint-edge photon overlap",
        "status": "STARTING", "mpi_ranks": 1, "n_live": 800,
        "declared_dimension": 15, "effective_free_dimension": 14,
        "dataset_sha256": EXPECTED_HASH, "run_dir": str(SCRATCH / "run"),
        "archive_dir": str(CAMPAIGN / "products"),
        "log": str(CAMPAIGN / "retrieval.log"), "return_code": "",
    }
    write_manifest(row)
    with LOG.open("x", encoding="utf-8") as stream:
        process = subprocess.Popen(
            [str(PYTHON), "-u", str(Path(__file__).resolve()), "--worker"],
            cwd=ROOT, env=environment(), stdout=stream, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL, start_new_session=True,
        )
    PIDFILE.write_text(str(process.pid) + "\n", encoding="utf-8")
    time.sleep(2)
    if process.poll() is not None:
        raise RuntimeError(f"Supervisor exited {process.returncode}; inspect {LOG}")
    print(json.dumps({"supervisor_pid": process.pid,
                      "campaign_state": str(STATE), "log": str(LOG)}))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        worker()
    else:
        launch()
