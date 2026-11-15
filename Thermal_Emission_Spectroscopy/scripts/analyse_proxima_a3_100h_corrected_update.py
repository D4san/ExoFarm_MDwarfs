"""Update A3--100 h inference from audited corrected-bin retrieval products.

This is post-processing only: it never launches POSEIDON or changes a native
retrieval, its audit, the observed data, or the historical scientific tables.
Current-series tables explicitly identify the operator of every row.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import shutil
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

from report_proxima_loo_lin_sigma import calibrated_sigma
from retrieval_reference import log10_column_averaged_mixing_ratio


ROOT = Path(__file__).resolve().parents[2]
STAGE = ROOT / "Thermal_Emission_Spectroscopy"
BASE = STAGE / "outputs/life_proxima_b_earthlike_v1"
CAMPAIGN = BASE / "retrievals/a3_100h_binning_corrected_loo_20261019"
FULL = BASE / "retrievals/a3_100h_binning_corrected_mpi14_resume_20261018"
OUTPUT = BASE / "tables/a3_100h_corrected_update_20261020"
FIGURES = BASE / "plots/a3_100h_corrected_update_20261020"
FINAL = STAGE / "final_products/tables"
REPORT = ROOT / "docs/life_proxima_a3_100h_corrected_results_update_2026-10-20.md"
SPECIES = ("N2O", "NH3")
PROBABILITIES = (0.025, 0.16, 0.5, 0.84, 0.975)
Q_LABELS = ("q025", "q16", "median", "q84", "q975")
INPUTS = {}

sys.path.insert(0, str(ROOT / "Transmission_Spectroscopy/notebooks"))
from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE  # noqa: E402


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return path.relative_to(ROOT).as_posix()


def record(path, expected=None):
    digest = sha256(path)
    require(expected is None or digest == expected, f"Hash mismatch: {path}")
    INPUTS[relative(path)] = digest
    return path


def read_json(path, expected=None):
    return json.loads(record(path, expected).read_text(encoding="utf-8"))


def read_csv(path):
    with record(path).open(encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def samples(path, expected=None):
    record(path, expected)
    with path.open(encoding="utf-8") as stream:
        names = [field.strip() for field in stream.readline().split("|")]
    values = np.atleast_2d(np.loadtxt(path, skiprows=1))
    require(values.shape[1] == len(names), f"Posterior header mismatch: {path}")
    require(np.isfinite(values).all(), f"Non-finite posterior: {path}")
    return names, values


def fit_statistics(path, declared, free):
    text = record(path).read_text(encoding="utf-8")
    values = {}
    for key, expression in (
        ("chi2", r"-> chi\^2 = ([0-9.eE+-]+)"),
        ("chi2_red_native", r"-> chi\^2_red = ([0-9.eE+-]+)"),
        ("dof_native", r"-> degrees of freedom = ([0-9]+)"),
    ):
        match = re.search(expression, text)
        require(match is not None, f"Missing {key} in {path}")
        values[key] = float(match.group(1))
    values.update(declared_parameters=declared, free_parameters=free,
                  dof_effective=31 - free,
                  chi2_red_effective=values["chi2"] / (31 - free))
    return values


def odds_update(q, q0):
    if q in (0.0, 1.0):
        return None, None, "tail_not_resolved"
    value = q * (1 - q0) / ((1 - q) * q0)
    return value, math.log(value), "both_regions_sampled"


def summarize_region(model, species, reference, values, threshold, sample_path):
    delta = values - threshold
    quantiles = np.quantile(delta, PROBABILITIES)
    probability = float(np.mean(delta >= 0.0))
    prior_mass = (-1.0 - threshold) / 11.0
    factor, log_factor, tail = odds_update(probability, prior_mass)
    row = {
        "scenario": "A3", "hours": 100, "model": model,
        "species": species, "reference": reference,
        "log10_reference_effective": threshold, "n_samples": len(values),
        "n_ge_reference": int(np.count_nonzero(delta >= 0.0)),
        "p_ge_reference": probability, "nominal_prior_mass": prior_mass,
        "K_nominal": factor, "ln_K_nominal": log_factor, "tail_status": tail,
    }
    for label, value in zip(Q_LABELS, quantiles):
        row[f"delta_dex_{label}"] = float(value)
        row[f"ratio_{label}"] = float(10**value)
    width68 = float(quantiles[3] - quantiles[1])
    row.update(width95_dex=float(quantiles[4] - quantiles[0]),
               z_descriptive=float(quantiles[2] / (width68 / 2)),
               samples_rel=relative(sample_path))
    return row


def plot_comparison(old, new, references, old_pt, new_pt):
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["STIX Two Text", "STIXGeneral", "Times New Roman"],
        "mathtext.fontset": "stix", "axes.spines.top": False,
        "axes.spines.right": False,
    })
    colors = {"historical": PALETTE["slate_green"],
              "corrected": PALETTE["deep_space_blue"]}
    reference_colors = {"A0": PALETTE["scenario_green"],
                        "A1": PALETTE["scenario_cyan"],
                        "A3": PALETTE["scenario_pink"]}
    fig, axes = plt.subplots(1, 3, figsize=(13.4, 4.7))
    fig.subplots_adjust(top=.75, bottom=.23, left=.065, right=.98, wspace=.31)
    for axis, species in zip(axes[:2], SPECIES):
        limits = (-7.12, -5.8) if species == "N2O" else (-12, -7.45)
        bins = np.linspace(*limits, 65)
        for label, bundle in (("historical", old), ("corrected", new)):
            names, matrix = bundle
            values = matrix[:, names.index("log_" + species)]
            q025, q16, median, q84, q975 = np.quantile(values, PROBABILITIES)
            axis.hist(values, bins=bins, density=True, histtype="step",
                      lw=1.8, color=colors[label])
            axis.axvline(median, color=colors[label], lw=1)
            axis.axvspan(q025, q975, color=colors[label], alpha=.045)
            axis.axvspan(q16, q84, color=colors[label], alpha=.09)
        for scenario in ("A0", "A1", "A3"):
            axis.axvline(references[scenario][species], ls="--", lw=1.25,
                         color=reference_colors[scenario])
        axis.set(xlim=limits, xlabel=r"$\log_{10}X$", ylabel="Densidad posterior",
                 title=r"$\mathrm{" + species.replace("2", "_2").replace("3", "_3") + "}$")
        axis.grid(alpha=.16, axis="y")
    for label, path in (("historical", old_pt), ("corrected", new_pt)):
        pt = np.loadtxt(record(path), skiprows=1)
        require(pt.shape[1] == 6 and np.isfinite(pt).all(), "Invalid P-T table")
        axes[2].plot(pt[:, 3], pt[:, 0], color=colors[label], lw=1.8)
        axes[2].fill_betweenx(pt[:, 0], pt[:, 1], pt[:, 5], color=colors[label], alpha=.06)
        axes[2].fill_betweenx(pt[:, 0], pt[:, 2], pt[:, 4], color=colors[label], alpha=.14)
    axes[2].set(yscale="log", ylim=(1, 1e-6), xlabel="Temperatura (K)",
                ylabel="Presión (bar)", title="P–T posterior")
    axes[2].grid(alpha=.16)
    handles = [Line2D([0], [0], color=colors[label], lw=2, label=name)
               for label, name in (("historical", "Histórico"), ("corrected", "Corregido"))]
    handles += [Line2D([0], [0], color=reference_colors[s], ls="--", lw=1.5,
                       label=f"Referencia efectiva {s}") for s in references]
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(.51, .89),
               ncol=5, frameon=False, fontsize=9)
    fig.suptitle("LIFE Proxima · A3 · 100 h: actualización del retrieval", y=.98, fontsize=15)
    fig.text(.5, .09, "Misma realización observada. Cambian el operador y la rejilla nativa "
             "(3.8–19 → 3–20 μm). Bandas: 68 % y 95 %.", ha="center", fontsize=9)
    fig.text(.5, .035, "Las referencias efectivas comprimen perfiles verticales; "
             "no son parámetros isoquímicos verdaderos impuestos al retrieval.", ha="center", fontsize=8.5)
    for suffix in ("png", "pdf"):
        fig.savefig(FIGURES / f"posterior_PT_comparison.{suffix}", dpi=200)
    plt.close(fig)


def report(summary, region_rows, evidence_rows):
    find = lambda model, species, ref: next(
        r for r in region_rows if (r["model"], r["species"], r["reference"]) == (model, species, ref)
    )
    rows = []
    for species in SPECIES:
        old, new = find("historical_full", species, "A1"), find("corrected_full", species, "A1")
        rows.append(f"| {species} | {old['ratio_median']:.3f} [{old['ratio_q025']:.3f}, {old['ratio_q975']:.3f}] | "
                    f"{new['ratio_median']:.3f} [{new['ratio_q025']:.3f}, {new['ratio_q975']:.3f}] | "
                    f"{old['width95_dex']:.3f} → {new['width95_dex']:.3f} |")
    ev_lines = []
    for species in SPECIES:
        pair = [next(r for r in evidence_rows if r["species"] == species and r["version"] == version)
                for version in ("historical", "corrected")]
        ev_lines.append(f"| {species} | {pair[0]['ln_B']:.6f} ± {pair[0]['ln_B_numeric_error']:.6f} | "
                        f"{pair[1]['ln_B']:.6f} ± {pair[1]['ln_B_numeric_error']:.6f} | "
                        f"{pair[1]['sigma_calibrated_auxiliary']:.3f} |")
    joint_a1 = next(r for r in summary["joint_regions"]
                    if r["model"] == "corrected_full" and r["reference"] == "A1")
    gas_lines = []
    for species in SPECIES:
        for ref in ("A0", "A1"):
            r = find("corrected_full", species, ref)
            k = f"{r['K_nominal']:.4f}" if r["K_nominal"] is not None else "—"
            log_k = f"{r['ln_K_nominal']:.4f}" if r["ln_K_nominal"] is not None else "—"
            probability = "≈100 %" if r["p_ge_reference"] == 1 else f"{100*r['p_ge_reference']:.4f} %"
            gas_lines.append(f"| {species} | {ref} | {probability} | {k} | {log_k} |")
    fit = summary["fit_statistics"]
    text = f"""# Actualización A3–100 h: binning corregido, evidencia y enriquecimiento

