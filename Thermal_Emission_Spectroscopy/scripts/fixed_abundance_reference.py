"""Validate a frozen scalar A0 reference without importing POSEIDON."""

import hashlib
import json
import math
from pathlib import Path


def load_fixed_abundances(reference_path, species, repo_root):
    """Return explicit log10 VMR constraints with checked profile provenance."""
    reference = json.loads(Path(reference_path).read_text(encoding="utf-8"))
    species = list(species)
    if not species or len(set(species)) != len(species):
        raise ValueError("Specify distinct fixed species")
    if set(species) - {"N2O", "NH3"}:
        raise ValueError("This A0 reference supports only N2O and NH3")
    profile = (Path(repo_root) / reference["profile_rel"]).resolve()
    if not profile.is_relative_to(Path(repo_root).resolve()):
        raise ValueError("Reference profile escapes repository")
    digest = hashlib.sha256(profile.read_bytes()).hexdigest()
    if digest != reference["profile_sha256"]:
        raise ValueError("Frozen A0 profile checksum changed")
    values = {}
    for name in species:
        value = float(reference["log10_vmr"][name])
        vmr = float(reference["vmr"][name])
        if not math.isfinite(value) or not -12 <= value <= -1:
            raise ValueError(f"Invalid fixed abundance for {name}")
        if vmr <= 0 or not math.isclose(math.log10(vmr), value, abs_tol=1e-12):
            raise ValueError(f"Inconsistent VMR/log10 reference for {name}")
        values[name] = value
    return values


def constrain_priors(prior_types, prior_ranges, values):
    """A zero-width unit-cube transform is a fixed point, not a narrow prior."""
    for species, value in values.items():
        parameter = "log_" + species
        prior_types[parameter] = "uniform"
        prior_ranges[parameter] = [value, value]
