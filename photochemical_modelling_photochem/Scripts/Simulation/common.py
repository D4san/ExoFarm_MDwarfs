import json
import math
from pathlib import Path

import numpy as np
import yaml


MODULE_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = Path(__file__).resolve().parents[3]
CATALOG_PATH = MODULE_ROOT / "Config" / "catalog.json"
SETTINGS_TEMPLATE_PATH = MODULE_ROOT / "Config" / "Templates" / "settings_base.yaml"

K_BOLTZMANN_CGS = 1.380649e-16
AMU_TO_GRAMS = 1.66053906660e-24
AU_TO_CM = 1.495978707e13
R_SUN_TO_CM = 6.957e10

SPECIES_ALIASES = {
    "COS": "OCS",
    "H2SO4_l": None,
}


def load_catalog():
    with CATALOG_PATH.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def project_path(relative_path):
    return PROJECT_ROOT / relative_path


def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)
    return path


def prepared_root():
    return ensure_dir(MODULE_ROOT / "Results" / "Prepared")


def outputs_root():
    return ensure_dir(MODULE_ROOT / "Results" / "Outputs")


def summaries_root():
    return ensure_dir(MODULE_ROOT / "Results" / "Summaries")


def logs_root():
    return ensure_dir(MODULE_ROOT / "Results" / "Logs")


def mechanism_root():
    return ensure_dir(prepared_root() / "mechanism")


def stellar_flux_root():
    return ensure_dir(prepared_root() / "stellar_flux")


def settings_root():
    return ensure_dir(prepared_root() / "settings")


def climate_root():
    return ensure_dir(prepared_root() / "climate")


def initial_atmosphere_root():
    return ensure_dir(prepared_root() / "initial_atmospheres")


def load_yaml(path):
    with Path(path).open("r", encoding="utf-8-sig") as handle:
        return yaml.safe_load(handle)


def dump_yaml(data, path):
    with Path(path).open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False)


def list_runs(star_key=None):
    catalog = load_catalog()
    runs = catalog["runs"]
    if star_key is None:
        return runs
    return [run for run in runs if run["star"] == star_key]


def get_run(run_id):
    for run in list_runs():
        if run["id"] == run_id:
            return run
    raise KeyError(f"Unknown run id: {run_id}")


def get_star(star_key):
    return load_catalog()["stars"][star_key]


def get_scenario(scenario_key):
    return load_catalog()["scenarios"][scenario_key]


def get_planet(planet_key):
    planets = load_catalog().get("planets", {})
    if planet_key not in planets:
        raise KeyError(f"Unknown planet key: {planet_key}")
    return planets[planet_key]


def get_planet_for_run(run_id):
    catalog = load_catalog()
    run = get_run(run_id)
    planet_key = run.get("planet", catalog["model"].get("default_planet", "earth"))
    return get_planet(planet_key)


def load_settings_template():
    return load_yaml(SETTINGS_TEMPLATE_PATH)


def mechanism_output_path():
    catalog = load_catalog()
    network_name = Path(catalog["model"]["vulcan_network_file"]).name.replace(".txt", ".yaml")
    return mechanism_root() / network_name


def mechanism_data_dir():
    return mechanism_root() / "vulcandata"


def stellar_flux_path(star_config):
    return stellar_flux_root() / star_config["output_file"]


def settings_output_path(run_id):
    return settings_root() / f"{run_id}_settings.yaml"


def climate_settings_output_path(run_id):
    return climate_root() / f"{run_id}_climate_settings.yaml"


def climate_species_output_path(run_id):
    return climate_root() / f"{run_id}_climate_species.yaml"


def initial_atmosphere_path(run_id):
    return initial_atmosphere_root() / f"{run_id}_initial_atmosphere.txt"


def atmosphere_output_path(run_id):
    return outputs_root() / f"{run_id}_steady_state.txt"


def summary_output_path(run_id):
    return summaries_root() / f"{run_id}_summary.json"


def log_output_path(run_id):
    return logs_root() / f"{run_id}.log"


def read_mechanism_species(mechanism_file):
    mechanism = load_yaml(mechanism_file)
    gas_species = [entry["name"] for entry in mechanism.get("species", [])]
    particle_species = [entry["name"] for entry in mechanism.get("particles", [])]
    return gas_species, particle_species


