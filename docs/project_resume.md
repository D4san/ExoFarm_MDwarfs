## Estado vigente — 2026-10-29

**Comparación con literatura LIFE y condiciones superficiales (29-oct):** [nota comparativa](life_proxima_detectabilidad_comparacion_literatura_2026-10-29.md). La preferencia A3 por N₂O en 10 h y el NH₃ a 100 h son condicionales. Las velocidades de deposición coinciden con la configuración terrestre de la instalación VULCAN; su sensibilidad y las realizaciones adicionales son extensiones opcionales sujetas a recursos. No se ejecutaron modelos nuevos. La referencia numérica sigue siendo el informe integrado.


**Referencia única LIFE Proxima A1/A3 — análisis integrado (29-oct):** [informe científico vigente](life_proxima_a1_a3_retrievals_analisis_integrado_2026-10-29.md), con 42 modelos corregidos, 36 ablaciones emparejadas, probabilidades y K de los siete gases frente a A0/A1/A3, posteriores de 15 parámetros, regiones conjuntas y diagnósticos. La extensión A3–1000 h está separada y mantiene `PENDING_FIXED_MOMENT_REVIEW`. Los informes y cortes LIFE anteriores que siguen son bitácora y evidencia de procedencia; la referencia numérica vigente es el informe integrado. Se recalculó desde productos existentes, sin lanzar retrievals. Siguen abiertas la incertidumbre de nested sampling, sensibilidad de prior/umbral, adecuación del ajuste y validación de ruido/covarianza.

**Integridad y estabilidad LIFE A1/A3 (28-oct):** se creó un [inventario SHA-256](evidence/life_proxima_a1_a3_release_2026-10-28/README.md) de 979 archivos y una copia en `E:\Respaldos\ExoFarm_MDwarfs\LIFE_Proxima_A1_A3_20261028`, verificada archivo por archivo. Incluye productos, referencias, datasets, figura y logs; se añadieron y verificaron por separado 12 registros de supervisor. Se guardó además una lista posterior de 240 paquetes del entorno POSEIDON, en el repo y el respaldo; no equivale a preservar el entorno ni las opacidades externas. Pendiente: asegurar esas dependencias y ordenar Git por lotes. En la revisión previa al inventario, el informe, las tablas, el manifiesto y la figura oficiales aún no estaban versionados; Git ignoraba los `.log`. Git mostraba además 16 rutas largas históricas ausentes de la copia de trabajo cuyos objetos permanecen en `HEAD`; investigar antes de registrar esas bajas o restaurarlas.

**Synthetic noise overlays on signal panels (2026-10-27):** the Proxima emission figure shows LIFE A3 1/10/100 h uncertainties as ±1σ curves on the lower N₂O/NH₃ panels; the A0–A3 spectra above remain clear. The JWST figure shows NIRSpec PRISM and MIRI LRS at 10/20/100 transits on the lower TRAPPIST-1e signal panels, with their original limits fixed. The five-transit series is omitted. No models or retrievals were run; R=200 is for presentation only. [LIFE report](life_proxima_emission_spectra_with_life_data_2026-10-27.md) · [JWST report](trappist1e_jwst_noise_curves_signal_panels_2026-10-27.md).

**Cerrada y auditada — homologación LIFE A1/A3 con binning corregido (campaña r01):** los 33 retrievals autorizados (21 A1 y 12 LOO A3) y los tres completos A3 de referencia pasaron la auditoría independiente. El manifiesto quedó conciliado en `complete_validated`; el supervisor terminó con exit 0 y no hay corridas activas. El informe final contiene los 30 contrastes LOO emparejados, errores en cuadratura y probabilidades `P(log10 X>A0)` cuando la especie permanece activa. [Informe y resultados](life_proxima_a1_a3_corrected_binning_matrix_results_2026-10-28.md) · [tablas de modelos](life_proxima_a1_a3_corrected_binning_matrix_models_2026-10-28.csv) · [contrastes LOO](life_proxima_a1_a3_corrected_binning_matrix_loo_2026-10-28.csv) · [ledger de campaña](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a1_a3_corrected_binning_matrix_loo_20261021_r01/README.md). Las campañas con binning anterior permanecen preservadas; comparar operadores es una sensibilidad metodológica, no un factor de Bayes molecular.

**Cerrada y validada — campaña A3 a 1 h y 10 h con binning corregido.** Las seis corridas (completo, sin NH₃ y sin N₂O en cada duración) terminaron con `return_code=0` y pasaron auditoría independiente de datos, priors, posteriores, espectros, P–T, `log_X`, MultiNest, finitud y operador/binding. El supervisor está detenido; el manifiesto y `campaign_state.json` se reconciliaron después de finalizar, preservando snapshots preauditoría. ΔlnZ favorece la inclusión de N₂O a 10 h (`+9.141993±0.292323`; sigma bilateral calibrado `+4.664`, auxiliar); los otros tres contrastes son compatibles con cero o favorecen levemente el modelo sin la especie. En el posterior completo a 10 h, `P(N₂O>A0)=0.99986` y `P(NH₃>A0)=0.8040`, probabilidades que no sustituyen la comparación de modelos. Informe, tablas y límites en el [informe de resultados](life_proxima_a3_1_10h_corrected_binning_loo_results_2026-10-21.md) y el [README/ledger r03](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1_10h_binning_corrected_loo_20261020_r03/README.md). La instrumentación rezagada durante RUNNING se reconcilió solo tras confirmar que el supervisor había terminado.

**Registro histórico del monitoreo durante la ejecución (20-oct):** los cortes de progreso y contadores parciales que siguen describen estados transitorios, no el estado vigente. La discrepancia de serialización entre manifiesto y `campaign_state.json` se resolvió en el cierre documentado arriba; se conservaron r01/r02 y los snapshots originales. La bitácora operativa recoge la secuencia completa.

**Atlas oficial LIFE A1/A3 (N₂O y NH₃ primero; sin panel P–T):** [PNG](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_posteriors_N2O_NH3_first_no_PT_proxima_20261028.png), [PDF](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_posteriors_N2O_NH3_first_no_PT_proxima_20261028.pdf), [SVG](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_posteriors_N2O_NH3_first_no_PT_proxima_20261028.svg) y [procedencia con hashes](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_posteriors_N2O_NH3_first_no_PT_proxima_20261028.provenance.json). La grilla compara los completos a 1/10/100 h y conserva los perfiles verticales de abundancia. Los atlas anteriores quedan preservados. [Informe y reproducción](life_proxima_corrected_binning_full_posteriors_plot_2026-10-28.md) · [cierre de matriz y LOO](life_proxima_a1_a3_corrected_binning_matrix_results_2026-10-28.md).

**Postprocesado actualizado — A3–100 h corregido:** se recalcularon evidencia, abundancias y probabilidades a partir de los productos auditados. NH3: `P(X≥A1)=98.6654 %`, mediana `13.630 A1`, intervalo central 95 % `[2.572,25.377] A1`, anchura `0.994 dex` y `K marginal=23.991`; región conjunta ≥A1: `98.6654 %`, `K(R11/complemento)=113.924`. N2O: mediana `4.145 A1`, 95 % `[3.238,5.176] A1`. El ln B de NH3 es moderado por su valor central, cercano al umbral 2.5 con error numérico 0.345. [Informe de abundancias y LOO](life_proxima_a3_100h_corrected_results_update_2026-10-20.md). Las tres restricciones A0 de **100 h** necesitan parejas corregidas antes de actualizar sus evidencias; no se han relanzado. Las masas previas y los K regionales se verificaron y actualizaron el 26-oct en el [informe de cuatro celdas](life_proxima_a1_regions_corrected_binning_2026-10-26.md); resta cuantificar su incertidumbre Monte Carlo. El manuscrito permanece para revisión de redacción en chat.

Checklist de la línea LIFE Proxima, con análisis cerrados y pendientes: [checklist maestra](life_proxima_analysis_checklist_2026-10-20.md); el [plan actualizado de retrievals a rehacer](life_proxima_corrected_binning_update_plan_2026-10-21.md) distingue los 33 de la matriz homogénea y tres A0-fijos adicionales.

**Corrección 2026-10-26 — regiones A1 en A3:** el prior efectivo ya está validado por las configuraciones resueltas: `log_N2O` y `log_NH3` son coordenadas independientes, uniformes en `[-12,-1]`. Se calcularon las cuatro masas posteriores y previas para A3 corregido a 1/10/100 h; `K(R11/complemento)=0.106/4.181/113.924`. El informe nuevo reemplaza la etiqueta previa de `K nominal`; solo queda estimar incertidumbre Monte Carlo y atender las colas escasas de 10/100 h. [Informe, CSV y hashes](life_proxima_a1_regions_corrected_binning_2026-10-26.md).

**Decisión para la pregunta ExoFarm/enriquecimiento:** las regiones bajo A1 se calcularon desde los posteriores corregidos A3 de 1/10/100 h, sin retrievals nuevos; siguen pendientes la incertidumbre Monte Carlo y la sensibilidad a umbrales predefinidos. La matriz homogénea de 33 retrievals quedó cerrada y auditada. Tres A3–100 h con gases fijos a A0 siguen como posible extensión separada, no incluida en esa matriz. La comparación causal ExoFarm–preagrícola aún requiere definir familias predictivas justificadas; su conteo de corridas no está establecido. [Método y resultados](life_proxima_enrichment_region_comparison_decision_2026-10-21.md).

**Cerrada y validada — A3–100 h con binning corregido, ablaciones moleculares (20-oct):** `A3_100h_no_NH3` (MPI8) y `A3_100h_no_N2O` (MPI7) finalizaron con `return_code=0`; el baseline corregido y ambas ablaciones pasaron auditoría independiente de productos, datos, priors, hashes y operador. En comparaciones emparejadas, `ΔlnZ=+2.748991±0.344630` al omitir NH3 y `+84.660508±0.346532` al omitir N2O; evidencia de inclusión más fuerte para N2O. Las sigma calibradas (+2.853 y +13.217) son auxiliares, no significancias frecuentistas. En posteriores que mantienen cada gas, `P(N2O>A0)=1.0000` y `P(NH3>A0)=0.9913` en el completo; la especie retirada queda N/A por construcción. `χ²_red` del completo=3.57 y del modelo sin N2O=13.55, límites relevantes de adecuación. Dataset SHA-256 `78662546181a5b74391a14b7b73ae80d879200a74db6a4bc5338e3ce7eee4705`, 31 canales, 3–20 μm. Auditoría, tablas y lectura científica: [informe de ablaciones](life_proxima_a3_100h_corrected_binning_molecular_ablation_2026-10-19.md); [README/ledger de campaña](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_100h_binning_corrected_loo_20261019/README.md). Se preservan todas las campañas y productos anteriores.

Las tres corridas A3–1000 h/A0 fija con binning corregido finalizaron exit 0 y pasaron la auditoría de productos, configuración emparejada, dataset, operador, priors, evidencias y hashes. La aceptación formal sigue pendiente por seis `NaN` en desviaciones derivadas de abundancias fijadas; los originales y sidecars están preservados. Ledger: `VALIDATED_PRIMARY_PRODUCTS_REQUIRES_REVIEW`; `PENDING_FIXED_MOMENT_REVIEW`.

**A3–100 h con binning corregido, MPI14 (muestreo y auditoría cerrados, 2026-10-20):** se detuvo la corrida serial a petición del usuario y se continuó su checkpoint validado en campaña aislada. MultiNest terminó con `exit_code=0`, 44.526 reemplazos, 1.474.040 evaluaciones y `ln(ev)=894.331224 ± 0.246654`; generó muestras, espectro, perfiles P–T y `log_X`. El baseline pasó la auditoría independiente del 2026-10-20 y se acepta como comparador de las ablaciones del mismo dataset. La comparación con muestras históricas sigue siendo una sensibilidad entre implementaciones (`ln Z=884.333304` frente a `894.331224`), no un Bayes factor molecular: además del operador cambió la rejilla 3.8–19 a 3–20 μm y el manifiesto histórico no conserva todos los límites de prior. El campo `error` del estado registra el primer preflight Open MPI fallido; se conserva como historial y queda explicado por el retry MPICH/Hydra PASS y el muestreo final exitoso. Véanse la [bitácora con tabla y figura](life_proxima_a3_100h_binning_corrected_mpi14_resume_2026-10-18.md) y la [campaña MPI14 validada](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_100h_binning_corrected_mpi14_resume_20261018/). Se preservan los seis completos oficiales, los 36 LOO, la matriz 8/8 y todos los productos previos.

**FR-Genghis, pausa solicitada 2026-10-04 16:38 COT:** la campaña quedó detenida por el usuario; no quedan procesos activos ni lock. Los cinco checkpoints de los bloques de 8.000 celdas coinciden por SHA-256 entre controller, sidecar, archivo y restart, y pasaron `lpjcheck -pedantic` con exit 0. No hay códigos finales ni productos aceptados. Configuración al pausar: CH4, un rank MPI por bloque, `MAX_PARALLEL=5` y retención completa. Véase el [registro de pausa](fr_genghis_campaign_pause_2026-10-04.md). `river_routing=false` y `reservoir=false` limitan la interpretación al routing local desactivado; no relanzar sin nueva autorización.

**FR-Genghis, seguimiento 2026-10-04 15:57 COT:** 00000_07999 guardó un checkpoint nuevo, SHA-256 3558df2823e16b0e75da872c64c07afffa62ae65334e01a5f09bd30045f0934a. El archivo archivado y restart/checkpoint.lpj coinciden byte a byte; lpjcheck -pedantic terminó con exit 0 e indicó reanudación desde el año 1566. Los otros hashes vigentes, también coincidentes entre archivo archivado y restart, son 08000_15999 8b3bdde51ef3348ef0309c17bda51de83f7d6a71307261f46670323cd63a8110; 16000_23999 8320adbef33619710eada5a49c9c87522116b4ded3b100e9580b38dd87d88605; 24000_31999 0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa; 32000_39999 dc6f24a5fc1adb6fc9c56703f664ca75590d7986c25eb90981b7bb9a4dbf3864. Siguen activos los cinco bloques con un rank MPI por bloque, CH4 y MAX_PARALLEL=5; no hay códigos finales ni productos aceptados. Hay 12 GiB de RAM disponible, 7,0 de 8 GiB de swap ocupados y 498 GiB libres en disco; vmstat no mostró intercambio sostenido. Se conserva MAX_PARALLEL=5. El exit 137 de 00000_07999 sigue siendo histórico del 2026-10-01. river_routing=false y reservoir=false limitan la interpretación al routing local desactivado.

**FR-Genghis, seguimiento 2026-10-04 14:56 COT:** los cinco bloques siguen en POTENTIAL_CHUNKS_RUNNING, con cinco LPJmL y cinco mpirun -np 1 activos; cada modelo usa ~39,9–40,0% de CPU. No hay checkpoint nuevo desde la revisión anterior. Los hashes del último checkpoint guardado, el archivo archivado y restart coinciden: 00000_07999 c59f10b4ee452d24259ae591ede142485bdc26413dbd381c758222ba9e1cfd6d; 08000_15999 8b3bdde51ef3348ef0309c17bda51de83f7d6a71307261f46670323cd63a8110; 16000_23999 8320adbef33619710eada5a49c9c87522116b4ded3b100e9580b38dd87d88605; 24000_31999 0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa; 32000_39999 dc6f24a5fc1adb6fc9c56703f664ca75590d7986c25eb90981b7bb9a4dbf3864. La RAM disponible es 11 GiB y quedan 499 GiB libres en disco; la swap llegó a 8,0/8,0 GiB ocupados, con 8 KiB libres. vmstat registró 8 KiB/s de swap-out en un intervalo y cero si/so en los tres siguientes; no se observa intercambio sostenido en esa ventana, pero la reserva de swap está agotada. No hay códigos finales ni productos aceptados. Mantengo MAX_PARALLEL=5 sin cambios. El exit 137 de 00000_07999 sigue siendo histórico, fechado el 2026-10-01. river_routing=false y reservoir=false limitan la interpretación al routing local desactivado.

**FR-Genghis, seguimiento 2026-10-04 13:55 COT:** la campaña sigue en POTENTIAL_CHUNKS_RUNNING con cinco bloques, cinco procesos LPJmL y un rank MPI por bloque; MAX_PARALLEL=5 y retención completa. 08000_15999 guardó un checkpoint nuevo, SHA-256 8b3bdde51ef3348ef0309c17bda51de83f7d6a71307261f46670323cd63a8110. El archivo archivado y restart/checkpoint.lpj coinciden byte a byte; lpjcheck -pedantic terminó con exit 0 e indicó reinicio desde el año 1494. Los otros hashes vigentes, también coincidentes entre restart y archivo, son 00000_07999 c59f10b4ee452d24259ae591ede142485bdc26413dbd381c758222ba9e1cfd6d; 16000_23999 8320adbef33619710eada5a49c9c87522116b4ded3b100e9580b38dd87d88605; 24000_31999 0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa; 32000_39999 dc6f24a5fc1adb6fc9c56703f664ca75590d7986c25eb90981b7bb9a4dbf3864. Los cinco LPJmL usan cerca de 40% de CPU; hay 11 GiB de RAM disponible, 7,6 de 8 GiB de swap ocupados y 499 GiB libres en disco. vmstat mostró actividad pequeña en la primera muestra y cero si/so en las cuatro siguientes: swap casi llena, sin paginación sostenida observada. No hay códigos finales ni productos aceptados. Se mantiene el límite MAX_PARALLEL=5. El exit 137 de 00000_07999 sigue siendo un incidente histórico del 2026-10-01. river_routing=false y reservoir=false limitan la interpretación al routing local desactivado.

**FR-Genghis, seguimiento 2026-10-04 11:53 COT:** los cinco bloques permanecen activos con un rank MPI por bloque, MAX_PARALLEL=5, CH4 y retención completa; cada LPJmL usa ~39,9--40,0% de CPU. No hay códigos finales ni productos aceptados. No se guardaron checkpoints nuevos; los SHA-256 de los cinco últimos eventos de controller coinciden con restart y archivo archivado (cmp=PASS): 00000_07999 c59f10b4ee452d24259ae591ede142485bdc26413dbd381c758222ba9e1cfd6d; 08000_15999 e8a62f04e7ec5b47c6e9e3468fc6a38910743f8cca7c659f0897ae23bdafcd2b; 16000_23999 8320adbef33619710eada5a49c9c87522116b4ded3b100e9580b38dd87d88605; 24000_31999 0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa; 32000_39999 dc6f24a5fc1adb6fc9c56703f664ca75590d7986c25eb90981b7bb9a4dbf3864. Los stdout avanzaron: 16000_23999 registra la fila 1493 y 32000_39999 la 1485; 00000 se mantiene en 1565, 08000 en 1493 y 24000 en 1485. Los cinco LPJmL, mpirun y checkpoint_runner siguen activos. Hay 11 GiB de RAM disponible y 500 GiB libres en disco; la swap está ocupada en 8,0 de 8 GiB (12 KiB libres). Las cuatro muestras de intervalo posteriores al promedio inicial de vmstat mostraron si/so=0, sin paginación sostenida en la ventana. Se conserva MAX_PARALLEL=5; no se cambia la ejecución. El exit 137 de 00000_07999 sigue siendo el incidente histórico del 2026-10-01. river_routing=false y reservoir=false limitan la interpretación al routing local desactivado.

