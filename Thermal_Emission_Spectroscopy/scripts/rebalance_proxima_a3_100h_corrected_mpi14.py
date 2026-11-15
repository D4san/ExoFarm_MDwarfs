"""Stop the serial A3-100 h corrected-bin run and resume it with 14 MPI ranks.

This one-use migration preserves the serial attempt, validates and snapshots
its exact MultiNest checkpoint while the sampler is frozen, then resumes the
same likelihood in a new scratch/campaign. Invalid checkpoints trigger a
fresh 14-rank run only; old files are never overwritten.
"""

import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
import traceback

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1"
RETRIEVALS = PROJECT / "retrievals"
OLD_CAMPAIGN = RETRIEVALS / "a3_100h_binning_corrected_20261017"
OLD_SCRATCH = Path("/home/dasan/exofarm_a3_100h_binning_corrected_20261017")
CAMPAIGN = RETRIEVALS / "a3_100h_binning_corrected_mpi14_resume_20261018"
SCRATCH = Path("/home/dasan/exofarm_a3_100h_binning_corrected_mpi14_resume_20261018")
DATASET = PROJECT / "life_data/LIFE_proxima_A3_100h.dat"
EXPECTED_DATASET_SHA256 = (
    "78662546181a5b74391a14b7b73ae80d879200a74db6a4bc5338e3ce7eee4705"
)
BASELINE = (
    RETRIEVALS / "POSEIDON_output/proxima_b_earthlike/retrievals/results"
    / "proxima_A3_100h_O2_fixedBlack1bar_noxtol_"
    "proxima_A3_100h_O2_fixedBlack1bar_noxtol_postprocess_manifest.json"
)
ORIGINAL_ADAPTER = ROOT / (
    "Thermal_Emission_Spectroscopy/scripts/"
    "run_life_retrieval_a3_100h_binning_corrected.py"
)
MPI14_ADAPTER = ROOT / (
    "Thermal_Emission_Spectroscopy/scripts/"
    "run_life_retrieval_a3_100h_binning_corrected_mpi14_resume.py"
)
BASE_RUNNER = ROOT / "Thermal_Emission_Spectroscopy/scripts/run_life_retrieval.py"
OPERATOR = ROOT / "Thermal_Emission_Spectroscopy/scripts/life_bin_operator_diagnostic.py"
PYTHON = Path("/home/dasan/anaconda3/envs/POSEIDON/bin/python")
MPIEXEC = Path("/home/dasan/anaconda3/envs/POSEIDON/bin/mpiexec")
RANKS = 14
N_LIVE = 800
TAG = "_O2_fixedBlack1bar_noxtol_BIN1_20261017"
MODEL_NAME = "proxima_A3_100h_O2_fixedBlack1bar_noxtol_BIN1_20261017"
RUN_ID = "A3_100h_full_BIN1_20261018_MPI14_resume01"
RESERVE_KIB = int(4.5 * 1024 * 1024)
STATE = CAMPAIGN / "campaign_state.json"
MANIFEST = CAMPAIGN / "manifest.csv"
SUPERVISOR_LOG = RETRIEVALS / "a3_100h_binning_corrected_mpi14_resume_20261018.supervisor.log"
SUPERVISOR_PID = RETRIEVALS / "a3_100h_binning_corrected_mpi14_resume_20261018.supervisor.pid"
RETRY_LOG = RETRIEVALS / "a3_100h_binning_corrected_mpi14_resume_20261018.retry01.supervisor.log"
RETRY_PID = RETRIEVALS / "a3_100h_binning_corrected_mpi14_resume_20261018.retry01.supervisor.pid"


def utc_now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def record(state):
    state["updated_utc"] = utc_now()
    write_json(STATE, state)


def process_identity(pid):
    stat = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
    rest = stat[stat.rindex(")") + 2:].split()
    command = Path(f"/proc/{pid}/cmdline").read_bytes()
    return {
        "pid": int(pid),
        "ppid": int(rest[1]),
        "state": rest[0],
        "start_ticks": rest[19],
        "command": command.replace(b"\0", b" ").decode(errors="replace").strip(),
    }


def signal_exact(saved, sig):
    current = process_identity(saved["pid"])
    if (current["start_ticks"] != saved["start_ticks"]
            or current["command"] != saved["command"]):
        raise RuntimeError(f"PID identity changed; refusing signal to {saved['pid']}")
    os.kill(saved["pid"], sig)


def proc_table():
    records = {}
    for path in Path("/proc").iterdir():
        if not path.name.isdigit():
            continue
        try:
            records[int(path.name)] = process_identity(int(path.name))
        except (FileNotFoundError, ProcessLookupError, PermissionError, OSError):
            continue
    return records


def descendants(root_pid):
    table = proc_table()
    found = {int(root_pid)}
    changed = True
    while changed:
        changed = False
        for pid, item in table.items():
            if item["ppid"] in found and pid not in found:
                found.add(pid)
                changed = True
    return [table[pid] for pid in sorted(found) if pid in table]


def pss_kib(pid):
    path = Path(f"/proc/{pid}/smaps_rollup")
    try:
        match = re.search(r"^Pss:\s+(\d+)\s+kB", path.read_text(), re.MULTILINE)
    except (FileNotFoundError, PermissionError, OSError):
        return 0
    return int(match.group(1)) if match else 0


