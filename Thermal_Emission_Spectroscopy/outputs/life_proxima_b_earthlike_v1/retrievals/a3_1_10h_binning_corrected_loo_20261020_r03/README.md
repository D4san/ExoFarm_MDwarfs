# A3 LIFE Proxima a 1 h y 10 h — LOO con binning corregido

**Estado: `COMPLETE_VALIDATED`; auditoría independiente PASS (2026-10-21).** Se completaron seis retrievals: completo, sin NH₃ y sin N₂O para 1 h y 10 h. Los seis terminaron con `return_code=0`; los manifiestos y snapshots del supervisor se reconciliaron después de verificar productos y logs. Las copias previas a reconciliación quedan preservadas junto a este README.

## Contrastes emparejados

En cada fila, `ΔlnZ = lnZ(completo) − lnZ(sin X)`. Solo se restaron evidencias del mismo dataset/duración; errores en cuadratura. ΔlnZ positivo favorece incluir la especie.

| Duración | Especie retirada | ΔlnZ ± error numérico | Sigma bilateral auxiliar | P(log₁₀ X>A0) en completo |
|---:|---|---:|---:|---:|
| 1 h | NH₃ | −0.526485 ± 0.234278 | N/A | 0.5397 |
| 1 h | N₂O | −0.029618 ± 0.234922 | N/A | 0.1898 |
| 10 h | NH₃ | −0.225706 ± 0.292617 | N/A | 0.8040 |
| 10 h | N₂O | +9.141993 ± 0.292323 | +4.664 | 0.99986 |

La señal condicional más clara es N₂O a 10 h. La evidencia para incluir NH₃ queda equilibrada o favorece levemente la ablación, aunque su posterior a 10 h tiene masa mayoritaria sobre A0. La probabilidad posterior de abundancia y la comparación de modelos contestan preguntas distintas. La sigma es una calibración bilateral descriptiva, no una significancia frecuentista ni una probabilidad de actividad agrícola.

## Diseño y validación

Se usaron realizaciones observadas preservadas: 1 h `LIFE_proxima_A3_1h_O2_fixedBlack1bar_official.dat` (SHA-256 `a3043e5de76a834983949e6eca12636ea4de174ebdb2db0853155282c100dee2`) y 10 h `LIFE_proxima_A3_10h.dat` (SHA-256 `46a026504b9b9521fa29407a501169b9d3cfc433de40a91b8ade86d7767abb5b`), ambas de 31 canales. Cada tanda ejecutó tres MPI5 (15 ranks) secuencialmente; no se reutilizaron checkpoints. Configuración: `N_live=800`, `ev_tol=0.5`, `R=10000`, 3–20 μm, Madhu/isochem/O₂, superficie negra fija a 1 bar y sin inflación de errores; full 15/14 coordenadas declaradas/libres, LOO 14/13.

La auditoría verificó por corrida exit 0, configuraciones y priors emparejados, hashes de datasets, exclusión simultánea de parámetro y opacidad, callback corrected-bin enlazado durante muestreo/postproceso, coincidencia entre posterior POSEIDON y muestras equal-weight MultiNest, finitud, espectro, P–T, `log_X`, stats, resume, evaluaciones, reemplazos y puntos vivos. Los 1 h y 10 h se comparan por separado. Las ejecuciones históricas con binning anterior no son comparadores emparejados; también difieren en la ventana espectral nativa.

## Artefactos

- [Informe científico con tablas, posteriores e interpretación](../../../../../docs/life_proxima_a3_1_10h_corrected_binning_loo_results_2026-10-21.md)
- [`selected_scope.json`](selected_scope.json), [`campaign_state.json`](campaign_state.json) y [`manifest.csv`](manifest.csv)
- [Auditoría detallada y hashes](validation_report_20261021.json)
- [Resumen por modelo (seis retrievals)](retrieval_models_validated_20261021.csv) · [contrastes LOO (cuatro parejas)](loo_results_validated_20261021.csv)
- [Figura SVG de ΔlnZ](a3_1_10h_corrected_bin_molecular_ablation_lnB_20261021.svg)
- [Script reproducible de auditoría](../../../../scripts/audit_proxima_a3_1_10h_corrected_bin_campaign.py)
- [Snapshot original del ledger](campaign_state_pre_audit_20261021.json) · [snapshot original del manifiesto](manifest_pre_audit_20261021.csv)

Se conservan intactos los intentos de arranque r01/r02, los productos previos y todas las demás campañas. Esta comparación de retrievals no basta para atribuir N₂O o NH₃ a una tecnosignatura agrícola ni para excluir otras explicaciones atmosféricas.
