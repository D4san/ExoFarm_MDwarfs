# Franck et al. (2011): reproducción moderna y flujos de N

> **A0 validado 2026-09-22:** `a0_natural` terminó con `exit_code=0`, cubrió
> 1996--2005 y pasó la validación global. La integración y el contraste por
> especie están en [`docs/lpjml_global_a0_control_validation_2026-09-22.md`](../../../docs/lpjml_global_a0_control_validation_2026-09-22.md); no se ejecuta VULCAN hasta resolver el alcance/calibración de NH3.

> **Control natural A0 reanudado 2026-09-21 00:30 UTC:** el checkpoint de
> `a0_natural` del año 1587 fue verificado por SHA-256 y la campaña volvió a
> ejecutarse con ocho ranks desde `restart/checkpoint.lpj`. La interrupción
> anterior no produjo un error de LPJmL; este bloque conserva el historial de la
> reanudación.

> **Campaña global A1 validada 2026-09-20:** `global_a1_checkpoints_20260909`
> completó 1996--2005 con 67 420 celdas, ocho ranks y `exit_code=0`. El
> validador y `analyze_n_fluxes.py --coverage global` produjeron los informes
> bajo `a1_2005_n/output/analysis/`; el detalle y la comparación con la
> referencia congelada están en
> [`docs/lpjml_global_a1_validation_2026-09-20.md`](../../../docs/lpjml_global_a1_validation_2026-09-20.md).
> Estos son flujos agrícolas integrados de stand. El control natural emparejado
> ya está validado; el contraste A0/A1 está documentado y todavía no se ha
> acoplado a VULCAN.

## Objetivo de la primera prueba

Este flujo separa dos preguntas que no deben mezclarse en una sola corrida:

1. **Benchmark 2005 con ciclo de N** (`a1_2005_n`): usa el uso de suelo
   histórico, fertilizante y manure prescritos para comprobar la interfaz de
   productividad y obtener pérdidas agrícolas de `N2O` y `NH3`.
2. **Potencial de rendimiento** (`potential_yield_unlimited_n`): simula todos
   los cultivos en cada celda con N no limitante para reconstruir el método de
   capacidad de carga de Franck et al. No se interpretan sus salidas de N como
   emisiones físicas.

La primera ejecución es un piloto de una celda. Conserva el mínimo interno de
2100 años exigido por LPJmL 6.0.6 para equilibrar el suelo, pero solo valida
configuración, lectura de entradas, restart y forma/unidades de las salidas. El
modo `global` es el que puede producir resultados científicos.

## Rama de capacidad seleccionada

Para los escenarios hipotéticos inspirados en Franck et al. (2011) se
seleccionó como primera rama `FR-genghis-khan-crop-only`, separada de A0--A3.
`FR-save-forests` queda como segunda rama:

- `FR-genghis-khan-crop-only`: cultivo anual energético ganador en toda la
  tierra elegible, sin pasture, ganado ni manure;
- `FR-save-forests`: el mismo mapa crop-only, excluyendo la máscara de bosques
  tropicales y boreales perennifolios.

La rama potencial `potential_yield_unlimited_n` se usa para obtener los
rendimientos candidatos. La campaña global activa
`fr_genghis_potential_20260922_chunks_ch4` conserva las cinco salidas de
selección más los diagnósticos CH4, y secuencia bloques de 8.000 celdas con un
rank para mantenerse dentro de la memoria de WSL; cada bloque tiene su propio
restart y `checkpoint_runner.py`. La pasada local desactiva ríos y embalses
porque la red de vecinos es global; esa limitación queda en el manifiesto. Al
finalizar se construirá el mapa `landuse` sintético y se ejecutará una segunda
campaña con ciclo de nitrógeno y metano. La campaña crop-only usará
`grazing = "none"`, `grazing_others = "none"`, `manure_input = false` y
`prescribe_lsuha = false`. `landuse = "all_crops"` no selecciona por sí mismo
el cultivo ganador. El diseño completo, incluido el plan methane-enabled, está en
[`docs/lpjml_franck_capacity_scenarios_design_2026-09-22.md`](../../../docs/lpjml_franck_capacity_scenarios_design_2026-09-22.md).

El planificador `run_capacity_potential_chunks.sh` admite concurrencia acotada
con `MAX_PARALLEL`, manteniendo un rank MPI por bloque; el valor por defecto
sigue siendo 1. Desde 2026-10-01 01:54 COT la campaña CH4 corre dos bloques
(`00000_07999` y `08000_15999`) simultáneamente, con un rank MPI en cada uno.
`checkpoint_runner.py` conserva todas las generaciones
(`MAX_ARCHIVED_CHECKPOINTS=0`). A las 05:14 COT ambos procesos seguían activos;
el bloque 0 reporta año 1553 y conserva el checkpoint de año 1552. El bloque 1
guardó y reanudó año 1482 con hash verificado
`79698dfb5cd3558c13c2219bf8fe6d862fade574c11a27764c74acec48577f79`.
La ganancia real de velocidad se medirá con el avance por bloque. Hubo un
lanzamiento breve en otro directorio, que se detuvo y cuyos archivos parciales
se preservan separados. Véase [la nota de paralelismo y checkpoints](../../../docs/lpjml_capacity_chunk_parallelism_2026-10-01.md).

