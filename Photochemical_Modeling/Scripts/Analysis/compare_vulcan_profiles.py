"""Compare two directories of VULCAN products with matching filenames."""

from __future__ import annotations

import argparse
import csv
import pickle
from pathlib import Path

import numpy as np


DEFAULT_SPECIES = ("N2O", "NH3", "O3", "CH4", "H2SO4")


def load_vulcan(path: Path) -> dict:
    with path.open("rb") as handle:
        return pickle.load(handle)


def compare_product(old_path: Path, new_path: Path, species_names: tuple[str, ...]) -> list[dict]:
    old = load_vulcan(old_path)
    new = load_vulcan(new_path)
    old_variable = old["variable"]
    new_variable = new["variable"]
    old_ymix = np.asarray(old_variable["ymix"])
    new_ymix = np.asarray(new_variable["ymix"])
    species = list(old_variable["species"])

    if species != list(new_variable["species"]) or old_ymix.shape != new_ymix.shape:
        raise ValueError(f"Incompatible VULCAN products: {old_path} and {new_path}")

    relative_change = np.abs(new_ymix - old_ymix) / np.maximum(np.abs(old_ymix), 1.0e-30)
    rows = []
    for species_name in species_names:
        species_index = species.index(species_name)
        rows.append(
            {
                "file": old_path.name,
                "species": species_name,
                "old_end_case": old["parameter"]["end_case"],
                "new_end_case": new["parameter"]["end_case"],
                "old_count": old["parameter"]["count"],
                "new_count": new["parameter"]["count"],
                "old_longdy": old_variable["longdy"],
                "new_longdy": new_variable["longdy"],
                "surface_relative_change": relative_change[0, species_index],
                "maximum_profile_relative_change": np.max(relative_change[:, species_index]),
            }
        )
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("old_dir", type=Path)
    parser.add_argument("new_dir", type=Path)
    parser.add_argument("output_csv", type=Path)
    parser.add_argument("--species", nargs="+", default=DEFAULT_SPECIES)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = []
    for old_path in sorted(args.old_dir.glob("*.vul")):
        new_path = args.new_dir / old_path.name
        if new_path.exists():
            rows.extend(compare_product(old_path, new_path, tuple(args.species)))
        else:
            print(f"Missing comparison product: {new_path}")

    if not rows:
        raise FileNotFoundError("No matching VULCAN products were found")

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", newline="", encoding="ascii") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} comparison rows to {args.output_csv}")


if __name__ == "__main__":
    main()
