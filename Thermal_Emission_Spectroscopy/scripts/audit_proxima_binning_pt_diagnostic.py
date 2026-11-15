"""Independent post-execution integrity audit, without POSEIDON imports."""

import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import sys

import numpy as np

from life_bin_operator_diagnostic import LifePhotonOperator


def main():
    root = Path(__file__).resolve().parents[2]
    directory = (root / "Thermal_Emission_Spectroscopy/outputs"
                 / "life_proxima_b_earthlike_v1/diagnostics"
                 / "A3_binning_PT_controls_20261014")
    destination = directory / "post_execution_audit.json"
    if destination.exists():
        raise RuntimeError("Audit already exists; preserve it")
    hashes = json.loads((directory / "preserved_inputs.json").read_text())
    for path, expected in hashes.items():
        if hashlib.sha256(Path(path).read_bytes()).hexdigest() != expected:
            raise AssertionError(f"Protected source changed: {path}")
    forward = np.load(directory / "forward_controls.npz")
    thermal = np.load(directory / "thermal_inputs.npz")
    for archive in (forward, thermal):
        for key in archive.files:
            if not np.isfinite(archive[key]).all():
                raise AssertionError(f"Nonfinite array: {key}")
    operator = LifePhotonOperator.build(forward["wl_um"], forward["centres_um"])
    report = json.loads((directory / "forward_comparison.json").read_text())
    closure_errors = {}
    for name in report["comparisons"]:
        recomputed = operator.apply(forward[name + "_native_Fp"])
        np.testing.assert_allclose(recomputed, forward[name + "_binned_Fp"],
                                   rtol=1e-12, atol=0)
        relative = recomputed / forward["life_Fp"] - 1
        expected = report["comparisons"][name]["rms_relative"]
        np.testing.assert_allclose(np.sqrt(np.mean(relative ** 2)), expected,
                                   rtol=1e-10, atol=1e-13)
        closure_errors[name] = float(np.max(np.abs(
            recomputed / forward[name + "_binned_Fp"] - 1)))
    np.testing.assert_allclose(
        operator.apply(forward["archived_full_vector_native_Fp"]),
        forward["archived_full_vector_matched_Fp"], rtol=1e-12, atol=0,
    )
    surface = {
        name: float(forward[name + "_T"][0] - forward["true_T"][0])
        for name in report["comparisons"] if name != "true"
    }
    value = {
        "status": "PASS_DIAGNOSTIC_ONLY",
        "protected_sources_checked": len(hashes), "all_hashes_match": True,
        "all_exported_arrays_finite": True,
        "operator_recomputed_independently": True,
        "max_relative_recomputed_binning_error": closure_errors,
        "surface_temperature_difference_K": surface,
        "python": sys.version,
        "packages": {package: version(package)
                     for package in ("numpy", "scipy", "matplotlib", "POSEIDON")},
        "new_retrievals": 0, "noise_changed": False,
        "scientific_acceptance_of_existing_retrievals_changed": False,
    }
    destination.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n",
                           encoding="utf-8")
    print(json.dumps(value, indent=2))


if __name__ == "__main__":
    main()
