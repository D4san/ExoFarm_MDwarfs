"""Authorized isolated binning closure and thermal-profile controls for A3.

Stage one fits T(P) directly, with no use of observed fluxes in the objective.
Stage two computes three deterministic forwards with vertical chemistry fixed
and re-evaluates one archived parameter vector through the actual forward-model
entry. It never runs MultiNest, changes noise, or accepts old retrievals.
"""

import argparse
import hashlib
import inspect
import json
import os
from pathlib import Path
import sys

os.environ.setdefault(
    "POSEIDON_input_data",
    "/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs",
)
os.environ.setdefault(
    "PYSYN_CDBS", os.environ["POSEIDON_input_data"] + "/stellar_grids",
)
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
import POSEIDON.core as poseidon_core
import POSEIDON.retrieval as poseidon_retrieval
from POSEIDON.core import compute_spectrum, define_model, load_data

import emission_forward as ef
from audit_proxima_a3_retrieval_residuals import rebin_energy_flux
from life_bin_operator_diagnostic import LifePhotonOperator, bind_poseidon_binning

ROOT = ef.REPO
PROJECT = ROOT / "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1"
FULL = PROJECT / "retrievals/a3_1000h_full_20261011/native_grid_retry"
OUTPUT = PROJECT / "diagnostics/A3_binning_PT_controls_20261014"
DATASET = PROJECT / "life_data/LIFE_proxima_A3_1000h_O2_fixedBlack1bar_official.dat"
PT_NAMES = ("a1", "a2", "log_P1", "log_P2", "log_P3", "T_ref")
P_PARAM_SET = 1.0e-2
sys.path.insert(0, str(ROOT / "Transmission_Spectroscopy/notebooks"))
from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(filename, value):
    (OUTPUT / filename).write_text(json.dumps(value, indent=2, allow_nan=False)
                                  + "\n", encoding="utf-8")


def state(stage):
    write_json("execution_state.json", {
        "stage": stage, "pid": os.getpid(), "new_retrievals": 0,
        "instrumental_noise_in_scope": False,
    })
    print(stage, flush=True)


def load_inputs():
    configuration = json.loads((FULL / "resolved_configuration.json").read_text())
    with np.load(PROJECT / "forward_emission/A3_emission.npz") as saved:
        wavelength = saved["wl_um"]
        native_truth = saved["Fp_obs_W_m2_m"]
    with np.load(PROJECT / "lifesim/life_classic_binned_products.npz") as saved:
        centres = saved["wl_bins_um"]
        life_truth = saved["flux_binned_A3"] * 6.62607015e-34 * 299792458.0
        life_truth /= centres * 1e-6
    data = np.loadtxt(DATASET, skiprows=1)
    operator = LifePhotonOperator.build(wavelength, centres)
    np.testing.assert_allclose(data[:, 0], centres, rtol=0, atol=5e-6)
    np.testing.assert_allclose(data[:, 1], np.diff(operator.edges_um) / 2,
                               rtol=0, atol=5e-6)
    if data.shape != (31, 4) or not np.isfinite(data).all():
        raise ValueError("Unexpected or nonfinite A3 dataset")
    if digest(DATASET) != configuration["dataset_sha256"]:
        raise ValueError("Dataset no longer matches the archived retrieval")
    return configuration, wavelength, native_truth, centres, life_truth, data, operator


def thermal_profile(pressure, parameters):
    if parameters[4] < max(parameters[2], parameters[3]):
        raise ValueError("Madhu pressure ordering invalid")
    rough = poseidon_atmosphere.compute_T_Madhu(
        pressure, *parameters, P_PARAM_SET,
    )
    return gaussian_filter1d(rough, sigma=3, axis=0, mode="nearest")[:, 0, 0]


def temperature_metrics(profile, truth, pressure):
    difference = profile - truth
    return {
        "rms_K_all_log_spaced_layers": float(np.sqrt(np.mean(difference ** 2))),
        "max_abs_K_all_layers": float(np.max(np.abs(difference))),
        "min_K": float(profile.min()), "max_K": float(profile.max()),
        "rms_K_1e_minus4_to_1bar": float(np.sqrt(
            np.mean(difference[pressure >= 1e-4] ** 2))),
    }


