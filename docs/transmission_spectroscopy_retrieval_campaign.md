# Campaña de Inversión Atmosférica con POSEIDON y Ajuste Bayesiano (MultiNest)

**Fecha del reporte:** 2026-06-18  
**Etapa del Pipeline:** Etapa 2 (Inversión Atmosférica y Ajuste Bayesiano)  
**Herramientas:** POSEIDON (v1.4+) [2], PyMultiNest [3]  
**Sistema:** Análogo de TRAPPIST-1e  

---

## 1. Ajuste Atmosférico y Recuperación con POSEIDON (Retrieval Model)

El proceso de inversión atmosférica (retrieval) implementado en POSEIDON realiza el análisis bayesiano para deducir las propiedades de la atmósfera de TRAPPIST-1e a partir de los espectros sintéticos observados por JWST.

Para el ajuste de esta campaña, el modelo de retrieval en POSEIDON se configura con las siguientes simplificaciones y parametrizaciones directas:

*   **Perfil de Temperatura-Presión (PT):** Modelo isotérmico (`PT_profile="isotherm"`). Asume una temperatura uniforme $T$ constante en toda la atmósfera.
*   **Perfiles de Abundancia Molecular:** Perfil isoquímico de mezcla constante (`X_profile="isochem"`). Las fracciones volumétricas de mezcla de cada gas son constantes con la altitud.
*   **Tratamiento de la Superficie y Extensión de la Malla (`surface=False`):** En el retrieval de POSEIDON se desactiva la superficie física y se calcula la atmósfera extendiéndola de forma continua hasta $10.0$ bar.
    > [!IMPORTANT]
    > **Justificación Física:** En espectroscopía de transmisión, debido a la geometría tangencial del camino óptico rasante, la atmósfera del planeta templado se vuelve completamente opaca ($\tau \gg 1$) a presiones muy bajas ($\lesssim 0.1$ bar). La superficie sólida física del planeta a $1.0$ bar queda completamente oculta bajo esta opacidad y no es constreñible. Por ende, para no introducir la presión superficial ($P_{\mathrm{surf}}$) como parámetro libre degenerado con el radio de referencia ($R_{p,\mathrm{ref}}$), se desactiva la superficie y se extiende el cálculo hasta $10.0$ bar, de manera que la opacidad física del gas a alta presión actúe como un corte óptico natural.

---

## 2. Espacio de Parámetros y Priors (9 Dimensiones)

El retrieval busca ajustar de manera simultánea 9 variables libres que definen el estado de la atmósfera. Los priors son planos (uniformes) para evitar sesgos iniciales:

| Parámetro | Rango del Prior | Tipo de Prior | Justificación / Anclaje |
| :--- | :--- | :--- | :--- |
| **$T$** | $[200.0, 500.0]$ K | Uniforme | Rango de temperatura templada plausible de la atmósfera. |
| **$R_{p,\mathrm{ref}}$** | $[0.9 \times R_p, 1.1 \times R_p]$ | Uniforme | Radio de referencia del planeta anclado a $P_{\mathrm{ref}} = 1.0$ bar. |
| **$\log X_{\mathrm{H_2O}}$** | $[-10.0, -1.0]$ | Uniforme (dex) | Fracción de volumen del vapor de agua. |
| **$\log X_{\mathrm{CO_2}}$** | $[-10.0, -1.0]$ | Uniforme (dex) | Fracción de volumen de dióxido de carbono. |
| **$\log X_{\mathrm{CH_4}}$** | $[-10.0, -1.0]$ | Uniforme (dex) | Fracción de volumen de metano. |
| **$\log X_{\mathrm{O_2}}$** | $[-10.0, -1.0]$ | Uniforme (dex) | Fracción de volumen de oxígeno molecular. |
| **$\log X_{\mathrm{O_3}}$** | $[-10.0, -1.0]$ | Uniforme (dex) | Fracción de volumen de ozono. |
| **$\log X_{\mathrm{N_2O}}$** | $[-10.0, -1.0]$ | Uniforme (dex) | Fracción de mezcla de óxido nitroso (forzamiento ExoFarm). |
| **$\log X_{\mathrm{NH_3}}$** | $[-10.0, -1.0]$ | Uniforme (dex) | Fracción de mezcla de amoníaco (forzamiento ExoFarm). |

*   **Gas de Relleno (Bulk Gas):** Nitrógeno molecular ($\mathrm{N_2}$) no fiteado directamente, cuya abundancia se calcula para cada paso como la fracción complementaria:
    $$X_{\mathrm{N_2}} = 1.0 - \sum_{i} X_{i,\mathrm{trace}}$$

---

## 3. Configuración del Fiteador (MultiNest)

