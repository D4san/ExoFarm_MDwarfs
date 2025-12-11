# Simulación de Biosignaturas Agrícolas en Exoplanetas: Introducción y Metodología

## 1. Introducción

La búsqueda de vida fuera del Sistema Solar ha transitado de la detección de exoplanetas a la caracterización de sus atmósferas. En este contexto, la distinción entre biosignaturas (gases producidos por vida simple) y tecnosignaturas (evidencia de tecnología o civilizaciones avanzadas) se ha vuelto un campo de estudio crucial (Seager, 2014; Kaltenegger, 2017). Una intersección interesante entre ambas categorías es la "agricultura planetaria" o "ExoFarm", donde la actividad biológica es amplificada artificialmente a escala global para sostener una población masiva.

Este estudio se centra en dos gases clave asociados a la actividad biológica y agrícola en la Tierra: el óxido nitroso ($N_2O$) y el amoníaco ($NH_3$). En la Tierra, el $N_2O$ es producido principalmente por bacterias desnitrificantes, pero su abundancia ha aumentado significativamente debido al uso de fertilizantes nitrogenados (Tian et al., 2020). Schwieterman et al. (2022) proponen que niveles elevados de $N_2O$ en una atmósfera exoplanetaria podrían servir como una biofirma robusta, e incluso una tecnofirma si los flujos exceden lo explicable por biología natural.

El objetivo de este trabajo es simular la fotoquímica atmosférica de un planeta tipo Tierra bajo diferentes regímenes de producción agrícola ("Escenarios ExoFarm"), orbitando dos tipos de estrellas distintos: una estrella tipo Sol (G2V) y una enana ultrafría (M8), específicamente TRAPPIST-1. El sistema TRAPPIST-1 es de particular interés debido a que alberga múltiples planetas en la zona de habitabilidad, siendo TRAPPIST-1e el candidato principal para estudios atmosféricos con el Telescopio Espacial James Webb (Gillon et al., 2017; Turbet et al., 2016).

Utilizando modelos de cinética fotoquímica, evaluamos cómo la distribución espectral de energía (SED) de la estrella anfitriona afecta la acumulación y fotólisis de estos gases, determinando si las firmas espectrales de una "Exo-Tierra agrícola" serían más detectables alrededor de una enana M tranquila que alrededor de una estrella similar al Sol.

### 1.1. El Ciclo del Nitrógeno y las "ExoFarms" como Tecnosignatura
La agricultura representa una intervención tecnológica directa en el ciclo del nitrógeno planetario. En la Tierra, la invención del proceso Haber-Bosch permitió la fijación artificial de nitrógeno para fertilizantes, alterando significativamente los flujos naturales. Haqq-Misra et al. (2022) proponen que esta disrupción puede considerarse una tecnosignatura detectable.

El ciclo del nitrógeno describe el movimiento de este elemento esencial entre la atmósfera, la biosfera y la litosfera. En su forma natural, el nitrógeno atmosférico inerte ($N_2$) debe ser transformado en formas reactivas para ser utilizado por la vida, proceso conocido como **fijación** (realizado por bacterias o rayos, convirtiendo $N_2 \rightarrow NH_3/NH_4^+$). Las plantas asimilan estos compuestos para formar biomasa. Posteriormente, la descomposición y excreción devuelven nitrógeno al suelo como amonio (**amonificación**). Microbios especializados oxidan este amonio a nitratos en un proceso llamado **nitrificación** ($NH_4^+ \rightarrow NO_2^- \rightarrow NO_3^-$), liberando pequeñas cantidades de $N_2O$ como subproducto. Finalmente, en condiciones anaeróbicas, otras bacterias cierran el ciclo mediante la **desnitrificación**, reduciendo nitratos de vuelta a gas nitrógeno ($NO_3^- \rightarrow N_2$), liberando nuevamente $N_2O$ como intermediario obligado.

En una "ExoFarm", la inyección masiva de fertilizantes sintéticos (fijación industrial) sobrecarga este sistema. El exceso de nitratos disponibles acelera drásticamente las tasas de nitrificación y desnitrificación, resultando en fugas masivas de $N_2O$ a la atmósfera.

Por otro lado, el **amoníaco ($NH_3$)** tiene un origen más directo en este contexto. Es el producto primario del proceso industrial Haber-Bosch y el componente principal de muchos fertilizantes y abonos orgánicos. En prácticas agrícolas intensivas, una fracción significativa del fertilizante nitrogenado aplicado no es absorbida por las plantas ni convertida en nitratos, sino que se volatiliza directamente a la atmósfera como gas $NH_3$. Esta volatilización es especialmente alta en el uso de urea y estiércol, creando una segunda señal atmosférica paralela a la del $N_2O$.

