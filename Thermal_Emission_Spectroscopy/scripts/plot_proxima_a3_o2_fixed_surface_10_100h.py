"""Compare recovered corrected-interface A3 posteriors at 10 and 100 h.

This audit consumes existing POSEIDON/MultiNest products only. It does not
launch likelihood evaluations. Residuals are evaluated against each time's
own 31-bin LIFE dataset and its own diagonal uncertainties.
"""

from __future__ import annotations

import csv
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "Transmission_Spectroscopy" / "notebooks"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_proxima_a3_retrieval_residuals import rebin_energy_flux
from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE
from retrieval_reference import log10_column_averaged_mixing_ratio


CAMPAIGN = REPO / "Thermal_Emission_Spectroscopy" / "outputs" / "life_proxima_b_earthlike_v1"
PRODUCTS = (
    CAMPAIGN / "retrievals" / "POSEIDON_output" / "proxima_b_earthlike" / "retrievals"
)
DATA_DIR = CAMPAIGN / "life_data"
RAW_DIR = PRODUCTS / "MultiNest_raw"
RESULTS_DIR = PRODUCTS / "results"
SAMPLES_DIR = PRODUCTS / "samples"
PLOTS_DIR = CAMPAIGN / "plots"
TABLES_DIR = CAMPAIGN / "tables"
FORWARD_FILE = CAMPAIGN / "forward_emission" / "A3_emission.npz"
PROFILE_FILES = {
    "A0": REPO / "Transmission_Spectroscopy" / "profiles" / "Proxima_b_A0_PreAgri_chem.txt",
    "A3": REPO / "Transmission_Spectroscopy" / "profiles" / "Proxima_b_A3_Extreme_chem.txt",
}
RUNS = {
    10: {
        "tag": "proxima_A3_10h_O2_fixedBlack1bar_noxtol",
        "rows": 6972,
        "raw_suffix": "-post_equal_weights.d",
        "color": PALETTE["terracotta_mauve"],
    },
    100: {
        "tag": "proxima_A3_100h_O2_fixedBlack1bar_noxtol",
        "rows": 7479,
        "raw_suffix": "-post_equal_weights",
        "color": PALETTE["charcoal_violet"],
    },
}
MOLECULES = ("N2O", "NH3")
MOLECULE_LABELS = {"N2O": r"N$_2$O", "NH3": r"NH$_3$"}
OUTPUT_STEM = "retrieval_A3_10_vs_100h_o2_fixed_surface_proxima"

mpl.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["STIX Two Text", "STIXGeneral", "Times New Roman"],
        "mathtext.fontset": "stix",
        "axes.unicode_minus": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.8,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.top": True,
        "ytick.right": True,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_finite(path: Path, *, skiprows: int = 0) -> np.ndarray:
    if not path.is_file() or path.stat().st_size == 0:
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    if re.search(r"(?i)(?<![a-z])(?:nan|inf(?:inity)?)(?![a-z])", text):
        raise ValueError(f"NaN/Inf token in {path}")
    array = np.loadtxt(path, skiprows=skiprows, ndmin=2)
    if array.size == 0 or not np.isfinite(array).all():
        raise ValueError(f"Empty or non-finite numeric data in {path}")
    return array


def product_stem(tag: str) -> str:
    return f"{tag}_{tag}"


def load_result(tag: str) -> dict[str, float | int]:
    path = RESULTS_DIR / f"{product_stem(tag)}_results.txt"
    text = path.read_text(encoding="utf-8", errors="replace")
    if re.search(r"(?i)(?<![a-z])(?:nan|inf(?:inity)?)(?![a-z])", text):
        raise ValueError(f"NaN/Inf token in retrieval results {path}")
    patterns = {
        "ln_Z": r"->\s*ln Z\s*=\s*([+-]?[\d.]+(?:[eE][+-]?\d+)?)",
        "ln_Z_error": r"->\s*ln Z\s*=\s*[+-]?[\d.]+(?:[eE][+-]?\d+)?\s*\+/-\s*([\d.]+(?:[eE][+-]?\d+)?)",
        "chi2_red": r"->\s*chi\^2_red\s*=\s*([\d.]+(?:[eE][+-]?\d+)?)",
        "dof": r"->\s*degrees of freedom\s*=\s*(\d+)",
        "chi2": r"->\s*chi\^2\s*=\s*([\d.]+(?:[eE][+-]?\d+)?)",
    }
    found: dict[str, float | int] = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match is None:
            raise ValueError(f"Missing {key} in {path}")
        found[key] = int(match.group(1)) if key == "dof" else float(match.group(1))
    if "N_params = 15" not in text or "N_live = 800" not in text:
        raise ValueError(f"Unexpected retrieval configuration in {path}")
    return found


