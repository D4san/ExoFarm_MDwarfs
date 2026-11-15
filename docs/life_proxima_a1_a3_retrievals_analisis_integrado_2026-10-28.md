# LIFE Proxima A1/A3: análisis integrado de retrievals

**Fecha:** 2026-10-28 (America/Bogota). **Estado:** análisis reproducido desde productos corregidos; 42 modelos auditados: seis completos y 36 ablaciones. La comparación A3–1000 h con A0 fija se presenta aparte y conserva su aceptación pendiente.

## Alcance y método

A1 representa el benchmark de Tierra actual y A3 el escenario extremo ExoFarm simulado. Cada caso usa una realización sintética LIFE de 31 canales. Los modelos completos incluyen H₂O, CO₂, CH₄, O₂, O₃, N₂O y NH₃; cada ablación retira una de las seis especies estudiadas y su parámetro. O₂ permanece activo y no tiene ablación en esta matriz.

Los seis casos se reconstruyeron desde sus manifiestos, configuraciones, muestras y estadísticas nativas MultiNest. Se verificaron estados, retornos, hashes del inventario congelado, callback, columnas, muestras de peso igual, espectros, P–T, `log_X`, datos y priors. Cada pareja comparte escenario, exposición, dataset, operador y priors restantes. No se ejecutó ningún retrieval nuevo.

La referencia escalar de abundancia es el promedio del perfil vertical ponderado en presión; no constituye una equivalencia radiativa demostrada para una atmósfera isoquímica. Los intervalos son cuantiles de muestras de igual peso. Se calculan también probabilidades con las muestras ponderadas nativas.

**Límites:** un dataset/realización por caso; selección de la realización A1–1 h después de comparar dos; química isochem, P–T parametrizado y likelihood diagonal. Los valores absolutos de `ln Z` entre datasets distintos no son factores de Bayes entre A1 y A3. El umbral A1 se eligió retrospectivamente. Los valores 0%/100% indican una cola sin muestras, no probabilidades exactas.

## Lectura de los resultados

**N₂O y NH₃ tienen comportamientos distintos.** En A3, la diferencia de evidencia al retirar N₂O es -0.03, +9.14 y +84.66 para 1, 10 y 100 h; al retirar NH₃ es -0.53, -0.23 y +2.75. Son contrastes dentro de cada dataset; las incertidumbres figuran en la tabla de ablaciones. El apoyo a N₂O crece en estas realizaciones, mientras que el contraste de NH₃ solo es positivo en A3–100 h. La conclusión está condicionada al modelo y sus priors.

**Abundancias conjuntas.** En A3, la fracción de muestras donde N₂O y NH₃ superan ambas sus referencias A1 es 6.4%, 73.1% y 98.7% para 1, 10 y 100 h; las estimaciones ponderadas son 6.5%, 72.8% y 98.7%. Su masa previa es 39.4%, de modo que las odds se actualizan por factores 0.11, 4.18 y 113.9 frente al complemento. Estos valores describen regiones de abundancia definidas después de ver los resultados, no probabilidades de que exista agricultura.

A3–10 h ilustra por qué hay que comparar con el prior: P(NH₃≥A1) es 73.1%, mientras que su probabilidad previa es 75.5%; el factor de actualización de odds es 0.88. La probabilidad conjunta alta está impulsada principalmente por N₂O. Las colas poco pobladas y el error del muestreo requieren cautela.

**Calidad de ajuste.** Para A3–100 h, χ² es 57.19: el χ² reducido reportado es 3.57 y, con 14 parámetros libres, el cociente efectivo es 3.36. Dos canales de la mediana puntual superan |3σ|. El desajuste justifica estudiar perfiles, ruido y modelo antes de endurecer la interpretación de las evidencias.

## Referencias efectivas de abundancia

| Gas | log₁₀ A0 | log₁₀ A1 | log₁₀ A3 |
|---|---:|---:|---:|
| N2O | -6.8843 | -6.7338 | -6.0141 |
| NH3 | -9.9505 | -9.3049 | -8.2315 |
| H2O | -2.5359 | -2.5359 | -2.5367 |
| CO2 | -3.3957 | -3.3958 | -3.3957 |
| CH4 | -4.8062 | -4.8221 | -4.8367 |
| O3 | -8.2595 | -8.2501 | -8.2950 |
| O2 | -0.6958 | -0.6958 | -0.6958 |