**FR-Genghis, seguimiento 2026-10-04 10:52 COT:** los cinco bloques siguen activos con un rank MPI por bloque, MAX_PARALLEL=5, salida CH4 y retención completa; los cinco LPJmL usan ~39,9--40,0% de CPU. No hay códigos finales ni productos aceptados. No se guardaron checkpoints nuevos; para todos los bloques, el último SHA-256 del controller coincide con restart y archivo archivado, y cmp pasa: 00000_07999 c59f10b4ee452d24259ae591ede142485bdc26413dbd381c758222ba9e1cfd6d; 08000_15999 e8a62f04e7ec5b47c6e9e3468fc6a38910743f8cca7c659f0897ae23bdafcd2b; 16000_23999 8320adbef33619710eada5a49c9c87522116b4ded3b100e9580b38dd87d88605; 24000_31999 0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa; 32000_39999 dc6f24a5fc1adb6fc9c56703f664ca75590d7986c25eb90981b7bb9a4dbf3864. Las últimas filas visibles siguen en 1565 (00000), 1493 (08000) y 1485 (24000); los otros segmentos consultados continúan activos desde checkpoint. Hay 11 GiB de RAM disponible y 500 GiB libres en disco; la swap llegó a 8,0/8,0 GiB, sin bytes libres. En vmstat, las cuatro muestras de intervalo posteriores a la línea promedio inicial mostraron si/so=0; una indicó un proceso bloqueado, sin que la ventana muestre paginación sostenida. La swap está agotada y mantengo MAX_PARALLEL=5 bajo vigilancia, sin cambiar procesos en esta lectura. El exit 137 del controller.stderr de 00000_07999 sigue siendo histórico (2026-10-01). river_routing=false y reservoir=false limitan la interpretación al routing local desactivado.

**FR-Genghis, seguimiento 2026-10-04 09:51 COT:** continúan activos los cinco bloques con un rank MPI cada uno, MAX_PARALLEL=5, salida CH4 y retención completa; los cinco LPJmL usan ~39,9--40,0% de CPU. No hay códigos finales ni productos aceptados. No hubo checkpoint nuevo: los hashes del último evento del controller coinciden con restart y archivo archivado, y cmp pasa para los cinco bloques: 00000_07999 c59f10b4ee452d24259ae591ede142485bdc26413dbd381c758222ba9e1cfd6d; 08000_15999 e8a62f04e7ec5b47c6e9e3468fc6a38910743f8cca7c659f0897ae23bdafcd2b; 16000_23999 8320adbef33619710eada5a49c9c87522116b4ded3b100e9580b38dd87d88605; 24000_31999 0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa; 32000_39999 dc6f24a5fc1adb6fc9c56703f664ca75590d7986c25eb90981b7bb9a4dbf3864. Las filas recientes visibles son 1565 en 00000_07999, 1493 en 08000_15999 y 1485 en 24000_31999; 16000 y 32000 continúan activos desde sus checkpoints. Hay 11 GiB de RAM disponible y 500 GiB libres en disco, pero la swap está ocupada en 8,0 de 8 GiB, con solo 4 MiB libres. Las cuatro muestras de intervalo de vmstat mostraron si/so=0: no se observa paginación sostenida en esa ventana, aunque el margen de swap está prácticamente agotado. Mantengo MAX_PARALLEL=5 y vigilo recursos. El exit 137 presente en el stderr de 00000_07999 corresponde al incidente histórico del 2026-10-01. river_routing=false y reservoir=false limitan la interpretación al routing local desactivado.

**FR-Genghis, seguimiento 2026-10-04 08:50 COT:** los cinco bloques siguen activos con un rank MPI por bloque, MAX_PARALLEL=5, CH4 y retención completa; los cinco LPJmL usan 39,9% de CPU y no hay códigos finales ni productos aceptados. No se guardaron checkpoints nuevos: para los cinco bloques, los SHA-256 del último evento del controller, restart y archivo archivado coinciden y cmp pasa. Hashes vigentes: 00000_07999 c59f10b4ee452d24259ae591ede142485bdc26413dbd381c758222ba9e1cfd6d; 08000_15999 e8a62f04e7ec5b47c6e9e3468fc6a38910743f8cca7c659f0897ae23bdafcd2b; 16000_23999 8320adbef33619710eada5a49c9c87522116b4ded3b100e9580b38dd87d88605; 24000_31999 0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa; 32000_39999 dc6f24a5fc1adb6fc9c56703f664ca75590d7986c25eb90981b7bb9a4dbf3864. El registro más reciente sigue en la fila 1493 de 08000_15999; los otros segmentos visibles no cambiaron. La memoria disponible es 11 GiB, quedan 500 GiB en disco y la swap está ocupada en 8,0 de 8 GiB (30 MiB libres). En vmstat, las cuatro filas de intervalo posteriores al promedio inicial mostraron si/so=0; no se observa paginación sostenida en esa ventana. La reserva de swap está agotada y queda bajo vigilancia; mantengo el límite de cinco procesos. El exit 137 que aparece en controller.stderr.log de 00000_07999 pertenece al incidente histórico del 2026-10-01. river_routing=false y reservoir=false limitan la interpretación al routing local desactivado.

**FR-Genghis, seguimiento 2026-10-04 07:49 COT:** siguen activos los cinco bloques con un rank MPI cada uno, MAX_PARALLEL=5, salida CH4 y retención completa. Los cinco LPJmL usan 39,8--39,9% de CPU; no hay códigos finales ni productos aceptados. Los SHA-256 del checkpoint guardado, restart y archivo archivado coinciden (cmp=PASS) y no cambiaron desde la revisión anterior: 00000_07999 c59f10b4ee452d24259ae591ede142485bdc26413dbd381c758222ba9e1cfd6d; 08000_15999 e8a62f04e7ec5b47c6e9e3468fc6a38910743f8cca7c659f0897ae23bdafcd2b; 16000_23999 8320adbef33619710eada5a49c9c87522116b4ded3b100e9580b38dd87d88605; 24000_31999 0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa; 32000_39999 dc6f24a5fc1adb6fc9c56703f664ca75590d7986c25eb90981b7bb9a4dbf3864. El segmento más reciente de 08000_15999 registró la fila 1493. Hay 11,3 GiB disponibles y 500 GiB libres en disco; la swap está ocupada en 7,94 de 8 GiB (unos 61 MiB libres). vmstat 1 6 mostró valores nulos de swap-in/out después de la primera muestra, así que no se observa paginación sostenida en ese intervalo. Mantengo el límite de cinco procesos y vigilo la reserva de swap. El exit 137 de 00000_07999 sigue siendo histórico, del 2026-10-01. river_routing=false y reservoir=false limitan la interpretación al routing local desactivado.

**FR-Genghis, seguimiento 2026-10-04 06:49 COT:** los cinco bloques continúan activos con un rank MPI por bloque, MAX_PARALLEL=5, CH4 y retención completa. 16000_23999 guardó el checkpoint 8320adbef33619710eada5a49c9c87522116b4ded3b100e9580b38dd87d88605; hash del controlador, archivo archivado y restart coinciden, cmp pasa y lpjcheck -pedantic devuelve 0, con restart desde año 1492. Los demás hashes no cambiaron: 00000_07999 c59f10b4ee452d24259ae591ede142485bdc26413dbd381c758222ba9e1cfd6d; 08000_15999 e8a62f04e7ec5b47c6e9e3468fc6a38910743f8cca7c659f0897ae23bdafcd2b; 24000_31999 0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa; 32000_39999 dc6f24a5fc1adb6fc9c56703f664ca75590d7986c25eb90981b7bb9a4dbf3864. Los cinco LPJmL usan alrededor de 40% de CPU. La swap bajó a 6,8 de 8 GiB y quedan 10 GiB de RAM disponible y 500 GiB libres en /home; vmstat mostró solo actividad breve, no sostenida. No hay error fatal ni códigos finales; el exit 137 en 00000_07999 es histórico del 2026-10-01. Se mantiene MAX_PARALLEL=5. river_routing=false y reservoir=false limitan la interpretación al routing local desactivado.

**FR-Genghis, seguimiento 2026-10-04 05:49 COT:** los cinco bloques siguen activos con un rank MPI cada uno, MAX_PARALLEL=5, salida CH4 y retención completa. No hay checkpoints nuevos; los últimos hashes del controlador/restart se mantienen: 00000_07999 c59f10b4ee452d24259ae591ede142485bdc26413dbd381c758222ba9e1cfd6d; 08000_15999 e8a62f04e7ec5b47c6e9e3468fc6a38910743f8cca7c659f0897ae23bdafcd2b; 16000_23999 eacf565edfd881572b7db1cbf64eae100f060af6b19836dc24d16a4e0a886ec3; 24000_31999 0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa; 32000_39999 dc6f24a5fc1adb6fc9c56703f664ca75590d7986c25eb90981b7bb9a4dbf3864. Cada LPJmL continúa alrededor de 40% de CPU y no hay errores fatales ni códigos finales. La swap ahora está completamente ocupada (8,0 de 8,0 GiB); quedan 11 GiB de RAM disponible y 501 GiB libres en /home. vmstat no mostró intercambio sostenido después del primer intervalo, pero el margen de swap se agotó. Se mantiene MAX_PARALLEL=5 y no se amplía. El exit 137 de 00000_07999 sigue siendo un incidente histórico del 2026-10-01. river_routing=false y reservoir=false limitan la interpretación al routing local desactivado.

**FR-Genghis, seguimiento 2026-10-04 04:48 COT:** los cinco bloques siguen activos con un rank MPI por bloque, MAX_PARALLEL=5, salida CH4 y retención completa. Los últimos checkpoints no cambiaron y sus restart coinciden con los hashes del controlador y archivo archivado: 00000_07999 c59f10b4ee452d24259ae591ede142485bdc26413dbd381c758222ba9e1cfd6d; 08000_15999 e8a62f04e7ec5b47c6e9e3468fc6a38910743f8cca7c659f0897ae23bdafcd2b; 16000_23999 eacf565edfd881572b7db1cbf64eae100f060af6b19836dc24d16a4e0a886ec3; 24000_31999 0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa; 32000_39999 dc6f24a5fc1adb6fc9c56703f664ca75590d7986c25eb90981b7bb9a4dbf3864. Los cinco LPJmL mantienen cerca de 40% de CPU, sin error fatal actual ni códigos finales; el exit 137 de 00000_07999 es histórico del 2026-10-01. Hay 11 GiB de RAM disponible y 501 GiB libres en /home, pero la swap subió a 7,8 de 8,0 GiB (161 MiB libres). vmstat registró actividad solo en el primer intervalo y cero intercambio en los tres siguientes, sin paginación sostenida observada. Se conserva MAX_PARALLEL=5 sin ampliarlo y se vigila el margen de memoria. river_routing=false y reservoir=false limitan la interpretación al routing local desactivado.

**FR-Genghis, seguimiento 2026-10-04 03:47 COT:** se mantienen activos los cinco bloques, un rank MPI por bloque, MAX_PARALLEL=5, salida CH4 y retención completa. El bloque 32000_39999 guardó el checkpoint dc6f24a5fc1adb6fc9c56703f664ca75590d7986c25eb90981b7bb9a4dbf3864; el hash de controller, archivo y restart coincide, cmp pasa y lpjcheck -pedantic termina con 0, indicando reanudación desde el año 1484. Los últimos SHA-256 sin cambio son 00000_07999 c59f10b4ee452d24259ae591ede142485bdc26413dbd381c758222ba9e1cfd6d; 08000_15999 e8a62f04e7ec5b47c6e9e3468fc6a38910743f8cca7c659f0897ae23bdafcd2b; 16000_23999 eacf565edfd881572b7db1cbf64eae100f060af6b19836dc24d16a4e0a886ec3; 24000_31999 0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa. Los cinco procesos LPJmL usan cerca de 40% de CPU; quedan 11 GiB de RAM disponibles, 6,5 de 8 GiB de swap están ocupados y hay 501 GiB libres en /home. vmstat no mostró intercambio sostenido. No hay error fatal actual ni códigos finales; el exit 137 de 00000_07999 es el incidente histórico del 2026-10-01. Se mantiene el máximo de cinco procesos. river_routing=false y reservoir=false limitan la interpretación al routing local desactivado.

**FR-Genghis, seguimiento 2026-10-04 02:46 COT:** los cinco bloques continúan activos con un rank MPI cada uno, MAX_PARALLEL=5, salida CH4 y retención completa. El bloque 00000_07999 guardó un checkpoint nuevo: SHA-256 c59f10b4ee452d24259ae591ede142485bdc26413dbd381c758222ba9e1cfd6d; el controlador, el archivo archivado y restart/checkpoint.lpj coinciden, cmp pasa y lpjcheck -pedantic devuelve 0, con restart desde año 1564. Los demás checkpoints y hashes coinciden sin cambios: 08000_15999 e8a62f04e7ec5b47c6e9e3468fc6a38910743f8cca7c659f0897ae23bdafcd2b; 16000_23999 eacf565edfd881572b7db1cbf64eae100f060af6b19836dc24d16a4e0a886ec3; 24000_31999 0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa; 32000_39999 56929c418b142ba637156110295a9c531f9e3a0b7bf5c1d48adb204127fdd792. Los cinco LPJmL siguen cerca de 40% de CPU; RAM disponible 12 GiB, swap usada 6,7 de 8 GiB y 502 GiB libres en /home. vmstat no mostró intercambio sostenido. Se mantiene MAX_PARALLEL=5. No hay error fatal actual ni códigos finales; el exit 137 de 00000_07999 continúa siendo histórico del 2026-10-01. river_routing=false y reservoir=false limitan la interpretación al routing local desactivado.

**FR-Genghis, seguimiento 2026-10-04 01:46 COT:** los cinco bloques continúan activos, con un rank MPI por bloque, MAX_PARALLEL=5, salida CH4 y retención completa de checkpoints. Los SHA-256 vigentes de controller.log y restart son: 00000_07999 88f680589b802dd42ca806fb59eaa8c23ed4f84ed0cc2543fc11e8481c29c60f; 08000_15999 e8a62f04e7ec5b47c6e9e3468fc6a38910743f8cca7c659f0897ae23bdafcd2b; 16000_23999 eacf565edfd881572b7db1cbf64eae100f060af6b19836dc24d16a4e0a886ec3; 24000_31999 0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa; 32000_39999 56929c418b142ba637156110295a9c531f9e3a0b7bf5c1d48adb204127fdd792. Para los checkpoints nuevos de 08000_15999 y 24000_31999, hash del controlador, archivo archivado y restart coinciden, cmp pasa y lpjcheck -pedantic devuelve 0; informa reanudación desde los años 1492 y 1484. Los cinco LPJmL mantienen cerca de 40% de CPU. Quedan 11 GiB disponibles y 503 GiB en /home, pero la swap está en 7,0 de 8,0 GiB; vmstat no mostró intercambio sostenido tras el primer intervalo. Se conserva MAX_PARALLEL=5 sin ampliarlo y se vigila la memoria. Los stderr recientes solo muestran advertencias conocidas; el exit 137 de 00000_07999 sigue siendo histórico del 2026-10-01. Aún no hay códigos finales ni productos aceptados. river_routing=false y reservoir=false limitan la interpretación al routing local desactivado.

