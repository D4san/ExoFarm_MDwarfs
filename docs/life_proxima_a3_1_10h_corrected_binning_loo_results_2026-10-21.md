# LIFE Proxima A3 a 1 h y 10 h: ablaciones con binning corregido

**Estado: COMPLETE_VALIDATED; auditoría independiente PASS, 2026-10-21.** Se completaron y validaron seis retrievals LIFE de Proxima b: modelo completo, sin NH₃ y sin N₂O para cada una de las exposiciones de 1 h y 10 h. El contraste de evidencia más claro aparece para N₂O a 10 h. Las comparaciones de NH₃ y ambos contrastes a 1 h son compatibles con evidencia prácticamente equilibrada entre el modelo completo y el modelo sin esa molécula.

## Pregunta y alcance

La prueba mide cómo cambia la evidencia al retirar por separado NH₃ o N₂O, con todo lo demás emparejado dentro de la misma duración. Para cada especie (X) y duración (t):

\[
\Delta\ln B_X(t)=\ln Z_{\mathrm{completo},t}-\ln Z_{\mathrm{sin}\,X,t},
\qquad
\sigma_{\Delta\ln B}=\sqrt{\sigma_{\ln Z,\mathrm{completo}}^2+\sigma_{\ln Z,\mathrm{sin}\,X}^2}.
\]

Un valor positivo favorece incluir (X) frente a la ablación especificada, condicionado a los priors y la verosimilitud de este retrieval. La resta se hizo únicamente entre modelos con idéntico archivo observado, SHA-256 y duración. Los valores absolutos de ln Z de 1 h y 10 h **no** se restan entre sí.

La campaña conserva las realizaciones observadas existentes, con 31 canales cada una:

| Duración | Dataset | SHA-256 |
|---|---|---|
| 1 h | `LIFE_proxima_A3_1h_O2_fixedBlack1bar_official.dat` | `a3043e5de76a834983949e6eca12636ea4de174ebdb2db0853155282c100dee2` |
| 10 h | `LIFE_proxima_A3_10h.dat` | `46a026504b9b9521fa29407a501169b9d3cfc433de40a91b8ade86d7767abb5b` |

Configuración común auditada: `N_live=800`, tolerancia de evidencia 0.5, `R=10000`, intervalo de modelo 3–20 μm, P–T Madhu, abundancias isochem, O₂ incluido, superficie negra fija a 1 bar y sin inflación de errores. El modelo completo declara 15 coordenadas (14 libres); cada LOO declara 14 (13 libres). La ablación retira tanto `log_X` como la opacidad de la especie. Priors y ajustes restantes coinciden con la configuración de referencia del retrieval A3–100 h corregido.

El operador aplicado integra fotones mediante solapamiento de bordes/puntos medios y convierte a energía en el centro exacto del canal. Los seis registros de operador documentan el callback POSEIDON enlazado en muestreo y postproceso, cinco ranks MPI por retrieval, 31 canales y cierre relativo de (2.2649\times10^{-14}). Las tandas 1 h y 10 h corrieron secuencialmente con tres MPI5 (15 ranks) cada una; no se reutilizaron checkpoints.

## Evidencia de modelo

| Duración | Contraste | ln Z completo | ln Z sin X | Δ ln Z (error numérico) | Sigma bilateral auxiliar | χ² reducido completo / sin X |
|---:|---|---:|---:|---:|---:|---:|
| 1 h | sin NH₃ | 866.282760 ± 0.166589 | 866.809245 ± 0.164725 | **−0.526485 ± 0.234278** | N/A | 1.63 / 1.51 |
| 1 h | sin N₂O | 866.282760 ± 0.166589 | 866.312379 ± 0.165640 | **−0.029618 ± 0.234922** | N/A | 1.63 / 1.52 |
| 10 h | sin NH₃ | 891.387174 ± 0.208811 | 891.612880 ± 0.204995 | **−0.225706 ± 0.292617** | N/A | 1.22 / 1.35 |
| 10 h | sin N₂O | 891.387174 ± 0.208811 | 882.245181 ± 0.204575 | **+9.141993 ± 0.292323** | +4.664 | 1.22 / 2.34 |

Las incertidumbres de Δln Z propagan en cuadratura los errores numéricos reportados por MultiNest. La sigma de la última fila es la transformación bilateral calibrada del módulo de ln B prescrita por [`report_proxima_loo_lin_sigma.py`](../Thermal_Emission_Spectroscopy/scripts/report_proxima_loo_lin_sigma.py); se incluye como descriptor auxiliar, no como significancia frecuentista. La convención devuelve N/A para Δln Z ≤ 0.

## Dirección de los posteriores respecto a A0

La probabilidad (P(\log_{10}X>\log_{10}X_{A0})) se calcula sobre las muestras equal-weight del posterior validado. Los umbrales son `log10(N2O_A0) = −6.884325289636784` y `log10(NH3_A0) = −9.950526295665036`. Una molécula retirada no tiene posterior ni probabilidad definida en esa variante; allí se informa N/A.