def load_run(hours: int, config: dict[str, object]) -> dict[str, object]:
    tag = str(config["tag"])
    stem = product_stem(tag)
    manifest_path = RESULTS_DIR / f"{stem}_postprocess_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    raw_path = RAW_DIR / f"{stem}{config['raw_suffix']}"
    raw_hash = sha256(raw_path)
    if raw_hash != manifest["raw_sample_sha256"]:
        raise ValueError(f"Raw MultiNest hash mismatch for {hours} h")
    if int(manifest["sample_rows"]) != int(config["rows"]):
        raise ValueError(f"Unexpected raw sample count in manifest for {hours} h")
    dat_copy = RAW_DIR / f"{stem}-post_equal_weights.dat"
    if sha256(dat_copy) != raw_hash:
        raise ValueError(f"Analyzer .dat copy is not byte-identical to raw sample for {hours} h")
    config_record = manifest["configuration"]
    if (
        config_record.get("X_profile") != "isochem"
        or config_record.get("N_live") != 800
        or config_record.get("error_inflation") != "none"
        or config_record.get("x_tol") != "absent"
        or config_record.get("R") != 10000
        or "log_P_surf=0" not in config_record.get("surface", "")
    ):
        raise ValueError(f"Post-processing manifest configuration mismatch for {hours} h")

    sample_path = SAMPLES_DIR / f"{stem}_samples.txt"
    sample_text = sample_path.read_text(encoding="utf-8", errors="replace")
    if re.search(r"(?i)(?<![a-z])(?:nan|inf(?:inity)?)(?![a-z])", sample_text):
        raise ValueError(f"NaN/Inf token in posterior {sample_path}")
    header = [name.strip() for name in sample_text.splitlines()[0].split("|")]
    samples = require_finite(sample_path, skiprows=1)
    if samples.shape != (int(config["rows"]), len(header)):
        raise ValueError(f"Posterior table dimensions changed: {samples.shape}")
    columns = {name: i for i, name in enumerate(header)}
    required = {"R_p_ref", "log_N2O", "log_NH3", "log_O2", "log_P_surf"}
    if not required.issubset(columns):
        raise ValueError(f"Posterior missing columns: {required - set(columns)}")
    if not np.allclose(samples[:, columns["log_P_surf"]], 0.0, rtol=0.0, atol=1e-12):
        raise ValueError(f"Surface pressure is not fixed at 1 bar for {hours} h")

    posterior: dict[str, np.ndarray] = {}
    for molecule in MOLECULES:
        posterior[molecule] = samples[:, columns[f"log_{molecule}"]]
    quantiles = {
        parameter: {
            "q16": float(np.percentile(samples[:, columns[parameter]], 16)),
            "median": float(np.percentile(samples[:, columns[parameter]], 50)),
            "q84": float(np.percentile(samples[:, columns[parameter]], 84)),
        }
        for parameter in ("R_p_ref", "log_N2O", "log_NH3", "log_O2")
    }
    for entry in quantiles.values():
        entry["sigma68"] = 0.5 * (entry["q84"] - entry["q16"])

    spectrum_path = SAMPLES_DIR / f"{stem}_spectrum_retrieved.txt"
    spectrum = require_finite(spectrum_path, skiprows=1)
    if spectrum.shape[1] != 6:
        raise ValueError(f"Unexpected recovered spectrum shape {spectrum.shape}")
    pt_path = SAMPLES_DIR / f"{stem}_PT_retrieved.txt"
    pt = require_finite(pt_path, skiprows=1)
    if pt.shape != (100, 6):
        raise ValueError(f"Unexpected recovered P--T shape {pt.shape}")
    log_x_path = SAMPLES_DIR / f"{stem}_log_X_retrieved.txt"
    log_x_text = log_x_path.read_text(encoding="utf-8", errors="replace")
    if re.search(r"(?i)(?<![a-z])(?:nan|inf(?:inity)?)(?![a-z])", log_x_text):
        raise ValueError(f"NaN/Inf token in retrieved log-X {log_x_path}")
    log_x_rows = []
    for line in log_x_text.splitlines():
        fields = line.split()
        if not fields:
            continue
        try:
            float(fields[0])
        except ValueError:
            continue
        row = np.asarray([float(value) for value in fields], dtype=float)
        if row.shape != (6,) or not np.isfinite(row).all():
            raise ValueError(f"Malformed log-X row in {log_x_path}: {line}")
        log_x_rows.append(row)
    if len(log_x_rows) != 800:
        raise ValueError(f"Expected 800 numeric log-X rows for {hours} h")
    data_path = DATA_DIR / f"LIFE_proxima_A3_{hours}h.dat"
    data = require_finite(data_path, skiprows=1)
    if data.shape != (31, 4) or np.any(data[:, 3] <= 0):
        raise ValueError(f"Invalid LIFE {hours} h dataset: {data.shape}")
    if np.any(np.diff(data[:, 0]) <= 0):
        raise ValueError(f"Non-monotonic LIFE wavelengths in {data_path}")
    if sha256(data_path) != manifest["dataset_sha256"]:
        raise ValueError(f"Dataset hash differs from post-processing manifest for {hours} h")

    with np.load(FORWARD_FILE) as forward:
        truth = rebin_energy_flux(
            np.asarray(forward["wl_um"], dtype=float),
            np.asarray(forward["Fp_obs_W_m2_m"], dtype=float),
            data[:, 0],
        )
    median_flux = rebin_energy_flux(spectrum[:, 0], spectrum[:, 3], data[:, 0])
    residual = (data[:, 2] - median_flux) / data[:, 3]
    noise_residual = (data[:, 2] - truth) / data[:, 3]
    model_offset = (truth - median_flux) / data[:, 3]
    if not np.allclose(residual, noise_residual + model_offset, rtol=0.0, atol=1e-10):
        raise ValueError(f"Residual/noise/model decomposition failed at {hours} h")

    return {
        "hours": hours,
        "tag": tag,
        "raw_sample": str(raw_path),
        "raw_sha256": raw_hash,
        "manifest": str(manifest_path),
        "dataset": str(data_path),
        "dataset_sha256": sha256(data_path),
        "posterior_file": str(sample_path),
        "posterior_sha256": sha256(sample_path),
        "posterior_rows": samples.shape[0],
        "posterior": posterior,
        "quantiles": quantiles,
        "result": load_result(tag),
        "spectrum_file": str(spectrum_path),
        "spectrum_sha256": sha256(spectrum_path),
        "pt_shape": list(pt.shape),
        "log_x_numeric_rows": len(log_x_rows),
        "data": data,
        "truth_flux": truth,
        "median_flux": median_flux,
        "residual_sigma": residual,
        "noise_only_sigma": noise_residual,
        "median_residual_chi2": float(np.dot(residual, residual)),
        "median_residual_rms_sigma": float(np.sqrt(np.mean(residual**2))),
        "median_residual_bins_over_3sigma": int(np.count_nonzero(np.abs(residual) > 3.0)),
    }


