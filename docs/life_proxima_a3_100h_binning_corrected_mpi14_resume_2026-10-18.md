# A3–100 h con bineado corregido: parada y reanudación MPI14

**Fecha:** 2026-10-18 (COT)  
**Estado al 2026-10-19:** muestreo concluido; comparación directa de posteriores calculada; auditoría integral de productos aún pendiente.  
**Autorización:** el usuario pidió detener el retrieval serial activo y
relanzarlo con 14 procesos.

## Qué se cambió

Se detuvo el sampler serial A3–100 h del 17-oct y se congeló su checkpoint
MultiNest. La campaña original y su scratch se conservaron. Una campaña y un
scratch nuevos alojan la continuación, evitando sobrescribir la evidencia del
intento serial. La inspección del checkpoint confirmó `N_live=800`, 14
coordenadas libres, 800 puntos vivos en el cubo unidad y en espacio físico,
dimensiones esperadas, valores finitos y cumplimiento de los límites de prior
y coordenadas constantes.

La parada ocurrió en **31.300 reemplazos y 663.011 evaluaciones**. El checkpoint
validado se copió y se verificó por hash. MultiNest confirmó `resuming from
previous job`, por lo que la corrida actual continúa desde ese estado en vez de
volver a iniciar el muestreo.

## Inicialización MPI y solución del fallo

El primer preflight MPI14 terminó antes de muestrear con código 15. El log
reportó `launcher not compatible with PMI1 client`: el `mpiexec` Open MPI 4.1.6
del sistema intentó lanzar un `mpi4py` compilado para MPICH 4.3.1. Se preservó
ese log y no se lanzó ningún sampler con esa configuración.

El segundo preflight usó el `mpiexec` Hydra incluido en el entorno POSEIDON.
Pasaron la inicialización de 14 ranks, la carga de modelo/datos/priors, el
callback de POSEIDON enlazado al operador fotónico corregido y el gate de
recursos. El cierre relativo máximo del forward fue
`2.2648549702353193e-14` para 31 canales; también pasó la verificación de
binding en muestreo y postprocesamiento.

| Control | Evidencia al iniciar MPI14 | Estado |
|---|---:|---|
| Ranks de muestreo | 14 procesos confirmados por PID | PASS |
| CPU visible | 16 lógicas | PASS |
| Pico PSS del árbol durante preflight | 9.358.423 KiB | PASS |
| Mínimo de `MemAvailable` | 22.360.144 KiB | PASS |
| Umbral requerido (pico PSS + reserva 4,5 GiB) | 14.077.015 KiB | PASS |
| Swap libre después del preflight | 8 GiB de 8 GiB | PASS |
| Callback real / cierre del operador | error relativo máximo `2.26e-14` | PASS |

## Configuración preservada

- Dataset LIFE Proxima A3–100 h, 31 canales; SHA-256
  `78662546181a5b74391a14b7b73ae80d879200a74db6a4bc5338e3ce7eee4705`.
- Modelo POSEIDON con 15 coordenadas declaradas y 14 libres, química
  isochemical, O₂, superficie negra fija a 1 bar y sin inflación de errores.
- `N_live=800`, `R=10000`, operador de solapamiento fotónico corregido y
  rejilla nativa de 3–20 μm.
- Un único sampler MultiNest bajo `mpiexec -n 14`; una hebra por rank mediante
  límites de BLAS/OpenMP.
- Checkpoint procedente únicamente del mismo operador, likelihood, dataset y
  configuración. No se mezclan checkpoints de la campaña A0 fija ni del
  operador histórico.

El resultado histórico de A3–100 h utilizó una rejilla nativa de 3.8–19 μm.
La ejecución corregida emplea 3–20 μm para cubrir los bordes completos de los
canales. Esa diferencia de dominio espectral queda como factor adicional de la
comparación; cualquier cambio posterior no debe atribuirse exclusivamente al
bineado.

## Estado de muestreo y validación

**Corte de estado: 2026-10-19 10:45 COT.** El retrieval concluyó el
2026-10-18 21:01 COT (`end_utc=2026-10-19T02:01:05Z`). MultiNest registró
44.526 reemplazos, 1.474.040 evaluaciones y evidencia final de log
`ln(ev)=894.33122354454542 ± 0.24665403052524296`; `retrieval.log` confirma
`Sampling finished`, código de salida 0 y generación de 1.000 espectros y
perfiles P–T posteriores. Existen productos de muestras, espectro, P–T,
`log_X`, resultados y `MultiNest_raw`. La comprobación de procesos ya no
encuentra los PID del supervisor/lanzador ni un `mpiexec` activo.

La campaña permanece `COMPLETE_PENDING_VALIDATION` con aceptación
`PENDING_INDEPENDENT_AUDIT`. Se deben revisar finitud/consistencia, hashes,
priors y productos derivados antes de interpretar o comparar la evidencia. El
estado JSON conserva además `error=RuntimeError: MPI14 corrected-bin preflight
exited 15`, mientras registra `retry_preflight=PASS`,
`preflight=PASS_MPI14_MPICH_HYDRA` y `exit_code=0`. El primer preflight falló
por la incompatibilidad Open MPI/MPICH documentada; el segundo pasó. La
discrepancia del campo `error` se conserva como asunto pendiente de
reconciliación; el JSON original no se modifica.

## Artefactos

- Campaña activa:
  [`campaign_state.json`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_100h_binning_corrected_mpi14_resume_20261018/campaign_state.json),
  [`manifest.csv`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_100h_binning_corrected_mpi14_resume_20261018/manifest.csv),
  [`README de campaña`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_100h_binning_corrected_mpi14_resume_20261018/README.md).
