"""
Script to run parallel VULCAN simulations for Earth scenarios.

This script manages the execution of multiple VULCAN simulations in parallel.
It performs the following steps for each scenario:
1. Creates a temporary working directory (e.g., temp_run_A0).
2. Copies necessary VULCAN source code and data files (atm, thermo, fastchem) to the temp directory.
3. Stages the scenario-specific lower boundary file as atm/BC_bot_Earth.txt.
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
from collections import deque

# ==========================================
# Configuration
# ==========================================

# List of scenarios to run.
# Each dictionary contains:
# - id: Unique identifier for the run (used for temp folder naming).
# - yaml: Relative path to the YAML configuration file.
# - name: Human-readable name for the scenario.
# - bc_source: Scenario-specific BC template staged to atm/BC_bot_Earth.txt.
scenarios = [
    {
        'id': 'A0',
        'yaml': 'planets/earth_sun/input_earth_sun_A0.yml',
        'name': 'Pre-Agri',
        'bc_source': 'bc_earth_preagri_full.txt'
    },
    {
        'id': 'A1',
        'yaml': 'planets/earth_sun/input_earth_sun_A1.yml',
        'name': 'Current',
        'bc_source': 'bc_earth_current_full.txt'
    },
    {
        'id': 'A2',
        'yaml': 'planets/earth_sun/input_earth_sun_A2.yml',
        'name': 'Moderate',
        'bc_source': 'bc_earth_exofarm_moderate_full.txt'
    },
    {
        'id': 'A3',
        'yaml': 'planets/earth_sun/input_earth_sun_A3.yml',
        'name': 'Extreme',
        'bc_source': 'bc_earth_exofarm_full.txt'
    }
]

scenario_filter = {
    item.strip() for item in os.environ.get('EXOFARM_SCENARIOS', '').split(',')
    if item.strip()
}
if scenario_filter:
    scenarios = [sc for sc in scenarios if sc['id'] in scenario_filter]
    print(f"Scenario filter active: {', '.join(sorted(scenario_filter))}")

# Keep failed temp directories so the logs and staged VULCAN workspace
# are still available for debugging. Successful runs are cleaned up.
KEEP_FAILED_TEMP = True
KEEP_SUCCESS_TEMP = os.environ.get('EXOFARM_KEEP_TEMP', '').strip() == '1'
LOG_TAIL_LINES = 80


def read_log_tail(log_path, max_lines=LOG_TAIL_LINES):
    """Return the last max_lines lines from a log file as a string."""
    if not os.path.exists(log_path):
        return ''

    with open(log_path, 'r', encoding='utf-8', errors='replace') as handle:
        return ''.join(deque(handle, maxlen=max_lines))

# ==========================================
# Path Setup
# ==========================================

script_dir = os.path.dirname(os.path.abspath(__file__))
# Project root is 3 levels up from Scripts/Simulation/
project_root = os.path.abspath(os.path.join(script_dir, '../../../'))

# Define key directories
vulcan_dir = os.path.join(project_root, 'VULCAN')
config_dir = os.path.join(project_root, 'Photochemical_Modeling', 'Config')
boundary_conditions_dir = os.path.join(config_dir, 'Boundary_Conditions')
output_final_dir = os.path.join(project_root, 'Photochemical_Modeling', 'Results', 'Outputs')

# Work base directory for creating temporary simulation folders
work_base_dir = os.path.join(project_root, 'Photochemical_Modeling')

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

    # 4. Stage the lower boundary file using the official VULCAN path.
    bc_source = os.path.join(boundary_conditions_dir, sc['bc_source'])
    bc_target = os.path.join(temp_dir, 'atm', 'BC_bot_Earth.txt')
    if os.path.exists(bc_source):
        shutil.copy2(bc_source, bc_target)
    else:
        print(f"[{run_id}] Warning: Boundary conditions file not found at {bc_source}")

    # 5. Create output structure
    for folder in folders_to_create:
        os.makedirs(os.path.join(temp_dir, folder), exist_ok=True)

    # 6. Launch Simulation Process
    # Command: python -u run_case.py <abs_path_to_yaml>
    # -u: Unbuffered output (useful for logging)
    cmd = [sys.executable, '-u', 'run_case.py', yaml_abs_path]

    # Redirect stdout/stderr to a log file
    log_file_path = os.path.join(temp_dir, f'run_{run_id}.log')
    print(f"[{run_id}] Launching VULCAN... (Log: {log_file_path})")
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

failed_runs = []

for proc in processes:
    proc['log'].close()
    run_id = proc['id']
    temp_dir = proc['dir']
    log_file_path = os.path.join(temp_dir, f'run_{run_id}.log')
    return_code = proc['p'].returncode

    print(f"[{run_id}] Finished with return code {return_code}")

    # 1. Collect Output Files (.vul)
    vul_files = glob.glob(os.path.join(temp_dir, 'output', '*.vul'))
    run_failed = return_code != 0 or not vul_files

    if run_failed:
        failed_runs.append(run_id)
        if return_code == 0 and not vul_files:
            print(f"[{run_id}] ERROR: Process finished but produced no .vul files.")
        elif return_code != 0:
            print(f"[{run_id}] ERROR: VULCAN exited with code {return_code}.")

        log_tail = read_log_tail(log_file_path)
        if log_tail:
            print(f"[{run_id}] Last {LOG_TAIL_LINES} log lines:\n{log_tail}")

        if KEEP_FAILED_TEMP:
            print(f"[{run_id}] Preserving temp directory for debugging: {temp_dir}")
            continue

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

    if KEEP_SUCCESS_TEMP:
        print(f"[{run_id}] Preserving temp directory by EXOFARM_KEEP_TEMP=1: {temp_dir}")
        continue

    # 2. Delete Temporary Directory
    print(f"[{run_id}] Cleaning up temp directory {temp_dir}...")
    try:
        shutil.rmtree(temp_dir)
        print(f"[{run_id}] Temp directory removed.")
    except Exception as e:
        print(f"[{run_id}] Failed to remove temp directory: {e}")

if failed_runs:
    print(f"Parallel execution finished with failures: {', '.join(failed_runs)}")
    sys.exit(1)

print("Parallel execution finished.")
