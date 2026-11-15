# De dónde procede v_dep(NH3) = 1 cm/s y cómo fundamentar escenarios

**Fecha:** 2026-10-13. **Registro:** `nh3_deposition_origin_review_20261013`.
**Alcance:** lectura de Hauglustaine (1994) y Hu et al. (2012), revisión de
las fuentes de intercambio marino y corrección de la propuesta de
sensibilidades. No se modificaron BC ni se ejecutaron modelos atmosféricos.

La atribución general de la tabla de Tsai a Hauglustaine no proporciona una
derivación específica del `1 cm/s` de NH3. El artículo citado de Hauglustaine
no incluye NH3 en su tabla de deposición. El antecedente que sí documenta
ese valor es Hu et al.: allí se prescribe por la solubilidad y reactividad
del gas y se explica un marco de resistencias. Esta distinción cambia el
diseño propuesto: los escenarios deben modificar parámetros de transporte
y del reservorio superficial, no asignar factores de reducción sin una
condición física identificada.

**Selección posterior, mismo día:** el usuario solicita un único valor.
El [diseño `0.65 cm/s`](nh3_weakened_surface_sink_vdep_0p65_design_2026-10-13.md)
concreta una sensibilidad condicionada: retirar una contribución marina
idealizada de `0.70*0.50=0.35 cm/s` y conservar el residual terrestre de la
referencia global. La cifra está seleccionada; la partición es una inferencia
de proyecto y el presupuesto oceánico sigue pendiente. Sin corridas ni
modificación de BC.

## Cadena de referencias comprobada

