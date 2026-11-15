#!/usr/bin/env bash
set -euo pipefail

# Run the Franck candidate stage in bounded cell blocks.  LPJmL keeps a large
# per-cell state even with MPI, so each block uses one rank; independent blocks
# may run concurrently when MAX_PARALLEL is raised above its conservative default.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LPJML_ROOT="${LPJML_ROOT:-/home/dasan/exofarm-lpjml-runtime/LPJmL-6.0.6-balance-fix-20260912}"
INPUT_ROOT="${LPJ_INPUT_ROOT:-/home/dasan/lpjml-data/public_standard}"
CAMPAIGN_DIR="${CAPACITY_POTENTIAL_CHUNKS_DIR:-/home/dasan/exofarm-lpjml-runs/fr_genghis_potential_20260922_chunks_ch4}"
A0_RESTART="${A0_RESTART:-/home/dasan/exofarm-lpjml-runs/global_a1_checkpoints_20260909/a0_natural/restart/restart_1700_nv_stdfire.lpj}"
MPI_RANKS="${MPI_RANKS:-1}"
CHUNK_SIZE="${CHUNK_SIZE:-12000}"
MAX_PARALLEL="${MAX_PARALLEL:-1}"
MAX_ARCHIVED_CHECKPOINTS="${MAX_ARCHIVED_CHECKPOINTS:-0}"
CHECKPOINT_INTERVAL="${CHECKPOINT_INTERVAL_SECONDS:-3600}"

EXPECTED_COMMIT="5af44a1ed023279a23c28d6dfe76945b97aaac57"
[[ "$(git -C "$LPJML_ROOT" rev-parse HEAD 2>/dev/null || true)" == "$EXPECTED_COMMIT" ]] || {
  echo "LPJmL source is not the pinned balance-fix commit" >&2; exit 4;
}
[[ -x "$LPJML_ROOT/bin/lpjml" && -x "$LPJML_ROOT/bin/lpjcheck" ]] || exit 4
command -v mpirun >/dev/null 2>&1 || exit 4
((MPI_RANKS >= 1 && MPI_RANKS <= $(nproc))) || exit 5
((CHUNK_SIZE >= 1)) || exit 5
[[ "$MAX_PARALLEL" =~ ^[1-9][0-9]*$ ]] || exit 5
[[ "$MAX_ARCHIVED_CHECKPOINTS" =~ ^(0|[1-9][0-9]*)$ ]] || exit 5
((MAX_PARALLEL * MPI_RANKS <= $(nproc))) || exit 5
[[ -s "$A0_RESTART" ]] || { echo "Missing A0 restart: $A0_RESTART" >&2; exit 6; }

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

if [[ ! -f "$CAMPAIGN_DIR/configs/manifest.json" ]] || ! grep -q '"with_methane": true' "$CAMPAIGN_DIR/configs/spinup_natural.json" 2>/dev/null; then
  python3 "$SCRIPT_DIR/prepare_configs.py" \
    --lpjml-root "$LPJML_ROOT" \
    --input-root "$INPUT_ROOT" \
    --output-dir "$CAMPAIGN_DIR/configs" \
    --mode global \
    --workflow franck2011 \
    --with-methane \
    --crop-only
fi

NCell="$(python3 - "$INPUT_ROOT/grid.clm.json" <<'PY'
import json
import sys
d=json.load(open(sys.argv[1]))
print(int(d["ncell"]))
PY
)"
printf 'campaign=%s\nncell=%s\nchunk_size=%s\nmpi_ranks_per_chunk=%s\nmax_parallel_chunks=%s\nmax_archived_checkpoints=%s\n' \
  "$CAMPAIGN_DIR" "$NCell" "$CHUNK_SIZE" "$MPI_RANKS" \
  "$MAX_PARALLEL" "$MAX_ARCHIVED_CHECKPOINTS" >"$CAMPAIGN_DIR/manifest_runtime.txt"
echo "POTENTIAL_CHUNKS_RUNNING $(date -Is)" >"$CAMPAIGN_DIR/campaign_status.txt"

