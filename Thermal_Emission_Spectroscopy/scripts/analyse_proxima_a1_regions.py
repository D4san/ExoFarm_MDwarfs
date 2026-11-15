"""Post-process existing Proxima samples for abundance regions X >= X(A1).

Uses the historical six-case series, with its documented binning limitation.
No retrieval is launched. Odds updates use explicitly nominal, independent
log-uniform abundance priors, pending validation of the full effective prior.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from retrieval_reference import log10_column_averaged_mixing_ratio


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / (
    "Thermal_Emission_Spectroscopy/final_products/tables/"
    "life_proxima_a0_enrichment_posterior_2026-10-10.csv"
)
OUT = ROOT / (
    "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/"
    "tables/a1_regions_2026-10-15"
)
SPECIES = ("N2O", "NH3")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nominal_odds_update(q: float, q0: float) -> dict:
    """Keep unresolved empirical tails explicit; add no pseudo-counts."""
    if q == 0.0 or q == 1.0:
        return {
            "K_nominal": None,
            "ln_K_nominal": None,
            "tail_status": "complement_unsampled" if q == 1 else "region_unsampled",
        }
    value = q * (1.0 - q0) / ((1.0 - q) * q0)
    return {
        "K_nominal": value,
        "ln_K_nominal": float(np.log(value)),
        "tail_status": "both_sides_sampled",
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    references = {}
    profile_hashes = {}
    for scenario, suffix in (("A0", "PreAgri"), ("A1", "Current"), ("A3", "Extreme")):
        path = ROOT / f"Transmission_Spectroscopy/profiles/Proxima_b_{scenario}_{suffix}_chem.txt"
        profile = np.genfromtxt(path, names=True)
        references[scenario] = {
            species: log10_column_averaged_mixing_ratio(profile, species)
            for species in SPECIES
        }
        profile_hashes[path.relative_to(ROOT).as_posix()] = sha256(path)

    with SOURCE.open(encoding="utf-8") as stream:
        source_rows = list(csv.DictReader(stream))
    cases = {}
    for row in source_rows:
        key = (row["scenario"], int(row["hours"]))
        cases.setdefault(key, {})[row["species"]] = row
    if set(cases) != {(s, h) for s in ("A1", "A3") for h in (1, 10, 100)}:
        raise ValueError("Unexpected source case matrix")

    marginal, joint, inputs = [], [], []
    for scenario, hours in sorted(cases, key=lambda key: (key[1], key[0])):
        rows = cases[(scenario, hours)]
        first = rows["N2O"]
        sample_path = ROOT / first["samples_rel"]
        dataset_path = ROOT / first["dataset_rel"]
        for row in rows.values():
            for field in ("samples_rel", "samples_sha256", "dataset_rel", "dataset_sha256"):
                if row[field] != first[field]:
                    raise ValueError(f"Inconsistent species metadata: {field}")
        for path, expected in (
            (sample_path, first["samples_sha256"]),
            (dataset_path, first["dataset_sha256"]),
        ):
            if sha256(path) != expected:
                raise ValueError(f"Input hash mismatch: {path}")
        with sample_path.open(encoding="utf-8") as stream:
            names = [name.strip() for name in stream.readline().split("|")]
        samples = np.atleast_2d(np.loadtxt(sample_path, skiprows=1))
        if samples.shape[1] != len(names) or not np.isfinite(samples).all():
            raise ValueError("Invalid sample matrix")
        n_samples = len(samples)
        events, prior_masses = {}, {}
        for species in SPECIES:
            values = samples[:, names.index("log_" + species)]
            original = rows[species]
            if n_samples != int(original["n_samples"]):
                raise ValueError("Sample count changed")
            if np.count_nonzero(values > references["A0"][species]) != int(original["n_above"]):
                raise ValueError("A0 count does not reproduce the frozen summary")
            if np.any((values < -12.0) | (values > -1.0)):
                raise ValueError("Abundance outside nominal prior")
            delta = values - references["A1"][species]
            quantiles = np.quantile(delta, [0.025, 0.16, 0.5, 0.84, 0.975])
            event = delta >= 0.0
            q = float(np.mean(event))
            q0 = (-1.0 - references["A1"][species]) / 11.0
            events[species], prior_masses[species] = event, q0
            result = {
                "scenario": scenario, "hours": hours, "species": species,
                "n_samples": n_samples,
                "n_ge_a1": int(np.count_nonzero(event)),
                "n_equal_a1": int(np.count_nonzero(delta == 0.0)),
                "p_ge_a1": q, "p_ge_a1_nominal_prior": q0,
                "log10_a1_effective": references["A1"][species],
            }
            for label, value in zip(("q025", "q16", "median", "q84", "q975"), quantiles):
                result[f"delta_dex_{label}"] = float(value)
                result[f"ratio_to_a1_{label}"] = float(10.0 ** value)
            result["width95_dex"] = float(quantiles[4] - quantiles[0])
            result.update(nominal_odds_update(q, q0))
            result["samples_rel"] = first["samples_rel"]
            marginal.append(result)
        both = events["N2O"] & events["NH3"]
        either = events["N2O"] | events["NH3"]
        q_joint = float(np.mean(both))
        q0_joint = prior_masses["N2O"] * prior_masses["NH3"]
        joint.append({
            "scenario": scenario, "hours": hours, "n_samples": n_samples,
            "n_both_ge_a1": int(np.count_nonzero(both)),
            "p_both_ge_a1": q_joint,
            "p_either_ge_a1": float(np.mean(either)),
            "p_both_ge_a1_nominal_prior": q0_joint,
            **nominal_odds_update(q_joint, q0_joint),
            "samples_rel": first["samples_rel"],
        })
        inputs.append({field: first[field] for field in (
            "scenario", "hours", "samples_rel", "samples_sha256",
            "dataset_rel", "dataset_sha256", "dataset_seed",
        )})

    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUT / "marginal.csv", marginal)
    write_csv(OUT / "joint.csv", joint)
    manifest = {
        "date_local": "2026-10-15", "timezone": "America/Bogota",
        "criterion": "X >= pressure-column effective A1 reference",
        "series": "historical six-case series; generator/likelihood binning discrepancy remains",
        "interpretation": "abundance-region probability conditional on retrieval model; no causal ExoFarm probability",
        "references_log10_vmr": references,
        "profile_sha256": profile_hashes,
        "nominal_prior": "independent uniform log10(X) in [-12,-1]; full effective prior not validated",
        "source_summary": SOURCE.relative_to(ROOT).as_posix(),
        "source_summary_sha256": sha256(SOURCE),
        "inputs": inputs,
        "validation": "all input hashes matched; all frozen A0 marginal counts reproduced",
        "software": {"numpy": np.__version__},
        "script_sha256": sha256(Path(__file__)),
        "outputs_sha256": {name: sha256(OUT / name) for name in ("marginal.csv", "joint.csv")},
    }
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({"references": references, "marginal": marginal, "joint": joint}, indent=2))


if __name__ == "__main__":
    main()
