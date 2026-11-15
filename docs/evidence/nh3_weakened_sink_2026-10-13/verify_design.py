"""Verify the selected NH3 sink arithmetic and unchanged reference products.

This checks a conditional design, not an atmosphere or ocean simulation.
Run from any directory with Python's standard library.
"""

import hashlib
import json
import math
import platform
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent


def sha256_file(path: Path) -> str:
    """Hash files without loading the atmospheric products into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    design_path = EVIDENCE / "design_manifest.json"
    design = json.loads(design_path.read_text(encoding="utf-8"))
    reference_path = ROOT / design["integrity_reference_manifest"]
    reference = json.loads(reference_path.read_text(encoding="utf-8"))
    checks = []

    def check(name: str, condition: bool) -> None:
        if not condition:
            raise ValueError(f"Design verification failed: {name}")
        checks.append(name)

    check("NH3 only", design["species"] == "NH3")
    check("No new simulations", design["new_atmospheric_simulations"] == 0)
    check(
        "No canonical mutations",
        not design["canonical_bc_or_profiles_changed"],
    )
    ocean = design["ocean_area_fraction_assumed"]
    land = design["land_area_fraction_assumed"]
    control = design["reference_global_effective_velocity_cm_s"]
    marine = design["marine_control_anchor_cm_s"]
    weak = design["selected_global_effective_velocity_cm_s"]
    land_velocity = design["land_control_residual_cm_s_per_land_area"]
    marine_weak = design["marine_weakened_net_velocity_cm_s"]
    check("Area fractions sum to one", math.isclose(ocean + land, 1.0))
    check(
        "5 mm/s equals 0.50 cm/s",
        math.isclose(design["marine_anchor_original_mm_s"] / 10.0, marine),
    )
    check(
        "Baseline recovers 1 cm/s",
        math.isclose(ocean * marine + land * land_velocity, control),
    )
    check(
        "Ocean contribution is 0.35 cm/s", math.isclose(ocean * marine, 0.35)
    )
    check("Residual land capture is positive", land_velocity > 0.0)
    check(
        "Weak sink is 0.65 cm/s",
        math.isclose(ocean * marine_weak + land * land_velocity, weak),
    )
    check(
        "35 percent coefficient reduction at fixed density",
        math.isclose(
            1.0 - weak / control,
            design["fractional_coefficient_reduction_at_fixed_number_density"],
        ),
    )
    check(
        "Resistance converted from cm/s to m/s",
        math.isclose(
            1.0 / (weak / 100.0),
            design["equivalent_effective_resistance_s_m"],
        ),
    )
    # v [cm/s] times n [molecules/cm^3] gives J [molecules/cm^2/s].
    check("Hand-checkable surface flux", math.isclose(weak * 1.0e10, 6.5e9))

    phase = design["extra_phase_proposal"]
    cases = phase["candidate_cases"]
    check(
        "Four paired scenario proposals",
        [case["baseline_scenario"] for case in cases]
        == ["A0", "A1", "A2", "A3"],
    )
    check(
        "Unique candidate case identities",
        len({case["candidate_id"] for case in cases}) == 4,
    )
    check(
        "One additional sink value for the phase",
        phase["additional_velocity_cm_s"] == weak
        and phase["reference_velocity_cm_s"] == control,
    )
    check("Phase report exists", (ROOT / phase["report"]).is_file())
    box = design["linear_box_diagnostic"]
    check(
        "Deposition-only box ratio",
        math.isclose(control / weak, box["deposition_only_ratio"]),
    )
    # k*H has velocity units; here chemical loss equals reference deposition.
    check(
        "Equal-chemical-loss box ratio",
        math.isclose(
            (control + control) / (weak + control),
            box["equal_chemical_and_reference_deposition_ratio"],
        ),
    )
    check(
        "Box calculation is not a VULCAN prediction",
        not box["is_VULCAN_prediction_or_universal_bound"],
    )

    input_checks = []
    for case in reference["existing_earth_cases"]:
        for key in ("boundary", "saved_product"):
            original = case[key]
            current = ROOT / original["path"]
            actual_hash = sha256_file(current)
            check(
                f"SHA-256 unchanged: {original['path']}",
                actual_hash == original["sha256"],
            )
            input_checks.append(
                {"path": original["path"], "sha256": actual_hash}
            )
        boundary_path = ROOT / case["boundary"]["path"]
        boundary_lines = boundary_path.read_text(encoding="utf-8").splitlines()
        rows = [line.split() for line in boundary_lines]
        nh3_rows = [row for row in rows if row and row[0] == "NH3"]
        check(f"One canonical NH3 row: {case['scenario']}", len(nh3_rows) == 1)
        check(
            f"Canonical NH3 v_dep remains 1: {case['scenario']}",
            float(nh3_rows[0][2]) == 1.0,
        )

    result = {
        "analysis_date": design["analysis_date"],
        "design_id": design["design_id"],
        "status": "PASS_ANALYTIC_DESIGN_AND_INPUT_INTEGRITY_ONLY",
        "python_version": platform.python_version(),
        "design_sha256": sha256_file(design_path),
        "verification_script_sha256": sha256_file(Path(__file__).resolve()),
        "checks": checks,
        "reference_products_checked": input_checks,
        "new_atmospheric_simulations": 0,
        "physical_ocean_budget_validated": False,
    }
    output = EVIDENCE / "design_verification.json"
    output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"PASS: {len(checks)} analytical/integrity checks; "
        "no atmospheric simulations."
    )
    print(output.relative_to(ROOT))


if __name__ == "__main__":
    main()
