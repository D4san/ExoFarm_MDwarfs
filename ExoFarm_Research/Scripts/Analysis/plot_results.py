"""
Script to generate ALL analysis plots for the ExoFarm project.

This script generates:
1. Vertical Abundance Profiles (Mixing Ratio vs Pressure) for each simulation.
2. Temperature-Pressure (TP) Profiles for each simulation.
3. Surface Normalized Bar Charts: Comparing surface abundances across scenarios (A0-A3),
   normalized to the Earth A1 (Present Day) baseline.
4. Star Comparison Profiles: Comparing Earth vs TRAPPIST-1e atmospheric structure for the same scenarios.
5. Stellar Spectra Comparison: Plotting the input stellar fluxes (Sun vs TRAPPIST-1).

Usage:
    python plot_results.py
"""

import pickle
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import sys

# =============================================================================
# Configuration
# =============================================================================

# Set style for professional plots
plt.style.use('default')
plt.rcParams.update({
    'font.size': 14,
    'axes.labelsize': 16,
    'axes.titlesize': 18,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'legend.fontsize': 12,
    'lines.linewidth': 2.5,
    'figure.figsize': (10, 8)
})

MOLECULES_OF_INTEREST = ['N2O', 'NH3', 'O3', 'CH4', 'H2O', 'CO2']
SCENARIOS = ['A0', 'A1', 'A2', 'A3']
SCENARIO_LABELS = ['Pre-Agri', 'Present', 'ExoFarm (Mod)', 'ExoFarm (Ext)']
STARS = ['Earth', 'Trappist']

# =============================================================================
# Helper Functions
# =============================================================================

def load_vulcan_output(filepath):
    """Loads a VULCAN output pickle file."""
    try:
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        return data
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def get_surface_mixing_ratio(data, species):
    """Extracts the surface mixing ratio of a species."""
    if 'variable' not in data or 'species' not in data['variable']:
        return None
    
    if species not in data['variable']['species']:
        return None
        
    sp_idx = data['variable']['species'].index(species)
    
    # Surface is usually the max pressure index
    pco = data['atm']['pco']
    surf_idx = np.argmax(pco)
    
    # Handle ymix shape
    ymix = data['variable']['ymix']
    if ymix.shape[0] == len(data['variable']['species']): # (n_species, nz)
        return float(ymix[sp_idx, surf_idx])
    else: # (nz, n_species)
        return float(ymix[surf_idx, sp_idx])

# =============================================================================
# Plotting Functions
# =============================================================================

def plot_vertical_profiles(data, filename, output_dir):
    """Plots vertical mixing ratio profiles for key species."""
    if not data: return

    species_list = data['variable']['species']
    pressure = data['atm']['pco'] / 1e6 # bar
    
    fig, ax = plt.subplots(figsize=(8, 10))
    
    # Plot defined molecules
    for sp in MOLECULES_OF_INTEREST:
        if sp in species_list:
            idx = species_list.index(sp)
            ymix = data['variable']['ymix']
            
            if ymix.shape[0] == len(species_list):
                profile = ymix[idx, :]
            else:
                profile = ymix[:, idx]
            
            ax.plot(profile, pressure, label=sp)

    ax.set_yscale('log')
    ax.set_xscale('log')
    ax.invert_yaxis()
    
    ax.set_xlabel('Mixing Ratio')
    ax.set_ylabel('Pressure (bar)')
    ax.set_title(f'Vertical Abundance Profiles\n{filename}')
    ax.grid(True, which="both", ls="-", alpha=0.3)
    ax.legend(loc='best')
    ax.set_xlim(1e-12, 1.0) # Focus on relevant range
    
    out_path = os.path.join(output_dir, f"{filename}_profiles.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {out_path}")

def plot_tp_profile(data, filename, output_dir):
    """Plots the Temperature-Pressure profile."""
    if not data: return

    pressure = data['atm']['pco'] / 1e6 # bar
    temp = data['atm']['Tco']
    
    fig, ax = plt.subplots(figsize=(6, 8))
    
    ax.plot(temp, pressure, 'r-', linewidth=3)
    
    ax.set_yscale('log')
    ax.invert_yaxis()
    
    ax.set_xlabel('Temperature (K)')
    ax.set_ylabel('Pressure (bar)')
    ax.set_title(f'Temperature-Pressure Profile\n{filename}')
    ax.grid(True, which="both", ls="-", alpha=0.3)
    
    out_path = os.path.join(output_dir, f"{filename}_TP.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {out_path}")

