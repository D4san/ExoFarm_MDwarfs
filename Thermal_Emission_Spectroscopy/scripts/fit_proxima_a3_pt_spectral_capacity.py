"""Fit only Madhu T(P) to the saved noiseless A3 spectrum, not a retrieval.

Vertical chemistry, planet geometry, surface and the LIFE operator are frozen.
The declared 1000 h errors only weight a deterministic approximation to the
known truth. No observed noise realization enters the objective; no evidence,
new noise or posterior is generated.
"""

import hashlib
import json
import os
from pathlib import Path
import sys

os.environ.setdefault("POSEIDON_input_data",
                      "/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs")
os.environ.setdefault("PYSYN_CDBS", os.environ["POSEIDON_input_data"] + "/stellar_grids")
for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS"):
    os.environ[variable] = "1"

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize
from scipy.ndimage import gaussian_filter1d
import POSEIDON.atmosphere as poseidon_atmosphere
from POSEIDON.core import compute_spectrum

import emission_forward as ef
from life_bin_operator_diagnostic import LifePhotonOperator

ROOT = ef.REPO
PROJECT = ROOT / "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1"
PREVIOUS = PROJECT / "diagnostics/A3_binning_PT_controls_20261014"
OUTPUT = PROJECT / "diagnostics/A3_PT_spectral_capacity_20261014"
FULL = PROJECT / "retrievals/a3_1000h_full_20261011/native_grid_retry"
PT_NAMES = ("a1", "a2", "log_P1", "log_P2", "log_P3", "T_ref")
sys.path.insert(0, str(ROOT / "Transmission_Spectroscopy/notebooks"))
from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(filename, value):
    (OUTPUT / filename).write_text(json.dumps(value, indent=2, allow_nan=False)
                                  + "\n", encoding="utf-8")


def state(stage, evaluations=0):
    write_json("execution_state.json", {
        "stage": stage, "pid": os.getpid(), "forward_evaluations": evaluations,
        "new_retrievals": 0, "instrumental_noise_in_scope": False,
    })
    print(stage, flush=True)


