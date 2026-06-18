import os
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# Add local path to import project style
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE
from plot_pure_transmission_spectra import compute_system_spectra, rebin_curve

OUTPUT_DIR = BASE_DIR / "POSEIDON_output" / "TRAPPIST-1e"
RETRIEVAL_SAMPLES_DIR = OUTPUT_DIR / "retrievals" / "samples"
SYNTHETIC_DATA_DIR = OUTPUT_DIR / "synthetic_data" / "base_1transit"
PLOTS_DIR = OUTPUT_DIR / "plots"

WL_MIN = 0.6
WL_MAX = 12.0

SCENARIO_LABELS = {
    "A0": "A0: Pre-agricultural",
    "A3": "A3: Extreme ExoFarm",
}
SCENARIO_FILE_LABELS = {
    "A0": "Trappist_A0_PreAgri",
    "A3": "Trappist_A3_Extreme",
}

# Retrieval envelope colors (standard scenario colors)
RETRIEVED_COLORS = {
    "A0": "#95E36B",  # scenario_green
    "A3": "#E34F95",  # scenario_pink
}

# True model colors (using vibrant scenario_cyan and scenario_violet from the main palette as requested)
TRUE_COLORS = {
    "A0": "#56E3DB",  # scenario_cyan
    "A3": "#BD62E3",  # scenario_violet
}

# Observation point colors (darker shades for readability)
OBSERVATION_COLORS = {
    "A0": "#3F633E",  # deep_moss
    "A3": "#840032",  # dark_amaranth
}

INSTRUMENT_FILE_LABELS = {
    "NIRSpec": "JWST_NIRSpec_PRISM",
    "MIRI": "JWST_MIRI_LRS",
}

# Zoom windows adjusted according to user feedback:
# 1. 4.5 um N2O shifted to start at 3.8 um.
# 2. 8.6 um N2O expanded to go from 7.0 to 9.2 um.
# 3. 10.7 um NH3 range limited from 9.5 to 12.0 um.
ZOOM_WINDOWS = [
    {"name": r"N$_2$O (4.5 $\mu$m)", "xlim": (3.8, 4.9)},
    {"name": r"N$_2$O (8.6 $\mu$m)", "xlim": (7.0, 9.2)},
    {"name": r"NH$_3$ (10.7 $\mu$m)", "xlim": (9.5, 12.0)},
]

def retrieval_spectrum_path(scenario, transits):
    return RETRIEVAL_SAMPLES_DIR / (
        f"TRAPPIST1e_{scenario}_retrieval_isotherm_isochem_"
        f"{transits}transits_NIRSpec_MIRI_spectrum_retrieved.txt"
    )

def synthetic_observation_path(scenario, instrument, transits):
    return SYNTHETIC_DATA_DIR / (
        f"TRAPPIST-1e_SYNTHETIC_{INSTRUMENT_FILE_LABELS[instrument]}_"
        f"{SCENARIO_FILE_LABELS[scenario]}_N_trans_{transits}.dat"
    )

def load_retrieved_spectrum(path):
    data = np.loadtxt(path, skiprows=1)
    return {
        "wl": data[:, 0],
        "minus_2": data[:, 1] * 1.0e6,
        "minus_1": data[:, 2] * 1.0e6,
        "median": data[:, 3] * 1.0e6,
        "plus_1": data[:, 4] * 1.0e6,
        "plus_2": data[:, 5] * 1.0e6,
    }

def load_synthetic_observations(scenario, transits):
    observations = []
    for instrument in ("NIRSpec", "MIRI"):
        path = synthetic_observation_path(scenario, instrument, transits)
        if not path.exists():
            continue
        data = np.loadtxt(path)
        observations.append(
            {
                "instrument": instrument,
                "wl": data[:, 0],
                "wl_err": data[:, 1],
                "depth": data[:, 2] * 1.0e6,
                "depth_err": data[:, 3] * 1.0e6,
            }
        )
    return observations

def resample_retrieved_spectrum(spec, target_wl):
    rebinned = {}
    for key in ("minus_2", "minus_1", "median", "plus_1", "plus_2"):
        rebinned[key] = np.interp(target_wl, spec["wl"], spec[key])
    rebinned["wl"] = target_wl
    return rebinned

