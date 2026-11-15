"""Prepare or explicitly launch matched scalar-A0 retrievals; never overwrite.

--prepare freezes all 18 candidate cells without scheduling any retrieval.
--preflight-prototypes checks a full model and the three constraints on A3-100h.
--launch --mode joint|separate|both selects 6|12|18 cells, preflights each
against a matched full configuration, then uses at most two MPI6 workers.
Explicit --scenarios and --hours can restrict this selection (e.g. A3, 100).
Interrupted/failed states require a separately audited recovery, not relaunch.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from fixed_abundance_reference import load_fixed_abundances
from run_proxima_molecule_ablation_campaign import (
    CONDA_INIT, CONDA_PREFIX, DATASETS, POSEIDON_INPUT_DATA, PROJECT_REL,
    PYSYN_CDBS, RESULTS_REL,
)
from validate_proxima_molecular_ablation_loo import parse_evidence_from_result


CAMPAIGN_REL = PROJECT_REL / "retrievals/a0_fixed_reference_20261010"
SCRATCH = Path("/home/dasan/exofarm_a0ref_20261010")
VARIANTS = {"N2O": ["N2O"], "NH3": ["NH3"], "joint": ["N2O", "NH3"]}
MODE_VARIANTS = {"joint": ["joint"], "separate": ["N2O", "NH3"], "both": list(VARIANTS)}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def frozen_json(path, value):
    if path.exists():
        if json.loads(path.read_text(encoding="utf-8")) != value:
            raise ValueError(f"Frozen input changed: {path}")
    else:
        atomic_json(path, value)


def command(root, case, *, setup=False, full=False):
    name = case["run_id"] + ("_fullcheck" if full else "")
    config_path = root / CAMPAIGN_REL / "resolved" / (name + ".json")
    run_dir = SCRATCH / ("preflight" if setup else "runs") / name
    args = [str(CONDA_PREFIX / "bin/python"), "-u",
            str(root / "Thermal_Emission_Spectroscopy/scripts/run_life_retrieval.py"),
            "--campaign", "proxima", "--scenario", case["scenario"],
            "--hours", str(case["hours"]), "--n-live", "800", "--R", "10000",
            "--wl-min", "3.8", "--wl-max", "19.0", "--include-o2",
            "--x-profile", "isochem", "--error-inflation", "none",
            "--surface-pressure-mode", "fixed-black", "--dataset-file", case["dataset"],
            "--output-tag", "_A0ref_" + case["variant"] + "_v1" + ("_fullcheck" if full else ""),
            "--run-dir", str(run_dir), "--configuration-json", str(config_path)]
    if not full:
        args += ["--a0-reference", str(root / CAMPAIGN_REL / "a0_reference.json"),
                 "--fix-a0-species", *VARIANTS[case["variant"]]]
    if setup:
        args.append("--setup-only")
    else:
        args = [str(CONDA_PREFIX / "bin/mpiexec"), "-n", "6", *args]
    env = ["set -euo pipefail", "source " + shlex.quote(CONDA_INIT),
           "conda activate POSEIDON",
           "export POSEIDON_input_data=" + shlex.quote(POSEIDON_INPUT_DATA),
           "export PYSYN_CDBS=" + shlex.quote(PYSYN_CDBS),
           "export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1",
           "cd " + shlex.quote(str(root)), "exec " + shlex.join(args)]
    return "; ".join(env)


def prepare(root):
    campaign = root / CAMPAIGN_REL
    for folder in ("configs", "resolved", "preflight", "logs", "pids", "runs"):
        (campaign / folder).mkdir(parents=True, exist_ok=True)
    reference = load_fixed_abundances(campaign / "a0_reference.json", ["N2O", "NH3"], root)
    cases = []
    for hours in (100, 10, 1):
        for scenario in ("A3", "A1"):
            source = DATASETS[scenario, hours]
            dataset = root / PROJECT_REL / "life_data" / source["file"]
            full = root / RESULTS_REL / source["full_results"]
            if sha(dataset) != source["sha256"]:
                raise ValueError(f"Official dataset changed: {dataset}")
            parse_evidence_from_result(full, expected_parameters=15)
            for variant, species in VARIANTS.items():
                run_id = f"{scenario}_{hours}h_A0_{variant}"
                case = {"run_id": run_id, "scenario": scenario, "hours": hours,
                        "variant": variant, "fixed_species": species,
                        "fixed_log10_vmr": {x: reference[x] for x in species},
                        "dataset": str(dataset), "dataset_sha256": sha(dataset),
                        "dataset_seed": source["seed"], "full_results": str(full),
                        "full_results_sha256": sha(full),
                        "declared_dimension": 15, "effective_free_dimension": 14 - len(species),
                        "run_dir": str(SCRATCH / "runs" / run_id),
                        "archive_dir": str(campaign / "runs" / run_id)}
                case["command"] = command(root, case)
                frozen_json(campaign / "configs" / (run_id + ".json"), case)
                cases.append(case)
    plan = {"campaign": "a0_fixed_reference_20261010", "status": "AWAITING_MATRIX_CHOICE",
            "candidate_cells": 18, "selected_cells": 0, "new_retrievals_launched": 0,
            "options": {"joint": 6, "separate": 12, "both": 18},
            "mpi_ranks_per_run": 6, "max_parallel": 2, "n_live": 800, "ev_tol": 0.5,
            "reference_sha256": sha(campaign / "a0_reference.json"),
            "runner_sha256": sha(root / "Thermal_Emission_Spectroscopy/scripts/run_life_retrieval.py"),
            "fixed_prior_helper_sha256": sha(root / "Thermal_Emission_Spectroscopy/scripts/fixed_abundance_reference.py"),
            "canonical_full_models_reused": True, "cases": cases}
    frozen_json(campaign / "campaign_plan.json", plan)
    with (campaign / "candidate_manifest.csv").open("w", newline="", encoding="utf-8") as stream:
        fields = ["run_id", "scenario", "hours", "variant", "dataset_sha256",
                  "dataset_seed", "full_results", "full_results_sha256",
                  "declared_dimension", "effective_free_dimension", "run_dir", "archive_dir"]
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(cases)
    return cases


def verify_matched_configuration(full, fixed, case):
    """Permit exactly the named abundance priors to differ; retain all opacities."""
    for key in ("parameters", "declared_dimension", "param_species", "dataset_sha256",
                "R", "wl_min", "wl_max", "n_live", "ev_tol", "surface_pressure_mode",
                "error_inflation", "x_profile", "likelihood", "prior_types"):
        if full[key] != fixed[key]:
            raise ValueError(f"Matched-model mismatch: {case['run_id']} / {key}")
    for name, bounds in full["prior_ranges"].items():
        if name in ["log_" + x for x in case["fixed_species"]]:
            value = case["fixed_log10_vmr"][name[4:]]
            expected = [value, value]
        else:
            expected = bounds
        if fixed["prior_ranges"][name] != expected:
            raise ValueError(f"Unexpected prior change: {case['run_id']} / {name}")
    if full["effective_free_dimension"] != 14 or fixed["effective_free_dimension"] != case["effective_free_dimension"]:
        raise ValueError("Effective dimension mismatch")
    if fixed["dataset_sha256"] != case["dataset_sha256"]:
        raise ValueError("Dataset differs from frozen manifest")


def preflight(root, cases):
    campaign = root / CAMPAIGN_REL
    records = []
    for case in cases:
        for full in (True, False):
            name = case["run_id"] + ("_fullcheck" if full else "")
            log = campaign / "preflight" / (name + ".log")
            if log.exists():
                if "[setup-only] model, dataset, and priors validated; MultiNest skipped" not in log.read_text():
                    raise ValueError(f"Preserve failed/incomplete previous preflight: {log}")
            else:
                with log.open("x", encoding="utf-8") as stream:
                    completed = subprocess.run(["/bin/bash", "-lc", command(root, case, setup=True, full=full)],
                                               stdout=stream, stderr=subprocess.STDOUT)
                if completed.returncode != 0:
                    raise RuntimeError(f"Preflight exit {completed.returncode}: {log}")
        full_config = json.loads((campaign / "resolved" / (case["run_id"] + "_fullcheck.json")).read_text())
        fixed_config = json.loads((campaign / "resolved" / (case["run_id"] + ".json")).read_text())
        verify_matched_configuration(full_config, fixed_config, case)
        record = {"run_id": case["run_id"], "status": "PASS", "utc": now(),
                  "effective_free_dimension": fixed_config["effective_free_dimension"]}
        records.append(record)
        atomic_json(campaign / "preflight_progress.json", {"verified": records, "retrievals_launched": 0})
        print("[preflight]", case["run_id"], "PASS", flush=True)


def scientific_processes():
    output = subprocess.check_output(["ps", "-eo", "pid=,args="], text=True)
    return [line for line in output.splitlines()
            if any(token in line for token in ("/bin/mpiexec", "run_life_retrieval.py", "vulcan.py", "lpjml "))]


def save_state(campaign, state):
    state["updated_utc"] = now()
    state["counts"] = {status: sum(c["status"] == status for c in state["cases"])
                       for status in ("pending", "running", "complete", "failed")}
    atomic_json(campaign / "campaign_state.json", state)
    with (campaign / "manifest.csv").open("w", newline="", encoding="utf-8") as stream:
        fields = ["run_id", "scenario", "hours", "variant", "status", "pid", "return_code",
                  "start_utc", "end_utc", "dataset_sha256", "run_dir", "archive_dir", "launch_log"]
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(state["cases"])


def select_cases(cases, mode, scenarios, hours):
    """Select only the explicitly requested hypotheses and observed datasets."""
    if len(set(scenarios)) != len(scenarios) or len(set(hours)) != len(hours):
        raise ValueError("Duplicate scenario/time selection")
    if not scenarios or not hours or set(scenarios) - {"A1", "A3"} or set(hours) - {1, 10, 100}:
        raise ValueError("Invalid scenario/time selection")
    selected = [dict(c, status="pending") for c in cases
                if c["variant"] in MODE_VARIANTS[mode]
                and c["scenario"] in scenarios and c["hours"] in hours]
    expected = len(scenarios) * len(hours) * len(MODE_VARIANTS[mode])
    if len(selected) != expected or len({c["run_id"] for c in selected}) != expected:
        raise ValueError("Selected matrix is incomplete or duplicated")
    return selected


def launch(root, cases, mode, scenarios, hours):
    campaign = root / CAMPAIGN_REL
    if (campaign / "campaign_state.json").exists():
        raise RuntimeError("Existing campaign: audit state/checkpoints; duplicate launch refused")
    active = scientific_processes()
    if active:
        raise RuntimeError("Scientific processes already active: " + "\n".join(active))
    selected = select_cases(cases, mode, scenarios, hours)
    scope = {"mode": mode, "scenarios": scenarios, "hours": hours,
             "selected_cells": len(selected), "selected_run_ids": [c["run_id"] for c in selected],
             "candidate_plan_preserved": True, "selection_utc": now()}
    frozen_json(campaign / "selected_scope.json", scope)
    state = {"campaign": "a0_fixed_reference_20261010", "mode": mode,
             "status": "PREFLIGHT", "start_utc": now(), "supervisor_pid": os.getpid(),
             "max_parallel": 2, "mpi_ranks": 6, "cases": selected,
             "reference_sha256": sha(campaign / "a0_reference.json"),
             "selection": scope, "supervisor_code_sha256": sha(Path(__file__))}
    save_state(campaign, state)
    try:
        preflight(root, selected)
        # Setup-only resolves priors; no MPI execution is allowed until ALL pass.
        active = scientific_processes()
        if active:
            raise RuntimeError("Processes appeared during preflight: " + "\n".join(active))
        state["status"] = "RUNNING"
        processes = {}
        streams = {}
        failed = False
        while processes or any(c["status"] == "pending" for c in selected):
            for case in selected:
                key = case["run_id"]
                if key in processes and processes[key].poll() is not None:
                    rc = processes.pop(key).returncode
                    streams.pop(key).close()
                    case.update(return_code=rc, end_utc=now(), status="complete" if rc == 0 else "failed")
                    if rc == 0:
                        shutil.copytree(case["run_dir"], case["archive_dir"])
                        case["validation_status"] = "AWAITING_INDEPENDENT_PRODUCT_AUDIT"
                    else:
                        failed = True
                        state["failure"] = f"{key}: retrieval exit {rc}; see {case['launch_log']}"
                    print("[exit]", key, rc, flush=True)
            if not failed:
                for case in selected:
                    if len(processes) >= 2:
                        break
                    if case["status"] != "pending":
                        continue
                    directory = Path(case["run_dir"])
                    if directory.exists() and any(directory.iterdir()):
                        raise RuntimeError(f"Non-empty run directory: {directory}")
                    if Path(case["archive_dir"]).exists():
                        raise RuntimeError(f"Existing archive: {case['archive_dir']}")
                    log = campaign / "logs" / (case["run_id"] + ".log")
                    stream = log.open("x", encoding="utf-8")
                    process = subprocess.Popen(["/bin/bash", "-lc", case["command"]],
                                               stdout=stream, stderr=subprocess.STDOUT,
                                               start_new_session=True)
                    case.update(status="running", pid=process.pid, start_utc=now(), launch_log=str(log))
                    (campaign / "pids" / (case["run_id"] + ".pid")).write_text(str(process.pid) + "\n")
                    processes[case["run_id"]] = process
                    streams[case["run_id"]] = stream
                    print("[launch]", case["run_id"], process.pid, flush=True)
            save_state(campaign, state)
            if failed and not processes:
                break
            time.sleep(15)
        state["status"] = "FAILED_PRESERVED" if failed else "SAMPLING_COMPLETE_AUDIT_REQUIRED"
        save_state(campaign, state)
    except Exception as error:
        # Keep scratch, logs, and any active worker; never kill or restart it here.
        state.update(status="ACTION_REQUIRED", error=repr(error))
        save_state(campaign, state)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--prepare", action="store_true")
    actions.add_argument("--preflight-prototypes", action="store_true")
    actions.add_argument("--launch", action="store_true")
    parser.add_argument("--mode", choices=list(MODE_VARIANTS))
    parser.add_argument("--scenarios", nargs="+", choices=["A1", "A3"], default=["A1", "A3"])
    parser.add_argument("--hours", nargs="+", type=int, choices=[1, 10, 100], default=[1, 10, 100])
    args = parser.parse_args()
    if args.launch and not args.mode:
        parser.error("--launch requires the user's explicit --mode choice")
    root = Path(__file__).resolve().parents[2]
    cases = prepare(root)
    if args.preflight_prototypes:
        preflight(root, [c for c in cases if c["scenario"] == "A3" and c["hours"] == 100])
    elif args.launch:
        launch(root, cases, args.mode, args.scenarios, args.hours)
    else:
        print("Prepared 18 candidates; 0 selected; 0 retrievals launched", flush=True)


if __name__ == "__main__":
    main()