Fecha: 2026-10-20, America/Bogota. Análisis ejecutado; sin nuevos retrievals.
El «A100» indicado por el usuario se identifica como **A3–100 h**, campaña
completa del 17-oct continuada con MPI14 el 18-oct y dos omisiones del 19-oct,
cerradas y auditadas el 20-oct.

## Fuentes y aceptación

- [Auditoría primaria](life_proxima_a3_100h_corrected_binning_molecular_ablation_2026-10-19.md): baseline y dos ablaciones PASS.
- [Script de esta actualización](../Thermal_Emission_Spectroscopy/scripts/analyse_proxima_a3_100h_corrected_update.py).
- [Resumen y hashes](../{relative(OUTPUT / 'summary.json')}).
- [Comparación de posteriores y P–T](../{relative(FIGURES / 'posterior_PT_comparison.png')}).

Se verificaron los hashes de productos contra la auditoría, las muestras
exportadas contra MultiNest de peso igual, finitud/dimensiones, límites de
prior, dataset común y evidencias exactas frente a la tabla auditada.
El nuevo resultado completo tiene {summary['sample_counts']['corrected_full']} muestras, 15
coordenadas declaradas y 14 libres; cada omisión tiene 13 libres.

## 1. Qué cambió y qué puede compararse

La realización observada es idéntica (31 canales; seed 129315834; SHA-256
`78662546181a5b74391a14b7b73ae80d879200a74db6a4bc5338e3ce7eee4705`).
La repetición corrigió la integración fotónica y cambió la rejilla nativa
de 3.8–19 a 3–20 μm. Los bordes de los canales caben en ambos dominios;
la ampliación sigue siendo un cambio de discretización. Las diferencias
histórico/corregido no aíslan exclusivamente el operador.

