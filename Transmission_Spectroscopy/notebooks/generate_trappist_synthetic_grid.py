import argparse

from exofarm_transmission_workflow import (
    OBSERVATION_TRANSIT_COUNTS,
    SCENARIOS,
    compute_forward_spectra,
    create_pressure_grid,
    create_trappist_system,
    define_forward_models,
    generate_synthetic_grid,
    load_profiles,
    make_atmospheres,
    make_wavelength_grid_and_opacities,
    prepare_pandexo_base_data,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Generate TRAPPIST-1e forward spectra and synthetic JWST datasets "
            "for the ExoFarm A0-A3 grid."
        )
    )
    parser.add_argument(
        "--scenarios",
        nargs="+",
        choices=sorted(SCENARIOS),
        default=sorted(SCENARIOS),
        help="Scenario keys to generate.",
    )
    parser.add_argument(
        "--transits",
        nargs="+",
        type=int,
        choices=OBSERVATION_TRANSIT_COUNTS,
        default=OBSERVATION_TRANSIT_COUNTS,
        help="Transit counts for NIRSpec and MIRI.",
    )
    parser.add_argument(
        "--no-scatter",
        action="store_true",
        help="Generate deterministic synthetic data without Gaussian scatter.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    scenario_keys = list(args.scenarios)

    star, planet = create_trappist_system()
    P, P_surf, P_ref, R_p_ref = create_pressure_grid()
    models = define_forward_models(scenario_keys)
    temperatures, compositions = load_profiles(models, P, scenario_keys)
    atmospheres = make_atmospheres(
        planet,
        models,
        P,
        P_ref,
        R_p_ref,
        P_surf,
        temperatures,
        compositions,
    )
    wl, opac = make_wavelength_grid_and_opacities(models[scenario_keys[0]])
    spectra = compute_forward_spectra(planet, star, models, atmospheres, opac, wl)
    data_base, _ = prepare_pandexo_base_data(wl)

    runs = generate_synthetic_grid(
        planet,
        wl,
        spectra,
        data_base,
        scenario_keys,
        args.transits,
        gauss_scatter=not args.no_scatter,
    )

    print("\nGenerated synthetic datasets:")
    for (scenario_key, n_obs), run in sorted(runs.items()):
        print(f" - {scenario_key}, {n_obs}+{n_obs} transits")
        for dataset in run["datasets"]:
            print(f"   {dataset}")


if __name__ == "__main__":
    main()
