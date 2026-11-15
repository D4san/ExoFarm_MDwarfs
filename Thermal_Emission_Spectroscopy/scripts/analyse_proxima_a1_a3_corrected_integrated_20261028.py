"""Recompute the corrected LIFE Proxima retrieval analysis from native products.

The 1/10/100 h matrix and the exploratory 1000 h fixed-A0 comparison are
processed separately. This script never launches retrievals or edits inputs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import re
import sys
from pathlib import Path
from statistics import NormalDist

import numpy as np


DATE = "2026-10-28"  # project date in America/Bogota
BASE_REL = Path("Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1")
RETR_REL = BASE_REL / "retrievals"
MAIN = "a1_a3_corrected_binning_matrix_loo_20261021_r01"
SHORT = "a3_1_10h_binning_corrected_loo_20261020_r03"
FULL100 = "a3_100h_binning_corrected_mpi14_resume_20261018"
LOO100 = "a3_100h_binning_corrected_loo_20261019"
FULL1000 = "a3_1000h_binning_corrected_20261014"
FIXED1000 = "a0_fixed_reference_A3_1000h_binning_corrected_20261016_relaunch_01"
FROZEN_REL = Path("docs/evidence/life_proxima_a1_a3_release_2026-10-28/SHA256SUMS.txt")
FROZEN_HASH = "39af0fa0982008b15b3b854a25bbcc6a163093eb810329df12b10afce9126e87"
OUT_REL = Path("Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a1_a3_integrated_20261028")
REPORT_REL = Path("docs/life_proxima_a1_a3_retrievals_analisis_integrado_2026-10-28.md")
SCRIPT_REL = Path("Thermal_Emission_Spectroscopy/scripts/analyse_proxima_a1_a3_corrected_integrated_20261028.py")
GASES = ("N2O", "NH3", "H2O", "CO2", "CH4", "O3", "O2")
LOO_SPECIES = GASES[:-1]
HOURS = (1, 10, 100)
SCENARIOS = ("A1", "A3")
PROFILE_STEMS = {"A0": "Proxima_b_A0_PreAgri", "A1": "Proxima_b_A1_Current", "A3": "Proxima_b_A3_Extreme"}
REGIONS = ("R11", "R10", "R01", "R00")
QUANTILES = (0.025, 0.16, 0.5, 0.84, 0.975)
Q_NAMES = ("q025", "q16", "median", "q84", "q975")
STATS_RE = re.compile(r"Nested Sampling Global Log-Evidence\s*:\s*([-+\d.eE]+)\s*\+/-\s*([-+\d.eE]+)")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict]) -> None:
    require(bool(rows), f"Empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def one_file(directory: Path, pattern: str) -> Path:
    matches = list(directory.glob(pattern))
    require(len(matches) == 1, f"Expected one {pattern} in {directory}; got {len(matches)}")
    return matches[0]


def wilson_reference(count: int, n: int) -> tuple[float, float]:
    """95% Wilson interval under iid Bernoulli draws; not nested-sampling error."""
    z = NormalDist().inv_cdf(0.975)
    p = count / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    width = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - width), min(1.0, centre + width)


def odds_update(q: float, q0: float) -> float | None:
    if not 0 < q < 1 or not 0 < q0 < 1:
        return None
    return q * (1 - q0) / ((1 - q) * q0)


def fmt(value, digits: int = 3) -> str:
    if value is None or value == "":
        return "—"
    return f"{float(value):.{digits}f}"


def pct(value, count: int | None = None, n: int | None = None) -> str:
    if value is None or value == "":
        return "—"
    if count == 0 or (count is None and float(value) == 0.0):
        return "0 en muestra"
    if (n is not None and count == n) or (count is None and float(value) == 1.0):
        return "100 en muestra"
    return f"{100 * float(value):.2f}%"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()
    root = args.repo.resolve()
    out = (args.output or root / OUT_REL).resolve()
    report_path = (args.report or root / REPORT_REL).resolve()
    require(not out.exists(), f"Output already exists: {out}")
    require(not report_path.exists(), f"Report already exists: {report_path}")
    sys.path.insert(0, str(root / "Thermal_Emission_Spectroscopy/scripts"))
    from life_bin_operator_diagnostic import LifePhotonOperator
    from report_proxima_loo_lin_sigma import calibrated_sigma, check_calibration
    from retrieval_reference import log10_column_averaged_mixing_ratio
    from validate_proxima_molecular_ablation_loo import validate_log_x

    check_calibration()
    frozen_file = root / FROZEN_REL
    require(sha256(frozen_file) == FROZEN_HASH, "Frozen checksum manifest changed")
    frozen: dict[str, str] = {}
    for line in frozen_file.read_text(encoding="utf-8").splitlines():
        digest, sep, rel = line.partition("  ")
        require(bool(sep) and len(digest) == 64 and rel not in frozen, "Invalid frozen inventory")
        frozen[rel] = digest
    require(len(frozen) == 979, "Unexpected frozen inventory size")
    inputs: dict[str, str] = {}

    def record(path: Path, *, in_frozen: bool = True, expected: str | None = None) -> Path:
        path = path.resolve()
        rel = path.relative_to(root).as_posix()
        if rel not in inputs:
            require(path.is_file(), f"Missing file: {rel}")
            digest = sha256(path)
            if in_frozen:
                require(rel in frozen and digest == frozen[rel], f"Missing or changed frozen input: {rel}")
            inputs[rel] = digest
        if expected is not None:
            require(inputs[rel] == expected, f"Audit hash mismatch: {rel}")
        return path

    def load_json(path: Path, **kw) -> dict:
        return json.loads(record(path, **kw).read_text(encoding="utf-8"))

    for script in ("life_bin_operator_diagnostic.py", "report_proxima_loo_lin_sigma.py", "retrieval_reference.py", "validate_proxima_molecular_ablation_loo.py"):
        record(root / "Thermal_Emission_Spectroscopy/scripts" / script)
    preserve = load_json(root / RETR_REL / MAIN / "preserved_inputs.json")
    datasets: dict[tuple[str, int], dict] = {}
    for key, item in preserve["datasets"].items():
        scenario, time_name = key.split("_")
        hours = int(time_name.removesuffix("h"))
        file = record(root / item["path"], expected=item["sha256"])
        data = np.loadtxt(file, skiprows=1)
        require(data.shape == (31, 4) and np.isfinite(data).all() and np.all(data[:, 3] > 0), f"Bad dataset {key}")
        datasets[(scenario, hours)] = {"path": file, "data": data, "sha256": item["sha256"], "seed": item["seed"]}
    require(set(datasets) == {(s, h) for s in SCENARIOS for h in HOURS}, "Incomplete datasets")

    references: dict[str, dict[str, float]] = {}
    profiles: dict[str, np.ndarray] = {}
    for scenario, stem in PROFILE_STEMS.items():
        path = record(root / "Transmission_Spectroscopy/profiles" / f"{stem}_chem.txt")
        profile = np.genfromtxt(path, names=True)
        profiles[scenario] = profile
        references[scenario] = {g: log10_column_averaged_mixing_ratio(profile, g) for g in GASES}

    def read_result(path: Path, *, in_frozen: bool = True, expected: str | None = None) -> dict:
        text = record(path, in_frozen=in_frozen, expected=expected).read_text(encoding="utf-8")
        patterns = {"chi2": r"->\s*chi\^2\s*=\s*([-+\d.eE]+)",
                    "chi2_red_reported": r"->\s*chi\^2_red\s*=\s*([-+\d.eE]+)",
                    "dof_reported": r"->\s*degrees of freedom\s*=\s*([0-9]+)",
                    "lnz_reported": r"->\s*ln\s+Z\s*=\s*([-+\d.eE]+)\s*\+/-\s*([-+\d.eE]+)"}
        matches = {k: re.search(v, text, re.IGNORECASE) for k, v in patterns.items()}
        require(all(matches.values()), f"Incomplete POSEIDON result: {path}")
        return {"chi2": float(matches["chi2"].group(1)),
                "chi2_red_reported": float(matches["chi2_red_reported"].group(1)),
                "dof_reported": int(matches["dof_reported"].group(1)),
                "lnz_reported": float(matches["lnz_reported"].group(1)),
                "lnz_error_reported": float(matches["lnz_reported"].group(2))}

    def read_stats(path: Path, *, in_frozen: bool = True, expected: str | None = None) -> tuple[float, float]:
        text = record(path, in_frozen=in_frozen, expected=expected).read_text(encoding="utf-8")
        match = STATS_RE.search(text)
        require(match is not None, f"Missing native evidence: {path}")
        value, error = float(match.group(1)), float(match.group(2))
        require(math.isfinite(value) and math.isfinite(error) and error >= 0, f"Bad evidence: {path}")
        return value, error

    def load_model(row: dict, scenario: str, hours: int, excluded: str, *, full100: bool = False) -> dict:
        case = datasets[(scenario, hours)]
        status = str(row["status"]).lower()
        require(status in {"validated", "complete_validated"} and str(row["return_code"]) == "0", f"Not validated: {row['run_id']}")
        require(row["dataset_sha256_expected"] == case["sha256"], f"Manifest dataset mismatch: {row['run_id']}")
        config_path = root / Path(row["configuration_json"])
        cfg = load_json(config_path)
        require(cfg["dataset_sha256"] == case["sha256"], f"Configuration dataset mismatch: {row['run_id']}")
        require(cfg["n_live"] == 800 and cfg["R"] == 10000 and cfg["ev_tol"] == 0.5, f"Unexpected sampling settings: {row['run_id']}")
        require(cfg["x_profile"] == "isochem" and not cfg["fixed_log10_abundances"], f"Unexpected chemistry: {row['run_id']}")
        require(cfg["effective_free_dimension"] == (13 if excluded else 14), f"Unexpected dimension: {row['run_id']}")
        require((f"log_{excluded}" not in cfg["parameters"] and excluded not in cfg["param_species"]) if excluded else all(f"log_{g}" in cfg["parameters"] for g in GASES), f"Species mismatch: {row['run_id']}")
        operator = load_json(root / Path(row["operator_runtime"]))
        bound = operator.get("actual_poseidon_callback_bound") is True or operator.get("actual_forward_model_callback_bound") is True
        scope = operator.get("binding_scope", "").lower()
        binding = operator.get("sampling_and_postprocessing_binding") is True or ("sampling" in scope and "post" in scope)
        require(operator.get("status") == "PASS" and operator.get("dataset_sha256") == case["sha256"] and bound and binding, f"Operator mismatch: {row['run_id']}")
        require(operator.get("channels") == 31, f"Operator channel mismatch: {row['run_id']}")
        folder = root / Path(row["archive_dir"])
        if not full100:
            folder = folder / "POSEIDON_output/proxima_b_earthlike/retrievals"
        sample = record(one_file(folder / "samples", "*_samples.txt"))
        spectrum = record(one_file(folder / "samples", "*_spectrum_retrieved.txt"))
        pt = record(one_file(folder / "samples", "*_PT_retrieved.txt"))
        logx = record(one_file(folder / "samples", "*_log_X_retrieved.txt"))
        result = read_result(one_file(folder / "results", "*_results.txt"))
        stats = one_file(folder / "MultiNest_raw", "*-stats.dat")
        lnz, lnz_error = read_stats(stats)
        require(abs(result["lnz_reported"] - lnz) < 0.011 and abs(result["lnz_error_reported"] - lnz_error) < 0.011, f"Evidence mismatch: {row['run_id']}")
        equal_path = record(one_file(folder / "MultiNest_raw", "*-post_equal_weights.dat"))
        weighted_path = record(one_file(folder / "MultiNest_raw", "*-.txt"))
        with sample.open(encoding="utf-8") as stream:
            names = [x.strip() for x in stream.readline().split("|")]
        values = np.atleast_2d(np.loadtxt(sample, skiprows=1))
        equal = np.atleast_2d(np.loadtxt(equal_path))
        weighted = np.atleast_2d(np.loadtxt(weighted_path))
        require(names == cfg["parameters"] and values.shape[1] == len(names), f"Posterior header mismatch: {row['run_id']}")
        require(np.isfinite(values).all() and np.isfinite(equal).all() and np.isfinite(weighted).all(), f"Nonfinite posterior: {row['run_id']}")
        require(equal.shape == (len(values), len(names) + 1) and np.allclose(values, equal[:, :len(names)], rtol=0, atol=1e-12), f"Posterior/equal-weight mismatch: {row['run_id']}")
        require(weighted.shape[1] == len(names) + 2 and np.all(weighted[:, 0] >= 0), f"Weighted shape/weights mismatch: {row['run_id']}")
        weight_sum = float(np.sum(weighted[:, 0]))
        require(abs(weight_sum - 1.0) < 1e-6, f"Weights not normalized: {row['run_id']}")
        weights = weighted[:, 0] / weight_sum
        weight_ess = float(1.0 / np.sum(weights * weights))
        spec = np.loadtxt(spectrum, skiprows=1)
        temps = np.loadtxt(pt, skiprows=1)
        require(spec.ndim == 2 and spec.shape[1] == 6 and len(spec) >= 1000 and np.isfinite(spec).all() and np.all(np.diff(spec[:, 0]) > 0), f"Invalid spectrum: {row['run_id']}")
        require(np.all(np.diff(spec[:, 1:], axis=1) >= -1e-20), f"Spectrum quantile order: {row['run_id']}")
        require(temps.shape == (100, 6) and np.isfinite(temps).all() and np.all(np.diff(temps[:, 0]) < 0), f"Invalid PT: {row['run_id']}")
        require(np.all(np.diff(temps[:, 1:], axis=1) >= -1e-8), f"PT quantile order: {row['run_id']}")
        logx_rows = validate_log_x(logx, excluded)
        return {"run_id": row["run_id"], "scenario": scenario, "hours": hours, "excluded_species": excluded,
                "config": cfg, "lnz": lnz, "lnz_error": lnz_error, "result": result,
                "n_samples": len(values), "n_weighted": len(weighted), "weight_ess": weight_ess,
                "names": names, "samples": values, "weighted": weighted[:, 2:], "weights": weights,
                "spectrum": spec, "pt": temps, "logx_rows": logx_rows, "dataset_sha256": case["sha256"],
                "source_campaign": row["source_campaign"], "sample_rel": sample.relative_to(root).as_posix(),
                "stats_rel": stats.relative_to(root).as_posix(), "config_rel": config_path.relative_to(root).as_posix()}

    rows = []
    main_path = record(root / RETR_REL / MAIN / "manifest.csv")
    for item in read_csv(main_path):
        item["source_campaign"] = MAIN
        rows.append((item, item["scenario"], int(item["hours"]), item["excluded_species"], False))
    short_path = record(root / RETR_REL / SHORT / "manifest.csv")
    for item in read_csv(short_path):
        item["source_campaign"] = SHORT
        rows.append((item, "A3", int(item["hours"]), item["excluded_species"], False))
    loo100_path = record(root / RETR_REL / LOO100 / "manifest.csv")
    for item in read_csv(loo100_path):
        item["source_campaign"] = LOO100
        rows.append((item, "A3", 100, item["excluded_species"], False))
    full100_path = record(root / RETR_REL / FULL100 / "manifest.csv")
    f100 = read_csv(full100_path)
    require(len(f100) == 1, "Unexpected 100 h reference manifest")
    item = f100[0]
    item.update(source_campaign=FULL100, dataset_sha256_expected=item["dataset_sha256"],
                archive_dir=(RETR_REL / FULL100 / "products").as_posix(),
                configuration_json=(RETR_REL / FULL100 / "resolved_configuration.json").as_posix(),
                operator_runtime=(RETR_REL / FULL100 / "operator_preflight_mpi14_retry01.json").as_posix())
    rows.append((item, "A3", 100, "", True))
    require(len(rows) == 42, f"Expected 42 models, found {len(rows)}")

    models: dict[tuple[str, int, str], dict] = {}
    for item, scenario, hours, excluded, special in rows:
        key = (scenario, hours, excluded)
        require(key not in models, f"Duplicate model {key}")
        models[key] = load_model(item, scenario, hours, excluded, full100=special)
    expected_keys = {(s, h, gas) for s in SCENARIOS for h in HOURS for gas in ("", *LOO_SPECIES)}
    require(set(models) == expected_keys, "Model matrix is incomplete")
    model_rows, probability_rows, posterior_rows, loo_rows = [], [], [], []

    for key in sorted(models, key=lambda k: (SCENARIOS.index(k[0]), HOURS.index(k[1]), -1 if not k[2] else LOO_SPECIES.index(k[2]))):
        m = models[key]
        cfg, names, values, weighted, weights = m["config"], m["names"], m["samples"], m["weighted"], m["weights"]
        r = m["result"]
        effective_dof = 31 - cfg["effective_free_dimension"]
        model_rows.append({"scenario": key[0], "hours": key[1], "excluded_species": key[2] or "none",
            "run_id": m["run_id"], "source_campaign": m["source_campaign"], "dataset_sha256": m["dataset_sha256"],
            "lnz": m["lnz"], "lnz_error": m["lnz_error"], "chi2_printed": r["chi2"],
            "chi2_red_reported": r["chi2_red_reported"], "dof_reported": r["dof_reported"],
            "dof_effective": effective_dof, "chi2_red_effective_from_rounded_chi2": r["chi2"] / effective_dof,
            "n_equal": m["n_samples"], "n_weighted": m["n_weighted"], "weight_ess_concentration_only": m["weight_ess"],
            "posterior_rel": m["sample_rel"], "native_stats_rel": m["stats_rel"], "config_rel": m["config_rel"]})
        for gas in ("N2O", "NH3"):
            if f"log_{gas}" not in names:
                for reference in ("A0", "A1"):
                    probability_rows.append({"scenario": key[0], "hours": key[1], "excluded_species": key[2] or "none", "gas": gas,
                        "reference": reference, "threshold_log10": references[reference][gas], "n_equal": len(values),
                        "n_ge": None, "p_equal": None, "p_weighted": None, "wilson_iid_low": None, "wilson_iid_high": None,
                        "status": "species_excluded"})
                continue
            i = names.index(f"log_{gas}")
            for reference in ("A0", "A1"):
                threshold = references[reference][gas]
                count = int(np.count_nonzero(values[:, i] >= threshold))
                low, high = wilson_reference(count, len(values))
                probability_rows.append({"scenario": key[0], "hours": key[1], "excluded_species": key[2] or "none", "gas": gas,
                    "reference": reference, "threshold_log10": threshold, "n_equal": len(values), "n_ge": count,
                    "p_equal": count / len(values), "p_weighted": float(np.sum(weights * (weighted[:, i] >= threshold))),
                    "wilson_iid_low": low, "wilson_iid_high": high,
                    "status": "unsampled_tail" if count in (0, len(values)) else ("sparse_tail" if min(count, len(values)-count) < 20 else "sampled")})
        if not key[2]:
            for i, name in enumerate(names):
                quantiles = np.quantile(values[:, i], QUANTILES)
                gas = name.removeprefix("log_") if name.startswith("log_") else ""
                row = {"scenario": key[0], "hours": key[1], "parameter": name,
                       **{label: float(value) for label, value in zip(Q_NAMES, quantiles)},
                       "n_equal": len(values), "fixed_parameter": name in cfg["fixed_parameters"]}
                for ref in ("A0", "A1", "A3"):
                    threshold = references[ref].get(gas)
                    row[f"reference_{ref}_log10"] = threshold
                    row[f"p_ge_{ref}"] = None if threshold is None else float(np.mean(values[:, i] >= threshold))
                    row[f"ratio_median_to_{ref}"] = None if threshold is None else float(10 ** (quantiles[2] - threshold))
                    row[f"ratio_q025_to_{ref}"] = None if threshold is None else float(10 ** (quantiles[0] - threshold))
                    row[f"ratio_q975_to_{ref}"] = None if threshold is None else float(10 ** (quantiles[4] - threshold))
                posterior_rows.append(row)

    for scenario in SCENARIOS:
        for hours in HOURS:
            full = models[(scenario, hours, "")]
            for gas in LOO_SPECIES:
                reduced = models[(scenario, hours, gas)]
                a, b = full["config"], reduced["config"]
                require(a["dataset_sha256"] == b["dataset_sha256"] == full["dataset_sha256"], f"Dataset mismatch {scenario} {hours} {gas}")
                require(b["parameters"] == [x for x in a["parameters"] if x != f"log_{gas}"], f"Parameter mismatch {scenario} {hours} {gas}")
                require(b["param_species"] == [x for x in a["param_species"] if x != gas], f"Opacity-species mismatch {scenario} {hours} {gas}")
                for param in b["parameters"]:
                    require(a["prior_types"][param] == b["prior_types"][param] and a["prior_ranges"][param] == b["prior_ranges"][param], f"Prior mismatch {scenario} {hours} {gas} {param}")
                for field in ("R", "wl_min", "wl_max", "n_live", "ev_tol", "surface_pressure_mode", "error_inflation", "x_profile", "likelihood"):
                    require(a[field] == b[field], f"Setting mismatch {scenario} {hours} {gas} {field}")
                delta = full["lnz"] - reduced["lnz"]
                error = math.hypot(full["lnz_error"], reduced["lnz_error"])
                sigma, _ = calibrated_sigma(delta)
                loo_rows.append({"scenario": scenario, "hours": hours, "excluded_species": gas,
                    "full_run_id": full["run_id"], "loo_run_id": reduced["run_id"], "dataset_sha256": full["dataset_sha256"],
                    "lnz_full": full["lnz"], "lnz_full_error": full["lnz_error"], "lnz_loo": reduced["lnz"],
                    "lnz_loo_error": reduced["lnz_error"], "delta_lnz": delta, "delta_error_quadrature": error,
                    "sigma_calibrated_auxiliary": sigma, "chi2_red_full_reported": full["result"]["chi2_red_reported"],
                    "chi2_red_loo_reported": reduced["result"]["chi2_red_reported"],
                    "full_source_campaign": full["source_campaign"], "loo_source_campaign": reduced["source_campaign"]})

    # Compare recomputation to independent previously archived audits, without using
    # those tables as the numerical input to any comparison.
    prior_rows = []
    previous_matrix = read_csv(record(root / "docs/life_proxima_a1_a3_corrected_binning_matrix_loo_2026-10-28.csv"))
    for row in previous_matrix:
        prior_rows.append((row["scenario"], int(row["hours"]), row["excluded_species"], float(row["delta_lnz_full_minus_loo"]), float(row["delta_error_quadrature"])))
    previous_short = read_csv(record(root / RETR_REL / SHORT / "loo_results_validated_20261021.csv"))
    for row in previous_short:
        prior_rows.append(("A3", int(row["hours"]), row["excluded_species"], float(row["delta_lnb_full_minus_without"]), float(row["delta_lnb_numeric_error_quadrature"])))
    previous_100 = read_csv(record(root / RETR_REL / LOO100 / "loo_results_validated_20261020.csv"))
    for row in previous_100:
        prior_rows.append(("A3", 100, row["excluded_species"], float(row["delta_lnb"]), float(row["delta_lnb_numeric_error"])))
    require(len(prior_rows) == 36, "Previous audits do not cover 36 LOO pairs")
    for s, h, gas, old_delta, old_error in prior_rows:
        new = next(x for x in loo_rows if (x["scenario"], x["hours"], x["excluded_species"]) == (s, h, gas))
        require(abs(new["delta_lnz"] - old_delta) < 1e-9 and abs(new["delta_error_quadrature"] - old_error) < 1e-10, f"Prior audit mismatch {s} {h} {gas}")

    enrichment_rows = []
    for scenario in SCENARIOS:
        for hours in HOURS:
            m = models[(scenario, hours, "")]
            for gas in ("N2O", "NH3"):
                idx = m["names"].index(f"log_{gas}")
                for ref in ("A0", "A1", "A3"):
                    threshold = references[ref][gas]
                    delta_values = m["samples"][:, idx] - threshold
                    quantiles = np.quantile(delta_values, QUANTILES)
                    count = int(np.count_nonzero(delta_values >= 0))
                    enrichment_rows.append({"scenario": scenario, "hours": hours, "gas": gas,
                        "reference": ref, "reference_log10": threshold,
                        **{f"delta_dex_{name}": float(q) for name, q in zip(Q_NAMES, quantiles)},
                        **{f"factor_{name}": float(10**q) for name, q in zip(Q_NAMES, quantiles)},
                        "n_equal": len(delta_values), "count_ge_reference": count,
                        "p_equal_ge_reference": count / len(delta_values),
                        "p_weighted_ge_reference": float(np.sum(m["weights"] * (m["weighted"][:, idx] >= threshold))),
                        "tail_status": "unsampled_tail" if count in (0, len(delta_values)) else ("sparse_tail" if min(count, len(delta_values)-count) < 20 else "sampled")})

    region_rows, marginal_rows, joint_summary = [], [], []
    for scenario in SCENARIOS:
        for hours in HOURS:
            m = models[(scenario, hours, "")]
            cfg, vals, weighted, weights, names = m["config"], m["samples"], m["weighted"], m["weights"], m["names"]
            i, j = names.index("log_N2O"), names.index("log_NH3")
            for gas in ("N2O", "NH3"):
                require(cfg["prior_types"][f"log_{gas}"] == "uniform" and cfg["prior_ranges"][f"log_{gas}"] == [-12, -1], f"Unexpected regional prior: {scenario} {hours} {gas}")
            for ref in ("A0", "A1"):
                t1, t2 = references[ref]["N2O"], references[ref]["NH3"]
                p1, p2 = (-1 - t1) / 11, (-1 - t2) / 11
                require(0 < p1 < 1 and 0 < p2 < 1, "Threshold outside prior")
                prior = {"R11": p1*p2, "R10": p1*(1-p2), "R01": (1-p1)*p2, "R00": (1-p1)*(1-p2)}
                flags = (vals[:, i] >= t1, vals[:, j] >= t2)
                wf = (weighted[:, i] >= t1, weighted[:, j] >= t2)
                masks = {"R11": flags[0]&flags[1], "R10": flags[0]&~flags[1], "R01": ~flags[0]&flags[1], "R00": ~flags[0]&~flags[1]}
                wmasks = {"R11": wf[0]&wf[1], "R10": wf[0]&~wf[1], "R01": ~wf[0]&wf[1], "R00": ~wf[0]&~wf[1]}
                require(sum(int(mask.sum()) for mask in masks.values()) == len(vals), "Regions do not partition posterior")
                summary = {"scenario": scenario, "hours": hours, "reference": ref, "n_equal": len(vals), "weight_ess_concentration_only": m["weight_ess"]}
                for name in REGIONS:
                    count = int(masks[name].sum())
                    q = count / len(vals)
                    wq = float(np.sum(weights * wmasks[name]))
                    lo, hi = wilson_reference(count, len(vals))
                    region_rows.append({"scenario": scenario, "hours": hours, "reference": ref, "region": name,
                        "n_equal": len(vals), "count": count, "p_equal": q, "p_weighted": wq, "p_prior": prior[name],
                        "K_vs_complement": odds_update(q, prior[name]), "wilson_iid_low": lo, "wilson_iid_high": hi,
                        "tail_status": "unsampled" if count == 0 else ("unsampled_complement" if count == len(vals) else ("sparse" if min(count, len(vals)-count) < 20 else "sampled"))})
                    summary[name] = q
                    summary[name + "_count"] = count
                    summary[name + "_weighted"] = wq
                summary["prior_R11"] = prior["R11"]
                summary["K_R11_vs_complement"] = odds_update(summary["R11"], prior["R11"])
                summary["K_R11_vs_R10"] = None if summary["R10"] == 0 else (summary["R11"] / summary["R10"]) / (prior["R11"] / prior["R10"])
                summary["pearson_logN2O_logNH3"] = float(np.corrcoef(vals[:, i], vals[:, j])[0, 1])
                joint_summary.append(summary)
                for gas, idx, prior_mass in (("N2O", i, p1), ("NH3", j, p2)):
                    count = int(np.count_nonzero(vals[:, idx] >= references[ref][gas]))
                    q = count / len(vals)
                    lo, hi = wilson_reference(count, len(vals))
                    marginal_rows.append({"scenario": scenario, "hours": hours, "reference": ref, "gas": gas,
                        "n_equal": len(vals), "count": count, "p_equal": q,
                        "p_weighted": float(np.sum(weights * (weighted[:, idx] >= references[ref][gas]))),
                        "p_prior": prior_mass, "K_vs_complement": odds_update(q, prior_mass),
                        "wilson_iid_low": lo, "wilson_iid_high": hi,
                        "tail_status": "unsampled_tail" if count in (0, len(vals)) else ("sparse_tail" if min(count, len(vals)-count) < 20 else "sampled")})

    # Rebin the pointwise posterior-median spectrum to the original LIFE grid.
    binned_path = record(root / BASE_REL / "lifesim/life_classic_binned_products.npz", expected=preserve["binned_reference_sha256"])
    binned = np.load(binned_path)
    centres = np.asarray(binned["wl_bins_um"], dtype=float)
    require(centres.shape == (31,) and np.all(np.diff(centres) > 0), "Invalid LIFE grid")
    fit_rows, bin_rows, pt_rows = [], [], []
    for scenario in SCENARIOS:
        forward_path = record(root / BASE_REL / f"forward_emission/{scenario}_emission.npz", expected=preserve[f"native_{scenario}_sha256"])
        with np.load(forward_path) as f:
            wl_truth, fp_truth = np.asarray(f["wl_um"]), np.asarray(f["Fp_obs_W_m2_m"])
        truth = LifePhotonOperator.build(wl_truth, centres).apply(fp_truth)
        truth_saved = np.asarray(binned[f"flux_binned_{scenario}"]) * (6.62607015e-34 * 2.99792458e8) / (centres * 1e-6)
        require(np.allclose(truth, truth_saved, rtol=1e-10, atol=0), f"Truth/operator closure mismatch: {scenario}")
        stem = PROFILE_STEMS[scenario]
        pt_true_path = record(root / "Transmission_Spectroscopy/profiles" / f"{stem}_PT.txt")
        pt_true = np.genfromtxt(pt_true_path, names=True)
        for hours in HOURS:
            m = models[(scenario, hours, "")]
            data = datasets[(scenario, hours)]["data"]
            require(np.allclose(data[:, 0], centres, atol=5e-6, rtol=0), f"LIFE centres mismatch: {scenario} {hours}")
            median = LifePhotonOperator.build(m["spectrum"][:, 0], centres).apply(m["spectrum"][:, 3])
            residual = (data[:, 2] - median) / data[:, 3]
            noise = (data[:, 2] - truth) / data[:, 3]
            model_offset = (truth - median) / data[:, 3]
            require(np.allclose(residual, noise + model_offset, rtol=1e-12, atol=1e-10), "Residual decomposition failed")
            top = np.argsort(np.abs(residual))[::-1][:3]
            fit_rows.append({"scenario": scenario, "hours": hours, "dataset_sha256": m["dataset_sha256"],
                "chi2_best_printed": m["result"]["chi2"], "chi2_red_best_reported": m["result"]["chi2_red_reported"],
                "chi2_red_best_effective": m["result"]["chi2"] / 17, "chi2_pointwise_median": float(np.dot(residual, residual)),
                "noise_squared": float(np.dot(noise, noise)), "model_offset_squared": float(np.dot(model_offset, model_offset)),
                "bins_abs_residual_gt3": int(np.count_nonzero(np.abs(residual) > 3)),
                "top3_wavelength_um": "; ".join(f"{centres[i]:.4f}" for i in top),
                "top3_residual_sigma": "; ".join(f"{residual[i]:+.3f}" for i in top)})
            for k, wave in enumerate(centres):
                bin_rows.append({"scenario": scenario, "hours": hours, "wavelength_um": float(wave),
                    "observed_fp": float(data[k, 2]), "sigma_fp": float(data[k, 3]), "truth_fp": float(truth[k]),
                    "pointwise_median_fp_binned": float(median[k]), "residual_observed_minus_median_sigma": float(residual[k]),
                    "noise_observed_minus_truth_sigma": float(noise[k]), "truth_minus_median_sigma": float(model_offset[k])})
            for pressure in (1.0, 0.1, 0.01, 0.001):
                x = math.log10(pressure)
                t_truth = float(np.interp(x, np.log10(pt_true["P"][::-1]), pt_true["T"][::-1]))
                t_median = float(np.interp(x, np.log10(m["pt"][:, 0][::-1]), m["pt"][:, 3][::-1]))
                pt_rows.append({"scenario": scenario, "hours": hours, "pressure_bar": pressure,
                    "truth_temperature_K": t_truth, "retrieved_median_K": t_median, "median_minus_truth_K": t_median - t_truth})

    # Updated 1000 h fixed-A0 results are exploratory: the independent audit
    # explicitly left formal acceptance pending for six fixed-moment NaNs.
    audit_path = root / RETR_REL / FIXED1000 / "validation_report_20261017.json"
    audit = load_json(audit_path, in_frozen=False)
    require(audit["primary_products_and_evidence_pass"] and not audit["accepted"] and not audit["strict_finiteness_pass"], "1000 h audit status changed")
    require(len(audit["fixed_coordinate_derived_moment_issues"]) == 6, "1000 h issue count changed")
    dataset1000 = record(root / audit["dataset_rel"], in_frozen=False, expected=audit["dataset_sha256"])
    full_folder = root / RETR_REL / FULL1000 / "products"
    full_cfg_path = root / RETR_REL / FULL1000 / "resolved_configuration.json"
    full_cfg = load_json(full_cfg_path, in_frozen=False, expected=audit["full_run"]["config_sha256"])
    require(full_cfg["dataset_sha256"] == audit["dataset_sha256"], "1000 h full dataset mismatch")
    require(sha256(root / "Thermal_Emission_Spectroscopy/scripts/life_bin_operator_diagnostic.py") == audit["operator_source_sha256"], "1000 h operator source differs from audit")
    full_op = load_json(root / RETR_REL / FULL1000 / "operator_preflight.json", in_frozen=False, expected=audit["full_run"]["operator_preflight_sha256"])
    require(full_op["status"] == "PASS" and full_op["actual_forward_model_callback_bound"] and full_op["native_grid_identical"] and full_op["dataset_sha256"] == audit["dataset_sha256"] and "sampling" in full_op["binding_scope"] and "postprocessing" in full_op["binding_scope"], "1000 h full operator or callback mismatch")
    full_product_hashes = audit["full_run"]["audit_product_sha256"]
    def audited_path(folder: Path, pattern: str, hashes: dict) -> Path:
        path = one_file(folder, pattern)
        rel = path.relative_to(root).as_posix()
        require(rel in hashes, f"No independent audit hash for {rel}")
        return record(path, in_frozen=False, expected=hashes[rel])
    full_stats = audited_path(full_folder / "MultiNest_raw", "*-stats.dat", full_product_hashes)
    z1000, ez1000 = read_stats(full_stats, in_frozen=False)
    full_result = audited_path(full_folder / "results", "*_results.txt", full_product_hashes)
    r1000 = read_result(full_result, in_frozen=False)
    full_samples = audited_path(full_folder / "samples", "*_samples.txt", full_product_hashes)
    with full_samples.open(encoding="utf-8") as f:
        h1000 = [x.strip() for x in f.readline().split("|")]
    v1000 = np.atleast_2d(np.loadtxt(full_samples, skiprows=1))
    require(h1000 == full_cfg["parameters"] and np.isfinite(v1000).all(), "Invalid 1000 h full posterior")
    full_equal = np.atleast_2d(np.loadtxt(audited_path(full_folder / "MultiNest_raw", "*-post_equal_weights.dat", full_product_hashes)))
    require(full_equal.shape == (len(v1000), len(h1000) + 1) and np.isfinite(full_equal).all() and np.allclose(v1000, full_equal[:, :len(h1000)], rtol=0, atol=1e-12), "1000 h full posterior/equal-weight mismatch")
    full_weighted = np.atleast_2d(np.loadtxt(audited_path(full_folder / "MultiNest_raw", "*-.txt", full_product_hashes)))
    require(full_weighted.shape[1] == len(h1000) + 2 and np.isfinite(full_weighted).all() and np.all(full_weighted[:, 0] >= 0) and abs(float(full_weighted[:, 0].sum()) - 1) < 1e-6, "1000 h weighted posterior invalid")
    w1000 = full_weighted[:, 0] / full_weighted[:, 0].sum()
    for gas in ("N2O", "NH3"):
        require(full_cfg["prior_types"][f"log_{gas}"] == "uniform" and full_cfg["prior_ranges"][f"log_{gas}"] == [-12, -1], "1000 h regional prior mismatch")
    fixed1000_regions = []
    for ref in ("A0", "A1"):
        i, j = h1000.index("log_N2O"), h1000.index("log_NH3")
        t1, t2 = references[ref]["N2O"], references[ref]["NH3"]
        b1, b2 = v1000[:, i] >= t1, v1000[:, j] >= t2
        w1, w2 = full_weighted[:, i+2] >= t1, full_weighted[:, j+2] >= t2
        p1, p2 = (-1-t1)/11, (-1-t2)/11
        prior = {"R11": p1*p2, "R10": p1*(1-p2), "R01": (1-p1)*p2, "R00": (1-p1)*(1-p2)}
        masks = {"R11": b1&b2, "R10": b1&~b2, "R01": ~b1&b2, "R00": ~b1&~b2}
        wmasks = {"R11": w1&w2, "R10": w1&~w2, "R01": ~w1&w2, "R00": ~w1&~w2}
        require(sum(int(mask.sum()) for mask in masks.values()) == len(v1000), "1000 h regions do not partition posterior")
        for region in REGIONS:
            count = int(masks[region].sum())
            q = count / len(v1000)
            fixed1000_regions.append({"reference": ref, "region": region, "n_equal": len(v1000), "count": count,
                "p_equal": q, "p_weighted": float(np.sum(w1000 * wmasks[region])), "p_prior": prior[region],
                "K_vs_complement": odds_update(q, prior[region]),
                "tail_status": "unsampled_tail" if count in (0, len(v1000)) else ("sparse_tail" if min(count, len(v1000)-count) < 20 else "sampled"),
                "status": "EXPLORATORY_PENDING_FIXED_MOMENT_REVIEW"})
    fixed_rows = []
    fixed_manifest = record(root / RETR_REL / FIXED1000 / "manifest.csv", in_frozen=False)
    fixed_cases = read_csv(fixed_manifest)
    require(len(fixed_cases) == 3, "1000 h fixed-A0 campaign incomplete")
    for item in fixed_cases:
        require(item["return_code"] == "0" and item["acceptance"] == "PENDING_FIXED_MOMENT_REVIEW", "1000 h acceptance differs")
        a = audit["run_audits"][item["run_id"]]
        cfg_path = root / RETR_REL / FIXED1000 / "resolved" / f"{item['variant']}.json"
        cfg = load_json(cfg_path, in_frozen=False, expected=a["config_sha256"])
        require(cfg["dataset_sha256"] == audit["dataset_sha256"] and cfg["parameters"] == full_cfg["parameters"], "1000 h paired configuration mismatch")
        fixed_species = cfg["fixed_log10_abundances"]
        expected_species = {"N2O", "NH3"} if item["variant"] == "joint" else {item["variant"]}
        require(set(fixed_species) == expected_species, "1000 h fixed species mismatch")
        for param in cfg["parameters"]:
            if param.removeprefix("log_") not in fixed_species:
                require(cfg["prior_types"][param] == full_cfg["prior_types"][param] and cfg["prior_ranges"][param] == full_cfg["prior_ranges"][param], f"1000 h prior mismatch: {param}")
        for gas, value in fixed_species.items():
            require(abs(value - references["A0"][gas]) < 1e-10, "1000 h A0 threshold mismatch")
            require(cfg["prior_ranges"][f"log_{gas}"] == [value, value], "1000 h fixed prior mismatch")
        op = load_json(root / RETR_REL / FIXED1000 / "preflight" / f"{item['variant']}_operator.json", in_frozen=False, expected=a["operator_record_sha256"])
        require(op == audit["operator_records"][item["run_id"]] and op["status"] == "PASS" and op["actual_forward_model_callback_bound"] and op["native_grid_identical"] and op["dataset_sha256"] == audit["dataset_sha256"] and op["operator_sha256"] == audit["operator_source_sha256"] and op["fixed_log10_vmr"] == fixed_species and set(op["retained_opacities"]) == expected_species and "sampling" in op["binding_scope"] and "postprocessing" in op["binding_scope"], "1000 h fixed operator or callback mismatch")
        folder = root / RETR_REL / FIXED1000 / "runs" / item["variant"] / "POSEIDON_output/proxima_b_earthlike/retrievals"
        hashes = a["product_sha256"]
        stat = audited_path(folder / "MultiNest_raw", "*-stats.dat", hashes)
        z, ez = read_stats(stat, in_frozen=False)
        result = read_result(audited_path(folder / "results", "*_results.txt", hashes), in_frozen=False)
        samples = audited_path(folder / "samples", "*_samples.txt", hashes)
        with samples.open(encoding="utf-8") as f:
            names = [x.strip() for x in f.readline().split("|")]
        values = np.atleast_2d(np.loadtxt(samples, skiprows=1))
        require(names == cfg["parameters"] and np.isfinite(values).all(), "1000 h fixed posterior invalid")
        equal = np.atleast_2d(np.loadtxt(audited_path(folder / "MultiNest_raw", "*-post_equal_weights.dat", hashes)))
        require(equal.shape == (len(values), len(names) + 1) and np.isfinite(equal).all() and np.allclose(values, equal[:, :len(names)], rtol=0, atol=1e-12), "1000 h fixed posterior/equal-weight mismatch")
        for gas, value in fixed_species.items():
            require(np.allclose(values[:, names.index(f"log_{gas}")], value, rtol=0, atol=1e-10), "1000 h fixed coordinate changed")
        saved = next(x for x in audit["rows"] if x["run_id"] == item["run_id"])
        delta, error = z1000 - z, math.hypot(ez1000, ez)
        require(abs(delta - saved["ln_B_full_minus_A0"]) < 1e-9 and abs(error - saved["ln_B_numeric_error_quadrature"]) < 1e-10, "1000 h audit comparison mismatch")
        fixed_rows.append({"variant": item["variant"], "run_id": item["run_id"], "dataset_sha256": audit["dataset_sha256"],
            "lnz_full": z1000, "lnz_full_error": ez1000, "lnz_fixed": z, "lnz_fixed_error": ez,
            "delta_lnz_full_minus_fixed": delta, "delta_error_quadrature": error,
            "chi2_full_printed": r1000["chi2"], "chi2_red_full_effective": r1000["chi2"] / 17,
            "chi2_fixed_printed": result["chi2"], "chi2_red_fixed_effective": result["chi2"] / (31 - cfg["effective_free_dimension"]),
            "n_equal": len(values), "formal_acceptance": item["acceptance"], "audit_issue_count_total": 6})

    out.mkdir(parents=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    tables = {"models.csv": model_rows, "loo.csv": loo_rows, "posterior_full_parameters.csv": posterior_rows,
              "enrichment_full_nitrogen.csv": enrichment_rows,
              "probabilities_all_models.csv": probability_rows, "regions_joint.csv": region_rows,
              "regions_summary.csv": joint_summary, "regions_marginal.csv": marginal_rows,
              "fit_summary.csv": fit_rows, "residual_bins.csv": bin_rows, "pt_probes.csv": pt_rows,
              "fixed_a0_1000h_exploratory.csv": fixed_rows, "regions_1000h_exploratory.csv": fixed1000_regions}
    for name, table in tables.items():
        write_csv(out / name, table)
    write_csv(out / "input_hashes.csv", [{"path": p, "sha256": h, "in_original_freeze": p in frozen} for p, h in sorted(inputs.items())])

    # Write a single human-readable authoritative narrative with the actual
    # recalculated quantities; CSVs provide precision and all model variants.
    lines = ["# LIFE Proxima A1/A3: análisis integrado de retrievals", "",
        f"**Fecha:** {DATE} (America/Bogota). **Estado:** análisis reproducido desde productos corregidos; 42 modelos auditados: seis completos y 36 ablaciones. La comparación A3–1000 h con A0 fija se presenta aparte y conserva su aceptación pendiente.", "",
        "## Alcance y método", "",
        "A1 representa el benchmark de Tierra actual y A3 el escenario extremo ExoFarm simulado. Cada caso usa una realización sintética LIFE de 31 canales. Los modelos completos incluyen H₂O, CO₂, CH₄, O₂, O₃, N₂O y NH₃; cada ablación retira una de las seis especies estudiadas y su parámetro. O₂ permanece activo y no tiene ablación en esta matriz.", "",
        "Los seis casos se reconstruyeron desde sus manifiestos, configuraciones, muestras y estadísticas nativas MultiNest. Se verificaron estados, retornos, hashes del inventario congelado, callback, columnas, muestras de peso igual, espectros, P–T, `log_X`, datos y priors. Cada pareja comparte escenario, exposición, dataset, operador y priors restantes. No se ejecutó ningún retrieval nuevo.", "",
        "La referencia escalar de abundancia es el promedio del perfil vertical ponderado en presión; no constituye una equivalencia radiativa demostrada para una atmósfera isoquímica. Los intervalos son cuantiles de muestras de igual peso. Se calculan también probabilidades con las muestras ponderadas nativas.", "",
        "**Límites:** un dataset/realización por caso; selección de la realización A1–1 h después de comparar dos; química isochem, P–T parametrizado y likelihood diagonal. Los valores absolutos de `ln Z` entre datasets distintos no son factores de Bayes entre A1 y A3. El umbral A1 se eligió retrospectivamente. Los valores 0%/100% indican una cola sin muestras, no probabilidades exactas.", ""]
    def loo_value(scenario: str, hours: int, gas: str) -> dict:
        return next(x for x in loo_rows if (x["scenario"], x["hours"], x["excluded_species"]) == (scenario, hours, gas))
    def regional(scenario: str, hours: int, reference: str) -> dict:
        return next(x for x in joint_summary if (x["scenario"], x["hours"], x["reference"]) == (scenario, hours, reference))
    def margin(scenario: str, hours: int, reference: str, gas: str) -> dict:
        return next(x for x in marginal_rows if (x["scenario"], x["hours"], x["reference"], x["gas"]) == (scenario, hours, reference, gas))
    a3n = [loo_value("A3", h, "N2O") for h in HOURS]
    a3a = [loo_value("A3", h, "NH3") for h in HOURS]
    a3r = [regional("A3", h, "A1") for h in HOURS]
    a3m10 = margin("A3", 10, "A1", "NH3")
    a3f100 = next(x for x in fit_rows if x["scenario"] == "A3" and x["hours"] == 100)
    lines += ["## Lectura de los resultados", "",
        f"**N₂O y NH₃ tienen comportamientos distintos.** En A3, la diferencia de evidencia al retirar N₂O es {a3n[0]['delta_lnz']:+.2f}, {a3n[1]['delta_lnz']:+.2f} y {a3n[2]['delta_lnz']:+.2f} para 1, 10 y 100 h; al retirar NH₃ es {a3a[0]['delta_lnz']:+.2f}, {a3a[1]['delta_lnz']:+.2f} y {a3a[2]['delta_lnz']:+.2f}. Son contrastes dentro de cada dataset; las incertidumbres figuran en la tabla de ablaciones. El apoyo a N₂O crece en estas realizaciones, mientras que el contraste de NH₃ solo es positivo en A3–100 h. La conclusión está condicionada al modelo y sus priors.", "",
        f"**Abundancias conjuntas.** En A3, la fracción de muestras donde N₂O y NH₃ superan ambas sus referencias A1 es {100*a3r[0]['R11']:.1f}%, {100*a3r[1]['R11']:.1f}% y {100*a3r[2]['R11']:.1f}% para 1, 10 y 100 h; las estimaciones ponderadas son {100*a3r[0]['R11_weighted']:.1f}%, {100*a3r[1]['R11_weighted']:.1f}% y {100*a3r[2]['R11_weighted']:.1f}%. Su masa previa es {100*a3r[0]['prior_R11']:.1f}%, de modo que las odds se actualizan por factores {a3r[0]['K_R11_vs_complement']:.2f}, {a3r[1]['K_R11_vs_complement']:.2f} y {a3r[2]['K_R11_vs_complement']:.1f} frente al complemento. Estos valores describen regiones de abundancia definidas después de ver los resultados, no probabilidades de que exista agricultura.", "",
        f"A3–10 h ilustra por qué hay que comparar con el prior: P(NH₃≥A1) es {100*a3m10['p_equal']:.1f}%, mientras que su probabilidad previa es {100*a3m10['p_prior']:.1f}%; el factor de actualización de odds es {a3m10['K_vs_complement']:.2f}. La probabilidad conjunta alta está impulsada principalmente por N₂O. Las colas poco pobladas y el error del muestreo requieren cautela.", "",
        f"**Calidad de ajuste.** Para A3–100 h, χ² es {a3f100['chi2_best_printed']:.2f}: el χ² reducido reportado es {a3f100['chi2_red_best_reported']:.2f} y, con 14 parámetros libres, el cociente efectivo es {a3f100['chi2_red_best_effective']:.2f}. Dos canales de la mediana puntual superan |3σ|. El desajuste justifica estudiar perfiles, ruido y modelo antes de endurecer la interpretación de las evidencias.", "",
        "## Referencias efectivas de abundancia", "", "| Gas | log₁₀ A0 | log₁₀ A1 | log₁₀ A3 |", "|---|---:|---:|---:|"]
    for gas in GASES:
        lines.append(f"| {gas} | {fmt(references['A0'][gas], 4)} | {fmt(references['A1'][gas], 4)} | {fmt(references['A3'][gas], 4)} |")
    lines += ["", "## Modelos completos y ajuste", "", "| Escenario | h | ln Z ± error numérico | χ² mejor ajuste | χ² reducido reportado | Muestras iguales |", "|---|---:|---:|---:|---:|---:|"]
    for scenario in SCENARIOS:
        for hours in HOURS:
            m = models[(scenario, hours, "")]
            lines.append(f"| {scenario} | {hours} | {m['lnz']:.3f} ± {m['lnz_error']:.3f} | {m['result']['chi2']:.2f} | {m['result']['chi2_red_reported']:.2f} | {m['n_samples']} |")
    lines += ["", "El χ² reducido reportado usa los grados de libertad impresos por POSEIDON; el CSV conserva también el cociente con 14 parámetros libres. Son diagnósticos de ajuste, no pruebas independientes de detección.", "", "## Posteriores completos: gases", "", "Cuantiles en log₁₀ de fracción de mezcla. P(≥A0/A1) es la fracción de muestras del modelo completo por encima de cada referencia escalar.", "", "| Escenario | h | Gas | q2,5 | q16 | Mediana | q84 | q97,5 | P(≥A0) | P(≥A1) |", "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|"]
    for row in posterior_rows:
        gas = row["parameter"].removeprefix("log_")
        if gas not in GASES:
            continue
        lines.append(f"| {row['scenario']} | {row['hours']} | {gas} | {fmt(row['q025'])} | {fmt(row['q16'])} | {fmt(row['median'])} | {fmt(row['q84'])} | {fmt(row['q975'])} | {pct(row['p_ge_A0'])} | {pct(row['p_ge_A1'])} |")
    lines += ["", "### Enriquecimiento respecto a A0 y A1", "", "Para cada muestra se calcula Δ = log₁₀ X − log₁₀ X_ref y el cociente X/X_ref = 10^Δ. La tabla da la mediana y el intervalo central 95% del cociente, relativos a los perfiles efectivos de referencia. Es un cociente de abundancias dentro del modelo isochem, no un cociente de flujos de superficie.", "", "| Escenario | h | Gas | X/A0: mediana [2,5%, 97,5%] | X/A1: mediana [2,5%, 97,5%] |", "|---|---:|---|---:|---:|"]
    for scenario in SCENARIOS:
        for hours in HOURS:
            for gas in ("N2O", "NH3"):
                cells = []
                for ref in ("A0", "A1"):
                    e = next(x for x in enrichment_rows if (x["scenario"], x["hours"], x["gas"], x["reference"]) == (scenario, hours, gas, ref))
                    cells.append(f"{e['factor_median']:.2g} [{e['factor_q025']:.2g}, {e['factor_q975']:.2g}]")
                lines.append(f"| {scenario} | {hours} | {gas} | " + " | ".join(cells) + " |")
    lines += ["", "El CSV de enriquecimiento incluye Δ en dex, cuantiles y probabilidades también frente a A3, tanto con pesos iguales como con pesos nativos."]
    lines += ["", "## Parámetros planetarios y térmicos", "", "Cada celda muestra mediana [q16, q84]. `log_P_surf` está fija en 0 (1 bar). Las unidades siguen las configuraciones resueltas: radio en radios terrestres, temperatura en K y presiones en log₁₀(bar).", "", "| Parámetro | A1 1 h | A1 10 h | A1 100 h | A3 1 h | A3 10 h | A3 100 h |", "|---|---:|---:|---:|---:|---:|---:|"]
    structural = ("R_p_ref", "a1", "a2", "log_P1", "log_P2", "log_P3", "T_ref", "log_P_surf")
    for name in structural:
        cells = []
        for scenario in SCENARIOS:
            for hours in HOURS:
                qrow = next(x for x in posterior_rows if (x["scenario"], x["hours"], x["parameter"]) == (scenario, hours, name))
                cells.append(f"{qrow['median']:.3f} [{qrow['q16']:.3f}, {qrow['q84']:.3f}]")
        lines.append("| " + name + " | " + " | ".join(cells) + " |")
    lines += ["", "Los cuantiles completos de los 15 parámetros están en [posterior_todos_los_parametros.csv](../" + (OUT_REL / "posterior_full_parameters.csv").as_posix() + "). La probabilidad de una especie eliminada es N/A por construcción; las variantes restantes se encuentran en [probabilidades de todos los modelos](../" + (OUT_REL / "probabilities_all_models.csv").as_posix() + ").", "", "## Ablaciones moleculares emparejadas", "", "ΔlnZ = lnZ(completo) − lnZ(sin X). El error numérico se combina en cuadratura; σ calibrada es un descriptor auxiliar, no una significancia frecuentista.", "", "| Escenario | h | Especie retirada | ΔlnZ ± error | σ auxiliar | χ²red completo / sin X |", "|---|---:|---|---:|---:|---:|"]
    for row in loo_rows:
        lines.append(f"| {row['scenario']} | {row['hours']} | {row['excluded_species']} | {row['delta_lnz']:+.3f} ± {row['delta_error_quadrature']:.3f} | {fmt(row['sigma_calibrated_auxiliary'])} | {row['chi2_red_full_reported']:.2f} / {row['chi2_red_loo_reported']:.2f} |")
    lines += ["", "Las 36 diferencias y sus incertidumbres coinciden con las auditorías previas. Los contrastes evalúan inclusión molecular dentro del modelo y del dataset de la pareja.", "", "## Regiones conjuntas N₂O/NH₃", "", "R11: ambas abundancias ≥ referencia; R10: solo N₂O; R01: solo NH₃; R00: ninguna. K compara las odds posteriores de R11 frente a su complemento con las odds previas. El prior efectivo de cada log-abundancia es uniforme en [−12, −1] y las coordenadas son independientes.", "", "| Escenario | h | Referencia | R11 | R10 | R01 | R00 | K(R11/complemento) | R11 ponderada |", "|---|---:|---|---:|---:|---:|---:|---:|---:|"]
    for row in joint_summary:
        cells = [pct(row[g], row[g+"_count"], row["n_equal"]) for g in REGIONS]
        lines.append(f"| {row['scenario']} | {row['hours']} | {row['reference']} | " + " | ".join(cells) + f" | {fmt(row['K_R11_vs_complement'])} | {100*row['R11_weighted']:.2f}% |")
    lines += ["", "Las cuatro regiones usan muestras conjuntas, no productos de probabilidades marginales. El CSV incluye conteos, estimaciones ponderadas y límites Wilson de referencia **solo bajo la hipótesis de muestras independientes**. El remuestreo de MultiNest y su incertidumbre de nested sampling no quedan cuantificados por ese intervalo ni por el ESS de concentración de pesos. Las colas con pocas o ninguna muestra permanecen sin precisión suficiente para inferencias extremas.", "", "### Probabilidades marginales y prior", "", "| Escenario | h | Referencia | Gas | P igual peso | P ponderada | P previa | K frente al complemento | Estado de cola |", "|---|---:|---|---|---:|---:|---:|---:|---|"]
    for row in marginal_rows:
        lines.append(f"| {row['scenario']} | {row['hours']} | {row['reference']} | {row['gas']} | {pct(row['p_equal'], row['count'], row['n_equal'])} | {100*row['p_weighted']:.2f}% | {100*row['p_prior']:.2f}% | {fmt(row['K_vs_complement'])} | {row['tail_status']} |")
    lines += ["", "## Residuos espectrales y perfil térmico", "", "Se aplicó el operador fotónico a la mediana puntual del espectro posterior en la rejilla original de 31 canales. Esa mediana puntual rebinada no es necesariamente el espectro del mejor vector de parámetros ni la mediana de espectros ya binados. El χ² de mejor ajuste procede del resultado POSEIDON; el otro corresponde a la mediana puntual. Los flujos y sus incertidumbres en `residual_bins.csv` son flujos espectrales observados Fp en W m⁻² m⁻¹; las longitudes de onda están en µm.", "", "| Escenario | h | χ² mejor ajuste | χ² mediana puntual | Bins con residuo absoluto > 3σ | Tres canales con mayor residuo absoluto (µm) |", "|---|---:|---:|---:|---:|---|"]
    for row in fit_rows:
        lines.append(f"| {row['scenario']} | {row['hours']} | {row['chi2_best_printed']:.2f} | {row['chi2_pointwise_median']:.2f} | {row['bins_abs_residual_gt3']} | {row['top3_wavelength_um']} |")
    lines += ["", "La separación `observado − mediana = (observado − verdad) + (verdad − mediana)` se verificó en cada bin. Los cuadrados de sus componentes incluyen un término cruzado y no se suman directamente. La prueba compara contra la verdad sintética y no establece una identificación molecular individual.", "", "### Diferencia térmica de la mediana frente al perfil de entrada", "", "Valores en K, mediana recuperada menos perfil de entrada, interpolados en presión logarítmica.", "", "| Escenario | h | 1 bar | 0,1 bar | 0,01 bar | 0,001 bar |", "|---|---:|---:|---:|---:|---:|"]
    for scenario in SCENARIOS:
        for hours in HOURS:
            probes = [x for x in pt_rows if x["scenario"] == scenario and x["hours"] == hours]
            lines.append(f"| {scenario} | {hours} | " + " | ".join(f"{x['median_minus_truth_K']:+.2f}" for x in probes) + " |")
    lines += ["", "Los residuos por canal y las temperaturas de entrada y recuperadas están en los CSV vinculados al final.", "", "## Extensión exploratoria A3–1000 h: A0 fija", "", "Los tres contrastes usan el completo corregido y la misma realización de 1000 h. El auditor anterior validó productos primarios y evidencias, pero la aceptación formal sigue pendiente por seis NaN en momentos derivados de coordenadas fijas. No se alteró ese estado. Fijar una abundancia mantiene su opacidad y compara el modelo libre con un valor escalar concreto.", "", "| Gas libre | Mediana log₁₀ X | Intervalo central 95% | P(≥A0) en muestras | P(≥A1) en muestras |", "|---|---:|---:|---:|---:|"]
    for gas in ("N2O", "NH3"):
        v = v1000[:, h1000.index(f"log_{gas}")]
        q = np.quantile(v, (0.025, 0.5, 0.975))
        ca0, ca1 = int(np.count_nonzero(v >= references["A0"][gas])), int(np.count_nonzero(v >= references["A1"][gas]))
        lines.append(f"| {gas} | {q[1]:.3f} | [{q[0]:.3f}, {q[2]:.3f}] | {pct(ca0/len(v), ca0, len(v))} | {pct(ca1/len(v), ca1, len(v))} |")
    lines += ["", "| Fijación | ΔlnZ libre − fija ± error | χ²red efectivo del completo | Estado |", "|---|---:|---:|---|"]
    for row in fixed_rows:
        lines.append(f"| {row['variant']} | {row['delta_lnz_full_minus_fixed']:+.3f} ± {row['delta_error_quadrature']:.3f} | {row['chi2_red_full_effective']:.2f} | {row['formal_acceptance']} |")
    lines += ["", "| Umbral | R11: ambas sobre el umbral | R10: solo N₂O | R01: solo NH₃ | R00: ninguna | R11 ponderada |", "|---|---:|---:|---:|---:|---:|"]
    for ref in ("A0", "A1"):
        group = {x["region"]: x for x in fixed1000_regions if x["reference"] == ref}
        cells = [pct(group[r]["p_equal"], group[r]["count"], group[r]["n_equal"]) for r in REGIONS]
        lines.append(f"| {ref} | " + " | ".join(cells) + f" | {100*group['R11']['p_weighted']:.2f}% |")
    lines += ["", "El ajuste de 1000 h es deficiente respecto al ruido supuesto. La evidencia compara modelos condicionados y no atribuye una fuente agrícola. Las tres fijaciones A0 de A3–100 h con el operador corregido no se ejecutaron; sus resultados con el operador histórico no se incorporan a esta serie.", "", "## Interpretación y siguientes comprobaciones", "", "Las ablaciones evalúan apoyo a incluir una opacidad; P(X≥A0/A1) y K regional describen abundancias dentro del modelo completo. Ninguna de estas cantidades identifica por sí sola una familia física ExoFarm frente a todas las atmósferas preagrícolas. Se recomienda examinar la sensibilidad a priors y umbrales, cuantificar incertidumbre de nested sampling, revisar el ajuste y explorar ruido/covarianza y perfiles verticales antes de fortalecer la atribución.", "", "## Referencias metodológicas", "", "- [Benneke y Seager (2013), *How to Distinguish between Cloudy Mini-Neptunes and Water/Volatile-Dominated Super-Earths*](https://doi.org/10.1088/0004-637X/778/2/153): contexto para comparación bayesiana y conversión descriptiva de evidencias; la calibración concreta aplicada aquí está en el script local.", "- [Lin et al. (2021), *Differentiating Modern and Prebiotic Earth Scenarios for TRAPPIST-1e*](https://doi.org/10.1093/mnras/stab1486): referencia histórica del tratamiento comparativo de señales moleculares; sus condiciones instrumentales y modelos no sustituyen las de esta campaña.", "- [Wogan et al. (2026), *Toward Inferring the Surface Fluxes of Biosignature Gases on Rocky Exoplanets from Telescope Spectra*](https://arxiv.org/abs/2604.21848): contexto para el problema de inferir emisiones de superficie. La comparación regional de abundancias de este informe es un análisis diferente y condicionado al prior.", "", "## Productos y trazabilidad", "", "Este es el informe vigente integrado para la serie A1/A3. Los documentos anteriores permanecen como bitácora metodológica e histórica; las tablas de esta edición son la referencia numérica de esta síntesis.", ""]
    for name in tables:
        lines.append(f"- [{name}](../{(OUT_REL / name).as_posix()})")
    lines += [f"- [Hashes de insumos](../{(OUT_REL / 'input_hashes.csv').as_posix()}) y [procedencia](../{(OUT_REL / 'provenance.json').as_posix()}).",
              f"- [Script reproducible](../{SCRIPT_REL.as_posix()}).",
              "- [Atlas oficial A1/A3](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_posteriors_N2O_NH3_first_no_PT_proxima_20261028.png).",
              "- [Bitácora y auditoría de campañas previas](life_proxima_analysis_checklist_2026-10-20.md).", ""]
    report_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    output_hashes = {p.name: sha256(p) for p in sorted(out.glob("*.csv"))}
    provenance = {"analysis_date_project_timezone": DATE, "scope": "corrected LIFE Proxima A1/A3 1,10,100h; exploratory A3 1000h fixed A0",
        "script_rel": SCRIPT_REL.as_posix(), "script_sha256": sha256(Path(__file__).resolve()),
        "frozen_manifest_rel": FROZEN_REL.as_posix(), "frozen_manifest_sha256": FROZEN_HASH,
        "python": platform.python_version(), "numpy": np.__version__,
        "primary_models": len(models), "primary_loo_pairs": len(loo_rows), "previous_audit_pairs_crosschecked": len(prior_rows),
        "fixed1000_pairs_exploratory": len(fixed_rows), "fixed1000_acceptance": "PENDING_FIXED_MOMENT_REVIEW",
        "reference_log10": references, "input_file_count": len(inputs), "inputs": inputs,
        "outputs_sha256": output_hashes, "report_sha256": sha256(report_path),
        "weighted_probability_limit": "Weight ESS measures concentration, not independent nested-sampling uncertainty.",
        "wilson_limit": "Wilson intervals assume iid Bernoulli draws and do not capture nested-sampling uncertainty.",
        "retrievals_launched": 0}
    (out / "provenance.json").write_text(json.dumps(provenance, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"models": len(models), "loo_pairs": len(loo_rows), "regional_cells": len(region_rows),
                      "residual_bins": len(bin_rows), "fixed1000_pairs": len(fixed_rows),
                      "inputs": len(inputs), "report_sha256": provenance["report_sha256"], "output": str(out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
