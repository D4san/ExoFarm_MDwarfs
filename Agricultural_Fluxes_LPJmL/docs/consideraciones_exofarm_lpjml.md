# Consideraciones para ExoFarm-LPJmL

## Proposito

Este documento define la ruta LPJmL. La idea central es usar LPJmL como capa
global de agroecosistemas: land use, cultivos, hidrologia, carbono y nitrogeno.
La salida que le interesa a ExoFarm sigue siendo un flujo de frontera para la
atmosfera, no una abundancia atmosferica.

## 1. Por que LPJmL cambia el enfoque

LPJmL es un modelo global grillado que representa ecosistemas naturales y
manejados dentro de una misma celda. Esto lo hace apropiado si la pregunta
ExoFarm se formula como:

```text
dada una tecnosfera agricola planetaria o regional,
que patron espacial de produccion, agua y perdidas de nitrogeno produce,
y que flujo atmosferico integrado resulta de ese patron
```

El costo es que LPJmL exige mas disciplina de configuracion: version del modelo,
inputs grillados, manejo agricola, outputs solicitados, area de celdas y
metadatos.

## 2. Version y ciclo de nitrogeno

Para ExoFarm no basta una corrida LPJmL de carbono/agua. Hay que usar una
version con ciclo de N activado. En la configuracion publica actual aparecen
controles como:

- `with_nitrogen`
- `fertilizer_input`
- `manure_input`
- `irrigation`
- `tillage_type`
- `residue_treatment`
- `landuse`

Los identificadores de salida relevantes en el codigo fuente incluyen:

- `N2O_DENIT`
- `N2O_NIT`
- `N2_EMIS`
- `N_VOLATILIZATION`
- `N2O_DENIT_AGR`
- `N2O_NIT_AGR`
- `NH3_AGR`
- `N2_AGR`
- `NFERT_AGR`
- `NMANURE_AGR`
- `NLEACHING_AGR`

Cuando tengamos una instalacion local, la lista autoritativa debe salir de:

```bash
./bin/lpjml -ofiles
```

No hay que confiar en nombres de salida copiados entre versiones sin verificar.

## 3. Que significa `NH3` en esta ruta

LPJmL reporta perdidas de nitrogeno como masa de N en procesos. Para ExoFarm,
`NH3_AGR` o `N_VOLATILIZATION` se deben tratar como flujo de N asociado a
volatilizacion de amoniaco, no como una fraccion de mezcla atmosferica.

La traduccion correcta es:

```text
masa de N por area por tiempo
        -> moles de N
        -> moles de molecula portadora
        -> moleculas cm^-2 s^-1
```

Para `NH3`, 1 molecula tiene 1 atomo de N. Para `N2O`, 1 molecula tiene 2
atomos de N. El script de conversion de este modulo usa esa diferencia.

## 4. Escenarios ExoFarm con LPJmL

Una matriz LPJmL inicial puede organizarse asi:

| Dimension | Valores iniciales |
| --- | --- |
| Area agricola | pre-agricola, Tierra actual, alta, extrema |
| Cultivo/arquetipo | cereales templados, arroz, maiz/tropical, pulses, grassland |
| Agua | rainfed, irrigacion limitada, irrigacion potencial, pulsos humedos |
| N sintetico | bajo, actual, alto, auto-fertilizacion como envolvente |
| Manure/livestock | no, actual, intensivo |
| Residuos/tillage | remocion, retorno, no-till/reduced tillage si la version lo soporta |
| Bioquimica incompleta | `epsilon = 0`, `0.1`, `0.5`, `1` como post-proceso |

El filtro de consistencia sigue siendo obligatorio:

- no mezclar "pre-agricola" con fertilizante sintetico alto;
- no usar `auto` fertilization como escenario realista sin marcarlo como
  envolvente;
- no aumentar area agricola extrema sin revisar agua disponible;
- no interpretar `epsilon = 1` como planeta terrestre normal.

## 5. Diagnosticos minimos

Para que una corrida LPJmL pueda alimentar VULCAN/PhotoChem, guardar al menos:

- version exacta de LPJmL y hash si viene de Git;
- configuracion activa;
- fuente de inputs climaticos, land use, fertilizer, manure y grid;
- area de celda o archivo `grid`;
- unidades y timestep de cada output;
- `N2O_DENIT_AGR`, `N2O_NIT_AGR`, `NH3_AGR`, `N2_AGR`;
- `NFERT_AGR`, `NMANURE_AGR`, `NLEACHING_AGR`, `NUPTAKE_AGR`;
- metadatos de salida (`output_metafile` o equivalente), para evitar leer
  binarios sin unidades.

## 6. Primera corrida recomendada

La primera prueba no deberia ser una matriz enorme. Mejor:

1. Instalar o clonar LPJmL fuera de los scripts ExoFarm.
2. Confirmar dependencias: `json-c`, `netcdf`, `udunits`, y MPI solo si se va a
   correr en paralelo.
3. Ejecutar `lpjml -h`, `lpjml -ofiles` y `lpjcheck`.
4. Usar una configuracion historica pequena o una subregion para validar lectura
   de inputs.
5. Activar ciclo de N y pedir outputs nitrogenados con metadatos.
6. Leer outputs con `lpjmlkit` o una rutina propia que respete metadatos.
7. Convertir los flujos nitrogenados a `molecules cm^-2 s^-1`.
8. Solo despues mapear a A0/A1/A2/A3.

## 7. Pregunta clave para el paper

La pregunta LPJmL para ExoFarm no es:

```text
cuanto N2O o NH3 puedo imponer arbitrariamente
```

Sino:

```text
que perdidas atmosfericas de N emergen de una biosfera agricola planetaria
con land use, agua, fertilizante, manure y productividad autoconsistentes
```

Luego VULCAN decide si esos flujos sostienen abundancias detectables bajo una
estrella tipo Sol o una enana M.

## Fuentes principales leidas

- Schaphoff et al. 2018, LPJmL4 Part 1: model description.
- Schaphoff et al. 2018, LPJmL4 Part 2: model evaluation.
- von Bloh et al. 2018, LPJmL5 nitrogen cycle.
- Lutz et al. 2019, LPJmL5-tillage.
- Wirth et al. 2024, biological nitrogen fixation in LPJmL 5.7.9.
- PIK LPJmL model page.
- PIK-LPJmL GitHub repository and configuration files.
- lpjmlkit documentation for reading LPJmL outputs and metadata.
