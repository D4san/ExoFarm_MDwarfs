"""Create the three publication-facing LIFE retrieval figures for Proxima.

The figures are built only from products that already exist in the campaign
directory.  The canonical retrieval matrix is A0--A3 at 10 h and 240 h, while
the presentation compares the two scientifically informative extremes A0 and
A3.  The available A3--1200 h retrieval is intentionally reported as an
excluded pilot and is not mixed into these figures.

Outputs
-------
``retrieval_global_spectra_proxima``
    Full LIFE wavelength range with forward spectrum, retrieved spectrum,
    posterior uncertainty, and the binned synthetic observations.
``retrieval_molecular_zooms_proxima``
    Three selected N2O/NH3 windows, using the same line and colour meanings.
``retrieval_profiles_posteriors_proxima``
    A3 marginal posterior samples with the A3 VULCAN profiles, the effective
    A0 pressure-column reference, posterior medians, and comparison metrics.
``retrieval_profiles_posteriors_proxima_4rows_audit``
    Optional audit view with A3 posterior rows for 10, 240, 500, and 1200 h;
    the latter two use the robust direct-LIFEsim retrieval products.
``retrieval_A1_A3_10_100_240h_audit_molecular_profiles_PT_proxima``
    Separate audit view with one row per integration time (10, 100, and 240 h),
    focused on the N2O and NH3 posteriors, their VULCAN vertical profiles,
    A0-effective references, signed posterior distances, retrieved P--T, and
    per-dataset ln Z / reduced chi-square annotations. Its compact grid and
    callout styling are adapted from ``plot_profiles_posteriors`` above.
``retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima``
    Official A1/A3 comparison with one row per exposure (1, 10, and 100 h),
    six molecular species (O2 omitted from the display), and a P--T column.
    The official default (V2) uses profile-aware dynamic x limits clamped to
    the abundance prior [-12, -1]. It uses an approximately 7.28-in exported
    full-width layout and the selected independent A1-1 h
    realization (seed 2125532119). Each row repeats the A1/A3 VULCAN abundance
    profiles alongside the exposure-specific posterior. A0 is labeled once
    above each species column, and a compact equation defines the descriptive
    posterior offset from that reference.
    The 2026-10-20 update reads the accepted A3--100 h replacement directly
    from its separate campaign. The other five runs retain their original
    sources; a JSON sidecar records the configuration version of each case.
``retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima_full_prior_xlim``
    Preserved V1 companion with the full abundance-prior range [-12, -1].
``retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima_dynamic_xlim``
    Reproducible alias of the official V2 profile-aware view.
``retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima_posterior_xlim``
    Layout-matched companion whose per-species limits are based only on pooled
    posterior samples and clamped to the abundance prior [-12, -1].
``retrieval_A1_1h_selected_official_vs_previous_N2O_NH3_PT_proxima``
    A1-1 h comparison of the selected realization (seed 2125532119) with the
    previous official candidate (seed 368516754), retained as sensitivity.

The direct planetary-flux convention is preserved throughout:
``F_p`` is in W m^-2 m^-1, with the plotted ordinate scaled by 10^-13 only for
readability.  High-resolution forward and retrieved spectra are interpolated
onto 250 points in the global panel and 75 points in each zoom for display;
the underlying products remain unchanged.
"""

from __future__ import annotations

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
from matplotlib.lines import Line2D
from matplotlib.offsetbox import AnchoredOffsetbox, TextArea, VPacker
from matplotlib.patches import Patch


REPO = Path(__file__).resolve().parents[2]
STYLE_DIR = REPO / "Transmission_Spectroscopy" / "notebooks"
sys.path.insert(0, str(STYLE_DIR))
from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE
from retrieval_reference import log10_column_averaged_mixing_ratio


CAMPAIGN_ID = "life_proxima_b_earthlike_v1"
CAMPAIGN_DIR = REPO / "Thermal_Emission_Spectroscopy" / "outputs" / CAMPAIGN_ID
PLOTS_DIR = CAMPAIGN_DIR / "plots"
FORWARD_DIR = CAMPAIGN_DIR / "forward_emission"
LIFE_DATA_DIR = CAMPAIGN_DIR / "life_data"
SAMPLES_DIR = (
    CAMPAIGN_DIR
    / "retrievals"
    / "POSEIDON_output"
    / "proxima_b_earthlike"
    / "retrievals"
    / "samples"
)
RESULTS_DIR = SAMPLES_DIR.parent / "results"
PROFILE_DIR = REPO / "Transmission_Spectroscopy" / "profiles"

PLOT_SCENARIOS = ("A0", "A3")
PROFILE_POSTERIOR_SCENARIO = "A3"
PROFILE_REFERENCE_SCENARIO = "A0"
HOURS = (10, 240)
SCENARIOS = {
    "A0": {
        "label": "A0: Pre-agricultural",
        "color": PALETTE["scenario_green"],
        "profile_stem": "Proxima_b_A0_PreAgri",
    },
    "A1": {
        "label": "A1: Current Earth",
        "color": PALETTE["scenario_cyan"],
        "profile_stem": "Proxima_b_A1_Current",
    },
    "A2": {
        "label": "A2: Moderate ExoFarm",
        "color": PALETTE["scenario_violet"],
        "profile_stem": "Proxima_b_A2_Moderate",
    },
    "A3": {
        "label": "A3: Extreme ExoFarm",
        "color": PALETTE["scenario_pink"],
        "profile_stem": "Proxima_b_A3_Extreme",
    },
}

MOLECULES = ("H2O", "CO2", "CH4", "O3", "N2O", "NH3")
MOLECULE_LABELS = {
    "H2O": r"H$_2$O",
    "CO2": r"CO$_2$",
    "CH4": r"CH$_4$",
    "O3": r"O$_3$",
    "N2O": r"N$_2$O",
    "NH3": r"NH$_3$",
    "O2": r"O$_2$",
}
PROFILE_X_AXIS_LABELS = {
    "H2O": r"log(X$_{\mathrm{H_2O}}$)",
    "CO2": r"log(X$_{\mathrm{CO_2}}$)",
    "CH4": r"log(X$_{\mathrm{CH_4}}$)",
    "O3": r"log(X$_{\mathrm{O_3}}$)",
    "N2O": r"log(X$_{\mathrm{N_2O}}$)",
    "NH3": r"log(X$_{\mathrm{NH_3}}$)",
    "O2": r"log(X$_{\mathrm{O_2}}$)",
}
SAMPLE_COLUMNS = (
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
    "x_tol",
    "log_P_surf",
)
SAMPLE_INDEX = {name.removeprefix("log_"): i for i, name in enumerate(SAMPLE_COLUMNS) if name.startswith("log_")}

WAVELENGTH_RANGE = (3.8, 19.0)
FLUX_SCALE = 1.0e-13
PROFILE_FLOOR = 1.0e-30
GLOBAL_DISPLAY_POINTS = 250
ZOOM_DISPLAY_POINTS = 75
RETRIEVED_2SIGMA_ALPHA = 0.025
RETRIEVED_1SIGMA_ALPHA = 0.05
RETRIEVED_MEDIAN_ALPHA = 0.70
TRUE_SPECTRUM_ALPHA = 0.50
OBSERVATION_MARKERSIZE_GLOBAL = 5.8
OBSERVATION_MARKERSIZE_ZOOM = 6.2
OBSERVATION_MARKER_EDGE = PALETTE["dim_grey"]
OBSERVATION_MARKER_EDGE_WIDTH_GLOBAL = 0.90
OBSERVATION_MARKER_EDGE_WIDTH_ZOOM = 0.95
ZOOM_WINDOWS = (
    (7.15, 8.35, r"N$_2$O (7.15 - 8.35 $\mu$m)"),
    (10.0, 11.25, r"NH$_3$ (10.0 - 11.25 $\mu$m)"),
    (16.25, 17.75, r"N$_2$O (16.25 - 17.75 $\mu$m)"),
)

