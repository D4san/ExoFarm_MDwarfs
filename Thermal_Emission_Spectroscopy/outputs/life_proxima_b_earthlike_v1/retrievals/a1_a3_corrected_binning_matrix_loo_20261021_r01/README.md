# A1/A3 corrected-bin homologous LIFE retrieval matrix

**Estado: `COMPLETE_VALIDATED` (2026-10-28).** Los 33 retrievals nuevos terminaron con `return_code=0` y pasaron auditoría independiente: 21 A1 (tres completos y 18 LOO) y 12 LOO A3. Los tres completos A3 de campañas anteriores se usaron como referencias y también pasaron revisión; no se relanzaron.

Los 33 preflights MPI4 pasaron. La cola respetó el máximo de tres retrievals MPI4 (12 ranks totales); el supervisor de recuperación intento 2 terminó con exit 0 a `2026-10-28T20:13:03Z`, sin procesos activos ni violaciones de recursos. Se verificaron hashes de datos, priors/dimensiones emparejados, exclusión molecular, callback corrected-bin ligado a likelihood y postproceso, productos finitos, posterior POSEIDON igual a MultiNest equal-weight, espectros, P–T, `log_X`, evidencias y contadores.

La reconciliación final dejó las 33 entradas como `complete_validated`. Se conservan `recovery_20261027_power_restore_r01/manifest.before.csv`, `campaign_state.before.json`, checkpoints y logs. Una solicitud de inicio concurrente fue rechazada con `[RECOVERY_ERROR] RuntimeError: Prior recovery supervisor 473 is still alive`; la instancia existente siguió y concluyó correctamente, sin duplicar retrievals.

Las comparaciones LOO usan solo el completo del mismo escenario, duración y dataset. `ΔlnZ = lnZ_completo − lnZ_sinX`; errores en cuadratura; sigma bilateral calibrado auxiliar. Véanse el [informe final](../../../../../docs/life_proxima_a1_a3_corrected_binning_matrix_results_2026-10-28.md), las [tablas de modelos](../../../../../docs/life_proxima_a1_a3_corrected_binning_matrix_models_2026-10-28.csv) y [contrastes](../../../../../docs/life_proxima_a1_a3_corrected_binning_matrix_loo_2026-10-28.csv), y el [resumen de auditoría](../../../../../docs/life_proxima_a1_a3_corrected_binning_matrix_audit_2026-10-28.json).

Se preservan las campañas históricas, referencias A3 y productos con binning anterior. La comparación metodológica entre operadores no es un factor de Bayes molecular ni atribuye causalidad a ExoFarm.

Scratch: `/home/dasan/exofarm_a1_a3_corrected_binning_matrix_20261021_r01/`.
