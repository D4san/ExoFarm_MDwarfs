> **Incidente 2026-09-09 02:00 America/Bogota:** campaña `global_a1_20260907` interrumpida. Dos comprobaciones confirman ausencia de procesos LPJmL/mpirun; WSL indica menos de un minuto de actividad. Última salida: año -231, modificada a las 01:29:08. `campaign_status.txt` conserva SPINUP_RUNNING obsoleto y run_status solo el inicio; carpeta spinup_natural/restart vacía. Causa del cierre sin determinar. No se relanzó. A1, validación y comparación pendientes; seguimiento pausado hasta decidir recuperación.

# Campaña global A1: flujos agrícolas de N2O y NH3

Fecha: 2026-09-07. Campaña: `global_a1_20260907`.
**Estado de lanzamiento: SPINUP_RUNNING**, iniciado a las 22:37:44 UTC
(17:37:44 America/Bogota). Se observaron ocho procesos LPJmL y 67,420 celdas
en la configuración global. No hay aún flujos globales aceptados.

## Pregunta científica

El usuario autorizó ejecutar la campaña global después de la
[prueba MPI aceptada](lpjml_mpi_smoke_validation_2026-09-07.md), para evaluar
si las emisiones agrícolas calculadas por LPJmL son comparables con el aporte
agrícola impuesto en la matriz fotoquímica ExoFarm.

La comparación se hará entre medias de 1996–2005, primero en `TgN/yr` y después
en moléculas `cm^-2 s^-1` promediadas sobre toda la esfera terrestre. Se fijó
la referencia a partir de los archivos reales
[A0](../Photochemical_Modeling/Config/Boundary_Conditions/bc_earth_preagri_full.txt)
y [A1](../Photochemical_Modeling/Config/Boundary_Conditions/bc_earth_current_full.txt):

| Especie | F(A0) | F(A1) | Incremento A1−A0 | Equivalente TgN/yr |
| --- | ---: | ---: | ---: | ---: |
| N2O | 1.58e9 | 2.30e9 | 7.20e8 | 5.39109 |
| NH3 | 2.94e9 | 1.30e10 | 1.006e10 | 37.6627 |

Las tres columnas F están en moléculas `cm^-2 s^-1`. Los equivalentes de masa
son un cálculo del proyecto usando `R_earth=6.371e6 m`, 365.25 días por año,
`M_N=14.0067 g/mol` y `N_A=6.02214076e23 mol^-1`.

```text
M_i [TgN/yr] = F_i * 10^4 * 4*pi*R_earth^2 * segundos/año * M_N*n_N / N_A / 10^12
n_N(N2O)=2; n_N(NH3)=1
F_LPJ(N2O) <- integral(n2o_nit_agr + n2o_denit_agr) sobre land_area
F_LPJ(NH3) <- integral(nh3_agr) sobre land_area
razón diagnóstica_i = F_LPJ(i) / [F_i(A1)-F_i(A0)]
```

**Límite de interpretación:** LPJmL entrega emisiones de los terrenos agrícolas,
mientras A1−A0 representa el incremento prescrito del proyecto. La razón evalúa
magnitud y consistencia bajo esos alcances; aislar el efecto causal neto de la
agricultura exige una simulación sin agricultura con clima y demás condiciones
comparables. El reinicio natural de 1700 no constituye por sí solo ese control
1996–2005. No se reescalará LPJmL para forzar acuerdo ni se cambiarán los BC.

## Configuración y procedencia

- LPJmL 6.0.6, commit `5af44a1ed023279a23c28d6dfe76945b97aaac57`.
- Open MPI 4.1.6; ocho ranks, un rank por núcleo físico del Ryzen 7 5700X3D.
- Host: 16 CPUs lógicas, 31.3 GiB RAM WSL, 790 GiB libres en ext4 al preparar.
- Runtime `/home/dasan/exofarm-lpjml-runtime/LPJmL-6.0.6`.
- Dataset `/home/dasan/lpjml-data/public_standard`, previamente verificado:
  archivo oficial MD5 `682d8b894d7983301313e9d60a49483b`;
  [recuperación](lpjml_wsl_storage_recovery_2026-09-07.md).
- Resultados `/home/dasan/exofarm-lpjml-runs/global_a1_20260907`, almacenados
  físicamente en E: mediante `E:\Programas\WSL\Ubuntu`.
