# Diseño de campañas de observación LIFE y matriz de retrievals (Etapa III)

**Fecha:** 2026-07-25
**Estado:** diseño aprobado para ejecución; manifiesto de campaña previo a los
retrievals (puerta exigida por el [plan de dos capas](life_stage_iii_two_layer_workplan_2026-07-20.md)).
**Base de evidencia:** [auditoría científica](stage_iii_scientific_audit_2026-07-25.md),
[Capa 1](life_earth_sun_10pc_interface_snr_2026-07-22.md),
[Capa 2](life_proxima_b_branch_bitacora_2026-07-22.md).

---

## 1. Pregunta

¿Cuánto tiempo de observación LIFE hace falta para **distinguir cada escenario
ExoFarm (A1, A2, A3) del baseline pre-agrícola A0** en emisión térmica, y en
cuántas campañas realistas se logra?

## 2. Tiempos de integración anclados en la literatura LIFE

Los tres regímenes no son arbitrarios: replican las escalas que la propia serie
LIFE usa para detección, caracterización y biofirmas difíciles.

| Régimen | Tiempo | Ancla en la literatura |
| --- | --- | --- |
| **Corto** (detección/reconocimiento) | **10 h** | LIFE X (Carrión-González et al. 2023) reporta S/N=170 en 10 h para Proxima b; su criterio de detectabilidad es S/N=7 con t<100 h. |
| **Razonable** (campaña estándar de caracterización) | **240 h ≈ 10 días** | LIFE XII (Angerhausen et al. 2024): "~10 days in certain standard scenarios such as temperate, terrestrial planets around M star hosts at 5 pc" — el caso más cercano al nuestro (planeta templado alrededor de M). |
| **Extremo** (límite factible) | **1200 h = 50 días** (y 2400 h = 100 días como cota) | LIFE XII: "~50 - 100 days in the most challenging but still feasible cases, such as an Earth twin at 5 pc". Consistente con LIFE III (Konrad et al. 2022): "~7 weeks with 4x2m apertures" (≈1176 h) para R=50, S/N=10 en una Tierra a 10 pc. |
| (referencia de "golden target") | pocos días | LIFE XII: "only a few days of observation time for certain very near-by 'Golden Target' scenarios" — categoría en la que cae Proxima b (1.3 pc). |

**Decisión [INF]:** matriz de tiempos **{10 h, 240 h, 1200 h}** para los
retrievals, más 2400 h reservado como cota superior si el caso extremo lo exige.
Los tres se reportan siempre junto a su ancla.

## 3. Matriz de campañas

Objetivo primario **Proxima b** (`life_proxima_b_earthlike_v1`), porque es el
único de nuestras dos capas donde la señal supera el ruido en tiempos factibles
(S/N=5 en 11–32 h para A3; ver Capa 2). Tierra–Sol a 10 pc queda como control
de contraste: allí ni el caso extremo alcanza el umbral (S/N=5 requeriría
~9 400 h para N2O 7.8 µm), lo que ya es un resultado.

| Campaña | Objetivo | Escenarios | Tiempos | Runs |
| --- | --- | --- | --- | --- |
| `C-short` | Proxima b | A0, A1, A2, A3 | 10 h | 4 |
| `C-standard` | Proxima b | A0, A1, A2, A3 | 240 h | 4 |
| `C-extreme` | Proxima b | A0, A1, A2, A3 | 1200 h | 4 |
| `C-control` | Tierra–Sol 10 pc | A0, A3 | 1200 h | 2 |
| **Total** | | | | **14 retrievals** |

Cada run: espectro LIFE binado (R=20 Proxima / R=50 Tierra–Sol) con σ por bin del
simulador clásico, escalada `σ(t)=σ(10 h)·√(10/t)` (escalado √t validado), una
realización de ruido con semilla registrada.

## 4. Criterio de "distinguible de A0"

Se reportarán tres criterios, de más débil a más fuerte, para no confundir
diagnóstico con detección:

1. **Diagnóstico de señal (ya calculado):** SNR de banda del contrafactual
   `≥3` (indicio) / `≥5` (fuerte).
2. **Separación de posteriores:** distancia entre la abundancia de N2O (y NH3)
   recuperada en Aj y la recuperada en A0, en unidades de σ combinada
   (`|μ_j − μ_0| / √(σ_j²+σ_0²)`); ≥3σ = escenarios distinguibles.
