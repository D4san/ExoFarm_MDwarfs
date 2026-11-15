"""Three fresh A0-fixed A3-1000h retrievals, corrected binning, MPI5 each.

Only the N2O/NH3 fixed priors differ from the existing corrected full model.
Checkpoints from the previous observation operator are never reused. A detached
supervisor preflights all three, measures MPI5 physical memory and schedules up
to three independent MPI communicators within a 15-rank CPU/memory budget.
"""

import argparse
import csv
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import time

import run_proxima_a3_1000h as base
from continue_proxima_a3_binning_shared_memory import available_kib, descendants_pss
from fixed_abundance_reference import load_fixed_abundances
from run_proxima_a0_reference_campaign import (
    VARIANTS, atomic_json, now, verify_matched_configuration,
)
from audit_life_operator_source_equivalence import audit as audit_operator_source

ROOT, PROJECT, PREFIX, SCRIPTS = base.ROOT, base.PROJECT, base.PREFIX, base.SCRIPTS


def configured_path(environment_name, default):
    """Resolve an optional isolated campaign/scratch root from the environment."""
    return Path(os.environ.get(environment_name, str(default))).expanduser().resolve()


CAMPAIGN = configured_path(
    "EXOFARM_A0_BINNING_CAMPAIGN",
    PROJECT / "retrievals/a0_fixed_reference_A3_1000h_binning_corrected_20261015",
)
SCRATCH = configured_path(
    "EXOFARM_A0_BINNING_SCRATCH",
    "/home/dasan/exofarm_a0bin_A3_1000h_20261015",
)
BASELINE = PROJECT / "retrievals/a3_1000h_binning_corrected_20261014"
REFERENCE = PROJECT / "retrievals/a0_fixed_reference_20261010/a0_reference.json"
RUNNER = SCRIPTS / "run_life_a0_binning_corrected.py"
STATE = CAMPAIGN / "campaign_state.json"
LOG = CAMPAIGN.parent / (CAMPAIGN.name + ".supervisor.log")
PID = LOG.with_suffix(".pid")
RANKS, BUDGET = 5, 15
EXPECTED_HASH = "5611c5904ef03aa02586bed15f14c0c2560ac5ae6fa9463ef420229311db75fa"
OS_RESERVE_KIB = 4 * 1024 ** 2
PER_JOB_WORK_KIB = int(0.25 * RANKS * 1024 ** 2)
PREFLIGHT_FOLDER = "preflight"


def science_jobs():
    """Read real process entries; shell snippets do not count as workers."""
    rows = subprocess.check_output(["ps", "-eo", "pid=,comm=,args="], text=True)
    jobs = []
    for row in rows.splitlines():
        fields = row.split(None, 2)
        if len(fields) != 3:
            continue
        pid, comm, command = fields
        if comm.startswith(("mpiexec", "mpirun", "orterun", "prterun")):
            args = shlex.split(command)
            rank_flag = "-n" if "-n" in args else "-np"
            if rank_flag not in args:
                raise RuntimeError("Unexpected MPI command: " + row)
            ranks = int(args[args.index(rank_flag) + 1])
            run_dir = args[args.index("--run-dir") + 1] if "--run-dir" in args else ""
            allowed = (str(RUNNER) in args and ranks == RANKS
                       and any(run_dir == str(SCRATCH / folder / variant)
                               for folder in ("preflight", "preflight_R1", "runs") for variant in VARIANTS))
            jobs.append({"pid": int(pid), "ranks": ranks, "allowed": allowed,
                         "command": command})
        elif comm.lower().startswith("lpj") or (comm.startswith("python") and "vulcan.py" in command):
            raise RuntimeError("Other scientific workload: " + row)
        elif comm.startswith("python") and "run_life_retrieval" in command:
            raise RuntimeError("Other retrieval worker: " + row)
    return jobs


def check_host(require_empty=False):
    jobs = science_jobs()
    if any(not job["allowed"] for job in jobs) or (require_empty and jobs):
        raise RuntimeError("Other MPI workload present: " + json.dumps(jobs))
    total = sum(job["ranks"] for job in jobs)
    if total > BUDGET or len(jobs) > 3:
        raise RuntimeError("Global MPI budget exceeded")
    cpus = len(os.sched_getaffinity(0))
    if cpus < BUDGET:
        raise RuntimeError(f"Need 15 logical CPUs, found {cpus}")
    return {"logical_cpus": cpus, "mpi_jobs": jobs, "rank_total": total,
            "available_KiB": available_kib()}


