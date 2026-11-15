#!/usr/bin/env bash
set -euo pipefail

repo_root=/mnt/c/Proyectos/Astro/ExoFarm_MDwarfs
campaign_parent="$repo_root/Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals"
campaign_root="$campaign_parent/molecule_ablation_loo_20261004"
supervisor="$repo_root/Thermal_Emission_Spectroscopy/scripts/run_proxima_molecule_ablation_campaign.py"
python=/home/dasan/anaconda3/envs/POSEIDON/bin/python
log="$campaign_parent/molecule_ablation_loo_20261004.supervisor.log"
pid_file="$campaign_parent/molecule_ablation_loo_20261004.supervisor.pid"

if [[ -e "$campaign_root/campaign_state.json" ]]; then
    echo "Refusing duplicate campaign: state already exists at $campaign_root"
    exit 2
fi
if [[ -e "$log" || -e "$pid_file" ]]; then
    echo "Refusing to overwrite prior launch records: $log or $pid_file"
    exit 2
fi

nohup "$python" -u "$supervisor" --max-parallel 2 \
    >> "$log" 2>&1 < /dev/null &
supervisor_pid=$!
printf '%s\n' "$supervisor_pid" > "$pid_file"
sleep 2
if ! kill -0 "$supervisor_pid" 2>/dev/null; then
    echo "Supervisor exited during launch; inspect $log"
    exit 1
fi
echo "supervisor_pid=$supervisor_pid"
echo "log=$log"
echo "state=$campaign_root/campaign_state.json"
