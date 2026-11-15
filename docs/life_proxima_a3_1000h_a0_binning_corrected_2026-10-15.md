# A3–1000 h: tres restricciones A0 con el binning corregido

**Relanzamiento autorizado 2026-10-16 12:04 UTC / 07:04 COT:** el usuario
pidió volver a lanzar exactamente N₂O fija, NH₃ fija y ambas fijas. Para no
alterar el intento interrumpido, se creó la campaña separada
`a0_fixed_reference_A3_1000h_binning_corrected_20261016_relaunch_01` y un
scratch nuevo. No se restauraron los archivos NUL ni se reutilizan checkpoints;
el código conserva `checkpoint_reuse=false`. El completo corregido y el dataset
pasaron la verificación de hashes; dataset SHA-256
`5611c5904ef03aa02586bed15f14c0c2560ac5ae6fa9463ef420229311db75fa`.

En la última lectura 13:18:16UTC, el supervisor799 sigue vivo en `RUNNING`,
con `PASS_ALL_THREE_MPI5` y MPI5 PID1126/1171/1236, cinco ranks reales por
corrida. Las tres variantes ya muestrean: reemplazos/muestras N₂O 12450/61633,
NH₃ 11300/59725, conjunta11750/59165; ocho archivos raw de MultiNest por caso.
El PSS agregado de los ranks era≈6.72GiB; memoria disponible≈24GiB, swap0,
sin error observado. La evidencia ln(Z) de logs es provisional. La aceptación
continúa pendiente de cierre y auditoría. El heartbeat de90min sigue la ruta
nueva.

Fecha: 2026-10-15, America/Bogota. Autorización: lanzar exclusivamente las
tres referencias A0 a 1000 h, con cinco procesos MPI por corrida, hasta tres
corridas simultáneas y seguimiento cada 90 minutos. La revisión de 100 h queda
aplazada. Supervisor inicial PID814; continuación preflight PID816; la
fuente operativa es el estado y el manifest de la campaña indicados abajo.
Seis pruebas de contrato y doce pruebas del operador PASS; scripts compilados.
Monitor heartbeat `seguimiento-a3-1000-h-a0-binning-corregido` creado ACTIVE;
configuración guardada verificada con intervalo de 90 minutos.

**Interrupción detectada 2026-10-16, 11:44 UTC / 06:44 COT — intento original:**
El inspector falló al leer `campaign_state.json` con `JSONDecodeError:
Expecting value: line 1 column 1 (char 0)`. La inspección binaria confirma que
el archivo (16386 bytes) y `manifest.csv` (1790 bytes) están compuestos
íntegramente por bytes nulos; ambos registran última escritura a las10:10:30UTC.
El PID guardado816 ya no existe; `ps` no encuentra supervisor, los tres
`mpiexec` ni los quince workers, y `pgrep mpiexec` no devuelve procesos.

El último snapshot legible fue09:49UTC (41k/38k/37.05k reemplazos; 686281/
681683/673688 muestras). Los logs de retrieval avanzaron hasta sus marcas
09:48:49–09:50:14UTC: N₂O41400/704371, NH₃38550/700838 y conjunta37550/693688
(reemplazos/muestras). No contienen firmas fatales conocidas, pero tampoco
registran cierre ni código de salida. Los tres scratch conservan los ocho
archivos MultiNest por variante; no prueban aceptación o terminación. El log
`source_audit_R1` solo registra preflight PASS y los tres lanzamientos; no
explica la desaparición posterior. El `ValueError` del log supervisor original
es el fallo del gate inicial, ya sustituido por R1 PASS, no una causa actual.

Conclusión operativa: campaña interrumpida, cierre/exit code desconocidos,
productos no aceptados y PSS de ejecución no disponible porque ya no hay
procesos. No se tocó ni reconstruyó el estado/manifest ni se reanudó/reinició
nada en ese momento. Conservar logs y scratch; la autorización posterior y la
campaña limpia se documentan al inicio de esta bitácora. La causa exacta de la
interrupción original sigue sin establecerse.

