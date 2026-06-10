import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from exofarm_transmission_workflow import (
    OBSERVATION_TRANSIT_COUNTS,
    SCENARIOS,
    compute_forward_spectra,
    create_pressure_grid,
    create_trappist_system,
    define_forward_models,
    load_profiles,
    make_atmospheres,
    make_wavelength_grid_and_opacities,
)
from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE


NOTEBOOK_DIR = Path(__file__).resolve().parent
POSEIDON_OUTPUT_DIR = NOTEBOOK_DIR / "POSEIDON_output" / "TRAPPIST-1e"
SYNTHETIC_DATA_DIR = POSEIDON_OUTPUT_DIR / "synthetic_data" / "base_1transit"
RETRIEVAL_SAMPLES_DIR = POSEIDON_OUTPUT_DIR / "retrievals" / "samples"
PLOTS_DIR = POSEIDON_OUTPUT_DIR / "plots"

PLANET_NAME = "TRAPPIST-1e"
RS_TRAPPIST_KM = 0.11697 * 695700.0
RP_TRAPPIST_KM = 0.917985 * 6371.0

TRANSIT_STYLES = {
    5: {
        "color": PALETTE["dust_grey"],
        "alpha": 0.30,
        "marker": "+",
        "label": "Synthetic JWST data: 5 Transits",
        "zorder": 1,
    },
    10: {
        "color": PALETTE["dim_grey"],
        "alpha": 0.42,
        "marker": "+",
        "label": "Synthetic JWST data: 10 Transits",
        "zorder": 2,
    },
    20: {
        "color": PALETTE["ink_black"],
        "alpha": 0.54,
        "marker": "+",
        "label": "Synthetic JWST data: 20 Transits",
        "zorder": 3,
    },
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Plot TRAPPIST-1e synthetic observations in a retrieved-spectrum style."
    )
    parser.add_argument(
        "--scenarios",
        nargs="+",
        choices=sorted(SCENARIOS),
        default=["A3", "A0"],
        help="Scenario panels to include.",
    )
    parser.add_argument(
        "--transits",
        nargs="+",
        type=int,
        choices=OBSERVATION_TRANSIT_COUNTS,
        default=OBSERVATION_TRANSIT_COUNTS,
        help="Synthetic observation transit counts to plot.",
    )
    parser.add_argument(
        "--retrieval-transits",
        nargs="+",
        type=int,
        default=[5, 10, 20],
        help="Retrieved spectra to overlay when matching files exist.",
    )
    parser.add_argument(
        "--retrieval-instruments",
        nargs="+",
        choices=["miri", "nirspec", "both"],
        default=["miri", "nirspec", "both"],
        help="Retrieved instrument modes to overlay when matching files exist.",
    )
    parser.add_argument(
        "--output-stem",
        default="trappist_simulated_observations_A3_A0",
        help="Output filename stem in POSEIDON_output/TRAPPIST-1e/plots.",
    )
    parser.add_argument("--wl-min", type=float, default=0.6)
    parser.add_argument("--wl-max", type=float, default=12.0)
    parser.add_argument(
        "--spectrum-r",
        type=float,
        default=260.0,
        help="Visual constant-R rebinning for the true and retrieved spectra.",
    )
    parser.add_argument(
        "--errorbar-r",
        type=float,
        default=0.0,
        help=(
            "Optional visual constant-R rebinning for synthetic error bars. "
            "Use 0 to keep the native observation bins."
        ),
    )
    parser.add_argument(
        "--y-pad-fraction",
        type=float,
        default=0.16,
        help="Fractional padding around the true-spectrum range for the y axis.",
    )
    return parser.parse_args()


def synthetic_path(scenario_key, instrument, n_transits):
    label = SCENARIOS[scenario_key]["label"]
    if instrument == "nirspec":
        name = f"{PLANET_NAME}_SYNTHETIC_JWST_NIRSpec_PRISM_{label}_N_trans_{n_transits}.dat"
    elif instrument == "miri":
        name = f"{PLANET_NAME}_SYNTHETIC_JWST_MIRI_LRS_{label}_N_trans_{n_transits}.dat"
    else:
        raise ValueError(instrument)
    return SYNTHETIC_DATA_DIR / name


def load_dat(path):
    data = np.loadtxt(path)
    return data[:, 0], data[:, 1], data[:, 2], data[:, 3]


def retrieval_path(scenario_key, n_transits, instrument_mode):
    suffix = {
        "miri": "_MIRI",
        "nirspec": "_NIRSpec",
        "both": "_NIRSpec_MIRI",
    }[instrument_mode]
    return RETRIEVAL_SAMPLES_DIR / (
        f"TRAPPIST1e_{scenario_key}_retrieval_isotherm_isochem_"
        f"{n_transits}transits{suffix}_spectrum_retrieved.txt"
    )


def instrument_range(instrument_mode):
    if instrument_mode == "nirspec":
        return 0.60, 5.30
    if instrument_mode == "miri":
        return 5.00, 12.0
    return 0.60, 12.0


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


