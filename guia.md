Vale, vamos a dejar esto como una “super-instrucción” para tu proyecto, con pasos concretos, valores razonables y referencias donde puedas ir a pescar datos más finos.

*(Y nota rápida: algunos PDFs que habíamos usado en otros chats ya “expiraron” en este hilo; si necesitas que vuelva a leer alguno, súbelo otra vez aquí.)*

---

## 0. Idea central del proyecto

**Meta:**
Comparar, de forma fotodinámica y autoconsistente (con VULCAN), los perfiles verticales de especies nitrogenadas (sobre todo N₂O y NH₃, pero también NOₓ, HNO₃, etc.) en una Tierra:

1. **Sin agricultura industrial** (“Tierra pre-agrícola / sólo flujos naturales”).
2. **Con agricultura moderna** (flujos actuales de fertilización, ganadería, etc.).
3. **Con agricultura “hiper-intensiva” tipo ExoFarm de Haqq-Misra** (flujos exagerados → tecnofirma). ([arXiv][1])

Y repetir estos escenarios para dos estrellas:

* **Sol** (G2V, caso análogo Tierra–Sol).
* **TRAPPIST-1** (M8, usando SED tipo Mega-MUSCLES / Peacock+). ([arXiv][2])

---

## 1. Paquete de referencias que vas a “copiar” o adaptar

1. **VULCAN** – modelo fotoquímico 1D de Tsai et al. (2021), con redes C–H–O–N–S y release NCHO (Earth-like oxidizing atmospheres). ([arXiv][3])

   * Repo GitHub:

     ```text
     https://github.com/exoclime/VULCAN
     ```

2. **“ExoFarm” de Haqq-Misra** – te da el marco conceptual de “agricultura como tecnofirma” mediante NH₃ + N₂O. Ellos usan un generador sintético de espectros y parametrizan abundancias de NH₃/N₂O para planetas con 30–100 mil millones de personas. ([arXiv][1])

   * Preprint:

     ```text
     https://arxiv.org/abs/2204.05360
     ```

3. **Schwieterman+ 2022 (N₂O biosignature)** – trabajo clave que ya hace lo que tú quieres pero a nivel de *N₂O general*, no específicamente agricultura: acoplan modelo biogeoquímico + fotquímico + espectral y barren flujos de N₂O de 0.01 a 100 Tmol/yr para Earth-like alrededor de estrellas FGKM (incluyendo TRAPPIST-1e). ([ResearchGate][4])

4. **Leung+ 2022 (metilhaluros en atmósferas tipo Hycean/Tierra)** – ya tienes el PDF y su uso de un código fotoquímico estilo Atmos; su lógica de “tasas de producción biológica → perfiles fotoquímicos → espectros” es exactamente el tipo de pipeline que quieres replicar pero para N₂O/NH₃ agrícolas. ([arXiv][5])

5. **Mega-MUSCLES TRAPPIST-1 SED (Wilson+ 2021)** – SED 5 Å–100 μm para TRAPPIST-1, combinando X, UV, óptico e IR, pensado precisamente para modelar atmósferas de sus planetas. ([arXiv][2])

   * Paper:

     ```text
     https://arxiv.org/abs/2102.11415
     ```
   * El SED/tablas están en los materiales asociados (via NASA/MAST u hojas suplementarias).

6. **Global Nitrous Oxide Budget 1980–2020 (Global Carbon Project, Tian+ 2024, etc.)** – de aquí sacas cuánto del N₂O global viene de agricultura hoy (~70–75% de las emisiones antropogénicas, y ~35–40% del total global). ([essd.copernicus.org][6])

7. **NH₃ y agricultura** – revisiones que muestran que ≳80% de las emisiones de NH₃ provienen de agricultura (fertilizantes sintéticos, estiércol, etc.). ([ResearchGate][7])

---

## 2. Archivos que tendrás que tocar/crear en VULCAN

(La estructura exacta depende un poco de la versión del repo, pero conceptualmente siempre tendrás algo así):

1. **Archivo de parámetros planetarios**
   Algo tipo `input_Terra_Sun.yml` / `input_Terra_Trappist.yml`, donde defines:

   * Gravedad, radio, presión superficial.
   * Perfil T–z.
   * Composición de fondo (N₂, O₂, CO₂, H₂O, etc.).
   * Mezcla inicial de trazas (N₂O, NH₃, NOx…) como seed.
   * Coeficiente de difusión vertical Kzz(z).

