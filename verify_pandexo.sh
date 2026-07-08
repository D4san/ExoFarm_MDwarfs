#!/bin/bash
export pandeia_refdata=/home/wsldasan/pandeia_data/pandeia_data-2026.2-jwst
export PYSYN_CDBS=/home/wsldasan/pysynphot_data/grp/redcat/trds
~/miniconda3/envs/POSEIDON/bin/python -c "import pandeia.engine; pandeia.engine.pandeia_version()"
~/miniconda3/envs/POSEIDON/bin/python -c "import pandexo.engine; print('PandExo engine successfully imported!')"
