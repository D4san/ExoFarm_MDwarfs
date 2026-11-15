"""Validate and visualize the recovered Proxima A3 100 h LIFE retrieval.

Compares the earlier 100 h isochemical audit (no O2, no explicit surface) with
the corrected-interface audit (O2 plus a black 1 bar surface), and checks the
retrieved median spectra against the same 31-bin LIFE realization.
"""

from __future__ import annotations

import csv
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
from matplotlib.lines import Line2D


REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPO / "Transmission_Spectroscopy" / "notebooks"))
from retrieval_reference import log10_column_averaged_mixing_ratio
from audit_proxima_a3_retrieval_residuals import rebin_energy_flux
from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE


CAMPAIGN = (
    REPO / "Thermal_Emission_Spectroscopy" / "outputs"
    / "life_proxima_b_earthlike_v1"
)
RETRIEVAL = CAMPAIGN / "retrievals" / "POSEIDON_output" / "proxima_b_earthlike" / "retrievals"
RAW = RETRIEVAL / "MultiNest_raw"
SAMPLES = RETRIEVAL / "samples"
RESULTS = RETRIEVAL / "results"
LIFE_DATA = CAMPAIGN / "life_data" / "LIFE_proxima_A3_100h.dat"
PLOTS = CAMPAIGN / "plots"
TABLES = CAMPAIGN / "tables"
MOLECULES = ("N2O", "NH3")
LABELS = {"N2O": r"N$_2$O", "NH3": r"NH$_3$"}
VARIANTS = {
    "legacy": {
        "tag": "proxima_A3_100h_fixedP1bar_noxtol",
        "label": "Legacy: sin O$_2$, sin superficie explícita",
        "color": PALETTE["charcoal_violet"],
        "marker": "o",
    },
    "corrected": {
        "tag": "proxima_A3_100h_O2_fixedBlack1bar_noxtol",
        "label": "Interfaz corregida: O$_2$ + superficie negra a 1 bar",
        "color": PALETTE["scenario_pink"],
        "marker": "s",
    },
}
PROFILE_PATHS = {
    "A0": REPO / "Transmission_Spectroscopy" / "profiles" / "Proxima_b_A0_PreAgri_chem.txt",
    "A3": REPO / "Transmission_Spectroscopy" / "profiles" / "Proxima_b_A3_Extreme_chem.txt",
}
PROFILE_COLORS = {"A0": PALETTE["scenario_green"], "A3": PALETTE["scenario_pink"]}
REFERENCE_COLORS = {"A0": PALETTE["deep_moss"], "A3": PALETTE["dark_amaranth"]}
PROFILE_FLOOR = 1.0e-30
EXPECTED_RAW_SUFFIXES = (
    "-.txt",
    "-ev.dat",
    "-live.points",
    "-phys_live.points",
    "-post_equal_weights",
    "-post_equal_weights.dat",
    "-resume.dat",
    "-stats.dat",
    "-summary.txt",
)

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
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def retrieval_stem(tag: str) -> str:
    return f"{tag}_{tag}"


def sample_path(tag: str) -> Path:
    return SAMPLES / f"{retrieval_stem(tag)}_samples.txt"


def result_path(tag: str) -> Path:
    return RESULTS / f"{retrieval_stem(tag)}_results.txt"


def ensure_no_nonfinite_text(path: Path) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    if re.search(r"(?i)(?<![a-z])(?:nan|inf(?:inity)?)(?![a-z])", text):
        raise ValueError(f"NaN/Inf token in {path}")


def validate_numeric_table(path: Path, *, skiprows: int = 0) -> np.ndarray:
    array = np.loadtxt(path, skiprows=skiprows, ndmin=2)
    if array.size == 0 or not np.isfinite(array).all():
        raise ValueError(f"Empty or non-finite numeric data in {path}")
    return array


