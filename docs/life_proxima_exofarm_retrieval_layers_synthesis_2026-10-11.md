# ¿Puede LIFE distinguir la perturbación ExoFarm? Síntesis de las capas de retrieval y evidencia

Fecha: 2026-10-11. Alcance: análogo terrestre controlado bajo Proxima,
LIFEsim clásico, serie oficial A1/A3 × {1, 10, 100 h}, 36 ablaciones
moleculares y tres restricciones a A0 efectiva en A3–100 h.

## 1. Respuesta científica y cierre

**Resultado directo:** en el dataset sintético A3–100 h, el modelo completo
con N₂O libre se prefiere fuertemente al modelo que mantiene N₂O en la
referencia preagrícola escalar: **ln B = 29.440 ± 0.340**, con **7.96σ
calibrados** mediante la convención histórica adoptada. La posterior del
completo coloca el N₂O por encima de esa referencia y estima un factor
mediano **5.45**, con intervalo creíble central del 95 % **[4.15, 6.97]**.

**Interpretación del proyecto:** estas simulaciones apoyan la
distinguibilidad del enriquecimiento de N₂O asociado al escenario extremo
ExoFarm A3 frente al valor A0 elegido. La inferencia está condicionada al
modelo atmosférico, los priors, la escena instrumental y esta realización de
ruido. NH₃ ofrece apoyo débil por sí sola. La comparación conjunta también
favorece el modelo libre; su resultado corresponde a la restricción conjunta.

La identificación causal de agricultura exige comparar explicaciones del
enriquecimiento que aquí no se modelaron. Tampoco se ha contrastado una
familia física completa de atmósferas A0 con una familia completa A3. El
experimento actual compara abundancias constantes libres con valores A0
constantes fijados, manteniendo los demás parámetros recuperables.

**Cierre autorizado:** los tres productos A0 quedan aceptados con la
salvedad de momentos derivados de coordenadas fijas; las evidencias y
productos primarios pasan la auditoría independiente. Se preservan los NaN
originales, las tablas provisionales y el diagnóstico anterior. La tabla
final conserva exactamente los mismos ln B y sigmas. La aceptación técnica
permite usar los resultados con sus limitaciones científicas; no certifica
que el modelo describa perfectamente los datos.

## 2. Por qué se construyeron varias capas

El análisis empezó con una señal espectral prevista y terminó con hipótesis
comparables sobre el mismo dato. Cada paso responde a una pregunta distinta:

| Capa | Pregunta | Producto y alcance de la respuesta |
| --- | --- | --- |
| Fotoquímica y emisión | ¿Qué cambia al perturbar los flujos nitrogenados? | Perfiles verticales VULCAN y espectros POSEIDON de A0–A3 |
| S/N de plantilla | ¿Es grande la diferencia espectral frente al ruido esperado? | Norma ponderada de una plantilla; diagnóstico previo al ajuste |
| Retrieval completo | ¿Qué atmósferas parametrizadas explican el espectro? | Posterior de abundancias/radio/P–T y evidencia Z |
| Distancia posterior a A0 | ¿Hacia dónde y cuánto se desplaza la abundancia? | Intervalos de enriquecimiento y masa posterior sobre A0 |
| LOO molecular | ¿Los datos favorecen incluir la molécula? | ln B del completo frente al modelo sin esa especie |
| A0 fija | ¿Los datos favorecen liberar la abundancia frente al valor preagrícola? | ln B libre/A0 fija, conservando la opacidad molecular |
| Auditoría e interpretación | ¿Son utilizables los productos y qué afirmación sostienen? | Validación, salvedades, límites y trazabilidad |

La distancia posterior a A0 es una distancia en el espacio de abundancias.
Estos resultados no establecen un alcance máximo en parsecs. La distancia
física adoptada para la escena es 1.30 pc.

## 3. Escenarios, procedencia y objeto simulado

La ecuación vigente del diseño es

\[
F_i(A_j)=F_i(A0)+\alpha_{i,j}\,\Delta F_{i,\mathrm{agri}},
\qquad i\in\{\mathrm{N_2O},\mathrm{NH_3}\}.
\]

