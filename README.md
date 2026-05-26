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

The current study compares two stellar environments:

1. **Earth-Sun analogue (G2V)**, which provides the Solar-System benchmark.
2. **TRAPPIST-1e analogue (M8V)**, which probes the effect of a low-UV ultra-cool dwarf host on the lifetime and detectability of nitrogen-bearing technosignatures.

All VULCAN scenarios inherit the official Earth baseline setup, so the atmospheric template, sulfur chemistry, and lower-boundary architecture remain fixed unless intentionally modified. In practice, the controlled experiment is defined by changing the stellar irradiation field and the imposed surface fluxes of $N_2O$ and $NH_3$.

---

## Repository Layout

### `Photochemical_Modeling/`
Forward photochemical calculations, scenario configuration, diagnostic analysis, and figure generation.

### `Agricultural_Fluxes_LPJmL/`
LPJmL research notes, source bibliography, and scripts for converting gridded nitrogen-cycle outputs into ExoFarm lower-boundary fluxes.

### `Transmission_Spectroscopy/`
Profile export products, transmission-spectrum synthesis, synthetic JWST observations, and atmospheric retrieval workflows derived from the photochemical outputs.

### `VULCAN/`
Local working copy of the VULCAN photochemical solver used as the chemistry engine for Stage I of the pipeline.

The top-level directory names were chosen to reflect the scientific role of each module rather than a generic "research" or notebook-oriented organization.

---

## End-to-End Workflow

### Stage 0: Agricultural Flux Estimates

`Agricultural_Fluxes_LPJmL/` is the upstream agricultural-production branch of the project. Its role is to use LPJmL to estimate spatially explicit crop, hydrology, carbon, and nitrogen-cycle fluxes under land-use and management scenarios, then convert selected nitrogen outputs into the molecules cm^-2 s^-1 fluxes used by the atmospheric models.

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

---

## Scenario Definition

We consider four agricultural intensity levels for each stellar environment. Surface source fluxes are expressed in **molecules cm^-2 s^-1**.

| ID | Scenario | Scientific Interpretation | $N_2O$ Flux | $NH_3$ Flux |
| :--- | :--- | :--- | :--- | :--- |
| **A0** | Pre-Agricultural | Natural biogenic baseline | $9.0 \times 10^8$ | $3.0 \times 10^8$ |
| **A1** | Current Earth | Present-day biological plus anthropogenic benchmark | $2.3 \times 10^9$ | $1.5 \times 10^9$ |
| **A2** | Moderate ExoFarm | Intensified nitrogen-cycle perturbation | $2.3 \times 10^{10}$ | $1.5 \times 10^{10}$ |
| **A3** | Extreme ExoFarm | Upper-limit agricultural forcing experiment | $2.3 \times 10^{11}$ | $1.5 \times 10^{11}$ |

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

1. Build or validate the PT and chemistry profile files in `Transmission_Spectroscopy/profiles/`.
2. Generate forward spectra in the POSEIDON notebook workflow.
3. Generate paired JWST-compatible datasets for 5, 10, and 20 observations with NIRSpec Prism and MIRI LRS.
4. Execute the retrieval scripts for the selected scenario and transit count.

Example retrieval run:

```bash
cd Transmission_Spectroscopy/notebooks
python run_trappist_retrieval.py --scenario A3 --n-transits 20
```

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

For module-specific details, see the dedicated READMEs in `Photochemical_Modeling/` and `Transmission_Spectroscopy/`.




