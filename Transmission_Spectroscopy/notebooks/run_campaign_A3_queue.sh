#!/usr/bin/env bash
set -euo pipefail

export POSEIDON_input_data=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/
export PYSYN_CDBS=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids/

cd /mnt/c/Proyectos/Astro/ExoFarm_MDwarfs/Transmission_Spectroscopy/notebooks
source /home/dasan/anaconda3/etc/profile.d/conda.sh
conda activate POSEIDON

mkdir -p POSEIDON_output/TRAPPIST-1e/retrievals/campaign_logs

python run_trappist_retrieval_campaign.py --resume \
  > POSEIDON_output/TRAPPIST-1e/retrievals/campaign_logs/campaign_trappist_retrieval_queue.nohup.log \
  2>&1
