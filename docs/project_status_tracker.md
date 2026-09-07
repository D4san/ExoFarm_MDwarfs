# ExoFarm Project Status and Management Tracker

**Fecha de actualización:** 2026-09-06
**Propósito:** Centralizar el estado operativo, dependencias de software,
decisiones de diseño y tareas técnicas pendientes del pipeline ExoFarm.

**Reanudación:** antes de iniciar trabajo técnico, leer
[`project_resume.md`](project_resume.md). Para la procedencia del benchmark
Tierra--Sol que alimentará LIFE, leer también
[`earth_sun_n2o_matrix_provenance_2026-07-20.md`](earth_sun_n2o_matrix_provenance_2026-07-20.md).

---

## 1. Estado operativo de las etapas

```mermaid
graph TD
    Stage0["Etapa 0: LPJmL, prueba reactivada"] -. "flujo molecular tras validación" .-> Stage1["Etapa I: VULCAN"]
    Stage1 -->|"Earth A0--A3 2026-06-15: benchmark pre-N2O"| Stage3A["Capa 1: emisión/LIFE Tierra-Sol a 10 pc"]
    ProxSED["SED Proxima validada"] --> Stage1P["Nueva Etapa I: Proxima A0--A3"]
    Stage1P -->|"PT y química exportados"| Stage3B["Capa 2: emisión/LIFE Proxima"]
    Stage1 -->|Perfiles químicos y PT| Stage2["Etapa II: transmisión, POSEIDON y JWST"]
```

### Etapa 0: flujos agrícolas upstream

- **Estado:** **piloto de interfaz aceptado el 2026-09-06 y paquete MPI portátil
  preparado** para Franck et al.
  (2011), con benchmark agrícola de `N2O`/`NH3` y rama de rendimiento
  potencial; reproducción global pendiente.
- **Ejecución verificada:** checkout oficial LPJmL `v6.0.6`, commit
  `5af44a1ed023279a23c28d6dfe76945b97aaac57`; compilación serial y comprobaciones
  locales superadas. Paquete estándar oficial verificado por tamaño/MD5 y
  extracción (76 archivos); campaña `pilot_20260907T031220Z` terminada con
  código 0 en las tres etapas y NetCDF 1996--2005 auditados.
- **Flujo reproducible:** `workflows/franck2011_reproduction`, además de las
  notas metodológicas y el conversor de masa de N a flujo molecular en
  [`convert_lpjml_n_flux.py`](../Agricultural_Fluxes_LPJmL/scripts/convert_lpjml_n_flux.py).
- **Límite actual:** no existen aún resultados LPJmL científicos ni un
  forzamiento agrícola validado para VULCAN. El piloto solo aceptará la interfaz
  y las unidades; la integración planetaria exige una corrida global completa.
- **Próxima ejecución:** instalar el checkout fijado con MPICH en el otro PC,
  verificar recursos/entradas, pasar el smoke test MPI de ocho celdas y correr
  por separado el spin-up global y A1 según
  [`lpjml_global_a1_mpi_other_pc_runbook.md`](lpjml_global_a1_mpi_other_pc_runbook.md).

### Etapa I: modelado fotoquímico

- **Tierra-Sol:** completado como conjunto aceptado de 2026-06-15. Los cuatro
  escenarios A0--A3 alcanzaron el estado estacionario guardado (`end_case = 1`).
  A2/A3 anteceden la corrección posterior de N2O: son un benchmark de interfaz
  LIFE, no la realización final de la matriz vigente hasta decidir un rerun o
  su uso explícitamente histórico.
- **TRAPPIST-1e:** completado y aceptado con salvedad de convergencia parcial
  (`end_case = 3`), atribuida a `C2H5` traza alrededor de 0.019 bar.
- **Parámetros físicos:** corregidos y auditados el 2026-06-15 (radio
  planetario, gravedad, espectro solar y eliminación del duplicado de `H2SO4`).
