# Validación científica de la rama LIFEsim clásica de la Etapa III

**Fecha de cierre documental:** 2026-08-30  
**Alcance:** POSEIDON en emisión térmica + LIFEsim clásico + diagnósticos de
señal/SNR + retrievals de emisión con incertidumbres diagonales.  
**Estado:** **rama clásica validada como experimento científico de referencia**;
no equivale todavía a la rama instrumental completa de LIFE.

La reconstrucción detallada de datos, ecuaciones, configuraciones, productos y
retrievals se documenta en la
[metodología completa de la Etapa III clásica](life_stage_iii_classic_methodology_2026-08-30.md).
La lectura conjunta de resultados, tablas y figuras está en el
[informe integrado de la Etapa III](life_stage_iii_integrated_methodology_results_2026-08-30.md).

## Qué queda validado

La cadena ejecutada es:

```text
perfiles PT/química VULCAN
    → forward de emisión POSEIDON
    → flujo planetario observado Fp
    → binning y ruido astrofísico/fotónico de LIFEsim clásico
    → contrafactuales moleculares y SNR
    → datasets sintéticos con una semilla registrada
    → retrievals POSEIDON con sigma diagonal
```

La interfaz física fue comprobada mediante: geometría de emisión directa,
conversión energía--fotones, control de cuerpo negro, comparación de opacidades,
calibración de la escena Proxima contra LIFE X y escalado `sqrt(t)`. La
procedencia, los cálculos y las validaciones numéricas están detallados en la
[auditoría científica](stage_iii_scientific_audit_2026-07-25.md), el
[informe Tierra--Sol](life_earth_sun_10pc_interface_snr_2026-07-22.md) y la
[bitácora Proxima](life_proxima_b_branch_bitacora_2026-07-22.md).

La matriz canónica de retrievals de la rama clásica contiene **8 corridas**:
Proxima A0--A3 por `{10 h, 240 h}`. Su índice de datos es
[`dataset_index.json`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/dataset_index.json)
y el resumen cuantitativo es
[`retrieval_separation_from_A0.csv`](../Thermal_Emission_Spectroscopy/outputs/_comparison/retrieval_separation_from_A0.csv).

## Clasificación de los productos de 1200 h

Los cuatro datasets Proxima de 1200 h y el retrieval A3--1200 h se clasifican
como **evidencia de auditoría/piloto excluida de la matriz canónica**.

- No son residuos sin relación: fueron generados con la misma cadena física y
  ayudaron a revelar que, a S/N muy alto, el desajuste entre el perfil VULCAN y
  un modelo de retrieval demasiado rígido domina la verosimilitud.
- No son resultados canónicos: la matriz final fue reducida a 8 corridas de
  10/240 h; `dataset_index.json` enumera únicamente esas ocho.
- No deben entrar en tablas de separación, conteos de completitud ni claims de
  detectabilidad. Se conservan para reconstruir los pilotos y auditar las
  decisiones sobre PT, `Piette20` y el prior de `R_p_ref`.

El inventario exacto y la regla de uso están junto a los productos en
[`outputs/life_proxima_b_earthlike_v1/README.md`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/README.md).

## Resultado científico defendible

### Tierra--Sol a 10 pc

Con el benchmark `earth_20260615_pre_n2o_correction`, la señal agrícola queda
por debajo del ruido astrofísico/fotónico del escenario LIFE clásico de 2 m.
N2O es el observable agrícola dominante; su banda de 7.8 micras supera a la de
17 micras en este caso, mientras NH3 permanece muy por debajo del umbral. Este
resultado valida la interfaz y muestra que un gemelo solar a 10 pc no es un
objetivo favorable bajo esta configuración. No representa todavía la matriz
Tierra--Sol con las condiciones de frontera de N2O corregidas.

### Análogo terrestre bajo Proxima

La rama Proxima usa una SED MUSCLES trazada, fotoquímica VULCAN A0--A3
convergida (`end_case=1`), condiciones de frontera corregidas y PT/Kzz
terrestre controlado. En el diagnóstico clásico, la cercanía de 1.30 pc eleva
la observabilidad de A3: N2O alcanza S/N de banda 5 en aproximadamente 11 h en
17 micras y 32 h en 7.8 micras. Esto demuestra una fuerte dependencia con la
selección de objetivo; no demuestra que la atmósfera real de Proxima b sea
terrestre ni agrícola.

En los retrievals canónicos, A3 a 240 h recupera N2O como una medición y excluye
la referencia preagrícola efectiva —el promedio columnar ponderado en presión
del perfil A0— a **3.14 sigma**.
A1 y A2 devuelven límites superiores, no mediciones, y NH3 no es discriminante.
Por ello no es válido extrapolar para A1/A2 un número de campañas a partir de
sus posteriores actuales. El retrieval es más conservador que el SNR
contrafactual porque ajusta simultáneamente PT, radio, presión superficial y
seis abundancias.

## Límites obligatorios

Todo uso de estos resultados debe declarar conjuntamente:

1. Se usó **LIFEsim clásico**, con fuga estelar, zodi/exozodi y ruido fotónico;
   no se modeló aún la inestabilidad instrumental completa.
2. Las incertidumbres de los retrievals son **diagonales**. No existe todavía
   una covarianza LIFEsimMC/PHRINGE propagada en la likelihood.
3. Hay **una realización de ruido por dataset**. No se han medido tasas de
   falsos positivos/negativos mediante múltiples semillas.
4. No se ejecutaron aún comparaciones de evidencia entre modelos con/sin N2O o
   NH3. Un posterior restringido no debe denominarse detección molecular formal.
5. El truth VULCAN tiene perfiles verticales; el retrieval usa abundancias
   isoquímicas y un PT paramétrico. `x_tol` absorbe parte de ese desajuste.
6. Proxima es un análogo terrestre controlado y Tierra--Sol conserva la
   etiqueta precorrección de N2O.

## Frontera de trabajo futuro

La siguiente rama científica es **LIFEsimMC + PHRINGE**. Debe congelar la
configuración instrumental, generar y preservar la covarianza, registrar
semillas, probar una likelihood correlacionada o whitening reproducible y
repetir los casos mínimos que determinen si el resultado A3 sobrevive a las
inestabilidades instrumentales. Después deben añadirse varias realizaciones de
ruido y comparaciones con/sin molécula.

Hasta entonces, la conclusión correcta es: **la rama clásica está validada como
benchmark y cota optimista de observabilidad; la detectabilidad instrumental
completa de LIFE permanece abierta**.
