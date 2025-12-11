import sys
import shutil
import yaml
import os
import subprocess

def create_vulcan_cfg(config_file):
    with open(config_file, 'r') as f:
        conf = yaml.safe_load(f)
    
    # Convert const_mix dict to string representation for python file
    const_mix_str = str(conf['atmosphere']['const_mix'])
    
    cfg_content = f"""# =============================================================================
# Configuration file of VULCAN (Auto-generated from {config_file})
# =============================================================================

# ====== Setting up the elements included in the network ======
atom_list = ['H', 'O', 'C', 'N', 'S']

# ====== Setting up paths and filenames ======
network = '{conf['chemistry']['network']}'
use_lowT_limit_rates = False
gibbs_text = 'thermo/gibbs_text.txt'
cross_folder = 'thermo/photo_cross/'
com_file = 'thermo/all_compose.txt'
atm_file = '{conf['atmosphere']['atm_file']}'
sflux_file = '{conf['star']['sflux_file']}'
top_BC_flux_file = 'atm/BC_top.txt'
bot_BC_flux_file = '{conf['chemistry']['bot_BC_flux_file']}'
vul_ini = 'output/'
output_dir = 'output/'
plot_dir = 'plot/'
movie_dir = 'plot/movie/'
out_name = '{conf['chemistry']['out_name']}'

# ====== Setting up the elemental abundance ======
use_solar = False 
O_H = 6.0618E-4 * 0.85
C_H = 2.7761E-4
N_H = 8.1853E-5
S_H = 1.3183E-5
He_H = 0.09692
ini_mix = 'const_mix'
fastchem_met_scale = 1.

use_ini_cold_trap = True

# Initialising uniform mixing ratios
const_mix = {const_mix_str}

# ====== Setting up photochemistry ======
use_photo = {conf['chemistry']['use_photo']}
r_star = {conf['star']['r_star']}
Rp = {conf['planet']['Rp']}
orbit_radius = {conf['planet']['orbit_radius']}
sl_angle = {conf['planet']['sl_angle']} / 180. * 3.14159
f_diurnal = {conf['planet']['f_diurnal']}
scat_sp = ['N2', 'O2'] 
T_cross_sp = ['CO2', 'H2O', 'NH3'] 

edd = 0.5
dbin1 = 0.1
dbin2 = 2.
dbin_12trans = 240.
ini_update_photo_frq = 100
final_update_photo_frq = 5

# ====== Setting up ionchemistry ======
use_ion = False

# ====== Setting up parameters for the atmosphere ======
atm_base = 'N2' 
rocky = {conf['planet']['rocky']}
nz = {conf['atmosphere']['nz']}
P_b = {conf['atmosphere']['P_b']}
P_t = {conf['atmosphere']['P_t']}
use_Kzz = True
use_moldiff = True
use_vm_mol = False
use_vz = False
atm_type = '{conf['atmosphere']['atm_type']}'
Kzz_prof = '{conf['atmosphere']['Kzz_prof']}'
K_max = 1e5
K_p_lev = 0.1
vz_prof = 'const'
gs = {conf['planet']['gs']}
Tiso = 1000
para_warm = [120., 1500., 0.1, 0.02, 1., 1.]
para_anaTP = para_warm
const_Kzz = 1.E10
const_vz = 0
update_frq = 100

# ====== Setting up the boundary conditions ======
use_topflux = False
use_botflux = {conf['chemistry']['use_botflux']}
use_fix_sp_bot = {{"H2O":0.00894, "H2O_l_s":0, 'CO2':4E-4}}
diff_esc = ['H2', 'H'] # species for diffusion-limit escape at TOA
max_flux = 1e13  # upper limit for the diffusion-limit fluxes

# ====== Reactions to be switched off  ======
remove_list = [] # in pairs e.g. [1,2]

# == Condensation ======
use_condense = True
use_settling = True
use_relax = ['H2O', 'H2SO4']
humidity = 0.25 # only for water
r_p = {{'H2O_l_s': 0.01, 'H2SO4_l': 1e-4}}  # particle radius in cm (1e-4 = 1 micron)
rho_p = {{'H2O_l_s': 0.9, 'H2SO4_l': 1.8302}} # particle density in g cm^-3
start_conden_time = 0
stop_conden_time = 5e8
condense_sp = ["H2O" , "H2SO4"]      
non_gas_sp = [ 'H2O_l_s', "H2SO4_l"]
fix_species = ['H2O','H2O_l_s',"H2SO4","H2SO4_l"]      # fixed the condensable species after condensation-evapoation EQ has reached  
fix_species_time = stop_conden_time # ~20 yrs; after this time to fix the condensable species

fix_species_from_coldtrap_lev = True
use_ini_cold_trap = True  # cold trap from the get go
use_sat_surfaceH2O = False # for terrestriall atmospheres where H2O is controlled by surface T

# ====== steady state check ======
st_factor = 0.5
conv_step = 500

# ====== Setting up numerical parameters for the ODE solver ====== 
ode_solver = 'Ros2' # case sensitive
use_print_prog = True
use_print_delta = False
print_prog_num = 500  # print the progress every x steps 
dttry = 1.E-10
trun_min = 1e2
runtime = 1.E22
dt_min = 1.E-14
dt_max = runtime*1e-5
dt_var_max = 2.
dt_var_min = 0.5
count_min = 120
count_max = 5000
atol = 1.E-1 # Try decreasing this if the solutions are not stable
mtol = 1.E-22
mtol_conv = 1.E-16
pos_cut = 0
nega_cut = -1.
loss_eps = 1e12 # for using BC
yconv_cri = 0.01 # for checking steady-state
slope_cri = 1.e-4
yconv_min = 0.1
flux_cri = 0.1
flux_atol = 1.

# ====== Setting up numerical parameters for Ros2 ODE solver ====== 
rtol = 1.5             # relative tolerence for adjusting the stepsize 
post_conden_rtol = 0.2 # switched to this value after fix_species_time
use_adapt_rtol = False # True: use the adaptive rtol (experimental)
rtol_min = 1e-4

# ====== Diffusion-limit escape ======
diff_esc = ['H2', 'H'] # species for diffusion-limit escape at TOA
max_flux = 1e13  # upper limit for the diffusion-limit fluxes

# ====== Setting up for ouwtput and plotting ======
# plotting:
plot_TP = False
use_live_plot = False
use_live_flux = False
use_plot_end = False
use_plot_evo = False
use_save_movie = False
use_flux_movie = False
plot_height = False
use_PIL = True 
live_plot_frq = 10
save_movie_rate = live_plot_frq
y_time_freq = 1  #  storing data for every 'y_time_freq' step
plot_spec = ['H2O', 'H2O_l_s', 'O3',  'CH4', 'NH3' ,'N2O']  
# output:
output_humanread = False
use_shark = False
save_evolution = False   # save the evolution of chemistry (y_time and t_time) for every save_evo_frq step
save_evo_frq = 10
"""
    with open('vulcan_cfg.py', 'w') as f:
        f.write(cfg_content)
    print(f"Generated vulcan_cfg.py from {config_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_case.py <config_yaml>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    # Backup original cfg
    if os.path.exists('vulcan_cfg.py') and not os.path.exists('vulcan_cfg.py.bak'):
        shutil.copy('vulcan_cfg.py', 'vulcan_cfg.py.bak')
    
    try:
        create_vulcan_cfg(config_file)
        print("Running VULCAN...")
        # Run vulcan.py
        subprocess.run([sys.executable, '-u', 'vulcan.py'], check=True)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Restore
        if os.path.exists('vulcan_cfg.py.bak'):
            shutil.move('vulcan_cfg.py.bak', 'vulcan_cfg.py')
            print("Restored original vulcan_cfg.py")
