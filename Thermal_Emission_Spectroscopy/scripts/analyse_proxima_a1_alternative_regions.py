"""Conditional A1 region diagnostics from the historical A0-fixed retrievals."""

import json
import math
from pathlib import Path

import numpy as np

from analyse_proxima_a1_regions import OUT, ROOT, nominal_odds_update, sha256


def main():
    manifest_path = OUT / "manifest.json"
    references = json.loads(manifest_path.read_text())["references_log10_vmr"]
    audit_path = ROOT / (
        "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/"
        "retrievals/a0_fixed_reference_20261010/validation_report_20261011.json"
    )
    audit = json.loads(audit_path.read_text())
    rows = []
    for run, species in (
        ("A3_100h_A0_N2O", "NH3"), ("A3_100h_A0_NH3", "N2O")
    ):
        run_audit = audit["run_audits"][run]
        candidates = [
            (path, checksum)
            for path, checksum in run_audit["product_sha256"].items()
            if path.endswith("_samples.txt")
        ]
        if len(candidates) != 1:
            raise ValueError("Ambiguous sample file")
        path = Path(candidates[0][0])
        if sha256(path) != candidates[0][1]:
            raise ValueError("Sample hash differs from accepted audit")
        with path.open() as stream:
            names = [name.strip() for name in stream.readline().split("|")]
        samples = np.loadtxt(path, skiprows=1)
        if len(samples) != run_audit["posterior_samples"] or not np.isfinite(samples).all():
            raise ValueError("Invalid samples")
        fixed_species = "N2O" if species == "NH3" else "NH3"
        fixed_values = samples[:, names.index("log_" + fixed_species)]
        if np.max(np.abs(fixed_values - references["A0"][fixed_species])) > 1e-12:
            raise ValueError("Fixed coordinate does not match A0")
        delta = samples[:, names.index("log_" + species)] - references["A1"][species]
        q = float(np.mean(delta >= 0.0))
        q0 = (-1.0 - references["A1"][species]) / 11.0
        # Restricted-model evidence isolates freeing this molecule while the
        # other remains at A0. It is distinct from the region odds update.
        delta_log_z = run_audit["lnz"] - audit["run_audits"]["A3_100h_A0_joint"]["lnz"]
        rows.append({
            "run": run, "free_species": species, "fixed_species_at_a0": fixed_species,
            "p_free_species_ge_a1": q, "p_nominal_prior": q0,
            "ratio_to_a1_q025_median_q975": (10**np.quantile(delta, [.025, .5, .975])).tolist(),
            **nominal_odds_update(q, q0),
            "ln_B_free_vs_both_a0": delta_log_z,
            "B_free_vs_both_a0": math.exp(delta_log_z),
            "ln_B_numerical_error": math.hypot(
                run_audit["lnz_error"], audit["run_audits"]["A3_100h_A0_joint"]["lnz_error"]
            ),
            "samples_rel": path.relative_to(ROOT).as_posix(),
            "samples_sha256": sha256(path), "n_samples": len(samples),
        })
    output = {
        "date_local": "2026-10-15", "rows": rows,
        "source_audit_rel": audit_path.relative_to(ROOT).as_posix(),
        "source_audit_sha256": sha256(audit_path),
        "source_manifest_sha256": sha256(manifest_path),
        "script_sha256": sha256(Path(__file__)),
        "limits": "historical binning discrepancy; nominal prior; conditional sensitivity, no causal attribution",
    }
    destination = OUT / "alternative_a0_conditional.json"
    destination.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
