# POSEIDON emission + LIFE noise: verified doc excerpts and interface contract

**Compiled:** 2026-07-21 (Phase 2 of the LIFE extension). Source-derived facts
are tagged `[SRC]` with the URL checked; project inferences are tagged `[INF]`;
items to re-verify at implementation time are tagged `[VERIFY]`. Live docs are
the source of truth — re-check before coding, because the LIFEsimMC docs were
reorganizing when this was compiled (some tutorial URLs 404'd).

---

## 1. POSEIDON emission forward model

`[SRC]` https://poseidon-retrievals.readthedocs.io/en/latest/content/notebooks/emission_basic.html

Call order (same skeleton as the transmission engine
`Transmission_Spectroscopy/notebooks/exofarm_transmission_workflow.py`, with the
emission-specific changes in **bold**):

```python
from POSEIDON.core import (create_star, create_planet, define_model,
                           make_atmosphere, read_opacities, compute_spectrum,
                           wl_grid_constant_R)

wl   = wl_grid_constant_R(wl_min, wl_max, R)          # emission tutorial: 0.3–10 µm, R=10000
star = create_star(R_s, T_s, log_g_s, Met_s, wl=wl, stellar_grid='phoenix')
planet = create_planet(planet_name, R_p, mass=M_p, T_eq=T_eq)

model = define_model(model_name, bulk_species, param_species,
                     PT_profile='gradient',          # emission is very PT-sensitive
                     thermal=True,                    # << enables thermal emission
                     thermal_scattering=False)        # optional toggle

atmosphere = make_atmosphere(planet, model, P, P_ref, R_p_ref, PT_params, log_X_params)
opac = read_opacities(model, wl, opacity_treatment, T_fine, log_P_fine)

Fp_Fs = compute_spectrum(planet, star, model, atmosphere, opac, wl,
                         spectrum_type='emission')
```

Key facts:
- `[SRC]` Output of `spectrum_type='emission'` is the **secondary-eclipse
  contrast Fp/Fs** (dayside planet-to-star flux ratio), **dimensionless**
  (example range 0–5e-3). Plotting uses `y_unit='Fp/Fs'`,
  `spectrum_type='emission'`.
- `[SRC]` Emission requires a real vertical **temperature gradient** and a
  **stellar spectrum** (the routine normalizes Fp to F_star). Transmission in
  the current engine used isothermal-ish `file_read` PT; emission cares much
  more about the PT profile.
- `[INF]` For ExoFarm we keep the VULCAN hand-off: `PT_profile='file_read'`,
  `X_profile='file_read'` (as in the transmission engine) but add
  `thermal=True` and call with `spectrum_type='emission'`. The transmission
  wrapper's PHOENIX star + file-read profiles are a **reading reference, not a
  validated LIFE emission config** (repo rule).
- `[VERIFY]` Whether POSEIDON can return absolute planet flux `Fp` (not just
  Fp/Fs) directly, and in which units. The POSEIDON data reader accepts `Fp/Fs`
  or `Fp` with per-bin errors —
  https://poseidon-retrievals.readthedocs.io/en/latest/autoapi/POSEIDON/utility/index.html
- Surface handling for emission not covered in the basic tutorial `[VERIFY]`;
  the transmission engine used `surface=True` at 1 bar for TRAPPIST-1e.

---

## 2. The POSEIDON → LIFE interface (the units gate)

This adapter is a **mandatory gate** (repo docs). A "visually reasonable" plot
does not prove the units are right.

Chain to make explicit and test on a noise-free A0 case:

```
POSEIDON Fp/Fs (dimensionless)
   → planet flux at planet:  Fp(λ)  = (Fp/Fs) · F_star(λ)     [need F_star units]
   → observed flux at 10 pc: F_obs  = Fp · (R_p / d)^2 geometry (declare once)
   → spectral radiance for the LIFE input file (per-tool units below)
```

**Unit contract per tool (critical — the two LIFE tools differ):**

| Tool | Input spectrum file | x unit | y unit |
| --- | --- | --- | --- |
| LIFEsim classic `[SRC]` | `.txt`, modes `absolute`/`additive` | `micron` | **photon** spectral radiance `photon micron-1 s-1 m-2 sr-1` |
| LIFEsimMC `[SRC-repo]` | 2-column text | `micron` | **energy** radiance `W sr-1 m-2 micron-1` |

`[SRC-repo]` = quoted in `docs/life_lifesim_stage_iii_plan.md`, originally from
`lifesimmc.readthedocs.io/.../custom_spectrum.html` (URL now 404 → re-verify the
live page). **Do not assume the two tools take the same units**: classic wants
photon radiance, MC wants energy (W) radiance. Converting energy↔photon needs a
factor of photon energy `hc/λ`. Both also need distance, planet radius and
integration time supplied to the scene, not baked into the file.

---

## 3. LIFEsim classic (astrophysical/photon-noise, yields)

`[SRC]` https://lifesim.readthedocs.io/en/latest/example.html

```python
import lifesim
bus = lifesim.Bus()
bus.data.options.set_scenario('baseline')            # or set_manual(diameter=4., ...)
bus.data.catalog_from_ppop(input_path='ppop_catalog.txt')   # or a manual Star/Planet scene

instrument = lifesim.Instrument(name='inst'); bus.add_module(instrument)
transm  = lifesim.TransmissionMap(name='transm');        bus.add_module(transm)
exo     = lifesim.PhotonNoiseExozodi(name='exo');        bus.add_module(exo)
local   = lifesim.PhotonNoiseLocalzodi(name='local');    bus.add_module(local)
star_l  = lifesim.PhotonNoiseStar(name='star');          bus.add_module(star_l)
bus.connect(('inst','transm')); bus.connect(('inst','exo'))
bus.connect(('inst','local'));  bus.connect(('inst','star')); bus.connect(('star','transm'))

instrument.get_snr()                                  # SNR per planet after 1 h
```

- `[SRC]` Noise sources: stellar leakage, local zodi, exozodi, photon shot
  noise. Current LIFEsim assumes photon-noise-dominated (no instrumental
  instability).
- `[SRC]` `get_snr()` gives SNR after **1 hour**; **SNR ∝ √t_int**, so any
  integration time scales from the 1-hour value → directly answers Phase 3
  "S/N vs observation time".
- `[SRC]` Custom planet spectrum: `.txt`, x=`micron`, y=`photon micron-1 s-1
  m-2 sr-1`; modes `absolute` (use imported only) / `additive` (add to
  blackbody). Blackbody-only = additive with empty file. Also set Distance,
  Planet Radius, Integration Time.
- `[SRC]` Outputs in `bus.data.catalog` (pandas): `snr_1h`, `detected`,
  `int_time`; export via `bus.data.export_catalog(...hdf5)`. Options in
  `lifesim.util.options`.
- `[VERIFY]` Exact call to obtain **per-wavelength-bin** SNR of an input
  spectrum (vs the single-planet `snr_1h`). LIFE II (Dannert et al. 2022,
  A&A 664 A22) is the signal-simulation/extraction reference.

---

## 4. LIFEsimMC (instrumental instability + covariance)

`[SRC]` https://lifesimmc.readthedocs.io/en/latest/ ,
https://lifesimmc.readthedocs.io/en/latest/usage.html ,
Huber et al. 2025 (AJ 170 227, arXiv:2508.15756).

- `[SRC]` Monte-Carlo **end-to-end** simulator; **uses PHRINGE internally for
  data generation**. Explicitly evolves the instrument response in time to model
  **instrumental instability noise**; matched-filter extraction from full
  synthetic data; flexible instrument architectures (not only X-Array Double
  Bracewell); correlation maps, **full covariance estimates**, hypothesis tests.
- `[SRC]` Handles correlated errors via **ZCA whitening with a calibration
  star** (module `ZCAWhiteningCalibrationStarModule`; Huber et al. 2025).
- `[SRC]` Cannot run yields (use LIFEsim classic for yields). Compute-heavy;
  GPU-friendly.

Pipeline pattern `[SRC]` (usage.html):

```python
from lifesimmc.core.pipeline import Pipeline
from lifesimmc.core.modules.setup_module import SetupModule
from lifesimmc.core.entities.configuration import Configuration
from pathlib import Path

pipeline = Pipeline()
pipeline.add_module(SetupModule(n_config_out='config',
                                configuration=Configuration(path=Path('config.py'))))
# ... DataGenerationModule (PHRINGE), TemplateGenerationModule,
#     ZCAWhiteningCalibrationStarModule, MLParameterEstimationModule /
#     EnergyDetectorTestModule / NeymanPearsonTestModule ...
pipeline.run()
result = pipeline.get_resource('...')
```

- `[SRC]` Entities: `Observation`, `Instrument`, `Scene`, `Configuration`,
  `Sources` (Planet, Star, LocalZodi, ExoZodi). Preset: `SingleEpochObservation`.
- `[VERIFY]` Exact `Configuration` file keys (integration time, wavelength
  range, spectral resolving power, distance, array architecture, backgrounds)
  and the exact custom-spectrum loading call/units on the **live** docs — the
  config-file tutorial page was not reachable at compile time. Check the repo
  README of the `lifesimmc` package and `Sources`/`Planet` entity API.

---

## 5. SNR diagnostic (band-integrated) and interpretation rule

`[SRC]` `docs/life_lifesim_stage_iii_plan.md`. Define the molecular signal from
a counterfactual (replace only the target molecule's profile with the A0
reference, keep everything else fixed):
`Δy_i(λ) = y_full(λ) − y_{i,ref}(λ)`.

Ideal, independent per-bin uncertainties → band-integrated SNR (a **diagnostic,
not a detection**):

```
SNR_i,band = [ Σ_{k∈band} ( Δy_i(λ_k) / σ_k )^2 ]^{1/2}
```

With LIFEsimMC instrumental noise, data and models must be **whitened** (or use
a covariance-aware likelihood with matrix C); a table of σ_i alone is not
enough. SNR tables must record: scenario, molecule, band, integration time, LIFE
config, seed/realization, signal definition, covariance method, source-spectrum
path.

---

## 6. Targets and provenance caveats (both in scope per user decision)

- **`life_earth_sun_10pc`** (repo Layer 1): Earth–Sun A0–A3 at 10 pc. A2/A3 are
  the frozen `earth_20260615_pre_n2o_correction` set (N2O `3.35e9`/`1.20e10`,
  predating active BC `3.416e9`/`1.238e10`) → interface validation only, label
  every product; not the current matrix without a rerun/historical decision.
  See `docs/earth_sun_n2o_matrix_provenance_2026-07-20.md`.
- **TRAPPIST-1e** (user-requested transmission mirror): keep the
  partial-convergence `end_case=3` caveat; the repo classifies it as a
  **deferred** LIFE control, and LIFE X (Carrión-González 2023) shows it misses
  S/N=7 in 100 h for the reference architecture — so treat as comparison, not a
  clean primary molecular case.

## 7. Environment (this host)

POSEIDON, lifesim, lifesimmc are **not installed** here (only the `Main_DFT`
science stack; no 72 GB opacity tree). `lifesim`/`lifesimmc` are pip-installable
and lightweight; POSEIDON emission generation needs the heavy env or an external
run. See `CLAUDE.md` and the `host-environment` memory.

## Primary references
- POSEIDON emission tutorial (above).
- Dannert et al. 2022, LIFE II, A&A 664, A22 (signal simulation/extraction) —
  https://doi.org/10.1051/0004-6361/202141958
- Konrad et al. 2022, LIFE III, A&A 664, A23 (Earth twin at 10 pc; R/λ/sensitivity).
- Angerhausen et al. 2024, LIFE XII, AJ 167, 128 (N2O/laughing-gas detectability; TRAPPIST-1-like at 5 pc).
- Huber et al. 2025, AJ 170, 227, arXiv:2508.15756 (LIFEsimMC/PHRINGE, correlated errors, ZCA whitening).
- Carrión-González et al. 2023, LIFE X, A&A 678, A96 (known-target detectability; TRAPPIST-1e).
