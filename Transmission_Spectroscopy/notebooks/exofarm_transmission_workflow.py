from pathlib import Path
import shutil

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

from POSEIDON.contributions import spectral_contribution
from POSEIDON.constants import M_E, R_E, R_Sun
from POSEIDON.core import (
    compute_spectrum,
    create_planet,
    create_star,
    define_model,
    load_data,
    make_atmosphere,
    read_opacities,
    wl_grid_constant_R,
)
from POSEIDON.instrument import generate_syn_data_from_file
from POSEIDON.utility import bin_spectrum, read_chem_file, read_PT_file


# This module keeps the notebook light.  The numerical work stays here so the
# notebook can focus on the scientific narrative: A0 -> A1 -> A2 -> A3, then
# synthetic JWST observations.  The comments emphasize units, grid choices, and
# assumptions because those are the places where scientific workflows usually
# become ambiguous.

# Resolve paths from this file instead of the active notebook directory.  That
# makes the workflow robust to launching Jupyter from the repo root or from
# Transmission_Spectroscopy/notebooks.
NOTEBOOK_DIR = Path(__file__).resolve().parent
PROFILES_DIR = NOTEBOOK_DIR.parent / "profiles"
POSEIDON_OUTPUT_DIR = NOTEBOOK_DIR / "POSEIDON_output" / "TRAPPIST-1e"
SYNTHETIC_DATA_DIR = POSEIDON_OUTPUT_DIR / "synthetic_data" / "base_1transit"

PLANET_NAME = "TRAPPIST-1e"

# Scenario metadata is the single source of truth for labels, colours, and
# profile filenames.  Adding/removing a scenario should normally happen here
# rather than inside the notebook cells.
SCENARIOS = {
    "A0": {
        "label": "Trappist_A0_PreAgri",
        "name": "Pre-agricultural",
        "colour": "darkgreen",
    },
    "A1": {
        "label": "Trappist_A1_Current",
        "name": "Current Earth",
        "colour": "royalblue",
    },
    "A2": {
        "label": "Trappist_A2_Moderate",
        "name": "Moderate ExoFarm",
        "colour": "goldenrod",
    },
    "A3": {
        "label": "Trappist_A3_Extreme",
        "name": "Extreme ExoFarm",
        "colour": "darkred",
    },
}

# Observation plan used for the final synthetic datasets.  Each number means
# N NIRSpec Prism transits and N MIRI LRS transits.
OBSERVATION_TRANSIT_COUNTS = [5, 10, 20]
INSTRUMENTS = ["JWST_NIRSpec_PRISM", "JWST_MIRI_LRS"]

# R_TO_BIN is passed to POSEIDON's synthetic-data generator.  Keep the list in
# the same order as INSTRUMENTS.
R_TO_BIN = [100, 100]
DEFAULT_PLOT_R = 100

# Visual encodings for observation-count comparisons.  These are deliberately
# independent from scenario colours, so a "by scenario" plot can use colour and
# marker shape to compare 5, 10, and 20 transit pairs.
TRANSIT_COUNT_STYLES = {
    5: {"colour": "tab:purple", "marker": "o", "label": "5 + 5"},
    10: {"colour": "tab:blue", "marker": "s", "label": "10 + 10"},
    20: {"colour": "tab:green", "marker": "^", "label": "20 + 20"},
}

# Visual encodings for scenario comparisons at fixed noise level.
SCENARIO_MARKERS = {
    "A0": "o",
    "A1": "s",
    "A2": "^",
    "A3": "D",
}

CONTRIBUTION_SPECIES = ["N2O", "NH3", "CH4", "O3"]
CONTRIBUTION_COLOURS = {
    "Total": "0.15",
    "N2O": "#1f77b4",
    "NH3": "#ff7f0e",
    "CH4": "#9467bd",
    "O3": "#17becf",
}

# Windows used to summarize the growth of visually prominent diagnostic peaks
# relative to A0.  They are intentionally explicit so the notebook can adjust
# them if a different feature definition is needed later.
DEFAULT_PEAK_WINDOWS = (
    {"species": "N2O", "label": "Banda N$_2$O 1", "wl_min": 2.7, "wl_max": 3.2},
    {"species": "N2O", "label": "Banda N$_2$O 2", "wl_min": 7.5, "wl_max": 8.5},
    {"species": "NH3", "label": "Banda NH$_3$", "wl_min": 10.0, "wl_max": 11.2},
)

# N2 is the bulk species; the remaining species are treated explicitly because
# they drive the spectral comparison and the technosignature interpretation.
BULK_SPECIES = ["N2"]
PARAM_SPECIES = ["H2O", "CO2", "CH4", "O2", "O3", "N2O", "NH3"]

# Column order in the VULCAN chemistry profile files.  POSEIDON selects only
# the subset requested by each model through chem_species_in_model, so this list
# must stay synchronized with the profile export format.
CHEM_SPECIES_FILE = [
    "OH", "H2", "H2O", "H", "O", "CH", "C", "CH2", "CH3", "CH4",
    "C2", "C2H2", "C2H", "C2H3", "C2H4", "C2H5", "C2H6",
    "CO", "CO2", "CH2OH", "H2CO", "HCO", "CH3O", "CH3OH", "CH3CO",
    "O2", "H2CCO", "HCCO", "CH3O2", "HO2", "CH3OOH",
    "N", "NH", "CN", "HCN", "NH2", "N2", "NH3", "NO",
    "N2H2", "N2H", "N2H3", "N2H4", "HNO", "H2CN", "HNCO", "NO2", "N2O",
    "C4H2", "CH2NH2", "CH2NH", "CH3NH2", "CH3CHO",
    "O3", "NO3", "HNO3", "HNO2", "NCO", "N2O5",
    "S", "SH", "S2", "SO", "H2S", "CS", "COS", "CS2", "NS", "HS2", "SO2",
    "S4", "S8", "HCS", "S3", "H2O2", "SO3", "HSO3", "HSO", "H2SO4",
    "HC3N", "CH3CN", "CH2CN", "C2H3CN", "CH3SH", "CH3S",
    "C3H3", "C3H2", "C3H4", "C6H5", "C6H6", "C4H3", "C4H5",
    "S2O", "O_1", "CH2_1", "N_2D", "He", "H2O_l_s", "H2SO4_l",
]


