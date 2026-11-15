**FR-Genghis, seguimiento 2026-10-04 15:57 COT:** la campaña continúa en POTENTIAL_CHUNKS_RUNNING, con cinco bloques de 8.000 celdas, salida CH4, un rank MPI por bloque, MAX_PARALLEL=5 y MAX_ARCHIVED_CHECKPOINTS=0. Los cinco LPJmL, cinco mpirun -np 1, cinco checkpoint_runner y el scheduler siguen activos. No hay códigos finales ni productos aceptados.

El bloque 00000_07999 guardó el checkpoint 1791096968589529619.lpj, SHA-256 3558df2823e16b0e75da872c64c07afffa62ae65334e01a5f09bd30045f0934a. El archivo archivado y chunks/00000_07999/restart/checkpoint.lpj coinciden byte a byte (cmp=0). lpjcheck -pedantic terminó con exit 0, reportó las advertencias conocidas de entorno/insumos y aceptó el restart desde el año 1566; el proceso continúa en un segmento nuevo.

Los otros SHA-256 de controller, archivo archivado y restart coinciden: 08000_15999 8b3bdde51ef3348ef0309c17bda51de83f7d6a71307261f46670323cd63a8110; 16000_23999 8320adbef33619710eada5a49c9c87522116b4ded3b100e9580b38dd87d88605; 24000_31999 0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa; 32000_39999 dc6f24a5fc1adb6fc9c56703f664ca75590d7986c25eb90981b7bb9a4dbf3864. Las últimas filas anuales visibles son 1565, 1494, 1493, 1485 y 1485, respectivamente. Los stderr revisados muestran advertencias conocidas y no reportan un error fatal actual. El traceback LPJmL exit 137 que sigue presente en controller.stderr.log de 00000_07999 corresponde al incidente histórico del 2026-10-01; el proceso de la generación actual está activo.

Los cinco modelos usan aproximadamente 39,7–40,0% de CPU cada uno. free -h informa 12 GiB disponibles y swap ocupada en 7,0/8,0 GiB, con 1,0 GiB libre; /home conserva 498 GiB libres. vmstat registró actividad pequeña en la primera muestra y si/so=0 en las cuatro muestras de intervalo posteriores, sin intercambio sostenido observado. La reserva de swap mejoró frente a la revisión anterior; mantengo MAX_PARALLEL=5.

La configuración conserva river_routing=false y reservoir=false, por lo que la interpretación sigue limitada al routing local desactivado.

**FR-Genghis, seguimiento 2026-10-04 14:56 COT:** campaign_status.txt continúa como POTENTIAL_CHUNKS_RUNNING. Los cinco bloques de 8.000 celdas siguen activos con un rank MPI cada uno, salida CH4, MAX_PARALLEL=5 y retención completa; siguen vivos los cinco LPJmL, cinco mpirun -np 1, cinco checkpoint_runner y el scheduler. No hay códigos finales ni productos aceptados. No se guardó checkpoint nuevo desde la revisión de 13:55 COT.

Los últimos SHA-256 reportados por los controladores siguen coincidiendo con el restart/checkpoint.lpj y el último archivo archivado de cada bloque (cmp=0): 00000_07999 c59f10b4ee452d24259ae591ede142485bdc26413dbd381c758222ba9e1cfd6d; 08000_15999 8b3bdde51ef3348ef0309c17bda51de83f7d6a71307261f46670323cd63a8110; 16000_23999 8320adbef33619710eada5a49c9c87522116b4ded3b100e9580b38dd87d88605; 24000_31999 0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa; 32000_39999 dc6f24a5fc1adb6fc9c56703f664ca75590d7986c25eb90981b7bb9a4dbf3864. El checkpoint de 08000_15999 conserva la validación previa lpjcheck -pedantic: exit 0 y restart desde año 1494. Las últimas filas anuales visibles siguen en 1565, 1494, 1493, 1485 y 1485, respectivamente; los procesos permanecen activos.

Los LPJmL usan alrededor de 40% de CPU cada uno. free -h informa 11 GiB disponibles; la swap está ocupada en 8,0/8,0 GiB, con 8 KiB libres; /home conserva 499 GiB libres. vmstat 1 5 mostró 3 KiB/s de swap-in y 269 KiB/s de swap-out en la línea inicial, 8 KiB/s de swap-out en el primer intervalo medido y si/so=0 en los tres intervalos siguientes. No se observa intercambio sostenido durante esa muestra, aunque la reserva de swap está agotada. Mantengo MAX_PARALLEL=5 y no cambio los procesos. Los stderr recientes contienen advertencias conocidas, sin error fatal nuevo. El exit 137 que permanece en controller.stderr.log de 00000_07999 corresponde al incidente histórico del 2026-10-01; el LPJmL actual sigue activo.

La configuración conserva river_routing=false y reservoir=false; la interpretación queda limitada al routing local desactivado.

**FR-Genghis, seguimiento 2026-10-04 13:55 COT:** la campaña global de selección de cultivos continúa activa, con bloques de 8.000 celdas, salida CH4, un rank MPI por bloque, MAX_PARALLEL=5 y MAX_ARCHIVED_CHECKPOINTS=0. campaign_status.txt conserva POTENTIAL_CHUNKS_RUNNING; los cinco LPJmL, cinco mpirun -np 1, cinco checkpoint_runner y el scheduler siguen activos. No hay códigos finales ni productos aceptados.

El bloque 08000_15999 guardó el checkpoint 1791093519616755527.lpj. Su SHA-256 es 8b3bdde51ef3348ef0309c17bda51de83f7d6a71307261f46670323cd63a8110; coincide entre el archivo archivado y chunks/08000_15999/restart/checkpoint.lpj (cmp=0). lpjcheck -pedantic terminó con exit 0, mostró las advertencias conocidas de entorno/insumos y aceptó el restart desde el año 1494. El segmento nuevo sigue activo.

Los SHA-256 vigentes de los otros checkpoints también coinciden con sus archivos de restart: 00000_07999 c59f10b4ee452d24259ae591ede142485bdc26413dbd381c758222ba9e1cfd6d; 16000_23999 8320adbef33619710eada5a49c9c87522116b4ded3b100e9580b38dd87d88605; 24000_31999 0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa; 32000_39999 dc6f24a5fc1adb6fc9c56703f664ca75590d7986c25eb90981b7bb9a4dbf3864. Las últimas filas anuales visibles fueron 1565 en 00000_07999, 1493 en 16000_23999, 1485 en 24000_31999 y 1485 en 32000_39999; 08000_15999 reanudó desde el año 1494 y su segmento nuevo aún no registra una fila anual.

Los cinco modelos consumen aproximadamente 39,7–40,0% de CPU cada uno. free -h informa 11 GiB disponibles, swap usada 7,6/8,0 GiB y 448 MiB libres; el filesystem tiene 499 GiB libres. vmstat registró 3 KiB/s de swap-in y 272 KiB/s de swap-out en la primera muestra y cero en las cuatro muestras de intervalo siguientes; no se observa paginación sostenida en esa ventana, aunque el margen de swap sigue estrecho. Los stderr recientes contienen advertencias conocidas, sin error fatal actual. El traceback LPJmL exit 137 que aún aparece en el stderr de 00000_07999 pertenece al 2026-10-01, antes de la generación vigente; el proceso actual de ese bloque sigue activo. No aumento el paralelismo por encima de cinco.

La configuración confirmada conserva river_routing=false y reservoir=false, por lo que la interpretación se limita al routing local desactivado.

**FR-Genghis, seguimiento 2026-10-04 11:53 COT:** campaign_status sigue en POTENTIAL_CHUNKS_RUNNING. Permanecen activos cinco LPJmL, cinco mpirun -np 1 y cinco checkpoint_runner, con ~39,9--40,0% de CPU por modelo. No hay códigos finales ni productos aceptados. No se registró checkpoint nuevo; los SHA-256 del último CHECKPOINT_SAVED de cada controller coinciden con restart/checkpoint.lpj y el archivo archivado más reciente, con cmp=0: 00000_07999 c59f10b4ee452d24259ae591ede142485bdc26413dbd381c758222ba9e1cfd6d; 08000_15999 e8a62f04e7ec5b47c6e9e3468fc6a38910743f8cca7c659f0897ae23bdafcd2b; 16000_23999 8320adbef33619710eada5a49c9c87522116b4ded3b100e9580b38dd87d88605; 24000_31999 0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa; 32000_39999 dc6f24a5fc1adb6fc9c56703f664ca75590d7986c25eb90981b7bb9a4dbf3864. Los stdout muestran las filas 1565, 1493, 1493, 1485 y 1485 para 00000, 08000, 16000, 24000 y 32000, respectivamente; 16000 avanzó a la fila 1493 y 32000 a la 1485 desde la revisión anterior. Los stderr consultados mantienen advertencias conocidas; el exit 137 de controller.stderr en 00000 corresponde al incidente de 2026-10-01. free -h informa 11 GiB disponibles; swap 8,0/8 GiB usada con 12 KiB libres; /home mantiene 500 GiB libres. En vmstat 1 5 los cuatro intervalos medidos después de la fila promedio inicial tuvieron si/so=0; no se observó paginación sostenida. Mantengo MAX_PARALLEL=5, un rank MPI por bloque, CH4 y MAX_ARCHIVED_CHECKPOINTS=0. Se conservan river_routing=false y reservoir=false como límites de interpretación.

