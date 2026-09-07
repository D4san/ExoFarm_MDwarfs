# Auditoría del retrieval Proxima A3 a 500 h, 2026-08-31

> **Actualización posterior, 2026-08-31:** el retrieval se lanzó antes de
> instalar LIFEsim en el entorno WSL. Después se generó una observación directa
> con LIFEsim 0.2.32 y SpectRes 2.1.1; el `.dat` usado por esta corrida coincide
> byte a byte con el producto directo. La procedencia numérica queda, por tanto,
> confirmada sin repetir MultiNest. El detalle de instalación y comparación
> está en [`validación directa de LIFEsim`](life_proxima_a3_500h_lifesim_direct_validation_2026-08-31.md).

## Pregunta y clasificación

Se ejecutó un retrieval intermedio de `A3` a 500 h para comprobar si la
configuración corregida de POSEIDON permanece estable entre los casos canónicos
de 10 h y 240 h y el piloto problemático de 1200 h. Es un **piloto de
auditoría**, no una ampliación de la matriz científica oficial y no debe
interpretarse como una detección.

La matriz canónica permanece sin cambios:

```text
Proxima A0--A3 x {10 h, 240 h}
```

## Entorno y dependencias verificadas

La corrida se lanzó desde Ubuntu/WSL, en el entorno conda `POSEIDON`:

```text
conda root: /home/wsldasan/miniconda3
environment: /home/wsldasan/miniconda3/envs/POSEIDON
POSEIDON_input_data: /home/wsldasan/POSEIDON/inputs
PYSYN_CDBS: /home/wsldasan/POSEIDON/inputs/stellar_grids
```

En la primera ejecución se verificó la importación de POSEIDON 1.4.0,
`pymultinest` 2.12, MultiNest 3.10, `spectres` 2.2.2 y `astropy` 7.2.1. En
ese momento el paquete `lifesim` no estaba instalado en este entorno. Por ello,
el dataset usado originalmente por el retrieval se construyó desde los bins
LIFEsim clásicos validados usando el escalado auditado de incertidumbre

```text
sigma(t) = sigma(10 h) * sqrt(10 / t)
```

El retrieval de POSEIDON no requiere importar `lifesim`; consumió el archivo
`.dat` ya generado con `Fp` y sus incertidumbres diagonales. La validación
posterior con una observación directa está separada en el [informe de
validación directa](life_proxima_a3_500h_lifesim_direct_validation_2026-08-31.md).

## Dataset de entrada

El dataset se generó sin sobrescribir el índice canónico:

- índice de auditoría:
  [`dataset_index_500h_audit.json`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/dataset_index_500h_audit.json);
- datos:
  [`LIFE_proxima_A3_500h.dat`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A3_500h.dat);
- semilla maestra: `20260831`;
- semilla derivada del dataset: `737920415`;
- bins: `31`;
- S/N mediano del continuo: `332.02`.

La etiqueta del índice deja explícito que el producto está excluido de la
matriz canónica.

## Configuración del retrieval

Se usó `run_life_retrieval.py` con:

- escenario `A3`, integración `500 h`, 200 puntos vivos de MultiNest;
- emisión directa, observable `Fp`, `3.8--19.0 um`, `R=2000`;
- perfil PT `Madhu` y abundancias constantes con altura (`isochem`);
- inflación fraccional de errores `Piette20`;
- prior de `R_p_ref` expresado en metros antes de la conversión interna de
  POSEIDON, con el radio planetario recuperado en `R_E`;
- 15 parámetros libres.

La corrección del prior de radio es esencial: el piloto antiguo de 1200 h
dividía el radio por la unidad dos veces y terminó con un radio no físico. Esta
corrida usa el rango físico corregido `[0.8, 1.3] R_p` en la entrada esperada
por POSEIDON.

## Resultado directo

MultiNest terminó normalmente después de 43 893 evaluaciones:

```text
ln Z = 893.18 +/- 0.40
chi^2_red = 1.59  (16 grados de libertad; chi^2 = 25.38)
```

El archivo de resultados informa:

```text
R_p_ref = 1.23 (+0.03) (-0.02) R_E
x_tol   = 0.05 (+0.02) (-0.01)
log_N2O = -6.24 (+0.36) (-0.45)
log_NH3 = -9.20 (+1.45) (-1.55)
```

La muestra posterior contiene 2 822 filas finitas. El promedio columnar
ponderado en presión usado como referencia A0 da
`log10(X_N2O,A0,eff) = -6.88`; la separación de la mediana A3 frente a esa
referencia es aproximadamente `+1.6 sigma` en esta realización de 500 h.
Para `NH3`, la posterior sigue siendo ancha y no permite una discriminación
limpia.

El resultado es computacionalmente estable y el radio es físico. Esto contrasta
con el piloto de 1200 h, que se conserva como evidencia excluida por su
terminación patológica y su radio espurio. La estabilidad de 500 h no convierte
el experimento en una detección: el dataset usa sigma diagonal, una única
realización de ruido y un modelo de retrieval isquímico más simple que los
perfiles verticales VULCAN.

## Productos

Los archivos producidos por POSEIDON están bajo:

[`retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/)

Incluyen el resumen de resultados, muestras posteriores, espectro recuperado,
perfil PT, perfiles de abundancia y los archivos crudos de MultiNest con el
prefijo `proxima_A3_500h_proxima_A3_500h`.

Se generó además una vista de inspección, no oficial:

[`retrieval_profiles_posteriors_proxima_A3_500h_audit.png`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/audit/retrieval_profiles_posteriors_proxima_A3_500h_audit.png)

La figura sirve para revisar la forma de la posterior junto al perfil VULCAN
de A3 y la referencia A0 efectiva; no se incorpora al atlas oficial de 10/240 h.

## Qué queda pendiente

Este piloto no resuelve las limitaciones inferenciales de la rama clásica. Para
una afirmación instrumental o una detección estadística todavía hacen falta
LIFEsimMC/PHRINGE con covarianza, varias realizaciones de ruido y comparación de
modelos con y sin `N2O`/`NH3`. Si se desea una comparación formal adicional,
deberá registrarse como una nueva campaña y decidirse explícitamente si se
generan también `A0` y controles con la misma realización y configuración.
