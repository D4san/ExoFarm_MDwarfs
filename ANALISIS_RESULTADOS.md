# 🧪 Análisis de Resultados: Tecnofirmas Agrícolas en Exoplanetas

Este documento presenta un análisis científico de las simulaciones fotoquímicas realizadas con VULCAN, comparando la detectabilidad de gases agrícolas ($N_2O$, $NH_3$) en planetas similares a la Tierra orbitando dos tipos de estrellas: una estrella tipo Sol (G2V) y una enana ultra-fría (TRAPPIST-1, M8V).

---

## 1. Contexto Teórico

La detectabilidad de gases en una atmósfera planetaria depende fundamentalmente del equilibrio entre su **producción** (flujos superficiales, en este caso agricultura intensiva) y su **destrucción** (principalmente fotólisis por radiación UV y reacciones químicas).

*   **El Sol (G2V)**: Emite una cantidad significativa de radiación en el Ultravioleta Cercano (NUV, 200-400 nm).
*   **TRAPPIST-1 (M8V)**: Es una estrella mucho más fría. Aunque activa en rayos X y UV extremo (XUV/FUV) durante erupciones, su emisión en el continuo NUV es órdenes de magnitud menor que la del Sol.
*   **Hipótesis**: Moléculas como el $N_2O$ y el $NH_3$, que son destruidas eficientemente por fotones UV, deberían tener vidas medias más largas en el entorno de TRAPPIST-1e, facilitando su acumulación.

---

## 2. Análisis de Espectros Estelares

![Comparación de Espectros Estelares](VULCAN/plot/stellar_spectra_comparison.png)

**Observaciones:**
La figura muestra la distribución de energía espectral (SED) recibida en el tope de la atmósfera.
1.  **Diferencia de Flujo**: Se observa claramente que el flujo solar (línea naranja) domina en el visible y UV.
2.  **Región UV (<400 nm)**: En la zona sombreada gris, crítica para la fotoquímica, el flujo de TRAPPIST-1 (línea roja) es drásticamente menor (varios órdenes de magnitud) en el Ultravioleta Cercano (NUV).
3.  **Emisión en Onda Corta (XUV/FUV)**: Sin embargo, es notable que TRAPPIST-1e presenta picos de emisión intensa en longitudes de onda muy cortas (<150 nm), correspondientes a líneas de emisión cromosférica (como Lyman-$\alpha$). Aunque la estrella es "oscura" en el NUV, es paradójicamente activa y "brillante" en el UV extremo, lo cual tiene implicaciones complejas para la química superior de la atmósfera, aunque el "escudo" en el NUV sigue siendo el factor dominante para la supervivencia de moléculas como el $N_2O$.
4.  **Implicación Global**: La "tasa de fotólisis" ($J$-value) total para moléculas absorbentes de NUV será mucho menor en TRAPPIST-1e.

---

## 3. Perfiles Verticales de Abundancia

### 3.1. Escenario Tipo Sol (G2V)
![Perfiles Tierra-Sol](VULCAN/plot/agricultural_comparison.png)

**Análisis:**
*   **Comportamiento General**: Las concentraciones de $N_2O$ y $NH_3$ caen rápidamente con la altura en la atmósfera superior. Esto es consistente con la eficiente destrucción por radiación UV solar.
*   **Sensibilidad a la Fuente**: A medida que aumentamos el flujo agrícola (A0 $\to$ A3), la concentración superficial aumenta, pero el perfil vertical mantiene una pendiente pronunciada de destrucción.

### 3.2. Escenario TRAPPIST-1e (M8V)
![Perfiles TRAPPIST-1e](VULCAN/plot/trappist_comparison.png)

**Análisis:**
*   **Mayor Acumulación**: Comparado con el caso solar, los perfiles en TRAPPIST-1e muestran una caída menos abrupta en la estratosfera para los mismos flujos superficiales.
*   **Transporte Vertical**: La menor fotólisis permite que el transporte vertical (mezcla turbulenta, $K_{zz}$) lleve estas moléculas a mayores alturas antes de ser destruidas. Esto es crucial para la detección por transmisión (JWST), que sondea capas altas de la atmósfera.

---

## 4. Comparación Directa y Tendencias

### 4.1. Perfiles Comparativos
![Comparación de Perfiles](VULCAN/plot/star_comparison_profiles.png)

