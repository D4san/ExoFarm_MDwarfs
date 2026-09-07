# Scripts de la Etapa III

Aquí viven adaptadores y validadores reproducibles para lectura de
perfiles VULCAN, forward de emisión POSEIDON, conversión a radiancia LIFEsimMC,
validación de unidades y cálculo SNR/covarianza. No duplicar aquí scripts de
transmisión ni comandos PandExo.

La rama clásica incluye runners de forward Tierra--Sol/Proxima,
contrafactuales, escena LIFEsim, S/N, generación de datasets, retrievals y
análisis de separación. `run_matrix.sh` reproduce la matriz canónica de 8
retrievals Proxima A0--A3 × {10 h, 240 h}.

No existe todavía un runner LIFEsimMC/PHRINGE ni un tratamiento de covarianza.
Esa ausencia es la frontera de trabajo futuro, no una propiedad de los
resultados clásicos.

## Piloto A3--500 h

El piloto intermedio del 2026-08-31 se ejecutó en Ubuntu/WSL con el entorno
conda `POSEIDON` y la configuración de entrada:

```bash
source /home/wsldasan/miniconda3/etc/profile.d/conda.sh
conda activate POSEIDON
export POSEIDON_input_data=/home/wsldasan/POSEIDON/inputs
export PYSYN_CDBS=/home/wsldasan/POSEIDON/inputs/stellar_grids
```

El entorno importa POSEIDON 1.4.0 y contiene `lifesim 0.2.32`, la variante
`SpectRes 2.1.1` de `fdannert/SpectRes` (necesaria para `edge_mode`), PyQt5
5.15.11, `tables` 3.11.1 y GitPython 3.1.61. La opción `--direct-lifesim` llama
al instrumento para cada tiempo solicitado; `--index-output` y
`--name-suffix` mantienen el producto de auditoría separado del índice y los
datasets canónicos:

```bash
python make_life_datasets.py --campaign proxima --scenarios A3 --hours 500 \
  --seed 20260831 --direct-lifesim --name-suffix _lifesim_direct \
  --index-output ../outputs/life_proxima_b_earthlike_v1/life_data/dataset_index_500h_lifesim_direct_audit.json
```

La ruta histórica que produjo el retrieval fue:

```bash
python make_life_datasets.py --campaign proxima --scenarios A3 --hours 500 \
  --seed 20260831 \
  --index-output ../outputs/life_proxima_b_earthlike_v1/life_data/dataset_index_500h_audit.json
python run_life_retrieval.py --campaign proxima --scenario A3 --hours 500 \
  --n-live 200
```

El archivo directo y el archivo histórico coinciden byte a byte, por lo que el
retrieval ya ejecutado es también válido para la observación directa y no se
repitió. Para un dataset alternativo se pueden usar `--dataset-file` y
`--output-tag` en `run_life_retrieval.py`, evitando sobreescribir resultados.
El piloto queda fuera de la matriz canónica A0--A3 x {10 h, 240 h}; su
procedencia y resultados están en
[`docs/life_proxima_a3_500h_retrieval_audit_2026-08-31.md`](../../docs/life_proxima_a3_500h_retrieval_audit_2026-08-31.md).
La validación directa está en
[`docs/life_proxima_a3_500h_lifesim_direct_validation_2026-08-31.md`](../../docs/life_proxima_a3_500h_lifesim_direct_validation_2026-08-31.md).

## Retrieval robusto A3--500/1200 h

Para la auditoría del 2026-08-31 se generaron ambos datasets directamente con
LIFEsim y se lanzaron con `N_live=800`, `Piette20`, PT `Madhu`, abundancias
`isochem` y el prior físico de `R_p_ref`. Las salidas se separan de las
anteriores mediante `--output-tag`:

```bash
python make_life_datasets.py --campaign proxima --scenarios A3 --hours 500 1200 \
  --seed 20260831 --direct-lifesim \
  --name-suffix _robust_lifesim_direct \
  --index-output ../outputs/life_proxima_b_earthlike_v1/life_data/dataset_index_500_1200h_robust_lifesim_direct_audit.json

python run_life_retrieval.py --campaign proxima --scenario A3 --hours 500 \
  --n-live 800 \
  --dataset-file Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A3_500h_robust_lifesim_direct.dat \
  --output-tag _robust_lifesim_direct

python run_life_retrieval.py --campaign proxima --scenario A3 --hours 1200 \
  --n-live 800 \
  --dataset-file Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A3_1200h_robust_lifesim_direct.dat \
  --output-tag _robust_lifesim_direct
```

