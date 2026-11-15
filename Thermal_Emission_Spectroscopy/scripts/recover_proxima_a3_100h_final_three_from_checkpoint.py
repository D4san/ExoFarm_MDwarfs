#!/usr/bin/env python3
"""Resume only the three interrupted A3-100 h LOO runs from their own MultiNest checkpoints."""
from __future__ import annotations

import argparse
import csv
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path('/mnt/c/Proyectos/Astro/ExoFarm_MDwarfs')
CAMPAIGN = ROOT / 'Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a1_a3_corrected_binning_matrix_loo_20261021_r01'
RECOVERY = CAMPAIGN / 'recovery_20261027_power_restore_r01'
SCRATCH = Path('/home/dasan/exofarm_a1_a3_corrected_binning_matrix_20261021_r01')
SNAPSHOTS = SCRATCH / 'recovery_20261027_power_restore_r01/checkpoint_snapshots'
SCRIPTS = ROOT / 'Thermal_Emission_Spectroscopy/scripts'
WORKER_SCRIPT = Path(__file__).resolve()
STATE_PATH = CAMPAIGN / 'campaign_state.json'
MANIFEST_PATH = CAMPAIGN / 'manifest.csv'
RECOVERY_STATE_PATH = RECOVERY / 'recovery_state.json'
TARGET_IDS = ('A3_100h_no_CO2', 'A3_100h_no_CH4', 'A3_100h_no_O3')
NEW_FIELDS = (
    'recovery_attempt', 'recovery_start_utc', 'recovery_end_utc',
    'recovery_return_code', 'recovery_resume_checkpoint',
)
MIN_MEM_GIB = 24
MIN_SWAP_FREE_GIB = 2
MIN_DISK_GIB = 80
MIB = 1024 * 1024

sys.path.insert(0, str(SCRIPTS))
import launch_proxima_a1_a3_corrected_binning_matrix_loo as campaign  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    os.replace(temp, path)


def read_manifest() -> tuple[list[dict], list[str]]:
    with MANIFEST_PATH.open(newline='', encoding='utf-8') as stream:
        reader = csv.DictReader(stream)
        return list(reader), list(reader.fieldnames or [])


def write_manifest(rows: list[dict], fields: list[str]) -> None:
    for field in NEW_FIELDS:
        if field not in fields:
            fields.append(field)
    temp = MANIFEST_PATH.with_suffix('.csv.tmp')
    with temp.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temp, MANIFEST_PATH)


def append_jsonl(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(value, sort_keys=True) + '\n')
        stream.flush()
        os.fsync(stream.fileno())


def resource_snapshot() -> dict:
    base = campaign.resource_snapshot()
    return {
        **base,
        'mem_available_gib': base['mem_available_kib'] / MIB,
        'swap_free_gib': base['swap_free_kib'] / MIB,
    }


def resource_gate(snapshot: dict) -> list[str]:
    problems = []
    if snapshot['logical_cpus'] < campaign.MIN_LOGICAL_CPUS:
        problems.append(f"logical CPUs {snapshot['logical_cpus']} < {campaign.MIN_LOGICAL_CPUS}")
    if snapshot['mem_available_kib'] < MIN_MEM_GIB * MIB:
        problems.append(f"available RAM {snapshot['mem_available_gib']:.1f} GiB < {MIN_MEM_GIB} GiB")
    if snapshot['swap_free_kib'] < MIN_SWAP_FREE_GIB * MIB:
        problems.append(f"free swap {snapshot['swap_free_gib']:.1f} GiB < {MIN_SWAP_FREE_GIB} GiB")
    if snapshot['project_disk_free_gib'] < MIN_DISK_GIB:
        problems.append(f"project disk {snapshot['project_disk_free_gib']} GiB < {MIN_DISK_GIB} GiB")
    if snapshot['scratch_disk_free_gib'] < MIN_DISK_GIB:
        problems.append(f"scratch disk {snapshot['scratch_disk_free_gib']} GiB < {MIN_DISK_GIB} GiB")
    return problems


