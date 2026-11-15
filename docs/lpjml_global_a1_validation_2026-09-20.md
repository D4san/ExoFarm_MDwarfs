# Validación de la campaña global A1 de LPJmL (2026-09-20)

## Alcance y procedencia

Este informe cierra la validación operativa de `global_a1_checkpoints_20260909`,
ejecutada en Ubuntu/WSL sobre el disco E: en
`/home/dasan/exofarm-lpjml-runs/global_a1_checkpoints_20260909`. La campaña
usó ocho ranks MPI, el build local
`LPJmL-6.0.6-balance-fix-20260912` y `fail_on_balance=true`. El spin-up
natural ya estaba aceptado y se reanudó desde checkpoints; no se repitió.

La fase A1 terminó el 2026-09-20 a las 16:40:38 UTC con `exit_code=0`.
`campaign_status.txt` pasó a `SIMULATIONS_COMPLETE_PENDING_VALIDATION` antes
de esta revisión. Después del cierre no quedaron procesos `mpirun`/`lpjml`.
El segmento final contiene los años 2004 y 2005 y el mensaje de terminación
normal de LPJmL para 67 420 celdas.

El último checkpoint periódico archivado corresponde al año 2003, de acuerdo
con el intervalo de guardado. El archivo
`a1_2005_n/checkpoints/1789917702303492589.lpj` y su `.sha256` tienen el mismo
SHA-256:

```text
f8d4a0d9bd25efc0ce5cb3f776e9501f205c1e1e1858af226d6599c40f497773
```

La ausencia de `a1_2005_n/restart/checkpoint.lpj` después de la terminación es
el cierre normal del lanzador; el checkpoint archivado y los productos finales
son la evidencia recuperable. Se conservaron 47 generaciones archivadas.

## Validación estructural y numérica

El validador reproducible es
[`validate_global_a1_outputs.py`](../Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction/validate_global_a1_outputs.py).
La validación produjo
`a1_2005_n/output/analysis/global_a1_validation.json` con resultado `PASS`:

- configuración: `firstyear=1901`, `outputyear=1996`, `lastyear=2005`,
  `nspinup=420`;
- cobertura temporal: diez años, 1996--2005;
- malla: 280 × 720; 67 420 celdas válidas según `grid.cellid`;
- `land_area` finita en las 67 420 celdas válidas; 67 370 tienen área positiva
  y 50 representan celdas válidas con área cero;
- las dimensiones temporales, las máscaras fuera de la malla válida y los
  valores finitos se comprobaron en los productos de salida;
- unidades de los flujos agrícolas: `gN m-2 yr-1`; `cellfrac_agr` se conserva
  como diagnóstico y no se multiplica otra vez durante la integración;
- se revisaron los NetCDF anuales y los diagnósticos `bnf_agr`, `n2_agr`,
  `ndepo_agr`, `nfert_agr`, `nleaching_agr`, `nmanure_agr` y `nuptake_agr`.

Los rangos válidos fueron finitos. Los mínimos negativos diminutos de algunos
flujos (`~10^-24`--`10^-26`) son redondeo numérico alrededor de cero y no
producen valores no físicos relevantes en la integración.

## Flujos integrados y comparación congelada

Se ejecutó, solo después de la validación, el analizador existente:

```text
python analyze_n_fluxes.py --output-dir <campaña>/a1_2005_n/output --coverage global
```

Sus salidas son `output/analysis/nitrogen_flux_summary.json` y
`output/analysis/nitrogen_flux_timeseries.csv`. El analizador integra `gN` por
área de celda y convierte a moléculas usando dos átomos de N para `N2O` y uno
para `NH3`.

| Magnitud | A1 agrícola = ΔF_agri medio 1996--2005 | ΔF_agri de referencia | Diferencia del componente agrícola | Equivalente TgN/año |
| --- | ---: | ---: | ---: | ---: |
| N2O (moléculas cm^-2 s^-1) | 7.697271226e8 | 7.200000000e8 | +4.9727123e7 (+6.91 %) | 5.7634 frente a 5.3911; +0.3723 |
| NH3 (moléculas cm^-2 s^-1) | 4.241070982e9 | 1.006000000e10 | −5.8189290e9 (−57.84 %; 42.16 % de la referencia) | 15.8778 frente a 37.6627; −21.7850 |