La evidencia completa pasa de {summary['full_evidence']['historical']['lnz']:.6f} a
{summary['full_evidence']['corrected']['lnz']:.6f}; Δln Z =
{summary['operator_sensitivity_delta_lnz']:.6f} es sensibilidad metodológica,
no evidencia molecular. Las comparaciones moleculares nuevas sí emparejan
operador, rejilla, priors y dato dentro de cada pareja.

## 2. Evidencia de presencia molecular

| Especie | ln B histórico | ln B corregido | Sigma calibrada corregida |
|---|---:|---:|---:|
{chr(10).join(ev_lines)}

N2O mantiene una preferencia fuerte por su inclusión. El valor central de NH3
pasa de apoyo débil a **moderado** (ln B=2.749, frente al umbral orientativo
2.5), cerca de esa frontera respecto del error numérico de 0.345.
La calibración es auxiliar: 2.853 sigma no equivale a una detección
frecuentista de 3 sigma ni a una probabilidad de origen agrícola.

## 3. Abundancias respecto de A1

| Molécula | Histórico: mediana [95 %] X/A1 | Corregido: mediana [95 %] X/A1 | Anchura 95 % (dex) |
|---|---:|---:|---:|
{chr(10).join(rows)}

El intervalo central del 95 % de NH3 queda ahora completamente por encima
de A1: el cambio relevante afecta especialmente a su cola inferior.
La concentración central sigue favoreciendo abundancias elevadas; esto
mejora la precisión del enriquecimiento condicionado al modelo.
Las medianas cambian mucho menos que las colas: +0.031 dex para N2O y
+0.087 dex para NH3. La anchura del intervalo NH3 pasa de 2.946 a 0.994 dex.
El control respecto de la referencia efectiva A3 también se conserva en
`posterior_regions.csv`; esta referencia comprime un perfil vertical y no
es un parámetro isoquímico verdadero que el retrieval deba recuperar sin sesgo.

