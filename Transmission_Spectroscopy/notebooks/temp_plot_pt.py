import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Load Lin et al. PT profile
lin_path = "/home/wsldasan/POSEIDON/POSEIDON/reference_data/models/TRAPPIST-1e/TRAPPIST-1e_1.0bar_100xCO2_Modern_PT.txt"
lin_data = np.loadtxt(lin_path, skiprows=1)
# Column 1 is P (bar), Column 2 is T (K)
lin_P = lin_data[:, 1]
lin_T = lin_data[:, 2]

# Load VULCAN PT profile (we use Trappist_A0_PreAgri_PT.txt)
vulcan_path = "/mnt/c/Proyetos/Repos/ExoFarm_MDwarfs/Transmission_Spectroscopy/profiles/Trappist_A0_PreAgri_PT.txt"
vulcan_data = np.loadtxt(vulcan_path, skiprows=1)
# Typically column 1 is Pressure (dyne/cm2 or bar?) Let's check VULCAN PT files.
# VULCAN PT files usually have: Height, Pressure, Temp...
# Actually, the python script plot_pure_transmission_spectra reads it with P_column=2, T_column=3, wait, 0-indexed that would be col 1 and 2.
vulcan_P = vulcan_data[:, 1]
vulcan_T = vulcan_data[:, 2]
# We might need to convert VULCAN pressure from dyne/cm2 to bar (1e6 dyne/cm2 = 1 bar) if it is dyne/cm2.
# Let's plot assuming it's dyne/cm2 first and convert to bar, unless it's already in bar.
# Usually VULCAN output is in dyne/cm2 or bars depending on the stage.
# In plot_pure_transmission_spectra.py, it reads it directly or interpolates.
# We'll just plot and see the limits.

plt.figure(figsize=(6, 8))
plt.plot(lin_T, lin_P, label="POSEIDON/Lin (100x CO2)", color="blue", linewidth=2)
# If VULCAN P is around 1e6 at surface, it's dyne/cm2. We divide by 1e6 to get bar.
vulcan_P_bar = vulcan_P / 1e6 if np.max(vulcan_P) > 10 else vulcan_P
plt.plot(vulcan_T, vulcan_P_bar, label="ExoFarm/VULCAN (1x CO2)", color="red", linestyle="--", linewidth=2)

plt.yscale('log')
plt.gca().invert_yaxis()
plt.xlabel("Temperature (K)")
plt.ylabel("Pressure (bar)")
plt.title("TRAPPIST-1e PT Profiles Comparison")
plt.legend()
plt.grid(True, which="both", ls="--", alpha=0.5)

out_path = "/mnt/c/Proyetos/Repos/ExoFarm_MDwarfs/Transmission_Spectroscopy/notebooks/temp_pt_comparison.png"
plt.savefig(out_path, dpi=300, bbox_inches="tight")
print("Plot saved to", out_path)
