# Diagnóstico de interfaz del forward LIFE Proxima A3 (2026-09-23)

## Pregunta y alcance

Los retrievals A3 de auditoría a 100 y 240 h (`isochem`, `N_live=800`, sin
inflación) dejan residuos coherentes y sus distancias posteriores respecto de
A0 efectiva se vuelven difíciles de interpretar. Esta prueba identifica
diferencias verificables entre el **forward que generó los datos** y la
configuración usada para recuperarlos. No ejecuta MultiNest, no cambia los
datasets ni modifica la matriz canónica 8/8.

## Implementación y validación

El [script de forwards controlados](../Thermal_Emission_Spectroscopy/scripts/diagnose_proxima_a3_forward_swaps.py)
se ejecutó en Ubuntu con `/home/dasan/anaconda3/envs/POSEIDON/bin/python`,
`POSEIDON_input_data=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs` y
`PYSYN_CDBS=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids`.
Reutiliza el [forward A3 guardado](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/forward_emission/A3_emission.npz),
la PT/química VULCAN A3, el radio verdadero, las muestras y perfiles
posteriores, y las `sigma` de los datasets LIFE de 100 y 240 h. Calcula
`Fp_obs` en la rejilla original de 18 971 longitudes de onda, integra la
densidad de fotones en los 31 bins LIFE y reconvierte a `W m^-2 m^-1`.
El forward original con siete especies y superficie explícita se reprodujo
**exactamente** (error relativo máximo `0.0`).

El forward generador incluye `N2`, `H2O`, `CO2`, `CH4`, **`O2`**, `O3`, `N2O`
y `NH3` y define `surface=True` con `P_surf=1 bar`. El archivo VULCAN A3
contiene `O2=0.2002647` en la capa de 1 bar. El retrieval usa seis especies
parametrizadas (`H2O`, `CO2`, `CH4`, `O3`, `N2O`, `NH3`) y, en el modo de
auditoría `fixed-bottom`, establece `surface=False`. Al omitir O2, el N2
de relleno y la mezcla de opacidades/CIA también cambian. POSEIDON 1.4.0
define la superficie mediante `P_surf` en `compute_spectrum`; si este es
`None`, desactiva la superficie y asigna internamente `P_surf=100 bar` como
valor auxiliar (`POSEIDON/core.py`, líneas 1502--1507 del entorno usado).
La malla atmosférica termina en 1 bar, pero eso **no equivale** a un cuerpo
negro superficial explícito allí. La afirmación previa de equivalencia en
[`run_life_retrieval.py`](../Thermal_Emission_Spectroscopy/scripts/run_life_retrieval.py)
era incorrecta; se corrigió su documentación y mensaje de ejecución sin
alterar la conducta ni los retrievals existentes. El nombre del sufijo
`_fixedP1bar_noxtol` se conserva únicamente por trazabilidad histórica.

Para cada variante `v` se informa
`D_v(t)=sum_k[(Fp_A3,true,k-Fp_v,k)/sigma_k(t)]²`. Es una **distancia espectral
cuadrática frente al forward sin ruido**, no el chi-cuadrado de una solución
ajustada ni una significancia de detección. Los valores a 240 h escalan por
2.4 respecto de 100 h porque las `sigma` siguen `t^(-1/2)`. En la tabla,
«7/6 especies» cuenta las parametrizadas; N2 es la especie de fondo adicional.

| Perfiles PT/química y radio | Especies | Superficie explícita | D(100 h) | D(240 h) |
| --- | --- | --- | ---: | ---: |
| VULCAN A3 verdadero | 7, con O2 | Sí, 1 bar | 0.00 | 0.00 |
| VULCAN A3 verdadero | 7, con O2 | No (`surface=False`) | 293.31 | 703.95 |
| VULCAN A3 verdadero | 6, sin O2 | Sí, 1 bar | 684.76 | 1643.43 |
| VULCAN A3 verdadero | 6, sin O2 | No (`surface=False`) | 218.30 | 523.93 |
| Medianas marginales PT/química/radio recuperadas | 6, sin O2 | No | 221.47 | 459.15 |