**FR-Genghis, seguimiento 2026-10-03 19:40 COT:** el bloque 16000_23999 guardó un checkpoint nuevo tras la fila anual 1490: SHA-256 eacf565edfd881572b7db1cbf64eae100f060af6b19836dc24d16a4e0a886ec3. La copia archivada y restart/checkpoint.lpj coinciden; lpjcheck -pedantic terminó con código 0 e indicó reanudación desde el año 1490. El proceso ya continúa en un segmento nuevo. Los otros checkpoints permanecen: 00000_07999, año 1561, 88f680589b802dd42ca806fb59eaa8c23ed4f84ed0cc2543fc11e8481c29c60f; 08000_15999, año 1489, 6479e6dcb8e3f6e122557a70cbbe04f5f13c3c7dd2c80eabff64dd2c7cabef7d; 24000_31999, año 1481, 70174d7e6bfb430dd691f87529472571949b7215e4099043cf1ee53adbd454ae; y 32000_39999, año 1481, 56929c418b142ba637156110295a9c531f9e3a0b7bf5c1d48adb204127fdd792. En los cinco bloques, el SHA-256 del restart activo coincide con el último checkpoint registrado por el controlador. Las últimas filas anuales visibles son 1563, 1491, 1490, 1483 y 1483, respectivamente. Siguen activos cinco LPJmL y cinco mpirun con un rank por bloque, cerca de 40% de CPU cada uno; no hay códigos finales ni productos aceptados, y los stderr recientes no muestran fallos fatales. El exit 137 de 00000_07999 sigue limitado al incidente histórico del 2026-10-01. Quedan 9,6 GiB de RAM disponible, 6,1 GiB de swap usada de 8 GiB y 505 GiB libres en el filesystem. vmstat mostró un intercambio pequeño en el primer intervalo y cero si/so en los dos siguientes, sin paginación sostenida. Se conserva MAX_PARALLEL=5, CH4 y la retención completa de checkpoints; no aumento el paralelismo. river_routing=false y reservoir=false limitan la interpretación al routing local desactivado.
**FR-Genghis, seguimiento 2026-10-03 13:35 COT:** la campaña sigue en ejecución con cinco procesos LPJmL activos, un rank MPI por bloque y MAX_PARALLEL=5; la retención completa de checkpoints y la salida CH4 siguen configuradas. Los SHA-256 de los cinco restart/checkpoint.lpj coinciden con el último CHECKPOINT_SAVED de cada controller.log: 00000_07999, año 1561, 88f680589b802dd42ca806fb59eaa8c23ed4f84ed0cc2543fc11e8481c29c60f; 08000_15999, año 1489, 6479e6dcb8e3f6e122557a70cbbe04f5f13c3c7dd2c80eabff64dd2c7cabef7d; 16000_23999, año 1487, 753623983d436f2b20b476ef8fedf9c7c6ca60a4ca1ddd1f8a84928393bd8d80; 24000_31999, año 1481, 70174d7e6bfb430dd691f87529472571949b7215e4099043cf1ee53adbd454ae; 32000_39999, año 1481, 56929c418b142ba637156110295a9c531f9e3a0b7bf5c1d48adb204127fdd792. Los cinco modelos mantienen alrededor de 40% de CPU cada uno. free -h informa 10 GiB disponibles, pero la swap de 8 GiB está completamente ocupada; VmSwap suma aproximadamente 7,8 GiB en tres procesos y es casi nula en los otros dos. vmstat 1 4 mostró salida de swap de 365 KiB/s en el primer intervalo y cero swap-in/out en los tres siguientes, sin intercambio sostenido durante la muestra. Quedan 506 GiB libres en el filesystem. Esto señala presión de memoria que conviene vigilar; con CPU activa y sin paginación sostenida observada, mantengo MAX_PARALLEL=5 y no cambio ni detengo procesos. Los stderr recientes revisados no muestran fallos fatales; el exit 137 de 00000_07999 es el incidente histórico del 2026-10-01. No hay códigos finales ni productos aceptados. La interpretación conserva river_routing=false y reservoir=false, por lo que el routing de esta campaña sigue siendo local.
**FR-Genghis, seguimiento 2026-10-03 11:33 COT:** se verificaron dos checkpoints nuevos. `00000_07999` avanzó hasta después de la fila anual 1561, SHA-256 `88f680589b802dd42ca806fb59eaa8c23ed4f84ed0cc2543fc11e8481c29c60f`; `08000_15999` avanzó después de la fila 1489, SHA-256 `6479e6dcb8e3f6e122557a70cbbe04f5f13c3c7dd2c80eabff64dd2c7cabef7d`. En ambos casos el restart activo y el archivo de checkpoint registrado por `controller.log` tienen el mismo SHA-256. `lpjcheck -pedantic` terminó con código 0 para cada configuración y reportó reanudación desde los años 1562 y 1490, respectivamente. Los cinco bloques siguen activos, un rank MPI por bloque, `MAX_PARALLEL=5`, retención completa de checkpoints; no hay códigos finales ni productos aceptados. Los checkpoints sin cambio son `16000_23999` año 1487, SHA-256 `753623983d436f2b20b476ef8fedf9c7c6ca60a4ca1ddd1f8a84928393bd8d80`; `24000_31999` año 1481, `70174d7e6bfb430dd691f87529472571949b7215e4099043cf1ee53adbd454ae`; y `32000_39999` año 1481, `56929c418b142ba637156110295a9c531f9e3a0b7bf5c1d48adb204127fdd792` (ya validado, reanudación desde 1482). Los procesos consumen cerca de 40% CPU cada uno; RAM disponible 11 GiB, swap usada 6.0 de 8 GiB y 506 GiB libres en el filesystem. `vmstat` mostró swap-in/out nulo en las muestras posteriores al primer intervalo, sin intercambio sostenido. Los segmentos activos no muestran errores fatales; las advertencias observadas son conocidas. El exit 137 en el stderr de `00000_07999` sigue siendo histórico del 2026-10-01, anterior a esta generación. Se conserva `MAX_PARALLEL=5`; routing local desactivado (`river_routing=false`, `reservoir=false`) limita la interpretación.
**FR-Genghis, seguimiento 2026-10-03 10:45 COT:** `32000_39999` guardó su primer checkpoint tras la fila anual 1481, SHA-256 `56929c418b142ba637156110295a9c531f9e3a0b7bf5c1d48adb204127fdd792`; el archivo activo y el archivo archivado indicado por `controller.log` coinciden byte a byte. La comprobación correcta `lpjcheck -pedantic` sobre `checkpoint_config.json`, con `inpath`, `outpath` y `restartpath` de este bloque, terminó con código 0 e indicó reanudación desde el año 1482; el supervisor inició un nuevo segmento. Los cinco bloques continúan activos, con un rank MPI por bloque y `MAX_PARALLEL=5`; no hay códigos finales ni productos aceptados. Checkpoints vigentes: `00000_07999` año 1560, SHA-256 `1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212`; `08000_15999` año 1488, `836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1`; `16000_23999` año 1487, `753623983d436f2b20b476ef8fedf9c7c6ca60a4ca1ddd1f8a84928393bd8d80`; `24000_31999` año 1481, `70174d7e6bfb430dd691f87529472571949b7215e4099043cf1ee53adbd454ae`; `32000_39999` año 1481, hash indicado arriba. La salida CH4 aparece en la configuración comprobada. Los cinco LPJmL usan cerca de 40% CPU cada uno. RAM disponible 11 GiB, swap ocupada 6.5 de 8 GiB y 509 GiB libres en el filesystem; `vmstat` mostró un primer intercambio de salida pequeño y luego cero swap-in/out en las muestras siguientes, sin intercambio sostenido. Los segmentos activos muestran progreso/arranque y advertencias conocidas, sin error fatal actual; el traceback con exit 137 en `00000_07999` pertenece al 2026-10-01 y es anterior a la reanudación vigente. Mantengo el límite de cinco procesos y las limitaciones interpretativas `river_routing=false` y `reservoir=false`.
**FR-Genghis, seguimiento 2026-10-03 09:32 COT:** 24000_31999 guardó checkpoint después de la fila anual 1481; SHA-256 70174d7e6bfb430dd691f87529472571949b7215e4099043cf1ee53adbd454ae. El SHA-256 del restart coincide con controller/archive; lpjcheck terminó con exit 0 e informó que el restart continúa desde 1482. El supervisor inició un nuevo segmento para el mismo bloque, que sigue activo. Permanecen activos los cinco bloques, MAX_PARALLEL=5 y un rank MPI por bloque; no hay códigos finales ni productos aceptados. Checkpoints vigentes: 00000_07999 año 1560, SHA-256 1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212; 08000_15999 año 1488, 836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1; 16000_23999 año 1487, 753623983d436f2b20b476ef8fedf9c7c6ca60a4ca1ddd1f8a84928393bd8d80; 24000_31999 año 1481, hash indicado arriba; 32000_39999 aún sin checkpoint guardado. Los últimos años anuales visibles siguen en 1561, 1489, 1487, 1481 y 1481. Hay 7.5 GiB de RAM disponible, 3.2 GiB de swap usada y 511 GiB libres en /home; vmstat no indica intercambio sostenido. Segmentos activos revisados sin errores fatales. Mantengo MAX_PARALLEL=5 y river_routing=false/reservoir=false como limitaciones de interpretación.

**FR-Genghis, seguimiento 2026-10-03 08:32 COT:** se guardó un nuevo checkpoint para 16000_23999 tras la fila anual 1487; SHA-256 753623983d436f2b20b476ef8fedf9c7c6ca60a4ca1ddd1f8a84928393bd8d80. El hash del restart activo coincide con el de controller/archive, y lpjcheck terminó con exit 0; informó reinicio desde el checkpoint en año 1488. El supervisor relanzó normalmente el mismo bloque con un nuevo segmento; siguen cinco bloques activos, MAX_PARALLEL=5, un rank MPI cada uno, sin códigos finales ni productos aceptados. Los otros checkpoints no cambian: 00000_07999 año 1560, SHA-256 1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212; 08000_15999 año 1488, 836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1. 24000_31999 y 32000_39999 siguen sin checkpoint guardado. Las últimas filas visibles son 1561, 1489, 1487, 1481 y 1481; los otros bloques mantienen actividad de CPU aunque sus filas anuales no avanzaron desde la última revisión. RAM disponible 8.0 GiB, swap usada 4.2 GiB de 8 GiB, disco libre 514 GiB; vmstat mostró swap-in/out nulos en las dos muestras instantáneas, sin intercambio sostenido. El segmento nuevo de 16000_23999 y los stderr revisados no muestran errores fatales. Mantengo el límite en cinco y la cautela interpretativa river_routing=false/reservoir=false.

**FR-Genghis, seguimiento 2026-10-03 07:32 COT:** los cinco bloques continúan activos con un rank MPI por bloque y MAX_PARALLEL=5. Los tiempos de CPU de los cinco LPJmL avanzaron unos 23 min durante los 58 min entre muestreos (cerca de 41% por proceso), aunque las últimas filas anuales siguen en 1561, 1489, 1487, 1481 y 1481; los stdout no cambian desde aproximadamente 01:57–04:43 COT según el bloque. No aparecieron checkpoints nuevos. Los últimos checkpoints, sin cambios y con SHA-256 verificado contra el restart, son 00000_07999 año 1560 (1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212), 08000_15999 año 1488 (836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1) y 16000_23999 año 1486 (7f3b065e67ed12d4ec1703faf068cb07d16667a83879fa04cde7b35e6d19077e); 24000_31999 y 32000_39999 siguen sin checkpoint guardado desde A0. No hay códigos finales ni productos aceptados. Quedan 7.3 GiB de RAM disponible, swap usada 3.8 GiB de 8 GiB y 515 GiB libres en /home; vmstat mostró swap-in/out nulos en las dos muestras instantáneas tras la primera, sin señal de intercambio sostenido. Los stderr activos no reportan errores fatales; el exit 137 histórico de 00000_07999 corresponde al 2026-10-01. Mantengo MAX_PARALLEL=5 por prudencia y river_routing=false/reservoir=false como limitaciones de interpretación.

**FR-Genghis, seguimiento 2026-10-03 05:29 COT:** los cinco bloques continúan activos con MAX_PARALLEL=5 y un rank MPI por bloque. Las filas más recientes observadas son: 00000_07999 año 1561, 08000_15999 1489, 16000_23999 1487, 24000_31999 y 32000_39999 1481. Los checkpoints siguen en los años 1560, 1488 y 1486, con SHA-256 1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212, 836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1 y 7f3b065e67ed12d4ec1703faf068cb07d16667a83879fa04cde7b35e6d19077e; aún no hay checkpoint de esta generación para los otros dos bloques, códigos finales ni productos aceptados. Cada LPJmL consume cerca de 40.9% de CPU; quedan 3.7 GiB de RAM disponible, 7 MiB de swap usada y 515 GiB libres en /home. Los stderr recientes revisados muestran advertencias conocidas, sin error fatal actual; el exit 137 de 00000_07999 pertenece a una generación anterior (2026-10-01). Mantengo el máximo en cinco por la reserva de RAM inferior a 4 GiB. river_routing=false y reservoir=false limitan la interpretación al routing local sin ríos ni reservorios.

