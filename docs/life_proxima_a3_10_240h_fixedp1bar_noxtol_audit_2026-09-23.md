# Auditoría de retrievals Proxima A3 a 10 h y 240 h sin x_tol, 2026-09-23

## Pregunta y clasificación

Se repitieron únicamente los retrievals A3 de Proxima a 10 h y 240 h para
comprobar el efecto del modo heredado `fixed-bottom`, retirar x_tol y
desactivar la inflación de errores. Son productos de **auditoría excluidos de
la matriz canónica**. Los ocho retrievals A0--A3 × {10 h, 240 h} permanecen
intactos.

El par no cambia un solo factor frente al caso canónico. Cambian a la vez la
inflación de errores, la presión superficial libre, x_tol y N_live (de 200 a
800); por eso la diferencia no se puede atribuir exclusivamente a una de esas
decisiones.

## Configuración y procedencia

Ejecución en Ubuntu/WSL, conda POSEIDON: Python 3.10.13, POSEIDON 1.4.0 y
NumPy 1.26.4. La configuración fue X_profile=isochem, N_live=800,
evidence_tol=0.5, error_inflation=none, `surface=False` con malla que termina
en 1 bar, sin x_tol y sin log_P_surf recuperado. **Corrección metodológica
2026-09-23:** este modo no equivale a la superficie negra explícita de 1 bar
del forward generador; véase el
[diagnóstico de interfaz](life_proxima_a3_forward_swap_audit_2026-09-23.md).
POSEIDON modela F_p entre 3.8--19.0 um
a R=2000, con 31 bins LIFE y 13 parámetros libres.

Se reutilizaron los datasets LIFE de la matriz:

| Archivo | SHA-256 |
| --- | --- |
| life_data/LIFE_proxima_A3_10h.dat | 46A026504B9B9521FA29407A501169B9D3CFC433DE40A91B8ADE86D7767ABB5B |
| life_data/LIFE_proxima_A3_240h.dat | 7F04734252BE9B8428EA13288D65471F861A23815723616B363B48B27EFADD7B |

Ejemplo del comando de 240 h (para 10 h se cambia únicamente --hours):

```bash
export POSEIDON_input_data=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs
export PYSYN_CDBS=/mnt/d/Proyectos/IA_SpecAtm_Bio/Data/POSEIDON/inputs/stellar_grids
/home/dasan/anaconda3/envs/POSEIDON/bin/python \
  /mnt/c/Proyectos/Astro/ExoFarm_MDwarfs/Thermal_Emission_Spectroscopy/scripts/run_life_retrieval.py \
  --campaign proxima --scenario A3 --hours 240 --n-live 800 \
  --error-inflation none --surface-pressure-mode fixed-bottom \
  --output-tag _fixedP1bar_noxtol
```

El sufijo separa estos productos de la matriz canónica. La salida POSEIDON
está en
Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/POSEIDON_output/proxima_b_earthlike/retrievals/.

## Resultados

La comparación de las posteriores canónicas y de auditoría para `N2O` y `NH3`,
con la abundancia efectiva A0 marcada y `chi^2_red` por tiempo, está en
[`retrieval_A3_molecular_posteriors_audit_comparison_proxima.png`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A3_molecular_posteriors_audit_comparison_proxima.png)
([PDF](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/retrieval_A3_molecular_posteriors_audit_comparison_proxima.pdf)).
La figura se reproduce con
[`plot_proxima_a3_molecular_posteriors.py`](../Thermal_Emission_Spectroscopy/scripts/plot_proxima_a3_molecular_posteriors.py)
y conserva clasificación de auditoría: no reemplaza el atlas canónico.

Los intervalos son las restricciones de 1 sigma reportadas por POSEIDON. Los
valores canónicos se incluyen como referencia de configuración; sus likelihoods
y priors no son idénticos a los de esta auditoría.

| Integración y variante | Parámetros / dof | ln Z | chi^2_red (chi^2) | R_p_ref (R_E) | log_N2O | log_NH3 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 h, canónica: Piette20, x_tol y P_surf libres, N_live=200 | 15 / 16 | 877.94 +/- 0.45 | 1.61 (25.74) | 1.25 +/- 0.02 | -6.50 (+0.31/-0.52) | -9.30 (+1.29/-1.48) |
| 10 h, auditoría: sin inflación, surface=False, sin x_tol, N_live=800 | 13 / 18 | 888.98 +/- 0.21 | 1.43 (25.81) | 1.22 +/- 0.02 | -6.49 (+0.24/-0.33) | -9.09 (+0.97/-1.83) |
| 240 h, canónica: Piette20, x_tol y P_surf libres, N_live=200 | 15 / 16 | 894.44 +/- 0.43 | 2.28 (36.44) | 1.20 (+0.02/-0.02) | -6.19 (+0.24/-0.21) | -9.49 (+1.46/-1.63) |
| 240 h, auditoría: sin inflación, surface=False, sin x_tol, N_live=800 | 13 / 18 | 816.05 +/- 0.25 | 13.07 (235.24) | 1.213 (+0.004/-0.004) | -6.39 (+0.04/-0.05) | -9.61 (+0.87/-1.59) |

