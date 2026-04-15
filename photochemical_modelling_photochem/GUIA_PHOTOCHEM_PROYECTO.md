# Guia de uso de `photochem` en este proyecto

## 1. Para que existe este modulo

`photochemical_modelling_photochem/` es la version del Stage I quimico del proyecto hecha con `photochem`, como alternativa al flujo historico con VULCAN.

La idea no es rehacer toda la logica cientifica desde cero, sino:

- conservar la comparabilidad con los casos `A0-A3` ya definidos en el repo
- separar con mas claridad estos cuatro bloques de entrada que `photochem` usa de forma natural:
  - mecanismo quimico
  - archivo de settings / boundary conditions
  - espectro estelar
  - atmosfera inicial
- dejar el tipo estelar separado del escenario quimico

En nuestro caso:

- el escenario (`A0`, `A1`, `A2`, `A3`) cambia sobre todo las condiciones de frontera de superficie
- la estrella (`earth_sun`, `earth_trappist`) cambia el espectro incidente y el angulo cenital efectivo
- el planeta del run ahora tambien importa de forma explicita, sobre todo para TRAPPIST-1e, porque masa, radio, gravedad y clima ya no se heredan de la Tierra

## 2. Estructura real del modulo

La fuente de verdad del modulo no esta en un solo YAML, sino repartida asi:

- `Config/catalog.json`
  - define constantes globales del modelo
  - define estrellas
  - define escenarios
  - define runs concretos
- `Config/Templates/settings_base.yaml`
  - template base terrestre de `photochem`
  - luego se modifica en tiempo de preparacion para cada run
- `Scripts/Simulation/common.py`
  - es el archivo clave
  - ahi esta la logica que traduce el catalogo en archivos concretos
- `Scripts/Simulation/prepare_photochem_inputs.py`
  - prepara mecanismo, espectros, settings y atmosfera inicial
- `Scripts/Simulation/run_case.py`
  - inicializa `photochem.EvoAtmosphere`, mueve el TOA y busca steady state
- `Scripts/Analysis/*.py`
  - resumen especies superficiales y exportacion a `Transmission_Spectroscopy/`

Los productos generados no se escriben en `Config/`, sino en:

- `Results/Prepared/mechanism/`
- `Results/Prepared/stellar_flux/`
- `Results/Prepared/settings/`
- `Results/Prepared/initial_atmospheres/`
- `Results/Outputs/`
- `Results/Summaries/`
- `Results/Logs/`

## 3. Que necesita `photochem` para correr

En este proyecto cada corrida termina usando exactamente estos cuatro insumos:

1. `mechanism_file`
2. `settings_file`
3. `flux_file`
4. `initial_atmosphere_file`

Eso es justo lo que recibe `EvoAtmosphere(...)` en `Scripts/Simulation/run_case.py`.

Conceptualmente:

1. el mecanismo dice que especies y reacciones existen
2. el settings file dice como esta armado el planeta y sus boundary conditions
3. el flux file dice que radiacion llega desde la estrella
4. la atmosfera inicial da el primer guess vertical de composicion, temperatura, densidad y mezcla turbulenta

## 4. Instalacion recomendada

### 4.1. Importante en Windows

La documentacion local del workshop de `photochem` recomienda usar WSL en Windows. Eso cuadra bien con este repo, porque varios outputs y rutas historicas ya aparecen en formato tipo `/mnt/c/...`.

### 4.2. Instalacion base

La guia local del workshop en `.codex_tmp/photochem_workshop/2_Installation/README.md` recomienda:

```bash
conda create -n workshop -c conda-forge photochem=0.6.2 matplotlib jupyter
conda activate workshop
python -c "import photochem; print('Photochem version:', photochem.__version__)"
```

### 4.3. Estado actual de este entorno

En el entorno donde revise el repo, `photochem` no esta instalado actualmente.

Antes de correr cualquier script de este modulo conviene verificar:

```bash
python -c "import photochem; print(photochem.__version__)"
```

Si eso falla, `prepare_photochem_inputs.py`, `run_case.py` y `run_official_modern_earth.py` tambien van a fallar.

