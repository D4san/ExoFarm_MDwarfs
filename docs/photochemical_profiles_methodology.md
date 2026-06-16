# Construcción de los perfiles fotoquímicos de ExoFarm con VULCAN

**Fecha de revisión:** 2026-06-15  
**Etapa:** modelado fotoquímico directo  
**Implementación:** VULCAN local en `VULCAN/`

## Propósito del experimento

La etapa fotoquímica de ExoFarm traduce una perturbación agrícola superficial
en una estructura química vertical. La pregunta no es simplemente cuánto
`N2O` o `NH3` se asigna a una atmósfera, sino qué perfil resulta cuando esos
gases se emiten desde la superficie, se mezclan verticalmente, se depositan,
reaccionan y son fotodisociados bajo distintos campos estelares.

El experimento compara dos ambientes:

1. una Tierra alrededor del Sol;
2. un planeta con los parámetros físicos y orbitales de TRAPPIST-1e, pero que
   conserva deliberadamente el perfil terrestre de temperatura y difusión
   turbulenta `Kzz`.

Esta segunda elección convierte la comparación en un experimento controlado:
permite estudiar primero la respuesta química al ambiente estelar y a los
flujos agrícolas sin introducir simultáneamente un nuevo perfil climático.
También limita la interpretación: el caso TRAPPIST-1e no representa todavía
una atmósfera climáticamente autoconsistente de ese planeta.

## Cadena reproducible

Cada caso se construye mediante cuatro tipos de entrada:

```text
red química + perfil P-T-Kzz + espectro estelar + condiciones de frontera
                              |
                              v
                         integración VULCAN
                              |
                              v
                  perfiles verticales de mezcla .vul
```

Los archivos YAML de `Photochemical_Modeling/Config/planets/` definen qué
entradas usa cada planeta. Los lanzadores
`Photochemical_Modeling/Scripts/Simulation/run_parallel_earth.py` y
`run_parallel_trappist.py` copian VULCAN a directorios temporales, colocan la
condición de frontera correspondiente como `atm/BC_bot_Earth.txt`, generan
`vulcan_cfg.py` mediante `VULCAN/run_case.py` y ejecutan la integración.

## Red química y discretización

La configuración activa utiliza:

```text
VULCAN/thermo/SNCHO_full_photo_network.txt
```

Esta es la red completa de azufre, nitrógeno, carbono, hidrógeno y oxígeno de
VULCAN para atmósferas oxidantes tipo Tierra. Los productos calculados
contienen:

- 100 especies químicas;
- 1284 reacciones;
- 120 capas verticales;
- presiones centrales desde `1 bar` hasta `5e-8 bar`.

Las constantes cinéticas están escritas dentro de la red y VULCAN calcula las
reacciones inversas a partir de datos termodinámicos. Las secciones eficaces de
absorción y fotodisociación se encuentran en `VULCAN/thermo/photo_cross/`.
`Source_references.txt` atribuye la mayoría a la base de Leiden y documenta
excepciones como `N2O`, `NO2`, `N2O5` y `HNO3`.

Antes de integrar, VULCAN reconstruye `chem_funs.py` desde la red. Los logs de
la campaña del 2026-06-15 confirman conservación elemental y ausencia de
reacciones duplicadas.

### Perfil atmosférico controlado

Ambos ambientes usan:

```text
VULCAN/atm/atm_Earth_Jan_Kzz.txt
```

El perfil resultante abarca aproximadamente:

| Magnitud | Intervalo |
| --- | ---: |
| Temperatura | `187.2-300.0 K` |
| `Kzz` | `3.90e3-1.12e5 cm2 s-1` |
| Presión | `1-5e-8 bar` |

VULCAN interpola este archivo sobre las 120 capas. Se incluyen difusión
molecular, condensación de `H2O` y `H2SO4`, sedimentación y escape limitado por
difusión para `H` y `H2`.

## Diseño de los escenarios agrícolas

La agricultura tecnológica se representa modificando los flujos de frontera
inferior de `NH3` y `N2O`, no imponiendo directamente sus abundancias
atmosféricas. El resto de las condiciones de frontera se mantiene igual entre
los escenarios.

La decisión conceptual procede de la nota de diseño
`Diseño de escenarios ExoFarm por flujos.md`:

- Haqq-Misra et al. (2022) proporciona escenarios ExoFarm expresados como
  abundancias objetivo para una Tierra preagrícola, actual y futuros 30B/100B.
- Haqq-Misra et al. (2025) proporciona un marco de tecnosferas; su escenario S2
  Wild West alcanza un índice de contaminación agrícola `15x`.
- El proyecto traduce esas anclas narrativas a perturbaciones de flujo para
  permitir que VULCAN calcule las abundancias y perfiles resultantes.

La ecuación de diseño es:

```text
F_i(A_j) = F_i(A0) + alpha_i,j * Delta F_i,agri
```

donde `A0` es el fondo preagrícola y `Delta F_i,agri` representa la
contribución agrícola moderna que se intensifica.

### Flujos implementados

Los valores realmente usados por VULCAN son:

| Caso | Interpretación | `NH3` | `N2O` |
| --- | --- | ---: | ---: |
| A0 | fondo preagrícola | `2.94e9` | `1.58e9` |
| A1 | Tierra actual | `1.30e10` | `2.30e9` |
| A2 | ExoFarm moderado, inspirado en 30B | `3.82e10` | `3.35e9` |
| A3 | ExoFarm extremo, inspirado en S2 | `1.54e11` | `1.20e10` |

Unidades: `molecules cm^-2 s^-1`.

Estos valores viven en
`Photochemical_Modeling/Config/Boundary_Conditions/`. Además del flujo, cada
fila define una velocidad de deposición. En particular:

| Especie | Velocidad de deposición |
| --- | ---: |
| `NH3` | `1 cm s^-1` |
| `N2O` | `1e-4 cm s^-1` |

Esta diferencia es físicamente importante. `NH3` es soluble y reactivo, por lo
que la deposición superficial limita fuertemente su acumulación. `N2O` tiene
una deposición mucho menor y sus pérdidas relevantes ocurren principalmente
mediante química y fotólisis a mayor altura.

### Estado de la derivación cuantitativa

Los factores de A2 se obtuvieron de las abundancias objetivo de Haqq-Misra
et al. (2022):

```text
alpha_NH3,A2 = (30 - 2) / (10 - 2) = 3.50
alpha_N2O,A2 = (590 - 170) / (335 - 170) = 2.55
```

A3 adopta `alpha = 15` como envolvente inspirada en el índice agrícola S2 de
Haqq-Misra et al. (2025).

Sin embargo, existe una inconsistencia que debe resolverse antes de presentar
la matriz como una aplicación exacta de la ecuación. Si se calcula
`Delta F = F(A1) - F(A0)` usando los valores redondeados implementados, los
flujos de `N2O` implican:

```text
alpha_N2O,A2 = 2.458, no 2.55
alpha_N2O,A3 = 14.472, no 15
```

Para `NH3`, los factores implícitos son `3.505` y `15.016`, compatibles con
redondeo. Para `N2O` la diferencia es mayor. Debe recuperarse la derivación con
valores no redondeados o decidir si se corrigen los flujos o los factores
documentados. Hasta entonces, los valores de la tabla son los forzamientos
ejecutados, mientras que los `alpha` son las anclas conceptuales declaradas.

## Tratamiento de los espectros estelares

VULCAN espera que el archivo estelar contenga densidad de flujo en la
**superficie de la estrella**, con longitud de onda en `nm` y flujo en
`erg cm^-2 s^-1 nm^-1`. Luego calcula el flujo recibido en el planeta mediante:

```text
F_planet(lambda) =
F_surface(lambda) * (R_star / a)^2
```

Esta operación está implementada en `VULCAN/build_atm.py`. Posteriormente,
VULCAN interpola el espectro sobre su malla fotoquímica:

- `0.1 nm` por bin para longitudes menores que `240 nm`;
- `2 nm` por bin desde `240 nm`;
- intervalo fotoquímico usado en estas corridas: `2-700 nm`.

### Caso solar

El caso Earth-Sun utiliza:

```text
VULCAN/atm/stellar_flux/Gueymard_solar.txt
```

