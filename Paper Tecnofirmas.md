---
aliases:
date: 2025-12-09
tags:
  - maestria
curso:
bibliografía:
---
# TÍTULO (Propuesta):

**The M-Dwarf Amplifier: Enhanced Accumulation of Agricultural Technosignatures (**$N_2O$**,** $NH_3$**) in TRAPPIST-1e Atmospheres**

Autores: $$

Tu Nombre

$$ , $$

Colaboradores si los hay

$$ **Afiliación:** $$ Tu Universidad/Instituto$$

## 📄 RESUMEN (Abstract)

La búsqueda de tecnofirmas atmosféricas requiere identificar gases que indiquen un desequilibrio termodinámico insostenible por procesos naturales. En este trabajo, investigamos la detectabilidad de la agricultura industrial ("ExoFarms") en exoplanetas habitables, analizando cómo el entorno de radiación estelar modula la vida media de gases nitrogenados sintéticos. Utilizando el modelo de cinética fotoquímica 1D VULCAN, simulamos atmósferas tipo Tierra orbitando una estrella solar (G2V) y una enana ultra-fría (TRAPPIST-1, M8V) bajo flujos de emisión superficial de $N_2O$ y $NH_3$ que escalan desde niveles preindustriales hasta una ecumenópolis agrícola (100x la tasa terrestre actual).

Nuestros resultados demuestran que el entorno deficiente en UV cercano (NUV) de TRAPPIST-1e actúa como un "amplificador fotoquímico" selectivo para las emisiones agrícolas. Reportamos que (1) la abundancia de $N_2O$ en superficie se amplifica hasta un factor de ~3.6x respecto al caso solar para el mismo flujo industrial; (2) el $NH_3$, aunque limitado en superficie por deposición, experimenta una supervivencia vertical dramáticamente mayor, saturando la columna atmosférica en TRAPPIST-1e mientras es destruido en la Tierra; y (3) contrariamente a la hipótesis de una "atmósfera reductora", la concentración de radicales hidroxilo ($OH$) se mantiene robusta, confirmando que la acumulación se debe al cese de la fotólisis directa y no a una falla en la capacidad oxidativa. Concluimos que, si bien el sistema M8V favorece la acumulación de tecnofirmas nitrogenadas, presenta desafíos significativos para la caracterización contextual debido a la baja abundancia basal de ozono ($O_3$), cuya producción fotolítica es ineficiente en estos entornos estelares. Esto posiciona al par $N_2O+NH_3$ como un objetivo prioritario pero complejo para la caracterización con el JWST.

## 1. INTRODUCCIÓN

La caracterización de atmósferas exoplanetarias ha transitado de la detección de componentes mayoritarios a la búsqueda de trazas de gases que indiquen desequilibrio químico. En este contexto, la distinción entre biosignaturas (vida simple) y tecnosignaturas (civilizaciones avanzadas) es fundamental para la astrobiología (Seager, 2014; Tarter, 2007). Mientras que muchas tecnofirmas propuestas, como los contaminantes industriales (CFCs) o la combustión de hidrocarburos ($NO_2$), dependen de recursos finitos y podrían representar fases transitorias de una civilización, la agricultura representa una tecnología potencialmente longeva. Como argumentan Haqq-Misra et al. (2022), la fijación industrial de nitrógeno solo requiere energía, agua y una atmósfera de $N_2$, recursos renovables que permitirían a una "ExoFarm" sostenerse durante escalas de tiempo geológicas, maximizando así su probabilidad de detección.

La agricultura intensiva constituye una intervención directa en el ciclo del nitrógeno planetario. En la Tierra, la invención del proceso Haber-Bosch permitió la fijación sintética de $N_2$ a tasas que hoy rivalizan con la fijación biológica natural (Battye et al., 2017). Esta disrupción genera dos subproductos gaseosos principales: el Óxido Nitroso ($N_2O$), liberado por la desnitrificación microbiana acelerada de fertilizantes, y el Amoníaco ($NH_3$), volatilizado directamente desde suelos y ganadería. Aunque el $N_2O$ ha sido estudiado extensamente como biosignatura (Schwieterman et al., 2022), la acumulación simultánea de $NH_3$ —un gas altamente soluble y de vida corta— en una atmósfera oxidante rica en $O_2$ es termodinámicamente improbable sin una fuente de producción continua y masiva, convirtiendo a este par de gases en una tecnofirma combinada robusta (Haqq-Misra et al., 2022).

