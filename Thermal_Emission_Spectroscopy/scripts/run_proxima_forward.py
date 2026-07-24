"""Layer-2 (`life_proxima_b_earthlike`) emission forward runner + manifest.

Same POSEIDON emission machinery as Layer 1 (via emission_forward.PROXIMA_B),
but the target is an Earth-like atmosphere under the Proxima Centauri radiation
field. Star/planet/distance are frozen from LIFE X (Carrión-González et al.
2023); the chemistry comes from the VULCAN Proxima A0--A3 run (corrected active
BC, terrestrial PT). Unlike Layer 1 this branch is NOT pre-correction.

Run (after the Proxima profiles are exported to Transmission_Spectroscopy/profiles/):
    source /home/castello/POSEIDON/activate_exofarm_life.sh
    python Thermal_Emission_Spectroscopy/scripts/run_proxima_forward.py --scenarios A0
    python Thermal_Emission_Spectroscopy/scripts/run_proxima_forward.py --scenarios A0 A1 A2 A3
"""

import argparse
import hashlib
import json
import platform
from datetime import datetime, timezone
from importlib.metadata import version, PackageNotFoundError

import numpy as np

import emission_forward as ef

TARGET = ef.PROXIMA_B
CAMPAIGN_ID = "life_proxima_b_earthlike_v1"
OUTPUT_DIR = ef.REPO / "Thermal_Emission_Spectroscopy" / "outputs" / CAMPAIGN_ID
FORWARD_DIR = OUTPUT_DIR / "forward_emission"


def _md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _pkg(name):
    try:
        return version(name)
    except PackageNotFoundError:
        return "not-installed"


def write_manifest(wl):
    profile_records = {}
    for key, label in TARGET.scenarios.items():
        rec = {}
        for kind in ("PT", "chem"):
            p = ef.PROFILES_DIR / f"{label}_{kind}.txt"
            rec[kind] = {
                "path": str(p.relative_to(ef.REPO)),
                "md5": _md5(p) if p.exists() else "MISSING",
            }
        profile_records[key] = rec

    manifest = {
        "campaign_id": CAMPAIGN_ID,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "layer": "2 - life_proxima_b_earthlike (Proxima environment, controlled)",
        "provenance_label": TARGET.provenance_label,
        "provenance_note": (
            "Earth-like analogue under the Proxima Centauri radiation field, NOT "
            "Proxima b's measured atmosphere. Chemistry from VULCAN Proxima A0-A3 "
            "with the CORRECTED active BC (current ExoFarm matrix) and terrestrial "
            "PT/Kzz (atm_Earth_Jan_Kzz.txt). Stellar SED: MUSCLES v22 GJ551 "
            "(MAST HLSP DOI 10.17909/T9DG6F), converted to VULCAN surface flux by "
            "convert_proxima_muscles_sed.py. See "
            "docs/life_proxima_b_branch_bitacora_2026-07-22.md."
        ),
        "scene": {
            "distance_pc": TARGET.distance_pc,
            "distance_m": TARGET.distance_m,
            "source": "Carrión-González et al. 2023 (LIFE X), Table G.1",
        },
        "star_proxima": TARGET.star | {"stellar_grid": "phoenix",
                                       "note": "T=3050 K, R=0.14 Rsun (LIFE X)"},
        "planet_proxima_b": TARGET.planet | {
            "note": "R_p=1.23 R_E, M_p=1.59 M_E, T_eq=229 K (LIFE X, Table G.1)"},
        "forward_config": {
            "spectrum_types": ["emission (Fp/Fs)", "direct_emission (Fp_obs at d)"],
            "bulk_species": ef.BULK_SPECIES,
            "param_species": ef.PARAM_SPECIES,
            "opacity_database": "High-T (Opacity_database_v1.3.hdf5; contains NH3/N2O)",
            "wl_min_um": float(wl[0]),
            "wl_max_um": float(wl[-1]),
            "wl_n_points": int(wl.size),
            "wl_native_R": 10000,
            "surface": True,
            "P_surf_bar": TARGET.P_max_bar,
        },
        "profiles": profile_records,
        "versions": {
            "python": platform.python_version(),
            "POSEIDON": _pkg("POSEIDON"), "lifesim": _pkg("lifesim"),
            "lifesimmc": _pkg("lifesimmc"), "phringe": _pkg("phringe"),
            "numpy": np.__version__,
        },
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_DIR / "manifest.json", "w") as fh:
        json.dump(manifest, fh, indent=2)
    return manifest


