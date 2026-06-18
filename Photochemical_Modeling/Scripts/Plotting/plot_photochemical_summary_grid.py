import os
import pickle

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../../Results"))
OUTPUT_DIR = os.path.join(RESULTS_DIR, "Outputs")
PLOT_DIR = os.path.join(RESULTS_DIR, "Plots")

MOLECULES = ["N2O", "NH3", "O3", "CH4", "OH"]
MOLECULE_LABELS = {
    "N2O": r"N$_2$O",
    "NH3": r"NH$_3$",
    "O3": r"O$_3$",
    "CH4": r"CH$_4$",
    "OH": "OH",
}
SCENARIOS = ["A0", "A1", "A2", "A3"]
SCENARIO_LABELS = {
    "A0": "A0\nPre-agri",
    "A1": "A1\nCurrent",
    "A2": "A2\nModerate",
    "A3": "A3\nExtreme",
}
SCENARIO_LEGEND_LABELS = {
    "A0": "A0 Pre-agri",
    "A1": "A1 Current",
    "A2": "A2 Moderate",
    "A3": "A3 Extreme",
}
SCENARIO_SUFFIX = {
    "A0": "_A0_PreAgri.vul",
    "A1": "_A1_Current.vul",
    "A2": "_A2_Moderate.vul",
    "A3": "_A3_Extreme.vul",
}
SCENARIO_COLORS = {
    "A0": "#95E36B",
    "A1": "#56E3DB",
    "A2": "#BD62E3",
    "A3": "#E34F95",
}
EXOFARM_PALETTE = {
    "deep_moss": "#3F633E",
    "slate_green": "#57635E",
    "charcoal_violet": "#5B4763",
    "terracotta_mauve": "#8E5651",
}
STARS = {
    "Sun": {
        "label": "Earth-Sun (G2V)",
        "prefix": "Earth",
        "color": EXOFARM_PALETTE["terracotta_mauve"],
        "marker": "o",
        "linestyle": "-",
    },
    "Trappist": {
        "label": "TRAPPIST-1e (M8V)",
        "prefix": "Trappist",
        "color": EXOFARM_PALETTE["charcoal_violet"],
        "marker": "^",
        "linestyle": "--",
    },
}


def load_vulcan_output(star_key, scenario):
    filename = STARS[star_key]["prefix"] + SCENARIO_SUFFIX[scenario]
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        print(f"Warning: missing VULCAN output: {filepath}")
        return None

    with open(filepath, "rb") as handle:
        return pickle.load(handle)


def species_profile(data, molecule):
    species = data["variable"]["species"]
    if molecule not in species:
        return None, None

    idx = species.index(molecule)
    pressure_bar = data["atm"]["pco"] / 1.0e6
    vmr = data["variable"]["ymix"][:, idx]
    return pressure_bar, vmr


def column_averaged_mixing_ratio(data, molecule):
    """Return int q(P) dP / (p_bot - p_top) from VULCAN layer-center profiles."""
    pressure, vmr = species_profile(data, molecule)
    if pressure is None:
        return np.nan

    finite = np.isfinite(pressure) & np.isfinite(vmr) & (pressure > 0) & (vmr > 0)
    if finite.sum() < 2:
        return np.nan

    pressure = pressure[finite]
    vmr = vmr[finite]
    order = np.argsort(pressure)
    pressure = pressure[order]
    vmr = vmr[order]

    pressure_span = np.trapz(np.ones_like(pressure), x=pressure)
    if pressure_span <= 0:
        return np.nan

    return np.trapz(vmr, x=pressure) / pressure_span


def format_ratio(ratio):
    if not np.isfinite(ratio):
        return "n/a"
    if ratio >= 1000 or ratio < 0.01:
        mantissa, exponent = f"{ratio:.1e}".split("e")
        return f"{mantissa}e{int(exponent)}x"
    if ratio >= 10:
        return f"{ratio:.0f}x"
    return f"{ratio:.2g}x"


def positive_limits(values):
    finite = np.asarray(values)
    finite = finite[np.isfinite(finite) & (finite > 0)]
    if finite.size == 0:
        return 1.0e-14, 1.0e-1

    low = 10 ** np.floor(np.log10(finite.min()) - 0.15)
    high = 10 ** np.ceil(np.log10(finite.max()) + 0.15)
    return max(low, 1.0e-30), high


def add_molecule_label(ax, molecule, x=0.04, y=0.08, clip_on=True):
    ax.text(
        x,
        y,
        MOLECULE_LABELS[molecule],
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=11,
        fontweight="bold",
        bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": "0.82", "alpha": 0.82},
        clip_on=clip_on,
    )


