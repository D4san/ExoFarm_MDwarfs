from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE


BASE_DIR = Path(__file__).resolve().parent
RETRIEVAL_DIR = BASE_DIR / "POSEIDON_output" / "TRAPPIST-1e" / "retrievals"
SAMPLES_DIR = RETRIEVAL_DIR / "samples"
PLOTS_DIR = BASE_DIR / "POSEIDON_output" / "TRAPPIST-1e" / "plots"

SCENARIOS = ["A3"]
TRANSITS = [5, 10, 20, 100]
NOISE_TRANSITS = [5, 10, 20, 100]
INSTRUMENTS = ["MIRI", "NIRSpec", "NIRSpec_MIRI"]
INSTRUMENT_LABELS = {
    "MIRI": "MIRI",
    "NIRSpec": "NIRSpec",
    "NIRSpec_MIRI": "NIRSpec + MIRI",
}
INSTRUMENT_RANGES = {
    "MIRI": (5.0, 12.0),
    "NIRSpec": (0.6, 5.3),
    "NIRSpec_MIRI": (0.6, 12.0),
}
TRANSIT_COLOURS = {
    5: PALETTE["dark_amaranth"],
    10: PALETTE["deep_space_blue"],
    20: PALETTE["rusty_spice"],
    100: PALETTE["dim_grey"],
}
NOISE_STYLES = {
    5: {"color": PALETTE["dust_grey"], "alpha": 0.26, "label": "Synthetic error: 5 transits"},
    10: {"color": PALETTE["dim_grey"], "alpha": 0.34, "label": "Synthetic error: 10 transits"},
    20: {"color": PALETTE["ink_black"], "alpha": 0.44, "label": "Synthetic error: 20 transits"},
    100: {"color": PALETTE["golden_orange"], "alpha": 0.24, "label": "Synthetic error: 100 transits"},
}
PARAMETERS = ["log_CH4", "log_NH3", "log_N2O", "log_O3"]


def spectrum_path(scenario, transits, instrument):
    return SAMPLES_DIR / (
        f"TRAPPIST1e_{scenario}_retrieval_isotherm_isochem_"
        f"{transits}transits_{instrument}_spectrum_retrieved.txt"
    )


def sample_path(scenario, transits, instrument):
    return SAMPLES_DIR / (
        f"TRAPPIST1e_{scenario}_retrieval_isotherm_isochem_"
        f"{transits}transits_{instrument}_samples.txt"
    )


def synthetic_path(scenario, instrument, transits):
    labels = {
        "A0": "Trappist_A0_PreAgri",
        "A3": "Trappist_A3_Extreme",
    }
    instrument_names = {
        "NIRSpec": "JWST_NIRSpec_PRISM",
        "MIRI": "JWST_MIRI_LRS",
    }
    return (
        BASE_DIR
        / "POSEIDON_output"
        / "TRAPPIST-1e"
        / "synthetic_data"
        / "base_1transit"
        / (
            f"TRAPPIST-1e_SYNTHETIC_{instrument_names[instrument]}_"
            f"{labels[scenario]}_N_trans_{transits}.dat"
        )
    )


def load_synthetic(path):
    data = np.loadtxt(path)
    return data[:, 0], data[:, 1], data[:, 3]


def load_retrieved_spectrum(path):
    data = np.loadtxt(path, skiprows=1)
    return {
        "wl": data[:, 0],
        "minus_2": data[:, 1],
        "minus_1": data[:, 2],
        "median": data[:, 3],
        "plus_1": data[:, 4],
        "plus_2": data[:, 5],
    }


def rebin_curve(wl, values, wl_min=0.6, wl_max=12.0, resolving_power=260):
    edges = np.exp(
        np.arange(np.log(wl_min), np.log(wl_max) + np.log1p(1 / resolving_power), np.log1p(1 / resolving_power))
    )
    wl_bins = []
    value_bins = []
    for left, right in zip(edges[:-1], edges[1:]):
        mask = (wl >= left) & (wl < right)
        if not np.any(mask):
            continue
        wl_bins.append(np.exp(0.5 * (np.log(left) + np.log(right))))
        value_bins.append(np.nanmedian(values[mask]))
    return np.asarray(wl_bins), np.asarray(value_bins)


