# LPJmL Agricultural Fluxes

This module defines the LPJmL-centered upstream agricultural-flux layer for
ExoFarm.

LPJmL (Lund-Potsdam-Jena managed Land) is a global dynamic vegetation, managed
land, and hydrology model. For ExoFarm, its useful role is not to prescribe
atmospheric abundances directly. Its role is to estimate spatially explicit
land-use, crop, water, carbon, and nitrogen fluxes, then let the photochemical
stage decide the atmospheric response.

## Role in the ExoFarm Pipeline

The intended workflow is:

1. Define global or regional ExoFarm scenarios through land use, crop mix,
   fertilizer, manure, irrigation, residue, tillage, and climate assumptions.
2. Run an LPJmL version with nitrogen cycling enabled.
3. Extract nitrogen-loss outputs relevant to atmospheric forcing, especially:
   - `N2O_DENIT` and `N2O_NIT`
   - agricultural variants such as `N2O_DENIT_AGR`, `N2O_NIT_AGR`, and `NH3_AGR`
   - diagnostic reservoirs such as `N2_EMIS`, `N2_AGR`, leaching, uptake,
     fertilizer, manure, and deposition.
4. Convert nitrogen-mass fluxes into molecules cm^-2 s^-1 before passing them
   to VULCAN or another atmospheric chemistry model.
5. Map the resulting surface fluxes into the ExoFarm scenario matrix:
   - `A0`: pre-agricultural baseline
   - `A1`: current Earth benchmark
   - `A2`: moderate ExoFarm forcing
   - `A3`: extreme ExoFarm forcing

## Local Contents

- `docs/consideraciones_exofarm_lpjml.md`: research notes and first workflow.
- `docs/lpjml_sources.bib`: bibliography for the LPJmL papers and tools read for
  this pivot.
- `scripts/convert_lpjml_n_flux.py`: small unit converter from LPJmL-style
  nitrogen-mass fluxes to atmospheric molecule fluxes.

No LPJmL source tree or input data are vendored here yet. If we install it
locally, keep the upstream code under a separate `software/LPJmL/` directory or
document an external path, and keep ExoFarm scripts and derived outputs separate
from the upstream model distribution.

## Conversion Principle

LPJmL nitrogen outputs are nitrogen-mass fluxes, not atmospheric abundance
targets. For example, an `N2O` output reported as grams of nitrogen per square
meter per year must be converted through nitrogen atoms:

```text
g N -> mol N -> mol N2O = mol N / 2 -> molecules N2O -> cm^-2 s^-1
```

For `NH3`, the nitrogen atom count is one. This distinction matters: converting
`N2O-N` as if it were whole `N2O` mass would bias the lower-boundary flux.

## First Local Checks Once LPJmL Is Installed

```bash
./bin/lpjml -h
./bin/lpjml -ofiles
./bin/lpjcheck lpjml_config.cjson
python Agricultural_Fluxes_LPJmL/scripts/convert_lpjml_n_flux.py --help
```

Before trusting a flux file, record the LPJmL version, the active configuration,
the output units, whether outputs are grid-scaled, and whether the source values
are total grid-cell fluxes or per-area fluxes.
