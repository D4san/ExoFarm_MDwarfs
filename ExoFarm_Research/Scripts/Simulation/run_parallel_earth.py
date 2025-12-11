"""
Script to run parallel VULCAN simulations for Earth scenarios.

This script manages the execution of multiple VULCAN simulations in parallel.
It performs the following steps for each scenario:
1. Creates a temporary working directory (e.g., temp_run_A0).
2. Copies necessary VULCAN source code and data files (atm, thermo, fastchem) to the temp directory.
3. Copies the specific Boundary Condition files.
4. Generates a VULCAN configuration file from the specified YAML input.
5. Runs the simulation using `run_case.py`.
6. Moves the final output (.vul file) to the Results/Outputs directory.
7. Cleans up (deletes) the temporary directory.

Usage:
    python run_parallel_earth.py
"""

import os
import shutil
import subprocess
import sys
import time
import glob

# ==========================================
# Configuration
# ==========================================

# List of scenarios to run.
# Each dictionary contains:
# - id: Unique identifier for the run (used for temp folder naming).
# - yaml: Relative path to the YAML configuration file.
# - name: Human-readable name for the scenario.
scenarios = [
    {
        'id': 'A0',
        'yaml': 'planets/earth_sun/input_earth_sun_A0.yml',
        'name': 'Pre-Agri'
    },
    {
        'id': 'A1',
        'yaml': 'planets/earth_sun/input_earth_sun_A1.yml',
        'name': 'Current'
    },
    {
        'id': 'A2',
        'yaml': 'planets/earth_sun/input_earth_sun_A2.yml',
        'name': 'Moderate'
    },
    {
        'id': 'A3',
        'yaml': 'planets/earth_sun/input_earth_sun_A3.yml',
        'name': 'Extreme'
    }
]

# DEBUGGING / TESTING:
# Uncomment the following line to run only specific scenarios (e.g., only A1)
# scenarios = scenarios[1:2] 

# ==========================================
# Path Setup
# ==========================================

script_dir = os.path.dirname(os.path.abspath(__file__))
# Project root is 3 levels up from Scripts/Simulation/
project_root = os.path.abspath(os.path.join(script_dir, '../../../'))

# Define key directories
vulcan_dir = os.path.join(project_root, 'VULCAN')
config_dir = os.path.join(project_root, 'ExoFarm_Research', 'Config')
boundary_conditions_dir = os.path.join(config_dir, 'Boundary_Conditions')
output_final_dir = os.path.join(project_root, 'ExoFarm_Research', 'Results', 'Outputs')

# Work base directory for creating temporary simulation folders
work_base_dir = os.path.join(project_root, 'ExoFarm_Research')

# Ensure output directory exists
if not os.path.exists(output_final_dir):
    os.makedirs(output_final_dir)
    print(f"Created output directory: {output_final_dir}")

# ==========================================
# Simulation Execution
# ==========================================

# Define resources to copy
py_files = glob.glob(os.path.join(vulcan_dir, '*.py'))
vulcan_folders_to_copy = ['thermo', 'atm', 'fastchem_vulcan']
folders_to_create = ['output', 'plot']

processes = []

print(f"Starting parallel execution of {len(scenarios)} scenarios...")
print(f"Project Root: {project_root}")
print(f"VULCAN Dir: {vulcan_dir}")
print(f"Output Dir: {output_final_dir}")

for sc in scenarios:
    run_id = sc['id']
    yaml_rel_path = sc['yaml']
    yaml_abs_path = os.path.join(config_dir, yaml_rel_path)
    
    # 1. Create unique temp directory
    temp_dir = os.path.join(work_base_dir, f'temp_run_{run_id}')
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    print(f"[{run_id}] Setting up directory: {temp_dir}")
    
    # 2. Copy Python source files
    print(f"[{run_id}] Copying .py files from VULCAN...")
    for f in py_files:
        try:
            shutil.copy(f, temp_dir)
        except Exception as e:
            print(f"[{run_id}] Error copying {f}: {e}")

    # Explicitly ensure run_case.py and vulcan.py are copied (critical files)
    for f in ['run_case.py', 'vulcan.py']:
        src = os.path.join(vulcan_dir, f)
        dst = os.path.join(temp_dir, f)
        if os.path.exists(src):
            try:
                shutil.copy2(src, dst)
            except Exception as e:
                print(f"[{run_id}] Error explicitly copying {f}: {e}")
        else:
             print(f"[{run_id}] Warning: {f} not found in {vulcan_dir}")
        
    # 3. Copy VULCAN data folders (thermo, atm, etc.)
    for folder in vulcan_folders_to_copy:
        src = os.path.join(vulcan_dir, folder)
        dst = os.path.join(temp_dir, folder)
        if os.path.exists(src):
            shutil.copytree(src, dst)

    # 4. Copy Boundary Conditions
    # Note: VULCAN expects a 'boundary_conditions' folder
    src_bc = boundary_conditions_dir
    dst_bc = os.path.join(temp_dir, 'boundary_conditions')
    if os.path.exists(src_bc):
        shutil.copytree(src_bc, dst_bc)
            
    # 5. Create output structure
    for folder in folders_to_create:
        os.makedirs(os.path.join(temp_dir, folder), exist_ok=True)
        
    # 6. Launch Simulation Process
    print(f"[{run_id}] Launching VULCAN...")
    # Command: python -u run_case.py <abs_path_to_yaml>
    # -u: Unbuffered output (useful for logging)
    cmd = [sys.executable, '-u', 'run_case.py', yaml_abs_path]
    
    # Redirect stdout/stderr to a log file
    log_file_path = os.path.join(temp_dir, f'run_{run_id}.log')
    log_file = open(log_file_path, 'w')
    
    p = subprocess.Popen(cmd, cwd=temp_dir, stdout=log_file, stderr=subprocess.STDOUT)
    processes.append({'p': p, 'id': run_id, 'dir': temp_dir, 'log': log_file})

# ==========================================
# Monitoring
# ==========================================

print("All processes launched. Waiting for completion...")

completed = 0
while completed < len(processes):
    time.sleep(5)
    completed = 0
    for proc in processes:
        if proc['p'].poll() is not None:
            completed += 1
    
    # Here you could add more sophisticated progress tracking if needed
    # e.g., tailing the log files

print("All runs completed.")

# ==========================================
# Cleanup and Collection
# ==========================================

for proc in processes:
    proc['log'].close()
    run_id = proc['id']
    temp_dir = proc['dir']
    
    # 1. Collect Output Files (.vul)
    vul_files = glob.glob(os.path.join(temp_dir, 'output', '*.vul'))
    for vf in vul_files:
        fname = os.path.basename(vf)
        dst = os.path.join(output_final_dir, fname)
        print(f"[{run_id}] Moving output {fname} to {output_final_dir}")
        
        # Safely remove destination if it exists (overwrite)
        if os.path.exists(dst):
            try:
                os.remove(dst)
            except OSError as e:
                print(f"[{run_id}] Error removing existing file {dst}: {e}")
        
        try:
            shutil.move(vf, dst)
        except Exception as e:
             print(f"[{run_id}] Error moving output file: {e}")
        
    # 2. Delete Temporary Directory
    print(f"[{run_id}] Cleaning up temp directory {temp_dir}...")
    try:
        shutil.rmtree(temp_dir)
        print(f"[{run_id}] Temp directory removed.")
    except Exception as e:
        print(f"[{run_id}] Failed to remove temp directory: {e}")

print("Parallel execution finished.")
