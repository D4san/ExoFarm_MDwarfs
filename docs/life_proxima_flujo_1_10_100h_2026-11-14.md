# LIFE Proxima: análisis centrado en 1, 10 y 100 horas — 2026-11-14

Por decisión del usuario, el flujo prioritario comprende A1/A3 a 1, 10 y 100 h con binning corregido. El análisis histórico integrado del 29 de octubre y sus productos se conservan. La extensión de 1000 h y la comparación con la tabla de ablaciones anterior quedan fuera de esta ejecución.

## Procedimiento y procedencia

[Script centrado](../Thermal_Emission_Spectroscopy/scripts/analyse_proxima_a1_a3_1_10_100h.py), derivado del [script congelado de 29-oct](../Thermal_Emission_Spectroscopy/scripts/analyse_proxima_a1_a3_corrected_integrated_20261029.py). Conserva los cálculos y verificaciones de la matriz primaria, incluidas las comparaciones con 36 auditorías previas de la matriz corregida. Es una copia de trabajo deliberada para preservar la fuente histórica; conviene extraer un núcleo compartido en una futura refactorización auditada. No se ejecutaron modelos ni retrievals nuevos.

Ejecución desde la raíz del repositorio con `.venv\Scripts\python.exe Thermal_Emission_Spectroscopy/scripts/analyse_proxima_a1_a3_1_10_100h.py`. La salida por defecto es una carpeta nueva y el script rechaza sobrescribirla; para una ejecución adicional, usar `--output` con otra carpeta. Las [tablas, hashes y procedencia](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a1_a3_1_10_100h_20261114/) registran 446 insumos, 42 modelos y 36 pares LOO.

## Verificación

Los SHA-256 de las 11 tablas primarias coinciden byte a byte con las correspondientes a la [edición del 29-oct](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a1_a3_integrated_20261029/): modelos, LOO, parámetros, enriquecimiento, probabilidades, regiones conjunta/marginal/resumen, ajustes, residuos y perfiles PT. Los 446 insumos registrados no contienen rutas de campañas `1000h`, `molecule_ablation_loo_20261004`, la tabla histórica `life_proxima_loo_lnB_sigma_lin_2026-10-10.csv` ni las regiones históricas `a1_regions_2026-10-15`. El inventario congelado de 979 archivos se comprueba como archivo de procedencia; sus entradas adicionales no se leen como datos del cálculo centrado.

Esta equivalencia verifica los productos tabulares de esta ejecución y no sustituye una auditoría de otras figuras, informes, rutas o usos de campañas antiguas. Los límites científicos del informe original —una realización por caso, prior, discrepancia de perfil y likelihood diagonal— siguen vigentes. A3–100 h presenta el ajuste deficiente ya documentado.

## Siguiente decisión de organización

Se pueden clasificar para revisión las campañas de 1000 h y la ablación antigua fuera del flujo centrado. Antes de moverlas o borrarlas hay que identificar sus otros consumidores, preservar la procedencia, preparar cambios de rutas y solicitar aprobación para destinos exactos de eliminación de acuerdo con `repository_cleanup_workflow.md`. El informe histórico y su script original todavía las referencian. La copia de respaldo previa del 14-nov no contiene esta nueva ejecución ni sus documentos.