## Modelos completos y ajuste

| Escenario | h | ln Z ± error numérico | χ² mejor ajuste | χ² reducido reportado | Muestras iguales |
|---|---:|---:|---:|---:|---:|
| A1 | 1 | 868.823 ± 0.171 | 15.23 | 0.95 | 7695 |
| A1 | 10 | 889.986 ± 0.211 | 22.35 | 1.40 | 6601 |
| A1 | 100 | 910.921 ± 0.244 | 27.74 | 1.73 | 6461 |
| A3 | 1 | 866.283 ± 0.167 | 26.12 | 1.63 | 6026 |
| A3 | 10 | 891.387 ± 0.209 | 19.48 | 1.22 | 7036 |
| A3 | 100 | 894.331 ± 0.247 | 57.19 | 3.57 | 7268 |

El χ² reducido reportado usa los grados de libertad impresos por POSEIDON; el CSV conserva también el cociente con 14 parámetros libres. Son diagnósticos de ajuste, no pruebas independientes de detección.

## Posteriores completos: gases

Cuantiles en log₁₀ de fracción de mezcla. P(≥A0/A1) es la fracción de muestras del modelo completo por encima de cada referencia escalar.

| Escenario | h | Gas | q2,5 | q16 | Mediana | q84 | q97,5 | P(≥A0) | P(≥A1) |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| A1 | 1 | H2O | -3.776 | -3.471 | -3.154 | -2.766 | -1.709 | 10.47% | 10.47% |
| A1 | 1 | CO2 | -3.259 | -3.161 | -3.016 | -2.749 | -1.708 | 100 en muestra | 100 en muestra |
| A1 | 1 | CH4 | -4.504 | -4.277 | -4.054 | -3.733 | -2.877 | 99.92% | 99.96% |
| A1 | 1 | O2 | -5.792 | -4.921 | -3.143 | -1.331 | -0.492 | 5.63% | 5.63% |
| A1 | 1 | O3 | -11.788 | -10.927 | -9.075 | -7.811 | -7.343 | 30.85% | 30.58% |
| A1 | 1 | N2O | -11.805 | -10.924 | -9.179 | -7.370 | -6.294 | 8.68% | 6.71% |
| A1 | 1 | NH3 | -11.867 | -11.189 | -9.748 | -8.252 | -7.336 | 55.30% | 39.84% |
| A1 | 10 | H2O | -3.102 | -3.035 | -2.962 | -2.855 | -2.374 | 6.53% | 6.53% |
| A1 | 10 | CO2 | -3.427 | -3.396 | -3.360 | -3.304 | -2.814 | 83.67% | 83.68% |
| A1 | 10 | CH4 | -4.580 | -4.496 | -4.404 | -4.292 | -3.962 | 99.98% | 99.98% |
| A1 | 10 | O2 | -5.809 | -4.954 | -3.114 | -1.322 | -0.490 | 5.95% | 5.95% |
| A1 | 10 | O3 | -11.508 | -9.609 | -8.294 | -8.020 | -7.853 | 46.58% | 45.71% |
| A1 | 10 | N2O | -11.845 | -11.036 | -9.267 | -7.561 | -6.780 | 3.62% | 2.11% |
| A1 | 10 | NH3 | -11.883 | -11.356 | -10.158 | -8.897 | -8.152 | 44.48% | 26.28% |
| A1 | 100 | H2O | -2.987 | -2.959 | -2.930 | -2.903 | -2.876 | 0 en muestra | 0 en muestra |
| A1 | 100 | CO2 | -3.448 | -3.431 | -3.411 | -3.393 | -3.378 | 19.93% | 19.95% |
| A1 | 100 | CH4 | -4.781 | -4.741 | -4.699 | -4.660 | -4.623 | 99.50% | 99.85% |
| A1 | 100 | O2 | -5.854 | -5.108 | -3.300 | -1.520 | -0.692 | 2.57% | 2.57% |
| A1 | 100 | O3 | -8.137 | -8.081 | -8.029 | -7.981 | -7.937 | 100 en muestra | 99.98% |
| A1 | 100 | N2O | -7.078 | -6.928 | -6.802 | -6.698 | -6.608 | 74.32% | 26.68% |
| A1 | 100 | NH3 | -11.934 | -11.546 | -10.622 | -9.670 | -9.035 | 24.83% | 6.78% |
| A3 | 1 | H2O | -2.963 | -2.753 | -2.524 | -2.289 | -2.052 | 51.91% | 51.91% |
| A3 | 1 | CO2 | -3.168 | -3.045 | -2.892 | -2.729 | -2.566 | 100 en muestra | 100 en muestra |
| A3 | 1 | CH4 | -4.685 | -4.393 | -4.123 | -3.869 | -3.628 | 98.59% | 98.72% |
| A3 | 1 | O2 | -5.808 | -4.987 | -3.180 | -1.395 | -0.518 | 4.68% | 4.68% |
| A3 | 1 | O3 | -11.858 | -11.212 | -9.874 | -8.551 | -7.806 | 10.29% | 10.09% |
| A3 | 1 | N2O | -11.775 | -10.827 | -8.784 | -6.655 | -5.625 | 18.98% | 17.14% |
| A3 | 1 | NH3 | -11.860 | -11.186 | -9.787 | -8.325 | -7.420 | 53.97% | 37.19% |
| A3 | 10 | H2O | -2.944 | -2.869 | -2.787 | -2.704 | -2.622 | 0.23% | 0.23% |
| A3 | 10 | CO2 | -3.404 | -3.370 | -3.330 | -3.287 | -3.239 | 95.42% | 95.42% |
| A3 | 10 | CH4 | -4.888 | -4.737 | -4.607 | -4.489 | -4.377 | 92.88% | 94.22% |
| A3 | 10 | O2 | -5.821 | -5.013 | -3.161 | -1.277 | -0.467 | 6.07% | 6.07% |
| A3 | 10 | O3 | -11.789 | -10.680 | -8.726 | -8.169 | -7.956 | 22.91% | 22.33% |
| A3 | 10 | N2O | -6.346 | -6.175 | -6.015 | -5.886 | -5.778 | 99.99% | 99.96% |
| A3 | 10 | NH3 | -11.698 | -10.298 | -8.229 | -7.690 | -7.428 | 80.40% | 73.08% |
| A3 | 100 | H2O | -2.954 | -2.922 | -2.889 | -2.858 | -2.832 | 0 en muestra | 0 en muestra |
| A3 | 100 | CO2 | -3.413 | -3.396 | -3.380 | -3.364 | -3.348 | 83.31% | 83.31% |
| A3 | 100 | CH4 | -4.713 | -4.668 | -4.622 | -4.578 | -4.540 | 100 en muestra | 100 en muestra |
| A3 | 100 | O2 | -5.865 | -5.112 | -3.346 | -1.427 | -0.592 | 3.92% | 3.92% |
| A3 | 100 | O3 | -8.293 | -8.213 | -8.141 | -8.077 | -8.021 | 94.39% | 92.61% |
| A3 | 100 | N2O | -6.224 | -6.169 | -6.116 | -6.065 | -6.020 | 100 en muestra | 100 en muestra |
| A3 | 100 | NH3 | -8.895 | -8.394 | -8.170 | -8.015 | -7.900 | 99.13% | 98.67% |