def checkpoint_info(case: dict) -> dict:
    run_dir = Path(case['run_dir'])
    raw = run_dir / 'POSEIDON_output/proxima_b_earthlike/retrievals/MultiNest_raw'
    model = case['model_name']
    required = [
        raw / f'{model}-resume.dat', raw / f'{model}-live.points',
        raw / f'{model}-phys_live.points', raw / f'{model}-ev.dat',
        raw / f'{model}-post_equal_weights.dat', raw / f'{model}-.txt',
        raw / f'{model}-stats.dat', raw / f'{model}-summary.txt',
    ]
    missing = [str(path) for path in required if not path.is_file() or path.stat().st_size == 0]
    if missing:
        raise RuntimeError(f"Incomplete MultiNest checkpoint/product set for {case['run_id']}: {missing}")
    lines = required[0].read_text(encoding='utf-8', errors='replace').splitlines()
    if len(lines) < 2:
        raise RuntimeError(f"Malformed resume.dat for {case['run_id']}")
    numbers = [float(value) for value in lines[1].split()]
    if len(numbers) < 4 or not all(map(lambda x: x == x and abs(x) != float('inf'), numbers[:4])):
        raise RuntimeError(f"Non-finite or malformed resume.dat counters for {case['run_id']}")
    replacements, evaluations, mode_count, live_points = map(int, numbers[:4])
    if replacements <= 0 or evaluations <= replacements or live_points != 800:
        raise RuntimeError(f"Checkpoint counters/live-point count mismatch for {case['run_id']}: {numbers[:4]}")
    return {
        'run_dir': str(run_dir),
        'model_name': model,
        'resume_file': str(required[0]),
        'replacements': replacements,
        'evaluations': evaluations,
        'mode_count': mode_count,
        'n_live': live_points,
        'files': {path.name: {'bytes': path.stat().st_size, 'sha256': sha256(path)} for path in required},
    }


def validate_frozen_inputs(rows_by_id: dict[str, dict], cases_by_id: dict[str, dict],
                           run_ids: list[str]) -> dict:
    selected = json.loads((CAMPAIGN / 'selected_scope.json').read_text(encoding='utf-8'))
    preserved = json.loads((CAMPAIGN / 'preserved_inputs.json').read_text(encoding='utf-8'))
    current_operator_hash = sha256(campaign.OPERATOR_SOURCE)
    current_runner_hash = sha256(campaign.RUNNER)
    if selected.get('operator_source_sha256') != current_operator_hash:
        raise RuntimeError('Corrected-bin operator source hash differs from the frozen campaign')
    if preserved.get('runner_sha256') != current_runner_hash:
        raise RuntimeError('Retrieval runner hash differs from the frozen campaign')
    if preserved.get('operator_source_sha256') != current_operator_hash:
        raise RuntimeError('Preserved-input operator hash differs from the frozen campaign')
    datasets = campaign.check_dataset_inputs()
    check = {'operator_source_sha256': current_operator_hash, 'runner_sha256': current_runner_hash,
             'datasets': datasets, 'runs': {}}
    for run_id in run_ids:
        row = rows_by_id[run_id]
        case = cases_by_id[run_id]
        dataset = ROOT / row['dataset_rel']
        actual_dataset_hash = sha256(dataset)
        if actual_dataset_hash != row['dataset_sha256_expected']:
            raise RuntimeError(f'Dataset hash mismatch for {run_id}: {actual_dataset_hash}')
        config_path = ROOT / row['configuration_json']
        resolved = campaign.validate_resolved_config(
            config_path, row['scenario'], int(row['hours']), row['excluded_species'] or None)
        if row['run_dir'] != case['run_dir'] or row['model_name'] != case['model_name'] or row['output_tag'] != case['output_tag']:
            raise RuntimeError(f'Frozen run identity/path mismatch for {run_id}')
        preflight = json.loads((ROOT / row['operator_preflight']).read_text(encoding='utf-8'))
        runtime = json.loads((ROOT / row['operator_runtime']).read_text(encoding='utf-8'))
        for record_name, record in [('preflight', preflight), ('runtime', runtime)]:
            if record.get('status') != 'PASS' or record.get('actual_poseidon_callback_bound') is not True:
                raise RuntimeError(f'{record_name} operator record no longer passes for {run_id}')
            if record.get('dataset_sha256') != actual_dataset_hash or record.get('operator_source_sha256') != current_operator_hash:
                raise RuntimeError(f'{record_name} operator binding/hash mismatch for {run_id}')
        checkpoint = checkpoint_info(case)
        if (ROOT / row['archive_dir']).exists():
            raise RuntimeError(f'Archive already exists; refusing to overwrite {row["archive_dir"]}')
        check['runs'][run_id] = {
            'dataset_sha256': actual_dataset_hash,
            'resolved_config_sha256': sha256(config_path),
            'declared_dimension': resolved['declared_dimension'],
            'effective_free_dimension': resolved['effective_free_dimension'],
            'species': resolved['param_species'],
            'operator_preflight_sha256': sha256(ROOT / row['operator_preflight']),
            'operator_runtime_before_recovery_sha256': sha256(ROOT / row['operator_runtime']),
            'checkpoint': checkpoint,
        }
    return check


