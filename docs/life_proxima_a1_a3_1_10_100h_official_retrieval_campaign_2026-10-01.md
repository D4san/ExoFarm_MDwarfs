# Campaña oficial de retrievals LIFE Proxima A1/A3 a 1, 10 y 100 h

**Fecha de decisión y lanzamiento:** 2026-10-01 (COT; cierre y figura
verificados a las 18:48 COT).  
**Estado:** A1 y A3 de 1 h cerraron MultiNest con `[retrieval_exit] 0`; los
productos de ambos se recuperaron del scratch y pasaron validación numérica.
La figura focal oficial A1/A3 de 1/10/100 h ya está generada e inspeccionada.
Los retrievals previos de 10 y 100 h también están incluidos y validados.  
**Alcance:** esta es la serie focal vigente. Los demás retrievals LIFE quedan
como legacy para esta pregunta y se preservan; no se borran datos ni productos.

## Actualización vigente (2026-10-02): A1 de 1 h

Por decisión del proyecto, el dataset A1 de 1 h con la realización
independiente pasa a ser la entrada oficial de la serie focal A1/A3 1/10/100 h.
El dataset y retrieval anteriores de A1 (seed 368516754, tag
OFFICIAL1h) se conservan íntegros como comparación de sensibilidad; no se
reemplazaron archivos. A3-1 h y los casos de 10/100 h no cambian. El índice
revisado de la serie focal es
[dataset_index_A1_A3_1h_official_revision_20261002.json](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/dataset_index_A1_A3_1h_official_revision_20261002.json);
el índice amplio canónico 8/8 permanece intacto.

El archivo seleccionado es
LIFE_proxima_A1_1h_O2_fixedBlack1bar_noiseRepeat2.dat (31 bins, seed
2125532119; master seed 20261002). Mantiene exactamente los centros, anchos y
sigmas del primer dataset A1 de 1 h, pero tiene una nueva extracción gaussiana
por bin. Se generó a partir de la sigma validada de LIFE clásico escalada como
sigma(1 h)=sigma(10 h)*sqrt(10); no fue una observación directa nueva de
LIFEsim. El retrieval POSEIDON MPI6 asociado cerró con exit 0 (PID mpiexec
1874): 337319 evaluaciones, 7334 muestras de igual peso, 23807 filas de
evidencia; todos los productos examinados son finitos.

Para esta entrada oficial, los valores son ln Z=867.68±0.17,
chi²red=1.10 (16 dof), R_p_ref=1.21 R_earth [q16,q84]=[1.172,1.254],
log_N2O=-9.200 (+1.759/-1.701), log_NH3=-9.680 (+1.483/-1.479) y
log_O2=-3.064 (+1.780/-1.799). La realización anterior tuvo una mediana
log_N2O=-5.767; la diferencia de 3.43 dex demuestra sensibilidad a esta
realización concreta. Como la selección del nuevo seed se hizo después de
inspeccionar ambos posteriores, debe tratarse como una decisión post hoc; no
es una selección ciega o preregistrada. Para estimar robustez poblacional
frente al ruido se requieren más realizaciones, no escoger la posterior más
conveniente. Los dos ln Z pertenecen a datasets distintos y no se comparan
como factor de Bayes.

La figura oficial actualizada usa el retrieval seleccionado:
[PNG](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima.png)
/
[PDF](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima.pdf).
La figura oficial previa, construida con seed 368516754, se conserva como
archivo histórico en su ruta anterior. La comparación de ambas realizaciones
está en
[retrieval_A1_1h_selected_official_vs_previous_N2O_NH3_PT_proxima.png](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A1_1h_selected_official_vs_previous_N2O_NH3_PT_proxima.png).
La sección de abajo registra la configuración inicial del 2026-10-01; si
describe otra elección de A1-1 h, prevalece esta actualización fechada
2026-10-02.

## Decisión y pregunta

La comparación oficial usa únicamente A1 y A3 a 1, 10 y 100 h. A0 efectiva se
mantiene como referencia de abundancia/perfil para describir las posteriores;
no se convierte por ello en un retrieval adicional de esta serie. Las figuras
de auditoría que incluyen 240 h quedan como evidencia histórica. La matriz
amplia de ocho datasets A0--A3 × {10 h, 240 h}, su índice y sus archivos se
conservan intactos como archivo de referencia, fuera del contraste focal
actual.

