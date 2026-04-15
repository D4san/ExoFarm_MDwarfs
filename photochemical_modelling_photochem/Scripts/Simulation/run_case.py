import argparse
import json

from common import (
    atmosphere_output_path,
    get_planet_for_run,
    get_run,
    get_star,
    get_surface_mixing_ratio,
    initial_atmosphere_path,
    load_catalog,
    mechanism_data_dir,
    mechanism_output_path,
    read_atmosphere_output,
    settings_output_path,
    stellar_flux_path,
    summary_output_path,
)
from prepare_photochem_inputs import prepare_run


def require_photochem():
    try:
        from photochem import EvoAtmosphere  # noqa: F401
    except ImportError as exc:
        raise RuntimeError(
            "photochem is not installed. Install photochem before running a case."
        ) from exc


def get_surface_temperature(output_path):
    if not output_path.exists():
        return None
    _, columns = read_atmosphere_output(output_path)
    pressure = columns["press"]
    surface_index = int(pressure.argmax())
    return float(columns["temp"][surface_index])


def run_case(run_id, force_prepare=False):
    require_photochem()
    from photochem import EvoAtmosphere

    catalog = load_catalog()
    run = get_run(run_id)
    planet = get_planet_for_run(run_id)
    star = get_star(run["star"])

    prepare_run(run_id, force=force_prepare)

    mechanism_file = mechanism_output_path()
    settings_file = settings_output_path(run_id)
    flux_file = stellar_flux_path(star)
    initial_atmosphere_file = initial_atmosphere_path(run_id)
    output_file = atmosphere_output_path(run_id)
    summary_file = summary_output_path(run_id)

    pc = EvoAtmosphere(
        str(mechanism_file),
        str(settings_file),
        str(flux_file),
        str(initial_atmosphere_file),
        data_dir=str(mechanism_data_dir()),
    )
    pc.var.verbose = 0
    pc.update_vertical_grid(TOA_pressure=catalog["model"]["target_toa_pressure_bar"] * 1.0e6)
    converged = bool(pc.find_steady_state())
    pc.out2atmosphere_txt(str(output_file), overwrite=True)

    surface_fluxes, top_fluxes = pc.gas_fluxes()
    tracked_species = catalog["model"]["tracked_species"]
    surface_mixing_ratios = {
        species: get_surface_mixing_ratio(output_file, species)
        for species in tracked_species
    }

    summary = {
        "run_id": run_id,
        "planet": run.get("planet", catalog["model"].get("default_planet", "earth")),
        "planet_label": planet.get("label"),
        "star": run["star"],
        "scenario": run["scenario"],
        "converged": converged,
        "surface_temperature_k": get_surface_temperature(output_file),
        "output_atmosphere": str(output_file),
        "settings_file": str(settings_file),
        "stellar_flux_file": str(flux_file),
        "initial_atmosphere_file": str(initial_atmosphere_file),
        "surface_mixing_ratios": surface_mixing_ratios,
        "surface_fluxes_molecules_cm2_s": {
            species: float(surface_fluxes[species])
            for species in tracked_species
            if species in surface_fluxes
        },
        "top_fluxes_molecules_cm2_s": {
            species: float(top_fluxes[species])
            for species in ("H", "H2")
            if species in top_fluxes
        }
    }

    with summary_file.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    return converged


def main():
    parser = argparse.ArgumentParser(description="Run a single named photochem case.")
    parser.add_argument("run_id", help="Run identifier from Config/catalog.json")
    parser.add_argument(
        "--force-prepare",
        action="store_true",
        help="Rebuild prepared inputs before the run.",
    )
    args = parser.parse_args()

    converged = run_case(args.run_id, force_prepare=args.force_prepare)
    print(f"{args.run_id}: converged={converged}")


if __name__ == "__main__":
    main()