- Workflow congelado `/home/dasan/exofarm-lpjml-runtime/workflow_20260907`;
  fuente versionada [run_global_a1_mpi.sh](../Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction/run_global_a1_mpi.sh).

El dry run verificó los requisitos del runner y generó las configuraciones;
se comprobaron `startgrid=endgrid=all`, N limitado y ríos/irrigación activados
en A1. `lpjcheck` pasó al iniciar la fase natural. El lanzador ejecuta:

1. Spin-up natural: 3799 años de equilibrio, año final 1700 y reinicio propio.
2. A1 gestionado: reutiliza ese reinicio, 420 años de spin-up gestionado,
   simulación histórica 1901–2005 y salida 1996–2005. Uso de suelo y fertilizante
   prescritos, manure, ciclo de N limitado, ríos, embalses, uso de agua e
   irrigación limitada. No usa la configuración hidrológica reducida del piloto.

Cada fase conserva stdout, stderr y `run_status.txt`; el paso a A1 exige código
cero y reinicio no vacío. El runner copia y registra SHA-256 del reinicio.
Al acabar A1, el estado será `SIMULATIONS_COMPLETE_PENDING_VALIDATION`.

## Lanzamiento y recuperación

El wrapper local `launch_campaign.sh` usa un lock exclusivo, logs persistentes
y captura de errores. Un primer intento se detuvo antes de simular porque
`OMP_NUM_THREADS=1` hacía que `nproc` informara una CPU. Se retiraron
`OMP_NUM_THREADS`/`OMP_THREAD_LIMIT` del wrapper, conservando el control del
runner y `OPENBLAS_NUM_THREADS=1`; no cambió la configuración científica.
El error quedó en `launcher.log` y el segundo intento arrancó correctamente.

Proceso Windows/WSL oculto inicial: PID 49976. No usar ese PID como único
indicador; comprobar los procesos y logs actuales. Al inicio se observaron
ocho ranks de aproximadamente 0.5 GiB cada uno, y 4.7 GiB de memoria WSL usada.

Tras cargar las entradas (unos cinco minutos), cada rank llegó a unos 3.0 GiB
residentes, WSL usó 26 GiB y 5.4 GiB de swap, con aproximadamente 5.3 GiB
disponibles según `free`. Una muestra `vmstat 2 4` terminó con `si=so=0`,
ocho procesos ejecutables y CPU agregada alrededor del 50 % de las 16 CPUs
lógicas. Se observó avance hasta el año de equilibrio −2096. Esto permite
mantener la ejecución, pero se debe vigilar paginación, memoria disponible y
crecimiento del estado vegetal; no garantiza recursos suficientes para toda A1.

```bash
cat /home/dasan/exofarm-lpjml-runs/global_a1_20260907/campaign_status.txt
tail /home/dasan/exofarm-lpjml-runs/global_a1_20260907/launcher.log
tail /home/dasan/exofarm-lpjml-runs/global_a1_20260907/spinup_natural/stdout.log
```

El seguimiento horario existente se actualizó como «Seguimiento global A1
LPJmL», ID `seguimiento-de-descarga-lpjml`. Avisará al cambiar de fase,
terminar o requerir intervención; permanece en silencio durante avance normal.
No relanzar automáticamente ni duplicar la campaña. Un spin-up interrumpido
requiere inspección de checkpoints; un A1 fallido debe recuperar su reinicio
completo sin repetir el spin-up. El apagado/suspensión puede interrumpir el trabajo.

## Validación antes de comparar

### Control horario 2026-09-07 18:39 America/Bogota

Continúa `SPINUP_RUNNING`, con avance hasta −2017 frente a −2096 en la
comprobación inicial. Ocho ranks activos al 97–98 % CPU cada uno; 29 GiB RAM
usada, 1.9 GiB disponible, 4.0 GiB swap y 790 GiB libres en disco. Los dos
intervalos actuales de `vmstat 2 3` muestran `si=so=0`; no se observa paginación
sostenida ni fallo. El margen de RAM es menor y se mantiene bajo vigilancia.
No cambió de fase y A1 aún no comenzó; avance normal, sin aviso al usuario.

### Control horario 2026-09-07 19:40 America/Bogota

