"""Fresh single MPI15 retrieval; immutable baseline, resource gate, archive."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

import run_proxima_a3_1000h as base

ROOT, PROJECT, PREFIX, SCRIPTS = base.ROOT, base.PROJECT, base.PREFIX, base.SCRIPTS
CAMPAIGN = PROJECT / "retrievals/a3_1000h_binning_corrected_20261014"
SCRATCH = Path("/home/dasan/exofarm_a3_1000h_binning_20261014")
STATE = CAMPAIGN / "campaign_state.json"
LOG = CAMPAIGN.parent / "a3_1000h_binning_corrected_20261014.supervisor.log"
PID = LOG.with_suffix(".pid")
OLD = PROJECT / "retrievals/a3_1000h_full_20261011/native_grid_retry"
RUNNER = SCRIPTS / "run_life_retrieval_binning_corrected.py"
TAG = "_O2_fixedBlack1bar_noxtol_MPI15_BIN1"


def record(state):
    base.STATE = STATE
    base.record(state)


def active_science():
    lines = subprocess.check_output(["ps", "-eo", "pid,args"], text=True).splitlines()
    return [line for line in lines if any(token in line for token in
            ("/bin/mpiexec", "run_life_retrieval.py", "run_life_retrieval_binning_corrected.py",
             "vulcan.py", "lpjml "))]


def arguments():
    return ["--operator-record", str(CAMPAIGN / "operator_preflight.json"),
            "--campaign", "proxima", "--scenario", "A3", "--hours", "1000",
            "--n-live", "800", "--error-inflation", "none",
            "--surface-pressure-mode", "fixed-black", "--include-o2",
            "--x-profile", "isochem", "--output-tag", TAG, "--R", "10000",
            "--wl-min", "3.0", "--wl-max", "20.0",
            "--dataset-file", str(base.DATASET.relative_to(ROOT))]


def worker():
    state = json.loads(STATE.read_text())
    try:
        state.update(status="PREFLIGHT", supervisor_pid=os.getpid())
        record(state)
        snapshot = json.loads((CAMPAIGN / "preserved_inputs.json").read_text())
        base.verify_frozen(snapshot)
        base.CAMPAIGN = CAMPAIGN
        base.run_stage(["/usr/bin/time", "-v", PREFIX / "bin/python", "-u", RUNNER,
                        *arguments(), "--run-dir", SCRATCH / "preflight",
                        "--configuration-json", CAMPAIGN / "resolved_configuration.json",
                        "--setup-only", "--validate-forward"], "preflight.log")
        resolved = json.loads((CAMPAIGN / "resolved_configuration.json").read_text())
        reference = json.loads((OLD / "resolved_configuration.json").read_text())
        differences = {key: [reference.get(key), value] for key, value in resolved.items()
                       if key != "model_name" and value != reference.get(key)}
        if differences:
            raise ValueError(f"Baseline configuration differs: {differences}")
        if (resolved["declared_dimension"], resolved["effective_free_dimension"]) != (15, 14):
            raise ValueError("Expected 15 declared / 14 free coordinates")
        preflight = json.loads((CAMPAIGN / "operator_preflight.json").read_text())
        if preflight["status"] != "PASS":
            raise RuntimeError("Operator preflight failed")
        measured, = re.findall(r"Maximum resident set size \(kbytes\):\s*(\d+)",
                               (CAMPAIGN / "preflight.log").read_text())
        available = int(re.search(r"MemAvailable:\s*(\d+)", Path("/proc/meminfo").read_text())[1])
        needed = 15 * int(measured) + 4 * 1024 ** 2
        resources = {"logical_cpus": os.cpu_count(), "preflight_peak_RSS_KiB": int(measured),
                     "MemAvailable_KiB": available, "required_KiB": needed,
                     "mpi_ranks": 15, "threads_per_rank": 1}
        (CAMPAIGN / "resource_gate.json").write_text(json.dumps(resources, indent=2) + "\n")
        if os.cpu_count() < 15 or available < needed:
            raise RuntimeError(f"MPI15 resource gate failed: {resources}")
        base.verify_frozen(snapshot)
        if active_science():
            raise RuntimeError("Other science workers appeared; preserve all")
        state.update(status="RUNNING", preflight="PASS", baseline_configuration="IDENTICAL",
                     resources=resources)
        with (CAMPAIGN / "retrieval.log").open("x") as stream:
            process = subprocess.Popen(base.environment_command([
                PREFIX / "bin/mpiexec", "-n", "15", PREFIX / "bin/python", "-u", RUNNER,
                *arguments(), "--run-dir", SCRATCH / "run"]), cwd=SCRIPTS,
                stdout=stream, stderr=subprocess.STDOUT)
            state["mpiexec_pid"] = process.pid
            record(state)
            state["exit_code"] = process.wait()
        if state["exit_code"] != 0:
            raise RuntimeError(f"Retrieval exit {state['exit_code']}; all products preserved")
        source = SCRATCH / "run/POSEIDON_output/proxima_b_earthlike/retrievals"
        for folder in ("MultiNest_raw", "results", "samples"):
            if not (source / folder).is_dir():
                raise RuntimeError(f"Missing {source / folder}")
        shutil.copytree(source, CAMPAIGN / "products")
        base.verify_frozen(snapshot)
        state.update(status="COMPLETE_PENDING_VALIDATION", acceptance="PENDING",
                     products="products", comparison="PENDING", scratch_preserved=True)
        record(state)
        base.run_stage([PREFIX / "bin/python", "-u",
                        SCRIPTS / "compare_proxima_a3_binning_retrievals.py"], "comparison.log")
        state.update(comparison="SAVED", acceptance="PENDING_INDEPENDENT_REVIEW")
        record(state)
    except Exception as error:
        state.update(status="FAILED", error=f"{type(error).__name__}: {error}",
                     scratch_preserved=True)
        record(state)
        raise


def launch():
    if sys.platform != "linux":
        raise RuntimeError("Ubuntu launch only")
    if any(path.exists() for path in (STATE, LOG, PID, SCRATCH)):
        raise RuntimeError("Existing launch records or scratch; refuse duplicate")
    if active_science():
        raise RuntimeError("Science workers active; preserve them")
    if base.sha256(base.DATASET) != "5611c5904ef03aa02586bed15f14c0c2560ac5ae6fa9463ef420229311db75fa":
        raise ValueError("Dataset changed")
    base.validate_dataset()
    CAMPAIGN.mkdir(parents=True, exist_ok=True)
    (CAMPAIGN / "launch.lock").mkdir()
    snapshot = base.frozen_inputs()
    paths = [base.DATASET, OLD / "resolved_configuration.json", RUNNER, Path(__file__),
             SCRIPTS / "life_bin_operator_diagnostic.py",
             SCRIPTS / "compare_proxima_a3_binning_retrievals.py"]
    paths += [path for path in (OLD / "products").rglob("*") if path.is_file()]
    snapshot.update({str(path.relative_to(ROOT)): base.sha256(path) for path in paths})
    (CAMPAIGN / "preserved_inputs.json").write_text(json.dumps(snapshot, indent=2) + "\n")
    (CAMPAIGN / "manifest.csv").write_text(
        "run_id,scenario,hours,model,mpi_ranks,n_live,dataset_sha256\n"
        f"A3_1000h_full_BIN1,A3,1000,full,15,800,{base.sha256(base.DATASET)}\n")
    record({"status": "STARTING", "authorized_runs": 1, "scenario": "A3", "hours": 1000,
            "mpi_ranks": 15, "n_live": 800, "acceptance": "PENDING", "scratch": str(SCRATCH),
            "model_name": "proxima_A3_1000h" + TAG, "scientific_change": "binning only",
            "checkpoint_reuse": False, "baseline": str(OLD.relative_to(ROOT))})
    with LOG.open("x") as stream:
        process = subprocess.Popen([str(PREFIX / "bin/python"), "-u", __file__, "--worker"],
                                   cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                                   stdin=subprocess.DEVNULL, start_new_session=True)
    PID.write_text(str(process.pid) + "\n")
    time.sleep(2)
    if process.poll() is not None:
        raise RuntimeError(f"Supervisor exit {process.returncode}; inspect {LOG}")
    print(json.dumps({"supervisor_pid": process.pid, "state": str(STATE), "log": str(LOG)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--launch", action="store_true")
    actions.add_argument("--worker", action="store_true")
    options = parser.parse_args()
    worker() if options.worker else launch()