def arguments(variant, setup=False):
    """Keep model names short enough for MultiNest's output-root limit."""
    if variant not in VARIANTS:
        raise ValueError("Unknown selected variant")
    args = ["--variant", variant,
            "--operator-record", CAMPAIGN / PREFLIGHT_FOLDER / (variant + "_operator.json"),
            "--campaign", "proxima", "--scenario", "A3", "--hours", "1000",
            "--n-live", "800", "--error-inflation", "none",
            "--surface-pressure-mode", "fixed-black", "--include-o2",
            "--x-profile", "isochem", "--R", "10000", "--wl-min", "3.0",
            "--wl-max", "20.0", "--dataset-file", base.DATASET.relative_to(ROOT),
            "--output-tag", "_A0ref_" + variant + "_BIN1",
            "--a0-reference", CAMPAIGN / "a0_reference.json",
            "--fix-a0-species", *VARIANTS[variant],
            "--run-dir", SCRATCH / (PREFLIGHT_FOLDER if setup else "runs") / variant,
            "--configuration-json", CAMPAIGN / "resolved" / (variant + ".json")]
    if setup:
        args += ["--setup-only", "--validate-forward"]
    return [PREFIX / "bin/mpiexec", "-n", str(RANKS),
            PREFIX / "bin/python", "-u", RUNNER, *args]


def save(state):
    state["updated_utc"] = now()
    atomic_json(STATE, state)
    fields = ["run_id", "scenario", "hours", "variant", "status", "mpi_ranks",
              "effective_free_dimension", "pid", "return_code", "preflight",
              "dataset_sha256", "run_dir", "archive_dir", "launch_log"]
    temporary = CAMPAIGN / "manifest.csv.tmp"
    with temporary.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(state["cases"])
    temporary.replace(CAMPAIGN / "manifest.csv")


def preflight(state, snapshot):
    full = json.loads((BASELINE / "resolved_configuration.json").read_text())
    base.validate_dataset()
    for case in state["cases"]:
        variant = case["variant"]
        check_host(require_empty=True)
        peak = 0
        minimum = available_kib()
        with (CAMPAIGN / PREFLIGHT_FOLDER / (variant + ".log")).open("x") as stream:
            child = subprocess.Popen(base.environment_command(arguments(variant, setup=True)),
                                     cwd=ROOT, stdin=subprocess.DEVNULL,
                                     stdout=stream, stderr=subprocess.STDOUT)
            state["preflight_pid"] = child.pid
            state["preflight_variant"] = variant
            save(state)
            while child.poll() is None:
                peak = max(peak, descendants_pss(child.pid))
                minimum = min(minimum, available_kib())
                time.sleep(2)
        if child.returncode:
            raise RuntimeError(f"{variant}: MPI5 preflight exit {child.returncode}; see preflight log")
        config = CAMPAIGN / "resolved" / (variant + ".json")
        resolved = json.loads(config.read_text())
        verify_matched_configuration(full, resolved, case)
        expected = {"log_P_surf", *("log_" + name for name in case["fixed_species"])}
        if (set(resolved["fixed_parameters"]) != expected
                or resolved["fixed_log10_abundances"] != case["fixed_log10_vmr"]):
            raise ValueError("Unexpected fixed coordinates or values")
        record = json.loads((CAMPAIGN / PREFLIGHT_FOLDER / (variant + "_operator.json")).read_text())
        baseline_operator = json.loads((BASELINE / "preserved_inputs.json").read_text())
        key = str((SCRIPTS / "life_bin_operator_diagnostic.py").relative_to(ROOT))
        if record["status"] != "PASS" or record["mpi_ranks"] != RANKS:
            raise ValueError("Observation operator differs from the corrected full model")
        if record["operator_sha256"] != baseline_operator[key]:
            equivalence = audit_operator_source(write=False)
            if (equivalence["full_run_source_sha256"] != baseline_operator[key]
                    or equivalence["current_source_sha256"] != record["operator_sha256"]
                    or equivalence["scientific_operator_change"]):
                raise ValueError("Observation operator differs from the corrected full model")
            state["source_equivalence"] = equivalence
        case.update(preflight="PASS_MPI5", resolved_sha256=base.sha256(config),
                    peak_preflight_PSS_KiB=peak, minimum_MemAvailable_KiB=minimum)
        save(state)
        print("[preflight]", variant, "PASS_MPI5", "PSS_KiB", peak, flush=True)
    base.verify_frozen(snapshot)
    required = (sum(case["peak_preflight_PSS_KiB"] for case in state["cases"])
                + 3 * PER_JOB_WORK_KIB + OS_RESERVE_KIB)
    gate = {"available_KiB": available_kib(), "required_KiB": required,
            "peak_MPI5_PSS_KiB": {c["variant"]: c["peak_preflight_PSS_KiB"] for c in state["cases"]},
            "sampling_reserve_per_job_KiB": PER_JOB_WORK_KIB,
            "os_reserve_KiB": OS_RESERVE_KIB,
            "method": "sum of measured MPI5 PSS peaks, 0.25 GiB per rank work reserve, 4 GiB OS reserve",
            "all_three_simultaneous_fit": required < available_kib()}
    atomic_json(CAMPAIGN / "resource_gate.json", gate)
    atomic_json(CAMPAIGN / "preflight_validation.json", {
        "utc": now(), "all_pass": True, "dataset_sha256": EXPECTED_HASH,
        "same_operator_as_corrected_full": True,
        "same_configuration_except_selected_fixed_abundances": True,
        "free_dimensions": [13, 13, 12], "resource_gate": gate})
    state.update(preflight="PASS_ALL_THREE_MPI5", resource_gate=gate)
    save(state)


