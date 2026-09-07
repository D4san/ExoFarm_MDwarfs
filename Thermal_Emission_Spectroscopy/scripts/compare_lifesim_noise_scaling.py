"""Compare direct LIFEsim noise with the validated sqrt(time) scaling.

The LIFEsim classic noise model is deterministic for a fixed scene and
integration time.  The random Gaussian realization used in a POSEIDON data
file is a separate step.  This script compares both layers for the Proxima
scene, using the same forward spectra and the same paired standard-normal
draw in the direct and scaled cases.

Outputs are audit products only.  They do not modify the canonical LIFE data
or retrieval matrix.
"""

import csv
import json
from importlib.metadata import version
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import emission_forward as ef

# The project palette lives with the transmission plotting helpers, but is
# shared by the Stage-III figures as well.
STYLE_DIR = ef.REPO / "Transmission_Spectroscopy" / "notebooks"
sys.path.insert(0, str(STYLE_DIR))
from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE

from life_scene_classic import LifeSceneClassic
from validate_proxima_life_scene import (
    A_AU, D_PC, EXOZODI, R_STAR, SPEC_RES, T_STAR,
    proxima_ecliptic_lat_rad,
)

H_PLANCK = 6.62607015e-34
C_LIGHT = 2.99792458e8
CAMPAIGN_ID = "life_proxima_b_earthlike_v1"
OUT = ef.REPO / "Thermal_Emission_Spectroscopy" / "outputs" / CAMPAIGN_ID
FWD = OUT / "forward_emission"
TABLES = OUT / "tables"
PLOTS = OUT / "plots" / "audit"
SCENARIOS = ("A0", "A3")
HOURS = (1.0, 10.0, 100.0, 240.0, 500.0, 1200.0)
REFERENCE_HOURS = 10.0
MASTER_SEED = 20260831


def proxima_scene():
    """Return the calibrated LIFE-X Proxima scene used by the campaign."""
    return LifeSceneClassic(
        spec_res=SPEC_RES, diameter_m=2.0,
        temp_s=T_STAR, radius_s=R_STAR, distance_pc=D_PC,
        ecl_lat_rad=proxima_ecliptic_lat_rad(), exozodi=EXOZODI,
        angsep_arcsec=A_AU / D_PC,
    )


def compare_one(direct, reference, hours, noise_draw, ph_to_energy):
    """Return scalar comparison statistics for one scenario and time."""
    sigma_direct = np.asarray(direct["sigma_ph"])
    sigma_scaled = np.asarray(reference["sigma_ph"]) * np.sqrt(
        REFERENCE_HOURS / hours)
    flux_direct = np.asarray(direct["flux_binned_ph"])
    flux_reference = np.asarray(reference["flux_binned_ph"])
    snr_direct = np.asarray(direct["snr_per_bin"])
    snr_scaled = np.asarray(reference["snr_per_bin"]) * np.sqrt(
        hours / REFERENCE_HOURS)

    finite = (
        np.isfinite(sigma_direct) & np.isfinite(sigma_scaled)
        & (sigma_direct > 0) & (sigma_scaled > 0)
    )
    ratio = sigma_direct[finite] / sigma_scaled[finite]
    flux_mask = (
        np.isfinite(flux_direct) & np.isfinite(flux_reference)
        & (flux_reference != 0)
    )
    flux_fractional = (
        (flux_direct[flux_mask] - flux_reference[flux_mask])
        / flux_reference[flux_mask]
    )
    snr_mask = (
        np.isfinite(snr_direct) & np.isfinite(snr_scaled)
        & (snr_scaled > 0)
    )
    snr_ratio = snr_direct[snr_mask] / snr_scaled[snr_mask]

    # The data maker adds a Gaussian draw after LIFEsim has supplied sigma.
    # Reusing the same draw isolates any difference in the noise scale itself.
    flux_direct_energy = flux_direct * ph_to_energy
    flux_scaled_energy = flux_reference * ph_to_energy
    sigma_direct_energy = sigma_direct * ph_to_energy
    sigma_scaled_energy = sigma_scaled * ph_to_energy
    paired_direct = flux_direct_energy + noise_draw * sigma_direct_energy
    paired_scaled = flux_scaled_energy + noise_draw * sigma_scaled_energy
    paired_mask = finite & np.isfinite(sigma_direct_energy)
    paired_difference_sigma = (
        (paired_direct[paired_mask] - paired_scaled[paired_mask])
        / sigma_direct_energy[paired_mask]
    )

    return {
        "n_bins": int(finite.sum()),
        "median_sigma_direct_ph": float(np.median(sigma_direct[finite])),
        "median_sigma_scaled_ph": float(np.median(sigma_scaled[finite])),
        "sigma_ratio_min": float(np.min(ratio)),
        "sigma_ratio_median": float(np.median(ratio)),
        "sigma_ratio_max": float(np.max(ratio)),
        "sigma_fractional_rms": float(np.sqrt(np.mean((ratio - 1.0) ** 2))),
        "sigma_fractional_max_abs": float(np.max(np.abs(ratio - 1.0))),
        "flux_fractional_max_abs_vs_10h": float(
            np.max(np.abs(flux_fractional)) if flux_fractional.size else np.nan
        ),
        "snr_ratio_median": float(np.median(snr_ratio)),
        "snr_ratio_max_abs_from_1": float(np.max(np.abs(snr_ratio - 1.0))),
        "paired_noise_rms_sigma": float(
            np.sqrt(np.mean(paired_difference_sigma ** 2))
        ),
        "paired_noise_max_abs_sigma": float(
            np.max(np.abs(paired_difference_sigma))
        ),
    }


