#!/usr/bin/env bash
set -euo pipefail

# Launch matched, corrected-interface Proxima A1/A3 240 h audit retrievals
# concurrently. MultiNest writes to per-run Linux ext4 scratch; exact-prefix
# outputs are harvested into the project only after a clean exit.

REPO=/mnt/c/Proyectos/Astro/ExoFarm_MDwarfs
CAMPAIGN="$REPO/Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1"
OUT="$CAMPAIGN/retrievals"
RESULTS="$OUT/POSEIDON_output/proxima_b_earthlike/retrievals"
DATA_DIR="$CAMPAIGN/life_data"
RANKS=6
N_LIVE=800
TAG=_O2_fixedBlack1bar_noxtol_MPI6_AUDIT
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
SCRATCH="/home/dasan/exofarm_proxima_a1_a3_240h_MPI6_${RUN_ID}"

declare -A DATASET EXPECTED_SHA RUN_DIR LOG PIDFILE RETRIEVAL
DATASET[A1]="$DATA_DIR/LIFE_proxima_A1_240h.dat"
DATASET[A3]="$DATA_DIR/LIFE_proxima_A3_240h.dat"
EXPECTED_SHA[A1]=0d73c1ff91ab756bae8905024095b4482a877d39b7051af0fa2f683899a1ab0c
EXPECTED_SHA[A3]=7f04734252be9b8428ea13288d65471f861a23815723616b363b48b27efadd7b

for scenario in A1 A3; do
    RETRIEVAL[$scenario]="proxima_${scenario}_240h${TAG}"
    LOG[$scenario]="$OUT/${RETRIEVAL[$scenario]}.launch.log"
    PIDFILE[$scenario]="$OUT/${RETRIEVAL[$scenario]}.pid"
    RUN_DIR[$scenario]="$SCRATCH/$scenario"

    if [[ ! -s "${DATASET[$scenario]}" ]]; then
        printf '[abort] Missing/empty dataset: %s\n' "${DATASET[$scenario]}" >&2
        exit 3
    fi
    actual_sha="$(sha256sum "${DATASET[$scenario]}" | awk '{print $1}')"
    if [[ "$actual_sha" != "${EXPECTED_SHA[$scenario]}" ]]; then
        printf '[abort] Dataset checksum changed for %s: %s\n' \
            "$scenario" "$actual_sha" >&2
        exit 4
    fi
    for path in "${LOG[$scenario]}" "${PIDFILE[$scenario]}"; do
        if [[ -e "$path" ]]; then
            printf '[abort] Preserving existing run record: %s\n' "$path" >&2
            exit 5
        fi
    done
    for subdir in MultiNest_raw results samples; do
        for candidate in "$RESULTS/$subdir/${RETRIEVAL[$scenario]}"*; do
            if [[ -e "$candidate" ]]; then
                printf '[abort] Refusing to overwrite existing output: %s\n' \
                    "$candidate" >&2
                exit 6
            fi
        done
    done
    if ps -eo args= \
        | grep -F "run_life_retrieval.py --campaign proxima --scenario $scenario --hours 240" \
        | grep -v grep | grep -q .; then
        printf '[abort] A matching %s 240 h retrieval is already active.\n' \
            "$scenario" >&2
        exit 7
    fi
done

if [[ -e "$SCRATCH" ]]; then
    printf '[abort] Scratch path already exists; preserving it: %s\n' "$SCRATCH" >&2
    exit 8
fi

ENV_PREFIX=/home/dasan/anaconda3/envs/POSEIDON
MPIEXEC="$ENV_PREFIX/bin/mpiexec"
PYTHON="$ENV_PREFIX/bin/python"
if [[ ! -x "$MPIEXEC" || ! -x "$PYTHON" ]]; then
    printf '[abort] POSEIDON MPICH/python not available under %s\n' \
        "$ENV_PREFIX" >&2
    exit 9
fi
export CONDA_PREFIX="$ENV_PREFIX"
export CONDA_DEFAULT_ENV=POSEIDON
export PATH="$ENV_PREFIX/bin:$PATH"
export LD_LIBRARY_PATH="$ENV_PREFIX/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

export POSEIDON_input_data=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs
export PYSYN_CDBS=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids
if [[ ! -d "$POSEIDON_input_data" || ! -d "$PYSYN_CDBS" ]]; then
    printf '[abort] POSEIDON input/stellar-grid path missing.\n' >&2
    exit 10
fi
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

mkdir -p "$SCRATCH"
cd "$REPO/Thermal_Emission_Spectroscopy/scripts"