def fit_thermal_profile(pressure, truth, configuration):
    """Finite multi-start approximation, not proof of a global minimum."""
    bounds = np.array([configuration["prior_ranges"][name]
                       for name in PT_NAMES], dtype=float)

    def decode(unit_coordinates):
        return bounds[:, 0] + unit_coordinates * np.diff(bounds, axis=1)[:, 0]

    def objective(unit_coordinates):
        parameters = decode(unit_coordinates)
        try:
            profile = thermal_profile(pressure, parameters)
        except ValueError:
            return 1e12
        if not np.isfinite(profile).all() or profile.min() <= 100:
            return 1e12
        return float(np.mean((profile - truth) ** 2))

    constraints = [
        {"type": "ineq", "fun": lambda unit: decode(unit)[4] - decode(unit)[2]},
        {"type": "ineq", "fun": lambda unit: decode(unit)[4] - decode(unit)[3]},
    ]
    attempts = []
    for seed in (20261014, 20261015):
        result = optimize.differential_evolution(
            objective, [(0.0, 1.0)] * 6, seed=seed, maxiter=350,
            popsize=10, tol=1e-8, polish=False, workers=1,
        )
        polished = optimize.minimize(
            objective, result.x, method="SLSQP", bounds=[(0.0, 1.0)] * 6,
            constraints=constraints, options={"maxiter": 1200, "ftol": 1e-9},
        )
        chosen = polished if polished.fun < result.fun else result
        parameters = decode(chosen.x)
        profile = thermal_profile(pressure, parameters)
        if not np.isfinite(profile).all() or objective(chosen.x) >= 1e12:
            raise ValueError("No admissible thermal approximation found")
        attempts.append({
            "seed": seed, "parameters": parameters.tolist(),
            "temperature_mse_K2": float(chosen.fun),
            "de_success": bool(result.success), "de_message": str(result.message),
            "de_evaluations": int(result.nfev),
            "polish_success": bool(polished.success),
            "polish_message": str(polished.message),
            "polish_evaluations": int(polished.nfev),
        })
    best = min(attempts, key=lambda row: row["temperature_mse_K2"])
    return np.array(best["parameters"]), {
        "objective": "mean squared T error over 100 equally log-spaced layers",
        "uses_observed_flux_or_sigma": False,
        "bounds": dict(zip(PT_NAMES, bounds.tolist())),
        "P_param_set_bar": P_PARAM_SET, "gaussian_sigma_layers": 3,
        "attempts": attempts, "selected": best,
        "global_optimum_proven": False,
    }


def protected_paths(configuration):
    name = configuration["model_name"]
    return [
        PROJECT / "forward_emission/A3_emission.npz",
        PROJECT / "lifesim/life_classic_binned_products.npz", DATASET,
        ef.PROFILES_DIR / "Proxima_b_A3_Extreme_PT.txt",
        ef.PROFILES_DIR / "Proxima_b_A3_Extreme_chem.txt",
        FULL / "resolved_configuration.json", FULL / "campaign_state.json",
        FULL / f"products/MultiNest_raw/{name}-post_equal_weights.dat",
        PROJECT / "retrievals/a0_fixed_reference_A3_1000h_20261012/campaign_state.json",
        Path(ef.__file__), Path(__file__),
        Path(__file__).with_name("life_bin_operator_diagnostic.py"),
        Path(__file__).with_name("test_life_bin_operator_diagnostic.py"),
        Path(poseidon_atmosphere.__file__), Path(poseidon_core.__file__),
        Path(poseidon_retrieval.__file__),
        Path(poseidon_core.__file__).with_name("instrument.py"),
        Path(__file__).with_name("run_life_retrieval.py"),
        Path(__file__).with_name("make_life_datasets.py"),
    ]


def check_hashes():
    protected = json.loads((OUTPUT / "preserved_inputs.json").read_text())
    for path, expected in protected.items():
        if digest(Path(path)) != expected:
            raise RuntimeError(f"Protected input changed: {path}")