def write_plot(rows):
    """Write the compact audit figure comparing both noise routes."""
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["STIX Two Text", "STIXGeneral", "Times New Roman"],
        "mathtext.fontset": "stix",
    })
    colors = {"A0": PALETTE["scenario_green"],
              "A3": PALETTE["scenario_pink"]}
    fig, (ax_sigma, ax_ratio) = plt.subplots(
        2, 1, figsize=(8.2, 6.8), sharex=True,
        gridspec_kw={"height_ratios": [1.25, 1.0]},
    )

    for scen in SCENARIOS:
        selected = [r for r in rows if r["scenario"] == scen]
        t = np.array([r["hours"] for r in selected])
        direct = np.array([r["median_sigma_direct_ph"] for r in selected])
        scaled = np.array([r["median_sigma_scaled_ph"] for r in selected])
        ratio = np.array([r["sigma_ratio_median"] for r in selected])
        colour = colors[scen]
        ax_sigma.loglog(t, direct, "o-", color=colour, lw=2.2,
                        ms=5.5, label=f"{scen} direct LIFEsim")
        ax_sigma.loglog(t, scaled, "s--", color=colour, lw=1.5,
                        ms=4.2, alpha=0.75, label=f"{scen} scaled")
        ax_ratio.semilogx(t, ratio, "o-", color=colour, lw=2.0,
                          ms=5.2, label=scen)

    ax_sigma.set_ylabel(r"Median $\sigma_{F}$ [ph m$^{-2}$ s$^{-1}$ m$^{-1}$]")
    ax_sigma.set_title(r"Direct LIFEsim noise versus $\sqrt{t}$ scaling")
    ax_sigma.legend(frameon=False, ncol=2, fontsize=9)
    ax_sigma.grid(False)

    max_deviation = max(r["sigma_fractional_max_abs"] for r in rows)
    ax_ratio.axhline(1.0, color=PALETTE["dim_grey"], lw=1.1)
    ax_ratio.set_ylabel(r"Direct / scaled $\sigma$")
    ax_ratio.set_xlabel("Integration time [h]")
    ax_ratio.legend(frameon=False, ncol=2, fontsize=9)
    ax_ratio.grid(False)
    if max_deviation < 1e-10:
        ax_ratio.set_ylim(1.0 - 1e-10, 1.0 + 1e-10)
        ax_ratio.text(
            0.02, 0.08,
            "Differences below 10$^{-10}$ (floating-point precision)",
            transform=ax_ratio.transAxes, fontsize=9,
        )
    else:
        margin = max(0.01, 1.5 * max_deviation)
        ax_ratio.set_ylim(1.0 - margin, 1.0 + margin)

    fig.suptitle("Proxima LIFE classic noise audit", y=0.99, fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, 0.965))
    PLOTS.mkdir(parents=True, exist_ok=True)
    png = PLOTS / "lifesim_direct_vs_scaled_noise_proxima.png"
    pdf = PLOTS / "lifesim_direct_vs_scaled_noise_proxima.pdf"
    fig.savefig(png, dpi=240, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    plt.close(fig)
    return png, pdf


def main():
    TABLES.mkdir(parents=True, exist_ok=True)
    scene = proxima_scene()
    wl_bins_m = np.asarray(scene.wl_bins)
    ph_to_energy = H_PLANCK * C_LIGHT / wl_bins_m

    observations = {}
    for scen in SCENARIOS:
        forward = np.load(FWD / f"{scen}_emission.npz")
        observations[scen] = {
            hours: scene.observe(
                forward["wl_um"], forward["Fp_obs_W_m2_m"], hours * 3600.0
            )
            for hours in HOURS
        }

    rows = []
    rng = np.random.default_rng(MASTER_SEED)
    for scen in SCENARIOS:
        # A paired draw is used for direct/scaled at every time, while the
        # scenario-specific sequence remains reproducible.
        noise_draw = rng.normal(0.0, 1.0, size=wl_bins_m.size)
        reference = observations[scen][REFERENCE_HOURS]
        for hours in HOURS:
            metrics = compare_one(
                observations[scen][hours], reference, hours,
                noise_draw, ph_to_energy,
            )
            rows.append({"scenario": scen, "hours": hours, **metrics})

    csv_path = TABLES / "lifesim_noise_scaling_comparison.csv"
    with open(csv_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "campaign": CAMPAIGN_ID,
        "scenarios": list(SCENARIOS),
        "hours": list(HOURS),
        "reference_hours": REFERENCE_HOURS,
        "master_seed": MASTER_SEED,
        "lifesim_version": version("lifesim"),
        "spectres_version": version("spectres"),
        "scene": {
            "spec_res": SPEC_RES, "diameter_m": 2.0,
            "temp_s_K": T_STAR, "radius_s_Rsun": R_STAR,
            "distance_pc": D_PC, "exozodi": EXOZODI,
            "angsep_arcsec": A_AU / D_PC,
            "n_bins": int(wl_bins_m.size),
        },
        "comparison": (
            "direct sigma from LIFEsim at each time versus "
            "sigma(10h)*sqrt(10h/t); same paired Gaussian draw"
        ),
        "max_sigma_fractional_abs_difference": max(
            r["sigma_fractional_max_abs"] for r in rows
        ),
        "max_paired_noise_difference_sigma": max(
            r["paired_noise_max_abs_sigma"] for r in rows
        ),
        "rows": rows,
    }
    json_path = TABLES / "lifesim_noise_scaling_comparison.json"
    with open(json_path, "w") as fh:
        json.dump(summary, fh, indent=2)

    png_path, pdf_path = write_plot(rows)

    print(f"[scene] {len(wl_bins_m)} bins, Proxima LIFE X configuration")
    for row in rows:
        print(
            f"[{row['scenario']} {row['hours']:6.0f} h] "
            f"median direct/scaled sigma = {row['sigma_ratio_median']:.12g}; "
            f"max |ratio-1| = {row['sigma_fractional_max_abs']:.3e}; "
            f"paired noise max = {row['paired_noise_max_abs_sigma']:.3e} sigma"
        )
    print(f"[table] {csv_path.relative_to(ef.REPO)}")
    print(f"[json]  {json_path.relative_to(ef.REPO)}")
    print(f"[plot]  {png_path.relative_to(ef.REPO)}")
    print(f"[plot]  {pdf_path.relative_to(ef.REPO)}")


if __name__ == "__main__":
    main()
