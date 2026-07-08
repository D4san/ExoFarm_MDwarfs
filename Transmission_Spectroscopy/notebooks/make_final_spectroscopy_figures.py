"""Build the provisional final spectroscopy figure set.

This script is intentionally a thin presentation layer. It reruns the plot
scripts that generate the currently selected figures and copies those products
into Transmission_Spectroscopy/final_products/figures/.

Run from Ubuntu/WSL in the Anaconda environment named POSEIDON.
"""

from pathlib import Path
import shutil

import plot_a0_a3_diagonal_distinguishability
import plot_pure_transmission_spectra
import plot_retrieved_zooms
import plot_molecular_snr_summary
import plot_trappist_simulated_observations


NOTEBOOK_DIR = Path(__file__).resolve().parent
SPECTROSCOPY_DIR = NOTEBOOK_DIR.parent
FINAL_FIGURE_DIR = SPECTROSCOPY_DIR / "final_products" / "figures"
TRAPPIST_PLOTS_DIR = NOTEBOOK_DIR / "POSEIDON_output" / "TRAPPIST-1e" / "plots"
PURE_SPECTRA_PLOTS_DIR = NOTEBOOK_DIR / "POSEIDON_output" / "pure_spectra" / "plots"

FINAL_EXTENSIONS = ("png", "pdf")

FINAL_PLOT_SOURCES = (
    (
        PURE_SPECTRA_PLOTS_DIR,
        "trappist1e_pure_a0_molecular_residuals_v2",
    ),
    (
        TRAPPIST_PLOTS_DIR,
        "trappist_A0_A3_diagonal_joint_sigma_separation",
    ),
    (
        TRAPPIST_PLOTS_DIR,
        "trappist_A0_A3_diagonal_logX_difference_posteriors",
    ),
    (
        TRAPPIST_PLOTS_DIR,
        "trappist_A3_distance_from_best_A0_reference",
    ),
    (
        TRAPPIST_PLOTS_DIR,
        "trappist_retrieved_zooms_A0_A3",
    ),
    (
        TRAPPIST_PLOTS_DIR,
        "trappist_retrieved_global_A0_A3",
    ),
    (
        TRAPPIST_PLOTS_DIR,
        "trappist_retrieved_zooms_A0_A3_v2",
    ),
    (
        TRAPPIST_PLOTS_DIR,
        "trappist_retrieved_global_A0_A3_v2",
    ),
    (
        TRAPPIST_PLOTS_DIR,
        "trappist1e_net_molecular_snr_comparison",
    ),
    (
        TRAPPIST_PLOTS_DIR,
        "trappist_simulated_observations_A3_A0",
    ),
)


def copy_plot(source_dir, stem):
    """Copy one PNG/PDF plot pair into the curated final figure directory."""

    for extension in FINAL_EXTENSIONS:
        source = source_dir / f"{stem}.{extension}"
        if not source.exists():
            print(f"Missing: {source}")
            continue
        destination = FINAL_FIGURE_DIR / source.name
        shutil.copy2(source, destination)
        print(destination)


def main():
    FINAL_FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    plot_pure_transmission_spectra.main()
    plot_a0_a3_diagonal_distinguishability.main()
    plot_retrieved_zooms.main()
    plot_molecular_snr_summary.main()
    plot_trappist_simulated_observations.main()

    for source_dir, stem in FINAL_PLOT_SOURCES:
        copy_plot(source_dir, stem)


if __name__ == "__main__":
    main()
