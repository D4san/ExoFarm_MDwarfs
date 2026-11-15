# Validación de LPJmL con ocho celdas y dos procesos MPI

Fecha: 2026-09-07. Campaña: `mpi_smoke_20260907`.
Resultado: **prueba de interfaz aceptada**, con salvedades de entradas.

## Pregunta y procedimiento

Se comprobó que el LPJmL instalado en este equipo puede ejecutar el equilibrio
natural, escribir un reinicio, reutilizarlo en A1 con ciclo de N y generar
salidas agrícolas auditables usando MPI. Se emplearon LPJmL 6.0.6, commit
`5af44a1ed023279a23c28d6dfe76945b97aaac57`, Open MPI 4.1.6, dos ranks y
las celdas 27410–27417. Ubuntu y los productos están en el disco E:.

Las entradas oficiales fueron verificadas como se describe en el
[registro de recuperación](lpjml_wsl_storage_recovery_2026-09-07.md).
El workflow es [run_mpi_smoke.sh](../Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction/run_mpi_smoke.sh),
ejecutado desde su copia Linux con finales LF. La configuración se produce con
[prepare_configs.py](../Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction/prepare_configs.py)
y el resumen con [analyze_n_fluxes.py](../Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction/analyze_n_fluxes.py).

```bash
bash /home/dasan/exofarm-lpjml-runtime/workflow_20260907/run_mpi_smoke.sh \
  --lpjml-root /home/dasan/exofarm-lpjml-runtime/LPJmL-6.0.6 \
  --input-root /home/dasan/lpjml-data/public_standard \
  --results-dir /home/dasan/exofarm-lpjml-runs/mpi_smoke_20260907 \
  --mpi-ranks 2
```

Para repetir, usar un directorio de resultados nuevo. El piloto usa 2100 años
de spin-up natural y 30 de spin-up gestionado; conserva salidas 1996–2005.
El enrutamiento fluvial está desactivado en este subconjunto; la campaña
global requerirá la configuración global y su propio spin-up.

## Resultados directos

- `readiness=PASS`; 16 CPUs lógicas, 31.3 GiB RAM y 789 GiB libres al inicio.
- Equilibrio natural: ocho celdas procesadas, terminación correcta, 47 s totales.
- A1: ocho celdas procesadas, terminación correcta, 27 s totales.
- Runner con código 0 y `mpi_smoke=PASS`.
- Ocho pruebas existentes de cálculo aprobadas, incluidas la relación de dos
  átomos de N en N2O frente a uno en NH3 y la integración por área una sola vez.
- Reinicio de 113,373 bytes; SHA-256 idéntico antes/después de copiarlo a A1:
  `d3f05f4bbc5f5e6894ceb9912714f13c3fc869e4ae05aeefd331327c2ea3a977`.

Los cinco NetCDF principales tienen forma `(time=10, lat=16, lon=1)`.
Contienen exactamente ocho posiciones válidas por año; las otras ocho son
relleno geográfico. La máscara válida coincide entre área, fracción agrícola,
N2O por nitrificación, N2O por desnitrificación y NH3, y permanece constante.
Todos los valores de esas ocho celdas son finitos y no negativos; las áreas son
positivas y las fracciones agrícolas están entre cero y uno. La coordenada
temporal declara días desde 1996 y diez pasos anuales coherentes con 1996–2005.
La primera comprobación asumió incorrectamente ocho posiciones totales; se
corrigió el criterio de auditoría tras inspeccionar coordenadas y relleno,
sin cambiar ni regenerar los datos.

| Variable | Unidad | Mínimo válido | Máximo válido |
| --- | --- | ---: | ---: |
| N2O nitrificación agrícola | gN/m2/yr | 0.000627508 | 0.0973125 |
| N2O desnitrificación agrícola | gN/m2/yr | 0.0000528293 | 0.565888 |
| NH3 agrícola | gN/m2/yr | 0.000175423 | 2.49230 |

La integración del subconjunto da medias de `0.00233250 TgN/yr` para N2O-N
y `0.00211911 TgN/yr` para NH3-N. Son diagnósticos de estas ocho celdas.
Los flujos moleculares planetarios quedan deliberadamente en `null`.

## Salvedades y siguiente paso

Los logs conservan advertencias sobre suelo y extensión temporal de clima,
deposición, laboreo, densidad ganadera y fechas de siembra. En la celda 27415
se advierte una suma de fracciones de uso de suelo superior a uno entre 1871
y 1903, con máximo registrado 1.004638. Esto debe revisarse antes de aceptar
resultados globales; no se ajustaron las entradas para ocultar la advertencia.

La interpretación de proyecto es que funcionan la ejecución MPI, la transferencia
del reinicio y la extracción de flujos. Esta prueba no valida convergencia
global, hidrología global, desempeño a muchos ranks ni emisiones planetarias.
El siguiente paso es preparar la campaña global A1 según el
[runbook](lpjml_global_a1_mpi_other_pc_runbook.md), manteniendo la revisión de
estas advertencias y la aceptación física de sus productos como puertas propias.
No se ha lanzado la campaña global ni modificado VULCAN.

## Evidencia conservada

Productos completos: `/home/dasan/exofarm-lpjml-runs/mpi_smoke_20260907`.
Copia compacta versionable en [evidence/mpi_smoke_20260907](evidence/mpi_smoke_20260907/):
[validación](evidence/mpi_smoke_20260907/validation.json),
[runner](evidence/mpi_smoke_20260907/runner.log),
[pruebas](evidence/mpi_smoke_20260907/unit_tests.log), configuraciones, logs
de ambas fases, resumen JSON/CSV y manifiesto SHA-256. No se generaron figuras.
