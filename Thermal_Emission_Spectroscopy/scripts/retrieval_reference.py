"""Reference abundances for comparing isochemical retrievals with VULCAN.

The retrieval fits constant-with-height abundances, whereas VULCAN provides
vertical profiles.  This module centralizes the pressure-column average used
to map a VULCAN profile into the retrieval's scalar abundance space.
"""

from __future__ import annotations

import numpy as np


def column_averaged_mixing_ratio(
    profile: np.ndarray,
    molecule: str,
    pressure_field: str = "PRESS",
) -> float:
    """Return the pressure-column average of one VULCAN mixing-ratio profile.

    The pressure integral follows the existing project diagnostic:

        integral X(p) dp / (p_bottom - p_top)

    Pressure increments approximate atmospheric column mass under hydrostatic
    balance, so this weights the dense lower atmosphere more strongly than an
    unweighted mean over model levels.
    """
    pressure = np.asarray(profile[pressure_field], dtype=float)
    vmr = np.asarray(profile[molecule], dtype=float)
    finite = (
        np.isfinite(pressure)
        & np.isfinite(vmr)
        & (pressure > 0.0)
        & (vmr > 0.0)
    )
    if np.count_nonzero(finite) < 2:
        raise ValueError(f"Insufficient finite positive values for {molecule}")

    pressure = pressure[finite]
    vmr = vmr[finite]
    order = np.argsort(pressure)
    pressure = pressure[order]
    vmr = vmr[order]

    # NumPy 1.x (used by the POSEIDON environment) exposes this as trapz;
    # NumPy 2.x provides the preferred trapezoid name.
    # ``getattr`` evaluates its default eagerly, and NumPy 2.4 no longer has
    # ``trapz``. Select the available API without touching the missing alias.
    trapezoid = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    pressure_span = trapezoid(np.ones_like(pressure), x=pressure)
    if pressure_span <= 0.0:
        raise ValueError(f"Non-positive pressure span for {molecule}")
    return float(trapezoid(vmr, x=pressure) / pressure_span)


def log10_column_averaged_mixing_ratio(
    profile: np.ndarray,
    molecule: str,
    pressure_field: str = "PRESS",
) -> float:
    """Return the base-10 logarithm of the pressure-column average."""
    value = column_averaged_mixing_ratio(profile, molecule, pressure_field)
    return float(np.log10(value))
