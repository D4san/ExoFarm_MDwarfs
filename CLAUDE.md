# CLAUDE.md

Native Claude Code entry point for this repository. The canonical, tool-agnostic
guidance already lives in [AGENTS.md](AGENTS.md); it is imported below and must
be treated as the source of truth for scientific discipline, coding standards,
retrieval/plot conventions, and cleanup workflow.

@AGENTS.md

---

## Native environment notes (Claude Code)

These notes adapt the Codex-oriented setup in `AGENTS.md` to the actual machine
this Claude Code session runs on. They record verified facts, not aspirations.

### Conda environments actually present here (updated 2026-07-21)

This host is `/home/castello/...` (Linux/WSL2), **not** the historical
`/home/wsldasan` or `/home/dasan` hosts referenced throughout `AGENTS.md` and
the docs. `conda` lives at `/home/castello/miniconda3`. Environments:

- `base` (bare) and `Main_DFT` (py3.11: numpy/scipy/matplotlib/pandas/numba/h5py)
  — general lightweight post-processing.
- **`ExoFarm_LIFE`** (py3.11) — **dedicated Stage III env, created 2026-07-21.**
  Contains the full LIFE toolchain, all importing and running:
  - `POSEIDON` 1.4.0 (editable, cloned at `/home/castello/POSEIDON`),
    `numpy 1.26.4` (POSEIDON pins numpy<2), numba 0.66, pysynphot, mpi4py,
    pymultinest.
  - `lifesim` 0.2.32 (classic astrophysical/photon noise + yields).
  - `lifesimmc` 1.3.5 + `phringe` 1.8.2 (instrumental-instability MC + covariance).
  - Dep notes: pinned `psutil 6.1.1` and `packaging 23.2` for phringe/lifesimmc;
    the leftover ipython/wheel warnings are dev-tooling only. **`lifesim`'s
    `Instrument.get_spectrum` needs fdannert's modified SpectRes** (`spectres
    2.1.1`, adds the `edge_mode` kwarg) — installed 2026-07-22, replacing the
    stock `spectres 2.2.2`. Re-verified: POSEIDON `bin_spectrum`/compute and
    lifesimmc still import/run. Do not reinstall stock spectres or lifesim breaks.
  - LIFEsim custom-spectrum input to `get_spectrum` = astropy Quantities
    `[wl(m), photon flux density (ph m^-3 s^-1)]`; convert POSEIDON direct_emission
    `Fp_obs [W m^-2 m^-1]` via `F_ph = Fp_obs * wl/(h c)`. `spectrum_type=
    'direct_emission'` (observed Fp at d) is the LIFE quantity, not Fp/Fs.

Activate Stage III work with the helper (sets `POSEIDON_input_data` +
`PYSYN_CDBS`):

```bash
source /home/castello/POSEIDON/activate_exofarm_life.sh   # conda activate ExoFarm_LIFE + env vars
```

**Opacity/stellar data (72 GB):** POSEIDON imports without it, but computing
emission spectra needs the input tree. `inputs.zip` (67 GiB, Zenodo record
19595136, MD5 8a3da02d76f9d2fcc510e9baa7dfebf7) downloads to
`/home/castello/POSEIDON/inputs.zip` → unzip to `/home/castello/POSEIDON/inputs/`.
Until then, `read_opacities()` and `create_star(stellar_grid=...)` will fail.

### Skills configured for this project

Project skills live under `.claude/skills/`. Consult the relevant one before
starting matching work:

- `use-lpjml-exofarm` — LPJmL nitrogen-flux workflows and conversion to
  atmospheric lower-boundary fluxes (molecules cm^-2 s^-1). Native adaptation of
  the original Codex skill in `.codex/skills/use-lpjml-exofarm/`.
- `use-poseidon-life-emission` — POSEIDON **emission** spectra + **LIFEsim
  classic and LIFEsimMC/PHRINGE** mid-infrared noise/covariance/SNR for the LIFE
  interferometer track. See the skill for the transmission→emission distinction,
  the Fp/Fs→radiance interface contract, and the per-tool units (classic wants
  photon radiance, MC wants energy radiance).

### Current work track: Stage III — LIFE thermal emission (planned, no products)

The published pipeline (Stage II) does **transmission** spectroscopy with
POSEIDON + PandExo for JWST (transit depth, `(Rp/Rs)^2`). Stage III
(`Thermal_Emission_Spectroscopy/`) is a **planned, not yet executed** parallel
**thermal-emission** track for the LIFE nulling interferometer, where POSEIDON
runs `spectrum_type="emission"` (Fp/Fs) and the noise route is **LIFEsimMC +
PHRINGE** (NOT LIFEsim classic — classic does astrophysical/yield noise only,
not time-dependent instrumental instability). LIFE reads emission spectra, not
transit depths — keep the two tracks separate in code, filenames, and figures.

Authoritative planning docs (read before any Stage III action):
`docs/project_resume.md` (entry point) → `docs/project_status_tracker.md` →
`docs/life_stage_iii_two_layer_workplan_2026-07-20.md` →
`docs/earth_sun_n2o_matrix_provenance_2026-07-20.md` →
`docs/life_target_selection_2026-07-20.md`.

Two ordered layers, gated:
- **Layer 1 `life_earth_sun_10pc`** — interface benchmark using the accepted
  Earth–Sun A0–A3 VULCAN profiles at 10 pc. The A2/A3 profiles are the frozen
  `earth_20260615_pre_n2o_correction` set (N2O `3.35e9`/`1.20e10`, predating the
  active corrected BC `3.416e9`/`1.238e10`); use them to validate the interface,
  never as the current matrix without a documented rerun/historical decision.
- **Layer 2 `life_proxima_b_earthlike`** — blocked until a MUSCLES Proxima SED is
  converted to VULCAN surface flux and a new Proxima A0–A3 photochemistry branch
  is run and accepted.

Hard rules: SNR is a diagnostic, not a detection; do not launch LIFE retrievals
until forward + molecular counterfactuals + noise + SNR are validated and a
campaign manifest is recorded; preserve LIFEsimMC covariance (whitening), do not
collapse to diagonal errors; Stage III products live only under
`Thermal_Emission_Spectroscopy/outputs/<campaign-id>/`.
