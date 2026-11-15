# Productos finales de la Etapa III

## Referencia vigente LIFE Proxima A1/A3 (2026-10-29)

El [informe integrado](../../docs/life_proxima_a1_a3_retrievals_analisis_integrado_2026-10-29.md) es la fuente numérica y narrativa de la serie corregida de 1/10/100 h. Las [tablas reproducibles](tables/life_proxima_a1_a3_integrated_20261029/) y el [atlas oficial](figures/retrieval_A1_A3_1_10_100h_official_posteriors_N2O_NH3_first_no_PT_proxima_20261028.png) forman el conjunto vigente; 1000 h se identifica como exploratorio. Los productos enumerados más abajo se conservan como bitácora o sensibilidad histórica y no se usan como tablas vigentes de esta serie.

## Archivo y bitácora de productos anteriores

## Actualización A3–100 h corregida (2026-10-20)

El [informe de actualización](../../docs/life_proxima_a3_100h_corrected_results_update_2026-10-20.md) contiene la interpretación y sus límites. Los siguientes productos sustituyen las filas A3–100 h de N2O/NH3 y regiones A1 en tablas vigentes con fuente/operador por fila; preservan los CSV históricos. Las demás exposiciones mantienen su versión histórica. Los K son nominales, pendientes de validar el prior efectivo. Los contrastes A0 fijos de 100 h conservan su versión histórica separada.

- [Evidencia molecular histórica/corregida](tables/life_proxima_a3_100h_corrected_2026-10-20_molecular_evidence.csv).
- [Regiones posteriores marginales A0/A1/A3](tables/life_proxima_a3_100h_corrected_2026-10-20_posterior_regions.csv).
- [Regiones conjuntas A0/A1/A3](tables/life_proxima_a3_100h_corrected_2026-10-20_joint_regions.csv).
- [Comparación de los 15 parámetros declarados](tables/life_proxima_a3_100h_corrected_2026-10-20_parameter_comparison.csv).
- [Matriz vigente N2O/NH3, con operador por fila](tables/life_proxima_a3_100h_corrected_2026-10-20_current_nitrogen_loo.csv).
- [Regiones A1 vigentes, con operador por fila](tables/life_proxima_a3_100h_corrected_2026-10-20_current_a1_regions.csv).

## Enriquecimiento posterior respecto a A0 efectiva (2026-10-10)

[CSV marginal: 12 filas](tables/life_proxima_a0_enrichment_posterior_2026-10-10.csv),
[CSV conjunto: seis filas](tables/life_proxima_a0_enrichment_joint_2026-10-10.csv)
y [controles y procedencia](tables/life_proxima_a0_enrichment_posterior_2026-10-10.validation.json).
Calculados desde los seis retrievals completos oficiales, con referencia
VULCAN congelada. Son probabilidades e intervalos posteriores condicionados;
no asignan probabilidad de agricultura ni nuevos sigma de detección.
[Procedimiento, interpretación y próximos contrastes A0 fijos](../../docs/life_proxima_a0_enrichment_methodology_2026-10-10.md).
Tres hipótesis **solo A3-100 h** terminadas con exit 0. La tabla de evidencia
está aceptada con salvedad explícita por `NaN` en desviaciones derivadas de
parámetros fijos; productos primarios/evidencias PASS, originales preservados
y momentos auxiliares estables. Los otros 15
modelos candidatos no se ejecutan.
[CSV final](tables/life_proxima_a0_lnB_sigma_lin_2026-10-11.csv),
[JSON aceptado](tables/life_proxima_a0_lnB_sigma_lin_2026-10-11.json)
y [auditoría con diagnóstico](../../docs/life_proxima_a3_100h_a0_fixed_audit_2026-10-11.md).
La [síntesis de las capas](../../docs/life_proxima_exofarm_retrieval_layers_synthesis_2026-10-11.md)
explica la conclusión condicionada ExoFarm/LIFE. Los CSV/JSON con sufijo
`_provisional` se preservan como historial, con cifras idénticas.

## Tabla de evidencia molecular LIFE Proxima (2026-10-10)

[CSV: ln B ± error numérico y sigma calibrado](tables/life_proxima_loo_lnB_sigma_lin_2026-10-10.csv),
36 comparaciones A1/A3 × 1/10/100 h × seis especies; 27 sigma calibrados y
nueve `N/A`. Adopta la calibración bilateral citada por Lin et al. (2021),
con regla `N/A` para `ln B ≤ 0`. [Método, fuentes y tabla legible](../../docs/life_proxima_loo_sigma_lin_convention_2026-10-10.md);
[validación de exportación](tables/life_proxima_loo_lnB_sigma_lin_2026-10-10.validation.json).
La auditoría original y todos los retrievals permanecen en su carpeta de campaña.

