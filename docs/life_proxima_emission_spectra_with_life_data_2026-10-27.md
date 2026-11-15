# LIFE Proxima A3 noise curves on molecular signals (2026-10-27)

## Scope

This figure compares the existing Proxima b Earth-like A0–A3 emission spectra and molecular counterfactual signals with the synthetic LIFE A3 uncertainties for 1, 10, and 100 h. The three datasets are represented as symmetric ±1σ curves in the lower N₂O and NH₃ signal panels. The upper emission-spectrum panel contains only the model spectra.

The work reuses saved model and LIFE products. It does not run a forward model, an instrument simulation, or a retrieval.

## Inputs and configuration

- **Forward spectra:** [A0–A3 products](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/forward_emission/).
- **Molecular counterfactuals:** [N₂O and NH₃ products](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/molecular_diagnostics/).
- **LIFE datasets:** each file contains 31 channels and one synthetic realization. The three datasets share wavelength centres and half-bin widths.
  - 1 h: [LIFE_proxima_A3_1h_O2_fixedBlack1bar_official.dat](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A3_1h_O2_fixedBlack1bar_official.dat), SHA-256 a3043e5de76a834983949e6eca12636ea4de174ebdb2db0853155282c100dee2.
  - 10 h: [LIFE_proxima_A3_10h.dat](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A3_10h.dat), SHA-256 46a026504b9b9521fa29407a501169b9d3cfc433de40a91b8ade86d7767abb5b.
  - 100 h: [LIFE_proxima_A3_100h.dat](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A3_100h.dat), SHA-256 78662546181a5b74391a14b7b73ae80d879200a74db6a4bc5338e3ce7eee4705.
- **Observable and units:** direct planetary flux Fp at the system distance, in W m⁻² µm⁻¹. Input fluxes and uncertainties are in W m⁻² m⁻¹ and are multiplied by 10⁻⁶.
- **Model signals:** the molecular signal is F_reset_to_A0 − F_full; dark curves show F_A0 − F_Aj. Model curves are rebinned to R=200 for presentation; LIFE noise remains at its native 31 channel centres.
- **Noise display:** each dataset contributes +σ_Fp as a solid curve and −σ_Fp as a dashed curve, both centred on zero in the two lower panels. Curves use the plotted molecular-signal scale. The vertical ranges are set from the model signals before noise curves are added and autoscaling is then disabled. A curve at a panel edge indicates that the uncertainty exceeds the fixed signal range.
- **Palette:** 1 h uses rusty spice, 10 h deep space blue, and 100 h deep moss, all from the shared project palette. Curve alpha is 0.56.

## Direct result

The fixed signal-panel limits are −0.1713 to 1.9637 × 10⁻¹⁹ W m⁻² µm⁻¹ for N₂O and −0.1674 to 1.8812 × 10⁻¹⁹ W m⁻² µm⁻¹ for NH₃. The fraction of channel uncertainties that exceeds the plotted range is:

| Signal panel | Integration | +1σ above upper limit | −1σ below lower limit |
| --- | ---: | ---: | ---: |
| N₂O | 1 h | 32.3% | 87.1% |
| N₂O | 10 h | 6.5% | 51.6% |
| N₂O | 100 h | 0.0% | 35.5% |
| NH₃ | 1 h | 35.5% | 96.8% |
| NH₃ | 10 h | 9.7% | 51.6% |
| NH₃ | 100 h | 0.0% | 35.5% |

These are channel fractions from the saved diagonal uncertainties, not detection statistics.

## Interpretation and limits

- **Source fact:** the LIFE files contain synthetic per-channel uncertainties; they are not astronomical observations.
- **Figure result:** the noise amplitude decreases with longer integration, while portions of the 1 h and 10 h curves reach the fixed panel boundaries.
- **Project interpretation:** the plot compares uncertainty scale with modeled molecular signals. It does not establish a detection.
- **Limit:** the displayed uncertainties are diagonal and do not represent cross-channel covariance. Each file is one saved realization. The plotted curves do not apply a new instrumental operator and do not replace a forward-to-instrument-to-retrieval comparison.

The transmission-depth JWST figure is documented separately in [trappist1e_jwst_noise_curves_signal_panels_2026-10-27.md](trappist1e_jwst_noise_curves_signal_panels_2026-10-27.md); its observable and units are distinct from LIFE emission flux.

## Reproduction and outputs

Source script: [plot_emission_molecular_residuals.py](../Thermal_Emission_Spectroscopy/scripts/plot_emission_molecular_residuals.py). Run from the repository root:

    .venv\Scripts\python.exe Thermal_Emission_Spectroscopy\scripts\plot_emission_molecular_residuals.py --campaign proxima --observations Thermal_Emission_Spectroscopy\outputs\life_proxima_b_earthlike_v1\life_data\LIFE_proxima_A3_1h_O2_fixedBlack1bar_official.dat Thermal_Emission_Spectroscopy\outputs\life_proxima_b_earthlike_v1\life_data\LIFE_proxima_A3_10h.dat Thermal_Emission_Spectroscopy\outputs\life_proxima_b_earthlike_v1\life_data\LIFE_proxima_A3_100h.dat --output-suffix LIFE_A3_1_10_100h

Outputs: [PNG](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/emission_molecular_residuals_proxima_LIFE_A3_1_10_100h.png), [PDF](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/emission_molecular_residuals_proxima_LIFE_A3_1_10_100h.pdf), and [provenance sidecar](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/emission_molecular_residuals_proxima_LIFE_A3_1_10_100h.provenance.json), including input hashes, fixed axis limits, and clipping fractions. The separate 100 h-only figure remains available.

The 100 h dataset audit and prior results are in [life_proxima_a3_100h_corrected_binning_molecular_ablation_2026-10-19.md](life_proxima_a3_100h_corrected_binning_molecular_ablation_2026-10-19.md).
