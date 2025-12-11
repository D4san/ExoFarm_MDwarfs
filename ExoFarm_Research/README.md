# ExoFarm Research Project

Este repositorio contiene el código fuente, configuraciones y resultados del proyecto de investigación sobre atmósferas planetarias y biofirmas agrícolas (ExoFarm).

El proyecto utiliza **VULCAN** (ubicado en el directorio hermano `../VULCAN`) como motor de cinética química, pero mantiene toda la lógica específica del proyecto, configuraciones y análisis en esta estructura de directorios.

## Estructura del Directorio

### 1. Config
Contiene todos los archivos de configuración necesarios para las simulaciones.
- **Boundary_Conditions/**: Archivos de flujo de condiciones de frontera (BC) para diferentes escenarios (Pre-Agri, Present, ExoFarm, etc.).
- **planets/**: Archivos de configuración YAML para VULCAN, organizados por sistema planetario (Earth-Sun, Earth-Trappist).

### 2. Results
Almacena los resultados generados por las simulaciones y los análisis.
- **Outputs/**: Archivos de salida crudos de VULCAN (`.vul`).
- **Plots/**: Gráficas generadas por los scripts de visualización.

### 3. Scripts
Contiene el código fuente organizado por funcionalidad.

#### Simulation
Scripts para ejecutar las simulaciones de VULCAN.
- `run_parallel_earth.py`: Ejecuta simulaciones en paralelo para escenarios de la Tierra (Sol).
- `run_parallel_trappist.py`: Ejecuta simulaciones en paralelo para escenarios de TRAPPIST-1e.

#### Analysis
Scripts para procesar datos y generar tablas.
- `extract_surface_values.py`: Extrae valores de mezcla superficial y genera tablas comparativas en la terminal.
- `process_trappist_spectrum.py`: Procesa espectros estelares para TRAPPIST-1.
- `compare_vulcan_outputs.py`: Utilidad para comparar salidas de VULCAN.
- `inspect_vul.py`: Utilidad para inspeccionar archivos `.vul`.

#### Plotting
Scripts para generar visualizaciones.
- `plot_agricultural_comparison.py`: Genera comparaciones de escenarios agrícolas.
- `plot_profiles_with_OH.py`: Grafica perfiles atmosféricos incluyendo radicales OH.
- `plot_spectra_comparison.py`: Compara espectros estelares.
- `plot_surface_normalized_bars.py`: Genera gráficos de barras de abundancias normalizadas.

## Uso

### Ejecutar Simulaciones
Para correr las simulaciones de la Tierra:
```bash
cd Scripts/Simulation
python run_parallel_earth.py
```

Para correr las simulaciones de TRAPPIST-1e:
```bash
cd Scripts/Simulation
python run_parallel_trappist.py
```

### Generar Gráficas
Los scripts de ploteo leen los resultados de `Results/Outputs` y guardan las imágenes en `Results/Plots`.
```bash
cd Scripts/Plotting
python plot_agricultural_comparison.py
# ... y otros scripts de ploteo
```

### Ver Tablas de Resultados
Para ver las tablas de abundancia en la terminal:
```bash
cd Scripts/Analysis
python extract_surface_values.py
```

## Requisitos
- Python 3.x
- Librerías: `numpy`, `matplotlib`, `scipy`, `pandas`
- VULCAN (configurado en el directorio padre)
