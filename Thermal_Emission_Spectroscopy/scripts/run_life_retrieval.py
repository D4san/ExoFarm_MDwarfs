"""Run a POSEIDON emission retrieval on one LIFE synthetic dataset.

Retrieves a flexible PT profile plus a configurable abundance parameterization
for the radiatively active species from the LIFE observable
(`spectrum_unit='Fp'`, `spectrum_type='direct_emission'`). The default model is
deliberately simpler than the truth (VULCAN vertical profiles), while selected
species can be given POSEIDON's ``gradient`` or ``two-gradients`` profile. That
model choice is part of the experiment and must be stated when interpreting
posteriors, exactly as the transmission campaign does.

Usage (one run; memory-safe: never launch alongside VULCAN):
    source /home/wsldasan/miniconda3/etc/profile.d/conda.sh
    conda activate POSEIDON
    python run_life_retrieval.py --campaign proxima --scenario A3 --hours 500 \
        --x-profile two-gradients --vertical-gradient-species NH3

For an audit dataset with a non-standard filename, pass ``--dataset-file`` and
use ``--output-tag`` to keep its MultiNest products separate from the canonical
retrieval matrix.

Caveats carried by every product: sigma is diagonal (LIFEsim classic photon
noise, no instrumental covariance); one noise realization per dataset; Proxima
is a controlled Earth-like analogue, not Proxima b's measured atmosphere.
"""

import argparse
from pathlib import Path

import numpy as np

from POSEIDON.core import (create_star, create_planet, define_model, load_data,
                           set_priors, wl_grid_constant_R, read_opacities)
from POSEIDON.retrieval import run_retrieval

import emission_forward as ef

