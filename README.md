# ExoFarm: Agricultural Technosignatures in Earth-like Exoplanet Atmospheres

[![VULCAN](https://img.shields.io/badge/Model-VULCAN-blue)](https://github.com/exoclime/VULCAN)
[![Python](https://img.shields.io/badge/Python-3.x-yellow)]()

---

## Scientific Overview

This repository implements a modular modelling framework to assess whether large-scale agricultural activity could generate remotely detectable atmospheric technosignatures on Earth-like exoplanets. The central hypothesis is that anthropogenic perturbation of the nitrogen cycle, represented here by enhanced surface fluxes of nitrous oxide ($N_2O$) and ammonia ($NH_3$), can produce spectral signatures that remain distinguishable from natural biogenic baselines.

The workflow is explicitly modular:

0. **Agricultural flux modelling** with **LPJmL**, used to estimate gridded crop, water, carbon, and nitrogen-cycle fluxes that can be translated into surface boundary fluxes.
1. **Photochemical forward modelling** with **VULCAN**, used to integrate atmospheric chemistry under different surface-emission scenarios and stellar UV environments.
2. **Transmission spectroscopy and retrieval analysis** with **POSEIDON** and synthetic **JWST/PandExo** observing setups, used to translate those chemically self-consistent atmospheres into observable spectra and retrieval products.
3. **Thermal-emission/direct-observability analysis** with **POSEIDON** and future **LIFE/LIFEsimMC** simulations, organized as a Tierra--Sol 10 pc benchmark followed by a new Proxima-environment photochemical branch before its direct-observation analysis.

At present, Stage 0 is suspended by project decision. Stages I--II remain the
active evidence pipeline, while Stage III is documented and deliberately not
yet executed. To recover the exact operational state from a new chat, begin at
[`docs/project_resume.md`](docs/project_resume.md), then consult the
[`docs/project_status_tracker.md`](docs/project_status_tracker.md).

The completed photochemical comparison contains two stellar environments:

1. **Earth-Sun analogue (G2V)**, which provides the Solar-System benchmark.
2. **TRAPPIST-1e analogue (M8V)**, which probes the effect of a low-UV ultra-cool dwarf host on the lifetime and detectability of nitrogen-bearing technosignatures.

The next planned M-dwarf branch is distinct from the existing TRAPPIST-1e
experiment: `life_proxima_b_earthlike` will first recompute VULCAN A0--A3 under
the observed Proxima environment, using a controlled Earth-like PT/Kzz baseline.

All VULCAN scenarios inherit the official Earth baseline setup, so the atmospheric template, sulfur chemistry, and lower-boundary architecture remain fixed unless intentionally modified. In practice, the controlled experiment is defined by changing the stellar irradiation field and the imposed surface fluxes of $N_2O$ and $NH_3$.

### Current Scientific Status

The four saved Earth-Sun A0-A3 products reached VULCAN's saved steady-state
termination condition. The four current TRAPPIST-1e products stopped at the
configured maximum step count with `end_case = 3`, but the non-convergence is
dominated by low-abundance trace chemistry rather than by the target nitrogen
species alone. These profiles are therefore accepted as the current
TRAPPIST-1e products with a documented partial-convergence caveat, not as
failed experiments. See
[`docs/vulcan_profile_reproduction_2026-06-15.md`](docs/vulcan_profile_reproduction_2026-06-15.md).

The saved Earth--Sun A0--A3 profiles are accepted `end_case = 1` products from
2026-06-15. Their A2/A3 `N2O` values predate the current corrected boundary
conditions, so they are an interface benchmark for Stage III rather than the
final realization of the current matrix. The exact evidence and recovery rule
are in [`docs/earth_sun_n2o_matrix_provenance_2026-07-20.md`](docs/earth_sun_n2o_matrix_provenance_2026-07-20.md).

---

## Repository Layout

### `Photochemical_Modeling/`
Forward photochemical calculations, scenario configuration, diagnostic analysis, and figure generation.

### `Agricultural_Fluxes_LPJmL/`
LPJmL research notes, source bibliography, and scripts for converting gridded nitrogen-cycle outputs into ExoFarm lower-boundary fluxes.

### `Transmission_Spectroscopy/`
Profile export products, transmission-spectrum synthesis, synthetic JWST observations, and atmospheric retrieval workflows derived from the photochemical outputs.

### `Thermal_Emission_Spectroscopy/`
Planned Stage III for POSEIDON thermal-emission forward models, LIFE/LIFEsimMC
instrumental-noise simulations, SNR diagnostics, and a later retrieval campaign.

### `VULCAN/`
Local working copy of the VULCAN photochemical solver used as the chemistry engine for Stage I of the pipeline.

### `experiments/`
Compact human index of active, accepted, legacy, and cleanup-review campaigns.
Scientific products remain in their stage directories; reports live in `docs/`.

The top-level directory names were chosen to reflect the scientific role of each module rather than a generic "research" or notebook-oriented organization.

---

## Experiment and Cleanup Notes

Use [`experiments/README.md`](experiments/README.md) as the compact campaign
index and [`experiments/cleanup.md`](experiments/cleanup.md) for reviewed
cleanup candidates. Canonical product locations and legacy root directories are
documented in [`docs/repository_structure.md`](docs/repository_structure.md).

---

## End-to-End Workflow

### Stage 0: Agricultural Flux Estimates

`Agricultural_Fluxes_LPJmL/` is the upstream agricultural-production branch of the project. Its role is to use LPJmL to estimate spatially explicit crop, hydrology, carbon, and nitrogen-cycle fluxes under land-use and management scenarios, then convert selected nitrogen outputs into the molecules cm^-2 s^-1 fluxes used by the atmospheric models.

**Current status: suspended.** The existing checkout, documentation and
conversion workflow are retained, but no LPJmL execution or new coupling work
is scheduled until the project explicitly reactivates this stage.

Primary products:

- LPJmL configuration notes for land-use, fertilizer, manure, irrigation, and nitrogen-cycle settings
- tabulated `N2O` and `NH3`-relevant nitrogen flux estimates
- unit-conversion scripts from LPJmL nitrogen-mass outputs to atmospheric lower-boundary fluxes
- scenario mapping into A0/A1/A2/A3 ExoFarm forcing levels

### Stage I: Photochemical Forward Model

`Photochemical_Modeling/` contains the chemically self-consistent forward calculations. Scenario-specific boundary conditions and planetary YAML files are passed to VULCAN, which produces steady-state atmospheric outputs in `.vul` format. These outputs are then post-processed to extract surface abundances and comparative diagnostics.

Primary products:

- `.vul` files for all Earth-Sun and TRAPPIST-1e scenarios
- comparative abundance plots
- normalized abundance diagnostics
- stellar-spectrum comparison figures

### Stage II: Spectral Interpretation

`Transmission_Spectroscopy/` consumes the chemistry generated in Stage I. The exported pressure-temperature and composition profiles are used to build POSEIDON atmospheres, compute transmission spectra, generate synthetic JWST observations, and run retrieval experiments for selected scenarios.

Primary products:

- POSEIDON-ready PT and chemistry profiles
- forward transmission spectra
- synthetic JWST NIRSpec Prism and MIRI LRS datasets
- retrieval outputs, posterior summaries, and corner plots

### Stage III: Thermal Emission and LIFE

`Thermal_Emission_Spectroscopy/` is the planned direct-observability branch. It
will generate **thermal-emission** source spectra with POSEIDON, quantify
molecular signals, simulate LIFE instrumental noise with LIFEsimMC/PHRINGE,
build SNR tables/plots, and only then define a retrieval campaign. It is not a
reprocessing of JWST transmission products.

Its execution path has two layers: `life_earth_sun_10pc` first consumes the
frozen 2026-06-15 Tierra--Sol PT/química profiles only as an interface
benchmark; a corrected scientific A0--A3 interpretation requires the
provenance decision documented above. `life_proxima_b_earthlike` first creates
a new VULCAN branch from the Proxima SED and then repeats the same emission/LIFE
chain. The detailed structure and gates are in
[`docs/life_stage_iii_two_layer_workplan_2026-07-20.md`](docs/life_stage_iii_two_layer_workplan_2026-07-20.md), with the general
LIFE plan in [`docs/life_lifesim_stage_iii_plan.md`](docs/life_lifesim_stage_iii_plan.md).

---

## Scenario Definition

We consider four agricultural intensity levels for each stellar environment. Surface source fluxes are expressed in **molecules cm^-2 s^-1**. These are imposed photochemical lower-boundary fluxes, not simulated agricultural-production outputs.

The current matrix treats technological agriculture as a perturbation to the pre-agricultural nitrogen flux:

$$
F_i(A_j)=F_{i,A0}+\alpha_{i,j}\Delta F_{i,\mathrm{agri}}.
$$

| ID | Scenario | Scientific Interpretation | $\alpha_{NH_3}$ | $\alpha_{N_2O}$ | $N_2O$ Flux | $NH_3$ Flux |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A0** | Pre-Agricultural | Natural biogenic baseline | 0 | 0 | $1.58 \times 10^9$ | $2.94 \times 10^9$ |
| **A1** | Current Earth | Present-day benchmark with explicit agricultural contribution | 1 | 1 | $2.30 \times 10^9$ | $1.30 \times 10^{10}$ |
| **A2** | Moderate ExoFarm | 30B-inspired ExoFarm perturbation from Haqq-Misra et al. 2022 | 3.50 | 2.55 | $3.416 \times 10^9$ | $3.82 \times 10^{10}$ |
| **A3** | S2 Extreme ExoFarm | S2 Wild West agricultural-pollution envelope from Haqq-Misra et al. 2025 | 15 | 15 | $1.238 \times 10^{10}$ | $1.54 \times 10^{11}$ |

This table is the **current boundary-condition design**. It must not be
silently applied to the saved 2026-06-15 Earth--Sun A2/A3 profiles, which used
an earlier N2O realization; see
[`docs/earth_sun_n2o_matrix_provenance_2026-07-20.md`](docs/earth_sun_n2o_matrix_provenance_2026-07-20.md).

The earlier exploratory matrix used direct 10x and 100x multipliers of the modern total flux for A2 and A3. That version is preserved only as a legacy sensitivity because it conflated total modern flux with the agricultural perturbation.

All other lower-boundary species remain fixed relative to the Earth baseline so that changes in atmospheric composition can be attributed directly to the imposed nitrogen-cycle forcing and host-star environment.

---

## Usage

### Run the Photochemical Simulations

Earth-Sun cases:

```bash
cd Photochemical_Modeling/Scripts/Simulation
python run_parallel_earth.py
```

TRAPPIST-1e cases:

```bash
cd Photochemical_Modeling/Scripts/Simulation
python run_parallel_trappist.py
```

### Generate Chemistry Diagnostics and Figures

Surface-abundance tables:

```bash
cd Photochemical_Modeling/Scripts/Analysis
python extract_surface_values.py
```

All plots:

```bash
cd Photochemical_Modeling/Scripts/Plotting
python run_all_plots.py
```

### Run the Spectral Analysis

The transmission-spectroscopy stage is organized around notebooks and retrieval scripts in `Transmission_Spectroscopy/notebooks/`. In broad terms, the recommended order is:

1. Export the latest VULCAN `.vul` files into
   `Transmission_Spectroscopy/profiles/`; the canonical raw `.vul` files remain
   in `Photochemical_Modeling/Results/Outputs/`.
2. Generate TRAPPIST-1e forward spectra in the POSEIDON workflow.
3. Generate paired JWST-compatible datasets for 5, 10, and 20 observations with NIRSpec Prism and MIRI LRS.
4. Execute the retrieval scripts for the selected scenario, transit count, and instrument mode.

Refresh the hand-off from photochemistry to transmission spectroscopy:

```bash
python Transmission_Spectroscopy/scripts/export_vulcan_profiles.py
```

Generate the TRAPPIST-1e synthetic grid from WSL in the `POSEIDON` conda environment.
Verify the historical paths below in the live WSL environment before executing:

```bash
cd /mnt/c/Proyectos/Astro/ExoFarm_MDwarfs/Transmission_Spectroscopy/notebooks
source /home/dasan/anaconda3/etc/profile.d/conda.sh
conda activate POSEIDON
export POSEIDON_input_data=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/
export PYSYN_CDBS=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids/
python generate_trappist_synthetic_grid.py --scenarios A0 A1 A2 A3 --transits 5 10 20
```

Example retrieval runs:

```bash
cd /mnt/c/Proyectos/Astro/ExoFarm_MDwarfs/Transmission_Spectroscopy/notebooks
source /home/dasan/anaconda3/etc/profile.d/conda.sh
conda activate POSEIDON
export POSEIDON_input_data=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/
export PYSYN_CDBS=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids/
python run_trappist_retrieval.py --scenario A3 --n-transits 5 --instrument miri
python run_trappist_retrieval.py --scenario A3 --n-transits 5 --instrument nirspec
python run_trappist_retrieval.py --scenario A3 --n-transits 5 --instrument both
```

The active retrieval campaign is documented in
`Transmission_Spectroscopy/README.md`. The current optimized campaign contains
18 completed A0/A3 retrievals for equivalent total observing budgets of 10, 100
and 200 transits; the former 42-run matrix is legacy evidence. Use the retrieval
product inventory to distinguish complete, partial, and failed-resume product
sets; structural completion is not scientific validation.

### Future Stage III: LIFE/LIFEsimMC

No LIFE command is intentionally provided yet. First read the recovery guide
[`docs/project_resume.md`](docs/project_resume.md) and execute the documented
Capa 1 gates in [`Thermal_Emission_Spectroscopy/README.md`](Thermal_Emission_Spectroscopy/README.md):
freeze the POSEIDON-emission-to-LIFEsimMC interface, run one reproducible noise
pilot, validate molecular SNR diagnostics and approve the retrieval design.
Only then may the longer Capa 2 begin with the Proxima SED → VULCAN workflow;
its profiles must exist and be accepted before any LIFE command for that case.

---

## Software Requirements

### Core chemistry stage

- Python 3.x
- `numpy`
- `scipy`
- `pandas`
- `matplotlib`
- local VULCAN installation in `VULCAN/`

### Spectroscopy and retrieval stage

- POSEIDON
- PandExo
- `mpi4py`
- an environment configured for the notebook and retrieval scripts in `Transmission_Spectroscopy/notebooks/`

### Planned LIFE stage

- LIFEsimMC/PHRINGE in a versioned, validated environment
- a documented interface to a POSEIDON thermal-emission forward spectrum
- a frozen LIFE target/instrument configuration before generating products

For module-specific details, see the dedicated READMEs in `Photochemical_Modeling/`, `Transmission_Spectroscopy/` and `Thermal_Emission_Spectroscopy/`.




