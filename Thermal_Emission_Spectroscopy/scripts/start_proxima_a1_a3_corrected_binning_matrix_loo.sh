#!/usr/bin/env bash
set -euo pipefail

source /home/dasan/anaconda3/etc/profile.d/conda.sh
conda activate POSEIDON
export POSEIDON_input_data=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs
export PYSYN_CDBS=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

cd /mnt/c/Proyectos/Astro/ExoFarm_MDwarfs
mode="${1:---start}"
exec /home/dasan/anaconda3/envs/POSEIDON/bin/python -u \
  /mnt/c/Proyectos/Astro/ExoFarm_MDwarfs/Thermal_Emission_Spectroscopy/scripts/launch_proxima_a1_a3_corrected_binning_matrix_loo.py \
  "${mode}"
