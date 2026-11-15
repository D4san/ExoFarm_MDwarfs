#!/usr/bin/env bash
set -euo pipefail

# Independent-noise repeat of the official A1 1 h retrieval.
# Keeps the official dataset/products untouched and harvests only after exit 0.

REPO=/mnt/c/Proyectos/Astro/ExoFarm_MDwarfs
CAMPAIGN="$REPO/Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1"
DATA="$CAMPAIGN/life_data"
RETRIEVALS="$CAMPAIGN/retrievals"
RESULTS="$RETRIEVALS/POSEIDON_output/proxima_b_earthlike/retrievals"
SCENARIO=A1
HOURS=1
MASTER_SEED=20261002
DATA_SUFFIX=_O2_fixedBlack1bar_noiseRepeat2
DATASET_REL="Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A1_1h${DATA_SUFFIX}.dat"
DATASET="$REPO/$DATASET_REL"
INDEX="$DATA/dataset_index_A1_1h_noiseRepeat2.json"
TAG=_O2_fixedBlack1bar_noxtol_MPI6_NOISE2
RETRIEVAL="proxima_A1_1h${TAG}"
LOG="$RETRIEVALS/${RETRIEVAL}.launch.log"
PIDFILE="$RETRIEVALS/${RETRIEVAL}.pid"
RUN_DIR=/home/dasan/exofarm_proxima_a1_1h_noise_repeat2_20261001/retrieval
CANONICAL_INDEX="$DATA/dataset_index.json"
OFFICIAL_DATASET="$DATA/LIFE_proxima_A1_1h_O2_fixedBlack1bar_official.dat"

for path in "$DATASET" "$INDEX" "$LOG" "$PIDFILE" "$RUN_DIR"; do
    if [[ -e "$path" ]]; then
        printf '[abort] preserving existing path: %s\n' "$path" >&2
        exit 2
    fi
done

for subdir in MultiNest_raw results samples; do
    if [[ -d "$RESULTS/$subdir" ]] && \
            find "$RESULTS/$subdir" -maxdepth 1 -name "${RETRIEVAL}*" \
                -print -quit | grep -q .; then
        printf '[abort] matching harvested products exist; refusing overwrite\n' >&2
        exit 3
    fi
done

if ps -eo args= | grep -F 'run_life_retrieval.py --campaign proxima --scenario A1 --hours 1 ' \
        | grep -v 'grep -'; then
    printf '[abort] a Proxima A1 1 h retrieval process is already active\n' >&2
    exit 4
fi

mkdir -p "$RETRIEVALS"
( set -o noclobber; : > "$LOG" )
printf '%s\n' "$$" > "$PIDFILE"
exec >>"$LOG" 2>&1

printf '[launch_utc] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
printf '[scenario] A1\n[hours] 1\n[mpi_ranks] 6\n'
printf '[master_seed] %s\n[dataset] %s\n' "$MASTER_SEED" "$DATASET_REL"
printf '[scratch] %s\n' "$RUN_DIR"
printf '[config] POSEIDON/MPICH conda=POSEIDON X_profile=isochem N_live=800 '
printf 'error_inflation=none x_tol=disabled O2=true surface=fixed-black-1bar R=10000 bins=31\n'

source /home/dasan/anaconda3/etc/profile.d/conda.sh
conda activate POSEIDON
MPIEXEC="$CONDA_PREFIX/bin/mpiexec"
PYTHON="$CONDA_PREFIX/bin/python"
if [[ ! -x "$MPIEXEC" || ! -x "$PYTHON" ]]; then
    printf '[abort] POSEIDON Python or MPICH mpiexec is unavailable\n'
    exit 5
fi
export POSEIDON_input_data=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs
export PYSYN_CDBS=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cd "$REPO/Thermal_Emission_Spectroscopy/scripts"

CANONICAL_SHA_BEFORE=$(sha256sum "$CANONICAL_INDEX" | awk '{print $1}')
"$PYTHON" -u make_life_datasets.py \
    --campaign proxima --scenarios A1 --hours 1 --seed "$MASTER_SEED" \
    --name-suffix "$DATA_SUFFIX" \
    --index-output "$INDEX" \
    --index-classification audit_independent_noise_repeat_A1_1h_excluded_from_canonical_8of8

"$PYTHON" - "$DATASET" "$INDEX" "$CANONICAL_INDEX" \
    "$CANONICAL_SHA_BEFORE" "$OFFICIAL_DATASET" <<'PY'
import hashlib
import json
import sys

import numpy as np

dataset_path, index_path, canonical_path, expected_sha, official_path = sys.argv[1:]
index = json.load(open(index_path, encoding="utf-8"))
if index.get("classification") != "audit_independent_noise_repeat_A1_1h_excluded_from_canonical_8of8":
    raise SystemExit("[abort] unexpected repeat-dataset classification")
rows = index.get("datasets", [])
if len(rows) != 1 or rows[0].get("scenario") != "A1" or rows[0].get("hours") != 1.0:
    raise SystemExit("[abort] repeat index must contain only A1 at 1 h")
actual_sha = hashlib.sha256(open(canonical_path, "rb").read()).hexdigest()
if actual_sha != expected_sha:
    raise SystemExit("[abort] canonical 8/8 dataset index changed")
repeat = np.loadtxt(dataset_path, skiprows=1)
official = np.loadtxt(official_path, skiprows=1)
if repeat.shape != (31, 4) or official.shape != (31, 4):
    raise SystemExit(f"[abort] expected two 31x4 datasets, got {repeat.shape}, {official.shape}")
if not np.isfinite(repeat).all() or np.any(repeat[:, 1] <= 0) or np.any(repeat[:, 3] <= 0):
    raise SystemExit("[abort] repeat dataset contains invalid bins or uncertainties")
if not np.allclose(repeat[:, [0, 1, 3]], official[:, [0, 1, 3]], rtol=0.0, atol=1e-12):
    raise SystemExit("[abort] repeat grid/widths/sigma differ from the official A1 1 h dataset")
if np.array_equal(repeat[:, 2], official[:, 2]):
    raise SystemExit("[abort] repeat flux is identical to the official noise realization")
old = json.load(open(index_path.replace("dataset_index_A1_1h_noiseRepeat2.json",
                                         "dataset_index_A1_A3_1h_official.json"), encoding="utf-8"))
old_seed = next(row["seed"] for row in old["datasets"] if row["scenario"] == "A1")
new_seed = rows[0]["seed"]
if new_seed == old_seed:
    raise SystemExit("[abort] repeat noise seed matches the official A1 seed")
print(f"[dataset_validated] seed={new_seed} bins=31 independent_noise=true")
print(f"[canonical_index_sha256_unchanged] {actual_sha}")
PY

sha256sum "$DATASET" "$INDEX"
COMMON_ARGS=(
    --campaign proxima --scenario A1 --hours 1 --n-live 800
    --error-inflation none --surface-pressure-mode fixed-black --include-o2
    --x-profile isochem --output-tag "$TAG" --R 10000
    --dataset-file "$DATASET_REL"
)
mkdir -p "$RUN_DIR/preflight"
"$PYTHON" -u run_life_retrieval.py "${COMMON_ARGS[@]}" \
    --run-dir "$RUN_DIR/preflight" --setup-only

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
