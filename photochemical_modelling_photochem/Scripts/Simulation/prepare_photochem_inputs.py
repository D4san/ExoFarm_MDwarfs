import argparse
import os
from pathlib import Path

import yaml

from common import (
    build_initial_atmosphere_for_run,
    build_settings_for_run,
    get_run,
    get_star,
    list_runs,
    load_catalog,
    load_stellar_surface_spectrum,
    mechanism_data_dir,
    mechanism_output_path,
    mechanism_root,
    project_path,
    read_mechanism_species,
    save_photochem_stellar_flux,
    scale_surface_flux_to_planet,
    stellar_flux_path,
)


def require_photochem():
    try:
        from photochem.utils import stars, vulcan2yaml  # noqa: F401
        from photochem.clima import AdiabatClimate  # noqa: F401
    except ImportError as exc:
        raise RuntimeError(
            "photochem is not installed. Install photochem before running this preparation step."
        ) from exc


def _split_equation(equation):
    for token in ("<=>", "=>"):
        if token in equation:
            lhs, rhs = equation.split(token, 1)
            return lhs.strip(), rhs.strip()
    return None, None


def sanitize_mechanism_file(path):
    mechanism_path = Path(path)
    mechanism = yaml.safe_load(mechanism_path.read_text(encoding="utf-8"))
    reactions = mechanism.get("reactions", [])
    cleaned = []
    removed = []

    for reaction in reactions:
        equation = reaction.get("equation", "")
        lhs, rhs = _split_equation(equation)
        if lhs is not None and lhs == rhs:
            removed.append(equation)
            continue
        cleaned.append(reaction)

    mechanism["reactions"] = cleaned
    mechanism_path.write_text(yaml.safe_dump(mechanism, sort_keys=False), encoding="utf-8")
    return removed


def prepare_mechanism(force=False):
    require_photochem()
    from photochem.utils import vulcan2yaml

    catalog = load_catalog()
    output_file = mechanism_output_path()
    data_dir = mechanism_data_dir()
    if output_file.exists() and data_dir.exists() and not force:
        return output_file

    mechanism_root()
    current_workdir = Path.cwd()
    os.chdir(mechanism_root())
    try:
        vulcan2yaml(
            str(project_path(catalog["model"]["vulcan_network_file"])),
            str(project_path(catalog["model"]["vulcan_thermo_dir"])),
        )
    finally:
        os.chdir(current_workdir)

    generated_name = Path(catalog["model"]["vulcan_network_file"]).name.replace(".txt", ".yaml")
    generated_file = mechanism_root() / generated_name
    if generated_file != output_file and generated_file.exists():
        generated_file.replace(output_file)

    removed = sanitize_mechanism_file(output_file)
    if removed:
        print(f"Removed {len(removed)} identity reactions from {output_file.name}: {', '.join(removed)}")

    return output_file


def prepare_stellar_flux(star_key, force=False):
    require_photochem()
    from photochem.utils import stars

    star_config = get_star(star_key)
    output_path = stellar_flux_path(star_config)
    if output_path.exists() and not force:
        return output_path

    if star_config["strategy"] == "solar_spectrum":
        stars.solar_spectrum(
            outputfile=str(output_path),
            age=star_config["age_ga"],
            stellar_flux=star_config["stellar_flux_w_m2"],
            scale_before_age=True,
        )
    elif star_config["strategy"] == "hazmat_spectrum":
        stars.hazmat_spectrum(
            star_name=star_config["hazmat_star_name"],
            model=star_config["hazmat_model"],
            outputfile=str(output_path),
            stellar_flux=star_config["stellar_flux_w_m2"],
        )
    elif star_config["strategy"] == "local_surface_spectrum":
        wavelength_nm, surface_flux = load_stellar_surface_spectrum(
            project_path(star_config["source_spectrum_file"])
        )
        flux_planet = scale_surface_flux_to_planet(
            surface_flux=surface_flux,
            stellar_radius_solar=star_config["stellar_radius_solar"],
            orbital_distance_au=star_config["orbital_distance_au"],
        )
        save_photochem_stellar_flux(output_path, wavelength_nm, flux_planet)
    else:
        raise ValueError(f"Unknown stellar strategy: {star_config['strategy']}")

    return output_path


def prepare_run(run_id, force=False):
    run = get_run(run_id)
    mechanism_file = prepare_mechanism(force=force)
    gas_species, particle_species = read_mechanism_species(mechanism_file)
    prepare_stellar_flux(run["star"], force=force)
    build_settings_for_run(run_id, gas_species)
    build_initial_atmosphere_for_run(run_id, gas_species, particle_species)


def main():
    parser = argparse.ArgumentParser(description="Prepare photochem inputs for one or more named runs.")
    parser.add_argument(
        "run_id",
        nargs="?",
        default="all",
        help="Run identifier from Config/catalog.json, or 'all'.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rebuild existing prepared files.",
    )
    args = parser.parse_args()

    if args.run_id == "all":
        run_ids = [run["id"] for run in list_runs()]
    else:
        run_ids = [args.run_id]

    for run_id in run_ids:
        print(f"Preparing inputs for {run_id}")
        prepare_run(run_id, force=args.force)


if __name__ == "__main__":
    main()

