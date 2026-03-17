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