# Match the transmission-plot semantics: vivid scenario colours identify the
# retrieved model, darker companion colours identify the true/observed case,
# and marker shape distinguishes the two scenarios in the data.
RETRIEVED_COLORS = {
    "A0": PALETTE["scenario_green"],
    "A3": PALETTE["scenario_pink"],
}
TRUE_COLORS = {
    "A0": PALETTE["deep_moss"],
    "A3": PALETTE["dark_amaranth"],
}
OBSERVATION_COLORS = TRUE_COLORS.copy()
SCENARIO_MARKERS = {
    "A0": "o",
    "A3": "d",
}
AUDIT_MOLECULES = ("N2O", "NH3")
OFFICIAL_PROFILE_MOLECULES = ("H2O", "CO2", "CH4", "O3", "N2O", "NH3")
OFFICIAL_MATRIX_POSTERIOR_MOLECULES = ("N2O", "NH3", "H2O", "CO2", "CH4", "O3")
# Keep these display bounds synchronized with prior_ranges in
# run_life_retrieval.py. The official runs use a distinct O2 prior.
LOG_VMR_PRIOR_LIMITS = (-12.0, -1.0)
LOG_O2_PRIOR_LIMITS = (-6.0, float(np.log10(0.5)))
LOG_VMR_PRIOR_TICKS = (-12.0, -9.0, -6.0, -3.0, -1.0)
LOG_O2_PRIOR_TICKS = (-6.0, -4.0, -2.0, LOG_O2_PRIOR_LIMITS[1])
AUDIT_TIME_RUN_STEMS = {
    10: {
        "A1": "proxima_A1_10h_O2_fixedBlack1bar_noxtol_MPI6R1",
        "A3": (
            "proxima_A3_10h_O2_fixedBlack1bar_noxtol_"
            "proxima_A3_10h_O2_fixedBlack1bar_noxtol"
        ),
    },
    100: {
        "A1": "proxima_A1_100h_O2_fixedBlack1bar_noxtol_MPI6R1",
        "A3": (
            "proxima_A3_100h_O2_fixedBlack1bar_noxtol_"
            "proxima_A3_100h_O2_fixedBlack1bar_noxtol"
        ),
    },
    240: {
        "A1": "proxima_A1_240h_O2_fixedBlack1bar_noxtol_MPI6_AUDIT",
        "A3": "proxima_A3_240h_O2_fixedBlack1bar_noxtol_MPI6_AUDIT",
    },
}
OFFICIAL_TIME_RUN_STEMS = {
    1: {
        "A1": "proxima_A1_1h_O2_fixedBlack1bar_noxtol_MPI6_NOISE2",
        "A3": "proxima_A3_1h_O2_fixedBlack1bar_noxtol_MPI6_OFFICIAL1h",
    },
    10: AUDIT_TIME_RUN_STEMS[10],
    100: {
        **AUDIT_TIME_RUN_STEMS[100],
        "A3": "proxima_A3_100h_O2_fixedBlack1bar_noxtol_BIN1_20261017",
    },
}
# Read the accepted replacement in place. Historical audit products retain
# their original roots and stems; no retrieval files are copied or renamed.
OFFICIAL_RUN_ROOTS = {
    (100, "A3"): (
        CAMPAIGN_DIR
        / "retrievals/a3_100h_binning_corrected_mpi14_resume_20261018/products"
    ),
}
CORRECTED_MATRIX_FULL_RUN_STEMS = {
    1: {
        "A1": "proxima_A1_1h_O2_fixedBlack1bar_noxtol_BIN1_20261021_MATRIX_A1_1h_full",
        "A3": "proxima_A3_1h_O2_fixedBlack1bar_noxtol_BIN1_20261020_1h_full",
    },
    10: {
        "A1": "proxima_A1_10h_O2_fixedBlack1bar_noxtol_BIN1_20261021_MATRIX_A1_10h_full",
        "A3": "proxima_A3_10h_O2_fixedBlack1bar_noxtol_BIN1_20261020_10h_full",
    },
    100: {
        "A1": "proxima_A1_100h_O2_fixedBlack1bar_noxtol_BIN1_20261021_MATRIX_A1_100h_full",
        "A3": "proxima_A3_100h_O2_fixedBlack1bar_noxtol_BIN1_20261017",
    },
}
CORRECTED_MATRIX_FULL_RUN_ROOTS = {
    (1, "A1"): CAMPAIGN_DIR / (
        "retrievals/a1_a3_corrected_binning_matrix_loo_20261021_r01/"
        "runs/A1_1h_full/POSEIDON_output/proxima_b_earthlike/retrievals"
    ),
    (10, "A1"): CAMPAIGN_DIR / (
        "retrievals/a1_a3_corrected_binning_matrix_loo_20261021_r01/"
        "runs/A1_10h_full/POSEIDON_output/proxima_b_earthlike/retrievals"
    ),
    (100, "A1"): CAMPAIGN_DIR / (
        "retrievals/a1_a3_corrected_binning_matrix_loo_20261021_r01/"
        "runs/A1_100h_full/POSEIDON_output/proxima_b_earthlike/retrievals"
    ),
    (1, "A3"): CAMPAIGN_DIR / (
        "retrievals/a3_1_10h_binning_corrected_loo_20261020_r03/"
        "runs/A3_1h_full/POSEIDON_output/proxima_b_earthlike/retrievals"
    ),
    (10, "A3"): CAMPAIGN_DIR / (
        "retrievals/a3_1_10h_binning_corrected_loo_20261020_r03/"
        "runs/A3_10h_full/POSEIDON_output/proxima_b_earthlike/retrievals"
    ),
    (100, "A3"): CAMPAIGN_DIR / (
        "retrievals/a3_100h_binning_corrected_mpi14_resume_20261018/products"
    ),
}
CORRECTED_MATRIX_SHARED_INPUTS = (
    REPO / "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/"
    "retrievals/a1_a3_corrected_binning_matrix_loo_20261021_r01/selected_scope.json",
    REPO / "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/"
    "retrievals/a1_a3_corrected_binning_matrix_loo_20261021_r01/manifest.csv",
    REPO / "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/"
    "retrievals/a3_1_10h_binning_corrected_loo_20261020_r03/selected_scope.json",
    REPO / "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/"
    "retrievals/a3_1_10h_binning_corrected_loo_20261020_r03/manifest.csv",
    REPO / "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/"
    "retrievals/a3_100h_binning_corrected_mpi14_resume_20261018/selected_scope.json",
    REPO / "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/"
    "retrievals/a3_100h_binning_corrected_mpi14_resume_20261018/"
    "operator_preflight_mpi14_retry01.json",
)
_MATRIX_R01 = (
    "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/"
    "retrievals/a1_a3_corrected_binning_matrix_loo_20261021_r01"
)
_A3_R03 = (
    "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/"
    "retrievals/a3_1_10h_binning_corrected_loo_20261020_r03"
)
_A3_100H = (
    "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/"
    "retrievals/a3_100h_binning_corrected_mpi14_resume_20261018"
)
CORRECTED_MATRIX_CASE_SOURCES = {
    (1, "A1"): {
        "campaign": _MATRIX_R01,
        "run_id": "A1_1h_full",
        "validation_status": "sampling_exit_0; independent_final_audit_PASS_2026-10-28",
        "dataset_sha256_expected": (
            "93fb65765101950063d5aa9a3dafae4df"
            "38273292cb0e3349e94b8a34516cfcc"
        ),
        "paths": {
            "dataset": REPO / (
                "Thermal_Emission_Spectroscopy/outputs/"
                "life_proxima_b_earthlike_v1/life_data/"
                "LIFE_proxima_A1_1h_O2_fixedBlack1bar_noiseRepeat2.dat"
            ),
            "configuration": REPO / f"{_MATRIX_R01}/resolved/A1_1h_full.json",
            "runtime_operator": REPO / f"{_MATRIX_R01}/runtime/operators/A1_1h_full.json",
        },
    },
    (10, "A1"): {
        "campaign": _MATRIX_R01,
        "run_id": "A1_10h_full",
        "validation_status": "sampling_exit_0; independent_final_audit_PASS_2026-10-28",
        "dataset_sha256_expected": (
            "ed39ae6dc5b8ff0d5c8aca3d126a2945"
            "343a289be30f3b8d9e8e72c434ee9b8f"
        ),
        "paths": {
            "dataset": REPO / (
                "Thermal_Emission_Spectroscopy/outputs/"
                "life_proxima_b_earthlike_v1/life_data/"
                "LIFE_proxima_A1_10h.dat"
            ),
            "configuration": REPO / f"{_MATRIX_R01}/resolved/A1_10h_full.json",
            "runtime_operator": REPO / f"{_MATRIX_R01}/runtime/operators/A1_10h_full.json",
        },
    },
    (100, "A1"): {
        "campaign": _MATRIX_R01,
        "run_id": "A1_100h_full",
        "validation_status": "sampling_exit_0; independent_final_audit_PASS_2026-10-28",
        "dataset_sha256_expected": (
            "d66c886238a2916312c645589be86018"
            "28fbf0a7cd2f02a383ef1d6a3454b5e3"
        ),
        "paths": {
            "dataset": REPO / (
                "Thermal_Emission_Spectroscopy/outputs/"
                "life_proxima_b_earthlike_v1/life_data/"
                "LIFE_proxima_A1_100h_O2_fixedBlack1bar_noxtol_audit.dat"
            ),
            "configuration": REPO / f"{_MATRIX_R01}/resolved/A1_100h_full.json",
            "runtime_operator": REPO / f"{_MATRIX_R01}/runtime/operators/A1_100h_full.json",
        },
    },
    (1, "A3"): {
        "campaign": _A3_R03,
        "run_id": "A3_1h_full",
        "validation_status": "previously_validated_corrected_bin_baseline",
        "dataset_sha256_expected": (
            "a3043e5de76a834983949e6eca12636e"
            "a4de174ebdb2db0853155282c100dee2"
        ),
        "paths": {
            "dataset": REPO / (
                "Thermal_Emission_Spectroscopy/outputs/"
                "life_proxima_b_earthlike_v1/life_data/"
                "LIFE_proxima_A3_1h_O2_fixedBlack1bar_official.dat"
            ),
            "configuration": REPO / f"{_A3_R03}/resolved/A3_1h_full.json",
            "runtime_operator": REPO / f"{_A3_R03}/runtime/operators/A3_1h_full.json",
        },
    },
    (10, "A3"): {
        "campaign": _A3_R03,
        "run_id": "A3_10h_full",
        "validation_status": "previously_validated_corrected_bin_baseline",
        "dataset_sha256_expected": (
            "46a026504b9b9521fa29407a501169b9d3cfc4"
            "33de40a91b8ade86d7767abb5b"
        ),
        "paths": {
            "dataset": REPO / (
                "Thermal_Emission_Spectroscopy/outputs/"
                "life_proxima_b_earthlike_v1/life_data/"
                "LIFE_proxima_A3_10h.dat"
            ),
            "configuration": REPO / f"{_A3_R03}/resolved/A3_10h_full.json",
            "runtime_operator": REPO / f"{_A3_R03}/runtime/operators/A3_10h_full.json",
        },
    },
    (100, "A3"): {
        "campaign": _A3_100H,
        "run_id": "A3_100h_full_BIN1_20261018_MPI14_resume01",
        "validation_status": "previously_validated_corrected_bin_baseline",
        "dataset_sha256_expected": (
            "78662546181a5b74391a14b7b73ae80d"
            "879200a74db6a4bc5338e3ce7eee4705"
        ),
        "paths": {
            "dataset": REPO / (
                "Thermal_Emission_Spectroscopy/outputs/"
                "life_proxima_b_earthlike_v1/life_data/"
                "LIFE_proxima_A3_100h.dat"
            ),
            "configuration": REPO / f"{_A3_100H}/resolved_configuration.json",
            "operator_record": REPO / f"{_A3_100H}/operator_preflight_mpi14_retry01.json",
        },
    },
}
A1_1H_NOISE_REPEAT_STEMS = {
    "previous": "proxima_A1_1h_O2_fixedBlack1bar_noxtol_MPI6_OFFICIAL1h",
    "official": "proxima_A1_1h_O2_fixedBlack1bar_noxtol_MPI6_NOISE2",
}
AUDIT_POSTERIOR_COLORS = {
    "A1": PALETTE["scenario_cyan"],
    "A3": PALETTE["scenario_pink"],
}
OFFICIAL_POSTERIOR_COLORS = {
    "A1": PALETTE["scenario_green"],
    "A3": PALETTE["scenario_pink"],
}
OFFICIAL_ANNOTATION_COLORS = {
    "A1": PALETTE["deep_moss"],
    "A3": PALETTE["dark_amaranth"],
}
mpl.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": [
            "STIXGeneral",
            "DejaVu Serif",
            "Times New Roman",
            "CMU Serif",
            "Liberation Serif",
        ],
        "mathtext.fontset": "stix",
        "axes.unicode_minus": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": False,
        "axes.linewidth": 0.8,
        "figure.titlesize": 16,
        "figure.titleweight": "normal",
        "figure.dpi": 140,
        "font.size": 10,
        "axes.titlesize": 13,
        "axes.titleweight": "normal",
    }
)


def retrieval_stem(scenario: str, hours: int, output_tag: str = "") -> str:
    """Return the shared stem used by the LIFE retrieval exports."""
    run_name = f"proxima_{scenario}_{hours}h{output_tag}"
    return f"{run_name}_proxima_{scenario}_{hours}h{output_tag}"


def require(path: Path) -> Path:
    """Raise an actionable error when a required evidence file is absent."""
    if not path.exists():
        raise FileNotFoundError(path)
    return path


def load_observation(scenario: str, hours: int) -> dict[str, np.ndarray]:
    """Load one binned LIFE observation in the campaign's direct-Fp units."""
    path = require(LIFE_DATA_DIR / f"LIFE_proxima_{scenario}_{hours}h.dat")
    data = np.loadtxt(path, skiprows=1)
    return {
        "wavelength": data[:, 0],
        "half_bin": data[:, 1],
        "flux": data[:, 2] / FLUX_SCALE,
        "sigma": data[:, 3] / FLUX_SCALE,
    }


def load_retrieved_spectrum(scenario: str, hours: int) -> dict[str, np.ndarray]:
    """Load retrieved spectrum quantiles and scale Fp for display."""
    path = require(SAMPLES_DIR / f"{retrieval_stem(scenario, hours)}_spectrum_retrieved.txt")
    data = np.loadtxt(path, skiprows=1)
    return {
        "wavelength": data[:, 0],
        "q02": data[:, 1] / FLUX_SCALE,
        "q16": data[:, 2] / FLUX_SCALE,
        "median": data[:, 3] / FLUX_SCALE,
        "q84": data[:, 4] / FLUX_SCALE,
        "q98": data[:, 5] / FLUX_SCALE,
    }


def load_truth_spectrum(scenario: str) -> dict[str, np.ndarray]:
    """Load the direct planetary flux from the forward-emission product."""
    path = require(FORWARD_DIR / f"{scenario}_emission.npz")
    with np.load(path) as data:
        return {
            "wavelength": np.asarray(data["wl_um"]),
            "flux": np.asarray(data["Fp_obs_W_m2_m"]) / FLUX_SCALE,
        }


def load_samples(scenario: str, hours: int, output_tag: str = "") -> np.ndarray:
    """Load posterior draws using the fixed POSEIDON export column order."""
    path = require(
        SAMPLES_DIR / f"{retrieval_stem(scenario, hours, output_tag)}_samples.txt"
    )
    data = np.loadtxt(path, skiprows=1)
    return np.atleast_2d(data)


def load_tagged_posterior(
    scenario: str,
    hours: int,
    output_tag: str,
    *,
    product_stem: str | None = None,
    required_species: tuple[str, ...] = AUDIT_MOLECULES,
    product_root: Path | None = None,
) -> dict[str, np.ndarray | list[str]]:
    """Load samples and their header for an explicitly tagged audit run."""
    stem = product_stem or f"proxima_{scenario}_{hours}h{output_tag}"
    samples_dir = product_root / "samples" if product_root else SAMPLES_DIR
    path = require(samples_dir / f"{stem}_samples.txt")
    lines = path.read_text(encoding="utf-8").splitlines()
    columns = [field.strip() for field in lines[0].split("|")]
    samples = np.atleast_2d(np.loadtxt(path, skiprows=1))
    if samples.shape[1] != len(columns):
        raise ValueError(
            f"Sample header/data mismatch for {scenario}: "
            f"{len(columns)} names, {samples.shape[1]} columns"
        )
    if not np.isfinite(samples).all():
        raise ValueError(f"Non-finite posterior samples in {path}")
    missing = set(required_species) - {
        name.removeprefix("log_") for name in columns
    }
    if missing:
        raise ValueError(
            f"Missing audit posterior species for {scenario}: {sorted(missing)}"
        )
    return {"columns": columns, "samples": samples}


def load_audit_pt(
    product_stem: str, product_root: Path | None = None
) -> np.ndarray:
    """Load and validate a tagged posterior P--T summary export."""
    samples_dir = product_root / "samples" if product_root else SAMPLES_DIR
    path = require(samples_dir / f"{product_stem}_PT_retrieved.txt")
    data = np.atleast_2d(np.loadtxt(path, skiprows=1))
    if data.shape != (100, 6) or not np.isfinite(data).all():
        raise ValueError(f"Unexpected or non-finite P--T summary in {path}: {data.shape}")
    if np.any(data[:, 0] <= 0) or np.any(np.diff(data[:, 0]) >= 0):
        raise ValueError(f"P--T pressure grid must be positive and descending: {path}")
    if np.any(data[:, 1] > data[:, 2]) or np.any(data[:, 2] > data[:, 3]):
        raise ValueError(f"Invalid lower P--T quantiles in {path}")
    if np.any(data[:, 3] > data[:, 4]) or np.any(data[:, 4] > data[:, 5]):
        raise ValueError(f"Invalid upper P--T quantiles in {path}")
    return data


def load_audit_fit_metrics(
    product_stem: str, product_root: Path | None = None
) -> dict[str, float]:
    """Read final ln Z and fit statistics from one POSEIDON result file."""
    results_dir = product_root / "results" if product_root else RESULTS_DIR
    path = require(results_dir / f"{product_stem}_results.txt")
    text = path.read_text(encoding="utf-8")
    patterns = {
        "ln_z": r"->\s*ln\s+Z\s*=\s*([-+\d.eE]+)\s*\+/-\s*([-+\d.eE]+)",
        "chi2_red": r"->\s*chi\^2_red\s*=\s*([-+\d.eE]+)",
        "dof": r"->\s*degrees\s+of\s+freedom\s*=\s*(\d+)",
    }
    evidence = re.search(patterns["ln_z"], text, flags=re.IGNORECASE)
    chi2_red = re.search(patterns["chi2_red"], text, flags=re.IGNORECASE)
    dof = re.search(patterns["dof"], text, flags=re.IGNORECASE)
    if evidence is None or chi2_red is None or dof is None:
        raise ValueError(f"Missing final fit metrics in {path}")
    metrics = {
        "ln_z": float(evidence.group(1)),
        "ln_z_error": float(evidence.group(2)),
        "chi2_red": float(chi2_red.group(1)),
        "dof": float(dof.group(1)),
    }
    if not np.isfinite(list(metrics.values())).all() or metrics["dof"] <= 0:
        raise ValueError(f"Invalid fit metrics in {path}: {metrics}")
    return metrics


