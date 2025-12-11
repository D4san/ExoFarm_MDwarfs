# ExoFarm: Agricultural Technosignatures in Exoplanetary Atmospheres

[![VULCAN](https://img.shields.io/badge/Model-VULCAN-blue)](https://github.com/exoclime/VULCAN)
[![Python](https://img.shields.io/badge/Python-3.x-yellow)]()

---

## 🌍 Abstract / Scientific Rationale

This project investigates the atmospheric detectability of intensive, industrial-scale agriculture ("ExoFarms") on Earth-like exoplanets. By utilizing the **VULCAN** 1D photochemical kinetics model, we simulate the atmospheric accumulation of Nitrogen-based technosignatures—specifically Nitrous Oxide ($N_2O$) and Ammonia ($NH_3$)—resulting from the disruption of the planetary nitrogen cycle by Haber-Bosch-like processes.

The study compares two distinct stellar environments:
1.  **Earth-Sun System (G2V)**: A benchmark case representing current Earth conditions.
2.  **Earth-TRAPPIST-1e System (M8V)**: A potentially habitable planet orbiting an ultra-cool dwarf star.

Our goal is to quantify how the different UV flux environments affect the photochemical lifetime of these agricultural gases, determining whether "ExoFarms" could provide a detectable technosignature distinct from natural biological baselines.

---

## 📂 Repository Structure & Folders

This project uses a dedicated research directory `ExoFarm_Research/` to organize configuration, scripts, and results, keeping the core `VULCAN` code separate.

*   **`ExoFarm_Research/Config/`**: Contains all input configurations.
    *   `planets/`: YAML configuration files for each simulation scenario.
        *   `earth_sun/`: Scenarios A0-A3 for the Earth-Sun system.
        *   `earth_trappist/`: Scenarios A0-A3 for the TRAPPIST-1e system.
    *   `Boundary_Conditions/`: Defines the surface flux boundary conditions (the "agricultural emissions").
        *   `bc_earth_preagri_full.txt`: Natural biological fluxes (Pre-agricultural).
        *   `bc_earth_current_full.txt`: Current Earth fluxes (including anthropogenic sources).
        *   `bc_earth_exofarm_moderate_full.txt`: 10x amplification of $N_2O$ and $NH_3$ fluxes.
        *   `bc_earth_exofarm_full.txt`: 100x amplification (Extreme ExoFarm).
*   **`ExoFarm_Research/Scripts/`**: Custom Python scripts for automation and analysis.
    *   `Simulation/`: Scripts to run parallel VULCAN simulations (`run_parallel_earth.py`, `run_parallel_trappist.py`).
    *   `Analysis/`: Scripts to analyze data and generate figures (`plot_results.py`, `extract_surface_values.py`).
*   **`ExoFarm_Research/Results/`**: Stores simulation outputs.
    *   `Outputs/`: Final `.vul` (binary pickle) output files.
    *   `Figures/`: Generated scientific plots.
*   **`VULCAN/`**: The core photochemical model source code.

---

## 🧪 Simulation Scenarios

We simulate four distinct agricultural intensity levels for both star systems. The surface boundary conditions for key species are defined as follows:

### Agricultural Flux Table (Surface Emissions)
All fluxes are in units of **molecules cm⁻² s⁻¹**.

| ID | Scenario Name | Description | $N_2O$ Flux | $NH_3$ Flux | Scaling Factor (approx.) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A0** | **Pre-Agricultural** | Natural biological baseline. | $9.0 \times 10^8$ | $3.0 \times 10^8$ | Baseline (Biological) |
| **A1** | **Current Earth** | Present-day anthropogenic + biological. | $2.3 \times 10^9$ | $1.5 \times 10^9$ | 1x (Current Benchmark) |
| **A2** | **Moderate ExoFarm** | Intensified agriculture. | $2.3 \times 10^{10}$ | $1.5 \times 10^{10}$ | ~15x $N_2O$ / 10x $NH_3$ |
| **A3** | **Extreme ExoFarm** | Maximum theoretical intensity. | $2.3 \times 10^{11}$ | $1.5 \times 10^{11}$ | ~150x $N_2O$ / 100x $NH_3$ |

*Note: Other species (CO, CH4, etc.) are kept at constant fluxes across all scenarios to isolate the effect of nitrogen-cycle disruption.*

---

## 📊 Data Visualization & Analysis Guide

This project generates a comprehensive suite of plots to analyze the impact of agricultural emissions on exoplanetary atmospheres. The analysis pipeline produces the following key figures in `ExoFarm_Research/Results/Figures/`:

### 1. Surface Normalized Bars (`Comparison_Surface_Normalized.png`)
*   **What it shows**: A bar chart comparing the surface abundance (mixing ratio) of key species ($N_2O, NH_3, O_3, CH_4$) across all scenarios (A0-A3).
*   **Key Feature**: Values are **normalized** to the Present-Day Earth (A1) baseline. A value of "10x" means the planet has 10 times more of that gas than Earth today.
*   **Scientific Insight**: Directly quantifies the "detectability signal." We look for large bars in the TRAPPIST-1e system compared to Earth, indicating that M-dwarf stars facilitate the accumulation of these gases.

### 2. Vertical Abundance Profiles (`*_profiles.png`)
*   **What it shows**: The mixing ratio of gases as a function of altitude (pressure).
*   **Scientific Insight**: Reveals the vertical structure of the atmosphere.
    *   **Tropopause Trap**: Shows if gases are confined to the lower atmosphere or transported high up.
    *   **Photolysis Cutoff**: A sharp drop at high altitudes indicates where UV radiation destroys the molecule.

### 3. Star Comparison (`Comparison_Star_A2_ExoFarm_Mod.png`)
*   **What it shows**: Direct side-by-side comparison of Earth vs. TRAPPIST-1e atmospheric profiles for the *same* agricultural scenario (e.g., A2 Moderate ExoFarm).
*   **Scientific Insight**: Isolates the stellar effect. Since the surface flux is identical, any difference in the atmospheric profile is solely due to the different stellar environment (UV flux, temperature) and background atmosphere.

### 4. Stellar Spectra Comparison (`Comparison_Spectra.png`)
*   **What it shows**: The input stellar flux (Irradiance) for the Sun (G-type) vs. TRAPPIST-1 (M-type).
*   **Scientific Insight**: Explains *why* the chemistry differs. M-dwarfs like TRAPPIST-1 have much lower near-UV (NUV) flux, which is the primary destroyers of $N_2O$ and $NH_3$. This plot visualizes the "UV deficit" that allows these gases to accumulate.

### 5. Temperature-Pressure Profiles (`*_TP.png`)
*   **What it shows**: The thermal structure of the atmosphere.
*   **Scientific Insight**: Ensures the physical plausibility of the simulation and shows the habitable zone context (surface temperature).

---

## 🚀 Reproducibility Guide

### 1. Prerequisites
*   Python 3.x
*   VULCAN dependencies (`numpy`, `scipy`, `matplotlib`, `pickle`, etc.)
*   The `VULCAN` source code must be present in the root directory.

### 2. Running Simulations (Parallelized)
We use orchestration scripts to execute all 4 scenarios simultaneously for a given star. These scripts automatically handle temporary directory creation, file copying, and cleanup.

**Step 1: Run Earth-Sun Scenarios**
```bash
cd ExoFarm_Research/Scripts/Simulation
python run_parallel_earth.py
```
*   This will launch 4 parallel processes (A0-A3).
*   Progress is logged to the console.
*   Outputs are saved to `ExoFarm_Research/Results/Outputs/`.

**Step 2: Run Earth-TRAPPIST-1e Scenarios**
```bash
python run_parallel_trappist.py
```
*   Similar to the Earth run, but uses the TRAPPIST-1e stellar spectrum and physical parameters.

### 3. Data Visualization & Analysis
Once simulations are complete and `.vul` files are in `Results/Outputs/`, run the analysis scripts:

**Step 3: Extract Data Tables**
```bash
cd ../Analysis
python extract_surface_values.py
```
*   Prints formatted tables of surface mixing ratios to the console (Markdown format).

**Step 4: Generate All Plots**
```bash
python plot_results.py
```
*   Automatically generates all figures described in the "Data Visualization" section above.
*   Saves plots to `ExoFarm_Research/Results/Figures/`.

---

## 📚 References

*   **VULCAN Model**: Tsai, S.-M., et al. (2017). *VULCAN: An Open-source, Validated Chemical Kinetics Code for Exoplanetary Atmospheres*. [[DOI: 10.3847/1538-4365/aa51dd](https://doi.org/10.3847/1538-4365/aa51dd)]
*   **Nitrogen Cycle & ExoFarms**: Haqq-Misra, et al. (2022). *Disruption of a Planetary Nitrogen Cycle as Evidence of Extraterrestrial Agriculture*. The Astrophysical Journal Letters, 929, L28. [[DOI: 10.3847/2041-8213/ac65ff](https://doi.org/10.3847/2041-8213/ac65ff)]
*   **Biosignatures Review**: Schwieterman, E. W., et al. (2018). *Exoplanet Biosignatures: A Review of Remotely Detectable Signs of Life*. [[DOI: 10.1089/ast.2017.1729](https://doi.org/10.1089/ast.2017.1729)]
*   **TRAPPIST-1 Spectrum**: Wilson, D. J., et al. (2021). *The Mega-MUSCLES Spectral Energy Distribution Library*. [[Data Repository](https://github.com/parkus/Mega-MUSCLES)]
