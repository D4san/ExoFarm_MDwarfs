"""Plot the Proxima A3 fixed-bottom retrieval audit at 10, 100, and 240 h.

The figure separates the VULCAN vertical profiles from the isochemical
posterior densities so their vertical and scalar-abundance interpretations do
not share an axis. It is an audit product and never modifies canonical plots.
"""

from __future__ import annotations

import argparse
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
STYLE_DIR = REPO / "Transmission_Spectroscopy" / "notebooks"
sys.path.insert(0, str(STYLE_DIR))
from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE
from retrieval_reference import log10_column_averaged_mixing_ratio


CAMPAIGN_DIR = (
    REPO
    / "Thermal_Emission_Spectroscopy"
    / "outputs"
    / "life_proxima_b_earthlike_v1"
)
RETRIEVAL_DIR = (
    CAMPAIGN_DIR
    / "retrievals"
    / "POSEIDON_output"
    / "proxima_b_earthlike"
    / "retrievals"
)
PROFILE_DIR = REPO / "Transmission_Spectroscopy" / "profiles"
PLOTS_DIR = CAMPAIGN_DIR / "plots"
HOURS = (10, 100, 240)
MOLECULES = ("N2O", "NH3")
MOLECULE_LABELS = {"N2O": r"N$_2$O", "NH3": r"NH$_3$"}
PROFILE_STEMS = {
    "A0": "Proxima_b_A0_PreAgri_chem.txt",
    "A3": "Proxima_b_A3_Extreme_chem.txt",
}
PROFILE_COLORS = {
    "A0": PALETTE["scenario_green"],
    "A3": PALETTE["scenario_pink"],
}
REFERENCE_COLORS = {
    "A0": PALETTE["deep_moss"],
    "A3": PALETTE["dark_amaranth"],
}
TIME_COLORS = {
    10: PALETTE["terracotta_mauve"],
    100: PALETTE["charcoal_violet"],
    240: PALETTE["rusty_spice"],
}
TIME_STYLES = {10: "-", 100: "--", 240: "-."}
PROFILE_FLOOR = 1.0e-30
EXPECTED_SAMPLE_COLUMNS = (
    "R_p_ref",
    "a1",
    "a2",
    "log_P1",
    "log_P2",
    "log_P3",
    "T_ref",
    "log_H2O",
    "log_CO2",
    "log_CH4",
    "log_O3",
    "log_N2O",
    "log_NH3",
)
RAW_SUFFIXES = (
    "-.txt",
    "-ev.dat",
    "-live.points",
    "-phys_live.points",
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


def retrieval_stem(hours: int) -> str:
    """Return the fixed-bottom audit basename used by POSEIDON."""
    base = f"proxima_A3_{hours}h_fixedP1bar_noxtol"
    return f"{base}_{base}"


def audit_prefix(hours: int) -> str:
    """Return the prefix shared by POSEIDON and MultiNest products."""
    return RETRIEVAL_DIR / "MultiNest_raw" / retrieval_stem(hours)


def _assert_no_nonfinite_tokens(path: Path) -> None:
    """Reject textual NaN/Inf markers in an output artifact."""
    contents = path.read_text(encoding="utf-8", errors="replace")
    if re.search(r"(?i)(?<![a-z])(?:nan|inf(?:inity)?)(?![a-z])", contents):
        raise ValueError(f"NaN/Inf token found in {path}")


def _numeric_block_rows(path: Path) -> int:
    """Validate all numeric rows in the block-formatted log-X export."""
    numeric_rows = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        fields = line.split()
        if not fields:
            continue
        try:
            values = np.asarray([float(value) for value in fields], dtype=float)
        except ValueError:
            continue
        if values.size != 6 or not np.isfinite(values).all():
            raise ValueError(f"Invalid numeric row in {path}: {line}")
        numeric_rows += 1
    if numeric_rows != 700:
        raise ValueError(
            f"Expected seven 100-level log-X blocks in {path}; "
            f"got {numeric_rows} rows"
        )
    return numeric_rows


def load_result_metadata(hours: int) -> dict[str, float | int]:
    """Parse evidence and fit diagnostics from one POSEIDON results file."""
    path = RETRIEVAL_DIR / "results" / f"{retrieval_stem(hours)}_results.txt"
    if not path.is_file():
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    patterns = {
        "n_params": r"N_params\s*=\s*(\d+)",
        "n_live": r"N_live\s*=\s*(\d+)",
        "ln_z": r"->\s*ln Z\s*=\s*([+-]?[\d.]+(?:[eE][+-]?\d+)?)",
        "ln_z_err": (
            r"->\s*ln Z\s*=\s*[+-]?[\d.]+(?:[eE][+-]?\d+)?"
            r"\s*\+/-\s*([\d.]+(?:[eE][+-]?\d+)?)"
        ),
        "chi2_red": r"->\s*chi\^2_red\s*=\s*([\d.]+(?:[eE][+-]?\d+)?)",
        "dof": r"->\s*degrees of freedom\s*=\s*(\d+)",
    }
    parsed: dict[str, float | int] = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match is None:
            raise ValueError(f"Could not parse {key} from {path}")
        if key in ("n_params", "n_live", "dof"):
            parsed[key] = int(match.group(1))
        else:
            parsed[key] = float(match.group(1))
    if parsed["n_params"] != 13 or parsed["n_live"] != 800:
        raise ValueError(f"Unexpected retrieval configuration in {path}: {parsed}")
    return parsed


def load_retrieval(hours: int) -> dict:
    """Validate the complete POSEIDON/MultiNest product set for one time."""
    stem = retrieval_stem(hours)
    prefix = audit_prefix(hours)
    results = RETRIEVAL_DIR / "results" / f"{stem}_results.txt"
    samples_path = RETRIEVAL_DIR / "samples" / f"{stem}_samples.txt"
    spectrum_path = RETRIEVAL_DIR / "samples" / f"{stem}_spectrum_retrieved.txt"
    pt_path = RETRIEVAL_DIR / "samples" / f"{stem}_PT_retrieved.txt"
    log_x_path = RETRIEVAL_DIR / "samples" / f"{stem}_log_X_retrieved.txt"
    raw_paths = [Path(f"{prefix}{suffix}") for suffix in RAW_SUFFIXES]
    required = [results, samples_path, spectrum_path, pt_path, log_x_path, *raw_paths]
    missing = [
        str(path)
        for path in required
        if not path.is_file() or path.stat().st_size == 0
    ]
    if missing:
        raise FileNotFoundError(f"Missing or empty {hours} h products: {missing}")

    for path in required:
        _assert_no_nonfinite_tokens(path)

    header = tuple(
        name.strip()
        for name in samples_path.open(encoding="utf-8").readline().split("|")
    )
    if header != EXPECTED_SAMPLE_COLUMNS:
        raise ValueError(f"Unexpected sample columns at {samples_path}: {header}")
    samples = np.loadtxt(samples_path, skiprows=1)
    samples = np.atleast_2d(np.asarray(samples, dtype=float))
    if samples.shape[0] < 1000 or not np.isfinite(samples).all():
        raise ValueError(
            f"Invalid posterior samples in {samples_path}: {samples.shape}"
        )

    spectrum = np.atleast_2d(np.loadtxt(spectrum_path, skiprows=1))
    pt = np.atleast_2d(np.loadtxt(pt_path, skiprows=1))
    if spectrum.shape != (3219, 6) or not np.isfinite(spectrum).all():
        raise ValueError(
            f"Invalid retrieved spectrum in {spectrum_path}: {spectrum.shape}"
        )
    if pt.shape != (100, 6) or not np.isfinite(pt).all():
        raise ValueError(f"Invalid retrieved P-T profile in {pt_path}: {pt.shape}")
    log_x_rows = _numeric_block_rows(log_x_path)

    result = results.read_text(encoding="utf-8", errors="replace")
    if "log_N2O" not in result or "log_NH3" not in result:
        raise ValueError(f"Missing retrieved species in {results}")

    if hours == 100:
        log_path = (
            CAMPAIGN_DIR
            / "retrievals"
            / "proxima_A3_100h_fixedP1bar_noxtol.retry1.launch.log"
        )
        if not log_path.is_file():
            raise FileNotFoundError(log_path)
        log = log_path.read_text(encoding="utf-8", errors="replace")
        if "Sampling finished. Exiting MultiNest" not in log or "Traceback" in log:
            raise ValueError(
                f"The 100 h MultiNest log does not show clean completion: {log_path}"
            )

    metadata = load_result_metadata(hours)
    live_points = np.atleast_2d(np.loadtxt(Path(f"{prefix}-live.points")))
    physical_live_points = np.atleast_2d(np.loadtxt(Path(f"{prefix}-phys_live.points")))
    equal_weight_points = np.atleast_2d(
        np.loadtxt(Path(f"{prefix}-post_equal_weights.dat"))
    )
    if live_points.shape[0] != metadata["n_live"]:
        raise ValueError(f"Expected {metadata['n_live']} live points at {prefix}")
    if physical_live_points.shape[0] != metadata["n_live"]:
        raise ValueError(
            f"Expected {metadata['n_live']} physical live points at {prefix}"
        )
    if equal_weight_points.shape[0] != samples.shape[0]:
        raise ValueError(f"Sample/MultiNest row count mismatch at {prefix}")
    if not all(
        np.isfinite(values).all()
        for values in (live_points, physical_live_points, equal_weight_points)
    ):
        raise ValueError(f"Non-finite live/equal-weight points in {prefix}")

    columns = {name: index for index, name in enumerate(header)}
    posterior = {
        molecule: samples[:, columns[f"log_{molecule}"]]
        for molecule in MOLECULES
    }
    summary: dict[str, dict[str, float]] = {}
    for molecule, values in posterior.items():
        q16, median, q84 = np.percentile(values, (16.0, 50.0, 84.0))
        sigma68 = 0.5 * (q84 - q16)
        summary[molecule] = {
            "q16": float(q16),
            "median": float(median),
            "q84": float(q84),
            "sigma68": float(sigma68),
        }
    q16, median, q84 = np.percentile(samples[:, columns["R_p_ref"]], (16, 50, 84))
    return {
        "hours": hours,
        "samples": samples,
        "posterior": posterior,
        "summary": summary,
        "radius": {"q16": float(q16), "median": float(median), "q84": float(q84)},
        "metadata": metadata,
        "sample_count": int(samples.shape[0]),
        "spectrum_shape": tuple(spectrum.shape),
        "pt_shape": tuple(pt.shape),
        "log_x_numeric_rows": log_x_rows,
    }


def load_profiles() -> dict[str, np.ndarray]:
    """Load finite VULCAN A0/A3 chemistry profiles for the selected species."""
    profiles = {}
    for scenario, filename in PROFILE_STEMS.items():
        path = PROFILE_DIR / filename
        profile = np.genfromtxt(path, names=True)
        required = ("PRESS", *MOLECULES)
        if any(name not in profile.dtype.names for name in required):
            raise ValueError(f"Missing columns in {path}: {profile.dtype.names}")
        if not np.isfinite(profile["PRESS"]).all() or np.any(profile["PRESS"] <= 0):
            raise ValueError(f"Invalid pressure grid in {path}")
        for molecule in MOLECULES:
            if (
                not np.isfinite(profile[molecule]).all()
                or np.any(profile[molecule] < 0)
            ):
                raise ValueError(f"Invalid {molecule} profile in {path}")
        profiles[scenario] = profile
    return profiles


def format_result_row(hours: int, product: dict, references: dict) -> list[str]:
    """Format the compact fit/posterior/z table row for one integration time."""
    metadata = product["metadata"]
    radius = product["radius"]
    radius_sigma = 0.5 * (radius["q84"] - radius["q16"])
    row = [
        f"{hours} h",
        f"{metadata['ln_z']:.2f} ± {metadata['ln_z_err']:.2f}",
        f"{metadata['chi2_red']:.2f} ({metadata['dof']})",
        f"{radius['median']:.3f} ± {radius_sigma:.3f}",
    ]
    for molecule in MOLECULES:
        summary = product["summary"][molecule]
        z = (summary["median"] - references["A0"][molecule]) / summary["sigma68"]
        row.append(f"{summary['median']:.2f}; {z:+.2f}σ")
    return row


def plot_audit(output_dir: Path) -> tuple[Path, Path]:
    """Create a profile/posterior atlas with fit and signed-z diagnostics."""
    profiles = load_profiles()
    products = {hours: load_retrieval(hours) for hours in HOURS}
    references = {
        scenario: {
            molecule: log10_column_averaged_mixing_ratio(profile, molecule)
            for molecule in MOLECULES
        }
        for scenario, profile in profiles.items()
    }

    fig = plt.figure(figsize=(12.8, 9.1))
    grid = fig.add_gridspec(
        2,
        2,
        left=0.085,
        right=0.985,
        bottom=0.285,
        top=0.755,
        wspace=0.22,
        hspace=0.38,
    )

    for row, molecule in enumerate(MOLECULES):
        profile_ax = fig.add_subplot(grid[row, 0])
        posterior_ax = fig.add_subplot(grid[row, 1])
        profile_x_values = []
        for scenario in ("A0", "A3"):
            profile = profiles[scenario]
            abundance = np.log10(np.clip(profile[molecule], PROFILE_FLOOR, None))
            profile_x_values.append(abundance)
            profile_ax.plot(
                abundance,
                profile["PRESS"],
                color=PROFILE_COLORS[scenario],
                linewidth=2.0,
                label=f"{scenario} VULCAN",
            )

        a0_reference = references["A0"][molecule]
        a3_reference = references["A3"][molecule]
        for ax in (profile_ax, posterior_ax):
            ax.axvline(
                a0_reference,
                color=REFERENCE_COLORS["A0"],
                linestyle=":",
                linewidth=1.4,
                zorder=5,
            )
            ax.axvline(
                a3_reference,
                color=REFERENCE_COLORS["A3"],
                linestyle="-.",
                linewidth=1.3,
                zorder=5,
            )

        profile_ax.set_yscale("log")
        profile_ax.set_ylim(1.0, 5.0e-8)
        profile_lo = max(
            -30.5,
            min(float(np.min(values)) for values in profile_x_values)
            - 0.25,
        )
        profile_hi = min(
            0.0,
            max(float(np.max(values)) for values in profile_x_values)
            + 0.25,
        )
        profile_lo = min(profile_lo, a0_reference, a3_reference)
        profile_hi = max(profile_hi, a0_reference, a3_reference)
        profile_ax.set_xlim(profile_lo, profile_hi)
        profile_ax.grid(which="major", linestyle=":", alpha=0.32)
        profile_ax.grid(which="minor", linestyle=":", alpha=0.14)
        profile_ax.tick_params(direction="in", top=True, right=True, labelsize=8.5)
        profile_ax.minorticks_on()
        profile_ax.set_title(
            f"{MOLECULE_LABELS[molecule]} — VULCAN vertical profiles",
            fontsize=11.5,
        )
        profile_ax.set_xlabel(r"$\log_{10}$ volume mixing ratio")
        profile_ax.set_ylabel("Pressure [bar]")

        posterior_values = [products[hours]["posterior"][molecule] for hours in HOURS]
        posterior_lo = max(
            -13.0,
            min(float(np.percentile(values, 0.5)) for values in posterior_values)
            - 0.25,
        )
        posterior_hi = min(
            0.0,
            max(float(np.percentile(values, 99.5)) for values in posterior_values)
            + 0.25,
        )
        posterior_lo = min(posterior_lo, a0_reference, a3_reference)
        posterior_hi = max(posterior_hi, a0_reference, a3_reference)
        if posterior_hi - posterior_lo < 1.0:
            posterior_hi = posterior_lo + 1.0
        bin_edges = np.linspace(posterior_lo, posterior_hi, 48)
        for hours in HOURS:
            values = products[hours]["posterior"][molecule]
            density, _ = np.histogram(values, bins=bin_edges, density=True)
            color = TIME_COLORS[hours]
            style = TIME_STYLES[hours]
            posterior_ax.stairs(
                density,
                bin_edges,
                color=color,
                linewidth=1.8,
                linestyle=style,
                label=f"{hours} h",
            )
            posterior_ax.fill_between(
                bin_edges[:-1],
                density,
                step="post",
                color=color,
                alpha=0.10,
            )
            posterior_ax.axvline(
                products[hours]["summary"][molecule]["median"],
                color=color,
                linewidth=1.1,
                linestyle=style,
                alpha=0.88,
            )
        posterior_ax.set_xlim(posterior_lo, posterior_hi)
        posterior_ax.grid(axis="y", linestyle=":", alpha=0.30)
        posterior_ax.tick_params(direction="in", top=True, right=True, labelsize=8.5)
        posterior_ax.minorticks_on()
        posterior_ax.set_title(
            f"{MOLECULE_LABELS[molecule]} — isochemical posteriors",
            fontsize=11.5,
        )
        posterior_ax.set_xlabel(r"$\log_{10}$ volume mixing ratio")
        posterior_ax.set_ylabel("Posterior density")

    legend_handles = [
        Line2D([], [], color=PROFILE_COLORS["A0"], lw=2.0, label="A0 VULCAN profile"),
        Line2D([], [], color=PROFILE_COLORS["A3"], lw=2.0, label="A3 VULCAN profile"),
        Line2D(
            [], [], color=REFERENCE_COLORS["A0"], lw=1.4, ls=":",
            label="A0 efectiva",
        ),
        Line2D(
            [], [], color=REFERENCE_COLORS["A3"], lw=1.3, ls="-.",
            label="A3 efectiva",
        ),
        *[
            Line2D(
                [], [], color=TIME_COLORS[hours], lw=1.8,
                ls=TIME_STYLES[hours], label=f"Posterior {hours} h",
            )
            for hours in HOURS
        ],
    ]
    fig.legend(
        handles=legend_handles,
        loc="upper center",
        ncol=4,
        frameon=False,
        fontsize=8.7,
        columnspacing=1.6,
        handlelength=2.0,
        bbox_to_anchor=(0.53, 0.875),
    )
    fig.suptitle(
        "Proxima b — auditoría de retrieval A3 por tiempo de integración",
        y=0.975,
        fontsize=16,
    )
    fig.text(
        0.5,
        0.932,
        "POSEIDON · isochem · N_live=800 · límite negro fijo a 1 bar · "
        "sin x_tol ni inflación de errores",
        ha="center",
        fontsize=9.5,
    )

    table_ax = fig.add_axes([0.035, 0.075, 0.93, 0.155])
    table_ax.axis("off")
    headers = (
        "Integración",
        "ln Z ± σ",
        "χ²_red (dof)",
        r"$R_{p,ref}$ [$R_\oplus$]",
        r"log$_{10}X$(N$_2$O); z",
        r"log$_{10}X$(NH$_3$); z",
    )
    rows = [format_result_row(hours, products[hours], references) for hours in HOURS]
    table = table_ax.table(
        cellText=rows,
        colLabels=headers,
        cellLoc="center",
        colLoc="center",
        bbox=[0.0, 0.0, 1.0, 1.0],
        colWidths=[0.12, 0.15, 0.15, 0.17, 0.205, 0.205],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8.5)
    for (row, _column), cell in table.get_celld().items():
        cell.set_edgecolor("0.78")
        cell.set_linewidth(0.45)
        if row == 0:
            cell.set_facecolor("#f0eeee")
            cell.set_text_props(weight="bold", color=PALETTE["ink_black"])
        elif row % 2 == 0:
            cell.set_facecolor("#faf8f8")
    for index, hours in enumerate(HOURS, start=1):
        table[(index, 0)].set_text_props(color=TIME_COLORS[hours], weight="bold")

    fig.text(
        0.5,
        0.047,
        r"$z=(\mathrm{mediana}_{A3}-\log_{10}X_{A0,eff})/\sigma_{68}$; "
        "z es descriptivo, no una detección. "
        r"Perfiles VULCAN recortados sólo para visualización a $X=10^{-30}$.",
        ha="center",
        va="bottom",
        fontsize=8.0,
    )
    fig.text(
        0.5,
        0.018,
        "Ruido diagonal y una realización por tiempo; el ajuste isochem/VULCAN "
        "sigue tensionado "
        r"($\chi^2_\nu=5.27$ a 100 h; 13.07 a 240 h). "
        "ln Z no compara exposiciones distintas.",
        ha="center",
        va="bottom",
        fontsize=8.0,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    stem = "retrieval_A3_audit_profiles_posteriors_10_100_240h_proxima"
    png_path = output_dir / f"{stem}.png"
    pdf_path = output_dir / f"{stem}.pdf"
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)

    for hours in HOURS:
        product = products[hours]
        print(
            f"{hours} h: lnZ={product['metadata']['ln_z']:.2f} "
            f"+/- {product['metadata']['ln_z_err']:.2f}; "
            f"chi2red={product['metadata']['chi2_red']:.2f} "
            f"(dof={product['metadata']['dof']}); "
            f"samples={product['sample_count']}; "
            f"N2O={product['summary']['N2O']['median']:.3f}, "
            f"NH3={product['summary']['NH3']['median']:.3f}; "
            f"z_N2O={format_result_row(hours, product, references)[4].split('; ')[1]}, "
            f"z_NH3={format_result_row(hours, product, references)[5].split('; ')[1]}"
        )
    print(f"PNG={png_path}")
    print(f"PDF={pdf_path}")
    return png_path, pdf_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PLOTS_DIR,
        help="Directory for the audit PNG/PDF pair.",
    )
    args = parser.parse_args()
    plot_audit(args.output_dir.resolve())


if __name__ == "__main__":
    main()
