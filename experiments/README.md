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
| `life_earth_sun_10pc` thermal-emission observability | Interface benchmark executed (classic branch); LIFEsimMC branch pending | `docs/life_earth_sun_10pc_interface_snr_2026-07-22.md`, `Thermal_Emission_Spectroscopy/outputs/life_earth_sun_10pc_interface_v1/` | Campaign `life_earth_sun_10pc_interface_v1`: POSEIDON emission A0--A3 + N2O/NH3 counterfactuals + LIFEsim-classic S/N. Interface validated (blackbody check PASS); ExoFarm signal below noise at LIFE baseline/10 pc (best peak N2O 7.82 µm). Pre-correction profiles (`earth_20260615_pre_n2o_correction`) — NOT the current matrix. Instrumental noise/covariance (LIFEsimMC/PHRINGE) and any retrieval still pending; SNR is a diagnostic, not a detection. |
| `life_proxima_b_earthlike` | **Executed 2026-07-23** (classic branch); LIFEsimMC pending | `docs/life_proxima_b_branch_bitacora_2026-07-22.md`, `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/` | Campaign `life_proxima_b_earthlike_v1`: MUSCLES v22 SED → VULCAN surface flux (bolometric 1.037) → VULCAN Proxima A0--A3 **all end_case=1** (corrected BC, terrestrial PT) → POSEIDON emission + N2O/NH3 counterfactuals → LIFE X-scene S/N. Result: ExoFarm A3 N2O reaches S/N=5 in ~11--32 h (vs years for Earth--Sun @10pc) — ~30--65x more detectable, a proximity effect. Controlled M-environment analogue, NOT Proxima b's measured atmosphere. SNR is a diagnostic, not a detection. |

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
