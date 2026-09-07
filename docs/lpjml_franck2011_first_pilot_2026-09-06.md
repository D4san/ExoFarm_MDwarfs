# Piloto LPJmL para Franck et al. (2011) y flujos agrícolas de N

**Fecha local:** 2026-09-06  
**Campaña aceptada:** `pilot_20260907T031220Z`  
**Clasificación:** prueba de interfaz de una celda; no es un resultado global

## Pregunta y alcance

La prueba comprueba que el repositorio puede ejecutar con entradas públicas una
reproducción metodológica moderna del cálculo de capacidad de carga de Franck
et al. (2011) y, en una rama físicamente separada, leer los flujos agrícolas de
`N2O` y `NH3` de LPJmL. No intenta reproducir todavía los valores globales de la
Tabla 3 ni genera un forzamiento atmosférico para VULCAN.

Se ejecutaron tres etapas sobre la celda LPJmL `27410`:

1. equilibrio natural y archivo de reinicio;
2. benchmark histórico `a1_2005_n`, con ciclo de N limitado, fertilizante y
   manure;
3. `potential_yield_unlimited_n`, con todos los cultivos y N no limitante, para
   validar las salidas requeridas por el método de capacidad de carga.

## Procedencia y configuración

- LPJmL `6.0.6`, commit
  `5af44a1ed023279a23c28d6dfe76945b97aaac57`.
- Entradas oficiales LPJmL 6.0.x de Zenodo, registro `19064225`.
- Archivo: `lpjml6-0-5_standard_input.tar.gz`, `37,763,601,476` bytes.
- MD5 verificado: `682d8b894d7983301313e9d60a49483b`.
- Extracción verificada: 76 archivos y `66,338,995,720` bytes.
- Clima moderno: GSWP3-W5E5; por tanto, esta es una reproducción metodológica,
  no una réplica bit a bit del LPJmL 3.x + CRU usado en 2011.
- Periodo de salida analizado: media anual 1996--2005.

El manifiesto persistente de los datos está en
[`input_dataset_manifest.json`](../Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction/input_dataset_manifest.json).
La configuración, el código de análisis y los comandos están en
[`workflows/franck2011_reproduction/`](../Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction/).

## Compatibilidad de metadatos

Cuatro JSON oficiales contienen caracteres Unicode en campos descriptivos.
LPJmL 6.0.6 usa `json-c` en modo estricto y rechazó inicialmente esos archivos.
El generador crea copias ASCII únicamente para la ejecución y convierte sus
rutas relativas a rutas absolutas hacia los binarios originales. El manifiesto
de campaña conserva SHA-256 del original y de cada copia. Los 76 archivos
extraídos no fueron modificados.

## Resultado de aceptación

`lpjcheck` confirmó que existen todas las entradas y que las tres
configuraciones son válidas. Las tres simulaciones terminaron con código 0 y
LPJmL informó `1 grid cells processed`.

| Producto | Dimensiones | Unidad | Comprobación |
| --- | --- | --- | --- |
| `land_area` | `(10, 1, 1)` | `m2` | finito |
| `cellfrac_agr` | `(10, 1, 1)` | adimensional | finito |
| `n2o_nit_agr` | `(10, 1, 1)` | `gN m-2 yr-1` | finito |
| `n2o_denit_agr` | `(10, 1, 1)` | `gN m-2 yr-1` | finito |
| `nh3_agr` | `(10, 1, 1)` | `gN m-2 yr-1` | finito |
| `pft_harvestc` potencial | `(10, 32, 1, 1)` | `gC m-2 yr-1` | finito, no nulo |
| `pft_harvestc2` potencial | `(10, 32, 1, 1)` | `gC m-2 yr-1` | finito, segunda cosecha presente |
| `maxthaw_depth` potencial | `(10, 1, 1)` | `mm` | finito |

El resumen local 1996--2005 de `a1_2005_n` integra la densidad sobre el área
terrestre de esa única celda:

- `N2O-N = n2o_nit_agr + n2o_denit_agr`:
  `2.314224699e-4 TgN yr-1` de media;
- `NH3-N = nh3_agr`: `5.273633905e-6 TgN yr-1` de media.

Estos valores solo demuestran que la extracción y la contabilidad de unidades
funcionan. No son emisiones planetarias ni pueden compararse con una estimación
global. Por esa razón, el analizador dejó deliberadamente vacíos los flujos en
`molecules cm-2 s-1`.

## Advertencias y límite científico

La ejecución conserva advertencias upstream sobre el mapa de tipos de suelo y
la extensión temporal de sowing dates, tillage y densidad ganadera. No impiden
aceptar una prueba de interfaz, pero deben revisarse antes de aceptar una
campaña global.

La primera prueba queda cerrada. Para reproducir los resultados publicados aún
faltan la corrida global, el posprocesamiento por bandas latitudinales, las
reservas de tierra por persona, la máscara `save forests`, la regla de segunda
cosecha y la comparación cuantitativa con la Tabla 3. Solo una salida global
aceptada podrá convertirse en flujos moleculares de `N2O` y `NH3` para VULCAN.