2. **Archivo de espectro estelar / radiación**

   * Un archivo de tabla UV–visible–IR para el **Sol** (puedes usar un estándar tipo Thuillier 2004 o lo que ya trae VULCAN). ([ResearchGate][4])
   * Un archivo similar para **TRAPPIST-1**, re-muestreando el SED de Mega-MUSCLES o algún modelo basado en Peacock+ 2018. ([arXiv][2])

3. **Archivo de red química**

   * Usar la red C–H–O–N–S oxidante que VULCAN ofrece para atmósferas tipo Tierra (NCHO release). ([GitHub][8])
   * Verificar que incluya explícitamente:
     `N2, NH3, N2O, NO, NO2, HNO3, HNO2, HONO, HNO, HCN` y las reacciones clave con OH, O(¹D), O₃, fotólisis, etc.
   * Si falta algo para N₂O/NH₃, añadir reacciones copiadas de Schwieterman 2022 / ATMOS / Leung 2022.

4. **Archivo de condiciones de frontera (`boundary_conditions`)**

   * Ahí pondrás tus **flujos superficiales** (en molec cm⁻² s⁻¹) para N₂O, NH₃, (posiblemente NO, HCN…) representando:

     * Sólo naturaleza.
     * Naturaleza + agricultura actual.
     * Agricultura hiper-intensiva (tipo ExoFarm).

5. **Archivo de deposición seca/húmeda**

   * VULCAN permite parametrizar velocidades de deposición o “sink” en superficie. Ajustar para NH₃, NOx, HNO₃ y N₂O según literatura (o copiar valores de Earth-case de Tsai / Schwieterman si los localizas).

---

## 3. Cómo parametrizar la “agricultura” en VULCAN

La agricultura industrial entra **como modificación de los flujos superficiales** de especies nitrogenadas y quizá de las velocidades de deposición (porque cambias uso del suelo, suelos anóxicos, etc.).

### 3.1. Punto de partida: flujos globales actuales

De los presupuestos globales:

* Total de emisiones de N₂O ≈ 12–13 Tg N₂O-N / año.
* ~36–40% antropogénicas, el resto naturales. ([Global Carbon Atlas][9])
* Dentro de lo antropogénico, la **agricultura** ≈ 70–75%. ([csiro.au][10])

Schwieterman+ (2022) traducen esto a un flujo superficial global de orden:
**Φ₀(N₂O) ≈ 0.4 Tmol/yr ≈ 1.5×10⁹ molec cm⁻² s⁻¹ para la Tierra moderna.** ([ResearchGate][4])

Para NH₃, compilaciones recientes indican que **>80%** de las emisiones globales provienen de agricultura moderna. ([ResearchGate][7])

> **Moral:**
>
> * “Tierra pre-agrícola” ≈ sólo el componente natural → ~60–65% del flujo actual de N₂O, y quizá ~10–20% del flujo actual de NH₃.
> * “Tierra actual” = flujo total presente.
> * “Super-ExoFarm” = factores ×10–×100 sobre Φ₀, en línea con los escenarios extremos que exploran Haqq-Misra (más gente, más fertilizante) y Schwieterman (hasta 100 Tmol/yr). ([arXiv][1])

### 3.2. Convertir a unidades de VULCAN

Supón que VULCAN pide flujos en `molec cm^-2 s^-1`:

1. El valor de Schwieterman ya está en esas unidades para Tierra moderna:

   * `Φ_earth_modern(N2O) ≈ 1.5e9 molec cm^-2 s^-1`. ([ResearchGate][4])

2. Escenarios propuestos (ejemplo para N₂O):

   * **Pre-agrícola:**
     `Φ_pre ≈ 0.6 × Φ_earth_modern ≈ 9×10^8 molec cm^-2 s^-1`
   * **Tierra actual:**
     `Φ_now = Φ_earth_modern ≈ 1.5×10^9`
   * **ExoFarm “moderado”:**
     `Φ_exofarm_10 ≈ 10 × Φ_earth_modern ≈ 1.5×10^10`
   * **ExoFarm “extremo”:**
     `Φ_exofarm_100 ≈ 100 × Φ_earth_modern ≈ 1.5×10^11`

   Estos rangos encajan bien en el barrido 0.01–100 Tmol/yr de Schwieterman. ([ResearchGate][4])

