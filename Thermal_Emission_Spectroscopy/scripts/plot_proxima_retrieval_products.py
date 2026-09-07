"""Create the three publication-facing LIFE retrieval figures for Proxima.

The figures are built only from products that already exist in the campaign
directory.  The canonical retrieval matrix is A0--A3 at 10 h and 240 h, while
the presentation compares the two scientifically informative extremes A0 and
A3.  The available A3--1200 h retrieval is intentionally reported as an
excluded pilot and is not mixed into these figures.

Outputs
-------
``retrieval_global_spectra_proxima``
    Full LIFE wavelength range with forward spectrum, retrieved spectrum,
    posterior uncertainty, and the binned synthetic observations.
``retrieval_molecular_zooms_proxima``
    Three selected N2O/NH3 windows, using the same line and colour meanings.
``retrieval_profiles_posteriors_proxima``
    A3 marginal posterior samples with the A3 VULCAN profiles, the effective
    A0 pressure-column reference, posterior medians, and comparison metrics.
``retrieval_profiles_posteriors_proxima_4rows_audit``
    Optional audit view with A3 posterior rows for 10, 240, 500, and 1200 h;
    the latter two use the robust direct-LIFEsim retrieval products.

The direct planetary-flux convention is preserved throughout:
``F_p`` is in W m^-2 m^-1, with the plotted ordinate scaled by 10^-13 only for
readability.  High-resolution forward and retrieved spectra are interpolated
onto 250 points in the global panel and 75 points in each zoom for display;
the underlying products remain unchanged.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.offsetbox import AnchoredOffsetbox, TextArea, VPacker


REPO = Path(__file__).resolve().parents[2]
STYLE_DIR = REPO / "Transmission_Spectroscopy" / "notebooks"
sys.path.insert(0, str(STYLE_DIR))
from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE
from retrieval_reference import log10_column_averaged_mixing_ratio


CAMPAIGN_ID = "life_proxima_b_earthlike_v1"
CAMPAIGN_DIR = REPO / "Thermal_Emission_Spectroscopy" / "outputs" / CAMPAIGN_ID
PLOTS_DIR = CAMPAIGN_DIR / "plots"
FORWARD_DIR = CAMPAIGN_DIR / "forward_emission"
LIFE_DATA_DIR = CAMPAIGN_DIR / "life_data"
SAMPLES_DIR = (
    CAMPAIGN_DIR
    / "retrievals"
    / "POSEIDON_output"
    / "proxima_b_earthlike"
    / "retrievals"
    / "samples"
)
PROFILE_DIR = REPO / "Transmission_Spectroscopy" / "profiles"

PLOT_SCENARIOS = ("A0", "A3")
PROFILE_POSTERIOR_SCENARIO = "A3"
PROFILE_REFERENCE_SCENARIO = "A0"
HOURS = (10, 240)
SCENARIOS = {
    "A0": {
        "label": "A0: Pre-agricultural",
        "color": PALETTE["scenario_green"],
        "profile_stem": "Proxima_b_A0_PreAgri",
    },
    "A1": {
        "label": "A1: Current Earth",
        "color": PALETTE["scenario_cyan"],
        "profile_stem": "Proxima_b_A1_Current",
    },
    "A2": {
        "label": "A2: Moderate ExoFarm",
        "color": PALETTE["scenario_violet"],
        "profile_stem": "Proxima_b_A2_Moderate",
    },
    "A3": {
        "label": "A3: Extreme ExoFarm",
        "color": PALETTE["scenario_pink"],
        "profile_stem": "Proxima_b_A3_Extreme",
    },
}

MOLECULES = ("H2O", "CO2", "CH4", "O3", "N2O", "NH3")
MOLECULE_LABELS = {
    "H2O": r"H$_2$O",
    "CO2": r"CO$_2$",
    "CH4": r"CH$_4$",
    "O3": r"O$_3$",
    "N2O": r"N$_2$O",
    "NH3": r"NH$_3$",
}
PROFILE_X_AXIS_LABELS = {
    "H2O": r"log(X$_{\mathrm{H_2O}}$)",
    "CO2": r"log(X$_{\mathrm{CO_2}}$)",
    "CH4": r"log(X$_{\mathrm{CH_4}}$)",
    "O3": r"log(X$_{\mathrm{O_3}}$)",
    "N2O": r"log(X$_{\mathrm{N_2O}}$)",
    "NH3": r"log(X$_{\mathrm{NH_3}}$)",
}
SAMPLE_COLUMNS = (
    "R_p_ref",
    "a1",
    "a2",
    "log_P1",
    "log_P2",
    "log_P3",
    "T_ref",
    "log_H2O",
    "log_CO2",
    "log_CH4",
    "log_O3",
    "log_N2O",
    "log_NH3",
    "x_tol",
    "log_P_surf",
)
SAMPLE_INDEX = {name.removeprefix("log_"): i for i, name in enumerate(SAMPLE_COLUMNS) if name.startswith("log_")}

WAVELENGTH_RANGE = (3.8, 19.0)
FLUX_SCALE = 1.0e-13
PROFILE_FLOOR = 1.0e-30
GLOBAL_DISPLAY_POINTS = 250
ZOOM_DISPLAY_POINTS = 75
RETRIEVED_2SIGMA_ALPHA = 0.025
RETRIEVED_1SIGMA_ALPHA = 0.05
RETRIEVED_MEDIAN_ALPHA = 0.70
TRUE_SPECTRUM_ALPHA = 0.50
OBSERVATION_MARKERSIZE_GLOBAL = 5.8
OBSERVATION_MARKERSIZE_ZOOM = 6.2
OBSERVATION_MARKER_EDGE = PALETTE["dim_grey"]
OBSERVATION_MARKER_EDGE_WIDTH_GLOBAL = 0.90
OBSERVATION_MARKER_EDGE_WIDTH_ZOOM = 0.95
ZOOM_WINDOWS = (
    (7.15, 8.35, r"N$_2$O (7.15 - 8.35 $\mu$m)"),
    (10.0, 11.25, r"NH$_3$ (10.0 - 11.25 $\mu$m)"),
    (16.25, 17.75, r"N$_2$O (16.25 - 17.75 $\mu$m)"),
)

# Match the transmission-plot semantics: vivid scenario colours identify the
# retrieved model, darker companion colours identify the true/observed case,
# and marker shape distinguishes the two scenarios in the data.
RETRIEVED_COLORS = {
    "A0": PALETTE["scenario_green"],
    "A3": PALETTE["scenario_pink"],
}
TRUE_COLORS = {
    "A0": PALETTE["deep_moss"],
    "A3": PALETTE["dark_amaranth"],
}
OBSERVATION_COLORS = TRUE_COLORS.copy()
SCENARIO_MARKERS = {
    "A0": "o",
    "A3": "d",
}
mpl.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": [
            "STIXGeneral",
            "DejaVu Serif",
            "Times New Roman",
            "CMU Serif",
            "Liberation Serif",
        ],
        "mathtext.fontset": "stix",
        "axes.unicode_minus": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": False,
        "axes.linewidth": 0.8,
        "figure.titlesize": 16,
        "figure.titleweight": "normal",
        "figure.dpi": 140,
        "font.size": 10,
        "axes.titlesize": 13,
        "axes.titleweight": "normal",
    }
)


def retrieval_stem(scenario: str, hours: int, output_tag: str = "") -> str:
    """Return the shared stem used by the LIFE retrieval exports."""
    run_name = f"proxima_{scenario}_{hours}h{output_tag}"
    return f"{run_name}_proxima_{scenario}_{hours}h{output_tag}"


def require(path: Path) -> Path:
    """Raise an actionable error when a required evidence file is absent."""
    if not path.exists():
        raise FileNotFoundError(path)
    return path


def load_observation(scenario: str, hours: int) -> dict[str, np.ndarray]:
    """Load one binned LIFE observation in the campaign's direct-Fp units."""
    path = require(LIFE_DATA_DIR / f"LIFE_proxima_{scenario}_{hours}h.dat")
    data = np.loadtxt(path, skiprows=1)
    return {
        "wavelength": data[:, 0],
        "half_bin": data[:, 1],
        "flux": data[:, 2] / FLUX_SCALE,
        "sigma": data[:, 3] / FLUX_SCALE,
    }