- **Proxima / nueva rama:** ejecutada como `life_proxima_b_earthlike`: SED
  MUSCLES versionada, rama VULCAN A0--A3 con PT/Kzz terrestre controlado y
  productos de emisión/LIFEsim bajo su propio árbol. No es una modificación de
  Earth--Sun ni TRAPPIST-1e.

### Etapa II: espectroscopia de transmisión y retrieval

- **Espectros forward y ruido:** completados para la campaña de transmisión
  TRAPPIST-1e.
- **Campaña de inversión actual:** la matriz optimizada A0/A3 de 18 combinaciones
  terminó en Ubuntu/WSL con los perfiles fotoquímicos corregidos. El commit
  `fb9812d` actualizó los BC N2O y regeneró los `.vul`/exports TRAPPIST usados
  por esta rama; la salvedad Earth--Sun de junio no se transfiere aquí. Las
  últimas cuatro ejecuciones cerraron el 2026-07-12 con código 0. Las 42 corridas
  anteriores se preservan como evidencia legacy, no como base de interpretación
  actual.
- **Capa curada:** las figuras actuales viven en
  [`Transmission_Spectroscopy/final_products/`](../Transmission_Spectroscopy/final_products/)
  y deben mantener la salvedad de convergencia parcial de TRAPPIST-1e.

### Etapa III: emisión térmica, LIFE y LIFEsimMC

La reconstrucción metodológica reproducible de las dos capas, desde los datos
de entrada hasta el análisis y los retrievals, está en
[`life_stage_iii_classic_methodology_2026-08-30.md`](life_stage_iii_classic_methodology_2026-08-30.md).
La síntesis que reúne metodología, tablas, resultados y el atlas de plots está
en [`life_stage_iii_integrated_methodology_results_2026-08-30.md`](life_stage_iii_integrated_methodology_results_2026-08-30.md).

- **Estado consolidado (2026-08-30, actualizado 2026-08-31):** **rama LIFEsim
  clásica validada y cerrada documentalmente.** El entorno histórico conda
  `ExoFarm_LIFE` contenía POSEIDON 1.4.0 (+71 GB de opacidades, MD5 verificado),
  LIFEsim 0.2.32, LIFEsimMC 1.3.5 y PHRINGE 1.8.2. La reejecución actual se
  completó en Ubuntu/WSL con el entorno `POSEIDON` de
  `/home/wsldasan/miniconda3/envs/POSEIDON`, donde ahora están instalados
  LIFEsim 0.2.32 y el SpectRes modificado de fdannert (`2.1.1`, con
  `edge_mode`). Campaña `life_earth_sun_10pc_interface_v1`:
  forward de emisión A0--A3 + 18 contrafactuales + S/N con LIFEsim clásico
  ([informe](life_earth_sun_10pc_interface_snr_2026-07-22.md)). Interfaz validada
  (chequeo cuerpo negro PASS); tecnofirma ExoFarm **bajo el ruido** en baseline
  LIFE 2 m a 10 pc (mejor pico N2O 7.82 µm; √t confirmado). Perfiles
  pre-corrección: no es la matriz vigente.
- **Capa 2 `life_proxima_b_earthlike` — ejecutada (2026-07-23).** SED MUSCLES v22
  GJ551 → flujo superficial VULCAN (validado, bolométrica 1.037) → VULCAN Proxima
  A0--A3 **todos `end_case=1`** (BC corregidos, PT terrestre) → emisión POSEIDON +
  contrafactuales → S/N escena LIFE X (R=20, z=3, 1.30 pc; calibrada 166.5 vs 170
  @D=2m). Resultado: la tecnofirma A3 alcanza **S/N=5 en ~11--32 h** (N2O 17/7.8 µm)
  frente a años en Tierra--Sol — ~30--65× más detectable por cercanía. Análogo M
  controlado, no la atmósfera medida de Proxima b.
  [Bitácora](life_proxima_b_branch_bitacora_2026-07-22.md).