3. Para **NH₃**, puedes hacer algo análogo, pero aquí no tienes un flujo “estándar” igual de consolidado. Una estrategia razonable:

   * Tomar un flujo base Φ₀(NH₃) de alguna revisión global (o de un modelo tipo Seager/Bains/Huang “Cold Haber World” para poner un orden de magnitud). ([arXiv][11])
   * Escalar:

     * Pre-agrícola: 0.2×Φ₀.
     * Tierra actual: 1×Φ₀.
     * ExoFarm: 10× y 100× Φ₀.

---

## 4. Setup de los casos numéricos (qué casos corres)

### 4.1. Planeta y perfiles T–z

* **Planeta**:

  * `R_p = R_⊕`, `g = g_⊕` (puedes fijar 1 bar a z=0).
  * Composición de fondo:

    * `N2 ≈ 0.78`, `O2 ≈ 0.21`, `Ar ≈ 0.01`, `CO2 ≈ 4×10^-4`, H₂O según perfil.

* **Perfil T(z):**

  * Caso A: usar un perfil estándar de atmósfera terrestre (tropopausa a ~200 K, estratosfera calentando etc.).
  * Caso B (para TRAPPIST-1): puedes usar output de un GCM para TRAPPIST-1e en modo “Earth-like” (p.ej. trabajos de Turbet+ o Lincowski+), o al menos un perfil paramétrico razonable que mantenga habitabilidad superficial. ([PMC][12])

* **Kzz(z):**

  * Copiar un perfil típico de Earth-like de Tsai 2021 u otro trabajo: Kzz ~10⁵–10⁷ cm²/s en troposfera, aumentando en la estratosfera. ([arXiv][3])

### 4.2. Espectros estelares

1. **Sol**:

   * Usa el espectro solar estándar de VULCAN o uno estilo Thuillier 2004 (ya utilizado en Schwieterman et al.). ([ResearchGate][4])

2. **TRAPPIST-1**:

   * Opción “high-fidelity”:

     * Usa el SED de **Mega-MUSCLES TRAPPIST-1** (Wilson+ 2021), disponible como tabla de flujo vs. longitud de onda (5 Å–100 μm). ([arXiv][2])
   * Opción alternativa:

     * Usa el espectro PHOENIX calibrado de Peacock+ 2018 (100 Å–2.5 μm) extendido a IR con un modelo. ([arXiv][13])

   En ambos casos, re-muestras a la cuadrícula UV de VULCAN y te aseguras de que la banda relevante para fotólisis de N₂O y NH₃ (λ < 300 nm) esté bien resuelta.

---

## 5. Diseño experimental: matriz de modelos

Te propongo algo así:

### 5.1. Ejes principales

1. **Tipo de estrella:** Sol vs TRAPPIST-1.

2. **Nivel de agricultura (modificado vía flujos superficiales):**

   * `A0` – Pre-agrícola (solo flujos naturales).
   * `A1` – Tierra actual.
   * `A2` – ExoFarm moderado (10×).
   * `A3` – ExoFarm extremo (100×).

3. **Oxígeno de fondo:**

   * Puedes empezar con 1 PAL de O₂ (moderno). Después, explorar 0.1 PAL y 0.01 PAL para ver cómo cambia la fotoquímica de N₂O (igual que en Schwieterman+). ([ResearchGate][4])

### 5.2. Casos mínimos

* **Sol + 1 PAL O₂:**

  * S-A0, S-A1, S-A2, S-A3.
* **TRAPPIST-1 + 1 PAL O₂:**

  * T-A0, T-A1, T-A2, T-A3.

Más adelante puedes añadir series con O₂ reducido.

---

## 6. Qué outputs guardar de VULCAN

Para cada caso:

1. **Perfiles verticales al estado estacionario** de:

   * N₂O, NH₃, NO, NO₂, HNO₃, HCN, CH₄, O₃, OH, HOx, NOx.
   * Temperatura, presión, Kzz, densidad total.

2. **Tasas de producción y destrucción** (P(z), L(z) para N₂O y NH₃) para separar:

   * Fotólisis vs reacciones químicas vs deposición.

3. **Columnas integradas**:

   * Columna total de N₂O y NH₃ (molec cm⁻²).
   * Columnas parciales troposfera/estratosfera.

