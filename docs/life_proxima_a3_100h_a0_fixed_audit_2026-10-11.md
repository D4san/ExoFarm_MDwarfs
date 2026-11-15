# LIFE Proxima A3–100 h: evidencia frente a A0 fija y auditoría de cierre

**Limitación identificada posteriormente, 2026-10-14:** la integración del
generador y la likelihood difiere (bordes y ponderación). El mismo forward
verdadero discrepa RMS0.925σ/máximo2.842σ en el dataset100 h. La aceptación
técnica y los valores históricos se preservan; la interpretación física
requiere advertir/controlar este sesgo instrumental. No se reauditaron ni
modificaron esos productos en este diagnóstico.
[Evidencia independiente](life_proxima_nh3_1000h_interface_diagnosis_2026-10-14.md).

Fecha: 2026-10-11. Campaña: `a0_fixed_reference_20261010`.

## Resultado y estado de aceptación

Las tres corridas autorizadas terminaron con código 0. La última finalizó
el 2026-10-11 a las **16:35:01 UTC, 11:35:01 COT**. La auditoría independiente
completó el examen del modelo completo oficial y las tres restricciones.
Los productos primarios, evidencias, priors, valores fijados y hashes pasan.
La **finitud estricta de todos los resúmenes MultiNest falla** en dos modelos:
aparecen `NaN` exclusivamente en desviaciones derivadas de coordenadas fijas.
La primera auditoría dejó `REQUIRES_REVIEW` y una tabla provisional.
**Cierre autorizado por el usuario el 2026-10-11:** aceptación
`ACCEPTED_WITH_FIXED_MOMENT_SALVEDAD`, estado de campaña
`VALIDATED_COMPLETE_WITH_SALVEDAD`. La finitud estricta original sigue
fallando únicamente en esos momentos auxiliares; se preservan sus ocho NaN.
Se generó un resumen auxiliar estable de siete coordenadas fijas, con
desviación cero en muestras ponderadas/de igual peso. Los 52 hashes y
las tres filas de evidencia/sigma coinciden exactamente con la revisión.
Monitor eliminado tras verificar el cierre; confirmación de la aplicación en
[registro de cierre](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a0_fixed_reference_20261010/closure_record_20261011.json).
No se repitió ningún retrieval.

Esta separación entre fin del muestreo y aceptación sigue el
[procedimiento A0](life_proxima_a0_enrichment_methodology_2026-10-10.md).
La decisión explícita se guarda en
[acceptance_decision_20261011.json](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a0_fixed_reference_20261010/acceptance_decision_20261011.json),
ligada a los hashes de la auditoría anterior. La excepción no acepta NaN
de parámetros libres, evidencias o productos primarios.
[Síntesis de las capas y respuesta ExoFarm/LIFE](life_proxima_exofarm_retrieval_layers_synthesis_2026-10-11.md).

## Tabla final de evidencia, aceptada con salvedad

Cada fila compara el completo oficial libre con una restricción aplicada
al **mismo dataset A3–100 h**. Las opacidades N₂O/NH₃ están presentes.
Cuando se fija una sola molécula, la otra continúa libre.

| Restricción a A0 efectiva | ln B ± error numérico | σ calibrado bilateral |
| --- | ---: | ---: |
| N₂O fija; NH₃ libre | +29.440 ± 0.340 | 7.96 |
| NH₃ fija; N₂O libre | +1.170 ± 0.342 | 2.12 |
| N₂O y NH₃ fijas | +31.103 ± 0.336 | 8.17 |

[CSV final de tres filas, precisión completa](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a0_lnB_sigma_lin_2026-10-11.csv) ·
[JSON aceptado con salvedad](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a0_lnB_sigma_lin_2026-10-11.json) ·
[auditoría detallada, hashes e incidencias](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a0_fixed_reference_20261010/validation_report_20261011.json).