def make_worker_command(run_id: str, attempt: int, row: dict) -> list[str]:
    python = Path('/home/dasan/anaconda3/envs/POSEIDON/bin/python')
    mpiexec = Path('/home/dasan/anaconda3/envs/POSEIDON/bin/mpiexec')
    if not python.is_file() or not mpiexec.is_file():
        raise FileNotFoundError('POSEIDON python/mpiexec is unavailable')
    operator_record = RECOVERY / f'attempt_{attempt:02d}/runtime_operators/{run_id}.json'
    args = [
        str(python), '-u', str(WORKER_SCRIPT), '--worker', run_id,
        '--operator-record', str(operator_record),
        '--campaign', 'proxima', '--scenario', row['scenario'], '--hours', row['hours'],
        '--n-live', '800', '--error-inflation', 'none', '--surface-pressure-mode', 'fixed-black',
        '--include-o2', '--x-profile', 'isochem', '--output-tag', row['output_tag'],
        '--R', '10000', '--wl-min', '3.0', '--wl-max', '20.0',
        '--dataset-file', str(ROOT / row['dataset_rel']), '--run-dir', row['run_dir'],
        '--configuration-json', str(ROOT / row['configuration_json']),
        '--exclude-species', row['excluded_species'], '--resume',
    ]
    return [str(mpiexec), '-n', str(campaign.RANKS_PER_RUN), *args]


def validate_completed(case: dict, run_id: str, operator_record: Path, log_path: Path) -> dict:
    raw = Path(case['run_dir']) / 'POSEIDON_output/proxima_b_earthlike/retrievals/MultiNest_raw'
    posterior = raw / f"{case['model_name']}-post_equal_weights.dat"
    if not posterior.is_file() or posterior.stat().st_size == 0:
        raise RuntimeError(f'Completed retrieval has no posterior: {posterior}')
    import numpy as np
    samples = np.loadtxt(posterior)
    if samples.ndim != 2 or samples.shape[0] < 2 or not np.isfinite(samples).all():
        raise RuntimeError(f'Posterior is empty/non-finite after resume for {run_id}: {samples.shape}')
    required_suffixes = ('-summary.txt', '-stats.dat', '-ev.dat', '-resume.dat')
    for suffix in required_suffixes:
        path = raw / f"{case['model_name']}{suffix}"
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f'Missing final MultiNest product for {run_id}: {path}')
    record = json.loads(operator_record.read_text(encoding='utf-8'))
    if record.get('status') != 'PASS' or record.get('actual_poseidon_callback_bound') is not True or record.get('mpi_size') != 4:
        raise RuntimeError(f'Corrected-bin callback/operator record failed for {run_id}')
    if not record.get('resume_checkpoint') or record.get('stage') != 'sampling_resume':
        raise RuntimeError(f'Resume provenance missing in operator record for {run_id}')
    log = log_path.read_text(encoding='utf-8', errors='replace')
    if '[operator-postprocessing-complete]' not in log:
        raise RuntimeError(f'Postprocessing binding marker missing for {run_id}')
    return {'posterior_rows': int(samples.shape[0]), 'posterior_columns': int(samples.shape[1]),
            'all_finite': True, 'posterior_sha256': sha256(posterior),
            'operator_record_sha256': sha256(operator_record)}