Los F son flujos de frontera inferior en moléculas cm⁻² s⁻¹. VULCAN calcula
las abundancias y los perfiles resultantes. A0 representa el fondo natural
preagrícola; A1 el benchmark terrestre actual; A2 una perturbación moderada
inspirada en ExoFarm 30B; A3 la envolvente extrema asociada al marco
tecnosférico S2 Wild West. La traducción de esas anclas a flujos es una
decisión del proyecto, documentada en la
[metodología fotoquímica](photochemical_profiles_methodology.md). El índice
15× se refiere al incremento agrícola del diseño; la antigua matriz
10×/100× del flujo total se conserva como sensibilidad legacy.

La procedencia ejecutada es MUSCLES Proxima → conversión del flujo estelar
→ VULCAN A0–A3 → perfiles PT/química → emisión térmica POSEIDON →
LIFEsim clásico → datasets de flujo planetario → retrievals. La SED
MUSCLES alimenta la fotoquímica; la rejilla PHOENIX cumple la función estelar
del forward espectral. Son entradas con funciones diferentes. La rama
Proxima usa la corrección vigente de N₂O y una estructura PT/Kzz terrestre
de control, sin importar el benchmark Tierra–Sol anterior a la corrección
como si fuera la misma matriz.

El objeto es un análogo terrestre bajo el entorno radiativo de Proxima;
se adoptan d=1.30 pc, Rₚ=1.23 R⊕, Mₚ=1.59 M⊕, T⋆=3050 K,
R⋆=0.14 R☉ y a=0.0485 AU. La atmósfera de Proxima b no ha sido medida
por este trabajo. Los perfiles y los parámetros adoptados se describen en
la [metodología focal](life_proxima_a1_a3_1_10_100h_methodology_2026-10-03.md).
Los flujos agrícolas LPJmL aguas arriba no son abundancias atmosféricas y
su estado de calibración debe conservarse al discutir una conexión agrícola
cuantitativa; esta campaña espectral usa los forzamientos congelados de su
matriz fotoquímica.

## 4. De la emisión a los espectros «observados»

La magnitud utilizada es el flujo planetario directo recibido Fp(λ), en
W m⁻² m⁻¹. Los productos de transmisión/JWST y la profundidad de tránsito
pertenecen a otra rama. El forward de emisión conserva siete especies con
opacidad (H₂O, CO₂, CH₄, O₂, O₃, N₂O, NH₃) y N₂ de fondo, con superficie
negra opaca explícita a 1 bar.

La escena LIFEsim clásica usa cuatro colectores de 2 m, throughput nominal
5 %, banda 4–18.5 μm, resolución instrumental R=20, 31 canales y
exozodi de 3 zodis. Modela el ruido fotónico de fuga estelar, zodi local y
exozodi. La interfaz convierte energía a fotones mediante

\[
F_{\mathrm{ph}}=F_p\frac{\lambda}{hc},\qquad
\sigma_{F_p}=\sigma_{\mathrm{ph}}\frac{hc}{\lambda},
\]

con λ en metros en la conversión. El dataset que recibe POSEIDON contiene
centro y semiancho en μm, Fp y σFp en unidades energéticas. La escala
fotónica de exposición sigue σ(t)=σ(10 h)√(10 h/t).

Los seis datasets focales tienen realizaciones independientes entre
escenarios/duraciones. **Dentro de cada pareja de modelos se usa el mismo
archivo de observación, los mismos errores y los mismos bytes.** Por ello,
el completo A3–100 h, sus seis LOO y sus tres restricciones A0 usan el
mismo espectro observado. Los flujos y errores no se vuelven a sortear al
retirar o fijar una molécula. A1–1 h usa la realización NoiseRepeat2
promovida post hoc, decisión preservada y relevante para evaluar sesgo de
selección o cobertura.

El dataset A3–100 h es
[LIFE_proxima_A3_100h.dat](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A3_100h.dat),
seed 129315834, SHA-256
`78662546181a5b74391a14b7b73ae80d879200a74db6a4bc5338e3ce7eee4705`.
La implementación instrumental temporal/correlacionada de LIFEsimMC/PHRINGE
sigue pendiente; la rama clásica cerrada no incorpora esa validación.

