# AGENTS.md

Guidance for Codex and other coding agents working in this repository.

This project is a scientific modelling workflow, not a generic software demo.
Treat every code change, notebook edit, plot, and written explanation as part of
a reproducible scientific argument about agricultural technosignatures in
Earth-like exoplanet atmospheres.

## Project Role

ExoFarm studies whether large-scale agriculture can perturb atmospheric nitrogen
chemistry enough to produce remotely detectable signatures. The current
controlled experiment changes the imposed lower-boundary fluxes of `N2O` and
`NH3` while keeping the rest of the atmospheric setup fixed unless explicitly
stated.

The pipeline has three scientific stages:

1. `Agricultural_Fluxes_LPJmL/`
   - Upstream agricultural flux modelling.
   - LPJmL estimates land-use, crop, water, carbon, and nitrogen-cycle outputs.
   - LPJmL outputs are not atmospheric abundances. Convert nitrogen-mass fluxes
     into molecules cm^-2 s^-1 before using them as atmospheric forcing.

2. `Photochemical_Modeling/`
   - Forward photochemical modelling with the local `VULCAN/` solver.
   - Produces chemically self-consistent `.vul` atmospheres for Earth-Sun and
     TRAPPIST-1e-like cases.
   - Scenario differences should be attributable to stellar environment and
     imposed `N2O` / `NH3` lower-boundary fluxes.

3. `Transmission_Spectroscopy/`
   - Spectral interpretation with POSEIDON, PandExo-style synthetic JWST data,
     and retrieval analysis.
   - Consumes POSEIDON-ready pressure-temperature and chemistry profiles.
   - Produces forward transmission spectra, synthetic JWST observations,
     retrieved spectra, posterior summaries, and publication figures.

## Scientific Context

The active scenario matrix is A0-A3:

- `A0`: pre-agricultural natural baseline.
- `A1`: current Earth benchmark.
- `A2`: moderate ExoFarm forcing, anchored to the 30B-inspired ExoFarm
  perturbation from Haqq-Misra et al. 2022.
- `A3`: extreme ExoFarm forcing, using the 15x agricultural-pollution envelope
  associated with the S2 Wild West technosphere frame from Haqq-Misra et al.
  2025.

Use the current project equation when explaining the flux design:

```text
F_i(A_j) = F_i(A0) + alpha_i,j * Delta F_i,agri
```

Do not silently revive the old exploratory 10x/100x total-flux matrix. It is a
legacy sensitivity, not the current source of truth.

Keep these distinctions clear:

- Source-derived fact: directly stated by a paper, README, data file, log, or
  retrieval output.
- Project inference: a modelling decision or interpretation made by this repo.
- Speculation: plausible scientific explanation that still needs checking.

When writing scientific claims, label these categories instead of blending them.

## Reference Discipline

Before making scientific or methodological claims, inspect the real local source
where possible:

- top-level `README.md`
- `Photochemical_Modeling/README.md`
- `Transmission_Spectroscopy/README.md`
- `Agricultural_Fluxes_LPJmL/README.md`
- `Agricultural_Fluxes_LPJmL/docs/lpjml_sources.bib`
- `.codex/skills/use-lpjml-exofarm/references/lpjml-model-and-papers.md`
- relevant notebooks, scripts, retrieval outputs, or `.vul` products

LPJmL reference anchors:

- Schaphoff et al. 2018 Part 1: LPJmL model description.
- Schaphoff et al. 2018 Part 2: LPJmL model evaluation.
- von Bloh et al. 2018: LPJmL nitrogen-cycle implementation.
- Lutz et al. 2019/2020: tillage, management, and N2O interpretation cautions.
- Wirth et al. 2024: biological nitrogen fixation in LPJmL.

ExoFarm scenario anchors:

- Haqq-Misra et al. 2022: ExoFarm abundance/technosignature basis.
- Haqq-Misra et al. 2025: technosphere/worldbuilding frame and 15x upper-bound
  agricultural-pollution anchor.

If a paper is central to the answer and the exact wording matters, re-check the
paper or the project note before finalizing. Do not rely on memory for new
scientific claims.

## Scientific Reports and Analysis Notes

Use the top-level `docs/` directory as the persistent home for scientific
reports, methodological analyses, interpretation notes, and research-log
entries produced from this repository.

- Write reports in Markdown and add them to `docs/README.md`.
- Use descriptive, stable filenames rather than generic names such as
  `analysis.md`.
- Link every report to the scripts, notebooks, input products, and generated
  figures on which it depends.
