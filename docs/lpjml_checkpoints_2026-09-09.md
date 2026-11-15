> **Reanudación 2026-09-09 20:43 America/Bogota:** usuario confirma apagado del PC como causa de la interrupción y autoriza continuar. Checkpoint activo verificado por SHA256; lpjcheck confirma año -1578 y ocho procesos LPJmL activos. Campaña global_a1_checkpoints_20260909 reanudada desde ese estado para continuar en -1577; checkpoints horarios y seguimiento activos. A1 seguirá tras spin-up. Notas anteriores conservadas como historial.

> **Incidente 2026-09-09 15:57 America/Bogota:** global_a1_checkpoints_20260909 interrumpida; dos consultas sin procesos y WSL recién iniciado. Último log -1562 a las 15:15:41. Checkpoint de las 15:00 al año -1578 íntegro: SHA256 recalculado del activo y copia archivada coincide con 3dcda941501b5240d8d1a1eadeb1b6a136db8897a27a0b98d3f39be756048b93. Recuperación disponible desde -1577; 16 años de avance posterior no guardados. Causa del cierre pendiente. No se relanzó; seguimiento pausado. A1 y comparación pendientes.

# Checkpoints LPJmL: validación inicial, 2026-09-09

El controlador [checkpoint_runner.py](../Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction/checkpoint_runner.py)
solicita SIGTERM al rank cero de su propio proceso MPI, espera la salida
ordenada y conserva una copia con SHA256 antes de continuar. El intervalo
predeterminado es 3600 segundos; el guardado espera el cierre del año simulado.
Una cerradura impide dos controladores en el mismo directorio.

## Fuente y mecanismo

LPJmL 6.0.6, commit 5af44a1ed023279a23c28d6dfe76945b97aaac57.
`src/lpj/iterate.c` instala el manejador cuando existe checkpoint_filename,
escribe el checkpoint tras SIGTERM y sale con código cero. Al reanudar toma
checkpointyear+1; elimina el checkpoint activo tras completar la fase.
Por eso una salida cero aislada no demuestra finalización de la simulación.

## Prueba ejecutada

Directorio Ubuntu (almacenamiento físico E:):
`/home/dasan/exofarm-lpjml-runs/checkpoint_test_20260909`.
Config copiada del piloto MPI de ocho celdas, dos ranks, 2100 años de spin-up;
única adición científica/operativa: checkpoint_filename absoluto.
Primer segmento con intervalo 10 segundos y max-checkpoints=1; segundo
segmento con intervalo 3600 segundos hasta terminar.

- Guardado ordenado al año -389; copia archivada y SHA256 registrado.
- Reanudación confirmada por el solver desde checkpoint; años -388–1700.
- Salida cero y reinicio final producido.
- Los 2089 años de diagnósticos impresos coinciden con el piloto continuo,
  sin diferencias a la precisión del log.
- Los hashes binarios finales difieren. fwriterestart.c incorpora fecha y
  argumentos en history; no se ha demostrado igualdad binaria del estado
  científico, ni debe inferirse de los diagnósticos redondeados.

