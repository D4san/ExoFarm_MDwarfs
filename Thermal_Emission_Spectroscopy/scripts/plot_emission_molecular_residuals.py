"""Emission-track analogue of `trappist1e_pure_a0_molecular_residuals_v2`.

Three stacked panels in the curated final-products style, adapted from
transmission (transit depth, ppm) to LIFE thermal emission (observed planet
flux at 10 pc):

  1. Top    : Earth--Sun A0--A3 emission spectra, molecular-band annotations,
              LIFE band bar (4--18.5 um).
  2. Middle : N2O molecular signal per scenario (counterfactual fill) plus the
              net scenario difference Delta(A0 - Aj) as dark lines.
  3. Bottom : same for NH3.

Sign convention (emission): adding an absorber REMOVES flux, so the plotted
"mol signal" is the emission deficit  F(reset_i_to_A0) - F(full) >= 0 inside the
molecule's bands, and the net difference is F(A0) - F(Aj). Positive peaks thus
mean "flux removed by the agricultural perturbation", visually matching the
positive-ppm convention of the transmission figure.

Colours follow plot_pure_transmission_spectra.py exactly (scenario colours,
residual dark colours) so visual meaning stays stable across tracks.
Provenance: earth_20260615_pre_n2o_correction (interface validation only).
"""

import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import emission_forward as ef

CAMPAIGNS = {
    "earth_sun": ("life_earth_sun_10pc_interface_v1", "Earth–Sun", "10 pc"),
    "proxima": ("life_proxima_b_earthlike_v1", "Proxima b (Earth-like)", "1.30 pc"),
}
# Set by main() from --campaign.
FWD = None
CF = None
PLOTS = None

# Exact palette of the curated transmission residuals figure.
SCENARIO_COLOURS = {
    "A0": "#746F75",   # dim_grey
    "A1": "#56E3DB",   # scenario_cyan
    "A2": "#95E36B",   # scenario_green
    "A3": "#E34F95",   # scenario_pink
}
RESIDUAL_DARK_COLOURS = {
    "A1": "#002642",   # deep_space_blue
    "A2": "#3F633E",   # deep_moss
    "A3": "#840032",   # dark_amaranth
}
SCENARIO_NAMES = {
    "A0": "A0: Pre-agricultural scenario",
    "A1": "A1: Current Earth",
    "A2": "A2: Moderate ExoFarm",
    "A3": "A3: Extreme ExoFarm",
}
FILL_ORDER = ("A3", "A2", "A1")
FILL_ALPHA = {"A3": 0.72, "A2": 0.82, "A1": 0.92}
DARK_ALPHA = {"A3": 0.58, "A2": 0.68, "A1": 0.68}

LIFE_MIN, LIFE_MAX = 4.0, 18.5
DISPLAY_R = 200
TOP_SCALE = 1e-20      # W m^-2 um^-1
RES_SCALE = 1e-21      # W m^-2 um^-1

BAND_ANNOTATIONS = [
    (r"N$_2$O", 7.8), (r"NH$_3$", 10.6), (r"N$_2$O", 17.0),
    (r"O$_3$", 9.6), (r"CO$_2$", 15.0), (r"H$_2$O", 6.3),
]


def _style():
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["STIX Two Text", "STIXGeneral", "Times New Roman"],
        "mathtext.fontset": "stix", "figure.dpi": 140,
        "axes.linewidth": 0.8,
    })


def log_rebin(wl, y, R=DISPLAY_R):
    edges = [wl[0]]
    while edges[-1] < wl[-1]:
        edges.append(edges[-1] * (1 + 1.0 / R))
    edges = np.asarray(edges)
    idx = np.digitize(wl, edges)
    c, v = [], []
    for b in range(1, len(edges)):
        m = idx == b
        if m.any():
            c.append(wl[m].mean())
            v.append(y[m].mean())
    return np.asarray(c), np.asarray(v)


def load_full(s):
    d = np.load(FWD / f"{s}_emission.npz")
    return d["wl_um"], d["Fp_obs_W_m2_m"] * 1e-6      # -> W m^-2 um^-1


def load_reset(s, sp):
    d = np.load(CF / f"{s}_reset_{sp}_Fp_obs.npz")
    return d["Fp_obs_W_m2_m"] * 1e-6                  # -> W m^-2 um^-1


