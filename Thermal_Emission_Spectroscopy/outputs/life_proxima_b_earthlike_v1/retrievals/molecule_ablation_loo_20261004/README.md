# Comparación LIFE Proxima con/sin moléculas: campaña LOO, 2026-10-04

**Estado final, corte 2026-10-10:** `campaign_state.json` registra
`campaign_status=completed`, 36/36 corridas con `return_code=0`, preflight
36/36 `PASS` y 14 parámetros por ablación. Las 36 carpetas archivadas pasaron
la auditoría de productos y las seis evidencias de los modelos completos
concuerdan con sus resultados POSEIDON. No hay jobs activos o pendientes ni
procesos MPI de la campaña en WSL. El estado confirma que se reutilizaron los
seis retrievals completos y `canonical_8of8_modified=false`.

Resultados auditados: [`loo_results_validated_20261010.csv`](loo_results_validated_20261010.csv),
[`validation_report_20261010.json`](validation_report_20261010.json) y la
[figura final](../../../../final_products/figures/life_proxima_molecular_ablation_loo_lnB_2026-10-10.svg).
El [informe científico](../../../../../docs/life_proxima_molecular_ablation_loo_2026-10-04.md)
contiene la tabla completa e interpretación. `campaign_state.json` y
`manifest.csv` siguen siendo la fuente de trazabilidad; no relanzar ni duplicar
ninguna celda ya completada.

## Pregunta y alcance

Esta campaña cuantifica cuánto favorece cada espectro LIFE simulado un modelo
que permite una molécula concreta frente a otro que la omite. La motivación
es el análisis de Lin & Kaltenegger: contrastar retrievals completos con
modelos en los que se excluyen especies y derivar la significancia a partir de
la evidencia bayesiana. Trasladamos esa lógica a la serie focal LIFE Proxima
A1/A3 sin multiplicar retrievals para buscar post hoc qué realización produce
la respuesta más atractiva.

La matriz contiene 36 modelos sin una molécula:

\[
2\ \text{escenarios (A1,A3)}
\times 3\ \text{exposiciones (1,10,100 h)}
\times 6\ \text{especies (H₂O, CO₂, CH₄, O₃, N₂O, NH₃)}.
\]

Cada uno se contrasta con el retrieval completo oficial del mismo escenario,
tiempo y archivo de datos. Los seis retrievals completos ya existen; no se
repiten. O₂ permanece activo en todos los modelos y no forma parte de las seis
ablaciones porque la pregunta focal considera las seis especies del atlas.
La matriz histórica 8/8, los datasets y los productos completos se preservan.

## Definición del contraste

Para una misma observación \(D_{s,t}\), con escenario \(s\), exposición \(t\)
y realización de ruido fija, calcularemos

\[
\Delta\ln Z_X(D_{s,t}) =
\ln Z_{\rm completo}(D_{s,t}) -
\ln Z_{\rm sin\ }X(D_{s,t}).
\]

Un valor positivo favorece el modelo que incluye \(X\); el factor de Bayes
condicional es \(B_{\rm completo,sin\,X}=\exp(\Delta\ln Z_X)\). Se reportarán
las incertidumbres numéricas de ambas evidencias. No se compararán evidencias
de datasets distintos —por ejemplo, 1 h contra 100 h, A1 contra A3 o
realizaciones diferentes— como factores de Bayes. Las distancias \(z\) del
atlas frente a A0 efectiva son descriptivas y no sustituyen este contraste.

“Sin X” significa retirar la opacidad de \(X\) y su parámetro de abundancia,
manteniendo los restantes gases y parámetros. El modelo completo recupera
15 parámetros; cada ablación debe recuperar 14. Los parámetros compartidos,
sus priors, el PT Madhu, la superficie y la likelihood permanecen iguales.
La comparación es condicional al modelo y a esos priors; no marginaliza
incertidumbres de perfil químico vertical ni ruido correlacionado.

## Inputs oficiales congelados

Los hashes se verifican antes del preflight. Cada pareja completo/ablacionado
usa exactamente el mismo archivo de 31 bins; así, el contraste no mezcla el
efecto de retirar una especie con un cambio de realización de ruido.