Sigue `SPINUP_RUNNING`, hasta −1934: 83 años simulados de avance desde el
control anterior. Ocho ranks al 98–99 % CPU, sin nuevas advertencias al final
del log. RAM usada 30 GiB, disponible 782 MiB, swap 4.0/8.0 GiB y disco libre
790 GiB. Los dos intervalos actuales de `vmstat` tienen `si=so=0`; el proceso
continúa computando con ritmo similar. El margen de RAM sigue disminuyendo:
vigilar crecimiento y paginación en el próximo control. A1 aún no comenzó;
no se relanzó ni se modificó la campaña.

### Control horario 2026-09-07 20:40 America/Bogota

`SPINUP_RUNNING` hasta −1869, 65 años simulados más desde el control anterior.
Ocho ranks activos al 99 % CPU, sin nuevas advertencias al final de stderr.
RAM usada 30 GiB, disponible 763 MiB, swap 4.0/8.0 GiB y disco libre 790 GiB;
el uso de memoria se mantiene próximo al control anterior. Las muestras
actuales de `vmstat` muestran intercambio nulo (`si=so=0`). Continúa el avance,
sin cambio de fase ni intervención; A1 y la comparación de flujos siguen pendientes.

### Control horario 2026-09-07 21:40 America/Bogota

Continúa `SPINUP_RUNNING`, hasta −1813: avance de 56 años simulados desde el
control anterior. Ocho ranks al 99 % CPU y sin nuevas advertencias al final
de stderr. RAM usada 30 GiB, disponible 765 MiB, swap 4.0/8.0 GiB y disco
libre 790 GiB; recursos similares al control previo. Los dos intervalos
actuales de `vmstat` indican `si=so=0`. El avance es más lento que al comienzo,
pero sostenido; sin cambio de fase, error ni necesidad de intervención confirmada.

### Control horario 2026-09-07 22:41 America/Bogota

`SPINUP_RUNNING` hasta −1745, 68 años simulados más desde el control anterior.
Ocho ranks al 99 % CPU, sin nuevas advertencias al final de stderr. RAM usada
30 GiB, disponible 764 MiB, swap 4.0/8.0 GiB y disco libre 790 GiB. Ambas
muestras actuales de `vmstat` muestran `si=so=0`; memoria y ritmo estables
respecto a controles recientes. Sin cambio de fase ni incidencia; A1 pendiente.

### Control horario 2026-09-07 23:41 America/Bogota

Sigue `SPINUP_RUNNING`, hasta −1675: avance de 70 años simulados desde el
control anterior. Ocho ranks activos al 99 % CPU, sin nuevas advertencias
al final de stderr. RAM usada 30 GiB, disponible 755 MiB, swap 4.0/8.0 GiB
y disco libre 790 GiB. Los dos intervalos actuales de `vmstat` muestran
`si=so=0`; recursos estables y avance sostenido. No se requiere intervención
confirmada; A1 y la validación/comparación global siguen pendientes.

### Control horario 2026-09-08 00:44 America/Bogota

Continúa `SPINUP_RUNNING`, hasta −1600, con 75 años simulados de avance desde
el control anterior. Ocho ranks al 99 % CPU y sin nuevas advertencias al final
de stderr. RAM usada 30 GiB, disponible 753 MiB, swap 4.0/8.0 GiB y disco
libre 790 GiB; ambos intervalos actuales de `vmstat` tienen `si=so=0`.
Recursos estables y avance sostenido, sin cambio de fase ni intervención.

### Control 2026-09-08 04:47 America/Bogota

Continúa `SPINUP_RUNNING`, hasta −1280: 320 años simulados de avance desde
la última comprobación documentada de las 00:44. Ocho ranks al 99 % CPU,
sin nuevas advertencias al final de stderr. RAM usada 29 GiB, disponible
1.3 GiB, swap 4.9/8.0 GiB y disco libre 790 GiB. Los dos intervalos actuales
de `vmstat` muestran `si=so=0`; el aumento acumulado de swap no corresponde
a paginación sostenida durante esta muestra. Avance confirmado, sin cambio
de fase ni intervención necesaria. No se atribuyen mediciones a los controles
intermedios sin evidencia registrada.

### Control horario 2026-09-08 05:48 America/Bogota