def effective_references() -> dict[str, dict[str, float]]:
    profiles = {key: np.genfromtxt(path, names=True) for key, path in PROFILE_FILES.items()}
    return {
        scenario: {
            molecule: float(log10_column_averaged_mixing_ratio(profile, molecule))
            for molecule in MOLECULES
        }
        for scenario, profile in profiles.items()
    }


def posterior_z(quantiles: dict[str, float], reference: float) -> float:
    sigma68 = float(quantiles["sigma68"])
    return (float(quantiles["median"]) - reference) / sigma68


def draw_posteriors(ax: plt.Axes, products: dict[int, dict[str, object]], molecule: str,
                    references: dict[str, dict[str, float]]) -> None:
    arrays = [products[hours]["posterior"][molecule] for hours in products]
    low = min(float(np.percentile(values, 0.5)) for values in arrays)
    high = max(float(np.percentile(values, 99.5)) for values in arrays)
    low = min(low, references["A0"][molecule], references["A3"][molecule]) - 0.18
    high = max(high, references["A0"][molecule], references["A3"][molecule]) + 0.18
    edges = np.linspace(low, high, 66)
    for hours, product in products.items():
        values = product["posterior"][molecule]
        density, _ = np.histogram(values, bins=edges, density=True)
        color = RUNS[hours]["color"]
        z_value = product["z_descriptive"][molecule]
        ax.stairs(
            density,
            edges,
            color=color,
            linewidth=2.0,
            label=f"{hours} h ($z_{{A0}}={z_value:+.2f}$)",
        )
        ax.fill_between(edges[:-1], density, step="post", color=color, alpha=0.12)
        median = product["quantiles"][f"log_{molecule}"]["median"]
        ax.axvline(median, color=color, linewidth=1.0)
    ax.axvline(references["A0"][molecule], color=PALETTE["deep_moss"],
               linestyle=":", linewidth=1.7, label="A0 efectiva")
    ax.axvline(references["A3"][molecule], color=PALETTE["dark_amaranth"],
               linestyle="-.", linewidth=1.5, label="A3 efectiva")
    ax.set_xlim(low, high)
    ax.set_xlabel(r"$\log_{10}$ VMR isochem")
    ax.set_ylabel("Densidad posterior")
    ax.set_title(f"{MOLECULE_LABELS[molecule]} — distribución marginal")
    ax.grid(axis="y", linestyle=":", alpha=0.28)
    ax.minorticks_on()
    ax.tick_params(direction="in", top=True, right=True, labelsize=8.5)