- **Retrievals de emisión (2026-07-25):** matriz canónica de 8 corridas Proxima A0--A3 x
  {10 h, 240 h} ejecutada con configuración validada (PT Madhu + `Piette20` +
  prior `R_p_ref` en metros). Con una campaña estándar de 10 d solo A3 mide N2O
  excluyendo la referencia pre-agrícola efectiva (3.14σ); A2/A1 quedan como
  límites superiores y no permiten extrapolar un número de campañas. El
  retrieval es más conservador que el diagnóstico de S/N. Los cuatro datasets
  de 1200 h y el retrieval A3--1200 h son evidencia de auditoría/piloto excluida
  de la matriz canónica. El piloto adicional A3--500 h ejecutado el 2026-08-31
  también queda excluido. El piloto histórico terminó con `ln Z = 893.18 +/-
  0.40`, `chi^2_red = 1.59` y radio `1.23 R_E`; el dataset usado coincide byte
  a byte con la observación directa de LIFEsim. Después se relanzaron por
  separado A3--500 h y A3--1200 h con datasets directos, `N_live=800` y la
  configuración actual de `Piette20`: `ln Z=901.17`, `chi^2_red=2.07` y
  `R_p_ref=1.23 R_E` a 500 h; `ln Z=898.31`, `chi^2_red=2.82` y
  `R_p_ref=1.26 R_E` a 1200 h. Ambos son auditoría/piloto y no cambian la
  matriz canónica.
  [Diseño y resultados](life_retrieval_campaign_design_2026-07-25.md),
  [auditoría](stage_iii_scientific_audit_2026-07-25.md).
- **Pendiente Etapa III:** rama LIFEsimMC/PHRINGE (inestabilidad instrumental +
  covarianza), múltiples realizaciones de ruido, modelos con/sin molécula y
  decisión de procedencia N2O de Tierra--Sol.
  Memoria: máx 2 solvers VULCAN a la vez (WSL 7.6 GB).
- **Objetivo:** la rama clásica ya generó forwards, ruido astrofísico/fotónico,
  S/N y retrievals diagonales. La extensión pendiente debe añadir ruido
  instrumental/covarianza antes de convertir esos resultados en una conclusión
  de detectabilidad instrumental de LIFE.
- **Contrato:** es una rama paralela a transmisión/JWST. No reutiliza espectros
  de transmisión, ruido PandExo ni conteos de tránsitos como entradas LIFE.
  La ruta técnica de ruido instrumental prevista es LIFEsimMC/PHRINGE; LIFEsim
  clásico queda para referencia astrofísica/yield.
- **Programa de dos capas:** `life_earth_sun_10pc` usa el conjunto Tierra--Sol
  congelado de 2026-06-15 para la primera validación de interfaz. La
  interpretación científica de la matriz vigente queda bloqueada por la
  salvedad de N2O. `life_proxima_b_earthlike` es la
  segunda capa y completó SED → VULCAN Proxima A0--A3 → emisión/LIFEsim clásico
  → S/N → retrievals canónicos. Ambas tienen productos clásicos autorizados; la
  rama instrumental LIFEsimMC/PHRINGE continúa pendiente.
- **Plan y puertas de activación:**
  [`docs/life_lifesim_stage_iii_plan.md`](life_lifesim_stage_iii_plan.md),
  [plan operativo de dos capas](life_stage_iii_two_layer_workplan_2026-07-20.md)
  y [`Thermal_Emission_Spectroscopy/README.md`](../Thermal_Emission_Spectroscopy/README.md).
  La selección y sus límites están en
  [`docs/life_target_selection_2026-07-20.md`](life_target_selection_2026-07-20.md).

---

## 2. Dependencias de software y entorno

- **VULCAN:** solver fotoquímico local en `VULCAN/`.
- **POSEIDON:** código de forward/retrieval en el entorno Anaconda `POSEIDON` de
  Ubuntu/WSL. Las rutas activas y requisitos de entrada están documentados en
  `Transmission_Spectroscopy/README.md`.
