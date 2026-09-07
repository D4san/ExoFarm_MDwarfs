# Metodología de la Etapa III: emisión térmica, LIFEsim clásico y retrievals LIFE

**Fecha de reconstrucción metodológica:** 2026-08-30  
**Campañas cubiertas:** `life_earth_sun_10pc_interface_v1` y
`life_proxima_b_earthlike_v1`  
**Alcance:** perfiles fotoquímicos VULCAN → emisión térmica POSEIDON → ruido
astrofísico/fotónico LIFEsim clásico → diagnósticos moleculares → datasets
sintéticos → retrievals POSEIDON.  
**Estado:** metodología ejecutada y validada para la rama clásica. La rama
LIFEsimMC/PHRINGE con inestabilidad instrumental y covarianza permanece como
trabajo futuro.

## 1. Propósito del experimento

La Etapa III estudia cómo se observarían en emisión térmica las atmósferas
fotoquímicas de ExoFarm con un interferómetro de infrarrojo medio tipo LIFE. El
experimento no impone una abundancia detectable de N2O o NH3. Comienza con
flujos superficiales agrícolas, calcula la respuesta química vertical con
VULCAN y pregunta si la diferencia atmosférica resultante sobrevive a la
transformación en espectro, al modelo de observación y a la inferencia.

La cadena científica completa es:

```text
forzamiento superficial A0--A3
    → VULCAN: PT y perfiles químicos verticales
    → POSEIDON: espectro térmico sin ruido
    → LIFEsim clásico: binning y ruido astrofísico/fotónico
    → contrafactuales moleculares y S/N
    → observaciones sintéticas con semilla registrada
    → retrieval POSEIDON
    → separabilidad respecto de A0
```

La Etapa III es paralela a la espectroscopia de transmisión. No reutiliza
profundidades de tránsito, PandExo, conteos de tránsitos ni retrievals JWST como
si fueran observaciones LIFE.

## 2. Escenarios agrícolas A0--A3

La perturbación agrícola se introduce en VULCAN mediante flujos de frontera
inferior de N2O y NH3, en `molecules cm^-2 s^-1`. La ecuación de diseño es:

```text
F_i(A_j) = F_i(A0) + alpha_i,j * Delta F_i,agri
```

`A0` representa el fondo preagrícola y `Delta F_i,agri` la contribución
agrícola moderna. A1 adopta esa contribución una vez; A2 usa una perturbación
moderada inspirada en el escenario ExoFarm 30B de Haqq-Misra et al. (2022); A3
usa la envolvente de contaminación agrícola `15x` del escenario tecnosférico S2
de Haqq-Misra et al. (2025).

| Escenario | Interpretación | `alpha_NH3` | `alpha_N2O` | Flujo NH3 | Flujo N2O |
| --- | --- | ---: | ---: | ---: | ---: |
| A0 | fondo preagrícola | 0 | 0 | `2.94e9` | `1.58e9` |
| A1 | Tierra actual | 1 | 1 | `1.30e10` | `2.30e9` |
| A2 | ExoFarm moderado, 30B | 3.50 | 2.55 | `3.82e10` | `3.416e9` |
| A3 | ExoFarm extremo, S2 | 15 | 15 | `1.54e11` | `1.238e10` |

Los factores moderados se derivaron de las abundancias objetivo publicadas:

```text
alpha_NH3,A2 = (30 - 2) / (10 - 2) = 3.50
alpha_N2O,A2 = (590 - 170) / (335 - 170) = 2.55
```

Las velocidades de deposición inferiores permanecen explícitas: `1 cm s^-1`
para NH3 y `1e-4 cm s^-1` para N2O. Esto evita tratar ambos gases como trazadores
equivalentes: NH3 es soluble y reactivo y queda fuertemente limitado por los
sumideros superficiales; N2O tiene deposición mucho menor y pérdidas dominadas
por química y fotólisis a mayor altura. La derivación completa está en la
[metodología fotoquímica](photochemical_profiles_methodology.md).

## 3. Por qué se eligieron dos sistemas

Se usaron dos configuraciones complementarias, no dos afirmaciones sobre
atmósferas observadas.

### 3.1 Tierra--Sol a 10 pc: control de interfaz

El primer sistema es un gemelo Tierra--Sol sintético colocado a 10 pc. Se
escogió porque existían perfiles Tierra--Sol A0--A3 aceptados, los cuatro con
`end_case=1`, y porque una Tierra a 10 pc es un benchmark habitual de la serie
LIFE para caracterización en infrarrojo medio. Esta capa aísla la interfaz
VULCAN--POSEIDON--LIFEsim sin introducir una nueva estrella o fotoquímica.

Los 10 pc pertenecen exclusivamente a la escena observacional. No modifican la
irradiación usada por VULCAN ni convierten la Tierra real en un objetivo
observacional.

