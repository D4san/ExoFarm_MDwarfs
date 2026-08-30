"""Generate molecular counterfactual chemistry profiles for the LIFE emission track.

For a scenario S and a target molecule i, the counterfactual replaces ONLY that
molecule's vertical mixing-ratio profile with the A0 (pre-agricultural) profile,
keeping every other species from S. Running POSEIDON emission on the original and
the counterfactual then isolates the molecule's differential signal:

    dy_i(lambda) = y_full(lambda) - y_{i -> A0}(lambda)

Targets are the ExoFarm species N2O and NH3; H2O, CO2, O3 and CH4 are generated
as overlap/degeneracy controls. The A0 profile is interpolated (in log-abundance
vs log-pressure) onto the scenario pressure grid so the substitution is robust to
any grid differences.

Output chem files keep the exact export format (header row of species names,
one pressure column + one column per species) and are written to
``Transmission_Spectroscopy/profiles/counterfactual_A0_replacements/`` alongside
the pre-existing TRAPPIST counterfactuals.

Provenance: earth_20260615_pre_n2o_correction (interface validation only).
"""

import argparse
from pathlib import Path

import numpy as np

import emission_forward as ef

REPLACEMENT_DIR = ef.PROFILES_DIR / "counterfactual_A0_replacements"

TARGET_SPECIES = ["N2O", "NH3", "H2O", "CO2", "O3", "CH4"]
TARGETS = {"earth_sun": ef.EARTH_SUN, "proxima": ef.PROXIMA_B}

# Scenarios that carry an ExoFarm perturbation relative to A0.
PERTURBED = ["A1", "A2", "A3"]

FLOOR = 1e-30  # abundance floor so log-interpolation never sees a true zero


def read_chem(label):
    """Return (header_species, press[bar], X[n_layer, n_species])."""
    path = ef.PROFILES_DIR / f"{label}_chem.txt"
    with open(path) as fh:
        header = fh.readline().split()
    data = np.loadtxt(path, skiprows=1)
    press = data[:, 0]
    X = data[:, 1:]
    return header[1:], press, X


def write_chem(out_path, species, press, X):
    """Write a chem file in the canonical PRESS + species format."""
    header = "PRESS " + " ".join(species)
    block = np.column_stack([press, X])
    np.savetxt(out_path, block, header=header, comments="",
               fmt="%.6e")


def a0_profile_on_grid(a0_species, a0_press, a0_X, target, press_target):
    """A0 mixing ratio of `target` interpolated (log-log) onto press_target."""
    j = a0_species.index(target)
    a0_col = np.clip(a0_X[:, j], FLOOR, None)
    # Interpolate in log10(abundance) vs log10(P). Both profiles are monotonic in P.
    log_a0 = np.interp(
        np.log10(press_target),
        np.log10(a0_press[::-1]) if a0_press[0] > a0_press[-1] else np.log10(a0_press),
        np.log10(a0_col[::-1]) if a0_press[0] > a0_press[-1] else np.log10(a0_col),
    )
    return 10.0 ** log_a0


def make_for_scenario(scenario_key, species_list, tgt):
    label = tgt.scenarios[scenario_key]
    sp, press, X = read_chem(label)
    a0_sp, a0_press, a0_X = read_chem(tgt.scenarios["A0"])
    assert sp == a0_sp, "species column mismatch between scenario and A0"

    REPLACEMENT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for target in species_list:
        if target not in sp:
            print(f"  [skip] {target} not in chem header")
            continue
        Xc = X.copy()
        Xc[:, sp.index(target)] = a0_profile_on_grid(a0_sp, a0_press, a0_X, target, press)
        out = REPLACEMENT_DIR / f"{label}_reset_{target}_to_A0_chem.txt"
        write_chem(out, sp, press, Xc)
        written.append(out.name)
    return written


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", choices=list(TARGETS), default="earth_sun")
    ap.add_argument("--scenarios", nargs="+", default=PERTURBED,
                    choices=["A1", "A2", "A3"])
    ap.add_argument("--species", nargs="+", default=TARGET_SPECIES)
    args = ap.parse_args()

    tgt = TARGETS[args.target]
    for key in args.scenarios:
        print(f"[{key}] counterfactuals ({tgt.name}) -> reset to {tgt.scenarios['A0']}")
        names = make_for_scenario(key, args.species, tgt)
        for n in names:
            print(f"   wrote {n}")
    print("[done]")


if __name__ == "__main__":
    main()
