"""Diagnose A3 LIFE retrieval residuals on the saved classic-LIFE bins.

Uses existing 10/100/240 h datasets and posterior-median spectra only. The
reported POSEIDON chi-square comes from the best fit, so the chi-square of the
rebinned pointwise posterior median is labelled separately.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
import re
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "Transmission_Spectroscopy" / "notebooks"))
from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE


CAMPAIGN = (
    REPO / "Thermal_Emission_Spectroscopy" / "outputs"
    / "life_proxima_b_earthlike_v1"
)
SAMPLES = (
    CAMPAIGN / "retrievals" / "POSEIDON_output" / "proxima_b_earthlike"
    / "retrievals" / "samples"
)
RESULTS = SAMPLES.parent / "results"
LIFE_DATA = CAMPAIGN / "life_data"
PLOTS = CAMPAIGN / "plots"
TABLES = CAMPAIGN / "tables"
HOURS = (10, 100, 240)
H_PLANCK = 6.62607015e-34
C_LIGHT = 2.99792458e8
WINDOWS = (
    ("N2O 7.5-8.1", 7.5, 8.1),
    ("NH3 9.5-11.5", 9.5, 11.5),
    ("N2O 16.5-17.5", 16.5, 17.5),
)
COLORS = {
    10: PALETTE["terracotta_mauve"],
    100: PALETTE["charcoal_violet"],
    240: PALETTE["rusty_spice"],
}


def bin_edges(centres: np.ndarray) -> np.ndarray:
    """Return the midpoint edges used by spectres for a centre-only grid."""
    if centres.ndim != 1 or centres.size < 2 or np.any(np.diff(centres) <= 0):
        raise ValueError("Expected a strictly increasing one-dimensional grid")
    edges = np.empty(centres.size + 1)
    edges[1:-1] = (centres[:-1] + centres[1:]) / 2.0
    edges[0] = centres[0] - (edges[1] - centres[0])
    edges[-1] = centres[-1] + (centres[-1] - edges[-2])
    return edges


def rebin_energy_flux(
    native_wl_um: np.ndarray,
    native_energy_flux: np.ndarray,
    target_wl_um: np.ndarray,
) -> np.ndarray:
    """Overlap-integrate photon density, then convert back to energy flux.

    LIFEsim bins photon density; integration directly in energy flux would
    silently change the observable. Native values are piecewise constant over
    centre-derived cells, matching the spectres convention used upstream.
    """
    native_edges = bin_edges(native_wl_um)
    target_edges = bin_edges(target_wl_um)
    photon_density = native_energy_flux * (native_wl_um * 1e-6) / (
        H_PLANCK * C_LIGHT
    )
    rebinned = np.empty(target_wl_um.size)
    for j in range(target_wl_um.size):
        left = np.maximum(native_edges[:-1], target_edges[j])
        right = np.minimum(native_edges[1:], target_edges[j + 1])
        overlap = np.maximum(right - left, 0.0)
        width = target_edges[j + 1] - target_edges[j]
        if not np.isclose(overlap.sum(), width, rtol=0, atol=1e-8):
            raise ValueError(f"Target bin {j} is not covered by native grid")
        rebinned[j] = np.dot(overlap, photon_density) / width
    return rebinned * H_PLANCK * C_LIGHT / (target_wl_um * 1e-6)


def window_label(wavelength: float) -> str:
    for label, low, high in WINDOWS:
        if low <= wavelength <= high:
            return label
    return "other"


def main() -> None:
    with np.load(CAMPAIGN / "lifesim" / "life_classic_binned_products.npz") as saved:
        wl_bins = np.asarray(saved["wl_bins_um"], dtype=float)
        binned_photons = np.asarray(saved["flux_binned_A3"], dtype=float)
        reference_energy = binned_photons * H_PLANCK * C_LIGHT / (wl_bins * 1e-6)
    with np.load(CAMPAIGN / "forward_emission" / "A3_emission.npz") as forward:
        wl_native = np.asarray(forward["wl_um"], dtype=float)
        flux_native = np.asarray(forward["Fp_obs_W_m2_m"], dtype=float)
    truth = rebin_energy_flux(wl_native, flux_native, wl_bins)
    relative_validation_error = float(
        np.max(np.abs((truth - reference_energy) / reference_energy))
    )
    if relative_validation_error > 1e-10:
        raise ValueError(
            "Rebin disagrees with the saved LIFE A3 product: "
            f"{relative_validation_error:.3e}"
        )

    rows = []
    results = {"validation_max_relative_rebin_error": relative_validation_error}
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["STIX Two Text", "STIXGeneral", "Times New Roman"],
        "mathtext.fontset": "stix",
    })
    fig, axes = plt.subplots(3, 1, figsize=(10.2, 8.5), sharex=True)
    truth_pt = np.loadtxt(
        REPO / "Transmission_Spectroscopy" / "profiles"
        / "Proxima_b_A3_Extreme_PT.txt", skiprows=1
    )
    for ax, hours in zip(axes, HOURS):
        data = np.loadtxt(LIFE_DATA / f"LIFE_proxima_A3_{hours}h.dat", skiprows=1)
        if data.shape != (wl_bins.size, 4):
            raise ValueError(f"Unexpected {hours} h dataset shape: {data.shape}")
        wl_data, half_width, observed, sigma = data.T
        max_grid_rounding = float(np.max(np.abs(wl_data - wl_bins)))
        if max_grid_rounding > 1e-5 or not np.all(np.isfinite(data)) or np.any(sigma <= 0):
            raise ValueError(f"Invalid {hours} h LIFE dataset")
        name = f"proxima_A3_{hours}h_fixedP1bar_noxtol"
        stem = f"{name}_{name}"
        result_path = RESULTS / f"{stem}_results.txt"
        result_text = result_path.read_text(encoding="utf-8")
        match = re.search(r"-> chi\^2 = ([0-9.]+)", result_text)
        if match is None:
            raise ValueError(f"Missing best-fit chi-square in {result_path}")
        best_fit_chi2 = float(match.group(1))
        spectrum = np.loadtxt(SAMPLES / f"{stem}_spectrum_retrieved.txt", skiprows=1)
        if spectrum.ndim != 2 or spectrum.shape[1] != 6:
            raise ValueError(f"Unexpected {hours} h retrieved spectrum shape")
        median_model = rebin_energy_flux(spectrum[:, 0], spectrum[:, 3], wl_bins)
        pt = np.loadtxt(SAMPLES / f"{stem}_PT_retrieved.txt", skiprows=1)
        p_probe = np.array([1.0, 0.1, 0.01, 0.001])
        true_t = np.interp(
            np.log10(p_probe), np.log10(truth_pt[:, 1][::-1]),
            truth_pt[:, 2][::-1]
        )
        retrieved_t = np.interp(
            np.log10(p_probe), np.log10(pt[:, 0][::-1]), pt[:, 3][::-1]
        )
        residual = (observed - median_model) / sigma
        model_offset = (truth - median_model) / sigma
        injected_noise = (observed - truth) / sigma
        if not np.all(np.isfinite(median_model)):
            raise ValueError(f"Non-finite {hours} h rebinned spectrum")

        chi2_median = float(np.dot(residual, residual))
        chi2_injected_noise = float(np.dot(injected_noise, injected_noise))
        chi2_model_offset = float(np.dot(model_offset, model_offset))
        by_window = {}
        for label in ("N2O 7.5-8.1", "NH3 9.5-11.5", "N2O 16.5-17.5", "other"):
            mask = np.array([window_label(w) == label for w in wl_bins])
            by_window[label] = {
                "bins": int(mask.sum()),
                "median_residual_chi2": float(np.dot(residual[mask], residual[mask])),
                "truth_minus_median_chi2": float(
                    np.dot(model_offset[mask], model_offset[mask])
                ),
            }
        top_bins = np.argsort(np.abs(residual))[-5:][::-1]
        results[str(hours)] = {
            "n_bins": int(wl_bins.size),
            "max_grid_rounding_um": max_grid_rounding,
            "median_spectrum_chi2": chi2_median,
            "median_spectrum_chi2_per_18_dof": chi2_median / 18.0,
            "reported_best_fit_chi2": best_fit_chi2,
            "reported_best_fit_chi2_per_18_dof": best_fit_chi2 / 18.0,
            "injected_noise_chi2": chi2_injected_noise,
            "truth_minus_median_chi2": chi2_model_offset,
            "n_observed_minus_median_over_3sigma": int(
                np.count_nonzero(np.abs(residual) > 3)
            ),
            "temperature_probes": [
                {
                    "pressure_bar": float(p),
                    "true_K": float(t_true),
                    "retrieved_median_K": float(t_retrieved),
                    "median_minus_true_K": float(t_retrieved - t_true),
                }
                for p, t_true, t_retrieved in zip(
                    p_probe, true_t, retrieved_t
                )
            ],
            "windows": by_window,
            "top_bins": [
                {
                    "wavelength_um": float(wl_bins[i]),
                    "residual_sigma": float(residual[i]),
                    "model_offset_sigma": float(model_offset[i]),
                    "injected_noise_sigma": float(injected_noise[i]),
                }
                for i in top_bins
            ],
            "results_file": str(result_path.relative_to(REPO)),
        }
        for i, wl in enumerate(wl_bins):
            rows.append({
                "hours": hours,
                "wavelength_um": f"{wl:.9f}",
                "half_bin_um": f"{half_width[i]:.9f}",
                "window": window_label(wl),
                "observed_Fp_W_m2_m": f"{observed[i]:.9e}",
                "true_A3_Fp_W_m2_m": f"{truth[i]:.9e}",
                "retrieved_median_Fp_W_m2_m": f"{median_model[i]:.9e}",
                "sigma_Fp_W_m2_m": f"{sigma[i]:.9e}",
                "observed_minus_median_sigma": f"{residual[i]:+.6f}",
                "truth_minus_median_sigma": f"{model_offset[i]:+.6f}",
                "injected_noise_sigma": f"{injected_noise[i]:+.6f}",
            })

        for label, low, high in WINDOWS:
            ax.axvspan(low, high, color=(
                PALETTE["rusty_spice"] if label.startswith("N2O")
                else PALETTE["charcoal_violet"]
            ), alpha=0.07, lw=0)
        ax.axhline(0, color=PALETTE["dim_grey"], lw=0.8)
        ax.plot(wl_bins, model_offset, color=COLORS[hours], lw=1.7,
                label="A3 sin ruido - mediana recuperada")
        ax.scatter(wl_bins, residual, s=20, facecolors="white",
                   edgecolors=COLORS[hours], linewidths=1.0,
                   label="Observación - mediana recuperada", zorder=4)
        ax.set_ylabel(r"Residuo / $\sigma$")
        ax.set_title(f"A3 {hours} h  |  chi2 mediana = {chi2_median:.1f} (31 bins)",
                     loc="left", fontsize=10)
        ax.grid(axis="y", alpha=0.16, linestyle=":")
        ax.legend(loc="upper right", fontsize=7.7, frameon=False)

    axes[-1].set_xlabel(r"Longitud de onda [$\mu$m]")
    axes[-1].set_xlim(float(wl_bins[0] - 0.15), float(wl_bins[-1] + 0.15))
    fig.suptitle("Proxima A3 - residuos del retrieval LIFE clásico", fontsize=14)
    fig.text(0.5, 0.012,
             "Puntos: una realización por tiempo. Línea: desplazamiento del modelo "
             "respecto al forward A3; bandas sombreadas: ventanas moleculares.",
             ha="center", fontsize=8)
    fig.tight_layout(rect=(0, 0.035, 1, 0.97))
    PLOTS.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    stem = "retrieval_A3_fixedP1bar_noxtol_residual_audit_10_100_240h"
    fig.savefig(PLOTS / f"{stem}.png", dpi=210)
    fig.savefig(PLOTS / f"{stem}.pdf")
    plt.close(fig)
    with (TABLES / f"{stem}.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (TABLES / f"{stem}.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
