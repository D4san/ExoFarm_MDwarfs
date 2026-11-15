"""Export paired LIFE evidence using the calibration cited by Lin et al. (2021).

Only post-process audited evidence; never launch or modify a retrieval. The
historical Bayesian-to-Gaussian calibration is an equality approximation to
a bound, not a measured frequentist significance. Non-favourable comparisons
are N/A, matching the reporting rule in Lin et al., Table 2.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path


CAMPAIGN_REL = Path(
    "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/"
    "retrievals/molecule_ablation_loo_20261004"
)
TABLE_REL = Path("Thermal_Emission_Spectroscopy/final_products/tables")
REPORT_REL = Path("docs/life_proxima_loo_sigma_lin_convention_2026-10-10.md")
SPECIES = ("H2O", "CO2", "CH4", "O3", "N2O", "NH3")
LABELS = dict(zip(SPECIES, ("H₂O", "CO₂", "CH₄", "O₃", "N₂O", "NH₃")))
METHOD = "Benneke-Seager-2013-eq8-eq9-equality-bilateral; Lin-2021-Table2-NA"


def log_two_sided_gaussian_tail(z: float) -> float:
    """Return log(erfc(z/sqrt(2))) without underflow at very large z."""
    if z <= 30.0:
        return math.log(math.erfc(z / math.sqrt(2.0)))
    # Mills-ratio expansion: eight terms suffice above z=30 (relative error
    # below 1e-12); the exponential is kept in log space for z~305.
    term = correction = 1.0
    for index in range(1, 9):
        term *= -(2 * index - 1) / (z * z)
        correction += term
    return (
        -0.5 * z * z - math.log(z)
        + 0.5 * math.log(2.0 / math.pi) + math.log(correction)
    )


def calibrated_sigma(log_b: float) -> tuple[float | None, float | None]:
    """Return historical bilateral sigma and log(p); N/A for ln B <= 0.

    Set B = -1/(e*p*ln(p)), taking 0<p<1/e. With y=-ln(p), solve
    y-ln(y)=1+ln(B), y>1. Then invert p=erfc(sigma/sqrt(2)). Working
    in log space avoids exp(ln B) overflow for the largest CO2 contrasts.
    """
    if not math.isfinite(log_b):
        raise ValueError("ln B must be finite")
    if log_b <= 0.0:
        return None, None
    target = 1.0 + log_b
    low, high = 1.0, target + math.log(target + 1.0) + 4.0
    for _ in range(120):
        mid = (low + high) / 2.0
        if mid - math.log(mid) < target:
            low = mid
        else:
            high = mid
    log_p = -(low + high) / 2.0
    low, high = 0.0, math.sqrt(-2.0 * log_p) + 2.0
    for _ in range(120):
        mid = (low + high) / 2.0
        if log_two_sided_gaussian_tail(mid) > log_p:
            low = mid
        else:
            high = mid
    return (low + high) / 2.0, log_p


def check_calibration() -> None:
    """Check equations, published rounded controls, direction and extremes."""
    # Benneke & Seager (2013), Table 2; the tabulated Bayes factors are rounded.
    for bayes_factor, rounded_sigma in ((2.9, 2.1), (12, 2.7), (21, 3.0),
                                       (150, 3.6), (43000, 5.0)):
        sigma, log_p = calibrated_sigma(math.log(bayes_factor))
        assert sigma is not None and log_p is not None
        assert abs(sigma - rounded_sigma) < 0.051
        p_value = math.erfc(sigma / math.sqrt(2.0))
        reconstructed = -1.0 - math.log(p_value) - math.log(-math.log(p_value))
        assert abs(reconstructed - math.log(bayes_factor)) < 1e-11
    assert calibrated_sigma(0.0) == (None, None)
    assert calibrated_sigma(-1.5) == (None, None)
    for log_b in (0.047, 11.127, 469.134, 46592.005):
        sigma, log_p = calibrated_sigma(log_b)
        assert sigma is not None and log_p is not None
        assert math.isfinite(sigma) and sigma > 0.0
        assert abs((-1.0 - log_p - math.log(-log_p)) - log_b) < 1e-10
        assert abs(log_two_sided_gaussian_tail(sigma) - log_p) < 1e-10
    exact_at_30 = math.log(math.erfc(30.0 / math.sqrt(2.0)))
    assert abs(log_two_sided_gaussian_tail(30.0 + 1e-10) - exact_at_30) < 4e-9


def load_validated_rows(root: Path) -> tuple[list[dict], str]:
    source = root / CAMPAIGN_REL / "loo_results_validated_20261010.csv"
    audit = json.loads((root / CAMPAIGN_REL / "validation_report_20261010.json")
                       .read_text(encoding="utf-8"))
    if (audit["campaign_status"] != "completed" or audit["validated_pairs"] != 36
            or audit["errors"] or audit["canonical_8of8_modified"]):
        raise ValueError("Campaign audit is not a clean completed 36-pair audit")
    with source.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    expected = {(s, t, x) for s in ("A1", "A3") for t in (1, 10, 100)
                for x in SPECIES}
    keys = {(r["scenario"], int(r["hours"]), r["excluded_species"]) for r in rows}
    if len(rows) != 36 or keys != expected:
        raise ValueError("CSV does not contain the complete unique 36-pair matrix")
    hashes: dict[tuple[str, int], str] = {}
    for row in rows:
        actual_hash = hashlib.sha256((root / row["dataset_rel"]).read_bytes()).hexdigest()
        if actual_hash != row["dataset_sha256"]:
            raise ValueError(f"Dataset checksum mismatch: {row['dataset_rel']}")
        key = (row["scenario"], int(row["hours"]))
        if hashes.setdefault(key, actual_hash) != actual_hash:
            raise ValueError("Ablations within one case use different datasets")
        log_b = float(row["lnz_full"]) - float(row["lnz_loo"])
        error = math.hypot(float(row["lnz_full_error"]), float(row["lnz_loo_error"]))
        if abs(log_b - float(row["delta_lnb"])) > 1e-10:
            raise ValueError("Stored ln B differs from matched evidence subtraction")
        if abs(error - float(row["delta_lnb_numeric_error"])) > 1e-12:
            raise ValueError("Stored ln B numerical error differs from quadrature")
        sigma, log_p = calibrated_sigma(log_b)
        row.update(sigma_lin_convention="N/A" if sigma is None else sigma,
                   log_p_calibration="N/A" if log_p is None else log_p,
                   sigma_status="not_favoured" if sigma is None else "calibrated",
                   sigma_method=METHOD)
    return rows, hashlib.sha256(source.read_bytes()).hexdigest()


def write_report(root: Path, rows: list[dict], source_hash: str) -> None:
    table_link = "../" + TABLE_REL.as_posix() + "/life_proxima_loo_lnB_sigma_lin_2026-10-10.csv"
    source_link = "../" + CAMPAIGN_REL.as_posix() + "/loo_results_validated_20261010.csv"
    script_link = "../Thermal_Emission_Spectroscopy/scripts/report_proxima_loo_lin_sigma.py"
    text = f"""# LIFE Proxima: ln B y sigma con la convención citada por Lin et al.

