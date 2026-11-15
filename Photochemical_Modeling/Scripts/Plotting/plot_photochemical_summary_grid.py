import os
import pickle

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from matplotlib.ticker import LogLocator


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
        "column_label": "Earth-Sun\n(G2V)",
        "prefix": "Earth",
        "color": EXOFARM_PALETTE["terracotta_mauve"],
        "marker": "o",
        "linestyle": "-",
    },
    "Trappist": {
        "label": "TRAPPIST-1e (M8V)",
        "column_label": "TRAPPIST-1e\n(M8V)",
        "prefix": "Trappist",
        "color": EXOFARM_PALETTE["charcoal_violet"],
        "marker": "^",
        "linestyle": "--",
    },
    "Proxima": {
        "label": "Proxima analog (M5.5V)",
        "column_label": "Proxima b\n(M5.5V)",
        "prefix": "Proxima_b",
        "color": EXOFARM_PALETTE["slate_green"],
        "marker": "s",
        "linestyle": ":",
    },
}
ANNOTATION_OFFSETS_POINTS = {
    "N2O": {"Sun": 16, "Trappist": 27, "Proxima": -20},
    "NH3": {"Sun": -18, "Trappist": 32, "Proxima": 22},
    "O3": {"Sun": 24, "Trappist": 8, "Proxima": 8},
    "CH4": {"Sun": -16, "Trappist": 24, "Proxima": -8},
    "OH": {"Sun": 38, "Trappist": -18, "Proxima": 18},
}
DEFAULT_ANNOTATION_OFFSET_POINTS = 5


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

    integrate = getattr(np, "trapezoid", None)
    if integrate is None:
        integrate = np.trapz

    pressure_span = integrate(np.ones_like(pressure), x=pressure)
    if pressure_span <= 0:
        return np.nan

    return integrate(vmr, x=pressure) / pressure_span


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
        fontsize=9,
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
            linewidth=1.7,
            alpha=0.7,
        )

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(*x_limits)
    ax.set_ylim(1.2, 1.0e-8)
    ax.xaxis.set_major_locator(LogLocator(base=10.0, numticks=3))
    ax.yaxis.set_major_locator(LogLocator(base=100.0, numticks=5))
    ax.tick_params(axis="both", which="major", labelsize=6.0, pad=1.0)
    ax.grid(True, which="both", alpha=0.25, linewidth=0.45)


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
            markersize=5.2,
            linewidth=1.7,
            alpha=0.78,
        )

    positive = np.asarray(plotted_values, dtype=float)
    if positive.size:
        ymin = max(float(np.min(positive)) / 8.0, 1.0e-30)
        upper_padding_factor = 32.0 if molecule == "O3" else 8.0
        ymax = float(np.max(positive)) * upper_padding_factor
    else:
        ymin, ymax = positive_limits(positive)
    ax.set_yscale("log")
    ax.set_ylim(ymin, ymax)
    ax.set_xticks(x)
    ax.set_xlim(-0.55, len(SCENARIOS) - 0.45)
    ax.set_xticklabels([SCENARIO_LABELS[sc] for sc in SCENARIOS], fontsize=5.8)
    ax.tick_params(axis="y", labelsize=7.2, pad=1.0)
    ax.grid(True, which="major", axis="x", alpha=0.22, linewidth=0.45)
    ax.grid(False, which="both", axis="y")
    ax.axhline(baseline, color="0.35", linestyle="-.", linewidth=1.8, alpha=0.9)

    if not np.isfinite(baseline) or baseline <= 0:
        return

    ax.figure.canvas.draw()
    gap_px = 12.0 * ax.figure.dpi / 72.0
    edge_px = 5.0 * ax.figure.dpi / 72.0
    lower_y = ax.bbox.y0 + edge_px
    upper_y = ax.bbox.y1 - edge_px

    for idx, xi in enumerate(x):
        labels = []
        for star_key, star_info in STARS.items():
            yi = finite_curves[star_key][idx]
            if not np.isfinite(yi) or yi <= 0:
                continue
            point_y = ax.transData.transform((xi, yi))[1]
            labels.append(
                {
                    "star_key": star_key,
                    "star_info": star_info,
                    "yi": yi,
                    "point_y": point_y,
                    "preferred_y": point_y
                    + ANNOTATION_OFFSETS_POINTS.get(molecule, {}).get(
                        star_key, DEFAULT_ANNOTATION_OFFSET_POINTS
                    )
                    * ax.figure.dpi
                    / 72.0,
                    "text": format_ratio(yi / baseline),
                }
            )

        labels.sort(key=lambda label: label["preferred_y"])
        if not labels:
            continue

        # Respect molecule-specific placement, then separate nearby labels.
        target_y = [label["preferred_y"] for label in labels]
        for label_idx in range(1, len(target_y)):
            target_y[label_idx] = max(
                target_y[label_idx], target_y[label_idx - 1] + gap_px
            )

        if target_y[0] < lower_y and target_y[-1] > upper_y:
            # Conflicting preferred offsets cannot fit inside the panel.
            target_y = np.linspace(lower_y, upper_y, len(target_y)).tolist()
        elif target_y[-1] > upper_y:
            target_y[-1] = upper_y
            for label_idx in range(len(target_y) - 2, -1, -1):
                target_y[label_idx] = min(
                    target_y[label_idx], target_y[label_idx + 1] - gap_px
                )
        elif target_y[0] < lower_y:
            target_y[0] = lower_y
            for label_idx in range(1, len(target_y)):
                target_y[label_idx] = max(
                    target_y[label_idx], target_y[label_idx - 1] + gap_px
                )

        for label, label_y in zip(labels, target_y):
            if idx == 0:
                x_offset = 3
                ha = "left"
            elif idx == len(x) - 1:
                x_offset = -3
                ha = "right"
            else:
                x_offset = 0
                ha = "center"
            y_offset = (label_y - label["point_y"]) * 72.0 / ax.figure.dpi
            ax.annotate(
                label["text"],
                xy=(xi, label["yi"]),
                xytext=(x_offset, y_offset),
                textcoords="offset points",
                ha=ha,
                va="center",
                fontsize=7.5,
                color=label["star_info"]["color"],
                fontweight="bold",
            )


