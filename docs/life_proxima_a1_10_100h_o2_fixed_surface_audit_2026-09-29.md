# Auditoría Proxima LIFE A1 a 10 y 100 h: interfaz corregida

**Estado al 2026-09-29:** ambos retrievals corregidos terminaron con `exit_code=0`,
se validaron y se compararon con los perfiles VULCAN A1 y las referencias
efectivas A0/A1. Esta auditoría se mantiene fuera de la matriz canónica
Proxima A0--A3 × {10 h, 240 h} (8/8).

## Pregunta y alcance

Comprobar si la misma interfaz POSEIDON que se usó para las auditorías A3
corregidas recupera el escenario A1 (benchmark de Tierra actual en la rama
química Proxima controlada) a 10 y 100 h. El planeta sigue siendo un análogo
terrestre bajo la SED de Proxima, no una atmósfera medida de Proxima b.

## Datos e índices

Ambos archivos tienen 31 bins de emisión `Fp` en `W m^-2 m^-1`, errores
diagonales de LIFEsim clásico y una realización de ruido por dataset.

| Tiempo | Dataset | SHA-256 | Procedencia |
| --- | --- | --- | --- |
| 10 h | `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A1_10h.dat` | `ed39ae6dc5b8ff0d5c8aca3d126a2945343a289be30f3b8d9e8e72c434ee9b8f` | Dataset de la matriz canónica, semilla registrada `1099171982`; se conserva intacto. |
| 100 h | `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A1_100h_O2_fixedBlack1bar_noxtol_audit.dat` | `d66c886238a2916312c645589be8601828fbf0a7cd2f02a383ef1d6a3454b5e3` | Nuevo dataset de auditoría generado desde `A1_emission.npz`; `sigma(t)=sigma(10 h)*sqrt(10/t)`, semilla de realización `460512527` (semilla maestra `20260929`). Índice: `dataset_index_A1_100h_O2_fixedBlack1bar_noxtol_audit.json`. |

El procedimiento de 100 h replica el empleado en la auditoría A3 intermedia,
con una realización nueva e independiente. Por ello, el contraste temporal
incluye variación de ruido además del cambio de incertidumbre; los `ln Z` de
datasets distintos no se interpretarán como factor de Bayes.

## Configuración POSEIDON

- POSEIDON `1.4.0`, Python `3.10.13`, NumPy `1.26.4`, entorno conda
  `/home/dasan/anaconda3/envs/POSEIDON` en Ubuntu/WSL.
- Perfil térmico recuperado `Madhu`; abundancias `X_profile=isochem`.
- Especies recuperadas: H2O, CO2, CH4, O2, O3, N2O y NH3; N2 de fondo.
- Superficie negra explícita fijada a 1 bar (`surface=True`, `log_P_surf=0`).
- `N_live=800`, `R=10000`, `error_inflation=none`; `x_tol` no forma parte del
  modelo. El likelihood es de ruido diagonal.
- Los dos `--setup-only` verificaron el archivo de datos, el modelo de 15
  parámetros, O2 y el prior de anchura nula de `log_P_surf`.

POSEIDON avisa que LIFE no tiene una función de transmisión instrumental
implementada y usa bins tipo caja. El dataset y la interfaz de esta campaña
también representan cada uno de los 31 bins observados; la advertencia queda
registrada para no atribuir una respuesta espectral más detallada.

## Ejecución y recuperación: registro histórico

Los dos intentos seriales iniciales (PIDs `38091`/`38269`) se detuvieron a
petición del usuario después de confirmar que consumían aproximadamente un
núcleo cada uno. Se eliminaron sus archivos parciales de `MultiNest_raw`, logs
de lanzamiento y PID files, limitados a los prefijos exactos A1--10 h y
A1--100 h. Se conservaron ambos datasets e índices de entrada; sus SHA-256
siguen siendo los indicados arriba.

Se verificó la ruta MPI compatible: el entorno POSEIDON usa MPICH `4.3.1`,
`mpi4py 4.1.0`, PyMultiNest `2.12` y MultiNest `3.10`, con `libmultinest_mpi`
instalada. El `/usr/bin/mpiexec` global es OpenMPI y no se usa. El `mpiexec`
de conda completó un smoke test de MultiNest de dos ranks (109 evaluaciones),
y el módulo `POSEIDON.retrieval` importó con `COMM_WORLD.size=2`.

