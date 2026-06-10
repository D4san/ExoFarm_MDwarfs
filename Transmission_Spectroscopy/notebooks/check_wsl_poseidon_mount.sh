#!/usr/bin/env bash
set -u

log=/mnt/c/Proyectos/Astro/ExoFarm_MDwarfs/Transmission_Spectroscopy/notebooks/POSEIDON_output/TRAPPIST-1e/retrievals/campaign_logs/wsl_poseidon_mount_check.log
{
  date
  echo "whoami=$(whoami)"
  echo "pwd=$(pwd)"
  echo "mounts:"
  mount | grep -E ' /mnt/[cd] ' || true
  echo "catalog:"
  ls -l /mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids/grid/phoenix/catalog.fits
} > "$log" 2>&1