## Qué es reproducción y qué no es réplica exacta

La referencia usó una versión LPJmL 3.x, clima CRU mensual y rendimientos medios
de 1996-2005. La ruta pública disponible se fija en LPJmL `v6.0.6`, commit
`5af44a1`, con el conjunto estándar GSWP3-W5E5. Por ello esta campaña es una
**reproducción metodológica moderna**, no una réplica numérica bit a bit. Los
valores publicados siguen siendo objetivos de comparación, no números que se
deban forzar:

El archivo oficial esperado, su tamaño, URL y checksum quedan fijados en
`input_dataset_manifest.json`; las entradas grandes se almacenan fuera de Git.

| Escenario | 0 m2/persona | 750 m2/persona | 1500 m2/persona |
| --- | ---: | ---: | ---: |
| Benchmark de uso de suelo 2005 | 11.4 | - | - |
| Genghis-Khan | 281.5 | 88.6 | 53.8 |
| Save forests | 150.4 | 50.5 | 31.1 |
| Burger | 96.4 | 51.4 | 36.1 |
| Wheat-maize-rice + pasture | 244.2 | 84.4 | 52.2 |

Las cifras están en miles de millones de personas.

## Reglas reconstruidas de la fuente primaria

- resolución global de 0.5 grados;
- promedio de rendimientos 1996-2005;
- 11 CFT y pasture;
- selección por celda del cultivo con mayor rendimiento energético;
- solo el órgano de almacenamiento cosechado cuenta como alimento;
- profundidad máxima de deshielo mínima de 1 m (`1000 mm` en LPJmL 6.0.6);
- irrigación limitada por descarga fluvial en la campaña global;
- requerimiento de `1e6 kcal persona-1 año-1`;
- transferencia de pasture a productos animales del 10 %;
- reserva local de 0, 750 o 1500 m2 por persona, aplicada por banda de 10 grados;
- sin comercio entre bandas;
- `save forests` excluye celdas cuya vegetación natural potencial está dominada
  por bosque tropical evergreen o boreal evergreen.

El artículo también duplicó la producción anual donde el ciclo era menor de
medio año y no estaba limitado por temperatura. LPJmL 6.0.6 ya ofrece segunda
cosecha (`pft_harvestc2`), por lo que se conservarán ambas salidas y se evitará
duplicar de nuevo una cosecha que el modelo moderno ya haya simulado.

## Conversión de cosecha a energía

LPJmL informa carbono cosechado en `gC m-2 yr-1`. El código de LPJmL define:

```text
carbono = 0.45 * biomasa seca
```

Para cada cultivo:

```text
kcal m-2 yr-1 = gC m-2 yr-1 / 0.45 / fracción_seca * kcal g-1_húmedo
```

Las fracciones y densidades energéticas están transcritas en
`crop_energy_table.csv` desde la Tabla 2 de Franck et al. (2011). Sugarcane
existe en LPJmL 6.0.6, pero se excluye de la matriz del artículo.

## Salidas de nitrógeno

El benchmark solicita, como mínimo:

- `cellfrac_agr`, para auditar la fracción agrícola emisora de cada celda;
- `n2o_nit_agr` y `n2o_denit_agr`;
- `nh3_agr` y `n2_agr`;
- `nfert_agr`, `nmanure_agr`, `nleaching_agr`, `nuptake_agr`, `bnf_agr` y
  `ndepo_agr`.

Los campos con sufijo `_agr` ya incluyen la ponderación por fracción de los
rodales que LPJmL clasifica como agrícolas. Se integran con `land_area`, sin
volver a multiplicar por `cellfrac_agr`. Esa fracción incluye el conjunto de
rodales gestionados definido por `isagriculture(stand)`; para restringir el
análisis a cultivos/CFT concretos se necesitan `cftfrac` y `cft_n2_emis` (o una
salida equivalente) en una corrida diagnóstica.

Todas son masa de **N**, no masa molecular. La integración global debe
multiplicar `gN m-2 yr-1` por el área terrestre de cada celda. Después:

```text
N2O = n2o_nit_agr + n2o_denit_agr  (2 átomos de N por molécula)
NH3 = nh3_agr                        (1 átomo de N por molécula)
```

Para VULCAN 1-D se reportará el total en `TgN yr-1` y el flujo molecular medio
distribuido sobre `4 pi R_earth^2`. No se confundirá ese promedio planetario con
el flujo medio sobre el área agrícola emisora.

## Ejecución

Requisitos de esta ruta WSL/Ubuntu:

- checkout oficial LPJmL `v6.0.6` bajo `software/LPJmL/`;
- `build-essential`, `libjson-c-dev`, `libnetcdf-dev`, `libudunits2-dev` y
  `zlib1g-dev` para compilar;