def worker_entry() -> None:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--worker', required=True)
    parser.add_argument('--operator-record', required=True)
    options, arguments = parser.parse_known_args()
    run_id = options.worker
    if run_id not in TARGET_IDS or arguments.count('--resume') != 1 or '--setup-only' in arguments:
        raise RuntimeError('Worker is restricted to the three interrupted A3-100 h checkpoint continuations')
    operator_record = Path(options.operator_record).resolve()
    attempt_dir = operator_record.parents[1]
    if operator_record != (attempt_dir / 'runtime_operators' / f'{run_id}.json').resolve():
        raise RuntimeError('Recovery operator record escaped its attempt directory')
    sys.path.insert(0, str(SCRIPTS))
    import run_life_retrieval_a1_a3_corrected_matrix as retrieval
    original_parse = retrieval.parse_scope
    expected_original_record = (CAMPAIGN / 'runtime/operators' / f'{run_id}.json').resolve()

    def parse_recovery_scope(values: list[str], supplied_record: Path):
        if supplied_record.resolve() != operator_record:
            raise RuntimeError('Worker supplied an unexpected recovery operator record')
        if values.count('--resume') != 1:
            raise RuntimeError('Only a saved same-run MultiNest checkpoint may be resumed')
        parsed = original_parse([value for value in values if value != '--resume'], expected_original_record)
        if parsed[-1] != run_id or parsed[2] != {'A3_100h_no_CO2': 'CO2', 'A3_100h_no_CH4': 'CH4', 'A3_100h_no_O3': 'O3'}[run_id]:
            raise RuntimeError('Worker model identity differs from the interrupted run')
        return parsed

    original_validate = retrieval.validate_operator

    def validate_recovery_operator(scenario: str, hours: int, excluded: str | None, dataset: Path, record_path: Path):
        operator, record = original_validate(scenario, hours, excluded, dataset, record_path)
        if retrieval.MPI.COMM_WORLD.rank == 0:
            saved = json.loads(record_path.read_text(encoding='utf-8'))
            saved['stage'] = 'sampling_resume'
            saved['resume_checkpoint'] = True
            saved['recovery_attempt'] = int(attempt_dir.name.split('_')[-1])
            saved['recovery_source_campaign'] = str(CAMPAIGN)
            write_json(record_path, saved)
        return operator, record

    retrieval.parse_scope = parse_recovery_scope
    retrieval.validate_operator = validate_recovery_operator
    sys.argv = [sys.argv[0], '--operator-record', str(operator_record), *arguments]
    retrieval.main()