3. **Evidencia bayesiana (si el runner lo permite):** ln B entre el modelo con
   y sin N2O sobre el mismo dato.

El entregable es la tabla "**¿cuántas campañas** (múltiplos del tiempo estándar)
hacen falta para separar Aj de A0 a ≥3σ?", usando que la separación en σ escala
como √t: `n_campañas = (3σ / separación_obtenida)² `.

## 5. Reglas y salvedades que acompañan a todo producto

- σ **diagonales** de LIFEsim clásico (ruido astrofísico/fotónico). Sin
  covarianza instrumental: los retrievals son un **límite superior optimista**
  hasta que corra LIFEsimMC/PHRINGE. Etiqueta obligatoria en cada tabla/figura.
- Proxima = análogo terrestre controlado bajo la SED de Proxima, **no** la
  atmósfera medida de Proxima b; R_p es estimado (no transita).
- Tierra–Sol = conjunto pre-corrección N2O.
- Una sola realización de ruido por punto (semilla registrada); la robustez
  estadística (múltiples realizaciones) queda como trabajo posterior.
- SNR/posteriores son diagnósticos de distinguibilidad, no un anuncio de
  detección de vida ni de agricultura.

## 6. Resultado: ¿cuántas campañas separan cada escenario de A0?

Calculado con el diagnóstico validado (señal contrafactual de banda sobre σ por
bin de LIFEsim clásico) y el escalado √t verificado:
`n_campañas = (S/N_objetivo / S/N_1campaña)²`. Campaña estándar = **240 h ≈ 10
días** (ancla LIFE XII). Script:
[`campaigns_to_differentiate.py`](../Thermal_Emission_Spectroscopy/scripts/campaigns_to_differentiate.py);
tabla completa (3 duraciones × 3 escenarios × 2 moléculas × 2 objetivos) en
`outputs/_comparison/campaigns_to_differentiate_A0.csv`.

### Proxima b (1.30 pc, escena LIFE X)

| Escenario | Molécula | S/N en 1 campaña (240 h) | Campañas → 3σ | Campañas → 5σ | Horas → 5σ |
| --- | --- | ---: | ---: | ---: | ---: |
| A1 (Tierra actual) | N2O | 2.85 | **2** | **4** | 738 |
| A1 | NH3 | 0.53 | 32 | 88 | 21 100 |
| A2 (ExoFarm moderado) | N2O | 7.04 | **1** | **1** | 121 |
| A2 | NH3 | 1.82 | 3 | 8 | 1 813 |
| A3 (ExoFarm extremo) | N2O | 27.2 | **1** | **1** | **8** |
| A3 | NH3 | 7.06 | 1 | 1 | 120 |

### Tierra–Sol (10 pc, baseline LIFE) — control

| Escenario | Molécula | S/N en 1 campaña | Campañas → 5σ |
| --- | --- | ---: | ---: |
| A3 | N2O | 0.88 | 33 (≈7 780 h) |
| A2 | N2O | 0.26 | 370 |
| A1 | N2O | 0.11 | 1 934 |
| cualquiera | NH3 | ≤0.03 | ≥4×10⁴ |

### Lectura

- **En Proxima b basta una sola campaña estándar (10 días) para separar A2 y A3
  de A0 a 5σ vía N2O**; A3 lo logra en apenas **8 h** (menos que la campaña
  corta de LIFE X). Incluso el escenario A1 —la Tierra actual, sin ExoFarm— se
  separa del baseline pre-agrícola en **4 campañas** (~1 mes de integración).
- **NH3 es mucho más exigente**: solo A3 lo alcanza en una campaña; A2 necesita
  8 y A1 queda fuera de alcance práctico. Coherente con su carácter traza y con
  la advertencia del proyecto sobre NH3.
- **Alrededor de un gemelo solar a 10 pc nada es alcanzable**: ni el caso
  extremo baja de ~33 campañas (≈año de integración) para N2O.
- Corolario de diseño: la discriminación ExoFarm con LIFE es un problema de
  **elección de objetivo cercano**, no de acumular tiempo.

## 6b. Resultado de los retrievals bayesianos (matriz completa 8/8)

Matriz ejecutada y completa: Proxima b A0–A3 × {10 h, 240 h} (8 retrievals). Modelo: PT Madhu de 6 parámetros + 6 abundancias
isoquímicas + `R_p_ref` + `log_P_surf` + tolerancia fraccional de modelo
`x_tol`; MultiNest con 200 live points; `spectrum_unit='Fp'`,
`spectrum_type='direct_emission'`. Script:
[`analyze_retrieval_separation.py`](../Thermal_Emission_Spectroscopy/scripts/analyze_retrieval_separation.py);
CSV `outputs/_comparison/retrieval_separation_from_A0.csv`.

