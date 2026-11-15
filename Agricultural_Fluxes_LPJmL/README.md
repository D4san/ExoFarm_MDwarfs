**FR-Genghis, pausa solicitada 2026-10-04 16:38 COT:** campaña detenida por el usuario; se terminaron scheduler, cinco workers, cinco `checkpoint_runner`, cinco `mpirun` y cinco LPJmL tras verificar las rutas y los cinco bloques. No quedan procesos ni lock. Los checkpoints en años 1566/1494/1494/1484/1484 pasaron la verificación de SHA-256 y `lpjcheck -pedantic` (exit 0); no hay códigos finales ni productos aceptados. Mantener pausada hasta nueva autorización. Configuración al detener: bloques de 8.000 celdas, un rank MPI por bloque, CH4, `MAX_PARALLEL=5`, retención completa. `river_routing=false` y `reservoir=false` limitan la interpretación al routing local desactivado. Detalles: [registro de pausa](../docs/fr_genghis_campaign_pause_2026-10-04.md).

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
> **FR-Genghis interrumpido — revisión 2026-10-02 21:14 COT:** el reinicio con `MAX_PARALLEL=4`, un rank MPI por bloque de 8.000 celdas, CH4 y retención completa quedó sin procesos: dos comprobaciones a las 21:13 y 21:14 confirmaron la ausencia de workers. Los logs de la generación actual no crecieron después de las 19:53; `campaign_status.txt` quedó con RUNNING obsoleto. Los checkpoints de 00000/08000/16000 (años 1560/1488/1486) coinciden restart/archivo por SHA-256 y pasaron `lpjcheck -pedantic` con exit 0: `1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212`, `836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1` y `7f3b065e67ed12d4ec1703faf068cb07d16667a83879fa04cde7b35e6d19077e`. 24000 inició desde A0 y no tiene checkpoint. Sin códigos finales ni productos aceptados; la causa de la interrupción queda sin determinar y no se relanzó otra copia automáticamente. `river_routing=false` y `reservoir=false` limitan la interpretación al routing local desactivado. Informe: [`paralelismo de bloques`](../docs/lpjml_capacity_chunk_parallelism_2026-10-01.md).

> **FR-Genghis, revisión 2026-10-02 14:36 COT:** los tres bloques siguen corriendo CH4 con un rank MPI cada uno, `MAX_PARALLEL=3` y retención completa. Últimos años visibles: 1560, 1488 y 1485. Checkpoints SHA-256: `1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212`, `836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1` y `7f3b065e67ed12d4ec1703faf068cb07d16667a83879fa04cde7b35e6d19077e`; el tercero se guardó a las 14:29 COT. Los dos primeros siguen activos sin nuevas filas desde 12:34 COT. Sin códigos finales ni salida aceptada. RAM disponible 14 GiB, swap 95 MiB y 517 GiB libres; sin presión inmediata. `river_routing=false` y `reservoir=false` limitan la interpretación.

> **FR-Genghis, revisión 2026-10-02 13:38 COT:** continúan activos los tres bloques CH4 con CPU creciente. Las últimas filas siguen en 1560, 1488 y 1485; los checkpoints activos tienen SHA-256 `1f43bf9901be316f4ab6885e75ae14eaeced573048d640d2a9dc8aa012762212`, `836c31b82f3b9a788e530e071aeced8c0ea09d8707d014f50a47171865d9f3e1` y `e9d67152cc7770b7a53e11440effa12ed699d984969f1d53967c0199a0ae14ce`. Sin avance anual desde 12:34 COT ni códigos finales; los stderr recientes solo muestran advertencias. Hay 15 GiB disponibles, 575 MiB de swap y 518 GiB libres; sin presión inmediata. Configuración vigente: tres bloques, un rank MPI cada uno, retención completa, routing/embalses locales desactivados. No se acepta producto de la campaña.

