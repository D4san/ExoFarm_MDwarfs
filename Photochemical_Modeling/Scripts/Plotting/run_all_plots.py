import os
import subprocess
import sys

def run_script(script_name):
    """Runs a python script and handles errors."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '../../..'))
    script_path = os.path.join(script_dir, script_name)
    cwd = project_root if script_name in {
        "plot_agricultural_comparison.py",
        "plot_trappist_comparison.py",
    } else script_dir
    print(f"--- Running {script_name} ---")
    try:
        subprocess.run([sys.executable, script_path], cwd=cwd, check=True)
        print(f"Successfully ran {script_name}\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}:")
        print(e.stderr)
        print("\n")
        return False

def main():
    print("Starting batch plot generation...\n")
    
    scripts = [
        "plot_agricultural_comparison.py",
        "plot_trappist_comparison.py",
        "plot_surface_normalized_bars.py",
        "plot_star_comparison.py",
        "plot_spectra_comparison.py"
    ]
    
    failed = []
    for script in scripts:
        if not run_script(script):
            failed.append(script)
        
    if failed:
        print(f"Plot generation finished with failures: {', '.join(failed)}")
        sys.exit(1)

    print("All plots generated successfully.")

if __name__ == "__main__":
    main()