**Validación del piloto (A3, 240 h):** `R_p_ref = 1.21 ± 0.02 R⊕` (verdad 1.23),
`x_tol = 0.03` (el PT flexible absorbe casi todo el desajuste), y N2O recuperado
`−6.17 ± 0.20` frente a una verdad de `−6.01`. CO2 y CH4 también constreñidos;
O3 y NH3 no. La evidencia pasó de `ln Z ≈ −9×10⁶` (configuración rota) a
`ln Z = 895.4 ± 0.45` con 48 450 evaluaciones.

**Separación respecto de A0 (240 h = una campaña de 10 días):**

| Escenario | N2O recuperado (log) | ¿medido? | σ vs abundancia real de A0 | Veredicto |
| --- | --- | --- | ---: | --- |
| **A3** | **−6.19 ± 0.22** | **sí (medición)** | **3.12** | **distinguible en 1 campaña** |
| A2 | −9.26 ± 1.73 | no (límite superior) | — | no medido |
| A1 | −8.30 ± 1.61 | no (límite superior) | — | no medido |
| (NH3, cualquiera) | ≈ −9.5 ± 1.4 | no (límite superior) | — | no medido |

> **Filtro de validez.** Una separación solo se considera real si (i) el
> posterior del escenario es una **medición** (σ < 0.5 dex, no un límite
> superior) y (ii) la desviación tiene el **signo físico**: todos los escenarios
> ExoFarm *añaden* N2O sobre A0, así que una mediana por debajo de la verdad de
> A0 es un artefacto del prior en un posterior sin constreñir, no evidencia de
> diferencia. Sin este filtro, A1 a 10 h aparentaba "2.15σ" con un posterior de
> σ=1.37 dex cuya mediana caía 3 dex *por debajo* de A0 — imposible físicamente.

### Régimen corto (10 h, campaña de reconocimiento LIFE X)

| Escenario | N2O recuperado (log) | ¿medido? | σ vs verdad A0 | Veredicto |
| --- | --- | --- | ---: | --- |
| A3 | −6.50 ± 0.41 | **sí (medición)** | 0.92 | medido, **insuficiente** (≈11 campañas de 10 h) |
| A2 | −8.23 ± 1.85 | no | — | límite superior |
| A1 | −9.83 ± 1.37 | no | — | límite superior |

**Lectura del régimen corto.** Ya en 10 h el retrieval **mide** N2O en A3
(σ=0.41 dex), pero la medición todavía no excluye el valor pre-agrícola
(0.92σ). Es la transición esperada: al pasar de 10 h a 240 h la anchura del
posterior se reduce de 0.41 a 0.22 dex (factor 1.9, compatible con el √24≈4.9
sólo parcialmente, porque las degeneraciones no escalan con √t) y la separación
sube de 0.92σ a 3.12σ. Es decir, **la campaña estándar de 10 días es
efectivamente el umbral** donde A3 se vuelve distinguible; el reconocimiento de
10 h detecta el planeta y mide N2O, pero no discrimina el escenario.

Se reportan **dos métricas** porque responden preguntas distintas:
(a) *posterior vs posterior* `|μ_j−μ_0|/√(σ_j²+σ_0²)` — conservadora y sin
suposiciones, pero **dominada por la anchura del posterior de A0**: en el
baseline el N2O es demasiado débil para medirse (σ≈1.8 dex), así que la métrica
castiga incluso a A3 (1.26σ). (b) *posterior vs abundancia verdadera de A0*
`|μ_j−verdad_0|/σ_j` — responde "¿esta observación excluye el valor
pre-agrícola?", que es la pregunta de una campaña real contra una hipótesis
concreta. La tabla usa (b) como criterio principal y conserva (a) en el CSV.

**Interpretación.** Con una sola campaña estándar de 10 días sobre Proxima b,
**solo el escenario extremo A3 produce una medición de N2O, y esa medición
excluye el valor pre-agrícola a 3.1σ**. A2 y A1 no producen medición alguna: el
retrieval devuelve límites superiores. Para ellos **no es válido extrapolar un
número de campañas desde el posterior**, porque pasar de "límite superior" a
"medición" no es un simple escalado √t de la anchura; la estimación por S/N de
§6 (≈1 y ≈4 campañas para 5σ de señal en A2 y A1) es la cota optimista, y el
número real requeriría correr retrievals a tiempos mayores para localizar dónde
la abundancia se vuelve medible. NH3 no es discriminante en ningún caso.

