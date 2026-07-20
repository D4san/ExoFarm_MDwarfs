# Informes científicos y notas de análisis de ExoFarm

Esta carpeta conserva informes Markdown derivados de los flujos de modelado,
espectroscopía y retrieval del repositorio. Los documentos se escriben como una
bitácora académica: registran el razonamiento, la procedencia de los datos, los
supuestos, los resultados y las limitaciones necesarias para transformar
análisis exploratorios en evidencia científica auditable y, posteriormente, en
secciones de un artículo.

## Reanudar desde un chat nuevo

1. Leer el [punto de entrada operativo](project_resume.md).
2. Confirmar estado, decisiones y backlog en el
   [tracker del proyecto](project_status_tracker.md).
3. Si la tarea toca la Capa 1 LIFE o los perfiles Tierra--Sol, leer la
   [nota de procedencia N2O](earth_sun_n2o_matrix_provenance_2026-07-20.md)
   antes de interpretar resultados.

Los informes fechados son evidencia, no instrucciones operativas por sí solos.

## Informes

- [Auditoría Científica de Modelos, 2026-07-01](scientific_audit_2026-07-01.md)
  Auditoría histórica que detectó la inconsistencia N2O, discrepancias de
  radio planetario/estelar y advertencias sobre el 'model mismatch'. La
  corrección está en los BC activos; la procedencia de perfiles ya guardados se
  aclara en la nota N2O de 2026-07-20.
- [Construcción de los perfiles fotoquímicos de ExoFarm con VULCAN](photochemical_profiles_methodology.md)
  Descripción narrativa y auditable de la red química, malla vertical, flujos
  A0-A3, espectros estelares, geometría de iluminación y bloqueo por marea.
- [Procedencia de la matriz Tierra--Sol de N2O para LIFE, 2026-07-20](earth_sun_n2o_matrix_provenance_2026-07-20.md)
  Separa los BC N2O vigentes del conjunto de perfiles Tierra--Sol guardado el
  2026-06-15 y define qué uso LIFE queda permitido antes de un rerun.
- [Auditoría de reproducción de perfiles verticales VULCAN, 2026-06-15](vulcan_profile_reproduction_2026-06-15.md)
  Registra la corrección de los parámetros físicos de TRAPPIST-1e, la condición
  de borde duplicada de H2SO4 y la comparación cuantitativa de los ocho perfiles.
- [Distinguibilidad posterior entre A0 y A3 para campañas equivalentes](trappist1e_a0_a3_diagonal_posterior_distinguishability.md)  
  Interpretación metodológica y científica de tres diagnósticos que comparan
  las abundancias recuperadas de `N2O` y `NH3` en TRAPPIST-1e.
- [Generación histórica de espectros sintéticos y simulación de ruido con PandExo](transmission_spectroscopy_synthetic_spectra_generation.md)
  Detalles fechados del modelo directo nativo de POSEIDON y PandExo; no define
  la campaña actual ni se reutiliza para LIFE. Consultar el tracker antes de
  ejecutar transmisión/JWST.
- [Campaña histórica de retrievals atmosféricos y configuración del fiteador (MultiNest)](transmission_spectroscopy_retrieval_campaign.md)
  Registro de la grilla legacy de 42 corridas y `surface=False`; no define la
  campaña actual de 18 corridas ni el modelo vigente con `surface=True`.
- [Inventario de espectroscopia de transmisión, 2026-06-16](transmission_spectroscopy_inventory_2026-06-16.md)
  Diagnóstico read-only de `Transmission_Spectroscopy/`: rutas activas,
  productos legacy/ambiguos, scripts de plots, ubicación de figuras y entorno
  POSEIDON en Ubuntu/WSL.
- [Picos de contribución molecular neta en TRAPPIST-1e, 2026-06-17](trappist1e_net_molecular_contribution_peaks_2026-06-17.md)
  Resume el diagnóstico contrafactual donde `N2O`, `NH3` y `H2O` se resetean
  al perfil `A0` dentro de `A1-A3`, y exporta los tres picos residuales más
  fuertes por molécula y escenario. Registra además la trazabilidad de la
  figura oficial `trappist1e_pure_a0_molecular_residuals_v2`.
- [Promedio columnar de mixing ratio para perfiles fotoquímicos, 2026-06-17](photochemical_column_averaged_mixing_ratio_2026-06-17.md)
  Registra la definición, discretización e interpretación del diagnóstico
  `column-averaged mixing ratio` usado en la tercera columna del resumen
  fotoquímico A0-A3.
- [Estructura del repositorio y ubicaciones canónicas](repository_structure.md)
  Define dónde deben vivir configuraciones, productos y reportes, y clasifica
  las rutas legacy de la raíz.
- [Workflow de revisión, organización y limpieza del repositorio](repository_cleanup_workflow.md)
  Procedimiento liviano para auditar estructura, clasificar evidencia, borrar
  residuos temporales solo con aprobación y registrar decisiones duraderas.
- [Seguimiento y Estado de Gestión del Proyecto](project_status_tracker.md)
  Centraliza el estado operativo de las Etapas 0-3, versiones de dependencias, decisiones de diseño tomadas y backlog de tareas técnicas. Debe leerse después del punto de entrada operativo.
- [Plan de la Etapa III: emisión térmica, LIFE y LIFEsimMC](life_lifesim_stage_iii_plan.md)
  Define la rama paralela de emisión, el contrato POSEIDON--LIFEsimMC,
  diagnósticos de señal/SNR y las puertas previas a retrievals.
- [Plan operativo de dos capas LIFE, 2026-07-20](life_stage_iii_two_layer_workplan_2026-07-20.md)
  Registra la próxima secuencia: benchmark `life_earth_sun_10pc` con perfiles
  VULCAN existentes y, después, `life_proxima_b_earthlike` desde SED MUSCLES,
  conversión a VULCAN y nueva fotoquímica A0--A3.
- [Selección del objetivo de referencia LIFE, 2026-07-20](life_target_selection_2026-07-20.md)
  Justifica Tierra--Sol a 10 pc como benchmark, Proxima como extensión M
  prioritaria y los límites que impiden presentar el segundo caso como una
  atmósfera medida de Proxima b.

## Convención documental

Cada informe debe identificar:

1. la pregunta científica;
2. los scripts, notebooks y productos utilizados;
3. el cálculo y sus supuestos;
4. el resultado directo y su interpretación;
5. aquello que todavía no puede concluirse;
6. el siguiente análisis necesario;
7. las referencias que justifican las decisiones.

El estado resumido de las campañas y las decisiones de limpieza se documentan
en [`../experiments/README.md`](../experiments/README.md) y
[`../experiments/cleanup.md`](../experiments/cleanup.md).
