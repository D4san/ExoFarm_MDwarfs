# Inventario de la campaña `life_proxima_b_earthlike_v1`

## Resultado actual: matriz A1/A3 corregida (2026-10-28)

La campaña de retrievals LIFE Proxima más reciente es la matriz
A1/A3 `COMPLETE_VALIDATED`, con 33 nuevos retrievals auditados y tres
referencias A3 aceptadas. El índice de campañas está en
[`retrievals/README.md`](retrievals/README.md); el resultado científico y las
tablas están en
[`docs/life_proxima_a1_a3_corrected_binning_matrix_results_2026-10-28.md`](../../../docs/life_proxima_a1_a3_corrected_binning_matrix_results_2026-10-28.md).

## Referencia A3–100 h validada, continuación MPI14 (2026-10-18)

La continuación MPI14 terminó con `exit_code=0` y pasó la auditoría
independiente. Es la referencia A3–100 h usada por análisis anteriores; sus
resultados son distintos de la nueva matriz y se conservan. El intento serial
del 17-oct y el preflight MPI fallido también permanecen documentados como
historial, no como trabajos activos. Véanse el
[README de la campaña](retrievals/a3_100h_binning_corrected_mpi14_resume_20261018/README.md)
y la [bitácora MPI14](../../../docs/life_proxima_a3_100h_binning_corrected_mpi14_resume_2026-10-18.md).

## Campaña focal anterior: cierre 2026-10-11

La serie focal anterior estudió A1/A3 × {1,10,100 h}: seis completos,
36 LOO y tres restricciones A0 fija **solo A3-100 h**. Las restricciones
están aceptadas con salvedad numérica de momentos fijos, originales y hashes
preservados. La matriz corregida posterior está enlazada en la sección
“Resultado actual” al inicio de este inventario. Véanse la
[síntesis científica](../../../docs/life_proxima_exofarm_retrieval_layers_synthesis_2026-10-11.md),
[campaña A0 y tabla final](retrievals/a0_fixed_reference_20261010/README.md)
y [campaña LOO](retrievals/molecule_ablation_loo_20261004/README.md).

## Productos canónicos históricos: matriz legacy 8/8

La matriz histórica preservada contiene **8 corridas**, fuera del total
focal de 45 productos que cerró el 2026-10-11:

```text
Proxima A0--A3 x {10 h, 240 h}
```

Los ocho datasets autorizados están enumerados en
[`life_data/dataset_index.json`](life_data/dataset_index.json). Los resultados
que alimentaron el análisis histórico de separación son los archivos 10/240 h de
`retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/` y el resumen
[`../_comparison/retrieval_separation_from_A0.csv`](../_comparison/retrieval_separation_from_A0.csv).

## Figuras de retrieval

Las tres figuras reproducibles de la matriz canónica se generan con
`Thermal_Emission_Spectroscopy/scripts/plot_proxima_retrieval_products.py` y
se guardan en `plots/` en PNG y PDF:

Las dos figuras espectrales comparan únicamente los extremos A0 y A3 para
mantener legible la separación entre referencia preagrícola y ExoFarm extremo.
La figura de perfiles/posteriores se centra en A3: muestra el perfil vertical
VULCAN de A3, su posterior isoquímico y una única referencia escalar A0
efectiva, calculada como promedio columnar ponderado en presión. Esta referencia
no es la abundancia de la capa superficial ni el posterior A0. Las curvas
forward y recuperadas se interpolan a 250 puntos en el panel global y 75 puntos
por ventana molecular únicamente para presentación; los bins LIFE, las muestras
y los resultados de retrieval no se modifican. Los puntos observados llevan un
contorno gris fino para conservar su protagonismo sobre los envelopes
continuos. La semántica visual sigue la figura análoga de transmisión: tonos
brillantes para `Retrieved`, tonos oscuros para `True` y `Observed`, y
círculo/rombo para A0/A3.
El panel global no usa grid de fondo y sus marcadores observados son mayores
que los de la versión anterior: 5.8 pt en el panel global y 6.2 pt en los
zooms, con borde gris ligeramente reforzado.
Para dar prioridad a las observaciones, los envelopes continuos usan
`alpha=0.025` (2 sigma) y `alpha=0.05` (1 sigma); las líneas continuas se
atenúan a propósito; las barras de error mantienen la opacidad definida para
la figura análoga de transmisión, mientras que los puntos se dibujan opacos y
con borde gris.

