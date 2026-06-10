#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
LPJML_DIR="$PROJECT_DIR/Agricultural_Fluxes_LPJmL/software/LPJmL"
RESULTS_DIR="$SCRIPT_DIR/results"
INPUT_ROOT="${1:-${LPJINPATH:-}}"

if [[ -z "$INPUT_ROOT" ]]; then
  cat >&2 <<'MSG'
Missing LPJmL input data path.

Usage:
  ./run_lpjml_scenarios.sh /path/to/public_standard

or:
  export LPJINPATH=/path/to/public_standard
  ./run_lpjml_scenarios.sh
MSG
  exit 2
fi

required_inputs=(
  "grid.clm.json"
  "soil_30arcmin_13_types.clm.json"
  "global_co2_ann_1700_2022.txt"
  "tas_gswp3-w5e5_obsclim_1901-2019.clm.json"
  "pr_gswp3-w5e5_obsclim_1901-2019.clm.json"
)

missing=0
for item in "${required_inputs[@]}"; do
  if [[ ! -e "$INPUT_ROOT/$item" ]]; then
    echo "Missing input: $INPUT_ROOT/$item" >&2
    missing=1
  fi
done
if [[ "$missing" -ne 0 ]]; then
  exit 3
fi

mkdir -p "$RESULTS_DIR/shared_spinup/output" "$RESULTS_DIR/shared_spinup/restart"
mkdir -p "$RESULTS_DIR/modern_earth_lu/output" "$RESULTS_DIR/modern_earth_lu/restart"
mkdir -p "$RESULTS_DIR/no_synthetic_fertilizer_lu/output" "$RESULTS_DIR/no_synthetic_fertilizer_lu/restart"

cd "$LPJML_DIR"

echo "Checking spinup config..."
./bin/lpjcheck \
  -inpath "$INPUT_ROOT" \
  -outpath "$RESULTS_DIR/shared_spinup" \
  -restartpath "$RESULTS_DIR/shared_spinup/restart" \
  lpjml_config.cjson

echo "Running shared natural spinup..."
./bin/lpjml \
  -inpath "$INPUT_ROOT" \
  -outpath "$RESULTS_DIR/shared_spinup" \
  -restartpath "$RESULTS_DIR/shared_spinup/restart" \
  lpjml_config.cjson

for scenario in modern_earth_lu no_synthetic_fertilizer_lu; do
  echo "Preparing $scenario..."
  cp "$RESULTS_DIR/shared_spinup/restart/restart_1700_nv_stdfire.lpj" \
     "$RESULTS_DIR/$scenario/restart/restart_1700_nv_stdfire.lpj"

  echo "Checking $scenario config..."
  ./bin/lpjcheck \
    -DFROM_RESTART \
    -inpath "$INPUT_ROOT" \
    -outpath "$RESULTS_DIR/$scenario" \
    -restartpath "$RESULTS_DIR/$scenario/restart" \
    "$SCRIPT_DIR/configs/$scenario.cjson"

  echo "Running $scenario..."
  ./bin/lpjml \
    -DFROM_RESTART \
    -inpath "$INPUT_ROOT" \
    -outpath "$RESULTS_DIR/$scenario" \
    -restartpath "$RESULTS_DIR/$scenario/restart" \
    "$SCRIPT_DIR/configs/$scenario.cjson"
done

cat <<MSG
Done.

Scenario outputs:
  $RESULTS_DIR/modern_earth_lu/output
  $RESULTS_DIR/no_synthetic_fertilizer_lu/output
MSG