Los ln Z de configuraciones con distinto número de parámetros, priors e
incertidumbres no son una prueba comparativa de modelo. El ajuste de 10 h es
razonable; a 240 h, sin inflación de errores, el ajuste es muy deficiente
(chi^2_red=13.07). La precisión aparente de R_p_ref y log_N2O no compensa ese
desajuste.

## Contraste con la referencia A0 efectiva

Para comparar una abundancia isquímica constante con la verdad vertical VULCAN
se usa el promedio columnar ponderado en presión:

```text
X_A0,eff = integral X_A0(p) dp / (p_bottom - p_top).
```

Aplicado a Transmission_Spectroscopy/profiles/Proxima_b_A0_PreAgri_chem.txt,
da log10(N2O_A0,eff)=-6.884 y log10(NH3_A0,eff)=-9.951. La función de
referencia del proyecto mantiene la misma integral, prioriza np.trapezoid
cuando existe y usa np.trapz con el NumPy 1.26.4 del entorno POSEIDON.

| Tiempo | Especie | Mediana A3 (log10 VMR) | Intervalo 1 sigma | A0 efectiva | Delta A3--A0 |
| ---: | --- | ---: | ---: | ---: | ---: |
| 10 h | N2O | -6.495 | [-6.824, -6.260] | -6.884 | +0.390 dex |
| 10 h | NH3 | -9.082 | [-10.912, -8.125] | -9.951 | +0.868 dex |
| 240 h | N2O | -6.393 | [-6.440, -6.351] | -6.884 | +0.492 dex |
| 240 h | NH3 | -9.577 | [-11.186, -8.736] | -9.951 | +0.374 dex |

**Interpretación:** a 10 h, N2O queda modestamente separado de A0 y NH3 conserva
un intervalo ancho que incluye A0. A 240 h el posterior isquímico de N2O se
estrecha y se desplaza sobre A0, mientras NH3 sigue siendo amplio. Ese
estrechamiento de N2O no es una detección defendible: el modelo describe mal
los datos con las incertidumbres sin inflar. Se interpreta como tensión entre
el modelo y la precisión formal del dataset, no como una abundancia medida con
precisión.

El S/N integrado de una plantilla molecular evalúa la amplitud de una señal
contrafactual sobre bins LIFE con ruido diagonal. El retrieval también ajusta
radio, perfil térmico y otras abundancias, y representa perfiles verticales con
abundancias isquímicas. Un S/N alto no garantiza que ese modelo ajuste los
datos. Además, cada resultado usa una sola realización de ruido y Proxima es un
análogo terrestre controlado, no la atmósfera medida de Proxima b.

## Integridad y completitud

Se verificaron para ambos tiempos el archivo de resultados, las muestras
posteriores, el espectro recuperado, perfiles P--T y log_X, además de los
archivos MultiNest de evidencia, muestras equiponderadas y puntos vivos. Las
muestras tienen 13 columnas y 7,021 filas para 10 h, y 13 columnas y 7,470
filas para 240 h. Cada conjunto conserva 800 puntos vivos. No se encontraron
tokens NaN/Inf en esos productos.

MultiNest termina con Sampling finished; para 240 h reporta 2,916,081
evaluaciones y ln(ev)=816.05457 +/- 0.25255. El proceso POSEIDON ya no está
activo y existen los resultados, las muestras y el espectro posterior. El
lanzamiento desacoplado no conservó un código de salida del shell; la
completitud se acepta a partir del cierre de MultiNest y la integridad de los
productos finales.

## Decisión de uso

- Mantener ambos runs como auditoría separada; no reemplazan A3 canónico ni
  cambian la matriz 8/8.
- Usar el caso de 240 h como evidencia de que eliminar conjuntamente x_tol e
  inflación de errores deja expuesto un desajuste severo. Esta corrida no
  permite aislar cuál de los cambios lo causa.
- No declarar detección de N2O o NH3. Para resolver el desajuste se deben
  revisar residuos por bin y el perfil vertical frente a isochem; cualquier
  conclusión instrumental también requiere LIFEsimMC/PHRINGE, covarianza y
  múltiples realizaciones.

## Archivos principales

- Script: Thermal_Emission_Spectroscopy/scripts/run_life_retrieval.py.
- Resultados, muestras y productos MultiNest: subcarpetas results/, samples/ y
  MultiNest_raw/ en la salida POSEIDON indicada arriba.
- Log 240 h: Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/proxima_A3_240h_fixedP1bar_noxtol.launch.log.
- PID registrado: Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/proxima_A3_240h_fixedP1bar_noxtol.pid (el proceso terminó).
