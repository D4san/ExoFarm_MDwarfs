# A3 a 1 h y 10 h: ablaciones moleculares con binning corregido

**Bitácora de ejecución cerrada — 2026-10-21.** La campaña r03 completó los seis retrievals y pasó auditoría independiente; los resultados inferenciales aceptados están en el [informe de cierre](life_proxima_a3_1_10h_corrected_binning_loo_results_2026-10-21.md). Las secciones de progreso que siguen son registros históricos fechados durante la ejecución, no el estado actual. Supervisor, ledger reconciliado y productos por corrida permanecen en [r03](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1_10h_binning_corrected_loo_20261020_r03/).

## Pregunta y diseño

La prueba pregunta cuánto cambia la evidencia de inclusión de NH3 y N2O al corregir la integración fotónica del espectro LIFE, manteniendo la misma realización observada en cada duración. El contraste se hará dentro de cada exposición: el modelo sin NH3 o sin N2O se comparará solamente con el nuevo modelo completo ajustado al mismo archivo de 1 h o 10 h. Los resultados previos obtenidos con el operador antiguo se conservarán como sensibilidad metodológica; no reemplazan estos comparadores.

La campaña corre dos tandas secuenciales. Cada tanda usa tres samplers MPI5 simultáneos (15 ranks en total, con 16 CPUs lógicas visibles); la tanda de 10 h comienza después de que los tres casos de 1 h finalicen. No se reutilizan checkpoints. Los datasets observados existentes se mantienen sin regenerarlos:

| Duración | Archivo | SHA-256 esperado | Canales |
|---|---|---|---:|
| 1 h | `LIFE_proxima_A3_1h_O2_fixedBlack1bar_official.dat` | `a3043e5de76a834983949e6eca12636ea4de174ebdb2db0853155282c100dee2` | 31 |
| 10 h | `LIFE_proxima_A3_10h.dat` | `46a026504b9b9521fa29407a501169b9d3cfc433de40a91b8ade86d7767abb5b` | 31 |

La configuración congelada es `N_live=800`, tolerancia de evidencia 0.5, `R=10000`, intervalo de modelo 3–20 μm, perfil P–T Madhu, abundancias isochem, O2 retenido, superficie negra opaca fija a 1 bar y sin inflación de errores. El modelo completo declara 15 coordenadas y deja 14 libres; cada ablación declara 14 y deja 13 libres. Retirar una molécula elimina tanto su opacidad como su parámetro de abundancia. El callback de likelihood se vincula al operador de solapamiento fotónico corregido durante el muestreo; el mismo vínculo se exige en el postproceso.

La referencia metodológica de configuración es el baseline A3–100 h corregido aceptado en [campaña MPI14](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_100h_binning_corrected_mpi14_resume_20261018/README.md). Ese retrieval sirve para verificar el operador y la familia de priors; no se usará como comparador de evidencia para 1 h o 10 h.

## Historial de lanzamiento y progreso observado durante la ejecución

Se preservaron dos intentos de arranque que terminaron antes de cualquier muestreo:

1. [Log r01](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1_10h_binning_corrected_loo_20261020.supervisor.log): el guard de duplicados vio los archivos `.log` y `.pid` que el propio launcher acababa de crear y se detuvo antes de crear el directorio de campaña.
2. [Campaña r02](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1_10h_binning_corrected_loo_20261020_r02/): el preflight MPI5 devolvió `ValueError: Run or resolved-configuration path escaped the isolated campaign`; las rutas fijas del wrapper y del supervisor no coincidían. No se lanzó ningún sampler. Se conservaron estado y logs.

El intento aislado vigente fue [r03](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1_10h_binning_corrected_loo_20261020_r03/). Sus tres preflights MPI5 de 1 h pasaron (`PASS_MPI5_OPERATOR_PRIORS`, exit 0), con dimensiones 15/14, 14/13 y 14/13. El gate al inicio de la primera tanda observó 16 CPUs, 31,929,900 KiB disponibles y 8,388,608 KiB de swap libre. Se lanzaron `A3_1h_full`, `A3_1h_no_NH3` y `A3_1h_no_N2O` como tres `mpiexec -n 5`; las anotaciones runtime verifican callback corregido enlazado y cinco ranks identificados por corrida.

