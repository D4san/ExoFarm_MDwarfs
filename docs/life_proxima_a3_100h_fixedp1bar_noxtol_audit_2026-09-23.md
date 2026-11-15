# Auditoría Proxima A3 a 100 h con modo fixed-bottom heredado y sin x_tol (2026-09-23)

## Pregunta y clasificación

Esta corrida intermedia amplía la auditoría A3 de 10 y 240 h para comprobar cómo
evolucionan el ajuste y las posteriores bajo la misma configuración sin
inflación de errores. Las tres integraciones comparables para la figura final
son 10, 100 y 240 h, todas con `X_profile=isochem`, `N_live=800`,
`surface=False`, malla atmosférica que termina en 1 bar y sin `x_tol`.
**Corrección metodológica 2026-09-23:** `surface=False` no reproduce la
superficie negra explícita a 1 bar del forward; véase el
[diagnóstico de interfaz](life_proxima_a3_forward_swap_audit_2026-09-23.md).
El nuevo producto es una auditoría
excluida; no reabre ni modifica la matriz canónica A0--A3 × {10 h, 240 h}.

El análisis integrado de S/N motivó las 100 h como tiempo intermedio: la
proyección de plantilla completa sitúa NH3 cerca de S/N=5, mientras N2O ya
supera ese umbral mucho antes. S/N sigue siendo un diagnóstico con ruido
diagonal, no una predicción directa del posterior ni una detección.

## Dataset y procedencia

El dataset `LIFE_proxima_A3_100h.dat` se generó para esta auditoría con
`make_life_datasets.py`, usando el escalado temporal ya validado para la rama
LIFEsim clásica:

```text
sigma(t) = sigma(10 h) * sqrt(10 h / t)
```

La observación contiene 31 bins, usa una realización gaussiana de ruido con
semilla de dataset `129315834` y tiene SHA-256
`78662546181A5B74391A14B7B73AE80D879200A74DB6A4BC5338E3CE7EEE4705`. El índice
separado
[`dataset_index_A3_100h_fixedP1bar_noxtol_audit.json`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/dataset_index_A3_100h_fixedP1bar_noxtol_audit.json)
lo clasifica como auditoría y deja intacto el índice canónico. La semilla
maestra del generador es `20260923`.

La opción de observación directa no está instalada en el entorno conda POSEIDON
usado aquí; por eso se empleó el camino de escalado de sigma. El ensayo previo
de ruido directo frente a escalado encontró equivalencia numérica para
LIFEsim clásico en 1--1200 h. Esto no añade covarianza ni ruido de inestabilidad
instrumental.

## Configuración y ejecución

Entorno: Ubuntu/WSL, Python `/home/dasan/anaconda3/envs/POSEIDON/bin/python`,
POSEIDON 1.4.0. El comando ejecutado fue:

```bash
export POSEIDON_input_data=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs
export PYSYN_CDBS=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids
/home/dasan/anaconda3/envs/POSEIDON/bin/python \
  /mnt/c/Proyectos/Astro/ExoFarm_MDwarfs/Thermal_Emission_Spectroscopy/scripts/run_life_retrieval.py \
  --campaign proxima --scenario A3 --hours 100 --n-live 800 \
  --error-inflation none --surface-pressure-mode fixed-bottom \
  --output-tag _fixedP1bar_noxtol
```

El primer intento terminó antes de iniciar MultiNest porque faltaba el dataset;
no produjo resultados. Tras generar y validar la entrada se lanzó una sola
repetición, PID `7898`. El proceso terminó con el mensaje `Sampling finished.
Exiting MultiNest`; el log reporta 1,703,135 evaluaciones y
`ln(ev)=877.04567 +/- 0.24262`. Su log es
[`proxima_A3_100h_fixedP1bar_noxtol.retry1.launch.log`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/proxima_A3_100h_fixedP1bar_noxtol.retry1.launch.log)
y el PID está en
[`proxima_A3_100h_fixedP1bar_noxtol.retry1.pid`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/proxima_A3_100h_fixedP1bar_noxtol.retry1.pid).
El proceso ya no está activo y los resultados, muestras y espectro se guardaron.
El lanzador desacoplado no conservó un código de salida del shell por separado;
el cierre se valida con el marcador final de MultiNest y el conjunto íntegro de
productos descrito abajo.

## Resultados y comparación entre integraciones

Las posteriores se resumen con percentiles 16/50/84. `R_p_ref` se muestra como
mediana ± semiancho central del 68 %. Se incluyen las auditorías A3 a 10 y
240 h para contextualizar la nueva corrida; son datasets independientes.

