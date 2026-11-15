"""Overlay JWST 1-sigma noise curves on the existing TRAPPIST-1e signal panels.

The canonical spectrum and molecular-signal figure remains the raster background.
Only the two lower signal panels receive noise curves. Their vertical limits are
calibrated from the visible ticks and frame of the source image, then fixed so
large JWST uncertainties are shown clipped at the panel boundary.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from PIL import Image

from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE


NOTEBOOK_DIR = Path(__file__).resolve().parent
REPO_ROOT = NOTEBOOK_DIR.parents[1]
DATA_DIR = (
    NOTEBOOK_DIR
    / "POSEIDON_output"
    / "TRAPPIST-1e"
    / "synthetic_data"
    / "base_1transit"
)
SOURCE_FIGURE = (
    NOTEBOOK_DIR
    / "POSEIDON_output"
    / "pure_spectra"
    / "plots"
    / "trappist1e_pure_a0_molecular_residuals_v2.png"
)
OUTPUT_DIR = SOURCE_FIGURE.parent
TRANSIT_COUNTS = (10, 20, 100)
INSTRUMENTS = {
    "NIRSpec_PRISM": {
        "label": "NIRSpec PRISM",
        "pattern": (
            "TRAPPIST-1e_SYNTHETIC_JWST_NIRSpec_PRISM_"
            "Trappist_A3_Extreme_N_trans_{n}.dat"
        ),
        "linestyle": "-",
    },
    "MIRI_LRS": {
        "label": "MIRI LRS",
        "pattern": (
            "TRAPPIST-1e_SYNTHETIC_JWST_MIRI_LRS_"
            "Trappist_A3_Extreme_N_trans_{n}.dat"
        ),
        "linestyle": (0, (3.2, 1.8)),
    },
}
TRANSIT_COLOURS = {
    10: PALETTE["deep_space_blue"],
    20: PALETTE["rusty_spice"],
    100: PALETTE["dim_grey"],
}

# Pixel coordinates are from the native 3312 x 2304 canonical PNG. The y tick
# centres were calibrated against the plotted 0, 5, 10, 15 and 20 ppm gridlines.
SOURCE_IMAGE_SIZE = (3312, 2304)
SOURCE_FIGURE_SHA256 = "6409661ea9340099f93b82678af8b16f729949d5531cd547bb954cd0917affe0"
X_FRAME_PIXELS = (267.0, 3272.0)
SIGNAL_PANELS = {
    "N2O": {
        "frame_y_pixels": (1332.0, 1729.0),
        "tick_y_pixels": (1338.5, 1419.5, 1500.5, 1581.5, 1662.5),
        "tick_values_ppm": (20.0, 15.0, 10.0, 5.0, 0.0),
    },
    "NH3": {
        "frame_y_pixels": (1764.0, 2162.0),
        "tick_y_pixels": (1771.5, 1852.5, 1933.5, 2014.5, 2095.5),
        "tick_values_ppm": (20.0, 15.0, 10.0, 5.0, 0.0),
    },
}
PANEL_ALPHA = 0.56


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Overlay fixed-scale JWST 1-sigma noise curves for 10, 20 and "
            "100 transits on the N2O and NH3 panels of the existing figure."
        )
    )
    parser.add_argument(
        "--output-stem",
        default="trappist1e_jwst_transit_count_observations_A3",
        help="Output filename stem in the existing pure_spectra/plots folder.",
    )
    return parser.parse_args()


def read_observations() -> dict[tuple[str, int], dict[str, np.ndarray | Path]]:
    observations = {}
    for instrument, metadata in INSTRUMENTS.items():
        reference_wavelength = None
        reference_half_width = None
        for transit_count in TRANSIT_COUNTS:
            path = DATA_DIR / metadata["pattern"].format(n=transit_count)
            if not path.is_file():
                raise FileNotFoundError(f"Missing JWST synthetic dataset: {path}")
            values = np.loadtxt(path, ndmin=2)
            if values.shape[1] != 4 or not np.all(np.isfinite(values)):
                raise ValueError(
                    f"Expected finite wavelength, half-bin, depth and sigma "
                    f"columns in {path}"
                )
            wavelength, half_width, _depth, sigma = values.T
            if np.any(half_width <= 0) or np.any(sigma <= 0):
                raise ValueError(f"Non-positive bin width or sigma in {path}")
            if reference_wavelength is None:
                reference_wavelength = wavelength
                reference_half_width = half_width
            elif not np.array_equal(
                wavelength, reference_wavelength
            ) or not np.array_equal(half_width, reference_half_width):
                raise ValueError(
                    f"{instrument} datasets do not share channel centres: {path}"
                )
            observations[(instrument, transit_count)] = {
                "path": path,
                "wavelength": wavelength,
                "half_width": half_width,
                "sigma_ppm": sigma * 1e6,
            }
    return observations


def calibrated_panel_limits(panel: dict[str, tuple | list]) -> tuple[float, float]:
    """Map source-image frame edges to ppm using its labelled horizontal ticks."""
    pixel_to_value = np.polyfit(
        np.asarray(panel["tick_y_pixels"], dtype=float),
        np.asarray(panel["tick_values_ppm"], dtype=float),
        deg=1,
    )
    frame_top, frame_bottom = panel["frame_y_pixels"]
    lower = float(np.polyval(pixel_to_value, frame_bottom))
    upper = float(np.polyval(pixel_to_value, frame_top))
    return lower, upper


def add_signal_panel_axes(
    fig: matplotlib.figure.Figure,
    image_shape: tuple[int, int, int],
    name: str,
) -> matplotlib.axes.Axes:
    height, width, _channels = image_shape
    x_left, x_right = X_FRAME_PIXELS
    y_top, y_bottom = SIGNAL_PANELS[name]["frame_y_pixels"]
    axes = fig.add_axes(
        [
            x_left / width,
            1.0 - y_bottom / height,
            (x_right - x_left) / width,
            (y_bottom - y_top) / height,
        ],
        zorder=2,
    )
    axes.set_facecolor((1.0, 1.0, 1.0, 0.0))
    axes.set_xscale("log")
    axes.set_xlim(0.5, 20.0)
    axes.set_ylim(*calibrated_panel_limits(SIGNAL_PANELS[name]))
    axes.set_autoscale_on(False)
    axes.set_xticks([])
    axes.set_yticks([])
    for spine in axes.spines.values():
        spine.set_visible(False)
    return axes


def draw_noise_curves(
    axes: matplotlib.axes.Axes,
    observations: dict[tuple[str, int], dict[str, np.ndarray | Path]],
    panel_limits: tuple[float, float],
) -> dict[str, dict[str, float]]:
    lower_limit, upper_limit = panel_limits
    clipping = {}
    for (instrument, transit_count), values in observations.items():
        sigma = np.asarray(values["sigma_ppm"], dtype=float)
        wavelength = np.asarray(values["wavelength"], dtype=float)
        style = INSTRUMENTS[instrument]["linestyle"]

        # Saturate values at the original signal-panel limits. The note in the
        # lower-right panel identifies these edge segments as out-of-range noise.
        plus_curve = np.clip(sigma, lower_limit, upper_limit)
        minus_curve = np.clip(-sigma, lower_limit, upper_limit)
        axes.plot(
            wavelength,
            plus_curve,
            color=TRANSIT_COLOURS[transit_count],
            linestyle=style,
            linewidth=0.9,
            alpha=PANEL_ALPHA,
            solid_capstyle="round",
            zorder=10 + TRANSIT_COUNTS.index(transit_count),
        )
        axes.plot(
            wavelength,
            minus_curve,
            color=TRANSIT_COLOURS[transit_count],
            linestyle=style,
            linewidth=0.9,
            alpha=PANEL_ALPHA,
            solid_capstyle="round",
            zorder=10 + TRANSIT_COUNTS.index(transit_count),
        )
        clipping[f"{instrument}:{transit_count}"] = {
            "fraction_plus_sigma_above_panel": float(np.mean(sigma > upper_limit)),
            "fraction_minus_sigma_below_panel": float(np.mean(-sigma < lower_limit)),
        }
    return clipping


def add_legend(axes: matplotlib.axes.Axes) -> None:
    handles = [
        Line2D(
            [0],
            [0],
            color=TRANSIT_COLOURS[count],
            linewidth=1.3,
            label=f"{count} transits",
        )
        for count in TRANSIT_COUNTS
    ]
    handles.extend(
        Line2D(
            [0],
            [0],
            color=PALETTE["ink_black"],
            linewidth=1.3,
            linestyle=INSTRUMENTS[name]["linestyle"],
            label=INSTRUMENTS[name]["label"],
        )
        for name in INSTRUMENTS
    )
    axes.legend(
        handles=handles,
        title="Noise ±1σ · color: transit count · line: instrument",
        frameon=True,
        facecolor="white",
        framealpha=0.88,
        edgecolor="none",
        fontsize=7.1,
        title_fontsize=7.1,
        ncol=2,
        loc="upper right",
        borderpad=0.4,
        labelspacing=0.3,
        handlelength=1.5,
        columnspacing=0.8,
    )


def make_figure(
    observations: dict[tuple[str, int], dict[str, np.ndarray | Path]],
    output_stem: str,
) -> tuple[Path, Path, Path, dict[str, dict[str, float]]]:
    if not SOURCE_FIGURE.is_file():
        raise FileNotFoundError(f"Canonical signal figure not found: {SOURCE_FIGURE}")
    source_hash = sha256(SOURCE_FIGURE)
    if source_hash != SOURCE_FIGURE_SHA256:
        raise ValueError(
            "The source PNG changed; review and update the pixel calibration "
            "before overlaying noise curves."
        )
    source_image = np.asarray(Image.open(SOURCE_FIGURE).convert("RGB"))
    height, width, channels = source_image.shape
    if (width, height) != SOURCE_IMAGE_SIZE:
        raise ValueError(
            "The canonical image dimensions changed; update the pixel "
            f"calibration. Found {width}x{height}."
        )

    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["STIX Two Text", "STIXGeneral", "Times New Roman"],
            "mathtext.fontset": "stix",
        }
    )
    fig = plt.figure(figsize=(13.8, 9.6), dpi=240)
    fig.figimage(source_image, xo=0, yo=0, origin="upper", zorder=0)

    clipping_summary = {}
    panel_axes = {}
    for species in ("N2O", "NH3"):
        axes = add_signal_panel_axes(fig, source_image.shape, species)
        limits = calibrated_panel_limits(SIGNAL_PANELS[species])
        clipping_summary[species] = draw_noise_curves(axes, observations, limits)
        panel_axes[species] = axes

    add_legend(panel_axes["N2O"])
    panel_axes["NH3"].text(
        0.99,
        0.96,
        "At panel edge: σ exceeds the fixed range",
        transform=panel_axes["NH3"].transAxes,
        ha="right",
        va="top",
        fontsize=7.1,
        color=PALETTE["ink_black"],
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.86, "pad": 2.2},
        zorder=30,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    png_path = OUTPUT_DIR / f"{output_stem}.png"
    pdf_path = OUTPUT_DIR / f"{output_stem}.pdf"
    provenance_path = OUTPUT_DIR / f"{output_stem}.provenance.json"
    fig.savefig(png_path, dpi=240, facecolor="white")
    fig.savefig(pdf_path, facecolor="white")
    plt.close(fig)
    return png_path, pdf_path, provenance_path, clipping_summary


def write_provenance(
    path: Path,
    observations: dict[tuple[str, int], dict[str, np.ndarray | Path]],
    output_paths: tuple[Path, Path, Path, dict[str, dict[str, float]]],
    clipping_summary: dict[str, dict[str, float]],
) -> None:
    panel_limits = {
        name: list(calibrated_panel_limits(config))
        for name, config in SIGNAL_PANELS.items()
    }
    provenance = {
        "generated_on": date.today().isoformat(),
        "script": str(Path(__file__).resolve().relative_to(REPO_ROOT)),
        "target": "TRAPPIST-1e",
        "scenario": "A3 synthetic JWST noise over A0-A3 molecular signal panels",
        "observable": "transit depth uncertainty for (Rp/Rs)^2",
        "display_units": "ppm",
        "sigma_conversion": "sigma in .dat is dimensionless; multiply by 1e6",
        "transit_counts": list(TRANSIT_COUNTS),
        "instruments": list(INSTRUMENTS),
        "line_alpha": PANEL_ALPHA,
        "line_width_pt": 0.9,
        "curve_definition": (
            "Symmetric +1 sigma and -1 sigma curves for each wavelength channel; "
            "NIRSpec is solid, MIRI is dashed, and colour encodes transit count."
        ),
        "signal_panel_limits_ppm": panel_limits,
        "fixed_limits_method": (
            "Calibrated from the source PNG's 0, 5, 10, 15 and 20 ppm tick "
            "centres and panel-frame pixel coordinates; autoscaling is disabled."
        ),
        "out_of_range_display": (
            "Noise curves are clipped to the original molecular-signal panel "
            "limits. A curve on a panel edge means the corresponding ±1 sigma "
            "exceeds that fixed range; no values are inferred from the clipped segment."
        ),
        "clipping_fractions_by_species": clipping_summary,
        "observations": [
            {
                "file": str(values["path"].relative_to(REPO_ROOT)),
                "sha256": sha256(values["path"]),
                "instrument": instrument,
                "n_transits": transit_count,
                "n_channels": int(len(values["wavelength"])),
                "wavelength_range_um": [
                    float(np.min(values["wavelength"])),
                    float(np.max(values["wavelength"])),
                ],
                "sigma_range_ppm": [
                    float(np.min(values["sigma_ppm"])),
                    float(np.max(values["sigma_ppm"])),
                ],
                "uncertainty": "per-channel diagonal 1-sigma in synthetic data",
            }
            for (instrument, transit_count), values in observations.items()
        ],
        "source_figure": {
            "file": str(SOURCE_FIGURE.relative_to(REPO_ROOT)),
            "sha256": sha256(SOURCE_FIGURE),
            "image_dimensions": list(SOURCE_IMAGE_SIZE),
            "top_spectrum_panel": "retained unchanged from the canonical PNG",
            "lower_signal_panels": [
                "original N2O signal panel with noise curves overlaid",
                "original NH3 signal panel with noise curves overlaid",
            ],
        },
        "interpretation_limit": (
            "These are synthetic JWST noise estimates, not observed JWST data. "
            "The source signal figure is retained as a raster background."
        ),
        "outputs": [
            str(output.relative_to(REPO_ROOT))
            for output in output_paths[:2]
        ],
    }
    path.write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    args = parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.output_stem):
        raise ValueError("--output-stem may contain only letters, digits, '-' and '_'")
    observations = read_observations()
    output_paths = make_figure(observations, args.output_stem)
    write_provenance(output_paths[2], observations, output_paths, output_paths[3])
    for output in output_paths[:3]:
        print(f"saved {output.relative_to(REPO_ROOT)}")
    print(
        "Fixed signal-panel limits (ppm): "
        + json.dumps(
            {
                name: calibrated_panel_limits(config)
                for name, config in SIGNAL_PANELS.items()
            }
        )
    )


if __name__ == "__main__":
    main()

