"""Generate POSEIDON-compatible LIFE synthetic datasets for the retrieval matrix.

For each (target, scenario, integration time) this writes a 4-column .dat file
POSEIDON's `load_data(..., spectrum_unit='Fp')` can read:

    wavelength[um]   half_bin_width[um]   Fp[W m^-2 m^-1]   sigma_Fp

Inputs are the already-validated products of the emission + LIFEsim-classic
chain: the noise-free forward spectrum and the per-bin 1-sigma noise. The
default route scales the validated 10 h sigma as
sigma(t) = sigma(10h) * sqrt(10/t); `--direct-lifesim` instead calls LIFEsim
at each requested integration time.

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
from importlib.metadata import version
from pathlib import Path

import numpy as np
import emission_forward as ef
from spectres import spectres

# Capture this before importing LIFEsim: its package initialization changes the
# process CWD to its installation directory.
INITIAL_CWD = Path.cwd()

H_PLANCK = 6.62607015e-34
C_LIGHT = 2.99792458e8

CAMPAIGNS = {
    "proxima": ("life_proxima_b_earthlike_v1", ef.PROXIMA_B),
    "earth_sun": ("life_earth_sun_10pc_interface_v1", ef.EARTH_SUN),
}
HOURS = [10.0, 240.0]  # short (LIFE X) + standard ~10 d (LIFE XII); 1200 h dropped: A2/A3 already separate from A0 in one standard campaign, and lower S/N reduces model mismatch
SCENARIOS = ["A0", "A1", "A2", "A3"]
REF_HOURS = 10.0


def direct_scene(campaign):
    """Build the LIFEsim classic scene for a direct observation.

    The Proxima parameters are kept in the LIFE-X calibration module so this
    dataset generator cannot silently fall back to the Earth--Sun defaults.
    """
    if campaign == "earth_sun":
        from life_scene_classic import LifeSceneClassic

        return LifeSceneClassic()

    from validate_proxima_life_scene import (
        A_AU, D_PC, EXOZODI, R_STAR, SPEC_RES, T_STAR,
        proxima_ecliptic_lat_rad,
    )
    from life_scene_classic import LifeSceneClassic

    return LifeSceneClassic(
        spec_res=SPEC_RES, diameter_m=2.0,
        temp_s=T_STAR, radius_s=R_STAR, distance_pc=D_PC,
        ecl_lat_rad=proxima_ecliptic_lat_rad(), exozodi=EXOZODI,
        angsep_arcsec=A_AU / D_PC,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign", choices=list(CAMPAIGNS), default="proxima")
    ap.add_argument("--scenarios", nargs="+", default=SCENARIOS)
    ap.add_argument("--hours", nargs="+", type=float, default=HOURS)
    ap.add_argument("--seed", type=int, default=20260725)
    ap.add_argument(
        "--index-output",
        type=Path,
        default=None,
        help="write the dataset index to this path instead of the canonical index",
    )
    ap.add_argument(
        "--index-classification",
        default="audit/pilot dataset; excluded from canonical matrix",
        help=(
            "classification recorded in a non-canonical dataset index; use "
            "only with --index-output"
        ),
    )
    ap.add_argument(
        "--direct-lifesim",
        action="store_true",
        help="call LIFEsim classic at each requested integration time instead of scaling sigma",
    )
    ap.add_argument(
        "--name-suffix",
        default="",
        help="suffix appended before .dat, e.g. _lifesim_direct",
    )
    args = ap.parse_args()
    # LIFEsim may change the process CWD while initializing its data bus.  Fix
    # a user-supplied relative index path before that happens.
    index_output = args.index_output
    if index_output is not None and not index_output.is_absolute():
        index_output = (INITIAL_CWD / index_output).resolve()

    campaign_id, target = CAMPAIGNS[args.campaign]
    from life_scene_classic import fp_obs_to_photon_flux

    out_root = ef.REPO / "Thermal_Emission_Spectroscopy" / "outputs" / campaign_id
    prod = None
    scene = None
    if args.direct_lifesim:
        scene = direct_scene(args.campaign)
    else:
        prod = np.load(out_root / "lifesim" / "life_classic_binned_products.npz",
                       allow_pickle=True)
    data_dir = out_root / "life_data"
    data_dir.mkdir(parents=True, exist_ok=True)

    wl_bins_um = (np.asarray(scene.wl_bins_um) if args.direct_lifesim
                  else prod["wl_bins_um"])
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
        for t_h in args.hours:
            if args.direct_lifesim:
                observed = scene.observe(
                    d["wl_um"], d["Fp_obs_W_m2_m"], t_h * 3600.0)
                F_ph_binned = observed["flux_binned_ph"]
                sigma_ph = observed["sigma_ph"]
            else:
                wl_m_native, F_ph_native = fp_obs_to_photon_flux(
                    d["wl_um"], d["Fp_obs_W_m2_m"])
                F_ph_binned = spectres(wl_bins_m, wl_m_native, F_ph_native,
                                        fill=0.0, verbose=False)
                sigma_ph_ref = prod[f"sigma_{scen}"]
                sigma_ph = sigma_ph_ref * np.sqrt(REF_HOURS / t_h)

            F_energy = F_ph_binned * ph_to_energy
            sigma_energy = sigma_ph * ph_to_energy
            ok = np.isfinite(sigma_energy) & (sigma_energy > 0) & (F_energy > 0)

            seed = int(rng_master.integers(1, 2**31 - 1))
            noise = np.random.default_rng(seed).normal(0.0, 1.0, size=F_energy.size)
            F_obs = F_energy + noise * np.where(ok, sigma_energy, 0.0)

            name = (f"LIFE_{args.campaign}_{scen}_{int(t_h)}h"
                    f"{args.name_suffix}.dat")
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
            method_tag = "direct LIFEsim" if args.direct_lifesim else "scaled sigma"
            print(f"[{scen} {t_h:6.0f} h] {name}  bins={ok.sum():3d} "
                  f"({method_tag}) "
                  f"median continuum S/N={snr_med:8.1f}  seed={seed}")

    index_path = index_output or (data_dir / "dataset_index.json")
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_payload = {
        "generated_from": campaign_id,
        "master_seed": args.seed,
        "sigma_scaling": ("none; LIFEsim called at each requested integration time"
                          if args.direct_lifesim
                          else "sigma(t)=sigma(10h)*sqrt(10/t)"),
        "generation_method": (
            "direct LIFEsim classic observation at requested integration time"
            if args.direct_lifesim
            else "scaled sigma from validated 10 h LIFEsim-classic bins"
        ),
        "units": "Fp in W m^-2 m^-1 (POSEIDON spectrum_unit='Fp')",
        "datasets": index,
    }
    if args.direct_lifesim:
        index_payload["lifesim_version"] = version("lifesim")
        index_payload["spectres_version"] = version("spectres")
    if index_output is not None:
        index_payload["classification"] = args.index_classification
        index_payload["canonical_index"] = str(data_dir / "dataset_index.json")
    with open(index_path, "w") as fh:
        json.dump(index_payload, fh, indent=2)
    index_abs = index_path.resolve()
    try:
        index_display = index_abs.relative_to(ef.REPO.resolve())
    except ValueError:
        index_display = index_abs
    print(f"\n[index] {index_display}")


if __name__ == "__main__":
    main()
