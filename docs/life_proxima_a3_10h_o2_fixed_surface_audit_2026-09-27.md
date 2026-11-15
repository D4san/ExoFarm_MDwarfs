# Registro de ejecución: Proxima LIFE A3 corregido a 10 h (2026-09-27)

## Pregunta y alcance

Se inició un retrieval A3 de 10 h para compararlo de manera controlada con la
auditoría corregida A3 de 100 h. La matriz canónica A0--A3 × {10 h, 240 h}
permanece intacta: esta nueva corrida es una auditoría adicional, separada de
8/8. El retrieval A3 de 10 h ya existente usa otra interfaz/configuración y no
es sustituto de esta corrida emparejada.

## Dataset y configuración

Dataset clásico LIFE de 31 bins:
`Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A3_10h.dat`,
SHA-256 `46a026504b9b9521fa29407a501169b9d3cfc433de40a91b8ade86d7767abb5b`.
Ruido diagonal y una realización.

| Opción | Valor |
| --- | --- |
| escenario/tiempo | Proxima A3, 10 h |
| `X_profile` | `isochem` |
| especies | H2O, CO2, CH4, O2, O3, N2O, NH3; N2 de fondo |
| superficie | negra explícita fija a 1 bar (`surface=True`, `log_P_surf=0`) |
| errores | `error_inflation=none`; sin `x_tol` |
| resolución de malla POSEIDON | `R=10000` |
| muestreo | `N_live=800`, `evidence_tol=0.5` |

La validación de forward/configuración terminó con salida cero antes del
lanzamiento. Tras llevar el forward verdadero a los 31 bins observados, obtuvo
RMS `0.07963 sigma` y máximo `0.2545 sigma`. POSEIDON confirmó dataset, priors,
superficie y especies; MultiNest fue omitido en este paso de validación.

## Lanzamiento original

Comando de retrieval:

```bash
python -u run_life_retrieval.py \
  --campaign proxima --scenario A3 --hours 10 --n-live 800 \
  --error-inflation none --surface-pressure-mode fixed-black \
  --include-o2 --output-tag _O2_fixedBlack1bar_noxtol --R 10000
```

La corrida se lanzó en Ubuntu/WSL con PID `30640`. El lanzador
[`launch_proxima_a3_10h_o2_fixed_surface.sh`](../Thermal_Emission_Spectroscopy/scripts/launch_proxima_a3_10h_o2_fixed_surface.sh)
mantiene viva la sesión Ubuntu mientras espera el proceso, evita duplicados y
registra el código de salida.

- Log: [`proxima_A3_10h_O2_fixedBlack1bar_noxtol.launch.log`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/proxima_A3_10h_O2_fixedBlack1bar_noxtol.launch.log)
- PID: [`proxima_A3_10h_O2_fixedBlack1bar_noxtol.pid`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/proxima_A3_10h_O2_fixedBlack1bar_noxtol.pid)
- Retrieval corregido de 100 h para contraste: [informe](life_proxima_a3_100h_o2_fixed_surface_audit_2026-09-23.md)

Un intento inicial del lanzador terminó antes de iniciar Python por un error de
formato en el registro; un segundo proceso no persistió al cerrarse la sesión
Ubuntu. Se verificó que ambos intentos dejaron cero archivos MultiNest y
ningún proceso activo. El PID `30640` fue el único lanzamiento que ejecutó
MultiNest; su log y el código de salida final quedaron preservados.

## Recuperación de productos y resultados (2026-09-28)

**Hecho observado.** El log llega a `Sampling finished. Exiting MultiNest` y
registra `ln(ev)=890.96651762313104 ± 0.20853756729145093`, 1,201,886
evaluaciones y después `[process_exit] PID=30640 exit_code=1`. El error de
salida ocurre en el posprocesamiento: POSEIDON Analyzer solicita
`...-post_equal_weights.dat`, mientras la muestra cruda existente termina en
`...-post_equal_weights.d`. El nombre contiene el tag completo duplicado por
el tag duplicado. La inspección del código confirma por qué: el runner ponía
el mismo tag en `model_name` y en el argumento explícito `retrieval_name`, y
POSEIDON concatena ambos (`model_name + '_' + retrieval_name`) cuando recibe
ese argumento. Los basenames crudos de 10 h y 100 h miden exactamente 100
caracteres; el de 10 h se corta en `.d` y el de 100 h termina sin extensión,
lo que apunta a truncamiento del basename del writer. No se encontró una
colisión o sobrescritura entre ambos retrievals: tags, datasets, muestras y
archivos de resultados son distintos.

