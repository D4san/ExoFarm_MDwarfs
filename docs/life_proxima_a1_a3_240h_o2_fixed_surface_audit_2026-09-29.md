# Auditoría de retrievals Proxima A1/A3 a 240 h con MPI

**Cierre validado el 2026-09-30 America/Bogota:** ambos retrievals terminaron
con `exit_code=0`; se cosecharon y validaron las salidas de POSEIDON y
MultiNest. El informe conserva el caveat del preflight A3 y resume por separado
las posteriores, el ajuste y la comparación de P–T con VULCAN. La auditoría no
modifica la matriz canónica 8/8.

## Pregunta y alcance

Se lanzaron retrievals de emisión POSEIDON para Proxima A1 (Tierra actual) y A3
(forzamiento ExoFarm extremo) a 240 h, con el mismo modelo corregido. La
comparación futura preguntará si las abundancias isochem recuperadas se
desplazan hacia los valores A1/A3 y respecto de la referencia A0 efectiva bajo
ruido LIFE diagonal. Los dos archivos usan realizaciones de ruido diferentes;
los `ln Z` se interpretarán por dataset, nunca como un factor de Bayes entre
A1 y A3. Las distancias de abundancia serán condicionales a la parametrización
vertical, el perfil P--T, la realización y el modelo de ruido, no detecciones
formales.

La matriz canónica A0--A3 × {10 h, 240 h} permanece cerrada e intacta. Estos
dos productos son una auditoría comparativa adicional con sufijo separado.

## Entradas verificadas

Se reutilizaron los dos datasets canónicos de 31 bins, sin regenerarlos ni
editarlos:

| Escenario | Entrada | Semilla del índice | SHA-256 |
| --- | --- | ---: | --- |
| A1 | `LIFE_proxima_A1_240h.dat` | 857409621 | `0d73c1ff91ab756bae8905024095b4482a877d39b7051af0fa2f683899a1ab0c` |
| A3 | `LIFE_proxima_A3_240h.dat` | 473833971 | `7f04734252be9b8428ea13288d65471f861a23815723616b363b48b27efadd7b` |

La procedencia está en `life_data/dataset_index.json` (master seed
20260725). La incertidumbre es diagonal y cada escenario representa una sola
realización; A1/A3 no constituyen un experimento emparejado de ruido.

## Configuración y ejecución

Ambos usan POSEIDON en `/home/dasan/anaconda3/envs/POSEIDON`, MPICH 4.3.1,
seis ranks por retrieval (doce ranks MPI en total), `N_live=800`,
`X_profile=isochem`, inclusión de O2, superficie opaca explícita fija a 1 bar
(`log_P_surf=0`), `R=10000`, `error_inflation=none` y sin `x_tol`. El modelo
tiene 15 parámetros, incluido `log_P_surf` con prior de anchura cero. Las
bibliotecas OMP/OpenBLAS/MKL/NumExpr se limitaron a un hilo por rank. Una
prueba MPI4Py separada confirmó que el entorno inicia correctamente seis
ranks.

### Espacio de priors

La configuración `isochem` asigna un único log-abundancia constante con la
presión a cada especie recuperada. El código usa priors uniformes en el
parámetro logarítmico, de modo que la densidad previa es uniforme por dex y no
por intervalo lineal de VMR:

| Parámetro molecular | Prior de `log10(VMR)` | Equivalente en VMR |
| --- | ---: | ---: |
| H2O, CO2, CH4, O3, N2O, NH3 | Uniforme [`−12`, `−1`] | `10⁻¹²` a `10⁻¹` |
| O2 | Uniforme [`−6`, `log10(0.5)`] | `10⁻⁶` a `0.5` |

Cada especie tiene su propio parámetro. Para los demás parámetros,
`a1,a2 ~ U[0.02,2]`, `log_P1,log_P2 ~ U[−6,1]`,
`log_P3 ~ U[−2,1]`, `T_ref ~ U[150,400] K`, y `R_p_ref` tiene el intervalo
`[0.8,1.3]` veces el radio nominal del planeta (los límites se entregan a
POSEIDON en metros). `log_P_surf=0` fija la superficie en 1 bar y tiene ancho
de prior cero; `x_tol` no se muestrea porque la inflación de errores está
desactivada. Estos límites reproducen
[`run_life_retrieval.py`](../Thermal_Emission_Spectroscopy/scripts/run_life_retrieval.py).