En el atlas de perfiles, el perfil VULCAN A3 usa el tono oscuro de `True`, la
mediana posterior A3 el rosa de `Retrieved` y la referencia A0 efectiva el
verde oscuro de `True`. La leyenda de estas tres convenciones queda horizontal
bajo el título; la fórmula de la distancia firmada aparece aparte y los
recuadros de cada panel muestran la mediana A3, el valor A0 de referencia y su
distancia en sigma.

- `retrieval_global_spectra_proxima`: espectro completo, forward VULCAN,
  mediana recuperada, intervalo del 68 % y bins observados;
- `retrieval_molecular_zooms_proxima`: ventanas de N2O y NH3;
- `retrieval_profiles_posteriors_proxima`: perfil VULCAN A3, posterior A3,
  referencia A0 efectiva, medianas, barras de incertidumbre y muestras para
  H2O, CO2, CH4, O3, N2O y NH3.

Como producto separado de auditoría, `retrieval_A1_A3_10_100_240h_audit_molecular_profiles_PT_proxima`
ordena las filas por integración (10, 100 y 240 h) y se concentra en N2O/NH3,
más una columna P–T. Cada panel molecular muestra posteriores A1/A3, barras de
errores horizontales asimétricos q16–q84 alrededor de la mediana, perfiles verticales VULCAN de ambos
escenarios, referencia efectiva A0 y distancias z firmadas respecto a A0. Las
abundancias recuperadas son isochem y constantes con presión; por claridad, la
incertidumbre se resume como errorbar y no como banda vertical extensa. La fila
de 100 h usa datasets independientes de auditoría (semillas A1 `460512527` y
A3 `129315834`). `z` es una distancia descriptiva condicional, distinta de
`ln Z` y no equivalente a detección formal. Se genera con
`--audit-a1-a3-times` en `plot_proxima_retrieval_products.py`; deja intactas las
figuras y datos canónicos. Las figuras anteriores se conservan como vistas
históricas.

El observable es el flujo planetario directo `F_p` en `W m^-2 m^-1`, mostrado
con una escala de `10^-13` para legibilidad. Las figuras se construyen desde
los productos canónicos A0--A3 x {10 h, 240 h}; los espectros muestran A0/A3 y
el atlas de perfiles muestra A3 contra la referencia A0 efectiva. El retrieval
A3--1200 h sigue clasificado como evidencia de auditoría/piloto y no se mezcla
con la matriz canónica.

## Evidencia de auditoría/piloto: 500 h

El 2026-08-31 se ejecutó un retrieval intermedio `A3--500 h` con la
configuración corregida de POSEIDON. El dataset y su índice separado se
conservan en:

- [`life_data/LIFE_proxima_A3_500h.dat`](life_data/LIFE_proxima_A3_500h.dat);
- [`life_data/dataset_index_500h_audit.json`](life_data/dataset_index_500h_audit.json);
- [`retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/`](retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/).

La corrida terminó normalmente (`ln Z = 893.18 +/- 0.40`, `chi^2_red = 1.59`,
`R_p_ref = 1.23 R_E`). El dataset tiene 31 bins y S/N mediano del continuo
`332.02`; se generó mediante `sigma(t)=sigma(10 h)*sqrt(10/t)` a partir de
los bins clásicos validados, con semilla maestra `20260831` y semilla derivada
`737920415`.

Este producto es **auditoría/piloto y está excluido** de la matriz canónica y
del atlas oficial. La corrida de POSEIDON se lanzó antes de instalar `lifesim`
en el WSL utilizado y consumió el archivo `.dat` generado por escalado. Después
se instaló LIFEsim 0.2.32 con SpectRes 2.1.1 y se llamó directamente al
instrumento para regenerar el mismo caso:

- [`life_data/LIFE_proxima_A3_500h_lifesim_direct.dat`](life_data/LIFE_proxima_A3_500h_lifesim_direct.dat);
- [`life_data/dataset_index_500h_lifesim_direct_audit.json`](life_data/dataset_index_500h_lifesim_direct_audit.json).

