# Regiones de abundancia A1 en los posteriores A3 corregidos

**Fecha:** 2026-10-26. **Estado:** masas previas verificadas y posprocesado completado para A3 a 1, 10 y 100 h; incertidumbre Monte Carlo de las colas y sensibilidad al umbral siguen abiertas.

## Hallazgo principal

Tenías razón: el prior efectivo de estas regiones ya está especificado en los retrievals. El runner define las abundancias como parámetros logarítmicos independientes con prior uniforme en log10 entre −12 y −1; las configuraciones resueltas de A3 a 1, 10 y 100 h confirman por separado esos tipos y límites para `log_N2O` y `log_NH3`. El código de configuración está en [run_life_retrieval.py](../Thermal_Emission_Spectroscopy/scripts/run_life_retrieval.py), y las configuraciones auditadas están en las campañas enlazadas bajo Fuentes.

Por tanto, las masas previas de los umbrales A1 se calculan directamente como q0 = (−1 − log10 X_A1)/11. No hace falta muestrear de nuevo el prior. Como los dos log-abundancias son coordenadas independientes, las cuatro masas conjuntas también son productos exactos de sus masas marginales:

| Región previa | Masa |
|---|---:|
| R11: N2O ≥ A1 y NH3 ≥ A1 | 39,3543 % |
| R10: solo N2O ≥ A1 | 12,7714 % |
| R01: solo NH3 ≥ A1 | 36,1445 % |
| R00: ambas < A1 | 11,7298 % |

Los umbrales usados son log10(N2O_A1) = −6,7338304684 y log10(NH3_A1) = −9,3048651166. Las masas previas están verificadas respecto de los priors efectivos declarados y auditados. Los K que siguen usan esas masas; su incertidumbre pendiente proviene de estimar las masas posteriores con muestras finitas, no de desconocer el prior.

## Cuatro celdas posteriores

| A3 | R11: ambas ≥ A1 | R10: solo N2O ≥ A1 | R01: solo NH3 ≥ A1 | R00: ninguna ≥ A1 |
|---:|---:|---:|---:|---:|
| 1 h | 6,42 % (387/6026) | 10,72 % (646/6026) | 30,77 % (1854/6026) | 52,09 % (3139/6026) |
| 10 h | 73,07 % (5141/7036) | 26,89 % (1892/7036) | 0,014 % (1/7036) | 0,028 % (2/7036) |
| 100 h | 98,665 % (7171/7268) | 1,335 % (97/7268) | 0 % (0/7268) | 0 % (0/7268) |

El K principal compara R11 con todo su complemento, es decir, ambas moléculas por encima de A1 frente a cualquier otra combinación:

| A3 | K(R11 / complemento) | Lectura |
|---:|---:|---|
| 1 h | 0,106 | Los datos desplazan masa fuera de la región donde ambas superan A1. |
| 10 h | 4,181 | La región conjunta alta gana odds frente a todas las combinaciones restantes. |
| 100 h | 113,924 | La región conjunta alta domina el posterior; el complemento tiene 97 muestras. |

Para aislar el aporte adicional de NH3 cuando N2O ya supera A1, K(R11/R10) vale 0,194 a 1 h, 0,882 a 10 h y 23,991 a 100 h. Así se ve que el cambio a 10 h está impulsado principalmente por N2O: la probabilidad conjunta de 73,07 % es alta, pero condicionar a N2O ≥ A1 no añade apoyo posterior para que NH3 cruce A1 frente al prior. A 100 h, todas las muestras de N2O ya superan A1 y el contraste condicional coincide con el K marginal de NH3.

Las celdas R01 y R00 de 10 h tienen solo una y dos muestras. A 100 h no aparece ninguna muestra con N2O < A1. No deben interpretarse K de esas colas como medidas precisas; para N2O a 10 h, el K marginal de 2153 también depende de solo tres muestras por debajo del umbral. En cambio, el K de R11 frente a su complemento sí se puede estimar en 10 h, donde el complemento reúne 1895 muestras.

## Evidencia de ausencia molecular

Las ablaciones LOO corregidas ya comparan, para A3, el modelo completo con el modelo que elimina a la vez la abundancia libre y la opacidad de cada molécula. La convención es ΔlnZ = lnZ(completo) − lnZ(sin X); valores positivos favorecen conservar la especie.

| A3 | ΔlnZ sin N2O | ΔlnZ sin NH3 | Resultado sobre la ausencia |
|---:|---:|---:|---|
| 1 h | −0,030 ± 0,235 | −0,526 ± 0,234 | Casi empate para N2O; inclinación débil a omitir NH3. |
| 10 h | +9,142 ± 0,292 | −0,226 ± 0,293 | Evidencia fuerte para incluir N2O; NH3 sigue prácticamente empatada. |
| 100 h | +84,661 ± 0,347 | +2,749 ± 0,345 | Evidencia abrumadora para incluir N2O y moderada para NH3. |

