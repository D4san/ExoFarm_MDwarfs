# Matriz LIFE Proxima A1/A3 con binning corregido: alcance y ejecución

**Inicio:** 2026-10-21 (America/Bogota)  
**Estado al crear esta nota:** campaña en preflight; la bitácora siguiente registra cortes históricos. **Cierre (2026-10-28):** 33/33 retrievals auditados y ledger conciliado; véase el [informe final con tablas](life_proxima_a1_a3_corrected_binning_matrix_results_2026-10-28.md).

## Pregunta y alcance

Se autorizó rehacer con el operador de binning fotónico corregido los casos necesarios para una matriz homogénea A1/A3 a 1, 10 y 100 h. Son **33 retrievals**:

- **A1:** tres modelos completos (1/10/100 h) y 18 ablaciones LOO: H₂O, CO₂, CH₄, O₃, N₂O y NH₃, cada especie retirada por separado para cada duración.
- **A3:** 12 ablaciones LOO de H₂O, CO₂, CH₄ y O₃ a 1/10/100 h.

Los completos A3 corregidos ya auditados y las ablaciones A3 de NH₃/N₂O ya auditadas son referencias preservadas; no se relanzan. Las tres corridas A3–100 h con abundancias A0 fijas son comparadores opcionales separados y no pertenecen a esta autorización. La ejecución no modifica la matriz canónica 8/8 ni recupera/reescribe campañas históricas.

## Diseño de ejecución

La campaña nueva, sin reusar checkpoints, se identifica como `proxima_A1_A3_corrected_bin_matrix_33_20261021_r01`. Su fuente de verdad es:

`Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a1_a3_corrected_binning_matrix_loo_20261021_r01/`

El scratch se mantiene separado en `/home/dasan/exofarm_a1_a3_corrected_binning_matrix_20261021_r01/`. Antes de muestrear se ejecutan los **33 preflights MPI4** y se valida cada configuración LOO contra su completo correspondiente. La cola limita concurrencia a tres retrievals MPI4 (12 ranks totales en una máquina de 16 CPU lógicas), reserva cuatro CPU lógicas para sistema/supervisión y empieza por los tres completos A1. Después ejecuta los LOO por olas; el orden y cada salida quedan en los manifiestos/logs.

Configuración congelada: POSEIDON de emisión directa, operador LIFE corrected-bin ligado durante likelihood/muestreo y postproceso, rejilla 3–20 μm, R=10 000, N_live=800, tolerancia de evidencia 0.5, perfil isochem, O₂, superficie negra fija a 1 bar y sin inflación de errores. Cada pareja comparte escenario, duración, dataset observado, semilla y priors de parámetros restantes; el LOO retira opacidad y coordenada de abundancia de una sola especie. Hashes, semillas, priors efectivos y configuración resuelta por caso están en el manifiesto/JSON de ejecución.

La inicialización verificó disponibilidad de 16 CPU lógicas, memoria, swap y espacio en discos de proyecto/scratch. El callback corrected-bin se contrastó con el flujo LIFE guardado para A1 y A3: 31 canales por caso y discrepancia relativa máxima de aproximadamente `2.3e-14`. Los tres completos A3 de referencia pasaron la puerta preliminar de productos; sus campañas de origen siguen siendo la fuente de aceptación independiente.

## Estado operativo

**Corte inicial del 21-oct:** el supervisor se lanzó, pasaron los 33 preflights MPI4 y wave 1 inició con los tres completos A1. Este estado era provisional y no describe la situación actual. La campaña terminó el 28-oct con exit 0; la auditoría independiente aprobó 33/33 y los tres completos A3 de referencia. Véanse el [manifiesto conciliado](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a1_a3_corrected_binning_matrix_loo_20261021_r01/manifest.csv) y el [informe final](life_proxima_a1_a3_corrected_binning_matrix_results_2026-10-28.md).

Mientras el supervisor escribe, una discrepancia parcial de serialización puede dejar campos de `campaign_state.json` rezagados respecto al manifiesto/logs. No editar ledgers durante la ejecución. Al cerrar, confirmar primero la salida del supervisor y reconciliar estados con manifiesto, logs, códigos de salida y productos.

## Auditoría y análisis al cierre

Para cada corrida se verificará `return_code=0`, posterior y pesos, espectro, perfil P–T, `log_X`, estadísticas MultiNest, finitud, hashes, priors, exclusión molecular, dataset y operador/binding. La aceptación exige productos auditados, no solo un código de salida exitoso.

Calcular `ΔlnZ = lnZ_completo − lnZ_sinX` únicamente con el modelo completo del mismo escenario, duración, dataset y semilla. Combinar errores numéricos en cuadratura; conservar ΔlnZ como evidencia primaria y cualquier sigma bilateral calibrada como auxiliar. Calcular `P(log10 X > A0)` solo desde un posterior que conserve X. No comparar lnZ entre duraciones ni realizaciones distintas. Separar preferencia entre modelos de dirección posterior de abundancia y no atribuir causalidad ExoFarm a estas comparaciones por sí solas.

**Cierre 2026-10-28:** la revisión de los 33 casos aprobó exit codes, posteriores/espectros/P–T/`log_X`/MultiNest, finitud, hashes, priors, exclusiones moleculares y binding corrected-bin. Se calcularon 30 contrastes LOO contra el completo homólogo, con errores en cuadratura; `σ_aux` queda como descriptor calibrado y `P(log10 X>A0)` solo se informa donde la especie sigue activa. README, ledgers, resumen, tracker e índice documental están actualizados. La solicitud de arranque concurrente rechazada queda registrada como incidente de protección, no como fallo de retrieval; se preservaron snapshots, corridas históricas y productos con binning anterior.
