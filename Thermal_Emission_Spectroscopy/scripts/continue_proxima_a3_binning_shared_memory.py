"""Continue the pre-sampling gate using measured MPI shared physical memory.

The initial conservative RSS-times-ranks gate double-counted shared opacities.
Preserve that failed record; test MPI15 with truth forwards and no sampling,
then require measured physical PSS plus sampling reserve to fit available RAM.
"""

import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import time

import launch_proxima_a3_binning_corrected as campaign

ROOT, PREFIX, CAMPAIGN = campaign.ROOT, campaign.PREFIX, campaign.CAMPAIGN
LOG = campaign.LOG.with_name("a3_1000h_binning_corrected_20261014.sharedmemory.supervisor.log")
PID = LOG.with_suffix(".pid")


def available_kib():
    return int(next(line.split()[1] for line in Path("/proc/meminfo").read_text().splitlines()
                    if line.startswith("MemAvailable:")))


def descendants_pss(parent):
    """Sum proportional set sizes; shared pages count once across MPI ranks."""
    tree = {}
    for folder in Path("/proc").iterdir():
        if not folder.name.isdigit():
            continue
        try:
            lines = (folder / "status").read_text().splitlines()
            ppid = int(next(line.split()[1] for line in lines if line.startswith("PPid:")))
            tree[int(folder.name)] = ppid
        except (OSError, StopIteration):
            continue
    selected = {parent}
    while True:
        added = {pid for pid, ppid in tree.items() if ppid in selected} - selected
        if not added:
            break
        selected |= added
    total = 0
    for pid in selected:
        try:
            lines = Path(f"/proc/{pid}/smaps_rollup").read_text().splitlines()
            total += int(next(line.split()[1] for line in lines if line.startswith("Pss:")))
        except (OSError, StopIteration):
            continue
    return total


def probe():
    # Execute the exact authorized wrapper/forward under MPI15, no MultiNest.
    import sys
    import run_life_retrieval_binning_corrected as wrapper
    arguments = campaign.arguments()
    arguments[arguments.index("--operator-record") + 1] = str(CAMPAIGN / "operator_MPI15_preflight.json")
    sys.argv = [__file__, *arguments, "--run-dir", str(campaign.SCRATCH / "mpi15_preflight"),
                "--setup-only", "--validate-forward"]
    wrapper.main()