El resultado resumido es `ln Z=901.17`, `chi^2_red=2.07` a 500 h y
`ln Z=898.31`, `chi^2_red=2.82` a 1200 h. Ambos son productos de
auditoría/piloto y no entran en la matriz canónica A0--A3 x {10 h, 240 h}.
El informe completo está en
[`docs/life_proxima_a3_500h_1200h_robust_retrieval_2026-08-31.md`](../../docs/life_proxima_a3_500h_1200h_robust_retrieval_2026-08-31.md).

## Diagnóstico de perfil vertical NH3 a 500 h

El 2026-09-01 se probó una parametrización `two-gradients` de POSEIDON para
`NH3` únicamente. Las demás especies permanecen `isochem`; se conserva PT
`Madhu`, `Piette20`, el dataset directo de LIFEsim y se usa `N_live=1000`:

```bash
python run_life_retrieval.py --campaign proxima --scenario A3 --hours 500 \
  --n-live 1000 \
  --dataset-file Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A3_500h_robust_lifesim_direct.dat \
  --output-tag _nh3twograd \
  --x-profile two-gradients \
  --vertical-gradient-species NH3
```

El resultado terminó con `ln Z=895.86 +/- 0.17`, `chi^2_red=3.15` y 18
parámetros; el retrieval isquímico robusto de referencia tiene
`ln Z=901.17 +/- 0.22` y `chi^2_red=2.07`. El perfil vertical recupera la
dirección de la caída de NH3, pero la capa alta queda débilmente constreñida y
el producto es sólo diagnóstico, no matriz canónica ni claim de detección.
Los nombres de salida son `proxima_A3_500h_nh3twograd` y el detalle completo
está en
[`docs/life_proxima_a3_500h_nh3_two_gradients_2026-09-01.md`](../../docs/life_proxima_a3_500h_nh3_two_gradients_2026-09-01.md).

## Diagnósticos rápidos de Bayes factor

`evaluate_life_bayes_factor_diagnostics.py` compara dos plantillas fijas sobre
el mismo dataset A3--240 h: A3 frente a A0 y A3 frente al contrafactual con
N2O reiniciado al perfil A0. Reproduce la conversión `Fp -> fotones -> bins
LIFE -> Fp` usada por el generador de datasets y evalúa una likelihood
gaussiana diagonal. Como no hay parámetros libres, la diferencia de
log-likelihood es el Bayes factor de este diagnóstico fijo:

```bash
python evaluate_life_bayes_factor_diagnostics.py
```

El resultado del 2026-09-01 fue `ln B=394.35` para A3/A0 y `ln B=385.63`
para A3/N2O-reiniciado. Los productos están en
`../outputs/life_proxima_b_earthlike_v1/tables/` y el informe
[`../../docs/life_proxima_bayes_factor_diagnostics_2026-09-01.md`](../../docs/life_proxima_bayes_factor_diagnostics_2026-09-01.md)
los clasifica como auditoría: no incluyen marginalización de nuisance
parameters, múltiples realizaciones ni covarianza instrumental.

## Ensayo directo frente a escalado de ruido

`compare_lifesim_noise_scaling.py` ejecuta `LifeSceneClassic.observe` para A0 y
A3 en 1, 10, 100, 240, 500 y 1200 h, y lo compara con
`sigma(10 h)*sqrt(10 h/t)`. Reutiliza una realización normal emparejada para
aislar la diferencia del modelo de ruido. Es una auditoría y no modifica la
matriz canónica:

```bash
python compare_lifesim_noise_scaling.py
```

Genera una tabla y un JSON en `../outputs/life_proxima_b_earthlike_v1/tables/`
y las figuras PNG/PDF en `../outputs/life_proxima_b_earthlike_v1/plots/audit/`.
El ensayo de 2026-08-31 encontró identidad dentro de la precisión numérica:
LIFEsim clásico sigue `sigma ∝ t^{-1/2}`. No prueba covarianza ni ruido
instrumental temporal; para eso sigue siendo necesaria la rama
LIFEsimMC/PHRINGE.

