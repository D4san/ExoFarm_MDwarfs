# Un único sumidero superficial NH3 debilitado: v_dep = 0.65 cm/s

**Fecha:** 2026-10-13. **Registro de diseño:**
`nh3_weakened_surface_sink_vdep_0p65_20261013`.
**Estado:** valor seleccionado como hipótesis de sensibilidad; sin implementar
en las fronteras canónicas y sin simulaciones nuevas.

**Ampliación solicitada, mismo día:** el valor se incorpora a la
[propuesta de fase adicional de captación superficial reducida](nh3_reduced_capture_extra_phase_proposal_2026-10-13.md),
con parejas A0-A3 de referencia y debilitadas. Se documentan plausibilidad
condicionada, implicaciones y controles; la fase sigue sin ejecutar.

Se selecciona **`v_dep(NH3) = 0.65 cm s^-1`** para una futura sensibilidad
separada. Su interpretación es una reducción de la captación superficial
efectiva en una atmósfera oxidante, motivada por un océano superficial
enriquecido en NHx y cercano al punto de compensación con el aire. La
captación terrestre y la química atmosférica permanecen activas.

La cifra es una **inferencia de diseño condicionada**, obtenida con una
partición explícita del coeficiente de referencia y una ancla marina
publicada. Ninguna de las fuentes revisadas mide `0.65 cm/s` como velocidad
global ni demuestra un océano global en ese estado. La hipótesis se puede
examinar con VULCAN; su viabilidad biogeoquímica requiere otro balance.

## Construcción del valor

**Hechos de fuentes.** La referencia local A0-A3 prescribe `1 cm/s` de
NH3; la [revisión de procedencia](nh3_deposition_velocity_provenance_and_physical_scenarios_2026-10-13.md)
comprueba que Hu et al. (2012), tabla 3 nota e, adopta ese valor por
solubilidad/reactividad. La atribución general de Tsai a Hauglustaine no
proporciona una calibración NH3 específica ni una partición océano/tierra.

