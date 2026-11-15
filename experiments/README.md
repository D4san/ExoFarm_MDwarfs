**LIFE: comparación con literatura (29-oct):** [nota de contexto y diagnóstico](../docs/life_proxima_detectabilidad_comparacion_literatura_2026-10-29.md); solo análisis de productos existentes. Los controles de superficie, ruido y ajuste quedan como propuestas, sin nueva campaña.

**LIFE Proxima A1/A3 — análisis vigente, 2026-10-29:** [informe integrado y productos](../docs/life_proxima_a1_a3_retrievals_analisis_integrado_2026-10-29.md), recalculados desde seis completos y 36 ablaciones corregidas; 1000 h A0 fija sigue exploratorio con aceptación pendiente. Las entradas LIFE antiguas siguientes son bitácora de campañas; no se ejecutaron retrievals adicionales para este análisis.

**Inventario y respaldo LIFE A1/A3 (28-oct):** [979 archivos y 12 registros de supervisor verificados por SHA-256](../docs/evidence/life_proxima_a1_a3_release_2026-10-28/README.md), incluidos productos, referencias y logs, con copia comprobada en E:. Se guardó aparte una lista posterior de paquetes del entorno actual; queda pendiente versionar selectivamente los resultados y preservar el entorno y las opacidades externas.

**Cerrada y auditada — LIFE Proxima, matriz A1/A3 con binning corregido (28-oct):** 33/33 retrievals pasaron la auditoría independiente: tres completos y 18 LOO A1, más 12 LOO A3; los tres completos A3 de referencia también se validaron. La cola respetó el máximo de tres MPI4/12 ranks. Se conciliaron los ledgers después de la salida 0 del supervisor y se preservaron snapshots, corridas históricas y productos con binning anterior. [Informe y resultados](../docs/life_proxima_a1_a3_corrected_binning_matrix_results_2026-10-28.md) · [tablas](../docs/life_proxima_a1_a3_corrected_binning_matrix_models_2026-10-28.csv) · [campaña y manifiesto](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a1_a3_corrected_binning_matrix_loo_20261021_r01/README.md).

**Cerrada y validada — seis retrievals A3 a 1 h/10 h con binning corregido (2026-10-21):** completo, sin NH₃ y sin N₂O para cada duración. Todos finalizaron con `return_code=0` y pasaron auditoría de posterior, espectro, P–T, `log_X`, MultiNest, finitud, hashes, priors y operador. Los contrastes `ΔlnZ=lnZ_completo−lnZ_sinX` se emparejaron dentro de cada dataset; a 10 h, la inclusión de N₂O está favorecida por `+9.141993±0.292323` (sigma bilateral calibrado `+4.664`, auxiliar). NH₃ da `−0.225706±0.292617`, compatible con empate, aunque `P(NH₃>A0)=0.8040` en el posterior completo de 10 h. La comparación no demuestra origen agrícola. Véanse el [informe con datos e interpretación](../docs/life_proxima_a3_1_10h_corrected_binning_loo_results_2026-10-21.md), el [README/campaña r03](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1_10h_binning_corrected_loo_20261020_r03/README.md) y la [bitácora](../docs/life_proxima_a3_1_10h_corrected_binning_loo_2026-10-20.md). Los intentos r01/r02 y snapshots originales quedan preservados.

**Registro histórico de monitoreo (20-oct):** los contadores y estados parciales descritos en notas anteriores corresponden al muestreo en curso; no son el estado actual.

**Plan de homologación por binning corregido (2026-10-21):** el inventario concluye que faltan 33 retrievals para una matriz homogénea A1/A3 (tres completos A1, 18 LOO A1 y 12 LOO A3 para H₂O/CO₂/CH₄/O₃). Los tres completos A3 y seis LOO A3 de NH₃/N₂O ya están corregidos y validados. Se agregan tres retrievals A3–100 h A0-fijos solo si se decide reemplazar esa comparación histórica; total 36 con ese bloque. Antes de ejecutar se verifican hashes de los datasets y se congela ventana, priors y configuración. [Inventario y puertas; sin lanzamiento autorizado](../docs/life_proxima_corrected_binning_update_plan_2026-10-21.md).

**Regiones de abundancia para la pregunta ExoFarm (actualización 2026-10-26):** el análisis de posteriores A3 corregidos ya se ejecutó con **0 retrievals nuevos**. Las cuatro celdas conjuntas N₂O/NH₃ y sus masas previas están calculadas; la incertidumbre Monte Carlo y la sensibilidad al umbral siguen pendientes. Las 33 corridas de matriz (36 con tres A0-fijas opcionales) son independientes; una comparación causal entre familias ExoFarm/preagrícola todavía no tiene alcance ni conteo definido. [Método y resultados](../docs/life_proxima_a1_regions_corrected_binning_2026-10-26.md).

**Cerrada y validada, 2026-10-20 — A3–100 h, ablaciones sin NH3/sin N2O con binning corregido:** ambos retrievals y el baseline común pasaron auditoría de productos. `ΔlnZ=+2.748991±0.344630` para NH3 y `+84.660508±0.346532` para N2O; el posterior completo deja `P(X>A0)=0.9913` para NH3 y 1.0000 para N2O. La sigma calibrada es solo auxiliar; el `χ²_red=3.57` del completo y 13.55 sin N2O condicionan la lectura. Los conteos finales de posterior fueron conciliados con los productos nativos y sus snapshots originales preservados. [Informe](../docs/life_proxima_a3_100h_corrected_binning_molecular_ablation_2026-10-19.md); [campaña, ledger, manifiesto y auditoría](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_100h_binning_corrected_loo_20261019/README.md).

**LIFE Proxima A3–100 h, binning corregido, MPI14 (muestreo y auditoría cerrados; 2026-10-20):** reanudó desde checkpoint validado en campaña aislada; MultiNest cerró con `exit_code=0`, 44.526 reemplazos, 1.474.040 evaluaciones y `ln(ev)=894.331224 ± 0.246654`. La auditoría independiente de posterior, espectro, P–T, `log_X`, MultiNest, finitud, hashes, priors y operador pasó; el baseline es el comparador aceptado de las ablaciones LOO. El campo `error` inicial se conserva como primer preflight Open MPI fallido; el retry MPICH/Hydra pasó y el muestreo final cerró con exit 0. La comparación histórica sigue mezclando operador y rejilla (3.8–19 frente a 3–20 μm). Informe: [bitácora MPI14](../docs/life_proxima_a3_100h_binning_corrected_mpi14_resume_2026-10-18.md); estado y productos validados en [campaña](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_100h_binning_corrected_mpi14_resume_20261018/).

La comparación preliminar de las muestras históricas y corregidas ya está
calculada: `ln Z=884.333304` frente a `894.331224`, `χ²_red=4.94` frente a
`3.57`; las medianas de N₂O cambian `+0.031 dex` y las de NH₃ `+0.087 dex`.
El `Δ ln Z≈+9.998` es sensibilidad a la implementación del forward, no un
factor de Bayes; la rejilla y la falta de límites históricos completos de
prior impiden atribuir el cambio exclusivamente al bineado. Véase la
[tabla y figura de comparación](../docs/life_proxima_a3_100h_binning_corrected_mpi14_resume_2026-10-18.md).

**FR-Genghis, pausa solicitada 2026-10-04 16:38 COT:** campaña detenida por el usuario con `SIGKILL` tras su autorización explícita. No quedan procesos ni lock; el cálculo no guardado desde cada checkpoint se descartó. Los cinco checkpoints finales de esta generación coinciden con controller, sidecar y restart y pasaron `lpjcheck -pedantic` (exit 0). No hay exit codes finales ni productos aceptados. Configuración al detener: cinco bloques de 8.000 celdas, un rank MPI por bloque, CH4, `MAX_PARALLEL=5` y retención completa. No relanzar sin nueva autorización; véase [registro de pausa](../docs/fr_genghis_campaign_pause_2026-10-04.md). Interpretación limitada por `river_routing=false` y `reservoir=false`.

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
> **FR-Genghis interrumpido — revisión 2026-10-02 21:14 COT:** la generación de cuatro bloques (`MAX_PARALLEL=4`, `MPI_RANKS=1`, `CHUNK_SIZE=8000`, CH4, retención completa) dejó de correr entre 20:11 y 21:13. Dos comprobaciones confirmaron ausencia de workers; logs sin crecimiento desde 19:53 y marcador RUNNING obsoleto. Los checkpoints 00000/08000/16000 (años 1560/1488/1486) siguen íntegros: SHA-256 `1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212`, `836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1`, `7f3b065e67ed12d4ec1703faf068cb07d16667a83879fa04cde7b35e6d19077e`; `cmp` y `lpjcheck -pedantic` dieron exit 0. 24000 comenzó desde A0 sin checkpoint; no hay códigos finales ni productos aceptados. Sin evento OOM accesible; causa indeterminada. No se reinició automáticamente. Se preserva la limitación `river_routing=false`/`reservoir=false`. Informe: [`paralelismo de bloques`](../docs/lpjml_capacity_chunk_parallelism_2026-10-01.md).

> **Actualización de la serie oficial LIFE, 2026-10-02:** la realización
> independiente A1-1 h (seed `2125532119`, MPI6 PID `1874`) fue promovida a la
> entrada oficial de la serie focal A1/A3 × {1, 10, 100 h}; la primera
> realización (seed `368516754`) se conserva como sensibilidad. La decisión
> fue post hoc, después de inspeccionar las dos posteriores. El atlas oficial
> se regeneró con el producto seleccionado. La matriz A0--A3 × {10 h, 240 h}
> 8/8 permanece intacta como evidencia legacy. [Informe y figuras](../docs/life_proxima_a1_1h_independent_noise_repeat_2026-10-02.md).

