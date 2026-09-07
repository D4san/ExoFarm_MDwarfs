"""Emission-track analogue of `trappist1e_pure_a0_molecular_residuals_v2`.

Three stacked panels in the curated final-products style, adapted from
transmission (transit depth, ppm) to LIFE thermal emission (observed planet
flux at 10 pc):

  1. Top    : A0--A3 emission spectra, molecular-band labels across the LIFE
              band (4--18.5 um).
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
DARK_ALPHA = {"A3": 0.78, "A2": 0.82, "A1": 0.82}

LIFE_MIN, LIFE_MAX = 4.0, 18.5
DISPLAY_R = 200
TOP_SCALE = 1e-20      # W m^-2 um^-1
RES_SCALE = 1e-21      # W m^-2 um^-1

BAND_ANNOTATIONS = (
    (7.8, 7.65, r"N$_2$O", 0.12),
    (10.6, 10.6, r"NH$_3$", 0.12),
    (17.0, 17.0, r"N$_2$O", 0.10),
)


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


def style_emission_axis(ax):
    """Match the transmission-figure axes without changing the observable."""
    ax.set_xlim(LIFE_MIN, LIFE_MAX)
    ax.set_xticks([4, 5, 6, 8, 10, 12, 14, 16, 18])
    ax.tick_params(direction="in", top=True, right=True)
    ax.minorticks_on()


def annotate_top_molecular_regions(ax, wavelengths, spectra):
    """Place direct molecular labels above the local spectral envelope."""
    envelope = np.maximum.reduce([spectra[key] for key in ["A0", "A1", "A2", "A3"]])
    for wavelength, label_x, label, y_offset in BAND_ANNOTATIONS:
        y_value = np.interp(wavelength, wavelengths, envelope)
        ax.text(
            label_x,
            y_value + y_offset,
            label,
            color="black",
            fontsize=13,
            fontfamily="serif",
            ha="center",
            va="bottom",
            zorder=20,
        )


def annotate_life_coverage(ax, y_position, y_step):
    """Show the single LIFE coverage interval without molecular guide lines."""
    ax.hlines(
        y_position,
        LIFE_MIN,
        LIFE_MAX,
        color="#5B4763",
        linewidth=2.8,
        zorder=18,
    )
    ax.text(
        (LIFE_MIN + LIFE_MAX) / 2,
        y_position + 0.48 * y_step,
        "LIFE 4–18.5 µm",
        color="black",
        fontsize=10,
        fontfamily="serif",
        ha="center",
        va="bottom",
        zorder=19,
    )


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
        3, 1, figsize=(13.8, 9.6), sharex=True, constrained_layout=True,
        gridspec_kw={"height_ratios": [2.85, 1.0, 1.0]},
    )

    # ---- top panel: spectra with scenario fills over A0 -------------------
    for s in FILL_ORDER:
        ax_top.fill_between(
            wl_b[band], Fb["A0"][band] / TOP_SCALE, Fb[s][band] / TOP_SCALE,
            color=SCENARIO_COLOURS[s], lw=0,
        )
        line_width = {"A3": 1.7, "A2": 1.9, "A1": 2.1}[s]
        ax_top.plot(wl_b[band], Fb[s][band] / TOP_SCALE,
                    color=SCENARIO_COLOURS[s], lw=line_width,
                    label=SCENARIO_NAMES[s])
    ax_top.plot(wl_b[band], Fb["A0"][band] / TOP_SCALE,
                color=SCENARIO_COLOURS["A0"], lw=1.15,
                label=SCENARIO_NAMES["A0"])

    top_arrays = [Fb[key][band] / TOP_SCALE for key in ["A0", "A1", "A2", "A3"]]
    top_min = min(np.nanmin(values) for values in top_arrays)
    top_max = max(np.nanmax(values) for values in top_arrays)
    top_span = top_max - top_min
    top_pad = max(0.28, 0.18 * top_span)
    annotate_top_molecular_regions(
        ax_top,
        wl_b[band],
        {key: Fb[key][band] / TOP_SCALE for key in ["A0", "A1", "A2", "A3"]},
    )
    annotate_life_coverage(
        ax_top,
        y_position=top_min - 0.82 * top_pad,
        y_step=0.18 * top_pad,
    )
    style_emission_axis(ax_top)
    ax_top.tick_params(axis="both", labelsize=14)
    ax_top.set_ylim(top_min - top_pad, top_max + top_pad)
    ax_top.set_ylabel(
        "Observed planetary flux "
        rf"$F_p$" "\n"
        rf"[$10^{{{top_exp}}}$ W m$^{{-2}}$ $\mu$m$^{{-1}}$]",
        fontsize=16,
        fontfamily="serif",
        color="black",
    )
    ax_top.set_title(
        "Proxima thermal-emission spectra\nand molecular residuals",
        fontfamily="serif",
        loc="center",
        fontsize=22,
        color="black",
        pad=14,
    )
    ax_top.legend(frameon=False, fontsize=13, ncol=2, loc="upper left")

    # ---- residual panels ---------------------------------------------------
    for ax, sp, label in [(ax_n2o, "N2O", r"N$_2$O signal"),
                          (ax_nh3, "NH3", r"NH$_3$ signal")]:
        for s in FILL_ORDER:
            ax.fill_between(
                wl_b[band], 0.0, mol_sig[(s, sp)][band] / RES_SCALE,
                color=SCENARIO_COLOURS[s], lw=0,
                label=rf"A$_{s[1]}$ mol signal",
            )
        for s in FILL_ORDER:
            ax.plot(
                wl_b[band], net_diff[s][band] / RES_SCALE,
                color=RESIDUAL_DARK_COLOURS[s], lw=1.05, alpha=DARK_ALPHA[s],
                label=rf"$\Delta$(A$_0$ $-$ A$_{s[1]}$)",
            )
        ax.axhline(0.0, color="0.4", lw=0.6, ls=":")
        style_emission_axis(ax)
        ax.tick_params(axis="both", labelsize=14)
        ax.text(
            0.015,
            0.84,
            label,
            transform=ax.transAxes,
            color="black",
            fontsize=13,
            fontfamily="serif",
            ha="left",
            va="top",
        )
        ax.set_ylabel(
            rf"$\Delta F_p$" "\n"
            rf"($10^{{{res_exp}}}$ W m$^{{-2}}$ $\mu$m$^{{-1}}$)",
            fontsize=13,
            fontfamily="serif",
            color="black",
        )
    ax_n2o.legend(frameon=False, fontsize=9.5, ncol=3, loc="upper left",
                  bbox_to_anchor=(0.36, 0.98))

    ax_nh3.set_xlabel("Wavelength [µm]", fontfamily="serif", fontsize=17,
                      color="black")

    out = PLOTS / f"emission_molecular_residuals_{args.campaign}.png"
    out_pdf = PLOTS / f"emission_molecular_residuals_{args.campaign}.pdf"
    fig.savefig(out, dpi=240, bbox_inches="tight")
    fig.savefig(out_pdf, bbox_inches="tight")
    print(f"saved {out.relative_to(ef.REPO)}")
    print(f"saved {out_pdf.relative_to(ef.REPO)}")


if __name__ == "__main__":
    main()
