#!/usr/bin/env python3
"""Validate completed Proxima LIFE A1 MPI6R1 retrievals and plot posteriors/PT.

This is a post-processing audit. It does not launch POSEIDON or alter the
canonical Proxima A0--A3, {10 h, 240 h} retrieval matrix.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "Transmission_Spectroscopy" / "notebooks"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE
from retrieval_reference import log10_column_averaged_mixing_ratio


CAMPAIGN = REPO / "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1"
PRODUCTS = CAMPAIGN / "retrievals/POSEIDON_output/proxima_b_earthlike/retrievals"
RESULTS_DIR = PRODUCTS / "results"
SAMPLES_DIR = PRODUCTS / "samples"
RAW_DIR = PRODUCTS / "MultiNest_raw"
LOG_DIR = CAMPAIGN / "retrievals"
DATA_DIR = CAMPAIGN / "life_data"
PROFILE_DIR = REPO / "Transmission_Spectroscopy/profiles"
PROFILE_FILES = {
    "A0": PROFILE_DIR / "Proxima_b_A0_PreAgri_chem.txt",
    "A1": PROFILE_DIR / "Proxima_b_A1_Current_chem.txt",
}
TRUE_PT_FILE = PROFILE_DIR / "Proxima_b_A1_Current_PT.txt"
RUNS = {
    10: {
        "tag": "proxima_A1_10h_O2_fixedBlack1bar_noxtol_MPI6R1",
        "dataset": "LIFE_proxima_A1_10h.dat",
        "dataset_sha256": "ed39ae6dc5b8ff0d5c8aca3d126a2945343a289be30f3b8d9e8e72c434ee9b8f",
        "color": PALETTE["deep_space_blue"],
    },
    100: {
        "tag": "proxima_A1_100h_O2_fixedBlack1bar_noxtol_MPI6R1",
        "dataset": "LIFE_proxima_A1_100h_O2_fixedBlack1bar_noxtol_audit.dat",
        "dataset_sha256": "d66c886238a2916312c645589be8601828fbf0a7cd2f02a383ef1d6a3454b5e3",
        "color": PALETTE["rusty_spice"],
    },
}
MOLECULES = ("N2O", "NH3", "O2")
MOLECULE_LABELS = {"N2O": r"N$_2$O", "NH3": r"NH$_3$", "O2": r"O$_2$"}
OUTPUT_STEM = "retrieval_A1_10_100h_MPI6R1_posteriors_PT_proxima"
NONFINITE_TOKEN = re.compile(r"(?i)(?<![A-Za-z])(?:nan|inf(?:inity)?)(?![A-Za-z])")

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


def check_text(path: Path) -> str:
    if not path.is_file() or path.stat().st_size == 0:
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    if NONFINITE_TOKEN.search(text):
        raise ValueError(f"NaN/Inf token in {path}")
    return text


def load_numeric(path: Path, *, skiprows: int = 0) -> np.ndarray:
    check_text(path)
    array = np.loadtxt(path, skiprows=skiprows, ndmin=2)
    if array.size == 0 or not np.isfinite(array).all():
        raise ValueError(f"Empty or non-finite numeric table: {path}")
    return array


def parse_result(path: Path) -> dict[str, float | int]:
    text = check_text(path)
    patterns = {
        "ln_Z": r"->\s*ln Z\s*=\s*([+-]?[\d.]+(?:[eE][+-]?\d+)?)",
        "ln_Z_error": r"->\s*ln Z\s*=\s*[+-]?[\d.]+(?:[eE][+-]?\d+)?\s*\+/-\s*([\d.]+(?:[eE][+-]?\d+)?)",
        "chi2_red": r"->\s*chi\^2_red\s*=\s*([\d.]+(?:[eE][+-]?\d+)?)",
        "dof": r"->\s*degrees of freedom\s*=\s*(\d+)",
        "chi2": r"->\s*chi\^2\s*=\s*([\d.]+(?:[eE][+-]?\d+)?)",
    }
    found: dict[str, float | int] = {}
    for name, pattern in patterns.items():
        match = re.search(pattern, text)
        if match is None:
            raise ValueError(f"Missing {name} in {path}")
        found[name] = int(match.group(1)) if name == "dof" else float(match.group(1))
    if "N_params = 15" not in text or "N_live = 800" not in text:
        raise ValueError(f"Unexpected N_params/N_live in {path}")
    best_fit_section = text.split("Best-fitting parameters", maxsplit=1)
    if len(best_fit_section) != 2:
        raise ValueError(f"Missing best-fitting parameter block in {path}")
    for key in ("R_p_ref", "log_N2O", "log_NH3", "log_O2", "log_P_surf"):
        match = re.search(
            rf"^\s*{re.escape(key)}\s*=\s*([+-]?[\d.]+(?:[eE][+-]?\d+)?)",
            best_fit_section[1],
            re.MULTILINE,
        )
        if match is None:
            raise ValueError(f"Missing best-fit {key} in {path}")
        found[f"bestfit_{key}"] = float(match.group(1))
    return found


def numeric_log_x_rows(path: Path) -> np.ndarray:
    text = check_text(path)
    rows = []
    for line in text.splitlines():
        fields = line.split()
        try:
            values = np.asarray([float(field) for field in fields], dtype=float)
        except ValueError:
            continue
        if values.size:
            if values.size != 6 or not np.isfinite(values).all():
                raise ValueError(f"Malformed numeric log-X row in {path}: {line}")
            rows.append(values)
    array = np.asarray(rows, dtype=float)
    if array.shape != (800, 6):
        raise ValueError(f"Expected 800 finite log-X rows, got {array.shape} in {path}")
    return array


def parse_resume(path: Path) -> dict[str, int]:
    lines = [line.split() for line in check_text(path).splitlines() if line.strip()]
    if len(lines) < 2 or len(lines[1]) < 4:
        raise ValueError(f"Unrecognized MultiNest resume.dat: {path}")
    replacements, evaluations, nlive = int(lines[1][0]), int(lines[1][1]), int(lines[1][3])
    if nlive != 800:
        raise ValueError(f"resume.dat has n_live={nlive}, expected 800: {path}")
    return {"replacements": replacements, "evaluations": evaluations, "n_live": nlive}


def load_run(hours: int, config: dict[str, object]) -> dict[str, object]:
    tag = str(config["tag"])
    result_path = RESULTS_DIR / f"{tag}_results.txt"
    result_text = check_text(result_path)
    if f"Model: {tag}" not in result_text:
        raise ValueError(f"Model tag mismatch in {result_path}")
    if f"LIFE ({config['dataset']})" not in result_text:
        raise ValueError(f"Dataset mismatch in {result_path}")

    log_path = LOG_DIR / f"{tag}.launch.log"
    log = check_text(log_path)
    if "Sampling finished. Exiting MultiNest" not in log or "All done!" not in log:
        raise ValueError(f"Missing MultiNest/post-processing completion marker: {log_path}")
    if f"[process_exit] PID=" not in log or "exit_code=0" not in log:
        raise ValueError(f"Missing clean process exit in {log_path}")
    for required in (
        "--resume",
        "--n-live 800",
        "--error-inflation none",
        "--surface-pressure-mode fixed-black",
        "--include-o2",
        "--x-profile isochem",
        "--R 10000",
    ):
        if required not in log:
            raise ValueError(f"Launch log lacks {required}: {log_path}")
    if "Fortran runtime error" in log or "BAD TERMINATION" in log or "Traceback" in log:
        raise ValueError(f"Failure marker in {log_path}")

    dataset_path = DATA_DIR / str(config["dataset"])
    dataset = load_numeric(dataset_path, skiprows=1)
    dataset_sha = sha256(dataset_path)
    if dataset.shape != (31, 4) or np.any(dataset[:, 3] <= 0):
        raise ValueError(f"Expected 31 LIFE bins and positive errors: {dataset_path}")
    if dataset_sha != config["dataset_sha256"]:
        raise ValueError(f"Dataset checksum changed for {hours} h: {dataset_sha}")

    raw_prefix = RAW_DIR / tag
    raw_suffixes = (
        "-.txt",
        "-ev.dat",
        "-live.points",
        "-phys_live.points",
        "-post_equal_weights.dat",
        "-resume.dat",
        "-stats.dat",
        "-summary.txt",
    )
    raw_paths = {suffix: Path(f"{raw_prefix}{suffix}") for suffix in raw_suffixes}
    raw_text = {suffix: check_text(path) for suffix, path in raw_paths.items()}
    raw_shapes: dict[str, list[int]] = {}
    for suffix in (
        "-.txt",
        "-ev.dat",
        "-live.points",
        "-phys_live.points",
        "-post_equal_weights.dat",
        "-summary.txt",
    ):
        raw_arrays = load_numeric(raw_paths[suffix])
        raw_shapes[suffix] = list(raw_arrays.shape)
        if suffix in ("-live.points", "-phys_live.points") and raw_arrays.shape[0] != 800:
            raise ValueError(f"Expected 800 live points in {raw_paths[suffix]}")
    if "Nested Sampling Global Log-Evidence" not in raw_text["-stats.dat"]:
        raise ValueError(f"MultiNest stats lacks global evidence: {raw_paths['-stats.dat']}")
    resume = parse_resume(raw_paths["-resume.dat"])
    if raw_shapes["-ev.dat"][0] != resume["replacements"] - resume["n_live"]:
        raise ValueError(f"ev.dat rows do not match the final resume checkpoint for {hours} h")
    if not re.search(rf"\b{resume['evaluations']}\b", log):
        raise ValueError(f"Final resume evaluation count is absent from the run log ({hours} h)")

    sample_path = SAMPLES_DIR / f"{tag}_samples.txt"
    sample_header = [item.strip() for item in check_text(sample_path).splitlines()[0].split("|")]
    samples = load_numeric(sample_path, skiprows=1)
    if samples.shape[1] != len(sample_header):
        raise ValueError(f"Posterior header/data width mismatch in {sample_path}")
    columns = {name: i for i, name in enumerate(sample_header)}
    required_columns = {"R_p_ref", "log_N2O", "log_NH3", "log_O2", "log_P_surf"}
    if not required_columns.issubset(columns):
        raise ValueError(f"Missing posterior columns: {required_columns - set(columns)}")
    if "x_tol" in columns:
        raise ValueError(f"Unexpected x_tol parameter in corrected retrieval for {hours} h")
    if not np.allclose(samples[:, columns["log_P_surf"]], 0.0, atol=1e-12, rtol=0.0):
        raise ValueError(f"Surface-pressure posterior is not fixed to 1 bar for {hours} h")
    raw_equal = load_numeric(raw_paths["-post_equal_weights.dat"])
    if raw_equal.shape[0] != samples.shape[0] or not np.allclose(
        samples, raw_equal[:, : samples.shape[1]], rtol=0.0, atol=1e-12
    ):
        raise ValueError(f"POSEIDON posterior does not reproduce MultiNest equal-weight samples for {hours} h")

    manifest_path = LOG_DIR / f"{tag}.resume_manifest.json"
    manifest = json.loads(check_text(manifest_path))
    if manifest.get("source_files_modified") is not False:
        raise ValueError(f"Checkpoint manifest does not confirm source preservation: {manifest_path}")
    old_tag = f"proxima_A1_{hours}h{manifest['old_tag']}"
    original_hashes = {}
    for suffix, expected_hash in manifest["source_sha256"].items():
        original_path = RAW_DIR / f"{old_tag}{suffix}"
        actual_hash = sha256(original_path)
        if actual_hash != expected_hash:
            raise ValueError(f"Original MPI6 checkpoint changed: {original_path}")
        original_hashes[suffix] = actual_hash
    posterior = {m: samples[:, columns[f"log_{m}"]] for m in MOLECULES}
    posterior["R_p_ref"] = samples[:, columns["R_p_ref"]]
    quantiles = {}
    for parameter, values in posterior.items():
        q16, median, q84 = np.percentile(values, [16, 50, 84])
        quantiles[parameter] = {
            "q16": float(q16),
            "median": float(median),
            "q84": float(q84),
            "sigma68": float(0.5 * (q84 - q16)),
        }

    pt_path = SAMPLES_DIR / f"{tag}_PT_retrieved.txt"
    pt = load_numeric(pt_path, skiprows=1)
    if pt.shape != (100, 6) or np.any(pt[:, 0] <= 0):
        raise ValueError(f"Unexpected retrieved P--T table: {pt.shape} in {pt_path}")
    spectrum_path = SAMPLES_DIR / f"{tag}_spectrum_retrieved.txt"
    spectrum = load_numeric(spectrum_path, skiprows=1)
    if spectrum.shape[1] != 6 or not np.all(np.diff(spectrum[:, 0]) > 0):
        raise ValueError(f"Unexpected retrieved spectrum table: {spectrum.shape}")
    log_x_path = SAMPLES_DIR / f"{tag}_log_X_retrieved.txt"
    log_x = numeric_log_x_rows(log_x_path)

    true_pt = np.genfromtxt(TRUE_PT_FILE, names=True)
    true_pressure = np.asarray(true_pt["P"], dtype=float)
    true_temperature = np.asarray(true_pt["T"], dtype=float)
    order = np.argsort(np.log10(true_pressure))
    true_temperature_interp = np.interp(
        np.log10(pt[:, 0]), np.log10(true_pressure[order]), true_temperature[order]
    )
    pt_difference = pt[:, 3] - true_temperature_interp
    pt_metrics = {
        "rms_median_minus_A1_true_K": float(np.sqrt(np.mean(pt_difference**2))),
        "median_bias_K": float(np.median(pt_difference)),
        "fraction_A1_true_inside_68pct": float(
            np.mean((true_temperature_interp >= pt[:, 2]) & (true_temperature_interp <= pt[:, 4]))
        ),
        "fraction_A1_true_inside_95pct": float(
            np.mean((true_temperature_interp >= pt[:, 1]) & (true_temperature_interp <= pt[:, 5]))
        ),
    }

    return {
        "hours": hours,
        "tag": tag,
        "dataset": str(dataset_path),
        "dataset_sha256": dataset_sha,
        "dataset_bins": int(dataset.shape[0]),
        "log": str(log_path),
        "raw_files": {suffix: str(path) for suffix, path in raw_paths.items()},
        "raw_file_count": len(raw_paths),
        "raw_numeric_shapes": raw_shapes,
        "resume": resume,
        "original_MPI6_source_hashes_verified": original_hashes,
        "posterior_file": str(sample_path),
        "posterior_rows": int(samples.shape[0]),
        "posterior_columns": sample_header,
        "posterior_quantiles": quantiles,
        "result": parse_result(result_path),
        "pt_file": str(pt_path),
        "pt_shape": list(pt.shape),
        "pt_metrics_vs_A1_input": pt_metrics,
        "log_x_file": str(log_x_path),
        "log_x_numeric_rows": int(log_x.shape[0]),
        "spectrum_file": str(spectrum_path),
        "spectrum_shape": list(spectrum.shape),
        "spectrum_wavelength_um": [float(spectrum[0, 0]), float(spectrum[-1, 0])],
        "posterior": posterior,
        "pt": pt,
        "true_temperature_interp": true_temperature_interp,
        "true_pressure": true_pressure,
        "true_temperature": true_temperature,
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


def add_reference_lines(ax: plt.Axes, molecule: str, references: dict[str, dict[str, float]]) -> None:
    ax.axvline(
        references["A0"][molecule],
        color=PALETTE["deep_moss"],
        linestyle=":",
        linewidth=1.7,
        label="A0 efectiva",
    )
    ax.axvline(
        references["A1"][molecule],
        color=PALETTE["scenario_cyan"],
        linestyle="--",
        linewidth=1.7,
        label="A1 efectiva (entrada)",
    )


def make_figure(
    products: dict[int, dict[str, object]],
    references: dict[str, dict[str, float]],
    overwrite: bool,
) -> tuple[Path, Path]:
    plot_dir = CAMPAIGN / "plots"
    plot_dir.mkdir(parents=True, exist_ok=True)
    png = plot_dir / f"{OUTPUT_STEM}.png"
    pdf = plot_dir / f"{OUTPUT_STEM}.pdf"
    if (png.exists() or pdf.exists()) and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing figure: {png} / {pdf}")

    fig = plt.figure(figsize=(12.6, 8.2), constrained_layout=True)
    grid = fig.add_gridspec(2, 3, height_ratios=(1.0, 1.15))
    axes = [fig.add_subplot(grid[0, i]) for i in range(3)]
    for ax, molecule in zip(axes, MOLECULES):
        arrays = [products[h]["posterior"][molecule] for h in (10, 100)]
        low = min(float(np.percentile(values, 0.5)) for values in arrays)
        high = max(float(np.percentile(values, 99.5)) for values in arrays)
        low = min(low, references["A0"][molecule], references["A1"][molecule]) - 0.25
        high = max(high, references["A0"][molecule], references["A1"][molecule]) + 0.25
        edges = np.linspace(low, high, 72)
        for hours in (10, 100):
            values = products[hours]["posterior"][molecule]
            density, _ = np.histogram(values, bins=edges, density=True)
            label = f"{hours} h"
            ax.stairs(density, edges, color=RUNS[hours]["color"], linewidth=1.9, label=label)
            ax.fill_between(edges[:-1], density, step="post", color=RUNS[hours]["color"], alpha=0.13)
            median = products[hours]["posterior_quantiles"][molecule]["median"]
            ax.axvline(median, color=RUNS[hours]["color"], linewidth=0.9, alpha=0.8)
        add_reference_lines(ax, molecule, references)
        ax.set_xlim(low, high)
        ax.set_xlabel(r"$\log_{10}$ VMR")
        ax.set_ylabel("Densidad posterior")
        ax.set_title(f"{MOLECULE_LABELS[molecule]} — isochem")
        ax.grid(axis="y", linestyle=":", alpha=0.28)
        ax.minorticks_on()
        ax.tick_params(direction="in", top=True, right=True, labelsize=8.5)
        if molecule == "N2O":
            ax.legend(frameon=True, fontsize=7.4, loc="upper left")

    pt_ax = fig.add_subplot(grid[1, :])
    true_order = np.argsort(products[10]["true_pressure"])
    p_true = products[10]["true_pressure"][true_order]
    t_true = products[10]["true_temperature"][true_order]
    pt_ax.plot(
        t_true,
        p_true,
        color=PALETTE["ink_black"],
        linewidth=2.0,
        linestyle="--",
        label="VULCAN A1 de entrada",
    )
    for hours in (10, 100):
        pt = products[hours]["pt"]
        color = RUNS[hours]["color"]
        pt_ax.fill_betweenx(pt[:, 0], pt[:, 1], pt[:, 5], color=color, alpha=0.07)
        pt_ax.fill_betweenx(pt[:, 0], pt[:, 2], pt[:, 4], color=color, alpha=0.17)
        metrics = products[hours]["pt_metrics_vs_A1_input"]
        pt_ax.plot(
            pt[:, 3],
            pt[:, 0],
            color=color,
            linewidth=1.8,
            label=(
                f"POSEIDON {hours} h: mediana; RMS vs A1 = "
                f"{metrics['rms_median_minus_A1_true_K']:.1f} K"
            ),
        )
    pt_ax.set_yscale("log")
    pt_ax.invert_yaxis()
    pt_ax.set_xlabel("Temperatura [K]")
    pt_ax.set_ylabel("Presión [bar]")
    pt_ax.set_title("Perfil térmico recuperado — bandas 68 % y 95 %")
    pt_ax.grid(which="both", linestyle=":", alpha=0.28)
    pt_ax.legend(frameon=True, fontsize=8, ncol=3, loc="best")
    pt_ax.tick_params(direction="in", top=True, right=True, labelsize=8.5)

    fig.suptitle(
        "Proxima b — recuperación LIFE del escenario A1 a 10 y 100 h\n"
        "Posteriores isochem y P–T; referencias escalares A0/A1 por promedio columnar",
        fontsize=14,
    )
    fig.savefig(png, dpi=300, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    plt.close(fig)
    return png, pdf


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    TABLE_DIR = CAMPAIGN / "tables"
    summary_path = TABLE_DIR / f"{OUTPUT_STEM}_summary.json"
    if summary_path.exists() and not args.overwrite:
        raise FileExistsError(f"Refusing to overwrite existing summary: {summary_path}")

    products = {hours: load_run(hours, config) for hours, config in RUNS.items()}
    references = effective_references()
    for hours, product in products.items():
        product["z_descriptive_vs_A0"] = {
            molecule: (
                product["posterior_quantiles"][molecule]["median"] - references["A0"][molecule]
            )
            / product["posterior_quantiles"][molecule]["sigma68"]
            for molecule in MOLECULES
        }
        product["z_descriptive_vs_A1"] = {
            molecule: (
                product["posterior_quantiles"][molecule]["median"] - references["A1"][molecule]
            )
            / product["posterior_quantiles"][molecule]["sigma68"]
            for molecule in MOLECULES
        }

    png, pdf = make_figure(products, references, overwrite=args.overwrite)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    summary = {
        "question": "Recovery of Proxima LIFE A1 under corrected POSEIDON interface at 10 and 100 h",
        "classification": "separate audit; excluded from canonical 8/8",
        "configuration": {
            "POSEIDON": "1.4.0",
            "MPI": "MPICH, six ranks per run, resumed MultiNest 3.10 checkpoint",
            "X_profile": "isochem",
            "N_live": 800,
            "error_inflation": "none",
            "x_tol": "absent",
            "species": ["H2O", "CO2", "CH4", "O2", "O3", "N2O", "NH3"],
            "surface": "black, fixed at 1 bar (log_P_surf=0)",
            "R": 10000,
            "data": "31 LIFE Fp bins; diagonal uncertainties; 10 h canonical dataset and independent 100 h audit realization",
        },
        "references_log10_vmr_pressure_column_mean": references,
        "runs": {},
        "figure": {"png": str(png), "pdf": str(pdf)},
        "interpretation_limit": (
            "Distances z=(posterior median-reference)/sigma68 are descriptive and conditional on the isochemical "
            "retrieval, retrieved Madhu PT, diagonal noise and each dataset realization. A1-effective and A0-effective "
            "abundances are close for N2O, NH3 and O2, so these retrievals do not establish formal discrimination of A1 from A0. "
            "The 10 h and 100 h datasets differ in both uncertainty and realization; their ln Z values are not Bayes factors."
        ),
    }
    for hours, product in products.items():
        summary["runs"][str(hours)] = {
            key: value
            for key, value in product.items()
            if key not in {"posterior", "pt", "true_temperature_interp", "true_pressure", "true_temperature"}
        }
        summary["runs"][str(hours)]["z_descriptive_vs_A0"] = product["z_descriptive_vs_A0"]
        summary["runs"][str(hours)]["z_descriptive_vs_A1"] = product["z_descriptive_vs_A1"]
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    for hours, product in products.items():
        quantiles = product["posterior_quantiles"]
        print(
            f"{hours} h: lnZ={product['result']['ln_Z']:.2f}±{product['result']['ln_Z_error']:.2f}; "
            f"chi2_red={product['result']['chi2_red']:.2f} (dof={product['result']['dof']}); "
            f"Rp_ref={quantiles['R_p_ref']['median']:.4f} R_E; "
            f"logN2O={quantiles['N2O']['median']:.3f} [{quantiles['N2O']['q16']:.3f}, {quantiles['N2O']['q84']:.3f}]; "
            f"logNH3={quantiles['NH3']['median']:.3f}; logO2={quantiles['O2']['median']:.3f}; "
            f"PT_RMS={product['pt_metrics_vs_A1_input']['rms_median_minus_A1_true_K']:.2f} K; "
            f"resume={product['resume']['replacements']} replacements/{product['resume']['evaluations']} evaluations"
        )
    print("References, log10 VMR:", json.dumps(references, sort_keys=True))
    print(f"PNG={png}\nPDF={pdf}\nSUMMARY={summary_path}")


if __name__ == "__main__":
    main()
