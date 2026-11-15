# Comparar regiones de abundancia alta y baja para la hipótesis ExoFarm

**Fecha:** 2026-10-21. **Estado:** decisión metodológica y plan de posprocesado; no requiere una nueva campaña por defecto.

### Actualización de resultados — 2026-10-26

La revisión del runner y de las tres configuraciones resueltas confirmó que `log_N2O` y `log_NH3` son parámetros independientes con prior uniforme en log10 entre −12 y −1. La masa previa efectiva de las cuatro regiones queda determinada exactamente por esos límites y los umbrales A1; deja de ser un pendiente. El análisis de posterior completo A3 a 1/10/100 h está ejecutado y sus tablas tienen procedencia por SHA-256 en el [informe reproducible](life_proxima_a1_regions_corrected_binning_2026-10-26.md). Las fracciones posteriores siguen sujetas a error Monte Carlo; R01/R00 están representadas por solo 1/2 muestras a 10 h y carecen de muestras con N₂O < A1 a 100 h.

Resultados principales: `P(R11|D)` = 6,42 %, 73,07 % y 98,665 %; `K(R11/complemento)` = 0,106, 4,181 y 113,924, para 1/10/100 h. El contraste adicional `R11/R10` vale 0,194/0,882/23,991. Esto no convierte el umbral retrospectivo A1 en un clasificador causal de ExoFarm.

## Pregunta y recomendación

La pregunta planteada es si el espectro LIFE favorece un patrón de abundancias compatible con el escenario ExoFarm frente a abundancias más bajas. Los retrievals completos corregidos ya proporcionan posteriores de N₂O y NH₃ con las que podemos medir esa preferencia por regiones. El posprocesado y la validación de las masas previas se completaron el 26-oct-2026; no se requirieron retrievals con priors recortados. La incertidumbre Monte Carlo posterior y la sensibilidad al umbral siguen abiertas.

Esto cuantifica apoyo a regiones de abundancia dentro del modelo isoquímico adoptado. La lectura como «ExoFarm frente a preagrícola» necesita justificar que los límites regionales representen esas familias físicas. A1 es el benchmark de Tierra actual; el complemento de abundancias por debajo de A1 incluye escenarios distintos de A0. Por tanto, exceder A1 describe enriquecimiento respecto de ese benchmark, no identifica por sí solo una fuente agrícola.

## Cálculo desde el posterior completo

Sea $M$ el retrieval completo, con parámetros $\theta$, posterior $p(\theta\mid D,M)$ y prior efectivo $\pi(\theta\mid M)$. Para una región $R$, definimos

\[
q_R=P(R\mid D,M),\qquad q_{0,R}=P(R\mid M).
\]

El modelo restringido a (R) equivale a truncar y renormalizar el mismo prior. Su evidencia cumple

\[
Z_R=Z_M\,\frac{q_R}{q_{0,R}}.
\]

Para dos regiones disjuntas (R,S), con soporte previo en ambas,

\[
\frac{Z_R}{Z_S}=\frac{q_R/q_S}{q_{0,R}/q_{0,S}}.
\]

Esta es la razón de odds posterior a previa. La identidad es exacta bajo el modelo común y sus priors condicionales; la estimación numérica depende de que las muestras cubran ambas regiones. Es la construcción de factores de región de Wogan et al. (2026), ecuación 13, aplicada a abundancias en lugar de flujos. Los factores de región no sustituyen el contraste de modelos con/sin molécula ni la evidencia entre familias físicas.

Para una molécula $X$, $R_+=\{\log_{10}X\ge\log_{10}X_{A1}\}$ y $R_-=R_+^c$. Entonces

\[
K_{+/-}=\frac{P(R_+\mid D)/P(R_-\mid D)}{P(R_+\mid M)/P(R_-\mid M)}.
\]

La probabilidad posterior $P(R_+\mid D)$ contesta qué fracción de la posterior supera A1. $K$ cuantifica cuánto cambiaron esas odds al incorporar los datos respecto del prior. Si la masa posterior resulta alta porque el prior ya colocaba mucha masa sobre A1, $K$ puede ser mucho menos llamativo. Las dos cantidades deben informarse juntas.

## Las dos moléculas: cuatro regiones

Se clasifican las muestras conjuntas de N₂O y NH₃ en cuatro celdas, contando posterior y prior efectivo en cada una:

| Región | N₂O | NH₃ | Lectura operacional |
|---|---|---|---|
| $R_{00}$ | < A1 | < A1 | Ninguna supera el benchmark |
| $R_{10}$ | ≥ A1 | < A1 | Solo N₂O supera el benchmark |
| $R_{01}$ | < A1 | ≥ A1 | Solo NH₃ supera el benchmark |
| $R_{11}$ | ≥ A1 | ≥ A1 | Ambas superan el benchmark |

Se preservan las regiones mixtas. Comparar $R_{11}$ solo con $R_{00}$ responde a «ambas altas frente a ambas bajas» y deja fuera las dos celdas mixtas; comparar $R_{11}$ con $R_{00}\cup R_{10}\cup R_{01}$ responde a «ambas altas frente a todo lo demás». Son hipótesis distintas. Para medir el apoyo adicional a NH₃ cuando N₂O ya supera A1, se puede comparar $R_{11}$ con $R_{10}$, corrigiendo por sus masas previas. No se fija N₂O exactamente a A0.

