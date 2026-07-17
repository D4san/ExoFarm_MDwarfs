#!/usr/bin/env bash
set -euo pipefail

cd /mnt/c/Proyectos/Astro/ExoFarm_MDwarfs/Transmission_Spectroscopy/notebooks
exec /home/dasan/anaconda3/envs/POSEIDON/bin/python plot_profile_posterior_comparison.py
