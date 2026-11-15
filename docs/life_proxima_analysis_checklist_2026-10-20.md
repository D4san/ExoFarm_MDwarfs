# Checklist maestra de análisis LIFE–ExoFarm / Proxima

**Actualización 2026-10-29:** el [informe integrado vigente](life_proxima_a1_a3_retrievals_analisis_integrado_2026-10-29.md) reúne y reproduce los análisis con seis completos y 36 ablaciones corregidas; incluye posteriores, enriquecimiento, cuatro regiones, comparación de pesos, residuos, P–T y extensión exploratoria de 1000 h. Los registros de resultados inferiores se conservan como bitácora de su fecha. Sigue pendiente la incertidumbre de nested sampling y de colas, sensibilidad de prior/umbral, ajuste y ruido/covarianza; las tres fijaciones A0 de 100 h corregido no se ejecutaron. No se lanzaron retrievals para el nuevo informe.

**Corte del inventario inicial:** 2026-10-20. **Estado reconciliado:** 2026-10-21. **Alcance:** la línea de análisis de emisión térmica y retrievals LIFE Proxima A1/A3 discutida en este proyecto. No resume todas las etapas agrícolas ni toda la fotoquímica del repositorio. La actualización posterior a la campaña A3 de 1/10 h está registrada en el [plan de actualización por binning corregido](life_proxima_corrected_binning_update_plan_2026-10-21.md).

## Cómo leer esta lista

- `[x]` ejecutado y documentado; cuando se indica, auditado.
- `[~]` ejecutado con una salvedad o una decisión de aceptación pendiente.
- `[ ]` pendiente o requiere decidir el alcance antes de invertir en nuevas corridas.

## Análisis realizados

### 1. Cadena física y espectral

- [x] Se organizó la cadena MUSCLES Proxima → VULCAN A0–A3 → perfiles de química y P–T → emisión POSEIDON → espectros/datasets LIFE → retrieval POSEIDON.
- [x] Se compararon espectros A3 con química vertical, la salida de LIFE y abundancias isochemical. La comparación mostró que una discrepancia puede venir de la representación espectral y de perfiles/química, además de las abundancias.
- [x] Se diagnosticó y corrigió el operador de binning fotónico. El callback real se verificó en el muestreo y el postprocesado; los productos corregidos se conservaron separados de los históricos.
- [x] Se revisaron la resolución de opacidades y la representación P–T/Madhu, incluidos controles espectrales con química vertical fija.
- [x] Se evaluó el escalado de ruido fotónico clásico con tiempo de exposición y el S/N de plantillas. Es un diagnóstico previo al retrieval, no una validación completa del ruido instrumental.

### 2. Retrievals y comparaciones moleculares

- [x] Se regeneró y promovió la figura oficial V2 con muestras, `log_X` y P–T nuevos de A3–100 h; las versiones anteriores quedan archivadas y los seis casos tienen procedencia por hash. El producto promovido aún no incorpora los nuevos A3 de 1/10 h corregidos. [Figura, borrador y registro](life_proxima_official_plot_and_draft_update_2026-10-20.md).
- [x] Se actualizaron los análisis de A3–100 h desde el completo y ambas omisiones corregidas aceptadas. NH3 ≥A1: `98.6654 %`, `K nominal=23.991`, 95 % `[2.572,25.377] A1`, anchura `0.994 dex`; conjunta ≥A1: `98.6654 %`, `K nominal=113.924`. Se guardaron seis CSV con procedencia por fila y figura posterior/P–T. El [informe reproducible](life_proxima_a3_100h_corrected_results_update_2026-10-20.md) documenta también χ² explícito, redondeo y denominadores declarado/libre; todos los productos históricos permanecen preservados.
- [x] Se preservaron y validaron los seis retrievals completos oficiales A1/A3 a 1, 10 y 100 h.
- [x] Se completaron y auditaron los 36 LOO moleculares históricos. Sus resultados siguen siendo evidencia de la configuración histórica; no se deben mezclar con los nuevos contrastes corregidos como si compartieran forward model.
- [x] La matriz histórica A0–A3 × {10, 240 h} permanece intacta, 8/8.
- [x] Se calcularon posteriores de abundancia respecto a la A0 efectiva: cuantiles, desplazamiento/factor de enriquecimiento y probabilidades individuales y conjuntas de superar umbrales como A0/A1. También se documentó cómo dependen del prior y por qué no equivalen a evidencia de inclusión molecular.
- [x] Se fijaron N₂O, NH₃ y ambas a A0 en tres retrievals A3–100 h con el operador histórico. Fueron aceptados con salvedad por momentos `NaN` derivados de coordenadas constantes. Resultados `ln B` libre/A0: +29.440, +1.170 y +31.103, respectivamente.
- [x] Se ejecutó el completo A3–100 h con binning corregido y se auditó como comparador. `ln Z=894.331224 ± 0.246654`, `χ²_red=3.57`.
- [x] Se terminaron y auditaron las dos ablaciones A3–100 h corregidas, emparejadas con el mismo dataset y baseline:

  | Modelo sin | `Δln B` (completo − sin especie) | σ calibrado auxiliar | Lectura |
  |---|---:|---:|---|
  | NH₃ | +2.748991 ± 0.344630 | 2.853 | Favorece incluir NH₃ bajo este retrieval. |
  | N₂O | +84.660508 ± 0.346532 | 13.217 | Favorece con mucha fuerza incluir N₂O bajo este retrieval. |