Esta carpeta recibirá únicamente tablas o figuras promovidas tras revisión.
Los productos de trabajo permanecen bajo `outputs/<campaign-id>/` con sus
manifiestos y trazabilidad completa.

> **Reanudación:** antes de promover una figura, comprobar en la [guía de reanudación](../../docs/project_resume.md) y el [tracker](../../docs/project_status_tracker.md) que la puerta de campaña correspondiente está aprobada.

## Figuras oficiales actuales

- `emission_molecular_residuals_proxima.png`
- `emission_molecular_residuals_proxima.pdf`

Figura conjunta de emisión térmica y señales moleculares para
`life_proxima_b_earthlike_v1`. La fuente reproducible permanece en
`outputs/life_proxima_b_earthlike_v1/plots/`; la promoción no cambia datos,
unidades ni interpretación científica.

## Figura oficial de SNR integrado

- `life_classic_snr_comparison_proxima.png`
- `life_classic_snr_comparison_proxima.pdf`
- `life_classic_snr_integrated_proxima.csv`
- `life_classic_snr_integrated_proxima.png`
- `life_classic_snr_integrated_proxima.pdf`

Diagnóstico integrado sobre los 31 bins de la rejilla LIFE clásica para
`N2O` y `NH3` en Proxima. El panel superior muestra las dos plantillas
moleculares por escenario y tiempo de integración; el inferior proyecta A3 y
marca las horas requeridas para S/N=3 y S/N=5. La figura mantiene el carácter
diagnóstico del S/N clásico y no constituye una afirmación de detección.

Los nombres canónicos `life_classic_snr_comparison_proxima.{png,pdf}` apuntan
ahora a esta versión integrada para mantener la ruta de la figura final. La
misma figura se conserva con el nombre explícito
`life_classic_snr_integrated_proxima.{png,pdf}`. La versión anterior de S/N de
picos por rasgo espectral se preserva como
`life_classic_snr_peak_comparison_proxima.{png,pdf}` y queda marcada como
legacy.

## Atlas oficial LIFE A1/A3 — N₂O/NH₃ primero, sin panel P–T (2026-10-28)

- retrieval_A1_A3_1_10_100h_official_posteriors_N2O_NH3_first_no_PT_proxima_20261028.png
- retrieval_A1_A3_1_10_100h_official_posteriors_N2O_NH3_first_no_PT_proxima_20261028.pdf
- retrieval_A1_A3_1_10_100h_official_posteriors_N2O_NH3_first_no_PT_proxima_20261028.svg
- retrieval_A1_A3_1_10_100h_official_posteriors_N2O_NH3_first_no_PT_proxima_20261028.provenance.json

Tres filas para 1/10/100 h y seis columnas en el orden N₂O, NH₃, H₂O, CO₂, CH₄, O₃. Se mantienen los perfiles verticales moleculares; no se muestra el perfil P–T ni una nota de estado. Los seis retrievals completos pasaron auditoría independiente y los hashes de las tres exportaciones coinciden con el sidecar. La edición inicial del 26-oct y la edición intermedia del 28-oct con P–T quedan preservadas como versiones históricas. [Informe y reproducción](../../docs/life_proxima_corrected_binning_full_posteriors_plot_2026-10-28.md).


## Atlas anterior de retrievals Proxima b LIFE — histórico

- `retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima.png`
- `retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima.pdf`
- `retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima.svg`

Diseño V2 previo, con **A3–100 h actualizado el 2026-10-20**: seis especies
moleculares más P--T, posteriores normalizadas, perfiles VULCAN y distancias
descriptivas respecto a A0 efectiva. Se sustituyen muestras, `log_X` y P–T
del nuevo completo aceptado; los otros cinco casos mantienen sus fuentes
históricas. PNG/PDF/SVG se promovieron tras revisión visual y comparación de
hashes. El [JSON por caso](figures/retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima.provenance.json)
registra las entradas y etiquetas. La figura anterior se preserva en
`outputs/life_proxima_b_earthlike_v1/plots/history/official_before_A3_100h_update_20261020/`.
Las variantes V1/V3 previas al 20-oct conservan sus fuentes históricas.
[Registro histórico de actualización parcial](../../docs/life_proxima_official_plot_and_draft_update_2026-10-20.md). El atlas vigente es la edición del 28-oct con N₂O/NH₃ primero y sin panel P–T, descrita arriba.
