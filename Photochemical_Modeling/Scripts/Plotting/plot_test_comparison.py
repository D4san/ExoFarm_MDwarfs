import matplotlib.pyplot as plt
import numpy as np
import os
import pickle
from matplotlib.gridspec import GridSpec

# Paths to the output files
res_dir = "/mnt/c/Proyetos/Repos/ExoFarm_MDwarfs/Photochemical_Modeling/Results/Outputs"
prof_dir = "/mnt/c/Proyetos/Repos/ExoFarm_MDwarfs/Transmission_Spectroscopy/profiles"

files = {
    "A0_Baseline (1x CO2, Earth PT)": os.path.join(res_dir, "Trappist_A0_PreAgri.vul"),
    "A3_Baseline (1x CO2, Earth PT)": os.path.join(res_dir, "Trappist_A3_Extreme.vul"),
    "A0_LinPT (1x CO2)": os.path.join(res_dir, "Trappist_Test1_A0_LinPT.vul"),
    "A0_LinPT (100x CO2)": os.path.join(res_dir, "Trappist_Test2_A0_LinPT_100xCO2.vul"),
    "A3_LinPT (1x CO2)": os.path.join(res_dir, "Trappist_Test3_A3_LinPT.vul"),
    "A3_LinPT (100x CO2)": os.path.join(res_dir, "Trappist_Test4_A3_LinPT_100xCO2.vul")
}

def read_profile(filepath, species_name):
    if not os.path.exists(filepath):
        return None, None
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
    
    species_list = list(data["variable"]["species"])
    if species_name not in species_list:
        return None, None
    
    idx = species_list.index(species_name)
    pressure = np.asarray(data["atm"]["pco"]) # dyne/cm2
    mixing_ratio = np.asarray(data["variable"]["ymix"])[:, idx]
    return pressure, mixing_ratio

molecules = ["N2O", "NH3", "CH4", "O3", "CO2", "H2O"]

fig = plt.figure(figsize=(15, 10))
gs = GridSpec(2, 3, figure=fig)
axes = [fig.add_subplot(gs[i, j]) for i in range(2) for j in range(3)]

colors = {
    "A0_Baseline (1x CO2, Earth PT)": "#95E36B", # scenario_green
    "A3_Baseline (1x CO2, Earth PT)": "#E34F95", # scenario_pink
    "A0_LinPT (1x CO2)": "#56E3DB",              # scenario_cyan
    "A0_LinPT (100x CO2)": "#3F633E",            # deep_moss
    "A3_LinPT (1x CO2)": "#BD62E3",              # scenario_violet
    "A3_LinPT (100x CO2)": "#840032"             # dark_amaranth
}

linestyles = {
    "A0_Baseline (1x CO2, Earth PT)": "-",
    "A3_Baseline (1x CO2, Earth PT)": "-",
    "A0_LinPT (1x CO2)": "--",
    "A0_LinPT (100x CO2)": ":",
    "A3_LinPT (1x CO2)": "--",
    "A3_LinPT (100x CO2)": ":"
}

for i, mol in enumerate(molecules):
    ax = axes[i]
    for label, filepath in files.items():
        p, mix = read_profile(filepath, mol)
        if p is not None:
            p_bar = p / 1e6 # Convert dyne/cm2 to bar
            ax.plot(mix, p_bar, label=label, color=colors[label], linestyle=linestyles[label], linewidth=2)
            
    ax.set_yscale('log')
    ax.set_xscale('log')
    ax.invert_yaxis()
    ax.set_xlabel("Mixing Ratio")
    ax.set_ylabel("Pressure (bar)")
    ax.set_title(f"{mol} Mixing Ratio")
    ax.grid(True, which="both", ls="--", alpha=0.5)

# Put legend only on the first plot
axes[0].legend(loc='best', fontsize=7)

plt.tight_layout()
out_plot = "/mnt/c/Proyetos/Repos/ExoFarm_MDwarfs/Photochemical_Modeling/Results/Outputs/tests_chemical_profiles_6mol.png"
plt.savefig(out_plot, dpi=300)
print(f"Plot saved to {out_plot}")
