# Resguardo de resultados vigentes de emisión — 2026-11-14

El punto de partida para la serie LIFE Proxima A1/A3 a 1, 10 y 100 h es el [análisis integrado del 29 de octubre](life_proxima_a1_a3_retrievals_analisis_integrado_2026-10-29.md). Su extensión A3–1000 h sigue siendo exploratoria y `PENDING_FIXED_MOMENT_REVIEW`.

## Qué consultar

- [Informe científico vigente](life_proxima_a1_a3_retrievals_analisis_integrado_2026-10-29.md): resultados, interpretación y límites.
- [Tablas, hashes de 480 insumos y procedencia](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a1_a3_integrated_20261029/).
- [Script del análisis integrado](../Thermal_Emission_Spectroscopy/scripts/analyse_proxima_a1_a3_corrected_integrated_20261029.py).
- [Productos finales y atlas oficial](../Thermal_Emission_Spectroscopy/final_products/README.md).
- [Inventario anterior y suplementos de campañas](evidence/life_proxima_a1_a3_release_2026-10-28/README.md): identifica campañas, datasets, perfiles, forwards, configuración y evidencias históricas.

## Comprobación y copia independiente

El 14 de noviembre se recalcularon los hashes de los 480 insumos enumerados en `input_hashes.csv`: **480 coincidentes**. El inventario original de 979 archivos y el de 12 supervisores coinciden tanto en origen como en la copia histórica de E:. Los suplementos de 125 y 28 archivos coinciden en la copia histórica; en origen, siete y cinco entradas respectivamente han cambiado, todas correspondientes a índices, README o bitácoras actualizados. No se sustituyeron los inventarios históricos.

Se creó una nueva copia en `E:\Respaldos\ExoFarm_MDwarfs\emision_resguardo_2026-11-14`, con **2941 archivos y 3974409281 bytes**: todo el árbol `Thermal_Emission_Spectroscopy`, `docs`, `experiments` y documentación raíz existente. Incluye archivos `.log` ignorados por Git. Cada archivo se verificó mediante SHA-256 de origen y destino inmediatamente después de copiar. `SHA256SUMS.txt` y `BACKUP_INFO.json` están en la raíz del respaldo. SHA-256 del manifiesto: `56cb2b3a37d53c78c21dfb3cbcf3c5ee8cd6fdd5d36a2893c95b22029001ed94`.

La copia excluye cachés `__pycache__` y `.pyc`, y no incluye entornos, opacidades, entradas o datos externos fuera de las carpetas indicadas. Por tanto preserva productos y documentación para inspección, pero no garantiza por sí sola ejecutar de nuevo POSEIDON o LIFEsim. La captura histórica de paquetes se encuentra en el inventario anterior; identificar y resguardar dependencias externas sigue pendiente. No se movieron ni borraron productos.