### Enriquecimiento respecto a A0 y A1

Para cada muestra se calcula Δ = log₁₀ X − log₁₀ X_ref y el cociente X/X_ref = 10^Δ. La tabla da la mediana y el intervalo central 95% del cociente, relativos a los perfiles efectivos de referencia. Es un cociente de abundancias dentro del modelo isochem, no un cociente de flujos de superficie.

| Escenario | h | Gas | X/A0: mediana [2,5%, 97,5%] | X/A1: mediana [2,5%, 97,5%] |
|---|---:|---|---:|---:|
| A1 | 1 | N2O | 0.0051 [1.2e-05, 3.9] | 0.0036 [8.5e-06, 2.8] |
| A1 | 1 | NH3 | 1.6 [0.012, 4.1e+02] | 0.36 [0.0027, 93] |
| A1 | 10 | N2O | 0.0041 [1.1e-05, 1.3] | 0.0029 [7.7e-06, 0.9] |
| A1 | 10 | NH3 | 0.62 [0.012, 63] | 0.14 [0.0026, 14] |
| A1 | 100 | N2O | 1.2 [0.64, 1.9] | 0.85 [0.45, 1.3] |
| A1 | 100 | NH3 | 0.21 [0.01, 8.2] | 0.048 [0.0023, 1.9] |
| A3 | 1 | N2O | 0.013 [1.3e-05, 18] | 0.0089 [9.1e-06, 13] |
| A3 | 1 | NH3 | 1.5 [0.012, 3.4e+02] | 0.33 [0.0028, 77] |
| A3 | 10 | N2O | 7.4 [3.5, 13] | 5.2 [2.4, 9] |
| A3 | 10 | NH3 | 53 [0.018, 3.3e+02] | 12 [0.004, 75] |
| A3 | 100 | N2O | 5.9 [4.6, 7.3] | 4.1 [3.2, 5.2] |
| A3 | 100 | NH3 | 60 [11, 1.1e+02] | 14 [2.6, 25] |

