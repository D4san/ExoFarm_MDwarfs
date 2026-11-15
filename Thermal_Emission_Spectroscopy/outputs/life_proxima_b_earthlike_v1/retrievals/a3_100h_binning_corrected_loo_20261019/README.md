# A3–100 h: ablaciones moleculares con binning corregido

**Estado: COMPLETE_VALIDATED; auditoría independiente PASS (2026-10-20).** Campaña iniciada el 2026-10-19 y concluida con ambas variantes en `return_code=0`. Esta carpeta conserva manifiesto, configuraciones, evidencias del operador, logs, productos y tablas de auditoría. El scratch original fue `/home/dasan/exofarm_a3_100h_binning_corrected_loo_20261019/`.

## Alcance congelado

Se comparan dos modelos con la misma realización LIFE Proxima A3–100 h y el mismo retrieval completo de binning corregido:

| Caso | Modelo sin especie | Ranks | Estado |
|---|---|---:|---|
| `A3_100h_no_NH3` | Se retiran el parámetro `log_NH3` y su opacidad | 8 | VALIDATED; 42 008 reemplazos; 1 248 394 evaluaciones |
| `A3_100h_no_N2O` | Se retiran el parámetro `log_N2O` y su opacidad | 7 | VALIDATED; 42 995 reemplazos; 1 023 289 evaluaciones |

La suma es 15 ranks MPI, un hilo de BLAS/OMP por rank; no se reutiliza checkpoint. Cada modelo declara 14 parámetros, de los cuales 13 son libres porque `log_P_surf` permanece fijado en 1 bar. Los demás priors se heredan del completo corregido, incluida la misma verosimilitud Gaussiana diagonal y la misma tabla observada.

Configuración común: `N_live=800`, `ev_tol=0.5`, `R=10000`, rejilla nativa 3–20 μm, perfil P–T Madhu, química isochem, O2 incluido, superficie negra explícita a 1 bar, sin inflación `x_tol`. Dataset `life_data/LIFE_proxima_A3_100h.dat`, SHA-256 `78662546181a5b74391a14b7b73ae80d879200a74db6a4bc5338e3ce7eee4705`, 31 canales, semilla de generación 129315834.

## Binning y preflight

El adaptador `scripts/run_life_retrieval_a3_100h_binning_corrected_loo.py` enlaza `LifePhotonOperator` con el callback real de POSEIDON durante muestreo y postproceso. El operador integra fotones mediante solapamiento con celdas de bordes/puntos medios y convierte a energía en el centro exacto de cada canal. En ambos preflight se verificó el callback activo, 31 canales, tamaño MPI real (8 y 7) y cierre frente al producto binned guardado con error relativo máximo `2.2649e-14`. Las dos configuraciones resueltas tienen 14 parámetros declarados/13 libres y priors compartidos idénticos al completo, salvo que desaparece la especie excluida.

## Cierre y validación

La auditoría independiente del 2026-10-20 pasó para el baseline completo y las dos ablaciones. Revisó posterior contra `-post_equal_weights.dat`, espectro, PT, `log_X`, tablas MultiNest, finitud, hashes, priors, coordenadas fijas y callback del operador corregido. El ledger quedó en `COMPLETE_VALIDATED`, con `active_run_ids=[]`; ambos logs incluyen finalización y cierre de postprocesamiento.

El controlador guardó 6380 filas para sin NH3 y 6822 para sin N2O, una fila menos que `samples.txt` y las muestras de peso igual de MultiNest. Se preservaron los contadores iniciales y se reconciliaron los totales finales a 6381 y 6823, que coinciden entre productos.

La consulta independiente del árbol Linux de procesos no estuvo disponible desde esta sesión Windows; el cierre se sustenta en el ledger, logs, códigos de salida y productos.

### Registro operativo durante la ejecución

