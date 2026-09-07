#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LPJML_ROOT=""
INPUT_ROOT=""
CAMPAIGN_DIR=""
MPI_RANKS=""
PHASE="all"
DRY_RUN=0

usage() {
  cat <<'MSG'
Usage: run_global_a1_mpi.sh [options]

Required:
  --lpjml-root DIR    Pinned LPJmL 6.0.6 MPI checkout.
  --input-root DIR    Verified public_standard input directory.
  --campaign-dir DIR  Persistent Linux-filesystem campaign directory.
  --mpi-ranks N       MPI processes (begin conservatively, e.g. physical cores).

Options:
  --phase spinup|a1|all  Run only the requested recoverable phase (default all).
  --dry-run              Validate, generate configs, and print commands only.
  -h, --help             Show this help.

The A1 phase requires the completed natural-spinup restart in the same campaign.
MSG
}

while (($#)); do
  case "$1" in
    --lpjml-root) LPJML_ROOT="$2"; shift 2 ;;
    --input-root) INPUT_ROOT="$2"; shift 2 ;;
    --campaign-dir) CAMPAIGN_DIR="$2"; shift 2 ;;
    --mpi-ranks) MPI_RANKS="$2"; shift 2 ;;
    --phase) PHASE="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$LPJML_ROOT" || -z "$INPUT_ROOT" || -z "$CAMPAIGN_DIR" || -z "$MPI_RANKS" ]]; then
  usage >&2
  exit 2
fi
if [[ "$PHASE" != "spinup" && "$PHASE" != "a1" && "$PHASE" != "all" ]]; then
  echo "--phase must be spinup, a1, or all" >&2
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
  printf 'Expected %s; observed %s\n' "$EXPECTED_COMMIT" "${ACTUAL_COMMIT:-none}" >&2
  exit 4
fi
if [[ ! -x "$LPJML_ROOT/bin/lpjml" || ! -x "$LPJML_ROOT/bin/lpjcheck" ]]; then
  echo "LPJmL is not built under $LPJML_ROOT" >&2
  exit 4
fi
if ! command -v mpirun >/dev/null 2>&1 || ! grep -q -- '-DUSE_MPI' "$LPJML_ROOT/Makefile.inc"; then
  echo "LPJmL MPI build not detected. Run setup_lpjml_mpi.sh first." >&2
  exit 4
fi
if ((MPI_RANKS > $(nproc))); then
  echo "Refusing oversubscription: $MPI_RANKS ranks exceed $(nproc) logical CPUs." >&2
  exit 5
fi

for item in grid.clm.json soil_30arcmin_13_types.clm.json global_co2_ann_1700_2022.txt; do
  [[ -f "$INPUT_ROOT/$item" ]] || { echo "Missing input: $INPUT_ROOT/$item" >&2; exit 6; }
done

CONFIG_DIR="$CAMPAIGN_DIR/configs"
if [[ -f "$CONFIG_DIR/manifest.json" ]]; then
  for config_name in spinup_natural.json a1_2005_n.json; do
    [[ -f "$CONFIG_DIR/$config_name" ]] || {
      echo "Incomplete existing config set: $CONFIG_DIR" >&2
      exit 8
    }
  done
  if ! grep -q "\"lpjml_commit\": \"$EXPECTED_COMMIT\"" "$CONFIG_DIR/manifest.json" || \
     ! grep -q '"workflow": "global-a1"' "$CONFIG_DIR/manifest.json" || \
     ! grep -q '"mode": "global"' "$CONFIG_DIR/manifest.json"; then
    echo "Existing campaign configs do not match the pinned global A1 workflow." >&2
    exit 8
  fi
  echo "Reusing frozen campaign configs: $CONFIG_DIR"
else
  if [[ -d "$CONFIG_DIR" ]] && find "$CONFIG_DIR" -mindepth 1 -print -quit | grep -q .; then
    echo "Config directory is non-empty but has no manifest: $CONFIG_DIR" >&2
    exit 8
  fi
  mkdir -p "$CONFIG_DIR"
  python3 "$SCRIPT_DIR/prepare_configs.py" \
    --lpjml-root "$LPJML_ROOT" \
    --input-root "$INPUT_ROOT" \
    --output-dir "$CONFIG_DIR" \
    --mode global \
    --workflow global-a1
fi

export LPJROOT="$LPJML_ROOT"

run_scenario() {
  local scenario="$1"
  local config="$CONFIG_DIR/$scenario.json"
  local scenario_dir="$CAMPAIGN_DIR/$scenario"
  mkdir -p "$scenario_dir/output" "$scenario_dir/restart"

  local command=(mpirun -np "$MPI_RANKS" "$LPJML_ROOT/bin/lpjml"
    -inpath "$INPUT_ROOT"
    -outpath "$scenario_dir"
    -restartpath "$scenario_dir/restart"
    "$config")
  printf 'COMMAND:'
  printf ' %q' "${command[@]}"
  printf '\n'
  if [[ "$DRY_RUN" -eq 0 ]]; then
    "$LPJML_ROOT/bin/lpjcheck" \
      -inpath "$INPUT_ROOT" \
      -outpath "$scenario_dir" \
      -restartpath "$scenario_dir/restart" \
      "$config"
    printf 'started_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >"$scenario_dir/run_status.txt"
    "${command[@]}" >"$scenario_dir/stdout.log" 2>"$scenario_dir/stderr.log"
    printf 'completed_utc=%s\nexit_code=0\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"$scenario_dir/run_status.txt"
  fi
}

if [[ "$PHASE" == "spinup" || "$PHASE" == "all" ]]; then
  run_scenario spinup_natural
fi

if [[ "$PHASE" == "a1" || "$PHASE" == "all" ]]; then
  SPINUP_RESTART="$CAMPAIGN_DIR/spinup_natural/restart/restart_1700_nv_stdfire.lpj"
  if [[ "$DRY_RUN" -eq 0 && ! -s "$SPINUP_RESTART" ]]; then
    echo "A1 cannot start: completed spinup restart is missing: $SPINUP_RESTART" >&2
    exit 7
  fi
  mkdir -p "$CAMPAIGN_DIR/a1_2005_n/restart"
  if [[ "$DRY_RUN" -eq 0 ]]; then
    cp -p "$SPINUP_RESTART" "$CAMPAIGN_DIR/a1_2005_n/restart/"
    sha256sum "$SPINUP_RESTART" >"$CAMPAIGN_DIR/spinup_restart.sha256"
  fi
  run_scenario a1_2005_n
fi

printf 'campaign_dir=%s\n' "$CAMPAIGN_DIR"
