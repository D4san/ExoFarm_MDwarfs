"""Read-only diagnosis of the NH3 change between official A3 100/1000h.

Writes only derived diagnostic products. Does not fit, resume, accept or
modify retrievals. Distinguishes median-spectrum residuals from best-fit chi2.
"""

import hashlib
import json
from pathlib import Path
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr

from audit_proxima_a3_retrieval_residuals import rebin_energy_flux, PALETTE
from run_proxima_molecule_ablation_campaign import DATASETS, RESULTS_REL

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1"
FULL = PROJECT / "retrievals/a3_1000h_full_20261011/native_grid_retry"
OUTPUT = PROJECT / "diagnostics/nh3_1000h_posterior_change_20261013"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    rerender = "--rerender" in sys.argv
    if OUTPUT.exists() and not rerender:
        raise RuntimeError("Diagnostic exists; preserve it")
    OUTPUT.mkdir(parents=True, exist_ok=rerender)
    provenance = {}

    def tracked(path):
        provenance[str(path.relative_to(ROOT))] = digest(path)
        return path

    forward_path = tracked(PROJECT / "forward_emission/A3_emission.npz")
    with np.load(forward_path) as forward:
        truth_wl = forward["wl_um"]
        truth_flux = forward["Fp_obs_W_m2_m"]
    with np.load(tracked(PROJECT / "lifesim/life_classic_binned_products.npz")) as saved:
        bins = saved["wl_bins_um"]
    truth = rebin_energy_flux(truth_wl, truth_flux, bins)
    pt_truth = np.loadtxt(tracked(ROOT / "Transmission_Spectroscopy/profiles/Proxima_b_A3_Extreme_PT.txt"), skiprows=1)
    chemistry = np.genfromtxt(tracked(ROOT / "Transmission_Spectroscopy/profiles/Proxima_b_A3_Extreme_chem.txt"), names=True)
    reference = json.loads(tracked(PROJECT / "retrievals/a0_fixed_reference_20261010/a0_reference.json").read_text())
    configuration = json.loads(tracked(FULL / "resolved_configuration.json").read_text())
    report = {"scope": "diagnosis only; no acceptance, new retrieval or scientific input changes",
              "comparisons": {}, "truth_rebin": "same photon-space overlap operator as generator"}
    stored = {}
    for hours in (100, 1000):
        if hours == 100:
            source = DATASETS["A3", 100]
            stem = source["full_results"].removesuffix("_results.txt")
            retrieval = ROOT / RESULTS_REL.parent
            data_file = PROJECT / "life_data" / source["file"]
            name = stem
            raw_name = stem
        else:
            retrieval = FULL / "products"
            name = configuration["model_name"]
            raw_name = name
            data_file = PROJECT / "life_data/LIFE_proxima_A3_1000h_O2_fixedBlack1bar_official.dat"
        result_path = tracked(retrieval / "results" / (name + "_results.txt"))
        result_text = result_path.read_text()
        chi2 = float(re.search(r"-> chi\^2 = ([0-9.]+)", result_text)[1])
        sample_path = tracked(retrieval / "samples" / (name + "_samples.txt"))
        names = [n.strip() for n in sample_path.open().readline().split("|")]
        samples = np.loadtxt(sample_path, skiprows=1, ndmin=2)
        raw_path = tracked(retrieval / "MultiNest_raw" / (raw_name + "-post_equal_weights.dat"))
        raw = np.loadtxt(raw_path, ndmin=2)
        np.testing.assert_allclose(samples, raw[:, :15], atol=6e-6, rtol=1e-6)
        assert np.isfinite(raw).all()
        samples = raw[:, :15]
        data = np.loadtxt(tracked(data_file), skiprows=1)
        np.testing.assert_allclose(data[:, 0], bins, atol=1e-5, rtol=0)
        spectrum = np.loadtxt(tracked(retrieval / "samples" / (name + "_spectrum_retrieved.txt")), skiprows=1)
        pt = np.loadtxt(tracked(retrieval / "samples" / (name + "_PT_retrieved.txt")), skiprows=1)
        median = rebin_energy_flux(spectrum[:, 0], spectrum[:, 3], bins)
        residual = (data[:, 2] - median) / data[:, 3]
        noise = (data[:, 2] - truth) / data[:, 3]
        model_bias = (median - truth) / data[:, 3]
        assert np.isfinite(np.concatenate([residual, noise, model_bias])).all()
        nh3 = samples[:, names.index("log_NH3")]
        q = np.quantile(nh3, [.025, .5, .975])
        correlations = {}
        for col, parameter in enumerate(names):
            if parameter not in ("log_NH3", "log_P_surf"):
                correlations[parameter] = float(spearmanr(nh3, samples[:, col]).statistic)
        high = nh3 > -8.8
        likelihood_gap = (float(np.max(raw[high, -1]) - np.max(raw[:, -1]))
                          if high.any() else None)
        probe = np.array([1, .1, .01, .001])
        true_temp = np.interp(np.log10(probe), np.log10(pt_truth[::-1, 1]), pt_truth[::-1, 2])
        median_temp = np.interp(np.log10(probe), np.log10(pt[::-1, 0]), pt[::-1, 3])
        nh3_band = (bins >= 9.5) & (bins <= 11.5)
        top = np.argsort(np.abs(residual))[-6:][::-1]
        record = {"n_samples": len(samples), "equal_weight_export_matches_raw": True,
                  "best_fit_chi2": chi2, "best_fit_chi2_per_17_effective_dof": chi2 / 17,
                  "median_spectrum_chi2": float(residual @ residual),
                  "true_forward_noise_chi2": float(noise @ noise),
                  "model_minus_truth_chi2": float(model_bias @ model_bias),
                  "model_fractional_rms": float(np.sqrt(np.mean(((median-truth)/truth)**2))),
                  "residual_bins_over_3sigma": int(np.sum(np.abs(residual) > 3)),
                  "nh3_log10_quantiles": q.tolist(),
                  "nh3_factor_A0_quantiles": (10**(q-reference["log10_vmr"]["NH3"])).tolist(),
                  "nh3_band_median_residual_chi2": float(residual[nh3_band] @ residual[nh3_band]),
                  "strongest_nh3_spearman": sorted(correlations.items(), key=lambda p: abs(p[1]), reverse=True)[:5],
                  "nh3_above_minus8p8_count": int(high.sum()),
                  "nh3_high_subset_max_loglike_gap": likelihood_gap,
                  "temperature_probes": [dict(pressure_bar=float(p), true_K=float(t), median_K=float(m))
                                         for p,t,m in zip(probe, true_temp, median_temp)],
                  "top_residuals": [dict(wavelength_um=float(bins[i]), residual_sigma=float(residual[i]),
                                         noise_sigma=float(noise[i]), model_offset_sigma=float(model_bias[i])) for i in top]}
        report["comparisons"][str(hours)] = record
        stored[hours] = dict(data=data, residual=residual, noise=noise, bias=model_bias,
                             median=median, pt=pt, nh3_q=q)
    # Check whether the low-NH3 region was present before the full-run interruption.
    checkpoint = FULL / "recovery_20261012_R1/checkpoint_backup"
    checkpoint_live = np.loadtxt(tracked(checkpoint / (configuration["model_name"] + "-phys_live.points")), ndmin=2)
    old_nh3 = checkpoint_live[:, configuration["parameters"].index("log_NH3")]
    report["pre_resume_checkpoint_nh3"] = {
        "n_live": len(old_nh3), "log10_q025_median_q975": np.quantile(old_nh3,[.025,.5,.975]).tolist(),
        "n_above_minus8p8": int(np.sum(old_nh3 > -8.8)),
        "note": "live points are not posterior; show region existed before resume"}
    old_data = stored[100]["data"]
    new_data = stored[1000]["data"]
    report["dataset_contract"] = {"centres_halfwidths_identical": bool(np.array_equal(old_data[:,:2],new_data[:,:2])),
        "sigma_scaling_max_relative_error": float(np.max(np.abs(new_data[:,3]/(old_data[:,3]/np.sqrt(10))-1))),
        "independent_noise_correlation": float(np.corrcoef(stored[100]["noise"],stored[1000]["noise"])[0,1])}
    report["truth_profile"] = {"nh3_log10_range": [float(np.log10(np.min(chemistry["NH3"]))),float(np.log10(np.max(chemistry["NH3"])))],
        "pressure_bar_range": [float(np.min(chemistry["PRESS"])),float(np.max(chemistry["PRESS"]))]}
    report["provenance_sha256"] = provenance
    for relative, expected in provenance.items():
        assert digest(ROOT / relative) == expected
    if rerender:
        assert json.loads((OUTPUT / "diagnostic.json").read_text()) == json.loads(json.dumps(report))
    else:
        (OUTPUT / "diagnostic.json").write_text(json.dumps(report, indent=2)+"\n")
    plt.rcParams.update({"font.family":"serif", "font.serif":["STIXGeneral"], "mathtext.fontset":"stix"})
    fig, axes = plt.subplots(2,2,figsize=(12,8))
    operator_file = OUTPUT / "binning_operator.json"
    actual_operator = json.loads(operator_file.read_text()) if operator_file.exists() else None
    colours = {100: PALETTE["rusty_spice"],1000: PALETTE["dark_amaranth"]}
    for ax, hours in zip(axes[0],(100,1000)):
        item = stored[hours]
        ax.axhspan(-1,1,color="0.9")
        ax.axvspan(9.5,11.5,color=PALETTE["sunlit_clay"],alpha=.25)
        residual_to_plot = (actual_operator[str(hours)]["actual_median_residual_per_bin_sigma"]
                            if actual_operator else item["residual"])
        ax.plot(bins,residual_to_plot,"o-",label="Dato − mediana (likelihood)",color=colours[hours])
        ax.plot(bins,item["noise"],".--",label="Dato − verdad (generador)",color="0.4")
        ax.axhline(0,color="0.4",lw=.8)
        ax.set(xlabel="Longitud de onda (μm)",ylabel="Residuo / σ del dataset",title=f"{hours} h · χ² mejor ajuste = {report['comparisons'][str(hours)]['best_fit_chi2']:.2f}")
        ax.legend(fontsize=9)
    ax=axes[1,0]
    ax.plot(pt_truth[:,2],pt_truth[:,1],color="black",ls="--",label="PT verdadero VULCAN")
    for hours in (100,1000):
        pt=stored[hours]["pt"]
        ax.plot(pt[:,3],pt[:,0],color=colours[hours],label=f"PT mediana {hours} h")
        ax.fill_betweenx(pt[:,0],pt[:,1],pt[:,5],color=colours[hours],alpha=.12)
    ax.set(yscale="log",ylim=(1,1e-5),xlabel="Temperatura (K)",ylabel="Presión (bar)",title="Perfil térmico · banda central 95 %")
    ax.legend(fontsize=9)
    ax=axes[1,1]
    ax.plot(chemistry["NH3"],chemistry["PRESS"],"k--",label=r"NH$_3$ verdadero: perfil vertical")
    for hours in (100,1000):
        q=10**stored[hours]["nh3_q"]
        ax.axvline(q[1],color=colours[hours],label=f"NH$_3$ isochem {hours} h")
        ax.axvspan(q[0],q[2],color=colours[hours],alpha=.12)
    ax.axvline(reference["vmr"]["NH3"],color="0.4",ls=":",label="Referencia escalar A0")
    ax.set(xscale="log",yscale="log",ylim=(1,1e-5),xlim=(1e-14,1e-7),xlabel=r"VMR NH$_3$",ylabel="Presión (bar)",title="Representación química · banda central 95 %")
    ax.legend(fontsize=9)
    fig.suptitle(r"Diagnóstico A3: NH$_3$ a 100 y 1000 h · resultados preliminares",fontsize=16)
    fig.tight_layout(rect=(0,0,1,.95))
    fig.savefig(OUTPUT/"diagnostic.png",dpi=170)
    fig.savefig(OUTPUT/"diagnostic.pdf")
    print(json.dumps({k:v for k,v in report.items() if k!="provenance_sha256"},indent=2))


if __name__ == "__main__":
    main()
