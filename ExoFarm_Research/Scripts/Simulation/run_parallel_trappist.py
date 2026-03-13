"""
Script to run parallel VULCAN simulations for TRAPPIST-1e scenarios.

This script manages the execution of multiple VULCAN simulations in parallel.
It performs the following steps for each scenario:
1. Creates a temporary working directory (e.g., temp_run_Trappist_A0).
2. Copies necessary VULCAN source code and data files (atm, thermo, fastchem) to the temp directory.
3. Stages the scenario-specific lower boundary file as atm/BC_bot_Earth.txt.
4. Generates a VULCAN configuration file from the specified YAML input.
5. Runs the simulation using `run_case.py`.
6. Moves the final output (.vul file) to the Results/Outputs directory.
7. Cleans up (deletes) the temporary directory.

Usage:
    python run_parallel_trappist.py
"""

import os
import shutil
import subprocess
import time
import glob
import sys
from collections import deque


# =============================================================================
# 1. Configuration and Path Setup
# =============================================================================

# Get absolute paths to key directories
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '../../../'))
vulcan_dir = os.path.join(project_root, 'VULCAN')
config_dir = os.path.join(project_root, 'ExoFarm_Research', 'Config')
boundary_conditions_dir = os.path.join(config_dir, 'Boundary_Conditions')
output_final_dir = os.path.join(project_root, 'ExoFarm_Research', 'Results', 'Outputs')

# Base directory for temporary simulation folders
work_base_dir = os.path.join(project_root, 'ExoFarm_Research')

# Ensure output directory exists
if not os.path.exists(output_final_dir):
    os.makedirs(output_final_dir)
    print(f"Created output directory: {output_final_dir}")

# Define scenarios to run
# Each scenario has a unique ID, a relative path to its configuration file,
# and a BC template staged to atm/BC_bot_Earth.txt.
scenarios = [
    {'id': 'Trappist_A0', 'config': 'planets/earth_trappist/input_earth_trappist_A0.yml', 'bc_source': 'bc_earth_preagri_full.txt'},
    {'id': 'Trappist_A1', 'config': 'planets/earth_trappist/input_earth_trappist_A1.yml', 'bc_source': 'bc_earth_current_full.txt'},
    {'id': 'Trappist_A2', 'config': 'planets/earth_trappist/input_earth_trappist_A2.yml', 'bc_source': 'bc_earth_exofarm_moderate_full.txt'},
    {'id': 'Trappist_A3', 'config': 'planets/earth_trappist/input_earth_trappist_A3.yml', 'bc_source': 'bc_earth_exofarm_full.txt'}
]

# FOR TESTING: Uncomment the following line to run only the first scenario
# scenarios = scenarios[:1]

# Keep failed temp directories so the logs and staged VULCAN workspace
# are still available for debugging. Successful runs are cleaned up.
KEEP_FAILED_TEMP = True
LOG_TAIL_LINES = 80


def read_log_tail(log_path, max_lines=LOG_TAIL_LINES):
    """Return the last max_lines lines from a log file as a string."""
    if not os.path.exists(log_path):
        return ''

    with open(log_path, 'r', encoding='utf-8', errors='replace') as handle:
        return ''.join(deque(handle, maxlen=max_lines))


# =============================================================================
# 2. Simulation Execution
# =============================================================================

processes = []

print(f"Starting parallel execution of {len(scenarios)} TRAPPIST-1e scenarios...")
print(f"VULCAN source: {vulcan_dir}")
print(f"Working base: {work_base_dir}")

for sc in scenarios:
    run_id = sc['id']
    config_rel_path = sc['config']
    config_abs_path = os.path.join(config_dir, config_rel_path)

    # Define temporary directory path
    temp_dir = os.path.join(work_base_dir, f'temp_run_{run_id}')

    # Clean up any existing temp directory
    if os.path.exists(temp_dir):
        print(f"[{run_id}] Cleaning existing temp dir: {temp_dir}")
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    print(f"[{run_id}] Setting up in {temp_dir}...")

    # -------------------------------------------------------------------------
    # Copy VULCAN Source Code
    # -------------------------------------------------------------------------

    # Copy all .py files from VULCAN root
    py_files = glob.glob(os.path.join(vulcan_dir, '*.py'))
    for file in py_files:
        try:
            shutil.copy(file, temp_dir)
        except Exception as e:
            print(f"[{run_id}] Error copying {file}: {e}")

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

    # Copy data folders: atm, thermo, fastchem_vulcan
    vulcan_folders_to_copy = ['atm', 'thermo', 'fastchem_vulcan']
    for folder in vulcan_folders_to_copy:
        src = os.path.join(vulcan_dir, folder)
        dst = os.path.join(temp_dir, folder)
        if os.path.exists(src):
            shutil.copytree(src, dst)
        else:
            print(f"[{run_id}] Warning: Folder {folder} not found in VULCAN dir.")

    # -------------------------------------------------------------------------
    # Stage Boundary Conditions
    # -------------------------------------------------------------------------

    bc_source = os.path.join(boundary_conditions_dir, sc['bc_source'])
    bc_target = os.path.join(temp_dir, 'atm', 'BC_bot_Earth.txt')
    if os.path.exists(bc_source):
        shutil.copy2(bc_source, bc_target)
    else:
        print(f"[{run_id}] Warning: Boundary conditions file not found at {bc_source}")

    # Create output directories within the temp folder
    os.makedirs(os.path.join(temp_dir, 'output'), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, 'plot'), exist_ok=True)

    # -------------------------------------------------------------------------
    # Launch Process
    # -------------------------------------------------------------------------

    # Command to run: python run_case.py <config_file>
    # We pass the absolute path of the YAML file
    cmd = [sys.executable, '-u', 'run_case.py', config_abs_path]

    # Open log file to capture stdout/stderr
    log_file_path = os.path.join(temp_dir, f'{run_id}.log')
    log_file = open(log_file_path, 'w')

    print(f"[{run_id}] Launching VULCAN... (Log: {log_file_path})")

    # Start the subprocess non-blocking
    p = subprocess.Popen(cmd, cwd=temp_dir, stdout=log_file, stderr=subprocess.STDOUT)

    processes.append({
        'id': run_id,
        'p': p,
        'log': log_file,
        'dir': temp_dir
    })

print("All processes launched. Waiting for completion...")


# =============================================================================
# 3. Monitoring and Cleanup
# =============================================================================

# Wait for all processes to finish
for proc in processes:
    proc['p'].wait()
    print(f"[{proc['id']}] Finished with return code {proc['p'].returncode}")
    # Close the log file
    proc['log'].close()

print("All runs completed.")

# Collect outputs and clean up
failed_runs = []

for proc in processes:
    run_id = proc['id']
    temp_dir = proc['dir']
    log_file_path = os.path.join(temp_dir, f'{run_id}.log')
    return_code = proc['p'].returncode

    # -------------------------------------------------------------------------
    # Move Output Files
    # -------------------------------------------------------------------------

    # Find .vul files in temp_dir/output
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

    # -------------------------------------------------------------------------
    # Remove Temporary Directory
    # -------------------------------------------------------------------------

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