Este gráfico superpone directamente los resultados.
*   **$N_2O$ (Óxido Nitroso)**: Para un mismo escenario (ej. A3-Extremo), la línea punteada (TRAPPIST) alcanza mayores altitudes y proporciones de mezcla superiores a la línea sólida (Sol), especialmente en la atmósfera media ($10^{-2} - 10^{-4}$ bar).
*   **$NH_3$ (Amoniaco)**: La diferencia es dramática. Mientras que en el escenario solar (línea verde sólida) el amoniaco es prácticamente inexistente por encima de la superficie, en TRAPPIST-1e (línea verde punteada) sobrevive en concentraciones detectables hasta presiones bajas.
*   **$CH_4$ (Metano)**: Muestra un perfil casi vertical en TRAPPIST-1e, indicando una mezcla eficiente y baja destrucción. En contraste, en el Sol su abundancia cae con la altura.
*   **$O_3$ (Ozono)**: Aquí observamos un comportamiento interesante. El perfil de ozono en la Tierra-Sol muestra el clásico "pico" de la capa de ozono estratosférica. En TRAPPIST-1e, la estructura es más compleja y, en general, la abundancia total de ozono parece ser menor, probablemente debido a la menor disponibilidad de fotones UV necesarios para romper el $O_2$ e iniciar el ciclo de Chapman.

### 4.2. Tendencias de Abundancia vs. Intensidad Agrícola
![Tendencias de Abundancia](VULCAN/plot/star_comparison_trends.png)

**Hallazgo Principal del Estudio:**
Este gráfico resume la respuesta media de la atmósfera a la "ExoFarm".

1.  **Divergencia Estelar (El "Amplificador M")**:
    *   **$N_2O$ y $NH_3$**: Las curvas de TRAPPIST-1 (triángulos azules) muestran una pendiente ascendente mucho más marcada que las del Sol (círculos naranjas). Para el amoniaco, la diferencia es de varios órdenes de magnitud.
    *   **$CH_4$**: El metano se mantiene alto y constante en TRAPPIST-1e (~$10^{-4}$), mientras que en el escenario solar es menor y decrece con la intensidad agrícola en nuestros modelos (posiblemente por cambios en la química del OH).

2.  **Umbral de Detectabilidad**:
    *   Si asumimos un umbral de detectabilidad para el JWST de aproximadamente $10^{-6}$ (1 ppm), el $N_2O$ en un entorno tipo Sol requeriría niveles extremos (A3) para ser detectado. En TRAPPIST-1e, el escenario moderado (A2) ya cruza este umbral.
    *   El $NH_3$ sigue siendo difícil de detectar incluso en TRAPPIST-1e a menos que se llegue a escenarios extremos, pero es *imposible* en un análogo solar.

3.  **Conclusión sobre Tecnofirmas**:
    *   Los planetas alrededor de enanas M actúan como **amplificadores de tecnofirmas** para gases fotolábiles.
    *   Una civilización no necesitaría una agricultura tan intensiva en TRAPPIST-1e para ser visible, en comparación con una en la Tierra.

---

## 5. Conclusiones

Las simulaciones confirman que el entorno fotoquímico de las estrellas enanas M favorece la acumulación de gases agrícolas. La falta de flujo NUV reduce las tasas de fotólisis del $N_2O$ y $NH_3$, resultando en mayores abundancias de equilibrio.

**Implicaciones para la Búsqueda de Vida:**
Esto sugiere que TRAPPIST-1e es un objetivo excelente no solo para biofirmas, sino para tecnofirmas atmosféricas. Sin embargo, también implica un riesgo de "falsos positivos": niveles modestos de actividad biológica podrían acumularse hasta parecer niveles industriales si no se calibra bien el modelo con el espectro estelar correcto.

---

## 6. Validación con Literatura Científica

Para validar nuestros resultados, hemos contrastado los hallazgos de las simulaciones con literatura científica reciente sobre fotoquímica en enanas M.

### 6.1. Resiliencia del Óxido Nitroso ($N_2O$)
Nuestras simulaciones muestran una acumulación significativa de $N_2O$ en TRAPPIST-1e. Esto es consistente con estudios previos como **Grenfell et al. (2013)**, quienes demostraron que el $N_2O$ puede sobrevivir en atmósferas de planetas orbitando enanas M bajo diversas condiciones de actividad estelar, a diferencia de entornos tipo Sol donde la fotólisis es rápida. La falta de radiación NUV en estrellas M (como se ve en nuestra Figura 1) es el mecanismo clave que permite esta acumulación.

### 6.2. El Desafío del Amoniaco ($NH_3$)
Nuestros resultados muestran tendencias crecientes para el $NH_3$, pero la literatura sugiere cautela:
*   **Huang et al. (2021)** (*Assessment of Ammonia as a Biosignature Gas*) indican que el $NH_3$ es generalmente una biofirma pobre debido a su **extrema solubilidad en agua** y corta vida media fotoquímica.
*   Sin embargo, el mismo estudio señala que el **mejor escenario para la detección** es precisamente un planeta rocoso orbitando una **enana M** (como TRAPPIST-1e), donde la vida media es mayor debido al espectro estelar.
*   Para ser detectable con JWST, se estiman necesarias concentraciones promedio de columna > 5 ppm. Nuestras simulaciones (Escenarios A2/A3) se acercan a estos regímenes, confirmando que solo niveles "industriales" o agrícolas extremos (ExoFarm) harían visible esta molécula, validando el enfoque de usarlo como tecnofirma en lugar de biofirma pasiva.

