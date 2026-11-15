#!/usr/bin/env bash
set -euo pipefail

# Resume a validated A1 MultiNest checkpoint on WSL's Linux filesystem.
# The original failed-run files stay untouched under the repository; completed
# retry products are harvested back only after a clean POSEIDON exit.
# Usage: bash resume_proxima_a1_o2_fixed_surface.sh 10|100 [mpi-ranks; default 6]

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
if [[ "$MPI_RANKS" != "6" ]]; then
    printf '[abort] These checkpoints were created with six MPI ranks; use 6.\n' >&2
    exit 2
fi

REPO=/mnt/c/Proyectos/Astro/ExoFarm_MDwarfs
CAMPAIGN="$REPO/Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1"
OUT="$CAMPAIGN/retrievals"
RESULTS="$OUT/POSEIDON_output/proxima_b_earthlike/retrievals"
TAG=_O2_fixedBlack1bar_noxtol_MPI${MPI_RANKS}R1
RETRIEVAL="proxima_A1_${HOURS}h${TAG}"
LOG="$OUT/${RETRIEVAL}.launch.log"
PIDFILE="$OUT/${RETRIEVAL}.pid"
MANIFEST="$OUT/${RETRIEVAL}.resume_manifest.json"
RUN_DIR="/home/dasan/exofarm_life_a1_resume_20260929/${HOURS}h"
STAGE_TOOL="$REPO/Thermal_Emission_Spectroscopy/scripts/stage_proxima_a1_multinest_resume.py"

if [[ "$HOURS" == "10" ]]; then
    DATASET_REL=Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A1_10h.dat
else
    DATASET_REL=Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A1_100h_O2_fixedBlack1bar_noxtol_audit.dat
fi
DATASET="$REPO/$DATASET_REL"
if [[ ! -s "$DATASET" ]]; then
    printf '[abort] Missing or empty dataset: %s\n' "$DATASET" >&2
    exit 3
fi
for path in "$LOG" "$PIDFILE"; do
    if [[ -e "$path" ]]; then
        printf '[abort] Preserving existing recovery record: %s\n' "$path" >&2
        exit 4
    fi
done
if [[ ! -s "$MANIFEST" ]]; then
    printf '[abort] Missing validated resume manifest: %s\n' "$MANIFEST" >&2
    exit 4
fi
if ps -eo args= | grep -F 'run_life_retrieval.py --campaign proxima --scenario A1 --hours ' \
        | grep -F -- "--hours $HOURS" \
        | grep -F -- '--resume' \
        | grep -v 'grep -'; then
    printf '[abort] Matching A1 resume process is already active.\n' >&2
    exit 5
fi

source /home/dasan/anaconda3/etc/profile.d/conda.sh
conda activate POSEIDON
MPIEXEC="$CONDA_PREFIX/bin/mpiexec"
PYTHON="$CONDA_PREFIX/bin/python"
if [[ ! -x "$MPIEXEC" || ! -x "$PYTHON" ]]; then
    printf '[abort] POSEIDON env does not provide matching MPI/Python.\n' >&2
    exit 6
fi
export POSEIDON_input_data=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs
export PYSYN_CDBS=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

cd "$REPO/Thermal_Emission_Spectroscopy/scripts"
if [[ ! -f "$RUN_DIR/POSEIDON_output/proxima_b_earthlike/retrievals/MultiNest_raw/${RETRIEVAL}-resume.dat" \
   || ! -f "$RUN_DIR/POSEIDON_output/proxima_b_earthlike/retrievals/MultiNest_raw/${RETRIEVAL}-ev.dat" \
   || ! -f "$RUN_DIR/POSEIDON_output/proxima_b_earthlike/retrievals/MultiNest_raw/${RETRIEVAL}-live.points" \
   || ! -f "$RUN_DIR/POSEIDON_output/proxima_b_earthlike/retrievals/MultiNest_raw/${RETRIEVAL}-phys_live.points" ]]; then
    printf '[abort] Validated staged checkpoint is missing for %s; not starting.\n' \
        "$RETRIEVAL" >&2
    exit 7
fi

