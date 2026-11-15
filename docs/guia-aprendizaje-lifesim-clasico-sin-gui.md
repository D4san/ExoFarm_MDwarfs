---
aliases:
  - LIFEsim clásico sin GUI
  - LIFE desde Python
tags:
  - astronomía/exoplanetas
  - tutorial
  - espectroscopía
created: 2026-10-02
---

# Guía de aprendizaje: usar LIFEsim clásico desde código

Esta nota recorre paso a paso qué hace LIFEsim, qué necesita como entrada, qué devuelve y cómo se conecta con el flujo LIFE de ExoFarm. Está escrita para aprender desde consola y Python; no requiere GUI.

El ejemplo es la rama Proxima del repositorio ExoFarm. Representa un planeta con atmósfera terrestre bajo el ambiente de Proxima Centauri. Es un análogo controlado para estudiar el método; sus resultados no describen una atmósfera medida de Proxima b.

> [!abstract] La idea central
> LIFEsim clásico recibe un espectro de emisión planetaria sin ruido y una escena de observación. Calcula el binning, el S/N y una incertidumbre esperada por bin bajo su modelo clásico de ruido astrofísico/fotónico. El código de ExoFarm usa esos errores para fabricar un espectro sintético con una realización aleatoria de ruido. Después POSEIDON ajusta ese espectro.

## 1. El recorrido completo, en una mirada

```text
Perfiles de temperatura y química de VULCAN
        ↓
POSEIDON calcula emisión térmica del planeta
        ↓
Espectro planetario observado Fp, todavía sin ruido
        ↓
LIFEsim clásico: escena, bins, S/N por bin y sigma por bin
        ↓
El generador añade una realización aleatoria de ruido
        ↓
Archivo .dat: longitud de onda, flujo observado y sigma
        ↓
POSEIDON hace retrieval del espectro sintético
```

| Etapa | Qué responde | Archivo o código del proyecto |
|---|---|---|
| VULCAN | ¿Qué perfiles de temperatura y composición produce la atmósfera? | Perfiles PT y química |
| POSEIDON en emisión | ¿Qué flujo térmico planetario llega al observatorio? | `run_proxima_forward.py` |
| LIFEsim clásico | ¿Qué resolución y ruido fotónico/astrofísico corresponderían a esta escena LIFE? | `life_scene_classic.py` |
| Generador de datos | ¿Cómo quedaría una realización concreta con ruido aleatorio? | `make_life_datasets.py` |
| POSEIDON retrieval | ¿Qué parámetros atmosféricos son compatibles con esos datos y errores? | `run_life_retrieval.py` |

LIFEsim no calcula la fotoquímica ni recupera abundancias atmosféricas. Esas tareas pertenecen, respectivamente, a VULCAN y POSEIDON.

## 2. Vocabulario básico

### Escena

La **escena** reúne las propiedades del instrumento y del sistema observado. En el ejemplo incluye resolución y rango de longitudes de onda, diámetro de los colectores, temperatura y radio de la estrella, distancia al sistema, separación angular planeta–estrella, brillo del zodi local y del exozodi, y latitud eclíptica de la línea de visión.

Si cambian la distancia, la estrella, el exozodi o el tamaño de los colectores, cambia el S/N aunque el espectro planetario sea el mismo.

### Flujo planetario y flujo estelar

En este flujo usamos el **flujo planetario recibido en el observatorio**, `Fp_obs`, con unidades:

```text
W m^-2 m^-1
```

Ese es el espectro que el código pasa a LIFEsim. `Fp/Fs` es otra cantidad: compara el flujo del planeta con el de la estrella. El script POSEIDON puede guardar ambas, pero la interfaz con LIFEsim clásico de este proyecto usa `Fp_obs`.

### S/N por bin

Un **bin** es una franja de longitud de onda que el instrumento distingue. Para cada bin, LIFEsim devuelve una razón señal/ruido:

```text
SNR_i = señal_i / incertidumbre_i
```

El vector de S/N tiene un valor por longitud de onda. El S/N indica cuánto sobresale la señal modelada respecto de la incertidumbre esperada bajo esa configuración.

### Incertidumbre `sigma`