def load_audit_log_profile(
    product_stem: str,
    required_species: tuple[str, ...],
    product_root: Path | None = None,
) -> dict[str, np.ndarray]:
    """Load pressure-dependent posterior log-abundance quantiles."""
    samples_dir = product_root / "samples" if product_root else SAMPLES_DIR
    path = require(samples_dir / f"{product_stem}_log_X_retrieved.txt")
    lines = path.read_text(encoding="utf-8").splitlines()
    header_pattern = re.compile(r"P \(bar\) \| log_([A-Za-z0-9_]+):")
    profiles: dict[str, np.ndarray] = {}
    index = 0
    while index < len(lines):
        match = header_pattern.match(lines[index].strip())
        if match is None:
            index += 1
            continue
        species = match.group(1)
        index += 1
        rows = []
        while index < len(lines):
            fields = lines[index].split()
            if len(fields) < 6:
                break
            try:
                rows.append([float(value) for value in fields[:6]])
            except ValueError:
                break
            index += 1
        if rows:
            profile = np.asarray(rows, dtype=float)
            if profile.ndim != 2 or profile.shape[1] != 6:
                raise ValueError(f"Unexpected log-X profile shape in {path}: {profile.shape}")
            if not np.isfinite(profile).all() or np.any(profile[:, 0] <= 0):
                raise ValueError(f"Non-finite or non-positive log-X profile in {path}")
            if np.any(np.diff(profile[:, 0]) >= 0):
                raise ValueError(f"Log-X pressure grid must descend in {path}")
            if np.any(np.diff(profile[:, 1:], axis=1) < 0):
                raise ValueError(f"Log-X quantiles are not ordered in {path}")
            profiles[species] = profile

    missing = sorted(set(required_species) - profiles.keys())
    if missing:
        raise ValueError(f"Missing retrieved log-X blocks in {path}: {missing}")
    return profiles


def load_truth_pt(scenario: str) -> tuple[np.ndarray, np.ndarray]:
    """Load the VULCAN input pressure and temperature profiles for a scenario."""
    stem = SCENARIOS[scenario]["profile_stem"]
    path = require(PROFILE_DIR / f"{stem}_PT.txt")
    table = np.genfromtxt(path, names=True)
    pressure = np.atleast_1d(np.asarray(table["P"], dtype=float))
    temperature = np.atleast_1d(np.asarray(table["T"], dtype=float))
    valid = np.isfinite(pressure) & np.isfinite(temperature) & (pressure > 0)
    if np.count_nonzero(valid) < 2:
        raise ValueError(f"Insufficient finite VULCAN P--T values in {path}")
    return pressure[valid], temperature[valid]


def load_truth_profile(scenario: str) -> np.ndarray:
    """Load a VULCAN-derived chemical profile with named columns."""
    stem = SCENARIOS[scenario]["profile_stem"]
    return np.genfromtxt(PROFILE_DIR / f"{stem}_chem.txt", names=True)


def load_retrieved_log_profile(scenario: str, hours: int) -> dict[str, np.ndarray]:
    """Parse the block-formatted retrieved vertical-abundance export."""
    path = require(SAMPLES_DIR / f"{retrieval_stem(scenario, hours)}_log_X_retrieved.txt")
    lines = path.read_text(encoding="utf-8").splitlines()
    blocks: dict[str, np.ndarray] = {}
    header_pattern = re.compile(r"P \(bar\) \| log_([A-Za-z0-9_]+):")
    index = 0
    while index < len(lines):
        match = header_pattern.match(lines[index].strip())
        if match is None:
            index += 1
            continue
        molecule = match.group(1)
        index += 1
        rows = []
        while index < len(lines):
            fields = lines[index].split()
            if len(fields) < 6:
                break
            try:
                rows.append([float(value) for value in fields[:6]])
            except ValueError:
                break
            index += 1
        if rows:
            blocks[molecule] = np.asarray(rows, dtype=float)
    missing = [molecule for molecule in MOLECULES if molecule not in blocks]
    if missing:
        raise ValueError(f"Missing retrieved log-X blocks in {path}: {missing}")
    return blocks


def load_campaign_products() -> dict[str, dict]:
    """Load and validate all products needed by the three canonical figures."""
    products = {"truth": {}, "observations": {}, "retrieved": {}, "samples": {}, "profiles": {}}
    for scenario in PLOT_SCENARIOS:
        products["truth"][scenario] = load_truth_spectrum(scenario)
        products["profiles"][scenario] = load_truth_profile(scenario)
        for hours in HOURS:
            key = (scenario, hours)
            products["observations"][key] = load_observation(scenario, hours)
            products["retrieved"][key] = load_retrieved_spectrum(scenario, hours)
            products["samples"][key] = load_samples(scenario, hours)
    return products


def finite_values(arrays) -> np.ndarray:
    """Concatenate finite values from an iterable of arrays."""
    values = np.concatenate([np.ravel(np.asarray(array)) for array in arrays])
    return values[np.isfinite(values)]


def padded_limits(arrays, fraction: float = 0.08, minimum_pad: float = 0.2) -> tuple[float, float]:
    """Return finite limits with a small readable margin."""
    values = finite_values(arrays)
    if values.size == 0:
        return -1.0, 1.0
    lower = float(np.min(values))
    upper = float(np.max(values))
    span = max(upper - lower, minimum_pad)
    padding = max(minimum_pad, fraction * span)
    return lower - padding, upper + padding


def spectrum_band_mask(wavelength: np.ndarray) -> np.ndarray:
    """Select the common wavelength interval used by retrieved spectra."""
    return (wavelength >= WAVELENGTH_RANGE[0]) & (wavelength <= WAVELENGTH_RANGE[1])


def resample_retrieved_spectrum(
    spectrum: dict[str, np.ndarray], target_wavelength: np.ndarray
) -> dict[str, np.ndarray]:
    """Interpolate retrieved quantiles onto a clean display grid."""
    resampled = {
        key: np.interp(target_wavelength, spectrum["wavelength"], spectrum[key])
        for key in ("q02", "q16", "median", "q84", "q98")
    }
    resampled["wavelength"] = target_wavelength
    return resampled


def resample_truth_spectrum(
    spectrum: dict[str, np.ndarray], target_wavelength: np.ndarray
) -> dict[str, np.ndarray]:
    """Interpolate a VULCAN forward spectrum onto a clean display grid."""
    return {
        "wavelength": target_wavelength,
        "flux": np.interp(target_wavelength, spectrum["wavelength"], spectrum["flux"]),
    }


def flux_ylabel() -> str:
    return r"Planetary flux $F_p$ [$10^{-13}$ W m$^{-2}$ m$^{-1}$]"


def comparison_legend_handles() -> list[Line2D]:
    """Return the transmission-style Retrieved/True/Observed legend."""
    ret_a0 = Line2D([], [], color=RETRIEVED_COLORS["A0"], lw=2.5, label="Retrieved A0")
    ret_a3 = Line2D([], [], color=RETRIEVED_COLORS["A3"], lw=2.5, label="Retrieved A3")
    true_a0 = Line2D(
        [], [], color=TRUE_COLORS["A0"], lw=1.2, alpha=0.70, label="True A0"
    )
    true_a3 = Line2D(
        [], [], color=TRUE_COLORS["A3"], lw=1.2, alpha=0.70, label="True A3"
    )
    observed_a0 = Line2D(
        [], [], color="none", marker=SCENARIO_MARKERS["A0"], markersize=6.0,
        markerfacecolor=OBSERVATION_COLORS["A0"],
        markeredgecolor=OBSERVATION_MARKER_EDGE, markeredgewidth=0.90,
        alpha=1.0, label="Observed A0",
    )
    observed_a3 = Line2D(
        [], [], color="none", marker=SCENARIO_MARKERS["A3"], markersize=6.0,
        markerfacecolor=OBSERVATION_COLORS["A3"],
        markeredgecolor=OBSERVATION_MARKER_EDGE, markeredgewidth=0.90,
        alpha=1.0, label="Observed A3",
    )
    # Matplotlib fills legend columns in the same order as the transmission
    # reference: Retrieved, True, Observed.
    return [ret_a0, ret_a3, true_a0, true_a3, observed_a0, observed_a3]


def add_comparison_legend(fig: plt.Figure, title: str) -> None:
    """Place a single framed Retrieved/True/Observed legend above the axes."""
    fig.suptitle(title, fontsize=14, fontweight="bold", y=0.98)
    fig.legend(
        handles=comparison_legend_handles(),
        loc="upper center",
        ncol=3,
        bbox_to_anchor=(0.5, 0.93),
        frameon=True,
        facecolor="white",
        edgecolor="none",
        framealpha=0.8,
        fontsize=9,
        handlelength=2.0,
        columnspacing=1.7,
        labelspacing=0.35,
    )


def plot_observation_markers(
    ax: plt.Axes,
    observed: dict[str, np.ndarray],
    observed_mask: np.ndarray,
    scenario: str,
    markersize: float,
    markeredgewidth: float,
) -> None:
    """Overlay opaque observation markers on the translucent error bars."""
    ax.plot(
        observed["wavelength"][observed_mask],
        observed["flux"][observed_mask],
        linestyle="none",
        marker=SCENARIO_MARKERS[scenario],
        markersize=markersize,
        color=OBSERVATION_COLORS[scenario],
        markerfacecolor=OBSERVATION_COLORS[scenario],
        markeredgecolor=OBSERVATION_MARKER_EDGE,
        markeredgewidth=markeredgewidth,
        alpha=1.0,
        zorder=45,
    )


def plot_global_spectra(products: dict[str, dict]) -> plt.Figure:
    """Plot the full retrieved LIFE spectra at 10 h and 240 h."""
    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    for row, hours in enumerate(HOURS):
        ax = axes[row]
        arrays = []
        target_wavelength = np.linspace(
            WAVELENGTH_RANGE[0], WAVELENGTH_RANGE[1], GLOBAL_DISPLAY_POINTS
        )

        # Retrieved models use the vivid scenario colours and the true VULCAN
        # spectra use the darker companion colours, as in the transmission
        # reference figures.
        for scenario in PLOT_SCENARIOS:
            retrieved = resample_retrieved_spectrum(
                products["retrieved"][(scenario, hours)], target_wavelength
            )
            retrieved_color = RETRIEVED_COLORS[scenario]

            ax.fill_between(
                retrieved["wavelength"],
                retrieved["q02"],
                retrieved["q98"],
                color=retrieved_color,
                alpha=RETRIEVED_2SIGMA_ALPHA,
                linewidth=0,
                zorder=11,
            )
            ax.fill_between(
                retrieved["wavelength"],
                retrieved["q16"],
                retrieved["q84"],
                color=retrieved_color,
                alpha=RETRIEVED_1SIGMA_ALPHA,
                linewidth=0,
                zorder=12,
            )
            ax.plot(
                retrieved["wavelength"],
                retrieved["median"],
                color=retrieved_color,
                linewidth=2.0,
                alpha=RETRIEVED_MEDIAN_ALPHA,
                zorder=20,
            )

            truth = resample_truth_spectrum(products["truth"][scenario], target_wavelength)
            observed = products["observations"][(scenario, hours)]
            observed_mask = spectrum_band_mask(observed["wavelength"])
            ax.errorbar(
                observed["wavelength"][observed_mask],
                observed["flux"][observed_mask],
                yerr=observed["sigma"][observed_mask],
                xerr=observed["half_bin"][observed_mask],
                fmt="none",
                ecolor=OBSERVATION_COLORS[scenario],
                alpha=0.35,
                elinewidth=0.4,
                capsize=0,
                zorder=39,
            )
            plot_observation_markers(
                ax,
                observed,
                observed_mask,
                scenario,
                OBSERVATION_MARKERSIZE_GLOBAL,
                OBSERVATION_MARKER_EDGE_WIDTH_GLOBAL,
            )
            ax.plot(
                truth["wavelength"],
                truth["flux"],
                color=TRUE_COLORS[scenario],
                linewidth=1.0,
                alpha=TRUE_SPECTRUM_ALPHA,
                zorder=30,
            )

            arrays.extend(
                [
                    retrieved["q02"],
                    retrieved["q98"],
                    truth["flux"],
                    observed["flux"][observed_mask] - observed["sigma"][observed_mask],
                    observed["flux"][observed_mask] + observed["sigma"][observed_mask],
                ]
            )

        ax.set_xlim(*WAVELENGTH_RANGE)
        ax.set_ylim(*padded_limits(arrays, fraction=0.06, minimum_pad=0.25))
        ax.grid(False)
        ax.set_ylabel(flux_ylabel(), fontsize=11.5)
        ax.tick_params(direction="in", top=True, right=True, labelsize=10)
        ax.minorticks_on()
        ax.text(
            1.02,
            0.50,
            f"{hours} h",
            transform=ax.transAxes,
            fontsize=11.5,
            fontweight="bold",
            va="center",
            ha="left",
            rotation=-90,
        )

    axes[-1].set_xlabel(r"Wavelength [$\mu$m]", fontsize=12)
    fig.tight_layout(rect=[0, 0, 0.985, 0.89])
    add_comparison_legend(fig, "Proxima b LIFE Retrieval Performance")
    return fig