| Integración | ln Z ± σ | chi² reducido (dof) | R_p_ref (R_E) | log_N2O mediana [q16, q84] | log_NH3 mediana [q16, q84] |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 10 h | 888.98 ± 0.21 | 1.43 (18) | 1.220 ± 0.020 | -6.495 [-6.822, -6.262] | -9.082 [-10.906, -8.128] |
| 100 h | 877.05 ± 0.24 | 5.27 (18) | 1.219 ± 0.007 | -6.485 [-6.571, -6.401] | -8.395 [-9.188, -8.165] |
| 240 h | 816.05 ± 0.25 | 13.07 (18) | 1.213 ± 0.004 | -6.393 [-6.440, -6.351] | -9.577 [-11.182, -8.739] |

El resultado de 100 h reporta `chi²=94.89`, `chi²_red=5.27`, `dof=18`,
`N_live=800`, 13 parámetros y 7,349 muestras equiponderadas. Los estimadores
de abundancia coinciden con el resumen POSEIDON a la precisión impresa:
`log_N2O=-6.48 (+0.08/-0.09)` y `log_NH3=-8.40 (+0.23/-0.79)`.

## Contraste con las referencias verticales

La referencia A0 efectiva ponderada en presión es
`log10(N2O_A0,eff)=-6.884` y `log10(NH3_A0,eff)=-9.951`. Para A3, el mismo
promedio del perfil VULCAN da `log10(N2O_A3,eff)=-6.014` y
`log10(NH3_A3,eff)=-8.232`. La señal impuesta por A3, por tanto, parte de
perfiles verticales que el retrieval `isochem` sólo puede representar con una
abundancia constante.

Se usa la distancia firmada descriptiva
`z=(mediana_A3-log10(X_A0,eff))/sigma68`, con
`sigma68=(q84-q16)/2` de la posterior isquímica:

| Tiempo | z_N2O | z_NH3 |
| ---: | ---: | ---: |
| 10 h | +1.39 | +0.62 |
| 100 h | +4.69 | +3.04 |
| 240 h | +11.11 | +0.31 |

A 100 h las medianas son `log_N2O=-6.485` y `log_NH3=-8.395`. Sus z altos
respecto de A0 describen la separación de las posteriores bajo este modelo;
no son detecciones. En particular, `chi²_red=5.27` evidencia tensión entre
los datos y el modelo a errores sin inflar. A 240 h la aparente separación de
N2O aumenta a 11.11 sigma mientras `chi²_red=13.07`; la precisión estrecha no
es interpretable como una medición fiable. La fila de 10 h tiene un ajuste más
razonable (`chi²_red=1.43`) y posteriores más amplias.

Los valores `ln Z` se reportan para cada dataset, pero no se comparan entre
integraciones como factor de Bayes: cambian la exposición, las incertidumbres
y la realización de ruido. La figura conserva esta advertencia junto a los
valores de ajuste.

## Integridad, figura y reproducibilidad

El conjunto de 100 h contiene resultados, 7,349 muestras × 13 parámetros,
espectro recuperado de 3,219 × 6, perfil P--T de 100 × 6, siete bloques
log-X de 100 niveles y los archivos MultiNest de evidencia, muestras
equiponderadas, puntos vivos y resumen. El resultado declara 800 puntos vivos;
MultiNest finalizó limpiamente. Se comprobaron los textos y las tablas
numéricas de resultados, muestras, espectro, P--T, log-X y archivos MultiNest:
no hay NaN/Inf. Los parámetros `x_tol` y `log_P_surf` no aparecen entre las 13
columnas recuperadas, conforme a la configuración fija.

La comparación visual 10/100/240 h muestra los perfiles verticales VULCAN A0 y
A3, los perfiles posteriores isochem, sus referencias efectivas y los z
firmados:

- [Figura PNG](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A3_audit_profiles_posteriors_10_100_240h_proxima.png)
- [Figura PDF](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A3_audit_profiles_posteriors_10_100_240h_proxima.pdf)
- Script reproducible: [`plot_proxima_a3_10_100_240h_audit.py`](../Thermal_Emission_Spectroscopy/scripts/plot_proxima_a3_10_100_240h_audit.py)

La figura se inspeccionó visualmente. Los perfiles VULCAN se recortan a
`X=10^-30` sólo para permitir la representación logarítmica; los retrievals
usan sigma diagonal y una realización por integración. El desajuste perfil
vertical/isochem y los chi-cuadrados altos impiden una afirmación formal de
detección de N2O o NH3. La matriz canónica A0--A3 × {10 h, 240 h} permanece
intacta.

## Fuentes

- [Informe de S/N LIFE integrado](life_classic_snr_integrated_2026-09-22.md).
- [Auditoría A3 a 10 y 240 h](life_proxima_a3_10_240h_fixedp1bar_noxtol_audit_2026-09-23.md).
- [Análisis de S/N integrado LIFE](life_classic_snr_integrated_2026-09-22.md).
- `Thermal_Emission_Spectroscopy/scripts/make_life_datasets.py`.
- `Thermal_Emission_Spectroscopy/scripts/run_life_retrieval.py`.
- `Thermal_Emission_Spectroscopy/scripts/plot_proxima_a3_10_100_240h_audit.py`.
- `docs/life_proxima_lifesim_noise_scaling_2026-08-31.md`.
