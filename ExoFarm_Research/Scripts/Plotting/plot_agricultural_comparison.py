import matplotlib.pyplot as plt
import pickle
import numpy as np
import os

# Scenarios
scenarios = [
    {'file': '../../Results/Outputs/Earth_A0_PreAgri.vul', 'label': 'Pre-Agricultural', 'color': 'green'},
    {'file': '../../Results/Outputs/Earth_A1_Current.vul', 'label': 'Current Earth-like', 'color': 'blue'},
    {'file': '../../Results/Outputs/Earth_A2_Moderate.vul', 'label': 'ExoFarm Moderate (10x)', 'color': 'orange'},
    {'file': '../../Results/Outputs/Earth_A3_Extreme.vul', 'label': 'ExoFarm Extreme (100x)', 'color': 'red'}
]

# Species to plot
species_to_plot = ['N2O', 'NH3', 'O3', 'CH4']

# Output directory
plot_dir = '../../Results/Plots/'
if not os.path.exists(plot_dir):
    os.makedirs(plot_dir)

# Create figure
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()

fig.suptitle("Sun-like Star (G2V)", fontsize=16)

for i, sp in enumerate(species_to_plot):
    ax = axes[i]
    ax.set_title(sp)
    
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
    ax.set_ylim(1.2, 1e-8) # Surface at bottom
    ax.set_xlim(1e-12, 1e-1)
    ax.grid(True, which="both", ls="-", alpha=0.2)
    ax.set_ylabel('Pressure (bar)')
    ax.set_xlabel('Mixing Ratio')
    
    if i == 0:
        ax.legend(loc='best', fontsize='small')

plt.tight_layout(rect=[0, 0, 1, 0.95])
output_file = os.path.join(plot_dir, 'agricultural_comparison.png')
plt.savefig(output_file, dpi=300)
print(f"Saved plot to {output_file}")
