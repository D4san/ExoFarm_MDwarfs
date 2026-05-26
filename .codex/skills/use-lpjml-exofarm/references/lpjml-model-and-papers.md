# LPJmL Papers and How to Use Them

Use this file to connect ExoFarm choices to peer-reviewed LPJmL model evidence.

## Core Model Description

Schaphoff et al. 2018 Part 1 describes LPJmL4 as a dynamic global vegetation
model with managed land. Use it when explaining why LPJmL is the upstream
land-use/crop/hydrology layer rather than an atmospheric chemistry model.

Reference:

```text
Schaphoff et al. (2018), LPJmL4 - a dynamic global vegetation model with
managed land - Part 1: Model description, GMD 11, 1343-1375.
https://doi.org/10.5194/gmd-11-1343-2018
```

Schaphoff et al. 2018 Part 2 evaluates the model. Use it when the user asks
whether LPJmL outputs should be treated as model-estimated fluxes with known
evaluation limits rather than exact truth.

```text
Schaphoff et al. (2018), LPJmL4 - a dynamic global vegetation model with
managed land - Part 2: Model evaluation, GMD 11, 1377-1403.
https://doi.org/10.5194/gmd-11-1377-2018
```

## Nitrogen Cycle

von Bloh et al. 2018 is the key nitrogen-cycle paper. It states that LPJmL was
extended to include soil nitrogen dynamics, plant uptake, nitrogen allocation,
photosynthesis/respiration responses to N, and agricultural nitrogen management.
Use this as the main justification for extracting N2O/NH3-relevant fluxes from
LPJmL rather than only using crop yield or water outputs.

It also reports that nitrogen limitation improved crop productivity patterns and
that land use strongly affects nitrogen losses. That matters for ExoFarm because
land-use assumptions are not cosmetic; they affect the nitrogen budget.

```text
von Bloh et al. (2018), Implementing the nitrogen cycle into the dynamic global
vegetation, hydrology, and crop growth model LPJmL (version 5.0), GMD 11,
2789-2812. https://doi.org/10.5194/gmd-11-2789-2018
```

## Tillage, Management, and N2O Caution

Lutz et al. 2019 adds tillage practices to LPJmL5. Use it when ExoFarm scenarios
vary residue incorporation, soil disturbance, and management effects on C, water,
and N.

```text
Lutz et al. (2019), Simulating the effect of tillage practices with the global
ecosystem model LPJmL (version 5.0-tillage), GMD 12, 2419-2440.
https://doi.org/10.5194/gmd-12-2419-2019
```

Lutz et al. 2020 is especially important for N2O interpretation. It shows that
tillage effects on N2O are difficult and sensitive to management detail and soil
moisture representation. Use this as a warning against overconfident ExoFarm
claims from a single global management setup.

```text
Lutz et al. (2020), The importance of management information and soil moisture
representation for simulating tillage effects on N2O emissions in
LPJmL5.0-tillage, GMD 13, 3905-3923.
https://doi.org/10.5194/gmd-13-3905-2020
```

## Biological Nitrogen Fixation

Wirth et al. 2024 describes biological nitrogen fixation in LPJmL 5.7.9 for
natural and agricultural vegetation. Use it when scenarios include legumes,
biological N fixation, or when `bnf_agr` is used as a diagnostic of N supply.

```text
Wirth et al. (2024), Biological nitrogen fixation of natural and agricultural
vegetation simulated with LPJmL 5.7.9, GMD 17, 7889-7914.
https://doi.org/10.5194/gmd-17-7889-2024
```

## Practical Data Handling

Use `lpjmlkit` for reading outputs when R is acceptable. The important practical
point is not the plotting API; it is that `read_io()` can read LPJmL outputs with
metadata and that raw files without metadata are fragile.

```text
lpjmlkit LPJmL Data documentation:
https://pik-piam.r-universe.dev/lpjmlkit/doc/lpjml-data.html
```

## Citation Discipline

When producing a report or paper draft, cite:

- the LPJmL software repo/version used;
- Schaphoff et al. Part 1 and Part 2 for model description/evaluation;
- von Bloh et al. for nitrogen-cycle use;
- Lutz 2019/2020 if tillage or N2O management interpretation is central;
- Wirth et al. if biological N fixation is part of the scenario.
