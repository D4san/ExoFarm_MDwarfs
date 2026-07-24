# Bitácora Capa 2 — `life_proxima_b_earthlike`: SED, fotoquímica y rama LIFE

**Fecha de inicio:** 2026-07-22
**Estado al escribir:** SED preservada y convertida (validada); VULCAN Proxima
A0–A3 **en ejecución**; rama de emisión térmica pendiente de la aceptación de la
química.
**Regla de interpretación:** esto es un **análogo terrestre bajo el entorno
radiativo de Proxima Centauri**, no la atmósfera medida de Proxima b
([plan de dos capas](life_stage_iii_two_layer_workplan_2026-07-20.md)).

---

## 1. Pregunta científica

¿Cómo cambia el experimento controlado ExoFarm (forzamientos A0–A3 de N2O/NH3
sobre una atmósfera terrestre) cuando el entorno radiativo solar se sustituye
por el de una M5.5V activa y cercana (Proxima Centauri), y qué observabilidad
tendría en emisión térmica con LIFE para su objetivo insignia, Proxima b?

## 2. Espectro estelar: origen, cita y preservación

- **Producto:** SED pancromática MUSCLES Treasury Survey **v22** de
  **GJ 551 (Proxima Centauri)**, variante `adapt-const-res-sed` (1 Å constante,
  submuestreada en regiones de bajo S/N). Se preservó también la variante
  `var-res-sed` como referencia de archivo.
- **Descarga:** 2026-07-22 vía `astroquery.mast` (v0.4.11), URI
  `mast:HLSP/muscles/v22/gj551/hlsp_muscles_multi_multi_gj551_broadband_v22_adapt-const-res-sed.fits`.
  (Las rutas web históricas `archive.stsci.edu/missions/hlsp/...` y
  `prepds/...` hoy redirigen a HTML; la vía API es la reproducible.)
- **Preservación:** `Photochemical_Modeling/Config/Stellar_Spectra/`
  - `...adapt-const-res-sed.fits` — 5 189 760 bytes, MD5
    `f0f91be58db0896dc1152a0a958b485d`
  - `...var-res-sed.fits` — 80 651 520 bytes, MD5
    `9bea25448539a176d75dbc80c54e2cda`
- **Citas del producto:** France et al. 2016, ApJ 820, 89 (survey); Youngblood
  et al. 2016 (Lyα/EUV); Loyd et al. 2016 (panchromatic SEDs). DOI del HLSP:
  `10.17909/T9DG6F`.
- **Contenido:** 54 997 muestras, 3 Å–5.5 µm; combina HST STIS/FOS (UV-óptico),
  XMM EPIC (rayos X) y modelos APEC, reconstrucción de Lyα y fotosfera PHX.
  Columnas usadas: `WAVELENGTH` [Å], `FLUX` [erg s⁻¹ cm⁻² Å⁻¹] **observado en
  la Tierra**.

## 3. Conversión a flujo superficial VULCAN (la corrección observador→superficie)

Script versionado:
[`convert_proxima_muscles_sed.py`](../Photochemical_Modeling/Scripts/Simulation/convert_proxima_muscles_sed.py)
→ salida `VULCAN/atm/stellar_flux/ProximaCen_surface.txt` (54 997 filas,
0.30–5499.9 nm).

- **Regla de escala única** (contrato VULCAN, ver
  [metodología fotoquímica](photochemical_profiles_methodology.md)): el archivo
  estelar de VULCAN vive en la **superficie estelar**; VULCAN lo reescala solo
  con `(R_star/orbit_radius)²`. Por tanto aquí se aplicó exactamente una vez
  `F_surf = F_obs · (d/R_star)²`, con `d = 1.30 pc` y `R_star = 0.14 R_⊙`
  (ambos del catálogo de LIFE X, §5). Factor aplicado:
  `(d/R_star)² = 1.696242e17` (`d/R_star = 4.118545e8`; compárese el factor
  análogo TRAPPIST documentado, `4.7272904e9`). Usar el mismo `R_star` en el
  YAML garantiza que `R_star` se cancela y el flujo en órbita es
  `F_obs·(d/a)²` — sin doble escalado.
- **Unidades:** Å→nm (÷10) y por-Å→por-nm (×10).
- **Limpieza:** negativos→0 (resultaron **0 de 54 997**).

### Validaciones (salida del script, 2026-07-22)

