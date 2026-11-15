# Extensión autorizada LIFE Proxima A3–1000 h — 2026-10-11

**Ampliación explícita 2026-10-12:** el usuario confirmó los cuatro modelos
a 1000 h: completo existente y N₂O/NH₃/ambas fijas a A0, en paralelo.
El alcance limitado inferior es histórico; véase el
[nuevo procedimiento](life_proxima_a3_1000h_a0_comparison_2026-10-12.md).

## Decisión y pregunta

El usuario autorizó un retrieval completo **solo A3 a 1000 horas de
integración**, equivalente a 41.6667 días. Esta elección sustituye las
propuestas de 30/50 días y añade un punto a la secuencia A3 1/10/100/1000 h.
Es tiempo de observación sintética, no una estimación del tiempo de cómputo.
No se autorizan A1–1000 h, LOO, A0 fija ni una nueva parametrización P–T.

El objetivo es examinar la recuperación de NH₃/N₂O y la calidad de ajuste al
reducir el ruido, conservando la familia inferencial oficial. El aumento de
exposición puede mejorar restricciones y hacer más visible la discrepancia
del modelo; ningún resultado ni significancia se presuponen.

## Configuración reproducible

Se reutilizan el forward A3 aceptado y los errores LIFEsim clásicos a 10 h:
`sigma(1000 h)=sigma(10 h)*sqrt(10/1000)`. Respecto a 100 h, sigma baja por
`sqrt(10)`. Una nueva realización gaussiana independiente queda registrada
con semilla maestra **20261011** y semilla derivada en el índice/manifiesto.
Observable `Fp` en W m⁻² m⁻¹, centros y semianchos en μm, 31 canales,
4–18.5 μm, R instrumental 20, cuatro colectores de 2 m, throughput 5 %,
3 zodis y distancia 1.30 pc. Se mantiene el ruido diagonal clásico; no se
afirma validación instrumental temporal/correlacionada.

Retrieval: POSEIDON/Ubuntu `POSEIDON`, Madhu de seis parámetros, isochem,
O₂ incluido, superficie negra explícita fija en 1 bar, R del modelo 10000,
N_live=800, ev_tol=0.5, sin inflación ni x_tol. Hay 15 coordenadas declaradas,
14 efectivamente libres. El preflight compara exactamente los priors y la
configuración con el fullcheck del completo oficial A3–100 h, y verifica
la identidad del forward en unidades de los errores del nuevo dataset.
No se amplían priors ni se cambia la química/P–T durante este experimento.
La corrección numérica diagnosticada utiliza exactamente la rejilla nativa
del generador, **3–20 μm a R=10000** (18 971 puntos), en lugar de la rejilla
3.8–19 μm de los completos anteriores. Los **31 canales observados** siguen
idénticos. Registrar esta diferencia al comparar recuperaciones entre tiempos:
se conserva el modelo físico/prior, con una corrección explícita de discretización.

## Ejecución y fuente de verdad

**Actualización 2026-10-12:** el muestreo inicial se interrumpió sin un código
de cierre registrado. El usuario autorizó reanudar; se validaron checkpoint,
priors y hashes y se archivó el estado previo. R1 fue lanzado a las 17:25:14
COT con MPI6 `--resume`, mismo basename y scratch. El log vigente pasa a
`native_grid_retry/recovery_20261012_R1/retrieval.log`, y se mantiene como
estado central `native_grid_retry/campaign_state.json`.
[Registro completo de recuperación](life_proxima_a3_1000h_checkpoint_resume_2026-10-12.md).

- [Supervisor reproducible](../Thermal_Emission_Spectroscopy/scripts/run_proxima_a3_1000h.py).
- Campaña: `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1000h_full_20261011/`.
- Dataset separado: `life_data/LIFE_proxima_A3_1000h_O2_fixedBlack1bar_official.dat`.
- Índice separado: `life_data/dataset_index_A3_1000h_official.json`.
- Estado/manifiesto: `campaign_state.json`, `manifest.csv` en la campaña.
- Configuración resuelta: `resolved_configuration.json`; logs de generación,
  preflight y retrieval guardados junto al estado.
- Log/PID desacoplados: `retrievals/a3_1000h_full_20261011.supervisor.{log,pid}`.
- Scratch Linux: `/home/dasan/exofarm_a3_1000h_20261011/`; una corrida MPI6,
  una hebra BLAS por rank. No se eliminan checkpoints ni se reintenta un fallo.

El primer intento conserva íntegros los registros anteriores con estado FAILED.
El intento corregido tiene estado/manifiesto/configuración propios en
`a3_1000h_full_20261011/native_grid_retry/`, logs/PID en
`retrievals/a3_1000h_full_20261011.nativegrid.supervisor.{log,pid}` y scratch
`/home/dasan/exofarm_a3_1000h_20261011_nativegrid/`. Reutiliza el mismo dataset
de 1000 h por SHA-256 y verifica los priors y todas las opciones físicas
contra el completo oficial A3–100 h. Solo `wl_min`/`wl_max` admiten la
diferencia numérica documentada; los límites de aceptación 0.3/1 σ se mantienen.

Invocación efectuada en Ubuntu:
`/home/dasan/anaconda3/envs/POSEIDON/bin/python Thermal_Emission_Spectroscopy/scripts/run_proxima_a3_1000h.py --launch-native-grid-retry`.
El supervisor activa POSEIDON y las bibliotecas de opacidades/PHOENIX;
protege contra duplicados. El modo `--launch` describe el primer intento
histórico; ambos modos rechazan registros existentes y no deben usarse para
duplicar o reanudar la ejecución vigente.

