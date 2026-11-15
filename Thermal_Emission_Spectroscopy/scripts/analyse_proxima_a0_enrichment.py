"""Quantify posterior enrichment above the fixed pressure-column A0 reference.

Uses the six official full-model equal-weight posterior exports, not the LOO
posteriors. Event probabilities are empirical posterior masses, never converted
to Gaussian detection sigma. The reference is a scalar diagnostic, not the
entire pre-agricultural atmosphere or an inferred agricultural emission flux.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from retrieval_reference import column_averaged_mixing_ratio
from run_proxima_molecule_ablation_campaign import DATASETS, PROJECT_REL, RESULTS_REL


SPECIES = ("N2O", "NH3")
ANALYSIS_REL = PROJECT_REL / "retrievals" / "a0_fixed_reference_20261010"
PROFILE_REL = Path("Transmission_Spectroscopy/profiles/Proxima_b_A0_PreAgri_chem.txt")
OUTPUT_REL = Path("Thermal_Emission_Spectroscopy/final_products/tables")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_math() -> None:
    profile = np.array([(1.0, 2.0), (2.0, 4.0), (3.0, 6.0)],
                       dtype=[("PRESS", float), ("N2O", float)])
    np.testing.assert_allclose(column_averaged_mixing_ratio(profile, "N2O"), 4.0)
    delta = np.array([-1.0, 0.0, 1.0, 2.0])
    assert np.mean(delta > 0) == 0.5
    assert np.mean(delta >= 0) == 0.75
    assert np.mean(np.column_stack((delta > 0, delta > 1)).all(axis=1)) == 0.25
    np.testing.assert_allclose(np.log10(10.0 ** delta), delta)


def analyse(root: Path) -> tuple[list[dict], list[dict], dict]:
    profile_path = root / PROFILE_REL
    profile = np.genfromtxt(profile_path, names=True)
    refs = {x: column_averaged_mixing_ratio(profile, x) for x in SPECIES}
    reference = {
        "definition": "integral X(p) dp / (p_bottom - p_top); atlas convention",
        "profile_rel": PROFILE_REL.as_posix(),
        "profile_sha256": digest(profile_path),
        "pressure_min_bar": float(np.min(profile["PRESS"])),
        "pressure_max_bar": float(np.max(profile["PRESS"])),
        "vmr": refs,
        "log10_vmr": {x: float(np.log10(refs[x])) for x in SPECIES},
        "reference_uncertainty": "fixed; not marginalized",
        "prior_log10_vmr_nominal": [-12.0, -1.0],
    }
    rows, joint_rows = [], []
    for scenario in ("A1", "A3"):
        for hours in (1, 10, 100):
            source = DATASETS[scenario, hours]
            dataset_path = root / PROJECT_REL / "life_data" / source["file"]
            if digest(dataset_path) != source["sha256"]:
                raise ValueError(f"Dataset changed: {dataset_path}")
            stem = source["full_results"].removesuffix("_results.txt")
            sample_path = root / RESULTS_REL.parent / "samples" / f"{stem}_samples.txt"
            with sample_path.open(encoding="utf-8") as stream:
                names = [x.strip() for x in stream.readline().split("|")]
            samples = np.atleast_2d(np.loadtxt(sample_path, skiprows=1))
            if samples.shape[1] != len(names) or len(names) != 15:
                raise ValueError(f"Unexpected parameter header: {sample_path}")
            if not np.isfinite(samples).all():
                raise ValueError(f"Nonfinite posterior: {sample_path}")
            events = {}
            for species in SPECIES:
                values = samples[:, names.index("log_" + species)]
                if np.min(values) < -12.000001 or np.max(values) > -0.999999:
                    raise ValueError(f"Samples outside recorded prior: {sample_path}")
                log_ref = reference["log10_vmr"][species]
                delta = values - log_ref
                q025, q16, q50, q84, q975 = np.quantile(
                    delta, [0.025, 0.16, 0.5, 0.84, 0.975]
                )
                above = delta > 0.0
                events[species] = above
                p_prior = float(np.clip((-1.0 - log_ref) / 11.0, 0.0, 1.0))
                row = {
                    "scenario": scenario, "hours": hours, "species": species,
                    "log10_a0_effective": log_ref,
                    "delta_log10_q025": float(q025),
                    "delta_log10_q16": float(q16),
                    "delta_log10_median": float(q50),
                    "delta_log10_q84": float(q84),
                    "delta_log10_q975": float(q975),
                    "enrichment_factor_q025": float(10.0 ** q025),
                    "enrichment_factor_median": float(10.0 ** q50),
                    "enrichment_factor_q975": float(10.0 ** q975),
                    "p_above_a0_empirical": float(np.mean(above)),
                    "n_above": int(np.sum(above)),
                    "n_at_or_below": int(np.sum(~above)),
                    "n_samples": int(len(values)),
                    "empirical_resolution_1_over_n": 1.0 / len(values),
                    "p_above_a0_nominal_prior": p_prior,
                    "posterior_minus_nominal_prior_mass": float(np.mean(above)) - p_prior,
                    "tail_status": "no_draws_below" if above.all() else (
                        "no_draws_above" if not above.any() else "both_sides_sampled"
                    ),
                    "z_descriptive": float(q50 / (0.5 * (q84 - q16))),
                    "dataset_rel": dataset_path.relative_to(root).as_posix(),
                    "dataset_seed": source["seed"],
                    "dataset_sha256": source["sha256"],
                    "samples_rel": sample_path.relative_to(root).as_posix(),
                    "samples_sha256": digest(sample_path),
                }
                rows.append(row)
            both = events["N2O"] & events["NH3"]
            either = events["N2O"] | events["NH3"]
            joint_rows.append({
                "scenario": scenario, "hours": hours,
                "p_both_above_a0_empirical": float(np.mean(both)),
                "p_either_above_a0_empirical": float(np.mean(either)),
                "n_both_above": int(np.sum(both)),
                "n_either_above": int(np.sum(either)),
                "n_samples": int(len(samples)),
                "samples_rel": sample_path.relative_to(root).as_posix(),
                "note": "paired draws preserve posterior molecular dependence",
            })
    return rows, joint_rows, reference


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.repo.resolve()
    check_math()
    rows, joint_rows, reference = analyse(root)
    analysis_dir = root / ANALYSIS_REL
    analysis_dir.mkdir(parents=True, exist_ok=True)
    reference_path = analysis_dir / "a0_reference.json"
    if reference_path.exists():
        if json.loads(reference_path.read_text(encoding="utf-8")) != reference:
            raise ValueError("Frozen A0 reference changed; do not overwrite campaign inputs")
    else:
        reference_path.write_text(json.dumps(reference, indent=2) + "\n", encoding="utf-8")
    output = root / OUTPUT_REL
    output.mkdir(parents=True, exist_ok=True)
    csv_path = output / "life_proxima_a0_enrichment_posterior_2026-10-10.csv"
    write_csv(csv_path, rows)
    write_csv(output / "life_proxima_a0_enrichment_joint_2026-10-10.csv", joint_rows)
    report = {
        "marginal_rows": len(rows), "joint_rows": len(joint_rows),
        "math_controls": "PASS", "finite_samples": "PASS",
        "six_dataset_checksums": "PASS", "reference": reference,
        "sampling": "POSEIDON equal-weight posterior exports",
        "zero_tail_warning": "zero observed draws does not imply zero tail probability",
        "nominal_prior_warning": "uniform scalar prior; not probability of an agricultural scenario",
        "new_retrievals_executed": 0,
    }
    csv_path.with_suffix(".validation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(reference, indent=2))
    for row in rows:
        print(f"{row['scenario']} {row['hours']:3}h {row['species']}: "
              f"delta={row['delta_log10_median']:+.3f} "
              f"[{row['delta_log10_q025']:+.3f}, {row['delta_log10_q975']:+.3f}], "
              f"P_above={row['p_above_a0_empirical']:.6f}, "
              f"below={row['n_at_or_below']}/{row['n_samples']}, "
              f"P_prior={row['p_above_a0_nominal_prior']:.3f}")
    print(f"PASS: {len(rows)} marginal and {len(joint_rows)} joint summaries")


if __name__ == "__main__":
    main()