**FR-Genghis, seguimiento 2026-10-04 10:52 COT:** campaign_status continúa en POTENTIAL_CHUNKS_RUNNING; siguen vivos cinco LPJmL, cinco mpirun -np 1 y cinco checkpoint_runner. Los LPJmL usan ~39,9--40,0% CPU. No hay códigos finales ni productos aceptados. No se guardaron checkpoints nuevos. El último SHA-256 de cada controller coincide con restart/checkpoint.lpj y el archivo archivado más reciente; cmp devuelve 0 en los cinco bloques: 00000_07999 c59f10b4ee452d24259ae591ede142485bdc26413dbd381c758222ba9e1cfd6d; 08000_15999 e8a62f04e7ec5b47c6e9e3468fc6a38910743f8cca7c659f0897ae23bdafcd2b; 16000_23999 8320adbef33619710eada5a49c9c87522116b4ded3b100e9580b38dd87d88605; 24000_31999 0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa; 32000_39999 dc6f24a5fc1adb6fc9c56703f664ca75590d7986c25eb90981b7bb9a4dbf3864. Las filas anuales visibles no cambiaron: 1565 en 00000, 1493 en 08000 y 1485 en 24000; los stdout de los otros dos bloques siguen mostrando el arranque desde restart. El stderr de 00000 contiene el RuntimeError LPJmL exit 137 ya fechado como incidente histórico del 2026-10-01; los demás stderr revisados solo muestran advertencias conocidas. Recursos: 11 GiB de RAM disponible, 500 GiB libres en /home y swap usada 8,0/8,0 GiB (0 B libres). Las cuatro muestras posteriores al promedio inicial de vmstat 1 5 marcaron si/so=0; la última tuvo b=1. No se observa intercambio sostenido en esa breve ventana, pero la reserva de swap está agotada. Mantengo MAX_PARALLEL=5, un rank por bloque, CH4 y MAX_ARCHIVED_CHECKPOINTS=0; no paro ni relanzo tareas. river_routing=false y reservoir=false siguen limitando la interpretación al routing local desactivado.

**FR-Genghis, seguimiento 2026-10-04 09:51 COT:** campaign_status conserva POTENTIAL_CHUNKS_RUNNING. Hay cinco procesos LPJmL y cinco mpirun -np 1, más cinco checkpoint_runner; cada LPJmL usa ~39,9--40,0% CPU. No hay códigos finales ni productos aceptados. Los últimos SHA-256 registrados por los controladores coinciden con restart/checkpoint.lpj y el checkpoint archivado más reciente; cmp termina en 0 para cada bloque. No cambió ningún hash desde 08:50 COT: 00000_07999 c59f10b4ee452d24259ae591ede142485bdc26413dbd381c758222ba9e1cfd6d; 08000_15999 e8a62f04e7ec5b47c6e9e3468fc6a38910743f8cca7c659f0897ae23bdafcd2b; 16000_23999 8320adbef33619710eada5a49c9c87522116b4ded3b100e9580b38dd87d88605; 24000_31999 0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa; 32000_39999 dc6f24a5fc1adb6fc9c56703f664ca75590d7986c25eb90981b7bb9a4dbf3864. Los stdout muestran filas anuales 1565 (00000), 1493 (08000) y 1485 (24000); los demás segmentos recientes siguen mostrando el arranque desde sus restart. El stdout de 24000 se actualizó a las 09:43 COT y el de 00000 a las 08:55 COT. Los controller/segment stderr consultados contienen advertencias conocidas; el traceback LPJmL exit 137 de 00000 es histórico, del 2026-10-01. Recursos: 11 GiB de RAM disponible, 500 GiB libres en /home, swap 8,0/8 GiB ocupada con 4 MiB libres. En vmstat 1 5 las cuatro muestras medidas tras la línea promedio dieron si/so=0, así que no se observa paginación sostenida durante la ventana, pero prácticamente no hay reserva de swap. Se mantiene MAX_PARALLEL=5, un rank MPI por bloque, CH4 y MAX_ARCHIVED_CHECKPOINTS=0; no cambio ni detengo procesos. river_routing=false y reservoir=false siguen limitando la interpretación al routing local desactivado.

**FR-Genghis, seguimiento 2026-10-04 08:50 COT:** campaign_status continúa como POTENTIAL_CHUNKS_RUNNING. Los cinco LPJmL y los cinco mpirun -np 1 siguen activos; cada LPJmL usa ~39,9% CPU. Los cinco scheduler/checkpoint_runner siguen vivos. No hay códigos finales ni productos aceptados. No se guardaron checkpoints nuevos desde la lectura anterior; el SHA-256 del último CHECKPOINT_SAVED de cada controller coincide con restart/checkpoint.lpj y con el archivo más reciente de checkpoints, y cmp devuelve 0: 00000_07999 c59f10b4ee452d24259ae591ede142485bdc26413dbd381c758222ba9e1cfd6d; 08000_15999 e8a62f04e7ec5b47c6e9e3468fc6a38910743f8cca7c659f0897ae23bdafcd2b; 16000_23999 8320adbef33619710eada5a49c9c87522116b4ded3b100e9580b38dd87d88605; 24000_31999 0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa; 32000_39999 dc6f24a5fc1adb6fc9c56703f664ca75590d7986c25eb90981b7bb9a4dbf3864. El segmento más reciente de 08000_15999 todavía muestra la fila 1493; no se observaron filas nuevas en los otros segmentos recientes. Los stderr revisados muestran advertencias conocidas; el traceback LPJmL exit 137 en 00000_07999 es el incidente histórico del 2026-10-01, no un fallo de la generación actual. free -h informa 11 GiB disponibles; swap usada 8,0 de 8 GiB con 30 MiB libres; /home conserva 500 GiB libres. En vmstat 1 5, tras la fila promedio inicial (3 KiB/s si, 288 KiB/s so), los cuatro intervalos medidos mostraron si/so=0: swap agotada, sin paginación sostenida durante esta ventana. Mantengo MAX_PARALLEL=5, un rank MPI por bloque, CH4 y MAX_ARCHIVED_CHECKPOINTS=0, sin modificar los procesos. Se mantienen river_routing=false y reservoir=false como limitaciones interpretativas (routing local desactivado).

**FR-Genghis, seguimiento 2026-10-04 07:49 COT:** los cinco bloques siguen activos; ps muestra cinco LPJmL con 39,8--39,9% de CPU y el scheduler/checkpoint runners permanecen activos. No se registraron códigos finales ni productos aceptados. Los SHA-256 reportados por los controladores coinciden con los archivos activos y archivados (cmp=PASS): 00000_07999 c59f10b4ee452d24259ae591ede142485bdc26413dbd381c758222ba9e1cfd6d; 08000_15999 e8a62f04e7ec5b47c6e9e3468fc6a38910743f8cca7c659f0897ae23bdafcd2b; 16000_23999 8320adbef33619710eada5a49c9c87522116b4ded3b100e9580b38dd87d88605; 24000_31999 0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa; 32000_39999 dc6f24a5fc1adb6fc9c56703f664ca75590d7986c25eb90981b7bb9a4dbf3864. No hubo checkpoint nuevo en esta inspección; el stdout más reciente de 08000_15999 avanzó hasta la fila anual 1493. Los segmentos stderr consultados conservan advertencias conocidas, sin fallo fatal nuevo; el traceback con LPJmL exit 137 en 00000_07999 es del 2026-10-01. La memoria informa 11,3 GiB disponibles, 500 GiB libres en /home y swap ocupada en 7,94 de 8 GiB (unos 61 MiB libres). vmstat 1 6 mostró actividad pequeña de swap en su primera línea de promedio y cero si/so en los cinco intervalos siguientes: swap casi agotada, sin paginación sostenida observada en la ventana. Se conserva MAX_PARALLEL=5, un rank MPI por bloque, CH4 y MAX_ARCHIVED_CHECKPOINTS=0; no aumento ni detengo procesos en esta lectura. La configuración comprobada mantiene river_routing=false y reservoir=false, por lo que la interpretación sigue limitada al routing local desactivado.
**FR-Genghis, seguimiento 2026-10-03 13:35 COT:** la campaña sigue en ejecución con cinco procesos LPJmL activos, un rank MPI por bloque y MAX_PARALLEL=5; la retención completa de checkpoints y la salida CH4 siguen configuradas. Los SHA-256 de los cinco restart/checkpoint.lpj coinciden con el último CHECKPOINT_SAVED de cada controller.log: 00000_07999, año 1561, 88f680589b802dd42ca806fb59eaa8c23ed4f84ed0cc2543fc11e8481c29c60f; 08000_15999, año 1489, 6479e6dcb8e3f6e122557a70cbbe04f5f13c3c7dd2c80eabff64dd2c7cabef7d; 16000_23999, año 1487, 753623983d436f2b20b476ef8fedf9c7c6ca60a4ca1ddd1f8a84928393bd8d80; 24000_31999, año 1481, 70174d7e6bfb430dd691f87529472571949b7215e4099043cf1ee53adbd454ae; 32000_39999, año 1481, 56929c418b142ba637156110295a9c531f9e3a0b7bf5c1d48adb204127fdd792. Los cinco modelos mantienen alrededor de 40% de CPU cada uno. free -h informa 10 GiB disponibles, pero la swap de 8 GiB está completamente ocupada; VmSwap suma aproximadamente 7,8 GiB en tres procesos y es casi nula en los otros dos. vmstat 1 4 mostró salida de swap de 365 KiB/s en el primer intervalo y cero swap-in/out en los tres siguientes, sin intercambio sostenido durante la muestra. Quedan 506 GiB libres en el filesystem. Esto señala presión de memoria que conviene vigilar; con CPU activa y sin paginación sostenida observada, mantengo MAX_PARALLEL=5 y no cambio ni detengo procesos. Los stderr recientes revisados no muestran fallos fatales; el exit 137 de 00000_07999 es el incidente histórico del 2026-10-01. No hay códigos finales ni productos aceptados. La interpretación conserva river_routing=false y reservoir=false, por lo que el routing de esta campaña sigue siendo local.
**FR-Genghis, seguimiento 2026-10-03 11:33 COT:** se verificaron dos checkpoints nuevos. `00000_07999` avanzó hasta después de la fila anual 1561, SHA-256 `88f680589b802dd42ca806fb59eaa8c23ed4f84ed0cc2543fc11e8481c29c60f`; `08000_15999` avanzó después de la fila 1489, SHA-256 `6479e6dcb8e3f6e122557a70cbbe04f5f13c3c7dd2c80eabff64dd2c7cabef7d`. En ambos casos el restart activo y el archivo de checkpoint registrado por `controller.log` tienen el mismo SHA-256. `lpjcheck -pedantic` terminó con código 0 para cada configuración y reportó reanudación desde los años 1562 y 1490, respectivamente. Los cinco bloques siguen activos, un rank MPI por bloque, `MAX_PARALLEL=5`, retención completa de checkpoints; no hay códigos finales ni productos aceptados. Los checkpoints sin cambio son `16000_23999` año 1487, SHA-256 `753623983d436f2b20b476ef8fedf9c7c6ca60a4ca1ddd1f8a84928393bd8d80`; `24000_31999` año 1481, `70174d7e6bfb430dd691f87529472571949b7215e4099043cf1ee53adbd454ae`; y `32000_39999` año 1481, `56929c418b142ba637156110295a9c531f9e3a0b7bf5c1d48adb204127fdd792` (ya validado, reanudación desde 1482). Los procesos consumen cerca de 40% CPU cada uno; RAM disponible 11 GiB, swap usada 6.0 de 8 GiB y 506 GiB libres en el filesystem. `vmstat` mostró swap-in/out nulo en las muestras posteriores al primer intervalo, sin intercambio sostenido. Los segmentos activos no muestran errores fatales; las advertencias observadas son conocidas. El exit 137 en el stderr de `00000_07999` sigue siendo histórico del 2026-10-01, anterior a esta generación. Se conserva `MAX_PARALLEL=5`; routing local desactivado (`river_routing=false`, `reservoir=false`) limita la interpretación.
**FR-Genghis, seguimiento 2026-10-03 10:45 COT:** `32000_39999` guardó su primer checkpoint tras la fila anual 1481, SHA-256 `56929c418b142ba637156110295a9c531f9e3a0b7bf5c1d48adb204127fdd792`; el archivo activo y el archivo archivado indicado por `controller.log` coinciden byte a byte. La comprobación correcta `lpjcheck -pedantic` sobre `checkpoint_config.json`, con `inpath`, `outpath` y `restartpath` de este bloque, terminó con código 0 e indicó reanudación desde el año 1482; el supervisor inició un nuevo segmento. Los cinco bloques continúan activos, con un rank MPI por bloque y `MAX_PARALLEL=5`; no hay códigos finales ni productos aceptados. Checkpoints vigentes: `00000_07999` año 1560, SHA-256 `1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212`; `08000_15999` año 1488, `836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1`; `16000_23999` año 1487, `753623983d436f2b20b476ef8fedf9c7c6ca60a4ca1ddd1f8a84928393bd8d80`; `24000_31999` año 1481, `70174d7e6bfb430dd691f87529472571949b7215e4099043cf1ee53adbd454ae`; `32000_39999` año 1481, hash indicado arriba. La salida CH4 aparece en la configuración comprobada. Los cinco LPJmL usan cerca de 40% CPU cada uno. RAM disponible 11 GiB, swap ocupada 6.5 de 8 GiB y 509 GiB libres en el filesystem; `vmstat` mostró un primer intercambio de salida pequeño y luego cero swap-in/out en las muestras siguientes, sin intercambio sostenido. Los segmentos activos muestran progreso/arranque y advertencias conocidas, sin error fatal actual; el traceback con exit 137 en `00000_07999` pertenece al 2026-10-01 y es anterior a la reanudación vigente. Mantengo el límite de cinco procesos y las limitaciones interpretativas `river_routing=false` y `reservoir=false`.
# Paralelismo seguro para la selección de capacidad LPJmL

