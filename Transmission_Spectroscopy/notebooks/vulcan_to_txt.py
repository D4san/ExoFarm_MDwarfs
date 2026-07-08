import pickle
import numpy as np
import os

vulcan_dir = "/mnt/c/Proyetos/Repos/ExoFarm_MDwarfs/Photochemical_Modeling/Results/Outputs"
prof_dir = "/mnt/c/Proyetos/Repos/ExoFarm_MDwarfs/Transmission_Spectroscopy/profiles"

cases = {
    "Trappist_A0": ("Trappist_A0_PreAgri.vul", "Trappist_A0_PreAgri_chem.txt"),
    "Trappist_A1": ("Trappist_A1_Current.vul", "Trappist_A1_Current_chem.txt"),
    "Trappist_A2": ("Trappist_A2_Moderate.vul", "Trappist_A2_Moderate_chem.txt"),
    "Trappist_A3": ("Trappist_A3_Extreme.vul", "Trappist_A3_Extreme_chem.txt")
}

for case_id, (in_file, out_file) in cases.items():
    vul_path = os.path.join(vulcan_dir, in_file)
    txt_path = os.path.join(prof_dir, out_file)
    
    if not os.path.exists(vul_path):
        print(f"Skipping {vul_path} - does not exist yet")
        continue
        
    with open(vul_path, "rb") as f:
        data = pickle.load(f)
        
    # 1. Export chemistry profile
    species = data["variable"]["species"]
    pressure = np.asarray(data["atm"]["pco"]) # dyne/cm2
    mixing_ratios = np.asarray(data["variable"]["ymix"])
    
    header = "PRESS " + " ".join(species)
    out_data = np.column_stack((pressure, mixing_ratios))
    np.savetxt(txt_path, out_data, header=header, comments="", fmt="%.5E")
    print(f"Successfully wrote {txt_path}")

    # 2. Export PT profile
    pt_out_file = out_file.replace("_chem.txt", "_PT.txt")
    pt_path = os.path.join(prof_dir, pt_out_file)
    
    altitude_km = np.asarray(data["atm"]["zmco"]) / 1e5 # cm to km
    pressure_bar = np.asarray(data["atm"]["pco"]) / 1e6 # dyne/cm2 to bar
    temperature = np.asarray(data["atm"]["Tco"]) # K
    
    pt_header = "ALT P T"
    pt_data = np.column_stack((altitude_km, pressure_bar, temperature))
    np.savetxt(pt_path, pt_data, header=pt_header, comments="", fmt="%.6e")
    print(f"Successfully wrote {pt_path}")