La detectabilidad de estas especies depende críticamente del entorno estelar. Las estrellas enanas M, como el sistema TRAPPIST-1, presentan un régimen de radiación único: poseen un flujo en el Ultravioleta Cercano (NUV, 200-300 nm) órdenes de magnitud menor que el del Sol. Históricamente, se ha debatido si este déficit de UV impide la formación de radicales hidroxilo ($OH$), el principal agente oxidante atmosférico derivado de la fotólisis del ozono y agua. Una atmósfera pobre en $OH$ podría volverse "reductora", permitiendo la acumulación abiótica de gases como metano o amoníaco, generando falsos positivos (Segura et al., 2005; Grenfell et al., 2013). Por tanto, es crucial determinar si una detección de $NH_3$ en un planeta tipo M es señal de tecnología o simplemente el resultado de una química atmosférica perezosa.

Por tal motivo, este trabajo busca evaluar los efectos de la agricultura a gran escala en la acumulación de gases tecnofirma clave ($NH_3$ y $N_2O$) mediante el uso de modelos fotoquímicos autoconsistentes, cuantificando simultáneamente cómo el entorno radiativo de la estrella anfitriona (Sol vs. Enana M) modula dicha acumulación. Para ello, el estudio se estructura en las siguientes secciones: en la **Metodología (Sección 2)** describimos el uso del modelo VULCAN y la construcción de los escenarios de emisión agrícola. En **Resultados (Sección 3)**, presentamos secuencialmente el impacto del entorno radiativo, la respuesta vertical de las especies, las tendencias globales de abundancia y la validación de la química de oxidantes. Finalmente, en la **Discusión (Sección 4)**, analizamos las implicaciones de estos hallazgos para la detectabilidad con telescopios como el JWST y los posibles efectos colaterales sobre biofirmas clave como el ozono.

## 2. METODOLOGÍA

### 2.1 Modelo Fotoquímico

Empleamos el código de cinética química 1D **VULCAN** (Tsai et al., 2017), utilizando la red de reacciones estándar proporcionada por la distribución del modelo (`NCHO_earth_photo_network`). Esta red incluye un total de **47 especies químicas** (abarcando gases clave como $N_2O$, $NH_3$, $O_3$, $CH_4$, $CO_2$, $H_2O$, y radicales fundamentales como $OH$, $O$, y $H$).

La red resuelve un total de **715 reacciones**, cuyas constantes de velocidad y secciones eficaces provienen de las bases de datos validadas de VULCAN (NIST, JPL Kinetics), desglosadas en:

- 528 reacciones de dos cuerpos.
    
- 88 reacciones de tres cuerpos (importantes para la formación de ozono y recombinación a altas presiones).
    
- 99 reacciones de fotodisociación dependientes del espectro estelar.
    

Esta configuración está optimizada para simular atmósferas oxidantes dominadas por $N_2-O_2$ bajo diferentes regímenes de irradiación.

### 2.2 Parámetros del Sistema

Se modeló un planeta con parámetros físicos terrestres ($1 R_{\oplus}$, $g=980$ cm/s$^2$). Para garantizar la reproducibilidad y aislar las variables fotoquímicas, adoptamos los perfiles atmosféricos estándar incluidos en la librería de VULCAN:

- **Perfil T-P:** Se utilizó el perfil de la Atmósfera Estándar de EE.UU. 1976 proporcionado por defecto en el modelo (`atm_Earth_standard`), manteniendo la estructura térmica fija para todas las simulaciones.
    
- **Transporte Vertical (**$K_{zz}$**):** Empleamos el perfil de difusión parmetrizada estándar de VULCAN para atmósferas terrestres. Este perfil simula una mezcla convectiva eficiente en la troposfera que decae en la estratosfera, aplicándose idénticamente a ambos casos estelares.
    
    - _Justificación:_ Aunque la meteorología de un planeta con acoplamiento de marea (tidally locked) diferiría, mantenemos el $K_{zz}$ estándar para aislar el efecto puramente radiativo/químico.
        

### 2.3 Entornos Estelares

