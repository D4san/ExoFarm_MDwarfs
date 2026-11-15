#!/usr/bin/env python3
"""Validate and stage a copied, internally consistent A1 MultiNest checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import math
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
RAW_REL = Path(
    "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1"
    "/retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/MultiNest_raw"
)
CAMPAIGN_RETRIEVALS = (
    REPO / "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals"
)
OLD_TAG = "_O2_fixedBlack1bar_noxtol_MPI6"
NEW_TAG = "_O2_fixedBlack1bar_noxtol_MPI6R1"
N_LIVE = 800
CHECKPOINT_SUFFIXES = ("-resume.dat", "-ev.dat", "-live.points", "-phys_live.points")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_rows(data: bytes, label: str) -> tuple[int, int]:
    rows = data.splitlines()
    if not rows:
        raise ValueError(f"{label}: archivo vacío")
    ncols = None
    for row_number, raw in enumerate(rows, start=1):
        try:
            fields = raw.decode("ascii").split()
            values = [float(field) for field in fields]
        except (UnicodeDecodeError, ValueError) as exc:
            raise ValueError(f"{label}: fila {row_number} no es numérica") from exc
        if not values or not all(math.isfinite(value) for value in values):
            raise ValueError(f"{label}: fila {row_number} vacía o con NaN/Inf")
        if ncols is None:
            ncols = len(values)
        elif len(values) != ncols:
            raise ValueError(f"{label}: número de columnas irregular en fila {row_number}")
    return len(rows), int(ncols or 0)


def check_poseidon_api() -> None:
    from POSEIDON.retrieval import run_retrieval

    signature = inspect.signature(run_retrieval)
    print(f"POSEIDON run_retrieval{signature}")
    if "resume" not in signature.parameters:
        raise SystemExit("[abort] POSEIDON run_retrieval no acepta resume=")
    print("[api-check] resume= está disponible")


def stage(hours: int, run_dir: Path, manifest_path: Path) -> None:
    if hours not in (10, 100):
        raise ValueError("hours debe ser 10 o 100")
    if not run_dir.is_absolute() or not run_dir.is_relative_to(Path("/home")):
        raise ValueError("run-dir debe ser un directorio absoluto bajo /home")

    run_name = f"proxima_A1_{hours}h"
    source_stem = run_name + OLD_TAG
    target_stem = run_name + NEW_TAG
    raw_source = REPO / RAW_REL
    source_prefix = raw_source / source_stem

    resume_bytes = Path(f"{source_prefix}-resume.dat").read_bytes()
    resume_lines = [line.split() for line in resume_bytes.splitlines() if line.strip()]
    if len(resume_lines) < 2 or len(resume_lines[1]) < 4:
        raise ValueError(f"{source_stem}: formato resume.dat no reconocido")
    try:
        replacements = int(resume_lines[1][0])
        nlive_in_checkpoint = int(resume_lines[1][3])
    except ValueError as exc:
        raise ValueError(f"{source_stem}: contadores inválidos en resume.dat") from exc
    if nlive_in_checkpoint != N_LIVE:
        raise ValueError(
            f"{source_stem}: resume.dat declara nlive={nlive_in_checkpoint}, "
            f"se esperaba {N_LIVE}"
        )
    expected_ev_rows = replacements - N_LIVE
    if expected_ev_rows <= 0:
        raise ValueError(f"{source_stem}: contador ev.dat no plausible")

    source_data = {
        suffix: Path(f"{source_prefix}{suffix}").read_bytes()
        for suffix in CHECKPOINT_SUFFIXES
    }
    ev_rows, ev_cols = parse_rows(source_data["-ev.dat"], f"{source_stem}-ev.dat")
    if ev_rows < expected_ev_rows:
        raise ValueError(
            f"{source_stem}: ev.dat tiene {ev_rows} filas, checkpoint requiere "
            f"{expected_ev_rows}; no se puede reanudar con seguridad"
        )
    if ev_rows - expected_ev_rows > 1000:
        raise ValueError(
            f"{source_stem}: ev.dat excede el checkpoint por "
            f"{ev_rows - expected_ev_rows} filas; revisar antes de continuar"
        )

    live_rows, live_cols = parse_rows(
        source_data["-live.points"], f"{source_stem}-live.points"
    )
    phys_rows, phys_cols = parse_rows(
        source_data["-phys_live.points"], f"{source_stem}-phys_live.points"
    )
    if live_rows != N_LIVE or phys_rows != N_LIVE:
        raise ValueError(
            f"{source_stem}: live={live_rows}, phys_live={phys_rows}; "
            f"ambos deben ser {N_LIVE}"
        )

    # MultiNest's saved iteration counter is the authority for ev.dat length.
    # The source files contain post-checkpoint rows; retain only the exact prefix
    # represented by resume.dat in the staged copy. Originals remain untouched.
    ev_lines = source_data["-ev.dat"].splitlines(keepends=True)
    staged_data = dict(source_data)
    staged_data["-ev.dat"] = b"".join(ev_lines[:expected_ev_rows])
    staged_ev_rows, staged_ev_cols = parse_rows(
        staged_data["-ev.dat"], f"staged {target_stem}-ev.dat"
    )
    if staged_ev_rows != expected_ev_rows or staged_ev_cols != ev_cols:
        raise ValueError("ev.dat recortado no coincide con el checkpoint")

    target_raw = run_dir / "POSEIDON_output/proxima_b_earthlike/retrievals/MultiNest_raw"
    if run_dir.exists():
        raise FileExistsError(f"[abort] El directorio de reanudación ya existe: {run_dir}")
    target_raw.mkdir(parents=True)
    for suffix in CHECKPOINT_SUFFIXES:
        target = target_raw / f"{target_stem}{suffix}"
        if target.exists():
            raise FileExistsError(f"[abort] No se sobrescribe checkpoint: {target}")

    staged_hashes = {}
    with tempfile.TemporaryDirectory(prefix="a1-resume-") as temp_name:
        temp_dir = Path(temp_name)
        for suffix, data in staged_data.items():
            temp_file = temp_dir / f"{target_stem}{suffix}"
            temp_file.write_bytes(data)
            staged_hashes[suffix] = sha256(data)
        for suffix in CHECKPOINT_SUFFIXES:
            os.replace(
                temp_dir / f"{target_stem}{suffix}",
                target_raw / f"{target_stem}{suffix}",
            )

    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "scenario": "Proxima LIFE A1",
        "hours": hours,
        "old_tag": OLD_TAG,
        "new_tag": NEW_TAG,
        "n_live": N_LIVE,
        "resume_replacements": replacements,
        "expected_ev_rows_from_checkpoint": expected_ev_rows,
        "source_ev_rows": ev_rows,
        "surplus_ev_rows_excluded_from_staged_copy": ev_rows - expected_ev_rows,
        "live_points_rows": live_rows,
        "phys_live_points_rows": phys_rows,
        "column_counts": {"ev": ev_cols, "live": live_cols, "phys_live": phys_cols},
        "source_sha256": {suffix: sha256(data) for suffix, data in source_data.items()},
        "staged_sha256": staged_hashes,
        "source_directory": str(raw_source),
        "staged_directory": str(target_raw),
        "source_files_modified": False,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    if manifest_path.exists():
        raise FileExistsError(f"[abort] No se sobrescribe manifiesto: {manifest_path}")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-poseidon-api", action="store_true")
    parser.add_argument("--hours", type=int, choices=(10, 100))
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    if args.check_poseidon_api:
        check_poseidon_api()
        return
    if args.hours is None or args.run_dir is None or args.manifest is None:
        parser.error("indica --hours, --run-dir y --manifest, o usa --check-poseidon-api")
    stage(args.hours, args.run_dir, args.manifest)


if __name__ == "__main__":
    main()
