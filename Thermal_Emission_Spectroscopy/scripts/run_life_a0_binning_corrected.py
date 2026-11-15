"""Matched A0 constraints on A3-1000h using the validated photon operator.

The three fixed-abundance models retain molecular opacities. This separate
entrypoint preserves the frozen full-model wrapper and its archived hashes.
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

from fixed_abundance_reference import load_fixed_abundances
from life_bin_operator_diagnostic import LifePhotonOperator, bind_poseidon_binning
import run_life_retrieval as legacy
from run_life_retrieval_binning_corrected import EXPECTED_HASH, PROJECT, ROOT

VARIANTS = {"N2O": ["N2O"], "NH3": ["NH3"], "joint": ["N2O", "NH3"]}
FIXED = {"N2O": -6.884325289636784, "NH3": -9.950526295665036}


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--variant", choices=VARIANTS, required=True)
    parser.add_argument("--operator-record", type=Path, required=True)
    options, arguments = parser.parse_known_args()
    contract = argparse.ArgumentParser(add_help=False)
    for flag in ("campaign", "scenario", "hours", "n-live", "error-inflation",
                 "surface-pressure-mode", "x-profile", "R", "wl-min", "wl-max",
                 "dataset-file", "a0-reference", "run-dir"):
        contract.add_argument("--" + flag, required=True)
    contract.add_argument("--fix-a0-species", nargs="+", required=True)
    values, _ = contract.parse_known_args(arguments)
    required = {"campaign": "proxima", "scenario": "A3", "hours": "1000",
                "n_live": "800", "error_inflation": "none",
                "surface_pressure_mode": "fixed-black", "x_profile": "isochem",
                "R": "10000", "wl_min": "3.0", "wl_max": "20.0"}
    if any(getattr(values, name) != value for name, value in required.items()):
        raise ValueError("The frozen A3-1000h scientific contract changed")
    if (values.fix_a0_species != VARIANTS[options.variant]
            or "--include-o2" not in arguments
            or any(flag in arguments for flag in ("--resume", "--exclude-species",
                                                    "--vertical-gradient-species"))):
        raise ValueError("Only the selected fresh A0 constraint is authorized")
    fixed = load_fixed_abundances(values.a0_reference,
                                 VARIANTS[options.variant], ROOT)
    if fixed != {name: FIXED[name] for name in VARIANTS[options.variant]}:
        raise ValueError("Frozen effective-A0 values changed")
    dataset = ROOT / values.dataset_file
    if hashlib.sha256(dataset.read_bytes()).hexdigest() != EXPECTED_HASH:
        raise ValueError("Observed dataset checksum changed")
    implementation = Path(__file__).with_name("life_bin_operator_diagnostic.py")
    operator_hash = hashlib.sha256(implementation.read_bytes()).hexdigest()
    if "--setup-only" not in arguments:
        record = json.loads(options.operator_record.read_text())
        if (record["status"] != "PASS" or record["variant"] != options.variant
                or record["operator_sha256"] != operator_hash
                or record["fixed_log10_vmr"] != fixed):
            raise ValueError("A matching successful operator preflight is required")
    with np.load(PROJECT / "forward_emission/A3_emission.npz") as saved:
        wavelength = saved["wl_um"].copy()
        truth = saved["Fp_obs_W_m2_m"].copy()
    with np.load(PROJECT / "lifesim/life_classic_binned_products.npz") as saved:
        centres = saved["wl_bins_um"].copy()
        reference = (saved["flux_binned_A3"] * 6.62607015e-34 * 299792458.0
                     / (centres * 1e-6))
    operator = LifePhotonOperator.build(wavelength, centres)
    observed = np.loadtxt(dataset, skiprows=1)

    def validate(planet, star, model, native, pressure, target, dataset_path):
        """Test the actual bound callback on independent vertical A3 truth."""
        truth_model = legacy.ef.build_model("A3", target)
        np.testing.assert_array_equal(truth_model["chemical_species"],
                                      model["chemical_species"])
        np.testing.assert_array_equal(native, wavelength)
        temperature, chemistry = legacy.ef.load_profiles(
            truth_model, pressure, "A3", target)
        opacity = legacy.ef.read_opacities_for(truth_model, native)
        atmosphere = legacy.make_atmosphere(
            planet, truth_model, pressure, target.P_max_bar, target.planet["R_p"],
            surface_params=np.array([np.log10(target.P_max_bar)]),
            T_input=temperature, X_input=chemistry)
        candidate = legacy.compute_spectrum(
            planet, star, truth_model, atmosphere, opacity, native,
            spectrum_type="direct_emission")
        np.testing.assert_allclose(candidate, truth, rtol=1e-10, atol=0)
        data = legacy.load_data(str(dataset.parent), [dataset.name], ["LIFE"],
                                native, skiprows=1, wl_unit="micron",
                                bin_width="half", spectrum_unit="Fp")
        if retrieval.forward_model.__globals__["bin_spectrum_to_data"] != retrieval.bin_spectrum_to_data:
            raise RuntimeError("Actual likelihood callback did not bind")
        binned = retrieval.bin_spectrum_to_data(candidate, native, data)
        np.testing.assert_allclose(binned, reference, rtol=1e-10, atol=0)
        np.testing.assert_allclose(operator.apply(truth), reference,
                                   rtol=1e-12, atol=0)
        record = {
            "status": "PASS", "variant": options.variant,
            "mpi_ranks": MPI.COMM_WORLD.size,
            "actual_forward_model_callback_bound": True,
            "native_grid_identical": True, "dataset_sha256": EXPECTED_HASH,
            "operator_sha256": operator_hash, "fixed_log10_vmr": fixed,
            "retained_opacities": list(VARIANTS[options.variant]),
            "max_relative_truth_closure": float(np.max(np.abs(binned / reference - 1))),
            "truth_chi2": float(np.sum(((observed[:, 2] - binned)
                                       / observed[:, 3]) ** 2)),
            "temperature_opacity_grid_K": [180, 310, 10],
            "binding_scope": "sampling and posterior postprocessing",
            "operator": "midpoint photon overlap; exact channel-centre energy",
        }
        if MPI.COMM_WORLD.rank == 0:
            options.operator_record.write_text(json.dumps(record, indent=2) + "\n")
            print("[corrected-A0-preflight] " + json.dumps(record), flush=True)

    legacy.validate_truth_forward = validate
    sys.argv = [sys.argv[0], *arguments]
    with bind_poseidon_binning(operator) as retrieval:
        if retrieval.forward_model.__globals__["bin_spectrum_to_data"] != retrieval.bin_spectrum_to_data:
            raise RuntimeError("Likelihood binding failed")
        print(f"[operator-active] variant={options.variant} "
              f"rank={MPI.COMM_WORLD.rank} size={MPI.COMM_WORLD.size}", flush=True)
        legacy.main()
        print(f"[operator-postprocessing-complete] rank={MPI.COMM_WORLD.rank}", flush=True)


if __name__ == "__main__":
    main()