4. **“Budget” químico**:

   * Contribución de agricultura (vía flujo de frontera) a la columna total, i.e. corre un caso con flujos agrícolas =0 y otro con flujos agrícolas >0, compara.

---

## 7. De VULCAN a espectros (para compararte con Haqq-Misra)

Una vez tengas los perfiles:

1. **Exportar perfiles a un radiative transfer**:

   Opciones típicas:

   * **Planetary Spectrum Generator (PSG)** – usado por Schwieterman para N₂O. ([research-collection.ethz.ch][14])
   * **SMART** – usado en Leung 2022 para metilhaluros. ([research-collection.ethz.ch][14])
   * **petitRADTRANS / Exo-Transmit** si prefieres algo más exoplanetero genérico. ([arXiv][15])

2. **Simular espectros** para:

   * **Tierra–Sol**:

     * Emisión térmica (5–20 μm).
     * Reflejado (0.3–3 μm).
   * **Tierra–TRAPPIST-1e**:

     * Transmisión en tránsito (0.6–10 μm, relevante para JWST NIRISS/NIRSpec/MIRI).
     * Emisión si quieres.

3. **Comparar directamente con Haqq-Misra**:

   * Ellos fijan mezcla de NH₃/N₂O y miran detectabilidad. ([arXiv][1])
   * Tú puedes:

     * Tomar tus mezclas derivadas fotoquímicamente para `A0`, `A1`, `A2`, `A3`.
     * Meterlas al generador sintético y ver:

       * ¿Qué escenario se parece a “Tierra actual”?
       * ¿Cuándo entras en régimen de detectabilidad (S/N > 5, etc.)?

---

## 8. Cómo “separar” agricultura de biología natural

Para poder decir algo tipo “esto es agricultura y no sólo biosfera natural”:

1. **Compara “A0” vs “A1” (pre-agrícola vs Tierra actual):**

   * Mide el aumento en columna de N₂O y NH₃.
   * Mira si la combinación de gases (N₂O + NH₃ + NOₓ + CH₄…) entra en regímenes de “runaway” fotquímico tipo Ranjan+ 2022 para NH₃, o se queda en escalamiento lineal con el flujo. ([arXiv][16])

2. **Añade un componente “abiotic agriculture-like”**:

   * Por ejemplo, explora flujos de N₂O a partir de procesos no biológicos (chemodenitrificación, relámpagos intensos, etc.), siguiendo Schwieterman 2022 y Barth+ 2024. ([arXiv][17])
   * Ve si puedes distinguir:

     * Perfiles verticales de N₂O (picos en estratosfera vs troposfera).
     * Co-presencia de otros gases (p.ej. NH₃ co-elevado) que sugieren fertilización vs sólo relámpagos.

3. **Define indicadores “tecnofirma”**:

   * Ratios como:

     * $\text{N₂O}/\text{CH₄}$,
     * $\text{NH₃}/\text{N₂O}$,
     * $\text{N₂O}/\text{NOₓ}$,
       comparados con límites de escenarios puramente biológicos en Schwieterman y Leung.

---

## 9. Checklist de archivos concretos que tendrás en tu carpeta de trabajo

Imagina una estructura tipo:

```text
VULCAN/
  networks/
    network_earth_CHNOS.dat       # red química adaptada para N2O/NH3
  stars/
    sun_thuillier_2004.dat        # espectro solar
    trappist1_megamuscles.dat     # SED TRAPPIST-1 re-muestreado
  planets/
    earth_sun/
      input_earth_sun_A0.yml      # pre-agrícola
      input_earth_sun_A1.yml      # actual
      input_earth_sun_A2.yml      # ExoFarm x10
      input_earth_sun_A3.yml      # ExoFarm x100
    earth_trappist/
      input_earth_trappist_A0.yml
      input_earth_trappist_A1.yml
      input_earth_trappist_A2.yml
      input_earth_trappist_A3.yml
  boundary_conditions/
    bc_earth_preagri.dat
    bc_earth_now.dat
    bc_earth_exofarm10.dat
    bc_earth_exofarm100.dat
  outputs/
    earth_sun_A0_profile.dat
    earth_sun_A1_profile.dat
    ...
    earth_trappist_A3_profile.dat
  spectra_inputs/
    earth_sun_A*.psg_profile.dat
    earth_trappist_A*.psg_profile.dat
```

