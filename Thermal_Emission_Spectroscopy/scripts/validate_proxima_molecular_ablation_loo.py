#!/usr/bin/env python3
"""Validate and summarize the completed Proxima LIFE molecular LOO campaign.

The campaign state is the run ledger. This audit independently checks the
matched datasets, final POSEIDON products, MultiNest products, and evidence
agreement before computing any full-versus-ablated Bayes factor.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Iterator


CAMPAIGN_REL = Path(
    "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/"
    "retrievals/molecule_ablation_loo_20261004"
)
DATA_ROOT_REL = Path("Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1")
EXPECTED_SPECIES = ("H2O", "CO2", "CH4", "O3", "N2O", "NH3")
GAS_PARAMETERS = tuple(f"log_{species}" for species in ("H2O", "CO2", "CH4", "O2", "O3", "N2O", "NH3"))
BASE_PARAMETERS = ("R_p_ref", "a1", "a2", "log_P1", "log_P2", "log_P3", "T_ref", "log_P_surf")
SCENARIO_ORDER = ("A1", "A3")
HOUR_ORDER = (1, 10, 100)
SPECIES_LABEL = {
    "H2O": "H₂O",
    "CO2": "CO₂",
    "CH4": "CH₄",
    "O3": "O₃",
    "N2O": "N₂O",
    "NH3": "NH₃",
}
SCENARIO_COLOR = {"A1": "#56E3DB", "A3": "#E34F95"}
TIME_MARKER = {1: "circle", 10: "square", 100: "triangle"}

RESULT_EVIDENCE_RE = re.compile(
    r"->\s*ln\s+Z\s*=\s*([-+\d.eE]+)\s*\+/-\s*([-+\d.eE]+)",
    re.IGNORECASE,
)
STATS_EVIDENCE_RE = re.compile(
    r"Nested Sampling Global Log-Evidence\s*:\s*"
    r"([-+\d.eE]+)\s*\+/-\s*([-+\d.eE]+)",
    re.IGNORECASE,
)


def repo_path(value: str | Path, root: Path) -> Path:
    """Map repository-relative and WSL /mnt/c paths into the current checkout."""
    raw = str(value)
    marker = "/mnt/c/Proyectos/Astro/ExoFarm_MDwarfs/"
    if raw.startswith(marker):
        return root / Path(*PurePosixPath(raw[len(marker) :]).parts)
    if raw.startswith("/mnt/c/"):
        return Path("C:/") / Path(*PurePosixPath(raw[len("/mnt/c/") :]).parts)
    return root / Path(raw.replace("/", str(Path.sep)))


def require_file(path: Path) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f"missing or empty file: {path}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def numeric_rows(
    path: Path,
    *,
    skip_lines: int = 0,
    allow_text_prefix: bool = False,
    allow_text_anywhere: bool = False,
) -> Iterator[list[float]]:
    """Yield finite whitespace-delimited rows; optionally skip textual headers."""
    require_file(path)
    yielded = 0
    with path.open("r", encoding="utf-8", errors="replace") as stream:
        for line_number, line in enumerate(stream):
            if line_number < skip_lines or not line.strip() or line.lstrip().startswith("#"):
                continue
            try:
                row = [float(token) for token in line.split()]
            except ValueError:
                if allow_text_anywhere:
                    continue
                if allow_text_prefix and yielded == 0:
                    continue
                raise ValueError(f"non-numeric row at {path}:{line_number + 1}")
            if not row or not all(math.isfinite(value) for value in row):
                raise ValueError(f"empty or non-finite numeric row at {path}:{line_number + 1}")
            yielded += 1
            yield row
    if yielded == 0:
        raise ValueError(f"no numeric rows: {path}")


def validate_table(
    path: Path,
    *,
    skip_lines: int = 0,
    allow_text_prefix: bool = False,
    expected_columns: int | None = None,
    min_rows: int = 1,
    max_rows: int | None = None,
    row_check: Any = None,
    allow_text_anywhere: bool = False,
) -> tuple[int, int]:
    row_count = 0
    column_count: int | None = expected_columns
    for row in numeric_rows(
        path,
        skip_lines=skip_lines,
        allow_text_prefix=allow_text_prefix,
        allow_text_anywhere=allow_text_anywhere,
    ):
        if column_count is None:
            column_count = len(row)
        if len(row) != column_count:
            raise ValueError(
                f"inconsistent columns in {path}: expected {column_count}, got {len(row)}"
            )
        if row_check is not None:
            row_check(row, row_count)
        row_count += 1
    if row_count < min_rows or (max_rows is not None and row_count > max_rows):
        raise ValueError(f"unexpected row count in {path}: {row_count}")
    return row_count, int(column_count or 0)


def validate_log_x(path: Path, excluded_species: str) -> int:
    """Validate the repeated 100-layer abundance-quantile blocks in log-X."""
    require_file(path)
    all_profile_species = {name.removeprefix("log_") for name in GAS_PARAMETERS}
    expected = {"N2"} | (all_profile_species - {excluded_species})
    seen: set[str] = set()
    block_species: str | None = None
    block_rows = 0
    pressure_previous = math.inf
    total_rows = 0

    def finish_block() -> None:
        if block_species is not None and block_rows != 100:
            raise ValueError(f"expected 100 pressure rows for log_{block_species} in {path}; got {block_rows}")

    with path.open("r", encoding="utf-8", errors="replace") as stream:
        for line_number, line in enumerate(stream, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("Chemical species:"):
                continue
            header = re.match(r"P\s*\(bar\)\s*\|\s*log_([A-Za-z0-9]+):", stripped)
            if header:
                finish_block()
                block_species = header.group(1)
                if block_species not in expected or block_species in seen:
                    raise ValueError(f"unexpected or duplicate log-X species header at {path}:{line_number}")
                if not all(label in stripped for label in ("-2σ", "-1σ", "median", "+1σ", "+2σ")):
                    raise ValueError(f"incomplete log-X quantile header at {path}:{line_number}")
                seen.add(block_species)
                block_rows = 0
                pressure_previous = math.inf
                continue
            try:
                row = [float(token) for token in stripped.split()]
            except ValueError as exc:
                raise ValueError(f"unexpected text in log-X product at {path}:{line_number}") from exc
            if block_species is None or len(row) != 6 or not all(math.isfinite(value) for value in row):
                raise ValueError(f"malformed or non-finite log-X row at {path}:{line_number}")
            if row[0] <= 0 or row[0] >= pressure_previous or any(a > b for a, b in zip(row[1:], row[2:])):
                raise ValueError(f"invalid log-X pressure grid or quantiles at {path}:{line_number}")
            pressure_previous = row[0]
            block_rows += 1
            total_rows += 1
    finish_block()
    if seen != expected or total_rows != 100 * len(expected):
        raise ValueError(
            f"log-X species/layer coverage mismatch in {path}: "
            f"species={sorted(seen)}, rows={total_rows}, expected={sorted(expected)}"
        )
    return total_rows


def parse_evidence_from_result(path: Path, *, expected_parameters: int) -> dict[str, float | int | str]:
    require_file(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    evidence = RESULT_EVIDENCE_RE.search(text)
    model = re.search(r"^Model:\s*(\S+)\s*$", text, re.MULTILINE)
    dataset = re.search(r"->\s*LIFE\s*\(([^)]+)\)", text)
    n_params = re.search(r"N_params\s*=\s*(\d+)", text)
    n_live = re.search(r"N_live\s*=\s*(\d+)", text)
    chi2_red = re.search(r"->\s*chi\^2_red\s*=\s*([-+\d.eE]+)", text)
    dof = re.search(r"->\s*degrees\s+of\s+freedom\s*=\s*(\d+)", text)
    if not all((evidence, model, dataset, n_params, n_live, chi2_red, dof)):
        raise ValueError(f"incomplete final fit metadata in {path}")
    values = {
        "model": model.group(1),
        "dataset_label": dataset.group(1),
        "lnz_printed": float(evidence.group(1)),
        "lnz_error_printed": float(evidence.group(2)),
        "chi2_red": float(chi2_red.group(1)),
        "dof": int(dof.group(1)),
        "n_params": int(n_params.group(1)),
        "n_live": int(n_live.group(1)),
    }
    if values["n_params"] != expected_parameters or values["n_live"] != 800:
        raise ValueError(
            f"expected N_params={expected_parameters}, N_live=800 in {path}; "
            f"got {values['n_params']}, {values['n_live']}"
        )
    if values["dof"] <= 0 or not all(
        math.isfinite(float(values[key]))
        for key in ("lnz_printed", "lnz_error_printed", "chi2_red")
    ):
        raise ValueError(f"non-finite or invalid final fit metrics in {path}")
    return values


def parse_evidence_from_stats(path: Path) -> tuple[float, float]:
    require_file(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    match = STATS_EVIDENCE_RE.search(text)
    if match is None:
        raise ValueError(f"global nested-sampling evidence absent from {path}")
    lnz, error = float(match.group(1)), float(match.group(2))
    if not (math.isfinite(lnz) and math.isfinite(error) and error > 0):
        raise ValueError(f"invalid MultiNest evidence in {path}")
    return lnz, error


def parse_resume(path: Path) -> dict[str, int]:
    require_file(path)
    lines = [line.split() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(lines) < 2 or len(lines[1]) < 4:
        raise ValueError(f"unrecognized MultiNest resume file: {path}")
    try:
        replacements, evaluations, n_live = int(lines[1][0]), int(lines[1][1]), int(lines[1][3])
    except ValueError as exc:
        raise ValueError(f"invalid resume counters in {path}") from exc
    if n_live != 800 or replacements < n_live or evaluations <= 0:
        raise ValueError(f"invalid final MultiNest counters in {path}")
    return {"replacements": replacements, "evaluations": evaluations, "n_live": n_live}


def parse_table_header(path: Path) -> list[str]:
    require_file(path)
    first = path.read_text(encoding="utf-8", errors="replace").splitlines()[0]
    fields = [field.strip() for field in first.split("|")]
    if not fields or any(not field for field in fields):
        raise ValueError(f"unrecognized table header in {path}")
    return fields


def compare_posterior_to_multinest(samples_path: Path, equal_path: Path, columns: int) -> int:
    samples_iter = numeric_rows(samples_path, skip_lines=1)
    equal_iter = numeric_rows(equal_path)
    count = 0
    while True:
        try:
            sample_row = next(samples_iter)
        except StopIteration:
            sample_row = None
        try:
            equal_row = next(equal_iter)
        except StopIteration:
            equal_row = None
        if sample_row is None and equal_row is None:
            break
        if sample_row is None or equal_row is None:
            raise ValueError(f"posterior row-count mismatch: {samples_path} vs {equal_path}")
        if len(sample_row) != columns or len(equal_row) < columns:
            raise ValueError(f"posterior column mismatch: {samples_path} vs {equal_path}")
        if any(
            not math.isclose(a, b, rel_tol=0.0, abs_tol=2e-7)
            for a, b in zip(sample_row, equal_row[:columns])
        ):
            raise ValueError(f"POSEIDON posterior does not match MultiNest equal-weight samples: {samples_path}")
        count += 1
    return count


def validate_ablation(run: dict[str, Any], root: Path, campaign: Path) -> dict[str, Any]:
    run_id = run["run_id"]
    if run.get("status") != "completed" or int(run.get("return_code", -1)) != 0:
        raise ValueError(f"campaign ledger is not successful for {run_id}")
    if run.get("preflight_status") != "pass" or int(run.get("preflight_parameters", -1)) != 14:
        raise ValueError(f"preflight is not a 14-parameter PASS for {run_id}")
    if int(run.get("preflight_return_code", -1)) != 0:
        raise ValueError(f"preflight return code is not zero for {run_id}")

    data_path = root / Path(*PurePosixPath(run["dataset_rel"]).parts)
    require_file(data_path)
    actual_hash = sha256(data_path)
    if actual_hash != run["dataset_sha256_expected"]:
        raise ValueError(f"dataset SHA-256 mismatch for {run_id}: {actual_hash}")
    data_rows, data_cols = validate_table(
        data_path,
        skip_lines=1,
        expected_columns=4,
        min_rows=31,
        max_rows=31,
    )
    data_previous = -math.inf
    for row in numeric_rows(data_path, skip_lines=1):
        if row[0] <= data_previous or row[1] <= 0 or row[3] <= 0:
            raise ValueError(f"invalid wavelength/bin/error values in {data_path}")
        data_previous = row[0]

    archive = repo_path(run["archive_dir"], root)
    retrieval = archive / "POSEIDON_output/proxima_b_earthlike/retrievals"
    stem = f"proxima_{run['scenario']}_{run['hours']}h{run['output_tag']}"
    result_path = retrieval / "results" / f"{stem}_results.txt"
    samples_path = retrieval / "samples" / f"{stem}_samples.txt"
    spectrum_path = retrieval / "samples" / f"{stem}_spectrum_retrieved.txt"
    pt_path = retrieval / "samples" / f"{stem}_PT_retrieved.txt"
    logx_path = retrieval / "samples" / f"{stem}_log_X_retrieved.txt"
    raw_dir = retrieval / "MultiNest_raw"
    raw_prefix = raw_dir / stem
    raw_paths = {
        suffix: Path(f"{raw_prefix}{suffix}")
        for suffix in (
            "-.txt",
            "-ev.dat",
            "-live.points",
            "-phys_live.points",
            "-post_equal_weights.dat",
            "-resume.dat",
            "-stats.dat",
            "-summary.txt",
        )
    }

    result = parse_evidence_from_result(result_path, expected_parameters=14)
    if result["model"] != stem:
        raise ValueError(f"model tag mismatch in {result_path}: {result['model']}")
    if result["dataset_label"] != Path(run["dataset_rel"]).name:
        raise ValueError(
            f"dataset label mismatch for {run_id}: {result['dataset_label']} vs "
            f"{Path(run['dataset_rel']).name}"
        )
    result_dataset = data_path.parent / result["dataset_label"]
    require_file(result_dataset)
    if sha256(result_dataset) != actual_hash:
        raise ValueError(f"result dataset bytes differ from the manifest dataset for {run_id}")

    stats_lnz, stats_error = parse_evidence_from_stats(raw_paths["-stats.dat"])
    if abs(stats_lnz - float(result["lnz_printed"])) > 0.0051:
        raise ValueError(f"POSEIDON/MultiNest lnZ mismatch for {run_id}")
    if abs(stats_error - float(result["lnz_error_printed"])) > 0.0051:
        raise ValueError(f"POSEIDON/MultiNest lnZ-error mismatch for {run_id}")

    header = parse_table_header(samples_path)
    expected_parameters = set(BASE_PARAMETERS) | (set(GAS_PARAMETERS) - {f"log_{run['excluded_species']}"})
    if len(header) != 14 or set(header) != expected_parameters:
        raise ValueError(f"unexpected 14-parameter posterior for {run_id}: {header}")
    sample_columns = len(header)
    surf_index = header.index("log_P_surf")
    sample_rows, _ = validate_table(
        samples_path,
        skip_lines=1,
        expected_columns=sample_columns,
        min_rows=1,
        row_check=lambda row, _: (
            None
            if abs(row[surf_index]) <= 1e-12
            else (_ for _ in ()).throw(ValueError(f"log_P_surf is not fixed to 0 in {samples_path}"))
        ),
    )
    equal_rows, equal_columns = validate_table(
        raw_paths["-post_equal_weights.dat"],
        min_rows=1,
        row_check=None,
    )
    if equal_rows != sample_rows or equal_columns < sample_columns:
        raise ValueError(f"posterior dimensions differ from MultiNest for {run_id}")
    compared_rows = compare_posterior_to_multinest(samples_path, raw_paths["-post_equal_weights.dat"], sample_columns)

    wavelength_previous = -math.inf

    def check_spectrum(row: list[float], _: int) -> None:
        nonlocal wavelength_previous
        if row[0] <= wavelength_previous or any(a > b for a, b in zip(row[1:], row[2:])):
            raise ValueError(f"invalid wavelength or spectral quantiles in {spectrum_path}")
        wavelength_previous = row[0]

    spectrum_rows, spectrum_cols = validate_table(
        spectrum_path,
        skip_lines=1,
        expected_columns=6,
        min_rows=2,
        row_check=check_spectrum,
    )

    pressure_previous = math.inf

    def check_pt(row: list[float], _: int) -> None:
        nonlocal pressure_previous
        if row[0] <= 0 or row[0] >= pressure_previous or any(a > b for a, b in zip(row[1:], row[2:])):
            raise ValueError(f"invalid pressure grid or P-T quantiles in {pt_path}")
        pressure_previous = row[0]

    pt_rows, pt_cols = validate_table(
        pt_path,
        skip_lines=1,
        expected_columns=6,
        min_rows=100,
        max_rows=100,
        row_check=check_pt,
    )
    logx_rows = validate_log_x(logx_path, run["excluded_species"])
    logx_cols = 6

    raw_shapes: dict[str, list[int]] = {}
    for suffix in ("-.txt", "-ev.dat", "-live.points", "-phys_live.points", "-summary.txt"):
        count, columns = validate_table(raw_paths[suffix], min_rows=1)
        raw_shapes[suffix] = [count, columns]
    for suffix in ("-live.points", "-phys_live.points"):
        if raw_shapes[suffix][0] != 800:
            raise ValueError(f"expected 800 live points in {raw_paths[suffix]}")
    resume = parse_resume(raw_paths["-resume.dat"])
    if raw_shapes["-ev.dat"][0] != resume["replacements"] - resume["n_live"]:
        raise ValueError(f"MultiNest ev/resume row mismatch for {run_id}")

    launch_log = repo_path(run.get("launch_log", ""), root)
    if not launch_log.is_file():
        launch_log = campaign / "logs" / f"{run_id}.launch.log"
    require_file(launch_log)
    log_text = launch_log.read_text(encoding="utf-8", errors="replace")
    if "Sampling finished. Exiting MultiNest" not in log_text or "All done!" not in log_text:
        raise ValueError(f"completion markers are missing from {launch_log}")
    if f"[done] {stem}" not in log_text:
        raise ValueError(f"final [done] marker is missing from {launch_log}")

    return {
        "run_id": run_id,
        "scenario": run["scenario"],
        "hours": int(run["hours"]),
        "excluded_species": run["excluded_species"],
        "dataset_rel": run["dataset_rel"],
        "dataset_seed": int(run["dataset_seed"]),
        "dataset_sha256": actual_hash,
        "full_results": run["full_results"],
        "full_evidence": None,
        "lnz_loo": stats_lnz,
        "lnz_loo_error": stats_error,
        "chi2_red_loo": float(result["chi2_red"]),
        "dof_loo": int(result["dof"]),
        "posterior_samples": sample_rows,
        "spectrum_rows": spectrum_rows,
        "pt_rows": pt_rows,
        "logx_rows": logx_rows,
        "numeric_columns": {"dataset": data_cols, "spectrum": spectrum_cols, "pt": pt_cols, "logx": logx_cols},
        "posterior_rows_crosschecked": compared_rows,
        "resume": resume,
        "multinest_shapes": raw_shapes,
    }


def validate_full_model(result_path: Path, expected_dataset_hash: str) -> dict[str, float | int | str]:
    stem = result_path.name.removesuffix("_results.txt")
    result = parse_evidence_from_result(result_path, expected_parameters=15)
    if result["model"] != stem:
        raise ValueError(f"full-model tag mismatch in {result_path}")
    result_dataset = DATA_ROOT_REL / "life_data" / str(result["dataset_label"])
    # DATA_ROOT_REL is relative to the repository; the caller uses its root below.
    return {**result, "stem": stem, "result_dataset_rel": result_dataset.as_posix(), "expected_dataset_hash": expected_dataset_hash}


def validate_full_for_pair(run: dict[str, Any], root: Path, campaign_hash: str) -> dict[str, Any]:
    result_path = repo_path(run["full_results"], root)
    parsed = validate_full_model(result_path, campaign_hash)
    data_path = root / Path(*PurePosixPath(parsed["result_dataset_rel"]).parts)
    require_file(data_path)
    full_hash = sha256(data_path)
    if full_hash != campaign_hash:
        raise ValueError(f"official full-model input differs from the matched LIFE dataset for {run['run_id']}")
    raw_dir = result_path.parent.parent / "MultiNest_raw"
    stats_path = raw_dir / f"{parsed['stem']}-stats.dat"
    lnz_stats, error_stats = parse_evidence_from_stats(stats_path)
    if abs(lnz_stats - float(parsed["lnz_printed"])) > 0.0051:
        raise ValueError(f"official full-model POSEIDON/MultiNest lnZ mismatch for {run['run_id']}")
    if abs(error_stats - float(parsed["lnz_error_printed"])) > 0.0051:
        raise ValueError(f"official full-model POSEIDON/MultiNest error mismatch for {run['run_id']}")
    return {
        "result_path": result_path,
        "dataset_label": parsed["dataset_label"],
        "dataset_sha256": full_hash,
        "lnz": lnz_stats,
        "lnz_error": error_stats,
        "chi2_red": float(parsed["chi2_red"]),
        "dof": int(parsed["dof"]),
        "n_params": int(parsed["n_params"]),
        "n_live": int(parsed["n_live"]),
    }


def sellke_sigma(log_b: float) -> float:
    """Invert the Sellke upper-bound relation and return signed Gaussian z."""
    magnitude = abs(log_b)
    target = 1.0 + magnitude
    low = 1.0
    high = max(2.0, target + math.log(target + 1.0) + 4.0)
    for _ in range(120):
        mid = (low + high) / 2.0
        if mid - math.log(mid) < target:
            low = mid
        else:
            high = mid
    log_p = -(low + high) / 2.0
    log_tail = log_p - math.log(2.0)

    def log_normal_survival(z: float) -> float:
        if z < 8.0:
            return math.log(0.5 * math.erfc(z / math.sqrt(2.0)))
        inverse_square = 1.0 / (z * z)
        correction = 1.0 - inverse_square + 3.0 * inverse_square**2 - 15.0 * inverse_square**3 + 105.0 * inverse_square**4
        return -0.5 * z * z - math.log(z) - 0.5 * math.log(2.0 * math.pi) + math.log(correction)

    z_low, z_high = 0.0, max(2.0, math.sqrt(max(0.0, -2.0 * log_tail)) + 2.0)
    while log_normal_survival(z_high) > log_tail:
        z_high *= 2.0
    for _ in range(120):
        mid = (z_low + z_high) / 2.0
        if log_normal_survival(mid) > log_tail:
            z_low = mid
        else:
            z_high = mid
    z = (z_low + z_high) / 2.0
    return math.copysign(z, log_b)


def build_pairs(valid_runs: list[dict[str, Any]], full_cache: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = []
    for item in valid_runs:
        full = full_cache[item["full_results"]]
        delta = float(full["lnz"]) - item["lnz_loo"]
        sigma_delta = math.hypot(float(full["lnz_error"]), item["lnz_loo_error"])
        pairs.append(
            {
                **item,
                "lnz_full": float(full["lnz"]),
                "lnz_full_error": float(full["lnz_error"]),
                "chi2_red_full": float(full["chi2_red"]),
                "dof_full": int(full["dof"]),
                "delta_lnb": delta,
                "delta_lnb_numeric_error": sigma_delta,
                "sellke_sigma_max": sellke_sigma(delta),
            }
        )
    return sorted(
        pairs,
        key=lambda item: (
            SCENARIO_ORDER.index(item["scenario"]),
            HOUR_ORDER.index(item["hours"]),
            EXPECTED_SPECIES.index(item["excluded_species"]),
        ),
    )


def write_svg_figure(pairs: list[dict[str, Any]], path: Path) -> None:
    width, height = 1420, 970
    panel_width = 620
    panel_gap = 70
    panel_lefts = (70, 70 + panel_width + panel_gap)
    plot_left_offset, plot_right_offset = 100, panel_width - 18
    top, row_height = 190, 105
    plot_bottom = top + row_height * len(EXPECTED_SPECIES) - 12
    all_values = [
        value
        for item in pairs
        for value in (item["delta_lnb"] - item["delta_lnb_numeric_error"], item["delta_lnb"] + item["delta_lnb_numeric_error"])
    ]
    x_min = min(-3.0, math.floor(min(all_values)))
    x_max = max(10.0, max(all_values))
    x_max = 10.0 ** math.ceil(math.log10(x_max + 1.0)) if x_max > 10 else 10.0
    threshold = 1.0

    def transform(value: float) -> float:
        return math.copysign(math.log10(1.0 + abs(value) / threshold), value)

    t_min, t_max = transform(x_min), transform(x_max)

    def x_position(panel_left: int, value: float) -> float:
        plot_left = panel_left + plot_left_offset
        plot_width = plot_right_offset - plot_left_offset
        return plot_left + (transform(value) - t_min) / (t_max - t_min) * plot_width

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:Georgia,"Times New Roman",serif;fill:#20202a}.title{font-size:28px;font-weight:bold}.subtitle{font-size:15px}.panel{font-size:22px;font-weight:bold}.species{font-size:17px}.tick{font-size:13px}.legend{font-size:15px}.foot{font-size:14px}</style>',
        '<text x="710" y="42" text-anchor="middle" class="title">Conditional molecular evidence in LIFE Proxima LOO retrievals</text>',
        '<text x="710" y="70" text-anchor="middle" class="subtitle">Matched full-model ln Z − one-species-absent ln Z; error bars show propagated MultiNest numerical uncertainty</text>',
    ]
    ticks = [
        value
        for value in (-3, -1, 0, 1, 3, 10, 30, 100, 300, 1000, 3000, 10000, 30000, 100000)
        if x_min <= value <= x_max
    ]
    for panel_left, scenario in zip(panel_lefts, SCENARIO_ORDER):
        out.append(f'<text x="{panel_left + panel_width / 2}" y="112" text-anchor="middle" class="panel">{scenario}</text>')
        plot_left = panel_left + plot_left_offset
        plot_right = panel_left + plot_right_offset
        for tick in ticks:
            x = x_position(panel_left, tick)
            color = "#6a6a74" if tick == 0 else "#dedee5"
            dash = ' stroke-dasharray="5 4"' if tick == 0 else ""
            out.append(f'<line x1="{x:.1f}" y1="{top - 10}" x2="{x:.1f}" y2="{plot_bottom}" stroke="{color}"{dash}/>')
            out.append(f'<text x="{x:.1f}" y="{plot_bottom + 24}" text-anchor="middle" class="tick">{tick:g}</text>')
        out.append(f'<line x1="{plot_left}" y1="{plot_bottom}" x2="{plot_right}" y2="{plot_bottom}" stroke="#30303a" stroke-width="1.2"/>')
        for species_index, species in enumerate(EXPECTED_SPECIES):
            center_y = top + species_index * row_height + row_height / 2
            out.append(f'<text x="{panel_left + 84}" y="{center_y + 6}" text-anchor="end" class="species">{SPECIES_LABEL[species]}</text>')
            out.append(f'<line x1="{plot_left}" y1="{center_y + row_height / 2}" x2="{plot_right}" y2="{center_y + row_height / 2}" stroke="#eeeeF2"/>')
            for hour_index, hours in enumerate(HOUR_ORDER):
                item = next(
                    entry for entry in pairs
                    if entry["scenario"] == scenario and entry["hours"] == hours and entry["excluded_species"] == species
                )
                value = item["delta_lnb"]
                error = item["delta_lnb_numeric_error"]
                y = center_y + (hour_index - 1) * 18
                x1, x2, xc = (x_position(panel_left, value - error), x_position(panel_left, value + error), x_position(panel_left, value))
                color = SCENARIO_COLOR[scenario]
                out.append(f'<line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="2"/>')
                out.append(f'<line x1="{x1:.1f}" y1="{y-4:.1f}" x2="{x1:.1f}" y2="{y+4:.1f}" stroke="{color}" stroke-width="1.5"/>')
                out.append(f'<line x1="{x2:.1f}" y1="{y-4:.1f}" x2="{x2:.1f}" y2="{y+4:.1f}" stroke="{color}" stroke-width="1.5"/>')
                marker = TIME_MARKER[hours]
                if marker == "circle":
                    out.append(f'<circle cx="{xc:.1f}" cy="{y:.1f}" r="5.3" fill="{color}" stroke="#282833" stroke-width="1"/>')
                elif marker == "square":
                    out.append(f'<rect x="{xc-5:.1f}" y="{y-5:.1f}" width="10" height="10" fill="{color}" stroke="#282833" stroke-width="1"/>')
                else:
                    out.append(f'<path d="M {xc:.1f} {y-6:.1f} L {xc+6:.1f} {y+5:.1f} L {xc-6:.1f} {y+5:.1f} Z" fill="{color}" stroke="#282833" stroke-width="1"/>')
        legend_y = plot_bottom + 58
        for hour_index, hours in enumerate(HOUR_ORDER):
            lx = panel_left + 155 + hour_index * 115
            marker = TIME_MARKER[hours]
            if marker == "circle":
                out.append(f'<circle cx="{lx}" cy="{legend_y-4}" r="5" fill="{SCENARIO_COLOR[scenario]}" stroke="#282833"/>')
            elif marker == "square":
                out.append(f'<rect x="{lx-5}" y="{legend_y-9}" width="10" height="10" fill="{SCENARIO_COLOR[scenario]}" stroke="#282833"/>')
            else:
                out.append(f'<path d="M {lx} {legend_y-10} L {lx+6} {legend_y+2} L {lx-6} {legend_y+2} Z" fill="{SCENARIO_COLOR[scenario]}" stroke="#282833"/>')
            out.append(f'<text x="{lx+10}" y="{legend_y}" class="legend">{hours} h</text>')
    out.append('<text x="710" y="930" text-anchor="middle" class="foot">Positive values favor including the species. Horizontal axis is symmetric-log (linear near zero); ln B is conditional on each matched dataset.</text>')
    out.append('</svg>')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def write_outputs(campaign: Path, root: Path, pairs: list[dict[str, Any]], checks: dict[str, Any]) -> tuple[Path, Path, Path]:
    csv_path = campaign / "loo_results_validated_20261010.csv"
    json_path = campaign / "validation_report_20261010.json"
    figure_path = root / "Thermal_Emission_Spectroscopy/final_products/figures/life_proxima_molecular_ablation_loo_lnB_2026-10-10.svg"
    fieldnames = (
        "scenario", "hours", "excluded_species", "dataset_rel", "dataset_seed", "dataset_sha256",
        "lnz_full", "lnz_full_error", "lnz_loo", "lnz_loo_error", "delta_lnb",
        "delta_lnb_numeric_error", "sellke_sigma_max", "chi2_red_full", "dof_full", "chi2_red_loo",
        "dof_loo", "posterior_samples", "spectrum_rows", "pt_rows", "logx_rows",
    )
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for item in pairs:
            writer.writerow({key: item[key] for key in fieldnames})
    report = {
        **checks,
        "validated_pairs": len(pairs),
        "summary_csv": csv_path.relative_to(root).as_posix(),
        "figure_svg": figure_path.relative_to(root).as_posix(),
        "method": {
            "delta_lnb": "lnZ(full) - lnZ(without X), from final MultiNest stats.dat; matched only by scenario/time/dataset/seed",
            "numeric_error": "quadrature of the two MultiNest lnZ errors, assuming independent numerical errors",
            "sellke_sigma": "signed inversion of the Sellke upper-bound relation; descriptive upper bound, not frequentist detection significance",
        },
    }
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_svg_figure(pairs, figure_path)
    return csv_path, json_path, figure_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.repo.resolve()
    campaign = root / CAMPAIGN_REL
    state_path = campaign / "campaign_state.json"
    manifest_path = campaign / "manifest.csv"
    with state_path.open(encoding="utf-8") as stream:
        state = json.load(stream)
    with manifest_path.open(newline="", encoding="utf-8") as stream:
        manifest = {row["run_id"]: row for row in csv.DictReader(stream)}

    errors: list[str] = []
    runs = state.get("runs", [])
    if state.get("campaign_status") != "completed":
        errors.append(f"campaign_status={state.get('campaign_status')!r}, expected 'completed'")
    if state.get("active_run_ids"):
        errors.append(f"active_run_ids is not empty: {state.get('active_run_ids')}")
    if state.get("canonical_8of8_modified") is not False:
        errors.append("canonical 8/8 matrix is not explicitly recorded as unchanged")
    if state.get("official_full_model_runs_reused") is not True:
        errors.append("state does not confirm reuse of the six official full-model runs")
    if len(runs) != 36 or len(manifest) != 36:
        errors.append(f"expected 36 state/manifest entries, got {len(runs)}/{len(manifest)}")

    groups: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for run in runs:
        groups[(run["scenario"], int(run["hours"]))].append(run)
        row = manifest.get(run["run_id"])
        if row is None:
            errors.append(f"manifest missing {run['run_id']}")
        elif row.get("status") != "completed" or row.get("return_code") != "0" or row.get("preflight_status") != "pass":
            errors.append(f"manifest does not show completed/pass/exit-0 for {run['run_id']}")
    expected_species = set(EXPECTED_SPECIES)
    for key, members in groups.items():
        if len(members) != 6 or {member["excluded_species"] for member in members} != expected_species:
            errors.append(f"incomplete or duplicated molecular set for {key}")
        for field in ("dataset_rel", "dataset_seed", "dataset_sha256_expected", "full_results"):
            if len({member[field] for member in members}) != 1:
                errors.append(f"mismatched {field} within matched dataset group {key}")
    if set(groups) != {(scenario, hour) for scenario in SCENARIO_ORDER for hour in HOUR_ORDER}:
        errors.append("scenario/time groups do not equal A1/A3 × 1/10/100 h")

    valid_runs: list[dict[str, Any]] = []
    for run in runs:
        try:
            valid_runs.append(validate_ablation(run, root, campaign))
        except Exception as exc:  # retain every diagnostic and continue auditing other runs
            errors.append(f"{run.get('run_id')}: {exc}")

    full_cache: dict[str, dict[str, Any]] = {}
    for run in runs:
        full_path = run["full_results"]
        if full_path in full_cache:
            continue
        try:
            group_key = (run["scenario"], int(run["hours"]))
            campaign_hash = run["dataset_sha256_expected"]
            full_cache[full_path] = validate_full_for_pair(run, root, campaign_hash)
        except Exception as exc:
            errors.append(f"official full model {full_path}: {exc}")

    pairs: list[dict[str, Any]] = []
    if len(valid_runs) == 36 and len(full_cache) == 6 and not errors:
        pairs = build_pairs(valid_runs, full_cache)
    checks = {
        "campaign_id": state.get("campaign_id"),
        "campaign_status": state.get("campaign_status"),
        "completed_utc": state.get("completed_utc"),
        "updated_utc": state.get("updated_utc"),
        "state_runs": len(runs),
        "manifest_runs": len(manifest),
        "preflight_passes": sum(1 for run in runs if run.get("preflight_status") == "pass" and int(run.get("preflight_parameters", -1)) == 14),
        "exit_zero_runs": sum(1 for run in runs if int(run.get("return_code", -1)) == 0),
        "archived_run_products_valid": len(valid_runs),
        "official_full_models_valid": len(full_cache),
        "active_run_ids": state.get("active_run_ids", []),
        "max_parallel": state.get("max_parallel"),
        "mpi_ranks_per_run": state.get("mpi_ranks_per_run"),
        "canonical_8of8_modified": state.get("canonical_8of8_modified"),
        "errors": errors,
    }
    if not errors and len(pairs) == 36:
        csv_path, json_path, figure_path = write_outputs(campaign, root, pairs, checks)
        print(f"VALID: {len(pairs)}/36 matched LOO pairs; all products, datasets and baseline evidences passed.")
        print(f"CSV: {csv_path}")
        print(f"JSON: {json_path}")
        print(f"SVG: {figure_path}")
        for item in pairs:
            print(
                f"{item['scenario']} {item['hours']:>3} h {item['excluded_species']:>3}: "
                f"lnB={item['delta_lnb']:+.6f} +/- {item['delta_lnb_numeric_error']:.6f}; "
                f"Sellke sigma_max={item['sellke_sigma_max']:+.3f}"
            )
        return 0

    failure_path = campaign / "validation_report_20261010.json"
    checks["validated_pairs"] = 0
    failure_path.write_text(json.dumps(checks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"VALIDATION FAILED: {len(errors)} issue(s); details: {failure_path}", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
