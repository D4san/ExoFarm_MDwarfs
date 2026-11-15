# Comparación de realizaciones A1 LIFE a 1 h

**Estado actual (2026-10-02):** por decisión del proyecto, esta realización
(seed 2125532119, tag NOISE2) es ahora el dataset/retrieval oficial A1-1 h de
la serie focal 1/10/100 h. La primera realización (seed 368516754) se conserva
como comparación de sensibilidad; esta promoción ocurrió después de revisar
ambos posteriores y, por tanto, es una selección post hoc. Ambas realizaciones
y sus productos permanecen disponibles; el índice canónico 8/8 no cambia.

**Lanzamiento:** 2026-10-01 20:47 COT (2026-10-02 01:47 UTC).  
**Cierre:** 2026-10-01 23:48:39 COT (2026-10-02 04:48:39 UTC),
`[retrieval_exit] 0`; MultiNest y el postproceso terminaron. Los productos se
cosecharon en el árbol aislado de esta repetición y el scratch quedó preservado.  
**Propósito:** comprobar si la mediana alta de N₂O en el A1 oficial de 1 h
(`log_N2O = −5.77`) persiste bajo otra realización o responde al ruido de ese
dataset.

## Diseño y preservación

La repetición usa una **nueva realización gaussiana independiente** sobre la
misma señal A1, con los mismos 31 centros/ancho de bin y las mismas
incertidumbres del dataset oficial de 1 h. El escalado de incertidumbre sigue
`sigma(1 h) = sigma(10 h) × sqrt(10)`. El master seed del generador es
`20261002`; la semilla de la realización registrada en el índice es
`2125532119`.

El dataset no se añade a la serie oficial ni al índice canónico 8/8. El
lanzador comprueba que la malla y `sigma` coincidan con el A1 oficial, que el
flujo observado sea distinto, y que la semilla no se repita. El hash del índice
canónico verificado al generar la entrada es
`3f037dc9450ebead70e871f44f5db3dcde7480d9d141411f7de3ea3bcdf5e27b`.

| Elemento | Ruta / valor |
| --- | --- |
| Dataset independiente | `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A1_1h_O2_fixedBlack1bar_noiseRepeat2.dat` |
| Índice aislado | `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/dataset_index_A1_1h_noiseRepeat2.json` |
| SHA-256 del dataset | `93fb65765101950063d5aa9a3dafae4df38273292cb0e3349e94b8a34516cfcc` |
| Lanzador | [`launch_proxima_a1_1h_noise_repeat_mpi.sh`](../Thermal_Emission_Spectroscopy/scripts/launch_proxima_a1_1h_noise_repeat_mpi.sh) |
| Tag del retrieval | `_O2_fixedBlack1bar_noxtol_MPI6_NOISE2` |
| Scratch Linux WSL | `/home/dasan/exofarm_proxima_a1_1h_noise_repeat2_20261001/retrieval` |
| Log | `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/proxima_A1_1h_O2_fixedBlack1bar_noxtol_MPI6_NOISE2.launch.log` |
| `mpiexec` observado | PID `1874` |
| Configuración | POSEIDON/MPICH, 6 ranks, `N_live=800`, `isochem`, O₂, superficie negra fija a 1 bar, `R=10000`, sin `x_tol` ni inflación de errores |
| Productos cosechados | `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/` |
| Resultado / posterior | `results/proxima_A1_1h_O2_fixedBlack1bar_noxtol_MPI6_NOISE2_results.txt`; `samples/proxima_A1_1h_O2_fixedBlack1bar_noxtol_MPI6_NOISE2_samples.txt` bajo el árbol anterior |

La serie oficial A1/A3 1/10/100 h, su dataset A1 de 1 h, los productos ya
cosechados, la matriz amplia 8/8 y sus entradas permanecen intactos. La
repetición usó un tag nuevo; el lanzador cosechó los productos tras confirmar
`exit_code=0` y conservó el scratch Linux.

## Validación y resultado

POSEIDON/MultiNest 3.10 terminó con 337.319 evaluaciones de likelihood, 800
live points y 15 parámetros. El resultado informa `ln Z = 867.68 ± 0.17`,
`χ² = 17.55`, 16 dof (`χ²_red = 1.10`) y `R_p_ref = 1.21 R_⊕`
(q16–q84: 1.172–1.254). Esta evidencia pertenece a este dataset y no se
compara con el `ln Z` oficial como factor de Bayes.

