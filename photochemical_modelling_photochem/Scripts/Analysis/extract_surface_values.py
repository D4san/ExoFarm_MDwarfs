from pathlib import Path
import sys

SIMULATION_ROOT = Path(__file__).resolve().parents[1] / "Simulation"
if str(SIMULATION_ROOT) not in sys.path:
    sys.path.insert(0, str(SIMULATION_ROOT))

from common import atmosphere_output_path, get_surface_mixing_ratio, list_runs, load_catalog


def main():
    catalog = load_catalog()
    tracked_species = catalog["model"]["tracked_species"]

    star_groups = [
        ("Sun (G2V)", [run for run in list_runs("earth_sun")]),
        ("TRAPPIST-1-like (M8V)", [run for run in list_runs("earth_trappist")]),
    ]

    scenario_order = ["A0", "A1", "A2", "A3"]
    scenario_labels = {
        key: catalog["scenarios"][key]["display_name"]
        for key in scenario_order
    }

    results = {}
    for star_name, runs in star_groups:
        results[star_name] = {}
        for run in runs:
            output_path = atmosphere_output_path(run["id"])
            results[star_name][run["scenario"]] = {
                species: get_surface_mixing_ratio(output_path, species)
                for species in tracked_species
            }

    print("## Surface mixing ratios")
    print("")
    for star_name, _ in star_groups:
        print(f"### {star_name}")
        print("| Species | A0 | A1 | A2 | A3 |")
        print("| :--- | :---: | :---: | :---: | :---: |")
        for species in tracked_species:
            row = [f"| **{species}** |"]
            for scenario in scenario_order:
                value = results[star_name].get(scenario, {}).get(species)
                cell = f"{value:.2e}" if value is not None else "N/A"
                row.append(f" {cell} |")
            print("".join(row))
        print("")

    baseline = results["Sun (G2V)"]["A1"]
    print("## Normalized to Earth A1")
    print("")
    for star_name, _ in star_groups:
        print(f"### {star_name}")
        print("| Species | A0 | A1 | A2 | A3 |")
        print("| :--- | :---: | :---: | :---: | :---: |")
        for species in tracked_species:
            row = [f"| **{species}** |"]
            baseline_value = baseline.get(species)
            for scenario in scenario_order:
                value = results[star_name].get(scenario, {}).get(species)
                if value is None or baseline_value in (None, 0.0):
                    cell = "N/A"
                else:
                    ratio = value / baseline_value
                    if ratio < 0.01 or ratio >= 1000.0:
                        cell = f"{ratio:.2e}x"
                    else:
                        cell = f"{ratio:.2f}x"
                row.append(f" {cell} |")
            print("".join(row))
        print("")

    print("Scenarios:", ", ".join(f"{key}={scenario_labels[key]}" for key in scenario_order))


if __name__ == "__main__":
    main()
