"""Prepare a new campaign without modifying the interrupted campaign evidence."""
import hashlib
import json
from pathlib import Path
import shutil

source = Path(__file__).resolve().parent
runtime = Path('/home/dasan/exofarm-lpjml-runtime/workflow_checkpoints_20260909')
campaign = Path('/home/dasan/exofarm-lpjml-runs/global_a1_checkpoints_20260909')
previous = campaign.parent / 'global_a1_20260907'
shutil.copytree(source, runtime)
for path in runtime.glob('*.sh'):
    path.write_bytes(path.read_bytes().replace(b'\r\n', b'\n'))
campaign.mkdir()
shutil.copytree(previous / 'configs', campaign / 'configs')
shutil.copy2(previous / 'campaign_manifest.json', campaign / 'reference_campaign_manifest.json')
manifest = {'campaign': campaign.name, 'source_campaign': previous.name,
            'checkpoint_interval_seconds': 3600, 'ranks': 8,
            'scientific_configs': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in (campaign / 'configs').glob('*.json')},
            'comparison_reference': 'reference_campaign_manifest.json',
            'runtime': str(runtime)}
(campaign / 'campaign_manifest.json').write_text(json.dumps(manifest, indent=2))
launcher = f'''#!/usr/bin/env bash
set -euo pipefail
exec 9>{campaign}/campaign.lock
flock -n 9 || exit 9
exec >>{campaign}/launcher.log 2>&1
trap 'echo FAILED >{campaign}/campaign_status.txt' ERR
unset OMP_NUM_THREADS OMP_THREAD_LIMIT
export OPENBLAS_NUM_THREADS=1
for phase in spinup a1; do
  echo "${{phase}}_RUNNING $(date -Is)" >{campaign}/campaign_status.txt
  bash {runtime}/run_global_a1_mpi.sh --lpjml-root /home/dasan/exofarm-lpjml-runtime/LPJmL-6.0.6 --input-root /home/dasan/lpjml-data/public_standard --campaign-dir {campaign} --mpi-ranks 8 --phase "$phase"
done
echo SIMULATIONS_COMPLETE_PENDING_VALIDATION >{campaign}/campaign_status.txt
'''
(campaign / 'launch_campaign.sh').write_text(launcher)
print(campaign)
