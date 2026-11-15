"""One user-authorized MPI3-to-MPI5 checkpoint migration of three variants.

Freeze the exact supervisor tree, validate and back up every raw checkpoint,
then stop only verified PID identities and resume the same three basenames.
Any pre-stop validation failure unfreezes the original workers.
"""

import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time

import numpy as np
import run_proxima_a0_a3_1000h as original

CAMPAIGN = original.CAMPAIGN
RECOVERY = CAMPAIGN / "recovery_20261013_MPI5_R1"


def identity(pid):
    stat = Path(f"/proc/{pid}/stat").read_text()
    rest = stat[stat.rindex(")") + 2:].split()
    return {"pid": pid, "ppid": int(rest[1]), "start_ticks": rest[19],
            "command": Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode()}


def signal_exact(record, sig):
    current = identity(record["pid"])
    if current["start_ticks"] != record["start_ticks"] or current["command"] != record["command"]:
        raise RuntimeError("PID identity changed; refuse signaling")
    os.kill(record["pid"], sig)


def validate(case):
    config_file = CAMPAIGN / "resolved" / (case["variant"] + ".json")
    if original.full.sha256(config_file) != case["resolved_sha256"]:
        raise RuntimeError("Resolved configuration changed")
    config = json.loads(config_file.read_text())
    raw = Path(case["run_dir"]) / "POSEIDON_output/proxima_b_earthlike/retrievals/MultiNest_raw"
    prefix = str(raw / (config["model_name"] + "-"))
    counts = [int(x) for x in Path(prefix + "resume.dat").read_text().splitlines()[1].split()]
    if len(counts) != 4 or counts[3] != 800 or counts[0] <= 0:
        raise RuntimeError("Invalid resume counters")
    live = np.loadtxt(prefix + "live.points", ndmin=2)
    physical = np.loadtxt(prefix + "phys_live.points", ndmin=2)
    events = np.loadtxt(prefix + "ev.dat", ndmin=2)
    if live.shape != (800, 16) or physical.shape != (800, 17):
        raise RuntimeError("Invalid live-point shapes")
    if events.shape[0] < counts[0] - 800 or events.shape[1] < 16:
        raise RuntimeError("Invalid event table")
    if not all(np.isfinite(x).all() for x in (live, physical, events)):
        raise RuntimeError("Nonfinite checkpoint")
    if np.any(live[:, :15] < 0) or np.any(live[:, :15] > 1):
        raise RuntimeError("Unit cube invalid")
    np.testing.assert_array_equal(live[:, 15], physical[:, 15])
    for col, name in enumerate(config["parameters"]):
        low, high = config["prior_ranges"][name]
        if np.any(physical[:, col] < low - 1e-12) or np.any(physical[:, col] > high + 1e-12):
            raise RuntimeError("Live points outside prior: " + name)
        if low == high:
            np.testing.assert_allclose(physical[:, col], low, rtol=0, atol=0)
    hashes = {p.name: original.full.sha256(p) for p in raw.iterdir() if p.is_file()}
    return {"variant": case["variant"], "raw": str(raw), "hashes": hashes,
            "replacements": counts[0], "evaluations": counts[1],
            "finite_priors_fixed_values": "PASS", "event_shape": list(events.shape)}


