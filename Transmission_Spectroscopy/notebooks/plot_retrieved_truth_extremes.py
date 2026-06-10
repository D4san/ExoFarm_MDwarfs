from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE
from plot_pure_transmission_spectra import compute_system_spectra, rebin_curve


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "POSEIDON_output" / "TRAPPIST-1e"
RETRIEVAL_SAMPLES_DIR = OUTPUT_DIR / "retrievals" / "samples"
SYNTHETIC_DATA_DIR = OUTPUT_DIR / "synthetic_data" / "base_1transit"
PLOTS_DIR = OUTPUT_DIR / "plots"

SCENARIOS = ("A1", "A2", "A3")
TRANSITS = (10, 100)
INSTRUMENT = "NIRSpec_MIRI"
WL_MIN = 0.6
WL_MAX = 12.0
RETRIEVAL_TARGET_POINTS = 220

SCENARIO_LABELS = {
    "A0": "A0: Pre-agricultural",
    "A1": "A1: Current Earth",
    "A2": "A2: Moderate ExoFarm",
    "A3": "A3: Extreme ExoFarm",
}
SCENARIO_FILE_LABELS = {
    "A0": "Trappist_A0_PreAgri",
    "A1": "Trappist_A1_Current",
    "A2": "Trappist_A2_Moderate",
    "A3": "Trappist_A3_Extreme",
}
SCENARIO_COLOURS = {
    "A1": PALETTE["golden_orange"],
    "A2": PALETTE["deep_space_blue"],
    "A3": PALETTE["dark_amaranth"],
}
TRANSIT_STYLES = {
    10: {
        "colour": PALETTE["deep_space_blue"],
        "label": "Retrieved: 10 transits",
    },
    100: {
        "colour": PALETTE["golden_orange"],
        "label": "Retrieved: 100 transits",
    },
}
OBSERVATION_STYLES = {
    10: {
        "colour": PALETTE["dim_grey"],
        "alpha": 0.50,
        "label": "Synthetic observations: 10 transits",
    },
    100: {
        "colour": PALETTE["ink_black"],
        "alpha": 0.58,
        "label": "Synthetic observations: 100 transits",
    },
}
INSTRUMENT_FILE_LABELS = {
    "NIRSpec": "JWST_NIRSpec_PRISM",
    "MIRI": "JWST_MIRI_LRS",
}
TRUE_COLOURS = {
    "A0": "#39FF14",
    "A3": "#FF1493",
}


def retrieval_spectrum_path(scenario, transits):
    return RETRIEVAL_SAMPLES_DIR / (
        f"TRAPPIST1e_{scenario}_retrieval_isotherm_isochem_"
        f"{transits}transits_{INSTRUMENT}_spectrum_retrieved.txt"
    )


def synthetic_observation_path(scenario, instrument, transits):
    return SYNTHETIC_DATA_DIR / (
        f"TRAPPIST-1e_SYNTHETIC_{INSTRUMENT_FILE_LABELS[instrument]}_"
        f"{SCENARIO_FILE_LABELS[scenario]}_N_trans_{transits}.dat"
    )


def load_retrieved_spectrum(path):
    data = np.loadtxt(path, skiprows=1)
    return {
        "wl": data[:, 0],
        "minus_2": data[:, 1] * 1.0e6,
        "minus_1": data[:, 2] * 1.0e6,
        "median": data[:, 3] * 1.0e6,
        "plus_1": data[:, 4] * 1.0e6,
        "plus_2": data[:, 5] * 1.0e6,
    }


def load_synthetic_observations(scenario, transits):
    observations = []
    for instrument in ("NIRSpec", "MIRI"):
        path = synthetic_observation_path(scenario, instrument, transits)
        if not path.exists():
            continue
        data = np.loadtxt(path)
        observations.append(
            {
                "instrument": instrument,
                "wl": data[:, 0],
                "wl_err": data[:, 1],
                "depth": data[:, 2] * 1.0e6,
                "depth_err": data[:, 3] * 1.0e6,
            }
        )
    return observations


def available_retrieval_scenarios():
    scenarios = []
    for scenario in SCENARIOS:
        if any(retrieval_spectrum_path(scenario, n_obs).exists() for n_obs in TRANSITS):
            scenarios.append(scenario)
    return scenarios


