import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import os

# Paths
lin_path = "/home/wsldasan/POSEIDON/POSEIDON/reference_data/models/TRAPPIST-1e/TRAPPIST-1e_1.0bar_100xCO2_Modern_PT.txt"
earth_atm_path = "/mnt/c/Proyetos/Repos/ExoFarm_MDwarfs/VULCAN/atm/atm_Earth_Jan_Kzz.txt"
out_path = "/mnt/c/Proyetos/Repos/ExoFarm_MDwarfs/VULCAN/atm/atm_Trappist1e_Lin_Kzz.txt"

# 1. Load Lin PT
# Header: ALT P T FH2O O3 THEAT TCOOL PSATCO2 FCO2
lin_data = np.loadtxt(lin_path, skiprows=1)
lin_P_bar = lin_data[:, 1]
lin_T = lin_data[:, 2]
lin_P_cgs = lin_P_bar * 1e6  # Convert bar to dyne/cm2

# 2. Load Earth Kzz
earth_data = np.loadtxt(earth_atm_path, skiprows=2)
earth_P_cgs = earth_data[:, 0]
earth_Kzz = earth_data[:, 2]

# 3. Interpolate Kzz onto Lin Pressure grid
# Kzz interpolation is better done in log-log space
f_interp = interp1d(np.log10(earth_P_cgs[::-1]), np.log10(earth_Kzz[::-1]), kind='linear', fill_value="extrapolate")
lin_Kzz_log = f_interp(np.log10(lin_P_cgs))
lin_Kzz = 10**lin_Kzz_log

# 4. Write output file
with open(out_path, "w") as f:
    f.write("# (dyne/cm2) (K)     (cm2/s)\n")
    f.write("Pressure\tTemp\tKzz\n")
    for p, t, k in zip(lin_P_cgs, lin_T, lin_Kzz):
        f.write(f"{p:.3E}\t{t:.1f}\t{k:.2E}\n")

print(f"Successfully generated {out_path}")