| Caso | Dataset | Semilla registrada | SHA-256 |
| --- | --- | ---: | --- |
| A1, 1 h | LIFE_proxima_A1_1h_O2_fixedBlack1bar_noiseRepeat2.dat | 2125532119 | 93fb65765101950063d5aa9a3dafae4df38273292cb0e3349e94b8a34516cfcc |
| A3, 1 h | LIFE_proxima_A3_1h_O2_fixedBlack1bar_official.dat | 1376328125 | a3043e5de76a834983949e6eca12636ea4de174ebdb2db0853155282c100dee2 |
| A1, 10 h | LIFE_proxima_A1_10h.dat | 1099171982 | ed39ae6dc5b8ff0d5c8aca3d126a2945343a289be30f3b8d9e8e72c434ee9b8f |
| A3, 10 h | LIFE_proxima_A3_10h.dat | 1469409748 | 46a026504b9b9521fa29407a501169b9d3cfc433de40a91b8ade86d7767abb5b |
| A1, 100 h | LIFE_proxima_A1_100h_O2_fixedBlack1bar_noxtol_audit.dat | 460512527 | d66c886238a2916312c645589be8601828fbf0a7cd2f02a383ef1d6a3454b5e3 |
| A3, 100 h | LIFE_proxima_A3_100h.dat | 129315834 | 78662546181a5b74391a14b7b73ae80d879200a74db6a4bc5338e3ce7eee4705 |

La entrada A1 de 1 h es la realización independiente oficial NoiseRepeat2,
promovida tras revisar sus posteriores; la semilla 368516754 se conserva como
sensibilidad y no se sustituye aquí. Las realizaciones de 100 h son
independientes por diseño, pero cada ablación se empareja con su retrieval
completo sobre la misma realización.

## Retrieval setup

Todas las ablaciones usan el lanzador existente
[run_life_retrieval.py](../Thermal_Emission_Spectroscopy/scripts/run_life_retrieval.py)
con POSEIDON, escenario A1/A3, exposición 1/10/100 h, una especie excluida,
O₂ incluido, perfil isochem, superficie negra explícita fija a 1 bar,
error_inflation desactivada, R=10000, N_live=800, archivo de datos congelado,
etiqueta de salida única y directorio absoluto aislado.

POSEIDON y MPICH proceden del entorno conda POSEIDON en Ubuntu/WSL. Cada
MultiNest usa seis ranks MPI y un hilo por rank para las bibliotecas BLAS /
OpenMP. Se fijan POSEIDON_input_data y PYSYN_CDBS para las opacidades y rejillas
estelares. Se mantiene una malla de presión de 100 capas, perfil térmico Madhu
flexible, y abundancias isochem para las especies restantes. Los priors
compartidos conservan la configuración de los retrievals completos:
log10(VMR) uniforme en [-12,-1] y para O₂ [-6, log10(0.5)]. Los priors de PT,
radio y superficie también permanecen iguales; log_P_surf tiene prior de ancho
cero en 0, correspondiente a 1 bar. Los seis resultados completos se indican
por nombre de archivo en el manifiesto de campaña.

## Paralelismo y runtime

Ubuntu/WSL expone 16 CPU lógicas y 31 GiB de RAM. La cola ejecutará como máximo
dos retrievals simultáneos, cada uno con seis ranks (12 ranks totales), dejando
cuatro CPU lógicas para WSL, el sistema y la E/S. Elegimos este esquema frente
a asignar 12 o 16 ranks a un único retrieval porque el proyecto ya completó
dos retrievals Proxima de 240 h concurrentes en MPI6 y aún no hay benchmark
que muestre escalado eficiente de MultiNest con más ranks para una posterior.
Lanzar los 36 a la vez saturaría CPU y E/S.

El orden prioriza N₂O/NH₃ a 100 h, luego 10 h y 1 h; después CH₄, O₃, CO₂ y
H₂O. Como presupuesto preliminar, estimamos aproximadamente 5–10 días: los
fits MPI6 previos van de varias horas para ajustes cortos a unas 19 h para
fits completos de 240 h. Extrapolando 5–7 h para celdas cortas y hasta 10–19 h
para las de 100 h, las 36 corridas con dos concurrentes requieren del orden de
5–8 días efectivos, más margen por variación/convergencia. Es una inferencia,
no una fecha de entrega; la primera pareja de 100 h calibrará el pronóstico.

## Organización durable y recuperación

El supervisor reproducible es
[run_proxima_molecule_ablation_campaign.py](../Thermal_Emission_Spectroscopy/scripts/run_proxima_molecule_ablation_campaign.py).
Su raíz es
Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/molecule_ablation_loo_20261004/.
Contiene:

- campaign_state.json y manifest.csv: 36 celdas, hashes, preflight, estado,
  PID, código de salida, marcas de tiempo, duración y rutas;
- configs/: comando y configuración efectiva de cada run;
- preflight/: 36 logs setup-only con parámetros y especie excluida;
- pids/ y logs/: PID y log durable por corrida;
- runs/: copias completas de scratch solo después de exit 0.

