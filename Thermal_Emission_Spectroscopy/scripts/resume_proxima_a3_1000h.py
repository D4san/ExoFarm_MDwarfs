"""Resume the user-authorized A3-1000 h native-grid checkpoint once.

Preserve the interrupted state, logs and raw files before writing to the same
MultiNest basename. Never generate data, change priors, or start from zero.
"""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

import run_proxima_a3_1000h as original

original.select_native_grid_retry()
CAMPAIGN = original.CAMPAIGN
RECOVERY = CAMPAIGN / "recovery_20261012_R1"
SOURCE = original.SCRATCH / "run/POSEIDON_output/proxima_b_earthlike/retrievals"
RAW = SOURCE / "MultiNest_raw"
SUPERVISOR_LOG = RECOVERY / "supervisor.log"
PID_FILE = RECOVERY / "supervisor.pid"


def validate_checkpoint():
    """Read-only structural, finite, prior, likelihood and provenance checks."""
    import numpy as np

    if sys.platform != "linux":
        raise RuntimeError("Resume only in the verified Ubuntu environment")
    if original.active_science():
        raise RuntimeError("Scientific processes active: do not duplicate")
    state = json.loads(original.STATE.read_text())
    if state["status"] not in ("RUNNING", "INTERRUPTED"):
        raise RuntimeError(f"Unexpected interrupted state: {state['status']}")
    if (CAMPAIGN / "products").exists() or state.get("exit_code") == 0:
        raise RuntimeError("Closed products exist: do not resume sampling")
    snapshot = json.loads((CAMPAIGN / "preserved_inputs.json").read_text())
    original.verify_frozen(snapshot)
    if original.sha256(original.DATASET) != state["dataset_sha256"]:
        raise RuntimeError("Dataset hash differs from the interrupted run")
    original.validate_dataset()
    configuration = json.loads((CAMPAIGN / "resolved_configuration.json").read_text())
    if (configuration["declared_dimension"] != 15
            or configuration["effective_free_dimension"] != 14
            or configuration["n_live"] != 800
            or [configuration["wl_min"], configuration["wl_max"]] != [3.0, 20.0]
            or configuration["R"] != 10000
            or configuration["dataset_sha256"] != state["dataset_sha256"]):
        raise RuntimeError("Resolved configuration inconsistent with authorized run")
    prefix = RAW / (configuration["model_name"] + "-")

    def product(suffix):
        return Path(str(prefix) + suffix)

    resume_lines = product("resume.dat").read_text().splitlines()
    counters = [int(value) for value in resume_lines[1].split()]
    if len(counters) != 4 or counters[3] != 800 or counters[0] <= 0:
        raise RuntimeError("Invalid resume counters or live-point count")
    replacements, evaluations = counters[:2]
    live = np.loadtxt(product("live.points"), ndmin=2)
    physical = np.loadtxt(product("phys_live.points"), ndmin=2)
    events = np.loadtxt(product("ev.dat"), ndmin=2)
    if live.shape != (800, 16) or physical.shape != (800, 17):
        raise RuntimeError(f"Unexpected live-point shapes: {live.shape}, {physical.shape}")
    for name, values in (("live", live), ("physical", physical), ("events", events)):
        if not np.isfinite(values).all():
            raise RuntimeError(f"Nonfinite checkpoint values: {name}")
    if np.any(live[:, :15] < 0) or np.any(live[:, :15] > 1):
        raise RuntimeError("Unit-cube live points lie outside [0,1]")
    np.testing.assert_allclose(live[:, 15], physical[:, 15], rtol=0, atol=0)
    for column, name in enumerate(configuration["parameters"]):
        low, high = configuration["prior_ranges"][name]
        values = physical[:, column]
        if np.any(values < low - 1e-12) or np.any(values > high + 1e-12):
            raise RuntimeError(f"Checkpoint parameter outside recorded prior: {name}")
        if low == high:
            np.testing.assert_allclose(values, low, rtol=0, atol=0)
    if events.shape[0] < replacements - 800 or events.shape[1] < 16:
        raise RuntimeError(f"Insufficient checkpoint event table: {events.shape}")
    files = sorted(RAW.glob(configuration["model_name"] + "-*"))
    hashes = {path.name: original.sha256(path) for path in files if path.is_file()}
    return {
        "validated_utc": datetime.now(timezone.utc).isoformat(), "result": "PASS",
        "replacements": replacements, "evaluations": evaluations,
        "live_shape": list(live.shape), "physical_shape": list(physical.shape),
        "event_shape": list(events.shape), "finite": True,
        "live_likelihoods_identical": True, "priors_and_fixed_surface": "PASS",
        "preserved_inputs": len(snapshot), "dataset_sha256": state["dataset_sha256"],
        "configuration_sha256": original.sha256(CAMPAIGN / "resolved_configuration.json"),
        "runner_sha256": original.sha256(original.SCRIPTS / "run_life_retrieval.py"),
        "raw_hashes": hashes, "checkpoint_directory": str(RAW),
    }