> **FR-Genghis, estado 2026-10-02 01:27 COT:** siguen activos los tres
> bloques CH4 con un rank MPI por bloque, `MAX_PARALLEL=3` y retención
> completa. `00000_07999` registra 1557 y conserva el checkpoint 1556
> (`f150c32b9c5ebdbe9202cf15dc18785d35d0c4efa20575f301ba2db9541c2080`);
> `08000_15999` registra 1485 y conserva el checkpoint 1484
> (`7d687ce9dfc6fe08478f181152cce943f9095f19b37d7e583833e939574f4e85`).
> `16000_23999` guardó el año 1482
> (`de713797e50d9ccf0b3b9a67eb89746035f3eb9f36f436377364c1745757f857`);
> `lpjcheck -pedantic` terminó con código 0. No hay códigos finales ni
> salida aceptada. Quedan 14 GiB de RAM disponibles, swap usada 1.5 MiB y
> 523 GiB libres en disco; no se ve presión de recursos. Routing y embalses
> siguen desactivados, lo que limita la interpretación.

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

> **FR-Genghis reanudado 2026-09-22 20:48 America/Bogota:** la campaña
> candidata está activa otra vez desde el checkpoint íntegro del bloque
> `00000_07999` (`sha256=80c0a282b424c4f5f6b9faae3eca2b8f2c69e40f4fa9fe4a2ee43fe39e71f52a`).
> Se confirmó que no había procesos anteriores antes de reanudar. El bloque
> todavía está en cálculo; no se aceptan flujos de esta fase.

> **FR-Genghis reanudado con tres bloques 2026-10-01 18:51 COT:** tras un
> reinicio de WSL se confirmó que no quedaban procesos y que el bloqueo global
> estaba vacío. El usuario autorizó reanudar con más paralelismo. Ahora corren
> tres bloques de 8.000 celdas, un rank MPI por bloque, CH4 y retención completa
> (`MAX_PARALLEL=3`, `MAX_ARCHIVED_CHECKPOINTS=0`). `00000_07999` retomó desde
> año 1556, SHA-256
> `f150c32b9c5ebdbe9202cf15dc18785d35d0c4efa20575f301ba2db9541c2080`;
> `08000_15999`, desde año 1484, SHA-256
> `7d687ce9dfc6fe08478f181152cce943f9095f19b37d7e583833e939574f4e85`.
> `lpjcheck` aceptó ambos reinicios. `16000_23999` inició desde A0 y todavía
> no tiene checkpoint. La primera lectura registró 25 GiB disponibles, cero
> swap y 525 GiB libres; el aumento real de velocidad sigue sin medirse. La
> interpretación conserva `river_routing=false` y `reservoir=false`. Véase
> [`informe de paralelismo`](../docs/lpjml_capacity_chunk_parallelism_2026-10-01.md).
> Revisión 19:08 COT: siguen activos los tres procesos LPJmL; una muestra
> instantánea registró 80 %, 68 % y 52 % de CPU, con 4.2--4.7 GiB de RSS por
> proceso. Quedan 17 GiB disponibles, no se usa swap y hay 525 GiB libres. Los hashes de los
> dos reinicios siguen coincidiendo; las bitácoras de esta generación aún no
> reportan un año simulado nuevo ni se ha guardado checkpoint del bloque nuevo.

> **FR-Genghis en paralelo 2026-10-01 05:14 COT:** los bloques
> `00000_07999` y `08000_15999` están activos en la campaña CH4, con un rank
> MPI por bloque, `MAX_PARALLEL=2` y retención completa de checkpoints. El
> bloque 0 reanudó desde año 1552; su SHA-256 es
> `5c0073cbf3acce68e5b2d6d4a43df66dde3217b2318bbe547e93f6a20fda52df`. La
> última salida del bloque 0 reporta año 1553. El bloque 1 guardó y reanudó año
> 1482 con SHA-256 íntegro
> `79698dfb5cd3558c13c2219bf8fe6d862fade574c11a27764c74acec48577f79`.
> ganancia todavía no está medida y la selección sigue incompleta. Hubo un
> lanzamiento inicial corto en otro directorio; se detuvo sin aceptar sus
> archivos y estos quedaron preservados aparte. Detalles y pruebas:
> `docs/lpjml_capacity_chunk_parallelism_2026-10-01.md`.

