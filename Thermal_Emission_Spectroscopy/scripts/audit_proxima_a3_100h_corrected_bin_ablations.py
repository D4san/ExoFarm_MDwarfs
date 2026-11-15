#!/usr/bin/env python3
"""Independently audit the corrected-bin A3-100 h NH3/N2O ablations.

This is a read-only audit of finished retrieval products. It does not launch,
resume, or modify any sampler. The audit writes only its CSV/JSON summaries
inside the named two-run campaign.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path, PurePosixPath
from typing import Any

from report_proxima_loo_lin_sigma import calibrated_sigma, check_calibration
import validate_proxima_molecular_ablation_loo as validator
from validate_proxima_molecular_ablation_loo import (
    BASE_PARAMETERS,
    GAS_PARAMETERS,
    compare_posterior_to_multinest,
    numeric_rows,
    parse_evidence_from_result,
    parse_evidence_from_stats,
    parse_resume,
    parse_table_header,
    require_file,
    sha256,
    validate_log_x,
    validate_table,
)


CAMPAIGN_REL = Path(
    "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/"
    "retrievals/a3_100h_binning_corrected_loo_20261019"
)
DATASET_SHA256 = "78662546181a5b74391a14b7b73ae80d879200a74db6a4bc5338e3ce7eee4705"
THRESHOLDS = {"N2O": -6.884325289636784, "NH3": -9.950526295665036}
EXPECTED_RUNS = {"A3_100h_no_NH3": "NH3", "A3_100h_no_N2O": "N2O"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_json(path: Path) -> dict[str, Any]:
    require_file(path)
    return json.loads(path.read_text(encoding="utf-8"))


def repo_path(value: str | Path, root: Path) -> Path:
    """Map repository-relative and WSL paths without relying on Path.sep."""
    raw = str(value).replace("\\", "/")
    marker = "/mnt/c/Proyectos/Astro/ExoFarm_MDwarfs/"
    if raw.startswith(marker):
        return root / Path(*PurePosixPath(raw[len(marker):]).parts)
    if raw.startswith("/mnt/c/"):
        return Path("C:/") / Path(*PurePosixPath(raw[len("/mnt/c/"):]).parts)
    return root / Path(*PurePosixPath(raw).parts)


def quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = probability * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def posterior_summary(path: Path, species: str | None = None) -> dict[str, Any]:
    header = parse_table_header(path)
    rows = list(numeric_rows(path, skip_lines=1))
    require(all(len(row) == len(header) for row in rows), f"ragged posterior: {path}")
    summary: dict[str, Any] = {"rows": len(rows), "columns": len(header)}
    if species is not None:
        name = f"log_{species}"
        require(name in header, f"{name} absent from retained-species posterior {path}")
        values = [row[header.index(name)] for row in rows]
        threshold = THRESHOLDS[species]
        summary.update(
            parameter=name,
            a0_log10_threshold=threshold,
            q16=quantile(values, 0.16),
            median=quantile(values, 0.50),
            q84=quantile(values, 0.84),
            q025=quantile(values, 0.025),
            q975=quantile(values, 0.975),
            samples_above_a0=sum(value > threshold for value in values),
            probability_above_a0=sum(value > threshold for value in values) / len(values),
        )
    return summary


def validate_config_pair(full: dict[str, Any], ablated: dict[str, Any], species: str) -> None:
    require(ablated["dataset_sha256"] == full["dataset_sha256"] == DATASET_SHA256,
            f"dataset hash mismatch in resolved config for no-{species}")
    expected_parameters = set(full["parameters"]) - {f"log_{species}"}
    require(set(ablated["parameters"]) == expected_parameters and len(ablated["parameters"]) == 14,
            f"parameter exclusion/config dimension mismatch for no-{species}")
    require(ablated["declared_dimension"] == 14 and ablated["effective_free_dimension"] == 13,
            f"unexpected declared/free dimensions for no-{species}")
    require(f"log_{species}" not in ablated["parameters"], f"excluded parameter remains for {species}")
    require(species not in ablated["param_species"], f"excluded opacity remains for {species}")
    require(ablated["fixed_parameters"] == full["fixed_parameters"],
            f"fixed parameter mismatch for no-{species}")
    require(ablated["fixed_log10_abundances"] == full["fixed_log10_abundances"],
            f"fixed abundances mismatch for no-{species}")
    require(ablated["n_live"] == full["n_live"] == 800,
            f"N_live mismatch for no-{species}")
    for key in ("R", "wl_min", "wl_max", "ev_tol", "surface_pressure_mode",
                "error_inflation", "x_profile", "likelihood"):
        require(ablated[key] == full[key], f"matched retrieval setting {key} differs for no-{species}")
    for parameter in expected_parameters:
        require(ablated["prior_types"][parameter] == full["prior_types"][parameter],
                f"prior type differs for {parameter} in no-{species}")
        require(ablated["prior_ranges"][parameter] == full["prior_ranges"][parameter],
                f"prior range differs for {parameter} in no-{species}")


def check_operator(path: Path, run: dict[str, Any], expected_hash: str) -> dict[str, Any]:
    record = read_json(path)
    require(record.get("status") == "PASS", f"operator callback record did not pass: {path}")
    require(record.get("dataset_sha256") == expected_hash, f"operator dataset hash mismatch: {path}")
    require(record.get("channels") == 31, f"operator channel count mismatch: {path}")
    require(record.get("native_grid_um") == [3.0, 20.0], f"operator grid mismatch: {path}")
    require("midpoint-edge photon overlap" in record.get("operator", "") and
            "exact channel centre" in record.get("operator", ""),
            f"operator identity does not match corrected photon-overlap definition: {path}")
    require(record.get("actual_poseidon_callback_bound") is True,
            f"actual POSEIDON callback was not bound: {path}")
    require("sampling" in record.get("binding_scope", "") and "postprocessing" in record.get("binding_scope", ""),
            f"operator binding scope incomplete: {path}")
    require(float(record.get("callback_truth_closure_max_relative", math.inf)) < 1e-12,
            f"operator callback closure failed: {path}")
    require(record.get("mpi_size") == int(run["mpi_ranks"]), f"operator MPI size mismatch: {path}")
    return record


def validate_baseline(root: Path, campaign_state: dict[str, Any], data_path: Path) -> dict[str, Any]:
    baseline = campaign_state["baseline_full"]
    baseline_campaign = root / Path(*PurePosixPath(baseline["campaign"]).parts)
    baseline_state = read_json(baseline_campaign / "campaign_state.json")
    require(baseline_state.get("exit_code") == 0 and
            baseline_state.get("dataset_sha256") == DATASET_SHA256,
            "full baseline campaign ledger does not confirm matched dataset and exit zero")
    require(baseline_state.get("retry_preflight") == "PASS",
            "full baseline retry preflight is not recorded as PASS")
    result_path = root / Path(*PurePosixPath(baseline["result"]).parts)
    parsed = parse_evidence_from_result(result_path, expected_parameters=15)
    require(parsed["n_live"] == 800 and parsed["dataset_label"] == data_path.name,
            "full-model result metadata does not match matched dataset/N_live")
    require(sha256(data_path) == DATASET_SHA256, "full-model observed dataset hash mismatch")
    stem = result_path.name.removesuffix("_results.txt")
    raw_dir = result_path.parent.parent / "MultiNest_raw"
    raw_prefix = raw_dir / stem
    raw = {suffix: Path(f"{raw_prefix}{suffix}") for suffix in (
        "-.txt", "-ev.dat", "-live.points", "-phys_live.points",
        "-post_equal_weights.dat", "-resume.dat", "-stats.dat", "-summary.txt",
    )}
    lnz, error = parse_evidence_from_stats(raw["-stats.dat"])
    require(abs(lnz - float(parsed["lnz_printed"])) <= 0.0051,
            "full-model result lnZ does not agree with native MultiNest stats")
    require(abs(error - float(parsed["lnz_error_printed"])) <= 0.0051,
            "full-model result lnZ error does not agree with native MultiNest stats")
    require(abs(lnz - float(baseline["lnz"])) <= 1e-10 and
            abs(error - float(baseline["lnz_error"])) <= 1e-10,
            "campaign baseline evidence does not match native stats")

    config_path = root / Path(*PurePosixPath(baseline["configuration"]).parts)
    config = read_json(config_path)
    require(config["dataset_sha256"] == DATASET_SHA256, "baseline resolved config dataset hash mismatch")
    require(config["declared_dimension"] == 15 and config["effective_free_dimension"] == 14,
            "baseline resolved parameter dimensions mismatch")
    require(config["n_live"] == 800 and config["error_inflation"] == "none",
            "baseline resolved sampling/noise configuration mismatch")
    require(config["wl_min"] == 3.0 and config["wl_max"] == 20.0,
            "baseline resolved wavelength range mismatch")
    require(config["R"] == 10000 and config["ev_tol"] == 0.5 and
            config["x_profile"] == "isochem" and
            config["surface_pressure_mode"] == "fixed-black",
            "baseline resolved retrieval settings do not match the authorized comparison")

    operator_path = result_path.parent.parent.parent / "operator_preflight_mpi14_retry01.json"
    operator = read_json(operator_path)
    require(operator.get("status") == "PASS" and operator.get("dataset_sha256") == DATASET_SHA256,
            "full-model corrected operator preflight did not pass for matched dataset")
    require(operator.get("actual_forward_model_callback_bound") is True and
            operator.get("sampling_and_postprocessing_binding") is True,
            "full-model corrected operator callback/binding was not verified")
    require(operator.get("channels") == 31 and operator.get("native_wavelength_range_um") == [3.0, 20.0],
            "full-model corrected operator channel/grid metadata mismatch")
    require(float(operator.get("maximum_relative_truth_closure", math.inf)) < 1e-12,
            "full-model corrected operator truth closure exceeded tolerance")

    samples_path = result_path.parent.parent / "samples" / f"{stem}_samples.txt"
    header = parse_table_header(samples_path)
    expected_header = set(BASE_PARAMETERS) | set(GAS_PARAMETERS)
    require(len(header) == 15 and set(header) == expected_header, "full-model posterior parameter header mismatch")
    surface_index = header.index("log_P_surf")
    sample_rows, sample_columns = validate_table(
        samples_path, skip_lines=1, expected_columns=15,
        row_check=lambda row, _: require(abs(row[surface_index]) <= 1e-12,
                                          "full posterior has non-fixed log_P_surf sample"),
    )
    equal_rows, equal_columns = validate_table(raw["-post_equal_weights.dat"], min_rows=1)
    require(equal_columns >= sample_columns and equal_rows == sample_rows,
            "full POSEIDON posterior dimensions differ from MultiNest equal-weight posterior")
    require(compare_posterior_to_multinest(samples_path, raw["-post_equal_weights.dat"], 15) == sample_rows,
            "full POSEIDON posterior rows differ from MultiNest equal-weight samples")

    spectrum = result_path.parent.parent / "samples" / f"{stem}_spectrum_retrieved.txt"
    previous = -math.inf
    def check_spectrum(row: list[float], _: int) -> None:
        nonlocal previous
        require(row[0] > previous and all(a <= b for a, b in zip(row[1:], row[2:])),
                "full retrieved spectrum wavelength/quantiles are invalid")
        previous = row[0]
    spectrum_rows, _ = validate_table(spectrum, skip_lines=1, expected_columns=6,
                                      min_rows=2, row_check=check_spectrum)

    pt = result_path.parent.parent / "samples" / f"{stem}_PT_retrieved.txt"
    pressure = math.inf
    def check_pt(row: list[float], _: int) -> None:
        nonlocal pressure
        require(0 < row[0] < pressure and all(a <= b for a, b in zip(row[1:], row[2:])),
                "full P-T pressure grid/quantiles are invalid")
        pressure = row[0]
    pt_rows, _ = validate_table(pt, skip_lines=1, expected_columns=6,
                                min_rows=100, max_rows=100, row_check=check_pt)
    logx = result_path.parent.parent / "samples" / f"{stem}_log_X_retrieved.txt"
    logx_rows = validate_log_x(logx, "")

    raw_shapes = {}
    for suffix in ("-.txt", "-ev.dat", "-live.points", "-phys_live.points", "-summary.txt"):
        raw_shapes[suffix] = list(validate_table(raw[suffix], min_rows=1))
    for suffix in ("-live.points", "-phys_live.points"):
        require(raw_shapes[suffix][0] == 800, f"full MultiNest {suffix} does not contain 800 live points")
    resume = parse_resume(raw["-resume.dat"])
    require(raw_shapes["-ev.dat"][0] == resume["replacements"] - resume["n_live"],
            "full MultiNest ev/resume replacement counts disagree")

    retrieval_log = result_path.parent.parent.parent / "retrieval.log"
    require_file(retrieval_log)
    log_text = retrieval_log.read_text(encoding="utf-8", errors="replace")
    require("Sampling finished. Exiting MultiNest" in log_text and "All done!" in log_text,
            "full-model retrieval log lacks successful sampling/postprocessing completion")
    require("[operator-postprocessing-complete]" in log_text,
            "full-model retrieval log lacks corrected-operator postprocessing confirmation")

    sample_values = list(numeric_rows(samples_path, skip_lines=1))
    full_species = {
        species: posterior_summary(samples_path, species)
        for species in ("N2O", "NH3")
    }
    return {
        "campaign": baseline["campaign"],
        "source_state_status": baseline.get("state_status"),
        "source_acceptance_before_audit": baseline.get("acceptance"),
        "source_historical_error_field": campaign_state.get("error"),
        "source_retry_preflight": campaign_state.get("retry_preflight"),
        "source_final_exit_code": campaign_state.get("exit_code"),
        "campaign_state_status": baseline_state.get("status"),
        "campaign_acceptance_before_audit": baseline_state.get("acceptance"),
        "campaign_historical_error_field": baseline_state.get("error"),
        "result": result_path.relative_to(root).as_posix(),
        "result_sha256": sha256(result_path),
        "stats": raw["-stats.dat"].relative_to(root).as_posix(),
        "stats_sha256": sha256(raw["-stats.dat"]),
        "lnz": lnz,
        "lnz_error": error,
        "chi2_red": parsed["chi2_red"],
        "dof": parsed["dof"],
        "chi2": float(parsed["chi2_red"]) * int(parsed["dof"]),
        "declared_parameters": parsed["n_params"],
        "effective_free_parameters": config["effective_free_dimension"],
        "posterior_rows": sample_rows,
        "posterior_sha256": sha256(samples_path),
        "posterior_finite": all(math.isfinite(value) for row in sample_values for value in row),
        "spectrum_rows": spectrum_rows,
        "spectrum_sha256": sha256(spectrum),
        "pt_rows": pt_rows,
        "pt_sha256": sha256(pt),
        "logx_rows": logx_rows,
        "logx_sha256": sha256(logx),
        "resume": resume,
        "multinest_shapes": raw_shapes,
        "operator_preflight_sha256": sha256(operator_path),
        "operator_callback_bound": True,
        "operator_closure_max_relative": operator["maximum_relative_truth_closure"],
        "configuration_sha256": sha256(config_path),
        "operator_product_hashes": {
            "posterior_equal_weights": sha256(raw["-post_equal_weights.dat"]),
            "resume": sha256(raw["-resume.dat"]),
            "evidence_samples": sha256(raw["-ev.dat"]),
            "live_points": sha256(raw["-live.points"]),
            "physical_live_points": sha256(raw["-phys_live.points"]),
        },
        "posterior_abundances": full_species,
    }


def validate_campaign(root: Path) -> dict[str, Any]:
    check_calibration()
    campaign = root / CAMPAIGN_REL
    state = read_json(campaign / "campaign_state.json")
    require(state.get("campaign_status") in {"COMPLETE_PENDING_VALIDATION", "COMPLETE_VALIDATED"},
            f"unexpected campaign status {state.get('campaign_status')!r}")
    require(state.get("active_run_ids") == [], "campaign ledger still lists active retrievals")
    require(state.get("checkpoint_reuse") is False, "campaign unexpectedly reused checkpoints")
    require(state.get("dataset_sha256") == DATASET_SHA256, "campaign-level dataset hash mismatch")
    require(len(state.get("runs", [])) == 2, "campaign must contain exactly two authorized runs")

    runner_path = root / "Thermal_Emission_Spectroscopy/scripts/run_life_retrieval_a3_100h_binning_corrected_loo.py"
    supervisor_path = root / "Thermal_Emission_Spectroscopy/scripts/launch_proxima_a3_100h_binning_corrected_loo.py"
    audit_path = Path(__file__).resolve()
    runner_hash = sha256(runner_path)
    supervisor_hash = sha256(supervisor_path)
    require(runner_hash == state["code_sha256"]["corrected_ablation_runner"],
            "corrected-bin runner source hash differs from the launch ledger")
    require(supervisor_hash == state["code_sha256"]["supervisor"],
            "campaign supervisor source hash differs from the launch ledger")

    data_path = root / "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A3_100h.dat"
    require(sha256(data_path) == DATASET_SHA256, "observed LIFE dataset SHA-256 mismatch")
    from validate_proxima_molecular_ablation_loo import validate_table as check_table
    data_rows, data_columns = check_table(data_path, skip_lines=1, expected_columns=4,
                                         min_rows=31, max_rows=31)
    baseline = validate_baseline(root, state, data_path)

    baseline_config = read_json(root / Path(*PurePosixPath(state["baseline_full"]["configuration"]).parts))
    with (campaign / "manifest.csv").open(newline="", encoding="utf-8") as handle:
        manifest = {row["run_id"]: row for row in csv.DictReader(handle)}
    require(set(manifest) == set(EXPECTED_RUNS), "manifest keys differ from the two authorized ablations")

    audit_runs = []
    for run in state["runs"]:
        run_id = run["run_id"]
        excluded = EXPECTED_RUNS.get(run_id)
        require(excluded is not None and run["excluded_species"] == excluded,
                f"unexpected run/species assignment: {run_id}")
        require(run.get("status") in {"complete_pending_validation", "validated"} and run.get("return_code") == 0,
                f"run did not complete cleanly: {run_id}")
        require(run.get("error") == "", f"run recorded an error: {run_id}: {run.get('error')}")
        require(run.get("preflight_status") == "PASS_MPI_OPERATOR_AND_MATCHED_PRIORS" and
                run.get("preflight_return_code") == 0 and run.get("preflight_parameters") == 14 and
                run.get("preflight_effective_free") == 13,
                f"preflight did not pass expected dimensions: {run_id}")
        require(run.get("mpi_ranks") == (8 if excluded == "NH3" else 7),
                f"rank count mismatch: {run_id}")
        row = manifest[run_id]
        require(row.get("status") in {"complete_pending_validation", "validated"} and row.get("return_code") == "0" and
                row.get("error") == "", f"manifest does not record clean completion: {run_id}")
        require(int(row["mpi_ranks"]) == int(run["mpi_ranks"]) and
                int(row["replacements"]) == int(run["replacements"]) and
                int(row["evaluations"]) == int(run["evaluations"]),
                f"manifest and campaign state counters disagree: {run_id}")
        require(int(run["mpi_ranks"]) <= 15 and int(run["replacements"]) > 0 and
                int(run["evaluations"]) > int(run["replacements"]),
                f"invalid MPI or MultiNest counters: {run_id}")

        config_path = root / Path(*PurePosixPath(run["configuration_json"]).parts)
        config = read_json(config_path)
        validate_config_pair(baseline_config, config, excluded)
        preflight_path = root / Path(*PurePosixPath(run["operator_preflight"]).parts)
        runtime_path = root / Path(*PurePosixPath(run["operator_runtime"]).parts)
        preflight = check_operator(preflight_path, run, DATASET_SHA256)
        runtime = check_operator(runtime_path, run, DATASET_SHA256)
        require(preflight.get("stage") == "setup_only", f"operator preflight stage mismatch: {run_id}")
        require(runtime.get("stage") == "sampling", f"operator runtime stage mismatch: {run_id}")

        normalized = dict(run)
        normalized.update(
            status="completed",
            preflight_status="pass",
            dataset_seed=int(state["dataset_seed"]),
            full_results=run["baseline_full_results"],
        )
        # Reuse the established audit for posterior/native MultiNest agreement,
        # finite output tables, fixed surface pressure, spectra, P-T and log-X.
        from validate_proxima_molecular_ablation_loo import validate_ablation
        products = validate_ablation(normalized, root, campaign)
        # The supervisor sampled this counter before the last post-processing
        # row was flushed. Preserve it as provenance and use the final matched
        # POSEIDON/MultiNest tables as the audited count.
        products["posterior_rows_ledger"] = int(run["posterior_rows"])
        products["posterior_rows_reconciled_delta"] = (
            products["posterior_samples"] - int(run["posterior_rows"])
        )
        require(products["resume"]["replacements"] == int(run["replacements"]) and
                products["resume"]["evaluations"] == int(run["evaluations"]),
                f"MultiNest resume counters differ from campaign ledger: {run_id}")

        result_path = root / Path(*PurePosixPath(run["archive_dir"]).parts) / "POSEIDON_output/proxima_b_earthlike/retrievals/results" / f"{run['model_name']}_results.txt"
        result_metrics = parse_evidence_from_result(result_path, expected_parameters=14)
        result_metrics["lnz_stats"], result_metrics["lnz_error_stats"] = parse_evidence_from_stats(
            root / Path(*PurePosixPath(run["archive_dir"]).parts) / "POSEIDON_output/proxima_b_earthlike/retrievals/MultiNest_raw" / f"{run['model_name']}-stats.dat"
        )
        require(products["dataset_sha256"] == DATASET_SHA256,
                f"ablation dataset hash mismatch: {run_id}")
        require(products["dataset_seed"] == int(state["dataset_seed"]),
                f"ablation dataset seed mismatch: {run_id}")

        retained = "N2O" if excluded == "NH3" else "NH3"
        p_summary = posterior_summary(
            root / Path(*PurePosixPath(run["archive_dir"]).parts) / "POSEIDON_output/proxima_b_earthlike/retrievals/samples" / f"{run['model_name']}_samples.txt",
            retained,
        )
        row_result = {
            **products,
            "model_name": run["model_name"],
            "mpi_ranks": run["mpi_ranks"],
            "replacements": products["resume"]["replacements"],
            "evaluations": products["resume"]["evaluations"],
            "lnz_loo": float(result_metrics["lnz_stats"]),
            "lnz_loo_error": float(result_metrics["lnz_error_stats"]),
            "chi2_red_loo": float(result_metrics["chi2_red"]),
            "dof_loo": int(result_metrics["dof"]),
            "chi2_loo": float(result_metrics["chi2_red"]) * int(result_metrics["dof"]),
            "posterior_abundance_retained": {retained: p_summary},
            "posterior_rows_final": products["posterior_samples"],
            "posterior_rows_controller": int(run["posterior_rows"]),
            "posterior_rows_controller_initial": int(
                run.get("posterior_rows_controller_initial", run["posterior_rows"])
            ),
            "configuration_sha256": sha256(config_path),
            "operator_preflight_sha256": sha256(preflight_path),
            "operator_runtime_sha256": sha256(runtime_path),
            "launch_log_sha256": sha256(root / Path(*PurePosixPath(run["launch_log"]).parts)),
        }
        retrieval = (root / Path(*PurePosixPath(run["archive_dir"]).parts) /
                     "POSEIDON_output/proxima_b_earthlike/retrievals")
        stem = f"proxima_{run['scenario']}_{run['hours']}h{run['output_tag']}"
        row_result["product_hashes"] = {
            "results": sha256(retrieval / "results" / f"{stem}_results.txt"),
            "posterior": sha256(retrieval / "samples" / f"{stem}_samples.txt"),
            "spectrum": sha256(retrieval / "samples" / f"{stem}_spectrum_retrieved.txt"),
            "pt": sha256(retrieval / "samples" / f"{stem}_PT_retrieved.txt"),
            "log_x": sha256(retrieval / "samples" / f"{stem}_log_X_retrieved.txt"),
            "multinest_stats": sha256(retrieval / "MultiNest_raw" / f"{stem}-stats.dat"),
            "multinest_equal_weights": sha256(retrieval / "MultiNest_raw" / f"{stem}-post_equal_weights.dat"),
            "multinest_resume": sha256(retrieval / "MultiNest_raw" / f"{stem}-resume.dat"),
            "multinest_evidence_samples": sha256(retrieval / "MultiNest_raw" / f"{stem}-ev.dat"),
        }
        delta = baseline["lnz"] - row_result["lnz_loo"]
        delta_error = math.hypot(baseline["lnz_error"], row_result["lnz_loo_error"])
        sigma, log_p = calibrated_sigma(delta)
        row_result.update(
            delta_lnb=delta,
            delta_lnb_numeric_error=delta_error,
            sigma_calibrated_auxiliary=sigma,
            log_p_calibration=log_p,
            ln_b_direction="favours including molecule" if delta > 0 else
                            "favours omission" if delta < 0 else "neutral at central estimate",
        )
        audit_runs.append(row_result)

    require(sum(int(run["mpi_ranks"]) for run in state["runs"]) == 15,
            "total rank allocation differs from the authorized 15")
    require(baseline["posterior_finite"], "full posterior contains non-finite values")
    return {
        "campaign_id": state["campaign_id"],
        "campaign_status_at_audit": state["campaign_status"],
        "campaign_acceptance_before_audit": state.get("pre_validation_snapshot", {}).get(
            "acceptance", state["acceptance"]
        ),
        "pre_validation_snapshot": state.get("pre_validation_snapshot", {}),
        "completed_utc": state["completed_utc"],
        "audit_status": "PASS",
        "dataset": {
            "path": "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A3_100h.dat",
            "sha256": sha256(data_path),
            "channels": data_rows,
            "columns": data_columns,
            "seed": state["dataset_seed"],
        },
        "settings": {
            "n_live": state["n_live"],
            "evidence_tolerance": state["evidence_tolerance"],
            "R": state["R"],
            "native_wavelength_range_um": state["native_wavelength_range_um"],
            "error_inflation": state["error_inflation"],
            "total_mpi_ranks": state["total_mpi_ranks"],
        },
        "baseline_full": baseline,
        "source_code_hashes": {
            "corrected_ablation_runner": {
                "path": runner_path.relative_to(root).as_posix(), "sha256": runner_hash
            },
            "supervisor": {
                "path": supervisor_path.relative_to(root).as_posix(), "sha256": supervisor_hash
            },
            "independent_audit": {
                "path": audit_path.relative_to(root).as_posix(), "sha256": sha256(audit_path)
            },
        },
        "ablations": sorted(audit_runs, key=lambda item: item["excluded_species"]),
        "interpretation_guardrails": [
            "lnB compares model evidence under the matched prior/configuration; it is not a probability of agriculture.",
            "Posterior P(log10 X > A0) is defined only for models that retain X.",
            "Calibrated sigma is auxiliary and is not a frequentist detection significance.",
            "Historical old-binning retrievals also used a different wavelength interval; they are not the matched comparator.",
        ],
    }


def write_csv(report: dict[str, Any], path: Path) -> None:
    fields = [
        "excluded_species", "model_name", "mpi_ranks", "replacements", "evaluations",
        "lnz_full", "lnz_full_error", "lnz_loo", "lnz_loo_error", "delta_lnb",
        "delta_lnb_numeric_error", "sigma_calibrated_auxiliary", "chi2_red_full",
        "dof_full", "chi2_full", "chi2_red_loo", "dof_loo", "chi2_loo",
        "posterior_rows_final", "posterior_rows_controller", "posterior_rows_controller_initial",
        "retained_species", "retained_species_q16", "retained_species_median",
        "retained_species_q84", "retained_species_probability_above_a0",
        "excluded_species_probability_above_a0",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for item in report["ablations"]:
            retained, summary = next(iter(item["posterior_abundance_retained"].items()))
            writer.writerow({
                "excluded_species": item["excluded_species"],
                "model_name": item["model_name"],
                "mpi_ranks": item["mpi_ranks"],
                "replacements": item["replacements"],
                "evaluations": item["evaluations"],
                "lnz_full": report["baseline_full"]["lnz"],
                "lnz_full_error": report["baseline_full"]["lnz_error"],
                "lnz_loo": item["lnz_loo"],
                "lnz_loo_error": item["lnz_loo_error"],
                "delta_lnb": item["delta_lnb"],
                "delta_lnb_numeric_error": item["delta_lnb_numeric_error"],
                "sigma_calibrated_auxiliary": "N/A" if item["sigma_calibrated_auxiliary"] is None else item["sigma_calibrated_auxiliary"],
                "chi2_red_full": report["baseline_full"]["chi2_red"],
                "dof_full": report["baseline_full"]["dof"],
                "chi2_full": report["baseline_full"]["chi2"],
                "chi2_red_loo": item["chi2_red_loo"],
                "dof_loo": item["dof_loo"],
                "chi2_loo": item["chi2_loo"],
                "posterior_rows_final": item["posterior_rows_final"],
                "posterior_rows_controller": item["posterior_rows_controller"],
                "posterior_rows_controller_initial": item["posterior_rows_controller_initial"],
                "retained_species": retained,
                "retained_species_q16": summary["q16"],
                "retained_species_median": summary["median"],
                "retained_species_q84": summary["q84"],
                "retained_species_probability_above_a0": summary["probability_above_a0"],
                "excluded_species_probability_above_a0": "N/A by construction",
            })


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.repo.resolve()
    validator.repo_path = repo_path
    campaign = root / CAMPAIGN_REL
    errors: list[str] = []
    try:
        report = validate_campaign(root)
    except Exception as exc:
        report = {"audit_status": "FAIL", "errors": [f"{type(exc).__name__}: {exc}"]}
        errors.extend(report["errors"])
    report_path = campaign / "validation_report_20261020.json"
    csv_path = campaign / "loo_results_validated_20261020.csv"
    report["audit_errors"] = errors
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if errors:
        print(f"AUDIT FAILED: {report_path}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    write_csv(report, csv_path)
    print(f"AUDIT PASS: {report_path}")
    print(f"CSV: {csv_path}")
    print("Matched contrasts:")
    for item in report["ablations"]:
        sigma = item["sigma_calibrated_auxiliary"]
        sigma_text = "N/A" if sigma is None else f"{sigma:.3f}"
        print(
            f"  no-{item['excluded_species']}: lnZ={item['lnz_loo']:.9f} +/- {item['lnz_loo_error']:.9f}; "
            f"delta lnB={item['delta_lnb']:.9f} +/- {item['delta_lnb_numeric_error']:.9f}; "
            f"sigma(aux)={sigma_text}; chi2red={item['chi2_red_loo']:.2f}; "
            f"P(retained {next(iter(item['posterior_abundance_retained']))}>A0)="
            f"{next(iter(item['posterior_abundance_retained'].values()))['probability_above_a0']:.6f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
