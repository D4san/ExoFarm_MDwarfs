# ExoFarm Repository Structure and Product Locations

**Audit date:** 2026-06-12 (Stage III routing added 2026-07-20)

This document defines where new work belongs. It does not move or delete legacy
products; cleanup decisions are summarized in
[`../experiments/cleanup.md`](../experiments/cleanup.md). To recover the active
scope before placing a product, read
[`project_resume.md`](project_resume.md) and
[`project_status_tracker.md`](project_status_tracker.md).

## Canonical Structure

| Path | Purpose |
| :--- | :--- |
| `Agricultural_Fluxes_LPJmL/` | ExoFarm LPJmL workflows, conversion scripts, and derived agricultural-flux products. |
| `Photochemical_Modeling/Config/` | Versioned photochemical inputs and scenario configuration. The future Proxima SED source/conversion belongs under `Config/Stellar_Spectra/`; the future `earth_proxima_b/` YAMLs belong under `Config/planets/`. |
| `Photochemical_Modeling/Results/` | Canonical VULCAN outputs and photochemistry plots; future `Proxima_b_A*.vul` products remain here, not in Stage III. |
| `Transmission_Spectroscopy/profiles/` | Reproducible hand-off profiles from photochemistry. |
| `Transmission_Spectroscopy/notebooks/POSEIDON_output/` | Canonical forward-spectrum, synthetic-data, retrieval, and spectroscopy-plot products. |
| `Thermal_Emission_Spectroscopy/` | Etapa III planificada: `configs/life_earth_sun_10pc/` para la Capa 1, `configs/life_proxima_b_earthlike/` para la Capa 2 posterior a VULCAN, adaptadores y productos de emisión/LIFE. La Capa 1 solo puede crear productos bajo `outputs/life_earth_sun_10pc/` con manifiesto que etiquete `earth_20260615_pre_n2o_correction` hasta la decisión de procedencia. No almacenar aquí resultados de transmisión, PandExo ni `.vul` crudos. |
| `docs/` | Persistent scientific reports and methodological analyses. |
| `experiments/` | Compact campaign index and reviewed cleanup notes. |

The local upstream LPJmL checkout belongs under
`Agricultural_Fluxes_LPJmL/software/LPJmL/`, but it is not vendored as ExoFarm
source. Record the upstream commit in experiment records. Large official input
datasets remain outside Git.

## Non-Canonical and Legacy Paths

| Path | Classification | Rule |
| :--- | :--- | :--- |
| `output/` | Archived legacy figures | Do not add new products; retained as historical diagnostic evidence. |
| `POSEIDON_output/` | Empty local directory tree | Do not use; the canonical path is inside `Transmission_Spectroscopy/notebooks/`. |
| `Transmission_Spectroscopy/vulcan_outputs/` | Retired duplicate hand-off copies | Canonical `.vul` files live in photochemistry. |
| `photochemical_modelling_photochem...png` | Exact malformed-path duplicate | Cleanup candidate; retain until deletion review is approved. |

## Placement Rules

1. Put model configuration and small reproducibility inputs in Git.
2. Put generated products beside the stage that creates them.
3. Record substantial campaigns in `experiments/README.md` before expensive execution.
4. Link scientific reports to exact evidence products.
5. Do not create a new generic `output/`, `results/`, or `figures/` directory at
   repository root.
6. Do not delete a legacy or failed product merely because a newer product
   exists; follow the experiment deletion gate.
7. Keep the future LIFE/LIFEsimMC products under
   `Thermal_Emission_Spectroscopy/outputs/<campaign-id>/`; do not create a
   second repository-root output tree or mix them into `Transmission_Spectroscopy/`.
8. For `life_proxima_b_earthlike`, preserve the raw MUSCLES SED and conversion
   metadata under `Photochemical_Modeling/Config/Stellar_Spectra/`; retain the
   new VULCAN profiles in `Photochemical_Modeling/Results/Outputs/` and export
   only the PT/chemistry hand-off needed by Stage III.

Large generated products should remain beside the stage that creates them, or
outside Git when they are too large to version sensibly. Record external paths
in the relevant stage README or scientific report.
