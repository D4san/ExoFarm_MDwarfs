# A3–100 h sin NH3 y sin N2O con el bineador corregido

**Inicio:** 2026-10-19. **Cierre y auditoría independiente:** 2026-10-20. **Estado:** las dos ablaciones y el baseline corregido están validados; se preservaron todos los productos nativos.

## Pregunta científica

La pregunta operativa es cuánto favorece la distribución LIFE de A3 a 100 h un modelo que conserva cada opacidad molecular frente al contrafactual donde se retira una molécula. Para responderla se iniciaron dos ablaciones independientes: una sin NH3 y otra sin N2O. Ambas se emparejan con el retrieval completo A3–100 h que usa el bineador fotónico corregido y exactamente la misma realización observada.

Esta prueba evalúa soporte del dato para la molécula dentro de esta configuración de retrieval. No mide por sí sola una probabilidad de origen agrícola, no reemplaza una comparación de escenarios generativos A0–A3 y no elimina las limitaciones de perfil vertical, ruido diagonal o una sola realización.

## Modelos y contraste

En cada ablación se quitan a la vez el parámetro de abundancia constante (`log_NH3` o `log_N2O`) y la opacidad correspondiente. Los otros parámetros, perfiles, límites de prior, datos, likelihood, bineador, PT, tratamiento de O2, superficie y presupuesto de integración permanecen emparejados con el completo corregido. Por ello cada modelo pasa de 15 coordenadas declaradas/14 libres a 14 declaradas/13 libres; `log_P_surf` sigue fijo a 1 bar.

Para la especie X, el contraste principal será:

\[
\Delta\ln Z_X = \ln Z_{\mathrm{completo, corregido}} - \ln Z_{\mathrm{sin\,X, corregido}}.
\]

Un valor positivo favorece incluir la molécula bajo los priors declarados; uno negativo favorece la ablación. La incertidumbre numérica de la diferencia se calculará como \(\sqrt{\sigma^2_{\mathrm{full}}+\sigma^2_{\mathrm{sinX}}}\). La sigma descriptiva calibrada con la convención del proyecto será auxiliar y se reportará N/A para \(\Delta\ln Z\le0\); `ln B` conserva la interpretación principal.

La dirección de abundancia se tratará en una columna distinta: la fracción de muestras posterior del completo por encima de la abundancia A0 efectiva, además de mediana y cuantiles. Esa fracción no se definirá para la especie ausente en el modelo ablacionado. Diferenciar ambas cantidades evita confundir preferencia de modelos con probabilidad posterior de enriquecimiento.

## Configuración y procedencia

- Escenario/tiempo: LIFE Proxima A3–100 h.
- Dataset: `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A3_100h.dat`; 31 canales; SHA-256 `78662546181a5b74391a14b7b73ae80d879200a74db6a4bc5338e3ce7eee4705`; semilla de generación 129315834.
- Completo comparador: campaña `a3_100h_binning_corrected_mpi14_resume_20261018`, posterior y stats en `products/`; `ln Z=894.3312235445454 ± 0.24665403052524296`, `χ²_red=3.57` (16 grados de libertad). Pasó la misma auditoría independiente de productos y quedó marcado `COMPLETE_VALIDATED`.
- Ajustes emparejados: `N_live=800`, `ev_tol=0.5`, `R=10000`, 3–20 μm, Madhu, isochem, O2, superficie negra fija a 1 bar, sin `x_tol` ni inflación.
- Paralelismo solicitado: sin NH3 MPI8; sin N2O MPI7; 15 ranks total y un hilo por rank. No se reanudan checkpoints.
- Campaña nueva: `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_100h_binning_corrected_loo_20261019/`.
- Scratch aislado: `/home/dasan/exofarm_a3_100h_binning_corrected_loo_20261019/`.
- Operador: solapamiento fotónico por celdas limitadas por bordes/puntos medios y conversión energética en centro de canal; callback POSEIDON se enlaza durante el muestreo y el postproceso.

## Ejecución y auditoría independiente

