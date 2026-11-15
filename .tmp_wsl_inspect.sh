#!/usr/bin/env bash
set -euo pipefail
printf 'PWD=%s\n' "$PWD"
printf 'TARGET=%s\n' /home/dasan/exofarm-lpjml-runs
ls -la /home/dasan/exofarm-lpjml-runs
for d in /home/dasan/exofarm-lpjml-runs/*; do
  printf 'ENTRY=%s type=%s\n' "$d" "$(stat -c %F "$d")"
done
printf 'A0 candidates:\n'
find /home/dasan -maxdepth 4 -type f \( -name 'restart_1700*' -o -name 'run_status.txt' \) -printf '%p\n' 2>/dev/null | head -100
printf 'A0 dir:\n'
find /home/dasan/exofarm-lpjml-runs/global_a1_checkpoints_20260909/a0_natural -maxdepth 3 -type f -printf '%p\n' 2>/dev/null | head -60
echo SCRIPT_OK
bash -n /mnt/c/Proyectos/Astro/ExoFarm_MDwarfs/Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction/run_capacity_potential_mpi.sh
