import json

with open('Plot_Transmission_Spectra_TRAPPIST.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for i in range(max(0, len(nb['cells'])-4), len(nb['cells'])):
    print(f"CELL {i}, ID: {nb['cells'][i].get('id')}")
    print("".join(nb['cells'][i]['source']))
