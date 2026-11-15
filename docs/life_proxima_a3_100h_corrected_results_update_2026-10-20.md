# Actualización A3–100 h: binning corregido, evidencia y enriquecimiento

Fecha: 2026-10-20, America/Bogota. Análisis ejecutado; sin nuevos retrievals.
El «A100» indicado por el usuario se identifica como **A3–100 h**, campaña
completa del 17-oct continuada con MPI14 el 18-oct y dos omisiones del 19-oct,
cerradas y auditadas el 20-oct.

## Fuentes y aceptación

- [Auditoría primaria](life_proxima_a3_100h_corrected_binning_molecular_ablation_2026-10-19.md): baseline y dos ablaciones PASS.
- [Script de esta actualización](../Thermal_Emission_Spectroscopy/scripts/analyse_proxima_a3_100h_corrected_update.py).
- [Resumen y hashes](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/a3_100h_corrected_update_20261020/summary.json).
- [Comparación de posteriores y P–T](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/a3_100h_corrected_update_20261020/posterior_PT_comparison.png).

Se verificaron los hashes de productos contra la auditoría, las muestras
exportadas contra MultiNest de peso igual, finitud/dimensiones, límites de
prior, dataset común y evidencias exactas frente a la tabla auditada.
El nuevo resultado completo tiene 7268 muestras, 15
coordenadas declaradas y 14 libres; cada omisión tiene 13 libres.

## 1. Qué cambió y qué puede compararse

La realización observada es idéntica (31 canales; seed 129315834; SHA-256
`78662546181a5b74391a14b7b73ae80d879200a74db6a4bc5338e3ce7eee4705`).
La repetición corrigió la integración fotónica y cambió la rejilla nativa
de 3.8–19 a 3–20 μm. Los bordes de los canales caben en ambos dominios;
la ampliación sigue siendo un cambio de discretización. Las diferencias
histórico/corregido no aíslan exclusivamente el operador.

La evidencia completa pasa de 884.333304 a
894.331224; Δln Z =
9.997919 es sensibilidad metodológica,
no evidencia molecular. Las comparaciones moleculares nuevas sí emparejan
operador, rejilla, priors y dato dentro de cada pareja.

## 2. Evidencia de presencia molecular

| Especie | ln B histórico | ln B corregido | Sigma calibrada corregida |
|---|---:|---:|---:|
| N2O | 65.549528 ± 0.340609 | 84.660508 ± 0.346532 | 13.217 |
| NH3 | 1.506182 ± 0.342110 | 2.748991 ± 0.344630 | 2.853 |

N2O mantiene una preferencia fuerte por su inclusión. El valor central de NH3
pasa de apoyo débil a **moderado** (ln B=2.749, frente al umbral orientativo
2.5), cerca de esa frontera respecto del error numérico de 0.345.
La calibración es auxiliar: 2.853 sigma no equivale a una detección
frecuentista de 3 sigma ni a una probabilidad de origen agrícola.

## 3. Abundancias respecto de A1

| Molécula | Histórico: mediana [95 %] X/A1 | Corregido: mediana [95 %] X/A1 | Anchura 95 % (dex) |
|---|---:|---:|---:|
| N2O | 3.856 [2.935, 4.930] | 4.145 [3.238, 5.176] | 0.225 → 0.204 |
| NH3 | 11.145 [0.027, 23.837] | 13.630 [2.572, 25.377] | 2.946 → 0.994 |

El intervalo central del 95 % de NH3 queda ahora completamente por encima
de A1: el cambio relevante afecta especialmente a su cola inferior.
La concentración central sigue favoreciendo abundancias elevadas; esto
mejora la precisión del enriquecimiento condicionado al modelo.
Las medianas cambian mucho menos que las colas: +0.031 dex para N2O y
+0.087 dex para NH3. La anchura del intervalo NH3 pasa de 2.946 a 0.994 dex.
El control respecto de la referencia efectiva A3 también se conserva en
`posterior_regions.csv`; esta referencia comprime un perfil vertical y no
es un parámetro isoquímico verdadero que el retrieval deba recuperar sin sesgo.

## 4. Probabilidades y actualización de odds

| Molécula | Umbral | P(X ≥ referencia) | K nominal | ln K nominal |
|---|---|---:|---:|---:|
| N2O | A0 | ≈100 % | — | — |
| N2O | A1 | ≈100 % | — | — |
| NH3 | A0 | 99.1332 % | 26.1871 | 3.2653 |
| NH3 | A1 | 98.6654 % | 23.9914 | 3.1777 |

