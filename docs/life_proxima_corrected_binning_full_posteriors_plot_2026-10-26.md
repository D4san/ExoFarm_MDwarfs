# Atlas de posteriores completas A1/A3 (edición inicial, 26-oct; historial preservado)

Fecha: 2026-10-26 (America/Bogota). Se actualiza el atlas comparativo de LIFE Proxima b para mostrar los retrievals completos A1 y A3 a 1, 10 y 100 h, usando productos con binning corregido. La figura mantiene el diseño oficial de seis especies, perfiles verticales y P–T; las versiones previas permanecen intactas.

## Artefactos oficiales

- [PNG](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_corrected_bin_full_posteriors_PT_proxima_20261026.png)
- [SVG](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_corrected_bin_full_posteriors_PT_proxima_20261026.svg)
- [Procedencia JSON: muestras, resúmenes, entradas y hashes](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_corrected_bin_full_posteriors_PT_proxima_20261026.provenance.json)

En el corte previo a la regeneración del 28-oct
- [Generador reproducible](../Thermal_Emission_Spectroscopy/scripts/plot_proxima_retrieval_products.py), modo `--official-corrected-bin-matrix-fulls`.

El atlas tiene tres filas (1/10/100 h), seis columnas moleculares (H₂O, CO₂, CH₄, O₃, N₂O y NH₃) y una columna P–T. Los histogramas resumen los posteriores isochem; se muestran medianas e intervalos centrales 68 %, perfiles verticales VULCAN y una referencia efectiva A0. O₂ permanece activo en los retrievals completos, pero se omite del atlas para conservar el diseño establecido.

## Fuentes y estado de auditoría

| Caso | Campaña / corrida usada | Posterior | ln Z ± error nativo | χ² reducido | Estado de aceptación |
|---|---|---:|---:|---:|---|
| A1, 1 h | matriz r01 / `A1_1h_full` | 7.695 | 868,82 ± 0,17 | 0,95 | Auditoría independiente aprobada (28-oct) |
| A3, 1 h | campaña r03 / `A3_1h_full` | 6.026 | 866,28 ± 0,17 | 1,63 | Baseline corrected-bin previamente validado |
| A1, 10 h | matriz r01 / `A1_10h_full` | 6.601 | 889,99 ± 0,21 | 1,40 | Auditoría independiente aprobada (28-oct) |
| A3, 10 h | campaña r03 / `A3_10h_full` | 7.036 | 891,39 ± 0,21 | 1,22 | Baseline corrected-bin previamente validado |
| A1, 100 h | matriz r01 / `A1_100h_full` | 6.461 | 910,92 ± 0,24 | 1,73 | Auditoría independiente aprobada (28-oct) |
| A3, 100 h | campaña MPI14 validada / `A3_100h_full_BIN1_20261018_MPI14_resume01` | 7.268 | 894,33 ± 0,25 | 3,57 | Baseline corrected-bin previamente validado |

Las seis fuentes usan los datasets LIFE identificados por SHA-256 en el sidecar. Para A1 son `93fb65765101950063d5aa9a3dafae4df38273292cb0e3349e94b8a34516cfcc` (1 h), `ed39ae6dc5b8ff0d5c8aca3d126a2945343a289be30f3b8d9e8e72c434ee9b8f` (10 h) y `d66c886238a2916312c645589be8601828fbf0a7cd2f02a383ef1d6a3454b5e3` (100 h). A3 usa `a3043e5de76a834983949e6eca12636ea4de174ebdb2db0853155282c100dee2`, `46a026504b9b9521fa29407a501169b9d3cfc433de40a91b8ade86d7767abb5b` y `78662546181a5b74391a14b7b73ae80d879200a74db6a4bc5338e3ce7eee4705`, respectivamente. El sidecar guarda hashes de cada muestra, `log_X`, P–T, resultados, configuraciones y registros del operador disponibles.

Configuración completa compartida: 15 parámetros declarados/14 libres, `N_live=800`, `ev_tol=0.5`, `R=10000`, 3–20 μm, perfil térmico Madhu, abundancias isochem, superficie negra fija a 1 bar, sin inflación de errores y O₂ activo. El callback usa solapamiento fotónico con bordes de canal punto medio y conversión energía→fotones en el centro exacto del canal. Los manifiestos, configuraciones y registros del operador quedan hasheados o enlazados en el sidecar.

**Corte histórico al generar el atlas (26-oct):** la campaña todavía estaba ejecutándose y la nota de progreso original registró auditoría A1 pendiente. El 28-oct, los 33 retrievals r01 y los tres completos A3 de referencia pasaron la auditoría independiente. Se actualizó el sidecar de procedencia; los PNG y SVG permanecen sin cambios y coinciden con sus hashes. El PDF listado por el sidecar no se encontró en la ruta oficial. El [informe de cierre de la matriz](life_proxima_a1_a3_corrected_binning_matrix_results_2026-10-28.md) contiene las comparaciones LOO.

## Alcance interpretativo

Cada `ln Z` corresponde a un dataset, exposición y realización de ruido distintos. Los valores de líneas diferentes no constituyen factores de Bayes A1/A3. La figura sirve para comparar descriptivamente las posteriores bajo el modelo completo; las etiquetas de desplazamiento respecto a A0 no son significancias de detección ni demuestran origen agrícola. La auditoría valida la integridad de productos, no elimina las limitaciones del modelo. Hay una realización de ruido por caso y la likelihood es diagonal, según los manifiestos de las campañas.

## Reproducción y controles

Desde la raíz del repositorio:

```powershell
.venv\Scripts\python.exe -m py_compile Thermal_Emission_Spectroscopy\scripts\plot_proxima_retrieval_products.py
.venv\Scripts\python.exe Thermal_Emission_Spectroscopy\scripts\plot_proxima_retrieval_products.py `
  --official-corrected-bin-matrix-fulls `
  --output-dir Thermal_Emission_Spectroscopy\final_products\figures
```

La carga validó finitud y encabezados de las seis posteriores; comprobó los seis conjuntos de especies, las tablas P–T y los `log_X`, y rechazó cualquier dataset cuyo hash no coincidiera con el manifiesto congelado. El código terminó con exit 0 y se inspeccionó visualmente el PNG. No se modificaron datasets, productos de retrieval, archivos de campaña ni corridas activas. La versión V2 anterior y su informe del 20-oct se conservan como registro histórico.
