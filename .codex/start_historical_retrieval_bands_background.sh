#!/usr/bin/env bash
set -euo pipefail

cd /mnt/c/Proyectos/Astro/ExoFarm_MDwarfs/Transmission_Spectroscopy/notebooks
export POSEIDON_input_data=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs
export PYSYN_CDBS=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids

nohup /home/dasan/anaconda3/envs/POSEIDON/bin/python plot_retrieved_zooms.py \
  > /mnt/c/Proyectos/Astro/ExoFarm_MDwarfs/.codex/historical_retrieval_bands.log 2>&1 < /dev/null &
echo $! > /mnt/c/Proyectos/Astro/ExoFarm_MDwarfs/.codex/historical_retrieval_bands.pid