> **A0 validado 2026-09-22:** el control natural global terminó con `exit_code=0` y pasó cobertura, finitud, máscaras, unidades e integración 1996--2005. El contraste A0/A1 está en `docs/lpjml_global_a0_control_validation_2026-09-22.md`; NH3 requiere resolver la diferencia con la referencia congelada antes de acoplar la fotoquímica.

> **Control natural A0 reanudado 2026-09-21 00:30 UTC:** el proceso llegó al
> año 1587, conservó el checkpoint `4c6dfe69fd019922380ab6196ba52572365734b44219f2d3db64298387149b7c` y fue relanzado desde ese archivo tras una interrupción externa de WSL. Ocho ranks siguen activos; la salida A0 todavía no está validada.

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

# LPJmL Agricultural Fluxes

> **Cierre global A1 2026-09-20:** `global_a1_checkpoints_20260909` terminó con
> `exit_code=0` usando ocho ranks del build
> `LPJmL-6.0.6-balance-fix-20260912`. La validación de 67 420 celdas y diez
> años (1996--2005), el checkpoint SHA-256 y la integración global de N2O/NH3
> pasaron. El resultado es una emisión agrícola de stand. El control natural
> emparejado ya está validado; el contraste A0/A1 y la decisión pendiente sobre
> NH3 están en el [informe A1](../docs/lpjml_global_a1_validation_2026-09-20.md)
> y el [informe A0](../docs/lpjml_global_a0_control_validation_2026-09-22.md).

> **Global A1 lanzado 2026-09-07 (registro histórico):** `global_a1_20260907`
> abrió el spin-up de 67,420 celdas con ocho ranks MPI en Ubuntu sobre E:. La
> campaña aceptada posterior y su control A0 están documentados arriba.
> [Registro](../docs/lpjml_global_a1_campaign_2026-09-07.md).

> **Prueba MPI 2026-09-07 aceptada:** ocho celdas y dos ranks completaron
> spin-up/A1; reinicio, NetCDF y ocho pruebas de cálculo verificados.
> [Resultados y salvedades](../docs/lpjml_mpi_smoke_validation_2026-09-07.md).
> El piloto no producía flujos planetarios; las campañas globales posteriores sí
> quedaron validadas y se enlazan en el cierre de arriba.

> **Recuperación local 2026-09-07:** datos oficiales descargados, verificados y extraídos en Ubuntu,
> alojado en E:, y build Open MPI 6.0.6 compilado con `make test` pasado. Las rutas históricas de datos
> no existen en este PC. Consultar el [registro actual](../docs/lpjml_wsl_storage_recovery_2026-09-07.md)
> antes de interpretar el piloto previo como instalación local disponible.

This module defines the LPJmL-centered upstream agricultural-flux layer for
ExoFarm.

LPJmL (Lund-Potsdam-Jena managed Land) is a global dynamic vegetation, managed
land, and hydrology model. For ExoFarm, its useful role is not to prescribe
atmospheric abundances directly. Its role is to estimate spatially explicit
land-use, crop, water, carbon, and nitrogen fluxes, then let the photochemical
stage decide the atmospheric response.

> **Estado de proyecto (2026-09-06): primera prueba de interfaz aceptada.**
> LPJmL `v6.0.6` (commit
> `5af44a1ed023279a23c28d6dfe76945b97aaac57`) compila y pasa las comprobaciones
> locales. El paquete oficial fue verificado por tamaño/MD5 y extracción; el
> piloto de una celda completó el benchmark con ciclo de N y la rama de
> rendimiento potencial, incluyendo NetCDF de `N2O` y `NH3`. Todavía no existe
> un flujo **global** LPJmL aceptado ni un nuevo forzamiento para VULCAN.
> Para recuperar el estado completo, leer
> [`../docs/project_resume.md`](../docs/project_resume.md).

