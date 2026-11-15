"""Run exactly three A0-fixed A3-1000h models beside the existing full model.

New models use MPI3; the untouched full model uses MPI6. The global budget
is 15 ranks on the verified 16-logical-CPU host. Never retry or overwrite.
"""

import argparse
import csv
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

import run_proxima_a3_1000h as full
from fixed_abundance_reference import load_fixed_abundances
from run_proxima_a0_reference_campaign import (
    VARIANTS, atomic_json, now, verify_matched_configuration,
)

full.select_native_grid_retry()
ROOT = full.ROOT
CAMPAIGN = full.PROJECT / "retrievals/a0_fixed_reference_A3_1000h_20261012"
SCRATCH = Path("/home/dasan/exofarm_a0ref_A3_1000h_20261012")
REFERENCE = full.PROJECT / "retrievals/a0_fixed_reference_20261010/a0_reference.json"
STATE = CAMPAIGN / "campaign_state.json"
RANKS = 3
BUDGET = 15


def check_host():
    """Allow only our existing full MPI6 and our new MPI3 workers."""
    output = subprocess.check_output(["ps", "-eo", "pid=,args="], text=True)
    mpi = []
    for line in output.splitlines():
        if "/bin/mpiexec" in line and "run_life_retrieval.py" in line:
            argv = line.split()
            ranks = int(argv[argv.index("-n") + 1])
            allowed_full = str(full.SCRATCH / "run") in argv and ranks == 6
            allowed_fixed = any(str(SCRATCH / "runs" / name) in argv
                                for name in VARIANTS) and ranks == RANKS
            if not (allowed_full or allowed_fixed):
                raise RuntimeError("Unrelated or unexpected MPI job: " + line)
            mpi.append(ranks)
        if "vulcan.py" in line or "lpjml " in line:
            raise RuntimeError("Other scientific workload: " + line)
    if sum(mpi) > BUDGET or len(mpi) > 4:
        raise RuntimeError("Global MPI budget exceeded")
    if len(os.sched_getaffinity(0)) < 16:
        raise RuntimeError("Expected at least 16 logical CPUs")
    memory = dict(line.split(":", 1) for line in
                  Path("/proc/meminfo").read_text().splitlines())
    available_kib = int(memory["MemAvailable"].split()[0])
    return {"mpi_ranks": mpi, "rank_total": sum(mpi),
            "available_gib": available_kib / 1024**2}


def arguments(variant, setup=False):
    args = full.common_arguments()
    # Execution topology changes, physical model and sampling settings do not.
    args[args.index("--output-tag") + 1] = "_A0ref_" + variant + "_1000NG"
    args += ["--a0-reference", str(CAMPAIGN / "a0_reference.json"),
             "--fix-a0-species", *VARIANTS[variant],
             "--run-dir", str(SCRATCH / ("preflight" if setup else "runs") / variant),
             "--configuration-json", str(CAMPAIGN / "resolved" / (variant + ".json"))]
    if setup:
        args += ["--setup-only"]
        return [full.PREFIX / "bin/python", "-u",
                full.SCRIPTS / "run_life_retrieval.py", *args]
    return [full.PREFIX / "bin/mpiexec", "-n", str(RANKS),
            full.PREFIX / "bin/python", "-u",
            full.SCRIPTS / "run_life_retrieval.py", *args]