> **Estado Stage III vigente, 2026-10-01 18:48 COT:** la serie focal oficial
> A1/A3 a **1, 10 y 100 h** está cerrada y validada; la figura N2O/NH3/P--T
> oficial también está generada e inspeccionada. Los dos retrievals de 1 h
> cerraron con código de muestreo 0; sus 13 archivos por escenario se
> recuperaron sin sobrescritura tras corregir la ruta de cosecha. La matriz
> amplia A0–A3 × {10 h, 240 h}, su índice 8/8 y los scratch originales siguen
> intactos. Ruido diagonal y una realización por dataset: `z` es condicional y
> `ln Z` se informa por dataset, no como factor de Bayes entre exposiciones.

> **FR-Genghis, revisión 2026-10-02 14:36 COT:** los tres bloques continúan activos con CPU. Últimas filas: 1560/1488/1485; SHA-256 de los checkpoints `1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212`, `836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1` y `7f3b065e67ed12d4ec1703faf068cb07d16667a83879fa04cde7b35e6d19077e`. El bloque 16000 guardó un nuevo checkpoint a las 14:29 COT y el proceso actual ya lo cargó. No hay nuevas filas en los otros dos bloques desde 12:34 COT; sin códigos finales ni productos aceptados. Hay 14 GiB disponibles, 95 MiB de swap y 517 GiB libres; no se observa presión inmediata. Se mantienen CH4, `MAX_PARALLEL=3`, un rank por bloque, retención completa y las limitaciones `river_routing=false`/`reservoir=false`.

> **FR-Genghis, revisión 2026-10-02 13:38 COT:** siguen activos los tres bloques con CPU creciente. Últimas filas: 1560/1488/1485; checkpoints activos con SHA-256 `1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212`, `836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1` y `e9d67152cc7770b7a53e11440effa12ed699d984969f1d53967c0199a0ae14ce`. No hay filas nuevas desde 12:34 COT ni códigos finales. RAM disponible 15 GiB, swap 575 MiB y 518 GiB libres; sin presión inmediata. Se mantienen CH4, `MAX_PARALLEL=3`, un rank por bloque, retención completa y las limitaciones `river_routing=false`/`reservoir=false`.

> **FR-Genghis, checkpoint del tercer bloque verificado 2026-10-02 01:27 COT:**
> `16000_23999` guardó el año 1482, SHA-256
> `de713797e50d9ccf0b3b9a67eb89746035f3eb9f36f436377364c1745757f857`;
> `lpjcheck -pedantic` terminó con código 0. Los dos bloques reanudados
> conservan sus hashes de años 1556 y 1484 y sus logs registran 1557 y 1485.
> Los tres procesos siguen activos; hay 14 GiB de RAM disponibles, 1.5 MiB de
> swap usados y 523 GiB libres. Continúa la selección de tres bloques CH4,
> un rank por bloque y retención completa; no se acepta producto científico.
> `river_routing=false` y `reservoir=false` siguen limitando la interpretación.

> **FR-Genghis, estado 2026-10-02 08:30 COT:** `00000_07999` registra
> 1559 y conserva el checkpoint íntegro de 1558
> (`4c1beab2ecf40db4e78cfbdd8a4ed5843bc9f0ba39031d37d2a9e88cdca07030`);
> `08000_15999` registra 1487 y conserva el checkpoint de 1486
> (`66d13bb13237714af53246b13840d21177ad7b5c252dbb7c6527eda02a6b1578`).
> `16000_23999` guardó checkpoint de 1484
> (`e9d67152cc7770b7a53e11440effa12ed699d984969f1d53967c0199a0ae14ce`);
> `lpjcheck -pedantic` aceptó ese reinicio con código 0. Los tres procesos
> siguen activos con CPU; hay 14.7 GiB disponibles, 1.5 MiB de swap y 520 GiB
> libres. Sin códigos finales ni salidas aceptadas. Se mantienen CH4,
> `MAX_PARALLEL=3`, un rank por bloque, retención completa y las limitaciones
> `river_routing=false` y `reservoir=false`.

> **FR-Genghis, revisión 2026-10-02 10:32 COT:** no avanzaron las filas de
> año ni los checkpoints desde las 08:30; los tres LPJmL siguen activos y con
> uso de CPU de 61.5--68.9 % por proceso. Se conservan los checkpoints 1558,
> 1486 y 1484 en los bloques `00000_07999`, `08000_15999` y `16000_23999`,
> respectivamente, con SHA-256
> `4c1beab2ecf40db4e78cfbdd8a4ed5843bc9f0ba39031d37d2a9e88cdca07030`,
> `66d13bb13237714af53246b13840d21177ad7b5c252dbb7c6527eda02a6b1578` y
> `e9d67152cc7770b7a53e11440effa12ed699d984969f1d53967c0199a0ae14ce`.
> Hay 14 GiB disponibles, 1.5 MiB de swap usados y 520 GiB libres. No hay
> productos aceptados; routing y embalses locales siguen desactivados.

> **FR-Genghis, revisión 2026-10-02 11:33 COT:** el log de
> `16000_23999` avanzó a 1485 y mantiene checkpoint 1484
> (`e9d67152cc7770b7a53e11440effa12ed699d984969f1d53967c0199a0ae14ce`).
> Los otros bloques siguen en 1559/1558 y 1487/1486, con SHA-256
> `4c1beab2ecf40db4e78cfbdd8a4ed5843bc9f0ba39031d37d2a9e88cdca07030` y
> `66d13bb13237714af53246b13840d21177ad7b5c252dbb7c6527eda02a6b1578`.
> Tres procesos siguen activos con CPU. Hay 14 GiB disponibles, 1.5 MiB de
> swap usados y 520 GiB libres; sin códigos finales ni productos aceptados.
> El restart 16000 conserva la aceptación previa de `lpjcheck -pedantic`
> (código 0). Se mantienen CH4, `MAX_PARALLEL=3`, retención completa y
> routing/embalses locales desactivados.

> **FR-Genghis, revisión 2026-10-02 12:34 COT:** los logs avanzaron a 1560
> (`00000_07999`) y 1488 (`08000_15999`); sus checkpoints activos guardados
> en esta revisión tienen SHA-256
> `1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212` y
> `836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1`.
> `16000_23999` registra 1485 y conserva restart de 1484
> (`e9d67152cc7770b7a53e11440effa12ed699d984969f1d53967c0199a0ae14ce`).
> Los tres LPJmL siguen activos con CPU; hay 16 GiB disponibles, 1.5 MiB de
> swap usados y 518 GiB libres. Sin códigos finales ni productos aceptados;
> los stderr recientes solo muestran advertencias. Sigue CH4,
> `MAX_PARALLEL=3`, retención completa y routing/embalses locales desactivados.

> **FR-Genghis, estado 2026-10-02 04:30 COT:** `00000_07999` y
> `08000_15999` ya guardaron y validaron con `lpjcheck -pedantic` los años
> 1558 (`4c1beab2ecf40db4e78cfbdd8a4ed5843bc9f0ba39031d37d2a9e88cdca07030`)
> y 1486 (`66d13bb13237714af53246b13840d21177ad7b5c252dbb7c6527eda02a6b1578`),
> ambos con código 0. `16000_23999` registra 1483 y conserva el checkpoint de
> 1482 (`de713797e50d9ccf0b3b9a67eb89746035f3eb9f36f436377364c1745757f857`).
> Los tres procesos siguen activos con CPU; hay 16 GiB disponibles, 1.5 MiB
> de swap usados y 521 GiB libres. Sin salidas finales aceptadas. Sigue la
> configuración CH4, `MAX_PARALLEL=3`, un rank por bloque y retención completa;
> `river_routing=false` y `reservoir=false` limitan la interpretación.

> **FR-Genghis reanudado con tres bloques 2026-10-01 18:51 COT:** tras un
> reinicio de WSL se confirmó que no quedaban procesos y que el bloqueo global
> estaba vacío. Los checkpoints activos se recalcularon: `00000_07999` reanudó
> desde año 1556 (`f150c32b9c5ebdbe9202cf15dc18785d35d0c4efa20575f301ba2db9541c2080`),
> `08000_15999` desde año 1484
> (`7d687ce9dfc6fe08478f181152cce943f9095f19b37d7e583833e939574f4e85`),
> ambos aceptados por `lpjcheck`. A solicitud del usuario, la campaña CH4
> corre desde las 18:49 con `MAX_PARALLEL=3`, un rank MPI por bloque y
> `MAX_ARCHIVED_CHECKPOINTS=0`. El nuevo bloque `16000_23999` inició desde A0,
> sin checkpoint todavía. La primera lectura dejó 25 GiB disponibles, swap 0
> y 525 GiB libres; velocidad y resultados científicos siguen pendientes.
> Routing local y embalses permanecen desactivados. Véase el
> [`informe de paralelismo`](../docs/lpjml_capacity_chunk_parallelism_2026-10-01.md).
> Revisión 19:08 COT: los tres procesos siguen activos; una muestra instantánea
> registró 80 %, 68 % y 52 % de CPU, con 4.2--4.7 GiB de RSS cada uno; quedan
> 17 GiB de RAM disponibles, sin swap usado y 525 GiB libres. Los SHA-256 de
> los checkpoints retomados se mantienen. Los
> logs de esta generación aún no muestran un año nuevo y el bloque 16000 no
> tiene checkpoint; la tasa de avance continúa pendiente.

> **FR-Genghis reanudado 2026-09-22 20:48 America/Bogota:** el primer bloque
> sigue en cálculo desde el checkpoint íntegro (`sha256=
> 80c0a282b424c4f5f6b9faae3eca2b8f2c69e40f4fa9fe4a2ee43fe39e71f52a`) tras
> comprobar la ausencia de procesos previos. Un rank MPI está activo; todavía
> no hay salida científica aceptada.

> **A0 validado 2026-09-22:** el control natural terminó con `exit_code=0`,
> cobertura 1996--2005 y validación PASS. Sus medias son `1.334471e9` N2O y
> `2.964787e9` NH3 moléculas `cm-2 s-1`; el informe A0/A1 documenta la
> discrepancia de NH3 con la referencia congelada.

