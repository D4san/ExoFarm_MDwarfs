# Reasignación autorizada MPI3 → MPI5 de los tres contrastes A0 A3–1000 h

Fecha: 2026-10-13. El usuario solicitó explícitamente parar las tres variantes
y reanudarlas con cinco procesos cada una. El completo terminó con exit 0
y sigue pendiente de auditoría; no se relanzó ni se alteraron sus productos.

## Razón y alcance

Al cerrar el completo quedaron CPU libres. Se asignan quince ranks de las
dieciséis CPU lógicas a N₂O fija, NH₃ fija y ambas fijas, cinco por modelo.
La documentación de [X-PSI, ejemplo de ejecución MultiNest](https://xpsi-group.github.io/xpsi/Example_job.html)
describe aumentar procesos al reanudar. Es respaldo metodológico; la lectura
real de estos checkpoints se verifica aparte. No se promete aceleración
proporcional a ranks: depende del rechazo, comunicación y carga del equipo.

Mismos basename, scratch, dataset SHA-256
`5611c5904ef03aa02586bed15f14c0c2560ac5ae6fa9463ef420229311db75fa`,
priors, referencia A0, opacidades, PT, N_live=800 y rejilla nativa 3–20 μm,
R=10000. Solo cambia `mpiexec -n 3` a `-n 5` y se añade `--resume`.
No se crean observaciones, nuevos modelos ni posteriors alternativos.

## Procedimiento ejecutado

Se comprobaron PID, argumentos, parentesco y fecha de creación de procesos.
Se suspendió temporalmente el supervisor y su árbol exacto para estabilizar
los archivos. Con las escrituras congeladas se comprobaron los tres estados:
800 puntos vivos, dimensiones 800×16 y 800×17, tablas de eventos completas,
finitud, cubo unitario, igualdad de likelihoods, priors y valores fijos exactos.
Si fallaba esta fase, el procedimiento devolvía los procesos originales a
ejecución, sin cerrarlos. Los tres checkpoints pasaron.

Se respaldaron ocho archivos por variante, 24 en total, con comprobación
SHA-256 de cada copia. Solo después se cerraron por SIGKILL las identidades
verificadas del supervisor original y sus tres árboles MPI. Los checkpoints
quedan preservados; el cómputo no persistido desde ellos puede repetirse.
No se borraron directorios ni archivos científicos.

| Variante | Reemplazos persistidos | Evaluaciones persistidas | Nuevos MPI PID |
| --- | ---: | ---: | ---: |
| N₂O fija | 43 600 | 889 636 | 5080 |
| NH₃ fija | 33 000 | 882 767 | 5090 |
| Ambas fijas | 42 800 | 884 613 | 5100 |

Supervisor nuevo PID 5062, central RUNNING. Quince ranks activos confirmados:
N₂O 5112/5114/5115/5117/5120; NH₃ 5113/5116/5118/5119/5121;
conjunta 5123–5127. Arranque en carga de opacidades; la lectura efectiva
MultiNest y el avance posterior de contadores todavía están pendientes.
Memoria disponible ~26 GiB y swap vacía en el primer control.

## Recuperabilidad

- [Migrador y supervisor](../Thermal_Emission_Spectroscopy/scripts/rebalance_proxima_a0_1000h_mpi5.py).
- Campaña: `retrievals/a0_fixed_reference_A3_1000h_20261012/`.
- Estado vigente: `campaign_state.json` y `manifest.csv` centrales.
- Logs nuevos y supervisor: `recovery_20261013_MPI5_R1/`.
- Evidencia de migración: `before_state.json`, `before_manifest.csv`,
  `old_process_identities.json`, `checkpoint_validation.json`,
  `protected_inputs.json`, `checkpoint_backup/{N2O,NH3,joint}/`.
- Los logs `logs/` anteriores son históricos; usar los nuevos para progreso.
- El migrador es de un solo uso; no reintenta, no duplica ni acepta resultados.

Se congelaron adicionalmente hashes de los productos cerrados del completo.
Los originales anteriores y las tres configuraciones resueltas permanecen
intactos. Exit 0 sigue conduciendo a auditoría independiente y después a
ln B emparejados y sigmas según el [procedimiento de comparación](life_proxima_a3_1000h_a0_comparison_2026-10-12.md).