def rebalance():
    if RECOVERY.exists():
        raise RuntimeError("Recovery already exists; never duplicate")
    state = json.loads(original.STATE.read_text())
    if state["status"] != "RUNNING" or len(state["cases"]) != 3:
        raise RuntimeError("Unexpected campaign state")
    if any(c["status"] != "running" or c["mpi_ranks"] != 3 for c in state["cases"]):
        raise RuntimeError("All three must still be active MPI3")
    host = original.check_host()
    if host["rank_total"] != 9 or host["available_gib"] < 12:
        raise RuntimeError("Require only the three MPI3 jobs and 12 GiB headroom")
    snapshot = json.loads((CAMPAIGN / "preserved_inputs.json").read_text())
    original.full.verify_frozen(snapshot)
    full_state = json.loads(original.full.STATE.read_text())
    if full_state["status"] != "COMPLETE_PENDING_VALIDATION" or full_state["exit_code"] != 0:
        raise RuntimeError("Full must be closed; preserve it")
    supervisor = identity(state["supervisor_pid"])
    if "run_proxima_a0_a3_1000h.py --worker" not in supervisor["command"]:
        raise RuntimeError("Supervisor identity mismatch")
    records = {supervisor["pid"]: supervisor}
    candidates = []
    for path in Path("/proc").iterdir():
        if path.name.isdigit():
            try:
                candidates.append(identity(int(path.name)))
            except (FileNotFoundError, ProcessLookupError, PermissionError):
                pass
    while True:
        new = [r for r in candidates if r["ppid"] in records and r["pid"] not in records]
        if not new:
            break
        records.update({r["pid"]: r for r in new})
    for case in state["cases"]:
        mpi = records.get(case["pid"])
        if not mpi or "/bin/mpiexec -n 3 " not in mpi["command"] or case["run_dir"] not in mpi["command"]:
            raise RuntimeError("MPI identity mismatch")
        ranks = [r for r in records.values() if "run_life_retrieval.py" in r["command"]
                 and "/bin/mpiexec" not in r["command"] and case["run_dir"] in r["command"]]
        if len(ranks) != 3:
            raise RuntimeError("Expected exactly three ranks per old job")
    RECOVERY.mkdir()
    original.atomic_json(RECOVERY / "before_state.json", state)
    shutil.copy2(CAMPAIGN / "manifest.csv", RECOVERY / "before_manifest.csv")
    original.atomic_json(RECOVERY / "old_process_identities.json", list(records.values()))
    stopped = []
    try:
        # Stop the supervisor first, preventing launch/postprocess races.
        for record in records.values():
            signal_exact(record, signal.SIGSTOP)
            stopped.append(record)
        time.sleep(1)
        reports = [validate(case) for case in state["cases"]]
        for report in reports:
            backup = RECOVERY / "checkpoint_backup" / report["variant"]
            shutil.copytree(report["raw"], backup)
            for name, expected in report["hashes"].items():
                if original.full.sha256(backup / name) != expected:
                    raise RuntimeError("Backup hash mismatch")
        original.full.verify_frozen(snapshot)
        # Freeze completed full products separately, without altering them.
        protected = dict(snapshot)
        for path in [original.full.STATE, *sorted((original.full.CAMPAIGN / "products").rglob("*"))]:
            if path.is_file():
                protected[str(path.relative_to(original.ROOT))] = original.full.sha256(path)
        original.atomic_json(RECOVERY / "protected_inputs.json", protected)
        original.atomic_json(RECOVERY / "checkpoint_validation.json", {
            "utc": original.now(), "all_pass": True, "reports": reports,
            "old_ranks": 3, "new_ranks": 5, "host": host,
            "supporting_source": "https://xpsi-group.github.io/xpsi/Example_job.html"})
    except Exception:
        for record in reversed(stopped):
            signal_exact(record, signal.SIGCONT)
        original.atomic_json(RECOVERY / "aborted.json", {"status": "VALIDATION_FAILED_ORIGINAL_UNFROZEN"})
        raise
    # Checkpoints and backups are now immutable and validated. Discard only
    # unpersisted computation in this precisely identified, authorized tree.
    for record in records.values():
        signal_exact(record, signal.SIGKILL)
    time.sleep(2)
    for report, case in zip(reports, state["cases"]):
        case.update(status="pending_resume", previous_pid=case["pid"], mpi_ranks=5,
                    checkpoint_evaluations=report["evaluations"],
                    checkpoint_replacements=report["replacements"], recovery=RECOVERY.name)
        args = list(case["command"])
        args[args.index("-n") + 1] = "5"
        args.append("--resume")
        case["recovery_command"] = args
    state.update(status="RESUMING", recovery=RECOVERY.name,
                 authorization="Explicit user request to stop and resume all three with five ranks",
                 migration_utc=original.now())
    original.save(state)
    with (RECOVERY / "supervisor.log").open("x") as stream:
        process = subprocess.Popen([str(original.full.PREFIX / "bin/python"), "-u", __file__, "--worker"],
                                   cwd=original.ROOT, stdout=stream, stderr=subprocess.STDOUT,
                                   stdin=subprocess.DEVNULL, start_new_session=True)
    (RECOVERY / "supervisor.pid").write_text(str(process.pid) + "\n")
    print(json.dumps({"supervisor_pid": process.pid, "reports": reports}), flush=True)


def worker():
    state = json.loads(original.STATE.read_text())
    protected = json.loads((RECOVERY / "protected_inputs.json").read_text())
    processes, streams = {}, {}
    try:
        output = subprocess.check_output(["ps", "-eo", "args="], text=True)
        if "/bin/mpiexec" in output or "run_life_retrieval.py --campaign" in output:
            raise RuntimeError("Old or unrelated workers remain; do not duplicate")
        original.full.verify_frozen(protected)
        for case in state["cases"]:
            report = validate(case)
            if report["evaluations"] != case["checkpoint_evaluations"]:
                raise RuntimeError("Checkpoint changed before recovery")
            log = RECOVERY / (case["variant"] + ".log")
            stream = log.open("x")
            process = subprocess.Popen(original.full.environment_command(case["recovery_command"]),
                                       cwd=original.ROOT, stdout=stream, stderr=subprocess.STDOUT,
                                       stdin=subprocess.DEVNULL, start_new_session=True)
            processes[case["variant"]] = process
            streams[case["variant"]] = stream
            case.update(status="running", pid=process.pid, launch_log=str(log), resume_utc=original.now())
            state.update(status="RUNNING", supervisor_pid=os.getpid())
            original.save(state)
        while processes:
            for case in state["cases"]:
                key = case["variant"]
                if key in processes and processes[key].poll() is not None:
                    rc = processes.pop(key).returncode
                    streams.pop(key).close()
                    case.update(return_code=rc, end_utc=original.now())
                    if rc == 0:
                        shutil.copytree(case["run_dir"], case["archive_dir"])
                        case.update(status="complete_pending_validation", acceptance="PENDING")
                    else:
                        case["status"] = "failed"
                        state["failure"] = f"{key}: resumed retrieval exit {rc}"
            original.save(state)
            time.sleep(15)
        original.full.verify_frozen(protected)
        state["status"] = "FAILED_PRESERVED" if state.get("failure") else "COMPLETE_PENDING_VALIDATION"
        original.save(state)
    except Exception as error:
        state.update(status="ACTION_REQUIRED", error=f"{type(error).__name__}: {error}")
        original.save(state)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--rebalance", action="store_true")
    actions.add_argument("--worker", action="store_true")
    options = parser.parse_args()
    worker() if options.worker else rebalance()
