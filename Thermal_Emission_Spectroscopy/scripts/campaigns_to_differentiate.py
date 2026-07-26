"""How many LIFE campaigns are needed to separate each ExoFarm scenario from A0?

Uses the validated band-integrated molecular-signal S/N diagnostic (counterfactual
signal over the LIFEsim-classic per-bin noise) together with the verified
sqrt(t) photon-noise scaling. For a campaign of duration t_camp, the S/N after
n campaigns is

    S/N(n) = S/N(t_camp) * sqrt(n)

so the number of campaigns needed to reach a threshold S/N_target is

    n = (S/N_target / S/N(t_camp))^2       (rounded up)

Campaign lengths follow docs/life_retrieval_campaign_design_2026-07-25.md
(literature-anchored): short 10 h (LIFE X), standard 240 h ~10 d (LIFE XII
M-dwarf case), extreme 1200 h = 50 d (LIFE XII / LIFE III).

This is a DIAGNOSTIC of distinguishability, not a detection claim, and it
assumes diagonal photon-noise sigma (no instrumental covariance).
"""

import csv
import math

import numpy as np

import emission_forward as ef

CAMPAIGNS = {
    "proxima": "life_proxima_b_earthlike_v1",
    "earth_sun": "life_earth_sun_10pc_interface_v1",
}
BANDS = {
    "N2O": [(7.5, 8.1), (16.5, 17.5)],
    "NH3": [(9.5, 11.5)],
}
CAMPAIGN_HOURS = {"short (10 h)": 10.0, "standard (240 h)": 240.0,
                  "extreme (1200 h)": 1200.0}
REF_HOURS = 10.0
THRESHOLDS = [3.0, 5.0]


def band_snr(d, scen, sp, windows, hours):
    wl = d["wl_bins_um"]
    mask = np.zeros_like(wl, dtype=bool)
    for lo, hi in windows:
        mask |= (wl >= lo) & (wl <= hi)
    dF = d[f"dF_{scen}_{sp}"]
    sigma = d[f"sigma_{scen}"] * math.sqrt(REF_HOURS / hours)
    per = np.where((sigma > 0) & np.isfinite(sigma), dF / sigma, 0.0)
    return float(np.sqrt(np.nansum(per[mask] ** 2)))


def main():
    rows = []
    for camp_key, camp_id in CAMPAIGNS.items():
        path = (ef.REPO / "Thermal_Emission_Spectroscopy" / "outputs" / camp_id /
                "lifesim" / "life_classic_binned_products.npz")
        if not path.exists():
            continue
        d = np.load(path, allow_pickle=True)
        scenarios = [s for s in ("A1", "A2", "A3") if f"dF_{s}_N2O" in d]
        for scen in scenarios:
            for sp, windows in BANDS.items():
                for cname, chours in CAMPAIGN_HOURS.items():
                    snr1 = band_snr(d, scen, sp, windows, chours)
                    row = {"target": camp_key, "scenario": scen, "molecule": sp,
                           "campaign": cname, "SNR_1_campaign": round(snr1, 3)}
                    for thr in THRESHOLDS:
                        n = math.inf if snr1 <= 0 else (thr / snr1) ** 2
                        row[f"n_campaigns_SNR{int(thr)}"] = (
                            "inf" if not np.isfinite(n) else
                            (f"{math.ceil(n):,}" if n >= 1 else "1"))
                        row[f"hours_SNR{int(thr)}"] = (
                            "inf" if not np.isfinite(n) else f"{n * chours:,.0f}")
                    rows.append(row)

    out = ef.REPO / "Thermal_Emission_Spectroscopy" / "outputs" / "_comparison"
    out.mkdir(parents=True, exist_ok=True)
    csv_path = out / "campaigns_to_differentiate_A0.csv"
    with open(csv_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    # Human-readable summary for the standard campaign.
    print("=== ¿Cuántas campañas para separar cada escenario de A0? ===")
    print("(campaña estándar = 240 h ~ 10 días, ancla LIFE XII)\n")
    print(f"{'objetivo':10s} {'esc':4s} {'mol':4s} {'S/N 1 camp':>11s} "
          f"{'camps→3σ':>9s} {'camps→5σ':>9s} {'horas→5σ':>12s}")
    for r in rows:
        if r["campaign"] != "standard (240 h)":
            continue
        print(f"{r['target']:10s} {r['scenario']:4s} {r['molecule']:4s} "
              f"{r['SNR_1_campaign']:>11} {r['n_campaigns_SNR3']:>9} "
              f"{r['n_campaigns_SNR5']:>9} {r['hours_SNR5']:>12}")
    print(f"\n[csv] {csv_path.relative_to(ef.REPO)}  ({len(rows)} filas)")


if __name__ == "__main__":
    main()
