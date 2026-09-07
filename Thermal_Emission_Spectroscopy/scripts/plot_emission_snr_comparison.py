"""Emission-track analogue of `trappist1e_net_molecular_snr_comparison`.

Two stacked panels, adapted from transmission (number of transits) to LIFE
thermal emission (integration time):

  (a) Peak molecular-excess S/N per spectral feature. Marker shape encodes the
      scenario (A1 circle, A2 square, A3 triangle — same as the curated
      transmission figure); colour encodes the integration time
      (10 h cyan, 100 h green, 1000 h violet — the transmission figure used the
      same colours for 1/10/100 transits). Features are the LIFE-band peaks
      identified in the S/N table: N2O 7.8 um, N2O 17.0 um, NH3 10.7 um.

  (b) Integration time required to reach fixed S/N thresholds (3 and 5) for the
      strongest A3 features, using the verified photon-noise scaling
      S/N(t) = S/N(10 h) * sqrt(t / 10 h).

Reads lifesim/life_classic_binned_products.npz. SNR here is the band-peak
|dF|/sigma DIAGNOSTIC (not a detection). Provenance:
earth_20260615_pre_n2o_correction (interface validation only).
"""

import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import emission_forward as ef

# Campaign is chosen at runtime (--campaign). Default = Layer-1 Earth--Sun.
CAMPAIGNS = {
    "earth_sun": ("life_earth_sun_10pc_interface_v1", "Earth--Sun"),
    "proxima": ("life_proxima_b_earthlike_v1", "Proxima"),
}

# Features: (species, band window um, axis label)
FEATURES = [
    ("N2O", (7.5, 8.1), "7.8 $\\mu$m\n(N$_2$O)"),
    ("N2O", (16.5, 17.5), "17.0 $\\mu$m\n(N$_2$O)"),
    ("NH3", (9.5, 11.5), "10.7 $\\mu$m\n(NH$_3$)"),
]
N2O_NH3_SEPARATOR_X = 1.5     # between the 2nd and 3rd feature slots

SCENARIOS = {
    "A1": {"offset": -0.20, "marker": "o", "label": "A1 Current Earth", "size": 130},
    "A2": {"offset": 0.00, "marker": "s", "label": "A2 Moderate ExoFarm", "size": 120},
    "A3": {"offset": 0.20, "marker": "^", "label": "A3 Extreme ExoFarm", "size": 140},
}
TIME_STYLES = {
    10.0: {"color": "#56E3DB", "label": "10 h"},      # scenario_cyan
    100.0: {"color": "#95E36B", "label": "100 h"},    # scenario_green
    1000.0: {"color": "#BD62E3", "label": "1000 h"},  # scenario_violet
}
C_N2O = "#8E5651"   # terracotta_mauve (same role as in the transmission figure)
C_NH3 = "#5B4763"   # charcoal_violet
THRESHOLDS = [(3.0, "--"), (5.0, "-.")]


def _style():
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["STIX Two Text", "STIXGeneral", "Times New Roman"],
        "mathtext.fontset": "stix", "figure.dpi": 140,
    })


