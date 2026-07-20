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
- `planets/`: YAML case definitions for Earth-Sun and Earth-TRAPPIST-1e experiments; the future `earth_proxima_b/` branch will remain separate.
- `Stellar_Spectra/`: external stellar spectra used by selected scenarios, including the future archived MUSCLES Proxima source and conversion metadata.

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
| A2 | ModerateExoFarm | 3.50 | 2.55 | 3.82e10 | 3.416e9 |
| A3 | S2ExtremeExoFarm | 15 | 15 | 1.54e11 | 1.238e10 |

This is the **active boundary-condition matrix** staged by the current Earth
runner. It is not retroactive: the accepted Earth--Sun A2/A3 `.vul` profiles
saved on 2026-06-15 used the earlier N2O values `3.35e9` and `1.20e10`. They
remain useful as a frozen interface benchmark, but a rerun or an explicit
historical label is required before treating a downstream LIFE result as the
current matrix. See
[`../docs/earth_sun_n2o_matrix_provenance_2026-07-20.md`](../docs/earth_sun_n2o_matrix_provenance_2026-07-20.md).

The old A2/A3 10x/100x flux multipliers are legacy sensitivity cases only and should not be interpreted as the current scenario definition.

## Recommended Workflow

1. Run the chemistry ensemble from `Scripts/Simulation/`.
2. Verify that the `.vul` files are written to `Results/Outputs/`.
3. Extract comparative abundance tables from `Scripts/Analysis/`.
4. Generate the figure set from `Scripts/Plotting/`.

## Current Product Status

The active TRAPPIST-1e YAML files were corrected on 2026-06-15 to use the
planet's radius, gravity, orbital distance, and updated stellar radius while
retaining the terrestrial pressure-temperature and Kzz profiles as the
controlled atmospheric structure. The active lower-boundary files were also
corrected to remove a duplicate `H2SO4` row that silently overwrote its
documented surface flux. After review on 2026-06-15, the corrected re-run
products were promoted into `Results/Outputs/` as the canonical profiles. The
former profiles were deleted; the machine-readable comparison and scientific
decision are retained in `../docs/vulcan_profile_reproduction_2026-06-15.md`.

As audited on 2026-06-15:

- all four Earth-Sun products saved with VULCAN `end_case = 1`, indicating
  successful integration to steady-state. Their saved A2/A3 BC provenance is
  pre-N2O-correction; do not silently equate them with the active table above;
- all four TRAPPIST-1e products saved with `end_case = 3` after exceeding the
  configured maximum step count before satisfying VULCAN's global convergence
  criterion.

The current TRAPPIST-1e products are accepted with a partial-convergence caveat:
the remaining global convergence signal is dominated by low-abundance trace
chemistry, especially `C2H5` near 0.019 bar, not by a demonstrated instability
of the target nitrogen perturbation alone. Downstream spectra and retrievals
may use these products, but papers and reports must state this caveat and avoid
claiming that the full chemical network reached VULCAN's strict steady-state
criterion.

The Earth-Sun and TRAPPIST-1e simulation runners now inspect the saved VULCAN
termination code before moving a `.vul` product into `Results/Outputs/`.
Earth-Sun products still require `end_case = 1`. TRAPPIST-1e products may be
promoted when the run exits cleanly and the partial-convergence caveat is
documented in the reproduction report.

### Planned controlled Proxima branch

`life_proxima_b_earthlike` is planned as a new VULCAN branch, not as a reuse of
the accepted TRAPPIST-1e files. Its first configuration will preserve the
Earth-like `atm_Earth_Jan_Kzz.txt` PT/Kzz structure and A0--A3 boundary
conditions while substituting the validated Proxima MUSCLES stellar environment
and the documented orbital/illumination parameters. This isolates the stellar
SED effect; it does not claim to model the unknown atmosphere or climate of
Proxima b.

Before creating YAMLs or running VULCAN, archive the raw SED and its metadata,
convert it reproducibly to the VULCAN stellar-surface convention (nm and
`erg cm^-2 s^-1 nm^-1`), verify that the star--planet geometry is applied once,
and document the required MIR extension for the downstream LIFE scene. The
future `Proxima_b_A0--A3.vul` products must meet the normal Earth-style
acceptance gate (`end_case = 1`) before export to the thermal-emission branch.

The full two-layer dependency is in
[`../docs/life_stage_iii_two_layer_workplan_2026-07-20.md`](../docs/life_stage_iii_two_layer_workplan_2026-07-20.md).
To resume safely from a new chat, start with
[`../docs/project_resume.md`](../docs/project_resume.md).

### Numerical sensitivity experiments

`VULCAN/run_case.py` accepts a limited, validated `numerics` block in a planet
YAML file. This makes convergence sensitivity experiments explicit and
reproducible. For example:

```yaml
numerics:
  count_max: 50000
  mtol_conv: 1.0e-15
```

Supported keys are `conv_step`, `count_max`, `atol`, `mtol_conv`, `yconv_cri`,
`slope_cri`, `yconv_min`, `flux_cri`, and `rtol`. Any override defines a new
experiment and must be recorded separately. Increasing `count_max` or relaxing
a threshold does not by itself improve the scientific interpretation; it must
be compared against the accepted partial-convergence baseline.

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