def load_retrieved_spectrum(scenario: str, hours: int) -> dict[str, np.ndarray]:
    """Load retrieved spectrum quantiles and scale Fp for display."""
    path = require(SAMPLES_DIR / f"{retrieval_stem(scenario, hours)}_spectrum_retrieved.txt")
    data = np.loadtxt(path, skiprows=1)
    return {
        "wavelength": data[:, 0],
        "q02": data[:, 1] / FLUX_SCALE,
        "q16": data[:, 2] / FLUX_SCALE,
        "median": data[:, 3] / FLUX_SCALE,
        "q84": data[:, 4] / FLUX_SCALE,
        "q98": data[:, 5] / FLUX_SCALE,
    }


def load_truth_spectrum(scenario: str) -> dict[str, np.ndarray]:
    """Load the direct planetary flux from the forward-emission product."""
    path = require(FORWARD_DIR / f"{scenario}_emission.npz")
    with np.load(path) as data:
        return {
            "wavelength": np.asarray(data["wl_um"]),
            "flux": np.asarray(data["Fp_obs_W_m2_m"]) / FLUX_SCALE,
        }


def load_samples(scenario: str, hours: int, output_tag: str = "") -> np.ndarray:
    """Load posterior draws using the fixed POSEIDON export column order."""
    path = require(
        SAMPLES_DIR / f"{retrieval_stem(scenario, hours, output_tag)}_samples.txt"
    )
    data = np.loadtxt(path, skiprows=1)
    return np.atleast_2d(data)