**FR-Genghis, seguimiento 2026-10-03 19:40 COT:** el bloque 16000_23999 guardó un checkpoint nuevo tras la fila anual 1490: SHA-256 eacf565edfd881572b7db1cbf64eae100f060af6b19836dc24d16a4e0a886ec3. La copia archivada y restart/checkpoint.lpj coinciden; lpjcheck -pedantic terminó con código 0 e indicó reanudación desde el año 1490. El proceso ya continúa en un segmento nuevo. Los otros checkpoints permanecen: 00000_07999, año 1561, 88f680589b802dd42ca806fb59eaa8c23ed4f84ed0cc2543fc11e8481c29c60f; 08000_15999, año 1489, 6479e6dcb8e3f6e122557a70cbbe04f5f13c3c7dd2c80eabff64dd2c7cabef7d; 24000_31999, año 1481, 70174d7e6bfb430dd691f87529472571949b7215e4099043cf1ee53adbd454ae; y 32000_39999, año 1481, 56929c418b142ba637156110295a9c531f9e3a0b7bf5c1d48adb204127fdd792. En los cinco bloques, el SHA-256 del restart activo coincide con el último checkpoint registrado por el controlador. Las últimas filas anuales visibles son 1563, 1491, 1490, 1483 y 1483, respectivamente. Siguen activos cinco LPJmL y cinco mpirun con un rank por bloque, cerca de 40% de CPU cada uno; no hay códigos finales ni productos aceptados, y los stderr recientes no muestran fallos fatales. El exit 137 de 00000_07999 sigue limitado al incidente histórico del 2026-10-01. Quedan 9,6 GiB de RAM disponible, 6,1 GiB de swap usada de 8 GiB y 505 GiB libres en el filesystem. vmstat mostró un intercambio pequeño en el primer intervalo y cero si/so en los dos siguientes, sin paginación sostenida. Se conserva MAX_PARALLEL=5, CH4 y la retención completa de checkpoints; no aumento el paralelismo. river_routing=false y reservoir=false limitan la interpretación al routing local desactivado.

**FR-Genghis, seguimiento 2026-10-03 09:32 COT:** 24000_31999 guardó checkpoint después de la fila anual 1481; SHA-256 70174d7e6bfb430dd691f87529472571949b7215e4099043cf1ee53adbd454ae. El SHA-256 del restart coincide con controller/archive; lpjcheck terminó con exit 0 e informó que el restart continúa desde 1482. El supervisor inició un nuevo segmento para el mismo bloque, que sigue activo. Permanecen activos los cinco bloques, MAX_PARALLEL=5 y un rank MPI por bloque; no hay códigos finales ni productos aceptados. Checkpoints vigentes: 00000_07999 año 1560, SHA-256 1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212; 08000_15999 año 1488, 836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1; 16000_23999 año 1487, 753623983d436f2b20b476ef8fedf9c7c6ca60a4ca1ddd1f8a84928393bd8d80; 24000_31999 año 1481, hash indicado arriba; 32000_39999 aún sin checkpoint guardado. Los últimos años anuales visibles siguen en 1561, 1489, 1487, 1481 y 1481. Hay 7.5 GiB de RAM disponible, 3.2 GiB de swap usada y 511 GiB libres en /home; vmstat no indica intercambio sostenido. Segmentos activos revisados sin errores fatales. Mantengo MAX_PARALLEL=5 y river_routing=false/reservoir=false como limitaciones de interpretación.

**FR-Genghis, seguimiento 2026-10-03 08:32 COT:** se guardó un nuevo checkpoint para 16000_23999 tras la fila anual 1487; SHA-256 753623983d436f2b20b476ef8fedf9c7c6ca60a4ca1ddd1f8a84928393bd8d80. El hash del restart activo coincide con el de controller/archive, y lpjcheck terminó con exit 0; informó reinicio desde el checkpoint en año 1488. El supervisor relanzó normalmente el mismo bloque con un nuevo segmento; siguen cinco bloques activos, MAX_PARALLEL=5, un rank MPI cada uno, sin códigos finales ni productos aceptados. Los otros checkpoints no cambian: 00000_07999 año 1560, SHA-256 1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212; 08000_15999 año 1488, 836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1. 24000_31999 y 32000_39999 siguen sin checkpoint guardado. Las últimas filas visibles son 1561, 1489, 1487, 1481 y 1481; los otros bloques mantienen actividad de CPU aunque sus filas anuales no avanzaron desde la última revisión. RAM disponible 8.0 GiB, swap usada 4.2 GiB de 8 GiB, disco libre 514 GiB; vmstat mostró swap-in/out nulos en las dos muestras instantáneas, sin intercambio sostenido. El segmento nuevo de 16000_23999 y los stderr revisados no muestran errores fatales. Mantengo el límite en cinco y la cautela interpretativa river_routing=false/reservoir=false.

**FR-Genghis, seguimiento 2026-10-03 07:32 COT:** los cinco bloques continúan activos con un rank MPI por bloque y MAX_PARALLEL=5. Los tiempos de CPU de los cinco LPJmL avanzaron unos 23 min durante los 58 min entre muestreos (cerca de 41% por proceso), aunque las últimas filas anuales siguen en 1561, 1489, 1487, 1481 y 1481; los stdout no cambian desde aproximadamente 01:57–04:43 COT según el bloque. No aparecieron checkpoints nuevos. Los últimos checkpoints, sin cambios y con SHA-256 verificado contra el restart, son 00000_07999 año 1560 (1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212), 08000_15999 año 1488 (836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1) y 16000_23999 año 1486 (7f3b065e67ed12d4ec1703faf068cb07d16667a83879fa04cde7b35e6d19077e); 24000_31999 y 32000_39999 siguen sin checkpoint guardado desde A0. No hay códigos finales ni productos aceptados. Quedan 7.3 GiB de RAM disponible, swap usada 3.8 GiB de 8 GiB y 515 GiB libres en /home; vmstat mostró swap-in/out nulos en las dos muestras instantáneas tras la primera, sin señal de intercambio sostenido. Los stderr activos no reportan errores fatales; el exit 137 histórico de 00000_07999 corresponde al 2026-10-01. Mantengo MAX_PARALLEL=5 por prudencia y river_routing=false/reservoir=false como limitaciones de interpretación.

**FR-Genghis, seguimiento 2026-10-03 05:29 COT:** los cinco bloques continúan activos con MAX_PARALLEL=5 y un rank MPI por bloque. Las filas más recientes observadas son: 00000_07999 año 1561, 08000_15999 1489, 16000_23999 1487, 24000_31999 y 32000_39999 1481. Los checkpoints siguen en los años 1560, 1488 y 1486, con SHA-256 1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212, 836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1 y 7f3b065e67ed12d4ec1703faf068cb07d16667a83879fa04cde7b35e6d19077e; aún no hay checkpoint de esta generación para los otros dos bloques, códigos finales ni productos aceptados. Cada LPJmL consume cerca de 40.9% de CPU; quedan 3.7 GiB de RAM disponible, 7 MiB de swap usada y 515 GiB libres en /home. Los stderr recientes revisados muestran advertencias conocidas, sin error fatal actual; el exit 137 de 00000_07999 pertenece a una generación anterior (2026-10-01). Mantengo el máximo en cinco por la reserva de RAM inferior a 4 GiB. river_routing=false y reservoir=false limitan la interpretación al routing local sin ríos ni reservorios.

**Fecha:** 2026-10-01  
**Campaña:** `FR-genghis-khan-crop-only`  
**Directorio previsto:** `/home/dasan/exofarm-lpjml-runs/fr_genghis_potential_20260922_chunks_ch4`

## Motivo y estado

