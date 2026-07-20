# Reanudar ExoFarm: punto de entrada operativo

**Última actualización estructural:** 2026-07-20
**Uso:** leer este documento al iniciar una tarea nueva o un chat nuevo en este
repositorio. Resume el estado recuperable, la próxima acción autorizada y los
documentos que contienen el detalle. No sustituye la verificación en vivo de
procesos, entornos, archivos ni `git status`.

## Lectura mínima, en este orden

1. [`../AGENTS.md`](../AGENTS.md): reglas científicas, de seguridad, rutas y
   requisitos de verificación.
2. Este documento: alcance activo y siguiente paso.
3. [`project_status_tracker.md`](project_status_tracker.md): backlog, decisiones
   y estado por etapa.
4. El README de la etapa afectada y, si se va a ejecutar software, su documento
   de entorno correspondiente.

Los informes fechados en `docs/` son evidencia y contexto; no se deben usar
aisladamente como estado operativo actual. Ante discrepancia, comprobar los
archivos/outputs en vivo y actualizar el tracker y este documento.

## Estado recuperable en un minuto

| Etapa | Estado | Regla de reanudación |
| --- | --- | --- |
| 0 — LPJmL | **Suspendida** | Conservar checkout, notas y conversores; no descargar, compilar, correr ni acoplar LPJmL sin una reactivación explícita. |
| I — VULCAN Tierra--Sol | **Aceptada, benchmark pre-corrección de N2O** | Los cuatro A0--A3 tienen `end_case = 1`, pero A2/A3 proceden del conjunto guardado el 2026-06-15, anterior a la corrección actual de N2O. Sirven para validar la interfaz LIFE, no para presentar todavía la matriz vigente como resultado final. |
| I — VULCAN TRAPPIST-1e | **Aceptada con salvedad** | `end_case = 3` por química traza; conservar la salvedad en cualquier uso de esos productos. No usar esos perfiles para Proxima. |
| II — transmisión/JWST | **Campaña A0/A3 cerrada** | La matriz optimizada de 18 retrievals es la evidencia vigente. Los perfiles TRAPPIST actuales se regeneraron junto con los BC corregidos en `fb9812d`; no confundir esta campaña con la salvedad Tierra--Sol de Stage III ni reabrir una cola sin verificar outputs y procesos en vivo. |
| III — LIFE | **Planificada; sin productos** | La única acción inmediata es la auditoría de entorno y manifiesto de Capa 1. No hay instalación/configuración versionada de LIFEsimMC/PHRINGE, forward térmico, ruido, SNR ni retrievals LIFE. |

## Próximo trabajo autorizado

### Capa 1 — `life_earth_sun_10pc`

Es el único caso LIFE que puede prepararse de inmediato. La acción autorizada
ahora es una auditoría no destructiva de entorno/API y un manifiesto; el primer
cálculo posterior sería un forward A0 sin ruido. Usa el benchmark sintético
Tierra--Sol a 10 pc; los 10 pc pertenecen a la escena observacional, no cambian
la fotoquímica existente.

**Insumos canónicos que se deben cargar, no regenerar ni aproximar:**

| Escenario | `.vul` canónico | Hand-off PT/química |
| --- | --- | --- |
| A0 | `Photochemical_Modeling/Results/Outputs/Earth_A0_PreAgri.vul` | `Transmission_Spectroscopy/profiles/Earth_A0_PreAgri_{PT,chem}.txt` |
| A1 | `Photochemical_Modeling/Results/Outputs/Earth_A1_Current.vul` | `Transmission_Spectroscopy/profiles/Earth_A1_Current_{PT,chem}.txt` |
| A2 | `Photochemical_Modeling/Results/Outputs/Earth_A2_Moderate.vul` | `Transmission_Spectroscopy/profiles/Earth_A2_Moderate_{PT,chem}.txt` |
| A3 | `Photochemical_Modeling/Results/Outputs/Earth_A3_Extreme.vul` | `Transmission_Spectroscopy/profiles/Earth_A3_Extreme_{PT,chem}.txt` |

El formato PT es altitud (km), presión (bar), temperatura (K); química es
presión (bar) y mixing ratios por especie. El exportador que define este
contrato es
[`../Transmission_Spectroscopy/scripts/export_vulcan_profiles.py`](../Transmission_Spectroscopy/scripts/export_vulcan_profiles.py).

> **Salvedad de procedencia.** Este conjunto de perfiles está congelado como
> `earth_20260615_pre_n2o_correction`: A2/A3 usaron `N2O = 3.35e9` y `1.20e10`,
> no los BC activos corregidos (`3.416e9` y `1.238e10`). Puede validar la
> interfaz POSEIDON--LIFEsimMC/PHRINGE, pero no debe presentarse como la matriz
> ExoFarm vigente hasta tomar una decisión de rerun o de uso histórico.
> Véase la [nota de procedencia](earth_sun_n2o_matrix_provenance_2026-07-20.md).

**Secuencia, sin saltos:**

1. Verificar y congelar versiones/licencias de POSEIDON, LIFEsimMC y PHRINGE,
   más escena LIFE, superficie/emisividad, malla, fondos, tiempo y semilla;
   registrar el rótulo de procedencia anterior en el manifiesto.
2. Construir un forward de **emisión** POSEIDON que lea PT/química de archivo
   para validar la interfaz, no para declarar la matriz corregida.
   Los scripts de transmisión actuales son referencias de lectura, no una
   configuración térmica reutilizable.
