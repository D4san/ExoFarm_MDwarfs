# LIFE Proxima A3–100 h — binning corregido

**Disposición final:** `STOPPED_BY_USER_MPI14_REBALANCE` el 2026-10-18; `return_code=-15`. Esta corrida serial fue detenida por solicitud del usuario y quedó sustituida por la [continuación MPI14 validada](../a3_100h_binning_corrected_mpi14_resume_20261018/README.md). No es un trabajo activo ni el resultado vigente.

### Estado observado al iniciar el intento (snapshot histórico)

En el lanzamiento, la corrida completa fresca había pasado el preflight, iniciado MultiNest con 800 puntos vivos y aún no tenía contador final de reemplazos. Se conserva la misma realización observada de 100 h (31 canales, SHA-256 `78662546181a5b74391a14b7b73ae80d879200a74db6a4bc5338e3ce7eee4705`). No se reutilizó checkpoint alguno.

- `selected_scope.json`: alcance autorizado y comparación.
- `campaign_state.json`, `manifest.csv`: estado y corrida.
- `operator_preflight.json`: binding del callback, cierre del forward y hash del dataset.
- `resolved_configuration.json`: configuración de muestreo resuelta.
- `preflight.log`, `retrieval.log`: logs del gate y de MultiNest.
- `preserved_inputs.json`: hashes de los inputs congelados.
- `products/`: se poblará solo al completar sin error; estado de validación separado.

El scratch vivo queda en `/home/dasan/exofarm_a3_100h_binning_corrected_20261017/`. El supervisor y el PID se registran en el directorio `retrievals` padre, con prefijo `a3_100h_binning_corrected_20261017`. No se debe reanudar con un checkpoint de la ejecución histórica.

La corrida anterior usó una rejilla POSEIDON de 3.8–19 μm; esta usa 3–20 μm. El preflight midió los bordes en 3.9974–18.5768 μm, dentro de ambos intervalos; la ampliación sigue el contrato de la rejilla corregida, aunque no era necesaria para cubrir estos bordes. La discretización nativa cambia. La comparación final debe consignarlo y auditar priors, callback, productos, hashes y finitud antes de interpretar posteriores o `ln Z`.
