"""Generate POSEIDON-compatible LIFE synthetic datasets for the retrieval matrix.

For each (target, scenario, integration time) this writes a 4-column .dat file
POSEIDON's `load_data(..., spectrum_unit='Fp')` can read:

    wavelength[um]   half_bin_width[um]   Fp[W m^-2 m^-1]   sigma_Fp

Inputs are the already-validated products of the emission + LIFEsim-classic
chain: the noise-free forward spectrum (rebinned onto the LIFE grid) and the
per-bin 1-sigma noise at the reference 10 h, scaled as sigma(t) = sigma(10h) *
sqrt(10/t) (photon-noise scaling verified in both layers).

The stored noise is in ENERGY flux units to match POSEIDON's 'Fp': the LIFEsim
sigma is a photon flux density, so it is converted back with sigma_F =
sigma_ph * hc/lambda (the exact inverse of the forward conversion).

Integration times follow docs/life_retrieval_campaign_design_2026-07-25.md:
10 h (LIFE X detection), 240 h ~10 d (LIFE XII standard M-dwarf case), 1200 h
= 50 d (LIFE XII challenging-but-feasible / LIFE III ~7 weeks).

One Gaussian noise realization per file, with a recorded per-file seed.
"""

import argparse
import json

import numpy as np
from spectres import spectres

import emission_forward as ef
from life_scene_classic import fp_obs_to_photon_flux

H_PLANCK = 6.62607015e-34
C_LIGHT = 2.99792458e8

CAMPAIGNS = {
    "proxima": ("life_proxima_b_earthlike_v1", ef.PROXIMA_B),
    "earth_sun": ("life_earth_sun_10pc_interface_v1", ef.EARTH_SUN),
}
HOURS = [10.0, 240.0]  # short (LIFE X) + standard ~10 d (LIFE XII); 1200 h dropped: A2/A3 already separate from A0 in one standard campaign, and lower S/N reduces model mismatch
SCENARIOS = ["A0", "A1", "A2", "A3"]
REF_HOURS = 10.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign", choices=list(CAMPAIGNS), default="proxima")
    ap.add_argument("--scenarios", nargs="+", default=SCENARIOS)
    ap.add_argument("--hours", nargs="+", type=float, default=HOURS)
    ap.add_argument("--seed", type=int, default=20260725)
    args = ap.parse_args()

    campaign_id, target = CAMPAIGNS[args.campaign]
    out_root = ef.REPO / "Thermal_Emission_Spectroscopy" / "outputs" / campaign_id
    prod = np.load(out_root / "lifesim" / "life_classic_binned_products.npz",
                   allow_pickle=True)
    data_dir = out_root / "life_data"
    data_dir.mkdir(parents=True, exist_ok=True)

    wl_bins_um = prod["wl_bins_um"]
    wl_bins_m = wl_bins_um * 1e-6
    # Half-bin widths from the LIFE grid spacing (log-spaced -> use midpoints).
    edges = np.concatenate(([wl_bins_um[0] - 0.5 * (wl_bins_um[1] - wl_bins_um[0])],
                            0.5 * (wl_bins_um[1:] + wl_bins_um[:-1]),
                            [wl_bins_um[-1] + 0.5 * (wl_bins_um[-1] - wl_bins_um[-2])]))
    half_width = 0.5 * np.diff(edges)

    # photon -> energy conversion factor per bin (inverse of the forward one)
    ph_to_energy = H_PLANCK * C_LIGHT / wl_bins_m

    index = []
    rng_master = np.random.default_rng(args.seed)
    for scen in args.scenarios:
        # Noise-free model on the LIFE grid, in energy units (W m^-2 m^-1).
        d = np.load(out_root / "forward_emission" / f"{scen}_emission.npz")
        wl_m_native, F_ph_native = fp_obs_to_photon_flux(d["wl_um"],
                                                         d["Fp_obs_W_m2_m"])
        F_ph_binned = spectres(wl_bins_m, wl_m_native, F_ph_native,
                               fill=0.0, verbose=False)
        F_energy = F_ph_binned * ph_to_energy

        sigma_ph_ref = prod[f"sigma_{scen}"]
        for t_h in args.hours:
            sigma_ph = sigma_ph_ref * np.sqrt(REF_HOURS / t_h)
            sigma_energy = sigma_ph * ph_to_energy
            ok = np.isfinite(sigma_energy) & (sigma_energy > 0) & (F_energy > 0)

            seed = int(rng_master.integers(1, 2**31 - 1))
            noise = np.random.default_rng(seed).normal(0.0, 1.0, size=F_energy.size)
            F_obs = F_energy + noise * np.where(ok, sigma_energy, 0.0)

            name = f"LIFE_{args.campaign}_{scen}_{int(t_h)}h.dat"
            block = np.column_stack([wl_bins_um[ok], half_width[ok],
                                     F_obs[ok], sigma_energy[ok]])
            np.savetxt(data_dir / name, block,
                       header="wavelength(um) half_bin(um) Fp(W m^-2 m^-1) sigma_Fp",
                       comments="", fmt="%.6e")
            snr_med = float(np.median((F_energy[ok] / sigma_energy[ok])))
            index.append({"file": name, "campaign": campaign_id,
                          "scenario": scen, "hours": t_h, "seed": seed,
                          "n_bins": int(ok.sum()),
                          "median_continuum_SNR": round(snr_med, 2)})
            print(f"[{scen} {t_h:6.0f} h] {name}  bins={ok.sum():3d} "
                  f"median continuum S/N={snr_med:8.1f}  seed={seed}")

    with open(data_dir / "dataset_index.json", "w") as fh:
        json.dump({"generated_from": campaign_id, "master_seed": args.seed,
                   "sigma_scaling": "sigma(t)=sigma(10h)*sqrt(10/t)",
                   "units": "Fp in W m^-2 m^-1 (POSEIDON spectrum_unit='Fp')",
                   "datasets": index}, fh, indent=2)
    print(f"\n[index] {(data_dir / 'dataset_index.json').relative_to(ef.REPO)}")


if __name__ == "__main__":
    main()