def load_truth_profile(scenario: str) -> np.ndarray:
    """Load a VULCAN-derived chemical profile with named columns."""
    stem = SCENARIOS[scenario]["profile_stem"]
    return np.genfromtxt(PROFILE_DIR / f"{stem}_chem.txt", names=True)


def load_retrieved_log_profile(scenario: str, hours: int) -> dict[str, np.ndarray]:
    """Parse the block-formatted retrieved vertical-abundance export."""
    path = require(SAMPLES_DIR / f"{retrieval_stem(scenario, hours)}_log_X_retrieved.txt")
    lines = path.read_text(encoding="utf-8").splitlines()
    blocks: dict[str, np.ndarray] = {}
    header_pattern = re.compile(r"P \(bar\) \| log_([A-Za-z0-9_]+):")
    index = 0
    while index < len(lines):
        match = header_pattern.match(lines[index].strip())
        if match is None:
            index += 1
            continue
        molecule = match.group(1)
        index += 1
        rows = []
        while index < len(lines):
            fields = lines[index].split()
            if len(fields) < 6:
                break
            try:
                rows.append([float(value) for value in fields[:6]])
            except ValueError:
                break
            index += 1
        if rows:
            blocks[molecule] = np.asarray(rows, dtype=float)
    missing = [molecule for molecule in MOLECULES if molecule not in blocks]
    if missing:
        raise ValueError(f"Missing retrieved log-X blocks in {path}: {missing}")
    return blocks


def load_campaign_products() -> dict[str, dict]:
    """Load and validate all products needed by the three canonical figures."""
    products = {"truth": {}, "observations": {}, "retrieved": {}, "samples": {}, "profiles": {}}
    for scenario in PLOT_SCENARIOS:
        products["truth"][scenario] = load_truth_spectrum(scenario)
        products["profiles"][scenario] = load_truth_profile(scenario)
        for hours in HOURS:
            key = (scenario, hours)
            products["observations"][key] = load_observation(scenario, hours)
            products["retrieved"][key] = load_retrieved_spectrum(scenario, hours)
            products["samples"][key] = load_samples(scenario, hours)
    return products


def finite_values(arrays) -> np.ndarray:
    """Concatenate finite values from an iterable of arrays."""
    values = np.concatenate([np.ravel(np.asarray(array)) for array in arrays])
    return values[np.isfinite(values)]


def padded_limits(arrays, fraction: float = 0.08, minimum_pad: float = 0.2) -> tuple[float, float]:
    """Return finite limits with a small readable margin."""
    values = finite_values(arrays)
    if values.size == 0:
        return -1.0, 1.0
    lower = float(np.min(values))
    upper = float(np.max(values))
    span = max(upper - lower, minimum_pad)
    padding = max(minimum_pad, fraction * span)
    return lower - padding, upper + padding


def spectrum_band_mask(wavelength: np.ndarray) -> np.ndarray:
    """Select the common wavelength interval used by retrieved spectra."""
    return (wavelength >= WAVELENGTH_RANGE[0]) & (wavelength <= WAVELENGTH_RANGE[1])


def resample_retrieved_spectrum(
    spectrum: dict[str, np.ndarray], target_wavelength: np.ndarray
) -> dict[str, np.ndarray]:
    """Interpolate retrieved quantiles onto a clean display grid."""
    resampled = {
        key: np.interp(target_wavelength, spectrum["wavelength"], spectrum[key])
        for key in ("q02", "q16", "median", "q84", "q98")
    }
    resampled["wavelength"] = target_wavelength
    return resampled


def resample_truth_spectrum(
    spectrum: dict[str, np.ndarray], target_wavelength: np.ndarray
) -> dict[str, np.ndarray]:
    """Interpolate a VULCAN forward spectrum onto a clean display grid."""
    return {
        "wavelength": target_wavelength,
        "flux": np.interp(target_wavelength, spectrum["wavelength"], spectrum["flux"]),
    }


def flux_ylabel() -> str:
    return r"Planetary flux $F_p$ [$10^{-13}$ W m$^{-2}$ m$^{-1}$]"


