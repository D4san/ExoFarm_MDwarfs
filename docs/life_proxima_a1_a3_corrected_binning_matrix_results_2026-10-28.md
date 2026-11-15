# Matriz LIFE Proxima A1/A3 con binning corregido: cierre y resultados

**Fecha de auditoría:** 2026-10-28 (America/Bogota). **Campaña:** `proxima_A1_A3_corrected_bin_matrix_33_20261021_r01`. **Estado:** 33/33 retrievals auditados y aceptados; supervisor de recuperación terminó con `exit_code=0`, sin procesos activos.

## Alcance y procedencia

La campaña contiene 21 corridas A1 (tres modelos completos y 18 ablaciones LOO) y 12 ablaciones LOO A3. Los tres completos A3 son referencias corregidas independientes: 1/10 h de `a3_1_10h_binning_corrected_loo_20261020_r03` y 100 h de `a3_100h_binning_corrected_mpi14_resume_20261018`. En total, las tablas incluyen 36 modelos; solo 33 pertenecen a la campaña nueva.

- [README y ledger de campaña](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a1_a3_corrected_binning_matrix_loo_20261021_r01/README.md)
- [Manifiesto conciliado](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a1_a3_corrected_binning_matrix_loo_20261021_r01/manifest.csv) y [estado](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a1_a3_corrected_binning_matrix_loo_20261021_r01/campaign_state.json)
- [Recuperación y logs](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a1_a3_corrected_binning_matrix_loo_20261021_r01/recovery_20261027_power_restore_r01/)
- Validadores reutilizados: [auditor de productos LOO](../Thermal_Emission_Spectroscopy/scripts/validate_proxima_molecular_ablation_loo.py) y [calibración bilateral auxiliar](../Thermal_Emission_Spectroscopy/scripts/report_proxima_loo_lin_sigma.py).
- [Tabla de modelos y probabilidades por especie activa](life_proxima_a1_a3_corrected_binning_matrix_models_2026-10-28.csv) · [contrastes LOO](life_proxima_a1_a3_corrected_binning_matrix_loo_2026-10-28.csv) · [resumen estructurado](life_proxima_a1_a3_corrected_binning_matrix_audit_2026-10-28.json).

Los 33 retrievals terminaron con `return_code=0`, los 33 preflights MPI4 pasaron y la auditoría independiente aceptó 33/33 productos. Se verificaron hashes de datasets, parámetros y priors emparejados, exclusión molecular, finitud y consistencia entre POSEIDON y MultiNest. Cada posterior coincide fila a fila con las muestras equal-weight nativas de MultiNest; los espectros tienen cuantiles ordenados; P–T contiene 100 capas; `log_X` es finito; y los productos nativos concuerdan con los contadores finales. El callback corrected-bin estuvo ligado al muestreo y al postproceso; la discrepancia relativa máxima de cierre fue `2.26×10⁻¹⁴`. Los completos tienen 15 parámetros declarados/14 libres y cada LOO 14/13. Los tres comparadores A3 completos también pasaron revisión y comparten hash de dataset con sus LOO emparejados.

La cola se limitó a tres MPI4 simultáneos (12 ranks); no se detectaron violaciones ni uso de swap. El supervisor de recuperación (intento 2) terminó a `2026-10-28T20:13:03Z` con salida 0. El log conserva una solicitud de inicio concurrente rechazada por la protección: `[RECOVERY_ERROR] RuntimeError: Prior recovery supervisor 473 is still alive`. La instancia existente siguió trabajando y archivó los tres últimos A3–100 h; no hubo retrieval duplicado ni fallo de muestreo. Los snapshots previos se conservaron antes de conciliar el estado final.

## Comparación LOO emparejada

Se define `ΔlnZ = lnZ_completo − lnZ_sinX`; un valor positivo favorece incluir X. El error combina las incertidumbres numéricas en cuadratura. `σ_aux` es la conversión bilateral calibrada histórica de Sellke, un descriptor auxiliar, no una significancia frecuentista. La última columna da `P(log₁₀ X>A0)` del posterior completo correspondiente para N₂O/NH₃.