Para aislar el impacto de la distribución espectral de energía (SED) en la fotoquímica, seleccionamos dos casos extremos representativos:

1. **G2V (Sol):** Utilizamos el espectro solar estándar incluido en la distribución de VULCAN (basado en Gueymard, 2004) como caso de control, representando un entorno con alto flujo de UV Cercano (NUV, 200–400 nm).
    
2. **M8V (TRAPPIST-1):** Empleamos datos observacionales combinados del programa _Mega-MUSCLES_ (Wilson et al., 2021), que integran observaciones UV del Hubble y modelos de rayos X. Los flujos fueron escalados geométricamente para representar la irradiación bolométrica en la órbita de TRAPPIST-1e (S = 0.66 $S_{\oplus}$). Este espectro se caracteriza por una emisión NUV extremadamente baja, pero una alta actividad en Lyman-$\alpha$ y XUV.
    

### 2.4 Definición de Escenarios de Emisión "ExoFarm"

Existe una distinción metodológica clave en este trabajo respecto a la literatura previa. Mientras que Haqq-Misra et al. (2022) simularon escenarios agrícolas fijando abundancias atmosféricas constantes, nosotros adoptamos un enfoque físico más dinámico definiendo **condiciones de frontera de flujo superficial** ($\Phi$, en moléculas cm$^{-2}$ s$^{-1}$). Esto permite que la atmósfera evolucione libremente hacia un estado de equilibrio fotoquímico (_steady-state_) determinado por la eficiencia de destrucción de cada estrella, en lugar de imponer la concentración final.

Los escenarios se construyeron escalando los flujos terrestres actuales basándonos en el presupuesto global de nitrógeno (Tabla 1):

- **Escenario A1 (Referencia Actual):** Se adoptaron los flujos superficiales de la Tierra moderna calibrados según Tian et al. (2020).
    
- **Escenario A0 (Pre-Agrícola):** Para aislar la señal tecnológica, establecemos una línea base puramente biológica restando el componente antropogénico estimado (40% para $N_2O$, 80% para $NH_3$).
    
- **Escenarios A2 y A3 (ExoFarms):** Modelan civilizaciones con mayor demanda alimentaria, aplicando factores de escala multiplicativos (10x y 100x) a los flujos totales, consistentes con los límites de capacidad de carga planetaria (Cohen, 1995; Haqq-Misra et al., 2022).
    

Tabla 1. Resumen de Flujos Superficiales de Nitrógeno para los Escenarios Simulados.

Valores en moléculas cm$^{-2}$ s$^{-1}$.

|   |   |   |   |   |   |
|---|---|---|---|---|---|
|**ID**|**Escenario**|**Descripción**|**Factor N2​O**|**Factor NH3​**|**Justificación**|
|**A0**|Pre-Agri|Base Natural|0.6x Actual|0.2x Actual|Eliminación de fuentes antropogénicas.|
|**A1**|Actual|Tierra Moderna|1.0x ($1.5 \text{e}9$)|1.0x ($1.5 \text{e}9$)|Calibración con presupuesto global actual.|
|**A2**|ExoFarm-10|Intensiva|10x Actual|10x Actual|Población ~80 mil millones.|
|**A3**|ExoFarm-100|Ecumenópolis|100x Actual|100x Actual|Límite de carga planetaria.|

### 2.5 Diseño Experimental Comparativo

La metodología central consistió en un diseño factorial cruzado. Sometimos los cuatro regímenes de emisión (A0, A1, A2, A3) idénticos a los dos entornos radiativos distintos (Sol vs. TRAPPIST-1).

## 3. RESULTADOS

El análisis se estructura en cinco componentes: el forzamiento radiativo, la respuesta vertical de las especies, las tendencias químicas acopladas ($O_3$, $CH_4$), la amplificación relativa en superficie y la validación de la capacidad oxidativa.

### 3.1 El Entorno Radiativo (La Causa)

