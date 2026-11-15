# Recuperación de LPJmL en Ubuntu sobre E:

Fecha: 2026-09-07. Rama inspeccionada: `LIFEAnal`, HEAD `04d0206`.

**Cierre de recuperación:** `INPUTS_VERIFIED 2026-09-07T21:37:00Z`
(16:37 America/Bogota), comprobado en vivo a las 16:49. El worker terminó
la comprobación de tamaño/MD5 y la extracción con sus controles de 76 archivos
y 66,338,995,720 bytes. El archivo tiene exactamente 37,763,601,476 bytes;
no quedan procesos curl/verificación/extracción y Linux conserva 790 GiB libres.
Seguimiento horario pausado al completar. La prueba MPI con entradas reales
quedó aceptada posteriormente en `mpi_smoke_20260907`; véase el
[informe MPI](lpjml_mpi_smoke_validation_2026-09-07.md). La campaña global y los
flujos atmosféricos siguen pendientes.

El usuario autorizó recuperar las entradas e instalación para continuar los
flujos agrícolas, usando el disco de mayor capacidad. La consulta de volúmenes
confirmó E: (`Riqueza`), 8.0 TB totales y 7.7 TB libres. El registro de WSL sitúa
Ubuntu en `E:\Programas\WSL\Ubuntu`; sus archivos Linux consumen ese volumen.
El filesystem virtual reportó 887 GiB libres, suficientes para esta preparación.

## Rutas de este equipo

- Runtime: `/home/dasan/exofarm-lpjml-runtime/LPJmL-6.0.6`.
- Archivo: `/home/dasan/lpjml-data/downloads/lpjml6-0-5_standard_input.tar.gz`.
- Extracción prevista: `/home/dasan/lpjml-data/public_standard`.
- Campañas futuras: `/home/dasan/exofarm-lpjml-runs/`.
- Copia ejecutable del workflow: `/home/dasan/exofarm-lpjml-runtime/workflow_20260907`.

Las rutas históricas `C:/Proyetos/Data/LPJmL/` no existen aquí. El
[manifiesto histórico](../Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction/input_dataset_manifest.json)
conserva la verificación anterior; no demuestra que la descarga actual esté completa.

## Ejecución y verificación

Se instalaron `libopenmpi-dev` 4.1.6 y `python3-scipy` 1.11.4 mediante apt.
Se mantiene Open MPI, ya presente en el equipo, en lugar de añadir MPICH.
El setup fija LPJmL 6.0.6, commit `5af44a1ed023279a23c28d6dfe76945b97aaac57`.
La compilación MPI terminó con código 0, incluidos `make test` y la generación
de `lpjml_mpi_installation.txt` (2026-09-07T15:48:45Z). `lpjml -v` confirmó
el commit y `-DUSE_MPI`. Falta todavía la prueba científica MPI con entradas.
Log: `/home/dasan/exofarm-lpjml-runtime/setup.log`.
Los scripts de este checkout tienen CRLF: se copió el workflow a Linux y se
normalizaron únicamente los finales de línea de los `.sh` de esa copia.

