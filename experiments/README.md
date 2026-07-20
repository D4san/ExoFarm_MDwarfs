# ExoFarm Campaign Index

This directory is a compact human index for ExoFarm campaigns. It is not a
second data model for the repository: the scientific evidence lives in the
stage directories and in `docs/`.

Use this file to answer three questions quickly:

1. Which campaigns are current?
2. What caveat must be stated?
3. Where is the evidence?

For the authoritative next action, read
[`../docs/project_resume.md`](../docs/project_resume.md) before using a row as
an execution instruction.

## Current campaigns

| Campaign | Status | Main evidence | Notes |
| --- | --- | --- | --- |
| A0-A3 flux matrix | Current design | `README.md`, `Photochemical_Modeling/README.md` | Uses the perturbation equation `F_i(A_j) = F_i(A0) + alpha_i,j * Delta F_i,agri`; do not revive the old 10x/100x total-flux matrix as current. A2/A3 N2O are `3.416e9`/`1.238e10`. |
| Earth-Sun A0-A3 photochemistry | Accepted pre-correction benchmark | `Photochemical_Modeling/Results/Outputs/Earth_*.vul`, `docs/earth_sun_n2o_matrix_provenance_2026-07-20.md` | All four saved products reached `end_case = 1`; A2/A3 are the 2026-06-15 N2O realization (`3.35e9`/`1.20e10`), so not the current matrix without rerun or historical label. |
| TRAPPIST-1e A0-A3 photochemistry | Accepted with partial-convergence caveat | `Photochemical_Modeling/Results/Outputs/Trappist_*.vul`, `docs/vulcan_profile_reproduction_2026-06-15.md` | Products stopped with `end_case = 3`, but the remaining convergence signal is dominated by low-abundance trace chemistry. State this caveat explicitly. |
| TRAPPIST-1e forward spectra and retrievals | Active spectroscopy campaign | `Transmission_Spectroscopy/README.md`, `Transmission_Spectroscopy/notebooks/POSEIDON_output/TRAPPIST-1e/` | Interpret results conditional on the accepted TRAPPIST-1e partial-convergence caveat. |
| LPJmL agricultural flux workflow | Suspended by project decision | `Agricultural_Fluxes_LPJmL/README.md`, `docs/project_status_tracker.md` | Preserve the workflow and conversion discipline; do not start LPJmL runs or force coupling until explicitly reactivated. |


## Planned campaigns

| Campaign | Status | Main evidence | Notes |
| --- | --- | --- | --- |
| `life_earth_sun_10pc` thermal-emission observability | Planned; only environment/interface design, no products yet | `Thermal_Emission_Spectroscopy/README.md`, `docs/life_stage_iii_two_layer_workplan_2026-07-20.md` | Capa 1 uses the pre-correction Earth--Sun PT/química set only for interface validation. Environment/manifiesto precede a forward A0; no SNR/retrieval result may represent the current matrix before the provenance decision. |
| `life_proxima_b_earthlike` | Planned; blocked by SED-to-VULCAN and new photochemistry | `docs/life_stage_iii_two_layer_workplan_2026-07-20.md`, `docs/life_target_selection_2026-07-20.md` | Capa 2: SED MUSCLES → flujo superficial VULCAN → Proxima A0--A3 → misma cadena LIFE. Es análogo terrestre controlado, no atmósfera medida de Proxima b. |

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