Fecha del análisis y consulta de fuentes: 2026-10-10. Campaña:
`proxima_a1_a3_molecule_ablation_loo_20261004`; A1/A3 × 1/10/100 h × seis especies.

## Método y trazabilidad bibliográfica

**Hecho de fuente:** [Lin et al. (2021), §5.2, p. 10 del manuscrito](https://arxiv.org/pdf/2105.09319#page=10)
comparan la evidencia del retrieval completo con modelos que excluyen moléculas
y remiten a Benneke & Seager (2013) y MacDonald & Madhusudhan (2017) para la
significancia. Su **tabla 2, p. 11** muestra `N/A` cuando el factor de Bayes
no favorece la presencia de la especie (`B ≲ 1`).

**Reconstrucción metodológica:** Lin et al. no imprimen una ecuación de conversión
ni publican en esa tabla sus Bayes factors. Aquí implementamos la calibración
explícita de su referencia [Benneke & Seager (2013), §2.2, ecuaciones (8)–(9),
tabla 2, p. 5](https://arxiv.org/pdf/1306.6325#page=5), basada en Trotta (2008)
y Sellke et al. (2001). Esto reproduce la convención bibliográfica citada;
no constituye una comprobación del código privado de Lin et al.

Para cada pareja con **el mismo dataset y realización de ruido**:

\\[
\\ln B=\\ln Z_{{\\rm completo}}-\\ln Z_{{\\rm sin\\,X}},\\qquad
\\delta_{{\\rm num}}(\\ln B)=\\sqrt{{\\delta_{{\\rm num}}(\\ln Z_{{\\rm completo}})^2+
\\delta_{{\\rm num}}(\\ln Z_{{\\rm sin\\,X}})^2}}.
\\]

Para `ln B > 0`, igualamos la calibración de la ecuación (8) e invertimos:

\\[
B=\\frac{{-1}}{{e\\,p\\ln p}},\\quad 0<p<e^{{-1}},\\qquad
p=1-\\operatorname{{erf}}\\!\\left(\\frac{{\\sigma_{{\\rm cal}}}}{{\\sqrt{{2}}}}\\right)
=\\operatorname{{erfc}}\\!\\left(\\frac{{\\sigma_{{\\rm cal}}}}{{\\sqrt{{2}}}}\\right).
\\]

Se utiliza la rama `y=-ln p > 1` de `y-ln y=1+ln B`. Es una calibración
**bilateral**. Para `ln B ≤ 0` guardamos `N/A`, conservando el signo y valor de
`ln B`; no aplicamos valor absoluto ni asignamos sigma negativos de detección.
Los valores positivos coinciden con la tabla auxiliar anterior a la precisión
mostrada. La incertidumbre de `ln B` describe el error numérico de MultiNest,
con independencia asumida entre corridas; no es incertidumbre observacional.

**Límite de interpretación:** la ecuación (8) original es una desigualdad.
Su inversión como igualdad es la práctica histórica que se desea reproducir,
no una equivalencia universal ni un p-value medido. Las objeciones posteriores
de [Kipping & Benneke (2025)](https://arxiv.org/abs/2506.05392) y
[Thorngren et al. (2025)](https://arxiv.org/abs/2510.00169) siguen vigentes.
`ln B` es la métrica primaria; la columna sigma se etiqueta como calibrada.

## Tabla guardada

[CSV con precisión completa]({table_link}). `N/A` significa que el valor central
del contraste no favorece incluir la molécula; no significa sigma cero.
Las cifras sigma se muestran con dos decimales para lectura.

| Escenario | Exposición | Molécula | ln B ± error numérico | σ calibrado, convención Lin |
| --- | ---: | --- | ---: | ---: |
"""
    for row in rows:
        sigma = row["sigma_lin_convention"]
        formatted = "N/A" if sigma == "N/A" else f"{sigma:.2f}"
        text += (f"| {row['scenario']} | {row['hours']} h | {LABELS[row['excluded_species']]} "
                 f"| {float(row['delta_lnb']):+.3f} ± "
                 f"{float(row['delta_lnb_numeric_error']):.3f} | {formatted} |\n")
    text += f"""
## Diagnóstico condicionado a la campaña

H₂O, CO₂ y CH₄ favorecen la inclusión en las seis observaciones. O₃ alcanza
9.03σ calibrados en A1-100 h y 6.59σ en A3-100 h. N₂O alcanza 4.25σ y 11.67σ
en A3 a 10 y 100 h; en A1-100 h queda en 2.36σ. NH₃ presenta preferencia
débil solo en A3-100 h (`ln B=1.506 ± 0.342`, 2.31σ calibrados).

Los valores enormes de CO₂ (hasta 305.28σ calibrados) expresan la magnitud de
la comparación dentro de estos modelos. La adecuación absoluta exige atención:
los retrievals completos de 100 h tienen χ² reducido 3.18 (A1) y 4.94 (A3),
con 16 grados de libertad. Se conservan las limitaciones de abundancias
isochem frente a perfiles verticales VULCAN, una realización diagonal por
dataset, sensibilidad a priors y ausencia de covarianza instrumental. A1-1 h
usa la realización NoiseRepeat2 promovida post hoc; no se estima cobertura
con esta campaña. Véase el [informe LOO](life_proxima_molecular_ablation_loo_2026-10-04.md).

## Reproducción y verificación

Se cargaron las 36 parejas del [CSV auditado]({source_link}), sin ejecutar
retrievals. Se verificaron cardinalidad y claves únicas, estado de auditoría,
SHA-256 de los seis datasets, resta de evidencias y propagación del error.
SHA-256 del CSV de entrada: `{source_hash}`.

El [script de cálculo]({script_link}) utiliza exclusivamente la biblioteca
estándar de Python y resuelve en logaritmos para evitar overflow de `exp(ln B)`
y underflow de p. Sus controles reproducen a la precisión publicada la tabla 2
de Benneke & Seager (B=2.9, 12, 21, 150 y 43000), prueban `N/A` para B≤1 y
comprueban ambas ecuaciones hasta `ln B=46592.005`.

Desde la raíz del repositorio:

```text
python Thermal_Emission_Spectroscopy/scripts/report_proxima_loo_lin_sigma.py --repo .
```

El CSV auditado anterior conserva su columna firmada como producto histórico.
La tabla de reporte vigente usa `sigma_lin_convention` y `N/A`. Las 36 ablaciones,
los seis retrievals completos, sus datasets y la matriz legacy 8/8 permanecen
intactos. El JSON contiguo al CSV guarda la validación de esta exportación.
"""
    (root / REPORT_REL).write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.repo.resolve()
    check_calibration()
    rows, source_hash = load_validated_rows(root)
    output = root / TABLE_REL
    output.mkdir(parents=True, exist_ok=True)
    csv_path = output / "life_proxima_loo_lnB_sigma_lin_2026-10-10.csv"
    fields = ["scenario", "hours", "excluded_species", "delta_lnb",
              "delta_lnb_numeric_error", "sigma_lin_convention", "sigma_status",
              "lnz_full", "lnz_full_error", "lnz_loo", "lnz_loo_error",
              "dataset_rel", "dataset_seed", "dataset_sha256",
              "log_p_calibration", "sigma_method"]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    write_report(root, rows, source_hash)
    with csv_path.open(encoding="utf-8", newline="") as handle:
        saved = list(csv.DictReader(handle))
    assert len(saved) == 36
    assert [r["delta_lnb"] for r in saved] == [r["delta_lnb"] for r in rows]
    na_count = sum(r["sigma_lin_convention"] == "N/A" for r in saved)
    validation = {
        "campaign_id": "proxima_a1_a3_molecule_ablation_loo_20261004",
        "input_sha256": source_hash,
        "rows": 36,
        "calibrated_sigma_rows": 36 - na_count,
        "not_favoured_na_rows": na_count,
        "calibration_controls": "PASS",
        "paired_evidence_and_dataset_checks": "PASS",
        "csv_roundtrip": "PASS",
        "method": METHOD,
        "retrievals_launched": 0,
        "sources": ["https://arxiv.org/pdf/2105.09319#page=10",
                    "https://arxiv.org/pdf/2105.09319#page=11",
                    "https://arxiv.org/pdf/1306.6325#page=5"],
    }
    csv_path.with_suffix(".validation.json").write_text(
        json.dumps(validation, indent=2) + "\n", encoding="utf-8"
    )
    print(f"PASS: 36 pairs; {36-na_count} calibrated sigma; {na_count} N/A.")
    print(csv_path)
    print(root / REPORT_REL)


if __name__ == "__main__":
    main()
