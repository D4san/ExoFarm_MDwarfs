# A3–1000 h / A0 fija: relanzamiento con binning corregido

Autorizado por el usuario el 2026-10-16 tras el apagón que interrumpió el
intento `a0_fixed_reference_A3_1000h_binning_corrected_20261015`. Ese intento
y su estado/manifest dañados permanecen preservados. El scratch anterior no
contiene checkpoints legibles; este relanzamiento empieza desde cero y no
reutiliza muestras.

## Alcance congelado

- A3–1000 h: N₂O fija a A0, NH₃ fija a A0 y ambas fijas.
- Cinco ranks MPI por corrida, máximo tres corridas y 15 ranks en total;
  respetar la cola por recursos.
- Mismo dataset observado, SHA-256
  `5611c5904ef03aa02586bed15f14c0c2560ac5ae6fa9463ef420229311db75fa`.
- Operador de binning corregido, callback validado; contraste únicamente con
  `a3_1000h_binning_corrected_20261014`.
- N_live=800, ev_tol=0.5, R=10000, 3–20 μm, Madhu/isochem/O₂, superficie negra
  a 1 bar, nodos térmicos 180–310 K cada 10 K, sin inflación.
- 15 coordenadas declaradas; 13/13/12 efectivamente libres. Retener opacidades;
  log10 A0: N₂O=−6.884325289636784, NH₃=−9.950526295665036.
- No ejecutar 1/10/100 h ni otros escenarios.

## Cierre de ejecución y auditoría — 2026-10-17

Las tres variantes terminaron con `return_code=0`. La auditoría independiente
validó posterior/prior y dimensiones, espectro, P–T, `log_X`, ocho archivos
MultiNest por corrida, contadores, evidencia, dataset, operador y hashes. La
tabla final empareja las tres ln Z con el completo corregido usando el mismo
dataset. N₂O fija: `ln B=626.5061±0.3845`; NH₃ fija:
`ln B=−0.9927±0.3825` (sigma `N/A`); ambas fijas:
`ln B=626.0635±0.3822`. El sigma bilateral auxiliar es 35.50/`N/A`/35.49;
`ln B` permanece como resultado principal.

La aceptación formal sigue pendiente por seis `NaN` limitados a desviaciones
derivadas de coordenadas exactamente fijas en `-summary.txt`/`stats.dat`.
Los valores de muestras, perfiles fijados y demás productos son finitos; los
originales no se modificaron. Momentos centrados estables con desviaciones
cero se guardaron como sidecars separados. El ledger indica
`VALIDATED_PRIMARY_PRODUCTS_REQUIRES_REVIEW`, aceptación
`PENDING_FIXED_MOMENT_REVIEW`; no se aplicó una excepción automática.

La posterior libre sitúa N₂O en mediana `6.71×A0` (IC95 % 6.28–7.14; las
7168 filas guardadas superan A0). NH₃ tiene mediana `6.62×A0`, pero IC95 %
0.0215–19.22 y `P(NH₃>A0)=0.787`, por debajo del prior nominal 0.814. La
comparación conjunta no asigna evidencia individual a NH₃. El completo
mantiene `χ²_red=14.29` con 17 dof efectivos, por lo que las conclusiones son
condicionales y requieren cautela de adecuación del modelo.

- [Informe científico y decisión de aceptación pendiente](../../../../../docs/life_proxima_a3_1000h_a0_fixed_binning_corrected_audit_2026-10-17.md).
- [Auditoría JSON](validation_report_20261017.json), [estado](campaign_state.json), [manifiesto](manifest.csv).
- [Tabla CSV](../../../../final_products/tables/life_proxima_a3_1000h_a0_fixed_binning_corrected_2026-10-17.csv) y [JSON](../../../../final_products/tables/life_proxima_a3_1000h_a0_fixed_binning_corrected_2026-10-17.json).
- [Momentos estables auxiliares CSV](fixed_parameter_moments_stable_20261017.csv) y [JSON](fixed_parameter_moments_stable_20261017.json); los productos MultiNest originales quedan preservados.
- Logs finales conservados en esta campaña; no quedan MPI activos. La tentativa interrumpida de 15-oct sigue separada e intacta.