def create_trappist_system():
    """Create POSEIDON star and planet objects for the TRAPPIST-1e setup."""
    star = create_star(
        0.11697 * R_Sun,
        2559.0,
        5.21,
        0.04,
        stellar_grid="phoenix",
    )

    planet = create_planet(
        PLANET_NAME,
        0.917985 * R_E,
        mass=0.6356 * M_E,
        T_eq=255.0,
    )

    return star, planet


def create_pressure_grid(P_min=1.0e-10, P_max=10.0, n_layers=100):
    """
    Create the pressure grid used by all scenarios.

    Pressures are in bar.  A log-spaced grid is used because transmission
    spectra are sensitive over many atmospheric scale heights; uniform spacing
    would waste resolution near the lower boundary.
    """
    P = np.logspace(np.log10(P_max), np.log10(P_min), n_layers)

    # The surface is treated as an opaque lower boundary at 1 bar.  The
    # reference radius is anchored at the same pressure to keep scenarios
    # directly comparable.
    P_surf = 1.0
    P_ref = P_surf
    R_p_ref = 0.917985 * R_E

    return P, P_surf, P_ref, R_p_ref


def define_forward_models(scenario_keys):
    """Define one file-read POSEIDON forward model per requested scenario."""
    models = {}

    for scenario_key in scenario_keys:
        scenario = SCENARIOS[scenario_key]
        models[scenario_key] = define_model(
            scenario["label"],
            BULK_SPECIES,
            PARAM_SPECIES,
            # Both temperature and composition come from exported profile files.
            # That keeps the spectroscopy conditional on the photochemical run.
            PT_profile="file_read",
            X_profile="file_read",
            radius_unit="R_E",
            surface=True,
        )

    return models


def load_profiles(models, P, scenario_keys):
    """
    Read PT and chemistry profiles and interpolate them onto the POSEIDON grid.

    read_PT_file/read_chem_file handle the interpolation internally.  Keeping a
    common pressure grid here avoids comparing spectra generated on slightly
    different vertical grids.
    """
    temperatures = {}
    compositions = {}

    for scenario_key in scenario_keys:
        label = SCENARIOS[scenario_key]["label"]

        temperatures[scenario_key] = read_PT_file(
            str(PROFILES_DIR),
            f"{label}_PT.txt",
            P,
            skiprows=1,
            # The profile files store altitude/radius-like information before
            # pressure and temperature; these are the POSEIDON column indices.
            P_column=2,
            T_column=3,
        )

        compositions[scenario_key] = read_chem_file(
            str(PROFILES_DIR),
            f"{label}_chem.txt",
            P,
            CHEM_SPECIES_FILE,
            chem_species_in_model=models[scenario_key]["chemical_species"],
            skiprows=1,
        )

    return temperatures, compositions


def make_atmospheres(planet, models, P, P_ref, R_p_ref, P_surf, temperatures, compositions):
    """Build POSEIDON atmosphere dictionaries from the loaded profile arrays."""
    atmospheres = {}

    for scenario_key, model in models.items():
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

    return atmospheres


def make_wavelength_grid_and_opacities(reference_model, wl_min=0.5, wl_max=14.0, R=10000):
    """
    Create the wavelength grid and read opacity tables.

    The wavelength range covers NIRSpec Prism and MIRI LRS together.  R=10000 is
    intentionally higher than the plotted/synthetic resolution so binning does
    not imprint the model grid onto the instrument products.
    """
    wl = wl_grid_constant_R(wl_min, wl_max, R)

    # Opacity tables are sampled on regular T/logP grids.  The chosen ranges
    # bracket the TRAPPIST-1e atmospheric profiles while avoiding unnecessary
    # memory use.
    T_fine = np.arange(100.0, 400.0 + 10.0, 10.0)
    log_P_fine = np.arange(-10.0, 0.0 + 0.2, 0.2)

    opac = read_opacities(
        reference_model,
        wl,
        "opacity_sampling",
        T_fine,
        log_P_fine,
        opacity_database="High-T",
    )

    return wl, opac


def compute_forward_spectra(planet, star, models, atmospheres, opac, wl):
    """Compute the native forward transmission spectrum for each scenario."""
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

    return spectra


def compute_spectral_contributions(
    planet,
    star,
    models,
    atmospheres,
    opac,
    wl,
    scenario_keys=("A0", "A3"),
    contribution_species=CONTRIBUTION_SPECIES,
):
    """
    Compute selected molecular spectral contributions for chosen scenarios.

    The contribution calculation is intentionally kept separate from
    compute_forward_spectra(...), because it is more diagnostic and can be
    skipped when the notebook only needs total spectra or synthetic data.
    """
    contributions = {}

    for scenario_key in scenario_keys:
        total, names, component_list = spectral_contribution(
            planet,
            star,
            models[scenario_key],
            atmospheres[scenario_key],
            opac,
            wl,
            contribution_species_list=list(contribution_species),
            bulk_species=False,
            cloud_contribution=False,
        )

        contributions[scenario_key] = {
            "total": total,
            "names": list(names),
            "components": {
                name: component for name, component in zip(names, component_list)
            },
        }

    return contributions


