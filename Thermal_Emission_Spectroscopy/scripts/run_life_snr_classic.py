"""LIFEsim-classic S/N analysis for `life_earth_sun_10pc` (Phase-3 steps 4-5).

Pipeline:
  1. Observe each Earth--Sun scenario A0--A3 with the LIFE classic scene at a
     reference integration time -> per-bin observed flux and 1-sigma noise.
  2. Isolate each molecule's differential signal from the counterfactuals:
     dF_i = F_binned(full scenario) - F_binned(scenario reset_i_to_A0), on the
     LIFE grid.
  3. Band-integrated diagnostic SNR of the molecular signal:
     SNR_i,band = sqrt( sum_{bins in band} (dF_i / sigma)^2 )  (sigma from the
     full-scenario observation). This is a DIAGNOSTIC, not a detection.
  4. Rank the individual bins by |dF_i|/sigma -> most useful S/N peaks.
  5. S/N vs integration time: classic is photon-noise dominated so SNR ~ sqrt(t);
     the scaling is verified against direct get_spectrum calls, then extrapolated.

Outputs: tables/life_classic_snr_table.csv and plots under outputs/<campaign>/.
Provenance: earth_20260615_pre_n2o_correction (interface validation only).
"""

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from spectres import spectres

import emission_forward as ef
from life_scene_classic import LifeSceneClassic, fp_obs_to_photon_flux

CAMPAIGN_ID = "life_earth_sun_10pc_interface_v1"
OUT = ef.REPO / "Thermal_Emission_Spectroscopy" / "outputs" / CAMPAIGN_ID
FWD = OUT / "forward_emission"
CF = OUT / "molecular_diagnostics"
TABLES = OUT / "tables"
PLOTS = OUT / "plots"

REF_HOURS = 10.0                       # reference integration time
SCENARIOS = ["A0", "A1", "A2", "A3"]
PERTURBED = ["A1", "A2", "A3"]
TARGETS = ["N2O", "NH3"]               # ExoFarm technosignature species
CONTROLS = ["H2O", "CO2", "O3", "CH4"]
ALL_SPECIES = TARGETS + CONTROLS

# Diagnostic mid-IR bands (um). Targets first.
BANDS = {
    "N2O": [(7.5, 8.1), (16.5, 17.5)],
    "NH3": [(9.5, 11.5)],
    "H2O": [(5.5, 7.3), (17.0, 18.5)],
    "CO2": [(14.0, 16.0)],
    "O3":  [(9.4, 9.9)],
    "CH4": [(7.4, 8.0)],
}

SCENARIO_COLOUR = {"A0": "#95E36B", "A1": "#56E3DB", "A2": "#BD62E3", "A3": "#E34F95"}
MOL_COLOUR = {"N2O": "#1f77b4", "NH3": "#ff7f0e", "CH4": "#9467bd",
              "O3": "#17becf", "H2O": "#2ca02c", "CO2": "#8c564b"}


def _style():
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["STIX Two Text", "STIXGeneral", "Times New Roman"],
        "mathtext.fontset": "stix", "figure.dpi": 130,
    })


def load_full(scenario):
    d = np.load(FWD / f"{scenario}_emission.npz")
    return d["wl_um"], d["Fp_obs_W_m2_m"]


def load_reset(scenario, species):
    d = np.load(CF / f"{scenario}_reset_{species}_Fp_obs.npz")
    return d["wl_um"], d["Fp_obs_W_m2_m"]


def rebin_photon(wl_um, Fp_obs, wl_bins_m):
    """POSEIDON Fp_obs -> photon flux density rebinned onto LIFE bins."""
    wl_m, F_ph = fp_obs_to_photon_flux(wl_um, Fp_obs)
    return spectres(wl_bins_m, wl_m, F_ph, fill=0.0, verbose=False)


def band_mask(wl_um, windows):
    m = np.zeros_like(wl_um, dtype=bool)
    for lo, hi in windows:
        m |= (wl_um >= lo) & (wl_um <= hi)
    return m


