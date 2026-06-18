# Column-averaged mixing ratio for photochemical profile summaries

**Date:** 2026-06-17  
**Workflow stage:** `Photochemical_Modeling/`  
**Script:** `Photochemical_Modeling/Scripts/Plotting/plot_photochemical_summary_grid.py`  
**Products:** `Photochemical_Modeling/Results/Plots/photochemical_summary_grid.{png,pdf}`

## Scientific question

The summary figure compares the vertical chemical response of the active A0-A3
agricultural scenarios under two stellar environments: Earth-Sun and
TRAPPIST-1e. The first two columns show the full vertical profiles. The third
column needs a compact scalar that summarizes the bulk atmospheric abundance
change of each molecule across scenarios without implying a retrieval
detection.

## Adopted diagnostic

The third column now reports the **column-averaged mixing ratio**:

```text
              integral x_i(p) dp
x_i,colbar = --------------------
                 p_bot - p_top
```

where `x_i(p)` is the VMR, or mixing ratio, profile of molecule `i`, and
`p_bot` and `p_top` are the bottom and top pressures of the VULCAN profile.

The unnormalized pressure-column integral,

```text
C_i = integral x_i(p) dp
```

is also physically meaningful, but the normalized form is easier to compare
across molecules and panels because it remains in mixing-ratio units.

## Implementation

The VULCAN outputs provide layer-center pressure and mixing-ratio arrays. The
script sorts each profile by pressure and evaluates the pressure integral with a
trapezoidal rule:

```python
pressure_span = np.trapz(np.ones_like(pressure), x=pressure)
x_colbar = np.trapz(vmr, x=pressure) / pressure_span
```

This is a pressure-coordinate approximation to a column mean. Because pressure
increments trace atmospheric column mass under hydrostatic balance, the
diagnostic weights dense lower-atmosphere layers more strongly than tenuous
upper-atmosphere layers. This makes it more physically interpretable than an
unweighted average over model levels.

The plotted multiplier labels are normalized molecule-by-molecule to the
Earth-Sun A1 column-averaged value:

```text
factor(star, scenario, molecule) =
    x_colbar(star, scenario, molecule) / x_colbar(Earth-Sun, A1, molecule)
```

## Direct result

The third column is now titled **Column-averaged mixing ratio** rather than
`mean mixing ratio` or `pressure-integrated mean`. This language is more
compact and closer to the physical quantity being shown.

## Interpretation and limitations

**Direct result:** the diagnostic summarizes how the bulk pressure column of a
given molecule changes across A0-A3 and between stellar environments.

**Project interpretation:** it is appropriate for comparing global abundance
changes caused by the agricultural lower-boundary forcing matrix, especially
when paired with the full profile columns.

**Limitation:** this is not a radiative-transfer weighting function and should
not be interpreted as detectability. Spectral detectability still depends on
line opacity, wavelength coverage, temperature-pressure structure, clouds or
hazes if present, instrument noise, and retrieval degeneracies.

**TRAPPIST-1e caveat:** the TRAPPIST-1e VULCAN products remain accepted
partial-convergence profiles. The column-averaged values inherit that caveat and
should be described as diagnostics of the accepted step-limited profiles, not as
strict steady-state chemical network results.