def setup():
    if OUTPUT.exists():
        raise RuntimeError("Diagnostic already exists; preserve it")
    OUTPUT.mkdir(parents=True)
    inputs = load_inputs()
    config, wl, flux, centres, life, observed, operator = inputs
    write_json("selected_scope.json", {
        "authorization": "User approves isolated binning and PT diagnostics; excludes noise",
        "binning": "generator-compatible overlap operator, process-local diagnostic binding",
        "PT_controls": ["true vertical", "Madhu approximation to true T(P)",
                        "archived best-point 1000h Madhu with chemistry fixed"],
        "new_retrievals": 0, "change_existing_datasets": False,
        "change_installed_POSEIDON": False, "change_noise": False,
        "other_species_controls": "not launched in this diagnostic",
    })
    write_json("preserved_inputs.json", {str(path): digest(path)
                                          for path in protected_paths(config)})
    data = load_data(str(DATASET.parent), [DATASET.name], ["LIFE"], wl,
                     skiprows=1, wl_unit="micron", bin_width="half",
                     spectrum_unit="Fp")
    old = poseidon_retrieval.bin_spectrum_to_data(flux, wl, data)
    original_function = poseidon_retrieval.bin_spectrum_to_data
    with bind_poseidon_binning(operator) as retrieval:
        if retrieval.forward_model.__globals__["bin_spectrum_to_data"] != retrieval.bin_spectrum_to_data:
            raise RuntimeError("The actual forward-model entry did not bind")
        matched = retrieval.bin_spectrum_to_data(flux, wl, data)
    if poseidon_retrieval.bin_spectrum_to_data is not original_function:
        raise RuntimeError("Process-local operator was not restored")
    np.testing.assert_allclose(matched, life, rtol=1e-12, atol=0)
    np.testing.assert_allclose(matched, rebin_energy_flux(wl, flux, centres),
                               rtol=1e-12, atol=0)
    report = {
        "operator_closure_max_relative": float(np.max(np.abs(matched / life - 1))),
        "legacy_vs_truth_rms_sigma": float(np.sqrt(np.mean(((old - life) / observed[:, 3]) ** 2))),
        "legacy_vs_truth_max_sigma": float(np.max(np.abs((old - life) / observed[:, 3]))),
        "corrected_truth_chi2": float(np.sum(((observed[:, 2] - matched) / observed[:, 3]) ** 2)),
        "legacy_truth_chi2": float(np.sum(((observed[:, 2] - old) / observed[:, 3]) ** 2)),
        "actual_forward_model_global_bound_and_restored": True,
        "official_code_or_data_changed": False,
    }
    write_json("binning_closure.json", report)
    np.savez(OUTPUT / "operator.npz", native_um=wl, centres_um=centres,
             edges_um=operator.edges_um, rows=operator.rows,
             columns=operator.columns, weights=operator.weights)
    state("BINNING_CLOSURE_PASS; fitting T(P) without observing a spectrum")
    model = ef.build_model("A3", ef.PROXIMA_B)
    pressure, _, _, _ = ef.pressure_grid(ef.PROXIMA_B)
    temperature, chemistry = ef.load_profiles(model, pressure, "A3", ef.PROXIMA_B)
    truth_T = temperature.reshape(-1)
    parameters, fit_report = fit_thermal_profile(pressure, truth_T, config)
    raw = np.loadtxt(FULL / f"products/MultiNest_raw/{config['model_name']}-post_equal_weights.dat")
    if raw.shape[1] != len(config["parameters"]) + 1 or not np.isfinite(raw).all():
        raise ValueError("Unexpected archived equal-weight posterior")
    best_point = raw[np.argmax(raw[:, -1]), :-1]
    recovered = best_point[[config["parameters"].index(name) for name in PT_NAMES]]
    fitted_T = thermal_profile(pressure, parameters)
    recovered_T = thermal_profile(pressure, recovered)
    fit_report["profile_metrics"] = {
        "Madhu_truth_approximation": temperature_metrics(fitted_T, truth_T, pressure),
        "Madhu_archived_bestpoint_1000h": temperature_metrics(recovered_T, truth_T, pressure),
    }
    fit_report["archived_bestpoint_PT_parameters"] = dict(zip(PT_NAMES, recovered.tolist()))
    write_json("thermal_approximation.json", fit_report)
    np.savez(OUTPUT / "thermal_inputs.npz", pressure_bar=pressure,
             true_T=truth_T, fitted_T=fitted_T, recovered_T=recovered_T,
             fitted_parameters=parameters, recovered_parameters=recovered,
             archived_bestpoint=best_point, true_X=chemistry)
    check_hashes()
    state("SETUP_COMPLETE; no opacity load, no new retrieval")
    print(json.dumps(report, indent=2), flush=True)
    print(json.dumps(fit_report["profile_metrics"], indent=2), flush=True)


