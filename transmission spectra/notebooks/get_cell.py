import json

with open('Plot_Transmission_Spectra_TRAPPIST.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for i, cl in enumerate(nb['cells']):
    if "wl_min" in "".join(cl['source']):
        print(f"CELL {i}")
        print("".join(cl['source']))