El CSV de enriquecimiento incluye Δ en dex, cuantiles y probabilidades también frente a A3, tanto con pesos iguales como con pesos nativos.

## Parámetros planetarios y térmicos

Cada celda muestra mediana [q16, q84]. `log_P_surf` está fija en 0 (1 bar). Las unidades siguen las configuraciones resueltas: radio en radios terrestres, temperatura en K y presiones en log₁₀(bar).

| Parámetro | A1 1 h | A1 10 h | A1 100 h | A3 1 h | A3 10 h | A3 100 h |
|---|---:|---:|---:|---:|---:|---:|
| R_p_ref | 1.212 [1.175, 1.257] | 1.208 [1.190, 1.228] | 1.216 [1.211, 1.222] | 1.164 [1.147, 1.191] | 1.227 [1.208, 1.246] | 1.220 [1.214, 1.227] |
| a1 | 1.308 [0.828, 1.745] | 1.273 [0.803, 1.727] | 1.380 [0.871, 1.801] | 1.393 [0.981, 1.778] | 1.256 [0.768, 1.750] | 1.402 [0.891, 1.806] |
| a2 | 0.159 [0.136, 0.188] | 0.120 [0.115, 0.126] | 0.120 [0.117, 0.123] | 0.242 [0.193, 0.311] | 0.131 [0.124, 0.138] | 0.125 [0.121, 0.128] |
| log_P1 | -2.851 [-3.365, -2.244] | -2.538 [-2.681, -2.394] | -2.623 [-2.697, -2.513] | -2.446 [-4.183, -1.135] | -2.573 [-2.831, -2.287] | -2.672 [-2.769, -2.484] |
| log_P2 | -1.693 [-2.017, -1.490] | -1.341 [-1.413, -1.301] | -1.340 [-1.367, -1.311] | -2.654 [-4.166, -1.997] | -1.401 [-1.476, -1.334] | -1.378 [-1.405, -1.334] |
| log_P3 | 0.366 [-0.099, 0.763] | 0.435 [0.047, 0.801] | 0.519 [0.164, 0.840] | 0.441 [0.093, 0.784] | 0.498 [0.166, 0.826] | 0.496 [0.175, 0.846] |
| T_ref | 212.073 [204.648, 219.251] | 222.687 [214.687, 228.793] | 219.014 [215.937, 223.568] | 214.092 [208.328, 220.216] | 217.337 [210.438, 226.710] | 216.058 [212.911, 222.774] |
| log_P_surf | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

Los cuantiles completos de los 15 parámetros están en [posterior_todos_los_parametros.csv](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a1_a3_integrated_20261028/posterior_full_parameters.csv). La probabilidad de una especie eliminada es N/A por construcción; las variantes restantes se encuentran en [probabilidades de todos los modelos](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a1_a3_integrated_20261028/probabilities_all_models.csv).

## Ablaciones moleculares emparejadas

ΔlnZ = lnZ(completo) − lnZ(sin X). El error numérico se combina en cuadratura; σ calibrada es un descriptor auxiliar, no una significancia frecuentista.

