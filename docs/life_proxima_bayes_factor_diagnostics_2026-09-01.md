# Diagnósticos de Bayes factor para Proxima A3 a 240 h, 2026-09-01

## Pregunta y clasificación

Se evaluaron dos comparaciones sobre el mismo dataset sintético de Proxima
A3 a 240 h:

1. el modelo atmosférico completo A3 frente al modelo completo A0;
2. el modelo completo A3 frente al mismo A3 con el perfil de N2O reiniciado al
   perfil A0.

El producto queda clasificado como **experimento de auditoría/diagnóstico de
plantillas fijas**. No amplía la matriz canónica de ocho retrievals, no
reemplaza una evidencia marginalizada con nuisance parameters y no constituye
una detección instrumental de LIFE.

## Entrada y procedencia

El dataset común fue:

- [`LIFE_proxima_A3_240h.dat`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A3_240h.dat);
- 31 bins, observable `Fp` en `W m^-2 m^-1`;
- una realización de ruido diagonal de LIFEsim clásico.

Las plantillas se tomaron de los forwards y del contrafactual molecular
existentes:

- [`A0_emission.npz`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/forward_emission/A0_emission.npz);
- [`A3_emission.npz`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/forward_emission/A3_emission.npz);
- [`A3_reset_N2O_Fp_obs.npz`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/molecular_diagnostics/A3_reset_N2O_Fp_obs.npz).

El contrafactual no elimina todo el N2O: conserva la estructura A3 restante y
reemplaza únicamente el perfil de N2O por el de A0. Por tanto, el segundo
diagnóstico mide el soporte del **exceso de N2O de A3**, no una hipótesis de
opacidad exactamente nula.

## Método

El script [`evaluate_life_bayes_factor_diagnostics.py`](../Thermal_Emission_Spectroscopy/scripts/evaluate_life_bayes_factor_diagnostics.py)
reproduce la conversión usada por el generador de datasets:

```text
Fp [W m^-2 m^-1] -> flujo de fotones -> rebin a los bins LIFE -> Fp energético
```

La likelihood diagonal usada para cada plantilla es:

```text
ln L = -1/2 sum_i [ ((D_i - F_i)/sigma_i)^2
                    + ln(2 pi sigma_i^2) ]
```

Como las plantillas son fijas y las dos hipótesis comparten la normalización
gaussiana, en este diagnóstico:

```text
ln B_10 = ln Z_1 - ln Z_0 = ln L_1 - ln L_0
```

Esto es un Bayes factor de modelos deterministas con parámetros libres nulos.
No integra radio, perfil PT, abundancias, `x_tol` ni otros parámetros nuisance.

La comprobación de la interfaz fue satisfactoria: al usar la malla LIFE de
precisión completa, el rebin del forward A3 reproduce el producto LIFE
guardado con un error relativo máximo de `6.77e-15`. Las longitudes de onda
escritas en el `.dat` están redondeadas a seis cifras, con una diferencia
máxima de `4.60e-6 um` respecto a la malla interna.

## Resultados

| Diagnóstico | `chi2` preferido | `chi2` referencia | `Delta chi2` | `ln B` | `log10 B` | `B` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A3 frente a A0 | 27.626 | 816.327 | 788.701 | 394.351 | 171.264 | `1.84e171` |
| A3 con N2O frente a N2O reiniciado a A0 | 27.626 | 798.892 | 771.266 | 385.633 | 167.478 | `3.01e167` |

Las likelihoods logarítmicas fueron `976.561` para A3, `582.210` para A0 y
`590.928` para el contrafactual de N2O reiniciado.

## Interpretación

En esta realización de ruido y con plantillas completamente fijas, el dataset
favorece fuertemente A3 frente a A0. También favorece fuertemente la
presencia del exceso de N2O de A3 frente a reiniciarlo al perfil A0. La
segunda comparación es la más directamente relacionada con la contribución
molecular de N2O.

Los valores son mucho más extremos que la separación de `3.14 sigma` del
retrieval porque las plantillas fijas no pueden reajustar el radio, el perfil
térmico, las abundancias ni `x_tol`. Por eso no deben presentarse como una
conversión de `3.14 sigma` a Bayes factor ni como una significancia instrumental
final. Son un diagnóstico de discriminación idealizada bajo el benchmark
clásico.

## Qué falta para la comparación formal

La siguiente versión debe usar el mismo dataset A3--240 h y dos modelos
POSEIDON/MultiNest con parámetros nuisance comunes, priors emparejados y
evidencias marginalizadas:

```text
ln B_A3,A0 = ln Z(D_A3 | M_A3) - ln Z(D_A3 | M_A0)
```

Conviene repetir después el contraste sobre el dataset A0 para medir falsos
positivos y usar varias semillas. La comparación instrumental final requiere
además covarianza e inestabilidad de LIFEsimMC/PHRINGE. El resultado actual
permanece, por tanto, fuera de los claims canónicos.

## Reproducción

Desde WSL/Ubuntu en el entorno `POSEIDON`:

```bash
cd /mnt/c/Proyetos/Repos/ExoFarm_MDwarfs/Thermal_Emission_Spectroscopy/scripts
source /home/wsldasan/miniconda3/etc/profile.d/conda.sh
conda activate POSEIDON
python evaluate_life_bayes_factor_diagnostics.py
```

Productos tabulares:

- [`life_bayes_factor_diagnostics_A3_240h.csv`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/life_bayes_factor_diagnostics_A3_240h.csv);
- [`life_bayes_factor_diagnostics_A3_240h.json`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/life_bayes_factor_diagnostics_A3_240h.json).

