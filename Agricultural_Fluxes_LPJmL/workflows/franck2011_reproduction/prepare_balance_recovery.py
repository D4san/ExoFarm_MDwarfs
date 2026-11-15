"""Prepare an isolated LPJmL 6.0.6 checkpoint balance regression in WSL."""
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path('/home/dasan/exofarm-lpjml-runtime')
SOURCE = ROOT / 'LPJmL-6.0.6'
BUILD = ROOT / 'LPJmL-6.0.6-balance-fix-20260912'
CAMPAIGN = Path('/home/dasan/exofarm-lpjml-runs/global_a1_checkpoints_20260909')
TEST = Path('/home/dasan/exofarm-lpjml-runs/balance_recovery_20260912')
EXPECTED = 'd4b276cd3f65732a50e1d818dca0681935d2debf0d3abbce727fcf2d430117d5'


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def main():
    if BUILD.exists() or TEST.exists():
        raise RuntimeError('Preparation already exists; inspect before reuse.')
    checkpoint = CAMPAIGN / 'spinup_natural/restart/checkpoint.lpj'
    assert digest(checkpoint) == EXPECTED
    shutil.copytree(SOURCE, BUILD, symlinks=True)
    source = BUILD / 'src/lpj/check_fluxes.c'
    old = source.read_text()
    before = '''  if(config->ischeckpoint)
    startyear=max(config->firstyear-config->nspinup,config->checkpointyear)+1;
  else if (config->withlanduse)'''
    after = '''  if (config->withlanduse)'''
    assert old.count(before) == 1
    new = old.replace(before, after)
    anchor = '\n  if(year>startyear && fabs(balance.carbon)'
    assert new.count(anchor) == 1
    new = new.replace(anchor, '''
  /* The natural spin-up gate in updateannual_grid must initialize balance.tot
     before checking a difference, including when resuming a checkpoint. */
  if(config->ischeckpoint)
    startyear=max(startyear,config->checkpointyear+1);
''' + anchor)
    source.write_text(new)
    TEST.mkdir()
    (TEST / 'balance-fix.patch').write_text(''.join(difflib.unified_diff(
        old.splitlines(True), new.splitlines(True),
        fromfile='a/src/lpj/check_fluxes.c', tofile='b/src/lpj/check_fluxes.c')))
    with (TEST / 'build.log').open('w') as log:
        subprocess.run(['make', '-j', '4'], cwd=BUILD, stdout=log,
                       stderr=subprocess.STDOUT, check=True)
    phase = TEST / 'spinup_natural'
    (phase / 'restart').mkdir(parents=True)
    (phase / 'output').mkdir()
    shutil.copy2(checkpoint, phase / 'restart/checkpoint.lpj')
    config = json.loads((CAMPAIGN / 'spinup_natural/checkpoint_config.json').read_text())
    config['checkpoint_filename'] = str(phase / 'restart/checkpoint.lpj')
    # Preserve all scientific fields, including lastyear and equilibration.
    (phase / 'checkpoint_config.json').write_text(json.dumps(config, indent=2))
    (TEST / 'manifest.json').write_text(json.dumps({
        'source_commit': '5af44a1ed023279a23c28d6dfe76945b97aaac57',
        'source_checkpoint_sha256': EXPECTED, 'source_checkpoint_year': -3,
        'patched_binary_sha256': digest(BUILD / 'bin/lpjml'),
        'patched_source_sha256': digest(source), 'mpi_ranks': 8,
        'acceptance': 'Exit zero, checkpoint after year 4, no balance errors; fail_on_balance remains true',
    }, indent=2))
    command = f'''#!/usr/bin/env bash
set -euo pipefail
unset OMP_NUM_THREADS OMP_THREAD_LIMIT
export OPENBLAS_NUM_THREADS=1
python3 {ROOT}/workflow_checkpoints_20260909/checkpoint_runner.py --config {phase}/checkpoint_config.json --phase-dir {phase} --interval-seconds 1 --not-before-year 4 --max-checkpoints 1 -- mpirun -np 8 {BUILD}/bin/lpjml -inpath /home/dasan/lpjml-data/public_standard -outpath {phase} -restartpath {phase}/restart {phase}/checkpoint_config.json >{TEST}/controller.log 2>{TEST}/controller.stderr.log
echo TEST_EXIT_ZERO >{TEST}/status.txt
'''
    (TEST / 'run_test.sh').write_text(command)
    print('PREPARED', TEST, flush=True)


if __name__ == '__main__':
    main()
