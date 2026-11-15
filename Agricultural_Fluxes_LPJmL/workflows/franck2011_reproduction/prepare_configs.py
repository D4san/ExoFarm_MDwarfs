#!/usr/bin/env python3
"""Generate compact LPJmL 6.0.6 configs from the pinned upstream template."""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import unicodedata


ANALYSIS_OUTPUTS = (
    "grid",
    "land_area",
    "cftfrac",
    "cftfrac2",
    "cellfrac_agr",
    "cft_nharvest",
    "pft_harvestc",
    "pft_harvestc2",
    "sdate",
    "hdate",
    "sdate2",
    "hdate2",
    "maxthaw_depth",
    "harvestc_agr",
    "pft_harvestn",
    "pft_harvestn2",
    "n2o_nit_agr",
    "n2o_denit_agr",
    "nh3_agr",
    "n2_agr",
    "nfert_agr",
    "nmanure_agr",
    "nleaching_agr",
    "nuptake_agr",
    "bnf_agr",
    "ndepo_agr",
)

# Minimal auditable output set for the first global current-Earth experiment.
# Keeping the compact LPJmL land-cell grid avoids allocating a mostly empty
# global latitude/longitude cube while MPI still writes one coordinated file.
GLOBAL_A1_OUTPUTS = (
    "grid",
    "land_area",
    "cellfrac_agr",
    "n2o_nit_agr",
    "n2o_denit_agr",
    "nh3_agr",
    "n2_agr",
    "nfert_agr",
    "nmanure_agr",
    "nleaching_agr",
    "nuptake_agr",
    "bnf_agr",
    "ndepo_agr",
)

# The capacity selector only needs per-CFT carbon harvest and the compact
# cell geometry.  Keeping N and phenology diagnostics out of this stage is
# essential: LPJmL allocates their arrays before MPI starts and the full
# analysis set can exceed the WSL memory budget even though the final crop
# campaign only needs N/CH4 outputs after the map has been built.
CAPACITY_OUTPUTS = (
    "grid",
    "land_area",
    "pft_harvestc",
    "pft_harvestc2",
    "maxthaw_depth",
)

# Methane diagnostics are monthly LPJmL land and process outputs.  They are
# kept out of the original N-only campaigns and added explicitly when a
# methane-enabled capacity branch is requested.
METHANE_OUTPUTS = (
    "ch4_agr",
    "ch4_rice_em",
    "ch4_grassland",
    "ch4_emissions_wet",
    "ch4_emissions",
    "ch4_oxidation",
    "ch4_sink",
    "ch4_litter",
    "ch4_ebullition",
    "ch4_plant_gas",
)

# Monthly whole-stand losses for the matched natural control. These are kept
# separate from A1's annual agricultural-stand products.
GLOBAL_A0_OUTPUTS = (
    "grid",
    "land_area",
    "n2o_nit",
    "n2o_denit",
    "n_volatilization",
)


def _outputs_with_methane(outputs: tuple[str, ...], with_methane: bool) -> tuple[str, ...]:
    """Append methane diagnostics only for an explicitly methane-enabled run."""

    return outputs + METHANE_OUTPUTS if with_methane else outputs

NON_ASCII_METADATA = (
    "kbf.clm.json",
    "phusum_gswp3-w5e5_obsclim_24_bands_annual_1901-2019.clm.json",
    "sdate_24_bands.clm.json",
    "wateruse_isimip3a_histsoc_1850-2021.clm.json",
)

ASCII_REPLACEMENTS = str.maketrans(
    {
        "°": " degrees",
        "–": "-",
        "ä": "a",
        "ö": "o",
        "ü": "u",
    }
)


