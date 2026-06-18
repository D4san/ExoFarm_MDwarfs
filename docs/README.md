# Informes científicos y notas de análisis de ExoFarm

Esta carpeta conserva informes Markdown derivados de los flujos de modelado,
espectroscopía y retrieval del repositorio. Los documentos se escriben como una
bitácora académica: registran el razonamiento, la procedencia de los datos, los
supuestos, los resultados y las limitaciones necesarias para transformar
análisis exploratorios en evidencia científica auditable y, posteriormente, en
secciones de un artículo.

## Informes

- [Construcción de los perfiles fotoquímicos de ExoFarm con VULCAN](photochemical_profiles_methodology.md)
  Descripción narrativa y auditable de la red química, malla vertical, flujos
  A0-A3, espectros estelares, geometría de iluminación y bloqueo por marea.
- [Auditoría de reproducción de perfiles verticales VULCAN, 2026-06-15](vulcan_profile_reproduction_2026-06-15.md)
  Registra la corrección de los parámetros físicos de TRAPPIST-1e, la condición
  de borde duplicada de H2SO4 y la comparación cuantitativa de los ocho perfiles.
- [Distinguibilidad posterior entre A0 y A3 para campañas equivalentes](trappist1e_a0_a3_diagonal_posterior_distinguishability.md)  
  Interpretación metodológica y científica de tres diagnósticos que comparan
  las abundancias recuperadas de `N2O` y `NH3` en TRAPPIST-1e.
- [Generación de espectros sintéticos y simulación de ruido con PandExo](transmission_spectroscopy_synthetic_spectra_generation.md)  
  Detalles del modelo directo nativo de POSEIDON, los parámetros de PandExo para
  construir las plantillas de 1 tránsito y la proyección de ruido instrumental.
- [Campaña de retrievals atmosféricos y configuración del fiteador (MultiNest)](transmission_spectroscopy_retrieval_campaign.md)  
  Descripción del modelo de retrieval isotérmico/isoquímico, la justificación física
  de omitir la superficie sólida y la grilla de las 42 corridas de inversión.
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
