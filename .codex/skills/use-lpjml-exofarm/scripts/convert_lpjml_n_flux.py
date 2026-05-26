#!/usr/bin/env python3
"""Convert LPJmL nitrogen-mass fluxes to atmospheric molecule fluxes."""

from __future__ import annotations

import argparse
from dataclasses import dataclass

AVOGADRO = 6.02214076e23
MOLAR_MASS_N_G_MOL = 14.0067
SECONDS_PER_DAY = 86400.0
SECONDS_PER_YEAR = 365.25 * SECONDS_PER_DAY
CM2_PER_M2 = 1.0e4

N_ATOMS = {
    "N": 1,
    "NH3": 1,
    "NO": 1,
    "NO2": 1,
    "N2": 2,
    "N2O": 2,
}


@dataclass(frozen=True)
class ConversionResult:
    source_gn_m2_s: float
    molecules_cm2_s: float


def _period_seconds(unit: str, period_days: float | None) -> float:
    if unit.endswith("_s"):
        return 1.0
    if unit.endswith("_day"):
        return SECONDS_PER_DAY
    if unit.endswith("_month"):
        days = period_days if period_days is not None else 365.25 / 12.0
        return days * SECONDS_PER_DAY
    if unit.endswith("_yr") or unit.endswith("_year"):
        days = period_days if period_days is not None else 365.25
        return days * SECONDS_PER_DAY
    raise ValueError(f"Cannot infer period from unit: {unit}")


def value_to_gn_m2_s(
    value: float,
    unit: str,
    *,
    area_m2: float | None = None,
    period_days: float | None = None,
) -> float:
    """Return grams of N per m2 per second."""

    unit = unit.strip()

    if unit.startswith("gN_m2_"):
        return value / _period_seconds(unit, period_days)

    if unit.startswith("kgN_ha_"):
        grams_n_per_m2 = value * 1000.0 / 10000.0
        return grams_n_per_m2 / _period_seconds(unit, period_days)

    if unit.startswith("TgN_global_"):
        if area_m2 is None:
            raise ValueError("--area-m2 is required for global TgN units")
        grams_n_per_m2 = value * 1.0e12 / area_m2
        return grams_n_per_m2 / _period_seconds(unit, period_days)

    raise ValueError(
        "Unsupported unit. Use one of: gN_m2_s, gN_m2_day, gN_m2_month, "
        "gN_m2_yr, kgN_ha_day, kgN_ha_yr, TgN_global_yr."
    )


def convert(
    value: float,
    unit: str,
    species: str,
    *,
    area_m2: float | None = None,
    period_days: float | None = None,
) -> ConversionResult:
    species = species.upper()
    if species not in N_ATOMS:
        known = ", ".join(sorted(N_ATOMS))
        raise ValueError(f"Unsupported species {species!r}. Known species: {known}")

    gn_m2_s = value_to_gn_m2_s(
        value,
        unit,
        area_m2=area_m2,
        period_days=period_days,
    )
    mol_n_m2_s = gn_m2_s / MOLAR_MASS_N_G_MOL
    mol_species_m2_s = mol_n_m2_s / N_ATOMS[species]
    molecules_cm2_s = mol_species_m2_s * AVOGADRO / CM2_PER_M2
    return ConversionResult(gn_m2_s, molecules_cm2_s)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Convert an LPJmL-style N-mass flux into molecules cm^-2 s^-1. "
            "The input value is interpreted as mass of nitrogen, not whole "
            "molecular mass."
        )
    )
    parser.add_argument("--value", type=float, required=True, help="Input flux value.")
    parser.add_argument(
        "--unit",
        required=True,
        choices=[
            "gN_m2_s",
            "gN_m2_day",
            "gN_m2_month",
            "gN_m2_yr",
            "gN_m2_year",
            "kgN_ha_day",
            "kgN_ha_yr",
            "kgN_ha_year",
            "TgN_global_yr",
            "TgN_global_year",
        ],
        help="Unit of the input value.",
    )
    parser.add_argument(
        "--species",
        required=True,
        choices=sorted(N_ATOMS),
        help="Target molecule carrying the N flux.",
    )
    parser.add_argument(
        "--area-m2",
        type=float,
        help="Area over which a TgN_global_* value should be distributed.",
    )
    parser.add_argument(
        "--period-days",
        type=float,
        help="Override the period length for month/year units.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = convert(
        args.value,
        args.unit,
        args.species,
        area_m2=args.area_m2,
        period_days=args.period_days,
    )
    print(f"source_gN_m2_s={result.source_gn_m2_s:.12e}")
    print(f"{args.species}_molecules_cm-2_s-1={result.molecules_cm2_s:.12e}")


if __name__ == "__main__":
    main()
