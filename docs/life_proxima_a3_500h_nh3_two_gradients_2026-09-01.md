# Retrieval Proxima A3 a 500 h con perfil vertical de NH3, 2026-09-01

## Pregunta y clasificación

Se probó si el retrieval de emisión directa a `500 h` mejora al permitir que
`NH3` varíe verticalmente. El perfil usado por POSEIDON fue `two-gradients`;
`H2O`, `CO2`, `CH4`, `O3` y `N2O` permanecieron isquímicos. Es un diagnóstico
de parametrización y queda como **auditoría/piloto excluida**: no amplía la
matriz canónica `Proxima A0--A3 x {10 h, 240 h}`, no sustituye al retrieval
isquímico robusto de 500 h y no constituye una detección.

**Resultado directo:** la corrida terminó normalmente y produjo posteriores
completos. El modelo vertical no mejoró el ajuste reportado frente al modelo
isquímico bajo los priors usados en esta prueba.

**Interpretación del proyecto:** el posterior sí permite una caída de `NH3`
con la altura, pero la capa alta está débilmente informada. La evidencia no
debe leerse como una comparación definitiva de modelos: cambia la
parametrización y también el volumen de prior de `NH3`.

## Entorno y entradas

La ejecución se hizo en Ubuntu/WSL, dentro del entorno conda `POSEIDON`:

```text
conda root: /home/wsldasan/miniconda3
environment: /home/wsldasan/miniconda3/envs/POSEIDON
POSEIDON_input_data: /home/wsldasan/POSEIDON/inputs
PYSYN_CDBS: /home/wsldasan/POSEIDON/inputs/stellar_grids
POSEIDON: 1.4.0
LIFEsim: 0.2.32
SpectRes: 2.1.1
```

Se reutilizó el dataset directo de LIFEsim ya validado, sin regenerarlo ni
escalar su sigma:

- [`LIFE_proxima_A3_500h_robust_lifesim_direct.dat`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A3_500h_robust_lifesim_direct.dat)

La orden reproducible fue:

```bash
python run_life_retrieval.py --campaign proxima --scenario A3 --hours 500 \
  --n-live 1000 \
  --dataset-file Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A3_500h_robust_lifesim_direct.dat \
  --output-tag _nh3twograd \
  --x-profile two-gradients \
  --vertical-gradient-species NH3
```

El primer intento usó un tag descriptivo más largo. POSEIDON concatena el
nombre del modelo y el de la corrida; el prefijo resultante fue truncado por
la rutina Fortran de MultiNest y la ejecución terminó antes de muestrear. Se
conservó ese archivo parcial de cero bytes y se relanzó con el tag corto
`_nh3twograd`; no se mezclaron archivos entre ambas corridas.

## Configuración del modelo

- observable directo `F_p`, `3.8--19.0 um`, `R=2000`;
- perfil térmico `Madhu`;
- `X_profile="two-gradients"`, `X_dim=1`;
- `species_vert_gradient=["NH3"]`;
- inflación fraccional `Piette20`, con `x_tol` entre `0` y `0.3`;
- `surface=True`, `N_live=1000`, `evidence_tol=0.5`;
- 18 parámetros libres: los 15 del retrieval isquímico más
  `log_NH3_high`, `log_NH3_mid`, `log_P_NH3_mid` y `log_NH3_deep` en lugar de
  una única abundancia `log_NH3`;
- prior de la capa alta de NH3: `[-25, -3]` dex, para no imponer el límite
  artificial de `10^-12` sobre el perfil VULCAN A3, cuya abundancia cae hasta
  aproximadamente `10^-20` en la atmósfera alta;
- priors de `log_NH3_mid` y `log_NH3_deep`: `[-12, -1]` dex;
- prior de `log_P_NH3_mid`: `[-5, 0]` en `log10(bar)`;
- el prior de `R_p_ref` se introdujo en metros antes de la conversión interna
  de POSEIDON, como en el retrieval robusto de referencia.

El perfil químico de comparación es el producto VULCAN
[`Proxima_b_A3_Extreme_chem.txt`](../Transmission_Spectroscopy/profiles/Proxima_b_A3_Extreme_chem.txt).

## Resultado del retrieval

Los valores siguientes son las restricciones de `1 sigma` escritas por
POSEIDON:

| Parámetro | Resultado |
| --- | ---: |
| `ln Z` | `895.86 +/- 0.17` |
| `chi^2_red` | `3.15` |
| `chi^2` (`dof=13`) | `40.94` |
| `R_p_ref` | `1.22 (+0.03/-0.02) R_E` |
| `x_tol` | `0.05 (+0.01/-0.01)` |
| `log_N2O` | `-6.31 (+0.36/-0.42)` |
| `log_NH3_high` | `-14.28 (+7.03/-6.96)` |
| `log_NH3_mid` | `-9.03 (+2.43/-1.98)` |
| `log_P_NH3_mid` | `-2.44 (+1.65/-1.67)` |
| `log_NH3_deep` | `-8.80 (+2.79/-2.10)` |

MultiNest terminó con `428 414` evaluaciones de likelihood y una evidencia
cruda `ln(ev)=895.857855 +/- 0.174979`. POSEIDON escribió `16 001` muestras
posteriores ponderadas, además del espectro recuperado, el perfil PT, el
perfil químico recuperado y los archivos crudos.

## Comparación con el retrieval isquímico de 500 h

La referencia es el retrieval robusto de 500 h con el mismo dataset directo,
PT `Madhu`, `Piette20` y abundancias `isochem`:

| Modelo | `N_params` | `ln Z` | `chi^2_red` | `chi^2` | `R_p_ref` |
| --- | ---: | ---: | ---: | ---: | ---: |
| isochem | 15 | `901.17 +/- 0.22` | `2.07` | `33.13` | `1.23 R_E` |
| NH3 `two-gradients` | 18 | `895.86 +/- 0.17` | `3.15` | `40.94` | `1.22 R_E` |

La diferencia nominal es `Delta ln Z = -5.31` y el `chi^2` reportado aumenta
en `7.81`, pese a los tres parámetros adicionales. **Resultado directo:**
esta corrida concreta no aporta evidencia a favor de reemplazar el modelo
isquímico. **Salvedad metodológica:** la comparación de evidencias incorpora
priors distintos, en particular la extensión de `log_NH3_high` y el nuevo
prior de la presión de transición; por ello no se presenta como una prueba
final de selección de perfil.

## Qué recupera el perfil vertical

La tabla resume la mediana y el intervalo central del `68 %` del bloque
`NH3` exportado por POSEIDON, comparados con el perfil VULCAN de entrada. Las
abundancias son `log10(X_NH3)`.

| Presión [bar] | VULCAN | Posterior mediana | Posterior `-1 sigma` | Posterior `+1 sigma` |
| ---: | ---: | ---: | ---: | ---: |
| `1` | `-8.20` | `-8.81` | `-10.20` | `-7.50` |
| `1e-1` | `-8.33` | `-8.94` | `-10.48` | `-7.69` |
| `3e-2` | `-9.24` | `-9.17` | `-10.78` | `-7.55` |
| `1e-2` | `-10.66` | `-9.33` | `-11.20` | `-7.40` |
| `1e-3` | `-13.75` | `-9.83` | `-12.75` | `-7.12` |
| `1e-5` | `-20.34` | `-12.78` | `-18.75` | `-7.03` |
| `1e-7` | `-21.29` | `-14.60` | `-21.10` | `-7.68` |

**Interpretación:** el posterior reproduce la dirección de la caída y coloca
la transición cerca de `P_mid ~ 10^-2.4 bar`, pero la banda superior es amplia
y su mediana permanece por encima de la depleción extrema del VULCAN. Esto es
compatible con que el dataset de una sola realización y el modelo térmico aún
absorban parte de la estructura química; no es una reconstrucción validada del
perfil vertical.

## Productos

- [resultado POSEIDON](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/results/proxima_A3_500h_nh3twograd_proxima_A3_500h_nh3twograd_results.txt);
- [muestras posteriores](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/samples/proxima_A3_500h_nh3twograd_proxima_A3_500h_nh3twograd_samples.txt);
- [perfil químico recuperado](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/samples/proxima_A3_500h_nh3twograd_proxima_A3_500h_nh3twograd_log_X_retrieved.txt);
- [espectro recuperado](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/samples/proxima_A3_500h_nh3twograd_proxima_A3_500h_nh3twograd_spectrum_retrieved.txt);
- [archivos crudos de MultiNest](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/MultiNest_raw/).

Todos estos productos usan LIFEsim clásico con sigma diagonal y una sola
realización de ruido. La inferencia definitiva requiere la rama
LIFEsimMC/PHRINGE, covarianza instrumental, varias realizaciones y
comparaciones controladas de modelos con y sin las moléculas objetivo.