def blackbody_flux_wl(wl_um, T):
    h, c, kB = 6.62607015e-34, 2.99792458e8, 1.380649e-23
    wl_m = wl_um * 1e-6
    return (2 * h * c**2 / wl_m**5) / np.expm1(h * c / (wl_m * kB * T))


def validate_A0(wl, Fp_Fs, Fp_obs):
    """A0 units/geometry gate. PT is terrestrial so the emitting T stays ~285 K,
    but the geometry uses the Proxima planet radius and 1.30 pc distance."""
    print("\n=== VALIDACION A0 Proxima (sin ruido) ===")
    print(f"  wl: {wl.size} pts, {wl[0]:.3f}..{wl[-1]:.3f} um")
    print(f"  Fp/Fs   : min={np.nanmin(Fp_Fs):.3e} max={np.nanmax(Fp_Fs):.3e}")
    print(f"  Fp_obs  : min={np.nanmin(Fp_obs):.3e} max={np.nanmax(Fp_obs):.3e} (W m^-2 m^-1)")
    T_emit = 285.0
    geom = (TARGET.planet["R_p"] / TARGET.distance_m) ** 2
    bb = np.pi * blackbody_flux_wl(wl, T_emit) * geom
    i10 = int(np.argmin(np.abs(wl - 10.0)))
    ratio = Fp_obs[i10] / bb[i10]
    print(f"  blackbody(285K, 1.23R_E, 1.30pc) @10um = {bb[i10]:.3e}")
    print(f"  Fp_obs @10um                           = {Fp_obs[i10]:.3e}")
    print(f"  ratio @10um = {ratio:.3f} (expect ~0.3-1.5)")
    ok = (np.isfinite(Fp_obs).all() and (Fp_obs > 0).all() and 0.05 < ratio < 5.0)
    print(f"  --> A0 Proxima interface check: {'PASS' if ok else 'REVISAR'}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", nargs="+", default=["A0"],
                    choices=list(TARGET.scenarios.keys()))
    ap.add_argument("--wl-min", type=float, default=3.0)
    ap.add_argument("--wl-max", type=float, default=20.0)
    ap.add_argument("--R", type=int, default=10000)
    args = ap.parse_args()

    # Guard: refuse to run until the Proxima profiles exist.
    missing = [f"{lbl}_{k}.txt" for lbl in TARGET.scenarios.values()
               for k in ("PT", "chem")
               if not (ef.PROFILES_DIR / f"{lbl}_{k}.txt").exists()]
    if missing:
        raise SystemExit("[abort] faltan perfiles Proxima exportados:\n  " +
                         "\n  ".join(missing))

    FORWARD_DIR.mkdir(parents=True, exist_ok=True)
    wl = ef.make_wavelength_grid(args.wl_min, args.wl_max, args.R)
    print(f"[manifest] freezing {CAMPAIGN_ID}")
    write_manifest(wl)

    print("[scene] Proxima (PHOENIX 3050K) + Earth-like planet @ 1.30 pc")
    star = ef.build_star(wl, TARGET)
    planet = ef.build_planet(TARGET)
    P, P_surf, P_ref, R_p_ref = ef.pressure_grid(TARGET)

    ref_model = ef.build_model("A0", TARGET)
    print("[opacities] reading High-T tables (once)...")
    opac = ef.read_opacities_for(ref_model, wl)

    for key in args.scenarios:
        print(f"\n[{key}] building model + atmosphere")
        model = ef.build_model(key, TARGET)
        T, X = ef.load_profiles(model, P, key, TARGET)
        atm = ef.build_atmosphere(planet, model, P, P_ref, R_p_ref, P_surf, T, X)
        print(f"[{key}] computing emission (Fp/Fs + direct_emission)")
        Fp_Fs, Fp_obs = ef.compute_emission(planet, star, model, atm, opac, wl)
        out = FORWARD_DIR / f"{key}_emission.npz"
        np.savez_compressed(out, wl_um=wl, Fp_Fs=Fp_Fs, Fp_obs_W_m2_m=Fp_obs,
                            scenario=key, provenance=TARGET.provenance_label)
        print(f"[{key}] saved {out.relative_to(ef.REPO)}")
        if key == "A0":
            validate_A0(wl, Fp_Fs, Fp_obs)

    print("\n[done]")


if __name__ == "__main__":
    main()
