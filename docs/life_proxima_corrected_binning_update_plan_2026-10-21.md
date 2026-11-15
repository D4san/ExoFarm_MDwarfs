# Plan de actualización tras corregir el binning LIFE–Proxima

**Corte del plan:** 2026-10-21. **Estado actual (28-oct):** las 33 corridas de la matriz se ejecutaron y pasaron auditoría independiente. Esta nota conserva el alcance original; resultados aceptados en el [informe de cierre](life_proxima_a1_a3_corrected_binning_matrix_results_2026-10-28.md).

**Decisión separada — regiones de abundancia:** el cálculo desde los posteriores corregidos A3 se completó sin retrievals nuevos; su incertidumbre Monte Carlo y sensibilidad a umbrales siguen pendientes. La matriz homogénea de 33 retrievals ya se ejecutó y auditó. Tres corridas A3–100 h con abundancias fijas a A0 continúan como posible extensión opcional, separada de r01. Una comparación causal entre familias ExoFarm y preagrícola requiere primero definir distribuciones predictivas justificadas; no tiene conteo de corridas establecido. Véase la [decisión metodológica de regiones](life_proxima_enrichment_region_comparison_decision_2026-10-21.md).

## Decisión de alcance

La corrección del operador de binning exige rehacer los resultados de retrieval que dependen de cómo POSEIDON integra el espectro en los canales LIFE. Los productos del operador anterior siguen preservados como resultados históricos; no se mezclan con evidencias corregidas ni se sobrescriben.

Las campañas corregidas verificadas hasta este corte cubren A3 completo a 1, 10 y 100 h, y las ablaciones sin NH₃ y sin N₂O para cada uno de esos tiempos. La auditoría de A3–1000 h con restricciones A0 también tiene sus tres corridas corregidas; queda una revisión formal de seis NaN en desviaciones resumidas de parámetros fijados, no otro muestreo.

## Inventario original de retrievals propuestos

| Bloque | Estado final de la matriz | Retrievals nuevos de r01 |
|---|---|---:|
| A3 completo, 1/10/100 h | Corregido y validado | 0 |
| A3 sin NH₃ y sin N₂O, 1/10/100 h | Seis ablaciones corregidas y validadas | 0 |
| A3 sin H₂O, CO₂, CH₄ u O₃, 1/10/100 h | 12 LOO completados y auditados en matriz r01 | 12 |
| A1 completo, 1/10/100 h | Tres completos completados y auditados en matriz r01 | 3 |
| A1 sin H₂O, CO₂, CH₄, O₃, N₂O o NH₃, 1/10/100 h | 18 LOO completados y auditados en matriz r01 | 18 |
| **Subtotal homogéneo: tres completos A1 + 30 LOO nuevos** | A3 suma 12 LOO nuevos; tres completos A3 son referencias | **33** |
| A3–100 h con N₂O fija a A0, NH₃ fija a A0 y ambas fijas | Las tres referencias disponibles son del operador histórico | 3 |
| **Total si también se actualiza el contraste A0-fijo A3–100 h** | 33 de matriz + 3 referencias A0 | **36** |

La lista de 36 LOO corresponde a A1/A3 × 1/10/100 h × {H₂O, CO₂, CH₄, O₃, N₂O, NH₃}; O₂ sigue incluido en los modelos como en la matriz de referencia. Los seis LOO corregidos de A3 para N₂O/NH₃ no se repiten. Los retrievals A3–1000 h/A0 corregidos tampoco se repiten: se cierra aparte su salvedad de resumen.

Las tres restricciones A0-fijas a A3–1 h y A3–10 h serían seis retrievals adicionales si se decide extender esa comparación a todas las duraciones. No forman parte del subtotal de 36 ni de una autorización vigente.

## Productos recalculados al cierre de la matriz

1. **Completado:** se calcularon los 30 `ΔlnZ = lnZ_completo − lnZ_sinX` con parejas de igual escenario, exposición, dataset y configuración; errores numéricos en cuadratura y sigma calibrada solo como descriptor auxiliar.
2. **Completado para este informe:** se calcularon las probabilidades sobre A0 en posteriores que conservan la especie. El recálculo regional de abundancias es un análisis separado ya documentado; su incertidumbre Monte Carlo aún está abierta.
3. **Completado:** se generaron tablas e informe A1/A3 para los resultados corregidos; el atlas oficial versionado de completos se preservó.
4. **Completado:** se auditaron datasets/priors/hashes, callback y binding, posteriores, espectros, P–T, `log_X`, MultiNest, finitud y exclusión de especies antes de aceptar cifras.

## Puertas antes de lanzar

- Verificar por separado el SHA-256 de cada dataset y registrar si la corrección afecta solo al operador de retrieval o también a la generación del dato sintético. No regenerar observaciones ni errores si la procedencia confirma que siguen siendo los mismos; si el generador de datos también cambia, regenerar el dataset y todas sus parejas de forma consistente.
- Congelar para cada bloque la ventana espectral, los priors, la configuración y las realizaciones. La sensibilidad histórica de A3–100 h combinó el operador con una ventana nativa distinta (3.8–19 frente a 3–20 μm); no atribuir esa diferencia únicamente al binning.
- Si se desea cuantificar aisladamente el efecto del operador, diseñar un control aparte con idénticos datos, ventana, priors y configuración, cambiando solo el binning. No contar ese diagnóstico como parte de los 36 LOO.
- Mantener los productos anteriores y sus hashes; las nuevas campañas deben tener directorios y ledgers separados.
- Esta lista documenta las puertas aplicadas a r01 y no inicia trabajos. La ampliación de tres corridas A3–100 h con gases fijos a A0 sigue opcional y requeriría una decisión independiente.

## Referencias de estado

- [Resultados corregidos A3 a 1/10 h](life_proxima_a3_1_10h_corrected_binning_loo_results_2026-10-21.md).
- [A3–100 h corregido y sus dos LOO](life_proxima_a3_100h_corrected_binning_molecular_ablation_2026-10-19.md).
- [Comparación de A3–100 h histórico/corregido](life_proxima_a3_100h_binning_corrected_mpi14_resume_2026-10-18.md).
- [Checklist maestra](life_proxima_analysis_checklist_2026-10-20.md).