def parse_boundary_conditions_file(path, allowed_species=None):
    parsed = {}

    with Path(path).open("r", encoding="utf-8-sig") as handle:
        for raw_line in handle:
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            parts = stripped.split()
            if len(parts) < 3:
                continue

            original_name = parts[0]
            if original_name.lower() == "species":
                continue

            mapped_name = SPECIES_ALIASES.get(original_name, original_name)
            if mapped_name is None:
                continue

            try:
                flux = float(parts[1].replace("D", "E"))
                vdep = float(parts[2].replace("D", "E"))
            except ValueError:
                continue

            if allowed_species is not None and mapped_name not in allowed_species:
                continue

            if flux > 0.0 and vdep > 0.0:
                entry = {
                    "name": mapped_name,
                    "lower-boundary": {
                        "type": "vdep + dist flux",
                        "vdep": vdep,
                        "flux": flux,
                        "height": -1.0,
                    },
                    "upper-boundary": {"type": "veff", "veff": 0.0},
                }
            elif flux > 0.0:
                entry = {
                    "name": mapped_name,
                    "lower-boundary": {"type": "flux", "flux": flux},
                    "upper-boundary": {"type": "veff", "veff": 0.0},
                }
            elif vdep > 0.0:
                entry = {
                    "name": mapped_name,
                    "lower-boundary": {"type": "vdep", "vdep": vdep},
                    "upper-boundary": {"type": "veff", "veff": 0.0},
                }
            else:
                continue

            score = flux
            existing = parsed.get(mapped_name)
            if existing is None or score > existing["_score"]:
                entry["_score"] = score
                parsed[mapped_name] = entry

    for entry in parsed.values():
        entry.pop("_score", None)

    return list(parsed.values())


def merge_boundary_conditions(base_entries, overlay_entries, allowed_species):
    merged = {}

    for entry in base_entries:
        if entry["name"] in allowed_species:
            merged[entry["name"]] = entry

    for entry in overlay_entries:
        if entry["name"] in allowed_species:
            merged[entry["name"]] = entry

    return [merged[name] for name in sorted(merged)]


def read_pressure_temperature_kzz(profile_path):
    pressures = []
    temperatures = []
    eddy = []

    with Path(profile_path).open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.lower().startswith("pressure"):
                continue

            parts = stripped.split()
            if len(parts) < 3:
                continue

            pressures.append(float(parts[0]))
            temperatures.append(float(parts[1]))
            eddy.append(float(parts[2]))

    return (
        np.asarray(pressures, dtype=float),
        np.asarray(temperatures, dtype=float),
        np.asarray(eddy, dtype=float),
    )


def read_seed_chemistry(template_path, floor):
    path = Path(template_path)
    if not path.exists():
        return None

    with path.open("r", encoding="utf-8") as handle:
        header = handle.readline().strip().split()
        rows = [
            [float(value) for value in line.strip().split()]
            for line in handle
            if line.strip()
        ]

    if not rows:
        return None

    data = np.asarray(rows, dtype=float)
    result = {"pressure_bar": data[:, 0]}
    for column_index, species in enumerate(header[1:], start=1):
        result[species] = np.maximum(data[:, column_index], floor)
    return result


def interpolate_seed_profile(seed_pressures_bar, seed_values, target_pressures_bar, floor):
    safe_seed_values = np.maximum(np.asarray(seed_values, dtype=float), floor)
    safe_target_pressures = np.maximum(np.asarray(target_pressures_bar, dtype=float), floor)

    log_seed_pressure = np.log10(np.asarray(seed_pressures_bar, dtype=float)[::-1])
    log_seed_values = np.log10(safe_seed_values[::-1])
    log_target_pressure = np.log10(safe_target_pressures[::-1])

    interpolated = np.interp(log_target_pressure, log_seed_pressure, log_seed_values)
    return np.power(10.0, interpolated[::-1])


def compute_altitude_km(pressure_cgs, temperature_k, mean_molecular_weight_amu, gravity_cms2):
    altitude_cm = np.zeros_like(pressure_cgs, dtype=float)
    particle_mass_g = mean_molecular_weight_amu * AMU_TO_GRAMS

    for index in range(1, pressure_cgs.size):
        temperature_layer = 0.5 * (temperature_k[index - 1] + temperature_k[index])
        scale_height_cm = K_BOLTZMANN_CGS * temperature_layer / (particle_mass_g * gravity_cms2)
        delta_z_cm = scale_height_cm * math.log(pressure_cgs[index - 1] / pressure_cgs[index])
        altitude_cm[index] = altitude_cm[index - 1] + delta_z_cm

    return altitude_cm / 1.0e5


def load_stellar_surface_spectrum(path):
    data = np.loadtxt(path, comments="#")
    if data.ndim == 1:
        data = data[None, :]
    if data.shape[1] < 2:
        raise ValueError(f"Stellar spectrum file must have at least two columns: {path}")
    wavelength_nm = data[:, 0].astype(float)
    surface_flux = data[:, 1].astype(float)
    return wavelength_nm, surface_flux