La selección potencial por bloques de 8.000 celdas se paraleliza entre bloques
disjuntos, manteniendo un rank MPI por bloque. El planificador anterior era
serial. La campaña CH4 se amplió primero a dos bloques y luego, tras una
interrupción de WSL, a tres bloques simultáneos con retención completa. El
2026-10-01 01:26 COT, el bloque `00000_07999` llevaba 36 checkpoints (~32 GB); su
restart y archivo más reciente coincidían en SHA-256
`5c0073cbf3acce68e5b2d6d4a43df66dde3217b2318bbe547e93f6a20fda52df`. Había
534 GiB libres en el volumen. A las 01:55 COT la lectura viva confirmó
`POTENTIAL_CHUNKS_RUNNING`, bloques `00000_07999` y `08000_15999` en ejecución,
un rank en cada uno, `MAX_PARALLEL=2` y `MAX_ARCHIVED_CHECKPOINTS=0`. La memoria
disponible era 26 GiB y quedaban 532 GiB en disco. El aumento real de velocidad
aún no se ha medido.

El primer bloque reanudó desde el checkpoint de año 1552 (SHA-256 arriba). El
segundo bloque cubre celdas 8000--15999. Ambos configs tienen
`with_methane=true`, `river_routing=false` y `reservoir=false`; la limitación de
enrutamiento local se conserva en la interpretación.

**Reanudación ampliada 2026-10-01 18:51 COT:** la campaña se encontró
interrumpida después de un reinicio de WSL: no había procesos activos, los logs
estaban inmóviles y `campaign.lock.d` estaba vacío. Los checkpoints de los dos
bloques existentes se verificaron antes de reanudar. Con autorización del
usuario, el planificador arrancó a las 18:49 COT con `MAX_PARALLEL=3`,
`MPI_RANKS=1`, `CHUNK_SIZE=8000` y `MAX_ARCHIVED_CHECKPOINTS=0`. El bloque
`00000_07999` retomó desde el año 1556, SHA-256
`f150c32b9c5ebdbe9202cf15dc18785d35d0c4efa20575f301ba2db9541c2080`; el bloque
`08000_15999` retomó desde el año 1484, SHA-256
`7d687ce9dfc6fe08478f181152cce943f9095f19b37d7e583833e939574f4e85`. `lpjcheck`
aceptó ambos reinicios. El bloque nuevo `16000_23999` inició desde A0 y aún no
tenía checkpoint en la primera lectura. El host Ubuntu informó 8 núcleos físicos
y 16 lógicos; al inicio había 25 GiB disponibles, swap sin uso y 525 GiB libres
en disco. Tres bloques por rank usan 3 núcleos físicos, por debajo de la
capacidad detectada. El rendimiento comparativo aún no tiene una ventana de
medición suficiente y no se ha intentado un cuarto bloque. La corrida se
mantiene en curso; estos estados operativos no aceptan salidas científicas.

**Seguimiento 2026-10-01 19:08 COT:** los tres procesos LPJmL siguen vivos; una
muestra instantánea registró 80 %, 68 % y 52 % de CPU por proceso, con 4.2--4.7
GiB de RSS cada uno. Quedan 17 GiB disponibles, no se usa swap y hay 525 GiB libres en
disco. Los SHA-256 de `checkpoint.lpj` en `00000_07999` y `08000_15999` siguen
siendo, respectivamente, `f150c32b9c5ebdbe9202cf15dc18785d35d0c4efa20575f301ba2db9541c2080`
y `7d687ce9dfc6fe08478f181152cce943f9095f19b37d7e583833e939574f4e85`. En
los logs de esta generación todavía no aparece un año simulado nuevo; el bloque
`16000_23999` aún no tiene checkpoint. No hay indicios de error o presión de
recursos en esta lectura. Mantener tres bloques permite medir el avance antes
de considerar más concurrencia.

**Checkpoint y actividad verificados (2026-10-02 01:27 COT):** los tres
bloques siguen activos. `00000_07999` registra el año simulado 1557 y conserva
el checkpoint de año 1556 (`f150c32b9c5ebdbe9202cf15dc18785d35d0c4efa20575f301ba2db9541c2080`);
`08000_15999` registra el año 1485 y conserva el checkpoint de año 1484
(`7d687ce9dfc6fe08478f181152cce943f9095f19b37d7e583833e939574f4e85`).
`16000_23999` guardó su primer checkpoint tras el año 1482, SHA-256
`de713797e50d9ccf0b3b9a67eb89746035f3eb9f36f436377364c1745757f857`;
`lpjcheck -pedantic` lo leyó desde ese año y terminó con código 0. El log
registra el guardado seguro por `SIGTERM` y el reinicio desde el checkpoint.
Los tres procesos LPJmL estaban activos en estado ejecutable, con porcentajes
de CPU informados por `ps` entre 61 y 70 % y RSS de 4.6--5.7 GiB. La RAM
disponible era 14 GiB, el swap usado 1.5 MiB y el disco conservaba 523 GiB.
No hay error fatal en esta generación ni presión de recursos. El
`controller.stderr.log` de `00000_07999` conserva un traceback con `LPJmL exit
137`, fechado el 2026-10-01 01:45 COT, anterior a la reanudación de las 18:49
COT desde el checkpoint íntegro. La generación actual sigue activa; los
`segment_*.stdout.stderr.log` recientes contienen advertencias, entre ellas
WARNING013 de uso de suelo en `08000_15999`, no un error fatal. `lpjcheck`
emitió advertencias no fatales de metadatos de suelo/tillage y de `LPJROOT`
ausente; la configuración pasó y los archivos de entrada/salida existen. La selección
sigue en curso y sus salidas no están aceptadas científicamente. Se mantienen
`with_methane=true`, `river_routing=false` y `reservoir=false`; el routing
local continúa limitando la interpretación.

**Lectura previa a la ampliación (2026-10-01 05:14 COT):** ambos bloques continuaban activos
con LPJmL al 99.9 % de un núcleo. El bloque `00000_07999` sigue desde el
checkpoint de año 1552 (`5c0073cb...fda52df`); el último registro de año en su
log es 1553 y todavía no hay un checkpoint posterior. El bloque
`08000_15999` guardó su primer checkpoint a las 05:43 COT:
`1790837715995448120.lpj`, SHA-256
`79698dfb5cd3558c13c2219bf8fe6d862fade574c11a27764c74acec48577f79`. El
restart activo y el archivo archivado coinciden en tamaño y hash; el controlador
capturó `SIGTERM` para el guardado seguro y reinició LPJmL desde ese estado.
No hay error en el proceso actual. En esta lectura había 19 GiB disponibles,
4.5 MiB de swap usada y 529 GiB libres. El ritmo científico por bloque aún no
se estima con una ventana suficiente.

## Diseño preparado

- `run_capacity_potential_chunks.sh` apunta por defecto a la carpeta CH4
  correcta y conserva `MPI_RANKS=1`; añade
  `MAX_PARALLEL` para limitar cuántos bloques independientes se ejecutan a la
  vez. El valor por defecto es 1, así que el comportamiento existente se
  conserva hasta una activación explícita. El planificador valida que
  `MAX_PARALLEL * MPI_RANKS` no exceda los procesadores disponibles, registra
  los parámetros y espera los resultados de todos los bloques iniciados.
- `checkpoint_runner.py` conserva todos los checkpoints si
  `MAX_ARCHIVED_CHECKPOINTS=0` (valor por defecto). Con un límite positivo,
  archiva y calcula SHA-256 del checkpoint nuevo, lo contrasta con el restart
  activo y solo entonces poda generaciones antiguas y sus sidecars. El restart
  activo no se poda.
- Los bloques usan directorios de salida, restart y controladores separados.
  `river_routing=false` y `reservoir=false` se mantienen en esta etapa local;
  la limitación de enrutamiento local sigue aplicando a la interpretación.
- La configuración activa de prueba es `MAX_PARALLEL=3`, `MPI_RANKS=1` y
  `CHUNK_SIZE=8000`, elegida con 8 núcleos físicos y holgura inicial de RAM.
  Aún no se ha medido el aumento real de rendimiento con tres bloques. No
  aumentar más hasta observar memoria, swap, espacio, tasas de avance y
  checkpoints tras un intervalo comparable.

## Verificación y relevo

El 2026-10-01 se ejecutaron en Ubuntu las dos pruebas unitarias de retención y
ambas pasaron; también pasó `bash -n`. El checkpoint archivado se contrastó con
el restart activo antes del relevo. Para activar el planificador se terminó el
segmento que llevaba ~2 h sin completar un año y se verificó la ausencia de
procesos, la estabilidad de los logs y el hash del restart. La simulación
reanuda ese bloque desde el checkpoint de 1552; las salidas científicas no
cambiaron durante el segmento interrumpido.

Hubo un lanzamiento inicial con la carpeta por defecto antigua
`fr_genghis_potential_20260922_chunks`, distinta de la carpeta CH4. Dos ranks
LPJmL corrieron allí durante algo más de dos minutos y se detuvieron; no se
aceptó ningún checkpoint de esa corrida. Sus archivos parciales y el estado
`FAILED` se conservaron intactos para inspección; no se mezclan con la campaña
CH4. Se fijó la carpeta CH4 como valor por defecto del lanzador y se relanzó con
`CAPACITY_POTENTIAL_CHUNKS_DIR` explícita. La campaña correcta usa
`MAX_PARALLEL=3`, `MPI_RANKS=1`, `CHUNK_SIZE=8000` y
`MAX_ARCHIVED_CHECKPOINTS=0`; todos los checkpoints se conservan. No se deben
iniciar copias paralelas manuales sobre este directorio: el planificador ya
posee el bloqueo global y administra los bloques pendientes.

## Archivos

- `Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction/run_capacity_potential_chunks.sh`
- `Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction/checkpoint_runner.py`
- `Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction/test_checkpoint_runner_retention.py`
- `docs/lpjml_franck_capacity_execution_2026-09-22.md`

## Seguimiento en vivo — 2026-10-02 04:30 COT

La campaña continúa con los tres bloques activos, `CH4`, `MAX_PARALLEL=3`,
un rank MPI por bloque y retención completa (`MAX_ARCHIVED_CHECKPOINTS=0`).
El seguimiento consultó el estado superior, los tres `run_status.txt`, logs de
control/segmento, procesos, recursos y SHA-256 de los reinicios activos.

