# Partición de N₂ y NH₃ en la campaña LPJmL (2026-09-22)

## N₂ agrícola

La campaña A1 conservó `a1_2005_n/output/n2_agr.nc`. Sus metadatos identifican
la variable `AN2_agr` como **pérdida de N a través de N₂ por desnitrificación en
rodales agrícolas**, con unidades `gN/m2/yr`. La integración sobre `land_area`,
excluyendo los valores de relleno NetCDF, da para 1996--2005:

| Magnitud | Media A1 agrícola |
| --- | ---: |
| N perdido como N₂ | `37.4887 TgN/año` |
| Flujo planetario equivalente | `5.0068e9 moléculas N₂ cm-2 s-1` |

El valor está expresado como masa de N. Si se quiere la masa de moléculas N₂,
hay que aplicar la razón molecular 28/14; para los balances de nitrógeno del
proyecto conservamos `TgN/año`. Este resultado es agrícola y procede de
desnitrificación; no representa todo el N₂ natural del planeta.

### Área que representa `n2_agr`

La configuración A1 activa `landuse: yes`, `landfrac_from_file: true` y el
archivo de uso de suelo de CFT (`cft_default_cft_aggregation_30min...`). LPJmL
reconstruye cada celda como una colección de *stands* con fracciones de área.
`cellfrac_agr` suma las fracciones de los stands que el código clasifica como
agrícolas. En LPJmL 6.0.6, `isagriculture(stand)` incluye `AGRICULTURE`,
`AGRICULTURE_GRASS`, `AGRICULTURE_TREE`, `OTHERS` y varios *set-aside*
gestionados. Por tanto, `n2_agr` representa el conjunto de rodales agrícolas
gestionados; su nombre no equivale automáticamente a “solo superficie de
cultivo anual cosechado”.

El acumulador de desnitrificación añade cada pérdida agrícola como
`N_denit * stand->frac`. Por eso los campos `n2_agr`, `n2o_denit_agr` y
`nh3_agr`, aunque se guardan en `gN/m2/yr`, ya están ponderados por la fracción
agrícola de la celda. Para obtener TgN/año se multiplican por `land_area`; no
se vuelve a multiplicar por `cellfrac_agr`. Esta última sirve para auditar el
área agrícola o para calcular una intensidad por m² agrícola, dividiendo el
flujo celular por `cellfrac_agr` cuando proceda.

Si la pregunta exige **solo cultivos agrícolas** y excluye pastos gestionados,
árboles agrícolas y *set-aside*, la corrida actual no tiene esa separación en
`n2_agr`. Hay dos rutas reproducibles: pedir en una corrida nueva `cftfrac`,
`cft_n2_emis` y `cft_n2o_denit` (que siguen cada CFT) o añadir una salida
específica que acumule únicamente el tipo de stand deseado. No se debe aplicar
`cellfrac_agr` como filtro adicional sobre `n2_agr`, porque duplicaría la
ponderación de área.

El control A0 no pidió `n2_emis`/`N2_EMIS` en su configuración de salidas. Por
eso la campaña actual no permite cuantificar el N₂ natural de suelo. Para ello
habría que añadir esa salida (y, si se quiere cerrar el presupuesto, salidas de
reservas minerales) a una corrida A0 específica.

## Qué significa NH₃

`nh3_agr.nc` está definido como **pérdida de N por volatilización de NH₃ en
rodales agrícolas**. Su media A1 es `15.8778 TgN/año`. Es el NH₃ que salió a la
atmósfera como volatilización; no es el total de nitrógeno amoniacal producido
ni una reserva de NH₃ que permanezca sin emitir.

En la misma campaña quedaron otros flujos diagnósticos medios (`TgN/año`):

| Flujo | Media |
| --- | ---: |
| Fertilizante `nfert_agr` | 83.3304 |
| Estiércol `nmanure_agr` | 17.8960 |
| Fijación biológica `bnf_agr` | 15.9366 |
| Deposición `ndepo_agr` | 12.6158 |
| Absorción `nuptake_agr` | 123.5450 |
| Lixiviación `nleaching_agr` | 24.2094 |
| N₂O agrícola | 5.7634 |
| N₂ agrícola | 37.4887 |
| NH₃ volatilizado | 15.8778 |

Estas magnitudes son flujos brutos y no forman por sí solas un presupuesto
cerrado: la absorción se recicla, hay cambios de reserva de suelo y faltan en
esta campaña salidas de `soilnh4`, `soilnitrate` y mineralización. Por tanto,
no se puede obtener el “NH₃ que quedó sin volatilizar” restando `nh3_agr` de
las entradas. Se necesita una corrida o salida ampliada con reservas de suelo y
un balance anual de entradas, transformaciones, pérdidas y cambios de stock.

## Implicación para ExoFarm

Para la frontera atmosférica, `n2_agr` y `nh3_agr` son pérdidas gaseosas
agrícolas separadas. El fondo A0 aporta las pérdidas terrestres naturales que
se hayan solicitado (`n2o_nit`, `n2o_denit`, `n_volatilization`); el océano y
otras fuentes externas siguen siendo componentes independientes.
