"""Plot integrated molecular-template S/N for the classic LIFE branch.

This is the LIFE analogue of the integrated transmission diagnostic.  LIFE has
one instrument in each campaign, so the upper panel contains two categories:
the full-grid molecular templates for N2O and NH3.  Marker shape encodes the
scenario and colour encodes integration time.  The lower panel projects the
A3 templates with the verified classic photon-noise scaling and annotates the
integration times required for S/N=3 and S/N=5.

The previous peak-per-feature figure remains available as legacy evidence.
This diagnostic uses the full saved LIFE grid and diagonal per-bin errors:

    SNR_m = sqrt(sum_k (Delta F_m,k / sigma_k)**2)

It is a template-S/N diagnostic, not a detection claim.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import emission_forward as ef

# Reuse the project spectroscopy palette rather than creating a second set of
# colours for the transmission and thermal-emission figures.
STYLE_DIR = ef.REPO / "Transmission_Spectroscopy" / "notebooks"
if str(STYLE_DIR) not in sys.path:
    sys.path.insert(0, str(STYLE_DIR))
from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE


CAMPAIGNS = {
    "earth_sun": ("life_earth_sun_10pc_interface_v1", "10 pc, LIFE baseline"),
    "proxima": ("life_proxima_b_earthlike_v1", "1.30 pc, LIFE X scene"),
}
FIGURE_TITLES = {
    "earth_sun": "LIFE S/N projections — Earth--Sun",
    "proxima": "LIFE S/N projections — Proxima",
}

SCENARIOS = {
    "A1": {"offset": -0.20, "marker": "o", "label": "A1 Current Earth", "size": 130},
    "A2": {"offset": 0.00, "marker": "s", "label": "A2 Moderate ExoFarm", "size": 120},
    "A3": {"offset": 0.20, "marker": "^", "label": "A3 Extreme ExoFarm", "size": 140},
}

TARGETS = ("N2O", "NH3")
TARGET_LABELS = {"N2O": r"N$_2$O", "NH3": r"NH$_3$"}
TIME_HOURS = (10.0, 100.0, 1000.0)
TIME_STYLES = {
    10.0: {"color": PALETTE["scenario_cyan"], "label": "10 h"},
    100.0: {"color": PALETTE["scenario_green"], "label": "100 h"},
    1000.0: {"color": PALETTE["scenario_violet"], "label": "1000 h"},
}
MOLECULE_COLOURS = {
    "N2O": PALETTE["terracotta_mauve"],
    "NH3": PALETTE["charcoal_violet"],
}
THRESHOLDS = ((3.0, "--"), (5.0, "-."))

# The saved NPZ products use the same diagnostic bands as the classic S/N
# runner.  They are exported as secondary rows; the figure uses full coverage.
BANDS = {
    "N2O": ((7.5, 8.1), (16.5, 17.5)),
    "NH3": ((9.5, 11.5),),
}

CSV_FIELDS = (
    "campaign",
    "scenario",
    "molecule",
    "aggregation",
    "instrument",
    "band_id",
    "band_min_um",
    "band_max_um",
    "n_bins",
    "reference_hours",
    "covariance_mode",
    "noise_source",
    "snr_10h",
    "snr_100h",
    "snr_1000h",
)


def _style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["STIX Two Text", "STIXGeneral", "Times New Roman"],
            "mathtext.fontset": "stix",
            "figure.dpi": 140,
        }
    )


def _campaign_paths(campaign: str) -> tuple[Path, Path, str]:
    campaign_id, target_label = CAMPAIGNS[campaign]
    output_dir = ef.REPO / "Thermal_Emission_Spectroscopy" / "outputs" / campaign_id
    products = output_dir / "lifesim" / "life_classic_binned_products.npz"
    return output_dir, products, target_label


def _snr_from_mask(signal: np.ndarray, sigma: np.ndarray, mask: np.ndarray) -> tuple[float, int]:
    valid = mask & np.isfinite(signal) & np.isfinite(sigma) & (sigma > 0.0)
    if not np.any(valid):
        return float("nan"), 0
    return float(np.sqrt(np.sum((signal[valid] / sigma[valid]) ** 2))), int(np.count_nonzero(valid))


def _scaled_snr(snr_reference: float, reference_hours: float) -> dict[str, float]:
    return {
        f"snr_{int(hours)}h": float(snr_reference * np.sqrt(hours / reference_hours))
        for hours in TIME_HOURS
    }


def compute_rows(d: np.lib.npyio.NpzFile, campaign: str, products_path: Path) -> list[dict[str, object]]:
    """Return full-grid rows and secondary band rows from one saved campaign."""

    wavelength = np.asarray(d["wl_bins_um"], dtype=float)
    reference_hours = float(d["t_ref_hours"])
    rows: list[dict[str, object]] = []

    for scenario in ("A1", "A2", "A3"):
        sigma = np.asarray(d[f"sigma_{scenario}"], dtype=float)
        for molecule in TARGETS:
            signal = np.asarray(d[f"dF_{scenario}_{molecule}"], dtype=float)
            full_mask = np.ones(wavelength.shape, dtype=bool)
            full_snr, n_full = _snr_from_mask(signal, sigma, full_mask)
            row = {
                "campaign": campaign,
                "scenario": scenario,
                "molecule": molecule,
                "aggregation": "instrument_total",
                "instrument": "LIFE_classic",
                "band_id": "full_coverage",
                "band_min_um": float(wavelength[0]),
                "band_max_um": float(wavelength[-1]),
                "n_bins": n_full,
                "reference_hours": reference_hours,
                "covariance_mode": "diagonal",
                "noise_source": str(products_path),
            }
            row.update(_scaled_snr(full_snr, reference_hours))
            rows.append(row)

            for band_index, (band_min, band_max) in enumerate(BANDS[molecule], start=1):
                band_mask = (wavelength >= band_min) & (wavelength <= band_max)
                band_snr, n_band = _snr_from_mask(signal, sigma, band_mask)
                if n_band == 0:
                    continue
                band_row = {
                    "campaign": campaign,
                    "scenario": scenario,
                    "molecule": molecule,
                    "aggregation": "band",
                    "instrument": "LIFE_classic",
                    "band_id": f"{molecule}_band_{band_index}",
                    "band_min_um": band_min,
                    "band_max_um": band_max,
                    "n_bins": n_band,
                    "reference_hours": reference_hours,
                    "covariance_mode": "diagonal",
                    "noise_source": str(products_path),
                }
                band_row.update(_scaled_snr(band_snr, reference_hours))
                rows.append(band_row)

    return rows


def write_rows(rows: list[dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"saved {path.relative_to(ef.REPO)}")


def _find_total(rows: list[dict[str, object]], scenario: str, molecule: str) -> dict[str, object] | None:
    for row in rows:
        if (
            row["scenario"] == scenario
            and row["molecule"] == molecule
            and row["aggregation"] == "instrument_total"
        ):
            return row
    return None


def _log_ticks(lower: float, upper: float) -> np.ndarray:
    exponents = np.arange(
        np.floor(np.log10(lower)),
        np.ceil(np.log10(upper)) + 1,
    )
    ticks = np.array(
        [multiplier * 10.0**exponent for exponent in exponents for multiplier in (1.0, 2.0, 5.0)]
    )
    return ticks[(ticks >= lower) & (ticks <= upper)]


def _time_ticks(upper: float) -> np.ndarray:
    """Use 1-2-5 labels for compact ranges and decades for long ranges."""

    if upper <= 1.0e4:
        return _log_ticks(1.0, upper)
    exponents = np.arange(0.0, np.floor(np.log10(upper)) + 1.0)
    return 10.0**exponents


def _time_tick_label(value: float) -> str:
    exponent = int(round(np.log10(value)))
    if np.isclose(value, 10.0**exponent):
        return rf"$10^{{{exponent}}}$"
    return f"{value:g}"


def plot_rows(rows: list[dict[str, object]], campaign: str, target_label: str, output_dir: Path) -> tuple[Path, Path]:
    """Create the two-panel full-grid S/N figure."""

    _style()
    total = [row for row in rows if row["aggregation"] == "instrument_total"]
    values = np.array(
        [float(row[f"snr_{int(hours)}h"]) for row in total for hours in TIME_HOURS],
        dtype=float,
    )
    values = values[np.isfinite(values) & (values > 0.0)]
    top_y_min = max(float(values.min()) / 2.0, 1e-6)
    top_y_max = float(values.max()) * 1.35

    fig, (ax_top, ax_bottom) = plt.subplots(
        2,
        1,
        figsize=(9.4, 10.4),
        gridspec_kw={"height_ratios": [1.15, 1.0]},
    )

    for molecule_index, molecule in enumerate(TARGETS):
        for scenario, scenario_style in SCENARIOS.items():
            row = _find_total(total, scenario, molecule)
            if row is None:
                continue
            for hours in TIME_HOURS:
                ax_top.scatter(
                    molecule_index + scenario_style["offset"],
                    float(row[f"snr_{int(hours)}h"]),
                    color=TIME_STYLES[hours]["color"],
                    marker=scenario_style["marker"],
                    s=scenario_style["size"],
                    edgecolors="#222222",
                    linewidths=0.8,
                    zorder=5,
                )

    ax_top.set_yscale("log")
    ax_top.set_ylim(top_y_min, top_y_max)
    ax_top.set_yticks(_log_ticks(top_y_min, top_y_max))
    ax_top.set_yticklabels([f"{tick:g}" for tick in ax_top.get_yticks()])
    ax_top.set_xticks(range(len(TARGETS)))
    ax_top.set_xticklabels([f"{TARGET_LABELS[m]}\n(full LIFE grid)" for m in TARGETS])
    ax_top.set_xlim(-0.6, 1.6)
    ax_top.set_ylabel("Integrated molecular-excess S/N")
    ax_top.set_xlabel("Molecular template", labelpad=8)
    ax_top.grid(True, which="both", linestyle=":", color="#dddddd", zorder=1)
    ax_top.axvline(0.5, color="#888888", linestyle="--", linewidth=1.2, alpha=0.5, zorder=2)
    label_y = top_y_max / 1.18
    ax_top.text(0.0, label_y, r"N$_2$O template", color="#444444", fontsize=10,
                fontstyle="italic", ha="center", weight="semibold")
    ax_top.text(1.0, label_y, r"NH$_3$ template", color="#444444", fontsize=10,
                fontstyle="italic", ha="center", weight="semibold")

    scenario_handles = [
        plt.Line2D(
            [0], [0], marker=style["marker"], color="w", label=style["label"],
            markerfacecolor="#888888", markeredgecolor="#222222",
            markersize=10, linestyle="None",
        )
        for style in SCENARIOS.values()
    ]
    time_handles = [
        plt.Line2D(
            [0], [0], marker="o", color="w", label=style["label"],
            markerfacecolor=style["color"], markeredgecolor="#222222",
            markersize=10, linestyle="None",
        )
        for style in TIME_STYLES.values()
    ]
    legend_scenarios = ax_top.legend(
        handles=scenario_handles,
        loc="lower left",
        bbox_to_anchor=(0.02, 0.05),
        title="Scenario",
        frameon=True,
        facecolor="#ffffff",
        edgecolor="#dddddd",
        framealpha=0.9,
        fontsize=9,
    )
    legend_scenarios.get_title().set_weight("bold")
    ax_top.add_artist(legend_scenarios)
    legend_times = ax_top.legend(
        handles=time_handles,
        loc="lower left",
        bbox_to_anchor=(0.40, 0.05),
        title="Integration time",
        frameon=True,
        facecolor="#ffffff",
        edgecolor="#dddddd",
        framealpha=0.9,
        fontsize=9,
    )
    legend_times.get_title().set_weight("bold")
    ax_top.set_title(
        "(a) Integrated molecular S/N relative to the pre-agricultural baseline",
        fontsize=12,
        pad=12,
        fontweight="bold",
    )

    # Bottom panel: A3 only, with both molecule templates on the same LIFE
    # instrument. The x limit expands when a threshold would otherwise fall
    # outside the plot, which is important for the Earth--Sun benchmark.
    crossings = []
    for molecule in TARGETS:
        row = _find_total(total, "A3", molecule)
        if row is None:
            continue
        snr_reference = float(row["snr_10h"])
        for threshold, _ in THRESHOLDS:
            crossings.append(10.0 * (threshold / snr_reference) ** 2)
    x_max = max(1_000.0, 10.0 ** np.ceil(np.log10(max(crossings) * 1.2)))
    hours_grid = np.logspace(0.0, np.log10(x_max), 500)

    for molecule in TARGETS:
        row = _find_total(total, "A3", molecule)
        if row is None:
            continue
        snr_reference = float(row["snr_10h"])
        snr_projection = snr_reference * np.sqrt(hours_grid / 10.0)
        visible = snr_projection <= 6.2
        ax_bottom.plot(
            hours_grid[visible],
            snr_projection[visible],
            color=MOLECULE_COLOURS[molecule],
            linewidth=2.4,
            label=f"{TARGET_LABELS[molecule]} full LIFE grid",
            zorder=3,
        )
        for hours in TIME_HOURS:
            value = float(row[f"snr_{int(hours)}h"])
            if value <= 6.2:
                ax_bottom.scatter(
                    hours,
                    value,
                    marker="D",
                    s=70,
                    color=MOLECULE_COLOURS[molecule],
                    edgecolors="#222222",
                    zorder=4,
                )
        for threshold, _ in THRESHOLDS:
            crossing = 10.0 * (threshold / snr_reference) ** 2
            if 1.0 <= crossing <= x_max:
                ax_bottom.scatter(
                    [crossing],
                    [threshold],
                    marker="D",
                    s=70,
                    color=MOLECULE_COLOURS[molecule],
                    edgecolors="#222222",
                    zorder=5,
                )
                ax_bottom.annotate(
                    f"{crossing:,.0f} h",
                    xy=(crossing, threshold),
                    xytext=(crossing * 0.55, threshold + 0.28),
                    fontsize=8.5,
                    color=MOLECULE_COLOURS[molecule],
                    bbox={
                        "boxstyle": "round,pad=0.22",
                        "facecolor": "#ffffff",
                        "edgecolor": MOLECULE_COLOURS[molecule],
                        "alpha": 0.9,
                    },
                    zorder=6,
                )

    for threshold, linestyle in THRESHOLDS:
        ax_bottom.axhline(
            threshold,
            color=PALETTE["scenario_pink"],
            linestyle=linestyle,
            linewidth=1.2,
            alpha=0.85,
        )
        label_x = 10.0 ** (np.log10(x_max) * 0.78)
        ax_bottom.text(
            label_x,
            threshold + 0.1,
            f"S/N = {threshold:g}",
            color=PALETTE["scenario_pink"],
            fontsize=9,
        )

    ax_bottom.set_xscale("log")
    ax_bottom.set_xlim(1.0, x_max)
    x_ticks = _time_ticks(x_max)
    ax_bottom.set_xticks(x_ticks)
    ax_bottom.set_xticklabels([_time_tick_label(tick) for tick in x_ticks], fontsize=8.5)
    ax_bottom.set_ylim(0.0, 6.2)
    ax_bottom.set_xlabel("Integration time [h]")
    ax_bottom.set_ylabel("Integrated molecular-excess S/N")
    ax_bottom.grid(True, which="both", linestyle=":", color="#dddddd")
    ax_bottom.legend(
        title="A3 molecular template",
        frameon=True,
        facecolor="#ffffff",
        edgecolor="#dddddd",
        framealpha=0.9,
        fontsize=9,
        title_fontproperties={"weight": "bold"},
        loc="upper left",
    )
    ax_bottom.set_title(
        "(b) Integration time required to reach fixed S/N thresholds in A3",
        fontsize=12,
        pad=12,
        fontweight="bold",
    )

    fig.suptitle(FIGURE_TITLES[campaign], fontsize=15, y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.965))

    plots_dir = output_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    stem = f"life_classic_snr_integrated_{campaign}"
    png_path = plots_dir / f"{stem}.png"
    pdf_path = plots_dir / f"{stem}.pdf"
    fig.savefig(png_path, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {png_path.relative_to(ef.REPO)}")
    print(f"saved {pdf_path.relative_to(ef.REPO)}")
    return png_path, pdf_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign", choices=tuple(CAMPAIGNS), default="proxima")
    args = parser.parse_args()

    output_dir, products_path, target_label = _campaign_paths(args.campaign)
    with np.load(products_path, allow_pickle=True) as products:
        rows = compute_rows(products, args.campaign, products_path)
        table_path = output_dir / "tables" / "life_classic_snr_integrated_table.csv"
        write_rows(rows, table_path)
        plot_rows(rows, args.campaign, target_label, output_dir)


if __name__ == "__main__":
    main()