- `00000_07999`: el checkpoint activo llegó al año 1558; SHA-256
  `4c1beab2ecf40db4e78cfbdd8a4ed5843bc9f0ba39031d37d2a9e88cdca07030`.
  `lpjcheck -pedantic` aceptó la configuración y el reinicio (código 0).
- `08000_15999`: checkpoint activo del año 1486; SHA-256
  `66d13bb13237714af53246b13840d21177ad7b5c252dbb7c6527eda02a6b1578`.
  `lpjcheck -pedantic` terminó con código 0.
- `16000_23999`: el segmento actual escribió el año 1483; el último checkpoint
  íntegro continúa en 1482, SHA-256
  `de713797e50d9ccf0b3b9a67eb89746035f3eb9f36f436377364c1745757f857`.

Los tres procesos LPJmL estaban en estado de ejecución y sus contadores de CPU
avanzaron durante una muestra de cinco segundos. `ps` informó 65.8--68.7 % de
CPU y 4.7--5.7 GiB de RSS por proceso. Había 16 GiB de RAM disponibles,
1.5 MiB de swap usados y 521 GiB libres. Los `run_status.txt` no contienen
códigos finales; no se acepta todavía ningún producto científico. Los stderr
actuales muestran advertencias, incluida `WARNING013` para fracciones de uso
del suelo en 08000, sin error fatal. El traceback `LPJmL exit 137` de
`00000_07999/controller.stderr.log` está fechado el 1 de octubre a la 01:45
COT, antes del reinicio autorizado de las 18:49 COT; no pertenece a la
generación activa. Se conservan `river_routing=false` y `reservoir=false`, por
lo que las inferencias siguen limitadas al routing local desactivado.

## Seguimiento en vivo — 2026-10-02 08:30 COT

Los tres bloques siguen activos en la campaña CH4 con `MAX_PARALLEL=3`, un
rank MPI por bloque y retención completa (`MAX_ARCHIVED_CHECKPOINTS=0`). Los
logs avanzaron desde la revisión de 04:30 COT:

- `00000_07999`: el log alcanza el año 1559; el checkpoint íntegro más reciente
  es 1558, SHA-256
  `4c1beab2ecf40db4e78cfbdd8a4ed5843bc9f0ba39031d37d2a9e88cdca07030`.
- `08000_15999`: el log alcanza el año 1487; checkpoint 1486, SHA-256
  `66d13bb13237714af53246b13840d21177ad7b5c252dbb7c6527eda02a6b1578`.
- `16000_23999`: se guardó checkpoint 1484, SHA-256
  `e9d67152cc7770b7a53e11440effa12ed699d984969f1d53967c0199a0ae14ce`;
  `lpjcheck -pedantic` terminó con código 0. El segmento posterior arrancó
  desde ese restart y aún no registraba otro año simulado.

Los tres procesos LPJmL permanecían activos; sus contadores de CPU aumentaron
durante una muestra de cinco segundos. Había 14.7 GiB de RAM disponibles,
1.5 MiB de swap usados y 520 GiB libres. No hay códigos finales ni productos
aceptados. Las advertencias recientes no son fatales. El `LPJmL exit 137` de
`00000_07999/controller.stderr.log` es un registro histórico del 1 de octubre,
01:45 COT, anterior al reinicio autorizado de las 18:49 COT. Se conservan
`river_routing=false` y `reservoir=false`; la interpretación continúa limitada
al routing local desactivado.

## Seguimiento en vivo — 2026-10-02 10:32 COT

La campaña conserva `POTENTIAL_CHUNKS_RUNNING`, con tres bloques CH4, un rank
MPI por bloque, `MAX_PARALLEL=3` y retención completa. No cambiaron las filas
de año, los checkpoints ni los tamaños/fechas de los logs recientes desde la
revisión de 08:30 COT:

- `00000_07999`: última fila visible 1559; checkpoint 1558, SHA-256
  `4c1beab2ecf40db4e78cfbdd8a4ed5843bc9f0ba39031d37d2a9e88cdca07030`.
- `08000_15999`: última fila visible 1487; checkpoint 1486, SHA-256
  `66d13bb13237714af53246b13840d21177ad7b5c252dbb7c6527eda02a6b1578`.
- `16000_23999`: checkpoint 1484, SHA-256
  `e9d67152cc7770b7a53e11440effa12ed699d984969f1d53967c0199a0ae14ce`;
  el segmento actual arrancó desde ese restart y todavía no imprimía otra
  fila anual.

Los tres procesos permanecen activos; `ps` registró 61.5--68.9 % de CPU y
aprox. 4.7--5.8 GiB de RSS por LPJmL, con contadores de CPU crecientes durante
una muestra de cinco segundos. Había 14 GiB de RAM disponibles, 1.5 MiB de
swap usados y 520 GiB libres. `run_status.txt` no contiene códigos finales;
no se aceptan productos. Los stderr de segmento más recientes muestran
advertencias, no errores fatales. El `LPJmL exit 137` de
`00000_07999/controller.stderr.log` mantiene su fecha antigua (1 de octubre,
01:45 COT), anterior al reinicio autorizado. Se mantienen
`river_routing=false` y `reservoir=false`, que limitan la interpretación al
routing local desactivado.

## Seguimiento en vivo — 2026-10-02 11:33 COT

La campaña continúa con los tres bloques CH4, `MAX_PARALLEL=3`, un rank MPI
por bloque y retención completa. El log más reciente de `16000_23999` avanzó
hasta el año 1485, aunque el checkpoint íntegro no ha cambiado desde 1484:
SHA-256 `e9d67152cc7770b7a53e11440effa12ed699d984969f1d53967c0199a0ae14ce`.
`00000_07999` sigue mostrando 1559 con checkpoint 1558, SHA-256
`4c1beab2ecf40db4e78cfbdd8a4ed5843bc9f0ba39031d37d2a9e88cdca07030`; y
`08000_15999`, 1487 con checkpoint 1486, SHA-256
`66d13bb13237714af53246b13840d21177ad7b5c252dbb7c6527eda02a6b1578`.

Una muestra de cinco segundos confirmó los tres procesos activos, con 60.7--
69.1 % de CPU y 4.7--5.8 GiB de RSS por LPJmL. Había 14 GiB de RAM
disponibles, 1.5 MiB de swap usados y 520 GiB libres. Los `run_status.txt`
siguen sin códigos finales. Los SHA-256 de los tres reinicios se recalcularon;
`lpjcheck -pedantic` había aceptado el checkpoint 1484 de 16000 con código 0
en la revisión previa. Los stderr recientes solo muestran advertencias; el
`exit 137` de 00000 es el registro histórico fechado el 1 de octubre a la
01:45 COT. Se mantienen `river_routing=false` y `reservoir=false`, que limitan
la interpretación al routing local desactivado.

## Seguimiento en vivo — 2026-10-02 12:34 COT

La campaña sigue con tres bloques CH4, `MAX_PARALLEL=3`, un rank MPI por
bloque y retención completa. Los logs más recientes avanzaron en los dos
primeros bloques y sus controladores registran nuevos guardados:

- `00000_07999`: el log alcanza la fila 1560; el restart activo tiene SHA-256
  `1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212`.
- `08000_15999`: el log alcanza la fila 1488; el restart activo tiene SHA-256
  `836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1`.
- `16000_23999`: el log permanece en 1485; conserva el restart 1484,
  SHA-256 `e9d67152cc7770b7a53e11440effa12ed699d984969f1d53967c0199a0ae14ce`.
  `lpjcheck -pedantic` había aceptado este checkpoint con código 0 en la
  revisión anterior.

Los tres LPJmL siguen activos y sus contadores de CPU aumentaron en cinco
segundos; las muestras marcaron 60.7--69.1 % de CPU y 4.5--5.0 GiB de RSS
por proceso. Había 16 GiB de RAM disponibles, 1.5 MiB de swap usados y 518
GiB libres. Los hashes activos se recalcularon; los dos guardados nuevos
constan en `controller.log`. Los `run_status.txt` siguen sin códigos finales
y no hay productos aceptados. Los stderr recientes contienen advertencias no
fatales; el `LPJmL exit 137` en el controller de 00000 conserva fecha antigua
(1 de octubre, 01:45 COT). Se mantienen `river_routing=false` y
`reservoir=false`, por lo que la interpretación sigue limitada al routing
local desactivado.

## Seguimiento en vivo — 2026-10-02 13:38 COT

La campaña conserva `POTENTIAL_CHUNKS_RUNNING` y la configuración CH4 de tres
bloques simultáneos, un rank MPI por bloque y retención completa. No se ven
nuevas filas anuales ni checkpoints desde la revisión de 12:34 COT; el último
registro anual visible continúa en 1560, 1488 y 1485 para `00000_07999`,
`08000_15999` y `16000_23999`, respectivamente. Las marcas de los segmentos
actuales son 12:20:25, 11:35:34 y 11:19:21 COT; cada uno arrancó desde el
checkpoint correspondiente y aún no ha escrito otra fila.

Los SHA-256 recalculados para `restart/checkpoint.lpj` son, en el mismo orden,
`1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212`,
`836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1` y
`e9d67152cc7770b7a53e11440effa12ed699d984969f1d53967c0199a0ae14ce`; los
controladores registran los dos primeros guardados recientes y el tercero ya
había sido aceptado por `lpjcheck -pedantic` con código 0. Los tres LPJmL,
`mpirun` y `checkpoint_runner` siguen presentes. Una muestra separada cinco
segundos registró 62.4--67.3 % de CPU por LPJmL y contadores de CPU crecientes;
RSS aproximado: 4.1, 5.1 y 5.6 GiB. Hay 15 GiB de RAM disponibles, 575 MiB de
swap ocupados y 518 GiB libres en disco. La swap aumentó respecto a lecturas
anteriores, pero la RAM disponible y el espacio libre no muestran presión
inmediata.

Los `run_status.txt` aún no tienen códigos finales. Los stderr recientes
contienen advertencias, no un error actual; el traceback `LPJmL exit 137` de
`00000_07999/controller.stderr.log` sigue siendo el episodio antiguo del 1 de
octubre a las 01:45 COT. No se acepta todavía ningún producto. Se mantienen
`river_routing=false` y `reservoir=false`, de modo que la interpretación queda
limitada al routing local desactivado.

## Seguimiento en vivo — 2026-10-02 14:36 COT

