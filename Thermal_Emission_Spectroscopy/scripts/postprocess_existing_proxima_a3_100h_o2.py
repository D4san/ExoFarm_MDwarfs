"""Recover POSEIDON products from the completed Proxima A3 100 h MultiNest run.

This is deliberately a post-processing-only entry point. It never calls
``run_retrieval`` or ``PyMultiNest_retrieval``. The existing extensionless
equal-weight sample is preserved and copied to the ``.dat`` filename that
PyMultiNest's Analyzer expects.
"""

from __future__ import annotations

import hashlib
import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


REPO = Path(__file__).resolve().parents[2]
os.environ.setdefault(
    "POSEIDON_input_data",
    "/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs",
)
os.environ.setdefault(
    "PYSYN_CDBS",
    "/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids",
)
sys.path.insert(0, str(Path(__file__).resolve().parent))

import emission_forward as ef  # noqa: E402
from POSEIDON.core import (  # noqa: E402
    define_model,
    load_data,
    set_priors,
    wl_grid_constant_R,
)
from POSEIDON.retrieval import retrieved_samples  # noqa: E402
from POSEIDON.utility import (  # noqa: E402
    write_MultiNest_results,
    write_retrieved_PT,
    write_retrieved_log_X,
    write_retrieved_spectrum,
)
from mpi4py import MPI  # noqa: E402


TAG = "proxima_A3_100h_O2_fixedBlack1bar_noxtol"
EXPECTED_RAW_SHA256 = (
    "43df7db9bffc11b00dc02f3e7ee97fa6de001d0c693128fa49f1fc3310831bc8"
)
POSTPROCESS_SEED = 20260926
N_OUTPUT_SAMPLES = 1000


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_finite(path: Path, skiprows: int = 0) -> np.ndarray:
    array = np.loadtxt(path, skiprows=skiprows, ndmin=2)
    if array.size == 0 or not np.isfinite(array).all():
        raise RuntimeError(f"Empty or non-finite numeric product: {path}")
    return array


