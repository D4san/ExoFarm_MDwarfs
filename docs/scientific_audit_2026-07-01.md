# Auditoría Científica de Modelos: Etapas I y II (2026-07-01)

## Contexto y Alcance
Esta auditoría revisa la implementación técnica de las etapas de Modelado Fotoquímico (VULCAN) y Espectroscopia de Transmisión (POSEIDON) para el proyecto ExoFarm, contrastando el código real ejecutado contra la documentación, decisiones de diseño y ecuaciones físicas subyacentes.

---

## Hallazgos Críticos y Contradicciones

### 1. Inconsistencia Matemática en los Flujos de N₂O (Escenarios A2 y A3)
La documentación del proyecto establece que los flujos agrícolas en la superficie se escalan linealmente según la ecuación:
$$ F_i(A_j) = F_i(A_0) + \alpha_{i,j} \times \Delta F_{i,agri} $$
donde $\Delta F_{i,agri} = F_i(A_1) - F_i(A_0)$.

- **Datos extraídos:**
  - $F_{N_2O}(A_0)$ = $1.58 \times 10^9$ molec cm⁻² s⁻¹
  - $F_{N_2O}(A_1)$ = $2.30 \times 10^9$ molec cm⁻² s⁻¹
  - $\Delta F_{N_2O,agri}$ = $0.72 \times 10^9$ molec cm⁻² s⁻¹

- **Contradicción en A2 (Moderate ExoFarm):**
  - Valor nominal documentado: $\alpha_{N_2O} = 2.55$.
  - Flujo teórico calculado: $1.58 \times 10^9 + 2.55 \times (0.72 \times 10^9) = \mathbf{3.416 \times 10^9}$.
  - Flujo codificado en `bc_earth_exofarm_moderate_full.txt`: $\mathbf{3.35 \times 10^9}$.
  - El $\alpha$ implícito real que VULCAN está corriendo es **~2.46**.

- **Contradicción en A3 (Extreme ExoFarm):**
  - Valor nominal documentado: $\alpha_{N_2O} = 15$.
  - Flujo teórico calculado: $1.58 \times 10^9 + 15 \times (0.72 \times 10^9) = \mathbf{12.38 \times 10^9}$ ($1.238 \times 10^{10}$).
  - Flujo codificado en `bc_earth_exofarm_full.txt`: $\mathbf{1.20 \times 10^{10}}$.
  - El $\alpha$ implícito real que VULCAN está corriendo es **~14.47**.

*Impacto:* Los forzamientos químicos simulados no corresponden con precisión a los multiplicadores declarados. Los flujos de $NH_3$ sí cuadran (salvo mínimos redondeos).

### 2. Discrepancias Fundamentales en Parámetros del Sistema (Radio Planetario y Estelar)
Existe una desincronización entre los parámetros físicos con los que se genera el modelo químico en VULCAN y con los que se realiza el retrieval en POSEIDON, lo cual afectará la normalización del espectro de transmisión:

- **Radio Estelar ($R_S$):**
  - VULCAN (`input_earth_trappist_A0.yml`): `r_star = 0.1192` $R_\odot$
  - POSEIDON (`trappist1e_retrieval_common.py`): `R_S = 0.11697` $R_\odot$
- **Radio Planetario ($R_P$):**
  - VULCAN: `Rp = 5.867852e8` cm (aprox. **0.921** $R_\oplus$)
  - POSEIDON: `R_P = 0.917985` $R_\oplus$

*Impacto:* Como la profundidad de tránsito es proporcional a $(R_P/R_S)^2$, evaluar un modelo químico generado bajo una gravedad/radio planetario con un código espectral que asume otro tamaño estelar y planetario introducirá sesgos y distorsionará la "verdad" subyacente.

### 3. Fuerte "Model Mismatch" Asumido en Retrievals (Isotérmico vs. Lin PT)
En `trappist1e_retrieval_common.py` la campaña asume `PT_profile="isotherm"` y `X_profile="isochem"`. Sin embargo, desde el 2026-06-30, el tracker oficial indica que se promovió usar el modelo de temperatura de Lin et al. (`atm_Trappist1e_Lin_Kzz.txt`).

- **El problema:** Se justificó mantener esta asunción isotérmica e isoquímica para conservar la "uniformidad de la campaña de 42 corridas" (según tracker el 2026-06-29). Sin embargo, otra entrada del tracker estipula que **la campaña se va a re-definir y re-ejecutar** porque las 42 corridas son obsoletas.
- **Vacío argumentativo:** Si se va a re-ejecutar la campaña desde cero con los nuevos perfiles fotoquímicos corregidos (Lin PT), *carece de sentido científico arrastrar una asunción simplista (isotherm/isochem)* si la verdad computada tiene fuerte estructura vertical. Recuperar una abundancia constante frente a un perfil real variado (particularmente en $NH_3$ o $H_2O$) introducirá fuertes sesgos y degeneraciones no cuantificadas, falseando las conclusiones sobre detectabilidad.

### 4. Ángulo Cenital (sl_angle) vs Tidal Locking
TRAPPIST-1e está anclado por mareas (tidally locked). En los `.yml` de VULCAN se configura `sl_angle = 48.0` y `f_diurnal = 1.0`. Físicamente, `f_diurnal = 1.0` implica una distribución de flujo solar irreal para un modelo 1D promedio global o diurno. Aunque el tracker indica "Se decidió ignorar el frente abierto sobre el ángulo cenital", este vacío metodológico es una debilidad persistente que un árbitro experto observará inmediatamente, ya que afecta las tasas fotolíticas de manera directa.

---

## Decisiones Científicas Válidas y Bien Soportadas

- **Aceptación de Convergencia Parcial (`end_case = 3`):**
  El pipeline atrapa e inspecciona activamente el final de VULCAN (`vulcan_output_checks.py`). Aceptar los perfiles de TRAPPIST-1e aunque detengan su convergencia global por culpa de trazas de $C_2H_5$ a $\sim 0.019$ bar es un compromiso razonable y pragmáticamente correcto, siempre y cuando se transparente. El código efectivamente verifica esto antes de promover los archivos.
- **Transición a PT de Lin et al. y 100x $CO_2$:**
  La actualización documentada el 30 de junio está reflejada adecuadamente en los `.yml` del pipeline.

---

## Recomendaciones para Saneamiento
1. Actualizar los archivos `.txt` de Boundary Conditions para que $F_{N_2O}$ encaje milimétricamente con los valores $\alpha=2.55$ y $\alpha=15$.
2. Unificar los radios de planeta y estrella. Sugiero heredar en POSEIDON los valores `0.1192` $R_\odot$ y $R_P$ en cm exactos declarados en VULCAN para consistencia.
3. Actualizar el script de retrieval (`trappist1e_retrieval_common.py`) para **no** ser isotérmico si de todos modos se correrá una campaña completamente nueva. De mínima, se requiere explorar retrievals estructurados o documentar firmemente el sesgo esperado.
