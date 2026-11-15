"""Emission-track analogue of `trappist1e_pure_a0_molecular_residuals_v2`.

Three stacked panels in the curated final-products style, adapted from
transmission (transit depth, ppm) to LIFE thermal emission (observed planet
flux at the target distance):

  1. Top    : A0--A3 emission spectra, molecular-band labels across the LIFE
              band (4--18.5 um), without observational noise overlays.
  2. Middle : N2O molecular signal per scenario (counterfactual fill) plus the
              net scenario difference Delta(A0 - Aj) as dark lines. When LIFE
              datasets are supplied, their fixed-range +/-1-sigma noise curves
              are overlaid here.
  3. Bottom : same for NH3, including the same LIFE noise curves.

Sign convention (emission): adding an absorber REMOVES flux, so the plotted
"mol signal" is the emission deficit  F(reset_i_to_A0) - F(full) >= 0 inside the
molecule's bands, and the net difference is F(A0) - F(Aj). Positive peaks thus
mean "flux removed by the agricultural perturbation", visually matching the
positive-ppm convention of the transmission figure.

Colours follow plot_pure_transmission_spectra.py exactly (scenario colours,
residual dark colours) so visual meaning stays stable across tracks.
For the Earth--Sun target, the forward products retain the
earth_20260615_pre_n2o_correction interface-validation caveat. The Proxima
products come from the separate LIFE Proxima branch.
"""

import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D


REPO = Path(__file__).resolve().parents[2]

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
LIFE_HOUR_COLOURS = {
    1: "#B54B19",    # rusty_spice
    10: "#002642",   # deep_space_blue
    100: "#3F633E",  # deep_moss
}

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


