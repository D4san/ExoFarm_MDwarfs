import matplotlib.pyplot as plt
import numpy as np
import pickle
import os
from matplotlib.lines import Line2D

# Configuration
output_dir = '../../Results/Outputs/'
plot_dir = '../../Results/Plots/'
if not os.path.exists(plot_dir):
    os.makedirs(plot_dir)

# Global Aesthetics
plt.rcParams.update({'font.size': 12})
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3
plt.rcParams['grid.color'] = '#cccccc'
plt.rcParams['lines.linewidth'] = 2.5

scenarios = ['A0', 'A1', 'A2', 'A3']
scenario_labels = ['Pre-Agri', 'Present', 'ExoFarm (Mod)', 'ExoFarm (Ext)']
stars = ['Sun', 'Trappist']
star_labels = {'Sun': 'Sun (G2V)', 'Trappist': 'TRAPPIST-1 (M8V)'}

# Colorblind-friendly palette (Okabe-Ito inspired)
# Sun: Orange, Trappist: Sky Blue
colors = {'Sun': '#E69F00', 'Trappist': '#56B4E9'}
linestyles = {'Sun': '-', 'Trappist': '--'}

# Molecules list and colors
molecules = ['OH']
# Molecules: distinct colors
mol_colors = {
    'OH':  '#000000'   # Black (Distinct for radical)
}

def load_vulcan_output(filepath):
    if not os.path.exists(filepath):
        print(f"Warning: File not found: {filepath}")
        return None
    try:
        with open(filepath, 'rb') as handle:
            data = pickle.load(handle)
        return data
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

# --- Plot: Profiles Comparison (4 Subplots) ---
fig, axes = plt.subplots(2, 2, figsize=(16, 12), sharex=True, sharey=True)
axes = axes.flatten()

fig.suptitle("Vertical Profiles Comparison (including OH): Earth-Sun vs. TRAPPIST-1e", fontsize=18, y=0.95)

for i, scenario in enumerate(scenarios):
    ax = axes[i]
    ax.set_title(f"{scenario_labels[i]} ({scenario})", fontsize=14, fontweight='bold')
    ax.set_yscale('log')
    ax.set_xscale('log')
    ax.set_xlim(1e-12, 1e-1)
    # Fixed pressure range: Surface (~1.2 bar) to Top (~1e-8 bar)
    ax.set_ylim(1.2, 1e-8) 
    
    if i % 2 == 0:
        ax.set_ylabel('Pressure (bar)', fontsize=12)
    if i >= 2:
        ax.set_xlabel('Mixing Ratio', fontsize=12)
    
    # Enhanced Grid
    ax.grid(which='major', alpha=0.5, linewidth=0.8)
    ax.grid(which='minor', alpha=0.2, linestyle=':', linewidth=0.5)

    for star in stars:
        prefix = "Earth" if star == "Sun" else "Trappist"
        suffix_map = {
            'A0': '_A0_PreAgri.vul',
            'A1': '_A1_Current.vul',
            'A2': '_A2_Moderate.vul',
            'A3': '_A3_Extreme.vul'
        }
        filename = prefix + suffix_map[scenario]
        filepath = os.path.join(output_dir, filename)
        
        data = load_vulcan_output(filepath)
        if data is None:
            continue
            
        pressure = data['atm']['pco'] / 1e6 # dyne/cm2 to bar
        
        for mol in molecules:
            if mol in data['variable']['species']:
                idx = data['variable']['species'].index(mol)
                mix_ratio = data['variable']['ymix'][:, idx]
                
                ax.plot(mix_ratio, pressure, 
                        color=mol_colors[mol], 
                        linestyle=linestyles[star], 
                        linewidth=2.5, 
                        alpha=0.8)

# Custom Legend for Profiles
custom_lines = []
custom_labels = []

# Stars header
custom_lines.append(Line2D([0], [0], color='white', alpha=0))
custom_labels.append(r"$\bf{Star\ Type}$")
for star in stars:
    custom_lines.append(Line2D([0], [0], color='gray', linestyle=linestyles[star], linewidth=2.5))
    custom_labels.append(star_labels[star])

# Spacer
custom_lines.append(Line2D([0], [0], color='white', alpha=0))
custom_labels.append("")

