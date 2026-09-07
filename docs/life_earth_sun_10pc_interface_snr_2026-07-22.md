# Capa 1 LIFE `life_earth_sun_10pc`: forward de emisión, contrafactuales y S/N clásico

> **Estado consolidado 2026-08-30:** benchmark de interfaz clásica validado y
> cerrado con su etiqueta `earth_20260615_pre_n2o_correction`. No se ejecutó una
> matriz canónica de retrievals Tierra--Sol. LIFEsimMC/PHRINGE y la decisión de
> rerun con N2O corregido permanecen abiertos.

**Fecha:** 2026-07-22
**Etapa:** III (emisión térmica / LIFE), Capa 1 — benchmark de interfaz
**Campaña:** `life_earth_sun_10pc_interface_v1`
**Procedencia de perfiles:** `earth_20260615_pre_n2o_correction` (validación de
interfaz; **no** la matriz N2O vigente sin decisión de rerun —
[nota de procedencia](earth_sun_n2o_matrix_provenance_2026-07-20.md)).
**Herramientas:** POSEIDON 1.4.0 (emisión), LIFEsim 0.2.32 (clásico), env conda
`ExoFarm_LIFE`.

> **Advertencia de alcance.** Este informe valida la **interfaz** POSEIDON→LIFE y
> reporta un diagnóstico S/N con **ruido astrofísico/fotónico** (LIFEsim clásico).
> No incluye aún el ruido de inestabilidad instrumental ni la covarianza
> (LIFEsimMC/PHRINGE). **SNR es un diagnóstico, no una detección.**

## 1. Pregunta científica

¿La interfaz de emisión térmica + observación LIFE preserva de forma trazable las
diferencias del conjunto Tierra–Sol A0–A3 al colocar el sistema a 10 pc, y qué
S/N tendría la tecnofirma agrícola (N2O, NH3) en emisión directa con LIFE?

## 2. Scripts, insumos y productos

- Wrapper de emisión: [`Thermal_Emission_Spectroscopy/scripts/emission_forward.py`](../Thermal_Emission_Spectroscopy/scripts/emission_forward.py)
- Runner forward + manifiesto: [`run_layer1_forward.py`](../Thermal_Emission_Spectroscopy/scripts/run_layer1_forward.py)
- Contrafactuales: [`make_counterfactuals.py`](../Thermal_Emission_Spectroscopy/scripts/make_counterfactuals.py), [`run_counterfactual_forward.py`](../Thermal_Emission_Spectroscopy/scripts/run_counterfactual_forward.py)
- Escena LIFE + adaptador de unidades: [`life_scene_classic.py`](../Thermal_Emission_Spectroscopy/scripts/life_scene_classic.py)
- Análisis S/N: [`run_life_snr_classic.py`](../Thermal_Emission_Spectroscopy/scripts/run_life_snr_classic.py)
  (guarda además los productos por bin en `lifesim/life_classic_binned_products.npz`)
- Figuras estilo capa curada (calcadas de las figuras finales de transmisión
  `trappist1e_pure_a0_molecular_residuals_v2` y
  `trappist1e_net_molecular_snr_comparison`, adaptadas a emisión):
  [`plot_emission_molecular_residuals.py`](../Thermal_Emission_Spectroscopy/scripts/plot_emission_molecular_residuals.py),
  [`plot_life_signal_noise_times.py`](../Thermal_Emission_Spectroscopy/scripts/plot_life_signal_noise_times.py),
  [`plot_emission_snr_comparison.py`](../Thermal_Emission_Spectroscopy/scripts/plot_emission_snr_comparison.py)
- Insumos: `Transmission_Spectroscopy/profiles/Earth_A0..A3_{PT,chem}.txt` (VULCAN
  `end_case = 1`), enlazados por checksum en el manifiesto.
- Productos: `Thermal_Emission_Spectroscopy/outputs/life_earth_sun_10pc_interface_v1/`
  → `manifest.json`, `forward_emission/A0..A3_emission.npz`,
  `molecular_diagnostics/` (18 contrafactuales), `tables/life_classic_snr_table.csv`,
  `plots/` (espectros A0–A3, señal vs ruido A3, S/N vs tiempo).

## 3. Cálculo y supuestos