def plot_molecular_zooms(products: dict[str, dict]) -> plt.Figure:
    """Plot the three selected molecular windows for both integration times."""
    fig, axes = plt.subplots(2, 3, figsize=(13, 8), sharex="col")
    for row, hours in enumerate(HOURS):
        for col, (left, right, title) in enumerate(ZOOM_WINDOWS):
            ax = axes[row, col]
            arrays = []
            target_wavelength = np.linspace(left, right, ZOOM_DISPLAY_POINTS)
            for scenario in PLOT_SCENARIOS:
                retrieved = resample_retrieved_spectrum(
                    products["retrieved"][(scenario, hours)], target_wavelength
                )
                observed = products["observations"][(scenario, hours)]
                retrieved_color = RETRIEVED_COLORS[scenario]
                observed_mask = (observed["wavelength"] >= left) & (observed["wavelength"] <= right)

                ax.fill_between(
                    retrieved["wavelength"],
                    retrieved["q02"],
                    retrieved["q98"],
                    color=retrieved_color,
                    alpha=RETRIEVED_2SIGMA_ALPHA,
                    linewidth=0,
                    zorder=11,
                )
                ax.fill_between(
                    retrieved["wavelength"],
                    retrieved["q16"],
                    retrieved["q84"],
                    color=retrieved_color,
                    alpha=RETRIEVED_1SIGMA_ALPHA,
                    linewidth=0,
                    zorder=12,
                )
                ax.plot(
                    retrieved["wavelength"],
                    retrieved["median"],
                    color=retrieved_color,
                    linewidth=2.0,
                    alpha=RETRIEVED_MEDIAN_ALPHA,
                    zorder=20,
                )
                ax.errorbar(
                    observed["wavelength"][observed_mask],
                    observed["flux"][observed_mask],
                    yerr=observed["sigma"][observed_mask],
                    xerr=observed["half_bin"][observed_mask],
                    fmt="none",
                    ecolor=OBSERVATION_COLORS[scenario],
                    alpha=0.70,
                    elinewidth=0.6,
                    capsize=1.0,
                    zorder=39,
                )
                plot_observation_markers(
                    ax,
                    observed,
                    observed_mask,
                    scenario,
                    OBSERVATION_MARKERSIZE_ZOOM,
                    OBSERVATION_MARKER_EDGE_WIDTH_ZOOM,
                )

                truth = resample_truth_spectrum(
                    products["truth"][scenario], target_wavelength
                )
                ax.plot(
                    truth["wavelength"],
                    truth["flux"],
                    color=TRUE_COLORS[scenario],
                    linewidth=1.0,
                    alpha=TRUE_SPECTRUM_ALPHA,
                    zorder=30,
                )
                arrays.extend(
                    [
                        retrieved["q02"],
                        retrieved["q98"],
                        truth["flux"],
                        observed["flux"][observed_mask] - observed["sigma"][observed_mask],
                        observed["flux"][observed_mask] + observed["sigma"][observed_mask],
                    ]
                )

            ax.set_xlim(left, right)
            ax.set_ylim(*padded_limits(arrays, fraction=0.08, minimum_pad=0.12))
            ax.grid(alpha=0.12, which="both", linestyle="--")
            ax.tick_params(direction="in", top=True, right=True, labelsize=9.5)
            ax.minorticks_on()
            if row == 0:
                ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
            if col == 0:
                ax.set_ylabel(flux_ylabel(), fontsize=10.5)
            if col == len(ZOOM_WINDOWS) - 1:
                ax.text(
                    1.05,
                    0.50,
                    f"{hours} h",
                    transform=ax.transAxes,
                    fontsize=11.5,
                    fontweight="bold",
                    va="center",
                    ha="left",
                    rotation=-90,
                )
            if row == len(HOURS) - 1:
                ax.set_xlabel(r"Wavelength [$\mu$m]", fontsize=10.5)

    fig.tight_layout(rect=[0, 0, 0.985, 0.89])
    add_comparison_legend(
        fig, "Proxima b LIFE retrievals in selected molecular bands"
    )
    return fig


def profile_x_limits(
    products: dict[str, dict],
    posterior_samples: dict[int, np.ndarray] | None = None,
) -> dict[str, tuple[float, float]]:
    """Set limits for the A3 posterior, profile, and effective A0 marker."""
    if posterior_samples is None:
        posterior_samples = {
            hours: products["samples"][(PROFILE_POSTERIOR_SCENARIO, hours)]
            for hours in HOURS
        }
    limits = {}
    for molecule in MOLECULES:
        posterior = []
        reference = []
        reference.append(
            np.log10(
                np.clip(
                    products["profiles"][PROFILE_POSTERIOR_SCENARIO][molecule],
                    PROFILE_FLOOR,
                    None,
                )
            )
        )
        reference.append(
            np.asarray(
                [
                    log10_column_averaged_mixing_ratio(
                        products["profiles"][PROFILE_REFERENCE_SCENARIO], molecule
                    )
                ]
            )
        )
        for samples in posterior_samples.values():
            posterior.append(samples[:, SAMPLE_INDEX[molecule]])
        post = finite_values(posterior)
        ref = finite_values(reference)
        lower = min(float(np.percentile(post, 0.5)), float(np.percentile(ref, 1.0))) - 0.25
        upper = max(float(np.percentile(post, 99.5)), float(np.percentile(ref, 99.0))) + 0.25
        # The retrieval priors bottom out close to -12 dex.  A hard display
        # floor keeps ultra-trace VULCAN values from flattening all histograms.
        lower = max(-13.0, lower)
        upper = min(0.0, upper)
        if upper - lower < 1.0:
            upper = lower + 1.0
        limits[molecule] = (lower, upper)
    return limits


def posterior_summary(values: np.ndarray) -> dict[str, float]:
    """Summarize one marginal posterior using the transmission-plot metrics."""
    q16, q50, q84 = np.percentile(values, [16.0, 50.0, 84.0])
    return {
        "median": float(q50),
        "q16": float(q16),
        "q84": float(q84),
        "err_low": float(q50 - q16),
        "err_high": float(q84 - q50),
        "sigma68": float(0.5 * (q84 - q16)),
    }


def signed_reference_distance(summary: dict[str, float], reference: float) -> float:
    """Return signed posterior-to-A0 distance in units of its 68% width."""
    sigma = summary["sigma68"]
    if sigma == 0.0:
        return float("nan")
    return (summary["median"] - reference) / sigma


def add_profile_metrics(
    ax: plt.Axes,
    x_limits: tuple[float, float],
    summary: dict[str, float],
    a0_reference: float,
) -> None:
    """Add A3 posterior and signed distance to the effective A0 reference."""
    distance = signed_reference_distance(summary, a0_reference)
    metrics_lines = [
        TextArea(
            rf"A3 = {summary['median']:.2f} $\pm$ {summary['sigma68']:.2f} dex",
            textprops={"color": RETRIEVED_COLORS[PROFILE_POSTERIOR_SCENARIO], "fontsize": 7.5},
        ),
        TextArea(
            rf"A0 ref. = {a0_reference:.2f} dex",
            textprops={"color": TRUE_COLORS[PROFILE_REFERENCE_SCENARIO], "fontsize": 7.2},
        ),
        TextArea(
            rf"$z_{{A3|A0}}$ = {distance:+.2f}$\sigma$",
            textprops={"color": PALETTE["dark_amaranth"], "fontsize": 7.2},
        ),
    ]
    posterior_center = summary["median"]
    x_mid = 0.5 * (x_limits[0] + x_limits[1])
    metrics_loc = "upper right" if posterior_center < x_mid else "upper left"
    metrics_anchor = (0.97, 0.965) if metrics_loc == "upper right" else (0.035, 0.965)
    metrics_pack = VPacker(children=metrics_lines, align="left", pad=0.0, sep=1.2)
    metrics_box = AnchoredOffsetbox(
        loc=metrics_loc,
        child=metrics_pack,
        pad=0.16,
        borderpad=0.30,
        frameon=True,
        bbox_to_anchor=metrics_anchor,
        bbox_transform=ax.transAxes,
    )
    metrics_box.patch.set_boxstyle("round,pad=0.20")
    metrics_box.patch.set_facecolor("white")
    metrics_box.patch.set_edgecolor("0.86")
    metrics_box.patch.set_linewidth(0.6)
    metrics_box.patch.set_alpha(0.90)
    metrics_box.set_zorder(20)
    ax.add_artist(metrics_box)


def plot_profiles_posteriors(
    products: dict[str, dict],
    posterior_hours: tuple[int, ...] = HOURS,
    posterior_samples: dict[int, np.ndarray] | None = None,
    title: str = "Proxima b: A3 Retrieval Relative to the A0 Reference",
) -> plt.Figure:
    """Plot marginal abundance posteriors and vertical reference profiles."""
    if posterior_samples is None:
        posterior_samples = {
            hours: products["samples"][(PROFILE_POSTERIOR_SCENARIO, hours)]
            for hours in posterior_hours
        }
    limits = profile_x_limits(products, posterior_samples)
    n_rows = len(posterior_hours)
    n_cols = len(MOLECULES)
    # Keep the compact transmission-like grid, reserving a clean header for the
    # title, horizontal line-semantics legend, and distance formula.
    fig = plt.figure(figsize=(2.78 * n_cols, 2.35 * n_rows))
    outer = fig.add_gridspec(
        n_rows,
        n_cols,
        left=0.068,
        right=0.985,
        bottom=0.055,
        top=0.83,
        wspace=0.11,
        hspace=0.20,
    )

    a3_profile_color = TRUE_COLORS[PROFILE_POSTERIOR_SCENARIO]
    a3_posterior_color = RETRIEVED_COLORS[PROFILE_POSTERIOR_SCENARIO]
    a0_effective_color = TRUE_COLORS[PROFILE_REFERENCE_SCENARIO]
    legend_handles = [
        Line2D([], [], color=a3_profile_color, lw=2.1, label="A3 VULCAN profile"),
        Line2D([], [], color=a3_posterior_color, lw=1.7, ls="--", label="A3 posterior median"),
        Line2D(
            [], [], color=a0_effective_color, lw=1.3, ls=":",
            label="A0 effective reference",
        ),
    ]
    for row, hours in enumerate(posterior_hours):
        for col, molecule in enumerate(MOLECULES):
            ax = fig.add_subplot(outer[row, col])
            ax_profile = ax.twinx()
            ax.set_zorder(2)
            ax_profile.set_zorder(1)
            ax.patch.set_alpha(0.0)

            left, right = limits[molecule]
            bin_edges = np.linspace(left, right, 28)
            values = posterior_samples[hours][:, SAMPLE_INDEX[molecule]]
            summary = posterior_summary(values)
            ax.hist(
                values,
                bins=bin_edges,
                density=True,
                histtype="stepfilled",
                color=a3_posterior_color,
                edgecolor=a3_posterior_color,
                linewidth=0.9,
                alpha=0.28,
                zorder=1,
            )
            ax.axvline(
                summary["median"],
                color=a3_posterior_color,
                lw=1.7,
                ls="--",
                alpha=0.95,
                zorder=4,
            )
            a0_reference = log10_column_averaged_mixing_ratio(
                products["profiles"][PROFILE_REFERENCE_SCENARIO], molecule
            )
            ax.axvline(
                a0_reference,
                color=a0_effective_color,
                lw=1.3,
                ls=":",
                alpha=0.90,
                zorder=5,
            )

            reference = products["profiles"][PROFILE_POSTERIOR_SCENARIO]
            ax_profile.plot(
                np.log10(np.clip(reference[molecule], PROFILE_FLOOR, None)),
                reference["PRESS"],
                color=a3_profile_color,
                lw=2.1,
                alpha=0.98,
                zorder=6,
            )

            ax.set_xlim(left, right)
            ax.set_ylim(bottom=0.0)
            ax.grid(axis="y", alpha=0.22, linestyle=":")
            ax.tick_params(direction="in", top=True, right=True, labelsize=8.3)
            ax.minorticks_on()

            ax_profile.set_yscale("log")
            ax_profile.set_ylim(1.0, 5.0e-8)
            ax_profile.tick_params(axis="y", direction="in", labelsize=8.0)
            ax_profile.spines["top"].set_visible(False)
            ax_profile.spines["left"].set_visible(False)
            ax_profile.spines["bottom"].set_visible(False)
            ax_profile.spines["right"].set_visible(col == n_cols - 1)
            if col != n_cols - 1:
                ax_profile.set_yticks([])
                ax_profile.set_yticks([], minor=True)
                ax_profile.tick_params(axis="y", right=False, labelright=False)

            post_ymax = ax.get_ylim()[1]
            ax.errorbar(
                summary["median"],
                0.11 * post_ymax,
                xerr=summary["sigma68"],
                fmt="s",
                ms=3.5,
                color=a3_posterior_color,
                markerfacecolor=a3_posterior_color,
                markeredgecolor="black",
                markeredgewidth=0.3,
                elinewidth=1.1,
                capsize=2.3,
                zorder=7,
            )
            add_profile_metrics(ax, (left, right), summary, a0_reference)

            if row == 0:
                ax.set_title(MOLECULE_LABELS[molecule], fontsize=13, pad=6)
            if col == 0:
                ax.set_ylabel("Probability density")
                ax.text(
                    -0.60,
                    0.50,
                    f"{hours} h",
                    transform=ax.transAxes,
                    rotation=90,
                    va="center",
                    ha="center",
                    fontsize=10.5,
                    fontweight="bold",
                )
            else:
                ax.tick_params(axis="y", labelleft=False)
            if row == n_rows - 1:
                ax.set_xlabel(PROFILE_X_AXIS_LABELS[molecule])
            else:
                ax.tick_params(axis="x", labelbottom=False)
            if col == n_cols - 1:
                ax_profile.tick_params(axis="y", which="both", right=True, labelright=True)
                ax_profile.set_ylabel("Pressure [bar]")

    fig.legend(
        legend_handles,
        [handle.get_label() for handle in legend_handles],
        loc="upper center",
        ncol=3,
        frameon=False,
        handlelength=2.0,
        fontsize=9.5,
        labelspacing=0.35,
        columnspacing=1.8,
        handletextpad=0.55,
        bbox_to_anchor=(0.5, 0.962),
    )
    fig.suptitle(
        title,
        y=0.995,
        fontsize=16,
    )
    fig.text(
        0.90,
        0.950,
        r"$z_{A3|A0}=\dfrac{\mu_{A3}-\log_{10}(X_{A0,\mathrm{eff}})}{\sigma_{A3}}$",
        color=PALETTE["charcoal_violet"],
        ha="right",
        va="top",
        fontsize=9.2,
        bbox={
            "boxstyle": "round,pad=0.25",
            "facecolor": "white",
            "edgecolor": PALETTE["charcoal_violet"],
            "linewidth": 0.6,
            "alpha": 0.88,
        },
    )
    return fig