3. Validar un A0 sin ruido: cantidad física, malla, radios, distancia y cadena
   `Fp/Fs` → flujo observado → radiancia de LIFEsimMC.
4. Generar A0--A3, contrafactuales de `N2O`/`NH3` y controles de `H2O`, `CO2`,
   `O3` y `CH4`, siempre con la etiqueta pre-corrección hasta resolver la
   procedencia.
5. Ejecutar un piloto reproducible LIFEsimMC/PHRINGE y guardar observación,
   SED extraído, covarianza, semilla y manifiesto.
6. Producir diagnósticos y tablas SNR de interfaz. Antes de atribuirlos a la
   matriz vigente, decidir/repetir el conjunto Tierra--Sol con BC corregidos.
   Solo entonces diseñar una matriz de retrievals; **no lanzar retrievals LIFE
   aún**.

El detalle y las puertas están en
[`life_stage_iii_two_layer_workplan_2026-07-20.md`](life_stage_iii_two_layer_workplan_2026-07-20.md)
y [`../Thermal_Emission_Spectroscopy/README.md`](../Thermal_Emission_Spectroscopy/README.md).

### Capa 2 — `life_proxima_b_earthlike`

Esta capa no es un preset adicional de LIFE: comienza como una rama nueva de
VULCAN. Está aprobada como siguiente extensión M, pero queda bloqueada hasta
cerrar su cadena de insumos.

```text
SED MUSCLES Proxima + metadatos/checksum
    → conversión reproducible a flujo superficial VULCAN
    → VULCAN Proxima A0--A3 aceptado
    → PT/química exportados
    → misma cadena POSEIDON emisión → LIFEsimMC → SNR → diseño de retrievals
```

- El baseline será `VULCAN/atm/atm_Earth_Jan_Kzz.txt`: un control terrestre
  para aislar el efecto de la SED de Proxima.
- No reutilizar `atm_Trappist1e_Lin_Kzz.txt`, `100x CO2`, factores de escala de
  TRAPPIST-1 ni su excepción de convergencia.
- Etiquetar el resultado como **análogo terrestre bajo el ambiente de Proxima
  b**, nunca como la atmósfera medida de Proxima b.
- La SED fuente, notas de reducción, estado de actividad, conversión a
  superficie, escala geométrica y extensión MIR para LIFE deben quedar
  registrados antes de una corrida VULCAN.

## Límites que no se pueden olvidar

- Stage III usa emisión térmica; no mezclar profundidades de tránsito, archivos
  PandExo, conteos de tránsitos ni `Transmission_Spectroscopy/notebooks/POSEIDON_output/`.
- LIFEsimMC puede entregar covarianza. No reducirla silenciosamente a errores
  diagonales: usar whitening reproducible o likelihood consciente de
  covarianza.
- SNR es un diagnóstico, no una detección. Las afirmaciones de detección esperan
  retrievals, modelos comparados y varias realizaciones de ruido.
- Los `.vul` permanecen en `Photochemical_Modeling/Results/Outputs/`; Stage III
  guarda sus productos únicamente bajo
  `Thermal_Emission_Spectroscopy/outputs/<campaign-id>/`.

## Cómo recuperar el trabajo de forma segura

1. Ejecutar `git status --short` y no sobrescribir cambios ajenos. La presencia
   de productos o documentación no implica que una simulación esté validada.
2. Confirmar la etapa y el ID de campaña contra el tracker y este documento.
3. Para POSEIDON, comprobar el entorno WSL en vivo; la ruta histórica útil es
   `/home/dasan/anaconda3` y los inputs viven bajo `/mnt/d/.../POSEIDON/inputs`,
   pero esas rutas deben verificarse antes de ejecutar.
4. Antes de una corrida costosa, comprobar que existe el manifiesto de campaña,
   que las unidades están escritas, que las entradas coinciden con la campaña y
   que el manifiesto distingue `earth_20260615_pre_n2o_correction` de los BC
   vigentes.
5. Después de una decisión, ejecución o validación material, actualizar:
   - `docs/project_status_tracker.md`;
   - este archivo `docs/project_resume.md`;
   - `experiments/README.md`;
   - el README de la etapa y un informe en `docs/` cuando cambie el argumento
     científico o la interfaz.

## Mapa de documentación

| Necesidad | Fuente canónica |
| --- | --- |
| Reglas para agentes y guardrails | [`../AGENTS.md`](../AGENTS.md) |
| Estado, backlog y decisiones | [`project_status_tracker.md`](project_status_tracker.md) |
| Etapa I y contrato de VULCAN | [`photochemical_profiles_methodology.md`](photochemical_profiles_methodology.md) |
| Inventario/entorno de transmisión | [`transmission_spectroscopy_inventory_2026-06-16.md`](transmission_spectroscopy_inventory_2026-06-16.md) |
| Diseño general Stage III | [`life_lifesim_stage_iii_plan.md`](life_lifesim_stage_iii_plan.md) |
| Flujo concreto de dos capas | [`life_stage_iii_two_layer_workplan_2026-07-20.md`](life_stage_iii_two_layer_workplan_2026-07-20.md) |
| Procedencia N2O de perfiles Tierra--Sol | [`earth_sun_n2o_matrix_provenance_2026-07-20.md`](earth_sun_n2o_matrix_provenance_2026-07-20.md) |
| Selección Tierra--Sol/Proxima | [`life_target_selection_2026-07-20.md`](life_target_selection_2026-07-20.md) |
| Ubicación de productos | [`repository_structure.md`](repository_structure.md) |