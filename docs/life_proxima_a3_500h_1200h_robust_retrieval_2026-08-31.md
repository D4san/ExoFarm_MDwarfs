# Retrieval robusto de Proxima A3 a 500 h y 1200 h, 2026-08-31

## Pregunta y clasificación

Se relanzaron los retrievals de `A3` a `500 h` y `1200 h` para comprobar el
comportamiento de la configuración corregida cuando el ruido de LIFEsim clásico
se reduce. Son productos de **auditoría/piloto**: no amplían la matriz científica
canónica `Proxima A0--A3 x {10 h, 240 h}`, no sustituyen LIFEsimMC/PHRINGE y no
constituyen por sí solos una detección.

El objetivo de esta corrida es separar dos problemas que se habían mezclado en
los pilotos anteriores: el cálculo del dataset y la estabilidad del modelo de
retrieval. Se conservaron los productos antiguos y se usaron nombres de salida
con el sufijo `_robust_lifesim_direct`.

## Entorno y entradas

La ejecución se hizo en Ubuntu/WSL, en el entorno conda `POSEIDON`:

```text
conda root: /home/wsldasan/miniconda3
environment: /home/wsldasan/miniconda3/envs/POSEIDON
POSEIDON_input_data: /home/wsldasan/POSEIDON/inputs
PYSYN_CDBS: /home/wsldasan/POSEIDON/inputs/stellar_grids
```

Versiones relevantes ya verificadas en ese entorno:

```text
POSEIDON 1.4.0
LIFEsim 0.2.32
SpectRes 2.1.1 (fdannert/SpectRes)
```

Los datasets se calcularon llamando directamente a `LifeSceneClassic.observe`
para cada tiempo, no escalando una sigma de 10 h:

```bash
python make_life_datasets.py --campaign proxima --scenarios A3 --hours 500 1200 \
  --seed 20260831 --direct-lifesim \
  --name-suffix _robust_lifesim_direct \
  --index-output ../outputs/life_proxima_b_earthlike_v1/life_data/dataset_index_500_1200h_robust_lifesim_direct_audit.json
```

El índice de auditoría registra 31 bins, flujo planetario `F_p` en
`W m^-2 m^-1`, una semilla derivada distinta para cada tiempo y S/N mediano del
continuo de `332.02` a 500 h y `514.37` a 1200 h. Las entradas son:

- [`LIFE_proxima_A3_500h_robust_lifesim_direct.dat`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A3_500h_robust_lifesim_direct.dat);
- [`LIFE_proxima_A3_1200h_robust_lifesim_direct.dat`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A3_1200h_robust_lifesim_direct.dat);
- [`dataset_index_500_1200h_robust_lifesim_direct_audit.json`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/dataset_index_500_1200h_robust_lifesim_direct_audit.json).

## Configuración del retrieval

Se utilizó [`run_life_retrieval.py`](../Thermal_Emission_Spectroscopy/scripts/run_life_retrieval.py)
con emisión directa de POSEIDON:

- escenario `A3`, observable `Fp`, rango `3.8--19.0 um`, `R=2000`;
- perfil térmico `Madhu` y abundancias constantes con altura (`isochem`);
- inflación fraccional de errores `Piette20`, con parámetro libre `x_tol`;
- `surface=True` y 15 parámetros libres;
- `N_live=800` y `evidence_tol=0.5`;
- prior físico de `R_p_ref`, introducido en metros antes de la conversión interna
  de POSEIDON: `[0.8, 1.3]` veces el radio objetivo;
- abundancias libres entre `10^-12` y `10^-1`, presión superficial entre `0.1`
  y `10 bar`, y `x_tol` entre `0` y `0.3`.

Los retrievals se lanzaron con:

```bash
python run_life_retrieval.py --campaign proxima --scenario A3 --hours 500 \
  --n-live 800 \
  --dataset-file Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A3_500h_robust_lifesim_direct.dat \
  --output-tag _robust_lifesim_direct

python run_life_retrieval.py --campaign proxima --scenario A3 --hours 1200 \
  --n-live 800 \
  --dataset-file Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A3_1200h_robust_lifesim_direct.dat \
  --output-tag _robust_lifesim_direct
```

## Resultados directos

Los intervalos siguientes son las restricciones de `1 sigma` reportadas por
POSEIDON:

