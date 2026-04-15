import argparse
from pathlib import Path
import sys

import numpy as np

SIMULATION_ROOT = Path(__file__).resolve().parents[1] / "Simulation"
if str(SIMULATION_ROOT) not in sys.path:
    sys.path.insert(0, str(SIMULATION_ROOT))

from common import (
    atmosphere_output_path,
    get_run,
    list_runs,
    read_atmosphere_output,
    species_columns_from_atmosphere_header,
)


TRANSMISSION_PROFILE_ROOT = Path(__file__).resolve().parents[3] / "Transmission_Spectroscopy" / "profiles"


def export_run(run_id):
    run = get_run(run_id)
    output_path = atmosphere_output_path(run_id)
    header, columns = read_atmosphere_output(output_path)

    species_names = species_columns_from_atmosphere_header(header)
    pressure_bar = columns["press"]
    altitude_km = columns["alt"]
    temperature_k = columns["temp"]

    order = np.argsort(pressure_bar)[::-1]
    pressure_bar = pressure_bar[order]
    altitude_km = altitude_km[order]
    temperature_k = temperature_k[order]

    chem_output = TRANSMISSION_PROFILE_ROOT / f"{run['profile_stem']}_chem.txt"
    pt_output = TRANSMISSION_PROFILE_ROOT / f"{run['profile_stem']}_PT.txt"
    TRANSMISSION_PROFILE_ROOT.mkdir(parents=True, exist_ok=True)

    chem_matrix = np.column_stack([pressure_bar] + [columns[name][order] for name in species_names])
    with chem_output.open("w", encoding="utf-8") as handle:
        handle.write("PRESS " + " ".join(species_names) + "\n")
        np.savetxt(handle, chem_matrix, fmt="%.6e")

    pt_matrix = np.column_stack([altitude_km, pressure_bar, temperature_k])
    with pt_output.open("w", encoding="utf-8") as handle:
        handle.write("ALT P T\n")
        np.savetxt(handle, pt_matrix, fmt="%.6e")

    print(f"Exported {chem_output}")
    print(f"Exported {pt_output}")


def main():
    parser = argparse.ArgumentParser(description="Export photochem outputs to Transmission_Spectroscopy/profiles.")
    parser.add_argument(
        "run_id",
        nargs="?",
        default="all",
        help="Run identifier from Config/catalog.json, or 'all'.",
    )
    args = parser.parse_args()

    if args.run_id == "all":
        run_ids = [run["id"] for run in list_runs()]
    else:
        run_ids = [args.run_id]

    for run_id in run_ids:
        export_run(run_id)


if __name__ == "__main__":
    main()