def flux_metrics(binned, truth, observed):
    relative = binned / truth - 1
    scaled = (binned - truth) / observed[:, 3]
    return {
        "rms_relative": float(np.sqrt(np.mean(relative ** 2))),
        "max_relative": float(np.max(np.abs(relative))),
        "rms_difference_over_sigma": float(np.sqrt(np.mean(scaled ** 2))),
        "max_difference_over_sigma": float(np.max(np.abs(scaled))),
        "chi2_observed_given_control": float(np.sum(
            ((observed[:, 2] - binned) / observed[:, 3]) ** 2)),
    }


def forwards():
    if not OUTPUT.exists() or (OUTPUT / "forward_comparison.json").exists():
        raise RuntimeError("Setup required, or completed diagnostic already exists")
    check_hashes()
    config, wl, saved_flux, centres, life, observed, operator = load_inputs()
    stored = np.load(OUTPUT / "thermal_inputs.npz")
    model = ef.build_model("A3", ef.PROXIMA_B)
    pressure, surface, reference, radius = ef.pressure_grid(ef.PROXIMA_B)
    true_T, true_X = ef.load_profiles(model, pressure, "A3", ef.PROXIMA_B)
    np.testing.assert_array_equal(stored["true_X"], true_X)
    planet, star = ef.build_planet(ef.PROXIMA_B), ef.build_star(wl, ef.PROXIMA_B)
    profiles = {"true": stored["true_T"], "Madhu_truth_approximation": stored["fitted_T"],
                "Madhu_archived_bestpoint_1000h": stored["recovered_T"]}
    atmospheres = {
        name: ef.build_atmosphere(planet, model, pressure, reference, radius,
                                  surface, profile, true_X)
        for name, profile in profiles.items()
    }
    for name, atmosphere in atmospheres.items():
        np.testing.assert_array_equal(atmosphere["X"], atmospheres["true"]["X"])
        np.testing.assert_allclose(atmosphere["T"].reshape(-1), profiles[name],
                                   rtol=1e-12, atol=0)
    all_temperatures = np.concatenate(list(profiles.values()))
    if all_temperatures.min() < 180 or all_temperatures.max() > 310:
        raise ValueError("PT control exceeds frozen 180-310 K opacity interpolation grid")
    state("Loading one shared opacity table; all chemistry fixed exactly")
    opac = ef.read_opacities_for(model, wl)
    report = {
        "scope": "PT-only forward controls, common generator-compatible observation operator",
        "same_vertical_chemistry_all_controls": True,
        "same_geometry_surface_and_native_grid": True,
        "noise_modified": False, "comparisons": {},
    }
    arrays = {"wl_um": wl, "centres_um": centres, "life_Fp": life,
              "sigma_1000h": observed[:, 3], "observed_Fp": observed[:, 2],
              "pressure_bar": pressure}
    for name, atmosphere in atmospheres.items():
        state("Computing PT-only forward " + name)
        flux = compute_spectrum(planet, star, model, atmosphere, opac, wl,
                                spectrum_type="direct_emission")
        if not np.isfinite(flux).all():
            raise ValueError("Nonfinite PT-only forward")
        if name == "true":
            np.testing.assert_allclose(flux, saved_flux, rtol=1e-10, atol=0)
        with bind_poseidon_binning(operator) as retrieval:
            binned = retrieval.bin_spectrum_to_data(flux, wl, {
                "instruments": ["LIFE"], "wl_data": observed[:, 0],
                "half_bin": observed[:, 1],
            })
        report["comparisons"][name] = flux_metrics(binned, life, observed)
        arrays[name + "_native_Fp"] = flux
        arrays[name + "_binned_Fp"] = binned
        arrays[name + "_T"] = profiles[name]

    # Re-evaluate one archived full-model vector through the actual forward
    # function, not a new fit. This connects the candidate to the likelihood.
    retrieved_model = define_model(
        "A3_archived_vector_binning_diagnostic", ef.BULK_SPECIES, ef.PARAM_SPECIES,
        PT_profile="Madhu", X_profile="isochem", radius_unit="R_E", surface=True,
        thermal=True, thermal_scattering=False, error_inflation=None,
    )
    if list(retrieved_model["param_names"]) != config["parameters"]:
        raise ValueError("Archived full-model parameter order differs")
    np.testing.assert_array_equal(retrieved_model["chemical_species"], model["chemical_species"])
    data = load_data(str(DATASET.parent), [DATASET.name], ["LIFE"], wl,
                     skiprows=1, wl_unit="micron", bin_width="half", spectrum_unit="Fp")
    defaults = inspect.signature(poseidon_retrieval.run_retrieval).parameters
    state("Re-evaluating one archived vector through actual forward_model; no fitting")
    with bind_poseidon_binning(operator) as retrieval:
        binned, native, atmosphere, prior_TP = retrieval.forward_model(
            param_vector=stored["archived_bestpoint"], planet=planet, star=star,
            model=retrieved_model, opac=opac, data=data, wl=wl, P=pressure,
            P_ref_set=reference, R_p_ref_set=radius, P_param_set=P_PARAM_SET,
            He_fraction=defaults["He_fraction"].default,
            N_slice_EM=defaults["N_slice_EM"].default,
            N_slice_DN=defaults["N_slice_DN"].default,
            spectrum_type="direct_emission", T_phot_grid=None, T_het_grid=None,
            log_g_phot_grid=None, log_g_het_grid=None, I_phot_grid=None,
            I_het_grid=None, y_p=planet["planet_impact_parameter"] * star["R_s"],
            F_s_obs=star["F_star"] * (star["R_s"] / planet["system_distance"]) ** 2,
            constant_gravity=defaults["constant_gravity"].default, chemistry_grid=None,
        )
    np.testing.assert_allclose(binned, operator.apply(native), rtol=1e-12, atol=0)
    legacy = poseidon_retrieval.bin_spectrum_to_data(native, wl, data)
    report["archived_vector_re_evaluation"] = {
        "not_a_new_fit": True, "ln_prior_TP": float(prior_TP),
        "legacy_chi2_same_vector": float(np.sum(((observed[:, 2] - legacy) / observed[:, 3]) ** 2)),
        "candidate_chi2_same_vector": float(np.sum(((observed[:, 2] - binned) / observed[:, 3]) ** 2)),
        "actual_forward_model_uses_candidate_exactly": True,
    }
    arrays["archived_full_vector_native_Fp"] = native
    arrays["archived_full_vector_matched_Fp"] = binned
    arrays["archived_full_vector_legacy_Fp"] = legacy
    check_hashes()
    write_json("forward_comparison.json", report)
    np.savez(OUTPUT / "forward_controls.npz", **arrays)
    plt.rcParams.update({"font.family": "serif", "font.serif": ["STIXGeneral"],
                         "mathtext.fontset": "stix", "font.size": 11})
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    labels = {"true": "VULCAN verdadero",
              "Madhu_truth_approximation": "Madhu aproximando T(P) verdadero",
              "Madhu_archived_bestpoint_1000h": "Madhu del punto archivado 1000 h"}
    colours = {"true": "black", "Madhu_truth_approximation": PALETTE["deep_space_blue"],
               "Madhu_archived_bestpoint_1000h": PALETTE["golden_orange"]}
    for name in profiles:
        axes[0].plot(profiles[name], pressure, color=colours[name], label=labels[name])
        if name != "true":
            binned = arrays[name + "_binned_Fp"]
            axes[1].plot(centres, 100 * (binned / life - 1), ".-", color=colours[name])
            axes[2].plot(centres, (binned - life) / observed[:, 3], ".-", color=colours[name])
    axes[0].set(yscale="log", ylim=(1, ef.PROXIMA_B.P_min_bar),
                xlabel="Temperatura (K)", ylabel="Presión (bar)")
    axes[0].legend(fontsize=8)
    axes[1].set(xlabel="Longitud de onda (μm)", ylabel="Cambio del flujo (%)")
    axes[2].set(xlabel="Longitud de onda (μm)", ylabel="Cambio / σ (1000 h)")
    for ax in axes[1:]:
        ax.axhline(0, color="0.5", lw=0.8)
        ax.axvspan(9.5, 11.5, color=PALETTE["sunlit_clay"], alpha=0.18)
    for ax in axes:
        ax.grid(alpha=0.15)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("A3: aislar P–T con química vertical y binning coherente")
    fig.text(0.5, 0.01, "Química y geometría fijas; ajuste de T(P), no retrieval. Cambio/σ no es detección.",
             ha="center", fontsize=10)
    fig.tight_layout(rect=(0, 0.035, 1, 0.93))
    fig.savefig(OUTPUT / "PT_only_comparison.png", dpi=180)
    fig.savefig(OUTPUT / "PT_only_comparison.pdf")
    state("COMPLETE_DIAGNOSTIC_ONLY")
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--setup-only", action="store_true")
    selection.add_argument("--forwards", action="store_true")
    args = parser.parse_args()
    if args.setup_only:
        setup()
    else:
        forwards()
