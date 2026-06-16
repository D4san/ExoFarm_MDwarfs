# Inventario de espectroscopia de transmision, 2026-06-16

## Proposito

Esta nota registra una revision read-only de
`Transmission_Spectroscopy/`. No se borraron, movieron ni renombraron archivos.
El objetivo fue dejar contexto para ordenar despues la etapa de espectroscopia
sin perder evidencia cientifica ni productos caros de POSEIDON/MultiNest.

La conclusion corta es que la carpeta contiene productos utiles, pero mezcla
tres capas que hoy se leen como una sola:

1. flujos actuales de TRAPPIST-1e para espectros, observaciones sinteticas y
   retrievals;
2. notebooks y figuras de analisis/post-procesamiento;
3. productos legacy, respaldos, caches y salidas exploratorias.

## Entorno de ejecucion

Los scripts que importan o ejecutan POSEIDON deben correrse en Ubuntu/WSL, no
en la `.venv` local de Windows. El entorno esperado es el ambiente de Anaconda
llamado `POSEIDON`.

Comandos base:

```bash
cd /mnt/c/Proyectos/Astro/ExoFarm_MDwarfs/Transmission_Spectroscopy/notebooks
source /home/dasan/anaconda3/etc/profile.d/conda.sh
conda activate POSEIDON
export POSEIDON_input_data=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/
export PYSYN_CDBS=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids/
```

Desde Codex en Windows, si `wsl` no encuentra distribuciones, no asumir que
Ubuntu esta ausente. Probar primero con una ruta especifica, por ejemplo
`ubuntu.exe run bash -lc "<command>"`, tal como se documenta en `AGENTS.md`.

La `.venv` local de Windows solo es apropiada para post-procesamiento liviano
que no importe POSEIDON.

## Estructura observada

Resumen de tamano al momento de la revision:

| Ruta | Archivos | Tamano aproximado |
| :--- | ---: | ---: |
| `Transmission_Spectroscopy/notebooks/` | 873 | 798.77 MB |
| `Transmission_Spectroscopy/profiles/` | 16 | 1.24 MB |
| `Transmission_Spectroscopy/scripts/` | 2 | 0.01 MB |
| `notebooks/POSEIDON_output/TRAPPIST-1e/retrievals/` | 664 | 764.80 MB |
| `notebooks/POSEIDON_output/TRAPPIST-1e/synthetic_data/base_1transit/` | 34 | 0.25 MB |
| `notebooks/POSEIDON_output/TRAPPIST-1e/plots/` | 77 | 14.93 MB |

Distribucion principal dentro de `POSEIDON_output/`:

| Directorio | Lectura actual |
| :--- | :--- |
| `TRAPPIST-1e/` | Campana activa principal: synthetic data, retrievals, logs y plots. |
| `pure_spectra/` | Productos utiles de espectros puros, pero conceptualmente separados de la campana de retrievals. |
| `Earth/` | Productos antiguos o comparativos; no parecen ser el frente activo de retrievals. |
| `Trappist/` | Productos antiguos con nomenclatura previa a `TRAPPIST-1e/`. |
| `Dummy/` | Estructura vacia. No borrar sin una decision explicita, pero no aporta evidencia actual. |

## Rutas canonicas actuales

Estas rutas deberian tratarse como el nucleo activo por ahora:

| Producto | Ruta canonica actual |
| :--- | :--- |
| Perfiles PT y quimica exportados desde VULCAN | `Transmission_Spectroscopy/profiles/` |
| Generacion de observaciones sinteticas | `Transmission_Spectroscopy/notebooks/generate_trappist_synthetic_grid.py` |
| Synthetic data activos | `Transmission_Spectroscopy/notebooks/POSEIDON_output/TRAPPIST-1e/synthetic_data/base_1transit/` |
| Retrieval individual | `Transmission_Spectroscopy/notebooks/run_trappist_retrieval.py` |
| Campana de retrievals | `Transmission_Spectroscopy/notebooks/run_trappist_retrieval_campaign.py` |
| Logica comun de retrieval | `Transmission_Spectroscopy/notebooks/trappist1e_retrieval_common.py` |
| Productos de retrieval | `Transmission_Spectroscopy/notebooks/POSEIDON_output/TRAPPIST-1e/retrievals/` |
| Plots derivados de la campana TRAPPIST-1e | `Transmission_Spectroscopy/notebooks/POSEIDON_output/TRAPPIST-1e/plots/` |
| Estilo visual compartido | `Transmission_Spectroscopy/notebooks/exofarm_plot_style.py` |
| Capa final curada | `Transmission_Spectroscopy/final_products/` |

