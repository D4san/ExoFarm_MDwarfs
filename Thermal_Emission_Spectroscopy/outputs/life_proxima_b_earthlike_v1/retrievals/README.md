# Retrievals LIFE de Proxima: resultado vigente e índice histórico

## Resultado oficial vigente

La matriz A1/A3 de ablaciones moleculares vigente está en
[`a1_a3_corrected_binning_matrix_loo_20261021_r01`](a1_a3_corrected_binning_matrix_loo_20261021_r01/README.md).
Su estado es `COMPLETE_VALIDATED`: los 33 retrievals nuevos pasaron auditoría
independiente. Consulta el [informe final](../../../../docs/life_proxima_a1_a3_corrected_binning_matrix_results_2026-10-28.md),
la [tabla de modelos](../../../../docs/life_proxima_a1_a3_corrected_binning_matrix_models_2026-10-28.csv)
y la [tabla LOO emparejada](../../../../docs/life_proxima_a1_a3_corrected_binning_matrix_loo_2026-10-28.csv).
El atlas oficial de posteriores está indexado en
[`final_products/README.md`](../../../final_products/README.md).
El [inventario de integridad](../../../../docs/evidence/life_proxima_a1_a3_release_2026-10-28/README.md)
registra las huellas de esta serie y sus referencias; existe una copia
verificada en E: con el alcance indicado en ese inventario.

Las referencias de modelos completos A3 usadas por la matriz son la campaña
validada de [1 h y 10 h](a3_1_10h_binning_corrected_loo_20261020_r03/README.md)
y la referencia validada de [100 h MPI14](a3_100h_binning_corrected_mpi14_resume_20261018/README.md).

## Otras campañas e historial

Estas carpetas responden preguntas distintas o conservan intentos anteriores.
No forman parte de la matriz vigente, salvo cuando el informe los identifica
explícitamente como referencias.

| Carpeta | Función / estado |
|---|---|
| `a3_1_10h_binning_corrected_loo_20261020_r02/` | Intento detenido por fallo de preflight MPI5 antes del muestreo; r03 lo sustituyó y quedó validado. Se conservan manifiestos y logs. |
| `a3_100h_binning_corrected_20261017/` | Corrida detenida por solicitud del usuario; la continuación MPI14 validada está enlazada arriba. |
| `a3_100h_binning_corrected_loo_20261019/` | Comparación molecular A3–100 h validada, con su propio dataset. |
| `a3_1000h_binning_corrected_20261014/` | Retrieval completo A3–1000 h con operador corregido; la validación independiente sigue pendiente. |
| `a3_1000h_full_20261011/` | Intento histórico fallido en preflight; se conserva para diagnóstico y procedencia. |
| `a0_fixed_reference_20261010/`, `a0_fixed_reference_A3_1000h_20261012/`, `a0_fixed_reference_A3_1000h_binning_corrected_20261015/`, `a0_fixed_reference_A3_1000h_binning_corrected_20261016_relaunch_01/` | Referencias A0 con configuraciones y estados de auditoría distintos; consultar cada README antes de reutilizarlas. |
| `molecule_ablation_loo_20261004/` | Estudio LOO anterior de 36 corridas, validado y separado de la matriz actual. |
| `POSEIDON_output/` | Productos POSEIDON históricos con su propia procedencia y nombres. |

Los productos históricos permanecen intactos para reproducibilidad. Los `.pid`
y logs de supervisor sueltos en esta carpeta son registros de lanzamientos
anteriores; para saber si hubo una corrida activa, prevalecen el estado y el
manifiesto de cada campaña. Este índice separa con claridad el resultado
vigente del historial. No moví carpetas: varias rutas antiguas están inscritas
en manifiestos, snapshots y scripts, y trasladarlas rompería esos enlaces.
