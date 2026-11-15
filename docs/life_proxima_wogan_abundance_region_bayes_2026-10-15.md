# Probabilidades de enriquecimiento y atribución ExoFarm: adaptación del análisis de Wogan

Fecha: 2026-10-15, America/Bogota. Estado: revisión metodológica y cálculo
ilustrativo A0; criterio ≥ A1 adoptado posteriormente por el usuario y
[calculado en un análisis separado](life_proxima_a1_posterior_regions_2026-10-15.md).
La atribución causal y la validación del prior efectivo siguen pendientes. Ámbito: las posteriores
isoquímicas LIFE Proxima A1/A3 de 1, 10 y 100 h ya existentes.

## Resultado de la revisión

El análisis por regiones de Wogan et al. (2026) se puede aplicar al espacio de
abundancias recuperadas sin inferir flujos superficiales. Sus dos operaciones
transferibles son integrar la posterior en una región definida científicamente
y comparar las odds posteriores con las odds previas de esa misma región.
Esto permite cuantificar enriquecimiento individual o conjunto y cuánto apoyo
añaden los datos respecto del prior.

Interpretar ese factor como evidencia causal de agricultura requiere además
hipótesis predictivas de atmósferas agrícolas y naturales. El presente cálculo
no asigna una probabilidad de ExoFarm ni adopta nuevos priors científicos.

Las cifras ilustrativas usan la serie original. Su discrepancia de integración
generador/likelihood está documentada en el
[diagnóstico de interfaz](life_proxima_nh3_1000h_interface_diagnosis_2026-10-14.md).
Una transformación estadística de las posteriores no corrige esa diferencia.
La propuesta deberá aplicarse a productos aceptados con un contrato espectral
coherente antes de fijar conclusiones para el artículo.

## 1. Fuente primaria leída