def plot_retrieved_spectra_grid(scenario):
    fig, axes = plt.subplots(
        len(INSTRUMENTS),
        1,
        figsize=(9.2, 9.5),
        sharex=False,
        constrained_layout=True,
    )
    for ax, instrument in zip(axes, INSTRUMENTS):
        wl_min, wl_max = INSTRUMENT_RANGES[instrument]
        for transits in TRANSITS:
            path = spectrum_path(scenario, transits, instrument)
            if not path.exists():
                continue
            spec = load_retrieved_spectrum(path)
            wl, minus_1 = rebin_curve(spec["wl"], spec["minus_1"], wl_min, wl_max)
            _, median = rebin_curve(spec["wl"], spec["median"], wl_min, wl_max)
            _, plus_1 = rebin_curve(spec["wl"], spec["plus_1"], wl_min, wl_max)
            _, minus_2 = rebin_curve(spec["wl"], spec["minus_2"], wl_min, wl_max)
            _, plus_2 = rebin_curve(spec["wl"], spec["plus_2"], wl_min, wl_max)
            colour = TRANSIT_COLOURS[transits]
            ax.fill_between(wl, minus_2, plus_2, color=colour, alpha=0.10, lw=0)
            ax.fill_between(wl, minus_1, plus_1, color=colour, alpha=0.22, lw=0)
            ax.plot(wl, median, color=colour, lw=1.5, label=f"{transits} transits")
        ax.set_xscale("log")
        ax.set_xlim(wl_min, wl_max)
        ax.grid(alpha=0.14, which="both")
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_ylabel(r"Transit depth $(R_p/R_s)^2$")
        ax.set_title(f"{scenario}: retrieved spectra, {INSTRUMENT_LABELS[instrument]}")
        ax.legend(frameon=False, ncol=3, fontsize=8)
    axes[-1].set_xlabel("Wavelength (micron)")
    return fig


def plot_noise_background_retrieval(scenario):
    fig, ax = plt.subplots(figsize=(9.6, 4.8), constrained_layout=True)
    reference_path = spectrum_path(scenario, 20, "NIRSpec_MIRI")
    if not reference_path.exists():
        reference_path = spectrum_path(scenario, 10, "NIRSpec_MIRI")
    reference = load_retrieved_spectrum(reference_path)

    for transits in NOISE_TRANSITS:
        style = NOISE_STYLES[transits]
        for instrument in ["NIRSpec", "MIRI"]:
            path = synthetic_path(scenario, instrument, transits)
            if not path.exists():
                continue
            wl, wl_err, depth_err = load_synthetic(path)
            centre = np.interp(wl, reference["wl"], reference["median"])
            ax.errorbar(
                wl,
                centre,
                yerr=depth_err,
                xerr=wl_err,
                fmt="+",
                ms=2.5,
                mew=0.55,
                color=style["color"],
                ecolor=style["color"],
                alpha=style["alpha"],
                elinewidth=0.55,
                capsize=0,
                linestyle="none",
                label=style["label"] if instrument == "NIRSpec" else None,
                zorder=1 + transits / 100,
            )

    for transits in TRANSITS:
        path = spectrum_path(scenario, transits, "NIRSpec_MIRI")
        if not path.exists():
            continue
        spec = load_retrieved_spectrum(path)
        wl, minus_1 = rebin_curve(spec["wl"], spec["minus_1"])
        _, median = rebin_curve(spec["wl"], spec["median"])
        _, plus_1 = rebin_curve(spec["wl"], spec["plus_1"])
        _, minus_2 = rebin_curve(spec["wl"], spec["minus_2"])
        _, plus_2 = rebin_curve(spec["wl"], spec["plus_2"])
        colour = TRANSIT_COLOURS[transits]
        ax.fill_between(wl, minus_2, plus_2, color=colour, alpha=0.10, lw=0, zorder=4)
        ax.fill_between(wl, minus_1, plus_1, color=colour, alpha=0.22, lw=0, zorder=5)
        ax.plot(wl, median, color=colour, lw=1.55, label=f"Retrieved: {transits} + {transits}", zorder=7)

    wl_ref, ref = rebin_curve(reference["wl"], reference["median"])
    ax.plot(wl_ref, ref, color=PALETTE["ink_black"], lw=1.0, ls=":", label="Reference retrieved spectrum", zorder=8)
    ax.hlines(ax.get_ylim()[0], 0.6, 5.3, color=PALETTE["deep_space_blue"], lw=1.4)
    ax.hlines(ax.get_ylim()[0], 5.3, 12.0, color=PALETTE["golden_orange"], lw=1.4)
    ax.set_xscale("log")
    ax.set_xlim(0.6, 12.0)
    ax.set_xticks([0.6, 0.8, 1, 2, 3, 4, 5, 6, 8, 10, 12])
    ax.set_xticklabels(["0.6", "0.8", "1", "2", "3", "4", "5", "6", "8", "10", "12"])
    ax.set_xlabel("Wavelength (micron)")
    ax.set_ylabel(r"Transit depth $(R_p/R_s)^2$")
    ax.set_title(f"{scenario}: retrieved spectra with synthetic error budget")
    ax.grid(alpha=0.12, which="both")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=8, ncol=2, loc="upper left")
    return fig