def worker():
    state = json.loads(STATE.read_text())
    snapshot = json.loads((CAMPAIGN / "preserved_inputs.json").read_text())
    processes, streams = {}, {}
    try:
        state.update(status="PREFLIGHT", supervisor_pid=os.getpid())
        save(state)
        base.verify_frozen(snapshot)
        preflight(state, snapshot)
        state["status"] = "RUNNING"
        failed = False
        while processes or any(case["status"] == "pending" for case in state["cases"]):
            for case in state["cases"]:
                variant = case["variant"]
                if variant in processes and processes[variant].poll() is not None:
                    child = processes.pop(variant)
                    streams.pop(variant).close()
                    case.update(return_code=child.returncode, end_utc=now())
                    if child.returncode:
                        failed = True
                        case["status"] = "failed_preserved"
                        state["failure"] = f"{variant}: retrieval exit {child.returncode}; {case['launch_log']}"
                    else:
                        case["status"] = "archiving"
                        save(state)
                        shutil.copytree(case["run_dir"], case["archive_dir"])
                        case.update(status="complete_pending_validation", acceptance="PENDING")
                    print("[exit]", variant, child.returncode, flush=True)
            if not failed:
                for case in state["cases"]:
                    if case["status"] != "pending":
                        continue
                    host = check_host()
                    needed = (case["peak_preflight_PSS_KiB"] + PER_JOB_WORK_KIB
                              + len(processes) * PER_JOB_WORK_KIB + OS_RESERVE_KIB)
                    # Reserve the still-unallocated part of active loaders too.
                    # MemAvailable alone would overstate headroom just after exec.
                    for active in state["cases"]:
                        if active["variant"] in processes:
                            needed += max(0, active["peak_preflight_PSS_KiB"]
                                          - descendants_pss(processes[active["variant"]].pid))
                    if (host["rank_total"] + RANKS > BUDGET
                            or host["available_KiB"] < needed):
                        case["queue_reason"] = "Waiting for measured MPI5 memory/CPU headroom"
                        break
                    base.verify_frozen(snapshot)
                    if base.sha256(CAMPAIGN / "resolved" / (case["variant"] + ".json")) != case["resolved_sha256"]:
                        raise RuntimeError("Resolved configuration changed after preflight")
                    if Path(case["run_dir"]).exists() or Path(case["archive_dir"]).exists():
                        raise RuntimeError("Existing production scratch/archive; duplicate refused")
                    stream = Path(case["launch_log"]).open("x")
                    child = subprocess.Popen(base.environment_command(arguments(case["variant"])),
                                             cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                                             stdin=subprocess.DEVNULL, start_new_session=True)
                    processes[case["variant"]] = child
                    streams[case["variant"]] = stream
                    case.update(status="running", pid=child.pid, start_utc=now())
                    case.pop("queue_reason", None)
                    save(state)
                    print("[launch]", case["variant"], child.pid, "MPI5", flush=True)
                    # Space opacity-loader peaks rather than starting all three at once.
                    time.sleep(20)
            state["host"] = check_host()
            save(state)
            if failed and not processes:
                break
            time.sleep(15)
        base.verify_frozen(snapshot)
        state.update(status="FAILED_PRESERVED" if failed else "COMPLETE_PENDING_VALIDATION",
                     acceptance="PENDING_INDEPENDENT_REVIEW", scratch_preserved=True)
        save(state)
    except Exception as error:
        state.update(status="ACTION_REQUIRED", error=f"{type(error).__name__}: {error}",
                     scratch_preserved=True)
        save(state)
        # Workers already sampling and all original products remain available.
        raise