| Escenario | h | Especie retirada | ΔlnZ ± error | σ auxiliar | χ²red completo / sin X |
|---|---:|---|---:|---:|---:|
| A1 | 1 | N2O | -0.549 ± 0.241 | — | 0.95 / 0.92 |
| A1 | 1 | NH3 | -0.627 ± 0.240 | — | 0.95 / 0.96 |
| A1 | 1 | H2O | +12.076 ± 0.238 | 5.276 | 0.95 / 2.54 |
| A1 | 1 | CO2 | +470.389 ± 0.284 | 30.786 | 0.95 / 53.94 |
| A1 | 1 | CH4 | +11.100 ± 0.240 | 5.081 | 0.95 / 2.48 |
| A1 | 1 | O3 | -0.182 ± 0.241 | — | 0.95 / 1.08 |
| A1 | 10 | N2O | +0.416 ± 0.299 | 1.599 | 1.40 / 1.32 |
| A1 | 10 | NH3 | -1.865 ± 0.295 | — | 1.40 / 1.30 |
| A1 | 10 | H2O | +224.847 ± 0.300 | 21.354 | 1.40 / 27.55 |
| A1 | 10 | CO2 | +4285.645 ± 0.367 | 92.631 | 1.40 / 501.00 |
| A1 | 10 | CH4 | +53.315 ± 0.293 | 10.563 | 1.40 / 7.96 |
| A1 | 10 | O3 | +0.100 ± 0.294 | 1.228 | 1.40 / 1.67 |
| A1 | 100 | N2O | +9.834 ± 0.341 | 4.816 | 1.73 / 3.00 |
| A1 | 100 | NH3 | -0.590 ± 0.344 | — | 1.73 / 1.61 |
| A1 | 100 | H2O | +2252.633 ± 0.355 | 67.185 | 1.73 / 265.47 |
| A1 | 100 | CO2 | +47460.685 ± 0.431 | 308.112 | 1.73 / 5578.66 |
| A1 | 100 | CH4 | +307.905 ± 0.339 | 24.948 | 1.73 / 38.19 |
| A1 | 100 | O3 | +40.133 ± 0.340 | 9.217 | 1.73 / 6.68 |
| A3 | 1 | N2O | -0.030 ± 0.235 | — | 1.63 / 1.52 |
| A3 | 1 | NH3 | -0.526 ± 0.234 | — | 1.63 / 1.51 |
| A3 | 1 | H2O | +18.430 ± 0.234 | 6.394 | 1.63 / 3.62 |
| A3 | 1 | CO2 | +447.756 ± 0.297 | 30.042 | 1.63 / 50.53 |
| A3 | 1 | CH4 | +5.499 ± 0.234 | 3.754 | 1.63 / 2.24 |
| A3 | 1 | O3 | -0.823 ± 0.234 | — | 1.63 / 1.52 |
| A3 | 10 | N2O | +9.142 ± 0.292 | 4.664 | 1.22 / 2.34 |
| A3 | 10 | NH3 | -0.226 ± 0.293 | — | 1.22 / 1.35 |
| A3 | 10 | H2O | +242.078 ± 0.307 | 22.148 | 1.22 / 28.96 |
| A3 | 10 | CO2 | +4548.019 ± 0.354 | 95.422 | 1.22 / 532.31 |
| A3 | 10 | CH4 | +27.919 ± 0.291 | 7.760 | 1.22 / 4.86 |
| A3 | 10 | O3 | +0.241 ± 0.293 | 1.422 | 1.22 / 1.38 |
| A3 | 100 | N2O | +84.661 ± 0.347 | 13.217 | 3.57 / 13.55 |
| A3 | 100 | NH3 | +2.749 ± 0.345 | 2.853 | 3.57 / 4.06 |
| A3 | 100 | H2O | +1952.511 ± 0.371 | 62.558 | 3.57 / 231.66 |
| A3 | 100 | CO2 | +39540.784 ± 0.395 | 281.235 | 3.57 / 4651.86 |
| A3 | 100 | CH4 | +274.708 ± 0.337 | 23.578 | 3.57 / 36.55 |
| A3 | 100 | O3 | +20.838 ± 0.342 | 6.768 | 3.57 / 6.27 |

Las 36 diferencias y sus incertidumbres coinciden con las auditorías previas. Los contrastes evalúan inclusión molecular dentro del modelo y del dataset de la pareja.

## Regiones conjuntas N₂O/NH₃

R11: ambas abundancias ≥ referencia; R10: solo N₂O; R01: solo NH₃; R00: ninguna. K compara las odds posteriores de R11 frente a su complemento con las odds previas. El prior efectivo de cada log-abundancia es uniforme en [−12, −1] y las coordenadas son independientes.

