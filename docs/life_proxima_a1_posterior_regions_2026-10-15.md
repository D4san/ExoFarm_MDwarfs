# Abundancias iguales o superiores a A1: probabilidades posteriores LIFE

Fecha: 2026-10-15, America/Bogota. Análisis ejecutado sobre las seis posteriores
históricas A1/A3 × {1, 10, 100 h}. Sin nuevos retrievals.

## Pregunta e interpretación

El usuario adopta el criterio **mayor o igual a A1** para preguntar cuánto apoyo
posterior reciben abundancias que alcanzan el benchmark actual del proyecto.
Definimos regiones individuales R_N = {X_N2O >= X_N2O(A1)} y
R_H = {X_NH3 >= X_NH3(A1)}, y la región conjunta R_N ∩ R_H.
Las probabilidades individuales son marginales; no suponen independencia
posterior. La intersección se cuenta sobre las mismas filas de muestras.

Estas regiones describen niveles de abundancia. Los escenarios agrícolas
actuales o intensificados del modelo motivan el umbral, pero otras causas
podrían producir esos niveles. Además, una región sin límite superior incluye
abundancias mayores que A3. Por tanto, alcanzar A1 no equivale a demostrar
compatibilidad con toda la familia física A1–A3 ni a identificar agricultura.
No se calcula una probabilidad causal de ExoFarm.

**Limitación de la serie:** las muestras proceden de la serie original, cuya
discrepancia entre integración espectral del generador y del likelihood está
documentada en el [diagnóstico](life_proxima_nh3_1000h_interface_diagnosis_2026-10-14.md).
Este postprocesado reproduce sus posteriores sin corregir ese operador.
Los porcentajes son resultados condicionados a esa serie; su uso como
predicciones del instrumento requiere repetir el análisis sobre productos
aceptados con un contrato espectral coherente.

## Fuentes y cálculo

- [Script reproducible](../Thermal_Emission_Spectroscopy/scripts/analyse_proxima_a1_regions.py).
- [Referencias efectivas compartidas](../Thermal_Emission_Spectroscopy/scripts/retrieval_reference.py).
- [Perfil A1](../Transmission_Spectroscopy/profiles/Proxima_b_A1_Current_chem.txt).
- [Resumen A0 usado como inventario y control](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a0_enrichment_posterior_2026-10-10.csv).
- [Resultados marginales](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/a1_regions_2026-10-15/marginal.csv).
- [Resultados conjuntos](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/a1_regions_2026-10-15/joint.csv).
- [Manifest de entradas, hashes y configuración](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/a1_regions_2026-10-15/manifest.json).

Se reutiliza la definición efectiva de abundancia del proyecto, sin cambiar
su promedio vertical. Los umbrales log10(VMR) A1 son −6,7338304684 para N2O
y −9,3048651166 para NH3. Se verificaron los hashes de las seis matrices de
muestras y los seis datasets contra el inventario original; se reprodujeron
los doce conteos marginales sobre A0. No hubo muestras exactamente iguales
al umbral A1; `>=` y `>` coinciden numéricamente en estas entradas.

Se calculan también Δ_i = log10[X_i/X_i(A1)], sus cuantiles 2,5, 16, 50, 84
y 97,5 %, las razones correspondientes y la anchura central del 95 % en dex.
La estimación de probabilidad usa la fracción de muestras posteriores de igual
peso dentro de cada región, siguiendo el producto exportado existente.

## Resultados directos: masas posteriores

| Horas | Escenario | N2O ≥ A1 | NH3 ≥ A1 | Ambas ≥ A1 |
|---:|:---:|---:|---:|---:|
| 1 | A1 | 6,57 % | 40,81 % | 2,82 % |
| 1 | A3 | 17,27 % | 38,51 % | 6,48 % |
| 10 | A1 | 1,11 % | 28,23 % | 0,38 % |
| 10 | A3 | 99,90 % | 61,33 % | 61,27 % |
| 100 | A1 | 0,47 % | 6,13 % | Ninguna muestra |
| 100 | A3 | Todas las muestras | 92,19 % | 92,19 % |

