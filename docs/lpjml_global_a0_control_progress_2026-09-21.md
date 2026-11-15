# Progreso del control natural A0 de LPJmL (2026-09-21)

## Estado vivo

La campaña `global_a1_checkpoints_20260909` está ejecutando el control natural
`a0_natural` en Ubuntu, sobre el disco E:, con ocho ranks MPI y el build local
`LPJmL-6.0.6-balance-fix-20260912`. La corrida conserva la misma malla, el
reinicio natural aceptado y el periodo de salida 1996--2005 que A1. La
configuración desactiva `landuse`, población, fertilizante, estiércol,
irrigación, uso de agua y routing, y guarda `n2o_nit`, `n2o_denit` y
`n_volatilization` como flujos naturales totales.

El primer lanzamiento comenzó el 2026-09-20 a las 20:05:41 UTC. El proceso
desapareció después de escribir el segmento que llegó al año 1587; no hubo
`ERROR_CODES` en el stderr del controlador ni mensaje de error de LPJmL. El
último checkpoint activo y archivado es:

```text
a0_natural/checkpoints/1789938392320082500.lpj
sha256=4c6dfe69fd019922380ab6196ba52572365734b44219f2d3db64298387149b7c
```

El SHA-256 del archivo archivado coincide con
`a0_natural/restart/checkpoint.lpj`. La ausencia de procesos y el indicador
`A0_RUNNING` sin cierre se clasifican como una interrupción externa del entorno
WSL, no como una finalización científica ni como un error de balance. La
reanudación se lanzó de forma independiente el 2026-09-21 a las 00:30:24 UTC;
el segmento nuevo lee explícitamente `restart/checkpoint.lpj` y hay ocho
procesos LPJmL activos.

## Próximo control

Se esperará a la terminación normal y se validarán dimensiones, máscaras,
finitud, unidades mensuales (`gN m-2 month-1`) y cobertura 1996--2005. Después
se sumarán los meses por año, se integrará por `land_area` y se convertirán los
flujos a `TgN/año` y moléculas `cm-2 s-1`. La comparación A0--A1 seguirá siendo
diagnóstica hasta confirmar que las fronteras de las dos salidas son
comparables; no se ejecutará VULCAN durante esta etapa.
