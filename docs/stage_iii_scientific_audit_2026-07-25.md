# Auditoría científica de la Etapa III (emisión térmica + LIFE), 2026-07-25

> **Actualización de estado, 2026-08-30:** la rama LIFEsim clásica fue cerrada
> con una matriz canónica de 8 retrievals Proxima A0--A3 × {10 h, 240 h}. Esta
> auditoría conserva la evaluación previa a los retrievals; el cierre, las
> limitaciones y la clasificación de los productos de 1200 h están en la
> [validación consolidada](lifesim_classic_stage_iii_validation_2026-08-30.md).

**Alcance:** rastrear de dónde salió cada dato, cómo se tomó cada decisión y
qué parte de la configuración observacional está anclada a referencias (serie
LIFE y fuentes primarias) frente a inferencias de proyecto. Cubre las campañas
`life_earth_sun_10pc_interface_v1` (Capa 1) y `life_proxima_b_earthlike_v1`
(Capa 2), ambas en su rama LIFEsim clásico (ruido fotónico).

Etiquetas: **[SRC]** = hecho derivado de fuente citada y verificada en esta
ejecución; **[INF]** = inferencia/decisión de proyecto documentada; **[VAL]** =
validación ejecutada con resultado numérico.

---

## 1. Procedencia de los insumos

| Insumo | Origen | Verificación |
| --- | --- | --- |
| Perfiles Tierra–Sol A0–A3 (PT+química) | VULCAN local, productos aceptados 2026-06-15, hand-off `Transmission_Spectroscopy/profiles/Earth_*` | [SRC] `end_case=1`; checksums MD5 congelados en `manifest.json` de la campaña. **Salvedad:** A2/A3 son el conjunto pre-corrección N2O (`earth_20260615_pre_n2o_correction`); ver [nota de procedencia](earth_sun_n2o_matrix_provenance_2026-07-20.md). |
| SED estelar de Proxima | MUSCLES Treasury v22, GJ551, producto `adapt-const-res-sed` (MAST HLSP, DOI 10.17909/T9DG6F; France et al. 2016; Youngblood et al. 2016; Loyd et al. 2016) | [SRC] descargado vía `astroquery.mast` 2026-07-22; MD5 `f0f91be...`; combina HST STIS/FOS + XMM + modelos (APEC, Lyα reconstruida, fotosfera PHX). |
| Conversión SED a superficie estelar | `convert_proxima_muscles_sed.py` (escala única `(d/R★)²`) | [VAL] integral bolométrica del SED observado = 1.037× la esperada de L=0.00151 L⊙ (Ribas et al. 2017) a 1.30 pc; Lyα>FUV>NUV coherente con M enana; 0 flujos negativos. R★ se cancela contra el reescalado `(R★/a)²` interno de VULCAN → sin doble escalado (contrato documentado en [metodología](photochemical_profiles_methodology.md)). |
| Fotoquímica Proxima A0–A3 | VULCAN local, configs `Config/planets/earth_proxima_b/`, BC **activos corregidos** (`bc_earth_*_full.txt`, post-corrección 2026-07-01) | [VAL] los 4 con `end_case=1` (count 13255/12916/13854/14275); N2O/NH3 superficiales crecen monótonos A0→A3. |
| PT/Kzz de la Capa 2 | `VULCAN/atm/atm_Earth_Jan_Kzz.txt` (terrestre, CIRA) | [INF] control del experimento exigido por el [plan de dos capas](life_stage_iii_two_layer_workplan_2026-07-20.md) y por decisión del usuario; NO es el clima de Proxima b. |
| Opacidades | POSEIDON `Opacity_database_v1.3.hdf5` ("High-T"), inputs Zenodo 19595136, MD5 verificado | [VAL] elegida porque la base Temperate **no contiene NH3** (inspección directa del HDF5); sesgo cuantificado vs Temperate a R=50: profundidad de banda N2O 7.8 µm difiere −1.8%, continuo <1% (sección 3.1 del [informe Capa 1](life_earth_sun_10pc_interface_snr_2026-07-22.md)). |
| Estrella para Fp/Fs | PHOENIX vía `create_star` (Sol: 5772 K/1 R⊙/logg 4.44; Proxima: 3050 K/0.14 R⊙/logg 5.2) | [SRC] parámetros de Proxima de LIFE X Tabla G.1; logg 5.2 [INF]. `direct_emission` (la cantidad LIFE) no depende del espectro estelar. |

## 2. Parámetros del sistema Proxima b — una sola fuente citable

Todos congelados de **LIFE X: Carrión-González et al. 2023, A&A 678, A96,
Tabla G.1** (medianas de su catálogo estadístico; radios vía Otegi et al. 2020 /
Hatzes & Rauer 2015): d=1.30 pc; T★=3050±100 K; R★=0.14 R⊙; P=11.2 d;
a=0.0485 AU (Anglada-Escudé et al. 2016; LIFE X lo tabula 0.05); M_p=0.005 M_J
=1.59 M⊕ (masa estadística; m·sin i=1.27 M⊕); R_p=0.11 R_J=1.23 R⊕ (estimado,
no medido — no transita); T_eq=229 K. Derivados [INF]: g_s=1030 cm/s²
(=g⊕·M/R²); separación angular 0.0373″ (=a/d); latitud eclíptica 44.8°
(coordenadas ICRS + astropy). Geometría bloqueada por marea (f_diurnal=1,
sl_angle=48°) [INF]: convención heredada de la rama TRAPPIST aceptada
(decisión 2026-06-29 del tracker); el bloqueo es esperable con P=11.2 d
(Ribas et al. 2016).