«Todas» y «ninguna» describen el muestreo finito. No establecen probabilidades
exactas uno/cero ni límites de confianza mediante 1/N. No se estimó aquí el
tamaño muestral efectivo ni la incertidumbre Monte Carlo. Las exposiciones
usan realizaciones de ruido diferentes, por lo que no constituyen una
secuencia de datos anidados. A1–1 h usa la realización NoiseRepeat2 promovida
post hoc, según el [registro](life_proxima_a1_1h_independent_noise_repeat_2026-10-02.md).

### Magnitud y anchura para A3–100 h

| Molécula | Mediana X/X(A1) | Intervalo central 95 % | Mediana Δ (dex) | Anchura 95 % (dex) |
|:---|---:|---:|---:|---:|
| N2O | 3,86 | 2,94–4,93 | 0,586 | 0,225 |
| NH3 | 11,14 | 0,027–23,84 | 1,047 | 2,946 |

El intervalo central contiene el 95 % de la masa posterior entre sus
cuantiles; queda un 2,5 % en cada cola. En NH3, aproximadamente un 7,81 % de la
masa permanece por debajo de A1, de modo que su intervalo central del 95 %
atraviesa el umbral. El intervalo central del 68 % de NH3 sí está sobre A1
(4,43–17,70 veces). Ambas descripciones reflejan su asimetría.

**Interpretación del proyecto:** A3–100 h proporciona apoyo posterior a niveles
superiores al benchmark A1 en ambas moléculas. N2O delimita un enriquecimiento
estrecho, mientras que NH3 aporta una tendencia positiva menos precisa.
La igualdad entre probabilidad conjunta y marginal de NH3 se debe a que
todas las muestras de N2O superan A1: el resultado conjunto queda limitado por
NH3. Su valor no constituye una segunda prueba independiente de esa molécula.

En las simulaciones A1, las posteriores pueden quedar mayormente por debajo
de la propia referencia usada para generar el perfil. Esto exige conservar
los controles de recuperación, la diferencia entre perfil vertical y
abundancia constante y el problema conocido de integración espectral. La
tabla no valida el umbral como clasificador calibrado de agricultura.

## Actualización de odds: cálculo nominal inspirado en Wogan

Se usa K_R = [q/(1−q)]/[q0/(1−q0)], donde q es la masa posterior y q0 la
masa previa de la misma región. La [revisión de Wogan](life_proxima_wogan_abundance_region_bayes_2026-10-15.md)
documenta la fuente publicada y las condiciones de esta comparación.

Con los priors **nominales** independientes y uniformes en log10(X) entre
−12 y −1, q0 vale 52,13 % para N2O, 75,50 % para NH3 y 39,35 % para la
región conjunta. La gran masa previa por encima de A1 muestra por qué una
masa posterior elevada debe acompañarse del cambio respecto del prior.

| A3 | K conjunto nominal | ln K conjunto nominal | K NH3 nominal | ln K NH3 nominal |
|---:|---:|---:|---:|---:|
| 1 h | 0,107 | −2,237 | 0,203 | −1,593 |
| 10 h | 2,438 | 0,891 | 0,515 | −0,664 |
| 100 h | 18,194 | 2,901 | 3,832 | 1,343 |

En este diagnóstico nominal A3–100 h multiplica por 18,2 las odds de la
región conjunta respecto de su complemento y por 3,83 las de NH3. Las odds
previas de NH3 ya favorecen abundancias ≥ A1; su probabilidad posterior
92,19 % representa un incremento sobre ese punto de partida.

Estos factores comparan regiones complementarias de abundancia con priors
restringidos y renormalizados. No son los factores con/sin molécula ni los
de abundancias fijas A0. La validación del prior efectivo completo sigue
pendiente; por ello se conservan como diagnósticos nominales. No se asignan
factores infinitos cuando una región o su complemento no fueron muestreados.

## Reproducción y siguiente paso

Ejecutar desde la raíz con un Python que incluya NumPy:

```text
python Thermal_Emission_Spectroscopy/scripts/analyse_proxima_a1_regions.py
```