La variante de seis especies con superficie y la de siete sin superficie
producen desplazamientos de signos opuestos en buena parte del infrarrojo
medio; por eso el valor relativamente menor de `D` para seis especies sin
superficie refleja **cancelación**, no una equivalencia física con el
forward de entrada. El cambio `surface=True` → `False` dentro del modelo
de seis especies altera el flujo nativo hasta `3.89 %`. Las opacidades leídas
para el modelo completo incluyen pares O2--O2, O2--CO2 y O2--N2.

Los intercambios adicionales de PT, abundancias y radio, uno o dos a la vez,
se incluyen en el [resumen CSV](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/forward_swap_audit/forward_swap_summary.csv).
Por ejemplo, al partir del vector de medianas marginales a 100 h, sustituir
solo PT por el perfil verdadero da `D=850.36`, sustituir solo abundancias
`D=324.59`, y sustituir solo radio `D=442.79`. Su falta de mejora monótona
demuestra compensación entre parámetros: estos `D` **no** son contribuciones
aditivas de error ni permiten culpar a un único perfil.

## Relación con los residuos del retrieval

La [figura comparativa](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/forward_swap_audit/forward_swap_residuals.png)
se inspeccionó visualmente. El residuo de la mediana espectral posterior
frente al forward verdadero tiene `D=113.60` (100 h) y `230.27` (240 h),
según la [auditoría de residuos](life_proxima_a3_retrieval_residuals_2026-09-23.md).
El espectro obtenido con el **vector de medianas marginales** difiere a su
vez de la mediana espectral punto a punto en `sum(Delta/sigma)^2=59.82`
y `160.59`. Son objetos distintos; no se debe sustituir uno por otro para
reportar calidad de ajuste. Los patrones de la variante verdadera con seis
especies y sin superficie tienen correlación `-0.11` y `-0.25` con los
residuos de la mediana espectral posterior. El retrieval compensa en gran
parte las diferencias estructurales, de modo que la prueba **identifica una
interfaz incorrecta y una fuente plausible de sesgo**, pero no demuestra
que sea la única causa de los residuos finales ni descarta el desajuste de PT
o `isochem`.

## Decisión científica

Las cifras `z` A3--A0 efectiva obtenidas con estas auditorías no deben usarse
para la afirmación propuesta de cuántas horas distinguen N2O/NH3. Antes de
repetir retrievals, conviene construir y probar una configuración que conserve
la superficie negra **explícita** en 1 bar y O2 en la base química, y que
reproduzca el forward A3 en el límite de perfiles verdaderos. Después se puede
examinar el residuo que deja una PT parametrizada y una química isquímica,
manteniendo igual dataset y likelihood. La opción `fixed-bottom` existente no
se debe reinterpretar retrospectivamente como esa configuración corregida.
La matriz canónica usa superficie explícita con presión libre, pero comparte
la omisión de O2 en las especies del retrieval: su posterior queda como
resultado condicional a esa elección hasta una comprobación consistente.
Siguen vigentes las salvedades de LIFEsim clásico: ruido diagonal, una
realización por tiempo y ausencia de inestabilidad instrumental/covarianza.

## Productos

- [Resumen JSON](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/forward_swap_audit/forward_swap_summary.json)
  y [CSV](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/forward_swap_audit/forward_swap_summary.csv).
- [Diferencias por bin CSV](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/forward_swap_audit/forward_swap_bins.csv)
  y [figura PNG](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/forward_swap_audit/forward_swap_residuals.png).
- [Código del retrieval auditado](../Thermal_Emission_Spectroscopy/scripts/run_life_retrieval.py),
  [código del forward generador](../Thermal_Emission_Spectroscopy/scripts/emission_forward.py),
  [auditoría de 100 h](life_proxima_a3_100h_fixedp1bar_noxtol_audit_2026-09-23.md)
  y [auditoría de 10/240 h](life_proxima_a3_10_240h_fixedp1bar_noxtol_audit_2026-09-23.md).
