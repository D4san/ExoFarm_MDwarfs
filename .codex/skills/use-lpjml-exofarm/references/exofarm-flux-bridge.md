# ExoFarm Flux Bridge

Use this reference when turning LPJmL outputs into atmospheric lower-boundary
conditions.

## Required Product

Atmospheric models need fluxes in:

```text
molecules cm^-2 s^-1
```

LPJmL nitrogen outputs are generally:

```text
gN/m2/month
gN/m2/yr
gN/m2/growing season
```

Read the exact unit from the output metadata or `par/outputvars.cjson`.

## Conversion Logic

LPJmL reports mass of nitrogen. Convert through nitrogen atoms:

```text
g N -> mol N -> mol target molecule -> molecules -> cm^-2 s^-1
```

For `N2O`:

```text
mol N2O = mol N / 2
```

For `NH3`:

```text
mol NH3 = mol N
```

For a yearly `gN/m2/yr` value:

```text
gN_m2_s = value / (365.25 * 86400)
molN_m2_s = gN_m2_s / 14.0067
mol_species_m2_s = molN_m2_s / n_atoms_in_species
molecules_cm2_s = mol_species_m2_s * 6.02214076e23 / 1e4
```

Use `scripts/convert_lpjml_n_flux.py` for this conversion.

## N2O Flux Assembly

For agricultural forcing:

```text
N2O_N_mass = n2o_denit_agr + n2o_nit_agr
```

Then convert `N2O_N_mass` as species `N2O`.

If using all-stand monthly outputs:

```text
N2O_N_mass = n2o_denit + n2o_nit
```

Monthly outputs need either month-length-aware conversion or a clear annual
aggregation. Do not silently treat monthly values as yearly values.

## NH3 Flux Assembly

For agricultural forcing, prefer:

```text
NH3_N_mass = nh3_agr
```

For total land forcing, use:

```text
NH3_N_mass = n_volatilization
```

Document whether the flux is agricultural-only or whole-grid/whole-land.

## Incomplete Denitrification Envelope

If ExoFarm explores a biology where denitrification closes less efficiently to
`N2`, use `n2_agr` as a nitrogen reservoir:

```text
N2O_N_mass_exofarm = n2o_denit_agr + n2o_nit_agr + epsilon * n2_agr
N2_N_mass_exofarm = (1 - epsilon) * n2_agr
```

This is a post-processing hypothesis, not an LPJmL internal parameter. Keep
`epsilon = 0` as the unmodified LPJmL case. Treat `epsilon = 1` as an extreme
envelope, not a normal future.

## Scenario Mapping

Suggested ExoFarm structure:

| Scenario | LPJmL meaning |
| --- | --- |
| `A0` | no managed agriculture or explicit natural baseline |
| `A1` | present Earth historical benchmark |
| `A2` | intensified but internally consistent agriculture |
| `A3` | extreme area/input/water/bio-chemical envelope |

For every scenario, record:

- LPJmL version and commit;
- input data DOI/path and grid;
- `with_nitrogen`, `landuse`, `fertilizer_input`, `manure_input`, `irrigation`,
  `tillage_type`, `residue_treatment`;
- output IDs used and units;
- spatial aggregation rule and area;
- whether outputs are agricultural-only or total land;
- conversion command used.
