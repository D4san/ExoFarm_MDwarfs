# LIFE Proxima A3–1000 h: auditoría de restricciones A0 con binning corregido

**Auditoría:** 2026-10-17 18:24 UTC. **Estado:** productos primarios y evidencia validados; aceptación formal pendiente de revisar seis `NaN` derivados de coordenadas constantes. Los originales se conservaron. No se reinició ni reanudó ninguna corrida.

## Pregunta y diseño del contraste

La campaña pregunta cuánto favorecen estos datos A3–1000 h las abundancias libres de N₂O y NH₃ frente a fijar una de ellas o ambas en la referencia efectiva A0. Mantiene tres contrastes emparejados: N₂O fija, NH₃ fija y conjunta. Cada uno se compara exclusivamente con el retrieval libre completo **corregido** `a3_1000h_binning_corrected_20261014`, usando la misma realización observada, la misma likelihood y el mismo operador fotónico. Las A0 antiguas que usaban otro operador no son denominadores válidos para estos factores de Bayes.

La pregunta tiene dos capas que se reportan por separado:

1. **Preferencia entre modelos:** ¿mejora la evidencia marginal al permitir que la abundancia se aparte del valor escalar A0?
2. **Dirección y tamaño posterior:** en el modelo libre, ¿qué fracción de la posterior queda por encima de A0 y por cuánto?

Una evidencia favorable al modelo libre permite desviaciones en ambas direcciones; por sí sola no demuestra enriquecimiento. La dirección se calcula después sobre las muestras del completo y se compara también con la masa que ya asignaba el prior al evento `X > A0`.

## Qué significa aquí “A0 fija”

La abundancia de referencia es el promedio ponderado en presión del perfil preagrícola entre `5×10⁻⁸` y `1 bar`, calculado en el atlas y documentado en [la metodología A0](life_proxima_a0_enrichment_methodology_2026-10-10.md). No es el promedio de `log X`, ni un perfil vertical, ni una atmósfera A0 completa reinyectada. Para este ajuste se fijan exactamente:

| Especie | log₁₀ VMR A0 | VMR |
|---|---:|---:|
| N₂O | −6.884325289636784 | 1.305192923200922 × 10⁻⁷ |
| NH₃ | −9.950526295665036 | 1.1206595703796514 × 10⁻¹⁰ |

La referencia no marginaliza incertidumbre fotoquímica ni incertidumbre del propio promedio. En los modelos fijados las opacidades de la especie **se mantienen**; se fija su abundancia, no se elimina la molécula del forward model.

## Ejecución y configuración congelada

El usuario autorizó el 2026-10-16 un relanzamiento fresco tras el apagón. El intento del 15-oct quedó separado y preservado; este run no reutilizó checkpoints. La campaña cerró las tres variantes con `return_code=0`, tras pasar el preflight y los callbacks reales del forward model en MPI5. Dataset A3–1000 h, SHA-256 `5611c5904ef03aa02586bed15f14c0c2560ac5ae6fa9463ef420229311db75fa`.

Configuración emparejada: `N_live=800`, `ev_tol=0.5`, `R=10000`, 3–20 μm, Madhu/isochem/O₂, superficie negra fija a 1 bar, rejilla de opacidades de 180–310 K en pasos de 10 K, sin inflación de errores. Las variantes declaran 15 coordenadas y dejan 13/13/12 libres. Solo cambian los priors seleccionados a anchura cero. El operador de punto medio fotónico y la identidad del dataset se verificaron tanto en la vinculación real del callback como en el postprocesado. La fuente de operador usada y verificada es `life_bin_operator_diagnostic.py` (SHA-256 `ba17b7056eb094bd210aca23aacd6aa9dbdcfabdf65352d641faf93c20252731`); el registro de equivalencia confirma que el cambio frente al código reconstruido fue documental/mensajes de error, sin cambio del operador científico.

## Auditoría de productos y procedencia

