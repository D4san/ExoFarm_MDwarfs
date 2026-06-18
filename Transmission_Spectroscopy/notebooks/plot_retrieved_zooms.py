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

# True model colors (using same colors as observation dots for consistency and visual matching)
TRUE_COLORS = {
    "A0": "#3F633E",  # deep_moss (same as Observed A0)
    "A3": "#840032",  # dark_amaranth (same as Observed A3)
}

# Observation point colors (darker shades for readability)
OBSERVATION_COLORS = {
    "A0": "#3F633E",  # deep_moss
    "A3": "#840032",  # dark_amaranth
}

# Observation marker shapes (round for A0, diamond for A3)
SCENARIO_MARKERS = {
    "A0": "o",  # Circle / round
    "A3": "d",  # Thin diamond
}

INSTRUMENT_FILE_LABELS = {
    "NIRSpec": "JWST_NIRSpec_PRISM",
    "MIRI": "JWST_MIRI_LRS",
}

# Zoom windows restricted according to user feedback
ZOOM_WINDOWS = [
    {"name": r"N$_2$O (4.5 $\mu$m)", "xlim": (4.4, 4.7)},
    {"name": r"N$_2$O (8.6 $\mu$m)", "xlim": (8.2, 9.0)},
    {"name": r"NH$_3$ (10.7 $\mu$m)", "xlim": (10.6, 11.7)},
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

def generate_zoomed_plot(transit_options, truth, data_cache, column_y_values, v2_style=False):
    fig, axes = plt.subplots(2, 3, figsize=(13, 8))
    
    for r_idx, transits in enumerate(transit_options):
        for c_idx, window in enumerate(ZOOM_WINDOWS):
            ax = axes[r_idx, c_idx]
            x_min, x_max = window["xlim"]
            
            # Smooth target grid of 100 points for plotting (both retrieved and true)
            target_wl = np.linspace(x_min, x_max, 100)
            
            # 1. Plot retrieved spectrum envelopes (1 and 2 sigma)
            for scenario in ("A0", "A3"):
                ret_raw = data_cache[transits][scenario]["retrieved_raw"]
                if ret_raw is None:
                    continue
                color = RETRIEVED_COLORS[scenario]
                
                ret = resample_retrieved_spectrum(ret_raw, target_wl)
                
                # 2-sigma envelope (alpha=0.18)
                ax.fill_between(
                    ret["wl"],
                    ret["minus_2"],
                    ret["plus_2"],
                    color=color,
                    alpha=0.18,
                    lw=0,
                    zorder=11,
                )
                # 1-sigma envelope (alpha=0.32)
                ax.fill_between(
                    ret["wl"],
                    ret["minus_1"],
                    ret["plus_1"],
                    color=color,
                    alpha=0.32,
                    lw=0,
                    zorder=12,
                )
                # Median retrieved fit (linewidth=2.0, alpha=0.90, zorder=20)
                ax.plot(
                    ret["wl"],
                    ret["median"],
                    color=color,
                    linewidth=2.0,
                    alpha=0.90,
                    zorder=20,
                    label=f"Retrieved {scenario}" if r_idx == 0 and c_idx == 0 else "_nolegend_",
                )

            # 2. Plot synthetic observations (points with error bars) at noisy values - slight transparency (alpha=0.75)
            for scenario in ("A0", "A3"):
                color = OBSERVATION_COLORS[scenario]
                obs_list = data_cache[transits][scenario]["observations"]
                for obs in obs_list:
                    mask = (obs["wl"] >= x_min) & (obs["wl"] <= x_max)
                    if not np.any(mask):
                        continue
                    
                    # Plot error bars and points with alpha=0.70 (round/diamond markers and markersize=3.5) - zorder=40 (front)
                    ax.errorbar(
                        obs["wl"][mask],
                        obs["depth"][mask],
                        yerr=obs["depth_err"][mask],
                        fmt=SCENARIO_MARKERS[scenario],
                        markersize=3.5,
                        color=color,
                        ecolor=color,
                        alpha=0.70,
                        elinewidth=0.6,
                        capsize=1.0,
                        linestyle="none",
                        zorder=40,
                        label=f"Obs {scenario}" if r_idx == 0 and c_idx == 0 else "_nolegend_",
                    )

            # 3. Plot true spectra - thin line (zorder=30, front of retrieved, behind obs)
            for scenario in ("A0", "A3"):
                color = TRUE_COLORS[scenario]
                true_y_smooth = np.interp(target_wl, truth[scenario]["wl"], truth[scenario]["depth"])
                linestyle = "-" if v2_style else ":"
                linewidth = 1.0 if v2_style else 1.4
                
                ax.plot(
                    target_wl,
                    true_y_smooth,
                    color=color,
                    linestyle=linestyle,
                    linewidth=linewidth,
                    alpha=0.70,          # More transparent
                    label=f"True {scenario}" if r_idx == 0 and c_idx == 0 else "_nolegend_",
                    zorder=30,           # Front of retrieved fit/envelopes
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
                
            if r_idx == 0:
                ax.set_title(window["name"], fontsize=12, fontweight="bold", pad=10)
            if r_idx == 1:
                ax.set_xlabel(r"Wavelength ($\mu$m)", fontsize=10)
            if c_idx == 0:
                ax.set_ylabel(r"Transit Depth $(R_p/R_s)^2$ (ppm)", fontsize=10)
                
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

    import matplotlib.lines as mlines
    # Custom legend handles arranged in columns (for column-first legend layout)
    ret_a0_handle = mlines.Line2D([], [], color=RETRIEVED_COLORS["A0"], lw=2.5, label="Retrieved A0")
    ret_a3_handle = mlines.Line2D([], [], color=RETRIEVED_COLORS["A3"], lw=2.5, label="Retrieved A3")

    true_linestyle = "-" if v2_style else ":"
    true_linewidth = 1.2 if v2_style else 1.6
    true_a0_handle = mlines.Line2D([], [], color=TRUE_COLORS["A0"], linestyle=true_linestyle, lw=true_linewidth, alpha=0.70, label="True A0")
    true_a3_handle = mlines.Line2D([], [], color=TRUE_COLORS["A3"], linestyle=true_linestyle, lw=true_linewidth, alpha=0.70, label="True A3")

    obs_a0_handle = mlines.Line2D([], [], color="none", marker=SCENARIO_MARKERS["A0"], markersize=6.0, 
                                  markerfacecolor=OBSERVATION_COLORS["A0"], markeredgecolor=OBSERVATION_COLORS["A0"], 
                                  alpha=0.70, label="Observed A0")
    obs_a3_handle = mlines.Line2D([], [], color="none", marker=SCENARIO_MARKERS["A3"], markersize=6.0, 
                                  markerfacecolor=OBSERVATION_COLORS["A3"], markeredgecolor=OBSERVATION_COLORS["A3"], 
                                  alpha=0.70, label="Observed A3")

    # Order handles so that Column-first legend maps to: Col 1 = Retrieved, Col 2 = True, Col 3 = Observed
    handles = [ret_a0_handle, ret_a3_handle, 
               true_a0_handle, true_a3_handle, 
               obs_a0_handle, obs_a3_handle]
    labels = [h.get_label() for h in handles]

    fig.legend(handles, labels, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 0.93), 
               frameon=True, facecolor="white", edgecolor="none", framealpha=0.8, fontsize=9)
    
    fig.suptitle("TRAPPIST-1e retrievals in selected ExoFarm molecular bands", fontsize=14, fontweight="bold", y=0.98)
    
    fig.tight_layout(rect=[0, 0, 1, 0.89])
    
    suffix = "_v2" if v2_style else ""
    png_path = PLOTS_DIR / f"trappist_retrieved_zooms_A0_A3{suffix}.png"
    pdf_path = PLOTS_DIR / f"trappist_retrieved_zooms_A0_A3{suffix}.pdf"
    try:
        fig.savefig(png_path, dpi=240, bbox_inches="tight")
        print(f"Saved: {png_path}")
    except Exception as e:
        print(f"Warning: could not save PNG to {png_path}: {e}")
    try:
        fig.savefig(pdf_path, bbox_inches="tight")
        print(f"Saved: {pdf_path}")
    except Exception as e:
        print(f"Warning: could not save PDF to {pdf_path}: {e}")
    plt.close(fig)


def generate_global_plot(transit_options, truth, data_cache, v2_style=False):
    # Setup global plot: 2 rows (5 and 100 transits), 1 column (entire 0.6-12.0 micron range)
    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    
    for r_idx, transits in enumerate(transit_options):
        ax = axes[r_idx]
        
        # Smooth target grid of 300 points for the global plot (both retrieved and true)
        target_wl = np.linspace(WL_MIN, WL_MAX, 300)

        # 1. Plot retrieved spectrum envelopes (1 and 2 sigma)
        for scenario in ("A0", "A3"):
            ret_raw = data_cache[transits][scenario]["retrieved_raw"]
            if ret_raw is None:
                continue
            color = RETRIEVED_COLORS[scenario]
            
            ret = resample_retrieved_spectrum(ret_raw, target_wl)
            
            # 2-sigma envelope (alpha=0.18)
            ax.fill_between(
                ret["wl"],
                ret["minus_2"],
                ret["plus_2"],
                color=color,
                alpha=0.18,
                lw=0,
                zorder=11,
            )
            # 1-sigma envelope (alpha=0.32)
            ax.fill_between(
                ret["wl"],
                ret["minus_1"],
                ret["plus_1"],
                color=color,
                alpha=0.32,
                lw=0,
                zorder=12,
            )
            # Median retrieved fit (linewidth=2.0, alpha=0.90, zorder=20)
            ax.plot(
                ret["wl"],
                ret["median"],
                color=color,
                linewidth=2.0,
                alpha=0.90,
                zorder=20,
                label=f"Retrieved {scenario}" if r_idx == 0 else "_nolegend_",
            )

        # 2. Plot synthetic observations (points with error bars) at noisy values (alpha=0.35, markersize=1.8, no caps) - zorder=40 (front)
        for scenario in ("A0", "A3"):
            color = OBSERVATION_COLORS[scenario]
            obs_list = data_cache[transits][scenario]["observations"]
            for obs in obs_list:
                ax.errorbar(
                    obs["wl"],
                    obs["depth"],
                    yerr=obs["depth_err"],
                    fmt=SCENARIO_MARKERS[scenario],
                    markersize=1.8,
                    color=color,
                    ecolor=color,
                    alpha=0.35,
                    elinewidth=0.4,
                    capsize=0,
                    linestyle="none",
                    zorder=40,
                    label=f"Obs {scenario}" if r_idx == 0 else "_nolegend_",
                )

        # 3. Plot true spectra - thin line (zorder=30, front of retrieved, behind obs)
        for scenario in ("A0", "A3"):
            color = TRUE_COLORS[scenario]
            true_y_smooth = np.interp(target_wl, truth[scenario]["wl"], truth[scenario]["depth"])
            linestyle = "-" if v2_style else ":"
            linewidth = 1.0 if v2_style else 1.4
            
            ax.plot(
                target_wl,
                true_y_smooth,
                color=color,
                linestyle=linestyle,
                linewidth=linewidth,
                alpha=0.70,
                label=f"True {scenario}" if r_idx == 0 else "_nolegend_",
                zorder=30,
            )

        # Restrict y-limits based on true spectra to avoid stretching from noisy observations (floor at 5120 as requested)
        y_max = max(np.max(truth["A0"]["depth"]), np.max(truth["A3"]["depth"]))
        y_pad = max(15.0, 0.08 * (y_max - 5180))
        ax.set_ylim(5120, y_max + y_pad)

        # Grid and styling
        ax.set_xscale("log")
        ax.set_xlim(WL_MIN, WL_MAX)
        ax.set_xticks([0.6, 0.8, 1, 2, 3, 5, 8, 10, 12])
        ax.set_xticklabels(["0.6", "0.8", "1", "2", "3", "5", "8", "10", "12"])
        ax.grid(alpha=0.12, which="both", linestyle="--")
        
        ax.set_ylabel(r"Transit Depth $(R_p/R_s)^2$ (ppm)", fontsize=10)
        
        # Add row indicators on the right side of the figure
        ax.text(
            1.02, 0.5, f"{transits} Transits",
            transform=ax.transAxes,
            fontsize=12,
            fontweight="bold",
            va="center",
            ha="left",
            rotation=-90
        )

    import matplotlib.lines as mlines
    # Custom legend handles arranged in columns (for column-first legend layout)
    ret_a0_handle = mlines.Line2D([], [], color=RETRIEVED_COLORS["A0"], lw=2.5, label="Retrieved A0")
    ret_a3_handle = mlines.Line2D([], [], color=RETRIEVED_COLORS["A3"], lw=2.5, label="Retrieved A3")

    true_linestyle = "-" if v2_style else ":"
    true_linewidth = 1.2 if v2_style else 1.6
    true_a0_handle = mlines.Line2D([], [], color=TRUE_COLORS["A0"], linestyle=true_linestyle, lw=true_linewidth, alpha=0.70, label="True A0")
    true_a3_handle = mlines.Line2D([], [], color=TRUE_COLORS["A3"], linestyle=true_linestyle, lw=true_linewidth, alpha=0.70, label="True A3")

    obs_a0_handle = mlines.Line2D([], [], color="none", marker=SCENARIO_MARKERS["A0"], markersize=5.5, 
                                  markerfacecolor=OBSERVATION_COLORS["A0"], markeredgecolor=OBSERVATION_COLORS["A0"], 
                                  alpha=0.70, label="Observed A0")
    obs_a3_handle = mlines.Line2D([], [], color="none", marker=SCENARIO_MARKERS["A3"], markersize=5.5, 
                                  markerfacecolor=OBSERVATION_COLORS["A3"], markeredgecolor=OBSERVATION_COLORS["A3"], 
                                  alpha=0.70, label="Observed A3")

    # Order handles so that Column-first legend maps to: Col 1 = Retrieved, Col 2 = True, Col 3 = Observed
    handles = [ret_a0_handle, ret_a3_handle, 
               true_a0_handle, true_a3_handle, 
               obs_a0_handle, obs_a3_handle]
    labels = [h.get_label() for h in handles]

    fig.legend(handles, labels, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 0.93), 
               frameon=True, facecolor="white", edgecolor="none", framealpha=0.8, fontsize=9)
    
    fig.suptitle("TRAPPIST-1e ExoFarm Retrieval Performance", fontsize=14, fontweight="bold", y=0.98)
    
    fig.tight_layout(rect=[0, 0, 1, 0.89])
    
    suffix = "_v2" if v2_style else ""
    png_path = PLOTS_DIR / f"trappist_retrieved_global_A0_A3{suffix}.png"
    pdf_path = PLOTS_DIR / f"trappist_retrieved_global_A0_A3{suffix}.pdf"
    try:
        fig.savefig(png_path, dpi=240, bbox_inches="tight")
        print(f"Saved: {png_path}")
    except Exception as e:
        print(f"Warning: could not save PNG to {png_path}: {e}")
    try:
        fig.savefig(pdf_path, bbox_inches="tight")
        print(f"Saved: {pdf_path}")
    except Exception as e:
        print(f"Warning: could not save PDF to {pdf_path}: {e}")
    plt.close(fig)


def main():
    # Load true spectra
    print("Computing true spectra...")
    wl_grid, spectra = compute_system_spectra("TRAPPIST-1e", WL_MIN, WL_MAX, native_r=10000.0)
    truth = {
        "A0": {"wl": wl_grid, "depth": spectra["A0"] * 1.0e6},
        "A3": {"wl": wl_grid, "depth": spectra["A3"] * 1.0e6},
    }

    transit_options = [5, 100]
    
    # Store y-values to compute custom y-limits for each column (zooms)
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

    # Generate the two plots
    # 1. Original version (dotted True curves)
    generate_zoomed_plot(transit_options, truth, data_cache, column_y_values, v2_style=False)
    generate_global_plot(transit_options, truth, data_cache, v2_style=False)

    # 2. v2 version (thin solid True curves)
    generate_zoomed_plot(transit_options, truth, data_cache, column_y_values, v2_style=True)
    generate_global_plot(transit_options, truth, data_cache, v2_style=True)

if __name__ == "__main__":
    main()
