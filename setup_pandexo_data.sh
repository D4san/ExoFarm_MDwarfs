#!/bin/bash
set -e

echo "Downloading Pandeia JWST Data (v2026.2)..."
mkdir -p /home/wsldasan/pandeia_data
cd /home/wsldasan/pandeia_data
wget -c --timeout=30 --tries=3 -O pandeia_data.tar.gz "https://stsci.box.com/shared/static/0yd1ks949ee38qbuj76ply0gj3m1cppu.gz"
tar -xzf pandeia_data.tar.gz || echo "Extraction might have failed for Pandeia"

echo "Downloading PySynphot Phoenix Models..."
mkdir -p /home/wsldasan/pysynphot_data
cd /home/wsldasan/pysynphot_data
wget -c --timeout=30 --tries=3 -O phoenix_models.tar "https://archive.stsci.edu/hlsps/reference-atlases/hlsp_reference-atlases_hst_multi_pheonix-models_multi_v3_synphot5.tar"
tar -xf phoenix_models.tar || echo "Extraction might have failed for Phoenix"

echo "Downloading PySynphot Normalization Files..."
wget -c --timeout=30 --tries=3 -O norm_files.tar "https://archive.stsci.edu/hlsps/reference-atlases/hlsp_reference-atlases_hst_multi_everything_multi_v11_sed.tar"
tar -xf norm_files.tar || echo "Extraction might have failed for Norm"

echo "Done."