- `python3`, NumPy y SciPy para el posprocesamiento NetCDF;
- paquete estándar verificado en
  `/mnt/c/Proyetos/Data/LPJmL/public_standard` o una ruta indicada mediante
`LPJINPATH`;
- espacio adicional suficiente antes de extraer el archivo de 37.8 GB.

El generador elimina el `inpath` absoluto del servidor PIK que viene en la
plantilla upstream. Así, `-inpath` y `LPJINPATH` controlan de forma explícita la
ruta local sin modificar los 76 archivos oficiales extraídos. También genera
copias ASCII de compatibilidad para los cuatro metadatos descriptivos que el
parser estricto de LPJmL 6.0.6 no acepta; cada campaña conserva SHA-256 del
original y de la copia, que sigue apuntando a los binarios oficiales.

Piloto de interfaz:

```bash
cd /mnt/c/Proyetos/Repos/ExoFarm_MDwarfs/Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction
bash ./run_first_test.sh --mode pilot
```

Piloto incluyendo la rama de potencial:

```bash
bash ./run_first_test.sh --mode pilot --with-potential
```

Integración de los flujos del benchmark, después de una corrida completa:

```bash
python analyze_n_fluxes.py \
  --output-dir results/<campaign>/a1_2005_n/output \
  --coverage pilot
```

El modo `pilot` deja vacías deliberadamente las columnas de flujo molecular
planetario. Cambiar a `--coverage global` solo cuando la corrida incluya todas
las celdas y haya superado la aceptación de campaña.

Campaña global (solo después de aceptar el piloto y registrar recursos):

```bash
bash ./run_global_a1_mpi.sh --help
```

Cuando termine la selección global, el mapa se valida con `lpjcheck` y la rama
final se lanza con:

```bash
python build_capacity_landuse.py \
  --potential-root /home/dasan/exofarm-lpjml-runs/fr_genghis_potential_20260922_chunks_ch4/chunks/00000_07999 \
  --potential-root /home/dasan/exofarm-lpjml-runs/fr_genghis_potential_20260922_chunks_ch4/chunks/08000_15999 \
  --ncell 67420 \
  --output-dir /home/dasan/exofarm-lpjml-runs/fr_genghis_crop_only_20260922/map
bash ./run_capacity_genghis_chunks.sh --phase all --mpi-ranks 1 --chunk-size 8000 \
  --lpjml-root /home/dasan/exofarm-lpjml-runtime/LPJmL-6.0.6-balance-fix-20260912 \
  --input-root /home/dasan/lpjml-data/public_standard \
  --campaign-dir /home/dasan/exofarm-lpjml-runs/fr_genghis_crop_only_20260922 \
  --landuse-meta /home/dasan/exofarm-lpjml-runs/fr_genghis_crop_only_20260922/map/genghis_khan_crop_only_2005.clm.json
```

El lanzador repite el spin-up con `with_methane=true`, activa `only_crops` en
2005 y conserva los reinicios y hashes por fase. La campaña final por bloques
deja explícita la limitación de routing local. `run_capacity_potential_chunks.sh`,
`run_capacity_genghis_chunks.sh` y `build_capacity_landuse.py` son reproducibles
y no modifican VULCAN. `analyze_capacity_chunks.py` integra las salidas N y
CH4 de todos los bloques con sus unidades nativas.

La ejecución en otro PC, incluida la instalación de LPJmL/MPICH, verificación
de datos, smoke test MPI, selección de ranks, fases recuperables y aceptación,
está especificada en
[`../../../docs/lpjml_global_a1_mpi_other_pc_runbook.md`](../../../docs/lpjml_global_a1_mpi_other_pc_runbook.md).
La primera campaña global queda acotada a `A1`; la rama potencial de Franck se
mantiene separada hasta terminar el mapeo científico pendiente.

Los productos quedan bajo `results/<campaign>/`, ignorados por Git. Cada
campaña conserva configuraciones resueltas y un manifiesto con versión, commit y
clasificación científica.

## Pendientes antes de reproducir toda la Tabla 3

- mapear y documentar los 32 índices PFT/CFT del NetCDF moderno contra los 11
  CFT y pasture usados en el artículo;
- reconstruir la máscara PNV de `save forests`;
- resolver el umbral de productividad al que el artículo alude sin publicar su
  valor numérico;
- completar la campaña global de candidatos, generar el mapa de uso de suelo
  con el cultivo ganador por celda y aceptar la corrida crop-only methane-
  enabled con `lpjcheck`, checkpoints y cobertura global;
- validar la regla de segunda cosecha frente a las salidas modernas;
- ejecutar y aceptar la campaña A1 global preparada para MPI en el otro PC (cerrado el 2026-09-20); el control A0 y el contraste A1−A0 quedaron validados el 2026-09-22. Pendiente: decidir el alcance/calibración de NH3 antes de VULCAN.
