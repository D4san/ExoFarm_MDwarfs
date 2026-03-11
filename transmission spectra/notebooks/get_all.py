import json

with open('Plot_Transmission_Spectra_TRAPPIST.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for i in range(len(nb['cells'])):
    src = "".join(nb['cells'][i].get('source', ''))
    if "load_data" in src and "synthetic_dir" in src:
        print(f"CELL {i}, ID: {nb['cells'][i].get('id')}")
        print(src)
