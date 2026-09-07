# Reanudar ExoFarm: punto de entrada operativo

**Última actualización estructural:** 2026-09-06
**Uso:** leer este documento al iniciar una tarea nueva o un chat nuevo en este
repositorio. Resume el estado recuperable, la próxima acción autorizada y los
documentos que contienen el detalle. No sustituye la verificación en vivo de
procesos, entornos, archivos ni `git status`.

## Lectura mínima, en este orden

1. [`../AGENTS.md`](../AGENTS.md): reglas científicas, de seguridad, rutas y
   requisitos de verificación.
2. Este documento: alcance activo y siguiente paso.
3. [`project_status_tracker.md`](project_status_tracker.md): backlog, decisiones
   y estado por etapa.
4. El README de la etapa afectada y, si se va a ejecutar software, su documento
   de entorno correspondiente.

Los informes fechados en `docs/` son evidencia y contexto; no se deben usar
aisladamente como estado operativo actual. Ante discrepancia, comprobar los
archivos/outputs en vivo y actualizar el tracker y este documento.

## Estado recuperable en un minuto

| Etapa | Estado | Regla de reanudación |
| --- | --- | --- |
| 0 — LPJmL | **Piloto aceptado; campaña global A1/MPI preparada para otro PC** | LPJmL `v6.0.6` y las entradas oficiales están fijados. El paquete portátil instala MPI, audita el equipo, ejecuta un smoke test y separa spin-up/A1. Todavía no existen flujos globales; no acoplar el piloto a VULCAN. |
| I — VULCAN Tierra--Sol | **Aceptada, benchmark pre-corrección de N2O** | Los cuatro A0--A3 tienen `end_case = 1`, pero A2/A3 proceden del conjunto guardado el 2026-06-15, anterior a la corrección actual de N2O. Sirven para validar la interfaz LIFE, no para presentar todavía la matriz vigente como resultado final. |
| I — VULCAN TRAPPIST-1e | **Aceptada con salvedad** | `end_case = 3` por química traza; conservar la salvedad en cualquier uso de esos productos. No usar esos perfiles para Proxima. |
| II — transmisión/JWST | **Campaña A0/A3 cerrada** | La matriz optimizada de 18 retrievals es la evidencia vigente. Los perfiles TRAPPIST actuales se regeneraron junto con los BC corregidos en `fb9812d`; no confundir esta campaña con la salvedad Tierra--Sol de Stage III ni reabrir una cola sin verificar outputs y procesos en vivo. |
| III — LIFE | **Rama LIFEsim clásica validada; matriz de retrievals 8/8 cerrada** | Tierra--Sol y Proxima tienen forwards, contrafactuales y S/N clásico. Proxima A0--A3 × {10 h, 240 h} tiene retrievals completos: solo A3 a 240 h mide N2O y excluye la referencia preagrícola efectiva a 3.14 sigma; A1/A2 son límites superiores y NH3 no discrimina. Los retrievals robustos adicionales A3 a 500 h y 1200 h son auditoría excluida. **Próximo:** LIFEsimMC/PHRINGE con inestabilidad instrumental, covarianza, múltiples semillas y modelos con/sin molécula. Véase la [validación consolidada](lifesim_classic_stage_iii_validation_2026-08-30.md). |

## Próximo trabajo autorizado

### Etapa 0 — primera prueba Franck 2011 + N2O/NH3

La prueba acotada quedó aceptada el 2026-09-06. El checkout oficial está fijado
en LPJmL `v6.0.6`, commit
`5af44a1ed023279a23c28d6dfe76945b97aaac57`; la compilación serial pasó, el
paquete estándar fue verificado y extraído, y `pilot_20260907T031220Z` completó
el spin-up, A1 con ciclo de N y la rama de rendimiento potencial. Los NetCDF
1996--2005 tienen dimensiones/unidades plausibles y valores finitos. La
siguiente acción científica es trasladar el repositorio y el archivo de entrada
al PC de ejecución, pasar el smoke test MPI y ejecutar las fases globales
`spinup` y `a1`. La estrategia quedó fijada en el
[runbook para el otro PC](lpjml_global_a1_mpi_other_pc_runbook.md); la celda
piloto no produce un flujo planetario interpretable. Véanse también el
[informe de aceptación](lpjml_franck2011_first_pilot_2026-09-06.md) y
[`../Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction/README.md`](../Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction/README.md).

