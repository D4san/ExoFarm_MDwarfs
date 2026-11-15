#!/usr/bin/env python3
"""Select Franck-style crop winners and write a one-year LPJmL land-use map.

The candidate run uses landuse=all_crops and therefore gives every valid CFT a
tiny diagnostic stand. pft_harvestc is a per-stand yield, so the selection is
made from the harvest output itself rather than multiplying by the tiny
diagnostic fraction. The resulting map has one rainfed or surface-irrigated
crop band equal to one in each eligible cell; LPJmL's only_crops mode then
removes the natural/grass fallback and normalizes the crop fractions.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import struct

import numpy as np
from scipy.io import netcdf_file


LANDUSE_MAP = [
    "temperate cereals", "rice", "maize", "tropical cereals", "pulses",
    "temperate roots", "tropical roots", "oil crops sunflower",
    "oil crops soybean", "oil crops groundnut", "oil crops rapeseed",
    "sugarcane", "others", "grassland", "biomass grass", "biomass tree",
]
LANDUSE_HEADER = struct.Struct("<6i3f3i")
LANDUSE_HEADER_SIZE = 7 + 4 + LANDUSE_HEADER.size
CARBON_FRACTION_OF_DRY_BIOMASS = 0.45


def _read_nc(path: Path, variable: str | None = None) -> np.ndarray:
    with netcdf_file(path, mode="r", mmap=False) as ds:
        if variable is None:
            variable = next(
                v for v in ds.variables
                if v not in {"lon", "lat", "time", "time_bnds", "lon_bnds", "lat_bnds"}
            )
        values = np.asarray(ds.variables[variable].data, dtype=np.float64)
    values[~np.isfinite(values)] = np.nan
    values[values < -1e30] = np.nan
    return values


def _decode_names(path: Path) -> list[str]:
    with netcdf_file(path, mode="r", mmap=False) as ds:
        raw = np.asarray(ds.variables["NamePFT"].data)
    return [b"".join(row).decode("ascii", "ignore").strip() for row in raw]


def _load_energy_table(path: Path) -> dict[str, tuple[float, float]]:
    table = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["include_in_franck2011"].strip().lower() != "true":
                continue
            pft = row["lpjml_pft_name"].strip()
            if pft == "managed grassland" or not row["kcal_per_g_moist"].strip():
                continue
            table[pft] = (
                float(row["dry_matter_fraction"]),
                float(row["kcal_per_g_moist"]),
            )
    return table


def _candidate_indices(names: list[str], table: dict[str, tuple[float, float]]) -> list[tuple[int, str, int]]:
    selected = []
    for index, name in enumerate(names):
        parts = name.split(" ", 1)
        if len(parts) != 2 or parts[0] not in {"rainfed", "irrigated"}:
            continue
        crop = parts[1]
        if crop in table and crop in LANDUSE_MAP:
            selected.append((index, parts[0], LANDUSE_MAP.index(crop)))
    if not selected:
        raise ValueError("No eligible annual crop CFTs found in NamePFT")
    return selected


def _write_clm(path: Path, winner_band: np.ndarray, *, firstyear: int, firstcell: int, cellsize: float) -> None:
    ncell, nbands = winner_band.shape
    if nbands != 64:
        raise ValueError(f"Expected 64 land-use bands, got {nbands}")
    header = LANDUSE_HEADER.pack(
        1, firstyear, 1, firstcell, ncell, nbands,
        cellsize, 1.0, cellsize, 3, 1, 1,
    )
    with path.open("wb") as handle:
        handle.write(b"LPJLUSE")
        handle.write(struct.pack("<i", 4))
        handle.write(header)
        for row in np.asarray(winner_band, dtype="<f4"):
            handle.write(row.tobytes(order="C"))
    expected = LANDUSE_HEADER_SIZE + ncell * nbands * 4
    if path.stat().st_size != expected:
        raise IOError(f"CLM size mismatch: {path.stat().st_size} != {expected}")


def _collapse_spatial(values: np.ndarray, spatial_shape: tuple[int, ...], *, label: str) -> np.ndarray:
    """Collapse a leading time axis while preserving the grid dimensions."""
    values = np.asarray(values, dtype=np.float64)
    while values.ndim > len(spatial_shape):
        values = np.nanmean(values, axis=0)
    if values.shape != spatial_shape:
        raise ValueError(f"{label} shape {values.shape} does not match grid {spatial_shape}")
    return values


def _depth_in_meters(path: Path, values: np.ndarray) -> np.ndarray:
    """Convert LPJmL maxthaw_depth sidecar units to metres explicitly."""
    sidecar = path.with_suffix(path.suffix + ".json")
    unit = "mm"
    if sidecar.exists():
        unit = str(json.loads(sidecar.read_text()).get("unit", unit)).lower()
    if unit in {"mm", "millimeter", "millimetre", "millimeters", "millimetres"}:
        return values / 1000.0
    if unit in {"m", "meter", "metre", "meters", "metres"}:
        return values
    raise ValueError(f"Unsupported maxthaw_depth unit {unit!r} in {sidecar}")


def _root_arrays(root: Path, names: list[str], candidates: list[tuple[int, str, int]], table: dict[str, tuple[float, float]]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Read one candidate chunk and return ids, area, thaw, energy and pft names."""
    output = root / "output"
    current_names = _decode_names(output / "pft_harvestc.nc")
    if current_names != names:
        raise ValueError(f"NamePFT differs between candidate roots: {root}")
    grid = _read_nc(output / "grid.nc", "cellid")
    if grid.ndim not in (1, 2):
        raise ValueError(f"Expected 1-D or 2-D grid cell IDs, got {grid.shape} in {root}")
    spatial_shape = grid.shape
    cell_ids = np.rint(grid).astype(np.int64).reshape(-1)
    # LPJmL's local NetCDF grid stores IDs relative to the block.  The sidecar
    # metadata records the global firstcell, so restore global IDs before
    # merging chunks.  If a future global-grid output already stores absolute
    # IDs, its maximum exceeds the local ncell and no offset is applied.
    grid_meta = output / "grid.nc.json"
    if grid_meta.exists():
        meta = json.loads(grid_meta.read_text())
        firstcell = int(meta.get("firstcell", 0))
        local_ncell = int(meta.get("ncell", 0))
        valid_local = cell_ids >= 0
        if firstcell and local_ncell and np.any(valid_local) and int(np.nanmax(cell_ids[valid_local])) < local_ncell:
            cell_ids[valid_local] += firstcell
    harvest = _read_nc(output / "pft_harvestc.nc", "harvestc")
    harvest2 = _read_nc(output / "pft_harvestc2.nc", "harvestc2")
    if harvest.shape != harvest2.shape:
        raise ValueError(f"First- and second-harvest arrays differ in {root}")
    expected_ndim = len(spatial_shape) + 2  # time, pft, spatial grid
    if harvest.ndim == expected_ndim:
        yield_c = np.nanmean(harvest + harvest2, axis=0)
    elif harvest.ndim == len(spatial_shape) + 1:  # already time-collapsed
        yield_c = harvest + harvest2
    else:
        raise ValueError(f"Expected time,pft,grid harvest array, got {harvest.shape} in {root}")
    if yield_c.shape[0] != len(names) or tuple(yield_c.shape[1:]) != spatial_shape:
        raise ValueError(f"Harvest spatial shape {yield_c.shape} does not match grid {spatial_shape} in {root}")
    thaw = _depth_in_meters(
        output / "maxthaw_depth.nc",
        _collapse_spatial(_read_nc(output / "maxthaw_depth.nc"), spatial_shape, label="maxthaw_depth"),
    )
    area = _collapse_spatial(_read_nc(output / "land_area.nc"), spatial_shape, label="land_area")
    energy = np.full((len(candidates), cell_ids.size), np.nan, dtype=np.float64)
    flat_yield = yield_c.reshape(len(names), -1)
    for row, (pft_index, _mode, _crop_index) in enumerate(candidates):
        dry, kcal = table[names[pft_index].split(" ", 1)[1]]
        energy[row] = flat_yield[pft_index] / CARBON_FRACTION_OF_DRY_BIOMASS / dry * kcal
    return cell_ids, area.reshape(-1), thaw.reshape(-1), energy, names