El lanzador reproducible es
[`launch_proxima_a1_a3_240h_o2_fixed_surface_mpi6_audit.sh`](../Thermal_Emission_Spectroscopy/scripts/launch_proxima_a1_a3_240h_o2_fixed_surface_mpi6_audit.sh).
Escribe primero los outputs MultiNest a filesystem Linux ext4 y cosecha solo
los ficheros con el prefijo exacto del run después de un `exit_code=0`; no
sobrescribe destinos existentes. El scratch actual es
`/home/dasan/exofarm_proxima_a1_a3_240h_MPI6_20260930T044539Z/{A1,A3}`.

| Escenario | PID `mpiexec` | Log durable | PID file | Estado al inicio |
| --- | ---: | --- | --- | --- |
| A1 | 45344 | `outputs/life_proxima_b_earthlike_v1/retrievals/proxima_A1_240h_O2_fixedBlack1bar_noxtol_MPI6_AUDIT.launch.log` | `proxima_A1_240h_O2_fixedBlack1bar_noxtol_MPI6_AUDIT.pid` | MultiNest iniciado, 800 live points / 15 dimensiones |
| A3 | 45353 | `outputs/life_proxima_b_earthlike_v1/retrievals/proxima_A3_240h_O2_fixedBlack1bar_noxtol_MPI6_AUDIT.launch.log` | `proxima_A3_240h_O2_fixedBlack1bar_noxtol_MPI6_AUDIT.pid` | MultiNest iniciado, 800 live points / 15 dimensiones |

Ambos logs registran el cierre de MultiNest, `All done!`, `exit_code=0` y
`harvest_complete` el 2026-09-30 a las 19:10 COT. Los seis ranks de cada run
se mantuvieron en el filesystem ext4 de WSL; el lanzador cosechó los productos
bajo el prefijo exacto de cada auditoría tras el cierre exitoso. No se reinició
el muestreo ni se sobrescribieron los datos de entrada o la matriz canónica.

## Preflight del forward A3

`--setup-only` validó en ambos escenarios el modelo, la carga del dataset y los
priors. Para A3, la comprobación opcional de forward sobre los 31 bins dio RMS
`0.3901 sigma` y máximo `1.247 sigma`; el helper existente exige RMS ≤ `0.3`
y máximo ≤ `1.0`, de modo que reportó fallo de esa puerta estricta. El cociente
coincide, dentro del redondeo, con escalar las cifras de la auditoría corregida
de 100 h (`0.2518`, `0.8048`) por `sqrt(240/100)`, como se espera al reducir
sigma diagonal con `t^{-1/2}` para el mismo residuo espectral. Por tanto, se
conserva como caveat cuantitativo y no se etiqueta como `forward PASS`; el
retrieval A3 se ejecuta sin invocar esa aserción opcional. Los residuos por bin
y el ajuste posterior deberán revisarse antes de cualquier interpretación.

## Validación de cierre

El script [`audit_proxima_a1_a3_240h_mpi.py`](../Thermal_Emission_Spectroscopy/scripts/audit_proxima_a1_a3_240h_mpi.py)
verificó los marcadores de salida limpia y cosecha, configuración y etiquetas
de dataset, hashes de entrada, archivos MultiNest, coincidencia entre las
muestras equiponderadas de MultiNest y POSEIDON, la presión superficial fija y
valores finitos. Los dos casos contienen 800 puntos vivos; las muestras
posteriores tienen 6,426 × 15 (A1) y 6,596 × 15 (A3), los espectros
recuperados 16,094 × 6, los perfiles P–T 100 × 6 y `log_X` 800 filas
numéricas para las ocho especies. No se encontraron NaN/Inf. Los hashes de los
datasets cosechados coinciden con los hashes de entrada registrados arriba.

| Escenario | Evaluaciones | Reemplazos finales | `ln Z` por dataset | `χ²` (`χ²_red`, dof) | `R_p_ref` mediana [q16, q84] (`R_⊕`) |
| --- | ---: | ---: | ---: | ---: | ---: |
| A1 | 1,798,753 | 43,899 | 860.93 ± 0.25 | 152.73 (9.55, 16) | 1.2070 [1.2031, 1.2109] |
| A3 | 1,759,492 | 46,077 | 844.95 ± 0.25 | 179.23 (11.20, 16) | 1.2151 [1.2105, 1.2195] |

Los `ln Z` describen cada ajuste por separado. A1 y A3 usan datasets y
realizaciones de ruido distintos; su diferencia no es un factor de Bayes ni
una comparación de escenarios marginalizada.