## Role in the ExoFarm Pipeline

The intended workflow is:

1. Define global or regional ExoFarm scenarios through land use, crop mix,
   fertilizer, manure, irrigation, residue, tillage, and climate assumptions.
2. Run an LPJmL version with nitrogen cycling enabled.
3. Extract nitrogen-loss outputs relevant to atmospheric forcing, especially:
   - `N2O_DENIT` and `N2O_NIT`
   - agricultural variants such as `N2O_DENIT_AGR`, `N2O_NIT_AGR`, and `NH3_AGR`
   - diagnostic reservoirs such as `N2_EMIS`, `N2_AGR`, leaching, uptake,
     fertilizer, manure, and deposition.
4. Convert nitrogen-mass fluxes into molecules cm^-2 s^-1 before passing them
   to VULCAN or another atmospheric chemistry model.
5. Map the resulting surface fluxes into the ExoFarm scenario matrix:
   - `A0`: pre-agricultural baseline
   - `A1`: current Earth benchmark
   - `A2`: moderate ExoFarm forcing
   - `A3`: extreme ExoFarm forcing

## Local Contents

- `docs/consideraciones_exofarm_lpjml.md`: research notes and first workflow.
- `docs/lpjml_sources.bib`: bibliography for the LPJmL papers and tools read for
  this pivot.
- `scripts/convert_lpjml_n_flux.py`: small unit converter from LPJmL-style
  nitrogen-mass fluxes to atmospheric molecule fluxes.
- `workflows/franck2011_reproduction/`: reproducción metodológica moderna de
  la capacidad de carga y puente auditable hacia `N2O`/`NH3`.
- `../docs/lpjml_franck2011_first_pilot_2026-09-06.md`: informe de aceptación
  del piloto de una celda y sus límites científicos.
- `../docs/lpjml_global_a1_mpi_other_pc_runbook.md`: instalación reproducible
  de LPJmL 6.0.6 con MPI y estrategia por fases para la primera corrida global
  A1 en el PC de ejecución.

A local upstream LPJmL checkout may live under `software/LPJmL/`, but it is not
vendored as ExoFarm source and is ignored by the top-level Git configuration.
Record its version or commit in each experiment record. Keep official input
datasets outside Git, document their path, and keep ExoFarm scripts and derived
outputs separate from the upstream model distribution.

## Conversion Principle

LPJmL nitrogen outputs are nitrogen-mass fluxes, not atmospheric abundance
targets. For example, an `N2O` output reported as grams of nitrogen per square
meter per year must be converted through nitrogen atoms:

```text
g N -> mol N -> mol N2O = mol N / 2 -> molecules N2O -> cm^-2 s^-1
```

For `NH3`, the nitrogen atom count is one. This distinction matters: converting
`N2O-N` as if it were whole `N2O` mass would bias the lower-boundary flux.

## First Local Checks Once LPJmL Is Installed

```bash
./bin/lpjml -h
./bin/lpjml -ofiles
./bin/lpjcheck lpjml_config.cjson
python Agricultural_Fluxes_LPJmL/scripts/convert_lpjml_n_flux.py --help
```

Before trusting a flux file, record the LPJmL version, the active configuration,
the output units, whether outputs are grid-scaled, and whether the source values
are total grid-cell fluxes or per-area fluxes.







> **Reanudación A1 autorizada 2026-09-19 04:53 America/Bogota:** la campaña global volvió a ejecutar desde el checkpoint íntegro de 1738 con ocho ranks y el build corregido `LPJmL-6.0.6-balance-fix-20260912`; el spin-up natural completado se conserva. Productos 1996–2005 y comparación N2O/NH3 continúan pendientes.
