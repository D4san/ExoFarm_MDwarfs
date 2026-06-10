import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from POSEIDON.constants import M_E, R_E, R_Sun
from POSEIDON.core import (
    compute_spectrum,
    create_planet,
    create_star,
    define_model,
    make_atmosphere,
    read_opacities,
    wl_grid_constant_R,
)
from POSEIDON.utility import read_chem_file, read_PT_file

from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE
from exofarm_transmission_workflow import (
    BULK_SPECIES,
    CHEM_SPECIES_FILE,
    CONTRIBUTION_COLOURS,
    DEFAULT_PEAK_WINDOWS,
    PARAM_SPECIES,
    PROFILES_DIR,
)


NOTEBOOK_DIR = Path(__file__).resolve().parent
PLOTS_DIR = NOTEBOOK_DIR / "POSEIDON_output" / "pure_spectra" / "plots"

SCENARIO_KEYS = ("A0", "A1", "A2", "A3")
SCENARIO_NAMES = {
    "A0": "Pre-agricultural",
    "A1": "Current Earth",
    "A2": "Moderate ExoFarm",
    "A3": "Extreme ExoFarm",
}

SCENARIO_LABELS = {
    "Earth-Sun": {
        "A0": "Earth_A0_PreAgri",
        "A1": "Earth_A1_Current",
        "A2": "Earth_A2_Moderate",
        "A3": "Earth_A3_Extreme",
    },
    "TRAPPIST-1e": {
        "A0": "Trappist_A0_PreAgri",
        "A1": "Trappist_A1_Current",
        "A2": "Trappist_A2_Moderate",
        "A3": "Trappist_A3_Extreme",
    },
}

SCENARIO_COLOURS = {
    "A1": PALETTE["golden_orange"],
    "A2": PALETTE["deep_space_blue"],
    "A3": PALETTE["dark_amaranth"],
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Plot pure ExoFarm transmission spectra without synthetic observations."
    )
    parser.add_argument("--wl-min", type=float, default=0.5)
    parser.add_argument("--wl-max", type=float, default=20.0)
    parser.add_argument("--native-r", type=float, default=10000.0)
    parser.add_argument(
        "--n-bins",
        type=int,
        default=1000,
        help="Number of logarithmic wavelength bins used in the plotted spectra.",
    )
    parser.add_argument(
        "--plot-r",
        type=float,
        default=None,
        help="Deprecated; retained only so older calls do not fail.",
    )
    return parser.parse_args()


def create_earth_sun_system():
    star = create_star(
        1.0 * R_Sun,
        5778.0,
        4.44,
        0.0,
        stellar_grid="phoenix",
    )
    planet = create_planet(
        "Earth",
        1.0 * R_E,
        mass=1.0 * M_E,
        T_eq=255.0,
    )
    return star, planet, 1.0 * R_E


def create_trappist_system():
    star = create_star(
        0.11697 * R_Sun,
        2559.0,
        5.21,
        0.04,
        stellar_grid="phoenix",
    )
    planet = create_planet(
        "TRAPPIST-1e",
        0.917985 * R_E,
        mass=0.6356 * M_E,
        T_eq=255.0,
    )
    return star, planet, 0.917985 * R_E


def pressure_grid():
    P = np.logspace(np.log10(10.0), np.log10(1.0e-10), 100)
    P_surf = 1.0
    P_ref = P_surf
    return P, P_surf, P_ref


def define_models(system_key):
    models = {}
    for scenario_key, label in SCENARIO_LABELS[system_key].items():
        models[scenario_key] = define_model(
            label,
            BULK_SPECIES,
            PARAM_SPECIES,
            PT_profile="file_read",
            X_profile="file_read",
            radius_unit="R_E",
            surface=True,
        )
    return models


def load_atmospheres(system_key, planet, models, P, P_surf, P_ref, R_p_ref):
    atmospheres = {}
    for scenario_key, model in models.items():
        label = SCENARIO_LABELS[system_key][scenario_key]
        T = read_PT_file(
            str(PROFILES_DIR),
            f"{label}_PT.txt",
            P,
            skiprows=1,
            P_column=2,
            T_column=3,
        )
        X = read_chem_file(
            str(PROFILES_DIR),
            f"{label}_chem.txt",
            P,
            CHEM_SPECIES_FILE,
            chem_species_in_model=model["chemical_species"],
            skiprows=1,
        )
        atmospheres[scenario_key] = make_atmosphere(
            planet,
            model,
            P,
            P_ref,
            R_p_ref,
            T_input=T,
            X_input=X,
            P_surf=P_surf,
        )
    return atmospheres


def compute_system_spectra(system_key, wl_min, wl_max, native_r):
    if system_key == "Earth-Sun":
        star, planet, R_p_ref = create_earth_sun_system()
    elif system_key == "TRAPPIST-1e":
        star, planet, R_p_ref = create_trappist_system()
    else:
        raise ValueError(system_key)

    P, P_surf, P_ref = pressure_grid()
    models = define_models(system_key)
    atmospheres = load_atmospheres(system_key, planet, models, P, P_surf, P_ref, R_p_ref)

    wl = wl_grid_constant_R(wl_min, wl_max, native_r)
    T_fine = np.arange(100.0, 500.0 + 10.0, 10.0)
    log_P_fine = np.arange(-10.0, 0.0 + 0.2, 0.2)
    opac = read_opacities(
        models["A0"],
        wl,
        "opacity_sampling",
        T_fine,
        log_P_fine,
        opacity_database="High-T",
    )

    spectra = {}
    for scenario_key, model in models.items():
        spectra[scenario_key] = compute_spectrum(
            planet,
            star,
            model,
            atmospheres[scenario_key],
            opac,
            wl,
            spectrum_type="transmission",
        )
    return wl, spectra


