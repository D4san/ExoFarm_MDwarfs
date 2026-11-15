# Flujo y custodia de resultados LIFE Proxima — 2026-11-14

## Alcance y regla de lectura

Este mapa sigue la serie vigente A1/A3 a 1/10/100 h y la extensión exploratoria A3–1000 h del [informe integrado](life_proxima_a1_a3_retrievals_analisis_integrado_2026-10-29.md). Las rutas son las actuales y forman parte del contrato de scripts, manifiestos y enlaces: no mover carpetas sin revisar referencias y verificar de nuevo. Los 480 insumos del análisis se identifican por ruta y SHA-256 en [input_hashes.csv](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a1_a3_integrated_20261029/input_hashes.csv); todos coincidieron el 14-nov. Esa lista identifica insumos de postprocesado, no necesariamente todas las dependencias para regenerar desde cero.

## Flujo científico documentado

1. **SED y fotoquímica.** SED MUSCLES y conversiones para VULCAN; configuraciones `Photochemical_Modeling/Config/planets/earth_proxima_b/input_earth_proxima_b_A*.yml`, atmósfera PT/Kzz de control terrestre, red fotoquímica y productos VULCAN. Los perfiles PT/química exportados están en `Transmission_Spectroscopy/profiles/Proxima_b_*`. La [metodología](life_proxima_a1_a3_1_10_100h_methodology_2026-10-03.md) y [bitácora Proxima](life_proxima_b_branch_bitacora_2026-07-22.md) dan la procedencia. Los perfiles utilizados por el análisis incluyen A0 química, A1 y A3 PT/química. La captura de emisión no incluye automáticamente todos los datos externos de esta etapa.
2. **Emisión directa.** [emission_forward.py](../Thermal_Emission_Spectroscopy/scripts/emission_forward.py), configuración y perfiles alimentan POSEIDON; los espectros están en `outputs/life_proxima_b_earthlike_v1/forward_emission/`. El observable para LIFE es `Fp_obs`, W m⁻² m⁻¹. Conservar opacidades y rejilla PHOENIX externas o documentar cómo recuperarlas.
3. **Escena LIFE y datasets.** La escena clásica y sus componentes de ruido producen incertidumbres por canal; los archivos `.dat` de 1/10/100 h están en `outputs/life_proxima_b_earthlike_v1/life_data/`. Conservar los seis datasets concretos, semillas, índices, escena, scripts y salidas LIFE asociados. La [metodología](life_proxima_a1_a3_1_10_100h_methodology_2026-10-03.md) explica la conversión fotones/energía y las realizaciones independientes. El modelo clásico de ruido no incluye covarianza instrumental.
4. **Retrievals y operador.** POSEIDON/MultiNest usa el operador corrected-bin y configuraciones emparejadas; consultar [diseño](life_proxima_a1_a3_corrected_binning_matrix_2026-10-21.md), manifiestos y JSON resueltos. Conservar `run_life_retrieval.py`, `run_life_retrieval_a1_a3_corrected_matrix.py`, `launch_proxima_a1_a3_corrected_binning_matrix_loo.py`, `life_bin_operator_diagnostic.py`, sus imports y versiones capturadas, junto con manifiestos, datos, registros y productos por corrida. La comprobación de dependencia transitiva completa de cada ejecutable y de sus dependencias externas aún está pendiente.
5. **Auditoría y análisis.** [Validador](../Thermal_Emission_Spectroscopy/scripts/validate_proxima_molecular_ablation_loo.py), [referencias](../Thermal_Emission_Spectroscopy/scripts/retrieval_reference.py), [calibración auxiliar](../Thermal_Emission_Spectroscopy/scripts/report_proxima_loo_lin_sigma.py) y [análisis integrado](../Thermal_Emission_Spectroscopy/scripts/analyse_proxima_a1_a3_corrected_integrated_20261029.py) alimentan [tablas y procedencia](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a1_a3_integrated_20261029/) y el informe. El CSV histórico `life_proxima_loo_lnB_sigma_lin_2026-10-10.csv` también figura entre los insumos para la comparación metodológica: conservarlo aunque sea histórico.
6. **Figuras.** [plot_proxima_retrieval_products.py](../Thermal_Emission_Spectroscopy/scripts/plot_proxima_retrieval_products.py) y su modo `--official-corrected-bin-matrix-fulls` generan el atlas. [Informe del atlas](life_proxima_corrected_binning_full_posteriors_plot_2026-10-28.md) y sidecar de procedencia registran muestras, perfiles y configuraciones. El [índice de productos](../Thermal_Emission_Spectroscopy/final_products/README.md) identifica las figuras oficiales de emisión y SNR.