Según su estudio, una civilización que sostenga una población masiva (simulada entre 30 y 100 mil millones de personas en una Tierra análoga) requeriría una producción agrícola que elevaría las concentraciones atmosféricas no solo de óxido nitroso ($N_2O$), sino también de amoníaco ($NH_3$). Mientras que el $N_2O$ tiene fuentes biológicas naturales, la acumulación simultánea de $NH_3$ y $N_2O$ en una atmósfera rica en oxígeno es termodinámicamente improbable sin una fuente constante y masiva. Por lo tanto, la detección conjunta de estos gases en el espectro de un exoplaneta podría ser la evidencia definitiva de una "ExoFarm" o agricultura extraterrestre a escala global.

Esta perspectiva transforma la búsqueda de $N_2O$: de ser solo una posible biosignatura, pasa a ser, en conjunción con el $NH_3$, un indicador de una civilización tecnológica capaz de manipular la química planetaria para su subsistencia.

## 2. Metodología

Para investigar la estabilidad y acumulación de gases agrícolas, se realizaron simulaciones numéricas utilizando el código de cinética fotoquímica **VULCAN** (Tsai et al., 2017; 2021).

### 2.1. Modelo Fotoquímico (VULCAN)
VULCAN es un código de cinética química 1D diseñado para atmósferas exoplanetarias. Resuelve las ecuaciones de continuidad de masa para cada especie química, considerando:
1.  **Reacciones químicas:** Cinética térmica y fotoquímica.
2.  **Transporte vertical:** Difusión molecular y turbulenta (parametrizada mediante el coeficiente $K_{zz}$).
3.  **Deposición:** Velocidades de deposición en la superficie.

Para este estudio, se seleccionó la red química `NCHO_earth_photo_network.txt`. Esta decisión se basó en la necesidad de simular una atmósfera oxidante dominada por $N_2$ y $O_2$, en contraposición a las redes de "química reducida" (dominadas por $H_2$) comúnmente usadas para Júpiteres calientes. La red incluye especies de Carbono, Hidrógeno, Oxígeno y Nitrógeno, fundamentales para el ciclo del $N_2O$ y $NH_3$.

### 2.2. Parámetros Atmosféricos y Planetarios
Se definió un planeta "gemelo a la Tierra" para todos los escenarios, manteniendo constantes las siguientes variables para aislar el efecto estelar y de emisiones:
*   **Composición base:** $N_2$ (78%), $O_2$ (21%), $Ar$ (1%), $CO_2$ (400 ppm).
*   **Gravedad y Radio:** Valores terrestres ($1 R_{\oplus}$, $980 cm/s^2$).
*   **Perfil T-P:** Se utilizó el perfil estándar de la Atmósfera Estándar de EE.UU. 1976 (Earth Standard Atmosphere), asumiendo que la estructura térmica no varía drásticamente con los cambios en trazas de gases agrícolas para este primer orden de aproximación.
*   **Transporte Vertical ($K_{zz}$):** Se utilizó un perfil de mezcla troposférica estándar para simular la convección y mezcla en una atmósfera habitable.

### 2.3. Modelos Estelares y Procesamiento de Datos
Uno de los componentes críticos de la metodología fue el tratamiento riguroso de la radiación estelar, dado que la fotólisis es el principal sumidero de $N_2O$ y $NH_3$.

1.  **Escenario Solar:** Se utilizó el espectro solar estándar incluido en VULCAN (G2V).
2.  **Escenario TRAPPIST-1:**
    *   **Fuente de Datos:** Se obtuvieron datos observacionales del programa *Mega-MUSCLES*, específicamente el espectro combinado `trappist-1_model_const_res_v07.ecsv` (Wilson et al., 2021). Este dataset combina observaciones UV (HST), ópticas y modelos de rayos X para cubrir todo el rango fotoquímicamente activo.
    *   **Procesamiento de Datos:** Los datos originales, proporcionados en flujo observado desde la Tierra ($\text{erg cm}^{-2} \text{s}^{-1} \text{Å}^{-1}$ a $\sim 12.47$ pc), requirieron un post-procesamiento específico para su ingestión en VULCAN:
        *   *Conversión de Unidades:* Se transformó la longitud de onda de Angstroms ($\text{Å}$) a nanómetros ($nm$).
        *   *Escalado Geométrico:* VULCAN requiere el flujo emitido en la superficie de la estrella. Se aplicó un factor de escala basado en la relación $(D_{\star} / R_{\star})^2$, donde $D_{\star} = 12.47 \text{ pc}$ y $R_{\star} = 0.117 R_{\odot}$. Esto corrige la dilución geométrica de la luz a través del espacio interestelar, aumentando el flujo por un factor de $\sim 2 \times 10^{19}$ respecto al observado.
        *   *Validación:* Se implementó un script de verificación (`verify_spectrum.py`) que comparó los ratios de flujo integrados antes y después del procesamiento, asegurando la correcta conservación de la energía.

