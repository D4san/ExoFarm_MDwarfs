import matplotlib.pyplot as plt
import pickle
import numpy as np
import os

# Scenarios
scenarios = [
    {'file': '../../Results/Outputs/Trappist_A0_PreAgri.vul', 'label': 'Pre-Agricultural', 'color': 'green'},
    {'file': '../../Results/Outputs/Trappist_A1_Current.vul', 'label': 'Current Earth-like', 'color': 'blue'},
    {'file': '../../Results/Outputs/Trappist_A2_Moderate.vul', 'label': 'ExoFarm Moderate (10x)', 'color': 'orange'},
    {'file': '../../Results/Outputs/Trappist_A3_Extreme.vul', 'label': 'ExoFarm Extreme (100x)', 'color': 'red'}
]

# Species to plot
species_to_plot = ['N2O', 'NH3', 'O3', 'CH4']

# Create figure
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()

fig.suptitle("TRAPPIST-1e System (M8V)", fontsize=16)

for i, sp in enumerate(species_to_plot):
    ax = axes[i]
    
    for sc in scenarios:
        filename = sc['file']
        if not os.path.exists(filename):
            print(f"Warning: {filename} not found.")
            continue
        
        try:
            with open(filename, 'rb') as f:
                data = pickle.load(f)
        
            # Extract data
            species_list = data['variable']['species']
            if sp not in species_list:
                print(f"Warning: {sp} not found in {filename}")
                continue
        
            sp_idx = species_list.index(sp)
            ymix = data['variable']['ymix'][:, sp_idx]
            pco = data['atm']['pco'] / 1e6 # Convert dyne/cm2 to bar (1 bar = 1e6 dyne/cm2)
        
            ax.plot(ymix, pco, label=sc['label'], color=sc['color'], linewidth=2)
        
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    
    ax.set_yscale('log')
    ax.set_xscale('log')
    # ax.invert_yaxis()
    ax.set_ylim(1.2, 1e-8)
    ax.set_xlim(1e-12, 1e0)
    ax.set_title(sp)
    ax.set_ylabel('Pressure (bar)')
    ax.set_xlabel('Mixing Ratio')
    ax.grid(True, which="both", ls="-", alpha=0.3)
    if i == 0: # Legend only on first plot to avoid clutter
        ax.legend()

plt.tight_layout(rect=[0, 0, 1, 0.95])
output_plot = '../../Results/Plots/trappist_comparison.png'
if not os.path.exists('../../Results/Plots'):
    os.makedirs('../../Results/Plots')
plt.savefig(output_plot)
print(f"Plot saved to {output_plot}")