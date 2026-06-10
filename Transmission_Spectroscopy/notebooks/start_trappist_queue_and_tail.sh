#!/usr/bin/env bash
set -euo pipefail

cd /mnt/c/Proyectos/Astro/ExoFarm_MDwarfs/Transmission_Spectroscopy/notebooks
source /home/dasan/anaconda3/etc/profile.d/conda.sh
conda activate POSEIDON

if [ ! -f /mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids/grid/phoenix/catalog.fits ]; then
  echo "Missing POSEIDON stellar grid at /mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids/grid/phoenix/catalog.fits"
  echo "Check that D: is mounted inside WSL before relaunching."
  exit 1
fi

setsid bash ./run_campaign_trappist_queue.sh >/dev/null 2>&1 < /dev/null &
tail -f POSEIDON_output/TRAPPIST-1e/retrievals/campaign_logs/campaign_trappist_retrieval_queue.nohup.log