## 5. Retrieval completo: qué se deja inferir

El [runner de emisión](../Thermal_Emission_Spectroscopy/scripts/run_life_retrieval.py)
usa POSEIDON 1.4.0 y MultiNest 3.10. El espectro se calcula a R=10000
entre 3.8 y 19 μm y se integra sobre los canales instrumentales. Esa
resolución numérica difiere del R=20 de la observación. Se usan 100 capas,
N_live=800 y tolerancia de evidencia 0.5; sin inflación de errores ni
parámetro x_tol.

La familia de retrieval tiene química isochem: una VMR constante por
molécula. El perfil térmico Madhu tiene seis coordenadas; se recupera
también el radio de referencia. Hay 15 coordenadas declaradas: radio,
seis térmicas, siete abundancias y presión superficial. Esta última está
fija en log₁₀(P/bar)=0: el completo tiene **14 coordenadas efectivamente
libres**. O₂ permanece incluido; la etiqueta de modelo `O2_fixedBlack1bar`
no debe interpretarse como que todas sus coordenadas químicas estén fijas.

Los priors de log₁₀(VMR) de seis gases son uniformes [-12,−1]; para O₂ son
[-6,log₁₀(0.5)]. Radio: [0.984,1.599] R⊕; T_ref: [150,400] K;
a₁/a₂: [0.02,2]; log P₁/P₂: [-6,1]; log P₃: [-2,1]. La superficie tiene
prior de anchura cero. Los parámetros auxiliares siguen marginalizados en
los contrastes; los modelos restringidos no congelan el mejor ajuste del
completo. Los contratos exactos están en
[resolved](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a0_fixed_reference_20261010/resolved/).

Para ruido diagonal gaussiano,

\[
\ln\mathcal L(D|\theta,M)=-\frac12\sum_k
\left[\frac{(F_{p,k}^{\rm obs}-F_{p,k}^{M}(\theta))^2}{\sigma_k^2}
+\ln(2\pi\sigma_k^2)\right],\quad
Z_M=\int\mathcal L(D|\theta,M)\,\pi(\theta|M)\,d\theta.
\]

La posterior p(θ|D,M)=Lπ/Z responde por los parámetros dentro del modelo.
Z integra sobre los priors y permite comparar los modelos planteados.
Una ln Z positiva es admisible para una densidad de datos continua y no
constituye una probabilidad mayor que uno. Su valor absoluto no ordena
datasets diferentes como factores de Bayes.

## 6. Inventario cerrado: qué se ejecutó y qué se preserva

| Bloque | Casos | Estado |
| --- | ---: | --- |
| Completos oficiales A1/A3 × 1/10/100 h | 6 | Validados y reutilizados |
| LOO: seis especies para cada completo | 36 | Cerrados y auditados, exit 0 |
| A0 fija: N₂O / NH₃ / ambas, solo A3–100 h | 3 | Exit 0, aceptados con salvedad acotada |
| Total del argumento focal actual | 45 | Productos disponibles; sin nuevas corridas en este cierre |
| Matriz amplia A0–A3 × 10/240 h | 8 | Archivo legacy 8/8 preservado, fuera del total focal |

El plan inicial A0 contenía 18 candidatas. El usuario autorizó únicamente
las tres A3–100 h individuales/conjunta; las otras quince quedaron sin
ejecutar. [selected_scope](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a0_fixed_reference_20261010/selected_scope.json),
[estado](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a0_fixed_reference_20261010/campaign_state.json)
y [manifest](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a0_fixed_reference_20261010/manifest.csv)
registran el alcance real.

## 7. Capa LOO: evidencia de presencia molecular

Se ejecutó de nuevo el ajuste completo retirando cada una de seis especies
(H₂O, CO₂, CH₄, O₃, N₂O, NH₃). Cada variante conserva 14 coordenadas
declaradas y 13 libres, la superficie fija, el dataset y los demás priors.
O₂ permanece como parte del modelo. La diferencia
ln B_X=ln Z_completo(D)−ln Z_sinX(D) prueba la necesidad de esa especie
dentro de esta familia de modelos.