def draw_residual(ax: plt.Axes, product: dict[str, object]) -> None:
    data = product["data"]
    hours = int(product["hours"])
    color = RUNS[hours]["color"]
    ax.axhline(0.0, color=PALETTE["dim_grey"], lw=0.8)
    ax.axhline(3.0, color=PALETTE["scenario_pink"], ls="--", lw=0.9, alpha=0.7)
    ax.axhline(-3.0, color=PALETTE["scenario_pink"], ls="--", lw=0.9, alpha=0.7)
    ax.plot(data[:, 0], product["noise_only_sigma"], color=PALETTE["dim_grey"],
            marker="o", ms=3.2, lw=1.0, alpha=0.75, label="Realización − forward A3")
    ax.plot(data[:, 0], product["residual_sigma"], color=color,
            marker="s", ms=3.5, lw=1.25, label="Datos − mediana recuperada")
    ax.set_xlim(float(data[0, 0]) - 0.25, float(data[-1, 0]) + 0.25)
    ax.set_xlabel("Longitud de onda [µm]")
    ax.set_ylabel(r"Residuo / $\sigma_{diag}$")
    result = product["result"]
    ax.set_title(
        f"{hours} h — 31 bins propios, {result['dof']} dof; $\\chi^2_{{red, best}}$="
        f"{result['chi2_red']:.2f}; RMS mediana="
        f"{product['median_residual_rms_sigma']:.2f} $\\sigma$"
    )
    ax.grid(axis="y", linestyle=":", alpha=0.28)
    ax.minorticks_on()
    ax.tick_params(direction="in", top=True, right=True, labelsize=8.5)


