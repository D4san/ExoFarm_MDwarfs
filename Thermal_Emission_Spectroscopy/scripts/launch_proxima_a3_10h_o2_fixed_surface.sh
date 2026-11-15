#!/usr/bin/env bash
set -euo pipefail

REPO=/mnt/c/Proyectos/Astro/ExoFarm_MDwarfs
OUT="$REPO/Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals"
RESULTS="$OUT/POSEIDON_output/proxima_b_earthlike/retrievals"
DATASET="$REPO/Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A3_10h.dat"
TAG=_O2_fixedBlack1bar_noxtol
LOG="$OUT/proxima_A3_10h${TAG}.launch.log"
PIDFILE="$OUT/proxima_A3_10h${TAG}.pid"

if [[ ! -f "$DATASET" ]]; then
    printf '[abort] Missing LIFE dataset: %s\n' "$DATASET" >&2
    exit 2
fi

if [[ -e "$PIDFILE" ]]; then
    PREVIOUS_PID=$(<"$PIDFILE")
    if kill -0 "$PREVIOUS_PID" 2>/dev/null; then
        printf '[abort] Recorded PID is still active; refusing duplicate: %s\n' \
            "$PREVIOUS_PID" >&2
        exit 3
    fi
    printf '[stale_pid] previous launch PID=%s is no longer active; no matching outputs were found; preserving history in this log.\n' \
        "$PREVIOUS_PID" >> "$LOG"
fi

if [[ -e "$LOG" ]]; then
    printf '[notice] Existing log found without a PID record; preserving it and appending after duplicate checks.\n'
fi

if pgrep -af '[p]ython.*run_life_retrieval.py.*--campaign proxima --scenario A3 --hours 10.*--output-tag _O2_fixedBlack1bar_noxtol'; then
    printf '[abort] A matching corrected 10 h retrieval is already active.\n' >&2
    exit 4
fi

for candidate in \
    "$RESULTS/results/proxima_A3_10h${TAG}"* \
    "$RESULTS/samples/proxima_A3_10h${TAG}"* \
    "$RESULTS/MultiNest_raw/proxima_A3_10h${TAG}"*; do
    if [[ -e "$candidate" ]]; then
        printf '[abort] Matching retrieval output already exists: %s\n' \
            "$candidate" >&2
        exit 5
    fi
done

source /home/dasan/anaconda3/etc/profile.d/conda.sh
conda activate POSEIDON
export POSEIDON_input_data=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs
export PYSYN_CDBS=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids
cd "$REPO/Thermal_Emission_Spectroscopy/scripts"

{
    printf '[launch_attempt_utc] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf '[config] campaign=proxima scenario=A3 hours=10 N_live=800 '
    printf 'error_inflation=none surface=fixed-black-at-1-bar '
    printf 'include_O2=true x_tol=disabled R=10000 X_profile=isochem\n'
    printf '[dataset_sha256] '
    sha256sum "$DATASET"
    printf '%s\n' "[command] python -u run_life_retrieval.py --campaign proxima --scenario A3 --hours 10 --n-live 800 --error-inflation none --surface-pressure-mode fixed-black --include-o2 --output-tag $TAG --R 10000"
} >> "$LOG"

nohup "$CONDA_PREFIX/bin/python" -u run_life_retrieval.py \
    --campaign proxima --scenario A3 --hours 10 --n-live 800 \
    --error-inflation none --surface-pressure-mode fixed-black \
    --include-o2 --output-tag "$TAG" --R 10000 \
    >> "$LOG" 2>&1 < /dev/null &
RUN_PID=$!
printf '%s\n' "$RUN_PID" > "$PIDFILE"
printf '[started] PID=%s\n[log] %s\n[pidfile] %s\n' \
    "$RUN_PID" "$LOG" "$PIDFILE"

# Keep this Ubuntu launcher session alive while Python runs; some
# `ubuntu.exe run` invocations terminate background jobs when their shell exits.
sleep 5
if ! kill -0 "$RUN_PID" 2>/dev/null; then
    set +e
    wait "$RUN_PID"
    EXIT_STATUS=$?
    set -e
    printf '[early_exit] PID=%s exit_code=%s\n' "$RUN_PID" "$EXIT_STATUS" \
        >> "$LOG"
    exit "$EXIT_STATUS"
fi

printf '[process_confirmed] PID=%s remains active after startup.\n' "$RUN_PID" \
    >> "$LOG"
set +e
wait "$RUN_PID"
EXIT_STATUS=$?
set -e
printf '[process_exit] PID=%s exit_code=%s\n' "$RUN_PID" "$EXIT_STATUS" \
    >> "$LOG"
exit "$EXIT_STATUS"