| Escenario | Horas | ln B presencia N₂O ± num. | σ cal. N₂O | ln B presencia NH₃ ± num. | σ cal. NH₃ |
| --- | ---: | ---: | ---: | ---: | ---: |
| A1 | 1 | −1.797 ± 0.240 | N/A | −1.380 ± 0.242 | N/A |
| A1 | 10 | +0.447 ± 0.296 | 1.63 | −0.501 ± 0.294 | N/A |
| A1 | 100 | +1.608 ± 0.340 | 2.36 | −1.526 ± 0.341 | N/A |
| A3 | 1 | +0.047 ± 0.234 | 1.12 | −0.629 ± 0.231 | N/A |
| A3 | 10 | +7.388 ± 0.291 | 4.25 | −0.734 ± 0.292 | N/A |
| A3 | 100 | +65.550 ± 0.341 | 11.67 | +1.506 ± 0.342 | 2.31 |

Fuente: [CSV final LOO de 36 filas](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_loo_lnB_sigma_lin_2026-10-10.csv)
y [informe de campaña](life_proxima_molecular_ablation_loo_2026-10-04.md).
La tabla selecciona únicamente los gases agrícolas de interés; los otros
cuatro permanecen en la tabla completa. N/A significa que ln B≤0 y el
modelo completo no está favorecido en esa comparación. Una calibración
positiva pequeña, como 1.12σ, tampoco establece detección.

La señal N₂O de A3 crece claramente en estas realizaciones de 10/100 h;
NH₃ sigue ofreciendo apoyo limitado. El resultado A1–100 h es débil para
N₂O y desfavorable para incluir NH₃. Estas cifras no demuestran un
enriquecimiento A1/A0.

## 8. Capa posterior: dirección y magnitud del enriquecimiento

Se congela una referencia escalar a partir del perfil VULCAN A0:

\[
X_{i,0}^{\rm eff}=\frac{\int_{P_{\rm top}}^{P_{\rm bottom}}X_{i,A0}(P)\,dP}
{P_{\rm bottom}-P_{\rm top}},\qquad x_{i,0}=\log_{10}X_{i,0}^{\rm eff}.
\]

Se usa el promedio ponderado por presión del atlas, entre 5×10⁻⁸ y 1 bar:
N₂O=1.305192923200922×10⁻⁷ (x₀=−6.884325289636784) y
NH₃=1.1206595703796514×10⁻¹⁰ (x₀=−9.950526295665036).
Es una referencia efectiva elegida para comparar con una VMR constante;
no representa automáticamente el perfil radiativamente equivalente a A0.
El [JSON congelado](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a0_fixed_reference_20261010/a0_reference.json)
guarda el método y los hashes del perfil.

Para cada muestra de la posterior completa se calcula Δᵢ=xᵢ−xᵢ,₀ y
rᵢ=10^Δᵢ. Los cuantiles de r describen cuánto enriquecimiento se recupera;
P(Xᵢ>Xᵢ,₀|D,M_libre) describe su dirección. La probabilidad conjunta se
calcula en las mismas filas, preservando las dependencias entre moléculas.

En A3–100 h, N₂O da factor mediano 5.45 e intervalo 95 % [4.15,6.97].
Las 7479 muestras están sobre A0; el conteo 0/7479 bajo A0 expresa una
resolución empírica finita, sin justificar certeza exacta o sigma infinito.
NH₃ da factor mediano 49.29 pero intervalo 95 % [0.119,105.42], que cruza
A0. Su masa sobre A0 es 94.866 %; el prior nominal log-uniforme ya asigna
81.368 % sobre ese umbral. La lectura conjunta sobre ambas referencias es
94.866 %, calculada por filas, no como producto de dos probabilidades.

Se guardaron [12 resúmenes marginales](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a0_enrichment_posterior_2026-10-10.csv)
y [seis conjuntos](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a0_enrichment_joint_2026-10-10.csv).
En A3–10 h hay 3/6972 muestras N₂O bajo A0 (99.957 % sobre ella);
esa dirección está disponible sin ejecutar nuevas restricciones a 10 h.