La independencia del prior conjunto se verificó en el runner y en las tres configuraciones A3 resueltas: `log_N2O` y `log_NH3` son coordenadas independientes con el mismo prior uniforme en log-abundancia. Por eso, para estos retrievals, las cuatro masas previas conjuntas son los productos exactos de las masas marginales. Si otra configuración introduce restricciones compartidas o una parametrización distinta, esta comprobación debe repetirse.

## Estado de los productos y número de retrievals

Al corte original del 21-oct, el K de NH₃ A3–100 h se describía como nominal porque la masa previa efectiva aún no se había revisado. Esa salvedad quedó resuelta el 26-oct: $P(X\ge A1)=98.6654\%$, el K marginal de NH₃ es 23.991 y el contraste conjunto $K(R_{11}/R_{10}\cup R_{01}\cup R_{00})=113.924$. La actualización de resultados, con las cuatro celdas para 1/10/100 h, está en el [informe reproducible](life_proxima_a1_regions_corrected_binning_2026-10-26.md).

**Conteo para el análisis regional descrito aquí: cero retrievals nuevos inicialmente.** Se necesita una corrida adicional solo si una región relevante queda sin muestrear o con error Monte Carlo inaceptable; primero se diagnostica esa condición en las muestras y se elige el muestreo dirigido que la resuelva.

Si por «análisis general» se entiende completar la matriz corregida A1/A3 para todas las especies y exposiciones, el inventario separado es de **33 retrievals**: tres completos A1, 18 ablaciones A1 y 12 ablaciones A3 para H₂O/CO₂/CH₄/O₃. Añadir los tres contrastes A3–100 h con abundancias A0 fijas elevaría ese inventario a **36**, pero esos tres son una sensibilidad opcional. Ninguna de esas cifras es necesaria para el cálculo regional sobre A3 que ya tiene posteriores corregidos. Una comparación causal entre familias predictivas ExoFarm y preagrícola aún no tiene un número cerrado: primero hay que especificar perfiles, priors predictivos, incertidumbres y ruido de ambas familias.

Las 33 corridas pendientes del plan de homologación A1/A3 por cambio de binning responden a una pregunta diferente: completar baselines y ablaciones LOO corregidos para todas las moléculas. Las tres corridas A3–100 h con abundancias A0 fijas son otra sensibilidad y no se requieren para el factor de región. La decisión regional no cancela esas tareas de homologación.

## Límites de interpretación

- El umbral A1 es una región operacional de enriquecimiento. Para llamarla «ExoFarm», se debe justificar con predicciones de las familias A0/A3; el retrieval de abundancias no determina el origen del gas.
- El umbral A1 se adoptó después de revisar resúmenes de posteriores anteriores. Se conservará como criterio retrospectivo/exploratorio, sin ajustar su valor para maximizar el resultado. Una validación prospectiva requiere fijarlo antes de inspeccionar nuevas realizaciones.
- La referencia A0 efectiva también es un promedio escalar de un perfil vertical; aún no se demostró equivalencia radiativa entre ese número constante y el perfil A0. Este punto afecta la interpretación de umbrales basados en A0, no la definición matemática de los factores de región A1.
- Los resultados son condicionales a perfiles isoquímicos, P–T, datos, binning, likelihood y priors aceptados. Tensión de ajuste o desajuste de perfil restringe cualquier lectura de origen.
- Si se desea comparar directamente escenarios físicos, se deben construir (Z_{\rm ExoFarm}) y (Z_{\rm preagri}) integrando distribuciones predictivas justificadas de cada familia, con incertidumbre de fotoquímica, clima y perfiles. El número de retrievals para esa prueba dependerá de esas definiciones; las cuatro regiones A1 no son automáticamente ese contraste.

## Estado del procedimiento y tareas restantes

1. **Completado (26-oct):** validar los priors efectivos y calcular las masas previas de las cuatro regiones.
2. **Completado (26-oct):** calcular las cuatro masas posteriores y los K de región para A3 corregido a 1/10/100 h; las tablas registran muestras y hashes. Falta cuantificar la incertidumbre Monte Carlo de esos estimadores.
3. **Pendiente:** evaluar sensibilidad a umbrales físicos fijados por anticipado. A1 sigue siendo un corte retrospectivo en este conjunto.
4. **En curso:** incorporar los resultados manteniendo separados LOO de ausencia, desplazamiento de abundancia, apoyo regional y atribución de escenario; revisar primero el texto en chat antes de editar el `.tex`.
5. **Condicional:** considerar muestreo adicional solo si la incertidumbre de colas afecta una conclusión requerida. Una comparación de familias ExoFarm/preagrícola exige definir primero los modelos predictivos.

### Referencias y productos relacionados

- Wogan et al. (2026), [Toward Inferring the Surface Fluxes of Biosignature Gases on Rocky Exoplanets from Telescope Spectra](https://arxiv.org/abs/2604.21848), ecuación 13 y §4.1. El artículo enfatiza que abundancias atmosféricas por sí solas no identifican una fuente biológica; su método infiere flujos mediante un modelo fotoquímico-climático acoplado.
- Trotta (2008), [Bayes in the Sky](https://arxiv.org/abs/0803.4089), definición de evidencia como likelihood promediada sobre el prior y comparación de modelos.
- [Wogan adaptado a regiones de abundancia](life_proxima_wogan_abundance_region_bayes_2026-10-15.md).
- [Regiones posteriores respecto de A1](life_proxima_a1_posterior_regions_2026-10-15.md).
- [Postproceso A3–100 h corregido](life_proxima_a3_100h_corrected_results_update_2026-10-20.md).
- [Inventario de retrievals por binning corregido](life_proxima_corrected_binning_update_plan_2026-10-21.md).