def make_figure(products: dict[int, dict[str, object]],
                references: dict[str, dict[str, float]],
                overwrite: bool) -> tuple[Path, Path]:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    png = PLOTS_DIR / f"{OUTPUT_STEM}.png"
    pdf = PLOTS_DIR / f"{OUTPUT_STEM}.pdf"
    if (png.exists() or pdf.exists()) and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing figure: {png} / {pdf}")
    fig, axes = plt.subplots(2, 2, figsize=(12.2, 8.1), constrained_layout=True)
    for ax, molecule in zip(axes[0], MOLECULES):
        draw_posteriors(ax, products, molecule, references)
    draw_residual(axes[1, 0], products[10])
    draw_residual(axes[1, 1], products[100])
    axes[0, 0].legend(frameon=True, fontsize=8, loc="upper left")
    axes[1, 0].legend(frameon=True, fontsize=7.6, loc="best")
    fig.suptitle(
        "Proxima b — A3 corregido: posteriores isochem y ajuste por tiempo\n"
        "O$_2$ + superficie negra fija a 1 bar; distancias a A0 descriptivas",
        fontsize=13,
    )
    fig.savefig(png, dpi=300, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    plt.close(fig)
    return png, pdf


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace this script's own summary/figure outputs after revalidation",
    )
    args = parser.parse_args()
    summary_path = TABLES_DIR / f"{OUTPUT_STEM}_summary.json"
    residual_path = TABLES_DIR / f"{OUTPUT_STEM}_residuals.csv"
    if (summary_path.exists() or residual_path.exists()) and not args.overwrite:
        raise FileExistsError(f"Refusing to overwrite existing audit table: {summary_path}")

    products = {hours: load_run(hours, config) for hours, config in RUNS.items()}
    references = effective_references()
    for hours, product in products.items():
        product["z_descriptive"] = {
            molecule: posterior_z(
                product["quantiles"][f"log_{molecule}"], references["A0"][molecule]
            )
            for molecule in MOLECULES
        }

    png, pdf = make_figure(products, references, overwrite=args.overwrite)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    summary = {
        "question": "Corrected-interface Proxima A3 LIFE retrieval comparison at 10 and 100 h",
        "configuration": {
            "X_profile": "isochem",
            "species": ["H2O", "CO2", "CH4", "O2", "O3", "N2O", "NH3"],
            "N_live": 800,
            "error_inflation": "none",
            "x_tol": "absent",
            "surface": "explicit black surface; log_P_surf=0 (1 bar)",
            "R": 10000,
            "noise_model": "classic LIFE diagonal uncertainties; one realization per integration time",
        },
        "references_log10_vmr": references,
        "runs": {},
        "figure": {"png": str(png), "pdf": str(pdf)},
        "interpretation_limit": (
            "Posterior distances z=(median-A0_effective)/sigma68 are descriptive conditional summaries, "
            "not formal detection significances. The 10 h and 100 h datasets are different realizations; "
            "their ln Z values must not be compared as Bayes factors. A3 retrieval abundances are isochemical "
            "while the simulated atmosphere is vertically structured by VULCAN."
        ),
    }
    for hours, product in products.items():
        summary["runs"][str(hours)] = {
            "tag": product["tag"],
            "dataset": product["dataset"],
            "dataset_sha256": product["dataset_sha256"],
            "raw_equal_weight_sample": product["raw_sample"],
            "raw_sha256": product["raw_sha256"],
            "posterior_file": product["posterior_file"],
            "posterior_sha256": product["posterior_sha256"],
            "posterior_rows": product["posterior_rows"],
            "result": product["result"],
            "posterior_quantiles": product["quantiles"],
            "z_descriptive_vs_A0_effective": product["z_descriptive"],
            "spectrum_file": product["spectrum_file"],
            "spectrum_sha256": product["spectrum_sha256"],
            "median_spectrum_residual_chi2_own_bins": product["median_residual_chi2"],
            "median_spectrum_residual_rms_sigma_own_bins": product["median_residual_rms_sigma"],
            "median_spectrum_residual_bins_over_3sigma_own_bins": product["median_residual_bins_over_3sigma"],
        }
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    with residual_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["hours", "wavelength_um", "observed_Fp", "sigma_Fp_diagonal", "A3_truth_Fp",
             "noise_only_sigma", "median_retrieval_residual_sigma"]
        )
        for hours, product in products.items():
            data = product["data"]
            for index, row in enumerate(data):
                writer.writerow(
                    [hours, f"{row[0]:.9f}", f"{row[2]:.12e}", f"{row[3]:.12e}",
                     f"{product['truth_flux'][index]:.12e}",
                     f"{product['noise_only_sigma'][index]:.8f}",
                     f"{product['residual_sigma'][index]:.8f}"]
                )

    for hours, product in products.items():
        print(
            f"{hours} h: lnZ={product['result']['ln_Z']:.2f}±{product['result']['ln_Z_error']:.2f}; "
            f"chi2red={product['result']['chi2_red']:.2f} (dof={product['result']['dof']}); "
            f"Rp_ref={product['quantiles']['R_p_ref']['median']:.4f} R_E; "
            f"logN2O={product['quantiles']['log_N2O']['median']:.4f}; "
            f"logNH3={product['quantiles']['log_NH3']['median']:.4f}; "
            f"zN2O={product['z_descriptive']['N2O']:+.2f}; "
            f"zNH3={product['z_descriptive']['NH3']:+.2f}; "
            f"median-residual-rms={product['median_residual_rms_sigma']:.3f} sigma; "
            f">3sigma bins={product['median_residual_bins_over_3sigma']}"
        )
    print(f"A0 effective: N2O={references['A0']['N2O']:.6f}; NH3={references['A0']['NH3']:.6f}")
    print(f"A3 effective: N2O={references['A3']['N2O']:.6f}; NH3={references['A3']['NH3']:.6f}")
    print(f"PNG={png}\nPDF={pdf}\nSUMMARY={summary_path}\nRESIDUALS={residual_path}")


if __name__ == "__main__":
    main()