### 2.4. Definición de Escenarios "ExoFarm"
Para simular distintos grados de actividad agrícola, se modificaron las condiciones de frontera en la superficie (Bottom Boundary Conditions). En lugar de fijar una proporción de mezcla (que forzaría la atmósfera a tener una cantidad específica), se definieron **flujos de emisión** ($\text{mol cm}^{-2} \text{s}^{-1}$), permitiendo que la atmósfera alcance su propio equilibrio fotoquímico (steady state).

Se establecieron cuatro escenarios progresivos:

| Escenario | Descripción | Racional Metodológico |
| :--- | :--- | :--- |
| **A0 (Pre-Agri)** | Tierra Pre-industrial | Línea base natural. Emisiones biogénicas mínimas sin forzamiento antropogénico. |
| **A1 (Actual)** | Tierra Moderna | Calibración con valores actuales. Incluye emisiones naturales + agricultura industrial actual. |
| **A2 (ExoFarm Mod)** | 10x Emisiones Actuales | Hipótesis de una civilización que maximiza la superficie cultivable del planeta. |
| **A3 (ExoFarm Ext)** | 100x Emisiones Actuales | Escenario límite (Tecnosignatura). Representa una saturación agrícola o uso de fertilizantes sintéticos masivos. |

### 2.5. Ejecución y Automatización
Dada la complejidad de gestionar 8 simulaciones distintas (2 estrellas $\times$ 4 escenarios) y la necesidad de consistencia, se desarrolló una arquitectura de ejecución automatizada (`run_case.py`). Este sistema:
1.  Genera dinámicamente los archivos de configuración `vulcan_cfg.py` inyectando los parámetros de los archivos YAML diseñados para cada caso.
2.  Gestiona la restauración de archivos originales para evitar contaminación cruzada entre ejecuciones.
3.  Asegura que todos los modelos converjan utilizando los mismos criterios de tolerancia numérica.

Esta metodología asegura que las diferencias observadas en las abundancias finales de $N_2O$ y $NH_3$ sean atribuibles exclusivamente al tipo estelar y al flujo de emisión superficial, aislando las variables de interés.

## 3. Bibliografía

1.  Schwieterman, E. W. et al. (2022). Evaluating the Plausible Range Of N2O Biosignatures On Exo-Earths: An Integrated Biogeochemical, Photochemical, And Spectral Modeling Approach. *The Astrophysical Journal*, 937(2), 109. https://doi.org/10.3847/1538-4357/ac8cfb
2.  Tian, H. et al. (2020). A comprehensive quantification of global nitrous oxide sources and sinks. *Nature*, 586(7828), 248-256. https://doi.org/10.1038/s41586-020-2780-0
3.  Wilson, D. J. et al. (2021). The Mega-MUSCLES Spectral Energy Distribution Of TRAPPIST-1. *The Astrophysical Journal*, 911(2), 18. https://doi.org/10.3847/1538-4357/abe771
4.  Tsai, S. M. et al. (2017). VULCAN: An Open-source, Validated Chemical Kinetics Python Code for Exoplanetary Atmospheres. *Astrophysical Journal Supplement Series*, 228(2), 20. https://doi.org/10.3847/1538-4365/228/2/20
5.  Gillon, M. et al. (2017). Seven temperate terrestrial planets around the nearby ultracool dwarf star TRAPPIST-1. *Nature*, 542(7642), 456-460. https://doi.org/10.1038/nature21360
6.  Haqq-Misra, J. et al. (2022). Disruption of a Planetary Nitrogen Cycle as Evidence of Extraterrestrial Agriculture. *The Astrophysical Journal Letters*, 929(2), L28. https://doi.org/10.3847/2041-8213/ac65ff