def prepare_pandexo_base_data(wl):
    """
    Load the 1-transit PandExo templates used by POSEIDON.

    These files carry the wavelength sampling and uncertainty structure for
    NIRSpec Prism and MIRI LRS.  They are copied into the common synthetic-data
    directory because POSEIDON load_data expects all datasets for a run to live
    side by side.
    """
    prism_src = POSEIDON_OUTPUT_DIR / "pandexo_nirspec_prism_flat" / (
        "TRAPPIST-1e_flat_NIRSpec_Prism_1_transits.dat"
    )
    miri_src = POSEIDON_OUTPUT_DIR / "pandexo_miri_lrs_flat" / (
        "TRAPPIST-1e_flat_MIRI_LRS_1_transits.dat"
    )

    if not prism_src.exists():
        raise FileNotFoundError(f"No encontre {prism_src}")

    if not miri_src.exists():
        raise FileNotFoundError(f"No encontre {miri_src}")

    SYNTHETIC_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Copy only when needed; this keeps the workflow idempotent and avoids
    # touching timestamps unnecessarily when the notebook is re-run.
    for src in (prism_src, miri_src):
        dst = SYNTHETIC_DATA_DIR / src.name
        if src.resolve() != dst.resolve():
            shutil.copy2(src, dst)

    datasets_base = [
        "TRAPPIST-1e_flat_NIRSpec_Prism_1_transits.dat",
        "TRAPPIST-1e_flat_MIRI_LRS_1_transits.dat",
    ]

    data_base = load_data(
        str(SYNTHETIC_DATA_DIR),
        datasets_base,
        INSTRUMENTS,
        wl,
        skiprows=1,
        # POSEIDON expects microns and transit depth units matching the .dat
        # products written by the earlier PandExo notebook.
        wl_unit="micron",
        bin_width="half",
        spectrum_unit="(Rp/Rs)^2",
    )

    return data_base, datasets_base


def synthetic_dataset_names(scenario_key, n_nirspec, n_miri):
    """Return POSEIDON-compatible synthetic dataset filenames."""
    label = SCENARIOS[scenario_key]["label"]

    return [
        f"{PLANET_NAME}_SYNTHETIC_JWST_NIRSpec_PRISM_{label}_N_trans_{n_nirspec}.dat",
        f"{PLANET_NAME}_SYNTHETIC_JWST_MIRI_LRS_{label}_N_trans_{n_miri}.dat",
    ]


def read_poseidon_dat(path):
    """
    Read a POSEIDON-compatible .dat file.

    Expected columns are wavelength, wavelength_err, transit depth, and
    depth_err.  Wavelengths are in microns and transit depths are in (Rp/Rs)^2.
    The returned names make the units explicit for later plotting.
    """
    data = np.loadtxt(path, skiprows=1)

    if data.ndim != 2 or data.shape[1] < 4:
        raise ValueError(f"Formato inesperado en {path}")

    return {
        "wavelength": data[:, 0],
        "wavelength_err": data[:, 1],
        "depth": data[:, 2],
        "depth_err": data[:, 3],
    }


def load_synthetic_observation(scenario_key, n_obs):
    """
    Load the paired NIRSpec/MIRI synthetic observation for one scenario.

    n_obs is used for both instruments in the current observing plan.  The two
    instrument arrays are kept separate so marker/colour decisions can be made
    at the plotting layer if needed.
    """
    datasets = synthetic_dataset_names(scenario_key, n_obs, n_obs)
    paths = [SYNTHETIC_DATA_DIR / dataset for dataset in datasets]
    missing = [str(path) for path in paths if not path.exists()]

    if missing:
        raise FileNotFoundError(
            "Faltan observaciones sintéticas. Corre primero la celda de "
            "generación:\n" + "\n".join(missing)
        )

    return {
        "scenario_key": scenario_key,
        "n_obs": n_obs,
        "datasets": datasets,
        "nirspec": read_poseidon_dat(paths[0]),
        "miri": read_poseidon_dat(paths[1]),
    }


def generate_synthetic_observation(
    planet,
    wl,
    spectrum,
    data_base,
    scenario_key,
    n_nirspec,
    n_miri,
    gauss_scatter=True,
):
    """
    Generate and load one paired NIRSpec/MIRI synthetic observation.

    n_nirspec and n_miri are kept as separate arguments even though the current
    grid uses equal values.  This makes asymmetric observing plans explicit if
    they are introduced later.
    """
    n_trans = [n_nirspec, n_miri]
    label = SCENARIOS[scenario_key]["label"]

    generate_syn_data_from_file(
        planet,
        wl,
        spectrum,
        str(SYNTHETIC_DATA_DIR),
        data_base,
        R_to_bin=R_TO_BIN,
        N_trans=n_trans,
        label=label,
        # Gaussian scatter gives one noisy realization around the forward model.
        # Set gauss_scatter=False for deterministic, noise-free planning runs.
        Gauss_scatter=gauss_scatter,
    )

    datasets = synthetic_dataset_names(scenario_key, n_nirspec, n_miri)

    # Fail loudly if POSEIDON changes a filename convention or the write fails.
    # Silent missing files are painful later when retrieval/plotting cells load
    # stale products from a previous run.
    missing = [
        str(SYNTHETIC_DATA_DIR / dataset)
        for dataset in datasets
        if not (SYNTHETIC_DATA_DIR / dataset).exists()
    ]

    if missing:
        raise FileNotFoundError("No se generaron los archivos esperados:\n" + "\n".join(missing))

    data = load_data(
        str(SYNTHETIC_DATA_DIR),
        datasets,
        INSTRUMENTS,
        wl,
        skiprows=1,
        wl_unit="micron",
        bin_width="half",
        spectrum_unit="(Rp/Rs)^2",
    )

    return {
        "scenario_key": scenario_key,
        "n_trans": n_trans,
        "datasets": datasets,
        "data": data,
    }


def generate_synthetic_grid(
    planet,
    wl,
    spectra,
    data_base,
    scenario_keys,
    transit_counts,
    gauss_scatter=True,
):
    """
    Generate the full scenario x transit-count grid of synthetic observations.

    The loops are intentionally small and explicit: the heavy work is inside
    POSEIDON/PandExo-derived routines, and the returned dict preserves enough
    metadata to summarize exactly what was generated.
    """
    runs = {}

    for scenario_key in scenario_keys:
        for n_obs in transit_counts:
            runs[(scenario_key, n_obs)] = generate_synthetic_observation(
                planet,
                wl,
                spectra[scenario_key],
                data_base,
                scenario_key,
                n_obs,
                n_obs,
                gauss_scatter=gauss_scatter,
            )

    return runs


