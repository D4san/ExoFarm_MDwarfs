# A3–1000 h completo: repetición con binning coherente

Autorización/arranque: 2026-10-14. Cierre revisado: 2026-10-15. Estado
operativo en la fuente: **`COMPLETE_PENDING_VALIDATION`**, `exit_code=0`,
productos archivados y comparación `SAVED`. La aceptación del registro sigue
como **`PENDING_INDEPENDENT_REVIEW`**. Los PID 777/978 son identificadores
históricos; al comprobar el cierre no había procesos Python/MPI activos.

## Pregunta y decisión

El usuario autoriza repetir exclusivamente el completo A3–1000 h para aislar
el efecto del operador de observación. Los controles anteriores demostraron
que integrar energía en intervalos centro±semiancho y convertir/integrar fotones
sobre bordes derivados de los centros producen observables diferentes. El
segundo procedimiento reproduce la generación LIFE existente. Véanse el
[diagnóstico de interfaz](life_proxima_nh3_1000h_interface_diagnosis_2026-10-14.md)
y los [controles de binning/PT](life_proxima_a3_binning_pt_controls_2026-10-14.md).

La nueva campaña es
`Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1000h_binning_corrected_20261014/`;
scratch `/home/dasan/exofarm_a3_1000h_binning_20261014/`.
El completo anterior permanece en `retrievals/a3_1000h_full_20261011/native_grid_retry/`.

## Contrato científico congelado

- Una corrida completa, A3, 1000 horas (41,67 días de integración).
- MPI15, un hilo por rank; 16 CPU lógicas y aproximadamente 30 GiB disponibles
  en la comprobación previa. Antes de lanzar MPI se exige memoria disponible
  evaluada mediante PSS agregado (páginas compartidas contadas una vez),
  más 0,5 GiB/rank para trabajo adicional de muestreo y 4 GiB de reserva.
- Radio, seis coordenadas Madhu y siete abundancias constantes libres:
  H2O, CO2, CH4, O2, O3, N2O y NH3. Quince coordenadas declaradas,
  catorce efectivamente libres; superficie negra fija a 1 bar.
- N_live=800; ev_tol=0,5; R=10000; rejilla nativa 3–20 μm.
- Priors idénticos al completo anterior, comprobados campo a campo antes de MPI.
- T_fine=180–310 K con paso 10 K, discretización térmica original conservada.
  Refinamiento térmico aplazado por decisión del usuario.
- Mismo archivo observado `life_data/LIFE_proxima_A3_1000h_O2_fixedBlack1bar_official.dat`,
  31 canales, SHA-256 `5611c5904ef03aa02586bed15f14c0c2560ac5ae6fa9463ef420229311db75fa`.
  Ruido diagonal fotónico y realización existente conservados; sin inflación,
  nueva semilla ni covarianza instrumental añadida.

El único cambio científico es el binning. No se reutilizan checkpoints de la
verosimilitud anterior. Tampoco se relanzan las tres hipótesis A0, los 36 LOO,
los seis oficiales ni la matriz histórica 8/8.

## Matemática e implementación

Para flujo energético nativo F_i en W m⁻² m⁻¹, el promedio de fotones y la
conversión a energía en el centro exacto λ_k equivalen a

`F_k = Σ_i [overlap(i,k) / width(k)] × [λ_i / λ_k] × F_i`.

En términos prácticos, el generador primero convierte el flujo energético
nativo a densidad de fotones, integra esos fotones dentro de cada canal LIFE
y convierte el resultado otra vez a flujo energético usando el centro exacto
del canal. La likelihood anterior llamaba a POSEIDON, que reconstruía cada
canal como `centro ± semiancho` y hacía la integración en flujo energético.
Eso desplazaba los bordes en la rejilla logarítmica: para centros `[1, 2, 4]`,
el canal central definido por puntos medios ocupa `[1.5, 3]`, mientras que el
recuadro simétrico alrededor de 2 queda en `[1.25, 2.75]`. El cambio corrigió
esa geometría y la ponderación fotónica; no movió los datos ni cambió la
atmósfera. En la descomposición del control sobre el mismo espectro, el mayor
componente fue el de bordes (RMS 2.414 σ; máximo 8.459 σ); el término de
ponderación energía/fotones aportó RMS 0.619 σ. Estas cifras describen
residuos del operador frente al ruido asignado, no significancias de detección.

Los bordes son puntos medios de centros consecutivos; los centros precisos
proceden del NPZ LIFE, evitando reconstruirlos del ASCII redondeado. El
adaptador rechaza otras rejillas, instrumentos o anchos. El binding afecta la
función global que usa el `forward_model` real durante muestreo y
postprocesamiento posterior; restaura el proceso al terminar. El paquete
POSEIDON instalado y el runner anterior permanecen intactos.

### Juicio de validez y supuestos

