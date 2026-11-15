"""Audit Proxima A1/A3 LIFE SNR at 1/10/100 h from saved LIFEsim products.

The persisted 10 h binned product is the direct LIFEsim anchor. This script
recomputes band SNR using its per-bin noise and applies the photon-noise
sqrt(time) scaling to 1 h and 100 h. It also checks the scaled uncertainties
against the sigma columns of the existing A1/A3 LIFE datasets. It does not
draw a random realization, rerun LIFEsim, or modify any dataset/retrieval.
"""

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CAMPAIGN_OUT = (
    ROOT / "Thermal_Emission_Spectroscopy" / "outputs"
    / "life_proxima_b_earthlike_v1"
)
LIFESIM_NPZ = CAMPAIGN_OUT / "lifesim" / "life_classic_binned_products.npz"
LIFE_DATA = CAMPAIGN_OUT / "life_data"
PRIOR_DIRECT_JSON = CAMPAIGN_OUT / "tables" / "lifesim_noise_scaling_comparison.json"
TABLES = CAMPAIGN_OUT / "tables"
PLOTS = CAMPAIGN_OUT / "plots" / "audit"
STEM = "proxima_A1_A3_molecular_snr_direct_vs_scaled_1_10_100h"

SCENARIOS = ("A1", "A3")
MOLECULES = ("N2O", "NH3")
HOURS = (1.0, 10.0, 100.0)
DIRECT_ANCHOR_HOURS = 10.0
PALETTE = {"A1": "#56E3DB", "A3": "#E34F95"}
MOLECULE_STYLES = {"N2O": "-", "NH3": "--"}
BANDS_UM = {
    # Keep the diagnostic windows identical to run_life_snr_classic.py.
    "N2O": ((7.5, 8.1), (16.5, 17.5)),
    "NH3": ((9.5, 11.5),),
}
DATASET_FILES = {
    ("A1", 1.0): "LIFE_proxima_A1_1h_O2_fixedBlack1bar_official.dat",
    ("A3", 1.0): "LIFE_proxima_A3_1h_O2_fixedBlack1bar_official.dat",
    ("A1", 10.0): "LIFE_proxima_A1_10h.dat",
    ("A3", 10.0): "LIFE_proxima_A3_10h.dat",
    ("A1", 100.0): "LIFE_proxima_A1_100h_O2_fixedBlack1bar_noxtol_audit.dat",
    ("A3", 100.0): "LIFE_proxima_A3_100h.dat",
}


def band_mask(wavelength_um: np.ndarray, windows: tuple) -> np.ndarray:
    """Return bins covered by one or more inclusive wavelength windows."""
    mask = np.zeros(wavelength_um.shape, dtype=bool)
    for lower, upper in windows:
        mask |= (wavelength_um >= lower) & (wavelength_um <= upper)
    return mask


def integrated_snr(signal: np.ndarray, sigma: np.ndarray, mask: np.ndarray) -> float:
    """Return sqrt(sum((delta F/sigma)^2)) over finite selected bins."""
    selected = mask & np.isfinite(signal) & np.isfinite(sigma) & (sigma > 0)
    return float(np.sqrt(np.sum((signal[selected] / sigma[selected]) ** 2)))


def load_direct_anchor() -> tuple[dict, np.ndarray]:
    """Load the existing direct 10 h LIFEsim products and validate their grid."""
    if not LIFESIM_NPZ.is_file():
        raise FileNotFoundError(f"Missing saved direct LIFEsim anchor: {LIFESIM_NPZ}")
    data = np.load(LIFESIM_NPZ)
    if float(data["t_ref_hours"]) != DIRECT_ANCHOR_HOURS:
        raise ValueError("The saved LIFEsim binned product is not a 10 h reference.")
    wavelength_um = np.asarray(data["wl_bins_um"], dtype=float)
    if wavelength_um.size != 31:
        raise ValueError(f"Expected 31 LIFE bins; found {wavelength_um.size}.")
    return data, wavelength_um