Los nuevos retrievals se iniciaron con
[`launch_proxima_a1_o2_fixed_surface.sh`](../Thermal_Emission_Spectroscopy/scripts/launch_proxima_a1_o2_fixed_surface.sh),
seis ranks cada uno (12 workers de 16 CPUs), un hilo BLAS por rank y tags
`_O2_fixedBlack1bar_noxtol_MPI6`. Los PIDs de los lanzadores `mpiexec` son
`41224` (10 h) y `41269` (100 h). La verificación de arranque encontró seis
procesos Python por run y ambos avanzando por lectura/interpolación de
opacidades. En la última comprobación (10:15 COT; elapsed 14:53 y 14:51),
ambos lanzadores seguían activos y los logs mostraban 12,351 (10 h) y 12,282
(100 h) muestras, sin errores; las evidencias siguen siendo provisionales.
Había 20 GiB disponibles. El
monitor heartbeat
`monitor-proxima-life-a1-retrievals` se actualizó para vigilar estos tags/PIDs
cada dos horas, en silencio durante progreso sano.

El lanzador rechaza PID/logs y raíces POSEIDON existentes para impedir
duplicados y sobrescrituras. Los artefactos listados abajo permanecen
preservados; no se reinició ni se cambió el número de ranks.

## Incidente de cierre MPI (2026-09-29)

La inspección del 2026-09-29 a las 14:20 COT confirmó que ambos PIDs `mpiexec`
ya no existían. El A1--100 h se detuvo primero, alrededor de las 12:54 COT; el
A1--10 h se detuvo alrededor de las 13:27 COT. En ambos logs aparece el mismo
fallo de POSEIDON/MultiNest: en `nested.F90`, línea 2391 (unidad 57), el runtime
Fortran reportó `Cannot open file 'proxima_A1_<hours>h_O2_fixedBlack1bar_noxtol_MPI6-phys_live.points': Invalid argument`.
Hydra identificó como procesos fallidos los ranks 41274 (100 h) y 41232
(10 h), con código 9/señal 9; los launchers registraron `exit_code=9`. La causa
subyacente del argumento inválido aún no está identificada. El disco C: tenía
296 GiB libres durante la inspección, así que el log no respalda falta de
espacio como explicación.

Al interrumpirse, el log de 10 h había llegado a 310,975 muestras, 22,050
replacements y `ln Z=860.162459`; el de 100 h, a 228,866 muestras, 21,950
replacements y `ln Z=492.624776`. Son valores intermedios de MultiNest y no se
deben presentar como evidencia ni como ajuste final. Se conservan ambos logs,
PID files y prefijos crudos `MultiNest_raw/proxima_A1_*_MPI6*`, incluidos
`-.txt`, `-ev.dat`, `-resume.dat`, `-live.points`, `-phys_live.points`,
`-summary.txt`, `-stats.dat` y `-post_equal_weights.dat`. Los dos últimos
archivos de muestras equal-weight tenían solo 2 líneas (10 h) y 1 línea
(100 h) al inspeccionarlos. No aparecieron espectros recuperados, PT posterior
ni log-X final con el tag MPI6. Los checkpoints todavía requieren pruebas de
integridad y una evaluación explícita de si el postprocesamiento es recuperable;
su mera existencia no valida las posteriores.

Los datasets de entrada permanecen intactos y la matriz canónica 8/8 no se
modificó. En ese momento no se inició otra corrida de forma automática; el
muestreo quedó a la espera de una decisión explícita del usuario.

## Reanudación desde checkpoint MPI6R1 (2026-09-29)

A petición explícita del usuario se aprovechó el checkpoint de cada intento
MPI6, sin comenzar una cadena nueva desde cero. El análisis confirmó que los
archivos `resume.dat`, `live.points` y `phys_live.points` corresponden a
`N_live=800`, y que `ev.dat` contiene un segmento posterior al último checkpoint:

| Tiempo | Replacements guardados | Filas `ev.dat` requeridas | Filas fuente | Filas posteriores excluidas de la copia |
| --- | ---: | ---: | ---: | ---: |
| 10 h | 22,000 | 21,200 | 21,300 | 100 |
| 100 h | 21,900 | 21,100 | 21,200 | 100 |