El encabezado del archivo lo describe como el espectro extraterrestre
sintético/compuesto de Chris Gueymard, mayo de 2003. Se usa con
`R_star = 1 R_sun` y `a = 1 AU`; VULCAN realiza el escalado geométrico desde la
superficie solar hasta la órbita terrestre.

Existe una inconsistencia documental menor: `VULCAN/atm/stellar_flux/README.txt`
lo llama “Gueymard 2018”, mientras que el propio archivo indica 2003. Debe
confirmarse la referencia bibliográfica correcta.

### Caso TRAPPIST-1

El caso TRAPPIST-1e utiliza:

```text
VULCAN/atm/stellar_flux/TRAPPIST1_surface.txt
```

El repositorio conserva también:

```text
Photochemical_Modeling/Config/Stellar_Spectra/trappist-1_model_const_res_v07.ecsv
```

La nomenclatura y las notas externas del proyecto identifican el ECSV como un
producto de la grid Mega-MUSCLES. La relación matemática entre ambos archivos
sí puede demostrarse localmente:

1. la longitud de onda del ECSV está en angstrom y se divide por 10 para
   obtener `nm`;
2. el flujo por angstrom se multiplica por 10 para obtener flujo por `nm`;
3. todo el espectro se multiplica por un factor constante
   `2.2347274e19`.

La raíz cuadrada de ese factor es `4.7272904e9`, consistente con un escalado
geométrico desde la distancia del observador hasta la superficie estelar.
Por tanto, `TRAPPIST1_surface.txt` es efectivamente una versión superficial del
ECSV preservado. Lo que todavía falta registrar es el script original que hizo
la conversión y la cita exacta del producto Mega-MUSCLES.

VULCAN vuelve a escalar ese espectro superficial hasta TRAPPIST-1e usando:

```text
R_star = 0.1192 R_sun
a      = 0.02925 AU
```

## ¿Cómo se representa el bloqueo por marea?

Sí está representado en la configuración actual, pero como una aproximación 1D
a la iluminación, no como una simulación explícita de rotación o circulación
atmosférica.

VULCAN utiliza dos parámetros distintos:

| Parámetro | Earth-Sun | TRAPPIST-1e | Función |
| --- | ---: | ---: | --- |
| `f_diurnal` | `0.5` | `1.0` | multiplica todas las tasas de fotólisis |
| `sl_angle` | `58 deg` | `48 deg` | fija el ángulo cenital efectivo en la transferencia radiativa |

En el código, cada tasa de fotólisis se calcula como:

```text
k_photo = J * f_diurnal
```

Por ello:

- `f_diurnal = 0.5` representa el promedio día/noche de un planeta rotante
  como la Tierra;
- `f_diurnal = 1.0` representa iluminación permanente, la aproximación usada
  por VULCAN para un planeta bloqueado por marea.

El ángulo cenital controla la trayectoria óptica mediante
`exp[-tau / cos(sl_angle)]`. Para TRAPPIST-1e usamos `48 deg`, interpretado
como un ángulo efectivo del hemisferio diurno. Esta elección está escrita en
los YAML, pero todavía necesita una fuente o prueba de sensibilidad específica.

**Interpretación:** el modelo actual sí distingue un planeta rotante de uno
bloqueado por marea en las tasas fotoquímicas medias. No representa el lado
nocturno, transporte horizontal, terminador ni circulación día-noche. Por
tanto, “TRAPPIST-1e bloqueado” significa aquí una columna 1D iluminada
permanentemente con geometría efectiva.

## Parámetros planetarios y condiciones mantenidas

| Magnitud | Earth-Sun | TRAPPIST-1e |
| --- | ---: | ---: |
| Radio planetario | `6.3781e8 cm` | `5.867852e8 cm` |
| Gravedad superficial | `980.0 cm s^-2` | `801.2287 cm s^-2` |
| Distancia orbital | `1 AU` | `0.02925 AU` |
| Radio estelar | `1 R_sun` | `0.1192 R_sun` |
| Perfil P-T-Kzz | Tierra | Tierra, controlado |
| Red química | SNCHO completa | SNCHO completa |
| Flujos A0-A3 | iguales | iguales |

Los parámetros físicos corregidos de TRAPPIST-1e están basados en Agol et al.
(2021). El perfil térmico y `Kzz` no se corrigieron porque se mantienen como
parte deliberada del experimento controlado.