**Hecho de la fuente.** Tsai et al. (2021), tabla 2, publica `NH3` con
emisión `1.5e9 molecules cm^-2 s^-1` y velocidad `1 cm s^-1`. La nota b
de la columna de velocidades atribuye sus valores a Hauglustaine et al.
(1994). Su sección 3.3.1 también sigue el planteamiento terrestre de
Hu et al. (2012). La tabla no detalla una calibración individual de NH3.
Fuente: [Tsai, tabla 2 y sección 3.3.1](https://arxiv.org/pdf/2108.01790#page=17),
DOI [10.3847/1538-4357/ac29bc](https://doi.org/10.3847/1538-4357/ac29bc).

**Hecho del original leído.** Hauglustaine, Granier, Brasseur y Mégie (1994),
*The importance of atmospheric chemistry in the calculation of radiative
forcing on the climate system*, sección 2.3 y tabla 2, prescribe velocidades
para océano, continente y nieve/hielo. La unidad de la tabla es `10^-2 m/s`,
equivalente a `cm/s`. La tabla atribuye sus datos a Hough (1991) y
Kanakidou et al. (1991). Sus cambios estacionales de deposición se limitan
a la cobertura de nieve y hielo del modelo. NH3 no figura entre las doce
especies tabuladas. No contiene un cálculo de `v_dep(NH3)=1`.
Fuentes: [DOI 10.1029/93JD02987](https://doi.org/10.1029/93JD02987),
[PDF original, p. 1176 / página PDF 4](https://pure.mpg.de/rest/items/item_3191214_1/component/file_3574014/content#page=4).

Por ejemplo, el HNO3 sí tiene valores `1/4/0.5 cm/s` para
océano/continente/nieve. Ese `1` pertenece a otra especie y superficie.
No permite inferir automáticamente un coeficiente oceánico de NH3.

**Hecho de una fuente específica de NH3.** Hu, Seager y Bains (2012),
tabla 3, prescribe `v_dep(NH3)=1 cm/s` con superíndice **e**. La nota **c**
corresponde a las velocidades tomadas de Hauglustaine; la nota **e** dice:

> Dry deposition velocities are assumed by considering the solubility and reactivity of gases (see Appendix C).

La distinción entre notas se verificó en la página renderizada. Fuente:
[Hu, tabla 3, PDF p. 15](https://epacris.ipac.caltech.edu/pdf/Photochem1_Model.pdf#page=15),
DOI [10.1088/0004-637X/761/2/166](https://doi.org/10.1088/0004-637X/761/2/166).

**Inferencia delimitada.** El número puede justificarse como una prescripción
de captación eficiente para un gas muy soluble/reactivo. No se ha demostrado
que Tsai reconstruya un cálculo único de Hu con unos parámetros definidos.
Tampoco hay evidencia en estas tablas de que el valor sea una medición
oceánica universal o un coeficiente ajustado a la fracción de océano terrestre.

## El cálculo físico disponible en Hu

El apéndice C de Hu, ecuaciones C1-C3, expresa la deposición como pasos de
transporte y captación en serie:

\[
v_{dep}^{-1}=r_b+r_c, \qquad
r_b=\frac{5\,Sc^{2/3}}{u_*}.
\]

`r_b` es la resistencia de la subcapa cuasilaminar; `Sc` es el número de
Schmidt en aire, razón entre viscosidad cinemática y difusividad molecular;
`u_*` es la velocidad de fricción, vinculada al viento y la rugosidad.
Hu propone explorar `u_*=0.1-1 m/s` como parámetro libre. **No es la
velocidad del viento medida a 10 m** y no debe sustituirse por ella.

Para el océano presenta

\[
r_c=\frac{1}{k_G}+\frac{1}{k_LH},
\]

donde `k_G` y `k_L` son coeficientes de transferencia de masa de gas y
líquido y `H` es la constante de Henry adimensional en esa formulación.
La expresión debe conservar su convención de solubilidad: no introducir
directamente una constante de Henry dimensional sin convertirla.

Con resistencias en s/m, el resultado es m/s. `1 cm/s = 0.01 m/s`
equivale a una resistencia total de **100 s/m**. Ese número no identifica
una combinación única de viento, rugosidad, solubilidad o captación. Para
otro estado superficial hay que calcular nuevas resistencias o determinar
una velocidad mediante observaciones comparables.

Fuente: [Hu, apéndice C, PDF p. 26](https://epacris.ipac.caltech.edu/pdf/Photochem1_Model.pdf#page=26).
Su figura 8 ilustra otros gases a 273.15 K, 1 atm, océano con pH aproximado
6.5 y tierra desértica. No es una curva de NH3 en el océano terrestre actual.
El cierre del apéndice advierte que la velocidad efectiva puede ser menor
si falta una pérdida efectiva en la superficie y esta se encuentra saturada.

Hay que respetar además la altura de referencia. Hu relaciona la capa
inferior del modelo con la superficie. Otros esquemas incorporan una
resistencia aerodinámica `r_a` entre alturas. Su integración con VULCAN
debe comprobar que no duplique el transporte ya representado mediante Kzz.

## Una ancla marina cuantitativa y sus límites

Lee et al. (1998), *Exchange of ammonia at the sea surface: a preliminary
study*, determina captación de NH3 por agua marina en cámaras de laboratorio
y combina la resistencia superficial con una estimación del transporte en
aire. Para las aguas alrededor de las Islas Británicas obtiene una velocidad
media aproximada de **5 mm/s**, con rango de incertidumbre **2-15 mm/s**:

| Estimación publicada | mm/s | cm/s | Resistencia total equivalente, s/m |
| --- | ---: | ---: | ---: |
| Extremo inferior | 2 | 0.2 | 500 |
| Central | 5 | 0.5 | 200 |
| Extremo superior | 15 | 1.5 | 66.7 |

Fuente primaria: [Lee et al., resumen y fragmentos de métodos](https://doi.org/10.1016/S1352-2310(97)00277-X).
Se revisó el contenido disponible del editor, no la totalidad de sus nueve
páginas. Es un intervalo preliminar de ese estudio, no un intervalo de
confianza global ni una calibración para cualquier planeta.

En sus cámaras se empleó NH3 atmosférico suficientemente alto para hacer
despreciable la emisión frente a la captación. El coeficiente representa
por tanto transferencia/captación bajo ese régimen. El estudio también
considera un punto de compensación y reconoce posibles condiciones de
emisión marina. No corresponde a un océano saturado con deposición cero.

Esta referencia ofrece una ancla defendible para una sensibilidad de
**transporte oceánico** (`0.2/0.5/1.5 cm/s`). No son tres valores nuevos
del `bot_vdep` global: primero se necesita separar océano y tierra.

## Acumulación oceánica: modificar el gradiente, además del transporte

Una condición marina con signo positivo hacia la atmósfera es

\[
\Phi_{oc}=k_{tr}(C_{eq}-C_{air}).
\]

Con `k_tr` en m/s y concentraciones equivalentes en aire en mol/m³,
`Phi_oc` queda en mol m^-2 s^-1. La cantidad `C_eq` se calcula a partir de
`NHx=NH3(aq)+NH4+`, pH, temperatura, salinidad y equilibrio de Henry. Si se
expresa la pérdida neta como `v_net*C_air`, resulta

\[
v_{net}=k_{tr}\left(1-\frac{C_{eq}}{C_{air}}\right).
\]

Así se distinguen una transferencia lenta y una pérdida neta pequeña por
proximidad al equilibrio. En equilibrio, `v_net=0` aunque `k_tr` siga siendo
finito. Si el reservorio produce `C_eq>C_air`, el océano emite. Una velocidad
positiva constante multiplicada por `C_air` no representa esa reversión.

Johnson (2010) proporciona una parametrización de transferencia dependiente
de viento, temperatura, salinidad y propiedades del gas; Altieri et al.
(2021) la usa con observaciones de NHx marino y NH3 atmosférico. Esto
fundamenta escenarios por estado del océano. Fuentes:
[Johnson (2010)](https://doi.org/10.5194/os-6-913-2010),
[Altieri (2021), secciones 4-5](https://doi.org/10.1029/2020GL091963).

Las condiciones de Altieri son regionales y estacionales. No deben
combinarse sin justificación con el coeficiente de captación de Lee como
si ambos describieran un único océano global.

## Propuesta vigente para ExoFarm

La malla anterior de `0.1/0.01 cm/s` queda retirada como propuesta de
escenarios físicos. La referencia canónica `1 cm/s` se conserva. Las
hipótesis físicas que fundamentan el diseño y su posterior acoplamiento son:

| Hipótesis | Qué se especifica | Qué diferencia física se estudia |
| --- | --- | --- |
| Captación marina eficiente | Meteorología y resistencias o ancla marina publicada; NHx bajo | Capacidad del transporte para retirar NH3 de la atmósfera |
| Reservorio marino enriquecido | NHx y estado pH/T/salinidad, conservando el transporte comparable | Acercamiento al punto de compensación y reducción de pérdida neta |
| Pérdida biogeoquímica limitada | Entradas de N y capacidad/velocidad de consumo del reservorio | Evolución del NHx y posible persistencia del equilibrio o emisión |

El segundo caso es la prueba más directa de la idea del usuario. Debe
calcularse el punto de compensación para una concentración de NHx definida,
no fijar de antemano cuánto se desea reducir `v_dep`. El tercero requiere un
balance del reservorio; ninguna ausencia de sumideros se deduce solamente
de la ecuación de transferencia.

Para una atmósfera 1D representativa y sin hielo, una simplificación sería

\[
\Phi_{bot}=F_{land,emit}+f_{oc}k_{tr}C_{eq}
-\left(f_{oc}k_{tr}+f_{land}v_{land}\right)C_{air},
\]

con todas las cantidades en unidades coherentes. La tierra conserva una
captación separada. Hay que documentar fracciones de área, representatividad
del aire inferior y altura de intercambio, y convertir finalmente a las
unidades VULCAN. Un océano en equilibrio no elimina la pérdida terrestre.

**Restricción de balance.** El fondo natural actual de NH3 incluye emisiones
marinas. Si se reemplazan por intercambio bidireccional, hay que separar
esa contribución del flujo prescrito para evitar contar dos veces la emisión
oceánica. Los `19/65 %` de la matriz no proporcionan por sí solos esa
descomposición. Se requieren fuentes terrestres/marinas y un control de
referencia antes de comparar enriquecimiento agrícola.

El [valor efectivo seleccionado después de esta lectura](nh3_weakened_surface_sink_vdep_0p65_design_2026-10-13.md)
es `0.65 cm/s`, derivado de una partición idealizada del control. Su
interpretación oceánica física aún requiere definir NHx y su presupuesto,
calcular `k_tr` y `C_eq`, y comprobar el acoplamiento con los sumideros
terrestres. La sensibilidad agregada y una frontera bidireccional acoplada
son niveles de modelado distintos. No se implementa ni ejecuta una campaña.

## Evidencia y verificación

- [Auditoría previa de BC y cuatro Earth `.vul`](nh3_surface_sinks_huang_vulcan_review_2026-10-13.md).
- [Código de la frontera VULCAN](../VULCAN/build_atm.py) y
  [término de intercambio](../VULCAN/op.py): implementación actual `F-v*n`.
- [Manifiesto de lectura y conversiones](evidence/nh3_deposition_origin_2026-10-13/source_manifest.json):
  identificadores, archivos, tamaños, SHA-256, páginas y conversiones.
- PDF completos de Hauglustaine y Hu descargados de repositorios públicos,
  texto extraído y tabla 2/tabla 3/apéndice C inspeccionados visualmente.
  La unidad de la tabla de Hauglustaine y el superíndice e de NH3 en Hu
  se comprobaron en las páginas renderizadas.
- Lectura web de Lee, Johnson y Altieri con los límites indicados. Las
  conversiones `mm/s -> cm/s -> m/s -> resistencia s/m` se verificaron
  con valores simples; no implican una simulación atmosférica.

La conclusión trazable es que `1 cm/s` conserva una justificación física
aproximada de captación eficiente, pero las referencias revisadas no
determinan un único estado oceánico que obligue a ese valor. La nueva
propuesta permite relacionar cada modificación con una propiedad del planeta.
