import pickle
for f in ["Trappist_A1_Current.vul", "Trappist_Test2_A0_LinPT_100xCO2.vul", "Trappist_A0_PreAgri.vul", "Trappist_A3_Extreme.vul"]:
    with open("/mnt/c/Proyetos/Repos/ExoFarm_MDwarfs/Photochemical_Modeling/Results/Outputs/" + f, "rb") as file:
        d = pickle.load(file)
        print(f, d['parameter']['const_mix'])
