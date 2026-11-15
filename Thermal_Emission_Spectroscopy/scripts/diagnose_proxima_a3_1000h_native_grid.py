"""Check the failed 1000 h preflight on the generator's exact wavelength grid.

This single truth forward is a numerical diagnostic, not another retrieval.
It never changes the frozen dataset, runner, priors or original products.
"""

import json
import os
from pathlib import Path

# Resolve the same input libraries as the official Ubuntu retrieval launcher.
# These must be set before POSEIDON imports pysynphot and opacity readers.
os.environ.setdefault("POSEIDON_input_data", "/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs")
os.environ.setdefault("PYSYN_CDBS", "/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids")
for thread_variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[thread_variable] = "1"

import numpy as np
from POSEIDON.core import make_atmosphere, compute_spectrum

import emission_forward as ef
from audit_proxima_a3_retrieval_residuals import rebin_energy_flux


def main():
    project = ef.REPO / "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1"
    campaign = project / "retrievals/a3_1000h_full_20261011"
    output = campaign / "native_grid_diagnostic.json"
    if output.exists():
        raise RuntimeError("Diagnostic exists; preserve it")
    with np.load(project / "forward_emission/A3_emission.npz") as saved:
        wl = saved["wl_um"]
        saved_flux = saved["Fp_obs_W_m2_m"]
    data = np.loadtxt(project / "life_data/LIFE_proxima_A3_1000h_O2_fixedBlack1bar_official.dat",
                      skiprows=1)
    with np.load(project / "lifesim/life_classic_binned_products.npz") as saved:
        bins = saved["wl_bins_um"]
    target = ef.PROXIMA_B
    model = ef.build_model("A3", target)
    planet = ef.build_planet(target)
    star = ef.build_star(wl, target)
    pressure, surface, reference, radius = ef.pressure_grid(target)
    temperature, chemistry = ef.load_profiles(model, pressure, "A3", target)
    print(f"[native-grid] {len(wl)} points; {wl[0]}--{wl[-1]} um", flush=True)
    opacities = ef.read_opacities_for(model, wl)
    atmosphere = make_atmosphere(
        planet, model, pressure, reference, radius,
        surface_params=np.array([np.log10(surface)]),
        T_input=temperature, X_input=chemistry,
    )
    candidate = compute_spectrum(planet, star, model, atmosphere, opacities, wl,
                                 spectrum_type="direct_emission")
    delta = (rebin_energy_flux(wl, candidate, bins)
             - rebin_energy_flux(wl, saved_flux, bins)) / data[:, 3]
    report = {"native_points": len(wl), "wl_min": float(wl[0]),
              "wl_max": float(wl[-1]), "rms_sigma": float(np.sqrt(np.mean(delta**2))),
              "max_sigma": float(np.max(np.abs(delta))),
              "max_relative_native": float(np.max(np.abs(candidate / saved_flux - 1))),
              "finite": bool(np.isfinite(candidate).all()),
              "previous_preflight_rms_sigma": 0.7963,
              "interpretation": "Truth-forward grid consistency only; no sampling"}
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report), flush=True)


if __name__ == "__main__":
    main()