| Escenario | h | Referencia | R11 | R10 | R01 | R00 | K(R11/complemento) | R11 ponderada |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| A1 | 1 | A0 | 4.81% | 3.87% | 50.49% | 40.83% | 0.066 | 4.79% |
| A1 | 1 | A1 | 2.83% | 3.87% | 37.01% | 56.28% | 0.045 | 2.84% |
| A1 | 10 | A0 | 1.56% | 2.06% | 42.92% | 53.46% | 0.021 | 1.51% |
| A1 | 10 | A1 | 0.59% | 1.51% | 25.69% | 72.20% | 0.009 | 0.57% |
| A1 | 100 | A0 | 18.17% | 56.15% | 6.66% | 19.02% | 0.288 | 18.15% |
| A1 | 100 | A1 | 1.69% | 25.00% | 5.09% | 68.22% | 0.026 | 1.75% |
| A3 | 1 | A0 | 10.24% | 8.75% | 43.73% | 37.29% | 0.148 | 10.39% |
| A3 | 1 | A1 | 6.42% | 10.72% | 30.77% | 52.09% | 0.106 | 6.50% |
| A3 | 10 | A0 | 80.40% | 19.58% | 0 en muestra | 0.01% | 5.322 | 80.29% |
| A3 | 10 | A1 | 73.07% | 26.89% | 0.01% | 0.03% | 4.181 | 72.81% |
| A3 | 100 | A0 | 99.13% | 0.87% | 0 en muestra | 0 en muestra | 148.379 | 99.18% |
| A3 | 100 | A1 | 98.67% | 1.33% | 0 en muestra | 0 en muestra | 113.924 | 98.65% |

Las cuatro regiones usan muestras conjuntas, no productos de probabilidades marginales. El CSV incluye conteos, estimaciones ponderadas y límites Wilson de referencia **solo bajo la hipótesis de muestras independientes**. El remuestreo de MultiNest y su incertidumbre de nested sampling no quedan cuantificados por ese intervalo ni por el ESS de concentración de pesos. Las colas con pocas o ninguna muestra permanecen sin precisión suficiente para inferencias extremas.

### Probabilidades marginales y prior

| Escenario | h | Referencia | Gas | P igual peso | P ponderada | P previa | K frente al complemento | Estado de cola |
|---|---:|---|---|---:|---:|---:|---:|---|
| A1 | 1 | A0 | N2O | 8.68% | 8.55% | 53.49% | 0.083 | sampled |
| A1 | 1 | A0 | NH3 | 55.30% | 55.20% | 81.37% | 0.283 | sampled |
| A1 | 1 | A1 | N2O | 6.71% | 6.64% | 52.13% | 0.066 | sampled |
| A1 | 1 | A1 | NH3 | 39.84% | 39.70% | 75.50% | 0.215 | sampled |
| A1 | 10 | A0 | N2O | 3.62% | 3.57% | 53.49% | 0.033 | sampled |
| A1 | 10 | A0 | NH3 | 44.48% | 44.71% | 81.37% | 0.183 | sampled |
| A1 | 10 | A1 | N2O | 2.11% | 2.03% | 52.13% | 0.020 | sampled |
| A1 | 10 | A1 | NH3 | 26.28% | 26.61% | 75.50% | 0.116 | sampled |
| A1 | 100 | A0 | N2O | 74.32% | 74.14% | 53.49% | 2.516 | sampled |
| A1 | 100 | A0 | NH3 | 24.83% | 24.84% | 81.37% | 0.076 | sampled |
| A1 | 100 | A1 | N2O | 26.68% | 26.67% | 52.13% | 0.334 | sampled |
| A1 | 100 | A1 | NH3 | 6.78% | 6.78% | 75.50% | 0.024 | sampled |
| A3 | 1 | A0 | N2O | 18.98% | 19.15% | 53.49% | 0.204 | sampled |
| A3 | 1 | A0 | NH3 | 53.97% | 54.11% | 81.37% | 0.268 | sampled |
| A3 | 1 | A1 | N2O | 17.14% | 17.22% | 52.13% | 0.190 | sampled |
| A3 | 1 | A1 | NH3 | 37.19% | 37.26% | 75.50% | 0.192 | sampled |
| A3 | 10 | A0 | N2O | 99.99% | 99.98% | 53.49% | 6116.040 | sparse_tail |
| A3 | 10 | A0 | NH3 | 80.40% | 80.30% | 81.37% | 0.939 | sampled |
| A3 | 10 | A1 | N2O | 99.96% | 99.95% | 52.13% | 2153.126 | sparse_tail |
| A3 | 10 | A1 | NH3 | 73.08% | 72.84% | 75.50% | 0.881 | sampled |
| A3 | 100 | A0 | N2O | 100 en muestra | 100.00% | 53.49% | — | unsampled_tail |
| A3 | 100 | A0 | NH3 | 99.13% | 99.18% | 81.37% | 26.187 | sampled |
| A3 | 100 | A1 | N2O | 100 en muestra | 100.00% | 52.13% | — | unsampled_tail |
| A3 | 100 | A1 | NH3 | 98.67% | 98.65% | 75.50% | 23.991 | sampled |

