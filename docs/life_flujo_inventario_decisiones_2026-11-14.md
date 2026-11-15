# Inventario operativo y decisiones de organización LIFE — 2026-11-14

La [guía de lectura](../Thermal_Emission_Spectroscopy/GUIA_LECTURA.md) y el [mapa de flujo](life_proxima_mapa_flujo_y_custodia_2026-11-14.md) son las entradas para comprender la serie actual. [Inventario de 14 carpetas de retrieval](evidence/life_flujo_inventario_2026-11-14/campanas_retrieval.csv): incluye tamaño, recuento de insumos del análisis de 480 archivos y menciones textuales en documentación/scripts. El recuento de menciones es orientativo: no detecta todas las referencias indirectas ni prueba independencia. [Imports estáticos de 97 scripts Python](evidence/life_flujo_inventario_2026-11-14/scripts_imports_estaticos.csv): solo `import`/`from` con módulos hermanos, no dependencias dinámicas, comandos, shell, archivos ni paquetes externos.

Seis carpetas contienen insumos del análisis vigente o su extensión exploratoria. Dos intentos anteriores están documentados como evidencia histórica. Las otras seis precisan auditoría de usos; en particular, `molecule_ablation_loo_20261004` y `POSEIDON_output` contienen productos extensos y no se clasifican como prescindibles. Datos, manifiestos, logs y referencias fuera de `input_hashes.csv` también pueden ser necesarios.

## Dependencias externas observadas

- `D:\Proyectos\IA_SpecAtm_Bio\Data\POSEIDON\inputs` y `stellar_grids` existen; no se inspeccionó ni respaldó su contenido completo.
- `D:\Proyectos\IA_SpecAtm_Bio\Data\POSEIDON\inputs\opacity\Opacity_database_v1.3.hdf5` existe y ocupa 65.967.173.018 bytes. La metodología lo identifica como base High-T utilizada. No se calculó hash ni se verificó una segunda copia.
- `Photochemical_Modeling/Config/Stellar_Spectra/hlsp_muscles_multi_multi_gj551_broadband_v22_adapt-const-res-sed.fits` existe, 5.189.760 bytes; comprobar su correspondencia con el manifiesto estelar de la campaña antes de atribuir integridad.
- La captura histórica de paquetes del entorno POSEIDON está en [evidence](evidence/life_proxima_a1_a3_release_2026-10-28/conda_POSEIDON_snapshot_2026-10-28.txt); el entorno ejecutable WSL, su estado actual, opacidades, PHOENIX y scratch aún no se han verificado ni respaldado íntegramente. Una lista de paquetes no sustituye sus binarios o datos.
- El respaldo `E:\Respaldos\ExoFarm_MDwarfs\emision_resguardo_2026-11-14` incluye emisión, docs y experimentos en el estado previo a la creación de esta guía e inventario; no incluye todos los perfiles externos a esas carpetas ni las bases externas. El respaldo histórico cubre los perfiles enumerados en sus manifiestos; comprobar cobertura antes de una limpieza transversal.

## Orden de intervención

1. Preservar rutas vigentes, datos y campañas completas mientras se revisan imports, subprocess, configuraciones y referencias cruzadas. Mantener intactos manifiestos históricos y hashes.
2. Para las seis carpetas pendientes, rastrear informes, scripts, productos y respaldo de cada campaña; decidir si pertenecen al flujo vigente, comparación histórica o evidencia de auditoría. Un resultado fuera de los 480 insumos puede servir a otro producto.
3. Diseñar un índice de scripts por etapa y campaña. Un cambio físico de ruta de scripts requiere actualizar imports, comandos y documentación y verificar los consumidores; realizarlo por lotes después de establecer una tabla de equivalencias.
4. Mantener resultados históricos en su ubicación hasta verificar todas sus referencias; preparar una propuesta de traslado con origen y destino exactos, sin modificar el contenido de manifiestos congelados.
5. Para imágenes byte idénticas, registrar el papel de cada ruta y sus consumidores; conservar los nombres canónicos y proponer candidatos concretos solo tras verificar referencias. La eliminación requiere aprobación de rutas exactas conforme a `repository_cleanup_workflow.md`.

No se han movido ni eliminado archivos. El inventario facilita la siguiente revisión pero no constituye un cierre completo de dependencias ni una autorización de borrado.

## Alcance indicado por el usuario — 2026-11-14

El usuario prioriza conservar el flujo vigente A1/A3 a 1, 10 y 100 h; no tiene interés en la extensión de 1000 h ni en mantener la campaña de ablaciones anterior dentro del flujo principal. La campaña `molecule_ablation_loo_20261004` es la serie histórica, anterior a la matriz con binning corregido. Su tabla resumida histórica todavía se lee en el script integrado del 29-oct para una comparación contextual, no como resultado oficial.

El script integrado actual también lee explícitamente las carpetas de 1000 h y genera sus tablas. Antes de retirar esas rutas, crear y verificar una ruta de análisis limitada a 1/10/100 h que reproduzca los productos actuales pertinentes, y preservar la procedencia histórica. Identificar las rutas exactas candidatas y solicitar aprobación antes de borrar, según `repository_cleanup_workflow.md`. No se autoriza inferir que carpetas antiguas adicionales son prescindibles sin auditar.
