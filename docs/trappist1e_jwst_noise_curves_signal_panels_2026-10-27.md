# JWST noise curves on TRAPPIST-1e molecular signals (2026-10-27)

## Scope

This figure overlays synthetic JWST noise curves on the two lower panels of the canonical TRAPPIST-1e transmission figure: the N₂O and NH₃ molecular signals. The upper A0–A3 spectrum panel is preserved unchanged. Existing A3 products for NIRSpec PRISM and MIRI LRS are used at 10, 20, and 100 transits. The 5-transit series is omitted. No POSEIDON run or new synthetic observation was generated.

## Data and display

The source tables are the A3 products in the [synthetic-data directory](../Transmission_Spectroscopy/notebooks/POSEIDON_output/TRAPPIST-1e/synthetic_data/base_1transit/):

- **NIRSpec PRISM:** [10 transits](../Transmission_Spectroscopy/notebooks/POSEIDON_output/TRAPPIST-1e/synthetic_data/base_1transit/TRAPPIST-1e_SYNTHETIC_JWST_NIRSpec_PRISM_Trappist_A3_Extreme_N_trans_10.dat), [20 transits](../Transmission_Spectroscopy/notebooks/POSEIDON_output/TRAPPIST-1e/synthetic_data/base_1transit/TRAPPIST-1e_SYNTHETIC_JWST_NIRSpec_PRISM_Trappist_A3_Extreme_N_trans_20.dat), and [100 transits](../Transmission_Spectroscopy/notebooks/POSEIDON_output/TRAPPIST-1e/synthetic_data/base_1transit/TRAPPIST-1e_SYNTHETIC_JWST_NIRSpec_PRISM_Trappist_A3_Extreme_N_trans_100.dat).
- **MIRI LRS:** [10 transits](../Transmission_Spectroscopy/notebooks/POSEIDON_output/TRAPPIST-1e/synthetic_data/base_1transit/TRAPPIST-1e_SYNTHETIC_JWST_MIRI_LRS_Trappist_A3_Extreme_N_trans_10.dat), [20 transits](../Transmission_Spectroscopy/notebooks/POSEIDON_output/TRAPPIST-1e/synthetic_data/base_1transit/TRAPPIST-1e_SYNTHETIC_JWST_MIRI_LRS_Trappist_A3_Extreme_N_trans_20.dat), and [100 transits](../Transmission_Spectroscopy/notebooks/POSEIDON_output/TRAPPIST-1e/synthetic_data/base_1transit/TRAPPIST-1e_SYNTHETIC_JWST_MIRI_LRS_Trappist_A3_Extreme_N_trans_100.dat).

The .dat uncertainty column is dimensionless transit-depth sigma. It is multiplied by 10⁶ for display in ppm. Each instrument and transit count has symmetric +1σ and −1σ curves. Colour encodes transit count; NIRSpec is solid and MIRI is dashed. Curves are drawn at the native channel centres, without horizontal error bars. The shared palette assigns deep space blue to 10 transits, rusty spice to 20, and dim grey to 100. Line alpha is 0.56.

| Mode | Wavelength range and channels | Median σ (10 / 20 / 100 transits), ppm |
| --- | --- | ---: |
| NIRSpec PRISM | 0.602–5.298 µm; 217 | 28.31 / 20.02 / 8.95 |
| MIRI LRS | 5.021–12.000 µm; 87 | 91.38 / 64.61 / 28.90 |

## Fixed limits and interpretation

The original vertical limits remain fixed at approximately −4.1 to 20.4 ppm for N₂O and −4.1 to 20.5 ppm for NH₃. They were calibrated from the labelled ticks and panel frame in the original PNG; autoscaling is disabled. Curve segments at a panel edge exceed the displayed range and do not indicate a noise value equal to that boundary.

All −1σ branches fall below the lower limit. The fraction of +1σ channels above the upper limit is:

| Instrument | Transits | N₂O | NH₃ |
| --- | ---: | ---: | ---: |
| NIRSpec PRISM | 10 | 80.2% | 79.7% |
| NIRSpec PRISM | 20 | 46.1% | 45.6% |
| NIRSpec PRISM | 100 | 14.3% | 14.3% |
| MIRI LRS | 10 | 100.0% | 100.0% |
| MIRI LRS | 20 | 100.0% | 100.0% |
| MIRI LRS | 100 | 79.3% | 79.3% |

- **Source fact:** the .dat files contain synthetic per-channel uncertainties; they are not JWST observations.
- **Figure result:** the curves show which uncertainties fit within the original signal-panel range without changing the signal scale.
- **Project interpretation:** this is a visual comparison between σ and the modeled signals. It is not a detection, does not show a random noise realization, and does not include cross-channel covariance.
- **Reading limit:** the exact values of clipped branches cannot be read from the figure. Original values and clipping fractions remain in the sidecar.

A pixel comparison confirms that the upper spectrum panel matches the canonical image exactly. The two lower signal panels retain their original limits with the noise curves overlaid.

## Reproduction and outputs

Source script: [plot_trappist_synthetic_spectra_with_transit_counts.py](../Transmission_Spectroscopy/notebooks/plot_trappist_synthetic_spectra_with_transit_counts.py). Run from the repository root:

    .venv\Scripts\python.exe Transmission_Spectroscopy\notebooks\plot_trappist_synthetic_spectra_with_transit_counts.py

The script reads the six 10/20/100-transit tables linked above and generates [PNG](../Transmission_Spectroscopy/notebooks/POSEIDON_output/pure_spectra/plots/trappist1e_jwst_transit_count_observations_A3.png), [PDF](../Transmission_Spectroscopy/notebooks/POSEIDON_output/pure_spectra/plots/trappist1e_jwst_transit_count_observations_A3.pdf), and a [provenance sidecar](../Transmission_Spectroscopy/notebooks/POSEIDON_output/pure_spectra/plots/trappist1e_jwst_transit_count_observations_A3.provenance.json).

The reused canonical image is [trappist1e_pure_a0_molecular_residuals_v2.png](../Transmission_Spectroscopy/notebooks/POSEIDON_output/pure_spectra/plots/trappist1e_pure_a0_molecular_residuals_v2.png). The sidecar records the six input hashes, panel calibration, clipping fractions, and interpretation limits.