def comparison_legend_handles() -> list[Line2D]:
    """Return the transmission-style Retrieved/True/Observed legend."""
    ret_a0 = Line2D([], [], color=RETRIEVED_COLORS["A0"], lw=2.5, label="Retrieved A0")
    ret_a3 = Line2D([], [], color=RETRIEVED_COLORS["A3"], lw=2.5, label="Retrieved A3")
    true_a0 = Line2D(
        [], [], color=TRUE_COLORS["A0"], lw=1.2, alpha=0.70, label="True A0"
    )
    true_a3 = Line2D(
        [], [], color=TRUE_COLORS["A3"], lw=1.2, alpha=0.70, label="True A3"
    )
    observed_a0 = Line2D(
        [], [], color="none", marker=SCENARIO_MARKERS["A0"], markersize=6.0,
        markerfacecolor=OBSERVATION_COLORS["A0"],
        markeredgecolor=OBSERVATION_MARKER_EDGE, markeredgewidth=0.90,
        alpha=1.0, label="Observed A0",
    )
    observed_a3 = Line2D(
        [], [], color="none", marker=SCENARIO_MARKERS["A3"], markersize=6.0,
        markerfacecolor=OBSERVATION_COLORS["A3"],
        markeredgecolor=OBSERVATION_MARKER_EDGE, markeredgewidth=0.90,
        alpha=1.0, label="Observed A3",
    )
    # Matplotlib fills legend columns in the same order as the transmission
    # reference: Retrieved, True, Observed.
    return [ret_a0, ret_a3, true_a0, true_a3, observed_a0, observed_a3]


def add_comparison_legend(fig: plt.Figure, title: str) -> None:
    """Place a single framed Retrieved/True/Observed legend above the axes."""
    fig.suptitle(title, fontsize=14, fontweight="bold", y=0.98)
    fig.legend(
        handles=comparison_legend_handles(),
        loc="upper center",
        ncol=3,
        bbox_to_anchor=(0.5, 0.93),
        frameon=True,
        facecolor="white",
        edgecolor="none",
        framealpha=0.8,
        fontsize=9,
        handlelength=2.0,
        columnspacing=1.7,
        labelspacing=0.35,
    )


def plot_observation_markers(
    ax: plt.Axes,
    observed: dict[str, np.ndarray],
    observed_mask: np.ndarray,
    scenario: str,
    markersize: float,
    markeredgewidth: float,
) -> None:
    """Overlay opaque observation markers on the translucent error bars."""
    ax.plot(
        observed["wavelength"][observed_mask],
        observed["flux"][observed_mask],
        linestyle="none",
        marker=SCENARIO_MARKERS[scenario],
        markersize=markersize,
        color=OBSERVATION_COLORS[scenario],
        markerfacecolor=OBSERVATION_COLORS[scenario],
        markeredgecolor=OBSERVATION_MARKER_EDGE,
        markeredgewidth=markeredgewidth,
        alpha=1.0,
        zorder=45,
    )


def plot_global_spectra(products: dict[str, dict]) -> plt.Figure:
    """Plot the full retrieved LIFE spectra at 10 h and 240 h."""
    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    for row, hours in enumerate(HOURS):
        ax = axes[row]
        arrays = []
        target_wavelength = np.linspace(
            WAVELENGTH_RANGE[0], WAVELENGTH_RANGE[1], GLOBAL_DISPLAY_POINTS
        )

        # Retrieved models use the vivid scenario colours and the true VULCAN
        # spectra use the darker companion colours, as in the transmission
        # reference figures.
        for scenario in PLOT_SCENARIOS:
            retrieved = resample_retrieved_spectrum(
                products["retrieved"][(scenario, hours)], target_wavelength
            )
            retrieved_color = RETRIEVED_COLORS[scenario]

            ax.fill_between(
                retrieved["wavelength"],
                retrieved["q02"],
                retrieved["q98"],
                color=retrieved_color,
                alpha=RETRIEVED_2SIGMA_ALPHA,
                linewidth=0,
                zorder=11,
            )
            ax.fill_between(
                retrieved["wavelength"],
                retrieved["q16"],
                retrieved["q84"],
                color=retrieved_color,
                alpha=RETRIEVED_1SIGMA_ALPHA,
                linewidth=0,
                zorder=12,
            )
            ax.plot(
                retrieved["wavelength"],
                retrieved["median"],
                color=retrieved_color,
                linewidth=2.0,
                alpha=RETRIEVED_MEDIAN_ALPHA,
                zorder=20,
            )

            truth = resample_truth_spectrum(products["truth"][scenario], target_wavelength)
            observed = products["observations"][(scenario, hours)]
            observed_mask = spectrum_band_mask(observed["wavelength"])
            ax.errorbar(
                observed["wavelength"][observed_mask],
                observed["flux"][observed_mask],
                yerr=observed["sigma"][observed_mask],
                xerr=observed["half_bin"][observed_mask],
                fmt="none",
                ecolor=OBSERVATION_COLORS[scenario],
                alpha=0.35,
                elinewidth=0.4,
                capsize=0,
                zorder=39,
            )
            plot_observation_markers(
                ax,
                observed,
                observed_mask,
                scenario,
                OBSERVATION_MARKERSIZE_GLOBAL,
                OBSERVATION_MARKER_EDGE_WIDTH_GLOBAL,
            )
            ax.plot(
                truth["wavelength"],
                truth["flux"],
                color=TRUE_COLORS[scenario],
                linewidth=1.0,
                alpha=TRUE_SPECTRUM_ALPHA,
                zorder=30,
            )

            arrays.extend(
                [
                    retrieved["q02"],
                    retrieved["q98"],
                    truth["flux"],
                    observed["flux"][observed_mask] - observed["sigma"][observed_mask],
                    observed["flux"][observed_mask] + observed["sigma"][observed_mask],
                ]
            )

        ax.set_xlim(*WAVELENGTH_RANGE)
        ax.set_ylim(*padded_limits(arrays, fraction=0.06, minimum_pad=0.25))
        ax.grid(False)
        ax.set_ylabel(flux_ylabel(), fontsize=11.5)
        ax.tick_params(direction="in", top=True, right=True, labelsize=10)
        ax.minorticks_on()
        ax.text(
            1.02,
            0.50,
            f"{hours} h",
            transform=ax.transAxes,
            fontsize=11.5,
            fontweight="bold",
            va="center",
            ha="left",
            rotation=-90,
        )

    axes[-1].set_xlabel(r"Wavelength [$\mu$m]", fontsize=12)
    fig.tight_layout(rect=[0, 0, 0.985, 0.89])
    add_comparison_legend(fig, "Proxima b LIFE Retrieval Performance")
    return fig


