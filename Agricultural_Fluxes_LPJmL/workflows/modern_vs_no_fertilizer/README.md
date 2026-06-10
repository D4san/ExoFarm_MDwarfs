# LPJmL modern Earth vs no synthetic fertilizer

This workflow keeps the upstream LPJmL examples untouched and runs scenario
copies from this directory.

## Status

LPJmL is compiled in WSL, but the full run requires the LPJmL input dataset
usually referenced as:

```bash
/p/projects/lpjml/inputs/public_standard
```

The public LPJmL repository does not ship these input data. Point the workflow
to a local copy with:

```bash
cd /mnt/c/Proyectos/Astro/ExoFarm_MDwarfs/Agricultural_Fluxes_LPJmL/workflows/modern_vs_no_fertilizer
./run_lpjml_scenarios.sh /path/to/public_standard
```

or:

```bash
export LPJINPATH=/path/to/public_standard
./run_lpjml_scenarios.sh
```

## Scenarios

- `shared_spinup`: natural spinup from the official `lpjml_config.cjson`.
- `modern_earth_lu`: managed land transient with the default fertilizer and
  manure settings.
- `no_synthetic_fertilizer_lu`: managed land transient with
  `fertilizer_input: "no"` and `manure_input: true`.

## Flux outputs to compare

Primary ExoFarm outputs:

- `n2o_nit_agr`
- `n2o_denit_agr`
- `nh3_agr`
- `n2_agr`

Context outputs:

- `nfert_agr`
- `nmanure_agr`
- `nleaching_agr`
- `nuptake_agr`
- `bnf_agr`
- `ndepo_agr`
