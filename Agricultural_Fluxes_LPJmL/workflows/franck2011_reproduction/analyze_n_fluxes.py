#!/usr/bin/env python3
"""Integrate LPJmL agricultural N losses and prepare atmospheric fluxes.

LPJmL's ``*_agr`` outputs are annual nitrogen-mass densities already weighted
by agricultural stand fraction. They must be multiplied by grid-cell land
area, but not by ``cellfrac_agr`` a second time. A one-cell pilot is reported
only as an interface diagnostic; planetary molecule fluxes are emitted only
for a complete global run.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable

import numpy as np
from scipy.io import netcdf_file

from franck2011_core import summarize_global_n_flux


@dataclass(frozen=True)
class NetcdfSeries:
    """One LPJmL variable with enough metadata for safe integration."""

    values: np.ndarray
    dimensions: tuple[str, ...]
    units: str
    time_values: np.ndarray | None
    variable_name: str


VARIABLES = {
    "land_area": ("land_area.nc", ("land_area",), "m2"),
    "cellfrac_agr": ("cellfrac_agr.nc", ("CELLFRAC_agr",), ""),
    "n2o_nit_agr": (
        "n2o_nit_agr.nc",
        ("AN2O_NIT_agr", "n2o_nit_agr"),
        "gN/m2/yr",
    ),
    "n2o_denit_agr": (
        "n2o_denit_agr.nc",
        ("AN2O_DENIT_agr", "n2o_denit_agr"),
        "gN/m2/yr",
    ),
    "nh3_agr": ("nh3_agr.nc", ("ANH3_agr", "nh3_agr"), "gN/m2/yr"),
}


def _decode_attribute(value: object) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace").strip("\x00")
    return str(value)


def _masked_values(variable: object) -> np.ndarray:
    raw = np.asarray(variable[:], dtype=float)
    invalid = ~np.isfinite(raw)
    for name in ("_FillValue", "missing_value"):
        if hasattr(variable, name):
            marker = np.asarray(getattr(variable, name), dtype=float).reshape(-1)
            for value in marker:
                invalid |= raw == value
    values = raw.copy()
    values[invalid] = np.nan
    scale = float(getattr(variable, "scale_factor", 1.0))
    offset = float(getattr(variable, "add_offset", 0.0))
    return values * scale + offset


def _read_series(
    path: Path,
    expected_names: Iterable[str],
    expected_units: str,
) -> NetcdfSeries:
    if not path.is_file():
        raise FileNotFoundError(f"Missing LPJmL output: {path}")

    with netcdf_file(path, mode="r", mmap=False) as dataset:
        expected_lower = {name.lower() for name in expected_names}
        candidates = [
            (name, variable)
            for name, variable in dataset.variables.items()
            if name.lower() in expected_lower
        ]
        if not candidates:
            candidates = [
                (name, variable)
                for name, variable in dataset.variables.items()
                if not (
                    len(variable.dimensions) == 1
                    and variable.dimensions[0] == name
                )
            ]
        if len(candidates) != 1:
            names = ", ".join(name for name, _ in candidates) or "none"
            raise ValueError(
                f"Could not identify one data variable in {path}; candidates: {names}"
            )

        variable_name, variable = candidates[0]
        units = _decode_attribute(getattr(variable, "units", ""))
        if expected_units and units.replace(" ", "") != expected_units.replace(" ", ""):
            raise ValueError(
                f"Unexpected units for {variable_name} in {path}: "
                f"{units!r}, expected {expected_units!r}"
            )

        time_values = None
        for dimension in variable.dimensions:
            if dimension.lower() in {"time", "year"} and dimension in dataset.variables:
                time_values = np.asarray(dataset.variables[dimension][:], dtype=float)
                break

        return NetcdfSeries(
            values=_masked_values(variable),
            dimensions=tuple(variable.dimensions),
            units=units,
            time_values=time_values,
            variable_name=variable_name,
        )


def _time_by_space(series: NetcdfSeries) -> np.ndarray:
    """Normalize a scalar/spatial/annual array to ``(time, space)``."""

    values = np.asarray(series.values, dtype=float)
    time_axes = [
        index
        for index, name in enumerate(series.dimensions)
        if name.lower() in {"time", "year"}
    ]
    if len(time_axes) > 1:
        raise ValueError(f"Multiple time axes in {series.variable_name}")
    if time_axes:
        values = np.moveaxis(values, time_axes[0], 0)
    else:
        values = values.reshape((1,) + values.shape)
    return values.reshape(values.shape[0], -1)


def _broadcast_area(area: np.ndarray, target: np.ndarray) -> np.ndarray:
    if area.shape[1] != target.shape[1]:
        raise ValueError(
            f"Land-area cells {area.shape[1]} do not match flux cells "
            f"{target.shape[1]}"
        )
    if area.shape[0] == 1:
        return np.broadcast_to(area, target.shape)
    if area.shape[0] != target.shape[0]:
        raise ValueError(
            f"Land-area timesteps {area.shape[0]} do not match flux timesteps "
            f"{target.shape[0]}"
        )
    return area


def integrate_density(flux: np.ndarray, land_area: np.ndarray) -> np.ndarray:
    """Integrate ``gN m-2 yr-1`` over cell land area to ``gN yr-1``."""

    if flux.shape != land_area.shape:
        raise ValueError("Flux and broadcast land-area arrays must have equal shapes")
    product = flux * land_area
    if np.any(np.all(~np.isfinite(product), axis=1)):
        raise ValueError("At least one timestep has no finite flux-area products")
    return np.nansum(product, axis=1)


def _years(series: NetcdfSeries, first_year: int, count: int) -> tuple[np.ndarray, str]:
    if series.time_values is not None and series.time_values.size == count:
        values = np.asarray(series.time_values, dtype=float)
        if np.all(np.isfinite(values)) and np.nanmin(values) >= 1000:
            return np.rint(values).astype(int), "netcdf_time_coordinate"
    return np.arange(first_year, first_year + count), "configured_first_year"


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Scenario output directory containing the LPJmL NetCDF files.",
    )
    parser.add_argument(
        "--coverage",
        choices=("pilot", "global"),
        required=True,
        help="Planetary molecule fluxes are produced only for global coverage.",
    )
    parser.add_argument("--first-year", type=int, default=1996)
    parser.add_argument(
        "--summary-dir",
        type=Path,
        help="Destination; defaults to <output-dir>/analysis.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    output_dir = args.output_dir.resolve()
    summary_dir = (
        args.summary_dir.resolve()
        if args.summary_dir is not None
        else output_dir / "analysis"
    )

    loaded = {}
    for key, (filename, names, units) in VARIABLES.items():
        loaded[key] = _read_series(output_dir / filename, names, units)

    flux_arrays = {
        key: _time_by_space(loaded[key])
        for key in ("n2o_nit_agr", "n2o_denit_agr", "nh3_agr")
    }
    shapes = {array.shape for array in flux_arrays.values()}
    if len(shapes) != 1:
        raise ValueError(f"N-flux output shapes do not agree: {sorted(shapes)}")

    template = flux_arrays["nh3_agr"]
    land_area = _broadcast_area(_time_by_space(loaded["land_area"]), template)
    agricultural_fraction = _time_by_space(loaded["cellfrac_agr"])
    if agricultural_fraction.shape[0] == 1:
        agricultural_fraction = np.broadcast_to(
            agricultural_fraction, template.shape
        )
    if agricultural_fraction.shape != template.shape:
        raise ValueError("Agricultural-fraction shape does not match N outputs")

    total_land_area = np.nansum(land_area, axis=1)
    represented_agricultural_area = np.nansum(
        agricultural_fraction * land_area,
        axis=1,
    )
    n2o_nit_gn_year = integrate_density(flux_arrays["n2o_nit_agr"], land_area)
    n2o_denit_gn_year = integrate_density(
        flux_arrays["n2o_denit_agr"], land_area
    )
    n2o_gn_year = n2o_nit_gn_year + n2o_denit_gn_year
    nh3_gn_year = integrate_density(flux_arrays["nh3_agr"], land_area)
    years, year_source = _years(
        loaded["nh3_agr"], args.first_year, template.shape[0]
    )

    rows: list[dict[str, object]] = []
    for index, year in enumerate(years):
        row: dict[str, object] = {
            "year": int(year),
            "represented_land_area_m2": f"{total_land_area[index]:.12e}",
            "represented_agricultural_area_m2": (
                f"{represented_agricultural_area[index]:.12e}"
            ),
            "n2o_nit_tgN_yr": f"{n2o_nit_gn_year[index] / 1.0e12:.12e}",
            "n2o_denit_tgN_yr": f"{n2o_denit_gn_year[index] / 1.0e12:.12e}",
            "n2o_total_tgN_yr": f"{n2o_gn_year[index] / 1.0e12:.12e}",
            "nh3_tgN_yr": f"{nh3_gn_year[index] / 1.0e12:.12e}",
            "n2o_molecules_cm-2_s-1": "",
            "nh3_molecules_cm-2_s-1": "",
        }
        if args.coverage == "global":
            n2o_molecules = summarize_global_n_flux(
                n2o_gn_year[index], species_n_atoms=2
            ).molecules_cm2_s
            nh3_molecules = summarize_global_n_flux(
                nh3_gn_year[index], species_n_atoms=1
            ).molecules_cm2_s
            row["n2o_molecules_cm-2_s-1"] = (
                f"{n2o_molecules:.12e}"
            )
            row["nh3_molecules_cm-2_s-1"] = (
                f"{nh3_molecules:.12e}"
            )
        rows.append(row)

    summary_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(summary_dir / "nitrogen_flux_timeseries.csv", rows)
    mean_n2o_gn_year = float(np.mean(n2o_gn_year))
    mean_nh3_gn_year = float(np.mean(nh3_gn_year))
    summary = {
        "coverage": args.coverage,
        "scientific_status": (
            "interface_smoke_test_not_for_planetary_interpretation"
            if args.coverage == "pilot"
            else "global_integration_requires_campaign_acceptance"
        ),
        "year_source": year_source,
        "years": [int(years[0]), int(years[-1])],
        "n_years": int(len(years)),
        "mean_n2o_tgN_yr": mean_n2o_gn_year / 1.0e12,
        "mean_nh3_tgN_yr": mean_nh3_gn_year / 1.0e12,
        "mean_n2o_molecules_cm-2_s-1": None,
        "mean_nh3_molecules_cm-2_s-1": None,
        "source_units": "gN/m2/yr",
        "integration_note": (
            "Agricultural outputs already include stand-fraction weighting; "
            "they were multiplied by land_area but not by cellfrac_agr again."
        ),
        "files": {key: VARIABLES[key][0] for key in VARIABLES},
    }
    if args.coverage == "global":
        summary["mean_n2o_molecules_cm-2_s-1"] = summarize_global_n_flux(
            mean_n2o_gn_year, species_n_atoms=2
        ).molecules_cm2_s
        summary["mean_nh3_molecules_cm-2_s-1"] = summarize_global_n_flux(
            mean_nh3_gn_year, species_n_atoms=1
        ).molecules_cm2_s

    (summary_dir / "nitrogen_flux_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    print(summary_dir)


if __name__ == "__main__":
    main()
