#!/usr/bin/env bash
set -euo pipefail

# Run one MPI-parallel corrected Proxima A1 retrieval without touching the
# canonical dataset or the canonical 8/8 retrieval products.
# Usage: bash launch_proxima_a1_o2_fixed_surface.sh 10|100 [mpi-ranks; default 6]

HOURS="${1:-}"
MPI_RANKS="${2:-6}"
if [[ "$HOURS" != "10" && "$HOURS" != "100" ]]; then
    printf 'Usage: %s 10|100 [mpi-ranks: 2..8; default 6]\n' "$0" >&2
    exit 2
fi
if ! [[ "$MPI_RANKS" =~ ^[0-9]+$ ]] || (( MPI_RANKS < 2 || MPI_RANKS > 8 )); then
    printf 'MPI ranks must be an integer from 2 through 8; got: %s\n' \
        "$MPI_RANKS" >&2
    exit 2
fi

REPO=/mnt/c/Proyectos/Astro/ExoFarm_MDwarfs
CAMPAIGN="$REPO/Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1"
OUT="$CAMPAIGN/retrievals"
RESULTS="$OUT/POSEIDON_output/proxima_b_earthlike/retrievals"
TAG=_O2_fixedBlack1bar_noxtol_MPI${MPI_RANKS}
RETRIEVAL="proxima_A1_${HOURS}h${TAG}"
LOG="$OUT/${RETRIEVAL}.launch.log"
PIDFILE="$OUT/${RETRIEVAL}.pid"

if [[ "$HOURS" == "10" ]]; then
    DATASET_REL=Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A1_10h.dat
    DATASET="$REPO/$DATASET_REL"
else
    DATASET_REL=Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A1_100h_O2_fixedBlack1bar_noxtol_audit.dat
    DATASET="$REPO/$DATASET_REL"
fi
DATASET_ARGS=(--dataset-file "$DATASET_REL")

if [[ ! -s "$DATASET" ]]; then
    printf '[abort] Missing or empty dataset: %s\n' "$DATASET" >&2
    exit 3
fi

for path in "$LOG" "$PIDFILE"; do
    if [[ -e "$path" ]]; then
        printf '[abort] Preserving existing launch record; inspect before retry: %s\n' \
            "$path" >&2
        exit 4
    fi
done

if ps -eo args= | grep -F 'run_life_retrieval.py --campaign proxima --scenario A1 --hours ' \
        | grep -F -- "--hours $HOURS" \
        | grep -F -- '--output-tag _O2_fixedBlack1bar_noxtol' \
        | grep -v 'grep -'; then
    printf '[abort] Matching A1 retrieval process is already active.\n' >&2
    exit 5
fi

for subdir in MultiNest_raw results samples; do
    for candidate in "$RESULTS/$subdir/$RETRIEVAL"*; do
        if [[ -e "$candidate" ]]; then
            printf '[abort] Matching POSEIDON output already exists; refusing overwrite: %s\n' \
                "$candidate" >&2
            exit 6
        fi
    done
done

source /home/dasan/anaconda3/etc/profile.d/conda.sh
conda activate POSEIDON
MPIEXEC="$CONDA_PREFIX/bin/mpiexec"
if [[ ! -x "$MPIEXEC" ]]; then
    printf '[abort] Matching MPICH launcher is unavailable: %s\n' "$MPIEXEC" >&2
    exit 7
fi
export POSEIDON_input_data=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs
export PYSYN_CDBS=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids
# MultiNest parallelizes likelihood evaluations with MPI ranks. Limit threaded
# math libraries to one thread per rank to avoid nested oversubscription.
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
cd "$REPO/Thermal_Emission_Spectroscopy/scripts"

{
    printf '[launch_attempt_utc] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf '[config] campaign=proxima scenario=A1 hours=%s N_live=800 MPI_ranks=%s ' \
        "$HOURS" "$MPI_RANKS"
    printf 'X_profile=isochem O2=true surface=fixed-black-at-1-bar '
    printf 'error_inflation=none x_tol=disabled R=10000 '
    printf 'OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1\n'
    printf '[dataset] %s\n' "$DATASET_REL"
    printf '[dataset_sha256] '
    sha256sum "$DATASET"
    printf '[mpi_launcher] %s\n' "$MPIEXEC"
    printf '[command] %s -n %s %s/bin/python -u run_life_retrieval.py --campaign proxima --scenario A1 --hours %s --n-live 800 --error-inflation none --surface-pressure-mode fixed-black --include-o2 --x-profile isochem --output-tag %s --R 10000' \
        "$MPIEXEC" "$MPI_RANKS" "$CONDA_PREFIX" "$HOURS" "$TAG"
    printf ' --dataset-file %s' "$DATASET_REL"
    printf '\n'
} >> "$LOG"

"$MPIEXEC" -n "$MPI_RANKS" "$CONDA_PREFIX/bin/python" -u run_life_retrieval.py \
    --campaign proxima --scenario A1 --hours "$HOURS" --n-live 800 \
    --error-inflation none --surface-pressure-mode fixed-black \
    --include-o2 --x-profile isochem --output-tag "$TAG" --R 10000 \
    "${DATASET_ARGS[@]}" >> "$LOG" 2>&1 < /dev/null &
RUN_PID=$!
printf '%s\n' "$RUN_PID" > "$PIDFILE"
printf '[started] PID=%s\n[log] %s\n[pidfile] %s\n' \
    "$RUN_PID" "$LOG" "$PIDFILE"

# Keep the Ubuntu launcher alive while POSEIDON runs; background jobs can be
# terminated when a short-lived WSL shell exits.
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