- [x] Se compararon las ablaciones históricas y corregidas de A3–100 h. La evidencia de NH₃ pasó de `+1.506 ± 0.342` (σ=2.305) a `+2.749 ± 0.345` (σ=2.853); la de N₂O, de `+65.550 ± 0.341` (σ=11.672) a `+84.661 ± 0.347` (σ=13.217). El factor B equivalente sube aproximadamente de 4.51 a 15.63 para NH₃ y de `2.94×10²⁸` a `5.86×10³⁶` para N₂O.
- [x] Se documentó la comparación del completo A3–100 h histórico/corregido: `ln Z` 884.333/894.331 y `χ²_red` 4.94/3.57. Es una sensibilidad entre implementaciones, no un factor de Bayes molecular: cambiaron el operador y la cobertura nativa (3.8–19 frente a 3–20 μm), aunque el dataset observado de 31 canales es el mismo.
- [x] Se completó el retrieval corregido A3–1000 h y se hicieron tres contrastes A0 fijos. La evidencia primaria y los productos se auditaron. `ln B` libre/A0: N₂O fija `+626.5061 ± 0.3845`; NH₃ fija `−0.9927 ± 0.3825`; ambas fijas `+626.0635 ± 0.3822`. La lectura está condicionada por `χ²_red≈14.29` del completo.
- [x] **Actualización 2026-10-21:** se completaron y auditaron seis retrievals corregidos para A3–1/10 h: completo, sin NH₃ y sin N₂O por duración. Los resultados, hashes y cuatro contrastes emparejados están en el [informe final](life_proxima_a3_1_10h_corrected_binning_loo_results_2026-10-21.md). Junto con A3–100 h, ya están corregidos los tres completos A3 y las ablaciones A3 sin NH₃/sin N₂O para 1/10/100 h.
- [x] **Decisión 2026-10-21, ejecutada el 26-oct:** el prior efectivo y las cuatro celdas conjuntas N₂O/NH₃ se calcularon para A3 corregido a 1/10/100 h, sin retrievals nuevos. La incertidumbre Monte Carlo de las fracciones y K queda abierta; este análisis regional condicional no es una comparación causal entre ExoFarm y todo escenario preagrícola. [Resultados, hashes y límites](life_proxima_a1_regions_corrected_binning_2026-10-26.md).
- [x] **Actualización 2026-10-26 — regiones A1 corregidas:** prior efectivo confirmado en runner/configuraciones; cuatro celdas previas y posteriores recalculadas para A3 a 1/10/100 h con hashes. `K(R11/complemento)=0.106/4.181/113.924`. Se completó el cálculo puntual, no su incertidumbre Monte Carlo; las celdas R01/R00 de 10 h y las celdas con N₂O < A1 a 100 h tienen soporte escaso o nulo. [Informe reproducible](life_proxima_a1_regions_corrected_binning_2026-10-26.md).

### 3. Distinciones que deben conservarse al interpretar

- La **ablación LOO** elimina una especie y su opacidad; pregunta si los datos favorecen conservarla.
- La **restricción A0 fija** conserva la opacidad y fija la abundancia al escalar A0; pregunta si se prefiere dejarla libre frente a ese valor concreto.
- `P(log10 X > A0)` describe la dirección de una posterior de un modelo que conserva X. Para la especie retirada es N/A. No sustituye `Δln B`.
- `ln B` es el resultado bayesiano principal. El σ calibrado es una traducción descriptiva auxiliar, no una significancia frecuentista.
- Los resultados sintéticos condicionados a A3 pueden probar recuperación molecular/modelos especificados. Por sí solos no demuestran que una atmósfera real tenga origen ExoFarm ni que se haya distinguido causalmente de toda atmósfera preagrícola.

## Pendientes y decisiones

