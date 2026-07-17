#!/usr/bin/env bash
set -euo pipefail

cd /mnt/c/Proyectos/Astro/ExoFarm_MDwarfs/Transmission_Spectroscopy/notebooks
export POSEIDON_input_data=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs
export PYSYN_CDBS=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids

exec /home/dasan/anaconda3/envs/POSEIDON/bin/python plot_retrieval_campaign_comparison.py
