# Cleanup Notes

This file records products that may be removed after human review. It replaces
the former generated registry and keeps cleanup decisions readable.

General cleanup procedure:
[`../docs/repository_cleanup_workflow.md`](../docs/repository_cleanup_workflow.md).

## Already cleaned

| Path | Decision | Evidence |
| --- | --- | --- |
| `Transmission_Spectroscopy/vulcan_outputs/*.vul` | Removed from the active hand-off because these were duplicate raw `.vul` copies. | Canonical products live in `Photochemical_Modeling/Results/Outputs/`; profile hand-off files live in `Transmission_Spectroscopy/profiles/`. |
| `Photochemical_Modeling/temp_run_*` | Removed on 2026-06-16 after review because these were untracked temporary VULCAN workspaces. | Canonical `.vul` products remain in `Photochemical_Modeling/Results/Outputs/`; audit evidence remains in `Photochemical_Modeling/Results/Reproduction_2026-06-15/`. |
| `Photochemical_Modeling/Scripts/**/__pycache__/` | Removed on 2026-06-16 as generated Python cache files. | Source scripts remain under `Photochemical_Modeling/Scripts/`. |

## Review before deletion

| Path | Reason | Keep before deleting |
| --- | --- | --- |
| `photochemical_modelling_photochem...Earth_A1_profile_comparison.png` | Malformed root-level duplicate with encoded path separators. | Confirm the canonical figure exists under `output/figures/` or `Photochemical_Modeling/Results/Plots/`. |
| `output/` | Legacy root-level figures. | Keep unless every figure has a documented canonical replacement and no report depends on the legacy copy. |
| `POSEIDON_output/` | Empty or obsolete root-level POSEIDON tree if unused. | Confirm active POSEIDON products are under `Transmission_Spectroscopy/notebooks/POSEIDON_output/`. |

## Rule

Deletion is allowed only when:

1. the path is listed here;
2. a canonical replacement or reason for removal is clear;
3. inputs, commands, reports, or logs needed to understand the result remain;
4. the user explicitly approves the deletion.