write_header() {
    local scenario="$1"
    {
        printf '[launch_attempt_utc] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
        printf '[run_id] %s\n[scenario] %s\n' "$RUN_ID" "$scenario"
        printf '[config] hours=240 N_live=%s MPI_ranks=%s X_profile=isochem ' \
            "$N_LIVE" "$RANKS"
        printf 'O2=true surface=fixed-black-at-1-bar error_inflation=none '
        printf 'x_tol=disabled R=10000 noise=diagonal\n'
        printf '[dataset] %s\n' "${DATASET[$scenario]}"
        printf '[dataset_sha256] %s\n' "${EXPECTED_SHA[$scenario]}"
        printf '[seed] from canonical dataset_index.json\n'
        printf '[scratch_run_dir] %s\n' "${RUN_DIR[$scenario]}"
        printf '[mpi_launcher] %s\n' "$MPIEXEC"
        printf '[command] %s -n %s %s -u %s/run_life_retrieval.py ' \
            "$MPIEXEC" "$RANKS" "$PYTHON" "$REPO/Thermal_Emission_Spectroscopy/scripts"
        printf -- '--campaign proxima --scenario %s --hours 240 --n-live %s ' \
            "$scenario" "$N_LIVE"
        printf -- '--error-inflation none --surface-pressure-mode fixed-black '
        printf -- '--include-o2 --x-profile isochem --output-tag %s --R 10000 ' "$TAG"
        printf -- '--dataset-file %s --run-dir %s\n' \
            "${DATASET[$scenario]}" "${RUN_DIR[$scenario]}"
    } >> "${LOG[$scenario]}"
}

start_one() {
    local scenario="$1"
    write_header "$scenario"
    "$MPIEXEC" -n "$RANKS" "$PYTHON" -u \
        "$REPO/Thermal_Emission_Spectroscopy/scripts/run_life_retrieval.py" \
        --campaign proxima --scenario "$scenario" --hours 240 \
        --n-live "$N_LIVE" --error-inflation none \
        --surface-pressure-mode fixed-black --include-o2 --x-profile isochem \
        --output-tag "$TAG" --R 10000 \
        --dataset-file "${DATASET[$scenario]}" \
        --run-dir "${RUN_DIR[$scenario]}" \
        >> "${LOG[$scenario]}" 2>&1 < /dev/null &
    local pid=$!
    printf '%s\n' "$pid" > "${PIDFILE[$scenario]}"
    printf '[started] scenario=%s mpiexec_pid=%s ranks=%s log=%s\n' \
        "$scenario" "$pid" "$RANKS" "${LOG[$scenario]}"
    printf '[started] PID=%s\n' "$pid" >> "${LOG[$scenario]}"
}

harvest_one() {
    local scenario="$1" source_root="$2" prefix="$3"
    local subdir src dest file base
    for subdir in MultiNest_raw results samples; do
        src="$source_root/POSEIDON_output/proxima_b_earthlike/retrievals/$subdir"
        dest="$RESULTS/$subdir"
        if [[ ! -d "$src" ]]; then
            printf '[harvest_blocked] missing source directory: %s\n' "$src" \
                >> "${LOG[$scenario]}"
            return 1
        fi
        shopt -s nullglob
        local matches=("$src/$prefix"*)
        shopt -u nullglob
        if (( ${#matches[@]} == 0 )); then
            printf '[harvest_blocked] no %s-prefixed files in %s\n' \
                "$prefix" "$src" >> "${LOG[$scenario]}"
            return 1
        fi
        for file in "${matches[@]}"; do
            base="$(basename "$file")"
            if [[ -e "$dest/$base" ]]; then
                printf '[harvest_blocked] destination exists; preserving both: %s\n' \
                    "$dest/$base" >> "${LOG[$scenario]}"
                return 1
            fi
        done
    done

    for subdir in MultiNest_raw results samples; do
        src="$source_root/POSEIDON_output/proxima_b_earthlike/retrievals/$subdir"
        dest="$RESULTS/$subdir"
        mkdir -p "$dest"
        cp -a -- "$src/$prefix"* "$dest/" || return 1
    done
    printf '[harvest_complete] source=%s prefix=%s\n' \
        "$source_root" "$prefix" >> "${LOG[$scenario]}"
}

start_one A1
PID_A1="$(<"${PIDFILE[A1]}")"
start_one A3
PID_A3="$(<"${PIDFILE[A3]}")"

sleep 10
for scenario in A1 A3; do
    pid="$(<"${PIDFILE[$scenario]}")"
    if kill -0 "$pid" 2>/dev/null; then
        printf '[process_confirmed] scenario=%s mpiexec_pid=%s\n' \
            "$scenario" "$pid" >> "${LOG[$scenario]}"
    else
        printf '[early_exit] scenario=%s mpiexec_pid=%s; inspect log\n' \
            "$scenario" "$pid" >> "${LOG[$scenario]}"
    fi
done

set +e
wait "$PID_A1"
EXIT_A1=$?
printf '[process_exit] mpiexec_pid=%s exit_code=%s\n' "$PID_A1" "$EXIT_A1" \
    >> "${LOG[A1]}"
set -e
if (( EXIT_A1 == 0 )); then
    harvest_one A1 "${RUN_DIR[A1]}" "${RETRIEVAL[A1]}" || EXIT_A1=20
fi

set +e
wait "$PID_A3"
EXIT_A3=$?
printf '[process_exit] mpiexec_pid=%s exit_code=%s\n' "$PID_A3" "$EXIT_A3" \
    >> "${LOG[A3]}"
set -e
if (( EXIT_A3 == 0 )); then
    harvest_one A3 "${RUN_DIR[A3]}" "${RETRIEVAL[A3]}" || EXIT_A3=20
fi

printf '[pair_complete] A1_status=%s A3_status=%s scratch=%s\n' \
    "$EXIT_A1" "$EXIT_A3" "$SCRATCH"
if (( EXIT_A1 != 0 || EXIT_A3 != 0 )); then
    exit 1
fi