def load_a1_a3_time_comparison_products(
    run_stems: dict[int, dict[str, str]] = AUDIT_TIME_RUN_STEMS,
    molecules: tuple[str, ...] = AUDIT_MOLECULES,
    run_roots: dict[tuple[int, str], Path] | None = None,
) -> dict[tuple[int, str], dict]:
    """Load validated A1/A3 posterior, log-X, and P--T products by time."""
    products: dict[tuple[int, str], dict] = {}
    for hours, scenario_stems in run_stems.items():
        for scenario, stem in scenario_stems.items():
            product_root = (run_roots or {}).get((hours, scenario))
            posterior = load_tagged_posterior(
                scenario,
                hours,
                output_tag="",
                product_stem=stem,
                required_species=molecules,
                product_root=product_root,
            )
            columns = posterior["columns"]
            assert isinstance(columns, list)
            column_indices = {
                name.removeprefix("log_"): index
                for index, name in enumerate(columns)
            }
            products[(hours, scenario)] = {
                "stem": stem,
                "samples": posterior["samples"],
                "column_indices": column_indices,
                "log_x": load_audit_log_profile(stem, molecules, product_root),
                "pt": load_audit_pt(stem, product_root),
                "fit": load_audit_fit_metrics(stem, product_root),
                "product_root": product_root or SAMPLES_DIR.parent,
            }
    return products


def add_a1_a3_metrics(
    ax: plt.Axes,
    summaries: dict[str, dict[str, float]],
    a0_reference: float,
) -> None:
    """Annotate posterior intervals and signed distances from effective A0."""
    metrics_lines = [
        TextArea(
            rf"A0 effective = {a0_reference:.2f} dex",
            textprops={"color": PALETTE["deep_moss"], "fontsize": 7.0},
        )
    ]
    for scenario in ("A1", "A3"):
        summary = summaries[scenario]
        distance = signed_reference_distance(summary, a0_reference)
        metrics_lines.extend(
            [
                TextArea(
                    rf"{scenario} = {summary['median']:.2f} "
                    rf"(+{summary['err_high']:.2f}/"
                    rf"-{summary['err_low']:.2f}) dex",
                    textprops={
                        "color": AUDIT_POSTERIOR_COLORS[scenario],
                        "fontsize": 7.0,
                    },
                ),
                TextArea(
                    rf"$z_{{{scenario}|A0}}$ = {distance:+.2f}$\sigma$",
                    textprops={
                        "color": AUDIT_POSTERIOR_COLORS[scenario],
                        "fontsize": 6.9,
                    },
                ),
            ]
        )

    box = VPacker(children=metrics_lines, align="left", pad=0.0, sep=0.9)
    center = np.mean([summaries[s]["median"] for s in ("A1", "A3")])
    loc = "upper left" if center > np.mean(ax.get_xlim()) else "upper right"
    anchor = (0.025, 0.975) if loc == "upper left" else (0.975, 0.975)
    annotation = AnchoredOffsetbox(
        loc=loc,
        child=box,
        pad=0.15,
        borderpad=0.25,
        frameon=True,
        bbox_to_anchor=anchor,
        bbox_transform=ax.transAxes,
    )
    annotation.patch.set_boxstyle("round,pad=0.18")
    annotation.patch.set_facecolor("white")
    annotation.patch.set_edgecolor("0.82")
    annotation.patch.set_linewidth(0.55)
    annotation.patch.set_alpha(0.92)
    annotation.set_zorder(20)
    ax.add_artist(annotation)


def add_a1_a3_fit_metrics(
    ax: plt.Axes,
    products: dict[tuple[int, str], dict],
    hours: int,
) -> None:
    """Show per-dataset ln Z and reduced chi-square inside each P--T panel."""
    lines = []
    for scenario in ("A1", "A3"):
        fit = products[(hours, scenario)]["fit"]
        lines.append(
            TextArea(
                rf"{scenario}: $\chi^2_{{red}}$={fit['chi2_red']:.2f} "
                rf"({fit['dof']:.0f} dof); "
                rf"$\ln Z$={fit['ln_z']:.2f}$\pm${fit['ln_z_error']:.2f}",
                textprops={
                    "color": AUDIT_POSTERIOR_COLORS[scenario],
                    "fontsize": 6.8,
                },
            )
        )
    packed = VPacker(children=lines, align="left", pad=0.0, sep=1.1)
    annotation = AnchoredOffsetbox(
        loc="upper left",
        child=packed,
        pad=0.12,
        borderpad=0.25,
        frameon=True,
        bbox_to_anchor=(0.025, 0.975),
        bbox_transform=ax.transAxes,
    )
    annotation.patch.set_boxstyle("round,pad=0.18")
    annotation.patch.set_facecolor("white")
    annotation.patch.set_edgecolor("0.84")
    annotation.patch.set_linewidth(0.55)
    annotation.patch.set_alpha(0.91)
    annotation.set_zorder(20)
    ax.add_artist(annotation)


def add_official_molecular_metrics(
    ax: plt.Axes,
    summaries: dict[str, dict[str, float]],
    a0_reference: float,
    *,
    is_bottom_row: bool,
) -> None:
    """Place q50 and descriptive z labels below each molecular panel."""
    axis_box = ax.get_position()
    x_center = axis_box.x0 + axis_box.width / 2.0
    figure = ax.figure
    y_offsets = (0.049, 0.070) if is_bottom_row else (0.023, 0.045)
    for scenario, y_offset in zip(("A1", "A3"), y_offsets):
        summary = summaries[scenario]
        distance = signed_reference_distance(summary, a0_reference)
        figure.text(
            x_center,
            axis_box.y0 - y_offset,
            rf"$q_{{50}}={summary['median']:.2f};\ z={distance:+.2f}$",
            color=OFFICIAL_ANNOTATION_COLORS[scenario],
            fontsize=6.0,
            ha="center",
            va="center",
        )