def plot_molecular_zooms(products: dict[str, dict]) -> plt.Figure:
    """Plot the three selected molecular windows for both integration times."""
    fig, axes = plt.subplots(2, 3, figsize=(13, 8), sharex="col")
    for row, hours in enumerate(HOURS):
        for col, (left, right, title) in enumerate(ZOOM_WINDOWS):
            ax = axes[row, col]
            arrays = []
            target_wavelength = np.linspace(left, right, ZOOM_DISPLAY_POINTS)
            for scenario in PLOT_SCENARIOS:
                retrieved = resample_retrieved_spectrum(
                    products["retrieved"][(scenario, hours)], target_wavelength
                )
                observed = products["observations"][(scenario, hours)]
                retrieved_color = RETRIEVED_COLORS[scenario]
                observed_mask = (observed["wavelength"] >= left) & (observed["wavelength"] <= right)

                ax.fill_between(
                    retrieved["wavelength"],
                    retrieved["q02"],
                    retrieved["q98"],
                    color=retrieved_color,
                    alpha=RETRIEVED_2SIGMA_ALPHA,
                    linewidth=0,
                    zorder=11,
                )
                ax.fill_between(
                    retrieved["wavelength"],
                    retrieved["q16"],
                    retrieved["q84"],
                    color=retrieved_color,
                    alpha=RETRIEVED_1SIGMA_ALPHA,
                    linewidth=0,
                    zorder=12,
                )
                ax.plot(
                    retrieved["wavelength"],
                    retrieved["median"],
                    color=retrieved_color,
                    linewidth=2.0,
                    alpha=RETRIEVED_MEDIAN_ALPHA,
                    zorder=20,
                )
                ax.errorbar(
                    observed["wavelength"][observed_mask],
                    observed["flux"][observed_mask],
                    yerr=observed["sigma"][observed_mask],
                    xerr=observed["half_bin"][observed_mask],
                    fmt="none",
                    ecolor=OBSERVATION_COLORS[scenario],
                    alpha=0.70,
                    elinewidth=0.6,
                    capsize=1.0,
                    zorder=39,
                )
                plot_observation_markers(
                    ax,
                    observed,
                    observed_mask,
                    scenario,
                    OBSERVATION_MARKERSIZE_ZOOM,
                    OBSERVATION_MARKER_EDGE_WIDTH_ZOOM,
                )

                truth = resample_truth_spectrum(
                    products["truth"][scenario], target_wavelength
                )
                ax.plot(
                    truth["wavelength"],
                    truth["flux"],
                    color=TRUE_COLORS[scenario],
                    linewidth=1.0,
                    alpha=TRUE_SPECTRUM_ALPHA,
                    zorder=30,
                )
                arrays.extend(
                    [
                        retrieved["q02"],
                        retrieved["q98"],
                        truth["flux"],
                        observed["flux"][observed_mask] - observed["sigma"][observed_mask],
                        observed["flux"][observed_mask] + observed["sigma"][observed_mask],
                    ]
                )

            ax.set_xlim(left, right)
            ax.set_ylim(*padded_limits(arrays, fraction=0.08, minimum_pad=0.12))
            ax.grid(alpha=0.12, which="both", linestyle="--")
            ax.tick_params(direction="in", top=True, right=True, labelsize=9.5)
            ax.minorticks_on()
            if row == 0:
                ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
            if col == 0:
                ax.set_ylabel(flux_ylabel(), fontsize=10.5)
            if col == len(ZOOM_WINDOWS) - 1:
                ax.text(
                    1.05,
                    0.50,
                    f"{hours} h",
                    transform=ax.transAxes,
                    fontsize=11.5,
                    fontweight="bold",
                    va="center",
                    ha="left",
                    rotation=-90,
                )
            if row == len(HOURS) - 1:
                ax.set_xlabel(r"Wavelength [$\mu$m]", fontsize=10.5)

    fig.tight_layout(rect=[0, 0, 0.985, 0.89])
    add_comparison_legend(
        fig, "Proxima b LIFE retrievals in selected molecular bands"
    )
    return fig


