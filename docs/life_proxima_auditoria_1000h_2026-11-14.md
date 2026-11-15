# Auditoría de campañas LIFE Proxima de 1000 h — 2026-11-14

## Decisión de alcance

El usuario prioriza A1/A3 a 1/10/100 h y no tiene interés en 1000 h. La [ejecución centrada](life_proxima_flujo_1_10_100h_2026-11-14.md) reproduce las 11 tablas principales sin leer productos de 1000 h. La extensión del informe integrado del 29-oct permanece histórica y sus fijaciones A0 conservan `PENDING_FIXED_MOMENT_REVIEW`; el ajuste de 1000 h presenta problemas documentados.

## Carpetas identificadas

Rutas bajo `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/`. Tamaños incluyen logs y otros archivos locales, y son aproximados en MiB:

| Carpeta | Archivos | MiB | Papel y referencias |
| --- | ---: | ---: | --- |
| `a0_fixed_reference_A3_1000h_20261012` | 91 | 188,32 | Fijaciones A0 anteriores; comparación y reanudación documentadas en `life_proxima_a3_1000h_a0_comparison_2026-10-12.md` y `life_proxima_a3_1000h_mpi5_resume_2026-10-13.md`. |
| `a0_fixed_reference_A3_1000h_binning_corrected_20261015` | 28 | 0,53 | Intento corregido y auditoría de equivalencia del operador; bitácora del 15-oct. |
| `a0_fixed_reference_A3_1000h_binning_corrected_20261016_relaunch_01` | 62 | 122,32 | Tres fijaciones corregidas; auditoría del 17-oct y script integrado antiguo las leen. |
| `a3_1000h_binning_corrected_20261014` | 32 | 41,16 | Completo corregido, comparador de la extensión; script integrado antiguo y diagnósticos lo leen. |
| `a3_1000h_full_20261011` | 47 | 75,20 | Completo anterior, checkpoints y diagnósticos; informes y scripts históricos lo leen. |

Total: 260 archivos y aproximadamente 427,5 MiB. Los archivos de 1000 h también aparecen fuera de esas cinco carpetas: datasets, scripts, tablas, figuras e informes. Esta lista no es un inventario exhaustivo de todas esas rutas.

## Dependencias y preservación

El script integrado de 29-oct y sus informes/tablas de procedencia contienen rutas a estas campañas; moverlas rompería la reproducción histórica sin actualizar el consumidor o proporcionar una restauración con rutas originales. El script centrado de 1/10/100 h conserva dos constantes de nombres de campañas 1000 h heredadas, pero no las utiliza ni registra entradas de ellas en la ejecución verificada.

La copia completa de emisión en `E:\Respaldos\ExoFarm_MDwarfs\emision_resguardo_2026-11-14` contiene estas carpetas en su estado al crearla, incluidos logs; su manifiesto registra sus hashes. También existen respaldos históricos de partes de la extensión, cuyo alcance se documenta en [evidence de octubre](evidence/life_proxima_a1_a3_release_2026-10-28/README.md). El commit Git de respaldo conserva los archivos no ignorados, pero Git ignora `.log`.

## Propuesta

Tratar estas cinco carpetas como evidencia histórica fuera de la navegación principal. Antes de mover o eliminar, inventariar referencias de todos los productos de 1000 h fuera de ellas, comprobar las copias relevantes y definir una restauración que preserve rutas y hashes históricos. El flujo centrado ya no necesita esos datos, pero la auditoría no demuestra que todos los consumidores históricos estén desacoplados. No se han movido ni eliminado archivos. Para eliminar se requieren rutas exactas aprobadas, según `repository_cleanup_workflow.md`.
