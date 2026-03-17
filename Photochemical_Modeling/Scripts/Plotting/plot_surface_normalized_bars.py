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
plt.rcParams['lines.linewidth'] = 2.0

scenarios = ['A0', 'A1', 'A2', 'A3']
scenario_labels = ['Pre-Agri', 'Present', 'ExoFarm (Mod)', 'ExoFarm (Ext)']
stars = ['Sun', 'Trappist']
star_labels = {'Sun': 'Sun (G2V)', 'Trappist': 'TRAPPIST-1 (M8V)'}
colors = {'Sun': '#E69F00', 'Trappist': '#56B4E9'} # Orange vs Sky Blue

# Molecules to analyze (Matching the table in the report)
molecules = ['N2O', 'NH3', 'O3', 'CH4']
mol_colors = {
    'N2O': '#0072B2',
    'NH3': '#009E73',
    'O3':  '#CC79A7',
    'CH4': '#D55E00'
}

def get_surface_mixing_ratio(filepath, species):
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        if species not in data['variable']['species']:
            return None
        
        sp_idx = data['variable']['species'].index(species)
        # Find surface index (max pressure)
        pco = data['atm']['pco']
        surf_idx = np.argmax(pco)
        
        ymix = data['variable']['ymix'][surf_idx, sp_idx]
        return ymix
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

# 1. Gather Data
raw_data = {star: {mol: [] for mol in molecules} for star in stars}

# We need the baseline (Sun A1) for normalization
baselines = {}

for star in stars:
    prefix = "Earth" if star == "Sun" else "Trappist"
    suffix_map = {
        'A0': '_A0_PreAgri.vul',
        'A1': '_A1_Current.vul',
        'A2': '_A2_Moderate.vul',
        'A3': '_A3_Extreme.vul'
    }
    
    for sc in scenarios:
        filename = prefix + suffix_map[sc]
        filepath = os.path.join(output_dir, filename)
        
        for mol in molecules:
            val = get_surface_mixing_ratio(filepath, mol)
            raw_data[star][mol].append(val)
            
            # Capture baseline if this is Sun A1
            if star == 'Sun' and sc == 'A1':
                baselines[mol] = val

# 2. Plotting
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()

fig.suptitle("Surface Abundance Normalized to Current Earth (Sun-A1)", fontsize=16, y=0.96)

bar_width = 0.35
x = np.arange(len(scenarios))

for i, mol in enumerate(molecules):
    ax = axes[i]
    baseline = baselines.get(mol)
    
    if baseline is None or baseline == 0:
        ax.text(0.5, 0.5, "Baseline data missing", ha='center')
        continue

    # Prepare normalized values
    y_sun = []
    y_trap = []
    
    for val in raw_data['Sun'][mol]:
        y_sun.append(val / baseline if val is not None else 0)
        
    for val in raw_data['Trappist'][mol]:
        y_trap.append(val / baseline if val is not None else 0)
        
    # Plot Bars
    rects1 = ax.bar(x - bar_width/2, y_sun, bar_width, label='Sun (G2V)', color=colors['Sun'], alpha=0.9)
    rects2 = ax.bar(x + bar_width/2, y_trap, bar_width, label='TRAPPIST-1e (M8V)', color=colors['Trappist'], alpha=0.9)
    
    # Styling
    ax.set_title(f"{mol}", fontsize=14, fontweight='bold', color=mol_colors[mol])
    ax.set_xticks(x)
    ax.set_xticklabels(scenario_labels, fontsize=10)
    ax.set_yscale('log')
    
    # Reference Line at 1.0 (Earth Current)
    ax.axhline(1.0, color='gray', linestyle='--', linewidth=1.5, alpha=0.7)
    ax.text(3.6, 1.0, 'Earth A1', va='center', fontsize=9, color='gray')

    # Add grid
    ax.grid(True, which='major', axis='y', alpha=0.4)
    
    # Add value labels for all bars
    def add_labels(rects):
        for rect in rects:
            height = rect.get_height()
            if height <= 0: continue
            
            # Smart formatting
            if height >= 100:
                label = f'{height:.0f}x'
            elif height >= 10:
                label = f'{height:.1f}x'
            elif height >= 0.1:
                label = f'{height:.2f}x'
            else:
                label = f'{height:.2g}x'

            ax.annotate(label,
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=7, fontweight='bold')

    add_labels(rects1)
    add_labels(rects2)

    if i % 2 == 0:
        ax.set_ylabel('Normalized Ratio (vs Earth A1)', fontsize=11)

# Common Legend
handles = [
    plt.Rectangle((0,0),1,1, color=colors['Sun']),
    plt.Rectangle((0,0),1,1, color=colors['Trappist']),
    Line2D([0], [0], color='gray', linestyle='--', linewidth=1.5)
]
labels = ['Sun (G2V)', 'TRAPPIST-1e (M8V)', 'Baseline (Current Earth)']
fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.92), ncol=3, fontsize=11)

plt.tight_layout(rect=[0, 0, 1, 0.88])
output_file = os.path.join(plot_dir, 'surface_normalization_bars.png')
plt.savefig(output_file, dpi=300)
print(f"Saved normalized bar plot to {output_file}")
