from pathlib import Path
import re

import matplotlib.pyplot as plt
import numpy as np

from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE


BASE_DIR = Path(__file__).resolve().parent
RETRIEVAL_DIR = BASE_DIR / "POSEIDON_output" / "TRAPPIST-1e" / "retrievals"
RESULTS_DIR = RETRIEVAL_DIR / "results"
SAMPLES_DIR = RETRIEVAL_DIR / "samples"
PLOTS_DIR = BASE_DIR / "POSEIDON_output" / "TRAPPIST-1e" / "plots"

PARAMETERS = ["log_H2O", "log_CO2", "log_CH4", "log_O3", "log_N2O", "log_NH3"]
INSTRUMENT_ORDER = ["MIRI", "NIRSpec", "NIRSpec_MIRI"]
INSTRUMENT_LABELS = {
    "MIRI": "MIRI",
    "NIRSpec": "NIRSpec",
    "NIRSpec_MIRI": "NIRSpec+MIRI",
}
INSTRUMENT_COLOURS = {
    "MIRI": PALETTE["golden_orange"],
    "NIRSpec": PALETTE["deep_space_blue"],
    "NIRSpec_MIRI": PALETTE["dark_amaranth"],
}


def parse_case_name(path):
    pattern = (
        r"TRAPPIST1e_(?P<scenario>A\d)_retrieval_isotherm_isochem_"
        r"(?P<transits>\d+)transits_(?P<instrument>NIRSpec_MIRI|NIRSpec|MIRI)_results\.txt"
    )
    match = re.fullmatch(pattern, path.name)
    if not match:
        return None
    return {
        "scenario": match.group("scenario"),
        "transits": int(match.group("transits")),
        "instrument": match.group("instrument"),
    }


def parse_results(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    lnz = re.search(r"ln Z =\s*([-+0-9.]+) \+/- ([0-9.]+)", text)
    chi = re.search(r"chi\^2_red =\s*([-+0-9.]+)", text)
    values = {}
    for parameter in ["T", *PARAMETERS]:
        match = re.search(
            rf"^{parameter}\s*=\s*([-+0-9.]+) \(\+([-+0-9.]+)\) \(-([-+0-9.]+)\)",
            text,
            re.MULTILINE,
        )
        if match:
            values[parameter] = tuple(float(match.group(i)) for i in range(1, 4))
    return {
        "lnZ": float(lnz.group(1)) if lnz else np.nan,
        "lnZ_err": float(lnz.group(2)) if lnz else np.nan,
        "chi2_red": float(chi.group(1)) if chi else np.nan,
        "constraints": values,
    }


def sample_path(case):
    return SAMPLES_DIR / (
        f"TRAPPIST1e_{case['scenario']}_retrieval_isotherm_isochem_"
        f"{case['transits']}transits_{case['instrument']}_samples.txt"
    )


def posterior_widths(path):
    if not path.exists():
        return {}
    data = np.genfromtxt(path, names=True, comments=None, delimiter=None, skip_header=1)
    widths = {}
    for parameter in PARAMETERS:
        if parameter not in data.dtype.names:
            continue
        q16, q84 = np.percentile(data[parameter], [16, 84])
        widths[parameter] = 0.5 * (q84 - q16)
    return widths


def load_campaign(scenario):
    rows = []
    for path in sorted(RESULTS_DIR.glob(f"TRAPPIST1e_{scenario}_retrieval_isotherm_isochem_*_results.txt")):
        case = parse_case_name(path)
        if case is None:
            continue
        metrics = parse_results(path)
        metrics["posterior_widths"] = posterior_widths(sample_path(case))
        rows.append({**case, **metrics})
    return rows


def plot_scenario_summary(scenario):
    rows = load_campaign(scenario)
    if not rows:
        raise FileNotFoundError(f"No retrieval products found for {scenario}")

    transits = sorted({row["transits"] for row in rows})
    x = np.arange(len(transits))
    offsets = {"MIRI": -0.23, "NIRSpec": 0.0, "NIRSpec_MIRI": 0.23}

    fig, axes = plt.subplots(2, 1, figsize=(8.8, 7.4), sharex=True)
    for instrument in INSTRUMENT_ORDER:
        subset = [row for row in rows if row["instrument"] == instrument]
        if not subset:
            continue
        y_chi = []
        y_lnz = []
        xs = []
        for transit in transits:
            match = next((row for row in subset if row["transits"] == transit), None)
            if match is None:
                continue
            xs.append(x[transits.index(transit)] + offsets[instrument])
            y_chi.append(match["chi2_red"])
            y_lnz.append(match["lnZ"])
        axes[0].plot(
            xs,
            y_chi,
            marker="o",
            lw=1.8,
            color=INSTRUMENT_COLOURS[instrument],
            label=INSTRUMENT_LABELS[instrument],
        )
        axes[1].plot(
            xs,
            y_lnz,
            marker="o",
            lw=1.8,
            color=INSTRUMENT_COLOURS[instrument],
        )

    axes[0].axhline(1.0, color=PALETTE["dim_grey"], lw=1.0, ls="--", alpha=0.8)
    axes[0].set_ylabel(r"Best $\chi^2_\mathrm{red}$")
    axes[1].set_ylabel(r"$\ln Z$")
    axes[1].set_xlabel("Transits per instrument")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels([str(value) for value in transits])
    axes[0].legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.18))
    for ax in axes:
        ax.grid(alpha=0.18)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle(f"TRAPPIST-1e {scenario}: retrieval campaign metrics", y=0.98)
    fig.tight_layout()
    return fig


def plot_width_heatmap(scenario):
    rows = load_campaign(scenario)
    labels = []
    matrix = []
    for transit in sorted({row["transits"] for row in rows}):
        for instrument in INSTRUMENT_ORDER:
            row = next(
                (
                    item
                    for item in rows
                    if item["transits"] == transit and item["instrument"] == instrument
                ),
                None,
            )
            if row is None:
                continue
            labels.append(f"{transit} {INSTRUMENT_LABELS[instrument]}")
            matrix.append([row["posterior_widths"].get(parameter, np.nan) for parameter in PARAMETERS])

    values = np.asarray(matrix, dtype=float)
    fig, ax = plt.subplots(figsize=(10.8, max(4.8, 0.43 * len(labels))))
    image = ax.imshow(values, aspect="auto", cmap="magma_r")
    ax.set_yticks(np.arange(len(labels)))
    ax.set_yticklabels(labels)
    ax.set_xticks(np.arange(len(PARAMETERS)))
    ax.set_xticklabels([p.replace("log_", "") for p in PARAMETERS], rotation=35, ha="right")
    ax.set_title(f"TRAPPIST-1e {scenario}: posterior width (sigma68, dex)")
    cbar = fig.colorbar(image, ax=ax, pad=0.02)
    cbar.set_label("Posterior half-width")
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            if np.isfinite(values[i, j]):
                ax.text(j, i, f"{values[i, j]:.2f}", ha="center", va="center", fontsize=8)
    fig.tight_layout()
    return fig


def main():
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    for scenario in ["A0", "A1", "A2", "A3"]:
        if not load_campaign(scenario):
            continue
        for suffix, plotter in [
            ("metrics", plot_scenario_summary),
            ("posterior_widths", plot_width_heatmap),
        ]:
            fig = plotter(scenario)
            for extension in ["png", "pdf"]:
                path = PLOTS_DIR / f"trappist_retrieval_{scenario}_{suffix}.{extension}"
                fig.savefig(path, dpi=240, bbox_inches="tight")
                print(path)
            plt.close(fig)


if __name__ == "__main__":
    main()