## 5. Flujo de trabajo correcto en este proyecto

### 5.1. Paso 1: preparar insumos

Desde `photochemical_modelling_photochem/Scripts/Simulation/`:

```bash
python prepare_photochem_inputs.py
```

O para un caso particular:

```bash
python prepare_photochem_inputs.py Earth_A1_Current
```

Este paso hace cuatro cosas:

1. convierte la red de VULCAN a YAML compatible con `photochem`
2. genera o descarga el espectro estelar
3. construye el settings final del run
4. construye la atmosfera inicial del run

#### 5.1.1. Conversion del mecanismo

`prepare_mechanism()` llama a:

```python
photochem.utils.vulcan2yaml(...)
```

usando:

- `VULCAN/thermo/SNCHO_full_photo_network.txt`
- `VULCAN/thermo/`

El resultado queda en:

- `Results/Prepared/mechanism/SNCHO_full_photo_network.yaml`

Despues el script limpia reacciones identidad del tipo:

- `A <=> A`
- `A => A`

Eso se hace en `sanitize_mechanism_file()`.

#### 5.1.2. Generacion del espectro estelar

`prepare_stellar_flux()` usa el bloque `stars` del catalogo.

Actualmente hay dos estrategias:

- `solar_spectrum`
  - para `earth_sun`
  - usa `photochem.utils.stars.solar_spectrum`
- `local_surface_spectrum`
  - para `earth_trappist`
  - usa el archivo local `VULCAN/atm/stellar_flux/TRAPPIST1_surface.txt`
  - ese archivo esta en flujo a nivel de la estrella, asi que durante la preparacion se reescala geometricamente hasta obtener el flujo en TRAPPIST-1e, que es lo que `photochem` y `clima` necesitan

Esto es importante:

- la primera vez puede requerir acceso a red
- el escenario quimico no toca esta parte
- si quieres una estrella nueva, casi siempre el cambio empieza en `catalog.json`, no en los scripts

#### 5.1.3. Construccion del settings por run

`build_settings_for_run()` hace esto:

1. carga `Config/Templates/settings_base.yaml`
2. sobreescribe constantes globales desde `catalog.json`
3. mete el `solar-zenith-angle` segun la estrella
4. lee el archivo de BC del escenario
5. mezcla esas BC con las BC base
6. guarda el YAML final en `Results/Prepared/settings/`

#### 5.1.4. Construccion de la atmosfera inicial

`build_initial_atmosphere_for_run()` usa:

- `VULCAN/atm/atm_Earth_Jan_Kzz.txt`
  - como perfil de `P-T-Kzz`
- `Transmission_Spectroscopy/profiles/Earth_A1_Current_chem.txt`
  - como semilla quimica vertical si existe
- `fallback_initial_mixing_ratios`
  - como respaldo si falta la semilla o falta alguna especie

La atmosfera inicial final se escribe en:

- `Results/Prepared/initial_atmospheres/<run_id>_initial_atmosphere.txt`

### 5.2. Paso 2: correr un caso

```bash
python run_case.py Earth_A1_Current
```

Este script:

1. fuerza la preparacion del caso si hace falta
2. crea el objeto `EvoAtmosphere`
3. fija `pc.var.verbose = 0`
4. mueve la grilla vertical con `update_vertical_grid(...)`
5. llama `find_steady_state()`
6. exporta la atmosfera final
7. guarda un resumen JSON con especies trazadas y fluxes

El output principal queda en:

- `Results/Outputs/<run_id>_steady_state.txt`

Y el resumen en:

- `Results/Summaries/<run_id>_summary.json`

### 5.3. Paso 3: correr suites completas

Para los casos solares:

```bash
python run_parallel_earth.py
```

Para los casos tipo TRAPPIST:

```bash
python run_parallel_trappist.py
```

Estos scripts lanzan varios procesos y escriben logs en `Results/Logs/`.

### 5.4. Paso 4: productos de analisis

Resumen de mixing ratios superficiales:

```bash
cd ../Analysis
python extract_surface_values.py
```

Exportacion al formato usado por la etapa de espectroscopia:

```bash
python export_transmission_profiles.py
```

Eso actualiza archivos en:

- `Transmission_Spectroscopy/profiles/*_chem.txt`
- `Transmission_Spectroscopy/profiles/*_PT.txt`

## 6. Que significa cada bloque del `catalog.json`

### 6.1. Bloque `model`

Este bloque contiene decisiones globales del modulo.

- `planet_mass_g`
  - masa planetaria en gramos
- `planet_radius_cm`
  - radio planetario en cm
- `gravity_cms2`
  - gravedad usada para integrar altura desde el perfil de presion
- `surface_albedo`
  - albedo superficial que termina en el settings final
- `number_of_layers`
  - numero de capas de la grilla del modelo
- `target_toa_pressure_bar`
  - presion objetivo en el tope de la atmosfera
  - luego `run_case.py` la convierte a unidades CGS multiplicando por `1e6`
- `reference_mean_molecular_weight_amu`
  - masa molecular media de referencia para reconstruir altura en la atmosfera inicial
- `seed_floor_mixing_ratio`
  - piso numerico para evitar ceros exactos en especies
- `particle_radius_cm`
  - radio inicial asignado a aerosoles / particulas
- `vulcan_network_file`
  - archivo de red original de VULCAN
- `vulcan_thermo_dir`
  - carpeta termodinamica / fotoquimica que `vulcan2yaml` necesita
- `pressure_temperature_kzz_file`
  - perfil vertical base de `P-T-Kzz`
- `seed_chemistry_template`
  - perfil quimico semilla usado para interpolar composiciones iniciales
- `tracked_species`
  - especies que despues se guardan en el resumen JSON
- `fallback_initial_mixing_ratios`
  - valores iniciales de respaldo especie por especie

### 6.2. Bloque `stars`

Cada estrella define:

- `label`
  - nombre legible
- `strategy`
  - como se construye el espectro
- `stellar_flux_w_m2`
  - insolacion objetivo
- `age_ga`
  - para el caso solar
- `hazmat_star_name`, `hazmat_model`
  - para la libreria HAZMAT
- `solar_zenith_angle_deg`
  - se inyecta en el settings final
- `output_file`
  - nombre del archivo de flujo preparado

En este proyecto, cambiar de estrella no deberia requerir editar scripts salvo que inventemos una estrategia nueva.

### 6.3. Bloque `scenarios`

Cada escenario apunta sobre todo a un archivo:

- `boundary_condition_file`

Actualmente esos archivos vienen de:

- `Photochemical_Modeling/Config/Boundary_Conditions/`

O sea: estamos reutilizando directamente las condiciones de frontera del flujo VULCAN.

### 6.4. Bloque `runs`

Aqui se define cada corrida concreta.

Cada run amarra:

- un `id`
- un `profile_stem`
- una estrella
- un escenario

Ejemplo mental:

- `Earth_A2_Moderate` = estrella solar + escenario A2
- `Trappist_A2_Moderate` = estrella TRAPPIST + escenario A2

## 7. Como se construye el `settings.yaml` final

El template base actual esta inspirado en el ejemplo `ModernEarth` oficial de `photochem`.

Los bloques mas importantes son:

### 7.1. `atmosphere-grid`

- `bottom`
  - base de la atmosfera
- `top: atmospherefile`
  - aqui el template le dice a `photochem` que use el archivo de atmosfera inicial
- `number-of-layers`
  - lo pisa el valor del catalogo

### 7.2. `planet`

Aqui van propiedades fisicas y submodelos:

- masa
- radio
- albedo
- angulo cenital solar
- escape de hidrogeno
- tratamiento del agua

En nuestro template:

- `hydrogen-escape.type = diffusion limited`
- `fix-water-in-troposphere = false`
- `relative-humidity = manabe`
- `gas-rainout = true`
- `water-condensation = false`

Eso significa que el proyecto esta usando una configuracion bastante terrestre / oxidante como base, no una completamente libre o exotica.

