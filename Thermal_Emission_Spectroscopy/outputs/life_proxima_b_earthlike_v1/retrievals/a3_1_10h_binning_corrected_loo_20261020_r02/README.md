# A3 1 h y 10 h: retrievals con bineado corregido

**Disposición final:** `HALTED_PREFLIGHT_FAILURE`. El preflight MPI5 del primer modelo completo A3–1 h falló con `RuntimeError: MPI5 setup-only preflight failed (exit 1)`; no se inició ningún sampler y las demás entradas quedaron pendientes. Esta tentativa fue sustituida por [r03, que completó y validó los seis retrievals](../a3_1_10h_binning_corrected_loo_20261020_r03/README.md). Se conservan aquí los manifiestos, configuraciones y estado originales como historial de auditoría.

### Alcance descrito al preparar el intento (snapshot histórico)

La campaña se preparó para comparar, a cada exposición, el modelo completo con las ablaciones sin NH3 y sin N2O. El plan inicial describía tres MPI5 en paralelo y una tanda de 1 h seguida por la de 10 h; el fallo de preflight impidió iniciar ese plan. No reutilizaba checkpoints ni modificaba datasets históricos.

El plan inicial congelaba la realización LIFE de cada duración por SHA-256 y enlazaba el callback de likelihood al operador corregido durante muestreo y postproceso. La comparación prevista calculaba cada ΔlnZ frente al modelo completo nuevo de la misma duración. El resultado final de este intento es el fallo de preflight indicado arriba; el estado y el manifiesto preservan el detalle de cada entrada.