La descarga se inició mediante el servicio transitorio de systemd
`exofarm-lpjml-inputs-20260907.service`, ejecutado como `dasan`. Este servicio
no mantuvo WSL activo tras cerrar sus sesiones: la primera comprobación dio
`active`, pero luego quedó `inactive`, con 190,599,168 bytes preservados.
Se relanzó con `Start-Process -WindowStyle Hidden` como proceso Windows/WSL
independiente (PID inicial 46468), que mantiene Ubuntu activo. El worker volvió
a `DOWNLOADING` a las 15:52:14 UTC; comprobar proceso y bytes, no confiar en el
PID tras reinicios. El log del servicio conserva el primer intento; el estado
del worker es la referencia de la ejecución actual.
El worker `/home/dasan/lpjml-data/recover_inputs_20260907.sh` usa curl reanudable,
un lock exclusivo y luego ejecuta `verify_input_dataset.sh --extract`.
Exige 37,763,601,476 bytes, MD5 `682d8b894d7983301313e9d60a49483b`,
76 archivos extraídos y 66,338,995,720 bytes. No sobrescribe una extracción
preexistente. Fuente: [Zenodo 19064225](https://zenodo.org/records/19064225).

Estado: `/home/dasan/lpjml-data/recovery_status.txt`.
Log: `/home/dasan/lpjml-data/recovery.log`.
La descarga inicial rondó 0.5–0.6 MB/s; el tiempo restante es variable.

```bash
systemctl status exofarm-lpjml-inputs-20260907.service --no-pager
cat /home/dasan/lpjml-data/recovery_status.txt
tail /home/dasan/lpjml-data/recovery.log
stat -c %s /home/dasan/lpjml-data/downloads/lpjml6-0-5_standard_input.tar.gz
```

El servicio puede figurar `inactive` mientras el proceso Windows mantiene la
descarga actual. Desde PowerShell, `Get-Process -Id 46468` comprueba ese proceso;
dentro de Ubuntu, inspeccionar el proceso curl y el crecimiento del archivo.

Si Ubuntu o el equipo se apagan, el servicio transitorio no garantiza reanudación
automática. Reejecutar el worker después de revisar estado y destino; curl
conserva el archivo parcial. Si hay extracción parcial, inspeccionarla primero.

## Siguiente puerta

### Seguimiento solicitado

Comprobación del 2026-09-07 a las 13:00 America/Bogota: archivo de
14,220,967,936 bytes sobre 37,763,601,476 (37.7 %), estado `DOWNLOADING`,
curl activo durante 2 h 08 min y 873 GiB libres en Linux. Desde la reanudación
se observa una media aproximada de 1.83 MB/s; restarían unas 3.6 h si se mantiene,
más verificación/extracción. Esta estimación sustituye la tasa inicial más lenta.
Se activó el seguimiento horario de esta tarea en Codex,
`seguimiento-de-descarga-lpjml`: avisar al completar, fallar o requerir atención;
permanecer en silencio durante el avance normal y pausar tras `INPUTS_VERIFIED`.

Control horario 2026-09-07 14:02 America/Bogota: 20,903,997,440 bytes
(55.4 %), `DOWNLOADING`, curl activo y 867 GiB libres. Creció
6,683,029,504 bytes desde el control anterior; avance normal, sin incidencia.
Checksum y extracción todavía pendientes; seguimiento horario conservado.

Control horario 2026-09-07 15:02 America/Bogota: 28,348,366,848 bytes
(75.1 %), `DOWNLOADING`, curl activo y 860 GiB libres. Creció
7,444,369,408 bytes desde el control anterior; avance normal, sin incidencia.
Checksum y extracción siguen pendientes; se mantiene el seguimiento horario.

Control horario 2026-09-07 16:03 America/Bogota: 35,950,985,216 bytes
(95.2 %), `DOWNLOADING`, curl activo y 853 GiB libres. Creció
7,602,618,368 bytes desde el control anterior; avance normal, sin incidencia.
La integridad y extracción aún no están verificadas; seguimiento conservado.

Tras `INPUTS_VERIFIED` y compilación aceptada, ejecutar `check_other_pc.sh` y
`run_mpi_smoke.sh` con ocho celdas y dos ranks siguiendo el
[runbook](lpjml_global_a1_mpi_other_pc_runbook.md), usando las rutas anteriores.
No se lanzó la campaña global ni se generaron nuevos flujos atmosféricos.

La inspección directa de conda `POSEIDON` confirmó POSEIDON 1.4.0/Python 3.10.13;
`lifesim`, `lifesimmc` y `phringe` no importan en este equipo. Su instalación no
forma parte de esta recuperación agrícola. Los registros LIFE previos describen
otro estado de entorno y deben contrastarse antes de reanudar espectroscopía.