### Rama clásica — cerrada y preservada

Las dos capas ya completaron la cadena POSEIDON emisión → LIFEsim clásico →
S/N. La Capa 2 añadió ocho retrievals canónicos Proxima A0--A3 × {10 h,
240 h}. No reabrir o ampliar esa matriz sin una nueva pregunta científica.

- `life_earth_sun_10pc_interface_v1` conserva el rótulo
  `earth_20260615_pre_n2o_correction`; sirve como benchmark de interfaz, no como
  matriz Tierra--Sol vigente.
- `life_proxima_b_earthlike_v1` es un análogo terrestre bajo la SED de Proxima,
  no la atmósfera medida de Proxima b.
- Los datasets de 1200 h y el retrieval A3--1200 h se preservan como evidencia
  de auditoría/piloto y quedan fuera del cierre 8/8.
- El 2026-08-31 se ejecutó un piloto intermedio A3--500 h con la configuración
  corregida de POSEIDON. Terminó con `ln Z = 893.18 +/- 0.40`,
  `chi^2_red = 1.59` y `R_p_ref = 1.23 R_E`; queda como evidencia de
  auditoría, no amplía la matriz canónica ni el atlas oficial. La corrida se
  lanzó inicialmente con el escalado validado de sigma desde 10 h; después se
  instaló LIFEsim 0.2.32 en el WSL `POSEIDON` y la observación directa de 500 h
  produjo un archivo idéntico byte a byte al usado por ese piloto histórico.
  El posterior robusto se relanzó por separado con `N_live=800`, el dataset
  directo y la configuración actual de `Piette20`; ambos productos deben
  mantenerse distinguidos. Véase la [validación directa](life_proxima_a3_500h_lifesim_direct_validation_2026-08-31.md).
- El 2026-08-31 se completaron retrievals robustos independientes de A3 a 500 h
  y 1200 h con datasets directos de LIFEsim. Dieron, respectivamente,
  `ln Z = 901.17 +/- 0.22`, `chi^2_red = 2.07` y
  `ln Z = 898.31 +/- 0.22`, `chi^2_red = 2.82`, con radios
  `1.23 R_E` y `1.26 R_E`. El intento viejo de 1200 h queda como evidencia del
  fallo numérico anterior; los nuevos productos son auditoría/piloto y no
  alteran la matriz canónica. `a1` queda cerca del límite superior del prior en
  ambos posteriores, por lo que todavía falta una prueba de sensibilidad a
  priors antes de usarlos como inferencia final. Véase el [informe del retrieval
  robusto](life_proxima_a3_500h_1200h_robust_retrieval_2026-08-31.md).
- El 2026-09-01 se ejecutó un diagnóstico adicional A3--500 h con
  `X_profile=two-gradients` sólo para `NH3`, `N_live=1000` y el mismo dataset
  directo. Terminó con `ln Z = 895.86 +/- 0.17`, `chi^2_red = 3.15` y 18
  parámetros; la mediana recupera la dirección de la caída vertical, pero la
  capa alta queda débilmente constreñida y el ajuste no mejora al retrieval
  isquímico (`ln Z = 901.17`, `chi^2_red = 2.07`). Es auditoría excluida y no
  reemplaza el resultado de referencia. Véase la [prueba de perfil vertical
  NH3](life_proxima_a3_500h_nh3_two_gradients_2026-09-01.md).
- El 2026-09-01 se calcularon dos diagnósticos rápidos de Bayes factor sobre el
  mismo dataset Proxima A3--240 h: A3 frente a A0 (`ln B=394.35`) y A3 frente
  al contrafactual con N2O reiniciado a A0 (`ln B=385.63`). Son likelihoods de
  plantillas fijas, con una sola realización y sigma diagonal; quedan como
  experimento de auditoría y no sustituyen la evidencia marginalizada ni la
  validación LIFEsimMC/PHRINGE. Véase el [informe de diagnósticos bayesianos
  rápidos](life_proxima_bayes_factor_diagnostics_2026-09-01.md).
