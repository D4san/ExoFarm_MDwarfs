# S/N molecular integrado en LIFE, 2026-09-22

## Propósito

Se añadió una figura LIFE análoga al diagnóstico integrado de transmisión.
Cada campaña tiene un único instrumento LIFE clásico, por lo que el panel
superior compara únicamente las plantillas completas de `N2O` y `NH3`. El
panel inferior muestra sus proyecciones A3 y marca las horas necesarias para
alcanzar `S/N = 3` y `S/N = 5`.

El gráfico anterior basado en picos por rasgo espectral se conserva como
evidencia legacy. La figura integrada es la presentación principal del S/N
molecular clásico.

## Definición

Para cada escenario y molécula se usa el residual contrafactual ya guardado en
la malla LIFE:

```text
Delta F_m,k = F_full,k - F_reset_molecule_to_A0,k
SNR_m = sqrt(sum_k (Delta F_m,k / sigma_k)^2)
```

La suma cubre todos los bins válidos del instrumento clásico. El escalado
temporal verificado es `SNR(t) = SNR(10 h) sqrt(t / 10 h)`. La incertidumbre es
diagonal y procede de `life_classic_binned_products.npz`.

## Resultados A3

| Campaña | Bins | S/N N2O a 10 h | S/N NH3 a 10 h | Horas N2O para S/N=3/5 | Horas NH3 para S/N=3/5 |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Proxima, `life_proxima_b_earthlike_v1` | 31 | 5.965 | 1.536 | 3 / 7 h | 38 / 106 h |
| Tierra--Sol, `life_earth_sun_10pc_interface_v1` | 77 | 0.201 | 0.005 | 2,226 / 6,183 h | 3,303,599 / 9,176,663 h |

La fila Tierra--Sol usa el benchmark etiquetado
`earth_20260615_pre_n2o_correction`; sirve como validación de interfaz y no
representa por sí sola la matriz N2O vigente. La fila Proxima es un análogo
terrestre bajo la SED y escena Proxima, no una atmósfera medida de Proxima b.

## Productos

- Generador: [`plot_emission_snr_integrated.py`](../Thermal_Emission_Spectroscopy/scripts/plot_emission_snr_integrated.py)
- Tabla Proxima: [`life_classic_snr_integrated_table.csv`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/life_classic_snr_integrated_table.csv)
- Figura Proxima canónica PNG: [`life_classic_snr_comparison_proxima.png`](../Thermal_Emission_Spectroscopy/final_products/figures/life_classic_snr_comparison_proxima.png)
- Figura Proxima canónica PDF: [`life_classic_snr_comparison_proxima.pdf`](../Thermal_Emission_Spectroscopy/final_products/figures/life_classic_snr_comparison_proxima.pdf)
- Figura Proxima PNG: [`life_classic_snr_integrated_proxima.png`](../Thermal_Emission_Spectroscopy/final_products/figures/life_classic_snr_integrated_proxima.png)
- Figura Proxima PDF: [`life_classic_snr_integrated_proxima.pdf`](../Thermal_Emission_Spectroscopy/final_products/figures/life_classic_snr_integrated_proxima.pdf)
- Figura Tierra--Sol PNG: [`life_classic_snr_integrated_earth_sun.png`](../Thermal_Emission_Spectroscopy/outputs/life_earth_sun_10pc_interface_v1/plots/life_classic_snr_integrated_earth_sun.png)

## Límites

Este S/N suma una plantilla molecular conocida con errores independientes. No
incluye covarianza instrumental, inestabilidad temporal, parámetros nuisance,
múltiples realizaciones de ruido ni comparación formal de modelos. Mantiene
por tanto el estatus de diagnóstico de la rama LIFEsim clásica; la frontera
instrumental sigue siendo LIFEsimMC/PHRINGE.
