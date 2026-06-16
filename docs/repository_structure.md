# ExoFarm Repository Structure and Product Locations

**Audit date:** 2026-06-12

This document defines where new work belongs. It does not move or delete legacy
products; cleanup decisions are summarized in
[`../experiments/cleanup.md`](../experiments/cleanup.md).

## Canonical Structure

| Path | Purpose |
| :--- | :--- |
| `Agricultural_Fluxes_LPJmL/` | ExoFarm LPJmL workflows, conversion scripts, and derived agricultural-flux products. |
| `Photochemical_Modeling/Config/` | Versioned photochemical inputs and scenario configuration. |
| `Photochemical_Modeling/Results/` | Canonical VULCAN outputs and photochemistry plots. |
| `Transmission_Spectroscopy/profiles/` | Reproducible hand-off profiles from photochemistry. |
| `Transmission_Spectroscopy/notebooks/POSEIDON_output/` | Canonical forward-spectrum, synthetic-data, retrieval, and spectroscopy-plot products. |
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

Large generated products should remain beside the stage that creates them, or
outside Git when they are too large to version sensibly. Record external paths
in the relevant stage README or scientific report.
