import os
import shutil

base_yml = """planet:
  name: '{name}'
  Rp: 5.867852e8
  gs: 801.2287
  orbit_radius: 0.02925
  sl_angle: 48.0
  f_diurnal: 1.0
  rocky: True
atmosphere:
  atm_type: 'file'
  atm_file: 'atm/atm_Trappist1e_Lin_Kzz.txt'
  P_b: 1.0e6
  P_t: 5.0e-2
  nz: 120
  Kzz_prof: 'file'
  const_mix:
    N2: 0.78
    O2: 0.20
    H2O: 1.0e-6
    CO2: {co2}
    Ar: 9.34e-3
    SO2: 2.0e-10
star:
  type: 'TRAPPIST-1'
  r_star: 0.1192
  sflux_file: 'atm/stellar_flux/TRAPPIST1_surface.txt'
chemistry:
  network: 'thermo/SNCHO_full_photo_network.txt'
  use_photo: True
  use_botflux: True
  bot_BC_flux_file: 'atm/BC_bot_Earth.txt'
  out_name: '{out_name}'
"""

configs_dir = "/mnt/c/Proyetos/Repos/ExoFarm_MDwarfs/Photochemical_Modeling/Config/planets/earth_trappist/"

tests = [
    ("A0", "0.036", "Trappist_A0_PreAgri.vul"),
    ("A1", "0.036", "Trappist_A1_Current.vul"),
    ("A2", "0.036", "Trappist_A2_Moderate.vul"),
    ("A3", "0.036", "Trappist_A3_Extreme.vul")
]

for test_name, co2, out_name in tests:
    filename = os.path.join(configs_dir, f"input_earth_trappist_{test_name}.yml")
    with open(filename, "w") as f:
        f.write(base_yml.format(name=f"Trappist_{test_name}", co2=co2, out_name=out_name))
    print(f"Generated {filename}")