def profile_x_limits(
    products: dict[str, dict],
    posterior_samples: dict[int, np.ndarray] | None = None,
) -> dict[str, tuple[float, float]]:
    """Set limits for the A3 posterior, profile, and effective A0 marker."""
    if posterior_samples is None:
        posterior_samples = {
            hours: products["samples"][(PROFILE_POSTERIOR_SCENARIO, hours)]
            for hours in HOURS
        }
    limits = {}
    for molecule in MOLECULES:
        posterior = []
        reference = []
        reference.append(
            np.log10(
                np.clip(
                    products["profiles"][PROFILE_POSTERIOR_SCENARIO][molecule],
                    PROFILE_FLOOR,
                    None,
                )
            )
        )
        reference.append(
            np.asarray(
                [
                    log10_column_averaged_mixing_ratio(
                        products["profiles"][PROFILE_REFERENCE_SCENARIO], molecule
                    )
                ]
            )
        )
        for samples in posterior_samples.values():
            posterior.append(samples[:, SAMPLE_INDEX[molecule]])
        post = finite_values(posterior)
        ref = finite_values(reference)
        lower = min(float(np.percentile(post, 0.5)), float(np.percentile(ref, 1.0))) - 0.25
        upper = max(float(np.percentile(post, 99.5)), float(np.percentile(ref, 99.0))) + 0.25
        # The retrieval priors bottom out close to -12 dex.  A hard display
        # floor keeps ultra-trace VULCAN values from flattening all histograms.
        lower = max(-13.0, lower)
        upper = min(0.0, upper)
        if upper - lower < 1.0:
            upper = lower + 1.0
        limits[molecule] = (lower, upper)
    return limits


def posterior_summary(values: np.ndarray) -> dict[str, float]:
    """Summarize one marginal posterior using the transmission-plot metrics."""
    q16, q50, q84 = np.percentile(values, [16.0, 50.0, 84.0])
    return {
        "median": float(q50),
        "sigma68": float(0.5 * (q84 - q16)),
    }


def signed_reference_distance(summary: dict[str, float], reference: float) -> float:
    """Return signed A3-minus-A0 separation in units of A3's 68% width."""
    sigma = summary["sigma68"]
    if sigma == 0.0:
        return float("nan")
    return (summary["median"] - reference) / sigma


def add_profile_metrics(
    ax: plt.Axes,
    x_limits: tuple[float, float],
    summary: dict[str, float],
    a0_reference: float,
) -> None:
    """Add A3 posterior and signed distance to the effective A0 reference."""
    distance = signed_reference_distance(summary, a0_reference)
    metrics_lines = [
        TextArea(
            rf"A3 = {summary['median']:.2f} $\pm$ {summary['sigma68']:.2f} dex",
            textprops={"color": RETRIEVED_COLORS[PROFILE_POSTERIOR_SCENARIO], "fontsize": 7.5},
        ),
        TextArea(
            rf"A0 ref. = {a0_reference:.2f} dex",
            textprops={"color": TRUE_COLORS[PROFILE_REFERENCE_SCENARIO], "fontsize": 7.2},
        ),
        TextArea(
            rf"$z_{{A3|A0}}$ = {distance:+.2f}$\sigma$",
            textprops={"color": PALETTE["dark_amaranth"], "fontsize": 7.2},
        ),
    ]
    posterior_center = summary["median"]
    x_mid = 0.5 * (x_limits[0] + x_limits[1])
    metrics_loc = "upper right" if posterior_center < x_mid else "upper left"
    metrics_anchor = (0.97, 0.965) if metrics_loc == "upper right" else (0.035, 0.965)
    metrics_pack = VPacker(children=metrics_lines, align="left", pad=0.0, sep=1.2)
    metrics_box = AnchoredOffsetbox(
        loc=metrics_loc,
        child=metrics_pack,
        pad=0.16,
        borderpad=0.30,
        frameon=True,
        bbox_to_anchor=metrics_anchor,
        bbox_transform=ax.transAxes,
    )
    metrics_box.patch.set_boxstyle("round,pad=0.20")
    metrics_box.patch.set_facecolor("white")
    metrics_box.patch.set_edgecolor("0.86")
    metrics_box.patch.set_linewidth(0.6)
    metrics_box.patch.set_alpha(0.90)
    metrics_box.set_zorder(20)
    ax.add_artist(metrics_box)


