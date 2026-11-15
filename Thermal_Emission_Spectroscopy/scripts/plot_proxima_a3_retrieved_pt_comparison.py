"""Compare recovered Proxima A3 P--T profiles with the VULCAN input profile.

This is a post-processing plot only: it reads the saved 10 h and 100 h
POSEIDON posterior summaries and does not run a retrieval.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "Transmission_Spectroscopy" / "notebooks"))
from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE


CAMPAIGN = REPO / "Thermal_Emission_Spectroscopy" / "outputs" / "life_proxima_b_earthlike_v1"
SAMPLES = (
    CAMPAIGN / "retrievals" / "POSEIDON_output" / "proxima_b_earthlike"
    / "retrievals" / "samples"
)
PLOTS = CAMPAIGN / "plots"
TABLES = CAMPAIGN / "tables"
EXPECTED_TRUE_PT_MD5 = "0865b6b784915b5bbffca40096f8a90b"
RUNS = {
    10: {
        "tag": "proxima_A3_10h_O2_fixedBlack1bar_noxtol",
        "color": PALETTE["terracotta_mauve"],
    },
    100: {
        "tag": "proxima_A3_100h_O2_fixedBlack1bar_noxtol",
        "color": PALETTE["charcoal_violet"],
    },
}
OUTPUT_STEM = "retrieval_A3_recovered_PT_10_vs_100h_proxima"

mpl.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["STIX Two Text", "STIXGeneral", "Times New Roman"],
        "mathtext.fontset": "stix",
        "axes.unicode_minus": False,
        "axes.linewidth": 0.8,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.top": True,
        "ytick.right": True,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)


def md5(path: Path) -> str:
    digest = hashlib.md5()
    # Git's Windows checkout uses CRLF here; the campaign checksum was
    # recorded from the normalized LF text used on the Linux/WSL run.
    digest.update(path.read_bytes().replace(b"\r\n", b"\n"))
    return digest.hexdigest()


def load_finite_table(path: Path, *, skiprows: int) -> np.ndarray:
    if not path.is_file() or path.stat().st_size == 0:
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    if any(token in text.lower().split() for token in ("nan", "inf", "infinity")):
        raise ValueError(f"Non-finite token in {path}")
    values = np.loadtxt(path, skiprows=skiprows, ndmin=2)
    if values.size == 0 or not np.isfinite(values).all():
        raise ValueError(f"Empty or non-finite table: {path}")
    return values


def main() -> None:
    expected = json.loads((CAMPAIGN / "manifest.json").read_text(encoding="utf-8"))
    true_profile_record = expected["profiles"]["A3"]["PT"]
    true_profile_path = REPO / true_profile_record["path"]
    observed_md5 = md5(true_profile_path)
    if observed_md5 != EXPECTED_TRUE_PT_MD5 or observed_md5 != true_profile_record["md5"]:
        raise ValueError("A3 VULCAN PT profile checksum differs from the Stage III manifest")

    true_table = load_finite_table(true_profile_path, skiprows=1)
    if true_table.shape[1] != 3:
        raise ValueError(f"Expected ALT/P/T columns in {true_profile_path}")
    true_pressure = true_table[:, 1]
    true_temperature = true_table[:, 2]
    if np.any(true_pressure <= 0) or np.any(np.diff(true_pressure) >= 0):
        raise ValueError("VULCAN pressure grid must be positive and strictly decreasing")

    recovered: dict[int, dict[str, np.ndarray | float | int | str]] = {}
    for hours, config in RUNS.items():
        tag = str(config["tag"])
        pt_path = SAMPLES / f"{tag}_{tag}_PT_retrieved.txt"
        table = load_finite_table(pt_path, skiprows=1)
        if table.shape != (100, 6):
            raise ValueError(f"Unexpected recovered PT dimensions {table.shape}: {pt_path}")
        pressure = table[:, 0]
        if np.any(pressure <= 0) or np.any(np.diff(pressure) >= 0):
            raise ValueError(f"Invalid recovered pressure grid: {pt_path}")

        # Columns are pointwise -2 sigma, -1 sigma, median, +1 sigma, +2 sigma.
        inside = (pressure >= true_pressure.min()) & (pressure <= true_pressure.max())
        common_pressure = pressure[inside]
        true_on_grid = np.interp(
            np.log10(common_pressure),
            np.log10(true_pressure[::-1]),
            true_temperature[::-1],
        )
        delta = table[inside, 3] - true_on_grid
        within_1sigma = (
            (true_on_grid >= table[inside, 2]) & (true_on_grid <= table[inside, 4])
        )
        within_2sigma = (
            (true_on_grid >= table[inside, 1]) & (true_on_grid <= table[inside, 5])
        )
        recovered[hours] = {
            "path": pt_path.relative_to(REPO).as_posix(),
            "table": table,
            "pressure_common": common_pressure,
            "true_common": true_on_grid,
            "delta": delta,
            "rms_delta_K": float(np.sqrt(np.mean(delta**2))),
            "median_abs_delta_K": float(np.median(np.abs(delta))),
            "max_abs_delta_K": float(np.max(np.abs(delta))),
            "median_68pct_width_K": float(np.median(table[inside, 4] - table[inside, 2])),
            "median_95pct_width_K": float(np.median(table[inside, 5] - table[inside, 1])),
            "within_1sigma_fraction": float(np.mean(within_1sigma)),
            "within_2sigma_fraction": float(np.mean(within_2sigma)),
            "common_levels": int(common_pressure.size),
        }

    PLOTS.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    fig, (ax, residual_ax) = plt.subplots(
        2, 1, figsize=(7.6, 8.2), sharey=True,
        gridspec_kw={"height_ratios": [2.15, 1.0], "hspace": 0.08},
    )

    # The retrieved pressure grid extends slightly above the VULCAN grid;
    # restrict the comparison axes to their common range for a fair overlay.
    common_top = max(float(true_pressure.min()), max(float(v["table"][-1, 0]) for v in recovered.values()))
    common_bottom = min(float(true_pressure.max()), min(float(v["table"][0, 0]) for v in recovered.values()))
    visible_true = (true_pressure >= common_top) & (true_pressure <= common_bottom)
    ax.plot(
        true_temperature[visible_true], true_pressure[visible_true],
        color=PALETTE["deep_moss"], lw=2.1, ls="--", zorder=5,
        label="VULCAN A3 input (reference)",
    )

    for hours, config in RUNS.items():
        entry = recovered[hours]
        table = np.asarray(entry["table"])
        color = str(config["color"])
        ax.fill_betweenx(table[:, 0], table[:, 1], table[:, 5], color=color, alpha=0.09, lw=0)
        ax.fill_betweenx(table[:, 0], table[:, 2], table[:, 4], color=color, alpha=0.20, lw=0)
        ax.plot(table[:, 3], table[:, 0], color=color, lw=1.9, label=f"{hours} h retrieved median")

        p = np.asarray(entry["pressure_common"])
        true_t = np.asarray(entry["true_common"])
        delta = np.asarray(entry["delta"])
        lower_1 = table[(table[:, 0] >= common_top) & (table[:, 0] <= common_bottom), 2]
        upper_1 = table[(table[:, 0] >= common_top) & (table[:, 0] <= common_bottom), 4]
        lower_2 = table[(table[:, 0] >= common_top) & (table[:, 0] <= common_bottom), 1]
        upper_2 = table[(table[:, 0] >= common_top) & (table[:, 0] <= common_bottom), 5]
        band_pressure = table[(table[:, 0] >= common_top) & (table[:, 0] <= common_bottom), 0]
        true_band = np.interp(
            np.log10(band_pressure), np.log10(p[::-1]), true_t[::-1]
        )
        residual_ax.fill_betweenx(
            band_pressure, lower_2 - true_band, upper_2 - true_band,
            color=color, alpha=0.08, lw=0,
        )
        residual_ax.fill_betweenx(
            band_pressure, lower_1 - true_band, upper_1 - true_band,
            color=color, alpha=0.19, lw=0,
        )
        residual_ax.plot(delta, p, color=color, lw=1.6, label=f"{hours} h median − VULCAN")

    ax.set_xscale("linear")
    ax.set_yscale("log")
    ax.set_ylim(common_bottom, common_top)
    ax.set_xlim(175, 325)
    ax.set_ylabel("Pressure [bar]")
    ax.set_xlabel("")
    ax.legend(loc="upper right", frameon=True, framealpha=0.96, fontsize=8.5)
    ax.grid(which="major", alpha=0.24, lw=0.55)
    ax.grid(which="minor", axis="y", alpha=0.12, lw=0.4)

    residual_ax.axvline(0.0, color="0.25", lw=0.9, ls="--")
    residual_ax.set_xscale("linear")
    residual_ax.set_ylabel("Pressure [bar]")
    residual_ax.set_xlabel(r"Retrieved median $T$ − VULCAN $T$ [K]")
    residual_ax.grid(which="major", alpha=0.24, lw=0.55)
    residual_ax.grid(which="minor", axis="y", alpha=0.12, lw=0.4)
    residual_ax.legend(loc="lower right", frameon=True, framealpha=0.96, fontsize=8.2)

    fig.suptitle("Proxima b A3 — recovered thermal profiles", x=0.13, y=0.985, ha="left", fontsize=14)
    fig.text(
        0.13, 0.95,
        "POSEIDON Madhu PT (6 parameters), isochemical abundances; shading shows pointwise 68% and 95% intervals",
        ha="left", va="top", fontsize=8.8,
    )
    fig.text(
        0.5, 0.015,
        "Comparison restricted to the shared VULCAN/retrieval pressure range; the two retrievals use independent 31-bin noise realizations.",
        ha="center", fontsize=8.2,
    )
    fig.subplots_adjust(left=0.13, right=0.98, bottom=0.10, top=0.91, hspace=0.08)
    for ext in ("png", "pdf"):
        fig.savefig(PLOTS / f"{OUTPUT_STEM}.{ext}", dpi=240, bbox_inches="tight")
    plt.close(fig)

    summary = {
        "reference_profile": true_profile_path.relative_to(REPO).as_posix(),
        "reference_profile_md5": observed_md5,
        "reference_columns": "ALT_km, P_bar, T_K",
        "retrieved_columns": "P_bar, T_minus_2sigma_K, T_minus_1sigma_K, T_median_K, T_plus_1sigma_K, T_plus_2sigma_K",
        "retrieval_model": "POSEIDON Madhu six-parameter PT; isochemical abundances",
        "comparison_pressure_range_bar": [common_top, common_bottom],
        "runs": {
            str(hours): {
                key: value for key, value in entry.items()
                if key not in {"table", "pressure_common", "true_common", "delta"}
            }
            for hours, entry in recovered.items()
        },
        "interpretation_caveat": "Pointwise posterior intervals; fractions inside bands are descriptive per-level checks, not simultaneous confidence coverage.",
    }
    summary_path = TABLES / f"{OUTPUT_STEM}_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    for hours, entry in recovered.items():
        print(
            f"{hours} h: RMS(Tmedian - VULCAN)={entry['rms_delta_K']:.2f} K; "
            f"median |delta T|={entry['median_abs_delta_K']:.2f} K; "
            f"max |delta T|={entry['max_abs_delta_K']:.2f} K; "
            f"median pointwise 68% width={entry['median_68pct_width_K']:.2f} K; "
            f"truth inside pointwise 68%/95% bands="
            f"{entry['within_1sigma_fraction']:.1%}/{entry['within_2sigma_fraction']:.1%}"
        )
    print(f"Figure: {PLOTS / (OUTPUT_STEM + '.png')}")
    print(f"Summary: {summary_path}")


if __name__ == "__main__":
    main()