## Estado de los resultados

La reproducción del 2026-06-15 produjo:

- cuatro casos Earth-Sun que alcanzaron `end_case = 1`;
- cuatro casos TRAPPIST-1e que terminaron en `end_case = 3` al superar
  `20000` pasos.

Los casos TRAPPIST-1e corregidos no deben describirse como convergidos bajo el
criterio global estricto de VULCAN. Cerca del límite de pasos, el criterio está
controlado por `C2H5` alrededor de `0.019 bar`, con una mezcla apenas superior
al umbral numérico `mtol_conv = 1e-16`. En la arquitectura actual del proyecto,
esto se trata como una aceptación con convergencia parcial documentada, no como
un fracaso del perfil completo.

Los productos, logs, configuraciones previas, manifiestos y comparación
cuantitativa se conservan en:

```text
Photochemical_Modeling/Results/Reproduction_2026-06-15/
```

## Distinción entre hechos, decisiones e incertidumbres

### Hechos derivados de archivos y código

- Se utiliza la red `SNCHO_full_photo_network.txt`.
- Los productos contienen 100 especies, 1284 reacciones y 120 capas.
- Solo cambian `NH3` y `N2O` entre las condiciones de frontera A0-A3.
- VULCAN escala los espectros superficiales mediante `(R_star/a)^2`.
- `f_diurnal` multiplica directamente las tasas de fotólisis.
- Los casos TRAPPIST-1e actuales usan `f_diurnal = 1`.

### Decisiones del proyecto

- Usar abundancias de Haqq-Misra (2022) para construir factores efectivos, no
  como condiciones de frontera.
- Usar el índice S2 `15x` de Haqq-Misra (2025) como envolvente extrema.
- Mantener el perfil terrestre P-T-Kzz para aislar inicialmente la respuesta
  fotoquímica.
- Representar TRAPPIST-1e como una columna permanentemente iluminada.

### Preguntas aún abiertas

- Resolver la inconsistencia entre los `alpha` declarados y los flujos
  implementados de `N2O`.
- Registrar la referencia y el script exactos usados para convertir el producto
  Mega-MUSCLES en `TRAPPIST1_surface.txt`.
- Confirmar la edición correcta del espectro Gueymard.
- Justificar o someter a sensibilidad `sl_angle = 48 deg`.
- Cuantificar el efecto de la convergencia parcial de TRAPPIST-1e sobre `N2O`,
  `NH3` y los espectros de transmisión.
- Sustituir eventualmente el perfil P-T-Kzz terrestre por estructuras
  climáticamente autoconsistentes y evaluar cuánto cambia la conclusión.

## Archivos principales

| Papel | Archivo |
| --- | --- |
| Diseño científico A0-A3 | nota externa `Diseño de escenarios ExoFarm por flujos.md` |
| Configuración planetaria | `Photochemical_Modeling/Config/planets/` |
| Condiciones de frontera | `Photochemical_Modeling/Config/Boundary_Conditions/` |
| Adaptador YAML a VULCAN | `VULCAN/run_case.py` |
| Red química | `VULCAN/thermo/SNCHO_full_photo_network.txt` |
| Perfil P-T-Kzz | `VULCAN/atm/atm_Earth_Jan_Kzz.txt` |
| Espectro solar | `VULCAN/atm/stellar_flux/Gueymard_solar.txt` |
| Espectro TRAPPIST-1 superficial | `VULCAN/atm/stellar_flux/TRAPPIST1_surface.txt` |
| Producto ECSV preservado | `Photochemical_Modeling/Config/Stellar_Spectra/trappist-1_model_const_res_v07.ecsv` |
| Auditoría de reproducción | `docs/vulcan_profile_reproduction_2026-06-15.md` |

## Referencias metodológicas

- Tsai et al. (2017), descripción original de VULCAN.
- Tsai et al. (2021), extensión fotoquímica de VULCAN.
- Haqq-Misra et al. (2022), escenarios agrícolas ExoFarm y abundancias objetivo.
- Haqq-Misra et al. (2025), escenarios de tecnosfera e índice agrícola S2.
- Agol et al. (2021), parámetros revisados del sistema TRAPPIST-1,
  <https://doi.org/10.3847/PSJ/abd022>.
