"""Fresh A3 1 h/10 h retrievals with the audited LIFE photon-overlap operator."""

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
CAMPAIGN = ROOT / (
    "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/"
    "retrievals/a3_1_10h_binning_corrected_loo_20261020_r03"
)
DATASETS = {
    1: ("LIFE_proxima_A3_1h_O2_fixedBlack1bar_official.dat",
        "a3043e5de76a834983949e6eca12636ea4de174ebdb2db0853155282c100dee2"),
    10: ("LIFE_proxima_A3_10h.dat",
         "46a026504b9b9521fa29407a501169b9d3cfc433de40a91b8ade86d7767abb5b"),
}
MODEL_TAGS = {
    "full": "full",
    "NH3": "noNH3",
    "N2O": "noN2O",
}
MPI_RANKS = 5
OPERATOR_DESCRIPTION = (
    "midpoint-edge photon overlap; energy conversion at exact channel centre"
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


def parse_scope(arguments: list[str]) -> tuple[int, str | None, Path, Path, bool]:
    required = {
        "--campaign": "proxima", "--scenario": "A3", "--n-live": "800",
        "--error-inflation": "none", "--surface-pressure-mode": "fixed-black",
        "--x-profile": "isochem", "--R": "10000", "--wl-min": "3.0",
        "--wl-max": "20.0",
    }
    for flag, expected in required.items():
        if one_value(arguments, flag) != expected:
            raise ValueError(f"Frozen A3 short-run scope requires {flag} {expected}")
    if arguments.count("--include-o2") != 1:
        raise ValueError("All corrected short-run models must retain O2")
    if any(flag in arguments for flag in (
        "--resume", "--validate-forward", "--fixed-abundances-json",
        "--a0-reference", "--fix-a0-species", "--vertical-gradient-species",
    )):
        raise ValueError("Only fresh, isochemical, free-abundance models are authorized")

    hours = int(float(one_value(arguments, "--hours")))
    if hours not in DATASETS or float(one_value(arguments, "--hours")) != hours:
        raise ValueError("Only the authorized A3 1 h and 10 h datasets are accepted")
    exclusion_positions = [i for i, value in enumerate(arguments)
                           if value == "--exclude-species"]
    excluded: str | None = None
    if exclusion_positions:
        if len(exclusion_positions) != 1 or exclusion_positions[0] + 1 >= len(arguments):
            raise ValueError("At most one molecular omission is allowed")
        excluded = arguments[exclusion_positions[0] + 1]
        if excluded not in {"NH3", "N2O"}:
            raise ValueError("Only no-NH3 and no-N2O models are authorized")

    expected_tag = f"_O2_fixedBlack1bar_noxtol_BIN1_20261020_{hours}h_{MODEL_TAGS[excluded or 'full']}"
    if one_value(arguments, "--output-tag") != expected_tag:
        raise ValueError("Output tag does not match the frozen run identity")
    dataset_name, expected_hash = DATASETS[hours]
    supplied_dataset = Path(one_value(arguments, "--dataset-file"))
    dataset = supplied_dataset if supplied_dataset.is_absolute() else ROOT / supplied_dataset
    dataset = dataset.resolve()
    expected_dataset = (PROJECT / "life_data" / dataset_name).resolve()
    if dataset != expected_dataset:
        raise ValueError(f"Unexpected dataset path for {hours} h: {dataset}")
    if sha256(dataset) != expected_hash:
        raise ValueError(f"Frozen {hours} h dataset SHA-256 mismatch")

    run_dir = Path(one_value(arguments, "--run-dir"))
    config_path = Path(one_value(arguments, "--configuration-json")).resolve()
    run_id = f"A3_{hours}h_{'full' if excluded is None else 'no_' + excluded}"
    expected_config = (CAMPAIGN / "resolved" / f"{run_id}.json").resolve()
    if not run_dir.is_absolute() or config_path != expected_config:
        raise ValueError("Run or resolved-configuration path escaped the isolated campaign")
    setup_only = arguments.count("--setup-only") == 1
    if arguments.count("--setup-only") > 1:
        raise ValueError("Duplicate --setup-only flag")
    return hours, excluded, dataset, config_path, setup_only


def validate_operator(hours: int, excluded: str | None, dataset: Path,
                      operator_record: Path) -> tuple[LifePhotonOperator, dict]:
    with np.load(PROJECT / "forward_emission/A3_emission.npz") as saved:
        native = np.asarray(saved["wl_um"], dtype=np.float64).copy()
        truth_flux = np.asarray(saved["Fp_obs_W_m2_m"], dtype=np.float64).copy()
    with np.load(PROJECT / "lifesim/life_classic_binned_products.npz") as saved:
        centres = np.asarray(saved["wl_bins_um"], dtype=np.float64).copy()
        binned_flux = np.asarray(saved["flux_binned_A3"], dtype=np.float64).copy()
    truth_binned = binned_flux * 6.62607015e-34 * 299792458.0 / (centres * 1e-6)
    observed = np.loadtxt(dataset, skiprows=1)
    if observed.shape != (centres.size, 4) or centres.size != 31:
        raise ValueError(f"Expected 31 LIFE channels; found data shape {observed.shape}")
    if not np.all(np.isfinite(observed)) or np.any(observed[:, 3] <= 0):
        raise ValueError("Observed data or diagonal uncertainties are invalid")
    np.testing.assert_allclose(observed[:, 0], centres, rtol=0, atol=5e-6)

    operator = LifePhotonOperator.build(native, centres)
    np.testing.assert_allclose(operator.apply(truth_flux), truth_binned,
                               rtol=1e-12, atol=0)
    retrieval_name = f"proxima_A3_{hours}h{one_value(sys.argv[1:], '--output-tag')}"
    with bind_poseidon_binning(operator) as retrieval:
        if retrieval.forward_model.__globals__["bin_spectrum_to_data"] is not retrieval.bin_spectrum_to_data:
            raise RuntimeError("POSEIDON likelihood callback is not bound to corrected operator")
        data = legacy.load_data(
            str(dataset.parent), [dataset.name], ["LIFE"], native,
            skiprows=1, wl_unit="micron", bin_width="half", spectrum_unit="Fp",
        )
        callback_binned = retrieval.bin_spectrum_to_data(truth_flux, native, data)
        np.testing.assert_allclose(callback_binned, truth_binned, rtol=1e-10, atol=0)
        record = {
            "status": "PASS", "scenario": "A3", "hours": hours,
            "excluded_species": excluded, "dataset": str(dataset),
            "dataset_sha256": sha256(dataset), "channels": int(centres.size),
            "wavelength_centres_um": [float(centres[0]), float(centres[-1])],
            "native_grid_um": [float(native[0]), float(native[-1])],
            "operator": OPERATOR_DESCRIPTION,
            "max_relative_truth_closure": float(
                np.max(np.abs(operator.apply(truth_flux) / truth_binned - 1.0))
            ),
            "actual_poseidon_callback_bound": True,
            "max_relative_callback_closure": float(
                np.max(np.abs(callback_binned / truth_binned - 1.0))
            ),
            "truth_chi2": float(np.sum(((observed[:, 2] - truth_binned) / observed[:, 3]) ** 2)),
            "mpi_rank_pids": [int(pid) for pid in MPI.COMM_WORLD.allgather(os.getpid())],
            "mpi_size": int(MPI.COMM_WORLD.size),
            "binding_scope": "sampling and posterior spectral/PT postprocessing",
            "stage": "setup_only" if "--setup-only" in sys.argv else "sampling",
            "retrieval_name": retrieval_name,
        }
    if MPI.COMM_WORLD.rank == 0:
        operator_record.parent.mkdir(parents=True, exist_ok=True)
        with operator_record.open("x", encoding="utf-8") as stream:
            json.dump(record, stream, indent=2, sort_keys=True)
            stream.write("\n")
    return operator, record


def validate_resolved_config(path: Path, hours: int, excluded: str | None) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"Resolved configuration missing: {path}")
    config = json.loads(path.read_text(encoding="utf-8"))
    declared, free = (15, 14) if excluded is None else (14, 13)
    if config.get("declared_dimension") != declared or config.get("effective_free_dimension") != free:
        raise ValueError("Unexpected declared/free model dimensions")
    if config.get("dataset_sha256") != DATASETS[hours][1]:
        raise ValueError("Resolved configuration does not match the frozen dataset")
    if config.get("R") != 10000 or config.get("wl_min") != 3.0 or config.get("wl_max") != 20.0:
        raise ValueError("Resolved spectral grid differs from corrected-bin scope")
    if (config.get("n_live") != 800 or config.get("ev_tol") != 0.5
            or config.get("surface_pressure_mode") != "fixed-black"
            or config.get("error_inflation") != "none"
            or config.get("x_profile") != "isochem"):
        raise ValueError("Resolved retrieval settings differ from frozen scope")
    if config.get("fixed_log10_abundances") != {}:
        raise ValueError("Molecular abundances must remain free in all six runs")
    if "log_P_surf" not in config.get("fixed_parameters", []):
        raise ValueError("Opaque surface must remain fixed at 1 bar")
    if excluded:
        if f"log_{excluded}" in config["parameters"] or excluded in config["param_species"]:
            raise ValueError(f"Excluded abundance or opacity remains active: {excluded}")
    elif not {"log_NH3", "log_N2O"}.issubset(config["parameters"]):
        raise ValueError("Full model is missing a target molecular abundance")
    return config


