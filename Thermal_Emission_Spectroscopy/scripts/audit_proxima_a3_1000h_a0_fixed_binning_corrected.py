"""Independently validate the three corrected-binning A3-1000 h A0 runs.

This audit reads only completed retrieval products. It does not launch or
resume POSEIDON. Fixed-coordinate NaN standard deviations are reported as a
separate review issue; primary samples and evidence must still be finite.
"""

from __future__ import annotations

import csv
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

import audit_proxima_a0_fixed_reference as common
from fixed_abundance_reference import load_fixed_abundances
from report_proxima_loo_lin_sigma import METHOD, calibrated_sigma, check_calibration
from run_proxima_a0_reference_campaign import verify_matched_configuration
from validate_proxima_molecular_ablation_loo import numeric_rows, parse_table_header, sha256


CAMPAIGN_REL = Path(
    "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/"
    "retrievals/a0_fixed_reference_A3_1000h_binning_corrected_20261016_relaunch_01"
)
FULL_REL = Path(
    "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/"
    "retrievals/a3_1000h_binning_corrected_20261014"
)
DATASET_REL = Path(
    "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/"
    "LIFE_proxima_A3_1000h_O2_fixedBlack1bar_official.dat"
)
TABLE_REL = Path("Thermal_Emission_Spectroscopy/final_products/tables")
DATASET_SHA256 = "5611c5904ef03aa02586bed15f14c0c2560ac5ae6fa9463ef420229311db75fa"
EXPECTED = (
    ("A3_1000h_A0_N2O_BIN1", "N2O"),
    ("A3_1000h_A0_NH3_BIN1", "NH3"),
    ("A3_1000h_A0_joint_BIN1", "joint"),
)
OPERATOR_SCRIPT_REL = Path("Thermal_Emission_Spectroscopy/scripts/life_bin_operator_diagnostic.py")
SUPERVISOR_LOG = Path(
    "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/"
    "a0_fixed_reference_A3_1000h_binning_corrected_20261016_relaunch_01.supervisor.log"
)
TABLE_STEM = "life_proxima_a3_1000h_a0_fixed_binning_corrected_2026-10-17"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def relative_hashes(products: dict[str, str], root: Path) -> dict[str, str]:
    result = {}
    for path_text, digest in products.items():
        path = Path(path_text).resolve()
        result[path.relative_to(root.resolve()).as_posix()] = digest
    return result


def quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def posterior_enrichment(full_result: Path, fixed_values: dict[str, float]) -> dict:
    samples = full_result.parent.parent / "samples" / (
        full_result.name.removesuffix("_results.txt") + "_samples.txt"
    )
    headers = parse_table_header(samples)
    rows = list(numeric_rows(samples, skip_lines=1))
    if not rows or len(headers) != 15 or any(len(row) != 15 for row in rows):
        raise ValueError("Corrected full posterior has an unexpected shape")
    delta = {
        species: [row[headers.index("log_" + species)] - fixed_values[species] for row in rows]
        for species in ("N2O", "NH3")
    }
    result = {"rows": len(rows), "source": str(samples)}
    for species, values in delta.items():
        lo, median, hi = (quantile(values, q) for q in (0.025, 0.5, 0.975))
        result[species] = {
            "delta_log10_median_q025_q975_dex": [lo, median, hi],
            "enrichment_factor_median_q025_q975": [10.0**lo, 10.0**median, 10.0**hi],
            "posterior_probability_above_A0": sum(value > 0 for value in values) / len(values),
            "posterior_count_above_A0": sum(value > 0 for value in values),
            "posterior_count_at_or_below_A0": sum(value <= 0 for value in values),
            "nominal_log_uniform_prior_probability_above_A0": (-1.0 - fixed_values[species]) / 11.0,
        }
    both = [a > 0 and b > 0 for a, b in zip(delta["N2O"], delta["NH3"])]
    either = [a > 0 or b > 0 for a, b in zip(delta["N2O"], delta["NH3"])]
    result["joint_events_same_posterior_rows"] = {
        "both_above_A0_probability": sum(both) / len(both),
        "at_least_one_above_A0_probability": sum(either) / len(either),
        "rows_used": len(rows),
        "method": "equal-weight complete-posterior rows; preserve molecular dependence",
    }
    return result


