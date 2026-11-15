#!/usr/bin/env python3
"""Validate the completed global LPJmL A1 NetCDF hand-off.

This check is deliberately read-only.  It verifies the temporal and spatial
coverage, variable names, units, masks, finiteness and basic ranges needed
before converting agricultural nitrogen losses into atmospheric boundary
fluxes.  It does not run LPJmL or modify any model product.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.io import netcdf_file


REQUIRED = {
    "land_area.nc": ("land_area", "m2"),
    "cellfrac_agr.nc": ("CELLFRAC_agr", ""),
    "n2o_nit_agr.nc": ("AN2O_NIT_agr", "gN/m2/yr"),
    "n2o_denit_agr.nc": ("AN2O_DENIT_agr", "gN/m2/yr"),
    "nh3_agr.nc": ("ANH3_agr", "gN/m2/yr"),
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
    expected_lower = expected.lower()
    candidates = [
        (name, variable)
        for name, variable in dataset.variables.items()
        if name.lower() == expected_lower
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


def _time_values(dataset: object, dimensions: tuple[str, ...]) -> np.ndarray:
    for dimension in dimensions:
        if dimension.lower() in {"time", "year"} and dimension in dataset.variables:
            return np.asarray(dataset.variables[dimension][:], dtype=float)
    raise ValueError("data variable has no time coordinate")


def validate(output_dir: Path, config_path: Path) -> dict[str, object]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    expected_first = int(config.get("outputyear", 1996))
    expected_last = int(config.get("lastyear", 2005))
    expected_years = np.arange(expected_first, expected_last + 1)
    result: dict[str, object] = {
        "status": "PASS",
        "output_dir": str(output_dir),
        "config": {
            "firstyear": config.get("firstyear"),
            "lastyear": config.get("lastyear"),
            "outputyear": config.get("outputyear"),
            "nspinup": config.get("nspinup"),
            "startgrid": config.get("startgrid"),
            "endgrid": config.get("endgrid"),
        },
        "expected_years": [int(expected_first), int(expected_last)],
        "variables": {},
    }

    arrays: dict[str, np.ndarray] = {}
    spatial_shapes: set[tuple[int, ...]] = set()
    for filename, (expected_name, expected_units) in REQUIRED.items():
        path = output_dir / filename
        if not path.is_file():
            raise FileNotFoundError(path)
        with netcdf_file(path, mode="r", mmap=False) as dataset:
            name, variable = _data_variable(dataset, expected_name)
            units = _text(getattr(variable, "units", ""))
            if units.replace(" ", "") != expected_units.replace(" ", ""):
                raise ValueError(
                    f"{filename}: units {units!r}, expected {expected_units!r}"
                )
            values = _masked(variable)
            times = _time_values(dataset, variable.dimensions)
            if values.ndim < 2 or values.shape[0] != expected_years.size:
                raise ValueError(
                    f"{filename}: shape {values.shape} does not contain "
                    f"{expected_years.size} annual records"
                )
            if times.size != expected_years.size or not np.all(np.isfinite(times)):
                raise ValueError(f"{filename}: invalid time coordinate {times}")
            bounds = np.asarray(dataset.variables["time_bnds"][:], dtype=float)
            if bounds.shape != (expected_years.size, 2):
                raise ValueError(f"{filename}: invalid time_bnds shape {bounds.shape}")
            if not np.all(np.diff(bounds[:, 0]) > 0) or not np.all(bounds[:, 1] > bounds[:, 0]):
                raise ValueError(f"{filename}: non-monotonic time bounds")
            # LPJmL stores the annual midpoint as an integer day (182 rather
            # than 182.5 for the first 365-day interval), so allow the
            # documented sub-day rounding while still checking alignment.
            if not np.allclose(times, bounds.mean(axis=1), atol=1.0):
                raise ValueError(f"{filename}: time is not aligned with time_bnds")
            spatial_shape = tuple(values.shape[1:])
            spatial_shapes.add(spatial_shape)
            arrays[filename] = values
            finite = np.isfinite(values)
            result["variables"][filename] = {
                "variable": name,
                "dimensions": list(variable.dimensions),
                "shape": list(values.shape),
                "units": units,
                "finite_values": int(finite.sum()),
                "masked_values": int((~finite).sum()),
                "min_finite": float(np.nanmin(values)) if finite.any() else None,
                "max_finite": float(np.nanmax(values)) if finite.any() else None,
            }

    if len(spatial_shapes) != 1:
        raise ValueError(f"inconsistent spatial shapes: {sorted(spatial_shapes)}")
    spatial_shape = next(iter(spatial_shapes))
    if spatial_shape != (280, 720):
        raise ValueError(f"unexpected global grid shape {spatial_shape}")

    land = arrays["land_area.nc"]
    agr = arrays["cellfrac_agr.nc"]
    for filename in ("n2o_nit_agr.nc", "n2o_denit_agr.nc", "nh3_agr.nc"):
        values = arrays[filename]
        if not np.isfinite(values).any(axis=(1, 2)).all():
            raise ValueError(f"{filename}: at least one year has no finite cells")
    if np.nanmin(land) < 0:
        raise ValueError("land_area contains negative values")
    if np.nanmin(agr) < 0 or np.nanmax(agr) > 1.0 + 1e-6:
        raise ValueError("cellfrac_agr falls outside [0, 1]")
    grid_path = output_dir / "grid.nc"
    if not grid_path.is_file():
        raise FileNotFoundError(grid_path)
    with netcdf_file(grid_path, mode="r", mmap=False) as grid_dataset:
        _, cellid_variable = _data_variable(grid_dataset, "cellid")
        cellid = np.asarray(cellid_variable[:], dtype=float)
        if cellid.shape != spatial_shape:
            raise ValueError(f"grid.nc cellid shape {cellid.shape} != {spatial_shape}")
    valid_mask = np.isfinite(cellid) & (cellid >= 0)
    valid_cells = int(valid_mask.sum())
    land_finite_cells = int(np.isfinite(land).any(axis=0).sum())
    land_max = np.where(np.isfinite(land), land, -np.inf).max(axis=0)
    land_positive_cells = int((land_max > 0).sum())
    if not np.isfinite(land[:, valid_mask]).any(axis=1).all():
        raise ValueError("land_area has a year without finite values on valid cells")
    for filename, values in arrays.items():
        if filename == "land_area.nc":
            continue
        if values.ndim == 3 and not np.isfinite(values[:, valid_mask]).any(axis=1).all():
            raise ValueError(f"{filename} has a year without finite values on valid cells")
    result["coverage"] = {
        "grid_shape": list(spatial_shape),
        "grid_cells": int(np.prod(spatial_shape)),
        "valid_cellid_cells": valid_cells,
        "land_area_finite_cells": land_finite_cells,
        "land_area_positive_cells": land_positive_cells,
        "expected_lpJml_global_cells": 67420,
        "matches_lpJml_global_cells": valid_cells == 67420,
        "years": [int(year) for year in expected_years],
    }
    if valid_cells != 67420:
        raise ValueError(f"expected 67420 valid land cells, found {valid_cells}")
    result["finiteness"] = {
        "required_flux_years_have_finite_cells": True,
        "all_required_files_checked": True,
    }
    annual_products: list[dict[str, object]] = []
    for path in sorted(output_dir.glob("*.nc")):
        if path.name in REQUIRED or path.name == "grid.nc":
            continue
        with netcdf_file(path, mode="r", mmap=False) as dataset:
            data_candidates = [
                (name, variable)
                for name, variable in dataset.variables.items()
                if len(variable.dimensions) == 3
                and variable.dimensions[0].lower() in {"time", "year"}
            ]
            if len(data_candidates) != 1:
                raise ValueError(
                    f"{path.name}: expected one data variable, found "
                    f"{[name for name, _ in data_candidates]}"
                )
            name, variable = data_candidates[0]
            values = _masked(variable)
            if tuple(values.shape) != (expected_years.size,) + spatial_shape:
                raise ValueError(f"{path.name}: unexpected shape {values.shape}")
            finite_valid = np.isfinite(values[:, valid_mask])
            annual_products.append(
                {
                    "file": path.name,
                    "variable": name,
                    "dimensions": list(variable.dimensions),
                    "shape": list(values.shape),
                    "units": _text(getattr(variable, "units", "")),
                    "finite_valid_values": int(finite_valid.sum()),
                    "expected_finite_valid_values": int(expected_years.size * valid_cells),
                    "all_valid_values_finite": bool(finite_valid.all()),
                }
            )
            if not finite_valid.all():
                raise ValueError(f"{path.name}: non-finite value on a valid cell")
    result["annual_products"] = annual_products
    result["finiteness"]["all_annual_products_checked"] = True
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = validate(args.output_dir.resolve(), args.config.resolve())
    payload = json.dumps(report, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