def peak_snr_10h(d, scenario, species, window):
    """Peak |dF|/sigma inside the band window at the reference 10 h."""
    wl = d["wl_bins_um"]
    m = (wl >= window[0]) & (wl <= window[1])
    dF = np.abs(d[f"dF_{scenario}_{species}"])
    sigma = d[f"sigma_{scenario}"]
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where((sigma > 0) & np.isfinite(sigma), dF / sigma, 0.0)
    return float(np.nanmax(r[m]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign", choices=list(CAMPAIGNS), default="earth_sun")
    args = ap.parse_args()
    campaign_id, target_label = CAMPAIGNS[args.campaign]
    out = ef.REPO / "Thermal_Emission_Spectroscopy" / "outputs" / campaign_id
    products = out / "lifesim" / "life_classic_binned_products.npz"
    plots = out / "plots"

    _style()
    plots.mkdir(parents=True, exist_ok=True)
    d = np.load(products, allow_pickle=True)
    t_ref = float(d["t_ref_hours"])
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9.4, 10.4),
                                   gridspec_kw={"height_ratios": [1.15, 1.0]})

    # ---------------- panel (a): peak S/N per feature ----------------------
    top_snr_values = []
    for fx, (species, window, _) in enumerate(FEATURES):
        for s_key, s_sty in SCENARIOS.items():
            snr10 = peak_snr_10h(d, s_key, species, window)
            for t_h, t_sty in TIME_STYLES.items():
                snr_t = snr10 * np.sqrt(t_h / t_ref)
                top_snr_values.append(snr_t)
                ax1.scatter(
                    fx + s_sty["offset"],
                    snr_t,
                    color=t_sty["color"], marker=s_sty["marker"],
                    s=s_sty["size"], edgecolors="#222222",
                    linewidths=0.8, zorder=5,
                )
    ax1.set_yscale("log")
    # Keep the log axis close to the actual points while leaving headroom for
    # the highest marker and the molecular-region labels.
    top_y_min = min(top_snr_values) / 2.0
    top_y_max = max(top_snr_values) * 1.35
    ax1.set_ylim(top_y_min, top_y_max)
    # Label intermediate values on the logarithmic axis so the vertical
    # separation between nearby S/N points is easier to read.
    top_tick_exponents = np.arange(
        np.floor(np.log10(top_y_min)),
        np.ceil(np.log10(top_y_max)) + 1,
    )
    top_ticks = np.array([
        multiplier * 10.0 ** exponent
        for exponent in top_tick_exponents
        for multiplier in (1.0, 2.0, 5.0)
    ])
    top_ticks = top_ticks[(top_ticks >= top_y_min) & (top_ticks <= top_y_max)]
    ax1.set_yticks(top_ticks)
    ax1.set_yticklabels([f"{tick:g}" for tick in top_ticks])
    ax1.set_xticks(range(len(FEATURES)))
    ax1.set_xticklabels([f[2] for f in FEATURES])
    ax1.set_xlim(-0.6, len(FEATURES) - 0.4)
    ax1.set_ylabel("Peak molecular-excess S/N")
    ax1.set_xlabel("Spectral feature", labelpad=8)
    ax1.grid(True, which="both", linestyle=":", color="#dddddd", alpha=0.7, zorder=1)
    ax1.axvline(N2O_NH3_SEPARATOR_X, color="#888888", linestyle="--",
                linewidth=1.2, alpha=0.5, zorder=2)
    ax1.text(0.5, 1.3, r"N$_2$O bands", color="#444444", fontsize=10,
             fontstyle="italic", ha="center", weight="semibold")
    ax1.text(2.0, 1.3, r"NH$_3$ band", color="#444444", fontsize=10,
             fontstyle="italic", ha="center", weight="semibold")

    leg_scen = [plt.Line2D([0], [0], marker=s["marker"], color="w",
                           label=s["label"], markerfacecolor="#888888",
                           markeredgecolor="#222222", markersize=10,
                           linestyle="None")
                for s in SCENARIOS.values()]
    leg_time = [plt.Line2D([0], [0], marker="o", color="w",
                           label=t["label"], markerfacecolor=t["color"],
                           markeredgecolor="#222222", markersize=10,
                           linestyle="None")
                for t in TIME_STYLES.values()]
    l1 = ax1.legend(handles=leg_scen, loc="lower left", bbox_to_anchor=(0.02, 0.05),
                    title="Scenario", frameon=True, facecolor="#ffffff",
                    edgecolor="#dddddd", framealpha=0.9, fontsize=9)
    l1.get_title().set_weight("bold")
    ax1.add_artist(l1)
    l2 = ax1.legend(handles=leg_time, loc="lower left", bbox_to_anchor=(0.40, 0.05),
                    title="Integration time", frameon=True, facecolor="#ffffff",
                    edgecolor="#dddddd", framealpha=0.9, fontsize=9)
    l2.get_title().set_weight("bold")
    ax1.set_title("(a) Peak molecular S/N relative to the pre-agricultural baseline",
                  fontsize=12, pad=12, fontweight="bold")

    # ---------------- panel (b): hours to fixed S/N in A3 ------------------
    snr10_n2o = peak_snr_10h(d, "A3", "N2O", FEATURES[0][1])
    snr10_nh3 = peak_snr_10h(d, "A3", "NH3", FEATURES[2][1])
    # The useful projection range ends at a few hundred hours; extending the
    # axis to 1e8 h leaves a large empty tail after both curves leave the panel.
    hours = np.logspace(0, 3, 400)
    for snr10, colr, lbl in [(snr10_n2o, C_N2O, r"N$_2$O 7.8 $\mu$m"),
                             (snr10_nh3, C_NH3, r"NH$_3$ 10.7 $\mu$m")]:
        snr_t = snr10 * np.sqrt(hours / t_ref)
        ax2.plot(hours, snr_t, color=colr, lw=2.4, label=lbl, zorder=3)
        for thr, _ls in THRESHOLDS:
            t_cross = t_ref * (thr / snr10) ** 2
            if hours[0] <= t_cross <= hours[-1]:
                ax2.scatter([t_cross], [thr], marker="D", s=70, color=colr,
                            edgecolors="#222222", zorder=5)
                ax2.annotate(f"{t_cross:,.0f} h",
                             xy=(t_cross, thr), xytext=(t_cross * 0.55, thr + 0.28),
                             fontsize=8.5, color=colr,
                             bbox=dict(boxstyle="round,pad=0.22", fc="white",
                                       ec=colr, alpha=0.9))
    for thr, ls in THRESHOLDS:
        ax2.axhline(thr, color="#E34F95", linestyle=ls, lw=1.2, alpha=0.85)
        ax2.text(220, thr + 0.1, f"S/N = {thr:g}", color="#E34F95", fontsize=9)
    ax2.set_xscale("log")
    ax2.set_xlim(1, 1e3)
    ax2.set_ylim(0, 6.2)
    ax2.set_xlabel("Integration time [h]")
    ax2.set_ylabel("Peak molecular-excess S/N")
    ax2.grid(True, which="both", linestyle=":", color="#dddddd", alpha=0.7)
    ax2.legend(title="A3 molecular feature", frameon=True, facecolor="#ffffff",
               edgecolor="#dddddd", framealpha=0.9, fontsize=9,
               title_fontproperties={"weight": "bold"}, loc="upper left")
    ax2.set_title("(b) Integration time required to reach fixed S/N thresholds in A3",
                  fontsize=12, pad=12, fontweight="bold")

    fig.suptitle(f"LIFE S/N projections — {target_label}", fontsize=11, y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.985))
    out_png = plots / f"life_classic_snr_comparison_{args.campaign}.png"
    out_pdf = plots / f"life_classic_snr_comparison_{args.campaign}.pdf"
    fig.savefig(out_png, bbox_inches="tight")
    fig.savefig(out_pdf, bbox_inches="tight")
    print(f"saved {out_png.relative_to(ef.REPO)}")
    print(f"saved {out_pdf.relative_to(ef.REPO)}")


if __name__ == "__main__":
    main()