| Chequeo | Valor | Esperado / criterio |
| --- | --- | --- |
| Integral bolométrica del SED observado | 2.964e-8 erg s⁻¹ cm⁻² | 2.859e-8 (L=0.00151 L_⊙ a 1.30 pc; Ribas et al. 2017) → **razón 1.037** ✅ |
| Lyα 1210–1222 Å | 4.429e-12 erg s⁻¹ cm⁻² | > 0 y dominante del FUV ✅ |
| FUV 912–1700 Å | 5.377e-12 | Lyα/FUV ≈ 0.82, típico de M enana ✅ |
| NUV 1700–3200 Å | 1.559e-12 | > 0 ✅ |

## 4. Fotoquímica VULCAN Proxima A0–A3

Configs versionadas:
`Photochemical_Modeling/Config/planets/earth_proxima_b/input_earth_proxima_b_A{0..3}.yml`;
runner [`run_parallel_proxima.py`](../Photochemical_Modeling/Scripts/Simulation/run_parallel_proxima.py)
(clon del runner Tierra–Sol; 4 procesos paralelos; lanzado 2026-07-22, log
`Photochemical_Modeling/proxima_campaign.log`).

Decisiones de configuración (fuente → decisión):

| Parámetro | Valor | Fuente / justificación |
| --- | --- | --- |
| PT/Kzz | `atm/atm_Earth_Jan_Kzz.txt` (terrestre, CIRA) | Control del experimento; requerido por el usuario y el [plan de dos capas](life_stage_iii_two_layer_workplan_2026-07-20.md). No es el clima real de Proxima b. |
| R_p | 7.845e8 cm = 1.23 R_⊕ | LIFE X Tabla G.1 (0.11 R_J), radio estimado vía relaciones masa–radio (Hatzes & Rauer 2015; Otegi et al. 2020). |
| g_s | 1030.0 cm s⁻² | Derivada: g_⊕·(M_p/M_⊕)/(R_p/R_⊕)² con M_p=1.59 M_⊕ (masa estadística LIFE X, 0.005 M_J) y R_p=1.23 R_⊕. |
| orbit_radius | 0.0485 AU | Anglada-Escudé et al. 2016 (a=0.0485 AU); LIFE X Tabla G.1 lo lista redondeado a 0.05. |
| r_star | 0.14 R_⊙ | LIFE X Tabla G.1. Mismo valor usado en la conversión SED (cancelación exacta). |
| sl_angle / f_diurnal | 48.0° / 1.0 | Convención de planeta bloqueado por marea heredada de la rama TRAPPIST-1e aceptada (decisión 2026-06-29 del tracker). P=11.2 d hace probable el bloqueo (Ribas et al. 2016). **Inferencia de proyecto**, no dato de LIFE X. |
| const_mix (N2 0.78, O2 0.20, CO2 4e-4, …) | valores Tierra | Control terrestre; el plan de dos capas prohíbe heredar el `100x CO2` de TRAPPIST. |
| BCs A0–A3 | `bc_earth_{preagri,current,exofarm_moderate,exofarm}_full.txt` | **BC activos corregidos** (post-corrección N2O 2026-07-01, α=2.55/15). Esta rama nace con la matriz vigente — a diferencia del benchmark Tierra–Sol congelado (`earth_20260615_pre_n2o_correction`). |
| Red química | `SNCHO_full_photo_network` + fotólisis | Idéntica a las ramas aceptadas. |
| Salidas | `Proxima_b_A{0..3}_{PreAgri,Current,Moderate,Extreme}.vul` | → `Photochemical_Modeling/Results/Outputs/`. |

Criterio de aceptación: registrar `end_case`, validar especies objetivo y
perfiles; la salvedad de convergencia de TRAPPIST **no** se hereda
automáticamente (el runner marca fallo si `end_case ≠ 1`; una terminación ≠1 se
evaluará explícitamente antes de aceptar/rechazar).

## 5. Parámetros congelados estrella/planeta (con citas)

Fuente primaria unificada: **LIFE X — Carrión-González et al. 2023, A&A 678,
A96, Tabla G.1** (catálogo estadístico; medianas de 1000 realizaciones
orbitales, radios vía Hatzes & Rauer 2015 / Otegi et al. 2020, parámetros
estelares de su catálogo de entrada):

| Cantidad | Valor | Nota |
| --- | --- | --- |
| d | 1.30 pc | |
| T_★ | 3050 ± 100 K | M5.5V |
| R_★ | 0.14 (+0.02/−0.02) R_⊙ | |
| P | 11.2 d | descubrimiento: Anglada-Escudé et al. 2016 |
| a | 0.0485 AU (LIFE X: 0.05) | |
| M_p | 0.005 M_J = 1.59 M_⊕ | masa estadística (mediana sobre inclinaciones); m sin i = 1.27 M_⊕ (Anglada-Escudé 2016) |
| R_p | 0.11 R_J = 1.23 R_⊕ | estimado, no medido (no transita) |
| T_eq | 229 (+34/−37) K | albedo de Bond fijado por LIFE X |
| Separación angular | a/d = 0.0373″ | derivada; entra a la escena LIFE |

