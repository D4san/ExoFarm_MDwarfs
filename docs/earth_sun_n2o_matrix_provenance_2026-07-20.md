# Procedencia de la matriz Tierra--Sol de N2O para la Etapa III

**Fecha de revisión:** 2026-07-20
**Estado:** salvedad abierta de procedencia; no altera ni invalida los perfiles
aceptados, pero limita cómo se pueden usar en la Etapa III.

## Por qué existe esta nota

La Capa 1 de LIFE, `life_earth_sun_10pc`, reutiliza los cuatro perfiles
Tierra--Sol guardados el 2026-06-15. Al reconstruir su procedencia se encontró
que los perfiles A2 y A3 fueron producidos con una versión anterior de los
flujos de frontera de `N2O`, mientras que la configuración activa de VULCAN
ahora contiene la corrección que hace exactos los multiplicadores declarados.

Esta nota separa hechos observables de la decisión operativa para que un chat
nuevo no mezcle una configuración actual con perfiles que no se generaron con
ella.

## Evidencia de archivos

| Elemento | Ruta / valor | Tipo de evidencia |
| --- | --- | --- |
| Perfiles que consume la Capa 1 | `Photochemical_Modeling/Results/Outputs/Earth_A{0,1,2,3}_*.vul`; fecha de modificación 2026-06-15 | Producto aceptado |
| Snapshot A2 de la reproducción | `Photochemical_Modeling/Results/Reproduction_2026-06-15/before/bc_earth_exofarm_moderate_full.txt`: `N2O = 3.35e9` | Configuración histórica |
| Snapshot A3 de la reproducción | `Photochemical_Modeling/Results/Reproduction_2026-06-15/before/bc_earth_exofarm_full.txt`: `N2O = 1.20e10` | Configuración histórica |
| BC activo A2 | `Photochemical_Modeling/Config/Boundary_Conditions/bc_earth_exofarm_moderate_full.txt`: `N2O = 3.416e9` | Configuración actual |
| BC activo A3 | `Photochemical_Modeling/Config/Boundary_Conditions/bc_earth_exofarm_full.txt`: `N2O = 1.238e10` | Configuración actual |

El runner vigente `Photochemical_Modeling/Scripts/Simulation/run_parallel_earth.py`
copia estos BC activos a `atm/BC_bot_Earth.txt` antes de cada corrida. Los YAML
de Earth--Sun apuntan a ese archivo staged; por tanto, una nueva corrida usa
los valores corregidos, aunque conserve el mismo nombre de salida.

## Interpretación de la corrección

Con `F_N2O(A0) = 1.58e9` y `F_N2O(A1) = 2.30e9` moléculas cm^-2 s^-1,
`Delta F_N2O,agri = 0.72e9`. La ecuación activa del proyecto,

```text
F_i(A_j) = F_i(A0) + alpha_i,j * Delta F_i,agri
```

da `3.416e9` para A2 (`alpha = 2.55`) y `1.238e10` para A3
(`alpha = 15`). Los valores de los snapshots de junio implican aproximadamente
2.46 y 14.47, respectivamente. La auditoría histórica que detectó el problema
es [`scientific_audit_2026-07-01.md`](scientific_audit_2026-07-01.md).

## Regla operativa para recuperar el trabajo

1. Los perfiles `Earth_A0`--`Earth_A3` de 2026-06-15 siguen siendo un
   **benchmark congelado y aceptado** para validar la interfaz
   POSEIDON--LIFEsimMC/PHRINGE: lectura de perfiles, emisión, unidades,
   radiancia, malla y tratamiento de covarianza.
2. Etiquetar cualquier producto derivado de ellos como
   **`earth_20260615_pre_n2o_correction`** en su manifiesto y figuras/tablas.
   Nunca combinarlo con la tabla de BC corregidos como si fueran el mismo
   experimento.
3. Antes de presentar comparaciones A0--A3, SNR o retrievals LIFE como el
   resultado de la **matriz ExoFarm vigente**, decidir y documentar una de dos
   rutas: (a) regenerar/reexportar Tierra--Sol A0--A3 con los BC actuales y
   revalidar los perfiles; o (b) aprobar explícitamente el benchmark de junio
   como una matriz histórica, conservando el rótulo pre-corrección en todo
   producto científico.
4. La Capa 2 de Proxima no hereda este problema si nace directamente de los BC
   activos; aun así, su manifiesto debe registrar checksums de los BC usados.

La siguiente acción LIFE sigue siendo una auditoría no destructiva de entorno e
interfaz. No autoriza correr VULCAN, LIFEsimMC/PHRINGE ni retrievals.

## Documentos que deben leerse junto con esta nota

- [Punto de entrada de reanudación](project_resume.md)
- [Tracker de estado y backlog](project_status_tracker.md)
- [Plan operativo de dos capas](life_stage_iii_two_layer_workplan_2026-07-20.md)
- [Metodología de perfiles fotoquímicos](photochemical_profiles_methodology.md)