def validate_outputs(expected_outputs: list[Path], parameter_count: int) -> None:
    """Validate POSEIDON's numeric tables and block-formatted log-X export."""
    results, samples_path, spectrum_path, pt_path, log_x_path = expected_outputs
    for path in expected_outputs:
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"Missing or empty post-processing product: {path}")
        text = path.read_text(encoding="utf-8", errors="replace")
        if re.search(r"(?i)(?<![a-z])(?:nan|inf(?:inity)?)(?![a-z])", text):
            raise RuntimeError(f"NaN/Inf token found in {path}")

    samples = require_finite(samples_path, skiprows=1)
    if samples.shape != (7479, parameter_count):
        raise RuntimeError(f"Unexpected posterior sample export shape: {samples.shape}")
    spectrum = require_finite(spectrum_path, skiprows=1)
    if spectrum.ndim != 2 or spectrum.shape[1] != 6 or spectrum.shape[0] < 31:
        raise RuntimeError(f"Unexpected retrieved spectrum shape: {spectrum.shape}")
    pt = require_finite(pt_path, skiprows=1)
    if pt.shape != (100, 6):
        raise RuntimeError(f"Unexpected retrieved P-T profile shape: {pt.shape}")

    numeric_log_x_rows = []
    for line in log_x_path.read_text(encoding="utf-8", errors="replace").splitlines():
        fields = line.split()
        if not fields:
            continue
        try:
            float(fields[0])
        except ValueError:
            continue  # POSEIDON inserts species/column labels between blocks.
        values = np.asarray([float(field) for field in fields], dtype=float)
        if values.shape != (6,) or not np.isfinite(values).all():
            raise RuntimeError(f"Invalid numeric log-X row: {line}")
        numeric_log_x_rows.append(values)
    if len(numeric_log_x_rows) != 800:
        raise RuntimeError(
            f"Expected 8 species x 100 log-X rows; found {len(numeric_log_x_rows)}"
        )

    results_text = results.read_text(encoding="utf-8", errors="replace")
    for required in (
        "ln Z", "chi^2_red", "degrees of freedom", "log_N2O", "log_NH3", "log_O2"
    ):
        if required not in results_text:
            raise RuntimeError(f"Missing {required!r} in POSEIDON results: {results}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--validate-existing",
        action="store_true",
        help="validate files already generated without recomputing posterior products",
    )
    args = parser.parse_args()

    target = ef.PROXIMA_B
    campaign_root = REPO / "Thermal_Emission_Spectroscopy" / "outputs" / (
        "life_proxima_b_earthlike_v1"
    )
    run_root = campaign_root / "retrievals"
    data_path = campaign_root / "life_data" / "LIFE_proxima_A3_100h.dat"
    product_root = (
        run_root / "POSEIDON_output" / "proxima_b_earthlike" / "retrievals"
    )
    raw_dir = product_root / "MultiNest_raw"
    model_name = TAG
    product_name = f"{model_name}_{TAG}"
    raw_source = raw_dir / f"{product_name}-post_equal_weights"
    analyzer_sample = raw_dir / f"{product_name}-post_equal_weights.dat"
    launch_log = run_root / f"{TAG}.launch.log"

    if not data_path.is_file() or not launch_log.is_file():
        raise FileNotFoundError("Expected LIFE dataset or original launch log is missing")
    log_text = launch_log.read_text(encoding="utf-8", errors="replace")
    if "Sampling finished. Exiting MultiNest" not in log_text:
        raise RuntimeError("Launch log does not show normal MultiNest completion")
    if "ln(ev)=" not in log_text:
        raise RuntimeError("Launch log is missing MultiNest's final evidence line")

    if not raw_source.is_file():
        raise FileNotFoundError(f"Preserved MultiNest sample is missing: {raw_source}")
    raw_hash = sha256(raw_source)
    if raw_hash != EXPECTED_RAW_SHA256:
        raise RuntimeError(
            "The preserved MultiNest sample hash differs from the inspected file; "
            "refusing to post-process an unexpected artifact."
        )
    raw = require_finite(raw_source)
    if raw.shape != (7479, 16):
        raise RuntimeError(f"Unexpected MultiNest sample shape: {raw.shape}")

    # Rebuild the exact retrieval setup from run_life_retrieval.py.
    wl = wl_grid_constant_R(3.8, 19.0, 10000)
    star = ef.build_star(wl, target)
    planet = ef.build_planet(target)
    param_species = ["H2O", "CO2", "CH4", "O2", "O3", "N2O", "NH3"]
    model = define_model(
        model_name,
        ef.BULK_SPECIES,
        param_species,
        PT_profile="Madhu",
        X_profile="isochem",
        X_dim=1,
        species_vert_gradient=[],
        radius_unit="R_E",
        surface=True,
        thermal=True,
        thermal_scattering=False,
        error_inflation=None,
    )
    names = list(model["param_names"])
    if len(names) != 15 or "log_P_surf" not in names:
        raise RuntimeError(f"Unexpected corrected model parameterization: {names}")
    if "x_tol" in names or "log_O2" not in names:
        raise RuntimeError(f"Unexpected error/species parameters: {names}")
    surface_column = names.index("log_P_surf")
    if not np.allclose(raw[:, surface_column], 0.0, rtol=0.0, atol=1e-12):
        raise RuntimeError("MultiNest samples do not have the fixed 1-bar surface")

    data = load_data(
        str(data_path.parent),
        [data_path.name],
        ["LIFE"],
        wl,
        skiprows=1,
        wl_unit="micron",
        bin_width="half",
        spectrum_unit="Fp",
    )
    if len(data["ydata"]) != 31:
        raise RuntimeError(f"Expected 31 LIFE bins, found {len(data['ydata'])}")

    prior_types = {
        "a1": "uniform",
        "a2": "uniform",
        "log_P1": "uniform",
        "log_P2": "uniform",
        "log_P3": "uniform",
        "T_ref": "uniform",
        "log_X": "uniform",
        "R_p_ref": "uniform",
        "log_P_surf": "uniform",
        "log_O2": "uniform",
    }
    prior_ranges = {
        "a1": [0.02, 2.0],
        "a2": [0.02, 2.0],
        "log_P1": [-6, 1],
        "log_P2": [-6, 1],
        "log_P3": [-2, 1],
        "T_ref": [150, 400],
        "log_X": [-12, -1],
        "R_p_ref": [0.8 * target.planet["R_p"], 1.3 * target.planet["R_p"]],
        "log_P_surf": [0.0, 0.0],
        "log_O2": [-6.0, np.log10(0.5)],
    }
    priors = set_priors(planet, star, model, data, prior_types, prior_ranges)
    P = np.logspace(
        np.log10(target.P_max_bar), np.log10(target.P_min_bar), 100
    )
    # The original run_retrieval call used these defaults for direct emission.
    if planet["system_distance"] is None:
        planet["system_distance"] = 1.0
    F_s_obs = (star["R_s"] / planet["system_distance"]) ** 2 * star["F_star"]
    if not np.isfinite(F_s_obs).all():
        raise RuntimeError("The reconstructed stellar flux contains NaN/Inf")

    results_dir = product_root / "results"
    samples_dir = product_root / "samples"
    expected_outputs = [
        results_dir / f"{product_name}_results.txt",
        samples_dir / f"{product_name}_samples.txt",
        samples_dir / f"{product_name}_spectrum_retrieved.txt",
        samples_dir / f"{product_name}_PT_retrieved.txt",
        samples_dir / f"{product_name}_log_X_retrieved.txt",
    ]
    manifest_path = results_dir / f"{product_name}_postprocess_manifest.json"
    existing = [path for path in [*expected_outputs, manifest_path] if path.exists()]
    if args.validate_existing:
        missing = [path for path in expected_outputs if not path.is_file()]
        if missing:
            raise FileNotFoundError(f"Missing outputs to validate: {missing}")
        if not analyzer_sample.is_file() or sha256(analyzer_sample) != raw_hash:
            raise RuntimeError("Analyzer .dat copy is missing or differs from the raw sample")
        validate_outputs(expected_outputs, len(names))
        manifest = {
            "retrieval": TAG,
            "postprocessed_utc": datetime.now(timezone.utc).isoformat(),
            "method": "POSEIDON posterior reconstruction; MultiNest was not rerun",
            "raw_equal_weight_sample": str(raw_source),
            "raw_sample_sha256": raw_hash,
            "analyzer_sample_copy": str(analyzer_sample),
            "sample_rows": int(raw.shape[0]),
            "sample_columns_including_log_likelihood": int(raw.shape[1]),
            "parameter_names": names,
            "dataset": str(data_path),
            "dataset_sha256": sha256(data_path),
            "configuration": {
                "X_profile": "isochem",
                "species": param_species,
                "N_live": 800,
                "error_inflation": "none",
                "x_tol": "absent",
                "surface": "explicit black surface; log_P_surf=0 (1 bar)",
                "R": 10000,
                "posterior_predictive_draws": N_OUTPUT_SAMPLES,
                "postprocess_random_seed": POSTPROCESS_SEED,
            },
            "outputs": [str(path) for path in expected_outputs],
        }
        manifest_path.write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
        print(f"[postprocess-only] validated existing products for {TAG}")
        print(f"[sample] rows={raw.shape[0]}, columns={raw.shape[1]}, sha256={raw_hash}")
        for path in expected_outputs:
            print(f"[validated] {path}")
        print(f"[manifest] {manifest_path}")
        return
    if existing:
        raise RuntimeError(
            "Refusing to overwrite existing post-processing outputs: "
            + ", ".join(str(path) for path in existing)
        )
    if not results_dir.is_dir() or not samples_dir.is_dir():
        raise FileNotFoundError("POSEIDON results/samples directories are missing")

    if analyzer_sample.exists():
        if sha256(analyzer_sample) != raw_hash:
            raise RuntimeError("Analyzer .dat exists but differs from preserved sample")
    else:
        shutil.copy2(raw_source, analyzer_sample)
    if sha256(raw_source) != raw_hash:
        raise RuntimeError("The original MultiNest sample changed during recovery")

    opac = ef.read_opacities_for(model, wl)

    # Match POSEIDON's default 1000 posterior predictive draws deterministically.
    np.random.seed(POSTPROCESS_SEED)
    os.chdir(raw_dir)
    posterior_products = retrieved_samples(
        planet,
        star,
        model,
        opac,
        data,
        product_name,
        wl,
        P,
        P_ref_set=target.P_max_bar,
        R_p_ref_set=target.planet["R_p"],
        P_param_set=1.0e-2,
        He_fraction=0.17,
        N_slice_EM=2,
        N_slice_DN=4,
        spectrum_type="direct_emission",
        T_phot_grid=None,
        T_het_grid=None,
        log_g_phot_grid=None,
        log_g_het_grid=None,
        I_phot_grid=None,
        I_het_grid=None,
        y_p=np.array([0.0]),
        F_s_obs=F_s_obs,
        constant_gravity=False,
        chemistry_grid=None,
        N_output_samples=N_OUTPUT_SAMPLES,
        comm=MPI.COMM_WORLD,
    )
    (
        T_per_region,
        log_X_per_region,
        spec_low2,
        spec_low1,
        spec_median,
        spec_high1,
        spec_high2,
        _T_best,
        _spectrum_best,
        ymodel_best,
        _ymodel_samples,
    ) = posterior_products

    write_MultiNest_results(
        planet,
        model,
        data,
        product_name,
        800,
        0.5,
        "MultiNest",
        wl,
        10000,
        ymodel_best,
        "direct_emission",
    )
    write_retrieved_spectrum(
        product_name, wl, spec_low2, spec_low1, spec_median, spec_high1, spec_high2
    )
    for region_name, T_intervals in T_per_region.items():
        log_X_intervals = log_X_per_region[region_name]
        write_retrieved_PT(product_name, P, *T_intervals, region_name=region_name)
        write_retrieved_log_X(
            product_name,
            model["chemical_species"],
            P,
            *log_X_intervals,
            region_name=region_name,
        )

    validate_outputs(expected_outputs, len(names))

    manifest = {
        "retrieval": TAG,
        "postprocessed_utc": datetime.now(timezone.utc).isoformat(),
        "method": "POSEIDON posterior reconstruction; MultiNest was not rerun",
        "raw_equal_weight_sample": str(raw_source),
        "raw_sample_sha256": raw_hash,
        "analyzer_sample_copy": str(analyzer_sample),
        "sample_rows": int(raw.shape[0]),
        "sample_columns_including_log_likelihood": int(raw.shape[1]),
        "parameter_names": names,
        "dataset": str(data_path),
        "dataset_sha256": sha256(data_path),
        "configuration": {
            "X_profile": "isochem",
            "species": param_species,
            "N_live": 800,
            "error_inflation": "none",
            "x_tol": "absent",
            "surface": "explicit black surface; log_P_surf=0 (1 bar)",
            "R": 10000,
            "posterior_predictive_draws": N_OUTPUT_SAMPLES,
            "postprocess_random_seed": POSTPROCESS_SEED,
        },
        "outputs": [str(path) for path in expected_outputs],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if sha256(raw_source) != raw_hash:
        raise RuntimeError("The preserved MultiNest sample changed after recovery")
    print(f"[postprocess-only] completed {TAG}")
    print(f"[sample] rows={raw.shape[0]}, columns={raw.shape[1]}, sha256={raw_hash}")
    print(f"[manifest] {manifest_path}")
    for path in expected_outputs:
        print(f"[output] {path}")


if __name__ == "__main__":
    main()
