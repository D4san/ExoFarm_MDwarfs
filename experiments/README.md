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
| Franck 2011 + LPJmL agricultural N first test | One-cell pilot accepted; portable global A1/MPI campaign prepared, execution pending on other PC | `docs/lpjml_franck2011_first_pilot_2026-09-06.md`, `docs/lpjml_global_a1_mpi_other_pc_runbook.md`, `Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction/` | Campaign `pilot_20260907T031220Z` completed. The portable package pins LPJmL 6.0.6, verifies the official archive, tests MPI on eight cells, and separates global spin-up/A1. No global N2O/NH3 result exists yet; pilot totals must not force VULCAN. |


### Campaña de retrievals Stage III

| Campaign | Status | Main evidence | Notes |
| --- | --- | --- | --- |
| `life_retrieval_matrix_2026-07-25` | **Executed 2026-07-25 (8/8 complete)** | `docs/life_stage_iii_integrated_methodology_results_2026-08-30.md`, `docs/life_stage_iii_classic_methodology_2026-08-30.md`, `docs/life_retrieval_campaign_design_2026-07-25.md`, `docs/lifesim_classic_stage_iii_validation_2026-08-30.md`, `Thermal_Emission_Spectroscopy/outputs/*/life_data/dataset_index.json` | 8 emission retrievals: Proxima b A0--A3 x {10 h, 240 h}. Con 240 h solo A3 produce una medición de N2O y excluye la referencia preagrícola efectiva a 3.14 sigma; A2/A1 son límites superiores y NH3 no discrimina. El modelo usa PT Madhu, abundancias isoquímicas, `Piette20` y prior `R_p_ref` en metros. **Sigma diagonal y una semilla: cota optimista hasta LIFEsimMC/PHRINGE con covarianza y múltiples realizaciones.** |

### Evidencia de auditoría de Stage III

| Producto | Clasificación | Evidencia | Regla de uso |
| --- | --- | --- | --- |
| Datasets Proxima A0--A3 de 1200 h + retrieval A3--1200 h | **Piloto/auditoría, excluido** | `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/README.md` | Preservar como evidencia de los fallos y correcciones del retrieval a S/N alto; no contar en la matriz 8/8 ni usar en claims canónicos. |
| Dataset y retrieval Proxima A3--500 h | **Piloto/auditoría, excluido (2026-08-31)** | `docs/life_proxima_a3_500h_retrieval_audit_2026-08-31.md`, `docs/life_proxima_a3_500h_lifesim_direct_validation_2026-08-31.md`, `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/dataset_index_500h_lifesim_direct_audit.json` | Corrida estable con PT Madhu + `Piette20` + prior físico de `R_p_ref`. El retrieval se lanzó inicialmente con sigma escalada; LIFEsim 0.2.32 directo produjo después un dataset byte a byte idéntico, por lo que no se duplicó MultiNest. No altera la matriz canónica ni el atlas oficial. |
| Retrievals robustos Proxima A3--500/1200 h | **Piloto/auditoría, excluido (2026-08-31)** | `docs/life_proxima_a3_500h_1200h_robust_retrieval_2026-08-31.md`, `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/dataset_index_500_1200h_robust_lifesim_direct_audit.json`, `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/` | Datasets directos de LIFEsim, `N_live=800`, PT Madhu, `isochem`, `Piette20` y prior físico de radio. 500 h: `ln Z=901.17`, `chi^2_red=2.07`; 1200 h: `ln Z=898.31`, `chi^2_red=2.82`. Ambos tienen posteriores completos; no cuentan en la matriz canónica ni sustentan claims de detección. |
| Prueba de perfil vertical NH3 A3--500 h | **Auditoría/diagnóstico, excluida (2026-09-01)** | `docs/life_proxima_a3_500h_nh3_two_gradients_2026-09-01.md`, `Thermal_Emission_Spectroscopy/scripts/run_life_retrieval.py`, `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/` | Mismo dataset directo; `Madhu` + `Piette20`, `N_live=1000`, `X_profile=two-gradients` solo para NH3. `ln Z=895.86`, `chi^2_red=3.15`; no mejora el isquímico (`ln Z=901.17`, `chi^2_red=2.07`) bajo estos priors. |
| Ensayo de ruido directo frente a escalado temporal | **Auditoría cerrada (2026-08-31)** | `docs/life_proxima_lifesim_noise_scaling_2026-08-31.md`, `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/lifesim_noise_scaling_comparison.csv` | A0/A3, 1--1200 h, 31 bins: la llamada directa y `sigma(10 h)*sqrt(10 h/t)` coinciden a nivel de coma flotante. Confirma el atajo para LIFEsim clásico; no evalúa covarianza ni ruido instrumental temporal de LIFEsimMC/PHRINGE. |