La campaña conserva `POTENTIAL_CHUNKS_RUNNING` y la configuración CH4 de tres
bloques simultáneos, un rank MPI por bloque y retención completa. Los últimos
registros anuales visibles son 1560 (`00000_07999`), 1488 (`08000_15999`) y
1485 (`16000_23999`). Los SHA-256 recalculados de los reinicios activos son
`1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212`,
`836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1` y
`7f3b065e67ed12d4ec1703faf068cb07d16667a83879fa04cde7b35e6d19077e`. El
checkpoint del tercer bloque se guardó a las 14:29 COT; el segmento iniciado
después de ese guardado ya lo ha cargado. Los checkpoints de los dos primeros
bloques y sus últimos registros no han cambiado desde la revisión de 12:34 COT.

Los tres `checkpoint_runner`, `mpirun` y LPJmL permanecen activos. Una muestra
separada cinco segundos marcó 64.8--74.4 % de CPU por LPJmL, con contadores de
CPU crecientes; RSS aproximado 5.7, 5.2 y 4.6 GiB. Hay 14 GiB de RAM
disponibles, 95 MiB de swap utilizados y 517 GiB libres. Los `run_status.txt`
no tienen códigos de salida; los stderr recientes solo muestran advertencias.
El `LPJmL exit 137` que aparece en el controller stderr de `00000_07999` sigue
siendo el evento histórico del 1 de octubre a las 01:45 COT. Todavía no hay
productos aceptados. Se mantienen `river_routing=false` y `reservoir=false`,
por lo que la interpretación queda limitada al routing local desactivado.

## Seguimiento en vivo — 2026-10-02 15:42 COT

La campaña conserva `POTENTIAL_CHUNKS_RUNNING` con tres bloques CH4,
`MAX_PARALLEL=3`, un rank MPI por bloque y retención completa
(`MAX_ARCHIVED_CHECKPOINTS=0`). Los tres archivos de configuración confirman
`with_methane=true`, `river_routing=false` y `reservoir=false`.

Las últimas filas anuales encontradas en los logs siguen en 1560, 1488 y 1485
(`00000_07999`, `08000_15999`, `16000_23999`). Los segmentos actuales se
iniciaron desde sus checkpoints y no han escrito otra fila anual en esta
revisión. Los SHA-256 recalculados del restart y del checkpoint archivado más
reciente coinciden con controller:

- `00000_07999`: `1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212`
  (guardado 12:19 COT).
- `08000_15999`: `836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1`
  (guardado 11:34 COT).
- `16000_23999`: `7f3b065e67ed12d4ec1703faf068cb07d16667a83879fa04cde7b35e6d19077e`
  (guardado 14:29 COT y cargado por el segmento actual).

Los tres `checkpoint_runner`, `mpirun` y LPJmL siguen presentes. En muestras
separadas cinco segundos, LPJmL usó 64.8--71.5 % de CPU y aumentaron los
contadores de tiempo de CPU; el cálculo continúa aunque el registro anual sea
espaciado. Hay 14 GiB de RAM disponibles, 95 MiB de swap usados y 517 GiB
libres, sin presión inmediata. `run_status.txt` solo contiene bloque e inicio,
sin códigos finales; todavía no hay productos aceptados. Los stderr actuales
muestran advertencias, incluida WARNING013 de fracciones de uso de suelo. El
`LPJmL exit 137` de `00000_07999/controller.stderr.log` corresponde al evento
histórico del 1 de octubre a las 01:45 COT, no a la generación activa. La
interpretación sigue limitada al routing local desactivado.

## Seguimiento en vivo — 2026-10-02 16:37 COT

Los tres bloques siguen ejecutándose con CH4, un rank MPI por bloque,
`MAX_PARALLEL=3` y retención completa (`MAX_ARCHIVED_CHECKPOINTS=0`). Los
logs avanzaron a 1561 (`00000_07999`), 1489 (`08000_15999`) y 1486
(`16000_23999`). Los procesos LPJmL de los tres bloques continúan activos;
dos muestras separadas cinco segundos mostraron 64.6--67.6 % de CPU y
contadores de tiempo crecientes.

Los SHA-256 de restart y archivo reciente siguen coincidiendo con controller:

- `00000_07999`: `1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212`.
- `08000_15999`: `836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1`.
- `16000_23999`: `7f3b065e67ed12d4ec1703faf068cb07d16667a83879fa04cde7b35e6d19077e`.

No se registró un nuevo checkpoint desde la revisión anterior. Hay 14 GiB de
RAM disponibles, 95.6 MiB de swap usados y 517 GiB libres en disco, sin presión
inmediata. Los stderr recientes contienen advertencias, incluida WARNING013
no fatal; el `LPJmL exit 137` de `00000_07999` sigue siendo el incidente
histórico del 1 de octubre a las 01:45 COT. `run_status.txt` aún no contiene
códigos finales y no hay productos aceptados. `with_methane=true` se mantiene;
`river_routing=false` y `reservoir=false` limitan la interpretación al routing
local desactivado.

## Seguimiento en vivo — 2026-10-02 17:40 COT

La campaña permanece en `POTENTIAL_CHUNKS_RUNNING` con tres bloques CH4,
`MAX_PARALLEL=3`, un rank MPI por bloque y retención completa
(`MAX_ARCHIVED_CHECKPOINTS=0`). Los procesos LPJmL de los tres bloques siguen
activos. Dos muestras separadas cinco segundos mostraron 64.7--67.2 % de CPU
y contadores de tiempo crecientes. Los logs anuales no han avanzado desde la
revisión de las 16:37; los últimos registros observados siguen en 1561, 1489 y
1486 para `00000_07999`, `08000_15999` y `16000_23999`.

Los SHA-256 de restart y archivo más reciente se mantienen y coinciden con
controller:

- `00000_07999`: `1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212`.
- `08000_15999`: `836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1`.
- `16000_23999`: `7f3b065e67ed12d4ec1703faf068cb07d16667a83879fa04cde7b35e6d19077e`.

No se guardó un checkpoint nuevo desde la revisión anterior. Hay 14 GiB de RAM
disponibles, 95 MiB de swap usados y 517 GiB libres en disco, sin presión
inmediata. Los stderr de los tres controllers no muestran errores actuales;
el `exit 137` de `00000_07999` sigue siendo histórico (1 de octubre,
01:45 COT), mientras los segmentos recientes contienen advertencias. No hay
códigos finales ni productos aceptados. Se mantiene `with_methane=true`;
`river_routing=false` y `reservoir=false` limitan la interpretación al
routing local desactivado.

## Interrupción confirmada — 2026-10-02 18:43 COT

El archivo de campaña todavía dice `POTENTIAL_CHUNKS_RUNNING`, pero ya no hay
procesos `run_capacity_potential_chunks`, `checkpoint_runner`, `mpirun` ni
LPJmL. Dos comprobaciones, a las 18:43:38 y 18:43:49 COT, confirmaron la
ausencia de procesos y los mismos tamaños y fechas para campaign/launcher,
`run_status.txt`, controllers, segmentos y checkpoints. Los estados por bloque
solo conservan rango e inicio; no hay códigos de salida finales. No se inició
otra copia.

Últimas filas anuales registradas: 1561 para `00000_07999`, 1489 para
`08000_15999` y 1486 para `16000_23999`. Los checkpoints más recientes,
comparados por SHA-256 entre restart, archivo de checkpoints y registro
`CHECKPOINT_SAVED` del controller, son:

- `00000_07999`: `1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212`.
- `08000_15999`: `836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1`.
- `16000_23999`: `7f3b065e67ed12d4ec1703faf068cb07d16667a83879fa04cde7b35e6d19077e`.

Estos hashes confirman la copia byte a byte frente a controller; `lpjcheck`
aún no se ha ejecutado sobre estos tres guardados más recientes. El stderr de
controller de `00000_07999` conserva el fallo histórico `LPJmL exit 137` del
1 de octubre a las 01:45 COT; los otros dos controller stderr están vacíos.
Los segmentos recientes solo presentan advertencias. En el host hay 30 GiB de
RAM disponibles, no hay swap usada y quedan 517 GiB libres en disco, así que la
interrupción no coincide con presión actual de esos recursos.

La campaña usaba bloques de 8.000 celdas, un rank MPI por bloque, CH4,
`MAX_PARALLEL=3` y retención completa (`MAX_ARCHIVED_CHECKPOINTS=0`). Se
mantienen `river_routing=false` y `reservoir=false`, por lo que la
interpretación queda limitada al routing local desactivado. La recuperación
quedó pendiente hasta la autorización recibida el 2026-10-02.

## Reanudación con cuatro bloques — 2026-10-02 19:52 COT

Tras la interrupción confirmada a las 18:43 COT, el usuario autorizó reanudar y
aumentar los procesos paralelos. A las 19:43 COT, Ubuntu WSL exponía 16 CPU y
30 GiB de RAM disponibles; no había procesos de campaña ni `campaign.lock.d`.
El manifiesto anterior registraba `MAX_PARALLEL=3`, así que el nuevo límite se
fijó en cuatro bloques, un rank MPI por bloque, `CHUNK_SIZE=8000`, CH4 y
retención completa (`MAX_ARCHIVED_CHECKPOINTS=0`).

Antes del lanzamiento se recalcularon los SHA-256 de cada checkpoint archivado
y restart y se compararon byte a byte; los tres coincidieron con el último
`CHECKPOINT_SAVED` del controller. Los tres reinicios pasaron
`lpjcheck -pedantic` con código 0:

- `00000_07999`: año 1560; SHA-256
  `1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212`.
- `08000_15999`: año 1488; SHA-256
  `836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1`.
- `16000_23999`: año 1486; SHA-256
  `7f3b065e67ed12d4ec1703faf068cb07d16667a83879fa04cde7b35e6d19077e`.

El planificador reinició esos tres bloques desde sus checkpoints y abrió
`24000_31999` desde A0. A las 19:52 COT se observaron cuatro procesos LPJmL
activos, con 39.8--45.7 % de CPU y RSS de 0.9--4.7 GiB por proceso; había
17 GiB disponibles, swap sin uso y 516 GiB libres en disco. Los logs recién
iniciados aún no mostraban filas anuales nuevas. Los stderr de esta generación
solo contienen advertencias de entradas/uso de suelo conocidas; el `exit 137`
en `00000_07999` pertenece a la generación interrumpida del 1 de octubre.
Todavía no existen códigos de salida ni productos aceptados. `with_methane`
continúa activo; `river_routing=false` y `reservoir=false` limitan la lectura
al routing local desactivado. Se seguirá revisando con más frecuencia la RAM y
el swap después del aumento de concurrencia.