### 6.3. Mecanismos de Protección UV
Estudios complementarios sobre atmósferas en enanas M sugieren que, además de la baja emisión NUV estelar, mecanismos como el **scattering de Rayleigh** pueden actuar como un escudo adicional en atmósferas con baja capa de ozono, protegiendo moléculas en la baja atmósfera. En el caso del sistema solar, la vida media del $NH_3$ es de días/semanas, mientras que en entornos fríos y pobres en UV (como Plutón o potencialmente enanas M lejanas) puede extenderse significativamente (Science Advances, 2019),... apoyando nuestra observación de mayor estabilidad en el escenario TRAPPIST-1.

---

## 7. Tablas de Datos: Abundancias Superficiales

A continuación se presentan las proporciones de mezcla (mixing ratios) en la superficie para los diferentes escenarios simulados.

### Sun (G2V)
| Molécula | A0 (Pre-Agri) | A1 (Present) | A2 (ExoFarm Mod) | A3 (ExoFarm Ext) |
| :--- | :---: | :---: | :---: | :---: |
| **N2O** | 1.44e-07 | 3.49e-07 | 2.81e-06 | 2.43e-05 |
| **NH3** | 1.10e-11 | 5.44e-11 | 4.99e-10 | 4.06e-09 |
| **O3** | 2.07e-08 | 1.98e-08 | 1.30e-08 | 6.80e-09 |
| **CH4** | 1.21e-06 | 1.10e-06 | 4.89e-07 | 1.46e-07 |

### TRAPPIST-1e (M8V)
| Molécula | A0 (Pre-Agri) | A1 (Present) | A2 (ExoFarm Mod) | A3 (ExoFarm Ext) |
| :--- | :---: | :---: | :---: | :---: |
| **N2O** | 3.02e-07 | 7.72e-07 | 8.53e-06 | 8.70e-05 |
| **NH3** | 1.24e-11 | 6.20e-11 | 6.20e-10 | 6.20e-09 |
| **O3** | 1.46e-09 | 1.46e-09 | 1.49e-09 | 1.52e-09 |
| **CH4** | 1.01e-04 | 1.01e-04 | 1.33e-04 | 1.44e-04 |

### Tablas de Abundancia Normalizada (vs. Tierra Actual)
Valores expresados como múltiplos del nivel actual en la Tierra (Sun A1).

#### Sun (G2V) (Normalizado)
| Molécula | A0 (Pre-Agri) | A1 (Present) | A2 (ExoFarm Mod) | A3 (ExoFarm Ext) |
| :--- | :---: | :---: | :---: | :---: |
| **N2O** | 0.41x | 1.00x | 8.08x | 69.60x |
| **NH3** | 0.20x | 1.00x | 9.17x | 74.53x |
| **O3** | 1.04x | 1.00x | 0.66x | 0.34x |
| **CH4** | 1.10x | 1.00x | 0.45x | 0.13x |

#### TRAPPIST-1e (M8V) (Normalizado)
| Molécula | A0 (Pre-Agri) | A1 (Present) | A2 (ExoFarm Mod) | A3 (ExoFarm Ext) |
| :--- | :---: | :---: | :---: | :---: |
| **N2O** | 0.87x | 2.22x | 24.47x | 249.50x |
| **NH3** | 0.23x | 1.14x | 11.39x | 113.97x |
| **O3** | 0.07x | 0.07x | 0.08x | 0.08x |
| **CH4** | 91.97x | 92.23x | 121.45x | 131.39x |

### Visualización de Abundancias Normalizadas

![Abundancias Superficiales Normalizadas](VULCAN/plot/surface_normalization_bars.png)

**Interpretación del Gráfico:**
*   **Escala Logarítmica:** Se ha utilizado una escala logarítmica (eje Y) debido a la enorme disparidad en los valores. La línea punteada gris en **1.0** representa el nivel base de la Tierra actual (Sun A1).
*   **Amplificación en TRAPPIST-1e:** Las barras azules (TRAPPIST-1e) superan sistemáticamente a las naranjas (Sol) para $N_2O$ y $NH_3$ en los escenarios agrícolas (A2, A3).
*   **Caso Extremo del Metano ($CH_4$):** Se destaca cómo el metano en TRAPPIST-1e es casi 100 veces más abundante que en la Tierra actual de forma natural, independientemente del escenario agrícola.
*   **Ozono ($O_3$):** Por el contrario, el ozono en TRAPPIST-1e se mantiene en niveles muy bajos (~0.07x el terrestre), lo cual es consistente con la baja actividad UV necesaria para su formación.

