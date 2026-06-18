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
| `Transmission_Spectroscopy/notebooks/retrieve_trappist_A0_10.py`, `retrieve_trappist_A0_100.py`, `retrieve_trappist_A3_10.py`, `retrieve_trappist_A3_100.py` | Removed on 2026-06-16 after approval because these fixed A0/A3 10/100 wrappers are superseded by `run_trappist_retrieval.py`. | General retrieval entry point remains `Transmission_Spectroscopy/notebooks/run_trappist_retrieval.py`; campaign runner remains `run_trappist_retrieval_campaign.py`. |
| `Transmission_Spectroscopy/notebooks/run_campaign_A3_queue.sh` | Removed on 2026-06-16 after approval because it duplicated `run_campaign_trappist_queue.sh`. | `run_campaign_trappist_queue.sh` remains as the queue launcher used by `start_trappist_queue_and_tail.sh`. |
| `Transmission_Spectroscopy/notebooks/**/__pycache__/`, `Transmission_Spectroscopy/scripts/**/__pycache__/` | Removed on 2026-06-16 as generated Python cache files. | Source scripts remain in `Transmission_Spectroscopy/notebooks/` and `Transmission_Spectroscopy/scripts/`. |
| `Transmission_Spectroscopy/notebooks/POSEIDON_output/Dummy/` | Removed on 2026-06-16 after approval because it was an empty placeholder output tree. | Active products remain under `Transmission_Spectroscopy/notebooks/POSEIDON_output/TRAPPIST-1e/`. |
| `Transmission_Spectroscopy/notebooks/Plot_Transmission_Spectra_TRAPPIST.*backup*.ipynb`, `*.recovered_from_git.ipynb`, `Observation.ipynb` | Moved on 2026-06-16 to `Transmission_Spectroscopy/notebooks/legacy/` after approval. | Current scripts and curated outputs remain in `notebooks/` and `final_products/`; archived notebooks remain available for audit. |
| `Transmission_Spectroscopy/notebooks/POSEIDON_output/Earth/`, `Transmission_Spectroscopy/notebooks/POSEIDON_output/Trappist/` | Moved on 2026-06-16 to `Transmission_Spectroscopy/notebooks/POSEIDON_output/legacy/` after approval. | Current active POSEIDON products remain in `POSEIDON_output/TRAPPIST-1e/`; pure spectra remain in `POSEIDON_output/pure_spectra/`. |
| `Transmission_Spectroscopy/notebooks/POSEIDON_output/TRAPPIST-1e/retrievals/MultiNest_raw/failed_A0_5_MIRI_20260529`, `legacy_failed_resume` | Moved on 2026-06-16 to `Transmission_Spectroscopy/notebooks/POSEIDON_output/TRAPPIST-1e/retrievals/legacy_failed_runs/` after approval. | Active MultiNest raw products remain in `retrievals/MultiNest_raw/`; failed/resume evidence remains separated for audit. |

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