- Las figuras Proxima de espectro y señal se actualizaron el 2026-08-30 solo en
  presentación: títulos compactos, etiquetas moleculares sin guías verticales
  y rellenos claramente diferenciados. La comparación SNR/proyección se ajustó
  al intervalo útil de 1--1000 h y a los puntos representados, y quedó promovida
  en PNG/PDF a `Thermal_Emission_Spectroscopy/final_products/figures/`. La
  figura conjunta sigue la composición de tres paneles del análogo de
  transmisión, sin cambiar el observable `F_p`, los datos ni la interpretación.
- El ensayo directo de ruido de LIFEsim del 2026-08-31 comparó A0/A3 en
  1--1200 h contra `sigma(10 h)*sqrt(10 h/t)`. La máxima diferencia relativa
  fue `6.7e-16` y la diferencia de una realización emparejada fue menor que
  `8.6e-15 sigma`: el escalado reproduce la llamada directa para LIFEsim
  clásico. Esto no prueba ruido correlacionado ni inestabilidad instrumental;
  el siguiente salto sigue siendo LIFEsimMC/PHRINGE.
- El atlas de retrieval LIFE Proxima se regeneró a partir de los ocho productos
  canónicos A0--A3 x {10 h, 240 h}. Las figuras de espectro global y ventanas
  moleculares comparan solo A0/A3; la figura de perfiles/posteriores se centra
  en A3 y muestra su perfil VULCAN y posterior frente a una referencia A0
  efectiva, calculada como promedio columnar ponderado en presión. Las curvas
  espectrales se interpolan a 250 puntos globales y 75 puntos por zoom
  únicamente para presentación, con la semántica visual Retrieved/True/Observed
  alineada al código de transmisión. La matriz de perfiles conserva la lógica
  de transmisión: perfil químico sólido, mediana posterior discontinua, línea
  A0 efectiva punteada, leyenda horizontal bajo el título, fórmula de la
  distancia firmada aparte y recuadros reducidos a la mediana A3 y su distancia
  en sigma junto al valor A0 de referencia. El panel global quedó sin grid y
  con marcadores observados ampliados a 5.8 pt, y los zooms a 6.2 pt. Quedó en
  `outputs/life_proxima_b_earthlike_v1/plots/` para revisión; el piloto
  A3--1200 h no se incorporó.

### Rama instrumental — siguiente frontera

El próximo trabajo científico autorizado es construir un piloto mínimo de
**LIFEsimMC/PHRINGE** sobre espectros ya validados, sin reinterpretar primero la
rama clásica:

1. congelar versión/commit, licencia, escena, perturbaciones, tiempo y semilla;
2. validar la interfaz de espectro custom y las unidades;
3. preservar SED extraído y covarianza completa;
4. definir whitening reproducible o likelihood correlacionada;
5. repetir al menos A0/A3 Proxima en varias realizaciones de ruido;
6. comparar modelos con/sin N2O y, si la señal lo justifica, con/sin NH3.

En paralelo sigue abierta la decisión sobre rerun Tierra--Sol con las
condiciones de frontera de N2O corregidas. No presentar el benchmark de junio
como matriz actual mientras esa decisión permanezca abierta.

## Límites que no se pueden olvidar

- Stage III usa emisión térmica; no mezclar profundidades de tránsito, archivos
  PandExo, conteos de tránsitos ni `Transmission_Spectroscopy/notebooks/POSEIDON_output/`.
- LIFEsimMC puede entregar covarianza. No reducirla silenciosamente a errores
  diagonales: usar whitening reproducible o likelihood consciente de
  covarianza.
- SNR es un diagnóstico, no una detección. Las afirmaciones de detección esperan
  retrievals, modelos comparados y varias realizaciones de ruido.
- Los `.vul` permanecen en `Photochemical_Modeling/Results/Outputs/`; Stage III
  guarda sus productos únicamente bajo
  `Thermal_Emission_Spectroscopy/outputs/<campaign-id>/`.

## Cómo recuperar el trabajo de forma segura

1. Ejecutar `git status --short` y no sobrescribir cambios ajenos. La presencia
   de productos o documentación no implica que una simulación esté validada.