def make_snr_rows(data: dict, wavelength_um: np.ndarray) -> list[dict]:
    """Calculate molecular SNR from the saved direct 10 h anchor and scaling."""
    rows = []
    for scenario in SCENARIOS:
        sigma_10h = np.asarray(data[f"sigma_{scenario}"], dtype=float)
        continuum_snr_10h = np.asarray(data[f"snr_{scenario}"], dtype=float)
        if sigma_10h.shape != wavelength_um.shape:
            raise ValueError(f"Unexpected sigma shape for {scenario}.")

        for molecule in MOLECULES:
            signal = np.asarray(data[f"dF_{scenario}_{molecule}"], dtype=float)
            windows = BANDS_UM[molecule]
            scopes = [("full_31_bins", np.ones_like(wavelength_um, dtype=bool))]
            scopes.extend([
                (f"{lower:.1f}-{upper:.1f}um", band_mask(wavelength_um, ((lower, upper),)))
                for lower, upper in windows
            ])
            scopes.append(("feature_union", band_mask(wavelength_um, windows)))

            for band_name, mask in scopes:
                snr_10h = integrated_snr(signal, sigma_10h, mask)
                for hours in HOURS:
                    from_10h = snr_10h * np.sqrt(hours / DIRECT_ANCHOR_HOURS)
                    # The 100 h sigma anchor is itself the validated 10 h sigma
                    # divided by sqrt(10); this is an independent algebraic path.
                    sigma_100h = sigma_10h * np.sqrt(DIRECT_ANCHOR_HOURS / 100.0)
                    snr_100h = integrated_snr(
                        signal, sigma_100h, mask
                    ) * np.sqrt(hours / 100.0)
                    rows.append({
                        "scenario": scenario,
                        "molecule": molecule,
                        "band": band_name,
                        "hours": hours,
                        "direct_anchor_hours": DIRECT_ANCHOR_HOURS,
                        "snr_direct_lifesim_10h_anchor": snr_10h,
                        "snr_scaled_from_10h": float(from_10h),
                        "snr_scaled_from_100h": float(snr_100h),
                        "relative_difference_10h_vs_100h_scaling": float(
                            from_10h / snr_100h - 1.0
                        ) if snr_100h > 0 else float("nan"),
                        "noise_sigma_factor_vs_10h": float(
                            np.sqrt(DIRECT_ANCHOR_HOURS / hours)
                        ),
                        "noise_factor_if_sqrt_omitted": float(
                            DIRECT_ANCHOR_HOURS / hours
                        ),
                        "snr_if_sqrt_omitted": float(
                            snr_10h * hours / DIRECT_ANCHOR_HOURS
                        ),
                        "interpretation": (
                            "direct LIFEsim value at 10 h; other times are expected "
                            "sqrt(time)-scaled values"
                        ),
                    })

        # Keep continuum sensitivity separate from molecular counterfactual SNR.
        continuum_snr_10h_total = float(np.sqrt(np.nansum(continuum_snr_10h ** 2)))
        for hours in HOURS:
            continuum_snr = continuum_snr_10h_total * np.sqrt(
                hours / DIRECT_ANCHOR_HOURS
            )
            rows.append({
                "scenario": scenario,
                "molecule": "continuum",
                "band": "all_31_bins",
                "hours": hours,
                "direct_anchor_hours": DIRECT_ANCHOR_HOURS,
                "snr_direct_lifesim_10h_anchor": continuum_snr_10h_total,
                "snr_scaled_from_10h": float(continuum_snr),
                "snr_scaled_from_100h": float(continuum_snr),
                "relative_difference_10h_vs_100h_scaling": 0.0,
                "noise_sigma_factor_vs_10h": float(
                    np.sqrt(DIRECT_ANCHOR_HOURS / hours)
                ),
                "noise_factor_if_sqrt_omitted": float(
                    DIRECT_ANCHOR_HOURS / hours
                ),
                "snr_if_sqrt_omitted": float(
                    continuum_snr_10h_total * hours / DIRECT_ANCHOR_HOURS
                ),
                "interpretation": (
                    "continuum diagnostic; direct LIFEsim value at 10 h, "
                    "other times expected sqrt(time)-scaled"
                ),
            })
    return rows