## Posteriores moleculares y referencias efectivas

Las referencias escalares son promedios de columna ponderados por presión de
los perfiles VULCAN, con `X_eff = integral X(p) dp / (p_bottom - p_top)`.
`z=(mediana posterior − referencia)/σ68`, con
`σ68=(q84−q16)/2`, se incluye como distancia descriptiva condicional; no es
una significancia de detección.

| Escenario de entrada | `log10 N2O` | `log10 NH3` | `log10 O2` |
| --- | ---: | ---: | ---: |
| A0 efectiva | −6.8843 | −9.9505 | −0.6958 |
| A1 efectiva | −6.7338 | −9.3049 | −0.6958 |
| A3 efectiva | −6.0141 | −8.2315 | −0.6958 |

| Retrieval | Especie | Posterior q16 / mediana / q84 (`log10 VMR`) | `z` vs A0 | `z` vs escenario de entrada |
| --- | --- | ---: | ---: | ---: |
| A1 | N2O | −11.0249 / −9.0544 / −7.7947 | −1.34 | −1.44 |
| A1 | NH3 | −11.6028 / −10.7702 / −9.8352 | −0.93 | −1.66 |
| A1 | O2 | −5.1373 / −3.4457 / −1.7080 | −1.60 | −1.60 |
| A3 | N2O | −6.1255 / −6.0921 / −6.0603 | +24.30 | −2.39 |
| A3 | NH3 | −11.2368 / −9.8414 / −8.8241 | +0.09 | −1.33 |
| A3 | O2 | −5.1206 / −3.3533 / −1.6477 | −1.53 | −1.53 |

El retrieval A1 no separa N2O ni NH3 de A0 efectiva: ambas posteriores son
amplias y las referencias A0/A1 son cercanas. A3 produce una posterior de N2O
muy estrecha y desplazada respecto de A0, pero su mediana queda 2.39 `σ68`
por debajo de A3 efectiva; NH3 permanece amplia y centrada cerca de A0, y O2
no se recupera con precisión. La cifra descriptiva `z_N2O=+24.30` no se
presenta como detección: los dos ajustes tienen `χ²_red` muy alto, el
preflight A3 no satisfizo la puerta estricta y el PT recuperado difiere mucho
del VULCAN de entrada.

| Retrieval | RMS de `T_mediana − T_VULCAN` | Sesgo mediano | Verdad dentro de bandas marginales 68 % / 95 % |
| --- | ---: | ---: | ---: |
| A1 | 63.68 K | +38.65 K | 2 % / 5 % de niveles |
| A3 | 55.56 K | +28.87 K | 3 % / 12 % de niveles |

Las coberturas por nivel son resúmenes marginales, no cobertura conjunta del
perfil. En conjunto, el ajuste espectral y la recuperación térmica muestran
tensión de modelo suficiente para impedir una afirmación robusta de
distinción A3/A0, incluso cuando N2O aparece muy separado en la métrica
condicional.

### Por qué el ajuste de 240 h queda más tensionado

Los retrievals corregidos de 10, 100 y 240 h mantienen el mismo modelo y
configuración inferencial: `isochem`, los mismos priors, `N_live=800`, O2,
superficie negra fija a 1 bar, `R=10000`, sin `x_tol` ni inflación, y 31 bins.
Lo que cambia es el tiempo/ruido del dataset; la fila de 100 h, además, usa
realizaciones de auditoría independientes. Los ajustes registrados son:

| Tiempo | `χ²_red` A1 | `χ²_red` A3 | Dof |
| --- | ---: | ---: | ---: |
| 10 h | 1.55 | 1.28 | 16 |
| 100 h (auditoría) | 3.18 | 4.94 | 16 |
| 240 h | 9.55 | 11.20 | 16 |

En el escalado de ruido clásico, `σ(t)=σ(10 h)√(10 h/t)`; por tanto,
`σ(240 h)≈0.204 σ(10 h)`. El perfil `isochem` y la parametrización P–T no
reproducen completamente la atmósfera VULCAN. Al estrecharse los errores, esa
diferencia entre verdad y modelo pesa más en `χ²`. La tendencia también puede
recibir contribución de que cada archivo contiene una realización de ruido
distinta. Así, 240 h revela con mayor claridad la tensión de este modelo con
los datos sintéticos; no indica que observar más horas empeore por sí mismo el
experimento. Mantener iguales modelo y priors es lo apropiado para comparar
tiempos. Cambiarlos solo a 240 h confundiría la comparación; perfiles
verticales más flexibles y varias realizaciones son pruebas separadas de
robustez.