## 3. Configuración observacional LIFE — qué viene de qué paper

| Elemento | Valor usado | Fuente |
| --- | --- | --- |
| Arquitectura | 4 colectores, nulling X-array; D=2 m (referencia; 1/3.5 m como pesimista/optimista) | [SRC] LIFE I (Quanz et al. 2022, A&A 664, A21) define la referencia; LIFE X usa exactamente esos 3 escenarios. |
| Banda espectral | 4–18.5 µm | [SRC] LIFE I/III/X. |
| Throughput, QE | 5%, 0.7 | [SRC] escenario `baseline` de LIFEsim (Dannert et al. 2022, LIFE II) = "four 2-m telescopes with a total throughput of 5%" (LIFE X). |
| Resolución | Capa 2: **R=20** (S/N de detección; cita textual LIFE X: "Spectral resolution 20 λ/Δλ"). Capa 1: R=50 (requisito de caracterización, "4−18.5 µm, R=50, S/N>10", LIFE III/X) | [SRC]; la diferencia entre capas está etiquetada en cada producto. |
| Exozodi | Capa 2: **z=3** ("we set the exozodiacal dust level to 3 zodi for all exoplanetary systems", LIFE X). Capa 1: z=1 [INF] (benchmark limpio de interfaz). | [SRC]/[INF] |
| Ruido | Fuga estelar + zodi local (darwinsim) + exozodi + shot fotónico; sin ruido instrumental | [SRC] LIFEsim clásico (LIFE II); LIFE X usa lo mismo. La rama instrumental/covarianza (LIFEsimMC/PHRINGE, Huber et al. 2025) sigue **pendiente** — puerta abierta. |
| Escena Tierra–Sol | Sol 5772 K/1 R⊙ a 10 pc, separación 0.1″ (1 UA), lat 45° | [INF] benchmark sintético del workplan; 10 pc es la distancia canónica de gemelo terrestre en LIFE III. |

**[VAL] Calibración de escena contra el paper:** con planeta cuerpo negro
T_eq=229 K y R_p=1.23 R⊕, nuestra escena reproduce los anclajes de LIFE X
Tabla 3 para Proxima b: S/N(10 h) = 48.4/166.5/412.4 vs 45/**170**/466 para
D=1/2/3.5 m (razones 1.07/**0.98**/0.88). La configuración de referencia
coincide al 2%. Además [VAL] escalado √t exacto (ratio 100h/1h = 10.0) en ambas
capas, y [VAL] chequeo cuerpo-negro del forward A0 en ambas geometrías
(ratios 1.13 Tierra, 1.28 Proxima).

## 4. Cadena de decisiones (resumen auditable)

1. Cantidad física para LIFE = `spectrum_type="direct_emission"` (Fp observado a
   d, `F_p_obs=(R_p/d)²F_p`), no Fp/Fs [SRC: código POSEIDON inspeccionado;
   LIFE observa flujo directo]. Conversión a LIFEsim: `F_ph = F·λ/(hc)` como
   Quantities astropy [SRC: firma de `Instrument.get_spectrum`, "ph m-3 s-1"].
2. Señal molecular por contrafactual: `ΔF_i = F(escenario) − F(escenario con
   perfil de i reseteado a A0)` [INF, mismo diseño que el diagnóstico aceptado
   de transmisión]; [VAL] aislamiento verificado (el reset reproduce A0 en la
   especie objetivo y no toca las demás).
3. SNR de banda = suma en cuadratura de |ΔF|/σ por bin [INF diagnóstico;
   σ diagonal — válido solo en la rama clásica fotónica]. **SNR es diagnóstico,
   no detección.**
4. Bandas diagnósticas: N2O 7.5–8.1 y 16.5–17.5 µm; NH3 9.5–11.5 µm; controles
   H2O/CO2/O3/CH4 [SRC posiciones espectroscópicas estándar; N2O como
   tecnofirma sigue a Haqq-Misra et al. 2022 y LIFE XII (Angerhausen et al.
   2024)].

## 5. Limitaciones abiertas (deben acompañar cualquier claim)

1. **Sin ruido instrumental ni covarianza** (LIFEsimMC/PHRINGE pendiente); σ
   diagonales de LIFEsim clásico. Los retrievals que se lancen sobre estas σ
   heredan esta aproximación y deben etiquetarlo.
2. **Tierra–Sol usa el set pre-corrección N2O**; Proxima usa BC corregidos → la
   comparación entre capas está dominada por distancia pero tiene una
   diferencia secundaria de procedencia química (decisión de rerun pendiente).
3. PT terrestre controlado en Proxima; no clima real. R_p de Proxima b es
   estimado (no transita). Escena de una época (sin promedio orbital como el de
   las 1000 realizaciones de LIFE X — explica el ±12% frente a sus anclas).
4. Región H2O 6.3 µm: mayor sensibilidad a la base de opacidades (+32% HT vs
   Temperate por bin a R=50); tratar con cautela.

**Veredicto de auditoría de la rama clásica:** la cadena insumos→forward→ruido→SNR está trazada a
fuentes primarias con cuatro validaciones numéricas independientes (bolométrica,
cuerpo negro, anclas LIFE X, √t), las inferencias de proyecto están etiquetadas
y ninguna decisión de configuración observacional carece de referencia o de
registro. Fue apta para la matriz clásica posterior, siempre como cota optimista
con las limitaciones de §5. La validación instrumental final sigue pendiente de
LIFEsimMC/PHRINGE.
