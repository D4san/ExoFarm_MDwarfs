"""Audit existing Earth NH3 boundaries and reproduce analytic diagnostics.

This script reads accepted VULCAN products; it does not run atmospheric models.
Run from the repository root with a Python environment containing NumPy, which
is needed to unpickle these locally generated scientific products.
"""

import hashlib
import json
import math
import pickle
import platform
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = Path(__file__).with_name("nh3_surface_sink_audit.json")
AVOGADRO = 6.02214076e23
EARTH_AREA_CM2 = 5.101e18
SECONDS_PER_YEAR = 365.25 * 86400.0
N_MOLAR_MASS_G = 14.0067
NH3_MOLAR_MASS_G = 17.03052
OCEAN_VOLUME_L = 1.335e21
ILLUSTRATIVE_INVENTORY_MOL = 6.0e18
ILLUSTRATIVE_PKA = 9.25

CASES = {
    "A0": ("bc_earth_preagri_full.txt", "Earth_A0_PreAgri.vul"),
    "A1": ("bc_earth_current_full.txt", "Earth_A1_Current.vul"),
    "A2": ("bc_earth_exofarm_moderate_full.txt", "Earth_A2_Moderate.vul"),
    "A3": ("bc_earth_exofarm_full.txt", "Earth_A3_Extreme.vul"),
}


