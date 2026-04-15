import argparse
import json
from pathlib import Path

import numpy as np

from common import (
    K_BOLTZMANN_CGS,
    atmosphere_output_path,
    climate_root,
    dump_yaml,
    get_planet_for_run,
    get_run,
    get_scenario,
    get_star,
    initial_atmosphere_root,
    load_catalog,
    load_yaml,
    mechanism_data_dir,
    mechanism_output_path,
    mechanism_root,
    planet_config_value,
    project_path,
    read_mechanism_species,
    read_pressure_temperature_kzz,
    settings_output_path,
    settings_root,
    stellar_flux_path,
    summary_output_path,
)
from prepare_photochem_inputs import prepare_mechanism, prepare_stellar_flux


EXCLUDED_CLIMATE_PARTICLES = {"H2Oaer"}


def require_photochem():
    try:
        from photochem import EvoAtmosphere  # noqa: F401
    except ImportError as exc:
        raise RuntimeError(
            "photochem is not installed. Run this script in the WSL environment where photochem is available."
        ) from exc


def vulcan_profile_paths(run):
    stem = run["profile_stem"]
    chem = project_path(f"Transmission_Spectroscopy/profiles/{stem}_chem.txt")
    pt = project_path(f"Transmission_Spectroscopy/profiles/{stem}_PT.txt")
    return chem, pt


def experimental_mechanism_path(run_id):
    return mechanism_root() / f"{run_id}_vulcan_init_evolving_climate_mechanism.yaml"


def experimental_initial_atmosphere_path(run_id):
    return initial_atmosphere_root() / f"{run_id}_vulcan_init_evolving_climate_atmosphere.txt"


def experimental_settings_path(run_id):
    return settings_root() / f"{run_id}_vulcan_init_evolving_climate_settings.yaml"


def experimental_binary_output_path(run_id):
    return climate_root() / f"{run_id}_vulcan_init_evolving_climate_evolution.bin"


def experimental_output_path(run_id):
    return atmosphere_output_path(f"{run_id}_vulcan_init_evolving_climate")


def experimental_summary_path(run_id):
    return summary_output_path(f"{run_id}_vulcan_init_evolving_climate")


def load_table(path):
    with Path(path).open("r", encoding="utf-8-sig") as handle:
        header = handle.readline().strip().split()
        data = np.loadtxt(handle)
    if data.ndim == 1:
        data = data[None, :]
    columns = {name: data[:, index] for index, name in enumerate(header)}
    return header, columns


def interpolate_log_pressure(source_pressure_bar, source_values, target_pressure_bar):
    source_pressure_bar = np.asarray(source_pressure_bar, dtype=float)
    source_values = np.asarray(source_values, dtype=float)
    target_pressure_bar = np.asarray(target_pressure_bar, dtype=float)

    order = np.argsort(np.log10(source_pressure_bar))
    xp = np.log10(source_pressure_bar[order])
    yp = source_values[order]
    return np.interp(np.log10(target_pressure_bar), xp, yp)


def build_experimental_mechanism(run_id, source_mechanism_path):
    mechanism = load_yaml(source_mechanism_path)
    mechanism["particles"] = [
        entry for entry in mechanism.get("particles", []) if entry["name"] not in EXCLUDED_CLIMATE_PARTICLES
    ]
    output_path = experimental_mechanism_path(run_id)
    dump_yaml(mechanism, output_path)
    return output_path