**Recuperación aplicada.**
[`postprocess_existing_proxima_a3_10h_o2.py`](../Thermal_Emission_Spectroscopy/scripts/postprocess_existing_proxima_a3_10h_o2.py)
comprobó la muestra cruda de 6,972 × 16 y su SHA-256
`385df34856eca87968f6bdcb7cf945cf63d2cf10f3b03b4f0f07c5caf8201442`. Conservó
el original `.d` y creó la copia `.dat` solo tras verificar que aún faltaba;
la copia es idéntica byte por byte. También comprobó el hash del dataset de
10 h (`46a026504b9b9521fa29407a501169b9d3cfc433de40a91b8ade86d7767abb5b`).
Luego POSEIDON reconstruyó los productos posteriores desde esas muestras; no
se volvió a ejecutar MultiNest ni su likelihood. La reconstrucción sí calcula
espectros forward para los resúmenes predictivos. Manifiesto:
[`proxima_A3_10h_O2_fixedBlack1bar_noxtol_..._postprocess_manifest.json`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/results/proxima_A3_10h_O2_fixedBlack1bar_noxtol_proxima_A3_10h_O2_fixedBlack1bar_noxtol_postprocess_manifest.json).

Los ficheros de posterior tienen 6,972 × 15 columnas y pasan validaciones de
finitud y parámetros, incluyendo `log_P_surf=0`. También se validaron el
espectro recuperado (6 columnas), P--T (100 × 6) y log-X (800 filas numéricas
para las ocho especies). El resultado del mejor ajuste es `chi²=20.43`,
`chi²_red=1.28` (16 dof). Los cuantiles posteriores son:

| Caso corregido | `R_p_ref` [R_⊕], mediana [q16, q84] | `log_N2O`, mediana [q16, q84] | `log_NH3`, mediana [q16, q84] | `log_O2`, mediana [q16, q84] | `ln Z` | `chi²_red` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 h | 1.2269 [1.2083, 1.2455] | −6.0598 [−6.2186, −5.9237] | −8.6841 [−10.8134, −7.8345] | −3.1956 [−5.0271, −1.3192] | 890.97 ± 0.21 | 1.28 |
| 100 h | 1.2202 [1.2142, 1.2266] | −6.1476 [−6.2040, −6.0927] | −8.2578 [−8.6586, −8.0569] | −3.3095 [−5.0952, −1.4248] | 884.33 ± 0.24 | 4.94 |

La comparación usa las posteriores corregidas `isochem`, O2 y superficie negra
fija a 1 bar. Los conjuntos son realizaciones independientes de ruido diagonal
en sus propios 31 bins; por ello no interpretamos la diferencia de `ln Z`
como evidencia relativa ni comparamos residuos normalizados entre conjuntos.
El rebin y los residuos se calcularon por separado contra el espectro mediano y
los bins de cada tiempo. A 10 h, RMS del residuo mediano `0.914 sigma`, cero
bins sobre `3 sigma`; a 100 h, `1.635 sigma`, tres bins sobre `3 sigma`.

Las referencias efectivas derivadas de los perfiles VULCAN son
`log_N2O(A0)=-6.884325`, `log_NH3(A0)=-9.950526`,
`log_N2O(A3)=-6.014062` y `log_NH3(A3)=-8.231504`. Con
`z=(mediana−A0 efectiva)/sigma68`, las distancias descriptivas son:

| Tiempo | `z_N2O` | `z_NH3` | sigma68 N2O [dex] | sigma68 NH3 [dex] |
| --- | ---: | ---: | ---: | ---: |
| 10 h | +5.59 | +0.85 | 0.147 | 1.489 |
| 100 h | +13.24 | +5.63 | 0.056 | 0.301 |

**Interpretación del proyecto.** A 10 h la posterior de NH3 sigue incluyendo
un intervalo muy amplio y su centro está a solo `0.85 sigma68` de A0 efectiva;
este retrieval no separa bien el NH3 del baseline. A 100 h ambas posteriores
son más estrechas y se alejan de A0 efectiva, pero el ajuste empeora mucho
(`chi²_red=4.94`). Esa tensión importa: el retrieval usa abundancias constantes
con altura y la atmósfera simulada tiene perfiles VULCAN verticales. Por tanto,
los z son distancias condicionales descriptivas, no significancias de detección.
Un retrieval a 100 h no queda validado como científicamente superior por su
posterior más estrecha; tampoco se puede elegir 10 h frente a 100 h usando sus
`ln Z`.