- **PandExo:** simulación de ruido de JWST exclusiva de la Etapa II.
- **LIFEsimMC + PHRINGE:** instalados y verificados por importación, pero aún no
  ejecutados como campaña científica de la Etapa III. Antes de una
  corrida se deben congelar versión/commit, licencia, entorno, diseño LIFE,
  escena astrofísica y la compatibilidad con la exportación de emisión de
  POSEIDON.
- **Espectro solar local Gueymard:** su ruta, archivo y checksum deben
  preservarse junto con la cita metodológica; no sustituirlo por una SED solar
  genérica al construir el benchmark.
- **Espectro TRAPPIST-1:** procedente de Mega-MUSCLES y escalado a flujo
  superficial en la etapa fotoquímica.
- **Espectro Proxima:** MUSCLES/MAST v22 preservado con metadatos y checksum;
  conversión a flujo superficial VULCAN validada y usada en la rama A0--A3.

---

## 3. Decisiones de diseño clave

| Fecha | Decisión | Razón / justificación | Estado |
| :--- | :--- | :--- | :--- |
| 2026-09-06 | Preparar el primer global como A1 actual y ejecutarlo con MPI en otro PC | Permite obtener primero flujos físicos de N2O/NH3 sin mezclar la reconstrucción todavía incompleta de los escenarios de capacidad de carga. Se fijaron LPJmL 6.0.6, MPICH, salida compacta coordinada, smoke test de ocho celdas y fases spin-up/A1 recuperables. | Paquete y runbook verificados; ejecución global pendiente del PC destino |
| 2026-09-06 | Aceptar el piloto LPJmL de una celda | Las entradas oficiales pasaron tamaño, MD5 y extracción; spin-up, A1 con N y rendimiento potencial terminaron con código 0; los NetCDF 1996--2005 tienen unidades, dimensiones y valores finitos plausibles. | Cerrado como prueba de interfaz; no es un resultado global ni un forzamiento VULCAN |
| 2026-09-01 | Reactivar la Etapa 0 para una primera prueba Franck 2011 + N2O/NH3 | El usuario autorizó una prueba reproducible que separe la reproducción moderna de capacidad de carga del benchmark físico con ciclo de N. | Cerrado para el piloto; reproducción global activa |
| 2026-09-01 | Evaluar Bayes factors rápidos para A3/A0 y el exceso de N2O | Se compararon plantillas fijas sobre el mismo dataset A3--240 h, con la likelihood diagonal de `Fp`; se separó la comparación de escenario de la comparación molecular. | Cerrado como experimento de auditoría; evidencia marginalizada e instrumental pendiente |
| 2026-06-15 | Aceptar TRAPPIST-1e en `end_case = 3` | La no convergencia está dominada por química traza irrelevante para los objetivos espectrales. | Cerrado con salvedad |
| 2026-06-30 | Promover Lin PT + `100x CO2` para TRAPPIST-1e | Perfil térmico y abundancia de `CO2` adoptados como baseline oficial; los isoquímicos anteriores pasan a legacy. | Cerrado |
| 2026-07-01 | Corregir `alpha_N2O` y piso de ruido | Se alinearon los flujos de `N2O` con los alpha 2.55 y 15, y se impuso el piso de ruido de PandExo. | Cerrado |
| 2026-07-02 | Migrar el plot de posterior de notebook a script | `plot_profile_posterior_comparison.py` se convirtió en la ruta más robusta para la matriz vigente. | Cerrado |
| 2026-07-02 | Corregir priors y piso de superficie | Se activó `surface=True`, con priors revisados para abundancias y presión superficial. | Cerrado |
| 2026-07-12 | Completar campaña optimizada de retrievals | Las 18 corridas A0/A3 finalizaron; advertencias de borde de prior quedan como salvedad, no como fallos. | Cerrado |
| 2026-07-13 | Promover el par conjunto A0/A3 de 100+100 | Presupuesto total de 200 tránsitos para las figuras actuales; 5/50 se conservan como legacy. | Cerrado |
| 2026-07-20 | Suspender la Etapa 0 LPJmL | Mantener código, checkout y documentación, pero no dedicar ejecución ni acoplamiento mientras se prioriza la interpretación observacional. | Activo / suspendido |
| 2026-07-20 | Crear una Etapa III separada para LIFE | Emisión térmica y observación directa requieren un observable, una interfaz instrumental y métricas diferentes de transmisión/JWST. | Planificado |
| 2026-07-20 | Usar LIFEsimMC/PHRINGE para ruido instrumental | LIFEsimMC modela inestabilidades y covarianza; LIFEsim clásico no sustituye este caso. | Planificado |
| 2026-07-20 | Adoptar Tierra--Sol a 10 pc como objetivo LIFE primario | Es un benchmark publicado para retrievals LIFE y para LIFEsimMC con ruido correlacionado; reutiliza el conjunto Tierra--Sol convergido como interfaz pre-corrección y aísla la perturbación A0--A3. | Cerrado para alcance; interpretación pendiente de procedencia |
| 2026-07-20 | Priorizar Proxima como segunda capa M | Proxima b combina una geometría LIFE favorable con una SED MUSCLES pública; la rama se etiqueta como análogo terrestre bajo el entorno Proxima, no como atmósfera observada. | Planificado / bloqueado por fotoquímica |
| 2026-07-20 | Usar PT/Kzz terrestre controlado para el baseline Proxima | Aísla el efecto de sustituir la SED solar por la de Proxima; una sensibilidad climática requiere una campaña y evidencia distintas. | Cerrado para alcance inicial |
| 2026-07-20 | Separar el benchmark Tierra--Sol de junio de la matriz N2O corregida | Los perfiles A2/A3 aceptados usan `3.35e9`/`1.20e10`; los BC activos usan `3.416e9`/`1.238e10`. El benchmark puede validar interfaz LIFE, pero resultados científicos finales requieren rerun o rótulo histórico explícito. | Abierto: decisión antes de interpretación LIFE |
| 2026-07-20 | Diferir M8V a 5 pc, Teegarden y TRAPPIST-1e real | Siguen siendo preguntas alternativas de geometría/fotoquímica, no sustitutos de las dos capas aprobadas. | Activo / diferido |
| 2026-07-20 | Bloquear retrievals LIFE hasta validación | No lanzar retrievals sin interfaz, diagnóstico de señal/SNR y registro de campaña. | **Superada para la rama clásica** por la decisión 2026-07-25 de ejecutar una cota optimista con sigma diagonal; sigue vigente para claims instrumentales/finales basados en LIFEsimMC. |
| 2026-07-25 | **Anclar los tiempos de integración LIFE a la literatura** | Regímenes corto/razonable/extremo = **10 h / 240 h (~10 d) / 1200 h (50 d)**, tomados de LIFE X (S/N=170 en 10 h para Proxima b; criterio S/N=7 en <100 h), LIFE XII (~10 d para planeta templado alrededor de M a 5 pc; ~50--100 d para Tierra a 5 pc) y LIFE III (~7 semanas para R=50/S-N=10 en Tierra a 10 pc). Evita elegir tiempos arbitrarios. | **Cerrado** |
| 2026-07-25 | **Abrir la matriz de retrievals de emisión con sigma diagonal** | Con el diagnóstico de señal/SNR validado en ambas capas y el manifiesto registrado, se autorizó inicialmente una matriz de 14 retrievals usando sigma por bin de LIFEsim clásico, declarada como cota optimista hasta LIFEsimMC/PHRINGE. | **Cerrado 8/8**: matriz final Proxima A0--A3 × {10 h, 240 h}; PT Madhu + `Piette20` + prior de `R_p_ref` en metros. Solo A3 a 240 h mide N2O y excluye la referencia A0 efectiva a 3.14 sigma. |
| 2026-08-30 | **Clasificar los productos de 1200 h** | Fueron generados con la cadena clásica y documentan el diagnóstico de desajuste a S/N alto, pero no pertenecen a la matriz final 8/8. | **Evidencia de auditoría/piloto excluida**: conservar, no contar en resultados canónicos ni borrar como residuo. |
| 2026-08-30 | **Validar documentalmente la rama LIFEsim clásica** | La interfaz, forwards, contrafactuales, S/N y retrievals clásicos tienen evidencia suficiente para un benchmark reproducible con limitaciones. | **Cerrado con salvedades**: sigma diagonal, una semilla, sin covarianza instrumental ni comparación con/sin molécula. |
| 2026-08-30 | **Ajustar la legibilidad de las figuras Proxima de espectro/señal y SNR** | Títulos compactos, etiquetas moleculares sin guías verticales, rellenos claramente diferenciados, composición de tres paneles alineada al análogo de transmisión y límites de ejes ajustados a los datos separan mejor la información visual sin alterar los datos. | **Cerrado para la capa visual**; se regeneraron y verificaron los plots clásicos, y la comparación SNR/proyección quedó promovida en PNG/PDF. |
| 2026-08-30 | **Generar y refinar el atlas de retrieval LIFE Proxima** | Se usaron los productos existentes de espectro, muestras, perfiles VULCAN y bins LIFE de la matriz canónica. Las figuras espectrales interpolan las curvas a 250 puntos globales y 75 por zoom, y muestran A0/A3 con la semántica Retrieved/True/Observed alineada al código de transmisión. La matriz de perfiles usa histogramas, medianas discontinuas, perfiles sólidos, barras de incertidumbre y métricas por panel según la referencia de transmisión. Los envelopes continuos quedan en alpha 0.025/0.05 y las líneas espectrales se atenúan para priorizar las observaciones; los marcadores ampliados llevan un borde gris fino y se dibujan opacos, mientras las barras de error conservan su transparencia. | **Cerrado para revisión**; tres figuras en PNG/PDF bajo `outputs/life_proxima_b_earthlike_v1/plots/`, sin incluir A3--1200 h ni modificar los datos. |
| 2026-08-31 | **Usar una referencia A0 efectiva en el atlas de perfiles** | Para comparar el posterior isoquímico con el perfil vertical VULCAN sin escoger arbitrariamente la capa superficial, se añadió el promedio columnar ponderado en presión de A0 como referencia escalar reproducible. El atlas conserva el perfil VULCAN sólido y la mediana posterior discontinua de A3; las figuras espectrales mantienen A0/A3. | **Cerrado**; el código está en `retrieval_reference.py`, el CSV reporta `A0_effective` y la separación firmada, y el atlas muestra la distancia A3--A0 efectiva. |
| 2026-08-31 | **Simplificar el encabezado y las métricas del atlas de perfiles** | Se eliminó el texto explicativo redundante bajo el título y el `Delta log X` de los recuadros. La leyenda de perfil VULCAN A3, posterior A3 y referencia A0 efectiva queda horizontal bajo el título; la fórmula de `z` se muestra aparte y los recuadros conservan la mediana A3, el valor A0 de referencia y su distancia en sigma. | **Cerrado**; se mantuvieron las líneas sólido/discontinua/punteada y se alinearon los colores con `True`/`Retrieved` de los plots espectrales. |
| 2026-08-31 | **Priorizar las observaciones en el espectro global de retrieval** | Se retiró el grid de fondo del panel global y se aumentó el tamaño de sus marcadores observados, conservando los bins, barras de error y curvas de entrada. | **Cerrado**; cambio exclusivamente visual, regenerado en PNG/PDF. |
| 2026-08-31 | **Ajustar la escala final de los puntos observados y la fórmula de distancia** | Los marcadores con barras de error se ampliaron a 5.8 pt en el panel global y 6.2 pt en los zooms, con borde gris ligeramente reforzado. La fórmula de `z` se desplazó un poco hacia arriba y a la izquierda en el atlas de perfiles. | **Cerrado**; tres PNG/PDF oficiales regenerados y revisados visualmente, sin cambios en datos ni retrievals. |
| 2026-08-31 | **Ejecutar un piloto intermedio A3--500 h** | Comprobar la estabilidad de la configuración corregida entre 240 h y el piloto excluido de 1200 h sin alterar el índice ni la matriz canónica. Se usó WSL Ubuntu, conda `POSEIDON`, PT Madhu, `Piette20`, prior de `R_p_ref` en metros y 200 puntos vivos. | **Cerrado como auditoría**; MultiNest terminó normalmente (`43 893` evaluaciones, `chi^2_red = 1.59`, `R_p_ref = 1.23 R_E`). La ejecución inicial usó sigma escalada; la validación directa de LIFEsim 0.2.32 produjo un `.dat` idéntico, por lo que no se repitió MultiNest. Véanse `life_proxima_a3_500h_retrieval_audit_2026-08-31.md` y `life_proxima_a3_500h_lifesim_direct_validation_2026-08-31.md`. |
| 2026-08-31 | **Instalar LIFEsim y validar el cálculo directo A3--500 h** | El entorno WSL `POSEIDON` necesitaba LIFEsim y el SpectRes de fdannert para comprobar la procedencia del piloto. Se preservaron el índice canónico y el dataset anterior. | **Cerrado**; LIFEsim 0.2.32 + SpectRes 2.1.1 pasan la calibración LIFE X (166.5 vs 170 a 2 m). El archivo directo tiene 31 bins y coincide byte a byte con el dataset usado por el retrieval. Sigue siendo auditoría/piloto, no matriz canónica. |
| 2026-08-31 | **Comparar ruido directo de LIFEsim con el escalado temporal** | Se llamaron directamente las escenas Proxima A0/A3 en 1, 10, 100, 240, 500 y 1200 h y se compararon con `sigma(10 h)*sqrt(10 h/t)`, usando la misma realización normal emparejada. | **Cerrado como auditoría**; máxima diferencia relativa `6.7e-16` y máxima diferencia emparejada `8.5e-15 sigma`. El escalado reproduce el ruido clásico, pero no sustituye LIFEsimMC/PHRINGE ni prueba covarianza instrumental. Véase `docs/life_proxima_lifesim_noise_scaling_2026-08-31.md`. |
| 2026-08-31 | **Relanzar retrievals robustos Proxima A3 a 500 h y 1200 h** | Se usaron datasets directos de LIFEsim, el prior físico de `R_p_ref` en metros, `Piette20`, `Madhu`, `isochem` y `N_live=800`, manteniendo salidas separadas del índice y la matriz canónicos. | **Cerrado como auditoría/piloto, con salvedad de prior**; ambos runs terminaron con posterior completo: 500 h `ln Z=901.17`, `chi^2_red=2.07`, `R_p_ref=1.23 R_E`; 1200 h `ln Z=898.31`, `chi^2_red=2.82`, `R_p_ref=1.26 R_E`. `a1` queda cerca de su límite superior en ambos casos; falta prueba de sensibilidad con prior ampliado. No se usan para claims canónicos ni de detección. Véase `docs/life_proxima_a3_500h_1200h_robust_retrieval_2026-08-31.md`. |
| 2026-09-01 | **Probar un perfil vertical `two-gradients` para NH3 en A3--500 h** | Se reutilizó el dataset directo de LIFEsim y se mantuvieron PT `Madhu`, `Piette20` y el prior físico de radio. Sólo NH3 recibió `species_vert_gradient`; `N_live=1000` y salida separada `nh3twograd`. | **Cerrado como diagnóstico/auditoría excluida**; posterior completo con `ln Z=895.86`, `chi^2_red=3.15`, 18 parámetros y 16 001 muestras. La caída vertical tiene dirección compatible con VULCAN, pero la capa alta es ancha y el ajuste no mejora al isquímico robusto. Véase `docs/life_proxima_a3_500h_nh3_two_gradients_2026-09-01.md`. |