def plot_surface_bars_normalized(surface_data, output_dir):
    """
    Plots bar charts of surface abundances normalized to Earth A1.
    
    Args:
        surface_data (dict): Nested dict [star][scenario][molecule] -> value
    """
    # Baseline: Earth A1
    baseline = {}
    for mol in MOLECULES_OF_INTEREST:
        try:
            val = surface_data['Earth']['A1'][mol]
            baseline[mol] = val if val > 0 else 1.0 # Avoid div by zero
        except:
            baseline[mol] = 1.0
            
    # Prepare Plot
    fig, axes = plt.subplots(1, 2, figsize=(18, 8), sharey=True)
    
    x = np.arange(len(MOLECULES_OF_INTEREST))
    width = 0.2
    
    for i, star in enumerate(STARS):
        ax = axes[i]
        
        for j, scenario in enumerate(SCENARIOS):
            y_vals = []
            for mol in MOLECULES_OF_INTEREST:
                val = surface_data[star][scenario].get(mol, 1e-99)
                base = baseline.get(mol, 1.0)
                # Normalize
                norm_val = val / base
                y_vals.append(norm_val)
            
            # Offset bars
            offset = (j - 1.5) * width
            ax.bar(x + offset, y_vals, width, label=SCENARIO_LABELS[j], alpha=0.8)
            
        ax.set_title(f'{star} System', fontsize=20)
        ax.set_xticks(x)
        ax.set_xticklabels(MOLECULES_OF_INTEREST)
        ax.set_yscale('log')
        ax.grid(True, axis='y', alpha=0.3)
        if i == 0:
            ax.set_ylabel('Abundance relative to Earth Present (A1)', fontsize=16)
        
        # Add baseline line
        ax.axhline(1.0, color='k', linestyle='--', linewidth=1, alpha=0.5)

    # Common Legend
    axes[0].legend(loc='upper left', ncol=2)
    
    plt.suptitle('Surface Abundance Comparison (Normalized)', fontsize=24)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    out_path = os.path.join(output_dir, "Comparison_Surface_Normalized.png")
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Saved: {out_path}")

def plot_star_comparison(earth_data, trappist_data, scenario_name, output_dir):
    """Compares Earth vs Trappist profiles for a specific scenario."""
    if not earth_data or not trappist_data: return

    fig, ax = plt.subplots(figsize=(10, 8))
    
    colors = {'Earth': 'blue', 'Trappist': 'red'}
    linestyles = {'N2O': '-', 'O3': '--', 'CH4': ':'}
    
    compare_mols = ['N2O', 'O3', 'CH4']
    
    for mol in compare_mols:
        # Earth
        if mol in earth_data['variable']['species']:
            idx = earth_data['variable']['species'].index(mol)
            p = earth_data['atm']['pco']/1e6
            y = earth_data['variable']['ymix'][:, idx] if earth_data['variable']['ymix'].shape[1] == len(earth_data['variable']['species']) else earth_data['variable']['ymix'][idx, :]
            ax.plot(y, p, color=colors['Earth'], linestyle=linestyles[mol], label=f'Earth {mol}')
            
        # Trappist
        if mol in trappist_data['variable']['species']:
            idx = trappist_data['variable']['species'].index(mol)
            p = trappist_data['atm']['pco']/1e6
            y = trappist_data['variable']['ymix'][:, idx] if trappist_data['variable']['ymix'].shape[1] == len(trappist_data['variable']['species']) else trappist_data['variable']['ymix'][idx, :]
            ax.plot(y, p, color=colors['Trappist'], linestyle=linestyles[mol], label=f'Trappist {mol}')

    ax.set_yscale('log')
    ax.set_xscale('log')
    ax.invert_yaxis()
    ax.set_xlabel('Mixing Ratio')
    ax.set_ylabel('Pressure (bar)')
    ax.set_title(f'Earth vs TRAPPIST-1e: {scenario_name} Atmosphere')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    out_path = os.path.join(output_dir, f"Comparison_Star_{scenario_name}.png")
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Saved: {out_path}")