**Revisión 2026-10-02 20:00 COT:** los cuatro LPJmL permanecen activos; una
muestra de seis segundos mostró 48.4--49.4 % de CPU por proceso y un aumento
de alrededor de tres segundos en el tiempo de CPU por worker. El RSS se asentó
en 4.2--4.6 GiB por proceso. La RAM disponible bajó a 12 GiB mientras la swap
sigue en cero; quedan 516 GiB libres en disco. Los segmentos aún no han escrito
filas anuales nuevas desde el arranque, pero los contadores de CPU crecen y no
hay códigos de salida ni errores actuales. Se mantiene el límite de cuatro y
se vigilará si la memoria disponible cae o empieza el uso de swap.

## Interrupción confirmada — 2026-10-02 18:43 COT

El archivo de campaña todavía dice `POTENTIAL_CHUNKS_RUNNING`, pero ya no hay
procesos `run_capacity_potential_chunks`, `checkpoint_runner`, `mpirun` ni
LPJmL. Dos comprobaciones, a las 18:43:38 y 18:43:49 COT, confirmaron la
ausencia de procesos y los mismos tamaños y fechas para campaign/launcher,
`run_status.txt`, controllers, segmentos y checkpoints. Los estados por bloque
solo conservan rango e inicio; no hay códigos de salida finales. No se inició
otra copia.

Últimas filas anuales registradas: 1561 para `00000_07999`, 1489 para
`08000_15999` y 1486 para `16000_23999`. Los checkpoints más recientes,
comparados por SHA-256 entre restart, archivo de checkpoints y registro
`CHECKPOINT_SAVED` del controller, son:

- `00000_07999`: `1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212`.
- `08000_15999`: `836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1`.
- `16000_23999`: `7f3b065e67ed12d4ec1703faf068cb07d16667a83879fa04cde7b35e6d19077e`.

Estos hashes confirman la copia byte a byte frente a controller; `lpjcheck`
aún no se ha ejecutado sobre estos tres guardados más recientes. El stderr de
controller de `00000_07999` conserva el fallo histórico `LPJmL exit 137` del
1 de octubre a las 01:45 COT; los otros dos controller stderr están vacíos.
Los segmentos recientes solo presentan advertencias. En el host hay 30 GiB de
RAM disponibles, no hay swap usada y quedan 517 GiB libres en disco, así que la
interrupción no coincide con presión actual de esos recursos.

La campaña usaba bloques de 8.000 celdas, un rank MPI por bloque, CH4,
`MAX_PARALLEL=3` y retención completa (`MAX_ARCHIVED_CHECKPOINTS=0`). Se
mantienen `river_routing=false` y `reservoir=false`, por lo que la
interpretación queda limitada al routing local desactivado. La recuperación
queda pendiente; no se debe iniciar otra copia sin instrucción del usuario.

## Interrupción del reinicio con cuatro bloques — 2026-10-02 21:14 COT

La ejecución se reanudó a las 19:50:33 COT con `MAX_PARALLEL=4`, bloques de
8.000 celdas, un rank MPI por bloque, CH4 y retención completa. A las 20:11
los cuatro workers seguían activos. A las 21:13 y 21:14 no se encontraron
procesos `run_capacity_potential_chunks`, `checkpoint_runner`, `mpirun` ni
LPJmL. El tamaño y la fecha de los segmentos actuales no cambian desde las
19:51--19:53; `campaign_status.txt` sigue diciendo RUNNING y no es evidencia
de actividad. Los archivos `run_status.txt` solo registran los cuatro
identificadores y `started_utc`; no hay código de salida final.

Los tres checkpoints de reanudación se volvieron a verificar. Para cada uno,
el restart coincide byte a byte con su copia archivada (`cmp` exit 0), el
SHA-256 coincide con el registro `CHECKPOINT_SAVED` del controller y
`lpjcheck -pedantic` terminó con exit 0:

- `00000_07999`, año 1560: `1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212`.
- `08000_15999`, año 1488: `836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1`.
- `16000_23999`, año 1486: `7f3b065e67ed12d4ec1703faf068cb07d16667a83879fa04cde7b35e6d19077e`.

`24000_31999` arrancó desde A0 a las 19:50:33 y no guardó checkpoint; los
logs de ese segmento no contienen cierre ni fila anual. El estado actual no
presenta exit codes finales ni productos aceptados. No se encontró evidencia
OOM en `dmesg` o `journalctl -k` accesibles; la causa de la terminación queda
indeterminada. Después de la interrupción había 30 GiB disponibles, swap sin
uso y 516 GiB libres en `/home`, así que esa lectura no muestra presión de
recursos. La campaña permanece detenida y no se inició otra copia. La
configuración conserva `river_routing=false` y `reservoir=false`; toda
interpretación queda limitada al routing local desactivado.



## Reanudación con cinco bloques — 2026-10-02 21:56 COT

Después del reinicio del PC/WSL, la lectura viva de las 21:49 confirmó que WSL acababa de iniciar y no había procesos LPJmL, `mpirun` ni `checkpoint_runner`. `campaign.lock.d` estaba vacío y se retiró con `rmdir` para liberar el bloqueo obsoleto. El usuario autorizó reanudar y aumentar el paralelismo. Los tres checkpoints guardados volvieron a compararse byte a byte con sus copias archivadas (`cmp` exit 0), se recalcularon sus SHA-256 y `lpjcheck -pedantic` terminó con exit 0:

- `00000_07999`, checkpoint año 1560: `1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212`.
- `08000_15999`, checkpoint año 1488: `836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1`.
- `16000_23999`, checkpoint año 1486: `7f3b065e67ed12d4ec1703faf068cb07d16667a83879fa04cde7b35e6d19077e`.

El lanzador volvió a adquirir el bloqueo y puso en marcha la campaña a las 21:55:35 COT con `MAX_PARALLEL=5`, `MPI_RANKS=1`, `CHUNK_SIZE=8000`, CH4, `MAX_ARCHIVED_CHECKPOINTS=0` y checkpoints cada hora. A las 21:56:37 se observaron cinco procesos `mpirun -np 1` y cinco procesos LPJmL para `00000_07999`, `08000_15999`, `16000_23999`, `24000_31999` y `32000_39999`. Los tres primeros retomaron de sus checkpoints; los dos nuevos empezaron desde A0. WSL expone 16 CPU lógicas y 31 GiB de RAM; en esa lectura había 29 GiB disponibles, no se usaba swap y `/home` tenía 515 GiB libres. Los procesos llevaban seis segundos y todavía mostraban RSS de arranque (0.1--0.3 GiB); se requiere otra muestra cuando se estabilice el consumo. La generación no tiene exit codes finales ni productos aceptados y su aumento de velocidad aún no se ha medido.

Cinco bloques concurrentes de un rank aumentan el paralelismo de cuatro con margen prudente para los estados grandes por proceso. No se aumentaron los ranks MPI dentro de cada bloque. Se conservan `river_routing=false` y `reservoir=false`; la selección no representa routing global y sus resultados deben interpretarse con esa limitación.



## Seguimiento estabilizado — 2026-10-02 22:09 COT

Los cinco pares mpirun -np 1/LPJmL siguen activos. Cada LPJmL muestra 39.5–40.0 % de CPU y 4.4–4.8 GiB de RSS; quedan 8.4 GiB disponibles, no se usa swap y /home conserva 515 GiB libres. Los stdout actuales siguen con mensajes de arranque; los stderr muestran advertencias conocidas y el escaneo no encuentra error, fatal, failed, killed ni fallos de segmentación. Las advertencias registran 1489 después de reanudar 08000 desde 1488 y 1481 en 24000 iniciado desde A0. No hay códigos de salida ni checkpoints nuevos desde la reanudación. El consumo se acercó a los niveles típicos previos por proceso; se mantiene el límite de cinco para conservar margen de memoria.

## RAM más ajustada, workers aún activos — 2026-10-03 00:29 COT

La revisión encontró cinco LPJmL activos, cada uno con cerca de 40% de CPU y RSS entre 4.6 y 5.7 GiB. Quedan 4.3 GiB de RAM disponible, frente a 5.2 GiB en la revisión de las 23:29 COT (8.3 GiB a las 22:23); la swap usada es solo 6.5 MiB y `/home` conserva 515 GiB libres. Es una reducción del margen de memoria, sin evidencia de fallo por ahora. Se conserva `MAX_PARALLEL=5`; no se aumenta ni se detiene ningún bloque automáticamente.