Así que la comparación de ausencia molecular está lista para N2O y NH3 en los casos A3 disponibles. La región de abundancia < A1 responde una pregunta distinta: contiene abundancias bajas pero no nulas, mientras que la ablación quita la especie del espectro. El ajuste completo de 100 h conserva una discrepancia relevante con el ruido asumido (χ² reducido = 3,57); por ello, la evidencia sigue siendo condicional al modelo isoquímico, al perfil P–T y al ruido diagonal.

## Qué falta para cerrar el análisis

1. **Cuantificar el error Monte Carlo de las fracciones posteriores y de K.** La tabla usa conteos de muestras equal-weight. En particular, la cola complementaria de R11 a 100 h tiene 97 muestras; las regiones bajas de 10 h y 100 h tienen soporte insuficiente. Si esas colas son parte del argumento, primero hay que estimar su error con los productos ponderados de MultiNest o réplicas independientes; solo después decidir si hace falta muestreo dirigido.
2. **Hacer una sensibilidad al umbral.** A1 se eligió después de revisar resultados previos, así que el análisis actual es retrospectivo/exploratorio. Conviene mostrar si la lectura persiste con límites físicos fijados por anticipado, por ejemplo A0 y A1, sin seleccionar el corte que maximice el efecto.
3. **Cerrar la auditoría de la matriz A1.** El manifiesto actual de la campaña r01 registra 18 retrievals con muestreo terminado y auditoría final pendiente, tres ablaciones A1–100 h en muestreo y 12 ablaciones A3 para H2O/CO2/CH4/O3 en cola. Esto no bloquea las conclusiones LOO de A3 para N2O/NH3, ya aceptadas en campañas separadas.
4. **Revisar adecuación antes de afirmar detectabilidad robusta.** La likelihood actual usa ruido diagonal de fotones; además, el χ² reducido de A3–100 h es 3,57. La robustez a perfiles verticales, estructura P–T y covarianza instrumental es trabajo científico pendiente.
5. **Separar enriquecimiento de atribución.** Superar A1 no identifica ExoFarm. Una conclusión ExoFarm frente a atmósfera preagrícola necesita distribuciones predictivas físicas para ambas familias y sus incertidumbres. Los tres A3–100 h con abundancias A0 fijas también siguen pendientes bajo el operador corregido si se quiere comparar contra esa hipótesis puntual; no son necesarios para el LOO de ausencia.

**Trabajo que no requiere nuevos retrievals ahora:** actualizar el texto de resultados A3 con estas celdas, los K calculados con el prior efectivo, el resultado LOO y la limitación de las colas. La matriz general A1/A3 y la comparación causal son tareas separadas.

## Fuentes y reproducción

- Script reproducible: [analyse_proxima_a3_corrected_a1_regions.py](../Thermal_Emission_Spectroscopy/scripts/analyse_proxima_a3_corrected_a1_regions.py). Produce las [cuatro celdas](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/a1_regions_corrected_20261026/joint_cells.csv), las [regiones marginales](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/a1_regions_corrected_20261026/marginal_regions.csv) y su [procedencia y hashes](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/a1_regions_corrected_20261026/provenance.json).
- Priors/configuración: [A3–1 h](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1_10h_binning_corrected_loo_20261020_r03/resolved/A3_1h_full.json), [A3–10 h](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1_10h_binning_corrected_loo_20261020_r03/resolved/A3_10h_full.json), [A3–100 h](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_100h_binning_corrected_mpi14_resume_20261018/resolved_configuration.json).
- Auditorías LOO: [A3–1/10 h](life_proxima_a3_1_10h_corrected_binning_loo_results_2026-10-21.md) y [A3–100 h](life_proxima_a3_100h_corrected_binning_molecular_ablation_2026-10-19.md).
- [Decisión metodológica de regiones](life_proxima_enrichment_region_comparison_decision_2026-10-21.md), [plan de homologación corregida](life_proxima_corrected_binning_update_plan_2026-10-21.md) y [checklist de análisis](life_proxima_analysis_checklist_2026-10-20.md).

Las probabilidades posteriores son fracciones descriptivas de las muestras de igual peso; la incertidumbre Monte Carlo formal no se ha cuantificado aquí. Los valores de 0 % y 100 % describen muestras sin soporte en una cola, no probabilidades poblacionales exactas.