def mem_available_kib():
    text = Path("/proc/meminfo").read_text(encoding="utf-8")
    match = re.search(r"^MemAvailable:\s+(\d+)\s+kB", text, re.MULTILINE)
    if not match:
        raise RuntimeError("MemAvailable is absent from /proc/meminfo")
    return int(match.group(1))


def swap_kib():
    text = Path("/proc/meminfo").read_text(encoding="utf-8")
    total = re.search(r"^SwapTotal:\s+(\d+)\s+kB", text, re.MULTILINE)
    free = re.search(r"^SwapFree:\s+(\d+)\s+kB", text, re.MULTILINE)
    return {
        "total_kib": int(total.group(1)) if total else None,
        "free_kib": int(free.group(1)) if free else None,
    }


def environment():
    env = os.environ.copy()
    env.update({
        "POSEIDON_input_data": "/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs",
        "PYSYN_CDBS": "/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids",
        "OMP_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
        "PYTHONUNBUFFERED": "1",
    })
    return env


def active_science(excluded_pids=()):
    excluded = {int(pid) for pid in excluded_pids}
    tokens = ("mpiexec", "mpirun", "run_life_retrieval")
    return [item for pid, item in proc_table().items()
            if pid not in excluded and item["state"] not in ("Z", "X")
            and any(token in item["command"] for token in tokens)]


