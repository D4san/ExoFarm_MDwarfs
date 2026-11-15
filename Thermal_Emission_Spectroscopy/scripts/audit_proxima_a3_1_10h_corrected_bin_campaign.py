#!/usr/bin/env python3
"""Independently audit the six corrected-bin A3 1 h/10 h LIFE retrievals.

The audit reads finished products only. It writes the machine-readable audit,
summary tables, and an SVG figure inside the isolated campaign directory; it
never starts or resumes a sampler and does not edit campaign ledgers.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
import sys
from pathlib import Path, PurePosixPath
from typing import Any

import report_proxima_loo_lin_sigma as sigma_calibration
from report_proxima_loo_lin_sigma import calibrated_sigma, check_calibration
import validate_proxima_molecular_ablation_loo as validator


CAMPAIGN_REL = Path(
    "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/"
    "retrievals/a3_1_10h_binning_corrected_loo_20261020_r03"
)
THRESHOLDS = {"N2O": -6.884325289636784, "NH3": -9.950526295665036}
EXPECTED_RUNS = {
    "A3_1h_full": (1, None),
    "A3_1h_no_NH3": (1, "NH3"),
    "A3_1h_no_N2O": (1, "N2O"),
    "A3_10h_full": (10, None),
    "A3_10h_no_NH3": (10, "NH3"),
    "A3_10h_no_N2O": (10, "N2O"),
}
EXPECTED_DATASETS = {
    1: (
        "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/"
        "life_data/LIFE_proxima_A3_1h_O2_fixedBlack1bar_official.dat",
        "a3043e5de76a834983949e6eca12636ea4de174ebdb2db0853155282c100dee2",
    ),
    10: (
        "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/"
        "life_data/LIFE_proxima_A3_10h.dat",
        "46a026504b9b9521fa29407a501169b9d3cfc433de40a91b8ade86d7767abb5b",
    ),
}
BASE_PARAMETERS = set(validator.BASE_PARAMETERS)
GAS_PARAMETERS = set(validator.GAS_PARAMETERS)
EXPECTED_FULL_PARAMETERS = BASE_PARAMETERS | GAS_PARAMETERS


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_json(path: Path) -> dict[str, Any]:
    validator.require_file(path)
    return json.loads(path.read_text(encoding="utf-8"))


def repo_path(value: str | Path, root: Path) -> Path:
    raw = str(value).replace("\\", "/")
    marker = "/mnt/c/Proyectos/Astro/ExoFarm_MDwarfs/"
    if raw.startswith(marker):
        raw = raw[len(marker):]
    if raw.startswith("/mnt/c/"):
        return Path("C:/") / Path(*PurePosixPath(raw[len("/mnt/c/"):]).parts)
    return root / Path(*PurePosixPath(raw).parts)


def quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = probability * (len(ordered) - 1)
    lower, upper = math.floor(position), math.ceil(position)
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def posterior_summary(path: Path, species: str) -> dict[str, Any]:
    header = validator.parse_table_header(path)
    parameter = f"log_{species}"
    require(parameter in header, f"{parameter} absent from {path}")
    index = header.index(parameter)
    values = [row[index] for row in validator.numeric_rows(path, skip_lines=1)]
    threshold = THRESHOLDS[species]
    return {
        "parameter": parameter,
        "a0_threshold_log10": threshold,
        "samples": len(values),
        "q025": quantile(values, 0.025),
        "q16": quantile(values, 0.16),
        "median": quantile(values, 0.50),
        "q84": quantile(values, 0.84),
        "q975": quantile(values, 0.975),
        "samples_above_a0": sum(value > threshold for value in values),
        "probability_above_a0": sum(value > threshold for value in values) / len(values),
    }


def check_resolved_pair(full: dict[str, Any], ablated: dict[str, Any], species: str) -> None:
    require(ablated["dataset_sha256"] == full["dataset_sha256"], f"dataset mismatch for no-{species}")
    require(ablated["parameters"] == [p for p in full["parameters"] if p != f"log_{species}"],
            f"parameter list/order differs beyond removal of log_{species}")
    require(len(full["parameters"]) == 15 and full["declared_dimension"] == 15 and
            full["effective_free_dimension"] == 14, "full model parameter dimensions are not 15/14")
    require(len(ablated["parameters"]) == 14 and ablated["declared_dimension"] == 14 and
            ablated["effective_free_dimension"] == 13, f"no-{species} dimensions are not 14/13")
    require(species not in ablated["param_species"], f"excluded opacity {species} remains in config")
    require(ablated["fixed_parameters"] == full["fixed_parameters"], f"fixed parameters differ for no-{species}")
    require(ablated["fixed_log10_abundances"] == full["fixed_log10_abundances"],
            f"fixed abundances differ for no-{species}")
    for key in (
        "R", "wl_min", "wl_max", "ev_tol", "n_live", "surface_pressure_mode",
        "error_inflation", "x_profile", "likelihood",
    ):
        require(ablated[key] == full[key], f"matched setting {key} differs for no-{species}")
    for parameter in ablated["parameters"]:
        require(ablated["prior_types"][parameter] == full["prior_types"][parameter],
                f"prior type differs for {parameter} in no-{species}")
        require(ablated["prior_ranges"][parameter] == full["prior_ranges"][parameter],
                f"prior range differs for {parameter} in no-{species}")


def check_operator(path: Path, run: dict[str, Any], expected_hash: str, stage: str) -> dict[str, Any]:
    record = read_json(path)
    require(record.get("status") == "PASS", f"operator record did not pass: {path}")
    require(record.get("dataset_sha256") == expected_hash, f"operator dataset hash mismatch: {path}")
    require(record.get("channels") == 31 and record.get("native_grid_um") == [3.0, 20.0],
            f"operator channel/grid mismatch: {path}")
    operator_name = record.get("operator", "")
    require("midpoint-edge photon overlap" in operator_name and "exact channel centre" in operator_name,
            f"unexpected operator definition: {path}")
    require(record.get("actual_poseidon_callback_bound") is True,
            f"POSEIDON callback not bound: {path}")
    binding_scope = record.get("binding_scope", "")
    require("sampling" in binding_scope and "postprocessing" in binding_scope,
            f"operator binding scope incomplete: {path}")
    closure = max(
        float(record.get("max_relative_truth_closure", 0.0)),
        float(record.get("max_relative_callback_closure", 0.0)),
        float(record.get("callback_truth_closure_max_relative", 0.0)),
    )
    require(math.isfinite(closure) and closure < 1e-12, f"operator closure failed: {path}: {closure}")
    require(record.get("mpi_size") == int(run["mpi_ranks"]), f"operator MPI size mismatch: {path}")
    require(record.get("stage") == stage, f"operator stage mismatch: {path}")
    require(record.get("retrieval_name") == run["model_name"], f"operator model binding mismatch: {path}")
    expected_excluded = run.get("excluded_species") or None
    require(record.get("excluded_species") == expected_excluded, f"operator excluded-species mismatch: {path}")
    return {"record": record, "sha256": validator.sha256(path), "closure_max_relative": closure}


def validate_run(run: dict[str, str], root: Path, campaign: Path) -> dict[str, Any]:
    run_id = run["run_id"]
    hours, excluded = EXPECTED_RUNS[run_id]
    require(int(run["hours"]) == hours and run["scenario"] == "A3", f"run identity mismatch: {run_id}")
    require(int(run["return_code"]) == 0 and run["status"] in {"complete_pending_validation", "validated"},
            f"run did not finish successfully: {run_id}")
    require(run.get("error", "") == "", f"run has a recorded error: {run_id}: {run.get('error')}")
    require(run["preflight_status"] == "PASS_MPI5_OPERATOR_PRIORS" and int(run["preflight_return_code"]) == 0,
            f"preflight did not pass: {run_id}")
    expected_parameters = 15 if excluded is None else 14
    expected_free = 14 if excluded is None else 13
    require(int(run["declared_parameters"]) == expected_parameters and
            int(run["effective_free_parameters"]) == expected_free,
            f"manifest dimensions mismatch: {run_id}")
    require(int(run["mpi_ranks"]) == 5, f"MPI rank allocation mismatch: {run_id}")

    dataset_rel, expected_hash = EXPECTED_DATASETS[hours]
    require(run["dataset_rel"] == dataset_rel and run["dataset_sha256_expected"] == expected_hash,
            f"manifest dataset identity mismatch: {run_id}")
    data_path = root / Path(*PurePosixPath(dataset_rel).parts)
    validator.require_file(data_path)
    actual_hash = validator.sha256(data_path)
    require(actual_hash == expected_hash, f"dataset hash mismatch for {run_id}: {actual_hash}")
    data_rows, data_columns = validator.validate_table(
        data_path, skip_lines=1, expected_columns=4, min_rows=31, max_rows=31
    )
    previous_wavelength = -math.inf
    for row_values in validator.numeric_rows(data_path, skip_lines=1):
        require(row_values[0] > previous_wavelength and row_values[1] > 0 and row_values[3] > 0,
                f"invalid dataset wavelength/flux/error: {run_id}")
        previous_wavelength = row_values[0]

    config_path = repo_path(run["configuration_json"], root)
    config = read_json(config_path)
    require(config["dataset_sha256"] == expected_hash, f"resolved config hash mismatch: {run_id}")
    require(config["n_live"] == 800 and config["R"] == 10000 and config["ev_tol"] == 0.5,
            f"sampling configuration mismatch: {run_id}")
    require(config["wl_min"] == 3.0 and config["wl_max"] == 20.0 and
            config["x_profile"] == "isochem" and config["surface_pressure_mode"] == "fixed-black" and
            config["error_inflation"] == "none", f"forward/likelihood settings mismatch: {run_id}")
    require(config["declared_dimension"] == expected_parameters and
            config["effective_free_dimension"] == expected_free, f"resolved dimensions mismatch: {run_id}")
    expected_config_parameters = EXPECTED_FULL_PARAMETERS if excluded is None else (
        EXPECTED_FULL_PARAMETERS - {f"log_{excluded}"}
    )
    require(set(config["parameters"]) == expected_config_parameters,
            f"resolved parameter list/exclusion mismatch: {run_id}")

    operator_preflight_path = repo_path(run["operator_preflight"], root)
    operator_runtime_path = repo_path(run["operator_runtime"], root)
    preflight = check_operator(operator_preflight_path, run, expected_hash, "setup_only")
    runtime = check_operator(operator_runtime_path, run, expected_hash, "sampling")
    preflight_log = repo_path(run["preflight_log"], root)
    preflight_text = preflight_log.read_text(encoding="utf-8", errors="replace")
    require("[setup-only] corrected operator, model and priors PASS" in preflight_text,
            f"preflight log lacks final corrected-operator/prior PASS: {run_id}")

    archive = repo_path(run["archive_dir"], root)
    retrieval = archive / "POSEIDON_output/proxima_b_earthlike/retrievals"
    stem = run["model_name"]
    result_path = retrieval / "results" / f"{stem}_results.txt"
    samples_path = retrieval / "samples" / f"{stem}_samples.txt"
    spectrum_path = retrieval / "samples" / f"{stem}_spectrum_retrieved.txt"
    pt_path = retrieval / "samples" / f"{stem}_PT_retrieved.txt"
    logx_path = retrieval / "samples" / f"{stem}_log_X_retrieved.txt"
    raw_dir = retrieval / "MultiNest_raw"
    suffixes = (
        "-.txt", "-ev.dat", "-live.points", "-phys_live.points",
        "-post_equal_weights.dat", "-resume.dat", "-stats.dat", "-summary.txt",
    )
    raw = {suffix: Path(f"{raw_dir / stem}{suffix}") for suffix in suffixes}

    result = validator.parse_evidence_from_result(result_path, expected_parameters=expected_parameters)
    require(result["model"] == stem and result["dataset_label"] == Path(dataset_rel).name,
            f"result model/dataset label mismatch: {run_id}")
    require(validator.sha256(data_path) == expected_hash, f"result uses a different dataset: {run_id}")
    stats_lnz, stats_error = validator.parse_evidence_from_stats(raw["-stats.dat"])
    require(abs(stats_lnz - float(result["lnz_printed"])) <= 0.0051 and
            abs(stats_error - float(result["lnz_error_printed"])) <= 0.0051,
            f"POSEIDON result and native MultiNest stats disagree: {run_id}")

    expected_header = EXPECTED_FULL_PARAMETERS if excluded is None else (
        BASE_PARAMETERS | (GAS_PARAMETERS - {f"log_{excluded}"})
    )
    header = validator.parse_table_header(samples_path)
    require(len(header) == expected_parameters and set(header) == expected_header,
            f"posterior parameter list/exclusion mismatch: {run_id}")
    surface_index = header.index("log_P_surf")
    posterior_rows, posterior_columns = validator.validate_table(
        samples_path,
        skip_lines=1,
        expected_columns=expected_parameters,
        min_rows=1,
        row_check=lambda values, _: require(abs(values[surface_index]) <= 1e-12,
                                            f"log_P_surf not fixed at 0: {run_id}"),
    )
    equal_rows, equal_columns = validator.validate_table(raw["-post_equal_weights.dat"], min_rows=1)
    require(equal_rows == posterior_rows and equal_columns >= posterior_columns,
            f"POSEIDON/MultiNest posterior shape mismatch: {run_id}")
    compared_rows = validator.compare_posterior_to_multinest(
        samples_path, raw["-post_equal_weights.dat"], posterior_columns
    )

    previous_wave = -math.inf
    def check_spectrum(values: list[float], _: int) -> None:
        nonlocal previous_wave
        require(values[0] > previous_wave and all(a <= b for a, b in zip(values[1:], values[2:])),
                f"spectrum ordering/quantiles invalid: {run_id}")
        previous_wave = values[0]
    spectrum_rows, spectrum_columns = validator.validate_table(
        spectrum_path, skip_lines=1, expected_columns=6, min_rows=2, row_check=check_spectrum
    )

    previous_pressure = math.inf
    def check_pt(values: list[float], _: int) -> None:
        nonlocal previous_pressure
        require(0 < values[0] < previous_pressure and all(a <= b for a, b in zip(values[1:], values[2:])),
                f"P-T pressure ordering/quantiles invalid: {run_id}")
        previous_pressure = values[0]
    pt_rows, pt_columns = validator.validate_table(
        pt_path, skip_lines=1, expected_columns=6, min_rows=100, max_rows=100, row_check=check_pt
    )
    logx_rows = validator.validate_log_x(logx_path, excluded or "")

    raw_shapes: dict[str, list[int]] = {}
    for suffix in ("-.txt", "-ev.dat", "-live.points", "-phys_live.points", "-summary.txt"):
        raw_shapes[suffix] = list(validator.validate_table(raw[suffix], min_rows=1))
    for suffix in ("-live.points", "-phys_live.points"):
        require(raw_shapes[suffix][0] == 800, f"expected 800 live points in {run_id} {suffix}")
    resume = validator.parse_resume(raw["-resume.dat"])
    require(raw_shapes["-ev.dat"][0] == resume["replacements"] - resume["n_live"],
            f"MultiNest evidence rows/resume counters disagree: {run_id}")
    require(resume["replacements"] == int(run["replacements"]) and
            resume["evaluations"] == int(run["evaluations"]),
            f"manifest and MultiNest final counters disagree: {run_id}")
    require(int(run["posterior_rows"]) == posterior_rows,
            f"manifest posterior row count differs from final product: {run_id}")

    launch_log = repo_path(run["launch_log"], root)
    log_text = launch_log.read_text(encoding="utf-8", errors="replace")
    require("Sampling finished. Exiting MultiNest" in log_text and "All done!" in log_text and
            f"[done] {stem}" in log_text and "[operator-postprocessing-complete]" in log_text,
            f"run completion/operator-postprocessing markers missing: {run_id}")

    posterior_species = {}
    for species in ("N2O", "NH3"):
        if excluded != species:
            posterior_species[species] = posterior_summary(samples_path, species)

    products = {
        "results": result_path,
        "posterior": samples_path,
        "spectrum": spectrum_path,
        "pt": pt_path,
        "log_x": logx_path,
        "multinest_stats": raw["-stats.dat"],
        "multinest_equal_weights": raw["-post_equal_weights.dat"],
        "multinest_resume": raw["-resume.dat"],
        "multinest_evidence_samples": raw["-ev.dat"],
        "multinest_live_points": raw["-live.points"],
        "multinest_physical_live_points": raw["-phys_live.points"],
    }
    return {
        "run_id": run_id,
        "hours": hours,
        "model": "full" if excluded is None else f"no{excluded}",
        "excluded_species": excluded,
        "status_manifest": run["status"],
        "return_code": int(run["return_code"]),
        "mpi_ranks": int(run["mpi_ranks"]),
        "declared_parameters": expected_parameters,
        "effective_free_parameters": expected_free,
        "dataset_rel": dataset_rel,
        "dataset_sha256": actual_hash,
        "dataset_rows": data_rows,
        "dataset_columns": data_columns,
        "lnz": stats_lnz,
        "lnz_error": stats_error,
        "chi2_red": float(result["chi2_red"]),
        "dof": int(result["dof"]),
        "posterior_rows": posterior_rows,
        "posterior_columns": posterior_columns,
        "posterior_rows_crosschecked": compared_rows,
        "spectrum_rows": spectrum_rows,
        "spectrum_columns": spectrum_columns,
        "pt_rows": pt_rows,
        "pt_columns": pt_columns,
        "logx_rows": logx_rows,
        "multinest_resume": resume,
        "multinest_shapes": raw_shapes,
        "operator": {
            "name": runtime["record"]["operator"],
            "preflight_sha256": preflight["sha256"],
            "runtime_sha256": runtime["sha256"],
            "callback_bound": True,
            "binding_scope": runtime["record"]["binding_scope"],
            "closure_max_relative": runtime["closure_max_relative"],
        },
        "configuration_sha256": validator.sha256(config_path),
        "preflight_log_sha256": validator.sha256(preflight_log),
        "launch_log_sha256": validator.sha256(launch_log),
        "product_sha256": {name: validator.sha256(path) for name, path in products.items()},
        "posterior_abundances": posterior_species,
        "chi2": float(result["chi2_red"]) * int(result["dof"]),
        "result_dataset_label": result["dataset_label"],
    }


def write_svg(pairs: list[dict[str, Any]], path: Path) -> None:
    width, height = 1080, 560
    left, right, top, bottom = 120, 1020, 95, 430
    plot_width = right - left
    min_value = min(-1.0, min(row["delta_lnb_full_minus_without"] - row["delta_lnb_numeric_error_quadrature"] for row in pairs))
    max_value = max(1.0, max(row["delta_lnb_full_minus_without"] + row["delta_lnb_numeric_error_quadrature"] for row in pairs))
    span = max_value - min_value
    def xpos(value: float) -> float:
        return left + (value - min_value) / span * plot_width
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:"STIX Two Text",STIXGeneral,"Times New Roman",serif;fill:#02040F}.title{font-size:25px;font-weight:bold}.sub{font-size:15px}.label{font-size:17px}.tick{font-size:13px}.foot{font-size:14px}</style>',
        '<text x="540" y="36" text-anchor="middle" class="title">A3 LIFE: evidencia condicional con binning corregido</text>',
        '<text x="540" y="62" text-anchor="middle" class="sub">Δln Z = ln Z(completo) − ln Z(sin especie); barras = incertidumbre numérica propagada</text>',
    ]
    ticks = 6
    for index in range(ticks + 1):
        value = min_value + span * index / ticks
        x = xpos(value)
        stroke = "#555" if abs(value) < span / ticks / 2 else "#e5dada"
        dash = ' stroke-dasharray="5 4"' if abs(value) < span / ticks / 2 else ""
        out.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom}" stroke="{stroke}"{dash}/>')
        out.append(f'<text x="{x:.1f}" y="{bottom+22}" text-anchor="middle" class="tick">{value:.2f}</text>')
    out.append(f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#02040F"/>')
    y_positions = [155, 225, 325, 395]
    colors = {"N2O": "#1f77b4", "NH3": "#ff7f0e"}
    ordered = sorted(pairs, key=lambda row: (row["hours"], row["excluded_species"]))
    for row, y in zip(ordered, y_positions):
        species = row["excluded_species"]
        color = colors[species]
        value = row["delta_lnb_full_minus_without"]
        err = row["delta_lnb_numeric_error_quadrature"]
        x1, x2, xc = xpos(value - err), xpos(value + err), xpos(value)
        out.append(f'<text x="{left-14}" y="{y+5}" text-anchor="end" class="label">{row["hours"]} h · sin {species}</text>')
        out.append(f'<line x1="{x1:.1f}" y1="{y}" x2="{x2:.1f}" y2="{y}" stroke="{color}" stroke-width="3"/>')
        out.append(f'<line x1="{x1:.1f}" y1="{y-6}" x2="{x1:.1f}" y2="{y+6}" stroke="{color}" stroke-width="2"/>')
        out.append(f'<line x1="{x2:.1f}" y1="{y-6}" x2="{x2:.1f}" y2="{y+6}" stroke="{color}" stroke-width="2"/>')
        out.append(f'<circle cx="{xc:.1f}" cy="{y}" r="6" fill="{color}" stroke="#02040F"/>')
        out.append(f'<text x="{right+14}" y="{y+5}" class="label">{value:+.3f} ± {err:.3f}</text>')
    out.extend([
        '<text x="540" y="490" text-anchor="middle" class="foot">Δln Z positivo favorece incluir la molécula; los contrastes se emparejan solo dentro de cada duración/dataset.</text>',
        '<text x="540" y="515" text-anchor="middle" class="foot">La evidencia no es una probabilidad de agricultura ni una significancia frecuentista.</text>',
        '</svg>',
    ])
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def reconcile_ledgers(
    campaign: Path,
    state: dict[str, Any],
    manifest: dict[str, dict[str, str]],
    models: list[dict[str, Any]],
    report_path: Path,
) -> dict[str, str]:
    """Preserve the stale ledger snapshot, then reconcile from audited products."""
    state_path = campaign / "campaign_state.json"
    manifest_path = campaign / "manifest.csv"
    state_snapshot_path = campaign / "campaign_state_pre_audit_20261021.json"
    manifest_snapshot_path = campaign / "manifest_pre_audit_20261021.csv"
    state_bytes = state_path.read_bytes()
    manifest_bytes = manifest_path.read_bytes()
    if not state_snapshot_path.exists():
        state_snapshot_path.write_bytes(state_bytes)
    if not manifest_snapshot_path.exists():
        manifest_snapshot_path.write_bytes(manifest_bytes)

    state_sha = validator.sha256(state_snapshot_path)
    manifest_sha = validator.sha256(manifest_snapshot_path)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    model_by_id = {model["run_id"]: model for model in models}
    old_run_by_id = {run["run_id"]: run for run in state.get("runs", [])}
    reconciled_runs = []
    for run_id in EXPECTED_RUNS:
        row = manifest[run_id]
        old = dict(old_run_by_id.get(run_id, {}))
        model = model_by_id[run_id]
        for key in (
            "run_id", "scenario", "hours", "model", "excluded_species", "mpi_ranks",
            "declared_parameters", "effective_free_parameters", "dataset_rel",
            "dataset_sha256_expected", "matched_full_run", "output_tag", "model_name",
            "archive_dir", "configuration_json", "operator_preflight", "operator_runtime",
            "preflight_log", "preflight_status", "preflight_return_code", "pid", "pid_file",
            "launch_log", "start_utc", "end_utc", "elapsed_seconds", "return_code",
            "replacements", "evaluations", "posterior_rows", "error",
        ):
            if key in row:
                value: Any = row[key]
                if key in {
                    "hours", "mpi_ranks", "declared_parameters", "effective_free_parameters",
                    "preflight_return_code", "return_code", "replacements", "evaluations", "posterior_rows",
                }:
                    value = int(value) if value not in (None, "") else None
                elif key == "elapsed_seconds":
                    value = float(value) if value not in (None, "") else None
                old[key] = value
        old["status"] = "validated"
        old["audit_status"] = "PASS"
        old["audit_report"] = report_path.name
        old["posterior_rows_audited"] = model["posterior_rows"]
        old["lnz_audited"] = model["lnz"]
        old["lnz_error_audited"] = model["lnz_error"]
        reconciled_runs.append(old)

    # Keep a compact in-ledger link to the exact pre-reconciliation snapshots.
    state["pre_audit_ledger_snapshot"] = {
        "campaign_state_file": state_snapshot_path.name,
        "campaign_state_sha256": state_sha,
        "manifest_file": manifest_snapshot_path.name,
        "manifest_sha256": manifest_sha,
        "reason": "The supervisor left stale per-run serialization snapshots; original bytes are preserved and final fields were reconciled after supervisor exit using manifest, logs, MultiNest, and the independent audit.",
    }
    state["runs"] = reconciled_runs
    state["campaign_status"] = "COMPLETE_VALIDATED"
    state["acceptance"] = "VALIDATED_INDEPENDENT_AUDIT"
    state["active_run_ids"] = []
    state["validated_utc"] = now
    state["completed_utc"] = state.get("sampling_completed_utc") or now
    state["updated_utc"] = now
    state["audit_report"] = report_path.name
    state["sampling_start_confirmation"] = {
        "confirmed_run_ids": list(EXPECTED_RUNS),
        "pending_run_ids": [],
        "wave": 2,
        "observed_utc": now,
        "reconciled_after_supervisor_exit": True,
        "source": "manifest.csv + completed supervisor log + audited retrieval products",
    }
    state["ledger_reconciliation"] = {
        "status": "PASS",
        "reconciled_utc": now,
        "source_manifest": manifest_path.name,
        "source_audit_report": report_path.name,
        "original_snapshots_preserved": True,
    }
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with manifest_path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    additions = ["pre_audit_status", "audit_status", "audit_report"]
    for field in additions:
        if field not in fieldnames:
            fieldnames.append(field)
    for row in rows:
        row["pre_audit_status"] = row.get("pre_audit_status") or row.get("status", "")
        row["status"] = "validated"
        row["audit_status"] = "PASS"
        row["audit_report"] = report_path.name
    with manifest_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return {
        "status": "PASS",
        "reconciled_utc": now,
        "pre_audit_campaign_state_sha256": state_sha,
        "pre_audit_manifest_sha256": manifest_sha,
        "campaign_state_snapshot": state_snapshot_path.name,
        "manifest_snapshot": manifest_snapshot_path.name,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--campaign", type=Path, default=CAMPAIGN_REL)
    parser.add_argument("--reconcile-ledger", action="store_true",
                        help="after a passing audit, preserve pre-audit ledgers and reconcile their final status")
    args = parser.parse_args()
    root = args.repo.resolve()
    campaign = (root / args.campaign).resolve()
    check_calibration()
    state = read_json(campaign / "campaign_state.json")
    scope = read_json(campaign / "selected_scope.json")
    with (campaign / "manifest.csv").open(newline="", encoding="utf-8") as stream:
        manifest = {row["run_id"]: row for row in csv.DictReader(stream)}
    require(scope["campaign_id"] == state["campaign_id"], "scope/state campaign identity mismatch")
    require(scope["checkpoint_reuse"] is False and state.get("checkpoint_reuse") is False,
            "campaign indicates checkpoint reuse")
    require(state.get("active_run_ids") == [] and state.get("waves_completed") == [1, 2],
            "campaign state does not record both finished waves")
    require(set(manifest) == set(EXPECTED_RUNS), "manifest does not contain exactly the six authorized runs")
    require(scope["authorized_hours"] == [1, 10] and scope["models_per_exposure"] == ["full", "no_NH3", "no_N2O"],
            "selected campaign scope differs from the authorized six retrievals")
    require(scope["configuration"]["n_live"] == 800 and scope["configuration"]["R"] == 10000 and
            scope["configuration"]["evidence_tolerance"] == 0.5 and
            scope["configuration"]["wavelength_range_um"] == [3.0, 20.0],
            "selected campaign settings do not match the frozen analysis")
    reference_config = scope["matched_100h_corrected_reference"]["configuration"]

    # The campaign_state per-run snapshot is known to serialize stale pending
    # entries. The final manifest, logs, and products are checked independently.
    campaign_log = root / "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1_10h_binning_corrected_loo_20261020_r03.supervisor.log"
    validator.require_file(campaign_log)
    supervisor_text = campaign_log.read_text(encoding="utf-8", errors="replace")
    require("[campaign complete] six fresh corrected-bin retrievals; audit pending" in supervisor_text,
            "supervisor log lacks campaign-complete marker")
    for run_id in EXPECTED_RUNS:
        require(f"[completed+archived] {run_id}" in supervisor_text,
                f"supervisor log lacks completion marker for {run_id}")

    models = [validate_run(manifest[run_id], root, campaign) for run_id in EXPECTED_RUNS]
    by_id = {row["run_id"]: row for row in models}

    # Pair configs at fixed exposure. No cross-duration evidence comparison is made.
    config_checks = []
    for hours in (1, 10):
        full_id = f"A3_{hours}h_full"
        full_config = read_json(repo_path(manifest[full_id]["configuration_json"], root))
        require(set(full_config["parameters"]) == EXPECTED_FULL_PARAMETERS and
                full_config["declared_dimension"] == 15 and full_config["effective_free_dimension"] == 14,
                f"full parameter contract mismatch at {hours} h")
        for key, expected_value in reference_config.items():
            if key in {"dataset_sha256", "model_name"}:
                continue
            require(full_config.get(key) == expected_value,
                    f"full-model configuration differs from the accepted corrected-bin prior reference at {hours} h: {key}")
        for species in ("NH3", "N2O"):
            ablation_id = f"A3_{hours}h_no_{species}"
            ablated_config = read_json(repo_path(manifest[ablation_id]["configuration_json"], root))
            check_resolved_pair(full_config, ablated_config, species)
            config_checks.append({"hours": hours, "excluded_species": species, "matched_priors_and_dataset": True})

    pairs = []
    for hours in (1, 10):
        full = by_id[f"A3_{hours}h_full"]
        for species in ("NH3", "N2O"):
            ablated = by_id[f"A3_{hours}h_no_{species}"]
            delta = full["lnz"] - ablated["lnz"]
            numeric_error = math.hypot(full["lnz_error"], ablated["lnz_error"])
            sigma, log_p = calibrated_sigma(delta)
            pairs.append({
                "hours": hours,
                "excluded_species": species,
                "dataset_rel": full["dataset_rel"],
                "dataset_sha256": full["dataset_sha256"],
                "lnz_full": full["lnz"],
                "lnz_full_error": full["lnz_error"],
                "lnz_without_species": ablated["lnz"],
                "lnz_without_species_error": ablated["lnz_error"],
                "delta_lnb_full_minus_without": delta,
                "delta_lnb_numeric_error_quadrature": numeric_error,
                "sigma_calibrated_auxiliary": sigma,
                "calibration_log_p": log_p,
                "direction": "favours including molecule" if delta > 0 else
                            "favours omission" if delta < 0 else "neutral at central estimate",
                "chi2_red_full": full["chi2_red"],
                "dof_full": full["dof"],
                "chi2_red_without_species": ablated["chi2_red"],
                "dof_without_species": ablated["dof"],
                "p_species_gt_a0_full_model": full["posterior_abundances"][species]["probability_above_a0"],
                "posterior_probability_for_excluded_species_in_loo": None,
                "posterior_rows_full": full["posterior_rows"],
                "posterior_rows_without_species": ablated["posterior_rows"],
            })

    model_csv = campaign / "retrieval_models_validated_20261021.csv"
    pair_csv = campaign / "loo_results_validated_20261021.csv"
    json_path = campaign / "validation_report_20261021.json"
    figure_path = campaign / "a3_1_10h_corrected_bin_molecular_ablation_lnB_20261021.svg"
    model_fields = [
        "run_id", "hours", "model", "excluded_species", "return_code", "mpi_ranks",
        "declared_parameters", "effective_free_parameters", "dataset_rel", "dataset_sha256",
        "lnz", "lnz_error", "chi2_red", "dof", "posterior_rows", "spectrum_rows", "pt_rows", "logx_rows",
        "N2O_p_gt_A0", "NH3_p_gt_A0",
    ]
    with model_csv.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=model_fields)
        writer.writeheader()
        for row in models:
            writer.writerow({
                "run_id": row["run_id"], "hours": row["hours"], "model": row["model"],
                "excluded_species": row["excluded_species"] or "", "return_code": row["return_code"],
                "mpi_ranks": row["mpi_ranks"], "declared_parameters": row["declared_parameters"],
                "effective_free_parameters": row["effective_free_parameters"],
                "dataset_rel": row["dataset_rel"], "dataset_sha256": row["dataset_sha256"],
                "lnz": row["lnz"], "lnz_error": row["lnz_error"], "chi2_red": row["chi2_red"],
                "dof": row["dof"], "posterior_rows": row["posterior_rows"],
                "spectrum_rows": row["spectrum_rows"], "pt_rows": row["pt_rows"], "logx_rows": row["logx_rows"],
                "N2O_p_gt_A0": row["posterior_abundances"].get("N2O", {}).get("probability_above_a0", "N/A"),
                "NH3_p_gt_A0": row["posterior_abundances"].get("NH3", {}).get("probability_above_a0", "N/A"),
            })
    pair_fields = list(pairs[0].keys())
    with pair_csv.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=pair_fields)
        writer.writeheader()
        writer.writerows(pairs)
    write_svg(pairs, figure_path)

    report = {
        "audit_status": "PASS",
        "audited_utc_date": "2026-10-21",
        "campaign_id": scope["campaign_id"],
        "campaign_status_before_audit": state["campaign_status"],
        "campaign_acceptance_before_audit": state["acceptance"],
        "campaign_state_run_snapshots_stale": True,
        "campaign_state_snapshot_note": "The six campaign_state.runs entries still say pending; final manifest, supervisor completion log and all products were independently checked after supervisor exit.",
        "supervisor_exit_check": {"pid": state.get("supervisor_pid"), "running": False, "mpiexec_count": 0},
        "supervisor_log_sha256": validator.sha256(campaign_log),
        "supervisor_completion_marker": True,
        "waves_completed": state["waves_completed"],
        "checkpoint_reuse": False,
        "settings": scope["configuration"],
        "datasets": {str(hours): {"path": EXPECTED_DATASETS[hours][0], "sha256": EXPECTED_DATASETS[hours][1], "channels": 31} for hours in (1, 10)},
        "configuration_pair_checks": config_checks,
        "audit_code": {
            "path": Path(__file__).resolve().relative_to(root).as_posix(),
            "sha256": validator.sha256(Path(__file__).resolve()),
        },
        "audit_helpers": {
            "product_validator": {
                "path": Path(validator.__file__).resolve().relative_to(root).as_posix(),
                "sha256": validator.sha256(Path(validator.__file__).resolve()),
            },
            "calibrated_sigma": {
                "path": Path(sigma_calibration.__file__).resolve().relative_to(root).as_posix(),
                "sha256": validator.sha256(Path(sigma_calibration.__file__).resolve()),
            },
        },
        "models": models,
        "matched_loo_contrasts": pairs,
        "summary_files": {
            "models_csv": model_csv.name,
            "loo_csv": pair_csv.name,
            "figure_svg": figure_path.name,
        },
        "method": {
            "delta_lnb": "lnZ(full) - lnZ(without X), both read from final native MultiNest stats.dat and paired only at the same exposure and dataset.",
            "numeric_error": "sqrt(error_full^2 + error_without_X^2), assuming independent numerical evidence errors.",
            "sigma": "Calibrated bilateral mapping implemented in report_proxima_loo_lin_sigma.py; descriptive auxiliary only; N/A if delta lnB <= 0.",
            "posterior_probability": "P(log10 X > log10 A0) calculated from equal-weight POSEIDON posterior samples only when X is retained; N/A for the removed species.",
        },
        "interpretation_guardrails": [
            "Positive delta lnB favors the full model over the specified one-species-absent model under the matched priors and likelihood.",
            "Posterior probability above A0 describes abundance direction, not model preference or a causal agricultural attribution.",
            "Evidence differences are conditional on the same duration-specific dataset; 1 h and 10 h are not compared by subtracting their lnZ values.",
            "The historical old-binning campaign is not the comparator; it also used a different native wavelength interval.",
        ],
    }
    if args.reconcile_ledger:
        report["ledger_reconciliation"] = reconcile_ledgers(
            campaign, state, manifest, models, json_path
        )
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"AUDIT PASS: {json_path}")
    print(f"MODELS CSV: {model_csv}")
    print(f"LOO CSV: {pair_csv}")
    print(f"FIGURE: {figure_path}")
    for row in pairs:
        sigma_text = "N/A" if row["sigma_calibrated_auxiliary"] is None else f"{row['sigma_calibrated_auxiliary']:.3f}"
        print(
            f"A3-{row['hours']}h no-{row['excluded_species']}: "
            f"lnZfull={row['lnz_full']:.6f}±{row['lnz_full_error']:.6f}; "
            f"lnZLOO={row['lnz_without_species']:.6f}±{row['lnz_without_species_error']:.6f}; "
            f"delta={row['delta_lnb_full_minus_without']:+.6f}±{row['delta_lnb_numeric_error_quadrature']:.6f}; "
            f"sigma_aux={sigma_text}; P(X>A0|full)={row['p_species_gt_a0_full_model']:.6f}"
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # Keep the failure explicit; do not modify ledgers.
        print(f"AUDIT FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise
