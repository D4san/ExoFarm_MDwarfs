# Photochemical Modelling with photochem

## Purpose

This module is an alternative chemistry workflow for the ExoFarm project built around `photochem` instead of VULCAN. The goal is to keep the scientific comparison used in the repo while reorganizing the inputs around the way `photochem` expects them: reaction mechanism, settings/boundary conditions, stellar spectrum, and initial atmosphere.

## Design

This folder keeps the experiment definition in `Config/catalog.json` and translates it into prepared files under `Results/Prepared/`.

Key pieces:

- `Config/catalog.json`
  Central catalog for planets, stars, scenarios, tracked species, and named runs.
- `Config/Templates/settings_base.yaml`
  Base terrestrial `photochem` settings for the photochemical step.
- `Config/Templates/species_climate_hnoc.yaml`
  Climate species file used by the TRAPPIST-1e climate-preparation path.
- `Config/Templates/settings_climate_base.yaml`
  Base climate settings for `AdiabatClimate`.
- `Scripts/Simulation/prepare_photochem_inputs.py`
  Prepares the mechanism, stellar spectra, per-case settings files, and initial atmosphere files.
- `Scripts/Simulation/run_case.py`
  Runs one named case with `photochem.EvoAtmosphere`.

## How Stellar Flux Is Handled

The stellar flux file used by `photochem` must be the flux at the planet, not at the stellar surface.

Current setup:

- `earth_sun`
  Uses `photochem.utils.stars.solar_spectrum` scaled to present-day Earth insolation.
- `earth_trappist`
  Uses the local repo spectrum `VULCAN/atm/stellar_flux/TRAPPIST1_surface.txt`, which is stored at the stellar surface, and rescales it geometrically to TRAPPIST-1e before writing the `photochem` flux file.

## TRAPPIST-1e Climate Step

TRAPPIST-1e runs now have a climate-preparation stage before photochemistry.

That means:

- the stellar spectrum is first prepared at the planet
- `AdiabatClimate` builds a radiative-convective initial atmosphere for TRAPPIST-1e
- that atmosphere is then passed to `EvoAtmosphere` as the initial state for photochemistry

This is a one-way coupling:

- `clima -> photochem`

It is not yet the same as turning on `evolve-climate` inside `EvoAtmosphere`.

## Outputs

Prepared inputs are written under:

- `Results/Prepared/mechanism/`
- `Results/Prepared/stellar_flux/`
- `Results/Prepared/settings/`
- `Results/Prepared/climate/`
- `Results/Prepared/initial_atmospheres/`

Model outputs are written under:

- `Results/Outputs/`
- `Results/Summaries/`
- `Results/Logs/`

## Commands

Prepare all inputs:

```bash
cd photochemical_modelling_photochem/Scripts/Simulation
python prepare_photochem_inputs.py
```

Run the Solar suite:

```bash
cd photochemical_modelling_photochem/Scripts/Simulation
python run_parallel_earth.py
```

Run the TRAPPIST-like suite:

```bash
cd photochemical_modelling_photochem/Scripts/Simulation
python run_parallel_trappist.py
```

Extract surface abundances:

```bash
cd photochemical_modelling_photochem/Scripts/Analysis
python extract_surface_values.py
```

Export POSEIDON-style profiles:

```bash
cd photochemical_modelling_photochem/Scripts/Analysis
python export_transmission_profiles.py
```

## Notes

- These scripts assume `photochem` is installed and importable in the target environment.
- The Solar helper in `photochem.utils.stars` may need network access the first time it is used.
- The TRAPPIST-1e path now uses explicit planet parameters instead of reusing Earth mass and radius.

## Project Guide

For a detailed, project-specific note in Spanish, see:

- `GUIA_PHOTOCHEM_PROYECTO.md`