def plot_a1_a3_time_comparison(
    *,
    run_stems: dict[int, dict[str, str]] = AUDIT_TIME_RUN_STEMS,
    official: bool = False,
    dynamic_xlimits: bool = False,
    posterior_only_xlimits: bool = False,
    molecules: tuple[str, ...] = AUDIT_MOLECULES,
    run_roots: dict[tuple[int, str], Path] | None = None,
    include_pt_column: bool = True,
) -> plt.Figure:
    """Plot A1/A3 abundance posteriors and optionally a P--T column."""
    scenarios = ("A1", "A3")
    scenario_colors = (
        OFFICIAL_POSTERIOR_COLORS if official else AUDIT_POSTERIOR_COLORS
    )
    times = tuple(run_stems)
    products = load_a1_a3_time_comparison_products(
        run_stems,
        molecules,
        run_roots if run_roots is not None else (
            OFFICIAL_RUN_ROOTS if official else None
        ),
    )
    abundance_profiles = {s: load_truth_profile(s) for s in ("A0", *scenarios)}
    input_pt = {scenario: load_truth_pt(scenario) for scenario in scenarios}
    a0_effective = {
        molecule: log10_column_averaged_mixing_ratio(
            abundance_profiles["A0"], molecule
        )
        for molecule in molecules
    }

    abundance_limits = {
        molecule: (
            LOG_O2_PRIOR_LIMITS if molecule == "O2" else LOG_VMR_PRIOR_LIMITS
        )
        for molecule in molecules
    }
    x_limits = dict(abundance_limits)
    if (dynamic_xlimits or posterior_only_xlimits) and not official:
        raise ValueError("Dynamic x limits are available for the official figure only")
    if dynamic_xlimits and posterior_only_xlimits:
        raise ValueError("Choose either profile-aware or posterior-only x limits")
    if dynamic_xlimits or posterior_only_xlimits:
        for molecule in molecules:
            plotted_values = []
            if dynamic_xlimits:
                for scenario in scenarios:
                    truth = abundance_profiles[scenario]
                    truth_log_x = np.log10(
                        np.clip(
                            np.asarray(truth[molecule], dtype=float),
                            PROFILE_FLOOR,
                            None,
                        )
                    )
                    plotted_values.append(
                        truth_log_x[np.isfinite(truth_log_x)]
                    )
            for hours in times:
                for scenario in scenarios:
                    product = products[(hours, scenario)]
                    samples = product["samples"]
                    values = samples[:, product["column_indices"][molecule]]
                    values = values[np.isfinite(values)]
                    if values.size == 0:
                        raise ValueError(
                            f"No finite {molecule} samples for {scenario} {hours} h"
                        )
                    plotted_values.append(values)
            combined = np.concatenate(plotted_values)
            base_lower, base_upper = abundance_limits[molecule]
            data_lower = float(np.min(combined))
            data_upper = float(np.max(combined))
            padding = max(0.18, 0.035 * (data_upper - data_lower))
            x_limits[molecule] = (
                max(base_lower, data_lower - padding),
                min(base_upper, data_upper + padding),
            )
            if x_limits[molecule][0] >= x_limits[molecule][1]:
                raise ValueError(
                    f"Invalid dynamic x limits for {molecule}: "
                    f"{x_limits[molecule]}"
                )

    all_pt = [products[(hours, scenario)]["pt"] for hours in times for scenario in scenarios]
    all_log_x = [
        products[(hours, scenario)]["log_x"][molecule]
        for hours in times
        for scenario in scenarios
        for molecule in molecules
    ]
    pt_pressures = np.concatenate(
        [pt[:, 0] for pt in all_pt]
        + [profile[:, 0] for profile in all_log_x]
        + [np.asarray(abundance_profiles[s]["PRESS"], dtype=float) for s in ("A0", *scenarios)]
    )
    pressure_max = float(np.max(pt_pressures))
    pressure_min = float(np.min(pt_pressures))
    all_temperatures = [pt[:, 1:] for pt in all_pt]
    all_temperatures.extend(
        temperature[:, None] for _, temperature in input_pt.values()
    )
    t_low, t_high = np.percentile(finite_values(all_temperatures), [0.5, 99.5])
    t_padding = max(5.0, 0.05 * float(t_high - t_low))
    temperature_limits = (float(t_low - t_padding), float(t_high + t_padding))

    molecular_columns = len(molecules)
    n_columns = molecular_columns + int(include_pt_column)
    figure = plt.figure(
        figsize=(6.95, 5.65)
        if official
        else (2.78 * n_columns, 2.35 * len(times))
    )
    grid = figure.add_gridspec(
        len(times),
        n_columns,
        left=0.075 if official else 0.075,
        right=0.985 if official else 0.945,
        bottom=0.20 if official else 0.085,
        top=0.82 if official else 0.805,
        wspace=0.25 if official else 0.16,
        hspace=0.72 if official else 0.20,
        width_ratios=[1.0] * molecular_columns + ([1.08] if include_pt_column else []),
    )
    if official:
        legend_handles = [
            Patch(
                facecolor=scenario_colors["A1"],
                edgecolor=scenario_colors["A1"],
                alpha=0.25,
                label="A1 posterior",
            ),
            Line2D(
                [], [], color=scenario_colors["A1"], lw=1.7,
                label="A1 VULCAN abundance profile",
            ),
            Patch(
                facecolor=scenario_colors["A3"],
                edgecolor=scenario_colors["A3"],
                alpha=0.25,
                label="A3 posterior",
            ),
            Line2D(
                [], [], color=scenario_colors["A3"], lw=1.7,
                label="A3 VULCAN abundance profile",
            ),
            Line2D(
                [], [], color="0.28", lw=1.35, ls="--",
                label="Isochemical posterior median",
            ),
            Line2D(
                [], [], color=PALETTE["deep_moss"], lw=1.3, ls=":",
                label="A0 effective reference",
            ),
        ]
    else:
        legend_handles = [
            Line2D(
                [], [], color=scenario_colors["A1"], lw=2.0,
                label="A1 VULCAN profile",
            ),
            Line2D(
                [], [], color=scenario_colors["A1"], lw=1.7, ls="--",
                label="A1 posterior median",
            ),
            Line2D(
                [], [], color=scenario_colors["A3"], lw=2.0,
                label="A3 VULCAN profile",
            ),
            Line2D(
                [], [], color=scenario_colors["A3"], lw=1.7, ls="--",
                label="A3 posterior median",
            ),
            Line2D(
                [], [], color=PALETTE["deep_moss"], lw=1.3, ls=":",
                label="A0 effective reference",
            ),
            Line2D(
                [], [], color=PALETTE["charcoal_violet"], lw=1.5,
                label="P--T posterior median",
            ),
            Line2D(
                [], [], color=PALETTE["charcoal_violet"], lw=1.2, ls="--",
                label="P--T VULCAN input",
            ),
        ]

    shared_molecular_axes: list[plt.Axes | None] = [None] * molecular_columns
    shared_pt_axis: plt.Axes | None = None
    input_profile_colors = scenario_colors
    posterior_linestyles = {"A1": "--", "A3": "--"}
    posterior_markers = {"A1": "o", "A3": "D"}
    for row, hours in enumerate(times):
        for column, molecule in enumerate(molecules):
            axis = figure.add_subplot(
                grid[row, column],
                sharex=shared_molecular_axes[column] if row else None,
            )
            if row == 0:
                shared_molecular_axes[column] = axis
            profile_axis = axis.twinx()
            axis.set_zorder(2)
            if profile_axis is not None:
                profile_axis.set_zorder(1)
            axis.patch.set_alpha(0.0)
            prior_lower, prior_upper = abundance_limits[molecule]
            bins = np.linspace(prior_lower, prior_upper, 34)
            summaries = {}
            for scenario in scenarios:
                product = products[(hours, scenario)]
                samples = product["samples"]
                values = samples[:, product["column_indices"][molecule]]
                color = scenario_colors[scenario]
                summary = posterior_summary(values)
                summaries[scenario] = summary
                axis.hist(
                    values,
                    bins=bins,
                    density=True,
                    histtype="stepfilled",
                    color=color,
                    edgecolor=color,
                    linewidth=0.78,
                    alpha=0.27,
                    zorder=2 if scenario == "A1" else 3,
                )
                axis.axvline(
                    summary["median"],
                    color=color,
                    lw=1.45,
                    ls=posterior_linestyles[scenario],
                    alpha=0.95,
                    zorder=5,
                )
                profile = product["log_x"][molecule]
                profile_pressure = profile[:, 0]
                # The retrieved isochem median is pressure-constant. Confirm
                # that the saved profile summarizes the same posterior median.
                if not np.allclose(profile[:, 3], summary["median"], atol=0.20):
                    raise ValueError(
                        f"{scenario} {hours} h {molecule}: log-X median does "
                        "not match the isochemical posterior within 0.20 dex"
                    )
                truth = abundance_profiles[scenario]
                truth_pressure = np.asarray(truth["PRESS"], dtype=float)
                truth_log_x = np.log10(
                    np.clip(np.asarray(truth[molecule], dtype=float), PROFILE_FLOOR, None)
                )
                visible_profile = (
                    np.isfinite(truth_log_x)
                    & np.isfinite(truth_pressure)
                    & (truth_log_x >= x_limits[molecule][0])
                )
                if profile_axis is not None:
                    profile_axis.plot(
                        truth_log_x[visible_profile],
                        truth_pressure[visible_profile],
                        color=input_profile_colors[scenario],
                        lw=1.15 if official else 1.45,
                        alpha=0.96,
                        zorder=4,
                    )

            axis.axvline(
                a0_effective[molecule],
                color=PALETTE["deep_moss"],
                lw=1.25,
                ls=":",
                alpha=0.95,
                zorder=6,
            )
            if dynamic_xlimits or posterior_only_xlimits:
                for prior_edge in abundance_limits[molecule]:
                    axis.axvline(
                        prior_edge,
                        color="0.45",
                        lw=0.65,
                        ls=(0, (2, 2)),
                        alpha=0.75,
                        zorder=4,
                    )
            axis.set_xlim(*x_limits[molecule])
            if row == 0:
                if official:
                    axis.set_title(
                        f"{MOLECULE_LABELS[molecule]}\n"
                        rf"A0 = {a0_effective[molecule]:.2f}",
                        fontsize=7.0,
                        linespacing=1.08,
                        pad=2.0,
                    )
                else:
                    axis.set_title(
                        MOLECULE_LABELS[molecule], fontsize=11.5, pad=5
                    )
            axis.set_axisbelow(True)
            axis.grid(axis="y", alpha=0.22, linestyle=":")
            axis.tick_params(
                direction="in", top=not official, right=False,
                labelsize=6.0 if official else 8.1,
            )
            if official:
                axis.spines["right"].set_visible(False)
                axis.yaxis.set_ticks_position("left")
                axis.minorticks_off()
                axis.tick_params(
                    axis="y", which="both", right=False, labelright=False
                )
            axis.set_ylim(bottom=0.0)
            if profile_axis is not None:
                profile_axis.set_yscale("log")
                profile_axis.set_ylim(pressure_max * 1.03, pressure_min / 1.03)
                if official:
                    profile_axis.yaxis.set_visible(False)
                profile_axis.tick_params(
                    axis="y", direction="in", labelsize=7.8
                )
                profile_axis.spines["top"].set_visible(False)
                profile_axis.spines["left"].set_visible(False)
                profile_axis.spines["bottom"].set_visible(False)
                profile_axis.spines["right"].set_visible(
                    not official and column == molecular_columns - 1
                )
            if column == 0:
                axis.text(
                    -0.34 if official else -0.62, 0.50,
                    (
                        f"{hours} h"
                        if official or hours != 100
                        else "100 h*"
                    ),
                    transform=axis.transAxes,
                    rotation=90, va="center", ha="center",
                    fontsize=6.7 if official else 10.5,
                    fontweight="bold",
                )
            else:
                axis.tick_params(axis="y", labelleft=False)
            if official and column == 0:
                axis.yaxis.set_major_locator(plt.MaxNLocator(3))
            if profile_axis is not None and column != molecular_columns - 1:
                profile_axis.set_yticks([])
                profile_axis.set_yticks([], minor=True)
                profile_axis.tick_params(
                    axis="y", left=False, right=False,
                    labelleft=False, labelright=False,
                )
            elif profile_axis is not None:
                profile_axis.set_yticks([])
                profile_axis.set_yticks([], minor=True)
                profile_axis.tick_params(
                    axis="y", left=False, right=False,
                    labelleft=False, labelright=False,
                )
            if row < len(times) - 1:
                axis.tick_params(axis="x", labelbottom=False)
            if official:
                if dynamic_xlimits or posterior_only_xlimits:
                    axis.xaxis.set_major_locator(plt.MaxNLocator(5))
                    x_span = axis.get_xlim()[1] - axis.get_xlim()[0]
                    tick_format = "%.1f" if x_span < 6.0 else "%.0f"
                    axis.xaxis.set_major_formatter(
                        plt.FormatStrFormatter(tick_format)
                    )
                else:
                    axis.set_xticks([-12, -6, -1])
                    axis.set_xticklabels(("−12", "−6", "−1"))
                if row == len(times) - 1:
                    axis.tick_params(axis="x", labelbottom=True)
            elif molecule == "O2":
                axis.set_xticks(LOG_O2_PRIOR_TICKS)
                axis.set_xticklabels(("-6", "-4", "-2", "-0.30"))
            else:
                axis.set_xticks(LOG_VMR_PRIOR_TICKS)
                axis.set_xticklabels(("-12", "-9", "-6", "-3", "-1"))
            axis.set_ylim(top=axis.get_ylim()[1] * 1.05)
            density_top = axis.get_ylim()[1]
            for scenario in scenarios:
                summary = summaries[scenario]
                axis.errorbar(
                    summary["median"],
                    density_top * (0.075 if scenario == "A1" else 0.16),
                    xerr=np.array(
                        [[summary["err_low"]], [summary["err_high"]]]
                    ),
                    fmt=posterior_markers[scenario],
                    ms=2.4 if official else 3.2,
                    color=scenario_colors[scenario],
                    markerfacecolor=scenario_colors[scenario],
                    markeredgecolor="black",
                    markeredgewidth=0.35,
                    ecolor=scenario_colors[scenario],
                    elinewidth=0.85 if official else 1.15,
                    capsize=1.5 if official else 2.2,
                    zorder=8,
                )
            if official:
                add_official_molecular_metrics(
                    axis,
                    summaries,
                    a0_effective[molecule],
                    is_bottom_row=row == len(times) - 1,
                )
            else:
                add_a1_a3_metrics(axis, summaries, a0_effective[molecule])

        if include_pt_column:
            pt_axis = figure.add_subplot(
                grid[row, molecular_columns],
                sharex=shared_pt_axis if row else None,
            )
            if row == 0:
                shared_pt_axis = pt_axis
            for scenario in scenarios:
                product = products[(hours, scenario)]
                pt = product["pt"]
                pressure = pt[:, 0]
                color = scenario_colors[scenario]
                pt_axis.fill_betweenx(
                    pressure, pt[:, 1], pt[:, 5], color=color, alpha=0.075,
                    linewidth=0, zorder=1,
                )
                pt_axis.fill_betweenx(
                    pressure, pt[:, 2], pt[:, 4], color=color, alpha=0.20,
                    linewidth=0, zorder=2,
                )
                pt_axis.plot(pt[:, 3], pressure, color=color, lw=1.55, zorder=4)
                if not official or row == 0:
                    true_pressure, true_temperature = input_pt[scenario]
                    pt_axis.plot(
                        true_temperature,
                        true_pressure,
                        color="black" if official else color,
                        lw=0.95 if official else 1.1,
                        ls="--",
                        alpha=0.95,
                        zorder=5,
                    )

            if row == 0:
                pt_axis.set_title(
                    "P–T\nposterior bands"
                    if official
                    else "P--T profile",
                    fontsize=6.0 if official else 13,
                    linespacing=1.0,
                    pad=2.5 if official else 6,
                )
            pt_axis.set_yscale("log")
            pt_axis.set_ylim(pressure_max * 1.03, pressure_min / 1.03)
            pt_axis.set_xlim(*temperature_limits)
            pt_axis.set_axisbelow(True)
            pt_axis.grid(which="major", alpha=0.20, linestyle=":")
            pt_axis.tick_params(
                direction="in", top=not official, right=True,
                labelsize=6.0 if official else 8.2,
            )
            if row < len(times) - 1:
                pt_axis.tick_params(axis="x", labelbottom=False)
            else:
                pt_axis.set_xlabel(
                    "Temperature [K]", fontsize=6.0 if official else 10
                )
            if row == 0:
                pt_axis.yaxis.tick_right()
                pt_axis.yaxis.set_label_position("right")
                pt_axis.set_ylabel(
                    "Pressure [bar]", fontsize=6.2 if official else 10, labelpad=2
                )
            else:
                if official:
                    pt_axis.tick_params(
                        axis="y", labelleft=False, labelright=False,
                        left=False, right=False,
                    )
                else:
                    pt_axis.tick_params(axis="y", labelleft=False, left=False)
            pt_axis.xaxis.set_major_locator(plt.MaxNLocator(4))
            if not official:
                add_a1_a3_fit_metrics(pt_axis, products, hours)

        if official and row < len(times) - 1:
            next_row_left = grid[row + 1, 0].get_position(figure)
            next_row_right = grid[row + 1, n_columns - 1].get_position(figure)
            separator_y = next_row_left.y1 + 0.014
            figure.add_artist(
                Line2D(
                    [next_row_left.x0, next_row_right.x1],
                    [separator_y, separator_y],
                    transform=figure.transFigure,
                    color="0.82",
                    lw=0.55,
                    zorder=0,
                )
            )

    if official:
        figure.text(
            0.805,
            0.900,
            r"$z_{s|A0}^{\rm desc}="
            r"\dfrac{q_{50,s}-\log_{10}(\mathrm{VMR}_{A0,\mathrm{eff}})}{\sigma_{68,s}}$",
            ha="center",
            va="center",
            fontsize=6.5,
            color=PALETTE["charcoal_violet"],
        )
        figure.text(
            0.018,
            0.43,
            r"Posterior density [dex$^{-1}$]",
            rotation=90,
            ha="center",
            va="center",
            fontsize=6.2,
        )
        figure.text(
            0.53,
            0.105,
            r"$\log_{10}(\mathrm{VMR})$",
            ha="center",
            va="center",
            fontsize=6.0,
        )

    figure.suptitle(
        (
            "Proxima b LIFE retrievals: A1 and A3"
            if official
            else "Proxima LIFE: retrievals A1/A3 frente a la referencia A0"
        ),
        y=0.987,
        fontsize=10.5 if official else 15.5,
    )
    figure.legend(
        handles=legend_handles,
        loc="upper center",
        ncol=3 if official else 4,
        frameon=False,
        fontsize=6.0 if official else 7.3,
        handlelength=1.25 if official else 1.8,
        labelspacing=0.24 if official else 0.48,
        columnspacing=0.8 if official else 1.15,
        handletextpad=0.3 if official else 0.45,
        bbox_to_anchor=(0.34 if official else 0.52, 0.935 if official else 0.952),
    )
    if not official:
        figure.text(
            0.50,
            0.852,
            r"Histogramas: posteriores; barras: q16--q84; sólidos: VULCAN log-X; discontinuas: medianas; "
            r"P--T: mediana y bandas 68/95% (entrada VULCAN discontinua).",
            ha="center",
            va="center",
            fontsize=7.5,
            color=PALETTE["dim_grey"],
        )
        figure.text(
            0.975,
            0.895,
            r"$z_{s|A0}=\dfrac{\mathrm{mediana}_s-\log_{10}(X_{A0,eff})}{\sigma_{68,s}}$",
            color=PALETTE["charcoal_violet"],
            ha="right",
            va="top",
            fontsize=8.0,
            bbox={
                "boxstyle": "round,pad=0.22",
                "facecolor": "white",
                "edgecolor": PALETTE["charcoal_violet"],
                "linewidth": 0.55,
                "alpha": 0.9,
            },
        )
    if not official:
        footer = (
            r"* 100 h: datasets de auditoría independientes (semillas A1/A3 460512527/129315834), fuera de 8/8. "
            r"Ruido diagonal, una realización; $\ln Z$ se reporta por dataset y no es un factor de Bayes entre A1/A3. $z$ es descriptivo, no detección."
        )
        figure.text(
            0.50,
            0.027,
            footer,
            ha="center",
            va="center",
            fontsize=7.0,
            color=PALETTE["dim_grey"],
        )
    return figure


def load_a1_1h_noise_repeat_products() -> dict[str, dict]:
    """Load the current official and previous A1-1 h noise realizations."""
    products: dict[str, dict] = {}
    for realization, stem in A1_1H_NOISE_REPEAT_STEMS.items():
        posterior = load_tagged_posterior(
            "A1", 1, "", product_stem=stem
        )
        columns = posterior["columns"]
        assert isinstance(columns, list)
        products[realization] = {
            "stem": stem,
            "samples": posterior["samples"],
            "column_indices": {
                name.removeprefix("log_"): index
                for index, name in enumerate(columns)
            },
            "log_x": load_audit_log_profile(stem, AUDIT_MOLECULES),
            "pt": load_audit_pt(stem),
            "fit": load_audit_fit_metrics(stem),
        }
    return products


