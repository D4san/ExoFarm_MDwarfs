"""Export VULCAN .vul outputs into POSEIDON profile text files.

The spectroscopy notebooks read two files per scenario:

- ``<label>_PT.txt`` with altitude, pressure (bar), and temperature (K)
- ``<label>_chem.txt`` with pressure (bar) and species mixing ratios

This script makes that hand-off reproducible from the photochemical outputs.
"""

from __future__ import annotations

import argparse
import pickle
import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PHOTOCHEM_OUTPUTS = PROJECT_ROOT / "Photochemical_Modeling" / "Results" / "Outputs"
TRANSMISSION_ROOT = PROJECT_ROOT / "Transmission_Spectroscopy"
PROFILE_DIR = TRANSMISSION_ROOT / "profiles"
VULCAN_HANDOFF_DIR = TRANSMISSION_ROOT / "vulcan_outputs"


def export_one(vul_path: Path, profile_dir: Path, copy_dir: Path | None) -> None:
    with vul_path.open("rb") as handle:
        data = pickle.load(handle)

    label = vul_path.stem
    atm = data["atm"]
    variable = data["variable"]

    pressure_bar = atm["pco"] / 1.0e6
    temperature = atm["Tco"]
    altitude_km = atm["zco"][:-1] / 1.0e5
    species = list(variable["species"])
    ymix = variable["ymix"]

    if len(pressure_bar) != len(temperature) or len(pressure_bar) != ymix.shape[0]:
        raise ValueError(f"Unexpected vertical-grid shape in {vul_path}")

    if ymix.shape[1] != len(species):
        raise ValueError(f"Species count mismatch in {vul_path}")

    profile_dir.mkdir(parents=True, exist_ok=True)

    pt_path = profile_dir / f"{label}_PT.txt"
    with pt_path.open("w", encoding="ascii", newline="\n") as handle:
        handle.write("ALT P T\n")
        for altitude, pressure, temp in zip(altitude_km, pressure_bar, temperature):
            handle.write(f"{altitude:.6e} {pressure:.6e} {temp:.6e}\n")

    chem_path = profile_dir / f"{label}_chem.txt"
    with chem_path.open("w", encoding="ascii", newline="\n") as handle:
        handle.write("PRESS " + " ".join(species) + "\n")
        for pressure, row in zip(pressure_bar, ymix):
            values = " ".join(f"{value:.6e}" for value in row)
            handle.write(f"{pressure:.6e} {values}\n")

    if copy_dir is not None:
        copy_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(vul_path, copy_dir / vul_path.name)

    print(f"Exported {label}: {pt_path.name}, {chem_path.name}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=PHOTOCHEM_OUTPUTS,
        help="Directory containing VULCAN .vul outputs.",
    )
    parser.add_argument(
        "--profile-dir",
        type=Path,
        default=PROFILE_DIR,
        help="Destination directory for PT/chem profile text files.",
    )
    parser.add_argument(
        "--copy-vulcan-dir",
        type=Path,
        default=VULCAN_HANDOFF_DIR,
        help="Optional destination for copying the raw .vul hand-off files.",
    )
    parser.add_argument(
        "--pattern",
        default="*.vul",
        help="Glob pattern for selecting .vul files from source-dir.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    vul_files = sorted(args.source_dir.glob(args.pattern))

    if not vul_files:
        raise FileNotFoundError(f"No .vul files found in {args.source_dir}")

    for vul_path in vul_files:
        export_one(vul_path, args.profile_dir, args.copy_vulcan_dir)


if __name__ == "__main__":
    main()
