"""Posterior-based separation of each ExoFarm scenario from the A0 baseline.

Reads the POSEIDON retrieval posteriors of the LIFE campaign matrix and answers
the campaign question rigorously (the S/N diagnostic in
campaigns_to_differentiate.py is the fast version of the same question):

    separation(Aj vs A0) = |mu_j - mu_0| / sqrt(sigma_j^2 + sigma_0^2)     [sigma]

with mu, sigma the median and 1-sigma width of the retrieved log-abundance
posterior. Because posterior widths shrink as sqrt(t) in the photon-noise
regime, the complementary comparison uses the effective A0 pressure-column
reference, and the number of campaigns of the same length needed to reach a
target separation is

    n_campaigns = (target_sigma / separation_1campaign)^2

Caveats propagated to every number: diagonal LIFEsim-classic noise (no
instrumental covariance), one noise realization per dataset, isochemical
retrieval against vertically structured VULCAN truth (retrieved values are
column-like averages), Proxima is a controlled Earth-like analogue.
"""

import csv
import math
from pathlib import Path

import numpy as np

from retrieval_reference import log10_column_averaged_mixing_ratio


REPO = Path(__file__).resolve().parents[2]
PROFILES_DIR = REPO / "Transmission_Spectroscopy" / "profiles"

CAMPAIGN_ID = "life_proxima_b_earthlike_v1"
RESULTS = (REPO / "Thermal_Emission_Spectroscopy" / "outputs" / CAMPAIGN_ID /
           "retrievals" / "POSEIDON_output" / "proxima_b_earthlike" /
           "retrievals" / "samples")
OUT = REPO / "Thermal_Emission_Spectroscopy" / "outputs" / "_comparison"

SCENARIOS = ["A1", "A2", "A3"]
HOURS = [10, 240]
SPECIES = ["log_N2O", "log_NH3"]
TARGET_SIGMA = 3.0

# Two complementary distinguishability metrics are reported, because in the
# pre-agricultural baseline the target molecules are often too weak to measure
# (the retrieval returns an upper limit with a very wide posterior):
#   (a) posterior-vs-posterior: |mu_j - mu_0| / sqrt(s_j^2 + s_0^2). Conservative
#       and assumption-free, but dominated by the wide A0 posterior.
#   (b) posterior-vs-A0-effective: |mu_j - A0_eff| / s_j. Answers "does an
#       observation of Aj exclude the pre-agricultural abundance?", using the
#       pressure-column scalar comparable to the isochemical retrieval.
# The retrieval uses constant-with-height abundances, so the comparison value
# must map the vertical VULCAN profile into the same scalar space.  Reuse the
# project's pressure-column average rather than selecting one arbitrary layer.
A0_REFERENCE_PROFILE = PROFILES_DIR / "Proxima_b_A0_PreAgri_chem.txt"
A0_PROFILE = np.genfromtxt(A0_REFERENCE_PROFILE, names=True)


def load_posterior(scenario, hours):
    """Return {param: samples} for one retrieval, or None if missing."""
    tag = f"proxima_{scenario}_{hours}h"
    path = RESULTS / f"{tag}_{tag}_samples.txt"
    if not path.exists():
        return None
    with open(path) as fh:
        names = [n.strip() for n in fh.readline().split("|")]
    data = np.loadtxt(path, skiprows=1)
    return {n: data[:, i] for i, n in enumerate(names)}


def effective_A0_reference(species):
    """Return log10 of the pressure-column-averaged A0 VULCAN abundance."""
    return log10_column_averaged_mixing_ratio(A0_PROFILE, species)


def summarize(samples):
    """Median and symmetric 1-sigma half-width of a posterior."""
    lo, med, hi = np.percentile(samples, [15.865, 50.0, 84.135])
    return med, 0.5 * (hi - lo)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for hours in HOURS:
        post0 = load_posterior("A0", hours)
        if post0 is None:
            print(f"[skip] A0 {hours}h aún no disponible")
            continue
        for scen in SCENARIOS:
            post = load_posterior(scen, hours)
            if post is None:
                print(f"[skip] {scen} {hours}h aún no disponible")
                continue
            for sp in SPECIES:
                mu0, s0 = summarize(post0[sp])
                mu, s = summarize(post[sp])
                sep = abs(mu - mu0) / math.sqrt(s0**2 + s**2)
                n_camp = math.inf if sep <= 0 else (TARGET_SIGMA / sep) ** 2
                # Metric (b): does the Aj observation exclude the effective A0
                # reference in the scalar space used by the isochemical fit?
                reference0 = effective_A0_reference(sp.replace("log_", ""))
                signed_sep = ((mu - reference0) / s) if s > 0 else 0.0
                n_camp_t = (math.inf if signed_sep <= 0
                            else (TARGET_SIGMA / signed_sep) ** 2)

                # A separation is only meaningful if the scenario posterior is
                # an actual MEASUREMENT (not an upper limit) AND the offset has
                # the physical sign: every ExoFarm scenario ADDS N2O/NH3 over
                # A0, so a median below the effective A0 reference is a
                # prior-driven artefact of an unconstrained posterior, not
                # evidence of a difference.
                measured = s < 0.5                      # dex; wider => upper limit
                direction_ok = signed_sep > 0.0
                valid = bool(measured and direction_ok)

                def fmt(n):
                    return ("1" if n <= 1 else
                            (f"{math.ceil(n):,}" if np.isfinite(n) else "inf"))

                rows.append({
                    "hours": hours, "scenario": scen,
                    "species": sp.replace("log_", ""),
                    "A0_median": round(mu0, 3), "A0_sigma": round(s0, 3),
                    "scen_median": round(mu, 3), "scen_sigma": round(s, 3),
                    "A0_effective": round(reference0, 3),
                    "sep_vs_A0posterior": round(sep, 2),
                    "campaigns_3sig_vs_posterior": fmt(n_camp),
                    "signed_sep_vs_A0effective": round(signed_sep, 2),
                    "campaigns_3sig_vs_effective": fmt(n_camp_t) if valid else "n/a",
                    "measured": measured, "direction_ok": direction_ok,
                    "verdict": ("distinguible" if valid and signed_sep >= 3
                                else "medido, insuficiente" if valid
                                else "límite superior (no medido)"),
                })

    if not rows:
        print("[abort] no hay retrievals completos todavía")
        return

    csv_path = OUT / "retrieval_separation_from_A0.csv"
    with open(csv_path, "w", newline="") as fh:
        w = csv.DictWriter(
            fh,
            fieldnames=list(rows[0].keys()),
            lineterminator="\n",
        )
        w.writeheader(); w.writerows(rows)

    print("=== Separación respecto de A0 (retrievals LIFE, Proxima b) ===")
    print("(a) vs posterior de A0 (conservador)   (b) vs referencia A0 efectiva\n")
    print(f"{'t[h]':>5} {'esc':>4} {'mol':>4} {'Aj log±σ':>16} {'A0 post±σ':>16} "
          f"{'A0 eff.':>8} {'(b)σ':>6} {'camps':>6}  {'veredicto':<26}")
    for r in rows:
        print(f"{r['hours']:>5} {r['scenario']:>4} {r['species']:>4} "
              f"{r['scen_median']:>8}±{r['scen_sigma']:<7} "
              f"{r['A0_median']:>8}±{r['A0_sigma']:<7} "
              f"{r['A0_effective']:>8} "
              f"{r['signed_sep_vs_A0effective']:>6} {r['campaigns_3sig_vs_effective']:>6}  "
              f"{r['verdict']:<26}")
    print(f"\n[csv] {csv_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
