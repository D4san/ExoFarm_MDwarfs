import argparse
import csv
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

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
    PARAM_SPECIES,
    PROFILES_DIR,
)


NOTEBOOK_DIR = Path(__file__).resolve().parent
REPO_ROOT = NOTEBOOK_DIR.parents[1]
DOCS_DIR = REPO_ROOT / "docs"
PLOTS_DIR = NOTEBOOK_DIR / "POSEIDON_output" / "pure_spectra" / "plots"
SYNTHETIC_DATA_DIR = NOTEBOOK_DIR / "POSEIDON_output" / "TRAPPIST-1e" / "synthetic_data" / "base_1transit"
COUNTERFACTUAL_PROFILE_DIR = PROFILES_DIR / "counterfactual_A0_replacements"
PEAK_SUMMARY_CSV = PLOTS_DIR / "trappist1e_net_molecular_peak_summary.csv"
COUNTERFACTUAL_VALIDATION_CSV = PLOTS_DIR / "trappist1e_counterfactual_chemistry_validation.csv"
PEAK_SUMMARY_NOTE = DOCS_DIR / "trappist1e_net_molecular_contribution_peaks_2026-06-17.md"
NOISE_TRANSIT_COUNTS = (1, 10, 100)
INSTRUMENT_NOISE_FILES = {
    "NIRSpec_PRISM": SYNTHETIC_DATA_DIR / "TRAPPIST-1e_flat_NIRSpec_Prism_1_transits.dat",
    "MIRI_LRS": SYNTHETIC_DATA_DIR / "TRAPPIST-1e_flat_MIRI_LRS_1_transits.dat",
}
MOLECULAR_DELTA_SPECIES = ("N2O", "NH3", "H2O")
MOLECULE_LABELS = {
    "N2O": r"N$_2$O",
    "NH3": r"NH$_3$",
    "H2O": r"H$_2$O",
}
MOLECULAR_LABEL_COLOURS = {
    "N2O": "#1f77b4",
    "NH3": "#ff7f0e",
    "H2O": PALETTE["deep_space_blue"],
}
PEAK_MIN_SEPARATION_BINS = 25