`σ_i` es la incertidumbre de un sigma asociada con el bin `i`. En este proyecto el wrapper recupera `σ_i` a partir del flujo binado y el S/N:

```text
sigma_i = flujo_binado_i / SNR_i
```

Luego el generador convierte esta incertidumbre de unidades fotónicas a unidades de energía para escribir el archivo que lee POSEIDON.

### Contrafactual molecular

Para estimar la contribución de una molécula se compara el espectro completo con otro forward donde esa molécula se reinicia al valor de referencia A0:

```text
DeltaF_i = F_i(escenario completo) - F_i(molécula reiniciada a A0)
```

Esta diferencia permite preguntar cuánto cambia la señal en las bandas moleculares. Es un diagnóstico de contribución espectral; por sí solo no es una prueba estadística de detección.

## 3. La escena LIFE Proxima que usa el proyecto

La configuración clásica Proxima sigue el ancla adoptada por el proyecto para LIFE X:

| Parámetro | Valor usado | Para qué sirve |
|---|---:|---|
| Resolución espectral `R` | 20 | Define el ancho de los bins; da 31 bins entre 4 y 18.5 micras |
| Rango | 4–18.5 µm | Intervalo espectral simulado |
| Diámetro del colector | 2 m | Controla el área colectora |
| Temperatura estelar | 3050 K | Parámetro estelar de la escena |
| Radio estelar | 0.14 radios solares | Escala el flujo estelar |
| Distancia | 1.30 pc | Geometría del flujo recibido |
| Exozodi | 3 zodis | Polvo alrededor del sistema |
| Separación angular | Aproximadamente 0.0373 segundos de arco | Separación planeta–estrella proyectada |
| Tiempo de referencia del S/N | 10 h | Punto de referencia guardado por el análisis |

El código parte del escenario de instrumento `baseline` de LIFEsim y fija manualmente resolución, diámetro y rango espectral. Después conecta los módulos de transmisión, fuga estelar, zodi local y exozodi.

La configuración se arma en `Thermal_Emission_Spectroscopy/scripts/run_proxima_life_snr.py` y `Thermal_Emission_Spectroscopy/scripts/make_life_datasets.py`. Los valores del objetivo también están en `validate_proxima_life_scene.py`. La validación del proyecto comparó el ancla LIFE X con la escena implementada; los detalles están en `docs/life_proxima_a3_500h_lifesim_direct_validation_2026-08-31.md`.

### Cómo se relaciona este ejemplo con LIFE X y LIFE XII