- [ ] **Restricciones A0 de A3–100 h corregido:** faltan tres comparadores emparejados (N₂O fija, NH₃ fija y ambas fijas) para reemplazar los valores históricos `29.440/1.170/31.103`. Las nuevas omisiones moleculares responden otra pregunta. No se han lanzado.
- [x] **Prior efectivo de regiones:** validado en el runner y las configuraciones resueltas; `log_N2O` y `log_NH3` son coordenadas independientes uniformes en log10 entre −12 y −1. Las masas previas marginales y conjuntas se calcularon analíticamente. La incertidumbre de K por cobertura posterior finita continúa en el pendiente siguiente.
- [ ] **Revisión formal de A3–1000 h/A0 corregido:** la auditoría encontró seis `NaN` solo en desviaciones derivadas de coordenadas fijas. Los parámetros muestreados y productos primarios pasan; los momentos centrados auxiliares dan dispersión cero y los originales se preservan. La aceptación continúa como `PENDING_FIXED_MOMENT_REVIEW` hasta cerrar explícitamente esta salvedad.
- [ ] **Adecuación del modelo:** explicar la tensión de ajuste, especialmente `χ²_red≈14.29` a 1000 h y los residuos restantes en el análisis corregido de 100 h. Evaluar de forma controlada P–T, perfiles verticales/isochem y estructura química antes de fortalecer afirmaciones.
- [ ] **Ruido instrumental realista:** la rama cerrada usa ruido fotónico clásico diagonal. Falta una evaluación con covarianza/estabilidad instrumental mediante LIFEsimMC/PHRINGE y un piso de ruido instrumental validado.
- [ ] **Atribución exclusiva al binning:** solo hace falta otra comparación si se desea afirmar cuánto del cambio lo causó el operador aislado. El ensayo tendría que mantener idénticos dataset, intervalo espectral, priors y configuración, variando únicamente el binning.
- [x] **Homologación completa A1/A3 con binning corregido (28-oct):** los 33 retrievals nuevos y los tres completos A3 de referencia pasaron auditoría independiente; los ledgers se reconciliaron tras detenerse el supervisor. Resultados, 30 contrastes emparejados y tablas en el [informe de cierre](life_proxima_a1_a3_corrected_binning_matrix_results_2026-10-28.md). Los 36 LOO históricos y el binning anterior se preservan. Tres A3–100 h con abundancias A0 fijas siguen siendo opcionales y separados de esta matriz.
- [ ] **Incertidumbre y sensibilidad de regiones A1:** cuantificar error Monte Carlo para las cuatro celdas/K y evaluar la sensibilidad a umbrales predefinidos. Los priors efectivos y las masas puntuales ya están validados; no se requiere retrieval nuevo salvo que se necesite resolver una cola escasamente muestreada.
- [ ] **Afirmación ExoFarm frente a A0:** para una conclusión causal se requiere comparar familias físicas de escenarios A0/A3 con perfiles y flujos trazables, incertidumbre de fotoquímica/P–T, alternativas no agrícolas y realizaciones de ruido; las ablaciones actuales aíslan soporte molecular, no origen.
- [ ] **Manuscrito:** integrar la lectura final corregida y resolver la compilación bloqueada por la clase `aastex701.cls` ausente en el entorno.

## Secuencia de cierre recomendada

1. Resolver por escrito la salvedad de los momentos fijos de A3–1000 h, sin modificar los productos originales.
2. Elegir si la pregunta prioritaria es robustez a P–T/perfiles verticales, realismo del ruido o generalización temporal. No lanzar una matriz nueva hasta congelar esa pregunta y sus controles.
3. Mantener separadas las afirmaciones: inclusión molecular (`Δln B`), dirección/tamaño de enriquecimiento (posterior sobre A0) y atribución ExoFarm (comparación causal de escenarios).
4. Actualizar el manuscrito solo después de acordar qué resultados corregidos se reportarán y con qué salvedades.

## Informes y productos fuente

- [Figura oficial y borrador actualizados; repetición completa pendiente](life_proxima_official_plot_and_draft_update_2026-10-20.md).
- [Regiones A1 en A3 corregido: cuatro celdas, priors y LOO de ausencia (2026-10-26)](life_proxima_a1_regions_corrected_binning_2026-10-26.md).
- [A3–100 h: resultados corregidos, probabilidades, K e intervalos actualizados](life_proxima_a3_100h_corrected_results_update_2026-10-20.md).
- [Síntesis de las capas LIFE y la pregunta ExoFarm](life_proxima_exofarm_retrieval_layers_synthesis_2026-10-11.md).
- [A3–100 h: LOO con bineador corregido](life_proxima_a3_100h_corrected_binning_molecular_ablation_2026-10-19.md).
- [A3–100 h: baseline corregido e historial de binning](life_proxima_a3_100h_binning_corrected_mpi14_resume_2026-10-18.md).
- [A3–100 h: referencias A0 fijas, operador histórico](life_proxima_a3_100h_a0_fixed_audit_2026-10-11.md).
- [A3–1000 h: auditoría de referencias A0 corregidas](life_proxima_a3_1000h_a0_fixed_binning_corrected_audit_2026-10-17.md).
- [36 ablaciones históricas](life_proxima_molecular_ablation_loo_2026-10-04.md) y [convención de σ](life_proxima_loo_sigma_lin_convention_2026-10-10.md).
- [Comparación de espectros verticales/LIFE/isochem](life_proxima_a3_vertical_life_isochem_comparison_2026-10-14.md), [capacidad P–T](life_proxima_a3_pt_spectral_capacity_2026-10-14.md) y [integración bayesiana en el manuscrito](life_manuscript_bayesian_integration_2026-10-16.md).