La probabilidad conjunta ≥ A1 es 98.6654 %,
con K nominal 113.924210 y ln K 4.735533.
Coincide con la marginal NH3 porque todas las muestras N2O superan A1.
Los K son cambios de odds de regiones, no los contrastes con molécula
omitida ni con abundancia A0 fija. Se conservan como nominales bajo priors
independientes log-uniformes [-12,-1]; validación del prior efectivo pendiente.
Probabilidades extremas se presentan como ≈100 %; no se infieren K infinitos.

## 5. Adecuación del ajuste y denominador de chi-cuadrado

El resultado nativo reporta χ²=79.01 →
57.19, con χ² reducido impreso
4.94 → 3.57.
POSEIDON imprime 16 grados de libertad (31 menos 15 coordenadas declaradas).
Una coordenada está fija; contando 14 parámetros libres, el denominador
efectivo es 17 y el χ² reducido nuevo vale
3.3641. Ambas convenciones se guardan;
el ajuste sigue mostrando una discrepancia importante con el ruido asumido.

La auditoría original reconstruyó χ² multiplicando el χ² reducido ya
redondeado por sus grados de libertad. Aquí se utiliza el χ² explícito
del archivo de resultados (p.ej. 57.19 frente al reconstruido 57.12).
La diferencia es de redondeo y no altera la conclusión científica. No se
modifican productos ni auditorías originales.

## 6. Alcance de las actualizaciones

- La tabla vigente de los dos gases reemplaza solo A3–100 h por las parejas
  corregidas. Las demás exposiciones/escenarios conservan fuente histórica
  y se etiquetan explícitamente; no forman una serie corregida homogénea.
- Se actualizan las tres regiones A1 de A3–100 h en la tabla vigente de regiones.
- Las omisiones corregidas de H2O, CO2, CH4 y O3 no están disponibles.
- Las tres restricciones **A0 fija de A3–100 h con el operador nuevo no están
  disponibles**. Sus ln B históricos 29.440/1.170/31.103 y probabilidades
  condicionales históricas no se transfieren a este baseline.
- Las omisiones de una molécula y su fijación no nula en A0 plantean
  contrafactuales diferentes. Las posteriores de la especie retenida en una
  omisión se guardan separadas como sensibilidades condicionales.
- La rama A3–1000 h sigue separada y no se actualiza con estos datos.
- El manuscrito abierto no se modifica: la redacción continúa acordándose
  en el chat. Los CSV históricos y las figuras anteriores se preservan.

## 7. Interpretación actualizada

En la realización A3–100 h, el resultado corregido sostiene una preferencia
fuerte por N2O y moderada por NH3. La posterior completa sitúa ambas
abundancias por encima de A1 con aproximadamente 98.67 % de probabilidad
conjunta; los intervalos centrales del 95 % de ambas superan ese benchmark.
Esto fortalece la inferencia de enriquecimiento respecto de la versión
histórica, particularmente en NH3. La adecuación global, la aproximación
isoquímica, la realización única y el prior efectivo siguen limitando la
interpretación. No se calcula una probabilidad causal de ExoFarm.

**Cambios para el borrador acordado en chat:** sustituir las dos filas de
evidencia molecular A3–100 h; actualizar las probabilidades sobre A0/A1,
los K nominales, los intervalos/dex y la conclusión de NH3. La frase sobre
su intervalo del 95 % cruzando A0 o A1 corresponde al operador histórico:
el intervalo corregido ya queda por encima de ambas referencias. Retirar de
la conclusión corregida las evidencias de A0 fija antiguas y señalar esa
comparación como pendiente. Las cifras del S/N forward pertenecen a otra
etapa y no se recalculan mediante el cambio de una posterior.

## Reproducción

```text
.venv/Scripts/python.exe Thermal_Emission_Spectroscopy/scripts/analyse_proxima_a3_100h_corrected_update.py
```

Tablas legibles: [evidencia histórica/corregida](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/a3_100h_corrected_update_20261020/molecular_evidence.csv),
[regiones marginales](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/a3_100h_corrected_update_20261020/posterior_regions.csv),
[regiones conjuntas](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/a3_100h_corrected_update_20261020/joint_regions.csv),
[parámetros](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/a3_100h_corrected_update_20261020/parameter_comparison.csv),
[matriz vigente N2O/NH3](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/a3_100h_corrected_update_20261020/current_nitrogen_loo.csv) y
[regiones A1 vigentes](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/a3_100h_corrected_update_20261020/current_a1_regions.csv).