En cada `bc_*.dat` defines:

* Flujo de N₂O (Φ en molec cm⁻² s⁻¹).
* Flujo de NH₃.
* Opcionalmente flujos de NO, HCN, etc.

---

## 10. Siguiente paso práctico

Si quieres, en el próximo mensaje podemos:

* Coger un **archivo de ejemplo de VULCAN** (un `input_*.yml` real de su GitHub).
* Re-escribirlo juntos como `input_earth_sun_A1.yml` con *valores concretos* (g, R, P, mezcla de fondo) y un ejemplo numérico de flujo de N₂O y NH₃.
* Y a partir de ahí, ir caso por caso.

Así te queda ya no sólo la visión del proyecto, sino ficheros listos para empezar a correr.

[1]: https://arxiv.org/abs/2204.05360?utm_source=chatgpt.com "Disruption of a Planetary Nitrogen Cycle as Evidence of Extraterrestrial Agriculture"
[2]: https://arxiv.org/abs/2102.11415?utm_source=chatgpt.com "The Mega-MUSCLES Spectral Energy Distribution Of TRAPPIST-1"
[3]: https://arxiv.org/abs/2108.01790?utm_source=chatgpt.com "A Comparative Study of Atmospheric Chemistry with VULCAN"
[4]: https://www.researchgate.net/publication/364163091_Evaluating_the_Plausible_Range_of_N2O_Biosignatures_on_Exo-Earths_An_Integrated_Biogeochemical_Photochemical_and_Spectral_Modeling_Approach?utm_source=chatgpt.com "Evaluating the Plausible Range of N2O Biosignatures ..."
[5]: https://arxiv.org/abs/2411.07394?utm_source=chatgpt.com "The Mega-MUSCLES Treasury Survey: X-ray to infrared Spectral Energy Distributions of a representative sample of M dwarfs"
[6]: https://essd.copernicus.org/articles/16/2543/2024/?utm_source=chatgpt.com "Global nitrous oxide budget (1980–2020) - ESSD Copernicus"
[7]: https://www.researchgate.net/publication/363753925_Ammonia_emissions_from_agriculture_and_their_contribution_to_fine_particulate_matter_A_review_of_implications_for_human_health?utm_source=chatgpt.com "Ammonia emissions from agriculture and their contribution ..."
[8]: https://github.com/exoclime/VULCAN/releases?utm_source=chatgpt.com "Releases · shami-EEG/VULCAN"
[9]: https://globalcarbonatlas.org/fr/budgets/nitrous-oxide-budget/?utm_source=chatgpt.com "Nitrous oxide Budget"
[10]: https://www.csiro.au/en/research/environmental-impacts/emissions/global-greenhouse-gas-budgets/global-nitrous-oxide-budget?utm_source=chatgpt.com "Global nitrous oxide budget"
[11]: https://arxiv.org/abs/1309.6014?utm_source=chatgpt.com "A Biomass-based Model to Estimate the Plausibility of Exoplanet Biosignature Gases"
[12]: https://pmc.ncbi.nlm.nih.gov/articles/PMC7378127/?utm_source=chatgpt.com "A Review of Possible Planetary Atmospheres in the ..."
[13]: https://arxiv.org/abs/1812.06159?utm_source=chatgpt.com "Predicting the Extreme Ultraviolet Radiation Environment of Exoplanets Around Low-Mass Stars: the TRAPPIST-1 System"
[14]: https://www.research-collection.ethz.ch/server/api/core/bitstreams/ece3fd97-5b34-4171-b924-3faa8e3b5998/content?utm_source=chatgpt.com "Large Interferometer For Exoplanets (LIFE). XII. The ..."
[15]: https://arxiv.org/abs/1611.03871?utm_source=chatgpt.com "Exo-Transmit: An Open-Source Code for Calculating Transmission Spectra for Exoplanet Atmospheres of Varied Composition"
[16]: https://arxiv.org/abs/2201.08359?utm_source=chatgpt.com "Photochemical Runaway in Exoplanet Atmospheres: Implications for Biosignatures"
[17]: https://arxiv.org/abs/2210.01669?utm_source=chatgpt.com "Evaluating the Plausible Range of N2O Biosignatures on Exo-Earths: An Integrated Biogeochemical, Photochemical, and Spectral Modeling Approach"
