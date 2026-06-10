# Legacy 10x/100x Boundary Conditions

These files preserve the exploratory ExoFarm matrix used before 2026-05-27.
That matrix scaled A2 and A3 as direct multiples of the modern total flux:

| ID | Interpretation | NH3 flux | N2O flux |
| --- | --- | ---: | ---: |
| A0 | Pre-agricultural baseline used in the first VULCAN pass | 3.0e8 | 9.0e8 |
| A1 | Current Earth total-flux benchmark used in the first VULCAN pass | 1.5e9 | 2.3e9 |
| A2 | 10x modern total flux | 1.5e10 | 2.3e10 |
| A3 | 100x modern total flux | 1.5e11 | 2.3e11 |

This version is retained only as a legacy sensitivity. It is no longer the
active scenario definition because it multiplies total modern flux rather than
scaling the agricultural perturbation relative to the pre-agricultural baseline.

The active A0-A3 files live one directory up in `Boundary_Conditions/`.
