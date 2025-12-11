"""
Script to compare two VULCAN output files (.vul pickle files).

This script compares the species lists, temperature profiles (Tco), and mixing ratios (ymix)
between two VULCAN simulation outputs. It reports differences in species composition
and identifies significant discrepancies in mixing ratios.

Usage:
    python compare_vulcan_outputs.py <file1_path> <file2_path>
"""

import pickle
import numpy as np
import sys
import os
import argparse


def load_vulcan_output(filepath):
    """
    Loads a VULCAN output pickle file.

    Args:
        filepath (str): Path to the .vul file.

    Returns:
        dict: The loaded data dictionary.
    """
    try:
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        return data
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None


def get_species_data(y_arr, sp_list, species_name):
    """
    Extracts the mixing ratio array for a specific species.

    Args:
        y_arr (np.ndarray): The mixing ratio array (ymix).
        sp_list (list): List of species names.
        species_name (str): The species to extract.

    Returns:
        np.ndarray: The mixing ratio profile for the species, or None if not found.
    """
    if species_name not in sp_list:
        return None
    
    idx = sp_list.index(species_name)
    
    # Handle shape (nz, n_species) or (n_species, nz)
    # VULCAN output shape can vary depending on version/configuration
    if y_arr.shape[0] == len(sp_list): # (n_species, nz)
        return y_arr[idx, :]
    elif len(y_arr.shape) > 1 and y_arr.shape[1] == len(sp_list): # (nz, n_species)
        return y_arr[:, idx]
    else:
        # Fallback guess: usually (nz, n_species)
        return y_arr[:, idx]


def compare_outputs(file1, file2):
    """
    Compares two VULCAN output files and prints the differences.

    Args:
        file1 (str): Path to the first file.
        file2 (str): Path to the second file.
    """
    print(f"Comparing:\n  File 1: {file1}\n  File 2: {file2}")
    print("-" * 60)
    
    if not os.path.exists(file1):
        print(f"Error: {file1} does not exist.")
        return
    if not os.path.exists(file2):
        print(f"Error: {file2} does not exist.")
        return

    data1 = load_vulcan_output(file1)
    data2 = load_vulcan_output(file2)
    
    if data1 is None or data2 is None:
        return
    
    # Compare species list
    if 'species' in data1['variable']:
        sp1 = data1['variable']['species']
        sp2 = data2['variable']['species']
        
        common_species = sorted(list(set(sp1).intersection(set(sp2))))
        print(f"Species count in File 1: {len(sp1)}")
        print(f"Species count in File 2: {len(sp2)}")
        print(f"Common species count:    {len(common_species)}")
        
        if len(sp1) != len(sp2):
            print("\nSpecies lists differ:")
            unique1 = set(sp1) - set(sp2)
            unique2 = set(sp2) - set(sp1)
            if unique1:
                print(f"  Unique to File 1: {unique1}")
            if unique2:
                print(f"  Unique to File 2: {unique2}")

        # Compare 'ymix' (mixing ratios)
        var_key = 'ymix' if 'ymix' in data1['variable'] else 'y'
        print(f"\nComparing variable: '{var_key}'")

        if 'variable' in data1 and var_key in data1['variable']:
            y1 = data1['variable'][var_key]
            y2 = data2['variable'][var_key]
            
            max_rel_diff_overall = 0
            species_max_diff = ""
            
            print("Checking relative differences > 0.1% (1e-3)...")
            diff_found = False
            
            for sp in common_species:
                d1 = get_species_data(y1, sp1, sp)
                d2 = get_species_data(y2, sp2, sp)
                
                if d1 is None or d2 is None:
                    continue
                    
                diff = np.abs(d1 - d2)
                y_mean = (np.abs(d1) + np.abs(d2)) / 2.0
                
                # Avoid division by zero
                mask = y_mean > 1e-20
                
                rel_diff = np.zeros_like(diff)
                rel_diff[mask] = diff[mask] / y_mean[mask]
                
                max_rd = np.max(rel_diff)
                if max_rd > max_rel_diff_overall:
                    max_rel_diff_overall = max_rd
                    species_max_diff = sp
                
                if max_rd > 1e-3:
                    print(f"  {sp:<10}: Max Rel Diff = {max_rd:.4f}")
                    diff_found = True
            
            if not diff_found:
                print("  No significant differences found (> 0.1%).")
            
            print("-" * 60)
            print(f"Overall Max Relative Difference (Common Species): {max_rel_diff_overall:.6f}")
            print(f"Species with max difference: {species_max_diff}")
            
            if species_max_diff:
                d1 = get_species_data(y1, sp1, species_max_diff)
                d2 = get_species_data(y2, sp2, species_max_diff)
                
                # Find index of max relative difference
                y_mean = (np.abs(d1) + np.abs(d2)) / 2.0
                mask = y_mean > 1e-20
                rel_diff = np.zeros_like(d1)
                rel_diff[mask] = np.abs(d1 - d2)[mask] / y_mean[mask]
                
                idx_max_rel = np.argmax(rel_diff)
                print(f"  At index {idx_max_rel}:")
                print(f"    File 1 Value: {d1[idx_max_rel]:.4e}")
                print(f"    File 2 Value: {d2[idx_max_rel]:.4e}")

    # Compare T structure if available
    if 'atm' in data1 and 'Tco' in data1['atm']:
        t1 = data1['atm']['Tco']
        t2 = data2['atm']['Tco']
        max_diff_t = np.max(np.abs(t1 - t2))
        print(f"\nMax absolute difference in Temperature (Tco): {max_diff_t:.4f} K")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare two VULCAN output files.")
    parser.add_argument("file1", help="Path to the first .vul file")
    parser.add_argument("file2", help="Path to the second .vul file")
    
    args = parser.parse_args()
    
    compare_outputs(args.file1, args.file2)