def load_observations(path):
    """Read the four-column LIFE direct-emission table and validate its units."""
    rows = np.loadtxt(path, skiprows=1, ndmin=2)
    if rows.shape[1] != 4:
        raise ValueError(
            f"Expected 4 LIFE columns (wavelength, half-bin, Fp, sigma_Fp), "
            f"found {rows.shape[1]} in {path}"
        )
    wavelength_um, half_bin_um, fp_per_m, sigma_per_m = rows.T
    if not np.all(np.isfinite(rows)):
        raise ValueError(f"Non-finite LIFE values in {path}")
    if np.any(half_bin_um <= 0) or np.any(sigma_per_m <= 0):
        raise ValueError(
            f"LIFE bin widths and flux uncertainties must be positive: {path}"
        )
    return wavelength_um, half_bin_um, fp_per_m * 1e-6, sigma_per_m * 1e-6


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    global FWD, CF, PLOTS
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign", choices=list(CAMPAIGNS), default="earth_sun")
    ap.add_argument(
        "--observations",
        type=Path,
        nargs="+",
        help=(
            "Optional LIFE datasets. Their +/-1-sigma noise curves are drawn "
            "on the two molecular-signal panels, with the signal limits fixed. "
            "Columns: wavelength [um], half-bin [um], Fp and sigma_Fp "
            "[W m^-2 m^-1]."
        ),
    )
    ap.add_argument(
        "--observations-label",
        nargs="+",
        help="Legend label for the LIFE data (defaults to the filename).",
    )
    ap.add_argument(
        "--output-suffix",
        help="Optional suffix to preserve the existing default figure files.",
    )
    args = ap.parse_args()
    campaign_id, target_name, dist_label = CAMPAIGNS[args.campaign]
    out_dir = REPO / "Thermal_Emission_Spectroscopy" / "outputs" / campaign_id
    FWD = out_dir / "forward_emission"
    CF = out_dir / "molecular_diagnostics"
    PLOTS = out_dir / "plots"

    observation_paths = []
    observations = []
    observation_labels = []
    labels_supplied = args.observations_label is not None
    if args.observations is not None:
        observation_paths = [
            (path if path.is_absolute() else REPO / path).resolve()
            for path in args.observations
        ]
        for path in observation_paths:
            if not path.is_file():
                raise FileNotFoundError(f"LIFE dataset not found: {path}")
            observations.append(load_observations(path))
        if args.observations_label is None:
            observation_labels = [
                path.stem.replace("_", " ") for path in observation_paths
            ]
        elif len(args.observations_label) != len(observation_paths):
            raise ValueError(
                "Give one --observations-label per --observations file"
            )
        else:
            observation_labels = list(args.observations_label)

        # These three integration-time products are meant to occupy the same
        # LIFE channel centres, so fail loudly if their grids drift apart.
        reference_wl, reference_half_bin = observations[0][:2]
        for path, observation in zip(observation_paths[1:], observations[1:]):
            if not np.array_equal(reference_wl, observation[0]) or not np.array_equal(
                reference_half_bin, observation[1]
            ):
                raise ValueError(
                    "LIFE integrations must share wavelength centres and bin "
                    f"widths to overlay them without horizontal offsets: {path}"
                )

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
    ax_top.legend(
        frameon=False,
        fontsize=11.5,
        ncol=2,
        loc="upper left",
    )

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

    # Keep the molecular-signal ranges defined by the signal products alone.
    # LIFE uncertainties are symmetric around zero and clipped at these fixed
    # limits, so an edge segment denotes noise above the plotted signal range.
    observation_plot = {}
    fixed_signal_limits = {}
    if observations:
        hour_values = []
        for index, path in enumerate(observation_paths):
            hour_match = re.search(r"(?:^|_)(\d+)h(?:_|$)", path.stem)
            hours = int(hour_match.group(1)) if hour_match else None
            hour_values.append(hours)
            if hours is not None and not labels_supplied:
                observation_labels[index] = f"{hours} h"

        ordered_indices = sorted(
            range(len(observations)),
            key=lambda index: hour_values[index] if hour_values[index] is not None else index,
        )
        for species, axes in (("N2O", ax_n2o), ("NH3", ax_nh3)):
            limits = tuple(float(value) for value in axes.get_ylim())
            axes.set_ylim(*limits)
            axes.set_autoscale_on(False)
            fixed_signal_limits[species] = list(limits)
            species_clipping = {}
            for zorder, index in enumerate(ordered_indices, start=20):
                obs_wl, _obs_half_bin, _obs_fp, obs_sigma = observations[index]
                in_band = (obs_wl >= LIFE_MIN) & (obs_wl <= LIFE_MAX)
                if not np.any(in_band):
                    raise ValueError(
                        "A LIFE dataset has no channels in the 4--18.5 um band"
                    )
                sigma = obs_sigma[in_band] / RES_SCALE
                plus = np.clip(sigma, limits[0], limits[1])
                minus = np.clip(-sigma, limits[0], limits[1])
                hours = hour_values[index]
                colour = LIFE_HOUR_COLOURS.get(hours, "#746F75")
                axes.plot(
                    obs_wl[in_band], plus, color=colour, linestyle="-",
                    linewidth=0.9, alpha=0.56, zorder=zorder,
                )
                axes.plot(
                    obs_wl[in_band], minus, color=colour, linestyle="--",
                    linewidth=0.9, alpha=0.56, zorder=zorder,
                )
                species_clipping[observation_labels[index]] = {
                    "fraction_plus_sigma_above_panel": float(
                        np.mean(sigma > limits[1])
                    ),
                    "fraction_minus_sigma_below_panel": float(
                        np.mean(-sigma < limits[0])
                    ),
                }
            observation_plot[species] = species_clipping

        legend_handles = []
        seen_hours = set()
        for index in ordered_indices:
            hours = hour_values[index]
            if hours in seen_hours:
                continue
            seen_hours.add(hours)
            legend_handles.append(
                Line2D(
                    [0], [0],
                    color=LIFE_HOUR_COLOURS.get(hours, "#746F75"),
                    linewidth=1.3,
                    label=(f"{hours} h" if hours is not None
                           else observation_labels[index]),
                )
            )
        legend_handles.extend(
            [
                Line2D([0], [0], color="#02040F", linewidth=1.2,
                       linestyle="-", label="+1σ"),
                Line2D([0], [0], color="#02040F", linewidth=1.2,
                       linestyle="--", label="−1σ"),
            ]
        )
        ax_nh3.legend(
            handles=legend_handles,
            title=(
                "LIFE noise: color = integration time; line = sign\n"
                "Edge segments exceed fixed signal limits"
            ),
            frameon=True,
            facecolor="white",
            framealpha=0.88,
            edgecolor="none",
            fontsize=8.0,
            title_fontsize=8.0,
            ncol=2,
            loc="upper right",
            borderpad=0.45,
            labelspacing=0.3,
            handlelength=1.5,
            columnspacing=0.8,
        )
    ax_nh3.set_xlabel("Wavelength [µm]", fontfamily="serif", fontsize=17,
                      color="black")

    suffix = ""
    if args.output_suffix:
        clean_suffix = re.sub(
            r"[^A-Za-z0-9_-]+", "_", args.output_suffix
        ).strip("_")
        if not clean_suffix:
            raise ValueError("--output-suffix must contain letters or digits")
        suffix = f"_{clean_suffix}"
    output_stem = f"emission_molecular_residuals_{args.campaign}{suffix}"
    out = PLOTS / f"{output_stem}.png"
    out_pdf = PLOTS / f"{output_stem}.pdf"
    fig.savefig(out, dpi=240, bbox_inches="tight")
    fig.savefig(out_pdf, bbox_inches="tight")
    print(f"saved {out.relative_to(REPO)}")
    print(f"saved {out_pdf.relative_to(REPO)}")

    if observation_paths:
        inputs = {
            "model_spectra": [
                FWD / f"{scenario}_emission.npz"
                for scenario in ("A0", "A1", "A2", "A3")
            ],
            "molecular_counterfactuals": [
                CF / f"{scenario}_reset_{species}_Fp_obs.npz"
                for scenario in ("A1", "A2", "A3")
                for species in ("N2O", "NH3")
            ],
        }
        provenance = {
            "generated_on": date.today().isoformat(),
            "script": str(Path(__file__).resolve().relative_to(REPO)),
            "campaign": campaign_id,
            "target": target_name,
            "observable": "direct planetary emission flux Fp at the system distance",
            "display_units": "W m^-2 um^-1",
            "conversion_from_input": "multiply Fp and sigma_Fp [W m^-2 m^-1] by 1e-6",
            "observation_labels": observation_labels,
            "noise_curve_display": {
                "panels": ["N2O molecular signal", "NH3 molecular signal"],
                "definition": "symmetric +1 sigma and -1 sigma curves around zero",
                "display_scaling": "sigma_Fp / RES_SCALE; same units as molecular signals",
                "signal_panel_limits": fixed_signal_limits,
                "autoscaling_disabled_after_signal_limits_set": True,
                "line_alpha": 0.56,
                "line_width_pt": 0.9,
                "color_encodes": "LIFE integration time: 1 h, 10 h and 100 h",
                "line_style_encodes": "+1 sigma solid; -1 sigma dashed",
                "clipping_fractions_by_species": observation_plot,
            },
            "observations": [
                {
                    "file": str(path.relative_to(REPO)),
                    "sha256": sha256(path),
                    "n_channels": int(len(observation[0])),
                    "uncertainty": (
                        "per-channel diagonal 1-sigma sigma_Fp; "
                        "one synthetic realization"
                    ),
                    "bin_half_width": "validated but not drawn",
                }
                for path, observation in zip(observation_paths, observations)
            ],
            "model_curve_display": f"log-wavelength rebin at R={DISPLAY_R}; presentation only",
            "signal_definition": (
                "F_reset_to_A0 - F_full for each molecular counterfactual; "
                "net difference F_A0 - F_Aj"
            ),
            "inputs": {
                category: [
                    {"file": str(path.relative_to(REPO)), "sha256": sha256(path)}
                    for path in paths
                ]
                for category, paths in inputs.items()
            },
            "outputs": [str(out.relative_to(REPO)), str(out_pdf.relative_to(REPO))],
            "interpretation_limit": (
                "The LIFE noise curves are synthetic uncertainties, not an "
                "observed LIFE measurement. The upper emission spectra contain "
                "no noise overlay. JWST transmission-depth products use a "
                "different observable and are not overplotted."
            ),
        }
        provenance_path = PLOTS / f"{output_stem}.provenance.json"
        provenance_path.write_text(
            json.dumps(provenance, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"saved {provenance_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