El [script de auditoría independiente](../Thermal_Emission_Spectroscopy/scripts/audit_proxima_a3_1000h_a0_fixed_binning_corrected.py) releyó los resultados y los ocho productos MultiNest por variante; comprobó la configuración contra el completo, el mismo SHA del dataset, las regiones de prior, las coordenadas fijas en muestras ponderadas/igual-peso y perfiles, las cuentas de `resume.dat` y `ev.dat`, los 800 puntos vivos, y el acuerdo entre `stats.dat`, resumen nested y valores impresos en los resultados. También verificó logs de finalización MPI5 y re-hasheó los productos al cerrar la auditoría.

| Variante A0 | `ln Z` desde `stats.dat` | Error numérico | χ² / dof efectivo | Muestras iguales | Espectro / PT / `log_X` |
|---|---:|---:|---:|---:|---|
| N₂O fija | 200.104997 | 0.270869 | 1496.72 / 18 | 7512 | 18971×6 / 100×6 / 800 |
| NH₃ fija | 827.603805 | 0.268011 | 245.61 / 18 | 6809 | 18971×6 / 100×6 / 800 |
| N₂O + NH₃ fijas | 200.547545 | 0.267563 | 1499.30 / 19 | 7178 | 18971×6 / 100×6 / 800 |

En cada variante coinciden las filas exportadas de posterior de POSEIDON y las muestras `post_equal_weights`; las muestras ponderadas y los puntos `live`/`phys_live` respetan los priors. `log_X` contiene 800 filas y los tres perfiles fijados conservan los valores especificados. La tabla JSON de validación registra dimensiones, contadores, SHA-256 de cada producto, estadísticas y comprobaciones. La tabla CSV/JSON final tiene las tres parejas.

### Salvedad de finitud estricta

Se detectaron **seis tokens `NaN`** y todos están etiquetados como `derived_standard_deviation` de abundancias fijadas: uno en el `-summary.txt` de N₂O, uno en el de NH₃, tres en el `-summary.txt` conjunto (N₂O y dos momentos/resúmenes NH₃) y uno en la línea 17 de `joint-...-stats.dat` para NH₃. No hay `NaN` en las coordenadas de muestras, el espectro, P–T, `log_X`, la evidencia, puntos vivos ni parámetros libres. Las columnas fijas de las muestras igual-peso y ponderadas son exactamente constantes en todos los registros auditados.

El auditor calculó aparte los segundos momentos centrados alrededor del valor fijo con `math.fsum`. Para las coordenadas moleculares fijadas, medias = valor impuesto y desviaciones = **0.0 dex** en 7512/20787 filas ponderadas/iguales para N₂O, 6809/18751 para NH₃ y 7178/20132 para la conjunta (N₂O y NH₃). Se incluyó también `log_P_surf`, constante a 0.0. Estos sidecars son productos derivados nuevos; los `stats.dat` y `-summary.txt` originales permanecen sin reparar.

Conclusión de auditoría: **PASS** de resultados primarios, hashes, priors, evidencia, configuración y finitud de los parámetros muestreados; **FAIL** de finitud global estricta por las seis estadísticas derivadas. El estado de campaña queda `VALIDATED_PRIMARY_PRODUCTS_REQUIRES_REVIEW`, aceptación `PENDING_FIXED_MOMENT_REVIEW`. No se aplicó automáticamente una excepción de aceptación.

## Evidencia frente a A0

El completo corregido da `ln Z = 826.611078 ± 0.272874`; sus `stats.dat`, resumen nested y comparación oficial `corrected_operator` concuerdan. La diferencia y su incertidumbre numérica se calculan por pareja como

\[
\ln B_{\rm libre,A0}=\ln Z_{\rm completo,corregido}-\ln Z_{\rm A0},\qquad
s_{\ln B}=\sqrt{s_{\rm completo}^2+s_{\rm A0}^2}.
\]

