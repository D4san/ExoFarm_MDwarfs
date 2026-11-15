# S/N molecular integrado por instrumento en TRAPPIST-1e, 2026-09-22

## Estado y propósito

Este diagnóstico sustituye al S/N basado en el pico individual como métrica
principal de la figura curada de transmisión. El resumen de picos se conserva
como evidencia legacy. La pregunta es cuánta información aporta cada
instrumento para una molécula objetivo cuando se utilizan todos sus bins
observados.

El producto es un diagnóstico de plantilla molecular, no una detección formal.
La interpretación queda condicionada a los perfiles TRAPPIST-1e aceptados con
la salvedad documentada de convergencia parcial.

## Definición de la señal

Para cada escenario `A1`, `A2` y `A3`, la señal molecular se mantiene como el
contrafactual ya validado:

```text
Delta d_m = d_full(scenario) - d_reset_molecule_to_A0(scenario)
```

La señal se rebinea sobre la malla observacional real de cada archivo plano de
ruido, usando sus centros y semianchos de bin. Para errores diagonales, el S/N
integrado por instrumento es:

```text
SNR_m,instrument = sqrt(sum_i (Delta d_m,i / sigma_i)^2)
```

El CSV incluye además el mismo cálculo restringido a las ventanas heredadas de
la figura molecular. Esas filas son una descomposición secundaria; el resultado
`instrument_total` no depende de sus bordes.

## Configuración reproducida

- Forward y contrafactuales: `Transmission_Spectroscopy/notebooks/plot_pure_transmission_spectra.py`.
- Cálculo y figura: `Transmission_Spectroscopy/notebooks/plot_molecular_snr_instrument.py`.
- NIRSpec: `TRAPPIST-1e_flat_NIRSpec_Prism_1_transits.dat`, 403 bins, aproximadamente `0.6025--5.2976` micras.
- MIRI: `TRAPPIST-1e_flat_MIRI_LRS_1_transits.dat`, 247 bins, aproximadamente `5.0213--11.9998` micras.
- Escalado temporal: `SNR_N = SNR_1 sqrt(N)` para `N = 1, 10, 100` tránsitos.
- Covarianza: diagonal, porque estos archivos contienen errores por bin y no una matriz de covarianza.

## Resultado resumido: A3

| Molécula | Instrumento | S/N, 1 tránsito | S/N, 100 tránsitos |
| :--- | :--- | ---: | ---: |
| N2O | NIRSpec PRISM | 0.293 | 2.934 |
| N2O | MIRI LRS | 0.093 | 0.928 |
| NH3 | NIRSpec PRISM | 0.005 | 0.052 |
| NH3 | MIRI LRS | 0.018 | 0.182 |

N2O queda dominado por NIRSpec en esta configuración. NH3 aporta más en MIRI,
como anticipan sus rasgos principales de 9--12 micras, aunque el S/N integrado
sigue siendo bajo a 100 tránsitos. NH3--NIRSpec se conserva en la figura y la
tabla porque es débil, pero no exactamente nulo; podrá retirarse de la capa
visual si la composición final necesita concentrarse en los canales relevantes.

## Productos

- Tabla fuente: [`trappist1e_molecular_snr_by_instrument.csv`](../Transmission_Spectroscopy/notebooks/POSEIDON_output/pure_spectra/plots/trappist1e_molecular_snr_by_instrument.csv)
- Tabla curada: [`trappist1e_molecular_snr_by_instrument.csv`](../Transmission_Spectroscopy/final_products/trappist1e_molecular_snr_by_instrument.csv)
- Figura PNG: [`trappist1e_molecular_snr_by_instrument.png`](../Transmission_Spectroscopy/final_products/figures/trappist1e_molecular_snr_by_instrument.png)
- Figura PDF: [`trappist1e_molecular_snr_by_instrument.pdf`](../Transmission_Spectroscopy/final_products/figures/trappist1e_molecular_snr_by_instrument.pdf)
- Generador: [`plot_molecular_snr_instrument.py`](../Transmission_Spectroscopy/notebooks/plot_molecular_snr_instrument.py)

El panel superior compara S/N integrado por molécula e instrumento para `A1`,
`A2` y `A3`, sin líneas de umbral. El panel inferior proyecta el S/N de las
cuatro combinaciones en `A3`, mantiene los umbrales `S/N = 3` y `S/N = 5`, y
marca los tránsitos requeridos en cada cruce bajo el escalado de ruido
diagonal. El antiguo gráfico de picos queda disponible como evidencia legacy y
no se promueve por el constructor final.

## Límites

La suma cuadrática supone errores independientes y no incluye sistemáticas,
covarianza instrumental ni la marginalización de parámetros nuisance del
retrieval. Por ello, el S/N integrado ordena la información esperada de cada
instrumento, pero no autoriza por sí mismo una afirmación de detección.
