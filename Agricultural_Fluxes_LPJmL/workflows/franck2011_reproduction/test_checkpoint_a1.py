"""Integration test against the accepted continuous eight-cell MPI pilot."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np
from scipy.io import netcdf_file


root = Path('/home/dasan/exofarm-lpjml-runs/checkpoint_a1_20260909')
reference = Path('/home/dasan/exofarm-lpjml-runs/mpi_smoke_20260907')
root.mkdir(exist_ok=False)
(root / 'output').mkdir()
(root / 'restart').mkdir()
config = json.loads((reference / 'configs/a1_2005_n.json').read_text())
config['checkpoint_filename'] = str(root / 'restart/checkpoint.lpj')
config['flush_output'] = True
path = root / 'config.json'
path.write_text(json.dumps(config))
shutil.copy2(reference / 'spinup_natural/restart/restart_1700_nv_stdfire.lpj',
             root / 'restart')
command = ['mpirun', '-np', '2',
           '/home/dasan/exofarm-lpjml-runtime/LPJmL-6.0.6/bin/lpjml',
           '-inpath', '/home/dasan/lpjml-data/public_standard',
           '-outpath', str(root), '-restartpath', str(root / 'restart'), str(path)]
runner = [sys.executable, str(Path(__file__).with_name('checkpoint_runner.py')),
          '--config', str(path), '--phase-dir', str(root)]
subprocess.run(runner + ['--interval-seconds', '0.1', '--not-before-year', '1997',
                         '--max-checkpoints', '1', '--'] + command, check=True)
assert (root / 'restart/checkpoint.lpj').exists(), 'No interrupted checkpoint'
subprocess.run(runner + ['--interval-seconds', '3600', '--'] + command, check=True)
results = []
for expected in sorted((reference / 'a1_2005_n/output').glob('*.nc')):
    actual = root / 'output' / expected.name
    with netcdf_file(expected, mmap=False) as left, netcdf_file(actual, mmap=False) as right:
        assert left.dimensions == right.dimensions, expected.name
        assert left.variables.keys() == right.variables.keys(), expected.name
        for name in left.variables:
            np.testing.assert_array_equal(left.variables[name].data,
                                          right.variables[name].data,
                                          err_msg=f'{expected.name}:{name}')
    results.append(expected.name)
assert results
(root / 'validation.json').write_text(json.dumps({'status': 'PASS',
    'exact_netcdf_arrays': results}, indent=2))
print(json.dumps({'status': 'PASS', 'files': results}), flush=True)