def validate_raw_products(tag: str, expected_rows: int) -> dict[str, object]:
    stem = retrieval_stem(tag)
    suffixes = list(EXPECTED_RAW_SUFFIXES)
    if "O2_" not in tag:
        suffixes.remove("-post_equal_weights")
    files = {suffix: RAW / f"{stem}{suffix}" for suffix in suffixes}
    missing = [str(path) for path in files.values() if not path.is_file() or path.stat().st_size == 0]
    if missing:
        raise FileNotFoundError(f"Incomplete MultiNest file set for {tag}: {missing}")
    for path in files.values():
        ensure_no_nonfinite_text(path)

    equal_weight_suffix = (
        "-post_equal_weights" if "-post_equal_weights" in files
        else "-post_equal_weights.dat"
    )
    equal_weight = validate_numeric_table(files[equal_weight_suffix])
    analyzer_copy = files["-post_equal_weights.dat"]
    if "-post_equal_weights" in files and sha256(files["-post_equal_weights"]) != sha256(analyzer_copy):
        raise ValueError("Analyzer-compatible sample copy does not match original bytes")
    if equal_weight.shape != (expected_rows, 16 if "O2_" in tag else 14):
        raise ValueError(f"Unexpected raw equal-weight shape for {tag}: {equal_weight.shape}")
    live = validate_numeric_table(files["-live.points"])
    physical_live = validate_numeric_table(files["-phys_live.points"])
    if live.shape[0] != 800 or physical_live.shape[0] != 800:
        raise ValueError(f"Expected 800 live points for {tag}")
    if not np.isfinite(equal_weight).all():
        raise ValueError(f"Non-finite MultiNest equal-weight samples for {tag}")

    # The evidence trace is large; inspect it line-by-line without materializing
    # the full table in memory, and reject malformed/non-finite numeric rows.
    ev_path = files["-ev.dat"]
    ev_rows = 0
    with ev_path.open(encoding="utf-8", errors="replace") as handle:
        for line_number, line in enumerate(handle, start=1):
            fields = line.split()
            if not fields:
                continue
            try:
                values = np.asarray([float(field) for field in fields], dtype=float)
            except ValueError as exc:
                raise ValueError(f"Malformed evidence trace {ev_path}:{line_number}") from exc
            if not np.isfinite(values).all():
                raise ValueError(f"Non-finite evidence trace {ev_path}:{line_number}")
            ev_rows += 1
    if ev_rows == 0:
        raise ValueError(f"Empty MultiNest evidence trace: {ev_path}")

    return {
        "equal_weight_shape": list(equal_weight.shape),
        "live_points_shape": list(live.shape),
        "physical_live_points_shape": list(physical_live.shape),
        "evidence_trace_rows": ev_rows,
        "files": {suffix: {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)} for suffix, path in files.items()},
    }


def load_result(tag: str) -> dict[str, object]:
    path = result_path(tag)
    if not path.is_file():
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    ensure_no_nonfinite_text(path)
    patterns = {
        "n_params": r"N_params\s*=\s*(\d+)",
        "n_live": r"N_live\s*=\s*(\d+)",
        "ln_z": r"->\s*ln Z\s*=\s*([+-]?[\d.]+(?:[eE][+-]?\d+)?)",
        "ln_z_err": r"->\s*ln Z\s*=\s*[+-]?[\d.]+(?:[eE][+-]?\d+)?\s*\+/-\s*([\d.]+(?:[eE][+-]?\d+)?)",
        "chi2_red": r"->\s*chi\^2_red\s*=\s*([\d.]+(?:[eE][+-]?\d+)?)",
        "dof": r"->\s*degrees of freedom\s*=\s*(\d+)",
        "chi2": r"->\s*chi\^2\s*=\s*([\d.]+(?:[eE][+-]?\d+)?)",
    }
    result: dict[str, object] = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match is None:
            raise ValueError(f"Could not read {key} from {path}")
        value = match.group(1)
        result[key] = int(value) if key in {"n_params", "n_live", "dof"} else float(value)
    expected_params = 15 if "O2_" in tag else 13
    if result["n_params"] != expected_params or result["n_live"] != 800:
        raise ValueError(f"Unexpected POSEIDON configuration in {path}: {result}")
    return result