def add_a1_noise_repeat_metrics(
    ax: plt.Axes,
    summary: dict[str, float],
    a0_reference: float,
    a1_reference: float,
) -> None:
    """Annotate an A1 posterior and its descriptive distances to A0/A1."""
    color = AUDIT_POSTERIOR_COLORS["A1"]
    lines = [
        TextArea(
            rf"A1 post. = {summary['median']:.2f} "
            rf"(+{summary['err_high']:.2f}/-{summary['err_low']:.2f}) dex",
            textprops={"color": color, "fontsize": 6.5},
        ),
        TextArea(
            rf"A0 eff. = {a0_reference:.2f}; "
            rf"$z_{{A1|A0}}$={signed_reference_distance(summary, a0_reference):+.2f}$\sigma$",
            textprops={"color": PALETTE["deep_moss"], "fontsize": 6.2},
        ),
        TextArea(
            rf"A1 eff. = {a1_reference:.2f}; "
            rf"$z_{{A1|A1}}$={signed_reference_distance(summary, a1_reference):+.2f}$\sigma$",
            textprops={"color": PALETTE["dark_amaranth"], "fontsize": 6.2},
        ),
    ]
    loc = "upper right" if summary["median"] < np.mean(ax.get_xlim()) else "upper left"
    anchor = (0.975, 0.975) if loc == "upper right" else (0.025, 0.975)
    packed = VPacker(children=lines, align="left", pad=0.0, sep=1.0)
    annotation = AnchoredOffsetbox(
        loc=loc,
        child=packed,
        pad=0.13,
        borderpad=0.24,
        frameon=True,
        bbox_to_anchor=anchor,
        bbox_transform=ax.transAxes,
    )
    annotation.patch.set_boxstyle("round,pad=0.17")
    annotation.patch.set_facecolor("white")
    annotation.patch.set_edgecolor("0.84")
    annotation.patch.set_linewidth(0.55)
    annotation.patch.set_alpha(0.92)
    annotation.set_zorder(20)
    ax.add_artist(annotation)


def plot_a1_1h_noise_repeat_comparison() -> plt.Figure:
    """Compare A1-1 h posterior realizations in the established atlas layout."""
    products = load_a1_1h_noise_repeat_products()
    abundance_profiles = {
        scenario: load_truth_profile(scenario) for scenario in ("A0", "A1")
    }
    input_pressure, input_temperature = load_truth_pt("A1")
    effective = {
        scenario: {
            molecule: log10_column_averaged_mixing_ratio(
                abundance_profiles[scenario], molecule
            )
            for molecule in AUDIT_MOLECULES
        }
        for scenario in ("A0", "A1")
    }

    x_limits: dict[str, tuple[float, float]] = {}
    for molecule in AUDIT_MOLECULES:
        values = [effective[scenario][molecule] for scenario in ("A0", "A1")]
        for product in products.values():
            values.extend(
                [
                    product["samples"][:, product["column_indices"][molecule]],
                    product["log_x"][molecule][:, 3],
                ]
            )
        for scenario in ("A0", "A1"):
            profile = abundance_profiles[scenario]
            truth_log = np.log10(
                np.clip(np.asarray(profile[molecule], dtype=float), PROFILE_FLOOR, None)
            )
            values.append(truth_log[truth_log >= -13.0])
        q_low, q_high = np.percentile(finite_values(values), [0.5, 99.5])
        lower = max(-13.0, float(q_low) - 0.25)
        upper = min(0.0, float(q_high) + 0.25)
        if upper - lower < 0.8:
            midpoint = 0.5 * (upper + lower)
            lower, upper = max(-13.0, midpoint - 0.4), min(0.0, midpoint + 0.4)
        x_limits[molecule] = (lower, upper)

    pt_profiles = [product["pt"] for product in products.values()]
    log_x_profiles = [
        product["log_x"][molecule]
        for product in products.values()
        for molecule in AUDIT_MOLECULES
    ]
    all_pressures = np.concatenate(
        [pt[:, 0] for pt in pt_profiles]
        + [profile[:, 0] for profile in log_x_profiles]
        + [np.asarray(abundance_profiles[s]["PRESS"], dtype=float) for s in ("A0", "A1")]
    )
    pressure_max, pressure_min = float(np.max(all_pressures)), float(np.min(all_pressures))
    temperature_values = [pt[:, 1:] for pt in pt_profiles]
    temperature_values.append(np.asarray(input_temperature)[:, None])
    t_low, t_high = np.percentile(finite_values(temperature_values), [0.5, 99.5])
    t_pad = max(5.0, 0.05 * float(t_high - t_low))
    temperature_limits = (float(t_low - t_pad), float(t_high + t_pad))

    figure = plt.figure(figsize=(2.78 * 3, 2.58 * 2))
    grid = figure.add_gridspec(
        2,
        3,
        left=0.075,
        right=0.945,
        bottom=0.15,
        top=0.735,
        wspace=0.16,
        hspace=0.20,
        width_ratios=[1.0, 1.0, 1.02],
    )
    posterior_color = AUDIT_POSTERIOR_COLORS["A1"]
    legend_handles = [
        Patch(facecolor=posterior_color, edgecolor=posterior_color, alpha=0.28,
              label="A1 posterior (1 h realization)"),
        Line2D([], [], color=posterior_color, lw=1.45, ls="--",
               label="Posterior median"),
        Line2D([], [], color=posterior_color, lw=1.65,
               label="A1 VULCAN log-X"),
        Line2D([], [], color=PALETTE["deep_moss"], lw=1.25, ls=":",
               label="A0 effective"),
        Line2D([], [], color=PALETTE["dark_amaranth"], lw=1.15, ls="-.",
               label="A1 effective"),
        Line2D([], [], color=PALETTE["charcoal_violet"], lw=1.5,
               label="P--T posterior median"),
        Line2D([], [], color=PALETTE["charcoal_violet"], lw=1.1, ls="--",
               label="A1 VULCAN P--T"),
    ]
    shared_molecular_axes: list[plt.Axes | None] = [None] * len(AUDIT_MOLECULES)
    shared_pt_axis: plt.Axes | None = None
    row_labels = {
        "previous": "A1 1 h\nprevious seed",
        "official": "A1 1 h\nselected official",
    }
    for row, realization in enumerate(("previous", "official")):
        product = products[realization]
        for column, molecule in enumerate(AUDIT_MOLECULES):
            axis = figure.add_subplot(
                grid[row, column],
                sharex=shared_molecular_axes[column] if row else None,
            )
            if row == 0:
                shared_molecular_axes[column] = axis
            profile_axis = axis.twinx()
            axis.set_zorder(2)
            profile_axis.set_zorder(1)
            axis.patch.set_alpha(0.0)
            lower, upper = x_limits[molecule]
            values = product["samples"][:, product["column_indices"][molecule]]
            summary = posterior_summary(values)
            axis.hist(
                values,
                bins=np.linspace(lower, upper, 34),
                density=True,
                histtype="stepfilled",
                color=posterior_color,
                edgecolor=posterior_color,
                linewidth=0.78,
                alpha=0.28,
                zorder=3,
            )
            axis.axvline(
                summary["median"], color=posterior_color, lw=1.45, ls="--", zorder=5
            )
            for scenario, color, style in (
                ("A0", PALETTE["deep_moss"], ":"),
                ("A1", PALETTE["dark_amaranth"], "-."),
            ):
                axis.axvline(
                    effective[scenario][molecule],
                    color=color,
                    lw=1.15,
                    ls=style,
                    zorder=6,
                )

            profile = abundance_profiles["A1"]
            truth_log = np.log10(
                np.clip(np.asarray(profile[molecule], dtype=float), PROFILE_FLOOR, None)
            )
            truth_pressure = np.asarray(profile["PRESS"], dtype=float)
            keep = truth_log >= -13.0
            profile_axis.plot(
                truth_log[keep], truth_pressure[keep],
                color=posterior_color, lw=1.55, zorder=4,
            )
            retrieved_profile = product["log_x"][molecule]
            if not np.allclose(retrieved_profile[:, 3], summary["median"], atol=0.15):
                raise ValueError(
                    f"A1 {realization} 1 h {molecule}: log-X median and posterior disagree"
                )

            axis.set_xlim(lower, upper)
            if row == 0:
                axis.set_title(MOLECULE_LABELS[molecule], fontsize=13, pad=6)
            axis.set_axisbelow(True)
            axis.grid(axis="y", alpha=0.22, linestyle=":")
            axis.tick_params(direction="in", top=True, right=True, labelsize=8.1)
            axis.set_ylim(bottom=0.0)
            profile_axis.set_yscale("log")
            profile_axis.set_ylim(pressure_max * 1.03, pressure_min / 1.03)
            profile_axis.tick_params(axis="y", direction="in", labelsize=7.8)
            for spine in ("top", "left", "bottom"):
                profile_axis.spines[spine].set_visible(False)
            profile_axis.spines["right"].set_visible(
                column == len(AUDIT_MOLECULES) - 1
            )
            if column == 0:
                axis.set_ylabel("Probability density")
                axis.text(
                    -0.63, 0.50, row_labels[realization], transform=axis.transAxes,
                    rotation=90, va="center", ha="center", fontsize=9.2,
                    fontweight="bold",
                )
            else:
                axis.tick_params(axis="y", labelleft=False)
            if column != len(AUDIT_MOLECULES) - 1:
                profile_axis.set_yticks([])
                profile_axis.set_yticks([], minor=True)
                profile_axis.tick_params(axis="y", right=False, labelright=False)
            else:
                profile_axis.set_yticks([], minor=True)
                profile_axis.tick_params(axis="y", right=False, labelright=False)
            if row == 1:
                axis.set_xlabel(r"$\log_{10}$ VMR")
            else:
                axis.tick_params(axis="x", labelbottom=False)
            axis.xaxis.set_major_locator(plt.MaxNLocator(4))
            axis.set_ylim(top=axis.get_ylim()[1] * 1.05)
            density_top = axis.get_ylim()[1]
            axis.errorbar(
                summary["median"],
                density_top * 0.09,
                xerr=np.array([[summary["err_low"]], [summary["err_high"]]]),
                fmt="o",
                ms=3.2,
                color=posterior_color,
                markerfacecolor=posterior_color,
                markeredgecolor="black",
                markeredgewidth=0.35,
                ecolor=posterior_color,
                elinewidth=1.15,
                capsize=2.2,
                zorder=8,
            )
            add_a1_noise_repeat_metrics(
                axis, summary, effective["A0"][molecule], effective["A1"][molecule]
            )

        pt_axis = figure.add_subplot(
            grid[row, 2], sharex=shared_pt_axis if row else None
        )
        if row == 0:
            shared_pt_axis = pt_axis
        pt = product["pt"]
        pressure = pt[:, 0]
        pt_axis.fill_betweenx(pressure, pt[:, 1], pt[:, 5], color=posterior_color,
                              alpha=0.075, linewidth=0, zorder=1)
        pt_axis.fill_betweenx(pressure, pt[:, 2], pt[:, 4], color=posterior_color,
                              alpha=0.20, linewidth=0, zorder=2)
        pt_axis.plot(pt[:, 3], pressure, color=PALETTE["charcoal_violet"],
                     lw=1.55, zorder=4)
        pt_axis.plot(input_temperature, input_pressure, color=posterior_color,
                     lw=1.1, ls="--", alpha=0.95, zorder=5)
        if row == 0:
            pt_axis.set_title("P--T profile", fontsize=13, pad=6)
        pt_axis.set_yscale("log")
        pt_axis.set_ylim(pressure_max * 1.03, pressure_min / 1.03)
        pt_axis.set_xlim(*temperature_limits)
        pt_axis.set_axisbelow(True)
        pt_axis.grid(which="major", alpha=0.20, linestyle=":")
        pt_axis.tick_params(direction="in", top=True, right=True, labelsize=8.2)
        if row == 0:
            pt_axis.tick_params(axis="x", labelbottom=False)
        else:
            pt_axis.set_xlabel("Temperature [K]")
        pt_axis.yaxis.tick_right()
        pt_axis.yaxis.set_label_position("right")
        pt_axis.set_ylabel("Pressure [bar]")
        pt_axis.xaxis.set_major_locator(plt.MaxNLocator(4))
        fit = product["fit"]
        fit_text = (
            rf"$\chi^2_{{red}}$={fit['chi2_red']:.2f} ({fit['dof']:.0f} dof)"
            "\n"
            rf"$\ln Z$={fit['ln_z']:.2f}$\pm${fit['ln_z_error']:.2f} (this dataset)"
        )
        pt_axis.text(
            0.025, 0.975, fit_text, transform=pt_axis.transAxes,
            va="top", ha="left", fontsize=6.8, color=PALETTE["charcoal_violet"],
            bbox={"boxstyle": "round,pad=0.20", "facecolor": "white",
                  "edgecolor": "0.84", "linewidth": 0.55, "alpha": 0.92},
        )

    figure.suptitle(
        "Proxima LIFE A1 at 1 h: selected official vs previous noise realization",
        y=0.995,
        fontsize=15.5,
    )
    figure.legend(
        handles=legend_handles,
        loc="upper center",
        ncol=4,
        frameon=False,
        fontsize=7.2,
        handlelength=1.8,
        labelspacing=0.32,
        columnspacing=1.0,
        handletextpad=0.42,
        bbox_to_anchor=(0.50, 0.952),
    )
    figure.text(
        0.50, 0.785,
        "Histograms: posterior; bars: q16–q84; solid log-X: A1 VULCAN; "
        "dotted/dash-dot: A0/A1 effective references; P–T bands: 68/95%.",
        ha="center", va="center", fontsize=7.4, color=PALETTE["dim_grey"],
    )
    figure.text(
        0.50, 0.027,
        r"Independent diagonal-noise realizations; each $\ln Z$ is dataset-specific, not a Bayes factor. "
        r"The current official seed was selected after inspecting both posteriors; treat this comparison as post hoc.",
        ha="center", va="center", fontsize=6.6, color=PALETTE["dim_grey"],
    )
    return figure


