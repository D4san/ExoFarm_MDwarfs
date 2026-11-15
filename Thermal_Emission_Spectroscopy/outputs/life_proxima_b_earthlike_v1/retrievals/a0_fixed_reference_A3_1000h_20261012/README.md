# A3–1000 h: tres restricciones A0 emparejadas con el completo activo

**Vigente 2026-10-13:** reanudación autorizada MPI5 desde los tres checkpoints
validados y respaldados. Supervisor5062, MPI5080/5090/5100, quince ranks
activos en carga inicial; restauración MultiNest por confirmar. Completo
cerrado exit0, pendiente auditoría. Usar estado/manifest centrales y logs
`recovery_20261013_MPI5_R1/`. El arranque MPI3 inferior queda como historial.
[Registro](../../../../../docs/life_proxima_a3_1000h_mpi5_resume_2026-10-13.md).

Autorización explícita 2026-10-12. Solo N₂O fija, NH₃ fija y ambas fijas.
Supervisor lanzado 23:04:42 UTC / 18:04:42 America/Bogota, PID 1139.
Estado RUNNING, preflight 3/3 PASS; usar `campaign_state.json` y `manifest.csv`.
MPI PID 1208/1238/1271, ranks 1219–1221 / 1249–1251 / 1282–1284.
Nuevas variantes en carga de opacidades; completo MPI805 continúa muestreando.
No implica finalización ni aceptación de productos.

MPI3 por variante, completo existente MPI6 intacto, quince ranks globales.
Dataset común SHA-256 `5611c5904ef03aa02586bed15f14c0c2560ac5ae6fa9463ef420229311db75fa`.
No se regeneran observaciones, no se omiten opacidades, no se alteran PT,
priors libres, N_live=800 o rejilla 3–20 μm a R=10000. Referencia escalar
A0 congelada en `a0_reference.json`; 15 dimensiones declaradas y 13/13/12 libres.

Fuentes: `selected_scope.json`, `campaign_state.json`, `manifest.csv`,
`preserved_inputs.json`, `preflight_validation.json`, `resolved/`, `logs/`,
`supervisor.log` y `supervisor.pid`. Scratch Linux separado:
`/home/dasan/exofarm_a0ref_A3_1000h_20261012/`.

Exit 0 no acredita aceptación. Pendiente auditoría independiente y tres ln B
frente al completo sobre este mismo dataset; sigma según convención bilateral
documentada. No comparar ln Z entre tiempos ni asignar sigma conjunta por especie.
No relanzar, duplicar, matar, cambiar ranks ni aceptar por automatismo.

[Procedimiento y límites](../../../../../docs/life_proxima_a3_1000h_a0_comparison_2026-10-12.md).
