"""Fresh A3-100 h full retrieval using the LIFE photon-overlap operator.

This scope-specific adapter keeps the corrected observation operator bound to
POSEIDON's real forward-model callback for sampling and posterior export. It
does not resume a checkpoint made with the historical operator.
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
EXPECTED_HASH = "78662546181a5b74391a14b7b73ae80d879200a74db6a4bc5338e3ce7eee4705"
EXPECTED_DATASET = PROJECT / "life_data/LIFE_proxima_A3_100h.dat"
EXPECTED_TAG = "_O2_fixedBlack1bar_noxtol_BIN1_20261017"


def one_value(arguments, flag):
    positions = [index for index, item in enumerate(arguments) if item == flag]
    if len(positions) != 1 or positions[0] + 1 >= len(arguments):
        raise ValueError(f"Expected exactly one value for {flag}")
    return arguments[positions[0] + 1]


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--operator-record", type=Path, required=True)
    options, arguments = parser.parse_known_args()
    frozen = {
        "--campaign": "proxima", "--scenario": "A3", "--hours": "100",
        "--n-live": "800", "--error-inflation": "none",
        "--surface-pressure-mode": "fixed-black", "--x-profile": "isochem",
        "--output-tag": EXPECTED_TAG, "--R": "10000",
        "--wl-min": "3.0", "--wl-max": "20.0",
    }
    for flag, value in frozen.items():
        if one_value(arguments, flag) != value:
            raise ValueError(f"Frozen A3-100 h scope requires {flag} {value}")
    if arguments.count("--include-o2") != 1 or any(
        flag in arguments for flag in (
            "--resume", "--exclude-species", "--fixed-abundances-json",
            "--vertical-gradient-species", "--a0-reference", "--fix-a0-species",
        )
    ):
        raise ValueError("Only a fresh, full, O2-inclusive isochemical model is authorized")

    dataset_arg = Path(one_value(arguments, "--dataset-file"))
    dataset = dataset_arg if dataset_arg.is_absolute() else ROOT / dataset_arg
    dataset = dataset.resolve()
    if dataset != EXPECTED_DATASET.resolve():
        raise ValueError(f"Unexpected A3-100 h dataset: {dataset}")
    dataset_hash = hashlib.sha256(dataset.read_bytes()).hexdigest()
    if dataset_hash != EXPECTED_HASH:
        raise ValueError(f"Observed 100 h dataset hash changed: {dataset_hash}")

    with np.load(PROJECT / "forward_emission/A3_emission.npz") as saved:
        truth_wavelength = saved["wl_um"].copy()
        truth_flux = saved["Fp_obs_W_m2_m"].copy()
    with np.load(PROJECT / "lifesim/life_classic_binned_products.npz") as saved:
        centres = saved["wl_bins_um"].copy()
        binned_truth = (
            saved["flux_binned_A3"]
            * 6.62607015e-34 * 299792458.0 / (centres * 1e-6)
        )
    operator = LifePhotonOperator.build(truth_wavelength, centres)
    observed = np.loadtxt(dataset, skiprows=1)
    if observed.shape != (centres.size, 4):
        raise ValueError(f"Expected 31 LIFE channels × 4 columns; got {observed.shape}")
    if not np.allclose(observed[:, 0], centres, rtol=0, atol=5e-6):
        raise ValueError("A3-100 h data centres differ from the frozen LIFE channels")

    def validate(planet, star, model, native, pressure, target, dataset_path):
        """Validate the bound likelihood callback against the noiseless A3 forward."""
        if not model["surface"] or "O2" not in model["chemical_species"]:
            raise ValueError("Forward validation requires O2 and an explicit surface")
        truth_model = legacy.ef.build_model("A3", target)
        np.testing.assert_array_equal(truth_model["chemical_species"],
                                      model["chemical_species"])
        np.testing.assert_array_equal(native, truth_wavelength)
        temperature, chemistry = legacy.ef.load_profiles(
            truth_model, pressure, "A3", target
        )
        opacity = legacy.ef.read_opacities_for(truth_model, native)
        atmosphere = legacy.make_atmosphere(
            planet, truth_model, pressure, target.P_max_bar,
            target.planet["R_p"],
            surface_params=np.array([np.log10(target.P_max_bar)]),
            T_input=temperature, X_input=chemistry,
        )
        candidate = legacy.compute_spectrum(
            planet, star, truth_model, atmosphere, opacity, native,
            spectrum_type="direct_emission",
        )
        np.testing.assert_allclose(candidate, truth_flux, rtol=1e-10, atol=0)
        data = legacy.load_data(
            str(dataset_path.parent), [dataset_path.name], ["LIFE"], native,
            skiprows=1, wl_unit="micron", bin_width="half",
            spectrum_unit="Fp",
        )
        if retrieval.forward_model.__globals__["bin_spectrum_to_data"] \
                is not retrieval.bin_spectrum_to_data:
            raise RuntimeError("Actual POSEIDON likelihood callback is not bound")
        candidate_binned = retrieval.bin_spectrum_to_data(candidate, native, data)
        np.testing.assert_allclose(candidate_binned, binned_truth,
                                   rtol=1e-10, atol=0)
        np.testing.assert_allclose(operator.apply(truth_flux), binned_truth,
                                   rtol=1e-12, atol=0)
        record = {
            "status": "PASS",
            "scenario": "A3",
            "hours": 100,
            "dataset": str(dataset.relative_to(ROOT)),
            "dataset_sha256": dataset_hash,
            "channels": int(centres.size),
            "channel_centres_match": True,
            "native_grid_matches_saved_forward": True,
            "actual_forward_model_callback_bound": True,
            "sampling_and_postprocessing_binding": True,
            "maximum_relative_truth_closure": float(
                np.max(np.abs(candidate_binned / binned_truth - 1))
            ),
            "truth_chi2_against_this_100h_realization": float(
                np.sum(((observed[:, 2] - binned_truth) / observed[:, 3]) ** 2)
            ),
            "native_wavelength_range_um": [3.0, 20.0],
            "operator": "midpoint-edge photon overlap; convert to energy at exact channel centre",
            "operator_edges_um": [float(operator.edges_um[0]),
                                  float(operator.edges_um[-1])],
        }
        if MPI.COMM_WORLD.rank == 0:
            options.operator_record.parent.mkdir(parents=True, exist_ok=True)
            options.operator_record.write_text(
                json.dumps(record, indent=2) + "\n", encoding="utf-8"
            )
            print("[corrected-operator-preflight] " + json.dumps(record),
                  flush=True)

    legacy.validate_truth_forward = validate
    sys.argv = [sys.argv[0], *arguments]
    with bind_poseidon_binning(operator) as retrieval:
        if retrieval.forward_model.__globals__["bin_spectrum_to_data"] \
                is not retrieval.bin_spectrum_to_data:
            raise RuntimeError("POSEIDON likelihood binding failed")
        print(f"[operator-active] rank={MPI.COMM_WORLD.rank} "
              f"size={MPI.COMM_WORLD.size}", flush=True)
        legacy.main()
        print("[operator-postprocessing-complete] "
              f"rank={MPI.COMM_WORLD.rank}", flush=True)


if __name__ == "__main__":
    main()
