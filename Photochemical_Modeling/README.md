# Photochemical Modeling

## Scientific Role

This module contains the forward photochemical stage of the ExoFarm workflow. Its purpose is to compute chemically self-consistent atmospheric states for Earth-like planets subject to different levels of nitrogen-cycle perturbation, and to quantify how those states depend on host-star irradiation.

The calculations are performed with the local `VULCAN/` solver and are organized as a controlled comparison between Solar and TRAPPIST-1-like stellar environments.

## Scientific Inputs

- scenario-specific lower boundary conditions for $N_2O$ and $NH_3$
- planetary configuration files for Earth-Sun and Earth-TRAPPIST-1e analogues
- stellar spectral input files
- the baseline Earth chemistry and atmospheric structure inherited from VULCAN

## Scientific Outputs

- steady-state VULCAN atmosphere files in `.vul` format
- comparative abundance diagnostics
- vertical profile figures
- stellar-spectrum comparison plots
- normalized abundance summaries relative to the present-day Earth benchmark

## Directory Structure

### `Config/`
Configuration assets required to launch each scenario.

- `Boundary_Conditions/`: lower boundary templates staged into the VULCAN runtime directory as `atm/BC_bot_Earth.txt`
- `planets/`: YAML case definitions for Earth-Sun and Earth-TRAPPIST-1e experiments
- `Stellar_Spectra/`: external stellar spectra used by selected scenarios

### `Scripts/`
Code used to execute simulations and reduce outputs.

- `Simulation/`: parallel launchers for the Solar and TRAPPIST-1e ensembles
- `Analysis/`: numerical summaries derived from `.vul` outputs
- `Plotting/`: scripts that generate publication-style comparison figures

### `Results/`
Products generated from the chemistry calculations.

- `Outputs/`: raw `.vul` files
- `Plots/`: rendered figures for inter-scenario comparisons

## Scenario Matrix

The active A0-A3 matrix uses imposed lower-boundary fluxes in molecules cm^-2 s^-1:

| ID | Scenario | alpha_NH3 | alpha_N2O | NH3 flux | N2O flux |
| --- | --- | ---: | ---: | ---: | ---: |
| A0 | PreAgri | 0 | 0 | 2.94e9 | 1.58e9 |
| A1 | CurrentEarth | 1 | 1 | 1.30e10 | 2.30e9 |
| A2 | ModerateExoFarm | 3.50 | 2.55 | 3.82e10 | 3.35e9 |
| A3 | S2ExtremeExoFarm | 15 | 15 | 1.54e11 | 1.20e10 |

The old A2/A3 10x/100x flux multipliers are legacy sensitivity cases only and should not be interpreted as the current scenario definition.

## Recommended Workflow

1. Run the chemistry ensemble from `Scripts/Simulation/`.
2. Verify that the `.vul` files are written to `Results/Outputs/`.
3. Extract comparative abundance tables from `Scripts/Analysis/`.
4. Generate the figure set from `Scripts/Plotting/`.

## Commands

Earth-Sun ensemble:

```bash
cd Scripts/Simulation
python run_parallel_earth.py
```

TRAPPIST-1e ensemble:

```bash
cd Scripts/Simulation
python run_parallel_trappist.py
```

Surface-abundance diagnostics:

```bash
cd Scripts/Analysis
python extract_surface_values.py
```

Full plotting suite:

```bash
cd Scripts/Plotting
python run_all_plots.py
```

## Interpretation

This module is the physical foundation of the project. Any spectral prediction or retrieval experiment in the downstream module should be interpreted as conditional on the atmospheric structures produced here.
