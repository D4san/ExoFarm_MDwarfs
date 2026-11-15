"""Decompose generator/likelihood integration mismatch on saved native truth."""

import json
from pathlib import Path
import numpy as np
from audit_proxima_a3_retrieval_residuals import bin_edges, rebin_energy_flux


def integrate_cells(wl, flux, left, right):
    edges = bin_edges(wl)
    values = []
    for lo, hi in zip(left, right):
        overlap = np.maximum(np.minimum(edges[1:], hi)-np.maximum(edges[:-1], lo), 0)
        np.testing.assert_allclose(overlap.sum(),hi-lo,atol=1e-10)
        values.append(np.dot(overlap,flux)/(hi-lo))
    return np.asarray(values)


def main():
    root = Path(__file__).resolve().parents[2]
    project = root / "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1"
    directory = project / "diagnostics/nh3_1000h_posterior_change_20261013"
    output = directory / "binning_components.json"
    if output.exists():
        raise RuntimeError("Diagnostic exists")
    with np.load(project / "forward_emission/A3_emission.npz") as saved:
        wl, flux = saved["wl_um"],saved["Fp_obs_W_m2_m"]
    with np.load(project / "lifesim/life_classic_binned_products.npz") as saved:
        centres=saved["wl_bins_um"]
    data=np.loadtxt(project/"life_data/LIFE_proxima_A3_1000h_O2_fixedBlack1bar_official.dat",skiprows=1)
    edges=bin_edges(centres)
    photon_mid=rebin_energy_flux(wl,flux,centres)
    energy_mid=integrate_cells(wl,flux,edges[:-1],edges[1:])
    energy_sym=integrate_cells(wl,flux,data[:,0]-data[:,1],data[:,0]+data[:,1])
    operators=json.loads((directory/"binning_operator.json").read_text())
    total=np.asarray(operators["1000"]["discrepancy_per_bin_sigma"])
    weighting=(energy_mid-photon_mid)/data[:,3]
    recentering=(energy_sym-energy_mid)/data[:,3]
    discretization=total-weighting-recentering
    rows={}
    for key,delta in (("total_actual_operator_minus_generator",total),
                      ("energy_vs_photon_weighting_same_midpoint_bins",weighting),
                      ("symmetric_exported_bins_vs_true_midpoint_edges",recentering),
                      ("remaining_POSEIDON_integration_discretization",discretization)):
        rows[key]={"rms_sigma_1000h":float(np.sqrt(np.mean(delta**2))),
                   "max_abs_sigma_1000h":float(np.max(np.abs(delta))),
                   "values_sigma":delta.tolist()}
    report={"components":rows,"not_additive_in_chi2":"vectors add; component squared norms do not",
            "true_bin_midpoint_offset_um":(((edges[:-1]+edges[1:])/2)-centres).tolist(),
            "max_symmetric_bin_edge_shift_um":float(np.max(np.abs((edges[:-1]+edges[1:])/2-centres))),
            "generator_uses_midpoint_edges":"spectres(wl_centres); generally asymmetric around log-spaced centre",
            "retrieval_uses_symmetric_edges":"centre +/- half_width; half_width alone loses midpoint displacement"}
    output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({key:{k:v for k,v in item.items() if k!="values_sigma"} for key,item in rows.items()},indent=2))
    print("Maximum midpoint shift um:",report["max_symmetric_bin_edge_shift_um"])


if __name__=="__main__":
    main()