| Escenario | h | Se omite | ΔlnZ ± error numérico | σ_aux | χ²red completo / sin X | P(X>A0), completo |
|---|---:|---|---:|---:|---:|---:|
| A1 | 1 | H₂O | +12.076 ± 0.238 | 5.276 | 0.95 / 2.54 | — |
| A1 | 1 | CO₂ | +470.389 ± 0.284 | 30.786 | 0.95 / 53.94 | — |
| A1 | 1 | CH₄ | +11.100 ± 0.240 | 5.081 | 0.95 / 2.48 | — |
| A1 | 1 | O₃ | −0.182 ± 0.241 | — | 0.95 / 1.08 | — |
| A1 | 1 | N₂O | −0.549 ± 0.241 | — | 0.95 / 0.92 | 0.086810 |
| A1 | 1 | NH₃ | −0.627 ± 0.240 | — | 0.95 / 0.96 | 0.552956 |
| A1 | 10 | H₂O | +224.847 ± 0.300 | 21.354 | 1.40 / 27.55 | — |
| A1 | 10 | CO₂ | +4285.645 ± 0.367 | 92.631 | 1.40 / 501.00 | — |
| A1 | 10 | CH₄ | +53.315 ± 0.293 | 10.563 | 1.40 / 7.96 | — |
| A1 | 10 | O₃ | +0.100 ± 0.294 | 1.228 | 1.40 / 1.67 | — |
| A1 | 10 | N₂O | +0.416 ± 0.299 | 1.599 | 1.40 / 1.32 | 0.036207 |
| A1 | 10 | NH₃ | −1.865 ± 0.295 | — | 1.40 / 1.30 | 0.444781 |
| A1 | 100 | H₂O | +2252.633 ± 0.355 | 67.185 | 1.73 / 265.47 | — |
| A1 | 100 | CO₂ | +47460.685 ± 0.431 | 308.112 | 1.73 / 5578.66 | — |
| A1 | 100 | CH₄ | +307.905 ± 0.339 | 24.948 | 1.73 / 38.19 | — |
| A1 | 100 | O₃ | +40.133 ± 0.340 | 9.217 | 1.73 / 6.68 | — |
| A1 | 100 | N₂O | +9.834 ± 0.341 | 4.816 | 1.73 / 3.00 | 0.743229 |
| A1 | 100 | NH₃ | −0.590 ± 0.344 | — | 1.73 / 1.61 | 0.248259 |
| A3 | 1 | H₂O | +18.430 ± 0.234 | 6.394 | 1.63 / 3.62 | — |
| A3 | 1 | CO₂ | +447.760 ± 0.297 | 30.042 | 1.63 / 50.53 | — |
| A3 | 1 | CH₄ | +5.499 ± 0.234 | 3.754 | 1.63 / 2.24 | — |
| A3 | 1 | O₃ | −0.823 ± 0.234 | — | 1.63 / 1.52 | — |
| A3 | 10 | H₂O | +242.078 ± 0.307 | 22.148 | 1.22 / 28.96 | — |
| A3 | 10 | CO₂ | +4548.019 ± 0.354 | 95.416 | 1.22 / 532.31 | — |
| A3 | 10 | CH₄ | +27.919 ± 0.291 | 7.760 | 1.22 / 4.86 | — |
| A3 | 10 | O₃ | +0.241 ± 0.293 | 1.422 | 1.22 / 1.38 | — |
| A3 | 100 | H₂O | +1952.511 ± 0.371 | 62.558 | 3.57 / 231.66 | — |
| A3 | 100 | CO₂ | +39540.784 ± 0.395 | 281.235 | 3.57 / 4651.86 | — |
| A3 | 100 | CH₄ | +274.708 ± 0.337 | 23.578 | 3.57 / 36.55 | — |
| A3 | 100 | O₃ | +20.838 ± 0.342 | 6.768 | 3.57 / 6.27 | — |

### Modelos completos de referencia