El supervisor rechaza cualquier registro/dataset/scratch previo y procesos
científicos activos. Congela hashes de los datasets oficiales, índices
existentes, fuentes, forward y estados de las campañas cerradas. Archiva en
`products/` exclusivamente después de exit 0 y conserva scratch. Exit 0 queda
como **COMPLETE_PENDING_VALIDATION**, nunca como aceptación científica.

## Validación pendiente e interpretación

### Arranque verificado

**Incidencia del primer intento:** el preflight terminó el 2026-10-11 a
las 19:31:20 UTC con `ValueError: The fixed-surface/O2 model is not sufficiently
close to A3 LIFE truth (RMS=0.796, max=2.54 sigma)`. El cálculo preciso impreso
es RMS 0.7963 σ y máximo 2.545 σ, por encima de límites 0.3/1 σ.
**No se lanzó MPI ni MultiNest.** El estado del intento es `FAILED`, sus
productos/registro/scratch quedan preservados.

**Diagnóstico directo:** un único forward con PT/química verdaderas en la
rejilla nativa produjo RMS=0, máximo=0 σ y diferencia relativa nativa=0
frente al espectro guardado, con finitud PASS. Resultado reproducible en
`native_grid_diagnostic.json`, mediante
[control de rejilla](../Thermal_Emission_Spectroscopy/scripts/diagnose_proxima_a3_1000h_native_grid.py).
La discrepancia inicial se atribuye al cambio de rejilla de muestreo espectral;
este control no evalúa la capacidad Madhu/isochem ni demuestra un problema P–T.
El intento numérico corregido separado pasó el preflight (RMS=máximo=0 σ)
y entró en **RUNNING el 2026-10-11 a las 19:42:38 UTC (14:42:38 COT)**.
Supervisor PID **818**, mpiexec PID **921** y seis ranks **932–937** activos
verificados. Estado de esta inspección: inicialización/carga de opacidades;
todavía no se afirma posterior ni resultado científico. Comparación de
configuración PASS: 15 coordenadas declaradas, 14 libres, modelo físico y
priors idénticos, solo dos límites de rejilla numérica diferentes. Los
29 hashes protegidos del intento corregido pasaron (incluyen los registros
del primer intento); la prueba de lanzamiento duplicado fue rechazada con
exit 1 sin crear otra ejecución. Sintaxis de ambos scripts y siete enlaces
locales PASS. No se relajó el umbral, regeneró el dataset, cambió la física
ni repitió un muestreo anterior.

Supervisor desacoplado PID **794**, iniciado el 2026-10-11 a las
19:29 UTC (14:29 COT). Dataset generado y validado: **31 × 4** valores
finitos, centros/semianchos idénticos a A3–100 h y errores consistentes con
`sigma_100h/sqrt(10)` dentro del redondeo ASCII. Semilla derivada **1450560596**;
SHA-256 **5611c5904ef03aa02586bed15f14c0c2560ac5ae6fa9463ef420229311db75fa**.
S/N mediano del continuo 469.6: diagnóstico fotónico, no sigma de detección
molecular. Preparación alcanzó `PREFLIGHT` a las 19:29:42 UTC;
`campaign_state.json` tiene el estado posterior vigente.

Verificaciones adicionales: 22 hashes previos comprobados sin cambios;
segundo lanzamiento rechazado por la protección de registros existentes,
sin crear otra corrida. Sintaxis del supervisor y cinco enlaces locales PASS.
Versiones consultadas en el entorno efectivo: POSEIDON 1.4.0, NumPy 1.26.4,
SciPy 1.15.3, SpectRes 2.2.2 y PyMultiNest 2.12. `pip show lifesim` no encuentra
una distribución instalada en este entorno: esta preparación reutiliza los
productos clásicos congelados y no llama de nuevo al simulador LIFEsim.
Por tanto se distingue la procedencia histórica del ruido de las versiones
del entorno de postprocesado/retrieval actual.

Antes de aceptar: auditar posterior, espectro, PT/log_X, MultiNest, finitud,
priors, superficie fija, hashes, número de muestras y ajuste absoluto.
Preservar originales ante cualquier NaN y registrar el alcance exacto.
Comparar las restricciones y residuos con A3–100 h, sin restar ln Z entre
datasets de distinto tiempo. Un único completo nuevo no proporciona ln B
de presencia/enriquecimiento a 1000 h; requiere modelos emparejados adicionales
y autorización posterior. La masa posterior sobre A0 sigue siendo descriptiva
y dependiente de la referencia, del prior y de la familia isochem/Madhu.

Los seis completos oficiales anteriores, 36 LOO, tres A0 fija aceptadas con
salvedad y matriz legacy 8/8 se conservan. Los pilotos antiguos 500/1200 h
siguen separados y no sustituyen esta extensión.

## Referencias y contexto

- [Metodología de la serie oficial](life_proxima_a1_a3_1_10_100h_methodology_2026-10-03.md).
- [Síntesis de capas, aceptación y límites](life_proxima_exofarm_retrieval_layers_synthesis_2026-10-11.md).
- [Pilotos antiguos 500/1200 h](life_proxima_a3_500h_1200h_robust_retrieval_2026-08-31.md).
- Angerhausen et al. (2024), LIFE XII, [arXiv:2401.08492](https://arxiv.org/abs/2401.08492):
  contextualiza exposiciones de 10/50/100 días. **1000 h es una decisión del
  proyecto**, no una duración ni garantía de detección prescrita por el artículo.