# Molecules header
custom_lines.append(Line2D([0], [0], color='white', alpha=0))
custom_labels.append(r"$\bf{Molecule}$")
for mol in molecules:
    custom_lines.append(Line2D([0], [0], color=mol_colors[mol], linewidth=3))
    custom_labels.append(mol)

fig.legend(custom_lines, custom_labels, loc='center right', bbox_to_anchor=(0.98, 0.5), 
           fontsize=12, frameon=True, fancybox=True, shadow=True, borderpad=1)

plt.tight_layout(rect=[0, 0, 0.85, 0.95]) # Make room for legend on the right
plt.savefig(os.path.join(plot_dir, 'star_comparison_profiles_OH.png'), dpi=300)
print("Saved profile comparison plot with OH.")

def calc_pressure_weighted_mean(data, species):
    if species not in data['variable']['species']:
        return None
    idx = data['variable']['species'].index(species)
    ymix = data['variable']['ymix'][:, idx]
    pco = data['atm']['pco']
    return np.average(ymix, weights=pco)

# --- Plot 2: Trends (Scatter - 1 Subplot) ---
# 1 molecule -> 1 subplot
fig2, ax = plt.subplots(figsize=(10, 8))
fig2.suptitle("Abundance Trends (OH): Agriculture Intensity vs Star Type", fontsize=18, y=0.98)

# Prepare data
trends = {star: {mol: [] for mol in molecules} for star in stars}

for i, scenario in enumerate(scenarios):
    for star in stars:
        prefix = "Earth" if star == "Sun" else "Trappist"
        suffix_map = {
            'A0': '_A0_PreAgri.vul',
            'A1': '_A1_Current.vul',
            'A2': '_A2_Moderate.vul',
            'A3': '_A3_Extreme.vul'
        }
        filename = prefix + suffix_map[scenario]
        filepath = os.path.join(output_dir, filename)
        data = load_vulcan_output(filepath)
        
        for mol in molecules:
            val = np.nan
            if data is not None:
                 val = calc_pressure_weighted_mean(data, mol)
            trends[star][mol].append(val)

x_indices = np.arange(len(scenarios))

# Plot for each molecule (Only OH)
mol = 'OH'
ax.set_title(f"{mol}", fontsize=14, fontweight='bold', color=mol_colors[mol])
ax.set_yscale('log')
ax.set_xticks(x_indices)
ax.set_xticklabels(scenario_labels, fontsize=10, rotation=15)
ax.grid(True, alpha=0.3)
ax.set_ylabel('Mean Mixing Ratio', fontsize=12)
    
for star in stars:
    y_vals = trends[star][mol]
    
    # Plot line + markers
    ax.plot(x_indices, y_vals, 
            color=colors[star] if star in colors else ('#E69F00' if star == 'Sun' else '#56B4E9'), 
            linestyle=linestyles[star], 
            marker='o' if star == 'Sun' else '^',
            markersize=9,
            linewidth=2.5,
            alpha=0.8)

# Add Earth reference lines (Scenario A1 for Sun)
ref_val = trends['Sun'][mol][1]
if not np.isnan(ref_val):
    ax.axhline(ref_val, color='gray', linestyle=':', alpha=0.6, linewidth=2)

# Custom Legend for Trends
trend_lines = []
trend_labels = []
colors_map = {'Sun': '#E69F00', 'Trappist': '#56B4E9'}
markers_map = {'Sun': 'o', 'Trappist': '^'}

for star in stars:
    trend_lines.append(Line2D([0], [0], color=colors_map[star], marker=markers_map[star], linestyle=linestyles[star], markersize=9, linewidth=2.5))
    trend_labels.append(star_labels[star])

trend_lines.append(Line2D([0], [0], color='gray', linestyle=':', linewidth=2))
trend_labels.append("Current Earth Level")

fig2.legend(trend_lines, trend_labels, loc='upper center', bbox_to_anchor=(0.5, 0.93), ncol=3, fontsize=12, frameon=True)

plt.tight_layout(rect=[0, 0, 1, 0.90]) # Adjust for suptitle and legend
plt.savefig(os.path.join(plot_dir, 'star_comparison_trends_OH.png'), dpi=300)
print("Saved trends plot with OH.")