def band_snr(dF, sigma, mask):
    """sqrt(sum (dF/sigma)^2) over the masked bins."""
    per_bin = np.where((sigma > 0) & np.isfinite(sigma), dF / sigma, 0.0)
    return float(np.sqrt(np.nansum((per_bin[mask]) ** 2)))


def main():
    _style()
    TABLES.mkdir(parents=True, exist_ok=True)
    PLOTS.mkdir(parents=True, exist_ok=True)
    t_ref = REF_HOURS * 3600.0

    scene = LifeSceneClassic()
    wl_bins_m = scene.wl_bins
    wl_um = scene.wl_bins_um
    print(f"[scene] LIFE R={scene.spec_res:.0f} D={scene.diameter_m}m, "
          f"{len(wl_um)} bins {wl_um[0]:.1f}-{wl_um[-1]:.1f}um, t_ref={REF_HOURS}h")

    # --- observe each scenario (noise-free flux + sigma) -------------------
    obs = {}
    for s in SCENARIOS:
        w, fp = load_full(s)
        o = scene.observe(w, fp, t_ref)
        obs[s] = o
        print(f"[{s}] continuum SNR/bin max={np.nanmax(o['snr_per_bin']):.2f} "
              f"total(quad)={np.sqrt(np.nansum(o['snr_per_bin']**2)):.1f}")

    # --- molecular signals dF_i and binned counterfactuals -----------------
    # dF_i(scenario) = F_binned(full) - F_binned(reset_i)
    signals = {}   # (scenario, species) -> dF on LIFE grid
    for s in PERTURBED:
        F_full = obs[s]["flux_binned_ph"]
        for sp in ALL_SPECIES:
            w, fp = load_reset(s, sp)
            F_reset = rebin_photon(w, fp, wl_bins_m)
            signals[(s, sp)] = F_full - F_reset

    # --- results table: band SNR per (scenario, molecule) at t_ref ---------
    rows = []
    for s in PERTURBED:
        sigma = obs[s]["sigma_ph"]
        for sp in ALL_SPECIES:
            dF = signals[(s, sp)]
            for (lo, hi) in BANDS[sp]:
                m = band_mask(wl_um, [(lo, hi)])
                snr_b = band_snr(dF, sigma, m)
                # best single bin in this band
                per_bin = np.where((sigma > 0) & np.isfinite(sigma) & m,
                                   np.abs(dF) / sigma, 0.0)
                bi = int(np.argmax(per_bin))
                rows.append({
                    "scenario": s, "molecule": sp, "role":
                    ("target" if sp in TARGETS else "control"),
                    "band_um": f"{lo:.1f}-{hi:.1f}",
                    "band_SNR_10h": round(snr_b, 3),
                    "best_bin_um": round(float(wl_um[bi]), 2),
                    "best_bin_SNR_10h": round(float(per_bin[bi]), 3),
                })
        # whole-band signal SNR of each target over 4-18.5
        for sp in TARGETS:
            dF = signals[(s, sp)]
            m = np.ones_like(wl_um, dtype=bool)
            rows.append({
                "scenario": s, "molecule": sp, "role": "target",
                "band_um": "4.0-18.5(full)",
                "band_SNR_10h": round(band_snr(dF, sigma, m), 3),
                "best_bin_um": "", "best_bin_SNR_10h": "",
            })

    csv_path = TABLES / "life_classic_snr_table.csv"
    with open(csv_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"[table] wrote {csv_path.relative_to(ef.REPO)} ({len(rows)} rows)")

    # print the target summary
    print("\n=== Señal molecular ExoFarm — SNR por banda (t=10h, R=50, D=2m) ===")
    print(f"{'esc':>3} {'mol':>4} {'banda[um]':>14} {'SNR_banda':>9} "
          f"{'mejor_bin':>9} {'SNR_bin':>7}")
    for r in rows:
        if r["molecule"] in TARGETS and r["best_bin_um"] != "":
            print(f"{r['scenario']:>3} {r['molecule']:>4} {r['band_um']:>14} "
                  f"{r['band_SNR_10h']:>9} {str(r['best_bin_um'])+'um':>9} "
                  f"{r['best_bin_SNR_10h']:>7}")

    # --- verify sqrt(t) scaling for A3 total, then build SNR vs time --------
    verify_hours = [1.0, 10.0, 100.0]
    tot = []
    for th in verify_hours:
        o = scene.observe(*load_full("A3"), th * 3600.0)
        tot.append(np.sqrt(np.nansum(o["snr_per_bin"] ** 2)))
    ratio = tot[2] / tot[0]
    print(f"\n[sqrt(t) check] A3 total SNR at 1/10/100h = "
          f"{tot[0]:.1f}/{tot[1]:.1f}/{tot[2]:.1f}; ratio(100h/1h)={ratio:.1f} "
          f"(expect ~10 for sqrt-t)")

    _plot_snr_vs_time(wl_um, obs, signals)
    _plot_a3_signal(wl_um, obs, signals)
    print("[done]")


