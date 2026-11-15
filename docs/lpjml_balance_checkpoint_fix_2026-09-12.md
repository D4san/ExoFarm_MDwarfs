# Recuperación del balance tras checkpoint de spin-up

Fecha: 2026-09-12. Campaña: `global_a1_checkpoints_20260909`.

## Diagnóstico y corrección

LPJmL 6.0.6, commit `5af44a1ed023279a23c28d6dfe76945b97aaac57`,
terminó con ERROR004 al calcular el año 3. Los logs identifican las celdas
50566 y 58993: delta_totc coincide con todo el stock actual, porque el stock
anterior de diagnóstico todavía vale cero. El checkpoint guardado corresponde
al año −3 y su SHA256 verificado es
`d4b276cd3f65732a50e1d818dca0681935d2debf0d3abbce727fcf2d430117d5`.

En `src/lpj/updateannual_grid.c`, la primera llamada natural a `check_fluxes`
ocurre en año 3: −2099 + 900 + 60 × 20 + 0 + 2. El código continuo excluye
la aserción ese año para inicializar el acumulador. En `src/lpj/check_fluxes.c`,
la rama checkpoint sustituye ese umbral por checkpointyear + 1 = −2, haciendo
que la primera llamada compruebe una diferencia contra cero. La inspección del
runtime confirmó el mismo código que el checkout local.

La corrección conserva el umbral natural o agrícola y aplica
`startyear = max(startyear, checkpointyear + 1)` al reanudar. Se mantienen
`fail_on_balance=true`, tolerancias, ecuaciones y configuración científica.
Es una corrección local al control de diagnóstico, todavía sujeta a validación
de integración; no constituye una nueva versión oficial de LPJmL.

## Implementación reproducible y prueba

Preparación: [prepare_balance_recovery.py](../Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction/prepare_balance_recovery.py).
El script verifica el checkpoint y crea una copia del build en
`/home/dasan/exofarm-lpjml-runtime/LPJmL-6.0.6-balance-fix-20260912`.
El original queda preservado. La prueba independiente se aloja en
`/home/dasan/exofarm-lpjml-runs/balance_recovery_20260912`, físicamente en E:.
Allí quedan `balance-fix.patch`, `build.log`, `manifest.json`, `run_test.sh`,
logs por segmento y una copia separada del checkpoint.

La prueba conserva las 67,420 celdas y ocho ranks, y solicita un checkpoint
después del año 4 mediante el controlador existente. Debe atravesar el año
problemático 3 y comprobar balances de años posteriores, salir con código cero,
guardar un archivo íntegro y no producir errores de balance. Cambia únicamente
la ruta operativa del checkpoint; no acorta el spin-up ni modifica sus fechas.

Build corregido SHA256:
`bd7c46e889f5b88b682d237ba58aa1c25a83285bd505fa87c597d901970f585b`.
Fuente corregida SHA256:
`5e665c356060fe628fe19d4a152f499be32935e4dcaf032bfd613fd70aecc912`.

## Resultado y reanudación

Prueba aceptada: años −2 a 5 completos, salida cero y checkpoint guardado
con SHA256 `3a62872725279197113d1dd5c786fdf4b948b8fd1e964e231bc90c97d43b6d6f`.
Sin errores de balance; configuración científica idéntica. Todos los diagnósticos
anuales −2 a 2 coinciden exactamente con los del ejecutable original a la
precisión impresa del log. El checkpoint original sigue íntegro. `make test`
también terminó con código cero.

Aceptación reproducible: [accept_balance_recovery.py](../Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction/accept_balance_recovery.py).
Evidencia compacta: [validation.json](evidence/balance_recovery_20260912/validation.json),
[manifest.json](evidence/balance_recovery_20260912/manifest.json),
[parche](evidence/balance_recovery_20260912/balance-fix.patch),
[build.log](evidence/balance_recovery_20260912/build.log) y
[make-test.log](evidence/balance_recovery_20260912/make-test.log).

La campaña global se reanudó el 12 de septiembre a las 14:38 America/Bogota,
desde su checkpoint original −3, con ocho ranks activos comprobados y el build
corregido. El lanzador anterior quedó respaldado como
`launch_campaign.pre_balance_fix_20260912.sh`; se añadieron manifiesto y
validación del parche al directorio de campaña. Seguimiento horario reactivado.
La prueba hasta año 5 valida esta recuperación, no la finalización de todo el
spin-up ni los futuros flujos A1, que siguen pendientes.
