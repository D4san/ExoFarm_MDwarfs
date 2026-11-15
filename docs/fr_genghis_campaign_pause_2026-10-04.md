# Pausa de la campaña FR-Genghis crop-only

**Fecha:** 2026-10-04, 16:38 COT  
**Campaña:** `fr_genghis_potential_20260922_chunks_ch4`  
**Estado:** pausada por solicitud expresa del usuario.

## Acción y alcance

La campaña corría en cinco bloques de 8.000 celdas, con un rank MPI por bloque,
salidas CH4, `MAX_PARALLEL=5` y retención completa (`MAX_ARCHIVED_CHECKPOINTS=0`).
Tras la autorización explícita de terminarla inmediatamente, se enviaron señales
`SIGKILL` únicamente al scheduler, sus cinco workers, cinco `checkpoint_runner`,
cinco procesos `mpirun` y cinco procesos LPJmL verificados por ruta y bloque.
La campaña quedó sin procesos activos. Se guardó una copia timestamped del
estado previo y `campaign_status.txt` quedó como `PAUSED_BY_USER` a
2026-10-04T21:38:57Z (16:38:57 COT). Se retiró el directorio de bloqueo vacío
que dejó el scheduler terminado.

La terminación forzada descartó el cálculo no guardado desde el checkpoint de
cada bloque. Las copias archivadas de los últimos checkpoints se conservaron;
en los cinco bloques el hash registrado por el controller, el sidecar SHA-256,
el archivo archivado y `restart/checkpoint.lpj` coincidieron. `lpjcheck
-pedantic` devolvió exit 0 para cada configuración y reportó estos años de
reanudación:

| Bloque | Año del checkpoint | Archivo archivado | SHA-256 | Validación |
| --- | ---: | --- | --- | --- |
| `00000_07999` | 1566 | `1791096968589529619.lpj` | `3558df2823e16b0e75da872c64c07afffa62ae65334e01a5f09bd30045f0934a` | hash/controller/sidecar/restart coinciden; `lpjcheck` 0 |
| `08000_15999` | 1494 | `1791093519616755527.lpj` | `8b3bdde51ef3348ef0309c17bda51de83f7d6a71307261f46670323cd63a8110` | hash/controller/sidecar/restart coinciden; `lpjcheck` 0 |
| `16000_23999` | 1494 | `1791111480441020871.lpj` | `7bb70263206a4ea38a2a69320c8fff68203d0c0d276fc76f1543c172df1dc865` | hash/controller/sidecar/restart coinciden; `lpjcheck` 0 |
| `24000_31999` | 1484 | `1791037519506597047.lpj` | `0e52b9672760d674e24d0211aedaa0b5273f99200f633f559c5d2d7b4b46c3aa` | hash/controller/sidecar/restart coinciden; `lpjcheck` 0 |
| `32000_39999` | 1484 | `1791040623124640840.lpj` | `dc6f24a5fc1adb6fc9c56703f664ca75590d7986c25eb90981b7bb9a4dbf3864` | hash/controller/sidecar/restart coinciden; `lpjcheck` 0 |

No hay códigos finales de bloque ni productos finales aceptados. El código 137
que figura en `controller.stderr.log` de `00000_07999` corresponde al incidente
histórico del 2026-10-01; no es el motivo de esta pausa, que fue una terminación
solicitada por el usuario. La salida de esta campaña tampoco valida el mapa
crop-only ni la corrida final.

## Recursos y límites de interpretación

La última lectura previa a la pausa (16:30 COT) mostró 11 GiB de RAM disponible,
6,5 de 8 GiB de swap ocupados y 497 GiB libres en `/home`. La configuración
mantiene `river_routing=false` y `reservoir=false`; cualquier interpretación
posterior queda limitada al routing local desactivado, sin transporte fluvial ni
reservorios.

No se modificó ni ejecutó VULCAN. No se debe relanzar esta campaña hasta recibir
una nueva instrucción explícita del usuario. Al reanudar, comprobar primero que
no haya procesos ni lock, volver a verificar los checkpoints listados aquí y
registrar la nueva generación y sus códigos de salida.