La referencia y sus conversiones proceden de
`reference_campaign_manifest.json`, que queda congelado dentro de la campaña.
Los valores A1 de la tabla son el componente agrícola `ΔF_agri` integrado sobre
la malla global. El control natural `A0` ya está validado en el informe
[`lpjml_global_a0_control_validation_2026-09-22.md`](lpjml_global_a0_control_validation_2026-09-22.md);
el flujo total del escenario A1 se construye como `F_A0 + ΔF_agri`. Por tanto,
N2O queda numéricamente próximo y algo por encima del incremento de referencia,
mientras que NH3 queda muy por debajo. La discrepancia de NH3 sigue siendo una
decisión abierta de calibración y alcance.

No se modificó ni se ejecutó VULCAN. Tampoco se creó todavía un forzamiento
atmosférico a partir de estos valores.

## Comparación de alcance con la literatura

La magnitud de A1 se puede contrastar con inventarios publicados, pero la
comparación es de orden de magnitud. La síntesis de FAO sitúa las emisiones
agrícolas globales de `N2O-N` alrededor de 3.5 TgN/año y separa las pérdidas de
amoníaco asociadas a fertilizante mineral y estiércol; sus límites de sistema
no son idénticos a los de esta salida de LPJmL. Bouwman et al. reportan para
el conjunto fertilizante--estiércol valores de `NH3-N` que pasan de unos 18 a
34 TgN/año entre 1970 y 1995, y una serie de `N2O-N` de aproximadamente 2.0 a
2.7 TgN/año en ese intervalo. Frente a esas referencias, el A1 de este estudio
(5.76 TgN/año de N2O y 15.88 TgN/año de NH3) conserva el orden de magnitud:
N2O queda por encima de la banda citada y NH3 queda cerca del extremo bajo.

Estas cifras no constituyen una validación independiente: cambian el año,
los factores de emisión, las categorías incluidas y la frontera espacial.
Además, von Bloh et al. describen y evalúan el ciclo de nitrógeno de LPJmL,
pero esa publicación documenta el modelo y sus procesos, no una identidad
numérica con la campaña A1. Las referencias usadas son [FAO, evaluación
global de emisiones agrícolas](https://www.fao.org/4/y2780e/y2780e01a.htm),
[Bouwman et al. 2006, inventarios globales de NH3 y N2O](https://pubmed.ncbi.nlm.nih.gov/16512200/)
y [von Bloh et al. 2018, ciclo de nitrógeno de LPJmL](https://gmd.copernicus.org/articles/11/2789/2018/).

## Advertencias y evidencia de ejecución

El inventario de los 49 segmentos A1 contiene:

```text
WARNING001  49
WARNING004  98
WARNING013  18296
WARNING024  98
WARNING034  6909
WARNING035  686
WARNING036  49
WARNING040  1
WARNING041  33
ERROR_CODES 0
```

`controller.stderr.log` quedó vacío. `WARNING013` es la advertencia recurrente
de normalización de fracciones de uso de suelo. En
`Agricultural_Fluxes_LPJmL/software/LPJmL/src/landuse/landuse.c`, LPJmL divide
las fracciones por `landfrac` y, cuando la suma supera uno, renormaliza antes
de continuar; la suma máxima observada antes de esa normalización fue
aproximadamente 2.350413. El aviso debe conservarse como salvedad de la
entrada de uso de suelo, pero la salida global validada permanece finita y la
ejecución no produjo errores de balance.

`WARNING041` corresponde a celdas sin masa natural o humedal disponible durante
la deforestación. Los demás avisos son diagnósticos de rangos/metadatos de
entradas. Ninguno cambió el código de salida ni introdujo valores no finitos.

## Estado y siguiente acción

La campaña A1 global queda **completada y validada para emisiones agrícolas de
stand**. Antes de acoplarla a la fotoquímica o afirmar un incremento causal,
hay que ejecutar/validar el control A0 natural emparejado, aplicar la misma
integración y documentar `A1-A0` por especie. La reproducción de la tabla de
capacidad de carga de Franck et al. sigue siendo una tarea separada.