La ejecución produjo 12 filas marginales, 6 conjuntas y un manifest; todas
las comprobaciones de integridad y de reproducción A0 pasaron. Los CSV A0
originales permanecieron sin cambios. La decisión A1 se tomó después de
examinar la serie: debe registrarse como criterio retrospectivo y fijarse
antes de futuras realizaciones. Próximo paso: validar el prior efectivo y
aplicar el mismo procedimiento a la serie corregida cuando esté aceptada.
La rama de 1000 h queda fuera de esta ejecución.

## Ampliación: sensibilidad a los retrievals alternativos A0

Se ejecutó el [postprocesado condicional](../Thermal_Emission_Spectroscopy/scripts/analyse_proxima_a1_alternative_regions.py)
sobre las dos restricciones individuales del mismo dataset A3–100 h. Se
verificaron los hashes contra la [auditoría aceptada](life_proxima_a3_100h_a0_fixed_audit_2026-10-11.md),
el número de muestras, la finitud y el valor A0 de cada coordenada fija.
Los [resultados y su procedencia](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/a1_regions_2026-10-15/alternative_a0_conditional.json)
se guardan separados de la comparación entre modelos y de la serie principal.

| Modelo | Molécula libre examinada | P(≥ A1) | K nominal de región | ln K nominal |
|:---|:---|---:|---:|---:|
| Ambas libres, referencia principal | NH3 | 92,19 % | 3,832 | 1,343 |
| N2O fija A0 | NH3 | 94,43 % | 5,498 | 1,704 |
| NH3 fija A0 | N2O | ≈100 % | Cola sin resolver | Cola sin resolver |

La comparación evalúa cuánto cambia el enriquecimiento marginal cuando la
otra molécula deja de poder ajustarse. La probabilidad de NH3 sobre A1 se
mantiene elevada en ambos casos y el enriquecimiento de N2O persiste al fijar
NH3. Esta estabilidad se limita a las restricciones probadas. Fijar N2O en
A0 empeora fuertemente la evidencia del modelo: la posterior de NH3 en ese
modelo puede reflejar compensaciones ante el desajuste impuesto. No
constituye confirmación independiente de NH3 ni una prueba causal agrícola.

La evidencia de los modelos permite una segunda comparación, manteniendo
la otra molécula en A0 en ambos lados del contraste:

| Cambio respecto de ambas fijas A0 | ln B ± error numérico | B |
|:---|---:|---:|
| Liberar N2O; NH3 sigue A0 | 29,932 ± 0,332 | 9,987 × 10^12 |
| Liberar NH3; N2O sigue A0 | 1,663 ± 0,330 | 5,273 |

Con N2O ya libre, liberar además NH3 produce ln B = 1,170 ± 0,342
(B ≈ 3,223), según la comparación original. Así se cuantifica el aporte
adicional de NH3 después de permitir el enriquecimiento de N2O. Estas razones
de evidencias comparan abundancia libre con A0 puntual; los K de región
comparan ≥ A1 con < A1. Se reportan como preguntas diferentes y no se
multiplican como pruebas independientes. Si ambas moléculas están fijas A0,
la probabilidad de superar A1 es cero por construcción; esa fracción no
aporta una prueba adicional. Lo mismo ocurre para una molécula eliminada
en un retrieval de omisión.

**Presentación:** se adopta ≈0 % / ≈100 % para las fracciones extremas de
muestreo. El factor de odds correspondiente queda sin resolver, evitando
reportar cero o infinito a partir de una cola no muestreada.

**Orden narrativo propuesto:** tras el desplazamiento descriptivo, evaluar
presencia molecular con las comparaciones de omisión; después cuantificar
dirección y magnitud con probabilidades ≥ A1 y K de región del modelo
completo. Al presentar las restricciones A0, añadir los contrastes de
evidencias y la sensibilidad condicional de esas probabilidades.

Reproducción: `python Thermal_Emission_Spectroscopy/scripts/analyse_proxima_a1_alternative_regions.py`.
Se conservan la limitación de binning de la serie histórica y el carácter
nominal del prior. No se ejecutó un nuevo retrieval ni se editó el manuscrito.
