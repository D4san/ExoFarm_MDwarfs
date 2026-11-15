# Fase adicional: NH3 con captación superficial reducida

**Fecha:** 2026-10-13.
**Identificador de propuesta:** `nh3_reduced_capture_extra_phase_20261013`.
**Estado:** diseño propuesto y documentado; sin implementar ni ejecutar.

Esta fase amplía la matriz agrícola A0-A3 con un único valor de sumidero
superficial NH3 debilitado, **`0.65 cm/s`**, comparado con la referencia
`1 cm/s`. La pregunta es cuánto depende la respuesta atmosférica y espectral
de ExoFarm de la eficiencia de captación superficial, además de los flujos
agrícolas impuestos. La propuesta corresponde a escenarios de **plausibilidad
condicionada**: el intercambio reversible tiene fundamento físico; su
manifestación global persistente y la partición que produce el coeficiente
seleccionado siguen siendo hipótesis.

## Evaluación crítica de la idea

El [diseño del coeficiente](nh3_weakened_surface_sink_vdep_0p65_design_2026-10-13.md)
obtiene `0.65 = 1 - 0.70*0.50 cm/s`. `0.50 cm/s` es el ancla marina
regional preliminar de Lee et al. (1998); la geometría redondeada terrestre
y el residual continental se adoptan como supuestos de proyecto. La
captación oceánica neta se aproxima a cero en esa construcción límite,
mientras se conserva la captación terrestre. La cifra tiene una razón
trazable, pero carece de una calibración global independiente. Fuente:
[Lee](https://doi.org/10.1016/S1352-2310(97)00277-X).

**Hecho de fuente.** Altieri et al. (2021) calcula intercambio oceánico
próximo al equilibrio en condiciones regionales y estudia cómo un cambio
estacional del NHx marino podría invertir el flujo. Esto respalda una
captación neta pequeña en algunos entornos oxigenados de la Tierra, sin
establecer ese estado sobre todo el océano. Fuente:
[Altieri, secciones 4-5](https://doi.org/10.1029/2020GL091963).

**Inferencia del proyecto.** Una reducción moderada del coeficiente global
es una extensión razonable para comprobar la sensibilidad del experimento.
Su motivación puede ser el aumento del punto de compensación en superficies
enriquecidas en NHx. La categoría «plausible» debe ir acompañada de los
supuestos que hacen posible y sostienen ese estado. Haqq-Misra et al. (2022)
considera implausibles las superficies globalmente saturadas de NH3 para
O2-N2; por eso no se afirma una saturación universal ni una consecuencia
automática de A3. Fuente:
[Haqq-Misra, sección 4](https://arxiv.org/pdf/2204.05360#page=10).

Una misma velocidad agregada puede representar distintas combinaciones de
captación oceánica y terrestre. La atribución al océano es la motivación
elegida para este diseño, no una identificación que pueda hacer VULCAN
desde el coeficiente global. Tampoco se establece que el planeta haya
perdido oxígeno atmosférico o que toda su superficie marina sea anóxica.

## Matriz propuesta y comparación que permite

La fase conserva la ecuación agrícola vigente
`F_i(A_j)=F_i(A0)+alpha_i,j*Delta F_i,agri`. Añade un eje de captación,
sin redefinir A0-A3 ni introducir otro forzamiento N2O.

| Escenario de emisión | Referencia NH3, cm/s | Caso adicional NH3, cm/s | Identidad del caso adicional |
| --- | ---: | ---: | --- |
| A0 | 1.00 | 0.65 | `A0_NH3D065` |
| A1 | 1.00 | 0.65 | `A1_NH3D065` |
| A2 | 1.00 | 0.65 | `A2_NH3D065` |
| A3 | 1.00 | 0.65 | `A3_NH3D065` |

Son cuatro casos adicionales por entorno estelar seleccionado, junto con
cuatro referencias emparejadas. La estrella y la campaña de ejecución
quedan pendientes. En cada pareja se conservan el mismo flujo NH3 y N2O,
otros BC, SED, PT/Kzz, composición inicial oxidante y red fotoquímica. Se
cambia únicamente `v_dep(NH3)` y se recalcula la química resultante.

El A0 debilitado proporciona un control necesario para contrastar las
respuestas A1-A3 bajo la misma superficie. Es un **control contrafactual**;
no afirma que un planeta preagrícola tuviera un océano enriquecido por
agricultura. Comparar A3 debilitado con A0 de referencia introduciría a
la vez diferencias de emisión y captación.

Para una cantidad atmosférica positiva `Q`, por ejemplo columna NH3, se
pueden registrar el cociente por cambio de sumidero y la perturbación
respecto a A0 para cada captación:

\[
R_{sink,j}=\frac{Q(A_j,0.65)}{Q(A_j,1.00)},\qquad
G_{agri,j}(v)=\frac{Q(A_j,v)}{Q(A_0,v)}.
\]

Comparar `G_agri,j` entre ambas captaciones permite identificar cuánto
depende el contraste agrícola de la hipótesis superficial. Es una
interpretación del experimento controlado, no una atribución causal única
de agricultura a partir de un espectro observado.

## Implicaciones atmosféricas y observacionales

Se espera que una menor pérdida superficial favorezca la acumulación de
NH3 para un mismo flujo, pero su magnitud, perfil y acoplamientos químicos
deben salir de las corridas. Una referencia analítica simple usa una columna
`N`, una altura efectiva `H` y una pérdida química de primer orden `k`:

\[
\frac{dN}{dt}=F-\left(\frac{v}{H}+k\right)N,\qquad
\frac{N_{weak}}{N_{ref}}=
\frac{v_{ref}+kH}{v_{weak}+kH}.
\]

Con `v` en cm/s, `H` en cm y `k` en s^-1, ambos términos del denominador
son velocidades. Si `F`, `H` y `k>=0` permanecen fijos, el cociente está
entre 1 y **`1/0.65 = 1.538`**. El extremo corresponde a pérdida dominada
por deposición. Es un diagnóstico de caja lineal; **no es un límite
universal ni una predicción de VULCAN**, donde pueden cambiar oxidantes,
producción química, transporte y forma del perfil.

Por tanto, este valor examina un debilitamiento moderado. El posible
incremento de columna o de bandas NH3 no garantiza una mejora proporcional
de S/N ni evidencia de detección. Habría que evaluar los espectros, ruido,
solapamientos moleculares y ajuste de perfiles. La fotólisis y la química
oxidante continúan activas; la respuesta N2O podría variar indirectamente
por la red química aunque su flujo impuesto no cambie.

Mantener PT/Kzz preserva el experimento controlado. El modelo no calcularía
por ello un nuevo clima, nubosidad, aerosoles o daño ecológico. Una respuesta
espectral pequeña también sería informativa: cuantificaría la robustez de
las conclusiones frente a esta incertidumbre de captación.

## Implicaciones ambientales: condiciones y consecuencias posibles

La explicación oceánica exige sostener NHx en el agua que intercambia con
el aire frente a asimilación, nitrificación y mezcla/exportación. Una
entrada o regeneración elevada de NHx podría contribuir a ello. El punto
de compensación también depende de pH, temperatura y salinidad. Si aumenta
NH3 en el aire mientras el reservorio permanece fijo, se restablece el
gradiente de absorción; la captación débil puede ser transitoria.

**Hechos ambientales generales.** El exceso de NHx puede estimular
producción biológica, consumir oxígeno disuelto durante nitrificación y,
a concentraciones suficientes, provocar toxicidad acuática. La fracción
NH3 no ionizada y sus efectos dependen del estado del agua. La EPA describe
estas vías en aguas receptoras y ecosistemas acuáticos terrestres; sus
umbrales de agua dulce no se trasladan al océano de un exoplaneta.
Fuentes: [EPA CADDIS](https://www.epa.gov/caddis/ammonia),
[EPA, efectos acuáticos](https://www.epa.gov/wqc/aquatic-life-criteria-ammonia).

**Implicación condicionada.** Si la hipótesis fuera consecuencia de un
enriquecimiento planetario persistente, sugeriría un ciclo del nitrógeno
fuertemente perturbado y merecería estudiar eutrofización, demanda de
oxígeno y efectos ecológicos. **El coeficiente `0.65 cm/s` por sí solo no
determina concentración acuática, hipoxia, toxicidad ni colapso de la
biosfera.** Algunos procesos también retiran NHx y limitan su acumulación;
no se puede presentar el debilitamiento como un destino inevitable.

## Condiciones para ejecutar e interpretar la fase

1. Seleccionar el entorno estelar y registrar una campaña separada;
   mantener el identificador `NH3D065` fuera de los productos canónicos.
2. Construir parejas con exactamente las mismas entradas actuales salvo
   el coeficiente NH3. Los Earth A2/A3 de junio son
   `earth_20260615_pre_n2o_correction` y no sirven como controles actuales
   sin resolver la diferencia N2O descrita en la
   [nota de procedencia](earth_sun_n2o_matrix_provenance_2026-07-20.md).
3. Validar los perfiles y el balance de pérdidas, y comparar abundancia
   superficial, perfil vertical, columna NH3 y respuesta de otros gases.
4. Evaluar espectros y ruido solo después de aceptar los perfiles;
   conservar la distinción entre S/N diagnóstico y detección por retrieval.
5. Para sostener la etiqueta oceánica física, separar la emisión marina
   ya presente en el flujo natural y cerrar el intercambio bidireccional
   con NHx/pH/T/salinidad y consumo del reservorio. Con los flujos prescritos
   intactos, esta fase evalúa únicamente el coeficiente efectivo.

La solicitud actual autoriza **proponer y documentar** la fase. Se han
registrado su matriz, controles y preguntas físicas. No se han cambiado
fronteras, ejecutado modelos ni iniciado productos espectroscópicos.

## Evidencia asociada

- [Valor único y fundamento de la partición](nh3_weakened_surface_sink_vdep_0p65_design_2026-10-13.md).
- [Manifiesto de diseño, matriz y diagnóstico lineal](evidence/nh3_weakened_sink_2026-10-13/design_manifest.json).
- [Verificación analítica y de integridad](evidence/nh3_weakened_sink_2026-10-13/verify_design.py)
  y [resultado](evidence/nh3_weakened_sink_2026-10-13/design_verification.json).
- [BC actuales y definición A0-A3](../Photochemical_Modeling/README.md).
- [Lectura de fuentes originales](nh3_deposition_velocity_provenance_and_physical_scenarios_2026-10-13.md)
  y [auditoría Huang/VULCAN](nh3_surface_sinks_huang_vulcan_review_2026-10-13.md).
