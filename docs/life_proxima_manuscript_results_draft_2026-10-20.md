### De la separación respecto de A0 a la evidencia molecular

El desplazamiento respecto de A0 describe cuánto se aparta la abundancia inferida de la referencia preagrícola y con qué incertidumbre, suponiendo el modelo atmosférico utilizado. Otras composiciones o estructuras térmicas podrían ofrecer explicaciones alternativas del mismo espectro. Para fortalecer la identificación molecular debemos examinar si incluir cada especie mejora la explicación de los datos después de permitir que las demás propiedades atmosféricas se ajusten.

Para comparar dos modelos directos —en este caso, uno que incluye una molécula y otro que permite prescindir de ella— utilizamos el factor de Bayes. Este compara sus evidencias bayesianas, que consideran las distintas configuraciones de parámetros permitidas por cada modelo. Para un modelo \(M\), la evidencia es

\[
Z_M=p(D\mid M)
=\int p(D\mid\boldsymbol{\theta},M)\,
\pi(\boldsymbol{\theta}\mid M)\,d\boldsymbol{\theta},
\]

donde \(D\) representa el espectro observado, \(\boldsymbol{\theta}\) los parámetros atmosféricos y \(\pi\) su distribución previa. La evidencia promedia la capacidad de explicar el espectro sobre las configuraciones permitidas por el prior. El factor de Bayes para una especie \(i\) queda definido como

\[
B_i=\frac{Z_{\mathrm{completo}}}{Z_{\mathrm{sin}\,i}},
\qquad
\ln B_i=\ln Z_{\mathrm{completo}}-\ln Z_{\mathrm{sin}\,i}.
\]

Cuando \(\ln B_i>0\), los datos favorecen incluir la molécula. Los valores negativos favorecen su omisión, mientras que los próximos a cero indican un apoyo semejante para ambas alternativas.

