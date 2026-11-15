"""Compare A3 100 h molecular posteriors across binning operators."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Transmission_Spectroscopy" / "notebooks"))

from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE  # noqa: E402


HISTORICAL = ROOT / (
    "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/"
    "retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/samples/"
    "proxima_A3_100h_O2_fixedBlack1bar_noxtol_proxima_A3_100h_"
    "O2_fixedBlack1bar_noxtol_samples.txt"
)
CORRECTED = ROOT / (
    "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/"
    "retrievals/a3_100h_binning_corrected_mpi14_resume_20261018/"
    "products/samples/"
    "proxima_A3_100h_O2_fixedBlack1bar_noxtol_BIN1_20261017_samples.txt"
)
OUTPUT = ROOT / (
    "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/"
    "plots/retrieval_A3_100h_historical_vs_corrected_binning_posterior_proxima.png"
)

COLUMNS = {"log_N2O": 12, "log_NH3": 13}
DATASET_SHA256 = "78662546181a5b74391a14b7b73ae80d879200a74db6a4bc5338e3ce7eee4705"
A0_EFFECTIVE = {"log_N2O": -6.884325289636784, "log_NH3": -9.950526295665036}
COLORS = {
    "historical": PALETTE["slate_green"],
    "corrected": PALETTE["scenario_pink"],
    "a0": PALETTE["golden_orange"],
}


def load_samples(path: Path) -> np.ndarray:
    if not path.is_file():
        raise FileNotFoundError(path)
    samples = np.loadtxt(path, skiprows=1)
    if samples.ndim != 2 or samples.shape[1] != 15:
        raise ValueError(f"Expected an N x 15 posterior table in {path}, got {samples.shape}")
    if not np.isfinite(samples).all():
        raise ValueError(f"Non-finite posterior samples found in {path}")
    return samples


def main() -> None:
    posterior = {
        "Historical energy-bin operator": load_samples(HISTORICAL),
        "Corrected photon-overlap operator": load_samples(CORRECTED),
    }
    colors = [COLORS["historical"], COLORS["corrected"]]
    labels = list(posterior)

    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["STIX Two Text", "STIXGeneral", "Times New Roman"],
            "mathtext.fontset": "stix",
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 5.0))
    fig.subplots_adjust(top=0.78, bottom=0.22, wspace=0.18)
    for ax, (parameter, index) in zip(axes, COLUMNS.items()):
        for label, color in zip(labels, colors):
            values = posterior[label][:, index]
            q16, median, q84 = np.quantile(values, [0.16, 0.50, 0.84])
            ax.hist(
                values,
                bins=48,
                density=True,
                histtype="step",
                linewidth=1.9,
                color=color,
                label=f"{label} (n={len(values):,})",
            )
            ax.axvline(median, color=color, lw=1.35, ls="-")
            ax.axvspan(q16, q84, color=color, alpha=0.08, lw=0)

        ax.axvline(
            A0_EFFECTIVE[parameter],
            color=COLORS["a0"],
            lw=1.6,
            ls="--",
            label=r"A0 efectiva",
        )
        ax.set_xlabel(rf"$\log_{{10}}({parameter[4:]})$ (abundancia constante)")
        ax.set_ylabel("Densidad posterior")
        ax.grid(axis="y", alpha=0.2)
        ax.set_title(parameter.replace("_", " "))

    handles = [
        Line2D([0], [0], color=COLORS["historical"], lw=2, label="Bineado histórico"),
        Line2D([0], [0], color=COLORS["corrected"], lw=2, label="Bineado corregido"),
        Line2D([0], [0], color=COLORS["a0"], lw=1.6, ls="--", label="A0 efectiva"),
    ]
    fig.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.91),
        ncol=3,
        frameon=False,
    )
    fig.suptitle(
        "Proxima b · A3 · LIFE 100 h: sensibilidad del posterior al bineado",
        y=0.98,
        fontsize=13,
    )
    fig.text(
        0.5,
        0.035,
        "Misma realización observada (31 canales; SHA-256 "
        f"{DATASET_SHA256[:12]}…). Rejilla: 3.8–19 μm histórica y 3–20 μm corregida. "
        "Comparación metodológica; no es un factor de Bayes entre hipótesis.",
        ha="center",
        va="top",
        fontsize=8.5,
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(f"Figure: {OUTPUT}")
    for label, samples in posterior.items():
        print(f"{label}: n={len(samples)}, finite={bool(np.isfinite(samples).all())}")
        for parameter, index in COLUMNS.items():
            q16, median, q84 = np.quantile(samples[:, index], [0.16, 0.50, 0.84])
            print(f"  {parameter}: q16={q16:.6f}, median={median:.6f}, q84={q84:.6f}")


if __name__ == "__main__":
    main()
