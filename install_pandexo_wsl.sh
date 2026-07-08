#!/bin/bash
set -e

# Source conda
source /home/wsldasan/miniconda3/etc/profile.d/conda.sh

# Activate environment
conda activate POSEIDON

# Install pandexo
pip install git+https://github.com/natashabatalha/PandExo.git

# Fix numpy dependency for POSEIDON and Numba
pip install 'numpy<2'

# Verify installation (using pandeia.engine and pandexo.engine)
python -c "import pandeia.engine; print('Pandeia version:', pandeia.engine.pandeia_version())"
python -c "import pandexo.engine; print('PandExo engine successfully imported')"