Validación externa de luminosidad usada en §3: Ribas et al. 2017, A&A 603, A58
(L = 0.00151 L_⊙; irradiancia XUV ≈ 60× Tierra).

## 6. Configuración LIFE prevista para la rama de emisión (según LIFE X)

Para cumplir el requisito de basar la observación en el paper que explora este
planeta como objetivo (LIFE X):

- Arquitectura de referencia: **4 colectores de 2 m**, throughput 5%,
  banda **4–18.5 µm** (escenarios pesimista 1 m / optimista 3.5 m para
  sensibilidad).
- **Resolución espectral R=20** (la que usa LIFE X para su S/N; cita textual:
  "Spectral resolution 20 λ/Δλ"). Para diagnósticos de caracterización se
  reportará además R=50 (requisito LIFE de caracterización, "4−18.5 µm, R=50,
  S/N>10"), siempre etiquetado.
- **Exozodi = 3 zodis** ("we set the exozodiacal dust level to 3 zodi for all
  exoplanetary systems"); sensibilidad opcional a 27 zodis (su límite superior
  95% para Proxima… documentado en el paper).
- Escena: d=1.30 pc, T_★=3050 K, R_★=0.14 R_⊙, separación 0.0373″; LIFEsim
  clásico (ruido fotónico: fuga estelar + zodi local + exozodi), igual que
  LIFE X.
- **Ancla de validación:** LIFE X Tabla 3 para Proxima b: S/N(10 h) =
  45 / **170** / 466 con D = 1 / 2 / 3.5 m, y t(S/N=7) = 0.2 / 0.02 / 0.002 h.
  Antes de los diagnósticos moleculares, nuestra escena debe reproducir el
  orden del S/N=170 (continuo, R=20, 10 h, D=2 m) — esa es la puerta de
  calibración de la escena Proxima.

> **Puerta de calibración: SUPERADA (2026-07-22).** Con
> [`validate_proxima_life_scene.py`](../Thermal_Emission_Spectroscopy/scripts/validate_proxima_life_scene.py)
> (planeta cuerpo negro T_eq=229 K, R_p=1.23 R_⊕; escena LIFE X: R=20, z=3,
> d=1.30 pc, T_★=3050 K, R_★=0.14 R_⊙, separación 0.0373″, latitud eclíptica
> 44.8° calculada de las coordenadas ICRS con astropy) obtenemos S/N(10 h) =
> **48.4 / 166.5 / 412.4** vs los 45 / 170 / 466 de LIFE X — razones
> 1.07 / **0.98** / 0.88. La configuración de referencia (D=2 m) se reproduce
> al 2%; la dispersión restante es coherente con que LIFE X promedia 1000
> realizaciones orbitales y nosotros evaluamos una época con la separación
> media. La escena Proxima queda validada para los diagnósticos moleculares.

## 7. Resultados (ejecutados 2026-07-23)

### 7.1 Fotoquímica VULCAN Proxima A0–A3 — ACEPTADA

Los cuatro productos convergieron a **estado estacionario `end_case = 1`** (count
13255/12916/13854/14275), sin la salvedad de convergencia parcial de TRAPPIST-1e.
El forzamiento ExoFarm se propagó: N2O y NH3 superficiales crecen monótonamente
A0→A3 bajo la UV de Proxima:

| Escenario | N2O superf. | NH3 superf. |
| --- | --- | --- |
| A0 | 1.32e-7 | 1.22e-10 |
| A1 | 1.87e-7 | 5.38e-10 |
| A2 | 2.81e-7 | 1.58e-9 |
| A3 | 9.79e-7 | 6.37e-9 |

> Observación (interpretación de proyecto): el N2O de A3 Proxima (9.8e-7) es ~½
> del de A3 Tierra–Sol (1.8e-6) pese a la UV más baja de la M — el entorno M
> reconfigura la química de pérdida/producción, no simplemente "preserva más
> N2O". Requiere análisis dedicado antes de una afirmación.

Ejecución segura: **máx 2 solvers VULCAN a la vez** (el uso de RAM crece con los
pasos; 4 solvers saturaron los 7.6 GB de esta WSL → OOM). Perfiles exportados a
`Transmission_Spectroscopy/profiles/Proxima_b_*_{PT,chem}.txt`.

### 7.2 Emisión + LIFE — interfaz validada y S/N

Campaña `life_proxima_b_earthlike_v1`
([outputs/](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/)).
Forward A0 validado (chequeo cuerpo negro: Fp_obs @10µm = 1.19e-12 vs 9.25e-13,
ratio 1.28, PASS). 18 contrafactuales N2O/NH3+controles. S/N con la escena LIFE X
(R=20, D=2 m, z=3, d=1.30 pc). Continuo ~393 en 10 h.

**Señal molecular ExoFarm, SNR de banda (t=10 h):**

| Escenario | Molécula/banda | SNR Proxima | (SNR Tierra–Sol) |
| --- | --- | --- | --- |
| A3 | N2O 16.5–17.5 µm | **4.80** | 0.074 |
| A3 | N2O 7.5–8.1 µm | **2.81** | 0.163 |
| A3 | NH3 9.5–11.5 µm | **1.44** | 0.005 |
| A2 | N2O 17 µm | 1.20 | — |

Escalado √t confirmado (ratio 100h/1h = 10.0). Tiempo para S/N=5 (A3): N2O 17 µm
**11 h**, N2O 7.8 µm **32 h**, NH3 10.6 µm **120 h** — frente a 45 506 / 9 381 /
9.8e6 h en Tierra–Sol a 10 pc.

### 7.3 Interpretación

La misma perturbación ExoFarm, con la misma cadena de emisión+LIFE, es
**~30–65× más detectable en Proxima b (1.30 pc) que en un gemelo solar a 10 pc**,
casi enteramente por cercanía (tiempo ∝ d⁴ = (10/1.30)⁴ ≈ 3500×). El pico más
beneficioso pasa de N2O 7.8 µm (Tierra) a **N2O 17 µm** (Proxima). La tecnofirma
agrícola extrema (A3) alcanzaría un diagnóstico S/N=5 en **decenas de horas** con
LIFE — una sola visita. Salvedades: (i) SNR es diagnóstico, no detección; (ii)
Tierra–Sol usa el conjunto pre-corrección N2O y Proxima los BC corregidos, así
que el contraste está dominado por distancia con una diferencia secundaria de
química/BC; (iii) PT terrestre controlado, no el clima real de Proxima b.

### 7.4 Figuras

En `outputs/life_proxima_b_earthlike_v1/plots/`:
`emission_A0A3_Fp_obs.png`, `emission_molecular_residuals_proxima.png`,
`life_classic_A3_signal_vs_noise_times_proxima.png`,
`life_classic_snr_comparison_proxima.png`; y la comparación directa en
`outputs/_comparison/earthsun_vs_proxima_life_snr.png`.

Scripts (target-aware, `--campaign proxima`):
[`run_proxima_forward.py`](../Thermal_Emission_Spectroscopy/scripts/run_proxima_forward.py),
[`run_proxima_life_snr.py`](../Thermal_Emission_Spectroscopy/scripts/run_proxima_life_snr.py),
[`plot_earthsun_vs_proxima.py`](../Thermal_Emission_Spectroscopy/scripts/plot_earthsun_vs_proxima.py).

## 8b. Qué queda pendiente

1. LIFEsimMC/PHRINGE (ruido instrumental + covarianza) para ambas capas.
2. Decisión de procedencia N2O de Tierra–Sol (rerun con BC corregidos) para una
   comparación de misma-procedencia.
3. Análisis dedicado de por qué el N2O de A3 baja bajo Proxima.
4. Diseño de retrievals (solo tras la puerta MC+covarianza).

## 8. Referencias

- Carrión-González, Ó., et al. 2023, A&A 678, A96 (LIFE X). DOI: 10.1051/0004-6361/202347027
- Anglada-Escudé, G., et al. 2016, Nature 536, 437 (descubrimiento Proxima b).
- Ribas, I., et al. 2017, A&A 603, A58 (propiedades radiativas de Proxima).
- Ribas, I., et al. 2016, A&A 596, A111 (rotación/bloqueo por marea).
- France, K., et al. 2016, ApJ 820, 89 (MUSCLES); Youngblood et al. 2016;
  Loyd et al. 2016. HLSP DOI: 10.17909/T9DG6F.
- Hatzes & Rauer 2015; Otegi et al. 2020 (relaciones masa–radio usadas por LIFE X).
- Quanz, S., et al. 2022, A&A 664, A21 (LIFE I, arquitectura de referencia).