SCENARIO_KEYS = ("A0", "A1", "A2", "A3")
COUNTERFACTUAL_SCENARIO_KEYS = ("A1", "A2", "A3")
SCENARIO_NAMES = {
    "A0": "Pre-agricultural scenario",
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
    "A0": PALETTE["dim_grey"],
    "A1": PALETTE["scenario_cyan"],
    "A2": PALETTE["scenario_green"],
    "A3": "#E34F95",
}
SCENARIO_FILL_ORDER = ("A3", "A2", "A1")
RESIDUAL_DARK_COLOURS = {
    "A1": PALETTE["deep_space_blue"],
    "A2": PALETTE["deep_moss"],
    "A3": PALETTE["dark_amaranth"],
}
MOLECULAR_SIGNATURE_COLOURS = {
    "N2O": PALETTE["scenario_violet"],
    "NH3": PALETTE["scenario_green"],
    "H2O": PALETTE["scenario_cyan"],
}
MOLECULAR_SIGNAL_WINDOWS = {
    "N2O": (
        ("N2O_2p6_3p0", 2.60, 3.00),
        ("N2O_4p3_4p8", 4.30, 4.80),
        ("N2O_7p5_9p0", 7.50, 9.00),
        ("N2O_16p0_18p0", 16.00, 18.00),
    ),
    "NH3": (
        ("NH3_9p0_10p0", 9.00, 10.00),
        ("NH3_10p0_11p2", 10.00, 11.20),
        ("NH3_11p2_12p0", 11.20, 12.00),
    ),
    "H2O": (
        ("H2O_2p4_3p0", 2.40, 3.00),
        ("H2O_5p0_6p2", 5.00, 6.20),
        ("H2O_6p2_7p2", 6.20, 7.20),
    ),
}
TOP_SPECTRUM_ANNOTATIONS = (
    (2.85, r"N$_2$O", 42.0),
    (4.55, r"N$_2$O", 14.0),
    (8.65, r"N$_2$O", 6.0),
    (10.75, r"NH$_3$", 6.0),
)
INSTRUMENT_COVERAGE_BARS = (
    (0.6025, 5.2976, "NIRSpec PRISM", PALETTE["charcoal_violet"]),
    (5.0213, 11.9998, "MIRI LRS", PALETTE["scenario_cyan"]),
)


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
    parser.add_argument(
        "--include-legacy-v1",
        action="store_true",
        help=(
            "Also render the legacy trappist1e_pure_a0_difference_mountains "
            "layout. The default official output is v2 only."
        ),
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
    temperatures = {}
    compositions = {}
    for scenario_key, model in models.items():
        label = SCENARIO_LABELS[system_key][scenario_key]
        temperatures[scenario_key] = read_PT_file(
            str(PROFILES_DIR),
            f"{label}_PT.txt",
            P,
            skiprows=1,
            P_column=2,
            T_column=3,
        )
        compositions[scenario_key] = read_chem_file(
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
            T_input=temperatures[scenario_key],
            X_input=compositions[scenario_key],
            P_surf=P_surf,
        )
    return atmospheres, temperatures, compositions


def build_system_products(system_key, wl_min, wl_max, native_r):
    if system_key == "Earth-Sun":
        star, planet, R_p_ref = create_earth_sun_system()
    elif system_key == "TRAPPIST-1e":
        star, planet, R_p_ref = create_trappist_system()
    else:
        raise ValueError(system_key)

    P, P_surf, P_ref = pressure_grid()
    models = define_models(system_key)
    atmospheres, temperatures, compositions = load_atmospheres(
        system_key,
        planet,
        models,
        P,
        P_surf,
        P_ref,
        R_p_ref,
    )

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
    return {
        "star": star,
        "planet": planet,
        "models": models,
        "atmospheres": atmospheres,
        "temperatures": temperatures,
        "compositions": compositions,
        "wl": wl,
        "opac": opac,
        "spectra": spectra,
        "P": P,
        "P_surf": P_surf,
        "P_ref": P_ref,
        "R_p_ref": R_p_ref,
    }


def compute_system_spectra(system_key, wl_min, wl_max, native_r):
    products = build_system_products(system_key, wl_min, wl_max, native_r)
    return products["wl"], products["spectra"]


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
    ax.set_ylabel(
        "Transit depth\n" r"$[(R_p/R_s)^2]$ (ppm)",
        fontfamily="serif",
        fontsize=16,
        color="black",
    )


def style_delta_axis(ax, wl_min, wl_max):
    ax.set_xscale("log")
    ax.set_xlim(wl_min, wl_max)
    ax.set_xticks([0.5, 0.7, 1, 2, 3, 5, 8, 10, 14, 20])
    ax.set_xticklabels(["0.5", "0.7", "1", "2", "3", "5", "8", "10", "14", "20"])
    ax.tick_params(direction="in", top=True, right=True)
    ax.grid(alpha=0.12, which="both", color=PALETTE["ink_black"])
    ax.tick_params(axis="both", labelsize=14)


def hex_to_rgb01(hex_colour):
    stripped = hex_colour.lstrip("#")
    return np.array([int(stripped[i : i + 2], 16) / 255.0 for i in (0, 2, 4)])


def rgb01_to_hex(rgb):
    clipped = np.clip(rgb, 0.0, 1.0)
    return "#" + "".join(f"{int(round(channel * 255)):02X}" for channel in clipped)


def blend_hex(hex_colour, target_hex, fraction):
    colour = hex_to_rgb01(hex_colour)
    target = hex_to_rgb01(target_hex)
    return rgb01_to_hex((1.0 - fraction) * colour + fraction * target)


def molecular_signature_colour(species, scenario_key):
    base = MOLECULAR_SIGNATURE_COLOURS[species]
    if scenario_key == "A3":
        return blend_hex(base, PALETTE["ink_black"], 0.18)
    if scenario_key == "A2":
        return base
    if scenario_key == "A1":
        return blend_hex(base, PALETTE["dust_grey"], 0.34)
    raise ValueError(scenario_key)


def annotate_top_molecular_regions(ax, wavelengths, rebinned_total):
    envelope = np.maximum.reduce([rebinned_total[key] for key in SCENARIO_KEYS])
    for wavelength, label, y_offset in TOP_SPECTRUM_ANNOTATIONS:
        y_value = np.interp(wavelength, wavelengths, envelope)
        ax.text(
            wavelength,
            y_value + y_offset,
            label,
            color="black",
            fontsize=12,
            fontfamily="serif",
            ha="center",
            va="bottom",
            zorder=20,
        )


def annotate_instrument_coverage(ax, y_base, y_step):
    for index, (left, right, label, colour) in enumerate(INSTRUMENT_COVERAGE_BARS):
        y_position = y_base + index * y_step
        ax.hlines(
            y_position,
            left,
            right,
            color=colour,
            linewidth=2.8,
            zorder=18,
        )
        ax.vlines(
            [left, right],
            y_position - 0.42 * y_step,
            y_position + 0.42 * y_step,
            color=colour,
            linewidth=1.35,
            zorder=18,
        )
        ax.text(
            np.sqrt(left * right),
            y_position + 0.48 * y_step,
            label,
            color="black",
            fontsize=10.0,
            fontfamily="serif",
            ha="center",
            va="bottom",
            zorder=19,
        )


def scenario_delta_linewidth(scenario_key):
    return {
        "A1": 2.1,
        "A2": 1.9,
        "A3": 1.0,
    }[scenario_key]


def scenario_delta_zorder(scenario_key):
    return {
        "A3": 4,
        "A2": 6,
        "A1": 8,
    }[scenario_key]


def read_chemistry_table(path):
    header = path.read_text(encoding="utf-8").splitlines()[0].split()
    data = np.loadtxt(path, skiprows=1)
    return header, data


def source_chemistry_path(system_key, scenario_key):
    label = SCENARIO_LABELS[system_key][scenario_key]
    return PROFILES_DIR / f"{label}_chem.txt"


def counterfactual_chemistry_filename(system_key, scenario_key, species):
    label = SCENARIO_LABELS[system_key][scenario_key]
    return f"{label}_reset_{species}_to_A0_chem.txt"


def make_counterfactual_chemistry_file(system_key, scenario_key, species):
    source_path = source_chemistry_path(system_key, scenario_key)
    baseline_path = source_chemistry_path(system_key, "A0")
    source_header, source_data = read_chemistry_table(source_path)
    baseline_header, baseline_data = read_chemistry_table(baseline_path)

    if source_header != baseline_header:
        raise ValueError(f"Chemistry headers differ between {source_path} and {baseline_path}")
    if source_data.shape != baseline_data.shape:
        raise ValueError(f"Chemistry table shapes differ between {source_path} and {baseline_path}")
    if species not in source_header:
        raise ValueError(f"{species} is absent from {source_path}")

    species_index = source_header.index(species)
    pressure_index = source_header.index("PRESS")
    modified_data = np.array(source_data, copy=True)
    modified_data[:, species_index] = baseline_data[:, species_index]

    COUNTERFACTUAL_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    output_path = COUNTERFACTUAL_PROFILE_DIR / counterfactual_chemistry_filename(
        system_key,
        scenario_key,
        species,
    )
    np.savetxt(
        output_path,
        modified_data,
        header=" ".join(source_header),
        comments="",
        fmt="%.6e",
    )

    other_columns = [idx for idx in range(source_data.shape[1]) if idx != species_index]
    validation_row = {
        "scenario": scenario_key,
        "molecule": species,
        "chemistry_file": str(output_path.relative_to(REPO_ROOT)),
        "source_column": species_index,
        "source_pressure_max_abs_error": float(
            np.nanmax(np.abs(modified_data[:, pressure_index] - source_data[:, pressure_index]))
        ),
        "source_replaced_species_max_abs_error": float(
            np.nanmax(np.abs(modified_data[:, species_index] - baseline_data[:, species_index]))
        ),
        "source_other_species_max_abs_error": float(
            np.nanmax(np.abs(modified_data[:, other_columns] - source_data[:, other_columns]))
        ),
        "source_species_shift_max_abs": float(
            np.nanmax(np.abs(source_data[:, species_index] - baseline_data[:, species_index]))
        ),
    }
    return output_path, validation_row


def make_counterfactual_chemistry_files(system_key, species_order, scenario_keys):
    paths = {}
    validation_rows = []
    for species in species_order:
        paths[species] = {}
        for scenario_key in scenario_keys:
            path, validation_row = make_counterfactual_chemistry_file(
                system_key,
                scenario_key,
                species,
            )
            paths[species][scenario_key] = path
            validation_rows.append(validation_row)
    return paths, validation_rows


def validate_loaded_counterfactual_composition(products, scenario_key, species, composition, validation_row):
    model = products["models"][scenario_key]
    species_names = list(model["chemical_species"])
    species_index = species_names.index(species)

    expected = np.array(products["compositions"][scenario_key], copy=True)
    expected[species_index, :] = products["compositions"]["A0"][species_index, :]
    bulk_indices = [species_names.index(name) for name in BULK_SPECIES if name in species_names]
    explicit_other_indices = [
        idx
        for idx in range(expected.shape[0])
        if idx != species_index and idx not in bulk_indices
    ]
    explicit_indices = [idx for idx in range(expected.shape[0]) if idx not in bulk_indices]

    validation_row["loaded_replaced_species_max_abs_error"] = float(
        np.nanmax(np.abs(composition[species_index, :] - products["compositions"]["A0"][species_index, :]))
    )
    validation_row["loaded_other_species_max_abs_error"] = float(
        np.nanmax(
            np.abs(
                composition[explicit_other_indices, :]
                - products["compositions"][scenario_key][explicit_other_indices, :]
            )
        )
    )
    validation_row["loaded_total_max_abs_error"] = float(
        np.nanmax(np.abs(composition[explicit_indices, :] - expected[explicit_indices, :]))
    )
    validation_row["loaded_bulk_species_shift_max_abs"] = float(
        np.nanmax(
            np.abs(
                composition[bulk_indices, :]
                - products["compositions"][scenario_key][bulk_indices, :]
            )
        )
        if bulk_indices
        else 0.0
    )

    tolerance = 1.0e-12
    if validation_row["loaded_total_max_abs_error"] > tolerance:
        raise ValueError(
            f"Loaded counterfactual composition failed validation for {scenario_key} {species}: "
            f"max error = {validation_row['loaded_total_max_abs_error']:.3e}"
        )


def compute_counterfactual_spectrum(products, scenario_key, species, chemistry_path, validation_row):
    model = products["models"][scenario_key]
    temperatures = products["temperatures"][scenario_key]
    modified_composition = read_chem_file(
        str(chemistry_path.parent),
        chemistry_path.name,
        products["P"],
        CHEM_SPECIES_FILE,
        chem_species_in_model=model["chemical_species"],
        skiprows=1,
    )
    validate_loaded_counterfactual_composition(
        products,
        scenario_key,
        species,
        modified_composition,
        validation_row,
    )

    counterfactual_atmosphere = make_atmosphere(
        products["planet"],
        model,
        products["P"],
        products["P_ref"],
        products["R_p_ref"],
        T_input=temperatures,
        X_input=modified_composition,
        P_surf=products["P_surf"],
    )

    return compute_spectrum(
        products["planet"],
        products["star"],
        model,
        counterfactual_atmosphere,
        products["opac"],
        products["wl"],
        spectrum_type="transmission",
    )


def compute_counterfactual_spectra(products, species_order, scenario_keys, chemistry_paths, validation_rows):
    validation_by_key = {
        (row["molecule"], row["scenario"]): row
        for row in validation_rows
    }
    counterfactuals = {}
    for species in species_order:
        counterfactuals[species] = {}
        for scenario_key in scenario_keys:
            counterfactuals[species][scenario_key] = compute_counterfactual_spectrum(
                products,
                scenario_key,
                species,
                chemistry_paths[species][scenario_key],
                validation_by_key[(species, scenario_key)],
            )
    return counterfactuals


def detect_top_abs_peaks(wavelengths, values, top_n=3, min_separation_bins=PEAK_MIN_SEPARATION_BINS):
    absolute = np.abs(values)
    if len(values) == 0:
        return []

    local_candidates = []
    for idx in range(1, len(values) - 1):
        if absolute[idx] >= absolute[idx - 1] and absolute[idx] > absolute[idx + 1]:
            local_candidates.append(idx)

    if not local_candidates:
        local_candidates = [int(np.nanargmax(absolute))]

    ranked_candidates = sorted(local_candidates, key=lambda idx: absolute[idx], reverse=True)
    selected = []
    for idx in ranked_candidates:
        if any(abs(idx - kept_idx) < min_separation_bins for kept_idx in selected):
            continue
        selected.append(idx)
        if len(selected) == top_n:
            break

    if len(selected) < top_n:
        fallback_candidates = np.argsort(absolute)[::-1]
        for idx in fallback_candidates:
            idx = int(idx)
            if any(abs(idx - kept_idx) < min_separation_bins for kept_idx in selected):
                continue
            selected.append(idx)
            if len(selected) == top_n:
                break

    rows = []
    for rank, idx in enumerate(selected[:top_n], start=1):
        rows.append(
            {
                "peak_rank": rank,
                "wavelength_micron": float(wavelengths[idx]),
                "signal_ppm": float(values[idx]),
                "absolute_signal_ppm": float(abs(values[idx])),
            }
        )
    return rows


def detect_window_signal_peaks(wavelengths, values, windows):
    rows = []
    for rank, (band_id, window_min, window_max) in enumerate(windows, start=1):
        mask = (wavelengths >= window_min) & (wavelengths <= window_max)
        if not np.any(mask):
            continue
        window_indices = np.flatnonzero(mask)
        local_index = int(np.nanargmax(np.abs(values[mask])))
        idx = int(window_indices[local_index])
        rows.append(
            {
                "peak_rank": rank,
                "band_id": band_id,
                "window_min_micron": float(window_min),
                "window_max_micron": float(window_max),
                "wavelength_micron": float(wavelengths[idx]),
                "signal_ppm": float(values[idx]),
                "absolute_signal_ppm": float(abs(values[idx])),
            }
        )
    return rows


def load_noise_curves():
    curves = {}
    for instrument, path in INSTRUMENT_NOISE_FILES.items():
        data = np.loadtxt(path, skiprows=1)
        curves[instrument] = {
            "path": path,
            "wavelength": data[:, 0],
            "sigma_ppm": data[:, 3] * 1.0e6,
        }
    return curves


def noise_at_wavelength(wavelength_micron, noise_curves):
    for instrument in ("NIRSpec_PRISM", "MIRI_LRS"):
        curve = noise_curves[instrument]
        wavelengths = curve["wavelength"]
        if wavelengths[0] <= wavelength_micron <= wavelengths[-1]:
            index = int(np.argmin(np.abs(wavelengths - wavelength_micron)))
            return instrument, float(curve["sigma_ppm"][index])
    return "outside_coverage", np.nan


def add_noise_scaled_snr(rows):
    noise_curves = load_noise_curves()
    enriched_rows = []
    for row in rows:
        enriched = dict(row)
        instrument, sigma_1transit_ppm = noise_at_wavelength(
            row["wavelength_micron"],
            noise_curves,
        )
        enriched["noise_instrument"] = instrument
        enriched["sigma_1transit_ppm"] = sigma_1transit_ppm
        for n_transits in NOISE_TRANSIT_COUNTS:
            key = f"snr_{n_transits}transit"
            if np.isfinite(sigma_1transit_ppm) and sigma_1transit_ppm > 0.0:
                enriched[key] = row["absolute_signal_ppm"] * np.sqrt(n_transits) / sigma_1transit_ppm
            else:
                enriched[key] = np.nan
        enriched_rows.append(enriched)
    return enriched_rows


def export_peak_summary_csv(rows):
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    rows = add_noise_scaled_snr(rows)
    fieldnames = [
        "scenario",
        "molecule",
        "peak_rank",
        "band_id",
        "window_min_micron",
        "window_max_micron",
        "wavelength_micron",
        "signal_ppm",
        "absolute_signal_ppm",
        "noise_instrument",
        "sigma_1transit_ppm",
        "snr_1transit",
        "snr_10transit",
        "snr_100transit",
    ]
    with PEAK_SUMMARY_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def export_counterfactual_validation_csv(rows):
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "scenario",
        "molecule",
        "chemistry_file",
        "source_column",
        "source_pressure_max_abs_error",
        "source_replaced_species_max_abs_error",
        "source_other_species_max_abs_error",
        "source_species_shift_max_abs",
        "loaded_replaced_species_max_abs_error",
        "loaded_other_species_max_abs_error",
        "loaded_total_max_abs_error",
        "loaded_bulk_species_shift_max_abs",
    ]
    with COUNTERFACTUAL_VALIDATION_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def export_peak_summary_note(rows):
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    generated_on = date.today().isoformat()
    rows = add_noise_scaled_snr(rows)
    grouped = {}
    for row in rows:
        grouped.setdefault((row["scenario"], row["molecule"]), []).append(row)

    lines = [
        "# Picos de contribución molecular neta en TRAPPIST-1e, 2026-06-17",
        "",
        f"Fecha de generación: `{generated_on}`.",
        "",
        "## Propósito",
        "",
        "Registrar un diagnóstico contrafactual de contribución molecular neta para los espectros de transmisión de ExoFarm en TRAPPIST-1e.",
        "",
        "## Insumos",
        "",
        "- Script: `Transmission_Spectroscopy/notebooks/plot_pure_transmission_spectra.py`",
        "- Perfiles PT y químicos exportados en `Transmission_Spectroscopy/profiles/`",
        "- Perfiles químicos contrafactuales derivados en `Transmission_Spectroscopy/profiles/counterfactual_A0_replacements/`",
        "- Espectros forward POSEIDON calculados con la misma malla de presión, la misma grilla espectral y el mismo conjunto de opacidades que la figura principal",
        "",
        "## Definición del contrafactual",
        "",
        "Para cada escenario `A1`, `A2` y `A3`, y para cada molécula `N2O`, `NH3`, `H2O`, se recalcula un espectro forward manteniendo todo el escenario objetivo fijo excepto el perfil vertical de esa molécula, que se reemplaza por el perfil del escenario `A0`.",
        "",
        "El reemplazo se materializa primero en archivos `*_reset_<mol>_to_A0_chem.txt`; esos archivos derivados son los que se cargan de nuevo con `read_chem_file` para construir los nueve espectros contrafactuales.",
        "",
        "La curva neta exportada y graficada es:",
        "",
        "```text",
        "Net_mol(S) = Spectrum_full(S) - Spectrum_with_molecule_reset_to_A0(S)",
        "```",
        "",
        "Esto cuantifica el efecto espectral neto de la perturbación de esa molécula dentro del escenario completo. Es una prueba de necesidad contrafactual: cuánto cambia el espectro del escenario `S` si sólo esa molécula se devuelve a su perfil `A0` y el resto del escenario permanece fijo.",
        "",
        "No es una descomposición estrictamente aditiva del residual total. Las bandas pueden solaparse y otras moléculas pueden reforzar o contrarrestar la señal neta, por lo que la suma de `Net_mol(S)` para `N2O`, `NH3` y `H2O` no tiene por qué reproducir `Spectrum_full(S) - Spectrum_full(A0)`.",
        "",
        "## Trazabilidad de la figura oficial v2",
        "",
        "La figura oficial de trabajo es `trappist1e_pure_a0_molecular_residuals_v2.{png,pdf}`. Tiene cuatro paneles:",
        "",
        "- Panel superior: espectros puros de transmisión para `A0`, `A1`, `A2` y `A3`, con relleno entre cada escenario agrícola y `A0`.",
        "- Paneles inferiores: señales moleculares netas para `N2O`, `NH3` y `H2O`. En cada panel se superpone el residual total `A_j - A0` como línea continua oscura, y se rellena la señal molecular contrafactual del mismo escenario.",
        "- Las etiquetas superiores `N2O` y `NH3` son guías visuales ubicadas sobre regiones donde el diagnóstico contrafactual muestra picos relevantes; no son un ajuste espectroscópico independiente.",
        "",
        "La figura se generó con el entorno Ubuntu/Conda `POSEIDON` desde `Transmission_Spectroscopy/notebooks/`, usando las variables de datos externas `POSEIDON_input_data` y `PYSYN_CDBS` apuntando a los directorios locales de opacidades y grillas estelares.",
        "",
        "## Validación del reemplazo químico",
        "",
        "Para evitar que la señal molecular fuera un artefacto de indexación, el script escribe primero perfiles químicos contrafactuales y luego los vuelve a leer con `read_chem_file`. La tabla `trappist1e_counterfactual_chemistry_validation.csv` registra, para cada combinación `(escenario, molécula)`, la columna reemplazada y varios errores máximos absolutos.",
        "",
        "- `loaded_replaced_species_max_abs_error = 0.0` verifica que la especie reemplazada cargada desde disco coincide exactamente con el perfil `A0`.",
        "- `loaded_other_species_max_abs_error = 0.0` verifica que las demás especies explícitas coinciden con el escenario objetivo.",
        "- `loaded_total_max_abs_error = 0.0` verifica que el archivo contrafactual completo cargado por POSEIDON coincide con la composición esperada.",
        "- `source_species_shift_max_abs` no es un error; mide cuánto difería la molécula entre el escenario objetivo y `A0` antes del reemplazo.",
        "",
        "## Regla de picos",
        "",
        f"- Se usa la curva residual rebineada que se grafica en la figura final.",
            "- Se definen ventanas espectrales por molécula y se reporta el máximo de `|signal|` dentro de cada ventana.",
            "- Esto evita que un pico global fuera de la región interpretativa domine el resumen de una molécula.",
            "- Se reporta la señal molecular con signo, su valor absoluto, el identificador de ventana y los límites usados.",
        "",
        "## Estimación de S/N instrumental",
        "",
        "Se añadió una estimación simple de S/N usando los archivos planos de ruido de `1` tránsito en `synthetic_data/base_1transit/`. Los archivos planos almacenan `depth` y `depth_err` como profundidad de tránsito adimensional, es decir `(R_p/R_s)^2`. Para comparar con la figura, tanto la señal molecular como el ruido se expresan en ppm de `(R_p/R_s)^2`: `signal_ppm = signal_(Rp/Rs)^2 * 1e6` y `sigma_1transit_ppm = depth_err * 1e6`. Por tanto, el S/N exportado es adimensional.",
        "",
        "Para cada pico se toma el punto instrumental más cercano dentro de la cobertura de `NIRSpec_PRISM` o `MIRI_LRS`. La incertidumbre se escala como `sigma_N = sigma_1 / sqrt(N)` para `N = 1, 10, 100` tránsitos, y el cociente reportado es `S/N_N = |signal_ppm| / sigma_N`.",
        "",
        "Los picos fuera de la cobertura `0.6-12 μm` de esta combinación NIRSpec Prism + MIRI LRS se marcan como `outside_coverage` y no reciben S/N.",
        "",
        "## Resumen de picos",
        "",
    ]

    for scenario_key in COUNTERFACTUAL_SCENARIO_KEYS:
        lines.append(f"### {scenario_key}")
        lines.append("")
        for species in MOLECULAR_DELTA_SPECIES:
            lines.append(f"#### {species}")
            lines.append("")
            lines.append("| Ventana | Rango (μm) | Pico (μm) | Signal (ppm) | |Signal| (ppm) | Instrumento | σ 1 tránsito (ppm) | S/N 1 | S/N 10 | S/N 100 |")
            lines.append("| :--- | :--- | ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: |")
            for row in grouped[(scenario_key, species)]:
                sigma = "" if not np.isfinite(row["sigma_1transit_ppm"]) else f"{row['sigma_1transit_ppm']:.2f}"
                snr_1 = "" if not np.isfinite(row["snr_1transit"]) else f"{row['snr_1transit']:.3f}"
                snr_10 = "" if not np.isfinite(row["snr_10transit"]) else f"{row['snr_10transit']:.3f}"
                snr_100 = "" if not np.isfinite(row["snr_100transit"]) else f"{row['snr_100transit']:.3f}"
                lines.append(
                    f"| {row['band_id']} | {row['window_min_micron']:.2f}-{row['window_max_micron']:.2f} | {row['wavelength_micron']:.3f} | {row['signal_ppm']:.3f} | {row['absolute_signal_ppm']:.3f} | {row['noise_instrument']} | {sigma} | {snr_1} | {snr_10} | {snr_100} |"
                )
            lines.append("")

    lines.extend(
        [
            "## Archivos conservados",
            "",
            f"- Figura principal v2: `Transmission_Spectroscopy/notebooks/POSEIDON_output/pure_spectra/plots/trappist1e_pure_a0_molecular_residuals_v2.png`",
            f"- Figura principal v2 PDF: `Transmission_Spectroscopy/notebooks/POSEIDON_output/pure_spectra/plots/trappist1e_pure_a0_molecular_residuals_v2.pdf`",
            f"- Tabla CSV: `Transmission_Spectroscopy/notebooks/POSEIDON_output/pure_spectra/plots/{PEAK_SUMMARY_CSV.name}`",
            "",
            "## Archivos regenerables de auditoría",
            "",
            "El script puede volver a escribir los perfiles contrafactuales y la tabla de validación química cuando se ejecuta de nuevo. Estos productos no se conservan como artefactos finales porque son derivados exactos de los perfiles fuente y del código:",
            "",
            f"- Validación química regenerable: `Transmission_Spectroscopy/notebooks/POSEIDON_output/pure_spectra/plots/{COUNTERFACTUAL_VALIDATION_CSV.name}`",
            f"- Perfiles contrafactuales regenerables: `Transmission_Spectroscopy/profiles/counterfactual_A0_replacements/*_reset_<mol>_to_A0_chem.txt`",
            f"- Figura legacy regenerable con `--include-legacy-v1`: `Transmission_Spectroscopy/notebooks/POSEIDON_output/pure_spectra/plots/trappist1e_pure_a0_difference_mountains.{{png,pdf}}`",
        ]
    )
    PEAK_SUMMARY_NOTE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_counterfactual_products(system_key, products):
    if system_key != "TRAPPIST-1e":
        return None, []

    counterfactual_paths, validation_rows = make_counterfactual_chemistry_files(
        system_key,
        MOLECULAR_DELTA_SPECIES,
        COUNTERFACTUAL_SCENARIO_KEYS,
    )
    counterfactual_spectra = compute_counterfactual_spectra(
        products,
        MOLECULAR_DELTA_SPECIES,
        COUNTERFACTUAL_SCENARIO_KEYS,
        counterfactual_paths,
        validation_rows,
    )
    return counterfactual_spectra, validation_rows