def _rebin_poseidon(wl_native, spectrum_native, R_bin):
    """
    Rebin a spectrum with POSEIDON's native logarithmic-resolution binning.

    Inputs and outputs preserve the units of spectrum_native.  The notebook uses
    this for ppm-valued arrays so the plot remains readable while the stored
    model products stay in transit-depth units.
    """
    wl_bin, spec_bin, _ = bin_spectrum(wl_native, spectrum_native, R_bin)
    return wl_bin, spec_bin


def _finite_limits(arrays, pad_fraction):
    """Return robust limits over finite values from a list of arrays."""
    finite_values = [
        np.asarray(array)[np.isfinite(array)]
        for array in arrays
        if np.asarray(array)[np.isfinite(array)].size
    ]

    if not finite_values:
        return -1.0, 1.0

    values = np.concatenate(finite_values)
    vmin = float(np.nanmin(values))
    vmax = float(np.nanmax(values))
    span = vmax - vmin

    if span <= 0:
        span = max(abs(vmin), 1.0)

    pad = pad_fraction * span
    return vmin - pad, vmax + pad


def _species_label(species):
    """Format simple molecule names with Matplotlib subscripts."""
    return species.replace("2", "$_2$").replace("3", "$_3$").replace("4", "$_4$")


def _apply_log_wavelength_ticks(ax, wl_min=0.8, wl_max=12.0):
    """
    Use presentation-friendly wavelength ticks on a log axis.

    Matplotlib's default log ticks usually show only 1 and 10 microns across
    this wavelength range.  Fixed ticks keep the log spacing while giving
    enough anchors to read NIRSpec and MIRI features by eye.
    """
    tick_candidates = np.array([0.8, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0, 12.0])
    ticks = tick_candidates[(tick_candidates >= wl_min) & (tick_candidates <= wl_max)]

    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{tick:g}" for tick in ticks])


def plot_spectral_contributions_by_scenario(
    wl,
    spectra,
    contributions,
    scenario_keys=("A0", "A1", "A2", "A3"),
    species_order=CONTRIBUTION_SPECIES,
    R_plot=150,
    wl_min=0.8,
    wl_max=12.0,
):
    """
    Show total and molecular contribution spectra separately for each scenario.

    This is the less crowded companion to the two-scenario difference plot:
    every panel has one atmosphere, the same molecular colours, and a shared
    y-axis so the A0-A3 progression can be read without overplotting all
    scenarios in the same axes.
    """
    ppm = 1.0e6
    fig, axes = plt.subplots(2, 2, figsize=(15, 8.6), sharex=True, sharey=True)
    axes = axes.ravel()
    y_arrays = []

    for ax, scenario_key in zip(axes, scenario_keys):
        scenario = SCENARIOS[scenario_key]
        wl_binned, total_binned = _rebin_poseidon(
            wl,
            spectra[scenario_key] * ppm,
            R_plot,
        )
        y_arrays.append(total_binned)

        ax.plot(
            wl_binned,
            total_binned,
            color=CONTRIBUTION_COLOURS["Total"],
            lw=2.3,
            alpha=0.94,
            zorder=5,
            label="Total",
        )

        components = contributions[scenario_key]["components"]
        for species in species_order:
            if species not in components:
                continue

            colour = CONTRIBUTION_COLOURS.get(species, "0.45")
            _, component_binned = _rebin_poseidon(
                wl,
                components[species] * ppm,
                R_plot,
            )
            y_arrays.append(component_binned)

            ax.plot(
                wl_binned,
                component_binned,
                color=colour,
                lw=1.25,
                alpha=0.72,
                zorder=3,
                label=_species_label(species),
            )

        ax.set_title(f"{scenario_key}: {scenario['name']}", fontsize=12)
        ax.set_xscale("log")
        ax.set_xlim(wl_min, wl_max)
        _apply_log_wavelength_ticks(ax, wl_min, wl_max)
        ax.grid(True, which="major", alpha=0.26, linestyle="--")
        ax.tick_params(axis="both", labelsize=9)
        ax.tick_params(axis="x", which="both", labelbottom=True)

    y_min, y_max = _finite_limits(y_arrays, pad_fraction=0.05)
    for ax in axes[: len(scenario_keys)]:
        ax.set_ylim(y_min, y_max)

    for ax in axes[len(scenario_keys):]:
        ax.set_visible(False)

    handles = [
        Line2D([0], [0], color=CONTRIBUTION_COLOURS["Total"], lw=2.3, label="Total")
    ]
    for species in species_order:
        handles.append(
            Line2D(
                [0],
                [0],
                color=CONTRIBUTION_COLOURS.get(species, "0.45"),
                lw=1.8,
                label=_species_label(species),
            )
        )

    fig.legend(
        handles=handles,
        loc="upper center",
        ncol=len(handles),
        frameon=False,
        bbox_to_anchor=(0.5, 1.02),
        fontsize=10,
    )
    fig.supylabel("Transit depth (ppm)", x=0.01)
    fig.supxlabel("Wavelength (micron)", y=0.01)
    fig.suptitle(f"Contribuciones espectrales por escenario (R={R_plot})", y=1.08, fontsize=15)
    fig.tight_layout()
    return fig