def load_posterior(tag: str) -> dict[str, object]:
    path = sample_path(tag)
    if not path.is_file():
        raise FileNotFoundError(path)
    ensure_no_nonfinite_text(path)
    header = [item.strip() for item in path.open(encoding="utf-8").readline().split("|")]
    samples = validate_numeric_table(path, skiprows=1)
    if samples.shape[1] != len(header):
        raise ValueError(f"Header/sample dimension mismatch for {path}")
    expected_rows = 7479 if "O2_" in tag else 7349
    if samples.shape[0] != expected_rows:
        raise ValueError(f"Unexpected posterior row count for {tag}: {samples.shape[0]}")
    columns = {name: index for index, name in enumerate(header)}
    required = {"R_p_ref", "log_N2O", "log_NH3"}
    if "O2_" in tag:
        required |= {"log_O2", "log_P_surf"}
    if not required.issubset(columns):
        raise ValueError(f"Missing posterior columns in {path}: {required - set(columns)}")
    if "log_P_surf" in columns and not np.allclose(
        samples[:, columns["log_P_surf"]], 0.0, rtol=0.0, atol=1e-12
    ):
        raise ValueError("Recovered posterior does not keep the black surface at 1 bar")

    summary = {}
    for name in ("R_p_ref", "log_N2O", "log_NH3", "log_O2"):
        if name not in columns:
            continue
        q16, median, q84 = np.percentile(samples[:, columns[name]], (16, 50, 84))
        summary[name] = {
            "q16": float(q16),
            "median": float(median),
            "q84": float(q84),
            "sigma68": float(0.5 * (q84 - q16)),
        }
    return {
        "path": path,
        "header": header,
        "samples": samples,
        "summary": summary,
        "count": int(samples.shape[0]),
    }


def load_spectrum(tag: str) -> np.ndarray:
    path = SAMPLES / f"{retrieval_stem(tag)}_spectrum_retrieved.txt"
    if not path.is_file():
        raise FileNotFoundError(path)
    ensure_no_nonfinite_text(path)
    spectrum = validate_numeric_table(path, skiprows=1)
    if spectrum.shape[1] != 6:
        raise ValueError(f"Unexpected spectrum shape in {path}: {spectrum.shape}")
    return spectrum


def load_log_x(tag: str) -> dict[str, object]:
    path = SAMPLES / f"{retrieval_stem(tag)}_log_X_retrieved.txt"
    if not path.is_file():
        raise FileNotFoundError(path)
    ensure_no_nonfinite_text(path)
    numeric = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        fields = line.split()
        if not fields:
            continue
        try:
            float(fields[0])
        except ValueError:
            continue
        row = np.asarray([float(field) for field in fields], dtype=float)
        if row.shape != (6,) or not np.isfinite(row).all():
            raise ValueError(f"Malformed numeric log-X line in {path}: {line}")
        numeric.append(row)
    expected_rows = 800 if "O2_" in tag else 700
    if len(numeric) != expected_rows:
        raise ValueError(f"Expected {expected_rows} numeric log-X rows for {tag}; got {len(numeric)}")
    return {"path": path, "numeric_rows": len(numeric)}


def load_pt(tag: str) -> np.ndarray:
    path = SAMPLES / f"{retrieval_stem(tag)}_PT_retrieved.txt"
    if not path.is_file():
        raise FileNotFoundError(path)
    ensure_no_nonfinite_text(path)
    pt = validate_numeric_table(path, skiprows=1)
    if pt.shape != (100, 6):
        raise ValueError(f"Unexpected P-T product shape in {path}: {pt.shape}")
    return pt


def load_profiles() -> dict[str, np.ndarray]:
    profiles = {}
    for scenario, path in PROFILE_PATHS.items():
        profile = np.genfromtxt(path, names=True)
        for field in ("PRESS", *MOLECULES):
            if field not in profile.dtype.names:
                raise ValueError(f"Missing {field} in VULCAN profile {path}")
        if not np.isfinite(profile["PRESS"]).all() or np.any(profile["PRESS"] <= 0):
            raise ValueError(f"Invalid pressure values in {path}")
        for molecule in MOLECULES:
            if not np.isfinite(profile[molecule]).all() or np.any(profile[molecule] < 0):
                raise ValueError(f"Invalid {molecule} profile in {path}")
        profiles[scenario] = profile
    return profiles


