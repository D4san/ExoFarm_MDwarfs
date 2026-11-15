"""Recompute the corrected LIFE Proxima retrieval analysis from native products.

Recompute only the corrected 1/10/100 h matrix. Derived from the frozen
2026-10-29 analysis; preserves its validation and calculations. Never launches
retrievals or edits inputs. See the original script for historical provenance.
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


DATE = "2026-10-29"  # project date in America/Bogota
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
OUT_REL = Path("Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a1_a3_1_10_100h_20261114")
REPORT_REL = Path("docs/life_proxima_a1_a3_retrievals_analisis_integrado_2026-10-29.md")
SCRIPT_REL = Path("Thermal_Emission_Spectroscopy/scripts/analyse_proxima_a1_a3_corrected_integrated_20261029.py")
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


def fmt_factor(value) -> str:
    return "—" if value is None or value == "" else f"{float(value):.3g}"


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
    args = parser.parse_args()
    root = args.repo.resolve()
    out = (args.output or root / OUT_REL).resolve()
    require(not out.exists(), f"Output already exists: {out}")
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

    def abundance_probability(cfg: dict, names: list[str], values: np.ndarray,
                              weighted: np.ndarray, weights: np.ndarray,
                              gas: str, reference: str) -> dict:
        """Posterior and regional odds for a retained log-uniform coordinate."""
        name = f"log_{gas}"
        threshold = references[reference][gas]
        row = {"gas": gas, "reference": reference, "threshold_log10": threshold,
               "n_equal": len(values), "n_ge": None, "n_lt": None, "p_equal": None,
               "p_weighted": None, "prior_low_log10": None, "prior_high_log10": None,
               "p_prior": None, "K_equal_vs_complement": None, "K_weighted_vs_complement": None,
               "wilson_iid_low": None, "wilson_iid_high": None, "status": "species_excluded"}
        if name not in names:
            return row
        require(cfg["prior_types"].get(name) == "uniform", f"Non-uniform prior: {name}")
        bounds = cfg["prior_ranges"].get(name)
        require(len(bounds) == 2 and all(math.isfinite(float(x)) for x in bounds), f"Invalid prior: {name}")
        low, high = map(float, bounds)
        require(low <= high, f"Reversed prior: {name}")
        i = names.index(name)
        row["prior_low_log10"], row["prior_high_log10"] = low, high
        if low == high:
            require(np.allclose(values[:, i], low, rtol=0, atol=1e-10) and np.allclose(weighted[:, i], low, rtol=0, atol=1e-10), f"Fixed coordinate mismatch: {name}")
            # A0 is independently recomputed from the profile and may differ
            # from the resolved fixed value by floating-point roundoff.
            above = low > threshold or abs(low - threshold) <= 1e-10
            count = len(values) if above else 0
            row.update(n_ge=count, n_lt=len(values)-count, p_equal=float(above),
                       p_weighted=float(above), p_prior=float(above), status="fixed_zero_width_prior")
            return row
        count = int(np.count_nonzero(values[:, i] >= threshold))
        q = count / len(values)
        qw = float(np.clip(np.sum(weights * (weighted[:, i] >= threshold)), 0, 1))
        q0 = float(np.clip((high - threshold) / (high - low), 0, 1))
        ilo, ihi = wilson_reference(count, len(values))
        status = "threshold_outside_prior" if q0 in (0, 1) else ("unsampled_tail" if count in (0, len(values)) else ("sparse_tail" if min(count, len(values)-count) < 20 else "sampled"))
        row.update(n_ge=count, n_lt=len(values)-count, p_equal=q, p_weighted=qw, p_prior=q0,
                   K_equal_vs_complement=odds_update(q, q0), K_weighted_vs_complement=odds_update(qw, q0),
                   wilson_iid_low=ilo, wilson_iid_high=ihi, status=status)
        return row

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
        for gas in GASES:
            for reference in ("A0", "A1", "A3"):
                row = abundance_probability(cfg, names, values, weighted, weights, gas, reference)
                probability_rows.append({"scenario": key[0], "hours": key[1], "excluded_species": key[2] or "none", **row})
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
                    "log10_bayes_factor_full_vs_without": delta / math.log(10),
                    "log10_bayes_factor_error_quadrature": error / math.log(10),
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
            for ref in ("A0", "A1", "A3"):
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

    # Write only the primary matrix, keeping historical analysis untouched.
    out.mkdir(parents=True)
    tables = {"models.csv": model_rows, "loo.csv": loo_rows,
              "posterior_full_parameters.csv": posterior_rows,
              "enrichment_full_nitrogen.csv": enrichment_rows,
              "probabilities_all_models.csv": probability_rows,
              "regions_joint.csv": region_rows, "regions_summary.csv": joint_summary,
              "regions_marginal.csv": marginal_rows, "fit_summary.csv": fit_rows,
              "residual_bins.csv": bin_rows, "pt_probes.csv": pt_rows}
    for name, rows in tables.items():
        write_csv(out / name, rows)
    write_csv(out / "input_hashes.csv", [
        {"path": path, "sha256": digest, "in_original_freeze": path in frozen}
        for path, digest in sorted(inputs.items())
    ])
    provenance = {
        "scope": "corrected LIFE Proxima A1/A3, 1/10/100 h",
        "source_script": "Thermal_Emission_Spectroscopy/scripts/analyse_proxima_a1_a3_corrected_integrated_20261029.py",
        "script_sha256": sha256(Path(__file__).resolve()),
        "frozen_manifest_sha256": FROZEN_HASH,
        "python": platform.python_version(), "numpy": np.__version__,
        "models": len(models), "loo_pairs": len(loo_rows),
        "previous_audit_pairs_crosschecked": len(prior_rows),
        "inputs": inputs, "outputs_sha256": {name: sha256(out / name) for name in tables},
        "retrievals_launched": 0,
    }
    (out / "provenance.json").write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({"models": len(models), "loo_pairs": len(loo_rows),
                      "inputs": len(inputs), "output": str(out)}))


if __name__ == "__main__":
    main()