Las evidencias precisas, verificadas contra los resultados POSEIDON
redondeados y la última fila de `summary.txt`, son:

| Modelo | ln Z | Error numérico ln Z |
| --- | ---: | ---: |
| Completo oficial | 884.3333041378268 | 0.24446554153470446 |
| N₂O fija | 854.8931804139012 | 0.23584664829376045 |
| NH₃ fija | 883.1629039835424 | 0.23919838654023615 |
| Ambas fijas | 853.2306013393314 | 0.23066356667120869 |

## Matemática y convención de reporte

\[
B=\frac{Z_{\rm libre}(D)}{Z_{\rm A0\ fija}(D)},\qquad
\ln B=\ln Z_{\rm libre}-\ln Z_{\rm A0\ fija},\qquad
\delta_{\rm num}(\ln B)=\sqrt{\delta_{\rm libre}^2+\delta_{\rm fija}^2}.
\]

La cuadratura supone errores numéricos independientes entre ejecuciones.
Las tres filas comparten la misma evidencia completa: sus errores están
correlacionados por ese término y las filas no se combinan como mediciones
independientes. El error numérico tampoco mide incertidumbre de perfil,
prior, referencia A0 o ruido instrumental.

Se reutiliza sin cambios
[`report_proxima_loo_lin_sigma.py`](../Thermal_Emission_Spectroscopy/scripts/report_proxima_loo_lin_sigma.py)
y la [convención documentada](life_proxima_loo_sigma_lin_convention_2026-10-10.md):

\[
y-\ln y=1+\ln B,\quad y>1,\qquad
p=e^{-y}=\operatorname{erfc}(\sigma_{\rm cal}/\sqrt2).
\]