def load_residual_context(
    spectra: dict[str, np.ndarray],
) -> dict[str, object]:
    data = validate_numeric_table(LIFE_DATA, skiprows=1)
    if data.shape != (31, 4):
        raise ValueError(f"Expected 31 LIFE bins, found {data.shape}")
    wl, observed, sigma = data[:, 0], data[:, 2], data[:, 3]
    if not np.isfinite(data).all() or np.any(sigma <= 0):
        raise ValueError("Invalid LIFE data or diagonal uncertainties")
    dataset_hash = sha256(LIFE_DATA)

    with np.load(CAMPAIGN / "forward_emission" / "A3_emission.npz") as truth_file:
        truth = rebin_energy_flux(
            np.asarray(truth_file["wl_um"], dtype=float),
            np.asarray(truth_file["Fp_obs_W_m2_m"], dtype=float),
            wl,
        )
    residuals = {}
    for variant, spectrum in spectra.items():
        median_flux = rebin_energy_flux(spectrum[:, 0], spectrum[:, 3], wl)
        residual = (observed - median_flux) / sigma
        model_offset = (truth - median_flux) / sigma
        if not np.allclose(residual, model_offset + (observed - truth) / sigma, atol=1e-10):
            raise ValueError("Residual decomposition failed the truth/noise closure check")
        residuals[variant] = {
            "median_flux": median_flux,
            "residual_sigma": residual,
            "truth_minus_median_sigma": model_offset,
            "chi2_median": float(np.dot(residual, residual)),
            "rms_median": float(np.sqrt(np.mean(residual**2))),
            "n_over_3sigma": int(np.count_nonzero(np.abs(residual) > 3.0)),
        }
    noise = (observed - truth) / sigma
    return {
        "data": data,
        "wl": wl,
        "observed": observed,
        "sigma": sigma,
        "truth": truth,
        "noise_sigma": noise,
        "dataset_sha256": dataset_hash,
        "residuals": residuals,
    }


def posterior_z(summary: dict[str, float], reference: float) -> float:
    sigma68 = summary["sigma68"]
    if sigma68 <= 0:
        raise ValueError("Posterior has a non-positive central 68% width")
    return (summary["median"] - reference) / sigma68


def draw_profiles(ax: plt.Axes, profiles: dict[str, np.ndarray], molecule: str, refs: dict[str, dict[str, float]]) -> None:
    all_x = []
    for scenario in ("A0", "A3"):
        profile = profiles[scenario]
        x = np.log10(np.clip(profile[molecule], PROFILE_FLOOR, None))
        all_x.extend(x.tolist())
        ax.plot(
            x,
            profile["PRESS"],
            color=PROFILE_COLORS[scenario],
            linewidth=2.0,
            label=f"{scenario} VULCAN",
        )
    for scenario in ("A0", "A3"):
        ax.axvline(
            refs[scenario][molecule],
            color=REFERENCE_COLORS[scenario],
            linestyle=":" if scenario == "A0" else "-.",
            linewidth=1.4,
            label=f"{scenario} efectiva",
        )
    lo = max(-30.5, min(min(all_x), min(refs[s][molecule] for s in refs)) - 0.2)
    hi = min(0.0, max(max(all_x), max(refs[s][molecule] for s in refs)) + 0.2)
    ax.set_xlim(lo, hi)
    ax.set_yscale("log")
    ax.set_ylim(1.0, 5.0e-8)
    ax.set_xlabel(r"$\log_{10}$ volume mixing ratio")
    ax.set_ylabel("Pressure [bar]")
    ax.grid(which="major", linestyle=":", alpha=0.32)
    ax.grid(which="minor", linestyle=":", alpha=0.14)
    ax.minorticks_on()
    ax.tick_params(direction="in", top=True, right=True, labelsize=8.5)
    ax.set_title(f"{LABELS[molecule]} — perfil vertical VULCAN", fontsize=11)


