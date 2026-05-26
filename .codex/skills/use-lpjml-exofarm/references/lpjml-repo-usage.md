# LPJmL Repo Usage Notes

Use these notes after verifying the local repo version. They are grounded in
LPJmL 6.0.6 cloned from `https://github.com/PIK-LPJmL/LPJmL` on 2026-05-26.

## Local Repository

Expected ExoFarm clone:

```text
Agricultural_Fluxes_LPJmL/software/LPJmL
```

Important files:

- `README`: project, license, support boundary, source location.
- `INSTALL`: dependencies, configure/build commands, utilities.
- `VERSION`: model version.
- `CITATION.cff`: software citation metadata.
- `lpjml_config.cjson`: default full configuration.
- `input.cjson` and `input_netcdf.cjson`: input file definitions.
- `par/outputvars.cjson`: authoritative output IDs, names, timesteps, units.
- `man/man1/lpjml.1`, `man/man1/lpjcheck.1`: runtime options.

## Build and Validation

LPJmL is C code. For Linux/WSL, `INSTALL` lists these dependencies:

```bash
sudo apt-get install libnetcdf-dev
sudo apt-get install libudunits2-dev
sudo apt-get install libjson-c-dev
sudo apt-get install mpich
sudo apt-get install openmpi-bin openmpi-common libopenmpi-dev
```

Typical build:

```bash
./configure.sh
make
make lpjcheck
make utils
```

Useful runtime checks:

```bash
./bin/lpjml -v
./bin/lpjml -ofiles
./bin/lpjcheck -ofiles lpjml_config.cjson
./bin/lpjcheck -pedantic -inpath <input-data-root> lpjml_config.cjson
```

`lpjcheck` checks JSON syntax and whether required input files and output
directories exist. `-ofiles` lists available output variables. `-pedantic` turns
warnings into errors.

## Input Data Caveat

The repo contains source code and configurations, not all input data. The GitHub
project notes that public input data are available for historical simulations
starting with LPJmL 6.0.5, but the exact data root still has to be downloaded or
provided separately. Do not mark a run as reproducible until the input data DOI,
path, grid, and versions are recorded.

## Configuration Switches for ExoFarm

In `lpjml_config.cjson`, pay attention to:

- `with_nitrogen`: use `"lim"` for nitrogen limitation; `"unlim"` is diagnostic.
- `landuse`: agriculture requires a managed-land setting such as `"yes"`,
  `"const"`, `"all_crops"`, or `"only_crops"`.
- `fertilizer_input`: `"no"`, `"yes"`, or `"auto"`. Treat `"auto"` as an
  upper-bound because it applies exact N demand and removes N stress.
- `manure_input`: enables manure input.
- `fix_fertilization`: `false` uses prescribed time/cell/CFT input; `true` uses
  global constant rates from parameter files.
- `irrigation`: `"no"`, `"lim"`, `"pot"`, or `"all"`.
- `tillage_type`: `"read"`, `"all"`, or `"no"`.
- `residue_treatment`: keep explicit because residue handling affects C/N and
  N losses.
- `output_metafile`: keep `true` to generate JSON metadata for outputs.
- `default_fmt`, `default_suffix`, `grid_scaled`: record these before reading.

## ExoFarm Output IDs

Prefer the agricultural annual outputs for scenario forcing:

| Output ID | Meaning | Unit |
| --- | --- | --- |
| `n2o_denit_agr` | N loss through N2O from denitrification on agricultural stands | `gN/m2/yr` |
| `n2o_nit_agr` | N loss through N2O from nitrification on agricultural stands | `gN/m2/yr` |
| `nh3_agr` | N loss through NH3 volatilization on agricultural stands | `gN/m2/yr` |
| `n2_agr` | N loss through N2 from denitrification on agricultural stands | `gN/m2/yr` |
| `nfert_agr` | N input from fertilizer on agricultural stands | `gN/m2/yr` |
| `nmanure_agr` | N input from manure on agricultural stands | `gN/m2/yr` |
| `nleaching_agr` | N loss through leaching on agricultural stands | `gN/m2/yr` |
| `nuptake_agr` | N uptake on agricultural stands | `gN/m2/yr` |
| `bnf_agr` | biological N fixation on agricultural stands | `gN/m2/yr` |
| `ndepo_agr` | atmospheric N deposition on agricultural stands | `gN/m2/yr` |

The all-stand monthly analogues include `n2o_denit`, `n2o_nit`, `n2_emis`, and
`n_volatilization`, typically in `gN/m2/month`.

Code checks from the cloned repo:

- `src/soil/denitrification.c` writes `N2O_DENIT`, `N2_EMIS`,
  `N2O_DENIT_AGR`, and `N2_AGR`.
- `src/lpj/update_daily_cell.c` writes `N2O_NIT`, `N2O_NIT_AGR`,
  `N_VOLATILIZATION`, and `NH3_AGR`.

These outputs are N-mass fluxes. Convert them as nitrogen atoms, not as whole
molecular masses.
