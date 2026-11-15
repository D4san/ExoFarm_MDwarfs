# Validación del control natural A0 de LPJmL (2026-09-22)

## Ejecución y recuperación

El control `a0_natural` de `global_a1_checkpoints_20260909` terminó con
`exit_code=0` el 2026-09-21 a las 08:54:45 UTC, usando ocho ranks, el build
`LPJmL-6.0.6-balance-fix-20260912` y el reinicio natural aceptado. El primer
lanzamiento alcanzó el año 1587 y fue interrumpido por el entorno WSL sin un
error de LPJmL; la ejecución se reanudó desde el checkpoint íntegro y conservó
la cobertura final. Se archivaron nueve generaciones. La última copia
periódica es `1789974065040377876.lpj`, cuyo SHA-256 coincide con el sidecar:

```text
673fa0d06c5a960e244661f154d207a87446eebc46ad82849557184771b5418b
```

El último segmento contiene los años 1996--2005 y el mensaje de salida normal.
`controller.stderr.log` está vacío. Los ocho segmentos de la reanudación solo
contienen `WARNING001`, `WARNING034`, `WARNING035` y `WARNING036`, que son los
diagnósticos de fracciones, lagos y metadatos ya presentes en las entradas.
Los tres segmentos históricos previos a la reanudación contienen además
`WARNING019`, producido antes de fijar `LPJROOT` en el lanzador; no aparece en
la ejecución reanudada.

## Validación de productos

El validador reproducible es
[`validate_global_a0_outputs.py`](../Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction/validate_global_a0_outputs.py).
Su informe JSON es
`a0_natural/output/analysis/global_a0_validation.json` y resultó `PASS`:

- malla `280 × 720` con 67 420 celdas válidas;
- `land_area` anual para 1996--2005 y 120 registros mensuales de cada flujo;
- 67 406 celdas válidas con área positiva y 14 con área cero;
- productos finitos en las celdas válidas, sin valores negativos integrados;
- unidades `m2` para `land_area` y `gN m-2 month-1` para los tres flujos;
- finitud y máscaras comprobadas antes de sumar los doce meses de cada año.

La integración suma `n2o_nit + n2o_denit` para N2O y usa
`n_volatilization` para el NH3 natural. Los flujos mensuales se multiplican por
el área terrestre anual y se convierten a masa de N, `TgN/año` y moléculas
`cm-2 s-1` mediante la misma esfera terrestre y los mismos átomos de N por
molécula usados en A1.

## Alcance terrestre de A0

Este A0 es un control de la **superficie terrestre** representada por LPJmL.
Incluye los procesos de nitrógeno natural que producen `n2o_nit`, `n2o_denit` y
`n_volatilization` bajo `landuse=no`, población, fertilizante y estiércol
desactivados. La corrida no contiene biogeoquímica oceánica ni intercambio
océano-atmósfera; tampoco integramos como categorías separadas fuentes de
relámpagos, combustión o emisiones marinas.

Esto permite aislar el componente agrícola sobre un fondo terrestre emparejado.
Para una frontera atmosférica absoluta de todo el planeta, el aporte oceánico y
las demás fuentes externas a estos productos tendrían que añadirse como un
componente independiente y mantenerse fijo entre A0 y A1.

## Resultado A0 y contraste con A1

| Magnitud | A0 natural medio 1996--2005 | BC A0 congelado | A0−BC | A1 agrícola = ΔF_agri medio | ΔF_agri de referencia |
| --- | ---: | ---: | ---: | ---: | ---: |
| N2O (moléculas cm-2 s-1) | 1.334471e9 | 1.580000e9 | −15.54 % | 7.697271e8 | 7.200000e8 |
| NH3 (moléculas cm-2 s-1) | 2.964787e9 | 2.940000e9 | +0.84 % | 4.241071e9 | 1.006000e10 |

En unidades de masa, A0 alcanza `9.9920 TgN/año` de N2O y `11.0996 TgN/año`
de NH3. La salida agrícola de A1, que representa `ΔF_agri`, conserva los
valores ya validados: `5.7634 TgN/año` de N2O y `15.8778 TgN/año` de NH3.
Por tanto, el componente agrícola medido por las salidas A1 queda en
`7.6973e8` moléculas `cm-2 s-1` para N2O y `4.2411e9` para NH3. N2O queda un
6.91 % por encima del incremento congelado; NH3 alcanza solo el 42.16 % del
incremento congelado.

Aplicando `F_A1,total = F_A0,natural + ΔF_agri`, la suma del fondo natural y el
componente agrícola produce `2.1042e9` moléculas `cm-2 s-1` de N2O (91.49 % del
BC A1 de `2.3e9`) y `7.2059e9` de NH3 (55.43 % del BC A1 de `1.3e10`). La
comparación es diagnóstica y conserva separadas las dos particiones; no
sustituye una calibración de la parametrización de volatilización de NH3 ni
autoriza aún un producto fotoquímico.

La corrida A0 completa el control natural solicitado y permite separar el
fondo natural del aporte agrícola. El siguiente trabajo es documentar la
discrepancia de NH3 con el incremento congelado y decidir si se requiere una
corrida A1 complementaria con salidas totales o una revisión de la conversión y
del anclaje de la frontera de NH3. VULCAN no se ejecutó.