## Figura y productos reproducibles

- Figura comparativa revisada el 2026-10-01, organizada por tiempo (filas de 10, 100 y 240 h): [PNG](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A1_A3_10_100_240h_audit_molecular_profiles_PT_proxima.png) / [PDF](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A1_A3_10_100_240h_audit_molecular_profiles_PT_proxima.pdf). La implementación adapta directamente la cuadrícula compacta, la leyenda y los recuadros de `plot_profiles_posteriors()` del atlas original. Se limita a N2O y NH3: histogramas marginales A1/A3, barras horizontales asimétricas q16–q84 alrededor de la mediana, perfiles verticales VULCAN A1/A3, referencias efectivas A0 y distancias firmadas `z_A1|A0`/`z_A3|A0`; la tercera columna compara P–T posterior y entrada. Los recuadros moleculares muestran A0, medianas, intervalos y z; los de P–T muestran `χ²_red`, dof y `ln Z` finales por dataset. `z` es descriptivo condicional, no una significancia; los `ln Z` de realizaciones independientes no son un factor de Bayes entre A1/A3. La fila de 100 h usa datasets de auditoría independientes (semillas A1 `460512527`, A3 `129315834`), fuera de la matriz canónica. PNG y PDF se regeneraron e inspeccionaron.
- La figura conjunta toma los productos corregidos de 10 h (A1 `MPI6R1` y A3 `_O2_fixedBlack1bar_noxtol`) y los dos productos de auditoría MPI6 de 240 h descritos aquí. Los cuatro usan 800 puntos vivos, el modelo isochem de 15 parámetros, O2, superficie negra fijada a 1 bar y `R=10000`; los datasets son LIFE de 31 bins y las realizaciones de ruido son independientes. Las corridas A1 de 10 h y A3 de 10 h se documentan, respectivamente, en las auditorías [A1 10/100 h](life_proxima_a1_10_100h_o2_fixed_surface_audit_2026-09-29.md) y [A3 10 h](life_proxima_a3_10h_o2_fixed_surface_audit_2026-09-27.md).
- Figura previa, limitada a las dos corridas de 240 h y a N2O/NH3/O2: [PNG](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A1_A3_240h_MPI6_AUDIT_posteriors_PT_proxima.png) / [PDF](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A1_A3_240h_MPI6_AUDIT_posteriors_PT_proxima.pdf). Se conserva como vista anterior; la figura comparativa actual por tiempo se limita a N2O/NH3 e incluye A0 efectiva, z, intervalos asimétricos q16–q84 y perfiles VULCAN.
- Figura previa de posteriores y perfiles verticales de abundancia (N2O, NH3 y O2): [PNG](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A1_A3_240h_MPI6_AUDIT_profiles_posteriors_proxima.png) / [PDF](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A1_A3_240h_MPI6_AUDIT_profiles_posteriors_proxima.pdf). Se mantiene como registro de la primera composición, no como figura principal de la comparación por tiempo.
- Resumen de métricas, checksums y validación: [JSON](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/retrieval_A1_A3_240h_MPI6_AUDIT_posteriors_PT_proxima_summary.json).
- Validador y generador: [`audit_proxima_a1_a3_240h_mpi.py`](../Thermal_Emission_Spectroscopy/scripts/audit_proxima_a1_a3_240h_mpi.py).
- Generador de la figura comparativa: [`plot_proxima_retrieval_products.py`](../Thermal_Emission_Spectroscopy/scripts/plot_proxima_retrieval_products.py), opción `--audit-a1-a3-times` (el alias antiguo `--audit-a1-a3-240h` sigue habilitado). La opción produce solo la figura de auditoría y deja intactas las figuras canónicas.
- Logs finales: `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/proxima_A1_240h_O2_fixedBlack1bar_noxtol_MPI6_AUDIT.launch.log` y su equivalente `proxima_A3_...launch.log`.
- Productos POSEIDON se conservan bajo `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/` con los prefijos exactos del audit.

La interpretación sigue limitada por ruido diagonal y una realización por
escenario, el perfil isochem frente a perfiles VULCAN, la recuperación P–T
tensionada y la puerta de forward A3 no satisfecha. Los productos son una
auditoría adicional: la matriz canónica 8/8 y los datasets originales siguen
intactos.