La campana de retrieval actual esta definida por `DEFAULT_CAMPAIGN` en
`run_trappist_retrieval_campaign.py`: A0/A3 para 5, 10, 20 y 100 transitos; A1/A2
para 5, 10 y 20 transitos; instrumentos `MIRI`, `NIRSpec` y `NIRSpec_MIRI`.

## Capa final curada

Se agrego una capa final autosuficiente en
`Transmission_Spectroscopy/final_products/`. Esta carpeta no limpia ni reemplaza
el arbol de trabajo de POSEIDON; solo declara cuales figuras son parte de la
narrativa actual.

El script `Transmission_Spectroscopy/notebooks/make_final_spectroscopy_figures.py`
construye o actualiza esta coleccion. Debe correrse en Ubuntu/WSL con el entorno
Anaconda `POSEIDON`, porque reutiliza funciones que importan POSEIDON y leen los
productos actuales.

Familias promovidas por ahora:

| Familia | Producto final |
| :--- | :--- |
| Espectros sinteticos de los cuatro escenarios | `final_synthetic_observations_by_noise_level.{png,pdf}` |
| Ruido y reconstrucciones/retrieved spectra | `trappist_retrieval_A3_retrieved_noise_background.{png,pdf}`, `trappist_retrieval_A3_retrieved_spectra_grid.{png,pdf}`, `trappist_retrieved_truth_extremes_A3_10_100transits.{png,pdf}` |
| Super matriz posterior | `trappist_A0_A3_posterior_sigma_distance_matrix.{png,pdf}` |

El 2026-06-16 se copiaron a `Transmission_Spectroscopy/final_products/figures/`
las figuras existentes de ruido/retrieved spectra y la matriz posterior. La
figura de cuatro escenarios no aparecio como archivo ya exportado; queda
definida para generarse con `make_final_spectroscopy_figures.py` en el entorno
POSEIDON.

## Scripts y notebooks de plots

Hay varios codigos de plots en `notebooks/`, mezclados con scripts operativos.
No son necesariamente basura: muchos son analisis post-retrieval. El problema
es que no esta claro cuales son figuras finales, cuales son diagnosticos y
cuales quedaron como exploracion.

Scripts de plots detectados:

| Script | Lectura preliminar |
| :--- | :--- |
| `plot_a0_a3_diagonal_distinguishability.py` | Analisis A0/A3 para separacion posterior. |
| `plot_a0_a3_posterior_sigma_matrix.py` | Matriz de distancias/sigma posterior. |
| `plot_pure_transmission_spectra.py` | Espectros puros, separado de retrievals. |
| `plot_retrieval_campaign_summary.py` | Resumen de campana de retrievals. |
| `plot_retrieval_spectra_products.py` | Productos espectrales recuperados. |
| `plot_retrieved_truth_extremes.py` | Comparacion verdad-modelo recuperado en extremos. |
| `plot_trappist_simulated_observations.py` | Observaciones simuladas y presupuesto de error. |

Notebooks relevantes:

| Notebook | Lectura preliminar |
| :--- | :--- |
| `ExoFarm_Transmission_Spectra.ipynb` | Entrada narrativa/presentacional para espectros de transmision. |
| `Plot_Transmission_Spectra_TRAPPIST.ipynb` | Notebook historico importante, pero con copias backup/recovered al mismo nivel. |
| `Plot_Profile_Posterior_Comparison_TRAPPIST.ipynb` | Comparacion perfiles/posteriores. |
| `Plot_Vertical_Profiles.ipynb` | Revision de perfiles verticales. |
| `Observation.ipynb` | Exploracion/observacion; necesita clasificacion futura. |

Archivos de respaldo o recuperacion detectados:

- `Plot_Transmission_Spectra_TRAPPIST.codex_modified_backup.ipynb`
- `Plot_Transmission_Spectra_TRAPPIST.recovered_from_git.ipynb`

