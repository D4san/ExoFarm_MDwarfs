"""Layer-1 (`life_earth_sun_10pc`) emission forward runner + manifest.

Authorized sequence (docs/life_stage_iii_two_layer_workplan_2026-07-20.md):
  1. Freeze a manifest (versions, params, 10 pc scene, profile checksums,
     provenance label).
  2. Build the POSEIDON emission forward reading file PT/chem.
  3. Validate a noise-free A0 (grid, radii, distance, physical magnitude) BEFORE
     generating A0--A3.

Run (from the ExoFarm_LIFE env, with POSEIDON_input_data / PYSYN_CDBS set):
    source /home/castello/POSEIDON/activate_exofarm_life.sh
    python Thermal_Emission_Spectroscopy/scripts/run_layer1_forward.py --scenarios A0
    python Thermal_Emission_Spectroscopy/scripts/run_layer1_forward.py --scenarios A0 A1 A2 A3
"""

import argparse
import hashlib
import json
import platform
from datetime import datetime, timezone
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path

import numpy as np

import emission_forward as ef

CAMPAIGN_ID = "life_earth_sun_10pc_interface_v1"
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
    """Freeze provenance, versions, scene and profile checksums as manifest.json."""
    profile_records = {}
    for key, label in ef.SCENARIOS.items():
        rec = {}
        for kind in ("PT", "chem"):
            p = ef.PROFILES_DIR / f"{label}_{kind}.txt"
            rec[kind] = {"path": str(p.relative_to(ef.REPO)), "md5": _md5(p)}
        profile_records[key] = rec

    manifest = {
        "campaign_id": CAMPAIGN_ID,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "layer": "1 - life_earth_sun_10pc (interface validation)",
        "provenance_label": ef.PROVENANCE_LABEL,
        "provenance_caveat": (
            "A2/A3 profiles frozen 2026-06-15 (N2O=3.35e9/1.20e10) predate the "
            "active corrected BC (3.416e9/1.238e10). Interface validation only; "
            "not the current ExoFarm matrix without a documented rerun/decision."
        ),
        "scene": {
            "distance_pc": ef.DISTANCE_PC,
            "distance_m": ef.SYSTEM_DISTANCE_M,
            "note": "10 pc belongs to the LIFE scene only; VULCAN photochemistry unchanged.",
        },
        "star_sun": ef.STAR | {"stellar_grid": "phoenix"},
        "planet_earth": ef.PLANET,
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
            "P_surf_bar": 1.0,
        },
        "profiles": profile_records,
        "versions": {
            "python": platform.python_version(),
            "POSEIDON": _pkg("POSEIDON"),
            "lifesim": _pkg("lifesim"),
            "lifesimmc": _pkg("lifesimmc"),
            "phringe": _pkg("phringe"),
            "numpy": np.__version__,
        },
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_DIR / "manifest.json", "w") as fh:
        json.dump(manifest, fh, indent=2)
    return manifest


def blackbody_flux_wl(wl_um, T):
    """Planck spectral radiance B_lambda(T) in W m^-2 m^-1 sr^-1."""
    h = 6.62607015e-34
    c = 2.99792458e8
    kB = 1.380649e-23
    wl_m = wl_um * 1e-6
    return (2 * h * c**2 / wl_m**5) / (np.expm1(h * c / (wl_m * kB * T)))


def validate_A0(wl, Fp_Fs, Fp_obs):
    """Physical sanity checks for the noise-free A0 forward (units gate, part 1)."""
    print("\n=== VALIDACION A0 (sin ruido) ===")
    print(f"  wl: {wl.size} pts, {wl[0]:.3f}..{wl[-1]:.3f} um")
    print(f"  Fp/Fs   : min={np.nanmin(Fp_Fs):.3e} max={np.nanmax(Fp_Fs):.3e} "
          f"finite={np.isfinite(Fp_Fs).all()}")
    print(f"  Fp_obs  : min={np.nanmin(Fp_obs):.3e} max={np.nanmax(Fp_obs):.3e} "
          f"finite={np.isfinite(Fp_obs).all()} (W m^-2 m^-1)")

    # Blackbody cross-check: an Earth-radius disk at 285 K (effective emitting T),
    # observed at 10 pc, gives F ~ pi*B_lambda(285)*(R_E/d)^2. Order-of-magnitude
    # agreement with Fp_obs confirms the (R_p/d)^2 geometry and units.
    T_eff_emit = 285.0
    geom = (ef.PLANET["R_p"] / ef.SYSTEM_DISTANCE_M) ** 2
    bb_obs = np.pi * blackbody_flux_wl(wl, T_eff_emit) * geom
    ratio = Fp_obs / bb_obs
    i10 = int(np.argmin(np.abs(wl - 10.0)))
    print(f"  blackbody(285K, R_E, 10pc) @10um = {bb_obs[i10]:.3e} W m^-2 m^-1")
    print(f"  Fp_obs @10um                     = {Fp_obs[i10]:.3e} W m^-2 m^-1")
    print(f"  ratio Fp_obs/BB @10um            = {ratio[i10]:.3f} "
          f"(expect ~0.3-1.5 for a real atmosphere)")
    ok = (np.isfinite(Fp_Fs).all() and np.isfinite(Fp_obs).all()
          and (Fp_obs > 0).all() and 0.05 < ratio[i10] < 5.0)
    print(f"  --> A0 interface check: {'PASS' if ok else 'REVISAR'}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", nargs="+", default=["A0"],
                    choices=list(ef.SCENARIOS.keys()))
    ap.add_argument("--wl-min", type=float, default=3.0)
    ap.add_argument("--wl-max", type=float, default=20.0)
    ap.add_argument("--R", type=int, default=10000)
    args = ap.parse_args()

    FORWARD_DIR.mkdir(parents=True, exist_ok=True)

    wl = ef.make_wavelength_grid(args.wl_min, args.wl_max, args.R)
    print(f"[manifest] freezing {CAMPAIGN_ID}")
    write_manifest(wl)

    print("[scene] Sun (PHOENIX) + Earth @ 10 pc")
    star = ef.build_star(wl)
    planet = ef.build_planet()
    P, P_surf, P_ref, R_p_ref = ef.pressure_grid()

    # Opacities depend only on wl + species + T/P grid (identical across A0-A3),
    # so read once with the A0 model and reuse.
    ref_model = ef.build_model("A0")
    print("[opacities] reading High-T tables (once, reused for all scenarios)...")
    opac = ef.read_opacities_for(ref_model, wl)

    for key in args.scenarios:
        print(f"\n[{key}] building model + atmosphere")
        model = ef.build_model(key)
        T, X = ef.load_profiles(model, P, key)
        atm = ef.build_atmosphere(planet, model, P, P_ref, R_p_ref, P_surf, T, X)
        print(f"[{key}] computing emission (Fp/Fs + direct_emission)")
        Fp_Fs, Fp_obs = ef.compute_emission(planet, star, model, atm, opac, wl)

        out = FORWARD_DIR / f"{key}_emission.npz"
        np.savez_compressed(
            out, wl_um=wl, Fp_Fs=Fp_Fs, Fp_obs_W_m2_m=Fp_obs,
            scenario=key, provenance=ef.PROVENANCE_LABEL,
        )
        print(f"[{key}] saved {out.relative_to(ef.REPO)}")

        if key == "A0":
            validate_A0(wl, Fp_Fs, Fp_obs)

    print("\n[done]")


if __name__ == "__main__":
    main()
