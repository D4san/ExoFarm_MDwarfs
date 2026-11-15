"""Plot integrated molecular-template S/N for the TRAPPIST-1e branch.

The older peak-S/N product is retained for audit/legacy comparisons.  This
module uses the full counterfactual molecular signal on each instrument's
observational wavelength grid and reports:

* an instrument-total S/N over every valid bin;
* a band S/N for the existing diagnostic windows; and
* A3 integration-time projections for the instrument totals.

The current JWST noise products provide per-bin errors but no covariance
matrix, so the calculation is explicitly a diagonal-noise diagnostic.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE


NOTEBOOK_DIR = Path(__file__).resolve().parent
PLOTS_DIR = NOTEBOOK_DIR / "POSEIDON_output" / "pure_spectra" / "plots"
SYNTHETIC_DATA_DIR = (
    NOTEBOOK_DIR
    / "POSEIDON_output"
    / "TRAPPIST-1e"
    / "synthetic_data"
    / "base_1transit"
)

SUMMARY_CSV = PLOTS_DIR / "trappist1e_molecular_snr_by_instrument.csv"
PLOT_STEM = "trappist1e_molecular_snr_by_instrument"
TRANSIT_COUNTS = (1, 10, 100)
SCENARIOS = ("A1", "A2", "A3")
MOLECULES = ("N2O", "NH3")

INSTRUMENTS = {
    "NIRSpec_PRISM": {
        "label": "NIRSpec PRISM",
        "short_label": "NIRSpec",
        "path": SYNTHETIC_DATA_DIR / "TRAPPIST-1e_flat_NIRSpec_Prism_1_transits.dat",
        "colour": PALETTE["deep_space_blue"],
        "linestyle": "-",
    },
    "MIRI_LRS": {
        "label": "MIRI LRS",
        "short_label": "MIRI",
        "path": SYNTHETIC_DATA_DIR / "TRAPPIST-1e_flat_MIRI_LRS_1_transits.dat",
        "colour": PALETTE["golden_orange"],
        "linestyle": "--",
    },
}

MOLECULE_LABELS = {"N2O": r"N$_2$O", "NH3": r"NH$_3$"}
# Keep the projection-row colours aligned with the legacy S/N figure.  The
# line style distinguishes the instrument while the colour identifies the
# molecule across all four A3 curves.
MOLECULE_COLOURS = {
    "N2O": PALETTE["terracotta_mauve"],
    "NH3": PALETTE["charcoal_violet"],
}
SCENARIO_MARKERS = {"A1": "o", "A2": "s", "A3": "^"}
SCENARIO_LABELS = {
    "A1": "A1 Current Earth",
    "A2": "A2 Moderate ExoFarm",
    "A3": "A3 Extreme ExoFarm",
}
TRANSIT_COLOURS = {
    1: PALETTE["scenario_cyan"],
    10: PALETTE["scenario_green"],
    100: PALETTE["scenario_violet"],
}

# These are the same windows used by the molecular residual/peak diagnostic.
# Here they are secondary decomposition rows; the instrument-total rows do not
# depend on these boundaries.
MOLECULAR_SIGNAL_WINDOWS = {
    "N2O": (
        ("N2O_2p6_3p0", 2.60, 3.00),
        ("N2O_4p3_4p8", 4.30, 4.80),
        ("N2O_7p5_9p0", 7.50, 9.00),
    ),
    "NH3": (
        ("NH3_9p0_10p0", 9.00, 10.00),
        ("NH3_10p0_11p2", 10.00, 11.20),
        ("NH3_11p2_12p0", 11.20, 12.00),
    ),
}

CSV_FIELDS = (
    "scenario",
    "molecule",
    "aggregation",
    "instrument",
    "band_id",
    "band_min_micron",
    "band_max_micron",
    "n_bins",
    "covariance_mode",
    "noise_source",
    "snr_1transit",
    "snr_10transit",
    "snr_100transit",
)


def _load_noise_grid(path: Path) -> dict[str, np.ndarray | str]:
    """Load wavelength centers, half-bin widths, and 1-transit errors."""

    data = np.loadtxt(path, skiprows=1)
    if data.ndim != 2 or data.shape[1] < 4:
        raise ValueError(f"Unexpected noise table shape for {path}: {data.shape}")
    return {
        "wavelength": data[:, 0],
        "half_width": data[:, 1],
        "sigma": data[:, 3],
        "path": str(path),
    }


def _load_all_noise_grids() -> dict[str, dict[str, np.ndarray | str]]:
    return {
        name: _load_noise_grid(config["path"])
        for name, config in INSTRUMENTS.items()
    }


def _rebin_signal_to_observation_grid(
    wavelength_native: np.ndarray,
    signal_native: np.ndarray,
    wavelength_obs: np.ndarray,
    half_width_obs: np.ndarray,
) -> np.ndarray:
    """Average the native model signal inside each observed spectral bin."""

    result = np.full(wavelength_obs.shape, np.nan, dtype=float)
    for index, (center, half_width) in enumerate(
        zip(wavelength_obs, half_width_obs)
    ):
        left = center - abs(half_width)
        right = center + abs(half_width)
        mask = (wavelength_native >= left) & (wavelength_native <= right)
        if np.any(mask):
            result[index] = float(np.nanmean(signal_native[mask]))
        elif wavelength_native[0] <= center <= wavelength_native[-1]:
            result[index] = float(np.interp(center, wavelength_native, signal_native))
    return result


def _snr_from_mask(
    signal: np.ndarray,
    sigma: np.ndarray,
    mask: np.ndarray,
) -> tuple[float, int]:
    valid = mask & np.isfinite(signal) & np.isfinite(sigma) & (sigma > 0.0)
    if not np.any(valid):
        return float("nan"), 0
    per_bin = signal[valid] / sigma[valid]
    return float(np.sqrt(np.sum(per_bin**2))), int(np.count_nonzero(valid))


def _scaled_values(snr_1transit: float) -> dict[str, float]:
    return {
        f"snr_{transits}transit": (
            float(snr_1transit * np.sqrt(transits))
            if np.isfinite(snr_1transit)
            else float("nan")
        )
        for transits in TRANSIT_COUNTS
    }


def compute_snr_rows(products, counterfactual_spectra) -> list[dict[str, object]]:
    """Compute instrument-total and band-integrated S/N rows."""

    noise_grids = _load_all_noise_grids()
    wavelength_native = np.asarray(products["wl"])
    spectra = products["spectra"]
    rows: list[dict[str, object]] = []

    for scenario in SCENARIOS:
        for molecule in MOLECULES:
            signal_native = (
                np.asarray(spectra[scenario])
                - np.asarray(counterfactual_spectra[molecule][scenario])
            )
            for instrument, grid in noise_grids.items():
                wavelength_obs = np.asarray(grid["wavelength"])
                half_width_obs = np.asarray(grid["half_width"])
                sigma = np.asarray(grid["sigma"])
                signal_obs = _rebin_signal_to_observation_grid(
                    wavelength_native,
                    signal_native,
                    wavelength_obs,
                    half_width_obs,
                )
                coverage_mask = np.ones(wavelength_obs.shape, dtype=bool)
                total_snr, n_total = _snr_from_mask(
                    signal_obs,
                    sigma,
                    coverage_mask,
                )
                total_row = {
                    "scenario": scenario,
                    "molecule": molecule,
                    "aggregation": "instrument_total",
                    "instrument": instrument,
                    "band_id": "full_coverage",
                    "band_min_micron": float(wavelength_obs[0]),
                    "band_max_micron": float(wavelength_obs[-1]),
                    "n_bins": n_total,
                    "covariance_mode": "diagonal",
                    "noise_source": grid["path"],
                }
                total_row.update(_scaled_values(total_snr))
                rows.append(total_row)

                for band_id, band_min, band_max in MOLECULAR_SIGNAL_WINDOWS[molecule]:
                    band_mask = (wavelength_obs >= band_min) & (
                        wavelength_obs <= band_max
                    )
                    band_snr, n_band = _snr_from_mask(
                        signal_obs,
                        sigma,
                        band_mask,
                    )
                    if n_band == 0:
                        continue
                    band_row = {
                        "scenario": scenario,
                        "molecule": molecule,
                        "aggregation": "band",
                        "instrument": instrument,
                        "band_id": band_id,
                        "band_min_micron": band_min,
                        "band_max_micron": band_max,
                        "n_bins": n_band,
                        "covariance_mode": "diagonal",
                        "noise_source": grid["path"],
                    }
                    band_row.update(_scaled_values(band_snr))
                    rows.append(band_row)

    return rows


def write_summary_csv(rows: list[dict[str, object]]) -> None:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    with SUMMARY_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {SUMMARY_CSV}")


def _find_row(data: pd.DataFrame, scenario: str, molecule: str, instrument: str):
    matches = data[
        (data["scenario"] == scenario)
        & (data["molecule"] == molecule)
        & (data["instrument"] == instrument)
        & (data["aggregation"] == "instrument_total")
    ]
    if matches.empty:
        return None
    return matches.iloc[0]


def _apply_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["STIX Two Text", "STIXGeneral", "Times New Roman"],
            "mathtext.fontset": "stix",
            "axes.labelsize": 11,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "figure.titlesize": 13,
        }
    )


def plot_summary(rows: list[dict[str, object]] | None = None) -> tuple[Path, Path]:
    """Create the two-panel integrated-S/N comparison figure."""

    _apply_style()
    if rows is None:
        data = pd.read_csv(SUMMARY_CSV)
    else:
        data = pd.DataFrame(rows)

    category_order = (
        ("N2O", "NIRSpec_PRISM"),
        ("N2O", "MIRI_LRS"),
        ("NH3", "NIRSpec_PRISM"),
        ("NH3", "MIRI_LRS"),
    )
    category_labels = [
        f"{MOLECULE_LABELS[molecule]}\n{INSTRUMENTS[instrument]['short_label']}"
        for molecule, instrument in category_order
    ]
    total = data[data["aggregation"] == "instrument_total"]

    fig, (ax_top, ax_bottom) = plt.subplots(
        2,
        1,
        figsize=(8.5, 9.5),
        dpi=300,
        gridspec_kw={"height_ratios": [1.0, 0.78]},
    )

    scenario_offsets = {"A1": -0.20, "A2": 0.0, "A3": 0.20}
    for category_index, (molecule, instrument) in enumerate(category_order):
        for scenario in SCENARIOS:
            row = _find_row(total, scenario, molecule, instrument)
            if row is None:
                continue
            for transits in TRANSIT_COUNTS:
                value = float(row[f"snr_{transits}transit"])
                if not np.isfinite(value) or value <= 0.0:
                    continue
                ax_top.scatter(
                    category_index + scenario_offsets[scenario],
                    value,
                    color=TRANSIT_COLOURS[transits],
                    marker=SCENARIO_MARKERS[scenario],
                    s=105,
                    edgecolors="#222222",
                    linewidths=0.7,
                    alpha=0.95,
                    zorder=3,
                )

    value_columns = [f"snr_{transits}transit" for transits in TRANSIT_COUNTS]
    positive_values = total[value_columns].to_numpy(dtype=float).ravel()
    positive_values = positive_values[np.isfinite(positive_values) & (positive_values > 0)]
    lower = max(float(np.nanmin(positive_values)) * 0.45, 1e-5)
    upper = max(float(np.nanmax(positive_values)) * 1.35, 3.5)
    ax_top.set_yscale("log")
    ax_top.set_ylim(lower, upper)
    ax_top.set_xlim(-0.6, len(category_order) - 0.4)
    ax_top.set_xticks(range(len(category_order)))
    ax_top.set_xticklabels(category_labels)
    ax_top.set_ylabel("Integrated molecular-excess S/N", labelpad=8)
    ax_top.set_xlabel("Molecule and instrument")
    ax_top.set_title(
        "(a) Integrated molecular S/N relative to the pre-agricultural baseline",
        fontsize=12,
        pad=12,
        fontweight="bold",
    )
    ax_top.grid(True, which="both", axis="both", linestyle=":", color="#dddddd", alpha=0.7)
    ax_top.axvline(1.5, color="#888888", linestyle="--", linewidth=0.9, alpha=0.5)

    scenario_handles = [
        Line2D(
            [0], [0], marker=SCENARIO_MARKERS[scenario], color="w",
            label=SCENARIO_LABELS[scenario], markerfacecolor="#888888",
            markeredgecolor="#222222", markersize=8, linestyle="None",
        )
        for scenario in SCENARIOS
    ]
    transit_handles = [
        Line2D(
            [0], [0], marker="o", color="w", label=f"{transits} transit" if transits == 1 else f"{transits} transits",
            markerfacecolor=TRANSIT_COLOURS[transits], markeredgecolor="#222222",
            markersize=8, linestyle="None",
        )
        for transits in TRANSIT_COUNTS
    ]
    legend_scenarios = ax_top.legend(
        handles=scenario_handles,
        loc="lower left",
        bbox_to_anchor=(0.01, 0.01),
        title="Scenario",
        frameon=True,
        fontsize=8,
    )
    ax_top.add_artist(legend_scenarios)
    ax_top.legend(
        handles=transit_handles,
        loc="lower left",
        bbox_to_anchor=(0.39, 0.01),
        title="Transits",
        frameon=True,
        fontsize=8,
    )

    n_transits_grid = np.logspace(0, 6.0, 500)
    for molecule, instrument in category_order:
        row = _find_row(total, "A3", molecule, instrument)
        if row is None:
            continue
        snr_1 = float(row["snr_1transit"])
        if not np.isfinite(snr_1) or snr_1 <= 0.0:
            continue
        snr_projection = snr_1 * np.sqrt(n_transits_grid)
        visible = (snr_projection >= 1e-4) & (snr_projection <= 5.8)
        instrument_style = INSTRUMENTS[instrument]
        ax_bottom.plot(
            n_transits_grid[visible],
            snr_projection[visible],
            color=MOLECULE_COLOURS[molecule],
            linestyle=instrument_style["linestyle"],
            linewidth=2.0,
            label=f"{MOLECULE_LABELS[molecule]} {instrument_style['short_label']}",
        )
        for transits in TRANSIT_COUNTS:
            row_value = float(row[f"snr_{transits}transit"])
            if 1e-4 <= row_value <= 5.8:
                ax_bottom.scatter(
                    transits,
                    row_value,
                    color=MOLECULE_COLOURS[molecule],
                    marker="D",
                    s=55,
                    edgecolors="#222222",
                    linewidths=0.6,
                    zorder=4,
                )

    # Mark the integration time required to reach the two reference
    # thresholds, following the annotation convention of the legacy figure.
    # Every curve receives both labels so the instrument comparison remains
    # quantitative when four molecule--instrument combinations are shown.
    for molecule, instrument in category_order:
        row = _find_row(total, "A3", molecule, instrument)
        if row is None:
            continue
        snr_1 = float(row["snr_1transit"])
        if not np.isfinite(snr_1) or snr_1 <= 0.0:
            continue
        for threshold in (3.0, 5.0):
            required_transits = (threshold / snr_1) ** 2
            if not 1.0 <= required_transits <= 1_000_000.0:
                continue
            colour = MOLECULE_COLOURS[molecule]
            ax_bottom.scatter(
                required_transits,
                threshold,
                color=colour,
                edgecolor="#222222",
                marker="D",
                s=62,
                zorder=5,
            )
            y_offset = 10 if molecule == "N2O" else -20
            x_offset = -30 if (
                molecule == "NH3"
                and instrument == "NIRSpec_PRISM"
                and threshold == 5.0
            ) else 0
            ax_bottom.annotate(
                f"{int(round(required_transits)):,}",
                xy=(required_transits, threshold),
                xytext=(x_offset, y_offset),
                textcoords="offset points",
                ha="center",
                va="bottom" if y_offset > 0 else "top",
                color=colour,
                fontsize=7.5,
                fontweight="bold",
                bbox={
                    "boxstyle": "round,pad=0.2",
                    "facecolor": "#ffffff",
                    "edgecolor": colour,
                    "alpha": 0.9,
                    "linewidth": 0.5,
                },
                zorder=6,
            )

    ax_bottom.set_xscale("log")
    ax_bottom.set_xlim(1.0, 1_000_000.0)
    ax_bottom.set_ylim(1e-4, 5.8)
    ax_bottom.set_xlabel("Number of transits")
    ax_bottom.set_ylabel("Integrated molecular-excess S/N")
    ax_bottom.set_title(
        "(b) Transits required to reach fixed S/N thresholds in A3",
        fontsize=12,
        pad=12,
        fontweight="bold",
    )
    ax_bottom.grid(True, which="both", axis="both", linestyle=":", color="#dddddd", alpha=0.7)
    ax_bottom.axhline(3.0, color=PALETTE["scenario_pink"], linestyle="--", linewidth=1.0, alpha=0.8)
    ax_bottom.axhline(5.0, color=PALETTE["scenario_pink"], linestyle="-.", linewidth=1.0, alpha=0.8)
    ax_bottom.text(
        1.5,
        3.15,
        "S/N = 3",
        color=PALETTE["scenario_pink"],
        fontsize=9,
        fontweight="semibold",
    )
    ax_bottom.text(
        1.5,
        5.15,
        "S/N = 5",
        color=PALETTE["scenario_pink"],
        fontsize=9,
        fontweight="semibold",
    )
    ax_bottom.legend(
        loc="lower right",
        title="A3 molecular template",
        frameon=True,
        fontsize=8,
    )

    fig.text(
        0.01,
        0.005,
        "Diagonal-noise diagnostic; full coverage uses the instrument's observed wavelength grid.",
        fontsize=7.5,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.025, 1, 1))

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    png_path = PLOTS_DIR / f"{PLOT_STEM}.png"
    pdf_path = PLOTS_DIR / f"{PLOT_STEM}.pdf"
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {png_path}")
    print(f"Saved {pdf_path}")
    return png_path, pdf_path


def generate_from_products(products, counterfactual_spectra) -> list[dict[str, object]]:
    """Export the table and plot without rebuilding POSEIDON products."""

    rows = compute_snr_rows(products, counterfactual_spectra)
    write_summary_csv(rows)
    plot_summary(rows)
    return rows


def main() -> None:
    """Standalone entry point for the integrated-S/N product."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--from-table",
        action="store_true",
        help="Regenerate only the figure from the existing S/N CSV.",
    )
    args = parser.parse_args()
    if args.from_table:
        plot_summary()
        return

    from plot_pure_transmission_spectra import (
        build_counterfactual_products,
        build_system_products,
    )

    products = build_system_products("TRAPPIST-1e", 0.5, 20.0, 10000.0)
    counterfactual_spectra, _ = build_counterfactual_products("TRAPPIST-1e", products)
    generate_from_products(products, counterfactual_spectra)


if __name__ == "__main__":
    main()
