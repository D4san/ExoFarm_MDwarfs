"""Convert the MUSCLES v22 Proxima Centauri SED to a VULCAN surface-flux file.

Source product (preserved with checksum under Config/Stellar_Spectra/):
    hlsp_muscles_multi_multi_gj551_broadband_v22_adapt-const-res-sed.fits
    (MUSCLES Treasury Survey HLSP, MAST, DOI 10.17909/T9DG6F; France et al.
    2016; Youngblood et al. 2016; Loyd et al. 2016. Downloaded 2026-07-22 via
    astroquery.mast from mast:HLSP/muscles/v22/gj551/.)

MUSCLES reports flux density OBSERVED AT EARTH: FLUX [erg s^-1 cm^-2 A^-1] vs
WAVELENGTH [Angstrom]. VULCAN instead expects the flux AT THE STELLAR SURFACE
in [erg s^-1 cm^-2 nm^-1] vs [nm] (see VULCAN/atm/stellar_flux/*.txt and
docs/photochemical_profiles_methodology.md), and later rescales it itself to
the planetary orbit with (R_star/orbit_radius)^2. Therefore this script applies
the SINGLE geometric scaling

    F_surface(lambda) = F_obs(lambda) * (d / R_star)^2

and nothing else; using the same R_star in the VULCAN config guarantees the
R_star dependence cancels in the flux at the orbit (F_orbit = F_obs*(d/a)^2).

Adopted (frozen) parameters — LIFE X input catalogue, so the photochemistry,
the POSEIDON planet and the LIFE scene share one citable source:
    d      = 1.30 pc      (Carrión-González et al. 2023, Table G.1)
    R_star = 0.14 R_sun   (idem)

Unit conversions applied:
    wavelength: Angstrom -> nm  (/10)
    flux:       per-Angstrom -> per-nm  (*10)

Validation printed by the script:
    - bolometric integral of the observed SED vs the Ribas et al. (2017)
      luminosity L = 0.00151 L_sun placed at 1.30 pc;
    - Lyman-alpha and FUV/NUV band integrals (sanity, must be > 0);
    - fraction of negative-flux samples clipped to zero.

Output: VULCAN/atm/stellar_flux/ProximaCen_surface.txt
"""

from pathlib import Path

import numpy as np
from astropy.io import fits

REPO = Path(__file__).resolve().parents[3]
FITS_PATH = (REPO / "Photochemical_Modeling" / "Config" / "Stellar_Spectra" /
             "hlsp_muscles_multi_multi_gj551_broadband_v22_adapt-const-res-sed.fits")
OUT_PATH = REPO / "VULCAN" / "atm" / "stellar_flux" / "ProximaCen_surface.txt"

PC_CM = 3.0856775814913673e18
R_SUN_CM = 6.957e10
L_SUN = 3.828e33                     # erg/s (IAU nominal)

D_PC = 1.30                          # LIFE X, Table G.1
R_STAR_RSUN = 0.14                   # LIFE X, Table G.1
L_BOL_LSUN = 0.00151                 # Ribas et al. 2017 (validation only)


def main():
    with fits.open(FITS_PATH) as hdul:
        data = hdul[1].data
    wl_A = np.asarray(data["WAVELENGTH"], dtype=float)     # Angstrom
    f_obs_A = np.asarray(data["FLUX"], dtype=float)        # erg s-1 cm-2 A-1 at Earth

    # --- validation 1: bolometric integral vs Ribas+2017 luminosity --------
    F_bol_obs = np.trapz(np.clip(f_obs_A, 0, None), wl_A)  # erg s-1 cm-2
    d_cm = D_PC * PC_CM
    F_bol_expected = L_BOL_LSUN * L_SUN / (4.0 * np.pi * d_cm**2)
    print(f"[val] integral bolométrica SED  = {F_bol_obs:.3e} erg s-1 cm-2")
    print(f"[val] L=0.00151 Lsun @ 1.30 pc  = {F_bol_expected:.3e} erg s-1 cm-2")
    print(f"[val] razón SED/esperado        = {F_bol_obs / F_bol_expected:.3f} "
          f"(aceptable ~0.8-1.2)")

    # --- validation 2: key UV bands must carry flux ------------------------
    def band(lo_A, hi_A):
        m = (wl_A >= lo_A) & (wl_A <= hi_A)
        return np.trapz(np.clip(f_obs_A[m], 0, None), wl_A[m])
    print(f"[val] Ly-alpha 1210-1222 A      = {band(1210, 1222):.3e} erg s-1 cm-2")
    print(f"[val] FUV 912-1700 A            = {band(912, 1700):.3e} erg s-1 cm-2")
    print(f"[val] NUV 1700-3200 A           = {band(1700, 3200):.3e} erg s-1 cm-2")

    # --- clip unphysical negatives (noise in faint continuum windows) ------
    n_neg = int((f_obs_A < 0).sum())
    print(f"[val] muestras negativas -> 0    : {n_neg} de {len(f_obs_A)} "
          f"({100.0 * n_neg / len(f_obs_A):.2f}%)")
    f_obs_A = np.clip(f_obs_A, 0.0, None)

    # --- single geometric scaling to the stellar surface -------------------
    r_star_cm = R_STAR_RSUN * R_SUN_CM
    scale = (d_cm / r_star_cm) ** 2
    print(f"[conv] d/R_star = {d_cm / r_star_cm:.6e}  ->  (d/R_star)^2 = {scale:.6e}")

    wl_nm = wl_A / 10.0
    f_surf_nm = f_obs_A * 10.0 * scale     # per-A -> per-nm, then to surface

    header = (
        "# Wavelength(nm)    Flux(erg/cm2/s/nm)  at the STELLAR SURFACE\n"
        "# Proxima Centauri (GJ 551). Source: MUSCLES v22 adapt-const-res SED\n"
        "# (MAST HLSP, DOI 10.17909/T9DG6F; France et al. 2016), flux observed\n"
        f"# at Earth, scaled by (d/R_star)^2 = {scale:.6e} with d = {D_PC} pc,\n"
        f"# R_star = {R_STAR_RSUN} R_sun (Carrión-González et al. 2023, Table G.1).\n"
        "# Converted 2026-07-22 by convert_proxima_muscles_sed.py; negatives\n"
        "# clipped to zero. VULCAN rescales to the orbit with (R_star/a)^2."
    )
    np.savetxt(OUT_PATH, np.column_stack([wl_nm, f_surf_nm]),
               fmt="%.6e", header=header, comments="")
    print(f"[out] {OUT_PATH.relative_to(REPO)}  "
          f"({len(wl_nm)} filas, {wl_nm[0]:.2f}-{wl_nm[-1]:.1f} nm)")


if __name__ == "__main__":
    main()
