import pickle
with open('/mnt/c/Proyetos/Repos/ExoFarm_MDwarfs/Photochemical_Modeling/Results/Outputs/Trappist_A0_PreAgri.vul', 'rb') as f:
    d = pickle.load(f)
print("Root keys:", list(d.keys()))
print("atm keys:", list(d['atm'].keys()))
print("variable keys:", list(d['variable'].keys()))