En la primera lectura de campaña, `campaign_status=RUNNING_WAVE_1`; los tres casos figuraban `sampling` en el `manifest.csv` y el muestreador había creado sus archivos MultiNest. El supervisor registró 15 ranks activos y los logs mostraban `generating live points`. En ese corte había 0 filas de posterior. La muestra de recursos de 19:44:56 UTC midió PSS total≈5.5 GiB, `MemAvailable=26,211,500 KiB` (≈25.0 GiB) y `SwapFree=8,388,608 KiB` (8 GiB). Este párrafo conserva solo el estado de aquella lectura inicial.

**Actualización de progreso — 19:45:56 UTC (14:45:56 COT):** NH3 sin el gas llevaba 1.000 reemplazos/1.016 evaluaciones y N2O sin el gas 900/909; los contadores del modelo completo todavía no eran legibles. Las tres posteriores equal-weight seguían en 0 filas. PSS agregado≈6.1 GiB, `MemAvailable=25,280,444 KiB` (≈24.1 GiB) y `SwapFree=8,388,608 KiB` (8 GiB). Continúan activos los 15 ranks, sin error fatal; 10 h sigue en cola.

**Nota de integridad del ledger:** durante la ejecución, el `manifest.csv` y `campaign_state.json.runs` diferían por un bug de serialización. Tras confirmar que el supervisor había salido, se preservaron snapshots de ambos archivos y se reconciliaron los seis registros con el manifiesto, los logs y los productos auditados. El estado final es `COMPLETE_VALIDATED`; las copias anteriores permanecen en la carpeta de campaña.

## Cierre y resultado

Los seis retrievals finalizaron con `return_code=0`. La auditoría comprobó configuración, priors, datasets, callback corrected-bin, posterior igualado con MultiNest, espectro, P–T, `log_X`, estadísticas nativas, finitud y contadores. ΔlnZ se define como `lnZ(full)−lnZ(sin X)` y se calcula por pareja de igual duración: NH₃ a 1 h `−0.526485±0.234278`; N₂O a 1 h `−0.029618±0.234922`; NH₃ a 10 h `−0.225706±0.292617`; N₂O a 10 h `+9.141993±0.292323`. Solo N₂O a 10 h favorece claramente la inclusión; la evidencia de NH₃ permanece equilibrada. El posterior de 10 h sitúa N₂O sobre A0 con probabilidad 0.99986 en el completo; para NH₃ es 0.8040. Las probabilidades sobre A0 y la evidencia de inclusión son cantidades distintas y no atribuyen origen agrícola.

La tabla, cuantiles por modelo, sigma auxiliar, figura SVG y límites interpretativos aparecen en el [informe de auditoría](life_proxima_a3_1_10h_corrected_binning_loo_results_2026-10-21.md) y en el [README final de campaña](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1_10h_binning_corrected_loo_20261020_r03/README.md).

## Reproducción y referencias operativas

- Supervisor y alcance: [r03/selected_scope.json](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1_10h_binning_corrected_loo_20261020_r03/selected_scope.json), [campaign_state.json](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1_10h_binning_corrected_loo_20261020_r03/campaign_state.json), [manifest.csv](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1_10h_binning_corrected_loo_20261020_r03/manifest.csv).
- Supervisor: [launcher](../Thermal_Emission_Spectroscopy/scripts/launch_proxima_a3_1_10h_binning_corrected_loo.py).
- Wrapper de likelihood y binning: [runner](../Thermal_Emission_Spectroscopy/scripts/run_life_retrieval_a3_short_binning_corrected.py), [operador fotónico](../Thermal_Emission_Spectroscopy/scripts/life_bin_operator_diagnostic.py).
- Estado final observado: seis retrievals cerrados y validados; tablas, ΔlnZ, errores en cuadratura, sigma auxiliar y probabilidades posteriores están en el informe de cierre.

La inferencia quedará condicionada a la calidad de ajuste y a la adecuación del perfil isochem. Un ΔlnZ positivo mide preferencia por el modelo completo frente a la ablación especificada; no identifica por sí solo una abundancia sobre A0. Las probabilidades `P(log10 X > A0)` se calcularán solo en el posterior donde la molécula siga siendo un parámetro libre. No se atribuirá posterior a la molécula retirada.
