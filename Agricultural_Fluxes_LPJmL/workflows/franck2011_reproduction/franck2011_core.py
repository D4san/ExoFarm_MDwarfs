#!/usr/bin/env python3
"""Pure calculations shared by the Franck et al. (2011) workflow.

The functions in this module deliberately do not read LPJmL files. Keeping the
scientific arithmetic separate makes the unit conversions and carrying-capacity
equations testable with hand-checkable values.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable


CARBON_FRACTION_OF_DRY_BIOMASS = 0.45
DEFAULT_KCAL_PER_PERSON_YEAR = 1.0e6
EARTH_RADIUS_M = 6.371e6
AVOGADRO = 6.02214076e23
MOLAR_MASS_N_G_MOL = 14.0067
SECONDS_PER_YEAR = 365.25 * 86400.0
CM2_PER_M2 = 1.0e4


@dataclass(frozen=True)
class NitrogenFluxSummary:
    """A global nitrogen-loss flux expressed at three useful interfaces."""

    total_tgn_year: float
    global_mean_gn_m2_year: float
    molecules_cm2_s: float


def harvested_carbon_to_kcal(
    harvested_carbon_g_m2_year: float,
    *,
    dry_matter_fraction: float,
    kcal_per_g_moist: float,
    trophic_transfer: float = 1.0,
) -> float:
    """Convert LPJmL harvested carbon to edible kcal m-2 yr-1.

    LPJmL reports carbon mass. Its public source defines biomass-to-carbon as
    ``C = 0.45 * dry biomass``. Franck et al. Table 2 then supplies the dry
    matter fraction and the energy content of moist harvested matter.
    """

    if harvested_carbon_g_m2_year < 0:
        raise ValueError("Harvested carbon cannot be negative")
    if not 0 < dry_matter_fraction <= 1:
        raise ValueError("dry_matter_fraction must be in (0, 1]")
    if kcal_per_g_moist < 0:
        raise ValueError("kcal_per_g_moist cannot be negative")
    if not 0 <= trophic_transfer <= 1:
        raise ValueError("trophic_transfer must be in [0, 1]")

    dry_biomass_g_m2_year = (
        harvested_carbon_g_m2_year / CARBON_FRACTION_OF_DRY_BIOMASS
    )
    moist_biomass_g_m2_year = dry_biomass_g_m2_year / dry_matter_fraction
    return moist_biomass_g_m2_year * kcal_per_g_moist * trophic_transfer


def extreme_carrying_capacity(
    total_kcal_year: float,
    *,
    kcal_per_person_year: float = DEFAULT_KCAL_PER_PERSON_YEAR,
) -> float:
    """Return people supported when no land is reserved for other uses."""

    if total_kcal_year < 0:
        raise ValueError("total_kcal_year cannot be negative")
    if kcal_per_person_year <= 0:
        raise ValueError("kcal_per_person_year must be positive")
    return total_kcal_year / kcal_per_person_year


def soft_carrying_capacity(
    total_kcal_year: float,
    productive_area_m2: float,
    reserved_area_m2_person: float,
    *,
    kcal_per_person_year: float = DEFAULT_KCAL_PER_PERSON_YEAR,
) -> float:
    """Apply Franck et al. Eq. (3) within one latitude band.

    The yield density is represented by total calories divided by productive
    area. Applying this function separately to each 10-degree latitude band
    preserves the paper's local-production/no-trade assumption.
    """

    if productive_area_m2 < 0:
        raise ValueError("productive_area_m2 cannot be negative")
    if reserved_area_m2_person < 0:
        raise ValueError("reserved_area_m2_person cannot be negative")
    if total_kcal_year == 0 or productive_area_m2 == 0:
        return 0.0

    people_per_productive_m2 = (
        total_kcal_year / productive_area_m2 / kcal_per_person_year
    )
    return (
        productive_area_m2
        * people_per_productive_m2
        / (1.0 + reserved_area_m2_person * people_per_productive_m2)
    )


def sum_soft_capacity_by_band(
    band_calories_and_area: Iterable[tuple[float, float]],
    reserved_area_m2_person: float,
    *,
    kcal_per_person_year: float = DEFAULT_KCAL_PER_PERSON_YEAR,
) -> float:
    """Sum Eq. (3) over latitude bands."""

    return sum(
        soft_carrying_capacity(
            calories,
            area,
            reserved_area_m2_person,
            kcal_per_person_year=kcal_per_person_year,
        )
        for calories, area in band_calories_and_area
    )


def summarize_global_n_flux(
    total_gn_year: float,
    *,
    species_n_atoms: int,
    planet_radius_m: float = EARTH_RADIUS_M,
) -> NitrogenFluxSummary:
    """Convert a global N-mass loss to a global atmospheric boundary flux.

    ``total_gn_year`` is nitrogen mass, not whole-molecule mass. The returned
    molecule flux is distributed over the full spherical surface, which is the
    appropriate convention for a globally averaged 1-D atmospheric model.
    """

    if total_gn_year < 0:
        raise ValueError("total_gn_year cannot be negative")
    if species_n_atoms not in (1, 2):
        raise ValueError("species_n_atoms must be 1 or 2")
    if planet_radius_m <= 0:
        raise ValueError("planet_radius_m must be positive")

    surface_area_m2 = 4.0 * math.pi * planet_radius_m**2
    global_mean_gn_m2_year = total_gn_year / surface_area_m2
    mol_n_s = total_gn_year / MOLAR_MASS_N_G_MOL / SECONDS_PER_YEAR
    molecules_s = mol_n_s / species_n_atoms * AVOGADRO
    molecules_cm2_s = molecules_s / (surface_area_m2 * CM2_PER_M2)
    return NitrogenFluxSummary(
        total_tgn_year=total_gn_year / 1.0e12,
        global_mean_gn_m2_year=global_mean_gn_m2_year,
        molecules_cm2_s=molecules_cm2_s,
    )