La figura de posteriores y residuos por tiempo fue inspeccionada visualmente:
[PNG](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A3_10_vs_100h_o2_fixed_surface_proxima.png)
([PDF](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A3_10_vs_100h_o2_fixed_surface_proxima.pdf)).
El análisis reproducible está en
[`plot_proxima_a3_o2_fixed_surface_10_100h.py`](../Thermal_Emission_Spectroscopy/scripts/plot_proxima_a3_o2_fixed_surface_10_100h.py),
con [resumen JSON](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/retrieval_A3_10_vs_100h_o2_fixed_surface_proxima_summary.json)
y [residuos CSV](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/retrieval_A3_10_vs_100h_o2_fixed_surface_proxima_residuals.csv).
La auditoría permanece separada de la matriz canónica 8/8. Para una afirmación
de distinción se requieren sensibilidad a perfil vertical, comparación
marginalizada con/sin especies y varias realizaciones/covarianza instrumental.

### Perfil térmico recuperado frente a VULCAN (2026-09-29)

Se compararon los resúmenes P--T de POSEIDON para 10 y 100 h con el perfil
VULCAN A3 de entrada registrado en el manifiesto de `life_proxima_b_earthlike_v1`.
El checksum MD5 del manifiesto coincide con el texto normalizado a LF; la copia
Windows usa CRLF. Las posteriores usan el perfil flexible Madhu de seis
parámetros; el archivo exportado contiene mediana y bandas marginales
punto-a-punto de 1σ y 2σ. La referencia VULCAN se interpoló linealmente en
temperatura frente a `log10(P)` sobre los 97 niveles comunes entre
`5e-8` y `1 bar`.

| Tiempo | RMS de `T_mediana − T_VULCAN` | Mediana de `|ΔT|` | Máximo `|ΔT|` | Niveles con VULCAN dentro de bandas 1σ / 2σ |
| --- | ---: | ---: | ---: | ---: |
| 10 h | 32.71 K | 14.80 K | 59.37 K | 29.9% / 54.6% |
| 100 h | 60.36 K | 39.46 K | 99.26 K | 5.2% / 9.3% |

La anchura mediana de la banda marginal punto-a-punto de 68% disminuye de
43.40 K (10 h) a 20.61 K (100 h), mientras el RMS respecto a VULCAN casi se
duplica. La posterior se hace más precisa en cada nivel y al mismo tiempo
queda menos centrada en el perfil fuente.

La mediana recuperada de 100 h se aleja más de la referencia, particularmente
en la atmósfera alta; su intervalo posterior más estrecho queda centrado en un
perfil térmico menos compatible con el VULCAN de entrada. Los porcentajes son
un chequeo descriptivo por nivel de las bandas marginales: no representan una
región creíble conjunta ni una probabilidad formal de cobertura. Junto con
`chi²_red=4.94`, el contraste apunta a tensión de adecuación del modelo/datos a
100 h; por sí solo no identifica si domina la parametrización P--T, la
abundancia isochem, sus degeneraciones o la realización diagonal de ruido.

La figura inspeccionada muestra perfiles recuperados, bandas marginales y
`T_mediana − T_VULCAN` por presión:
[PNG](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A3_recovered_PT_10_vs_100h_proxima.png)
([PDF](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A3_recovered_PT_10_vs_100h_proxima.pdf)).
Se reproduce con
[`plot_proxima_a3_retrieved_pt_comparison.py`](../Thermal_Emission_Spectroscopy/scripts/plot_proxima_a3_retrieved_pt_comparison.py);
el resumen numérico está en
[`retrieval_A3_recovered_PT_10_vs_100h_proxima_summary.json`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/retrieval_A3_recovered_PT_10_vs_100h_proxima_summary.json).

El monitor programado anterior continúa cancelado; no se creó una nueva
automatización para esta corrida.

**Prevención.** Se corrigió `run_life_retrieval.py` para pasar
`retrieval_name=None` cuando el nombre del modelo ya contiene el tag completo.
POSEIDON usa entonces una sola copia del nombre como raíz MultiNest. El cambio
solo afecta nuevos lanzamientos; no renombra ni altera los ocho productos
canónicos ni los outputs de auditoría recuperados.
