# Retrieval corregido Proxima LIFE A3 a 100 h: O2 y superficie fija (2026-09-23)

## Pregunta y alcance

Esta auditoría repite únicamente A3 a 100 h después de encontrar que los
retrievals anteriores omitían O2 y que su modo `fixed-bottom` usaba
`surface=False`, aunque el forward que generó LIFE incluye O2 y una superficie
negra explícita a 1 bar. La matriz canónica A0--A3 × {10 h, 240 h} permanece
intacta. El objetivo es obtener un posterior A3 de 100 h bajo una interfaz
forward validada antes de usarlo para comparar abundancias con A0 efectiva.

## Configuración y prueba de forward

Ejecución en Ubuntu/WSL con el entorno conda `POSEIDON`, Python
`/home/dasan/anaconda3/envs/POSEIDON/bin/python`, POSEIDON 1.4.0 y NumPy
1.26.4. Se reutiliza el dataset A3 de 100 h ya auditado: 31 bins, una
realización de ruido y errores diagonales LIFE clásico.

| Opción | Valor |
| --- | --- |
| `X_profile` | `isochem` |
| especies recuperadas | H2O, CO2, CH4, O2, O3, N2O, NH3; N2 queda como gas de fondo |
| límite superficial | `surface=True`, albedo gris cero y `log_P_surf=0` exactamente (1 bar; prior uniforme degenerado `[0,0]`) |
| errores | `error_inflation=none`; no se incluye `x_tol` |
| resolución espectral POSEIDON | `R=10000` |
| MultiNest | `N_live=800`, `evidence_tol=0.5` |
| radio de referencia | mismo prior físico del script de retrieval; libre |

`--validate-forward --setup-only` comprobó primero los priors y calculó el
forward con PT/química VULCAN A3, O2 y superficie a 1 bar. Tras rebin de
fotones a los bins LIFE, la diferencia con el forward sin ruido guardado es
RMS `0.2518 sigma` y máximo `0.8048 sigma` en 31 bins. Se adoptó como puerta
de validación RMS < `0.3 sigma` y máximo < `1 sigma`. A `R=2000` la diferencia
era RMS `1.58 sigma` y máximo `4.225 sigma`; a `R=5000`, RMS `0.5788 sigma`
y máximo `1.725 sigma`. Por tanto el retrieval se lanzó a `R=10000` para
representar la resolución de la entrada con precisión suficiente.

## Cierre de MultiNest y recuperación del posprocesamiento

El retrieval se lanzó una sola vez, PID Ubuntu `10789`, con salida separada
del retrieval legacy. El comando reproducible está en
[`launch_proxima_a3_100h_o2_fixed_surface.sh`](../Thermal_Emission_Spectroscopy/scripts/launch_proxima_a3_100h_o2_fixed_surface.sh):

```bash
python -u run_life_retrieval.py \
  --campaign proxima --scenario A3 --hours 100 --n-live 800 \
  --error-inflation none --surface-pressure-mode fixed-black \
  --include-o2 --output-tag _O2_fixedBlack1bar_noxtol --R 10000
```

MultiNest cerró normalmente: el log termina con `Sampling finished. Exiting
MultiNest`, registra 1,804,581 evaluaciones y `ln(ev)=884.333304 ± 0.244466`.
El proceso envolvente de POSEIDON después lanzó una excepción al buscar
`...-post_equal_weights.dat`; PyMultiNest había escrito el archivo de muestras
con el mismo nombre pero sin la extensión `.dat`. Por tanto, faltaban los
productos de resumen, espectro y perfiles, no el muestreo ya concluido.

La recuperación conservó la muestra original, comprobó su SHA-256
`43df7db9bffc11b00dc02f3e7ee97fa6de001d0c693128fa49f1fc3310831bc8` y creó
una copia byte a byte con la extensión que exige Analyzer. Después ejecutó
únicamente `retrieved_samples` y los escritores de POSEIDON; **no se volvió a
ejecutar MultiNest ni se hicieron nuevas evaluaciones de likelihood**. El
posprocesamiento reproducible y su modo de validación están en
[`postprocess_existing_proxima_a3_100h_o2.py`](../Thermal_Emission_Spectroscopy/scripts/postprocess_existing_proxima_a3_100h_o2.py).
El manifiesto registra los checksums, la configuración y la semilla `20260926`
usada para el subconjunto de 1,000 espectros/perfiles predictivos.