def observation_wavelength_grid(scenario, transits):
    observations = load_synthetic_observations(scenario, transits)
    if not observations:
        raise FileNotFoundError(f"No synthetic observations found for {scenario}, {transits} transits.")
    wl = np.concatenate([observation["wl"] for observation in observations])
    return np.sort(wl)


def reference_observation_grid(scenario):
    for transits in TRANSITS:
        try:
            return observation_wavelength_grid(scenario, transits)
        except FileNotFoundError:
            continue
    raise FileNotFoundError(f"No synthetic observations found for {scenario}.")


def resample_curve(wl, values, target_wl):
    return np.interp(target_wl, wl, values)


def reduced_instrument_grid(scenario, transits, target_points=RETRIEVAL_TARGET_POINTS):
    wl = observation_wavelength_grid(scenario, transits)
    if len(wl) <= target_points:
        return wl
    indices = np.unique(np.linspace(0, len(wl) - 1, target_points, dtype=int))
    return wl[indices]


def resample_retrieved_spectrum(spec, target_wl):
    rebinned = {}
    for key in ("minus_2", "minus_1", "median", "plus_1", "plus_2"):
        rebinned[key] = resample_curve(spec["wl"], spec[key], target_wl)
    rebinned["wl"] = target_wl
    return rebinned


def prepare_truth_spectra():
    wl, spectra = compute_system_spectra("TRAPPIST-1e", WL_MIN, WL_MAX, native_r=10000.0)
    truth = {}
    for scenario, spectrum in spectra.items():
        truth[scenario] = {"wl": wl, "depth": spectrum * 1.0e6}
    return truth


def add_synthetic_observations(ax, scenario, transits, truth_depth):
    style = OBSERVATION_STYLES[transits]
    labelled = False
    for observation in load_synthetic_observations(scenario, transits):
        model_depth = np.interp(
            observation["wl"],
            truth_depth["wl"],
            truth_depth["depth"],
        )
        ax.errorbar(
            observation["wl"],
            model_depth,
            yerr=observation["depth_err"],
            fmt="none",
            mew=0.0,
            color=style["colour"],
            ecolor=style["colour"],
            alpha=style["alpha"],
            elinewidth=0.48,
            capsize=0,
            linestyle="none",
            label="_nolegend_",
            zorder=2,
        )
        labelled = True


def add_retrieved_spectrum(ax, scenario, transits, y_reference_values):
    retrieval_path = retrieval_spectrum_path(scenario, transits)
    if not retrieval_path.exists():
        return False

    target_wl = reduced_instrument_grid(scenario, transits)
    retrieved = resample_retrieved_spectrum(load_retrieved_spectrum(retrieval_path), target_wl)
    wl = retrieved["wl"]
    colour = TRANSIT_STYLES[transits]["colour"]
    y_reference_values.extend([retrieved["minus_2"], retrieved["plus_2"]])
    ax.fill_between(
        wl,
        retrieved["minus_2"],
        retrieved["plus_2"],
        color=colour,
        alpha=0.14,
        lw=0,
        label="_nolegend_",
        zorder=3,
    )
    ax.fill_between(
        wl,
        retrieved["minus_1"],
        retrieved["plus_1"],
        color=colour,
        alpha=0.26,
        lw=0,
        label="_nolegend_",
        zorder=4,
    )
    ax.plot(
        wl,
        retrieved["median"],
        color=colour,
        lw=1.65,
        alpha=0.84,
        label=TRANSIT_STYLES[transits]["label"],
        zorder=6,
    )
    return True


def style_single_axis(ax, y_reference_values):
    ax.set_xscale("log")
    ax.set_xlim(WL_MIN, WL_MAX)
    ax.set_xticks([0.6, 0.8, 1, 2, 3, 5, 8, 10, 12])
    ax.set_xticklabels(["0.6", "0.8", "1", "2", "3", "5", "8", "10", "12"])
    ax.grid(alpha=0.12, which="both", color=PALETTE["ink_black"])
    ax.tick_params(direction="in", top=True, right=True)
    ax.set_xlabel("Wavelength (micron)")
    ax.set_ylabel("Transit depth (ppm)")
    y_ref = np.concatenate(y_reference_values)
    y_low, y_high = np.nanpercentile(y_ref, [0.2, 99.8])
    y_pad = max(9.0, 0.08 * (y_high - y_low))
    ax.set_ylim(y_low - y_pad, y_high + y_pad)


