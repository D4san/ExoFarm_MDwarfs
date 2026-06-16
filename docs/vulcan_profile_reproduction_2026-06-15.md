# VULCAN vertical-profile reproduction audit, 2026-06-15

## Question

This audit re-ran the active A0-A3 VULCAN chemistry matrix to test whether the
saved vertical profiles are reproducible and whether the active configuration
contains unintended settings.

During the audit, the original products and corrected re-runs were preserved
separately under `Photochemical_Modeling/Results/Reproduction_2026-06-15/`.
After visual and numerical review, the corrected products were promoted into
`Photochemical_Modeling/Results/Outputs/` on 2026-06-15. The superseded `.vul`
files and temporary comparison plots were then deleted. The configuration
snapshots and machine-readable comparison remain as audit evidence.

## Configuration audit

### Direct findings

- The four Earth-Sun YAML files consistently use the Earth radius, gravity,
  orbit, solar spectrum, terrestrial pressure-temperature profile, and
  terrestrial Kzz profile.
- The former TRAPPIST-1e YAML files incorrectly retained the Earth radius and
  surface gravity. They also used an older stellar radius and orbital distance.
- The corrected TRAPPIST-1e YAML files use `R_p = 5.867852e8 cm`,
  `g = 801.2287 cm s^-2`, `a = 0.02925 AU`, and
  `R_star = 0.1192 R_sun`.
- The TRAPPIST-1e pressure-temperature and Kzz inputs intentionally remain the
  terrestrial `atm/atm_Earth_Jan_Kzz.txt` profile for this controlled
  experiment.
- Every active lower-boundary file contained two `H2SO4` rows. VULCAN reads the
  rows sequentially, so the second row silently replaced the intended
  `7.0e8 molecules cm^-2 s^-1` source with zero. The duplicate zero-flux row
  was removed.
- No active planet YAML contains a hidden numerical override. The re-runs use
  the default `count_max = 20000` and the existing convergence thresholds.

The TRAPPIST-1e bulk parameters are based on Agol et al. (2021),
<https://doi.org/10.3847/PSJ/abd022>. Radius and gravity were converted using
the repository's Earth reference radius and gravity.

## Re-run outcome

| Star/cases | Outcome | Interpretation |
| --- | --- | --- |
| Earth-Sun A0-A3 | All reached `end_case = 1` | Corrected products are converged under the configured VULCAN test. |
| TRAPPIST-1e A0-A3 | All reached `end_case = 3` at 20001 steps | Corrected products are accepted with a partial-convergence caveat because the remaining global convergence signal is dominated by low-abundance trace chemistry. |

The corrected TRAPPIST-1e `longdy` values are 0.272-0.276, compared with
0.288-0.292 in the former products. This is an improvement but remains above
the configured alternative convergence threshold of 0.1. At the step limit,
`C2H5` at approximately 0.019 bar controls `longdy`, with a mixing ratio only
slightly above the configured `mtol_conv = 1e-16`. This numerical sensitivity
must be tested explicitly rather than silently excluding the species.

## Profile comparison

The machine-readable comparison is
`Photochemical_Modeling/Results/Reproduction_2026-06-15/profile_comparison.csv`.

### Earth-Sun

- All four old and corrected products pass the saved steady-state termination
  condition.
- Surface `N2O` changes by less than 0.003%.
- Surface `NH3`, `O3`, and `CH4` changes are less than 0.05%.
- Surface `H2SO4` changes by approximately 14-19%, directly exposing the
  effect of the duplicated boundary-condition row.

### TRAPPIST-1e

- Neither the former nor corrected products are steady-state atmospheres.
- Correcting the planetary and stellar parameters changes surface `N2O` by
  about 13.4%, `O3` by about 25-27%, and `CH4` by about 19.5%.
- Profile-level differences are much larger. These are direct numerical
  results, but they must not be interpreted as steady-state chemical effects.
- `H2SO4` differences are dominated by correcting the silently overwritten
  lower-boundary flux.

## Interpretation and decision

**Direct result:** the former Earth-Sun profiles are broadly reproducible for
the principal nitrogen species, but their `H2SO4` boundary condition was not
the documented one.

**Direct result:** the former TRAPPIST-1e profiles are not reproducible under
the corrected TRAPPIST-1e physical parameters and remain non-converged.

**Project decision:** after review, promote the corrected re-runs into the
canonical output directory and delete the superseded profiles. Earth-Sun
products are the accepted steady-state profiles. TRAPPIST-1e products are the
official current profiles accepted with a partial-convergence caveat; downstream
spectra and retrievals can use them if this caveat remains explicit.

**Unresolved question:** quantify how much the trace-species convergence issue
affects the target nitrogen species and transmission spectra, especially before
claiming full-network steady state or modifying `mtol_conv`.