def scale_surface_flux_to_planet(surface_flux, stellar_radius_solar, orbital_distance_au):
    stellar_radius_cm = stellar_radius_solar * R_SUN_TO_CM
    orbital_distance_cm = orbital_distance_au * AU_TO_CM
    scale = (stellar_radius_cm / orbital_distance_cm) ** 2
    return surface_flux * scale


def save_photochem_stellar_flux(output_path, wavelength_nm, flux_planet_mw_m2_nm):
    output_path = Path(output_path)
    with output_path.open("w", encoding="utf-8") as handle:
        handle.write(f"{'Wavelength(nm)':>20}{'SolarFlux(mW/m^2/nm)':>20}\n")
        for wv, flux in zip(wavelength_nm, flux_planet_mw_m2_nm):
            handle.write(f"{wv:20.8e}{flux:20.8e}\n")
    return output_path


def planet_config_value(planet, catalog_key):
    catalog = load_catalog()
    return planet.get(catalog_key, catalog["model"][catalog_key])


def build_settings_for_run(run_id, mechanism_species):
    catalog = load_catalog()
    run = get_run(run_id)
    star = get_star(run["star"])
    scenario = get_scenario(run["scenario"])
    planet = get_planet_for_run(run_id)

    base_settings = load_settings_template()
    base_settings["atmosphere-grid"]["number-of-layers"] = catalog["model"]["number_of_layers"]
    base_settings["planet"]["planet-mass"] = planet_config_value(planet, "planet_mass_g")
    base_settings["planet"]["planet-radius"] = planet_config_value(planet, "planet_radius_cm")
    base_settings["planet"]["surface-albedo"] = planet_config_value(planet, "surface_albedo")
    base_settings["planet"]["solar-zenith-angle"] = star["solar_zenith_angle_deg"]

    scenario_boundaries = parse_boundary_conditions_file(
        project_path(scenario["boundary_condition_file"]),
        allowed_species=set(mechanism_species),
    )

    base_entries = base_settings.get("boundary-conditions", [])
    base_settings["boundary-conditions"] = merge_boundary_conditions(
        base_entries,
        scenario_boundaries,
        allowed_species=set(mechanism_species),
    )

    output_path = settings_output_path(run_id)
    dump_yaml(base_settings, output_path)
    return output_path


def build_climate_initial_atmosphere_for_run(run_id):
    run = get_run(run_id)
    planet = get_planet_for_run(run_id)
    star = get_star(run["star"])
    scenario = get_scenario(run["scenario"])
    climate = planet.get("climate", {})

    if not climate.get("enabled", False):
        raise ValueError(f"Climate is not enabled for run {run_id}")

    try:
        from photochem.clima import AdiabatClimate
    except ImportError as exc:
        raise RuntimeError(
            "photochem with climate support is not installed. Install photochem before preparing climate-coupled inputs."
        ) from exc

    species_template_path = project_path(climate["species_template"])
    settings_template_path = project_path(climate["settings_template"])
    species_output = climate_species_output_path(run_id)
    settings_output = climate_settings_output_path(run_id)

    species_output.write_text(species_template_path.read_text(encoding="utf-8"), encoding="utf-8")

    settings = load_yaml(settings_template_path)
    settings["atmosphere-grid"]["number-of-layers"] = int(
        climate.get("number_of_layers", settings["atmosphere-grid"]["number-of-layers"])
    )
    settings["planet"]["planet-mass"] = planet_config_value(planet, "planet_mass_g")
    settings["planet"]["planet-radius"] = planet_config_value(planet, "planet_radius_cm")
    settings["planet"]["surface-albedo"] = planet_config_value(planet, "surface_albedo")
    dump_yaml(settings, settings_output)

    c = AdiabatClimate(
        str(species_output),
        str(settings_output),
        str(stellar_flux_path(star)),
    )

    floor_bar = float(climate.get("trace_pressure_floor_bar", 1.0e-10))
    P_i = np.ones(len(c.species_names), dtype=float) * floor_bar
    surface_pressures = dict(climate.get("surface_pressures_bar", {}))
    surface_pressures.update(scenario.get("climate_surface_pressures_bar", {}))
    for species, pressure_bar in surface_pressures.items():
        if species in c.species_names:
            P_i[c.species_names.index(species)] = float(pressure_bar)
    P_i *= 1.0e6

    relative_humidity = float(climate.get("relative_humidity", 0.5))
    c.RH = np.ones(len(c.species_names), dtype=float) * relative_humidity
    c.P_top = float(climate.get("top_pressure_bar", 1.0e-5)) * 1.0e6
    c.max_rc_iters = int(climate.get("max_rc_iters", 30))
    c.convective_newton_step_size = float(climate.get("convective_newton_step_size", 0.05))

    if bool(climate.get("solve_for_t_trop", True)):
        c.solve_for_T_trop = True
        c.T_trop = c.rad.skin_temperature(float(climate.get("skin_temperature_albedo", 0.3)))
    elif "t_trop_k" in climate:
        c.T_trop = float(climate["t_trop_k"])

    T_guess = float(climate.get("surface_temperature_guess_k", 280.0))
    c.surface_temperature(P_i, T_guess=T_guess)
    converged = c.RCE(P_i, c.T_surf, c.T, c.convecting_with_below)
    if not converged:
        raise RuntimeError(f"AdiabatClimate did not converge for {run_id}")

    eddy_profile = climate.get("eddy_profile", "constant")
    if eddy_profile != "constant":
        raise ValueError(f"Unsupported climate eddy profile strategy: {eddy_profile}")

    eddy_value = float(climate.get("eddy_constant_cm2_s", 1.0e5))
    eddy = np.ones(c.z.shape[0], dtype=float) * eddy_value

    output_path = initial_atmosphere_path(run_id)
    c.out2atmosphere_txt(str(output_path), eddy=eddy, overwrite=True)
    return output_path