def plot_spectral_contribution_baseline_grid(
    wl,
    spectra,
    contributions,
    baseline_key="A0",
    comparison_keys=("A1", "A2", "A3"),
    species_order=CONTRIBUTION_SPECIES,
    R_plot=150,
    wl_min=0.8,
    wl_max=12.0,
):
    """
    Compare several scenarios against one baseline with difference panels.

    Each column is an A_i - A0 comparison: the top axis shows the total and
    molecular contribution spectra for the baseline and target scenario, while
    the lower axis shows target - baseline in ppm.  This preserves the useful
    structure of the original A0-vs-A3 plot without forcing A1, A2, and A3 into
    the same crowded axes.
    """
    ppm = 1.0e6
    n_cols = len(comparison_keys)
    fig, axes = plt.subplots(
        2,
        n_cols,
        figsize=(5.6 * n_cols, 8.2),
        sharex="col",
        gridspec_kw={"height_ratios": [2.25, 1.0]},
    )

    if n_cols == 1:
        axes = np.asarray(axes).reshape(2, 1)

    baseline_components = contributions[baseline_key]["components"]
    shared_top_arrays = []
    shared_delta_arrays = []

    for col, comparison_key in enumerate(comparison_keys):
        ax_top = axes[0, col]
        ax_delta = axes[1, col]
        comparison_components = contributions[comparison_key]["components"]

        wl_binned, baseline_total = _rebin_poseidon(
            wl,
            spectra[baseline_key] * ppm,
            R_plot,
        )
        _, comparison_total = _rebin_poseidon(
            wl,
            spectra[comparison_key] * ppm,
            R_plot,
        )
        total_diff = comparison_total - baseline_total

        top_arrays = [baseline_total, comparison_total]
        delta_arrays = [total_diff]

        ax_top.fill_between(
            wl_binned,
            baseline_total,
            comparison_total,
            color="0.75",
            alpha=0.26,
            zorder=1,
        )

        for species in species_order:
            if species not in baseline_components or species not in comparison_components:
                continue

            colour = CONTRIBUTION_COLOURS.get(species, "0.45")
            _, baseline_component = _rebin_poseidon(
                wl,
                baseline_components[species] * ppm,
                R_plot,
            )
            _, comparison_component = _rebin_poseidon(
                wl,
                comparison_components[species] * ppm,
                R_plot,
            )
            component_diff = comparison_component - baseline_component

            top_arrays.extend([baseline_component, comparison_component])
            delta_arrays.append(component_diff)

            ax_top.plot(
                wl_binned,
                baseline_component,
                color=colour,
                linestyle="-",
                lw=1.05,
                alpha=0.52,
                zorder=2,
            )
            ax_top.plot(
                wl_binned,
                comparison_component,
                color=colour,
                linestyle="--",
                lw=1.10,
                alpha=0.76,
                zorder=2,
            )

            ax_delta.plot(
                wl_binned,
                component_diff,
                color=colour,
                lw=1.20,
                alpha=0.84,
                zorder=3,
            )
            ax_delta.fill_between(
                wl_binned,
                0.0,
                component_diff,
                color=colour,
                alpha=0.18,
                zorder=2,
            )

        ax_top.plot(
            wl_binned,
            baseline_total,
            color=CONTRIBUTION_COLOURS["Total"],
            linestyle="-",
            lw=2.1,
            alpha=0.92,
            zorder=5,
        )
        ax_top.plot(
            wl_binned,
            comparison_total,
            color=CONTRIBUTION_COLOURS["Total"],
            linestyle="--",
            lw=2.1,
            alpha=0.94,
            zorder=5,
        )

        ax_delta.plot(
            wl_binned,
            total_diff,
            color="black",
            lw=1.75,
            alpha=0.84,
            zorder=6,
        )
        ax_delta.axhline(0.0, color="black", lw=1.0, linestyle=":", zorder=7)

        shared_top_arrays.extend(top_arrays)
        shared_delta_arrays.extend(delta_arrays)

        for ax in (ax_top, ax_delta):
            ax.set_xscale("log")
            ax.set_xlim(wl_min, wl_max)
            _apply_log_wavelength_ticks(ax, wl_min, wl_max)
            ax.grid(True, which="major", alpha=0.26, linestyle="--")
            ax.tick_params(axis="both", labelsize=9)

        ax_top.set_title(f"{baseline_key} vs {comparison_key}", fontsize=12)
        ax_delta.set_xlabel("Wavelength (micron)")

        if col == 0:
            ax_top.set_ylabel("Transit depth (ppm)")
            ax_delta.set_ylabel(r"$\Delta$ depth (ppm)")

    top_min, top_max = _finite_limits(shared_top_arrays, pad_fraction=0.05)
    delta_min, delta_max = _finite_limits(shared_delta_arrays, pad_fraction=0.14)
    for ax in axes[0, :n_cols]:
        ax.set_ylim(top_min, top_max)
    for ax in axes[1, :n_cols]:
        ax.set_ylim(delta_min, delta_max)

    component_handles = [
        Line2D([0], [0], color=CONTRIBUTION_COLOURS["Total"], lw=2.2, label="Total")
    ]
    for species in species_order:
        component_handles.append(
            Line2D(
                [0],
                [0],
                color=CONTRIBUTION_COLOURS.get(species, "0.45"),
                lw=1.8,
                label=_species_label(species),
            )
        )

    style_handles = [
        Line2D([0], [0], color="0.35", lw=2.0, linestyle="-", label=baseline_key),
        Line2D([0], [0], color="0.35", lw=2.0, linestyle="--", label="A1/A2/A3"),
    ]

    fig.legend(
        handles=component_handles + style_handles,
        loc="upper center",
        ncol=len(component_handles) + len(style_handles),
        frameon=False,
        bbox_to_anchor=(0.5, 1.02),
        fontsize=9,
    )
    fig.suptitle(
        f"Contribuciones espectrales relativas a {baseline_key} (R={R_plot})",
        y=1.07,
        fontsize=15,
    )
    fig.tight_layout()
    return fig


