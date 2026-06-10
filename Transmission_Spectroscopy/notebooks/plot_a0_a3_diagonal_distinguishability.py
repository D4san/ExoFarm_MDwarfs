from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE
from plot_a0_a3_posterior_sigma_matrix import (
    INSTRUMENT_LABELS,
    INSTRUMENT_ORDER,
    load_campaigns,
    load_samples,
)


BASE_DIR = Path(__file__).resolve().parent
PLOTS_DIR = BASE_DIR / "POSEIDON_output" / "TRAPPIST-1e" / "plots"

PARAMETERS = ("log_N2O", "log_NH3")
PARAMETER_LABELS = {
    "log_N2O": r"N$_2$O",
    "log_NH3": r"NH$_3$",
}
INSTRUMENT_COLOURS = {
    "MIRI": PALETTE["golden_orange"],
    "NIRSpec": PALETTE["deep_space_blue"],
    "NIRSpec_MIRI": PALETTE["dark_amaranth"],
}
REFERENCE_CAMPAIGN = (100, "NIRSpec_MIRI")
RNG = np.random.default_rng(271828)
DELTA_DRAWS = 100_000


def campaign_key(case):
    return case["transits"], case["instrument"]


def campaign_label(key):
    transits, instrument = key
    return f"{transits} {INSTRUMENT_LABELS[instrument]}"


def diagonal_campaigns(campaigns):
    a0 = {campaign_key(case): case for case in campaigns["A0"]}
    a3 = {campaign_key(case): case for case in campaigns["A3"]}
    keys = sorted(
        set(a0).intersection(a3),
        key=lambda key: (key[0], INSTRUMENT_ORDER[key[1]]),
    )
    return [(key, a0[key], a3[key]) for key in keys]


def parameter_samples(case, parameter):
    samples = load_samples(case["path"])
    return np.asarray(samples[parameter], dtype=float)


def posterior_summary(values):
    q16, median, q84 = np.nanpercentile(values, [16, 50, 84])
    return median, 0.5 * (q84 - q16)


def combined_sigma_distance(a0_values, a3_values):
    a0_median, a0_sigma = posterior_summary(a0_values)
    a3_median, a3_sigma = posterior_summary(a3_values)
    denominator = np.hypot(a0_sigma, a3_sigma)
    return abs(a3_median - a0_median) / denominator


def posterior_delta(a0_values, a3_values):
    a0_draws = RNG.choice(a0_values, size=DELTA_DRAWS, replace=True)
    a3_draws = RNG.choice(a3_values, size=DELTA_DRAWS, replace=True)
    return a3_draws - a0_draws


def a3_reference_distance(a3_values, reference):
    a3_median, a3_sigma = posterior_summary(a3_values)
    return abs(a3_median - reference) / a3_sigma


def style_campaign_axis(ax, keys):
    positions = np.arange(len(keys))
    ax.set_xticks(positions)
    ax.set_xticklabels([campaign_label(key) for key in keys], rotation=45, ha="right")
    ax.grid(axis="y", alpha=0.16)
    ax.spines[["top", "right"]].set_visible(False)
    return positions


def plot_combined_sigma(diagonal):
    keys = [item[0] for item in diagonal]
    fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.3), sharey=True, constrained_layout=True)
    for ax, parameter in zip(axes, PARAMETERS):
        values = []
        for _, a0_case, a3_case in diagonal:
            values.append(
                combined_sigma_distance(
                    parameter_samples(a0_case, parameter),
                    parameter_samples(a3_case, parameter),
                )
            )
        positions = style_campaign_axis(ax, keys)
        colours = [INSTRUMENT_COLOURS[key[1]] for key in keys]
        ax.bar(positions, values, color=colours, alpha=0.78, width=0.72)
        for position, value in zip(positions, values):
            ax.text(position, value + 0.05, f"{value:.2f}", ha="center", va="bottom", fontsize=7)
        ax.axhline(2.0, color=PALETTE["dim_grey"], ls="--", lw=0.9, alpha=0.75)
        ax.axhline(3.0, color=PALETTE["ink_black"], ls=":", lw=0.9, alpha=0.75)
        ax.set_title(PARAMETER_LABELS[parameter])
        ax.set_xlabel("Matched observing campaign")
    axes[0].set_ylabel(r"Combined posterior separation, $\Delta_\sigma$")
    fig.suptitle("A0 vs A3: median separation using joint posterior variance")
    return fig


