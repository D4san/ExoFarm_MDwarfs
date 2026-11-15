# A3–1000 h: intento con rejilla nativa — 2026-10-11

**Estado posterior vigente — R1, 2026-10-12:** interrupción confirmada y
reanudación autorizada desde 2 646 212 evaluaciones / 51 200 reemplazos,
con 800 puntos vivos validados. Respaldo de los ocho archivos MultiNest
verificado por hash; registros interrumpidos conservados en
`recovery_20261012_R1/`. R1 RUNNING desde 17:25:14 COT, supervisor 803,
mpiexec 805 y seis ranks 820–825 en inicialización. Log nuevo:
`recovery_20261012_R1/retrieval.log`; `campaign_state.json` sigue central.
[Informe R1](../../../../../../docs/life_proxima_a3_1000h_checkpoint_resume_2026-10-12.md).

**Historial del arranque inicial, 19:42:38 UTC / 14:42:38 COT**: preflight PASS con RMS=máximo=0 σ,
supervisor 818, mpiexec 921 y seis ranks 932–937 activos en inicialización.
29 hashes protegidos intactos; intento de duplicación rechazado. Esta es una
constancia de arranque, no de finalización ni de aceptación científica.

Único retrieval completo autorizado, MPI6 / N_live=800, Madhu/isochem,
O₂, superficie negra fija en 1 bar, sin inflación ni x_tol. Hay 15
coordenadas declaradas y 14 libres, con priors oficiales de A3–100 h.

La rejilla de cálculo coincide con el generador: 3–20 μm, R=10000,
18 971 puntos. Los 31 canales de observación, el dataset y la realización
de ruido quedan intactos. Se conserva el primer preflight fallido en el
directorio padre: no hubo un muestreo anterior de 1000 h. El control nativo
reproduce exactamente el forward guardado y permite corregir el muestreo
numérico sin cambiar PT/química ni relajar los umbrales de validación.

Fuente de verdad: `campaign_state.json`, `manifest.csv`,
`resolved_configuration.json`, `baseline_configuration_comparison.json`,
`preserved_inputs.json`, `preflight.log` y `retrieval.log` cuando exista.
La comparación de configuración se escribe únicamente al pasar el preflight.
Dataset SHA-256:
`5611c5904ef03aa02586bed15f14c0c2560ac5ae6fa9463ef420229311db75fa`.
Semilla derivada 1450560596. Scratch:
`/home/dasan/exofarm_a3_1000h_20261011_nativegrid/`.

El supervisor separado usa el prefijo
`a3_1000h_full_20261011.nativegrid.supervisor` en `retrievals/`.
No duplicar ni reanudar por automatismo. Exit 0 permite archivar `products/`,
pero la aceptación requiere una auditoría posterior independiente.

[Procedimiento, decisiones e interpretación](../../../../../../docs/life_proxima_a3_1000h_extension_2026-10-11.md).
