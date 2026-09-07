# Ensayo de ruido directo de LIFEsim frente a escalado temporal, 2026-08-31

## Pregunta

¿Cambia el ruido esperado si cada tiempo de integración se calcula llamando
directamente a LIFEsim clásico, en vez de obtenerlo a partir de la observación
de 10 h mediante el escalado `sigma(t) = sigma(10 h) * sqrt(10 h / t)`?

El ensayo es una auditoría de la rama clásica de LIFE. No modifica los
datasets ni los retrievals canónicos.

## Diseño reproducible

Se mantuvieron fijos la escena Proxima de LIFE X, los forwards de emisión y la
malla espectral. Se evaluaron los escenarios A0 y A3 en 1, 10, 100, 240, 500 y
1200 h. La escena usa `R=20`, diámetro de apertura de 2 m, 3 exozodis, 1.30 pc
y 31 bins LIFE. La referencia para el escalado fue 10 h.

Para cada escenario y tiempo se llamó directamente a
`LifeSceneClassic.observe`. Después se comparó su `sigma` por bin con la
predicción obtenida a partir de la observación de 10 h. Para separar una
diferencia del modelo de ruido de una diferencia aleatoria, se aplicó el mismo
vector de números normales estándar a las dos rutas.

El cálculo se ejecutó en Ubuntu/WSL, entorno conda `POSEIDON`, con:

```text
LIFEsim 0.2.32
SpectRes 2.1.1
POSEIDON 1.4.0
semilla del ensayo: 20260831
```

El generador es
[`compare_lifesim_noise_scaling.py`](../Thermal_Emission_Spectroscopy/scripts/compare_lifesim_noise_scaling.py).

## Resultado directo

La comparación directa y la escalada son equivalentes para esta escena y este
modelo de ruido:

| Métrica | Resultado |
| --- | ---: |
| Máxima diferencia relativa entre `sigma` directa y escalada | `6.7e-16` |
| Máxima diferencia entre realizaciones emparejadas | `8.5e-15 sigma` |
| Número de bins | 31 |
| Flujo esperado relativo entre tiempos | 0 |

En otras palabras, LIFEsim clásico produce el comportamiento esperado de ruido
fotónico diagonal:

```text
sigma(t) = sigma(t0) * sqrt(t0 / t)
SNR(t)   = SNR(t0)   * sqrt(t / t0)
```

Tomando 10 h como referencia, el ruido esperado baja por un factor aproximado
de 4.90 a 240 h, 7.07 a 500 h y 10.95 a 1200 h. El cálculo directo reproduce
exactamente esos factores, dentro de la precisión numérica de doble precisión.

Esto también explica el piloto A3--500 h: el dataset generado originalmente
con el escalado no tenía un ruido distinto del que habría producido la llamada
directa a LIFEsim. La validación específica del archivo de 500 h encontró,
además, identidad byte a byte con el dataset usado por el retrieval.

## Interpretación

Para LIFEsim clásico, escalar `sigma` es una forma válida y eficiente de
generar tiempos adicionales cuando la escena, el espectro y el modelo de ruido
permanecen fijos. No constituye una simulación de una nueva época instrumental:
solo cambia la incertidumbre esperada con el tiempo.

Si se cambia la semilla, los puntos observados pueden cambiar y un retrieval
puede moverse por fluctuación estadística, aunque la distribución de `sigma`
sea la misma. Esa variación aleatoria no es una diferencia entre la ruta directa
y la escalada.

El ensayo no valida ruido temporal correlacionado, inestabilidad instrumental,
covarianza entre bins ni varias realizaciones de misión. Esas preguntas siguen
requiriendo la rama LIFEsimMC/PHRINGE. Por ello, la rama clásica continúa siendo
una cota optimista de ruido astrofísico/fotónico y no una validación instrumental
final de LIFE.

## Productos

- Tabla completa: [`lifesim_noise_scaling_comparison.csv`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/lifesim_noise_scaling_comparison.csv).
- Resumen reproducible: [`lifesim_noise_scaling_comparison.json`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/lifesim_noise_scaling_comparison.json).
- Figura PNG: [`lifesim_direct_vs_scaled_noise_proxima.png`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/audit/lifesim_direct_vs_scaled_noise_proxima.png).
- Figura PDF: [`lifesim_direct_vs_scaled_noise_proxima.pdf`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/audit/lifesim_direct_vs_scaled_noise_proxima.pdf).