## Residuos espectrales y perfil térmico

Se aplicó el operador fotónico a la mediana puntual del espectro posterior en la rejilla original de 31 canales. Esa mediana puntual rebinada no es necesariamente el espectro del mejor vector de parámetros ni la mediana de espectros ya binados. El χ² de mejor ajuste procede del resultado POSEIDON; el otro corresponde a la mediana puntual. Los flujos y sus incertidumbres en `residual_bins.csv` son flujos espectrales observados Fp en W m⁻² m⁻¹; las longitudes de onda están en µm.

| Escenario | h | χ² mejor ajuste | χ² mediana puntual | Bins con residuo absoluto > 3σ | Tres canales con mayor residuo absoluto (µm) |
|---|---:|---:|---:|---:|---|
| A1 | 1 | 15.23 | 20.10 | 0 | 7.4763; 8.6865; 6.7647 |
| A1 | 10 | 22.35 | 23.26 | 0 | 14.3231; 12.3276; 9.1319 |
| A1 | 100 | 27.74 | 27.54 | 0 | 7.1116; 12.3276; 5.0111 |
| A3 | 1 | 26.12 | 28.75 | 0 | 14.3231; 7.1116; 11.1542 |
| A3 | 10 | 19.48 | 21.12 | 0 | 11.1542; 11.7263; 7.8597 |
| A3 | 100 | 57.19 | 57.64 | 2 | 7.1116; 6.7647; 18.2162 |

La separación `observado − mediana = (observado − verdad) + (verdad − mediana)` se verificó en cada bin. Los cuadrados de sus componentes incluyen un término cruzado y no se suman directamente. La prueba compara contra la verdad sintética y no establece una identificación molecular individual.

### Diferencia térmica de la mediana frente al perfil de entrada

Valores en K, mediana recuperada menos perfil de entrada, interpolados en presión logarítmica.

| Escenario | h | 1 bar | 0,1 bar | 0,01 bar | 0,001 bar |
|---|---:|---:|---:|---:|---:|
| A1 | 1 | +2.16 | +34.07 | -15.92 | -19.94 |
| A1 | 10 | +2.18 | +12.02 | -1.57 | +21.75 |
| A1 | 100 | +1.00 | +7.46 | -5.30 | +35.34 |
| A3 | 1 | +7.09 | +45.89 | -15.51 | -53.61 |
| A3 | 10 | +0.18 | +15.79 | -8.34 | +8.15 |
| A3 | 100 | +0.63 | +10.57 | -9.14 | +30.57 |

Los residuos por canal y las temperaturas de entrada y recuperadas están en los CSV vinculados al final.

## Extensión exploratoria A3–1000 h: A0 fija

Los tres contrastes usan el completo corregido y la misma realización de 1000 h. El auditor anterior validó productos primarios y evidencias, pero la aceptación formal sigue pendiente por seis NaN en momentos derivados de coordenadas fijas. No se alteró ese estado. Fijar una abundancia mantiene su opacidad y compara el modelo libre con un valor escalar concreto.

| Gas libre | Mediana log₁₀ X | Intervalo central 95% | P(≥A0) en muestras | P(≥A1) en muestras |
|---|---:|---:|---:|---:|
| N2O | -6.058 | [-6.087, -6.030] | 100 en muestra | 100 en muestra |
| NH3 | -9.130 | [-11.617, -8.667] | 78.71% | 61.82% |

| Fijación | ΔlnZ libre − fija ± error | χ²red efectivo del completo | Estado |
|---|---:|---:|---|
| N2O | +626.506 ± 0.384 | 14.29 | PENDING_FIXED_MOMENT_REVIEW |
| NH3 | -0.993 ± 0.382 | 14.29 | PENDING_FIXED_MOMENT_REVIEW |
| joint | +626.064 ± 0.382 | 14.29 | PENDING_FIXED_MOMENT_REVIEW |