## 4. Probabilidades y actualización de odds

| Molécula | Umbral | P(X ≥ referencia) | K nominal | ln K nominal |
|---|---|---:|---:|---:|
{chr(10).join(gas_lines)}

La probabilidad conjunta ≥ A1 es {100*joint_a1['p_both_ge_reference']:.4f} %,
con K nominal {joint_a1['K_nominal']:.6f} y ln K {joint_a1['ln_K_nominal']:.6f}.
Coincide con la marginal NH3 porque todas las muestras N2O superan A1.
Los K son cambios de odds de regiones, no los contrastes con molécula
omitida ni con abundancia A0 fija. Se conservan como nominales bajo priors
independientes log-uniformes [-12,-1]; validación del prior efectivo pendiente.
Probabilidades extremas se presentan como ≈100 %; no se infieren K infinitos.

## 5. Adecuación del ajuste y denominador de chi-cuadrado

El resultado nativo reporta χ²={fit['historical_full']['chi2']:.2f} →
{fit['corrected_full']['chi2']:.2f}, con χ² reducido impreso
{fit['historical_full']['chi2_red_native']:.2f} → {fit['corrected_full']['chi2_red_native']:.2f}.
POSEIDON imprime 16 grados de libertad (31 menos 15 coordenadas declaradas).
Una coordenada está fija; contando 14 parámetros libres, el denominador
efectivo es 17 y el χ² reducido nuevo vale
{fit['corrected_full']['chi2_red_effective']:.4f}. Ambas convenciones se guardan;
el ajuste sigue mostrando una discrepancia importante con el ruido asumido.

La auditoría original reconstruyó χ² multiplicando el χ² reducido ya
redondeado por sus grados de libertad. Aquí se utiliza el χ² explícito
del archivo de resultados (p.ej. 57.19 frente al reconstruido 57.12).
La diferencia es de redondeo y no altera la conclusión científica. No se
modifican productos ni auditorías originales.

## 6. Alcance de las actualizaciones

