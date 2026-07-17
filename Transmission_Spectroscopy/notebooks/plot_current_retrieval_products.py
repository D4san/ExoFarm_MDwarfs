"""Create the three presentation figures for the completed A0/A3 retrieval pair.

The figures use the joint NIRSpec+MIRI retrievals with 100 transits in each
instrument.  They intentionally leave the older 5/50-transit figures intact as
campaign evidence.
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
TRANSITS_PER_INSTRUMENT = 100
SCENARIO_FILE_STEMS = {"A0": "Trappist_A0_PreAgri", "A3": "Trappist_A3_Extreme"}
SCENARIO_LABELS = {"A0": "A0: pre-agricultural", "A3": "A3: extreme ExoFarm"}
RETRIEVED_COLORS = {"A0": PALETTE["scenario_green"], "A3": PALETTE["scenario_pink"]}
TRUE_COLORS = {"A0": PALETTE["deep_moss"], "A3": PALETTE["dark_amaranth"]}
MARKERS = {"A0": "o", "A3": "D"}
ZOOM_WINDOWS = (
    (r"N$_2$O band (2.6–3.0 $\mu$m)", 2.6, 3.0),
    (r"N$_2$O band (8.2–9.0 $\mu$m)", 8.2, 9.0),
    (r"NH$_3$ band (10.6–11.7 $\mu$m)", 10.6, 11.7),
)


def retrieval_spectrum_path(scenario: str) -> Path:
    return SAMPLES_DIR / (
        f"TRAPPIST1e_{scenario}_retrieval_isotherm_isochem_"
        f"{TRANSITS_PER_INSTRUMENT}transits_NIRSpec_MIRI_spectrum_retrieved.txt"
    )


def observation_path(scenario: str, instrument: str) -> Path:
    instrument_name = {"NIRSpec": "JWST_NIRSpec_PRISM", "MIRI": "JWST_MIRI_LRS"}[instrument]
    return SYNTHETIC_DIR / (
        f"TRAPPIST-1e_SYNTHETIC_{instrument_name}_"
        f"{SCENARIO_FILE_STEMS[scenario]}_N_trans_{TRANSITS_PER_INSTRUMENT}.dat"
    )


def load_retrieved_spectrum(path: Path) -> dict[str, np.ndarray]:
    data = np.loadtxt(path, skiprows=1)
    return {
        "wavelength": data[:, 0],
        "minus_2sigma": data[:, 1] * 1.0e6,
        "minus_1sigma": data[:, 2] * 1.0e6,
        "median": data[:, 3] * 1.0e6,
        "plus_1sigma": data[:, 4] * 1.0e6,
        "plus_2sigma": data[:, 5] * 1.0e6,
    }


def load_observations(scenario: str) -> list[dict[str, np.ndarray]]:
    observations = []
    for instrument in ("NIRSpec", "MIRI"):
        path = observation_path(scenario, instrument)
        data = np.loadtxt(path)
        observations.append({
            "wavelength": data[:, 0],
            "wavelength_error": data[:, 1],
            "depth": data[:, 2] * 1.0e6,
            "depth_error": data[:, 3] * 1.0e6,
        })
    return observations


def interpolate_spectrum(spectrum: dict[str, np.ndarray], wavelength: np.ndarray) -> dict[str, np.ndarray]:
    return {key: np.interp(wavelength, spectrum["wavelength"], values)
            for key, values in spectrum.items() if key != "wavelength"} | {"wavelength": wavelength}


def save_figure(fig: plt.Figure, stem: str) -> None:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    for directory in (PLOTS_DIR, FINAL_DIR):
        for suffix, kwargs in (("png", {"dpi": 260}), ("pdf", {})):
            destination = directory / f"{stem}.{suffix}"
            fig.savefig(destination, bbox_inches="tight", **kwargs)
            print(f"Saved: {destination}")


def plot_retrieval(ax: plt.Axes, retrieved: dict[str, dict[str, np.ndarray]], observations, truth, x_min: float, x_max: float) -> None:
    wavelength = np.linspace(x_min, x_max, 500)
    plotted = []
    for scenario in SCENARIOS:
        fit = interpolate_spectrum(retrieved[scenario], wavelength)
        color = RETRIEVED_COLORS[scenario]
        ax.fill_between(wavelength, fit["minus_2sigma"], fit["plus_2sigma"], color=color, alpha=0.13, lw=0)
        ax.fill_between(wavelength, fit["minus_1sigma"], fit["plus_1sigma"], color=color, alpha=0.30, lw=0)
        ax.plot(wavelength, fit["median"], color=color, lw=2.0, zorder=3)
        ax.plot(wavelength, np.interp(wavelength, truth[scenario]["wl"], truth[scenario]["depth"]),
                color=TRUE_COLORS[scenario], lw=1.05, ls="--", zorder=4)
        for observation in observations[scenario]:
            mask = (observation["wavelength"] >= x_min) & (observation["wavelength"] <= x_max)
            if np.any(mask):
                ax.errorbar(observation["wavelength"][mask], observation["depth"][mask],
                            yerr=observation["depth_error"][mask], fmt=MARKERS[scenario], ms=2.7,
                            color=TRUE_COLORS[scenario], ecolor=TRUE_COLORS[scenario], alpha=0.48,
                            elinewidth=0.45, capsize=0, ls="none", zorder=5)
                plotted.extend(observation["depth"][mask])
        plotted.extend(fit["minus_2sigma"])
        plotted.extend(fit["plus_2sigma"])
    low, high = np.percentile(plotted, [0.5, 99.5])
    pad = max(10.0, 0.12 * (high - low))
    ax.set(xlim=(x_min, x_max), ylim=(low - pad, high + pad))
    ax.grid(alpha=0.16, ls=":")


def make_spectral_figures(retrieved, observations, truth) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(14.0, 4.0))
    for ax, (title, x_min, x_max) in zip(axes, ZOOM_WINDOWS):
        plot_retrieval(ax, retrieved, observations, truth, x_min, x_max)
        ax.set_title(title)
        ax.set_xlabel(r"Wavelength ($\mu$m)")
    axes[0].set_ylabel(r"Transit depth $(R_p/R_s)^2$ (ppm)")
    handles = []
    for scenario in SCENARIOS:
        handles.extend((
            Line2D([], [], color=RETRIEVED_COLORS[scenario], lw=2.2, label=f"Retrieved {scenario}"),
            Line2D([], [], color=TRUE_COLORS[scenario], lw=1.1, ls="--", label=f"Input {scenario}"),
        ))
    fig.legend(handles=handles, loc="upper center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 1.04))
    fig.suptitle("TRAPPIST-1e retrievals in diagnostic molecular bands\nJoint NIRSpec+MIRI, 100+100 transits", y=1.12)
    fig.tight_layout()
    save_figure(fig, "trappist_current_retrieval_bands_A0_A3_100plus100")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12.0, 5.2))
    plot_retrieval(ax, retrieved, observations, truth, 0.6, 12.0)
    ax.set(xlabel=r"Wavelength ($\mu$m)", ylabel=r"Transit depth $(R_p/R_s)^2$ (ppm)")
    ax.set_title("TRAPPIST-1e joint NIRSpec+MIRI retrieval: full spectrum (100+100 transits)")
    ax.legend(handles=handles, loc="best", ncol=2, frameon=False, fontsize=9)
    fig.tight_layout()
    save_figure(fig, "trappist_current_retrieval_total_A0_A3_100plus100")
    plt.close(fig)


def load_posterior(path: Path) -> dict[str, np.ndarray]:
    with path.open(encoding="utf-8") as handle:
        header = [item.strip() for item in handle.readline().split("|")]
    data = np.loadtxt(path, skiprows=1)
    return {name: data[:, index] for index, name in enumerate(header)}


def make_posterior_grid(posteriors: dict[str, dict[str, np.ndarray]]) -> None:
    molecules = ("H2O", "CO2", "CH4", "O2", "O3", "N2O", "NH3")
    labels = {
        "H2O": r"log(X$_{\mathrm{H_2O}}$)", "CO2": r"log(X$_{\mathrm{CO_2}}$)",
        "CH4": r"log(X$_{\mathrm{CH_4}}$)", "O2": r"log(X$_{\mathrm{O_2}}$)",
        "O3": r"log(X$_{\mathrm{O_3}}$)", "N2O": r"log(X$_{\mathrm{N_2O}}$)",
        "NH3": r"log(X$_{\mathrm{NH_3}}$)",
    }
    fig, axes = plt.subplots(1, len(molecules), figsize=(18.0, 3.45))
    for ax, molecule in zip(axes, molecules):
        values = [posteriors[scenario][f"log_{molecule}"] for scenario in SCENARIOS]
        lo, hi = np.percentile(np.concatenate(values), [0.5, 99.5])
        padding = max(0.35, 0.13 * (hi - lo))
        edges = np.linspace(lo - padding, hi + padding, 34)
        for scenario, sample in zip(SCENARIOS, values):
            color = RETRIEVED_COLORS[scenario]
            median = np.median(sample)
            ax.hist(sample, bins=edges, density=True, histtype="stepfilled", color=color, alpha=0.30,
                    edgecolor=color, lw=0.9, label=SCENARIO_LABELS[scenario])
            ax.axvline(median, color=color, lw=1.7, ls="--")
        ax.set_title(labels[molecule], fontsize=11)
        ax.set_xlabel("log mixing ratio")
        ax.set_ylim(bottom=0)
        ax.grid(axis="y", alpha=0.18, ls=":")
    axes[0].set_ylabel("Posterior density")
    axes[-1].legend(loc="upper left", bbox_to_anchor=(1.02, 1.02), frameon=False, fontsize=9)
    fig.suptitle("TRAPPIST-1e marginal abundance posteriors\nJoint NIRSpec+MIRI retrievals, 100+100 transits", y=1.10)
    fig.tight_layout()
    save_figure(fig, "trappist_current_retrieval_posteriors_A0_A3_100plus100")
    plt.close(fig)


def main() -> None:
    os.chdir(BASE_DIR)
    for scenario in SCENARIOS:
        for path in (retrieval_spectrum_path(scenario), observation_path(scenario, "NIRSpec"),
                     observation_path(scenario, "MIRI")):
            if not path.exists():
                raise FileNotFoundError(path)
    retrieved = {scenario: load_retrieved_spectrum(retrieval_spectrum_path(scenario)) for scenario in SCENARIOS}
    observations = {scenario: load_observations(scenario) for scenario in SCENARIOS}
    truth_wavelength, truth_spectra = compute_system_spectra("TRAPPIST-1e", 0.6, 12.0, 3000)
    truth = {
        scenario: {"wl": truth_wavelength, "depth": truth_spectra[scenario] * 1.0e6}
        for scenario in SCENARIOS
    }
    posteriors = {scenario: load_posterior(SAMPLES_DIR / (
        f"TRAPPIST1e_{scenario}_retrieval_isotherm_isochem_"
        f"{TRANSITS_PER_INSTRUMENT}transits_NIRSpec_MIRI_samples.txt")) for scenario in SCENARIOS}
    make_spectral_figures(retrieved, observations, truth)
    make_posterior_grid(posteriors)


if __name__ == "__main__":
    main()