def collect_outputs():
    outputs = {}
    for star_key in STARS:
        outputs[star_key] = {}
        for scenario in SCENARIOS:
            outputs[star_key][scenario] = load_vulcan_output(star_key, scenario)
    return outputs


def molecule_profile_limits(outputs, molecule):
    all_vmr = []
    for star_key in STARS:
        for scenario in SCENARIOS:
            data = outputs[star_key][scenario]
            if data is None:
                continue

            pressure, vmr = species_profile(data, molecule)
            if pressure is None:
                continue

            finite = np.isfinite(pressure) & np.isfinite(vmr) & (pressure > 0) & (vmr > 0)
            if finite.any():
                all_vmr.extend(vmr[finite])

    return positive_limits(all_vmr)


def plot_profile_panel(ax, outputs, star_key, molecule, x_limits):
    for scenario in SCENARIOS:
        data = outputs[star_key][scenario]
        if data is None:
            continue

        pressure, vmr = species_profile(data, molecule)
        if pressure is None:
            continue

        ax.plot(
            vmr,
            pressure,
            color=SCENARIO_COLORS[scenario],
            linewidth=2.5,
            alpha=0.7,
        )

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(*x_limits)
    ax.set_ylim(1.2, 1.0e-8)
    ax.grid(True, which="both", alpha=0.25, linewidth=0.6)


def plot_mean_panel(ax, outputs, molecule, baseline):
    x = np.arange(len(SCENARIOS))
    mean_values = {star_key: [] for star_key in STARS}

    for star_key in STARS:
        for scenario in SCENARIOS:
            data = outputs[star_key][scenario]
            mean_values[star_key].append(
                column_averaged_mixing_ratio(data, molecule) if data is not None else np.nan
            )

    plotted_values = []
    finite_curves = {
        star_key: np.asarray(values, dtype=float)
        for star_key, values in mean_values.items()
    }

    for star_key, star_info in STARS.items():
        y = np.asarray(mean_values[star_key], dtype=float)
        plotted_values.extend(y[np.isfinite(y) & (y > 0)])

        ax.plot(
            x,
            y,
            color=star_info["color"],
            linestyle=star_info["linestyle"],
            marker=star_info["marker"],
            markersize=8.2,
            linewidth=2.5,
            alpha=0.78,
        )

        for idx, (xi, yi) in enumerate(zip(x, y)):
            if not np.isfinite(yi) or yi <= 0 or not np.isfinite(baseline) or baseline <= 0:
                continue
            ratio = yi / baseline
            other_values = [
                curve[idx]
                for other_key, curve in finite_curves.items()
                if other_key != star_key and idx < len(curve) and np.isfinite(curve[idx])
            ]
            is_upper_curve = other_values and yi >= max(other_values)
            if idx == 0:
                x_offset = 3
                ha = "left"
            elif idx == len(x) - 1:
                x_offset = -3
                ha = "right"
            else:
                x_offset = 0
                ha = "center"
            if molecule == "O3":
                y_offset = -16 if idx % 2 == 0 else 14
                va = "top" if idx % 2 == 0 else "bottom"
            else:
                y_offset = 11 + 7 * (idx % 2) if is_upper_curve else -14 - 9 * (idx % 2)
                va = "bottom" if is_upper_curve else "top"
            ax.annotate(
                format_ratio(ratio),
                xy=(xi, yi),
                xytext=(x_offset, y_offset),
                textcoords="offset points",
                ha=ha,
                va=va,
                fontsize=8.8,
                color=star_info["color"],
                fontweight="bold",
            )

    ymin, ymax = positive_limits(plotted_values)
    ax.set_yscale("log")
    ax.set_ylim(ymin / 35.0, ymax * 18.0)
    ax.set_xticks(x)
    ax.set_xlim(-0.55, len(SCENARIOS) - 0.45)
    ax.set_xticklabels([SCENARIO_LABELS[sc] for sc in SCENARIOS], fontsize=8.5)
    ax.grid(True, which="major", axis="x", alpha=0.22, linewidth=0.6)
    ax.grid(False, which="both", axis="y")
    ax.axhline(baseline, color="0.35", linestyle="-.", linewidth=1.8, alpha=0.9)


