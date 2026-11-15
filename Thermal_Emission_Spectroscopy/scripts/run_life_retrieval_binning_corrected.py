"""Authorized A3-1000 h full retrieval with generator-compatible channels.

Reuse the unchanged physical runner and validated overlap operator. The binding
stays active during sampling AND posterior spectral/PT postprocessing. Never
resume an archived likelihood with a different observation operator.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS"):
    os.environ[variable] = "1"

import numpy as np
from mpi4py import MPI

from life_bin_operator_diagnostic import LifePhotonOperator, bind_poseidon_binning
import run_life_retrieval as legacy

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1"
EXPECTED_HASH = "5611c5904ef03aa02586bed15f14c0c2560ac5ae6fa9463ef420229311db75fa"


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--operator-record", type=Path, required=True)
    options, arguments = parser.parse_known_args()
    required = {"--campaign": "proxima", "--scenario": "A3", "--hours": "1000",
                "--n-live": "800", "--error-inflation": "none",
                "--surface-pressure-mode": "fixed-black", "--x-profile": "isochem",
                "--R": "10000", "--wl-min": "3.0", "--wl-max": "20.0"}
    for flag, value in required.items():
        if arguments.count(flag) != 1 or arguments[arguments.index(flag) + 1] != value:
            raise ValueError(f"Frozen scope requires {flag} {value}")
    if "--include-o2" not in arguments or any(flag in arguments for flag in
            ("--resume", "--exclude-species", "--fixed-abundances-json",
             "--vertical-gradient-species")):
        raise ValueError("Only the fresh, full, O2-inclusive isochemical model is authorized")
    dataset = ROOT / arguments[arguments.index("--dataset-file") + 1]
    if hashlib.sha256(dataset.read_bytes()).hexdigest() != EXPECTED_HASH:
        raise ValueError("Observed dataset hash changed")
    with np.load(PROJECT / "forward_emission/A3_emission.npz") as saved:
        wl = saved["wl_um"].copy()
        truth = saved["Fp_obs_W_m2_m"].copy()
    with np.load(PROJECT / "lifesim/life_classic_binned_products.npz") as saved:
        centres = saved["wl_bins_um"].copy()
        reference = saved["flux_binned_A3"] * 6.62607015e-34 * 299792458.0 / (centres * 1e-6)
    operator = LifePhotonOperator.build(wl, centres)
    observed = np.loadtxt(dataset, skiprows=1)

    def validate(planet, star, model, native, pressure, target, dataset_path):
        """Validate the actual likelihood callback against independent LIFE truth."""
        truth_model = legacy.ef.build_model("A3", target)
        np.testing.assert_array_equal(truth_model["chemical_species"], model["chemical_species"])
        np.testing.assert_array_equal(native, wl)
        temperature, chemistry = legacy.ef.load_profiles(truth_model, pressure, "A3", target)
        opacity = legacy.ef.read_opacities_for(truth_model, native)
        atmosphere = legacy.make_atmosphere(
            planet, truth_model, pressure, target.P_max_bar, target.planet["R_p"],
            surface_params=np.array([np.log10(target.P_max_bar)]),
            T_input=temperature, X_input=chemistry)
        candidate = legacy.compute_spectrum(
            planet, star, truth_model, atmosphere, opacity, native,
            spectrum_type="direct_emission")
        np.testing.assert_allclose(candidate, truth, rtol=1e-10, atol=0)
        data = legacy.load_data(str(dataset.parent), [dataset.name], ["LIFE"], native,
                                skiprows=1, wl_unit="micron", bin_width="half",
                                spectrum_unit="Fp")
        if retrieval.forward_model.__globals__["bin_spectrum_to_data"] != retrieval.bin_spectrum_to_data:
            raise RuntimeError("Actual forward-model callback did not bind")
        binned = retrieval.bin_spectrum_to_data(candidate, native, data)
        np.testing.assert_allclose(binned, reference, rtol=1e-10, atol=0)
        np.testing.assert_allclose(operator.apply(truth), reference, rtol=1e-12, atol=0)
        record = {"status": "PASS", "actual_forward_model_callback_bound": True,
                  "native_grid_identical": True, "dataset_sha256": EXPECTED_HASH,
                  "max_relative_truth_closure": float(np.max(np.abs(binned / reference - 1))),
                  "truth_chi2": float(np.sum(((observed[:, 2] - binned) / observed[:, 3]) ** 2)),
                  "temperature_opacity_grid_K": [180, 310, 10],
                  "binding_scope": "sampling and posterior postprocessing",
                  "operator": "midpoint-edge photon overlap, energy conversion at precise channel centre"}
        if MPI.COMM_WORLD.rank == 0:
            options.operator_record.write_text(json.dumps(record, indent=2) + "\n")
            print("[corrected-operator-preflight] " + json.dumps(record), flush=True)

    legacy.validate_truth_forward = validate
    sys.argv = [sys.argv[0], *arguments]
    with bind_poseidon_binning(operator) as retrieval:
        if retrieval.forward_model.__globals__["bin_spectrum_to_data"] != retrieval.bin_spectrum_to_data:
            raise RuntimeError("Likelihood binding failed")
        print(f"[operator-active] rank={MPI.COMM_WORLD.rank} size={MPI.COMM_WORLD.size}", flush=True)
        legacy.main()
        print(f"[operator-postprocessing-complete] rank={MPI.COMM_WORLD.rank}", flush=True)


if __name__ == "__main__":
    main()