### 7.3. `particles`

El template base define:

- `H2Oaer`

Y luego la atmosfera inicial puede agregar columnas de particulas segun el mecanismo preparado.

### 7.4. `boundary-conditions`

Esta es la parte mas sensible del modulo.

La logica del proyecto es:

1. tomar unas BC base del template
2. leer el archivo del escenario
3. traducirlo a sintaxis `photochem`
4. hacer merge por nombre de especie

Eso permite mantener unas BC "estandar" para especies cortas o de deposicion comun, y al mismo tiempo reemplazar otras via escenario.

## 8. Formato de los archivos de condiciones de frontera del proyecto

Los archivos historicos se ven como:

```text
#species flux [cm-2 s-1]   v_dep [cm s-1]
CO   3.7e11   0.03
CH4  1.6e+11  0.
NO   1.3e10   0.001
...
```

El parser de `common.py` interpreta cada fila asi:

- si `flux > 0` y `vdep > 0`
  - crea `type: vdep + dist flux`
- si `flux > 0` y `vdep = 0`
  - crea `type: flux`
- si `flux = 0` y `vdep > 0`
  - crea `type: vdep`
- si ambos son cero
  - la especie no agrega BC explicita

Tambien:

- ignora comentarios
- ignora especies que no existan en el mecanismo permitido
- si una especie aparece repetida, se queda con la de mayor `flux`

### 8.1. Consecuencia importante

El archivo de escenario no entra "tal cual" al YAML final. Entra despues de un mapeo de tipos.

Por eso, cuando algo no aparezca en el `*_settings.yaml`, lo primero que hay que revisar no es `photochem`, sino la traduccion que hace `parse_boundary_conditions_file()`.

## 9. Atmosfera inicial: que contiene y como se arma

El archivo de atmosfera inicial preparado tiene una cabecera tipo:

```text
alt press den temp eddy ...
```

y luego columnas para:

- todas las especies del mecanismo
- todas las particulas
- radios de particula `<particle>_r`

### 9.1. De donde sale cada columna base

- `press`, `temp`, `eddy`
  - vienen del perfil `VULCAN/atm/atm_Earth_Jan_Kzz.txt`
- `alt`
  - no viene del archivo original
  - se reconstruye integrando alturas con gravedad fija y masa molecular media de referencia
- abundancias quimicas
  - se interpolan desde la semilla quimica si existe
  - si no, se rellenan con `fallback_initial_mixing_ratios`
- particulas
  - arrancan en el piso numerico
- radios de particula
  - arrancan todos con `particle_radius_cm`

### 9.2. Implicacion cientifica

La atmosfera inicial ya no se arma igual para todos los runs.

En este momento:

- los casos de la Tierra siguen pudiendo usar el perfil `P-T-Kzz` y la semilla quimica historica
- los casos de TRAPPIST-1e pasan primero por `AdiabatClimate` para obtener un perfil radiativo-convectivo autoconsistente antes de la fotoquimica

Entonces, para TRAPPIST-1e, la temperatura inicial ya no viene de un perfil terrestre heredado, sino del paso de clima.

## 10. La corrida oficial de referencia

Existe un script util para comparar contra el ejemplo oficial:

```bash
python run_official_modern_earth.py
```

Eso corre el caso `ModernEarth` de la copia local de `photochem` en `.codex_tmp/photochem_repo/examples/ModernEarth/`.

Sirve para:

- verificar que `photochem` esta bien instalado
- comparar la estructura del ejemplo oficial con nuestro flujo
- tener un baseline externo

## 11. Como agregar una estrella nueva

El procedimiento correcto es:

1. agregar una entrada en `Config/catalog.json -> stars`
2. definir:
   - `label`
   - `strategy`
   - parametros propios de la estrategia
   - `solar_zenith_angle_deg`
   - `output_file`
3. crear runs nuevos que apunten a esa estrella
4. volver a correr `prepare_photochem_inputs.py`

Solo hace falta tocar Python si la estrella nueva requiere una estrategia que hoy no existe.

