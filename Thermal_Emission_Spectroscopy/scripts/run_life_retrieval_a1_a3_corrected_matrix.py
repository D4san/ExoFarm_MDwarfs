"""Run one fresh A1/A3 LIFE retrieval with the audited corrected-bin operator."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

for _variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                  "NUMEXPR_NUM_THREADS"):
    os.environ[_variable] = "1"

import numpy as np
from mpi4py import MPI

from life_bin_operator_diagnostic import LifePhotonOperator, bind_poseidon_binning
import run_life_retrieval as legacy


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1"
CAMPAIGN = PROJECT / "retrievals/a1_a3_corrected_binning_matrix_loo_20261021_r01"
SCRATCH = Path("/home/dasan/exofarm_a1_a3_corrected_binning_matrix_20261021_r01")
OPERATOR_SOURCE = ROOT / "Thermal_Emission_Spectroscopy/scripts/life_bin_operator_diagnostic.py"
DATASETS = {
    ("A1", 1): (
        "LIFE_proxima_A1_1h_O2_fixedBlack1bar_noiseRepeat2.dat",
        "93fb65765101950063d5aa9a3dafae4df38273292cb0e3349e94b8a34516cfcc",
    ),
    ("A1", 10): (
        "LIFE_proxima_A1_10h.dat",
        "ed39ae6dc5b8ff0d5c8aca3d126a2945343a289be30f3b8d9e8e72c434ee9b8f",
    ),
    ("A1", 100): (
        "LIFE_proxima_A1_100h_O2_fixedBlack1bar_noxtol_audit.dat",
        "d66c886238a2916312c645589be8601828fbf0a7cd2f02a383ef1d6a3454b5e3",
    ),
    ("A3", 1): (
        "LIFE_proxima_A3_1h_O2_fixedBlack1bar_official.dat",
        "a3043e5de76a834983949e6eca12636ea4de174ebdb2db0853155282c100dee2",
    ),
    ("A3", 10): (
        "LIFE_proxima_A3_10h.dat",
        "46a026504b9b9521fa29407a501169b9d3cfc433de40a91b8ade86d7767abb5b",
    ),
    ("A3", 100): (
        "LIFE_proxima_A3_100h.dat",
        "78662546181a5b74391a14b7b73ae80d879200a74db6a4bc5338e3ce7eee4705",
    ),
}
EXCLUDED_SPECIES = {"H2O", "CO2", "CH4", "O3", "N2O", "NH3"}
BASE_SPECIES = ["H2O", "CO2", "CH4", "O2", "O3", "N2O", "NH3"]
MPI_RANKS = 4
OPERATOR_DESCRIPTION = (
    "midpoint-edge photon overlap; energy-to-photon conversion at exact channel centre"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def one_value(arguments: list[str], flag: str) -> str:
    positions = [index for index, value in enumerate(arguments) if value == flag]
    if len(positions) != 1 or positions[0] + 1 >= len(arguments):
        raise ValueError(f"Expected exactly one value for {flag}")
    return arguments[positions[0] + 1]


def case_identity(scenario: str, hours: int, excluded: str | None) -> str:
    suffix = "full" if excluded is None else f"no_{excluded}"
    return f"{scenario}_{hours}h_{suffix}"


def output_tag(scenario: str, hours: int, excluded: str | None) -> str:
    suffix = "full" if excluded is None else f"no{excluded}"
    return (f"_O2_fixedBlack1bar_noxtol_BIN1_20261021_MATRIX_"
            f"{scenario}_{hours}h_{suffix}")


def parse_scope(arguments: list[str], operator_record: Path) -> tuple[
        str, int, str | None, Path, Path, bool, str]:
    required = {
        "--campaign": "proxima", "--n-live": "800",
        "--error-inflation": "none", "--surface-pressure-mode": "fixed-black",
        "--x-profile": "isochem", "--R": "10000", "--wl-min": "3.0",
        "--wl-max": "20.0",
    }
    for flag, expected in required.items():
        if one_value(arguments, flag) != expected:
            raise ValueError(f"Frozen corrected-matrix scope requires {flag} {expected}")
    scenario = one_value(arguments, "--scenario")
    if scenario not in {"A1", "A3"}:
        raise ValueError("Only A1 and A3 are in the authorized corrected matrix")
    if arguments.count("--include-o2") != 1:
        raise ValueError("All matrix models must retain O2")
    if any(flag in arguments for flag in (
        "--resume", "--validate-forward", "--fixed-abundances-json",
        "--a0-reference", "--fix-a0-species", "--vertical-gradient-species",
    )):
        raise ValueError("Only fresh, isochemical, free-abundance retrievals are in scope")

    raw_hours = float(one_value(arguments, "--hours"))
    hours = int(raw_hours)
    if raw_hours != hours or (scenario, hours) not in DATASETS:
        raise ValueError("Only the frozen 1, 10 and 100 h datasets are authorized")

    exclusion_positions = [i for i, value in enumerate(arguments)
                           if value == "--exclude-species"]
    excluded: str | None = None
    if exclusion_positions:
        if len(exclusion_positions) != 1 or exclusion_positions[0] + 1 >= len(arguments):
            raise ValueError("At most one molecular species may be removed")
        excluded = arguments[exclusion_positions[0] + 1]
        if excluded not in EXCLUDED_SPECIES:
            raise ValueError(f"Unauthorized LOO species: {excluded}")

    if one_value(arguments, "--output-tag") != output_tag(scenario, hours, excluded):
        raise ValueError("Output tag does not match the frozen model identity")
    dataset_name, expected_hash = DATASETS[(scenario, hours)]
    supplied = Path(one_value(arguments, "--dataset-file"))
    dataset = (supplied if supplied.is_absolute() else ROOT / supplied).resolve()
    expected_dataset = (PROJECT / "life_data" / dataset_name).resolve()
    if dataset != expected_dataset or sha256(dataset) != expected_hash:
        raise ValueError(f"Dataset path/hash mismatch for {scenario} {hours} h")

    run_id = case_identity(scenario, hours, excluded)
    run_dir = Path(one_value(arguments, "--run-dir"))
    config_path = Path(one_value(arguments, "--configuration-json")).resolve()
    expected_config = (CAMPAIGN / "resolved" / f"{run_id}.json").resolve()
    setup_only = arguments.count("--setup-only") == 1
    if arguments.count("--setup-only") > 1:
        raise ValueError("Duplicate --setup-only flag")
    expected_run_dir = SCRATCH / ("preflight" if setup_only else "runs") / run_id
    if not run_dir.is_absolute() or run_dir != expected_run_dir or config_path != expected_config:
        raise ValueError("Run/configuration path escaped the isolated campaign")
    expected_record = (CAMPAIGN / "preflight/operators" if setup_only
                       else CAMPAIGN / "runtime/operators") / f"{run_id}.json"
    if operator_record.resolve() != expected_record.resolve():
        raise ValueError("Operator record path does not match campaign phase/run")
    return scenario, hours, excluded, dataset, config_path, setup_only, run_id


def validate_operator(scenario: str, hours: int, excluded: str | None,
                      dataset: Path, operator_record: Path) -> tuple[LifePhotonOperator, dict]:
    native_path = PROJECT / "forward_emission" / f"{scenario}_emission.npz"
    binned_path = PROJECT / "lifesim/life_classic_binned_products.npz"
    with np.load(native_path) as saved:
        native = np.asarray(saved["wl_um"], dtype=np.float64).copy()
        truth_flux = np.asarray(saved["Fp_obs_W_m2_m"], dtype=np.float64).copy()
    with np.load(binned_path) as saved:
        centres = np.asarray(saved["wl_bins_um"], dtype=np.float64).copy()
        binned_energy_flux = np.asarray(saved[f"flux_binned_{scenario}"],
                                        dtype=np.float64).copy()
    truth_binned = (binned_energy_flux * 6.62607015e-34 * 299792458.0 /
                    (centres * 1e-6))
    observed = np.loadtxt(dataset, skiprows=1)
    if observed.shape != (centres.size, 4) or centres.size != 31:
        raise ValueError(f"Expected 31 LIFE channels, got {observed.shape}")
    if not np.all(np.isfinite(observed)) or np.any(observed[:, 3] <= 0):
        raise ValueError("Observed data or diagonal uncertainties are invalid")
    np.testing.assert_allclose(observed[:, 0], centres, rtol=0, atol=5e-6)
    if not np.all(np.isfinite(native)) or not np.all(np.isfinite(truth_flux)):
        raise ValueError("Native emission truth contains non-finite values")

    operator = LifePhotonOperator.build(native, centres)
    operator_binned = operator.apply(truth_flux)
    np.testing.assert_allclose(operator_binned, truth_binned, rtol=1e-12, atol=0)
    with bind_poseidon_binning(operator) as retrieval:
        callback = retrieval.forward_model.__globals__["bin_spectrum_to_data"]
        if callback is not retrieval.bin_spectrum_to_data:
            raise RuntimeError("POSEIDON forward-model callback is not the corrected operator")
        data = legacy.load_data(
            str(dataset.parent), [dataset.name], ["LIFE"], native,
            skiprows=1, wl_unit="micron", bin_width="half", spectrum_unit="Fp",
        )
        callback_binned = retrieval.bin_spectrum_to_data(truth_flux, native, data)
        np.testing.assert_allclose(callback_binned, truth_binned, rtol=1e-10, atol=0)
        record = {
            "status": "PASS", "scenario": scenario, "hours": hours,
            "excluded_species": excluded, "dataset": str(dataset),
            "dataset_sha256": sha256(dataset), "channels": int(centres.size),
            "channel_centres_um": [float(centres[0]), float(centres[-1])],
            "native_grid_um": [float(native[0]), float(native[-1])],
            "operator": OPERATOR_DESCRIPTION,
            "operator_source_sha256": sha256(OPERATOR_SOURCE),
            "native_emission_sha256": sha256(native_path),
            "binned_reference_sha256": sha256(binned_path),
            "max_relative_operator_truth_closure": float(
                np.max(np.abs(operator_binned / truth_binned - 1.0))
            ),
            "max_relative_callback_truth_closure": float(
                np.max(np.abs(callback_binned / truth_binned - 1.0))
            ),
            "truth_chi2": float(np.sum(((observed[:, 2] - truth_binned) /
                                        observed[:, 3]) ** 2)),
            "actual_poseidon_callback_bound": True,
            "mpi_rank_pids": [int(pid) for pid in MPI.COMM_WORLD.allgather(os.getpid())],
            "mpi_size": int(MPI.COMM_WORLD.size),
            "binding_scope": "sampling and posterior spectral/PT postprocessing",
            "stage": "setup_only" if "--setup-only" in sys.argv else "sampling",
            "run_id": case_identity(scenario, hours, excluded),
        }
    if MPI.COMM_WORLD.rank == 0:
        operator_record.parent.mkdir(parents=True, exist_ok=True)
        with operator_record.open("x", encoding="utf-8") as stream:
            json.dump(record, stream, indent=2, sort_keys=True)
            stream.write("\n")
    return operator, record


def validate_resolved_config(path: Path, scenario: str, hours: int,
                             excluded: str | None) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"Resolved configuration missing: {path}")
    config = json.loads(path.read_text(encoding="utf-8"))
    expected_hash = DATASETS[(scenario, hours)][1]
    expected_species = [species for species in BASE_SPECIES if species != excluded]
    expected_parameters = [
        "R_p_ref", "a1", "a2", "log_P1", "log_P2", "log_P3", "T_ref",
        *[f"log_{species}" for species in expected_species], "log_P_surf",
    ]
    declared, free = (15, 14) if excluded is None else (14, 13)
    if config.get("declared_dimension") != declared or config.get("effective_free_dimension") != free:
        raise ValueError("Resolved declared/free dimensions differ from frozen scope")
    if config.get("parameters") != expected_parameters or config.get("param_species") != expected_species:
        raise ValueError("Resolved model has wrong species or parameter ordering")
    if config.get("dataset_sha256") != expected_hash:
        raise ValueError("Resolved configuration dataset SHA-256 mismatch")
    frozen = {
        "R": 10000, "wl_min": 3.0, "wl_max": 20.0,
        "n_live": 800, "ev_tol": 0.5, "surface_pressure_mode": "fixed-black",
        "error_inflation": "none", "x_profile": "isochem",
        "likelihood": "direct_emission; diagonal Gaussian; same observed Fp",
    }
    for key, value in frozen.items():
        if config.get(key) != value:
            raise ValueError(f"Resolved scope mismatch for {key}: {config.get(key)!r}")
    if config.get("fixed_log10_abundances") != {}:
        raise ValueError("Molecular abundances must be free in these retrievals")
    if config.get("fixed_parameters") != ["log_P_surf"]:
        raise ValueError("Only the opaque surface pressure may be fixed")
    for species in BASE_SPECIES:
        parameter = f"log_{species}"
        if species == excluded:
            if parameter in config.get("parameters", []) or species in config.get("param_species", []):
                raise ValueError(f"Excluded abundance/opacity remains active: {species}")
        elif parameter not in config.get("prior_ranges", {}):
            raise ValueError(f"Shared species prior is missing: {species}")
    if config["prior_ranges"].get("log_P_surf") != [0.0, 0.0]:
        raise ValueError("Opaque surface is not fixed at 1 bar")
    return config


def main() -> None:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--operator-record", type=Path, required=True)
    options, arguments = parser.parse_known_args()
    if MPI.COMM_WORLD.size != MPI_RANKS:
        raise RuntimeError(f"Expected MPI{MPI_RANKS}; got MPI{MPI.COMM_WORLD.size}")
    scenario, hours, excluded, dataset, config_path, setup_only, run_id = parse_scope(
        arguments, options.operator_record
    )
    operator, _ = validate_operator(scenario, hours, excluded, dataset,
                                    options.operator_record.resolve())
    if Path(one_value(arguments, "--configuration-json")).resolve() != config_path:
        raise ValueError("Resolved-configuration destination changed after scope validation")

    sys.argv = [sys.argv[0], *arguments]
    with bind_poseidon_binning(operator) as retrieval:
        if retrieval.forward_model.__globals__["bin_spectrum_to_data"] is not retrieval.bin_spectrum_to_data:
            raise RuntimeError("Corrected callback binding failed before retrieval")
        print(f"[corrected-operator-active] {run_id} rank={MPI.COMM_WORLD.rank} "
              f"size={MPI.COMM_WORLD.size}", flush=True)
        if setup_only:
            error = None
            if MPI.COMM_WORLD.rank == 0:
                try:
                    legacy.main()
                    validate_resolved_config(config_path, scenario, hours, excluded)
                except BaseException as exc:
                    error = f"{type(exc).__name__}: {exc}"
            error = MPI.COMM_WORLD.bcast(error, root=0)
            if error:
                raise RuntimeError(error)
            MPI.COMM_WORLD.Barrier()
            if MPI.COMM_WORLD.rank == 0:
                print("[setup-only] corrected operator, model, dataset and priors PASS",
                      flush=True)
            return

        legacy.main()
        MPI.COMM_WORLD.Barrier()
        if MPI.COMM_WORLD.rank == 0:
            print("[operator-postprocessing-complete] corrected callback remained bound",
                  flush=True)


if __name__ == "__main__":
    main()