`SPINUP_RUNNING` hasta −1199, 81 años simulados de avance desde el control
anterior. Ocho ranks al 99 % CPU, sin nuevas advertencias al final de stderr.
RAM usada 29 GiB, disponible 1.3 GiB, swap 4.9/8.0 GiB y disco libre 790 GiB;
ambos intervalos actuales de `vmstat` indican `si=so=0`. Avance confirmado,
recursos similares al control previo y sin cambio de fase ni intervención.

### Control horario 2026-09-08 06:49 America/Bogota

`SPINUP_RUNNING` hasta −1118, 81 años simulados más desde el control anterior.
Ocho ranks al 99 % CPU, sin nuevas advertencias al final de stderr. RAM usada
29 GiB, disponible 1.3 GiB, swap 4.9/8.0 GiB y disco libre 790 GiB. Ambas
muestras actuales de `vmstat` tienen `si=so=0`; avance y recursos estables.
Sin cambio de fase ni intervención; resultados A1 y comparación pendientes.

### Control horario 2026-09-08 07:50 America/Bogota

Continúa `SPINUP_RUNNING`, hasta −1059: 59 años simulados más desde el control
anterior. Ocho ranks al 99 % CPU y sin nuevas advertencias al final de stderr.
RAM usada 30 GiB, disponible 1.1 GiB, swap 4.9/8.0 GiB y disco libre 790 GiB.
Los dos intervalos actuales de `vmstat` muestran `si=so=0`. Avance confirmado
con margen de RAM vigilado; sin cambio de fase ni intervención necesaria.

### Control horario 2026-09-08 08:51 America/Bogota

`SPINUP_RUNNING` hasta −1006, 53 años simulados más desde el control anterior.
Ocho ranks al 99 % CPU y sin nuevas advertencias al final de stderr. RAM usada
30 GiB, disponible 1.1 GiB, swap 4.9/8.0 GiB y disco libre 790 GiB; ambos
intervalos actuales de `vmstat` muestran `si=so=0`. El avance continúa con
recursos similares al control previo; sin cambio de fase ni intervención.

### Control horario 2026-09-08 09:51 America/Bogota

Sigue `SPINUP_RUNNING`, hasta −958: 48 años simulados más desde el control
horario anterior (−1006), y avance frente a −997 observado a las 09:02.
Ocho ranks al 99 % CPU; sin nuevas advertencias al final de stderr. RAM usada
30 GiB, disponible 1.1 GiB, swap 4.9/8.0 GiB y disco libre 790 GiB. Ambas
muestras actuales de `vmstat` muestran `si=so=0`. Continúa computando, con
recursos similares y sin cambio de fase ni intervención necesaria.

### Control horario 2026-09-08 10:50 America/Bogota

`SPINUP_RUNNING` hasta −908: 50 años simulados más desde el control anterior.
Ocho ranks al 99 % CPU; sin nuevas advertencias al final de stderr. RAM usada
30 GiB, disponible 1.1 GiB, swap 4.9/8.0 GiB y disco libre 790 GiB. Los dos
intervalos actuales de `vmstat` muestran `si=so=0`. Avance y recursos estables;
sin cambio de fase ni intervención. A1 y la comparación siguen pendientes.

### Control horario 2026-09-08 11:50 America/Bogota

Continúa `SPINUP_RUNNING`, hasta −860: 48 años simulados de avance desde el
control anterior. Ocho ranks al 99 % CPU y sin nuevas advertencias al final
de stderr. RAM usada 30 GiB, disponible 1.1 GiB, swap 4.9/8.0 GiB y disco
libre 790 GiB. Ambos intervalos actuales de `vmstat` tienen `si=so=0`;
avance y recursos estables, sin cambio de fase ni intervención necesaria.

### Control horario 2026-09-08 12:53 America/Bogota

Sigue `SPINUP_RUNNING`, hasta −814: 46 años simulados más desde el control
anterior. Ocho ranks al 99 % CPU y sin nuevas advertencias al final de stderr.
RAM usada 30 GiB, disponible 1.1 GiB, swap 4.9/8.0 GiB y disco libre 790 GiB.
Ambas muestras actuales de `vmstat` muestran `si=so=0`. Avance confirmado y
recursos similares al control previo; sin cambio de fase ni intervención.