## 12. Como agregar un escenario quimico nuevo

Lo normal seria:

1. crear un archivo nuevo en `Photochemical_Modeling/Config/Boundary_Conditions/`
2. agregar una entrada en `catalog.json -> scenarios`
3. crear los runs correspondientes en `catalog.json -> runs`
4. preparar y correr

Lo importante es respetar el formato de columnas:

- especie
- flux
- `v_dep`

## 13. Como agregar un run nuevo

Es el cambio mas simple:

1. elegir una estrella existente
2. elegir un escenario existente
3. crear el run en `catalog.json -> runs`
4. ejecutar preparacion y corrida

Si no necesitas cambiar fisica global ni BC, no hace falta tocar nada mas.

## 14. Advertencias concretas del proyecto

Estas son las advertencias mas utiles que encontre revisando el codigo actual.

### 14.1. `photochem` no esta instalado en este entorno

Ahora mismo hay que instalarlo antes de ejecutar este modulo.

### 14.2. El helper de estrellas puede necesitar internet

La primera vez que se genera un espectro estelar con `photochem.utils.stars`, el script puede intentar descargar datos.

### 14.3. Ojo con `COS -> OCS`

En `Scripts/Simulation/common.py` existe hoy este alias:

```python
SPECIES_ALIASES = {
    "COS": "OCS",
    "H2SO4_l": None,
}
```

Pero el mecanismo preparado actual contiene `COS` como especie, no `OCS`.

Consecuencia practica:

- una BC escrita como `COS` en los archivos del escenario puede remapearse a `OCS`
- si `OCS` no existe en el mecanismo permitido, esa BC puede quedarse fuera del settings final

Eso merece revisarse en el codigo cuando se quiera usar seriamente el azufre-carbonilo en esta rama.

### 14.4. `H2SO4_l` se descarta a proposito

Ese alias a `None` hace que la especie se ignore durante la traduccion de BC.

No es un bug accidental: hoy es una decision explicita del parser.

### 14.5. El TOA se define en dos pasos

En el template aparece:

- `top: atmospherefile`

pero despues `run_case.py` hace:

```python
pc.update_vertical_grid(TOA_pressure=catalog["model"]["target_toa_pressure_bar"] * 1.0e6)
```

O sea:

- la atmosfera inicial define una grilla base
- luego la corrida mueve el tope de la atmosfera a la presion objetivo

Si el vertical grid final no coincide con lo esperado, hay que revisar ambos lugares.

### 14.6. La comparabilidad con VULCAN es buena, pero no exacta

Se reutilizan:

- la red de VULCAN
- el termodinamico / cross sections de VULCAN
- las BC `A0-A3`
- el perfil `P-T-Kzz`

Pero el solver y el formato de inputs son los de `photochem`.

Entonces este modulo es ideal para comparacion metodologica, no para asumir identidad numerica exacta con la rama VULCAN.

## 15. Ruta minima recomendada para trabajar

Si solo quieres correr y comparar casos:

1. instalar `photochem`
2. `python prepare_photochem_inputs.py`
3. `python run_parallel_earth.py`
4. `python run_parallel_trappist.py`
5. `cd ../Analysis`
6. `python extract_surface_values.py`
7. `python export_transmission_profiles.py`

Si quieres modificar ciencia:

1. decide si el cambio es de estrella, escenario o fisica global
2. cambia primero `catalog.json` si alcanza
3. toca `settings_base.yaml` solo si es una decision verdaderamente global
4. inspecciona siempre el `*_settings.yaml` generado antes de lanzar barridos grandes

## 16. Checklist rapido de depuracion

Si una corrida falla o sale rara, revisar en este orden:

1. `python -c "import photochem"`
2. que exista `Results/Prepared/mechanism/*.yaml`
3. que exista el flujo estelar preparado
4. que el `*_settings.yaml` tenga las especies esperadas
5. que el `*_initial_atmosphere.txt` tenga las columnas esperadas
6. que el `summary.json` marque `converged: true`
7. si el problema es de especies de azufre / `COS`, revisar el alias en `common.py`

