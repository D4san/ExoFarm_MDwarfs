import sys
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd

# Import project plot style
sys.path.append(str(Path(__file__).resolve().parent))
from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE


def main():
    # Output and Input paths
    BASE_DIR = Path(__file__).resolve().parent
    CSV_PATH = BASE_DIR / "POSEIDON_output" / "pure_spectra" / "plots" / "trappist1e_net_molecular_peak_summary.csv"
    OUTPUT_DIR = BASE_DIR.parent / "final_products" / "figures"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load data
    if not CSV_PATH.exists():
        print(f"Error: CSV file not found at {CSV_PATH}")
        sys.exit(1)

    df = pd.read_csv(CSV_PATH)

    # Filter for N2O and NH3 only
    df = df[df["molecule"].isin(["N2O", "NH3"])].copy()

    # Filter out all NH3 peaks except 10.7 um (NH3_10p0_11p2)
    df = df[df["band_id"].isin(["N2O_2p6_3p0", "N2O_4p3_4p8", "N2O_7p5_9p0", "NH3_10p0_11p2"])].copy()

    # Define band display names and order
    band_mapping = {
        "N2O_2p6_3p0": {"label": r"2.8 $\mu$m" + "\n" + r"($\mathrm{N}_2\mathrm{O}$)", "order": 0},
        "N2O_4p3_4p8": {"label": r"4.5 $\mu$m" + "\n" + r"($\mathrm{N}_2\mathrm{O}$)", "order": 1},
        "N2O_7p5_9p0": {"label": r"8.6 $\mu$m" + "\n" + r"($\mathrm{N}_2\mathrm{O}$)", "order": 2},
        "NH3_10p0_11p2": {"label": r"10.7 $\mu$m" + "\n" + r"($\mathrm{NH}_3$)", "order": 3},
    }

    df["band_order"] = df["band_id"].map(lambda x: band_mapping[x]["order"])
    df = df.sort_values("band_order")

    # Set up matplotlib style (STIX serif style for publication)
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["STIX Two Text", "STIXGeneral", "Times New Roman"],
        "mathtext.fontset": "stix",
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "figure.titlesize": 13,
    })

    # Create 2-panel figure (stacked vertically: 2 rows, 1 column)
    # The second panel is made shorter (height ratio 0.7)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.5, 9.5), dpi=300, gridspec_kw={'height_ratios': [1.0, 0.7]})

    # ------------------ PANEL 1: CATEGORICAL COMPARISON ------------------
    # Scenario offsets, markers, and labels (without colons)
    scenarios = {
        "A1": {"offset": -0.20, "marker": "o", "label": "A1 Current Earth", "size": 130},
        "A2": {"offset": 0.00, "marker": "s", "label": "A2 Moderate ExoFarm", "size": 120},
        "A3": {"offset": 0.20, "marker": "^", "label": "A3 Extreme ExoFarm", "size": 140},
    }

    # Transit counts and colors (azul, verde, morado)
    transit_styles = {
        1: {"color": PALETTE["scenario_cyan"], "label": "1 transit"},
        10: {"color": PALETTE["scenario_green"], "label": "10 transits"},
        100: {"color": PALETTE["scenario_violet"], "label": "100 transits"},
    }

    transit_cases = [
        {"suffix": "1transit", "val": 1},
        {"suffix": "10transit", "val": 10},
        {"suffix": "100transit", "val": 100},
    ]

    # Plot data points
    for scen_name, scen_style in scenarios.items():
        scen_df = df[df["scenario"] == scen_name]
        
        for case in transit_cases:
            x_positions = []
            y_positions = []
            
            for _, row in scen_df.iterrows():
                x_base = band_mapping[row["band_id"]]["order"]
                x_pos = x_base + scen_style["offset"]
                snr_val = row[f"snr_{case['suffix']}"]
                
                x_positions.append(x_pos)
                y_positions.append(snr_val)
                
            ax1.scatter(
                x_positions,
                y_positions,
                color=transit_styles[case["val"]]["color"],
                marker=scen_style["marker"],
                s=scen_style["size"],
                edgecolors="#222222",
                linewidths=0.8,
                zorder=3,
                alpha=0.95
            )

    # Customize ax1 (Y-axis Peak molecular-excess S/N)
    ax1.set_yscale("log")
    ax1.set_ylim(0.0001, 2.0)
    ax1.set_ylabel("Peak molecular-excess S/N", labelpad=8)

    # X-ticks and labels
    tick_positions = [band_mapping[b]["order"] for b in band_mapping]
    tick_labels = [band_mapping[b]["label"] for b in band_mapping]
    ax1.set_xticks(tick_positions)
    ax1.set_xticklabels(tick_labels)
    ax1.set_xlabel("Spectral feature", labelpad=10)
    ax1.set_xlim(-0.6, 3.6)

    # Grid lines
    ax1.grid(True, which="both", axis="both", linestyle=":", color="#dddddd", alpha=0.7, zorder=1)

    # Add vertical lines between the N2O and NH3 sections to separate them visually
    ax1.axvline(2.5, color="#888888", linestyle="--", linewidth=1.2, alpha=0.5, zorder=2)

    # Label molecular regions
    ax1.text(
        1.0, 1.2, r"$\mathrm{N}_2\mathrm{O}$ bands",
        color="#444444", fontsize=10, fontstyle="italic", ha="center", weight="semibold"
    )
    ax1.text(
        3.0, 1.2, r"$\mathrm{NH}_3$ band",
        color="#444444", fontsize=10, fontstyle="italic", ha="center", weight="semibold"
    )

    # Custom legend for scenarios (markers)
    legend_elements_scenarios = [
        plt.Line2D(
            [0], [0],
            marker=scenarios["A1"]["marker"],
            color="w",
            label=scenarios["A1"]["label"],
            markerfacecolor="#888888",
            markeredgecolor="#222222",
            markersize=10,
            linestyle="None"
        ),
        plt.Line2D(
            [0], [0],
            marker=scenarios["A2"]["marker"],
            color="w",
            label=scenarios["A2"]["label"],
            markerfacecolor="#888888",
            markeredgecolor="#222222",
            markersize=10,
            linestyle="None"
        ),
        plt.Line2D(
            [0], [0],
            marker=scenarios["A3"]["marker"],
            color="w",
            label=scenarios["A3"]["label"],
            markerfacecolor="#888888",
            markeredgecolor="#222222",
            markersize=10,
            linestyle="None"
        ),
    ]

    # Custom legend for transits (colors)
    legend_elements_transits = [
        plt.Line2D(
            [0], [0],
            marker="o",
            color="w",
            label=transit_styles[1]["label"],
            markerfacecolor=transit_styles[1]["color"],
            markeredgecolor="#222222",
            markersize=10,
            linestyle="None"
        ),
        plt.Line2D(
            [0], [0],
            marker="o",
            color="w",
            label=transit_styles[10]["label"],
            markerfacecolor=transit_styles[10]["color"],
            markeredgecolor="#222222",
            markersize=10,
            linestyle="None"
        ),
        plt.Line2D(
            [0], [0],
            marker="o",
            color="w",
            label=transit_styles[100]["label"],
            markerfacecolor=transit_styles[100]["color"],
            markeredgecolor="#222222",
            markersize=10,
            linestyle="None"
        ),
    ]

    leg1 = ax1.legend(
        handles=legend_elements_scenarios,
        loc="lower left",
        bbox_to_anchor=(0.02, 0.05),
        title="Scenario",
        frameon=True,
        facecolor="#ffffff",
        edgecolor="#dddddd",
        framealpha=0.9,
        fontsize=9
    )
    leg1.get_frame().set_boxstyle("round,pad=0.3")
    leg1.get_title().set_weight("bold")
    leg1.get_title().set_fontsize(9)
    ax1.add_artist(leg1)

    leg2 = ax1.legend(
        handles=legend_elements_transits,
        loc="lower left",
        bbox_to_anchor=(0.38, 0.05),
        title="Number of transits",
        frameon=True,
        facecolor="#ffffff",
        edgecolor="#dddddd",
        framealpha=0.9,
        fontsize=9
    )
    leg2.get_frame().set_boxstyle("round,pad=0.3")
    leg2.get_title().set_weight("bold")
    leg2.get_title().set_fontsize(9)

    ax1.set_title("(a) Peak molecular S/N relative to the pre-agricultural baseline", fontsize=12, pad=12, fontweight="bold")

    # ------------------ PANEL 2: S/N PROJECTION ------------------
    # Retrieve the A3 peak values for N2O (2.8 um) and NH3 (10.7 um)
    a3_df = df[df["scenario"] == "A3"]
    
    n2o_a3_row = a3_df[a3_df["band_id"] == "N2O_2p6_3p0"].iloc[0]
    nh3_a3_row = a3_df[a3_df["band_id"] == "NH3_10p0_11p2"].iloc[0]
    
    snr1_n2o = n2o_a3_row["snr_1transit"]
    snr1_nh3 = nh3_a3_row["snr_1transit"]
    
    # Transit range for projection lines: 1 to 1,000,000
    n_transits_grid = np.logspace(0, 6.0, 500)
    
    # Compute projection curves: S/N = S/N_1 * sqrt(N)
    snr_n2o_proj = snr1_n2o * np.sqrt(n_transits_grid)
    snr_nh3_proj = snr1_nh3 * np.sqrt(n_transits_grid)
    
    # Secondary colors from palette:
    # terracotta_mauve = #8E5651 (used for N2O)
    # charcoal_violet  = #5B4763 (used for NH3)
    c_n2o = PALETTE["terracotta_mauve"]
    c_nh3 = PALETTE["charcoal_violet"]
    
    # Filter projection to only show S/N up to 5.8
    mask_n2o = snr_n2o_proj <= 5.8
    mask_nh3 = snr_nh3_proj <= 5.8
    
    # Plot projection lines
    ax2.plot(n_transits_grid[mask_n2o], snr_n2o_proj[mask_n2o], color=c_n2o, lw=2.2, label=r"$\mathrm{N}_2\mathrm{O}$ 2.8 $\mu$m", zorder=3)
    ax2.plot(n_transits_grid[mask_nh3], snr_nh3_proj[mask_nh3], color=c_nh3, lw=2.2, label=r"$\mathrm{NH}_3$ 10.7 $\mu$m", zorder=3)
    
    # Add horizontal threshold lines at S/N = 3 and S/N = 5 (using scenario_pink from palette)
    color_sigmas = PALETTE["scenario_pink"]
    ax2.axhline(3.0, color=color_sigmas, linestyle="--", lw=1.0, alpha=0.8, zorder=2)
    ax2.axhline(5.0, color=color_sigmas, linestyle="-.", lw=1.0, alpha=0.8, zorder=2)
    ax2.text(1.5, 3.15, r"S/N = 3", color=color_sigmas, fontsize=9, fontweight="semibold")
    ax2.text(1.5, 5.15, r"S/N = 5", color=color_sigmas, fontsize=9, fontweight="semibold")
    
    # Calculate exact intersections
    n_3sigma_n2o = (3.0 / snr1_n2o) ** 2
    n_5sigma_n2o = (5.0 / snr1_n2o) ** 2
    n_3sigma_nh3 = (3.0 / snr1_nh3) ** 2
    n_5sigma_nh3 = (5.0 / snr1_nh3) ** 2
    
    # Plot intersection markers and labels
    intersections = [
        {"x": n_3sigma_n2o, "y": 3.0, "color": c_n2o, "text": f"{int(round(n_3sigma_n2o)):,}"},
        {"x": n_5sigma_n2o, "y": 5.0, "color": c_n2o, "text": f"{int(round(n_5sigma_n2o)):,}"},
        {"x": n_3sigma_nh3, "y": 3.0, "color": c_nh3, "text": f"{int(round(n_3sigma_nh3)):,}"},
        {"x": n_5sigma_nh3, "y": 5.0, "color": c_nh3, "text": f"{int(round(n_5sigma_nh3)):,}"},
    ]
    
    for inter in intersections:
        ax2.scatter(inter["x"], inter["y"], color=inter["color"], edgecolor="black", marker="D", s=70, zorder=5)
        # Adjust text offset depending on species to prevent overlap
        offset_y = 0.35 if inter["color"] == c_n2o else -0.45
        ax2.text(
            inter["x"], inter["y"] + offset_y, inter["text"],
            color=inter["color"], fontsize=8, ha="center", weight="bold",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#ffffff", edgecolor=inter["color"], alpha=0.9, lw=0.5)
        )
        
    # Plot actual data points for visual anchor (scenario A3, transits 1, 10, 100)
    # The baseline dots are colored to match the species line colors and use diamond markers
    for val in [1, 10, 100]:
        case_suffix = f"{val}transit"
        # N2O point
        n2o_val = n2o_a3_row[f"snr_{case_suffix}"]
        ax2.scatter(
            val, n2o_val,
            color=c_n2o,
            marker="D", s=100, edgecolors="#222222", linewidths=0.8, zorder=4
        )
        # NH3 point
        nh3_val = nh3_a3_row[f"snr_{case_suffix}"]
        ax2.scatter(
            val, nh3_val,
            color=c_nh3,
            marker="D", s=100, edgecolors="#222222", linewidths=0.8, zorder=4
        )
        
    # Customize axis (log X, linear Y from 0 to 5.8)
    ax2.set_xscale("log")
    ax2.set_xlim(1.0, 1000000.0)
    ax2.set_ylim(0.0, 5.8)
    ax2.set_xlabel("Number of transits", labelpad=10)
    ax2.set_ylabel("Peak molecular-excess S/N", labelpad=8)
    ax2.grid(True, which="both", axis="both", linestyle=":", color="#dddddd", alpha=0.7, zorder=1)
    
    # Legend for species (positioned at lower right as requested, no second legend needed)
    leg_proj = ax2.legend(
        loc="lower right",
        title="A3 molecular feature",
        frameon=True,
        facecolor="#ffffff",
        edgecolor="#dddddd",
        framealpha=0.9,
        fontsize=9
    )
    leg_proj.get_frame().set_boxstyle("round,pad=0.3")
    leg_proj.get_title().set_weight("bold")
    leg_proj.get_title().set_fontsize(9)
    
    ax2.set_title("(b) Transits required to reach fixed S/N thresholds in A3", fontsize=12, pad=12, fontweight="bold")
    
    plt.tight_layout()

    # Save figure
    for ext in ["png", "pdf"]:
        save_path = OUTPUT_DIR / f"trappist1e_net_molecular_snr_comparison.{ext}"
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Saved: {save_path}")


if __name__ == "__main__":
    main()
