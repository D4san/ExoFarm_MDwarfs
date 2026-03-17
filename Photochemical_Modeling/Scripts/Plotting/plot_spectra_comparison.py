import numpy as np
import matplotlib.pyplot as plt
import os

# Configuration
solar_file = '../../../VULCAN/atm/stellar_flux/Gueymard_solar.txt'
trappist_file = '../../../VULCAN/atm/stellar_flux/TRAPPIST1_surface.txt'
output_plot = '../../Results/Plots/stellar_spectra_comparison.png'

def read_spectrum(filepath):
    """Reads spectrum file. Assumes 2 columns: Wavelength (nm), Flux."""
    # VULCAN standard files often have headers or comments
    try:
        data = np.genfromtxt(filepath, comments='#', names=['wave', 'flux'])
        return data['wave'], data['flux']
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None, None

def plot_spectra():
    print("Generating Stellar Spectra Comparison Plot...")
    
    # Read Data
    wave_sun, flux_sun = read_spectrum(solar_file)
    wave_trap, flux_trap = read_spectrum(trappist_file)
    
    if wave_sun is None or wave_trap is None:
        print("Could not read one of the spectra files. Aborting.")
        return

    # Create Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot Sun
    ax.plot(wave_sun, flux_sun, label='Sun (G2V)', color='#ff7f0e', linewidth=1, alpha=0.8)
    
    # Plot TRAPPIST-1
    ax.plot(wave_trap, flux_trap, label='TRAPPIST-1 (M8V)', color='#d62728', linewidth=1, alpha=0.8)
    
    # Formatting
    ax.set_yscale('log')
    ax.set_xscale('log')
    
    ax.set_xlabel('Wavelength (nm)', fontsize=12)
    ax.set_ylabel('Stellar Surface Flux (erg cm$^{-2}$ s$^{-1}$ nm$^{-1}$)', fontsize=12)
    ax.set_title('Stellar Spectra Comparison: Sun vs TRAPPIST-1', fontsize=14, fontweight='bold')
    
    # Limits - Focus on relevant UV-Vis-IR range for photochemistry
    ax.set_xlim(10, 3000) # 10 nm to 3000 nm (3 microns)
    ax.set_ylim(1e0, 1e8)
    
    # Add UV region highlight (important for photochemistry)
    ax.axvspan(10, 400, alpha=0.3, color='#dddddd', label='UV Region (<400 nm)')
    
    ax.legend(fontsize=10)
    ax.grid(True, which="both", ls="-", alpha=0.2)
    
    plt.tight_layout()
    
    if not os.path.exists('../../Results/Plots'):
        os.makedirs('../../Results/Plots')
        
    plt.savefig(output_plot, dpi=300)
    print(f"Plot saved to {output_plot}")

if __name__ == "__main__":
    plot_spectra()
