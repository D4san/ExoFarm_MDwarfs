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

Binning provenance: this general runner uses POSEIDON's standard observation
operator. The A3-1000 h generator-compatible operator was validated and used by
the separately scoped ``run_life_retrieval_binning_corrected.py`` wrapper; that
wrapper is frozen to one dataset hash and is not a general replacement. Treat
the standard operator as the historical reproduction path. Before launching a
new LIFE inference, validate generator/likelihood bin equivalence for that
dataset or use a scope-validated corrected wrapper; do not mix operators in a
paired evidence comparison.

The legacy ``--surface-pressure-mode fixed-bottom`` removes ``log_P_surf`` by
setting ``surface=False`` while retaining the 1-bar pressure-grid bottom.
The 2026-09-23 forward-swap audit demonstrated that this is *not* equivalent
to the explicit opaque surface at 1 bar used to generate the LIFE data.
Preserve this mode only to reproduce existing audit retrievals; do not label
its products as fixed-black-surface retrievals or use them for detection claims.

Caveats carried by every product: sigma is diagonal (LIFEsim classic photon
noise, no instrumental covariance); one noise realization per dataset; Proxima
is a controlled Earth-like analogue, not Proxima b's measured atmosphere.
"""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from POSEIDON.core import (create_star, create_planet, define_model, load_data,
                           set_priors, wl_grid_constant_R, read_opacities,
                           make_atmosphere, compute_spectrum)
from POSEIDON.retrieval import run_retrieval

import emission_forward as ef
from fixed_abundance_reference import constrain_priors, load_fixed_abundances

CAMPAIGNS = {
    "proxima": ("life_proxima_b_earthlike_v1", ef.PROXIMA_B, "LIFE_proxima"),
    "earth_sun": ("life_earth_sun_10pc_interface_v1", ef.EARTH_SUN, "LIFE_earth_sun"),
}
# Retrieved species: the two ExoFarm targets plus the main mid-IR absorbers.
PARAM_SPECIES = ["H2O", "CO2", "CH4", "O3", "N2O", "NH3"]
ALL_RETRIEVABLE_SPECIES = ["H2O", "CO2", "CH4", "O2", "O3", "N2O", "NH3"]
SURFACE_PRESSURE_MIN_BAR = 0.1


def validate_truth_forward(planet, star, model, wl, P, target, dataset_path):
    """Check that the corrected retrieval interface reproduces LIFE A3 truth."""
    if not model["surface"] or "O2" not in model["chemical_species"]:
        raise ValueError("Forward validation requires an explicit surface and O2")

    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from audit_proxima_a3_retrieval_residuals import rebin_energy_flux

    truth_model = ef.build_model("A3", target)
    if not np.array_equal(
        truth_model["chemical_species"], model["chemical_species"]
    ):
        raise ValueError("Retrieval and truth models use different species order")
    T_true, X_true = ef.load_profiles(truth_model, P, "A3", target)
    opac = ef.read_opacities_for(truth_model, wl)
    atmosphere = make_atmosphere(
        planet, truth_model, P, target.P_max_bar, target.planet["R_p"],
        surface_params=np.array([np.log10(target.P_max_bar)]),
        T_input=T_true, X_input=X_true,
    )
    candidate_flux = compute_spectrum(
        planet, star, truth_model, atmosphere, opac, wl,
        spectrum_type="direct_emission",
    )
    if not np.all(np.isfinite(candidate_flux)):
        raise ValueError("Fixed-interface forward contains NaN/Inf")

    campaign_dir = (
        ef.REPO / "Thermal_Emission_Spectroscopy" / "outputs"
        / "life_proxima_b_earthlike_v1"
    )
    with np.load(campaign_dir / "forward_emission" / "A3_emission.npz") as saved:
        truth_wl = np.asarray(saved["wl_um"], dtype=float)
        truth_flux = np.asarray(saved["Fp_obs_W_m2_m"], dtype=float)
    with np.load(campaign_dir / "lifesim" / "life_classic_binned_products.npz") as life:
        wl_bins = np.asarray(life["wl_bins_um"], dtype=float)
    truth_binned = rebin_energy_flux(truth_wl, truth_flux, wl_bins)
    candidate_binned = rebin_energy_flux(wl, candidate_flux, wl_bins)
    dataset = np.loadtxt(dataset_path, skiprows=1)
    if dataset.shape != (wl_bins.size, 4):
        raise ValueError(f"Unexpected validation dataset shape: {dataset.shape}")
    delta_sigma = (candidate_binned - truth_binned) / dataset[:, 3]
    rms_sigma = float(np.sqrt(np.mean(delta_sigma**2)))
    max_sigma = float(np.max(np.abs(delta_sigma)))
    print(
        f"[forward-validation] RMS={rms_sigma:.4g} sigma, "
        f"max={max_sigma:.4g} sigma across {wl_bins.size} LIFE bins",
        flush=True,
    )
    if rms_sigma > 0.3 or max_sigma > 1.0:
        raise ValueError(
            "The fixed-surface/O2 model is not sufficiently close to A3 LIFE "
            f"truth (RMS={rms_sigma:.3g}, max={max_sigma:.3g} sigma)"
        )


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
        "--vertical-gradient-species", nargs="+", choices=ALL_RETRIEVABLE_SPECIES,
        default=[],
        help="species that use a vertical gradient profile",
    )
    ap.add_argument(
        "--error-inflation", choices=["Piette20", "none"],
        default="Piette20",
        help="fractional model-error term or photon-noise-only likelihood",
    )
    ap.add_argument(
        "--surface-pressure-mode",
        choices=["free", "fixed-bottom", "fixed-black"],
        default="free",
        help=(
            "retrieve P_surf; use legacy surface=False; or fix an explicit "
            "black surface at the pressure-grid bottom"
        ),
    )
    ap.add_argument(
        "--include-o2", action="store_true",
        help="retrieve O2 explicitly in addition to the default species",
    )
    ap.add_argument(
        "--exclude-species", nargs="+", choices=ALL_RETRIEVABLE_SPECIES,
        default=[], metavar="SPECIES",
        help=(
            "omit molecular opacity and its abundance parameter for the "
            "specified species (leave-one-molecule-out comparisons)"
        ),
    )
    ap.add_argument(
        "--a0-reference", type=Path,
        help="frozen A0 scalar-reference JSON; requires --fix-a0-species",
    )
    ap.add_argument(
        "--fix-a0-species", nargs="+", choices=["N2O", "NH3"], default=[],
        help="retain opacity but fix log10 VMR to the frozen A0 reference",
    )
    ap.add_argument(
        "--configuration-json", type=Path,
        help="write resolved priors and input hashes for matched-model auditing",
    )
    ap.add_argument(
        "--validate-forward", action="store_true",
        help="compare the corrected model with the saved noiseless LIFE A3 forward",
    )
    ap.add_argument("--wl-min", type=float, default=3.8)
    ap.add_argument("--wl-max", type=float, default=19.0)
    ap.add_argument("--R", type=int, default=2000)
    ap.add_argument(
        "--setup-only", action="store_true",
        help="validate model parameters, data, and priors without running MultiNest",
    )
    ap.add_argument(
        "--resume", action="store_true",
        help="resume MultiNest from an existing checkpoint for this retrieval name",
    )
    ap.add_argument(
        "--run-dir", type=Path, default=None,
        help="optional absolute directory for POSEIDON outputs (default: campaign retrievals)",
    )
    args = ap.parse_args()

    fixed_abundances = {}
    if bool(args.a0_reference) != bool(args.fix_a0_species):
        raise SystemExit("[abort] A0 reference and fixed species must be supplied together")
    if args.fix_a0_species:
        if args.x_profile != "isochem" or args.campaign != "proxima":
            raise SystemExit("[abort] fixed A0 currently requires Proxima isochem")
        if set(args.fix_a0_species) & set(args.exclude_species):
            raise SystemExit("[abort] fixed species must retain their opacity")
        reference_path = args.a0_reference.resolve()
        fixed_abundances = load_fixed_abundances(
            reference_path, args.fix_a0_species, ef.REPO
        )
    configuration_path = (
        args.configuration_json.resolve() if args.configuration_json else None
    )

    if args.x_profile == "isochem" and args.vertical_gradient_species:
        raise SystemExit(
            "[abort] --vertical-gradient-species requires --x-profile "
            "gradient or two-gradients"
        )
    if args.exclude_species:
        available_species = set(PARAM_SPECIES)
        if args.include_o2:
            available_species.add("O2")
        excluded_species = set(args.exclude_species)
        inactive_species = excluded_species - available_species
        if inactive_species:
            raise SystemExit(
                "[abort] cannot exclude species that are not active in this "
                f"model: {', '.join(sorted(inactive_species))}; use "
                "--include-o2 to make O2 an active retrieval species"
            )
        if excluded_species & set(args.vertical_gradient_species):
            raise SystemExit(
                "[abort] a species cannot be excluded and assigned a "
                "vertical gradient in the same retrieval"
            )
        if args.validate_forward:
            raise SystemExit(
                "[abort] forward-identity validation is not applicable to a "
                "model that intentionally excludes molecular opacity"
            )
    if args.surface_pressure_mode == "fixed-black" and not args.include_o2:
        raise SystemExit(
            "[abort] fixed-black mode for the Proxima A3 audit requires --include-o2"
        )
    if "O2" in args.vertical_gradient_species and not args.include_o2:
        raise SystemExit("[abort] retrieving an O2 gradient requires --include-o2")
    if args.validate_forward and (
        args.campaign != "proxima" or args.scenario != "A3"
    ):
        raise SystemExit("[abort] --validate-forward is currently specific to Proxima A3")

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

    # POSEIDON writes retrieval products relative to the CWD; allow local Linux
    # scratch for MPI I/O while keeping datasets and source files in the repo.
    run_dir = args.run_dir if args.run_dir is not None else out_root / "retrievals"
    if not run_dir.is_absolute():
        raise SystemExit("[abort] --run-dir must be an absolute path")
    run_dir.mkdir(parents=True, exist_ok=True)
    import os
    os.chdir(run_dir)

    retrieval_name = (f"{args.campaign}_{args.scenario}_{int(args.hours)}h"
                      f"{args.output_tag}")
    print(
        f"[retrieval] {retrieval_name}  (n_live={args.n_live}, "
        f"resume={args.resume})"
    )
    print(f"[run_dir] {run_dir}")
    print(
        "[configuration] "
        f"error_inflation={args.error_inflation}, "
        f"surface_pressure_mode={args.surface_pressure_mode}, "
        f"X_profile={args.x_profile}, "
        f"excluded_species={','.join(sorted(set(args.exclude_species))) or 'none'}"
    )

    wl = wl_grid_constant_R(args.wl_min, args.wl_max, args.R)
    star = ef.build_star(wl, target)
    planet = ef.build_planet(target)

    # Retrieval model. The truth is a 120-layer VULCAN atmosphere, so a rigid PT
    # parameterization cannot fit data whose sigma is <1% of the flux: the first
    # pilot (2-parameter gradient PT) drove the likelihood to ln(Z)~-9e6 and
    # MultiNest terminated without sampling. Madhu (Madhusudhan & Seager 2009)
    # supplies the flexible six-parameter PT profile. Production runs may also
    # use error_inflation='Piette20' (Piette et al. 2020); audit runs can disable
    # it explicitly to expose the photon-noise-only model tension.
    # Abundances are isochemical unless a gradient profile is selected
    # explicitly. The matched A1/A3 audit comparison uses isochem for every
    # retrieved molecule; separate gradient experiments remain distinct runs.
    retrieve_surface_pressure = args.surface_pressure_mode in {"free", "fixed-black"}
    param_species = list(PARAM_SPECIES)
    if args.include_o2:
        param_species.insert(param_species.index("O3"), "O2")
    excluded_species = set(args.exclude_species)
    param_species = [
        species for species in param_species if species not in excluded_species
    ]
    if not param_species:
        raise SystemExit(
            "[abort] at least one molecular species must remain in the model"
        )
    error_inflation = (
        None if args.error_inflation == "none" else args.error_inflation
    )

    model = define_model(
        retrieval_name, ef.BULK_SPECIES, param_species,
        PT_profile="Madhu", X_profile=args.x_profile, X_dim=1,
        species_vert_gradient=args.vertical_gradient_species,
        radius_unit="R_E", surface=retrieve_surface_pressure,
        thermal=True, thermal_scattering=False,
        # Piette20 (fractional) rather than Line15 (absolute): the likelihood
        # uses err^2 + (x_tol*model)^2, which is scale-invariant. Line15 adds
        # 10^b in *data units squared* — with Fp ~1e-12 W m^-2 m^-1 that prior is
        # impossible to set sanely (the second pilot inflated errors by ~28
        # orders of magnitude and left every abundance unconstrained).
        error_inflation=error_inflation,
    )

    if args.error_inflation == "none" and "x_tol" in model["param_names"]:
        raise RuntimeError("x_tol remains free in a no-inflation retrieval")
    if (not retrieve_surface_pressure and
            "log_P_surf" in model["param_names"]):
        raise RuntimeError("log_P_surf remains free in fixed-bottom mode")
    if (args.surface_pressure_mode == "fixed-black" and
            "log_P_surf" not in model["param_names"]):
        raise RuntimeError("fixed-black mode requires POSEIDON's surface parameter")

    data = load_data(str(data_dir), [dataset], ["LIFE"], wl,
                     skiprows=1, wl_unit="micron", bin_width="half",
                     spectrum_unit="Fp")

    # Priors: broad but physical. The isochemical abundance prior extends to
    # 1e-12 so a non-detection can be expressed. When P_surf is retrieved, its
    # prior is restricted to the model pressure grid; this avoids the former
    # 1--10 bar plateau when the grid itself ended at 1 bar. Madhu PT ranges
    # follow the standard parameterization, with T_ref bracketing a temperate
    # rocky atmosphere. `x_tol` is only present for Piette20 runs.
    prior_types = {
        "a1": "uniform", "a2": "uniform", "log_P1": "uniform",
        "log_P2": "uniform", "log_P3": "uniform", "T_ref": "uniform",
        "log_X": "uniform", "R_p_ref": "uniform",
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
    }
    if retrieve_surface_pressure:
        prior_types["log_P_surf"] = "uniform"
        if args.surface_pressure_mode == "fixed-black":
            fixed_log_p_surf = float(np.log10(target.P_max_bar))
            prior_ranges["log_P_surf"] = [fixed_log_p_surf, fixed_log_p_surf]
        else:
            prior_ranges["log_P_surf"] = [
                np.log10(SURFACE_PRESSURE_MIN_BAR),
                np.log10(target.P_max_bar),
            ]
    if args.include_o2:
        # The prior contains the Proxima A3 truth, X_O2 ~= 0.20.
        prior_types["log_O2"] = "uniform"
        prior_ranges["log_O2"] = [-6.0, np.log10(0.5)]
    if args.error_inflation == "Piette20":
        prior_types["x_tol"] = "uniform"
        # Fractional model-mismatch tolerance: up to 30% of the model flux.
        prior_ranges["x_tol"] = [0.0, 0.3]
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
    # Keep species/opacities identical to the full model. POSEIDON's installed
    # 1D prior transform maps every unit-cube draw to the same value when the
    # endpoints coincide, as already used for the fixed black surface.
    constrain_priors(prior_types, prior_ranges, fixed_abundances)
    priors = set_priors(planet, star, model, data, prior_types, prior_ranges)
    for species, value in fixed_abundances.items():
        if priors["prior_ranges"]["log_" + species] != [value, value]:
            raise RuntimeError(f"Fixed prior changed for {species}")
    fixed_parameters = [
        name for name in model["param_names"]
        if priors["prior_types"][name] == "uniform"
        and priors["prior_ranges"][name][0] == priors["prior_ranges"][name][1]
    ]
    print(f"[fixed-abundances] {json.dumps(fixed_abundances, sort_keys=True)}")
    print(f"[effective-free-parameters] {len(model['param_names']) - len(fixed_parameters)}")
    if configuration_path:
        configuration = {
            "model_name": retrieval_name,
            "parameters": list(model["param_names"]),
            "declared_dimension": len(model["param_names"]),
            "effective_free_dimension": len(model["param_names"]) - len(fixed_parameters),
            "fixed_parameters": fixed_parameters,
            "fixed_log10_abundances": fixed_abundances,
            "param_species": list(model["param_species"]),
            "prior_types": priors["prior_types"],
            "prior_ranges": priors["prior_ranges"],
            "dataset_sha256": hashlib.sha256((data_dir / dataset).read_bytes()).hexdigest(),
            "R": args.R, "wl_min": args.wl_min, "wl_max": args.wl_max,
            "n_live": args.n_live, "ev_tol": 0.5,
            "surface_pressure_mode": args.surface_pressure_mode,
            "error_inflation": args.error_inflation, "x_profile": args.x_profile,
            "likelihood": "direct_emission; diagonal Gaussian; same observed Fp",
        }
        configuration_path.parent.mkdir(parents=True, exist_ok=True)
        if configuration_path.exists():
            previous = json.loads(configuration_path.read_text(encoding="utf-8"))
            if previous != configuration:
                raise RuntimeError("Resolved configuration changed; preserve prior record")
        else:
            configuration_path.write_text(
                json.dumps(configuration, indent=2) + "\n", encoding="utf-8"
            )

    P = np.logspace(np.log10(target.P_max_bar), np.log10(target.P_min_bar), 100)
    if args.surface_pressure_mode == "fixed-bottom":
        print(
            "[surface] LEGACY surface=False with pressure-grid bottom at "
            f"P={target.P_max_bar:g} bar; no explicit black surface; "
            "log_P_surf is not retrieved"
        )
    elif args.surface_pressure_mode == "fixed-black":
        print(
            "[surface] explicit opaque surface fixed at "
            f"P={target.P_max_bar:g} bar; O2 included; "
            "log_P_surf has a zero-width prior"
        )
    print(f"[parameters] {len(model['param_names'])}: "
          + ", ".join(model["param_names"]))
    if args.setup_only:
        print("[setup-only] model, dataset, and priors validated; MultiNest skipped")
        if args.validate_forward:
            validate_truth_forward(
                planet, star, model, wl, P, target, data_dir / dataset
            )
        return
    opac = ef.read_opacities_for(model, wl)

    run_retrieval(
        planet, star, model, opac, data, priors, wl, P,
        P_ref=target.P_max_bar, R_p_ref=target.planet["R_p"],
        spectrum_type="direct_emission",
        # POSEIDON prepends model["model_name"] to an explicit retrieval_name.
        # This runner already puts the full campaign tag in model_name, so
        # passing the same string again duplicates the basename and can hit
        # MultiNest's observed 100-character output-root limit.
        R=args.R, retrieval_name=None,
        N_live=args.n_live, resume=args.resume, verbose=True,
    )
    print(f"[done] {retrieval_name}")


if __name__ == "__main__":
    main()