**FR-Genghis, seguimiento 2026-10-03 00:29 COT:** los cinco bloques de la generación iniciada a las 21:55 COT continúan activos; cada LPJmL usa cerca del 40% de CPU y entre 4.6 y 5.7 GiB de RSS. La RAM disponible bajó de 5.2 GiB a las 23:29 COT a 4.3 GiB; a las 22:23 COT había 8.3 GiB disponibles. La swap usada es 6.5 MiB y quedan 515 GiB libres en `/home`. Aún no hay checkpoints nuevos desde el relanzamiento; `24000_31999` y `32000_39999` siguen sin uno de esta generación. Los stdout no muestran todavía la fila anual parseable que activa el checkpoint del wrapper; según [checkpoint_runner.py](../Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction/checkpoint_runner.py#L109), el SIGTERM de guardado espera esa fila además del intervalo de 3600 s. Los cinco LPJmL mantienen actividad de CPU y los stderr activos no muestran errores fatales, así que la ausencia de checkpoint aún no indica una interrupción. Mantengo `MAX_PARALLEL=5` y no lo aumento; observar la RAM en los siguientes ciclos. Sin códigos finales ni productos aceptados. `river_routing=false` y `reservoir=false` limitan la interpretación al routing local desactivado.

**FR-Genghis, seguimiento 2026-10-02 22:09 COT:** los cinco bloques permanecen activos; cada LPJmL usa aproximadamente 39–40% de CPU y 4.4–4.8 GiB de RSS. Quedan 8.4 GiB de RAM, swap sin uso y 515 GiB libres en /home. El consumo subió desde el arranque, así que mantengo MAX_PARALLEL=5 sin ampliarlo durante esta generación. Los stdout nuevos aún están en inicio; stderr contiene advertencias conocidas y no aparecen errores, fallos fatales, procesos muertos ni errores de segmentación. Los mensajes muestran el año 1489 tras retomar 08000 desde 1488 y 1481 en 24000 iniciado desde A0. Aún no hay códigos de salida ni checkpoints nuevos; el rendimiento total no está cuantificado.
**FR-Genghis reanudado con cinco bloques — 2026-10-02 21:56 COT:** tras el reinicio del PC/WSL, se confirmó que no había workers y se retiró el directorio de bloqueo vacío. Por instrucción del usuario, la campaña volvió a correr a las 21:55:35 con bloques de 8.000 celdas, `MAX_PARALLEL=5`, un rank MPI por bloque, CH4 y retención completa (`MAX_ARCHIVED_CHECKPOINTS=0`). Los bloques `00000_07999`, `08000_15999` y `16000_23999` reanudan desde años 1560, 1488 y 1486; sus reinicios coinciden byte a byte con el archivo y `lpjcheck -pedantic` devolvió exit 0. SHA-256: `1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212`, `836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1` y `7f3b065e67ed12d4ec1703faf068cb07d16667a83879fa04cde7b35e6d19077e`. `24000_31999` y `32000_39999` arrancan desde A0. Hay cinco pares LPJmL/`mpirun -np 1` activos. A las 21:56:37 había 29 GiB disponibles, swap sin uso y 515 GiB libres en `/home`; la muestra corresponde al arranque. No hay códigos finales ni productos aceptados y la ganancia de rendimiento todavía no se mide. `river_routing=false` y `reservoir=false` limitan la interpretación al routing local desactivado. Informe: [bitácora de paralelismo](lpjml_capacity_chunk_parallelism_2026-10-01.md).
> **FR-Genghis interrumpido — revisión 2026-10-02 21:14 COT:** el reinicio con bloques de 8.000 celdas, `MAX_PARALLEL=4`, `MPI_RANKS=1`, CH4 y retención completa (`MAX_ARCHIVED_CHECKPOINTS=0`) quedó sin workers. `ps` confirmó procesos activos a las 20:11 COT y ausencia de `LPJmL`, `mpirun`, `checkpoint_runner` y launcher a las 21:13 y 21:14; los logs de la generación actual no crecieron después de las 19:53. `campaign_status.txt` aún dice RUNNING y está desactualizado. Checkpoints íntegros revalidados con hash, comparación restart/archivo (`cmp` exit 0) y `lpjcheck -pedantic` (exit 0): `00000_07999`, año 1560, `1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212`; `08000_15999`, año 1488, `836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1`; `16000_23999`, año 1486, `7f3b065e67ed12d4ec1703faf068cb07d16667a83879fa04cde7b35e6d19077e`. `24000_31999` inició desde A0 y no tiene checkpoint guardado. No hay exit codes finales ni productos aceptados; los segmentos nuevos no registraron filas anuales. No aparecen eventos OOM en `dmesg`/`journalctl` disponibles, por lo que la causa de la interrupción no está determinada. A la revisión había 30 GiB disponibles, swap 0 y 516 GiB libres. La campaña queda detenida; no se inicia otra copia automáticamente. `river_routing=false` y `reservoir=false` limitan la interpretación al routing local desactivado. Véase [bitácora de paralelismo](lpjml_capacity_chunk_parallelism_2026-10-01.md).

> **Decisión vigente A1-1 h (2026-10-02):** la realización independiente
> (seed `2125532119`, tag `_O2_fixedBlack1bar_noxtol_MPI6_NOISE2`) es ahora el
> producto A1-1 h oficial de la serie focal A1/A3 × {1, 10, 100 h}. La primera
> realización (seed `368516754`) queda preservada como sensibilidad. La
> elección se tomó tras inspeccionar ambos posteriores (post hoc); no es una
> selección ciega. El atlas se regeneró con esta versión:
> [PNG](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima.png).
> La matriz A0--A3 × {10 h, 240 h} se preserva intacta como archivo legacy; el
> índice revisado de 1 h es independiente.

> **Registro previo a la promoción, 2026-10-01 23:48 COT:** la realización
> independiente A1-1 h terminó con exit 0 y productos finitos. Las métricas
> comparativas siguen en [la bitácora](life_proxima_a1_1h_independent_noise_repeat_2026-10-02.md);
> esta entrada refleja el análisis anterior a la decisión post hoc del día
> siguiente.

> **Estado operativo Stage III, actualizado 2026-10-04:** retrievals POSEIDON
> oficiales A1/A3 a 1, 10 y 100 h están cerrados y validados. A1-1 h usa ahora
> seed `2125532119` (`χ²_red=1.10`, 16 dof; 7.334 muestras); seed `368516754`
> se conserva como sensibilidad. Los dos runs de 1 h
> registran `[retrieval_exit] 0`; sus productos se recuperaron del scratch
> preservado después de un fallo de ruta del wrapper. Muestras, espectros,
> perfiles P--T/log-X, resúmenes y archivos MultiNest pasaron comprobaciones
> estructurales y de finitud. El atlas oficial 1/10/100 h muestra H2O, CO2,
> CH4, O3, N2O y NH3, además de P--T; O2 sigue recuperado pero su columna se
> omite. La página exportada ocupa el ancho de dos columnas (~7.28 in): A1 va
> en verde, A3 en rosa y la referencia efectiva se etiqueta simplemente A0.
> El valor logarítmico de A0 aparece una vez por especie; la línea A0 se repite
> en cada tiempo. Las marginales y los perfiles VULCAN de abundancia aparecen
> en las tres filas. P--T posterior/bandas 68/95% está por fila; la entrada
> VULCAN se limita a la primera y ahora va en negro discontinuo, dentro de la
> columna P--T. La leyenda global no repite información de P--T ni el marcador
> redundante del intervalo. Debajo de cada panel se leen `q50=...; z=...`;
> una ecuación única, limpia y sin recuadro define el z descriptivo relativo a
> A0 efectiva. `z` es condicional y no una significancia de detección. Se
> retiró el pie gris; χ²red/ln Z y las cautelas permanecen en el informe.
> Cada histograma es una densidad normalizada a área uno (dex⁻¹), pero el eje
> vertical se ajusta por panel; por tanto, las alturas no se comparan entre
> tiempos. Hay separadores entre filas y más espacio para los valores bajo los
> paneles. La V2 (límites dinámicos definidos por muestras y perfiles VULCAN,
> recortados al prior) queda promovida como figura oficial y es la salida del
> comando estándar. Se preserva V1 con el prior completo `[-12, -1]` y V3 con
> límites definidos solo por las posteriores. Ambas vistas dinámicas se
> restringen a `[-12, -1]`; V3 no usa perfiles para elegir sus límites. Las
> líneas grises discontinuas señalan bordes del prior cuando quedan dentro de
> la ventana. Las tres versiones se inspeccionaron. La
> selección de A1-1 h fue post hoc. El wrapper ya busca la ruta POSEIDON
> anidada. Matriz 8/8 intacta y legacy.
> Informe:
> [campaña oficial](life_proxima_a1_a3_1_10_100h_official_retrieval_campaign_2026-10-01.md),
> [V2 oficial PNG](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima.png) ·
> [V1 prior completo PNG](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima_full_prior_xlim.png) ·
> [V3 PNG](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima_posterior_xlim.png); las variantes V1/V3 quedan como productos de trabajo. La V2 oficial también está en [PDF](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima.pdf) y [SVG](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima.svg).
> **Metodología integral:** [informe reproducible 2026-10-03](life_proxima_a1_a3_1_10_100h_methodology_2026-10-03.md), con procedencia de SED/opacidades, cadena VULCAN–POSEIDON–LIFEsim, construcción de datasets, relación con LIFE X, discusión de priors, y figuras de emisión, S/N proyectado y posteriores/P–T.

> **Auditoría conjunta Proxima A1/A3--240 h completada el 2026-09-30 COT (legacy para la serie vigente):**
> ambos retrievals MPI6 cerraron con `exit_code=0`; MultiNest y los productos
> cosechados pasaron validación de integridad y finitud. `χ²_red=9.55` (A1) y
> `11.20` (A3), 16 dof. A3 da una posterior estrecha de N2O, pero queda 2.39
> `σ68` por debajo de su referencia de entrada; el ajuste, el PT y el preflight
> A3 (0.3901σ RMS, 1.247σ máximo) impiden reclamar detección o separación
> robusta A3/A0. NH3 sigue amplia. Dataset y matriz canónica 8/8 intactos.
> Informe: [auditoría A1/A3--240 h](life_proxima_a1_a3_240h_o2_fixed_surface_audit_2026-09-29.md);
> figura comparativa por tiempo (10/100/240 h), enfocada en N2O y NH3, con
> perfiles verticales VULCAN A1/A3, barras asimétricas q16–q84 alrededor de la mediana, referencia A0
> efectiva, distancias z firmadas, P–T, y χ²red/ln Z por ajuste. Su cuadrícula,
> leyenda y recuadros siguen `plot_profiles_posteriors()` del atlas original:
> [PNG](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A1_A3_10_100_240h_audit_molecular_profiles_PT_proxima.png).
> Esta figura 10/100/240 h queda como registro histórico; la figura oficial
> 1/10/100 h ya se generó y revisó. La fila de 100 h usa
> datasets independientes (A1 seed `460512527`, A3 seed `129315834`).

> **Decisión de alcance inicial 2026-10-01 (A1-1 h revisado 2026-10-02):** la serie oficial de retrievals LIFE para el
> contraste es A1 y A3 a **1, 10 y 100 h**, con el mismo modelo, espacio de
> priors y configuración POSEIDON. Los resultados de 240 h y el resto de
> retrievals pasan a **legacy** para esta pregunta; se preservan sin borrarlos.
> La matriz/datasets amplios A0–A3 × {10 h, 240 h} continúan intactos como
> archivo de referencia, no como la comparación oficial actual. Los nuevos
> datasets de 1 h están en un índice separado y no alteran el índice canónico
> 8/8. Se generan desde la señal forward y `sigma(1 h)=sigma(10 h)*sqrt(10)`.
> La primera selección A1/A3 usó semillas `368516754`/`1376328125`; tras la
> comparación de realizaciones, A1-1 h seed `2125532119` es la entrada oficial
> vigente y seed `368516754` queda como sensibilidad (decisión post hoc).
> `χ²_red` vigente a 1 h es 1.10/1.66 (A1/A3, 16 dof). Se corrigió la ruta
> de cosecha y la figura oficial 1/10/100 h ya está disponible. Logs, scratch,
> métricas y configuración: [campaña oficial A1/A3]
> (life_proxima_a1_a3_1_10_100h_official_retrieval_campaign_2026-10-01.md).

> **Auditoría POSEIDON A1 LIFE cerrada 2026-09-29 COT:** los retrievals MPI6R1
> reanudados desde checkpoint para 10 h y 100 h terminaron con `exit_code=0`;
> posterior, espectro, P--T, log-X y archivos MultiNest pasaron validaciones de
> finitud e integridad. Resultados: `χ²_red=1.55` y `3.18` (16 dof),
> `log_N2O=−9.522` y `−7.127` a 10/100 h; `log_NH3=−10.080` y `−10.662`.
> El posterior de N2O se estrecha a 100 h, pero el experimento no distingue
> formalmente A1 de A0 y el ajuste/PT muestran desajuste. La auditoría queda
> fuera de la matriz canónica 8/8; sus datasets y checkpoints MPI6 originales
> siguen intactos. Informe, figura y datos reproducibles:
> [auditoría A1](life_proxima_a1_10_100h_o2_fixed_surface_audit_2026-09-29.md),
> [figura PNG](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A1_10_100h_MPI6R1_posteriors_PT_proxima.png),
> [resumen JSON](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/retrieval_A1_10_100h_MPI6R1_posteriors_PT_proxima_summary.json).

> **FR-Genghis, revisión 2026-10-02 14:36 COT:** continúan activos los tres bloques CH4 (`MAX_PARALLEL=3`, un rank MPI por bloque, retención completa). Las últimas filas visibles son 1560, 1488 y 1485; los SHA-256 de los checkpoints activos son `1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212`, `836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1` y `7f3b065e67ed12d4ec1703faf068cb07d16667a83879fa04cde7b35e6d19077e`. El tercer bloque guardó un checkpoint nuevo aproximadamente a las 14:29 COT y ya lo cargó el segmento actual. No hay registros anuales nuevos desde 12:34 en los dos primeros bloques; los tres procesos siguen usando CPU. Hay 14 GiB disponibles, 95 MiB de swap usados y 517 GiB libres, sin presión inmediata. Sin códigos finales ni productos aceptados; los stderr recientes muestran advertencias y el `exit 137` de 00000 es histórico. Continúan `river_routing=false` y `reservoir=false`, que limitan la interpretación al routing local desactivado.

> **FR-Genghis, revisión 2026-10-02 13:38 COT:** los tres bloques CH4 siguen activos con `MAX_PARALLEL=3`, un rank MPI por bloque y retención completa. Las últimas filas visibles siguen en 1560 (`00000_07999`), 1488 (`08000_15999`) y 1485 (`16000_23999`); los checkpoints activos tienen SHA-256 `1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212`, `836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1` y `e9d67152cc7770b7a53e11440effa12ed699d984969f1d53967c0199a0ae14ce`. No hay filas anuales nuevas desde la revisión de 12:34 COT, pero los tres procesos LPJmL siguen activos y sus contadores de CPU aumentaron en una muestra de cinco segundos (62.4--67.3 % de CPU). Hay 15 GiB disponibles, 575 MiB de swap usados y 518 GiB libres; esto no indica presión inmediata de memoria. Los `run_status.txt` siguen sin códigos de salida, los stderr recientes solo muestran advertencias y no hay productos aceptados. El `exit 137` de `00000_07999` permanece como evento histórico del 1 de octubre, 01:45 COT. Se mantienen `river_routing=false` y `reservoir=false`, que limitan la interpretación al routing local desactivado.

> **FR-Genghis: primer checkpoint del tercer bloque verificado 2026-10-02 01:27 COT:**
> los tres bloques continúan activos. `00000_07999` llegó al año 1557 y conserva
> el checkpoint íntegro de 1556 (`f150c32b9c5ebdbe9202cf15dc18785d35d0c4efa20575f301ba2db9541c2080`);
> `08000_15999` llegó a 1485 y conserva el de 1484
> (`7d687ce9dfc6fe08478f181152cce943f9095f19b37d7e583833e939574f4e85`).
> `16000_23999` guardó checkpoint de año 1482, SHA-256
> `de713797e50d9ccf0b3b9a67eb89746035f3eb9f36f436377364c1745757f857`;
> `lpjcheck -pedantic` terminó con código 0 y confirmó ese año. Los logs
> muestran el guardado seguro y la continuación desde el checkpoint. No hay
> códigos de salida finales ni resultado científico aceptado. Una muestra de
> `ps` encontró los tres LPJmL activos; RAM disponible 14 GiB, swap usada
> 1.5 MiB y 523 GiB libres en disco. Se conserva la configuración CH4,
> `MAX_PARALLEL=3`, un rank MPI por bloque, retención completa y la limitación
> `river_routing=false`/`reservoir=false`.

> **FR-Genghis reanudado y ampliado 2026-10-01 18:51 COT:** WSL se reinició
> entre revisiones; a las 18:38 no quedaban procesos, el indicador superior
> `POTENTIAL_CHUNKS_RUNNING` estaba obsoleto y los logs no crecían. Se
> verificaron los dos reinicios y sus SHA-256 antes de reanudar. Por petición
> del usuario, desde las 18:49 corre con tres bloques simultáneos, un rank MPI
> por bloque, CH4 y retención completa (`MAX_PARALLEL=3`, `MPI_RANKS=1`,
> `MAX_ARCHIVED_CHECKPOINTS=0`). `00000_07999` retomó desde año 1556
> (`f150c32b9c5ebdbe9202cf15dc18785d35d0c4efa20575f301ba2db9541c2080`);
> `08000_15999` retomó desde año 1484
> (`7d687ce9dfc6fe08478f181152cce943f9095f19b37d7e583833e939574f4e85`);
> `16000_23999` comenzó desde el reinicio
> A0 y aún no tiene checkpoint. `lpjcheck` aceptó los dos estados reanudados.
> En la primera lectura había 25 GiB disponibles, cero swap y 525 GiB libres;
> la carga alcanzó tres ranks y todavía no se mide el aumento de rendimiento.
> No hay salida científica aceptada. Informe operativo:
> [`paralelismo de bloques`](lpjml_capacity_chunk_parallelism_2026-10-01.md).
> **Revisión 2026-10-01 19:08 COT:** siguen activos los tres procesos; una
> muestra instantánea registró 80 %, 68 % y 52 % de CPU y 4.2--4.7 GiB de RSS;
> quedan 17 GiB disponibles,
> sin swap usado y 525 GiB libres. Los hashes de los reinicios de los bloques
> 00000 y 08000 siguen coincidiendo. Los logs de la nueva generación aún no
> reportan año simulado nuevo y 16000 todavía no tiene checkpoint; la actividad
> de CPU continúa. No se ha medido aún una tasa de avance ni se acepta salida.

> **FR-Genghis reanudado 2026-09-22 20:48 America/Bogota:** se confirmó que
> el lanzador anterior ya no tenía procesos activos. El bloque `00000_07999`
> dejó el checkpoint `1790108667908124560.lpj`; su SHA-256
> (`80c0a282b424c4f5f6b9faae3eca2b8f2c69e40f4fa9fe4a2ee43fe39e71f52a`)
> coincide con `restart/checkpoint.lpj`. La corrida se reanudó desde ese estado
> con un rank MPI y salidas de CH4. La primera comprobación encontró LPJmL
> activo, cerca de 99 % CPU y 4.3 GiB RSS, sin uso de swap; el bloque sigue
> incompleto y aún no es un resultado científico.

> **A0 validado 2026-09-22:** el control natural `a0_natural` terminó con
> `exit_code=0`, cubrió 1996--2005 y pasó la validación de 67 420 celdas,
> máscaras, unidades y finitud. El control preservó el checkpoint tras una
> interrupción externa de WSL y se integró con el mismo convenio de A1. A0
> produce `1.334471e9` moléculas `cm-2 s-1` de N2O y `2.964787e9` de NH3 como
> medias 1996--2005; el contraste A0/A1 está en
> `lpjml_global_a0_control_validation_2026-09-22.md`. Sigue pendiente decidir
> la calibración del déficit de NH3 antes de acoplar la fotoquímica.

> **Control natural A0 reanudado 2026-09-21 00:30 UTC:** el primer lanzamiento
> llegó al año 1587 y dejó el checkpoint íntegro
> `4c6dfe69fd019922380ab6196ba52572365734b44219f2d3db64298387149b7c`.
> WSL perdió los procesos sin mensaje de error de LPJmL; no se interpretó como
> finalización. El control se reanudó desde `a0_natural/restart/checkpoint.lpj`
> con ocho ranks y quedó activo de forma independiente. Véase
> `lpjml_global_a0_control_progress_2026-09-21.md`.

> **Cierre y validación 2026-09-20 America/Bogota:** la campaña global A1
> `global_a1_checkpoints_20260909` terminó con `exit_code=0` el 2026-09-20
> 16:40:38 UTC. La validación de 67 420 celdas, diez años (1996--2005),
> máscaras, unidades, finitud y checkpoint SHA-256 pasó; el analizador global
> generó los flujos medios de N2O y NH3. Son emisiones agrícolas de stand, no
> todavía una diferencia causal A1−A0: falta el control natural emparejado.
> Véase [el informe de validación](lpjml_global_a1_validation_2026-09-20.md).

> **Reanudación autorizada 2026-09-19 04:53 America/Bogota:** A1 global se reanudó desde el checkpoint íntegro del año 1738; ocho ranks del build `LPJmL-6.0.6-balance-fix-20260912` están activos y el spin-up natural se omitió por estar completado. La ejecución repetirá 1739–1742 y continuará hasta 2005. Productos y comparación siguen pendientes.

> **Interrupción verificada 2026-09-19 04:20 America/Bogota:** A1 sin procesos MPI en dos consultas; último año completo 1742, log detenido desde 2026-09-15 01:28. Indicador a1_RUNNING desactualizado. Checkpoint activo año 1738 (2.8 GiB), SHA256 recalculado coincide con el registrado: 08122825cc13ccf1168f652658c6cdd7721f57c16f44ab9b485de315457af3e3. Hay 23 generaciones. Spin-up natural completado conservado. Seguimiento pausado; no se relanzó. Próximo: confirmar causa de interrupción y reanudar A1 desde 1739 con autorización. Flujos y comparación pendientes.

> **Cambio de fase verificado 2026-09-14 02:08 America/Bogota:** spin-up completado a las 00:33 con exit_code=0; reinicio final 940 MiB y SHA256 de origen/copia A1 verificados idénticos. A1 activa automáticamente desde 00:33, año simulado 1498, ocho ranks y primer checkpoint año 1492 guardado 01:35 (2.4 GiB). WARNING013 de normalización de uso de suelo pendiente de evaluación global antes de aceptar flujos. Seguimiento horario activo; productos 1996–2005 y comparación pendientes.

> **Reanudación validada 2026-09-12 14:38 America/Bogota:** campaña global_a1_checkpoints_20260909 activa con ocho ranks y build LPJmL-6.0.6-balance-fix-20260912. Prueba global separada años -2 a 5 PASS: balances activos, trayectoria previa idéntica a precisión del log, checkpoint íntegro. Campaña retoma su checkpoint original año -3; checkpoints y seguimiento horarios activos. A1 sigue automáticamente tras spin-up. Informe: docs/lpjml_balance_checkpoint_fix_2026-09-12.md. Entradas previas son historial.

> **Recuperación autorizada 2026-09-12:** build separado LPJmL-6.0.6-balance-fix-20260912 compilado; prueba global corta balance_recovery_20260912 en ejecución desde copia del checkpoint año -3. Se conserva fail_on_balance=true. Campaña original detenida hasta validación; después se seleccionará el build corregido y se reanudará desde el checkpoint original. Véase docs/lpjml_balance_checkpoint_fix_2026-09-12.md. Seguimiento horario todavía pausado.

> **Incidente verificado 2026-09-12 03:49 America/Bogota:** global_a1_checkpoints_20260909 permanece FAILED, sin procesos MPI y sin crecimiento del log desde 2026-09-11 01:34. Último año completo 2; ERROR004 de balance de carbono en año 3, celdas 50566 y 58993. Checkpoint activo de 01:27 conserva SHA256 d4b276cd3f65732a50e1d818dca0681935d2debf0d3abbce727fcf2d430117d5. Hay 35 generaciones según último inventario. Seguimiento pausado; no se relanzó. Próximo: diagnosticar balance y validar recuperación antes de continuar. A1/comparación pendientes; estimación temporal anterior suspendida.

> **Reanudación 2026-09-09 20:43 America/Bogota:** usuario confirma apagado del PC como causa de la interrupción y autoriza continuar. Checkpoint activo verificado por SHA256; lpjcheck confirma año -1578 y ocho procesos LPJmL activos. Campaña global_a1_checkpoints_20260909 reanudada desde ese estado para continuar en -1577; checkpoints horarios y seguimiento activos. A1 seguirá tras spin-up. Notas anteriores conservadas como historial.

> **Incidente 2026-09-09 15:57 America/Bogota:** global_a1_checkpoints_20260909 interrumpida; dos consultas sin procesos y WSL recién iniciado. Último log -1562 a las 15:15:41. Checkpoint de las 15:00 al año -1578 íntegro: SHA256 recalculado del activo y copia archivada coincide con 3dcda941501b5240d8d1a1eadeb1b6a136db8897a27a0b98d3f39be756048b93. Recuperación disponible desde -1577; 16 años de avance posterior no guardados. Causa del cierre pendiente. No se relanzó; seguimiento pausado. A1 y comparación pendientes.

> **Estado actual 2026-09-09 07:49 America/Bogota:** nueva campaña `global_a1_checkpoints_20260909` lanzada en E:, ocho ranks MPI activos. Spin-up desde cero, seguido automáticamente por A1; checkpoints horarios con copias archivadas y SHA256. Recuperación A1 probada: 13 NetCDF idénticos al piloto continuo. Seguimiento horario activo. Detalles y rutas en [checkpoints](../docs/lpjml_checkpoints_2026-09-09.md). Las notas de interrupción siguientes corresponden a la campaña anterior.
> **2026-09-09 — checkpoints:** controlador periódico implementado y recuperación MPI probada en ocho celdas: guardado al año -389, continuación -388–1700 con salida cero; 2089 años de diagnósticos coinciden con el piloto continuo a la precisión del log. Campaña global sigue detenida; falta integrar el controlador en su lanzador y validar recuperación A1/NetCDF. Véase [informe de checkpoints](../docs/lpjml_checkpoints_2026-09-09.md).
> **Incidente 2026-09-09 02:00 America/Bogota:** campaña `global_a1_20260907` interrumpida. Dos comprobaciones confirman ausencia de procesos LPJmL/mpirun; WSL indica menos de un minuto de actividad. Última salida: año -231, modificada a las 01:29:08. `campaign_status.txt` conserva SPINUP_RUNNING obsoleto y run_status solo el inicio; carpeta spinup_natural/restart vacía. Causa del cierre sin determinar. No se relanzó. A1, validación y comparación pendientes; seguimiento pausado hasta decidir recuperación.

# Reanudar ExoFarm: punto de entrada operativo

**Actualización operativa 2026-09-07:** en este PC, Ubuntu reside físicamente en
E: (`Riqueza`). El dataset oficial quedó descargado, verificado y extraído a las
16:37 locales en `/home/dasan/lpjml-data/public_standard`
y LPJmL con Open MPI ya compiló y pasó `make test` en `/home/dasan/exofarm-lpjml-runtime`.
Readiness y prueba MPI de ocho celdas/dos ranks aprobadas; reinicio, diez años
de NetCDF y ocho pruebas de cálculo verificados. Véase la
[validación MPI](lpjml_mpi_smoke_validation_2026-09-07.md).
La campaña global `global_a1_20260907` arrancó a las 17:37 locales: 67,420
celdas y ocho ranks MPI, spin-up activo y paso automático a A1 tras éxito.
El siguiente paso es seguir procesos/logs y validar los productos antes de
comparar con el incremento A1−A0 prescrito. Véase el
[registro de campaña](lpjml_global_a1_campaign_2026-09-07.md).

**Última actualización estructural:** 2026-10-13
**Uso:** leer este documento al iniciar una tarea nueva o un chat nuevo en este
repositorio. Resume el estado recuperable, la próxima acción autorizada y los
documentos que contienen el detalle. No sustituye la verificación en vivo de
procesos, entornos, archivos ni `git status`.

## Lectura mínima, en este orden

1. [`../AGENTS.md`](../AGENTS.md): reglas científicas, de seguridad, rutas y
   requisitos de verificación.
2. Este documento: alcance activo y siguiente paso.
3. [`project_status_tracker.md`](project_status_tracker.md): backlog, decisiones
   y estado por etapa.
4. El README de la etapa afectada y, si se va a ejecutar software, su documento
   de entorno correspondiente.

Los informes fechados en `docs/` son evidencia y contexto; no se deben usar
aisladamente como estado operativo actual. Ante discrepancia, comprobar los
archivos/outputs en vivo y actualizar el tracker y este documento.

## Estado recuperable en un minuto

**Cierre y auditoría 2026-10-17:** las tres restricciones A0 del relanzamiento
fresco A3–1000 h terminaron con exit0. Se preservó el intento interrumpido del
15-oct y no se reutilizaron checkpoints. La auditoría independiente pasó para
posterior/prior, espectro, P–T, `log_X`, MultiNest, datos/operador y hashes;
las evidencias son concordantes entre `stats.dat`, resumen nested y resultados.
ln B (completo corregido menos A0 fija): N₂O `626.5061±0.3845`, NH₃
`−0.9927±0.3825` (sigma N/A), conjunta `626.0635±0.3822`. La finitud estricta
no pasa por seis NaN exclusivos de desviaciones derivadas para coordenadas
fijas; sidecars centrados dan exactamente cero y los originales quedaron
intactos. Estado `VALIDATED_PRIMARY_PRODUCTS_REQUIRES_REVIEW`, aceptación
`PENDING_FIXED_MOMENT_REVIEW`; hace falta decidir explícitamente si se acepta
esta salvedad. El completo conserva `χ²_red=14.29`, limitando la fuerza de la
interpretación. No hay nuevas corridas autorizadas. [Informe, tabla y
validación](life_proxima_a3_1000h_a0_fixed_binning_corrected_audit_2026-10-17.md).

**Nueva autorización 2026-10-15 — tres referencias A0 A3–1000 h corregidas:**
lanzar N₂O fija, NH₃ fija y ambas fijas con MPI5 cada una, hasta tres
simultáneas/15 ranks y monitor cada 90 minutos. Se reutiliza el completo
corregido existente y su dataset; se exige preflight MPI5 del callback,
priors/opacidades idénticos salvo las restricciones, y gate de memoria PSS.
Campaña `a0_fixed_reference_A3_1000h_binning_corrected_20261015`; los productos
antiguos quedan preservados. Las exposiciones 1/10/100 h quedan aplazadas.
La fuente operativa es `campaign_state.json`/`manifest.csv` de la nueva campaña.
**Interrupción 2026-10-16 11:44UTC (06:44COT):** el supervisor816, tres
mpiexec1083/1130/1177 y quince workers ya no aparecen en Ubuntu. El inspector
de solo lectura devuelve `JSONDecodeError: Expecting value: line 1 column 1
(char 0)`; `campaign_state.json` (16386 bytes) y `manifest.csv` (1790 bytes)
son completamente NUL, mtime10:10:30UTC. Últimos logs: N₂O41400/704371,
NH₃38550/700838, conjunta37550/693688 reemplazos/muestras; sin firma fatal,
pero sin exit ni cierre. Los ocho artefactos MultiNest por variante siguen en
scratch. Estado de campaña indeterminado/interrumpido; no restaurar JSON, no
reiniciar/reanudar, conservar todo y esperar decisión explícita. Causa exacta
de la pérdida del supervisor no registrada. [Incidente y evidencias](life_proxima_a3_1000h_a0_binning_corrected_2026-10-15.md).
Seguimiento 2026-10-16 09:49UTC (16oct04:49COT): `RUNNING`, aceptación
PENDING; supervisor816, MPI5 1083/1130/1177 y quince workers OMP1 vivos.
N₂O/NH₃/conjunta: 41000/38000/37050 reemplazos y686281/681683/673688
evaluaciones; desde08:14UTC avanzaron2150/3000/2450 reemplazos y
85200/84865/84691 evaluaciones. CPU creció en quince ranks; ocho archivos
MultiNest/caso, cinco registros de operador por log y sin patrones fatales.
Dataset SHA `5611c5904ef03aa02586bed15f14c0c2560ac5ae6fa9463ef420229311db75fa`,
operador SHA `ba17b7056eb094bd210aca23aacd6aa9dbdcfabdf65352d641faf93c20252731`;
callback real y tres registros preflight PASS. Dimensiones libres13/13/12;
RAM23.44GiB disponible, PSS19≈6.999GiB, swap0. No hay productos aceptados
ni ln Z interpretable; se conserva alcance y procesos, monitor90min.
Seguimiento 2026-10-16 08:14UTC (16oct03:14COT): `RUNNING`, supervisor816,
MPI5 1083/1130/1177, quince ranks OMP1. N₂O/NH₃/conjunta: reemplazos
38850/35000/34600, evaluaciones601081/596818/588997; desde06:48UTC
avanzaron2250/3400/2650 y77397/76938/78317. Quince contadores CPU avanzan;
ocho archivos MultiNest/caso, cinco bindings por log, cero patrones fatales.
Priors libres/tipos coinciden con el completo; dimensiones13/13/12 y valores
A0 correctos. Dataset SHA `5611c5904ef03aa02586bed15f14c0c2560ac5ae6fa9463ef420229311db75fa`,
operador SHA `ba17b7056eb094bd210aca23aacd6aa9dbdcfabdf65352d641faf93c20252731`,
callback y source-equivalence PASS. RAM disponible23.33GiB, PSS19≈7.131GiB,
swap0. Sin productos aceptados; ln Z provisional sin interpretar. Alcance y
procesos intactos; monitor90min.
Seguimiento 2026-10-16 06:48UTC (16oct01:48COT): `RUNNING`, supervisor816 y
MPI5 1083/1130/1177 con quince ranks activos OMP1. N₂O/NH₃/conjunta:
reemplazos36600/31600/31950, evaluaciones523684/519880/510680; del snapshot
05:22UTC avanzaron2450/3600/2300 y70207/67763/64301. Ocho archivos
MultiNest/caso, cinco bindings `[operator-active]` por log, cero patrones
fatales y CPU creciente en todos los ranks. Dataset SHA
`5611c5904ef03aa02586bed15f14c0c2560ac5ae6fa9463ef420229311db75fa`, operador
SHA `ba17b7056eb094bd210aca23aacd6aa9dbdcfabdf65352d641faf93c20252731`;
preflight/callback y comparación de priors libres PASS. RAM disponible
22.93GiB, PSS19procesos≈6.833GiB, swap0. Sin productos aceptados; ln Z
provisional sin interpretación. Alcance y procesos intactos; monitor90min.
Seguimiento 2026-10-16 05:22UTC (16oct00:22COT): `RUNNING`, supervisor816
y MPI5 1083/1130/1177 con quince ranks activos, OMP1. N₂O/NH₃/conjunta:
reemplazos34150/28000/29650 y evaluaciones453477/452117/446379; avances
desde03:54UTC de2750/2600/2750 reemplazos y59831/58358/58383 evaluaciones.
RAM24.41GiB disponible, PSS19procesos≈6.412GiB, swap0; ocho archivos
MultiNest/caso, binding5/5, sin patrones fatales. Dataset, operador, auditoría
de equivalencia y configuraciones conformes; dimensiones13/13/12, valores A0
y opacidades retenidas. Sin productos aceptados ni ln Z interpretable. Monitor
90min activo, sin cambios operativos.
Seguimiento 2026-10-16 03:54UTC (15oct22:54COT): `RUNNING`, supervisor816
y MPI5 1083/1130/1177 con quince workers activos, OMP1. N₂O/NH₃/conjunta:
reemplazos31400/25400/26900, evaluaciones393646/393759/387996; aumentos
desde02:31UTC de4150/2300/3250 reemplazos y66868/67944/64215 evaluaciones.
RAM disponible23.32GiB, PSS19procesos≈6.629GiB, swap0; ocho archivos
MultiNest/caso, binding5/5 y cero indicadores fatales. Manifiestos, hash del
dataset, hash del operador y gate de equivalencia PASS; dimensiones13/13/12,
abundancias fijas y opacidades conformes. Sin productos finales aceptados ni
interpretación de ln Z provisional. Monitor90min activo, sin cambios operativos.
Seguimiento 2026-10-16 02:31UTC (15oct21:31COT): `RUNNING`, supervisor816
verificado y tres MPI5 1083/1130/1177 con quince ranks y OMP1 activos.
N₂O/NH₃/conjunta: reemplazos27250/23100/23650 y evaluaciones
326778/325815/323781; todas las corridas avanzaron desde01:03UTC. RAM
disponible23.75GiB, PSS19procesos≈6.788GiB, swap0; cinco bindings del
operador y ocho archivos MultiNest por caso, cero indicadores fatales.
Manifiestos, hashes del dataset y dimensiones libres13/13/12 conformes;
valores A0 fijados y opacidades retenidas. Sin productos finales aceptados;
ln Z provisional no interpretado. Monitor90min activo, sin cambios operativos.
Seguimiento 2026-10-16 01:03UTC (15oct20:03COT): `RUNNING`, tres preflights MPI5 PASS en
`preflight_R1/`, supervisor PID816 y mpiexec1083/1130/1177 verificados;
quince ranks activos con un hilo cada uno. Reemplazos N₂O/NH₃/conjunta:
23600/21000/21400, evaluaciones268018/263805/265548 y CPU avanzando;
RAM disponible23.47GiB, PSS19procesos≈6.295GiB, swap0,49 hashes protegidos
y tres configuraciones resueltas PASS; sin errores fatales. Monitor
`seguimiento-a3-1000-h-a0-binning-corregido` ACTIVE cada90min. El gate inicial
se preservó antes del muestreo: cambios documentales del operador probados
por reconstrucción SHA exacta y AST equivalente en `source_equivalence/`.
[Procedimiento y cierre pendiente](life_proxima_a3_1000h_a0_binning_corrected_2026-10-15.md).

**Prioridad vigente 2026-10-15 — completo A3–1000 h con binning coherente:**
el retrieval autorizado terminó con `exit_code=0`, productos archivados y
comparación anterior/corregido guardada. El estado fuente sigue
`COMPLETE_PENDING_VALIDATION` / `PENDING_INDEPENDENT_REVIEW`; al cierre de
ese completo no quedaron sus procesos Python/MPI. El ajuste mejoró de χ²
542,64 a 242,88 (17 dof), pero
χ² reducido 14,29 aún indica tensión importante. `Δln Z=148,6876±0,3835`
entre operadores cuantifica sensibilidad numérica y no debe leerse como ln B
molecular. NH₃ cambia +1,357 dex en mediana con posterior ancha; N₂O +0,051 dex.
La figura se inspeccionó; la aceptación científica formal queda pendiente.
No comparar contra A0 antiguos, pues usaron el operador anterior. Se conserva
la configuración, los seis oficiales, los 36 LOO y la matriz legacy 8/8. La
autorización posterior de las tres referencias A0 figura arriba.
[Informe, comparación, figuras y límites](life_proxima_a3_1000h_binning_corrected_2026-10-14.md).
El operador nuevo integra fotones con bordes de canal de punto medio
verdaderos; la likelihood previa reconstruía bordes simétricos desde
centro±semiancho. Ya se usó dentro del callback de POSEIDON para este A3–1000 h.
Su wrapper sigue congelado al dataset/hash de esta corrida; no se ha cambiado
el runner general ni se ha actualizado A0. Para reutilizarlo fuera de este caso
hace falta preflight específico y, para evidencia A3/A0, una pareja homogénea.

**Registro previo — continuación P–T:** control de capacidad espectral con seis
coordenadas Madhu y química vertical/geometría fijas completado en directorio
separado `A3_PT_spectral_capacity_20261014`. Ajusta solo al Fp verdadero
sin ruido, con pesosσ1000 h existentes; dos arranques y presupuesto finito.
No inicia retrievals, evidencia, posteriores ni cambios de ruido.
Interpolación térmica100–400 K con nodos originales retenidos y cierre
exigido; cobertura diagnóstica limitada explícitamente. Exit0,161 forwards,
trece hashes y auditoría PASS, figura revisada. Menor Q41.0199, RMS1.1503
vecesσ; ventanaNH₃ RMS0.06118 %/máximo0.9216 vecesσ, residual16.64 μm
−4.164 vecesσ. Paradas xtol con gradientes altos y soluciones distintas:
no se demostró óptimo ni incapacidad global Madhu. Código instalado usa
opacidades del nodo T_fine más próximo (paso10 K); siguiente control por
decidir es resolución térmica, sin cambiar aún familiaPT o campaña.
Esta ejecución supersede «todavía sin ejecutar» más abajo.
[Resultado, figura y límites](life_proxima_a3_pt_spectral_capacity_2026-10-14.md).

**Alcance vigente 2026-10-14 — binning y P–T, ruido excluido:** el usuario
autoriza organizar los dos controles diagnósticos y descarta la vía de
ruido instrumental. Adaptador separado, sin editar POSEIDON/código oficial
ni datasets; doce pruebas PASS. Cierre sobre verdad guardada: máximo
relativo2.265×10⁻¹⁴ y χ²32.978 frente a314.519 del operador anterior.
Aproximación Madhu al T(P) verdadero con mismos priors, dos arranques
convergentes: RMS17.091 K; punto archivado1000 h RMS59.980 K sobre todas
las capas. Ninguno es ajuste espectral. Tres forwards P–T con química
VULCAN fija completados: RMS flujo8.437/10.137 % para aproximación térmica/
perfil archivado; menor error T no implica menor residual espectral.
Vector completo archivado reevaluado sin optimización: χ²542.643→365.856,
no es un nuevo mejor ajuste. Diecinueve hashes y auditoría independiente
PASS, figura inspeccionada. Cero nuevos retrievals; cuatro anteriores
siguen pendientes de aceptación científica. La continuación superior ya
ejecutó la prueba espectral finita; todavía no se escogió otra familia
P–T ni se despachó una campaña nueva.
No reanudar checkpoints bajo una likelihood cambiada.
[Procedimiento y estado](life_proxima_a3_binning_pt_controls_2026-10-14.md).

**Registro previo — control híbrido y ruido LIFE 2026-10-14:** tres forwards nuevos con solo
N₂O, solo NH₃ y ambas constantes a sus promedios A3, resto VULCAN/P–T
intactos. RMS relativos0.07382/0.01664/0.07567 %, máximos por canal
0.477/0.872/0.871 veces σ1000 h. Contratos/finitud/siete hashes PASS y
figura revisada. El fuerte desajuste all-isochem involucra otras abundancias
y/o composición de fondo; no queda explicado por estas dos solas.
Literatura LIFE XII/II y Huber2025: presupuesto vigente fotónico optimista,
sin un piso universal transferible a Proxima. σ/F mediano1000 h=0.21297 %;
no se añade ruido. Cuatro retrievals1000 h ya cerrados exit0, incluida NH₃;
estados COMPLETE_PENDING_VALIDATION. Auditoría científica pendiente.
Primer control recomendado por autorizar: copia con generador/likelihood
coherentes, seguida de atribución química/PT y presupuesto de covarianza.
No fixes ni nuevas corridas en este turno.
[Método, figura y fuentes](life_proxima_a3_target_isochem_and_noise_budget_2026-10-14.md).

**Control tres espectros A3 completado 2026-10-14:** vertical regenerado
coincide con forward guardado y LIFE sin ruido (máximo relativo2.26×10⁻¹⁴
con operador común). Isochem con promedios A3, PT verdadero idéntico:
RMS22.28 %/máximo58.30 %, pero ventana9.5–11.5 μm máximo0.826 %.
La discrepancia de likelihood sigue separada (RMS1.90 %/máximo8.14 %).
Dos forwards, cero retrievals/optimización; hashes y contratos PASS, PNG/PDF
inspeccionados. No prueba imposibilidad de cualquier isochem ni acepta1000 h.
[Figura, valores constantes y límites](life_proxima_a3_vertical_life_isochem_comparison_2026-10-14.md).

**Diagnóstico vigente 2026-10-14 — contrato de binning LIFE/POSEIDON discrepante:**
control con el mismo espectro verdadero demuestra RMS2.926σ/máximo8.986σ
a 1000 h entre generador y likelihood. Principal componente: bordes de
puntos medios vs centro±semiancho; también energía vs fotones. Preflight
anterior no validaba operador de likelihood. χ² verdadero bajo generador
32.98; bajo likelihood314.52; mejor retrieval542.64. NH₃ baja ya antes de
reanudar, muestras válidas; PT/isochem causales por separar. Mantener
1000 h sin aceptación científica y advertir limitación en 100 h aceptado.
No se corrigió código oficial ni se relanzó. Próxima acción requiere autorizar
una copia diagnóstica con binning idéntico y controles, antes de nuevas corridas.
[Informe, código y evidencia](life_proxima_nh3_1000h_interface_diagnosis_2026-10-14.md).

**Figura descriptiva 2026-10-13:** ocho marginales completas A3 de N₂O/NH₃
en 1/10/100/1000 h frente a A0 generadas y revisadas. N₂O 1000 h: 5.963×,
95 % [5.545,6.403]; NH₃: 0.291×, [0.0104,7.935]. Productos 1000 h aún
pendientes de auditoría; no aceptar por esta visualización. Diferencia NH₃
100→1000 h pendiente diagnóstico, realizaciones/rejilla difieren.
[Figura, procedencia y límites](life_proxima_a3_posterior_enrichment_plot_2026-10-13.md).

**Registro histórico 2026-10-13 — tres A0 A3–1000 h reanudadas en MPI5:** el
usuario autorizó parar y redistribuir. Checkpoints 889636/882767/884613
evaluaciones, finitud/priors/fijos PASS; 24 archivos respaldados por hash.
Supervisor nuevo 5062, MPI5080/5090/5100, quince ranks activos en carga
inicial de opacidades. Lectura MultiNest y nuevos contadores pendientes.
Completo terminó exit 0, COMPLETE_PENDING_VALIDATION, productos intactos.
Fuentes centrales de la misma campaña; logs nuevos `recovery_20261013_MPI5_R1/`.
No usar logs/PID MPI3 históricos para progreso actual. No relanzar por automatismo.
[Procedimiento y respaldo](life_proxima_a3_1000h_mpi5_resume_2026-10-13.md).

**Ampliación vigente 2026-10-12 — cuatro modelos A3–1000 h:** el usuario
confirmó completo + N₂O fija a A0 + NH₃ fija a A0 + ambas fijas, en paralelo.
La restricción histórica a un único completo queda superada para estas tres
variantes. Completo MPI6 reanudado intacto; nuevas MPI3 cada una, presupuesto
global quince ranks en dieciséis CPU lógicas. Mismo dataset, realización de
ruido, priors no fijados, opacidades y rejilla nativa. Fuente nueva:
`retrievals/a0_fixed_reference_A3_1000h_20261012/`. Preflight 3/3 PASS,
RUNNING: supervisor 1139, MPI PID 1208/1238/1271, tres ranks por variante
en carga de opacidades. Completo MPI PID 805 intacto; quince ranks activos
en total, ~21 GiB disponibles y swap vacía en el control inicial.
El completo confirmó recuperación y avance a 2 693 510 evaluaciones.
No incluye A1, LOO ni otros tiempos/PT; auditoría y ln B emparejados pendientes.
[Alcance y procedimiento](life_proxima_a3_1000h_a0_comparison_2026-10-12.md).

**Recuperación autorizada 2026-10-12 — solo A3–1000 h:** interrupción confirmada
por ausencia de supervisor/MPI; último log 10:40:26 COT. Checkpoint validado
PASS: 800 puntos vivos finitos, priors/superficie correctos, 29 hashes intactos,
51 200 reemplazos y 2 646 212 evaluaciones. R1 **RUNNING desde 17:25:14 COT**,
supervisor 803, mpiexec 805, seis ranks 820–825 en carga inicial de opacidades;
respaldo íntegro, mismo dataset/configuración/basename/scratch y MPI6, usando
`--resume`. Estado vigente en `native_grid_retry/campaign_state.json` y
log nuevo en `native_grid_retry/recovery_20261012_R1/retrieval.log`.
No usar el `retrieval.log` anterior para inferir progreso después de R1.
[Informe de recuperación](life_proxima_a3_1000h_checkpoint_resume_2026-10-12.md).

**Historial de arranque 2026-10-11 — A3–1000 h:** un único retrieval completo,
extensión de A3 1/10/100 h, sin cambiar Madhu/isochem, priors, superficie,
O2 ni modelo de ruido. Dataset separado, N_live=800, MPI6 y preflight obligatorio.
Estado del intento corregido:
`retrievals/a3_1000h_full_20261011/native_grid_retry/campaign_state.json`.
Primer intento detenido en preflight: RMS 0.7963 σ, máximo 2.545 σ frente
al forward verdadero; cero ranks/retrievals lanzados. Dataset conservado;
diagnóstico con rejilla nativa 3–20 μm reproduce exactamente el forward
(RMS=máximo=0 σ). Intento corregido **RUNNING desde 19:42:38 UTC / 14:42:38 COT**:
preflight PASS, supervisor 818, mpiexec 921 y seis ranks 932–937 activos en
carga inicial de opacidades. Mismo R=10000, 31 canales, P–T y priors; no se
relaja el preflight. 29 hashes intactos y protección contra duplicados PASS.
Primer intento intacto; pendiente cierre del muestreo y auditoría científica.
[Alcance, ejecución y aceptación pendiente](life_proxima_a3_1000h_extension_2026-10-11.md).
Esta autorización histórica sustituye las propuestas de 30/50 días; la
ampliación del 2026-10-12 incorpora las tres restricciones A0 a 1000 h.
No incluye A1, LOO ni pruebas P–T adicionales. No duplicar el supervisor ni
reanudar por automatismo; al terminar, auditar antes de aceptar.

**Auditoría A0 2026-10-11:** tres corridas A3-100 h terminadas con exit 0;
supervisor/MPI inactivos. Productos primarios, evidencias, priors, valores
fijados y hashes PASS. Finitud estricta FAIL: `NaN` en desviaciones derivadas
de coordenadas fijas, en `stats/summary` de N₂O y conjunta. Auditoría
aceptada explícitamente por el usuario con salvedad
`ACCEPTED_WITH_FIXED_MOMENT_SALVEDAD`; originales conservados. Tabla final
ln B: `29.440 ± 0.340 / 1.170 ± 0.342 / 31.103 ± 0.336`; sigma calibrado
bilateral `7.96 / 2.12 / 8.17` (N₂O/NH₃/conjunta).
[Informe, tabla e incidencia exacta](life_proxima_a3_100h_a0_fixed_audit_2026-10-11.md).
Se preservó la auditoría anterior, se generaron siete momentos auxiliares
estables con dispersión cero y se verificaron 52 hashes científicos intactos
y 13 controles PASS. La finitud estricta sigue false; no se ocultó la incidencia.
[Síntesis completa de las capas, decisiones y conclusión ExoFarm/LIFE](life_proxima_exofarm_retrieval_layers_synthesis_2026-10-11.md).
Monitor eliminado tras verificar el cierre.

**Nuevo alcance autorizado 2026-10-10 — enriquecimiento LIFE respecto a A0:**
se calcularon las probabilidades marginales/conjuntas y los intervalos de
enriquecimiento de los seis modelos completos; referencia escalar A0
congelada. Informe:
[procedimiento A0](life_proxima_a0_enrichment_methodology_2026-10-10.md).
**El usuario seleccionó únicamente A3-100 h**, individual y conjunto:
tres retrievals (N₂O fija / NH₃ fija / ambas fijas). Lanzados a las
19:05 COT del 2026-10-10: supervisor PID 758; MPI6 individuales PID 779/783
con seis ranks cada uno; el conjunto esperaba una vacante en ese arranque.
Los tres terminaron; máximo dos MPI6 durante el muestreo.
Selección vigente y fuente de verdad:
`retrievals/a0_fixed_reference_20261010/{selected_scope.json,campaign_state.json,manifest.csv}`.
El plan de 18 candidatas se conserva como historial; las otras 15 están
fuera del alcance autorizado y no se ejecutarán. Log/PID del supervisor en
`retrievals/a0_fixed_reference_20261010.A3_100h.supervisor.{log,pid}`.
**Primera acción al reanudar:** usar la síntesis para redactar resultados
condicionados y revisar residuos/degeneraciones. La aceptación de momentos
fijos se resolvió con autorización explícita y hashes congelados. No relanzar
por automatismo, reabrir los 36 LOO ni ejecutar las otras 15 candidatas.
N₂O A3-100 h distingue la referencia escalar A0 en esta realización;
NH₃ tiene evidencia débil. La atribución agrícola, robustez de realizaciones
y rama instrumental siguen siendo preguntas abiertas. La nueva autorización
incluye ahora el completo y las tres restricciones A0 A3–1000 h descritas arriba.
Los tres prototipos A3-100 h pasaron el contrato setup-only (15 coordenadas
declaradas; 13/13/12 libres); tres controles unitarios y compilación aprobados.
`preflight_progress.json` registra los tres PASS. La auditoría completa y la
tabla final están en el informe de 2026-10-11 enlazado arriba.
El monitor `seguimiento-life-a0-a3-100h-3` fue eliminado tras verificar el
cierre documental; no queda una cola pendiente y no se reinicia automáticamente.

**Estado actualizado 2026-10-10:** la campaña LOO LIFE Proxima A1/A3 terminó:
36/36 ablaciones con `return_code=0`, 36/36 preflight `PASS`, 14 parámetros por
variante y ningún caso activo o pendiente. La validación independiente aceptó
los productos de las 36 corridas y las seis evidencias completas; confirmó que
cada modelo completo y sus ablaciones usan bytes idénticos del mismo dataset.
Supervisor/MPI no activos al cierre. Los seis retrievals completos y la matriz
8/8 permanecen intactos (`canonical_8of8_modified=false`). Informe, tabla
completa y figura: [comparación LOO](life_proxima_molecular_ablation_loo_2026-10-04.md);
el registro de auditoría, CSV, manifiesto y 36 archivos están en
[`molecule_ablation_loo_20261004`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/molecule_ablation_loo_20261004/README.md).
Validador reproducible: [`validate_proxima_molecular_ablation_loo.py`](../Thermal_Emission_Spectroscopy/scripts/validate_proxima_molecular_ablation_loo.py).
Por solicitud del usuario, la tabla de reporte vigente usa `ln B ± error numérico`
y sigma calibrado con la convención citada por Lin et al.: ecuaciones (8)–(9)
de Benneke & Seager, bilateral, `N/A` para `ln B ≤ 0`. Son 27 cifras calibradas
y nueve `N/A`; sin nuevas ejecuciones ni cambios de evidencia. Método,
CSV oficial y reproducción: [tabla y convención](life_proxima_loo_sigma_lin_convention_2026-10-10.md).

**Siguiente paso autorizado para la campaña LOO cerrada:** interpretar los contrastes condicionales junto
con los perfiles verticales, residuos y degeneraciones antes de redactar una
afirmación de detección. La campaña cubre una realización diagonal por dataset;
no hay aquí análisis de repetibilidad ni de covarianza instrumental. No volver
a lanzar las 36 celdas ni cambiar la matriz 8/8. La caída eléctrica y la
reanudación segura de dos checkpoints quedan documentadas como historial en el
informe y en el log
[`resume_20261010_power_recovery`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/molecule_ablation_loo_20261004.resume_20261010_power_recovery.log).

| Etapa | Estado | Regla de reanudación |
| --- | --- | --- |
| 0 — LPJmL | **A1 y A0 completados y validados 2026-09-22** | `global_a1_checkpoints_20260909`, 67,420 celdas/ocho ranks, Ubuntu sobre E:. A1 agrícola y A0 natural cubren 1996--2005 con `exit_code=0`, máscaras/unidades/finitud y conversiones auditadas. El N2O queda próximo al incremento congelado; NH3 queda por debajo y requiere decisión de calibración antes de la fotoquímica. |
| I — VULCAN Tierra--Sol | **Aceptada, benchmark pre-corrección de N2O** | Los cuatro A0--A3 tienen `end_case = 1`, pero A2/A3 proceden del conjunto guardado el 2026-06-15, anterior a la corrección actual de N2O. Sirven para validar la interfaz LIFE, no para presentar todavía la matriz vigente como resultado final. |
| I — VULCAN TRAPPIST-1e | **Aceptada con salvedad** | `end_case = 3` por química traza; conservar la salvedad en cualquier uso de esos productos. No usar esos perfiles para Proxima. |
| II — transmisión/JWST | **Campaña A0/A3 cerrada** | La matriz optimizada de 18 retrievals es la evidencia vigente. Los perfiles TRAPPIST actuales se regeneraron junto con los BC corregidos en `fb9812d`; no confundir esta campaña con la salvedad Tierra--Sol de Stage III ni reabrir una cola sin verificar outputs y procesos en vivo. |
V2 sigue como atlas oficial de la serie clásica 8/8; para los seis baselines LIFE con binning corregido, el atlas oficial vigente es la edición del 2026-10-28.

### Actualización de la métrica S/N de transmisión (2026-09-22)

El plot vigente integra las plantillas contrafactuales de `N2O` y `NH3` por
instrumento sobre las rejillas observadas de NIRSpec Prism y MIRI LRS. Las
ventanas de picos y su tabla se conservan como legacy/descomposición
secundaria; el diagnóstico usa ruido diagonal y no equivale a una detección.
La evidencia está en
[`trappist1e_molecular_snr_by_instrument_2026-09-22.md`](trappist1e_molecular_snr_by_instrument_2026-09-22.md)
y en `Transmission_Spectroscopy/final_products/`.

### Actualización de la métrica S/N de LIFE (2026-09-22)

Se generó un diagnóstico integrado sobre todos los bins de los productos
LIFEsim clásicos para Tierra--Sol y Proxima. Cada campaña tiene un único
instrumento: el panel superior contiene `N2O` y `NH3`, y el inferior proyecta
A3 con marcas para S/N=3 y S/N=5. La figura Proxima se promovió a
`Thermal_Emission_Spectroscopy/final_products/`; la figura anterior basada en
picos permanece como legacy. Véase
[`life_classic_snr_integrated_2026-09-22.md`](life_classic_snr_integrated_2026-09-22.md).

### Diagnóstico del escalado de ruido Proxima A1/A3 (2026-10-02)

Se calculó S/N molecular integrado para N2O y NH3 a 1/10/100 h usando el
producto directo LIFEsim de 10 h ya guardado. La sigma de los seis datasets
actuales coincide con sigma proporcional a t^-1/2 hasta 4.68e-7 (redondeo de
archivos dat), así que la raíz del tiempo está aplicada correctamente. En 31
bins, A3 N2O da S/N=1.89/5.97/18.86 y NH3 0.49/1.54/4.86; A1 N2O da
0.19/0.61/1.92 y NH3 0.04/0.12/0.37. Las llamadas directas previas de
LIFEsim 0.2.32 ya habían validado el escalado temporal; en esta auditoría no
se repitió la llamada porque lifesim no estaba disponible para importarse en
el entorno actual. Véase el [informe fechado](life_proxima_lifesim_snr_a1_a3_1_10_100h_2026-10-02.md),
el [script](../Thermal_Emission_Spectroscopy/scripts/diagnose_proxima_lifesim_molecular_snr_scaling.py)
y la [figura](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/audit/proxima_A1_A3_molecular_snr_direct_vs_scaled_1_10_100h.png).
Es S/N esperado de plantilla con ruido diagonal, no una detección; realizaciones
independientes cambian residuos y retrievals, no esta sigma nominal. Índice 8/8
sin cambios.

### Auditoría de retrievals Proxima A3 (2026-09-23)

Se repitieron A3 a 10 h y 240 h con N_live=800, abundancias isochem,
error_inflation=none, modo heredado `surface=False` con malla hasta 1 bar y
sin x_tol. Ambos
conjuntos de productos están completos y finitos. A 10 h el ajuste es
razonable (chi^2_red=1.43); a 240 h sube a 13.07, aunque el posterior de N2O
se estrecha a -6.39 (+0.04/-0.05). Esa precisión no es defendible como
detección con el desajuste observado. Son auditorías excluidas; el cierre
canónico 8/8 y sus cifras no cambian. Véase
[life_proxima_a3_10_240h_fixedp1bar_noxtol_audit_2026-09-23.md](life_proxima_a3_10_240h_fixedp1bar_noxtol_audit_2026-09-23.md).
La comparación visual canónica/auditoría de las posteriores moleculares está en
[`retrieval_A3_molecular_posteriors_audit_comparison_proxima.png`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A3_molecular_posteriors_audit_comparison_proxima.png)
y es solo un diagnóstico de auditoría.

### Auditoría Proxima A3 a 100 h (2026-09-23, completada)

La integración intermedia de 100 h se eligió a partir del S/N integrado porque
la plantilla de NH3 se acerca a S/N=5 en ese tiempo; N2O cruza ese umbral mucho
antes. El dataset de 31 bins usa `sigma(t)=sigma(10 h)*sqrt(10 h/t)` y una
realización (`seed=129315834`; SHA-256
`78662546181A5B74391A14B7B73AE80D879200A74DB6A4BC5338E3CE7EEE4705`). El
retrieval `N_live=800`, `isochem`, sin inflación, `surface=False` y sin
`x_tol` terminó con `ln Z=877.05±0.24`, `chi²_red=5.27` (18 dof),
`log_N2O=-6.485` y `log_NH3=-8.395`. Las distancias firmadas respecto de A0
efectiva son `z=+4.69` y `+3.04`; se reportan como diagnósticos descriptivos,
no detecciones, dado el desajuste aún visible. Se generó y revisó el atlas
10/100/240 h con perfiles VULCAN, posteriores y métricas; la matriz canónica
8/8 permanece intacta. Véase el
[informe de auditoría](life_proxima_a3_100h_fixedp1bar_noxtol_audit_2026-09-23.md)
y [figura](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A3_audit_profiles_posteriors_10_100_240h_proxima.png).

**Diagnóstico de residuos 2026-09-23:** los espectros medianos de A3 dejan
`chi²=114.31` a 100 h y `238.86` a 240 h en los 31 bins, frente a `94.89`
y `235.24` de los mejores ajustes POSEIDON. Los residuos importantes se repiten
en 6.8--7.1 y 12--14 µm; 88.9 % y 80.0 % del `chi²` de la mediana queda fuera
de las ventanas moleculares estrechas marcadas. El espectro A3 verdadero menos
la mediana recuperada tiene correlación 0.974 entre ambos tiempos; por ahora
no se atribuye el patrón a una sola especie ni a `isochem`. Véase
[el informe y la figura](life_proxima_a3_retrieval_residuals_2026-09-23.md).

**Diagnóstico de interfaz 2026-09-23:** el forward A3 incluye O2 y una
superficie negra explícita a 1 bar; los retrievals de auditoría omiten O2 y
usan `surface=False`. Con perfiles verdaderos, desactivar solamente la
superficie produce una distancia cuadrática de `293.31` (100 h) / `703.95`
(240 h) en 31 bins; el modelo de seis especies sin superficie produce
`218.30` / `523.93` por cancelación parcial. Son distancias frente al
forward sin ruido, no chi² de ajuste. La etiqueta histórica
`_fixedP1bar_noxtol` no describe una superficie fija real; el modo de
ejecución quedó documentado como legado sin alterar productos.
[Informe, tabla y figura](life_proxima_a3_forward_swap_audit_2026-09-23.md).
**Retrieval corregido A3--100 h (cerrado 2026-09-26):** `X_profile=isochem`,
O2 añadido, superficie POSEIDON explícita fijada mediante `log_P_surf=0`,
sin inflación ni `x_tol`, `N_live=800`, `R=10000`. La validación del forward
con perfiles verdaderos dio RMS `0.2518 sigma` y máximo `0.8048 sigma` en 31
bins. MultiNest terminó con 1,804,581 evaluaciones y `ln Z=884.33±0.24`; la
excepción del proceso original ocurrió después, cuando Analyzer esperaba
`post_equal_weights.dat` y MultiNest había escrito la muestra sin extensión.
Se recuperó el posprocesamiento desde esa muestra y se validaron los productos
sin volver a muestrear: 7,479 × 15 muestras posteriores, espectro 3,219 × 6,
P--T 100 × 6 y log-X de ocho especies. Resultado: `chi²_red=4.94` (16 dof),
`R_p_ref=1.2202±0.0062 R_⊕`, `log_N2O=-6.1476`, `log_NH3=-8.2578` y
`log_O2=-3.3095`. Los z descriptivos frente a A0 efectiva son `+13.24` y
`+5.63`; el ajuste sigue tensionado, así que no equivalen a una detección.
La comparación legacy/corregida, residuos, manifiesto y límites están en el
[informe de auditoría](life_proxima_a3_100h_o2_fixed_surface_audit_2026-09-23.md)
y la [figura revisada](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A3_100h_legacy_vs_o2_fixed_surface_recovery_proxima.png).
El monitor programado se canceló tras verificar el cierre.

**Auditoría corregida A3--10 h cerrada (2026-09-28, fuera de 8/8):** se lanzó la corrida
emparejada con el caso corregido de 100 h: O2, superficie negra fija a 1 bar,
`R=10000`, `N_live=800`, `isochem`, sin `x_tol` ni inflación. La validación
previa pasó en los 31 bins con RMS `0.07963 sigma` y máximo `0.2545 sigma`.
PID Ubuntu `30640`; log y configuración en
[`proxima_A3_10h_O2_fixedBlack1bar_noxtol.launch.log`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/proxima_A3_10h_O2_fixedBlack1bar_noxtol.launch.log).
No pertenece a la matriz canónica 8/8. MultiNest terminó con `ln Z=890.9665±0.2085`
tras 1,201,886 evaluaciones. El wrapper salió con código 1 después: Analyzer
buscó `post_equal_weights.dat`, pero la muestra estaba guardada con terminación
`.d`. Se comprobó su SHA-256, se preservó el original y se creó una copia `.dat`
byte por byte idéntica; el postproceso terminó sin repetir el muestreo. Se
validaron 6,972 × 15 muestras finitas, espectro recuperado, P--T y log-X de ocho
especies. El ajuste es `chi²_red=1.28` (16 dof), `R_p_ref=1.2269 R_⊕`,
`log_N2O=-6.0598`, `log_NH3=-8.6841`, `log_O2=-3.1956`. Frente a A0 efectiva,
`z_N2O=+5.59` y `z_NH3=+0.85` son distancias descriptivas condicionadas al
modelo y a esta realización. En la comparación con 100 h bajo la interfaz
emparejada, sigma68 de N2O pasa de 0.147 a 0.056 dex; NH3 a 10 h sigue amplia
(sigma68 1.49 dex), mientras el ajuste de 100 h da `chi²_red=4.94`. Son datos
de ruido diagonal con realizaciones independientes: los `ln Z` no se comparan
como factores de Bayes y los z no constituyen detecciones formales. La causa
del sufijo truncado quedó localizada en la concatenación duplicada de nombres
en POSEIDON y el runner ya fue corregido para nuevos lanzamientos. Figura y
tablas reproducibles: `retrieval_A3_10_vs_100h_o2_fixed_surface_proxima` en
`Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/{plots,tables}/`.
Véase el [informe con los productos y límites](life_proxima_a3_10h_o2_fixed_surface_audit_2026-09-27.md).
La comparación explícita del perfil térmico recuperado con el PT VULCAN de
entrada refuerza la cautela: RMS de `T_mediana−T_VULCAN` de 32.71 K a 10 h y
60.36 K a 100 h. La anchura mediana de las bandas marginales 68% baja de
43.40 K a 20.61 K; VULCAN queda dentro de las bandas punto-a-punto de 2σ en
54.6% y 9.3% de niveles comunes, respectivamente. Es un chequeo descriptivo,
no una región creíble conjunta. Figura y
método: `retrieval_A3_recovered_PT_10_vs_100h_proxima` bajo los directorios
`plots/` y `tables/` de la campaña.

### Historial operativo de la auditoría corregida Proxima A1 a 10/100 h

Se preparó una comparación A1 con O2, superficie negra explícita a 1 bar,
`R=10000`, `N_live=800`, química `isochem`, sin inflación ni `x_tol`. El
dataset canónico A1--10 h se conserva; el dataset de auditoría A1--100 h se
generó con sigma escalada y semilla `460512527`. Ambos pasaron `--setup-only`
con 31 bins y 15 parámetros. A petición del usuario se detuvieron las dos
corridas seriales previas y se eliminaron sus muestras parciales/logs/PID,
preservando los inputs. Se relanzaron con MPICH: seis ranks por run (12 de 16
CPUs), tags `_O2_fixedBlack1bar_noxtol_MPI6`; PIDs `mpiexec` `41224` (10 h) y
`41269` (100 h). Ambos llegaron a muestreo activo con seis ranks, pero cerraron
anómalamente al intentar MultiNest abrir `proxima_A1_{10h,100h}_...-phys_live.points`:
`Fortran runtime error: Cannot open file ...: Invalid argument` en
`nested.F90:2391`; los lanzadores informaron `exit_code=9` tras señal 9. Al
cierre, 10 h registraba 310,975 muestras y `ln Z=860.162459`; 100 h,
228,866 muestras y `ln Z=492.624776`. Son valores provisionales de runs
interrumpidos, no resultados recuperados ni evidencia comparable entre datasets.
Los archivos crudos de MultiNest y los logs quedaron preservados; las salidas
`post_equal_weights.dat` solo tenían 2 líneas (10 h) y 1 línea (100 h), y no se
encontraron espectros, PT ni log-X finales con el tag MPI6. No se reinicia nada
automáticamente. La matriz 8/8 y ambos datasets permanecen intactos.
El monitor heartbeat
`monitor-proxima-life-a1-retrievals` identificó la falla; véase el informe
operativo enlazado abajo.
Véase el [informe operativo](life_proxima_a1_10_100h_o2_fixed_surface_audit_2026-09-29.md).

## Cierre de auditoría A1 (2026-09-29)

### Recuperación MPI6R1 completada

Ambos runs reanudados desde checkpoints terminaron con `exit_code=0`. Se
validaron ocho archivos crudos de MultiNest, 6,567/6,774 muestras posteriores,
espectros, perfiles P--T, log-X y finitud. `χ²_red=1.55` a 10 h y `3.18` a
100 h (16 dof); `log_N2O` mediano pasa de `−9.522` a `−7.127`, con contracción
marcada de su incertidumbre a 100 h. Aun así, las referencias efectivas A0/A1
son próximas, NH3 permanece amplio y el PT recuperado difiere del perfil
VULCAN. La conclusión se limita a esta configuración, ruido diagonal y
realizaciones concretas: no hay detección formal ni comparación de `ln Z`
como factor de Bayes entre datasets distintos. El experimento no altera la
matriz 8/8. Informe, código, figura y tabla están en
[el informe de auditoría](life_proxima_a1_10_100h_o2_fixed_surface_audit_2026-09-29.md).

No queda pendiente recuperar estos runs. Esta nota cierra aquellos productos
legacy y queda superada como instrucción de alcance por la campaña LOO
autorizada el 2026-10-04, que compara modelos con/sin especie sobre cada
dataset oficial emparejado. Cualquier nueva campaña fuera de ese alcance requiere
definir explícitamente la comparación científica —por ejemplo, modelos A0/A1
sobre un mismo dataset con parámetros nuisance marginalizados— y abordar
múltiples realizaciones/covarianza instrumental; no duplicar estos retrievals
por defecto.

### Etapa 0 — primera prueba Franck 2011 + N2O/NH3

La prueba acotada quedó aceptada el 2026-09-06. El checkout oficial está fijado
en LPJmL `v6.0.6`, commit
`5af44a1ed023279a23c28d6dfe76945b97aaac57`; la compilación serial pasó, el
paquete estándar fue verificado y extraído, y `pilot_20260907T031220Z` completó
el spin-up, A1 con ciclo de N y la rama de rendimiento potencial. Los NetCDF
1996--2005 tienen dimensiones/unidades plausibles y valores finitos. La
campaña global ya validó los productos 1996--2005 y los flujos agrícolas
integrados. El control natural `a0_natural` terminó y quedó validado; sus
resultados y el contraste por especie están en
[`lpjml_global_a0_control_validation_2026-09-22.md`](lpjml_global_a0_control_validation_2026-09-22.md).
La estrategia quedó fijada en el [runbook para el
otro PC](lpjml_global_a1_mpi_other_pc_runbook.md). La celda piloto no produce
un flujo planetario interpretable. Véanse también el
[informe de aceptación](lpjml_franck2011_first_pilot_2026-09-06.md) y
[`../Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction/README.md`](../Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction/README.md).

**Ruta inmediata después de la validación A0/A1:**

1. Generar como postproceso la sensibilidad de desnitrificación incompleta,
   conservando masa de N por celda y año: `N2O_N = n2o_nit_agr +
   n2o_denit_agr + epsilon*n2_agr` y `N2_N = (1-epsilon)*n2_agr`, con
   `epsilon = 0` como LPJmL sin modificar y `epsilon = 1` como límite superior.
2. Fijar el tratamiento de NH3: conservar la rama cruda de LPJmL y documentar
   aparte cualquier calibración al objetivo congelado; no escalarla de forma
   silenciosa.
3. Congelar el manifiesto de lower-boundary fluxes A0--A3 en `TgN/año` y
   `molecules cm-2 s-1`, con el número de átomos de N, el área planetaria y la
   procedencia de cada componente.
4. Solo después regenerar o aceptar los perfiles fotoquímicos Tierra--Sol con
   esos flujos. Los perfiles A2/A3 de junio de 2026 quedan como benchmark de
   interfaz hasta que se aplique esta decisión.

En paralelo, el usuario priorizó `FR-genghis-khan-crop-only`: toda la tierra
elegible se asignará al cultivo anual ganador, sin pasture, ganado ni manure.
El piloto methane-enabled y el contrato CLM del mapa pasaron. La campaña global
de candidatos está activa con cuatro bloques simultáneos, un rank MPI por
bloque, CH4 y checkpoints íntegros en
`/home/dasan/exofarm-lpjml-runs/fr_genghis_potential_20260922_chunks_ch4`, con
bloques de 8.000 celdas, checkpoints y salidas de cosecha más CH4. Los
intentos monolíticos con salidas completas terminaron por memoria
(`exit 137`) y quedaron preservados; la primera prueba local con routing global
dio `ERROR142` y también se conserva. Cuando termine, se construirá el mapa
mundial, se ejecutará `lpjcheck` y se lanzará `run_capacity_genghis_chunks.sh`,
que repetirá el spin-up con `with_methane=true` y evaluará la rama crop-only por
bloques. `FR-save-forests` queda como segunda rama. Ambas se mantendrán
separadas de A1/A2 y de VULCAN hasta cerrar el manifiesto y el alcance/calibración
de NH3. El diseño ejecutable está en
[`lpjml_franck_capacity_scenarios_design_2026-09-22.md`](lpjml_franck_capacity_scenarios_design_2026-09-22.md).

**Actualización 2026-10-01 18:51 COT:** tras confirmar que WSL había reiniciado,
que no quedaban procesos y que el bloqueo global estaba vacío, el usuario
autorizó reanudar desde los checkpoints verificados y elevar el paralelismo.
El planificador está activo con `MAX_PARALLEL=3`, `MPI_RANKS=1`, bloques de
8.000 celdas y salidas CH4. `lpjcheck` aceptó el checkpoint de
`00000_07999` en año 1556 (SHA-256
`f150c32b9c5ebdbe9202cf15dc18785d35d0c4efa20575f301ba2db9541c2080`) y el de
`08000_15999` en año 1484 (SHA-256
`7d687ce9dfc6fe08478f181152cce943f9095f19b37d7e583833e939574f4e85`).
`16000_23999` comenzó desde A0. La primera
lectura registró 25 GiB disponibles, cero swap y 525 GiB libres; el coste de
tres ranks aún no tiene una ventana suficiente para medir velocidad. Se
preservan todas las generaciones (`MAX_ARCHIVED_CHECKPOINTS=0`); aún no se
acepta ningún producto científico. Véase
[`lpjml_capacity_chunk_parallelism_2026-10-01.md`](lpjml_capacity_chunk_parallelism_2026-10-01.md).

**Seguimiento 2026-10-02 01:27 COT:** `00000_07999` y `08000_15999`
registran los años 1557 y 1485; sus checkpoints reanudables de 1556 y 1484
mantienen los SHA-256 indicados arriba. `16000_23999` ya guardó el año 1482
(`de713797e50d9ccf0b3b9a67eb89746035f3eb9f36f436377364c1745757f857`),
aceptado por `lpjcheck -pedantic` (`exit=0`). Los tres LPJmL siguen activos y
los logs muestran trabajo en curso; hay 14 GiB RAM disponibles, 1.5 MiB de
swap usados y 523 GiB libres. No se ha cerrado ningún bloque ni se acepta aún
salida científica. El tercer bloque continúa desde su checkpoint; se preserva
la configuración y la limitación de routing local.

**Seguimiento 2026-10-02 04:30 COT:** los reinicios activos de
`00000_07999` y `08000_15999` avanzaron a los años 1558 y 1486;
`lpjcheck -pedantic` aceptó ambos (`exit=0`). Sus SHA-256 son
`4c1beab2ecf40db4e78cfbdd8a4ed5843bc9f0ba39031d37d2a9e88cdca07030` y
`66d13bb13237714af53246b13840d21177ad7b5c252dbb7c6527eda02a6b1578`,
respectivamente. `16000_23999` registró el año 1483 y conserva el checkpoint
de 1482, SHA-256
`de713797e50d9ccf0b3b9a67eb89746035f3eb9f36f436377364c1745757f857`.
Los tres LPJmL siguen activos y sus contadores de CPU avanzaron en una muestra
de cinco segundos; no hay código de salida ni producto aceptado. Hay 16 GiB
disponibles, 1.5 MiB de swap usados y 521 GiB libres. Las advertencias de los
stderr recientes no son fatales; el `exit 137` de `00000_07999` sigue siendo
histórico, previo a la reanudación autorizada del 1 de octubre a las 18:49 COT.
Se mantienen `MAX_PARALLEL=3`, un rank por bloque, CH4, retención completa y
`river_routing=false`/`reservoir=false`.

**Seguimiento 2026-10-02 08:30 COT:** `00000_07999` registra el año 1559 y
conserva el checkpoint íntegro de 1558 (`4c1beab2ecf40db4e78cfbdd8a4ed5843bc9f0ba39031d37d2a9e88cdca07030`);
`08000_15999` registra el año 1487 y conserva el checkpoint de 1486
(`66d13bb13237714af53246b13840d21177ad7b5c252dbb7c6527eda02a6b1578`).
`16000_23999` guardó y pasó `lpjcheck -pedantic` (`exit=0`) con checkpoint
de 1484, SHA-256
`e9d67152cc7770b7a53e11440effa12ed699d984969f1d53967c0199a0ae14ce`.
Los tres procesos continúan activos y sus contadores de CPU avanzaron; hay
14.7 GiB disponibles, 1.5 MiB de swap usados y 520 GiB libres. No hay códigos
finales ni productos aceptados. Las advertencias actuales no son fatales; el
`exit 137` del controller de 00000 sigue siendo histórico y anterior a la
reanudación del 1 de octubre a las 18:49 COT. Se mantienen CH4, tres bloques,
un rank por bloque, retención completa y routing local desactivado.

**Seguimiento 2026-10-02 10:32 COT:** la campaña sigue en ejecución. No han
cambiado las filas de año ni los checkpoints desde la lectura de 08:30 COT:
`00000_07999` permanece en fila 1559/checkpoint 1558
(`4c1beab2ecf40db4e78cfbdd8a4ed5843bc9f0ba39031d37d2a9e88cdca07030`),
`08000_15999` en fila 1487/checkpoint 1486
(`66d13bb13237714af53246b13840d21177ad7b5c252dbb7c6527eda02a6b1578`) y
`16000_23999` conserva el checkpoint 1484
(`e9d67152cc7770b7a53e11440effa12ed699d984969f1d53967c0199a0ae14ce`),
desde el que arrancó el segmento más reciente sin imprimir otro año. Los tres
LPJmL siguen consumiendo CPU (61.5--68.9 % por proceso en la muestra); hay
14 GiB disponibles, 1.5 MiB de swap usados y 520 GiB libres. Los stderr
recientes solo contienen advertencias; el `exit 137` de 00000 sigue fechado
antes de la reanudación actual. No hay códigos de salida ni productos
aceptados. Sigue `MAX_PARALLEL=3`, CH4, un rank por bloque, retención completa
y `river_routing=false`/`reservoir=false`.

**Seguimiento 2026-10-02 11:33 COT:** el último segmento de
`16000_23999` avanzó hasta la fila 1485; su checkpoint íntegro sigue en 1484
(`e9d67152cc7770b7a53e11440effa12ed699d984969f1d53967c0199a0ae14ce`).
`00000_07999` y `08000_15999` no avanzaron desde la lectura previa: filas
1559/1487 y checkpoints 1558/1486, con SHA-256
`4c1beab2ecf40db4e78cfbdd8a4ed5843bc9f0ba39031d37d2a9e88cdca07030` y
`66d13bb13237714af53246b13840d21177ad7b5c252dbb7c6527eda02a6b1578`.
Los tres procesos siguen activos y consumen CPU (60.7--69.1 %); RAM disponible
14 GiB, swap usada 1.5 MiB y disco libre 520 GiB. Los checkpoints se
recalcularon por SHA-256; el de 16000 conserva la aceptación previa de
`lpjcheck -pedantic` con código 0. No hay códigos finales ni productos
aceptados; los stderr recientes solo muestran advertencias. El `exit 137` de
00000 sigue siendo histórico. Se mantienen CH4, `MAX_PARALLEL=3`, retención
completa y routing/embalses locales desactivados.

**Seguimiento 2026-10-02 12:34 COT:** los logs de `00000_07999` y
`08000_15999` avanzaron hasta las filas 1560 y 1488; los checkpoints activos
guardados en esta revisión tienen SHA-256
`1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212`;
`836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1`,
respectivamente.
`16000_23999` permanece en fila 1485 con checkpoint 1484
(`e9d67152cc7770b7a53e11440effa12ed699d984969f1d53967c0199a0ae14ce`).
Los tres reinicios se recalcularon por SHA-256; los dos checkpoints nuevos
están registrados en `controller.log` como guardados seguros. Los tres
procesos están activos con CPU; hay 16 GiB disponibles, swap usada 1.5 MiB y
518 GiB libres. No hay códigos finales ni productos aceptados. Las
advertencias de stderr no son fatales; el `exit 137` de 00000 sigue siendo
histórico. Se mantienen CH4, `MAX_PARALLEL=3`, retención completa y routing
local/embalses desactivados.

### Rama clásica — cerrada y preservada

**Manuscrito actualizado 2026-10-16:** [integración bayesiana LIFE](life_manuscript_bayesian_integration_2026-10-16.md) guardada en `E:/Down/ExoFarms_Photochemistry_v2.tex` y su bibliografía. Incluye evidencia molecular, probabilidades ≥ A1, K nominales, intervalos y restricciones A0, con causas y limitaciones en Discusión. ≈0/≈100 % y rayas para factores sin cola resuelta. Compilación integrada falla antes y después por falta de `aastex701.cls`; resultado visual pendiente. No se lanzaron modelos. Siguiente paso editorial: habilitar la dependencia de compilación del mismo documento y revisar su PDF.

**Ampliación A1, 2026-10-15:** [sensibilidad con restricciones A0](life_proxima_a1_posterior_regions_2026-10-15.md#ampliación-sensibilidad-a-los-retrievals-alternativos-a0) calculada sobre muestras existentes verificadas: NH3 ≥ A1 pasa de 92,19 % a 94,43 % al fijar N2O; K nominal de región 3,83 → 5,50. N2O ≥ A1 permanece ≈100 % al fijar NH3. Fijar N2O empeora fuertemente el modelo; estos resultados son condicionales. Prior efectivo y operador coherente siguen pendientes, sin nueva campaña.

**Criterio A1 adoptado y calculado 2026-10-15:** a partir de la [revisión de Wogan](life_proxima_wogan_abundance_region_bayes_2026-10-15.md), el usuario fijó regiones individuales y conjunta con abundancias ≥ A1. El [análisis ejecutado](life_proxima_a1_posterior_regions_2026-10-15.md) guarda masas posteriores, intervalos, razones y odds nominales de la serie histórica, con hashes verificados y conteos A0 reproducidos. A3–100 h: masa conjunta 92,19 %, K nominal 18,19; no equivale a probabilidad ExoFarm. Siguiente paso de esta línea: validar prior efectivo y aplicar a productos corregidos aceptados. No se lanzaron retrievals ni se modificaron prioridades de campañas activas.

Las dos capas ya completaron la cadena POSEIDON emisión → LIFEsim clásico →
S/N. La Capa 2 añadió ocho retrievals canónicos Proxima A0--A3 × {10 h,
240 h}. No reabrir o ampliar esa matriz sin una nueva pregunta científica.

- `life_earth_sun_10pc_interface_v1` conserva el rótulo
  `earth_20260615_pre_n2o_correction`; sirve como benchmark de interfaz, no como
  matriz Tierra--Sol vigente.
- `life_proxima_b_earthlike_v1` es un análogo terrestre bajo la SED de Proxima,
  no la atmósfera medida de Proxima b.
- Los datasets de 1200 h y el retrieval A3--1200 h se preservan como evidencia
  de auditoría/piloto y quedan fuera del cierre 8/8.
- El 2026-08-31 se ejecutó un piloto intermedio A3--500 h con la configuración
  corregida de POSEIDON. Terminó con `ln Z = 893.18 +/- 0.40`,
  `chi^2_red = 1.59` y `R_p_ref = 1.23 R_E`; queda como evidencia de
  auditoría, no amplía la matriz canónica ni el atlas oficial. La corrida se
  lanzó inicialmente con el escalado validado de sigma desde 10 h; después se
  instaló LIFEsim 0.2.32 en el WSL `POSEIDON` y la observación directa de 500 h
  produjo un archivo idéntico byte a byte al usado por ese piloto histórico.
  El posterior robusto se relanzó por separado con `N_live=800`, el dataset
  directo y la configuración actual de `Piette20`; ambos productos deben
  mantenerse distinguidos. Véase la [validación directa](life_proxima_a3_500h_lifesim_direct_validation_2026-08-31.md).
- El 2026-08-31 se completaron retrievals robustos independientes de A3 a 500 h
  y 1200 h con datasets directos de LIFEsim. Dieron, respectivamente,
  `ln Z = 901.17 +/- 0.22`, `chi^2_red = 2.07` y
  `ln Z = 898.31 +/- 0.22`, `chi^2_red = 2.82`, con radios
  `1.23 R_E` y `1.26 R_E`. El intento viejo de 1200 h queda como evidencia del
  fallo numérico anterior; los nuevos productos son auditoría/piloto y no
  alteran la matriz canónica. `a1` queda cerca del límite superior del prior en
  ambos posteriores, por lo que todavía falta una prueba de sensibilidad a
  priors antes de usarlos como inferencia final. Véase el [informe del retrieval
  robusto](life_proxima_a3_500h_1200h_robust_retrieval_2026-08-31.md).
- El 2026-09-01 se ejecutó un diagnóstico adicional A3--500 h con
  `X_profile=two-gradients` sólo para `NH3`, `N_live=1000` y el mismo dataset
  directo. Terminó con `ln Z = 895.86 +/- 0.17`, `chi^2_red = 3.15` y 18
  parámetros; la mediana recupera la dirección de la caída vertical, pero la
  capa alta queda débilmente constreñida y el ajuste no mejora al retrieval
  isquímico (`ln Z = 901.17`, `chi^2_red = 2.07`). Es auditoría excluida y no
  reemplaza el resultado de referencia. Véase la [prueba de perfil vertical
  NH3](life_proxima_a3_500h_nh3_two_gradients_2026-09-01.md).
- El 2026-09-01 se calcularon dos diagnósticos rápidos de Bayes factor sobre el
  mismo dataset Proxima A3--240 h: A3 frente a A0 (`ln B=394.35`) y A3 frente
  al contrafactual con N2O reiniciado a A0 (`ln B=385.63`). Son likelihoods de
  plantillas fijas, con una sola realización y sigma diagonal; quedan como
  experimento de auditoría y no sustituyen la evidencia marginalizada ni la
  validación LIFEsimMC/PHRINGE. Véase el [informe de diagnósticos bayesianos
  rápidos](life_proxima_bayes_factor_diagnostics_2026-09-01.md).
- Las figuras Proxima de espectro y señal se actualizaron el 2026-08-30 solo en
  presentación: títulos compactos, etiquetas moleculares sin guías verticales
  y rellenos claramente diferenciados. La comparación SNR/proyección se ajustó
  al intervalo útil de 1--1000 h y a los puntos representados, y quedó promovida
  en PNG/PDF a `Thermal_Emission_Spectroscopy/final_products/figures/`. La
  figura conjunta sigue la composición de tres paneles del análogo de
  transmisión, sin cambiar el observable `F_p`, los datos ni la interpretación.
- El ensayo directo de ruido de LIFEsim del 2026-08-31 comparó A0/A3 en
  1--1200 h contra `sigma(10 h)*sqrt(10 h/t)`. La máxima diferencia relativa
  fue `6.7e-16` y la diferencia de una realización emparejada fue menor que
  `8.6e-15 sigma`: el escalado reproduce la llamada directa para LIFEsim
  clásico. Esto no prueba ruido correlacionado ni inestabilidad instrumental;
  el siguiente salto sigue siendo LIFEsimMC/PHRINGE.
- El atlas de retrieval LIFE Proxima se regeneró a partir de los ocho productos
  canónicos A0--A3 x {10 h, 240 h}. Las figuras de espectro global y ventanas
  moleculares comparan solo A0/A3; la figura de perfiles/posteriores se centra
  en A3 y muestra su perfil VULCAN y posterior frente a una referencia A0
  efectiva, calculada como promedio columnar ponderado en presión. Las curvas
  espectrales se interpolan a 250 puntos globales y 75 puntos por zoom
  únicamente para presentación, con la semántica visual Retrieved/True/Observed
  alineada al código de transmisión. La matriz de perfiles conserva la lógica
  de transmisión: perfil químico sólido, mediana posterior discontinua, línea
  A0 efectiva punteada, leyenda horizontal bajo el título, fórmula de la
  distancia firmada aparte y recuadros reducidos a la mediana A3 y su distancia
  en sigma junto al valor A0 de referencia. El panel global quedó sin grid y
  con marcadores observados ampliados a 5.8 pt, y los zooms a 6.2 pt. Quedó en
  `outputs/life_proxima_b_earthlike_v1/plots/` para revisión; el piloto
  A3--1200 h no se incorporó.

### Rama instrumental — siguiente frontera

El próximo trabajo científico autorizado es construir un piloto mínimo de
**LIFEsimMC/PHRINGE** sobre espectros ya validados, sin reinterpretar primero la
rama clásica:

1. congelar versión/commit, licencia, escena, perturbaciones, tiempo y semilla;
2. validar la interfaz de espectro custom y las unidades;
3. preservar SED extraído y covarianza completa;
4. definir whitening reproducible o likelihood correlacionada;
5. repetir al menos A0/A3 Proxima en varias realizaciones de ruido;
6. comparar modelos con/sin N2O y, si la señal lo justifica, con/sin NH3.

En paralelo sigue abierta la decisión sobre rerun Tierra--Sol con las
condiciones de frontera de N2O corregidas. No presentar el benchmark de junio
como matriz actual mientras esa decisión permanezca abierta.

## Investigación de escenarios NH3 (2026-10-13)

La [revisión de sumideros NH3](nh3_surface_sinks_huang_vulcan_review_2026-10-13.md)
completó lectura de Huang/Tsai/Haqq-Misra y auditoría de los cuatro Earth
`.vul` existentes: `v_dep=1 cm/s` en A0-A3, pérdida superficial efectiva sin
descomposición oceánica. A1 elimina por ese término un flujo equivalente al
86.34 % de la emisión impuesta. Los BC agrícolas se reconstruyen con el
presupuesto de N y la selección natural más agricultura de la nota de diseño.
La [lectura posterior del original de Hauglustaine y de Hu](nh3_deposition_velocity_provenance_and_physical_scenarios_2026-10-13.md)
confirma que Hauglustaine no tabula NH3 y que Hu prescribe `1 cm/s` por
solubilidad/reactividad, con un marco de resistencias. La malla heurística
`0.1/0.01 cm/s` queda retirada como propuesta vigente. La solicitud posterior
de escoger un único valor se concreta en el
[diseño `v_dep=0.65 cm/s`](nh3_weakened_surface_sink_vdep_0p65_design_2026-10-13.md),
`nh3_weakened_surface_sink_vdep_0p65_20261013`: de `1 cm/s` se retira una
contribución oceánica idealizada `0.70*0.50=0.35 cm/s`, utilizando el ancla
marina central de Lee y conservando el residual terrestre. La partición es
una inferencia condicionada, no una medición global. La motivación es un
océano superficial cercano al punto de compensación en una atmósfera
oxidante; Haqq-Misra limita la plausibilidad de saturación global persistente.
Estado: **valor seleccionado; sin implementar ni simular**. El siguiente
problema físico es resolver NHx/pH/T/salinidad, consumo y exportación del
reservorio, y separar las emisiones marinas antes de un intercambio
bidireccional. Con los flujos actuales intactos, una futura corrida sería
solo una sensibilidad del coeficiente efectivo. A0-A3 y las campañas
activas conservan sus configuraciones; la selección no autoriza corridas.

La solicitud posterior incorpora ese valor a una
[fase adicional de captación superficial reducida](nh3_reduced_capture_extra_phase_proposal_2026-10-13.md),
`nh3_reduced_capture_extra_phase_20261013`: cuatro candidatos
`A0-A3_NH3D065` y referencias emparejadas a `1 cm/s` por entorno que se
seleccione. Es una propuesta de plausibilidad condicionada; el A0 debilitado
es control contrafactual. Misma emisión NH3/N2O, SED, PT/Kzz y red en cada
pareja. El diagnóstico lineal `1/0.65=1.538` solo ilustra una respuesta
moderada sin pérdidas químicas adicionales; no predice VULCAN. Implicaciones
ecológicas requieren conocer NHx acuático y consumo/exportación. Estado:
**fase propuesta y documentada, sin ejecución**; selección de entorno,
campaña y aceptación de perfiles pendientes. Los Earth A2/A3 históricos
no son controles de la matriz N2O actual sin resolver su procedencia.

## Límites que no se pueden olvidar

- Stage III usa emisión térmica; no mezclar profundidades de tránsito, archivos
  PandExo, conteos de tránsitos ni `Transmission_Spectroscopy/notebooks/POSEIDON_output/`.
- LIFEsimMC puede entregar covarianza. No reducirla silenciosamente a errores
  diagonales: usar whitening reproducible o likelihood consciente de
  covarianza.
- SNR es un diagnóstico, no una detección. Las afirmaciones de detección esperan
  retrievals, modelos comparados y varias realizaciones de ruido.
- Los `.vul` permanecen en `Photochemical_Modeling/Results/Outputs/`; Stage III
  guarda sus productos únicamente bajo
  `Thermal_Emission_Spectroscopy/outputs/<campaign-id>/`.

## Cómo recuperar el trabajo de forma segura

1. Ejecutar `git status --short` y no sobrescribir cambios ajenos. La presencia
   de productos o documentación no implica que una simulación esté validada.
2. Confirmar la etapa y el ID de campaña contra el tracker y este documento.
3. Para Stage III, comprobar el entorno WSL en vivo. La ejecución de
   2026-08-31 verificó Ubuntu, el entorno conda `POSEIDON` en
   `/home/wsldasan/miniconda3/envs/POSEIDON` y los inputs
   `/home/wsldasan/POSEIDON/inputs` y
   `/home/wsldasan/POSEIDON/inputs/stellar_grids`; la ruta y las dependencias
   deben volver a verificarse antes de ejecutar.
4. Antes de una corrida costosa, comprobar que existe el manifiesto de campaña,
   que las unidades están escritas, que las entradas coinciden con la campaña y
   que el manifiesto distingue `earth_20260615_pre_n2o_correction` de los BC
   vigentes.
5. Después de una decisión, ejecución o validación material, actualizar:
   - `docs/project_status_tracker.md`;
   - este archivo `docs/project_resume.md`;
   - `experiments/README.md`;
   - el README de la etapa y un informe en `docs/` cuando cambie el argumento
     científico o la interfaz.

## Mapa de documentación

| Necesidad | Fuente canónica |
| --- | --- |
| Reglas para agentes y guardrails | [`../AGENTS.md`](../AGENTS.md) |
| Estado, backlog y decisiones | [`project_status_tracker.md`](project_status_tracker.md) |
| Etapa I y contrato de VULCAN | [`photochemical_profiles_methodology.md`](photochemical_profiles_methodology.md) |
| Inventario/entorno de transmisión | [`transmission_spectroscopy_inventory_2026-06-16.md`](transmission_spectroscopy_inventory_2026-06-16.md) |
| Diseño general Stage III | [`life_lifesim_stage_iii_plan.md`](life_lifesim_stage_iii_plan.md) |
| Flujo concreto de dos capas | [`life_stage_iii_two_layer_workplan_2026-07-20.md`](life_stage_iii_two_layer_workplan_2026-07-20.md) |
| Metodología completa de Stage III clásico | [`life_stage_iii_classic_methodology_2026-08-30.md`](life_stage_iii_classic_methodology_2026-08-30.md) |
| Informe integrado Stage III: metodología, resultados, tablas y plots | [`life_stage_iii_integrated_methodology_results_2026-08-30.md`](life_stage_iii_integrated_methodology_results_2026-08-30.md) |
| Validación y resultado de LIFEsim clásico | [`lifesim_classic_stage_iii_validation_2026-08-30.md`](lifesim_classic_stage_iii_validation_2026-08-30.md) |
| Auditoría del retrieval Proxima A3--500 h | [`life_proxima_a3_500h_retrieval_audit_2026-08-31.md`](life_proxima_a3_500h_retrieval_audit_2026-08-31.md) |
| Validación directa LIFEsim Proxima A3--500 h | [`life_proxima_a3_500h_lifesim_direct_validation_2026-08-31.md`](life_proxima_a3_500h_lifesim_direct_validation_2026-08-31.md) |
| Ensayo de ruido directo frente a escalado temporal | [`life_proxima_lifesim_noise_scaling_2026-08-31.md`](life_proxima_lifesim_noise_scaling_2026-08-31.md) |
| Retrieval robusto Proxima A3--500/1200 h | [`life_proxima_a3_500h_1200h_robust_retrieval_2026-08-31.md`](life_proxima_a3_500h_1200h_robust_retrieval_2026-08-31.md) |
| Prueba de perfil vertical NH3 A3--500 h | [`life_proxima_a3_500h_nh3_two_gradients_2026-09-01.md`](life_proxima_a3_500h_nh3_two_gradients_2026-09-01.md) |
| Diagnósticos de Bayes factor Proxima A3--240 h | [`life_proxima_bayes_factor_diagnostics_2026-09-01.md`](life_proxima_bayes_factor_diagnostics_2026-09-01.md) |
| Procedencia N2O de perfiles Tierra--Sol | [`earth_sun_n2o_matrix_provenance_2026-07-20.md`](earth_sun_n2o_matrix_provenance_2026-07-20.md) |
| Selección Tierra--Sol/Proxima | [`life_target_selection_2026-07-20.md`](life_target_selection_2026-07-20.md) |
| Ubicación de productos | [`repository_structure.md`](repository_structure.md) |
