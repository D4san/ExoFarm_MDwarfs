"""Launch exactly one authorized A3-1000 h full retrieval, without overwrites.

Keep the official 100 h model and priors; change only integration time and
the recorded independent noise realization. A detached supervisor preserves
scratch and archives products after exit zero, pending scientific acceptance.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

from run_proxima_molecule_ablation_campaign import DATASETS, PROJECT_REL


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "Thermal_Emission_Spectroscopy/scripts"
PROJECT = ROOT / PROJECT_REL
CAMPAIGN = PROJECT / "retrievals/a3_1000h_full_20261011"
SCRATCH = Path("/home/dasan/exofarm_a3_1000h_20261011")
PREFIX = Path("/home/dasan/anaconda3/envs/POSEIDON")
TAG = "_O2_fixedBlack1bar_noxtol_MPI6_1000h"
DATASET = PROJECT / "life_data/LIFE_proxima_A3_1000h_O2_fixedBlack1bar_official.dat"
INDEX = PROJECT / "life_data/dataset_index_A3_1000h_official.json"
STATE = CAMPAIGN / "campaign_state.json"
LOG = CAMPAIGN.parent / "a3_1000h_full_20261011.supervisor.log"
PID = CAMPAIGN.parent / "a3_1000h_full_20261011.supervisor.pid"
FIRST_ATTEMPT = CAMPAIGN
NATIVE_GRID = False


def select_native_grid_retry():
    """Isolate the diagnosed numerical correction; retain every first record."""
    global CAMPAIGN, SCRATCH, STATE, LOG, PID, TAG, NATIVE_GRID
    NATIVE_GRID = True
    CAMPAIGN = FIRST_ATTEMPT / "native_grid_retry"
    SCRATCH = Path("/home/dasan/exofarm_a3_1000h_20261011_nativegrid")
    STATE = CAMPAIGN / "campaign_state.json"
    LOG = FIRST_ATTEMPT.parent / "a3_1000h_full_20261011.nativegrid.supervisor.log"
    PID = LOG.with_suffix(".pid")
    TAG = "_O2_fixedBlack1bar_noxtol_MPI6_NG"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def record(payload):
    payload["updated_utc"] = datetime.now(timezone.utc).isoformat()
    temporary = STATE.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(STATE)


def active_science():
    lines = subprocess.check_output(["ps", "-eo", "pid,args"], text=True).splitlines()
    return [line for line in lines if any(token in line for token in
            ("/bin/mpiexec", "run_life_retrieval.py", "vulcan.py", "lpjml "))]


def frozen_inputs():
    paths = [PROJECT / "life_data" / row["file"] for row in DATASETS.values()]
    paths += list((PROJECT / "life_data").glob("dataset_index*.json"))
    paths += [PROJECT / "forward_emission/A3_emission.npz",
              PROJECT / "lifesim/life_classic_binned_products.npz",
              SCRIPTS / "run_life_retrieval.py", SCRIPTS / "make_life_datasets.py",
              SCRIPTS / "emission_forward.py",
              PROJECT / "retrievals/molecule_ablation_loo_20261004/campaign_state.json",
              PROJECT / "retrievals/a0_fixed_reference_20261010/campaign_state.json"]
    return {str(path.relative_to(ROOT)): sha256(path) for path in paths}


def verify_frozen(snapshot):
    for relative, expected in snapshot.items():
        if sha256(ROOT / relative) != expected:
            raise RuntimeError(f"Frozen input changed: {relative}")


def environment_command(argv):
    setup = (
        "source /home/dasan/anaconda3/etc/profile.d/conda.sh && "
        "conda activate POSEIDON && "
        "export POSEIDON_input_data=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs "
        "PYSYN_CDBS=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids "
        "OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 "
        "NUMEXPR_NUM_THREADS=1 && exec "
    )
    return ["bash", "-lc", setup + shlex.join([str(value) for value in argv])]


def run_stage(argv, log_name):
    with (CAMPAIGN / log_name).open("x", encoding="utf-8") as stream:
        subprocess.run(environment_command(argv), cwd=SCRIPTS, stdout=stream,
                       stderr=subprocess.STDOUT, check=True)


def validate_dataset():
    import numpy as np

    data = np.loadtxt(DATASET, skiprows=1)
    baseline = np.loadtxt(PROJECT / "life_data/LIFE_proxima_A3_100h.dat", skiprows=1)
    if data.shape != (31, 4) or not np.isfinite(data).all():
        raise ValueError("Dataset must have 31 finite rows and four columns")
    if np.any(data[:, 1] <= 0) or np.any(data[:, 3] <= 0):
        raise ValueError("Nonpositive bin widths or uncertainties")
    np.testing.assert_array_equal(data[:, :2], baseline[:, :2])
    # Existing ASCII files round to seven significant digits.
    np.testing.assert_allclose(data[:, 3], baseline[:, 3] / np.sqrt(10), rtol=2e-6)
    index = json.loads(INDEX.read_text())
    row, = index["datasets"]
    if row["scenario"] != "A3" or row["hours"] != 1000 or row["n_bins"] != 31:
        raise ValueError("Unexpected scenario, exposure or channel count")
    return row


def common_arguments():
    arguments = ["--campaign", "proxima", "--scenario", "A3", "--hours", "1000",
            "--n-live", "800", "--error-inflation", "none",
            "--surface-pressure-mode", "fixed-black", "--include-o2",
            "--x-profile", "isochem", "--output-tag", TAG, "--R", "10000",
            "--dataset-file", str(DATASET.relative_to(ROOT))]
    if NATIVE_GRID:
        # Match the generator's exact opacity-sampling grid, not just its R.
        # The 31 observed bins and all physical parameters remain unchanged.
        arguments += ["--wl-min", "3.0", "--wl-max", "20.0"]
    return arguments


def worker():
    state = json.loads(STATE.read_text())
    try:
        state.update(status="VERIFYING_EXISTING_DATASET" if NATIVE_GRID
                     else "GENERATING_DATASET", supervisor_pid=os.getpid())
        record(state)
        snapshot = json.loads((CAMPAIGN / "preserved_inputs.json").read_text())
        verify_frozen(snapshot)
        if not NATIVE_GRID:
            run_stage([PREFIX / "bin/python", "-u", SCRIPTS / "make_life_datasets.py",
                       "--campaign", "proxima", "--scenarios", "A3", "--hours", "1000",
                       "--seed", "20261011", "--name-suffix", "_O2_fixedBlack1bar_official",
                       "--index-output", INDEX, "--index-classification",
                       "authorized_A3_1000h_extension_pending_validation"], "dataset.log")
        row = validate_dataset()
        state.update(status="PREFLIGHT", dataset_sha256=sha256(DATASET), seed=row["seed"])
        record(state)
        (CAMPAIGN / "manifest.csv").write_text(
            "run_id,scenario,hours,model,mpi_ranks,n_live,dataset_sha256,seed\n"
            f"A3_1000h_full,A3,1000,full,6,800,{state['dataset_sha256']},{row['seed']}\n",
            encoding="utf-8",
        )
        configuration = CAMPAIGN / "resolved_configuration.json"
        run_stage([PREFIX / "bin/python", "-u", SCRIPTS / "run_life_retrieval.py",
                   *common_arguments(), "--run-dir", SCRATCH / "preflight",
                   "--configuration-json", configuration, "--setup-only",
                   "--validate-forward"], "preflight.log")
        resolved = json.loads(configuration.read_text())
        reference = json.loads((PROJECT / "retrievals/a0_fixed_reference_20261010/resolved/"
                                "A3_100h_A0_NH3_fullcheck.json").read_text())
        keys = ("parameters", "declared_dimension", "effective_free_dimension",
                "fixed_parameters", "fixed_log10_abundances", "param_species",
                "prior_types", "prior_ranges", "R", "wl_min", "wl_max", "n_live",
                "ev_tol", "surface_pressure_mode", "error_inflation", "x_profile",
                "likelihood")
        for key in keys:
            expected = reference[key]
            if NATIVE_GRID and key in ("wl_min", "wl_max"):
                expected = {"wl_min": 3.0, "wl_max": 20.0}[key]
            if resolved[key] != expected:
                raise ValueError(f"Configuration differs from official 100 h model: {key}")
        if NATIVE_GRID:
            comparison = {
                "physical_model_and_priors": "IDENTICAL",
                "changed_numerical_keys": {
                    key: {"official_100h": reference[key], "new_1000h": resolved[key]}
                    for key in ("wl_min", "wl_max")
                },
                "reason": "Exact native generator grid; diagnostic RMS=max=0 sigma",
                "observed_bins": "UNCHANGED", "R": 10000,
            }
            (CAMPAIGN / "baseline_configuration_comparison.json").write_text(
                json.dumps(comparison, indent=2) + "\n", encoding="utf-8")
        if resolved["declared_dimension"] != 15 or resolved["effective_free_dimension"] != 14:
            raise ValueError("Unexpected parameter count")
        verify_frozen(snapshot)
        if active_science():
            raise RuntimeError("Scientific processes appeared during preflight")
        state.update(status="RUNNING", preflight="PASS", baseline_priors="IDENTICAL")
        with (CAMPAIGN / "retrieval.log").open("x", encoding="utf-8") as stream:
            process = subprocess.Popen(environment_command([
                PREFIX / "bin/mpiexec", "-n", "6", PREFIX / "bin/python", "-u",
                SCRIPTS / "run_life_retrieval.py", *common_arguments(),
                "--run-dir", SCRATCH / "run"]), cwd=SCRIPTS, stdout=stream,
                stderr=subprocess.STDOUT)
            state["mpiexec_pid"] = process.pid
            record(state)
            exit_code = process.wait()
        state["exit_code"] = exit_code
        if exit_code != 0:
            raise RuntimeError(f"Retrieval exited {exit_code}; all products preserved")
        source = SCRATCH / "run/POSEIDON_output/proxima_b_earthlike/retrievals"
        for folder in ("MultiNest_raw", "results", "samples"):
            if not (source / folder).is_dir():
                raise RuntimeError(f"Missing product directory: {source / folder}")
        shutil.copytree(source, CAMPAIGN / "products")
        verify_frozen(snapshot)
        state.update(status="COMPLETE_PENDING_VALIDATION", acceptance="PENDING",
                     products="products", scratch_preserved=True)
        record(state)
        print("[complete] exit 0; archived products require independent scientific audit", flush=True)
    except Exception as error:
        state.update(status="FAILED", error=f"{type(error).__name__}: {error}",
                     scratch_preserved=True)
        record(state)
        raise


def launch():
    if sys.platform != "linux":
        raise RuntimeError("Launch exclusively inside the verified Ubuntu environment")
    if NATIVE_GRID:
        first = json.loads((FIRST_ATTEMPT / "campaign_state.json").read_text())
        diagnostic = json.loads((FIRST_ATTEMPT / "native_grid_diagnostic.json").read_text())
        if first["status"] != "FAILED" or (FIRST_ATTEMPT / "retrieval.log").exists():
            raise RuntimeError("Retry only a failed preflight with no sampling")
        if not (diagnostic["finite"] and diagnostic["rms_sigma"] == 0.0
                and diagnostic["max_sigma"] == 0.0):
            raise RuntimeError("Native-grid identity diagnostic did not pass")
        if sha256(DATASET) != first["dataset_sha256"] or not INDEX.is_file():
            raise RuntimeError("Preserved 1000 h dataset/index changed")
        verify_frozen(json.loads((FIRST_ATTEMPT / "preserved_inputs.json").read_text()))
    protected = (STATE, LOG, PID, SCRATCH)
    if not NATIVE_GRID:
        protected += (DATASET, INDEX)
    if any(path.exists() for path in protected):
        raise RuntimeError("Launch records, data or scratch already exist; never duplicate")
    if active_science():
        raise RuntimeError("Scientific workers already active; preserve them")
    CAMPAIGN.mkdir(parents=True, exist_ok=True)
    (CAMPAIGN / "launch.lock").mkdir()
    snapshot = frozen_inputs()
    if NATIVE_GRID:
        for name in ("campaign_state.json", "resolved_configuration.json",
                     "native_grid_diagnostic.json", "preserved_inputs.json", "preflight.log"):
            path = FIRST_ATTEMPT / name
            snapshot[str(path.relative_to(ROOT))] = sha256(path)
        snapshot[str(DATASET.relative_to(ROOT))] = sha256(DATASET)
    (CAMPAIGN / "preserved_inputs.json").write_text(
        json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    record({"status": "STARTING", "run_id": "A3_1000h_full", "scenario": "A3",
            "hours": 1000, "integration_days": 1000 / 24, "authorized_runs": 1,
            "mpi_ranks": 6, "n_live": 800, "acceptance": "PENDING",
            "scratch": str(SCRATCH), "physical_model_changed": False,
            "numerical_grid_changed": NATIVE_GRID,
            "native_grid_um": [3.0, 20.0] if NATIVE_GRID else [3.8, 19.0],
            "first_attempt": str(FIRST_ATTEMPT.relative_to(ROOT)) if NATIVE_GRID else None,
            "launcher_sha256": sha256(Path(__file__))})
    with LOG.open("x", encoding="utf-8") as stream:
        worker_flag = "--native-grid-worker" if NATIVE_GRID else "--worker"
        process = subprocess.Popen([str(PREFIX / "bin/python"), "-u", __file__, worker_flag],
                                   cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                                   stdin=subprocess.DEVNULL, start_new_session=True)
    PID.write_text(str(process.pid) + "\n", encoding="utf-8")
    time.sleep(2)
    if process.poll() is not None:
        raise RuntimeError(f"Supervisor exited {process.returncode}; inspect {LOG}")
    print(json.dumps({"supervisor_pid": process.pid, "state": str(STATE), "log": str(LOG)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--launch", action="store_true")
    actions.add_argument("--worker", action="store_true")
    actions.add_argument("--launch-native-grid-retry", action="store_true")
    actions.add_argument("--native-grid-worker", action="store_true")
    options = parser.parse_args()
    if options.launch_native_grid_retry or options.native_grid_worker:
        select_native_grid_retry()
    worker() if options.worker or options.native_grid_worker else launch()