def build_plot():
    os.makedirs(PLOT_DIR, exist_ok=True)
    outputs = collect_outputs()

    baselines = {}
    sun_a1 = outputs["Sun"]["A1"]
    for molecule in MOLECULES:
        baselines[molecule] = column_averaged_mixing_ratio(sun_a1, molecule)

    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["STIX Two Text", "STIXGeneral", "Times New Roman"],
            "mathtext.fontset": "stix",
            "font.size": 10.5,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "lines.linewidth": 2.5,
        }
    )

    fig = plt.figure(figsize=(10.8, 13.2))
    grid = GridSpec(
        len(MOLECULES),
        3,
        figure=fig,
        width_ratios=[0.9, 0.9, 1.0],
        wspace=0.22,
        hspace=0.34,
    )
    axes = np.empty((len(MOLECULES), 3), dtype=object)
    for row in range(len(MOLECULES)):
        axes[row, 0] = fig.add_subplot(grid[row, 0])
        axes[row, 1] = fig.add_subplot(grid[row, 1], sharey=axes[row, 0])
        axes[row, 2] = fig.add_subplot(grid[row, 2])

    fig.text(
        0.345,
        0.972,
        "Vertical chemical profiles",
        ha="center",
        va="bottom",
        fontsize=14.5,
        fontweight="bold",
    )
    fig.text(
        0.2,
        0.865,
        STARS["Sun"]["label"],
        ha="center",
        va="bottom",
        fontsize=11.5,
        fontweight="bold",
    )
    fig.text(
        0.49,
        0.865,
        STARS["Trappist"]["label"],
        ha="center",
        va="bottom",
        fontsize=11.5,
        fontweight="bold",
    )
    fig.text(
        0.775,
        0.972,
        "Column-averaged mixing ratio",
        ha="center",
        va="bottom",
        fontsize=14.5,
        fontweight="bold",
    )

    for row, molecule in enumerate(MOLECULES):
        x_limits = molecule_profile_limits(outputs, molecule)
        axes[row, 0].set_ylabel("Pressure (bar)", fontsize=11.5, fontweight="bold")

        plot_profile_panel(axes[row, 0], outputs, "Sun", molecule, x_limits)
        plot_profile_panel(axes[row, 1], outputs, "Trappist", molecule, x_limits)
        plot_mean_panel(axes[row, 2], outputs, molecule, baselines[molecule])

        add_molecule_label(axes[row, 0], molecule)
        add_molecule_label(axes[row, 1], molecule)
        mean_label_positions = {
            "O3": {"x": 0.05, "y": 0.5},
            "CH4": {"x": 0.05, "y": 0.08},
        }
        mean_label_kwargs = mean_label_positions.get(molecule, {"x": 0.04, "y": 0.84})
        add_molecule_label(axes[row, 2], molecule, **mean_label_kwargs)

        axes[row, 1].tick_params(axis="y", labelleft=True)
        axes[row, 2].tick_params(axis="y", labelsize=9)
        axes[row, 2].set_ylabel("Mixing ratio", fontsize=10.5)
        axes[row, 2].yaxis.tick_right()
        axes[row, 2].yaxis.set_label_position("right")

        if row == len(MOLECULES) - 1:
            axes[row, 0].set_xlabel("Mixing ratio")
            axes[row, 1].set_xlabel("Mixing ratio")
            axes[row, 2].set_xlabel("Scenario")

    scenario_handles = [
        Line2D(
            [0],
            [0],
            color=SCENARIO_COLORS[sc],
            linewidth=2.7,
            label=SCENARIO_LEGEND_LABELS[sc],
        )
        for sc in SCENARIOS
    ]
    star_handles = [
        Line2D(
            [0],
            [0],
            color=info["color"],
            marker=info["marker"],
            linestyle=info["linestyle"],
            linewidth=2.5,
            markersize=8,
            label=info["label"],
        )
        for info in STARS.values()
    ]
    baseline_handle = Line2D(
        [0],
        [0],
        color="0.35",
        linestyle="-.",
        linewidth=1.8,
        label="Earth-Sun A1 baseline",
    )

    scenario_legend = fig.legend(
        handles=scenario_handles,
        loc="upper center",
        bbox_to_anchor=(0.345, 0.957),
        ncol=4,
        fontsize=9.5,
        title="Profile scenarios",
        title_fontsize=9.5,
        frameon=True,
    )
    fig.add_artist(scenario_legend)
    fig.legend(
        handles=star_handles + [baseline_handle],
        loc="upper center",
        bbox_to_anchor=(0.775, 0.957),
        ncol=1,
        fontsize=8.5,
        title="Column averages",
        title_fontsize=8.5,
        frameon=True,
    )

    fig.subplots_adjust(top=0.865, bottom=0.065, left=0.095, right=0.935)

    for extension in ("png", "pdf"):
        output_file = os.path.join(PLOT_DIR, f"photochemical_summary_grid.{extension}")
        fig.savefig(output_file, dpi=300, bbox_inches="tight")
        print(f"Saved photochemical summary plot to {output_file}")


if __name__ == "__main__":
    build_plot()
