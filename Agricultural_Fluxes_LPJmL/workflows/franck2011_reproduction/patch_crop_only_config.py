#!/usr/bin/env python3
"""Patch a frozen LPJmL config to consume a crop-only CLM land-use map.

The map is an operational input to the Genghis Khan branch.  Keeping this
small patch separate makes the generated scientific config auditable: the
Franck candidate config remains untouched and only the land-use source,
calendar year, and pilot/global grid selector are changed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--landuse-meta", type=Path, required=True)
    parser.add_argument("--year", type=int, default=2005)
    parser.add_argument("--startgrid", default="all")
    parser.add_argument("--endgrid", default="all")
    args = parser.parse_args()

    config = json.loads(args.source.read_text(encoding="utf-8"))
    config.update(
        {
            "landuse": "only_crops",
            "landuse_year_const": args.year,
            "fix_landuse": False,
            "startgrid": (
                int(args.startgrid) if args.startgrid != "all" else "all"
            ),
            "endgrid": int(args.endgrid) if args.endgrid != "all" else "all",
        }
    )
    landuse = config.setdefault("input", {}).setdefault("landuse", {})
    landuse["name"] = str(args.landuse_meta.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
