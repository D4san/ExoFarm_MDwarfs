#!/usr/bin/env bash
set -euo pipefail

# Build isolated 1 h inputs for the official focused A1/A3 retrieval series.
# The canonical A0--A3 x {10 h, 240 h} index is hashed before and after.

REPO=/mnt/c/Proyectos/Astro/ExoFarm_MDwarfs
DATA="$REPO/Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data"
INDEX="$DATA/dataset_index_A1_A3_1h_official.json"
CANONICAL_INDEX="$DATA/dataset_index.json"
SUFFIX=_O2_fixedBlack1bar_official

for scenario in A1 A3; do
    file="$DATA/LIFE_proxima_${scenario}_1h${SUFFIX}.dat"
    if [[ -e "$file" ]]; then
        printf '[abort] preserving existing dataset: %s\n' "$file" >&2
        exit 2
    fi
done
if [[ -e "$INDEX" ]]; then
    printf '[abort] preserving existing focused index: %s\n' "$INDEX" >&2
    exit 3
fi

CANONICAL_SHA_BEFORE=$(sha256sum "$CANONICAL_INDEX" | awk '{print $1}')
source /home/dasan/anaconda3/etc/profile.d/conda.sh
conda activate POSEIDON
cd "$REPO/Thermal_Emission_Spectroscopy/scripts"

python -u make_life_datasets.py \
    --campaign proxima --scenarios A1 A3 --hours 1 --seed 20261001 \
    --name-suffix "$SUFFIX" \
    --index-output "$INDEX" \
    --index-classification official_focused_A1_A3_1h_excluded_from_canonical_8of8

python - "$DATA" "$CANONICAL_SHA_BEFORE" <<'PY'
import hashlib
import json
import pathlib
import sys

import numpy as np

root = pathlib.Path(sys.argv[1])
expected_canonical_sha = sys.argv[2]
canonical = root / "dataset_index.json"
actual_canonical_sha = hashlib.sha256(canonical.read_bytes()).hexdigest()
if actual_canonical_sha != expected_canonical_sha:
    raise SystemExit("[abort] canonical dataset index changed during generation")

index = json.loads((root / "dataset_index_A1_A3_1h_official.json").read_text())
if index.get("classification") != "official_focused_A1_A3_1h_excluded_from_canonical_8of8":
    raise SystemExit("[abort] unexpected focused-series classification")
rows = index.get("datasets", [])
if {row.get("scenario") for row in rows} != {"A1", "A3"} or len(rows) != 2:
    raise SystemExit("[abort] focused index must contain exactly A1 and A3")
for row in rows:
    path = root / row["file"]
    data = np.loadtxt(path, skiprows=1)
    if data.shape != (31, 4) or not np.isfinite(data).all():
        raise SystemExit(f"[abort] invalid dataset shape or non-finite value: {path}")
    if np.any(data[:, 1] <= 0) or np.any(data[:, 3] <= 0):
        raise SystemExit(f"[abort] non-positive bin width or sigma: {path}")
    print(
        f"[validated] {row['scenario']} file={path.name} seed={row['seed']} "
        f"median_continuum_SNR={row['median_continuum_SNR']} bins={row['n_bins']}"
    )
print(f"[canonical_index_sha256_unchanged] {actual_canonical_sha}")
PY

sha256sum "$INDEX" \
    "$DATA/LIFE_proxima_A1_1h${SUFFIX}.dat" \
    "$DATA/LIFE_proxima_A3_1h${SUFFIX}.dat"