### Control horario 2026-09-08 13:51 America/Bogota

`SPINUP_RUNNING` hasta −767: 47 años simulados más desde el control anterior.
Ocho ranks al 99 % CPU y sin nuevas advertencias al final de stderr. RAM usada
30 GiB, disponible 1.1 GiB, swap 4.9/8.0 GiB y disco libre 790 GiB. Ambos
intervalos actuales de `vmstat` tienen `si=so=0`. Avance y recursos estables;
sin cambio de fase ni intervención, con A1 y comparación aún pendientes.

### Control horario 2026-09-08 14:51 America/Bogota

Sigue `SPINUP_RUNNING`, hasta −720: 47 años simulados más desde el control
anterior. Ocho ranks al 99 % CPU y sin nuevas advertencias al final de stderr.
RAM usada 30 GiB, disponible 1.1 GiB, swap 4.9/8.0 GiB y disco libre 790 GiB.
Ambos intervalos actuales de `vmstat` muestran `si=so=0`. Avance sostenido
y recursos similares; sin cambio de fase ni intervención necesaria.

### Control horario 2026-09-08 15:52 America/Bogota

`SPINUP_RUNNING` hasta −670, 50 años simulados más desde el control anterior.
Ocho ranks al 99 % CPU; sin nuevas advertencias al final de stderr. RAM usada
30 GiB, disponible 1.1 GiB, swap 4.9/8.0 GiB y disco libre 790 GiB. Ambos
intervalos actuales de `vmstat` indican `si=so=0`. Avance sostenido y recursos
estables; sin cambio de fase ni intervención. A1 y comparación pendientes.

### Consulta de progreso 2026-09-08 16:54 America/Bogota

Verificación en vivo: `SPINUP_RUNNING` hasta −618, 52 años simulados más
desde las 15:52. Completados aproximadamente 1,482/3,800 años del spin-up
(39 %), tras 23 h 17 min. Los ocho ranks siguen al 99 % CPU. RAM disponible
1.1 GiB, swap 4.9/8 GiB y disco libre 790 GiB; ambos intervalos actuales de
`vmstat` muestran `si=so=0`. El final de stderr conserva las advertencias
conocidas de cobertura temporal. A unas 50 anualidades simuladas por hora,
restan aproximadamente 46 horas de spin-up; es una extrapolación variable
y no incluye la fase A1 posterior. Comparación de flujos todavía pendiente.

### Control horario 2026-09-08 17:53 America/Bogota

`SPINUP_RUNNING` hasta −568, 50 años simulados más desde la consulta anterior.
Ocho ranks al 99 % CPU tras 24 h 16 min. El lanzador conserva la comprobación
positiva de entradas y directorios; el final de stderr mantiene las advertencias
conocidas de cobertura temporal. RAM disponible 1.1 GiB, swap 4.9/8 GiB y
disco libre 790 GiB. Ambos intervalos actuales de `vmstat` muestran `si=so=0`.
Avance normal, sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control horario 2026-09-08 18:56 America/Bogota

`SPINUP_RUNNING` hasta −515, 53 años simulados más desde el control anterior.
Ocho ranks al 99 % CPU tras 25 h 19 min. El lanzador y el estado de fase
siguen sin indicar finalización; el final de stderr mantiene las advertencias
conocidas de cobertura temporal. RAM disponible 1.1 GiB, swap 4.9/8 GiB y
disco libre 790 GiB. Ambos intervalos actuales de `vmstat` muestran `si=so=0`.
Avance normal, sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control horario 2026-09-08 19:57 America/Bogota

`SPINUP_RUNNING` hasta −466, 49 años simulados más desde el control de las
18:56 y 16 más desde la consulta del usuario a las 19:35 (−482). Ocho ranks
al 99 % CPU tras 26 h 19 min. El lanzador conserva la comprobación positiva
de entradas y directorios; el final de stderr mantiene las advertencias
conocidas de cobertura temporal. RAM disponible 1.1 GiB, swap 4.9/8 GiB y
disco libre 790 GiB. Ambos intervalos actuales de `vmstat` muestran `si=so=0`.
Avance normal, sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control horario 2026-09-08 20:56 America/Bogota