def supervisor_main() -> int:
    if sys.platform != 'linux':
        raise RuntimeError('Recovery supervisor must run inside Ubuntu/WSL')
    if not STATE_PATH.is_file() or not MANIFEST_PATH.is_file():
        raise FileNotFoundError('Original campaign state/manifest missing')
    lock_root = RECOVERY
    if RECOVERY_STATE_PATH.exists():
        prior_recovery = json.loads(RECOVERY_STATE_PATH.read_text(encoding='utf-8'))
        if prior_recovery.get('status') not in {'INTERRUPTED', 'RUNNING'}:
            raise RuntimeError(f"Prior recovery is terminal ({prior_recovery.get('status')}); review before another attempt")
        old_pid = int(prior_recovery.get('supervisor_pid') or 0)
        if old_pid and Path(f'/proc/{old_pid}').exists():
            raise RuntimeError(f'Prior recovery supervisor {old_pid} is still alive')
        attempt = int(prior_recovery.get('attempt', 0)) + 1
    else:
        attempt = 1
        RECOVERY.mkdir(parents=True, exist_ok=False)
        shutil.copy2(STATE_PATH, RECOVERY / 'campaign_state.before.json')
        shutil.copy2(MANIFEST_PATH, RECOVERY / 'manifest.before.csv')
    (RECOVERY / f'attempt_{attempt:02d}').mkdir(parents=True, exist_ok=False)
    attempt_dir = RECOVERY / f'attempt_{attempt:02d}'
    (attempt_dir / 'runtime_operators').mkdir(parents=True)
    (attempt_dir / 'launch_logs').mkdir(parents=True)
    (attempt_dir / 'launch_records').mkdir(parents=True)
    lock_handle = (RECOVERY / 'supervisor.lock').open('a+', encoding='utf-8')
    fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    state = json.loads(STATE_PATH.read_text(encoding='utf-8'))
    rows, fields = read_manifest()
    rows_by_id = {row['run_id']: row for row in rows}
    if set(TARGET_IDS) - set(rows_by_id):
        raise RuntimeError('One or more target run IDs are absent from the original manifest')
    current_processes = campaign.foreign_sampler_processes()
    if current_processes:
        raise RuntimeError('Existing MPI/retrieval process detected; refusing duplicate launch: ' + ' | '.join(current_processes))
    if len(rows) != 33 or state.get('authorized_run_count') != 33:
        raise RuntimeError('Original frozen 33-run campaign manifest/state mismatch')
    if state.get('checkpoint_reuse') is not False:
        raise RuntimeError('Unexpected campaign checkpoint policy; stopping for review')
    completed = [row for row in rows if row['status'] == 'complete_pending_validation' and row['return_code'] == '0']
    if len(completed) != 30:
        raise RuntimeError(f'Expected 30 preserved exit-0 runs; found {len(completed)}')
    active = [run_id for run_id in TARGET_IDS
              if rows_by_id[run_id]['status'] != 'complete_pending_validation']
    if not active:
        raise RuntimeError('All target rows are already complete; no retrievals to launch')
    retryable_statuses = {'sampling', 'recovery_sampling'}
    blocked = {run_id: rows_by_id[run_id]['status'] for run_id in active
               if rows_by_id[run_id]['status'] not in retryable_statuses}
    if blocked:
        raise RuntimeError(f'Incomplete retrievals have non-retryable manifest states: {blocked}')

    cases_by_id = {case['run_id']: case for case in campaign.build_cases()}
    frozen_check = validate_frozen_inputs(rows_by_id, cases_by_id, active)
    resource = resource_snapshot()
    problems = resource_gate(resource)
    if problems:
        raise RuntimeError('Resource gate failed: ' + '; '.join(problems))
    state_snapshot = {run_id: checkpoint_info(cases_by_id[run_id]) for run_id in active}

    snapshot_dir = SNAPSHOTS / f'attempt_{attempt:02d}'
    snapshot_dir.mkdir(parents=True, exist_ok=False)
    for run_id in active:
        shutil.copytree(Path(cases_by_id[run_id]['run_dir']), snapshot_dir / run_id)
    snapshot_hashes = {}
    for run_id in active:
        snapshot_hashes[run_id] = checkpoint_info_from_snapshot(snapshot_dir / run_id, cases_by_id[run_id]['model_name'])
        for name, item in state_snapshot[run_id]['files'].items():
            if snapshot_hashes[run_id]['files'][name]['sha256'] != item['sha256']:
                raise RuntimeError(f'Checkpoint changed while snapshotting {run_id}/{name}')

    recovery_state = json.loads(RECOVERY_STATE_PATH.read_text(encoding='utf-8')) if RECOVERY_STATE_PATH.exists() else {
        'campaign_id': state['campaign_id'], 'created_utc': utc_now(),
        'original_campaign_status_at_interruption': state.get('campaign_status'),
        'initial_target_run_ids': list(TARGET_IDS), 'status': 'INTERRUPTED', 'attempt': 0,
    }
    recovery_state.update({
        'status': 'RUNNING', 'attempt': attempt, 'supervisor_pid': os.getpid(),
        'started_utc': utc_now(), 'active_run_ids': list(active),
        'resume_from_same_run_multinest_checkpoint': True,
        'checkpoint_snapshots': str(snapshot_dir), 'checkpoint_snapshot_hashes': snapshot_hashes,
        'frozen_input_verification': frozen_check, 'resource_gate': resource,
        'max_parallel_retrievals': 3, 'ranks_per_retrieval': 4, 'total_mpi_ranks': 12,
        'pre_interruption_checkpoint_counters': state_snapshot,
    })
    write_json(RECOVERY_STATE_PATH, recovery_state)
    state.update({
        'campaign_status': f'RECOVERY_RUNNING_WAVE_11_ATTEMPT_{attempt:02d}',
        'supervisor_pid': os.getpid(), 'active_run_ids': list(active),
        'recovery_attempt': attempt, 'recovery_started_utc': utc_now(),
        'recovery_mode': 'resume_each_interrupted_retrieval_from_its_own_MultiNest_checkpoint',
        'recovery_checkpoint_snapshot': str(snapshot_dir),
        'recovery_exit_code': None,
    })
    write_json(STATE_PATH, state)

    for run_id in active:
        row = rows_by_id[run_id]
        row['status'] = 'recovery_sampling'
        row['recovery_attempt'] = str(attempt)
        row['recovery_start_utc'] = utc_now()
        row['recovery_end_utc'] = ''
        row['recovery_return_code'] = ''
        row['recovery_resume_checkpoint'] = 'true'
        row['error'] = ''
        write_manifest(rows, fields)

    env = os.environ.copy()
    env.update({
        'POSEIDON_input_data': '/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs',
        'PYSYN_CDBS': '/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids',
        'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1',
        'NUMEXPR_NUM_THREADS': '1', 'PYTHONUNBUFFERED': '1',
    })
    running = {}
    for run_id in active:
        row = rows_by_id[run_id]
        log_path = attempt_dir / 'launch_logs' / f'{run_id}.log'
        record_path = attempt_dir / 'launch_records' / f'{run_id}.json'
        operator_path = attempt_dir / 'runtime_operators' / f'{run_id}.json'
        command = make_worker_command(run_id, attempt, row)
        record = {
            'run_id': run_id, 'attempt': attempt, 'started_utc': utc_now(),
            'resume_checkpoint': True, 'checkpoint_before_resume': state_snapshot[run_id],
            'command': command, 'dataset_sha256': row['dataset_sha256_expected'],
            'resolved_configuration_sha256': frozen_check['runs'][run_id]['resolved_config_sha256'],
            'operator_source_sha256': frozen_check['operator_source_sha256'],
            'operator_record': str(operator_path), 'log': str(log_path),
            'mpi_ranks': 4, 'threads_per_rank': 1,
        }
        write_json(record_path, record)
        with log_path.open('x', encoding='utf-8') as log:
            log.write(f'[recovery_start_utc] {utc_now()}\n[run_id] {run_id}\n[attempt] {attempt}\n'
                      f'[resume_checkpoint] true\n[mpi_ranks] 4\n[command] {json.dumps(command)}\n')
            log.flush()
            try:
                process = subprocess.Popen(command, cwd=str(ROOT), env=env, stdout=log,
                                           stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                           start_new_session=True)
            except Exception as exc:
                row['status'] = 'recovery_failed_to_start'
                row['error'] = f'{type(exc).__name__}: {exc}'
                row['recovery_return_code'] = 'spawn_error'
                row['recovery_end_utc'] = utc_now()
                recovery_state.setdefault('run_results', {})[run_id] = {
                    'status': 'FAILED_TO_START', 'error': row['error'], 'attempt': attempt,
                }
                continue
        row['pid'] = str(process.pid)
        record['pid'] = process.pid
        write_json(record_path, record)
        running[run_id] = (cases_by_id[run_id], process, time.monotonic(), log_path, operator_path)
        write_manifest(rows, fields)
        print(f'[recovery launched] {run_id} MPI4 pid={process.pid} resume=true', flush=True)

    recovery_state['active_run_ids'] = list(running)
    recovery_state['status'] = 'RUNNING' if running else 'FAILED_TO_START'
    write_json(RECOVERY_STATE_PATH, recovery_state)
    state['active_run_ids'] = list(running)
    state['campaign_status'] = f'RECOVERY_RUNNING_WAVE_11_ATTEMPT_{attempt:02d}' if running else 'RECOVERY_HALTED_FAILURE'
    write_json(STATE_PATH, state)

    resource_path = CAMPAIGN / 'resources.jsonl'
    recovery_resources = RECOVERY / 'resource_samples.jsonl'
    last_sample = 0.0
    failure = False
    try:
        while running:
            current = time.monotonic()
            if current - last_sample >= 60:
                telemetry = campaign.resource_sample({
                    run_id: (case, process, started)
                    for run_id, (case, process, started, _, _) in running.items()
                })
                telemetry['recovery_attempt'] = attempt
                telemetry['sampling_mode'] = 'same_run_checkpoint_resume'
                append_jsonl(resource_path, telemetry)
                append_jsonl(recovery_resources, telemetry)
                for run_id, (case, _, _, _, _) in running.items():
                    counters = telemetry.get('cases', {}).get(run_id, {})
                    row = rows_by_id[run_id]
                    for key in ('replacements', 'evaluations', 'posterior_rows'):
                        if counters.get(key) is not None:
                            row[key] = str(counters[key])
                recovery_state['latest_resources'] = telemetry
                write_manifest(rows, fields)
                write_json(RECOVERY_STATE_PATH, recovery_state)
                last_sample = current
            for run_id, (case, process, started, log_path, operator_path) in list(running.items()):
                return_code = process.poll()
                if return_code is None:
                    continue
                row = rows_by_id[run_id]
                row['recovery_return_code'] = str(return_code)
                row['recovery_end_utc'] = utc_now()
                if return_code == 0:
                    try:
                        products = validate_completed(case, run_id, operator_path, log_path)
                        archive = ROOT / row['archive_dir']
                        if archive.exists():
                            raise FileExistsError(f'Refusing to overwrite archive {archive}')
                        shutil.copytree(Path(row['run_dir']), archive, symlinks=True)
                        row['status'] = 'complete_pending_validation'
                        row['return_code'] = '0'
                        row['end_utc'] = utc_now()
                        row['elapsed_seconds'] = f'{time.monotonic() - started:.1f}'
                        row['posterior_rows'] = str(products['posterior_rows'])
                        row['preliminary_acceptance'] = 'RETURN_CODE_0_RESUMED_PRODUCTS_ARCHIVED; FINAL_AUDIT_PENDING'
                        row['error'] = ''
                        recovery_state.setdefault('run_results', {})[run_id] = {
                            'status': 'COMPLETE_PENDING_INDEPENDENT_AUDIT', 'return_code': 0,
                            'finished_utc': utc_now(), 'products': products,
                            'archive_dir': row['archive_dir'], 'elapsed_seconds': row['elapsed_seconds'],
                        }
                        print(f'[recovery completed+archived] {run_id}; audit pending', flush=True)
                    except Exception as exc:
                        failure = True
                        row['status'] = 'recovery_product_gate_failed'
                        row['error'] = f'{type(exc).__name__}: {exc}'
                        recovery_state.setdefault('run_results', {})[run_id] = {
                            'status': 'PRODUCT_GATE_FAILED', 'return_code': 0,
                            'error': row['error'], 'finished_utc': utc_now(),
                        }
                        print(f'[recovery product gate failed] {run_id}: {row["error"]}', file=sys.stderr, flush=True)
                else:
                    failure = True
                    row['status'] = 'recovery_failed'
                    row['error'] = f'MPI4 checkpoint-resume retrieval exit {return_code}; scratch/logs preserved'
                    recovery_state.setdefault('run_results', {})[run_id] = {
                        'status': 'FAILED', 'return_code': return_code,
                        'error': row['error'], 'finished_utc': utc_now(),
                        'log': str(log_path), 'scratch_run_dir': row['run_dir'],
                    }
                    print(f'[recovery failed] {run_id} exit={return_code}; {log_path}', file=sys.stderr, flush=True)
                write_manifest(rows, fields)
                running.pop(run_id)
                recovery_state['active_run_ids'] = list(running)
                write_json(RECOVERY_STATE_PATH, recovery_state)
                state['active_run_ids'] = list(running)
                write_json(STATE_PATH, state)
            if running:
                time.sleep(20)
    except BaseException as exc:
        failure = True
        recovery_state['supervisor_exception'] = f'{type(exc).__name__}: {exc}'
        raise
    finally:
        failed_rows = [run_id for run_id in TARGET_IDS if rows_by_id[run_id]['status'] != 'complete_pending_validation']
        final_status = 'COMPLETE_PENDING_INDEPENDENT_AUDIT' if not failed_rows and not failure else 'HALTED_FAILURE'
        recovery_state.update({
            'status': final_status, 'ended_utc': utc_now(), 'active_run_ids': [],
            'incomplete_or_failed_run_ids': failed_rows,
            'supervisor_exit_code': 2 if final_status == 'HALTED_FAILURE' else 0,
        })
        write_json(RECOVERY_STATE_PATH, recovery_state)
        state.update({
            'campaign_status': 'RECOVERY_COMPLETE_PENDING_INDEPENDENT_AUDIT' if final_status != 'HALTED_FAILURE' else 'RECOVERY_HALTED_FAILURE',
            'active_run_ids': [], 'supervisor_exit_code': 0 if final_status != 'HALTED_FAILURE' else 2,
            'recovery_exit_code': 0 if final_status != 'HALTED_FAILURE' else 2,
            'recovery_ended_utc': utc_now(), 'recovery_incomplete_run_ids': failed_rows,
            'acceptance': 'PENDING_INDEPENDENT_AUDIT' if final_status != 'HALTED_FAILURE' else 'RECOVERY_FAILED_REQUIRES_REVIEW',
        })
        write_json(STATE_PATH, state)
        lock_handle.close()
    return 2 if final_status == 'HALTED_FAILURE' else 0


def checkpoint_info_from_snapshot(run_dir: Path, model_name: str) -> dict:
    raw = run_dir / 'POSEIDON_output/proxima_b_earthlike/retrievals/MultiNest_raw'
    files = [f'{model_name}-resume.dat', f'{model_name}-live.points', f'{model_name}-phys_live.points',
             f'{model_name}-ev.dat', f'{model_name}-post_equal_weights.dat', f'{model_name}-.txt',
             f'{model_name}-stats.dat', f'{model_name}-summary.txt']
    info = {}
    for name in files:
        path = raw / name
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f'Checkpoint snapshot is missing {path}')
        info[name] = {'bytes': path.stat().st_size, 'sha256': sha256(path)}
    return {'run_dir': str(run_dir), 'files': info}


def main() -> int:
    if '--worker' in sys.argv:
        worker_entry()
        return 0
    return supervisor_main()


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f'[RECOVERY_ERROR] {type(exc).__name__}: {exc}', file=sys.stderr, flush=True)
        raise SystemExit(2)
