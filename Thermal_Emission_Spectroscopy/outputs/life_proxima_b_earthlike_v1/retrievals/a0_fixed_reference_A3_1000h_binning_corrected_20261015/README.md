# A3–1000 h / A0: tres restricciones, binning corregido, MPI5

Autorización 2026-10-15: N₂O fija a A0, NH₃ fija a A0 y ambas fijas,
con cinco ranks cada una y máximo 15 ranks. El completo corregido se conserva
en `../a3_1000h_binning_corrected_20261014/`. Los otros tiempos se aplazan.

**Estado histórico:** este intento fue interrumpido por un apagón el
2026-10-16. Su `campaign_state.json` y `manifest.csv` se conservaron tal como
quedaron dañados, sin reconstruirlos. La autorización posterior produjo una
campaña limpia y separada en
[`a0_fixed_reference_A3_1000h_binning_corrected_20261016_relaunch_01`](../a0_fixed_reference_A3_1000h_binning_corrected_20261016_relaunch_01/);
no contiene ni reanuda estos productos.

Interrupción detectada2026-10-16 11:44UTC: el supervisor816 y las tres MPI5
ya no están activos. `campaign_state.json` (16386B) y `manifest.csv` (1790B)
están llenos de NUL, última escritura10:10:30UTC; el inspector devuelve
`JSONDecodeError: Expecting value: line 1 column 1 (char 0)`. Últimos logs:
N₂O41400/704371, NH₃38550/700838, joint37550/693688 reemplazos/muestras;
sin exit ni cierre. Los ocho ficheros MultiNest por variante siguen en
`/home/dasan/exofarm_a0bin_A3_1000h_20261015/runs/`. No se ha restaurado,
reiniciado ni reanudado nada; causa no registrada. Esperar instrucciones.

Seguimiento2026-10-16 09:49UTC/04:49COT: `RUNNING`, aceptaciónPENDING,
supervisor816 y tres MPI5/quince ranks OMP1. N₂O/NH₃/conjunta: reemplazos
41000/38000/37050, evaluaciones686281/681683/673688; desde08:14UTC avanzaron
2150/3000/2450 reemplazos y85200/84865/84691 evaluaciones. CPU avanzó en los
quince ranks; RAM disponible23.44GiB, PSS19≈6.999GiB, swap0. Ocho archivos
MultiNest/caso, binding5/5 por log, sin firmas fatales. Dataset/operator hashes,
callback y source-equivalence PASS; priors libres coincidentes, dimensiones
13/13/12. Sin productos aceptados ni ln Z interpretable; procesos intactos.

Seguimiento2026-10-16 06:48UTC/2026-10-16 01:48COT: `RUNNING`, supervisor816,
tres MPI5 y quince ranks OMP1. N₂O/NH₃/conjunta: reemplazos36600/31600/31950,
evaluaciones523684/519880/510680; desde05:22UTC avanzaron2450/3600/2300
reemplazos y70207/67763/64301 evaluaciones. CPU aumentó en los quince ranks;
RAM disponible22.93GiB, PSS19procesos≈6.833GiB, swap0. Ocho archivos
MultiNest/caso, binding5/5 por log, cero patrones fatales. Dataset/operator
hashes conformes; callback y comparación de priors libres PASS; dimensiones
13/13/12. Sin productos finales aceptados ni ln Z interpretable; sin cambios
en procesos o alcance.

Seguimiento2026-10-16 05:22UTC/2026-10-16 00:22COT: `RUNNING`, tres MPI5
realmente activos. Supervisor816, mpiexec1083/1130/1177 y cinco ranks0–4 por
corrida/OMP1; reemplazos34150/28000/29650 y evaluaciones453477/452117/446379.
CPU avanzó en los quince ranks; RAM disponible24.41GiB, swap0,
PSS19procesos≈6.412GiB. Dataset/configuraciones conformes, binding5/5 en cada
log y ocho archivos MultiNest por caso. Hash actual del operador y auditoría de
equivalencia PASS; sin indicadores fatales ni productos finales aceptados. ln Z
provisional no interpretado. Monitor90min activo, sin modificar procesos.

Fuente operativa: `selected_scope.json`, `campaign_state.json`, `manifest.csv`.
Preflight inicial MPI5 en `preflight/`; configuraciones en `resolved/`.
Continuación vigente en `preflight_R1/`, log supervisor
`../a0_fixed_reference_A3_1000h_binning_corrected_20261015.source_audit_R1.supervisor.log`.
El primer gate textual se detuvo antes de muestrear por cambios de docstrings
y dos errores descriptivos. Fuente anterior reconstruida con hash exacto y
AST de cálculo equivalente: `source_equivalence/audit.json`; registros del
gate conservados en `pre_sampling_source_gate_failure/`.
Contrato emparejado y gate PSS: `preflight_validation.json` y `resource_gate.json`.
Logs de producción: `logs/`; archivado tras exit0: `runs/`.
Log/PID supervisor en el directorio padre, prefijo igual al nombre de campaña
más `.supervisor`. Scratch: `/home/dasan/exofarm_a0bin_A3_1000h_20261015/`.

Dataset SHA-256 `5611c5904ef03aa02586bed15f14c0c2560ac5ae6fa9463ef420229311db75fa`.
Opacidades retenidas; 15 coordenadas declaradas y 13/13/12 libres.
Log₁₀ X A0: N₂O=−6.884325289636784; NH₃=−9.950526295665036.
Mismo cálculo `LifePhotonOperator` que el completo (equivalencia de fuente
auditada tras cambios documentales); fresh sampling sin
checkpoints del operador anterior, N_live800, R10000, Madhu/isochem,
superficie negra1bar, ruido diagonal sin inflación.

Monitor activo cada 90 minutos:
`seguimiento-a3-1000-h-a0-binning-corregido`, heartbeat de este chat.
Silencio en estados sanos sin novedades accionables; informar fallo,
finalización o acción requerida. No relanzar ni cambiar ranks automáticamente.

Inspección de solo lectura en Ubuntu:

```bash
/home/dasan/anaconda3/envs/POSEIDON/bin/python /mnt/c/Proyectos/Astro/ExoFarm_MDwarfs/Thermal_Emission_Spectroscopy/scripts/inspect_proxima_a0_binning_corrected.py
```

Exit0 requiere auditoría independiente posterior de muestras, priors, valores
fijos, finitud, espectro/P–T/log_X, MultiNest y hashes. Tabla futura de tres
filas compara exclusivamente evidencias del mismo operador/dataset. El
χ² reducido≈14.29 del completo limita la interpretación; no confundir cierre
de cómputo con aceptación científica. El monitor termina tras auditoría,
tabla e informe de cierre.

[Procedimiento, scripts y registro](../../../../../docs/life_proxima_a3_1000h_a0_binning_corrected_2026-10-15.md).