def checkpoint_report(run_root, configuration):
    raw = Path(run_root) / "POSEIDON_output/proxima_b_earthlike/retrievals/MultiNest_raw"
    prefix = raw / f"{configuration['model_name']}-"
    required = [
        Path(str(prefix) + "resume.dat"),
        Path(str(prefix) + "live.points"),
        Path(str(prefix) + "phys_live.points"),
        Path(str(prefix) + "ev.dat"),
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Checkpoint files missing: {missing}")
    lines = required[0].read_text(encoding="utf-8").splitlines()
    if len(lines) < 2:
        raise RuntimeError("resume.dat lacks its persisted counters")
    counters = [int(value) for value in lines[1].split()]
    if len(counters) != 4 or counters[0] < N_LIVE or counters[3] != N_LIVE:
        raise RuntimeError(f"Unexpected MultiNest resume counters: {counters}")
    replacements, evaluations = counters[:2]
    live = np.loadtxt(required[1], ndmin=2)
    physical = np.loadtxt(required[2], ndmin=2)
    events = np.loadtxt(required[3], ndmin=2)
    n_parameters = len(configuration["parameters"])
    if live.shape != (N_LIVE, n_parameters + 1):
        raise RuntimeError(f"Unexpected live.points shape: {live.shape}")
    if physical.shape != (N_LIVE, n_parameters + 2):
        raise RuntimeError(f"Unexpected phys_live.points shape: {physical.shape}")
    if events.shape[0] < max(0, replacements - N_LIVE) or events.shape[1] < n_parameters + 1:
        raise RuntimeError(f"Unexpected ev.dat shape: {events.shape}")
    for name, values in (("live", live), ("physical", physical), ("events", events)):
        if not np.isfinite(values).all():
            raise RuntimeError(f"Checkpoint contains nonfinite {name} values")
    if np.any(live[:, :n_parameters] < 0) or np.any(live[:, :n_parameters] > 1):
        raise RuntimeError("Unit-cube live points fall outside [0,1]")
    np.testing.assert_array_equal(live[:, -1], physical[:, n_parameters])
    for column, name in enumerate(configuration["parameters"]):
        low, high = configuration["prior_ranges"][name]
        values = physical[:, column]
        if np.any(values < low - 1e-12) or np.any(values > high + 1e-12):
            raise RuntimeError(f"Persisted live points fall outside prior for {name}")
        if low == high:
            np.testing.assert_allclose(values, low, rtol=0, atol=0)
    hashes = {path.name: sha256(path) for path in raw.iterdir() if path.is_file()}
    return {
        "status": "PASS",
        "raw_directory": str(raw),
        "replacements": replacements,
        "evaluations": evaluations,
        "n_live": N_LIVE,
        "live_shape": list(live.shape),
        "physical_live_shape": list(physical.shape),
        "event_shape": list(events.shape),
        "finite": True,
        "unit_cube_bounds": "PASS",
        "prior_bounds_and_fixed_values": "PASS",
        "hashes": hashes,
    }


def wait_until_gone(pid, timeout=90):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            item = process_identity(pid)
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            return True
        if item["state"] in ("Z", "X"):
            return True
        time.sleep(0.5)
    return False


def update_old_attempt(state, report):
    old_state_path = OLD_CAMPAIGN / "campaign_state.json"
    old_state = json.loads(old_state_path.read_text(encoding="utf-8"))
    old_state.update({
        "status": "STOPPED_BY_USER_MPI14_REBALANCE",
        "acceptance": "PENDING",
        "stop_reason": "Explicit user request to stop and relaunch with 14 MPI ranks",
        "stop_signal": "SIGTERM",
        "successor_campaign": str(CAMPAIGN.relative_to(ROOT)),
        "checkpoint_snapshot": str((CAMPAIGN / "checkpoint_validation.json").relative_to(ROOT)),
        "checkpoint_replacements_at_stop": report.get("replacements"),
        "checkpoint_evaluations_at_stop": report.get("evaluations"),
        "stop_utc": utc_now(),
        "updated_utc": utc_now(),
    })
    write_json(old_state_path, old_state)
    with (OLD_CAMPAIGN / "manifest.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
        fields = list(rows[0]) if rows else []
    if rows:
        rows[0]["status"] = "STOPPED_BY_USER_MPI14_REBALANCE"
        rows[0]["return_code"] = "-15"
        with (OLD_CAMPAIGN / "manifest.csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)


def stop_and_stage_checkpoint(_migration_state):
    source_state = json.loads((OLD_CAMPAIGN / "campaign_state.json").read_text())
    if (source_state.get("status") != "RUNNING"
            or source_state.get("mpi_ranks") != 1):
        raise RuntimeError(
            "Unexpected source state: "
            f"{source_state.get('status')}/{source_state.get('mpi_ranks')}"
        )
    if source_state.get("dataset_sha256") != EXPECTED_DATASET_SHA256:
        raise RuntimeError("Active source state has an unexpected dataset hash")
    if sha256(DATASET) != EXPECTED_DATASET_SHA256:
        raise RuntimeError("A3-100 h dataset hash changed")
    if sha256(OLD_CAMPAIGN / "resolved_configuration.json") != sha256(CAMPAIGN / "resolved_configuration.json"):
        raise RuntimeError("Resolved configuration snapshot differs from the active run")
    if json.loads((OLD_CAMPAIGN / "operator_preflight.json").read_text()).get("status") != "PASS":
        raise RuntimeError("Corrected photon-overlap preflight is not PASS")

    supervisor_pid = int(source_state["supervisor_pid"])
    run_pid = int(source_state["run_pid"])
    supervisor = process_identity(supervisor_pid)
    sampler = process_identity(run_pid)
    if "launch_proxima_a3_100h_binning_corrected.py --worker" not in supervisor["command"]:
        raise RuntimeError("Supervisor process identity does not match the source campaign")
    if ("run_life_retrieval_a3_100h_binning_corrected.py" not in sampler["command"]
            or sampler["ppid"] != supervisor_pid
            or str(OLD_SCRATCH / "run") not in sampler["command"]):
        raise RuntimeError("Sampler PID/parent/command identity mismatch")
    conflicts = active_science(excluded_pids=(supervisor_pid, run_pid, os.getpid()))
    if conflicts:
        raise RuntimeError(f"Unrelated retrieval/MPI workers are active: {conflicts}")

    (CAMPAIGN / "migration_evidence").mkdir(parents=True, exist_ok=True)
    write_json(CAMPAIGN / "migration_evidence/before_state.json", source_state)
    shutil.copy2(OLD_CAMPAIGN / "manifest.csv", CAMPAIGN / "migration_evidence/before_manifest.csv")
    write_json(CAMPAIGN / "migration_evidence/old_process_identities.json", [supervisor, sampler])
    os.kill(run_pid, signal.SIGSTOP)
    time.sleep(0.5)
    frozen = process_identity(run_pid)
    if frozen["state"] not in ("T", "t"):
        os.kill(run_pid, signal.SIGCONT)
        raise RuntimeError("Sampler did not enter a stopped state; left it running")

    try:
        resolved = json.loads((OLD_CAMPAIGN / "resolved_configuration.json").read_text())
        raw_source = (
            OLD_SCRATCH / "run/POSEIDON_output/proxima_b_earthlike/retrievals/MultiNest_raw"
        )
        backup = CAMPAIGN / "checkpoint_snapshot/MultiNest_raw"
        shutil.copytree(raw_source, backup)
        raw_hashes = {path.name: sha256(path) for path in raw_source.iterdir() if path.is_file()}
        for name, expected in raw_hashes.items():
            if sha256(backup / name) != expected:
                raise RuntimeError(f"Checkpoint snapshot hash mismatch: {name}")
        try:
            report = checkpoint_report(OLD_SCRATCH / "run", resolved)
        except Exception as checkpoint_error:
            report = {
                "status": "FAIL",
                "error": f"{type(checkpoint_error).__name__}: {checkpoint_error}",
                "raw_directory": str(raw_source),
                "hashes": raw_hashes,
                "validated_utc": utc_now(),
                "source_campaign": str(OLD_CAMPAIGN.relative_to(ROOT)),
                "resume_safe_basis": "Checkpoint failed validation; successor will start fresh.",
            }
        if report["status"] == "PASS":
            shutil.copytree(OLD_SCRATCH / "run", SCRATCH / "run")
            staged_raw = (
                SCRATCH / "run/POSEIDON_output/proxima_b_earthlike/"
                "retrievals/MultiNest_raw"
            )
            for name, expected in report["hashes"].items():
                if sha256(staged_raw / name) != expected:
                    raise RuntimeError(f"Staged resume hash mismatch: {name}")
    except Exception:
        os.kill(run_pid, signal.SIGCONT)
        raise

    report.setdefault("validated_utc", utc_now())
    report.setdefault("source_campaign", str(OLD_CAMPAIGN.relative_to(ROOT)))
    report["source_scratch"] = str(OLD_SCRATCH)
    report["staged_run_directory"] = str(SCRATCH / "run") if report["status"] == "PASS" else None
    report["rank_change"] = {"from": 1, "to": RANKS}
    if report["status"] == "PASS":
        report["resume_safe_basis"] = (
            "same corrected operator, dataset, resolved priors/model and MultiNest basename; "
            "only MPI rank count changes"
        )
    write_json(CAMPAIGN / "checkpoint_validation.json", report)

    signal_exact(sampler, signal.SIGTERM)
    signal_exact(sampler, signal.SIGCONT)
    if not wait_until_gone(run_pid):
        raise RuntimeError("Stopped sampler did not exit after SIGTERM; no new run launched")
    if not wait_until_gone(supervisor_pid, timeout=120):
        raise RuntimeError("Original supervisor did not finish its stop bookkeeping")
    update_old_attempt(source_state, report)
    return report


def mpi_prefix():
    # The POSEIDON environment uses MPICH/Hydra.  Open MPI's launcher is not
    # ABI-compatible with its mpi4py client and fails during PMI_Init.
    return [str(MPIEXEC), "-n", str(RANKS)]


def runner_arguments(operator_record, run_dir, setup_only):
    result = [
        "--operator-record", str(operator_record),
        "--campaign", "proxima", "--scenario", "A3", "--hours", "100",
        "--n-live", "800", "--error-inflation", "none",
        "--surface-pressure-mode", "fixed-black", "--include-o2",
        "--x-profile", "isochem", "--output-tag", TAG,
        "--R", "10000", "--wl-min", "3.0", "--wl-max", "20.0",
        "--dataset-file", str(DATASET.relative_to(ROOT)),
        "--run-dir", str(run_dir),
        "--configuration-json", str(CAMPAIGN / "resolved_configuration.json"),
    ]
    if setup_only:
        result.extend(["--setup-only", "--validate-forward"])
    return result


def resource_sample(pid):
    tree = descendants(pid)
    return {
        "utc": utc_now(),
        "tree_pids": [item["pid"] for item in tree],
        "tree_pss_kib": sum(pss_kib(item["pid"]) for item in tree),
        "mem_available_kib": mem_available_kib(),
        "swap": swap_kib(),
    }


def run_preflight(command, logfile):
    peak_pss = 0
    minimum_available = mem_available_kib()
    samples = []
    with logfile.open("x", encoding="utf-8") as stream:
        process = subprocess.Popen(
            command, cwd=ORIGINAL_ADAPTER.parent, env=environment(),
            stdout=stream, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL, start_new_session=True,
        )
        while process.poll() is None:
            sample = resource_sample(process.pid)
            samples.append(sample)
            peak_pss = max(peak_pss, sample["tree_pss_kib"])
            minimum_available = min(minimum_available, sample["mem_available_kib"])
            time.sleep(1)
        return_code = process.wait()
    return return_code, peak_pss, minimum_available, samples


def verify_mpi_log(logfile):
    text = logfile.read_text(encoding="utf-8", errors="replace")
    found = {(int(rank), int(size)) for rank, size in re.findall(
        r"\[operator-active\]\s+rank=(\d+)\s+size=(\d+)", text
    )}
    expected = {(rank, RANKS) for rank in range(RANKS)}
    if found != expected:
        raise RuntimeError(f"Preflight did not confirm all 14 MPI ranks: {sorted(found)}")


def write_manifest(row):
    fields = [
        "run_id", "scenario", "hours", "operator", "status", "mpi_ranks",
        "n_live", "declared_dimension", "effective_free_dimension",
        "dataset_sha256", "run_dir", "archive_dir", "log", "return_code",
    ]
    with MANIFEST.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerow({name: row.get(name, "") for name in fields})


def copy_campaign_inputs():
    shutil.copy2(OLD_CAMPAIGN / "resolved_configuration.json", CAMPAIGN / "resolved_configuration.json")
    shutil.copy2(OLD_CAMPAIGN / "operator_preflight.json", CAMPAIGN / "operator_preflight_serial_reference.json")
    shutil.copy2(OLD_CAMPAIGN / "preserved_inputs.json", CAMPAIGN / "source_preserved_inputs.json")
    old_scope = json.loads((OLD_CAMPAIGN / "selected_scope.json").read_text())
    scope = dict(old_scope)
    scope.update({
        "campaign": CAMPAIGN.name,
        "execution": "one mpiexec with exactly 14 MPI ranks; one thread per rank",
        "mpi_ranks": RANKS,
        "checkpoint_reuse": "resume only from the validated checkpoint of the same corrected likelihood",
        "resume_source_campaign": str(OLD_CAMPAIGN.relative_to(ROOT)),
        "native_grid_note": (
            "The 3-20 um native grid remains part of this corrected campaign; "
            "the historical run used 3.8-19 um, so grid extent is a comparison caveat."
        ),
        "authorization_utc": utc_now(),
    })
    write_json(CAMPAIGN / "selected_scope.json", scope)
    inputs = {
        "dataset": str(DATASET.relative_to(ROOT)),
        "dataset_sha256": sha256(DATASET),
        "baseline_manifest_sha256": sha256(BASELINE),
        "resolved_configuration_sha256": sha256(CAMPAIGN / "resolved_configuration.json"),
        "original_adapter_sha256": sha256(ORIGINAL_ADAPTER),
        "mpi14_adapter_sha256": sha256(MPI14_ADAPTER),
        "base_runner_sha256": sha256(BASE_RUNNER),
        "operator_source_sha256": sha256(OPERATOR),
        "mpi_ranks": RANKS,
        "thread_limit": 1,
    }
    write_json(CAMPAIGN / "preserved_inputs.json", inputs)
    (CAMPAIGN / "README.md").write_text(
        "# A3–100 h corrected-bin retrieval, MPI14 continuation\n\n"
        "This isolated attempt continues the same corrected photon-overlap "
        "likelihood from the validated MultiNest checkpoint produced by the "
        "serial attempt. The dataset, resolved model/priors, operator, `N_live=800`, "
        "`R=10000`, native 3–20 μm grid, 31 channels, no-inflation likelihood, "
        "isochemical chemistry, O2, and fixed black surface at 1 bar are retained.\n\n"
        "Exactly 14 MPI ranks are requested, with one computational thread per rank. "
        "The old attempt remains intact in its original campaign and scratch. "
        "No historical-operator checkpoint is reused. The 3–20 μm versus historical "
        "3.8–19 μm grid difference remains a comparison caveat.\n\n"
        "Authoritative status is in `campaign_state.json` and `manifest.csv`; "
        "checkpoint validation, preflight, logs, resource samples and final "
        "products are retained in this folder.\n",
        encoding="utf-8",
    )


def worker():
    state = json.loads(STATE.read_text(encoding="utf-8"))
    try:
        if sys.platform != "linux" or Path(sys.executable).resolve() != PYTHON.resolve():
            raise RuntimeError(f"Expected POSEIDON Python on Ubuntu; got {sys.executable}")
        if not MPIEXEC.is_file():
            raise FileNotFoundError(f"MPI launcher missing: {MPIEXEC}")
        if os.cpu_count() is None or os.cpu_count() < RANKS:
            raise RuntimeError(f"Fewer than {RANKS} logical CPUs are visible")
        if sha256(DATASET) != EXPECTED_DATASET_SHA256:
            raise RuntimeError("A3-100 h dataset hash changed")
        configuration = json.loads((OLD_CAMPAIGN / "resolved_configuration.json").read_text())
        if (configuration.get("dataset_sha256") != EXPECTED_DATASET_SHA256
                or configuration.get("n_live") != N_LIVE
                or configuration.get("R") != 10000
                or configuration.get("wl_min") != 3.0
                or configuration.get("wl_max") != 20.0
                or configuration.get("effective_free_dimension") != 14):
            raise RuntimeError("Source model/configuration differs from the frozen A3-100 h contract")
        copy_campaign_inputs()
        state.update(status="MIGRATING_SOURCE", supervisor_pid=os.getpid())
        record(state)
        checkpoint = stop_and_stage_checkpoint(state)
        selected_scope = json.loads((CAMPAIGN / "selected_scope.json").read_text())
        selected_scope["checkpoint_reuse"] = checkpoint.get("status") == "PASS"
        selected_scope["resume_source_replacements"] = checkpoint.get("replacements")
        selected_scope["resume_source_evaluations"] = checkpoint.get("evaluations")
        write_json(CAMPAIGN / "selected_scope.json", selected_scope)

        reuse = checkpoint.get("status") == "PASS"
        state.update(
            status="MPI14_PREFLIGHT",
            checkpoint_reuse=reuse,
            resume_from_replacements=checkpoint.get("replacements"),
            resume_from_evaluations=checkpoint.get("evaluations"),
            checkpoint_validation="checkpoint_validation.json",
            supervisor_pid=os.getpid(),
        )
        record(state)

        if not reuse:
            (SCRATCH / "run").mkdir(parents=True, exist_ok=True)
        preflight_dir = SCRATCH / "preflight_mpi14"
        operator_record = CAMPAIGN / "operator_preflight_mpi14.json"
        preflight_command = [
            *mpi_prefix(), str(PYTHON), "-u", str(MPI14_ADAPTER),
            *runner_arguments(operator_record, preflight_dir, True),
        ]
        write_json(CAMPAIGN / "preflight_command.json", preflight_command)
        return_code, peak_pss, min_available, samples = run_preflight(
            preflight_command, CAMPAIGN / "preflight_mpi14.log"
        )
        resource_gate = {
            "execution": "MPI14; one thread per rank",
            "logical_cpus_visible": os.cpu_count(),
            "peak_tree_pss_kib": peak_pss,
            "minimum_mem_available_kib": min_available,
            "required_mem_available_kib": peak_pss + RESERVE_KIB,
            "reserve_kib": RESERVE_KIB,
            "swap_after_preflight": swap_kib(),
            "status": "PASS" if min_available >= peak_pss + RESERVE_KIB else "FAIL",
            "sample_count": len(samples),
        }
        write_json(CAMPAIGN / "resource_gate_mpi14.json", resource_gate)
        if return_code != 0:
            raise RuntimeError(f"MPI14 corrected-bin preflight exited {return_code}")
        preflight = json.loads(operator_record.read_text(encoding="utf-8"))
        if preflight.get("status") != "PASS":
            raise RuntimeError("MPI14 operator callback preflight did not pass")
        verify_mpi_log(CAMPAIGN / "preflight_mpi14.log")
        if resource_gate["status"] != "PASS":
            raise RuntimeError(f"MPI14 memory gate failed: {resource_gate}")
        if active_science(excluded_pids=(os.getpid(),)):
            raise RuntimeError("A competing retrieval/MPI process appeared before sampling")

        command = [
            *mpi_prefix(), str(PYTHON), "-u", str(MPI14_ADAPTER),
        ]
        if reuse:
            command.append("--resume-matched-checkpoint")
        command.extend(runner_arguments(operator_record, SCRATCH / "run", False))
        write_json(CAMPAIGN / "sampling_command.json", command)
        row = {
            "run_id": RUN_ID, "scenario": "A3", "hours": 100,
            "operator": "corrected midpoint-edge photon overlap",
            "status": "RUNNING", "mpi_ranks": RANKS,
            "n_live": N_LIVE, "declared_dimension": 15,
            "effective_free_dimension": 14,
            "dataset_sha256": EXPECTED_DATASET_SHA256,
            "run_dir": str(SCRATCH / "run"),
            "archive_dir": str(CAMPAIGN / "products"),
            "log": str(CAMPAIGN / "retrieval.log"), "return_code": "",
        }
        write_manifest(row)
        state.update(status="RUNNING", preflight="PASS_MPI14",
                     mpi_ranks=RANKS, n_live=N_LIVE, run_id=RUN_ID,
                     run_pid=None, checkpoint_reuse=reuse,
                     start_utc=utc_now(), acceptance="PENDING")
        record(state)
        with (CAMPAIGN / "retrieval.log").open("x", encoding="utf-8") as stream:
            process = subprocess.Popen(
                command, cwd=ORIGINAL_ADAPTER.parent, env=environment(),
                stdout=stream, stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL, start_new_session=True,
            )
            state["run_pid"] = process.pid
            record(state)
            rank_deadline = time.time() + 300
            confirmed = False
            while process.poll() is None:
                tree = descendants(process.pid)
                rank_records = [item for item in tree
                                if str(MPI14_ADAPTER) in item["command"]
                                and "mpiexec" not in item["command"]
                                and "mpirun" not in item["command"]]
                if len(rank_records) == RANKS:
                    state.update(mpi_rank_pids=[item["pid"] for item in rank_records],
                                 mpi_rank_confirmation="14 rank processes observed",
                                 mpi_rank_confirmation_utc=utc_now())
                    record(state)
                    confirmed = True
                    break
                if time.time() > rank_deadline:
                    process.terminate()
                    process.wait(timeout=30)
                    raise RuntimeError(
                        f"Expected 14 MPI sampler ranks; observed {len(rank_records)}"
                    )
                time.sleep(2)
            if not confirmed and process.returncode is not None:
                raise RuntimeError(f"MPI14 sampler exited during startup: {process.returncode}")

            (CAMPAIGN / "resource_samples.jsonl").touch(exist_ok=True)
            while process.poll() is None:
                sample = resource_sample(process.pid)
                with (CAMPAIGN / "resource_samples.jsonl").open("a", encoding="utf-8") as metrics:
                    metrics.write(json.dumps(sample) + "\n")
                time.sleep(15)
            return_code = process.wait()

        row["return_code"] = return_code
        if return_code != 0:
            row["status"] = "FAILED"
            write_manifest(row)
            raise RuntimeError(f"MPI14 retrieval exited {return_code}; scratch preserved")
        source = SCRATCH / "run/POSEIDON_output/proxima_b_earthlike/retrievals"
        for folder in ("MultiNest_raw", "results", "samples"):
            if not (source / folder).is_dir():
                raise RuntimeError(f"Missing expected final output directory: {source / folder}")
        shutil.copytree(source, CAMPAIGN / "products")
        row["status"] = "COMPLETE_PENDING_VALIDATION"
        write_manifest(row)
        state.update(status="COMPLETE_PENDING_VALIDATION", exit_code=0,
                     products="products", acceptance="PENDING_INDEPENDENT_AUDIT",
                     scratch_preserved=True, end_utc=utc_now())
        record(state)
    except Exception as error:
        state.update(status="ACTION_REQUIRED", error=f"{type(error).__name__}: {error}",
                     scratch_preserved=True)
        record(state)
        traceback.print_exc()
        raise


def launch():
    if sys.platform != "linux":
        raise RuntimeError("Launch from Ubuntu/WSL inside the POSEIDON environment")
    if Path(sys.executable).resolve() != PYTHON.resolve():
        raise RuntimeError(f"Unexpected Python interpreter: {sys.executable}")
    if any(path.exists() for path in (CAMPAIGN, SCRATCH, SUPERVISOR_LOG, SUPERVISOR_PID)):
        raise RuntimeError("MPI14 campaign/scratch/log already exists; refusing duplication")
    if not OLD_CAMPAIGN.is_dir() or not OLD_SCRATCH.is_dir():
        raise FileNotFoundError("Serial source campaign or scratch is missing")
    CAMPAIGN.mkdir(parents=True)
    SCRATCH.mkdir(parents=True)
    (CAMPAIGN / "launch.lock").mkdir()
    initial = {
        "status": "MIGRATION_STARTING", "authorized_runs": 1,
        "scenario": "A3", "hours": 100,
        "dataset_sha256": EXPECTED_DATASET_SHA256,
        "mpi_ranks": RANKS, "n_live": N_LIVE,
        "acceptance": "PENDING", "scratch": str(SCRATCH),
        "operator": "corrected midpoint-edge photon overlap",
        "checkpoint_reuse": "validate exact active-run checkpoint before resume",
        "source_campaign": str(OLD_CAMPAIGN.relative_to(ROOT)),
        "created_utc": utc_now(),
    }
    record(initial)
    with SUPERVISOR_LOG.open("x", encoding="utf-8") as stream:
        process = subprocess.Popen(
            [str(PYTHON), "-u", str(Path(__file__).resolve()), "--worker"],
            cwd=ROOT, env=environment(), stdout=stream,
            stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
    SUPERVISOR_PID.write_text(str(process.pid) + "\n", encoding="utf-8")
    time.sleep(2)
    if process.poll() is not None:
        raise RuntimeError(f"MPI14 migration supervisor exited {process.returncode}; inspect its log")
    print(json.dumps({"supervisor_pid": process.pid,
                      "campaign_state": str(STATE),
                      "log": str(SUPERVISOR_LOG), "mpi_ranks": RANKS}), flush=True)


def retry_preflight_and_sampling():
    """Retry the failed MPI gate using the matching MPICH/Hydra launcher."""
    state = json.loads(STATE.read_text(encoding="utf-8"))
    checkpoint = json.loads((CAMPAIGN / "checkpoint_validation.json").read_text())
    old_state = json.loads((OLD_CAMPAIGN / "campaign_state.json").read_text())
    if state.get("status") != "ACTION_REQUIRED" or not state.get("checkpoint_reuse"):
        raise RuntimeError("Retry requires the preserved, validated MPI14 checkpoint campaign")
    if checkpoint.get("status") != "PASS":
        raise RuntimeError("Preserved MultiNest checkpoint did not pass validation")
    if old_state.get("status") != "STOPPED_BY_USER_MPI14_REBALANCE":
        raise RuntimeError("Serial source campaign is not recorded as stopped")
    if sha256(DATASET) != EXPECTED_DATASET_SHA256:
        raise RuntimeError("Dataset hash changed since the checkpoint snapshot")
    if active_science(excluded_pids=(os.getpid(),)):
        raise RuntimeError("A retrieval/MPI process is active; refusing a duplicate launch")

    staged_raw = (
        SCRATCH / "run/POSEIDON_output/proxima_b_earthlike/retrievals/MultiNest_raw"
    )
    for name, expected in checkpoint["hashes"].items():
        if sha256(staged_raw / name) != expected:
            raise RuntimeError(f"Preserved checkpoint changed after validation: {name}")
    if sha256(CAMPAIGN / "resolved_configuration.json") != sha256(
            OLD_CAMPAIGN / "resolved_configuration.json"):
        raise RuntimeError("Frozen configuration differs from the stopped serial campaign")

    retry_preflight_dir = SCRATCH / "preflight_mpi14_retry01"
    operator_record = CAMPAIGN / "operator_preflight_mpi14_retry01.json"
    preflight_log = CAMPAIGN / "preflight_mpi14_retry01.log"
    for path in (retry_preflight_dir, operator_record, preflight_log,
                 CAMPAIGN / "retrieval.log"):
        if path.exists():
            raise RuntimeError(f"Retry output already exists; refusing overwrite: {path}")

    state.pop("error", None)
    state.update(status="MPI14_PREFLIGHT_RETRY", supervisor_pid=os.getpid(),
                 last_preflight_error="Open MPI launcher incompatible with MPICH PMI1",
                 mpi_launcher=str(MPIEXEC), retry_attempt=1)
    record(state)
    command = [
        *mpi_prefix(), str(PYTHON), "-u", str(MPI14_ADAPTER),
        *runner_arguments(operator_record, retry_preflight_dir, True),
    ]
    write_json(CAMPAIGN / "preflight_mpi14_retry01_command.json", command)
    return_code, peak_pss, minimum_available, samples = run_preflight(
        command, preflight_log
    )
    resource_gate = {
        "execution": "MPICH/Hydra MPI14; one thread per rank",
        "logical_cpus_visible": os.cpu_count(),
        "peak_tree_pss_kib": peak_pss,
        "minimum_mem_available_kib": minimum_available,
        "required_mem_available_kib": peak_pss + RESERVE_KIB,
        "reserve_kib": RESERVE_KIB,
        "swap_after_preflight": swap_kib(),
        "status": "PASS" if minimum_available >= peak_pss + RESERVE_KIB else "FAIL",
        "sample_count": len(samples),
    }
    write_json(CAMPAIGN / "resource_gate_mpi14_retry01.json", resource_gate)
    if return_code != 0:
        raise RuntimeError(
            f"MPICH/Hydra MPI14 preflight exited {return_code}; see {preflight_log}"
        )
    preflight = json.loads(operator_record.read_text(encoding="utf-8"))
    if preflight.get("status") != "PASS":
        raise RuntimeError("MPICH/Hydra MPI14 operator callback preflight did not pass")
    verify_mpi_log(preflight_log)
    if resource_gate["status"] != "PASS":
        raise RuntimeError(f"MPI14 memory gate failed: {resource_gate}")
    if active_science(excluded_pids=(os.getpid(),)):
        raise RuntimeError("A competing retrieval/MPI process appeared before sampling")

    state.pop("error", None)
    state.update(status="RUNNING", preflight="PASS_MPI14_MPICH_HYDRA",
                 supervisor_pid=os.getpid(), run_pid=None,
                 preflight_log=str(preflight_log), mpi_launcher=str(MPIEXEC),
                 retry_preflight="PASS", start_utc=utc_now(), acceptance="PENDING")
    record(state)
    row = {
        "run_id": RUN_ID, "scenario": "A3", "hours": 100,
        "operator": "corrected midpoint-edge photon overlap",
        "status": "RUNNING", "mpi_ranks": RANKS,
        "n_live": N_LIVE, "declared_dimension": 15,
        "effective_free_dimension": 14,
        "dataset_sha256": EXPECTED_DATASET_SHA256,
        "run_dir": str(SCRATCH / "run"),
        "archive_dir": str(CAMPAIGN / "products"),
        "log": str(CAMPAIGN / "retrieval.log"), "return_code": "",
    }
    write_manifest(row)
    command = [*mpi_prefix(), str(PYTHON), "-u", str(MPI14_ADAPTER),
               "--resume-matched-checkpoint"]
    command.extend(runner_arguments(operator_record, SCRATCH / "run", False))
    write_json(CAMPAIGN / "sampling_command.json", command)
    with (CAMPAIGN / "retrieval.log").open("x", encoding="utf-8") as stream:
        process = subprocess.Popen(
            command, cwd=ORIGINAL_ADAPTER.parent, env=environment(),
            stdout=stream, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL, start_new_session=True,
        )
        state.update(run_pid=process.pid, start_utc=utc_now())
        record(state)
        rank_deadline = time.time() + 300
        rank_records = []
        while process.poll() is None:
            tree = descendants(process.pid)
            rank_records = [item for item in tree
                            if str(MPI14_ADAPTER) in item["command"]
                            and "mpiexec" not in item["command"]
                            and "mpirun" not in item["command"]]
            if len(rank_records) == RANKS:
                state.update(mpi_rank_pids=[item["pid"] for item in rank_records],
                             mpi_rank_confirmation="14 rank processes observed",
                             mpi_rank_confirmation_utc=utc_now())
                record(state)
                break
            if time.time() > rank_deadline:
                process.terminate()
                process.wait(timeout=30)
                raise RuntimeError(
                    f"Expected 14 MPI sampler ranks; observed {len(rank_records)}"
                )
            time.sleep(2)
        if process.poll() is not None:
            raise RuntimeError(f"MPI14 sampler exited during startup: {process.returncode}")

        (CAMPAIGN / "resource_samples.jsonl").touch(exist_ok=True)
        while process.poll() is None:
            sample = resource_sample(process.pid)
            with (CAMPAIGN / "resource_samples.jsonl").open("a", encoding="utf-8") as metrics:
                metrics.write(json.dumps(sample) + "\n")
            time.sleep(15)
        return_code = process.wait()
    row["return_code"] = return_code
    if return_code != 0:
        row["status"] = "FAILED"
        write_manifest(row)
        raise RuntimeError(f"MPI14 retrieval exited {return_code}; scratch preserved")
    source = SCRATCH / "run/POSEIDON_output/proxima_b_earthlike/retrievals"
    for folder in ("MultiNest_raw", "results", "samples"):
        if not (source / folder).is_dir():
            raise RuntimeError(f"Missing expected final output directory: {source / folder}")
    shutil.copytree(source, CAMPAIGN / "products")
    row["status"] = "COMPLETE_PENDING_VALIDATION"
    write_manifest(row)
    state.pop("error", None)
    state.update(status="COMPLETE_PENDING_VALIDATION", exit_code=0,
                 products="products", acceptance="PENDING_INDEPENDENT_AUDIT",
                 scratch_preserved=True, end_utc=utc_now())
    record(state)


def launch_retry():
    if any(path.exists() for path in (RETRY_LOG, RETRY_PID)):
        raise RuntimeError("MPI14 retry supervisor artifacts already exist; refusing overwrite")
    if active_science():
        raise RuntimeError("A retrieval/MPI process is active; refusing a duplicate retry")
    with RETRY_LOG.open("x", encoding="utf-8") as stream:
        process = subprocess.Popen(
            [str(PYTHON), "-u", str(Path(__file__).resolve()), "--retry-worker"],
            cwd=ROOT, env=environment(), stdout=stream,
            stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
    RETRY_PID.write_text(str(process.pid) + "\n", encoding="utf-8")
    time.sleep(2)
    if process.poll() is not None:
        raise RuntimeError(
            f"MPI14 retry supervisor exited {process.returncode}; inspect {RETRY_LOG}"
        )
    print(json.dumps({"supervisor_pid": process.pid,
                      "campaign_state": str(STATE),
                      "log": str(RETRY_LOG), "mpi_ranks": RANKS,
                      "launcher": str(MPIEXEC)}), flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        worker()
    elif len(sys.argv) > 1 and sys.argv[1] == "--retry-worker":
        try:
            retry_preflight_and_sampling()
        except Exception as error:
            state = json.loads(STATE.read_text(encoding="utf-8"))
            state.update(status="ACTION_REQUIRED",
                         error=f"{type(error).__name__}: {error}",
                         scratch_preserved=True)
            record(state)
            traceback.print_exc()
            raise
    elif len(sys.argv) > 1 and sys.argv[1] == "--retry":
        launch_retry()
    else:
        launch()
