"""Plot the A0--A3 thermal-emission spectra for a LIFE campaign.

Phase-3 step 2: "generate the spectrum with the signals". Reads the noise-free
POSEIDON forward products saved by ``run_layer1_forward.py`` and draws the four
scenarios across the LIFE mid-IR band, using compact molecular labels rather
than vertical guide lines.

Provenance: earth_20260615_pre_n2o_correction (interface validation only).
"""

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import emission_forward as ef

CAMPAIGNS = {
    "earth_sun": ("life_earth_sun_10pc_interface_v1", "Earth--Sun", "10 pc"),
    "proxima": ("life_proxima_b_earthlike_v1", "Proxima b (Earth-like)", "1.30 pc"),
}
# Set by main() from --campaign.
FORWARD_DIR = None
PLOTS_DIR = None

# Scenario colours: exact hex from the shared project palette
# (Transmission_Spectroscopy/notebooks/exofarm_plot_style.py). Kept literal here
# to keep the Stage III branch self-contained; meanings are unchanged.
SCENARIO_COLOUR = {
    "A0": "#95E36B",  # scenario_green  - pre-agricultural
    "A1": "#56E3DB",  # scenario_cyan   - current Earth
    "A2": "#BD62E3",  # scenario_violet - moderate ExoFarm
    "A3": "#E34F95",  # scenario_pink   - extreme ExoFarm
}
SCENARIO_NAME = {
    "A0": "A0 pre-agri", "A1": "A1 current",
    "A2": "A2 moderate", "A3": "A3 extreme",
}

# Diagnostic mid-IR band centres (um) for annotation. N2O/NH3 are the ExoFarm
# targets; the rest are overlap controls. The third value staggers the two
# labels near 7.7--7.8 um without adding guide lines.
BAND_LABELS = [
    ("H$_2$O", 6.3, 1.03),
    ("CH$_4$", 7.7, 1.04),
    ("N$_2$O", 7.8, 1.13),
    ("O$_3$", 9.6, 1.03),
    ("NH$_3$", 10.5, 1.13),
    ("CO$_2$", 15.0, 1.03),
    ("N$_2$O", 17.0, 1.13),
]

# LIFE nominal science band.
LIFE_MIN, LIFE_MAX = 4.0, 18.5


def _apply_style():
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["STIX Two Text", "STIXGeneral", "Times New Roman"],
        "mathtext.fontset": "stix",
        "axes.linewidth": 0.8,
        "figure.dpi": 130,
    })


def log_rebin(wl, y, R=120):
    """Boxcar-average onto a log-spaced grid of resolving power R (display only)."""
    edges = [wl[0]]
    while edges[-1] < wl[-1]:
        edges.append(edges[-1] * (1 + 1.0 / R))
    edges = np.array(edges)
    idx = np.digitize(wl, edges)
    centres, vals = [], []
    for b in range(1, len(edges)):
        m = idx == b
        if m.any():
            centres.append(wl[m].mean())
            vals.append(y[m].mean())
    return np.array(centres), np.array(vals)


def load(scenario):
    d = np.load(FORWARD_DIR / f"{scenario}_emission.npz")
    return d["wl_um"], d["Fp_Fs"], d["Fp_obs_W_m2_m"]


def main():
    global FORWARD_DIR, PLOTS_DIR
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign", choices=list(CAMPAIGNS), default="earth_sun")
    ap.add_argument("--quantity", choices=["Fp_obs", "Fp_Fs"], default="Fp_obs")
    ap.add_argument("--R", type=int, default=120)
    args = ap.parse_args()
    campaign_id, target_name, dist_label = CAMPAIGNS[args.campaign]
    out_dir = ef.REPO / "Thermal_Emission_Spectroscopy" / "outputs" / campaign_id
    FORWARD_DIR = out_dir / "forward_emission"
    PLOTS_DIR = out_dir / "plots"

    _apply_style()
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10.2, 5.6))
    ymax = 0.0
    for key in ["A0", "A1", "A2", "A3"]:
        wl, Fp_Fs, Fp_obs = load(key)
        y = Fp_obs if args.quantity == "Fp_obs" else Fp_Fs
        if args.quantity == "Fp_obs":
            y = y * 1e-6            # W m^-2 m^-1 -> W m^-2 um^-1
        wl_b, y_b = log_rebin(wl, y, args.R)
        band = (wl_b >= LIFE_MIN) & (wl_b <= LIFE_MAX)
        ax.plot(wl_b[band], y_b[band], color=SCENARIO_COLOUR[key],
                lw=1.4, label=SCENARIO_NAME[key])
        ymax = max(ymax, np.nanmax(y_b[band]))

    for name, wl_c, y_factor in BAND_LABELS:
        if LIFE_MIN <= wl_c <= LIFE_MAX:
            ax.text(wl_c, ymax * y_factor, name, va="bottom", ha="center",
                    fontsize=7.8, color="#57635E")

    ax.set_xlim(LIFE_MIN, LIFE_MAX)
    ax.set_ylim(0, ymax * 1.18)
    ax.set_xlabel(r"Wavelength [$\mu$m]")
    if args.quantity == "Fp_obs":
        ax.set_ylabel(r"Observed planet flux $F_p$ [W m$^{-2}$ $\mu$m$^{-1}$]")
    else:
        ax.set_ylabel(r"$F_p/F_s$")
    short_target = "Earth–Sun" if args.campaign == "earth_sun" else "Proxima"
    ax.set_title(f"{short_target} emission spectrum (A0–A3)", fontsize=12,
                 pad=10)
    ax.legend(frameon=False, fontsize=8.6, loc="upper right", ncol=2)
    fig.text(0.01, 0.012,
             f"LIFE 4–18.5 µm | {target_name} | S/N diagnostic",
             fontsize=7, color="0.45")
    fig.tight_layout(rect=(0, 0.035, 1, 1))

    out = PLOTS_DIR / f"emission_A0A3_{args.quantity}.png"
    fig.savefig(out, bbox_inches="tight")
    print(f"saved {out.relative_to(ef.REPO)}")


if __name__ == "__main__":
    main()