El atlas también muestra z_descriptivo=(q50−x₀)/[(q84−q16)/2]. En
A3–100 h vale 13.24 para N₂O y 5.63 para NH₃. Resume la escala central
de una posterior posiblemente asimétrica/multimodal; el caso NH₃ muestra
por qué ese cociente debe acompañarse de intervalos y colas. Se conserva
como diagnóstico del atlas y no se usa como sigma de evidencia.

## 9. Capa A0 fija: comparación de modelos de enriquecimiento

Se definieron tres restricciones al completo A3–100 h: N₂O fija en A0 con
NH₃ libre; NH₃ fija con N₂O libre; ambas fijas. La molécula sigue presente
con opacidad y abundancia no nula. Los priors de las coordenadas fijadas
tienen anchura cero; los demás priors y el dataset son idénticos. Las
dimensiones libres son 13/13/12, manteniendo las 15 coordenadas declaradas.
La evidencia restringida integra los parámetros auxiliares restantes, con
la normalización de la referencia puntual, sin penalizar arbitrariamente
la coordenada fija por una anchura de prior inventada.

\[
B=\frac{Z_{\rm libre}(D)}{Z_{\rm A0\ fija}(D)},\qquad
\ln B=\ln Z_{\rm libre}-\ln Z_{\rm A0\ fija},\qquad
\delta_{\rm num}(\ln B)=\sqrt{\delta_{\rm libre}^2+\delta_{\rm fija}^2}.
\]

La cuadratura usa la hipótesis de errores numéricos independientes entre
ejecuciones. Las tres filas comparten la evidencia del completo; sus errores
están correlacionados por ese término común. La incertidumbre numérica
reportada no incluye sensibilidad a priors, ruido o discrepancia física.

| Hipótesis restringida frente al completo libre | ln B ± error numérico | σ calibrado bilateral | Diagnóstico condicionado |
| --- | ---: | ---: | --- |
| N₂O=A0; NH₃ libre | +29.440 ± 0.340 | 7.96 | Preferencia fuerte por liberar N₂O |
| NH₃=A0; N₂O libre | +1.170 ± 0.342 | 2.12 | Preferencia débil por liberar NH₃ |
| N₂O=A0 y NH₃=A0 | +31.103 ± 0.336 | 8.17 | Restricción conjunta fuertemente desfavorecida |

Fuente: [CSV final de tres filas](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a0_lnB_sigma_lin_2026-10-11.csv)
y [JSON aceptado](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a0_lnB_sigma_lin_2026-10-11.json).
Las ln Z precisas del completo/N₂O fija/NH₃ fija/ambas son
884.3333041378268 / 854.8931804139012 / 883.1629039835424 /
853.2306013393314, cotejadas entre stats, summary y resultados impresos.

La preferencia libre/A0 por sí sola admite desplazamiento a cualquiera de
los dos lados. La posterior del completo aporta la dirección hacia valores
superiores. La coincidencia de ambas capas sostiene la interpretación de
enriquecimiento N₂O. El sigma conjunto pertenece a una hipótesis con dos
restricciones y no se asigna a cada gas, ni se suma con los sigmas
individuales. La semejanza entre ln B conjunta y N₂O indica que esta última
lleva la mayor parte del contraste; no descompone formalmente contribuciones
independientes.

## 10. Por qué se reportan ln B y sigma calibrado

Lin et al. (2021, §5.2) ajustaron modelos completos y modelos sin moléculas
para comparar sus evidencias. Benneke & Seager (2013, ecuaciones 8–9 y
tabla 2) ofrecen la calibración histórica citada para expresar esas
comparaciones en una escala gaussiana. La política del proyecto conserva
**ln B ± error numérico como resultado principal** y sigma como referencia
auxiliar solicitada por el usuario.

El [calculador congelado](../Thermal_Emission_Spectroscopy/scripts/report_proxima_loo_lin_sigma.py)
resuelve en logaritmos, para ln B>0,