| Restricción A0 | ln B libre/A0 ± error numérico | Sigma bilateral calibrado | Lectura de evidencia |
|---|---:|---:|---|
| N₂O fija | **626.5061 ± 0.3845** | **35.50** | Evidencia marginal abrumadora a favor de dejar N₂O libre dentro de estos modelos y datos. |
| NH₃ fija | **−0.9927 ± 0.3825** | **N/A** | El valor central favorece la restricción A0 por ~2.70:1; la diferencia es pequeña y comparable con el error numérico. No hay preferencia convincente por liberar NH₃. |
| N₂O + NH₃ fijas | **626.0635 ± 0.3822** | **35.49** | La pareja libre es fuertemente preferida a fijar ambas. Esta comparación conjunta no asigna sigma a cada especie. |

La columna sigma reproduce la calibración bilateral auxiliar de Benneke–Seager/Lin registrada en [la convención del proyecto](life_proxima_loo_sigma_lin_convention_2026-10-10.md): se resuelve `B = −1/(e p ln p)` con `p = erfc(σcal/√2)`. Para `ln B ≤ 0` se informa `N/A`, no cero ni una sigma negativa. **ln B sigue siendo la estadística primaria**; σ es una calibración descriptiva, no un p-value medido ni una significancia frecuentista. Los errores indicados solo representan la precisión numérica reportada por MultiNest; se combinaron en cuadratura suponiendo independencia entre retrievals. Las tres diferencias comparten el mismo ln Z completo, así que sus errores/resultados no son independientes entre sí.

## Dirección y tamaño de la posterior libre

Usando las 7168 filas de igual peso del completo corregido, para cada especie se calculó `δ = log₁₀ X − log₁₀ X₀` y `E = X/X₀ = 10^δ`. Intervalos son cuantiles marginales iguales al 95 %.

| Especie | δ mediana [2.5 %, 97.5 %] (dex) | Factor E mediana [2.5 %, 97.5 %] | P(X > A0 | D, modelo libre) | Prior nominal P(X > A0) |
|---|---:|---:|---:|---:|
| N₂O | 0.8265 [0.7977, 0.8540] | 6.706 [6.277, 7.144] | 7168/7168 = 1.000 en la muestra | 0.5349 |
| NH₃ | 0.8205 [−1.6669, 1.2838] | 6.615 [0.0215, 19.224] | 5642/7168 = 0.7871 | 0.8137 |

En N₂O todas las filas guardadas están por encima de A0, y el intervalo es estrecho: el resultado apoya una abundancia libre alta respecto de esta referencia, con la resolución finita de la posterior como límite. Para NH₃ la mediana del factor también supera seis, pero el intervalo incluye 1 y se extiende por debajo de A0; además, `P(NH₃>A0)` es menor que la masa nominal del prior. Por tanto, esta corrida **no da evidencia direccional de enriquecimiento de NH₃**. La evidencia marginal de NH₃ fija tampoco favorece liberar su abundancia. Estos resultados no niegan la presencia de NH₃: cuantifican la diferencia entre los modelos especificados y la dirección de una posterior bajo un prior concreto.

En las mismas filas del modelo libre, `P(N₂O>A0 y NH₃>A0)=0.7871` y `P(al menos una>A0)=1.000` en la muestra. La probabilidad conjunta respeta la dependencia posterior; no se obtuvo multiplicando marginales. Tampoco se convierte en sigma de evidencia ni se atribuye la evidencia del modelo conjunto a cada molécula.

## Qué permiten afirmar y qué queda abierto

**Resultado condicionado:** con el binning fotónico corregido, la realización LIFE A3–1000 h, el perfil isoquímico y esta parametrización, el conjunto de datos prefiere de manera muy marcada el modelo con N₂O libre frente al mismo modelo con N₂O fija a la referencia escalar A0. La posterior completa sitúa N₂O aproximadamente 6.7 veces por encima de ese valor. Para NH₃, el factor central es alto pero la posterior es ancha, incluye valores inferiores a A0 y su contraste de evidencia no favorece liberar la abundancia. El resultado conjunto señala sobre todo que la hipótesis con ambas abundancias fijadas es inadecuada; no demuestra individualmente las dos.

