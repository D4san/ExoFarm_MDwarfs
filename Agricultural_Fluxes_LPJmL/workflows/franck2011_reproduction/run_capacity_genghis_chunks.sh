#!/usr/bin/env bash
set -euo pipefail

# Memory-safe execution for the final FR-genghis-khan-crop-only branch.  The
# methane-enabled natural spinup is run once on the global grid.  The managed
# crop-only year is then evaluated in sequential cell blocks; local blocks
# cannot reconstruct LPJmL's global river-neighbour graph, so routing and
# reservoirs are disabled for this execution layer and recorded in the
# campaign manifest.  The generated crop map itself remains global and is
# validated against the full-cell map contract.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LPJML_ROOT="${LPJML_ROOT:-/home/dasan/exofarm-lpjml-runtime/LPJmL-6.0.6-balance-fix-20260912}"
INPUT_ROOT="${LPJ_INPUT_ROOT:-/home/dasan/lpjml-data/public_standard}"
CAMPAIGN_DIR="${GENGHIS_CHUNKS_DIR:-/home/dasan/exofarm-lpjml-runs/fr_genghis_final_20260922_chunks}"
LANDUSE_META=""
A0_RESTART="${A0_RESTART:-/home/dasan/exofarm-lpjml-runs/global_a1_checkpoints_20260909/a0_natural/restart/restart_1700_nv_stdfire.lpj}"
MPI_RANKS="${MPI_RANKS:-1}"
CHUNK_SIZE="${CHUNK_SIZE:-8000}"
CHECKPOINT_INTERVAL="${CHECKPOINT_INTERVAL_SECONDS:-3600}"
PHASE="all"
DRY_RUN=0

usage() {
  cat <<'MSG'
Usage: run_capacity_genghis_chunks.sh --landuse-meta FILE [options]

Options:
  --lpjml-root DIR       Pinned LPJmL checkout.
  --input-root DIR       public_standard input root.
  --campaign-dir DIR     Linux-filesystem campaign directory.
  --landuse-meta FILE    Crop-only CLM metadata from build_capacity_landuse.py.
  --a0-restart FILE      Validated natural A0 restart for methane spinup.
  --mpi-ranks N          MPI processes per launch (default 1).
  --chunk-size N         Managed cells per sequential block (default 8000).
  --phase spinup|managed|all
  --dry-run              Print commands and configs without running LPJmL.
MSG
}

while (($#)); do
  case "$1" in
    --lpjml-root) LPJML_ROOT="$2"; shift 2 ;;
    --input-root) INPUT_ROOT="$2"; shift 2 ;;
    --campaign-dir) CAMPAIGN_DIR="$2"; shift 2 ;;
    --landuse-meta) LANDUSE_META="$2"; shift 2 ;;
    --a0-restart) A0_RESTART="$2"; shift 2 ;;
    --mpi-ranks) MPI_RANKS="$2"; shift 2 ;;
    --chunk-size) CHUNK_SIZE="$2"; shift 2 ;;
    --phase) PHASE="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -n "$LANDUSE_META" ]] || { usage >&2; exit 2; }