def build_vulcan_initialized_atmosphere(run_id, gas_species, particle_species):
    catalog = load_catalog()
    run = get_run(run_id)
    planet = get_planet_for_run(run_id)
    floor = float(catalog["model"]["seed_floor_mixing_ratio"])
    particle_radius_cm = float(catalog["model"]["particle_radius_cm"])
    fallback = catalog["model"]["fallback_initial_mixing_ratios"]

    chem_path, pt_path = vulcan_profile_paths(run)
    chem_header, chem_columns = load_table(chem_path)
    _, pt_columns = load_table(pt_path)

    pressure_bar = np.asarray(pt_columns["P"], dtype=float)
    temperature_k = np.asarray(pt_columns["T"], dtype=float)
    altitude_km = np.asarray(pt_columns["ALT"], dtype=float)
    pressure_cgs = pressure_bar * 1.0e6
    density = pressure_cgs / (K_BOLTZMANN_CGS * temperature_k)

    kzz_pressure_cgs, _, kzz_values = read_pressure_temperature_kzz(
        project_path(planet_config_value(planet, "pressure_temperature_kzz_file"))
    )
    eddy = interpolate_log_pressure(kzz_pressure_cgs / 1.0e6, kzz_values, pressure_bar)

    chem_species = set(chem_header)
    matrix_columns = []
    surface_density_bc = {}
    surface_index = int(np.argmax(pressure_bar))

    for species in gas_species:
        if species in chem_species:
            values = np.asarray(chem_columns[species], dtype=float)
        elif species in fallback:
            values = np.ones_like(pressure_bar) * float(fallback[species])
        else:
            values = np.ones_like(pressure_bar) * floor

        values = np.maximum(values, floor)
        matrix_columns.append(values)
        surface_density_bc[species] = float(values[surface_index] * density[surface_index])

    for _species in particle_species:
        matrix_columns.append(np.ones_like(pressure_bar) * floor)
    for _species in particle_species:
        matrix_columns.append(np.ones_like(pressure_bar) * particle_radius_cm)

    header = ["alt", "press", "den", "temp", "eddy"] + gas_species + particle_species + [
        f"{species}_r" for species in particle_species
    ]
    data_columns = [altitude_km, pressure_cgs, density, temperature_k, eddy] + matrix_columns
    data = np.column_stack(data_columns)

    output_path = experimental_initial_atmosphere_path(run_id)
    with output_path.open("w", encoding="utf-8") as handle:
        handle.write(" ".join(header) + "\n")
        np.savetxt(handle, data, fmt="%.8e")

    top_altitude_cm = float(np.max(altitude_km) * 1.0e5)
    return output_path, surface_density_bc, top_altitude_cm


def build_evolving_climate_settings(run_id, gas_species, particle_species, surface_density_bc, top_altitude_cm):
    planet = get_planet_for_run(run_id)
    climate = planet.get("climate", {})
    base_settings_path = settings_output_path(run_id)
    if not base_settings_path.exists():
        raise FileNotFoundError(f"Prepared settings not found: {base_settings_path}")

    settings = load_yaml(base_settings_path)
    climate_template = load_yaml(project_path(climate["settings_template"]))

    settings["atmosphere-grid"]["top"] = float(top_altitude_cm)
    settings["atmosphere-grid"]["number-of-layers"] = int(
        climate.get("number_of_layers", climate_template["atmosphere-grid"]["number-of-layers"])
    )
    settings["planet"]["evolve-climate"] = True
    settings["planet"]["number-of-zenith-angles"] = int(climate_template["planet"].get("number-of-zenith-angles", 1))
    settings["optical-properties"] = climate_template["optical-properties"]
    settings["particles"] = [
        entry for entry in settings.get("particles", []) if entry.get("name") not in EXCLUDED_CLIMATE_PARTICLES
    ]

    water = settings["planet"].setdefault("water", {})
    water["fix-water-in-troposphere"] = True
    water["relative-humidity"] = float(climate.get("relative_humidity", 0.5))
    water["water-condensation"] = True
    if "tropopause-altitude" not in water:
        water["tropopause-altitude"] = 1.1e6

    converted = []
    for entry in settings.get("boundary-conditions", []):
        new_entry = json.loads(json.dumps(entry))
        lower = new_entry.get("lower-boundary")
        if lower and lower.get("type") == "press":
            species = new_entry["name"]
            if species == "H2O":
                continue
            if species not in surface_density_bc:
                raise KeyError(f"Missing surface density for fixed-pressure species {species}")
            new_entry["lower-boundary"] = {
                "type": "den",
                "den": float(surface_density_bc[species]),
            }
        converted.append(new_entry)

    settings["boundary-conditions"] = [
        entry for entry in converted if entry["name"] in gas_species or entry.get("type") == "short lived"
    ]

    output_path = experimental_settings_path(run_id)
    dump_yaml(settings, output_path)
    return output_path


