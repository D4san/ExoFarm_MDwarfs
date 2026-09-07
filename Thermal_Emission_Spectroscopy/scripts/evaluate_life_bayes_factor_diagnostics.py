"""Evaluate two fixed-template Bayes-factor diagnostics for LIFE emission.

The diagnostics use one observed dataset and compare deterministic forward
templates with the same diagonal Gaussian errors:

1. full A3 versus full A0;
2. full A3 versus A3 with its N2O profile reset to A0.

With no free nuisance parameters, the evidence ratio is the likelihood ratio.
This is intentionally a fast diagnostic, not a substitute for a matched pair
of POSEIDON/MultiNest retrievals with integrated nuisance parameters.
"""

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from spectres import spectres


H_PLANCK = 6.62607015e-34
C_LIGHT = 2.99792458e8

REPO = Path(__file__).resolve().parents[2]
CAMPAIGN_ID = "life_proxima_b_earthlike_v1"
OUTPUT_ROOT = REPO / "Thermal_Emission_Spectroscopy" / "outputs" / CAMPAIGN_ID
FORWARD_DIR = OUTPUT_ROOT / "forward_emission"
DIAGNOSTICS_DIR = OUTPUT_ROOT / "molecular_diagnostics"
DATA_DIR = OUTPUT_ROOT / "life_data"
TABLE_DIR = OUTPUT_ROOT / "tables"


def _load_dataset(path):
    data = np.loadtxt(path, skiprows=1)
    if data.ndim != 2 or data.shape[1] != 4:
        raise ValueError(f"expected four dataset columns, got {data.shape}")
    wl_um, half_bin_um, observed, sigma = data.T
    valid = (np.isfinite(wl_um) & np.isfinite(half_bin_um) &
             np.isfinite(observed) & np.isfinite(sigma) & (sigma > 0))
    if not np.all(valid):
        raise ValueError("dataset contains non-finite values or non-positive sigma")
    return {
        "wl_um": wl_um,
        "half_bin_um": half_bin_um,
        "observed": observed,
        "sigma": sigma,
    }


def _load_template(path, target_wl_um):
    product = np.load(path)
    wl_native_m = np.asarray(product["wl_um"], dtype=float) * 1e-6
    flux_native = np.asarray(product["Fp_obs_W_m2_m"], dtype=float)
    if wl_native_m.ndim != 1 or flux_native.shape != wl_native_m.shape:
        raise ValueError(f"invalid forward template: {path}")
    if not np.all(np.isfinite(flux_native)) or np.any(flux_native <= 0):
        raise ValueError(f"template contains invalid flux: {path}")

    target_wl_m = np.asarray(target_wl_um, dtype=float) * 1e-6
    photon_native = flux_native * wl_native_m / (H_PLANCK * C_LIGHT)
    photon_binned = spectres(
        target_wl_m, wl_native_m, photon_native,
        fill=0.0, verbose=False,
    )
    return photon_binned * (H_PLANCK * C_LIGHT / target_wl_m)


def _gaussian_loglike(observed, model, sigma):
    residual = (observed - model) / sigma
    chi2 = float(np.sum(residual ** 2))
    loglike = float(-0.5 * np.sum(
        residual ** 2 + np.log(2.0 * np.pi * sigma ** 2)))
    return loglike, chi2


