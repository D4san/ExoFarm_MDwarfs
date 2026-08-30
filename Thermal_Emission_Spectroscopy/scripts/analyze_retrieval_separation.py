"""Posterior-based separation of each ExoFarm scenario from the A0 baseline.

Reads the POSEIDON retrieval posteriors of the LIFE campaign matrix and answers
the campaign question rigorously (the S/N diagnostic in
campaigns_to_differentiate.py is the fast version of the same question):

    separation(Aj vs A0) = |mu_j - mu_0| / sqrt(sigma_j^2 + sigma_0^2)     [sigma]

with mu, sigma the median and 1-sigma width of the retrieved log-abundance
posterior. Because posterior widths shrink as sqrt(t) in the photon-noise
regime, the number of campaigns of the same length needed to reach a target
separation is

    n_campaigns = (target_sigma / separation_1campaign)^2

Caveats propagated to every number: diagonal LIFEsim-classic noise (no
instrumental covariance), one noise realization per dataset, isochemical
retrieval against vertically structured VULCAN truth (retrieved values are
column-like averages), Proxima is a controlled Earth-like analogue.
"""

import csv
import math

import numpy as np

import emission_forward as ef

CAMPAIGN_ID = "life_proxima_b_earthlike_v1"
RESULTS = (ef.REPO / "Thermal_Emission_Spectroscopy" / "outputs" / CAMPAIGN_ID /
           "retrievals" / "POSEIDON_output" / "proxima_b_earthlike" /
           "retrievals" / "samples")
OUT = ef.REPO / "Thermal_Emission_Spectroscopy" / "outputs" / "_comparison"

SCENARIOS = ["A1", "A2", "A3"]
HOURS = [10, 240]
SPECIES = ["log_N2O", "log_NH3"]
TARGET_SIGMA = 3.0

# Two complementary distinguishability metrics are reported, because in the
# pre-agricultural baseline the target molecules are often too weak to measure
# (the retrieval returns an upper limit with a very wide posterior):
#   (a) posterior-vs-posterior: |mu_j - mu_0| / sqrt(s_j^2 + s_0^2). Conservative
#       and assumption-free, but dominated by the wide A0 posterior.
#   (b) posterior-vs-A0-truth: |mu_j - truth_A0| / s_j. Answers "does an
#       observation of Aj exclude the pre-agricultural abundance?", the question
#       a real campaign would pose against a specific hypothesis.
# Truth values are the surface (1 bar) mixing ratios of the VULCAN A0 profile.
TRUTH_A0_PROFILE = (ef.PROFILES_DIR / "Proxima_b_A0_PreAgri_chem.txt")


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


def truth_A0_surface(species):
    """log10 of the A0 surface (1 bar) mixing ratio for one species."""
    with open(TRUTH_A0_PROFILE) as fh:
        header = fh.readline().split()[1:]
    data = np.loadtxt(TRUTH_A0_PROFILE, skiprows=1)
    i_layer = int(np.argmin(np.abs(data[:, 0] - 1.0)))
    return float(np.log10(data[i_layer, 1 + header.index(species)]))


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
                # Metric (b): does the Aj observation exclude A0's true abundance?
                truth0 = truth_A0_surface(sp.replace("log_", ""))
                sep_truth = abs(mu - truth0) / s if s > 0 else 0.0
                n_camp_t = (math.inf if sep_truth <= 0
                            else (TARGET_SIGMA / sep_truth) ** 2)

                # A separation is only meaningful if the scenario posterior is
                # an actual MEASUREMENT (not an upper limit) AND the offset has
                # the physical sign: every ExoFarm scenario ADDS N2O/NH3 over
                # A0, so a median below the A0 truth is a prior-driven artefact
                # of an unconstrained posterior, not evidence of a difference.
                measured = s < 0.5                      # dex; wider => upper limit
                direction_ok = mu > truth0
                valid = bool(measured and direction_ok)

                def fmt(n):
                    return ("1" if n <= 1 else
                            (f"{math.ceil(n):,}" if np.isfinite(n) else "inf"))

                rows.append({
                    "hours": hours, "scenario": scen,
                    "species": sp.replace("log_", ""),
                    "A0_median": round(mu0, 3), "A0_sigma": round(s0, 3),
                    "scen_median": round(mu, 3), "scen_sigma": round(s, 3),
                    "A0_truth": round(truth0, 3),
                    "sep_vs_A0posterior": round(sep, 2),
                    "campaigns_3sig_vs_posterior": fmt(n_camp),
                    "sep_vs_A0truth": round(sep_truth, 2),
                    "campaigns_3sig_vs_truth": fmt(n_camp_t) if valid else "n/a",
                    "measured": measured, "direction_ok": direction_ok,
                    "verdict": ("distinguible" if valid and sep_truth >= 3
                                else "medido, insuficiente" if valid
                                else "límite superior (no medido)"),
                })

    if not rows:
        print("[abort] no hay retrievals completos todavía")
        return

    csv_path = OUT / "retrieval_separation_from_A0.csv"
    with open(csv_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    print("=== Separación respecto de A0 (retrievals LIFE, Proxima b) ===")
    print("(a) vs posterior de A0 (conservador)   (b) vs abundancia verdadera de A0\n")
    print(f"{'t[h]':>5} {'esc':>4} {'mol':>4} {'Aj log±σ':>16} {'A0 post±σ':>16} "
          f"{'A0 real':>8} {'(b)σ':>6} {'camps':>6}  {'veredicto':<26}")
    for r in rows:
        print(f"{r['hours']:>5} {r['scenario']:>4} {r['species']:>4} "
              f"{r['scen_median']:>8}±{r['scen_sigma']:<7} "
              f"{r['A0_median']:>8}±{r['A0_sigma']:<7} "
              f"{r['A0_truth']:>8} "
              f"{r['sep_vs_A0truth']:>6} {r['campaigns_3sig_vs_truth']:>6}  "
              f"{r['verdict']:<26}")
    print(f"\n[csv] {csv_path.relative_to(ef.REPO)}")


if __name__ == "__main__":
    main()
