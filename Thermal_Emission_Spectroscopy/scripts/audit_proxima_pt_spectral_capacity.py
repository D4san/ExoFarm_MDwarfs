"""Independent integrity and arithmetic audit of the PT-only spectral fit."""

import hashlib
from importlib.metadata import version
import json
from pathlib import Path

import numpy as np

from life_bin_operator_diagnostic import LifePhotonOperator


def main():
    root = Path(__file__).resolve().parents[2]
    directory = (root / "Thermal_Emission_Spectroscopy/outputs"
                 / "life_proxima_b_earthlike_v1/diagnostics"
                 / "A3_PT_spectral_capacity_20261014")
    destination = directory / "post_execution_audit.json"
    if destination.exists():
        raise RuntimeError("Audit already exists; preserve it")
    hashes = json.loads((directory / "preserved_inputs.json").read_text())
    for path, expected in hashes.items():
        if hashlib.sha256(Path(path).read_bytes()).hexdigest() != expected:
            raise AssertionError(f"Protected input changed: {path}")
    arrays = np.load(directory / "best_control.npz")
    for key in arrays.files:
        if not np.isfinite(arrays[key]).all():
            raise AssertionError(f"Nonfinite array: {key}")
    report = json.loads((directory / "spectral_capacity.json").read_text())
    history = json.loads((directory / "optimization_history.json").read_text())
    operator = LifePhotonOperator.build(arrays["wl_um"], arrays["centres_um"])
    matched = operator.apply(arrays["best_native_Fp"])
    np.testing.assert_allclose(matched, arrays["best_binned_Fp"], rtol=1e-12, atol=0)
    scaled = (matched - arrays["target_Fp"]) / arrays["sigma_1000h"]
    np.testing.assert_allclose(scaled @ scaled,
                               report["weighted_template_squared_norm"], rtol=1e-12)
    np.testing.assert_allclose(min(row["weighted_template_squared_norm"] for row in history),
                               report["weighted_template_squared_norm"], rtol=1e-12)
    if len(history) != report["actual_forward_evaluations"]:
        raise AssertionError("Forward evaluation count differs from history")
    final = {
        "status": "PASS_DIAGNOSTIC_ONLY", "protected_sources_checked": len(hashes),
        "all_hashes_match": True, "all_arrays_finite": True,
        "operator_and_objective_recomputed": True,
        "forward_history_count_verified": len(history),
        "temperature_domain_K": [float(arrays["best_T"].min()),
                                  float(arrays["best_T"].max())],
        "optimizer_success_each_start": [row["success"] for row in report["attempts"]],
        "global_minimum_proven": False,
        "packages": {name: version(name) for name in ("numpy", "scipy", "POSEIDON")},
        "new_retrievals": 0, "noise_changed": False,
    }
    destination.write_text(json.dumps(final, indent=2, allow_nan=False) + "\n",
                           encoding="utf-8")
    print(json.dumps(final, indent=2))


if __name__ == "__main__":
    main()
