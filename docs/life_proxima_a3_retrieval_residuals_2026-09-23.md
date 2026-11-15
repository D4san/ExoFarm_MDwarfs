# Residuos espectrales del retrieval LIFE Proxima A3, 10/100/240 h (2026-09-23)

## Pregunta y alcance

Esta auditoría comprueba por qué las posteriores de A3 con `X_profile=isochem`,
`N_live=800`, malla hasta 1 bar con `surface=False` y
`error_inflation=none` se estrechan
mientras el ajuste empeora con las horas. Reutiliza los tres datasets y sus
productos POSEIDON/MultiNest; no ejecuta retrievals nuevos ni modifica la matriz
canónica A0--A3 × {10 h, 240 h}. La pregunta científica posterior sigue siendo
cuándo el espectro A3 permite distinguir el incremento de N2O/NH3 sobre A0.

## Cálculo reproducible

El script
[`audit_proxima_a3_retrieval_residuals.py`](../Thermal_Emission_Spectroscopy/scripts/audit_proxima_a3_retrieval_residuals.py)
lee el [forward A3 sin ruido](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/forward_emission/A3_emission.npz),
los tres datasets `LIFE_proxima_A3_{10,100,240}h.dat`, las medianas espectrales
posteriores y los resúmenes POSEIDON. Integra la densidad de **fotones** sobre
los 31 bins LIFE y convierte de nuevo a `Fp` en `W m^-2 m^-1`, igual que el
generador de datos. La reproducción del producto binado A3 guardado tiene error
relativo máximo `2.28e-14`; el redondeo de centros en los `.dat` alcanza
`4.60e-6 µm` y se usan los centros originales del producto LIFE.

Para cada bin `k` y tiempo `t` se calcularon, con la `sigma` diagonal del
dataset, tres cantidades distintas:

```text
r_obs,k   = (Fp_obs,k - Fp_med,k) / sigma_k
r_model,k = (Fp_A3_true,k - Fp_med,k) / sigma_k
r_noise,k = (Fp_obs,k - Fp_A3_true,k) / sigma_k
r_obs,k = r_model,k + r_noise,k
```

`Fp_med` es la **mediana puntual del espectro posterior** exportada por
POSEIDON; no es necesariamente el espectro del vector de parámetros mediano ni
el mejor ajuste. Por eso se conserva por separado el `chi²` del mejor ajuste
reportado por POSEIDON. Los cuadrados de `r_model` y `r_noise` tampoco se suman
directamente al `chi²` observado: existe un término cruzado.

## Resultados directos

| Tiempo | chi² mejor ajuste / 18 dof | chi² espectro mediano / 31 bins | Σ r_noise² | Σ r_model² | Bins con abs(r_obs)>3 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 10 h | 25.81 / 1.43 | 33.64 | 31.09 | 32.47 | 0 |
| 100 h | 94.89 / 5.27 | 114.31 | 42.36 | 113.60 | 3 |
| 240 h | 235.24 / 13.07 | 238.86 | 27.63 | 230.27 | 9 |

La realización de ruido de 100 h tiene una desviación cuadrática total algo
mayor que las otras (`42.36` frente a 31 bins), pero el desajuste entre el
forward A3 sin ruido y la mediana recuperada es mucho mayor a 100 y 240 h.
La señal de ese desajuste se repite: en flujo físico, los vectores
`Fp_A3_true - Fp_med` de 100 y 240 h tienen correlación de Pearson `0.974` y
coinciden en signo en `29/31` bins. Es evidencia de una diferencia espectral
coherente entre el forward de entrada y las soluciones recuperadas; las
realizaciones de ruido independientes no explican por sí solas el patrón.

Los bins con mayor `abs(r_obs)` a 100 h están en `12.96 µm` (`+5.35 sigma`),
`7.11 µm` (`+4.80 sigma`) y `6.76 µm` (`+3.85 sigma`). A 240 h se repiten
`12.96 µm` (`+6.13 sigma`) y `6.76 µm` (`+4.80 sigma`), junto con `14.32 µm`
(`+4.84 sigma`). En las ventanas diagnósticas estrechas N2O 7.5--8.1 y
16.5--17.5 µm, y NH3 9.5--11.5 µm, hay 7 bins; los otros 24 aportan
`101.61/114.31 = 88.9 %` del `chi²` del espectro mediano a 100 h y
`191.16/238.86 = 80.0 %` a 240 h. Esta partición es descriptiva: las
absorciones se solapan y un bin fuera de esas ventanas no identifica por sí
solo una molécula distinta.

El perfil térmico mediano recuperado también difiere del PT VULCAN de entrada:
a `0.1 bar` está `+16.9 K` (100 h) y `+15.3 K` (240 h) por encima del valor
verdadero interpolado. A `0.01 bar` está `-5.3 K` y `-4.2 K`. Estas diferencias
son compatibles con compensaciones entre PT y abundancias, pero no prueban
qué parámetro causa el residuo. En particular, este análisis no permite
atribuirlo exclusivamente a `isochem`, N2O o NH3.

## Interpretación y siguiente prueba

**Resultado:** la pérdida de ajuste con más horas es espectralmente coherente
y aparece sobre todo fuera de las ventanas moleculares estrechas elegidas para
el gráfico S/N. La posterior A3 a 100 h puede quedar a `+4.69` y `+3.04`
semianchos respecto de la referencia A0 efectiva, pero su `chi²_red=5.27`
impide llamar a esas cifras capacidad fiable de distinguir N2O/NH3. Lo mismo
vale, con más tensión, para N2O a 240 h.

**Prueba posterior completada:** el
[diagnóstico de forwards controlados](life_proxima_a3_forward_swap_audit_2026-09-23.md)
identificó dos diferencias de interfaz: la verdad incluye O2 y una superficie
negra explícita a 1 bar, mientras que estos retrievals omiten O2 y usan
`surface=False`. La denominación anterior de «fondo negro fijo» era
incorrecta. Ambas diferencias tienen efecto espectral medible y pueden
compensarse parcialmente; el patrón residual final tampoco se atribuye aún a
una sola de ellas, a PT o a `isochem`. Antes de otro retrieval A3 hay que
validar un modelo que reproduzca la interfaz del forward verdadero. Por ahora
no hace falta un retrieval de A0 ni una integración A3 adicional.

La rama sigue siendo una cota optimista de LIFEsim clásico: `sigma` diagonal,
una realización por tiempo e inexistencia aquí de covarianza/inestabilidad
instrumental. La literatura LIFE documenta que perfiles verticales
simplificados pueden sesgar retrievals de emisión
([Konrad et al., 2024, arXiv:2310.02634](https://arxiv.org/abs/2310.02634));
ese antecedente motiva la prueba, pero no identifica la causa de este caso.

## Productos

- [Figura de residuos PNG](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A3_fixedP1bar_noxtol_residual_audit_10_100_240h.png)
  y [PDF](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A3_fixedP1bar_noxtol_residual_audit_10_100_240h.pdf),
  inspeccionados visualmente.
- [Tabla por bin CSV](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/retrieval_A3_fixedP1bar_noxtol_residual_audit_10_100_240h.csv)
  y [resumen JSON](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/retrieval_A3_fixedP1bar_noxtol_residual_audit_10_100_240h.json).
- [Auditoría A3 100 h](life_proxima_a3_100h_fixedp1bar_noxtol_audit_2026-09-23.md)
  y [auditoría A3 10/240 h](life_proxima_a3_10_240h_fixedp1bar_noxtol_audit_2026-09-23.md).
