"""POSEIDON thermal-emission forward model for the LIFE track (Stage III, Layer 1).

Adapts the POSEIDON call skeleton from the transmission engine
(`Transmission_Spectroscopy/notebooks/exofarm_transmission_workflow.py`, used
here as a READ-ONLY reference) to **thermal emission** for the
`life_earth_sun_10pc` benchmark. This is the interface-validation branch: it
loads the accepted Earth--Sun A0--A3 VULCAN hand-off profiles and computes what
LIFE actually observes.

Two physical quantities are produced per scenario, because POSEIDON distinguishes
them and LIFE needs the *absolute* one:

- ``Fp_Fs``   : ``spectrum_type='emission'``        -> dimensionless secondary-
                eclipse contrast Fp/Fs (transiting geometry).
- ``Fp_obs``  : ``spectrum_type='direct_emission'`` -> planet flux observed at the
                system distance d, ``F_p_obs = (R_p/d)**2 * F_p`` (direct-imaging
                geometry, the LIFE case). POSEIDON returns this in
                ``W m^-2 m^-1`` (per-wavelength energy flux at the observer).

Provenance: the A2/A3 profiles are the frozen ``earth_20260615_pre_n2o_correction``
set (N2O = 3.35e9 / 1.20e10, predating the active corrected BC 3.416e9 / 1.238e10).
Use only to validate the POSEIDON->LIFE interface, never as the current ExoFarm
matrix without a documented rerun/historical decision. See
``docs/earth_sun_n2o_matrix_provenance_2026-07-20.md``.
"""

from pathlib import Path

import numpy as np

from POSEIDON.core import (
    create_star,
    create_planet,
    define_model,
    make_atmosphere,
    read_opacities,
    compute_spectrum,
    wl_grid_constant_R,
)
from POSEIDON.constants import R_Sun, R_E, M_E
from POSEIDON.utility import read_PT_file, read_chem_file


# ---------------------------------------------------------------------------
# Paths. Resolve from this file so the wrapper works from any launch directory.
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parents[2]
PROFILES_DIR = REPO / "Transmission_Spectroscopy" / "profiles"

# ---------------------------------------------------------------------------
# Targets. The system distance belongs to the LIFE observational scene only; it
# does NOT alter the photochemistry. A Target bundles everything that changes
# between the Layer-1 Earth--Sun benchmark and the Layer-2 Proxima b branch, so
# the forward machinery below stays single-source.
# ---------------------------------------------------------------------------
from dataclasses import dataclass, field

PARSEC_M = 3.0856775814913673e16          # 1 parsec in metres (not in POSEIDON.constants)

# N2 is the bulk filler; the 7 radiatively active species match the transmission
# study so the tracks stay comparable. VULCAN carries ~100 species but only
# these are loaded as opacity sources in the LIFE mid-IR band.
BULK_SPECIES = ["N2"]
PARAM_SPECIES = ["H2O", "CO2", "CH4", "O2", "O3", "N2O", "NH3"]


@dataclass(frozen=True)
class Target:
    name: str
    star: dict                 # R_s (m), T_eff (K), log_g, Met -> create_star(phoenix)
    planet: dict               # R_p (m), mass (kg), T_eq (K)
    distance_pc: float
    scenarios: dict            # scenario key -> profile file label
    provenance_label: str
    P_max_bar: float = 1.0     # surface pressure (opaque lower boundary)
    P_min_bar: float = 3.0e-8  # just below the exported profile top

    @property
    def distance_m(self):
        return self.distance_pc * PARSEC_M


# Layer 1 -- Earth--Sun @ 10 pc interface benchmark. Sun via PHOENIX grid.
EARTH_SUN = Target(
    name="earth_sun_10pc",
    star=dict(R_s=1.0 * R_Sun, T_eff=5772.0, log_g=4.44, Met=0.0),
    planet=dict(R_p=1.0 * R_E, mass=1.0 * M_E, T_eq=255.0),
    distance_pc=10.0,
    scenarios={
        "A0": "Earth_A0_PreAgri", "A1": "Earth_A1_Current",
        "A2": "Earth_A2_Moderate", "A3": "Earth_A3_Extreme",
    },
    provenance_label="earth_20260615_pre_n2o_correction",
)

# Layer 2 -- Earth-like analogue under the Proxima Centauri environment.
# Star/planet/distance frozen from LIFE X (Carrion-Gonzalez et al. 2023,
# Table G.1): d=1.30 pc, T=3050 K, R_star=0.14 R_sun; R_p=1.23 R_E,
# M_p=1.59 M_E, T_eq=229 K. log_g_star~5.2 (M5.5V). BCs are the corrected
# active matrix (not the pre-correction set), so this branch carries the
# current ExoFarm N2O values from the start.
PROXIMA_B = Target(
    name="proxima_b_earthlike",
    star=dict(R_s=0.14 * R_Sun, T_eff=3050.0, log_g=5.2, Met=0.0),
    planet=dict(R_p=1.23 * R_E, mass=1.59 * M_E, T_eq=229.0),
    distance_pc=1.30,
    scenarios={
        "A0": "Proxima_b_A0_PreAgri", "A1": "Proxima_b_A1_Current",
        "A2": "Proxima_b_A2_Moderate", "A3": "Proxima_b_A3_Extreme",
    },
    provenance_label="proxima_muscles_v22_terrestrialPT_correctedBC",
)

# --- Backward-compatible module aliases (Layer-1 scripts import these) -------
DISTANCE_PC = EARTH_SUN.distance_pc
SYSTEM_DISTANCE_M = EARTH_SUN.distance_m
STAR = EARTH_SUN.star
PLANET = EARTH_SUN.planet
SCENARIOS = EARTH_SUN.scenarios
PROVENANCE_LABEL = EARTH_SUN.provenance_label