def load_four_row_audit_posterior_samples() -> dict[int, np.ndarray]:
    """Load canonical and robust audit A3 posteriors for a four-row figure."""
    audit_tag = "_robust_lifesim_direct"
    return {
        10: load_samples("A3", 10),
        240: load_samples("A3", 240),
        500: load_samples("A3", 500, audit_tag),
        1200: load_samples("A3", 1200, audit_tag),
    }


def save_figure(
    fig: plt.Figure,
    stem: str,
    output_dir: Path,
    *,
    dpi: int = 240,
    write_svg: bool = False,
) -> tuple[Path, Path]:
    """Write the requested PNG and PDF pair and close the figure."""
    output_dir.mkdir(parents=True, exist_ok=True)
    png_path = output_dir / f"{stem}.png"
    pdf_path = output_dir / f"{stem}.pdf"
    fig.savefig(png_path, dpi=dpi, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    if write_svg:
        svg_path = output_dir / f"{stem}.svg"
        fig.savefig(svg_path, bbox_inches="tight")
        print(f"saved {svg_path.relative_to(REPO)}")
    plt.close(fig)
    print(f"saved {png_path.relative_to(REPO)}")
    print(f"saved {pdf_path.relative_to(REPO)}")
    return png_path, pdf_path


def write_official_provenance(
    output_dir: Path,
    figure_stem: str,
    *,
    run_stems: dict[int, dict[str, str]] = OFFICIAL_TIME_RUN_STEMS,
    run_roots: dict[tuple[int, str], Path] = OFFICIAL_RUN_ROOTS,
    revision: str = "2026-10-20_A3_100h_update",
    audit_status: str = "historical_sources_mixed; see limits",
    case_sources: dict[tuple[int, str], dict] | None = None,
    shared_inputs: tuple[Path, ...] = (),
    displayed_molecules: tuple[str, ...] = OFFICIAL_PROFILE_MOLECULES,
    include_pt_panel: bool = True,
    limits: tuple[str, ...] = (
        "Only A3-100h has been replaced; repeat the full matrix with a common operator.",
        "Descriptive z is not a molecular detection significance.",
        "Each case uses one noise realization and a diagonal likelihood.",
    ),
) -> None:
    """Record exact input products and labels for an official comparison view."""
    products = load_a1_a3_time_comparison_products(
        run_stems,
        OFFICIAL_PROFILE_MOLECULES,
        run_roots,
    )
    references = load_truth_profile("A0")
    cases = []
    for (hours, scenario), product in products.items():
        root = product["product_root"]
        stem = product["stem"]
        paths = [
            root / "samples" / f"{stem}_{suffix}.txt"
            for suffix in ("samples", "PT_retrieved", "log_X_retrieved")
        ]
        paths.append(root / "results" / f"{stem}_results.txt")
        source = (case_sources or {}).get((hours, scenario), {})
        source_paths = source.get("paths", {})
        source_hashes = {
            label: hashlib.sha256(require(path).read_bytes()).hexdigest()
            for label, path in source_paths.items()
        }
        expected_dataset = source.get("dataset_sha256_expected")
        if expected_dataset and source_hashes.get("dataset") != expected_dataset:
            raise ValueError(
                f"Dataset hash mismatch for {scenario} {hours} h: "
                f"expected {expected_dataset}, got {source_hashes.get('dataset')}"
            )
        summaries = {}
        for molecule in OFFICIAL_PROFILE_MOLECULES:
            values = product["samples"][:, product["column_indices"][molecule]]
            summary = posterior_summary(values)
            reference = log10_column_averaged_mixing_ratio(references, molecule)
            summaries[molecule] = {
                **summary,
                "a0_effective": reference,
                "z_descriptive_a0": signed_reference_distance(summary, reference),
            }
        cases.append({
            "scenario": scenario,
            "hours": hours,
            "stem": stem,
            "operator": (
                "corrected" if (hours, scenario) in run_roots else "historical"
            ),
            "source": {
                key: value for key, value in source.items() if key != "paths"
            },
            "source_sha256": source_hashes,
            "n_posterior_samples": len(product["samples"]),
            "input_sha256": {
                path.relative_to(REPO).as_posix(): hashlib.sha256(
                    require(path).read_bytes()
                ).hexdigest()
                for path in paths
            },
            "posterior_summaries": summaries,
            "fit_native": product["fit"],
        })
    profile_paths = [
        PROFILE_DIR / f"{SCENARIOS[scenario]['profile_stem']}_{suffix}.txt"
        for scenario in ("A0", "A1", "A3")
        for suffix in ("chem", "PT")
    ]
    metadata = {
        "revision": revision,
        "figure_stem": figure_stem,
        "audit_status": audit_status,
        "displayed_molecules": list(displayed_molecules),
        "includes_pt_panel": include_pt_panel,
        "cases": cases,
        "profile_sha256": {
            path.relative_to(REPO).as_posix(): hashlib.sha256(
                require(path).read_bytes()
            ).hexdigest()
            for path in profile_paths
        },
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "shared_inputs_sha256": {
            path.relative_to(REPO).as_posix(): hashlib.sha256(
                require(path).read_bytes()
            ).hexdigest()
            for path in shared_inputs
        },
        "figure_sha256": {
            extension: hashlib.sha256(
                (output_dir / f"{figure_stem}.{extension}").read_bytes()
            ).hexdigest()
            for extension in ("png", "pdf", "svg")
        },
        "limits": list(limits),
    }
    path = output_dir / f"{figure_stem}.provenance.json"
    path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"saved {path.relative_to(REPO)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PLOTS_DIR,
        help="Directory for generated figures (default: campaign plots directory).",
    )
    parser.add_argument(
        "--four-row-audit-output",
        type=Path,
        default=None,
        help="Optional directory for the four-row 10/240/500/1200 h audit posterior figure.",
    )
    parser.add_argument(
        "--official-a1-a3-times",
        action="store_true",
        help=(
            "Generate the official A1/A3 1/10/100 h figure with six molecular "
            "posteriors, vertical profiles, A0 references, and P--T (O2 omitted)."
        ),
    )
    parser.add_argument(
        "--official-corrected-bin-matrix-fulls",
        action="store_true",
        help=(
            "Generate the versioned official A1/A3 1/10/100 h full-model "
            "posterior figure from corrected-bin baselines."
        ),
    )
    parser.add_argument(
        "--official-a1-a3-times-full-prior-xlim",
        action="store_true",
        help=(
            "Generate the preserved full-prior V1 companion for the official "
            "A1/A3 1/10/100 h figure."
        ),
    )
    parser.add_argument(
        "--official-a1-a3-times-dynamic-xlim",
        action="store_true",
        help=(
            "Generate the companion official A1/A3 1/10/100 h figure with "
            "x limits from posterior samples and VULCAN profiles, clipped to "
            "the retrieval prior."
        ),
    )
    parser.add_argument(
        "--official-a1-a3-times-posterior-xlim",
        action="store_true",
        help=(
            "Generate the official A1/A3 1/10/100 h companion with x limits "
            "derived only from posterior samples and clipped to the prior."
        ),
    )
    parser.add_argument(
        "--a1-1h-noise-repeat",
        action="store_true",
        help=(
            "Generate the A1 1 h selected-versus-previous realization "
            "posterior, vertical log-X, and P--T comparison."
        ),
    )
    parser.add_argument(
        "--audit-a1-a3-times",
        "--audit-a1-a3-240h",
        dest="audit_a1_a3_times",
        action="store_true",
        help=(
            "Generate only the separate A1/A3 10/100/240 h audit figure "
            "with molecular posteriors, vertical log-X profiles, and P--T. "
            "The older --audit-a1-a3-240h spelling remains an alias."
        ),
    )
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    four_row_audit_output = (
        args.four_row_audit_output.resolve()
        if args.four_row_audit_output is not None
        else None
    )

    if args.a1_1h_noise_repeat:
        output_dir.mkdir(parents=True, exist_ok=True)
        save_figure(
            plot_a1_1h_noise_repeat_comparison(),
            "retrieval_A1_1h_selected_official_vs_previous_N2O_NH3_PT_proxima",
            output_dir,
        )
        return

    if args.official_corrected_bin_matrix_fulls:
        output_dir.mkdir(parents=True, exist_ok=True)
        figure_stem = (
            "retrieval_A1_A3_1_10_100h_official_posteriors_N2O_NH3_first_no_PT_"
            "proxima_20261028"
        )
        save_figure(
            plot_a1_a3_time_comparison(
                run_stems=CORRECTED_MATRIX_FULL_RUN_STEMS,
                official=True,
                dynamic_xlimits=True,
                molecules=OFFICIAL_MATRIX_POSTERIOR_MOLECULES,
                run_roots=CORRECTED_MATRIX_FULL_RUN_ROOTS,
                include_pt_column=False,
            ),
            figure_stem,
            output_dir,
            dpi=300,
            write_svg=True,
        )
        write_official_provenance(
            output_dir,
            figure_stem,
            run_stems=CORRECTED_MATRIX_FULL_RUN_STEMS,
            run_roots=CORRECTED_MATRIX_FULL_RUN_ROOTS,
            revision="2026-10-28_A1_A3_N2O_NH3_first_no_PT",
            audit_status=(
                "official_visualization_of_audited_A1_A3_full_baselines; "
                "independent_audit_PASS_2026-10-28"
            ),
            case_sources=CORRECTED_MATRIX_CASE_SOURCES,
            shared_inputs=CORRECTED_MATRIX_SHARED_INPUTS,
            displayed_molecules=OFFICIAL_MATRIX_POSTERIOR_MOLECULES,
            include_pt_panel=False,
            limits=(
                "A1 full retrieval products passed independent final audit on 2026-10-28.",
                "A3 full retrieval products are previously validated corrected-bin baselines; the current LOO campaign does not rerun A3 full models.",
                "The figure compares one noise realization per scenario/exposure; each ln Z is dataset-specific, not an A1-versus-A3 Bayes factor.",
                "Descriptive offsets from the effective A0 reference are not individual detection significances or evidence for an ExoFarm scenario.",
                "Display order: N2O, NH3, H2O, CO2, CH4, O3; the P-T panel is omitted by design. O2 remains active in the retrieval.",
            ),
        )
        return

    if args.official_a1_a3_times_full_prior_xlim:
        output_dir.mkdir(parents=True, exist_ok=True)
        save_figure(
            plot_a1_a3_time_comparison(
                run_stems=OFFICIAL_TIME_RUN_STEMS,
                official=True,
                molecules=OFFICIAL_PROFILE_MOLECULES,
            ),
            "retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima_full_prior_xlim",
            output_dir,
            dpi=300,
            write_svg=True,
        )
        return

    if args.official_a1_a3_times_dynamic_xlim:
        output_dir.mkdir(parents=True, exist_ok=True)
        save_figure(
            plot_a1_a3_time_comparison(
                run_stems=OFFICIAL_TIME_RUN_STEMS,
                official=True,
                dynamic_xlimits=True,
                molecules=OFFICIAL_PROFILE_MOLECULES,
            ),
            "retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima_dynamic_xlim",
            output_dir,
            dpi=300,
            write_svg=True,
        )
        return

    if args.official_a1_a3_times_posterior_xlim:
        output_dir.mkdir(parents=True, exist_ok=True)
        save_figure(
            plot_a1_a3_time_comparison(
                run_stems=OFFICIAL_TIME_RUN_STEMS,
                official=True,
                posterior_only_xlimits=True,
                molecules=OFFICIAL_PROFILE_MOLECULES,
            ),
            "retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima_posterior_xlim",
            output_dir,
            dpi=300,
            write_svg=True,
        )
        return

    if args.official_a1_a3_times:
        output_dir.mkdir(parents=True, exist_ok=True)
        save_figure(
            plot_a1_a3_time_comparison(
                run_stems=OFFICIAL_TIME_RUN_STEMS,
                official=True,
                dynamic_xlimits=True,
                molecules=OFFICIAL_PROFILE_MOLECULES,
            ),
            "retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima",
            output_dir,
            dpi=300,
            write_svg=True,
        )
        write_official_provenance(
            output_dir,
            "retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima",
        )
        return

    if args.audit_a1_a3_times:
        output_dir.mkdir(parents=True, exist_ok=True)
        save_figure(
            plot_a1_a3_time_comparison(),
            "retrieval_A1_A3_10_100_240h_audit_molecular_profiles_PT_proxima",
            output_dir,
        )
        return

    products = load_campaign_products()
    pilot_spectrum = SAMPLES_DIR / f"{retrieval_stem('A3', 1200)}_spectrum_retrieved.txt"
    if pilot_spectrum.exists():
        print("[info] A3-1200h retrieval found; classified as excluded pilot, not plotted in the canonical figures.")
    print("[info] loaded canonical retrieval products for plotted extremes: A0/A3 x {10 h, 240 h} = 4 retrievals")

    save_figure(plot_global_spectra(products), "retrieval_global_spectra_proxima", output_dir)
    save_figure(plot_molecular_zooms(products), "retrieval_molecular_zooms_proxima", output_dir)
    save_figure(plot_profiles_posteriors(products), "retrieval_profiles_posteriors_proxima", output_dir)
    if four_row_audit_output is not None:
        audit_samples = load_four_row_audit_posterior_samples()
        save_figure(
            plot_profiles_posteriors(
                products,
                posterior_hours=(10, 240, 500, 1200),
                posterior_samples=audit_samples,
                title="Proxima b: A3 Posterior by Integration Time",
            ),
            "retrieval_profiles_posteriors_proxima_4rows_audit",
            four_row_audit_output,
        )


if __name__ == "__main__":
    main()
