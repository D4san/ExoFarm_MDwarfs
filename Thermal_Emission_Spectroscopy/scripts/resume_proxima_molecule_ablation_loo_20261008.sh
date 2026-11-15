#!/usr/bin/env bash
set -euo pipefail

repo_root=/mnt/c/Proyectos/Astro/ExoFarm_MDwarfs
retrievals="$repo_root/Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals"
campaign_root="$retrievals/molecule_ablation_loo_20261004"
supervisor="$repo_root/Thermal_Emission_Spectroscopy/scripts/run_proxima_molecule_ablation_campaign.py"
python=/home/dasan/anaconda3/envs/POSEIDON/bin/python
log="$retrievals/molecule_ablation_loo_20261004.resume_20261008.log"
pid_file="$retrievals/molecule_ablation_loo_20261004.resume_20261008.pid"
phoenix_catalog=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids/grid/phoenix/catalog.fits

if [[ ! -r "$phoenix_catalog" ]]; then
    echo "Required PHOENIX catalog is not readable: $phoenix_catalog" >&2
    exit 2
fi
if [[ ! -f "$campaign_root/campaign_state.json" || ! -f "$campaign_root/manifest.csv" ]]; then
    echo "Existing campaign state/manifest not found: $campaign_root" >&2
    exit 2
fi
if [[ -e "$log" || -e "$pid_file" ]]; then
    echo "Refusing to overwrite resume records: $log or $pid_file" >&2
    exit 2
fi

nohup "$python" -u "$supervisor" --max-parallel 2 --resume-existing \
    >> "$log" 2>&1 < /dev/null &
supervisor_pid=$!
printf '%s\n' "$supervisor_pid" > "$pid_file"
sleep 2
if ! kill -0 "$supervisor_pid" 2>/dev/null; then
    echo "Resume supervisor exited during launch; inspect $log" >&2
    exit 1
fi
echo "supervisor_pid=$supervisor_pid"
echo "log=$log"
echo "state=$campaign_root/campaign_state.json"