def draw_posteriors(ax: plt.Axes, products: dict[str, dict[str, object]], molecule: str, refs: dict[str, dict[str, float]]) -> None:
    arrays = [products[v]["posterior"][molecule] for v in VARIANTS]
    lo = min(float(np.percentile(v, 0.5)) for v in arrays)
    hi = max(float(np.percentile(v, 99.5)) for v in arrays)
    lo = min(lo, refs["A0"][molecule], refs["A3"][molecule]) - 0.15
    hi = max(hi, refs["A0"][molecule], refs["A3"][molecule]) + 0.15
    edges = np.linspace(lo, hi, 62)
    for variant, style in VARIANTS.items():
        values = products[variant]["posterior"][molecule]
        density, _ = np.histogram(values, bins=edges, density=True)
        ax.stairs(
            density,
            edges,
            color=style["color"],
            linewidth=2.0,
            label=style["label"],
        )
        ax.fill_between(edges[:-1], density, step="post", color=style["color"], alpha=0.10)
        summary = products[variant]["summary"][f"log_{molecule}"]
        ax.axvline(summary["median"], color=style["color"], linestyle="-", linewidth=1.0)
    ax.axvline(refs["A0"][molecule], color=REFERENCE_COLORS["A0"], linestyle=":", lw=1.6, label="A0 efectiva")
    ax.axvline(refs["A3"][molecule], color=REFERENCE_COLORS["A3"], linestyle="-.", lw=1.5, label="A3 efectiva")
    ax.set_xlim(lo, hi)
    ax.set_xlabel(r"$\log_{10}$ volume mixing ratio")
    ax.set_ylabel("Posterior density")
    ax.grid(axis="y", linestyle=":", alpha=0.30)
    ax.minorticks_on()
    ax.tick_params(direction="in", top=True, right=True, labelsize=8.5)
    z_legacy = products["legacy"]["z"][molecule]
    z_corrected = products["corrected"]["z"][molecule]
    ax.set_title(
        f"{LABELS[molecule]} — posteriores isochem\n"
        f"z descriptivo: legacy {z_legacy:+.2f}; interfaz corregida {z_corrected:+.2f}",
        fontsize=10.5,
    )