La interpretación será condicional a una realización gaussiana por dataset,
ruido fotónico LIFE diagonal y abundancias recuperadas isochem frente a perfiles
verticales VULCAN. Las distancias a A0 son descriptivas, no detecciones
formales; `ln Z` se informa por dataset y no como factor de Bayes entre tiempos
o realizaciones distintas.

## Configuración inferencial común

| Componente | Configuración |
| --- | --- |
| Forward observable | Flujo planetario `Fp`, 31 bins clásicos LIFE de Proxima |
| Retrieval | POSEIDON, emisión directa, `X_profile=isochem`, PT Madhu |
| Especies | H2O, CO2, CH4, O2, O3, N2O y NH3 |
| Muestreo | MultiNest, `N_live=800` |
| Errores | `error_inflation=none`; `x_tol` ausente; sigma diagonal |
| Superficie | Negra explícita y fija a 1 bar, `log_P_surf=0` |
| Resolución | `R=10000` |
| Paralelismo de 1 h | MPICH del entorno conda `POSEIDON`, seis ranks por escenario; una hebra BLAS por rank |

Priors activos en el runner [run_life_retrieval.py](../Thermal_Emission_Spectroscopy/scripts/run_life_retrieval.py):

| Parámetros | Prior |
| --- | --- |
| `a1`, `a2` | uniforme `[0.02, 2]` |
| `log_P1`, `log_P2` | uniforme `[-6, 1]` |
| `log_P3` | uniforme `[-2, 1]` |
| `T_ref` | uniforme `[150, 400] K` |
| `R_p_ref` | uniforme `[0.8, 1.3] × R_nominal` |
| `log10(VMR)` de H2O, CO2, CH4, O3, N2O, NH3 | uniforme `[-12, -1]` |
| `log10(VMR)` de O2 | uniforme `[-6, log10(0.5)]` |
| `log_P_surf` | fijo en `0` (`1 bar`); no tiene anchura libre |

## Entradas de 1 h

No había entradas ni lanzamientos previos de 1 h. Se generaron a partir de los
forward guardados y las incertidumbres fotónicas de referencia a 10 h, usando
la regla ya validada en el generador del proyecto:

```text
sigma(1 h) = sigma(10 h) * sqrt(10)
```

La señal se mantiene y se inyecta una realización normal independiente por
escenario. Es el escalado clásico de ruido de LIFEsim; el entorno POSEIDON no
tiene instalado el módulo Python `lifesim`, por lo que no se invocó una nueva
observación directa del simulador para 1 h. El método, semillas y 31 bins
quedan explícitos para reproducibilidad.

| Escenario | Dataset | Semilla de realización | Bins | S/N mediana de continuo |
| --- | --- | ---: | ---: | ---: |
| A1 | `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A1_1h_O2_fixedBlack1bar_official.dat` | `368516754` | 31 | 14.85 |
| A3 | `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A3_1h_O2_fixedBlack1bar_official.dat` | `1376328125` | 31 | 14.85 |

Semilla maestra `20261001`; índice aislado
[`dataset_index_A1_A3_1h_official.json`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/dataset_index_A1_A3_1h_official.json).
Cada archivo se validó con 31 filas × 4 columnas, datos finitos, anchos de bin
y sigma positivos. El SHA-256 del índice canónico antes y después fue idéntico:
`3f037dc9450ebead70e871f44f5db3dcde7480d9d141411f7de3ea3bcdf5e27b`.

Los 10 h A1/A3 reutilizan sus datasets de la matriz amplia; los 100 h usan
realizaciones independientes ya existentes (semillas A1 `460512527`, A3
`129315834`). Estos datasets son parte de la serie focal temporal a partir de
la decisión actual, aunque siguen fuera de la matriz amplia A0--A3 × {10 h,
240 h}.

## Runs MPI6 de 1 h

Lanzador reproducible:
[`launch_proxima_a1_a3_1h_official_mpi.sh`](../Thermal_Emission_Spectroscopy/scripts/launch_proxima_a1_a3_1h_official_mpi.sh).
Los outputs de MultiNest se escriben primero en filesystem Linux de WSL y el
lanzador los cosecha al árbol POSEIDON del proyecto solo después de `exit 0`;
el scratch se conserva para auditoría/recuperación. Los logs durables y PID
files viven en `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/`.