La comparación de los espectros estelares (Fig. 1) revela dos regímenes distintos. En longitudes de onda cortas (<150 nm), TRAPPIST-1e (línea roja) exhibe una intensa actividad cromosférica, dominada por la línea de emisión Lyman-$\alpha$, con flujos que rivalizan o superan al Sol. Sin embargo, en la región crítica del Ultravioleta Cercano (NUV, 200-350 nm), se observa una discrepancia fundamental: el flujo solar supera al de TRAPPIST-1 por factores de $10^3-10^4$. Dado que las secciones eficaces de absorción del $N_2O$ y $NH_3$ alcanzan su máximo precisamente en esta banda "silenciosa" del NUV, la atmósfera de TRAPPIST-1e experimenta tasas de fotólisis ($J$-values) drásticamente reducidas para estas especies, a pesar de la alta energía disponible en el UV extremo (Schwieterman et al., 2022).

_(Aquí insertaremos `stellar_spectra_comparison.jpg` como Figura 1)_

### 3.2 Perfiles Verticales de Mezcla (El Mecanismo)

La Figura 2 presenta la distribución vertical de las especies clave, incluyendo los principales oxidantes. Las diferencias en la escala de altura química son determinantes para observaciones de transmisión.

_(Aquí insertaremos `star_comparison_profiles_OH.jpg` como Figura 2)_

1. **Tecnofirmas Nitrogenadas (**$N_2O, NH_3$**):**
    
    - En el sistema Tierra-Sol (líneas sólidas), ambos gases sufren una rápida destrucción en la estratosfera media ($<10^{-2}$ bar) debido a la penetración de UV.
        
    - En TRAPPIST-1e (líneas punteadas), los perfiles se mantienen casi isovariantes (mezclados verticalmente) hasta presiones mucho menores ($10^{-4}$ bar). Esto es crítico, ya que el $N_2O$ alcanza la alta atmósfera donde los telescopios espaciales tienen mayor sensibilidad.
        
2. **El Comportamiento del Ozono (**$O_3$**) y Metano (**$CH_4$**):**
    
    - **Ozono:** En el caso solar, observamos una capa de ozono bien definida (pico en $10^{-2}$ bar). En TRAPPIST-1e, la estructura es más compleja y la abundancia total es menor, consistente con una menor producción de $O$ atómico por fotólisis de $O_2$.
        
    - **Metano:** Muestra una divergencia extrema. En el Sol, el $CH_4$ decrece con la altura; en TRAPPIST-1e, se mantiene robusto y abundante ($\sim 10^{-4}$) en toda la columna, lo cual discutiremos en las tendencias globales.
        
3. **Estabilidad de la Capacidad Oxidativa (**$OH$**):**
    
    - El análisis del perfil vertical del radical hidroxilo ($OH$, línea negra discontinua) revela un hallazgo clave: su concentración en TRAPPIST-1e **no desaparece**. De hecho, en la troposfera alta y estratosfera baja, los niveles de OH son comparables a los del caso solar. Esto indica que la atmósfera de TRAPPIST-1e se mantiene oxidante y que la química de radicales sigue activa, a pesar del diferente espectro estelar.
        

### 3.3 Tendencias de Abundancia Atmosférica (Química Acoplada)

La Figura 3 resume la abundancia media de columna para las cuatro especies a través de los regímenes agrícolas. Este gráfico permite analizar el impacto sistémico de la ExoFarm.

_(Aquí insertaremos `star_comparison_trends.jpg` como Figura 3)_

- Acoplamiento $N_2O$ - $O_3$ (Ciclo de los NOx):
    
    En el sistema solar (círculos naranjas), observamos una clara anticorrelación: a medida que aumenta el $N_2O$ (agricultura intensiva), disminuye el $O_3$. Esto es evidencia del ciclo catalítico de destrucción de ozono por óxidos de nitrógeno ($NO_x$), producidos por la fotólisis del $N_2O$ ($N_2O + h\nu \rightarrow N_2 + O(1D)$). En TRAPPIST-1e, aunque el $N_2O$ es más abundante, la menor energía de fotones limita la producción de $O(1D)$, resultando en una respuesta del ozono más plana.
    
- Estabilidad del Metano ($CH_4$):
    
    El sistema TRAPPIST-1e (triángulos azules) muestra niveles de $CH_4$ consistentemente altos e insensibles a la intensidad agrícola. Esto sugiere que el planeta opera en un régimen químico distinto, donde el metano no es eficientemente oxidado, actuando como un gas de fondo dominante junto al $N_2$ y $CO_2$.
    

### 3.4 Amplificación Superficial Normalizada (El Resultado)