def main():
    # Load true spectra
    print("Computing true spectra...")
    wl_grid, spectra = compute_system_spectra("TRAPPIST-1e", WL_MIN, WL_MAX, native_r=10000.0)
    truth = {
        "A0": {"wl": wl_grid, "depth": spectra["A0"] * 1.0e6},
        "A3": {"wl": wl_grid, "depth": spectra["A3"] * 1.0e6},
    }

    # Setup the plot: 2 rows (5 and 100 transits), 3 columns (zooms)
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["STIX Two Text", "STIXGeneral", "Times New Roman"],
        "mathtext.fontset": "stix",
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.top": True,
        "ytick.right": True,
    })

    fig, axes = plt.subplots(2, 3, figsize=(13, 8), constrained_layout=True)
    
    transit_options = [5, 100]
    
    # Store y-values to compute custom y-limits for each column
    column_y_values = [[] for _ in range(3)]

    # First pass: load all data and collect y-values for plotting and scaling
    data_cache = {}
    for r_idx, transits in enumerate(transit_options):
        data_cache[transits] = {}
        for scenario in ("A0", "A3"):
            ret_path = retrieval_spectrum_path(scenario, transits)
            if ret_path.exists():
                ret_raw = load_retrieved_spectrum(ret_path)
            else:
                ret_raw = None
                print(f"Warning: missing retrieval for {scenario} {transits} transits")
                
            obs = load_synthetic_observations(scenario, transits)
            data_cache[transits][scenario] = {
                "retrieved_raw": ret_raw,
                "observations": obs,
            }

            if ret_raw is not None:
                # Add to y-value scaling limits per window using a smooth resampled version
                for c_idx, window in enumerate(ZOOM_WINDOWS):
                    x_min, x_max = window["xlim"]
                    target_wl = np.linspace(x_min, x_max, 100)
                    ret_resampled = resample_retrieved_spectrum(ret_raw, target_wl)
                    
                    column_y_values[c_idx].extend(ret_resampled["minus_2"])
                    column_y_values[c_idx].extend(ret_resampled["plus_2"])
            
            # Also add truth spectrum to scaling limits
            for c_idx, window in enumerate(ZOOM_WINDOWS):
                x_min, x_max = window["xlim"]
                mask = (truth[scenario]["wl"] >= x_min) & (truth[scenario]["wl"] <= x_max)
                column_y_values[c_idx].extend(truth[scenario]["depth"][mask])

    # Plotting loop
    for r_idx, transits in enumerate(transit_options):
        for c_idx, window in enumerate(ZOOM_WINDOWS):
            ax = axes[r_idx, c_idx]
            x_min, x_max = window["xlim"]
            
            # Get common observation wavelengths in this window for rebinning the True curves
            obs_wls = []
            for scenario in ("A0", "A3"):
                obs_list = data_cache[transits][scenario]["observations"]
                for obs in obs_list:
                    mask = (obs["wl"] >= x_min) & (obs["wl"] <= x_max)
                    obs_wls.extend(obs["wl"][mask])
            
            # Sort and remove duplicates to create a clean instrument-resolution grid for True curves
            if len(obs_wls) > 0:
                true_plot_wl = np.sort(np.unique(obs_wls))
            else:
                true_plot_wl = np.linspace(x_min, x_max, 60)
            
            # 1. Plot retrieved spectrum envelopes (1 and 2 sigma) - slightly more saturated as requested
            for scenario in ("A0", "A3"):
                ret_raw = data_cache[transits][scenario]["retrieved_raw"]
                if ret_raw is None:
                    continue
                color = RETRIEVED_COLORS[scenario]
                
                # Smooth target grid of 100 points for plotting
                target_wl = np.linspace(x_min, x_max, 100)
                ret = resample_retrieved_spectrum(ret_raw, target_wl)
                
                # 2-sigma envelope (more saturated, alpha=0.14)
                ax.fill_between(
                    ret["wl"],
                    ret["minus_2"],
                    ret["plus_2"],
                    color=color,
                    alpha=0.14,
                    lw=0,
                    zorder=1,
                )
                # 1-sigma envelope (more saturated, alpha=0.26)
                ax.fill_between(
                    ret["wl"],
                    ret["minus_1"],
                    ret["plus_1"],
                    color=color,
                    alpha=0.26,
                    lw=0,
                    zorder=2,
                )
                # Median retrieved fit (alpha=0.85)
                ax.plot(
                    ret["wl"],
                    ret["median"],
                    color=color,
                    linewidth=1.8,
                    alpha=0.85,
                    zorder=3,
                    label=f"Retrieved {scenario}" if r_idx == 0 and c_idx == 0 else "_nolegend_",
                )

            # 2. Plot synthetic observations (points with error bars) at the noisy observed value - NO TRANSPARENCY (alpha=1.0)
            for scenario in ("A0", "A3"):
                color = OBSERVATION_COLORS[scenario]
                obs_list = data_cache[transits][scenario]["observations"]
                for obs in obs_list:
                    # Filter observations inside current window
                    mask = (obs["wl"] >= x_min) & (obs["wl"] <= x_max)
                    if not np.any(mask):
                        continue
                    
                    # Plot observations with alpha=1.0 (no transparency) as requested
                    ax.errorbar(
                        obs["wl"][mask],
                        obs["depth"][mask],
                        yerr=obs["depth_err"][mask],
                        fmt="o",
                        markersize=3,
                        color=color,
                        ecolor=color,
                        alpha=1.0,
                        elinewidth=0.8,
                        capsize=1.5,
                        linestyle="none",
                        zorder=4,
                        label=f"Obs {scenario}" if r_idx == 0 and c_idx == 0 else "_nolegend_",
                    )

            # 3. Plot the true spectra rebinned to the observation wavelengths - DOTTED (linestyle=":")
            for scenario in ("A0", "A3"):
                color = TRUE_COLORS[scenario]
                
                # Interpolate True model to the observation wavelengths
                true_y_rebinned = np.interp(true_plot_wl, truth[scenario]["wl"], truth[scenario]["depth"])
                
                ax.plot(
                    true_plot_wl,
                    true_y_rebinned,
                    color=color,
                    linestyle=":",       # Dotted as requested
                    linewidth=1.2,       # Thin
                    label=f"True {scenario}" if r_idx == 0 and c_idx == 0 else "_nolegend_",
                    zorder=20,           # On top
                )

            # Grid and styling
            ax.set_xlim(x_min, x_max)
            ax.grid(alpha=0.12, which="both", linestyle="--")
            
            # Common y-limits per column
            y_vals = column_y_values[c_idx]
            if len(y_vals) > 0:
                y_low, y_high = np.percentile(y_vals, [0.5, 99.5])
                y_pad = max(10.0, 0.15 * (y_high - y_low))
                ax.set_ylim(y_low - y_pad, y_high + y_pad)
                
            # Column headers on top row
            if r_idx == 0:
                ax.set_title(window["name"], fontsize=12, fontweight="bold", pad=10)
                
            # X label only on bottom row
            if r_idx == 1:
                ax.set_xlabel(r"Wavelength ($\mu$m)", fontsize=10)
                
            # Y label only on first column
            if c_idx == 0:
                ax.set_ylabel("Transit Depth (ppm)", fontsize=10)
                
            # Add row indicators on the right side of the figure
            if c_idx == 2:
                ax.text(
                    1.05, 0.5, f"{transits} Transits",
                    transform=ax.transAxes,
                    fontsize=12,
                    fontweight="bold",
                    va="center",
                    ha="left",
                    rotation=-90
                )

    # Put a nice clean legend on the first column
    axes[0, 0].legend(frameon=True, facecolor="white", edgecolor="none", framealpha=0.8, fontsize=8, loc="upper right")

    # Shift layout slightly to avoid overlap with suptitle
    fig.suptitle("TRAPPIST-1e ExoFarm Retrieval Performance (A0 vs A3)", fontsize=14, fontweight="bold", y=0.98)
    
    # Save results
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    png_path = PLOTS_DIR / "trappist_retrieved_zooms_A0_A3.png"
    pdf_path = PLOTS_DIR / "trappist_retrieved_zooms_A0_A3.pdf"
    
    fig.savefig(png_path, dpi=240, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    print(f"Saved: {png_path}")
    print(f"Saved: {pdf_path}")
    plt.close(fig)

if __name__ == "__main__":
    main()
