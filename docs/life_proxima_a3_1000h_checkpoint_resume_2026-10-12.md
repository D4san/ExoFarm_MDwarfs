# Recuperación del retrieval LIFE Proxima A3–1000 h — 2026-10-12

## Alcance y autorización

El usuario autorizó continuar el único retrieval completo A3–1000 h desde
su último checkpoint. Se mantiene el dataset independiente, su realización
de ruido, Madhu/isochem, O₂, superficie negra fija a 1 bar, R=10000,
rejilla nativa 3–20 μm, N_live=800, 15 coordenadas declaradas y 14 libres.
No se generan nuevos datos ni se ejecutan LOO, A0 fija, A1 o variantes P–T.
Las 1000 horas son integración observacional sintética, no tiempo de cómputo.

## Interrupción observada

Revisión del 12 de octubre de 2026, aproximadamente 17:20 COT: el archivo
de campaña conservaba `RUNNING`, pero la inspección de procesos confirmó
ausencia del supervisor y MPI. El log terminó el 12 de octubre a las
15:40:26 UTC / 10:40:26 COT, con 51 250 reemplazos y 2 652 195 evaluaciones.
No se encontró una excepción en los logs. Ubuntu apareció recién iniciado;
la causa exacta de la interrupción permanece sin confirmar.

El checkpoint persistido registra **51 200 reemplazos y 2 646 212
evaluaciones**, con 800 puntos vivos. La diferencia de 5 983 evaluaciones
respecto al último log no estaba incorporada al checkpoint y puede repetirse.
La reanudación utiliza el punto persistido, no inventa recuperación del
segmento posterior ni reinicia el muestreo desde cero.

## Validación y respaldo

[Script de recuperación](../Thermal_Emission_Spectroscopy/scripts/resume_proxima_a3_1000h.py)
con modo `--check-only` completado con exit 0 y resultado PASS:

- `live.points`: 800 × 16; quince coordenadas del cubo unidad y likelihood.
- `phys_live.points`: 800 × 17; parámetros, likelihood e identificador de modo.
- `ev.dat`: 50 400 × 18, consistente con los reemplazos menos los 800 vivos.
- Finitud de las tres tablas PASS; coordenadas del cubo dentro de [0,1].
- Likelihoods de puntos vivos idénticos entre representación física y cubo.
- Todos los parámetros físicos dentro de los priors registrados; `log_P_surf=0`
  exactamente en las 800 muestras, sin cambiar su prior de anchura cero.
- 29 hashes protegidos intactos, configuración resuelta y dataset verificados.

Dataset SHA-256:
`5611c5904ef03aa02586bed15f14c0c2560ac5ae6fa9463ef420229311db75fa`.
Configuración SHA-256:
`2976d13f5669a2558c17dca2f30972dc16b907fba378b66dd3e065da476d5e7f`.
Runner SHA-256:
`3fcd08939e385ac9934b6fe297591480244fa753bf0122184aee2697e6e73fa1`.

La recuperación R1 crea una copia de los ocho archivos MultiNest con hash
de origen y respaldo idénticos antes de reanudar, y conserva estado,
configuración, manifiesto y logs interrumpidos. No elimina ni sobrescribe
los registros previos. Los archivos de trabajo del mismo basename se actualizan
al continuar el muestreo; la copia anterior permanece separada.

## Ejecución y fuentes de verdad

Campaña:
`Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_1000h_full_20261011/native_grid_retry/`.
El estado vigente sigue siendo `campaign_state.json`. Recuperación aislada:
`recovery_20261012_R1/`, con `checkpoint_validation.json`,
`checkpoint_backup/`, `interrupted_campaign_state.json`,
`interrupted_retrieval.log`, `command.json`, `supervisor.log`,
`supervisor.pid` y nuevo `retrieval.log`.

Se invoca el mismo runner y scratch original
`/home/dasan/exofarm_a3_1000h_20261011_nativegrid/run/`, con el mismo
basename `proxima_A3_1000h_O2_fixedBlack1bar_noxtol_MPI6_NG` y **`--resume`**.
Se conserva MPI6 y una hebra BLAS por rank. El runner recibe la configuración
resuelta previa y exige igualdad. La recuperación rechaza procesos científicos
activos o registros R1 preexistentes; no vuelve a intentar un fallo por automatismo.

**Lanzamiento R1 verificado a las 22:25:14 UTC / 17:25:14 COT**: supervisor
803, mpiexec 805 y seis ranks 820–825 activos, con `--resume` y la
configuración resuelta original. Estado central RUNNING; en la primera
inspección están cargando opacidades. El mensaje/contador restaurado de
MultiNest se comprobará antes de acreditar continuidad efectiva del muestreo.

**Comprobación posterior al arranque:** terminaron todas las opacidades y el
log nuevo registra `resuming from previous job` y `Starting MultiNest`.
Supervisor, mpiexec y seis ranks siguen activos (13 minutos de ejecución
en la comprobación). La lectura de recuperación está confirmada por el
programa; aún se espera el primer contador posterior para verificar avance
cuantitativo desde las 2 646 212 evaluaciones del checkpoint. No hay una
terminación ni una evidencia final aceptada en esta comprobación.

**Continuidad cuantitativa confirmada posteriormente:** log R1 con 51 500
reemplazos y 2 693 510 evaluaciones, superiores al checkpoint 51 200 /
2 646 212. El usuario amplió luego el alcance a cuatro modelos de 1000 h;
el completo conserva sus seis ranks y no fue reiniciado ni modificado.
[Ampliación de los tres contrastes A0](life_proxima_a3_1000h_a0_comparison_2026-10-12.md).
Los ocho archivos de respaldo coinciden por hash (cero discrepancias).
La prueba de duplicación R1 fue rechazada con exit 1 antes de crear procesos.

## Aceptación pendiente

Esta validación acredita la integridad estructural y numérica del checkpoint;
la lectura efectiva por MultiNest y la continuación deben comprobarse aparte.
Las muestras y evidencias parciales siguen provisionales. Exit 0 conduce a
`COMPLETE_PENDING_VALIDATION`; antes de aceptación deben auditarse posterior,
espectro, PT/log_X, priors, superficie, hashes, finitud y calidad del ajuste.
El único completo de 1000 h no aporta un ln B emparejado de presencia o
enriquecimiento; no se comparan ln Z entre datasets de diferentes exposiciones.

[Procedimiento original y corrección de rejilla](life_proxima_a3_1000h_extension_2026-10-11.md).