\[
y-\ln y=1+\ln B,\quad y>1,\quad p_{\rm cal}=e^{-y},\quad
p_{\rm cal}=\operatorname{erfc}(\sigma_{\rm cal}/\sqrt2).
\]

Se trata de la igualdad adoptada para calibrar una cota, con convención
bilateral. Para ln B≤0 se reporta N/A. La prueba reproduce a la precisión
publicada los controles B=2.9,12,21,150,43000. La crítica de Kipping &
Benneke (2025) subraya que una conversión de una cota no proporciona una
significancia frecuentista medida. Por ello usamos la etiqueta **sigma
calibrado**, sin interpretar 7.96σ como una tasa de falsos positivos
comprobada de agricultura. Los límites de prior también afectan B.

En particular, N₂O A3–100 h tiene tres números diferentes: z descriptivo
13.24; sigma de presencia LOO 11.67; sigma libre/A0 fija 7.96. Las
preguntas y denominadores son distintos y deben nombrarse junto a cada
número. El factor de Bayes es la división Z₁/Z₀; ln B es su logaritmo.
Ni B=3 ni ln B=3 describen el mismo umbral. Se evita un corte universal
«concluyente» sin explicitar la escala y el contexto.

## 11. Aceptación con salvedad: qué significan los NaN

El muestreo terminó con exit 0 en las tres corridas; la última a las
16:35:01 UTC (11:35:01 COT) del 2026-10-11. Exit 0 fue seguido por la
auditoría independiente del completo y los tres archivos. Se verificaron
posteriores contra MultiNest, espectros, P–T, log-X, contadores, priors,
valores fijos en todas las muestras físicas, dataset y hashes.

La finitud estricta encontró ocho NaN en cuatro archivos stats/summary,
exclusivamente en desviaciones resumidas de log_N2O/log_NH3 fijos. Se
conserva `strict_finiteness_pass=false`. Las evidencias, medias, ML/MAP,
espectros y muestras científicas son finitos; los parámetros fijos tienen
mínimo=máximo=valor de referencia. Un parámetro fijo posee varianza cero
por definición. La cancelación numérica al resumir esa varianza es una
explicación compatible con el patrón, pendiente de confirmar en la
implementación original.

El usuario autorizó aceptar esta incidencia acotada. El auditor compara
los hashes y los valores de evidencia con la auditoría previa y rechaza
cambios en los archivos revisados, nuevas incidencias o dispersión fija
distinta de cero. Se generó un resumen auxiliar con media constante y
desviación cero mediante segundo momento centrado y sumas estables, tanto
para muestras ponderadas como de igual peso. Son siete filas: las
coordenadas moleculares fijadas y la superficie en las tres corridas.

- [Decisión explícita y hashes](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a0_fixed_reference_20261010/acceptance_decision_20261011.json).
- [Auditoría anterior conservada](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a0_fixed_reference_20261010/validation_report_20261011_pre_acceptance.json).
- [Auditoría aceptada con salvedad](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a0_fixed_reference_20261010/validation_report_20261011.json).
- [Momentos auxiliares CSV](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a0_fixed_reference_20261010/fixed_parameter_moments_stable_20261011.csv) y [JSON](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a0_fixed_reference_20261010/fixed_parameter_moments_stable_20261011.json).
- [Informe de auditoría detallado](life_proxima_a3_100h_a0_fixed_audit_2026-10-11.md).

La campaña queda `VALIDATED_COMPLETE_WITH_SALVEDAD`; NH₃ individual pasa
sin NaN y las otras dos se aceptan con salvedad. Se comprobaron 52 hashes
de productos científicos sin cambios y 13 controles unitarios PASS.
Las tablas provisional/final coinciden exactamente en las tres filas.
No se relanzaron retrievals, cambiaron ranks, sustituyeron originales ni
alteraron los seis completos, los 36 LOO o la matriz 8/8.
Tras verificar tablas y 69 enlaces locales del conjunto metodológico,
el monitor `seguimiento-life-a0-a3-100h-3` fue eliminado; la aplicación
confirmó `deleteStatus=deleted`. La comprobación Ubuntu de cierre no
encontró supervisor/MPI/retrievals de esta campaña activos. Todo queda en el
[registro de cierre](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a0_fixed_reference_20261010/closure_record_20261011.json).
La revisión documental final comprobó 72 enlaces locales sin faltantes.
La prueba negativa de `--accept` sin salvedad rechazó la finitud estricta
y dejó idénticos el ledger aceptado, su auditoría y la decisión de aceptación.