Lee et al. (1998) estima una captación marina de aproximadamente `5 mm/s`,
equivalente a **`0.5 cm/s`**, alrededor de las Islas Británicas, combinando
experimentos en cámaras con resistencia de transporte en aire. Su intervalo
preliminar es `2-15 mm/s`; se leyó el resumen y los fragmentos públicos del
editor, no el artículo completo. El experimento empleó NH3 atmosférico alto
para minimizar la emisión frente a la captación. Fuente:
[Lee, resumen y métodos](https://doi.org/10.1016/S1352-2310(97)00277-X).

**Supuestos del proyecto.** Se toma una geometría terrestre redondeada,
`f_oc = 0.70`, `f_land = 0.30`, sin una categoría de hielo independiente.
El océano terrestre cubre aproximadamente el 71 % de la superficie
([NOAA](https://www.noaa.gov/jetstream/ocean)). Se supone la misma densidad
atmosférica inferior representativa sobre ambas superficies, para escribir

\[
v_{eff}=f_{oc}v_{oc,net}+f_{land}v_{land,net}.
\]

Se utiliza la estimación central marina de Lee como ancla de un control
idealizado con compensación despreciable. La extrapolación regional al
océano global y la equivalencia de alturas de intercambio son supuestos,
pendientes de validación. El componente terrestre se calibra para recuperar
la referencia global `1 cm/s`:

\[
\begin{aligned}
f_{oc}v_{oc,control} &= 0.70\times0.50=0.35\ {\rm cm\ s^{-1}},\\
f_{land}v_{land,control} &= 1.00-0.35=0.65\ {\rm cm\ s^{-1}},\\
v_{land,control} &= 0.65/0.30=2.17\ {\rm cm\ s^{-1}}.
\end{aligned}
\]

`2.17 cm/s` es un residual calibrado por unidad de área terrestre. No es
una medición continental ni un valor reconstruido de Tsai. En el límite
de pérdida oceánica neta despreciable, conservando ese residual terrestre,

\[
v_{eff,weak}=0.70\times0+0.30\times2.17
\simeq\boxed{0.65\ {\rm cm\ s^{-1}}}.
\]

El coeficiente se reduce un **35 %**. Esta fracción describe la pérdida
parametrizada **a una misma densidad NH3**, no una reducción calculada del
flujo real después de que la atmósfera se ajuste. Tampoco se deduce un
aumento de abundancia de `1/0.65`: las pérdidas químicas y el perfil cambian.

La fracción de océano no equivale a una fracción de pérdida. En esta
construcción el 70 % de área oceánica aporta el 35 % del coeficiente inicial.
El único valor seleccionado aquí es `0.65 cm/s`.

La incertidumbre preliminar de Lee impide interpretar esta cifra como una
estimación global precisa. Incluso el extremo marino `1.5 cm/s`, ponderado
por 0.70, excedería la referencia global y daría un residual terrestre
negativo. Esto muestra el límite de extrapolar ese intervalo a la partición;
no constituye un intervalo de incertidumbre del escenario seleccionado.

## Qué significa un océano cercano al punto de compensación

Con flujo positivo hacia abajo, el intercambio oceánico se escribe

\[
J_{oc,down}=k_{tr}(C_{air}-C_{eq}),\qquad
v_{oc,net}=k_{tr}\left(1-\frac{C_{eq}}{C_{air}}\right).
\]

`k_tr` tiene unidades de velocidad; `C_air` y `C_eq` son concentraciones
gaseosas expresadas en las mismas unidades. `C_eq` es la concentración en
aire en equilibrio con el NH3 disuelto, determinada por NHx acuático
(`NH3(aq)+NH4+`), pH, temperatura, salinidad y constante de Henry. Cuando
`C_eq` se acerca a `C_air`, disminuye la captación **neta**; en el límite
de igualdad el flujo neto es cero y la transferencia sigue siendo finita.

**Hecho de fuente.** Altieri et al. (2021), secciones 4-5, calcula flujos
pequeños hacia el océano en un transecto estival del Atlántico austral y
examina condiciones estacionales que podrían invertirlos. Sus resultados
respaldan el uso del punto de compensación, sin demostrar una saturación
global persistente. Fuente:
[Altieri, métodos y discusión](https://doi.org/10.1029/2020GL091963).

La expresión preferida para este diseño es **«captación oceánica neta
limitada por proximidad al punto de compensación»**. «Saturado» solo se
puede utilizar con esa definición operacional. No se ha alcanzado una
solubilidad máxima ni se ha establecido un inventario NHx del océano entero.
El estado relevante es el agua que intercambia con el aire.

## Cómo puede coexistir con una atmósfera oxidante

**Mecanismo hipotético.** Una entrada o regeneración sostenida de NHx en
el agua superficial, suficientemente grande respecto a su transformación,
asimilación y exportación, elevaría el NH3 de equilibrio y reduciría el
gradiente de captación desde el aire. La composición oxidante de la
atmósfera puede mantenerse mientras cambia ese gradiente superficial.
En tierra también existe intercambio bidireccional: Sutton et al. (2013),
sección 3, relaciona el punto de compensación con el cociente NH4+/H+,
temperatura y manejo de los ecosistemas. Ese mecanismo es compatible con
la Tierra oxigenada, pero aquí se conserva el residual terrestre para
aislar la motivación oceánica. Fuente:
[Sutton, sección 3](https://pmc.ncbi.nlm.nih.gov/articles/PMC3682750/).

El balance que falta resolver es, por ejemplo,

\[
\frac{dN_{NHx,surf}}{dt}=
L_{NHx}+P_{remin}+A_{oc}J_{oc,down}
-U_{assim}-U_{nitrif}-E_{mix/export}.
\]

Aquí el inventario se expresa en mol N y cada término en mol N por unidad
de tiempo, con conversiones de área y tiempo coherentes. `L_NHx` representa
entradas externas; `P_remin`, regeneración; los términos `U` y `E` retiran
NHx del reservorio superficial. La nitrificación transforma NHx a otras
formas de N y puede sostener un sumidero de NHx aun con abundante N total.
Debe justificarse por qué entradas/regeneración y transporte permiten
mantener el punto de compensación a pesar de esos procesos.

**Límite de plausibilidad.** Haqq-Misra et al. (2022), sección 4, considera
implausibles las superficies globalmente saturadas en NH3 para su atmósfera
O2-N2. El escenario elegido es por tanto un **caso límite de sensibilidad**;
la lectura no permite anunciarlo como consecuencia probable de agricultura
intensiva. Tampoco presupone un océano anóxico. Fuente:
[Haqq-Misra, PDF p. 10](https://arxiv.org/pdf/2204.05360#page=10).

Si el NH3 atmosférico aumenta y `C_eq` permanece fijo, el océano vuelve a
captarlo. Mantener pérdida oceánica neta despreciable en diferentes A0-A3
exigiría que el estado del reservorio acompañara a cada atmósfera o un
mecanismo que lo mantuviera. Un coeficiente constante no verifica esa
condición de persistencia.

## Alcance exacto en VULCAN y presupuesto de fuentes

El término auditado es `F_NH3 - v_dep*n_NH3,0`; véanse
[lectura de BC](../VULCAN/build_atm.py) y
[operador de frontera](../VULCAN/op.py). `F` se expresa en moléculas
cm^-2 s^-1, `n` en moléculas cm^-3 y `v_dep` en cm s^-1. La propuesta cambia
solo el **coeficiente superficial efectivo NH3** a `0.65`. Conserva los
flujos del caso de referencia, espectro estelar, PT/Kzz, composición
oxidante inicial, red química y tratamiento de otros gases. La fotólisis
y reacciones oxidantes de la red continúan operando; sus tasas y los
perfiles resultantes deben recalcularse si se ejecuta la sensibilidad.
No se deduce la desaparición de todas las pérdidas atmosféricas ni un
tratamiento físico de lluvia o aerosoles a partir de este cambio.

**Dos niveles de interpretación.** Con `F` prescrito intacto, una futura
corrida sería una sensibilidad controlada al sumidero efectivo. El flujo
natural vigente ya incluye emisiones marinas; por ello la corrida no
representaría por sí sola un océano con intercambio neto cero. Para
realizar esa segunda interpretación hay que separar `F_land,emit` y
reemplazar la fuente marina por `f_oc*k_tr*C_eq`, junto con su captación,
sin doble conteo. El valor escogido queda congelado como coeficiente
fenomenológico; el cierre oceánico permanece pendiente.

No se crea una matriz de flujos nueva. El diseño vigente sigue siendo
`F_i(A_j)=F_i(A0)+alpha_i,j*Delta F_i,agri`. Una futura comparación agrícola
necesita un A0 con el mismo tratamiento de sumidero; A3 debilitado frente
a A0 canónico mezclaría el efecto de emisión con el cambio de superficie.
El valor se puede aplicar en una rama separada después de definir su
alcance; este documento no ejecuta una campaña ni selecciona otra estrella.

## Texto breve para presentar la hipótesis

> Exploramos una sensibilidad de NH3 con velocidad efectiva de deposición
> superficial de 0.65 cm/s, conservando la atmósfera oxidante y el resto del
> forzamiento del caso de referencia. El valor se construye al retirar una
> contribución oceánica idealizada de 0.35 cm/s del coeficiente global de
> 1 cm/s, utilizando una cobertura oceánica de 0.70 y una ancla marina de
> 0.50 cm/s. La motivación física es un océano superficial enriquecido en
> NHx y próximo al punto de compensación del intercambio aire-mar, mientras
> persiste la captación terrestre. Se trata de un caso límite condicionado;
> su viabilidad y duración requieren resolver el presupuesto NHx oceánico.

Esta redacción describe el **diseño**. Una publicación debe utilizar
«exploramos» después de ejecutar y validar la sensibilidad, y distinguir
claramente el coeficiente agregado de un intercambio oceánico acoplado.

## Evidencia y verificación

- [Manifiesto del valor, supuestos y límites](evidence/nh3_weakened_sink_2026-10-13/design_manifest.json).
- [Verificación reproducible de aritmética, unidades y entradas](evidence/nh3_weakened_sink_2026-10-13/verify_design.py),
  [resultado](evidence/nh3_weakened_sink_2026-10-13/design_verification.json).
- [Informe Huang/VULCAN y auditoría de cuatro Earth `.vul`](nh3_surface_sinks_huang_vulcan_review_2026-10-13.md),
  [script de auditoría](evidence/nh3_surface_sinks_2026-10-13/audit_nh3_surface_sinks.py)
  y [JSON de procedencia](evidence/nh3_surface_sinks_2026-10-13/nh3_surface_sink_audit.json).
- [Revisión de Hauglustaine/Hu/Lee](nh3_deposition_velocity_provenance_and_physical_scenarios_2026-10-13.md)
  y [manifiesto de fuentes](evidence/nh3_deposition_origin_2026-10-13/source_manifest.json).
- [Plantilla Tierra-Sol A3](../Photochemical_Modeling/Config/planets/earth_sun/input_earth_sun_A3.yml)
  y [runner Tierra-Sol](../Photochemical_Modeling/Scripts/Simulation/run_parallel_earth.py):
  referencias de configuración, no modificadas para esta propuesta.

La verificación es analítica y de integridad de archivos. No valida la
biogeoquímica del océano ni anticipa abundancias, espectros o detecciones.
Los Earth `.vul` citados siguen siendo `earth_20260615_pre_n2o_correction`;
su auditoría histórica no sustituye una nueva corrida de la matriz actual.

## Referencias adicionales de procedencia

- Tsai et al. (2021), *VULCAN: An Open-source, Validated Chemical Kinetics
  Python Code for Exoplanetary Atmospheres*: DOI
  [10.3847/1538-4357/ac29bc](https://doi.org/10.3847/1538-4357/ac29bc).
- Hu, Seager y Bains (2012), *Photochemistry in Terrestrial Exoplanet
  Atmospheres. I. Photochemistry Model and Benchmark Cases*: DOI
  [10.1088/0004-637X/761/2/166](https://doi.org/10.1088/0004-637X/761/2/166).
- Huang et al. (2022), *Assessment of Ammonia as a Biosignature Gas in
  Exoplanet Atmospheres*: DOI
  [10.1089/ast.2020.2358](https://doi.org/10.1089/ast.2020.2358).

Las fuentes sustentan mecanismos y anclas; la selección `0.65 cm/s` y su
partición terrestre/oceánica son inferencias explícitas de ExoFarm.