**Seguimiento 2026-10-16, 09:49 UTC / 04:49 COT:**
`RUNNING`, supervisor816 conserva identidad; MPI5 1083/1130/1177 y quince
ranks OMP1 siguen activos. N₂O/NH₃/conjunta: 41000/38000/37050 reemplazos y
686281/681683/673688 evaluaciones; respecto a08:14UTC avanzaron
2150/3000/2450 y85200/84865/84691. Los quince contadores CPU aumentaron.
Cada caso mantiene ocho archivos MultiNest y cinco registros
`[operator-active]`; seis búsquedas de errores fatales no encontraron
coincidencias. No hay códigos finales ni productos aceptados; los ln Z de los
logs siguen siendo transitorios.

Estado `RUNNING`, aceptación `PENDING`, y manifest: solo las tres variantes
MPI5 autorizadas, dimensiones libres13/13/12 y dataset común SHA-256
`5611c5904ef03aa02586bed15f14c0c2560ac5ae6fa9463ef420229311db75fa`. El
operador actual conserva SHA-256
`ba17b7056eb094bd210aca23aacd6aa9dbdcfabdf65352d641faf93c20252731`; los
tres registros del operador indican PASS y callback real ligado a muestreo y
postproceso. RAM disponible23.44GiB, PSS de los19 procesos≈6.999GiB y swap0.
No se intervino ni se amplió el alcance; siguiente revisión en90min.

**Seguimiento 2026-10-16, 08:14 UTC / 2026-10-16, 03:14 COT:**
`RUNNING`, supervisor816 conserva identidad y siguen MPI5 1083/1130/1177,
cinco ranks por caso y quince activos OMP1. N₂O/NH₃/conjunta: 38850/35000/34600
reemplazos, 601081/596818/588997 evaluaciones; desde06:48UTC avanzaron
2250/3400/2650 reemplazos y77397/76938/78317 evaluaciones. Los quince
contadores CPU crecieron; cada caso tiene ocho archivos MultiNest, cinco
registros `[operator-active]` y cero patrones fatales.

Estado y manifest: exactamente las tres variantes MPI5 autorizadas, free
13/13/12; priors libres/tipos coinciden con el completo y solo cambian las
restricciones A0 especificadas. Dataset SHA-256
`5611c5904ef03aa02586bed15f14c0c2560ac5ae6fa9463ef420229311db75fa`; operador
SHA-256 `ba17b7056eb094bd210aca23aacd6aa9dbdcfabdf65352d641faf93c20252731`,
callback activo en muestreo/postproceso y source-equivalence PASS. RAM
disponible23.33GiB, PSS19procesos≈7.131GiB, swap0. Sin productos aceptados;
ln Z en cola sigue transitoria. No se intervino; monitor90min.

**Seguimiento 2026-10-16, 06:48 UTC / 2026-10-16, 01:48 COT:**
`RUNNING`, supervisor816 verificado; siguen tres MPI5 (1083/1130/1177), cinco
workers cada uno y quince ranks activos. N₂O/NH₃/conjunta: 36600/31600/31950
reemplazos y 523684/519880/510680 evaluaciones; frente a05:22UTC avanzaron
2450/3600/2300 reemplazos y70207/67763/64301 evaluaciones. Cada caso conserva
ocho archivos MultiNest, cinco registros `[operator-active]` y cero patrones
fatales en su log. CPU acumulada aumentó en los quince ranks.

El estado/manifest siguen limitados a las tres variantes autorizadas, MPI5,
dimensiones libres13/13/12 y dataset SHA-256
`5611c5904ef03aa02586bed15f14c0c2560ac5ae6fa9463ef420229311db75fa`; hash del
operador `ba17b7056eb094bd210aca23aacd6aa9dbdcfabdf65352d641faf93c20252731`.
Los registros de preflight confirman callback ligado durante muestreo y
postproceso; la comparación de los priors libres y tipos con el completo no
detectó diferencias. RAM disponible22.93GiB, PSS19procesos≈6.833GiB, swap0.
La continuación de source-equivalence permanece PASS. Los ln Z de cola son
transitorios: productos y aceptación siguen pendientes. Sin intervención;
monitor90min activo.