## 17. Resumen corto

La forma correcta de pensar `photochem` en este proyecto es esta:

- `catalog.json` decide combinaciones fisicas y experimentales
- `prepare_photochem_inputs.py` convierte eso en archivos que `photochem` entiende
- `run_case.py` corre el solver
- `Analysis/` traduce los resultados al resto del pipeline

Si vas a tocar algo, normalmente conviene empezar por el catalogo y revisar los archivos preparados, no editar outputs a mano.

## 18. Actualizacion importante: TRAPPIST-1e y clima

Esta rama ya incorpora dos cambios conceptuales importantes.

### 18.1. El flujo estelar que usa `photochem` debe estar en el planeta

Para `photochem` y para `photochem.clima`, el archivo de flujo debe representar la irradiancia en el planeta.

En nuestro caso de TRAPPIST-1e:

- el espectro local que traemos del repo esta en `VULCAN/atm/stellar_flux/TRAPPIST1_surface.txt`
- ese archivo esta a nivel de la superficie estelar
- durante `prepare_photochem_inputs.py` ahora se reescala con el factor geometrico `(R_star / a)^2`
- el archivo preparado final `TRAPPIST1e_flux.txt` si queda en formato utilizable por `photochem`

Eso responde la duda clave del proyecto: si, para TRAPPIST-1e el flujo que entra al modelo tiene que ser el flujo en el planeta, no el flujo en la estrella.

### 18.2. El planeta ya no se trata como si fuera la Tierra

Los runs de TRAPPIST ahora apuntan explicitamente al planeta `trappist1e` en el catalogo.

Eso permite usar parametros propios para:

- masa
- radio
- gravedad
- albedo
- configuracion de clima

Con eso evitamos seguir heredando masa y radio terrestres para el caso TRAPPIST.

### 18.3. Que significa aqui "activar clima"

En esta actualizacion, "activar clima" significa activar el paso con `AdiabatClimate` para construir una atmosfera inicial con temperatura autoconsistente antes de correr la fotoquimica.

O sea, el flujo actual queda asi:

1. preparar mecanismo
2. preparar flujo estelar en el planeta
3. correr `AdiabatClimate` para obtener el perfil inicial de TRAPPIST-1e
4. usar ese perfil como entrada a `EvoAtmosphere`
5. correr la fotoquimica hasta steady state

### 18.4. Esto no es lo mismo que `evolve-climate: true` dentro de `EvoAtmosphere`

`photochem` tambien tiene un modo interno de fotoquimica-clima acoplada con `evolve-climate: true`, pero no lo puse como default del pipeline por una razon importante:

- ese modo cambia las reglas de boundary conditions
- por ejemplo, no acepta `press` como lower boundary condition fija en `EvoAtmosphere`
- nuestro flujo actual de escenarios `A0-A3` aun depende bastante de ese estilo de BC

Entonces, por ahora, la opcion implementada y documentada en el modulo es:

- acople en una sola direccion `clima -> photochem`

Eso ya mejora bastante la consistencia termica de TRAPPIST-1e sin reescribir por completo la semantica de BC del proyecto.

### 18.5. Que se actualizo en los ejemplos del modulo

Se actualizaron al menos estas piezas del ejemplo de trabajo del modulo:

- `catalog.json` ahora distingue planeta y estrella
- TRAPPIST-1e usa parametros planetarios propios
- el espectro TRAPPIST se prepara desde el archivo local a superficie estelar y se reescala al planeta
- los runs de TRAPPIST usan un paso de clima para generar la atmosfera inicial
- se agregaron templates de clima en `Config/Templates/`

### 18.6. Implicacion practica

Si quieres preparar un caso TRAPPIST hoy, el comando sigue siendo el mismo:

```bash
python prepare_photochem_inputs.py Trappist_A1_Current
```

Pero internamente ya no hace lo mismo que antes:

- prepara el flujo correcto en el planeta
- genera una atmosfera inicial con `AdiabatClimate`
- despues deja listo el caso para la etapa fotoquimica


