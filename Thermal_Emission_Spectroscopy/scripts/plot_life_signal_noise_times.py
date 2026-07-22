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

import emission_forward as ef

CAMPAIGN_ID = "life_earth_sun_10pc_interface_v1"
OUT = ef.REPO / "Thermal_Emission_Spectroscopy" / "outputs" / CAMPAIGN_ID
PRODUCTS = OUT / "lifesim" / "life_classic_binned_products.npz"
PLOTS = OUT / "plots"

SCENARIO = "A3"
TARGETS = {"N2O": "#1f77b4", "NH3": "#ff7f0e"}   # shared molecular colours
NOISE_TIMES_H = [10.0, 100.0, 1000.0]
NOISE_GREYS = ["0.75", "0.55", "0.30"]           # lighter = shorter time


def _style():
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["STIX Two Text", "STIXGeneral", "Times New Roman"],
        "mathtext.fontset": "stix", "figure.dpi": 140,
    })


def main():
    _style()
    PLOTS.mkdir(parents=True, exist_ok=True)
    d = np.load(PRODUCTS, allow_pickle=True)
    wl_um = d["wl_bins_um"]
    t_ref = float(d["t_ref_hours"])
    sigma_ref = d[f"sigma_{SCENARIO}"]

    fig, ax = plt.subplots(figsize=(9.2, 5.2))

    for t_h, grey in zip(NOISE_TIMES_H, NOISE_GREYS):
        sigma_t = sigma_ref * np.sqrt(t_ref / t_h)
        ax.plot(wl_um, sigma_t, color=grey, lw=1.3,
                label=rf"LIFE 1$\sigma$ noise, {t_h:g} h")
        ax.fill_between(wl_um, 0, sigma_t, color=grey, alpha=0.10, lw=0)

    for sp, colr in TARGETS.items():
        dF = np.abs(d[f"dF_{SCENARIO}_{sp}"])
        ax.plot(wl_um, dF, color=colr, lw=1.5,
                label=rf"|$\Delta F$| {sp} (A3 $-$ reset)")

    ax.set_yscale("log")
    ax.set_xlim(4, 18.5)
    ax.set_ylim(bottom=1e-4)
    ax.set_xlabel(r"Wavelength [$\mu$m]", fontsize=12)
    ax.set_ylabel(r"Photon flux density [ph m$^{-2}$ s$^{-1}$ m$^{-1}$]",
                  fontsize=11)
    ax.set_title("A3 ExoFarm molecular signals vs LIFE noise floor "
                 "(classic, photon noise)\n"
                 f"noise bands for 10 / 100 / 1000 h; interface benchmark, "
                 f"{ef.PROVENANCE_LABEL}", fontsize=9.5)
    ax.legend(frameon=False, fontsize=8.5, loc="lower center", ncol=2)
    ax.grid(alpha=0.12, which="both", color="#02040F")
    fig.tight_layout()

    out = PLOTS / "life_classic_A3_signal_vs_noise_times.png"
    fig.savefig(out, bbox_inches="tight")
    print(f"saved {out.relative_to(ef.REPO)}")


if __name__ == "__main__":
    main()