- La tabla vigente de los dos gases reemplaza solo A3–100 h por las parejas
  corregidas. Las demás exposiciones/escenarios conservan fuente histórica
  y se etiquetan explícitamente; no forman una serie corregida homogénea.
- Se actualizan las tres regiones A1 de A3–100 h en la tabla vigente de regiones.
- Las omisiones corregidas de H2O, CO2, CH4 y O3 no están disponibles.
- Las tres restricciones **A0 fija de A3–100 h con el operador nuevo no están
  disponibles**. Sus ln B históricos 29.440/1.170/31.103 y probabilidades
  condicionales históricas no se transfieren a este baseline.
- Las omisiones de una molécula y su fijación no nula en A0 plantean
  contrafactuales diferentes. Las posteriores de la especie retenida en una
  omisión se guardan separadas como sensibilidades condicionales.
- La rama A3–1000 h sigue separada y no se actualiza con estos datos.
- El manuscrito abierto no se modifica: la redacción continúa acordándose
  en el chat. Los CSV históricos y las figuras anteriores se preservan.

## 7. Interpretación actualizada

En la realización A3–100 h, el resultado corregido sostiene una preferencia
fuerte por N2O y moderada por NH3. La posterior completa sitúa ambas
abundancias por encima de A1 con aproximadamente 98.67 % de probabilidad
conjunta; los intervalos centrales del 95 % de ambas superan ese benchmark.
Esto fortalece la inferencia de enriquecimiento respecto de la versión
histórica, particularmente en NH3. La adecuación global, la aproximación
isoquímica, la realización única y el prior efectivo siguen limitando la
interpretación. No se calcula una probabilidad causal de ExoFarm.

**Cambios para el borrador acordado en chat:** sustituir las dos filas de
evidencia molecular A3–100 h; actualizar las probabilidades sobre A0/A1,
los K nominales, los intervalos/dex y la conclusión de NH3. La frase sobre
su intervalo del 95 % cruzando A0 o A1 corresponde al operador histórico:
el intervalo corregido ya queda por encima de ambas referencias. Retirar de
la conclusión corregida las evidencias de A0 fija antiguas y señalar esa
comparación como pendiente. Las cifras del S/N forward pertenecen a otra
etapa y no se recalculan mediante el cambio de una posterior.

## Reproducción

```text
.venv/Scripts/python.exe Thermal_Emission_Spectroscopy/scripts/analyse_proxima_a3_100h_corrected_update.py
```

