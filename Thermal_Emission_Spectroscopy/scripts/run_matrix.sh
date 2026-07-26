#!/usr/bin/env bash
# 8 LIFE emission retrievals: Proxima A0-A3 x {10h, 240h}. Sequential (one
# POSEIDON process at a time) to respect the 7.6 GB WSL limit.
cd "$(dirname "$0")"
source /home/castello/POSEIDON/activate_exofarm_life.sh >/dev/null 2>&1
for h in 240 10; do
  for s in A0 A1 A2 A3; do
    echo "=== $s ${h}h @ $(date +%H:%M) ==="
    python run_life_retrieval.py --campaign proxima --scenario $s --hours $h --n-live 200
  done
done
echo "=== MATRIX DONE @ $(date) ==="