def build_plot(output_dir=PLOT_DIR, output_stem="photochemical_summary_grid"):
    os.makedirs(output_dir, exist_ok=True)
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
            "font.size": 8.0,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "lines.linewidth": 1.7,
        }
    )

    profile_star_keys = list(STARS)
    n_profile_columns = len(profile_star_keys)
    mean_column = n_profile_columns
    # Render near the expected two-column article width so labels retain their
    # intended point size when the PDF is included at full text width.
    fig = plt.figure(figsize=(7.0, 8.4))
    grid = GridSpec(
        len(MOLECULES),
        n_profile_columns + 1,
        figure=fig,
        width_ratios=[0.6] * n_profile_columns + [1.55],
        wspace=0.12,
        hspace=0.42,
    )
    axes = np.empty((len(MOLECULES), n_profile_columns + 1), dtype=object)
    for row in range(len(MOLECULES)):
        for column in range(n_profile_columns):
            if column == 0:
                axes[row, column] = fig.add_subplot(grid[row, column])
            else:
                axes[row, column] = fig.add_subplot(
                    grid[row, column], sharey=axes[row, 0]
                )
        axes[row, mean_column] = fig.add_subplot(grid[row, mean_column])

    fig.subplots_adjust(top=0.81, bottom=0.105, left=0.09, right=0.91)

    for row, molecule in enumerate(MOLECULES):
        x_limits = molecule_profile_limits(outputs, molecule)
        for column, star_key in enumerate(profile_star_keys):
            plot_profile_panel(
                axes[row, column], outputs, star_key, molecule, x_limits
            )
            if column == 0:
                add_molecule_label(axes[row, column], molecule)
            axes[row, column].tick_params(
                axis="y",
                left=(column == 0),
                labelleft=(column == 0),
                right=False,
                labelright=False,
            )
            axes[row, column].tick_params(axis="x", labelbottom=True)

        plot_mean_panel(
            axes[row, mean_column], outputs, molecule, baselines[molecule]
        )

        mean_ax = axes[row, mean_column]
        mean_ax.tick_params(axis="y", labelsize=7.0, pad=1.0)
        mean_ax.tick_params(axis="x", labelbottom=True)
        mean_ax.set_ylabel("Mixing ratio", fontsize=8.0, labelpad=4)
        mean_ax.yaxis.tick_right()
        mean_ax.yaxis.set_label_position("right")

        if row == len(MOLECULES) - 1:
            mean_ax.set_xlabel("Scenario")

    profile_left = axes[0, 0].get_position().x0
    profile_right = axes[0, n_profile_columns - 1].get_position().x1
    profile_center = (profile_left + profile_right) / 2.0
    fig.text(
        0.035,
        0.46,
        "Pressure (bar)",
        ha="center",
        va="center",
        rotation=90,
        fontsize=8.0,
        fontweight="bold",
    )
    fig.text(
        profile_center,
        0.048,
        "Mixing ratio",
        ha="center",
        va="center",
        fontsize=8.0,
    )

    scenario_handles = [
        Line2D(
            [0],
            [0],
            color=SCENARIO_COLORS[sc],
            linewidth=1.8,
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
            linewidth=1.7,
            markersize=5,
            label={
                "Sun": "Earth-Sun",
                "Trappist": "TRAPPIST-1e",
                "Proxima": "Proxima b",
            }[star_key],
        )
        for star_key, info in STARS.items()
    ]
    baseline_handle = Line2D(
        [0],
        [0],
        color="0.35",
        linestyle="-.",
        linewidth=1.8,
        label="Earth-Sun A1 baseline",
    )

    fig.canvas.draw()
    mean_position = axes[0, mean_column].get_position()
    mean_center = (mean_position.x0 + mean_position.x1) / 2.0

    fig.text(
        profile_center,
        0.974,
        "Vertical chemical profiles",
        ha="center",
        va="bottom",
        fontsize=11.5,
        fontweight="bold",
    )
    fig.text(
        mean_center,
        0.974,
        "Column-averaged mixing ratio",
        ha="center",
        va="bottom",
        fontsize=11.5,
        fontweight="bold",
    )
    for column, star_key in enumerate(profile_star_keys):
        position = axes[0, column].get_position()
        fig.text(
            (position.x0 + position.x1) / 2.0,
            0.84,
            STARS[star_key].get("column_label", STARS[star_key]["label"]),
            ha="center",
            va="bottom",
            fontsize=7.2,
            fontweight="bold",
        )

    scenario_legend = fig.legend(
        handles=scenario_handles,
        loc="upper center",
        bbox_to_anchor=(profile_center, 0.95),
        ncol=2,
        fontsize=6.5,
        handlelength=1.1,
        handletextpad=0.3,
        columnspacing=0.5,
        borderpad=0.3,
        labelspacing=0.3,
        title="Profile scenarios",
        title_fontsize=7.0,
        frameon=True,
    )
    fig.add_artist(scenario_legend)
    fig.legend(
        handles=star_handles + [baseline_handle],
        loc="upper center",
        bbox_to_anchor=(mean_center, 0.95),
        ncol=2,
        fontsize=6.3,
        handlelength=1.1,
        handletextpad=0.35,
        columnspacing=0.55,
        borderpad=0.3,
        labelspacing=0.25,
        title="Column averages",
        title_fontsize=7.0,
        frameon=True,
    )

    for extension in ("png", "pdf"):
        output_file = os.path.join(output_dir, f"{output_stem}.{extension}")
        fig.savefig(output_file, dpi=300, bbox_inches="tight")
        print(f"Saved photochemical summary plot to {output_file}")


if __name__ == "__main__":
    build_plot()
