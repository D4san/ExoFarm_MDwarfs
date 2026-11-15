"""Scope-locked corrected-bin runner for the A3 100 h NH3/N2O ablations.

The wrapper keeps the generator-compatible photon-overlap operator bound to
POSEIDON's real likelihood callback during sampling and posterior
postprocessing. Only the two authorized one-species-absent cases are accepted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"

import numpy as np
from mpi4py import MPI

from life_bin_operator_diagnostic import LifePhotonOperator, bind_poseidon_binning
import run_life_retrieval as legacy


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1"
CAMPAIGN = ROOT / (
    "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/"
    "retrievals/a3_100h_binning_corrected_loo_20261019"
)
DATASET = PROJECT / "life_data/LIFE_proxima_A3_100h.dat"
DATASET_SHA256 = "78662546181a5b74391a14b7b73ae80d879200a74db6a4bc5338e3ce7eee4705"
FULL_CAMPAIGN = ROOT / (
    "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/"
    "retrievals/a3_100h_binning_corrected_mpi14_resume_20261018"
)
FULL_CONFIG = FULL_CAMPAIGN / "resolved_configuration.json"
RANKS = {"NH3": 8, "N2O": 7}
TAGS = {
    "NH3": "_O2_fixedBlack1bar_noxtol_BIN1_20261019_noNH3",
    "N2O": "_O2_fixedBlack1bar_noxtol_BIN1_20261019_noN2O",
}


def _one_value(arguments: list[str], flag: str) -> str:
    positions = [index for index, value in enumerate(arguments) if value == flag]
    if len(positions) != 1 or positions[0] + 1 >= len(arguments):
        raise ValueError(f"Expected exactly one value for {flag}")
    return arguments[positions[0] + 1]


def _check_scope(arguments: list[str]) -> tuple[str, Path, Path, bool]:
    required = {
        "--campaign": "proxima",
        "--scenario": "A3",
        "--hours": "100",
        "--n-live": "800",
        "--error-inflation": "none",
        "--surface-pressure-mode": "fixed-black",
        "--x-profile": "isochem",
        "--R": "10000",
        "--wl-min": "3.0",
        "--wl-max": "20.0",
    }
    for flag, expected in required.items():
        if _one_value(arguments, flag) != expected:
            raise ValueError(f"Frozen A3-100 h scope requires {flag} {expected}")

    if arguments.count("--include-o2") != 1:
        raise ValueError("The corrected A3-100 h ablations must retain O2")
    excluded = _one_value(arguments, "--exclude-species")
    if excluded not in RANKS or arguments.count("--exclude-species") != 1:
        raise ValueError("Only one of the authorized NH3/N2O exclusions is allowed")
    forbidden = (
        "--resume", "--validate-forward", "--fixed-abundances-json",
        "--vertical-gradient-species", "--a0-reference", "--fix-a0-species",
    )
    if any(flag in arguments for flag in forbidden):
        raise ValueError("Resume, fixed-A0 and alternate-profile modes are forbidden")
    if _one_value(arguments, "--output-tag") != TAGS[excluded]:
        raise ValueError("Output tag does not match the frozen ablation identity")

    dataset_arg = Path(_one_value(arguments, "--dataset-file"))
    dataset = (dataset_arg if dataset_arg.is_absolute() else ROOT / dataset_arg).resolve()
    if dataset != DATASET.resolve():
        raise ValueError(f"Unexpected dataset path: {dataset}")
    digest = hashlib.sha256(dataset.read_bytes()).hexdigest()
    if digest != DATASET_SHA256:
        raise ValueError(f"A3-100 h dataset hash mismatch: {digest}")

    run_dir = Path(_one_value(arguments, "--run-dir"))
    if not run_dir.is_absolute():
        raise ValueError("--run-dir must be an absolute isolated Linux path")
    config_path = Path(_one_value(arguments, "--configuration-json")).resolve()
    expected_config = (CAMPAIGN / "resolved" / f"A3_100h_no_{excluded}.json").resolve()
    if config_path != expected_config:
        raise ValueError(f"Unexpected resolved-configuration path: {config_path}")
    setup_only = arguments.count("--setup-only") == 1
    if arguments.count("--setup-only") > 1:
        raise ValueError("Duplicate --setup-only flag")
    return excluded, run_dir, config_path, setup_only


def _validate_operator(dataset: Path, operator_record: Path) -> tuple[LifePhotonOperator, object]:
    with np.load(PROJECT / "forward_emission/A3_emission.npz") as saved:
        native = np.asarray(saved["wl_um"], dtype=np.float64).copy()
        truth_flux = np.asarray(saved["Fp_obs_W_m2_m"], dtype=np.float64).copy()
    with np.load(PROJECT / "lifesim/life_classic_binned_products.npz") as saved:
        centres = np.asarray(saved["wl_bins_um"], dtype=np.float64).copy()
        truth_binned = (
            np.asarray(saved["flux_binned_A3"], dtype=np.float64).copy()
            * 6.62607015e-34 * 299792458.0 / (centres * 1e-6)
        )

    observed = np.loadtxt(dataset, skiprows=1)
    if observed.shape != (centres.size, 4) or centres.size != 31:
        raise ValueError(f"Expected the frozen 31-channel LIFE dataset; got {observed.shape}")
    if not np.allclose(observed[:, 0], centres, rtol=0, atol=5e-6):
        raise ValueError("Observed wavelength centres differ from the frozen LIFE bins")

    operator = LifePhotonOperator.build(native, centres)
    np.testing.assert_allclose(operator.apply(truth_flux), truth_binned,
                               rtol=1e-12, atol=0)
    record = {
        "status": "PASS",
        "scenario": "A3",
        "hours": 100,
        "excluded_species": None,
        "dataset_sha256": DATASET_SHA256,
        "channels": int(centres.size),
        "native_grid_um": [float(native[0]), float(native[-1])],
        "operator": "midpoint-edge photon overlap; energy conversion at exact channel centre",
        "max_relative_truth_closure": float(
            np.max(np.abs(operator.apply(truth_flux) / truth_binned - 1.0))
        ),
        "mpi_rank_pids": [int(pid) for pid in MPI.COMM_WORLD.allgather(os.getpid())],
        "mpi_size": int(MPI.COMM_WORLD.size),
        "binding_scope": "sampling and posterior postprocessing",
    }

    with bind_poseidon_binning(operator) as retrieval:
        if retrieval.forward_model.__globals__["bin_spectrum_to_data"] is not retrieval.bin_spectrum_to_data:
            raise RuntimeError("POSEIDON's likelihood is not bound to the corrected operator")
        data = legacy.load_data(
            str(dataset.parent), [dataset.name], ["LIFE"], native,
            skiprows=1, wl_unit="micron", bin_width="half", spectrum_unit="Fp",
        )
        callback_binned = retrieval.bin_spectrum_to_data(truth_flux, native, data)
        np.testing.assert_allclose(callback_binned, truth_binned, rtol=1e-10, atol=0)
        record["actual_poseidon_callback_bound"] = True
        record["callback_truth_closure_max_relative"] = float(
            np.max(np.abs(callback_binned / truth_binned - 1.0))
        )

    if MPI.COMM_WORLD.rank == 0:
        record["excluded_species"] = _one_value(sys.argv[1:], "--exclude-species")
        record["stage"] = "setup_only" if "--setup-only" in sys.argv else "sampling"
        operator_record.parent.mkdir(parents=True, exist_ok=True)
        with operator_record.open("x", encoding="utf-8") as stream:
            json.dump(record, stream, indent=2)
            stream.write("\n")
    return operator, record


def _validate_resolved_config(path: Path, excluded: str) -> None:
    if not path.is_file():
        raise ValueError(f"Resolved configuration was not written: {path}")
    actual = json.loads(path.read_text(encoding="utf-8"))
    full = json.loads(FULL_CONFIG.read_text(encoding="utf-8"))
    expected_parameters = [name for name in full["parameters"] if name != f"log_{excluded}"]
    if actual["parameters"] != expected_parameters:
        raise ValueError("Ablation parameters differ from the matched full model")
    if actual["declared_dimension"] != 14 or actual["effective_free_dimension"] != 13:
        raise ValueError("Each ablation must have 14 declared and 13 free parameters")
    if f"log_{excluded}" in actual["parameters"]:
        raise ValueError(f"Excluded parameter log_{excluded} remains active")
    if actual["param_species"] != [name for name in full["param_species"] if name != excluded]:
        raise ValueError("Ablation opacity species do not match the requested exclusion")
    if actual["dataset_sha256"] != DATASET_SHA256:
        raise ValueError("Resolved ablation configuration has a different dataset")
    for key in ("R", "wl_min", "wl_max", "n_live", "ev_tol",
                "surface_pressure_mode", "error_inflation", "x_profile", "likelihood"):
        if actual[key] != full[key]:
            raise ValueError(f"Matched full-model setting changed: {key}")
    if actual["fixed_log10_abundances"] != {}:
        raise ValueError("Molecular-ablation runs must not fix an abundance")
    if actual["fixed_parameters"] != full["fixed_parameters"]:
        raise ValueError("Fixed surface parameter differs from the complete model")
    for section in ("prior_types", "prior_ranges"):
        for name in expected_parameters:
            if actual[section].get(name) != full[section].get(name):
                raise ValueError(f"Shared prior changed for {name}")
        if f"log_{excluded}" in actual[section]:
            raise ValueError(f"Excluded prior for log_{excluded} remains active")


def main() -> None:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--operator-record", type=Path, required=True)
    options, arguments = parser.parse_known_args()
    excluded, _, config_path, setup_only = _check_scope(arguments)
    expected_ranks = RANKS[excluded]
    if MPI.COMM_WORLD.size != expected_ranks:
        raise RuntimeError(
            f"Expected {expected_ranks} MPI ranks for no-{excluded}; "
            f"found {MPI.COMM_WORLD.size}"
        )

    operator, _ = _validate_operator(DATASET, options.operator_record.resolve())
    sys.argv = [sys.argv[0], *arguments]
    with bind_poseidon_binning(operator) as retrieval:
        if retrieval.forward_model.__globals__["bin_spectrum_to_data"] is not retrieval.bin_spectrum_to_data:
            raise RuntimeError("Corrected-bin callback binding failed before sampling")
        print(f"[corrected-operator-active] excluded={excluded} "
              f"rank={MPI.COMM_WORLD.rank} size={MPI.COMM_WORLD.size}", flush=True)
        if setup_only:
            error = None
            if MPI.COMM_WORLD.rank == 0:
                try:
                    legacy.main()
                    _validate_resolved_config(config_path, excluded)
                except BaseException as exc:  # broadcast setup failures to all ranks
                    error = f"{type(exc).__name__}: {exc}"
            error = MPI.COMM_WORLD.bcast(error, root=0)
            if error:
                raise RuntimeError(error)
            MPI.COMM_WORLD.Barrier()
            if MPI.COMM_WORLD.rank == 0:
                print("[setup-only] corrected operator, matched model and priors PASS; MultiNest skipped",
                      flush=True)
            return

        legacy.main()
        MPI.COMM_WORLD.Barrier()
        if MPI.COMM_WORLD.rank == 0:
            print("[operator-postprocessing-complete] corrected callback remained bound",
                  flush=True)


if __name__ == "__main__":
    main()
