"""LIFEsim-classic S/N analysis for `life_proxima_b_earthlike` (Layer 2).

Same diagnostic pipeline as the Layer-1 runner, but on the Proxima b forward
products and with the LIFE X scene (Carrión-González et al. 2023): R=20, D=2 m,
exozodi z=3, star T=3050 K / R=0.14 R_sun, d=1.30 pc, angular separation a/d,
ecliptic latitude from Proxima's ICRS coordinates. That scene reproduces the
LIFE X Proxima b anchor (S/N=170 in 10 h) to 2% — see
validate_proxima_life_scene.py.

Molecular-signal S/N and the sqrt(t) scaling are computed exactly as in Layer 1;
the band/SNR helpers are imported from run_life_snr_classic to stay single-source.

Outputs under outputs/life_proxima_b_earthlike_v1/. SNR is a diagnostic, not a
detection. Provenance: proxima_muscles_v22_terrestrialPT_correctedBC.
"""

import csv

import numpy as np

import emission_forward as ef
from life_scene_classic import LifeSceneClassic
from run_life_snr_classic import (
    BANDS, TARGETS, CONTROLS, ALL_SPECIES, PERTURBED,
    band_mask, band_snr, rebin_photon,
)
from validate_proxima_life_scene import (
    proxima_ecliptic_lat_rad, T_STAR, R_STAR, D_PC, A_AU, EXOZODI, SPEC_RES,
)

TARGET = ef.PROXIMA_B
CAMPAIGN_ID = "life_proxima_b_earthlike_v1"
OUT = ef.REPO / "Thermal_Emission_Spectroscopy" / "outputs" / CAMPAIGN_ID
FWD = OUT / "forward_emission"
CF = OUT / "molecular_diagnostics"
TABLES = OUT / "tables"
LIFESIM = OUT / "lifesim"

REF_HOURS = 10.0
SCENARIOS = ["A0", "A1", "A2", "A3"]


def proxima_scene():
    return LifeSceneClassic(
        spec_res=SPEC_RES, diameter_m=2.0,
        temp_s=T_STAR, radius_s=R_STAR, distance_pc=D_PC,
        ecl_lat_rad=proxima_ecliptic_lat_rad(), exozodi=EXOZODI,
        angsep_arcsec=A_AU / D_PC,
    )


def load_full(s):
    d = np.load(FWD / f"{s}_emission.npz")
    return d["wl_um"], d["Fp_obs_W_m2_m"]


def load_reset(s, sp):
    d = np.load(CF / f"{s}_reset_{sp}_Fp_obs.npz")
    return d["wl_um"], d["Fp_obs_W_m2_m"]


def main():
    for d in (TABLES, LIFESIM):
        d.mkdir(parents=True, exist_ok=True)
    t_ref = REF_HOURS * 3600.0

    scene = proxima_scene()
    wl_um = scene.wl_bins_um
    wl_bins_m = scene.wl_bins
    print(f"[scene] Proxima LIFE X: R={scene.spec_res:.0f} D={scene.diameter_m}m "
          f"z={EXOZODI} d={D_PC}pc, {len(wl_um)} bins {wl_um[0]:.1f}-{wl_um[-1]:.1f}um")

    obs = {}
    for s in SCENARIOS:
        w, fp = load_full(s)
        obs[s] = scene.observe(w, fp, t_ref)
        print(f"[{s}] total continuum SNR(quad,10h) = "
              f"{np.sqrt(np.nansum(obs[s]['snr_per_bin']**2)):.1f}")

    signals = {}
    for s in PERTURBED:
        F_full = obs[s]["flux_binned_ph"]
        for sp in ALL_SPECIES:
            w, fp = load_reset(s, sp)
            signals[(s, sp)] = F_full - rebin_photon(w, fp, wl_bins_m)

    # persist per-bin products
    payload = {"wl_bins_um": wl_um, "t_ref_hours": REF_HOURS,
               "provenance": TARGET.provenance_label}
    for s in SCENARIOS:
        payload[f"flux_binned_{s}"] = obs[s]["flux_binned_ph"]
        payload[f"sigma_{s}"] = obs[s]["sigma_ph"]
        payload[f"snr_{s}"] = obs[s]["snr_per_bin"]
    for (s, sp), dF in signals.items():
        payload[f"dF_{s}_{sp}"] = dF
    np.savez_compressed(LIFESIM / "life_classic_binned_products.npz", **payload)

    rows = []
    for s in PERTURBED:
        sigma = obs[s]["sigma_ph"]
        for sp in ALL_SPECIES:
            dF = signals[(s, sp)]
            for (lo, hi) in BANDS[sp]:
                m = band_mask(wl_um, [(lo, hi)])
                per_bin = np.where((sigma > 0) & np.isfinite(sigma) & m,
                                   np.abs(dF) / sigma, 0.0)
                bi = int(np.argmax(per_bin))
                rows.append({
                    "scenario": s, "molecule": sp,
                    "role": "target" if sp in TARGETS else "control",
                    "band_um": f"{lo:.1f}-{hi:.1f}",
                    "band_SNR_10h": round(band_snr(dF, sigma, m), 3),
                    "best_bin_um": round(float(wl_um[bi]), 2),
                    "best_bin_SNR_10h": round(float(per_bin[bi]), 3),
                })

    csv_path = TABLES / "life_classic_snr_table.csv"
    with open(csv_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"[table] wrote {csv_path.relative_to(ef.REPO)} ({len(rows)} rows)")

    print("\n=== Proxima ExoFarm molecular signal — SNR por banda (t=10h, R=20, D=2m) ===")
    for r in rows:
        if r["molecule"] in TARGETS:
            print(f"  {r['scenario']} {r['molecule']:>4} {r['band_um']:>10} um: "
                  f"SNR_banda={r['band_SNR_10h']:>7}  pico={r['best_bin_SNR_10h']:>6} "
                  f"@{r['best_bin_um']}um")

    # sqrt(t) verification
    tot = [np.sqrt(np.nansum(scene.observe(*load_full("A3"), th * 3600.0)["snr_per_bin"] ** 2))
           for th in (1.0, 10.0, 100.0)]
    print(f"\n[sqrt(t) check] A3 total SNR 1/10/100h = {tot[0]:.1f}/{tot[1]:.1f}/{tot[2]:.1f} "
          f"(ratio {tot[2]/tot[0]:.1f})")
    print("[done]")


if __name__ == "__main__":
    main()
