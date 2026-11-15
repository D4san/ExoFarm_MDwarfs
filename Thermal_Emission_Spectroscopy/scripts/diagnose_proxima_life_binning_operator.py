"""Compare the actual POSEIDON likelihood binning with the LIFE generator.

No opacity loading or new forward/retrieval: both operators act on the same
saved native truth and saved posterior-median spectra. Outputs are diagnostic.
"""

import json
import os
from pathlib import Path

os.environ.setdefault("POSEIDON_input_data", "/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs")
os.environ.setdefault("PYSYN_CDBS", "/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids")
for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[name] = "1"

import numpy as np
from POSEIDON.core import load_data
from POSEIDON.instrument import bin_spectrum_to_data
from audit_proxima_a3_retrieval_residuals import rebin_energy_flux
from run_proxima_molecule_ablation_campaign import DATASETS, RESULTS_REL


def main():
    root = Path(__file__).resolve().parents[2]
    project = root / "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1"
    output = project / "diagnostics/nh3_1000h_posterior_change_20261013/binning_operator.json"
    if output.exists():
        raise RuntimeError("Diagnostic already exists")
    with np.load(project / "forward_emission/A3_emission.npz") as saved:
        wl, flux = saved["wl_um"], saved["Fp_obs_W_m2_m"]
    with np.load(project / "lifesim/life_classic_binned_products.npz") as saved:
        centres = saved["wl_bins_um"]
    truth = rebin_energy_flux(wl, flux, centres)
    report = {}
    for hours in (100, 1000):
        if hours == 100:
            source = DATASETS["A3", 100]
            file = project / "life_data" / source["file"]
            stem = source["full_results"].removesuffix("_results.txt")
            samples = root / RESULTS_REL.parent / "samples"
        else:
            file = project / "life_data/LIFE_proxima_A3_1000h_O2_fixedBlack1bar_official.dat"
            full = project / "retrievals/a3_1000h_full_20261011/native_grid_retry"
            stem = json.loads((full / "resolved_configuration.json").read_text())["model_name"]
            samples = full / "products/samples"
        observed = np.loadtxt(file, skiprows=1)
        native_data = load_data(str(file.parent), [file.name], ["LIFE"], wl,
                               skiprows=1, wl_unit="micron", bin_width="half", spectrum_unit="Fp")
        native_truth_binned = bin_spectrum_to_data(flux, wl, native_data)
        discrepancy = (native_truth_binned-truth)/observed[:, 3]
        spectrum = np.loadtxt(samples / (stem + "_spectrum_retrieved.txt"), skiprows=1)
        median_data = load_data(str(file.parent), [file.name], ["LIFE"], spectrum[:,0],
                               skiprows=1, wl_unit="micron", bin_width="half", spectrum_unit="Fp")
        median = bin_spectrum_to_data(spectrum[:,3],spectrum[:,0],median_data)
        report[str(hours)] = {
            "actual_POSEIDON_truth_vs_generator_rms_sigma": float(np.sqrt(np.mean(discrepancy**2))),
            "actual_POSEIDON_truth_vs_generator_max_sigma": float(np.max(np.abs(discrepancy))),
            "actual_POSEIDON_truth_chi2": float(np.sum(((observed[:,2]-native_truth_binned)/observed[:,3])**2)),
            "actual_POSEIDON_median_chi2": float(np.sum(((observed[:,2]-median)/observed[:,3])**2)),
            "operator_max_relative_difference": float(np.max(np.abs(native_truth_binned/truth-1))),
            "discrepancy_per_bin_sigma": discrepancy.tolist(),
            "actual_median_residual_per_bin_sigma": ((observed[:,2]-median)/observed[:,3]).tolist(),
            "psf_sigma_pixels_range": [float(np.min(native_data["psf_sigma"])),float(np.max(native_data["psf_sigma"]))],
        }
    output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({key:{k:v for k,v in row.items() if not isinstance(v,list)} for key,row in report.items()},indent=2))


if __name__ == "__main__":
    main()