Los dos preflight reales (MPI8 y MPI7) pasaron el 2026-10-19 a las 16:37 UTC. Cada ablación declaró 14 coordenadas, 13 libres; mantuvo `log_P_surf=0` (superficie a 1 bar), la misma realización LIFE de 31 canales, priors compartidos y callback POSEIDON enlazado al operador corregido. El cierre del operador frente al producto LIFE guardado fue `2.2648549702353193e-14` como error relativo máximo. Los samplers usaron 15 ranks entre ambas corridas, sin reutilizar checkpoints, y terminaron con `return_code=0`.

La inspección final registró `active_run_ids=[]`; los logs de ambas variantes contienen los marcadores `[done]` y `[operator-postprocessing-complete]`. La consulta del árbol de procesos Linux no estuvo disponible desde esta sesión de Windows; el cierre se establece mediante ledger, logs y productos finales, no por una lectura independiente de `/proc`.

La auditoría del 2026-10-20 volvió a leer el baseline y las dos ablaciones, comparando resúmenes de resultados con stats nativos de MultiNest. Verificó dataset y hashes, configuración/prior emparejados, operador y binding durante muestreo y postproceso, finitud, headers y dimensiones posteriores, muestras iguales fila a fila a `-post_equal_weights.dat`, espectros, perfiles P–T, `log_X`, tablas raw, `resume`, puntos vivos y archivos de evidencia. Los valores de `log_P_surf` en todas las muestras permanecen en 0. Los reportes detallados de validación incluyen dimensiones, filas, cierres, hashes de los productos y formas de los archivos nativos.

El contador de filas que capturó el controlador quedó una unidad por debajo en cada ablación: 6380 frente a 6381 muestras finales para sin NH3 y 6822 frente a 6823 para sin N2O. En cada caso `samples.txt` y las muestras de peso igual de MultiNest coinciden entre sí en el conteo final; se reconciliaron las filas vigentes del ledger y manifiesto, preservando los valores iniciales en campos separados. Es una discrepancia de snapshot del contador, no una fila ausente en el posterior.

El estado inicial del baseline aún contiene el campo histórico `RuntimeError: MPI14 corrected-bin preflight exited 15`. Se conserva íntegro: corresponde a la primera invocación con launcher Open MPI incompatible con el cliente MPICH/PMI1. El retry con MPICH/Hydra registró preflight PASS y la corrida final `exit_code=0`; la auditoría de productos pasó. No representa un error de muestreo actual.

## Resultados

Se usa la diferencia de evidencia como métrica primaria:

\[
\Delta\ln Z_X = \ln Z_{\mathrm{completo, corregido}} - \ln Z_{\mathrm{sin\,X, corregido}},
\qquad
\sigma_{\Delta} = \sqrt{\sigma_{\mathrm{full}}^2+\sigma_{\mathrm{sinX}}^2}.
\]

Un valor positivo favorece incluir X bajo este modelo, likelihood y conjunto de priors. La sigma calibrada es auxiliar y descriptiva, no una significancia frecuentista.

| Ablación | `ln Z` sin X | `Δln Z` (error numérico) | Sigma calibrada auxiliar | `χ²_red` (g.l.) |
|---|---:|---:|---:|---:|
| Sin NH3 | 891.582233 ± 0.240689 | +2.748991 ± 0.344630 | +2.853 | 4.06 (17) |
| Sin N2O | 809.670715 ± 0.243406 | +84.660508 ± 0.346532 | +13.217 | 13.55 (17) |

Referencia común: completo `ln Z=894.331224 ± 0.246654`, `χ²_red=3.57` (16 g.l.). La evidencia favorece incluir ambas moléculas en el marco comparado, con contraste mucho más marcado para N2O. El modelo sin N2O presenta además un ajuste absoluto pobre (`χ²_red=13.55`), por lo que su penalización de evidencia debe leerse junto con esa falta de adecuación; estos resultados no identifican por sí mismos la fuente de la molécula.

La dirección de abundancia se resume por separado con cuantiles posteriores y la masa posterior por encima de los niveles A0 efectivos (`log10 N2O_A0=−6.884325289636784`; `log10 NH3_A0=−9.950526295665036`). Los cuantiles se muestran como q16/mediana/q84, en dex:

| Posterior usado | Especie retenida | q16 / mediana / q84 | \(P(\log_{10}X>A0)\) |
|---|---|---:|---:|
| Completo corregido | N2O | −6.1692 / −6.1163 / −6.0649 | 1.0000 |
| Completo corregido | NH3 | −8.3938 / −8.1704 / −8.0153 | 0.9913 |
| Sin NH3 | N2O | −6.1830 / −6.1308 / −6.0814 | 1.0000 |
| Sin N2O | NH3 | −8.2309 / −8.0692 / −7.9389 | 0.9991 |

Para la especie eliminada no hay una abundancia recuperada y la probabilidad sobre A0 es **N/A por construcción**. El posterior de una especie retenida en el modelo de la otra ablación es condicional a ese modelo. En particular, una probabilidad posterior alta de NH3 sobre A0 no equivale a la evidencia de inclusión de NH3: esa comparación la aporta `Δln Z`.

## Lectura y límites

En esta realización sintética y bajo el operador corregido, el modelo completo supera a la ablación de N2O por una gran diferencia de evidencia y a la ablación de NH3 por una diferencia positiva, de menor tamaño. Eso sustenta una preferencia comparativa condicionada por la configuración; no demuestra una detección independiente de una fuente agrícola, una atribución causal a ExoFarm ni una separación completa frente a todos los escenarios A0–A3. La evidencia depende de los priors, de la química isochem de abundancia constante y del modelo de ruido diagonal. El `χ²_red=3.57` del completo todavía aconseja cautela respecto de la adecuación global, especialmente si se comparan afirmaciones de alta significancia.

Las corridas históricas con el bineador anterior no son el comparador de este análisis. Además de cambiar el operador, aquellas usaron otra ventana nativa (3.8–19 μm frente a 3–20 μm); cualquier diferencia histórico/corregido combina ambos cambios y no aísla el efecto del operador. Las conclusiones de esta tabla sí proceden de parejas corregidas con la misma realización, rejilla, priors y likelihood.

## Archivos de auditoría y reproducción

- Tabla validada CSV: `../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_100h_binning_corrected_loo_20261019/loo_results_validated_20261020.csv`.
- Auditoría independiente JSON, con hashes y pruebas de productos: `../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_100h_binning_corrected_loo_20261019/validation_report_20261020.json`.
- Estado y manifiesto reconciliados: [README de la campaña](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_100h_binning_corrected_loo_20261019/README.md), `campaign_state.json` y `manifest.csv` en el mismo directorio.
- Auditor reproducible y de solo lectura sobre retrievals: [`audit_proxima_a3_100h_corrected_bin_ablations.py`](../Thermal_Emission_Spectroscopy/scripts/audit_proxima_a3_100h_corrected_bin_ablations.py); usa las validaciones de posterior y la convención auxiliar de [`report_proxima_loo_lin_sigma.py`](../Thermal_Emission_Spectroscopy/scripts/report_proxima_loo_lin_sigma.py).
- La calibración auxiliar sigue la [convención de sigma LOO del proyecto](life_proxima_loo_sigma_lin_convention_2026-10-10.md); se reporta N/A si `Δln Z≤0` y no se interpreta como p-valor.
- Productos nativos conservados: [salidas sin NH3](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_100h_binning_corrected_loo_20261019/runs/A3_100h_no_NH3/POSEIDON_output/proxima_b_earthlike/retrievals/) y [salidas sin N2O](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_100h_binning_corrected_loo_20261019/runs/A3_100h_no_N2O/POSEIDON_output/proxima_b_earthlike/retrievals/).

## Enlaces de ejecución

- [README de campaña, estado y manifiesto](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_100h_binning_corrected_loo_20261019/README.md)
- [Supervisor](../Thermal_Emission_Spectroscopy/scripts/launch_proxima_a3_100h_binning_corrected_loo.py)
- [Runner con operador corregido](../Thermal_Emission_Spectroscopy/scripts/run_life_retrieval_a3_100h_binning_corrected_loo.py)
- Baseline completo validado: [salida de resultados](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_100h_binning_corrected_mpi14_resume_20261018/products/results/proxima_A3_100h_O2_fixedBlack1bar_noxtol_BIN1_20261017_results.txt), estadísticas raw de MultiNest y [README de procedencia](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_100h_binning_corrected_mpi14_resume_20261018/README.md).
