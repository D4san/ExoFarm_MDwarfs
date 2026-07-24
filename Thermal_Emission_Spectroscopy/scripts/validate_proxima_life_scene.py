"""Calibration gate for the Proxima b LIFE scene against LIFE X anchors.

Reproduces the LIFE X (Carrión-González et al. 2023, A&A 678, A96) detectability
setup for Proxima Cen b and compares our LIFEsim-classic scene against their
Table 3 anchors BEFORE any molecular diagnostics:

    D = 1 m   -> S/N = 45   (10 h)
    D = 2 m   -> S/N = 170  (10 h)   [reference configuration]
    D = 3.5 m -> S/N = 466  (10 h)

Scene, frozen from LIFE X (Tables 2 and G.1): R=20, 4-18.5 um, exozodi z=3,
star T=3050 K, R=0.14 R_sun, d=1.30 pc; planet as a blackbody with
T_eq = 229 K, R_p = 1.23 R_E; angular separation a/d with a=0.0485 AU.
The ecliptic latitude is computed from Proxima's ICRS coordinates with astropy.

Passing criterion (documented, not silent): same order of magnitude and within
~+-40% of each anchor — LIFE X medians come from 1000 orbital realizations
(inclination/phase averaging) that we do not replicate for a single epoch.
"""

import numpy as np
import astropy.units as u
from astropy.coordinates import SkyCoord, BarycentricTrueEcliptic

from life_scene_classic import LifeSceneClassic

# --- LIFE X frozen parameters (Carrión-González et al. 2023) ----------------
T_STAR = 3050.0        # K            (Table G.1)
R_STAR = 0.14          # R_sun        (Table G.1)
D_PC = 1.30            # pc           (Table G.1)
A_AU = 0.0485          # AU           (Anglada-Escudé et al. 2016; LIFE X: 0.05)
T_EQ = 229.0           # K            (Table G.1)
R_P_RE = 1.23          # R_E          (Table G.1, via Otegi et al. 2020)
EXOZODI = 3.0          # zodis        (LIFE X Sect. 3)
SPEC_RES = 20.0        # lambda/dlambda (LIFE X Table 2)
T_INT_H = 10.0
ANCHORS = {1.0: 45.0, 2.0: 170.0, 3.5: 466.0}   # Table 3, S/N in 10 h

R_E_M = 6.3781e6
PC_M = 3.0856775814913673e16


def proxima_ecliptic_lat_rad():
    c = SkyCoord(ra="14h29m42.95s", dec="-62d40m46.1s", frame="icrs")
    beta = c.transform_to(BarycentricTrueEcliptic()).lat.to(u.rad).value
    return abs(beta)


def blackbody_fp_obs(wl_um, T, r_p_m, d_m):
    """Observed blackbody planet flux [W m^-2 m^-1] at distance d."""
    h, c, kB = 6.62607015e-34, 2.99792458e8, 1.380649e-23
    wl_m = wl_um * 1e-6
    B = (2 * h * c**2 / wl_m**5) / np.expm1(h * c / (wl_m * kB * T))
    return np.pi * B * (r_p_m / d_m) ** 2


def main():
    lat = proxima_ecliptic_lat_rad()
    angsep = A_AU / D_PC
    print(f"[scene] Proxima: lat_ecl={np.degrees(lat):.1f} deg  angsep={angsep:.4f}\"")

    wl_um = np.linspace(3.5, 19.5, 4000)
    fp_obs = blackbody_fp_obs(wl_um, T_EQ, R_P_RE * R_E_M, D_PC * PC_M)

    print(f"\n{'D[m]':>5} {'S/N(10h) nuestro':>17} {'LIFE X':>7} {'razón':>6}")
    for D, anchor in ANCHORS.items():
        scene = LifeSceneClassic(
            spec_res=SPEC_RES, diameter_m=D,
            temp_s=T_STAR, radius_s=R_STAR, distance_pc=D_PC,
            ecl_lat_rad=lat, exozodi=EXOZODI, angsep_arcsec=angsep,
        )
        o = scene.observe(wl_um, fp_obs, T_INT_H * 3600.0)
        snr_tot = float(np.sqrt(np.nansum(o["snr_per_bin"] ** 2)))
        print(f"{D:>5.1f} {snr_tot:>17.1f} {anchor:>7.0f} {snr_tot / anchor:>6.2f}")

    print("\nCriterio: razón ~0.6-1.4 en las tres aperturas -> escena calibrada.")


if __name__ == "__main__":
    main()