[[ "$PHASE" == spinup || "$PHASE" == managed || "$PHASE" == all ]] || exit 2
[[ "$MPI_RANKS" =~ ^[1-9][0-9]*$ ]] || exit 2
[[ "$CHUNK_SIZE" =~ ^[1-9][0-9]*$ ]] || exit 2
[[ "$CAMPAIGN_DIR" != /mnt/* && "$LPJML_ROOT" != /mnt/* ]] || exit 3

EXPECTED_COMMIT="5af44a1ed023279a23c28d6dfe76945b97aaac57"
[[ "$(git -C "$LPJML_ROOT" rev-parse HEAD 2>/dev/null || true)" == "$EXPECTED_COMMIT" ]] || exit 4
[[ -x "$LPJML_ROOT/bin/lpjml" && -x "$LPJML_ROOT/bin/lpjcheck" ]] || exit 4
command -v mpirun >/dev/null 2>&1 || exit 4
((MPI_RANKS <= $(nproc))) || exit 5
[[ -s "$A0_RESTART" ]] || { echo "Missing A0 restart: $A0_RESTART" >&2; exit 6; }
[[ -s "$LANDUSE_META" ]] || { echo "Missing map metadata: $LANDUSE_META" >&2; exit 6; }
LANDUSE_FILE="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["filename"])' "$LANDUSE_META")"
[[ -s "$(dirname "$LANDUSE_META")/$LANDUSE_FILE" ]] || exit 6

mkdir -p "$CAMPAIGN_DIR/configs" "$CAMPAIGN_DIR/chunks"
LOCK_DIR="$CAMPAIGN_DIR/campaign.lock.d"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "Campaign already locked: $CAMPAIGN_DIR" >&2
  exit 9
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT
exec >>"$CAMPAIGN_DIR/launcher.log" 2>&1
trap 'echo FAILED $(date -Is) >"$CAMPAIGN_DIR/campaign_status.txt"' ERR
unset OMP_NUM_THREADS OMP_THREAD_LIMIT
export OPENBLAS_NUM_THREADS=1

CONFIG_DIR="$CAMPAIGN_DIR/configs"
if [[ ! -f "$CONFIG_DIR/manifest.json" ]] || ! grep -q '"with_methane": true' "$CONFIG_DIR/spinup_natural.json" 2>/dev/null; then
  python3 "$SCRIPT_DIR/prepare_configs.py" \
    --lpjml-root "$LPJML_ROOT" --input-root "$INPUT_ROOT" \
    --output-dir "$CONFIG_DIR" --mode global --workflow global-a1 \
    --with-methane --crop-only
fi
PATCHED_CONFIG="$CONFIG_DIR/genghis_khan_crop_only.json"
if [[ ! -f "$PATCHED_CONFIG" ]]; then
  python3 "$SCRIPT_DIR/patch_crop_only_config.py" \
    --source "$CONFIG_DIR/a1_2005_n.json" --output "$PATCHED_CONFIG" \
    --landuse-meta "$LANDUSE_META" --year 2005
fi

NCell="$(python3 - "$INPUT_ROOT/grid.clm.json" <<'PY'
import json, sys
print(int(json.load(open(sys.argv[1]))["ncell"]))
PY
)"
printf 'campaign=%s\nncell=%s\nchunk_size=%s\nmpi_ranks=%s\nmap_metadata=%s\n' \
  "$CAMPAIGN_DIR" "$NCell" "$CHUNK_SIZE" "$MPI_RANKS" "$LANDUSE_META" >"$CAMPAIGN_DIR/manifest_runtime.txt"

make_chunk_config() {
  local source="$1" target="$2" checkpoint="$3" start="$4" end="$5"
  python3 - "$source" "$target" "$checkpoint" "$start" "$end" <<'PY'
import json, sys
source, target, checkpoint = sys.argv[1:4]
start, end = int(sys.argv[4]), int(sys.argv[5])
config = json.load(open(source))
config["startgrid"] = start
config["endgrid"] = end
config["checkpoint_filename"] = checkpoint
# A local block cannot build a valid global river-neighbour graph.  Preserve
# crop irrigation physics while disabling only cross-cell routing/reservoirs.
config["river_routing"] = False
config["reservoir"] = False
json.dump(config, open(target, "w"), indent=2)
open(target, "a").write("\n")
PY
}

run_phase() {
  local phase_dir="$1" config="$2" phase_name="$3" restart_source="$4"
  mkdir -p "$phase_dir/output" "$phase_dir/restart"
  if [[ -f "$phase_dir/run_status.txt" ]] && grep -q '^exit_code=0$' "$phase_dir/run_status.txt"; then
    echo "Completed phase retained: $phase_name"
    return
  fi
  if [[ -n "$restart_source" && ! -s "$phase_dir/restart/restart_1700_nv_stdfire.lpj" ]]; then
    cp -p "$restart_source" "$phase_dir/restart/restart_1700_nv_stdfire.lpj"
    sha256sum "$restart_source" >"$phase_dir/source_restart.sha256"
  fi
  local checkpoint_config="$phase_dir/checkpoint_config.json"
  local command=(mpirun -np "$MPI_RANKS" "$LPJML_ROOT/bin/lpjml" \
    -inpath "$INPUT_ROOT" -outpath "$phase_dir" -restartpath "$phase_dir/restart" "$checkpoint_config")
  printf 'PHASE %s COMMAND:' "$phase_name"; printf ' %q' "${command[@]}"; printf '\n'
  [[ "$DRY_RUN" -eq 0 ]] || return
  "$LPJML_ROOT/bin/lpjcheck" -inpath "$INPUT_ROOT" -outpath "$phase_dir" \
    -restartpath "$phase_dir/restart" "$checkpoint_config" >"$phase_dir/lpjcheck.log" 2>&1
  printf 'phase=%s\nstarted_utc=%s\n' "$phase_name" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >"$phase_dir/run_status.txt"
  python3 "$SCRIPT_DIR/checkpoint_runner.py" --config "$checkpoint_config" \
    --phase-dir "$phase_dir" --interval-seconds "$CHECKPOINT_INTERVAL" -- \
    "${command[@]}" >>"$phase_dir/controller.log" 2>>"$phase_dir/controller.stderr.log"
  printf 'completed_utc=%s\nexit_code=0\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"$phase_dir/run_status.txt"
}

if [[ "$PHASE" == spinup || "$PHASE" == all ]]; then
  SPINUP_DIR="$CAMPAIGN_DIR/spinup_natural"
  mkdir -p "$SPINUP_DIR/output" "$SPINUP_DIR/restart"
  if [[ ! -f "$SPINUP_DIR/checkpoint_config.json" ]]; then
    make_chunk_config "$CONFIG_DIR/spinup_natural.json" \
      "$SPINUP_DIR/checkpoint_config.json" "$SPINUP_DIR/restart/checkpoint.lpj" 0 $((NCell-1))
  fi
  echo "GENGHIS_SPINUP_RUNNING $(date -Is)" >"$CAMPAIGN_DIR/campaign_status.txt"
  run_phase "$SPINUP_DIR" "$CONFIG_DIR/spinup_natural.json" methane_spinup "$A0_RESTART"
  if [[ "$DRY_RUN" -eq 0 ]]; then
    [[ -s "$SPINUP_DIR/restart/restart_1700_nv_stdfire.lpj" ]] || { echo "Missing methane spinup restart" >&2; exit 7; }
    echo "GENGHIS_SPINUP_COMPLETE $(date -Is)" >"$CAMPAIGN_DIR/campaign_status.txt"
  fi
fi

if [[ "$PHASE" == managed || "$PHASE" == all ]]; then
  SPINUP_RESTART="$CAMPAIGN_DIR/spinup_natural/restart/restart_1700_nv_stdfire.lpj"
  [[ "$DRY_RUN" -eq 1 || -s "$SPINUP_RESTART" ]] || { echo "Missing methane spinup restart" >&2; exit 7; }
  echo "GENGHIS_MANAGED_RUNNING $(date -Is)" >"$CAMPAIGN_DIR/campaign_status.txt"
  for ((start=0; start<NCell; start+=CHUNK_SIZE)); do
    end=$((start + CHUNK_SIZE - 1)); ((end < NCell)) || end=$((NCell-1))
    tag=$(printf '%05d_%05d' "$start" "$end")
    phase_dir="$CAMPAIGN_DIR/chunks/$tag/managed_crop_only"
    mkdir -p "$phase_dir/output" "$phase_dir/restart"
    if [[ -f "$phase_dir/run_status.txt" ]] && grep -q '^exit_code=0$' "$phase_dir/run_status.txt"; then
      continue
    fi
    if [[ ! -s "$phase_dir/restart/restart_1700_nv_stdfire.lpj" && "$DRY_RUN" -eq 0 ]]; then
      cp -p "$SPINUP_RESTART" "$phase_dir/restart/restart_1700_nv_stdfire.lpj"
      sha256sum "$SPINUP_RESTART" >"$phase_dir/source_restart.sha256"
    fi
    make_chunk_config "$PATCHED_CONFIG" "$phase_dir/checkpoint_config.json" \
      "$phase_dir/restart/checkpoint.lpj" "$start" "$end"
    run_phase "$phase_dir" "$PATCHED_CONFIG" "managed_crop_only_${tag}" ""
  done
  [[ "$DRY_RUN" -eq 0 ]] && echo "GENGHIS_COMPLETE $(date -Is)" >"$CAMPAIGN_DIR/campaign_status.txt"
fi

printf 'campaign_dir=%s\nncell=%s\nchunk_size=%s\nmpi_ranks=%s\nmap_metadata=%s\nmap_sha256=%s\n' \
  "$CAMPAIGN_DIR" "$NCell" "$CHUNK_SIZE" "$MPI_RANKS" "$LANDUSE_META" \
  "$(sha256sum "$(dirname "$LANDUSE_META")/$LANDUSE_FILE" | awk '{print $1}')"