---

## 4. Tareas pendientes e incertidumbres

### Activo: Etapa 0 LPJmL

1. `[x]` Reactivar LPJmL con decisión explícita y fijar versión/commit.
2. `[x]` Compilar LPJmL `v6.0.6` y verificar el ejecutable local.
3. `[x]` Descargar, verificar por checksum y extraer el paquete estándar oficial.
4. `[x]` Correr y aceptar el piloto de una celda con ciclo de N activo y la
   rama de rendimiento potencial.
5. `[x]` Preparar instalación reproducible LPJmL/MPICH, auditoría del otro PC,
   smoke test MPI y runner global A1 por fases.
6. `[ ]` Ejecutar el benchmark global A1 actual y aceptar sus flujos de
   `N2O`/`NH3`.
7. `[ ]` Ejecutar la reproducción global moderna y comparar con los objetivos
   publicados de Franck et al. (2011).
8. `[ ]` Acoplar solo salidas globales aceptadas a los lower-boundary fluxes de
   la Etapa I, con unidades/metadatos auditados.

### Prioridad activa: validación de Etapa II

1. `[ ]` Generar múltiples realizaciones de ruido PandExo para medir tasas de
   falsos positivos y negativos en distinguibilidad de escenarios.
2. `[ ]` Ejecutar comparaciones de evidencia bayesiana con y sin opacidad de
   `N2O`/`NH3`; no presentar un posterior como detección sin ese análisis.