def make_figure(
    profiles: dict[str, np.ndarray],
    refs: dict[str, dict[str, float]],
    products: dict[str, dict[str, object]],
    residual_context: dict[str, object],
    output_stem: str,
) -> tuple[Path, Path]:
    fig = plt.figure(figsize=(13.0, 10.8))
    grid = fig.add_gridspec(
        3,
        2,
        left=0.075,
        right=0.985,
        top=0.855,
        bottom=0.30,
        height_ratios=(1.0, 1.0, 1.25),
        hspace=0.56,
        wspace=0.25,
    )
    for row, molecule in enumerate(MOLECULES):
        profile_ax = fig.add_subplot(grid[row, 0])
        posterior_ax = fig.add_subplot(grid[row, 1])
        draw_profiles(profile_ax, profiles, molecule, refs)
        draw_posteriors(posterior_ax, products, molecule, refs)
        if row == 0:
            profile_ax.legend(frameon=False, fontsize=8, loc="lower left", ncol=2)
            posterior_ax.legend(frameon=False, fontsize=7.7, loc="upper left")

    residual_ax = fig.add_subplot(grid[2, :])
    wl = residual_context["wl"]
    residual_series = residual_context["residuals"]
    for variant, style in VARIANTS.items():
        residual = residual_series[variant]["residual_sigma"]
        residual_ax.plot(
            wl,
            residual,
            color=style["color"],
            marker=style["marker"],
            markersize=4.0,
            linewidth=1.1,
            label=(
                f"{style['label']} (RMS={residual_series[variant]['rms_median']:.2f}σ; "
                f"χ²={residual_series[variant]['chi2_median']:.1f})"
            ),
        )
    residual_ax.plot(
        wl,
        residual_series["corrected"]["truth_minus_median_sigma"],
        color=PALETTE["dim_grey"],
        linestyle="--",
        linewidth=1.25,
        marker=".",
        markersize=3,
        label="A3 verdadero − mediana corregida",
    )
    residual_ax.axhline(0.0, color="black", linewidth=0.8)
    residual_ax.axhline(1.0, color="0.55", linestyle=":", linewidth=0.8)
    residual_ax.axhline(-1.0, color="0.55", linestyle=":", linewidth=0.8)
    residual_ax.axhline(3.0, color="0.65", linestyle="--", linewidth=0.7)
    residual_ax.axhline(-3.0, color="0.65", linestyle="--", linewidth=0.7)
    residual_ax.set_xlim(float(wl.min()), float(wl.max()))
    residual_ax.set_xlabel("Wavelength [μm]")
    residual_ax.set_ylabel(r"$(F_{p,obs}-F_{p,med})/\sigma$ per bin")
    residual_ax.set_title("Residuos sobre la misma realización LIFE de 100 h (31 bins)", fontsize=11)
    residual_ax.grid(axis="x", linestyle=":", alpha=0.28)
    residual_ax.legend(frameon=False, fontsize=8, ncol=2, loc="upper right")
    residual_ax.tick_params(direction="in", top=True, right=True, labelsize=8.5)

    fig.suptitle(
        "Proxima b — recuperación del retrieval LIFE A3 a 100 h",
        fontsize=16,
        y=0.975,
    )
    fig.text(
        0.5,
        0.94,
        "Comparación de la posterior legacy con la interfaz corregida · POSEIDON · "
        "N_live=800 · sin x_tol ni inflación de errores",
        ha="center",
        fontsize=9.5,
    )

    table_ax = fig.add_axes([0.035, 0.105, 0.93, 0.12])
    table_ax.axis("off")
    headings = (
        "Variante",
        "ln Z ± σ",
        "χ²_red (dof)",
        r"$R_{p,ref}$ [$R_\oplus$]",
        r"log$_{10}$N$_2$O; z$_{A0}$",
        r"log$_{10}$NH$_3$; z$_{A0}$",
        r"log$_{10}$O$_2$",
    )
    rows = []
    for variant in ("legacy", "corrected"):
        product = products[variant]
        metadata = product["metadata"]
        s = product["summary"]
        radius = s["R_p_ref"]
        radius_err = radius["sigma68"]
        oxygen = s.get("log_O2")
        rows.append(
            [
                "Legacy" if variant == "legacy" else "O$_2$ + superficie fija",
                f"{metadata['ln_z']:.2f} ± {metadata['ln_z_err']:.2f}",
                f"{metadata['chi2_red']:.2f} ({metadata['dof']})",
                f"{radius['median']:.3f} ± {radius_err:.3f}",
                f"{s['log_N2O']['median']:.3f}; {product['z']['N2O']:+.2f}",
                f"{s['log_NH3']['median']:.3f}; {product['z']['NH3']:+.2f}",
                "—" if oxygen is None else f"{oxygen['median']:.2f}",
            ]
        )
    table = table_ax.table(
        cellText=rows,
        colLabels=headings,
        cellLoc="center",
        colLoc="center",
        bbox=[0.0, 0.0, 1.0, 1.0],
        colWidths=[0.17, 0.13, 0.12, 0.15, 0.15, 0.15, 0.13],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8.1)
    for (row, _column), cell in table.get_celld().items():
        cell.set_edgecolor("0.78")
        cell.set_linewidth(0.45)
        if row == 0:
            cell.set_facecolor("#f0eeee")
            cell.set_text_props(weight="bold", color=PALETTE["ink_black"])
        elif row == 2:
            cell.set_facecolor("#faf8f8")
    table[(1, 0)].set_text_props(color=VARIANTS["legacy"]["color"], weight="bold")
    table[(2, 0)].set_text_props(color=VARIANTS["corrected"]["color"], weight="bold")

    fig.text(
        0.5,
        0.071,
        r"$z=(\mathrm{mediana}_{A3}-\log_{10}X_{A0,eff})/\sigma_{68}$; "
        "z es un contraste posterior condicional y descriptivo, no una detección. "
        "A0/A3 efectiva: promedio VULCAN ponderado en presión.",
        ha="center",
        fontsize=8.1,
    )
    fig.text(
        0.5,
        0.037,
        "Ambas variantes usan los mismos datos LIFE (31 bins, una realización, ruido diagonal). "
        "ln Z se muestra por corrida y no como factor de Bayes: cambian la interfaz y el número de parámetros. "
        "El ajuste sigue tensionado y el perfil VULCAN no es isochem.",
        ha="center",
        fontsize=7.8,
    )

    PLOTS.mkdir(parents=True, exist_ok=True)
    png = PLOTS / f"{output_stem}.png"
    pdf = PLOTS / f"{output_stem}.pdf"
    fig.savefig(png, dpi=300, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    plt.close(fig)
    return png, pdf


def main() -> None:
    tags = {name: config["tag"] for name, config in VARIANTS.items()}
    expected_sample_rows = {"legacy": 7349, "corrected": 7479}
    raw_validation = {
        variant: validate_raw_products(tag, expected_sample_rows[variant])
        for variant, tag in tags.items()
    }
    results = {variant: load_result(tag) for variant, tag in tags.items()}
    posterior = {variant: load_posterior(tag) for variant, tag in tags.items()}
    spectra = {variant: load_spectrum(tag) for variant, tag in tags.items()}
    pt_products = {variant: load_pt(tag) for variant, tag in tags.items()}
    log_x_products = {variant: load_log_x(tag) for variant, tag in tags.items()}

    if posterior["legacy"]["samples"].shape[0] != expected_sample_rows["legacy"]:
        raise ValueError("Legacy posterior row count changed")
    corrected_manifest_path = RESULTS / (
        "proxima_A3_100h_O2_fixedBlack1bar_noxtol_"
        "proxima_A3_100h_O2_fixedBlack1bar_noxtol_postprocess_manifest.json"
    )
    recovery_manifest = json.loads(corrected_manifest_path.read_text(encoding="utf-8"))
    if recovery_manifest["dataset_sha256"].upper() != sha256(LIFE_DATA).upper():
        raise ValueError("Corrected and legacy runs do not share the recorded LIFE dataset")
    for variant in VARIANTS:
        if results[variant]["n_live"] != 800:
            raise ValueError(f"Wrong live-point count for {variant}")
        if not np.isfinite(spectra[variant]).all() or not np.isfinite(pt_products[variant]).all():
            raise ValueError(f"Non-finite spectral/PT product for {variant}")

    profiles = load_profiles()
    references = {
        scenario: {
            molecule: log10_column_averaged_mixing_ratio(profile, molecule)
            for molecule in MOLECULES
        }
        for scenario, profile in profiles.items()
    }
    products: dict[str, dict[str, object]] = {}
    for variant in VARIANTS:
        sample = posterior[variant]
        columns = {name: index for index, name in enumerate(sample["header"])}
        posterior_values = {
            molecule: sample["samples"][:, columns[f"log_{molecule}"]]
            for molecule in MOLECULES
        }
        summary = sample["summary"]
        z_values = {
            molecule: posterior_z(summary[f"log_{molecule}"], references["A0"][molecule])
            for molecule in MOLECULES
        }
        products[variant] = {
            "posterior": posterior_values,
            "summary": summary,
            "metadata": results[variant],
            "z": z_values,
            "samples": sample["samples"],
            "header": sample["header"],
        }

    residual_context = load_residual_context(spectra)
    output_stem = "retrieval_A3_100h_legacy_vs_o2_fixed_surface_recovery_proxima"
    png, pdf = make_figure(profiles, references, products, residual_context, output_stem)

    TABLES.mkdir(parents=True, exist_ok=True)
    summary_path = TABLES / f"{output_stem}_summary.json"
    residual_path = TABLES / f"{output_stem}_residuals.csv"
    summary_document = {
        "question": "A3 100 h posterior recovery and corrected-interface comparison",
        "dataset": str(LIFE_DATA),
        "dataset_sha256": residual_context["dataset_sha256"],
        "bins": 31,
        "noise_model": "diagonal LIFE classic; one realization",
        "a0_effective_log10_vmr": references["A0"],
        "a3_effective_log10_vmr": references["A3"],
        "variants": {},
        "raw_multinest_validation": raw_validation,
        "postprocessing_manifest": str(corrected_manifest_path),
        "figure": {"png": str(png), "pdf": str(pdf)},
        "caveat": (
            "z values are conditional descriptive posterior distances; neither a formal detection "
            "nor a Bayes factor between the runs. Isochemical profiles remain mismatched to VULCAN."
        ),
    }
    for variant in VARIANTS:
        product = products[variant]
        summary_document["variants"][variant] = {
            "label": VARIANTS[variant]["label"],
            "n_parameters": results[variant]["n_params"],
            "n_live": results[variant]["n_live"],
            "ln_Z": results[variant]["ln_z"],
            "ln_Z_error": results[variant]["ln_z_err"],
            "chi2": results[variant]["chi2"],
            "chi2_red": results[variant]["chi2_red"],
            "dof": results[variant]["dof"],
            "posterior_rows": posterior[variant]["count"],
            "parameters": product["summary"],
            "z_descriptive": product["z"],
            "median_spectrum_residual_chi2": residual_context["residuals"][variant]["chi2_median"],
            "median_spectrum_residual_rms_sigma": residual_context["residuals"][variant]["rms_median"],
            "bins_over_3sigma": residual_context["residuals"][variant]["n_over_3sigma"],
            "pt_shape": list(pt_products[variant].shape),
            "log_x_numeric_rows": log_x_products[variant]["numeric_rows"],
            "samples_file_sha256": sha256(sample_path(tags[variant])),
            "results_file_sha256": sha256(result_path(tags[variant])),
        }
    summary_path.write_text(json.dumps(summary_document, indent=2) + "\n", encoding="utf-8")

    with residual_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "wavelength_um",
                "observed_Fp",
                "sigma_Fp_diagonal",
                "A3_truth_Fp",
                "noise_only_sigma",
                "legacy_residual_sigma",
                "corrected_residual_sigma",
                "corrected_truth_minus_median_sigma",
            ]
        )
        context = residual_context
        for index, wavelength in enumerate(context["wl"]):
            writer.writerow(
                [
                    f"{wavelength:.9f}",
                    f"{context['observed'][index]:.12e}",
                    f"{context['sigma'][index]:.12e}",
                    f"{context['truth'][index]:.12e}",
                    f"{context['noise_sigma'][index]:.8f}",
                    f"{context['residuals']['legacy']['residual_sigma'][index]:.8f}",
                    f"{context['residuals']['corrected']['residual_sigma'][index]:.8f}",
                    f"{context['residuals']['corrected']['truth_minus_median_sigma'][index]:.8f}",
                ]
            )

    for variant in VARIANTS:
        product = products[variant]
        print(
            f"{variant}: lnZ={results[variant]['ln_z']:.2f}±{results[variant]['ln_z_err']:.2f}; "
            f"chi2red={results[variant]['chi2_red']:.2f} (dof={results[variant]['dof']}); "
            f"Rp_ref={product['summary']['R_p_ref']['median']:.4f} R_E; "
            f"logN2O={product['summary']['log_N2O']['median']:.4f}; "
            f"logNH3={product['summary']['log_NH3']['median']:.4f}; "
            + (
                f"logO2={product['summary']['log_O2']['median']:.4f}; "
                if "log_O2" in product["summary"] else ""
            )
            + f"zN2O={product['z']['N2O']:+.2f}; zNH3={product['z']['NH3']:+.2f}; "
            f"median-residual-chi2={residual_context['residuals'][variant]['chi2_median']:.2f}"
        )
    print(f"A0 effective: logN2O={references['A0']['N2O']:.5f}; logNH3={references['A0']['NH3']:.5f}")
    print(f"A3 effective: logN2O={references['A3']['N2O']:.5f}; logNH3={references['A3']['NH3']:.5f}")
    print(f"PNG={png}")
    print(f"PDF={pdf}")
    print(f"SUMMARY={summary_path}")
    print(f"RESIDUALS={residual_path}")


if __name__ == "__main__":
    main()