def measure_peak_growth_relative_to_baseline(
    wl,
    spectra,
    baseline_key="A0",
    comparison_keys=("A1", "A2", "A3"),
    peak_windows=DEFAULT_PEAK_WINDOWS,
    R_plot=150,
):
    """
    Measure total-spectrum peak growth in selected diagnostic windows.

    For each feature window, the metric is the maximum value of
    total_spectrum(A_i) - total_spectrum(A0) after rebinning to R_plot, reported
    in ppm.  The feature label names the molecule that dominates that band, but
    the measured quantity is the total transit-depth spectrum.
    """
    ppm = 1.0e6
    rows = []
    wl_binned, baseline_binned = _rebin_poseidon(
        wl,
        spectra[baseline_key] * ppm,
        R_plot,
    )

    for window in peak_windows:
        species = window["species"]
        mask = (wl_binned >= window["wl_min"]) & (wl_binned <= window["wl_max"])

        if not np.any(mask):
            raise ValueError(
                f"La ventana {window['label']} no contiene puntos: "
                f"{window['wl_min']}-{window['wl_max']} micron"
            )

        for comparison_key in comparison_keys:
            _, comparison_binned = _rebin_poseidon(
                wl,
                spectra[comparison_key] * ppm,
                R_plot,
            )
            diff = comparison_binned - baseline_binned
            peak_idx_local = int(np.nanargmax(diff[mask]))
            window_indices = np.flatnonzero(mask)
            peak_idx = int(window_indices[peak_idx_local])

            rows.append(
                {
                    "feature": window["label"],
                    "species": species,
                    "scenario": comparison_key,
                    "wavelength": float(wl_binned[peak_idx]),
                    "magnitude_ppm": float(diff[peak_idx]),
                    "window": (window["wl_min"], window["wl_max"]),
                }
            )

    return rows


def plot_peak_growth_relative_to_baseline(
    wl,
    spectra,
    baseline_key="A0",
    comparison_keys=("A1", "A2", "A3"),
    peak_windows=DEFAULT_PEAK_WINDOWS,
    R_plot=150,
):
    """
    Plot selected total-spectrum peak growth from A1 to A3 relative to A0.

    The x-axis is categorical scenario number, while the y-axis is the measured
    peak increase in ppm.  The default windows are labelled by their dominant
    molecules: two N2O bands and one NH3 band.
    """
    rows = measure_peak_growth_relative_to_baseline(
        wl,
        spectra,
        baseline_key=baseline_key,
        comparison_keys=comparison_keys,
        peak_windows=peak_windows,
        R_plot=R_plot,
    )

    x = np.arange(len(comparison_keys))
    feature_styles = {
        "Banda N$_2$O 1": {"color": "#1565c0", "marker": "o", "linestyle": "-"},
        "Banda N$_2$O 2": {"color": "#00a6a6", "marker": "s", "linestyle": "--"},
        "Banda NH$_3$": {"color": CONTRIBUTION_COLOURS["NH3"], "marker": "^", "linestyle": "-"},
    }

    fig, ax = plt.subplots(figsize=(8.8, 5.3))
    ax.set_facecolor("#fbfbfb")

    for window in peak_windows:
        feature = window["label"]
        values = [
            next(
                row["magnitude_ppm"]
                for row in rows
                if row["feature"] == feature and row["scenario"] == scenario_key
            )
            for scenario_key in comparison_keys
        ]
        wavelengths = [
            next(
                row["wavelength"]
                for row in rows
                if row["feature"] == feature and row["scenario"] == scenario_key
            )
            for scenario_key in comparison_keys
        ]
        style = feature_styles.get(
            feature,
            {"color": "0.35", "marker": "o", "linestyle": "-"},
        )
        label = f"{feature}: {window['wl_min']:.1f}-{window['wl_max']:.1f} micron"

        ax.plot(
            x,
            values,
            color=style["color"],
            marker=style["marker"],
            linestyle=style["linestyle"],
            lw=2.4,
            ms=7.0,
            markeredgecolor="white",
            markeredgewidth=0.9,
            label=label,
        )

        for x_i, y_i, wl_i in zip(x, values, wavelengths):
            ax.annotate(
                f"{y_i:.1f}",
                (x_i, y_i),
                textcoords="offset points",
                xytext=(0, 9),
                ha="center",
                fontsize=8,
                color=style["color"],
                bbox={"boxstyle": "round,pad=0.18", "fc": "white", "ec": "none", "alpha": 0.72},
            )

    ax.axhline(0.0, color="0.25", lw=1.0, linestyle=":")
    ax.set_xlim(-0.28, len(comparison_keys) - 1 + 0.28)
    ax.set_xticks(x)
    ax.set_xticklabels(comparison_keys)
    ax.set_xlabel(f"Escenario comparado con {baseline_key}")
    ax.set_ylabel("Aumento del espectro total (ppm)")
    ax.set_title(f"Crecimiento del espectro total en bandas diagnósticas vs {baseline_key}", pad=14)
    ax.grid(True, axis="y", alpha=0.22, linestyle="--")
    ax.grid(True, axis="x", alpha=0.08, linestyle="-")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=False, fontsize=9, loc="upper left", bbox_to_anchor=(1.02, 1.0))
    fig.tight_layout()

    return fig, rows