def read_chem_file_species(scenario_label):
    """Return the ordered species names in a chem file header (drops 'PRESS').

    The Earth export carries 100 species (ending in Ar), which differs from the
    TRAPPIST column list hard-coded in the transmission engine. Reading the
    header keeps this wrapper in sync with whatever the exporter wrote.
    """
    with open(PROFILES_DIR / f"{scenario_label}_chem.txt") as fh:
        return fh.readline().split()[1:]


def make_wavelength_grid(wl_min=3.0, wl_max=20.0, R=10000):
    """Native emission grid covering the LIFE band (4--18.5 um) with margins.

    R is intentionally higher than the LIFE instrument resolution so that later
    rebinning to the LIFE grid does not imprint the model sampling.
    """
    return wl_grid_constant_R(wl_min, wl_max, R)


def build_star(wl, target=EARTH_SUN):
    s = target.star
    return create_star(
        s["R_s"], s["T_eff"], s["log_g"], s["Met"],
        wl=wl, stellar_grid="phoenix",
    )


def build_planet(target=EARTH_SUN):
    # d (system distance) is required for the direct_emission geometry.
    p = target.planet
    return create_planet(
        target.name, p["R_p"], mass=p["mass"],
        T_eq=p["T_eq"], d=target.distance_m,
    )


def pressure_grid(target=EARTH_SUN, n_layers=100):
    """Log-spaced pressure grid (bar). Surface is the opaque lower boundary.

    Profiles run P_min_bar .. P_max_bar (1 bar surface for both targets here);
    P_min is set just below the profile top so read_*_file never extrapolates.
    """
    P = np.logspace(np.log10(target.P_max_bar), np.log10(target.P_min_bar), n_layers)
    P_surf = target.P_max_bar
    P_ref = P_surf                 # anchor R_p at the surface, as in the transmission track
    R_p_ref = target.planet["R_p"]
    return P, P_surf, P_ref, R_p_ref


def build_model(scenario_key, target=EARTH_SUN):
    """File-read PT + chemistry emission model (thermal, single-stream)."""
    return define_model(
        f"life_{target.name}_{scenario_key}",
        BULK_SPECIES,
        PARAM_SPECIES,
        PT_profile="file_read",
        X_profile="file_read",
        radius_unit="R_E",
        surface=True,              # opaque rocky surface at 1 bar
        thermal=True,              # thermal emission (single stream)
        thermal_scattering=False,
    )


def load_profiles(model, P, scenario_key, target=EARTH_SUN):
    """Interpolate the VULCAN hand-off PT/chem onto the POSEIDON pressure grid."""
    label = target.scenarios[scenario_key]
    # PT file columns are ALT(km) P(bar) T(K) -> 1-based P_column=2, T_column=3.
    T = read_PT_file(
        str(PROFILES_DIR), f"{label}_PT.txt", P,
        skiprows=1, P_column=2, T_column=3,
    )
    chem_file_species = read_chem_file_species(label)
    X = read_chem_file(
        str(PROFILES_DIR), f"{label}_chem.txt", P,
        chem_file_species,
        chem_species_in_model=model["chemical_species"],
        skiprows=1,
    )
    return T, X


def load_profiles_custom_chem(model, P, pt_label, chem_dir, chem_filename):
    """Like load_profiles, but the chemistry comes from an explicit chem file.

    Used for the molecular counterfactuals: the PT profile stays the scenario's,
    while the chemistry is a `*_reset_<species>_to_A0_chem.txt` file. The
    counterfactuals share the scenario pressure grid, so no re-interpolation of PT
    is needed beyond POSEIDON's own file read.
    """
    T = read_PT_file(
        str(PROFILES_DIR), f"{pt_label}_PT.txt", P,
        skiprows=1, P_column=2, T_column=3,
    )
    with open(Path(chem_dir) / chem_filename) as fh:
        chem_file_species = fh.readline().split()[1:]
    X = read_chem_file(
        str(chem_dir), chem_filename, P, chem_file_species,
        chem_species_in_model=model["chemical_species"], skiprows=1,
    )
    return T, X


def build_atmosphere(planet, model, P, P_ref, R_p_ref, P_surf, T, X):
    return make_atmosphere(
        planet, model, P, P_ref, R_p_ref,
        T_input=T, X_input=X,
        surface_params=np.array([np.log10(P_surf)]),
    )


def compute_emission(planet, star, model, atmosphere, opac, wl):
    """Return (Fp_Fs, Fp_obs) for one scenario.

    Fp_Fs  : dimensionless contrast (spectrum_type='emission').
    Fp_obs : observed planet flux at d (spectrum_type='direct_emission').
    """
    Fp_Fs = compute_spectrum(
        planet, star, model, atmosphere, opac, wl,
        spectrum_type="emission",
    )
    Fp_obs = compute_spectrum(
        planet, star, model, atmosphere, opac, wl,
        spectrum_type="direct_emission",
    )
    return Fp_Fs, Fp_obs


def read_opacities_for(model, wl, T_fine=None, log_P_fine=None):
    """Opacity tables over the profile T/P envelope, High-T database (has NH3)."""
    if T_fine is None:
        # Earth profiles span 187--300 K; pad to the DB-friendly 180--310 K band.
        T_fine = np.arange(180.0, 310.0 + 10.0, 10.0)
    if log_P_fine is None:
        # Profiles span 5e-8 .. 1 bar -> log10 -7.3 .. 0.
        log_P_fine = np.arange(-7.5, 0.0 + 0.25, 0.25)
    return read_opacities(
        model, wl, "opacity_sampling", T_fine, log_P_fine,
        opacity_database="High-T",
    )
