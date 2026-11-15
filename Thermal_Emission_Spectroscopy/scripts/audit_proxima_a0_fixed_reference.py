"""Independently audit the three authorized A3-100h scalar-A0 contrasts.

Reads preserved products only; never runs POSEIDON or a supervisor. Non-finite
derived moments of fixed coordinates are reported explicitly and prevent
strict acceptance. An explicitly authorized, hash-bound fixed-moment salvedad
can accept these derived fields while retaining the strict failure and originals.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

from fixed_abundance_reference import load_fixed_abundances
from report_proxima_loo_lin_sigma import METHOD, calibrated_sigma, check_calibration
from run_proxima_a0_reference_campaign import verify_matched_configuration
from validate_proxima_molecular_ablation_loo import (
    compare_posterior_to_multinest,
    numeric_rows,
    parse_evidence_from_result,
    parse_evidence_from_stats,
    parse_resume,
    parse_table_header,
    sha256,
    validate_log_x,
    validate_table,
)

CAMPAIGN_REL = Path(
    "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/"
    "retrievals/a0_fixed_reference_20261010"
)
TABLE_REL = Path("Thermal_Emission_Spectroscopy/final_products/tables")
EXPECTED_IDS = ["A3_100h_A0_N2O", "A3_100h_A0_NH3", "A3_100h_A0_joint"]
DATA_HASH = "78662546181a5b74391a14b7b73ae80d879200a74db6a4bc5338e3ce7eee4705"
RAW_SUFFIXES = (
    "-.txt", "-ev.dat", "-live.points", "-phys_live.points",
    "-post_equal_weights.dat", "-resume.dat", "-stats.dat", "-summary.txt",
)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_fixed_moment_salvedad(audits, previous_report):
    """Waive only previously reviewed NaN sigmas of exactly fixed coordinates.

    This gate never bypasses the primary-product, prior or evidence validators.
    Bind the decision to the original strict audit and its scientific hashes.
    """
    if not previous_report["primary_products_and_evidence_pass"]:
        raise ValueError("Previous primary-product audit did not pass")
    previous_audits = previous_report["run_audits"]
    for run_id, audit in audits.items():
        previous = previous_audits[run_id]
        if audit["product_sha256"] != previous["product_sha256"]:
            raise ValueError("Reviewed scientific product hashes changed")
        issues = audit["derived_moment_audit"]["issues"]
        if issues != previous["derived_moment_audit"]["issues"]:
            raise ValueError("Reviewed fixed-moment issues changed")
        for issue in issues:
            species = issue["parameter"].removeprefix("log_")
            if (issue["quantity"] != "derived_standard_deviation"
                    or issue["token"] != "NaN"
                    or species not in audit["fixed_coordinate_spreads"]):
                raise ValueError("Issue is outside the fixed-moment salvedad")
            spread = audit["fixed_coordinate_spreads"][species]
            value = audit["fixed_log10_vmr"][species]
            if (spread["minimum"] != value or spread["maximum"] != value
                    or spread["centered_second_moment_about_reference"] != 0):
                raise ValueError("Fixed coordinate has nonzero spread")


def stable_fixed_moments(run_id, result_path, config):
    """Independent centered moments; leave the original MultiNest files intact."""
    stem = result_path.name.removesuffix("_results.txt")
    raw_dir = result_path.parent.parent / "MultiNest_raw"
    equal_path = raw_dir / f"{stem}-post_equal_weights.dat"
    weighted_path = raw_dir / f"{stem}-.txt"
    equal_rows = list(numeric_rows(equal_path))
    weighted_rows = list(numeric_rows(weighted_path))
    weights = [row[0] for row in weighted_rows]
    total_weight = math.fsum(weights)
    if total_weight <= 0 or any(weight < 0 for weight in weights):
        raise ValueError("Invalid posterior weights")
    records = []
    for index, name in enumerate(config["parameters"]):
        low, high = config["prior_ranges"][name]
        if low != high:
            continue
        equal_values = [row[index] for row in equal_rows]
        weighted_values = [row[index + 2] for row in weighted_rows]
        if any(value != low for value in equal_values + weighted_values):
            raise ValueError("Stable fixed-moment sidecar requires exact constants")
        equal_var = math.fsum((value - low) ** 2 for value in equal_values) / len(equal_values)
        weighted_var = math.fsum(
            weight * (value - low) ** 2 for weight, value in zip(weights, weighted_values)
        ) / total_weight
        records.append({
            "run_id": run_id, "parameter": name, "fixed_value": low,
            "equal_weight_mean": low, "equal_weight_sd": math.sqrt(equal_var),
            "weighted_mean": low, "weighted_sd": math.sqrt(weighted_var),
            "equal_weight_rows": len(equal_rows), "weighted_rows": len(weighted_rows),
            "equal_weight_sha256": sha256(equal_path),
            "weighted_sha256": sha256(weighted_path),
            "method": "centered second moment about exact fixed value; math.fsum",
        })
    return records


def mapped_path(value, root):
    marker = "/mnt/c/Proyectos/Astro/ExoFarm_MDwarfs/"
    if value.startswith(marker):
        return root / value[len(marker):]
    path = Path(value)
    return path if path.is_absolute() else root / path


def check_coordinates(row, parameters, priors, offset=0):
    """Check physical coordinates, including zero-width priors, in every row."""
    for index, name in enumerate(parameters):
        value = row[offset + index]
        low, high = priors[name]
        # Text exports round physical parameters; 2e-7 covers that precision.
        tolerance = 2e-7 if low != high else 1e-12
        if not low - tolerance <= value <= high + tolerance:
            raise ValueError(f"{name}={value} outside frozen prior [{low}, {high}]")


def check_quantile_grid(path, pressure=False):
    previous = math.inf if pressure else -math.inf

    def check(row, _):
        nonlocal previous
        invalid_grid = row[0] <= 0 or (
            row[0] >= previous if pressure else row[0] <= previous
        )
        if invalid_grid or any(a > b for a, b in zip(row[1:], row[2:])):
            raise ValueError(f"Invalid grid or unordered quantiles: {path}")
        if pressure and any(value <= 0 for value in row[1:]):
            raise ValueError(f"Non-positive temperature: {path}")
        previous = row[0]

    return validate_table(
        path, skip_lines=1, expected_columns=6,
        min_rows=100 if pressure else 2,
        max_rows=100 if pressure else None, row_check=check,
    )


def check_fixed_profiles(path, fixed):
    species = None
    counts = dict.fromkeys(fixed, 0)
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"P\s*\(bar\)\s*\|\s*log_([A-Za-z0-9]+):", line.strip())
        if match:
            species = match.group(1)
        elif species in fixed and line.strip():
            row = [float(token) for token in line.split()]
            # log-X quantiles are printed to eight decimal places.
            if any(abs(value - fixed[species]) > 5.1e-9 for value in row[1:]):
                raise ValueError(f"Fixed abundance changed in log-X: {species}")
            counts[species] += 1
    if any(count != 100 for count in counts.values()):
        raise ValueError(f"Fixed profile coverage mismatch: {counts}")
    return counts


def audit_derived_moments(summary_path, stats_path, header, fixed):
    """Locate non-finite moments without permitting them in scientific inputs.

    Summary layout is means, sigmas, ML, MAP, log evidence, max log likelihood.
    Fixed-coordinate moment failures remain an explicit strict-audit failure;
    they are never replaced in the preserved MultiNest files.
    """
    issues = []
    summary_rows = []
    for line_number, line in enumerate(summary_path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        row = [float(token) for token in line.split()]
        if len(row) != 4 * len(header) + 2:
            raise ValueError(f"Unexpected MultiNest summary layout: {summary_path}")
        for index, value in enumerate(row):
            if math.isfinite(value):
                continue
            parameter_index = index - len(header)
            if not 0 <= parameter_index < len(header):
                raise ValueError(f"Non-finite primary summary field: {summary_path}")
            name = header[parameter_index]
            if name.removeprefix("log_") not in fixed or not math.isnan(value):
                raise ValueError(f"Non-finite free-parameter moment: {summary_path}")
            issues.append({"file": str(summary_path), "line": line_number,
                           "column": index + 1, "parameter": name,
                           "quantity": "derived_standard_deviation", "token": "NaN"})
        summary_rows.append(row)
    for line_number, line in enumerate(stats_path.read_text().splitlines(), 1):
        if "nan" not in line.lower() and "inf" not in line.lower():
            continue
        fields = line.split()
        if len(fields) != 3 or not fields[0].isdigit():
            raise ValueError(f"Non-finite evidence/metadata field: {stats_path}:{line_number}")
        name = header[int(fields[0]) - 1]
        if (name.removeprefix("log_") not in fixed or not math.isfinite(float(fields[1]))
                or not math.isnan(float(fields[2]))):
            raise ValueError(f"Unexpected non-finite stats field: {stats_path}:{line_number}")
        issues.append({"file": str(stats_path), "line": line_number, "column": 3,
                       "parameter": name, "quantity": "derived_standard_deviation", "token": "NaN"})
    if not summary_rows:
        raise ValueError("Empty MultiNest summary")
    # Serialize neither NaN nor Infinity into the audit JSON.
    return {"shape": [len(summary_rows), len(summary_rows[0])], "issues": issues,
            "nested_summary_lnz": summary_rows[-1][-2]}


def audit_products(result_path, config, dataset, fixed):
    retrieval = result_path.parent.parent
    stem = result_path.name.removesuffix("_results.txt")
    result = parse_evidence_from_result(result_path, expected_parameters=15)
    if result["model"] != stem or result["dataset_label"] != dataset.name:
        raise ValueError(f"Model or dataset label mismatch: {result_path}")
    if config["dataset_sha256"] != sha256(dataset):
        raise ValueError("Configuration/dataset hash mismatch")
    raw = {suffix: retrieval / "MultiNest_raw" / f"{stem}{suffix}" for suffix in RAW_SUFFIXES}
    samples = retrieval / "samples" / f"{stem}_samples.txt"
    spectrum = retrieval / "samples" / f"{stem}_spectrum_retrieved.txt"
    pt = retrieval / "samples" / f"{stem}_PT_retrieved.txt"
    logx = retrieval / "samples" / f"{stem}_log_X_retrieved.txt"
    header = parse_table_header(samples)
    if header != config["parameters"] or len(header) != 15:
        raise ValueError(f"Posterior parameter order differs: {samples}")
    priors = config["prior_ranges"]
    sample_shape = validate_table(
        samples, skip_lines=1, expected_columns=15,
        row_check=lambda row, _: check_coordinates(row, header, priors),
    )
    equal_shape = validate_table(
        raw["-post_equal_weights.dat"], expected_columns=16,
        row_check=lambda row, _: check_coordinates(row, header, priors),
    )
    compared = compare_posterior_to_multinest(samples, raw["-post_equal_weights.dat"], 15)
    if equal_shape[0] != sample_shape[0] or compared != sample_shape[0]:
        raise ValueError("Equal-weight/exported posterior mismatch")
    spectrum_shape = check_quantile_grid(spectrum)
    pt_shape = check_quantile_grid(pt, pressure=True)
    logx_rows = validate_log_x(logx, "")  # N2 plus all seven opacity species.
    fixed_profile_rows = check_fixed_profiles(logx, fixed)
    raw_shapes = {}
    for suffix in ("-.txt", "-ev.dat", "-live.points", "-phys_live.points"):
        offset = 2 if suffix == "-.txt" else 0
        row_check = None if suffix in ("-live.points", "-summary.txt") else (
            lambda row, _, offset=offset: check_coordinates(row, header, priors, offset)
        )
        raw_shapes[suffix] = validate_table(raw[suffix], row_check=row_check)
    for suffix in ("-live.points", "-phys_live.points"):
        if raw_shapes[suffix][0] != 800:
            raise ValueError("Final live-point count differs from N_live=800")
    resume = parse_resume(raw["-resume.dat"])
    if raw_shapes["-ev.dat"][0] != resume["replacements"] - 800:
        raise ValueError("Resume/evidence trace counters disagree")
    lnz, error = parse_evidence_from_stats(raw["-stats.dat"])
    moments = audit_derived_moments(raw["-summary.txt"], raw["-stats.dat"], header, fixed)
    raw_shapes["-summary.txt"] = moments["shape"]
    if abs(moments["nested_summary_lnz"] - lnz) > 1e-10:
        raise ValueError("Nested summary/global stats evidence disagree")
    if (abs(lnz - result["lnz_printed"]) > 0.0051
            or abs(error - result["lnz_error_printed"]) > 0.0051):
        raise ValueError("Precise stats and rounded POSEIDON evidence disagree")
    result_text = result_path.read_text(encoding="utf-8")
    chi2 = float(re.search(r"->\s*chi\^2\s*=\s*([-+\d.eE]+)", result_text).group(1))
    effective_dof = 31 - config["effective_free_dimension"]
    products = [result_path, samples, spectrum, pt, logx, *raw.values()]
    fixed_spreads = {}
    # A centered second moment is stable when the coordinate is exactly fixed.
    # This is an independent sidecar diagnosis, not a repair of MultiNest output.
    for species, value in fixed.items():
        index = header.index("log_" + species)
        coordinates = [row[index] for row in numeric_rows(raw["-post_equal_weights.dat"])]
        fixed_spreads[species] = {
            "minimum": min(coordinates), "maximum": max(coordinates),
            "centered_second_moment_about_reference": math.fsum(
                (coordinate - value) ** 2 for coordinate in coordinates
            ) / len(coordinates),
        }
    return {
        "lnz": lnz, "lnz_error": error, "posterior_samples": sample_shape[0],
        "posterior_rows_crosschecked": compared, "spectrum_shape": spectrum_shape,
        "pt_shape": pt_shape, "logx_rows": logx_rows, "fixed_profile_rows": fixed_profile_rows,
        "raw_shapes": raw_shapes, "resume": resume,
        "derived_moment_audit": moments, "fixed_coordinate_spreads": fixed_spreads,
        "chi2_printed": chi2, "dof_historical_poseidon": result["dof"],
        "chi2_red_historical_poseidon": result["chi2_red"],
        "dof_effective": effective_dof,
        "chi2_red_effective_from_rounded_chi2": chi2 / effective_dof,
        "product_sha256": {str(path): sha256(path) for path in products},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--accept", action="store_true")
    parser.add_argument("--accept-fixed-moment-salvedad", action="store_true",
                        help="Explicit human-authorized acceptance of reviewed fixed-coordinate NaN sigmas only")
    parser.add_argument("--record-review", action="store_true",
                        help="Record the outstanding audit issue without accepting it")
    args = parser.parse_args()
    if args.accept_fixed_moment_salvedad and not args.accept:
        parser.error("The fixed-moment salvedad requires --accept")
    if args.accept and args.record_review:
        parser.error("Acceptance and record-review are mutually exclusive")
    root = Path(__file__).resolve().parents[2]
    campaign = root / CAMPAIGN_REL
    state_path = campaign / "campaign_state.json"
    state = read_json(state_path)
    selection = read_json(campaign / "selected_scope.json")
    cases = state["cases"]
    if ([case["run_id"] for case in cases] != EXPECTED_IDS
            or selection["selected_run_ids"] != EXPECTED_IDS
            or selection["scenarios"] != ["A3"] or selection["hours"] != [100]
            or state["counts"] != {"pending": 0, "running": 0, "complete": 3, "failed": 0}):
        raise ValueError("Authorized scope or completion ledger mismatch")
    with (campaign / "manifest.csv").open(encoding="utf-8", newline="") as stream:
        manifest = list(csv.DictReader(stream))
    if [row["run_id"] for row in manifest] != EXPECTED_IDS:
        raise ValueError("Manifest scope differs from selected scope")
    for row, case in zip(manifest, cases):
        for key in ("status", "return_code", "dataset_sha256", "end_utc", "archive_dir"):
            if row[key] != str(case[key]):
                raise ValueError(f"Manifest/state mismatch: {case['run_id']} / {key}")
        if case["status"] != "complete" or case["return_code"] != 0:
            raise ValueError("Non-successful retrieval")
    preflight = read_json(campaign / "preflight_progress.json")["verified"]
    if [record["run_id"] for record in preflight] != EXPECTED_IDS or any(
        record["status"] != "PASS" for record in preflight
    ):
        raise ValueError("Preflight ledger mismatch")
    reference_path = campaign / "a0_reference.json"
    reference = read_json(reference_path)
    if sha256(reference_path) != state["reference_sha256"]:
        raise ValueError("Reference hash changed")
    fixed_values = load_fixed_abundances(reference_path, ["N2O", "NH3"], root)
    if sha256(root / "Thermal_Emission_Spectroscopy/scripts/run_proxima_a0_reference_campaign.py") != state["supervisor_code_sha256"]:
        raise ValueError("Supervisor source differs from the frozen execution hash")
    dataset = mapped_path(cases[0]["dataset"], root)
    if sha256(dataset) != DATA_HASH:
        raise ValueError("Official dataset hash differs")
    validate_table(dataset, skip_lines=1, expected_columns=4, min_rows=31, max_rows=31)
    previous = -math.inf
    for row in numeric_rows(dataset, skip_lines=1):
        if row[0] <= previous or row[1] <= 0 or row[3] <= 0:
            raise ValueError("Invalid observed wavelength, width or error")
        previous = row[0]
    full_config = read_json(campaign / "resolved/A3_100h_A0_N2O_fullcheck.json")
    full_result = mapped_path(cases[0]["full_results"], root)
    if sha256(full_result) != cases[0]["full_results_sha256"]:
        raise ValueError("Official full result changed")
    full_audit = audit_products(full_result, full_config, dataset, {})
    controls = check_calibration()
    audits, rows, stable_moments = {}, [], []
    for case in cases:
        run_id = case["run_id"]
        config_path = campaign / "resolved" / f"{run_id}.json"
        config = read_json(config_path)
        matched_full = read_json(campaign / "resolved" / f"{run_id}_fullcheck.json")
        # Setup-only tags identify each preflight; all scientific fields agree.
        if ({key: value for key, value in matched_full.items() if key != "model_name"}
                != {key: value for key, value in full_config.items() if key != "model_name"}):
            raise ValueError("Three preflight full configurations differ")
        verify_matched_configuration(matched_full, config, case)
        for species in case["fixed_species"]:
            if case["fixed_log10_vmr"][species] != fixed_values[species]:
                raise ValueError("Case fixed value differs from reference")
        if case["dataset_sha256"] != DATA_HASH or mapped_path(case["full_results"], root) != full_result:
            raise ValueError("Pair does not share the official dataset/baseline")
        for suffix in ("", "_fullcheck"):
            text = (campaign / "preflight" / f"{run_id}{suffix}.log").read_text()
            if "[setup-only] model, dataset, and priors validated; MultiNest skipped" not in text:
                raise ValueError("Preflight completion marker missing")
        log_path = mapped_path(case["launch_log"], root)
        log = log_path.read_text(encoding="utf-8", errors="replace")
        stem = config["model_name"]
        if ("Sampling finished. Exiting MultiNest" not in log or "All done!" not in log
                or log.count(f"[done] {stem}") != 6):
            raise ValueError(f"Six-rank completion markers missing: {run_id}")
        if re.search(r"Traceback|MPI_ABORT|Fatal|Out of memory|Killed|\[failed\]", log):
            raise ValueError(f"Fatal marker in preserved log: {run_id}")
        result = mapped_path(case["archive_dir"], root) / (
            f"POSEIDON_output/proxima_b_earthlike/retrievals/results/{stem}_results.txt"
        )
        audit = audit_products(result, config, dataset, case["fixed_log10_vmr"])
        audit.update(config_sha256=sha256(config_path), log_sha256=sha256(log_path),
                     declared_dimension=15, effective_free_dimension=config["effective_free_dimension"],
                     fixed_log10_vmr=case["fixed_log10_vmr"], return_code=0)
        audits[run_id] = audit
        stable_moments.extend(stable_fixed_moments(run_id, result, config))
        ln_b = full_audit["lnz"] - audit["lnz"]
        sigma, log_p = calibrated_sigma(ln_b)
        rows.append({
            "run_id": run_id, "scenario": "A3", "hours": 100,
            "fixed_species": "+".join(case["fixed_species"]),
            "lnz_full": full_audit["lnz"], "lnz_full_error": full_audit["lnz_error"],
            "lnz_a0_fixed": audit["lnz"], "lnz_a0_fixed_error": audit["lnz_error"],
            "ln_B": ln_b, "ln_B_numerical_error": math.hypot(full_audit["lnz_error"], audit["lnz_error"]),
            "sigma_calibrated_bilateral": sigma, "log_p_calibrated": log_p,
            "sigma_method": METHOD, "dataset_sha256": DATA_HASH,
            "posterior_samples": audit["posterior_samples"],
            "effective_free_dimension": config["effective_free_dimension"],
        })
    utc = datetime.now(timezone.utc).isoformat()
    issues = [issue for audit in audits.values() for issue in audit["derived_moment_audit"]["issues"]]
    audit_path = campaign / "validation_report_20261011.json"
    snapshot_path = campaign / "validation_report_20261011_pre_acceptance.json"
    decision_path = campaign / "acceptance_decision_20261011.json"
    if decision_path.exists() and args.record_review:
        raise ValueError("An accepted campaign cannot be reverted by record-review")
    with_salvedad = args.accept_fixed_moment_salvedad
    if decision_path.exists() and not with_salvedad:
        # A later strict diagnostic must not overwrite the accepted audit.
        audit_path = campaign / "validation_report_20261011_strict_recheck.json"
    if with_salvedad:
        reviewed_path = snapshot_path if snapshot_path.exists() else audit_path
        previous_report = read_json(reviewed_path)
        validate_fixed_moment_salvedad(audits, previous_report)
        if previous_report["full_audit"]["product_sha256"] != full_audit["product_sha256"]:
            raise ValueError("Reviewed full-model products changed")
        if previous_report["rows"] != rows:
            raise ValueError("Evidence or calibrated sigma changed since review")
        if not snapshot_path.exists():
            snapshot_path.write_bytes(audit_path.read_bytes())
        decision = {
            "status": "ACCEPTED_WITH_FIXED_MOMENT_SALVEDAD",
            "decision_utc": utc, "authorization_source": "direct user request in this chat, 2026-10-11",
            "authorization_text": "Registra todo acepta lo aceptado",
            "scope": EXPECTED_IDS, "waived_quantity": "derived_standard_deviation of exactly fixed coordinates only",
            "strict_finiteness_pass": False, "originals_preserved": True,
            "reviewed_audit": snapshot_path.name, "reviewed_audit_sha256": sha256(snapshot_path),
            "issues": issues, "full_product_sha256": full_audit["product_sha256"],
            "run_product_sha256": {key: value["product_sha256"] for key, value in audits.items()},
        }
        if decision_path.exists():
            old_decision = read_json(decision_path)
            if any(old_decision[key] != decision[key] for key in decision if key != "decision_utc"):
                raise ValueError("Existing acceptance decision differs")
        else:
            decision_path.write_text(json.dumps(decision, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    accepted = not issues or with_salvedad
    status = ("ACCEPTED_WITH_FIXED_MOMENT_SALVEDAD" if with_salvedad
              else "REQUIRES_REVIEW" if issues else "ACCEPTED")
    report = {
        "status": status, "strict_finiteness_pass": not issues,
        "primary_products_and_evidence_pass": True, "issues": issues,
        "audit_utc": utc, "campaign": state["campaign"],
        "scope": selection, "dataset_sha256": DATA_HASH, "reference": reference,
        "full_audit": full_audit, "run_audits": audits,
        "calibration_controls": controls, "rows": rows,
        "methodological_limits": [
            "Equality calibration of a bound; not a measured frequentist significance",
            "Fixed scalar A0 reference; not the full vertical A0 atmosphere",
            "Relative evidence conditioned on priors, isochem and one diagonal noise realization",
            "Joint sigma belongs to the joint restriction; not to either molecule individually",
            "Numerical errors added in quadrature assuming independent evidence estimation; shared full error correlates rows",
        ],
        "auditor_sha256": sha256(Path(__file__)),
        "protected_products_modified": False,
        "accepted": accepted,
        "acceptance_decision": decision_path.name if with_salvedad else None,
        "stable_fixed_moments": stable_moments,
    }
    table_name = "life_proxima_a0_lnB_sigma_lin_2026-10-11"
    if decision_path.exists() and not with_salvedad:
        table_name += "_strict_recheck"
    elif issues and not accepted:
        table_name += "_provisional"
    table_base = root / TABLE_REL / table_name
    table_base.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    with table_base.with_suffix(".csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    table_base.with_suffix(".json").write_text(
        json.dumps({"status": status, "accepted": accepted,
                    "audit": str(audit_path.relative_to(root)), "method": METHOD, "rows": rows},
                   indent=2, allow_nan=False) + "\n", encoding="utf-8",
    )
    # Re-read the deliverables before acceptance; count and equality are exact.
    if read_json(table_base.with_suffix(".json"))["rows"] != rows:
        raise ValueError("JSON table round trip failed")
    with table_base.with_suffix(".csv").open(encoding="utf-8", newline="") as stream:
        saved_rows = list(csv.DictReader(stream))
    if len(saved_rows) != 3 or [row["run_id"] for row in saved_rows] != EXPECTED_IDS:
        raise ValueError("CSV scope/row count failed")
    if args.accept:
        if issues and not with_salvedad:
            raise ValueError("Strict finiteness failed; acceptance is prohibited. See saved audit and provisional table.")
        sidecar = campaign / "fixed_parameter_moments_stable_20261011"
        sidecar.with_suffix(".json").write_text(
            json.dumps({"originals_preserved": True, "rows": stable_moments}, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        with sidecar.with_suffix(".csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(stable_moments[0]))
            writer.writeheader()
            writer.writerows(stable_moments)
        if read_json(sidecar.with_suffix(".json"))["rows"] != stable_moments:
            raise ValueError("Stable-moment sidecar round trip failed")
        for audit in [full_audit, *audits.values()]:
            if any(sha256(Path(path)) != digest for path, digest in audit["product_sha256"].items()):
                raise ValueError("Original scientific product changed during audit")
        state["sampling_status"] = "SAMPLING_COMPLETE"
        state["status"] = "VALIDATED_COMPLETE_WITH_SALVEDAD" if with_salvedad else "VALIDATED_COMPLETE"
        state["validation_status"] = status
        state["strict_finiteness_pass"] = not issues
        state["acceptance_decision"] = decision_path.name if with_salvedad else None
        state["validation_issue_count"] = len(issues)
        state["audit_utc"] = utc
        state["validation_report"] = audit_path.name
        for case in state["cases"]:
            case["validation_status"] = (
                "ACCEPTED_WITH_FIXED_MOMENT_SALVEDAD"
                if audits[case["run_id"]]["derived_moment_audit"]["issues"] else "ACCEPTED"
            )
        state_path.write_text(json.dumps(state, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    elif args.record_review:
        if not issues:
            raise ValueError("No outstanding issue to record; use --accept after review")
        # Keep sampling status/exit codes unchanged and separate audit acceptance.
        state["validation_status"] = "REQUIRES_REVIEW"
        state["audit_utc"] = utc
        state["validation_report"] = audit_path.name
        state["validation_issue_count"] = len(issues)
        for case in state["cases"]:
            case["validation_status"] = (
                "REQUIRES_REVIEW" if audits[case["run_id"]]["derived_moment_audit"]["issues"]
                else "ACCEPTED"
            )
        state_path.write_text(json.dumps(state, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "issues": issues, "rows": rows}, indent=2))


if __name__ == "__main__":
    main()