**Forward de emisión (POSEIDON).** Estrella Sol PHOENIX (R=1 R⊙, Teff=5772 K,
log g=4.44, [M/H]=0), planeta Tierra (R=1 R⊕, M=1 M⊕), superficie opaca a 1 bar.
PT/química leídos de archivo (`PT_profile="file_read"`, `X_profile="file_read"`),
`thermal=True`, base de opacidades **High-T** (`Opacity_database_v1.3.hdf5`, única
con NH3), malla 3–20 µm a R=10000, 7 absorbentes (H2O, CO2, CH4, O2, O3, N2O,
NH3) sobre N2. Se calculan dos cantidades: `Fp/Fs` (`spectrum_type="emission"`) y
**`Fp_obs`** (`spectrum_type="direct_emission"`, flujo observado a d), esta última
la que consume LIFE.

**Puerta de unidades (validada).** `F_obs(285 K, R⊕, 10 pc)` de un cuerpo negro a
10 µm = 1.03e-14 W m⁻² m⁻¹; POSEIDON A0 da 1.16e-14 (ratio 1.13) → confirma la
geometría `(R_p/d)²` y las unidades. Conversión a LIFEsim clásico:
`F_ph = Fp_obs · λ/(h c)` [ph m⁻² s⁻¹ m⁻¹], entregado como Quantities astropy a
`Instrument.get_spectrum` (requiere el SpectRes modificado de fdannert por el
kwarg `edge_mode`).

**Escena LIFE clásico.** Baseline: colectores 2 m, R=50, banda 4–18.5 µm (77
bins), QE 0.7, throughput 0.05; 10 pc, latitud eclíptica 0.79 rad, exozodi=1,
separación 0.1″ (1 UA a 10 pc), localzodi `darwinsim`. Ruido: fuga estelar +
zodi local + exozodi + shot fotónico. Tiempo de referencia 10 h.

**Señal molecular (contrafactual).** Para molécula i en el escenario S:
`ΔF_i = F_binned(S) − F_binned(S con perfil de i reseteado a A0)`, verificado
(A3: N2O superficie 1.84e-6 → 2.46e-7 = A0; NH3 intacto). SNR de banda
diagnóstica `SNR_i,band = sqrt(Σ_bins (ΔF_i/σ)²)`, con σ de la observación del
escenario completo.

### 3.1 Verificación de la base de opacidades (High-T vs Temperate, 2026-07-22)

Toda la campaña usa la base **High-T** (`Opacity_database_v1.3.hdf5`), igual que
la Etapa II de transmisión y por la misma razón verificada en el HDF5: la base
Temperate (`Opacity_database_0.01cm-1_Temperate.hdf5`) **no contiene NH3**, una
de las dos moléculas objetivo. Diferencias estructurales relevantes: High-T
muestrea T en [100, 200, 300, 400, ...] K (pasos de 100 K en el régimen
terrestre), mientras Temperate usa pasos de 20 K en 100–400 K; la resolución
espectral en la banda LIFE es la misma (0.01 cm⁻¹). El rango de la atmósfera
(187–300 K) queda **interpolado, no extrapolado**, en ambas.

Para cuantificar el sesgo se recomputó el forward A3 con las 6 especies comunes
(sin NH3) en ambas bases (producto:
`forward_emission/A3_dbcheck_HT_vs_Temperate.npz`). A la resolución LIFE
(R=50): continuo +0.3%, O3 −0.4%, CO2 15 µm −1.6%, banda N2O 7.8 µm +3.6%
(máx 8% por bin), y el peor bin es la banda de H2O a 6.3 µm (+32%, región de
señal pequeña). La cantidad que gobierna el diagnóstico —la **profundidad de la
banda N2O 7.8 µm** (continuo−banda)— difiere solo **−1.8%** entre bases. Dado
que la conclusión central es un déficit de detectabilidad de ~1.5–3 órdenes de
magnitud, un sesgo de pocos por ciento en señal/flujo no altera ninguna
conclusión. Caveat registrado: si una campaña futura (p. ej. tras optimizar
apertura/distancia) acerca la S/N a los umbrales, repetir el subconjunto de 6
especies con Temperate como control sistemático y tratar con cautela la región
H2O 6.3 µm.

## 4. Resultado directo

- **Interfaz validada:** forward A0 físico (chequeo cuerpo negro PASS); espectro
  Tierra clásico con CO2 15 µm, O3 9.6 µm, CH4/N2O 7.7–7.8 µm, H2O.
- **Continuo:** SNR/bin máx ≈ 1.31 @ 11.9 µm; SNR total (cuadratura) ≈ 5.6 en
  10 h, casi idéntico entre A0–A3 (la perturbación ExoFarm es un diferencial
  pequeño).