Los `run_status.txt` continúan en ejecución y no muestran códigos de salida. Los controladores aún no registran checkpoints posteriores al reinicio de las 21:55 COT: los tres bloques reanudados conservan los checkpoints ya validados, mientras `24000_31999` y `32000_39999` todavía no tienen uno de esta generación. Los segmentos stdout no muestran aún la fila anual parseable que activa el checkpoint del wrapper. El [código de `checkpoint_runner.py`](../Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction/checkpoint_runner.py#L109) envía SIGTERM para guardar solo cuando aparece una fila anual y se cumple el intervalo de 3600 s; por tanto, con CPU activa la falta actual de checkpoint es compatible con una fase larga sin salida anual y no demuestra interrupción. El escaneo de los stderr de la generación activa no encontró errores fatales. Se comprobará de nuevo RAM, actividad, logs y checkpoints en el siguiente ciclo.

No hay exit codes finales ni productos aceptados. Se mantienen `river_routing=false` y `reservoir=false`, que limitan la interpretación al routing local desactivado.


## Seguimiento con swap alta — 2026-10-04 01:46 COT

La inspección de campaign_status.txt, controladores, estados por bloque, segmentos y procesos confirma que la generación iniciada el 2026-10-02 21:55:35 COT sigue activa en sus cinco bloques, con un rank MPI por bloque, salida CH4, MAX_PARALLEL=5 y retención completa (MAX_ARCHIVED_CHECKPOINTS=0). Los cinco procesos LPJmL usan aproximadamente 39,6–40,0% de CPU.

Se verificaron los archivos de checkpoint más recientes contra el SHA-256 de controller.log; en los cinco bloques el restart activo coincide con el checkpoint archivado. Los hashes son:

- 00000_07999: 88f680589b802dd42ca806fb59eaa8c23ed4f84ed0cc2543fc11e8481c29c60f (checkpoint tras la fila 1561).
- 08000_15999: e8a62f04e7ec5b47c6e9e3468fc6a38910743f8cca7c659f0897ae23bdafcd2b; cmp pasó y lpjcheck -pedantic devolvió 0, indicando restart desde el año 1492.
- 16000_23999: eacf565edfd881572b7db1cbf64eae100f060af6b19836dc24d16a4e0a886ec3 (checkpoint tras la fila 1490).
- 24000_31999: 0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa; cmp pasó y lpjcheck -pedantic devolvió 0, indicando restart desde el año 1484.
- 32000_39999: 56929c418b142ba637156110295a9c531f9e3a0b7bf5c1d48adb204127fdd792 (checkpoint tras la fila 1481).

Los segmentos recientes muestran que los modelos siguen trabajando y no hay un error fatal nuevo ni códigos de salida finales. El traceback con exit 137 de 00000_07999 corresponde al incidente del 2026-10-01, anterior a la generación vigente. En recursos, quedan 11 GiB de RAM disponible y 503 GiB libres en /home; la swap subió a 7,0 de 8,0 GiB. vmstat 1 3 mostró actividad de swap solo en el primer muestreo y cero intercambio en los dos siguientes, sin paginación sostenida. Por el margen reducido de swap, se mantiene MAX_PARALLEL=5 y no se aumenta el número de procesos.

No hay productos aceptados ni exit codes finales. Se mantienen river_routing=false y reservoir=false; los resultados representan la configuración con routing local desactivado.


## Seguimiento con checkpoint renovado — 2026-10-04 02:46 COT

La campaña permanece activa en cinco bloques: cinco pares mpirun/LPJmL, un rank por bloque, MAX_PARALLEL=5, CH4 y retención completa. El bloque 00000_07999 guardó el checkpoint c59f10b4ee452d24259ae591ede142485bdc26413dbd381c758222ba9e1cfd6d. Su SHA-256 coincide entre controller.log, el archivo archivado y restart/checkpoint.lpj; cmp pasó y lpjcheck -pedantic terminó con código 0 e indicó reanudación desde el año 1564.

Los checkpoints vigentes de los otros bloques no cambiaron y también coinciden entre restart, archivo y hash del controlador: 08000_15999 e8a62f04e7ec5b47c6e9e3468fc6a38910743f8cca7c659f0897ae23bdafcd2b; 16000_23999 eacf565edfd881572b7db1cbf64eae100f060af6b19836dc24d16a4e0a886ec3; 24000_31999 0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa; 32000_39999 56929c418b142ba637156110295a9c531f9e3a0b7bf5c1d48adb204127fdd792. Los cinco LPJmL usan cerca de 40% de CPU. Los logs actuales y stderr revisados no muestran error fatal nuevo ni códigos de salida finales; el exit 137 observado en el stderr de 00000_07999 es histórico y corresponde al 2026-10-01.

Quedan 12 GiB de RAM disponible, la swap usada bajó a 6,7 de 8 GiB y /home tiene 502 GiB libres. vmstat 1 4 mostró actividad de swap en el primer intervalo y cero en los tres posteriores, sin intercambio sostenido. Se mantiene MAX_PARALLEL=5 y no se amplía. No hay productos aceptados. Se conservan river_routing=false y reservoir=false, por lo que la interpretación se limita al routing local desactivado.


## Seguimiento con nuevo checkpoint en 32000_39999 — 2026-10-04 03:47 COT

La campaña continúa activa en sus cinco bloques, con un rank MPI por bloque, MAX_PARALLEL=5, salida CH4 y retención completa. 32000_39999 guardó el checkpoint dc6f24a5fc1adb6fc9c56703f664ca75590d7986c25eb90981b7bb9a4dbf3864. El SHA-256 del controlador coincide con el archivo archivado y restart/checkpoint.lpj; cmp pasó y lpjcheck -pedantic terminó con código 0, indicando restart desde el año 1484.

Los checkpoints vigentes de los otros cuatro bloques siguen coincidiendo entre el evento más reciente de controller.log, el archivo archivado y el restart activo: 00000_07999 c59f10b4ee452d24259ae591ede142485bdc26413dbd381c758222ba9e1cfd6d; 08000_15999 e8a62f04e7ec5b47c6e9e3468fc6a38910743f8cca7c659f0897ae23bdafcd2b; 16000_23999 eacf565edfd881572b7db1cbf64eae100f060af6b19836dc24d16a4e0a886ec3; 24000_31999 0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa. Los cinco procesos muestran aproximadamente 39–40% de CPU; los segmentos recientes y stderr no presentan error fatal nuevo. Los run_status siguen activos y no hay exit codes finales ni productos aceptados. El error exit 137 de 00000_07999 pertenece al incidente del 2026-10-01.

La memoria disponible es 11 GiB, la swap ocupada es 6,5 de 8 GiB y /home conserva 501 GiB libres. vmstat 1 4 mostró intercambio en el primer intervalo y cero en los tres siguientes. No hay paginación sostenida observada; se conserva MAX_PARALLEL=5 y no se aumenta. Continúan las limitaciones river_routing=false y reservoir=false, que restringen la interpretación al routing local desactivado.


## Swap casi agotada, procesos activos — 2026-10-04 04:48 COT

La campaña continúa activa en los cinco bloques, un rank MPI por bloque, MAX_PARALLEL=5, CH4 y retención completa. Todos los procesos LPJmL consumen entre 39,7 y 39,9% de CPU. No hubo cambios en los últimos checkpoints: 00000_07999 c59f10b4ee452d24259ae591ede142485bdc26413dbd381c758222ba9e1cfd6d; 08000_15999 e8a62f04e7ec5b47c6e9e3468fc6a38910743f8cca7c659f0897ae23bdafcd2b; 16000_23999 eacf565edfd881572b7db1cbf64eae100f060af6b19836dc24d16a4e0a886ec3; 24000_31999 0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa; 32000_39999 dc6f24a5fc1adb6fc9c56703f664ca75590d7986c25eb90981b7bb9a4dbf3864. En los cinco bloques, el hash del restart activo coincide con el último hash de controller.log y el archivo archivado.

La lectura de recursos muestra 11 GiB de RAM disponible, 7,8 de 8,0 GiB de swap ocupados (161 MiB libres) y 501 GiB libres en /home. vmstat 1 4 solo mostró actividad de intercambio en el primer intervalo; los tres posteriores registraron si/so cero, sin paging sostenido. Los run_status siguen activos; los logs revisados no contienen errores fatales nuevos ni códigos finales. El exit 137 en controller.stderr de 00000_07999 continúa siendo el incidente histórico del 2026-10-01. Se mantiene MAX_PARALLEL=5, sin ampliarlo, y se vigila la capacidad de memoria.

No hay productos aceptados. Se conservan river_routing=false y reservoir=false, por lo que los resultados representan routing local desactivado.


## Swap completa, workers activos — 2026-10-04 05:49 COT

La campaña sigue RUNNING con los cinco bloques activos, un rank MPI por bloque, salida CH4, retención completa y MAX_PARALLEL=5. Los cinco LPJmL consumen 39,8–39,9% de CPU. No se registraron checkpoints nuevos ni códigos de salida finales. Los hashes vigentes siguen siendo 00000_07999 c59f10b4ee452d24259ae591ede142485bdc26413dbd381c758222ba9e1cfd6d; 08000_15999 e8a62f04e7ec5b47c6e9e3468fc6a38910743f8cca7c659f0897ae23bdafcd2b; 16000_23999 eacf565edfd881572b7db1cbf64eae100f060af6b19836dc24d16a4e0a886ec3; 24000_31999 0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa; 32000_39999 dc6f24a5fc1adb6fc9c56703f664ca75590d7986c25eb90981b7bb9a4dbf3864. Los archivos de restart siguen coincidiendo con los checkpoints archivados y los hashes de controlador.

free -h informa 11 GiB disponibles, aunque los 8 GiB de swap están ocupados y no queda swap libre; /home conserva 501 GiB. vmstat 1 4 mostró actividad de intercambio en el primer intervalo y cero en los tres posteriores, sin paginación sostenida durante la muestra. Este es un margen reducido para picos de memoria: se mantiene el máximo ya autorizado de cinco procesos, sin ampliarlo ni detener workers automáticamente. Los stderr recientes no muestran errores fatales; el exit 137 de 00000_07999 sigue siendo histórico (2026-10-01).

No hay productos aceptados ni exit codes finales. Se conservan river_routing=false y reservoir=false como limitaciones de interpretación.


## Checkpoint validado en 16000_23999 — 2026-10-04 06:49 COT

Los cinco bloques siguen activos, con un rank MPI por bloque, MAX_PARALLEL=5, salida CH4 y retención completa. 16000_23999 guardó el checkpoint 8320adbef33619710eada5a49c9c87522116b4ded3b100e9580b38dd87d88605. El hash del controlador coincide con los archivos archivado y restart; cmp pasó y lpjcheck -pedantic terminó con exit 0 e indicó reanudación desde el año 1492.

Los otros hashes vigentes permanecen iguales y coinciden con los respectivos archivos de checkpoint: 00000_07999 c59f10b4ee452d24259ae591ede142485bdc26413dbd381c758222ba9e1cfd6d; 08000_15999 e8a62f04e7ec5b47c6e9e3468fc6a38910743f8cca7c659f0897ae23bdafcd2b; 24000_31999 0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa; 32000_39999 dc6f24a5fc1adb6fc9c56703f664ca75590d7986c25eb90981b7bb9a4dbf3864. Todos los LPJmL mantienen aproximadamente 39,8–39,9% de CPU y los segmentos recientes no muestran error fatal nuevo. El exit 137 almacenado en el stderr de 00000_07999 sigue fechado 2026-10-01; no corresponde a esta ejecución. No hay códigos finales ni productos aceptados.

La presión de memoria bajó respecto a la muestra anterior: quedan 10 GiB de RAM disponible, swap usada 6,8 de 8 GiB y 500 GiB libres en /home. vmstat 1 4 mostró actividad breve de intercambio, seguida por tres intervalos sin si/so. No se observó paginación sostenida; se conserva MAX_PARALLEL=5. La interpretación mantiene river_routing=false y reservoir=false, es decir, routing local desactivado.