def plot_delta_posteriors(diagonal):
    keys = [item[0] for item in diagonal]
    fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.6), sharey=False, constrained_layout=True)
    for ax, parameter in zip(axes, PARAMETERS):
        medians = []
        lower_68 = []
        upper_68 = []
        lower_95 = []
        upper_95 = []
        probabilities = []
        for _, a0_case, a3_case in diagonal:
            delta = posterior_delta(
                parameter_samples(a0_case, parameter),
                parameter_samples(a3_case, parameter),
            )
            q025, q16, median, q84, q975 = np.nanpercentile(delta, [2.5, 16, 50, 84, 97.5])
            medians.append(median)
            lower_68.append(median - q16)
            upper_68.append(q84 - median)
            lower_95.append(median - q025)
            upper_95.append(q975 - median)
            probabilities.append(np.mean(delta > 0.0))

        positions = style_campaign_axis(ax, keys)
        colours = [INSTRUMENT_COLOURS[key[1]] for key in keys]
        ax.errorbar(
            positions,
            medians,
            yerr=[lower_95, upper_95],
            fmt="none",
            ecolor=PALETTE["dim_grey"],
            elinewidth=1.1,
            capsize=3,
            alpha=0.65,
            zorder=2,
        )
        ax.errorbar(
            positions,
            medians,
            yerr=[lower_68, upper_68],
            fmt="none",
            ecolor=PALETTE["ink_black"],
            elinewidth=2.5,
            capsize=3,
            alpha=0.82,
            zorder=3,
        )
        ax.scatter(positions, medians, c=colours, s=34, zorder=4)
        for position, median, probability in zip(positions, medians, probabilities):
            ax.annotate(
                f"{100 * probability:.1f}%",
                (position, median),
                xytext=(0, 8 if median >= 0 else -12),
                textcoords="offset points",
                ha="center",
                fontsize=6.5,
            )
        ax.axhline(0.0, color=PALETTE["ink_black"], ls="--", lw=1.0)
        ax.set_title(PARAMETER_LABELS[parameter])
        ax.set_xlabel("Matched observing campaign")
    axes[0].set_ylabel(r"$\Delta\log X = \log X_{A3} - \log X_{A0}$ (dex)")
    fig.suptitle(
        "A0 vs A3: posterior difference using all posterior samples\n"
        "Thin bars: 95% interval | Thick bars: 68% interval | Labels: P(A3 > A0)"
    )
    return fig


def plot_a3_against_a0_reference(diagonal, campaigns):
    keys = [item[0] for item in diagonal]
    a0_reference_case = next(
        case for case in campaigns["A0"] if campaign_key(case) == REFERENCE_CAMPAIGN
    )
    references = {
        parameter: np.nanmedian(parameter_samples(a0_reference_case, parameter))
        for parameter in PARAMETERS
    }

    fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.3), sharey=True, constrained_layout=True)
    for ax, parameter in zip(axes, PARAMETERS):
        values = []
        for _, _, a3_case in diagonal:
            values.append(
                a3_reference_distance(
                    parameter_samples(a3_case, parameter),
                    references[parameter],
                )
            )
        positions = style_campaign_axis(ax, keys)
        colours = [INSTRUMENT_COLOURS[key[1]] for key in keys]
        ax.bar(positions, values, color=colours, alpha=0.78, width=0.72)
        for position, value in zip(positions, values):
            ax.text(position, value + 0.05, f"{value:.2f}", ha="center", va="bottom", fontsize=7)
        ax.axhline(2.0, color=PALETTE["dim_grey"], ls="--", lw=0.9, alpha=0.75)
        ax.axhline(3.0, color=PALETTE["ink_black"], ls=":", lw=0.9, alpha=0.75)
        ax.set_title(
            f"{PARAMETER_LABELS[parameter]}\n"
            rf"A0 reference: $\log X={references[parameter]:.2f}$"
        )
        ax.set_xlabel("A3 observing campaign")
    axes[0].set_ylabel(r"Distance from A0 reference using only $\sigma_{A3}$")
    fig.suptitle(
        "A3 inconsistency with the best-observed A0 reference\n"
        "A0 reference = median of the 100-transit NIRSpec+MIRI A0 posterior"
    )
    return fig


def save_figure(fig, stem):
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    for extension in ("png", "pdf"):
        output = PLOTS_DIR / f"{stem}.{extension}"
        fig.savefig(output, dpi=240, bbox_inches="tight")
        print(output)
    plt.close(fig)


def main():
    campaigns = load_campaigns()
    diagonal = diagonal_campaigns(campaigns)
    save_figure(
        plot_combined_sigma(diagonal),
        "trappist_A0_A3_diagonal_joint_sigma_separation",
    )
    save_figure(
        plot_delta_posteriors(diagonal),
        "trappist_A0_A3_diagonal_logX_difference_posteriors",
    )
    save_figure(
        plot_a3_against_a0_reference(diagonal, campaigns),
        "trappist_A3_distance_from_best_A0_reference",
    )


if __name__ == "__main__":
    main()