def constant_r_edges(wl_min, wl_max, resolving_power):
    step = np.log1p(1.0 / resolving_power)
    return np.exp(np.arange(np.log(wl_min), np.log(wl_max) + step, step))


def rebin_curve(wl, values, wl_min, wl_max, resolving_power):
    edges = constant_r_edges(wl_min, wl_max, resolving_power)
    wl_bins = []
    value_bins = []

    for left, right in zip(edges[:-1], edges[1:]):
        mask = (wl >= left) & (wl < right)
        if not np.any(mask):
            continue
        wl_bins.append(np.exp(0.5 * (np.log(left) + np.log(right))))
        value_bins.append(np.nanmedian(values[mask]))

    return np.asarray(wl_bins), np.asarray(value_bins)


def rebin_error_budget(wl, wl_err, truth_at_bins, depth_err, wl_min, wl_max, resolving_power):
    edges = constant_r_edges(wl_min, wl_max, resolving_power)
    wl_bins = []
    wl_err_bins = []
    truth_bins = []
    depth_err_bins = []

    for left, right in zip(edges[:-1], edges[1:]):
        mask = (wl >= left) & (wl < right)
        if not np.any(mask):
            continue
        centre = np.exp(0.5 * (np.log(left) + np.log(right)))
        wl_bins.append(centre)
        wl_err_bins.append(0.5 * (right - left))
        truth_bins.append(np.nanmedian(truth_at_bins[mask]))
        depth_err_bins.append(np.nanmedian(depth_err[mask]))

    return (
        np.asarray(wl_bins),
        np.asarray(wl_err_bins),
        np.asarray(truth_bins),
        np.asarray(depth_err_bins),
    )


def compute_truth_spectra(scenario_keys):
    star, planet = create_trappist_system()
    P, P_surf, P_ref, R_p_ref = create_pressure_grid()
    models = define_forward_models(scenario_keys)
    temperatures, compositions = load_profiles(models, P, scenario_keys)
    atmospheres = make_atmospheres(
        planet,
        models,
        P,
        P_ref,
        R_p_ref,
        P_surf,
        temperatures,
        compositions,
    )
    wl, opac = make_wavelength_grid_and_opacities(models[scenario_keys[0]])
    spectra = compute_forward_spectra(planet, star, models, atmospheres, opac, wl)
    return wl, spectra


def depth_to_altitude_km(depth):
    depth = np.asarray(depth)
    return np.sqrt(np.maximum(depth, 1.0e-12)) * RS_TRAPPIST_KM - RP_TRAPPIST_KM


def altitude_to_depth(altitude):
    return ((altitude + RP_TRAPPIST_KM) / RS_TRAPPIST_KM) ** 2


def add_instrument_bands(ax, ymin, ymax):
    y = ymin + 0.015 * (ymax - ymin)
    ax.hlines(y, 0.60, 5.30, color=PALETTE["dark_amaranth"], lw=1.2)
    ax.text(
        2.3,
        y + 0.006 * (ymax - ymin),
        "NIRSpec Prism",
        color=PALETTE["dark_amaranth"],
        ha="center",
        fontsize=9,
    )
    ax.hlines(y, 5.30, 12.0, color=PALETTE["golden_orange"], lw=1.2)
    ax.text(
        7.2,
        y + 0.006 * (ymax - ymin),
        "MIRI LRS",
        color=PALETTE["golden_orange"],
        ha="center",
        fontsize=9,
    )


