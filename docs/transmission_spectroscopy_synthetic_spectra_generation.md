# Síntesis de Espectros de Transmisión con POSEIDON y Simulación de Ruido con PandExo

**Fecha del reporte:** 2026-06-18  
**Etapa del Pipeline:** Etapa 2 (Espectros Directos y Observaciones Sintéticas)  
**Herramientas:** POSEIDON (v1.4+) [2], PandExo [4]  
**Sistema:** Análogo de TRAPPIST-1e  

> [!WARNING]
> **Registro histórico de generación.** Describe el flujo y parámetros
> documentados el 2026-06-18; no define una cola ni una configuración actual.
> Antes de ejecutar transmisión/JWST, consultar
> [`project_resume.md`](project_resume.md),
> [`project_status_tracker.md`](project_status_tracker.md) y
> [`../Transmission_Spectroscopy/README.md`](../Transmission_Spectroscopy/README.md).
> La Etapa III LIFE usa emisión y no reutiliza este documento como receta.

---

## 1. Introducción y Flujo de Trabajo General

La generación de espectros sintéticos de transmisión traduce los perfiles físicos y fotoquímicos derivados aguas arriba (escenarios `A0`-`A3`) en observaciones simuladas del Telescopio Espacial James Webb (JWST). Este proceso es estrictamente unidireccional (forward) y se separa de la posterior campaña de inversión o ajuste (retrieval):

```text
Perfiles VULCAN (A0-A3) 
   │
   ▼
[1. POSEIDON: Espectro Directo] (R=10000)
   │
   ▼  (Convolución y rebinado a R=100 + Ruido de PandExo)
[2. Observación Sintética JWST] (.dat compatible con POSEIDON)
```

---

## 2. Espectroscopía Directa de Alta Resolución (Forward Model con POSEIDON)

El modelo directo implementado en POSEIDON simula el paso de la luz estelar a través del limbo planetario en alta resolución espectral.

### Parámetros Físicos del Sistema (TRAPPIST-1e)
*   **Estrella:** Modelo PHOENIX con $R_* = 0.11697 \, R_\odot$, $T_{\mathrm{eff}} = 2559.0$ K, $\log g = 5.21$ y metalicidad estelar $\mathrm{[M/H]} = 0.04$.
*   **Planeta:** $R_p = 0.917985 \, R_\oplus$, $M_p = 0.6356 \, M_\oplus$ y $T_{\mathrm{eq}} = 255.0$ K.
*   **Geometría Atmosférica:** Malla de presión de 100 capas distribuidas logarítmicamente entre $10^{-10}$ bar y $10.0$ bar. La superficie sólida se define de forma explícita a una presión de corte opaco de $P_{\mathrm{surf}} = 1.0$ bar (`surface=True`), con el radio físico del planeta anclado a esta misma presión ($P_{\mathrm{ref}} = 1.0$ bar).
*   **Perfiles de Entrada:** Se interpolan y cargan las temperaturas y abundancias fotoquímicas calculadas en VULCAN (escenarios `A0`-`A3`) en la malla vertical (`PT_profile="file_read"`, `X_profile="file_read"`).

### Composición y Opacidades Activas en POSEIDON
*   **Gas de fondo:** $\mathrm{N_2}$ actuando como gas inerte de relleno.
*   **Gases absorbentes:** $\mathrm{H_2O}$, $\mathrm{CO_2}$, $\mathrm{CH_4}$, $\mathrm{O_2}$, $\mathrm{O_3}$, $\mathrm{N_2O}$ y $\mathrm{NH_3}$. Es importante notar que, aunque el modelo de red química de VULCAN computa abundancias para más de 80 especies químicas, el forward model de POSEIDON se restringe exclusivamente a cargar estas 7 especies activas por ser los absorbentes clave en el rango espectral seleccionado.
*   **Parámetros Radiativos:** Cobertura de longitudes de onda de $0.5$ a $14.0 \, \mu\text{m}$ a resolución espectral constante de $R = 10,000$. Tratamiento de opacidades por muestreo (`opacity_sampling`) sobre la base de datos `High-T`, la cual fue seleccionada específicamente para este proyecto por contar con las secciones eficaces de absorción detalladas para el amoníaco ($\mathrm{NH_3}$).

---

## 3. Generación de las Plantillas de Ruido Instrumentales (PandExo)

Para definir la dispersión de ruido y la cuadrícula espectral de los instrumentos de JWST, se generan **plantillas espectrales planas de 1 tránsito** utilizando el motor de PandExo (`pandexo.engine.justdoit`). 

### Configuración de la Simulación Base de PandExo
El script [Observation.ipynb](../Transmission_Spectroscopy/notebooks/legacy/Observation.ipynb) define los parámetros de PandExo para simular el límite de ruido instrumental de TRAPPIST-1e:

*   **Configuración Observacional del Sistema:**
    *   Magnitud estelar en banda J ($1.25 \, \mu\text{m}$): $J = 11.354$
    *   Temperatura de estrella Phoenix: $T = 2566$ K, gravedad superficial $\log g = 5.2396$ y metalicidad solar ($0.0$).
    *   Radio estelar nominal: $R_* = 0.121 \, R_\odot$.
    *   Espectro planetario de entrada: Espectro de transmisión plano (`planet.type = "constant"`) con radio planetario $R_p = 0.081 \, R_{\mathrm{Jup}}$ y duración del tránsito de $0.9535$ horas.
    *   Estrategia de baseline observacional: Duración total de la línea de base igual a tres veces la del tránsito ($3.0 \times \text{duración del tránsito}$), con nivel de saturación máximo del detector fijado al $80\%$ y sin piso de ruido instrumental extra (`noise_floor = 0`).

*   **Instrumento 1: JWST NIRSpec Prism (Modo Espectroscópico)**
    *   Subarray: `"sub512"`
    *   Grupos por integración: `ngroup = 6`
    *   Número de tránsitos: $1$
    *   Rango espectral útil conservado: $0.6$ a $5.3 \, \mu\text{m}$.

*   **Instrumento 2: JWST MIRI LRS (Espectroscopía de Baja Resolución)**
    *   Grupos por integración: `ngroup = 175`
    *   Número de tránsitos: $1$
    *   Rango espectral útil conservado: $5.0$ a $12.0 \, \mu\text{m}$.

Las simulaciones de PandExo producen para cada punto instrumental la longitud de onda binada ($wl$), el semiancho del bin ($\Delta wl = 0.5 \times | \nabla wl |$), la profundidad de tránsito y la incertidumbre del flujo espectral ($\sigma_1$). Estos productos planos de 1 tránsito se guardan en:
*   `POSEIDON_output/TRAPPIST-1e/pandexo_nirspec_prism_flat/TRAPPIST-1e_flat_NIRSpec_Prism_1_transits.dat`
*   `POSEIDON_output/TRAPPIST-1e/pandexo_miri_lrs_flat/TRAPPIST-1e_flat_MIRI_LRS_1_transits.dat`

---

## 4. Construcción del Espectro Sintético Observado (POSEIDON + Ruido)

Utilizando los espectros directos de alta resolución (Sección 2) y las plantillas de ruido de PandExo (Sección 3), POSEIDON genera los espectros sintéticos observados mediante la función `generate_syn_data_from_file`:

1.  **Rebinado Instrumental:** El modelo físico en alta resolución ($R=10,000$) se convoluciona y se proyecta en la malla de bines espectrales de PandExo a resolución instrumental ($R = 100$).
2.  **Escalado de Ruido:** La dispersión o error esperado en cada bin para un número de tránsitos $N_{\mathrm{trans}}$ se escala estadísticamente a partir del error de un tránsito de PandExo ($\sigma_1$):
    $$\sigma_{N} = \frac{\sigma_{1}}{\sqrt{N_{\mathrm{trans}}}}$$
3.  **Simulación de Dispersión Gaussiana:** Para generar una simulación observacional realista, se perturban las profundidades de tránsito binadas teóricas añadiendo una realización de ruido aleatorio extraída de una distribución normal centrada en cero con desviación estándar $\sigma_N$ (`Gauss_scatter=True`). Para estudios teóricos limpios, este paso se puede omitir para producir espectros bined puros sin ruido.

### Archivos de la Campaña Espectral Sintética
La campaña genera archivos `.dat` con columnas (`wavelength`, `wavelength_err`, `depth`, `depth_err`) para:
*   **Escenarios:** A0, A1, A2, A3.
*   **Cantidad de tránsitos ($N_{\mathrm{trans}}$):** 5, 10, 20 y 100.
*   **Instrumentos:** NIRSpec Prism y MIRI LRS individuales.
*   **Ruta de almacenamiento:** `POSEIDON_output/TRAPPIST-1e/synthetic_data/base_1transit/`

---

## 5. Referencias

1.  Haqq-Misra, J., Fauchez, T. J., Schwieterman, E. W., & Kopparapu, R. (2022). *Disruption of a Nitrogen Cycle as Evidence of Extraterrestrial Agriculture*. ApJL, 929, L28.
2.  MacDonald, R. J. (2023). *POSEIDON: A Multidimensional Atmospheric Retrieval Code*. JOSS, 8(81), 4873.
3.  Schaphoff, S., et al. (2018). *LPJmL4 – a dynamic global vegetation and agricultural model*. Geoscientific Model Development, 11, 1343-1375.
4.  Batalha, N. E., et al. (2017). *PandExo: A Community Tool for Transiting Exoplanet JWST Science Planning*. PASP, 129, 064501.