def compare_dataset_sigmas(data: dict, wavelength_um: np.ndarray) -> list[dict]:
    """Check dataset sigma columns against scaled direct 10 h LIFEsim sigma."""
    h_planck = 6.62607015e-34
    c_light = 2.99792458e8
    rows = []
    for (scenario, hours), filename in DATASET_FILES.items():
        path = LIFE_DATA / filename
        if not path.is_file():
            raise FileNotFoundError(f"Missing {scenario} {hours:g} h dataset: {path}")
        dataset = np.loadtxt(path, skiprows=1)
        if dataset.shape != (wavelength_um.size, 4):
            raise ValueError(f"Expected 31x4 data in {path}; got {dataset.shape}.")
        if not np.allclose(dataset[:, 0], wavelength_um, rtol=1e-5, atol=0.0):
            raise ValueError(f"Wavelength grid differs from direct LIFE bins in {path}.")

        sigma_10h_ph = np.asarray(data[f"sigma_{scenario}"], dtype=float)
        # Convert photon-flux-density uncertainty to energy flux-density units.
        photon_energy = h_planck * c_light / (wavelength_um * 1e-6)
        sigma_10h_energy = sigma_10h_ph * photon_energy
        expected = sigma_10h_energy * np.sqrt(DIRECT_ANCHOR_HOURS / hours)
        ratio = dataset[:, 3] / expected
        rows.append({
            "scenario": scenario,
            "hours": hours,
            "dataset_file": filename,
            "n_bins": int(dataset.shape[0]),
            "expected_sigma_factor_vs_10h": float(
                np.sqrt(DIRECT_ANCHOR_HOURS / hours)
            ),
            "median_dataset_over_lifesim_scaled_sigma": float(np.median(ratio)),
            "max_abs_fractional_difference": float(np.max(np.abs(ratio - 1.0))),
            "note": "difference is consistent with six-significant-digit .dat rounding",
        })
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_plot(snr_rows: list[dict], sigma_rows: list[dict]) -> tuple[Path, Path]:
    """Plot expected molecular SNR and relative per-bin noise vs time."""
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["STIX Two Text", "STIXGeneral", "Times New Roman"],
        "mathtext.fontset": "stix",
    })
    figure, (ax_snr, ax_noise) = plt.subplots(
        2, 1, figsize=(8.0, 6.5), sharex=True,
        gridspec_kw={"height_ratios": [1.4, 0.85]},
    )

    for scenario in SCENARIOS:
        for molecule in MOLECULES:
            selected = [
                row for row in snr_rows
                if row["scenario"] == scenario
                and row["molecule"] == molecule
                and row["band"] == "full_31_bins"
            ]
            selected.sort(key=lambda row: row["hours"])
            times = np.asarray([row["hours"] for row in selected])
            predicted = np.asarray([row["snr_scaled_from_10h"] for row in selected])
            color = PALETTE[scenario]
            linestyle = MOLECULE_STYLES[molecule]
            ax_snr.plot(
                times, predicted, color=color, linestyle=linestyle,
                linewidth=1.8, marker="o", markersize=4.8,
                label=f"{scenario} {molecule}",
            )
            anchor = selected[1]
            ax_snr.scatter(
                [DIRECT_ANCHOR_HOURS], [anchor["snr_direct_lifesim_10h_anchor"]],
                marker="o", s=36, color=color, edgecolor="black", linewidth=0.45,
                zorder=4,
            )

    ax_snr.set_xscale("log")
    ax_snr.set_yscale("log")
    ax_snr.set_ylabel("Molecular band S/N (diagonal $\\sigma$)")
    ax_snr.set_title("Proxima LIFE: direct 10 h LIFEsim anchor and $\\sqrt{t}$ scaling")
    ax_snr.grid(which="both", alpha=0.18, linestyle=":")
    ax_snr.legend(frameon=False, ncol=2, fontsize=9)

    times = np.asarray(HOURS)
    sigma_factor = np.sqrt(DIRECT_ANCHOR_HOURS / times)
    sigma_without_root = DIRECT_ANCHOR_HOURS / times
    ax_noise.plot(
        times, sigma_factor, color="#3F633E", marker="s", linewidth=1.8,
        label=r"Correct: $\sigma\propto t^{-1/2}$",
    )
    ax_noise.plot(
        times, sigma_without_root, color="0.4", marker="x", linestyle="--",
        linewidth=1.3, label=r"Wrong: $\sigma\propto t^{-1}$",
    )
    for scenario, marker in (("A1", "o"), ("A3", "D")):
        selected = [row for row in sigma_rows if row["scenario"] == scenario]
        selected.sort(key=lambda row: row["hours"])
        ax_noise.scatter(
            [row["hours"] for row in selected],
            [
                row["expected_sigma_factor_vs_10h"]
                * row["median_dataset_over_lifesim_scaled_sigma"]
                for row in selected
            ],
            marker=marker, s=34, color=PALETTE[scenario], edgecolor="black",
            linewidth=0.35, label=f"{scenario} dataset $\\sigma$",
            zorder=4,
        )
    ax_noise.set_xscale("log")
    ax_noise.set_yscale("log")
    ax_noise.set_xticks(times, labels=["1", "10", "100"])
    ax_noise.set_xlabel("Integration time [h]")
    ax_noise.set_ylabel(r"$\sigma(t)/\sigma(10\,h)$")
    ax_noise.grid(which="both", alpha=0.18, linestyle=":")
    ax_noise.set_ylim(0.08, 15.0)
    ax_noise.legend(frameon=False, fontsize=7.5, ncol=2)
    figure.text(
        0.5, 0.012,
        "Top: full-grid molecular S/N; feature-window S/N is in the CSV. "
        "1 h/100 h are scaled expectations, not new direct calls or realizations.",
        ha="center", va="bottom", fontsize=7.4, color="0.35",
    )
    figure.tight_layout(rect=(0.0, 0.045, 1.0, 1.0))

    PLOTS.mkdir(parents=True, exist_ok=True)
    png_path = PLOTS / f"{STEM}.png"
    pdf_path = PLOTS / f"{STEM}.pdf"
    figure.savefig(png_path, dpi=240, bbox_inches="tight")
    figure.savefig(pdf_path, bbox_inches="tight")
    plt.close(figure)
    return png_path, pdf_path


