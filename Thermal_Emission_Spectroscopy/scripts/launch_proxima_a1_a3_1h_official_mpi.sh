#!/usr/bin/env bash
set -euo pipefail

# Launch one member of the focused official A1/A3 1 h LIFE retrieval pair.
# MultiNest writes on WSL's Linux filesystem; harvest only after exit 0.
# Usage: bash launch_proxima_a1_a3_1h_official_mpi.sh A1|A3

SCENARIO="${1:-}"
if [[ "$SCENARIO" != "A1" && "$SCENARIO" != "A3" ]]; then
    printf 'Usage: %s A1|A3\n' "$0" >&2
    exit 2
fi

REPO=/mnt/c/Proyectos/Astro/ExoFarm_MDwarfs
CAMPAIGN="$REPO/Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1"
RETRIEVALS="$CAMPAIGN/retrievals"
RESULTS="$RETRIEVALS/POSEIDON_output/proxima_b_earthlike/retrievals"
DATASET_REL="Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_${SCENARIO}_1h_O2_fixedBlack1bar_official.dat"
DATASET="$REPO/$DATASET_REL"
TAG=_O2_fixedBlack1bar_noxtol_MPI6_OFFICIAL1h
RETRIEVAL="proxima_${SCENARIO}_1h${TAG}"
LOG="$RETRIEVALS/${RETRIEVAL}.launch.log"
PIDFILE="$RETRIEVALS/${RETRIEVAL}.pid"
RUN_DIR="/home/dasan/exofarm_proxima_a1_a3_1h_official_20261001/$SCENARIO/retrieval"

if [[ ! -s "$DATASET" ]]; then
    printf '[abort] Missing or empty dataset: %s\n' "$DATASET" >&2
    exit 3
fi
if [[ -e "$LOG" || -e "$PIDFILE" || -e "$RUN_DIR" ]]; then
    printf '[abort] Existing launch record or scratch found; preserving it.\n' >&2
    printf '[paths] log=%s pid=%s scratch=%s\n' "$LOG" "$PIDFILE" "$RUN_DIR" >&2
    exit 4
fi
if ps -eo args= | grep -F "run_life_retrieval.py --campaign proxima --scenario $SCENARIO --hours 1 " \
        | grep -v 'grep -'; then
    printf '[abort] Matching 1 h retrieval process is already active.\n' >&2
    exit 5
fi
for subdir in MultiNest_raw results samples; do
    if [[ -d "$RESULTS/$subdir" ]] && \
            find "$RESULTS/$subdir" -maxdepth 1 -name "${RETRIEVAL}*" \
                -print -quit | grep -q .; then
        printf '[abort] Matching harvested products exist; refusing overwrite.\n' >&2
        exit 6
    fi
done

mkdir -p "$RETRIEVALS"
( set -o noclobber; : > "$LOG" )
printf '%s\n' "$$" > "$PIDFILE"
exec >>"$LOG" 2>&1

printf '[launch_utc] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
printf '[scenario] %s\n[hours] 1\n[mpi_ranks] 6\n' "$SCENARIO"
printf '[dataset] %s\n' "$DATASET_REL"
sha256sum "$DATASET"
printf '[scratch] %s\n' "$RUN_DIR"
printf '[config] POSEIDON/MPICH conda=POSEIDON X_profile=isochem N_live=800 '
printf 'error_inflation=none x_tol=disabled O2=true surface=fixed-black-1bar R=10000 bins=31\n'

source /home/dasan/anaconda3/etc/profile.d/conda.sh
conda activate POSEIDON
MPIEXEC="$CONDA_PREFIX/bin/mpiexec"
PYTHON="$CONDA_PREFIX/bin/python"
if [[ ! -x "$MPIEXEC" || ! -x "$PYTHON" ]]; then
    printf '[abort] POSEIDON Python or MPICH mpiexec is unavailable.\n'
    exit 7
fi
export POSEIDON_input_data=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs
export PYSYN_CDBS=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cd "$REPO/Thermal_Emission_Spectroscopy/scripts"

"$PYTHON" - "$DATASET" <<'PY'
import sys
import numpy as np

data = np.loadtxt(sys.argv[1], skiprows=1)
if data.shape != (31, 4) or not np.isfinite(data).all():
    raise SystemExit(f"[abort] invalid LIFE dataset shape/content: {data.shape}")
if np.any(data[:, 1] <= 0) or np.any(data[:, 3] <= 0):
    raise SystemExit("[abort] bin widths and uncertainties must be positive")
print("[dataset_check] 31 bins, 4 columns, finite values, positive widths/sigma")
PY

COMMON_ARGS=(
    --campaign proxima --scenario "$SCENARIO" --hours 1 --n-live 800
    --error-inflation none --surface-pressure-mode fixed-black --include-o2
    --x-profile isochem --output-tag "$TAG" --R 10000
    --dataset-file "$DATASET_REL"
)
mkdir -p "$RUN_DIR/preflight"
if [[ "$SCENARIO" == "A3" ]]; then
    "$PYTHON" -u run_life_retrieval.py "${COMMON_ARGS[@]}" \
        --run-dir "$RUN_DIR/preflight" --setup-only --validate-forward
else
    "$PYTHON" -u run_life_retrieval.py "${COMMON_ARGS[@]}" \
        --run-dir "$RUN_DIR/preflight" --setup-only
fi

set +e
"$MPIEXEC" -n 6 "$PYTHON" -u run_life_retrieval.py \
    "${COMMON_ARGS[@]}" --run-dir "$RUN_DIR" &
RUN_PID=$!
printf '%s\n' "$RUN_PID" > "$PIDFILE"
printf '[mpiexec_pid] %s\n' "$RUN_PID"
wait "$RUN_PID"
RUN_EXIT=$?
set -e
printf '[retrieval_exit] %s\n' "$RUN_EXIT"
if (( RUN_EXIT != 0 )); then
    printf '[scratch_preserved] %s\n' "$RUN_DIR"
    exit "$RUN_EXIT"
fi

POSEIDON_RESULTS="$RUN_DIR/POSEIDON_output/proxima_b_earthlike/retrievals"
for subdir in MultiNest_raw results samples; do
    if [[ ! -d "$POSEIDON_RESULTS/$subdir" ]]; then
        printf '[harvest_abort] missing %s; scratch preserved at %s\n' \
            "$POSEIDON_RESULTS/$subdir" "$RUN_DIR"
        exit 8
    fi
    mkdir -p "$RESULTS/$subdir"
    cp -an "$POSEIDON_RESULTS/$subdir/." "$RESULTS/$subdir/"
done
printf '[harvested] %s\n' "$RESULTS"
printf '[scratch_preserved] %s\n' "$RUN_DIR"
printf '[complete_utc] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
