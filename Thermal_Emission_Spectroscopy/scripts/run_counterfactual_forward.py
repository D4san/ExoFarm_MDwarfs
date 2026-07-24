"""Compute emission spectra for the molecular counterfactuals (Layer 1).

For each perturbed scenario S and target molecule i, this loads the scenario PT
plus the `S_reset_i_to_A0_chem.txt` chemistry and computes the observed emission
flux Fp_obs. Combined with the full-scenario spectrum, the isolated molecular
signal is dy_i = Fp_obs(full) - Fp_obs(reset_i), quantified downstream.

Only Fp_obs (observed planet flux, W m^-2 m^-1) is computed here: it is the LIFE
observable and halves the radiative-transfer cost versus also doing Fp/Fs.

Run:
    source /home/castello/POSEIDON/activate_exofarm_life.sh
    python Thermal_Emission_Spectroscopy/scripts/run_counterfactual_forward.py \
        --scenarios A1 A2 A3 --species N2O NH3 H2O CO2 O3 CH4
"""

import argparse
from pathlib import Path

import numpy as np

import emission_forward as ef

TARGETS = {"earth_sun": ef.EARTH_SUN, "proxima": ef.PROXIMA_B}
CAMPAIGN_BY_TARGET = {
    "earth_sun": "life_earth_sun_10pc_interface_v1",
    "proxima": "life_proxima_b_earthlike_v1",
}
REPLACEMENT_DIR = ef.PROFILES_DIR / "counterfactual_A0_replacements"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", choices=list(TARGETS), default="earth_sun")
    ap.add_argument("--scenarios", nargs="+", default=["A1", "A2", "A3"],
                    choices=["A1", "A2", "A3"])
    ap.add_argument("--species", nargs="+",
                    default=["N2O", "NH3", "H2O", "CO2", "O3", "CH4"])
    ap.add_argument("--wl-min", type=float, default=3.0)
    ap.add_argument("--wl-max", type=float, default=20.0)
    ap.add_argument("--R", type=int, default=10000)
    args = ap.parse_args()

    tgt = TARGETS[args.target]
    cf_dir = (ef.REPO / "Thermal_Emission_Spectroscopy" / "outputs" /
              CAMPAIGN_BY_TARGET[args.target] / "molecular_diagnostics")
    cf_dir.mkdir(parents=True, exist_ok=True)

    wl = ef.make_wavelength_grid(args.wl_min, args.wl_max, args.R)
    star = ef.build_star(wl, tgt)
    planet = ef.build_planet(tgt)
    P, P_surf, P_ref, R_p_ref = ef.pressure_grid(tgt)

    ref_model = ef.build_model("A0", tgt)
    print("[opacities] reading High-T tables (once)...")
    opac = ef.read_opacities_for(ref_model, wl)

    for key in args.scenarios:
        pt_label = tgt.scenarios[key]
        model = ef.build_model(key, tgt)
        for sp in args.species:
            chem_fn = f"{pt_label}_reset_{sp}_to_A0_chem.txt"
            if not (REPLACEMENT_DIR / chem_fn).exists():
                print(f"[{key}/{sp}] missing {chem_fn}, skipping")
                continue
            T, X = ef.load_profiles_custom_chem(model, P, pt_label, REPLACEMENT_DIR, chem_fn)
            atm = ef.build_atmosphere(planet, model, P, P_ref, R_p_ref, P_surf, T, X)
            Fp_obs = ef.compute_spectrum(
                planet, star, model, atm, opac, wl,
                spectrum_type="direct_emission",
            )
            out = cf_dir / f"{key}_reset_{sp}_Fp_obs.npz"
            np.savez_compressed(out, wl_um=wl, Fp_obs_W_m2_m=Fp_obs,
                                scenario=key, reset_species=sp,
                                provenance=tgt.provenance_label)
            print(f"[{key}/{sp}] saved {out.relative_to(ef.REPO)}")

    print("[done]")


if __name__ == "__main__":
    main()
