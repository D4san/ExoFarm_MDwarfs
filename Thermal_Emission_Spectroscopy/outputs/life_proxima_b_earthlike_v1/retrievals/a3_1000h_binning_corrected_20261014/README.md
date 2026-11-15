# A3–1000 h completo, binning coherente, MPI15

Autorización: un nuevo retrieval completo A3 de 1000 h, 14 parámetros
efectivamente libres, superficie negra fija a 1 bar, MPI15/hilo1, `N_live=800`,
`ev_tol=0.5`, `R=10000` y misma rejilla térmica, dataset y priors del completo
anterior. El único cambio fue el operador de binning; no se reutilizó ningún
checkpoint. No se autorizaron retrievals adicionales.

**Cierre operativo:** `campaign_state.json` registra `exit_code=0`, productos
archivados y comparación `SAVED`. El estado permanece
`COMPLETE_PENDING_VALIDATION` / `PENDING_INDEPENDENT_REVIEW`; no hay procesos
Python/MPI activos. El preflight científico pasó; tras detener el gate
conservador RSS×15 sin muestreo, la continuación MPI15 midió PSS agregado
9,28 GiB y aprobó la reserva de memoria. El supervisor de continuación fue
PID777 y el `mpiexec` de producción PID978 (identificadores históricos del
proceso ya finalizado).

**Comparación anterior → corregido:** χ² 542,64 → 242,88 para 17 grados
efectivos; `ln Z` 677,92347 ± 0,26943 → 826,61108 ± 0,27287. La diferencia
`Δln Z=148,68760 ± 0,38347` mide sensibilidad al operador y no es evidencia
Bayesiana molecular. χ² reducido corregido ≈14,29, todavía alto. N₂O se
desplaza +0,051 dex en mediana; NH₃, +1,357 dex, con una posterior que conserva
una cola amplia hacia abundancias bajas. No presentar esos cambios como
detecciones ni como preferencia ExoFarm/A0.

**Qué se corrigió:** el generador de LIFE promedia fotones dentro de celdas
delimitadas por puntos medios de centros vecinos y convierte el resultado a
energía en el centro exacto del canal. La likelihood anterior reconstruía
cada celda como `centro ± semiancho`; en una rejilla logarítmica sus límites
no son los puntos medios reales. Por ejemplo, para centros `[1, 2, 4]`, el
canal central es `[1.5, 3]`, mientras el esquema simétrico da `[1.25, 2.75]`.
El operador corregido integra la superposición de celdas nativas en espacio
fotónico. Se aplicó al callback real de POSEIDON en muestreo y
postprocesamiento, con preflight del cierre contra la verdad A3; dataset,
ruido, priors, atmósfera y opacidades se conservaron.

**Uso posterior:** este wrapper está congelado al dataset A3–1000 h y rechaza
otro hash/configuración. El runner general sigue siendo el camino histórico;
para otro tiempo o para A0 se requiere ampliar y probar el preflight de forma
específica, y ejecutar las hipótesis emparejadas con idéntico operador. La
comparación actual no autoriza por sí sola una afirmación A3/A0.

Los productos primarios y la figura se revisaron; consulte
[`comparison/comparison.md`](comparison/comparison.md),
[`comparison/comparison.json`](comparison/comparison.json) y la figura
[`posterior_PT_comparison.png`](comparison/posterior_PT_comparison.png).
`preserved_inputs.json` conserva los insumos protegidos. Scratch:
`/home/dasan/exofarm_a3_1000h_binning_20261014/`.

Los retrievals A0 existentes emplean el operador anterior; una comparación de
preferencia A3/A0 requiere una pareja ejecutada bajo el mismo operador, datos y
likelihood. Se preserva toda evidencia de ambos operadores.

[Procedimiento científico, resultados y límites](../../../../../docs/life_proxima_a3_1000h_binning_corrected_2026-10-14.md).