Se comprobó que las filas copiadas y los 800 puntos vivos por archivo son
numéricos y finitos. Los prefijos fuente se dejaron intactos; únicamente las
copias nuevas `MPI6R1` recortan las cien filas que quedan fuera del último
checkpoint consistente. Los hashes fuente/staged, conteos y rutas constan en
[`proxima_A1_10h_O2_fixedBlack1bar_noxtol_MPI6R1.resume_manifest.json`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/proxima_A1_10h_O2_fixedBlack1bar_noxtol_MPI6R1.resume_manifest.json)
y el manifiesto equivalente de 100 h. La firma instalada de
`POSEIDON.retrieval.run_retrieval` acepta `resume`; también se validaron ambos
modelos con `--setup-only` antes de iniciar MultiNest.

Los dos trabajos se lanzaron simultáneamente con MPICH del entorno `POSEIDON`,
seis ranks y `resume=True`, bajo tags nuevos
`_O2_fixedBlack1bar_noxtol_MPI6R1`. Los lanzadores `mpiexec` son PID `43018`
(10 h) y PID `43070` (100 h). Para evitar repetir escritura MPI sobre `/mnt/c`,
los checkpoints y nuevos archivos se escriben en el filesystem Linux de WSL:
`/home/dasan/exofarm_life_a1_resume_20260929/10h` y `/home/dasan/exofarm_life_a1_resume_20260929/100h`.
El runner cosecha resultados a `Thermal_Emission_Spectroscopy/outputs/` solo
después de salida cero, sin sobrescribir destinos existentes. El fallo original
de Fortran sigue sin causa raíz demostrada; mover la escritura a ext4 es una
mitigación que se someterá a verificación durante esta reanudación.

En el control siguiente ambos padres MPI y sus seis workers seguían activos.
Los dos logs mostraron MultiNest v3.10, `no. of live points = 800`,
`dimensionality = 15`, `resuming from previous job` y `Starting MultiNest`.
En la lectura posterior, los contadores guardados avanzaron a 22,300
replacements (10 h) y 22,400 (100 h); los respectivos `ev.dat` tenían 21,500 y
21,700 filas. El archivo activo de 100 h iba 100 filas por delante del snapshot
`resume.dat`, así que se seguirá comprobando la sincronía al cerrar cada nuevo
checkpoint; no se recortan archivos activos. No reapareció el error de apertura
durante esta comprobación. Esto confirma la reanudación desde checkpoint, aunque
no es evidencia de convergencia ni de posterior final. La automatización
`monitor-proxima-life-a1-retrievals` se actualizó para seguir PIDs, logs,
scratch y cosecha cada dos horas, en silencio durante progreso sano. No se
usarán los `ln Z` MPI6 como resultados científicos ni se modificará 8/8.

## Límites de interpretación

La auditoría usa sigma diagonal y una realización por tiempo; no incluye
covarianza/inestabilidad instrumental. `X_profile=isochem` puede no reproducir
la estructura vertical VULCAN, y `Madhu` es una parametrización recuperada,
no el PT verdadero fijado. Las posteriores y distancias A0/A1 ya calculadas
son condicionales a esta configuración y no equivalen a detecciones formales.
Los valores intermedios de la primera ejecución MPI6 siguen excluidos; los
`ln Z` finales caracterizan cada dataset por separado y no se comparan como
factor de Bayes entre los tiempos.

## Cierre y resultados validados (2026-09-29 COT)

Los runs reanudados desde los checkpoints MPI6 finalizaron normalmente. Los
logs registran `process_exit ... exit_code=0`, el cierre de MultiNest y el
posprocesamiento de POSEIDON (`All done`). Los productos se generaron primero
en el filesystem ext4 de WSL. Como los logs no contienen el marcador de
cosecha esperado y los destinos del proyecto estaban ausentes, se copiaron
después de confirmar ambos cierres; los scratch y checkpoints originales se
conservaron. El validador volvió a comprobar la integridad numérica de las
salidas, los checkpoints de origen registrados en los manifiestos, la relación
entre muestras crudas y posteriores, y la finitud de los datos. No se repitió
el muestreo ni se sobrescribieron productos MPI6 anteriores.