| Escenario | h | lnZ ± error nativo | χ²red | Filas posteriores | P(N₂O>A0) | P(NH₃>A0) |
|---|---:|---:|---:|---:|---:|---:|
| A1 | 1 | 868.822919 ± 0.171231 | 0.95 | 7,695 | 0.086810 | 0.552956 |
| A1 | 10 | 889.986472 ± 0.210946 | 1.40 | 6,601 | 0.036207 | 0.444781 |
| A1 | 100 | 910.920720 ± 0.243879 | 1.73 | 6,461 | 0.743229 | 0.248259 |
| A3 | 1 | 866.282760 ± 0.166589 | 1.63 | 6,026 | 0.189844 | 0.539661 |
| A3 | 10 | 891.387174 ± 0.208811 | 1.22 | 7,036 | 0.999858 | 0.804008 |
| A3 | 100 | 894.331224 ± 0.246654 | 3.57 | 7,268 | 1.000000 | 0.991332 |

Los umbrales usados fueron `log₁₀(A0,N₂O) = −6.884325289637` y `log₁₀(A0,NH₃) = −9.950526295665`. La tabla de modelos conserva la probabilidad de cada retrieval donde el gas sigue activo; si la especie fue excluida, figura `N/A` por construcción.

## Lectura científica

**Resultado directo:** omitir H₂O, CO₂ y CH₄ empeora fuertemente la evidencia en los seis tiempos/escenarios. CO₂ destaca por contrastes extremos y ajustes inaceptables sin esa molécula. Esas cifras indican que el modelo sin CO₂ no reproduce los datos sintéticos con esta configuración; no son una detección aislada.

**Resultado directo:** O₃ tiene contrastes compatibles con cero a 1 h, casi nulos a 10 h y positivos a 100 h. A 100 h, los modelos sin O₃ también muestran ajuste pobre (`χ²red=6.68` en A1 y `6.27` en A3), por lo que el apoyo depende de la configuración y de esta realización de ruido.

**Resultado directo:** en A1, omitir N₂O y NH₃ se favorece levemente a 1 h. A 10 h el contraste de N₂O es pequeño (`+0.416`) y NH₃ favorece omitirlo (`−1.865`). A 100 h se favorece incluir N₂O (`+9.834`; el completo asigna `P(N₂O>A0)=0.7432`), mientras NH₃ favorece levemente la omisión (`−0.590`; `P(NH₃>A0)=0.2483`). Esta matriz no incluye LOO A3 de N₂O/NH₃: sus probabilidades en los completos son descriptivas y no reemplazan esas comparaciones.

**Interpretación y límite:** cada lnZ corresponde a su escenario, exposición y dataset. Solo son válidas aquí las parejas LOO con el mismo dataset, priors, operador y likelihood. Los valores absolutos de lnZ entre A1/A3 o entre exposiciones no son factores de Bayes. Las probabilidades posteriores sobre A0 describen abundancia dentro del modelo; el LOO compara modelos. Ninguno de estos resultados atribuye causalmente la atmósfera a ExoFarm frente a un escenario preagrícola.

Los retrievals históricos con el binning anterior se preservan como comparación metodológica. La diferencia de lnZ entre operadores no constituye un factor de Bayes molecular: cambia el forward model y la comparación requeriría reajustar ambos modelos bajo un contrato emparejado.

## Configuración y límites

Los datasets LIFE sintéticos tienen 31 canales entre 3–20 μm, una realización por escenario/exposición, `R=10000`, perfil térmico Madhu, química isochem, O₂ activo, superficie negra fija a 1 bar, sin inflación de errores, `N_live=800` y tolerancia de evidencia `0.5`. La likelihood es diagonal y no representa covarianza instrumental. La sigma calibrada se incluye solo para continuidad con análisis previos; no es significancia frecuentista.

Tras el cierre de la matriz, el atlas se regeneró y se designó oficial en PNG/PDF/SVG, con N₂O y NH₃ como primeras columnas, sin panel P–T ni nota sobre binning; los hashes de procedencia coinciden. Las figuras anteriores se preservan.