| Run | PID `mpiexec` | Scratch | Estado final verificado 2026-10-01 (COT) |
| --- | ---: | --- | --- |
| A1 | `3595` | `/home/dasan/exofarm_proxima_a1_a3_1h_official_20261001/A1/retrieval` | Cerrado, `[retrieval_exit] 0`; 22,161 replacements y 633,896 muestras. Última aceptación registrada `0.034960` en el checkpoint de 22,150 replacements. PID y ranks ausentes en la consulta posterior. |
| A3 | `3632` | `/home/dasan/exofarm_proxima_a1_a3_1h_official_20261001/A3/retrieval` | Cerrado, `[retrieval_exit] 0`; 22,068 replacements y 435,197 muestras. Última aceptación registrada `0.050708` en el checkpoint de 22,050 replacements. PID y ranks ausentes en la consulta posterior. |

La cosecha automática de ambos runs abortó después del muestreo porque el
wrapper buscaba `MultiNest_raw`, `results` y `samples` directamente bajo
`$RUN_DIR`; POSEIDON los había escrito bajo
`$RUN_DIR/POSEIDON_output/proxima_b_earthlike/retrievals/`. Los scratch de
ambos escenarios permanecen intactos. Se recuperaron sin sobrescritura los
13 productos por escenario y se corrigió el lanzador para buscar esa ruta
anidada en ejecuciones futuras; no se repitió ningún retrieval. La inspección
real de procesos en Ubuntu/WSL confirmó que ambos PID y sus ranks ya no estaban
activos. Muestras, espectros, perfiles P--T/log-X, resultados y archivos
MultiNest están presentes y finitos; los perfiles P--T tienen forma `100×6`,
los espectros `16094×6` y las muestras tienen 15 columnas. El índice canónico
8/8 permanece intacto.

## Resultados finales y lectura

Los resúmenes de abajo proceden de los archivos de resultados finales y de los
percentiles 16/50/84 de las muestras de igual peso. `R_p_ref` está en radios
terrestres; abundancias en `log10(VMR)`. Cada corrida tiene 16 grados de
libertad. `ln Z` se registra por dataset y no debe compararse entre tiempos o
escenarios como factor de Bayes.

| Escenario | Tiempo | `ln Z ± σ` | `χ²_red` | `R_p_ref` mediana [q16, q84] (`R_⊕`) | `log_N2O` mediana (+/−) | `log_NH3` mediana (+/−) | `log_O2` mediana (+/−) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A1 | 1 h | 867.68 ± 0.17 | 1.10 | 1.210 [1.172, 1.254] | −9.20 (+1.76/−1.70) | −9.68 (+1.48/−1.48) | −3.06 (+1.78/−1.80) |
| A3 | 1 h | 866.37 ± 0.16 | 1.66 | 1.1639 [1.1467, 1.1911] | −8.71 (+2.07/−2.10) | −9.75 (+1.44/−1.47) | −3.14 (+1.81/−1.80) |
| A1 | 10 h | 889.38 ± 0.21 | 1.55 | 1.2096 [1.1906, 1.2299] | −9.52 (+1.64/−1.60) | −10.08 (+1.27/−1.25) | −3.14 (+1.84/−1.91) |
| A3 | 10 h | 890.97 ± 0.21 | 1.28 | 1.2269 [1.2083, 1.2455] | −6.06 (+0.14/−0.16) | −8.68 (+0.85/−2.13) | −3.20 (+1.88/−1.83) |
| A1 | 100 h | 899.58 ± 0.24 | 3.18 | 1.2117 [1.2063, 1.2178] | −7.13 (+0.18/−0.31) | −10.66 (+0.95/−0.90) | −3.41 (+1.84/−1.66) |
| A3 | 100 h | 884.33 ± 0.24 | 4.94 | 1.2202 [1.2142, 1.2266] | −6.15 (+0.05/−0.06) | −8.26 (+0.20/−0.40) | −3.31 (+1.88/−1.79) |

La fila A1--1 h muestra la realización actualmente seleccionada (seed
`2125532119`), que sustituyó en la serie focal a la primera realización
(seed `368516754`; `χ²_red=1.93`, `log_N2O` mediana `−5.77`), preservada como
sensibilidad. La selección fue posterior a inspeccionar ambas posteriores y es
post hoc; el [informe de la repetición independiente](life_proxima_a1_1h_independent_noise_repeat_2026-10-02.md)
registra ambas salidas y la comparación completa.

