#!/bin/bash
set -e
cd /home/wsldasan/POSEIDON
echo "Starting download of POSEIDON inputs (72 GB)..."
wget -c -O inputs.zip https://zenodo.org/api/records/19595136/files/inputs.zip/content
echo "Download complete. Unzipping..."
unzip -q inputs.zip
echo "Unzip complete."
rm inputs.zip
echo "All done."
