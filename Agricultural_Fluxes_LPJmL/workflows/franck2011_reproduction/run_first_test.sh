#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
LPJML_DIR="${LPJML_ROOT:-$PROJECT_DIR/Agricultural_Fluxes_LPJmL/software/LPJmL}"
INPUT_ROOT="${LPJINPATH:-/mnt/c/Proyetos/Data/LPJmL/public_standard}"
RESULTS_BASE="$SCRIPT_DIR/results"
export LPJROOT="$LPJML_DIR"
MODE="pilot"
STARTGRID=27410
RUN_POTENTIAL=0
POTENTIAL_ONLY=0
WITH_METHANE=0
CROP_ONLY=0

usage() {
  cat <<'MSG'
Usage: run_first_test.sh [options]

Options:
  --input-root PATH     LPJmL public_standard directory.
  --lpjml-root PATH     LPJmL checkout/build to execute.
  --results-root PATH   Directory holding pilot results.
  --mode pilot|global  Pilot is a one-cell interface test; global is scientific.
  --startgrid INDEX    Cell used by pilot mode (default: 27410).
  --with-potential     Also run the unlimited-N all-crops yield branch.
  --potential-only     Run spin-up and the potential-yield branch only.
  --with-methane       Enable methane/oxygen dynamics and CH4 outputs.
  --crop-only          Disable pasture, livestock grazing and manure.
  -h, --help           Show this help.
MSG
}

while (($#)); do
  case "$1" in
    --input-root)
      INPUT_ROOT="$2"
      shift 2
      ;;
    --lpjml-root)
      LPJML_DIR="$2"
      shift 2
      ;;
    --results-root)
      RESULTS_BASE="$2"
      shift 2
      ;;
    --mode)
      MODE="$2"
      shift 2
      ;;
    --startgrid)
      STARTGRID="$2"
      shift 2
      ;;
    --with-potential)
      RUN_POTENTIAL=1
      shift
      ;;
    --potential-only)
      RUN_POTENTIAL=1
      POTENTIAL_ONLY=1
      shift
      ;;
    --with-methane)
      WITH_METHANE=1
      shift
      ;;
    --crop-only)
      CROP_ONLY=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ "$MODE" != "pilot" && "$MODE" != "global" ]]; then
  echo "--mode must be pilot or global" >&2
  exit 2
fi

required_inputs=(
  grid.clm.json
  soil_30arcmin_13_types.clm.json
  global_co2_ann_1700_2022.txt
  tas_gswp3-w5e5_obsclim_1901-2019.clm.json
  pr_gswp3-w5e5_obsclim_1901-2019.clm.json
)
for item in "${required_inputs[@]}"; do
  if [[ ! -e "$INPUT_ROOT/$item" ]]; then
    echo "Missing input: $INPUT_ROOT/$item" >&2
    exit 3
  fi
done

if [[ ! -x "$LPJML_DIR/bin/lpjml" || ! -x "$LPJML_DIR/bin/lpjcheck" ]]; then
  echo "LPJmL is not compiled under $LPJML_DIR" >&2
  exit 4
fi

CAMPAIGN="${MODE}_$(date -u +%Y%m%dT%H%M%SZ)"
RESULTS_DIR="$RESULTS_BASE/$CAMPAIGN"
CONFIG_DIR="$RESULTS_DIR/configs"

PREPARE_ARGS=(
  --lpjml-root "$LPJML_DIR"
  --input-root "$INPUT_ROOT"
  --output-dir "$CONFIG_DIR"
  --mode "$MODE"
  --startgrid "$STARTGRID"
)
if [[ "$WITH_METHANE" -eq 1 ]]; then
  PREPARE_ARGS+=(--with-methane)
fi
if [[ "$CROP_ONLY" -eq 1 ]]; then
  PREPARE_ARGS+=(--crop-only)
fi

python3 "$SCRIPT_DIR/prepare_configs.py" "${PREPARE_ARGS[@]}"

mkdir -p "$RESULTS_DIR/spinup_natural/output" \
  "$RESULTS_DIR/spinup_natural/restart"

cd "$LPJML_DIR"

run_checked() {
  local scenario="$1"
  local config="$2"
  local scenario_dir="$RESULTS_DIR/$scenario"
  mkdir -p "$scenario_dir/output" "$scenario_dir/restart"

  ./bin/lpjcheck \
    -inpath "$INPUT_ROOT" \
    -outpath "$scenario_dir" \
    -restartpath "$scenario_dir/restart" \
    "$config"

  ./bin/lpjml \
    -inpath "$INPUT_ROOT" \
    -outpath "$scenario_dir" \
    -restartpath "$scenario_dir/restart" \
    "$config" \
    >"$scenario_dir/stdout.log" \
    2>"$scenario_dir/stderr.log"
}

run_checked spinup_natural "$CONFIG_DIR/spinup_natural.json"

if [[ "$POTENTIAL_ONLY" -eq 0 ]]; then
  for scenario in a1_2005_n; do
    mkdir -p "$RESULTS_DIR/$scenario/restart"
    cp "$RESULTS_DIR/spinup_natural/restart/restart_1700_nv_stdfire.lpj" \
      "$RESULTS_DIR/$scenario/restart/restart_1700_nv_stdfire.lpj"
    run_checked "$scenario" "$CONFIG_DIR/$scenario.json"
  done
fi

if [[ "$RUN_POTENTIAL" -eq 1 ]]; then
  scenario=potential_yield_unlimited_n
  mkdir -p "$RESULTS_DIR/$scenario/restart"
  cp "$RESULTS_DIR/spinup_natural/restart/restart_1700_nv_stdfire.lpj" \
    "$RESULTS_DIR/$scenario/restart/restart_1700_nv_stdfire.lpj"
  run_checked "$scenario" "$CONFIG_DIR/$scenario.json"
fi

printf '%s\n' "$RESULTS_DIR"