Los datos de 1 h dejan N2O y NH3 amplias; al pasar a 10/100 h algunas
posteriores se estrechan, pero las medianas no evolucionan de forma uniforme
con el tiempo. Cada duración y escenario usa su propia realización, y a 100 h
el `χ²_red` sube a 3.18 (A1) y 4.94 (A3). Por ello el estrechamiento marginal
no basta para afirmar que la molécula se recupera ni que A3 se distingue
formalmente de A0: la inferencia sigue condicionada al perfil de abundancia
isochem frente a la química vertical VULCAN, a la P--T, a una sola realización
de ruido diagonal y al ajuste espectral. Los valores `z` de la figura son
distancias descriptivas frente a A0 efectiva, no significancias de detección.

## Figura oficial (seis especies, revisión visual 2026-10-03)

Se adaptó el generador existente
[`plot_proxima_retrieval_products.py`](../Thermal_Emission_Spectroscopy/scripts/plot_proxima_retrieval_products.py)
con la bandera `--official-a1-a3-times`; la figura de auditoría 10/100/240 h
conserva su ruta y contenido históricos. La figura focal mantiene una fila por
1, 10 y 100 h y muestra H2O, CO2, CH4, O3, N2O y NH3, junto con P--T. O2
continúa incluido en los retrievals; se omite únicamente su columna para dar
más espacio a las seis especies mostradas. La composición se ajustó a una
anchura exportada de aproximadamente 7.28 in para una figura de ancho
completo que abarca ambas columnas. A1 usa verde, A3 rosa y A0 efectiva verde
oscuro punteado. Cada encabezado de especie indica una sola vez el valor
logarítmico de VMR de A0; las filas conservan la línea
vertical de referencia. Las marginales y sus barras asimétricas q16–q84
aparecen en las tres exposiciones. Los perfiles verticales de abundancia VULCAN
de A1 y A3 se repiten en las tres filas para compararlos junto al posterior
isochem de cada tiempo; son perfiles de entrada, no perfiles moleculares
recuperados por el retrieval. El P--T posterior con bandas 68/95% aparece en
cada fila y el P--T VULCAN de entrada solo en la primera. La leyenda global se
limita a la codificación molecular; las bandas posteriores y la línea VULCAN
discontinua se explican localmente en la columna P--T. Esa columna no lleva
recuadros de ajuste. Los valores de `χ²_red` y `ln Z` por dataset permanecen
en la tabla de resultados anterior.