def save(state):
    state["updated_utc"] = now()
    atomic_json(STATE, state)
    fields = ["run_id", "scenario", "hours", "variant", "status", "mpi_ranks",
              "effective_free_dimension", "pid", "return_code", "dataset_sha256",
              "run_dir", "archive_dir", "launch_log"]
    with (CAMPAIGN / "manifest.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(state["cases"])


def preflight(state, snapshot):
    baseline = json.loads((full.CAMPAIGN / "resolved_configuration.json").read_text())
    full.validate_dataset()
    for case in state["cases"]:
        variant = case["variant"]
        with (CAMPAIGN / "preflight" / (variant + ".log")).open("x") as stream:
            subprocess.run(full.environment_command(arguments(variant, setup=True)),
                           cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=True)
        resolved = json.loads((CAMPAIGN / "resolved" / (variant + ".json")).read_text())
        verify_matched_configuration(baseline, resolved, case)
        expected_fixed = {"log_P_surf", *("log_" + x for x in case["fixed_species"])}
        if set(resolved["fixed_parameters"]) != expected_fixed:
            raise ValueError("Unexpected fixed coordinates")
        if resolved["fixed_log10_abundances"] != case["fixed_log10_vmr"]:
            raise ValueError("Unexpected fixed VMR")
        case["preflight"] = "PASS"
        case["resolved_sha256"] = full.sha256(CAMPAIGN / "resolved" / (variant + ".json"))
        save(state)
        print("[preflight]", variant, "PASS", flush=True)
    full.verify_frozen(snapshot)
    atomic_json(CAMPAIGN / "preflight_validation.json", {
        "utc": now(), "all_pass": True, "dataset_sha256": baseline["dataset_sha256"],
        "same_opacities_priors_grid_except_fixed_abundances": True,
        "free_dimensions": [c["effective_free_dimension"] for c in state["cases"]],
        "cases": state["cases"], "host": check_host(),
    })


def worker():
    state = json.loads(STATE.read_text())
    snapshot = json.loads((CAMPAIGN / "preserved_inputs.json").read_text())
    processes, streams = {}, {}
    try:
        state.update(status="PREFLIGHT", supervisor_pid=os.getpid())
        save(state)
        preflight(state, snapshot)
        state["status"] = "RUNNING"
        failed = False
        while processes or any(c["status"] == "pending" for c in state["cases"]):
            for case in state["cases"]:
                key = case["variant"]
                if key in processes and processes[key].poll() is not None:
                    code = processes.pop(key).returncode
                    streams.pop(key).close()
                    case.update(return_code=code, end_utc=now())
                    if code:
                        case["status"] = "failed"
                        state["failure"] = f"{key}: retrieval exit {code}; {case['launch_log']}"
                        failed = True
                    else:
                        shutil.copytree(case["run_dir"], case["archive_dir"])
                        case.update(status="complete_pending_validation", acceptance="PENDING")
                    print("[exit]", key, code, flush=True)
            if not failed:
                for case in state["cases"]:
                    if case["status"] != "pending":
                        continue
                    host = check_host()
                    # Leave memory headroom for transient opacity loading and postprocess.
                    if host["rank_total"] + RANKS > BUDGET or host["available_gib"] < 8:
                        case["queue_reason"] = "Waiting for CPU/memory headroom"
                        break
                    full.verify_frozen(snapshot)
                    key = case["variant"]
                    config = CAMPAIGN / "resolved" / (key + ".json")
                    if full.sha256(config) != case["resolved_sha256"]:
                        raise RuntimeError("Resolved configuration changed")
                    if Path(case["run_dir"]).exists() or Path(case["archive_dir"]).exists():
                        raise RuntimeError("Existing scratch/archive; duplicate refused")
                    log = CAMPAIGN / "logs" / (key + ".log")
                    stream = log.open("x", encoding="utf-8")
                    process = subprocess.Popen(full.environment_command(arguments(key)),
                                               cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                                               stdin=subprocess.DEVNULL, start_new_session=True)
                    case.update(status="running", pid=process.pid, start_utc=now(),
                                launch_log=str(log))
                    processes[key], streams[key] = process, stream
                    save(state)
                    print("[launch]", key, process.pid, "MPI3", flush=True)
                    # Allow exec to become visible before checking the global process budget.
                    time.sleep(2)
            save(state)
            if failed and not processes:
                break
            time.sleep(15)
        full.verify_frozen(snapshot)
        state["status"] = "FAILED_PRESERVED" if failed else "COMPLETE_PENDING_VALIDATION"
        save(state)
    except Exception as error:
        state.update(status="ACTION_REQUIRED", error=f"{type(error).__name__}: {error}")
        save(state)
        # Existing full and newly started workers are left intact; no automatic retries.
        raise


def launch():
    if sys.platform != "linux":
        raise RuntimeError("Use the verified Ubuntu POSEIDON environment")
    if CAMPAIGN.exists() or SCRATCH.exists():
        raise RuntimeError("Existing campaign/scratch; duplicate refused")
    host = check_host()
    if host["available_gib"] < 12:
        raise RuntimeError("Less than 12 GiB free for launch; preserve active full")
    baseline = json.loads((full.CAMPAIGN / "resolved_configuration.json").read_text())
    if baseline["dataset_sha256"] != full.sha256(full.DATASET):
        raise ValueError("Dataset changed")
    fixed = load_fixed_abundances(REFERENCE, ["N2O", "NH3"], ROOT)
    CAMPAIGN.mkdir()
    for folder in ("preflight", "resolved", "logs", "runs"):
        (CAMPAIGN / folder).mkdir()
    shutil.copy2(REFERENCE, CAMPAIGN / "a0_reference.json")
    snapshot = json.loads((full.CAMPAIGN / "preserved_inputs.json").read_text())
    for path in (full.CAMPAIGN / "resolved_configuration.json", REFERENCE,
                 CAMPAIGN / "a0_reference.json", Path(__file__),
                 full.SCRIPTS / "fixed_abundance_reference.py",
                 full.SCRIPTS / "run_proxima_a0_reference_campaign.py"):
        snapshot[str(path.relative_to(ROOT))] = full.sha256(path)
    full.verify_frozen(snapshot)
    atomic_json(CAMPAIGN / "preserved_inputs.json", snapshot)
    scope = {"scenario": "A3", "hours": 1000, "new_variants": list(VARIANTS),
             "new_retrievals": 3, "total_models_including_existing_full": 4,
             "existing_full_state": str(full.STATE), "existing_full_untouched": True,
             "mpi_ranks_new": RANKS, "mpi_ranks_existing_full": 6,
             "global_rank_budget": BUDGET, "max_new_parallel": 3,
             "authorization": "User explicitly confirmed all four at 1000h in parallel",
             "utc": now(), "host_at_launch": host}
    atomic_json(CAMPAIGN / "selected_scope.json", scope)
    cases = []
    for variant, species in VARIANTS.items():
        case = {"run_id": "A3_1000h_A0_" + variant, "variant": variant,
                "scenario": "A3", "hours": 1000, "status": "pending", "mpi_ranks": RANKS,
                "fixed_species": species, "fixed_log10_vmr": {x: fixed[x] for x in species},
                "effective_free_dimension": 14 - len(species), "declared_dimension": 15,
                "dataset_sha256": baseline["dataset_sha256"],
                "run_dir": str(SCRATCH / "runs" / variant),
                "archive_dir": str(CAMPAIGN / "runs" / variant),
                "command": [str(x) for x in arguments(variant)]}
        cases.append(case)
    save({"status": "STARTING", "selection": scope, "cases": cases,
          "acceptance": "PENDING", "created_utc": now()})
    with (CAMPAIGN / "supervisor.log").open("x", encoding="utf-8") as stream:
        process = subprocess.Popen([str(full.PREFIX / "bin/python"), "-u", __file__, "--worker"],
                                   cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                                   stdin=subprocess.DEVNULL, start_new_session=True)
    (CAMPAIGN / "supervisor.pid").write_text(str(process.pid) + "\n")
    time.sleep(2)
    if process.poll() is not None:
        raise RuntimeError("Supervisor exited; preserve records and inspect log")
    print(json.dumps({"supervisor_pid": process.pid, "state": str(STATE), "selection": scope}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--launch", action="store_true")
    group.add_argument("--worker", action="store_true")
    options = parser.parse_args()
    worker() if options.worker else launch()
