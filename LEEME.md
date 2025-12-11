# ExoFarm: Tecnofirmas Agrícolas en Atmósferas Exoplanetarias

[![VULCAN](https://img.shields.io/badge/Model-VULCAN-blue)](https://github.com/exoclime/VULCAN)
[![Python](https://img.shields.io/badge/Python-3.x-yellow)]()

---

## 🌍 Resumen / Justificación Científica

Este proyecto investiga la detectabilidad atmosférica de la agricultura intensiva a escala industrial ("ExoFarms") en exoplanetas similares a la Tierra. Utilizando el modelo de cinética fotoquímica **VULCAN**, simulamos la acumulación de tecnofirmas basadas en Nitrógeno—específicamente Óxido Nitroso ($N_2O$) y Amoníaco ($NH_3$)—resultantes de la disrupción del ciclo del nitrógeno planetario por procesos tipo Haber-Bosch.

El estudio compara dos entornos estelares distintos:
1.  **Sistema Tierra-Sol (G2V)**: Caso de control que representa las condiciones actuales de la Tierra.
2.  **Sistema Tierra-TRAPPIST-1e (M8V)**: Un planeta potencialmente habitable orbitando una estrella enana ultra-fría.

Nuestro objetivo es cuantificar cómo los diferentes flujos UV afectan la vida media fotoquímica de estos gases agrícolas, determinando si las "ExoFarms" podrían proporcionar una tecnofirma detectable y distinguible de los niveles biológicos naturales.

---

## 📂 Estructura del Repositorio y Carpetas

Este proyecto organiza la configuración, datos de entrada y resultados en directorios específicos:

*   **`VULCAN/planets/`**: Contiene los archivos de configuración YAML que definen cada escenario de simulación.
    *   `earth_sun/`: Escenarios A0-A3 para el sistema Tierra-Sol.
    *   `earth_trappist/`: Escenarios A0-A3 para el sistema TRAPPIST-1e.
*   **`VULCAN/boundary_conditions/`**: Define las condiciones de frontera de flujo superficial (las "emisiones agrícolas").
    *   `bc_earth_preagri_full.txt`: Flujos biológicos naturales (Pre-agrícola).
    *   `BC_bot_Earth.txt`: Flujos de la Tierra actual (incluyendo fuentes antropogénicas).
    *   `bc_earth_exofarm_moderate_full.txt`: Amplificación 10x de flujos de $N_2O$ y $NH_3$.
    *   `bc_earth_exofarm_full.txt`: Amplificación 100x (ExoFarm Extremo).
*   **`VULCAN/atm/stellar_flux/`**: Distribuciones de energía espectral estelar (SEDs).
    *   `TRAPPIST1_surface.txt`: El espectro procesado de Mega-MUSCLES para TRAPPIST-1, convertido a `nm` y escalado al flujo recibido en la superficie de TRAPPIST-1e.
*   **`VULCAN/output/`**: Almacena los resultados crudos de la simulación en formato `.vul` (pickle binario).
*   **`VULCAN/plot/`**: Destino para todas las figuras generadas y gráficos comparativos.
*   **`VULCAN/temp_run_*/`**: Directorios temporales creados durante la ejecución paralela para aislar configuraciones.

---

## 🧪 Escenarios de Simulación

Simulamos cuatro niveles distintos de intensidad agrícola para ambos sistemas estelares. Las condiciones de frontera superficiales para las especies clave se definen de la siguiente manera:

### Tabla de Flujos Agrícolas (Emisiones Superficiales)
Todos los flujos están en unidades de **moléculas cm⁻² s⁻¹**.

| ID | Nombre del Escenario | Descripción | Flujo $N_2O$ | Flujo $NH_3$ | Factor de Escala (aprox.) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A0** | **Pre-Agrícola** | Línea base natural (biológica). | $9.0 \times 10^8$ | $3.0 \times 10^8$ | Línea Base |
| **A1** | **Tierra Actual** | Antropogénico + biológico actual. | $1.5 \times 10^9$ | $1.5 \times 10^9$ | 1x (Referencia Actual) |
| **A2** | **ExoFarm Moderado** | Agricultura intensificada. | $2.3 \times 10^{10}$ | $1.5 \times 10^{10}$ | ~15x $N_2O$ / 10x $NH_3$ |
| **A3** | **ExoFarm Extremo** | Intensidad teórica máxima. | $2.3 \times 10^{11}$ | $1.5 \times 10^{11}$ | ~150x $N_2O$ / 100x $NH_3$ |

*Nota: Otras especies (CO, CH4, etc.) se mantienen con flujos constantes en todos los escenarios para aislar el efecto de la disrupción del ciclo del nitrógeno.*

---

## 📊 Guía de Visualización y Análisis de Datos

Esta sección explica el propósito científico y la interpretación de los gráficos generados.

### 1. Comparación de Espectros Estelares (`plot_spectra_comparison.py`)
*   **Qué muestra**: La distribución de energía espectral (flujo vs. longitud de onda) del Sol (G2V) frente a TRAPPIST-1 (M8V) recibida en el tope de la atmósfera del planeta.
*   **Análisis Clave**:
    *   **Diferencias UV**: El Sol emite órdenes de magnitud más radiación UV que TRAPPIST-1.
    *   **Fotoquímica**: Dado que los fotones UV impulsan la disociación de $N_2O$ y $NH_3$, el menor flujo UV de TRAPPIST-1 sugiere que estas moléculas deberían sobrevivir más tiempo y acumularse en mayores concentraciones.

### 2. Perfiles Verticales (`plot_star_comparison.py` - Gráfico de Perfiles)
*   **Qué muestra**: La proporción de mezcla (abundancia relativa al aire total) de $N_2O$, $NH_3$, $O_3$ y $CH_4$ en función de la altitud (presión).
*   **Análisis Clave**:
    *   **Acumulación Superficial**: Observamos cómo cambia la concentración en la superficie al aumentar el flujo agrícola.
    *   **Transporte Vertical vs. Fotólisis**: La forma del perfil revela la competencia entre el transporte ascendente (mezcla) y la destrucción por luz UV (fotólisis) en la atmósfera superior. Una caída más pronunciada indica una destrucción rápida.

### 3. Tendencias de Abundancia (`plot_star_comparison.py` - Gráfico de Tendencias)
*   **Qué muestra**: La abundancia media ponderada por presión de los gases agrícolas vs. la intensidad agrícola (A0-A3).
*   **Análisis Clave**:
    *   **Detectabilidad de Tecnofirmas**: Este gráfico responde directamente a la pregunta de investigación. Si la curva de TRAPPIST-1e es significativamente más alta que la del sistema Tierra-Sol, confirma que los entornos de enanas M favorecen la acumulación de estas tecnofirmas, haciéndolas potencialmente más fáciles de detectar con telescopios como el JWST.

---

## 🚀 Guía de Reproducibilidad

### 1. Preparación
Asegúrate de estar en el directorio `VULCAN/`. El proyecto utiliza scripts de Python personalizados para paralelizar las simulaciones.

### 2. Ejecutar Simulaciones (Paralelo)
Usamos scripts de orquestación para ejecutar los 4 escenarios simultáneamente para una estrella dada.

*   **Ejecutar Escenarios Tierra-Sol**:
    ```bash
    python run_parallel_earth.py
    ```
*   **Ejecutar Escenarios Tierra-TRAPPIST-1e**:
    ```bash
    python run_parallel_trappist.py
    ```

### 3. Visualización y Análisis de Datos
Utiliza los scripts de graficación proporcionados para generar las figuras del reporte:

*   **`python plot_spectra_comparison.py`**
    *   **Propósito**: Visualiza los espectros estelares de entrada.
    *   **Salida**: `plot/stellar_spectra_comparison.png`
    *   **Insight**: Muestra la dramática diferencia en flujo UV entre el Sol y TRAPPIST-1, lo cual impulsa las diferencias fotoquímicas.

*   **`python plot_star_comparison.py`**
    *   **Propósito**: El resultado comparativo principal. Grafica perfiles verticales de $N_2O$/$NH_3$ y sus tendencias de abundancia.
    *   **Salida**: `plot/star_comparison_profiles.png` (Perfiles de Mezcla Vertical)
    *   **Salida**: `plot/star_comparison_trends.png` (Abundancia vs. Intensidad Agrícola)

*   **`python plot_agricultural_comparison.py`**
    *   **Propósito**: Vista detallada solo de los escenarios Tierra-Sol.
    *   **Salida**: `plot/agricultural_comparison.png`

*   **`python plot_trappist_comparison.py`**
    *   **Propósito**: Vista detallada solo de los escenarios TRAPPIST-1e.
    *   **Salida**: `plot/trappist_comparison.png`

---

## 📚 Referencias

*   **Modelo VULCAN**: Tsai, S.-M., et al. (2017). *VULCAN: An Open-source, Validated Chemical Kinetics Code for Exoplanetary Atmospheres*. [[DOI: 10.3847/1538-4365/aa51dd](https://doi.org/10.3847/1538-4365/aa51dd)]
*   **Ciclo del Nitrógeno y ExoFarms**: Haqq-Misra, et al. (2022). *Disruption of a Planetary Nitrogen Cycle as Evidence of Extraterrestrial Agriculture*. The Astrophysical Journal Letters, 929, L28. [[DOI: 10.3847/2041-8213/ac65ff](https://doi.org/10.3847/2041-8213/ac65ff)]
*   **Biofirmas**: Schwieterman, E. W., et al. (2018). *Exoplanet Biosignatures: A Review of Remotely Detectable Signs of Life*. [[DOI: 10.1089/ast.2017.1729](https://doi.org/10.1089/ast.2017.1729)]
*   **Espectro TRAPPIST-1**: Wilson, D. J., et al. (2021). *The Mega-MUSCLES Spectral Energy Distribution Library*. [[Repositorio de Datos](https://github.com/parkus/Mega-MUSCLES)]