No se borraron porque pueden contener historia util o diferencias no revisadas.
La recomendacion futura es compararlos y archivarlos bajo una carpeta `legacy/`
o `notebook_backups/` solo despues de confirmar que no contienen resultados
unicos.

## Plots y figuras

Las figuras estan repartidas entre:

| Ruta | Rol probable |
| :--- | :--- |
| `notebooks/figures/` | Figuras generadas por notebooks de comparacion perfil/posterior. |
| `notebooks/POSEIDON_output/TRAPPIST-1e/plots/` | Plots activos de retrievals, distancias posteriores, simulaciones y espectros recuperados. |
| `notebooks/POSEIDON_output/pure_spectra/plots/` | Figuras de espectros puros. |
| `notebooks/POSEIDON_output/Earth/plots/` | Figuras antiguas/comparativas Earth-Sun. |
| `notebooks/POSEIDON_output/Trappist/plots/` | Figuras antiguas con nomenclatura previa. |

La ubicacion de los plots no es intuitiva para lectura humana porque combina
productos finales, diagnosticos y outputs generados automaticamente. Una
organizacion futura deberia separar al menos:

- `plots/final_or_report/` para figuras usadas en informes;
- `plots/diagnostics/` para control de calidad;
- `plots/legacy/` para figuras de campanas anteriores.

Por ahora no se hizo esa reorganizacion para evitar romper rutas usadas por
notebooks o scripts.

## Legacy o ambiguo, conservar por ahora

Estos elementos requieren decision futura, pero no deben borrarse en automatico:

| Elemento | Motivo para conservar por ahora |
| :--- | :--- |
| `retrieve_trappist_A0_10.py`, `retrieve_trappist_A0_100.py`, `retrieve_trappist_A3_10.py`, `retrieve_trappist_A3_100.py` | Parecen wrappers antiguos supersedidos por `run_trappist_retrieval.py`, pero documentan una etapa previa 10/100 transitos. |
| `run_campaign_A3_queue.sh` | Parece duplicar el runner general de campana, pero puede haber sido usado como launcher local. |
| Productos sin sufijo de instrumento en `retrievals/` | Probable campana legacy; no mezclarlos con `MIRI`, `NIRSpec`, `NIRSpec_MIRI` al interpretar resultados actuales. |
| `retrievals/MultiNest_raw/failed_A0_5_MIRI_20260529` | Evidencia de intento fallido o diagnostico de recuperacion. |
| `retrievals/MultiNest_raw/legacy_failed_resume` | Evidencia de recuperacion/continuacion fallida; conservar hasta cerrar auditoria. |
| `POSEIDON_output/Earth/`, `POSEIDON_output/Trappist/`, `POSEIDON_output/Dummy/` | No son nucleo activo actual, pero conviene mover/documentar antes que borrar. |
| `__pycache__/` en `notebooks/` y `scripts/` | Residuo tecnico borrable, pero el usuario pidio explicitamente no borrar nada en esta fase. |

## Diagnostico

La generacion de espectros, synthetic data y retrievals tiene una arquitectura
recuperable: hay scripts centrales claros y una ruta activa fuerte bajo
`TRAPPIST-1e/`. El desorden viene de que el directorio `notebooks/` cumple
demasiados roles a la vez: laboratorio de notebooks, ejecutor de POSEIDON,
contenedor de scripts operativos, contenedor de plots y raiz de outputs grandes.

La decision de corto plazo deberia ser documental, no destructiva:

1. tratar `TRAPPIST-1e/retrievals/`, `TRAPPIST-1e/synthetic_data/base_1transit/`
   y los scripts `run_trappist_*` como frente activo;
2. considerar `Earth/`, `Trappist/`, wrappers A0/A3 10/100, backups de notebooks
   y productos sin sufijo de instrumento como legacy/ambiguos hasta revisar;
3. no mover plots aun, pero empezar a etiquetar cuales son figuras de informe y
   cuales son diagnosticos;
4. mantener visible que POSEIDON se corre en Ubuntu/WSL con conda `POSEIDON`.

## Accion tomada

- Se hizo inventario read-only el 2026-06-16.
- No se borro nada.
- No se movio nada.
- No se renombro nada.
- Esta nota queda como contexto para una futura organizacion conservadora de
  `Transmission_Spectroscopy/`.