`SPINUP_RUNNING` hasta −428, 38 años simulados más desde el control anterior.
Ocho ranks al 99 % CPU tras 27 h 19 min. El avance de este intervalo es menor
que el anterior, pero continúa; el final de stderr conserva las advertencias
conocidas de cobertura temporal. RAM disponible 1.1 GiB, swap 4.9/8 GiB y
disco libre 790 GiB. Ambos intervalos actuales de `vmstat` muestran `si=so=0`.
Sin cambio de fase ni intervención necesaria. A1 y comparación pendientes.

### Control horario 2026-09-08 22:00 America/Bogota

`SPINUP_RUNNING` hasta −386, 42 años simulados más desde el control anterior.
Ocho ranks al 99 % CPU tras 28 h 22 min. El lanzador conserva la comprobación
positiva de entradas y directorios; el final de stderr mantiene las advertencias
conocidas de cobertura temporal. RAM disponible 1.1 GiB, swap 4.9/8 GiB y
disco libre 790 GiB. El muestreo actual de `vmstat` no muestra intercambio
activo de swap. Avance sostenido, sin cambio de fase ni intervención necesaria.
A1 y comparación pendientes.

### Control horario 2026-09-08 23:00 America/Bogota

`SPINUP_RUNNING` hasta −345, 41 años simulados más desde el control anterior.
Ocho ranks al 99 % CPU tras 29 h 22 min. El lanzador conserva la comprobación
positiva de entradas y directorios; el final de stderr mantiene las advertencias
conocidas de cobertura temporal. RAM disponible 1.1 GiB, swap 4.9/8 GiB y
disco libre 790 GiB. Ambos intervalos actuales de `vmstat` muestran `si=so=0`.
Avance sostenido, sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control horario 2026-09-09 00:00 America/Bogota

`SPINUP_RUNNING` hasta −300, 45 años simulados más desde el control anterior.
Ocho ranks al 99 % CPU tras 30 h 22 min. El lanzador conserva la comprobación
positiva de entradas y directorios; el final de stderr mantiene las advertencias
conocidas de cobertura temporal. RAM disponible 1.1 GiB, swap 4.9/8 GiB y
disco libre 790 GiB. Ambos intervalos actuales de `vmstat` muestran `si=so=0`.
Avance sostenido, sin cambio de fase ni intervención. A1 y comparación pendientes.

### Control horario 2026-09-09 00:59 America/Bogota

`SPINUP_RUNNING` hasta −254, 46 años simulados más desde el control anterior.
Ocho ranks al 99 % CPU tras 31 h 22 min. El lanzador conserva la comprobación
positiva de entradas y directorios; el final de stderr mantiene las advertencias
conocidas de cobertura temporal. RAM disponible 1.2 GiB, swap 4.0/8 GiB y
disco libre 789 GiB. Ambos intervalos actuales de `vmstat` muestran `si=so=0`.
Avance sostenido, sin cambio de fase ni intervención. A1 y comparación pendientes.

Comprobar códigos de salida, reinicio y hash, cobertura espacial y máscaras,
diez años, unidades, valores finitos en celdas válidas y diagnósticos del balance
de N. No equiparar el tamaño rectangular del NetCDF con el número de celdas
válidas: el piloto mostró relleno geográfico. Ejecutar el analizador con
`--coverage global` solo después de aceptar cobertura y entradas. Las razones
de comparación quedan pendientes hasta disponer de productos válidos.

Los warnings de fechas, suelo y uso de suelo deben contarse y evaluarse.
La inspección de `src/landuse/landuse.c` del commit fijado (líneas 595–627)
confirmó que LPJmL divide las fracciones por su suma si ésta supera uno, después
de avisar. En el piloto la celda 27415 llegó a 1.004638; conservar la advertencia
y cuantificar su alcance global antes de la aceptación científica. No se
modificaron los datos oficiales ni el solver para silenciarla.

## Evidencia y siguiente resultado

El manifiesto de campaña fija hashes de configuraciones y de ambos BC, unidades
y referencias numéricas. Se conserva copia compacta en
[evidence/global_a1_20260907](evidence/global_a1_20260907/), junto con el
lanzador y las configuraciones. El resultado esperado es una tabla anual y
media N2O/NH3 LPJmL frente al incremento prescrito, con razones, cobertura,
salvedades y procedencia. Todavía no hay resultado numérico de LPJmL global.
