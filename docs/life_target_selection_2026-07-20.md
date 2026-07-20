# Selección del objetivo de referencia para la Etapa III LIFE

**Fecha de decisión:** 2026-07-20
**Estado:** decisión de alcance; no se han ejecutado forwards de emisión,
simulaciones LIFE ni retrievals. Para reanudar, leer
[`project_resume.md`](project_resume.md) y el
[`project_status_tracker.md`](project_status_tracker.md).

## Decisión de proyecto

La primera preparación de la Etapa III usará el benchmark sintético
`life_earth_sun_10pc`: un análogo Tierra--Sol (G2V) observado a 10 pc, con los
perfiles fotoquímicos Tierra--Sol A0--A3 ya aceptados en este repositorio. Esos
perfiles A2/A3 son el conjunto congelado `earth_20260615_pre_n2o_correction`,
por lo que su uso inicial es validar interfaz y no declarar la matriz N2O
vigente sin una decisión/re-run. La distancia de 10 pc describe la geometría
observador--sistema de la escena LIFE; no cambia la fotoquímica VULCAN
Tierra--Sol ni pretende representar la Tierra real como un objetivo observable
desde 10 pc. La evidencia está en la
[nota de procedencia](earth_sun_n2o_matrix_provenance_2026-07-20.md).

El alcance inicial es deliberadamente secuencial:

1. Auditar entorno/interfaz y congelar el manifiesto para A0--A3 del caso
   `life_earth_sun_10pc`, con el rótulo pre-corrección; el primer forward sin
   ruido valida unidades, no la matriz científica vigente.
2. Solo después de validar la interfaz POSEIDON--LIFEsimMC, el tratamiento de
   covarianza y la decisión de procedencia (rerun o uso histórico), proponer
   retrievals piloto A0/A3 para ese mismo benchmark.
3. Preparar como segunda capa `life_proxima_b_earthlike`: una SED MUSCLES
   documentada debe convertirse a flujo superficial VULCAN y generar nuevos
   perfiles Proxima A0--A3 antes de iniciar emisión/LIFE.
4. Mantener el análogo TRAPPIST-1-like a 5 pc, Teegarden's Star b y
   TRAPPIST-1e real como controles/alternativas posteriores, no como campañas
   aprobadas por analogía.

Esta es una **decisión de alcance del proyecto**, no un resultado de
detectabilidad. Las configuraciones instrumentales, los tiempos de integración
y las realizaciones de ruido siguen pendientes de congelación.

## Evidencia que motiva la elección

### Hechos derivados de fuentes