| Umbral | R11: ambas sobre el umbral | R10: solo N₂O | R01: solo NH₃ | R00: ninguna | R11 ponderada |
|---|---:|---:|---:|---:|---:|
| A0 | 78.71% | 21.29% | 0 en muestra | 0 en muestra | 78.97% |
| A1 | 61.82% | 38.18% | 0 en muestra | 0 en muestra | 61.70% |

El ajuste de 1000 h es deficiente respecto al ruido supuesto. La evidencia compara modelos condicionados y no atribuye una fuente agrícola. Las tres fijaciones A0 de A3–100 h con el operador corregido no se ejecutaron; sus resultados con el operador histórico no se incorporan a esta serie.

## Interpretación y siguientes comprobaciones

Las ablaciones evalúan apoyo a incluir una opacidad; P(X≥A0/A1) y K regional describen abundancias dentro del modelo completo. Ninguna de estas cantidades identifica por sí sola una familia física ExoFarm frente a todas las atmósferas preagrícolas. Se recomienda examinar la sensibilidad a priors y umbrales, cuantificar incertidumbre de nested sampling, revisar el ajuste y explorar ruido/covarianza y perfiles verticales antes de fortalecer la atribución.

## Referencias metodológicas

- [Benneke y Seager (2013), *How to Distinguish between Cloudy Mini-Neptunes and Water/Volatile-Dominated Super-Earths*](https://doi.org/10.1088/0004-637X/778/2/153): contexto para comparación bayesiana y conversión descriptiva de evidencias; la calibración concreta aplicada aquí está en el script local.
- [Lin et al. (2021), *Differentiating Modern and Prebiotic Earth Scenarios for TRAPPIST-1e*](https://doi.org/10.1093/mnras/stab1486): referencia histórica del tratamiento comparativo de señales moleculares; sus condiciones instrumentales y modelos no sustituyen las de esta campaña.
- [Wogan et al. (2026), *Toward Inferring the Surface Fluxes of Biosignature Gases on Rocky Exoplanets from Telescope Spectra*](https://arxiv.org/abs/2604.21848): contexto para el problema de inferir emisiones de superficie. La comparación regional de abundancias de este informe es un análisis diferente y condicionado al prior.

## Productos y trazabilidad

Este es el informe vigente integrado para la serie A1/A3. Los documentos anteriores permanecen como bitácora metodológica e histórica; las tablas de esta edición son la referencia numérica de esta síntesis.

- [models.csv](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a1_a3_integrated_20261028/models.csv)
- [loo.csv](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a1_a3_integrated_20261028/loo.csv)
- [posterior_full_parameters.csv](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a1_a3_integrated_20261028/posterior_full_parameters.csv)
- [enrichment_full_nitrogen.csv](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a1_a3_integrated_20261028/enrichment_full_nitrogen.csv)
- [probabilities_all_models.csv](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a1_a3_integrated_20261028/probabilities_all_models.csv)
- [regions_joint.csv](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a1_a3_integrated_20261028/regions_joint.csv)
- [regions_summary.csv](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a1_a3_integrated_20261028/regions_summary.csv)
- [regions_marginal.csv](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a1_a3_integrated_20261028/regions_marginal.csv)
- [fit_summary.csv](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a1_a3_integrated_20261028/fit_summary.csv)
- [residual_bins.csv](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a1_a3_integrated_20261028/residual_bins.csv)
- [pt_probes.csv](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a1_a3_integrated_20261028/pt_probes.csv)
- [fixed_a0_1000h_exploratory.csv](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a1_a3_integrated_20261028/fixed_a0_1000h_exploratory.csv)
- [regions_1000h_exploratory.csv](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a1_a3_integrated_20261028/regions_1000h_exploratory.csv)
- [Hashes de insumos](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a1_a3_integrated_20261028/input_hashes.csv) y [procedencia](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a1_a3_integrated_20261028/provenance.json).
- [Script reproducible](../Thermal_Emission_Spectroscopy/scripts/analyse_proxima_a1_a3_corrected_integrated_20261028.py).
- [Atlas oficial A1/A3](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_posteriors_N2O_NH3_first_no_PT_proxima_20261028.png).
- [Bitácora y auditoría de campañas previas](life_proxima_analysis_checklist_2026-10-20.md).