| Tiempo | Dataset | `ln Z` | `χ²_red` (dof) | `R_p_ref` mediana [q16, q84] (`R_⊕`) | `log10 VMR N2O` | `log10 VMR NH3` | `log10 VMR O2` |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 h | Canónico A1, SHA-256 `ed39ae6d…e9b8f` | `889.38 ± 0.21` | 1.55 (16) | `1.2096 [1.1906, 1.2299]` | `−9.522 [−11.123, −7.886]` | `−10.080 [−11.326, −8.809]` | `−3.142 [−5.056, −1.301]` |
| 100 h | Auditoría independiente, semilla `460512527`, SHA-256 `d66c8862…b4e5e3` | `899.58 ± 0.24` | 3.18 (16) | `1.2117 [1.2063, 1.2178]` | `−7.127 [−7.437, −6.944]` | `−10.662 [−11.557, −9.715]` | `−3.412 [−5.071, −1.570]` |

Se validaron 6,567 y 6,774 muestras posteriores, respectivamente; cada caso
tiene espectro recuperado de 16,094 × 6, perfil P--T de 100 × 6, log-X de 800
filas y los ocho archivos esperados de MultiNest. El validador no encontró
NaN/Inf. Los `ln Z` se informan como propiedades de cada ajuste: los datos de
10 y 100 h son distintos y el segundo usa otra realización, por lo que su
diferencia no es un factor de Bayes.

### Referencias efectivas y lectura científica

Las medias columnares ponderadas en presión (`log10 VMR`) son:

| Especie | A0 efectiva | A1 efectiva |
| --- | ---: | ---: |
| N2O | −6.884 | −6.734 |
| NH3 | −9.951 | −9.305 |
| O2 | −0.696 | −0.696 |

La separación firmada `(mediana posterior − referencia)/σ68` es descriptiva y
condicional al modelo. Frente a A0, los valores `(N2O, NH3, O2)` son
`(−1.63, −0.10, −1.30) σ` a 10 h y `(−0.99, −0.77, −1.55) σ` a 100 h.
Frente a A1 son `(−1.72, −0.62, −1.30) σ` y
`(−1.60, −1.47, −1.55) σ`, respectivamente. A 100 h N2O se estrecha mucho y
su mediana se acerca a las referencias A0/A1; NH3 sigue ancho y desplazado a
valores bajos, y O2 no queda recuperado pese a que forma parte del modelo.
Estos resultados no distinguen formalmente A1 de A0: las referencias efectivas
de ambos escenarios son cercanas, el conjunto usa una sola realización y el
likelihood es diagonal.

El mejor ajuste a 100 h está más tensionado (`χ²_red=3.18`) que el de 10 h
(`χ²_red=1.55`). Esto no demuestra que más integración empeore el instrumento:
los datasets tienen realizaciones distintas y el modelo puede no representar
los perfiles verticales verdaderos. En el PT, la mediana recuperada difiere del
perfil VULCAN A1 con RMS de 56.46 K (10 h) y 54.36 K (100 h); la verdad cae
dentro de las bandas marginales de 68 % en solo 7 % y 8 % de los niveles, y
dentro de las de 95 % en 21 % y 15 %. La comparación nivel a nivel no mide
cobertura conjunta, pero muestra que el PT recuperado no reproduce bien el
perfil verdadero, por lo que la lectura de abundancias también es condicional a
esta discrepancia.

### Productos y reproducción

- Validador y generador: [`audit_proxima_a1_mpi_retrievals.py`](../Thermal_Emission_Spectroscopy/scripts/audit_proxima_a1_mpi_retrievals.py).
- Figura de posteriores y perfiles P--T: [PNG](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A1_10_100h_MPI6R1_posteriors_PT_proxima.png) / [PDF](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A1_10_100h_MPI6R1_posteriors_PT_proxima.pdf).
- Resumen numérico y manifiesto de validación: [`JSON`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/retrieval_A1_10_100h_MPI6R1_posteriors_PT_proxima_summary.json).
- Logs y manifiestos de reanudación: `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/proxima_A1_{10h,100h}_O2_fixedBlack1bar_noxtol_MPI6R1.launch.log` y `*.resume_manifest.json`; productos POSEIDON bajo `retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/`.

El experimento sigue excluido de la matriz 8/8. Para afirmar distinción entre
escenarios haría falta una comparación emparejada de modelos A0/A1 sobre el
mismo dataset, marginalizando parámetros nuisance y evaluando robustez frente
a varias realizaciones y, en la fase instrumental, covarianza de LIFEsimMC/PHRINGE.