- **Señal molecular ExoFarm (t = 10 h)** — mejor pico **N2O a 7.82 µm**:

  | Escenario | Molécula | Banda [µm] | SNR banda | SNR mejor bin |
  | --- | --- | --- | --- | --- |
  | A3 | N2O | 7.5–8.1 | **0.163** | 0.115 @ 7.82 |
  | A3 | N2O | 16.5–17.5 | 0.074 | 0.051 @ 17.05 |
  | A2 | N2O | 7.5–8.1 | 0.049 | 0.036 @ 7.82 |
  | A1 | N2O | 7.5–8.1 | 0.021 | 0.016 @ 7.82 |
  | A3 | NH3 | 9.5–11.5 | 0.005 | 0.004 @ 10.77 |

- **S/N vs tiempo:** escalado `√t` confirmado (A3 total 1.8/5.6/17.7 a 1/10/100 h;
  ratio 100h/1h = 10.0). La señal más fuerte (A3 N2O, banda 0.163 @ 10 h) alcanza
  SNR≈5 recién hacia ~1e4 h; ni a 1000 h llega a 5.
- **Figuras de capa curada (2026-07-22, mismo estilo que transmisión):**
  `plots/life_earth_sun_emission_molecular_residuals_v1.png` (espectros A0--A3 +
  paneles de señal N2O/NH3, con convención de déficit de emisión
  `F(reset)−F(full) ≥ 0` para reflejar la convención positiva en ppm de la figura
  de transmisión), `plots/life_classic_A3_signal_vs_noise_times.png` (pisos de
  ruido 1σ a 10/100/1000 h, σ ∝ 1/√t verificado) y
  `plots/life_classic_snr_comparison.png` con (a) S/N pico por rasgo espectral
  (7.8/17.0 µm N2O, 10.7 µm NH3) × escenario × tiempo (10/100/1000 h) y
  (b) horas requeridas para S/N fijo en A3: N2O 7.8 µm cruza S/N=3 a ~6.8e3 h y
  S/N=5 a ~1.9e4 h; NH3 10.7 µm necesita ~6.8e6 / ~1.9e7 h — fuera de todo
  presupuesto observacional realista.

## 5. Interpretación

En la configuración **baseline de LIFE (2 m) a 10 pc y con ruido solo
astrofísico**, la tecnofirma agrícola en emisión térmica **no es detectable**:
el suelo de ruido 1σ supera las señales |ΔF| de N2O/NH3 por 1–3 órdenes de
magnitud. El diagnóstico ordena los observables: **N2O ≫ NH3** (NH3 es traza y su
banda de 10.5 µm queda invisible incluso con el forzamiento ×15 de A3), y dentro
de N2O el pico más beneficioso es **7.82 µm**, seguido de ~17 µm. Esto es
consistente con la advertencia de la rama de transmisión sobre lo problemático de
NH3.

## 6. Qué todavía no puede concluirse

- No es un resultado de la **matriz N2O vigente**: los perfiles A2/A3 son
  pre-corrección. Interpretarlo como ExoFarm actual exige la decisión de rerun.
- No incluye **ruido instrumental ni covarianza** (LIFEsimMC/PHRINGE), que solo
  puede reducir la S/N. Ningún número aquí autoriza una afirmación de detección.
- Los parámetros de escena (apertura 2 m, 10 pc, R=50, latitud/zodi) no están
  optimizados; un barrido de sensibilidad mostraría cuánto acercan la señal.

## 7. Siguiente análisis

1. Rama **LIFEsimMC/PHRINGE**: ruido de inestabilidad instrumental, covarianza
   completa y whitening ZCA con estrella de calibración, sobre los mismos
   espectros de emisión. Es la puerta previa a cualquier retrieval LIFE.
2. Decisión de procedencia N2O (rerun con BC corregidos vs. etiqueta histórica).
3. Solo después de resolver esas dos puertas: decidir si una campaña de
   retrievals Tierra--Sol responde una pregunta científica útil. No forma parte
   de la matriz clásica canónica actual.

## 8. Referencias

- POSEIDON: MacDonald 2023, JOSS 8(81), 4873; tutorial de emisión.
- LIFEsim / LIFE II: Dannert et al. 2022, A&A 664, A22.
- LIFE III (gemelo terrestre a 10 pc): Konrad et al. 2022, A&A 664, A23.
- LIFE XII (detectabilidad de N2O): Angerhausen et al. 2024, AJ 167, 128.
- Procedencia de perfiles: [nota N2O 2026-07-20](earth_sun_n2o_matrix_provenance_2026-07-20.md).