def plot_legacy_molecular_delta_grid(system_key, products, counterfactual_spectra, wl_min, wl_max, n_bins):
    """Render the superseded five-panel layout for audit comparisons only."""

    if system_key != "TRAPPIST-1e":
        return

    wl = products["wl"]
    spectra = products["spectra"]
    fig, axes = plt.subplots(
        5,
        1,
        figsize=(13.6, 12.8),
        sharex=True,
        constrained_layout=True,
        gridspec_kw={"height_ratios": [3.7, 1.45, 0.95, 0.95, 0.95]},
    )
    ax_top = axes[0]
    ax_global_delta = axes[1]
    species_axes = dict(zip(MOLECULAR_DELTA_SPECIES, axes[2:]))

    rebinned_total = {}
    for scenario_key in SCENARIO_KEYS:
        wl_b, y_b = rebin_curve(wl, spectra[scenario_key] * 1.0e6, wl_min, wl_max, n_bins)
        rebinned_total[scenario_key] = y_b

    line_styles = {
        "A3": {"lw": 1.7, "zorder": 7},
        "A2": {"lw": 1.8, "zorder": 8},
        "A1": {"lw": 1.95, "zorder": 9},
    }
    for scenario_key in SCENARIO_FILL_ORDER:
        colour = SCENARIO_COLOURS[scenario_key]
        ax_top.fill_between(
            wl_b,
            rebinned_total["A0"],
            rebinned_total[scenario_key],
            color=colour,
            alpha=1.0,
            zorder=1 + ("A3", "A2", "A1").index(scenario_key),
        )
        ax_top.plot(
            wl_b,
            rebinned_total[scenario_key],
            color=colour,
            alpha=0.92,
            label=f"{scenario_key}: {SCENARIO_NAMES[scenario_key]}",
            **line_styles[scenario_key],
        )

    ax_top.plot(
        wl_b,
        rebinned_total["A0"],
        color=SCENARIO_COLOURS["A0"],
        lw=1.15,
        alpha=0.98,
        linestyle="-",
        label="A0: Pre-agricultural scenario",
        zorder=12,
    )
    style_axis(ax_top, wl_min, wl_max)
    ax_top.set_title(
        "ExoFarm transmission spectra\nand residuals relative to the pre-agricultural scenario",
        fontfamily="serif",
        loc="left",
        fontsize=22,
        color="black",
    )
    ax_top.legend(frameon=False, fontsize=14, ncol=2, loc="upper left")

    top_arrays = [rebinned_total[key] for key in SCENARIO_KEYS]
    top_min = min(np.nanmin(values) for values in top_arrays)
    top_max = max(np.nanmax(values) for values in top_arrays)
    top_span = top_max - top_min
    top_pad = max(14.0, 0.10 * (top_max - top_min))
    annotate_instrument_coverage(
        ax_top,
        y_base=top_min - 0.73 * top_pad,
        y_step=0.22 * top_pad,
    )
    ax_top.set_ylim(top_min - top_pad, top_max + top_pad)

    global_delta_arrays = []
    for scenario_key in ("A3", "A2", "A1"):
        delta = rebinned_total[scenario_key] - rebinned_total["A0"]
        global_delta_arrays.append(delta)
        ax_global_delta.fill_between(
            wl_b,
            0.0,
            delta,
            color=SCENARIO_COLOURS[scenario_key],
            alpha=0.72 if scenario_key == "A3" else 0.82 if scenario_key == "A2" else 0.92,
            lw=0,
            zorder=2 + ("A3", "A2", "A1").index(scenario_key),
        )
        ax_global_delta.plot(
            wl_b,
            delta,
            color=SCENARIO_COLOURS[scenario_key],
            lw=1.0 if scenario_key == "A3" else 1.9 if scenario_key == "A2" else 2.2,
            alpha=0.72 if scenario_key == "A3" else 0.96,
            label=f"{scenario_key} - A0",
            zorder=5 + ("A3", "A2", "A1").index(scenario_key),
        )

    style_delta_axis(ax_global_delta, wl_min, wl_max)
    ax_global_delta.axhline(
        0.0,
        color=PALETTE["ink_black"],
        lw=0.95,
        linestyle=":",
        alpha=0.82,
        zorder=12,
    )
    ax_global_delta.set_ylabel(r"$\Delta (R_p/R_s)^2$" "\n(ppm)", fontfamily="serif", fontsize=15, color="black")
    ax_global_delta.text(
        0.015,
        0.85,
        "Residual with pre-agricultural scenario",
        transform=ax_global_delta.transAxes,
        color=PALETTE["ink_black"],
        fontsize=15,
        fontfamily="serif",
        ha="left",
        va="top",
    )
    ax_global_delta.legend(frameon=False, fontsize=12, ncol=3, loc="lower left")

    global_delta_min = min(np.nanmin(values) for values in global_delta_arrays)
    global_delta_max = max(np.nanmax(values) for values in global_delta_arrays)
    global_delta_pad = max(3.0, 0.12 * (global_delta_max - global_delta_min))
    ax_global_delta.set_ylim(
        min(-global_delta_pad, global_delta_min - global_delta_pad),
        global_delta_max + global_delta_pad,
    )

    peak_summary_rows = []
    for species in MOLECULAR_DELTA_SPECIES:
        ax = species_axes[species]
        species_colour = MOLECULAR_LABEL_COLOURS[species]
        delta_arrays = []

        for scenario_key in ("A3", "A2", "A1"):
            _, full_binned = rebin_curve(wl, spectra[scenario_key] * 1.0e6, wl_min, wl_max, n_bins)
            _, reset_binned = rebin_curve(
                wl,
                counterfactual_spectra[species][scenario_key] * 1.0e6,
                wl_min,
                wl_max,
                n_bins,
            )
            delta = full_binned - reset_binned
            delta_arrays.append(delta)
            ax.fill_between(
                wl_b,
                0.0,
                delta,
                color=SCENARIO_COLOURS[scenario_key],
                alpha=0.72 if scenario_key == "A3" else 0.82 if scenario_key == "A2" else 0.92,
                lw=0,
                zorder=scenario_delta_zorder(scenario_key) - 2,
            )
            ax.plot(
                wl_b,
                delta,
                color=SCENARIO_COLOURS[scenario_key],
                lw=scenario_delta_linewidth(scenario_key),
                alpha=0.72 if scenario_key == "A3" else 0.96,
                label=f"{scenario_key} - A0",
                zorder=scenario_delta_zorder(scenario_key),
            )
            for peak_row in detect_window_signal_peaks(
                wl_b,
                delta,
                MOLECULAR_SIGNAL_WINDOWS[species],
            ):
                peak_summary_rows.append(
                    {
                        "scenario": scenario_key,
                        "molecule": species,
                        **peak_row,
                    }
                )

        style_delta_axis(ax, wl_min, wl_max)
        ax.axhline(0.0, color=PALETTE["ink_black"], lw=0.95, linestyle=":", alpha=0.82, zorder=12)
        ax.set_ylabel(r"$\Delta (R_p/R_s)^2$" "\n(ppm)", fontfamily="serif", fontsize=13, color="black")
        ax.text(
            0.015,
            0.84,
            f"{MOLECULE_LABELS[species]} molecular signal",
            transform=ax.transAxes,
            color="black",
            fontsize=13,
            fontfamily="serif",
            ha="left",
            va="top",
        )

        delta_min = min(np.nanmin(values) for values in delta_arrays)
        delta_max = max(np.nanmax(values) for values in delta_arrays)
        delta_pad = max(2.0, 0.14 * (delta_max - delta_min))
        ax.set_ylim(
            min(-delta_pad, delta_min - delta_pad),
            delta_max + delta_pad,
        )

    axes[-1].set_xlabel("Wavelength (μm)", fontfamily="serif", fontsize=17, color="black")

    stem = "trappist1e_pure_a0_difference_mountains"
    png_path = PLOTS_DIR / f"{stem}.png"
    pdf_path = PLOTS_DIR / f"{stem}.pdf"
    fig.savefig(png_path, dpi=240)
    fig.savefig(pdf_path)
    print(f"Saved {png_path}")
    print(f"Saved {pdf_path}")