Los dos `.dat` son idénticos byte a byte, con el mismo SHA-256, bins, flujo,
sigma y semilla. Por ello, el retrieval existente ya está alimentado por los
mismos valores que produce la observación directa de LIFEsim y no se repitió
MultiNest. La instalación, calibración y comparación están documentadas en
[`docs/life_proxima_a3_500h_lifesim_direct_validation_2026-08-31.md`](../../../docs/life_proxima_a3_500h_lifesim_direct_validation_2026-08-31.md).
La corrida de POSEIDON generó muestras, espectro, perfiles y archivos crudos de
MultiNest.
La vista de posteriores [`plots/audit/retrieval_profiles_posteriors_proxima_A3_500h_audit.png`](plots/audit/retrieval_profiles_posteriors_proxima_A3_500h_audit.png)
es sólo de inspección.

## Ensayo de ruido directo frente a escalado

Se comparó `LifeSceneClassic.observe` directo con el escalado desde 10 h para
A0 y A3 en 1--1200 h, manteniendo la misma escena Proxima, los forwards y una
realización normal emparejada. La máxima diferencia relativa de `sigma` fue
`6.7e-16`; la máxima diferencia de la realización emparejada fue
`8.5e-15 sigma`. En LIFEsim clásico, el escalado reproduce por tanto el ruido
esperado de la llamada directa. Este ensayo es sólo auditoría y no prueba
covarianza o inestabilidad instrumental.

- [`tables/lifesim_noise_scaling_comparison.csv`](tables/lifesim_noise_scaling_comparison.csv)
- [`tables/lifesim_noise_scaling_comparison.json`](tables/lifesim_noise_scaling_comparison.json)
- [`plots/audit/lifesim_direct_vs_scaled_noise_proxima.png`](plots/audit/lifesim_direct_vs_scaled_noise_proxima.png)
- [`plots/audit/lifesim_direct_vs_scaled_noise_proxima.pdf`](plots/audit/lifesim_direct_vs_scaled_noise_proxima.pdf)

## Evidencia de auditoría/piloto: 1200 h

Se conservan fuera de la matriz canónica:

- `life_data/LIFE_proxima_A0_1200h.dat`
- `life_data/LIFE_proxima_A1_1200h.dat`
- `life_data/LIFE_proxima_A2_1200h.dat`
- `life_data/LIFE_proxima_A3_1200h.dat`
- productos del retrieval `proxima_A3_1200h`

Estos archivos **no son residuos ni una campaña independiente**. Pertenecen al
diseño inicial de 1200 h y documentan los pilotos que revelaron el desajuste de
modelo a S/N alto. Se clasifican como **evidencia de auditoría/piloto**:

- no cuentan en el cierre 8/8;
- no se incluyen en `dataset_index.json`;
- no sustentan las tablas o claims canónicos;
- no deben borrarse sin una revisión de evidencia científica y aprobación
  explícita.

La decisión y la interpretación se registran en
[`../../../docs/lifesim_classic_stage_iii_validation_2026-08-30.md`](../../../docs/lifesim_classic_stage_iii_validation_2026-08-30.md).

## Retrievals robustos de auditoría: A3 a 500 h y 1200 h

El 2026-08-31 se generaron datasets nuevos llamando directamente a LIFEsim
clásico y se relanzaron ambos retrievals con `N_live=800`. Se usaron PT
`Madhu`, abundancias `isochem`, `Piette20` y el prior físico de `R_p_ref` en
metros. Los productos tienen nombres separados con el sufijo
`_robust_lifesim_direct` y no reemplazan ni borran los pilotos anteriores.

El índice de entrada es
[`life_data/dataset_index_500_1200h_robust_lifesim_direct_audit.json`](life_data/dataset_index_500_1200h_robust_lifesim_direct_audit.json),
con los datasets directos:

- [`life_data/LIFE_proxima_A3_500h_robust_lifesim_direct.dat`](life_data/LIFE_proxima_A3_500h_robust_lifesim_direct.dat);
- [`life_data/LIFE_proxima_A3_1200h_robust_lifesim_direct.dat`](life_data/LIFE_proxima_A3_1200h_robust_lifesim_direct.dat).

| Integración | `ln Z` | `chi^2_red` | `R_p_ref` | `log_N2O` (1 sigma) | `log_NH3` (1 sigma) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 500 h | `901.17 +/- 0.22` | `2.07` | `1.23 (+0.01/-0.01) R_E` | `-5.43 (+0.26/-0.28)` | `-8.68 (+1.69/-2.11)` |
| 1200 h | `898.31 +/- 0.22` | `2.82` | `1.26 (+0.02/-0.02) R_E` | `-5.06 (+0.20/-0.23)` | `-8.79 (+1.76/-2.09)` |