MultiNest escribe en el filesystem Linux WSL:
/home/dasan/exofarm_proxima_molecule_loo_20261004/runs/<run_id>/. El supervisor
limita la concurrencia a dos, evita sobrescribir, detiene la cola ante la
primera falla y no reintenta automáticamente. El scratch y el log de una falla
se conservan para diagnóstico. Los seis modelos completos, los archivos LIFE
originales y la matriz 8/8 son entradas de solo lectura.

Desde la raíz del repositorio, la vista resumida de estado es:

    python Thermal_Emission_Spectroscopy/scripts/run_proxima_molecule_ablation_campaign.py --status-only

El README de la carpeta de campaña, el estado JSON, manifiesto, configuración,
log y PID por corrida, junto con este informe, son el handoff entre sesiones.
Si WSL o el supervisor se detienen, primero se inspeccionan estado, procesos y
logs; el supervisor rechaza inicializar una segunda campaña en la misma raíz.
No relanzar celdas activas ni inferir éxito por tiempo transcurrido.

## Validación e interpretación

Antes del muestreo, los 36 casos deben pasar setup-only: hash del input,
resultado completo correspondiente, datos con 31 bins, ausencia de la especie
solicitada en param_names, exactamente 14 parámetros y configuración común.
Al cerrar cada proceso se requiere exit code 0 y se validan muestras, espectro
recuperado, P–T, log-X, archivos MultiNest y finitud numérica. Una corrida
fallida queda preservada y bloquea el avance automático. Al completar la
matriz, se calcula ΔlnZ_X y la incertidumbre numérica combinada usando solo la
pareja de evidencias del mismo dataset; se reportan también ajuste y posterior.

### Límites científicos

- El resultado corresponde a una realización de ruido por caso; no mide
  repetibilidad ni controla por sí mismo falsos positivos frecuentistas.
- LIFEsim clásico proporciona ruido fotónico diagonal; estos datos no incluyen
  una covarianza instrumental.
- La recuperación usa abundancias isochem aunque VULCAN varía verticalmente.
  El perfil Madhu recuperado también puede diferir de VULCAN. Una posterior
  estrecha o `ln B` positivo se interpreta junto con residuos, perfil térmico y
  degeneraciones.
- A1-1 h se seleccionó post hoc entre dos realizaciones. Su contraste es
  exploratorio y no constituye una predicción ciega.
- Ninguna lnZ entre tiempos, escenarios o realizaciones distintas es un factor
  de Bayes. No se declara detección formal solo por S/N, separación posterior
  z o un contraste condicional aislado.

### Cierre y validación

La auditoría final validó 36/36 productos: posteriores finitos que concuerdan
fila por fila con `post_equal_weights.dat`, espectros con longitud de onda
creciente, P–T de 100 capas con cuantiles ordenados, perfiles log-X completos,
trazas MultiNest y checkpoints coherentes. Los hashes de los seis datasets
coinciden con los archivos que declaran los resultados de sus modelos
completos. La `ln Z` y su error numérico en cada `stats.dat` concuerdan con el
resumen POSEIDON a la precisión impresa. El detalle reproducible está en el
[informe de validación](validation_report_20261010.json); el auditor está en
[`validate_proxima_molecular_ablation_loo.py`](../../../../scripts/validate_proxima_molecular_ablation_loo.py).

El corte eléctrico del 2026-10-10 interrumpió dos celdas a 100 h; ambas se
continuaron desde sus checkpoints MultiNest en el mismo scratch con `--resume`.
El historial permanece en
[`molecule_ablation_loo_20261004.resume_20261010_power_recovery.log`](../molecule_ablation_loo_20261004.resume_20261010_power_recovery.log)
y en `campaign_state.json`. Es un incidente resuelto, no un estado activo. La
tabla de `ln B`, sigma Sellke auxiliar, interpretación y límites científicos
se mantiene en el informe enlazado arriba.

## Referencias y productos relacionados

- Lin, Z., MacDonald, R. J., Kaltenegger, L., & Wilson, D. J. (2021),
  “Differentiating modern and prebiotic
  Earth scenarios for TRAPPIST-1e: high-resolution transmission spectra and
  predictions for JWST”, *MNRAS*, 505, 3562–3578,
  [doi:10.1093/mnras/stab1486](https://doi.org/10.1093/mnras/stab1486).
- [Campaña focal A1/A3 1/10/100 h](life_proxima_a1_a3_1_10_100h_official_retrieval_campaign_2026-10-01.md).
- [Atlas oficial V2](../Thermal_Emission_Spectroscopy/final_products/figures/retrieval_A1_A3_1_10_100h_official_six_species_PT_proxima.png).