- Supervisor: PID Linux `872`, registrado en `supervisor.runtime.pid`; log operativo `supervisor_run_02.log`.
- Primer intento de invocación: falló antes de ejecutar Python, al pasar el comando de inicio del shell; no creó estado, preflight ni sampler. Se conservan el `supervisor.log` vacío y el `supervisor.pid` 457, que corresponde al wrapper fallido, no al supervisor. El arranque efectivo creó esta campaña y guardó el PID real en `supervisor.runtime.pid`.
- Ambos preflight: PASS el 2026-10-19 alrededor de 16:37 UTC.
- Samplers: `mpiexec -n 8` para `no_NH3` y `mpiexec -n 7` para `no_N2O`; 15 procesos rank observados activos a 16:38 UTC. Supervisor sin reintentos automáticos.
- Primera lectura de recursos: 16 CPUs visibles, 27.9 GiB de RAM disponible, 8 GiB de swap libre; sin presión de swap. Los contadores MultiNest aún no estaban inicializados en esa primera lectura.
- Estado final `COMPLETE_VALIDATED`; `campaign_state.json` y `manifest.csv` conservan la reconciliación y el historial de la campaña.

## Productos validados

Los productos por modelo, los logs, los JSON del operador/configuración y las tablas nativas de MultiNest permanecen preservados. La auditoría verificó posterior, espectro, perfil P–T, `log_X`, estadísticas y tablas MultiNest, finitud, hashes, priors compartidos, operador enlazado y ausencia efectiva de la molécula excluida.

El contraste principal, calculado tras esa validación, es:

`ΔlnZ_X = lnZ_completo_corregido − lnZ_sinX`.

| Ablación | ln Z sin X | Δ ln Z (error numérico) | Sigma auxiliar | χ² reducido |
|---|---:|---:|---:|---:|
| Sin NH3 | 891.582233 ± 0.240689 | +2.748991 ± 0.344630 | +2.853 | 4.06 (17 g.l.) |
| Sin N2O | 809.670715 ± 0.243406 | +84.660508 ± 0.346532 | +13.217 | 13.55 (17 g.l.) |

El baseline completo validado tiene `ln Z=894.331224 ± 0.246654` y `χ²_red=3.57` (16 g.l.). `ln B` es la métrica primaria; la sigma calibrada es auxiliar y no equivale a una significancia frecuentista. La evidencia favorece incluir N2O con mayor fuerza que NH3 dentro de este marco. El ajuste absoluto sin N2O es pobre y el completo conserva tensión (`χ²_red=3.57`), por lo que la conclusión depende de la adecuación del modelo.

La probabilidad posterior (P(\log_{10}X>A0)) solo se define para la molécula que permanece en cada modelo; para la especie eliminada es N/A por construcción. En el completo: N2O `1.0000`, NH3 `0.9913`; en sin NH3, N2O `1.0000`; en sin N2O, NH3 `0.9991`. Los cuantiles y valores no redondeados están en el CSV/JSON. La probabilidad sobre A0 describe dirección de abundancia; `ΔlnZ` compara modelos. Ninguna establece por sí sola una causa agrícola.

Los resultados históricos con el bineador anterior no son el comparador de estas parejas. Además del operador, cambió la ventana nativa (3.8–19 μm frente a 3–20 μm), por lo que la diferencia histórica/corregida no aísla exclusivamente el efecto del bineado.

## Archivos de control

- `selected_scope.json`: alcance autorizado.
- `campaign_state.json`: estado del supervisor y evidencia baseline.
- `manifest.csv`: una fila por ablación.
- `preflight/`, `resolved/`, `runtime/`, `logs/`, `pids/`: evidencia operativa, callbacks, configuración y ejecución.
- `loo_results_validated_20261020.csv`: tabla validada de dos ablaciones.
- `validation_report_20261020.json`: auditoría independiente, hashes y comprobaciones detalladas.
- [Informe científico de resultados e interpretación](../../../../../docs/life_proxima_a3_100h_corrected_binning_molecular_ablation_2026-10-19.md).
