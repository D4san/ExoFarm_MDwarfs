"""Compare full A3 marginal posterior shapes, 1/10/100/1000h, against A0.

Equal-weight samples, empirical histograms (no smoothing), central 95% intervals.
The 1000h posterior is preliminary and does not accept the pending campaign.
"""

import hashlib
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from fixed_abundance_reference import load_fixed_abundances
from run_proxima_molecule_ablation_campaign import DATASETS, RESULTS_REL

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Transmission_Spectroscopy/notebooks"))
from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    project = ROOT / "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1"
    reference = project / "retrievals/a0_fixed_reference_20261010/a0_reference.json"
    refs = load_fixed_abundances(reference, ["N2O", "NH3"], ROOT)
    paths = {}
    for hours in (1, 10, 100):
        stem = DATASETS["A3", hours]["full_results"].removesuffix("_results.txt")
        paths[hours] = ROOT / RESULTS_REL.parent / "samples" / (stem + "_samples.txt")
    full = project / "retrievals/a3_1000h_full_20261011/native_grid_retry"
    config = json.loads((full / "resolved_configuration.json").read_text())
    paths[1000] = full / "products/samples" / (config["model_name"] + "_samples.txt")
    plt.rcParams.update({"font.family": "serif", "font.serif": ["STIXGeneral"],
                         "mathtext.fontset": "stix", "font.size": 12})
    fig, axes = plt.subplots(4, 2, figsize=(12, 9.5), sharex="col")
    colours = [PALETTE[k] for k in
               ("sunlit_clay", "golden_orange", "rusty_spice", "dark_amaranth")]
    rows = []
    for row, (hours, path) in enumerate(paths.items()):
        names = [n.strip() for n in path.open().readline().split("|")]
        samples = np.loadtxt(path, skiprows=1, ndmin=2)
        if len(names) != 15 or samples.shape[1] != 15 or not np.isfinite(samples).all():
            raise ValueError(f"Invalid sample export: {path}")
        if hours == 1000:
            raw = np.loadtxt(full / "products/MultiNest_raw" /
                             (config["model_name"] + "-post_equal_weights.dat"), ndmin=2)
            np.testing.assert_allclose(samples, raw[:, :15], rtol=1e-6, atol=6e-6)
            samples = raw[:, :15]  # Prefer full precision over ASCII-rounded export.
        for col, gas in enumerate(("N2O", "NH3")):
            values = samples[:, names.index("log_" + gas)]
            if np.min(values) < -12.00001 or np.max(values) > -0.99999:
                raise ValueError("Abundance outside nominal prior")
            delta = values - refs[gas]
            quantiles = np.quantile(delta, [0.025, 0.5, 0.975])
            factors = 10**quantiles
            ax = axes[row, col]
            # Fixed histogram bins across exposure within each molecular panel.
            low, high = -12 - refs[gas], -1 - refs[gas]
            bins = np.linspace(low, high, 551)
            density, edges = np.histogram(delta, bins=bins, density=True)
            np.testing.assert_allclose(np.sum(density * np.diff(edges)), 1, atol=1e-12)
            ax.axvspan(low, 0, color=PALETTE["dust_grey"], alpha=.35)
            ax.stairs(density, edges, color=colours[row], fill=True, alpha=.65, linewidth=1)
            ax.axvline(0, color=PALETTE["ink_black"], ls="--", lw=1.3)
            height = max(density) * 1.08
            ax.plot(quantiles[[0, 2]], [height, height], color=colours[row], lw=2)
            ax.plot(quantiles[1], height, "o", color=colours[row], ms=5)
            label = f"{hours} h" + (" · preliminar" if hours == 1000 else "")
            ax.text(.02, .91, label, transform=ax.transAxes, va="top", fontsize=12)
            ax.text(.98, .91, f"Mediana: {factors[1]:.2f}× A0\n95 %: [{factors[0]:.3g}, {factors[2]:.3g}]",
                    transform=ax.transAxes, ha="right", va="top", fontsize=10)
            ax.set_ylim(0, height * 1.35)
            ax.set_xlim(low, high)
            ticks = np.arange(np.ceil(low), np.floor(high) + 1)
            ax.set_xticks(ticks)
            ax.set_xticklabels([r"$10^{%d}$" % t if t != 0 else "1 (A0)" for t in ticks])
            ax.set_ylabel("Densidad / dex", fontsize=10)
            ax.spines[["top", "right"]].set_visible(False)
            ax.grid(axis="x", alpha=.15)
            if row == 0:
                ax.set_title(r"$\mathrm{N_2O}$" if col == 0 else r"$\mathrm{NH_3}$", fontsize=18)
            if row == 3:
                ax.set_xlabel(r"Factor de enriquecimiento $X/X_{A0}$ (escala logarítmica)")
            rows.append({"hours": hours, "species": gas, "n_samples": len(delta),
                         "factor_q025_median_q975": factors.tolist(),
                         "p_above_a0_empirical": float(np.mean(delta > 0)),
                         "n_at_or_below": int(np.sum(delta <= 0)),
                         "samples_path": str(path.relative_to(ROOT)), "samples_sha256": sha(path),
                         "status": "PRELIMINARY_PENDING_AUDIT" if hours == 1000 else "official_full"})
    fig.suptitle("LIFE Proxima · A3: posteriores completas frente a A0", fontsize=18, y=.985)
    fig.text(.5, .015, "Línea discontinua = referencia A0; barras = intervalo central 95 % y mediana.\n"
             "Distinta realización de ruido por exposición; sin evidencia de comparación entre tiempos.",
             ha="center", fontsize=10)
    fig.tight_layout(rect=(0, .055, 1, .96))
    output = ROOT / "Thermal_Emission_Spectroscopy/final_products/figures"
    output.mkdir(parents=True, exist_ok=True)
    stem = output / "life_proxima_A3_full_posterior_enrichment_1_10_100_1000h_preliminary"
    fig.savefig(stem.with_suffix(".png"), dpi=180)
    fig.savefig(stem.with_suffix(".pdf"))
    stem.with_suffix(".json").write_text(json.dumps({"reference_sha256": sha(reference),
        "method": "equal-weight histogram in log10(X/X_A0); empirical central quantiles",
        "missing_combinations": [], "rows": rows}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"figure": str(stem.with_suffix(".png")), "rows": rows}, indent=2))


if __name__ == "__main__":
    main()
