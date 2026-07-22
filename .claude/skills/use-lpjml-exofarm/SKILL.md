---
name: use-lpjml-exofarm
description: "Use when working with LPJmL for ExoFarm agricultural technosignature workflows: downloading or inspecting the LPJmL repo, building/running LPJmL, configuring managed land, nitrogen, fertilizer, manure, irrigation, tillage, selecting N2O/NH3 outputs, reading LPJmL output metadata, and converting LPJmL nitrogen-mass outputs into atmospheric lower-boundary fluxes in molecules cm^-2 s^-1 for VULCAN/PhotoChem."
---

# Use LPJmL for ExoFarm (native adaptation)

This is the Claude Code adaptation of the original Codex skill at
`.codex/skills/use-lpjml-exofarm/`. The instructions below are self-contained;
the deep reference notes and the converter script remain **canonical in the
`.codex` tree** and are linked to avoid duplicating (and later desyncing)
scientific documentation.

## Core rule

Treat LPJmL as the upstream global managed-land model. Do **not** pass LPJmL
values directly as atmospheric abundances. Extract nitrogen-mass fluxes, verify
units from metadata, then convert to molecules cm^-2 s^-1 before using the
fluxes in VULCAN, PhotoChem, or retrieval-facing ExoFarm scenarios.

## First checks

Look for existing project assets before doing anything new:

- `Agricultural_Fluxes_LPJmL/software/LPJmL/` — local clone of the official repo.
- `Agricultural_Fluxes_LPJmL/docs/` — project notes and source bibliography.
- `Agricultural_Fluxes_LPJmL/scripts/` — repo-level converters, if present.

Verify the actual code version instead of assuming it:

```bash
git -C Agricultural_Fluxes_LPJmL/software/LPJmL log -1 --oneline
cat Agricultural_Fluxes_LPJmL/software/LPJmL/VERSION
```

If no local clone exists and network use is allowed:

```bash
git clone https://github.com/PIK-LPJmL/LPJmL Agricultural_Fluxes_LPJmL/software/LPJmL
```

## Canonical references (read these before methodological claims)

- Build/run/configuration: `.codex/skills/use-lpjml-exofarm/references/lpjml-repo-usage.md`
- How papers constrain interpretation: `.codex/skills/use-lpjml-exofarm/references/lpjml-model-and-papers.md`
- ExoFarm scenario mapping and conversion: `.codex/skills/use-lpjml-exofarm/references/exofarm-flux-bridge.md`
- Deterministic unit converter: `.codex/skills/use-lpjml-exofarm/scripts/convert_lpjml_n_flux.py`

## Workflow

1. Read the relevant canonical reference above for the sub-task at hand.
2. Build or inspect LPJmL from the real repo (prefer WSL/Linux):
   `./configure.sh`, `make`, `make lpjcheck`, optionally `make utils`; confirm
   output IDs with `./bin/lpjml -ofiles`.
3. Configure a run: keep `with_nitrogen` explicit (normally `"lim"`); enable
   `landuse` when agricultural fluxes are required; treat
   `fertilizer_input: "auto"` as an upper-bound/diagnostic case; preserve
   `output_metafile: true`.
4. Request ExoFarm-relevant outputs: prefer `n2o_denit_agr`, `n2o_nit_agr`,
   `nh3_agr`, `n2_agr`; keep diagnostics `nfert_agr`, `nmanure_agr`,
   `nleaching_agr`, `nuptake_agr`, `bnf_agr`, `ndepo_agr`.
5. Read outputs **with metadata** (`lpjmlkit::read_io("output/file.bin.json")`).
   Never infer dimensions/units from memory; find the paired JSON/header/config.
6. Convert to atmospheric boundary fluxes. LPJmL nitrogen outputs are mass of
   **N**, not whole-molecule mass:
   - `N2O`: divide moles of N by 2 before converting to molecules.
   - `NH3`: moles of N equal moles of NH3.
   - Use `python .codex/skills/use-lpjml-exofarm/scripts/convert_lpjml_n_flux.py --help`.

## ExoFarm scenario discipline

- `A0`: pre-agricultural natural baseline.
- `A1`: present-Earth benchmark (historical land use, fertilizer, manure,
  irrigation, deposition).
- `A2`: intensified but plausible managed-land case.
- `A3`: extreme envelope, clearly labeled as such.

Do not simply multiply final atmospheric abundances. Apply any incomplete
denitrification hypothesis as a documented post-process on N-flux reservoirs
(e.g. `n2_agr`), then convert the N assigned to `N2O` into molecules cm^-2 s^-1.

## Environment note (this host)

POSEIDON and its 72 GB opacity tree are **not** installed on the current
`/home/castello` host. The general scientific stack lives in the `Main_DFT`
conda env. LPJmL compilation is a separate Ubuntu/WSL build task; see
`CLAUDE.md` for the verified environment state.