def _plot_snr_vs_time(wl_um, obs, signals):
    """Band-SNR of the ExoFarm targets vs integration time (sqrt-t scaling)."""
    hours = np.logspace(np.log10(1), np.log10(1000), 40)
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    for s in PERTURBED:
        sigma = obs[s]["sigma_ph"]
        for sp in TARGETS:
            dF = signals[(s, sp)]
            m = band_mask(wl_um, BANDS[sp])
            snr10 = band_snr(dF, sigma, m)             # at 10 h
            snr_t = snr10 * np.sqrt(hours / REF_HOURS)
            ls = "-" if sp == "N2O" else "--"
            ax.plot(hours, snr_t, ls=ls, color=SCENARIO_COLOUR[s],
                    lw=1.6, label=f"{s} {sp}")
    ax.axhline(5, color="0.6", lw=0.8, ls=":")
    ax.text(1.2, 5.2, "SNR=5 (diagnostic ref.)", fontsize=7, color="0.5")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Integration time [h]")
    ax.set_ylabel(r"Band-integrated molecular-signal SNR")
    ax.set_title("LIFE (classic) molecular-signal SNR vs time, Earth--Sun A1--A3 @10pc\n"
                 f"(interface benchmark, {ef.PROVENANCE_LABEL}; SNR is a diagnostic)",
                 fontsize=8.5)
    ax.legend(frameon=False, fontsize=7.5, ncol=3)
    fig.tight_layout()
    out = PLOTS / "life_classic_snr_vs_time.png"
    fig.savefig(out, bbox_inches="tight")
    print(f"[plot] {out.relative_to(ef.REPO)}")


def _plot_a3_signal(wl_um, obs, signals):
    """A3 molecular signals dF_N2O, dF_NH3 against the per-bin noise sigma."""
    fig, ax = plt.subplots(figsize=(9, 5))
    sigma = obs["A3"]["sigma_ph"]
    ax.plot(wl_um, sigma, color="0.6", lw=1.0, label=r"LIFE 1$\sigma$ noise (10h)")
    for sp in TARGETS:
        ax.plot(wl_um, np.abs(signals[("A3", sp)]), color=MOL_COLOUR[sp],
                lw=1.4, label=fr"|$\Delta F$| {sp} (A3$-$reset)")
    ax.set_yscale("log")
    ax.set_xlim(4, 18.5)
    ax.set_xlabel(r"Wavelength [$\mu$m]")
    ax.set_ylabel(r"Photon flux density [ph m$^{-2}$ s$^{-1}$ m$^{-1}$]")
    ax.set_title("A3 ExoFarm molecular signals vs LIFE noise floor (classic, 10h)\n"
                 f"(interface benchmark, {ef.PROVENANCE_LABEL})", fontsize=9)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    out = PLOTS / "life_classic_A3_signal_vs_noise.png"
    fig.savefig(out, bbox_inches="tight")
    print(f"[plot] {out.relative_to(ef.REPO)}")


if __name__ == "__main__":
    main()
