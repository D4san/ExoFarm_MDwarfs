import argparse
import json
from pathlib import Path


def require_photochem():
    try:
        from photochem import EvoAtmosphere, zahnle_earth  # noqa: F401
    except ImportError as exc:
        raise RuntimeError(
            "photochem is not installed. Install photochem before running the official ModernEarth example."
        ) from exc


def repo_root():
    return Path(__file__).resolve().parents[3]


def official_example_root():
    return repo_root() / ".codex_tmp" / "photochem_repo" / "examples" / "ModernEarth"


def output_root():
    path = repo_root() / "photochemical_modelling_photochem" / "Results" / "Official_ModernEarth"
    path.mkdir(parents=True, exist_ok=True)
    return path


def official_output_path():
    return output_root() / "ModernEarth_official_steady_state.txt"


def official_summary_path():
    return output_root() / "ModernEarth_official_summary.json"


def get_surface_mixing_ratios(output_path, tracked_species):
    import numpy as np

    with Path(output_path).open("r", encoding="utf-8") as handle:
        header = handle.readline().strip().split()
        data = np.loadtxt(handle)

    if data.ndim == 1:
        data = data[None, :]

    columns = {name: data[:, index] for index, name in enumerate(header)}
    pressure = columns["press"]
    surface_index = int(np.argmax(pressure))

    result = {}
    for species in tracked_species:
        if species in columns:
            result[species] = float(columns[species][surface_index])
    return result


def run_modern_earth_example(overwrite=False):
    require_photochem()
    from photochem import EvoAtmosphere, zahnle_earth

    example_root = official_example_root()
    settings_file = example_root / "settings.yaml"
    flux_file = example_root / "Sun_now.txt"
    atmosphere_file = example_root / "atmosphere.txt"
    output_file = official_output_path()

    if output_file.exists() and not overwrite:
        return output_file

    pc = EvoAtmosphere(
        zahnle_earth,
        str(settings_file),
        str(flux_file),
        str(atmosphere_file),
    )
    pc.var.verbose = 0
    converged = pc.find_steady_state()
    pc.out2atmosphere_txt(str(output_file), overwrite=True)

    summary = {
        "example": "photochem ModernEarth official",
        "converged": bool(converged),
        "reaction_mechanism": str(zahnle_earth),
        "settings_file": str(settings_file),
        "stellar_flux_file": str(flux_file),
        "initial_atmosphere_file": str(atmosphere_file),
        "output_atmosphere_file": str(output_file),
        "surface_mixing_ratios": get_surface_mixing_ratios(
            output_file,
            tracked_species=["CH4", "O3", "N2O", "NH3", "H2O", "CO2", "O2", "N2"],
        ),
    }
    official_summary_path().write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return output_file


def main():
    parser = argparse.ArgumentParser(description="Run photochem's official ModernEarth example.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Recompute even if the steady-state output already exists.",
    )
    args = parser.parse_args()

    output_path = run_modern_earth_example(overwrite=args.overwrite)
    print(output_path)


if __name__ == "__main__":
    main()