def add_instrument_ranges(ax):
    y_min, y_max = ax.get_ylim()
    y = y_min + 0.035 * (y_max - y_min)
    text_y = y_min + 0.055 * (y_max - y_min)
    ax.hlines(y, WL_MIN, 5.3, color=PALETTE["deep_space_blue"], lw=1.1, alpha=0.85)
    ax.hlines(y, 5.3, WL_MAX, color=PALETTE["dark_amaranth"], lw=1.1, alpha=0.85)
    ax.text(
        np.sqrt(WL_MIN * 5.3),
        text_y,
        "NIRSpec Prism",
        ha="center",
        va="bottom",
        color=PALETTE["deep_space_blue"],
        fontsize=8,
    )
    ax.text(
        np.sqrt(5.3 * WL_MAX),
        text_y,
        "MIRI LRS",
        ha="center",
        va="bottom",
        color=PALETTE["dark_amaranth"],
        fontsize=8,
    )


def save_figure(fig, stem):
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    for extension in ("png", "pdf"):
        output_path = PLOTS_DIR / f"{stem}.{extension}"
        fig.savefig(output_path, dpi=240, bbox_inches="tight")
        outputs.append(output_path)
        print(output_path)
    plt.close(fig)
    return outputs


def plot_single_scenario(scenario, truth):
    scenario_colour = SCENARIO_COLOURS.get(scenario, PALETTE["ink_black"])
    true_wl = reference_observation_grid(scenario)
    true_a0 = resample_curve(truth["A0"]["wl"], truth["A0"]["depth"], true_wl)
    true_scenario = resample_curve(truth[scenario]["wl"], truth[scenario]["depth"], true_wl)
    y_reference_values = [
        true_a0,
        true_scenario,
    ]
    fig, ax = plt.subplots(figsize=(9.2, 4.8), constrained_layout=True)

    if scenario == "A0":
        ax.plot(
            true_wl,
            true_a0,
            color=TRUE_COLOURS["A0"],
            lw=1.35,
            ls=":",
            alpha=1.0,
            label="True A0",
            zorder=20,
        )
    else:
        ax.plot(
            true_wl,
            true_a0,
            color=TRUE_COLOURS["A0"],
            lw=1.25,
            ls=":",
            alpha=1.0,
            label="True A0",
            zorder=20,
        )
        ax.plot(
            true_wl,
            true_scenario,
            color=TRUE_COLOURS["A3"],
            lw=1.35,
            ls=":",
            alpha=1.0,
            label=f"True {scenario}",
            zorder=21,
        )

    missing_retrievals = []
    for transits in TRANSITS:
        add_synthetic_observations(ax, scenario, transits, truth[scenario])
        if not add_retrieved_spectrum(ax, scenario, transits, y_reference_values):
            missing_retrievals.append(transits)

    if missing_retrievals:
        missing = ", ".join(str(n_obs) for n_obs in missing_retrievals)
        ax.text(
            0.985,
            0.03,
            f"No combined retrieval: {missing} transits",
            ha="right",
            va="bottom",
            transform=ax.transAxes,
            fontsize=8,
            color=PALETTE["dim_grey"],
        )

    style_single_axis(ax, y_reference_values)
    add_instrument_ranges(ax)
    ax.set_title(f"TRAPPIST-1e {scenario}: Retrieval Results")
    ax.legend(frameon=False, fontsize=8, ncol=2, loc="upper left")
    return fig


def main():
    truth = prepare_truth_spectra()
    save_figure(
        plot_single_scenario("A0", truth),
        "trappist_retrieved_truth_A0_10_100transits_single_panel",
    )
    save_figure(
        plot_single_scenario("A3", truth),
        "trappist_retrieved_truth_A3_10_100transits_single_panel",
    )


if __name__ == "__main__":
    main()