**Seguimiento 2026-10-16, 05:22 UTC / 2026-10-16, 00:22 COT:**
`RUNNING`, supervisor816 con identidad correcta y MPI5 1083/1130/1177,
cinco workers por caso (PMI_SIZE=5, OMP_NUM_THREADS=1). N₂O/NH₃/conjunta:
34150/28000/29650 reemplazos y453477/452117/446379 evaluaciones; desde
03:54UTC subieron2750/2600/2750 reemplazos y59831/58358/58383 evaluaciones.
CPU avanzó en los quince ranks; ocho archivos MultiNest por caso, cinco
bindings del operador por log y cero indicadores fatales.

El manifiesto conserva tres casos activos MPI5 y dimensiones libres13/13/12.
Dataset SHA-256 `5611c5904ef03aa02586bed15f14c0c2560ac5ae6fa9463ef420229311db75fa`;
valores A0 y opacidades retenidas conformes. Hash actual del operador
`ba17b7056eb094bd210aca23aacd6aa9dbdcfabdf65352d641faf93c20252731`;
auditoría de equivalencia PASS. RAM disponible24.41GiB, PSS19procesos≈6.412GiB,
swap0. No hay productos finales aceptados; ln Z visible en logs es transitoria
y no se interpreta. Sin cambios de proceso/rank; monitor90min activo.

**Seguimiento 2026-10-16, 03:54 UTC / 2026-10-15, 22:54 COT:**
`RUNNING`, sin error/fallo. Supervisor816 y MPI5 1083/1130/1177 mantienen
identidad; cinco workers por corrida, quince ranks activos, PMI_SIZE=5 y
OMP_NUM_THREADS=1. N₂O/NH₃/conjunta: 31400/25400/26900 reemplazos y
393646/393759/387996 evaluaciones; desde02:31UTC avanzaron
4150/2300/3250 reemplazos y66868/67944/64215 evaluaciones. El CPU avanzó
en los quince workers. Hay ocho archivos MultiNest por caso, cinco bindings
del operador en cada log y cero patrones fatales.

El manifiesto conserva tres casos `running`, MPI5 y dimensiones libres13/13/12.
Los tres usan el dataset con SHA-256
`5611c5904ef03aa02586bed15f14c0c2560ac5ae6fa9463ef420229311db75fa`; las
abundancias A0 fijadas y las opacidades retenidas coinciden con la configuración
autorizada. El operador actual conserva SHA-256
`ba17b7056eb094bd210aca23aacd6aa9dbdcfabdf65352d641faf93c20252731` y
`source_equivalence/audit.json` sigue en PASS. RAM disponible23.32GiB,
PSS19procesos≈6.629GiB, swap0. No hay productos finales aceptados; ln Z de
muestreo sigue provisional. Sin cambios de procesos, ranks o alcance; monitor
cada90min activo.

**Seguimiento 2026-10-16, 02:31 UTC / 2026-10-15, 21:31 COT:**
`RUNNING`, sin error/fallo. Supervisor816 mantiene identidad; MPI5
1083/1130/1177 conservan cinco ranks cada uno (15 en total), con PMI_SIZE=5
y OMP_NUM_THREADS=1. N₂O/NH₃/conjunta: 27250/23100/23650 reemplazos y
326778/325815/323781 evaluaciones; respecto a01:03UTC aumentaron
3650/2100/2250 reemplazos y58760/62010/58233 evaluaciones. Los quince
contadores CPU avanzaron. Cada log conserva cinco bindings del operador y
ocho archivos MultiNest; no aparecen indicadores fatales.

