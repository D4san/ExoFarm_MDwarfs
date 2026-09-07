"""A3 molecular signals vs LIFE noise floor at several integration times.

Upgrade of the single-time signal-vs-noise diagnostic: the 1-sigma noise floor
is drawn for a set of integration times (10 h, 100 h, 1000 h). In the classic
photon-noise-dominated case sigma scales exactly as 1/sqrt(t) (verified against
direct get_spectrum calls in run_life_snr_classic.py), so the extra curves are
scaled from the saved 10 h products rather than re-simulated.

Reads lifesim/life_classic_binned_products.npz written by run_life_snr_classic.py.
Provenance: earth_20260615_pre_n2o_correction (interface validation only).
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import argparse

import emission_forward as ef

CAMPAIGNS = {
    "earth_sun": ("life_earth_sun_10pc_interface_v1", "10 pc, LIFE baseline"),
    "proxima": ("life_proxima_b_earthlike_v1", "1.30 pc, LIFE X scene"),
}

SCENARIO = "A3"
TARGETS = {"N2O": "#1f77b4", "NH3": "#ff7f0e"}   # shared molecular colours
NOISE_TIMES_H = [10.0, 100.0, 1000.0]
NOISE_GREYS = ["0.65", "0.45", "0.25"]           # lighter = shorter time


def _style():
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["STIX Two Text", "STIXGeneral", "Times New Roman"],
        "mathtext.fontset": "stix", "figure.dpi": 140,
    })


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign", choices=list(CAMPAIGNS), default="earth_sun")
    args = ap.parse_args()
    campaign_id, scene_note = CAMPAIGNS[args.campaign]
    out = ef.REPO / "Thermal_Emission_Spectroscopy" / "outputs" / campaign_id
    products = out / "lifesim" / "life_classic_binned_products.npz"
    plots = out / "plots"

    _style()
    plots.mkdir(parents=True, exist_ok=True)
    d = np.load(products, allow_pickle=True)
    wl_um = d["wl_bins_um"]
    t_ref = float(d["t_ref_hours"])
    sigma_ref = d[f"sigma_{SCENARIO}"]
    provenance = str(d["provenance"]) if "provenance" in d else campaign_id

    fig, ax = plt.subplots(figsize=(9.2, 5.2))

    for t_h, grey in zip(NOISE_TIMES_H, NOISE_GREYS):
        sigma_t = sigma_ref * np.sqrt(t_ref / t_h)
        ax.plot(wl_um, sigma_t, color=grey, lw=1.2,
                label=rf"LIFE 1$\sigma$ noise, {t_h:g} h")
        ax.fill_between(wl_um, 0, sigma_t, color=grey, alpha=0.035, lw=0)

    for sp, colr in TARGETS.items():
        dF = np.abs(d[f"dF_{SCENARIO}_{sp}"])
        ax.plot(wl_um, dF, color=colr, lw=1.8, zorder=3,
                label=rf"{sp} signal |$\Delta F$|")

    ax.set_yscale("log")
    ax.set_xlim(4, 18.5)
    ax.set_ylim(bottom=1e-4)
    ax.set_xlabel(r"Wavelength [$\mu$m]", fontsize=12)
    ax.set_ylabel(r"Photon flux density [ph m$^{-2}$ s$^{-1}$ m$^{-1}$]",
                  fontsize=11)
    short_target = "Earth–Sun" if args.campaign == "earth_sun" else "Proxima"
    ax.set_title(f"A3 molecular signals and LIFE noise — {short_target}",
                 fontsize=12, pad=10)
    ax.legend(frameon=False, fontsize=8.5, loc="lower center", ncol=2)
    ax.grid(alpha=0.12, which="both", color="#02040F")
    fig.text(0.01, 0.012,
             f"Classic photon-noise model | {scene_note} | {provenance} | S/N diagnostic",
             fontsize=6.5, color="0.45")
    fig.tight_layout(rect=(0, 0.035, 1, 1))

    out_png = plots / f"life_classic_A3_signal_vs_noise_times_{args.campaign}.png"
    fig.savefig(out_png, bbox_inches="tight")
    print(f"saved {out_png.relative_to(ef.REPO)}")


if __name__ == "__main__":
    main()