def logarithmic_bin_edges(wl_min, wl_max, n_bins):
    return np.geomspace(wl_min, wl_max, n_bins + 1)


def rebin_curve(wl, values, wl_min, wl_max, n_bins):
    edges = logarithmic_bin_edges(wl_min, wl_max, n_bins)
    wl_bins = np.sqrt(edges[:-1] * edges[1:])
    value_bins = []
    for center, left, right in zip(wl_bins, edges[:-1], edges[1:]):
        mask = (wl >= left) & (wl < right)
        if not np.any(mask):
            value_bins.append(np.interp(center, wl, values))
            continue
        value_bins.append(np.nanmedian(values[mask]))
    return wl_bins, np.asarray(value_bins)


def style_axis(ax, wl_min, wl_max):
    ax.set_xscale("log")
    ax.set_xlim(wl_min, wl_max)
    ax.set_xticks([0.5, 0.7, 1, 2, 3, 5, 8, 10, 14, 20])
    ax.set_xticklabels(["0.5", "0.7", "1", "2", "3", "5", "8", "10", "14", "20"])
    ax.tick_params(direction="in", top=True, right=True)
    ax.grid(alpha=0.12, which="both", color=PALETTE["ink_black"])
    ax.set_xlabel("Wavelength (μm)", fontfamily="serif")
    ax.set_ylabel("Transit depth (ppm)", fontfamily="serif")


def annotate_peak_windows(ax):
    label_y = 0.985
    for window in DEFAULT_PEAK_WINDOWS:
        species = window["species"]
        wl_left = window["wl_min"]
        wl_right = window["wl_max"]
        colour = CONTRIBUTION_COLOURS.get(species, PALETTE["dim_grey"])
        ax.axvspan(wl_left, wl_right, color=colour, alpha=0.09, lw=0, zorder=0)
        ax.text(
            np.sqrt(wl_left * wl_right),
            label_y,
            species.replace("2", "$_2$").replace("3", "$_3$"),
            color=colour,
            fontsize=8,
            ha="center",
            va="top",
            transform=ax.get_xaxis_transform(),
            fontfamily="serif",
        )


def plot_stacked_spectra(system_key, wl, spectra, wl_min, wl_max, n_bins, earth_a0_reference=None):
    fig, ax = plt.subplots(figsize=(9.6, 4.9), constrained_layout=True)
    rebinned = {}
    for scenario_key in SCENARIO_KEYS:
        wl_b, y_b = rebin_curve(wl, spectra[scenario_key] * 1.0e6, wl_min, wl_max, n_bins)
        rebinned[scenario_key] = y_b

    annotate_peak_windows(ax)

    # Draw the largest ExoFarm perturbation first so smaller scenarios remain visible.
    fill_styles = {
        "A3": {"alpha": 0.16, "zorder": 1},
        "A2": {"alpha": 0.18, "zorder": 2},
        "A1": {"alpha": 0.22, "zorder": 3},
    }
    line_styles = {
        "A3": {"lw": 0.72, "zorder": 7},
        "A2": {"lw": 0.78, "zorder": 8},
        "A1": {"lw": 0.84, "zorder": 9},
    }
    for scenario_key in ("A3", "A2", "A1"):
        current = rebinned[scenario_key]
        colour = SCENARIO_COLOURS[scenario_key]
        ax.fill_between(
            wl_b,
            rebinned["A0"],
            current,
            color=colour,
            alpha=fill_styles[scenario_key]["alpha"],
            label="_nolegend_",
            zorder=fill_styles[scenario_key]["zorder"],
        )
        ax.plot(
            wl_b,
            current,
            color=colour,
            alpha=0.72,
            label=f"{scenario_key}: {SCENARIO_NAMES[scenario_key]}",
            **line_styles[scenario_key],
        )

    ax.plot(
        wl_b,
        rebinned["A0"],
        color=PALETTE["ink_black"],
        lw=1.05,
        alpha=0.82,
        linestyle=":",
        label="A0: Pre-agricultural",
        zorder=12,
    )

    title = "Earth-Sun pure transmission spectra" if system_key == "Earth-Sun" else "TRAPPIST-1e pure transmission spectra"
    ax.set_title(title, fontfamily="serif", loc="left")
    style_axis(ax, wl_min, wl_max)
    ax.legend(frameon=False, fontsize=8, ncol=2, loc="best")

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    stem = (
        "earth_sun_pure_a0_difference_mountains"
        if system_key == "Earth-Sun"
        else "trappist1e_pure_a0_difference_mountains"
    )
    png_path = PLOTS_DIR / f"{stem}.png"
    pdf_path = PLOTS_DIR / f"{stem}.pdf"
    fig.savefig(png_path, dpi=240)
    fig.savefig(pdf_path)
    print(f"Saved {png_path}")
    print(f"Saved {pdf_path}")


def main():
    args = parse_args()
    earth_wl, earth_spectra = compute_system_spectra(
        "Earth-Sun", args.wl_min, args.wl_max, args.native_r
    )
    trappist_wl, trappist_spectra = compute_system_spectra(
        "TRAPPIST-1e", args.wl_min, args.wl_max, args.native_r
    )

    plot_stacked_spectra(
        "Earth-Sun",
        earth_wl,
        earth_spectra,
        args.wl_min,
        args.wl_max,
        args.n_bins,
    )
    plot_stacked_spectra(
        "TRAPPIST-1e",
        trappist_wl,
        trappist_spectra,
        args.wl_min,
        args.wl_max,
        args.n_bins,
        earth_a0_reference=(earth_wl, earth_spectra["A0"]),
    )


if __name__ == "__main__":
    main()