Los perfiles A2/A3 fueron guardados el 2026-06-15 con flujos N2O anteriores a la
corrección activa: `3.35e9` y `1.20e10`. Por ello toda la campaña usa la etiqueta
`earth_20260615_pre_n2o_correction`. Es un benchmark de interfaz, no la matriz
Tierra--Sol vigente. Véase la
[nota de procedencia](earth_sun_n2o_matrix_provenance_2026-07-20.md).

### 3.2 Proxima: análogo terrestre bajo una estrella M cercana

El segundo sistema es un análogo terrestre sometido al ambiente radiativo de
Proxima Centauri y observado con la geometría de Proxima b. Se eligió porque:

1. Proxima es extremadamente cercana (`d=1.30 pc`), condición favorable para
   emisión directa;
2. LIFE X la incluye entre los objetivos conocidos y publica parámetros y S/N
   de referencia;
3. existe una SED pancromática MUSCLES trazable;
4. permite separar el efecto de sustituir la SED solar por una SED M manteniendo
   un PT/Kzz terrestre controlado.

Esta capa **no afirma** que Proxima b tenga una atmósfera terrestre, radio
medido, superficie, agricultura o inventario A0--A3. El radio es estimado porque
el planeta no transita, y el PT/Kzz usado es terrestre, no un clima calculado
para Proxima b.

## 4. Construcción de la rama fotoquímica de Proxima

### 4.1 SED MUSCLES

Se descargó mediante `astroquery.mast 0.4.11` el producto MUSCLES Treasury
Survey v22 para GJ 551:

```text
mast:HLSP/muscles/v22/gj551/
hlsp_muscles_multi_multi_gj551_broadband_v22_adapt-const-res-sed.fits
```

El producto `adapt-const-res-sed` contiene 54 997 muestras entre 3 angstrom y
5.5 micras. Combina observaciones HST STIS/FOS, XMM EPIC y componentes de modelo
para rayos X, Ly-alpha reconstruida y fotosfera. Se preservó además la variante
`var-res-sed`.

| Producto | Tamaño | MD5 |
| --- | ---: | --- |
| `adapt-const-res-sed` | 5 189 760 bytes | `f0f91be58db0896dc1152a0a958b485d` |
| `var-res-sed` | 80 651 520 bytes | `9bea25448539a176d75dbc80c54e2cda` |