def main():
    if OUTPUT.exists():
        raise RuntimeError("Spectral-capacity diagnostic exists; preserve it")
    OUTPUT.mkdir(parents=True)
    write_json("selected_scope.json", {
        "authorization": "User continues binning/PT diagnostics; noise excluded",
        "free_coordinates": list(PT_NAMES),
        "target": "saved noiseless A3 LIFE Fp, not the noisy observation",
        "weights": "unchanged declared 1000h sigma",
        "chemistry": "all original VULCAN vertical species, exactly fixed",
        "geometry_surface_grid": "true and fixed",
        "new_retrievals": 0, "new_evidence_or_posterior": False,
        "new_noise": False, "new_PT_family": False,
        "max_nfev_per_start": 50, "number_of_starts": 2,
        "numerical_temperature_domain_K": [100, 400],
    })
    config = json.loads((FULL / "resolved_configuration.json").read_text())
    sources = [Path(__file__), Path(ef.__file__),
               Path(__file__).with_name("life_bin_operator_diagnostic.py"),
               Path(poseidon_atmosphere.__file__),
               PREVIOUS / "thermal_inputs.npz", PREVIOUS / "forward_controls.npz",
               PREVIOUS / "binning_closure.json", FULL / "resolved_configuration.json",
               PROJECT / "forward_emission/A3_emission.npz",
               PROJECT / "lifesim/life_classic_binned_products.npz",
               PROJECT / "life_data/LIFE_proxima_A3_1000h_O2_fixedBlack1bar_official.dat",
               ef.PROFILES_DIR / "Proxima_b_A3_Extreme_PT.txt",
               ef.PROFILES_DIR / "Proxima_b_A3_Extreme_chem.txt"]
    hashes = {str(path): digest(path) for path in sources}
    write_json("preserved_inputs.json", hashes)
    previous = np.load(PREVIOUS / "forward_controls.npz")
    thermal = np.load(PREVIOUS / "thermal_inputs.npz")
    wl, centres = previous["wl_um"], previous["centres_um"]
    target, sigma = previous["life_Fp"], previous["sigma_1000h"]
    operator = LifePhotonOperator.build(wl, centres)
    model = ef.build_model("A3", ef.PROXIMA_B)
    planet, star = ef.build_planet(ef.PROXIMA_B), ef.build_star(wl, ef.PROXIMA_B)
    pressure, surface, reference, radius = ef.pressure_grid(ef.PROXIMA_B)
    true_T, true_X = ef.load_profiles(model, pressure, "A3", ef.PROXIMA_B)
    np.testing.assert_array_equal(true_X, thermal["true_X"])
    # Extend only the interpolation envelope, keeping every original 10-K
    # node. Truth must reproduce the original table before any optimization.
    T_fine = np.arange(100.0, 400.0 + 10.0, 10.0)
    write_json("opacity_interpolation.json", {
        "T_fine_K": T_fine.tolist(),
        "prior_interpolation_nodes_retained": "180..310 K, every 10 K",
        "reason": "numerical coverage during optimization, not new opacity physics",
        "out_of_domain_candidates": "rejected and counted",
        "global_PT_capability_proven": False,
    })
    state("Loading shared opacities; extending temperature interpolation to 100-400 K")
    opac = ef.read_opacities_for(model, wl, T_fine=T_fine)
    truth_atmosphere = ef.build_atmosphere(
        planet, model, pressure, reference, radius, surface, true_T, true_X,
    )
    repeated = compute_spectrum(planet, star, model, truth_atmosphere, opac, wl,
                               spectrum_type="direct_emission")
    np.testing.assert_allclose(repeated, previous["true_native_Fp"], rtol=1e-10, atol=0)
    np.testing.assert_allclose(operator.apply(repeated), target, rtol=1e-12, atol=0)
    bounds = np.array([config["prior_ranges"][name] for name in PT_NAMES], dtype=float)
    spans = bounds[:, 1] - bounds[:, 0]
    evaluation_count, invalid_count = 0, 0
    history = []
    best = None

    def decode(unit):
        return bounds[:, 0] + unit * spans

    def residual(unit):
        nonlocal evaluation_count, invalid_count, best
        parameters = decode(unit)
        if parameters[4] < max(parameters[2], parameters[3]):
            invalid_count += 1
            return np.full(target.size, 1e6)
        rough = poseidon_atmosphere.compute_T_Madhu(pressure, *parameters, 0.01)
        temperature = gaussian_filter1d(rough, sigma=3, axis=0, mode="nearest")[:, 0, 0]
        if (not np.isfinite(temperature).all() or temperature.min() < 100
                or temperature.max() > 400):
            invalid_count += 1
            return np.full(target.size, 1e6)
        atmosphere = ef.build_atmosphere(
            planet, model, pressure, reference, radius, surface, temperature, true_X,
        )
        np.testing.assert_array_equal(atmosphere["X"], truth_atmosphere["X"])
        flux = compute_spectrum(planet, star, model, atmosphere, opac, wl,
                                spectrum_type="direct_emission")
        if not np.isfinite(flux).all():
            raise RuntimeError("Nonfinite spectrum in an admissible PT candidate")
        binned = operator.apply(flux)
        difference = (binned - target) / sigma
        value = float(difference @ difference)
        evaluation_count += 1
        history.append({"evaluation": evaluation_count, "parameters": parameters.tolist(),
                        "weighted_template_squared_norm": value})
        if best is None or value < best["value"]:
            best = {"value": value, "parameters": parameters.copy(),
                    "temperature": temperature.copy(), "flux": flux.copy(),
                    "binned": binned.copy()}
        if evaluation_count % 10 == 0:
            state(f"PT-only spectral evaluations {evaluation_count}; best norm {best['value']:.6g}",
                  evaluation_count)
        return difference

    attempts = []
    starts = {"temperature_approximation": thermal["fitted_parameters"],
              "archived_PT": thermal["recovered_parameters"]}
    for name, parameters in starts.items():
        initial = (parameters - bounds[:, 0]) / spans
        start_residual = residual(initial)
        state("Optimizing only PT from " + name, evaluation_count)
        result = optimize.least_squares(
            residual, initial, bounds=(np.zeros(6), np.ones(6)), method="trf",
            x_scale="jac", diff_step=1e-4, max_nfev=50,
            ftol=1e-7, xtol=1e-7, gtol=1e-5,
        )
        final_residual = residual(result.x)
        attempts.append({
            "start": name, "success": bool(result.success), "status": int(result.status),
            "message": str(result.message), "nfev": int(result.nfev),
            "njev": int(result.njev), "optimality": float(result.optimality),
            "initial_weighted_norm": float(start_residual @ start_residual),
            "final_weighted_norm": float(final_residual @ final_residual),
            "final_parameters": decode(result.x).tolist(),
        })
    if best is None:
        raise RuntimeError("No admissible candidate")
    relative = best["binned"] / target - 1
    scaled = (best["binned"] - target) / sigma
    record = {
        "scope": "deterministic PT-only spectral capacity; no retrieval",
        "objective": "sum[(Fp_PT - Fp_noiseless_A3)/sigma_1000h]^2",
        "noisy_observation_used_in_objective": False,
        "number_of_starts": len(starts), "attempts": attempts,
        "actual_forward_evaluations": evaluation_count,
        "invalid_order_or_temperature_candidates": invalid_count,
        "finite_search_global_minimum_proven": False,
        "chemical_profiles_geometry_and_operator_fixed": True,
        "chosen_candidate": "lowest valid objective encountered, including finite-difference probes",
        "parameters": dict(zip(PT_NAMES, best["parameters"].tolist())),
        "weighted_template_squared_norm": best["value"],
        "rms_template_difference_over_sigma": float(np.sqrt(np.mean(scaled ** 2))),
        "max_template_difference_over_sigma": float(np.max(np.abs(scaled))),
        "rms_relative_flux": float(np.sqrt(np.mean(relative ** 2))),
        "max_relative_flux": float(np.max(np.abs(relative))),
        "rms_temperature_error_K": float(np.sqrt(np.mean(
            (best["temperature"] - true_T.reshape(-1)) ** 2))),
        "surface_temperature_error_K": float(best["temperature"][0] - true_T.reshape(-1)[0]),
        "noise_changed": False, "new_retrievals": 0,
    }
    for path, expected in hashes.items():
        if digest(Path(path)) != expected:
            raise RuntimeError("Protected input changed: " + path)
    write_json("spectral_capacity.json", record)
    write_json("optimization_history.json", history)
    np.savez(OUTPUT / "best_control.npz", wl_um=wl, centres_um=centres,
             pressure_bar=pressure, true_T=true_T.reshape(-1), best_T=best["temperature"],
             true_native_Fp=repeated, best_native_Fp=best["flux"],
             target_Fp=target, best_binned_Fp=best["binned"], sigma_1000h=sigma)
    plt.rcParams.update({"font.family": "serif", "font.serif": ["STIXGeneral"],
                         "mathtext.fontset": "stix", "font.size": 11})
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    colour = PALETTE["deep_space_blue"]
    axes[0].plot(true_T.reshape(-1), pressure, "k--", label="P–T VULCAN")
    axes[0].plot(best["temperature"], pressure, color=colour, label="Madhu ajustando Fp")
    axes[0].set(yscale="log", ylim=(1, ef.PROXIMA_B.P_min_bar),
                xlabel="Temperatura (K)", ylabel="Presión (bar)")
    axes[0].legend(fontsize=9)
    axes[1].plot(centres, 100 * relative, ".-", color=colour)
    axes[1].set(xlabel="Longitud de onda (μm)", ylabel="Cambio del flujo (%)")
    axes[2].plot(centres, scaled, ".-", color=colour)
    axes[2].set(xlabel="Longitud de onda (μm)", ylabel="Diferencia / σ1000 h")
    axes[2].axhspan(-1, 1, color="0.9", zorder=-1)
    for ax in axes[1:]:
        ax.axhline(0, color="0.5", lw=0.8)
        ax.axvspan(9.5, 11.5, color=PALETTE["sunlit_clay"], alpha=0.2)
    for ax in axes:
        ax.grid(alpha=0.15)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("A3: capacidad espectral P–T con química vertical fija")
    fig.text(0.5, 0.01, "Se ajusta al espectro sin ruido; búsqueda finita, no retrieval ni detección.",
             ha="center", fontsize=10)
    fig.tight_layout(rect=(0, 0.035, 1, 0.93))
    fig.savefig(OUTPUT / "spectral_capacity.png", dpi=180)
    fig.savefig(OUTPUT / "spectral_capacity.pdf")
    state("COMPLETE_DIAGNOSTIC_ONLY", evaluation_count)
    print(json.dumps(record, indent=2), flush=True)


if __name__ == "__main__":
    main()