- Checkpoint auditado:
  [`checkpoint_validation.json`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_100h_binning_corrected_mpi14_resume_20261018/checkpoint_validation.json).
- Preflight fallido, preservado:
  [`preflight_mpi14.log`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_100h_binning_corrected_mpi14_resume_20261018/preflight_mpi14.log).
- Preflight MPICH/Hydra aprobado:
  [`preflight_mpi14_retry01.log`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_100h_binning_corrected_mpi14_resume_20261018/preflight_mpi14_retry01.log)
  y [`registro del operador`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_100h_binning_corrected_mpi14_resume_20261018/operator_preflight_mpi14_retry01.json).
- Log activo:
  [`retrieval.log`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_100h_binning_corrected_mpi14_resume_20261018/retrieval.log).
- Scripts:
  [`controlador de rebalanceo`](../Thermal_Emission_Spectroscopy/scripts/rebalance_proxima_a3_100h_corrected_mpi14.py)
  y [`wrapper MPI14`](../Thermal_Emission_Spectroscopy/scripts/run_life_retrieval_a3_100h_binning_corrected_mpi14_resume.py).

## Comparación con el retrieval de bineado histórico

La comparación responde a la pregunta original: cuánto cambia el retrieval
A3–100 h al sustituir el operador histórico por el callback de solapamiento
fotónico corregido. Ambos usan la misma realización de LIFE de 31 canales
(SHA-256 `78662546181a5b74391a14b7b73ae80d879200a74db6a4bc5338e3ce7eee4705`).
Los resúmenes de resultados y las muestras equiponderadas preservadas se
contrastaron directamente. Los cuantiles siguientes se recalcularon como
q16/mediana/q84 a partir de los archivos de muestras; ambos contienen 15
columnas y todos los valores son finitos (7.479 filas históricas y 7.268
corregidas). El operador histórico promediaba el flujo energético con
`bin_spectrum_to_data`; el corregido integra la superposición de fotones usando
bordes medios entre canales y devuelve energía por canal en su centro.
Las entradas usadas son las muestras
[históricas](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/samples/proxima_A3_100h_O2_fixedBlack1bar_noxtol_proxima_A3_100h_O2_fixedBlack1bar_noxtol_samples.txt)
y
[corregidas](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_100h_binning_corrected_mpi14_resume_20261018/products/samples/proxima_A3_100h_O2_fixedBlack1bar_noxtol_BIN1_20261017_samples.txt).

| Métrica | Bineado histórico | Bineado corregido | Cambio descriptivo |
|---|---:|---:|---:|
| `ln Z` del retrieval completo | `884.333304 ± 0.244466` | `894.331224 ± 0.246654` | `+9.997920 ± 0.347278`* |
| Mejor `χ²` | 79.01 | 57.19 | −21.82 (−27.6 %) |
| `χ²_red` (16 grados de libertad) | 4.94 | 3.57 | −1.37 |

*La incertidumbre de la diferencia combina en cuadratura los errores de
integración de evidencia reportados por ambas corridas. Este `Δ ln Z` es una
medida de sensibilidad entre dos implementaciones del forward; **no es un
factor de Bayes interpretable entre modelos atmosféricos**. Cambiaron el
operador de integración y la rejilla nativa, y el manifiesto histórico no
preserva todos los límites de prior para certificar identidad parámetro a
parámetro.

| Parámetro | Histórico q16 / mediana / q84 | Corregido q16 / mediana / q84 | Cambio de mediana |
|---|---:|---:|---:|
| `log_N2O` | `−6.203983 / −6.147638 / −6.092660` | `−6.169192 / −6.116278 / −6.064926` | `+0.031360 dex` |
| `log_NH3` | `−8.658619 / −8.257788 / −8.056875` | `−8.393808 / −8.170365 / −8.015292` | `+0.087423 dex` |

El intervalo central del 68 % de N₂O se estrecha ligeramente (ancho 0.1113 a
0.1043 dex); el de NH₃ se estrecha más (0.6017 a 0.3785 dex, cerca de 37 %),
aunque ambos intervalos de NH₃ se solapan ampliamente. Frente a las referencias
efectivas `log10(N2O_A0) = −6.884325` y `log10(NH3_A0) = −9.950526`, la fracción
de muestras equiponderadas por encima de A0 es 100 % en ambas corridas para
N₂O, y 94.87 % histórica frente a 99.13 % corregida para NH₃. Esta fracción es
un resumen posterior condicional, no evidencia bayesiana ni atribución causal.

La lectura directa es que el cambio del forward mejora de forma marcada el
mejor ajuste y eleva modestamente las medianas; el cambio más visible en la
forma de la posterior es la reducción de la cola baja de NH₃. La corrida
corregida conserva `χ²_red=3.57`, todavía indicativo de tensión de ajuste. La
corrección no convierte por sí sola a NH₃ en una detección ni demuestra que el
bineado, aislado de la rejilla y de otros detalles de configuración, explique
toda la diferencia. La figura de posteriores superpuestas está en
[`retrieval_A3_100h_historical_vs_corrected_binning_posterior_proxima.png`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A3_100h_historical_vs_corrected_binning_posterior_proxima.png);
se reproduce con
[`plot_proxima_a3_100h_binning_sensitivity.py`](../Thermal_Emission_Spectroscopy/scripts/plot_proxima_a3_100h_binning_sensitivity.py).

La aceptación integral de la campaña permanece pendiente: debe reconciliarse
la discrepancia histórica del campo `error` del estado MPI14 y completar las
verificaciones de posterior, espectro, P–T, `log_X`, productos MultiNest,
hashes, priors y callback activo. Por tanto, estos números son una comparación
cuantitativa preliminar de productos concluidos, no el cierre de auditoría.