Los FITS se conservan en
`Photochemical_Modeling/Config/Stellar_Spectra/`. El producto HLSP tiene DOI
[10.17909/T9DG6F](https://doi.org/10.17909/T9DG6F).

### 4.2 Conversión observador--superficie estelar

MUSCLES entrega `WAVELENGTH` en angstrom y `FLUX` en
`erg s^-1 cm^-2 angstrom^-1` medido en la Tierra. VULCAN espera flujo en la
superficie de la estrella, longitud de onda en nm y densidad por nm. El script
[`convert_proxima_muscles_sed.py`](../Photochemical_Modeling/Scripts/Simulation/convert_proxima_muscles_sed.py)
aplicó:

```text
F_surf = F_obs * (d / R_star)^2
```

con `d=1.30 pc` y `R_star=0.14 R_sun`. El factor fue
`(d/R_star)^2 = 1.696242e17`. Las longitudes de onda se convirtieron de angstrom
a nm dividiendo por 10 y la densidad por angstrom a densidad por nm
multiplicando por 10. No hubo flujos negativos que corregir.

VULCAN aplica después una única escala `(R_star/a)^2` para calcular el flujo en
la órbita. Usar el mismo radio estelar en la conversión y en el YAML hace que el
radio se cancele y evita aplicar dos veces la geometría.

La integral bolométrica observada fue `2.964e-8 erg s^-1 cm^-2`, frente a
`2.859e-8` esperada a partir de `L=0.00151 L_sun` y 1.30 pc: razón 1.037. También
se comprobaron Ly-alpha, FUV y NUV. La salida VULCAN contiene 54 997 filas entre
0.30 y 5499.9 nm.

### 4.3 Configuración y aceptación VULCAN

Las configuraciones están en
`Photochemical_Modeling/Config/planets/earth_proxima_b/`. Se usó:

| Parámetro | Valor / decisión |
| --- | --- |
| PT/Kzz | `VULCAN/atm/atm_Earth_Jan_Kzz.txt`, control terrestre |
| Red química | `SNCHO_full_photo_network` + fotólisis |
| Mezcla mayoritaria | N2 0.78, O2 0.20, CO2 `4e-4`, valores terrestres |
| Radio planetario | `1.23 R_E` |
| Masa | `1.59 M_E` |
| Gravedad | `1030 cm s^-2` |
| Radio estelar | `0.14 R_sun` |
| Semieje mayor | `0.0485 AU` |
| Iluminación | `sl_angle=48 deg`, `f_diurnal=1`; inferencia de planeta bloqueado |
| Condiciones de frontera | matriz A0--A3 corregida |

El runner
[`run_parallel_proxima.py`](../Photochemical_Modeling/Scripts/Simulation/run_parallel_proxima.py)
generó los cuatro `.vul`. Todos alcanzaron `end_case=1`, con contadores
13255/12916/13854/14275 para A0/A1/A2/A3. Los perfiles PT y químicos se
exportaron a `Transmission_Spectroscopy/profiles/Proxima_b_*_{PT,chem}.txt`.
Las rutas y MD5 están congelados en el
[manifiesto Proxima](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/manifest.json).

## 5. Forward de emisión térmica con POSEIDON

La misma implementación se usó para las dos capas mediante
[`emission_forward.py`](../Thermal_Emission_Spectroscopy/scripts/emission_forward.py).

### 5.1 Entradas atmosféricas

Los perfiles exportados tienen:

- PT: altitud `[km]`, presión `[bar]`, temperatura `[K]`;
- química: presión `[bar]` y mixing ratio por especie.

POSEIDON interpola ambos sobre 100 capas logarítmicas entre 1 bar y
`3e-8 bar`. El radio de referencia se ancla en la superficie a 1 bar y se usa
una superficie rocosa opaca.

### 5.2 Especies y opacidades

`N2` se usa como gas mayoritario. Las especies radiativamente activas son:

```text
H2O, CO2, CH4, O2, O3, N2O, NH3
```

El modelo usa `PT_profile="file_read"`, `X_profile="file_read"`,
`thermal=True`, `thermal_scattering=False` y `surface=True`. La malla nativa
cubre 3--20 micras a resolución `R=10000`, con 18 971 puntos, para que el
binning posterior a R=20/R=50 no dependa de una malla insuficiente.

Se empleó POSEIDON `1.4.0` y la base High-T
`Opacity_database_v1.3.hdf5`, porque incluye simultáneamente N2O y NH3. Una
comparación A3 de seis especies comunes contra la base Temperate mostró que la
profundidad de N2O a 7.8 micras cambia aproximadamente -1.8%; el continuo cambia
menos de 1%. La región H2O de 6.3 micras mostró diferencias mayores, hasta 32%
por bin, y se conserva como limitación sistemática.

### 5.3 Cantidades espectrales

Para cada escenario se calcularon dos cantidades:

```text
emission        → Fp/Fs
direct_emission → Fp_obs = (R_p / d)^2 F_p
```

`Fp/Fs` es un contraste adimensional útil para comprobar el forward. LIFE
consume `Fp_obs`, el flujo planetario absoluto en el observador, devuelto por
POSEIDON en `W m^-2 m^-1`. La distancia entra aquí, en el observable, no en la
fotoquímica.

## 6. Diagnósticos moleculares contrafactuales

Un espectro completo no indica por sí mismo qué molécula causa la diferencia
entre escenarios. Para cada escenario perturbado A1--A3 se construyeron
contrafactuales reseteando una especie a su perfil A0 y conservando:

- el PT del escenario;
- las demás abundancias del escenario;
- la misma geometría y opacidades.

La señal de una especie `i` se definió como:

```text
Delta F_i(Aj) = F(Aj) - F(Aj con el perfil de i reseteado a A0)
```

Se generaron seis contrafactuales por escenario: N2O y NH3 como objetivos, y
H2O, CO2, O3 y CH4 como controles de solapamientos y cambios químicos. En total
son 18 contrafactuales por sistema. La operación se verificó comprobando que la
especie reseteada reproduce A0 sin modificar las demás.

## 7. Interfaz POSEIDON--LIFEsim clásico

La interfaz está implementada en
[`life_scene_classic.py`](../Thermal_Emission_Spectroscopy/scripts/life_scene_classic.py).
El flujo energético se convirtió a densidad de flujo de fotones mediante:

```text
F_ph(lambda) = Fp_obs(lambda) * lambda / (h c)
```

con unidades `ph m^-2 s^-1 m^-1`. Se entregaron a
`Instrument.get_spectrum` dos `astropy.Quantity`: longitud de onda en metros y
flujo fotónico. La instalación requiere la variante modificada de SpectRes que
acepta `edge_mode`.

El bus LIFEsim clásico usa el escenario `baseline` y conecta:

- `Instrument`;
- `TransmissionMap`;
- `PhotonNoiseStar` para fuga estelar;
- `PhotonNoiseLocalzodi`;
- `PhotonNoiseExozodi`.

El resultado por escenario contiene malla LIFE, flujo binado sin ruido, S/N por
bin y sigma fotónica por bin. Esta sigma es diagonal; no representa
inestabilidades instrumentales correlacionadas.

### 7.1 Escena Tierra--Sol

| Parámetro | Valor |
| --- | ---: |
| Distancia | 10 pc |
| Estrella | 5772 K, `1 R_sun`, `log g=4.44` |
| Planeta | `1 R_E`, `1 M_E`, `T_eq=255 K` |
| Colectores | 4 × 2 m |
| Banda | 4--18.5 micras |
| Resolución | R=50, 77 bins |
| Throughput total | 5% |
| Eficiencia cuántica | 0.7 |
| Exozodi | 1 zodi, decisión de benchmark limpio |
| Separación angular | 0.1 arcsec |
| Latitud eclíptica | 0.79 rad, aproximadamente 45 grados |
| Tiempo de referencia | 10 h |

### 7.2 Escena Proxima

Los parámetros físicos se congelaron principalmente desde LIFE X, Tabla G.1:

| Parámetro | Valor |
| --- | ---: |
| Distancia | 1.30 pc |
| Estrella | 3050 K, `0.14 R_sun`, `log g=5.2` |
| Planeta | `1.23 R_E`, `1.59 M_E`, `T_eq=229 K` |
| Semieje mayor | 0.0485 AU |
| Separación angular | 0.0373 arcsec |
| Latitud eclíptica | 44.8 grados, derivada con astropy |
| Colectores | 4 × 2 m |
| Banda | 4--18.5 micras |
| Resolución | R=20, 31 bins |
| Throughput / QE | 5% / 0.7 |
| Exozodi | 3 zodis |
| Tiempo de referencia | 10 h |

La escena se calibró con un planeta cuerpo negro contra los valores de LIFE X.
Para aperturas de 1/2/3.5 m se obtuvo S/N de 48.4/166.5/412.4 en 10 h, frente a
45/170/466 publicados. La configuración de referencia de 2 m reproduce el
ancla al 2%. LIFE X promedia 1000 realizaciones orbitales; el proyecto evalúa
una época con separación media.

### 7.3 Tratamiento del tiempo de integración

LIFEsim clásico no está limitado a una observación de 10 h. La interfaz
`Instrument.get_spectrum` recibe `integration_time` y puede calcular
directamente el S/N y la sigma por bin para cualquier tiempo solicitado. En la
implementación del proyecto, esta capacidad queda expuesta por
`LifeSceneClassic.observe(..., integration_time_s=...)`.

La campaña histórica se construyó en dos pasos:

1. LIFEsim se ejecutó directamente para la escena de referencia de 10 h.
2. Las sigma de 240 y 1200 h se obtuvieron mediante
   `sigma(t)=sigma(10 h) sqrt(10 h/t)`.

Este segundo paso es un atajo reproducible dentro del modelo clásico: con las
fuentes de ruido fotónico incluidas, la validación 1/10/100 h confirmó el
escalado `S/N proportional to sqrt(t)`. No significa que LIFEsim sea incapaz de
calcular esos tiempos directamente. Antes de reincorporar 1200 h a una matriz
canónica se debe ejecutar LIFEsim de forma directa a 10, 240 y 1200 h, guardar
las tres salidas y comprobar bin a bin que coinciden con el escalado.

La equivalencia no se extrapola a LIFEsimMC/PHRINGE. Una simulación con
inestabilidades instrumentales, extracción temporal y covarianza debe ejecutarse
para cada duración y preservar su matriz de covarianza; no puede sustituirse de
antemano por una simple proyección `sqrt(t)`.

## 8. Validaciones de la interfaz

Se aplicaron cuatro familias de comprobaciones antes de interpretar las señales:

1. **Cuerpo negro y geometría.** A 10 micras, Tierra A0 dio
   `1.16e-14 W m^-2 m^-1`, frente a `1.03e-14` para un cuerpo negro de 285 K a
   10 pc, razón 1.13. Proxima A0 dio razón 1.28 respecto a su control. Ambas son
   coherentes con estructura atmosférica sobre el continuo y confirman la
   escala `(R_p/d)^2`.
2. **Calibración LIFE X.** La escena Proxima de 2 m reproduce el S/N publicado
   al 2%.
3. **Escalado temporal.** LIFEsim clásico mostró exactamente
   `S/N proportional to sqrt(t)` entre 1, 10 y 100 h.
4. **Base de opacidades.** El observable N2O central cambia pocos por ciento al
   comparar High-T y Temperate para las especies comunes; H2O 6.3 micras se
   marca como región sensible.

Los manifiestos de campaña registran versiones, parámetros planetarios,
perfiles y hashes:

- [Tierra--Sol](../Thermal_Emission_Spectroscopy/outputs/life_earth_sun_10pc_interface_v1/manifest.json);
- [Proxima](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/manifest.json).

## 9. Cálculo de S/N molecular

Los espectros completos y contrafactuales se rebinaron sobre la malla LIFE. La
S/N de una banda se calculó como:

```text
SNR_i,band = sqrt[ sum_k (Delta F_i,k / sigma_k)^2 ]
```

donde `sigma_k` procede de la observación LIFEsim del escenario completo. Se
usó el valor absoluto para ordenar la contribución de cada bin, pero se conserva
el signo del residual en los productos.

| Molécula | Bandas diagnósticas [micras] |
| --- | --- |
| N2O | 7.5--8.1; 16.5--17.5 |
| NH3 | 9.5--11.5 |
| H2O | 5.5--7.3; 17.0--18.5 |
| CO2 | 14.0--16.0 |
| O3 | 9.4--9.9 |
| CH4 | 7.4--8.0 |

Esta S/N es un diagnóstico dirigido: conoce de antemano la forma diferencial
que debe sumar. No es una evidencia bayesiana ni una detección independiente.

## 10. Resultados del diagnóstico clásico

### 10.1 Tierra--Sol a 10 pc

En 10 h, la señal agrícola queda por debajo del ruido:

| Escenario | Señal | S/N de banda |
| --- | --- | ---: |
| A3 | N2O 7.5--8.1 | 0.163 |
| A3 | N2O 16.5--17.5 | 0.074 |
| A2 | N2O 7.5--8.1 | 0.049 |
| A1 | N2O 7.5--8.1 | 0.021 |
| A3 | NH3 9.5--11.5 | 0.005 |

La banda más favorable es N2O a 7.82 micras. NH3 permanece varios órdenes por
debajo de un tiempo de integración plausible. El resultado defendible es que
un gemelo solar a 10 pc no es un objetivo favorable bajo esta configuración
clásica; además, la campaña conserva la salvedad precorrección de N2O.

### 10.2 Análogo Proxima

En 10 h:

| Escenario | Señal | S/N de banda |
| --- | --- | ---: |
| A3 | N2O 16.5--17.5 | 4.80 |
| A3 | N2O 7.5--8.1 | 2.81 |
| A3 | NH3 9.5--11.5 | 1.44 |
| A2 | N2O 16.5--17.5 | 1.20 |

Por escalado `sqrt(t)`, A3 alcanza S/N=5 en aproximadamente 11 h para N2O a
17 micras, 32 h para N2O a 7.8 micras y 120 h para NH3. La comparación con
Tierra--Sol está fuertemente influida por la distancia. Un escalado aproximado
como `d^4` solo se espera si domina un fondo independiente de la distancia;
no es una ley general cuando cambian fuga estelar, exozodi, estrella y química.
La química no es idéntica;
por ejemplo, N2O superficial A3 bajo Proxima es menor que en Tierra--Sol, de
modo que no se interpreta la mejora como simple supervivencia química.

## 11. Construcción de los datasets sintéticos

Los retrievals consumen archivos de cuatro columnas:

```text
wavelength[um]  half_bin_width[um]  Fp[W m^-2 m^-1]  sigma_Fp
```

El script
[`make_life_datasets.py`](../Thermal_Emission_Spectroscopy/scripts/make_life_datasets.py)
convierte la sigma fotónica de LIFEsim de vuelta a flujo energético mediante
`sigma_F = sigma_ph h c / lambda`. Los productos históricos toman la sigma
calculada directamente por LIFEsim a 10 h y, para un tiempo `t`, usan:

```text
sigma(t) = sigma(10 h) * sqrt(10 h / t)
```

Cada dataset añade una realización gaussiana independiente con semilla
registrada. La semilla maestra fue `20260725`; las semillas por archivo están en
[`dataset_index.json`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/dataset_index.json).

La matriz canónica contiene ocho datasets Proxima A0--A3 por `{10 h, 240 h}`.
Los cuatro datasets de 1200 h se conservan como evidencia de piloto excluida,
no como parte del cierre 8/8. Sus barras son coherentes con la extrapolación
fotónica clásica; la exclusión se debe a que esas barras estrechas hicieron
dominante el desajuste entre la atmósfera vertical VULCAN y el modelo de
retrieval simplificado. No se clasifican como datos numéricamente erróneos.

## 12. Modelo de retrieval

Los retrievals se ejecutaron con
[`run_life_retrieval.py`](../Thermal_Emission_Spectroscopy/scripts/run_life_retrieval.py)
y MultiNest, usando 200 live points para la matriz final. La malla interna del
retrieval cubre 3.8--19 micras a `R=2000`; los datos conservan el binning LIFE
R=20. Se usa `spectrum_unit="Fp"` y
`spectrum_type="direct_emission"`.

El truth contiene perfiles VULCAN verticales. El modelo inverso es
intencionalmente más simple:

- PT Madhu de seis parámetros;
- abundancias isoquímicas para H2O, CO2, CH4, O3, N2O y NH3;
- radio de referencia libre;
- presión superficial libre;
- tolerancia fraccional de desajuste `x_tol` mediante `Piette20`;
- superficie opaca y emisión térmica.

### 12.1 Priors

| Parámetro | Prior uniforme |
| --- | --- |
| `a1`, `a2` | `[0.02, 2.0]` |
| `log_P1`, `log_P2` | `[-6, 1]` |
| `log_P3` | `[-2, 1]` |
| `T_ref` | `[150, 400] K` |
| cada `log_X` | `[-12, -1]` |
| `R_p_ref` | `[0.8, 1.3]` veces el radio objetivo, entregado en metros |
| `log_P_surf` | `[-1, 1]` |
| `x_tol` | `[0.0, 0.3]` |

El radio debe entregarse en metros porque POSEIDON divide internamente el prior
por la unidad de radio seleccionada. Pasarlo previamente en radios terrestres
produjo un radio doblemente normalizado y una terminación inmediata incorrecta.

`x_tol` es necesario porque el modelo paramétrico no reproduce exactamente una
atmósfera VULCAN de 120 capas. Su papel no es crear una detección, sino impedir
que el desajuste estructural domine artificialmente una likelihood con barras
de error pequeñas.

## 13. Pilotos y decisiones de desarrollo

Tres fallos permitieron definir la configuración final:

1. **PT rígido de dos parámetros.** Con S/N extremo, el desajuste respecto al
   PT VULCAN produjo `ln Z` del orden de `-9e6` y MultiNest no exploró un
   posterior físico.
2. **PT Madhu + `Line15`.** `Line15` suma un término absoluto `10^b` en unidades
   de dato al cuadrado. Para flujos `Fp` alrededor de `1e-12 W m^-2 m^-1` ese
   término infló las incertidumbres decenas de órdenes y dejó los parámetros
   sin restringir.
3. **PT Madhu + `Piette20`, radio mal escalado.** La tolerancia fraccional fue
   adecuada, pero el prior de radio en `R_E` se dividía otra vez dentro de
   POSEIDON. Al entregar metros, el piloto A3--240 h pasó a 48 450 evaluaciones,
   `ln Z=895.4 +/- 0.45` y parámetros físicos.

Los datasets de 1200 h y el retrieval A3--1200 h se conservan como evidencia de
estos pilotos. No cuentan en la matriz canónica ni en las conclusiones. Su
clasificación está en el
[inventario de campaña](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/README.md).

## 14. Interpretación de los retrievals

La matriz final contiene ocho retrievals Proxima A0--A3 por 10/240 h. Se
aplicaron dos condiciones antes de llamar a un resultado distinguible:

1. el posterior debe ser una medición, definida operacionalmente por
   `sigma < 0.5 dex`, no un límite superior;
2. la diferencia debe tener el signo físico esperado: A1--A3 añaden N2O sobre
   A0. Una mediana inferior a A0 en un posterior ancho se clasifica como
   artefacto del prior, no como separación.

### 14.1 Resultado a 240 h

| Escenario | N2O recuperado | Estado | Separación frente a la referencia A0 efectiva |
| --- | --- | --- | ---: |
| A3 | `-6.19 +/- 0.22` | medición | 3.14 sigma |
| A2 | `-9.26 +/- 1.73` | límite superior | no aplicable |
| A1 | `-8.30 +/- 1.61` | límite superior | no aplicable |
| NH3 | aproximadamente `-9.5 +/- 1.4` | límite superior | no aplicable |

La cifra 3.14 sigma es una **separación diagnóstica estandarizada** entre el
posterior A3 y la referencia A0 efectiva. Esta referencia es el logaritmo del
promedio columnar ponderado en presión del perfil vertical VULCAN de A0,
calculado para que sea comparable con la abundancia isoquímica constante del
retrieval; no es la abundancia de una capa superficial. No es una significancia
de detección ni una comparación de evidencias con/sin N2O. Tampoco es lo mismo
que posterior contra posterior: A0 no mide bien N2O y su posterior ancho reduce
esa segunda métrica a aproximadamente 1.25 sigma.

### 14.2 Resultado a 10 h

A3 recupera N2O como `-6.50 +/- 0.41`, pero solo se separa 0.93 sigma de la
referencia A0 efectiva. Por tanto, 10 h permiten restringir N2O en A3, pero no discriminar el
escenario preagrícola. A1 y A2 siguen siendo límites superiores.

El resultado inferencial defendible es más conservador que el diagnóstico de
S/N: con 240 h solo A3 produce una medición que excluye A0; A1/A2 no permiten
extrapolar un número de campañas mediante `sqrt(t)` porque todavía no han
pasado de límite superior a medición. NH3 no es discriminante.

### 14.3 Por qué NH3 tiene S/N pero no una medición

El contrafactual A3 de Proxima produce para NH3 un S/N de banda de 1.44 en
10 h. Bajo el escalado fotónico clásico correspondería aproximadamente a 7.1 en
240 h y 15.8 en 1200 h. Este diagnóstico compara el espectro completo contra el
mismo escenario reemplazando únicamente el perfil de NH3 por A0; conoce de
antemano qué molécula cambia y mantiene fijos los demás parámetros.

El retrieval resuelve un problema más difícil. Varía simultáneamente el PT, el
radio, la presión superficial, seis abundancias y la tolerancia de modelo, y
representa NH3 mediante una abundancia isoquímica en lugar del perfil vertical
de VULCAN. En los retrievals canónicos A3--10 h y A3--240 h, el posterior de
NH3 permanece ancho y dominado por degeneraciones; por eso se clasifica como
límite superior. La rama clásica demuestra una contribución espectral
condicionada de NH3, pero no su identificación molecular independiente.

El piloto A3--1200 h no resuelve esta cuestión porque quedó dominado por el
desajuste de modelo de alta precisión. Una prueba válida de NH3 requiere
calcular directamente cada tiempo, ejecutar el modelo inferencial corregido y
comparar evidencias con/sin NH3, primero bajo ruido clásico y después con la
covarianza LIFEsimMC/PHRINGE.

## 15. Qué puede concluirse

1. La interfaz VULCAN--POSEIDON--LIFEsim clásico conserva de forma trazable las
   perturbaciones atmosféricas A0--A3.
2. N2O es un observable agrícola mucho más favorable que NH3 en emisión
   térmica para estas atmósferas y configuraciones.
3. Un gemelo solar a 10 pc permanece fuera de alcance práctico en la rama
   clásica de 2 m.
4. La proximidad de Proxima convierte A3 en un caso favorable en el diagnóstico
   clásico; la banda de 17 micras supera a la de 7.8 micras para este sistema.
5. En la inferencia conjunta clásica, una campaña de 240 h distingue A3 del
   valor preagrícola de referencia mediante N2O; no ocurre lo mismo con A1,
   A2 o NH3.
6. El retrieval de alto S/N requiere un PT flexible, tolerancia de modelo
   fraccional y una convención de radio correctamente auditada.

## 16. Qué no puede concluirse

- No se ha demostrado una detección instrumental completa de LIFE.
- LIFEsim clásico no incluye la inestabilidad instrumental correlacionada que
  debe simular LIFEsimMC/PHRINGE.
- Las sigma usadas son diagonales y existe una sola realización de ruido por
  dataset.
- No se han comparado evidencias de modelos con/sin N2O o NH3.
- Proxima es un análogo terrestre controlado, no una reconstrucción de la
  atmósfera real de Proxima b.
- Tierra--Sol usa perfiles precorrección de N2O.
- Los retrievals usan abundancias isoquímicas y un PT paramétrico; los valores
  recuperados son promedios efectivos, no perfiles verticales resueltos.
- Un S/N contrafactual alto no equivale por sí solo a detección o atribución a
  agricultura.

## 17. Trabajo futuro: LIFEsimMC/PHRINGE

La continuación metodológica debe usar los espectros ya validados y añadir:

1. configuración instrumental perturbada, versiones/commits y semillas;
2. extracción de la SED y preservación de la matriz de covarianza;
3. whitening reproducible o likelihood explícitamente correlacionada;
4. múltiples realizaciones de ruido para A0/A3 como mínimo;
5. modelos comparados con/sin N2O y, si se justifica, con/sin NH3;
6. pruebas de que la separación A3 sobrevive a la inestabilidad instrumental;
7. decisión independiente sobre un rerun Tierra--Sol con los BC N2O corregidos.

Hasta completar esa rama, los resultados actuales se describen como
**benchmark validado y cota optimista de observabilidad con LIFEsim clásico**.

## 18. Proyectos científicos y software enlazados

| Proyecto | Papel en la metodología | Enlace oficial |
| --- | --- | --- |
| LIFE | Concepto de misión de interferometría anuladora en el infrarrojo medio | [Sitio oficial de LIFE](https://life-space-mission.com/) |
| LIFEsim clásico | Escena, transmisión, fuentes astrofísicas de ruido fotónico y S/N por bin | [Código](https://github.com/fdannert/LIFEsim) · [documentación](https://lifesim.readthedocs.io/en/latest/) |
| LIFEsimMC | Simulación Monte Carlo, extracción e interfaz con errores instrumentales | [Código](https://github.com/pahuber/LIFESIMMC) · [documentación](https://lifesimmc.readthedocs.io/en/latest/) |
| PHRINGE | Generación temporal de fotoelectrones para interferómetros anuladores | [Código](https://github.com/pahuber/PHRINGE) |
| POSEIDON | Forward de emisión térmica y retrieval atmosférico | [Código](https://github.com/MartianColonist/POSEIDON) · [documentación](https://poseidon-retrievals.readthedocs.io/en/latest/) |
| VULCAN | Fotoquímica 1D que genera los perfiles PT/químicos de entrada | [Código](https://github.com/shami-EEG/VULCAN) |

Las realizaciones locales del experimento son:

- [`life_earth_sun_10pc_interface_v1`](../Thermal_Emission_Spectroscopy/outputs/life_earth_sun_10pc_interface_v1/manifest.json): benchmark Tierra--Sol a 10 pc para validación de interfaz;
- [`life_proxima_b_earthlike_v1`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/README.md): análogo terrestre bajo el entorno de Proxima, con matriz clásica de retrievals;
- [configuración Tierra--Sol](../Thermal_Emission_Spectroscopy/configs/life_earth_sun_10pc/README.md);
- [configuración Proxima](../Thermal_Emission_Spectroscopy/configs/life_proxima_b_earthlike/README.md).

## 19. Archivos para reproducir la cadena

| Función | Archivo principal |
| --- | --- |
| Metodología VULCAN y escenarios | [`photochemical_profiles_methodology.md`](photochemical_profiles_methodology.md) |
| Conversión SED Proxima | [`convert_proxima_muscles_sed.py`](../Photochemical_Modeling/Scripts/Simulation/convert_proxima_muscles_sed.py) |
| Runner VULCAN Proxima | [`run_parallel_proxima.py`](../Photochemical_Modeling/Scripts/Simulation/run_parallel_proxima.py) |
| Forward de emisión | [`emission_forward.py`](../Thermal_Emission_Spectroscopy/scripts/emission_forward.py) |
| Contrafactuales | [`make_counterfactuals.py`](../Thermal_Emission_Spectroscopy/scripts/make_counterfactuals.py) |
| Escena LIFEsim clásico | [`life_scene_classic.py`](../Thermal_Emission_Spectroscopy/scripts/life_scene_classic.py) |
| S/N Tierra--Sol | [`run_life_snr_classic.py`](../Thermal_Emission_Spectroscopy/scripts/run_life_snr_classic.py) |
| Calibración Proxima | [`validate_proxima_life_scene.py`](../Thermal_Emission_Spectroscopy/scripts/validate_proxima_life_scene.py) |
| S/N Proxima | [`run_proxima_life_snr.py`](../Thermal_Emission_Spectroscopy/scripts/run_proxima_life_snr.py) |
| Datasets sintéticos | [`make_life_datasets.py`](../Thermal_Emission_Spectroscopy/scripts/make_life_datasets.py) |
| Retrieval individual | [`run_life_retrieval.py`](../Thermal_Emission_Spectroscopy/scripts/run_life_retrieval.py) |
| Matriz 8/8 | [`run_matrix.sh`](../Thermal_Emission_Spectroscopy/scripts/run_matrix.sh) |
| Separación de posteriores | [`analyze_retrieval_separation.py`](../Thermal_Emission_Spectroscopy/scripts/analyze_retrieval_separation.py) |
| Validación consolidada | [`lifesim_classic_stage_iii_validation_2026-08-30.md`](lifesim_classic_stage_iii_validation_2026-08-30.md) |

## 20. Referencias metodológicas

- Haqq-Misra, J., Fauchez, T. J., Schwieterman, E. W., & Kopparapu, R. (2022).
  *Disruption of a Planetary Nitrogen Cycle as Evidence of Extraterrestrial
  Agriculture*. ApJL, 929, L28.
  [doi:10.3847/2041-8213/ac65ff](https://doi.org/10.3847/2041-8213/ac65ff).
- Haqq-Misra, J., Profitiliotis, G., & Kopparapu, R. (2025). *Projections of
  Earth's technosphere: Scenario modeling, worldbuilding, and overview of
  remotely detectable technosignatures*. TFSC, 218, 124194.
  [doi:10.1016/j.techfore.2025.124194](https://doi.org/10.1016/j.techfore.2025.124194).
- Tsai, S.-M., et al. (2021). *VULCAN: An Open-source, Validated Chemical
  Kinetics Python Code for Exoplanetary Atmospheres*.
  [doi:10.3847/PSJ/abd022](https://doi.org/10.3847/PSJ/abd022).
- MacDonald, R. J. (2023). *POSEIDON: A Multidimensional Atmospheric Retrieval
  Code for Exoplanet Spectra*. JOSS, 8(81), 4873.
  [doi:10.21105/joss.04873](https://doi.org/10.21105/joss.04873).
- Quanz, S. P., et al. (2022). *LIFE I. Improved exoplanet detection yield
  estimates for a large mid-infrared space-interferometer mission*. A&A, 664,
  A21.
  [doi:10.1051/0004-6361/202140366](https://doi.org/10.1051/0004-6361/202140366).
- Dannert, F. A., et al. (2022). *LIFE II. Signal simulation, signal extraction,
  and fundamental exoplanet parameters from single-epoch observations*. A&A,
  664, A22.
  [doi:10.1051/0004-6361/202141958](https://doi.org/10.1051/0004-6361/202141958).
- Konrad, B. S., et al. (2022). *LIFE III. Spectral resolution, wavelength
  range, and sensitivity requirements based on atmospheric retrieval analyses
  of an exo-Earth*. A&A, 664, A23.
  [doi:10.1051/0004-6361/202141964](https://doi.org/10.1051/0004-6361/202141964).
- Carrión-González, Ó., et al. (2023). *LIFE X. Detectability of currently known
  exoplanets and synergies with future reflected-light missions*. A&A, 678,
  A96.
  [doi:10.1051/0004-6361/202347027](https://doi.org/10.1051/0004-6361/202347027).
- Angerhausen, D., et al. (2024). *LIFE XII. Detectability of capstone
  biosignatures in the mid-infrared*. AJ, 167, 128.
  [doi:10.3847/1538-3881/ad1f4b](https://doi.org/10.3847/1538-3881/ad1f4b).
- Huber, P. A., et al. (2025). *Robust Data Interpretation for Perturbed
  Nulling Interferometers via Proper Handling of Correlated Errors*. AJ, 170,
  227.
  [doi:10.3847/1538-3881/adfb6b](https://doi.org/10.3847/1538-3881/adfb6b).
- Feroz, F., Hobson, M. P., & Bridges, M. (2009). *MultiNest: an efficient and
  robust Bayesian inference tool*. MNRAS, 398, 1601--1614.
  [doi:10.1111/j.1365-2966.2009.14548.x](https://doi.org/10.1111/j.1365-2966.2009.14548.x).