def main() -> None:
    data, wavelength_um = load_direct_anchor()
    snr_rows = make_snr_rows(data, wavelength_um)
    sigma_rows = compare_dataset_sigmas(data, wavelength_um)
    snr_path = TABLES / f"{STEM}.csv"
    sigma_path = TABLES / f"{STEM}_dataset_sigma_validation.csv"
    write_csv(snr_path, snr_rows)
    write_csv(sigma_path, sigma_rows)
    png_path, pdf_path = write_plot(snr_rows, sigma_rows)

    with PRIOR_DIRECT_JSON.open("r", encoding="utf-8") as stream:
        prior_direct = json.load(stream)
    summary = {
        "campaign": "life_proxima_b_earthlike_v1",
        "scenarios": list(SCENARIOS),
        "molecules": list(MOLECULES),
        "integration_hours": list(HOURS),
        "direct_lifesim_anchor_hours": DIRECT_ANCHOR_HOURS,
        "direct_lifesim_calls_performed_in_this_audit": False,
        "direct_anchor_file": str(LIFESIM_NPZ.relative_to(ROOT)),
        "method": (
            "Use persisted 10 h direct LIFEsim per-bin sigma and full-minus-reset "
            "molecular contrasts. Predict 1 h and 100 h using SNR(t)=SNR(10h)*sqrt(t/10h) "
            "and sigma(t)=sigma(10h)*sqrt(10h/t); independently check actual dataset "
            "sigma columns after photon-to-energy conversion. No random realization is drawn."
        ),
        "direct_scaling_validation_previous_audit": {
            "source": "lifesim_noise_scaling_comparison.json",
            "lifesim_version": prior_direct.get("lifesim_version"),
            "spectres_version": prior_direct.get("spectres_version"),
            "scenarios_tested_directly": prior_direct.get("scenarios"),
            "hours_tested_directly": prior_direct.get("hours"),
            "max_sigma_fractional_abs_difference": prior_direct.get(
                "max_sigma_fractional_abs_difference"
            ),
            "max_paired_noise_difference_sigma": prior_direct.get(
                "max_paired_noise_difference_sigma"
            ),
            "scope_note": (
                "Prior fresh direct calls validate A0/A3 scene scaling; this audit's "
                "current A1/A3 molecular values use the saved direct 10 h anchor."
            ),
        },
        "dataset_sigma_validation": sigma_rows,
        "maximum_dataset_sigma_fractional_difference": max(
            row["max_abs_fractional_difference"] for row in sigma_rows
        ),
        "maximum_abs_fractional_snr_difference_between_10h_and_100h_scaling": max(
            abs(row["relative_difference_10h_vs_100h_scaling"])
            for row in snr_rows
        ),
        "canonical_8of8_modified": False,
        "files": {
            "snr_csv": str(snr_path.relative_to(ROOT)),
            "dataset_sigma_csv": str(sigma_path.relative_to(ROOT)),
            "png": str(png_path.relative_to(ROOT)),
            "pdf": str(pdf_path.relative_to(ROOT)),
        },
        "snr_rows": snr_rows,
    }
    json_path = TABLES / f"{STEM}.json"
    with json_path.open("w", encoding="utf-8") as stream:
        json.dump(summary, stream, indent=2)

    print(f"[direct anchor] {LIFESIM_NPZ.relative_to(ROOT)} ({DIRECT_ANCHOR_HOURS:g} h)")
    print("[expected molecular SNR] 10 h direct anchor; compare full grid and feature windows")
    for row in snr_rows:
        if row["band"] in ("full_31_bins", "feature_union"):
            print(
                f"  {row['scenario']} {row['molecule']} {row['hours']:g} h: "
                f"from10h={row['snr_scaled_from_10h']:.6g}, "
                f"from100h={row['snr_scaled_from_100h']:.6g}, "
                f"if-no-root={row['snr_if_sqrt_omitted']:.6g}"
            )
    print("[dataset sigma validation]")
    for row in sigma_rows:
        print(
            f"  {row['scenario']} {row['hours']:g} h: "
            f"median ratio={row['median_dataset_over_lifesim_scaled_sigma']:.9g}, "
            f"max |fractional difference|={row['max_abs_fractional_difference']:.3e}"
        )
    print(f"[json] {json_path.relative_to(ROOT)}")
    print(f"[plot] {png_path.relative_to(ROOT)}")
    print(f"[plot] {pdf_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
