#!/usr/bin/env bash
set -euo pipefail

LPJML_ROOT=""
INPUT_ROOT=""
MIN_FREE_GIB=100

usage() {
  cat <<'MSG'
Usage: check_other_pc.sh --lpjml-root DIR --input-root DIR

Read-only readiness report for the PC that will execute the global MPI run.
It does not install software or start LPJmL.
MSG
}

while (($#)); do
  case "$1" in
    --lpjml-root) LPJML_ROOT="$2"; shift 2 ;;
    --input-root) INPUT_ROOT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done
if [[ -z "$LPJML_ROOT" || -z "$INPUT_ROOT" ]]; then usage >&2; exit 2; fi

fail=0
printf 'kernel=%s\n' "$(uname -srmo)"
printf 'logical_cpus=%s\n' "$(nproc)"
printf 'memory_gib=%s\n' "$(awk '/MemTotal/ {printf "%.1f", $2/1024/1024}' /proc/meminfo)"
printf 'runtime_filesystem=%s\n' "$(df -PT "$LPJML_ROOT" 2>/dev/null | tail -1 || true)"
printf 'input_filesystem=%s\n' "$(df -PT "$INPUT_ROOT" 2>/dev/null | tail -1 || true)"

for command_name in mpicc mpirun python3; do
  if command -v "$command_name" >/dev/null 2>&1; then
    printf '%s=%s\n' "$command_name" "$(command -v "$command_name")"
  else
    printf '%s=MISSING\n' "$command_name"
    fail=1
  fi
done

if [[ ! -x "$LPJML_ROOT/bin/lpjml" || ! -x "$LPJML_ROOT/bin/lpjcheck" ]]; then
  echo "lpjml_build=MISSING"
  fail=1
elif ! grep -q -- '-DUSE_MPI' "$LPJML_ROOT/Makefile.inc"; then
  echo "lpjml_mpi=NO"
  fail=1
else
  echo "lpjml_mpi=YES"
  printf 'lpjml_commit=%s\n' "$(git -C "$LPJML_ROOT" rev-parse HEAD)"
fi

for item in grid.clm.json soil_30arcmin_13_types.clm.json global_co2_ann_1700_2022.txt; do
  if [[ ! -f "$INPUT_ROOT/$item" ]]; then
    printf 'missing_input=%s\n' "$INPUT_ROOT/$item"
    fail=1
  fi
done

FREE_KIB="$(df -Pk "$LPJML_ROOT" | awk 'NR==2 {print $4}')"
FREE_GIB=$((FREE_KIB / 1024 / 1024))
printf 'runtime_free_gib=%s\n' "$FREE_GIB"
if ((FREE_GIB < MIN_FREE_GIB)); then
  printf 'warning=less_than_%s_GiB_free_on_runtime_filesystem\n' "$MIN_FREE_GIB"
fi

if [[ "$LPJML_ROOT" == /mnt/* ]]; then
  echo "warning=LPJmL_source_is_on_a_Windows_mounted_filesystem"
fi
if [[ "$fail" -ne 0 ]]; then
  echo "readiness=FAIL"
  exit 10
fi
echo "readiness=PASS"

