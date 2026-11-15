# Contrastes LIFE Proxima frente a A0 efectiva

**Auditoría 2026-10-11:** 3 complete / 0 running / 0 pending / 0 failed,
con exit 0. La conjunta finalizó 16:35:01 UTC (11:35:01 COT);
supervisor/MPI inactivos. Productos primarios, valores fijos, hashes, priors
y evidencias PASS. Finitud estricta FAIL: NaN en desviaciones derivadas de
coordenadas fijas en stats/summary de N₂O y conjunta. Auditoría
`ACCEPTED_WITH_FIXED_MOMENT_SALVEDAD` por autorización explícita del usuario;
campaña `VALIDATED_COMPLETE_WITH_SALVEDAD`. NH₃ individual pasa sin NaN.
No relanzar ni modificar originales: la finitud estricta sigue false y la
salvedad queda ligada a los hashes de la revisión anterior.

[Auditoría y hashes](validation_report_20261011.json) ·
[informe e incidencia exacta](../../../../../docs/life_proxima_a3_100h_a0_fixed_audit_2026-10-11.md) ·
[CSV final de tres filas](../../../../final_products/tables/life_proxima_a0_lnB_sigma_lin_2026-10-11.csv) ·
[JSON aceptado](../../../../final_products/tables/life_proxima_a0_lnB_sigma_lin_2026-10-11.json).
[Decisión de aceptación](acceptance_decision_20261011.json),
[auditoría anterior preservada](validation_report_20261011_pre_acceptance.json),
[momentos fijos estables CSV](fixed_parameter_moments_stable_20261011.csv) y
[JSON](fixed_parameter_moments_stable_20261011.json). Siete coordenadas fijas
con dispersión cero ponderada/de igual peso; 52 hashes científicos intactos,
13 controles PASS. Tablas provisionales conservadas sin cambios de cifras.
[Síntesis completa y conclusión ExoFarm/LIFE](../../../../../docs/life_proxima_exofarm_retrieval_layers_synthesis_2026-10-11.md).
ln B ± error numérico: N₂O `29.440 ± 0.340`, NH₃ `1.170 ± 0.342`,
conjunta `31.103 ± 0.336`; sigma bilateral `7.96 / 2.12 / 8.17`.

Estado 2026-10-10: **solo A3-100 h, tres hipótesis** (N₂O fija, NH₃ fija,
ambas fijas), seleccionado por el usuario y lanzado a las 19:05 COT.
Supervisor PID 758; MPI6 individuales PID 779/783 con seis ranks por uno,
conjunta en cola. Estos PID describen el arranque; verificar actividad actual.
Las otras 15 candidatas no están autorizadas ni en cola.
Fuente de verdad: `selected_scope.json`, `campaign_state.json`, `manifest.csv`.
Log/PID en `retrievals` padre: `a0_fixed_reference_20261010.A3_100h.supervisor`.

Preflight de prototipos: tres parejas A3-100 h PASS; fijas N₂O, NH₃ o ambas,
15 coordenadas declaradas y 13/13/12 libres. Contratos completos/restringidos
guardados en `resolved/`, logs en `preflight/`, progreso en
`preflight_progress.json`. Tres controles unitarios y compilación aprobados.

Procedimiento, interpretación, fórmulas, referencias y resultados:
[informe metodológico](../../../../../docs/life_proxima_a0_enrichment_methodology_2026-10-10.md).

`a0_reference.json` congela los promedios VULCAN y el checksum del perfil.
`campaign_plan.json`, `candidate_manifest.csv` y `configs/` preservan el plan
inicial de candidatas; no representan la cola efectiva. `resolved/` y `preflight/` conservan los
contratos completos y restringidos. El supervisor verifica igualdad de dataset,
opacidades y priors restantes. La cola seleccionada contiene exactamente tres
filas A3-100 h, todas con el mismo dataset oficial.

Monitor eliminado tras verificar el cierre; confirmación registrada en
[closure_record_20261011.json](closure_record_20261011.json).
ID `seguimiento-life-a0-a3-100h-3`; razón: tres productos, tabla, auditoría
y documentación cerrados con salvedad autorizada. No reiniciar automáticamente.

Supervisor: `Thermal_Emission_Spectroscopy/scripts/run_proxima_a0_reference_campaign.py`.
Scratch: `/home/dasan/exofarm_a0ref_20261010/runs/`.
Máximo dos MPI6, threads por rank = 1; N_live = 800, R = 10000.
Preservar configuraciones, scratch y logs ante fallo. No relanzar si existe un
estado; verificar checkpoints y procesos antes de una recuperación autorizada.
El exit 0 fue seguido por la auditoría independiente de productos y ln Z.

Se conservan los seis modelos completos oficiales, los 36 LOO terminados y
la matriz legacy 8/8. La restricción fija valores no nulos y mantiene las
opacidades de N₂O/NH₃; solo evalúa la referencia escalar elegida.
