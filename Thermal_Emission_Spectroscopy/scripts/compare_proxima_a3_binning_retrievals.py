"""Preserve/audit primary products and compare full A3-1000 h operators.

This operator sensitivity is not a molecular Bayes factor. Scientific
acceptance and visual inspection remain a separate human-reviewed step.
"""

import json
from pathlib import Path
import re

import numpy as np

from audit_proxima_a0_fixed_reference import audit_derived_moments
from validate_proxima_molecular_ablation_loo import parse_evidence_from_stats, validate_table

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1"
OLD = PROJECT / "retrievals/a3_1000h_full_20261011/native_grid_retry"
NEW = PROJECT / "retrievals/a3_1000h_binning_corrected_20261014"


def inspect(campaign):
    config = json.loads((campaign / "resolved_configuration.json").read_text())
    stem = config["model_name"]
    products = campaign / "products"
    raw = products / "MultiNest_raw"
    samples = products / "samples"
    posterior = np.loadtxt(raw / (stem + "-post_equal_weights.dat"), ndmin=2)
    if posterior.shape[1] != 16 or not np.isfinite(posterior).all():
        raise ValueError("Invalid primary posterior")
    for index, name in enumerate(config["parameters"]):
        left, right = config["prior_ranges"][name]
        if np.any(posterior[:, index] < left - 1e-10) or np.any(posterior[:, index] > right + 1e-10):
            raise ValueError(f"Posterior outside prior: {name}")
    if np.any(posterior[:, config["parameters"].index("log_P_surf")] != 0):
        raise ValueError("Fixed surface changed")
    shapes = {}
    for suffix in ("-.txt", "-ev.dat", "-live.points", "-phys_live.points"):
        shapes[suffix] = validate_table(raw / (stem + suffix))
    for suffix in ("-live.points", "-phys_live.points"):
        if shapes[suffix][0] != 800:
            raise ValueError("Final live-point count differs")
    exported = np.loadtxt(samples / (stem + "_samples.txt"), skiprows=1, ndmin=2)
    np.testing.assert_allclose(exported, posterior[:, :15], rtol=1e-5, atol=1e-5)
    for suffix in ("_spectrum_retrieved.txt", "_PT_retrieved.txt", "_log_X_retrieved.txt"):
        shapes[suffix] = validate_table(samples / (stem + suffix),
                                        allow_text_anywhere=True, expected_columns=6)
    moments = audit_derived_moments(raw / (stem + "-summary.txt"),
                                    raw / (stem + "-stats.dat"),
                                    config["parameters"], {"P_surf": 0.0})
    lnz, error = parse_evidence_from_stats(raw / (stem + "-stats.dat"))
    if abs(lnz - moments["nested_summary_lnz"]) > 1e-10:
        raise ValueError("Evidence stats/summary disagreement")
    result = (products / "results" / (stem + "_results.txt")).read_text()
    chi2 = float(re.search(r"->\s*chi\^2\s*=\s*([-+\d.eE]+)", result)[1])
    quantiles = {name: np.quantile(posterior[:, index], [.025, .16, .5, .84, .975]).tolist()
                 for index, name in enumerate(config["parameters"])}
    return {"lnZ": lnz, "lnZ_numeric_error": error, "chi2_printed": chi2,
            "effective_dof": 17, "posterior_rows": len(posterior),
            "parameter_quantiles_025_16_50_84_975": quantiles,
            "primary_product_shapes": shapes, "derived_moment_salvedad": moments,
            "acceptance": "PENDING_INDEPENDENT_REVIEW"}, posterior, samples, stem


def main():
    state = json.loads((NEW / "campaign_state.json").read_text())
    if state.get("exit_code") != 0:
        raise RuntimeError("New retrieval has not finished with exit zero")
    old, old_posterior, old_samples, old_stem = inspect(OLD)
    new, new_posterior, new_samples, new_stem = inspect(NEW)
    payload = {"old_operator": old, "corrected_operator": new,
               "delta_lnZ_operator_only": new["lnZ"] - old["lnZ"],
               "interpretation": "Numerical operator sensitivity; not molecular ln B or detection sigma",
               "unchanged": "observed dataset, priors, physical model, thermal opacity grid",
               "scientific_acceptance": "PENDING"}
    output = NEW / "comparison"
    output.mkdir(exist_ok=False)
    (output / "comparison.json").write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "serif", "mathtext.fontset": "stix"})
    fig, axes = plt.subplots(1, 3, figsize=(12, 4), constrained_layout=True)
    config = json.loads((NEW / "resolved_configuration.json").read_text())
    for column, name in enumerate(("log_N2O", "log_NH3")):
        index = config["parameters"].index(name)
        for values, label, color in ((old_posterior, "Anterior", "#746F75"),
                                      (new_posterior, "Binning coherente", "#E34F95")):
            axes[column].hist(values[:, index], bins=50, density=True, histtype="step",
                               color=color, label=label)
        axes[column].set(xlabel=name, ylabel="Densidad posterior")
        axes[column].legend()
    for samples, stem, label, color in ((old_samples, old_stem, "Anterior", "#746F75"),
                                        (new_samples, new_stem, "Binning coherente", "#E34F95")):
        table = np.loadtxt(samples / (stem + "_PT_retrieved.txt"), skiprows=1)
        axes[2].plot(table[:, 3], table[:, 0], color=color, label=label)
        axes[2].fill_betweenx(table[:, 0], table[:, 2], table[:, 4], color=color, alpha=.15)
    axes[2].set(yscale="log", xlabel="T [K]", ylabel="P [bar]")
    axes[2].invert_yaxis()
    axes[2].legend()
    fig.savefig(output / "posterior_PT_comparison.png", dpi=220)
    fig.savefig(output / "posterior_PT_comparison.pdf")
    plt.close(fig)
    text = ("# Comparación A3–1000 h: operador de canales\n\n"
            f"χ² anterior: {old['chi2_printed']}; corregido: {new['chi2_printed']} (17 grados efectivos).\n\n"
            f"ln Z anterior: {old['lnZ']} ± {old['lnZ_numeric_error']}; "
            f"corregido: {new['lnZ']} ± {new['lnZ_numeric_error']}.\n\n"
            "La diferencia mide sensibilidad al operador numérico. No se informa como evidencia "
            "de una molécula ni se convierte a sigma. Los modelos A0 anteriores usan otro operador "
            "y requieren una pareja coherente antes de compararlos con este nuevo completo.\n\n"
            "Productos primarios finitos y dentro de priors; posibles NaN de momentos derivados "
            "de la superficie fija quedan preservados y registrados en comparison.json. "
            "Aceptación científica y revisión visual pendientes.\n\n"
            "![Posteriores y PT](posterior_PT_comparison.png)\n")
    (output / "comparison.md").write_text(text)
    print(json.dumps({"comparison": str(output), "acceptance": "PENDING"}))


if __name__ == "__main__":
    main()