Para aislar el beneficio observacional de las enanas M, normalizamos las concentraciones superficiales respecto a la línea base de la Tierra actual (Figura 4).

_(Aquí insertaremos `surface_normalization_bars.jpg` como Figura 4)_

- **El Dominio del** $N_2O$**:** El ratio de amplificación del óxido nitroso es extraordinario. Para un aumento de flujo de 100x (Escenario A3), la abundancia de $N_2O$ en TRAPPIST-1e aumenta **250x** respecto a la base, mientras que en el Sol solo aumenta ~70x. Esto convierte al $N_2O$ en la tecnofirma más sensible en términos absolutos de masa acumulada.
    
- **La Sutileza del** $NH_3$**:** A primera vista, la amplificación superficial del amoníaco parece modesta (~114x en M8V vs ~75x en G2V). Esto se debe a que la **deposición en superficie** (un proceso físico independiente de la estrella) actúa como un sumidero dominante en las capas bajas, "anclando" las concentraciones. Sin embargo, esta métrica superficial es engañosa para la detectabilidad remota. Como observamos en la Figura 2, la diferencia real radica en la **supervivencia vertical**: mientras el $NH_3$ solar desaparece a pocos kilómetros del suelo, el $NH_3$ en TRAPPIST-1e permea toda la columna atmosférica, ofreciendo una sección eficaz de absorción integrada mucho mayor para un observador externo.
    

## 4. DISCUSIÓN

### 4.1 Mecanismos Químicos: Dominio de la Fotólisis sobre la Oxidación

Uno de los mayores riesgos al proponer biosignaturas en enanas M es el falso positivo por "acumulación abiótica" en atmósferas reductoras, donde la falta de UV impide la formación de OH (Grenfell et al., 2013).

Nuestro análisis de radicales (Resultados 3.2, ítem 3) permite descartar este escenario para nuestra simulación. La persistencia del OH en TRAPPIST-1e indica que la atmósfera mantiene su capacidad oxidativa. Por lo tanto, la acumulación masiva de $N_2O$ y $NH_3$ que reportamos **no se debe a la incapacidad de la atmósfera para limpiarse químicamente (**$k_{OH}$**), sino casi exclusivamente a la ausencia de fotodisociación directa (**$J_{values}$**)**.

Siguiendo el marco cinético establecido por Segura et al. (2005) y Grenfell et al. (2013), la tasa de pérdida ($L$) de una especie traza como el $NH_3$ está gobernada por la competencia entre dos sumideros principales:

$$L_{NH3} = J_{NH3}[NH_3] + k_{OH}[OH][NH_3]$$

En el caso solar, el término de fotólisis ($J_{NH3}$) domina en la atmósfera superior, resultando en una destrucción rápida. En TRAPPIST-1e, el término $J_{NH3}$ se reduce drásticamente debido al espectro estelar. Aunque el término de oxidación ($k_{OH}[OH]$) sigue activo (como demuestra la presencia de OH en nuestros resultados), es insuficiente por sí solo para contrarrestar los flujos de emisión industriales al mismo ritmo. Esto fortalece la propuesta del $NH_3$ como tecnofirma en este contexto: su presencia no es un accidente geoquímico de una atmósfera inerte, sino una anomalía en una atmósfera químicamente activa.

### 4.2 Implicaciones para la Detectabilidad (JWST)

Considerando un umbral de detectabilidad conservador de ~1 ppm ($10^{-6}$) para observaciones de transmisión con el JWST (NIRSpec/MIRI):

1. **En G2V:** Detectar agricultura requeriría niveles extremos (Escenario A3) para el $N_2O$. El $NH_3$ permanece siempre por debajo de niveles de detección fácil, requiriendo instrumentos de altísima precisión.
    
2. **En M8V:** El $N_2O$ cruza el umbral de detectabilidad cómodamente desde el escenario A2. Aunque el $NH_3$ se mantiene en el rango de ppb, su mayor escala de altura y su coexistencia con niveles masivos de $N_2O$ podrían facilitar la detección de características espectrales conjuntas, diferenciándolo de un escenario puramente abiótico.
    

Esto sugiere que TRAPPIST-1e es un objetivo prioritario. La detección simultánea de $N_2O$ masivo y trazas de $NH_3$ sería un indicador robusto de un desequilibrio termodinámico severo, ya que mantener $NH_3$ a esos niveles sin una fuente industrial constante es improbable en atmósferas ricas en oxígeno.

