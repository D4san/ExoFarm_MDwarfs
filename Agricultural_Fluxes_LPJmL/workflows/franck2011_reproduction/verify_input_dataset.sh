#!/usr/bin/env bash
set -euo pipefail

EXPECTED_NAME="lpjml6-0-5_standard_input.tar.gz"
EXPECTED_BYTES=37763601476
EXPECTED_MD5="682d8b894d7983301313e9d60a49483b"
EXPECTED_FILES=76
EXPECTED_EXTRACTED_BYTES=66338995720
ARCHIVE=""
INPUT_ROOT=""
EXTRACT=0

usage() {
  cat <<'MSG'
Usage: verify_input_dataset.sh --archive FILE --input-root DIR [--extract]

Verify the official public_standard archive used by LPJmL 6.0.6. With
--extract, the destination must be absent or empty; existing data are never
overwritten. Archive source: https://zenodo.org/records/19064225
MSG
}

while (($#)); do
  case "$1" in
    --archive) ARCHIVE="$2"; shift 2 ;;
    --input-root) INPUT_ROOT="$2"; shift 2 ;;
    --extract) EXTRACT=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$ARCHIVE" || -z "$INPUT_ROOT" ]]; then
  usage >&2
  exit 2
fi
if [[ ! -f "$ARCHIVE" ]]; then
  echo "Archive not found: $ARCHIVE" >&2
  exit 3
fi

ACTUAL_BYTES="$(stat -c '%s' "$ARCHIVE")"
ACTUAL_MD5="$(md5sum "$ARCHIVE" | awk '{print $1}')"
if [[ "$ACTUAL_BYTES" != "$EXPECTED_BYTES" || "$ACTUAL_MD5" != "$EXPECTED_MD5" ]]; then
  echo "Input archive verification failed." >&2
  printf 'Expected %s bytes and MD5 %s\n' "$EXPECTED_BYTES" "$EXPECTED_MD5" >&2
  printf 'Observed %s bytes and MD5 %s\n' "$ACTUAL_BYTES" "$ACTUAL_MD5" >&2
  exit 4
fi

if [[ "$EXTRACT" -eq 1 ]]; then
  if [[ -d "$INPUT_ROOT" ]] && find "$INPUT_ROOT" -mindepth 1 -print -quit | grep -q .; then
    echo "Extraction target is not empty; refusing to overwrite: $INPUT_ROOT" >&2
    exit 5
  fi
  mkdir -p "$INPUT_ROOT"
  tar -xzf "$ARCHIVE" -C "$INPUT_ROOT"
fi

if [[ ! -d "$INPUT_ROOT" ]]; then
  echo "Verified archive, but input root does not exist: $INPUT_ROOT" >&2
  echo "Re-run with --extract." >&2
  exit 6
fi

ACTUAL_FILES="$(find "$INPUT_ROOT" -type f | wc -l | tr -d ' ')"
ACTUAL_EXTRACTED_BYTES="$(find "$INPUT_ROOT" -type f -printf '%s\n' | awk '{sum += $1} END {printf "%.0f", sum}')"
if [[ "$ACTUAL_FILES" != "$EXPECTED_FILES" || "$ACTUAL_EXTRACTED_BYTES" != "$EXPECTED_EXTRACTED_BYTES" ]]; then
  echo "Extracted dataset verification failed." >&2
  printf 'Expected %s files and %s bytes\n' "$EXPECTED_FILES" "$EXPECTED_EXTRACTED_BYTES" >&2
  printf 'Observed %s files and %s bytes\n' "$ACTUAL_FILES" "$ACTUAL_EXTRACTED_BYTES" >&2
  exit 7
fi

required_inputs=(
  grid.clm.json
  soil_30arcmin_13_types.clm.json
  global_co2_ann_1700_2022.txt
  tas_gswp3-w5e5_obsclim_1901-2019.clm.json
  pr_gswp3-w5e5_obsclim_1901-2019.clm.json
)
for item in "${required_inputs[@]}"; do
  [[ -f "$INPUT_ROOT/$item" ]] || { echo "Missing input: $INPUT_ROOT/$item" >&2; exit 8; }
done

printf 'Verified archive: %s (%s bytes, MD5 %s)\n' "$EXPECTED_NAME" "$ACTUAL_BYTES" "$ACTUAL_MD5"
printf 'Verified input root: %s (%s files, %s bytes)\n' "$INPUT_ROOT" "$ACTUAL_FILES" "$ACTUAL_EXTRACTED_BYTES"