> **A0 reanudado 2026-09-21 00:30 UTC:** el control natural alcanzó el año
> 1587 y dejó un checkpoint íntegro (`sha256=
> 4c6dfe69fd019922380ab6196ba52572365734b44219f2d3db64298387149b7c`). La
> primera ejecución se interrumpió sin error de LPJmL; se reanudó desde el
> checkpoint con ocho ranks y el estado sigue pendiente de validación.

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

# ExoFarm Campaign Index

**Atlas oficial LIFE Proxima (N₂O y NH₃ primero, sin panel P–T; 2026-10-28):** se trazan los completos A1/A3 a 1/10/100 h; los perfiles verticales de abundancia permanecen. PNG/PDF/SVG y procedencia con hashes están en Thermal_Emission_Spectroscopy/final_products/figures/; la nota sobre el binning fue retirada de la figura. [Informe y reproducción](../docs/life_proxima_corrected_binning_full_posteriors_plot_2026-10-28.md) · [cierre y resultados LOO](../docs/life_proxima_a1_a3_corrected_binning_matrix_results_2026-10-28.md).

**Postprocesado A3–100 h corregido, 2026-10-20:** [actualización de resultados](../docs/life_proxima_a3_100h_corrected_results_update_2026-10-20.md) ejecutada desde el baseline MPI14 y las dos ablaciones auditadas. Evidencia, regiones A0/A1/A3, K nominales, intervalos/dex y comparación P–T guardados con hashes. NH3 ≥A1: `98.6654 %`, 95 % `[2.572,25.377] A1`; conjunta ≥A1: `98.6654 %`, `K nominal=113.924`. Sin nueva campaña. La matriz vigente conserva etiquetas de operador por fila; tres restricciones A0 corregidas de 100 h siguen pendientes y las versiones históricas se preservan.

**Integración editorial 2026-10-16:** [análisis bayesiano LIFE en el manuscrito](../docs/life_manuscript_bayesian_integration_2026-10-16.md), sin nueva campaña. Se reutilizaron las seis posteriores históricas, las 36 omisiones y las tres restricciones A0. Texto y bibliografía guardados; compilación integrada bloqueada por clase AASTeX ausente, como antes de la edición. Condiciones de aceptación de productos científicos intactas.