def check_operator(record: dict, variant: str, dataset_sha: str, operator_sha: str) -> None:
    if record.get("status") != "PASS" or not record.get("actual_forward_model_callback_bound"):
        raise ValueError(f"Operator callback preflight failed: {variant}")
    if not record.get("native_grid_identical") or record.get("dataset_sha256") != dataset_sha:
        raise ValueError(f"Operator grid/dataset mismatch: {variant}")
    if record.get("operator_sha256") != operator_sha:
        raise ValueError(f"Operator source hash mismatch: {variant}")
    if record.get("binding_scope") != "sampling and posterior postprocessing":
        raise ValueError(f"Operator binding scope mismatch: {variant}")
    if record.get("temperature_opacity_grid_K") != [180, 310, 10]:
        raise ValueError(f"Thermal opacity grid mismatch: {variant}")


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    campaign = root / CAMPAIGN_REL
    full_root = root / FULL_REL
    state_path = campaign / "campaign_state.json"
    state = read_json(state_path)
    selection = read_json(campaign / "selected_scope.json")
    manifest_path = campaign / "manifest.csv"
    with manifest_path.open(encoding="utf-8", newline="") as stream:
        manifest = list(csv.DictReader(stream))
    expected_ids = [run_id for run_id, _ in EXPECTED]
    cases = state.get("cases", [])
    if [case.get("run_id") for case in cases] != expected_ids:
        raise ValueError("Campaign run scope/order differs from the three authorized variants")
    if [row.get("run_id") for row in manifest] != expected_ids:
        raise ValueError("Manifest run scope/order mismatch")
    if (selection.get("scenario") != "A3" or selection.get("hours") != 1000
            or selection.get("new_variants") != ["N2O", "NH3", "joint"]
            or selection.get("new_retrievals") != 3 or selection.get("checkpoint_reuse") is not False
            or selection.get("dataset_sha256") != DATASET_SHA256):
        raise ValueError("Selected scope differs from the authorized relaunch")
    if state.get("status") != "COMPLETE_PENDING_VALIDATION":
        raise ValueError(f"Unexpected pre-audit campaign status: {state.get('status')}")
    if state.get("acceptance") != "PENDING_INDEPENDENT_REVIEW":
        raise ValueError("Campaign acceptance state changed before independent audit")
    if not (state.get("source_equivalence", {}).get("status") == "PASS"
            and state["source_equivalence"].get("scientific_operator_change") is False
            and state["source_equivalence"].get("executable_AST_equal_except_docstrings_and_two_error_messages")):
        raise ValueError("Reconstructed full-run operator equivalence was not established")
    preflight = read_json(campaign / "preflight_validation.json")
    if (not preflight.get("all_pass") or not preflight.get("same_operator_as_corrected_full")
            or not preflight.get("same_configuration_except_selected_fixed_abundances")
            or preflight.get("free_dimensions") != [13, 13, 12]):
        raise ValueError("Three-variant preflight validation did not pass")

    dataset = root / DATASET_REL
    if sha256(dataset) != DATASET_SHA256:
        raise ValueError("Observed A3-1000 h dataset SHA-256 mismatch")
    common.validate_table(dataset, skip_lines=1, expected_columns=4, min_rows=31, max_rows=31)

    reference_path = campaign / "a0_reference.json"
    reference = read_json(reference_path)
    fixed_reference = load_fixed_abundances(reference_path, ["N2O", "NH3"], root)
    operator_path = root / OPERATOR_SCRIPT_REL
    operator_sha = sha256(operator_path)
    full_operator = read_json(full_root / "operator_preflight.json")
    if (full_operator.get("status") != "PASS"
            or not full_operator.get("actual_forward_model_callback_bound")
            or full_operator.get("dataset_sha256") != DATASET_SHA256):
        raise ValueError("Official corrected full-run operator preflight is not valid")
    full_config_path = full_root / "resolved_configuration.json"
    full_config = read_json(full_config_path)
    if full_config.get("dataset_sha256") != DATASET_SHA256:
        raise ValueError("Corrected full configuration uses a different dataset")
    full_result = full_root / "products/results" / f"{full_config['model_name']}_results.txt"
    full_audit = common.audit_products(full_result, full_config, dataset, {})
    comparison = read_json(full_root / "comparison/comparison.json").get("corrected_operator", {})
    for key, observed in (("lnZ", full_audit["lnz"]),
                          ("lnZ_numeric_error", full_audit["lnz_error"]),
                          ("chi2_printed", full_audit["chi2_printed"])):
        if key not in comparison or abs(float(comparison[key]) - observed) > 1e-9:
            raise ValueError(f"Corrected full-run comparison metadata mismatch: {key}")
    if comparison.get("posterior_rows") != full_audit["posterior_samples"]:
        raise ValueError("Corrected full posterior row count differs from comparison.json")

    fixed_values = {species: fixed_reference[species] for species in ("N2O", "NH3")}
    audits: dict[str, dict] = {}
    rows: list[dict] = []
    stable_moments: list[dict] = []
    operator_records = {}
    for (run_id, variant), case, manifest_row, expected_free in zip(
            EXPECTED, cases, manifest, (13, 13, 12)):
        if (case.get("status") != "complete_pending_validation" or case.get("return_code") != 0
                or case.get("acceptance") != "PENDING"):
            raise ValueError(f"Run ledger is not cleanly completed: {run_id}")
        for field in ("status", "return_code", "dataset_sha256", "archive_dir"):
            if manifest_row.get(field) != str(case.get(field)):
                raise ValueError(f"Manifest/state mismatch: {run_id}/{field}")
        if (case.get("variant") != variant or case.get("scenario") != "A3"
                or case.get("hours") != 1000 or case.get("mpi_ranks") != 5
                or case.get("declared_dimension") != 15
                or case.get("effective_free_dimension") != expected_free
                or case.get("dataset_sha256") != DATASET_SHA256):
            raise ValueError(f"Run scope/configuration mismatch: {run_id}")
        config_path = campaign / "resolved" / f"{variant}.json"
        config = read_json(config_path)
        if sha256(config_path) != case.get("resolved_sha256"):
            raise ValueError(f"Resolved configuration SHA-256 mismatch: {run_id}")
        verify_matched_configuration(full_config, config, case)
        if config.get("n_live") != 800 or config.get("ev_tol") != 0.5:
            raise ValueError(f"Nested-sampling configuration mismatch: {run_id}")
        fixed = case.get("fixed_log10_vmr", {})
        if fixed != {species: fixed_values[species] for species in case.get("fixed_species", [])}:
            raise ValueError(f"Fixed A0 abundance differs from reference: {run_id}")
        operator_record = read_json(campaign / "preflight" / f"{variant}_operator.json")
        check_operator(operator_record, variant, DATASET_SHA256, operator_sha)
        operator_records[run_id] = operator_record

        command = case.get("command", [])
        if not command or command.count("-n") != 1 or command[command.index("-n") + 1] != "5":
            raise ValueError(f"MPI5 command contract mismatch: {run_id}")
        if "--dataset-file" not in command or command[command.index("--dataset-file") + 1] != DATASET_REL.as_posix():
            raise ValueError(f"Run command dataset path mismatch: {run_id}")
        if "--n-live" not in command or command[command.index("--n-live") + 1] != "800":
            raise ValueError(f"Run command N_live mismatch: {run_id}")

        launch_log = str(case["launch_log"])
        wsl_root = "/mnt/c/Proyectos/Astro/ExoFarm_MDwarfs/"
        if launch_log.startswith(wsl_root):
            log_path = root / Path(launch_log.removeprefix(wsl_root))
        else:
            log_path = Path(launch_log)
            if not log_path.is_absolute():
                log_path = root / log_path
        log = log_path.read_text(encoding="utf-8", errors="replace")
        model = config["model_name"]
        done_markers = log.count(f"[done] {model}")
        ranks = {int(value) for value in re.findall(r"\[operator-postprocessing-complete\]\s*rank=(\d+)", log)}
        if ("Sampling finished. Exiting MultiNest" not in log or "All done!" not in log
                or done_markers != 5 or ranks != set(range(5))):
            raise ValueError(f"MPI5 completion/postprocessing markers incomplete: {run_id}")
        if re.search(r"Traceback|MPI_ABORT|Out of memory|Killed|\[failed\]", log):
            raise ValueError(f"Fatal marker in completed run log: {run_id}")

        archive = common.mapped_path(case["archive_dir"], root)
        result_path = archive / "POSEIDON_output/proxima_b_earthlike/retrievals/results" / f"{model}_results.txt"
        audit = common.audit_products(result_path, config, dataset, fixed)
        audit.update(
            config_sha256=sha256(config_path),
            operator_sha256=operator_sha,
            operator_record_sha256=sha256(campaign / "preflight" / f"{variant}_operator.json"),
            log_sha256=sha256(log_path),
            declared_dimension=15,
            effective_free_dimension=expected_free,
            fixed_log10_vmr=fixed,
            return_code=0,
        )
        audit["product_sha256"] = relative_hashes(audit["product_sha256"], root)
        audits[run_id] = audit
        stable_moments.extend(common.stable_fixed_moments(run_id, result_path, config))
        ln_b = full_audit["lnz"] - audit["lnz"]
        numerical_error = math.hypot(full_audit["lnz_error"], audit["lnz_error"])
        sigma, log_p = calibrated_sigma(ln_b)
        rows.append({
            "run_id": run_id,
            "variant": variant,
            "scenario": "A3",
            "hours": 1000,
            "fixed_species": "+".join(case["fixed_species"]),
            "lnz_full_corrected": full_audit["lnz"],
            "lnz_full_numeric_error": full_audit["lnz_error"],
            "lnz_a0_fixed": audit["lnz"],
            "lnz_a0_fixed_numeric_error": audit["lnz_error"],
            "ln_B_full_minus_A0": ln_b,
            "ln_B_numeric_error_quadrature": numerical_error,
            "sigma_calibrated_bilateral": sigma,
            "sigma_status": "calibrated" if sigma is not None else "N/A_lnB_not_positive",
            "log_p_calibration": log_p,
            "sigma_method": METHOD,
            "dataset_sha256": DATASET_SHA256,
            "posterior_samples": audit["posterior_samples"],
            "declared_dimension": 15,
            "effective_free_dimension": expected_free,
            "fixed_log10_vmr": json.dumps(fixed, sort_keys=True),
            "result_sha256": audit["product_sha256"][str((result_path.resolve().relative_to(root.resolve())).as_posix())],
            "stats_sha256": audit["product_sha256"][str((result_path.parent.parent / "MultiNest_raw" / f"{model}-stats.dat").resolve().relative_to(root.resolve()).as_posix())],
            "fixed_moment_issue_count": len(audit["derived_moment_audit"]["issues"]),
        })

    fixed_moment_issues = [
        {"run_id": run_id, **issue}
        for run_id, audit in audits.items()
        for issue in audit["derived_moment_audit"]["issues"]
    ]
    allowed_issues = all(
        issue["quantity"] == "derived_standard_deviation"
        and issue["token"] == "NaN"
        and issue["parameter"].removeprefix("log_") in audits[issue["run_id"]]["fixed_coordinate_spreads"]
        for issue in fixed_moment_issues
    )
    if fixed_moment_issues and not allowed_issues:
        raise ValueError("Non-finite output is not limited to exactly fixed-coordinate standard deviations")

    enrichment = posterior_enrichment(full_result, fixed_values)
    controls = check_calibration()
    supervisor_log = root / SUPERVISOR_LOG
    supervisor_text = supervisor_log.read_text(encoding="utf-8", errors="replace")
    if not all(f"[exit] {name} 0" in supervisor_text for name in ("N2O", "NH3", "joint")):
        raise ValueError("Supervisor log does not record exit 0 for all three variants")

    status = "REQUIRES_FIXED_MOMENT_REVIEW" if fixed_moment_issues else "ACCEPTED"
    audit_path = campaign / "validation_report_20261017.json"
    table_base = root / TABLE_REL / TABLE_STEM
    table_base.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "campaign": selection["campaign"],
        "audit_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "accepted": not fixed_moment_issues,
        "primary_products_and_evidence_pass": True,
        "strict_finiteness_pass": not fixed_moment_issues,
        "fixed_coordinate_derived_moment_issues": fixed_moment_issues,
        "fixed_coordinate_stable_moments": stable_moments,
        "scope": selection,
        "dataset_rel": DATASET_REL.as_posix(),
        "dataset_sha256": DATASET_SHA256,
        "a0_reference": reference,
        "reference_sha256": sha256(reference_path),
        "operator_source_sha256": operator_sha,
        "source_equivalence": state["source_equivalence"],
        "preflight_validation": preflight,
        "full_run": {
            "campaign": FULL_REL.as_posix(),
            "config_sha256": sha256(full_config_path),
            "audit": full_audit,
            "audit_product_sha256": relative_hashes(full_audit["product_sha256"], root),
            "corrected_comparison_metadata_sha256": sha256(full_root / "comparison/comparison.json"),
            "operator_preflight_sha256": sha256(full_root / "operator_preflight.json"),
            "chi2_red_nominal": full_audit["chi2_printed"] / full_audit["dof_effective"],
        },
        "run_audits": audits,
        "operator_records": operator_records,
        "posterior_enrichment_from_corrected_free_full": enrichment,
        "calibration_controls": controls,
        "rows": rows,
        "methodological_limits": [
            "ln B compares the corrected complete A3-1000 h run only with each fixed-A0 run using the same observed dataset and operator.",
            "A positive ln B favours the free-abundance model; enrichment direction comes separately from the free-model posterior relative to the scalar A0 reference.",
            "The fixed-A0 reference is a pressure-weighted scalar atlas value, not the complete vertical pre-agricultural atmosphere.",
            "Sigma is the project's bilateral equality calibration cited by Lin et al.; it is descriptive and not a measured frequentist significance.",
            "Numerical evidence errors are combined in quadrature assuming independent run estimates; all pair rows share the same full-model estimate.",
            "The corrected full model has elevated reduced chi-square; conclusions remain conditional on model adequacy, isochemical profiles, priors, and one diagonal-noise realization.",
            "The joint constraint tests the pair jointly; its sigma is not assigned to either molecule individually.",
        ],
        "scientific_products_modified": False,
        "auditor_sha256": sha256(Path(__file__)),
    }

    audit_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    table_base.with_suffix(".json").write_text(
        json.dumps({"status": status, "accepted": not fixed_moment_issues,
                    "audit": audit_path.relative_to(root).as_posix(),
                    "method": METHOD, "rows": rows, "posterior_enrichment": enrichment},
                   indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    csv_rows = []
    for row in rows:
        csv_rows.append({key: ("N/A" if value is None else value) for key, value in row.items()})
    with table_base.with_suffix(".csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(csv_rows)

    # Round-trip checks happen before the campaign ledger is updated.
    saved_json = read_json(table_base.with_suffix(".json"))
    if saved_json["rows"] != rows:
        raise ValueError("JSON table round-trip mismatch")
    with table_base.with_suffix(".csv").open(encoding="utf-8", newline="") as stream:
        saved_csv = list(csv.DictReader(stream))
    if len(saved_csv) != 3 or [row["run_id"] for row in saved_csv] != expected_ids:
        raise ValueError("CSV table scope/row-count round-trip mismatch")
    for collection in (full_audit, *audits.values()):
        for path_text, digest in collection["product_sha256"].items():
            product_path = Path(path_text)
            if not product_path.is_absolute():
                product_path = root / product_path
            if sha256(product_path) != digest:
                raise ValueError(f"Scientific product changed during audit: {path_text}")

    state["status"] = "VALIDATED_PRIMARY_PRODUCTS_REQUIRES_REVIEW" if fixed_moment_issues else "VALIDATED_COMPLETE"
    state["acceptance"] = "PENDING_FIXED_MOMENT_REVIEW" if fixed_moment_issues else "ACCEPTED"
    state["validation_status"] = status
    state["validation_report"] = audit_path.name
    state["validation_table"] = table_base.relative_to(root).as_posix()
    state["validation_issue_count"] = len(fixed_moment_issues)
    state["strict_finiteness_pass"] = not fixed_moment_issues
    state["updated_utc"] = report["audit_utc"]
    for case in state["cases"]:
        case["validation_status"] = status
        case["acceptance"] = "PENDING_FIXED_MOMENT_REVIEW" if fixed_moment_issues else "ACCEPTED"
    state_path.write_text(json.dumps(state, indent=2, allow_nan=False) + "\n", encoding="utf-8")

    manifest_fields = list(manifest[0])
    for field in ("validation_status", "acceptance"):
        if field not in manifest_fields:
            manifest_fields.append(field)
    with manifest_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=manifest_fields)
        writer.writeheader()
        for row in manifest:
            row["validation_status"] = status
            row["acceptance"] = "PENDING_FIXED_MOMENT_REVIEW" if fixed_moment_issues else "ACCEPTED"
            writer.writerow(row)

    if fixed_moment_issues:
        stable_path = campaign / "fixed_parameter_moments_stable_20261017"
        stable_path.with_suffix(".json").write_text(
            json.dumps({"originals_preserved": True, "rows": stable_moments}, indent=2) + "\n",
            encoding="utf-8",
        )
        with stable_path.with_suffix(".csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(stable_moments[0]))
            writer.writeheader()
            writer.writerows(stable_moments)

    print(json.dumps({
        "status": status,
        "accepted": not fixed_moment_issues,
        "full_lnz": full_audit["lnz"],
        "full_error": full_audit["lnz_error"],
        "chi2": full_audit["chi2_printed"],
        "chi2_red": full_audit["chi2_printed"] / full_audit["dof_effective"],
        "rows": rows,
        "fixed_coordinate_derived_moment_issues": fixed_moment_issues,
        "posterior_enrichment": enrichment,
        "table_csv": table_base.with_suffix(".csv").relative_to(root).as_posix(),
        "table_json": table_base.with_suffix(".json").relative_to(root).as_posix(),
        "audit_json": audit_path.relative_to(root).as_posix(),
    }, indent=2))


if __name__ == "__main__":
    main()