Tablas legibles: [evidencia histórica/corregida](../{relative(OUTPUT / 'molecular_evidence.csv')}),
[regiones marginales](../{relative(OUTPUT / 'posterior_regions.csv')}),
[regiones conjuntas](../{relative(OUTPUT / 'joint_regions.csv')}),
[parámetros](../{relative(OUTPUT / 'parameter_comparison.csv')}),
[matriz vigente N2O/NH3](../{relative(OUTPUT / 'current_nitrogen_loo.csv')}) y
[regiones A1 vigentes](../{relative(OUTPUT / 'current_a1_regions.csv')}).
"""
    REPORT.write_text(text, encoding="utf-8")


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    audit_path = CAMPAIGN / "validation_report_20261020.json"
    audit = read_json(audit_path)
    require(audit["audit_status"] == "PASS" and audit["audit_errors"] == [], "Audit not accepted")
    campaign = read_json(CAMPAIGN / "campaign_state.json")
    require(campaign["acceptance"] == "VALIDATED", "Campaign not validated")
    full_state = read_json(FULL / "campaign_state.json")
    require(full_state["status"] == "COMPLETE_VALIDATED", "Full retrieval not validated")
    baseline = audit["baseline_full"]
    config = read_json(FULL / "resolved_configuration.json", baseline["configuration_sha256"])
    record(ROOT / campaign["dataset_rel"], campaign["dataset_sha256"])
    require(config["dataset_sha256"] == campaign["dataset_sha256"], "Dataset mismatch")

    references = {}
    for scenario, label in (("A0", "PreAgri"), ("A1", "Current"), ("A3", "Extreme")):
        profile_path = ROOT / f"Transmission_Spectroscopy/profiles/Proxima_b_{scenario}_{label}_chem.txt"
        profile = np.genfromtxt(record(profile_path), names=True)
        references[scenario] = {sp: log10_column_averaged_mixing_ratio(profile, sp) for sp in SPECIES}

    old_marginals = read_csv(FINAL / "life_proxima_a0_enrichment_posterior_2026-10-10.csv")
    old_source = next(r for r in old_marginals if r["scenario"] == "A3" and r["hours"] == "100" and r["species"] == "N2O")
    old_path = ROOT / old_source["samples_rel"]
    old_bundle = samples(old_path, old_source["samples_sha256"])
    old_stem = old_path.stem.removesuffix("_samples")
    old_result = old_path.parent.parent / "results" / f"{old_stem}_results.txt"
    new_result = ROOT / baseline["result"]
    record(new_result, baseline["result_sha256"])
    record(ROOT / baseline["stats"], baseline["stats_sha256"])
    new_stem = new_result.stem.removesuffix("_results")
    new_path = FULL / "products/samples" / f"{new_stem}_samples.txt"
    new_bundle = samples(new_path, baseline["posterior_sha256"])
    require(len(new_bundle[1]) == baseline["posterior_rows"], "Baseline count mismatch")
    equal = FULL / "products/MultiNest_raw" / f"{new_stem}-post_equal_weights.dat"
    record(equal, baseline["operator_product_hashes"]["posterior_equal_weights"])
    raw_equal = np.loadtxt(equal)
    require(np.array_equal(new_bundle[1], raw_equal[:, :15]), "Exported posterior differs from equal-weight samples")
    for index, name in enumerate(new_bundle[0]):
        lo, hi = config["prior_ranges"][name]
        require(np.all((new_bundle[1][:, index] >= lo-1e-10) & (new_bundle[1][:, index] <= hi+1e-10)), f"Prior violation: {name}")

    bundles = {"historical_full": (old_path, old_bundle), "corrected_full": (new_path, new_bundle)}
    fit = {"historical_full": fit_statistics(old_result, 15, 14),
           "corrected_full": fit_statistics(new_result, 15, 14)}
    old_loo = read_csv(FINAL / "life_proxima_loo_lnB_sigma_lin_2026-10-10.csv")
    evidence_rows = []
    for species in SPECIES:
        historical = next(r for r in old_loo if r["scenario"] == "A3" and r["hours"] == "100" and r["excluded_species"] == species)
        evidence_rows.append({
            "scenario": "A3", "hours": 100, "species": species, "version": "historical",
            "ln_B": float(historical["delta_lnb"]), "ln_B_numeric_error": float(historical["delta_lnb_numeric_error"]),
            "sigma_calibrated_auxiliary": float(historical["sigma_lin_convention"]),
            "lnz_full": float(historical["lnz_full"]), "lnz_omitted": float(historical["lnz_loo"]),
            "source": relative(FINAL / "life_proxima_loo_lnB_sigma_lin_2026-10-10.csv"),
        })
        ablation = next(r for r in audit["ablations"] if r["excluded_species"] == species)
        run = next(r for r in campaign["runs"] if r["excluded_species"] == species)
        product_dir = ROOT / run["archive_dir"] / "POSEIDON_output/proxima_b_earthlike/retrievals"
        stem = run["model_name"]
        sample_path = product_dir / "samples" / f"{stem}_samples.txt"
        bundle = samples(sample_path, ablation["product_hashes"]["posterior"])
        require(len(bundle[1]) == ablation["posterior_rows_final"], "Ablation count mismatch")
        record(product_dir / "MultiNest_raw" / f"{stem}-stats.dat", ablation["product_hashes"]["multinest_stats"])
        result_path = product_dir / "results" / f"{stem}_results.txt"
        record(result_path, ablation["product_hashes"]["results"])
        bundles["corrected_without_" + species] = (sample_path, bundle)
        fit["corrected_without_" + species] = fit_statistics(result_path, 14, 13)
        ln_b = baseline["lnz"] - ablation["lnz_loo"]
        error = math.hypot(baseline["lnz_error"], ablation["lnz_loo_error"])
        sigma, _ = calibrated_sigma(ln_b)
        require(abs(ln_b-ablation["delta_lnb"]) < 1e-10, "Evidence difference changed")
        require(abs(error-ablation["delta_lnb_numeric_error"]) < 1e-10, "Evidence error changed")
        evidence_rows.append({
            "scenario": "A3", "hours": 100, "species": species, "version": "corrected",
            "ln_B": ln_b, "ln_B_numeric_error": error, "sigma_calibrated_auxiliary": sigma,
            "lnz_full": baseline["lnz"], "lnz_omitted": ablation["lnz_loo"], "source": relative(audit_path),
        })

    region_rows, joint_rows = [], []
    for model, (sample_path, (names, matrix)) in bundles.items():
        for ref, thresholds in references.items():
            events, masses = {}, {}
            for species in SPECIES:
                if "log_" + species not in names:
                    continue
                values = matrix[:, names.index("log_" + species)]
                row = summarize_region(model, species, ref, values, thresholds[species], sample_path)
                region_rows.append(row)
                events[species] = values >= thresholds[species]
                masses[species] = row["nominal_prior_mass"]
            if len(events) == 2:
                q = float(np.mean(events["N2O"] & events["NH3"]))
                q0 = masses["N2O"] * masses["NH3"]
                factor, log_factor, tail = odds_update(q, q0)
                joint_rows.append({"scenario": "A3", "hours": 100, "model": model,
                                   "reference": ref, "n_samples": len(matrix), "p_both_ge_reference": q,
                                   "p_either_ge_reference": float(np.mean(events["N2O"] | events["NH3"])),
                                   "nominal_prior_mass": q0, "K_nominal": factor,
                                   "ln_K_nominal": log_factor, "tail_status": tail})

    parameter_rows = []
    for name in new_bundle[0]:
        old_q = np.quantile(old_bundle[1][:, old_bundle[0].index(name)], PROBABILITIES)
        new_q = np.quantile(new_bundle[1][:, new_bundle[0].index(name)], PROBABILITIES)
        row = {"parameter": name, "median_shift_corrected_minus_historical": float(new_q[2]-old_q[2])}
        for version, quantiles in (("historical", old_q), ("corrected", new_q)):
            row.update({f"{version}_{label}": float(v) for label, v in zip(Q_LABELS, quantiles)})
        parameter_rows.append(row)

    current_loo = []
    for old in old_loo:
        if old["excluded_species"] not in SPECIES:
            continue
        row = {"scenario": old["scenario"], "hours": int(old["hours"]), "species": old["excluded_species"],
               "operator": "historical", "ln_B": float(old["delta_lnb"]),
               "ln_B_numeric_error": float(old["delta_lnb_numeric_error"]),
               "sigma_calibrated_auxiliary": None if old["sigma_lin_convention"] == "N/A" else float(old["sigma_lin_convention"]),
               "source": relative(FINAL / "life_proxima_loo_lnB_sigma_lin_2026-10-10.csv")}
        if row["scenario"] == "A3" and row["hours"] == 100:
            new = next(x for x in evidence_rows if x["species"] == row["species"] and x["version"] == "corrected")
            row.update(operator="corrected", ln_B=new["ln_B"], ln_B_numeric_error=new["ln_B_numeric_error"],
                       sigma_calibrated_auxiliary=new["sigma_calibrated_auxiliary"], source=new["source"])
        current_loo.append(row)
    current_loo.sort(key=lambda r: (r["hours"], r["scenario"], r["species"]))

    old_a1 = BASE / "tables/a1_regions_2026-10-15"
    current_regions = []
    for old in read_csv(old_a1 / "marginal.csv"):
        r = {"scenario": old["scenario"], "hours": int(old["hours"]), "region": old["species"],
             "operator": "historical", "probability": float(old["p_ge_a1"]),
             "K_nominal": float(old["K_nominal"]) if old["K_nominal"] else None,
             "ln_K_nominal": float(old["ln_K_nominal"]) if old["ln_K_nominal"] else None}
        if r["scenario"] == "A3" and r["hours"] == 100:
            n = next(x for x in region_rows if x["model"] == "corrected_full" and x["reference"] == "A1" and x["species"] == r["region"])
            r.update(operator="corrected", probability=n["p_ge_reference"], K_nominal=n["K_nominal"], ln_K_nominal=n["ln_K_nominal"])
        current_regions.append(r)
    for old in read_csv(old_a1 / "joint.csv"):
        r = {"scenario": old["scenario"], "hours": int(old["hours"]), "region": "joint",
             "operator": "historical", "probability": float(old["p_both_ge_a1"]),
             "K_nominal": float(old["K_nominal"]) if old["K_nominal"] else None,
             "ln_K_nominal": float(old["ln_K_nominal"]) if old["ln_K_nominal"] else None}
        if r["scenario"] == "A3" and r["hours"] == 100:
            n = next(x for x in joint_rows if x["model"] == "corrected_full" and x["reference"] == "A1")
            r.update(operator="corrected", probability=n["p_both_ge_reference"], K_nominal=n["K_nominal"], ln_K_nominal=n["ln_K_nominal"])
        current_regions.append(r)
    current_regions.sort(key=lambda r: (r["hours"], r["scenario"], r["region"]))

    plot_comparison(old_bundle, new_bundle, references,
                    old_path.with_name(old_stem + "_PT_retrieved.txt"),
                    new_path.with_name(new_stem + "_PT_retrieved.txt"))
    table_rows = {"molecular_evidence.csv": evidence_rows, "posterior_regions.csv": region_rows,
                  "joint_regions.csv": joint_rows, "parameter_comparison.csv": parameter_rows,
                  "current_nitrogen_loo.csv": current_loo, "current_a1_regions.csv": current_regions}
    for name, rows in table_rows.items():
        write_csv(OUTPUT / name, rows)
        shutil.copyfile(OUTPUT / name, FINAL / f"life_proxima_a3_100h_corrected_2026-10-20_{name}")
    old_evidence = next(r for r in evidence_rows if r["version"] == "historical")
    summary = {
        "date_local": "2026-10-20", "timezone": "America/Bogota",
        "campaign_full": relative(FULL), "campaign_omissions": relative(CAMPAIGN),
        "audit_status": audit["audit_status"], "references_log10_effective": references,
        "sample_counts": {m: len(b[1][1]) for m, b in bundles.items()},
        "full_evidence": {"historical": {"lnz": old_evidence["lnz_full"]},
                          "corrected": {"lnz": baseline["lnz"], "error": baseline["lnz_error"]}},
        "operator_sensitivity_delta_lnz": baseline["lnz"] - old_evidence["lnz_full"],
        "fit_statistics": fit, "joint_regions": joint_rows,
        "input_sha256": INPUTS, "script_sha256": sha256(Path(__file__)),
        "output_sha256": {name: sha256(OUTPUT / name) for name in table_rows},
        "software": {"python": sys.version.split()[0], "numpy": np.__version__, "matplotlib": matplotlib.__version__},
        "missing_corrected_100h": ["fixed_A0_N2O", "fixed_A0_NH3", "fixed_A0_joint",
                                  "omission_H2O", "omission_CO2", "omission_CH4", "omission_O3"],
        "limits": ["operator and native-grid discretization change together",
                   "nominal prior masses; effective-prior validation remains open",
                   "one noise realization; diagonal likelihood; vertical-to-isochemical mismatch",
                   "current multi-case tables retain explicitly labelled historical rows"],
    }
    (OUTPUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    report(summary, region_rows, evidence_rows)
    require(all(sha256(ROOT / p) == digest for p, digest in INPUTS.items()), "An input was modified")
    print(json.dumps({"report": relative(REPORT), "tables": {k: len(v) for k, v in table_rows.items()},
                      "new_full_fit": fit["corrected_full"],
                      "A1_joint": next(r for r in joint_rows if r["model"] == "corrected_full" and r["reference"] == "A1")}, indent=2))


if __name__ == "__main__":
    main()