3. `[ ]` Mantener separados los productos de la campaña optimizada de 18
   corridas y la evidencia legacy de 42 corridas.

### Etapa III: rama clásica cerrada y rama instrumental pendiente

#### Completado — LIFEsim clásico

1. `[x]` Forward de emisión POSEIDON A0--A3 para Tierra--Sol y Proxima.
2. `[x]` Contrafactuales N2O/NH3 y moléculas de control.
3. `[x]` Escenas LIFEsim clásico, validaciones de unidades/cuerpo negro/LIFE X
   y tablas de S/N.
4. `[x]` Fotoquímica Proxima A0--A3 convergida, SED y conversión auditadas.
5. `[x]` Matriz canónica de retrievals Proxima A0--A3 × {10 h, 240 h}, 8/8.
6. `[x]` Clasificación de los productos 1200 h como pilotos de auditoría.
7. `[x]` Instalación de LIFEsim 0.2.32/SpectRes compatible y validación directa
   del dataset A3--500 h.
8. `[x]` Comparación directa frente a escalado `sqrt(t)` para el ruido clásico
   de LIFEsim en Proxima A0/A3.
9. `[x]` Retrievals robustos de auditoría A3 a 500 h y 1200 h con datasets
   directos de LIFEsim, `N_live=800` y configuración `Piette20`.
