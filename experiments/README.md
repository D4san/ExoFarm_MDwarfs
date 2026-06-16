# ExoFarm Campaign Index

This directory is a compact human index for ExoFarm campaigns. It is not a
second data model for the repository: the scientific evidence lives in the
stage directories and in `docs/`.

Use this file to answer three questions quickly:

1. Which campaigns are current?
2. What caveat must be stated?
3. Where is the evidence?

## Current campaigns

| Campaign | Status | Main evidence | Notes |
| --- | --- | --- | --- |
| A0-A3 flux matrix | Current design | `README.md`, `Photochemical_Modeling/README.md` | Uses the perturbation equation `F_i(A_j) = F_i(A0) + alpha_i,j * Delta F_i,agri`; do not revive the old 10x/100x total-flux matrix as current. |
| Earth-Sun A0-A3 photochemistry | Accepted steady-state products | `Photochemical_Modeling/Results/Outputs/Earth_*.vul`, `docs/vulcan_profile_reproduction_2026-06-15.md` | All four saved products reached `end_case = 1`. |
| TRAPPIST-1e A0-A3 photochemistry | Accepted with partial-convergence caveat | `Photochemical_Modeling/Results/Outputs/Trappist_*.vul`, `docs/vulcan_profile_reproduction_2026-06-15.md` | Products stopped with `end_case = 3`, but the remaining convergence signal is dominated by low-abundance trace chemistry. State this caveat explicitly. |
| TRAPPIST-1e forward spectra and retrievals | Active spectroscopy campaign | `Transmission_Spectroscopy/README.md`, `Transmission_Spectroscopy/notebooks/POSEIDON_output/TRAPPIST-1e/` | Interpret results conditional on the accepted TRAPPIST-1e partial-convergence caveat. |
| LPJmL agricultural flux workflow | Upstream method development | `Agricultural_Fluxes_LPJmL/README.md` | LPJmL products are not atmospheric abundances; nitrogen-mass fluxes must be converted to molecules cm^-2 s^-1. |

## Legacy campaigns

| Campaign | Status | Main evidence | Notes |
| --- | --- | --- | --- |
| 10x/100x total-flux sensitivity | Legacy sensitivity | `Photochemical_Modeling/Config/Boundary_Conditions/legacy_10x_100x/` | Superseded by the current perturbation matrix. |
| Combined Earth/TRAPPIST photochemistry label | Superseded bookkeeping | Current stage READMEs | Split conceptually into Earth-Sun accepted steady state and TRAPPIST-1e accepted partial convergence. |
| Root `output/` figures | Archived legacy figures | `output/` | Do not add new products here. |

## Adding a campaign

Add one row to the relevant table and link the report or stage README that
explains the scientific question, inputs, commands, products, result, and
limitations. Keep this file short; detailed interpretation belongs in `docs/`.

## Cleanup

Potential deletions are listed in `cleanup.md`. Do not delete scientific
products merely because they are old or imperfect; preserve enough evidence for
a colleague to understand what was done and why a product was superseded.