def launch():
    if sys.platform != "linux":
        raise RuntimeError("Use the verified Ubuntu POSEIDON environment")
    if any(path.exists() for path in (CAMPAIGN, SCRATCH, LOG, PID)):
        raise RuntimeError("Existing campaign/scratch/launch records; duplicate refused")
    host = check_host(require_empty=True)
    if host["available_KiB"] < 20 * 1024 ** 2:
        raise RuntimeError("Less than 20 GiB available before the three-run preflight")
    if base.sha256(base.DATASET) != EXPECTED_HASH:
        raise ValueError("Dataset changed")
    baseline = json.loads((BASELINE / "campaign_state.json").read_text())
    if baseline.get("exit_code") != 0 or baseline.get("comparison") != "SAVED":
        raise ValueError("Corrected full model has not completed with saved comparison")
    fixed = load_fixed_abundances(REFERENCE, ["N2O", "NH3"], ROOT)
    CAMPAIGN.mkdir()
    for folder in ("preflight", "resolved", "logs", "runs"):
        (CAMPAIGN / folder).mkdir()
    shutil.copy2(REFERENCE, CAMPAIGN / "a0_reference.json")
    reference = json.loads(REFERENCE.read_text())
    snapshot = base.frozen_inputs()
    paths = [base.DATASET, Path(__file__), RUNNER, REFERENCE,
             CAMPAIGN / "a0_reference.json", ROOT / reference["profile_rel"],
             SCRIPTS / "fixed_abundance_reference.py",
             SCRIPTS / "run_life_retrieval_binning_corrected.py",
             SCRIPTS / "life_bin_operator_diagnostic.py",
             SCRIPTS / "run_proxima_a0_reference_campaign.py",
             BASELINE / "resolved_configuration.json", BASELINE / "campaign_state.json"]
    paths += [path for path in (BASELINE / "products").rglob("*") if path.is_file()]
    snapshot.update({str(path.relative_to(ROOT)): base.sha256(path) for path in paths})
    atomic_json(CAMPAIGN / "preserved_inputs.json", snapshot)
    scope = {"scenario": "A3", "hours": 1000, "new_variants": list(VARIANTS),
             "new_retrievals": 3, "existing_full": str(BASELINE),
             "campaign": CAMPAIGN.name,
             "mpi_ranks_per_run": RANKS, "max_parallel": 3,
             "global_rank_budget": BUDGET, "monitor_interval_minutes": 90,
             "operator": "same corrected midpoint-photon operator as full",
             "dataset_sha256": EXPECTED_HASH, "checkpoint_reuse": False,
             "previous_attempt": os.environ.get(
                 "EXOFARM_A0_BINNING_PREVIOUS_CAMPAIGN", ""),
             "other_exposures": "deferred; no 1/10/100h execution",
             "authorization": os.environ.get(
                 "EXOFARM_A0_BINNING_AUTHORIZATION",
                 "2026-10-15: user requests exactly three fresh runs, MPI5 each, monitoring every 90 minutes",
             ),
             "utc": now(), "host_at_launch": host}
    atomic_json(CAMPAIGN / "selected_scope.json", scope)
    cases = []
    for variant, species in VARIANTS.items():
        cases.append({
            "run_id": "A3_1000h_A0_" + variant + "_BIN1", "variant": variant,
            "scenario": "A3", "hours": 1000, "status": "pending",
            "mpi_ranks": RANKS, "fixed_species": species,
            "fixed_log10_vmr": {name: fixed[name] for name in species},
            "declared_dimension": 15, "effective_free_dimension": 14 - len(species),
            "dataset_sha256": EXPECTED_HASH,
            "run_dir": str(SCRATCH / "runs" / variant),
            "archive_dir": str(CAMPAIGN / "runs" / variant),
            "launch_log": str(CAMPAIGN / "logs" / (variant + ".log")),
            "command": [str(arg) for arg in arguments(variant)]})
    save({"status": "STARTING", "selection": scope, "cases": cases,
          "acceptance": "PENDING", "created_utc": now()})
    with LOG.open("x") as stream:
        child = subprocess.Popen([str(PREFIX / "bin/python"), "-u", __file__, "--worker"],
                                 cwd=ROOT, stdin=subprocess.DEVNULL, stdout=stream,
                                 stderr=subprocess.STDOUT, start_new_session=True)
    PID.write_text(str(child.pid) + "\n")
    time.sleep(2)
    if child.poll() is not None:
        raise RuntimeError(f"Supervisor exit {child.returncode}; inspect {LOG}")
    print(json.dumps({"supervisor_pid": child.pid, "state": str(STATE),
                      "log": str(LOG), "ranks_per_run": RANKS, "new_runs": 3}))