def summarize_molecular_signal_peaks(products, counterfactual_spectra, wl_min, wl_max, n_bins):
    """Return peak rows for the same molecular-signal curves shown in v2."""

    wl = products["wl"]
    spectra = products["spectra"]
    peak_summary_rows = []

    for species in MOLECULAR_DELTA_SPECIES:
        for scenario_key in ("A3", "A2", "A1"):
            wl_b, full_binned = rebin_curve(
                wl,
                spectra[scenario_key] * 1.0e6,
                wl_min,
                wl_max,
                n_bins,
            )
            _, reset_binned = rebin_curve(
                wl,
                counterfactual_spectra[species][scenario_key] * 1.0e6,
                wl_min,
                wl_max,
                n_bins,
            )
            delta = full_binned - reset_binned
            for peak_row in detect_window_signal_peaks(
                wl_b,
                delta,
                MOLECULAR_SIGNAL_WINDOWS[species],
            ):
                peak_summary_rows.append(
                    {
                        "scenario": scenario_key,
                        "molecule": species,
                        **peak_row,
                    }
                )

    return peak_summary_rows


def plot_molecular_delta_grid_v2(system_key, products, counterfactual_spectra, wl_min, wl_max, n_bins):
    if system_key != "TRAPPIST-1e":
        return

    wl = products["wl"]
    spectra = products["spectra"]
    fig, axes = plt.subplots(
        4,
        1,
        figsize=(13.8, 11.2),
        sharex=True,
        constrained_layout=True,
        gridspec_kw={"height_ratios": [2.85, 1.0, 1.0, 1.0]},
    )
    ax_top = axes[0]
    species_axes = dict(zip(MOLECULAR_DELTA_SPECIES, axes[1:]))

    rebinned_total = {}
    for scenario_key in SCENARIO_KEYS:
        wl_b, y_b = rebin_curve(wl, spectra[scenario_key] * 1.0e6, wl_min, wl_max, n_bins)
        rebinned_total[scenario_key] = y_b

    for scenario_key in ("A3", "A2", "A1"):
        colour = SCENARIO_COLOURS[scenario_key]
        ax_top.fill_between(
            wl_b,
            rebinned_total["A0"],
            rebinned_total[scenario_key],
            color=colour,
            alpha=1.0,
            zorder=1 + ("A3", "A2", "A1").index(scenario_key),
        )
        ax_top.plot(
            wl_b,
            rebinned_total[scenario_key],
            color=colour,
            alpha=0.92,
            lw=1.7 if scenario_key == "A3" else 1.9 if scenario_key == "A2" else 2.1,
            label=f"{scenario_key}: {SCENARIO_NAMES[scenario_key]}",
            zorder=6 + ("A3", "A2", "A1").index(scenario_key),
        )

    ax_top.plot(
        wl_b,
        rebinned_total["A0"],
        color=SCENARIO_COLOURS["A0"],
        lw=1.15,
        alpha=0.98,
        linestyle="-",
        label="A0: Pre-agricultural scenario",
        zorder=12,
    )
    style_axis(ax_top, wl_min, wl_max)
    ax_top.set_title(
        "ExoFarm transmission spectra\nand molecular residuals",
        fontfamily="serif",
        loc="center",
        fontsize=22,
        color="black",
    )
    annotate_top_molecular_regions(ax_top, wl_b, rebinned_total)
    ax_top.legend(frameon=False, fontsize=13, ncol=2, loc="upper left")
    top_arrays = [rebinned_total[key] for key in SCENARIO_KEYS]
    top_min = min(np.nanmin(values) for values in top_arrays)
    top_max = max(np.nanmax(values) for values in top_arrays)
    top_span = top_max - top_min
    top_pad = max(14.0, 0.10 * top_span)
    annotate_instrument_coverage(
        ax_top,
        y_base=top_min - 0.82 * top_pad,
        y_step=0.18 * top_pad,
    )
    ax_top.set_ylim(top_min - top_pad, top_max + top_pad)

    global_delta_by_scenario = {
        scenario_key: rebinned_total[scenario_key] - rebinned_total["A0"]
        for scenario_key in COUNTERFACTUAL_SCENARIO_KEYS
    }

    for species in MOLECULAR_DELTA_SPECIES:
        ax = species_axes[species]
        delta_arrays = []
        for scenario_key in ("A3", "A2", "A1"):
            _, full_binned = rebin_curve(wl, spectra[scenario_key] * 1.0e6, wl_min, wl_max, n_bins)
            _, reset_binned = rebin_curve(
                wl,
                counterfactual_spectra[species][scenario_key] * 1.0e6,
                wl_min,
                wl_max,
                n_bins,
            )
            delta = full_binned - reset_binned
            delta_arrays.append(delta)
            colour = SCENARIO_COLOURS[scenario_key]
            ax.fill_between(
                wl_b,
                0.0,
                delta,
                color=colour,
                alpha=0.72 if scenario_key == "A3" else 0.82 if scenario_key == "A2" else 0.92,
                lw=0,
                zorder=scenario_delta_zorder(scenario_key) - 2,
            )
            ax.plot(
                wl_b,
                delta,
                color=colour,
                lw=scenario_delta_linewidth(scenario_key),
                alpha=0.98,
                label=f"{scenario_key} - A0",
                zorder=scenario_delta_zorder(scenario_key),
            )

        for scenario_key in ("A3", "A2", "A1"):
            ax.plot(
                wl_b,
                global_delta_by_scenario[scenario_key],
                color=RESIDUAL_DARK_COLOURS[scenario_key],
                lw=1.05,
                alpha=0.58 if scenario_key == "A3" else 0.68,
                linestyle="-",
                zorder=1,
            )

        style_delta_axis(ax, wl_min, wl_max)
        ax.axhline(0.0, color=PALETTE["ink_black"], lw=0.95, linestyle=":", alpha=0.82, zorder=12)
        ax.set_ylabel(r"$\Delta (R_p/R_s)^2$" "\n(ppm)", fontfamily="serif", fontsize=13, color="black")
        ax.text(
            0.015,
            0.84,
            f"{MOLECULE_LABELS[species]} signal",
            transform=ax.transAxes,
            color="black",
            fontsize=13,
            fontfamily="serif",
            ha="left",
            va="top",
        )

        combined_arrays = delta_arrays + list(global_delta_by_scenario.values())
        delta_min = min(np.nanmin(values) for values in combined_arrays)
        delta_max = max(np.nanmax(values) for values in combined_arrays)
        delta_pad = max(1.5, 0.14 * (delta_max - delta_min))
        ax.set_ylim(
            min(-delta_pad, delta_min - delta_pad),
            delta_max + delta_pad,
        )

        if species == MOLECULAR_DELTA_SPECIES[0]:
            legend_handles = []
            for scenario_key in ("A3", "A2", "A1"):
                legend_handles.append(
                    Line2D(
                        [0],
                        [0],
                        color=SCENARIO_COLOURS[scenario_key],
                        lw=2.2,
                        label=f"{scenario_key} mol signal",
                    )
                )
                legend_handles.append(
                    Line2D(
                        [0],
                        [0],
                        color=RESIDUAL_DARK_COLOURS[scenario_key],
                        lw=1.4,
                        linestyle="-",
                        label=f"{scenario_key}-A0 total",
                    )
                )
            ax.legend(
                handles=legend_handles,
                frameon=False,
                fontsize=9.5,
                ncol=3,
                loc="lower left",
            )

    axes[-1].set_xlabel("Wavelength (μm)", fontfamily="serif", fontsize=17, color="black")

    stem = "trappist1e_pure_a0_molecular_residuals_v2"
    png_path = PLOTS_DIR / f"{stem}.png"
    pdf_path = PLOTS_DIR / f"{stem}.pdf"
    fig.savefig(png_path, dpi=240)
    fig.savefig(pdf_path)
    print(f"Saved {png_path}")
    print(f"Saved {pdf_path}")


def main():
    args = parse_args()
    trappist_products = build_system_products("TRAPPIST-1e", args.wl_min, args.wl_max, args.native_r)
    counterfactual_spectra, validation_rows = build_counterfactual_products(
        "TRAPPIST-1e",
        trappist_products,
    )
    peak_summary_rows = summarize_molecular_signal_peaks(
        trappist_products,
        counterfactual_spectra,
        args.wl_min,
        args.wl_max,
        args.n_bins,
    )
    export_peak_summary_csv(peak_summary_rows)
    export_counterfactual_validation_csv(validation_rows)
    export_peak_summary_note(peak_summary_rows)

    plot_molecular_delta_grid_v2(
        "TRAPPIST-1e",
        trappist_products,
        counterfactual_spectra,
        args.wl_min,
        args.wl_max,
        args.n_bins,
    )
    if args.include_legacy_v1:
        plot_legacy_molecular_delta_grid(
            "TRAPPIST-1e",
            trappist_products,
            counterfactual_spectra,
            args.wl_min,
            args.wl_max,
            args.n_bins,
        )


if __name__ == "__main__":
    main()