{
    printf '[launch_attempt_utc] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf '[config] campaign=proxima scenario=A1 hours=%s N_live=800 MPI_ranks=%s ' \
        "$HOURS" "$MPI_RANKS"
    printf 'X_profile=isochem O2=true surface=fixed-black-at-1-bar '
    printf 'error_inflation=none x_tol=disabled R=10000 resume=true '
    printf 'output_filesystem=WSL_ext4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 '
    printf 'MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1\n'
    printf '[dataset] %s\n' "$DATASET_REL"
    printf '[dataset_sha256] '
    sha256sum "$DATASET"
    printf '[resume_manifest] %s\n' "$MANIFEST"
    printf '[run_dir] %s\n' "$RUN_DIR"
    printf '[command] %s -n %s %s -u run_life_retrieval.py --campaign proxima --scenario A1 --hours %s --n-live 800 --error-inflation none --surface-pressure-mode fixed-black --include-o2 --x-profile isochem --output-tag %s --R 10000 --resume --run-dir %s --dataset-file %s\n' \
        "$MPIEXEC" "$MPI_RANKS" "$PYTHON" "$HOURS" "$TAG" "$RUN_DIR" "$DATASET_REL"
    cat "$MANIFEST"
} >> "$LOG"

"$MPIEXEC" -n "$MPI_RANKS" "$PYTHON" -u run_life_retrieval.py \
    --campaign proxima --scenario A1 --hours "$HOURS" --n-live 800 \
    --error-inflation none --surface-pressure-mode fixed-black \
    --include-o2 --x-profile isochem --output-tag "$TAG" --R 10000 \
    --resume --run-dir "$RUN_DIR" --dataset-file "$DATASET_REL" \
    >> "$LOG" 2>&1 < /dev/null &
RUN_PID=$!
printf '%s\n' "$RUN_PID" > "$PIDFILE"
printf '[started] PID=%s\n[log] %s\n[pidfile] %s\n' \
    "$RUN_PID" "$LOG" "$PIDFILE"

sleep 8
if ! kill -0 "$RUN_PID" 2>/dev/null; then
    set +e
    wait "$RUN_PID"
    EXIT_STATUS=$?
    set -e
    printf '[early_exit] PID=%s exit_code=%s\n' "$RUN_PID" "$EXIT_STATUS" >> "$LOG"
    exit "$EXIT_STATUS"
fi
printf '[process_confirmed] PID=%s remains active after startup.\n' "$RUN_PID" >> "$LOG"
set +e
wait "$RUN_PID"
EXIT_STATUS=$?
set -e
printf '[process_exit] PID=%s exit_code=%s\n' "$RUN_PID" "$EXIT_STATUS" >> "$LOG"
if (( EXIT_STATUS != 0 )); then
    printf '[harvest_skipped] Non-zero exit; scratch outputs preserved at %s\n' \
        "$RUN_DIR" >> "$LOG"
    exit "$EXIT_STATUS"
fi

# Preflight every target before copying any file, so a collision cannot cause
# a partial overwrite or mix this attempt with earlier evidence.
declare -a SOURCES=() TARGETS=()
for subdir in MultiNest_raw results samples; do
    src_dir="$RUN_DIR/POSEIDON_output/proxima_b_earthlike/retrievals/$subdir"
    dst_dir="$RESULTS/$subdir"
    for source_file in "$src_dir/$RETRIEVAL"*; do
        [[ -f "$source_file" ]] || continue
        target_file="$dst_dir/$(basename "$source_file")"
        if [[ -e "$target_file" ]]; then
            printf '[harvest_abort] Existing target preserved: %s\n' "$target_file" >> "$LOG"
            exit 8
        fi
        SOURCES+=("$source_file")
        TARGETS+=("$target_file")
    done
done
if (( ${#SOURCES[@]} == 0 )); then
    printf '[harvest_abort] No retry-prefix products found under %s\n' "$RUN_DIR" >> "$LOG"
    exit 9
fi
for index in "${!SOURCES[@]}"; do
    mkdir -p "$(dirname "${TARGETS[$index]}")"
    cp -p -- "${SOURCES[$index]}" "${TARGETS[$index]}"
done
printf '[harvested] %s files copied from WSL ext4 to project outputs.\n' \
    "${#SOURCES[@]}" >> "$LOG"
printf '[scratch_preserved] %s\n' "$RUN_DIR" >> "$LOG"
exit 0