El dataset observado mantiene SHA-256
`5611c5904ef03aa02586bed15f14c0c2560ac5ae6fa9463ef420229311db75fa`.
Los tres manifiestos siguen `running`, MPI5 y dimensiones libres13/13/12;
las configuraciones resueltas fijan N₂O en−6.884325289636784 y NH₃
en−9.950526295665036, reteniendo ambas especies en opacidades. RAM disponible
23.75GiB, swap0; PSS agregado≈6.788GiB para19 procesos medidos. Ningún
resultado provisional de ln Z se interpreta y aún no hay productos finales
aceptados. El monitor continúa cada90min; no se alteraron procesos ni ranks.

**Seguimiento 2026-10-16, 01:03 UTC / 2026-10-15, 20:03 COT:**
`RUNNING`, sin error/fallo; supervisor816 y tres MPI5 (1083/1130/1177)
conservan identidad y cinco workers activos cada uno. N₂O/NH₃/conjunta:
23600/21000/21400 reemplazos y268018/263805/265548 evaluaciones.
Respecto a23:32UTC avanzaron3550/2000/2500 reemplazos y
69553/65746/67634 evaluaciones; aumentó CPU en los quince ranks. Ocho
archivos MultiNest por caso y resume.dat actualizados a20:03COT.
RAM disponible23.47GiB, swap0; PSS19procesos≈6.295GiB.

Los49 archivos protegidos y las tres configuraciones resueltas conservan
hashes. Se verifican15 coordenadas declaradas,13/13/12 libres, mismos valores
A0, opacidades N₂O/NH₃ retenidas y cinco registros de binding por corrida.
La prueba de equivalencia de fuente permanece PASS y su copia reconstruida
coincide con el hash del completo. Cero coincidencias fatales en logs. No hay
salidas finales aceptadas ni se interpretan evidencias transitorias; monitor90min
activo y otros tiempos aplazados, sin cambios de ejecución.

**Seguimiento 2026-10-15, 23:32 UTC / 18:32 COT:** la campaña sigue
`RUNNING`, sin error ni fallo registrado. Supervisor816 y tres MPI5
(1083/1130/1177) conservan identidad; cinco workers por comunicador,
quince ranks totales. Reemplazos N₂O/NH₃/conjunta20050/19000/18900;
evaluaciones198465/198059/197914. Frente a22:05UTC avanzaron
2400/1850/2050 reemplazos y54910/53717/54328 evaluaciones, respectivamente;
los quince contadores CPU aumentaron. Ocho archivos MultiNest por caso,
resume.dat con escrituras recientes y cinco registros de binding del operador
por corrida. Ninguna coincidencia fatal en los logs.

RAM disponible23.93GiB, swap0; PSS de supervisor, tres launchers y quince
workers≈6.30GiB (19 procesos, sin auxiliares PMI). Los49 hashes protegidos
y los tres hashes de configuraciones resueltas coinciden. Dimensiones15
declaradas y13/13/12 libres, valores fijos, opacidades N₂O/NH₃ retenidas,
dataset y prueba de equivalencia de fuente siguen conformes. Sin cambios
de ejecución, productos finales o aceptación; monitor90min continúa y las
exposiciones1/10/100h siguen aplazadas. No se interpretan lnZ provisionales.

**Seguimiento 2026-10-15, 22:05 UTC / 17:05 COT:** `RUNNING`;
los tres preflights MPI5 y el gate de recursos pasaron. Supervisor PID816
verificado por su comando; mpiexec N₂O/NH₃/conjunta PID1083/1130/1177,
con cinco workers reales cada uno, PMI_RANK0–4, PMI_SIZE5 y OMP_NUM_THREADS1.
No hay productos finales aceptados ni se interpretan evidencias provisionales.

| Corrida | Reemplazos MultiNest | Evaluaciones registradas | Estado |
|---|---:|---:|---|
| N₂O fija A0 | 17 650 | 143 555 | RUNNING, MPI5 |
| NH₃ fija A0 | 17 150 | 144 342 | RUNNING, MPI5 |
| Ambas fijas A0 | 16 850 | 143 586 | RUNNING, MPI5 |