def launch():
    if RECOVERY.exists():
        raise RuntimeError("Recovery records already exist: never duplicate R1")
    report = validate_checkpoint()
    RECOVERY.mkdir()  # Atomic single-launch guard, preserved after completion/failure.
    try:
        shutil.copytree(RAW, RECOVERY / "checkpoint_backup")
        for name, expected in report["raw_hashes"].items():
            if original.sha256(RECOVERY / "checkpoint_backup" / name) != expected:
                raise RuntimeError(f"Backup hash mismatch: {name}")
        for name in ("campaign_state.json", "resolved_configuration.json",
                     "retrieval.log", "manifest.csv", "preflight.log"):
            shutil.copy2(CAMPAIGN / name, RECOVERY / ("interrupted_" + name))
        (RECOVERY / "checkpoint_validation.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8")
        state = json.loads(original.STATE.read_text())
        state.update(status="RESUMING", acceptance="PENDING",
                     interruption_observed_utc=report["validated_utc"],
                     interruption_cause="Not confirmed; prior workers absent",
                     resume_from_evaluations=report["evaluations"],
                     resume_from_replacements=report["replacements"],
                     recovery=str(RECOVERY.relative_to(CAMPAIGN)))
        original.record(state)
        with SUPERVISOR_LOG.open("x", encoding="utf-8") as stream:
            process = subprocess.Popen(
                [str(original.PREFIX / "bin/python"), "-u", __file__, "--worker"],
                cwd=original.ROOT, stdout=stream, stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL, start_new_session=True,
            )
        PID_FILE.write_text(str(process.pid) + "\n", encoding="utf-8")
        time.sleep(2)
        if process.poll() is not None:
            raise RuntimeError(f"Recovery supervisor exited {process.returncode}")
        print(json.dumps({"supervisor_pid": process.pid, "state": str(original.STATE),
                          "resume_from_evaluations": report["evaluations"],
                          "recovery": str(RECOVERY)}), flush=True)
    except Exception as error:
        state = json.loads(original.STATE.read_text())
        state.update(status="RESUME_FAILED", error=f"{type(error).__name__}: {error}")
        original.record(state)
        raise


def worker():
    state = json.loads(original.STATE.read_text())
    try:
        if original.active_science():
            raise RuntimeError("Another scientific worker appeared before resume")
        report = json.loads((RECOVERY / "checkpoint_validation.json").read_text())
        original.verify_frozen(json.loads((CAMPAIGN / "preserved_inputs.json").read_text()))
        if original.sha256(CAMPAIGN / "resolved_configuration.json") != report["configuration_sha256"]:
            raise RuntimeError("Configuration changed after validation")
        for name, expected in report["raw_hashes"].items():
            if original.sha256(RAW / name) != expected:
                raise RuntimeError(f"Checkpoint changed before sampling: {name}")
        arguments = [original.PREFIX / "bin/mpiexec", "-n", "6",
                     original.PREFIX / "bin/python", "-u",
                     original.SCRIPTS / "run_life_retrieval.py",
                     *original.common_arguments(), "--run-dir", original.SCRATCH / "run",
                     "--configuration-json", CAMPAIGN / "resolved_configuration.json",
                     "--resume"]
        (RECOVERY / "command.json").write_text(
            json.dumps([str(value) for value in arguments], indent=2) + "\n", encoding="utf-8")
        with (RECOVERY / "retrieval.log").open("x", encoding="utf-8") as stream:
            process = subprocess.Popen(original.environment_command(arguments),
                                       cwd=original.SCRIPTS, stdout=stream,
                                       stderr=subprocess.STDOUT)
            state.update(status="RUNNING", supervisor_pid=os.getpid(),
                         mpiexec_pid=process.pid, resumed=True,
                         retrieval_log="recovery_20261012_R1/retrieval.log")
            original.record(state)
            exit_code = process.wait()
        state["exit_code"] = exit_code
        if exit_code != 0:
            raise RuntimeError(f"Resumed retrieval exited {exit_code}; products preserved")
        for folder in ("MultiNest_raw", "results", "samples"):
            if not (SOURCE / folder).is_dir():
                raise RuntimeError(f"Missing final directory: {folder}")
        shutil.copytree(SOURCE, CAMPAIGN / "products")
        original.verify_frozen(json.loads((CAMPAIGN / "preserved_inputs.json").read_text()))
        state.update(status="COMPLETE_PENDING_VALIDATION", acceptance="PENDING",
                     products="products", scratch_preserved=True)
        original.record(state)
    except Exception as error:
        state.update(status="FAILED", error=f"{type(error).__name__}: {error}",
                     scratch_preserved=True)
        original.record(state)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--check-only", action="store_true")
    actions.add_argument("--launch", action="store_true")
    actions.add_argument("--worker", action="store_true")
    options = parser.parse_args()
    if options.check_only:
        print(json.dumps(validate_checkpoint(), indent=2), flush=True)
    elif options.launch:
        launch()
    else:
        worker()