[LIFE X, de Carrión-González et al.](https://doi.org/10.1051/0004-6361/202347027) estudia la detectabilidad de exoplanetas conocidos y sirve aquí como ancla para la escena Proxima: el artículo estima S/N 170 en 10 horas para Proxima Centauri b bajo su configuración de referencia. La validación del repositorio obtuvo 166.5 para la escena implementada. El proyecto conserva esa calibración y la combina con perfiles atmosféricos VULCAN propios de A0–A3.

[LIFE XII](https://doi.org/10.3847/1538-3881/ad1f4b) estudia detectabilidad de moléculas de interés astrobiológico con LIFE. Ayuda a entender por qué se evalúan señales moleculares y tiempos de integración. Sus resultados y los de ExoFarm son comparables solo después de alinear objetivo, espectro, atmósfera, resolución, escena, ruido, definición de S/N y método de retrieval.

Para estudiar con más detalle la etapa de observación y extracción, consulta también [LIFE II](https://arxiv.org/abs/2203.00471), que presenta la simulación de señal y la extracción en observaciones de una época. Las tres referencias ayudan a ubicar la pregunta científica; el código local documenta los supuestos concretos usados en este proyecto.

## 4. Recorrido por el código, paso a paso

### Paso 1: preparar el espectro de emisión planetaria

`run_proxima_forward.py` lee los perfiles PT y químicos exportados desde VULCAN, construye el modelo de emisión de POSEIDON y guarda dos productos:

- `Fp/Fs`: razón de flujos;
- `Fp_obs`: flujo planetario directo recibido a la distancia del sistema, en `W m^-2 m^-1`.

Los archivos sin ruido quedan en:

```text
Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/forward_emission/
```

Cada escenario tiene un archivo `A0_emission.npz`, `A1_emission.npz`, etc. Allí se guardan la longitud de onda y el flujo planetario. Esos `.npz` son la señal atmosférica previa a la observación LIFE.

### Paso 2: convertir energía en número de fotones

POSEIDON entrega energía por área, tiempo y longitud de onda. El conteo de fotones se calcula dividiendo por la energía de un fotón:

```text
E_foton = h c / lambda
F_fotones = Fp_obs / E_foton
          = Fp_obs lambda / (h c)
```

Aquí `h` es la constante de Planck, `c` es la velocidad de la luz y `lambda` debe estar en metros para que las unidades queden correctas.

El helper `fp_obs_to_photon_flux()` de `life_scene_classic.py` hace esta conversión. El wrapper entrega a LIFEsim la longitud de onda en metros y el flujo de fotones como `astropy.Quantity`.

### Paso 3: crear LIFEsim sin interfaz gráfica

El wrapper `LifeSceneClassic` realiza por código las acciones básicas que también podrían configurarse desde una interfaz:

1. crea `lifesim.Bus()`, el contenedor común de datos y opciones;
2. activa las opciones `baseline`;
3. fija manualmente resolución, diámetro y rango;
4. crea el módulo `Instrument`;
5. añade `TransmissionMap`, `PhotonNoiseStar`, `PhotonNoiseLocalzodi` y `PhotonNoiseExozodi`;
6. conecta los módulos al instrumento;
7. aplica las opciones y guarda los centros de los bins LIFE.

El concepto del **Bus** es importante: mantiene una configuración compartida y conecta módulos especializados. La documentación oficial explica el diseño del Bus y los módulos en la [arquitectura de LIFEsim](https://lifesim.readthedocs.io/en/latest/architecture.html).

### Paso 4: pedir la observación a LIFEsim

El método `observe()` toma tres argumentos esenciales:

```python
resultado = escena.observe(
    wl_um,
    Fp_obs_W_m2_m,
    integration_time_s,
)
```

El tiempo se pasa en segundos; para 10 horas se usa `10 * 3600`.

Puedes probar la llamada directamente desde una consola Python. Este ejemplo solo lee el forward A3 y calcula la observación en memoria; no escribe productos:

```bash
cd Thermal_Emission_Spectroscopy/scripts
python
```

```python
import numpy as np
from run_proxima_life_snr import proxima_scene

scene = proxima_scene()
forward = np.load(
    "../outputs/life_proxima_b_earthlike_v1/forward_emission/A3_emission.npz"
)
obs = scene.observe(
    forward["wl_um"],
    forward["Fp_obs_W_m2_m"],
    10 * 3600,
)

print(obs.keys())
print(obs["wl_bins_um"].shape)       # 31 bins
print(obs["snr_per_bin"][:5])       # primeros cinco S/N
print(obs["sigma_ph"][:5])          # primeras cinco sigmas, en fotones
```

Al terminar la consola escribe `exit()`. Cambia `10 * 3600` por el tiempo deseado en segundos. Esta prueba calcula sigma/SNR; el generador de datasets es quien añade la realización aleatoria.

Por dentro, el wrapper:

1. transforma `Fp_obs` de energía a fotones;
2. llama `Instrument.get_spectrum(...)` con la estrella, la geometría, el exozodi, la separación angular, el espectro planetario y el tiempo;
3. recibe el S/N por bin, el flujo y el ruido calculados por LIFEsim;
4. rebina el flujo planetario a la malla LIFE;
5. calcula `sigma = flujo_binado / SNR`;
6. devuelve los vectores en un diccionario de Python.

El diccionario que retorna incluye:

| Clave | Qué contiene |
|---|---|
| `wl_bins_um` | Centros de los bins LIFE, en micras |
| `snr_per_bin` | S/N esperado en cada bin |
| `flux_binned_ph` | Flujo planetario binado, en unidades fotónicas |
| `sigma_ph` | Incertidumbre de un sigma por bin, también fotónica |
| `integration_time_s` | Tiempo de integración usado |

Por eso la llamada a LIFEsim no devuelve únicamente “un array de S/N”. Devuelve varios vectores útiles para preparar la observación sintética. En el wrapper actual, el resultado `noise_ph` que devuelve internamente LIFEsim no se guarda en el diccionario: el código calcula `sigma_ph` mediante el S/N y el flujo binado.

### Paso 5: obtener S/N de moléculas, además del S/N del continuo

`run_proxima_life_snr.py` observa con LIFEsim los cuatro espectros completos A0–A3 a 10 horas. También carga los forwards contrafactuales de las especies, los rebina a la misma malla y calcula sus diferencias respecto del espectro completo.

Para una banda molecular con errores diagonales, el código suma en cuadratura:

```text
SNR_banda = sqrt( suma_i [ (DeltaF_i / sigma_i)^2 ] )
```

El script calcula tanto:

- el S/N integrado de cada banda;
- el bin individual con mayor `abs(DeltaF_i / sigma_i)`;
- el escalado aproximado del S/N con el tiempo de integración.

El S/N de un pico y el S/N integrado de una banda responden preguntas distintas. El pico describe el bin más contrastado; la suma de banda combina los bins seleccionados bajo la hipótesis de errores diagonales.

Los productos de esta etapa son:

```text
outputs/life_proxima_b_earthlike_v1/lifesim/life_classic_binned_products.npz
outputs/life_proxima_b_earthlike_v1/tables/life_classic_snr_table.csv
```

El primero guarda vectores por bin, como flujo, sigma y S/N. El CSV organiza resultados por escenario, molécula y banda.

### Paso 6: pasar de una incertidumbre esperada a una observación sintética concreta

Una predicción de sigma todavía no es un dato observado. `make_life_datasets.py` construye el espectro sintético que luego puede leer POSEIDON:

```text
F_observado_i = F_modelo_i + epsilon_i sigma_i
```

`epsilon_i` es una extracción normal estándar generada con una semilla registrada. El índice JSON guarda la semilla de cada archivo, el escenario, las horas y el número de bins.

El archivo `.dat` lleva cuatro columnas:

| Columna | Contenido | Unidad |
|---|---|---|
| 1 | longitud de onda | µm |
| 2 | semiancho del bin | µm |
| 3 | flujo planetario con ruido | `W m^-2 m^-1` |
| 4 | sigma del flujo | `W m^-2 m^-1` |

La conversión de sigma desde fotones a energía usa la relación inversa:

```text
sigma_F = sigma_fotones h c / lambda
```

Este archivo contiene la señal, una realización concreta de ruido y su incertidumbre por bin. El script registra una semilla por dataset; con otra semilla el espectro observado cambia aunque el modelo y sigma permanezcan iguales.

### Paso 7: retrieval posterior con POSEIDON

`run_life_retrieval.py` carga las cuatro columnas con `spectrum_unit="Fp"` y `bin_width="half"`. POSEIDON genera modelos y busca los parámetros atmosféricos compatibles con el espectro y sus sigmas.

El retrieval añade una pregunta distinta: además del ruido, ¿qué pasa cuando varios parámetros pueden imitarse entre sí? Por ejemplo, temperatura, radio y abundancias moleculares pueden compensar partes de la señal. En el análisis Proxima actual, la comparación focal usa A1 y A3 a 1, 10 y 100 horas con una configuración común. La matriz amplia A0–A3 a 10 y 240 horas se conserva como archivo de referencia. La [nota de la campaña focal](life_proxima_a1_a3_1_10_100h_official_retrieval_campaign_2026-10-01.md) documenta la configuración vigente.

> [!important] Serie focal vigente
> Los seis retrievals oficiales son A1/A3 a 1/10/100 h, con 31 bins, ruido diagonal y una realización de ruido por dataset. La entrada de 1 h se generó escalando sigma desde 10 h y tiene un índice separado; los datasets de 10 h A1/A3 se reutilizaron y los de 100 h usan realizaciones propias. El ejemplo de práctica de esta guía crea nuevas realizaciones con nombres separados: sirve para aprender el flujo, no reproduce los datasets oficiales.

## 5. Cómo ejecutar los scripts desde consola

Estos comandos muestran el flujo del proyecto. La instalación LIFE clásica registrada para el proyecto usa LIFEsim 0.2.32 y SpectRes 2.1.1 modificado. Los detalles de instalación de LIFEsim y SpectRes cambian con el tiempo; consulta la [página oficial de instalación](https://lifesim.readthedocs.io/en/latest/installation.html) y confirma que los imports se ejecutan en el mismo entorno que usarás para correr los scripts.

### 5.1 Confirmar Python y los paquetes

En Ubuntu/WSL, desde la raíz del checkout:

```bash
conda activate POSEIDON
which python
python -c "from importlib.metadata import version; import lifesim, spectres; print('LIFEsim', version('lifesim')); print('SpectRes', version('spectres'))"
```

El nombre del entorno se mantiene como `POSEIDON`; la ruta física de Conda ha variado entre ejecuciones. Comprueba `which python` y evita mezclar paquetes de dos entornos distintos. Si vas a reconstruir el forward POSEIDON, comprueba además las variables de datos `POSEIDON_input_data` y `PYSYN_CDBS` que use ese entorno.

### 5.2 Recalcular el forward de emisión

Solo corre esto cuando quieras reconstruir los forwards y hayas comprobado que los perfiles PT/químicos requeridos existen:

```bash
python Thermal_Emission_Spectroscopy/scripts/run_proxima_forward.py \
  --scenarios A0 A1 A2 A3
```

El runner tiene rutas de salida fijas. Reescribe el manifiesto y los `A*_emission.npz` de los escenarios indicados. Si solo quieres aprender cómo se usa LIFEsim y los forwards ya existen, puedes saltarte este paso.

### 5.3 Recalcular la observación clásica y la tabla de S/N

```bash
python Thermal_Emission_Spectroscopy/scripts/run_proxima_life_snr.py
```

Esta llamada usa directamente LIFEsim a 10 horas y guarda de nuevo `life_classic_binned_products.npz` y `life_classic_snr_table.csv`. Revisa la carpeta de salida antes de correrla porque esos nombres son fijos.

### 5.4 Crear datasets de práctica separados

El siguiente ejemplo usa los forwards y los productos de S/N guardados. Escala sigma desde 10 h y genera nuevas realizaciones de ruido para A1/A3 a 1, 10 y 100 h:

```bash
python Thermal_Emission_Spectroscopy/scripts/make_life_datasets.py \
  --campaign proxima \
  --scenarios A1 A3 \
  --hours 1 10 100 \
  --seed 20261002 \
  --name-suffix _tutorial_20261002 \
  --index-output /tmp/dataset_index_A1_A3_tutorial_20261002.json \
  --index-classification "practica; fuera de la comparacion oficial"
```

Los seis `.dat` se escriben en `outputs/life_proxima_b_earthlike_v1/life_data/` con el sufijo `tutorial_20261002`; el índice va a `/tmp`. El sufijo separa los nombres del conjunto focal. Si repites el comando, verifica primero si ya existen archivos con ese sufijo: el generador puede reescribirlos.

Este ejemplo no vuelve a llamar a LIFEsim. Usa `sigma(10 h)` guardado y aplica:

```text
sigma(t) = sigma(10 h) sqrt(10 h / t)
```

Esa ley se comprobó en el proyecto frente a llamadas directas de LIFEsim clásico. El mismo script permite solicitar una observación directa con `--direct-lifesim`; en ese caso requiere LIFEsim instalado en el entorno activo. Cada método queda registrado en el índice que escribe el generador.

### 5.5 Inspeccionar un `.dat` sin interfaz

Por ejemplo, para revisar un archivo desde Python:

```python
import numpy as np

path = "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A1_1h_tutorial_20261002.dat"
data = np.loadtxt(path, skiprows=1)

print(data.shape)              # se esperan 31 filas y 4 columnas
print(data[:3])                # primeras longitudes, flujos y sigmas
print(np.isfinite(data).all()) # True si todos los números son finitos
print((data[:, 3] > 0).all())  # True si sigma es positivo en todos los bins
```

El nombre exacto depende del sufijo pasado a `--name-suffix`. Inspeccionar el archivo así es una comprobación numérica básica; todavía conviene graficar flujo y barras de error cuando vayas a interpretar el espectro.

### 5.6 Entregar un dataset propio a POSEIDON

El runner acepta un archivo particular mediante `--dataset-file`. `--setup-only` valida datos, modelo y priors, y omite MultiNest:

```bash
python Thermal_Emission_Spectroscopy/scripts/run_life_retrieval.py \
  --campaign proxima \
  --scenario A1 \
  --hours 1 \
  --dataset-file Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A1_1h_tutorial_20261002.dat \
  --output-tag _tutorial_20261002 \
  --x-profile isochem \
  --error-inflation none \
  --surface-pressure-mode fixed-black \
  --include-o2 \
  --R 10000 \
  --setup-only
```

POSEIDON solo lee el dataset si las rutas de opacidades y grillas requeridas están configuradas. La ejecución con `--setup-only` evita el muestreo de MultiNest. Quita esa opción únicamente cuando tengas claro el coste, los archivos de salida y la configuración científica del retrieval. Esta llamada de práctica no forma parte de la campaña focal oficial.

## 6. Qué significa y qué no significa el S/N

El S/N que calcula LIFEsim clásico responde a una pregunta acotada:

> Dado este espectro planetario, esta escena estelar/planetaria y este tiempo de integración, ¿qué relación señal/ruido por bin predice el modelo clásico de LIFE?

Para traducirlo a una afirmación de detectabilidad todavía se necesita evaluar, entre otras cosas, si los errores representan bien al instrumento real, si las bandas se distinguen de las de otras moléculas, si el retrieval representa los perfiles verticales de verdad, cómo varían los resultados entre realizaciones de ruido y si un modelo con la molécula explica los datos mejor que un modelo comparable sin ella.

El S/N de banda del proyecto usa sigma diagonal. La cadena clásica incluye los fondos y el ruido fotónico de su escena, pero no la evolución temporal de inestabilidades instrumentales ni una covarianza espectral instrumental completa. La documentación de [LIFEsimMC explica cuándo usar la versión Monte Carlo y su diferencia con LIFEsim clásico](https://lifesimmc.readthedocs.io/en/latest/when_to_use.html). Por eso el proyecto presenta la rama clásica como una simulación de referencia/sensibilidad, con límites explícitos.

## 7. Preguntas frecuentes

### ¿LIFEsim devuelve un espectro ruidoso?

La llamada `observe()` del wrapper devuelve flujo binado, S/N y sigma esperada por bin. La realización ruidosa se genera después en `make_life_datasets.py` usando la sigma y una semilla aleatoria. Así se distingue el cálculo instrumental esperado de una observación sintética concreta.

### ¿El cálculo depende de la estrella?

Sí. En esta interfaz la llamada incluye temperatura estelar, radio, distancia, latitud eclíptica y separación angular, además de exozodi. Estos valores afectan la escena de observación y el ruido esperado.

### ¿Se entrega a LIFEsim el espectro MUSCLES de Proxima?

La función de observación de este proyecto recibe el flujo planetario de POSEIDON y los parámetros escalares de la estrella. No recibe un arreglo de SED estelar MUSCLES. La SED MUSCLES se usa antes, en la rama VULCAN, para modelar la fotoquímica bajo el ambiente ultravioleta de Proxima. Esa química contribuye al espectro planetario que POSEIDON calcula; la configuración clásica de fuga estelar usa los parámetros estelares de la escena LIFEsim.

### ¿Entonces para qué sirve POSEIDON después?

LIFEsim calcula ruido/SNR a nivel de observación simulada. POSEIDON trata el archivo con flujo y sigma como datos y ajusta modelos atmosféricos. El retrieval permite estudiar degeneraciones entre abundancias, temperatura y otros parámetros.

### ¿S/N alto equivale a detección de vida?

El S/N caracteriza una diferencia espectral bajo una escena y un modelo de ruido definidos. La detección de una molécula requiere contrastes inferenciales adecuados. La detección de vida requeriría además una interpretación astrobiológica de la molécula, su contexto y explicaciones abióticas. Esta rama no calcula por sí misma una probabilidad de vida.

### ¿El flujo representa a Proxima b real?

No. La etiqueta del caso es `life_proxima_b_earthlike`: una atmósfera de tipo terrestre controlada bajo el ambiente de Proxima. El proyecto no dispone aquí de una atmósfera medida de Proxima b.

## 8. Mapa del código y del material para profundizar

Las rutas de esta tabla son del repositorio ExoFarm. Si guardas esta nota en otro vault, los enlaces externos de la sección siguiente seguirán disponibles; las rutas locales requieren abrir el checkout del proyecto.

| Ruta dentro del repositorio | Qué estudiar allí |
|---|---|
| `Thermal_Emission_Spectroscopy/scripts/emission_forward.py` | Parámetros de los objetivos, lectura de perfiles y forward POSEIDON |
| `Thermal_Emission_Spectroscopy/scripts/run_proxima_forward.py` | Orquestación de los forwards Proxima |
| `Thermal_Emission_Spectroscopy/scripts/life_scene_classic.py` | Conversión energía/fotones, Bus, módulos, llamada `get_spectrum()` y resultado `observe()` |
| `Thermal_Emission_Spectroscopy/scripts/validate_proxima_life_scene.py` | Parámetros y calibración de la escena LIFE Proxima |
| `Thermal_Emission_Spectroscopy/scripts/run_proxima_life_snr.py` | S/N por escenario y molécula a 10 h |
| `Thermal_Emission_Spectroscopy/scripts/make_life_datasets.py` | Escalado temporal, semilla, realización gaussiana y escritura `.dat` |
| `Thermal_Emission_Spectroscopy/scripts/run_life_retrieval.py` | Lectura del `.dat`, configuración del modelo y retrieval POSEIDON |
| `docs/life_proxima_lifesim_noise_scaling_2026-08-31.md` | Validación de sigma directa frente a escala temporal |
| `docs/life_proxima_a1_a3_1_10_100h_official_retrieval_campaign_2026-10-01.md` | Estado de la comparación focal vigente |

## 9. Enlaces para continuar aprendiendo

1. [Documentación oficial de LIFEsim](https://lifesim.readthedocs.io/en/latest/) — visión general del simulador.
2. [Arquitectura de LIFEsim](https://lifesim.readthedocs.io/en/latest/architecture.html) — Bus, módulos y conexiones.
3. [Ejemplos oficiales en Python](https://lifesim.readthedocs.io/en/latest/example.html#simulating-the-search-phase) — creación de `Bus`, instrumento y fuentes de ruido desde código.
4. [Instalación oficial de LIFEsim](https://lifesim.readthedocs.io/en/latest/installation.html) — incluye la dependencia de la variante de SpectRes que necesita LIFEsim.
5. [Código fuente de LIFEsim](https://github.com/fdannert/LIFEsim) y [código de SpectRes usado con LIFEsim](https://github.com/fdannert/SpectRes).
6. [POSEIDON: modelo de emisión](https://poseidon-retrievals.readthedocs.io/en/latest/content/notebooks/emission_basic.html) — contexto del forward que produce `Fp`.
7. [Cuándo usar LIFEsimMC](https://lifesimmc.readthedocs.io/en/latest/when_to_use.html) y [tutorial de una observación de época](https://lifesimmc.readthedocs.io/en/latest/tutorials/seo.html) — comparación de la rama clásica con ruido instrumental y extracción más completa.
8. [LIFE II](https://arxiv.org/abs/2203.00471), [LIFE X](https://arxiv.org/abs/2308.09646) y [LIFE XII](https://doi.org/10.3847/1538-3881/ad1f4b) — artículos para seguir la aplicación científica de LIFEsim en observaciones individuales, objetivos conocidos y firmas moleculares.

## 10. Resumen de bolsillo

1. VULCAN produce perfiles atmosféricos.
2. POSEIDON transforma esos perfiles en un espectro planetario de emisión `Fp_obs`.
3. `life_scene_classic.py` convierte `Fp_obs` a fotones y llama el instrumento clásico LIFE.
4. LIFEsim devuelve bins, S/N esperado y ruido/sigma para el tiempo definido.
5. `make_life_datasets.py` puede escalar sigma o volver a observar directamente; luego añade una realización aleatoria y guarda flujo más sigma.
6. POSEIDON hace el retrieval de ese `.dat`.
7. El S/N ayuda a planear y diagnosticar la observación. La interpretación científica necesita retrieval, comprobaciones de degeneración y una descripción explícita de los límites del modelo de ruido.
