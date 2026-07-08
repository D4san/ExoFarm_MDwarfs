import pickle
with open('/mnt/c/Proyetos/Repos/ExoFarm_MDwarfs/Photochemical_Modeling/Results/Outputs/Trappist_A0_PreAgri.vul','rb') as f:
    d = pickle.load(f)
    print('A0 NH3:', d['variable']['ymix'][0][d['variable']['species'].index('NH3')])
with open('/mnt/c/Proyetos/Repos/ExoFarm_MDwarfs/Photochemical_Modeling/Results/Outputs/Trappist_A3_Extreme.vul','rb') as f:
    d = pickle.load(f)
    print('A3 NH3:', d['variable']['ymix'][0][d['variable']['species'].index('NH3')])