10. `[x]` Prueba diagnóstica de perfil `two-gradients` para NH3 en A3--500 h,
    con posterior completo y salida separada.

11. `[x]` Diagnósticos rápidos de Bayes factor A3/A0 y N2O A3/N2O reiniciado,
    calculados sobre el mismo dataset A3--240 h con plantillas fijas.

#### Pendiente — LIFEsimMC/PHRINGE y robustez inferencial

1. `[ ]` Congelar versión/commit, licencia, escena perturbada, semilla y
   configuración instrumental del piloto MC.
2. `[ ]` Validar el contrato de espectro custom y preservar SED/covarianza.
3. `[ ]` Implementar whitening reproducible o likelihood correlacionada.
4. `[ ]` Ejecutar al menos A0/A3 Proxima con varias realizaciones de ruido.
5. `[~]` Comparar evidencia de modelos con/sin N2O y, si procede, con/sin NH3.
   El diagnóstico de plantillas fijas A3/A0 y N2O reiniciado ya está cerrado;
   queda pendiente la evidencia marginalizada con parámetros nuisance y ruido
   instrumental/correlacionado.
6. `[ ]` Si se usan los retrievals A3 de 500/1200 h para inferencia cuantitativa,
   repetirlos con sensibilidad al prior ampliado de `a1`.
7. `[ ]` Decidir rerun Tierra--Sol con BC N2O corregidos o mantenerlo solo como
   benchmark histórico de interfaz.
8. `[ ]` Mantener M8V a 5 pc, Teegarden y TRAPPIST-1e real como alternativas
   posteriores sujetas a insumos y campañas separadas.
