# Figura oficial y borrador LIFE Proxima actualizados

Fecha: 2026-10-20, America/Bogota. Solicitud: actualizar el texto adjunto y la figura oficial con el nuevo A3–100 h; registrar como pendiente la repetición homogénea del análisis. No se ejecutaron nuevos retrievals ni se modificó el `.tex` abierto.

> **Estado de figura:** este documento conserva la actualización parcial del 20-oct como historial. El atlas visual vigente, con los seis completos A1/A3 de 1/10/100 h y binning corregido, se generó el 26-oct: [informe, procedencia y artefactos](life_proxima_corrected_binning_full_posteriors_plot_2026-10-26.md). Los archivos enlazados en esta nota no se sobrescribieron.

## Productos entregados

- [Borrador completo para acordar en chat](life_proxima_manuscript_results_draft_2026-10-20.md).
- [Figura oficial PNG](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima.png), [PDF](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima.pdf) y [SVG](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima.svg).
- [Procedencia por caso, hashes y valores de las etiquetas](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima.provenance.json).
- [Archivo de versiones anteriores y manifiesto de promoción](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/history/official_before_A3_100h_update_20261020/promotion_manifest.json).
- [Análisis y tablas científicas que sostienen los valores nuevos](life_proxima_a3_100h_corrected_results_update_2026-10-20.md).

## Procedencia y alcance

El adjunto del usuario se leyó como texto de partida, no como instrucciones de ejecución: `C:/Users/User/.codex/attachments/16682138-0abb-4d32-8d90-9f25c8522d50/Texto pegado.txt`. Se conservaron la estructura narrativa y la explicación de métricas; se actualizaron cifras e interpretaciones de A3–100 h. Los números históricos de los tres contrastes A0 se retiraron del borrador vigente y fueron sustituidos por su motivación, diseño y pendiente.

La figura conserva el diseño oficial V2: seis moléculas, columna P–T y filas de 1, 10 y 100 h. Se cargan directamente las muestras, `log_X`, P–T y resultados de la campaña aceptada `a3_100h_binning_corrected_mpi14_resume_20261018/products` para **A3–100 h**. Los otros cinco casos siguen usando sus productos históricos. El mapa de corridas de auditoría permanece independiente; no se renombran ni copian archivos de retrieval.

Se recalculan todas las etiquetas de esa fila desde el nuevo completo: N2O tiene mediana log10 X = −6.1163 y z descriptivo respecto de A0 = 14.7325; NH3, −8.1704 y 9.4060. La densidad, barras q16–q84, perfiles recuperados y bandas P–T usan los productos nuevos. La referencia VULCAN y los colores mantienen sus significados previos.

La figura es una **actualización parcial de fuentes**, no una matriz homogénea corregida. Las cuatro omisiones A3–100 h de H2O/CO2/CH4/O3 aún no tienen comparadores nuevos emparejados. Sus casillas se muestran como pendientes en el borrador; no se combina su evidencia histórica con el nuevo completo. Las restricciones A0 de 100 h también quedan pendientes. Los CSV científicos históricos, las seis figuras canónicas previas y las variantes V1/V3 existentes se preservan. Las variantes en disco previas al 20-oct conservan sus fuentes históricas.

## Nota interna pendiente

**Pendiente: repetir la matriz completa de retrievals A1/A3 a 1, 10 y 100 h y sus comparaciones moleculares con el rebineado correcto y una configuración común. Recalcular desplazamientos respecto de A0, probabilidades individuales y conjuntas ≥ A1, K de regiones, intervalos en dex y contrastes con abundancias fijadas en A0; regenerar después las tablas y figuras de toda la serie. Conservar los resultados históricos para trazabilidad. Esta nota documenta trabajo pendiente; no inicia nuevas corridas.**

Esta explicación se mantiene en la documentación interna. El borrador destinado al manuscrito no menciona el rebineado y señala únicamente los resultados todavía pendientes de incorporar. Las conclusiones permanecen condicionadas al modelo, a una realización de ruido y a la adecuación del ajuste. La probabilidad de una región de abundancias no se interpreta como probabilidad causal de ExoFarm.

## Fuentes metodológicas comprobadas

- [Trotta (2008), tabla 1](https://arxiv.org/html/0803.4089): escala orientativa de ln B.
- [Benneke y Seager (2013), ecuaciones 8–9 y tabla 2](https://arxiv.org/pdf/1306.6325#page=5): calibración auxiliar bilateral y naturaleza de cota de la relación original.
- [Lin et al. (2021), sección 5.2 y tabla 2](https://arxiv.org/pdf/2105.09319#page=10): comparación con exclusiones moleculares.
- [Feroz et al. (2009)](https://academic.oup.com/mnras/article/398/4/1601/981502): cálculo de evidencia y estimación de incertidumbre numérica.
- Wogan et al. (2026): se volvió a leer el PDF primario local, especialmente pp. 7–9; SHA-256 `46d3cdb0793dc8d4484a578c90e9b01b5ed23d62c9739dc840911defb83d12f5`. Sus masas de regiones y odds motivan la adaptación a abundancias. [Nota metodológica y ruta primaria](life_proxima_wogan_abundance_region_bayes_2026-10-15.md).
- [Schwieterman et al. (2018)](https://arxiv.org/abs/1705.05791), [Schwieterman et al. (2022)](https://arxiv.org/abs/2210.01669) y [Huang et al. (2022)](https://arxiv.org/abs/2107.12424): interpretación contextual y limitaciones de biofirmas, reservadas para Discusión.

## Reproducción y revisión

Script: [plot_proxima_retrieval_products.py](../Thermal_Emission_Spectroscopy/scripts/plot_proxima_retrieval_products.py).

```text
.venv/Scripts/python.exe Thermal_Emission_Spectroscopy/scripts/plot_proxima_retrieval_products.py --official-a1-a3-times --output-dir Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/official_A3_100h_update_20261020
```

La ejecución finalizó con exit 0. Se revisó visualmente el PNG completo: distribución, etiquetas, márgenes, bandas y ausencia de recortes. Los seis casos y sus hashes figuran en el JSON; se verificó que solo A3–100 h tiene la fuente corregida y que las copias promovidas coinciden byte a byte con los productos generados. El modelo histórico de auditoría continúa accesible desde su mapa original.