Evidencia: config.json, segment_*.stdout.log, segment_*.stdout.stderr.log,
checkpoints/*.lpj y *.sha256, restart/restart_1700_nv_stdfire.lpj en el directorio
de prueba. Referencia continua: ../mpi_smoke_20260907/spinup_natural.

## Actualización: A1 validado y campaña lanzada

2026-09-09 07:49 America/Bogota: campaña `global_a1_checkpoints_20260909`
lanzada desde cero y verificada con ocho procesos LPJmL activos, tras lpjcheck
con entradas y directorios presentes. Ruta `/home/dasan/exofarm-lpjml-runs/global_a1_checkpoints_20260909`
en E:. La campaña interrumpida permanece intacta. A1 sigue automáticamente tras
completar el spin-up. Seguimiento horario reactivado para la nueva ruta.

La prueba [test_checkpoint_a1.py](../Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction/test_checkpoint_a1.py)
guardó al finalizar 1998, reanudó hasta 2005 y comparó exactamente todas las
matrices y dimensiones de los 13 NetCDF con el piloto continuo: PASS.
Incluye N2O de nitrificación/desnitrificación, NH3, áreas y diagnósticos de N.
Evidencia en `/home/dasan/exofarm-lpjml-runs/checkpoint_a1_20260909/validation.json`
y sus config, segmentos y checkpoints. Se activó flush_output para solicitar
el checkpoint durante el periodo con salidas; no se cambiaron parámetros físicos.

El [lanzador](../Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction/run_global_a1_mpi.sh)
añade checkpoint_filename en una configuración operativa separada; omite fases
con exit_code=0 registrado tras completar el controlador. Runtime congelado:
`/home/dasan/exofarm-lpjml-runtime/workflow_checkpoints_20260909`.
Cada segmento tiene logs propios; el controlador escribe controller.log y
controller.stderr.log. Los checkpoints se archivan en checkpoints/ con SHA256.
El intervalo es 3600 segundos por segmento y espera al final del año activo.
El primer checkpoint global todavía no existía al verificar la inicialización.

campaign_manifest.json fija hashes y remite a reference_campaign_manifest.json
para los valores científicos y BC originales. La comparación global sigue pendiente.

## Límites de recuperación

### Control 2026-09-09 08:51 America/Bogota

Primer checkpoint global escrito al terminar −2026 (08:49), archivado como
`1788958151853696013.lpj`, 737 MiB. SHA256 recalculado y coincidente:
`e1efdc67e76cfb9bc5227e5b745c715de6bdb490b838477c2ef4988d718b9dfb`.
Segundo segmento `1788961802991377033` confirma lectura del checkpoint;
ocho ranks activos durante la recarga/inicialización. Estado spinup_RUNNING,
controller.stderr.log vacío; advertencias temporales conocidas en los segmentos.
RAM disponible 2.9 GiB, swap 4.3/8 GiB, disco libre 788 GiB. Dos intervalos
actuales de vmstat con si=so=0. Guardado y reanudación normales, sin cambio
de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-09 10:51 America/Bogota

spinup_RUNNING hasta −1885; 69 años más que la consulta de las 09:50 (−1954).
Dos checkpoints archivados: el segundo terminó −1953 a las 09:51, 734 MiB,
con SHA256 registrado por el controlador
`d407292b6bbe4e8c459bfa25e0a6c0755b5d08abcca6ea78a391443b48cb20ad`.
Tercer segmento activo, ocho ranks cerca del 100 % CPU; controller.stderr.log
vacío y advertencias temporales conocidas. RAM disponible 1.6 GiB, swap
3.5/8 GiB, disco libre 787 GiB. vmstat actual: si=8 y luego 0, so=0 en ambos
intervalos; sin intercambio sostenido. Guardados y avance normales, sin cambio
de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-09 11:51 America/Bogota

spinup_RUNNING hasta −1810, 75 años más desde el control anterior. Tres
checkpoints archivados; el tercero terminó −1883 a las 10:53, 735 MiB,
SHA256 registrado por el controlador:
`4b22a3ebd9ba22d468e6550388ca971ad39f097ad3051a78d99a1ec4d76217f2`.
Cuarto segmento activo, ocho ranks cerca del 100 % CPU. controller.stderr.log
vacío; advertencias temporales conocidas. RAM disponible 1.4 GiB, swap
4.0/8 GiB, disco libre 786 GiB; ambos intervalos de vmstat con si=so=0.
Avance y checkpoints normales, sin cambio de fase ni intervención. A1 y
comparación pendientes.

### Control 2026-09-09 12:51 America/Bogota

spinup_RUNNING hasta −1734, 76 años más desde el control anterior. Cuatro
checkpoints archivados; el cuarto terminó −1806 a las 11:54, 738 MiB,
SHA256 registrado por el controlador:
`c67c6249c7168b1d8d32ef005ee205dfd1cdf0f1f86a761f64b2ff08b078db42`.
Quinto segmento activo, ocho ranks cerca del 100 % CPU. controller.stderr.log
vacío; advertencias temporales conocidas. RAM disponible 1.4 GiB, swap
3.4/8 GiB, disco libre 786 GiB; ambos intervalos de vmstat con si=so=0.
Avance y checkpoints normales, sin cambio de fase ni intervención. A1 y
comparación pendientes.

### Control 2026-09-09 13:52 America/Bogota

spinup_RUNNING hasta −1658, 76 años más desde el control anterior. Cinco
checkpoints archivados; el quinto terminó −1728 a las 12:56, 738 MiB,
SHA256 registrado por el controlador:
`cd46732c7a6a7a9101788081e96ffabea78e40ab0549d2a7a22190f56f7bb948`.
Sexto segmento activo, ocho ranks cerca del 100 % CPU. controller.stderr.log
vacío; advertencias temporales conocidas. RAM disponible 1.4 GiB, swap
4.0/8 GiB, disco libre 785 GiB; ambos intervalos de vmstat con si=so=0.
Avance y checkpoints normales, sin cambio de fase ni intervención. A1 y
comparación pendientes.

### Control 2026-09-09 14:55 America/Bogota

spinup_RUNNING hasta −1583, 75 años más desde el control anterior. Seis
checkpoints archivados; el sexto terminó −1651 a las 13:58, 737 MiB,
SHA256 registrado por el controlador:
`1cc9589f44507fed1e00f3edf35e014a52de045cfd9759d6d973579b278a35df`.
Séptimo segmento activo, ocho ranks cerca del 100 % CPU. controller.stderr.log
vacío; advertencias temporales conocidas. RAM disponible 1.4 GiB, swap
2.7/8 GiB, disco libre 784 GiB; muestreo actual sin intercambio activo de swap.
Avance y checkpoints normales, sin cambio de fase ni intervención. A1 y
comparación pendientes.

### Control 2026-09-09 21:44 America/Bogota

spinup_RUNNING hasta −1502, 76 años después del checkpoint recuperado −1578.
Ocho ranks cerca del 100 % CPU; segmento reanudado con unos 60 minutos de
ejecución. Se conservan siete checkpoints archivados; el siguiente guardado
todavía no figura en controller.log. controller.stderr.log vacío y advertencias
temporales conocidas. RAM disponible 732 MiB, swap 52 MiB/8 GiB y disco libre
783 GiB; ambos intervalos actuales de vmstat con si=so=0. Avance normal,
sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-09 22:44 America/Bogota

spinup_RUNNING hasta −1429, 73 años más desde el control anterior. Ocho
checkpoints archivados; el último terminó −1500 a las 21:45, 738 MiB,
SHA256 registrado por el controlador:
`d8ebdc4d2df4ecc8b022ef27bec77ada2b69f92e421208cb2bf63b92649d678f`.
Segmento 1789008348506444170 activo, ocho ranks cerca del 100 % CPU.
controller.stderr.log vacío; advertencias temporales conocidas. RAM disponible
1.0 GiB, swap 3.7/8 GiB, disco libre 783 GiB; ambos intervalos actuales de
vmstat con si=so=0. Avance y guardados normales, sin cambio de fase ni
intervención. A1 y comparación pendientes.

### Control 2026-09-09 23:43 America/Bogota

spinup_RUNNING hasta −1355, 74 años más desde el control anterior. Nueve
checkpoints archivados; el último terminó −1425 a las 22:47, 737 MiB,
SHA256 registrado por el controlador:
`46ab52a5f99c89c97b08fe101082398a3b24050c5017b328ae57009022d9e1bf`.
Segmento 1789012059461631423 activo, ocho ranks cerca del 100 % CPU.
controller.stderr.log vacío; advertencias temporales conocidas. RAM disponible
1.2 GiB, swap 4.1/8 GiB, disco libre 782 GiB; ambos intervalos actuales de
vmstat con si=so=0. Avance y guardados normales, sin cambio de fase ni
intervención. A1 y comparación pendientes.

### Control 2026-09-10 00:43 America/Bogota

spinup_RUNNING hasta −1280, 75 años más desde el control anterior. Diez
checkpoints archivados; el último terminó −1347 a las 23:50, 737 MiB,
SHA256 registrado por el controlador:
`a2eaff3740d05faa11a1a1281a561d0bb17f4557ad12e9e277cb2719ca836043`.
Segmento 1789015812974416368 activo, ocho ranks cerca del 100 % CPU.
controller.stderr.log vacío; advertencias temporales conocidas. RAM disponible
1.3 GiB, swap 3.7/8 GiB, disco libre 781 GiB; ambos intervalos actuales de
vmstat con si=so=0. Avance y guardados normales, sin cambio de fase ni
intervención. A1 y comparación pendientes.

### Control 2026-09-10 01:44 America/Bogota

spinup_RUNNING hasta −1204, 76 años más desde el control anterior. Once
checkpoints archivados; el último terminó −1268 a las 00:53, 737 MiB,
SHA256 registrado por el controlador:
`7080f69f24fc1323deca189b13c22681ae63e933bc1e46641856ad4bfc055fa8`.
Segmento 1789019595099281103 activo, ocho ranks cerca del 100 % CPU.
controller.stderr.log vacío; advertencias temporales conocidas. RAM disponible
1.3 GiB, swap 4.0/8 GiB y disco libre 781 GiB. vmstat registra salida puntual
de swap (so=5120, luego 0; si=0, luego 2), sin pérdida de avance observada.
Guardados normales, sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-10 02:47 America/Bogota

spinup_RUNNING hasta −1124, 80 años más desde el control anterior. Doce
checkpoints archivados; el último terminó −1190 a las 01:54, 731 MiB,
SHA256 registrado por el controlador:
`89bb70c8f5dec8fb4e78bcf1617ff7c72e9d29b1130249d9b1f44182551b2eb6`.
Segmento 1789023291971215694 activo, ocho ranks cerca del 100 % CPU.
controller.stderr.log vacío; advertencias temporales conocidas. RAM disponible
1.3 GiB, swap 2.7/8 GiB, disco libre 780 GiB; ambos intervalos actuales de
vmstat con si=so=0. Avance y guardados normales, sin cambio de fase ni
intervención. A1 y comparación pendientes.

### Control 2026-09-10 03:49 America/Bogota

spinup_RUNNING hasta −1066, 58 años más desde el control anterior. Trece
checkpoints archivados; el último terminó −1113 a las 02:56, 730 MiB,
SHA256 registrado por el controlador:
`4e457223fefa5a390449982602815e08729228d2548f88e32b975c60d655c4cd`.
Segmento 1789026984813321966 activo, ocho ranks cerca del 100 % CPU.
controller.stderr.log vacío; advertencias temporales conocidas. RAM disponible
1.4 GiB, swap 4.1/8 GiB, disco libre 779 GiB; ambos intervalos actuales de
vmstat con si=so=0. El avance es menor que en el intervalo anterior, pero
continúa sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-10 04:51 America/Bogota

spinup_RUNNING hasta −1014, 52 años más desde el control anterior. Catorce
checkpoints archivados; el último terminó −1058 a las 03:58, 934 MiB,
SHA256 registrado por el controlador:
`a28e09f2f69efd67632331802bd8212f04ca5209c9f8ebd37d147807c6700ed0`.
Segmento 1789030691348158152 activo, ocho ranks cerca del 100 % CPU.
controller.stderr.log vacío; advertencias temporales conocidas. RAM disponible
2.0 GiB, swap 4.1/8 GiB, disco libre 778 GiB. vmstat registra salida puntual
de swap (so=7760, luego 0; si=0 en ambos intervalos). El checkpoint aumentó
de tamaño y fue cargado por el segmento siguiente, que continúa avanzando.
Sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-10 05:51 America/Bogota

spinup_RUNNING hasta −962, 52 años más desde el control anterior. Quince
checkpoints archivados; el último terminó −1005 a las 05:01, 935 MiB,
SHA256 registrado por el controlador:
`f8d5494f86646eedcca80843cb3e9882977c7250e233a8ff26df4713eb1d2c98`.
Segmento 1789034468809329954 activo, ocho ranks cerca del 100 % CPU.
controller.stderr.log vacío; advertencias temporales conocidas. RAM disponible
1.3 GiB, swap 4.1/8 GiB, disco libre 777 GiB; ambos intervalos actuales de
vmstat con si=so=0. Avance y guardados normales, sin cambio de fase ni
intervención. A1 y comparación pendientes.

### Control 2026-09-10 06:52 America/Bogota

spinup_RUNNING hasta −912, 50 años más desde el control anterior. Dieciséis
checkpoints archivados; el último terminó −953 a las 06:02, 938 MiB,
SHA256 registrado por el controlador:
`ae01199ab68dce97040224461960b78e668faaac2cb295be9e3e50507e9438c3`.
Segmento 1789038167684121309 activo, ocho ranks cerca del 99 % CPU.
controller.stderr.log vacío; advertencias temporales conocidas. RAM disponible
2.0 GiB, swap 4.2/8 GiB, disco libre 776 GiB; ambos intervalos actuales de
vmstat con si=so=0. Avance y guardados normales, sin cambio de fase ni
intervención. A1 y comparación pendientes.

### Control 2026-09-10 07:52 America/Bogota

spinup_RUNNING hasta −861, 51 años más desde el control anterior. Diecisiete
checkpoints archivados; el último terminó −902 a las 07:03, 939 MiB,
SHA256 registrado por el controlador:
`a93f74bc3824297be21ac8036a78606f862a9fdc9f9de14dccb76a7afaaf354c`.
Segmento 1789041806902484459 activo, ocho ranks cerca del 98–99 % CPU.
controller.stderr.log vacío; advertencias temporales conocidas. RAM disponible
2.0 GiB, swap 2.8/8 GiB, disco libre 775 GiB; ambos intervalos actuales de
vmstat con si=so=0. Avance y guardados normales, sin cambio de fase ni
intervención. A1 y comparación pendientes.

### Control 2026-09-10 08:53 America/Bogota

spinup_RUNNING hasta −811, 50 años más desde el control anterior. Dieciocho
checkpoints archivados; el último terminó −851 a las 08:04, 940 MiB,
SHA256 registrado por el controlador:
`0ac7a6a9e8da957ddf85d788a039230fc1c1f7e01b19187dd265bbf17f6e804e`.
Segmento 1789045485395964486 activo, ocho ranks cerca del 98–99 % CPU.
controller.stderr.log vacío; advertencias temporales conocidas. RAM disponible
1.7 GiB, swap 4.0/8 GiB, disco libre 774 GiB; ambos intervalos actuales de
vmstat con si=so=0. Avance y guardados normales, sin cambio de fase ni
intervención. A1 y comparación pendientes.

### Control 2026-09-10 09:54 America/Bogota

spinup_RUNNING hasta −762, 49 años más desde el control anterior. Diecinueve
checkpoints archivados; el último terminó −800 a las 09:06, 941 MiB,
SHA256 registrado por el controlador:
`1832513242db07624759b20e229df8c3d26a321f6938ad2e20d84e2ca559c4e9`.
Segmento 1789049191671368751 activo, ocho ranks cerca del 100 % CPU.
controller.stderr.log vacío; advertencias temporales conocidas. RAM disponible
1.9 GiB, swap 3.8/8 GiB, disco libre 773 GiB. vmstat registra salida puntual
de swap (so=25600, luego 0; si=0 en ambos intervalos). Avance y guardados
normales, sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-10 10:55 America/Bogota

spinup_RUNNING hasta −713, 49 años más desde el control anterior. Veinte
checkpoints archivados; el último terminó −750 a las 10:07, 942 MiB,
SHA256 registrado por el controlador:
`019a613fc794cc356f6a652f4820ecb915a375ba87c57388b05283cfd0a73ac0`.
Segmento 1789052877780601193 activo, ocho ranks cerca del 98 % CPU.
controller.stderr.log vacío; advertencias temporales conocidas. RAM disponible
1.6 GiB, swap 4.0/8 GiB, disco libre 773 GiB; ambos intervalos actuales de
vmstat con si=so=0. Avance y guardados normales, sin cambio de fase ni
intervención. A1 y comparación pendientes.

### Control 2026-09-10 11:55 America/Bogota

spinup_RUNNING hasta −664, 49 años más desde el control anterior. Veintiún
checkpoints archivados; el último terminó −701 a las 11:09, 942 MiB,
SHA256 registrado por el controlador:
`c8c3dc410e84cf7d61881467cc48e81c000a3cad46c84cad3422088d43be6c63`.
Segmento 1789056566394049511 activo, ocho ranks cerca del 98 % CPU.
controller.stderr.log vacío; advertencias temporales conocidas. RAM disponible
1.7 GiB, swap 2.6/8 GiB, disco libre 772 GiB. vmstat registra salida puntual
de swap (so=3072, luego 0; si=0 en ambos intervalos). Avance y guardados
normales, sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-10 12:56 America/Bogota

spinup_RUNNING hasta −613, 51 años más desde el control anterior. Veintidós
checkpoints archivados; el último terminó −650 a las 12:10, 944 MiB,
SHA256 registrado por el controlador:
`8ee3de5bb735b22c7a980a5e9b8bba58e5195191658ff451fa06a1be6fb35813`.
Segmento 1789060257539997338 activo, ocho ranks cerca del 98 % CPU.
controller.stderr.log vacío; advertencias temporales conocidas. RAM disponible
2.0 GiB, swap 4.2/8 GiB, disco libre 771 GiB; ambos intervalos actuales de
vmstat con si=so=0. Avance y guardados normales, sin cambio de fase ni
intervención. A1 y comparación pendientes.

### Control 2026-09-10 13:57 America/Bogota

spinup_RUNNING hasta −563, 50 años más desde el control anterior. Veintitrés
checkpoints archivados; el último terminó −600 a las 13:11, 944 MiB,
SHA256 registrado por el controlador:
`14730361efe03c36f1d64788f1cba086ea65a8db96995c89aafe299b1da430bb`.
Segmento 1789063917676380598 activo, ocho ranks cerca del 98 % CPU.
controller.stderr.log vacío; advertencias temporales conocidas. RAM disponible
1.7 GiB, swap 4.1/8 GiB, disco libre 770 GiB; ambos intervalos actuales de
vmstat con si=so=0. Avance y guardados normales, sin cambio de fase ni
intervención. A1 y comparación pendientes.

### Control 2026-09-10 14:57 America/Bogota

spinup_RUNNING hasta −513, 50 años más desde el control anterior. Veinticuatro
checkpoints archivados; el último terminó −549 a las 14:13, 942 MiB,
SHA256 registrado por el controlador:
`9d095da57249ad190f4cac04673b87602de5289cc5d408de6107516438d1a4c4`.
Segmento 1789067598875464295 activo, ocho ranks cerca del 98 % CPU.
controller.stderr.log vacío; advertencias temporales conocidas. RAM disponible
2.1 GiB, swap 3.7/8 GiB, disco libre 769 GiB; ambos intervalos actuales de
vmstat con si=so=0. Avance y guardados normales, sin cambio de fase ni
intervención. A1 y comparación pendientes.

### Control 2026-09-10 15:58 America/Bogota

spinup_RUNNING hasta −462, 51 años más desde el control anterior. Veinticinco
checkpoints archivados; el último terminó −498 a las 15:14, 943 MiB,
SHA256 registrado por el controlador:
`326c6a82cd93c58666597d4b72b54f2b7ff4e83f20b077111c1dda8b10472565`.
Segmento 1789071273074067387 activo, ocho ranks cerca del 98 % CPU.
controller.stderr.log vacío; advertencias temporales conocidas. RAM disponible
1.4 GiB, swap 1.4/8 GiB, disco libre 768 GiB; ambos intervalos actuales de
vmstat con si=so=0. Avance y guardados normales, sin cambio de fase ni
intervención. A1 y comparación pendientes.

### Control 2026-09-10 16:59 America/Bogota

spinup_RUNNING hasta −411, 51 años más desde el control anterior. Veintiséis
checkpoints archivados; el último terminó −447 a las 16:15, 944 MiB,
SHA256 registrado por el controlador:
`dd739a41a65de6fd9da06b30e9adcd8b96e18d1cec629bad19a754c0523c419e`.
Segmento 1789074932862231533 activo, ocho ranks cerca del 98 % CPU.
controller.stderr.log vacío; advertencias temporales conocidas. RAM disponible
2.4 GiB, swap 3.9/8 GiB, disco libre 767 GiB; ambos intervalos actuales de
vmstat con si=so=0. Avance y guardados normales, sin cambio de fase ni
intervención. A1 y comparación pendientes.

### Control 2026-09-10 17:59 America/Bogota

spinup_RUNNING hasta −362, 49 años más desde el control anterior. Veintisiete
checkpoints archivados; el último terminó −397 a las 17:16, 944 MiB,
SHA256 registrado por el controlador:
`d7e77772fee57df15c03fc3f0bbfc15811e8811759972fa0096de7cd36db361e`.
Segmento 1789078584493855951 activo, ocho ranks cerca del 98 % CPU.
controller.stderr.log vacío; advertencias temporales conocidas. RAM disponible
3.0 GiB, swap 4.1/8 GiB, disco libre 766 GiB; ambos intervalos actuales de
vmstat con si=so=0. Avance y guardados normales, sin cambio de fase ni
intervención. A1 y comparación pendientes.

### Control 2026-09-10 19:00 America/Bogota

spinup_RUNNING hasta −312, 50 años más desde el control anterior. Veintiocho
checkpoints archivados; el último terminó −347 a las 18:16, 943 MiB,
SHA256 registrado por el controlador:
`043c82cbce89e7ed3d9366ab57e7bcb96331296cc048bfa975c94e526197c6dd`.
Segmento 1789082220282758310 activo, ocho ranks cerca del 98 % CPU.
controller.stderr.log vacío; advertencias temporales conocidas. RAM disponible
2.9 GiB, swap 3.6/8 GiB, disco libre 765 GiB; ambos intervalos actuales de
vmstat con si=so=0. Avance y guardados normales, sin cambio de fase ni
intervención. A1 y comparación pendientes.

### Control 2026-09-10 19:59 America/Bogota

spinup_RUNNING hasta −262, 50 años más desde el control anterior. Veintinueve
checkpoints archivados; el último terminó −297 a las 19:17, 944 MiB,
SHA256 registrado por el controlador:
`008d9e72eca5c69ada9db8d4c1f79d4f371bde48e3ce158e2947bdd12f94a0c0`.
Segmento 1789085852487441242 activo, ocho ranks cerca del 98 % CPU.
controller.stderr.log vacío; advertencias temporales conocidas. RAM disponible
2.7 GiB, swap 4.1/8 GiB, disco libre 764 GiB; ambos intervalos actuales de
vmstat con si=so=0. Avance y guardados normales, sin cambio de fase ni
intervención. A1 y comparación pendientes.

### Control 2026-09-10 21:01 America/Bogota

spinup_RUNNING hasta −211, 51 años más desde el control anterior. Treinta
checkpoints archivados; el último terminó −246 a las 20:18, 944 MiB,
SHA256 registrado por el controlador:
`ca8355d171ced6cac310b8a617b87438809276e22baa6eb20f59d7901c709924`.
Segmento 1789089535505194011 activo, ocho ranks cerca del 98 % CPU.
controller.stderr.log vacío; advertencias temporales conocidas. RAM disponible
2.3 GiB, swap 4.1/8 GiB, disco libre 763 GiB; ambos intervalos actuales de
vmstat con si=so=0. Avance y guardados normales, sin cambio de fase ni
intervención. A1 y comparación pendientes.

### Control 2026-09-10 22:02 America/Bogota

spinup_RUNNING hasta −161, 50 años más desde el control anterior. Treinta y un
checkpoints archivados; el último terminó −196 a las 21:19, 945 MiB,
SHA256 registrado por el controlador:
`de912ff801955362f3c610441b3282dfbba8a528b91268f3f11eb0d0b4d3a1a7`.
Segmento 1789093159012821800 activo, ocho ranks cerca del 98 % CPU.
controller.stderr.log vacío; advertencias temporales conocidas. RAM disponible
2.0 GiB, swap 3.8/8 GiB, disco libre 762 GiB; ambos intervalos actuales de
vmstat con si=so=0. Avance y guardados normales, sin cambio de fase ni
intervención. A1 y comparación pendientes.

### Control 2026-09-10 23:02 America/Bogota

spinup_RUNNING hasta −112, 49 años más desde el control anterior. Treinta y dos
checkpoints archivados; el último terminó −145 a las 22:20, 945 MiB,
SHA256 registrado por el controlador:
`ca714ebffa6a7b7dde4e7e6b0ff6526e7c39619c42892373fded500d5798e245`.
Segmento 1789096814665942787 activo, ocho ranks cerca del 98 % CPU.
controller.stderr.log vacío; advertencias temporales conocidas. RAM disponible
1.4 GiB, swap 2.2/8 GiB, disco libre 761 GiB; ambos intervalos actuales de
vmstat con si=so=0. Avance y guardados normales, sin cambio de fase ni
intervención. A1 y comparación pendientes.

### Control 2026-09-11 00:05 America/Bogota

Consulta del usuario sobre continuidad: verificación en vivo confirma spinup_RUNNING
hasta −66, 46 años más desde el control anterior. Ocho ranks activos al 97.7–98.5 %
CPU; no hace falta relanzar. Hay 33 checkpoints archivados; el último archivo
se guardó el 10 de septiembre a las 23:21, 944 MiB, SHA256 registrado:
`18a703e0251fb2bec53866205e62724004b64aa1dc8a255e17652ac03da8d6ed`.
controller.stderr.log vacío; RAM disponible 2.0 GiB, swap 4.4/8 GiB y disco
libre 761 GiB. Continúa el spin-up; A1 y comparación de flujos pendientes.

### Control 2026-09-11 00:30 America/Bogota

spinup_RUNNING hasta −48, 18 años más desde las 00:05. Ocho ranks activos;
34 checkpoints archivados. Último guardado a las 00:23, 945 MiB, SHA256
registrado por el controlador:
`2d4077f1b224244b1b40dd596e96cbf86b4b937d0a67c802d2dd92834bfa5b2f`.
controller.stderr.log vacío. RAM disponible 2.7 GiB, swap 2.4/8 GiB y disco
libre 760 GiB. Continúa el spin-up; A1 y comparación pendientes.

### Control 2026-09-11 01:03 America/Bogota

spinup_RUNNING hasta −20, 28 años más desde las 00:30. Ocho ranks activos
al 97.8–98.5 % CPU; 34 checkpoints archivados. Último guardado a las 00:23,
945 MiB, SHA256 registrado:
`2d4077f1b224244b1b40dd596e96cbf86b4b937d0a67c802d2dd92834bfa5b2f`.
controller.stderr.log vacío y advertencias temporales conocidas en el segmento.
RAM disponible 1.9 GiB, swap 4.0/8 GiB, disco libre 760 GiB; ambos intervalos
actuales de vmstat con si=so=0. Avance normal, sin cambio de fase ni intervención.
A1 y comparación pendientes.

Las pruebas validan spin-up y recuperación de A1 en ocho celdas. Conservar generaciones previas
protege frente a interrupción durante una escritura, pero la selección de una
copia previa debe ser explícita y validar su integridad. Un cierre abrupto de
WSL no puede solicitar el guardado; se recuperará el último checkpoint completo.

### Incidente 2026-09-12 03:49 America/Bogota

> **Incidente verificado 2026-09-12 03:49 America/Bogota:** global_a1_checkpoints_20260909 permanece FAILED, sin procesos MPI y sin crecimiento del log desde 2026-09-11 01:34. Último año completo 2; ERROR004 de balance de carbono en año 3, celdas 50566 y 58993. Checkpoint activo de 01:27 conserva SHA256 d4b276cd3f65732a50e1d818dca0681935d2debf0d3abbce727fcf2d430117d5. Hay 35 generaciones según último inventario. Seguimiento pausado; no se relanzó. Próximo: diagnosticar balance y validar recuperación antes de continuar. A1/comparación pendientes; estimación temporal anterior suspendida.

Evidencia: spinup_natural/segment_1789108033976118071.stdout.stderr.log y .stdout.log, dentro de la campaña Ubuntu documentada. ERROR004: balances -25280.6961378056 y -14527.5804951857. La causa raíz sigue pendiente; no se desactivaron controles de conservación. El diagnóstico anterior quedó incompleto por rechazo de aprobación automática asociado al límite de uso de Codex; la lectura se pudo reanudar en este control.

### Diagnóstico de código 2026-09-12

La ruta SAFE de `Agricultural_Fluxes_LPJmL/software/LPJmL/src/lpj/updateannual_grid.c` llama por primera vez a `check_fluxes` cuando year > -2099 + 900 + 60*20 + 0 + 1, es decir, en año 3. `newgrid.c` inicializa balance.tot a cero. `check_fluxes.c` calcula delta_tot contra ese acumulador antes de actualizarlo. En ejecución continua, su umbral natural startyear=3 omite la aserción ese primer año; en checkpoint usa checkpointyear+1=-2 y activa la aserción en año 3. Esto explica que delta_totc coincida exactamente con tot.carbon en ambos errores observados. Es diagnóstico del código local; pendiente cotejar archivo de runtime y prueba de regresión antes de atribuir recuperación validada.

El log del segmento 1789104220030960846 confirma que el último checkpoint terminó el año -3. Propuesta: conservar el umbral natural de inicialización y combinarlo con el del checkpoint mediante max, manteniendo fail_on_balance=true. Probar ambos modos y transición de equilibrado; después probar continuación desde copia del checkpoint sin tocar la campaña original. Aún no se modificó ni relanzó el ejecutable global.

### Reanudación validada 2026-09-12 14:38

> **Reanudación validada 2026-09-12 14:38 America/Bogota:** campaña global_a1_checkpoints_20260909 activa con ocho ranks y build LPJmL-6.0.6-balance-fix-20260912. Prueba global separada años -2 a 5 PASS: balances activos, trayectoria previa idéntica a precisión del log, checkpoint íntegro. Campaña retoma su checkpoint original año -3; checkpoints y seguimiento horarios activos. A1 sigue automáticamente tras spin-up. Informe: docs/lpjml_balance_checkpoint_fix_2026-09-12.md. Entradas previas son historial.

### Control 2026-09-12 15:40 America/Bogota

spinup_RUNNING. Completó el año 49 y guardó checkpoint a las 15:39 (945 MiB);
36 generaciones archivadas. SHA256 registrado por el controlador:
`30fe15a75a5bb56757dc56efa1b28c72bdb15724e613c80a2d1979b88aa64324`.
Nuevo segmento arrancando con ocho ranks activos después del cierre normal.
El error 4 que permanece en controller.stderr.log corresponde al segmento
1789108033976118071 anterior al parche; el segmento reciente solo muestra
advertencias temporales conocidas. RAM disponible 13 GiB durante carga,
swap 18 MiB/8 GiB, disco libre 756 GiB; si=so=0 en ambos intervalos actuales.
Avance normal tras la corrección, sin cambio de fase ni intervención.
A1 y comparación pendientes.

### Control 2026-09-12 19:43 America/Bogota

spinup_RUNNING. Año 250 completado; 40 checkpoints archivados. Último guardado
19:42, 945 MiB, SHA256 registrado por el controlador:
`40915697a659ce0b0478365f9a03608556a6d5f6323e09b09f195371136af206`.
Nuevo segmento 1789260152504676349 cargando con ocho ranks activos. El error 4
persistente corresponde al segmento histórico 1789108033976118071; el stderr
reciente contiene las advertencias temporales conocidas. RAM disponible 12 GiB
durante carga, swap 129 MiB/8 GiB, disco libre 752 GiB; si=so=0 en los dos
intervalos actuales. Continúa normalmente, sin cambio de fase ni intervención.
El control parcial de 16:41 había observado año 99 y 37 generaciones; los
controles intermedios no se registraron como verificaciones completas.
A1 y comparación pendientes.

### Control 2026-09-12 20:44 America/Bogota

spinup_RUNNING. Año 301 completado, 51 años más desde el control anterior;
41 checkpoints archivados. Último guardado 20:43, 945 MiB, SHA256 registrado:
`31a2d0e79282edd37edbc44d1aad76fedf29e20575e59cf7b3da60698351ea4d`.
Segmento 1789263819965023398 cargando con ocho ranks activos. El error 4
persistente corresponde al segmento histórico 1789108033976118071; stderr
reciente con advertencias temporales conocidas. RAM disponible 18 GiB durante
carga, swap 129 MiB/8 GiB, disco libre 751 GiB; ambos intervalos actuales
si=so=0. Avance y checkpoint normales, sin cambio de fase ni intervención.
A1 y comparación pendientes.

### Control 2026-09-12 21:45 America/Bogota

spinup_RUNNING. Año 353 completado, 52 años más desde el control anterior;
42 checkpoints archivados. Último guardado 21:44, 946 MiB, SHA256 registrado:
`2db183dac35999e170d1b30a4a6d69a9a37a88b6684fa6dac07050611ab8df63`.
Segmento 1789267488857791587 cargando con ocho ranks activos. El error 4
persistente corresponde al segmento histórico 1789108033976118071; stderr
reciente con advertencias temporales conocidas. RAM disponible 9.4 GiB durante
carga, swap 131 MiB/8 GiB, disco libre 750 GiB. Intervalos actuales de vmstat:
si=0, so=44 y 14 KiB/s durante carga; sin indicio de bloqueo. Avance y checkpoint
normales, sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-12 22:45 America/Bogota

spinup_RUNNING hasta año 404, 51 años más desde el control anterior.
42 checkpoints archivados; último guardado 21:44, año 353, 946 MiB, SHA256
registrado `2db183dac35999e170d1b30a4a6d69a9a37a88b6684fa6dac07050611ab8df63`.
Segmento 1789267488857791587 activo con ocho ranks al 98.5–99.0 % CPU, próximo
al cierre horario. Error 4 histórico del segmento 1789108033976118071; stderr
reciente solo con advertencias temporales conocidas. RAM disponible 1.3 GiB,
swap 4.1/8 GiB, disco libre 750 GiB; si=so=0 en ambos intervalos actuales.
Avance normal, sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-12 23:46 America/Bogota

spinup_RUNNING hasta año 457, 53 años más desde el control anterior.
43 checkpoints archivados; último guardado 22:46, año 405, 946 MiB, SHA256
registrado `bcc615d55d42eed8580867f176f28a0d6100cd8e54bd5df0fd3491b7295c2175`.
Segmento 1789271175539295125 activo con ocho ranks al 98.3–98.8 % CPU, próximo
al cierre horario. Error 4 histórico del segmento 1789108033976118071; stderr
reciente solo con advertencias temporales conocidas. RAM disponible 1.6 GiB,
swap 4.1/8 GiB, disco libre 750 GiB; si=so=0 en ambos intervalos actuales.
Avance normal, sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-13 00:47 America/Bogota

spinup_RUNNING hasta año 509, 52 años más desde el control anterior.
44 checkpoints archivados; último guardado 12 de septiembre 23:47, año 458,
946 MiB, SHA256 registrado:
`e8f7cd900ac0203b7bbb075178aea6d90bc4e5fab65ff2bbb38c676d458b4df9`.
Segmento 1789274842407135883 activo con ocho ranks al 98.4–98.9 % CPU, próximo
al cierre horario. Error 4 histórico del segmento 1789108033976118071; stderr
reciente solo con advertencias temporales conocidas. RAM disponible 1.4 GiB,
swap 4.0/8 GiB, disco libre 749 GiB; vmstat si=0 en ambos intervalos, so=344
KiB/s y después cero. Avance normal, sin cambio de fase ni intervención.
A1 y comparación pendientes.

### Control 2026-09-13 01:49 America/Bogota

spinup_RUNNING hasta año 562, 53 años más desde el control anterior.
45 checkpoints archivados; último guardado 00:48, año 510, 947 MiB, SHA256
registrado `092d4c9f9f4ecf66691cdbb1f3a1b826aba4f19c1e4a0a7105c30ed5aac68e6c`.
Segmento 1789278532443567732 activo con ocho ranks al 98.5–99.0 % CPU, próximo
al cierre horario. Error 4 histórico del segmento 1789108033976118071; stderr
reciente solo con advertencias temporales conocidas. RAM disponible 1.7 GiB,
swap 3.6/8 GiB, disco libre 748 GiB; si=so=0 en ambos intervalos actuales.
Avance normal, sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-13 02:49 America/Bogota

spinup_RUNNING hasta año 614, 52 años más desde el control anterior.
46 checkpoints archivados; último guardado 01:50, año 563, 945 MiB, SHA256
registrado `2cff653c8592fb7204979c49c77b94aa12b7c117758eb1ad26e24213c0059201`.
Segmento 1789282205277873231 activo con ocho ranks al 98.4–98.9 % CPU, próximo
al cierre horario. Error 4 histórico del segmento 1789108033976118071; stderr
reciente solo con advertencias temporales conocidas. RAM disponible 1.4 GiB,
swap 4.0/8 GiB, disco libre 747 GiB; si=so=0 en ambos intervalos actuales.
Avance normal, sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-13 03:50 America/Bogota

spinup_RUNNING hasta año 665, 51 años más desde el control anterior.
47 checkpoints archivados; último guardado 02:50, año 615, 945 MiB, SHA256
registrado `3817240d825766bf24cdbb83a04064593161ebdefe2f1e19c5dc524f763d65a7`.
Segmento 1789285830161538765 activo con ocho ranks al 98.4–99.0 % CPU, próximo
al cierre horario. Error 4 histórico del segmento 1789108033976118071; stderr
reciente solo con advertencias temporales conocidas. RAM disponible 1.4 GiB,
swap 4.3/8 GiB, disco libre 746 GiB; si=so=0 en ambos intervalos actuales.
Avance normal, sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-13 04:51 America/Bogota

spinup_RUNNING hasta año 717, 52 años más desde el control anterior.
48 checkpoints archivados; último guardado 03:51, año 666, 947 MiB, SHA256
registrado `05db9d870416926f4d45f1795e03b248f9f8ef1324d983a4dad3cb84c3cde6e8`.
Segmento 1789289489205605115 activo con ocho ranks al 98.5–99.1 % CPU, próximo
al cierre horario. Error 4 histórico del segmento 1789108033976118071; stderr
reciente solo con advertencias temporales conocidas. RAM disponible 1.2 GiB,
swap 1.9/8 GiB, disco libre 745 GiB; si=so=0 en ambos intervalos actuales.
Avance normal, sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-13 05:51 America/Bogota

spinup_RUNNING hasta año 769, 52 años más desde el control anterior.
49 checkpoints archivados; último guardado 04:52, año 718, 946 MiB, SHA256
registrado `a38488257f52443d73a194e3036363fd59519fcc7a3f62165800add9ae502201`.
Segmento 1789293129695278497 activo con ocho ranks al 98.5–99.0 % CPU, próximo
al cierre horario. Error 4 histórico del segmento 1789108033976118071; stderr
reciente solo con advertencias temporales conocidas. RAM disponible 1.8 GiB,
swap 3.3/8 GiB, disco libre 744 GiB; si=so=0 en ambos intervalos actuales.
Avance normal, sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-13 06:51 America/Bogota

spinup_RUNNING hasta año 820, 51 años más desde el control anterior.
50 checkpoints archivados; último guardado 05:52, año 770, 945 MiB, SHA256
registrado `88ae8fc85b1f0234964d539ea319c39cdc360b64f4ffb9962460d086bf42f12a`.
Segmento 1789296752072302191 activo con ocho ranks al 98.5–99.0 % CPU, próximo
al cierre horario. Error 4 histórico del segmento 1789108033976118071; stderr
reciente solo con advertencias temporales conocidas. RAM disponible 1.5 GiB,
swap 3.2/8 GiB, disco libre 743 GiB; si=so=0 en ambos intervalos actuales.
Avance normal, sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-13 07:51 America/Bogota

spinup_RUNNING hasta año 872, 52 años más desde el control anterior.
51 checkpoints archivados; último guardado 06:53, año 822, 946 MiB, SHA256
registrado `0c627690e04305a2edd1687c58ce95588ad2d8d7f15f4888b308110390e57525`.
Segmento 1789300426990154548 activo con ocho ranks al 98.4–99.0 % CPU.
Error 4 histórico del segmento 1789108033976118071; stderr reciente solo con
advertencias temporales conocidas. RAM disponible 1.5 GiB, swap 3.2/8 GiB,
disco libre 742 GiB; si=so=0 en ambos intervalos actuales. Avance normal,
sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-13 08:52 America/Bogota

spinup_RUNNING hasta año 924, 52 años más desde el control anterior.
52 checkpoints archivados; último guardado 07:54, año 874, 947 MiB, SHA256
registrado `747ddd6d44e059d9fca03edcc3e52a0d17585d87afd9417d8fee1e47958e13aa`.
Segmento 1789304062257511835 activo con ocho ranks al 98.5–99.0 % CPU.
Error 4 histórico del segmento 1789108033976118071; stderr reciente solo con
advertencias temporales conocidas. RAM disponible 2.0 GiB, swap 3.4/8 GiB,
disco libre 741 GiB; vmstat si=0 en ambos intervalos, so=0 y 2048 KiB/s.
Avance normal, sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-13 09:53 America/Bogota

spinup_RUNNING hasta año 974, 50 años más desde el control anterior.
53 checkpoints archivados; último guardado 08:55, año 926, 947 MiB, SHA256
registrado `d5692c3703eb9a7e8725ffaccca64bc769c0e06c798d0bb2776360c9eb8e2c89`.
Segmento 1789307718119528013 activo con ocho ranks al 98.5–99.1 % CPU.
Error 4 histórico del segmento 1789108033976118071; stderr reciente solo con
advertencias temporales conocidas. RAM disponible 2.0 GiB, swap 3.5/8 GiB,
disco libre 740 GiB; si=so=0 en ambos intervalos actuales. Avance normal,
sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-13 10:54 America/Bogota

spinup_RUNNING hasta año 1026, 52 años más desde el control anterior.
54 checkpoints archivados; último guardado 09:56, año 977, 948 MiB, SHA256
registrado `8c48aea5951a6332c44ff8df823d56d260f3d7639247f42002c0f02929ad3180`.
Segmento 1789311375205545674 activo con ocho ranks al 98.4–98.9 % CPU.
Error 4 histórico del segmento 1789108033976118071; stderr reciente solo con
advertencias temporales conocidas. RAM disponible 1.4 GiB, swap 4.0/8 GiB,
disco libre 739 GiB; si=so=0 en ambos intervalos actuales. Avance normal,
sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-13 11:55 America/Bogota

spinup_RUNNING hasta año 1078, 52 años más desde el control anterior.
55 checkpoints archivados; último guardado 10:57, año 1029, 948 MiB, SHA256
registrado `699ef56998749b86546ef4da55350f29956a2cf8fcce1688bf2a139e90a92043`.
Segmento 1789315053185978266 activo con ocho ranks al 98.3–98.9 % CPU.
Error 4 histórico del segmento 1789108033976118071; stderr reciente solo con
advertencias temporales conocidas. RAM disponible 2.0 GiB, swap 3.5/8 GiB,
disco libre 738 GiB; si=so=0 en ambos intervalos actuales. Avance normal,
sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-13 12:56 America/Bogota

spinup_RUNNING hasta año 1128, 50 años más desde el control anterior.
56 checkpoints archivados; último guardado 11:59, año 1081, 947 MiB, SHA256
registrado `d338927703534e9e9f04e3052e7b9f3dc7a4182fb5ff1194898561b03799a2a2`.
Segmento 1789318746900279235 activo con ocho ranks al 98.3–98.8 % CPU.
Error 4 histórico del segmento 1789108033976118071; stderr reciente solo con
advertencias temporales conocidas. RAM disponible 1.7 GiB, swap 4.1/8 GiB,
disco libre 737 GiB; si=so=0 en ambos intervalos actuales. Avance normal,
sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-13 13:57 America/Bogota

spinup_RUNNING hasta año 1179, 51 años más desde el control anterior.
57 checkpoints archivados; último guardado 12:59, año 1131, 947 MiB, SHA256
registrado `db18cb7e3998122984394ebf300014796d72d796c13f0cddd8e2190912b74e26`.
Segmento 1789322392436925398 activo con ocho ranks al 98.2–98.7 % CPU.
Error 4 histórico del segmento 1789108033976118071; stderr reciente solo con
advertencias temporales conocidas. RAM disponible 1.8 GiB, swap 4.0/8 GiB,
disco libre 737 GiB; vmstat si=0 en ambos intervalos, so=10240 KiB/s y luego
cero. Avance normal, sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-13 14:57 America/Bogota

spinup_RUNNING hasta año 1229, 50 años más desde el control anterior.
58 checkpoints archivados; último guardado 14:00, año 1182, 947 MiB, SHA256
registrado `901766c495b361b48d88b30c1a7d370ffa3719622689b634ba6e56f9dc23b879`.
Segmento 1789326044030122330 activo con ocho ranks al 98.1–98.7 % CPU.
Error 4 histórico del segmento 1789108033976118071; stderr reciente solo con
advertencias temporales conocidas. RAM disponible 1.7 GiB, swap 4.1/8 GiB,
disco libre 736 GiB; si=so=0 en ambos intervalos actuales. Avance normal,
sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-13 15:58 America/Bogota

spinup_RUNNING hasta año 1279, 50 años más desde el control anterior.
59 checkpoints archivados; último guardado 15:02, año 1233, 947 MiB, SHA256
registrado `f0ada541b669ac96ebe237b45114345f14f2a70c3009102cb6d8cef6d60b8d51`.
Segmento 1789329733770478438 activo con ocho ranks al 98.0–98.5 % CPU.
Error 4 histórico del segmento 1789108033976118071; stderr reciente solo con
advertencias temporales conocidas. RAM disponible 1.6 GiB, swap 4.1/8 GiB,
disco libre 735 GiB; si=so=0 en ambos intervalos actuales. Avance normal,
sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-13 16:58 America/Bogota

spinup_RUNNING hasta año 1329, 50 años más desde el control anterior.
60 checkpoints archivados; último guardado 16:02, año 1283, 948 MiB, SHA256
registrado `b080812ea7ac179fa48aef13b7806c9325acc31b747a45308156845f2f6fc228`.
Segmento 1789333379131949420 activo con ocho ranks al 98.3–98.9 % CPU.
Error 4 histórico del segmento 1789108033976118071; stderr reciente solo con
advertencias temporales conocidas. RAM disponible 2.3 GiB, swap 3.7/8 GiB,
disco libre 734 GiB; si=so=0 en ambos intervalos actuales. Avance normal,
sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-13 17:59 America/Bogota

spinup_RUNNING hasta año 1379, 50 años más desde el control anterior.
61 checkpoints archivados; último guardado 17:03, año 1333, 947 MiB, SHA256
registrado `f80d41a64403ea4768611ae84e2c84d26b9871fde2ac4d5f4abc56b037643d10`.
Segmento 1789337009678995722 activo con ocho ranks al 98.4–98.9 % CPU.
Error 4 histórico del segmento 1789108033976118071; stderr reciente solo con
advertencias temporales conocidas. RAM disponible 1.2 GiB, swap 3.7/8 GiB,
disco libre 733 GiB; si=so=0 en ambos intervalos actuales. Avance normal,
sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-13 19:00 America/Bogota

spinup_RUNNING hasta año 1429, 50 años más desde el control anterior.
62 checkpoints archivados; último guardado 18:04, año 1383, 948 MiB, SHA256
registrado `70af86991fc64acf6fa1910b5f1a5e8cac385bd2e11055b8adf1dd0440cc6eda`.
Segmento 1789340659356407336 activo con ocho ranks al 98.3–98.9 % CPU.
Error 4 histórico del segmento 1789108033976118071; stderr reciente solo con
advertencias temporales conocidas. RAM disponible 1.0 GiB, swap 3.2/8 GiB,
disco libre 732 GiB; si=so=0 en ambos intervalos actuales. Avance normal,
sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-13 20:00 America/Bogota

spinup_RUNNING hasta año 1479, 50 años más desde el control anterior.
63 checkpoints archivados; último guardado 19:04, año 1433, 948 MiB, SHA256
registrado `0e985b29eff4d4cf2cc158b3bea10c6ae50488ea6af8409912d456b3181f5111`.
Segmento 1789344285884371881 activo con ocho ranks al 98.4–98.9 % CPU.
Error 4 histórico del segmento 1789108033976118071; stderr reciente solo con
advertencias temporales conocidas. RAM disponible 1.9 GiB, swap 3.1/8 GiB,
disco libre 731 GiB; si=so=0 en ambos intervalos actuales. Avance normal,
sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-13 21:01 America/Bogota

spinup_RUNNING hasta año 1531, 52 años más desde el control anterior.
64 checkpoints archivados; último guardado 20:05, año 1484, 947 MiB, SHA256
registrado `be32941df8f965ce0013fbb720b1a01ee9f00a889592b2c75e9b86b5f97e3dbb`.
Segmento 1789347952571646565 activo con ocho ranks al 98.3–98.9 % CPU.
Error 4 histórico del segmento 1789108033976118071; stderr reciente solo con
advertencias temporales conocidas. RAM disponible 1.8 GiB, swap 4.0/8 GiB,
disco libre 730 GiB; si=so=0 en ambos intervalos actuales. Avance normal,
sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-13 22:03 America/Bogota

spinup_RUNNING hasta año 1583, 52 años más desde el control anterior.
65 checkpoints archivados; último guardado 21:07, año 1536, 948 MiB, SHA256
registrado `5c3eae939b36a20c98680090bc7e2fc0f70cada63e73321f0ebac503ea9b0b3f`.
Segmento 1789351638084241585 activo con ocho ranks al 98.2–98.8 % CPU.
Error 4 histórico del segmento 1789108033976118071; stderr reciente solo con
advertencias temporales conocidas. RAM disponible 2.1 GiB, swap 4.0/8 GiB,
disco libre 729 GiB; si=so=0 en ambos intervalos actuales. Avance normal,
sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-13 23:04 America/Bogota

spinup_RUNNING hasta año 1635, 52 años más desde el control anterior.
66 checkpoints archivados; último guardado 22:08, año 1587, 947 MiB, SHA256
registrado `d70b5bc48486a2b37d73af16769ab69a22ae2d09ffd7398df6b0f5f7a96b7c97`.
Segmento 1789355298338731563 activo con ocho ranks al 98.5–99.0 % CPU.
Error 4 histórico del segmento 1789108033976118071; stderr reciente solo con
advertencias temporales conocidas. RAM disponible 2.1 GiB, swap 3.8/8 GiB,
disco libre 728 GiB; si=so=0 en ambos intervalos actuales. Avance normal,
sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control 2026-09-14 00:05 America/Bogota

spinup_RUNNING hasta año 1681, 46 años más desde el control anterior.
67 checkpoints archivados; último guardado 13 de septiembre 23:09, año 1639,
947 MiB, SHA256 registrado:
`b75840ad2a5ea9b72385801ecb2fc65a1d675a6961752e49761132a83ce9c886`.
Segmento 1789358955435543149 activo con ocho ranks al 98.4–98.9 % CPU.
Error 4 histórico del segmento 1789108033976118071; stderr reciente solo con
advertencias temporales conocidas. RAM disponible 2.4 GiB, swap 4.1/8 GiB,
disco libre 727 GiB; si=so=0 en ambos intervalos actuales. Avance normal,
sin cambio de fase ni intervención. A1 y comparación pendientes.

### Cambio de fase 2026-09-14 02:08 America/Bogota

Spin-up terminado 00:33:03, exit_code=0 y PHASE_EXIT_ZERO_PENDING_SCIENTIFIC_VALIDATION.
Reinicio final restart_1700_nv_stdfire.lpj (940 MiB): SHA256 recalculado tanto
para origen como para copia en A1 coincide con spinup_restart.sha256:
`788018ae428edda7d00fa51a2be29db7ea9b40dc46f9a80e17b4c230f5d2ada6`.
A1 empezó automáticamente a las 00:33:07 y completó año 1498 a las 02:08.
Primer checkpoint A1 año 1492 guardado 01:35, 2.4 GiB; SHA256 registrado:
`dbae076811a7ca953b783bcd5c42403cfc47264dcf1b3be20d8b8026077f1b1e`.
Ocho ranks activos al 96.3–97.6 % CPU. controller.stderr.log A1 vacío.
WARNING013 en uso de suelo: por ejemplo celda 25093 año 1499, suma 1.116690
tras escalar por landfrac 0.092433. Evaluar extensión y normalización antes
de aceptación científica. RAM disponible 2.0 GiB, swap 4.9/8 GiB, disco libre
721 GiB. A1 y validación/comparación pendientes. No se relanzó ninguna fase.
El control 01:07 no obtuvo acceso WSL por límite de uso en revisión automática;
esta verificación recuperó el acceso y confirmó el cambio de fase.

### Control 2026-09-14 03:09 America/Bogota

A1_RUNNING hasta año 1510, 12 años más desde el control anterior.
Dos checkpoints A1 archivados; último guardado 02:39, año 1505, 2.6 GiB,
SHA256 registrado `fa9d3cd3abb8df8ae03fbda00f31545f1c46d192068b60801c8e8cb8ef2db819`.
Segmento 1789371575831485725 activo con ocho ranks al 95.9–97.4 % CPU.
controller.stderr.log vacío. Persisten WARNING013 de normalización de uso de
suelo, pendientes de evaluación global antes de aceptar flujos. RAM disponible
2.0 GiB, swap 5.0/8 GiB, disco libre 718 GiB; si=so=0 en ambos intervalos
actuales. Avance y checkpoint normales, sin cambio de fase ni intervención.
Productos 1996–2005 y comparación pendientes.

### Control 2026-09-14 04:09 America/Bogota

A1_RUNNING hasta año 1521, 11 años más desde el control anterior.
Tres checkpoints A1 archivados; último guardado 03:43, año 1517, 2.7 GiB,
SHA256 registrado `62090a4a9f4bce53d99aa0d8db4ea789d370ac5f4e76d1f44a7bdeb4c5b4c9bf`.
Segmento 1789375408686012646 activo con ocho ranks al 95.4–96.8 % CPU.
controller.stderr.log vacío. Persisten WARNING013 de normalización de uso de
suelo, pendientes de evaluación global antes de aceptar flujos. RAM disponible
1.4 GiB, swap 4.8/8 GiB, disco libre 715 GiB; si=so=0 en ambos intervalos
actuales. Avance y checkpoint normales, sin cambio de fase ni intervención.
Productos 1996–2005 y comparación pendientes.

### Interrupción verificada 2026-09-19 04:20 America/Bogota

> **Interrupción verificada 2026-09-19 04:20 America/Bogota:** A1 sin procesos MPI en dos consultas; último año completo 1742, log detenido desde 2026-09-15 01:28. Indicador a1_RUNNING desactualizado. Checkpoint activo año 1738 (2.8 GiB), SHA256 recalculado coincide con el registrado: 08122825cc13ccf1168f652658c6cdd7721f57c16f44ab9b485de315457af3e3. Hay 23 generaciones. Spin-up natural completado conservado. Seguimiento pausado; no se relanzó. Próximo: confirmar causa de interrupción y reanudar A1 desde 1739 con autorización. Flujos y comparación pendientes.

controller.stderr.log vacío. Último segmento 1789452250181613738; WARNING013 de uso de suelo hasta 1743. RAM disponible 30 GiB, swap 0/8 GiB, disco libre 661 GiB. Causa de interrupción no determinada; cuatro años completos posteriores al checkpoint deberán repetirse. No se analizaron productos incompletos.
### Reanudación A1 autorizada 2026-09-19 04:53 America/Bogota

Tras verificar ausencia de procesos y la coincidencia del SHA256 del checkpoint activo y archivado, el usuario autorizó retomar A1. El lanzador operativo omitió el spin-up natural ya completado y arrancó ocho ranks del build `LPJmL-6.0.6-balance-fix-20260912` desde `a1_2005_n/restart/checkpoint.lpj`, año 1738. La ejecución está activa; repetirá los años 1739–1742 que quedaron después del último checkpoint antes de continuar. La campaña conserva `fail_on_balance=true`; los productos 1996–2005, la evaluación de WARNING013 y la comparación N2O/NH3 siguen pendientes.
