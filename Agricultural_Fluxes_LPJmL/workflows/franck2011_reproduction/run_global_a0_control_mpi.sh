#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LPJML_ROOT=""
INPUT_ROOT=""
CAMPAIGN_DIR=""
MPI_RANKS=""
DRY_RUN=0

usage() {
  cat <<'MSG'
Usage: run_global_a0_control_mpi.sh [options]

Required:
  --lpjml-root DIR    Pinned LPJmL 6.0.6 MPI checkout.
  --input-root DIR    Verified public_standard input directory.
  --campaign-dir DIR  Existing campaign containing spinup_natural/restart.
  --mpi-ranks N       MPI processes.

Options:
  --dry-run            Validate inputs and print the command only.
  -h, --help           Show this help.
MSG
}

while (($#)); do
  case "$1" in
    --lpjml-root) LPJML_ROOT="$2"; shift 2 ;;
    --input-root) INPUT_ROOT="$2"; shift 2 ;;
    --campaign-dir) CAMPAIGN_DIR="$2"; shift 2 ;;
    --mpi-ranks) MPI_RANKS="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$LPJML_ROOT" || -z "$INPUT_ROOT" || -z "$CAMPAIGN_DIR" || -z "$MPI_RANKS" ]]; then
  usage >&2
  exit 2
fi
if ! [[ "$MPI_RANKS" =~ ^[1-9][0-9]*$ ]]; then
  echo "--mpi-ranks must be a positive integer" >&2
  exit 2
fi
if [[ "$CAMPAIGN_DIR" == /mnt/* || "$LPJML_ROOT" == /mnt/* ]]; then
  echo "Put LPJmL and campaign outputs on the Linux filesystem, not /mnt/*." >&2
  exit 3
fi

EXPECTED_COMMIT="5af44a1ed023279a23c28d6dfe76945b97aaac57"
ACTUAL_COMMIT="$(git -C "$LPJML_ROOT" rev-parse HEAD 2>/dev/null || true)"
if [[ "$ACTUAL_COMMIT" != "$EXPECTED_COMMIT" ]]; then
  echo "LPJmL source is not the pinned v6.0.6 commit." >&2
  exit 4
fi
if [[ ! -x "$LPJML_ROOT/bin/lpjml" || ! -x "$LPJML_ROOT/bin/lpjcheck" ]]; then
  echo "LPJmL is not built under $LPJML_ROOT" >&2
  exit 4
fi
if ! command -v mpirun >/dev/null 2>&1 || ! grep -q -- '-DUSE_MPI' "$LPJML_ROOT/Makefile.inc"; then
  echo "LPJmL MPI build not detected." >&2
  exit 4
fi
if ((MPI_RANKS > $(nproc))); then
  echo "Refusing oversubscription: $MPI_RANKS ranks exceed $(nproc) logical CPUs." >&2
  exit 5
fi
for item in grid.clm.json soil_30arcmin_13_types.clm.json global_co2_ann_1700_2022.txt; do
  [[ -f "$INPUT_ROOT/$item" ]] || { echo "Missing input: $INPUT_ROOT/$item" >&2; exit 6; }
done

RESTART="$CAMPAIGN_DIR/spinup_natural/restart/restart_1700_nv_stdfire.lpj"
if [[ ! -s "$RESTART" ]]; then
  echo "A0 cannot start: accepted natural-spinup restart is missing: $RESTART" >&2
  exit 7
fi

CONFIG_DIR="$CAMPAIGN_DIR/configs_a0_control"
if [[ ! -f "$CONFIG_DIR/manifest.json" ]]; then
  mkdir -p "$CONFIG_DIR"
  python3 "$SCRIPT_DIR/prepare_configs.py" \
    --lpjml-root "$LPJML_ROOT" \
    --input-root "$INPUT_ROOT" \
    --output-dir "$CONFIG_DIR" \
    --mode global \
    --workflow global-a0-control
fi
if ! grep -q '"workflow": "global-a0-control"' "$CONFIG_DIR/manifest.json"; then
  echo "A0 config manifest has an unexpected workflow." >&2
  exit 8
fi

A0_DIR="$CAMPAIGN_DIR/a0_natural"
mkdir -p "$A0_DIR/output" "$A0_DIR/restart"
if [[ -f "$A0_DIR/run_status.txt" ]] && grep -q 'exit_code=0' "$A0_DIR/run_status.txt"; then
  echo "Completed A0 control retained: $A0_DIR"
  exit 0
fi
if [[ ! -s "$A0_DIR/restart/restart_1700_nv_stdfire.lpj" ]]; then
  cp -p "$RESTART" "$A0_DIR/restart/"
fi

CONFIG="$CONFIG_DIR/a0_natural.json"
CHECKPOINT_CONFIG="$A0_DIR/checkpoint_config.json"
if [[ ! -f "$CHECKPOINT_CONFIG" ]]; then
  python3 - "$CONFIG" "$CHECKPOINT_CONFIG" "$A0_DIR/restart/checkpoint.lpj" <<'PY'
import json
from pathlib import Path
import sys

config = json.loads(Path(sys.argv[1]).read_text())
config["checkpoint_filename"] = sys.argv[3]
Path(sys.argv[2]).write_text(json.dumps(config, indent=2) + "\n")
PY
fi

COMMAND=(mpirun -np "$MPI_RANKS" "$LPJML_ROOT/bin/lpjml"
  -inpath "$INPUT_ROOT"
  -outpath "$A0_DIR"
  -restartpath "$A0_DIR/restart"
  "$CHECKPOINT_CONFIG")
printf 'COMMAND:'
printf ' %q' "${COMMAND[@]}"
printf '\n'
if ((DRY_RUN)); then
  exit 0
fi

# lpjcheck uses LPJROOT to locate the build metadata; keep it pinned to the
# same local executable tree used by the MPI run.
export LPJROOT="$LPJML_ROOT"
"$LPJML_ROOT/bin/lpjcheck" \
  -inpath "$INPUT_ROOT" \
  -outpath "$A0_DIR" \
  -restartpath "$A0_DIR/restart" \
  "$CHECKPOINT_CONFIG"
printf 'started_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >"$A0_DIR/run_status.txt"
printf 'A0_RUNNING %s\n' "$(date -Is)" >"$CAMPAIGN_DIR/campaign_status.txt"
python3 "$SCRIPT_DIR/checkpoint_runner.py" \
  --config "$CHECKPOINT_CONFIG" \
  --phase-dir "$A0_DIR" \
  --interval-seconds 3600 \
  -- "${COMMAND[@]}" \
  >>"$A0_DIR/controller.log" 2>>"$A0_DIR/controller.stderr.log"
printf 'completed_utc=%s\nexit_code=0\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"$A0_DIR/run_status.txt"
printf 'A0_COMPLETE_PENDING_VALIDATION %s\n' "$(date -Is)" >"$CAMPAIGN_DIR/campaign_status.txt"