| Integración | `ln Z` | `chi^2_red` | `chi^2` (dof=16) | `R_p_ref` | `x_tol` | `log_N2O` | `log_NH3` |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 500 h | `901.17 +/- 0.22` | `2.07` | `33.13` | `1.23 (+0.01/-0.01) R_E` | `0.02 (+0.01/-0.00)` | `-5.43 (+0.26/-0.28)` | `-8.68 (+1.69/-2.11)` |
| 1200 h | `898.31 +/- 0.22` | `2.82` | `45.16` | `1.26 (+0.02/-0.02) R_E` | `0.03 (+0.01/-0.01)` | `-5.06 (+0.20/-0.23)` | `-8.79 (+1.76/-2.09)` |

MultiNest necesitó `505 676` evaluaciones de likelihood para 500 h y `453 552`
para 1200 h. Los archivos crudos reportan respectivamente
`ln(ev)=901.174160 +/- 0.224111` y `ln(ev)=898.308932 +/- 0.221254`.

La inspección de las muestras añade una salvedad de prior: `a1` concentra
probabilidad muy cerca de su límite superior `a1=2` en ambos runs (el cuantil
0.1 % superior es aproximadamente `1.998`). En 500 h MultiNest avisó durante
la exploración que un parámetro de modo se acercaba al borde del prior. El
resultado, por tanto, es robusto frente al colapso numérico del piloto viejo,
pero no es aún una prueba de insensibilidad a los priors; una inferencia final
debe repetir el análisis con un prior de `a1` ampliado y una prueba de
sensibilidad.

## Verificación de completitud

Cada corrida produjo el resumen de resultados, las muestras posteriores, el
espectro recuperado, los perfiles PT/químicos y los archivos crudos de
MultiNest. Las muestras tienen, excluyendo la cabecera, `10 107` filas para
500 h y `11 227` para 1200 h; no se encontraron cadenas `nan` o `inf` en esos
archivos.

Los resultados principales están en:

- [resultado A3--500 h](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/results/proxima_A3_500h_robust_lifesim_direct_proxima_A3_500h_robust_lifesim_direct_results.txt);
- [resultado A3--1200 h](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/results/proxima_A3_1200h_robust_lifesim_direct_proxima_A3_1200h_robust_lifesim_direct_results.txt);
- [muestras y archivos crudos](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/).

## Comparación con los pilotos anteriores

El retrieval viejo de 500 h (`N_live=200`) produjo `ln Z=893.18`,
`chi^2_red=1.59` y `R_p_ref=1.23 R_E`. Su dataset coincide byte a byte con el
dataset directo de 500 h, pero no es el mismo producto inferencial: el nuevo
run usa `N_live=800`, el sufijo separado y la implementación actual de
`Piette20`. Por eso se conservan ambos resultados y no se deben mezclar sus
posteriores.

El piloto viejo de 1200 h era numéricamente patológico:
`ln Z=-9 158 024.75`, `chi^2_red=1 144 880.01` y
`R_p_ref=2.1e-7 R_E`. El nuevo retrieval de 1200 h evita ese colapso: el radio
es físico, la evidencia es finita y el archivo posterior está completo. Esto
valida la estabilidad computacional de la configuración corregida, pero no
demuestra que 1200 h sea un régimen inferencial ideal: el `chi^2_red=2.82`
todavía indica tensión entre los datos simulados y el modelo paramétrico.

## Interpretación y límites

**Resultado directo:** la combinación de dataset directo de LIFEsim, prior de
radio físico, perfil `Madhu` y `Piette20` permite terminar ambos retrievals sin
el fallo numérico del piloto de 1200 h.

**Interpretación del proyecto:** 500 h y 1200 h son útiles como controles de
robustez y evidencia de auditoría, pero permanecen fuera de la matriz canónica.
El posterior usa abundancias isoquímicas, mientras la verdad VULCAN es vertical;
por tanto `log_N2O` y `log_NH3` son valores efectivos dependientes del modelo,
no una reconstrucción completa del perfil químico.

**Lo que no se puede concluir:** estos resultados usan una sola realización,
errores diagonales de LIFEsim clásico y ningún modelo comparativo con/sin
`N2O`/`NH3`. No sustituyen una campaña LIFEsimMC/PHRINGE con covarianza,
múltiples realizaciones y comparación de modelos, ni autorizan lenguaje de
detección.