def plot_spectra_comparison(project_root, output_dir):
    """Plots the input stellar fluxes."""
    earth_flux_path = os.path.join(project_root, 'VULCAN/atm/stellar_flux/Gueymard_solar.txt')
    trappist_flux_path = os.path.join(project_root, 'VULCAN/atm/stellar_flux/TRAPPIST1_surface.txt')
    
    if not os.path.exists(earth_flux_path) or not os.path.exists(trappist_flux_path):
        print("Skipping spectra plot: Flux files not found.")
        return

    # Load Earth (skip rows until data)
    # Format usually: lambda(nm) flux(erg/cm2/s/nm) ...
    try:
        # Simple parser for Gueymard
        earth_data = np.genfromtxt(earth_flux_path, skip_header=10, comments='#') 
        # Gueymard is usually nm, flux
        w_earth = earth_data[:,0]
        f_earth = earth_data[:,1]
        
        # Load Trappist
        trap_data = np.loadtxt(trappist_flux_path, skiprows=1)
        w_trap = trap_data[:,0]
        f_trap = trap_data[:,1]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(w_earth, f_earth, 'b-', alpha=0.7, label='Sun (Earth Surface)')
        ax.plot(w_trap, f_trap, 'r-', alpha=0.7, label='TRAPPIST-1 (Planet Surface)')
        
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel('Wavelength (nm)')
        ax.set_ylabel('Flux (erg s$^{-1}$ cm$^{-2}$ nm$^{-1}$)')
        ax.set_title('Stellar Spectra Comparison (Surface Insolation)')
        ax.set_xlim(100, 4000) # UV to IR
        ax.legend()
        ax.grid(True, which="both", alpha=0.3)
        
        out_path = os.path.join(output_dir, "Comparison_Spectra.png")
        plt.savefig(out_path, dpi=300)
        plt.close(fig)
        print(f"Saved: {out_path}")
        
    except Exception as e:
        print(f"Error plotting spectra: {e}")

# =============================================================================
# Main Execution
# =============================================================================

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '../../'))
    output_dir = os.path.join(project_root, 'ExoFarm_Research', 'Results', 'Outputs')
    figures_dir = os.path.join(project_root, 'ExoFarm_Research', 'Results', 'Figures')
    
    if not os.path.exists(figures_dir):
        os.makedirs(figures_dir)

    print("--- Starting Plot Generation ---")

    # Data container for surface bars: [Star][Scenario][Mol] -> Val
    surface_data = {star: {sc: {} for sc in SCENARIOS} for star in STARS}
    
    # Store full data for A2 comparison
    earth_a2_data = None
    trappist_a2_data = None

    # Process all scenarios
    for star in STARS:
        for sc in SCENARIOS:
            filename = f"{star}_{sc}" 
            # Match actual filenames (e.g., Earth_A0_PreAgri.vul)
            pattern = os.path.join(output_dir, f"{star}_{sc}_*.vul")
            files = glob.glob(pattern)
            
            if not files:
                print(f"Warning: No output found for {star} {sc}")
                continue
                
            filepath = files[0] # Take first match
            short_name = os.path.basename(filepath).replace('.vul', '')
            
            print(f"Processing {short_name}...")
            data = load_vulcan_output(filepath)
            
            if data:
                # 1. Individual Plots
                plot_vertical_profiles(data, short_name, figures_dir)
                plot_tp_profile(data, short_name, figures_dir)
                
                # 2. Collect Surface Data
                for mol in MOLECULES_OF_INTEREST:
                    val = get_surface_mixing_ratio(data, mol)
                    if val is not None:
                        surface_data[star][sc][mol] = val
                
                # 3. Store for Comparison
                if sc == 'A2':
                    if star == 'Earth': earth_a2_data = data
                    if star == 'Trappist': trappist_a2_data = data

    # 4. Generate Aggregate Plots
    print("Generating aggregate plots...")
    plot_surface_bars_normalized(surface_data, figures_dir)
    plot_star_comparison(earth_a2_data, trappist_a2_data, 'A2_ExoFarm_Mod', figures_dir)
    plot_spectra_comparison(project_root, figures_dir)
    
    print("--- All plots generated in Results/Figures ---")

if __name__ == "__main__":
    main()
