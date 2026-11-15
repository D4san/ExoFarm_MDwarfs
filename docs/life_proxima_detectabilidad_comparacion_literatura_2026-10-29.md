# LIFE Proxima: comparación de detectabilidad con la literatura

**Fecha:** 2026-10-29. **Alcance:** contraste interpretativo de los resultados existentes de A1/A3 con artículos de investigación; no se han ejecutado nuevas simulaciones. Las cifras oficiales permanecen en el [análisis integrado](life_proxima_a1_a3_retrievals_analisis_integrado_2026-10-29.md) y sus tablas; esta nota reúne contexto, comparabilidad y preguntas abiertas, sin crear una segunda versión de resultados.

## Conclusión

La tendencia general es plausible: el infrarrojo térmico puede ser sensible al N₂O alrededor de estrellas cercanas, la señal de NH₃ depende con fuerza de sus sumideros, y la inferencia de cada especie depende de los demás gases y de la estructura térmica. Sin embargo, **la preferencia A3 por incluir N₂O en 10 h es un resultado condicionado de una realización, todavía no una previsión de detectabilidad robusta ni una validación por los trabajos anteriores**. El resultado de NH₃ a 100 h también requiere controlar adecuación de ajuste, priors, química y ruido. La bibliografía demuestra que estos controles pueden ser decisivos.

## Aporte del estudio frente a trabajos anteriores

