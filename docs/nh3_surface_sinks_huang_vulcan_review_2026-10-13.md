# NH3: sumideros superficiales, saturación oceánica y escenarios hipotéticos

**Fecha:** 2026-10-13. **Registro:** `nh3_surface_sinks_review_20261013`.
**Alcance ejecutado:** revisión bibliográfica, lectura de código/BC y auditoría
de cuatro `.vul` existentes, con cálculos analíticos reproducibles. Las
sensibilidades propuestas permanecen sin ejecutar; A0-A3 conserva sus BC.

**Actualización de procedencia, mismo día:** la
[lectura de Hauglustaine y Hu](nh3_deposition_velocity_provenance_and_physical_scenarios_2026-10-13.md)
resuelve la limitación inicial de acceso. Hauglustaine no tabula NH3;
Hu prescribe `1 cm/s` por solubilidad/reactividad. La propuesta vigente
se basa en transporte y estado del reservorio oceánico; la malla heurística
de reducciones queda retirada como definición de escenarios físicos.
**Selección posterior:** el [diseño de un único valor debilitado](nh3_weakened_surface_sink_vdep_0p65_design_2026-10-13.md)
adopta `0.65 cm/s` como sensibilidad condicionada del coeficiente global,
con una partición oceánica/terrestre explícita. Sin implementación ni corridas.

La propuesta de reducir sumideros de NH3 es útil para estudiar cuánto depende
la acumulación atmosférica de la eficiencia superficial. La implementación
actual usa una velocidad efectiva de `1 cm s^-1`, compartida por A0-A3, sin
resolver por separado océano, suelo y vegetación. El caso de velocidad cero
define un límite del modelo. Su interpretación como océano saturado exige un
argumento adicional sobre inventario, intercambio y biogeoquímica. Haqq-Misra
et al. (2022), sección 5, advierte expresamente que las superficies saturadas
en NH3 son poco plausibles para su contexto O2-N2; el resultado favorable de
Huang corresponde a otro entorno planetario.

## Procedencia: qué significa el flujo terrestre