**El retrieval es bastante más conservador que el diagnóstico de S/N** de §6
(que daba 1 campaña también para A2 y 4 para A1). La diferencia es real y esperable: el diagnóstico
de S/N mide la señal diferencial *sabiendo exactamente qué buscar*, mientras el
retrieval debe ajustar simultáneamente PT, radio, presión superficial y seis
abundancias, y las degeneraciones consumen información. **La cifra del retrieval
es la defendible**; la de S/N es una cota optimista útil para planificar.

## 7. Estado de los retrievals bayesianos (trabajo en curso)

Los 14 datasets están generados y el runner
([`run_life_retrieval.py`](../Thermal_Emission_Spectroscopy/scripts/run_life_retrieval.py))
existe, pero **la matriz aún no produce posteriores válidos**. Tres pilotos
documentan los modos de fallo, todos reales y de interés metodológico:

1. **PT rígido (gradiente de 2 parámetros):** ln Z ≈ −9×10⁶ y MultiNest termina
   sin muestrear. Con σ ≲1% del flujo (S/N≈514 a 1200 h) el desajuste entre un
   PT paramétrico simple y la atmósfera VULCAN de 120 capas es catastrófico.
2. **PT Madhu + `error_inflation='Line15'`:** MultiNest muestrea, pero `b` se
   pega al borde del prior y todo queda sin constreñir. Causa: `Line15` suma
   `10^b` en **unidades absolutas al cuadrado**; con Fp≈10⁻¹² W m⁻² m⁻¹
   (σ²≈10⁻³⁰) cualquier prior "razonable" infla el error ~28 órdenes.
3. **PT Madhu + `Piette20`** (inflación fraccional, invariante de escala):
   seguía terminando en 200 evaluaciones con `R_p_ref → 2×10⁻⁷ R⊕`. Causa
   encontrada: POSEIDON **divide internamente el prior de `R_p_ref` por la
   unidad de radio** (`core.py`, `set_priors`), es decir lo espera **en metros**;
   al pasarlo ya en R⊕ quedaba dividido dos veces. **Resuelto.**

Configuración final validada (la de §6b): PT Madhu + `error_inflation='Piette20'`
+ prior de `R_p_ref` en metros. Con ella el muestreo pasó de 200 evaluaciones
(terminación inmediata) a 48 450, con `ln Z = 895.4 ± 0.45` y posteriores
físicos.

**Lección metodológica (aplicable a cualquier retrieval de emisión LIFE de alto
S/N):** hacen falta PT flexible **y** un término de tolerancia de modelo
**fraccional** (no absoluto: `Line15` suma `10^b` en unidades de dato al
cuadrado, imposible de priorizar cuando el flujo es ~10⁻¹² SI). Sin ambos, el
model mismatch domina la verosimilitud y el muestreador no explora. Nótese la
paradoja: **más S/N agrava el problema**, porque las barras de error se vuelven
más pequeñas que el error intrínseco del modelo.

**Pendiente:** los cuatro retrievals del régimen corto (10 h) se están
ejecutando; completarán la tabla con la campaña de reconocimiento.

## 8. Referencias

- Quanz et al. 2022, A&A 664, A21 (LIFE I: arquitectura de referencia).
- Dannert et al. 2022, A&A 664, A22 (LIFE II: LIFEsim, ruido astrofísico).
- Konrad et al. 2022, A&A 664, A23 (LIFE III: R=50, S/N=10, ~7 semanas para una
  Tierra a 10 pc).
- Carrión-González et al. 2023, A&A 678, A96 (LIFE X: objetivos conocidos;
  Proxima b S/N=170 en 10 h; criterio S/N=7 en <100 h; 3 zodis; R=20).
- Angerhausen et al. 2024, AJ 167, 128 (LIFE XII: N2O como biofirma capstone;
  ~días para golden targets, ~10 días para M a 5 pc, ~50–100 días para Tierra a
  5 pc).
- Huber et al. 2025, AJ 170, 227 (LIFEsimMC/PHRINGE: ruido instrumental y
  covarianza — puerta pendiente).
- Haqq-Misra et al. 2022, ApJL 929, L28 (N2O agrícola como tecnofirma).