Para `ln B ≤ 0`, sigma es `N/A`. Esta reconstrucción implementa la
calibración bilateral de las ecuaciones (8)–(9) de
[Benneke & Seager (2013)](https://arxiv.org/pdf/1306.6325#page=5), citada por
[Lin et al. (2021), §5.2 y tabla 2](https://arxiv.org/pdf/2105.09319#page=10).
Igualar la cota constituye la convención histórica elegida, sin verificar el
código privado de Lin. **σ calibrado es auxiliar; ln B es la métrica principal.**
La conversión no proporciona un p-value frecuentista medido ni una probabilidad
de agricultura. Los controles de calibración publicados, la reconstrucción
de las ecuaciones y los casos límite pasan y quedan en el JSON de auditoría.

## Contrato y controles independientes

Solo se seleccionaron `A3_100h_A0_N2O`, `A3_100h_A0_NH3` y
`A3_100h_A0_joint`. Selección, manifiesto y estado coinciden exactamente;
las otras quince candidatas quedan como historial sin ejecución.

Dataset: `LIFE_proxima_A3_100h.dat`, 31 bins, seed `129315834`, flujo observado
`Fp` en W m⁻² m⁻¹. SHA-256:
`78662546181a5b74391a14b7b73ae80d879200a74db6a4bc5338e3ce7eee4705`.
El resultado completo coincide con su hash congelado
`37aca3cd91fdc115323706aa746865e014b6656e6eb77eabd247592f311b54c2`.
Se verificó el perfil VULCAN de A0, su referencia congelada y el código
del supervisor contra los hashes de lanzamiento.

La referencia escalar es el promedio VULCAN ponderado en presión entre
`5×10⁻⁸` y `1 bar`: `log₁₀ X_N2O = −6.884325289636784` y
`log₁₀ X_NH3 = −9.950526295665036`. Los priors restantes, las siete opacidades,
la likelihood diagonal, PT Madhu, isochem, R = 10000, 3.8–19 μm,
N_live = 800, tolerancia de evidencia 0.5 y superficie negra a 1 bar son
idénticos a sus controles completos. Sin inflación de errores.

Se comprobaron todas las coordenadas físicas contra los priors en la
posterior exportada, posterior MultiNest de igual peso, posterior ponderada,
traza de puntos eliminados y puntos vivos físicos. Los valores fijados son
constantes en todas esas muestras. Las 15 coordenadas declaradas se conservan:
14 libres en el completo, 13/13/12 en las restricciones.

| Producto/control | Completo | N₂O fija | NH₃ fija | Ambas fijas |
| --- | ---: | ---: | ---: | ---: |
| Muestras de igual peso, cotejadas con exportación | 7479 | 6692 | 6152 | 6021 |
| Espectro: filas × columnas | 16094 × 6 | 16094 × 6 | 16094 × 6 | 16094 × 6 |
| P–T: filas × columnas | 100 × 6 | 100 × 6 | 100 × 6 | 100 × 6 |
| log-X: filas, ocho especies | 800 | 800 | 800 | 800 |
| N_live final | 800 | 800 | 800 | 800 |
| Finitud estricta de resúmenes derivados | PASS | FAIL | PASS | FAIL |

Espectro/PT/log-X tienen mallas monótonas, cuantiles ordenados y valores
finitos. Cada perfil fijo mantiene el valor de referencia en sus 100 niveles
y cinco cuantiles. Se verificaron los ocho tipos de archivo MultiNest,
los contadores `ev/resume`, los marcadores de fin de seis ranks y los códigos 0.
No hay patrones fatales en los logs de ejecución. Comprobación de procesos
al cierre: supervisor PID 758 y MPI de esta campaña ya inactivos.

## Incidencia exacta y diagnóstico numérico

El primer control estricto produjo:

```text
ValueError: empty or non-finite numeric row at .../A3_100h_A0_N2O/.../MultiNest_raw/proxima_A3_100h_A0ref_N2O_v1-summary.txt:2
```

Se localizaron ocho apariciones `NaN`, en cuatro archivos originales:

| Run | Archivo | Línea / columna | Cantidad |
| --- | --- | --- | --- |
| N₂O fija | `proxima_A3_100h_A0ref_N2O_v1-summary.txt` | 2 / 28 | desviación log_N2O |
| N₂O fija | `proxima_A3_100h_A0ref_N2O_v1-stats.dat` | 16 / 3 | desviación log_N2O |
| Ambas fijas | `proxima_A3_100h_A0ref_joint_v1-summary.txt` | 1 y 2 / 28 y 29 | desviaciones log_N2O/log_NH3 |
| Ambas fijas | `proxima_A3_100h_A0ref_joint_v1-stats.dat` | 16 y 17 / 3 | desviaciones log_N2O/log_NH3 |

Las medias, valores ML/MAP y evidencias son finitos. Las muestras primarias
tienen mínimo = máximo = valor congelado. El cálculo centrado independiente
`fsum((x − x_A0)²)/N` da **exactamente cero** para todas las coordenadas fijas.
Incluso el resumen NH₃ individual, finito, imprime una dispersión residual
muy pequeña para una coordenada constante; no se usa para inferencia.

**Inferencia diagnóstica:** el patrón es compatible con cancelación numérica
al resumir una coordenada de varianza cero. La implementación exacta que
originó el `NaN` no se ha inspeccionado; esa causa permanece por confirmar.
La evidencia no usa esas desviaciones derivadas y se cotejó entre tres
representaciones. Se mantienen los originales y sus hashes; sus `NaN`
permanecen intactos y no se repite muestreo. La excepción se aceptó
exclusivamente tras la autorización del usuario, con control independiente.

**Decisión resuelta:** el usuario autorizó el cierre con salvedad explícita.
El [CSV auxiliar](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a0_fixed_reference_20261010/fixed_parameter_moments_stable_20261011.csv)
y su [JSON](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a0_fixed_reference_20261010/fixed_parameter_moments_stable_20261011.json)
usan segundos momentos centrados y sumas estables; incluyen también
log_P_surf fijo. La auditoría anterior se conserva byte a byte como
[snapshot previo](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a0_fixed_reference_20261010/validation_report_20261011_pre_acceptance.json),
y las tablas provisionales quedan como historial. `strict_finiteness_pass`
sigue en false; la excepción es acotada a las incidencias revisadas.

## Interpretación científica condicionada

**Resultados directos:** el completo se prefiere fuertemente a N₂O fijado
en A0 efectiva. La preferencia frente a NH₃ fija es mucho menor. La
restricción conjunta es fuertemente desfavorecida; su sigma pertenece a la
hipótesis conjunta y no se asigna por separado a cada molécula.

**Interpretación del proyecto:** la combinación con la posterior completa
apoya enriquecimiento de N₂O respecto a la referencia escalar: mediana
`5.45 × A0`, intervalo 95 % `[4.15, 6.97]`, sin muestras bajo A0 en 7479 filas.
Para NH₃, `94.866 %` está sobre A0 pero el intervalo 95 % cruza la referencia
y el prior nominal ya asigna `81.368 %` por encima. `ln B = 1.170` mantiene
la conclusión prudente de apoyo limitado al contraste libre/A0. La ganancia
del contraste conjunto está dominada por N₂O; las evidencias no se suman.

El completo conserva tensión de ajuste: χ² impreso `79.01`, χ²_red
histórico POSEIDON `4.94` con 16 dof declarados. Con 14 coordenadas realmente
libres, el diagnóstico actualizado es `79.01/17 ≈ 4.65`. Los modelos
restringidos dan aproximadamente `8.11/4.86/8.09` con 18/18/19 dof efectivos,
calculados desde χ² redondeado. Una preferencia relativa alta convive con
este desajuste absoluto. Los perfiles isoquímicos, PT, degeneraciones, ruido
diagonal de una realización y la referencia A0 escalar limitan una afirmación
física de detección o atribución agrícola.

## Reproducción y preservación

Auditor independiente:
[`audit_proxima_a0_fixed_reference.py`](../Thermal_Emission_Spectroscopy/scripts/audit_proxima_a0_fixed_reference.py).
Ejecución ligera, sin importar POSEIDON ni generar likelihoods:

```text
python Thermal_Emission_Spectroscopy/scripts/audit_proxima_a0_fixed_reference.py --accept --accept-fixed-moment-salvedad
```

`--record-review` registra la incidencia manteniendo códigos/estado de
muestreo. `--accept` solo se rechaza con los originales actuales; la opción
explícita `--accept-fixed-moment-salvedad` comprueba los hashes y momentos
fijos revisados antes de aceptar la excepción autorizada. Un diagnóstico
estricto posterior guarda un informe separado sin sobrescribir la aceptación.
Las tablas provisionales y el informe de auditoría anterior son
salidas derivadas nuevas. Los seis completos oficiales, las 36 ablaciones
LOO, la matriz legacy 8/8, los logs y el scratch se preservan.

Verificación del auditor: diez controles de regresión PASS en
[`test_a0_independent_audit.py`](../Thermal_Emission_Spectroscopy/scripts/test_a0_independent_audit.py),
tres controles del contrato fijo PASS (13 en total) y compilación PASS. La prueba negativa
`--accept` produjo el rechazo esperado y dejó el ledger idéntico por SHA-256.
Se recalcularon los hashes de **52 archivos científicos**, sin modificaciones;
CSV/JSON tienen exactamente tres filas y los enlaces locales del informe y
README de campaña resuelven. La primera prueba de fixtures falló por permisos
del directorio temporal del sandbox Windows; al ubicarlos dentro del workspace,
los seis controles iniciales pasaron. El cierre añade cuatro controles de la
excepción: aceptación con dispersión cero y rechazo por hash cambiado,
dispersión no nula o incidencia nueva. La salvedad está aceptada; no se
elimina el registro de la incidencia original.
