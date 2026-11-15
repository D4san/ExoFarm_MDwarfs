"""Recompute A1 abundance regions for the corrected A3 LIFE posteriors.

This is post-processing only. It validates the audited posterior products,
resolved priors, and effective A1 thresholds before writing regional tables.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1"
OUT = BASE / "tables/a1_regions_corrected_20261026"
REFERENCE_SUMMARY = BASE / "tables/a3_100h_corrected_update_20261020/summary.json"
SHORT_CAMPAIGN = BASE / "retrievals/a3_1_10h_binning_corrected_loo_20261020_r03"
LONG_CAMPAIGN = BASE / "retrievals/a3_100h_binning_corrected_mpi14_resume_20261018"
A3_INPUTS = {
    1: {
        "samples": SHORT_CAMPAIGN / "runs/A3_1h_full/POSEIDON_output/proxima_b_earthlike/retrievals/samples/proxima_A3_1h_O2_fixedBlack1bar_noxtol_BIN1_20261020_1h_full_samples.txt",
        "config": SHORT_CAMPAIGN / "resolved/A3_1h_full.json",
        "sha256": "ca150f785bef10db0b5f924565efbd88dfd43ae9ef8da67138817744666fd405",
        "rows": 6026,
    },
    10: {
        "samples": SHORT_CAMPAIGN / "runs/A3_10h_full/POSEIDON_output/proxima_b_earthlike/retrievals/samples/proxima_A3_10h_O2_fixedBlack1bar_noxtol_BIN1_20261020_10h_full_samples.txt",
        "config": SHORT_CAMPAIGN / "resolved/A3_10h_full.json",
        "sha256": "13101314d3b0449cb8cde10f241bf71919412b9bc484e467668323ad0a9a8616",
        "rows": 7036,
    },
    100: {
        "samples": LONG_CAMPAIGN / "products/samples/proxima_A3_100h_O2_fixedBlack1bar_noxtol_BIN1_20261017_samples.txt",
        "config": LONG_CAMPAIGN / "resolved_configuration.json",
        "sha256": "d56084124109efc11c478e7389b4bcf7b6e488b1bd9f86a3a215376d1c748baf",
        "rows": 7268,
    },
}

REGIONS = ("R11", "R10", "R01", "R00")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write an empty table: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def k_region(q: float, q0: float) -> float | None:
    if q in (0.0, 1.0):
        return None
    return q * (1.0 - q0) / ((1.0 - q) * q0)


def main() -> None:
    references = read_json(REFERENCE_SUMMARY)["references_log10_effective"]["A1"]
    thresholds = {"N2O": float(references["N2O"]), "NH3": float(references["NH3"])}
    prior_cells = {"R11": 0.0, "R10": 0.0, "R01": 0.0, "R00": 0.0}
    posterior_rows: list[dict] = []
    marginal_rows: list[dict] = []
    provenance = {
        "analysis_date": "2026-10-26",
        "thresholds_log10_A1": thresholds,
        "prior_model": {},
        "posterior_inputs": {},
        "results": {},
        "uncertainty": "Equal-weight sample fractions; no independent Monte Carlo error estimate is applied.",
    }

    reference_hash = sha256(REFERENCE_SUMMARY)
    for hours, item in A3_INPUTS.items():
        config = read_json(item["config"])
        posterior_path = item["samples"]
        actual_hash = sha256(posterior_path)
        if actual_hash != item["sha256"]:
            raise ValueError(f"Posterior SHA-256 mismatch for A3 {hours} h")
        if config.get("effective_free_dimension") != 14:
            raise ValueError(f"Unexpected free dimension for A3 {hours} h")
        if config.get("fixed_log10_abundances") != {}:
            raise ValueError(f"Unexpected fixed abundance in A3 {hours} h")
        for species in ("N2O", "NH3"):
            parameter = f"log_{species}"
            if parameter not in config["parameters"]:
                raise ValueError(f"Missing free parameter {parameter} in A3 {hours} h")
            if config["prior_types"].get(parameter) != "uniform":
                raise ValueError(f"Non-uniform prior for {parameter} in A3 {hours} h")
            bounds = config["prior_ranges"].get(parameter)
            if bounds != [-12, -1]:
                raise ValueError(f"Unexpected prior range for {parameter}: {bounds}")

        names = [field.strip() for field in posterior_path.open(encoding="utf-8").readline().split("|")]
        values = np.atleast_2d(np.loadtxt(posterior_path, skiprows=1))
        if values.shape != (item["rows"], len(names)) or not np.isfinite(values).all():
            raise ValueError(f"Unexpected shape or non-finite posterior in A3 {hours} h")
        i_n2o, i_nh3 = names.index("log_N2O"), names.index("log_NH3")
        high_n2o = values[:, i_n2o] >= thresholds["N2O"]
        high_nh3 = values[:, i_nh3] >= thresholds["NH3"]
        posterior_masks = {
            "R11": high_n2o & high_nh3,
            "R10": high_n2o & ~high_nh3,
            "R01": ~high_n2o & high_nh3,
            "R00": ~high_n2o & ~high_nh3,
        }
        masses = {
            species: (-1.0 - thresholds[species]) / 11.0
            for species in ("N2O", "NH3")
        }
        prior = {
            "R11": masses["N2O"] * masses["NH3"],
            "R10": masses["N2O"] * (1.0 - masses["NH3"]),
            "R01": (1.0 - masses["N2O"]) * masses["NH3"],
            "R00": (1.0 - masses["N2O"]) * (1.0 - masses["NH3"]),
        }
        if not np.isclose(sum(prior.values()), 1.0, rtol=0.0, atol=1e-12):
            raise ValueError("Analytic prior cell masses do not sum to one")
        prior_cells = prior
        n = len(values)
        counts = {region: int(mask.sum()) for region, mask in posterior_masks.items()}
        q = {region: counts[region] / n for region in REGIONS}
        cell_factors = {region: k_region(q[region], prior[region]) for region in REGIONS}
        conditional_k_11_10 = None
        if counts["R11"] and counts["R10"]:
            conditional_k_11_10 = (q["R11"] / q["R10"]) / (prior["R11"] / prior["R10"])

        for region in REGIONS:
            posterior_rows.append({
                "scenario": "A3", "hours": hours, "region": region,
                "n_samples": n, "n_region": counts[region],
                "p_posterior": q[region], "p_prior": prior[region],
                "K_region_vs_complement": cell_factors[region],
                "tail_status": "unsampled" if counts[region] == 0 else ("sparse" if counts[region] < 20 else "sampled"),
            })
        for label, mask, q0 in (
            ("N2O", high_n2o, masses["N2O"]),
            ("NH3", high_nh3, masses["NH3"]),
            ("both", posterior_masks["R11"], prior["R11"]),
            ("either", high_n2o | high_nh3, 1.0 - prior["R00"]),
        ):
            count = int(mask.sum())
            probability = count / n
            marginal_rows.append({
                "scenario": "A3", "hours": hours, "region": label,
                "n_samples": n, "n_ge_A1": count, "p_posterior": probability,
                "p_prior": q0, "K_region_vs_complement": k_region(probability, q0),
                "tail_status": "unsampled_complement" if probability == 1.0 else "sampled",
            })
        provenance["posterior_inputs"][str(hours)] = {
            "path": posterior_path.relative_to(ROOT).as_posix(),
            "sha256": actual_hash, "n_samples": n,
            "config_path": item["config"].relative_to(ROOT).as_posix(),
            "config_sha256": sha256(item["config"]),
            "prior_types": {species: config["prior_types"][f"log_{species}"] for species in ("N2O", "NH3")},
            "prior_ranges": {species: config["prior_ranges"][f"log_{species}"] for species in ("N2O", "NH3")},
        }
        provenance["results"][str(hours)] = {
            "posterior_counts": counts, "posterior_masses": q, "prior_masses": prior,
            "K_R11_vs_complement": cell_factors["R11"],
            "K_R11_vs_R10": conditional_k_11_10,
        }

    provenance["prior_model"] = {
        "reference_summary": REFERENCE_SUMMARY.relative_to(ROOT).as_posix(),
        "reference_summary_sha256": reference_hash,
        "log10_bounds": [-12, -1],
        "independent_coordinates": ["log_N2O", "log_NH3"],
        "marginal_masses": {
            "N2O_ge_A1": (-1.0 - thresholds["N2O"]) / 11.0,
            "NH3_ge_A1": (-1.0 - thresholds["NH3"]) / 11.0,
        },
        "joint_cells": prior_cells,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUT / "joint_cells.csv", posterior_rows)
    write_csv(OUT / "marginal_regions.csv", marginal_rows)
    (OUT / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
