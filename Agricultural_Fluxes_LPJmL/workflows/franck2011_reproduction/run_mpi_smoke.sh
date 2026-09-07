#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LPJML_ROOT=""
INPUT_ROOT=""
RESULTS_DIR=""
MPI_RANKS=2
STARTGRID=27410
ENDGRID=27417

usage() {
  cat <<'MSG'
Usage: run_mpi_smoke.sh --lpjml-root DIR --input-root DIR --results-dir DIR
                        [--mpi-ranks N]

Run an eight-cell MPI interface smoke test. This validates the MPI executable,
restart hand-off, and N-output files; it is not a global scientific result.
MSG
}

while (($#)); do
  case "$1" in
    --lpjml-root) LPJML_ROOT="$2"; shift 2 ;;
    --input-root) INPUT_ROOT="$2"; shift 2 ;;
    --results-dir) RESULTS_DIR="$2"; shift 2 ;;
    --mpi-ranks) MPI_RANKS="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done
if [[ -z "$LPJML_ROOT" || -z "$INPUT_ROOT" || -z "$RESULTS_DIR" ]]; then
  usage >&2
  exit 2
fi
if ! [[ "$MPI_RANKS" =~ ^[1-8]$ ]]; then
  echo "Use 1-8 MPI ranks for the fixed eight-cell smoke test." >&2
  exit 2
fi
if [[ "$RESULTS_DIR" == /mnt/* || "$LPJML_ROOT" == /mnt/* ]]; then
  echo "Use the Linux filesystem for LPJmL and results, not /mnt/*." >&2
  exit 3
fi
if [[ ! -x "$LPJML_ROOT/bin/lpjml" ]] || ! grep -q -- '-DUSE_MPI' "$LPJML_ROOT/Makefile.inc"; then
  echo "Pinned MPI build not found. Run setup_lpjml_mpi.sh first." >&2
  exit 4
fi

CONFIG_DIR="$RESULTS_DIR/configs"
mkdir -p "$CONFIG_DIR"
python3 "$SCRIPT_DIR/prepare_configs.py" \
  --lpjml-root "$LPJML_ROOT" \
  --input-root "$INPUT_ROOT" \
  --output-dir "$CONFIG_DIR" \
  --mode pilot \
  --workflow global-a1 \
  --startgrid "$STARTGRID" \
  --endgrid "$ENDGRID"

export LPJROOT="$LPJML_ROOT"
run_scenario() {
  local scenario="$1"
  local scenario_dir="$RESULTS_DIR/$scenario"
  local config="$CONFIG_DIR/$scenario.json"
  mkdir -p "$scenario_dir/output" "$scenario_dir/restart"
  "$LPJML_ROOT/bin/lpjcheck" -inpath "$INPUT_ROOT" -outpath "$scenario_dir" \
    -restartpath "$scenario_dir/restart" "$config"
  mpirun -np "$MPI_RANKS" "$LPJML_ROOT/bin/lpjml" \
    -inpath "$INPUT_ROOT" -outpath "$scenario_dir" \
    -restartpath "$scenario_dir/restart" "$config" \
    >"$scenario_dir/stdout.log" 2>"$scenario_dir/stderr.log"
}

run_scenario spinup_natural
mkdir -p "$RESULTS_DIR/a1_2005_n/restart"
cp -p "$RESULTS_DIR/spinup_natural/restart/restart_1700_nv_stdfire.lpj" \
  "$RESULTS_DIR/a1_2005_n/restart/"
run_scenario a1_2005_n

python3 "$SCRIPT_DIR/analyze_n_fluxes.py" \
  --output-dir "$RESULTS_DIR/a1_2005_n/output" \
  --coverage pilot

printf 'mpi_smoke=PASS\nresults_dir=%s\n' "$RESULTS_DIR"

