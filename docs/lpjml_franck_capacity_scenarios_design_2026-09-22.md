# Diseño de escenarios de capacidad agrícola inspirados en Franck et al. (2011)

**Fecha:** 2026-09-22  
**Estado:** `FR-genghis-khan-crop-only` es la primera rama autorizada para
implementación; `FR-save-forests` queda como segunda rama. La campaña global de
capacidad está activa en
`/home/dasan/exofarm-lpjml-runs/fr_genghis_potential_20260922_chunks_ch4` con
bloques de 8.000 celdas, un rank por bloque y methane-enabled. Dos intentos
anteriores con todas las salidas de análisis terminaron con `exit 137` al
asignar memoria; una primera prueba por bloques con routing global dio
`ERROR142`; ambos registros se conservan como evidencia de recursos. Los
escenarios canónicos A0--A3 siguen intactos.

## Pregunta

El artículo de Franck et al. (2011), *Harvesting the sun: New estimations of
the maximum population of planet Earth*, usa LPJmL para construir una envolvente
de capacidad agrícola. Queremos saber si esa lógica puede generar escenarios
hipotéticos de ExoFarm y, después, flujos de `N2O` y `NH3` para la interfaz
fotoquímica.

La referencia primaria es Franck et al. (2011), *Ecological Modelling* 222,
2019--2026, DOI
[`10.1016/j.ecolmodel.2011.03.030`](https://doi.org/10.1016/j.ecolmodel.2011.03.030).
El artículo calcula capacidad alimentaria; no calcula emisiones de `N2O` o
`NH3`. Esa segunda parte será una extensión de ExoFarm y debe conservar sus
propios supuestos de fertilización y manejo.

## Qué hizo realmente el artículo

### Rama de referencia

- LPJmL se ejecutó en una rejilla global de 0.5° con rendimientos medios de
  1996--2005, usando clima CRU de la versión histórica del modelo.
- El caso de comprobación parte de la distribución de cultivos de 2005 y
  produce una capacidad de aproximadamente 11.4 mil millones de personas.
- Para cada celda se considera el cultivo con mayor rendimiento energético
  (`kcal m-2 yr-1`) entre los cultivos elegibles. Se respetan la profundidad
  mínima de deshielo de 1 m y la disponibilidad de agua de riego limitada por
  descarga fluvial.
- Solo se cuenta el órgano cosechado como alimento. En el caso de pastura, el
  artículo convierte una décima parte de las calorías de la hierba ingerida por
  animales en calorías humanas.

### Escenarios hipotéticos

1. **Genghis Khan:** toda la tierra productiva elegible se asigna al cultivo
   energético ganador de cada celda. La versión extrema no reserva superficie
   para ciudades, recreación u otros usos.
2. **Save forests:** repite la lógica de selección, pero excluye las celdas
   cuya vegetación natural potencial está dominada por bosques tropicales o
   boreales perennifolios.
3. **Burger:** usa pastura como fuente de alimento animal; es una rama distinta
   y no es necesaria para el primer escenario atmosférico de ExoFarm.

Cada escenario tiene además versiones “soft”. Estas versiones no fijan un
porcentaje universal de reserva: reservan `B = 750` o `1500 m2/persona` para
usos no agrícolas dentro de cada banda latitudinal de 10°. Como el área
reservada depende de la población calculada, la capacidad se obtiene con una
ecuación de cierre por banda, no cambiando una sola opción de LPJmL.

## Qué tenemos ya en el repositorio

El flujo de
[`workflows/franck2011_reproduction/`](../Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction/)
ya separa dos ramas:

- `a1_2005_n`: uso de suelo histórico, nitrógeno limitado, fertilizante y
  manure. Es la base de nuestro A1 actual y de los flujos agrícolas auditados.
- `potential_yield_unlimited_n`: `landuse = "all_crops"`, nitrógeno no
  limitante y fertilización automática. La campaña global de selección produce
  solo `grid`, `land_area`, `pft_harvestc`, `pft_harvestc2` y `maxthaw_depth`;
  esa reducción evita reservar memoria para flujos N que no se interpretan en
  esta etapa.

En el código LPJmL, `all_crops` añade una fracción mínima (`tinyfrac`) para
todos los cultivos en cada suelo válido. No significa “elige el mejor cultivo”
ni equivale todavía al mapa de Genghis Khan. La selección del ganador debe
hacerse como postproceso con la tabla energética de Franck y luego convertirse
en un mapa de uso de suelo que LPJmL pueda leer.

## Configuración propuesta para ExoFarm

La rama debe mantenerse separada de la matriz canónica actual:

```text
A0       fondo natural terrestre
A1       Tierra actual, uso de suelo de 2005 y manejo observado
A2       perturbación ExoFarm 30B de la matriz vigente
A3       envolvente extrema 15x de la matriz vigente

FR-genghis-khan-crop-only  toda la tierra elegible + cultivo anual ganador,
                           sin pasture, ganado ni manure
FR-save-forests            mismo mapa crop-only, excluyendo la máscara forestal
FR-soft750                 variante futura + 750 m2/persona no agrícola
FR-soft1500                variante futura + 1500 m2/persona no agrícola
```

Si se decide que `A1` y `A2` deben adoptar esta lógica, esa será una revisión
explícita de la matriz y obligará a regenerar los perfiles fotoquímicos. No se
deben cambiar esas etiquetas silenciosamente, porque hoy `A1` significa
benchmark actual y `A2` significa una perturbación moderada definida por
`alpha_NH3 = 3.50` y `alpha_N2O = 2.55`.

### Etapa 1: mapa de cultivos óptimos

1. Ejecutar la rama potencial con todos los CFT y guardar rendimientos de la
   primera y segunda cosecha.
2. Convertir cada rendimiento de carbono cosechado a energía usando
   `crop_energy_table.csv` y la relación de LPJmL `C = 0.45 * biomasa seca`.
3. Aplicar las restricciones del artículo: suelo válido, deshielo mínimo,
   riego limitado y conjunto de CFT compatible con la tabla de 2011.
4. Elegir el CFT de máximo rendimiento energético por celda y guardar también
   el ganador, el rendimiento, el área elegible y las cosechas utilizadas.
5. Para `FR-save-forests`, aplicar una máscara de vegetación natural potencial
   antes de construir el mapa. Esta máscara todavía no existe como producto
   aceptado en el repositorio y requiere una derivación auditable.

### Etapa 2: mapa de uso de suelo LPJmL

El ganador por celda se materializa con `build_capacity_landuse.py`, que
escribe `genghis_khan_crop_only_2005.clm` y `selection_manifest.json`. La
validación piloto con `lpjcheck` aceptó el encabezado de 64 bandas después de
corregir el metadato `map` a sus 16 nombres CFT; LPJmL expande internamente las
cuatro familias de riego. El mapa final debe ser un archivo `landuse`
compatible con LPJmL 6.0.6, preferiblemente NetCDF/CLM con las mismas bandas
CFT, fracciones rainfed/irrigated y metadatos del conjunto oficial. El mapa debe
conservar:

- fracciones que sumen uno solo sobre el área elegible;
- superficie no cultivada explícita en las versiones soft/save-forests;
- sistema de riego y disponibilidad de agua documentados;
- checksum del archivo y un manifiesto que identifique el CFT ganador por
  celda.

En la configuración de LPJmL, la ruta conservadora es usar `landuse = "yes"`
con el archivo sintético y `fix_landuse` desde el año en que se quiera congelar
el patrón. `landuse = "only_crops"` se usará para el mapa constante de
fracciones exclusivamente agrícolas, pero normaliza las fracciones de cultivo
internamente. Ya pasó `lpjcheck` en una configuración piloto y queda pendiente
la aceptación de una corrida global. `landuse = "all_crops"` queda reservado para obtener la
tabla de rendimientos candidatos; no es el mapa final.

El área reservada de 750/1500 m² por persona no puede codificarse de forma
fiel como una fracción fija antes de conocer la población. La implementación
fiel es un postproceso iterativo por banda de 10°: se calcula la población
alimentable, se descuenta `B` por persona y se vuelve a evaluar la capacidad.
Una fracción fija sería una variante simplificada propia de ExoFarm y tendría
que recibir otro nombre.

### Etapa 3: flujos nitrogenados

El artículo no prescribe una política de fertilización que podamos reutilizar
directamente para `N2O`/`NH3`. Para cada mapa de capacidad se requiere una
segunda corrida con ciclo de nitrógeno:

- rama central: `with_nitrogen = "lim"`, fertilizante y manure explícitos;
- rama de envolvente: `fertilizer_input = "auto"`, marcada como límite de
  productividad y no como agricultura terrestre observada;
- misma configuración de agua y riego que la usada para construir el mapa de
  cultivos;
- salidas `n2o_nit_agr`, `n2o_denit_agr`, `nh3_agr`, `n2_agr`, `cellfrac_agr`,
  `land_area` y diagnósticos de entradas de N.

Después se aplicará, si procede, la sensibilidad ya prevista para la
desnitrificación incompleta:

```text
N2O_N(epsilon) = n2o_nit_agr + n2o_denit_agr + epsilon*n2_agr
N2_N(epsilon)  = (1-epsilon)*n2_agr
```

Para la primera rama crop-only se fija además:

- excluir `Pasture` de la tabla de candidatos y del mapa final;
- `grazing = "none"` y `grazing_others = "none"`;
- `manure_input = false` y `prescribe_lsuha = false`;
- mantener fertilización sintética explícita en la rama central;
- reservar `fertilizer_input = "auto"` para una envolvente separada.

El resultado se integrará primero como masa de N y después se convertirá a
`TgN/año` y `molecules cm-2 s-1`. El artículo aporta la geometría de uso de
suelo y productividad; la magnitud de las emisiones será un resultado de la
configuración nitrogenada de ExoFarm.

### Etapa 4: CH4 como rama acoplada

CH4 no puede recuperarse como un postproceso de la campaña actual: A0/A1 y la
rama potencial se generaron con `with_methane = false`. Para el escenario
crop-only se activará `with_methane = true` en una campaña nueva y se pedirán
las salidas mensuales `ch4_agr`, `ch4_rice_em`, `ch4_grassland`,
`ch4_emissions_wet`, `ch4_emissions`, `ch4_oxidation`, `ch4_sink`,
`ch4_litter`, `ch4_ebullition` y `ch4_plant_gas`.

La ausencia de ganado elimina la ruta ganadera y el manure, pero no implica
CH4 agrícola nulo: arroz inundado, residuos, suelos húmedos y humedales pueden
seguir emitiendo. `ch4_agr` y `ch4_rice_em` se reportarán separados de los
humedales naturales y del CH4 total. El piloto methane-enabled completó la
interfaz y mostró las salidas mensuales esperadas. La ruta conservadora ya
quedó fijada: `run_capacity_genghis_chunks.sh` repetirá un spin-up
methane-enabled y después ejecutará el mapa crop-only en bloques con
checkpoints de 3600 s. La red de ríos y embalses se desactiva en cada bloque
local porque su vecino es global; el manifiesto debe mantener esta limitación.
El reinicio natural A0 sin metano no se reutiliza como estado de la campaña
final.

## Decisión recomendada

Mantener A0--A3 como la matriz atmosférica canónica y desarrollar primero
`FR-genghis-khan-crop-only`, seguido por `FR-save-forests`, como ramas de
capacidad agrícola. Así
separamos:

- el benchmark terrestre observado;
- la envolvente biogeofísica inspirada en Franck;
- el supuesto adicional de fertilización que convierte productividad en flujo
  de N.

El prototipo de una celda ya verificó la selección energética, la exclusión de
ganado, la salida CH4 y el contrato CLM. La campaña global de candidatos es el
siguiente paso; cuando finalice, se construirá el mapa mundial, se ejecutará
`lpjcheck` sobre la configuración final y se lanzará el spin-up methane-enabled.
No se debe lanzar VULCAN hasta congelar ese manifiesto y decidir el tratamiento
de NH3.

## Fuentes y productos relacionados

- Franck et al. (2011), DOI
  [`10.1016/j.ecolmodel.2011.03.030`](https://doi.org/10.1016/j.ecolmodel.2011.03.030).
- [`README de la reproducción moderna`](../Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction/README.md).
- [`consideraciones_exofarm_lpjml.md`](../Agricultural_Fluxes_LPJmL/docs/consideraciones_exofarm_lpjml.md).
- [`project_resume.md`](project_resume.md), para el estado operativo A0/A1 y el
  puente pendiente hacia VULCAN.
