# Atlas oficial LIFE A1/A3: N₂O y NH₃ primero, sin panel P–T

Fecha: 2026-10-28 (America/Bogota). Tras revisar el primer atlas, se actualizó la composición solicitada: N₂O y NH₃ ocupan las dos primeras columnas; el panel P–T y la nota de estado fueron retirados. Se mantienen los perfiles verticales de abundancia molecular. Los seis completos A1/A3 a 1, 10 y 100 h siguen siendo la fuente de datos; no se relanzaron retrievals.

## Artefactos oficiales

- [PNG](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_posteriors_N2O_NH3_first_no_PT_proxima_20261028.png)
- [PDF vectorial](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_posteriors_N2O_NH3_first_no_PT_proxima_20261028.pdf)
- [SVG](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_posteriors_N2O_NH3_first_no_PT_proxima_20261028.svg)
- [Procedencia JSON: entradas, orden de moléculas, muestras y hashes](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_posteriors_N2O_NH3_first_no_PT_proxima_20261028.provenance.json)
- [Edición previa del 28-oct con panel P–T](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_corrected_bin_full_posteriors_PT_proxima_20261028.png)
- [Edición inicial del 26-oct](life_proxima_corrected_binning_full_posteriors_plot_2026-10-26.md)
- [Generador reproducible](../Thermal_Emission_Spectroscopy/scripts/plot_proxima_retrieval_products.py), modo --official-corrected-bin-matrix-fulls.

El PNG, PDF y SVG nuevos se regeneraron y sus SHA-256 coinciden con el sidecar. La grilla tiene tres filas (1/10/100 h) y seis columnas en este orden: N₂O, NH₃, H₂O, CO₂, CH₄ y O₃. O₂ permanece activo en los retrievals completos, pero se omite del atlas. El panel P–T queda fuera de esta edición; la información de abundancia vertical sigue visible en cada columna.

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

**Versiones anteriores preservadas:** la salida inicial del 26-oct y la edición del 28-oct que incluía P–T permanecen en la carpeta oficial como historial. La edición vigente descrita arriba prioriza N₂O/NH₃, retira el panel P–T y omite la nota de estado. La auditoría de retrievals y las comparaciones LOO están en el [informe final de matriz](life_proxima_a1_a3_corrected_binning_matrix_results_2026-10-28.md).

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