def plot_spectral_contribution_comparison(
    wl,
    spectra,
    contributions,
    baseline_key="A0",
    comparison_key="A3",
    species_order=CONTRIBUTION_SPECIES,
    R_plot=150,
    wl_min=0.8,
    wl_max=12.0,
):
    """
    Compare total and molecular contributions between two scenarios.

    The top panel shows the rebinned total spectra and selected molecular
    contribution curves.  The lower panel emphasizes the difference
    comparison_key - baseline_key, which makes the incremental technosignature
    signal easier to read than in a single crowded spectrum panel.
    """
    ppm = 1.0e6
    wl_binned, baseline_total = _rebin_poseidon(
        wl,
        spectra[baseline_key] * ppm,
        R_plot,
    )
    _, comparison_total = _rebin_poseidon(
        wl,
        spectra[comparison_key] * ppm,
        R_plot,
    )
    total_diff = comparison_total - baseline_total

    fig, (ax_top, ax_delta) = plt.subplots(
        2,
        1,
        figsize=(14, 9),
        sharex=True,
        gridspec_kw={"height_ratios": [2.3, 1.0]},
    )

    ax_top.fill_between(
        wl_binned,
        baseline_total,
        comparison_total,
        color="0.75",
        alpha=0.30,
        zorder=1,
        label="Total envelope",
    )

    top_arrays = [baseline_total, comparison_total]
    delta_arrays = [total_diff]

    baseline_components = contributions[baseline_key]["components"]
    comparison_components = contributions[comparison_key]["components"]

    for species in species_order:
        if species not in baseline_components or species not in comparison_components:
            continue

        colour = CONTRIBUTION_COLOURS.get(species, "0.45")
        _, baseline_component = _rebin_poseidon(
            wl,
            baseline_components[species] * ppm,
            R_plot,
        )
        _, comparison_component = _rebin_poseidon(
            wl,
            comparison_components[species] * ppm,
            R_plot,
        )
        component_diff = comparison_component - baseline_component

        top_arrays.extend([baseline_component, comparison_component])
        delta_arrays.append(component_diff)

        ax_top.plot(
            wl_binned,
            baseline_component,
            color=colour,
            linestyle="-",
            lw=1.15,
            alpha=0.62,
            zorder=2,
        )
        ax_top.plot(
            wl_binned,
            comparison_component,
            color=colour,
            linestyle="--",
            lw=1.15,
            alpha=0.72,
            zorder=2,
        )

        ax_delta.plot(
            wl_binned,
            component_diff,
            color=colour,
            linestyle="-",
            lw=1.45,
            alpha=0.90,
            zorder=3,
        )
        ax_delta.fill_between(
            wl_binned,
            0.0,
            component_diff,
            color=colour,
            alpha=0.22,
            zorder=2,
        )

    ax_top.plot(
        wl_binned,
        baseline_total,
        color=CONTRIBUTION_COLOURS["Total"],
        linestyle="-",
        lw=2.4,
        alpha=0.95,
        zorder=5,
    )
    ax_top.plot(
        wl_binned,
        comparison_total,
        color=CONTRIBUTION_COLOURS["Total"],
        linestyle="--",
        lw=2.4,
        alpha=0.95,
        zorder=5,
    )

    ax_delta.plot(
        wl_binned,
        total_diff,
        color="black",
        linestyle="-",
        lw=2.0,
        alpha=0.86,
        zorder=6,
        label="Total difference",
    )
    ax_delta.axhline(0.0, color="black", lw=1.15, linestyle=":", zorder=7)

    top_min, top_max = _finite_limits(top_arrays, pad_fraction=0.05)
    delta_min, delta_max = _finite_limits(delta_arrays, pad_fraction=0.12)
    ax_top.set_ylim(top_min, top_max)
    ax_delta.set_ylim(delta_min, delta_max)

    molecule_handles = [
        Line2D([0], [0], color=CONTRIBUTION_COLOURS["Total"], lw=2.4, label="Total")
    ]
    for species in species_order:
        if species in baseline_components and species in comparison_components:
            molecule_handles.append(
                Line2D(
                    [0],
                    [0],
                    color=CONTRIBUTION_COLOURS.get(species, "0.45"),
                    lw=2.0,
                    label=_species_label(species),
                )
            )

    style_handles = [
        Line2D([0], [0], color="0.35", lw=2.0, linestyle="-", label=baseline_key),
        Line2D([0], [0], color="0.35", lw=2.0, linestyle="--", label=comparison_key),
    ]

    leg_components = ax_top.legend(
        handles=molecule_handles,
        loc="upper left",
        title="Componentes",
        fontsize=9,
        title_fontsize=10,
        frameon=True,
        edgecolor="0.82",
    )
    ax_top.add_artist(leg_components)
    ax_top.legend(
        handles=style_handles,
        loc="upper right",
        title="Escenarios",
        fontsize=9,
        title_fontsize=10,
        frameon=True,
        edgecolor="0.82",
    )

    ax_top.set_title(
        f"Contribuciones espectrales {baseline_key} vs {comparison_key} (R={R_plot})",
        fontsize=14,
        pad=12,
    )
    ax_top.set_ylabel("Transit depth (ppm)")
    ax_delta.set_ylabel(r"$\Delta$ depth (ppm)")
    ax_delta.set_xlabel("Wavelength (micron)")

    for ax in (ax_top, ax_delta):
        ax.set_xscale("log")
        ax.set_xlim(wl_min, wl_max)
        _apply_log_wavelength_ticks(ax, wl_min, wl_max)
        ax.grid(True, which="major", alpha=0.28, linestyle="--")
        ax.tick_params(axis="both", labelsize=10)

    fig.tight_layout()
    fig.subplots_adjust(hspace=0.05)
    return fig


def _binned_spectrum_for_plot(wl, spectrum, R_plot=DEFAULT_PLOT_R):
    """
    Return a visually binned forward spectrum in ppm units.

    The synthetic data files are already generated at R_TO_BIN, but the forward
    spectra are computed on POSEIDON's native high-resolution grid.  Rebinning
    the model curve keeps the comparison readable and mirrors the original
    Plot_Transmission_Spectra_TRAPPIST notebook, where plot_spectra was called
    with plot_full_res=False and R_to_bin=100.
    """
    return _rebin_poseidon(wl, spectrum * 1.0e6, R_plot)