def plot_profiles_posteriors(
    products: dict[str, dict],
    posterior_hours: tuple[int, ...] = HOURS,
    posterior_samples: dict[int, np.ndarray] | None = None,
    title: str = "Proxima b: A3 Retrieval Relative to the A0 Reference",
) -> plt.Figure:
    """Plot marginal abundance posteriors and vertical reference profiles."""
    if posterior_samples is None:
        posterior_samples = {
            hours: products["samples"][(PROFILE_POSTERIOR_SCENARIO, hours)]
            for hours in posterior_hours
        }
    limits = profile_x_limits(products, posterior_samples)
    n_rows = len(posterior_hours)
    n_cols = len(MOLECULES)
    # Keep the compact transmission-like grid, reserving a clean header for the
    # title, horizontal line-semantics legend, and distance formula.
    fig = plt.figure(figsize=(2.78 * n_cols, 2.35 * n_rows))
    outer = fig.add_gridspec(
        n_rows,
        n_cols,
        left=0.068,
        right=0.985,
        bottom=0.055,
        top=0.83,
        wspace=0.11,
        hspace=0.20,
    )

    a3_profile_color = TRUE_COLORS[PROFILE_POSTERIOR_SCENARIO]
    a3_posterior_color = RETRIEVED_COLORS[PROFILE_POSTERIOR_SCENARIO]
    a0_effective_color = TRUE_COLORS[PROFILE_REFERENCE_SCENARIO]
    legend_handles = [
        Line2D([], [], color=a3_profile_color, lw=2.1, label="A3 VULCAN profile"),
        Line2D([], [], color=a3_posterior_color, lw=1.7, ls="--", label="A3 posterior median"),
        Line2D(
            [], [], color=a0_effective_color, lw=1.3, ls=":",
            label="A0 effective reference",
        ),
    ]
    for row, hours in enumerate(posterior_hours):
        for col, molecule in enumerate(MOLECULES):
            ax = fig.add_subplot(outer[row, col])
            ax_profile = ax.twinx()
            ax.set_zorder(2)
            ax_profile.set_zorder(1)
            ax.patch.set_alpha(0.0)

            left, right = limits[molecule]
            bin_edges = np.linspace(left, right, 28)
            values = posterior_samples[hours][:, SAMPLE_INDEX[molecule]]
            summary = posterior_summary(values)
            ax.hist(
                values,
                bins=bin_edges,
                density=True,
                histtype="stepfilled",
                color=a3_posterior_color,
                edgecolor=a3_posterior_color,
                linewidth=0.9,
                alpha=0.28,
                zorder=1,
            )
            ax.axvline(
                summary["median"],
                color=a3_posterior_color,
                lw=1.7,
                ls="--",
                alpha=0.95,
                zorder=4,
            )
            a0_reference = log10_column_averaged_mixing_ratio(
                products["profiles"][PROFILE_REFERENCE_SCENARIO], molecule
            )
            ax.axvline(
                a0_reference,
                color=a0_effective_color,
                lw=1.3,
                ls=":",
                alpha=0.90,
                zorder=5,
            )

            reference = products["profiles"][PROFILE_POSTERIOR_SCENARIO]
            ax_profile.plot(
                np.log10(np.clip(reference[molecule], PROFILE_FLOOR, None)),
                reference["PRESS"],
                color=a3_profile_color,
                lw=2.1,
                alpha=0.98,
                zorder=6,
            )

            ax.set_xlim(left, right)
            ax.set_ylim(bottom=0.0)
            ax.grid(axis="y", alpha=0.22, linestyle=":")
            ax.tick_params(direction="in", top=True, right=True, labelsize=8.3)
            ax.minorticks_on()

            ax_profile.set_yscale("log")
            ax_profile.set_ylim(1.0, 5.0e-8)
            ax_profile.tick_params(axis="y", direction="in", labelsize=8.0)
            ax_profile.spines["top"].set_visible(False)
            ax_profile.spines["left"].set_visible(False)
            ax_profile.spines["bottom"].set_visible(False)
            ax_profile.spines["right"].set_visible(col == n_cols - 1)
            if col != n_cols - 1:
                ax_profile.set_yticks([])
                ax_profile.set_yticks([], minor=True)
                ax_profile.tick_params(axis="y", right=False, labelright=False)

            post_ymax = ax.get_ylim()[1]
            ax.errorbar(
                summary["median"],
                0.11 * post_ymax,
                xerr=summary["sigma68"],
                fmt="s",
                ms=3.5,
                color=a3_posterior_color,
                markerfacecolor=a3_posterior_color,
                markeredgecolor="black",
                markeredgewidth=0.3,
                elinewidth=1.1,
                capsize=2.3,
                zorder=7,
            )
            add_profile_metrics(ax, (left, right), summary, a0_reference)

            if row == 0:
                ax.set_title(MOLECULE_LABELS[molecule], fontsize=13, pad=6)
            if col == 0:
                ax.set_ylabel("Probability density")
                ax.text(
                    -0.60,
                    0.50,
                    f"{hours} h",
                    transform=ax.transAxes,
                    rotation=90,
                    va="center",
                    ha="center",
                    fontsize=10.5,
                    fontweight="bold",
                )
            else:
                ax.tick_params(axis="y", labelleft=False)
            if row == n_rows - 1:
                ax.set_xlabel(PROFILE_X_AXIS_LABELS[molecule])
            else:
                ax.tick_params(axis="x", labelbottom=False)
            if col == n_cols - 1:
                ax_profile.tick_params(axis="y", which="both", right=True, labelright=True)
                ax_profile.set_ylabel("Pressure [bar]")

    fig.legend(
        legend_handles,
        [handle.get_label() for handle in legend_handles],
        loc="upper center",
        ncol=3,
        frameon=False,
        handlelength=2.0,
        fontsize=9.5,
        labelspacing=0.35,
        columnspacing=1.8,
        handletextpad=0.55,
        bbox_to_anchor=(0.5, 0.962),
    )
    fig.suptitle(
        title,
        y=0.995,
        fontsize=16,
    )
    fig.text(
        0.90,
        0.950,
        r"$z_{A3|A0}=\dfrac{\mu_{A3}-\log_{10}(X_{A0,\mathrm{eff}})}{\sigma_{A3}}$",
        color=PALETTE["charcoal_violet"],
        ha="right",
        va="top",
        fontsize=9.2,
        bbox={
            "boxstyle": "round,pad=0.25",
            "facecolor": "white",
            "edgecolor": PALETTE["charcoal_violet"],
            "linewidth": 0.6,
            "alpha": 0.88,
        },
    )
    return fig