def get_surface_temperature(output_path):
    if not Path(output_path).exists():
        return None
    header, columns = load_table(output_path)
    if "temp" not in header:
        return None
    surface_index = int(np.argmax(columns["press"]))
    return float(columns["temp"][surface_index])


def run_case(run_id, force_prepare=False, t_end=1.0e10, n_times=40):
    require_photochem()
    from photochem import EvoAtmosphere

    run = get_run(run_id)
    star = get_star(run["star"])
    scenario = get_scenario(run["scenario"])

    source_mechanism_file = prepare_mechanism(force=force_prepare)
    mechanism_file = build_experimental_mechanism(run_id, source_mechanism_file)
    gas_species, particle_species = read_mechanism_species(mechanism_file)
    prepare_stellar_flux(run["star"], force=force_prepare)

    base_settings = settings_output_path(run_id)
    if not base_settings.exists() or force_prepare:
        from common import build_settings_for_run

        build_settings_for_run(run_id, gas_species)

    initial_atmosphere_file, surface_density_bc, top_altitude_cm = build_vulcan_initialized_atmosphere(
        run_id, gas_species, particle_species
    )
    settings_file = build_evolving_climate_settings(
        run_id,
        gas_species,
        particle_species,
        surface_density_bc,
        top_altitude_cm,
    )
    flux_file = stellar_flux_path(star)
    output_file = experimental_output_path(run_id)
    summary_file = experimental_summary_path(run_id)
    binary_file = experimental_binary_output_path(run_id)

    pc = EvoAtmosphere(
        str(mechanism_file),
        str(settings_file),
        str(flux_file),
        str(initial_atmosphere_file),
        data_dir=str(mechanism_data_dir()),
    )
    pc.var.verbose = 0

    t_eval = np.logspace(0.0, np.log10(float(t_end)), int(n_times))
    success = bool(pc.evolve(str(binary_file), 0.0, pc.wrk.usol, t_eval, overwrite=True))
    pc.out2atmosphere_txt(str(output_file), overwrite=True)

    surface_fluxes, top_fluxes = pc.gas_fluxes()
    tracked_species = load_catalog()["model"]["tracked_species"]
    summary = {
        "run_id": run_id,
        "mode": "vulcan_init_evolving_climate",
        "scenario": run["scenario"],
        "scenario_label": scenario.get("label"),
        "success": success,
        "t_end_s": float(t_end),
        "n_times": int(n_times),
        "mechanism_file": str(mechanism_file),
        "settings_file": str(settings_file),
        "initial_atmosphere_file": str(initial_atmosphere_file),
        "stellar_flux_file": str(flux_file),
        "binary_evolution_file": str(binary_file),
        "output_atmosphere": str(output_file),
        "surface_temperature_k": get_surface_temperature(output_file),
        "surface_fluxes_molecules_cm2_s": {
            species: float(surface_fluxes[species])
            for species in tracked_species
            if species in surface_fluxes
        },
        "top_fluxes_molecules_cm2_s": {
            species: float(top_fluxes[species])
            for species in ("H", "H2")
            if species in top_fluxes
        },
    }
    with summary_file.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    return output_file, summary_file


def main():
    parser = argparse.ArgumentParser(
        description="Run a photochem case initialized from the VULCAN profile and evolved with climate."
    )
    parser.add_argument("run_id", help="Run identifier from Config/catalog.json")
    parser.add_argument("--force-prepare", action="store_true", help="Rebuild prepared photochem inputs before running.")
    parser.add_argument("--t-end", type=float, default=1.0e10, help="Final integration time in seconds for pc.evolve.")
    parser.add_argument("--n-times", type=int, default=40, help="Number of output checkpoints for pc.evolve.")
    args = parser.parse_args()

    output_file, summary_file = run_case(
        args.run_id,
        force_prepare=args.force_prepare,
        t_end=args.t_end,
        n_times=args.n_times,
    )
    print(output_file)
    print(summary_file)


if __name__ == "__main__":
    main()