| Diagnósticos de Bayes factor Proxima A3--240 h | **Experimento de auditoría ejecutado (2026-09-01)** | `docs/life_proxima_bayes_factor_diagnostics_2026-09-01.md`, `Thermal_Emission_Spectroscopy/scripts/evaluate_life_bayes_factor_diagnostics.py`, `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/life_bayes_factor_diagnostics_A3_240h.csv` | Plantillas fijas sobre el mismo dataset A3: `ln B(A3/A0)=394.35` y `ln B(A3/N2O-reset)=385.63`. Diagnóstico de likelihood/Bayes factor sin nuisance parameters; no sustituye la comparación marginalizada ni la validación LIFEsimMC/PHRINGE. |

## Ramas de campaña Stage III

| Campaign | Status | Main evidence | Notes |
| --- | --- | --- | --- |
| `life_earth_sun_10pc` thermal-emission observability | Interface benchmark executed (classic branch); LIFEsimMC branch pending | `docs/life_earth_sun_10pc_interface_snr_2026-07-22.md`, `Thermal_Emission_Spectroscopy/outputs/life_earth_sun_10pc_interface_v1/` | Campaign `life_earth_sun_10pc_interface_v1`: POSEIDON emission A0--A3 + N2O/NH3 counterfactuals + LIFEsim-classic S/N. Interface validated (blackbody check PASS); ExoFarm signal below noise at LIFE baseline/10 pc (best peak N2O 7.82 µm). Pre-correction profiles (`earth_20260615_pre_n2o_correction`) — NOT the current matrix. Instrumental noise/covariance (LIFEsimMC/PHRINGE) and any retrieval still pending; SNR is a diagnostic, not a detection. |
| `life_proxima_b_earthlike` | **Executed 2026-07-23** (classic branch); LIFEsimMC pending | `docs/life_proxima_b_branch_bitacora_2026-07-22.md`, `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/` | Campaign `life_proxima_b_earthlike_v1`: MUSCLES v22 SED → VULCAN surface flux (bolometric 1.037) → VULCAN Proxima A0--A3 **all end_case=1** (corrected BC, terrestrial PT) → POSEIDON emission + N2O/NH3 counterfactuals → LIFE X-scene S/N. Result: ExoFarm A3 N2O reaches S/N=5 in ~11--32 h (vs years for Earth--Sun @10pc) — ~30--65x more detectable, a proximity effect. Controlled M-environment analogue, NOT Proxima b's measured atmosphere. SNR is a diagnostic, not a detection. |

La actualización visual del 2026-08-30--31 regeneró los PNG de espectro, señal,
comparación SNR/proyección y el atlas de retrieval de esta campaña. La última
revisión amplió los puntos observados con barras de error y recolocó la fórmula
de distancia del atlas, sin cambiar los datos ni los retrievals. La
comparación SNR/proyección fue
promovida además en PNG/PDF a `Thermal_Emission_Spectroscopy/final_products/figures/`;
el atlas de retrieval queda en
`Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/` como
salida oficial de la campaña y los scripts/productos de entrada permanecen en
la ruta de la campaña.
No se modificó la matriz científica.

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
