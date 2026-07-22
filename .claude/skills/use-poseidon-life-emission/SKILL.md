---
name: use-poseidon-life-emission
description: "Use when working on ExoFarm Stage III (thermal-emission / LIFE track): generating POSEIDON EMISSION spectra (spectrum_type='emission', Fp/Fs) from the VULCAN A0–A3 hand-off profiles, converting them to the radiance a LIFE simulator reads, and simulating mid-infrared noise / SNR with LIFEsim classic and/or LIFEsimMC+PHRINGE. Covers the POSEIDON→LIFE units interface, molecular counterfactual signals, band-integrated SNR, SNR-vs-integration-time, covariance/whitening, and the provenance/gate rules. NOT for transmission/JWST/PandExo work — that is Stage II."
---

# Use POSEIDON emission + LIFE noise for ExoFarm (Stage III)

Detailed, cited excerpts and the units contract live in
[`references/poseidon-emission-and-life-noise.md`](references/poseidon-emission-and-life-noise.md).
Read it before coding. Live docs are the source of truth; the LIFEsimMC docs
were reorganizing when this skill was written, so verify config-file and
custom-spectrum details against the current pages.

## Core rules (do not violate)

1. **LIFE reads emission, not transmission.** Use POSEIDON
   `spectrum_type='emission'` (returns **Fp/Fs**, dimensionless). Never feed
   transmission depth `(Rp/Rs)^2`, PandExo `.dat`, or transit counts into a LIFE
   scene. Stage III products live only under
   `Thermal_Emission_Spectroscopy/outputs/<campaign-id>/`.
2. **The POSEIDON→LIFE units conversion is a mandatory gate.** Validate the
   chain Fp/Fs → observed flux → radiance on a noise-free A0 case before any
   noisy run. A nice-looking plot is not a units proof. Note the two LIFE tools
   want **different** y-units:
   - LIFEsim classic: `photon micron-1 s-1 m-2 sr-1` (photon radiance).
   - LIFEsimMC: `W sr-1 m-2 micron-1` (energy radiance). Convert with `hc/λ`.
3. **SNR is a diagnostic, not a detection.** Do not launch LIFE retrievals until
   forward + molecular counterfactuals + noise + SNR are validated AND a campaign
   manifest exists in `experiments/README.md`.
4. **Preserve covariance.** With LIFEsimMC instrumental noise, whiten (ZCA with
   a calibration star) or use a covariance-aware likelihood. Never silently
   collapse to diagonal σ.
5. **Carry provenance labels.** Earth–Sun A2/A3 profiles are frozen
   `earth_20260615_pre_n2o_correction` → interface validation only. TRAPPIST-1e
   keeps its `end_case=3` partial-convergence caveat and is a deferred LIFE
   control, not the clean primary case.

## First steps for any Stage III task

1. Recover state: read `docs/project_resume.md`, then
   `docs/project_status_tracker.md`, then
   `docs/life_stage_iii_two_layer_workplan_2026-07-20.md` and the provenance
   note. Confirm live `git status` and that no campaign is mid-run.
2. Confirm the environment: POSEIDON/lifesim/lifesimmc are **not** installed on
   this host (`Main_DFT` has only the base science stack; no 72 GB opacities).
   `pip install lifesim` / `lifesimmc` is lightweight; POSEIDON emission needs
   the heavy env or an external run. Decide where each step runs before coding.

## POSEIDON emission workflow (adapt, don't reuse, the transmission engine)

`Transmission_Spectroscopy/notebooks/exofarm_transmission_workflow.py` is a
**read-only reference** for the POSEIDON call skeleton and the VULCAN hand-off
(`read_PT_file`, `read_chem_file`, `file_read` PT/X). Build a separate emission
wrapper under `Thermal_Emission_Spectroscopy/scripts/`:

- `define_model(..., thermal=True, thermal_scattering=False)` and a real PT
  gradient (emission is PT-sensitive); keep `PT_profile='file_read'`,
  `X_profile='file_read'` for the VULCAN hand-off.
- `compute_spectrum(..., spectrum_type='emission')` → `Fp/Fs`.
- Load the canonical profiles listed in the two-layer workplan (Earth A0–A3
  `.vul` → `Transmission_Spectroscopy/profiles/Earth_*_{PT,chem}.txt`). Do not
  regenerate or duplicate `.vul`.

## Molecular signal (counterfactual) and SNR

- Signal: replace only the target molecule's profile with its A0 reference,
  keep all else fixed: `Δy_i(λ) = y_full(λ) − y_{i,ref}(λ)`. Targets `N2O`,
  `NH3`; keep `H2O`, `CO2`, `O3`, `CH4` as overlap/degeneracy controls.
- Band-integrated diagnostic SNR (independent σ only):
  `SNR_i,band = [ Σ_k (Δy_i(λ_k)/σ_k)^2 ]^{1/2}`.
- **S/N vs integration time:** LIFEsim classic gives SNR after 1 h and
  `SNR ∝ √t_int` — scale directly. For LIFEsimMC, re-run realizations per
  integration time rather than assuming √t.
- SNR tables must record scenario, molecule, band, integration time, LIFE
  config, seed/realization, signal definition, covariance method, and the
  source-spectrum path.

## Noise simulators

- **LIFEsim classic** (astrophysical/photon noise, yields): `Bus` +
  `Instrument` + `TransmissionMap` + `PhotonNoise{Star,Localzodi,Exozodi}`;
  `instrument.get_snr()`; results in `bus.data.catalog`. Custom spectrum `.txt`
  (`absolute`/`additive`), photon-radiance y-units, + distance/radius/int-time.
- **LIFEsimMC + PHRINGE** (instrumental instability, covariance): `Pipeline` +
  `SetupModule(Configuration(path=...))` + `DataGenerationModule` (PHRINGE) +
  `TemplateGenerationModule` + `ZCAWhiteningCalibrationStarModule` +
  extraction/test modules (`MLParameterEstimationModule`,
  `EnergyDetectorTestModule`, `NeymanPearsonTestModule`). Preset
  `SingleEpochObservation`. Preserve the covariance/whitening output.

Per the user's Phase-1 decision, run **both** simulators and **both** targets
(`life_earth_sun_10pc` and TRAPPIST-1e) as a comparison, honoring each target's
caveat above.

## Verification checklist before declaring a Stage III product

- Units/interface: noise-free A0 Fp/Fs → radiance chain shape/normalization test.
- Physical sanity: wavelength grid, radii, distance, flux/contrast/radiance
  definition, background scene declared.
- Provenance label present on every table/figure.
- Covariance treatment stated (diagonal σ only allowed for the ideal LIFEsim
  classic diagnostic; MC requires whitening).
- Manifest written before any expensive/noisy run.