def main() -> None:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--operator-record", type=Path, required=True)
    options, arguments = parser.parse_known_args()
    hours, excluded, dataset, config_path, setup_only = parse_scope(arguments)
    if MPI.COMM_WORLD.size != MPI_RANKS:
        raise RuntimeError(f"Expected exactly MPI{MPI_RANKS}; got MPI{MPI.COMM_WORLD.size}")
    operator_record = options.operator_record.resolve()
    operator, _ = validate_operator(hours, excluded, dataset, operator_record)
    config = Path(one_value(arguments, "--configuration-json")).resolve()
    if config != config_path:
        raise ValueError("Resolved-configuration destination changed after scope validation")

    sys.argv = [sys.argv[0], *arguments]
    with bind_poseidon_binning(operator) as retrieval:
        if retrieval.forward_model.__globals__["bin_spectrum_to_data"] is not retrieval.bin_spectrum_to_data:
            raise RuntimeError("Corrected callback binding failed before sampling")
        print(f"[corrected-operator-active] hours={hours} excluded={excluded or 'none'} "
              f"rank={MPI.COMM_WORLD.rank} size={MPI.COMM_WORLD.size}", flush=True)
        if setup_only:
            error = None
            if MPI.COMM_WORLD.rank == 0:
                try:
                    legacy.main()
                    validate_resolved_config(config_path, hours, excluded)
                except BaseException as exc:
                    error = f"{type(exc).__name__}: {exc}"
            error = MPI.COMM_WORLD.bcast(error, root=0)
            if error:
                raise RuntimeError(error)
            MPI.COMM_WORLD.Barrier()
            if MPI.COMM_WORLD.rank == 0:
                print("[setup-only] corrected operator, model and priors PASS", flush=True)
            return

        legacy.main()
        MPI.COMM_WORLD.Barrier()
        if MPI.COMM_WORLD.rank == 0:
            print("[operator-postprocessing-complete] corrected callback remained bound",
                  flush=True)


if __name__ == "__main__":
    main()
