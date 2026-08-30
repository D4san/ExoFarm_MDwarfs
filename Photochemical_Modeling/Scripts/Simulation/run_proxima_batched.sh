#!/usr/bin/env bash
# Run VULCAN Proxima A0-A3 in batches of 2 to respect the 7.6 GB WSL RAM limit
# (never >2 solvers; never concurrent with a POSEIDON opacity read).
set -u
cd "$(dirname "$0")"
source /home/castello/miniconda3/etc/profile.d/conda.sh
conda activate ExoFarm_LIFE
echo "=== BATCH 1: A0,A1 @ $(date) ==="
EXOFARM_SCENARIOS=A0,A1 python -u run_parallel_proxima.py
echo "=== BATCH 2: A2,A3 @ $(date) ==="
EXOFARM_SCENARIOS=A2,A3 python -u run_parallel_proxima.py
echo "=== DONE @ $(date) ==="
