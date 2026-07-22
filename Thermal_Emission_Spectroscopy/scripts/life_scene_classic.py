"""LIFEsim (classic) observing scene for `life_earth_sun_10pc` (Layer 1).

Wraps the LIFEsim classic Bus/Instrument setup and the POSEIDON->LIFE units
conversion into a small reusable API. This tool models the *astrophysical /
photon-noise* case (stellar leakage, local zodi, exozodi, shot noise); it is the
quick sensitivity/SNR-vs-time branch. The instrumental-instability + covariance
case is LIFEsimMC/PHRINGE (separate module).

Units gate (validated 2026-07-22):
  POSEIDON direct_emission  Fp_obs   [W m^-2 m^-1]   (observed planet flux at d)
      -> photon flux density F_ph = Fp_obs * wl/(h c)  [ph m^-2 s^-1 m^-1]
      -> passed to Instrument.get_spectrum as astropy Quantities [wl(m), F_ph].
`get_spectrum` rebins internally onto the LIFE bins and returns SNR per bin.
"""

from dataclasses import dataclass, field

import numpy as np
import astropy.units as u
import lifesim

H_PLANCK = 6.62607015e-34
C_LIGHT = 2.99792458e8

# --- Earth--Sun @ 10 pc scene (interface benchmark) -------------------------
SUN = dict(temp_s=5772.0, radius_s=1.0)     # K, R_sun
DISTANCE_PC = 10.0
ECL_LAT_RAD = 0.79                          # ~45 deg ecliptic latitude (local-zodi pointing)
EXOZODI = 1.0                               # solar-system-like exozodi [zodis]
ANGSEP_ARCSEC = 0.1                         # 1 AU at 10 pc = 0.1"
# LIFE baseline array with the characterization resolution R=50 (Quanz+2022).
LIFE_DIAMETER_M = 2.0
LIFE_R = 50.0
LIFE_WL_MIN, LIFE_WL_MAX = 4.0, 18.5


def fp_obs_to_photon_flux(wl_um, Fp_obs_W_m2_m):
    """Convert POSEIDON direct_emission flux to LIFEsim photon flux density.

    Fp_obs [W m^-2 m^-1] -> [ph m^-2 s^-1 m^-1] using E_photon = h c / wl.
    """
    wl_m = wl_um * 1e-6
    return wl_m, Fp_obs_W_m2_m * wl_m / (H_PLANCK * C_LIGHT)


@dataclass
class LifeSceneClassic:
    spec_res: float = LIFE_R
    diameter_m: float = LIFE_DIAMETER_M
    wl_min: float = LIFE_WL_MIN
    wl_max: float = LIFE_WL_MAX
    _inst: object = field(default=None, repr=False)

    def __post_init__(self):
        bus = lifesim.Bus()
        bus.data.options.set_scenario("baseline")
        bus.data.options.set_manual(
            spec_res=self.spec_res, diameter=self.diameter_m,
            wl_min=self.wl_min, wl_max=self.wl_max,
        )
        inst = lifesim.Instrument(name="inst")
        bus.add_module(inst)
        for cls, nm in [
            (lifesim.TransmissionMap, "tm"),
            (lifesim.PhotonNoiseStar, "sl"),
            (lifesim.PhotonNoiseLocalzodi, "lz"),
            (lifesim.PhotonNoiseExozodi, "ez"),
        ]:
            bus.add_module(cls(name=nm))
        for c in [("inst", "tm"), ("inst", "sl"), ("inst", "lz"),
                  ("inst", "ez"), ("sl", "tm")]:
            bus.connect(c)
        inst.apply_options()
        self._inst = inst
        self.wl_bins = np.array(bus.data.inst["wl_bins"])          # m
        self.wl_bins_um = self.wl_bins * 1e6

    def observe(self, wl_um, Fp_obs_W_m2_m, integration_time_s):
        """Observe a POSEIDON emission spectrum. Returns a dict with per-bin
        SNR, the noise-free binned flux, and sigma (all photon-flux-density)."""
        from spectres import spectres

        wl_m, F_ph = fp_obs_to_photon_flux(wl_um, Fp_obs_W_m2_m)
        fps = [wl_m * u.m, F_ph * (u.ph / u.m**3 / u.s)]
        (wl_bins, snr_spec), flux_ph, noise_ph = self._inst.get_spectrum(
            temp_s=SUN["temp_s"], radius_s=SUN["radius_s"],
            distance_s=DISTANCE_PC, lat_s=ECL_LAT_RAD, z=EXOZODI,
            angsep=ANGSEP_ARCSEC, flux_planet_spectrum=fps,
            integration_time=integration_time_s,
        )
        wl_bins = np.array(wl_bins)
        snr = np.array(snr_spec)
        # Noise-free binned flux on the LIFE grid (photon flux density).
        F_binned = spectres(wl_bins, wl_m, F_ph, fill=0.0, verbose=False)
        # Per-bin 1-sigma flux uncertainty from SNR = signal/sigma.
        with np.errstate(divide="ignore", invalid="ignore"):
            sigma = np.where(snr > 0, F_binned / snr, np.inf)
        return {
            "wl_bins_m": wl_bins,
            "wl_bins_um": wl_bins * 1e6,
            "snr_per_bin": snr,
            "flux_binned_ph": F_binned,
            "sigma_ph": sigma,
            "integration_time_s": integration_time_s,
        }