[Haqq-Misra et al. (2022)](https://doi.org/10.3847/2041-8213/ac65ff) propusieron la combinación de N₂O y NH₃ como candidata a tecnoseñal agrícola. [Haqq-Misra, Kopparapu y Profitiliotis (2025)](https://arxiv.org/abs/2511.20329) ya mostraron espectros LIFEsim con N₂O, CH₄ y NH₃ en escenarios de tecnosfera complejos, para una Tierra a 10 pc, R=50 y 10 días. No corresponde reivindicar la idea ni la primera simulación LIFE de esos gases como novedosas en sí mismas.

El aporte específico de este estudio es conectar escenarios controlados de forzamiento N₂O/NH₃ con fotoquímica vertical, espectros térmicos de un análogo terrestre bajo radiación de Proxima y retrievals a 1, 10 y 100 h; cuantificar diferencias entre modelos completos y ablaciones para cada gas, posterior y prior; y examinar conjuntamente enriquecimiento, detectabilidad y adecuación del ajuste. En los ejemplos analizados el N₂O de A3 es favorecido a 10 h mientras NH₃ aún no lo es. Esto informa una limitación de la estrategia conjunta bajo las hipótesis indicadas. Es una contribución concreta sin afirmar prioridad bibliográfica absoluta; la revisión consultada no es una búsqueda exhaustiva de todos los trabajos publicados.

## Qué se está comparando

Nuestro experimento simula un análogo terrestre bajo radiación de Proxima: distancia 1,30 pc, radio supuesto 1,23 radios terrestres, temperatura y química fijadas por el modelo, y cuatro colectores de 2 m, transmisión óptica 5%, tres exozodis y R≈20 en 31 canales entre 4 y 18,5 μm. El flujo estelar de MUSCLES se usa para la fotoquímica; no constituye una medición de la atmósfera del planeta. La generación de datos utiliza LIFEsim clásico con ruido fotónico asociado, entre otras contribuciones, a fuga estelar y fondos zodiacal y exozodiacal; la likelihood es diagonal y se usa una realización por caso. No incorpora la covarianza temporal instrumental de LIFEsimMC/PHRINGE. La malla interna del forward y la resolución de presentación de figuras no son la resolución de los datos. Fuentes: [metodología](life_proxima_a1_a3_1_10_100h_methodology_2026-10-03.md) y [análisis integrado](life_proxima_a1_a3_retrievals_analisis_integrado_2026-10-29.md).

En cada pareja emparejada, ΔlnZ = lnZ(completo) − lnZ(sin especie). Describe la preferencia entre esos dos modelos para el mismo dataset, su prior y sus hipótesis. Una señal integrada frente a una plantilla fija, una incertidumbre de abundancia y un factor de Bayes de ablación responden preguntas diferentes y no pueden intercambiarse numéricamente.

| A3 | 1 h | 10 h | 100 h |
|---|---:|---:|---:|
| N₂O: ΔlnZ | −0,030 ± 0,235 | +9,142 ± 0,292 | +84,661 ± 0,347 |
| NH₃: ΔlnZ | −0,526 ± 0,234 | −0,226 ± 0,293 | +2,749 ± 0,345 |
| O₃: ΔlnZ | −0,82 | +0,241 ± 0,293 | +20,838 ± 0,342 |

Los errores son numéricos de evidencia combinados en cuadratura; no miden sensibilidad a prior, ruido ni modelo. A 100 h el modelo completo A3 tiene χ² reducido reportado 3,57, con dos canales que exceden |3σ| en la mediana puntual; el cociente usando 14 parámetros libres es 3,36. Los contrastes de 100 h son por tanto condicionales y el ajuste merece examen. La fuente de todos los valores, incluidos los errores redondeados restantes y el resto de moléculas, es la tabla canónica enlazada.

## N₂O: LIFE XII y otros trabajos

[Angerhausen et al., LIFE XII (2024)](https://doi.org/10.3847/1538-3881/ad1f4b) simulan atmósferas oxigenadas con N₂O y muestran que un objetivo muy cercano como Proxima puede requerir mucho menos tiempo que sistemas más lejanos. Su tabla principal para una estrella tipo Proxima usa **5 pc**, resolución R=50 y 10 días: el SNR integrado en bandas es 1,3 para su escenario de 1 Tmol/año y 7,4 para 10 Tmol/año. También muestran por separado un ejemplo de Proxima a 1,3 pc. Sus tiempos y SNR no deben trasladarse de manera directa al ΔlnZ nuestro de 10 h: distancias, perfiles, concentraciones, ruido, resolución y métrica difieren. El artículo encuentra asimismo solapamientos espectrales entre N₂O y otros gases; la comparación entre modelos completos merece atención.

Un contraste fotoquímico concreto es relevante. En el [perfil VULCAN A3](../Photochemical_Modeling/Results/Outputs/Proxima_b_A3_Extreme.vul) el N₂O de superficie es 9,789×10⁻⁷, aproximadamente 0,98 ppm, frente a 2,75 ppm en el escenario Proxima de 1 Tmol/año de [la tabla 13 de LIFE XII](https://arxiv.org/html/2401.08492). Los flujos por unidad de área citados son 1,238×10¹⁰ moléculas cm⁻² s⁻¹ en nuestro A3 y 3,7×10⁹ en aquel escenario. Una emisión bruta mayor junto a una abundancia menor señala distintas relaciones emisión–concentración. No prueba por sí sola cuál modelo es correcto: pueden importar deposición, campo estelar, tasas químicas, transporte y estructura atmosférica. LIFE XII señala que los sumideros superficiales de N₂O son pequeños, mientras nuestro modelo tiene deposición efectiva no nula; se detalla más abajo.

[Schwieterman et al. (2022)](https://doi.org/10.3847/1538-4357/ac8cfb) muestran que abundancias considerables de N₂O también pueden proceder de escenarios microbianos naturales y estudian falsos positivos; su ejemplo de JWST/transmisión para TRAPPIST-1e utiliza otra geometría y no fija el tiempo LIFE de Proxima. La presencia de N₂O por sí sola no identifica agricultura.

[Konrad et al., LIFE III](https://doi.org/10.1051/0004-6361/202141964) recuperan H₂O, CO₂ y O₃ en su análogo terrestre a 10 pc, pero obtienen un límite superior de N₂O; CH₄ depende de resolución y SNR. Ese sistema y sensibilidad son distintos del nuestro y, por tanto, no contradicen que Proxima más cercana sea favorable. [Grenfell et al.](https://doi.org/10.1093/mnras/staf1878) también muestran que las conclusiones para una Tierra alrededor de Proxima cambian al usar otros supuestos y colocar las estrellas de prueba a 10 pc. Estas referencias motivan sensibilidad de resolución y atmósfera, no una validación cruzada de las 10 h.

## NH₃: producción, captación y observabilidad

[Huang et al. (2022)](https://doi.org/10.1089/ast.2020.2358) explican que solubilidad, deposición y otros sumideros pueden impedir la acumulación de NH₃. Su umbral ilustrativo de ~5 ppm corresponde a JWST, transmisión y una atmósfera favorable dominada por H₂; no es un umbral transferible a nuestra atmósfera N₂–O₂ ni a emisión LIFE. [Cesario et al. (2026)](https://doi.org/10.1093/mnras/stag1451) modelan NH₃ como trazador de atmósferas fuertemente reductoras; tampoco son nuestros perfiles oxigenados, pero ayudan a formular alternativas al origen agrícola.

Nuestros resultados van en la dirección cualitativa de un NH₃ difícil: a 10 h, el contraste de inclusión no favorece el modelo completo; a 100 h ΔlnZ=2,749 corresponde a B≈15,6 entre estos modelos bajo el prior utilizado, condicionado además por el desajuste citado. En A3–10 h, P(NH₃≥A1)=73,1% pero su probabilidad previa es 75,5%: la posición de la posterior respecto al umbral no equivale a una detección ni a una probabilidad de agricultura.

## Diagnóstico nuevo: términos inferiores realmente guardados

**Procedencia verificada.** Las velocidades `v_dep=1 cm/s` para NH₃ y `1×10⁻⁴ cm/s` para N₂O coinciden con el [archivo terrestre de la instalación local de VULCAN](../VULCAN/atm/BC_bot_Earth.txt). Las cuatro [plantillas de condiciones inferiores del proyecto](../Photochemical_Modeling/Config/Boundary_Conditions/) conservan esas velocidades y cambian los flujos de los escenarios; el [lanzador Proxima](../Photochemical_Modeling/Scripts/Simulation/run_parallel_proxima.py) coloca cada plantilla en la ruta de VULCAN. Por tanto, los valores provienen de una configuración terrestre ya adoptada y documentada; esta comparación no ha detectado un error de deposición. La diferencia con otros estudios constituye contexto metodológico.

**Cálculo directo sobre el producto, no una nueva simulación.** La configuración Proxima activa `use_botflux` y [VULCAN calcula](../VULCAN/op.py) en la capa inferior la contribución `F_impuesto − v_dep n_superficie`. Las cantidades siguientes provienen de `atm.bot_flux`, `atm.bot_vdep` y `variable.y` de la capa de mayor presión de los `.vul`; las unidades de ambos flujos son moléculas cm⁻² s⁻¹ y las velocidades cm s⁻¹.

| Escenario | Gas | F impuesto | v_dep | v_dep n_superficie | Cociente (v_dep n)/F |
|---|---|---:|---:|---:|---:|
| A0 | N₂O | 1,58×10⁹ | 1×10⁻⁴ | 3,19×10⁸ | 20,16% |
| A1 | N₂O | 2,30×10⁹ | 1×10⁻⁴ | 4,50×10⁸ | 19,59% |
| A3 | N₂O | 1,238×10¹⁰ | 1×10⁻⁴ | 2,363×10⁹ | 19,09% |
| A0 | NH₃ | 2,94×10⁹ | 1 | 2,935×10⁹ | 99,842% |
| A1 | NH₃ | 1,30×10¹⁰ | 1 | 1,298×10¹⁰ | 99,826% |
| A3 | NH₃ | 1,54×10¹¹ | 1 | 1,538×10¹¹ | 99,850% |

Estos cocientes cuantifican los dos términos del límite inferior **en los perfiles guardados y bajo la parametrización adoptada**; no son una medición del planeta ni una estimación independiente de la fracción de moléculas individuales que se deposita. En particular, no atribuyen el sumidero a un proceso específico ni permiten extrapolar linealmente una alternativa. Para NH₃ los términos casi se compensan y el aporte neto al dominio es sensible al modelo de superficie. Para N₂O la contribución de deposición tampoco es cero. Los resultados actuales responden válidamente al experimento definido con la configuración terrestre de VULCAN; estudiar otras superficies o velocidades sería una extensión de sensibilidad opcional. No se deben inferir sus resultados sin ejecutarla. Una [propuesta previa de captación reducida de NH₃](nh3_reduced_capture_extra_phase_proposal_2026-10-13.md) sigue sin ejecutarse.

## O₃ y los demás gases

A 10 h el contraste O₃ es cercano a cero para A1 (+0,100 ± 0,294) y A3 (+0,241 ± 0,293); el resultado no aporta apoyo claro a la presencia de O₃ bajo este contraste. A 100 h los valores se vuelven positivos, sujetos a adecuación del modelo, sobre todo en A3. [Braam y Angerhausen (2026)](https://arxiv.org/abs/2512.16619), con un modelo 3D de un acuaplaneta tipo Proxima b, encuentran que nubosidad, fase y perfil térmico pueden modificar o hacer desaparecer la característica de O₃. Su análisis de variabilidad de fase no es una ablación ni da un umbral comparable al nuestro.

En nuestra realización A3, H₂O, CO₂ y CH₄ presentan fuerte preferencia por inclusión; LIFE III también muestra potencial para esas especies en su escenario, con dependencias de la sensibilidad y resolución. Las magnitudes numéricas de ΔlnZ de modelos distintos no equivalen a una certeza observacional universal. [Mettler et al.](https://arxiv.org/html/2310.02634), usando espectros reales de la Tierra, muestran sesgos asociados a nubosidad, estructura y degeneraciones. En nuestro control de forward con perfil verdadero y abundancias constantes [la diferencia espectral sin ajustar es notable](life_proxima_a3_vertical_life_isochem_comparison_2026-10-14.md); esto no demuestra que sea el residual del mejor ajuste ni identifica por sí solo al gas causante.

## Alcance y posibles mejoras según recursos

El conjunto disponible permite publicar o discutir resultados **condicionados a los modelos y realizaciones analizados**, sujeto a la evaluación científica habitual. No es necesario ejecutar muchas realizaciones adicionales para que los resultados existentes sean útiles. Con una realización por caso no se mide la dispersión de resultados entre realizaciones, y el A1–1 h se eligió entre dos. La incertidumbre numérica de evidencia no representa esa variación.

1. Aprovechar posteriores, espectros y diagnósticos ya guardados para explicar ajustes, degeneraciones, prior y diferencias entre presencia molecular y regiones de abundancia. Si resulta útil, un análisis de señales con espectros fijos y ruido analítico podría ser económico, pero no sustituiría retrievals repetidos ni mediría por sí solo la dispersión de ΔlnZ.
2. Mantener documentados los perfiles verticales y sus diferencias con `isochem`; la comparación sin optimización no representa el residual del mejor ajuste.
3. Diferenciar emisión impuesta, deposición terrestre de referencia de VULCAN, flujo neto y perfiles resultantes. Controles fotoquímicos alternativos y múltiples realizaciones son estudios de sensibilidad futuros, opcionales y sujetos a disponibilidad de cómputo.
4. Incorporar covarianza y supuestos instrumentales realistas. [Huber et al.](https://arxiv.org/html/2508.15756) encuentran que las correlaciones pueden sesgar la extracción y que el blanqueo con covarianza conocida puede mitigar efectos, con pérdidas dependientes de perturbación y calibración. No se puede asumir que todo efecto instrumental siempre degrada igual.
5. Tratar P(X≥A1) y su actualización K como resultados condicionales a los priors de abundancia, sin llamarlos probabilidades de agricultura. Una comparación causal necesita alternativas naturales/abióticas y un vínculo incierto entre espectro, abundancia y flujo; [Wogan et al.](https://arxiv.org/abs/2604.21848) ofrecen una vía de inferencia de flujos para otro sistema. La decisión previa de reutilizar posteriores existentes para la pregunta de regiones se mantiene.

El análisis de comparación no ha cambiado productos, resultados sellados ni configuraciones y no ha lanzado retrievals.