def main():
    global FWD, CF, PLOTS
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign", choices=list(CAMPAIGNS), default="earth_sun")
    args = ap.parse_args()
    campaign_id, target_name, dist_label = CAMPAIGNS[args.campaign]
    out_dir = ef.REPO / "Thermal_Emission_Spectroscopy" / "outputs" / campaign_id
    FWD = out_dir / "forward_emission"
    CF = out_dir / "molecular_diagnostics"
    PLOTS = out_dir / "plots"

    _style()
    PLOTS.mkdir(parents=True, exist_ok=True)

    # Native spectra (shared wl grid across all products).
    wl, F = {}, {}
    for s in ["A0", "A1", "A2", "A3"]:
        wl_native, F[s] = load_full(s)
    wl_b = None
    Fb = {}
    for s in F:
        wl_b, Fb[s] = log_rebin(wl_native, F[s])
    band = (wl_b >= LIFE_MIN) & (wl_b <= LIFE_MAX)

    # Molecular signals (emission deficit, >= 0 in bands) and net differences.
    mol_sig, net_diff = {}, {}
    for s in ["A1", "A2", "A3"]:
        _, net = log_rebin(wl_native, F["A0"] - F[s])
        net_diff[s] = net
        for sp in ["N2O", "NH3"]:
            deficit = load_reset(s, sp) - F[s]
            _, mol_sig[(s, sp)] = log_rebin(wl_native, deficit)

    # Auto-scale the y-axes to the target brightness (Earth-Sun ~1e-20;
    # Proxima ~100x closer -> ~1e-18). Round to the enclosing power of ten.
    def _pow10(x):
        return 10.0 ** np.floor(np.log10(x)) if x > 0 else 1.0
    band0 = (wl_b >= LIFE_MIN) & (wl_b <= LIFE_MAX)
    top_scale = _pow10(np.nanmax(Fb["A0"][band0]))
    sig_peak = max(np.nanmax(np.abs(mol_sig[(s, sp)][band0]))
                   for s in ["A1", "A2", "A3"] for sp in ["N2O", "NH3"])
    res_scale = _pow10(sig_peak)
    top_exp = int(np.round(np.log10(top_scale)))
    res_exp = int(np.round(np.log10(res_scale)))
    TOP_SCALE = top_scale
    RES_SCALE = res_scale

    fig, (ax_top, ax_n2o, ax_nh3) = plt.subplots(
        3, 1, figsize=(10.6, 7.6), sharex=True,
        gridspec_kw={"height_ratios": [2.85, 1.0, 1.0]},
    )

    # ---- top panel: spectra with scenario fills over A0 -------------------
    for s in FILL_ORDER:
        ax_top.fill_between(
            wl_b[band], Fb["A0"][band] / TOP_SCALE, Fb[s][band] / TOP_SCALE,
            color=SCENARIO_COLOURS[s], alpha=FILL_ALPHA[s], lw=0,
        )
        ax_top.plot(wl_b[band], Fb[s][band] / TOP_SCALE,
                    color=SCENARIO_COLOURS[s], lw=1.1,
                    label=SCENARIO_NAMES[s])
    ax_top.plot(wl_b[band], Fb["A0"][band] / TOP_SCALE,
                color=SCENARIO_COLOURS["A0"], lw=0.9,
                label=SCENARIO_NAMES["A0"])

    y_max = np.nanmax(Fb["A0"][band]) / TOP_SCALE
    for name, wl_c in BAND_ANNOTATIONS:
        if LIFE_MIN < wl_c < LIFE_MAX:
            ax_top.text(wl_c, y_max * 1.04, name, ha="center", va="bottom",
                        fontsize=8.5, color="0.25")
    ax_top.set_ylim(0, y_max * 1.22)
    ax_top.set_ylabel(rf"$F_p$ @ {dist_label}" "\n"
                      rf"($10^{{{top_exp}}}$ W m$^{{-2}}$ $\mu$m$^{{-1}}$)",
                      fontsize=11)
    # LIFE band bar (analogue of the NIRSpec/MIRI bars).
    ax_top.plot([LIFE_MIN, LIFE_MAX], [y_max * 0.045] * 2,
                color="#5B4763", lw=2.4, solid_capstyle="butt")
    ax_top.text((LIFE_MIN + LIFE_MAX) / 2, y_max * 0.075, "LIFE 4–18.5 µm",
                ha="center", fontsize=8, color="#5B4763")
    ax_top.legend(frameon=False, fontsize=8.6, ncol=2, loc="upper left")

    # ---- residual panels ---------------------------------------------------
    for ax, sp, label in [(ax_n2o, "N2O", r"N$_2$O signal"),
                          (ax_nh3, "NH3", r"NH$_3$ signal")]:
        for s in FILL_ORDER:
            ax.fill_between(
                wl_b[band], 0.0, mol_sig[(s, sp)][band] / RES_SCALE,
                color=SCENARIO_COLOURS[s], alpha=FILL_ALPHA[s], lw=0,
                label=rf"A$_{s[1]}$ mol signal",
            )
        for s in FILL_ORDER:
            ax.plot(
                wl_b[band], net_diff[s][band] / RES_SCALE,
                color=RESIDUAL_DARK_COLOURS[s], lw=0.9, alpha=DARK_ALPHA[s],
                label=rf"$\Delta$(A$_0$ $-$ A$_{s[1]}$)",
            )
        ax.axhline(0.0, color="0.4", lw=0.6, ls=":")
        ax.text(0.012, 0.86, label, transform=ax.transAxes, fontsize=10)
        ax.set_ylabel(rf"$\Delta F_p$" "\n"
                      rf"($10^{{{res_exp}}}$ W m$^{{-2}}$ $\mu$m$^{{-1}}$)",
                      fontsize=10)
    ax_n2o.legend(frameon=False, fontsize=6.8, ncol=3, loc="upper right")

    ax_nh3.set_xlim(LIFE_MIN, LIFE_MAX)
    ax_nh3.set_xlabel(r"Wavelength ($\mu$m)", fontsize=12)
    fig.suptitle("ExoFarm thermal-emission spectra and molecular residuals\n"
                 f"({target_name} @ {dist_label}; campaign {campaign_id})",
                 fontsize=11.5)
    fig.tight_layout(rect=(0, 0, 1, 0.965))

    out = PLOTS / f"emission_molecular_residuals_{args.campaign}.png"
    fig.savefig(out, bbox_inches="tight")
    print(f"saved {out.relative_to(ef.REPO)}")


if __name__ == "__main__":
    main()
