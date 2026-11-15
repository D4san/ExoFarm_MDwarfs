#!/usr/bin/env python3
"""Validate and summarize the Proxima A1/A3 240 h MPI audit retrievals.

This post-processing entry point reads the exact suffixed products from the
two completed POSEIDON runs. It does not rerun retrievals or modify the
canonical A0--A3 by {10 h, 240 h} dataset matrix.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

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
DATA_DIR = CAMPAIGN / "life_data"
LOG_DIR = CAMPAIGN / "retrievals"
PROFILE_DIR = REPO / "Transmission_Spectroscopy/profiles"
MOLECULES = ("N2O", "NH3", "O2")
MOLECULE_LABELS = {"N2O": r"N$_2$O", "NH3": r"NH$_3$", "O2": r"O$_2$"}
OUTPUT_STEM = "retrieval_A1_A3_240h_MPI6_AUDIT_posteriors_PT_proxima"

RUNS: dict[str, dict[str, Any]] = {
    "A1": {
        "tag": "proxima_A1_240h_O2_fixedBlack1bar_noxtol_MPI6_AUDIT",
        "dataset": "LIFE_proxima_A1_240h.dat",
        "dataset_sha256": "0d73c1ff91ab756bae8905024095b4482a877d39b7051af0fa2f683899a1ab0c",
        "pid": 45344,
        "color": PALETTE["scenario_cyan"],
        "chem": PROFILE_DIR / "Proxima_b_A1_Current_chem.txt",
        "pt": PROFILE_DIR / "Proxima_b_A1_Current_PT.txt",
    },
    "A3": {
        "tag": "proxima_A3_240h_O2_fixedBlack1bar_noxtol_MPI6_AUDIT",
        "dataset": "LIFE_proxima_A3_240h.dat",
        "dataset_sha256": "7f04734252be9b8428ea13288d65471f861a23815723616b363b48b27efadd7b",
        "pid": 45353,
        "color": PALETTE["scenario_pink"],
        "chem": PROFILE_DIR / "Proxima_b_A3_Extreme_chem.txt",
        "pt": PROFILE_DIR / "Proxima_b_A3_Extreme_PT.txt",
    },
}
REFERENCE_CHEM = {
    name: PROFILE_DIR / f"Proxima_b_{suffix}_chem.txt"
    for name, suffix in (("A0", "A0_PreAgri"), ("A1", "A1_Current"), ("A3", "A3_Extreme"))
}

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
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_file(path: Path) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        raise FileNotFoundError(f"Missing or empty required product: {path}")


def load_numeric(path: Path, *, skiprows: int = 0) -> np.ndarray:
    require_file(path)
    values = np.loadtxt(path, skiprows=skiprows, ndmin=2)
    if values.size == 0 or not np.isfinite(values).all():
        raise ValueError(f"Empty or non-finite numeric product: {path}")
    return values


def parse_result(path: Path, tag: str, dataset_name: str) -> dict[str, float | int]:
    require_file(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    if f"Model: {tag}" not in text or f"LIFE ({dataset_name})" not in text:
        raise ValueError(f"Model or dataset label mismatch in {path}")
    if "N_params = 15" not in text or "N_live = 800" not in text:
        raise ValueError(f"Unexpected sampler dimensions in {path}")
    patterns = {
        "ln_Z": r"->\s*ln Z\s*=\s*([+-]?[\d.]+(?:[eE][+-]?\d+)?)",
        "ln_Z_error": r"->\s*ln Z\s*=\s*[+-]?[\d.]+(?:[eE][+-]?\d+)?\s*\+/-\s*([\d.]+(?:[eE][+-]?\d+)?)",
        "chi2_red": r"->\s*chi\^2_red\s*=\s*([\d.]+(?:[eE][+-]?\d+)?)",
        "dof": r"->\s*degrees of freedom\s*=\s*(\d+)",
        "chi2": r"->\s*chi\^2\s*=\s*([\d.]+(?:[eE][+-]?\d+)?)",
    }
    result: dict[str, float | int] = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match is None:
            raise ValueError(f"Missing {key} in {path}")
        result[key] = int(match.group(1)) if key == "dof" else float(match.group(1))

    best_fit = text.split("Best-fitting parameters", maxsplit=1)
    if len(best_fit) != 2:
        raise ValueError(f"Missing best-fit block in {path}")
    for parameter in ("R_p_ref", "log_N2O", "log_NH3", "log_O2", "log_P_surf"):
        match = re.search(
            rf"^\s*{re.escape(parameter)}\s*=\s*([+-]?[\d.]+(?:[eE][+-]?\d+)?)",
            best_fit[1],
            re.MULTILINE,
        )
        if match is None:
            raise ValueError(f"Missing best-fit {parameter} in {path}")
        result[f"bestfit_{parameter}"] = float(match.group(1))
    return result


def parse_log_x(path: Path) -> np.ndarray:
    require_file(path)
    rows: list[list[float]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            row = [float(item) for item in line.split()]
        except ValueError:
            continue
        if row:
            if len(row) != 6 or not np.isfinite(row).all():
                raise ValueError(f"Malformed numeric log-X row in {path}")
            rows.append(row)
    values = np.asarray(rows, dtype=float)
    if values.shape != (800, 6):
        raise ValueError(f"Expected 800 x 6 finite log-X rows, got {values.shape} in {path}")
    return values


def parse_resume(path: Path) -> dict[str, int]:
    require_file(path)
    rows = [line.split() for line in path.read_text().splitlines() if line.strip()]
    if len(rows) < 2 or len(rows[1]) < 4:
        raise ValueError(f"Unrecognized final MultiNest resume file: {path}")
    replacements, evaluations, n_live = int(rows[1][0]), int(rows[1][1]), int(rows[1][3])
    if n_live != 800:
        raise ValueError(f"Expected 800 live points in {path}; found {n_live}")
    return {"replacements": replacements, "evaluations": evaluations, "n_live": n_live}


def load_run(scenario: str, config: dict[str, Any]) -> dict[str, Any]:
    tag = config["tag"]
    result_dir = PRODUCTS / "results"
    sample_dir = PRODUCTS / "samples"
    raw_dir = PRODUCTS / "MultiNest_raw"
    log_path = LOG_DIR / f"{tag}.launch.log"
    require_file(log_path)
    log = log_path.read_text(encoding="utf-8", errors="replace")
    if f"[process_exit] mpiexec_pid={config['pid']} exit_code=0" not in log:
        raise ValueError(f"No successful process-exit marker for {scenario}: {log_path}")
    if "Sampling finished. Exiting MultiNest" not in log or "All done!" not in log:
        raise ValueError(f"Missing MultiNest/POSEIDON completion marker: {log_path}")
    if f"[harvest_complete] source=/home/dasan/exofarm_proxima_a1_a3_240h_MPI6_20260930T044539Z/{scenario}" not in log:
        raise ValueError(f"Missing post-exit harvest marker for {scenario}: {log_path}")
    for required in (
        "--n-live 800",
        "--error-inflation none",
        "--surface-pressure-mode fixed-black",
        "--include-o2",
        "--x-profile isochem",
        "--R 10000",
        f"--scenario {scenario}",
        f"LIFE_proxima_{scenario}_240h.dat",
    ):
        if required not in log:
            raise ValueError(f"Launch log lacks {required}: {log_path}")

    dataset_path = DATA_DIR / config["dataset"]
    dataset = load_numeric(dataset_path, skiprows=1)
    digest = sha256(dataset_path)
    if dataset.shape != (31, 4) or np.any(dataset[:, 3] <= 0):
        raise ValueError(f"Expected 31 bins and positive diagonal uncertainties: {dataset_path}")
    if digest != config["dataset_sha256"]:
        raise ValueError(f"Dataset checksum mismatch for {scenario}: {digest}")

    result_path = result_dir / f"{tag}_results.txt"
    result = parse_result(result_path, tag, config["dataset"])
    raw_prefix = raw_dir / tag
    suffixes = (
        "-.txt",
        "-ev.dat",
        "-live.points",
        "-phys_live.points",
        "-post_equal_weights.dat",
        "-resume.dat",
        "-stats.dat",
        "-summary.txt",
    )
    raw_paths = {suffix: Path(f"{raw_prefix}{suffix}") for suffix in suffixes}
    raw_shapes: dict[str, list[int]] = {}
    raw_arrays: dict[str, np.ndarray] = {}
    for suffix in ("-.txt", "-ev.dat", "-live.points", "-phys_live.points", "-post_equal_weights.dat", "-summary.txt"):
        raw_arrays[suffix] = load_numeric(raw_paths[suffix])
        raw_shapes[suffix] = list(raw_arrays[suffix].shape)
    for suffix in ("-live.points", "-phys_live.points"):
        if raw_arrays[suffix].shape[0] != 800:
            raise ValueError(f"Expected 800 rows in {raw_paths[suffix]}")
    stats_text = raw_paths["-stats.dat"].read_text(encoding="utf-8", errors="replace")
    if "Nested Sampling Global Log-Evidence" not in stats_text:
        raise ValueError(f"Missing global evidence in {raw_paths['-stats.dat']}")
    resume = parse_resume(raw_paths["-resume.dat"])
    if raw_shapes["-ev.dat"][0] != resume["replacements"] - resume["n_live"]:
        raise ValueError(f"Final ev.dat/resume.dat row mismatch for {scenario}")
    if not re.search(rf"\b{resume['evaluations']}\b", log):
        raise ValueError(f"Final MultiNest evaluation count absent from log for {scenario}")

    sample_path = sample_dir / f"{tag}_samples.txt"
    require_file(sample_path)
    header = [field.strip() for field in sample_path.read_text(encoding="utf-8").splitlines()[0].split("|")]
    samples = load_numeric(sample_path, skiprows=1)
    if samples.shape[1] != len(header) or samples.shape[1] != 15:
        raise ValueError(f"Posterior dimensions/header mismatch for {scenario}: {samples.shape}")
    columns = {name: index for index, name in enumerate(header)}
    required_parameters = {"R_p_ref", "log_N2O", "log_NH3", "log_O2", "log_P_surf"}
    if not required_parameters.issubset(columns) or "x_tol" in columns:
        raise ValueError(f"Unexpected posterior parameters for {scenario}: {header}")
    if not np.allclose(samples[:, columns["log_P_surf"]], 0.0, atol=1e-12, rtol=0.0):
        raise ValueError(f"Surface pressure is not fixed to 1 bar for {scenario}")
    raw_equal = raw_arrays["-post_equal_weights.dat"]
    if raw_equal.shape[0] != samples.shape[0] or raw_equal.shape[1] < samples.shape[1]:
        raise ValueError(f"Posterior row count does not match MultiNest equal-weight output for {scenario}")
    if not np.allclose(samples, raw_equal[:, : samples.shape[1]], rtol=0.0, atol=1e-12):
        raise ValueError(f"POSEIDON posterior differs from MultiNest equal-weight samples for {scenario}")

    posterior: dict[str, np.ndarray] = {}
    quantiles: dict[str, dict[str, float]] = {}
    for parameter in ("R_p_ref", *[f"log_{molecule}" for molecule in MOLECULES]):
        values = samples[:, columns[parameter]]
        q16, median, q84 = np.percentile(values, [16, 50, 84])
        posterior[parameter] = values
        quantiles[parameter] = {
            "q16": float(q16),
            "median": float(median),
            "q84": float(q84),
            "sigma68": float((q84 - q16) / 2.0),
        }

    pt_path = sample_dir / f"{tag}_PT_retrieved.txt"
    pt = load_numeric(pt_path, skiprows=1)
    if pt.shape != (100, 6) or np.any(pt[:, 0] <= 0) or np.any(np.diff(pt[:, 0]) >= 0):
        raise ValueError(f"Unexpected P--T product for {scenario}: {pt.shape}")
    spectrum_path = sample_dir / f"{tag}_spectrum_retrieved.txt"
    spectrum = load_numeric(spectrum_path, skiprows=1)
    if spectrum.shape[1] != 6 or not np.all(np.diff(spectrum[:, 0]) > 0):
        raise ValueError(f"Unexpected retrieved spectrum for {scenario}: {spectrum.shape}")
    log_x_path = sample_dir / f"{tag}_log_X_retrieved.txt"
    log_x = parse_log_x(log_x_path)

    resume_text = raw_paths["-resume.dat"].read_text().splitlines()
    raw_checkpoint_sha256 = {
        suffix: sha256(path)
        for suffix, path in raw_paths.items()
    }
    true_pt_table = np.genfromtxt(config["pt"], names=True)
    true_pressure = np.asarray(true_pt_table["P"], dtype=float)
    true_temperature = np.asarray(true_pt_table["T"], dtype=float)
    order = np.argsort(np.log10(true_pressure))
    true_temperature_interp = np.interp(
        np.log10(pt[:, 0]), np.log10(true_pressure[order]), true_temperature[order]
    )
    pt_delta = pt[:, 3] - true_temperature_interp
    pt_metrics = {
        "rms_median_minus_VULCAN_K": float(np.sqrt(np.mean(pt_delta**2))),
        "median_bias_K": float(np.median(pt_delta)),
        "fraction_true_inside_68pct": float(np.mean((true_temperature_interp >= pt[:, 2]) & (true_temperature_interp <= pt[:, 4]))),
        "fraction_true_inside_95pct": float(np.mean((true_temperature_interp >= pt[:, 1]) & (true_temperature_interp <= pt[:, 5]))),
    }

    return {
        "scenario": scenario,
        "tag": tag,
        "dataset": str(dataset_path),
        "dataset_sha256": digest,
        "dataset_bins": int(dataset.shape[0]),
        "dataset_sigma_min": float(dataset[:, 3].min()),
        "dataset_sigma_max": float(dataset[:, 3].max()),
        "log": str(log_path),
        "result_file": str(result_path),
        "result": result,
        "resume": resume,
        "resume_checkpoint_lines": resume_text,
        "raw_files": {suffix: str(path) for suffix, path in raw_paths.items()},
        "raw_sha256": raw_checkpoint_sha256,
        "raw_shapes": raw_shapes,
        "posterior_file": str(sample_path),
        "posterior_rows": int(samples.shape[0]),
        "posterior_columns": header,
        "posterior_quantiles": quantiles,
        "pt_file": str(pt_path),
        "pt_shape": list(pt.shape),
        "pt_metrics_vs_VULCAN": pt_metrics,
        "spectrum_file": str(spectrum_path),
        "spectrum_shape": list(spectrum.shape),
        "log_X_file": str(log_x_path),
        "log_X_numeric_shape": list(log_x.shape),
        "posterior": posterior,
        "pt": pt,
        "true_pressure": true_pressure,
        "true_temperature": true_temperature,
        "true_temperature_interp": true_temperature_interp,
    }


def effective_references() -> dict[str, dict[str, float]]:
    profiles = {name: np.genfromtxt(path, names=True) for name, path in REFERENCE_CHEM.items()}
    return {
        scenario: {
            molecule: float(log10_column_averaged_mixing_ratio(profile, molecule))
            for molecule in MOLECULES
        }
        for scenario, profile in profiles.items()
    }


def make_figure(runs: dict[str, dict[str, Any]], references: dict[str, dict[str, float]]) -> tuple[Path, Path]:
    plot_dir = CAMPAIGN / "plots"
    plot_dir.mkdir(parents=True, exist_ok=True)
    png = plot_dir / f"{OUTPUT_STEM}.png"
    pdf = plot_dir / f"{OUTPUT_STEM}.pdf"
    if png.exists() or pdf.exists():
        raise FileExistsError(f"Refusing to overwrite existing audit figure: {png}")

    fig = plt.figure(figsize=(13.2, 8.3), constrained_layout=True)
    grid = fig.add_gridspec(2, 3, height_ratios=(1.0, 1.18))
    axes = [fig.add_subplot(grid[0, index]) for index in range(3)]
    for ax, molecule in zip(axes, MOLECULES):
        parameter = f"log_{molecule}"
        distributions = [runs[name]["posterior"][parameter] for name in ("A1", "A3")]
        low = min(float(np.percentile(values, 0.5)) for values in distributions)
        high = max(float(np.percentile(values, 99.5)) for values in distributions)
        low = min(low, *(references[name][molecule] for name in ("A0", "A1", "A3"))) - 0.20
        high = max(high, *(references[name][molecule] for name in ("A0", "A1", "A3"))) + 0.20
        edges = np.linspace(low, high, 76)
        for scenario in ("A1", "A3"):
            values = runs[scenario]["posterior"][parameter]
            density, _ = np.histogram(values, bins=edges, density=True)
            color = RUNS[scenario]["color"]
            ax.stairs(density, edges, color=color, linewidth=1.8, label=f"{scenario} posterior")
            ax.fill_between(edges[:-1], density, step="post", color=color, alpha=0.15)
            ax.axvline(
                runs[scenario]["posterior_quantiles"][parameter]["median"],
                color=color,
                linewidth=0.9,
                alpha=0.85,
            )
        ax.axvline(references["A0"][molecule], color=PALETTE["deep_moss"], linestyle="-.", linewidth=1.6, label="A0 efectiva")
        ax.axvline(references["A1"][molecule], color=RUNS["A1"]["color"], linestyle=":", linewidth=1.5, label="A1 efectiva")
        ax.axvline(references["A3"][molecule], color=RUNS["A3"]["color"], linestyle=":", linewidth=1.5, label="A3 efectiva")
        ax.set_xlim(low, high)
        ax.set_xlabel(r"$log_{10}$ VMR")
        ax.set_ylabel("Densidad posterior")
        ax.set_title(f"{MOLECULE_LABELS[molecule]} — isochem")
        ax.grid(axis="y", linestyle=":", alpha=0.28)
        ax.minorticks_on()
        ax.tick_params(direction="in", top=True, right=True, labelsize=8.5)
        if molecule == "N2O":
            ax.legend(frameon=True, fontsize=7.1, loc="upper left")

    pt_ax = fig.add_subplot(grid[1, :])
    for scenario in ("A1", "A3"):
        run = runs[scenario]
        color = RUNS[scenario]["color"]
        pt = run["pt"]
        order = np.argsort(pt[:, 0])
        pressure = pt[order, 0]
        pt_ax.fill_betweenx(pressure, pt[order, 1], pt[order, 5], color=color, alpha=0.08)
        pt_ax.fill_betweenx(pressure, pt[order, 2], pt[order, 4], color=color, alpha=0.18)
        pt_ax.plot(pt[order, 3], pressure, color=color, linewidth=1.9, label=f"POSEIDON {scenario} median")
        true_order = np.argsort(run["true_pressure"])
        pt_ax.plot(
            run["true_temperature"][true_order],
            run["true_pressure"][true_order],
            color=color,
            linewidth=1.4,
            linestyle="--",
            label=f"VULCAN {scenario} input",
        )
    pt_ax.set_yscale("log")
    pt_ax.invert_yaxis()
    pt_ax.set_xlabel("Temperatura [K]")
    pt_ax.set_ylabel("Presión [bar]")
    pt_ax.set_title("Perfil P–T recuperado — bandas marginales del 68 % y 95 %")
    pt_ax.grid(which="both", linestyle=":", alpha=0.28)
    pt_ax.legend(frameon=True, fontsize=8.2, ncol=4, loc="best")
    pt_ax.tick_params(direction="in", top=True, right=True, labelsize=8.5)

    fig.suptitle(
        "Proxima b — retrieval LIFE A1/A3 a 240 h (auditoría MPI6)\n"
        "Abundancias isochem y P–T; A0/A1/A3 efectivos; ruido diagonal con realizaciones independientes\n"
        f"$\\chi^2_{{red}}$: A1={runs['A1']['result']['chi2_red']:.2f}, A3={runs['A3']['result']['chi2_red']:.2f} (16 dof); "
        "A3 forward preflight RMS=0.390σ, máximo=1.247σ (umbral estricto no satisfecho)",
        fontsize=13.2,
    )
    fig.savefig(png, dpi=300, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    plt.close(fig)
    return png, pdf


def main() -> None:
    runs = {scenario: load_run(scenario, config) for scenario, config in RUNS.items()}
    references = effective_references()
    for scenario, run in runs.items():
        quantiles = run["posterior_quantiles"]
        run["z_descriptive_vs_A0"] = {}
        run["z_descriptive_vs_truth"] = {}
        for molecule in MOLECULES:
            parameter = f"log_{molecule}"
            posterior = quantiles[parameter]
            sigma68 = posterior["sigma68"]
            run["z_descriptive_vs_A0"][molecule] = (posterior["median"] - references["A0"][molecule]) / sigma68
            run["z_descriptive_vs_truth"][molecule] = (posterior["median"] - references[scenario][molecule]) / sigma68

    table_dir = CAMPAIGN / "tables"
    summary_path = table_dir / f"{OUTPUT_STEM}_summary.json"
    if summary_path.exists():
        raise FileExistsError(f"Refusing to overwrite existing summary: {summary_path}")
    png_path = CAMPAIGN / "plots" / f"{OUTPUT_STEM}.png"
    pdf_path = CAMPAIGN / "plots" / f"{OUTPUT_STEM}.pdf"
    if png_path.exists() or pdf_path.exists():
        raise FileExistsError(f"Refusing to overwrite existing audit figure: {png_path}")
    png, pdf = make_figure(runs, references)
    table_dir.mkdir(parents=True, exist_ok=True)

    def serializable_run(run: dict[str, Any]) -> dict[str, Any]:
        return {
            key: value
            for key, value in run.items()
            if key not in {"posterior", "pt", "true_pressure", "true_temperature", "true_temperature_interp"}
        }

    summary = {
        "date_local": "2026-09-30 America/Bogota",
        "question": "Recovery of Proxima LIFE A1 and A3 abundance/thermal profiles at 240 h under the corrected fixed-surface POSEIDON setup",
        "classification": "separate audit; excluded from canonical A0-A3 x {10 h, 240 h} 8/8 matrix",
        "configuration": {
            "POSEIDON": "1.4.0",
            "MPI": "MPICH; six ranks per retrieval; two retrievals run concurrently",
            "MultiNest": "3.10",
            "N_live": 800,
            "parameters": 15,
            "X_profile": "isochem",
            "included_species": ["H2O", "CO2", "CH4", "O2", "O3", "N2O", "NH3"],
            "error_inflation": "none",
            "x_tol": "absent",
            "surface": "black surface fixed at 1 bar (log_P_surf=0)",
            "R": 10000,
            "data": "31 LIFE Fp bins; diagonal uncertainties; distinct A1 and A3 canonical 240 h datasets/realizations",
        },
        "references_log10_vmr_pressure_column_mean": references,
        "runs": {scenario: serializable_run(run) for scenario, run in runs.items()},
        "figure": {"png": str(png), "pdf": str(pdf)},
        "interpretation_limits": [
            "The A3 forward preflight on 31 bins was RMS=0.3901 sigma and maximum=1.247 sigma; it exceeded the helper's strict RMS<=0.3/max<=1.0 gate and is not labeled a pass.",
            "Both best-fit reduced chi-square values are high (16 dof), indicating substantial model/data tension under the adopted isochemical retrieval and diagonal-noise realization.",
            "The A1 and A3 data files are distinct noise realizations; their ln Z values are not a Bayes factor and are not compared as evidence for A1 versus A3.",
            "Posterior-reference distances use sigma68=(q84-q16)/2 and are descriptive, conditional on the isochemical abundance model, retrieved PT, diagonal noise, and each dataset realization; they are not formal detection significances.",
            "The canonical A0-A3 x {10 h, 240 h} retrieval matrix and input datasets were not modified; these suffixed runs remain an external audit.",
        ],
    }
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    for scenario, run in runs.items():
        q = run["posterior_quantiles"]
        print(
            f"{scenario}: lnZ={run['result']['ln_Z']:.2f}±{run['result']['ln_Z_error']:.2f}; "
            f"chi2_red={run['result']['chi2_red']:.2f} (dof={run['result']['dof']}); "
            f"posterior_rows={run['posterior_rows']}; replacements={run['resume']['replacements']}; "
            f"evaluations={run['resume']['evaluations']}; R_p_ref={q['R_p_ref']['median']:.4f}; "
            + "; ".join(
                f"{m}={q[f'log_{m}']['median']:.3f} [{q[f'log_{m}']['q16']:.3f}, {q[f'log_{m}']['q84']:.3f}], "
                f"z_A0={run['z_descriptive_vs_A0'][m]:+.2f}, z_truth={run['z_descriptive_vs_truth'][m]:+.2f}"
                for m in MOLECULES
            )
            + f"; PT_RMS={run['pt_metrics_vs_VULCAN']['rms_median_minus_VULCAN_K']:.2f} K"
        )
    print(f"Validated products and wrote {summary_path}, {png}, {pdf}")


if __name__ == "__main__":
    main()
