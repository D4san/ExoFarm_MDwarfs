import os
import subprocess
import sys

def run_script(script_name):
    """Runs a python script and handles errors."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, script_name)
    print(f"--- Running {script_name} ---")
    try:
        result = subprocess.run([sys.executable, script_path], cwd=script_dir, check=True, capture_output=True, text=True)
        print(result.stdout)
        print(f"Successfully ran {script_name}\n")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}:")
        print(e.stderr)
        print("\n")

def main():
    print("Starting batch plot generation...\n")
    
    scripts = [
        "plot_agricultural_comparison.py",
        "plot_trappist_comparison.py",
        "plot_surface_normalized_bars.py",
        "plot_star_comparison.py",
        "plot_spectra_comparison.py"
    ]
    
    for script in scripts:
        run_script(script)
        
    print("All plots generated successfully.")

if __name__ == "__main__":
    main()