| Duración | Modelo | Mediana log₁₀ N₂O; IC 95 %; P(N₂O>A0) | Mediana log₁₀ NH₃; IC 95 %; P(NH₃>A0) |
|---:|---|---|---|
| 1 h | Completo | −8.784; [−11.775, −5.625]; **0.1898** | −9.787; [−11.860, −7.420]; **0.5397** |
| 1 h | Sin NH₃ | −8.641; [−11.794, −5.639]; **0.2169** | N/A | 
| 1 h | Sin N₂O | N/A | −9.837; [−11.877, −7.470]; **0.5243** |
| 10 h | Completo | −6.015; [−6.346, −5.778]; **0.99986** | −8.229; [−11.698, −7.428]; **0.8040** |
| 10 h | Sin NH₃ | −6.089; [−6.411, −5.824]; **1.0000** | N/A |
| 10 h | Sin N₂O | N/A | −8.186; [−11.631, −7.493]; **0.8390** |

## Lectura

- **N₂O, 1 h:** Δln Z = −0.030 ± 0.235, esencialmente empate de evidencia; el posterior completo asigna 0.190 de probabilidad a abundancia sobre A0. Con esta realización de 1 h, los datos todavía no separan con claridad los dos modelos.
- **N₂O, 10 h:** Δln Z = +9.142 ± 0.292 favorece fuertemente el modelo que mantiene N₂O. El posterior ubica N₂O sobre A0 en 0.99986 del modelo completo y 1.0000 cuando se retira NH₃. La conclusión sobre N₂O es consistente entre ambos ajustes que conservan esa molécula.
- **NH₃, 1 h:** Δln Z = −0.526 ± 0.234 se inclina hacia la ablación, mientras (P(NH₃>A0)) es 0.540 en el modelo completo y 0.524 al retirar N₂O. No emerge una preferencia convincente por incluir NH₃.
- **NH₃, 10 h:** Δln Z = −0.226 ± 0.293 sigue siendo compatible con empate y su valor central favorece levemente el modelo sin NH₃. Al mismo tiempo, (P(NH₃>A0)=0.804) en el completo y 0.839 sin N₂O: el posterior desplaza masa sobre A0, pero el contraste de evidencia no favorece añadir el parámetro/opacidad de NH₃ bajo estos priors y este modelo.

En conjunto, esta prueba ofrece evidencia condicional robusta para N₂O a 10 h, pero no establece evidencia de inclusión equivalente para NH₃. (P(X>A0)) describe la dirección posterior de abundancia; Δln Z compara modelos. Ninguna métrica atribuye por sí sola la molécula a actividad agrícola, determina origen biológico o industrial, ni demuestra que ExoFarm pueda distinguirse de todos los escenarios naturales. La interpretación permanece condicionada al espectro sintético A3, la estructura isochem, el perfil P–T, los priors y el modelo de ruido/likelihood fijados.

Los resultados históricos con el bineador anterior no forman parte de estas parejas emparejadas. Además del operador, los retrievals antiguos usaron otra ventana espectral nativa (3.8–19 μm frente a 3–20 μm); la diferencia entre implementaciones no aísla por sí sola el efecto del binning.

## Auditoría, trazabilidad y reproducción

El supervisor finalizó las dos tandas y ya no estaba activo al iniciar la auditoría (`PID 852` ausente; cero `mpiexec`). Los seis códigos de retorno son 0. La auditoría independiente comprobó, para cada modelo: configuración y priors, SHA-256 del dataset, coincidencia del posterior POSEIDON con `-post_equal_weights.dat`, finitud, espectro (18 971 filas), perfil P–T (100 filas), `log_X` (800 filas completo; 700 filas LOO), tablas nativas, 800 puntos vivos, concordancia de reemplazos/evaluaciones, evidencia `stats.dat` frente al resultado, exclusión de parámetro/opacidad y callback corregido durante muestreo/postproceso.

El supervisor había dejado seis entradas `pending` en `campaign_state.json.runs` aunque `manifest.csv`, logs y productos mostraban la finalización. Tras comprobar que el PID 852 había salido y aprobar la auditoría, se conservaron copias byte-a-byte [`campaign_state_pre_audit_20261021.json`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1_10h_binning_corrected_loo_20261020_r03/campaign_state_pre_audit_20261021.json) y [`manifest_pre_audit_20261021.csv`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1_10h_binning_corrected_loo_20261020_r03/manifest_pre_audit_20261021.csv). Luego ambos ledgers se reconciliaron a `COMPLETE_VALIDATED`/`validated`, preservando los códigos y contadores originales.

- [README y ledger final de campaña](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1_10h_binning_corrected_loo_20261020_r03/README.md)
- [Alcance congelado](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1_10h_binning_corrected_loo_20261020_r03/selected_scope.json)
- [Auditoría detallada, checks y hashes](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1_10h_binning_corrected_loo_20261020_r03/validation_report_20261021.json)
- [Tabla por retrieval](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1_10h_binning_corrected_loo_20261020_r03/retrieval_models_validated_20261021.csv) · [contrastes LOO](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1_10h_binning_corrected_loo_20261020_r03/loo_results_validated_20261021.csv)
- [Figura de Δln Z](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1_10h_binning_corrected_loo_20261020_r03/a3_1_10h_corrected_bin_molecular_ablation_lnB_20261021.svg)
- [Script de auditoría reproducible](../Thermal_Emission_Spectroscopy/scripts/audit_proxima_a3_1_10h_corrected_bin_campaign.py) · [validador de productos](../Thermal_Emission_Spectroscopy/scripts/validate_proxima_molecular_ablation_loo.py)
- [Bitácora de lanzamiento y preflight](life_proxima_a3_1_10h_corrected_binning_loo_2026-10-20.md)
