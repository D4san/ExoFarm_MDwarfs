# A3–1000 h: un retrieval completo autorizado

Solo A3, 1000 horas (41.6667 días), full isochem/Madhu con la configuración
oficial y una nueva observación sintética independiente. No hay modelos LOO,
A0 fija, A1 ni cambio de P–T autorizados en esta campaña.

**Primer intento: FAILED en preflight, sin MPI ni MultiNest**, por diferencia
de muestreo espectral 0.7963 σ RMS / 2.545 σ máximo. El diagnóstico en la
rejilla nativa produce diferencia cero; registros/scratch quedan íntegros.
El intento corregido está en `native_grid_retry/`: rejilla numérica 3–20 μm,
R=10000, mismos canales, dataset, modelo físico y priors. No se relajan umbrales.

Fuente de verdad del intento corregido: `native_grid_retry/campaign_state.json`,
`native_grid_retry/manifest.csv`, `native_grid_retry/resolved_configuration.json`
y `native_grid_retry/baseline_configuration_comparison.json`.
Fuente del primer intento: `campaign_state.json`, `manifest.csv`,
`resolved_configuration.json`, `preserved_inputs.json` y los logs locales.
Los productos de exit 0 se archivan en `products/` y requieren auditoría
independiente antes de aceptación. Scratch y productos previos intactos.

[Procedimiento y alcance](../../../../../docs/life_proxima_a3_1000h_extension_2026-10-11.md).
