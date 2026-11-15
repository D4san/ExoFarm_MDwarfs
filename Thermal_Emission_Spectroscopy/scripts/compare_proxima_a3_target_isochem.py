"""Three authorized hybrid forwards: N2O, NH3, or both constant in A3.

Keep true PT and every unselected VULCAN species profile. File-read chemistry
represents a hybrid profile; selected columns are exactly constant. No fitting
or retrieval, no instrumentation correction, no noise-floor injection.
"""

import hashlib
import json
import os
from pathlib import Path
import sys

os.environ.setdefault("POSEIDON_input_data", "/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs")
os.environ.setdefault("PYSYN_CDBS", "/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids")
for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[variable] = "1"

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from POSEIDON.core import compute_spectrum
import emission_forward as ef
from audit_proxima_a3_retrieval_residuals import rebin_energy_flux, H_PLANCK, C_LIGHT
from retrieval_reference import column_averaged_mixing_ratio

ROOT = ef.REPO
PROJECT = ROOT / "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1"
OUTPUT = PROJECT / "diagnostics/A3_N2O_NH3_hybrid_isochem_20261014"
VARIANTS = {"N2O": ["N2O"], "NH3": ["NH3"], "joint": ["N2O", "NH3"]}
sys.path.insert(0, str(ROOT / "Transmission_Spectroscopy/notebooks"))
from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def state(stage):
    (OUTPUT / "execution_state.json").write_text(json.dumps({"stage": stage, "pid": os.getpid(),
        "new_retrievals": 0}, indent=2)+"\n")
    print(stage, flush=True)