**Hecho bibliográfico.** Tsai et al. (2021), sección 3.3 y tabla 2, asignan
`F_NH3 = 1.5e9 molecules cm^-2 s^-1` y `v_dep = 1 cm s^-1` a la validación
terrestre de VULCAN. La tabla atribuye las emisiones a Seinfeld & Pandis
(2016) y las velocidades a Hauglustaine et al. (1994). Son una emisión
impuesta y una pérdida dependiente de la concentración. La tabla no obtiene
ese flujo descontando un sumidero oceánico ni proporciona su descomposición
por superficie. Fuente: [Tsai et al.](https://doi.org/10.3847/1538-4357/ac29bc),
[PDF revisado, p. 17](https://arxiv.org/pdf/2108.01790#page=17).

**Decisión del proyecto y reproducción aritmética.** Nuestro A1 utiliza
`1.30e10`, no el flujo de la validación original. La nota de diseño del vault
`03 Proyectos/Tecnosignatures/Biblio y Conceptos/Diseño de escenarios ExoFarm
por flujos.md` prescribe fondo natural más agricultura, excluyendo el
componente antropogénico no agrícola. Haqq-Misra et al. (2022), sección 2,
reporta un presupuesto de `58 Tg N yr^-1`: 19 % natural y 65 % agrícola. La
selección del 84 % es una decisión de ExoFarm. Fuente:
[Haqq-Misra et al., pp. 4-5](https://arxiv.org/pdf/2204.05360#page=4).

Con un átomo de N por molécula de NH3,

\[
F_{NH_3}=\frac{\dot M_N\,10^{12}}{14.0067}
\frac{N_A}{(5.101\times10^{18})(31557600)},
\]

donde `M_N` se expresa en Tg N/año, la masa molar en g/mol, el área en cm² y
el año en segundos. Se reproducen los valores redondeados de los BC:

| Componente | Tg N/año | Flujo calculado, moléculas cm^-2 s^-1 |
| --- | ---: | ---: |
| A0, 19 % natural | 11.02 | 2.9433e9 |
| Incremento agrícola, 65 % | 37.70 | 1.0069e10 |
| A1, natural más agricultura | 48.72 | 1.3013e10 |

Los demás escenarios conservan
`F_i(A_j) = F_i(A0) + alpha_i,j * Delta F_i,agri`.
El 19 % natural incluye fuentes marinas, entre otras: modificar solamente la
deposición preservaría esas emisiones por decisión de control experimental.
Un océano físicamente diferente podría cambiar ambos lados del intercambio.

El comentario heredado `NH3 17.9 Tg/yr` del archivo de frontera no deriva el
A1 actual. Se conserva como evidencia histórica; la procedencia vigente se
reconstruye con la nota de diseño, los BC y el presupuesto anterior.
La primera descarga de Hauglustaine encontró una barrera; la lectura
posterior del original muestra que su tabla 2 no incluye NH3. La tabla 3
de Hu separa las velocidades tomadas de Hauglustaine de las supuestas
por solubilidad/reactividad, categoría a la que pertenece NH3. Véase la
[revisión específica de procedencia](nh3_deposition_velocity_provenance_and_physical_scenarios_2026-10-13.md).

## Qué implementa el código y qué contienen los productos

**Resultado de inspección.** [build_atm.py](../VULCAN/build_atm.py) lee la
segunda columna como `bot_flux` y la tercera como `bot_vdep`. En
[op.py](../VULCAN/op.py), el término añadido a la celda inferior es

```python
diff[0] += (atm.bot_flux - y[0] * atm.bot_vdep) / dzi[0]
```

Por tanto,

\[
\Phi_{bot,NH_3}=F_{NH_3}-v_{dep}n_{NH_3}(z_0),
\]

con `n` en moléculas cm^-3. El producto `v_dep*n` es una pérdida en moléculas
cm^-2 s^-1. No hay variables de pH oceánico, NH4+ disuelto, capacidad del
reservorio o fracción de océano en esta condición de frontera. No se
identificó un término vertical independiente de lavado por lluvia de NH3 en
la ruta auditada. El coeficiente de frontera puede representar una pérdida
superficial efectiva; esta implementación no reproduce por sí sola el
tratamiento explícito de lluvia de Huang.

El [runner terrestre](../Photochemical_Modeling/Scripts/Simulation/run_parallel_earth.py)
copia las cuatro plantillas de
[Boundary_Conditions](../Photochemical_Modeling/Config/Boundary_Conditions/)
al archivo indicado por los
[YAML terrestres](../Photochemical_Modeling/Config/planets/earth_sun/).
Los `.vul` canónicos existentes confirman:

| Caso | F_NH3 impuesto | v_dep, cm/s | NH3 superficial, ppb | v_dep*n/F_NH3 |
| --- | ---: | ---: | ---: | ---: |
| A0 | 2.94e9 | 1 | 0.1070 | 0.8787 |
| A1 | 1.30e10 | 1 | 0.4650 | 0.8634 |
| A2 | 3.82e10 | 1 | 1.3146 | 0.8307 |
| A3 | 1.54e11 | 1 | 4.7187 | 0.7397 |

Los flujos están en moléculas cm^-2 s^-1. La última columna compara el flujo
de deposición prescrito con la emisión impuesta: no es una fracción oceánica
ni la fracción del inventario atmosférico eliminado. Los cuatro productos
tienen `end_case=1`. Sus A2/A3 conservan N2O histórico `3.35e9`/`1.20e10`;
esta auditoría mantiene el rótulo `earth_20260615_pre_n2o_correction` y la
[salvedad de procedencia](earth_sun_n2o_matrix_provenance_2026-07-20.md).

**Inferencia del proyecto.** La pérdida superficial tiene un peso grande en
estos estados guardados. Eso justifica evaluar su sensibilidad, pero todavía
no cuantifica la respuesta de una corrida nueva con menor deposición.

## Qué aporta Huang y cómo interpretarlo

**Hechos del artículo.** Huang et al. (2022), secciones 3.2-3.3 y 4.4,
separa un modelo de partición océano-atmósfera de su cálculo fotoquímico.
Compara deposición seca y húmeda activas con ambas anuladas para NH3. En su
caso H2 dominante alrededor de una M5V, la tabla 4-1 requiere `6.40e15`
con deposición frente a `1.44e10` moléculas cm^-2 s^-1 sin ella para obtener
5 ppm en promedio de columna. Fuente:
[Huang et al.](https://doi.org/10.1089/ast.2020.2358),
[tabla revisada, PDF p. 20](https://arxiv.org/pdf/2107.12424#page=20).

Ese valor de 5 ppm es un diagnóstico de su configuración JWST, no un umbral
universal para nuestras observaciones LIFE/JWST. Sus casos N2 y CO2 tampoco
constituyen una validación de nuestra atmósfera con 20 % de O2. La conexión
útil es la dependencia respecto a pérdidas superficiales; trasladar una
abundancia exige recalcular química, UV y estructura.

**Interpretación física.** La expresión superficie saturada describe aquí el
límite de pérdida neta superficial ineficiente. Un agua en equilibrio con una
presión parcial dada puede seguir admitiendo NH3 si esa presión aumenta o si
la biología transforma el nitrógeno disuelto. El equilibrio de intercambio,
el exceso de nutrientes y el límite de solubilidad son condiciones distintas.

Para aislar específicamente el océano, una condición bidireccional puede
escribirse, con signo positivo hacia la atmósfera,

\[
\Phi_{oc}=k_g(C_{eq}-C_{air}),\qquad
C_{eq}=\frac{[NH_3]_{aq}}{H^{cp}RT}.
\]

Aquí las concentraciones son mol/m³, `H^cp` es mol m^-3 Pa^-1 y `k_g` es
m/s; el flujo queda en mol m^-2 s^-1. La conversión al formato VULCAN
multiplica por `N_A/10^4`. Con `C_eq=C_air` el flujo neto desaparece; si
el océano consume NHx, el gradiente puede reaparecer. Esto es una propuesta
de interfaz, no código ya implementado. Altieri et al. (2021) calculan
sumideros en el transecto austral de verano y muestran condiciones que
pueden invertir el intercambio; un océano real puede actuar como fuente o
sumidero según su estado. Fuente:
[Altieri et al., secciones 4-5](https://doi.org/10.1029/2020GL091963).

## Consecuencias ambientales y escala del reservorio

**Química y cálculo ilustrativo.** El reservorio acuático comprende
`NHx = NH3(aq) + NH4+`. Con el pKa aproximado de 9.25 utilizado por Huang,

\[
f_{NH_3}=\frac{1}{1+10^{pK_a-pH}}.
\]

| pH ilustrativo | Fracción de NHx como NH3 libre |
| --- | ---: |
| 7.0 | 0.56 % |
| 8.1 | 6.61 % |
| 9.25 | 50.00 % |
| 10.0 | 84.90 % |

Son cálculos con pKa fijo de agua diluida aproximadamente a temperatura
ambiente. Un océano requiere correcciones por temperatura, salinidad y
escala de pH; no usar estos porcentajes como calibración de agua marina.

**Hechos ambientales y extrapolación condicionada.** El enriquecimiento en
NHx puede aumentar la producción biológica si otros recursos lo permiten;
la oxidación de amonio y la degradación de biomasa consumen oxígeno. NH3
libre es particularmente tóxico para numerosos organismos terrestres, con
respuesta dependiente del pH, la temperatura y la especie. Estos mecanismos
sugieren presión ecológica y riesgo de hipoxia para un océano con gran NHx;
no determinan una tasa de extinción ni tolerancias de organismos alienígenas.
Fuente: [EPA, Ammonia](https://www.epa.gov/caddis/ammonia).

La adición de NH3 puede consumir acidez, pero la nitrificación libera
protones:

\[
NH_4^+ + 2O_2 \rightarrow NO_3^- + 2H^+ + H_2O.
\]

El estado de pH requiere balance de alcalinidad y carbono. Una gran carga
de nitrógeno no fija por sí sola un océano alcalino. Tampoco un océano
anóxico garantiza sumidero cero: la disponibilidad de aceptores alternativos
y las rutas de pérdida de N siguen importando. Santoro et al. documentan
nitrificación, desnitrificación y anammox en el entorno de zonas oceánicas
deficientes en oxígeno. Fuente:
[Santoro et al. (2021)](https://doi.org/10.1029/2020GB006716).

Para dimensionar el límite, el inventario de `6e18 mol` discutido por Huang,
distribuido en `1.335e21 L` de océano, equivale a **4.494 mM NHx**, o
**62.95 mg N/L**. Es una traducción aritmética de ese inventario con océano
uniforme; no es una concentración universal de saturación. Altieri mide
hasta 0.36 µM en su transecto de verano: son contextos muy distintos y esa
observación regional no define todo el océano terrestre.

Si ese inventario se construyera desde cero únicamente a partir de nuestros
flujos atmosféricos A1/A3, reteniendo cada molécula y sin pérdidas, se
necesitarían como mínimo aproximadamente **1.73 millones / 146 mil años**.
Son cotas condicionadas, no una predicción: excluyen aportes hídricos,
producción oceánica y reservorios previos. Subrayan la diferencia entre
mantener una abundancia atmosférica y crear un reservorio planetario.

## Propuesta revisada y selección de una sensibilidad condicionada

La solicitud posterior del usuario prioriza escenarios con fundamento
físico. La malla heurística inicial `0.1/0.01 cm/s` queda retirada como
propuesta vigente. La [revisión de procedencia](nh3_deposition_velocity_provenance_and_physical_scenarios_2026-10-13.md)
recomienda separar transporte oceánico, concentración de compensación y
consumo del reservorio. Lee et al. (1998) proporciona una ancla preliminar
de captación marina de `0.5 cm/s`, con rango `0.2-1.5 cm/s`; estos valores
pertenecen al componente oceánico y no reemplazan directamente el BC global.
La solicitud posterior de un único valor se concreta en el
[diseño `0.65 cm/s`](nh3_weakened_surface_sink_vdep_0p65_design_2026-10-13.md):
de la referencia global `1` se retira `0.70*0.50=0.35 cm/s` de contribución
oceánica idealizada y se conserva el residual terrestre. La motivación es
proximidad al punto de compensación; la partición y extrapolación regional
son supuestos explícitos del proyecto. La cifra está seleccionada como
sensibilidad efectiva, sin presupuesto oceánico físico resuelto.

La pregunta revisada es: *cómo cambia la pérdida neta cuando un océano
definido por NHx, pH, temperatura y salinidad se aproxima al equilibrio con
la atmósfera, manteniendo explícitos el transporte y los sumideros terrestres?*
El límite de deposición global cero sigue siendo un diagnóstico matemático;
un océano en equilibrio no elimina el consumo terrestre. Los estados físicos
y el presupuesto de fuentes todavía requieren definición. Cualquier
atribución de enriquecimiento agrícola necesita controles A0 comparables.
Los productos futuros requieren una campaña y rutas separadas; no se
ejecutaron sensibilidades ni se cambiaron las entradas A0-A3.

Para asignar una reducción al océano hace falta una descomposición, por
ejemplo `v_eff = f_oc*v_oc + f_land*v_land`, bajo el supuesto adicional de
aire superficial representativo de ambas superficies. La fracción oceánica
de área no equivale a su fracción de pérdida. El paso físico posterior
debería incluir intercambio bidireccional, NHx acuático, pH/temperatura,
aportes y consumo, manteniendo separados los sumideros terrestres.

La extensión a N2O debe partir de producción y consumo microbianos o
rendimientos de desnitrificación, no de trasladar el apagado de NH3. El
estado bajo O2 puede alterar producción y consumo de N2O; Santoro documenta
ambos procesos. No permite asumir un aumento monotónico del flujo. Esta
pregunta queda abierta y no modifica la matriz N2O vigente.

## Evidencia y reproducción

Los resultados y hashes están en
[nh3_surface_sink_audit.json](evidence/nh3_surface_sinks_2026-10-13/nh3_surface_sink_audit.json).
El [script de auditoría](evidence/nh3_surface_sinks_2026-10-13/audit_nh3_surface_sinks.py)
lee los cuatro BC y los cuatro
[Earth `.vul` existentes](../Photochemical_Modeling/Results/Outputs/).
Ejecutado con Python 3.14.3 y NumPy disponible:

```powershell
.\.venv\Scripts\python.exe docs/evidence/nh3_surface_sinks_2026-10-13/audit_nh3_surface_sinks.py
```

Exit 0; comprobaciones de conversión, igualdad de BC/snapshots de NH3,
deposición y terminación guardada aprobadas. No se cambió ninguna entrada
del modelo ni se generaron atmósferas, espectros o retrievals. Los PDF de
Huang y Tsai se extrajeron y sus tablas se inspeccionaron visualmente; los
archivos temporales y sus hashes se registran en el JSON. No hay una figura
científica nueva de sensibilidad que pueda confundirse con una simulación.

Referencias adicionales: [metodología fotoquímica del proyecto](photochemical_profiles_methodology.md),
[README de Etapa I](../Photochemical_Modeling/README.md),
[estado central](project_status_tracker.md) y
[registro de campañas](../experiments/README.md).