La corrección es científicamente apropiada para esta campaña sintética porque
hace coincidir el operador de la likelihood con la convención que produjo los
canales observados: remuestrea densidad de flujo de fotones sobre celdas
definidas por los puntos medios y convierte de regreso a flujo energético en
el centro de cada canal. Este tipo de remuestreo conserva el flujo integrado
en rejillas arbitrarias, incluidas las no uniformes ([SpectRes, Carnall 2017](https://arxiv.org/abs/1705.05165); [documentación de SpectRes](https://spectres.readthedocs.io/en/latest/)). La comprobación del proyecto contra el producto A3 guardado y el callback real del retrieval respalda la consistencia numérica de la implementación en el alcance probado.

La conclusión es deliberadamente acotada. El operador supone celdas top-hat,
bordes inferidos como puntos medios y densidad espectral constante por celda
nativa durante la integración. Los datos de 1000 h son los canales sintéticos
LIFE classic con incertidumbres escaladas desde 10 h; esta campaña no añade
una respuesta instrumental calibrada dentro de cada canal, una función de
dispersión espectral (LSF), ni covarianza entre canales. Por tanto, se valida
la consistencia entre generador y likelihood para este producto, no una
respuesta instrumental LIFE completa. Si se dispone de una curva de respuesta
calibrada, debe aplicarse de forma coherente al generador y al modelo directo,
y repetirse el preflight antes de interpretar nuevos retrievals.

Códigos reproducibles:

- [Operador probado](../Thermal_Emission_Spectroscopy/scripts/life_bin_operator_diagnostic.py).
- [Wrapper autorizado](../Thermal_Emission_Spectroscopy/scripts/run_life_retrieval_binning_corrected.py).
- [Supervisor y gate de recursos](../Thermal_Emission_Spectroscopy/scripts/launch_proxima_a3_binning_corrected.py).
- [Comparación al finalizar](../Thermal_Emission_Spectroscopy/scripts/compare_proxima_a3_binning_retrievals.py).

Verificación previa: compilación de los tres scripts y doce pruebas del
operador PASS. El preflight hace un forward vertical verdadero independiente,
comprueba la rejilla, especies y cierre contra LIFE, y verifica el callback
real de la verosimilitud. `operator_preflight.json`, `resource_gate.json`,
`resolved_configuration.json`, manifest y logs son la evidencia operativa.

Smoke test adicional: el comparador audita el completo anterior, 7.101 muestras,
ln Z=677,923472817355. Supervisor iniciado el 2026-10-14T17:55:00Z;
preflight PASS, cierre relativo 2,26485×10⁻¹⁴ y χ² verdad32,9783723351.
La comparación de todas las claves científicas/configuración y hash es PASS.

El gate inicial RSS×15 detuvo el lanzamiento **antes del muestreo**: pico
RSS6,75 GiB, estimación105,29 GiB frente a30,46 GiB disponibles. Se conserva
`initial_RSS_gate_failed_state.json` y el log original. Inspección del código
instalado: `absorption.py:735–740` comparte las tablas; solo `node_rank==0`
las carga/interpola, y `utility.py:315–344` asigna nbytes=0 en los demás ranks.
Multiplicar todo RSS cuenta de nuevo tablas compartidas y temporales del loader.
El [supervisor de continuación](../Thermal_Emission_Spectroscopy/scripts/continue_proxima_a3_binning_shared_memory.py)
ejecuta por ello el mismo preflight bajo MPI15, sin muestreo, mide la suma PSS
y exige margen antes de iniciar MultiNest. El probe se detiene si MemAvailable
baja de4 GiB. Registro `resource_gate_shared_memory.json`, log
`mpi15_memory_preflight.log`; supervisor padre prefijo
`a3_1000h_binning_corrected_20261014.sharedmemory.supervisor`.

**Resultado del gate medido (registro de arranque, 2026-10-14):** preflight
MPI15 completado sin muestreo y con cierre científico PASS en los quince ranks.
Pico PSS agregado9.2767 GiB; mínimo MemAvailable21.0307 GiB; después del probe
30.4517 GiB disponibles. Se exige pico más reserva11.5 GiB: PASS. Producción
iniciada con mpiexec PID978 y binding confirmado para ranks0–14 en
retrieval.log. Los42 hashes protegidos pasaron nuevamente. Esta instantánea
antecede al cierre del 2026-10-15 que se documenta abajo. Las1000 horas
corresponden a exposición sintética, no a tiempo CPU.

Verificación posterior al arranque: opacidades cargadas y contadores MultiNest
avanzando (1.050 replacements / 1.076 Total Samples). El ln Z inicial impreso
como asteriscos es un desbordamiento del campo de formato durante la fase
temprana; todavía no constituye una evidencia final interpretable. Solo se
usarán stats/resultados finales auditados, sin sustituirlos por el log temprano.

## Cierre, auditoría e interpretación (2026-10-15)

La corrida A3–1000 h terminó con `exit_code=0`; la comparación se guardó y no
quedaron procesos `python`, `mpiexec` o `mpirun` activos al revisar el estado.
La campaña conserva el estado operativo `COMPLETE_PENDING_VALIDATION` y la
aceptación `PENDING_INDEPENDENT_REVIEW`: el cierre de cómputo y la inspección
de esta comparación están documentados, mientras que la aceptación científica
formal sigue abierta por el ajuste residual y las limitaciones del modelo.

El comparador registró productos primarios finitos y dentro de priors;
posteriores exportadas consistentes con MultiNest; mismo tamaño de salida para
espectro (`18971×6`), perfil P–T (`100×6`) y `log_X` (`800×6`); 800 puntos
vivos en cada muestreo; y `issues=[]` en los resúmenes de momentos derivados.
La superficie `log_P_surf` es fija en cero y se conserva sin alterar. La figura
se inspeccionó visualmente. La tabla exacta, cuantiles y formas de productos
están en [comparison.json](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1000h_binning_corrected_20261014/comparison/comparison.json),
con la [figura PNG](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1000h_binning_corrected_20261014/comparison/posterior_PT_comparison.png)
y [figura PDF](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1000h_binning_corrected_20261014/comparison/posterior_PT_comparison.pdf).

| Resultado | Operador anterior | Binning coherente |
|---|---:|---:|
| `ln Z` ± error numérico | 677,92347 ± 0,26943 | 826,61108 ± 0,27287 |
| χ² del mejor ajuste | 542,64 | 242,88 |
| χ² reducido (17 dof efectivos) | 31,92 | 14,287 |
| Muestras posteriores exportadas | 7101 | 7168 |

La diferencia `Δln Z = 148,68760 ± 0,38347` (errores numéricos combinados en
cuadratura) cuantifica la sensibilidad al cambio del operador espectral en
esta comparación. **No es un ln Bayes entre hipótesis atmosféricas ni evidencia
de detección molecular; no se convierte a sigma.** El mismo modelo, datos,
priors, malla de opacidades y configuración física se conservaron; el cambio
aislado fue el binning. El descenso de χ² es grande (≈55,3 %), aunque el
χ² reducido corregido sigue cerca de 14,3. Por tanto, el ajuste todavía
presenta una discrepancia sustancial con los datos y el ruido asumido.

Los posteriores marginales describen otro efecto del operador:

| Parámetro | Anterior: mediana [95 %] | Corregido: mediana [95 %] | Cambio de mediana |
|---|---|---|---:|
| `log_N2O` | −6,10887 [−6,14042, −6,07793] | −6,05786 [−6,08659, −6,03037] | +0,051 dex (≈1,13×) |
| `log_NH3` | −10,48663 [−11,93358, −9,05097] | −9,12999 [−11,61744, −8,66668] | +1,357 dex (≈22,7×) |

En N₂O, la distribución corregida se desplaza modestamente hacia abundancias
mayores y los intervalos del 95 % apenas se solapan. En NH₃, la mediana sube
marcadamente, pero el intervalo sigue ancho y mantiene una cola hacia valores
bajos; la mediana no equivale a una detección robusta. En el perfil P–T, la
figura muestra diferencias sobre todo en la región alta de la atmósfera y una
coincidencia mucho mayor en profundidad. Son comparaciones descriptivas entre
dos operadores, condicionadas a una única realización sintética.

Los retrievals A0 existentes usaron el operador anterior. No corresponde
calcular a partir de ellos una preferencia libre/A0 con el nuevo completo.
Para esa pregunta se necesita una pareja A0–A3 con el mismo operador, datos y
tratamiento de likelihood. La química isochemical, la PT aproximada, la única
realización y el ruido fotónico idealizado siguen limitando la inferencia.

### Regla de uso después de esta prueba

El operador coherente quedó ejecutado dentro de la likelihood para este único
caso A3–1000 h, con preflight del callback real y restauración del binding al
terminar. El wrapper
[`run_life_retrieval_binning_corrected.py`](../Thermal_Emission_Spectroscopy/scripts/run_life_retrieval_binning_corrected.py)
está deliberadamente congelado a A3–1000 h y al hash de su dataset. Por tanto,
la corrección ya forma parte del registro metodológico y de este resultado;
las salidas anteriores siguen siendo reproducibles con su operador original.
Para otra exposición o para A0 se debe validar la misma convención contra los
centros, anchos, rejilla nativa y verdad correspondientes, y ejecutar las dos
hipótesis emparejadas con el mismo operador antes de comparar evidencias. El
runner general aún no selecciona automáticamente este callback. Esta nota
actualiza el estado respecto a los diagnósticos del 14 de octubre que, en ese
momento, recomendaban la prueba y decían correctamente que todavía no se había
implementado en un retrieval.
