# Configuraciones de la Etapa III

Esta carpeta conserva el contrato y la separación conceptual de las dos capas.
La rama clásica ya fue ejecutada; sus manifiestos efectivos están junto a los
productos bajo `outputs/<campaign-id>/manifest.json`, y sus parámetros también
quedan versionados en `scripts/`. Aún falta promoverlos a una configuración
ejecutable autocontenida en `configs/`.

- `life_earth_sun_10pc/`: configuración de emisión POSEIDON y escena
  LIFEsimMC/PHRINGE para el benchmark primario.
- `life_proxima_b_earthlike/`: configuración LIFE posterior a que VULCAN acepte
  los nuevos perfiles bajo la SED de Proxima.

Cada manifiesto nuevo deberá enlazar el perfil PT/química exacto, versiones de
software, parámetros de estrella/planeta, geometría, escena, malla, unidades,
semilla y ruta de productos. No copiar perfiles ni espectros grandes aquí.

Véase [`../../docs/life_stage_iii_two_layer_workplan_2026-07-20.md`](../../docs/life_stage_iii_two_layer_workplan_2026-07-20.md).

> **Reanudación:** la próxima configuración nueva corresponde al piloto
> LIFEsimMC/PHRINGE con covarianza. Antes de añadirla, leer el
> [contrato de la Etapa III](../README.md), el
> [punto de entrada operativo](../../docs/project_resume.md) y el
> [tracker](../../docs/project_status_tracker.md).