def file_record(path):
    """Identify an input without changing its contents."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": digest.hexdigest(),
    }


def read_boundaries(path):
    """Return imposed emission and deposition velocity by species."""
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        species, flux, velocity, *_ = line.split()
        if species in rows:
            raise ValueError(f"Duplicate species {species} in {path}")
        rows[species] = (float(flux), float(velocity))
    return rows


def nitrogen_budget_to_nh3_flux(tg_n_year):
    """Convert nitrogen mass to NH3 molecules (one N atom per molecule)."""
    return (
        tg_n_year * 1e12 / N_MOLAR_MASS_G * AVOGADRO
        / (EARTH_AREA_CM2 * SECONDS_PER_YEAR)
    )


def main():
    cases = []
    for scenario, (bc_name, vul_name) in CASES.items():
        bc_path = (
            ROOT / "Photochemical_Modeling/Config/Boundary_Conditions"
            / bc_name
        )
        vul_path = ROOT / "Photochemical_Modeling/Results/Outputs" / vul_name
        boundaries = read_boundaries(bc_path)
        # Only load the repository's own accepted VULCAN products.
        with vul_path.open("rb") as handle:
            saved = pickle.load(handle)
        variable = saved["variable"]
        atmosphere = saved["atm"]
        nh3_index = variable["species"].index("NH3")
        n2o_index = variable["species"].index("N2O")
        emission = float(atmosphere["bot_flux"][nh3_index])
        velocity = float(atmosphere["bot_vdep"][nh3_index])
        surface_density = float(variable["y"][0, nh3_index])
        deposition = velocity * surface_density
        assert math.isclose(
            emission, boundaries["NH3"][0], rel_tol=1e-12
        )
        assert velocity == boundaries["NH3"][1] == 1.0
        assert saved["parameter"]["end_case"] == 1
        assert 0 < deposition / emission < 1
        cases.append({
            "scenario": scenario,
            "boundary": file_record(bc_path),
            "saved_product": file_record(vul_path),
            "termination_code": int(saved["parameter"]["end_case"]),
            "nh3_emission_molecules_cm2_s": emission,
            "nh3_deposition_velocity_cm_s": velocity,
            "nh3_surface_number_density_cm3": surface_density,
            "nh3_surface_vmr_ppb": float(variable["ymix"][0, nh3_index]) * 1e9,
            "nh3_surface_deposition_molecules_cm2_s": deposition,
            "nh3_deposition_to_imposed_emission_ratio": deposition / emission,
            "n2o_emission_saved_molecules_cm2_s": float(
                atmosphere["bot_flux"][n2o_index]
            ),
            "n2o_emission_active_molecules_cm2_s": boundaries["N2O"][0],
            "surface_temperature_K": float(atmosphere["Tco"][0]),
            "surface_pressure_bar": float(atmosphere["pco"][0]) / 1e6,
            "nh3_emission_Tg_N_year": (
                emission * EARTH_AREA_CM2 * SECONDS_PER_YEAR / AVOGADRO
                * N_MOLAR_MASS_G / 1e12
            ),
        })

    # Hand-checks: one mole of N is one mole of NH3; pH=pKa gives equal pools.
    one_mole_n_tg = N_MOLAR_MASS_G / 1e12
    assert math.isclose(
        nitrogen_budget_to_nh3_flux(one_mole_n_tg)
        * EARTH_AREA_CM2 * SECONDS_PER_YEAR,
        AVOGADRO, rel_tol=1e-12,
    )
    assert 1.0 / (1.0 + 10 ** (ILLUSTRATIVE_PKA - ILLUSTRATIVE_PKA)) == 0.5

    ocean_mol_l = ILLUSTRATIVE_INVENTORY_MOL / OCEAN_VOLUME_L
    agricultural_delta = nitrogen_budget_to_nh3_flux(58 * 0.65)
    report = {
        "analysis_date": "2026-10-13",
        "campaign_id": "nh3_surface_sinks_review_20261013",
        "status": "READ_ONLY_AUDIT_AND_ANALYTIC_DIAGNOSTICS",
        "python_version": platform.python_version(),
        "new_atmospheric_simulations": 0,
        "constants": {
            "avogadro_molecules_mol": AVOGADRO,
            "earth_area_cm2": EARTH_AREA_CM2,
            "seconds_year": SECONDS_PER_YEAR,
            "nitrogen_molar_mass_g_mol": N_MOLAR_MASS_G,
            "nh3_molar_mass_g_mol": NH3_MOLAR_MASS_G,
            "ocean_volume_L": OCEAN_VOLUME_L,
        },
        "earth_profiles_provenance": "earth_20260615_pre_n2o_correction",
        "existing_earth_cases": cases,
        "haqq_misra_2022_emission_budget_reconstruction": {
            "reference_total_Tg_N_year": 58.0,
            "natural_fraction": 0.19,
            "agricultural_fraction": 0.65,
            "A0_flux_molecules_cm2_s": nitrogen_budget_to_nh3_flux(58 * 0.19),
            "agricultural_delta_flux_molecules_cm2_s": agricultural_delta,
            "A1_flux_molecules_cm2_s": nitrogen_budget_to_nh3_flux(58 * 0.84),
            "interpretation": "Project choice: natural + agriculture (84%).",
        },
        "illustrative_ocean_inventory": {
            "total_NHx_inventory_mol": ILLUSTRATIVE_INVENTORY_MOL,
            "total_NHx_concentration_mM": ocean_mol_l * 1e3,
            "total_NHx_concentration_mg_N_L": (
                ocean_mol_l * N_MOLAR_MASS_G * 1e3
            ),
            "assumptions": [
                "Distribute inventory uniformly in a whole Earth-sized ocean.",
                "No atmospheric inventory correction or ocean transport.",
                "This is not a universal solubility or saturation threshold.",
            ],
            "un_ionized_fraction": [
                {"pH": ph, "fraction": 1 / (1 + 10 ** (ILLUSTRATIVE_PKA - ph))}
                for ph in (7.0, 8.1, 9.25, 10.0)
            ],
            "pKa_assumptions": (
                "9.25 illustrative dilute-water value; seawater needs "
                "temperature/salinity correction."
            ),
            "minimum_accumulation_time_years": [
                {
                    "scenario": case["scenario"],
                    "years": ILLUSTRATIVE_INVENTORY_MOL / (
                        case["nh3_emission_molecules_cm2_s"] * EARTH_AREA_CM2
                        * SECONDS_PER_YEAR / AVOGADRO
                    ),
                }
                for case in cases if case["scenario"] in ("A1", "A3")
            ],
            "time_assumptions": [
                "Build from zero using imposed atmospheric emissions.",
                "Every emitted molecule accumulates; no recycling or removal.",
                "Exclude river/subsurface inputs and oceanic production.",
                "Conditional lower bounds do not predict ocean history.",
            ],
        },
        "sources": {
            "huang": "https://doi.org/10.1089/ast.2020.2358",
            "tsai": "https://doi.org/10.3847/1538-4357/ac29bc",
            "haqq_misra": "https://arxiv.org/abs/2204.05360",
            "altieri": "https://doi.org/10.1029/2020GL091963",
            "santoro": "https://doi.org/10.1029/2020GB006716",
            "epa": "https://www.epa.gov/caddis/ammonia",
        },
        "source_pdf_records": [
            file_record(path) for path in (
                ROOT / "tmp/pdfs/nh3_surface_sinks_20261013"
            ).glob("*.pdf")
        ],
    }
    OUTPUT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUTPUT.relative_to(ROOT).as_posix()}")
    for case in cases:
        ratio = case["nh3_deposition_to_imposed_emission_ratio"]
        print(
            f"{case['scenario']}: vdep=1 cm/s; "
            f"surface={case['nh3_surface_vmr_ppb']:.4f} ppb; "
            f"deposition/emission={ratio:.4f}"
        )
    print("Unit, boundary and saved-product checks passed; zero simulations.")


if __name__ == "__main__":
    main()
