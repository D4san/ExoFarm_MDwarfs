"""Compare canonical and fixed-bottom Proxima A3 LIFE posteriors.

The figure is an audit diagnostic: it overlays the canonical A3 retrieval and
the 2026-09-23 no-error-inflation/fixed-1-bar/no-x_tol rerun at 10 h and 240 h.
It does not replace the canonical retrieval atlas or promote the audit run.
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np


REPO = Path(__file__).resolve().parents[2]
STYLE_DIR = REPO / "Transmission_Spectroscopy" / "notebooks"
sys.path.insert(0, str(STYLE_DIR))
from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE

from retrieval_reference import log10_column_averaged_mixing_ratio


CAMPAIGN_DIR = (
    REPO / "Thermal_Emission_Spectroscopy" / "outputs"
    / "life_proxima_b_earthlike_v1"
)
RETRIEVAL_DIR = (
    CAMPAIGN_DIR / "retrievals" / "POSEIDON_output" / "proxima_b_earthlike"
    / "retrievals"
)
SAMPLES_DIR = RETRIEVAL_DIR / "samples"
RESULTS_DIR = RETRIEVAL_DIR / "results"
PROFILE_A0 = (
    REPO / "Transmission_Spectroscopy" / "profiles"
    / "Proxima_b_A0_PreAgri_chem.txt"
)
PLOTS_DIR = CAMPAIGN_DIR / "plots"

HOURS = (10, 240)
MOLECULES = ("N2O", "NH3")
MOLECULE_LABELS = {"N2O": r"N$_2$O", "NH3": r"NH$_3$"}

# A3 remains the scenario throughout. The dark companion hue separates the
# canonical setup from the fixed-bottom audit setup; A0 retains its project
# green as the external abundance reference.
CANONICAL_COLOR = PALETTE["terracotta_mauve"]
AUDIT_COLOR = PALETTE["scenario_pink"]
A0_COLOR = PALETTE["deep_moss"]

mpl.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["STIX Two Text", "STIXGeneral", "Times New Roman"],
        "mathtext.fontset": "stix",
        "axes.unicode_minus": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.8,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.top": True,
        "ytick.right": True,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)


def product_stem(hours: int, audit: bool) -> str:
    """Return the matching POSEIDON stem for one time/configuration pair."""
    base = f"proxima_A3_{hours}h"
    if audit:
        base += "_fixedP1bar_noxtol"
    return f"{base}_{base}"


def load_posterior(hours: int, audit: bool, molecule: str) -> np.ndarray:
    """Load and validate one equal-weight posterior abundance column."""
    stem = product_stem(hours, audit)
    path = SAMPLES_DIR / f"{stem}_samples.txt"
    if not path.is_file():
        raise FileNotFoundError(f"Missing posterior samples: {path}")

    header = [name.strip() for name in path.open(encoding="utf-8").readline().split("|")]
    column = f"log_{molecule}"
    if column not in header:
        raise ValueError(f"{column} is absent from {path.name}")
    values = np.loadtxt(path, skiprows=1, usecols=header.index(column))
    values = np.atleast_1d(np.asarray(values, dtype=float))
    if values.size < 2 or not np.all(np.isfinite(values)):
        raise ValueError(f"Invalid or non-finite posterior values in {path}")
    return values


def load_fit_metadata(hours: int, audit: bool) -> tuple[float, int]:
    """Read reduced chi-square and parameter count from the POSEIDON result."""
    stem = product_stem(hours, audit)
    path = RESULTS_DIR / f"{stem}_results.txt"
    if not path.is_file():
        raise FileNotFoundError(f"Missing retrieval result: {path}")
    text = path.read_text(encoding="utf-8", errors="replace")
    chi_match = re.search(r"chi\^2_red\s*=\s*([0-9.eE+-]+)", text)
    nparam_match = re.search(r"N_params\s*=\s*(\d+)", text)
    if chi_match is None or nparam_match is None:
        raise ValueError(f"Could not parse fit metadata from {path}")
    return float(chi_match.group(1)), int(nparam_match.group(1))


def summarize(values: np.ndarray) -> tuple[float, float, float]:
    """Return the posterior 16th, 50th, and 84th percentiles in log10 VMR."""
    low, median, high = np.percentile(values, (16.0, 50.0, 84.0))
    return float(low), float(median), float(high)


def interval_label(values: np.ndarray) -> str:
    """Format the median and central 68-percent interval compactly."""
    low, median, high = summarize(values)
    return f"{median:.2f} [{low:.2f}, {high:.2f}]"


def row_limits(samples: list[np.ndarray], reference: float) -> tuple[float, float]:
    """Set comparable x-limits while retaining A0 and nearly all samples."""
    tails = np.concatenate([np.percentile(values, (0.1, 99.9)) for values in samples])
    low = min(float(np.min(tails)), reference)
    high = max(float(np.max(tails)), reference)
    margin = max(0.08, 0.05 * (high - low))
    return low - margin, high + margin


def plot_posteriors() -> tuple[Path, Path]:
    """Generate the two-molecule, two-integration audit comparison."""
    profile_a0 = np.genfromtxt(PROFILE_A0, names=True)
    a0_effective = {
        molecule: log10_column_averaged_mixing_ratio(profile_a0, molecule)
        for molecule in MOLECULES
    }

    samples: dict[tuple[int, bool, str], np.ndarray] = {}
    fit: dict[tuple[int, bool], tuple[float, int]] = {}
    for hours in HOURS:
        for audit in (False, True):
            fit[(hours, audit)] = load_fit_metadata(hours, audit)
            for molecule in MOLECULES:
                samples[(hours, audit, molecule)] = load_posterior(
                    hours, audit, molecule
                )

    fig, axes = plt.subplots(2, 2, figsize=(11.4, 7.8), sharex="row")
    for row, molecule in enumerate(MOLECULES):
        molecule_samples = [
            samples[(hours, audit, molecule)]
            for hours in HOURS
            for audit in (False, True)
        ]
        x_left, x_right = row_limits(molecule_samples, a0_effective[molecule])
        bin_edges = np.linspace(x_left, x_right, 121)

        for col, hours in enumerate(HOURS):
            ax = axes[row, col]
            canonical = samples[(hours, False, molecule)]
            audit = samples[(hours, True, molecule)]
            canonical_chi2, _ = fit[(hours, False)]
            audit_chi2, _ = fit[(hours, True)]

            canonical_density, _ = np.histogram(
                canonical, bins=bin_edges, density=True
            )
            audit_density, _ = np.histogram(audit, bins=bin_edges, density=True)
            ax.stairs(
                canonical_density,
                bin_edges,
                baseline=0.0,
                fill=True,
                color=CANONICAL_COLOR,
                alpha=0.20,
                linewidth=1.0,
                zorder=2,
            )
            ax.stairs(
                audit_density,
                bin_edges,
                baseline=0.0,
                fill=True,
                color=AUDIT_COLOR,
                alpha=0.13,
                linestyle="--",
                linewidth=1.7,
                zorder=3,
            )

            _, canonical_median, _ = summarize(canonical)
            _, audit_median, _ = summarize(audit)
            ax.axvline(
                canonical_median,
                color=CANONICAL_COLOR,
                lw=1.5,
                ls="-",
                zorder=5,
            )
            ax.axvline(
                audit_median,
                color=AUDIT_COLOR,
                lw=1.5,
                ls="--",
                zorder=5,
            )
            ax.axvline(
                a0_effective[molecule],
                color=A0_COLOR,
                lw=1.5,
                ls=":",
                zorder=6,
            )

            ax.set_xlim(x_left, x_right)
            if row == 0:
                ax.set_title(
                    f"{hours} h\n"
                    rf"$\chi^2_\nu$ can./audit: "
                    f"{canonical_chi2:.2f} / {audit_chi2:.2f}",
                    fontsize=11.5,
                    pad=7,
                )
            else:
                ax.set_title(f"{hours} h", fontsize=12, pad=7)
            ax.grid(axis="y", linestyle=":", linewidth=0.6, alpha=0.30)
            ax.tick_params(labelsize=9.5, right=True, top=True)
            ax.minorticks_on()
            if col == 0:
                ax.set_ylabel(
                    f"{MOLECULE_LABELS[molecule]} posterior density",
                    fontsize=10.5,
                )
            else:
                ax.tick_params(axis="y", labelleft=False)
            if row == 1:
                ax.set_xlabel(r"$log_{10}$ volume mixing ratio", fontsize=10.5)
            else:
                ax.tick_params(axis="x", labelbottom=False)

    canonical_nparams = {fit[(hours, False)][1] for hours in HOURS}
    audit_nparams = {fit[(hours, True)][1] for hours in HOURS}
    if len(canonical_nparams) != 1 or len(audit_nparams) != 1:
        raise ValueError("Parameter count changes across integration times")

    legend_handles = [
        Line2D(
            [], [], color=CANONICAL_COLOR, lw=2.0, ls="-",
            label=(
                "A3 canónica (Piette20; "
                f"{next(iter(canonical_nparams))} parámetros)"
            ),
        ),
        Line2D(
            [], [], color=AUDIT_COLOR, lw=2.0, ls="--",
            label=(
                "A3 auditoría (Psurf=1 bar; sin x_tol; "
                f"{next(iter(audit_nparams))} parámetros)"
            ),
        ),
        Line2D(
            [], [], color=A0_COLOR, lw=1.8, ls=":",
            label="A0 efectiva (referencia VULCAN)",
        ),
    ]
    fig.legend(
        handles=legend_handles,
        loc="upper center",
        ncol=1,
        frameon=False,
        fontsize=9.2,
        handlelength=2.4,
        labelspacing=0.35,
        bbox_to_anchor=(0.53, 0.925),
    )
    fig.suptitle(
        "Posteriores moleculares de LIFE — Proxima, escenario A3",
        y=0.985,
        fontsize=16,
    )
    fig.text(
        0.5,
        0.025,
        "Líneas verticales: medianas A3 y abundancia A0 efectiva. "
        "Las corridas canónica y de auditoría difieren en varios supuestos; "
        "la comparación no aísla un único cambio.",
        ha="center",
        fontsize=8.7,
    )
    fig.subplots_adjust(
        left=0.12,
        right=0.98,
        bottom=0.10,
        top=0.76,
        hspace=0.24,
        wspace=0.12,
    )

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    png_path = PLOTS_DIR / "retrieval_A3_molecular_posteriors_audit_comparison_proxima.png"
    pdf_path = PLOTS_DIR / "retrieval_A3_molecular_posteriors_audit_comparison_proxima.pdf"
    fig.savefig(png_path, dpi=240, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)

    for molecule in MOLECULES:
        for hours in HOURS:
            canonical = samples[(hours, False, molecule)]
            audit = samples[(hours, True, molecule)]
            print(
                f"{hours} h {molecule}: "
                f"canonical n={canonical.size}, {interval_label(canonical)}; "
                f"audit n={audit.size}, {interval_label(audit)}; "
                f"A0eff={a0_effective[molecule]:.4f}; "
                f"chi2red={fit[(hours, False)][0]:.2f}/"
                f"{fit[(hours, True)][0]:.2f}"
            )
    print(f"PNG={png_path}")
    print(f"PDF={pdf_path}")
    return png_path, pdf_path


if __name__ == "__main__":
    plot_posteriors()