## 12. Qué permite decir «LIFE distingue ExoFarm»

La afirmación defendible es: **en este experimento sintético clásico de
Proxima, 100 h permiten distinguir un N₂O recuperado enriquecido respecto
a la referencia efectiva preagrícola fijada, para la perturbación extrema
A3**. La evidencia relativa y la dirección posterior coinciden. A3–10 h
ya favorece presencia molecular y muestra desplazamiento sobre A0, pero
carece aquí de una comparación A0 fija ejecutada. A1 no ofrece una
demostración equivalente, y NH₃ no proporciona una confirmación independiente
fuerte de enriquecimiento.

El resultado aún no acredita una separación robusta de poblaciones de
mundos agrícolas/naturales. Faltan contrastes contra explicaciones naturales
alternativas y una referencia A0 incierta/físicamente completa. La
realización de ruido, priors, perfil vertical y parametrización P–T deben
examinarse antes de extrapolar esta predicción a rendimiento de misión o
a una atmósfera real.

Existe además desajuste absoluto: el completo A3–100 h tiene χ² impreso
79.01; POSEIDON lo resume como χ²_red=4.94 con 16 grados de libertad
declarados. Descontando la superficie fija, el diagnóstico nominal usa
31−14=17 y da ≈4.65. N₂O fija/NH₃ fija/conjunta dan ≈8.11/4.86/8.09
con 18/18/19 grados nominales, desde χ² redondeado. Estos grados son un
diagnóstico de complejidad; restricciones/prior y no linealidad limitan su
interpretación exacta como distribución χ². La gran preferencia relativa
por el completo convive con un ajuste absoluto tensionado. La discrepancia
vertical isochem/VULCAN es una limitación conocida; este cierre no atribuye
todo el residuo a una causa única verificada.

Quedan como trabajo científico **propuesto**, sujeto a autorización:
realizaciones repetidas y calibración de falsas preferencias; sensibilidad
a priors y a la referencia A0; química vertical y estructura térmica;
ruido/covarianza LIFEsimMC/PHRINGE; y modelos físicos alternativos de
origen natural. Ninguna de esas campañas se lanzó durante el cierre.
La documentación, validación y las 45 corridas focales sí están cerradas.

## 13. Productos visuales y reproducción

[Atlas oficial PNG](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima.png),
[PDF](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima.pdf)
y [SVG](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima.svg)
muestran posteriores, perfiles VULCAN y P–T de los seis completos.
[Emisión y residuales moleculares](../Thermal_Emission_Spectroscopy/final_products/figures/emission_molecular_residuals_proxima.png)
y [S/N integrado](../Thermal_Emission_Spectroscopy/final_products/figures/life_classic_snr_integrated_proxima.png)
son la capa predictiva; la
[figura LOO](../Thermal_Emission_Spectroscopy/final_products/figures/life_proxima_molecular_ablation_loo_lnB_2026-10-10.svg)
corresponde a la comparación de modelos. Se enlazan productos existentes,
sin hacer pasar una figura S/N por una evidencia Bayesiana.

Desde la raíz, la auditoría de aceptación y los controles son reproducibles
sin importar POSEIDON ni ejecutar likelihoods:

```text
python Thermal_Emission_Spectroscopy/scripts/audit_proxima_a0_fixed_reference.py --accept --accept-fixed-moment-salvedad
python -m unittest discover -s Thermal_Emission_Spectroscopy/scripts -p test_a0_independent_audit.py
python -m unittest discover -s Thermal_Emission_Spectroscopy/scripts -p test_a0_reference_contract.py
```

