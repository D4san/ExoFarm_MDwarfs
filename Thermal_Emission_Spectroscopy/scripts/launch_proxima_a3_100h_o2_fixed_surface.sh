#!/usr/bin/env bash
set -euo pipefail

REPO=/mnt/c/Proyectos/Astro/ExoFarm_MDwarfs
OUT="$REPO/Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals"
TAG=_O2_fixedBlack1bar_noxtol
LOG="$OUT/proxima_A3_100h_O2_fixedBlack1bar_noxtol.launch.log"
PIDFILE="$OUT/proxima_A3_100h_O2_fixedBlack1bar_noxtol.pid"

if pgrep -af "run_life_retrieval.py --campaign proxima --scenario A3 --hours 100.*--output-tag $TAG"; then
    echo "[abort] matching retrieval process already exists" >&2
    exit 2
fi
if [[ -e "$LOG" || -e "$PIDFILE" ]]; then
    echo "[abort] output log or PID file already exists; refusing to overwrite" >&2
    exit 2
fi

source /home/dasan/anaconda3/etc/profile.d/conda.sh
conda activate POSEIDON
export POSEIDON_input_data=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs
export PYSYN_CDBS=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids
cd "$REPO/Thermal_Emission_Spectroscopy/scripts"

nohup python -u run_life_retrieval.py \
    --campaign proxima --scenario A3 --hours 100 --n-live 800 \
    --error-inflation none --surface-pressure-mode fixed-black \
    --include-o2 --output-tag "$TAG" --R 10000 \
    > "$LOG" 2>&1 < /dev/null &
RUN_PID=$!
printf '%s\n' "$RUN_PID" > "$PIDFILE"
printf '[started] PID=%s\n[log] %s\n[pidfile] %s\n' \
    "$RUN_PID" "$LOG" "$PIDFILE"