Adoptamos la escala orientativa presentada por [Trotta (2008), tabla 1](https://arxiv.org/pdf/0803.4089#page=14): \(|\ln B|<1\) corresponde a una comparación inconclusa; entre 1 y 2.5, a evidencia débil; entre 2.5 y 5, a evidencia moderada; y por encima de 5, a evidencia fuerte. El signo identifica el modelo favorecido. Estos niveles son convenciones de interpretación, cuya aplicación depende de las hipótesis y priors comparados.

Siguiendo el procedimiento de identificación molecular de [Lin et al. (2021)](https://arxiv.org/pdf/2105.09319), comparamos cada retrieval completo con seis modelos que excluyen individualmente H₂O, CO₂, CH₄, O₃, N₂O o NH₃. Al retirar una molécula se eliminan su opacidad y su parámetro de abundancia; los demás parámetros permanecen libres. Así comprobamos si los gases restantes, la estructura térmica y el radio planetario pueden reproducir el espectro sin ella.

El diseño de comparación comprende **36 retrievals de exclusión**, correspondientes a seis especies para cada combinación de A1/A3 y 1, 10 o 100 h. Junto con los seis retrievals completos, la matriz considera **42 modelos**. Cada contraste debe utilizar el mismo espectro observado, realización de ruido y priors compartidos. O₂ permanece libre en todas las configuraciones y su evidencia individual no se evalúa. La tabla presenta los resultados disponibles; las comparaciones de H₂O, CO₂, CH₄ y O₃ para A3 a 100 h quedan pendientes de incorporación.

### Expresión de la evidencia en una escala de sigmas

Los sigmas ofrecen una escala familiar para describir la magnitud de una discrepancia. En una comparación gaussiana, indican cuántas desviaciones estándar separan un resultado del valor de referencia. Una separación de \(3\sigma\), por ejemplo, deja aproximadamente un 0.27 % de la distribución normal en las dos colas más alejadas.

Nuestro análisis compara evidencias bayesianas. Para expresarlas también en esa escala utilizamos la calibración aproximada presentada por [Benneke y Seager (2013), ecuaciones 8–9 y tabla 2](https://arxiv.org/pdf/1306.6325#page=5). Obtenemos un valor auxiliar \(p_{\mathrm{cal}}\) mediante

\[
B_i=\frac{-1}{e\,p_{\mathrm{cal}}\ln p_{\mathrm{cal}}},
\qquad 0<p_{\mathrm{cal}}<e^{-1},
\]

y calculamos la separación gaussiana que deja esa probabilidad en sus dos colas:

\[
p_{\mathrm{cal}}
=\operatorname{erfc}
\left(\frac{\sigma_{\mathrm{cal}}}{\sqrt{2}}\right).
\]

Con esta calibración, \(\ln B\simeq3\) corresponde aproximadamente a \(3\sigma_{\mathrm{cal}}\), \(\ln B\simeq5\) a \(3.6\sigma_{\mathrm{cal}}\), y \(\ln B\simeq10.7\) a \(5\sigma_{\mathrm{cal}}\). La conversión utiliza como igualdad un límite aproximado entre el factor de Bayes y una probabilidad de cola. Por ello, los sigmas obtenidos sirven como escala auxiliar de lectura; no constituyen una significancia frecuentista medida directamente.

Aplicamos esta calibración cuando \(\ln B>0\), es decir, cuando la comparación favorece incluir la especie. Para \(\ln B\leq0\) mostramos una raya: no existe una preferencia positiva por su inclusión que debamos expresar como significancia de detección. En todos los casos, conservamos \(\ln B\) como resultado principal.

### Resultados de las comparaciones moleculares

La evidencia se calcula mediante una integración numérica. MultiNest utiliza un muestreo finito y proporciona una estimación de su incertidumbre, asociada a la precisión con que evalúa esa integral. Esta es una característica del cálculo de evidencia descrito por [Feroz et al. (2009)](https://doi.org/10.1111/j.1365-2966.2009.14548.x).

Para la diferencia entre dos evidencias propagamos esas incertidumbres suponiendo independencia numérica entre las ejecuciones:

\[
\delta_{\mathrm{num}}(\ln B_i)
=
\sqrt{
\delta_{\mathrm{num}}(\ln Z_{\mathrm{completo}})^2+
\delta_{\mathrm{num}}(\ln Z_{\mathrm{sin}\,i})^2
}.
\]

Los valores resultantes se encuentran entre 0.23 y 0.45. Estos errores describen la precisión numérica de la comparación; no incluyen la incertidumbre debida a otros modelos atmosféricos, priors o realizaciones de ruido. Además, los contrastes de un mismo dataset comparten la evidencia del modelo completo y sus errores no son independientes entre sí.

| Tiempo | Molécula | A1: \(\ln B\) | A1: \(\sigma_{\mathrm{cal}}\) | A3: \(\ln B\) | A3: \(\sigma_{\mathrm{cal}}\) |
|---|---|---:|---:|---:|---:|
| 1 h | H₂O | 11.13 | 5.09 | 19.52 | 6.57 |
| 1 h | CO₂ | 469.13 | 30.75 | 462.85 | 30.54 |
| 1 h | CH₄ | 9.28 | 4.69 | 6.00 | 3.89 |
| 1 h | O₃ | −1.55 | — | −0.36 | — |
| 1 h | N₂O | −1.80 | — | 0.05 | 1.12 |
| 1 h | NH₃ | −1.38 | — | −0.63 | — |
| 10 h | H₂O | 229.56 | 21.57 | 241.51 | 22.12 |
| 10 h | CO₂ | 4644.26 | 96.43 | 3970.54 | 89.16 |
| 10 h | CH₄ | 54.68 | 10.69 | 26.80 | 7.61 |
| 10 h | O₃ | 0.29 | 1.47 | −0.38 | — |
| 10 h | N₂O | 0.45 | 1.63 | 7.39 | 4.25 |
| 10 h | NH₃ | −0.50 | — | −0.73 | — |
| 100 h | H₂O | 2289.86 | 67.74 | Pend. | Pend. |
| 100 h | CO₂ | 41729.86 | 288.91 | Pend. | Pend. |
| 100 h | CH₄ | 314.09 | 25.20 | Pend. | Pend. |
| 100 h | O₃ | 38.40 | 9.03 | Pend. | Pend. |
| 100 h | N₂O | 1.61 | 2.36 | 84.66 | 13.22 |
| 100 h | NH₃ | −1.53 | — | 2.75 | 2.85 |

*Las incertidumbres numéricas de \(\ln B\), calculadas mediante la expresión anterior, se conservan en la tabla completa de resultados. Las rayas indican que no se asigna una significancia calibrada a favor de incluir la especie.*

*Pend.: contraste molecular pendiente de completar para A3–100 h.*

En esta configuración simulada, una hora de integración ya proporciona evidencia fuerte de H₂O, CO₂ y CH₄ en ambos escenarios. En A1, la exposición de 100 h también ofrece evidencia fuerte de O₃. H₂O y CO₂ aportan contexto sobre el ambiente atmosférico, mientras que CH₄ y O₃ forman parte de los gases estudiados como posibles biofirmas. Su interpretación depende de las fuentes capaces de sostenerlos y del entorno planetario, como revisan [Schwieterman et al. (2018)](https://arxiv.org/abs/1705.05791). Estas observaciones proporcionarían información relevante para investigar habitabilidad y ciclos biológicos incluso antes de identificar una perturbación agrícola.

Los gases nitrogenados relacionados con ExoFarm muestran una dependencia mayor de la intensidad del forzamiento. En A1, incluso 100 h proporcionan únicamente evidencia débil de N₂O, con \(\ln B=1.608\pm0.340\), y favorecen omitir NH₃. Una atmósfera con el forzamiento correspondiente al benchmark terrestre actual seguiría ofreciendo un acceso limitado a estos dos trazadores durante la campaña considerada.

En A3, N₂O empieza a resultar identificable con una exposición menor. A 1 h, \(\ln B=0.047\pm0.234\) deja la comparación inconclusa. A 10 h alcanza \(7.388\pm0.291\), superando el nivel de evidencia fuerte, y a 100 h aumenta hasta **\(84.661\pm0.347\)**. En los casos analizados, el forzamiento extremo permite reconocer N₂O desde 10 h, y la exposición de 100 h refuerza considerablemente el apoyo a su inclusión.

Para NH₃, las exposiciones de 1 y 10 h favorecen ligeramente los modelos que la omiten. A3 a 100 h ofrece apoyo positivo, con **\(\ln B=2.749\pm0.345\)** y \(2.85\sigma_{\mathrm{cal}}\): incluir la molécula mejora la evidencia por un factor aproximado de **15.6**. Su valor central corresponde a evidencia moderada, aunque se encuentra próximo al límite de 2.5 respecto de su incertidumbre numérica. Así, a 100 h NH₃ empieza a aportar información molecular complementaria a la evidencia fuerte de N₂O, con un apoyo menor que el obtenido para esta última especie.

### Probabilidad de alcanzar abundancias actuales o intensificadas

La identificación molecular deja abierta la magnitud de la perturbación. **¿El espectro permite abundancias próximas al estado preagrícola o concentra su apoyo en niveles que alcanzan el benchmark agrícola actual?** Para responderlo adoptamos las abundancias efectivas de A1 como umbrales, utilizando la definición presentada anteriormente:

\[
R_{\mathrm{N_2O}}
=
\left\{X_{\mathrm{N_2O}}\geq X_{A1,\mathrm{N_2O}}\right\},
\]

\[
R_{\mathrm{NH_3}}
=
\left\{X_{\mathrm{NH_3}}\geq X_{A1,\mathrm{NH_3}}\right\},
\]

\[
R_{\mathrm{conjunto}}
=R_{\mathrm{N_2O}}\cap R_{\mathrm{NH_3}}.
\]

El criterio ≥ A1 pregunta si la abundancia alcanza o supera el nivel asociado al escenario actual de nuestro modelo. Agrupa ese benchmark y los enriquecimientos mayores, sin exigir que el resultado coincida exactamente con A1 o A3. De esta manera podemos evaluar cuánto apoyo recibe un nivel de perturbación relevante para la secuencia agrícola, antes de intentar distinguir escenarios específicos.

Adaptando al espacio de abundancias el análisis por regiones de [Wogan et al. (2026)](https://doi.org/10.3847/1538-4357/ae6646), calculamos

\[
q_R=P(R\mid D,M_{\mathrm{completo}}).
\]

Esta cantidad representa la probabilidad posterior de que los parámetros atmosféricos se encuentren dentro de la región elegida, dado el espectro y el modelo utilizado. Por ejemplo, \(q_R=0.9\) para NH₃ significaría que el 90 % de su distribución posterior corresponde a abundancias iguales o superiores a su referencia A1.

Estimamos esta probabilidad mediante la fracción de muestras posteriores que satisface cada condición. Cada muestra representa una combinación de parámetros según la distribución inferida. Para la probabilidad conjunta exigimos que ambas abundancias superen sus respectivos umbrales en la misma muestra. Así respondemos si **las dos condiciones pueden cumplirse simultáneamente en una misma atmósfera inferida**, conservando la dependencia entre las moléculas.

| Tiempo | Escenario | \(P(\mathrm{N_2O}\geq A1)\) | \(P(\mathrm{NH_3}\geq A1)\) | \(P(\mathrm{ambas}\geq A1)\) |
|---|:---:|---:|---:|---:|
| 1 h | A1 | 6.57 % | 40.81 % | 2.82 % |
| 1 h | A3 | 17.27 % | 38.51 % | 6.48 % |
| 10 h | A1 | 1.11 % | 28.23 % | 0.38 % |
| 10 h | A3 | 99.90 % | 61.33 % | 61.27 % |
| 100 h | A1 | 0.47 % | 6.13 % | ≈0 % |
| 100 h | A3 | ≈100 % | 98.67 % | 98.67 % |

Estas probabilidades describen la composición inferida dentro del modelo. Su interpretación como probabilidad de agricultura requeriría comparar explícitamente los mecanismos agrícolas y naturales capaces de producirla.

### Cuánto apoyo al enriquecimiento aportan los datos

Una probabilidad posterior elevada puede reflejar, en parte, cómo se distribuyó inicialmente la probabilidad. Si el umbral está cerca del extremo inferior de un prior amplio, gran parte del rango permitido ya lo supera antes de observar el espectro. En ese caso, obtener una probabilidad posterior alta no demuestra por sí solo que los datos hayan fortalecido el enriquecimiento.

Esto resulta importante para nuestros priors uniformes en \(\log_{10}X\in[-12,-1]\), que asignan el mismo peso a cada década de abundancia. El umbral A1 de NH₃ se encuentra en \(\log_{10}X\simeq-9.305\): aproximadamente el 75.50 % del prior ya está por encima. Para N₂O, la proporción previa es 52.13 %, y la independencia nominal de ambos priors proporciona una masa conjunta de 39.35 %.

Para separar ese punto de partida del cambio introducido por el espectro utilizamos

\[
K_R=
\frac{q_R/(1-q_R)}
{q_{0,R}/(1-q_{0,R})},
\]

donde \(q_{0,R}\) es la probabilidad previa de la región. Cada cociente \(q/(1-q)\) compara la probabilidad de encontrarse dentro de la región con la de encontrarse fuera. \(K_R\) indica por cuánto se multiplica esa razón después de incorporar los datos.

Los valores \(K_R>1\) representan un aumento del apoyo relativo a la región; los inferiores a uno representan una reducción. Bajo priors restringidos y normalizados dentro de la región y su complemento, este cociente corresponde a su factor de Bayes. Conservamos los valores como **nominales** hasta verificar las restricciones del prior efectivo completo.

| Tiempo | Escenario | N₂O: \(K_R\;(\ln K_R)\) | NH₃: \(K_R\;(\ln K_R)\) | Ambas: \(K_R\;(\ln K_R)\) |
|---|:---:|---:|---:|---:|
| 1 h | A1 | 0.0646 (−2.739) | 0.224 (−1.497) | 0.0448 (−3.106) |
| 1 h | A3 | 0.192 (−1.652) | 0.203 (−1.593) | 0.107 (−2.237) |
| 10 h | A1 | 0.0103 (−4.573) | 0.128 (−2.058) | 0.00589 (−5.135) |
| 10 h | A3 | 913.85 (6.818) | 0.515 (−0.664) | 2.438 (0.891) |
| 100 h | A1 | 0.00436 (−5.435) | 0.0212 (−3.855) | — |
| 100 h | A3 | — | 23.991 (3.178) | 113.924 (4.736) |

*Las probabilidades extremas se presentan como ≈0 % o ≈100 %. Las rayas señalan factores cuyo cálculo depende de una cola no representada en las muestras disponibles.*

A 10 h, el espectro A3 todavía ofrece poco apoyo a un NH₃ enriquecido. Aunque el 61.33 % de su posterior supera A1, esta proporción es menor que el 75.50 % previo y produce \(K_R=0.515\). El resultado acompaña la comparación molecular anterior, donde \(\ln B=-0.734\pm0.292\) favorecía ligeramente omitir NH₃. Ambos análisis señalan información insuficiente a esta exposición, aunque evalúan preguntas distintas: la inclusión de la molécula y el nivel de su abundancia.

A 100 h, las dos comparaciones ofrecen apoyo positivo a NH₃. Su inclusión recibe evidencia moderada por el valor central y, dentro del modelo completo, la probabilidad de alcanzar o superar A1 asciende al **98.67 %**. El correspondiente **\(K_R=23.99\)** indica que el espectro multiplica por unas 24 la razón entre encontrarse por encima y por debajo del benchmark actual respecto del prior nominal. La probabilidad elevada viene acompañada de una actualización sustancial del apoyo relativo a esa región.

La probabilidad conjunta también alcanza el **98.67 %**, con **\(K_R=113.92\)**. Prácticamente toda la posterior muestreada de N₂O supera A1; por ello, NH₃ limita la fracción que satisface ambas condiciones. El factor conjunto mayor refleja también la menor masa previa de la intersección. Estas cantidades resumen la misma inferencia y deben interpretarse conjuntamente, conservando la dependencia entre las moléculas.

### Magnitud y precisión del enriquecimiento

Superar A1 permite reconocer el nivel de referencia alcanzado, pero deja abierta una cuestión física: **¿el espectro distingue un aumento pequeño de una perturbación varias veces mayor que el benchmark actual?** Para evaluar la amplitud del enriquecimiento y su precisión examinamos

\[
\Delta_i=\log_{10}\left(\frac{X_i}{X_{A1,i}}\right).
\]

Un valor de cero corresponde a A1; uno de 1 dex equivale a multiplicar su abundancia por diez, y uno de aproximadamente 0.3 dex, por dos. Para A3 a 100 h obtenemos:

| Molécula | Mediana \(X_i/X_{A1,i}\) | Intervalo central del 95 % | Mediana de \(\Delta_i\), dex | Anchura del 95 %, dex |
|---|---:|---:|---:|---:|
| N₂O | 4.15 | 3.24–5.18 | 0.618 | 0.204 |
| NH₃ | 13.63 | 2.57–25.38 | 1.134 | 0.994 |

Los intervalos contienen el 95 % central de la probabilidad posterior y dejan un 2.5 % en cada cola. Que su límite inferior supere una referencia significa que la parte central de la distribución favorece abundancias mayores; las colas pueden conservar una probabilidad pequeña por debajo de ella.

Para N₂O, la mediana corresponde a unas **4.1 veces A1** y el intervalo del 95 % se mantiene aproximadamente entre tres y cinco veces ese benchmark. Respecto de A0, la mediana es de **5.86 veces**, con un intervalo de **4.58–7.32 veces**. El espectro permite, dentro del modelo utilizado, situar el enriquecimiento de N₂O claramente por encima de las dos referencias y delimitar su magnitud en un rango relativamente estrecho.

NH₃ también favorece un enriquecimiento considerable. Su mediana alcanza **13.63 veces A1**; el 68 % central de su posterior se encuentra entre **8.15 y 19.48 veces**, y el intervalo central del 95 % abarca **2.57–25.38 veces A1**. La parte central de la distribución queda completamente por encima del benchmark actual. Su anchura de **0.99 dex**, frente a **0.20 dex** para N₂O, muestra que la magnitud de NH₃ sigue siendo menos precisa.

La cola inferior conserva aproximadamente el **1.33 %** de la probabilidad por debajo de A1. Respecto de A0, el **99.13 %** de la posterior supera la referencia, con una mediana de **60.28 veces A0** y un intervalo central del 95 % de **11.38–112.23 veces**. Así, el apoyo a abundancias elevadas de NH₃ es alto, aunque persiste una cola pequeña hacia valores bajos.

Los indicadores anteriores responden preguntas complementarias. En la sección de sensibilidad molecular con LIFE, el NH₃ de A3–100 h alcanzó un **S/N integrado de 4.86**, que describe el tamaño de su plantilla espectral frente al ruido adoptado. La figura de retrievals proporciona ahora **\(z^{\mathrm{desc}}=9.41\)** para su desplazamiento respecto de A0, mientras que la comparación con/sin NH₃ da **\(2.85\sigma_{\mathrm{cal}}\)** a partir de **\(\ln B=2.749\)**.

El valor de \(z^{\mathrm{desc}}\) expresa la separación de la mediana en unidades de la anchura central posterior. Describe una distribución que puede ser asimétrica y tener colas extendidas. En este caso, aproximadamente un **0.87 %** de la posterior conserva NH₃ en A0 o por debajo; por ello, \(z^{\mathrm{desc}}=9.41\) no representa una exclusión gaussiana de A0 a 9.41 sigmas. El conjunto de indicadores muestra una contribución espectral prevista accesible, una posterior concentrada en abundancias enriquecidas y evidencia molecular moderada bajo el modelo analizado.

### Qué aportarán los retrievals restringidos a A0

Las posteriores muestran que el modelo completo concentra su apoyo en abundancias enriquecidas. Para evaluar cuánto mejora la explicación del espectro al permitir ese desplazamiento, la siguiente comparación conservará las opacidades de N₂O y NH₃ y fijará sus abundancias a las referencias A0. Esto permite contrastar directamente la libertad de apartarse de un nivel preagrícola concreto, además de la comparación anterior entre presencia y ausencia molecular.

Seleccionamos **A3 a 100 h**, el caso de la serie que combina evidencia fuerte de N₂O y apoyo positivo a NH₃. Consideramos tres restricciones: N₂O en A0 con NH₃ libre, NH₃ en A0 con N₂O libre, y ambas abundancias en A0. La tercera ofrece una referencia común desde la cual evaluar la mejora que aporta liberar cada especie. En particular, permitir que N₂O se ajuste evita imponer a NH₃ y al resto de parámetros la necesidad de compensar una restricción que puede resultar incompatible con el espectro.

**[PENDIENTE — incorporar los tres contrastes A0 de A3–100 h emparejados con el modelo completo vigente. Reportar sus evidencias, el aporte de liberar cada molécula desde la referencia conjunta y las probabilidades ≥ A1 de la especie que permanece libre. Evaluar si NH₃ conserva apoyo al enriquecimiento después de permitir el ajuste de N₂O.]**

### Síntesis de los análisis

Los resultados disponibles describen una recuperación progresiva de información sobre la perturbación nitrogenada. En A3, N₂O alcanza evidencia molecular fuerte desde 10 h. A 100 h, su posterior delimita un enriquecimiento de aproximadamente tres a cinco veces el benchmark actual, con una incertidumbre considerablemente menor que la de NH₃.

NH₃ aporta a 100 h **evidencia molecular moderada por su valor central** y concentra un **98.67 %** de su posterior en abundancias iguales o superiores a A1. Su intervalo central del 95 % también queda completamente por encima de ese benchmark. El aumento de las odds frente al prior nominal respalda que el espectro añade información sobre el enriquecimiento, aunque su magnitud sigue estando menos delimitada que la de N₂O.

**Dentro de la configuración analizada, A3–100 h permite recuperar con mayor firmeza un N₂O enriquecido y obtener apoyo complementario a la presencia y el enriquecimiento de NH₃.** La probabilidad conjunta de que ambas abundancias alcancen o superen A1 es del **98.67 %**, condicionada al modelo completo. Para el benchmark A1, incluso 100 h mantienen un acceso limitado a los trazadores nitrogenados. Los contrastes A0 pendientes permitirán examinar qué apoyo recibe apartarse de ese estado de referencia.

**[PENDIENTE — A3 a 1000 h: incorporar los contrastes individuales y conjunto frente a A0 una vez cerrada su aceptación. Evaluar el apoyo a liberar NH₃, la anchura posterior y su aporte después de permitir el ajuste de N₂O. Aplicar también los criterios ≥ A1. La evidencia de presencia molecular requerirá comparaciones emparejadas con modelos que omitan cada especie.]**

### Para la sección de Discusión: interpretación y alcance

La recuperación de H₂O, CO₂, CH₄ y O₃ proporciona contexto para investigar condiciones atmosféricas y posibles ciclos biológicos. Interpretar esa composición exige relacionarla con las fuentes y sumideros capaces de sostenerla. Como desarrolla [Wogan et al. (2026)](https://doi.org/10.3847/1538-4357/ae6646), esa conexión depende de la fotoquímica y del entorno físico del planeta.

Para los gases nitrogenados, existen mecanismos naturales que deben considerarse. Grandes flujos biológicos de N₂O pueden aparecer cuando su producción mediante desnitrificación es eficiente y su reducción final a N₂ queda limitada, como discuten [Schwieterman et al. (2022)](https://arxiv.org/abs/2210.01669). NH₃ depende de otro balance: disolución, conversión a NH₄⁺, deposición y captación superficial pueden eliminarla eficazmente, mientras que su acumulación se vuelve más favorable cuando estos sumideros se debilitan o se aproximan a la saturación, según [Huang et al. (2022)](https://arxiv.org/abs/2107.12424).

Las probabilidades ≥ A1 cuantifican apoyo a niveles de composición asociados a nuestros escenarios agrícolas. Para calcular una probabilidad de ExoFarm sería necesario definir distribuciones predictivas para atmósferas agrícolas y naturales, junto con probabilidades previas contextuales para esas hipótesis. Los escenarios A0–A3 constituyen referencias controladas, pero por sí solos no establecen esas distribuciones.

Los resultados dependen también de la representación atmosférica. Los espectros sintéticos contienen perfiles verticales, mientras que el retrieval recupera abundancias constantes; el promedio efectivo de un perfil no tiene por qué coincidir con el valor favorecido por sus contribuciones espectrales. La recuperación de A1 por debajo de su propia referencia muestra la necesidad de conservar estos controles antes de utilizar el umbral como clasificador de escenarios.

Cada dataset utiliza una realización de ruido, por lo que el análisis no establece la frecuencia con que estos resultados se recuperarían en observaciones repetidas. Los factores de región requieren validar el prior efectivo completo, y A1 debe registrarse como un criterio elegido retrospectivamente para esta serie.

El ajuste de A3–100 h también conserva discrepancias respecto del ruido adoptado: su χ² es 57.19 para 31 canales, con un χ² reducido aproximado de 3.36 al contar los 14 parámetros libres. Esta tensión debe examinarse junto con la representación vertical y térmica antes de convertir el resultado de una realización sintética en una predicción general de observabilidad.