def plot_panel(
    ax,
    scenario_key,
    wl_truth,
    truth,
    transits,
    retrieval_transits,
    retrieval_instruments,
    wl_min,
    wl_max,
    spectrum_r,
    errorbar_r,
):
    scenario = SCENARIOS[scenario_key]
    wl_plot, truth_plot = rebin_curve(wl_truth, truth, wl_min, wl_max, spectrum_r)

    retrieval_colours = {
        5: PALETTE["dark_amaranth"],
        10: PALETTE["deep_space_blue"],
        20: PALETTE["rusty_spice"],
    }
    for n_transits in retrieval_transits:
        for instrument_mode in retrieval_instruments:
            path = retrieval_path(scenario_key, n_transits, instrument_mode)
            if not path.exists():
                continue
            retrieved = load_retrieved_spectrum(path)
            inst_min, inst_max = instrument_range(instrument_mode)
            ret_min = max(wl_min, inst_min)
            ret_max = min(wl_max, inst_max)
            wl_ret, minus_2 = rebin_curve(retrieved["wl"], retrieved["minus_2"], ret_min, ret_max, spectrum_r)
            _, minus_1 = rebin_curve(retrieved["wl"], retrieved["minus_1"], ret_min, ret_max, spectrum_r)
            _, median = rebin_curve(retrieved["wl"], retrieved["median"], ret_min, ret_max, spectrum_r)
            _, plus_1 = rebin_curve(retrieved["wl"], retrieved["plus_1"], ret_min, ret_max, spectrum_r)
            _, plus_2 = rebin_curve(retrieved["wl"], retrieved["plus_2"], ret_min, ret_max, spectrum_r)
            colour = retrieval_colours.get(n_transits, "tab:red")
            label = f"Retrieved: {n_transits} Transits"
            if instrument_mode != "both":
                label += f" ({instrument_mode.upper()})"
            ax.fill_between(
                wl_ret,
                minus_2,
                plus_2,
                color=colour,
                alpha=0.13,
                lw=0,
                zorder=4,
            )
            ax.fill_between(
                wl_ret,
                minus_1,
                plus_1,
                color=colour,
                alpha=0.26,
                lw=0,
                zorder=5,
            )
            ax.plot(
                wl_ret,
                median,
                color=colour,
                lw=1.35,
                label=label,
                zorder=6,
            )

    for n_transits in transits:
        style = TRANSIT_STYLES[n_transits]
        for instrument in ("nirspec", "miri"):
            path = synthetic_path(scenario_key, instrument, n_transits)
            if not path.exists():
                continue
            wl, wl_err, depth, depth_err = load_dat(path)
            true_at_bins = np.interp(wl, wl_truth, truth)
            if errorbar_r > 0:
                wl_b, wl_err_b, true_b, depth_err_b = rebin_error_budget(
                    wl,
                    wl_err,
                    true_at_bins,
                    depth_err,
                    wl_min,
                    wl_max,
                    errorbar_r,
                )
            else:
                wl_b, wl_err_b, true_b, depth_err_b = wl, wl_err, true_at_bins, depth_err
            ax.errorbar(
                wl_b,
                true_b,
                yerr=depth_err_b,
                xerr=wl_err_b,
                fmt=style["marker"],
                ms=3.0,
                mew=0.55,
                color=style["color"],
                ecolor=style["color"],
                alpha=style["alpha"],
                elinewidth=0.65,
                capsize=0,
                linestyle="none",
                label=style["label"] if instrument == "nirspec" else None,
                zorder=style["zorder"],
            )

    ax.plot(
        wl_plot,
        truth_plot,
        color=PALETTE["golden_orange"],
        lw=1.8,
        ls=":",
        label="True Spectrum",
        zorder=10,
    )

    ax.set_xscale("log")
    ax.set_xlim(wl_min, wl_max)
    ax.set_xticks([0.6, 0.8, 1, 2, 3, 4, 5, 6, 8, 10, 12])
    ax.set_xticklabels(["0.6", "0.8", "1", "2", "3", "4", "5", "6", "8", "10", "12"])
    ax.tick_params(direction="in", top=True, right=False)
    ax.grid(alpha=0.10, which="both", color=PALETTE["ink_black"])
    ax.text(
        0.11,
        0.94,
        scenario["name"],
        transform=ax.transAxes,
        fontsize=14,
        fontfamily="serif",
    )

    ymin, ymax = ax.get_ylim()
    add_instrument_bands(ax, ymin, ymax)


def y_limits_from_truth(wl_truth, spectra, scenario_keys, wl_min, wl_max, pad_fraction):
    selected = []
    for scenario_key in scenario_keys:
        mask = (wl_truth >= wl_min) & (wl_truth <= wl_max)
        selected.append(spectra[scenario_key][mask])

    values = np.concatenate(selected)
    ymin, ymax = np.percentile(values, [0.2, 99.8])
    span = ymax - ymin
    if span <= 0:
        span = max(abs(ymax), 1.0e-6)
    return ymin - pad_fraction * span, ymax + pad_fraction * span


def main():
    args = parse_args()
    wl_truth, spectra = compute_truth_spectra(args.scenarios)

    fig, axes = plt.subplots(
        len(args.scenarios),
        1,
        figsize=(8.6, 4.2 * len(args.scenarios)),
        sharex=True,
        constrained_layout=True,
    )
    if len(args.scenarios) == 1:
        axes = [axes]

    y_limits = y_limits_from_truth(
        wl_truth,
        spectra,
        args.scenarios,
        args.wl_min,
        args.wl_max,
        args.y_pad_fraction,
    )

    for ax, scenario_key in zip(axes, args.scenarios):
        plot_panel(
            ax,
            scenario_key,
            wl_truth,
            spectra[scenario_key],
            args.transits,
            args.retrieval_transits,
            args.retrieval_instruments,
            args.wl_min,
            args.wl_max,
            args.spectrum_r,
            args.errorbar_r,
        )
        ax.set_ylim(*y_limits)
        secax = ax.secondary_yaxis("right", functions=(depth_to_altitude_km, altitude_to_depth))
        secax.set_ylabel("Effective Altitude (km)", fontfamily="serif")
        secax.tick_params(direction="in")
        ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(0.10, 0.90), fontsize=8)

    axes[-1].set_xlabel("Wavelength (μm)", fontfamily="serif", fontsize=12)
    for ax in axes:
        ax.set_ylabel(r"Transit Depth  $(R_p / R_s)^2$", fontfamily="serif", fontsize=12)

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    png_path = PLOTS_DIR / f"{args.output_stem}.png"
    pdf_path = PLOTS_DIR / f"{args.output_stem}.pdf"
    fig.savefig(png_path, dpi=220)
    fig.savefig(pdf_path)
    print(f"Saved {png_path}")
    print(f"Saved {pdf_path}")


if __name__ == "__main__":
    main()
