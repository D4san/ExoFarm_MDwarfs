#!/usr/bin/env bash
set -euo pipefail

cd /mnt/c/Proyectos/Astro/ExoFarm_MDwarfs/Transmission_Spectroscopy/notebooks

export PYSYN_CDBS=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids
export POSEIDON_input_data=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs
export PYTHONUNBUFFERED=1

python_bin=/home/dasan/anaconda3/envs/POSEIDON/bin/python
log_dir=POSEIDON_output/TRAPPIST-1e/retrievals/campaign_logs
mkdir -p "$log_dir"
log_file="$log_dir/campaign_remaining_20260710.log"

run_one() {
    local scenario="$1"
    local transits="$2"
    local instrument="$3"
    printf '[%s] START %s_%s_%s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$scenario" "$transits" "$instrument" | tee -a "$log_file"
    "$python_bin" run_trappist_retrieval.py \
        --scenario "$scenario" \
        --n-transits "$transits" \
        --instrument "$instrument" \
        --n-live 1000 >>"$log_file" 2>&1
    printf '[%s] END %s_%s_%s returncode=0\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$scenario" "$transits" "$instrument" | tee -a "$log_file"
}

printf '\n[%s] REMAINING CAMPAIGN START\n' "$(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$log_file"
run_one A0 100 both
run_one A3 200 miri
run_one A3 200 nirspec
run_one A3 100 both
printf '[%s] REMAINING CAMPAIGN COMPLETE\n' "$(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$log_file"
