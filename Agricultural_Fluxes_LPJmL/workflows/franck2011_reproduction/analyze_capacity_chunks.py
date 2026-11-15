#!/usr/bin/env python3
"""Integrate N and methane outputs from sequential LPJmL cell blocks.

Each block is a local NetCDF grid, so the analysis sums cell-area-weighted
densities across roots instead of concatenating latitude/longitude arrays.
The script keeps LPJmL's native CH4 units explicit: most diagnostics are
``gCH4 m-2 month-1`` while ``ch4_emissions_wet`` is ``gC m-2 month-1``.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from analyze_n_fluxes import (
    VARIABLES,
    _broadcast_area,
    _read_series,
    _time_by_space,
    _write_csv,
    integrate_density,
)
from franck2011_core import summarize_global_n_flux
from scipy.io import netcdf_file


CH4_VARIABLES = (
    "ch4_agr",
    "ch4_rice_em",
    "ch4_grassland",
    "ch4_emissions_wet",
    "ch4_emissions",
    "ch4_oxidation",
    "ch4_sink",
    "ch4_litter",
    "ch4_ebullition",
    "ch4_plant_gas",
)


def _decode(value: object) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace").strip("\x00")
    return str(value)


def _masked(variable: object) -> np.ndarray:
    raw = np.asarray(variable[:], dtype=float)
    invalid = ~np.isfinite(raw)
    for name in ("_FillValue", "missing_value"):
        if hasattr(variable, name):
            for value in np.asarray(getattr(variable, name), dtype=float).reshape(-1):
                invalid |= raw == value
    values = raw.copy()
    values[invalid] = np.nan
    return values * float(getattr(variable, "scale_factor", 1.0)) + float(getattr(variable, "add_offset", 0.0))


def _read_ch4(path: Path) -> tuple[np.ndarray, tuple[str, ...], str, np.ndarray | None]:
    with netcdf_file(path, mode="r", mmap=False) as dataset:
        data_vars = [
            (name, variable)
            for name, variable in dataset.variables.items()
            if not (len(variable.dimensions) == 1 and variable.dimensions[0] == name)
        ]
        if len(data_vars) != 1:
            raise ValueError(f"Could not identify CH4 variable in {path}")
        _, variable = data_vars[0]
        time_values = None
        for dimension in variable.dimensions:
            if dimension.lower() in {"time", "month", "year"} and dimension in dataset.variables:
                time_values = np.asarray(dataset.variables[dimension][:], dtype=float)
                break
        return _masked(variable), tuple(variable.dimensions), _decode(getattr(variable, "units", "")), time_values


def _time_space(values: np.ndarray, dimensions: tuple[str, ...]) -> np.ndarray:
    axes = [i for i, name in enumerate(dimensions) if name.lower() in {"time", "month", "year"}]
    if len(axes) > 1:
        raise ValueError(f"Multiple temporal dimensions: {dimensions}")
    if axes:
        values = np.moveaxis(values, axes[0], 0)
    else:
        values = values.reshape((1,) + values.shape)
    return values.reshape(values.shape[0], -1)


def _load_n(root: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    loaded = {
        key: _read_series(root / filename, names, units)
        for key, (filename, names, units) in VARIABLES.items()
    }
    fluxes = {key: _time_by_space(loaded[key]) for key in ("n2o_nit_agr", "n2o_denit_agr", "nh3_agr")}
    template = fluxes["nh3_agr"]
    area = _broadcast_area(_time_by_space(loaded["land_area"]), template)
    frac = _time_by_space(loaded["cellfrac_agr"])
    if frac.shape[0] == 1:
        frac = np.broadcast_to(frac, template.shape)
    if frac.shape != template.shape:
        raise ValueError(f"Agricultural fraction does not match N outputs in {root}")
    n2o = integrate_density(fluxes["n2o_nit_agr"], area) + integrate_density(fluxes["n2o_denit_agr"], area)
    nh3 = integrate_density(fluxes["nh3_agr"], area)
    represented_area = np.nansum(frac * area, axis=1)
    return n2o, nh3, np.nansum(area, axis=1), represented_area


def _load_ch4(root: Path) -> dict[str, tuple[np.ndarray, str, np.ndarray | None]]:
    output = root
    result = {}
    for name in CH4_VARIABLES:
        values, dims, units, time_values = _read_ch4(output / f"{name}.nc")
        result[name] = (_time_space(values, dims), units, time_values)
    return result


def _write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    if rows:
        _write_csv(path, rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, action="append", required=True,
                        help="Managed chunk output directory; repeat for all chunks")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--first-year", type=int, default=1996)
    args = parser.parse_args()
    roots = [root.resolve() for root in args.output_root]
    summary_dir = args.output_dir.resolve()
    summary_dir.mkdir(parents=True, exist_ok=True)

    n2o_total = nh3_total = area_total = agr_area_total = None
    ch4_totals: dict[str, np.ndarray] = {}
    ch4_units: dict[str, str] = {}
    n_years = None
    for root in roots:
        n2o, nh3, area, agr_area = _load_n(root)
        if n2o_total is None:
            n2o_total, nh3_total, area_total, agr_area_total = map(np.array, (n2o, nh3, area, agr_area))
            n_years = len(n2o)
        elif len(n2o) != n_years:
            raise ValueError(f"N year count differs in {root}")
        else:
            n2o_total += n2o; nh3_total += nh3; area_total += area; agr_area_total += agr_area

        for name, (values, units, _time_values) in _load_ch4(root).items():
            if name not in ch4_totals:
                ch4_totals[name] = np.nansum(values, axis=1)
                ch4_units[name] = units
            else:
                if ch4_totals[name].shape != (values.shape[0],):
                    raise ValueError(f"CH4 time dimension differs in {root}/{name}")
                ch4_totals[name] += np.nansum(values, axis=1)

    years = np.arange(args.first_year, args.first_year + int(n_years))
    n_rows = []
    for i, year in enumerate(years):
        n_rows.append({
            "year": int(year),
            "represented_land_area_m2": f"{area_total[i]:.12e}",
            "represented_agricultural_area_m2": f"{agr_area_total[i]:.12e}",
            "n2o_total_tgN_yr": f"{n2o_total[i] / 1.0e12:.12e}",
            "nh3_tgN_yr": f"{nh3_total[i] / 1.0e12:.12e}",
            "n2o_molecules_cm-2_s-1": f"{summarize_global_n_flux(n2o_total[i], species_n_atoms=2).molecules_cm2_s:.12e}",
            "nh3_molecules_cm-2_s-1": f"{summarize_global_n_flux(nh3_total[i], species_n_atoms=1).molecules_cm2_s:.12e}",
        })
    _write_rows(summary_dir / "nitrogen_flux_timeseries.csv", n_rows)

    methane_rows = []
    methane_annual_rows = []
    for name, totals in ch4_totals.items():
        if totals.size % 12:
            raise ValueError(f"CH4 output for {name} does not contain complete years")
        for index, value in enumerate(totals):
            year = args.first_year + index // 12
            methane_rows.append({"variable": name, "year": year, "month": index % 12 + 1,
                                 "integrated_native_mass": f"{value:.12e}", "native_units": ch4_units[name]})
        for year_index, year in enumerate(years):
            value = float(np.nansum(totals[year_index * 12:(year_index + 1) * 12]))
            methane_annual_rows.append({"variable": name, "year": int(year),
                                        "integrated_native_mass": f"{value:.12e}", "native_units": ch4_units[name]})
    _write_rows(summary_dir / "methane_flux_monthly.csv", methane_rows)
    _write_rows(summary_dir / "methane_flux_annual.csv", methane_annual_rows)

    summary = {
        "roots": [str(root) for root in roots],
        "n_years": int(n_years),
        "years": [int(years[0]), int(years[-1])],
        "mean_n2o_tgN_yr": float(np.mean(n2o_total) / 1.0e12),
        "mean_nh3_tgN_yr": float(np.mean(nh3_total) / 1.0e12),
        "mean_n2o_molecules_cm-2_s-1": float(summarize_global_n_flux(float(np.mean(n2o_total)), species_n_atoms=2).molecules_cm2_s),
        "mean_nh3_molecules_cm-2_s-1": float(summarize_global_n_flux(float(np.mean(nh3_total)), species_n_atoms=1).molecules_cm2_s),
        "ch4_variables": {name: ch4_units[name] for name in sorted(ch4_units)},
        "routing_note": "Managed chunks disable river_routing and reservoir because local NetCDF blocks cannot reconstruct the global neighbour graph.",
    }
    (summary_dir / "capacity_flux_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