def worker():
    state = json.loads(campaign.STATE.read_text())
    try:
        state.update(status="MPI15_MEMORY_PREFLIGHT", supervisor_pid=os.getpid(),
                     prior_gate_error=state.pop("error", None))
        campaign.record(state)
        snapshot = json.loads((CAMPAIGN / "preserved_inputs.json").read_text())
        campaign.base.verify_frozen(snapshot)
        capacity = available_kib()
        peak, minimum_available = 0, capacity
        with (CAMPAIGN / "mpi15_memory_preflight.log").open("x") as stream:
            child = subprocess.Popen(campaign.base.environment_command([
                PREFIX / "bin/mpiexec", "-n", "15", PREFIX / "bin/python", "-u",
                Path(__file__), "--probe"]), cwd=campaign.SCRIPTS,
                stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
            state["memory_probe_mpiexec_pid"] = child.pid
            campaign.record(state)
            while child.poll() is None:
                peak = max(peak, descendants_pss(child.pid))
                minimum_available = min(minimum_available, available_kib())
                if available_kib() < 4 * 1024 ** 2:
                    # Stop this setup-only diagnostic before memory exhaustion;
                    # it contains no sampler/checkpoint and runs in its own group.
                    os.killpg(child.pid, signal.SIGTERM)
                    child.wait()
                    raise RuntimeError("MPI15 setup-only probe stopped: less than 4 GiB available")
                time.sleep(2)
            if child.returncode != 0:
                raise RuntimeError(f"MPI15 setup-only preflight exit {child.returncode}")
        preflight = json.loads((CAMPAIGN / "operator_MPI15_preflight.json").read_text())
        if preflight["status"] != "PASS":
            raise RuntimeError("MPI15 forward preflight did not pass")
        # Reserve 0.5 GiB per rank for sampling work arrays above the measured
        # simultaneous truth-forward peak, plus 4 GiB for OS/headroom.
        reserve = int((15 * .5 + 4) * 1024 ** 2)
        gate = {"status": "PASS" if peak + reserve < available_kib() else "FAIL",
                "mpi_ranks": 15, "logical_cpus": os.cpu_count(),
                "aggregate_peak_PSS_KiB": peak, "minimum_MemAvailable_KiB": minimum_available,
                "MemAvailable_after_probe_KiB": available_kib(), "reserve_KiB": reserve,
                "method": "sum of proportional set sizes, shared pages counted once",
                "shared_source": "POSEIDON absorption.py:735-740, node_rank==0 loader; utility.py:315-344",
                "initial_RSS_gate": "preserved; overcounted shared/loader memory"}
        (CAMPAIGN / "resource_gate_shared_memory.json").write_text(json.dumps(gate, indent=2) + "\n")
        if gate["status"] != "PASS" or os.cpu_count() < 15:
            raise RuntimeError(f"Measured MPI15 resource gate failed: {gate}")
        if campaign.active_science():
            raise RuntimeError("Other scientific workers appeared")
        campaign.base.verify_frozen(snapshot)
        state.update(status="RUNNING", preflight="PASS_MPI15", baseline_configuration="IDENTICAL",
                     resources_shared=gate)
        with (CAMPAIGN / "retrieval.log").open("x") as stream:
            child = subprocess.Popen(campaign.base.environment_command([
                PREFIX / "bin/mpiexec", "-n", "15", PREFIX / "bin/python", "-u", campaign.RUNNER,
                *campaign.arguments(), "--run-dir", campaign.SCRATCH / "run"]),
                cwd=campaign.SCRIPTS, stdout=stream, stderr=subprocess.STDOUT)
            state["mpiexec_pid"] = child.pid
            campaign.record(state)
            state["exit_code"] = child.wait()
        if state["exit_code"] != 0:
            raise RuntimeError(f"Retrieval exit {state['exit_code']}; all products preserved")
        import shutil
        source = campaign.SCRATCH / "run/POSEIDON_output/proxima_b_earthlike/retrievals"
        for folder in ("MultiNest_raw", "results", "samples"):
            if not (source / folder).is_dir():
                raise RuntimeError(f"Missing {source / folder}")
        shutil.copytree(source, CAMPAIGN / "products")
        campaign.base.verify_frozen(snapshot)
        state.update(status="COMPLETE_PENDING_VALIDATION", acceptance="PENDING",
                     products="products", comparison="PENDING", scratch_preserved=True)
        campaign.record(state)
        campaign.base.CAMPAIGN = CAMPAIGN
        campaign.base.run_stage([PREFIX / "bin/python", "-u",
                                campaign.SCRIPTS / "compare_proxima_a3_binning_retrievals.py"],
                               "comparison.log")
        state.update(comparison="SAVED", acceptance="PENDING_INDEPENDENT_REVIEW")
        campaign.record(state)
    except Exception as error:
        state.update(status="FAILED", error=f"{type(error).__name__}: {error}", scratch_preserved=True)
        campaign.record(state)
        raise


def launch():
    state = json.loads(campaign.STATE.read_text())
    if (state["status"] != "FAILED" or "resource gate failed" not in state.get("error", "")
            or (CAMPAIGN / "retrieval.log").exists() or campaign.active_science()):
        raise RuntimeError("Only the stopped pre-sampling memory gate may continue")
    if LOG.exists() or PID.exists():
        raise RuntimeError("Continuation already exists; refuse duplicate")
    import shutil
    shutil.copy2(campaign.STATE, CAMPAIGN / "initial_RSS_gate_failed_state.json")
    (CAMPAIGN / "shared_memory_continuation.json").write_text(json.dumps({
        "source_sha256": campaign.base.sha256(Path(__file__)),
        "sampling_started_before_continuation": False,
        "physical_model_and_operator_changed": False, "ranks": 15}, indent=2) + "\n")
    with LOG.open("x") as stream:
        child = subprocess.Popen([str(PREFIX / "bin/python"), "-u", __file__, "--worker"],
                                 cwd=ROOT, stdin=subprocess.DEVNULL, stdout=stream,
                                 stderr=subprocess.STDOUT, start_new_session=True)
    PID.write_text(str(child.pid) + "\n")
    print(json.dumps({"supervisor_pid": child.pid, "log": str(LOG)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--launch", action="store_true")
    actions.add_argument("--worker", action="store_true")
    actions.add_argument("--probe", action="store_true")
    options = parser.parse_args()
    if options.probe:
        probe()
    elif options.worker:
        worker()
    else:
        launch()