El muestreo del espacio de parámetros se realiza mediante la implementación de *Nested Sampling* de MultiNest [3].

*   **Número de Puntos Vivos:** $N_{\mathrm{live}} = 1000$. Garantiza una resolución estadística adecuada para mapear posteriores con formas complejas o posibles mínimos locales sin incurrir en un costo de cómputo inasequible.
*   **Modelo de Radiación y Bining:** En cada evaluación de MultiNest, POSEIDON calcula el espectro de transmisión del modelo a alta resolución ($R = 10,000$) y luego lo bina dinámicamente a la grilla de bins del instrumento ($R = 100$) para calcular la verosimilitud estadística ($\chi^2$) comparándolo con los puntos sintéticos ruidosos generados en la etapa forward.
*   **Control del Fiteador:** Los retrievals se ejecutan de manera modular mediante `run_trappist_retrieval.py` y se coordinan para múltiples combinaciones con el programador `run_trappist_retrieval_campaign.py`. Está activa la capacidad de reanudación automática (`resume=True`) para evitar reiniciar ejecuciones costosas interrumpidas.

---

## 4. Estructura y Combinaciones de la Campaña Activa

La campaña de retrievals está configurada para explorar la distinguibilidad en función del escenario atmosférico, la cantidad de tránsitos acumulados y el canal instrumental utilizado. Comprende un total de **42 ejecuciones completas de MultiNest** definidas por la siguiente matriz:

*   **Matriz de Escenarios y Tránsitos:**
    *   **Escenarios `A0` (Preagrícola) y `A3` (ExoFarm Extremo):** Se fitean para tránsitos de $5$, $10$, $20$ y $100$.
    *   **Escenarios `A1` (Tierra) y `A2` (ExoFarm Moderado):** Se fitean para tránsitos de $5$, $10$ y $20$ (se omiten 100 tránsitos por costo computacional).
*   **Modos Instrumentales (Canales):**
    *   `nirspec`: Únicamente datos de JWST NIRSpec Prism ($0.6 - 5.3 \, \mu\text{m}$).
    *   `miri`: Únicamente datos de JWST MIRI LRS ($5.0 - 12.0 \, \mu\text{m}$).
    *   `both`: Ajuste conjunto de NIRSpec Prism + MIRI LRS ($0.6 - 12.0 \, \mu\text{m}$).

```text
Campañas Extremas (A0, A3):
2 escenarios x 4 cantidades de tránsitos x 3 modos instrumentales = 24 corridas

Campañas Intermedias (A1, A2):
2 escenarios x 3 cantidades de tránsitos x 3 modos instrumentales = 18 corridas

Total de la Campaña de Retrievals = 42 corridas de MultiNest
```

Los outputs de posterior, logs de MultiNest y archivos de diagnóstico se guardan de forma persistente en:
`Transmission_Spectroscopy/notebooks/POSEIDON_output/TRAPPIST-1e/retrievals/`

---

## 5. Limitaciones Clave e Interpretación Científica

*   **Sesgos de Perfil Vertical (Fact):** La suposición de perfiles químicos planos (isoquímicos) puede introducir sesgos significativos al recuperar especies sujetas a gradientes verticales intensos. Un ejemplo crítico es el amoníaco (\(\mathrm{NH_3}\)): en el modelo directo fotoquímico, la fotólisis destruye el amoníaco por encima de los $\sim 0.01$ bar, por lo que su abundancia varía órdenes de magnitud. El retrieval isotérmico asume un valor plano que pondera la región a la que el instrumento es sensible. Esto explica por qué el \(\mathrm{NH_3}\) recuperado no muestra un comportamiento monótono al aumentar los tránsitos y puede sesgar el valor del radio planetario.
*   **Limitación de Ruido Único:** Las observaciones sintéticas se basan en una única realización de ruido aleatorio por tránsito. Esto implica que la variabilidad puntual entre corridas puede verse influenciada por la semilla del generador y no representa un promedio analítico riguroso de múltiples experimentos observacionales.

---

## 6. Referencias

1.  Haqq-Misra, J., Fauchez, T. J., Schwieterman, E. W., & Kopparapu, R. (2022). *Disruption of a Nitrogen Cycle as Evidence of Extraterrestrial Agriculture*. ApJL, 929, L28.
2.  MacDonald, R. J. (2023). *POSEIDON: A Multidimensional Atmospheric Retrieval Code*. JOSS, 8(81), 4873.
3.  Feroz, F., Hobson, M. P., & Bridges, M. (2009). *MultiNest: an efficient and robust Bayesian inference tool for cosmology and particle physics*. MNRAS, 398, 1601-1614.