def load_four_row_audit_posterior_samples() -> dict[int, np.ndarray]:
    """Load canonical and robust audit A3 posteriors for a four-row figure."""
    audit_tag = "_robust_lifesim_direct"
    return {
        10: load_samples("A3", 10),
        240: load_samples("A3", 240),
        500: load_samples("A3", 500, audit_tag),
        1200: load_samples("A3", 1200, audit_tag),
    }


def save_figure(fig: plt.Figure, stem: str, output_dir: Path) -> tuple[Path, Path]:
    """Write the requested PNG and PDF pair and close the figure."""
    output_dir.mkdir(parents=True, exist_ok=True)
    png_path = output_dir / f"{stem}.png"
    pdf_path = output_dir / f"{stem}.pdf"
    fig.savefig(png_path, dpi=240, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {png_path.relative_to(REPO)}")
    print(f"saved {pdf_path.relative_to(REPO)}")
    return png_path, pdf_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PLOTS_DIR,
        help="Directory for the PNG/PDF pairs (default: campaign plots directory).",
    )
    parser.add_argument(
        "--four-row-audit-output",
        type=Path,
        default=None,
        help="Optional directory for the four-row 10/240/500/1200 h audit posterior figure.",
    )
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    four_row_audit_output = (
        args.four_row_audit_output.resolve()
        if args.four_row_audit_output is not None
        else None
    )

    products = load_campaign_products()
    pilot_spectrum = SAMPLES_DIR / f"{retrieval_stem('A3', 1200)}_spectrum_retrieved.txt"
    if pilot_spectrum.exists():
        print("[info] A3-1200h retrieval found; classified as excluded pilot, not plotted in the canonical figures.")
    print("[info] loaded canonical retrieval products for plotted extremes: A0/A3 x {10 h, 240 h} = 4 retrievals")

    save_figure(plot_global_spectra(products), "retrieval_global_spectra_proxima", output_dir)
    save_figure(plot_molecular_zooms(products), "retrieval_molecular_zooms_proxima", output_dir)
    save_figure(plot_profiles_posteriors(products), "retrieval_profiles_posteriors_proxima", output_dir)
    if four_row_audit_output is not None:
        audit_samples = load_four_row_audit_posterior_samples()
        save_figure(
            plot_profiles_posteriors(
                products,
                posterior_hours=(10, 240, 500, 1200),
                posterior_samples=audit_samples,
                title="Proxima b: A3 Posterior by Integration Time",
            ),
            "retrieval_profiles_posteriors_proxima_4rows_audit",
            four_row_audit_output,
        )


if __name__ == "__main__":
    main()
