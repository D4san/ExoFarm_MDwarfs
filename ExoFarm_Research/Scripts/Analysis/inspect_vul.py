import pickle
import sys
import os

filename = os.path.join(os.getcwd(), '../../Results/Outputs', 'Earth_A0_PreAgri.vul')
try:
    with open(filename, 'rb') as f:
        data = pickle.load(f)
    print("Keys:", data.keys())
    if 'variable' in data:
        print("Variable keys:", list(data['variable'].keys()))
        if 'ymix' in data['variable']:
            print("ymix shape:", data['variable']['ymix'].shape)
        if 'species' in data['variable']:
            print("species:", data['variable']['species'])
    if 'atm' in data:
        print("Atm keys:", list(data['atm'].keys()))
        if 'pco' in data['atm']:
            print("pco shape:", data['atm']['pco'].shape)
except Exception as e:
    print(f"Error loading {filename}: {e}")