- Record the date of the analysis and enough configuration detail to reproduce
  it.
- Distinguish source-derived facts, direct results, project interpretations,
  and unresolved questions.
- Include equations, units, campaign identifiers, assumptions, and limitations
  close to the claims that depend on them.
- Prefer academic but narrative language: write as a comprehensible research
  log that explains why an analysis was performed, how decisions were made,
  what the result means, and what remains uncertain.
- Treat these reports as intermediate evidence for a future scientific paper,
  not as polished manuscript claims. Avoid stronger detection language than the
  analysis supports.
- Include references with DOI, arXiv, or stable project/source links whenever
  they justify a scientific or methodological choice.

## Repository Review and Cleanup Workflow

When the user asks to review, organize, clean, depurar, or tidy the repository,
use `docs/repository_cleanup_workflow.md` as the operating procedure.

Trigger phrases include "revisemos el repo", "organicemos el repo",
"depuremos el repo", "hay codigo basura?", "borremos experimentos fallidos",
and "limpiemos outputs temporales".

The expected sequence is:

1. Inspect read-only first: structure, `git status`, tracked/untracked files,
   sizes, temporary folders, caches, legacy paths, and suspicious code markers.
2. Classify findings as canonical evidence, audit evidence, legacy evidence,
   temporary execution residue, or ambiguous product.
3. Report exact proposed deletion targets and wait for explicit approval unless
   the user already approved those exact targets in the same turn.
4. Delete narrowly, verify the target is gone, and report what was left
   unchanged.
5. Record durable decisions in `docs/`, `experiments/cleanup.md`, or
   `AGENTS.md` as appropriate.

Never delete scientific products merely because they are old, failed,
step-limited, or superseded. Preserve enough inputs, commands, logs, reports,
or manifests for a colleague to understand the decision.

## Coding Standards

Write code as if another scientist will audit it six months from now.

- Follow PEP 8 for Python code.
- Prefer clear function names, explicit inputs, and small units of work.
- Add comments where they explain a modelling choice, unit conversion, file
  convention, numerical assumption, or non-obvious scientific constraint.
- Avoid comments that merely repeat the code.
- Keep unit conversions explicit, especially:
  - nitrogen mass versus whole-molecule mass;
  - molecules cm^-2 s^-1;
  - transit depth `(R_p/R_s)^2`;
  - ppm conversions;
  - pressure units;
  - wavelength units.
- Do not hide path conventions in magic strings if the same convention is used
  more than once.
- Preserve existing file naming conventions for VULCAN, POSEIDON, synthetic
  data, and retrieval products.

## Testing and Verification

Every non-trivial code change should include verification. Scale the test depth
to the risk of the change.

For scripts:

- Run the script or a minimal smoke test.
- Check generated files exist and have plausible sizes.
- Validate expected columns, units, and row counts.
- For plot scripts, generate the figure and visually inspect it when possible.
- For retrieval/posterior code, report which products were loaded and which were
  missing.

For scientific calculations:

- Test unit conversions with simple hand-checkable values.
- Test species-specific nitrogen atom counts (`N2O` has 2 N atoms, `NH3` has 1).
- Check that the same scenario/instrument/transit naming is used by samples,
  results, spectra, and synthetic `.dat` files.
- Do not classify a TRAPPIST-1e VULCAN product as failed solely because it
  saved with `end_case = 3`. The 2026-06-15 accepted products are
  trace-limited partial-convergence profiles: the remaining global convergence
  signal is dominated by low-abundance `C2H5` near 0.019 bar. State this caveat
  explicitly, and only call the product failed if the target species, spectral
  products, or documented acceptance criteria are actually invalid.
- Do not interpret a retrieved posterior as a detection unless the model
  assumptions, degeneracies, and profile mismatch have been considered.

For notebooks:

- Run the changed cells, or explain clearly why they were not run.
- Avoid huge opaque cells. Split long logic into small cells or helper functions.
- Keep outputs intentional. Remove stale or misleading outputs when editing raw
  notebook JSON.

## Jupyter Notebook Style

Notebooks are scientific evidence objects. They should be readable by a human
before being runnable by a machine.

Use this structure:

1. Short Markdown section explaining the scientific question.
2. Compact configuration cell.
3. Small data-loading cell.
4. Small transformation/analysis cells.
5. Plotting cell.
6. Markdown interpretation cell that distinguishes:
   - what the plot shows;
   - what can be concluded;
   - what remains uncertain.

Notebook cells should be atomized:

- Avoid long all-in-one cells.
- Move reusable logic into `.py` helpers when it grows beyond notebook-scale.
- Use Markdown to explain decisions, assumptions, and caveats.
- Keep plots and tables tied to their provenance: file paths, scenario keys,
  transit counts, instrument modes, and units.

## POSEIDON and Ubuntu Workflow

POSEIDON work generally does not run in the repo `.venv`. It should be run in
the Ubuntu/Anaconda environment named `POSEIDON`.

For spectroscopy/retrieval organization tasks, first consult
`docs/transmission_spectroscopy_inventory_2026-06-16.md`. It records the current
read-only inventory of active TRAPPIST-1e retrieval products, synthetic data,
plot scripts, figure locations, and legacy/ambiguous outputs. Do not delete or
move spectroscopy plots, notebooks, retrieval products, or POSEIDON outputs
without explicit user approval for exact paths.

Preferred commands inside Ubuntu:

```bash
cd /mnt/c/Proyectos/Astro/ExoFarm_MDwarfs/Transmission_Spectroscopy/notebooks
source /home/wsldasan/miniconda3/etc/profile.d/conda.sh
conda activate POSEIDON
export POSEIDON_input_data=/home/wsldasan/POSEIDON/inputs/
export PYSYN_CDBS=/home/wsldasan/POSEIDON/inputs/stellar_grids/
```

Then run examples such as:

```bash
python generate_trappist_synthetic_grid.py --scenarios A0 A1 A2 A3 --transits 5 10 20 100
python run_trappist_retrieval.py --scenario A3 --n-transits 20 --instrument both
```

Important Windows/WSL note:

- Sometimes `wsl` reports that no distribution exists.
- Do not immediately conclude that Ubuntu is absent.
- Check for the Ubuntu application or use a distribution-specific command such
  as `wsl -d Ubuntu` if available.
- From Codex on Windows, `ubuntu.exe run bash -lc "<command>"` is often the
  working path when `wsl -d Ubuntu` fails. Running it may require approval
  outside the sandbox.
- Once inside Ubuntu, activate the Anaconda environment named `POSEIDON`.
- POSEIDON scripts that create stars or read opacities also need
  `POSEIDON_input_data` and `PYSYN_CDBS`; use the paths above unless the data
  directory has moved.

Local Windows `.venv` is acceptable for lightweight post-processing that only
needs packages such as `numpy`, `matplotlib`, and `pandas`. It is not a
substitute for the POSEIDON environment when scripts import `POSEIDON`.

## Retrieval and Plotting Conventions

Current TRAPPIST-1e synthetic data live under:

```text
Transmission_Spectroscopy/notebooks/POSEIDON_output/TRAPPIST-1e/synthetic_data/base_1transit/
```

Current retrieval products live under:

```text
Transmission_Spectroscopy/notebooks/POSEIDON_output/TRAPPIST-1e/retrievals/
```

Use the current instrument suffixes:

- `MIRI`
- `NIRSpec`
- `NIRSpec_MIRI`

Supported transit counts are currently:

- `5`
- `10`
- `20`
- `100`

When plotting retrieved spectra or posteriors:

- Report which scenario/instrument/transit combinations were found.
- Report missing products explicitly.
- Treat old no-suffix 10/100 products as legacy unless the task explicitly asks
  for legacy comparisons.
- Be careful with `NH3`: retrieved constant-abundance `NH3` can be biased by
  vertical-profile mismatch and degeneracy with other parameters. Do not present
  high-SNR narrow `NH3` posteriors as clean detections without checking the true
  vertical profile and retrieval assumptions.

## Plot Style and Palette

Use the existing project plot style before inventing new colours.

The shared spectroscopy palette is defined in:

```text
Transmission_Spectroscopy/notebooks/exofarm_plot_style.py
```

Current named colours:

```text
scenario_pink   = #E34F95
scenario_violet = #BD62E3
scenario_cyan   = #56E3DB
scenario_green  = #95E36B
terracotta_mauve = #8E5651
charcoal_violet  = #5B4763
slate_green      = #57635E
deep_moss        = #3F633E
deep_space_blue = #002642
midnight_violet = #42133A
dark_amaranth   = #840032
rusty_spice     = #B54B19
golden_orange   = #E59500
sunlit_clay     = #E5B86D
dust_grey       = #E5DADA
dim_grey        = #746F75
ink_black       = #02040F
```

Import it in plot scripts as:

```python
from exofarm_plot_style import EXOFARM_GENERAL_PALETTE as PALETTE
```

Existing instrument encodings:

- `MIRI`: `PALETTE["golden_orange"]`
- `NIRSpec`: `PALETTE["deep_space_blue"]`
- `NIRSpec_MIRI`: `PALETTE["dark_amaranth"]`

Existing retrieved-transit encodings:

- `5`: `PALETTE["dark_amaranth"]`
- `10`: `PALETTE["deep_space_blue"]`
- `20`: `PALETTE["rusty_spice"]`
- `100`: `PALETTE["dim_grey"]`

Preferred A0-A3 scenario encodings for new publication-facing plots:

- `A0`: `PALETTE["scenario_green"]` / `#95E36B`
- `A1`: `PALETTE["scenario_cyan"]` / `#56E3DB`
- `A2`: `PALETTE["scenario_violet"]` / `#BD62E3`
- `A3`: `PALETTE["scenario_pink"]` / `#E34F95`

Use these four vibrant colours for the first visual layer, especially scenario
families in overplotted profiles. When a second visual layer is needed, such as
star type, instrument family, or an aggregate trend over scenario colours, use
the darker secondary colours:

- `terracotta_mauve`: `#8E5651`
- `charcoal_violet`: `#5B4763`
- `slate_green`: `#57635E`
- `deep_moss`: `#3F633E`

Existing molecular contribution encodings:

- `Total`: `0.15`
- `N2O`: `#1f77b4`
- `NH3`: `#ff7f0e`
- `CH4`: `#9467bd`
- `O3`: `#17becf`

When creating a new plot, keep visual meaning stable:

- colour should not switch meanings between related figures;
- instrument colours should remain instrument colours;
- scenario colours should remain scenario colours;
- transit-count colours should remain transit-count colours;
- for publication-facing Matplotlib figures, prefer a serif STIX style:
  `font.family="serif"`, `font.serif=["STIX Two Text", "STIXGeneral",
  "Times New Roman"]`, and `mathtext.fontset="stix"`;
- if a new visual category is necessary, add it to a shared helper rather than
  scattering literal hex codes across scripts.

## LPJmL Workflow Notes

Use LPJmL as the default upstream agricultural model for this repo. Do not
re-introduce DNDC as the active Stage 0 model unless explicitly asked.

For LPJmL on Windows:

- Prefer Ubuntu WSL/Linux commands.
- Keep upstream LPJmL source under `Agricultural_Fluxes_LPJmL/software/LPJmL/`
  or document the external path.
- Keep ExoFarm scripts, workflows, and derived outputs separate from upstream
  LPJmL source code.
- Large official LPJmL input datasets may live outside the repo, commonly on a
  portable `D:` path; document the path and do not duplicate large data into git.

Known useful Ubuntu build dependencies:

```bash
sudo apt-get install build-essential libjson-c-dev libnetcdf-dev libudunits2-dev
```

Before trusting an LPJmL output, record:

- LPJmL version or commit;
- configuration file;
- output variable name;
- output unit;
- whether values are grid-cell totals or per-area fluxes;
- conversion path into atmospheric lower-boundary fluxes.

## Project Management and Status Tracking

A central status log is maintained in [docs/project_status_tracker.md](file:///c:/Proyetos/Repos/ExoFarm_MDwarfs/docs/project_status_tracker.md). All coding agents must use and maintain this file as follows:

- **Consult status before coding:** Read [docs/project_status_tracker.md](file:///c:/Proyetos/Repos/ExoFarm_MDwarfs/docs/project_status_tracker.md) to understand the technical status of Stage 0, I, and II, active dependencies, and design decisions.
- **Maintain the backlog:** When the user requests new technical tasks, open questions, or modifications, check if they are in the backlog section. Mark completed tasks, and add new ones as appropriate.
- **Record design decisions:** Add rows to the design decisions table in [docs/project_status_tracker.md](file:///c:/Proyetos/Repos/ExoFarm_MDwarfs/docs/project_status_tracker.md) when an architectural decision, parameter correction, or control profile constraint is established.
- **Document tools and versions:** Ensure the versions of VULCAN, POSEIDON, and LPJmL and the host star spectrum configurations remain documented and up-to-date.

## Communication Style for This Repo

Be concise but scientifically explicit.

- Prefer "I checked X; it implies Y" over generic reassurance.
- Explain assumptions before conclusions.
- When something is uncertain, say what would resolve it.
- When editing artifacts, edit the real file and summarize what changed.
- Do not bury caveats; put them near the result they affect.
- When a result depends on stale or partial data, say so.

The goal is not just to make code run. The goal is to help the project produce
auditable, human-readable scientific evidence.
