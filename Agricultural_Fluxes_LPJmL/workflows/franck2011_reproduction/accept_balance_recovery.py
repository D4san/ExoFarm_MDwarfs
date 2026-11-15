"""Validate the isolated recovery test and select its build for the campaign.

Run only after the test controller exits. This does not launch the campaign
or replace its checkpoint; replay starts from the preserved year -3 state.
"""
import argparse
import json
from pathlib import Path
import re
import shutil

from prepare_balance_recovery import BUILD, CAMPAIGN, EXPECTED, TEST, digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select-build', action='store_true')
    args = parser.parse_args()
    assert (TEST / 'status.txt').read_text().strip() == 'TEST_EXIT_ZERO'
    phase = TEST / 'spinup_natural'
    logs = list(phase.glob('segment_*.stdout.log'))
    assert len(logs) == 1
    content = logs[0].read_text()
    years = [int(y) for y in re.findall(r'^\s*(-?\d+)\s+[-\d.]+\s', content, re.M)]
    assert years == list(range(-2, years[-1] + 1)) and years[-1] >= 5
    assert 'SIGTERM catched' in content
    # The patch must preserve the observed trajectory before the original abort.
    old_log = (CAMPAIGN / 'spinup_natural/segment_1789108033976118071.stdout.log').read_text()
    def annual_rows(text):
        return {int(parts[0]): parts[1:] for line in text.splitlines()
                if re.match(r'^\s*-?\d+\s+[-\d.]+\s', line)
                for parts in [line.split()]}
    previous_rows = annual_rows(old_log)
    current_rows = annual_rows(content)
    assert set(previous_rows) == set(range(-2, 3))
    assert all(current_rows[y] == row for y, row in previous_rows.items())
    stderr = logs[0].with_suffix('.stderr.log').read_text()
    assert not re.search(r'ERROR\d+|Invalid .*balance|Program terminated unsuccessfully', stderr)
    assert not (TEST / 'controller.stderr.log').read_text().strip()
    saved = list((phase / 'checkpoints').glob('*.lpj'))
    assert len(saved) == 1
    checksum = digest(saved[0])
    assert checksum == saved[0].with_suffix('.sha256').read_text().strip()
    assert checksum == digest(phase / 'restart/checkpoint.lpj')
    baseline = json.loads((CAMPAIGN / 'spinup_natural/checkpoint_config.json').read_text())
    trial = json.loads((phase / 'checkpoint_config.json').read_text())
    assert baseline['fail_on_balance'] is True
    baseline.pop('checkpoint_filename')
    trial.pop('checkpoint_filename')
    assert baseline == trial
    assert digest(CAMPAIGN / 'spinup_natural/restart/checkpoint.lpj') == EXPECTED
    manifest = json.loads((TEST / 'manifest.json').read_text())
    assert digest(BUILD / 'bin/lpjml') == manifest['patched_binary_sha256']
    result = {'status': 'PASS', 'years': years, 'checkpoint_sha256': checksum,
              'scientific_config_equal': True, 'fail_on_balance': True,
              'pre_failure_diagnostics_identical_at_log_precision': True,
              'original_checkpoint_preserved': True,
              'binary_sha256': manifest['patched_binary_sha256']}
    (TEST / 'validation.json').write_text(json.dumps(result, indent=2))
    if args.select_build:
        launcher = CAMPAIGN / 'launch_campaign.sh'
        original = launcher.read_text()
        old = '--lpjml-root /home/dasan/exofarm-lpjml-runtime/LPJmL-6.0.6 '
        assert original.count(old) == 1
        backup = CAMPAIGN / 'launch_campaign.pre_balance_fix_20260912.sh'
        assert not backup.exists()
        shutil.copy2(launcher, backup)
        launcher.write_text(original.replace(old, f'--lpjml-root {BUILD} '))
        shutil.copy2(TEST / 'manifest.json', CAMPAIGN / 'balance_fix_manifest.json')
        shutil.copy2(TEST / 'validation.json', CAMPAIGN / 'balance_fix_validation.json')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
