from pathlib import Path
import re

import matplotlib.pyplot as plt
import numpy as np

from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE


BASE_DIR = Path(__file__).resolve().parent
SAMPLES_DIR = (
    BASE_DIR
    / "POSEIDON_output"
    / "TRAPPIST-1e"
    / "retrievals"
    / "samples"
)
PLOTS_DIR = BASE_DIR / "POSEIDON_output" / "TRAPPIST-1e" / "plots"

PARAMETERS = ("log_N2O", "log_NH3")
PARAMETER_LABELS = {
    "log_N2O": r"N$_2$O",
    "log_NH3": r"NH$_3$",
}
INSTRUMENT_ORDER = {"MIRI": 0, "NIRSpec": 1, "NIRSpec_MIRI": 2}
INSTRUMENT_LABELS = {
    "MIRI": "MIRI",
    "NIRSpec": "NIRSpec",
    "NIRSpec_MIRI": "NIRSpec+MIRI",
}


def parse_sample_path(path):
    match = re.fullmatch(
        r"TRAPPIST1e_(A[03])_retrieval_isotherm_isochem_"
        r"(\d+)transits_(MIRI|NIRSpec|NIRSpec_MIRI)_samples\.txt",
        path.name,
    )
    if match is None:
        return None
    return {
        "scenario": match.group(1),
        "transits": int(match.group(2)),
        "instrument": match.group(3),
        "path": path,
    }


def load_samples(path):
    with path.open("r", encoding="utf-8") as handle:
        names = [name.strip() for name in handle.readline().split("|")]
    return np.genfromtxt(path, names=names, skip_header=1)


def summarize_campaign(path):
    samples = load_samples(path)
    summary = {}
    for parameter in PARAMETERS:
        if parameter not in samples.dtype.names:
            continue
        q16, median, q84 = np.nanpercentile(samples[parameter], [16, 50, 84])
        summary[parameter] = {
            "median": median,
            "sigma": 0.5 * (q84 - q16),
        }
    return summary


def load_campaigns():
    campaigns = {"A0": [], "A3": []}
    for path in SAMPLES_DIR.glob("*_samples.txt"):
        case = parse_sample_path(path)
        if case is None:
            continue
        case["summary"] = summarize_campaign(path)
        campaigns[case["scenario"]].append(case)
    for scenario in campaigns:
        campaigns[scenario].sort(
            key=lambda case: (
                case["transits"],
                INSTRUMENT_ORDER[case["instrument"]],
            )
        )
    return campaigns


def campaign_label(case):
    return f"{case['transits']} {INSTRUMENT_LABELS[case['instrument']]}"


def sigma_distance(a0_case, a3_case, parameter):
    a0 = a0_case["summary"].get(parameter)
    a3 = a3_case["summary"].get(parameter)
    if a0 is None or a3 is None:
        return np.nan
    denominator = np.hypot(a0["sigma"], a3["sigma"])
    if denominator == 0:
        return np.nan
    return abs(a3["median"] - a0["median"]) / denominator


def build_matrices(campaigns):
    matrices = {}
    for parameter in PARAMETERS:
        matrices[parameter] = np.asarray(
            [
                [
                    sigma_distance(a0_case, a3_case, parameter)
                    for a3_case in campaigns["A3"]
                ]
                for a0_case in campaigns["A0"]
            ],
            dtype=float,
        )
    return matrices


def plot_sigma_matrices(campaigns, matrices):
    finite_values = np.concatenate(
        [matrix[np.isfinite(matrix)] for matrix in matrices.values()]
    )
    vmax = max(1.0, float(np.nanpercentile(finite_values, 95)))

    fig, axes = plt.subplots(1, 2, figsize=(13.5, 7.2), constrained_layout=True)
    image = None
    for ax, parameter in zip(axes, PARAMETERS):
        matrix = matrices[parameter]
        image = ax.imshow(
            matrix,
            origin="lower",
            aspect="auto",
            cmap="magma",
            vmin=0.0,
            vmax=vmax,
        )
        ax.set_title(PARAMETER_LABELS[parameter])
        ax.set_xticks(np.arange(len(campaigns["A3"])))
        ax.set_xticklabels(
            [campaign_label(case) for case in campaigns["A3"]],
            rotation=55,
            ha="right",
            fontsize=7,
        )
        ax.set_yticks(np.arange(len(campaigns["A0"])))
        ax.set_yticklabels(
            [campaign_label(case) for case in campaigns["A0"]],
            fontsize=7,
        )
        for row in range(matrix.shape[0]):
            for col in range(matrix.shape[1]):
                value = matrix[row, col]
                if not np.isfinite(value):
                    continue
                text_colour = "white" if value > 0.52 * vmax else PALETTE["ink_black"]
                ax.text(
                    col,
                    row,
                    f"{value:.1f}",
                    ha="center",
                    va="center",
                    fontsize=6.5,
                    color=text_colour,
                )

    axes[0].set_ylabel("A0 observing campaign")
    for ax in axes:
        ax.set_xlabel("A3 observing campaign")
    cbar = fig.colorbar(image, ax=axes, shrink=0.78, pad=0.02)
    cbar.set_label(r"Posterior separation, $\Delta_\sigma$")
    fig.suptitle(
        "TRAPPIST-1e A0 vs A3 posterior separation by observing campaign",
        fontsize=16,
    )
    return fig


def main():
    campaigns = load_campaigns()
    if not campaigns["A0"] or not campaigns["A3"]:
        raise FileNotFoundError("A0 and A3 posterior samples are required.")
    matrices = build_matrices(campaigns)
    fig = plot_sigma_matrices(campaigns, matrices)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    for extension in ("png", "pdf"):
        output = PLOTS_DIR / f"trappist_A0_A3_posterior_sigma_distance_matrix.{extension}"
        fig.savefig(output, dpi=240, bbox_inches="tight")
        print(output)
    plt.close(fig)


if __name__ == "__main__":
    main()