Entre las lecturas de 22:03:49 y 22:05:31 UTC avanzaron los contadores de
las tres corridas; en la ventana final de 56 s los quince workers acumularon
aproximadamente 55–56 s CPU cada uno. Se encontraron ocho archivos MultiNest
por corrida y cero coincidencias fatales en logs. Memoria disponible24.24GiB,
swap0; PSS agregado de supervisor, tres launchers y quince workers≈6.32GiB
(19 procesos medidos; no incluye auxiliares PMI). Es una instantánea operativa.
Los49 archivos protegidos conservan sus hashes; equivalencia de fuente y
seis pruebas de contrato PASS. Se mantienen monitor90min, sin relanzamientos,
y la revisión1/10/100h aplazada.

## Pregunta y comparación

Se contrasta el modelo completo de abundancias libres con N₂O fijada a su
referencia A0 efectiva, NH₃ fijada a A0 y ambas fijadas a A0. Son restricciones
de abundancias con las opacidades retenidas. La referencia constante es la
misma del [procedimiento de enriquecimiento](life_proxima_a0_enrichment_methodology_2026-10-10.md):
log₁₀ X(N₂O)=−6.884325289636784 y log₁₀ X(NH₃)=−9.950526295665036.
Representa el promedio A0 ponderado en presión, condicionado a este modelo.

El [completo corregido existente](life_proxima_a3_1000h_binning_corrected_2026-10-14.md)
se reutiliza como referencia. Terminó exit0 con productos y comparación
guardados; conserva aceptación pendiente y χ² reducido≈14.29. La preferencia
entre estas hipótesis será condicional a esa familia de modelos aproximados.
Las referencias antiguas de 1000 h se preservan como sensibilidad del operador.

| Nueva corrida | MPI | Coordenadas declaradas / libres |
|---|---:|---:|
| N₂O fija a A0 | 5 | 15 / 13 |
| NH₃ fija a A0 | 5 | 15 / 13 |
| Ambas fijas a A0 | 5 | 15 / 12 |

Dataset común: `LIFE_proxima_A3_1000h_O2_fixedBlack1bar_official.dat`, 31
canales, SHA-256 `5611c5904ef03aa02586bed15f14c0c2560ac5ae6fa9463ef420229311db75fa`.
Se conservan la realización existente, ruido diagonal sin inflación, Madhu,
isochem, O₂, superficie negra fija a 1 bar, N_live=800, ev_tol=0.5, R=10000,
rejilla nativa 3–20 µm y nodos de opacidad 180–310 K cada 10 K. Solo cambian
los priors de las especies fijadas respecto al completo corregido.

## Ejecución reproducible

- [Supervisor y límites de recursos](../Thermal_Emission_Spectroscopy/scripts/launch_proxima_a0_binning_corrected.py).
- [Adaptador de las tres restricciones](../Thermal_Emission_Spectroscopy/scripts/run_life_a0_binning_corrected.py).
- [Pruebas de contrato](../Thermal_Emission_Spectroscopy/scripts/test_proxima_a0_binning_corrected.py).
- [Operador compartido con el completo](../Thermal_Emission_Spectroscopy/scripts/life_bin_operator_diagnostic.py).
- [Inspector de estado, ranks y progreso, solo lectura](../Thermal_Emission_Spectroscopy/scripts/inspect_proxima_a0_binning_corrected.py).
- Campaña: `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a0_fixed_reference_A3_1000h_binning_corrected_20261015/`.
- Scratch nuevo: `/home/dasan/exofarm_a0bin_A3_1000h_20261015/`.
- Log/PID del supervisor en `retrievals/`, prefijo `a0_fixed_reference_A3_1000h_binning_corrected_20261015.supervisor`.

Lanzamiento desde Ubuntu, usando el Python del entorno verificado POSEIDON:

```bash
/home/dasan/anaconda3/envs/POSEIDON/bin/python /mnt/c/Proyectos/Astro/ExoFarm_MDwarfs/Thermal_Emission_Spectroscopy/scripts/launch_proxima_a0_binning_corrected.py --launch
```