def load_samples(path):
    with path.open("r", encoding="utf-8") as handle:
        names = [name.strip() for name in handle.readline().split("|")]
    return np.genfromtxt(path, names=names, skip_header=1)


def plot_posterior_box_grid(scenario):
    fig, axes = plt.subplots(2, 2, figsize=(10.5, 7.6), constrained_layout=True)
    axes = axes.ravel()
    positions = np.arange(len(TRANSITS))
    offsets = {"MIRI": -0.24, "NIRSpec": 0.0, "NIRSpec_MIRI": 0.24}
    colours = {
        "MIRI": PALETTE["golden_orange"],
        "NIRSpec": PALETTE["deep_space_blue"],
        "NIRSpec_MIRI": PALETTE["dark_amaranth"],
    }

    for ax, parameter in zip(axes, PARAMETERS):
        for instrument in INSTRUMENTS:
            values = []
            xpos = []
            for i, transits in enumerate(TRANSITS):
                path = sample_path(scenario, transits, instrument)
                if not path.exists():
                    continue
                samples = load_samples(path)
                if parameter not in samples.dtype.names:
                    continue
                values.append(samples[parameter])
                xpos.append(positions[i] + offsets[instrument])
            if not values:
                continue
            violins = ax.violinplot(values, positions=xpos, widths=0.18, showextrema=False)
            for body in violins["bodies"]:
                body.set_facecolor(colours[instrument])
                body.set_edgecolor("none")
                body.set_alpha(0.32)
            medians = [np.median(v) for v in values]
            ax.scatter(xpos, medians, s=16, color=colours[instrument], label=INSTRUMENT_LABELS[instrument])
        ax.set_title(parameter.replace("log_", "log "))
        ax.set_xticks(positions)
        ax.set_xticklabels([str(t) for t in TRANSITS])
        ax.set_xlabel("Transits")
        ax.set_ylabel("Retrieved abundance")
        ax.grid(axis="y", alpha=0.16)
        ax.spines[["top", "right"]].set_visible(False)
    handles, labels = axes[0].get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    fig.legend(unique.values(), unique.keys(), frameon=False, ncol=3, loc="upper center")
    fig.suptitle(f"{scenario}: posterior marginals by instrument", y=1.03)
    return fig


def main():
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    for scenario in SCENARIOS:
        outputs = {
            "retrieved_spectra_grid": plot_retrieved_spectra_grid(scenario),
            "retrieved_noise_background": plot_noise_background_retrieval(scenario),
            "posterior_violins": plot_posterior_box_grid(scenario),
        }
        for suffix, fig in outputs.items():
            for extension in ["png", "pdf"]:
                path = PLOTS_DIR / f"trappist_retrieval_{scenario}_{suffix}.{extension}"
                fig.savefig(path, dpi=240, bbox_inches="tight")
                print(path)
            plt.close(fig)


if __name__ == "__main__":
    main()