def _diagnostic(name, preferred, reference, observed, sigma):
    loglike_preferred, chi2_preferred = _gaussian_loglike(
        observed, preferred, sigma)
    loglike_reference, chi2_reference = _gaussian_loglike(
        observed, reference, sigma)
    ln_bayes_factor = loglike_preferred - loglike_reference
    return {
        "diagnostic": name,
        "preferred_model": name.split(" vs ", 1)[0],
        "reference_model": name.split(" vs ", 1)[1],
        "loglike_preferred": loglike_preferred,
        "loglike_reference": loglike_reference,
        "chi2_preferred": chi2_preferred,
        "chi2_reference": chi2_reference,
        "delta_chi2_reference_minus_preferred": (
            chi2_reference - chi2_preferred),
        "ln_bayes_factor_preferred_over_reference": ln_bayes_factor,
        "log10_bayes_factor_preferred_over_reference": (
            ln_bayes_factor / np.log(10.0)),
        "bayes_factor_preferred_over_reference": (
            float(np.exp(ln_bayes_factor))
            if ln_bayes_factor < np.log(np.finfo(float).max) else None),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DATA_DIR / "LIFE_proxima_A3_240h.dat",
        help="one observed dataset used for both model comparisons",
    )
    parser.add_argument(
        "--output-stem",
        type=Path,
        default=TABLE_DIR / "life_bayes_factor_diagnostics_A3_240h",
    )
    args = parser.parse_args()

    dataset_path = args.dataset if args.dataset.is_absolute() else REPO / args.dataset
    output_stem = (args.output_stem if args.output_stem.is_absolute()
                   else REPO / args.output_stem)
    output_stem.parent.mkdir(parents=True, exist_ok=True)

    data = _load_dataset(dataset_path)
    wl_um = data["wl_um"]
    observed = data["observed"]
    sigma = data["sigma"]

    templates = {
        "A0": _load_template(FORWARD_DIR / "A0_emission.npz", wl_um),
        "A3": _load_template(FORWARD_DIR / "A3_emission.npz", wl_um),
        "A3_N2O_reset_to_A0": _load_template(
            DIAGNOSTICS_DIR / "A3_reset_N2O_Fp_obs.npz", wl_um),
    }
    if any(template.shape != observed.shape for template in templates.values()):
        raise ValueError("rebinned templates and dataset have different lengths")

    lifesim_product = np.load(
        OUTPUT_ROOT / "lifesim" / "life_classic_binned_products.npz",
        allow_pickle=True,
    )
    saved_wl_um = np.asarray(lifesim_product["wl_bins_um"], dtype=float)
    binned_reference_ph = lifesim_product["flux_binned_A3"]
    # The saved LIFE products are photon-flux density; the dataset and the
    # rebinned templates below are POSEIDON energy flux Fp.
    binned_reference = binned_reference_ph * (
        H_PLANCK * C_LIGHT / (saved_wl_um * 1e-6))
    validation_template = _load_template(
        FORWARD_DIR / "A3_emission.npz", saved_wl_um)
    max_relative_rebin_error = float(np.max(np.abs(
        (validation_template - binned_reference) / binned_reference)))
    max_dataset_wavelength_rounding = float(np.max(np.abs(saved_wl_um - wl_um)))

    results = [
        _diagnostic(
            "A3 vs A0",
            templates["A3"], templates["A0"], observed, sigma,
        ),
        _diagnostic(
            "A3 with N2O vs A3 N2O reset to A0",
            templates["A3"], templates["A3_N2O_reset_to_A0"],
            observed, sigma,
        ),
    ]

    metadata = {
        "experiment": "life_bayes_factor_diagnostics_A3_240h",
        "dataset": str(dataset_path.relative_to(REPO)),
        "n_bins": int(observed.size),
        "observable": "Fp",
        "noise_model": "diagonal Gaussian errors from LIFEsim classic",
        "data_scenario": "A3",
        "data_hours": 240,
        "evidence_definition": (
            "fixed-template Gaussian likelihood ratio; no free nuisance "
            "parameters, common likelihood normalization"
        ),
        "scenario_comparison": (
            "A3 full atmosphere versus A0 full atmosphere on the same A3 data"
        ),
        "molecular_comparison": (
            "A3 full atmosphere versus A3 with N2O reset to its A0 profile; "
            "this removes the A3 excess rather than setting all N2O to zero"
        ),
        "max_relative_rebin_error_A3_vs_saved_life_product": (
            max_relative_rebin_error
        ),
        "max_dataset_wavelength_rounding_um": max_dataset_wavelength_rounding,
        "limitations": [
            "fixed templates do not marginalize radius, PT, abundances, or x_tol",
            "one diagonal-noise realization",
            "LIFEsim classic does not include instrumental covariance",
            "this is not a final instrumental detection claim",
        ],
        "results": results,
    }

    json_path = output_stem.with_suffix(".json")
    csv_path = output_stem.with_suffix(".csv")
    json_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = list(results[0].keys())
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(results)

    print(f"[dataset] {dataset_path.relative_to(REPO)} ({observed.size} bins)")
    print(f"[validation] max relative A3 rebin error: {max_relative_rebin_error:.3e}")
    for result in results:
        print(
            f"[{result['diagnostic']}] "
            f"ln B={result['ln_bayes_factor_preferred_over_reference']:.6f} "
            f"log10 B={result['log10_bayes_factor_preferred_over_reference']:.3f} "
            f"Delta chi2={result['delta_chi2_reference_minus_preferred']:.3f}"
        )
    print(f"[saved] {json_path.relative_to(REPO)}")
    print(f"[saved] {csv_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