> **Reanudación:** antes de modificar o añadir un runner, leer el
> [contrato de Etapa III](../README.md), la
> [guía de reanudación](../../docs/project_resume.md) y la
> [validación clásica](../../docs/lifesim_classic_stage_iii_validation_2026-08-30.md).

## Figuras Proxima de espectro y señal

La capa visual clásica se regenera con estos scripts:

- `plot_emission_spectra.py`: espectro A0--A3 en la banda LIFE.
- `plot_emission_molecular_residuals.py`: espectro y señales moleculares
  contrafactuales.
- `plot_life_signal_noise_times.py`: señales A3 frente al ruido clásico para
  varios tiempos de integración.
- `plot_emission_snr_comparison.py`: SNR por banda y proyecciones de tiempo
  para alcanzar umbrales fijos.
- `retrieval_reference.py`: mapea perfiles VULCAN verticales a la referencia
  escalar de abundancia mediante el promedio columnar ponderado en presión.
- `analyze_retrieval_separation.py`: calcula la separación posterior--posterior
  y la separación firmada de A3 frente a la referencia A0 efectiva.
- `plot_proxima_retrieval_products.py`: tres figuras de retrieval LIFE para la
  matriz canónica Proxima A0--A3 x {10 h, 240 h}. El espectro global y los zooms
  moleculares muestran los extremos A0/A3; el atlas de perfiles/posteriores se
  centra en A3 y lo compara con el perfil VULCAN de A3 y una referencia A0
  efectiva, definida como promedio columnar ponderado en presión. Las curvas
  forward y recuperadas se interpolan a 250 puntos globales y 75 puntos por
  zoom solo para presentación; los datos originales no se alteran. Los
  marcadores observados llevan un contorno gris fino para aumentar el contraste.
La leyenda distingue explícitamente `Retrieved`, `True` y `Observed`, con los
  tonos y marcadores de la figura análoga de transmisión. Los envelopes
  continuos se muestran con `alpha=0.025` (2 sigma) y `alpha=0.05` (1 sigma)
  para mantener protagonistas a los puntos observados; las líneas `Retrieved`
  y `True` también se atenuaron; los marcadores de observación se ampliaron a
  5.8 pt en el panel global y 6.2 pt en los zooms.
  Los puntos son opacos (`alpha=1`) y sus barras de error conservan la
  transparencia del panel.

Para revisar juntos los cuatro tiempos de integración disponibles, el script
puede generar una vista de auditoría de cuatro filas (`10 h`, `240 h`, `500 h`
y `1200 h`) sin alterar las tres figuras canónicas:

```bash
python plot_proxima_retrieval_products.py \
  --four-row-audit-output ../outputs/life_proxima_b_earthlike_v1/plots/audit
```

La salida es `retrieval_profiles_posteriors_proxima_4rows_audit` en PNG y PDF.
Las filas de 500/1200 h leen los productos `_robust_lifesim_direct` y la
figura permanece clasificada como auditoría.

La revisión del 2026-08-30 usa títulos directos, etiquetas de moléculas sin
líneas verticales y rellenos sólidos claramente diferenciados para conservar la
lectura de las curvas. La figura conjunta adopta además la composición de tres
paneles del análogo de transmisión, con etiquetas y leyendas equivalentes. La
comparación SNR/proyección mantiene sólo el intervalo útil de 1--1000 h en su
panel inferior y ajusta el rango logarítmico superior a los puntos graficados.
En el atlas de perfiles, el perfil VULCAN A3 usa el tono oscuro de `True`, la
mediana posterior A3 el rosa de `Retrieved` y la referencia A0 efectiva el
verde oscuro de `True`. La leyenda de estas convenciones es horizontal bajo el
título; la fórmula de la distancia firmada aparece aparte y los recuadros
muestran la mediana A3, el valor A0 de referencia y su distancia en sigma.

Las figuras de retrieval conservan el observable directo `F_p` en
`W m^-2 m^-1`, separan espectro forward VULCAN, mediana recuperada, intervalo
del 68 % y bins observados. El perfil A3 se dibuja sólido, su mediana posterior
discontinua y la referencia A0 efectiva punteada; el panel global no lleva grid
y usa marcadores observados ampliados. En los recuadros del atlas se muestran
la mediana A3, el valor A0 de referencia y la distancia en sigma; no se
incorpora el piloto A3--1200 h.
Es un cambio de presentación; no cambia los productos científicos de entrada,
sus unidades ni la matriz de escenarios.