def build_initial_atmosphere_for_run(run_id, mechanism_species, particle_species):
    planet = get_planet_for_run(run_id)
    climate = planet.get("climate", {})
    if climate.get("enabled", False):
        return build_climate_initial_atmosphere_for_run(run_id)

    catalog = load_catalog()
    floor = catalog["model"]["seed_floor_mixing_ratio"]
    fallback = catalog["model"]["fallback_initial_mixing_ratios"]
    pressure_cgs, temperature_k, eddy = read_pressure_temperature_kzz(
        project_path(planet_config_value(planet, "pressure_temperature_kzz_file"))
    )
    pressure_bar = pressure_cgs / 1.0e6

    seed = read_seed_chemistry(project_path(planet_config_value(planet, "seed_chemistry_template")), floor)
    seed_pressures_bar = np.asarray(seed["pressure_bar"], dtype=float) if seed is not None else None

    altitude_km = compute_altitude_km(
        pressure_cgs=pressure_cgs,
        temperature_k=temperature_k,
        mean_molecular_weight_amu=planet_config_value(planet, "reference_mean_molecular_weight_amu"),
        gravity_cms2=planet_config_value(planet, "gravity_cms2"),
    )
    density = pressure_cgs / (K_BOLTZMANN_CGS * temperature_k)

    matrix_columns = []
    header = ["alt", "press", "den", "temp", "eddy"]

    for species in mechanism_species:
        if seed is not None and species in seed:
            values = interpolate_seed_profile(seed_pressures_bar, seed[species], pressure_bar, floor)
        else:
            values = np.full_like(pressure_bar, fallback.get(species, floor), dtype=float)

        values = np.maximum(values, floor)
        matrix_columns.append(values)
        header.append(species)

    particle_radius_cm = catalog["model"]["particle_radius_cm"]
    for particle in particle_species:
        matrix_columns.append(np.full_like(pressure_bar, floor, dtype=float))
        header.append(particle)

    for particle in particle_species:
        matrix_columns.append(np.full_like(pressure_bar, particle_radius_cm, dtype=float))
        header.append(f"{particle}_r")

    data_columns = [altitude_km, pressure_cgs, density, temperature_k, eddy] + matrix_columns
    data = np.column_stack(data_columns)

    output_path = initial_atmosphere_path(run_id)
    with output_path.open("w", encoding="utf-8") as handle:
        handle.write(" ".join(header) + "\n")
        np.savetxt(handle, data, fmt="%.8e")

    return output_path


def read_atmosphere_output(path):
    with Path(path).open("r", encoding="utf-8-sig") as handle:
        header = handle.readline().strip().split()
        rows = [
            [float(value) for value in line.strip().split()]
            for line in handle
            if line.strip()
        ]

    data = np.asarray(rows, dtype=float)
    columns = {name: data[:, index] for index, name in enumerate(header)}
    return header, columns


def get_surface_mixing_ratio(path, species):
    if not Path(path).exists():
        return None

    header, columns = read_atmosphere_output(path)
    if species not in header:
        return None

    pressure = columns["press"]
    surface_index = int(np.argmax(pressure))
    return float(columns[species][surface_index])


def species_columns_from_atmosphere_header(header):
    skip = {"alt", "press", "den", "temp", "eddy"}
    return [name for name in header if name not in skip and not name.endswith("_r")]

