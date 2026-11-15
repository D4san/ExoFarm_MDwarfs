#!/usr/bin/env python3
"""Validate and integrate the global natural A0 LPJmL products.

The A0 control writes monthly nitrogen-mass densities.  This read-only check
validates the ten annual land-area records, 120 monthly flux records, global
mask and units, then sums the months and converts the integrated N mass to
globally averaged molecular fluxes.  It deliberately keeps the natural total
separate from A1 agricultural-stand outputs.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from scipy.io import netcdf_file

from franck2011_core import summarize_global_n_flux


EXPECTED_FILES = {
    "land_area.nc": ("land_area", "m2", 10),
    "n2o_nit.nc": ("n2o_nitrification", "gN/m2/month", 120),
    "n2o_denit.nc": ("n2o_denitrification", "gN/m2/month", 120),
    "n_volatilization.nc": ("N_volatilization", "gN/m2/month", 120),
}


def _text(value: object) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace").strip("\x00")
    return str(value)


def _masked(variable: object) -> np.ndarray:
    raw = np.asarray(variable[:], dtype=float)
    invalid = ~np.isfinite(raw)
    for name in ("_FillValue", "missing_value"):
        if hasattr(variable, name):
            for marker in np.asarray(getattr(variable, name), dtype=float).reshape(-1):
                invalid |= raw == marker
    values = raw.copy()
    values[invalid] = np.nan
    scale = float(getattr(variable, "scale_factor", 1.0))
    offset = float(getattr(variable, "add_offset", 0.0))
    return values * scale + offset


def _data_variable(dataset: object, expected: str) -> tuple[str, object]:
    candidates = [
        (name, variable)
        for name, variable in dataset.variables.items()
        if name.lower() == expected.lower()
    ]
    if not candidates:
        candidates = [
            (name, variable)
            for name, variable in dataset.variables.items()
            if not (len(variable.dimensions) == 1 and variable.dimensions[0] == name)
        ]
    if len(candidates) != 1:
        raise ValueError(
            f"expected one data variable {expected!r}, found "
            f"{[name for name, _ in candidates]}"
        )
    return candidates[0]


def _read(path: Path, expected_name: str, expected_units: str, expected_count: int) -> tuple[np.ndarray, dict[str, object]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with netcdf_file(path, mode="r", mmap=False) as dataset:
        name, variable = _data_variable(dataset, expected_name)
        units = _text(getattr(variable, "units", ""))
        if units.replace(" ", "") != expected_units.replace(" ", ""):
            raise ValueError(f"{path.name}: units {units!r}, expected {expected_units!r}")
        values = _masked(variable)
        if values.ndim != 3 or values.shape[0] != expected_count:
            raise ValueError(f"{path.name}: unexpected shape {values.shape}")
        if tuple(variable.dimensions[1:]) != ("lat", "lon"):
            raise ValueError(f"{path.name}: unexpected dimensions {variable.dimensions}")
        time = np.asarray(dataset.variables["time"][:], dtype=float)
        bounds = np.asarray(dataset.variables["time_bnds"][:], dtype=float)
        if time.shape != (expected_count,) or bounds.shape != (expected_count, 2):
            raise ValueError(f"{path.name}: invalid time metadata")
        if not np.all(np.isfinite(time)) or not np.all(np.isfinite(bounds)):
            raise ValueError(f"{path.name}: non-finite time metadata")
        if not np.all(np.diff(bounds[:, 0]) > 0) or not np.all(bounds[:, 1] > bounds[:, 0]):
            raise ValueError(f"{path.name}: non-monotonic time bounds")
        info = {
            "variable": name,
            "dimensions": list(variable.dimensions),
            "shape": list(values.shape),
            "units": units,
            "time_count": expected_count,
            "finite_values": int(np.isfinite(values).sum()),
            "masked_values": int((~np.isfinite(values)).sum()),
            "min_finite": float(np.nanmin(values)) if np.isfinite(values).any() else None,
            "max_finite": float(np.nanmax(values)) if np.isfinite(values).any() else None,
        }
        return values, info


def validate(output_dir: Path, config_path: Path) -> dict[str, object]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    first_year = int(config.get("outputyear", 1996))
    last_year = int(config.get("lastyear", 2005))
    years = np.arange(first_year, last_year + 1)
    if years.size != 10:
        raise ValueError(f"expected ten output years, found {years.size}")

    grid_path = output_dir / "grid.nc"
    with netcdf_file(grid_path, mode="r", mmap=False) as dataset:
        _, cellid_variable = _data_variable(dataset, "cellid")
        cellid = np.asarray(cellid_variable[:], dtype=float)
    if cellid.shape != (280, 720):
        raise ValueError(f"unexpected grid shape {cellid.shape}")
    valid_mask = np.isfinite(cellid) & (cellid >= 0)
    valid_cells = int(valid_mask.sum())
    if valid_cells != 67420:
        raise ValueError(f"expected 67420 valid cells, found {valid_cells}")

    arrays: dict[str, np.ndarray] = {}
    variables: dict[str, dict[str, object]] = {}
    for filename, (expected_name, units, count) in EXPECTED_FILES.items():
        values, info = _read(output_dir / filename, expected_name, units, count)
        arrays[filename] = values
        variables[filename] = info
        finite_valid = np.isfinite(values[:, valid_mask])
        if not finite_valid.all():
            raise ValueError(f"{filename}: non-finite value on a valid cell")

    land = arrays["land_area.nc"]
    if np.nanmin(land) < 0:
        raise ValueError("land_area contains negative values")
    land_max = np.where(np.isfinite(land), land, -np.inf).max(axis=0)
    positive_cells = int((land_max > 0).sum())

    monthly_n2o = arrays["n2o_nit.nc"] + arrays["n2o_denit.nc"]
    monthly_nh3 = arrays["n_volatilization.nc"]
    annual_n2o_density = monthly_n2o.reshape(years.size, 12, 280, 720).sum(axis=1)
    annual_nh3_density = monthly_nh3.reshape(years.size, 12, 280, 720).sum(axis=1)
    total_n2o_gn = np.nansum(annual_n2o_density * land, axis=(1, 2))
    total_nh3_gn = np.nansum(annual_nh3_density * land, axis=(1, 2))
    if not np.all(np.isfinite(total_n2o_gn)) or not np.all(np.isfinite(total_nh3_gn)):
        raise ValueError("integrated totals contain non-finite values")
    if np.any(total_n2o_gn < 0) or np.any(total_nh3_gn < 0):
        raise ValueError("integrated N totals contain negative values")

    rows: list[dict[str, object]] = []
    for index, year in enumerate(years):
        n2o = summarize_global_n_flux(float(total_n2o_gn[index]), species_n_atoms=2)
        nh3 = summarize_global_n_flux(float(total_nh3_gn[index]), species_n_atoms=1)
        rows.append(
            {
                "year": int(year),
                "n2o_total_gN_yr": float(total_n2o_gn[index]),
                "n2o_total_TgN_yr": n2o.total_tgn_year,
                "n2o_molecules_cm-2_s-1": n2o.molecules_cm2_s,
                "nh3_total_gN_yr": float(total_nh3_gn[index]),
                "nh3_total_TgN_yr": nh3.total_tgn_year,
                "nh3_molecules_cm-2_s-1": nh3.molecules_cm2_s,
            }
        )

    mean_n2o = summarize_global_n_flux(float(np.mean(total_n2o_gn)), species_n_atoms=2)
    mean_nh3 = summarize_global_n_flux(float(np.mean(total_nh3_gn)), species_n_atoms=1)
    return {
        "status": "PASS",
        "output_dir": str(output_dir),
        "config": {
            "firstyear": config.get("firstyear"),
            "outputyear": config.get("outputyear"),
            "lastyear": config.get("lastyear"),
            "nspinup": config.get("nspinup"),
        },
        "coverage": {
            "grid_shape": [280, 720],
            "valid_cellid_cells": valid_cells,
            "land_area_positive_cells": positive_cells,
            "years": [int(years[0]), int(years[-1])],
            "annual_land_area_records": int(land.shape[0]),
            "monthly_flux_records": int(monthly_n2o.shape[0]),
        },
        "variables": variables,
        "finiteness": {
            "all_valid_cells_finite": True,
            "all_integrated_years_finite": True,
        },
        "summary": {
            "mean_n2o_TgN_yr": mean_n2o.total_tgn_year,
            "mean_n2o_molecules_cm-2_s-1": mean_n2o.molecules_cm2_s,
            "mean_nh3_TgN_yr": mean_nh3.total_tgn_year,
            "mean_nh3_molecules_cm-2_s-1": mean_nh3.molecules_cm2_s,
        },
        "timeseries": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--csv", type=Path, required=True)
    args = parser.parse_args()
    result = validate(args.output_dir.resolve(), args.config.resolve())
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    with args.csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["timeseries"][0]))
        writer.writeheader()
        writer.writerows(result["timeseries"])
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