Los productos están en
`Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/`.
La validación cubrió los archivos de evidencia y puntos vivos, la muestra
equiponderada, `results`, muestras POSEIDON, espectro, P--T y `log_X`. La
muestra contiene 7,479 filas × (15 parámetros + log-likelihood), todas finitas;
hay 800 puntos vivos, 3,219 × 6 valores espectrales, 100 × 6 puntos P--T y
800 filas numéricas `log_X` (ocho especies incluyendo N2 de fondo). La copia
`.dat` y el archivo original son idénticos; no se encontró NaN/Inf.

## Resultados y contraste con A0 efectiva

El resultado corregido da `ln Z=884.33±0.24`, `chi²=79.01`, `chi²_red=4.94`
con 16 grados de libertad, `N_live=800` y 15 parámetros. El resumen posterior
central del 68 % es:

| Parámetro | q16 | Mediana | q84 |
| --- | ---: | ---: | ---: |
| `R_p_ref` (`R_⊕`) | 1.2142 | 1.2202 | 1.2266 |
| `log_N2O` | -6.2040 | -6.1476 | -6.0927 |
| `log_NH3` | -8.6586 | -8.2578 | -8.0569 |
| `log_O2` | -5.0952 | -3.3095 | -1.4248 |

La referencia efectiva calculada de los perfiles VULCAN es
`log10(N2O_A0,eff)=-6.8843` y `log10(NH3_A0,eff)=-9.9505`; A3 efectiva es
`-6.0141` y `-8.2315`, respectivamente. Con
`z=(mediana_A3-log10(X_A0,eff))/sigma68`, la variante corregida da
`z_N2O=+13.24` y `z_NH3=+5.63`; la corrida legacy de 100 h da `+4.69` y
`+3.04`. Son distancias posteriores condicionales y descriptivas. La
incertidumbre estrecha de N2O y la separación de NH3 no convierten por sí solas
el resultado en una detección: el ajuste todavía está tensionado (`chi²_red`
`4.94`) y el modelo recupera abundancias constantes frente a perfiles VULCAN
verticales.

En el mismo dataset de 31 bins, el `chi²_red` del mejor ajuste pasa de 5.27
(legacy, 18 dof) a 4.94 (interfaz corregida, 16 dof). La chi-cuadrado del
espectro mediano baja de 114.30 a 82.83 y su RMS residual baja de 1.92 a
1.63 sigma/bin. La mejora es parcial y no aísla el efecto de una sola decisión:
la variante corregida cambia a la vez O2, superficie explícita, resolución de
R=10,000 y dimensionalidad del retrieval respecto de la legacy a R=2,000.
Ambas `ln Z` se muestran como diagnósticos por corrida; **no se interpretan
como factor de Bayes** entre estas configuraciones.

## Figura, archivos y reproducibilidad

La figura nueva reúne perfiles verticales VULCAN A0/A3, posteriores legacy y
corregidas para N2O/NH3, referencias efectivas, residuos por los 31 bins y
métricas de ajuste/evidencia:

- [Figura PNG](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A3_100h_legacy_vs_o2_fixed_surface_recovery_proxima.png)
- [Figura PDF](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A3_100h_legacy_vs_o2_fixed_surface_recovery_proxima.pdf)
- [Script de figura y validación](../Thermal_Emission_Spectroscopy/scripts/plot_proxima_a3_100h_o2_surface_recovery.py)
- [Resumen numérico y checksums](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/retrieval_A3_100h_legacy_vs_o2_fixed_surface_recovery_proxima_summary.json)
- [Residuos por bin](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/retrieval_A3_100h_legacy_vs_o2_fixed_surface_recovery_proxima_residuals.csv)
- Log de lanzamiento: [`proxima_A3_100h_O2_fixedBlack1bar_noxtol.launch.log`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/proxima_A3_100h_O2_fixedBlack1bar_noxtol.launch.log)
- Muestra equiponderada original (sin extensión): `.../MultiNest_raw/proxima_A3_100h_O2_fixedBlack1bar_noxtol_proxima_A3_100h_O2_fixedBlack1bar_noxtol-post_equal_weights`

La figura fue inspeccionada visualmente. El dataset tiene ruido diagonal de
LIFEsim clásico y una realización; no contiene covarianza ni inestabilidad
instrumental. El S/N orientó la elección de 100 h, pero no sustituye esta
prueba de retrieval. La auditoría corregida queda fuera de la matriz canónica
8/8. El monitor programado se canceló después de cerrar y validar la
recuperación.