def _plot_errorbar_dataset(
    ax,
    dataset,
    colour,
    marker,
    label=None,
    marker_alpha=0.62,
    eline_alpha=0.24,
    marker_size=2.6,
    eline_width=0.55,
):
    """
    Draw one NIRSpec+MIRI observation pair in ppm units.

    We convert only for visualization.  The stored .dat files remain in
    POSEIDON's native (Rp/Rs)^2 transit-depth units.  The data are already
    binned by generate_syn_data_from_file through R_TO_BIN; the softer marker
    and error-bar styling prevents the multi-panel comparisons from turning
    into a wall of vertical lines.
    """
    ppm = 1.0e6

    for instrument_name in ("nirspec", "miri"):
        instrument = dataset[instrument_name]
        container = ax.errorbar(
            instrument["wavelength"],
            instrument["depth"] * ppm,
            yerr=instrument["depth_err"] * ppm,
            xerr=instrument["wavelength_err"],
            fmt=marker,
            ms=marker_size,
            color=colour,
            ecolor=colour,
            elinewidth=eline_width,
            capsize=0,
            alpha=marker_alpha,
            linestyle="none",
            label=label,
            zorder=3,
        )

        # Matplotlib applies alpha to both points and bars by default.  The
        # original notebook made the bars much softer than the markers, so we
        # tune the bar collections after creating the container.
        for bar_collection in container[2]:
            bar_collection.set_alpha(eline_alpha)

        label = None


def _set_shared_spectrum_axes(ax, wl_min, wl_max, y_min, y_max):
    """Apply common formatting to spectrum/errorbar axes."""
    ax.set_xlim(wl_min, wl_max)
    ax.set_ylim(y_min, y_max)
    ax.grid(alpha=0.18)
    ax.set_xlabel("Wavelength (micron)")
    ax.set_ylabel("Transit depth (ppm)")


def spectrum_plot_limits(wl, spectra, scenario_keys, wl_min=0.8, wl_max=12.0, pad_fraction=0.22):
    """Compute y limits from the forward spectra in ppm units."""
    mask = (wl >= wl_min) & (wl <= wl_max)
    values = np.concatenate([spectra[key][mask] for key in scenario_keys]) * 1.0e6
    span = float(values.max() - values.min())

    if span <= 0:
        span = 20.0

    pad = pad_fraction * span
    return float(values.min() - pad), float(values.max() + pad)


def plot_observations_by_scenario(
    wl,
    spectra,
    scenario_keys,
    transit_counts=OBSERVATION_TRANSIT_COUNTS,
    R_model_bin=DEFAULT_PLOT_R,
    wl_min=0.8,
    wl_max=12.0,
):
    """
    Make four panels: one scenario per panel, with 5/10/20 error bars.

    This view answers: for a fixed atmosphere, how much do the uncertainties
    shrink as the observing plan goes from 5+5 to 20+20 transits?
    """
    y_min, y_max = spectrum_plot_limits(wl, spectra, scenario_keys, wl_min, wl_max)
    fig, axes = plt.subplots(2, 2, figsize=(15, 8.5), sharex=True, sharey=True)
    axes = axes.ravel()

    for ax, scenario_key in zip(axes, scenario_keys):
        scenario = SCENARIOS[scenario_key]
        wl_model, spectrum_model = _binned_spectrum_for_plot(
            wl,
            spectra[scenario_key],
            R_plot=R_model_bin,
        )
        ax.plot(
            wl_model,
            spectrum_model,
            color=scenario["colour"],
            lw=2.5,
            alpha=0.58,
            label=f"Modelo rebinned (R={R_model_bin})",
            zorder=4,
        )

        for n_obs in transit_counts:
            style = TRANSIT_COUNT_STYLES[n_obs]
            observation = load_synthetic_observation(scenario_key, n_obs)
            _plot_errorbar_dataset(
                ax,
                observation,
                colour=style["colour"],
                marker=style["marker"],
                label=style["label"],
            )

        _set_shared_spectrum_axes(ax, wl_min, wl_max, y_min, y_max)
        ax.set_title(f"{scenario_key}: {scenario['name']}")
        ax.legend(frameon=False, fontsize=8, loc="best")

    fig.suptitle("Observaciones sintéticas por escenario", y=1.02, fontsize=15)
    fig.tight_layout()
    return fig


def plot_observations_by_noise_level(
    wl,
    spectra,
    scenario_keys,
    transit_counts=OBSERVATION_TRANSIT_COUNTS,
    R_model_bin=DEFAULT_PLOT_R,
    wl_min=0.8,
    wl_max=12.0,
):
    """
    Make three panels: one transit count per panel, with A0-A3 error bars.

    This view answers: at a fixed noise level, how separable are the four
    atmospheric scenarios in the synthetic JWST observations?
    """
    y_min, y_max = spectrum_plot_limits(wl, spectra, scenario_keys, wl_min, wl_max)
    fig, axes = plt.subplots(
        1,
        len(transit_counts),
        figsize=(5.8 * len(transit_counts), 5.2),
        sharex=True,
        sharey=True,
    )

    if len(transit_counts) == 1:
        axes = [axes]

    for ax, n_obs in zip(axes, transit_counts):
        for scenario_key in scenario_keys:
            scenario = SCENARIOS[scenario_key]
            wl_model, spectrum_model = _binned_spectrum_for_plot(
                wl,
                spectra[scenario_key],
                R_plot=R_model_bin,
            )
            ax.plot(
                wl_model,
                spectrum_model,
                color=scenario["colour"],
                lw=2.0,
                alpha=0.54,
                zorder=2,
            )

            observation = load_synthetic_observation(scenario_key, n_obs)
            _plot_errorbar_dataset(
                ax,
                observation,
                colour=scenario["colour"],
                marker=SCENARIO_MARKERS[scenario_key],
                label=f"{scenario_key}: {scenario['name']}",
                marker_alpha=0.64,
                eline_alpha=0.22,
            )

        _set_shared_spectrum_axes(ax, wl_min, wl_max, y_min, y_max)
        ax.set_title(f"NIRSpec={n_obs}, MIRI={n_obs}")
        ax.legend(frameon=False, fontsize=8, loc="best")

    fig.suptitle("Comparación de escenarios por nivel de ruido", y=1.03, fontsize=15)
    fig.tight_layout()
    return fig