El [auditor](../Thermal_Emission_Spectroscopy/scripts/audit_proxima_a0_fixed_reference.py)
vuelve a exigir los productos revisados por hash. El
[análisis posterior](../Thermal_Emission_Spectroscopy/scripts/analyse_proxima_a0_enrichment.py)
documenta los conteos/intervalos. El
[reporte LOO](../Thermal_Emission_Spectroscopy/scripts/report_proxima_loo_lin_sigma.py)
calcula la calibración. Los scripts de campaña/launch son procedencia de
ejecución, no instrucciones para repetir una campaña ya cerrada. Logs,
configuraciones, scratch y resultados originales se preservan.

## 14. Referencias y decisiones de uso

Las referencias justifican familias de métodos; los límites de prior, la
referencia escalar y la aplicación a esta escena son decisiones del proyecto.
La comparación molecular y las ecuaciones de calibración se cotejaron con
las fuentes primarias el 2026-10-11.

- Haqq-Misra et al. (2022), *Disruption of a Planetary Nitrogen Cycle as Evidence of Extraterrestrial Agriculture*, [doi:10.3847/2041-8213/ac65ff](https://doi.org/10.3847/2041-8213/ac65ff): motivación ExoFarm; no demuestra causalidad de nuestros espectros.
- Haqq-Misra et al. (2025), *Projections of Earth's technosphere: Scenario modeling, worldbuilding, and overview of remotely detectable technosignatures*, [doi:10.1016/j.techfore.2025.124194](https://doi.org/10.1016/j.techfore.2025.124194): ancla narrativa de tecnosferas/extremos, traducida a flujos por el proyecto.
- France et al. (2016), MUSCLES, [doi:10.3847/0004-637X/820/2/89](https://doi.org/10.3847/0004-637X/820/2/89); [MAST MUSCLES](https://archive.stsci.edu/hlsp/muscles): procedencia de la SED.
- Tsai et al. (2021), VULCAN, [doi:10.3847/PSJ/abd022](https://doi.org/10.3847/PSJ/abd022); MacDonald (2023), POSEIDON, [doi:10.21105/joss.04873](https://doi.org/10.21105/joss.04873): fotoquímica y transferencia/retrieval.
- Husser et al. (2013), PHOENIX, [doi:10.1051/0004-6361/201219058](https://doi.org/10.1051/0004-6361/201219058): biblioteca estelar del forward.
- Dannert et al. (2022), LIFE II, [doi:10.1051/0004-6361/202141958](https://doi.org/10.1051/0004-6361/202141958); Carrión-González et al. (2023), LIFE X, [doi:10.1051/0004-6361/202347027](https://doi.org/10.1051/0004-6361/202347027): rama clásica y escena de referencia.
- Madhusudhan & Seager (2009), [doi:10.1088/0004-637X/707/1/24](https://doi.org/10.1088/0004-637X/707/1/24): familia P–T; Feroz, Hobson & Bridges (2009), [doi:10.1111/j.1365-2966.2009.14548.x](https://doi.org/10.1111/j.1365-2966.2009.14548.x): MultiNest.
- Lin, MacDonald, Kaltenegger & Wilson (2021), [doi:10.1093/mnras/stab1486](https://doi.org/10.1093/mnras/stab1486), [arXiv:2105.09319](https://arxiv.org/abs/2105.09319), §5.2 y tabla 2: comparación completo/ablaciones; sus resultados de transmisión TRAPPIST-1e/JWST no se trasladan como predicciones LIFE.
- Benneke & Seager (2013), [doi:10.1088/0004-637X/778/2/153](https://doi.org/10.1088/0004-637X/778/2/153), [arXiv:1306.6325](https://arxiv.org/abs/1306.6325), ecuaciones 8–9/tabla 2: calibración bilateral histórica.
- Kipping & Benneke (2025), [arXiv:2506.05392](https://arxiv.org/abs/2506.05392): precaución sobre convertir cotas Bayesianas en sigmas; fundamenta mantener ln B como principal.

La decisión de reporte queda: ln B con error numérico, sigma calibrado
claramente etiquetado, dirección posterior y referencia exacta al interpretar
enriquecimiento, e hipótesis/limitaciones junto a cualquier afirmación sobre
distinguibilidad ExoFarm.