def main():
    if OUTPUT.exists():
        raise RuntimeError("Diagnostic exists; preserve it")
    OUTPUT.mkdir(parents=True)
    paths = [PROJECT / "forward_emission/A3_emission.npz",
             PROJECT / "lifesim/life_classic_binned_products.npz",
             PROJECT / "life_data/LIFE_proxima_A3_1000h_O2_fixedBlack1bar_official.dat",
             ef.PROFILES_DIR / "Proxima_b_A3_Extreme_PT.txt",
             ef.PROFILES_DIR / "Proxima_b_A3_Extreme_chem.txt",
             ROOT / "Thermal_Emission_Spectroscopy/scripts/emission_forward.py", Path(__file__)]
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    (OUTPUT / "preserved_inputs.json").write_text(json.dumps(hashes,indent=2)+"\n")
    with np.load(paths[0]) as saved:
        wl, vertical = saved["wl_um"], saved["Fp_obs_W_m2_m"]
    with np.load(paths[1]) as saved:
        bins = saved["wl_bins_um"]
        life = saved["flux_binned_A3"] * H_PLANCK * C_LIGHT / (bins*1e-6)
    data = np.loadtxt(paths[2],skiprows=1)
    sigma = data[:,3]
    profile = np.genfromtxt(paths[4],names=True)
    values = {gas: column_averaged_mixing_ratio(profile,gas) for gas in ("N2O","NH3")}
    model = ef.build_model("A3",ef.PROXIMA_B)
    planet,star = ef.build_planet(ef.PROXIMA_B),ef.build_star(wl,ef.PROXIMA_B)
    P,surface,reference,radius = ef.pressure_grid(ef.PROXIMA_B)
    temperature,chemistry = ef.load_profiles(model,P,"A3",ef.PROXIMA_B)
    if chemistry.shape[0] != len(model["chemical_species"]):
        raise ValueError(f"Unexpected chemistry shape: {chemistry.shape}")
    truth_atmosphere = ef.build_atmosphere(planet,model,P,reference,radius,surface,temperature,chemistry)
    atmospheres = {}
    for key,selected in VARIANTS.items():
        changed = chemistry.copy()
        for gas in selected:
            index = list(model["chemical_species"]).index(gas)
            changed[index] = values[gas]
        atmosphere = ef.build_atmosphere(planet,model,P,reference,radius,surface,temperature,changed)
        np.testing.assert_array_equal(atmosphere["T"],truth_atmosphere["T"])
        for index,gas in enumerate(model["chemical_species"]):
            if gas in selected:
                np.testing.assert_allclose(atmosphere["X"][index],values[gas],atol=0,rtol=1e-12)
            else:
                np.testing.assert_array_equal(atmosphere["X"][index],truth_atmosphere["X"][index])
        atmospheres[key] = atmosphere
    state("Loading one shared opacity table; hybrid PT and unselected chemistry verified")
    opac = ef.read_opacities_for(model,wl)
    arrays = {"wl_um":wl,"vertical_Fp":vertical,"life_bins_um":bins,"life_Fp":life,"sigma_1000h":sigma}
    report = {"scope":"three hybrid forwards, no retrieval/fitting/noise changes",
              "isochem_values":values,"definition":"pressure-column A3 means",
              "true_PT_and_unselected_profiles_identical":True,
              "bulk_N2":"original file-read profile retained exactly",
              "comparisons":{}}
    for key,selected in VARIANTS.items():
        state("Computing hybrid "+key)
        flux=compute_spectrum(planet,star,model,atmospheres[key],opac,wl,spectrum_type="direct_emission")
        if not np.isfinite(flux).all():
            raise ValueError("Nonfinite spectrum")
        binned=rebin_energy_flux(wl,flux,bins)
        relative=binned/life-1
        scaled=(binned-life)/sigma
        windows={}
        for label,low,high in (("N2O_7p5_9",7.5,9),("NH3_9p5_11p5",9.5,11.5),("N2O_16p5_17p5",16.5,17.5)):
            mask=(bins>=low)&(bins<=high)
            windows[label]={"bins":int(mask.sum()),"rms_relative":float(np.sqrt(np.mean(relative[mask]**2))),
                           "max_relative":float(np.max(np.abs(relative[mask]))),
                           "rms_sigma_1000h":float(np.sqrt(np.mean(scaled[mask]**2)))}
        report["comparisons"][key]={"constant_species":selected,"rms_relative":float(np.sqrt(np.mean(relative**2))),
            "max_relative":float(np.max(np.abs(relative))),"rms_sigma_1000h":float(np.sqrt(np.mean(scaled**2))),
            "max_sigma_1000h":float(np.max(np.abs(scaled))),"windows":windows,
            "chemical_sum_range": [float(np.min(atmospheres[key]["X"].sum(axis=0))),
                                   float(np.max(atmospheres[key]["X"].sum(axis=0)))]}
        arrays[key+"_native_Fp"] = flux
        arrays[key+"_common_Fp"] = binned
    report["joint_not_assumed_additive"] = True
    for relative,expected in hashes.items():
        if sha(ROOT/relative)!=expected:
            raise RuntimeError("Protected input changed: "+relative)
    np.savez(OUTPUT/"hybrid_spectra.npz",**arrays)
    (OUTPUT/"comparison.json").write_text(json.dumps(report,indent=2)+"\n")
    plt.rcParams.update({"font.family":"serif","font.serif":["STIXGeneral"],"mathtext.fontset":"stix","font.size":12})
    fig,axes=plt.subplots(3,1,figsize=(11,9),sharex=True,gridspec_kw={"height_ratios":[1.5,1,1]})
    colours={"N2O":PALETTE["deep_space_blue"],"NH3":PALETTE["golden_orange"],"joint":PALETTE["dark_amaranth"]}
    labels={"N2O":r"Solo N$_2$O constante","NH3":r"Solo NH$_3$ constante","joint":r"N$_2$O y NH$_3$ constantes"}
    axes[0].plot(bins,life*1e12,"ko--",ms=4,lw=1,label="A3 vertical / LIFE sin ruido")
    for key in VARIANTS:
        binned=arrays[key+"_common_Fp"]
        axes[0].plot(bins,binned*1e12,color=colours[key],lw=1.6,label=labels[key])
        axes[1].plot(bins,100*(binned/life-1),color=colours[key],marker=".",label=labels[key])
        axes[2].plot(bins,(binned-life)/sigma,color=colours[key],marker=".",label=labels[key])
    axes[0].set_ylabel(r"$F_p$ ($10^{-12}$ W m$^{-2}$ m$^{-1}$)")
    axes[1].set_ylabel("Diferencia relativa (%)")
    axes[2].set_ylabel("Diferencia / σ (1000 h)")
    axes[2].set_xlabel("Longitud de onda (μm)")
    axes[0].legend(fontsize=10,ncol=2)
    for ax in axes:
        ax.set_xlim(4,18.5)
        ax.grid(alpha=.15)
        ax.spines[["top","right"]].set_visible(False)
    for ax in axes[1:]:
        ax.axhline(0,color="0.4",lw=.8)
        ax.axvspan(9.5,11.5,color=PALETTE["sunlit_clay"],alpha=.16)
    axes[2].axhspan(-1,1,color="0.9",zorder=-1)
    fig.suptitle(r"A3: aislar química constante en N$_2$O y NH$_3$",fontsize=16)
    fig.text(.5,.01,"Resto de perfiles y PT VULCAN intactos; mismo operador LIFE. Diferencia/σ es diagnóstico, no detección.",ha="center",fontsize=10)
    fig.tight_layout(rect=(0,.025,1,.96))
    fig.savefig(OUTPUT/"hybrid_comparison.png",dpi=170)
    fig.savefig(OUTPUT/"hybrid_comparison.pdf")
    state("COMPLETE_DIAGNOSTIC_ONLY")
    print(json.dumps(report,indent=2),flush=True)


if __name__=="__main__":
    main()