2. Confirmar la etapa y el ID de campaña contra el tracker y este documento.
3. Para Stage III, comprobar el entorno WSL en vivo. La ejecución de
   2026-08-31 verificó Ubuntu, el entorno conda `POSEIDON` en
   `/home/wsldasan/miniconda3/envs/POSEIDON` y los inputs
   `/home/wsldasan/POSEIDON/inputs` y
   `/home/wsldasan/POSEIDON/inputs/stellar_grids`; la ruta y las dependencias
   deben volver a verificarse antes de ejecutar.
4. Antes de una corrida costosa, comprobar que existe el manifiesto de campaña,
   que las unidades están escritas, que las entradas coinciden con la campaña y
   que el manifiesto distingue `earth_20260615_pre_n2o_correction` de los BC
   vigentes.
5. Después de una decisión, ejecución o validación material, actualizar:
   - `docs/project_status_tracker.md`;
   - este archivo `docs/project_resume.md`;
   - `experiments/README.md`;
   - el README de la etapa y un informe en `docs/` cuando cambie el argumento
     científico o la interfaz.

## Mapa de documentación

| Necesidad | Fuente canónica |
| --- | --- |
| Reglas para agentes y guardrails | [`../AGENTS.md`](../AGENTS.md) |
| Estado, backlog y decisiones | [`project_status_tracker.md`](project_status_tracker.md) |
| Etapa I y contrato de VULCAN | [`photochemical_profiles_methodology.md`](photochemical_profiles_methodology.md) |
| Inventario/entorno de transmisión | [`transmission_spectroscopy_inventory_2026-06-16.md`](transmission_spectroscopy_inventory_2026-06-16.md) |
| Diseño general Stage III | [`life_lifesim_stage_iii_plan.md`](life_lifesim_stage_iii_plan.md) |
| Flujo concreto de dos capas | [`life_stage_iii_two_layer_workplan_2026-07-20.md`](life_stage_iii_two_layer_workplan_2026-07-20.md) |
| Metodología completa de Stage III clásico | [`life_stage_iii_classic_methodology_2026-08-30.md`](life_stage_iii_classic_methodology_2026-08-30.md) |
| Informe integrado Stage III: metodología, resultados, tablas y plots | [`life_stage_iii_integrated_methodology_results_2026-08-30.md`](life_stage_iii_integrated_methodology_results_2026-08-30.md) |
| Validación y resultado de LIFEsim clásico | [`lifesim_classic_stage_iii_validation_2026-08-30.md`](lifesim_classic_stage_iii_validation_2026-08-30.md) |
| Auditoría del retrieval Proxima A3--500 h | [`life_proxima_a3_500h_retrieval_audit_2026-08-31.md`](life_proxima_a3_500h_retrieval_audit_2026-08-31.md) |
| Validación directa LIFEsim Proxima A3--500 h | [`life_proxima_a3_500h_lifesim_direct_validation_2026-08-31.md`](life_proxima_a3_500h_lifesim_direct_validation_2026-08-31.md) |
| Ensayo de ruido directo frente a escalado temporal | [`life_proxima_lifesim_noise_scaling_2026-08-31.md`](life_proxima_lifesim_noise_scaling_2026-08-31.md) |
| Retrieval robusto Proxima A3--500/1200 h | [`life_proxima_a3_500h_1200h_robust_retrieval_2026-08-31.md`](life_proxima_a3_500h_1200h_robust_retrieval_2026-08-31.md) |
| Prueba de perfil vertical NH3 A3--500 h | [`life_proxima_a3_500h_nh3_two_gradients_2026-09-01.md`](life_proxima_a3_500h_nh3_two_gradients_2026-09-01.md) |
| Diagnósticos de Bayes factor Proxima A3--240 h | [`life_proxima_bayes_factor_diagnostics_2026-09-01.md`](life_proxima_bayes_factor_diagnostics_2026-09-01.md) |
| Procedencia N2O de perfiles Tierra--Sol | [`earth_sun_n2o_matrix_provenance_2026-07-20.md`](earth_sun_n2o_matrix_provenance_2026-07-20.md) |
| Selección Tierra--Sol/Proxima | [`life_target_selection_2026-07-20.md`](life_target_selection_2026-07-20.md) |
| Ubicación de productos | [`repository_structure.md`](repository_structure.md) |