def _preprocess_upstream(lpjml_root: Path, *, from_restart: bool) -> dict:
    command = ["cpp", "-P"]
    if from_restart:
        command.append("-DFROM_RESTART")
    command.append("lpjml_config.cjson")
    completed = subprocess.run(
        command,
        cwd=lpjml_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def _output_spec(output_id: str) -> dict:
    return {
        "id": output_id,
        "file": {"fmt": "cdf", "name": f"output/{output_id}.nc"},
    }


def _set_grid(
    config: dict,
    mode: str,
    startgrid: int,
    endgrid: int | None = None,
) -> None:
    if mode == "pilot":
        config["startgrid"] = startgrid
        config["endgrid"] = startgrid if endgrid is None else endgrid
    else:
        config["startgrid"] = "all"
        config["endgrid"] = "all"


def _use_runtime_input_path(config: dict) -> None:
    """Let the runner's ``-inpath`` override upstream server paths."""

    config.pop("inpath", None)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _ascii_compatible(value, input_root: Path, key: str | None = None):
    """Make metadata acceptable to LPJmL's strict json-c parser.

    Runtime copies live away from the official input archive. Relative file
    references therefore become absolute while descriptive Unicode text is
    transliterated to ASCII. Numerical metadata remain unchanged.
    """

    if isinstance(value, dict):
        return {
            item_key: _ascii_compatible(item_value, input_root, item_key)
            for item_key, item_value in value.items()
        }
    if isinstance(value, list):
        return [_ascii_compatible(item, input_root) for item in value]
    if isinstance(value, str):
        if key == "filename" and not Path(value).is_absolute():
            return str((input_root / value).resolve())
        translated = value.translate(ASCII_REPLACEMENTS)
        return unicodedata.normalize("NFKD", translated).encode(
            "ascii", "ignore"
        ).decode("ascii")
    return value


def _prepare_runtime_metadata(input_root: Path, output_dir: Path) -> tuple[dict, list]:
    metadata_dir = output_dir / "runtime_input_metadata"
    overrides = {}
    records = []
    for filename in NON_ASCII_METADATA:
        source = input_root / filename
        if not source.is_file():
            raise FileNotFoundError(f"Missing LPJmL metadata: {source}")
        source_value = json.loads(source.read_text(encoding="utf-8"))
        runtime_value = _ascii_compatible(source_value, input_root)
        runtime_path = metadata_dir / filename
        _write_json(runtime_path, runtime_value)
        overrides[filename] = str(runtime_path.resolve())
        records.append(
            {
                "source": str(source.resolve()),
                "runtime_copy": str(runtime_path.resolve()),
                "source_sha256": _sha256(source),
                "runtime_sha256": _sha256(runtime_path),
                "change": (
                    "descriptive Unicode transliterated to ASCII; relative "
                    "filename references resolved against the verified input root"
                ),
            }
        )
    return overrides, records


def _apply_metadata_overrides(config: dict, overrides: dict) -> None:
    for input_spec in config.get("input", {}).values():
        if not isinstance(input_spec, dict):
            continue
        name = input_spec.get("name")
        if name in overrides:
            input_spec["name"] = overrides[name]


def _spinup_config(
    base: dict,
    mode: str,
    startgrid: int,
    endgrid: int | None = None,
    *,
    with_methane: bool = False,
) -> dict:
    config = deepcopy(base)
    config.update(
        {
            "sim_name": f"ExoFarm Franck 2011 natural spinup ({mode})",
            "with_methane": with_methane,
            # LPJmL 6.0.6 requires at least veg_equil_year +
            # nequilsoil * equisoil_interval = 2100 years whenever
            # equilsoil is enabled. Keep the model constraint in the pilot
            # instead of silently disabling soil equilibration.
            "nspinup": 2100 if mode == "pilot" else 3799,
            "nspinyear": 30,
            "firstyear": 1700,
            "lastyear": 1700,
            "outputyear": 1700,
            "baseyear": 1700,
            "restart": False,
            "write_restart": True,
            "write_restart_filename": "restart_1700_nv_stdfire.lpj",
            "restart_year": 1700,
            "json_config_filename": "output/resolved_config.json",
            "output": [
                {
                    "id": "globalflux",
                    "file": {"fmt": "txt", "name": "output/globalflux.csv"},
                }
            ],
        }
    )
    _use_runtime_input_path(config)
    _set_grid(config, mode, startgrid, endgrid)
    return config


def _managed_config(
    base: dict,
    *,
    mode: str,
    startgrid: int,
    endgrid: int | None,
    scenario: str,
    workflow: str,
    with_methane: bool = False,
    crop_only: bool = False,
) -> dict:
    config = deepcopy(base)
    config.update(
        {
            "sim_name": f"ExoFarm Franck 2011 {scenario} ({mode})",
            "with_methane": with_methane,
            "nspinup": 30 if mode == "pilot" else 420,
            "nspinyear": 30,
            "firstyear": 1901,
            "lastyear": 2005,
            "outputyear": 1996,
            "baseyear": 1996,
            "restart": True,
            "restart_filename": "restart_1700_nv_stdfire.lpj",
            "write_restart": False,
            "json_config_filename": "output/resolved_config.json",
            "netcdf4": False,
            "compress": 0,
            "global_netcdf": False,
            "grid_scaled": False,
            "output": [
                _output_spec(item)
                for item in (
                _outputs_with_methane(GLOBAL_A1_OUTPUTS, with_methane)
                    if workflow == "global-a1"
                    else _outputs_with_methane(GLOBAL_A0_OUTPUTS, with_methane)
                    if workflow == "global-a0-control"
                    else _outputs_with_methane(
                        CAPACITY_OUTPUTS
                        if scenario == "potential_yield_unlimited_n"
                        else ANALYSIS_OUTPUTS,
                        with_methane,
                    )
                )
            ],
        }
    )

    if scenario == "a1_2005_n":
        config.update(
            {
                "landuse": "yes",
                "with_nitrogen": "lim",
                "fertilizer_input": "yes",
                "manure_input": True,
            }
        )
    elif scenario == "a0_natural":
        config.update(
            {
                "landuse": "no",
                "population": "no",
                "with_nitrogen": "lim",
                "fertilizer_input": "no",
                "manure_input": False,
                "reservoir": False,
                "wateruse": "no",
                "river_routing": False,
                "irrigation": "no",
            }
        )
    elif scenario == "potential_yield_unlimited_n":
        config.update(
            {
                "landuse": "all_crops",
                "with_nitrogen": "unlim",
                "fertilizer_input": "auto",
                "manure_input": False,
            }
        )
    else:
        raise ValueError(f"Unknown scenario: {scenario}")

    if crop_only:
        # This branch deliberately excludes the livestock pathway.  The map
        # builder must also remove Pasture from the candidate CFT set; these
        # settings prevent a managed-grass fallback from reintroducing it.
        config.update(
            {
                "grazing": "none",
                "grazing_others": "none",
                "manure_input": False,
                "prescribe_lsuha": False,
                "others_to_crop": True,
            }
        )

    # A one-cell pilot is an interface smoke test, not a hydrological result.
    # Routing is retained only for the global campaign where river-limited
    # irrigation can be interpreted scientifically.
    if mode == "pilot" or scenario == "a0_natural":
        config.update(
            {
                "river_routing": False,
                "reservoir": False,
                "wateruse": "no",
                "irrigation": "no",
            }
        )
    else:
        config.update(
            {
                "river_routing": True,
                "reservoir": True,
                "wateruse": "all",
                "irrigation": "lim",
            }
        )

    _use_runtime_input_path(config)
    _set_grid(config, mode, startgrid, endgrid)
    return config


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lpjml-root", type=Path, required=True)
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--mode", choices=("pilot", "global"), default="pilot")
    parser.add_argument(
        "--workflow",
        choices=("franck2011", "global-a1", "global-a0-control"),
        default="franck2011",
        help=(
            "franck2011 keeps yield diagnostics; global-a1 writes agricultural "
            "N fields; global-a0-control writes monthly natural N losses."
        ),
    )
    parser.add_argument(
        "--startgrid",
        type=int,
        default=27410,
        help="Single LPJmL cell used only in pilot mode.",
    )
    parser.add_argument(
        "--endgrid",
        type=int,
        help="Last LPJmL cell in pilot mode; defaults to --startgrid.",
    )
    parser.add_argument(
        "--with-methane",
        action="store_true",
        help="Enable methane/oxygen dynamics and add monthly CH4 outputs.",
    )
    parser.add_argument(
        "--crop-only",
        action="store_true",
        help="Disable livestock/manure settings for a crop-only branch.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    lpjml_root = args.lpjml_root.resolve()
    input_root = args.input_root.resolve()
    output_dir = args.output_dir.resolve()

    spinup_base = _preprocess_upstream(lpjml_root, from_restart=False)
    managed_base = _preprocess_upstream(lpjml_root, from_restart=True)

    configs = {
        "spinup_natural": _spinup_config(
            spinup_base,
            args.mode,
            args.startgrid,
            args.endgrid,
            with_methane=args.with_methane,
        ),
    }
    if args.workflow == "global-a0-control":
        configs["a0_natural"] = _managed_config(
            managed_base,
            mode=args.mode,
            startgrid=args.startgrid,
            endgrid=args.endgrid,
            scenario="a0_natural",
            workflow=args.workflow,
            with_methane=args.with_methane,
            crop_only=args.crop_only,
        )
    else:
        configs["a1_2005_n"] = _managed_config(
            managed_base,
            mode=args.mode,
            startgrid=args.startgrid,
            endgrid=args.endgrid,
            scenario="a1_2005_n",
            workflow=args.workflow,
            with_methane=args.with_methane,
            crop_only=args.crop_only,
        )
    if args.workflow == "franck2011":
        configs["potential_yield_unlimited_n"] = _managed_config(
            managed_base,
            mode=args.mode,
            startgrid=args.startgrid,
            endgrid=args.endgrid,
            scenario="potential_yield_unlimited_n",
            workflow=args.workflow,
            with_methane=args.with_methane,
            crop_only=args.crop_only,
        )
    metadata_overrides, metadata_records = _prepare_runtime_metadata(
        input_root, output_dir
    )
    for name, config in configs.items():
        _apply_metadata_overrides(config, metadata_overrides)
        _write_json(output_dir / f"{name}.json", config)

    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=lpjml_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "lpjml_version": (lpjml_root / "VERSION").read_text().strip(),
        "lpjml_commit": commit,
        "mode": args.mode,
        "workflow": args.workflow,
        "startgrid": args.startgrid if args.mode == "pilot" else "all",
        "endgrid": (
            (args.startgrid if args.endgrid is None else args.endgrid)
            if args.mode == "pilot"
            else "all"
        ),
        "scientific_status": (
            "interface_smoke_test_not_for_interpretation"
            if args.mode == "pilot"
            else "modern_methodological_reproduction"
        ),
        "with_methane": args.with_methane,
        "crop_only": args.crop_only,
        "input_root": str(input_root),
        "runtime_metadata_compatibility_copies": metadata_records,
        "configs": sorted(f"{name}.json" for name in configs),
    }
    _write_json(output_dir / "manifest.json", manifest)


if __name__ == "__main__":
    main()