Los resultados completos están en los archivos con el mismo prefijo dentro de
[`retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/`](retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/).
La ejecución vieja de 1200 h permanece archivada como evidencia del fallo
numérico anterior; estos runs robustos son la referencia de auditoría actual,
no resultados canónicos. Las muestras dejan además `a1` cerca del límite
superior de su prior en ambos tiempos, así que la robustez demostrada es
computacional frente al fallo antiguo; para una inferencia final falta una
prueba de sensibilidad con ese prior ampliado.

La vista conjunta de las cuatro posteriores está disponible sólo para
inspección en:

- [`plots/audit/retrieval_profiles_posteriors_proxima_4rows_audit.png`](plots/audit/retrieval_profiles_posteriors_proxima_4rows_audit.png);
- [`plots/audit/retrieval_profiles_posteriors_proxima_4rows_audit.pdf`](plots/audit/retrieval_profiles_posteriors_proxima_4rows_audit.pdf).

La procedencia, los comandos, la verificación de muestras y los límites de
interpretación están en
[`docs/life_proxima_a3_500h_1200h_robust_retrieval_2026-08-31.md`](../../../docs/life_proxima_a3_500h_1200h_robust_retrieval_2026-08-31.md).

### Diagnóstico de perfil vertical NH3 a 500 h

El 2026-09-01 se reutilizó el dataset directo de 500 h para probar
`X_profile=two-gradients` sólo en `NH3`. El resto de las especies permaneció
`isochem`; se conservaron PT `Madhu`, `Piette20`, el prior físico de radio y
se usaron `N_live=1000`. La corrida terminó con `ln Z=895.86 +/- 0.17`,
`chi^2_red=3.15`, `dof=13` y 18 parámetros. El posterior muestra la dirección
de la caída vertical de NH3, pero con una capa alta muy ancha; además, no
mejora al retrieval isquímico robusto de referencia (`ln Z=901.17`,
`chi^2_red=2.07`).

Estos productos son **auditoría/diagnóstico excluido**: no reemplazan el
retrieval isquímico, no entran en la matriz canónica ni sustentan un claim de
detección. El detalle y los enlaces a los archivos están en
[`docs/life_proxima_a3_500h_nh3_two_gradients_2026-09-01.md`](../../../docs/life_proxima_a3_500h_nh3_two_gradients_2026-09-01.md).

## Diagnósticos de Bayes factor A3--240 h

El 2026-09-01 se ejecutó el experimento de auditoría
`life_bayes_factor_diagnostics_A3_240h` sobre el dataset canónico
`life_data/LIFE_proxima_A3_240h.dat`. Se compararon plantillas fijas sobre los
mismos 31 bins:

- A3 frente a A0: `ln B=394.35`, `log10 B=171.26`;
- A3 frente a A3 con N2O reiniciado al perfil A0: `ln B=385.63`,
  `log10 B=167.48`.

El segundo contraste elimina el exceso de N2O de A3, pero no fija toda la
abundancia de N2O a cero. La evaluación usa la misma likelihood diagonal
gaussiana y la misma conversión de unidades del generador LIFE. Es un
diagnóstico de plantillas fijas: no marginaliza parámetros nuisance, no usa
covarianza instrumental y no cambia la matriz canónica.

Los resultados reproducibles están en:

- [`tables/life_bayes_factor_diagnostics_A3_240h.csv`](tables/life_bayes_factor_diagnostics_A3_240h.csv);
- [`tables/life_bayes_factor_diagnostics_A3_240h.json`](tables/life_bayes_factor_diagnostics_A3_240h.json);
- [`../../../docs/life_proxima_bayes_factor_diagnostics_2026-09-01.md`](../../../docs/life_proxima_bayes_factor_diagnostics_2026-09-01.md).

## Limitación común de toda la campaña

Los datasets y retrievals de esta carpeta usan LIFEsim clásico con sigma
diagonal y una realización de ruido. Son una cota optimista hasta ejecutar la
rama LIFEsimMC/PHRINGE con covarianza instrumental.