La validación encontró 7.334 muestras posteriores de 15 parámetros, 7.334
filas en `post_equal_weights`, 23.807 filas de evidencia, 800 puntos vivos y
800 puntos vivos físicos. Muestras, espectro (16.094 × 6), P–T (100 × 6),
perfil log-X (8 especies × 100 niveles × 6 columnas) y tablas numéricas
MultiNest examinadas son finitos, sin NaN/Inf. El cierre y la cosecha constan
en el log del run.

Percentiles q16/q50/q84 de las muestras de igual peso:

| `log10(VMR)` | Primera realización, ahora sensibilidad (seed 368516754) | Realización seleccionada actual (seed 2125532119) |
| --- | ---: | ---: |
| N₂O | −7.565 / −5.767 / −5.416 | −10.901 / −9.200 / −7.441 |
| NH₃ | −11.365 / −10.108 / −8.820 | −11.159 / −9.680 / −8.197 |
| O₂ | −4.984 / −3.141 / −1.285 | −4.863 / −3.064 / −1.284 |

En N₂O, la mediana de la realización seleccionada es 3.43 dex menor que en la
primera; los intervalos centrales del 68% apenas se solapan (~0.12 dex). Frente a los
promedios verticales efectivos A1 (`−6.734`) y A0 (`−6.884`), 93.4% y 91.6%
de las muestras repetidas quedan por debajo, respectivamente. Las distancias
mediana–verdad, escaladas por la semiamplitud q16–q84, son `z` descriptivos
condicionales de −1.43 (A1) y −1.34 (A0); ambas verdades quedan dentro del
intervalo central del 95%. No constituyen detección ni exclusión formal.

La realización altera marcadamente la inferencia de N₂O a 1 h, mientras que
NH₃/O₂ cambian mucho menos en sus medianas. Esto confirma sensibilidad al
ruido para este caso concreto. Solo hay dos realizaciones, así que no estiman
cobertura ni una distribución de sesgo. El análisis condiciona en isochem,
perfil P–T asumido y errores diagonales; `χ²_red` también depende de cada
dataset. Los `ln Z` de ambas realizaciones no son comparables como factor de
Bayes.

## Figura de comparación entre realizaciones

Se adaptó el generador de productos existente, manteniendo el estilo del atlas
Proxima. La figura compara las posteriores A1 de 1 h de ambas realizaciones
para N₂O y NH₃ con perfiles verticales VULCAN, referencias A0/A1 efectivas y
P–T recuperado frente al perfil de entrada. Los recuadros incluyen medianas,
intervalos q16–q84, distancias `z` descriptivas y métricas de ajuste propias
de cada dataset. El `ln Z` se etiqueta por realización y no se compara entre
ellas.

- PNG histórico de la comparación: `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A1_1h_noise_repeat_N2O_NH3_PT_proxima.png`
- PDF histórico de la comparación: `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A1_1h_noise_repeat_N2O_NH3_PT_proxima.pdf`
- Reproducción desde la raíz: `python Thermal_Emission_Spectroscopy/scripts/plot_proxima_retrieval_products.py --a1-1h-noise-repeat`

La figura anterior se conserva en esas rutas. La figura actualizada de esta
comparación es `retrieval_A1_1h_selected_official_vs_previous_N2O_NH3_PT_proxima.png/PDF`;
el atlas focal A1/A3 de 1/10/100 h también se regeneró con la realización
seleccionada.

## Actualización de la figura oficial (2026-10-02)

La figura oficial A1/A3 de 1/10/100 h se regeneró con la realización
seleccionada. La figura oficial anterior, basada en seed 368516754, se conserva
en su ruta original como antecedente. La comparación actualizada entre el seed
previo y el seleccionado es
retrieval_A1_1h_selected_official_vs_previous_N2O_NH3_PT_proxima.png/PDF;
se genera con plot_proxima_retrieval_products.py --a1-1h-noise-repeat. La
selección post hoc debe permanecer explícita en cualquier resumen científico.
