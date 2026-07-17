"""Plot the complete corrected A0/A3 retrieval campaign.

The two spectral figures preserve the historic comparison at total observing
budgets of 10 and 100 transits.  In the optimized campaign these correspond to
5+5 and 50+50 joint NIRSpec+MIRI transits.  The posterior grid includes every
campaign configuration as one row.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D


BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parents[1]
sys.path.insert(0, str(BASE_DIR))

from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE
from plot_pure_transmission_spectra import compute_system_spectra


OUTPUT_DIR = BASE_DIR / "POSEIDON_output" / "TRAPPIST-1e"
SAMPLES_DIR = OUTPUT_DIR / "retrievals" / "samples"
SYNTHETIC_DIR = OUTPUT_DIR / "synthetic_data" / "base_1transit"
PLOTS_DIR = OUTPUT_DIR / "plots"
FINAL_DIR = REPO_ROOT / "Transmission_Spectroscopy" / "final_products" / "figures"

SCENARIOS = ("A0", "A3")
SCENARIO_STEMS = {"A0": "Trappist_A0_PreAgri", "A3": "Trappist_A3_Extreme"}
SCENARIO_LABELS = {"A0": "A0: pre-agricultural", "A3": "A3: extreme ExoFarm"}
SCENARIO_COLORS = {"A0": PALETTE["scenario_green"], "A3": PALETTE["scenario_pink"]}
TRUTH_COLORS = {"A0": PALETTE["deep_moss"], "A3": PALETTE["dark_amaranth"]}

# Each row is one of the 18 completed A0/A3 retrievals, represented by its
# observing configuration.  "both" counts are per instrument.
CAMPAIGN = (
    ("10 MIRI", 10, "MIRI"),
    ("10 NIRSpec", 10, "NIRSpec"),
    ("10 total (5+5)", 5, "NIRSpec_MIRI"),
    ("100 MIRI", 100, "MIRI"),
    ("100 NIRSpec", 100, "NIRSpec"),
    ("100 total (50+50)", 50, "NIRSpec_MIRI"),
    ("200 MIRI", 200, "MIRI"),
    ("200 NIRSpec", 200, "NIRSpec"),
    ("200 total (100+100)", 100, "NIRSpec_MIRI"),
)
SPECTRAL_COMPARISON = (
    ("5 NIRSpec + 5 MIRI (10 total)", 5),
    ("50 NIRSpec + 50 MIRI (100 total)", 50),
)
ZOOM_WINDOWS = (
    (r"N$_2$O band (2.6–3.0 $\mu$m)", 2.6, 3.0),
    (r"N$_2$O band (8.2–9.0 $\mu$m)", 8.2, 9.0),
    (r"NH$_3$ band (10.6–11.7 $\mu$m)", 10.6, 11.7),
)


def stem(scenario: str, transits: int, suffix: str) -> str:
    return f"TRAPPIST1e_{scenario}_retrieval_isotherm_isochem_{transits}transits_{suffix}"


def spectrum_path(scenario: str, transits: int) -> Path:
    return SAMPLES_DIR / f"{stem(scenario, transits, 'NIRSpec_MIRI')}_spectrum_retrieved.txt"


def sample_path(scenario: str, transits: int, suffix: str) -> Path:
    return SAMPLES_DIR / f"{stem(scenario, transits, suffix)}_samples.txt"


def observation_path(scenario: str, instrument: str, transits: int) -> Path:
    instrument_stem = {"NIRSpec": "JWST_NIRSpec_PRISM", "MIRI": "JWST_MIRI_LRS"}[instrument]
    return SYNTHETIC_DIR / f"TRAPPIST-1e_SYNTHETIC_{instrument_stem}_{SCENARIO_STEMS[scenario]}_N_trans_{transits}.dat"


def load_spectrum(path: Path) -> dict[str, np.ndarray]:
    values = np.loadtxt(path, skiprows=1)
    return {
        "wl": values[:, 0], "minus_2": values[:, 1] * 1e6,
        "minus_1": values[:, 2] * 1e6, "median": values[:, 3] * 1e6,
        "plus_1": values[:, 4] * 1e6, "plus_2": values[:, 5] * 1e6,
    }


def load_observations(scenario: str, transits: int) -> list[dict[str, np.ndarray]]:
    output = []
    for instrument in ("NIRSpec", "MIRI"):
        values = np.loadtxt(observation_path(scenario, instrument, transits))
        output.append({"wl": values[:, 0], "depth": values[:, 2] * 1e6, "error": values[:, 3] * 1e6})
    return output


def load_samples(path: Path) -> dict[str, np.ndarray]:
    with path.open(encoding="utf-8") as handle:
        header = [item.strip() for item in handle.readline().split("|")]
    values = np.loadtxt(path, skiprows=1)
    return {name: values[:, idx] for idx, name in enumerate(header)}


def save_figure(figure: plt.Figure, name: str) -> None:
    for directory in (PLOTS_DIR, FINAL_DIR):
        directory.mkdir(parents=True, exist_ok=True)
        figure.savefig(directory / f"{name}.png", dpi=260, bbox_inches="tight")
        figure.savefig(directory / f"{name}.pdf", bbox_inches="tight")


def add_spectrum(ax: plt.Axes, spectra, observations, truth, x_min: float, x_max: float) -> None:
    grid = np.linspace(x_min, x_max, 400)
    limits = []
    for scenario in SCENARIOS:
        spectrum = spectra[scenario]
        color = SCENARIO_COLORS[scenario]
        lower2, lower1, median, upper1, upper2 = (
            np.interp(grid, spectrum["wl"], spectrum[key])
            for key in ("minus_2", "minus_1", "median", "plus_1", "plus_2")
        )
        ax.fill_between(grid, lower2, upper2, color=color, alpha=0.13, lw=0, zorder=2)
        ax.fill_between(grid, lower1, upper1, color=color, alpha=0.28, lw=0, zorder=3)
        ax.plot(grid, median, color=color, lw=1.9, zorder=4)
        ax.plot(grid, np.interp(grid, truth[scenario]["wl"], truth[scenario]["depth"]),
                color=TRUTH_COLORS[scenario], lw=1.05, ls="--", zorder=5)
        limits.extend((lower2, upper2))
        # Preserve the historic visual treatment: uncertainty bars, not a marker
        # at every synthetic wavelength bin.
        for observed in observations[scenario]:
            mask = (observed["wl"] >= x_min) & (observed["wl"] <= x_max)
            ax.errorbar(observed["wl"][mask], observed["depth"][mask], yerr=observed["error"][mask],
                        fmt="none", color=TRUTH_COLORS[scenario], ecolor=TRUTH_COLORS[scenario],
                        alpha=0.28, elinewidth=0.42, capsize=0, zorder=1)
            limits.append(observed["depth"][mask])
    low, high = np.percentile(np.concatenate(limits), [0.5, 99.5])
    padding = max(9.0, 0.12 * (high - low))
    ax.set(xlim=(x_min, x_max), ylim=(low - padding, high + padding))
    ax.grid(alpha=0.15, ls=":")


def make_spectral_comparisons(truth) -> None:
    cache = {}
    for label, transits in SPECTRAL_COMPARISON:
        cache[transits] = {
            "spectra": {scenario: load_spectrum(spectrum_path(scenario, transits)) for scenario in SCENARIOS},
            "observations": {scenario: load_observations(scenario, transits) for scenario in SCENARIOS},
            "label": label,
        }
    handles = [
        Line2D([], [], color=SCENARIO_COLORS[scenario], lw=2, label=f"Retrieved {scenario}")
        for scenario in SCENARIOS
    ] + [
        Line2D([], [], color=TRUTH_COLORS[scenario], lw=1.1, ls="--", label=f"Input {scenario}")
        for scenario in SCENARIOS
    ]
    fig, axes = plt.subplots(2, 3, figsize=(14, 7.0))
    for row, (_, transits) in enumerate(SPECTRAL_COMPARISON):
        for col, (title, x_min, x_max) in enumerate(ZOOM_WINDOWS):
            ax = axes[row, col]
            add_spectrum(ax, cache[transits]["spectra"], cache[transits]["observations"], truth, x_min, x_max)
            if row == 0:
                ax.set_title(title)
            if row == 1:
                ax.set_xlabel(r"Wavelength ($\mu$m)")
            if col == 0:
                ax.set_ylabel(r"Transit depth (ppm)\n" + cache[transits]["label"])
    fig.legend(handles=handles, ncol=4, loc="upper center", bbox_to_anchor=(0.5, 0.985), frameon=False)
    fig.suptitle("TRAPPIST-1e retrievals in diagnostic molecular bands", y=1.04)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    save_figure(fig, "trappist_retrieval_bands_A0_A3_10_100total")
    plt.close(fig)

    fig, axes = plt.subplots(2, 1, figsize=(12, 7.0), sharex=True)
    for ax, (_, transits) in zip(axes, SPECTRAL_COMPARISON):
        add_spectrum(ax, cache[transits]["spectra"], cache[transits]["observations"], truth, 0.6, 12.0)
        ax.set_ylabel(r"Transit depth (ppm)\n" + cache[transits]["label"])
    axes[-1].set_xlabel(r"Wavelength ($\mu$m)")
    axes[0].set_title("TRAPPIST-1e joint NIRSpec+MIRI retrievals")
    axes[0].legend(handles=handles, ncol=2, loc="best", frameon=False, fontsize=9)
    fig.tight_layout()
    save_figure(fig, "trappist_retrieval_total_A0_A3_10_100total")
    plt.close(fig)


def make_campaign_posterior_grid() -> None:
    molecules = ("H2O", "CO2", "CH4", "O2", "O3", "N2O", "NH3")
    display = {"H2O": r"H$_2$O", "CO2": r"CO$_2$", "CH4": r"CH$_4$", "O2": r"O$_2$", "O3": r"O$_3$", "N2O": r"N$_2$O", "NH3": r"NH$_3$"}
    samples = {(scenario, label): load_samples(sample_path(scenario, transits, suffix))
               for label, transits, suffix in CAMPAIGN for scenario in SCENARIOS}
    fig, axes = plt.subplots(len(CAMPAIGN), len(molecules), figsize=(18, 17.5), squeeze=False)
    for row, (label, _, _) in enumerate(CAMPAIGN):
        for col, molecule in enumerate(molecules):
            ax = axes[row, col]
            values = [samples[(scenario, label)][f"log_{molecule}"] for scenario in SCENARIOS]
            low, high = np.percentile(np.concatenate(values), [0.5, 99.5])
            padding = max(0.3, 0.12 * (high - low))
            edges = np.linspace(low - padding, high + padding, 30)
            for scenario, posterior in zip(SCENARIOS, values):
                color = SCENARIO_COLORS[scenario]
                ax.hist(posterior, bins=edges, density=True, histtype="stepfilled", color=color,
                        edgecolor=color, alpha=0.30, lw=0.85)
                ax.axvline(np.median(posterior), color=color, ls="--", lw=1.35)
            if row == 0:
                ax.set_title(display[molecule], fontsize=12)
            if col == 0:
                ax.set_ylabel(label + "\nposterior density", fontsize=8.5)
            ax.set_ylim(bottom=0)
            ax.grid(axis="y", alpha=0.16, ls=":")
            ax.tick_params(labelsize=7.5)
    handles = [Line2D([], [], color=SCENARIO_COLORS[scenario], lw=2, label=SCENARIO_LABELS[scenario]) for scenario in SCENARIOS]
    fig.legend(handles=handles, ncol=2, loc="upper center", bbox_to_anchor=(0.5, 0.995), frameon=False)
    fig.suptitle("TRAPPIST-1e marginal abundance posteriors across the completed retrieval campaign", y=1.012)
    fig.tight_layout(rect=(0.07, 0, 1, 0.985))
    save_figure(fig, "trappist_retrieval_posteriors_A0_A3_all_campaigns")
    plt.close(fig)


def main() -> None:
    os.chdir(BASE_DIR)
    required = [sample_path(scenario, transits, suffix) for _, transits, suffix in CAMPAIGN for scenario in SCENARIOS]
    required += [spectrum_path(scenario, transits) for _, transits in SPECTRAL_COMPARISON for scenario in SCENARIOS]
    missing = [path for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing campaign products:\n" + "\n".join(map(str, missing)))
    wavelength, spectra = compute_system_spectra("TRAPPIST-1e", 0.6, 12.0, 3000)
    truth = {scenario: {"wl": wavelength, "depth": spectra[scenario] * 1e6} for scenario in SCENARIOS}
    make_spectral_comparisons(truth)
    # The profile-aware posterior grid is generated by plot_profile_posterior_comparison.py.


if __name__ == "__main__":
    main()