def build_map(potential_roots: list[Path], output_dir: Path, energy_table: Path, *, year: int, thaw_min_m: float, expected_ncell: int | None = None) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    if not potential_roots:
        raise ValueError("At least one candidate root is required")
    first_output = potential_roots[0] / "output"
    names = _decode_names(first_output / "pft_harvestc.nc")
    table = _load_energy_table(energy_table)
    candidates = _candidate_indices(names, table)

    # Chunks all carry LPJmL cell IDs; merge them by ID without retaining all
    # NetCDF arrays in memory.  This also handles a single unchunked root.
    first_grid = _read_nc(first_output / "grid.nc", "cellid")
    first_ids = np.rint(first_grid).astype(np.int64)
    valid_first = first_ids >= 0
    if not np.any(valid_first):
        raise ValueError("Grid contains no valid LPJmL cells")
    ncell = expected_ncell or int(np.nanmax(first_ids[valid_first])) + 1
    if ncell <= 0:
        raise ValueError("Invalid global cell count")
    best_energy = np.full(ncell, np.nan, dtype=np.float64)
    best_row = np.full(ncell, -1, dtype=np.int16)
    area_global = np.full(ncell, np.nan, dtype=np.float64)
    thaw_global = np.full(ncell, np.nan, dtype=np.float64)
    for root in potential_roots:
        cell_ids, area, thaw, energy, _ = _root_arrays(root, names, candidates, table)
        valid = (cell_ids >= 0) & (cell_ids < ncell)
        if not np.any(valid):
            continue
        ids = cell_ids[valid]
        area_values, thaw_values = area[valid], thaw[valid]
        fill_area = np.isnan(area_global[ids]) & np.isfinite(area_values)
        area_global[ids[fill_area]] = area_values[fill_area]
        fill_thaw = np.isnan(thaw_global[ids]) & np.isfinite(thaw_values)
        thaw_global[ids[fill_thaw]] = thaw_values[fill_thaw]
        for row in range(len(candidates)):
            values = energy[row, valid]
            finite = np.isfinite(values)
            if not np.any(finite):
                continue
            candidate_ids = ids[finite]
            candidate_values = values[finite]
            old = best_energy[candidate_ids]
            better = np.isnan(old) | (candidate_values > old)
            best_energy[candidate_ids[better]] = candidate_values[better]
            best_row[candidate_ids[better]] = row

    eligible = np.isfinite(area_global) & (area_global > 0)
    eligible &= np.isfinite(thaw_global) & (thaw_global >= thaw_min_m)
    eligible &= np.isfinite(best_energy) & (best_energy > 0) & (best_row >= 0)
    if not np.any(eligible):
        raise ValueError("No eligible cells have a positive crop yield")

    winner = np.zeros((ncell, 64), dtype=np.float32)
    selected_names = {}
    for cell in np.flatnonzero(eligible):
        row = int(best_row[cell])
        pft_index, mode, crop_index = candidates[row]
        band = crop_index + (16 if mode == "irrigated" else 0)
        winner[cell, band] = 1.0
        selected_names[int(cell)] = {
            "pft": names[pft_index],
            "mode": mode,
            "crop": names[pft_index].split(" ", 1)[1],
            "band": band,
            "energy_kcal_m2_yr": float(best_energy[cell]),
            "thaw_depth_m": float(thaw_global[cell]),
            "land_area_m2": float(area_global[cell]),
        }

    clm = output_dir / f"genghis_khan_crop_only_{year}.clm"
    _write_clm(clm, winner, firstyear=year, firstcell=0, cellsize=0.5)
    meta = {
        "filename": clm.name,
        "variable": "landfrac",
        "global_attrs": {
            "title": "ExoFarm Franck-inspired Genghis Khan crop-only land use",
            "summary": "One winning annual crop per eligible cell; pasture, grassland and biomass bands are zero.",
            "source": [str(root) for root in potential_roots],
        },
        "firstcell": 0, "ncell": ncell, "cellsize_lon": 0.5, "cellsize_lat": 0.5,
        "firstyear": year, "lastyear": year, "nyear": 1, "nstep": 1, "timestep": 1,
        "nbands": 64, "scalar": 1.0, "unit": "1", "datatype": "float", "format": "clm",
        "order": "cellyear", "grid": {"filename": "grid.clm.json", "format": "meta"},
        "version": 4, "offset": LANDUSE_HEADER_SIZE, "bigendian": False,
        # LPJmL expands this 16-entry CFT map to rainfed, surface,
        # sprinkler, and drip irrigation bands.  Repeating the names here
        # would make getmap() infer 64 CFTs and reject the valid 64-band CLM
        # header as if it required 128/256 bands.
        "long_name": (
            "fractions of grid cell for land-use types (rainfed, surface, "
            "sprinkler, and drip irrigation systems)"
        ),
        "map": LANDUSE_MAP,
    }
    (output_dir / f"{clm.name}.json").write_text(json.dumps(meta, indent=2) + "\n")
    counts = {}
    for item in selected_names.values():
        counts[item["pft"]] = counts.get(item["pft"], 0) + 1
    manifest = {
        "scenario": "FR-genghis-khan-crop-only",
        "source_candidate_root": [str(root) for root in potential_roots],
        "selection_years": [1996, 2005],
        "thaw_depth_min_m": thaw_min_m,
        "selection_rule": "max mean 1996-2005 (harvestc + harvestc2) converted to kcal m-2 yr-1",
        "carbon_fraction_of_dry_biomass": CARBON_FRACTION_OF_DRY_BIOMASS,
        "eligible_cells": int(len(selected_names)), "ncell": ncell, "winner_counts": counts,
        "irrigated_band_policy": "surface irrigation band for an irrigated winning CFT; LPJmL irrigation=lim applies water constraint",
        "landuse_file": str(clm), "landuse_sha256": hashlib.sha256(clm.read_bytes()).hexdigest(),
        "map_metadata": str(output_dir / f"{clm.name}.json"), "winner_cells": selected_names,
    }
    (output_dir / "selection_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--potential-root", type=Path, action="append", required=True,
                        help="Candidate root; repeat for sequential chunks")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--energy-table", type=Path, default=Path(__file__).with_name("crop_energy_table.csv"))
    parser.add_argument("--year", type=int, default=2005)
    parser.add_argument("--thaw-depth-min-m", type=float, default=1.0)
    parser.add_argument("--ncell", type=int, default=None,
                        help="Expected global LPJmL cell count (needed for chunked roots)")
    args = parser.parse_args()
    manifest = build_map(args.potential_root, args.output_dir, args.energy_table,
                         year=args.year, thaw_min_m=args.thaw_depth_min_m,
                         expected_ncell=args.ncell)
    print(json.dumps({k: manifest[k] for k in ("scenario", "eligible_cells", "ncell", "winner_counts", "landuse_sha256")}, indent=2))


if __name__ == "__main__":
    main()