Cada preflight ejecuta MPI5 sin muestreo, verifica priors/dataset frente al
completo corregido y el callback real contra la verdad vertical A3 guardada.
La identidad del código del operador se contrasta con el snapshot
del completo y la equivalencia de fuente auditada que se detalla abajo.
La verdad vertical valida el operador, no impone las abundancias
del modelo restringido al generar ese control. El binding queda activo durante
MultiNest y postprocesamiento. Se miden picos PSS por comunicador MPI5; la cola
conserva 0.25 GiB/rank de trabajo y 4 GiB para el sistema, y reserva la parte
del pico aún no asignada a los loaders activos. El objetivo es tres MPI5
simultáneos cuando los recursos medidos lo permiten, con máximo 15 ranks.

Se rechazan directorios previos, procesos científicos ajenos y reanudación
de checkpoints con otra likelihood. Se conservan datos, códigos y productos
protegidos por hashes, los seis completos oficiales, 36 LOO y la matriz 8/8.
Un fallo detiene nuevos lanzamientos; mantiene los otros workers y todos los
productos. Exit0 conduce a `COMPLETE_PENDING_VALIDATION` y archivado.

### Continuación del gate de procedencia, antes del muestreo

El primer N₂O completó el preflight numérico MPI5 con cierre relativo
2.2648549702353193e−14 y χ² verdadero32.97837233512558. Después, el gate de
hash textual detuvo el supervisor: `ValueError: Observation operator differs
from the corrected full model`. No se había iniciado ningún sampler.

La edición posterior al completo modificó exclusivamente docstrings y dos
mensajes ValueError. Se reconstruyó la fuente previa revirtiendo esas cinco
ediciones: coincide byte a byte con el hash original
`194a1c6cc958a2f2b681bd207170f09ef7e9fab45b31fc0a03f8b7e3a6dd2c83`.
La fuente actual es
`ba17b7056eb094bd210aca23aacd6aa9dbdcfabdf65352d641faf93c20252731`.
Los AST coinciden tras retirar docstrings y normalizar solo esos dos mensajes;
no cambia ningún cálculo. El gate verifica de nuevo esa prueba; un cambio
aritmético falla el checksum de reconstrucción.

Evidencia: `source_equivalence/audit.json` y copia reconstruida, generadas por
[auditor de fuente](../Thermal_Emission_Spectroscopy/scripts/audit_life_operator_source_equivalence.py).
Estado/snapshot/log/PID originales preservados en
`pre_sampling_source_gate_failure/`; preflight inicial intacto.
La continuación explícita `--continue-documentation-gate` exige ausencia de
workers y de muestreo previo, verifica los demás hashes y repite los tres
preflights MPI5 en `preflight_R1/`, con scratch separado. Su log termina en
`.source_audit_R1.supervisor.log`; el PID vigente se guarda en el archivo PID
principal. No reutiliza checkpoints ni altera el completo corregido.

## Seguimiento y cierre

El monitor revisará cada 90 minutos estado/manifest, identidad del supervisor,
como máximo tres MPI5, ranks activos, preflight, progreso MultiNest, logs,
memoria y swap. Permanecerá en silencio en estados sanos sin novedades
accionables; notificará finalización, fallo o acción requerida.

Antes de aceptar: auditoría independiente de posterior, espectro, P–T,
log_X, MultiNest, finitud, hashes, priors y valores fijos en todas las muestras.
Los NaN de momentos derivados de coordenadas constantes se explicarán por
separado, conservando salidas y verificando los parámetros primarios.

Para cada restricción i, usando evidencias precisas de stats:

`ln B_i = ln Z_completo_corregido − ln Z_A0_i_corregido`.

El error numérico se combina en cuadratura. El sigma calibrado bilateral usa
la [convención Lin registrada](life_proxima_loo_sigma_lin_convention_2026-10-10.md),
con N/A si ln B≤0. La hipótesis conjunta no asigna un sigma a cada molécula.
La dirección de enriquecimiento se evalúa con la posterior libre. Se guardarán
tabla CSV/JSON e interpretación; el mal ajuste residual permanece junto a la
conclusión. Desactivar el monitor tras cerrar auditoría, tabla e informe.
