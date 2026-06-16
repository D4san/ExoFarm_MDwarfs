"""Small read-only checks for deciding whether a VULCAN output is promotable."""

from __future__ import annotations

import pickle
from pathlib import Path


STEADY_STATE_END_CASE = 1


def inspect_vulcan_termination(path: str | Path) -> dict[str, int | float]:
    """Return the saved VULCAN termination diagnostics for one local output."""
    output_path = Path(path)
    with output_path.open("rb") as output_file:
        data = pickle.load(output_file)

    parameter = data["parameter"]
    variable = data["variable"]
    return {
        "end_case": int(parameter["end_case"]),
        "count": int(parameter["count"]),
        "longdy": float(variable["longdy"]),
        "longdydt": float(variable["longdydt"]),
        "aflux_change": float(variable["aflux_change"]),
    }


def steady_state_reached(path: str | Path) -> bool:
    """Return whether VULCAN saved the output after its convergence test passed."""
    return inspect_vulcan_termination(path)["end_case"] == STEADY_STATE_END_CASE

