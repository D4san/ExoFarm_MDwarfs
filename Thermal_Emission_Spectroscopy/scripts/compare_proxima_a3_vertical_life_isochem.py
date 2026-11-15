"""Generate the authorized three-spectrum A3 diagnostic, without retrievals.

Full vertical truth and pressure-averaged isochem use the same true PT,
geometry, surface, wavelength grid and opacities. Compare with preserved
noise-free LIFE products using the generator's photon-space operator.
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
from POSEIDON.core import define_model, make_atmosphere, compute_spectrum, load_data
from POSEIDON.instrument import bin_spectrum_to_data
import emission_forward as ef
from audit_proxima_a3_retrieval_residuals import rebin_energy_flux, H_PLANCK, C_LIGHT
from retrieval_reference import column_averaged_mixing_ratio

ROOT = ef.REPO
PROJECT = ROOT / "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1"
OUTPUT = PROJECT / "diagnostics/A3_vertical_LIFE_isochem_20261014"
sys.path.insert(0, str(ROOT / "Transmission_Spectroscopy/notebooks"))
from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def state(stage):
    (OUTPUT / "execution_state.json").write_text(json.dumps({"stage": stage,
        "pid": os.getpid(), "no_retrievals": True}, indent=2)+"\n")
    print(stage, flush=True)


def main():
    if OUTPUT.exists():
        raise RuntimeError("Comparison output exists; never overwrite")
    OUTPUT.mkdir(parents=True)
    protected = [PROJECT / "forward_emission/A3_emission.npz",
                 PROJECT / "lifesim/life_classic_binned_products.npz",
                 PROJECT / "life_data/LIFE_proxima_A3_1000h_O2_fixedBlack1bar_official.dat",
                 ef.PROFILES_DIR / "Proxima_b_A3_Extreme_PT.txt",
                 ef.PROFILES_DIR / "Proxima_b_A3_Extreme_chem.txt",
                 Path(__file__), ROOT / "Thermal_Emission_Spectroscopy/scripts/emission_forward.py"]
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in protected}
    (OUTPUT / "preserved_inputs.json").write_text(json.dumps(hashes, indent=2)+"\n")
    target = ef.PROXIMA_B
    with np.load(protected[0]) as saved:
        wl, saved_flux = saved["wl_um"], saved["Fp_obs_W_m2_m"]
    with np.load(protected[1]) as saved:
        bins = saved["wl_bins_um"]
        life = saved["flux_binned_A3"] * H_PLANCK * C_LIGHT / (bins * 1e-6)
    data = np.loadtxt(protected[2], skiprows=1)
    sigma = data[:,3]
    profile = np.genfromtxt(protected[4], names=True)
    values = {gas: column_averaged_mixing_ratio(profile,gas) for gas in ef.PARAM_SPECIES}
    if sum(values.values()) >= 1:
        raise ValueError("Invalid isochem sum")
    truth_model = ef.build_model("A3",target)
    iso_model = define_model("A3_isochem_columnmean_diagnostic", ef.BULK_SPECIES,
                            ef.PARAM_SPECIES, PT_profile="file_read", X_profile="isochem",
                            radius_unit="R_E", surface=True, thermal=True, thermal_scattering=False)
    np.testing.assert_array_equal(truth_model["chemical_species"],iso_model["chemical_species"])
    planet, star = ef.build_planet(target), ef.build_star(wl,target)
    P, surface, reference, radius = ef.pressure_grid(target)
    temperature, chemistry = ef.load_profiles(truth_model,P,"A3",target)
    truth_atm = ef.build_atmosphere(planet,truth_model,P,reference,radius,surface,temperature,chemistry)
    iso_atm = make_atmosphere(planet,iso_model,P,reference,radius,T_input=temperature,
                            log_X_params=np.log10([values[gas] for gas in ef.PARAM_SPECIES]),
                            surface_params=np.array([np.log10(surface)]))
    np.testing.assert_array_equal(truth_atm["T"],iso_atm["T"])
    # Prove the constants actually entered the constructed atmosphere.
    for gas,value in values.items():
        col=list(iso_model["chemical_species"]).index(gas)
        np.testing.assert_allclose(iso_atm["X"][col],value,rtol=1e-12,atol=0)
    state("Loading shared opacities for one vertical and one isochem forward")
    opac = ef.read_opacities_for(truth_model,wl)
    state("Computing vertical A3 spectrum")
    vertical = compute_spectrum(planet,star,truth_model,truth_atm,opac,wl,spectrum_type="direct_emission")
    state("Computing A3 isochem spectrum with identical true PT")
    iso = compute_spectrum(planet,star,iso_model,iso_atm,opac,wl,spectrum_type="direct_emission")
    if not np.isfinite(vertical).all() or not np.isfinite(iso).all():
        raise ValueError("Nonfinite forward")
    vertical_binned=rebin_energy_flux(wl,vertical,bins)
    iso_binned=rebin_energy_flux(wl,iso,bins)
    np.testing.assert_allclose(vertical,saved_flux,rtol=1e-10,atol=0)
    np.testing.assert_allclose(vertical_binned,life,rtol=1e-10,atol=0)
    # Separate interface diagnostic: the same native spectra through likelihood.
    native_data=load_data(str(protected[2].parent),[protected[2].name],["LIFE"],wl,
                          skiprows=1,wl_unit="micron",bin_width="half",spectrum_unit="Fp")
    vertical_likelihood=bin_spectrum_to_data(vertical,wl,native_data)
    iso_likelihood=bin_spectrum_to_data(iso,wl,native_data)
    comparisons={}
    for label,flux in (("vertical_common_operator",vertical_binned),
                       ("isochem_common_operator",iso_binned),
                       ("vertical_actual_likelihood",vertical_likelihood),
                       ("isochem_actual_likelihood",iso_likelihood)):
        fractional=flux/life-1
        residual=(flux-life)/sigma
        comparisons[label]={"rms_relative":float(np.sqrt(np.mean(fractional**2))),
                            "max_relative":float(np.max(np.abs(fractional))),
                            "rms_sigma_1000h":float(np.sqrt(np.mean(residual**2))),
                            "max_sigma_1000h":float(np.max(np.abs(residual))),
                            "sum_squared_difference_over_sigma":float(residual@residual)}
    np.savez(OUTPUT/"three_spectra.npz",wl_um=wl,vertical_Fp=vertical,isochem_Fp=iso,
             life_bin_centres_um=bins,life_Fp=life,vertical_common_Fp=vertical_binned,
             isochem_common_Fp=iso_binned,vertical_likelihood_Fp=vertical_likelihood,
             isochem_likelihood_Fp=iso_likelihood,sigma_1000h=sigma,P_bar=P,T_K=temperature)
    report={"observable":"Fp at observer in W m^-2 m^-1", "scenario":"A3",
            "true_PT_identical":True,"isochem_definition":"integral X(p) dp / pressure span",
            "constant_vmr":values,"log10_constant_vmr":{gas:float(np.log10(v)) for gas,v in values.items()},
            "N2_bulk":"isochem balance 1-sum(trace VMR); vertical uses original profile convention",
            "no_fitting":True,"native_grid_points":len(wl),"native_grid_um":[float(wl[0]),float(wl[-1])],
            "R":10000,"n_layers":len(P),"shared_opacities":True,"surface_bar":float(surface),
            "distance_pc":target.distance_pc,"comparisons":comparisons,
            "limitations":"pressure mean is not radiatively equivalent truth; PT file_read control is not a Madhu fit; saved noiseless LIFE product reused, no new extraction or noise realization"}
    for relative,expected in hashes.items():
        if sha(ROOT/relative)!=expected:
            raise RuntimeError("Input changed: "+relative)
    (OUTPUT/"comparison.json").write_text(json.dumps(report,indent=2)+"\n")
    plt.rcParams.update({"font.family":"serif","font.serif":["STIXGeneral"],"mathtext.fontset":"stix","font.size":12})
    fig,axes=plt.subplots(3,1,figsize=(11,10),sharex=True,gridspec_kw={"height_ratios":[2,1,1]})
    blue=PALETTE["deep_space_blue"]
    pink=PALETTE["scenario_pink"]
    violet=PALETTE["charcoal_violet"]
    axes[0].plot(wl,vertical*1e12,color=blue,alpha=.25,lw=.45,label="POSEIDON A3 vertical · nativo")
    axes[0].plot(bins,vertical_binned*1e12,color=blue,ls="--",lw=1.5,label="A3 vertical · mismos canales LIFE")
    axes[0].plot(bins,life*1e12,"o",color=pink,mfc="none",ms=7,label="LIFEsim guardado · sin ruido")
    axes[0].plot(bins,iso_binned*1e12,"s-",color=violet,ms=4,label="POSEIDON A3 isochem · mismos canales")
    axes[0].set_ylabel(r"$F_p$ ($10^{-12}$ W m$^{-2}$ m$^{-1}$)")
    axes[0].legend(fontsize=10,ncol=2)
    axes[0].set_title("Tres espectros A3 · mismo PT verdadero, radio y superficie",fontsize=16)
    axes[1].axhline(0,color="0.4",lw=.8)
    axes[1].plot(bins,100*(vertical_binned/life-1),"o--",color=blue,label="Vertical − LIFE")
    axes[1].plot(bins,100*(iso_binned/life-1),"s-",color=violet,label="Isochem − LIFE")
    axes[1].set_ylabel("Diferencia relativa (%)")
    axes[1].legend(fontsize=10)
    axes[2].axhspan(-1,1,color="0.92")
    axes[2].axhline(0,color="0.4",lw=.8)
    axes[2].plot(bins,(iso_binned-life)/sigma,"s-",color=violet,label="Isochem − LIFE · operador común")
    axes[2].plot(bins,(vertical_likelihood-life)/sigma,".--",color=PALETTE["rusty_spice"],label="Vertical − LIFE · operador actual retrieval")
    axes[2].set_ylabel("Diferencia / σ (1000 h)")
    axes[2].set_xlabel("Longitud de onda (μm)")
    axes[2].legend(fontsize=10)
    for ax in axes:
        ax.set_xlim(4,18.5)
        ax.grid(alpha=.15)
        ax.spines[["top","right"]].set_visible(False)
    fig.text(.5,.015,"Isochem: abundancias A3 promediadas en presión; sin optimización. Diferencia/σ es diagnóstico, no detección.",ha="center",fontsize=10)
    fig.tight_layout(rect=(0,.035,1,1))
    fig.savefig(OUTPUT/"three_spectra.png",dpi=170)
    fig.savefig(OUTPUT/"three_spectra.pdf")
    state("COMPLETE_DIAGNOSTIC_ONLY")
    print(json.dumps(report,indent=2),flush=True)


if __name__=="__main__":
    main()
