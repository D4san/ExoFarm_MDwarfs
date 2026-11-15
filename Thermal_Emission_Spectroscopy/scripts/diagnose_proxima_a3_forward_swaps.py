"""Controlled POSEIDON forwards for the Proxima A3 retrieval residual audit.

Vary PT, chemistry and radius one at a time between the saved VULCAN truth and
the posterior median, keeping the LIFE observable, pressure grid, star and
opacity configuration fixed. This script never runs MultiNest or writes to the
canonical forward/retrieval directories.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from POSEIDON.constants import R_E
from POSEIDON.core import define_model, compute_spectrum, make_atmosphere

import emission_forward as ef
from audit_proxima_a3_retrieval_residuals import PALETTE, rebin_energy_flux


CAMPAIGN = (
    ef.REPO / "Thermal_Emission_Spectroscopy" / "outputs"
    / "life_proxima_b_earthlike_v1"
)
SAMPLES = (
    CAMPAIGN / "retrievals" / "POSEIDON_output" / "proxima_b_earthlike"
    / "retrievals" / "samples"
)
OUTPUT = CAMPAIGN / "forward_swap_audit"
SPECIES_RETRIEVAL = ["H2O", "CO2", "CH4", "O3", "N2O", "NH3"]
HOURS = (100, 240)


def load_retrieved_profiles(hours: int, P: np.ndarray, expected_species: list[str]):
    name = f"proxima_A3_{hours}h_fixedP1bar_noxtol"
    stem = f"{name}_{name}"
    pt = np.loadtxt(SAMPLES / f"{stem}_PT_retrieved.txt", skiprows=1)
    if pt.shape != (P.size, 6):
        raise ValueError(f"Unexpected {hours} h PT product: {pt.shape}")
    if not np.allclose(pt[:, 0], P, rtol=1e-7, atol=0):
        raise ValueError(f"Pressure grid mismatch in {hours} h PT")
    T = pt[:, 3]

    lines = (SAMPLES / f"{stem}_log_X_retrieved.txt").read_text(
        encoding="utf-8"
    ).splitlines()
    species = lines[0].split(":", 1)[1].split()
    if species != expected_species:
        raise ValueError(f"Retrieved species {species} != model species {expected_species}")
    blocks = {}
    n_levels = P.size
    for j, molecule in enumerate(species):
        header_index = 1 + j * (n_levels + 1)
        header = lines[header_index]
        if not header.startswith(f"P (bar) | log_{molecule}:"):
            raise ValueError(f"Unexpected chemistry block header: {header}")
        block = np.loadtxt(lines[header_index + 1:header_index + 1 + n_levels])
        if block.shape != (n_levels, 6):
            raise ValueError(f"Unexpected chemistry block {molecule}: {block.shape}")
        if not np.allclose(block[:, 0], P, rtol=1e-7, atol=0):
            raise ValueError(f"Pressure grid mismatch in {molecule} block")
        blocks[molecule] = 10.0 ** block[:, 3]
    X = np.stack([blocks[molecule] for molecule in species])

    posterior = np.loadtxt(SAMPLES / f"{stem}_samples.txt", skiprows=1)
    if posterior.ndim != 2 or posterior.shape[1] != 13:
        raise ValueError(f"Unexpected {hours} h posterior shape: {posterior.shape}")
    R_p_ref = float(np.median(posterior[:, 0]) * R_E)
    return T, X, R_p_ref


def make_retrieval_species_model(surface: bool):
    return define_model(
        "proxima_A3_forward_swap_audit",
        ef.BULK_SPECIES,
        SPECIES_RETRIEVAL,
        PT_profile="file_read",
        X_profile="file_read",
        radius_unit="R_E",
        surface=surface,
        thermal=True,
        thermal_scattering=False,
    )


def evaluate(
    planet, star, model, opac, wl, P, P_surf, P_ref, radius, T, X,
):
    if model["surface"]:
        atmosphere = ef.build_atmosphere(
            planet, model, P, P_ref, radius, P_surf, T, X
        )
    else:
        atmosphere = make_atmosphere(
            planet, model, P, P_ref, radius, T_input=T, X_input=X
        )
    flux = compute_spectrum(
        planet, star, model, atmosphere, opac, wl,
        spectrum_type="direct_emission",
    )
    if flux.shape != wl.shape or not np.all(np.isfinite(flux)):
        raise ValueError("Invalid POSEIDON direct-emission spectrum")
    return flux


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--setup-only", action="store_true")
    args = parser.parse_args()

    target = ef.PROXIMA_B
    saved_path = CAMPAIGN / "forward_emission" / "A3_emission.npz"
    with np.load(saved_path) as saved:
        wl = np.asarray(saved["wl_um"], dtype=float)
        original_flux = np.asarray(saved["Fp_obs_W_m2_m"], dtype=float)
    model_truth = ef.build_model("A3", target)
    model_full_no_surface = define_model(
        "proxima_A3_full_species_no_surface_audit",
        ef.BULK_SPECIES,
        ef.PARAM_SPECIES,
        PT_profile="file_read",
        X_profile="file_read",
        radius_unit="R_E",
        surface=False,
        thermal=True,
        thermal_scattering=False,
    )
    model_six_surface = make_retrieval_species_model(surface=True)
    model_six = make_retrieval_species_model(surface=False)
    P, P_surf, P_ref, radius_truth = ef.pressure_grid(target)
    T_truth, X_truth = ef.load_profiles(model_truth, P, "A3", target)
    T_six, X_six = ef.load_profiles(model_six, P, "A3", target)
    expected = list(model_six["chemical_species"])
    print(
        f"[input] wl={wl.size} P={P.size} T={T_truth.shape} "
        f"X_truth={X_truth.shape} X_six={X_six.shape}"
    )
    print(f"[species] full={model_truth['chemical_species']} six={expected}")
    if not np.allclose(T_truth, T_six, rtol=0, atol=1e-8):
        raise ValueError("True PT differs between model species lists")
    profiles = {}
    for hours in HOURS:
        profiles[hours] = load_retrieved_profiles(hours, P, expected)
        T_retr, X_retr, radius_retr = profiles[hours]
        print(
            f"[{hours} h] T={T_retr.shape} X={X_retr.shape} "
            f"R_p_ref={radius_retr / R_E:.6f} R_E"
        )
        if X_retr.shape != X_six.shape:
            raise ValueError(f"Retrieved X shape {X_retr.shape} != {X_six.shape}")
    if args.setup_only:
        return

    print("[opacities] loading full seven-species model", flush=True)
    star = ef.build_star(wl, target)
    planet = ef.build_planet(target)
    opac_truth = ef.read_opacities_for(model_truth, wl)
    reproduced = evaluate(
        planet, star, model_truth, opac_truth, wl, P, P_surf, P_ref,
        radius_truth, T_truth, X_truth,
    )
    baseline_error = float(
        np.max(np.abs((reproduced - original_flux) / original_flux))
    )
    print(f"[validation] full A3 forward max relative error={baseline_error:.3e}",
          flush=True)
    if baseline_error > 1e-7:
        raise ValueError("Recomputed full A3 differs from saved forward")
    full_no_surface_flux = evaluate(
        planet, star, model_full_no_surface, opac_truth, wl, P, P_surf,
        P_ref, radius_truth, T_truth, X_truth,
    )
    del opac_truth

    print("[opacities] loading six-species model", flush=True)
    opac_six = ef.read_opacities_for(model_six, wl)
    six_true_flux = evaluate(
        planet, star, model_six, opac_six, wl, P, P_surf, P_ref,
        radius_truth, T_six, X_six,
    )
    six_surface_flux = evaluate(
        planet, star, model_six_surface, opac_six, wl, P, P_surf, P_ref,
        radius_truth, T_six, X_six,
    )
    with np.load(CAMPAIGN / "lifesim" / "life_classic_binned_products.npz") as life:
        wl_bins = np.asarray(life["wl_bins_um"], dtype=float)
    original_binned = rebin_energy_flux(wl, original_flux, wl_bins)
    full_no_surface_binned = rebin_energy_flux(
        wl, full_no_surface_flux, wl_bins
    )
    six_true_binned = rebin_energy_flux(wl, six_true_flux, wl_bins)
    six_surface_binned = rebin_energy_flux(wl, six_surface_flux, wl_bins)

    # The six-species model is the retrieval's opacity basis. For each time,
    # compare every controlled swap to the same seven-species A3 truth.
    summary = {
        "full_forward_max_relative_error": baseline_error,
        "full_species": list(model_truth["chemical_species"]),
        "retrieval_species": expected,
        "six_species_surface_true_max_relative_to_surface_false": float(
            np.max(np.abs((six_surface_flux - six_true_flux) / six_true_flux))
        ),
        "observable": "Fp_obs W m^-2 m^-1",
        "wavelength_grid": "saved original A3 forward",
        "pressure_grid": "1 to 3e-8 bar; 100 layers",
        "runs": {},
    }
    rows = []
    bin_rows = []
    plot_vectors = {}
    for hours in HOURS:
        T_retr, X_retr, radius_retr = profiles[hours]
        data = np.loadtxt(
            CAMPAIGN / "life_data" / f"LIFE_proxima_A3_{hours}h.dat", skiprows=1
        )
        if data.shape != (wl_bins.size, 4):
            raise ValueError(f"Unexpected {hours} h dataset shape")
        sigma = data[:, 3]
        name = f"proxima_A3_{hours}h_fixedP1bar_noxtol"
        stem = f"{name}_{name}"
        retrieved_spectrum = np.loadtxt(
            SAMPLES / f"{stem}_spectrum_retrieved.txt", skiprows=1
        )
        posterior_median_binned = rebin_energy_flux(
            retrieved_spectrum[:, 0], retrieved_spectrum[:, 3], wl_bins
        )
        median_offset = (original_binned - posterior_median_binned) / sigma
        plot_vectors[hours] = {"posterior_median": median_offset}
        results = {}
        for label, T_use, X_use, R_use in (
            ("full_species_truth_surface_false", T_truth, X_truth, radius_truth),
            ("six_species_truth_surface_true", T_six, X_six, radius_truth),
            ("six_species_truth", T_six, X_six, radius_truth),
            ("retrieved_T_X_R", T_retr, X_retr, radius_retr),
            ("true_T_only", T_six, X_retr, radius_retr),
            ("true_X_only", T_retr, X_six, radius_retr),
            ("true_R_only", T_retr, X_retr, radius_truth),
            ("true_T_X", T_six, X_six, radius_retr),
            ("true_T_R", T_six, X_retr, radius_truth),
            ("true_X_R", T_retr, X_six, radius_truth),
        ):
            if label == "full_species_truth_surface_false":
                binned = full_no_surface_binned
            elif label == "six_species_truth_surface_true":
                binned = six_surface_binned
            elif label == "six_species_truth":
                binned = six_true_binned
            else:
                flux = evaluate(
                    planet, star, model_six, opac_six, wl, P, P_surf, P_ref,
                    R_use, T_use, X_use,
                )
                binned = rebin_energy_flux(wl, flux, wl_bins)
            difference = (original_binned - binned) / sigma
            if not np.all(np.isfinite(difference)):
                raise ValueError(f"Non-finite residual for {hours} h/{label}")
            result = {
                "hours": hours,
                "variant": label,
                "n_bins": int(wl_bins.size),
                "chi2_to_A3_truth": float(np.dot(difference, difference)),
                "rms_sigma_to_A3_truth": float(np.sqrt(np.mean(difference**2))),
                "max_abs_sigma_to_A3_truth": float(np.max(np.abs(difference))),
                "correlation_with_posterior_median_residual": float(
                    np.corrcoef(difference, median_offset)[0, 1]
                ),
            }
            if label == "retrieved_T_X_R":
                median_difference = (binned - posterior_median_binned) / sigma
                result["chi2_to_posterior_median_spectrum"] = float(
                    np.dot(median_difference, median_difference)
                )
                result["max_abs_sigma_to_posterior_median_spectrum"] = float(
                    np.max(np.abs(median_difference))
                )
            results[label] = result
            rows.append(result)
            plot_vectors[hours][label] = difference
            for i, wavelength in enumerate(wl_bins):
                bin_rows.append({
                    "hours": hours,
                    "variant": label,
                    "bin": i,
                    "wavelength_um": float(wavelength),
                    "truth_Fp_W_m2_m": float(original_binned[i]),
                    "variant_Fp_W_m2_m": float(binned[i]),
                    "sigma_Fp_W_m2_m": float(sigma[i]),
                    "truth_minus_variant_sigma": float(difference[i]),
                    "truth_minus_posterior_median_sigma": float(median_offset[i]),
                })
            print(
                f"[{hours} h/{label}] chi2_to_A3={result['chi2_to_A3_truth']:.3f}",
                flush=True,
            )
        summary["runs"][str(hours)] = results

    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "forward_swap_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    with (OUTPUT / "forward_swap_summary.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(dict.fromkeys(key for row in rows for key in row))
        )
        writer.writeheader()
        writer.writerows(rows)
    with (OUTPUT / "forward_swap_bins.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(bin_rows[0]))
        writer.writeheader()
        writer.writerows(bin_rows)

    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["STIX Two Text", "STIXGeneral", "Times New Roman"],
        "mathtext.fontset": "stix",
    })
    fig, axes = plt.subplots(2, 1, figsize=(10.5, 7.1), sharex=True)
    styles = (
        ("posterior_median", "Posterior spectral median", PALETTE["ink_black"], "-"),
        ("full_species_truth_surface_false", "Truth PT/X, 7 species, no surface", PALETTE["rusty_spice"], "--"),
        ("six_species_truth_surface_true", "Truth PT/X, 6 species, 1 bar surface", PALETTE["deep_moss"], ":"),
        ("six_species_truth", "Truth PT/X, 6 species, no surface", PALETTE["charcoal_violet"], "-."),
    )
    for ax, hours in zip(axes, HOURS):
        for label, legend, color, linestyle in styles:
            ax.plot(
                wl_bins, plot_vectors[hours][label], label=legend,
                color=color, linestyle=linestyle, linewidth=1.65,
                marker="o", markersize=3.2,
            )
        ax.axhline(0.0, color="0.5", linewidth=0.7)
        ax.axhline(3.0, color="0.8", linewidth=0.7, linestyle="--")
        ax.axhline(-3.0, color="0.8", linewidth=0.7, linestyle="--")
        ax.set_ylabel(r"$(F_{\rm A3}-F_{\rm model})/\sigma$")
        ax.set_title(f"A3 {hours} h", loc="left")
        ax.grid(alpha=0.15)
    axes[0].legend(loc="best", fontsize=8, frameon=True)
    axes[-1].set_xlabel(r"Wavelength ($\mu$m)")
    fig.suptitle("Proxima LIFE A3 — forward-model interface audit", fontsize=15)
    fig.tight_layout()
    fig.savefig(OUTPUT / "forward_swap_residuals.png", dpi=220)
    plt.close(fig)
    print(f"[saved] {OUTPUT.relative_to(ef.REPO)}", flush=True)


if __name__ == "__main__":
    main()