Sin embargo, para confirmar la detectabilidad real, es indispensable realizar **simulaciones de transferencia radiativa** (espectros de transmisión o emisión) basadas en estos perfiles verticales. La abundancia a lo largo de la vertical es la que determina la profundidad óptica y la intensidad de las bandas de absorción resultantes. Solo modelando el espectro sintético podremos determinar si estas concentraciones enriquecidas producen una señal (S/N) suficiente para ser distinguida del ruido instrumental y de otras especies solapantes en observaciones futuras con el JWST o telescopios terrestres de siguiente generación.

### 4.3 Efectos Colaterales: Ozono y Metano

La discusión no puede limitarse a los gases tecnofirma; los efectos colaterales sobre el fondo atmosférico son igualmente reveladores.

- **Impacto en el Escudo de Ozono:** En un planeta tipo Tierra-Sol, la agricultura intensiva (A3) deprime significativamente la capa de ozono debido a la producción de $NO_x$ por fotólisis de $N_2O$, lo que comprometería la habitabilidad superficial. En TRAPPIST-1e, este efecto destructivo es mitigado por la falta de UV energético. Sin embargo, es fundamental notar que la abundancia basal de ozono en TRAPPIST-1e es ya de por sí baja (~$10^{-9}$ vs ~$10^{-7}$ en el Sol) debido a la escasa fotólisis de $O_2$. Por tanto, aunque la agricultura no destruye catastróficamente la capa de ozono en M8V (porque ya es tenue), la detección conjunta de $O_3$ y tecnofirmas será desafiante debido a la debilidad inherente de la señal de ozono en estos sistemas.
    
- **Riesgo de Brumas de Metano:** Los altos niveles de $CH_4$ (~$10^{-4}$) observados en TRAPPIST-1e plantean un desafío. Con una relación $CH_4/CO_2$ que se acerca a 0.1, se favorece la formación de brumas orgánicas fotoquímicas (similares a Titán). Estas brumas podrían aplanar el espectro de transmisión, dificultando la detección de otras especies, pero también podrían servir como un escudo UV adicional para la habitabilidad superficial.
    

### 4.4 Retroalimentación Climática y Limitaciones Dinámicas

Una limitación de este estudio es el uso de un perfil T-P fijo. El $N_2O$ es un potente gas de efecto invernadero. Abundancias de $10^{-4}$ (~87 ppm) en el escenario A3 podrían inducir un calentamiento significativo. Futuros trabajos deberían acoplar un modelo radiativo-convectivo para evaluar si una ExoFarm extrema calentaría el planeta hasta hacerlo inhabitable ("Invernadero Agrícola").

Adicionalmente, el uso de un coeficiente de transporte vertical ($K_{zz}$) terrestre es una aproximación de primer orden. En planetas con acoplamiento de marea alrededor de enanas M, como TRAPPIST-1e, la circulación atmosférica está dominada por una fuerte redistribución de calor día-noche, lo que podría generar patrones de mezcla vertical muy diferentes (e.g., corrientes ascendentes vigorosas en el punto subestelar). Esta dinámica 3D, no explorada en este modelo 1D, podría alterar la distribución vertical de los gases tecnofirma y, por ende, su señal espectral.

## 5. CONCLUSIONES

Este estudio confirma que el entorno fotoquímico de las estrellas enanas M juega un papel determinante en la viabilidad de detectar tecnofirmas agrícolas en exoplanetas. Mediante simulaciones autoconsistentes, hemos demostrado que la acumulación atmosférica de gases como el $N_2O$ y el $NH_3$ no depende únicamente de la intensidad de la fuente industrial (la "ExoFarm"), sino que está profundamente modulada por la distribución espectral de la estrella anfitriona. Específicamente, la deficiencia de radiación UV en estrellas como TRAPPIST-1 actúa como un mecanismo de protección que extiende la vida media de estas moléculas, permitiendo que señales tecnológicas modestas se amplifiquen hasta niveles potencialmente detectables.

A partir de este análisis, sintetizamos los siguientes hallazgos principales:

1. **Amplificación Selectiva del** $N_2O$**:** El óxido nitroso se revela como la tecnofirma más sensible al cambio de tipo estelar, experimentando una amplificación de hasta 3.6 veces en su abundancia superficial y extendiendo su presencia verticalmente en la atmósfera de TRAPPIST-1e, lo que lo convierte en un objetivo primario para la caracterización.
    
2. **Supervivencia Vertical del** $NH_3$**:** Aunque la deposición superficial limita el crecimiento del amoníaco en las capas bajas, el entorno de la enana M permite que este gas sobreviva el transporte vertical y sature la alta atmósfera, a diferencia de su destrucción total en análogos solares. Esto abre una ventana de detectabilidad espectral por transmisión que no existe en la Tierra.
    
3. **Robustez de la Señal Oxidante:** Nuestros modelos descartan que esta acumulación sea un falso positivo causado por el colapso de la capacidad oxidativa atmosférica. La persistencia de radicales $OH$ confirma que el mecanismo dominante es la supresión de la fotólisis directa, validando el uso de estos gases como marcadores en atmósferas oxigenadas.
    
4. **Compromisos Sistémicos:** La ventaja observacional viene acompañada de desafíos complejos, como la baja abundancia basal de ozono (que dificulta su uso como biofirma contextual) y la saturación de metano, que podría introducir opacidades por brumas orgánicas.
    

## 6. BIBLIOGRAFÍA

- **Battye, W., et al. (2017).** Is nitrogen the next carbon?. _Earth's Future_, 5(9), 894-904.
    
- **Cohen, J. E. (1995).** Population growth and earth's human carrying capacity. _Science_, 269(5222), 341-346.
    
- **Grenfell, J. L., et al. (2013).** Potential biosignatures in super-Earth atmospheres. _Astrobiology_, 13(5), 415-438.
    
- **Gueymard, C. A. (2004).** The sun's total and spectral irradiance for solar energy applications and solar radiation models. _Solar Energy_, 76(4), 423-453.
    
- **Haqq-Misra, J., et al. (2022).** Disruption of a Planetary Nitrogen Cycle as Evidence of Extraterrestrial Agriculture. _The Astrophysical Journal Letters_, 929(2), L28.
    
- **Mullan, B., & Haqq-Misra, J. (2019).** Population growth, energy use, and the implications for the search for extraterrestrial intelligence. _Futures_, 106, 4-17.
    
- **Reay, D. S., et al. (2012).** Global agriculture and nitrous oxide emissions. _Nature Climate Change_, 2(6), 410-416.
    
- **Schwieterman, E. W., et al. (2022).** Evaluating the Plausible Range Of N2O Biosignatures On Exo-Earths: An Integrated Biogeochemical, Photochemical, And Spectral Modeling Approach. _The Astrophysical Journal_, 937(2), 109.
    
- **Seager, S. (2014).** The future of spectroscopic life detection on exoplanets. _Proceedings of the National Academy of Sciences_, 111(35), 12634-12640.
    
- **Segura, A., et al. (2005).** Biosignatures from Earth-like planets around M dwarfs. _Astrobiology_, 5(6), 706-725.
    
- **Seinfeld, J. H., & Pandis, S. N. (2016).** _Atmospheric chemistry and physics: from air pollution to climate change_ (3rd ed.). John Wiley & Sons.
    
- **Smith, C., et al. (2020).** Green ammonia production technologies for fertilizer supply. _Energy & Environmental Science_, 13(2), 331.
    
- **Soloveichik, G. (2019).** Electrochemical synthesis of ammonia as a potential alternative to the Haber-Bosch process. _Nature Catalysis_, 2(5), 377-380.
    
- **Tarter, J. C. (2007).** The evolution of life in the universe: are we alone? _Highlights of Astronomy_, 14, 14-20.
    
- **Tian, H., et al. (2020).** A comprehensive quantification of global nitrous oxide sources and sinks. _Nature_, 586(7828), 248-256.
    
- **Tsai, S.-M., et al. (2017).** VULCAN: An Open-source, Validated Chemical Kinetics Python Code for Exoplanetary Atmospheres. _Astrophysical Journal Supplement Series_, 228(2), 20.
    
- **Wilson, D. J., et al. (2021).** The Mega-MUSCLES Spectral Energy Distribution Of TRAPPIST-1. _The Astrophysical Journal_, 911(2), 18.