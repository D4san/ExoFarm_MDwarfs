"""Build the curated final spectroscopy figure set.

This script is intentionally a thin presentation layer. It reuses the working
POSEIDON/retrieval plotting code and copies only the current narrative figures
into Transmission_Spectroscopy/final_products/figures/.

Run from Ubuntu/WSL in the Anaconda environment named POSEIDON.
"""

from pathlib import Path
import shutil

import matplotlib.pyplot as plt

from exofarm_transmission_workflow import (
    SCENARIOS,
    compute_forward_spectra,
    create_pressure_grid,
    create_trappist_system,
    define_forward_models,
    load_profiles,
    make_atmospheres,
    make_wavelength_grid_and_opacities,
    plot_observations_by_noise_level,
)
import plot_a0_a3_posterior_sigma_matrix
import plot_retrieval_spectra_products
import plot_retrieved_truth_extremes


NOTEBOOK_DIR = Path(__file__).resolve().parent
SPECTROSCOPY_DIR = NOTEBOOK_DIR.parent
FINAL_FIGURE_DIR = SPECTROSCOPY_DIR / "final_products" / "figures"
WORKING_PLOTS_DIR = NOTEBOOK_DIR / "POSEIDON_output" / "TRAPPIST-1e" / "plots"

FINAL_EXTENSIONS = ("png", "pdf")


def compute_current_trappist_spectra():
    """Compute the A0-A3 forward spectra needed by the synthetic-data figure."""

    scenario_keys = tuple(SCENARIOS)
    star, planet = create_trappist_system()
    pressure, pressure_surface, pressure_ref, radius_ref = create_pressure_grid()
    models = define_forward_models(scenario_keys)
    temperatures, compositions = load_profiles(models, pressure, scenario_keys)
    atmospheres = make_atmospheres(
        planet,
        models,
        pressure,
        pressure_ref,
        radius_ref,
        pressure_surface,
        temperatures,
        compositions,
    )
    wavelength, opacities = make_wavelength_grid_and_opacities(models[scenario_keys[0]])
    spectra = compute_forward_spectra(planet, star, models, atmospheres, opacities, wavelength)
    return wavelength, spectra, scenario_keys


def save_final_synthetic_observation_figure():
    """Save the four-scenario synthetic-observation figure into final_products."""

    wavelength, spectra, scenario_keys = compute_current_trappist_spectra()
    fig = plot_observations_by_noise_level(
        wavelength,
        spectra,
        scenario_keys,
        transit_counts=(5, 10, 20),
        wl_min=0.8,
        wl_max=12.0,
    )
    output_stem = FINAL_FIGURE_DIR / "final_synthetic_observations_by_noise_level"
    for extension in FINAL_EXTENSIONS:
        output = output_stem.with_suffix(f".{extension}")
        fig.savefig(output, dpi=240, bbox_inches="tight")
        print(output)
    plt.close(fig)


def copy_working_plot(stem):
    """Copy an existing working plot into the curated final figure directory."""

    for extension in FINAL_EXTENSIONS:
        source = WORKING_PLOTS_DIR / f"{stem}.{extension}"
        if not source.exists():
            print(f"Missing: {source}")
            continue
        destination = FINAL_FIGURE_DIR / source.name
        shutil.copy2(source, destination)
        print(destination)


def main():
    FINAL_FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    save_final_synthetic_observation_figure()

    plot_retrieval_spectra_products.main()
    plot_retrieved_truth_extremes.main()
    plot_a0_a3_posterior_sigma_matrix.main()

    for stem in (
        "trappist_retrieval_A3_retrieved_noise_background",
        "trappist_retrieval_A3_retrieved_spectra_grid",
        "trappist_retrieved_truth_extremes_A3_10_100transits",
        "trappist_A0_A3_posterior_sigma_distance_matrix",
    ):
        copy_working_plot(stem)


if __name__ == "__main__":
    main()
