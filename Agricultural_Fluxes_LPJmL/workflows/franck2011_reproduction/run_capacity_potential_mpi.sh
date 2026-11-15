#!/usr/bin/env bash
set -euo pipefail

# Global candidate-yield stage for Franck-inspired capacity branches.
# This stage is separate from the crop-only nitrogen/CH4 run: it uses the
# validated no-methane natural restart and only produces per-CFT harvest
# diagnostics needed to build the winner map.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LPJML_ROOT="${LPJML_ROOT:-/home/dasan/exofarm-lpjml-runtime/LPJmL-6.0.6-balance-fix-20260912}"
INPUT_ROOT="${LPJ_INPUT_ROOT:-/home/dasan/lpjml-data/public_standard}"
CAMPAIGN_DIR="${CAPACITY_POTENTIAL_DIR:-/home/dasan/exofarm-lpjml-runs/fr_genghis_potential_20260922}"
A0_RESTART="${A0_RESTART:-/home/dasan/exofarm-lpjml-runs/global_a1_checkpoints_20260909/a0_natural/restart/restart_1700_nv_stdfire.lpj}"
MPI_RANKS="${MPI_RANKS:-8}"
CHECKPOINT_INTERVAL="${CHECKPOINT_INTERVAL_SECONDS:-3600}"

EXPECTED_COMMIT="5af44a1ed023279a23c28d6dfe76945b97aaac57"
[[ "$(git -C "$LPJML_ROOT" rev-parse HEAD 2>/dev/null || true)" == "$EXPECTED_COMMIT" ]] || {
  echo "LPJmL source is not the pinned balance-fix commit" >&2
  exit 4
}
[[ -x "$LPJML_ROOT/bin/lpjml" && -x "$LPJML_ROOT/bin/lpjcheck" ]] || {
  echo "LPJmL binaries are missing under $LPJML_ROOT" >&2
  exit 4
}
command -v mpirun >/dev/null 2>&1 || { echo "mpirun is required" >&2; exit 4; }
((MPI_RANKS <= $(nproc))) || { echo "MPI ranks exceed available CPUs" >&2; exit 5; }
[[ -s "$A0_RESTART" ]] || { echo "Missing validated A0 restart: $A0_RESTART" >&2; exit 6; }

mkdir -p "$CAMPAIGN_DIR/configs" "$CAMPAIGN_DIR/potential_yield_unlimited_n/output" \
  "$CAMPAIGN_DIR/potential_yield_unlimited_n/restart"
exec 9>"$CAMPAIGN_DIR/campaign.lock"
flock -n 9 || { echo "Campaign already locked: $CAMPAIGN_DIR" >&2; exit 9; }
exec >>"$CAMPAIGN_DIR/launcher.log" 2>&1
trap 'echo FAILED $(date -Is) >"$CAMPAIGN_DIR/campaign_status.txt"' ERR
unset OMP_NUM_THREADS OMP_THREAD_LIMIT
export OPENBLAS_NUM_THREADS=1

CONFIG_DIR="$CAMPAIGN_DIR/configs"
if [[ ! -f "$CONFIG_DIR/manifest.json" ]]; then
  python3 "$SCRIPT_DIR/prepare_configs.py" \
    --lpjml-root "$LPJML_ROOT" \
    --input-root "$INPUT_ROOT" \
    --output-dir "$CONFIG_DIR" \
    --mode global \
    --workflow franck2011 \
    --crop-only
fi

if [[ -f "$CAMPAIGN_DIR/potential_yield_unlimited_n/run_status.txt" ]] && \
   grep -q '^exit_code=0$' "$CAMPAIGN_DIR/potential_yield_unlimited_n/run_status.txt"; then
  echo "Potential candidate stage already complete"
  echo "POTENTIAL_COMPLETE $(date -Is)" >"$CAMPAIGN_DIR/campaign_status.txt"
  exit 0
fi

cp -p "$A0_RESTART" "$CAMPAIGN_DIR/potential_yield_unlimited_n/restart/restart_1700_nv_stdfire.lpj"
sha256sum "$A0_RESTART" >"$CAMPAIGN_DIR/a0_restart.sha256"

SCENARIO_DIR="$CAMPAIGN_DIR/potential_yield_unlimited_n"
CHECKPOINT_CONFIG="$SCENARIO_DIR/checkpoint_config.json"
python3 - "$CONFIG_DIR/potential_yield_unlimited_n.json" "$CHECKPOINT_CONFIG" "$SCENARIO_DIR/restart/checkpoint.lpj" <<'PY'
import json
from pathlib import Path
import sys

source, target, checkpoint = map(Path, sys.argv[1:])
config = json.loads(source.read_text())
config["checkpoint_filename"] = str(checkpoint)
target.write_text(json.dumps(config, indent=2) + "\n")
PY

echo "POTENTIAL_RUNNING $(date -Is)" >"$CAMPAIGN_DIR/campaign_status.txt"
COMMAND=(mpirun -np "$MPI_RANKS" "$LPJML_ROOT/bin/lpjml"
  -inpath "$INPUT_ROOT"
  -outpath "$SCENARIO_DIR"
  -restartpath "$SCENARIO_DIR/restart"
  "$CHECKPOINT_CONFIG")
printf 'COMMAND:'
printf ' %q' "${COMMAND[@]}"
printf '\n'
"$LPJML_ROOT/bin/lpjcheck" \
  -inpath "$INPUT_ROOT" \
  -outpath "$SCENARIO_DIR" \
  -restartpath "$SCENARIO_DIR/restart" \
  "$CHECKPOINT_CONFIG"
printf 'started_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >"$SCENARIO_DIR/run_status.txt"
python3 "$SCRIPT_DIR/checkpoint_runner.py" \
  --config "$CHECKPOINT_CONFIG" \
  --phase-dir "$SCENARIO_DIR" \
  --interval-seconds "$CHECKPOINT_INTERVAL" \
  -- "${COMMAND[@]}" \
  >>"$SCENARIO_DIR/controller.log" \
  2>>"$SCENARIO_DIR/controller.stderr.log"
printf 'completed_utc=%s\nexit_code=0\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"$SCENARIO_DIR/run_status.txt"
echo "POTENTIAL_COMPLETE $(date -Is)" >"$CAMPAIGN_DIR/campaign_status.txt"