Wogan et al. (2026), *Toward Inferring the Surface Fluxes of Biosignature
Gases on Rocky Exoplanets from Telescope Spectra*, ApJ 1004:191, 14 páginas,
[DOI:10.3847/1538-4357/ae6646](https://doi.org/10.3847/1538-4357/ae6646).
Se leyó la versión publicada almacenada en Zotero, no solo la reseña previa.

Ruta local verificada:

`C:/Users/User/Zotero/storage/5FBDFVTW/Wogan et al. - 2026 - Toward Inferring the Surface Fluxes of Biosignature Gases on Rocky Exoplanets from Telescope Spectra.pdf`

SHA-256: `46d3cdb0793dc8d4484a578c90e9b01b5ed23d62c9739dc840911defb83d12f5`.

La API de Zotero estaba habilitada, pero su consulta desde el sandbox devolvió
WinError 10013. Se leyó directamente el adjunto guardado en la biblioteca.
Las páginas 8 y 9 se renderizaron y revisaron para comprobar las ecuaciones y
la tabla 2.

**Hechos de fuente:**

- En §2.5, pp. 5–6, definen regiones de flujos compatibles con sus criterios
  de biofirma y un complemento. Reconocen que los mecanismos físicos pueden
  solaparse; la partición binaria constituye una simplificación.
- En §3.3, p. 7, ecuaciones (7)–(8), estiman las masas previas y posteriores
  contando muestras en las regiones definidas.
- La tabla 2, p. 8, contiene una masa posterior de 0.76 en su región L y una
  masa previa de 0.38.
- En §4.1, pp. 8–9, ecuación (13), obtienen un factor de Bayes entre la región
  y su complemento dividiendo odds posteriores entre odds previas. Reportan
  aproximadamente K_L = 5.1; las cifras 0.76/0.38 están redondeadas.
- La ecuación (11) incorpora un prior contextual de vida. El paso de K_L a
  K_life utiliza una hipótesis proxy explícita: la región debe discriminar
  suficientemente bien vida/ausencia de vida y el modelo debe capturar los
  procesos relevantes. El artículo no identifica directamente el 76 % con
  una probabilidad de vida.

## 2. Traslado al espacio de abundancias

Sean theta los parámetros recuperados, D un dataset y M el modelo completo.
Para cada molécula definimos el enriquecimiento ya utilizado en el proyecto:

\[
\delta_i=\log_{10}(X_i/X_{0,i}).
\]

Una primera región operacional, que conserva exactamente la pregunta del
postproceso existente, es

\[
R=\{\theta:\delta_{\mathrm{N_2O}}>0
\ \land\ \delta_{\mathrm{NH_3}}>0\}.
\]

Su probabilidad posterior es

\[
q=P(R\mid D,M)=\int_R p(\theta\mid D,M)\,d\theta.
\]

Se cuentan las dos condiciones sobre las mismas filas posteriores de igual
peso para conservar su dependencia. Multiplicar las probabilidades marginales
posteriores no reproduce en general este evento conjunto.

El criterio usa una intersección porque pregunta por enriquecimiento de ambas
moléculas. Una unión preguntaría si al menos una supera A0 y tendría otra masa
previa, otra posterior y otra interpretación.

El complemento de R incluye casos con solo una molécula enriquecida. Por ello
no equivale a fijar ambas abundancias en A0, ni constituye una familia física
completa de mundos sin agricultura.

Otros umbrales, por ejemplo delta_i > a_i, permitirían estudiar amplitudes
mínimas de enriquecimiento. Sus valores deben justificarse con el diseño
físico y variabilidad natural o declararse sensibilidades exploratorias. No se
deben elegir a partir de los mismos datos para maximizar el resultado.

## 3. Qué añade comparar prior y posterior

Sea q_0 = P(R | M) la masa de la región bajo el prior completo. Para los dos
modelos obtenidos al restringir y renormalizar ese mismo prior en R y su
complemento se cumple

\[
K_{R/\bar R}
=\frac{q/(1-q)}{q_0/(1-q_0)}.
\]

Esta identidad se aplica a regiones complementarias con probabilidad previa
positiva. La likelihood y los priors condicionales de los restantes parámetros
deben ser los del modelo de origen. Es la adaptación de la ecuación (13) de
Wogan; no necesita inferir flujos.

q describe cuánto posterior satisface el criterio. K describe cuánto cambiaron
sus odds por incorporar el espectro. Una posterior alta puede ser poco
informativa si el prior ya asignaba una probabilidad similar a la región.

### Ilustración numérica con el prior escalar nominal

**Supuesto ilustrativo del proyecto:** dos priors independientes y uniformes
en log10 X entre -12 y -1, sin corregir posibles restricciones conjuntas del
prior efectivo. Los valores A0 son los congelados en el
[análisis de enriquecimiento](life_proxima_a0_enrichment_methodology_2026-10-10.md).

\[
q_{0,i}^{\mathrm{nominal}}=\frac{-1-\log_{10}X_{0,i}}{11}.
\]

Resultan 0.5349386626942532 para N2O y 0.8136842086968215 para NH3. Bajo
independencia nominal, la probabilidad de ambas por encima es su producto:
q_0 = 0.43527114245570925.

| A3: exposición | P(ambas > A0) posterior | K conjunto, prior nominal | ln K conjunto, prior nominal |
|---|---:|---:|---:|
| 1 h | 0.108885299 | 0.158531564 | -1.841801563 |
| 10 h | 0.715576592 | 3.264155916 | 1.183001204 |
| 100 h | 0.948656237 | 23.971835057 | 3.176879602 |

Estos K son cálculos ilustrativos bajo el supuesto nominal, no factores
oficiales validados para el prior efectivo del retrieval. Es necesario generar
o reconstruir muestras del prior completo y aplicar sus restricciones reales
antes de adoptar las cifras como resultados metodológicos de la campaña.

La lectura del caso de 100 h sería: dentro de este supuesto, las odds de que
ambas abundancias superen A0 se multiplican por aproximadamente 24. La cifra
no significa 94.87 % de probabilidad de agricultura. Tampoco es el contraste
libre/A0 puntual con ln B = 31.103; las alternativas comparadas son distintas.

Para NH3 individual, el mismo ejercicio da:

| A3: exposición | P(NH3 > A0) posterior | K NH3, prior nominal | ln K NH3, prior nominal |
|---|---:|---:|---:|
| 1 h | 0.543295638 | 0.272392306 | -1.300511950 |
| 10 h | 0.715863454 | 0.576895129 | -0.550094781 |
| 100 h | 0.948656237 | 4.230726523 | 1.442373733 |

**Interpretación exploratoria:** a 100 h aparece aprendizaje positivo hacia
NH3 enriquecido, mientras a 10 h la probabilidad posterior sigue por debajo
del 81.37 % nominal previo. Esta comparación permite expresar el indicio de
NH3 con más información que la mediana o la fracción posterior aisladas.

Para N2O a 100 h, las muestras guardadas sitúan la fracción por encima en uno.
No se debe reportar K infinito: la cola que determina el denominador no está
resuelta. No se añaden pseudoconteos ni se usa 1/N como límite calibrado.

## 4. Una probabilidad de ExoFarm sin inferir flujos

Es posible formular una comparación causal en el espacio de composición.
Requiere definir hipótesis H_E (agricultura) y H_N (sin agricultura) mediante
distribuciones predictivas normalizadas sobre composición y demás parámetros.
Los escenarios fotoquímicos pueden informar esas distribuciones, junto con
sus supuestos y variaciones naturales. Los cuatro escenarios A0–A3 por sí
solos son puntos de diseño; no definen automáticamente una distribución
poblacional ni amplitudes de incertidumbre.

Definidas esas hipótesis, el factor pertinente sería

\[
K_E=\frac{p(D\mid H_E,c)}{p(D\mid H_N,c)},
\qquad
P(H_E\mid D,c)=\frac{K_E\,\pi_E}{1-\pi_E+K_E\,\pi_E},
\]

donde pi_E = P(H_E | c) es la probabilidad previa de agricultura dado el
contexto. No es la masa de una región bajo el prior genérico de abundancias.

Esto corresponde a la estructura de las ecuaciones (11)–(12) de Wogan. Su
aplicación a agricultura es una propuesta del proyecto. Igualar K_E con el
factor de una región de abundancias requeriría demostrar que esa región
discrimina razonablemente fuentes agrícolas y naturales. Superar una única
referencia A0 no demuestra esa discriminación: otras biosferas naturales
podrían producir enriquecimiento nitrogenado.

Si se adoptan hipótesis operacionales limitadas, por ejemplo una familia
natural especificada y una familia agrícola especificada, la probabilidad
obtenida debe nombrarlas. Una probabilidad entre plantillas A0/A3 es
condicional a esas plantillas y no una atribución universal de agricultura.

### Posibilidad de reutilizar las muestras actuales

Si las hipótesis difieren únicamente en priors sobre los mismos parámetros,
comparten la likelihood y tienen soporte cubierto por el prior genérico pi_0,
puede evaluarse, en principio,

\[
Z_H=Z_0\,
E_{p_0(\theta\mid D)}
\left[\frac{\pi_H(\theta)}{\pi_0(\theta)}\right].
\]

La razón de esas expectativas da K_E. La identidad se obtiene sustituyendo
p_0(theta|D) = L(D|theta) pi_0(theta)/Z_0; no constituye una implementación
o resultado ejecutado en esta revisión. Exige priors H normalizados, soporte
adecuado y pesos estables. Si el nuevo modelo introduce otros perfiles o una
likelihood distinta, esa fórmula con solo el cociente de priors no basta.
Una referencia puntual A0 tampoco se reconstruye mediante pesos ordinarios
de un prior continuo; sus contrastes dedicados siguen siendo otra pregunta.

Por tanto, explorar probabilidades causales no obliga por definición a
convertir el retrieval en una inferencia de flujos. Primero hace falta
especificar el modelo causal de composición y comprobar si admite una
reutilización válida de las muestras.

## 5. Propuesta de siguiente análisis

1. Mantener las comparaciones con/sin molécula para presencia molecular y las
   restricciones puntuales A0 para su pregunta específica.
2. Añadir una tabla inspirada en Wogan: región, masa previa, masa posterior y
   cambio de odds. Incluir regiones individuales y conjunta, usando las mismas
   filas posteriores para los eventos conjuntos.
3. Congelar los criterios antes de interpretar nuevas realizaciones; registrar
   que el criterio A0 se examina aquí después de conocer resultados de la serie.
4. Validar el prior efectivo completo, la resolución de colas y, si se usan
   nuevos priors, el soporte y la estabilidad de los pesos.
5. Separar el resultado de enriquecimiento de la propuesta causal ExoFarm.
   Definir familias naturales/agrícolas y un prior contextual solo cuando se
   quiera calcular P(H_E | D,c).

Esta revisión deja la propuesta documentada. No adopta regiones como
clasificadores físicos de agricultura, no fija un prior poblacional ExoFarm y
no inicia nuevas simulaciones ni retrievals.

## 6. Procedencia y reproducción de la ilustración

Inputs leídos sin modificaciones:

- [Posteriores marginales](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a0_enrichment_posterior_2026-10-10.csv),
  SHA-256 `3a7ae1fc860ee5f15c78afe7deb726b3bba44b8cbaf0f25bab374b855e90f9d4`.
- [Eventos conjuntos](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a0_enrichment_joint_2026-10-10.csv),
  SHA-256 `f68c5959710cde5759c09d780e8335da26c8f84c3adc594c404f87807bf93ec1`.
- [Script original de enriquecimiento](../Thermal_Emission_Spectroscopy/scripts/analyse_proxima_a0_enrichment.py),
  procedencia de los conteos y probabilidades; no se modificó ni se reejecutó.
- [Runner y definición de priors](../Thermal_Emission_Spectroscopy/scripts/run_life_retrieval.py).
- [Método y aceptación A0](life_proxima_a0_enrichment_methodology_2026-10-10.md).

Para reproducir las dos tablas ilustrativas basta leer las filas A3 de los CSV,
calcular q_0 nominal con la ecuación de §3 y aplicar
K = q*(1-q_0)/((1-q)*q_0), seguido de ln K. Los cálculos se hicieron con
aritmética de doble precisión; todas las filas ilustradas tienen 0 < q < 1.
No se guardó un nuevo producto final ni se alteraron las tablas oficiales.

La revisión bibliográfica verificó la versión publicada, las ecuaciones
(7)–(13), la tabla 2 y el alcance del proxy. Las páginas matemáticas 8 y 9
se inspeccionaron visualmente; la extracción y las imágenes de lectura quedan
en `tmp/pdfs/wogan_20261015/` como material temporal de revisión.
