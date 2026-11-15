# Ejecución de capacidad Franck--LPJmL (2026-09-22)

**Estado al 2026-09-22:** la rama `FR-genghis-khan-crop-only` está en la
selección global de rendimientos candidatos. La campaña activa es
`/home/dasan/exofarm-lpjml-runs/fr_genghis_potential_20260922_chunks_ch4`, con
`POTENTIAL_CHUNKS_RUNNING`, bloques de 8.000 celdas y un rank MPI por bloque.
El build es `LPJmL-6.0.6-balance-fix-20260912`; cada bloque conserva su propio
restart, logs, `lpjcheck.log` y control de checkpoints.

> **Interrupción y reanudación verificada 2026-09-22 20:48 America/Bogota:**
> no quedaban procesos del lanzador ni de LPJmL y el indicador superior seguía
> como `POTENTIAL_CHUNKS_RUNNING` desde las 15:24. El bloque
> `00000_07999` había guardado el checkpoint
> `1790108667908124560.lpj` después de imprimir hasta el año de spin-up 1482.
> Su SHA-256 (`80c0a282b424c4f5f6b9faae3eca2b8f2c69e40f4fa9fe4a2ee43fe39e71f52a`)
> coincide con el de `restart/checkpoint.lpj`; `controller.stderr.log` estaba
> vacío. La campaña se reanudó a las 20:47:44 locales desde ese checkpoint,
> sin repetir el spin-up anterior. El segmento
> `1790128064901329557` confirma que LPJmL abrió el restart; la primera
> comprobación posterior encontró un rank activo, ~99 % CPU, ~4.3 GiB RSS,
> ~25 GiB disponibles y cero swap. Aún no hay `exit_code=0` ni resultados
> aceptados para este bloque.

## Decisiones ejecutadas

- La fase candidata usa `landuse = "all_crops"`, `with_nitrogen = "unlim"`,
  `fertilizer_input = "auto"`, sin ganado ni manure.
- Solo se solicitan `grid`, `land_area`, `pft_harvestc`, `pft_harvestc2` y
  `maxthaw_depth`, además de las salidas CH4 de la rama methane-enabled. Los
  flujos de N de esta fase no se interpretan porque el N es ilimitado.
- El selector promedia `harvestc + harvestc2` en 1996--2005, lo convierte a
  `kcal m-2 yr-1` con la tabla de Franck y elige un CFT anual por celda.
- Se excluyen pasture/managed grassland y sugarcane. El mapa final se escribirá
  en 64 bandas con un solo CFT rainfed o irrigado por celda elegible.

## Evidencia de recursos

Los intentos con el conjunto completo de salidas de análisis terminaron con
`LPJmL exit 137` justo después de `Simulation begins`; quedaron en
`fr_genghis_potential_20260922` y `fr_genghis_potential_20260922_r4`. El
intento con salidas mínimas llegó a reservar aproximadamente 31 GiB en un
global; se detuvo antes de aceptar sus resultados. La pasada válida usa bloques
de 8.000 celdas: el primer rank observado reserva aproximadamente 4.3 GiB y
el cálculo se secuencia para evitar competir por memoria. La primera prueba de
bloques con `river_routing=true` dio `ERROR142` al reconstruir vecinos globales;
la campaña válida desactiva ríos y embalses solo en el ranking local y conserva
la evidencia de ese fallo.

## Validación del contrato CLM

El piloto `pilot_20260922T184445Z` generó:

- mapa: `map_test/genghis_khan_crop_only_2005.clm`;
- SHA-256: `244372fe680f73d7a1c17eafb9afcd506d5ec90e9161815c9ae66ea51bd7ee47`;
- manifiesto: `map_test/selection_manifest.json`;
- ganador de la celda: `irrigated temperate roots`.

`lpjcheck` aceptó el mapa contra un reinicio global A0 con `only_crops` y
`landuse_year_const=2005`. Las advertencias conservadas son las esperables del
conjunto estándar (mapa de suelo, año de primera cosecha y título de fertilizante);
el error inicial de bandas se corrigió dejando los 16 nombres CFT oficiales en
el metadato y no repitiéndolos cuatro veces.

## Próxima transición

Cuando todos los bloques candidatos terminen con `exit_code=0`, se ejecutará:

```bash
python build_capacity_landuse.py \
  --potential-root /home/dasan/exofarm-lpjml-runs/fr_genghis_potential_20260922_chunks_ch4/chunks/00000_07999 \
  --potential-root /home/dasan/exofarm-lpjml-runs/fr_genghis_potential_20260922_chunks_ch4/chunks/08000_15999 \
  --ncell 67420 \
  --output-dir /home/dasan/exofarm-lpjml-runs/fr_genghis_crop_only_20260922/map
```

El comando real incluirá los nueve roots de bloques. Después se validará el
mapa global con `lpjcheck` y se lanzará
`run_capacity_genghis_chunks.sh`. Ese runner repite una vez el spin-up
`with_methane=true`, activa `only_crops` para 2005 y guarda las salidas N y CH4
por bloques con checkpoints de 3600 s. La limitación de routing local queda
registrada para la interpretación; no se modifica ni se ejecuta VULCAN en esta
etapa.