CAMPAIGNS = {
    "proxima": ("life_proxima_b_earthlike_v1", ef.PROXIMA_B, "LIFE_proxima"),
    "earth_sun": ("life_earth_sun_10pc_interface_v1", ef.EARTH_SUN, "LIFE_earth_sun"),
}
# Retrieved species: the two ExoFarm targets plus the main mid-IR absorbers.
PARAM_SPECIES = ["H2O", "CO2", "CH4", "O3", "N2O", "NH3"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign", choices=list(CAMPAIGNS), default="proxima")
    ap.add_argument("--scenario", required=True, choices=["A0", "A1", "A2", "A3"])
    ap.add_argument("--hours", required=True, type=float)
    ap.add_argument("--n-live", type=int, default=400)
    ap.add_argument(
        "--dataset-file", type=Path, default=None,
        help="optional dataset path relative to the repository root",
    )
    ap.add_argument(
        "--output-tag", default="",
        help="suffix for the retrieval name, e.g. _lifesim_direct",
    )
    ap.add_argument(
        "--x-profile", choices=["isochem", "gradient", "two-gradients"],
        default="isochem",
        help="POSEIDON abundance profile parameterization",
    )
    ap.add_argument(
        "--vertical-gradient-species", nargs="+", choices=PARAM_SPECIES,
        default=[],
        help="species that use a vertical gradient profile",
    )
    ap.add_argument("--wl-min", type=float, default=3.8)
    ap.add_argument("--wl-max", type=float, default=19.0)
    ap.add_argument("--R", type=int, default=2000)
    args = ap.parse_args()

    if args.x_profile == "isochem" and args.vertical_gradient_species:
        raise SystemExit(
            "[abort] --vertical-gradient-species requires --x-profile "
            "gradient or two-gradients"
        )

    campaign_id, target, prefix = CAMPAIGNS[args.campaign]
    out_root = ef.REPO / "Thermal_Emission_Spectroscopy" / "outputs" / campaign_id
    if args.dataset_file is None:
        data_dir = out_root / "life_data"
        dataset = f"{prefix}_{args.scenario}_{int(args.hours)}h.dat"
    else:
        dataset_path = args.dataset_file
        if not dataset_path.is_absolute():
            dataset_path = ef.REPO / dataset_path
        data_dir = dataset_path.parent
        dataset = dataset_path.name
    if not (data_dir / dataset).exists():
        raise SystemExit(f"[abort] falta {dataset}; corre make_life_datasets.py")

    # POSEIDON writes retrieval products relative to the CWD; keep them together.
    run_dir = out_root / "retrievals"
    run_dir.mkdir(parents=True, exist_ok=True)
    import os
    os.chdir(run_dir)

    retrieval_name = (f"{args.campaign}_{args.scenario}_{int(args.hours)}h"
                      f"{args.output_tag}")
    print(f"[retrieval] {retrieval_name}  (n_live={args.n_live})")

    wl = wl_grid_constant_R(args.wl_min, args.wl_max, args.R)
    star = ef.build_star(wl, target)
    planet = ef.build_planet(target)

    # Retrieval model. The truth is a 120-layer VULCAN atmosphere, so a rigid PT
    # parameterization cannot fit data whose sigma is <1% of the flux: the first
    # pilot (2-parameter gradient PT) drove the likelihood to ln(Z)~-9e6 and
    # MultiNest terminated without sampling. Two standard remedies are applied:
    #   - Madhu (Madhusudhan & Seager 2009) PT: 6 free parameters, flexible
    #     enough to track a real temperate thermal structure;
    #   - error_inflation='Piette20' (Piette et al. 2020): a free fractional
    #     parameter `x_tol` that inflates the per-bin errors, the accepted way to
    #     absorb model mismatch rather than let it masquerade as a confident
    #     (wrong) posterior.
    # Abundances are isochemical unless selected on the command line. For the
    # A3 audit run, NH3 uses POSEIDON's two-gradient profile so the strong
    # VULCAN depletion with altitude is representable instead of being forced
    # into one column-like abundance.
    model = define_model(
        retrieval_name, ef.BULK_SPECIES, PARAM_SPECIES,
        PT_profile="Madhu", X_profile=args.x_profile, X_dim=1,
        species_vert_gradient=args.vertical_gradient_species,
        radius_unit="R_E", surface=True,
        thermal=True, thermal_scattering=False,
        # Piette20 (fractional) rather than Line15 (absolute): the likelihood
        # uses err^2 + (x_tol*model)^2, which is scale-invariant. Line15 adds
        # 10^b in *data units squared* — with Fp ~1e-12 W m^-2 m^-1 that prior is
        # impossible to set sanely (the second pilot inflated errors by ~28
        # orders of magnitude and left every abundance unconstrained).
        error_inflation="Piette20",
    )

    data = load_data(str(data_dir), [dataset], ["LIFE"], wl,
                     skiprows=1, wl_unit="micron", bin_width="half",
                     spectrum_unit="Fp")

    # Priors: broad but physical. The isochemical abundance prior extends to
    # 1e-12 so a non-detection can be expressed; surface pressure is free within
    # 0.1-10 bar. Madhu PT ranges follow the standard parameterization, with
    # T_ref bracketing a temperate rocky atmosphere. `x_tol` is the Piette20
    # fractional error-inflation parameter.
    prior_types = {
        "a1": "uniform", "a2": "uniform", "log_P1": "uniform",
        "log_P2": "uniform", "log_P3": "uniform", "T_ref": "uniform",
        "log_X": "uniform", "R_p_ref": "uniform", "log_P_surf": "uniform",
        "x_tol": "uniform",
    }
    prior_ranges = {
        "a1": [0.02, 2.0], "a2": [0.02, 2.0],
        "log_P1": [-6, 1], "log_P2": [-6, 1], "log_P3": [-2, 1],
        "T_ref": [150, 400],
        "log_X": [-12, -1],
        # NOTE: POSEIDON divides this prior by the radius unit internally
        # (core.py set_priors), so it must be given in METRES, not in R_E.
        # Passing it already in R_E is what drove the third pilot to a
        # nonsensical R_p_ref ~ 2e-7 R_E (the value got divided twice).
        "R_p_ref": [0.8 * target.planet["R_p"], 1.3 * target.planet["R_p"]],
        "log_P_surf": [-1, 1],
        # Fractional model-mismatch tolerance: up to 30% of the model flux.
        "x_tol": [0.0, 0.3],
    }
    if args.x_profile == "two-gradients":
        # POSEIDON's two-gradient profile introduces a transition pressure and
        # high/mid/deep abundances for each selected species. The pressure prior
        # covers the A3 NH3 transition near 10^-1--10^-2 bar while retaining
        # room for the data to move it.
        prior_types["log_P_X_mid"] = "uniform"
        prior_ranges["log_P_X_mid"] = [-5, 0]
        if "NH3" in args.vertical_gradient_species:
            # A3 NH3 falls to ~10^-20 above the upper atmosphere in the VULCAN
            # profile, so the generic -12 lower bound would artificially force
            # excess upper-atmosphere NH3 into the retrieval.
            prior_types.update({
                "log_NH3_high": "uniform",
                "log_NH3_mid": "uniform",
                "log_P_NH3_mid": "uniform",
                "log_NH3_deep": "uniform",
            })
            prior_ranges.update({
                "log_NH3_high": [-25, -3],
                "log_NH3_mid": [-12, -1],
                "log_P_NH3_mid": [-5, 0],
                "log_NH3_deep": [-12, -1],
            })
    priors = set_priors(planet, star, model, data, prior_types, prior_ranges)

    P = np.logspace(np.log10(target.P_max_bar), np.log10(target.P_min_bar), 100)
    opac = ef.read_opacities_for(model, wl)

    run_retrieval(
        planet, star, model, opac, data, priors, wl, P,
        P_ref=target.P_max_bar, R_p_ref=target.planet["R_p"],
        spectrum_type="direct_emission",
        R=args.R, retrieval_name=retrieval_name,
        N_live=args.n_live, verbose=True,
    )
    print(f"[done] {retrieval_name}")


if __name__ == "__main__":
    main()
