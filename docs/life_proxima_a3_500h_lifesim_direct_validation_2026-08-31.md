# Validación directa de LIFEsim para Proxima A3 a 500 h, 2026-08-31

## Alcance

Se instaló LIFEsim clásico en el entorno WSL conda `POSEIDON` y se repitió la
observación sintética de Proxima A3 a 500 h llamando al instrumento de
LIFEsim directamente. El objetivo era comprobar si el retrieval piloto
anterior, que se había generado mientras el paquete no estaba instalado,
dependía de un cálculo incorrecto de las incertidumbres.

Este trabajo sigue siendo **evidencia de auditoría/piloto**. No amplía la
matriz canónica Proxima A0--A3 x {10 h, 240 h} y no convierte un S/N o un
posterior en una detección.

## Entorno instalado y compatibilidad

La ejecución se hizo en Ubuntu/WSL con:

```text
conda root: /home/wsldasan/miniconda3
environment: /home/wsldasan/miniconda3/envs/POSEIDON
POSEIDON_input_data: /home/wsldasan/POSEIDON/inputs
PYSYN_CDBS: /home/wsldasan/POSEIDON/inputs/stellar_grids
```

Versiones verificadas:

```text
POSEIDON 1.4.0
LIFEsim 0.2.32
SpectRes 2.1.1, fdannert/SpectRes commit 7a8c83025096c8907de30db633cca30c6f4b97ce
PyQt5 5.15.11
tables 3.11.1
GitPython 3.1.61
```

LIFEsim llama a `spectres(..., edge_mode=True)`. Por eso se instaló la variante
de `fdannert/SpectRes`, no el paquete stock `spectres 2.2.2`. PyQt5 5.15.4,
declarado literalmente por el metadata antiguo de LIFEsim, no ofrece el wheel
adecuado para este Python 3.12; se usó PyQt5 5.15.11 y la importación, la escena
y el cálculo pasaron. `pip check` también reporta un conflicto preexistente
entre `photutils 3.0.0` y `numpy 1.26.4`, pero cambiar `numpy` rompería la
restricción de POSEIDON y no es necesario para esta ruta.

La validación de la escena Proxima contra las anclas LIFE X dio:

```text
                       S/N nuestro   LIFE X   razón
D = 1 m, 10 h               48.4        45     1.07
D = 2 m, 10 h              166.5       170     0.98
D = 3.5 m, 10 h            412.4       466     0.88
```

Las tres razones quedan dentro del criterio documentado de 0.6--1.4.

## Cálculo directo de 500 h

El generador reproducible es
[`make_life_datasets.py`](../Thermal_Emission_Spectroscopy/scripts/make_life_datasets.py).
La nueva opción `--direct-lifesim` llama `LifeSceneClassic.observe` al tiempo
solicitado; no aplica posteriormente `sqrt(t)` a una sigma de 10 h. Se usó:

```bash
python make_life_datasets.py --campaign proxima --scenarios A3 --hours 500 \
  --seed 20260831 --direct-lifesim --name-suffix _lifesim_direct \
  --index-output ../outputs/life_proxima_b_earthlike_v1/life_data/dataset_index_500h_lifesim_direct_audit.json
```

El producto directo contiene 31 bins, semilla derivada `737920415` y S/N
mediano del continuo `332.02`:

- [dataset directo](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A3_500h_lifesim_direct.dat);
- [índice del dataset directo](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/dataset_index_500h_lifesim_direct_audit.json).

## Comparación con el retrieval piloto

Se comparó el dataset directo con el archivo consumido por el retrieval
`proxima_A3_500h`. Ambos tienen:

```text
31 bins y la misma malla de longitudes de onda
misma anchura de medio bin
misma sigma energética por bin
mismo flujo observado por bin
SHA-256 en ambos archivos:
E3CD8DE694D8875C5CD54B6B8057376C63A6847020E07D97DF3A111BD38AFF3A
```

La identidad se obtuvo usando la misma semilla y significa que el archivo
usado por el retrieval anterior es numéricamente y byte a byte igual al que
produce LIFEsim directo a 500 h. Por tanto, no se repitió MultiNest: repetirlo
con el archivo `_lifesim_direct` produciría la misma entrada y sólo duplicaría
el resultado. Los productos del retrieval siguen en
[`retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/)
y su resumen está en la
[auditoría del retrieval](life_proxima_a3_500h_retrieval_audit_2026-08-31.md).

## Interpretación y límites

La instalación corrige la incertidumbre de procedencia del piloto: el
resultado A3--500 h ya puede considerarse calculado con la escena clásica de
LIFEsim, aunque su ejecución original usó el escalado equivalente. No cambia
sus valores ni su clasificación como auditoría.

La rama sigue usando ruido astrofísico/fotónico diagonal, una sola realización
de ruido y un retrieval isquímico más simple que los perfiles verticales
VULCAN. LIFEsimMC/PHRINGE, covarianza instrumental, varias realizaciones y
modelos con/sin molécula siguen siendo necesarios para una conclusión
instrumental o una afirmación de detección.

## Código modificado

- `make_life_datasets.py`: opción de observación directa, sufijo de archivo e
  índice robusto frente al cambio de CWD que hace LIFEsim al inicializarse.
- `run_life_retrieval.py`: opciones `--dataset-file` y `--output-tag` para
  poder auditar datasets alternativos sin sobreescribir productos canónicos.
- `life_scene_classic.py`: importación opcional conservada para permitir que el
  postprocesamiento sin LIFEsim siga funcionando; la instancia directa exige
  ahora el paquete instalado.