**Ampliación de postprocesado A1, 2026-10-15:** [restricciones individuales A0](../docs/life_proxima_a1_posterior_regions_2026-10-15.md#ampliación-sensibilidad-a-los-retrievals-alternativos-a0) reutilizadas para probabilidades y odds nominales condicionales y contrastes de evidencias. Dos matrices de muestras verificadas contra la auditoría aceptada; sin nuevos retrievals. Se preservan la limitación de binning y la validación pendiente del prior efectivo.

**Postprocesado ejecutado, 2026-10-15 — regiones ≥ A1:** el usuario adoptó el umbral actual A1 para cada molécula y su intersección. Se calcularon masas posteriores, razones, intervalos y odds nominales de las seis corridas históricas: [informe reproducible](../docs/life_proxima_a1_posterior_regions_2026-10-15.md). La [adaptación de Wogan](../docs/life_proxima_wogan_abundance_region_bayes_2026-10-15.md) documenta el fundamento. Prior efectivo y causalidad pendientes; sin nuevos modelos ni retrievals.

**Postprocesado actualizado, 2026-10-26 — regiones A1 en A3 corregido:** se validaron los priors efectivos independientes uniformes en `log10 X ∈ [-12,-1]` y se calcularon las cuatro masas previas/posteriores a 1/10/100 h desde muestras verificadas por SHA-256. `P(R11|D)=6.42/73.07/98.665 %`; `K(R11/complemento)=0.106/4.181/113.924`. El LOO emparejado de ausencia de N₂O/NH₃ ya está auditado para esos tres tiempos. Sin nuevos retrievals. Pendientes: incertidumbre Monte Carlo/colas, sensibilidad al umbral y adecuación del modelo; no confundir región ≥A1 con atribución ExoFarm. [Informe, script y CSV](../docs/life_proxima_a1_regions_corrected_binning_2026-10-26.md).

## A3–1000 h: tres restricciones A0 con binning coherente (2026-10-15; auditoría 2026-10-17)

**Cierre auditado 2026-10-17:** el relanzamiento fresco de las tres variantes
terminó exit0. La auditoría de los productos primarios, ocho salidas
MultiNest/caso, dataset, priors, parámetros fijos, callback del operador y
hashes pasó. Diferencias emparejadas respecto al completo corregido:
N₂O fija `ln B=626.5061±0.3845`; NH₃ fija `−0.9927±0.3825` (sigma N/A);
conjunta `626.0635±0.3822`. La finitud global estricta sigue en revisión por
seis `NaN` únicamente en desviaciones calculadas para coordenadas fijas.
Los momentos centrados estables se guardaron por separado; los originales
no se modificaron y no se concedió salvedad automática. El completo tiene
`χ²_red=14.29` con 17 dof efectivos. Véase el [informe detallado](../docs/life_proxima_a3_1000h_a0_fixed_binning_corrected_audit_2026-10-17.md),
la [tabla CSV](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a3_1000h_a0_fixed_binning_corrected_2026-10-17.csv)
y el [JSON de validación](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a0_fixed_reference_A3_1000h_binning_corrected_20261016_relaunch_01/validation_report_20261017.json).

**Interrupción detectada2026-10-16 11:44UTC:** supervisor816, tres MPI5 y
quince ranks ya no existen. El inspector encontró
`JSONDecodeError: Expecting value: line 1 column 1 (char 0)`; estado (16386 B)
y manifest (1790 B) están llenos de NUL, mtime10:10:30UTC. Últimas cuentas de
logs: 41400/38550/37550 reemplazos y704371/700838/693688 muestras. Sin error
fatal o código de salida registrado; ocho archivos MultiNest por variante
permanecen en scratch. Cierre y aceptación desconocidos. No reanudar/reiniciar
ni alterar evidencias; recuperación pendiente de decisión del usuario.
[Registro](../docs/life_proxima_a3_1000h_a0_binning_corrected_2026-10-15.md).

Seguimiento2026-10-16 09:49UTC/16oct04:49COT: `RUNNING`, aceptaciónPENDING,
supervisor816, MPI5 1083/1130/1177 y quince ranks activos OMP1. N₂O/NH₃/conjunta
41000/38000/37050 reemplazos y686281/681683/673688 evaluaciones; frente a08:14UTC
avanzaron2150/3000/2450 y85200/84865/84691. CPU creció en todos; PSS19≈6.999GiB,
RAM23.44GiB disponible, swap0. Ocho archivos MultiNest/caso, binding5/5 por
log, sin firmas de fallo fatal. Dataset/operator hashes y callback/preflights
PASS; dimensiones libres13/13/12. Productos pendientes y ln Z transitoria
sin interpretar; el alcance y los procesos permanecen intactos.

Seguimiento2026-10-16 08:14UTC/16oct03:14COT: `RUNNING`, supervisor816,
MPI5 1083/1130/1177, quince ranks activos. N₂O/NH₃/conjunta: 38850/35000/34600
reemplazos y601081/596818/588997 evaluaciones; desde06:48UTC aumentaron
2250/3400/2650 reemplazos y77397/76938/78317 evaluaciones. PSS19procesos≈7.131GiB,
RAM23.33GiB disponible, swap0; ocho archivos MultiNest/caso, cinco bindings
del operador por log, cero patrones fatales. Priors libres/tipos, dataset,
operador y callback conformes. Sin productos aceptados; monitor90min.

Seguimiento2026-10-16 06:48UTC/16oct01:48COT: `RUNNING`, supervisor816,
MPI5 1083/1130/1177 y quince workers activos. N₂O/NH₃/conjunta:
36600/31600/31950 reemplazos, 523684/519880/510680 evaluaciones; del punto
05:22UTC aumentaron2450/3600/2300 reemplazos y70207/67763/64301 evaluaciones.
PSS19procesos≈6.833GiB, RAM22.93GiB disponible, swap0. Ocho archivos
MultiNest/caso, cinco bindings del operador por log y cero patrones fatales.
Hash de dataset y operador, callback y comparación de priors libres PASS.
Sin productos aceptados; monitor90min.

Seguimiento2026-10-16 05:22UTC/16oct00:22COT: `RUNNING`, supervisor816,
tres MPI5/quince workers OMP1. N₂O/NH₃/conjunta: reemplazos34150/28000/29650,
evaluaciones453477/452117/446379; los quince contadores CPU avanzaron desde
03:54UTC. RAM disponible24.41GiB, PSS≈6.412GiB, swap0; ocho archivos
MultiNest/caso, binding5/5 y cero patrones fatales. Dataset, operador y
equivalencia PASS; dimensiones libres13/13/12. Productos y aceptación
pendientes; ln Z provisional sin interpretación; monitor90min.

Seguimiento2026-10-16 03:54UTC/15oct22:54COT: `RUNNING`, supervisor816,
tres MPI5 y quince workers OMP1. N₂O/NH₃/conjunta: reemplazos31400/25400/26900,
evaluaciones393646/393759/387996; todos los contadores CPU avanzaron desde
02:31UTC. RAM disponible23.32GiB, PSS≈6.629GiB, swap0; ocho archivos
MultiNest/caso, binding5/5 y cero patrones fatales. Dataset y operador
verificados; auditoría de equivalencia PASS y dimensiones libres13/13/12.
Productos finales/aceptación pendientes, ln Z provisional sin interpretación;
monitor90min.

Seguimiento2026-10-16 02:31UTC/15oct21:31COT: `RUNNING`, supervisor816 y tres
MPI5 (1083/1130/1177), quince ranks OMP1. N₂O/NH₃/conjunta: reemplazos
27250/23100/23650 y evaluaciones326778/325815/323781; aumento en CPU de todos
los ranks. RAM disponible23.75GiB, PSS≈6.788GiB, swap0; cinco bindings del
operador por caso, ocho archivos MultiNest y cero patrones fatales. Dataset
SHA/configuraciones confirmados; dimensiones libres13/13/12. Productos finales
y aceptación pendientes; ln Z de logs sigue siendo provisional. Monitor90min.

Seguimiento2026-10-16 01:03UTC/15oct20:03COT: `RUNNING`, preflight3/3 PASS, tres MPI5 y
quince workers reales activos. Supervisor816, launchers1083/1130/1177;
reemplazos23600/21000/21400 y CPU avanzando. RAM23.47GiB disponible, swap0,
49 hashes protegidos PASS. Sin producto final aceptado; monitor90min continúa.

Autorizadas N₂O/NH₃/ambas fijas, MPI5 por corrida, máximo tres simultáneas
y 15 ranks. Se reutiliza el completo corregido y su mismo dataset/hash;
preflight del callback y priors y memoria PSS antes del muestreo. Estado
recuperable en `retrievals/a0_fixed_reference_A3_1000h_binning_corrected_20261015/`
bajo la campaña LIFE Proxima. Seguimiento cada 90 minutos. 100 h aplazado.
[Procedimiento, scripts y aceptación pendiente](../docs/life_proxima_a3_1000h_a0_binning_corrected_2026-10-15.md).

This directory is a compact human index for ExoFarm campaigns. It is not a
second data model for the repository: the scientific evidence lives in the
stage directories and in `docs/`.

Use this file to answer three questions quickly:

1. Which campaigns are current?
2. What caveat must be stated?
3. Where is the evidence?

For the authoritative next action, read
[`../docs/project_resume.md`](../docs/project_resume.md) before using a row as
an execution instruction.

## Current campaigns

**2026-10-15 — A3–1000 h, binning coherente, cómputo cerrado:**
`a3_1000h_binning_corrected_20261014` terminó con exit 0, productos y
comparación automática guardados; no quedan procesos MPI. Se mantuvieron los
datos, priors, modelo y rejilla térmica, cambiando solo el operador. El
generador integra fotones sobre bordes de canal definidos por centros vecinos;
el cálculo anterior de POSEIDON reconstruía bordes simétricos y ponderaba
energía. La versión corregida quedó ligada al callback real durante muestreo
y postproceso. El wrapper está congelado a A3–1000 h/dataset; cualquier otra
exposición o pareja A0/A3 requiere preflight específico y el mismo operador
en ambos retrievals. χ²
542,64→242,88 (17 dof); `ln Z` 677,9235→826,6111. La diferencia entre
operadores es sensibilidad numérica, no evidencia de molécula; el χ² reducido
corregido≈14,29 sigue siendo alto. N₂O cambia +0,051 dex y NH₃ +1,357 dex en
medianas; NH₃ conserva un intervalo amplio. Figura inspeccionada; aceptación
científica formal pendiente. No comparar con A0 bajo operador anterior.
[Informe, datos y figura](../docs/life_proxima_a3_1000h_binning_corrected_2026-10-14.md).

**2026-10-14 — capacidad espectral P–T, ruido excluido:** dos arranques
Madhu de seis coordenadas, química vertical/geometría fijas;161 forwards
y exit0. Menor Q41.0199/RMS1.1503σ; ventanaNH₃ máximo0.9216σ, residual
16.64 μm−4.164σ. Trece hashes/auditoría PASS y figura revisada. xtol con
gradientes altos, no óptimo certificado. Opacidades por nodo térmico más
próximo10 K comprobadas; sensibilidad por cuantificar. Sin nuevos retrievals,
datos, evidencias o ruido.
[Resultados y siguiente control](../docs/life_proxima_a3_pt_spectral_capacity_2026-10-14.md).

**2026-10-14 — binning y P–T autorizados; ruido excluido:** adaptador
diagnóstico separado con doce pruebas PASS, cierre de verdad2.265×10⁻¹⁴,
χ²32.978 vs314.519 anterior. Aproximación térmica Madhu con mismos priors
convergente en dos arranques; tres forwards P–T y química vertical fija
completados, RMS flujo8.437/10.137 %. Vector archivado reevaluado mediante
forward_model real: χ²542.643→365.856 sin optimización; no es nuevo mejor
ajuste. Diecinueve hashes y auditoría independiente PASS, figura revisada.
Sin nuevos retrievals, cambios de datos, ruido o código instalado.
[Método y productos](../docs/life_proxima_a3_binning_pt_controls_2026-10-14.md).

**2026-10-14 — controles híbridos N₂O/NH₃ y revisión de ruido:** tres
forwards A3 completados exit0, con PT/resto VULCAN intactos y promedios A3
constantes solo en los gases seleccionados. RMS relativos0.07382/0.01664/
0.07567 %, máximo conjunto0.871 veces σ1000 h; contratos/finitud/hashes
PASS, PNG/PDF revisados. Ruido vigente fotónico optimista; literatura LIFE
no fija un piso universal Proxima y no se altera el dataset. Los cuatro
retrievals1000 h cerraron exit0, incluida NH₃, pendiente auditoría científica.
[Método, productos y papers](../docs/life_proxima_a3_target_isochem_and_noise_budget_2026-10-14.md).

**Control autorizado 2026-10-14 — tres espectros A3:** generar vertical e
isochem promediado en presión, ambos con PT verdadero, comparar con LIFE
sin ruido guardado. Completado exit0; PT/especies/VMR/finitud/hashes PASS,
figura inspeccionada. Vertical/LIFE iguales a precisión numérica; isochem
promedio RMS22.28 %, máximo58.30 %. Cero retrievals, sin optimización ni
cambios de datos. Directorio diagnóstico independiente.
[Método, fuentes y productos](../docs/life_proxima_a3_vertical_life_isochem_comparison_2026-10-14.md).

**Diagnóstico 2026-10-14 — sin nuevas corridas:** cambio NH₃ 100→1000 h
investigado. Discrepancia instrumental generador/likelihood confirmada
RMS2.926σ/máximo8.986σ; origen principal recentering de bins, más ponderación.
Preflight previo no comprobaba likelihood real. No modificar productos,
implementar fix ni aceptar automáticamente; control coherente por autorizar.
[Resultados y pruebas](../docs/life_proxima_nh3_1000h_interface_diagnosis_2026-10-14.md).

**Figura descriptiva 2026-10-13:** posteriores completas A3 de N₂O/NH₃
en 1/10/100/1000 h frente a A0, sin nuevas corridas, PNG/PDF/JSON generados.
Finitud/priors/normalización PASS y revisión visual; 1000 h sigue preliminar.
[Procedencia y lectura](../docs/life_proxima_a3_posterior_enrichment_plot_2026-10-13.md).

**2026-10-13 — MPI5 autorizado para los tres A0 A3–1000 h:** completo
cerrado exit0, pendiente auditoría. Variantes reanudadas desde checkpoints
validados/respaldados con cinco ranks cada una; supervisor5062,
MPI5080/5090/5100, inicialización activa. Mismos modelos/dataset/scratch.
Logs vigentes `recovery_20261013_MPI5_R1/`; logs MPI3 inferiores históricos.
[Respaldo, alcance y verificación](../docs/life_proxima_a3_1000h_mpi5_resume_2026-10-13.md).

**Ampliación autorizada 2026-10-12 — cuatro A3–1000 h:** completo activo
MPI6 conservado; tres nuevas variantes N₂O/NH₃/ambas fijas a A0, MPI3 cada
una. Mismo dataset y opacidades; presupuesto global de quince ranks, con
cola si falta memoria. Campaña `a0_fixed_reference_A3_1000h_20261012`;
RUNNING desde 18:04:42 COT, supervisor 1139; preflight 3/3 PASS,
MPI 1208/1238/1271 con nueve ranks nuevos en carga de opacidades. Completo
MPI805 intacto, quince ranks totales. Supersede la exclusión histórica de A0 a 1000 h.
[Procedimiento y aceptación pendiente](../docs/life_proxima_a3_1000h_a0_comparison_2026-10-12.md).

**Recuperación A3–1000 h autorizada 2026-10-12:** interrupción confirmada;
checkpoint PASS en 2 646 212 evaluaciones, 800 puntos vivos y 29 hashes
intactos. R1 RUNNING desde 17:25:14 COT; supervisor 803, mpiexec 805 y seis
ranks 820–825 en inicialización, respaldo íntegro y protección duplicados PASS.
Mismo dataset, priors, scratch y MPI6 `--resume`. Log vigente de R1:
`native_grid_retry/recovery_20261012_R1/retrieval.log`; estado central en
`native_grid_retry/campaign_state.json`.
[Registro de recuperación](../docs/life_proxima_a3_1000h_checkpoint_resume_2026-10-12.md).

**Extensión autorizada 2026-10-11: A3–1000 h, un único completo.** Conserva
la configuración oficial A3–100 h, genera un dataset independiente con índice
separado y usa MPI6/N_live=800. No incluye A1, LOO, A0 fija ni cambio P–T.
Campaña `retrievals/a3_1000h_full_20261011/`; primer preflight FAIL por rejilla
numérica (0.7963/2.545 σ), sin muestreo. Control nativo PASS con diferencia
cero; preparación corregida en `native_grid_retry/` con rejilla 3–20 μm,
R=10000, física/priors/canales/dataset intactos. Fuente de verdad: estado,
manifiesto y configuración del intento corregido. **RUNNING desde 19:42:38 UTC**;
preflight PASS, un MPI6 activo e inicialización de opacidades verificada.
29 hashes protegidos intactos; productos pendientes de validación final.
[Procedimiento](../docs/life_proxima_a3_1000h_extension_2026-10-11.md).

La metodología completa, los priors, las realizaciones, resultados e
interpretación de la serie focal —incluidas las figuras de emisión, S/N
integrado/proyección y posteriores con perfiles verticales— están en
[`docs/life_proxima_a1_a3_1_10_100h_methodology_2026-10-03.md`](../docs/life_proxima_a1_a3_1_10_100h_methodology_2026-10-03.md).
La campaña de resultados y validación se conserva en
[`docs/life_proxima_a1_a3_1_10_100h_official_retrieval_campaign_2026-10-01.md`](../docs/life_proxima_a1_a3_1_10_100h_official_retrieval_campaign_2026-10-01.md).

La campaña LPJmL global A1 quedó completada y validada el 2026-09-20. El
informe de cierre es [`docs/lpjml_global_a1_validation_2026-09-20.md`](../docs/lpjml_global_a1_validation_2026-09-20.md).
El control natural A0 terminó y quedó validado; sus resultados y el contraste
`A0 + ΔF_agri` están en
[`docs/lpjml_global_a0_control_validation_2026-09-22.md`](../docs/lpjml_global_a0_control_validation_2026-09-22.md).
N2O queda próximo a la referencia congelada y NH3 requiere una decisión de
calibración antes del acoplamiento fotoquímico.

Preparación local 2026-09-07: recuperación del dataset LPJmL en Ubuntu sobre E:
y compilación con Open MPI completadas. Datos con `INPUTS_VERIFIED` a las
16:37 locales; smoke test MPI aceptado y seguimiento de descarga pausado;
la campaña global se lanzó después de aceptar el smoke test y quedó validada el
2026-09-20. [Registro de campaña](../docs/lpjml_global_a1_campaign_2026-09-07.md).

| Campaign | Status | Main evidence | Notes |
| --- | --- | --- | --- |
| LPJmL global A1 `global_a1_checkpoints_20260909` | **A1 y A0 validadas 2026-09-22** | `docs/lpjml_global_a1_validation_2026-09-20.md`, `docs/lpjml_global_a0_control_validation_2026-09-22.md`, `docs/lpjml_n2_nh3_partition_2026-09-22.md` | A1 y A0: 67,420 celdas/ocho ranks, salida 1996–2005, `exit_code=0`, máscaras/unidades/finitud y SHA-256 verificados. N2O agrícola queda próximo al incremento congelado; NH3 queda en 42.16 % y requiere decisión antes de VULCAN. |
| LPJmL MPI `mpi_smoke_20260907` | Interfaz aceptada: ocho celdas/dos ranks | `docs/lpjml_mpi_smoke_validation_2026-09-07.md`, `docs/evidence/mpi_smoke_20260907/` | Spin-up 47 s, A1 27 s; reinicio/NetCDF verificados, ocho pruebas aprobadas. Advertencias de entradas conservadas; no genera forzamiento planetario. |
| A0-A3 flux matrix | Current design | `README.md`, `Photochemical_Modeling/README.md` | Uses the perturbation equation `F_i(A_j) = F_i(A0) + alpha_i,j * Delta F_i,agri`; do not revive the old 10x/100x total-flux matrix as current. A2/A3 N2O are `3.416e9`/`1.238e10`. |
| Earth-Sun A0-A3 photochemistry | Accepted pre-correction benchmark | `Photochemical_Modeling/Results/Outputs/Earth_*.vul`, `docs/earth_sun_n2o_matrix_provenance_2026-07-20.md` | All four saved products reached `end_case = 1`; A2/A3 are the 2026-06-15 N2O realization (`3.35e9`/`1.20e10`), so not the current matrix without rerun or historical label. |
| TRAPPIST-1e A0-A3 photochemistry | Accepted with partial-convergence caveat | `Photochemical_Modeling/Results/Outputs/Trappist_*.vul`, `docs/vulcan_profile_reproduction_2026-06-15.md` | Products stopped with `end_case = 3`, but the remaining convergence signal is dominated by low-abundance trace chemistry. State this caveat explicitly. |
| TRAPPIST-1e forward spectra and retrievals | Active spectroscopy campaign | `Transmission_Spectroscopy/README.md`, `Transmission_Spectroscopy/notebooks/POSEIDON_output/TRAPPIST-1e/` | Interpret results conditional on the accepted TRAPPIST-1e partial-convergence caveat. |
| TRAPPIST-1e integrated molecular S/N | **Diagnostic executed 2026-09-22** | `docs/trappist1e_molecular_snr_by_instrument_2026-09-22.md`, `Transmission_Spectroscopy/final_products/trappist1e_molecular_snr_by_instrument.csv`, `Transmission_Spectroscopy/notebooks/plot_molecular_snr_instrument.py` | Primary metric integrates counterfactual `N2O`/`NH3` templates over the observed NIRSpec Prism and MIRI LRS grids for 1/10/100 transits. Diagonal uncertainties only; peak-based products remain legacy evidence. |
| Franck 2011 + LPJmL agricultural N first test | One-cell pilot and global A1/A0 accepted; FR-Genghis global crop-only CH4 candidate **paused by user on 2026-10-04**; final outputs pending | `docs/lpjml_franck2011_first_pilot_2026-09-06.md`, `docs/lpjml_franck_capacity_scenarios_design_2026-09-22.md`, `docs/lpjml_global_a1_validation_2026-09-20.md`, `docs/lpjml_global_a0_control_validation_2026-09-22.md`, `docs/lpjml_capacity_chunk_parallelism_2026-10-01.md`, `docs/fr_genghis_campaign_pause_2026-10-04.md`, `Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction/` | `pilot_20260907T031220Z`, `global_a1_checkpoints_20260909` and `a0_natural` completed. The five-block restart began 2026-10-02 21:55 COT with `MAX_PARALLEL=5`, `MPI_RANKS=1`, 8,000-cell blocks, CH4 and full checkpoint retention. On 2026-10-04 at 16:38 COT the user requested immediate termination; the verified scheduler, workers, checkpoint runners, MPI launchers and LPJmL processes were stopped. All five latest archived checkpoints matched controller hashes, sidecars and restart files and passed `lpjcheck -pedantic` with exit 0 (years 1566, 1494, 1494, 1484 and 1484). The campaign marker is `PAUSED_BY_USER`; no final exit codes or accepted products exist. No automatic restart until new user authorization. `river_routing=false`/`reservoir=false` limit interpretation to disabled local routing/reservoirs. |


### Revisión de sumideros NH3 (2026-10-13)

`nh3_surface_sinks_review_20261013`: **revisión y auditoría completadas;
sensibilidades propuestas sin ejecutar**. El
[informe](../docs/nh3_surface_sinks_huang_vulcan_review_2026-10-13.md) enlaza
el script y JSON de cuatro Earth `.vul` existentes. La velocidad efectiva
actual es `1 cm/s`; no resuelve un sumidero oceánico por separado. La
[revisión del origen del coeficiente](../docs/nh3_deposition_velocity_provenance_and_physical_scenarios_2026-10-13.md)
(`nh3_deposition_origin_review_20261013`) reemplaza la propuesta heurística
inicial. Hauglustaine no tabula NH3; Hu prescribe `1 cm/s` por
solubilidad/reactividad. El ancla marina de Lee (`0.5 cm/s`, rango preliminar
`0.2-1.5`) describe un componente regional, no un BC global medido.

`nh3_weakened_surface_sink_vdep_0p65_20261013`:
**diseño seleccionado, sin implementar ni ejecutar**. El
[diseño del único valor `0.65 cm/s`](../docs/nh3_weakened_surface_sink_vdep_0p65_design_2026-10-13.md)
retira `0.70*0.50=0.35 cm/s` de la referencia global, con una partición
idealizada que conserva captación terrestre y química oxidante. La
motivación es la proximidad del océano superficial al punto de compensación;
las fracciones y el residual terrestre son supuestos de proyecto. Falta
cerrar el presupuesto NHx y separar la emisión marina para una frontera
bidireccional física. No se generaron BC, atmósferas, espectros ni retrievals
nuevos. A0-A3 y las campañas activas mantienen su alcance.

`nh3_reduced_capture_extra_phase_20261013`:
**fase propuesta y documentada, sin implementar ni ejecutar**. La
[propuesta](../docs/nh3_reduced_capture_extra_phase_proposal_2026-10-13.md)
define cuatro candidatos `A0-A3_NH3D065` por entorno futuro, comparados
con referencias emparejadas a `1 cm/s`. Conserva los flujos NH3/N2O y demás
entradas dentro de cada pareja; A0 debilitado es control contrafactual.
Incluye evaluación de plausibilidad condicionada, diagnóstico lineal
`1/0.65=1.538` y límites de inferencia ambiental. Entorno y campaña de
ejecución pendientes; ningún producto nuevo ni cambio de campaña activa.

### Campaña de retrievals Stage III

**Actualización vigente (2026-10-02):** A1-1 h oficial usa seed 2125532119,
seleccionado después de revisar ambas posteriores (decisión post hoc); seed
368516754 queda como sensibilidad preservada. La matriz amplia A0--A3 ×
{10 h, 240 h} está archivada como legacy y no define el contraste focal
A1/A3 × {1, 10, 100 h}. Véanse el [informe de campaña](../docs/life_proxima_a1_a3_1_10_100h_official_retrieval_campaign_2026-10-01.md)
y la [revisión de la realización A1-1 h](../docs/life_proxima_a1_1h_independent_noise_repeat_2026-10-02.md).

| Campaign | Status | Main evidence | Notes |
| --- | --- | --- | --- |
| `life_retrieval_matrix_2026-07-25` | **Histórica/legacy para el contraste focal vigente; 8/8 preservada** | `docs/life_stage_iii_integrated_methodology_results_2026-08-30.md`, `docs/life_stage_iii_classic_methodology_2026-08-30.md`, `docs/life_retrieval_campaign_design_2026-07-25.md`, `docs/lifesim_classic_stage_iii_validation_2026-08-30.md`, `Thermal_Emission_Spectroscopy/outputs/*/life_data/dataset_index.json` | Los ocho retrievals A0--A3 × {10 h, 240 h} y sus datasets se conservan como evidencia histórica. Ya no definen la comparación oficial A1/A3 a 1/10/100 h. Mantener sus priors `Piette20` y supuestos separados; sigma diagonal/una semilla sigue siendo una cota optimista frente a LIFEsimMC/PHRINGE y múltiples realizaciones. |
| Retrievals Proxima A1 corregidos, 10/100 h | **Validados; forman el brazo 10/100 h de la serie oficial A1/A3 1/10/100** | `docs/life_proxima_a1_10_100h_o2_fixed_surface_audit_2026-09-29.md`, `Thermal_Emission_Spectroscopy/scripts/audit_proxima_a1_mpi_retrievals.py`, figura y resumen `retrieval_A1_10_100h_MPI6R1_posteriors_PT_proxima` | POSEIDON/MPICH, O2, superficie negra fija a 1 bar, `R=10000`, `N_live=800`, `isochem`, sin `x_tol` ni inflación, ruido diagonal. MPI6R1 cerró con `exit_code=0`; `χ²_red=1.55/3.18` (16 dof). N2O se estrecha a 100 h, sin separación formal A1/A0. A1-100 h es realización independiente (seed `460512527`); se preservan dataset 10 h y checkpoints fuente. |
| Retrievals Proxima A1/A3 oficiales, 1/10/100 h | **Completados y validados; subcampaña clásica cerrada; V2 oficial 2026-10-03** | `docs/life_proxima_a1_a3_1_10_100h_official_retrieval_campaign_2026-10-01.md`; revisión `dataset_index_A1_A3_1h_official_revision_20261002.json`; figura `retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima` | Configuración común: `isochem`, O2, superficie negra fija a 1 bar, `R=10000`, `N_live=800`, 31 bins LIFE, ruido diagonal, sin `x_tol` ni inflación. A1-1 h oficial es la realización independiente seed 2125532119 (337,319 evaluaciones; 7,334 muestras; `χ²_red=1.10`, 16 dof); seed 368516754 se conserva como sensibilidad. La decisión fue post hoc. V2 (perfiles+posteriores dentro del prior) es salida por defecto; V1 prior-completo y V3 posterior-only siguen preservadas. El atlas muestra perfiles VULCAN A1/A3 en las tres filas, A0 efectiva y valores `q50=...; z=...`; el P--T VULCAN es negro discontinuo y no lleva una clave redundante. Los seis productos pasan validación; la matriz A0--A3 × {10 h, 240 h} permanece intacta como legacy. Stage III global conserva pendientes instrumentales. |

### Evidencia de auditoría de Stage III

**Exportaciones del atlas oficial vigente (28-oct; N₂O/NH₃ primero, sin P–T):** [PNG](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_posteriors_N2O_NH3_first_no_PT_proxima_20261028.png), [PDF](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_posteriors_N2O_NH3_first_no_PT_proxima_20261028.pdf), [SVG](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_posteriors_N2O_NH3_first_no_PT_proxima_20261028.svg) y [procedencia](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_posteriors_N2O_NH3_first_no_PT_proxima_20261028.provenance.json). [Informe](../docs/life_proxima_corrected_binning_full_posteriors_plot_2026-10-28.md).

| Producto | Clasificación | Evidencia | Regla de uso |
| --- | --- | --- | --- |
| Datasets Proxima A0--A3 de 1200 h + retrieval A3--1200 h | **Piloto/auditoría, excluido** | `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/README.md` | Preservar como evidencia de los fallos y correcciones del retrieval a S/N alto; no contar en la matriz 8/8 ni usar en claims canónicos. |
| Dataset y retrieval Proxima A3--500 h | **Piloto/auditoría, excluido (2026-08-31)** | `docs/life_proxima_a3_500h_retrieval_audit_2026-08-31.md`, `docs/life_proxima_a3_500h_lifesim_direct_validation_2026-08-31.md`, `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/dataset_index_500h_lifesim_direct_audit.json` | Corrida estable con PT Madhu + `Piette20` + prior físico de `R_p_ref`. El retrieval se lanzó inicialmente con sigma escalada; LIFEsim 0.2.32 directo produjo después un dataset byte a byte idéntico, por lo que no se duplicó MultiNest. No altera la matriz canónica ni el atlas oficial. |
| Retrievals robustos Proxima A3--500/1200 h | **Piloto/auditoría, excluido (2026-08-31)** | `docs/life_proxima_a3_500h_1200h_robust_retrieval_2026-08-31.md`, `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/dataset_index_500_1200h_robust_lifesim_direct_audit.json`, `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/` | Datasets directos de LIFEsim, `N_live=800`, PT Madhu, `isochem`, `Piette20` y prior físico de radio. 500 h: `ln Z=901.17`, `chi^2_red=2.07`; 1200 h: `ln Z=898.31`, `chi^2_red=2.82`. Ambos tienen posteriores completos; no cuentan en la matriz canónica ni sustentan claims de detección. |
| Retrievals Proxima A3--10/240 h con `fixed-bottom` heredado, sin `x_tol` | **Auditoría completada (2026-09-23), excluida** | `docs/life_proxima_a3_10_240h_fixedp1bar_noxtol_audit_2026-09-23.md`, `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/`, `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A3_molecular_posteriors_audit_comparison_proxima.png`, `Thermal_Emission_Spectroscopy/scripts/plot_proxima_a3_molecular_posteriors.py` | `isochem`, `N_live=800`, `error_inflation=none`, `surface=False` y malla hasta 1 bar; **no** equivale a superficie negra explícita. 10 h: `ln Z=888.98`, `chi^2_red=1.43`; 240 h: `ln Z=816.05`, `chi^2_red=13.07`. La precisión aparente de N2O a 240 h no es detección ni reemplaza la matriz 8/8. |
| Dataset/retrieval Proxima A3--100 h con `fixed-bottom` heredado, sin `x_tol` | **Auditoría completada; excluida** | `docs/life_proxima_a3_100h_fixedp1bar_noxtol_audit_2026-09-23.md`, índice de dataset `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/dataset_index_A3_100h_fixedP1bar_noxtol_audit.json`, `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A3_audit_profiles_posteriors_10_100_240h_proxima.png` y `.pdf` | `N_live=800`, `isochem`, sin inflación, sin `x_tol`, `surface=False`; dataset de 31 bins y una realización. 100 h: `ln Z=877.05±0.24`, `chi²_red=5.27` (18 dof), `z_N2O=+4.69`, `z_NH3=+3.04` frente a A0 efectiva. Los z son descriptivos bajo un desajuste de interfaz; no son detecciones ni factores de Bayes entre tiempos. Matriz canónica 8/8 intacta. |
| Residuos A3--10/100/240 h, modo `fixed-bottom` heredado y sin x_tol | **Auditoría postproceso completada (2026-09-23), excluida** | `docs/life_proxima_a3_retrieval_residuals_2026-09-23.md`, `Thermal_Emission_Spectroscopy/scripts/audit_proxima_a3_retrieval_residuals.py`, figura y CSV/JSON `retrieval_A3_fixedP1bar_noxtol_residual_audit_10_100_240h` en `outputs/life_proxima_b_earthlike_v1/{plots,tables}/` | El rebin de fotones reproduce la verdad LIFE (`2.28e-14`); el desajuste entre forward A3 y mediana recuperada se repite entre 100/240 h (`r=0.974`). No se ejecutaron retrievals nuevos; la prueba posterior identificó diferencias de superficie y O2. |
| Forwards controlados Proxima A3 a 100/240 h | **Auditoría de interfaz completada (2026-09-23), excluida** | `docs/life_proxima_a3_forward_swap_audit_2026-09-23.md`, `Thermal_Emission_Spectroscopy/scripts/diagnose_proxima_a3_forward_swaps.py`, `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/forward_swap_audit/` | El forward original se reproduce exactamente. `surface=False` y omitir O2 generan cambios grandes y parcialmente compensados incluso con PT/química verdaderas; los z A3--A0 de la auditoría no sustentan un tiempo de distinción. Sin MultiNest nuevo ni cambios canónicos. |
| Retrieval Proxima A3--100 h con O2 y superficie negra explícita | **Auditoría cerrada 2026-09-26; excluida de 8/8** | `docs/life_proxima_a3_100h_o2_fixed_surface_audit_2026-09-23.md`, `Thermal_Emission_Spectroscopy/scripts/postprocess_existing_proxima_a3_100h_o2.py`, `Thermal_Emission_Spectroscopy/scripts/plot_proxima_a3_100h_o2_surface_recovery.py`, log y productos bajo `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/` | Forward validado a RMS 0.2518 y máximo 0.8048 sigma/bin (`R=10000`). MultiNest cerró con 1,804,581 evaluaciones, `ln Z=884.33±0.24`; Analyzer falló al buscar `.dat`, así que se recuperó de la muestra ya escrita sin repetir muestreo. Posterior: `chi²_red=4.94` (16 dof), `R_p_ref=1.2202±0.0062 R_⊕`; `z_N2O=+13.24`, `z_NH3=+5.63` descriptivos frente a A0 efectiva, no detecciones formales. Figura corregida/legacy y residuos: `outputs/life_proxima_b_earthlike_v1/plots/retrieval_A3_100h_legacy_vs_o2_fixed_surface_recovery_proxima.png` y `.pdf`; los `ln Z` no son factor de Bayes entre configuraciones. |
| Retrieval corregido Proxima A3--10 h con O2 y superficie negra explícita | **Auditoría cerrada 2026-09-28; excluida de 8/8** | `docs/life_proxima_a3_10h_o2_fixed_surface_audit_2026-09-27.md`, `Thermal_Emission_Spectroscopy/scripts/postprocess_existing_proxima_a3_10h_o2.py`, `Thermal_Emission_Spectroscopy/scripts/plot_proxima_a3_o2_fixed_surface_10_100h.py`, figura y tablas `retrieval_A3_10_vs_100h_o2_fixed_surface_proxima` bajo `outputs/life_proxima_b_earthlike_v1/{plots,tables}/` | MultiNest completó 1,201,886 evaluaciones (`ln Z=890.97±0.21`); el wrapper falló en Analyzer porque POSEIDON duplicaba el tag del modelo y retrieval, truncando la raíz a 100 caracteres (`.d`/sin extensión). Copia byte-idéntica y postproceso sin nuevo muestreo; el runner ya evita esa duplicación. 10 h: `chi²_red=1.28` (16 dof), `z_N2O=+5.59`, `z_NH3=+0.85`; 100 h: `chi²_red=4.94`, `z_N2O=+13.24`, `z_NH3=+5.63`. Distancias condicionales bajo perfil isochem y ruido diagonal de realizaciones independientes; no detección ni comparación de ln Z como Bayes factor. |
| Perfil PT recuperado Proxima A3--10/100 h | **Chequeo de compatibilidad completado 2026-09-29; auditoría excluida** | `docs/life_proxima_a3_10h_o2_fixed_surface_audit_2026-09-27.md`, `Thermal_Emission_Spectroscopy/scripts/plot_proxima_a3_retrieved_pt_comparison.py`, `outputs/life_proxima_b_earthlike_v1/plots/retrieval_A3_recovered_PT_10_vs_100h_proxima.png` y `tables/retrieval_A3_recovered_PT_10_vs_100h_proxima_summary.json` | Contra el PT VULCAN A3 del manifiesto, RMS `T_mediana−T_VULCAN` = 32.71/60.36 K a 10/100 h; la anchura mediana marginal 68% es 43.40/20.61 K y la referencia queda dentro de bandas 2σ en 54.6%/9.3% de 97 niveles comunes. Bandas por presión son punto-a-punto, no simultáneas. La mayor discrepancia a 100 h respalda la cautela por adecuación del modelo; no identifica por sí sola la fuente de la tensión. |
| Prueba de perfil vertical NH3 A3--500 h | **Auditoría/diagnóstico, excluida (2026-09-01)** | `docs/life_proxima_a3_500h_nh3_two_gradients_2026-09-01.md`, `Thermal_Emission_Spectroscopy/scripts/run_life_retrieval.py`, `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/` | Mismo dataset directo; `Madhu` + `Piette20`, `N_live=1000`, `X_profile=two-gradients` solo para NH3. `ln Z=895.86`, `chi^2_red=3.15`; no mejora el isquímico (`ln Z=901.17`, `chi^2_red=2.07`) bajo estos priors. |
| Ensayo de ruido directo frente a escalado temporal | **Auditoría cerrada (2026-08-31)** | `docs/life_proxima_lifesim_noise_scaling_2026-08-31.md`, `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/lifesim_noise_scaling_comparison.csv` | A0/A3, 1--1200 h, 31 bins: la llamada directa y `sigma(10 h)*sqrt(10 h/t)` coinciden a nivel de coma flotante. Confirma el atajo para LIFEsim clásico; no evalúa covarianza ni ruido instrumental temporal de LIFEsimMC/PHRINGE. |

| Diagnósticos de Bayes factor Proxima A3--240 h | **Experimento de auditoría ejecutado (2026-09-01)** | `docs/life_proxima_bayes_factor_diagnostics_2026-09-01.md`, `Thermal_Emission_Spectroscopy/scripts/evaluate_life_bayes_factor_diagnostics.py`, `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/life_bayes_factor_diagnostics_A3_240h.csv` | Plantillas fijas sobre el mismo dataset A3: `ln B(A3/A0)=394.35` y `ln B(A3/N2O-reset)=385.63`. Diagnóstico de likelihood/Bayes factor sin nuisance parameters; no sustituye la comparación marginalizada ni la validación LIFEsimMC/PHRINGE. |

## Ramas de campaña Stage III

Diagnóstico adicional completado el 2026-10-02: [S/N molecular LIFE Proxima
A1/A3 a 1/10/100 h](../docs/life_proxima_lifesim_snr_a1_a3_1_10_100h_2026-10-02.md).
Reutiliza el producto directo LIFEsim de 10 h, valida sigma contra los seis
datasets existentes y conserva fuera de alcance cualquier afirmación de
covarianza instrumental o detección.

| Campaign | Status | Main evidence | Notes |
| --- | --- | --- | --- |
| `life_earth_sun_10pc` thermal-emission observability | Interface benchmark executed (classic branch); LIFEsimMC branch pending | `docs/life_earth_sun_10pc_interface_snr_2026-07-22.md`, `Thermal_Emission_Spectroscopy/outputs/life_earth_sun_10pc_interface_v1/` | Campaign `life_earth_sun_10pc_interface_v1`: POSEIDON emission A0--A3 + N2O/NH3 counterfactuals + LIFEsim-classic S/N. Interface validated (blackbody check PASS); ExoFarm signal below noise at LIFE baseline/10 pc (best peak N2O 7.82 µm). Pre-correction profiles (`earth_20260615_pre_n2o_correction`) — NOT the current matrix. Instrumental noise/covariance (LIFEsimMC/PHRINGE) and any retrieval still pending; SNR is a diagnostic, not a detection. |
| `life_proxima_b_earthlike` | **Executed 2026-07-23** (classic branch); LIFEsimMC pending | `docs/life_proxima_b_branch_bitacora_2026-07-22.md`, `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/` | Campaign `life_proxima_b_earthlike_v1`: MUSCLES v22 SED → VULCAN surface flux (bolometric 1.037) → VULCAN Proxima A0--A3 **all end_case=1** (corrected BC, terrestrial PT) → POSEIDON emission + N2O/NH3 counterfactuals → LIFE X-scene S/N. Result: ExoFarm A3 N2O reaches S/N=5 in ~11--32 h (vs years for Earth--Sun @10pc) — ~30--65x more detectable, a proximity effect. Controlled M-environment analogue, NOT Proxima b's measured atmosphere. SNR is a diagnostic, not a detection. |
| Proxima LIFE A1/A3 official retrieval series (1/10/100 h) | **Completed; A1-1 h revised 2026-10-02** | `docs/life_proxima_a1_a3_1_10_100h_official_retrieval_campaign_2026-10-01.md`; current input index `dataset_index_A1_A3_1h_official_revision_20261002.json`; launch/preparation scripts listed in the campaign report | POSEIDON/MPICH, MPI6 per scenario, O2, black surface fixed at 1 bar, `R=10000`, `N_live=800`, `isochem`, no `x_tol` or error inflation, LIFE 31-bin diagonal noise. The 2026-10-01 index records the initial 1 h generation (A1 seed `368516754`, A3 `1376328125`). Following the 2026-10-02 project decision, A1 seed `2125532119` is the current official 1 h realization; seed `368516754` remains a preserved sensitivity product. This promotion was post hoc after posterior inspection. The revision index is separate from canonical 8/8; the initial index and all products remain preserved. All six focal retrievals passed product validation. |
| Proxima LIFE A1/A3 official comparison figure (1/10/100 h) | **V2 promoted to final products 2026-10-03; alternatives preserved; 8/8 intact** | Final `Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima` (PNG/PDF/SVG); reproducible source and V1/V3 under `outputs/life_proxima_b_earthlike_v1/plots/`; script flags `--official-a1-a3-times`, `--official-a1-a3-times-full-prior-xlim`, `--official-a1-a3-times-posterior-xlim` | Compact full-width atlas; each PDF/SVG is vector (PDF 7.287×5.232 in) and each PNG 2187×1569 at 300 dpi, visible labels ≥6 pt; six species plus P–T (O2 remains retrieved). Each molecular header shows A0 once; colored labels below every panel state `q50=...; z=...`, and one unboxed equation defines descriptive z relative to effective A0. Histograms have unit area and are shown as dex⁻¹ densities; each panel has an independent auto-scaled y-axis, so peak heights are not compared across rows. Official V2 fits profiles+posterior samples and clamps xlim to `[-12,-1]`; V1 retains the full prior under `_full_prior_xlim`; V3 fits xlim from posterior samples only under `_posterior_xlim`, with the same prior clamp. Profiles outside a view are clipped visually. Molecule headers sit close to their axes, horizontal rules separate exposure rows, and q50/z lines sit below each plot with the x-label close to the final row. VULCAN abundance profiles appear in all rows; input VULCAN P–T is black/dashed, with recovered bands colored by scenario. The global legend omits P–T entries and the gray footer. χ²red and ln Z remain in the campaign report. A1-1 h seed 2125532119 is selected post hoc; seed 368516754 remains sensitivity. |
| A1 1 h previous realization (seed 368516754) | **Preserved sensitivity comparison** | `docs/life_proxima_a1_1h_independent_noise_repeat_2026-10-02.md`; previous dataset/retrieval and `plots/retrieval_A1_1h_selected_official_vs_previous_N2O_NH3_PT_proxima` PNG/PDF | Same signal, bins and sigma as the selected A1 realization but a different diagonal-noise draw. Both posterior results are retained; `ln Z` across these independent datasets is not a Bayes factor. Seed 2125532119 was selected after posterior review (post hoc); multiple realizations are needed to assess coverage and robustness. |
| LIFE integrated molecular S/N | **Diagnostic ejecutado 2026-09-22** | `docs/life_classic_snr_integrated_2026-09-22.md`, `Thermal_Emission_Spectroscopy/final_products/life_classic_snr_integrated_proxima.csv`, `Thermal_Emission_Spectroscopy/scripts/plot_emission_snr_integrated.py` | Full-grid diagonal S/N over the saved classic LIFE bins. The upper panel has two molecules because each campaign uses one instrument; the lower panel marks A3 hours for S/N=3/5. Peak-per-feature products remain legacy; LIFEsimMC/PHRINGE covariance is pending. |

La actualización visual del 2026-08-30--31 regeneró los PNG de espectro, señal,
comparación SNR/proyección y el atlas de retrieval de esta campaña. La última
revisión amplió los puntos observados con barras de error y recolocó la fórmula
de distancia del atlas, sin cambiar los datos ni los retrievals. La
comparación SNR/proyección y el atlas oficial V2 de retrieval están promovidos
en PNG/PDF (y SVG para el atlas) a
`Thermal_Emission_Spectroscopy/final_products/figures/`. Los fuentes
reproducibles y las alternativas V1/V3 siguen en
`Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/`;
los scripts y productos de entrada permanecen en la ruta de la campaña. No se
modificó la matriz científica.

## Comparación molecular LOO LIFE Proxima (completada y auditada; 2026-10-10)

La matriz de 36 ablaciones individuales de H₂O, CO₂, CH₄, O₃, N₂O y NH₃ en
A1/A3 y 1/10/100 h está cerrada. Cada evidencia compara un retrieval sin X con
el retrieval completo oficial usando exactamente el mismo archivo LIFE y la
misma realización de ruido. La métrica principal es
`ln B = lnZ(completo) − lnZ(sin X)` dentro de cada pareja; no se comparan
evidencias entre tiempos, escenarios o realizaciones distintas. La columna de
sigma Sellke del informe es solo una cota auxiliar, no una significancia de
detección.

Resultado operativo: 36/36 corridas terminaron con código 0 y 36/36 preflight
pasaron con 14 parámetros. El auditor validó posterior, espectro, P–T, log-X,
archivos MultiNest y finitud en los 36 directorios; también contrastó los seis
modelos completos y verificó los SHA-256 de cada dataset compartido. El estado
confirma reutilización de los seis retrievals completos y
`canonical_8of8_modified=false`. No quedan procesos, celdas pendientes ni
reintentos.

La tabla final y la interpretación están en el
[informe LOO](../docs/life_proxima_molecular_ablation_loo_2026-10-04.md). Los
productos de máquina son [`loo_results_validated_20261010.csv`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/molecule_ablation_loo_20261004/loo_results_validated_20261010.csv)
y [`validation_report_20261010.json`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/molecule_ablation_loo_20261004/validation_report_20261010.json); la visualización final es
[`life_proxima_molecular_ablation_loo_lnB_2026-10-10.svg`](../Thermal_Emission_Spectroscopy/final_products/figures/life_proxima_molecular_ablation_loo_lnB_2026-10-10.svg).
La tabla de reporte vigente añade sigma calibrado con las ecuaciones (8)–(9)
de Benneke & Seager citadas por Lin et al., y usa `N/A` para `ln B ≤ 0`:
[método y tabla completa](../docs/life_proxima_loo_sigma_lin_convention_2026-10-10.md),
[CSV oficial](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_loo_lnB_sigma_lin_2026-10-10.csv).
Se verificaron 27 cifras calibradas y nueve `N/A`; el CSV original firmado se
preserva como histórico. Este posproceso no ejecutó ningún retrieval.
La auditoría se reproduce con
[`validate_proxima_molecular_ablation_loo.py`](../Thermal_Emission_Spectroscopy/scripts/validate_proxima_molecular_ablation_loo.py).
La caída eléctrica y la continuación de dos checkpoints con `--resume` quedan
registradas en el [log de recuperación](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/molecule_ablation_loo_20261004.resume_20261010_power_recovery.log);
ese registro es histórico y no indica actividad actual.

## Legacy campaigns

| Campaign | Status | Main evidence | Notes |
| --- | --- | --- | --- |
| 10x/100x total-flux sensitivity | Legacy sensitivity | `Photochemical_Modeling/Config/Boundary_Conditions/legacy_10x_100x/` | Superseded by the current perturbation matrix. |
| Combined Earth/TRAPPIST photochemistry label | Superseded bookkeeping | Current stage READMEs | Split conceptually into Earth-Sun accepted steady state and TRAPPIST-1e accepted partial convergence. |
| Root `output/` figures | Archived legacy figures | `output/` | Do not add new products here. |

## Contraste LIFE con A0 efectiva — 2026-10-10

Auditoría 2026-10-11: 3/3 exit 0 y campaña sin procesos activos. Productos
primarios/priors/hashes/evidencias PASS; finitud estricta FAIL en desviaciones
derivadas de coordenadas fijas de N₂O/conjunta (`NaN` en stats/summary).
Tabla final ln B `29.440/1.170/31.103`, sigma `7.96/2.12/8.17`.
Cierre autorizado por el usuario: `ACCEPTED_WITH_FIXED_MOMENT_SALVEDAD`,
siete momentos auxiliares estables, 52 hashes originales intactos y
13 controles PASS. Finitud estricta false conservada; no se repite muestreo.
Monitor eliminado tras verificar el cierre.
[Informe de auditoría, tabla y salvedad](../docs/life_proxima_a3_100h_a0_fixed_audit_2026-10-11.md).
[Síntesis de las 45 corridas focales y conclusión ExoFarm/LIFE](../docs/life_proxima_exofarm_retrieval_layers_synthesis_2026-10-11.md).

Nueva rama autorizada: `a0_fixed_reference_20261010`. Análisis posterior
ejecutado (12 filas marginales y seis conjuntas); referencia VULCAN y hashes
congelados, priors fijos implementados y 18 celdas candidatas preparadas.
El usuario seleccionó exclusivamente **A3-100 h**, individual y conjunto:
tres corridas, las otras 15 fuera del alcance. Cola lanzada 2026-10-10
19:05 COT con máximo dos MPI6, reutilizando el mismo dataset/completo
oficial A3-100 h. Preflight PASS; supervisor PID 758 y MPI6 PID 779/783
en el arranque, conjunta inicialmente en cola. Los tres casos están cerrados;
estos PID describen únicamente el historial, sin procesos activos al cierre.
Registro de metodología,
productos, pruebas y aceptación:
[informe A0](../docs/life_proxima_a0_enrichment_methodology_2026-10-10.md).
La comparación requiere valores A0 no nulos; conserva las opacidades.

## Adding a campaign

Add one row to the relevant table and link the report or stage README that
explains the scientific question, inputs, commands, products, result, and
limitations. Keep this file short; detailed interpretation belongs in `docs/`.

## Cleanup

Potential deletions are listed in `cleanup.md`. Do not delete scientific
products merely because they are old or imperfect; preserve enough evidence for
a colleague to understand what was done and why a product was superseded.

### LIFE noise curves on emission signals (2026-10-27)

The [Proxima A0–A3 figure with LIFE A3 at 1/10/100 h](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/emission_molecular_residuals_proxima_LIFE_A3_1_10_100h.png)
shows the three existing 31-channel datasets as ±1σ curves in the lower
N₂O/NH₃ signal panels; the upper emission spectra remain clear. No new campaign
was started. See the [reproducible report](../docs/life_proxima_emission_spectra_with_life_data_2026-10-27.md).

### JWST noise curves on signal panels (2026-10-27)

The [TRAPPIST-1e figure with synthetic JWST noise](../Transmission_Spectroscopy/notebooks/POSEIDON_output/pure_spectra/plots/trappist1e_jwst_transit_count_observations_A3.png)
shows ±1σ for NIRSpec PRISM and MIRI LRS at 10/20/100 transits in the lower
N₂O and NH₃ panels. The signal limits are fixed and clipped curves are
identified; the upper panel remains unchanged. These are synthetic
uncertainties, not observations. The [reproducible report](../docs/trappist1e_jwst_noise_curves_signal_panels_2026-10-27.md)
records units, limits, and provenance.

> **Reanudación de campaña 2026-09-19 04:53 America/Bogota:** A1 global autorizado reanudado desde el checkpoint validado de 1738 con ocho ranks y el build `LPJmL-6.0.6-balance-fix-20260912`. El spin-up natural ya estaba completado. Se repetirán los años 1739–1742 perdidos tras la última copia y se conservarán nuevos checkpoints. Aún no hay flujos científicos aceptados.


**Resguardo LIFE Proxima (2026-11-14):** 480 insumos vigentes verificados y copia independiente de emisión, documentación y registros en E:, con 2941 archivos cotejados por SHA-256. Dependencias externas pendientes. [Alcance y comprobación](../docs/life_proxima_resguardo_resultados_vigentes_2026-11-14.md).

**Mapa de flujo LIFE (2026-11-14):** dependencias vigentes y campañas históricas candidatas a auditoría; no mover ni borrar hasta completar referencias. [Mapa](../docs/life_proxima_mapa_flujo_y_custodia_2026-11-14.md).

**Organización LIFE (2026-11-14):** guía de lectura e inventarios de campañas e imports; depuración de dependencias externas y referencias cruzadas pendiente. [Inventario y decisiones](../docs/life_flujo_inventario_decisiones_2026-11-14.md).

**Alcance LIFE indicado por el usuario (2026-11-14):** priorizar flujo corregido A1/A3 1/10/100 h; 1000 h y ablaciones antiguas fuera del foco. El script integrado aún los consulta; desacoplar y verificar antes de proponer bajas exactas. [Decisión](../docs/life_flujo_inventario_decisiones_2026-11-14.md).

**LIFE 1/10/100 h (2026-11-14):** análisis centrado reproducido, 42 modelos y 36 LOO, 11 tablas idénticas a la edición de 29-oct; 1000 h y comparación antigua fuera de los 446 insumos. [Procedencia y límites](../docs/life_proxima_flujo_1_10_100h_2026-11-14.md).

**Auditoría 1000 h (2026-11-14):** cinco campañas históricas identificadas; flujo centrado independiente, consumidores históricos aún referencian sus rutas. [Auditoría](../docs/life_proxima_auditoria_1000h_2026-11-14.md).
