#!/usr/bin/env bash
set -euo pipefail
campaign=/home/dasan/exofarm-lpjml-runs/global_a1_20260907
exec 9>"$campaign/campaign.lock"
flock -n 9 || exit 9
exec >>"$campaign/launcher.log" 2>&1
status="$campaign/campaign_status.txt"
trap 'rc=$?; printf "FAILED exit=%s utc=%s\n" "$rc" "$(date -u +%FT%TZ)" > "$status"; exit "$rc"' ERR
test ! -e "$campaign/spinup_natural/run_status.txt"
export OPENBLAS_NUM_THREADS=1
unset OMP_NUM_THREADS OMP_THREAD_LIMIT
runner=/home/dasan/exofarm-lpjml-runtime/workflow_20260907/run_global_a1_mpi.sh
common=(--lpjml-root /home/dasan/exofarm-lpjml-runtime/LPJmL-6.0.6 --input-root /home/dasan/lpjml-data/public_standard --campaign-dir "$campaign" --mpi-ranks 8)
printf "SPINUP_RUNNING %s\n" "$(date -u +%FT%TZ)" > "$status"
bash "$runner" "${common[@]}" --phase spinup
test -s "$campaign/spinup_natural/restart/restart_1700_nv_stdfire.lpj"
grep -q 'exit_code=0' "$campaign/spinup_natural/run_status.txt"
printf "A1_RUNNING %s\n" "$(date -u +%FT%TZ)" > "$status"
bash "$runner" "${common[@]}" --phase a1
printf "SIMULATIONS_COMPLETE_PENDING_VALIDATION %s\n" "$(date -u +%FT%TZ)" > "$status"
