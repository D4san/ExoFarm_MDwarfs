"""Apply the approved LIFE narrative to the existing manuscript in place."""

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGE = Path(__file__).resolve().parent
TARGET = Path("E:/Down/ExoFarms_Photochemistry_v2.tex")
BIB = Path("E:/Down/reference.bib")
EXPECTED = {
    TARGET: "cf56a1d4bd9f6d4705cd5a21acb7d8d27287213514e8600b9934738bf54cbe68",
    BIB: "35b1d2c14ef82e0cbac0254733bea96680416d6b3926ce8596f42da0dcab00b5",
}
TABLES = ROOT / "Thermal_Emission_Spectroscopy/final_products/tables"
REGIONS = ROOT / (
    "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/"
    "tables/a1_regions_2026-10-15"
)


def checksum(data):
    return hashlib.sha256(data).hexdigest()


def load_rows(path):
    with path.open(encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def tables():
    loo = load_rows(TABLES / "life_proxima_loo_lnB_sigma_lin_2026-10-10.csv")
    lookup = {(r["scenario"], int(r["hours"]), r["excluded_species"]): r for r in loo}
    if len(lookup) != 36 or len(loo) != 36:
        raise ValueError("Unexpected omission matrix")
    molecules = ("H2O", "CO2", "CH4", "O3", "N2O", "NH3")
    loo_lines, region_lines = [], []
    marginal = load_rows(REGIONS / "marginal.csv")
    joint = load_rows(REGIONS / "joint.csv")
    m = {(r["scenario"], int(r["hours"]), r["species"]): r for r in marginal}
    j = {(r["scenario"], int(r["hours"])): r for r in joint}
    if len(m) != 12 or len(j) != 6:
        raise ValueError("Unexpected region matrix")
    for hours in (1, 10, 100):
        for scenario in ("A1", "A3"):
            rows = [lookup[(scenario, hours, species)] for species in molecules]
            ln_b = [f"${float(r['delta_lnb']):.2f}\\pm{float(r['delta_lnb_numeric_error']):.2f}$" for r in rows]
            sigma = [f"{float(r['sigma_lin_convention']):.2f}" if r["sigma_status"] == "calibrated" else "---" for r in rows]
            loo_lines.append(" & ".join([str(hours), scenario, r"$\ln B$", *ln_b]) + r" \\")
            loo_lines.append(" & ".join(["", "", r"$\sigma_{\mathrm{cal}}$", *sigma]) + r" \\")
            cells = [str(hours), scenario]
            for r, field in [
                (m[(scenario, hours, "N2O")], "p_ge_a1"),
                (m[(scenario, hours, "NH3")], "p_ge_a1"),
                (j[(scenario, hours)], "p_both_ge_a1"),
            ]:
                q = float(r[field])
                probability = r"$\simeq0$" if q == 0 else (r"$\simeq100$" if q == 1 else f"{100*q:.2f}")
                k = f"{float(r['K_nominal']):.3g}" if r["K_nominal"] else "---"
                log_k = f"{float(r['ln_K_nominal']):.3f}" if r["ln_K_nominal"] else "---"
                cells.extend((probability, k, log_k))
            region_lines.append(" & ".join(cells) + r" \\")
    return "\n".join(loo_lines), "\n".join(region_lines)


def main(apply):
    originals = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        if checksum(originals[path]) != expected:
            raise ValueError(f"Source changed since inspection: {path}")
    source = originals[TARGET].decode("utf-8-sig").replace("\r\n", "\n")
    bibliography = originals[BIB].decode("utf-8-sig").replace("\r\n", "\n")
    loo_table, region_table = tables()
    replacement = (STAGE / "results_fragment.tex").read_text(encoding="utf-8")
    replacement = replacement.replace("@@LOO_ROWS@@", loo_table).replace("@@REGION_ROWS@@", region_table)
    start = source.index("At 1 h, neither nitrogen-bearing species is strongly constrained.")
    end = source.index("\n\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%", start)
    source = source[:start] + replacement.rstrip() + source[end:]
    old_description = (
        "The quantity $z^{\\mathrm{desc}}$ expresses the displacement of the posterior median from the effective A0 abundance in units of the central posterior half-width. For approximately Gaussian and symmetric posteriors, it can be interpreted as an approximate sigma-equivalent separation from the A0 reference. We use it here as a descriptive measure of how strongly an inferred ExoFarm abundance departs from the pre-agricultural atmospheric state."
    )
    new_description = (
        "The quantity $z^{\\mathrm{desc}}$ expresses how far the posterior median lies from the effective A0 abundance relative to the central posterior half-width. It describes the recovered shift conditional on this retrieval model. The full posterior and evidence comparisons below assess the lower-abundance tails and the support for alternative atmospheric descriptions."
    )
    if source.count(old_description) != 1:
        raise ValueError("Descriptive paragraph anchor changed")
    source = source.replace(old_description, new_description)
    source = source.replace("omitted from the atlas for compactness.", "omitted from the figure for compactness.")
    discussion_anchor = "\\section{Discussion}\\label{sec:disc}\n"
    if source.count(discussion_anchor) != 1:
        raise ValueError("Ambiguous discussion anchor")
    discussion = (STAGE / "discussion_fragment.tex").read_text(encoding="utf-8")
    source = source.replace(discussion_anchor, discussion_anchor + "\n" + discussion)
    appendix = (STAGE / "references_append.bib").read_text(encoding="utf-8")
    new_keys = re.findall(r"@article\{([^,]+),", appendix)
    for key in new_keys:
        if re.search(r"@\w+\{" + re.escape(key) + r"\s*,", bibliography):
            raise ValueError(f"Citation already exists: {key}")
    bibliography = bibliography.rstrip() + "\n\n" + appendix.strip() + "\n"
    labels = re.findall(r"\\label\{([^}]+)\}", replacement + discussion)
    if len(labels) != len(set(labels)) or "@@" in source:
        raise ValueError("Duplicate labels or unexpanded table markers")
    for key in new_keys:
        if key not in source:
            raise ValueError("Unused added citation")
    # Preserve each target's original BOM and newline convention.
    proposed = {}
    for path, content in ((TARGET, source), (BIB, bibliography)):
        if b"\r\n" in originals[path]:
            content = content.replace("\n", "\r\n")
        encoding = "utf-8-sig" if originals[path].startswith(b"\xef\xbb\xbf") else "utf-8"
        proposed[path] = content.encode(encoding)
    record = {
        "target": str(TARGET), "new_labels": labels, "new_citations": new_keys,
        "loo_comparisons": 36, "posterior_cases": 6,
        "before_sha256": {str(p): checksum(b) for p, b in originals.items()},
        "after_sha256": {str(p): checksum(b) for p, b in proposed.items()},
        "bytes_added": {str(p): len(proposed[p])-len(originals[p]) for p in proposed},
        "applied": apply,
    }
    if apply:
        for path, data in originals.items():
            (STAGE / (path.name + ".original.bin")).write_bytes(data)
        for path, data in proposed.items():
            if checksum(path.read_bytes()) != EXPECTED[path]:
                raise ValueError("Concurrent target modification")
            path.write_bytes(data)
            if path.read_bytes() != data:
                raise ValueError("Saved bytes differ")
    (STAGE / "change_record.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    main(parser.parse_args().apply)