run_chunk() {
  local start="$1" end="$2" tag="$3"
  local phase_dir="$CAMPAIGN_DIR/chunks/$tag"
  local checkpoint_config="$phase_dir/checkpoint_config.json"
  local rc
  local -a command

  mkdir -p "$phase_dir/output" "$phase_dir/restart"
  if [[ -f "$phase_dir/run_status.txt" ]] && grep -q '^exit_code=0$' "$phase_dir/run_status.txt"; then
    printf 'Completed chunk retained: %s\n' "$tag"
    return 0
  fi

  printf 'chunk=%s\nstarted_utc=%s\n' "$tag" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >"$phase_dir/run_status.txt"
  if cp -p "$A0_RESTART" "$phase_dir/restart/restart_1700_nv_stdfire.lpj"; then
    :
  else
    rc=$?
    printf 'completed_utc=%s\nexit_code=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$rc" >>"$phase_dir/run_status.txt"
    return "$rc"
  fi
  sha256sum "$A0_RESTART" >"$phase_dir/a0_restart.sha256"
  if python3 - "$CAMPAIGN_DIR/configs/potential_yield_unlimited_n.json" "$checkpoint_config" "$phase_dir/restart/checkpoint.lpj" "$start" "$end" <<'PY'
import json
from pathlib import Path
import sys
source, target, checkpoint = map(Path, sys.argv[1:4])
start, end = int(sys.argv[4]), int(sys.argv[5])
config = json.loads(source.read_text())
config["startgrid"] = start
config["endgrid"] = end
# A local LPJmL grid cannot reconstruct the global river-neighbour graph.
# Keep crop/water allocation active but disable routing and reservoirs for the
# capacity-ranking pass; the final managed campaign will use the global map.
config["river_routing"] = False
config["reservoir"] = False
config["checkpoint_filename"] = str(checkpoint)
target.write_text(json.dumps(config, indent=2) + "\n")
PY
  then
    :
  else
    rc=$?
    printf 'completed_utc=%s\nexit_code=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$rc" >>"$phase_dir/run_status.txt"
    return "$rc"
  fi

  command=(mpirun -np "$MPI_RANKS" "$LPJML_ROOT/bin/lpjml"
    -inpath "$INPUT_ROOT" -outpath "$phase_dir" -restartpath "$phase_dir/restart" "$checkpoint_config")
  printf 'CHUNK %s COMMAND:' "$tag"
  printf ' %q' "${command[@]}"
  printf '\n'
  if "$LPJML_ROOT/bin/lpjcheck" -inpath "$INPUT_ROOT" -outpath "$phase_dir" \
      -restartpath "$phase_dir/restart" "$checkpoint_config" >"$phase_dir/lpjcheck.log" 2>&1; then
    :
  else
    rc=$?
    printf 'completed_utc=%s\nexit_code=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$rc" >>"$phase_dir/run_status.txt"
    return "$rc"
  fi

  if python3 "$SCRIPT_DIR/checkpoint_runner.py" \
      --config "$checkpoint_config" --phase-dir "$phase_dir" \
      --interval-seconds "$CHECKPOINT_INTERVAL" \
      --max-archived-checkpoints "$MAX_ARCHIVED_CHECKPOINTS" -- "${command[@]}" \
      >>"$phase_dir/controller.log" 2>>"$phase_dir/controller.stderr.log"; then
    printf 'completed_utc=%s\nexit_code=0\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"$phase_dir/run_status.txt"
    return 0
  else
    rc=$?
    printf 'completed_utc=%s\nexit_code=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$rc" >>"$phase_dir/run_status.txt"
    return "$rc"
  fi
}

declare -A ACTIVE_CHUNKS=()
ANY_FAILED=0
wait_for_chunk() {
  local finished_pid="" tag rc
  if wait -n -p finished_pid "${!ACTIVE_CHUNKS[@]}"; then
    rc=0
  else
    rc=$?
  fi
  tag="${ACTIVE_CHUNKS[$finished_pid]:-unknown}"
  unset 'ACTIVE_CHUNKS[$finished_pid]'
  printf 'CHUNK_WORKER_EXIT chunk=%s pid=%s exit_code=%s\n' "$tag" "$finished_pid" "$rc"
  if ((rc != 0)); then
    ANY_FAILED=1
  fi
}

for ((start=0; start<NCell; start+=CHUNK_SIZE)); do
  end=$((start + CHUNK_SIZE - 1))
  ((end < NCell)) || end=$((NCell - 1))
  tag=$(printf '%05d_%05d' "$start" "$end")
  phase_dir="$CAMPAIGN_DIR/chunks/$tag"
  if [[ -f "$phase_dir/run_status.txt" ]] && grep -q '^exit_code=0$' "$phase_dir/run_status.txt"; then
    echo "Completed chunk retained: $tag"
    continue
  fi
  while ((${#ACTIVE_CHUNKS[@]} >= MAX_PARALLEL)); do
    wait_for_chunk
    if ((ANY_FAILED)); then
      break
    fi
  done
  if ((ANY_FAILED)); then
    break
  fi
  run_chunk "$start" "$end" "$tag" &
  worker_pid=$!
  ACTIVE_CHUNKS[$worker_pid]="$tag"
done

while ((${#ACTIVE_CHUNKS[@]} > 0)); do
  wait_for_chunk
done

if ((ANY_FAILED)); then
  echo "FAILED $(date -Is)" >"$CAMPAIGN_DIR/campaign_status.txt"
  exit 1
fi

echo "POTENTIAL_CHUNKS_COMPLETE $(date -Is)" >"$CAMPAIGN_DIR/campaign_status.txt"
printf 'campaign_dir=%s\nncell=%s\nchunk_size=%s\nmpi_ranks_per_chunk=%s\nmax_parallel_chunks=%s\nmax_archived_checkpoints=%s\n' \
  "$CAMPAIGN_DIR" "$NCell" "$CHUNK_SIZE" "$MPI_RANKS" \
  "$MAX_PARALLEL" "$MAX_ARCHIVED_CHECKPOINTS"
