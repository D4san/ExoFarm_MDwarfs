---
name: use-lpjml-exofarm
description: "Use when working with LPJmL for ExoFarm agricultural technosignature workflows: downloading or inspecting the LPJmL repo, building/running LPJmL, configuring managed land, nitrogen, fertilizer, manure, irrigation, tillage, selecting N2O/NH3 outputs, reading LPJmL output metadata, and converting LPJmL nitrogen-mass outputs into atmospheric lower-boundary fluxes in molecules cm^-2 s^-1 for VULCAN/PhotoChem."
---

# Use LPJmL for ExoFarm

## Core Rule

Treat LPJmL as the upstream global managed-land model. Do not pass LPJmL values
directly as atmospheric abundances. Extract nitrogen-mass fluxes, verify units
from metadata, then convert to molecules cm^-2 s^-1 before using the fluxes in
VULCAN, PhotoChem, or retrieval-facing ExoFarm scenarios.

## First Checks

When the user asks for LPJmL work in `C:\Proyectos\Astro\ExoFarm_MDwarfs`, first
look for:

- `Agricultural_Fluxes_LPJmL/software/LPJmL/`: local clone of the official repo.
- `Agricultural_Fluxes_LPJmL/docs/`: project notes and source bibliography.
- `Agricultural_Fluxes_LPJmL/scripts/convert_lpjml_n_flux.py`: repo-level
  converter, if present.

Verify the actual code version instead of assuming it:

```bash
git -C Agricultural_Fluxes_LPJmL/software/LPJmL log -1 --oneline
cat Agricultural_Fluxes_LPJmL/software/LPJmL/VERSION
```

If no local clone exists and network use is allowed, clone the official repo:

```bash
git clone https://github.com/PIK-LPJmL/LPJmL Agricultural_Fluxes_LPJmL/software/LPJmL
```

## Workflow

1. Read the relevant references:
   - For build/run/configuration details, read `references/lpjml-repo-usage.md`.
   - For how papers constrain interpretation, read `references/lpjml-model-and-papers.md`.
   - For ExoFarm scenario mapping and conversion, read `references/exofarm-flux-bridge.md`.
2. Build or inspect LPJmL from the real repo:
   - Prefer WSL/Linux-style commands for compilation.
   - Use `./configure.sh`, `make`, `make lpjcheck`, and optionally `make utils`.
   - Use `./bin/lpjml -ofiles` or `./bin/lpjcheck -ofiles` to confirm output IDs.
3. Configure an LPJmL run:
   - Keep `with_nitrogen` explicit: normally `"lim"` for nitrogen limitation.
   - Enable managed land with `landuse` when agricultural fluxes are required.
   - Treat `fertilizer_input: "auto"` as an upper-bound or diagnostic case, not
     as a normal future agriculture scenario.
   - Preserve `output_metafile: true` unless there is a strong reason not to.
4. Request ExoFarm-relevant outputs:
   - Prefer agricultural outputs: `n2o_denit_agr`, `n2o_nit_agr`, `nh3_agr`,
     `n2_agr`.
   - Keep diagnostic context: `nfert_agr`, `nmanure_agr`, `nleaching_agr`,
     `nuptake_agr`, `bnf_agr`, `ndepo_agr`, and relevant area or land-use files.
5. Read outputs with metadata:
   - Prefer `lpjmlkit::read_io("output/file.bin.json")` when R is available.
   - If only raw binaries exist, do not infer dimensions/units by memory; find
     the paired JSON, header, config, or output definition first.
6. Convert to atmospheric boundary fluxes:
   - LPJmL nitrogen outputs are mass of N, not whole molecular mass.
   - For `N2O`, divide moles of N by 2 before converting to molecules.
   - For `NH3`, moles of N equal moles of `NH3`.
   - Use `scripts/convert_lpjml_n_flux.py --help` for deterministic conversion.

## ExoFarm Discipline

Keep the scenario bridge physically interpretable:

- `A0`: no managed agriculture or explicitly documented natural baseline.
- `A1`: present-Earth benchmark with historical land use, fertilizer, manure,
  irrigation, and deposition inputs.
- `A2`: intensified but plausible managed-land case.
- `A3`: extreme envelope, clearly labeled as such.

Do not simply multiply final atmospheric abundances. If using an incomplete
denitrification hypothesis, apply it as a documented post-process to nitrogen
flux reservoirs such as `n2_agr`, then convert the resulting N assigned to
`N2O` into molecules cm^-2 s^-1.

## Quick Commands

```bash
./bin/lpjml -v
./bin/lpjml -ofiles
./bin/lpjcheck -pedantic -inpath <input-data-root> lpjml_config.cjson
./bin/lpjml -inpath <input-data-root> -outpath <output-dir> lpjml_config.cjson
python scripts/convert_lpjml_n_flux.py --value 1 --unit gN_m2_yr --species N2O
```

On Windows, use WSL for compilation unless the user explicitly wants the
Microsoft/Cygwin route documented in LPJmL's `INSTALL`.