- El estudio LIFE III usa un gemelo terrestre alrededor de una estrella G2V a
  10 pc como caso de referencia para espectros MIR y retrievals. Sus requisitos
  de diseño son una referencia útil, pero su resultado para la Tierra nominal
  no demuestra detectabilidad de `N2O` agrícola.
  [Konrad et al. (2022)](https://doi.org/10.1051/0004-6361/202141964).
- El estudio de LIFEsimMC/PHRINGE sobre errores correlacionados adopta
  explícitamente una Tierra gemela alrededor de un Sol gemelo a 10 pc. Muestra
  que el whitening basado en covarianza importa para interpretar métricas de
  detección y para recuperar propiedades planetarias; por tanto respalda el
  mismo benchmark para la ruta instrumental prevista aquí.
  [Huber et al. (2025)](https://doi.org/10.3847/1538-3881/adfb6b).
- LIFE XII contiene el caso distinto de una Tierra sintética alrededor de una
  estrella tipo TRAPPIST-1 a 5 pc. Es un precedente para una extensión de M
  enana y para la relevancia MIR de `N2O`, pero no es TRAPPIST-1e real ni usa
  LIFEsimMC.
  [Angerhausen et al. (2024)](https://doi.org/10.3847/1538-3881/ad1f4b).
- LIFE X evalúa objetivos conocidos con una arquitectura clásica de referencia
  y concluye que TRAPPIST-1e no alcanza su criterio de S/N = 7 en 100 h para
  cuatro colectores de 2 m y baseline de nulación de 10--100 m. El resultado
  hace que TRAPPIST-1e sea una pregunta de arquitectura, no el control limpio
  para una primera campaña molecular ExoFarm.
  [Carrión-González et al. (2023)](https://doi.org/10.1051/0004-6361/202347027).
- MAST distribuye para Proxima Centauri (GJ 551) una SED MUSCLES v22 creada con
  metodología consistente con el resto de la familia MUSCLES. Incluye productos
  pancromáticos y componentes UV/X-ray/EUV/fotosféricos aptos para construir un
  insumo fotoquímico trazable, siempre que se conserven sus notas de reducción y
  se valide la normalización de flujo superficial.
  [MAST MUSCLES](https://archive.stsci.edu/hlsp/muscles).

### Interpretación y decisión de ExoFarm

El caso Tierra--Sol a 10 pc separa el efecto que interesa medir --la
perturbación A0--A3 de `N2O` y `NH3`-- de cambios simultáneos en espectro UV
estelar, radio/masa planetaria, excentricidad, separación angular y atmósfera
desconocida. También reutiliza cuatro perfiles Tierra--Sol que alcanzaron el
estado estacionario guardado. Por ello es el benchmark metodológico más
auditable para introducir LIFEsimMC sin convertir la primera campaña en una
encuesta de objetivos. Su A2/A3 de junio se conservan explícitamente como
benchmark de interfaz hasta resolver la procedencia de N2O, no como sustituto
silencioso de los BC actuales.

La afirmación científica resultante deberá limitarse a un **análogo
Tierra--Sol cercano bajo una configuración LIFE declarada**. No autoriza una
generalización automática a M enanas, planetas reales concretos ni a la
detectabilidad universal de tecnofirmas agrícolas.

## ¿Existe un planeta real que lo sustituya?

Hay planetas reales interesantes para LIFE, pero ninguno es un reemplazo
limpio del experimento controlado anterior. LIFE X identifica decenas de
planetas de zona habitable potencialmente detectables con su configuración
clásica de referencia; eso demuestra que una extensión basada en un objetivo
real es plausible, no que uno de ellos preserve las hipótesis de ExoFarm.

| Opción | Qué aporta | Papel de proyecto |
| --- | --- | --- |
| Tierra--Sol a 10 pc | Benchmark sintético publicado; perfiles VULCAN Tierra--Sol A0--A3 aceptados; control experimental directo. | **Capa 1.** Benchmark de interfaz `earth_20260615_pre_n2o_correction`; no es un planeta conocido ni la matriz N2O vigente hasta decisión/rerun. |
| Proxima b / `life_proxima_b_earthlike` | Planeta cercano de masa mínima terrestre y una SED MUSCLES pública, pancromática y trazable. LIFE X lo considera un objetivo conocido favorable en su arquitectura de referencia. | **Capa 2.** No sustituye el benchmark: primero requiere SED→VULCAN A0--A3 y se interpreta como análogo terrestre bajo entorno Proxima, no como atmósfera medida. |
| Teegarden's Star b | Caso real M muy interesante para LIFE y de baja masa. | Alternativa posterior: no tiene aún en el repositorio una SED integrada estilo MUSCLES ni perfiles fotoquímicos propios. |
| TRAPPIST-1e real | Conecta con la Etapa II existente. | Control futuro de arquitectura/geometría; no aísla la química agrícola ni es el caso molecular principal. |

La selección de Proxima no elimina las preguntas de Teegarden o TRAPPIST-1e:
prioriza la intersección entre geometría LIFE, planeta real cercano y un insumo
estelar UV--IR ya auditable. La actividad de Proxima exige que el baseline se
etiquete como quiescente/archival y que una sensibilidad flare/XUV sea una
variante explícita, no una extrapolación silenciosa.

Un candidato reciente alrededor de una estrella G cercana tampoco resuelve por
sí solo el problema: el planeta exterior confirmado de HD 20794 tiene una masa
mínima de aproximadamente 5.8 masas terrestres y una órbita excéntrica
(`e` aproximadamente 0.45), por lo que podría ser una super-Tierra o un
mini-Neptuno y plantea una pregunta climática distinta. Se conserva como
contexto de selección futura, no como insumo de esta campaña.
[Nari et al. (2025)](https://doi.org/10.1051/0004-6361/202451769).

## Consecuencia práctica

La primera implementación sigue sin necesitar un planeta real: debe auditar el entorno, congelar la escena/manifiesto `life_earth_sun_10pc`, validar la
cadena POSEIDON--LIFEsimMC y acotar su interpretación al benchmark
pre-corrección. La siguiente capa ya está definida, pero queda bloqueada por
nueva fotoquímica: `life_proxima_b_earthlike` empieza con la SED MUSCLES, su
conversión de unidades/flujo y VULCAN A0--A3 con PT/Kzz terrestre controlado.
Solo después reproduce la cadena de emisión, LIFE, SNR y diseño de retrievals.

El detalle operacional, las rutas y las puertas entre ambas capas están en
[`life_stage_iii_two_layer_workplan_2026-07-20.md`](life_stage_iii_two_layer_workplan_2026-07-20.md).

## Referencias

- Angerhausen, D., et al. (2024). *Large Interferometer For Exoplanets (LIFE).
  XII. The Detectability of Capstone Biosignatures in the Mid-infrared--Sniffing
  Exoplanetary Laughing Gas and Methylated Halogens*. **The Astronomical
  Journal, 167**, 128. DOI:
  [10.3847/1538-3881/ad1f4b](https://doi.org/10.3847/1538-3881/ad1f4b). [arXiv:2401.08492](https://arxiv.org/abs/2401.08492)
- Boukrouche, R., & Janson, M. (2025). *Disentangling the hemispheres of
  Teegarden's Star b with LIFE*. [arXiv:2512.19231](https://arxiv.org/abs/2512.19231).
- Carrión-González, Ó., et al. (2023). *Large Interferometer For Exoplanets
  (LIFE). X. Detectability of currently known exoplanets and synergies with
  future IR/O/UV reflected-starlight imaging missions*. **Astronomy &
  Astrophysics, 678**, A96. DOI:
  [10.1051/0004-6361/202347027](https://doi.org/10.1051/0004-6361/202347027). [arXiv:2308.09646](https://arxiv.org/abs/2308.09646)
- Huber, P. A., et al. (2025). *Robust Data Interpretation for Perturbed
  Nulling Interferometers via Proper Handling of Correlated Errors*. **The
  Astronomical Journal, 170**, 227. DOI:
  [10.3847/1538-3881/adfb6b](https://doi.org/10.3847/1538-3881/adfb6b). [arXiv:2508.15756](https://arxiv.org/abs/2508.15756)
- MAST MUSCLES. *Measurements of the Ultraviolet Spectral Characteristics of
  Low-mass Exoplanetary Systems*, HLSP DOI:
  [10.17909/T9DG6F](https://doi.org/10.17909/T9DG6F). Proxima Centauri is the
  GJ 551 v22 release; use its reduction notes with the downloaded product.
- Konrad, B. S., et al. (2022). *Large Interferometer For Exoplanets (LIFE).
  III. Spectral resolution, wavelength range, and sensitivity requirements
  based on atmospheric retrieval analyses of an exo-Earth*. **Astronomy &
  Astrophysics, 664**, A23. DOI:
  [10.1051/0004-6361/202141964](https://doi.org/10.1051/0004-6361/202141964). [arXiv:2112.02054](https://arxiv.org/abs/2112.02054)
- Nari, N., et al. (2025). *Revisiting the multi-planetary system of the nearby
  star HD 20794: Confirmation of a low-mass planet in the habitable zone of a
  nearby G-dwarf*. **Astronomy & Astrophysics, 693**, A297. DOI:
  [10.1051/0004-6361/202451769](https://doi.org/10.1051/0004-6361/202451769). [arXiv:2501.17092](https://arxiv.org/abs/2501.17092)