## Carpetas de retrieval directamente utilizadas

Rutas relativas a `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/`; recuentos de `input_hashes.csv`, no recuentos totales de carpetas:

| Carpeta | Insumos | Función |
| --- | ---: | --- |
| `a1_a3_corrected_binning_matrix_loo_20261021_r01` | 332 | Matriz principal A1/A3, manifiestos y auditoría. |
| `a3_1_10h_binning_corrected_loo_20261020_r03` | 62 | Completos y ablaciones A3 de referencia a 1/10 h. |
| `a3_100h_binning_corrected_loo_20261019` | 22 | Ablaciones A3 a 100 h. |
| `a3_100h_binning_corrected_mpi14_resume_20261018` | 11 | Completo A3 a 100 h. |
| `a3_1000h_binning_corrected_20261014` | 7 | Completo A3 a 1000 h exploratorio. |
| `a0_fixed_reference_A3_1000h_binning_corrected_20261016_relaunch_01` | 23 | Referencias fijadas A0 a 1000 h exploratorias; aceptación pendiente. |

Estos números suman 457; los otros 23 insumos incluyen datasets, forwards, scripts, perfiles y tablas. Conservar también manifiestos, configuraciones, scripts y registros no enumerados en el CSV cuando documenten cómo se generaron las corridas.

## Evidencia histórica y decisiones pendientes

- `a3_1_10h_binning_corrected_loo_20261020_r02` y `a3_100h_binning_corrected_20261017` son intentos anteriores que el [inventario de 979 archivos](evidence/life_proxima_a1_a3_release_2026-10-28/README.md) conserva como procedencia. Son candidatos a una futura sección histórica, no a borrar sin revisar dependencias y enlaces.
- `molecule_ablation_loo_20261004` y la tabla LOO de octubre representan una comparación anterior; la tabla es entrada explícita del análisis vigente. Revisar referencias y usos antes de mover cualquiera de sus productos.
- Los atlas anteriores y las copias en `plots/history/` conservan evolución editorial; el README de productos identifica el atlas vigente y las versiones anteriores. Las imágenes idénticas pueden cumplir funciones de promoción o archivo; la coincidencia de hash no demuestra que sobre una ruta.
- `a3_1000h_full_20261011`, `a0_fixed_reference_20261010`, `a0_fixed_reference_A3_1000h_20261012`, `a0_fixed_reference_A3_1000h_binning_corrected_20261015` y `POSEIDON_output` requieren auditoría de enlaces y procedencia antes de clasificarlas para mover o borrar. El inventario de 480 insumos no basta para demostrar que no se usan en otras figuras o trabajos.
- Datos externos, versiones, código upstream y generadores de datasets requieren un inventario de dependencias transitivas y sus ubicaciones actuales. La copia de noviembre y la de octubre excluyen entorno y opacidades externas; véase [resguardo](life_proxima_resguardo_resultados_vigentes_2026-11-14.md).

No se movió ni eliminó ningún archivo. Para una reorganización reproducible: completar el inventario de dependencias y referencias, preparar mapeo ruta antigua→nueva por lote, actualizar scripts/manifiestos/documentos sin alterar hashes históricos, verificar lectura de insumos y figuras, y proponer rutas exactas antes de cualquier eliminación.