La conclusión sigue siendo condicional porque el completo corregido conserva `χ²=242.88`. Con los 31 bins y 14 parámetros efectivamente libres, el dof recalculado es 17 y `χ²_red=14.287`. El archivo de POSEIDON imprime 15.18 al usar su convención histórica de 16 dof; la cifra de referencia de este informe usa el dof efectivo 17, como exige la dimensión auditada. Los `χ²_red` recalculados para N₂O fija, NH₃ fija y conjunta son 83.15, 13.65 y 78.91. El gran factor de Bayes N₂O ocurre en un contraste donde el modelo fijado tiene un ajuste extremadamente pobre; debe leerse junto con la inadecuación del modelo, los perfiles isoquímicos, los priors y la única realización de ruido diagonal. No establece por sí solo causalidad agrícola ni separación general de ExoFarm frente a toda atmósfera preagrícola.

La presión de referencia A0 es un resumen escalar de perfil vertical y no modela su variación con altura. La corrida tampoco explora varios ruidos, covarianza instrumental, química vertical variable ni incertidumbre del atlas. Para atribuir una señal a ExoFarm frente a un escenario preagrícola completo hará falta comprobar robustez a esos ingredientes y a perfiles verticales plausibles; aquí no se lanzó otro retrieval.

## Archivos y reproducción

- Estado, alcance y tres resultados: [`campaign_state.json`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a0_fixed_reference_A3_1000h_binning_corrected_20261016_relaunch_01/campaign_state.json), [`selected_scope.json`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a0_fixed_reference_A3_1000h_binning_corrected_20261016_relaunch_01/selected_scope.json), [`manifest.csv`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a0_fixed_reference_A3_1000h_binning_corrected_20261016_relaunch_01/manifest.csv).
- Informe de auditoría completo con checks, dimensiones y SHA-256: [`validation_report_20261017.json`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a0_fixed_reference_A3_1000h_binning_corrected_20261016_relaunch_01/validation_report_20261017.json).
- Momentos centrados estables, sin alterar originales: [`CSV`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a0_fixed_reference_A3_1000h_binning_corrected_20261016_relaunch_01/fixed_parameter_moments_stable_20261017.csv) y [`JSON`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a0_fixed_reference_A3_1000h_binning_corrected_20261016_relaunch_01/fixed_parameter_moments_stable_20261017.json).
- Tabla de contrastes: [`CSV`](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a3_1000h_a0_fixed_binning_corrected_2026-10-17.csv) y [`JSON`](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a3_1000h_a0_fixed_binning_corrected_2026-10-17.json).
- [Auditor](../Thermal_Emission_Spectroscopy/scripts/audit_proxima_a3_1000h_a0_fixed_binning_corrected.py), [contrato del operador](../Thermal_Emission_Spectroscopy/scripts/run_life_a0_binning_corrected.py), [implementación del operador](../Thermal_Emission_Spectroscopy/scripts/life_bin_operator_diagnostic.py), [método A0](life_proxima_a0_enrichment_methodology_2026-10-10.md) y [calibración sigma](life_proxima_loo_sigma_lin_convention_2026-10-10.md).
- Completo comparador: [`a3_1000h_binning_corrected_20261014`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1000h_binning_corrected_20261014/README.md) y su [`comparison.json`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1000h_binning_corrected_20261014/comparison/comparison.json).

La auditoría modificó únicamente metadatos de validación, tablas y sidecars derivados. Conservó intactos los productos científicos originales, los seis retrievals completos oficiales, los 36 LOO, la matriz 8/8, el completo corregido y la tentativa interrumpida del 15-oct.
