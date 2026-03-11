from POSEIDON.core import load_data, wl_grid_constant_R

# We just test load_data with paths
wl = wl_grid_constant_R(0.5, 14.0, 10000)
data_dir = 'POSEIDON_output/TRAPPIST-1e/'
datasets = [
    'pandexo_nirspec_prism_flat/TRAPPIST-1e_flat_NIRSpec_Prism_1_transits.dat',
    'pandexo_miri_lrs_flat/TRAPPIST-1e_flat_MIRI_LRS_1_transits.dat'
]
inst = ["JWST_NIRSpec_PRISM", "JWST_MIRI_LRS"]

# Trying load
try:
    load_data(data_dir, datasets, inst, wl, skiprows=1, wl_unit="micron", bin_width="half", spectrum_unit="(Rp/Rs)^2")
    print("SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")