Las tres variantes se exportan como una página de 7.287 × 5.232 in; cada PDF y
SVG es vectorial y cada PNG mide 2187 × 1569 px a 300 dpi. Los elementos
tipográficos visibles tienen al menos 6 pt, conforme a la guía gráfica de
[AAS Journals](https://journals.aas.org/graphics-guide/).

### Ajuste final de la figura (2026-10-03)

Cada panel muestra, por color de escenario, `q50=...; z=...` debajo del área de
datos. `q50` es la mediana posterior de `log10(VMR)`; el z firmado se define
como `z_(s|A0)^desc = [q50_s - log10(VMR_A0,eff)]/σ68_s`, donde
`σ68_s = (q84_s - q16_s)/2`. Una sola ecuación, sin caja, define el z en la
misma línea visual que la leyenda. A0 aparece una vez por especie. Este
desplazamiento está condicionado al modelo isochem, al perfil P--T y a la
realización de ruido; se expresa en unidades de la semianchura central del 68%
de la posterior. Es descriptivo y no equivale a una significancia de detección
ni a evidencia de separación formal.

Los histogramas usan `density=True`: el área de cada marginal es uno y la
densidad se expresa por dex de `log10(VMR)`. Para que las formas sean legibles,
cada panel ajusta automáticamente su límite vertical; las alturas de densidad
no deben compararse entre moléculas ni entre tiempos. Separadores horizontales
distinguen las filas, y las anotaciones `q50`/`z` quedan bajo cada fila con el
eje x próximo a la última.

Se guardan tres variantes, construidas con los mismos retrievals y estilo. Por
decisión del usuario del 2026-10-03, V2 queda promovida como la figura oficial
y el comando estándar la genera bajo el nombre base:

1. **V1, prior completo (alternativa preservada):** todos los paneles usan
   `log10(VMR)=[−12,−1]`. Los perfiles que salen de ese rango quedan
   recortados visualmente.
2. **V2, oficial — perfiles + posteriores:** los límites por especie se calculan con
   muestras posteriores y perfiles VULCAN de las tres filas. Después se
   recortan al dominio del prior `[-12,-1]`; por tanto, nunca se muestra una
   cola por debajo de −12. Las líneas grises discontinuas señalan los bordes
   del prior cuando están dentro de la ventana.
3. **V3, solo posteriores:** los límites se calculan exclusivamente con las
   muestras posteriores agrupadas entre A1/A3 y 1/10/100 h. Los perfiles
   VULCAN siguen dibujados, pero no determinan el encuadre y pueden quedar
   recortados. También se aplica el tope `[-12,-1]`.

Las tres exportaciones tienen título `Proxima b LIFE retrievals: A1 and A3`.
La V2 oficial está promovida a `Thermal_Emission_Spectroscopy/final_products/figures/`
y disponible en PNG, PDF vectorial y SVG vectorial:
[V2 oficial PNG](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima.png),
[PDF](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima.pdf),
[SVG](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima.svg). La misma base permanece en la ruta de campaña como salida reproducible; [V1 prior completo PNG](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima_full_prior_xlim.png),
[PDF](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima_full_prior_xlim.pdf),
[SVG](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima_full_prior_xlim.svg); [V3
posterior-only](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima_posterior_xlim.png),
[PDF](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima_posterior_xlim.pdf),
[SVG](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima_posterior_xlim.svg). El alias de V2 `_dynamic_xlim` se mantiene por compatibilidad.

La inspección visual final de las tres variantes confirmó las tres filas, seis
paneles moleculares, perfiles verticales VULCAN por tiempo, A0 y barras
asimétricas. Los resultados `q50=...` y `z=...` quedan debajo de cada panel;
una ecuación matemática única y sin marco define z sin repetir A0 ni explicar
`σ68` en un recuadro. Los histogramas tienen área unitaria y densidad por dex;
cada panel usa su propio límite vertical automático, así que la altura no
representa una comparación entre tiempos. Se dejó más espacio entre filas y
bajo la última para separar métricas de los ejes. V2 combina perfiles y
posteriores para elegir xlim y los acota al prior; V3 usa solo las posteriores
para elegirlos. Ambas respetan `[-12,−1]`; cualquier perfil externo se recorta
solo en pantalla. V1 mantiene el prior completo. El comando estándar
`--official-a1-a3-times` regenera V2; V1 puede generarse con
`--official-a1-a3-times-full-prior-xlim`, y el alias V2 con
`--official-a1-a3-times-dynamic-xlim`. La
entrada P--T de VULCAN se dibuja negra y discontinua
en la columna P--T; las posteriores conservan las bandas por escenario. Se
retiró la clave redundante de intervalos y la etiqueta local `(dashed:
VULCAN)`, además de las entradas P--T de la leyenda global y el pie gris. A1
verde queda separado de A0 punteada en verde oscuro. Las advertencias
científicas permanecen en este informe. La versión anterior de siete columnas
se conserva en su ruta previa; los retrievals y sus salidas no se modificaron.
La iteración focal anterior de dos moléculas se conserva sin sobrescribir como
registro histórico ([PNG](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A1_A3_1_10_100h_official_A1noiseRepeat2_molecular_profiles_PT_proxima.png),
[PDF](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A1_A3_1_10_100h_official_A1noiseRepeat2_molecular_profiles_PT_proxima.pdf)).
No se alteró la matriz ni los datasets canónicos 8/8; la vista 10/100/240 h
queda preservada como auditoría histórica.

## Reproducción

- Preparar entradas aisladas (el script aborta si encuentra archivos previos):
  [`prepare_proxima_a1_a3_1h_official_datasets.sh`](../Thermal_Emission_Spectroscopy/scripts/prepare_proxima_a1_a3_1h_official_datasets.sh).
- Lanzar A1 o A3: `bash launch_proxima_a1_a3_1h_official_mpi.sh A1` o `A3` desde Ubuntu/WSL.
- El runner recibe `--hours 1 --n-live 800 --error-inflation none --surface-pressure-mode fixed-black --include-o2 --x-profile isochem --R 10000` y `--run-dir` bajo `/home/dasan/`.
- La matriz canónica de 8/8 y sus datasets no se regeneran ni se editan.