def continue_documentation_gate():
    """Continue only a stopped pre-sampling provenance gate; keep its records."""
    global PREFLIGHT_FOLDER
    state = json.loads(STATE.read_text())
    if (state["status"] != "ACTION_REQUIRED"
            or state.get("error") != "ValueError: Observation operator differs from the corrected full model"
            or any(case["status"] != "pending" for case in state["cases"])
            or any(Path(case["run_dir"]).exists() for case in state["cases"])):
        raise RuntimeError("Only the stopped documentation-checksum preflight may continue")
    check_host(require_empty=True)
    previous_pid = int(PID.read_text())
    if Path(f"/proc/{previous_pid}").exists():
        raise RuntimeError("Previous supervisor is still present; preserve it")
    equivalence = audit_operator_source(write=True)
    archive = CAMPAIGN / "pre_sampling_source_gate_failure"
    archive.mkdir()
    for path in (STATE, CAMPAIGN / "preserved_inputs.json", LOG, PID):
        shutil.copy2(path, archive / path.name)
    (CAMPAIGN / "preflight_R1").mkdir()
    snapshot = json.loads((CAMPAIGN / "preserved_inputs.json").read_text())
    supervisor_rel = str(Path(__file__).relative_to(ROOT))
    # This continuation edits orchestration only; verify every other input first.
    expected_supervisor = snapshot.pop(supervisor_rel)
    base.verify_frozen(snapshot)
    snapshot[supervisor_rel] = base.sha256(Path(__file__))
    helper = SCRIPTS / "audit_life_operator_source_equivalence.py"
    snapshot[str(helper.relative_to(ROOT))] = base.sha256(helper)
    atomic_json(CAMPAIGN / "preserved_inputs.json", snapshot)
    state.update(status="STARTING", prior_gate_error=state.pop("error"),
                 preflight_folder="preflight_R1", source_equivalence=equivalence,
                 sampling_started_before_continuation=False,
                 previous_supervisor_source_sha256=expected_supervisor,
                 checkpoint_reuse=False)
    PREFLIGHT_FOLDER = "preflight_R1"
    for case in state["cases"]:
        case["command"] = [str(arg) for arg in arguments(case["variant"])]
    log = LOG.with_name(CAMPAIGN.name + ".source_audit_R1.supervisor.log")
    state["supervisor_log"] = str(log)
    save(state)
    with log.open("x") as stream:
        child = subprocess.Popen([str(PREFIX / "bin/python"), "-u", __file__,
                                  "--worker", "--source-audit-continuation"],
                                 cwd=ROOT, stdin=subprocess.DEVNULL, stdout=stream,
                                 stderr=subprocess.STDOUT, start_new_session=True)
    PID.write_text(str(child.pid) + "\n")
    time.sleep(2)
    if child.poll() is not None:
        raise RuntimeError(f"Continuation supervisor exit {child.returncode}; inspect {log}")
    print(json.dumps({"supervisor_pid": child.pid, "state": str(STATE),
                      "log": str(log), "source_equivalence": "PASS",
                      "sampling_started_before_continuation": False}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--launch", action="store_true")
    actions.add_argument("--worker", action="store_true")
    actions.add_argument("--continue-documentation-gate", action="store_true")
    parser.add_argument("--source-audit-continuation", action="store_true")
    options = parser.parse_args()
    if options.source_audit_continuation:
        PREFLIGHT_FOLDER = "preflight_R1"
    if options.continue_documentation_gate:
        continue_documentation_gate()
    elif options.worker:
        worker()
    else:
        launch()
