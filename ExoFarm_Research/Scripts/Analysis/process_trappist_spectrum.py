import numpy as np
import os

# Input and Output paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../../'))
input_file = os.path.join(project_root, 'trappist-1_model_const_res_v07.ecsv')
output_file = os.path.join(project_root, 'VULCAN/atm/stellar_flux/TRAPPIST1_surface.txt')

# Constants
pc_to_cm = 3.0857e18
R_sun_cm = 6.957e10
R_star_sun = 0.117 # TRAPPIST-1 radius in Solar Radii
R_star_cm = R_star_sun * R_sun_cm
d_star_pc = 12.47 # Distance to TRAPPIST-1 in pc
d_star_cm = d_star_pc * pc_to_cm

# Scaling factor: From observed flux at d_star to surface flux at R_star
# F_surf * 4*pi*R_star^2 = F_obs * 4*pi*d_star^2
# F_surf = F_obs * (d_star / R_star)^2
scale_factor = (d_star_cm / R_star_cm)**2

print(f"Scaling Factor: {scale_factor:.2e}")

# Read Data
# Skipping header lines starting with #
data = np.genfromtxt(input_file, comments='#', names=['wave', 'flux'])

# Convert Units
# Wavelength: Angstrom -> nm (divide by 10)
wave_nm = data['wave'] / 10.0

# Flux: erg/cm2/s/A -> erg/cm2/s/nm (multiply by 10)
# And apply geometric scaling to surface
flux_surf = data['flux'] * 10.0 * scale_factor

# Save to file
header = "Wavelength(nm)    Flux(erg/cm2/s/nm)"
save_data = np.column_stack((wave_nm, flux_surf))

# Sort by wavelength just in case
save_data = save_data[save_data[:,0].argsort()]

# Save
np.savetxt(output_file, save_data, header=header, fmt='%12.6e')
print(f"Saved processed spectrum to {output_file}")
