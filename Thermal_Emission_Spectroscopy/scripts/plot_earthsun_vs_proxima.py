"""Earth--Sun (10 pc) vs Proxima b (1.30 pc): the LIFE detectability contrast.

The headline Stage-III comparison: the SAME ExoFarm N2O/NH3 perturbation, run
through the SAME emission + LIFEsim-classic machinery, is dramatically more
detectable around the nearest star (Proxima, 1.30 pc, LIFE X scene) than around
a Sun analogue at 10 pc (LIFE baseline) — almost entirely a proximity effect.

Reads the saved per-bin products of both campaigns and draws:
  (a) band-integrated molecular-signal S/N at 10 h for A1/A2/A3, grouped by
      feature, Earth-Sun vs Proxima (log y);
  (b) integration time to reach S/N=5 for the A3 features, both targets (log y).

SNR is a diagnostic, not a detection. Earth-Sun profiles are the frozen
pre-N2O-correction set; Proxima uses the corrected active BC — so the contrast
is dominated by distance, with a secondary photochemistry/BC difference noted in
the report.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import emission_forward as ef

OUTROOT = ef.REPO / "Thermal_Emission_Spectroscopy" / "outputs"
CAMPAIGNS = {
    "Earth–Sun (10 pc)": "life_earth_sun_10pc_interface_v1",
    "Proxima b (1.30 pc)": "life_proxima_b_earthlike_v1",
}
CAMP_COLOUR = {"Earth–Sun (10 pc)": "#56E3DB", "Proxima b (1.30 pc)": "#E34F95"}

FEATURES = [("N2O", (7.5, 8.1), "N$_2$O\n7.8 µm"),
            ("N2O", (16.5, 17.5), "N$_2$O\n17 µm"),
            ("NH3", (9.5, 11.5), "NH$_3$\n10.6 µm")]
REF_HOURS = 10.0
PLOTS = OUTROOT / "_comparison"


def _style():
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["STIX Two Text", "STIXGeneral", "Times New Roman"],
        "mathtext.fontset": "stix", "figure.dpi": 140, "axes.linewidth": 0.8,
    })


def load(campaign_id):
    return np.load(OUTROOT / campaign_id / "lifesim" /
                   "life_classic_binned_products.npz", allow_pickle=True)


def band_snr(d, scenario, species, window):
    wl = d["wl_bins_um"]
    m = (wl >= window[0]) & (wl <= window[1])
    dF = d[f"dF_{scenario}_{species}"]
    sigma = d[f"sigma_{scenario}"]
    per = np.where((sigma > 0) & np.isfinite(sigma), dF / sigma, 0.0)
    return float(np.sqrt(np.nansum(per[m] ** 2)))


def main():
    _style()
    PLOTS.mkdir(parents=True, exist_ok=True)
    data = {name: load(cid) for name, cid in CAMPAIGNS.items()}

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9.6, 9.4),
                                   gridspec_kw={"height_ratios": [1.05, 1.0]})

    # ---- (a) band SNR @10h, A3, grouped by feature, both targets -----------
    x = np.arange(len(FEATURES))
    w = 0.38
    for k, (name, d) in enumerate(data.items()):
        vals = [band_snr(d, "A3", sp, win) for sp, win, _ in FEATURES]
        bars = ax1.bar(x + (k - 0.5) * w, vals, w, color=CAMP_COLOUR[name],
                       edgecolor="#222", linewidth=0.7, label=name, zorder=3)
        for xi, v in zip(x + (k - 0.5) * w, vals):
            ax1.text(xi, v * 1.08, f"{v:.2f}", ha="center", va="bottom",
                     fontsize=8, color="#333")
    ax1.axhline(5, color="#840032", ls="-.", lw=1.1)
    ax1.text(len(FEATURES) - 0.5, 5.3, "S/N=5", color="#840032", fontsize=8.5, ha="right")
    ax1.axhline(3, color="#840032", ls="--", lw=1.0)
    ax1.text(len(FEATURES) - 0.5, 3.15, "S/N=3", color="#840032", fontsize=8.5, ha="right")
    ax1.set_yscale("log")
    ax1.set_xticks(x); ax1.set_xticklabels([f[2] for f in FEATURES])
    ax1.set_ylabel("Band-integrated molecular-signal S/N (A3, 10 h)")
    ax1.set_title("(a) Same ExoFarm signal, two hosts: A3 molecular S/N in 10 h",
                  fontsize=12, fontweight="bold", pad=10)
    ax1.legend(frameon=False, fontsize=10, loc="upper left")
    ax1.grid(axis="y", which="both", ls=":", color="#ddd", alpha=0.7, zorder=0)

    # ---- (b) hours to S/N=5 for A3, both targets ---------------------------
    for k, (name, d) in enumerate(data.items()):
        hours = []
        for sp, win, _ in FEATURES:
            s10 = band_snr(d, "A3", sp, win)
            hours.append(REF_HOURS * (5.0 / s10) ** 2 if s10 > 0 else np.inf)
        bars = ax2.bar(x + (k - 0.5) * w, hours, w, color=CAMP_COLOUR[name],
                       edgecolor="#222", linewidth=0.7, label=name, zorder=3)
        for xi, h in zip(x + (k - 0.5) * w, hours):
            txt = f"{h:,.0f} h" if h < 1e5 else f"{h:.1e} h"
            ax2.text(xi, h * 1.15, txt, ha="center", va="bottom", fontsize=8, color="#333")
    ax2.set_yscale("log")
    ax2.set_xticks(x); ax2.set_xticklabels([f[2] for f in FEATURES])
    ax2.set_ylabel("Integration time to reach S/N=5 (A3) [h]")
    ax2.set_title("(b) Time to a S/N=5 diagnostic: proximity turns years into hours",
                  fontsize=12, fontweight="bold", pad=10)
    ax2.legend(frameon=False, fontsize=10, loc="upper left")
    ax2.grid(axis="y", which="both", ls=":", color="#ddd", alpha=0.7, zorder=0)
    # reference lines: 100 h (a feasible single LIFE visit) and 1 yr
    ax2.axhline(100, color="#3F633E", ls="-", lw=0.9, alpha=0.7)
    ax2.text(-0.45, 118, "100 h (feasible visit)", color="#3F633E", fontsize=8)
    ax2.axhline(8760, color="#5B4763", ls="-", lw=0.9, alpha=0.7)
    ax2.text(-0.45, 10200, "1 yr", color="#5B4763", fontsize=8)

    fig.suptitle("LIFE thermal-emission detectability of the ExoFarm N$_2$O/NH$_3$ "
                 "signature: Earth–Sun @10 pc vs Proxima b @1.30 pc\n"
                 "(LIFEsim classic, photon noise; S/N is a diagnostic, not a detection; "
                 "Earth–Sun = pre-N2O-correction set)", fontsize=9.5, y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    out = PLOTS / "earthsun_vs_proxima_life_snr.png"
    fig.savefig(out, bbox_inches="tight")
    print(f"saved {out.relative_to(ef.REPO)}")


if __name__ == "__main__":
    main()
