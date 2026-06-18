# Picos de contribución molecular neta en TRAPPIST-1e, 2026-06-17

Fecha de generación: `2026-06-17`.

## Propósito

Registrar un diagnóstico contrafactual de contribución molecular neta para los espectros de transmisión de ExoFarm en TRAPPIST-1e.

## Insumos

- Script: `Transmission_Spectroscopy/notebooks/plot_pure_transmission_spectra.py`
- Perfiles PT y químicos exportados en `Transmission_Spectroscopy/profiles/`
- Perfiles químicos contrafactuales derivados en `Transmission_Spectroscopy/profiles/counterfactual_A0_replacements/`
- Espectros forward POSEIDON calculados con la misma malla de presión, la misma grilla espectral y el mismo conjunto de opacidades que la figura principal

## Definición del contrafactual

Para cada escenario `A1`, `A2` y `A3`, y para cada molécula `N2O`, `NH3`, `H2O`, se recalcula un espectro forward manteniendo todo el escenario objetivo fijo excepto el perfil vertical de esa molécula, que se reemplaza por el perfil del escenario `A0`.

El reemplazo se materializa primero en archivos `*_reset_<mol>_to_A0_chem.txt`; esos archivos derivados son los que se cargan de nuevo con `read_chem_file` para construir los nueve espectros contrafactuales.

La curva neta exportada y graficada es:

```text
Net_mol(S) = Spectrum_full(S) - Spectrum_with_molecule_reset_to_A0(S)
```

Esto cuantifica el efecto espectral neto de la perturbación de esa molécula dentro del escenario completo. Es una prueba de necesidad contrafactual: cuánto cambia el espectro del escenario `S` si sólo esa molécula se devuelve a su perfil `A0` y el resto del escenario permanece fijo.

No es una descomposición estrictamente aditiva del residual total. Las bandas pueden solaparse y otras moléculas pueden reforzar o contrarrestar la señal neta, por lo que la suma de `Net_mol(S)` para `N2O`, `NH3` y `H2O` no tiene por qué reproducir `Spectrum_full(S) - Spectrum_full(A0)`.

## Trazabilidad de la figura oficial v2

La figura oficial de trabajo es `trappist1e_pure_a0_molecular_residuals_v2.{png,pdf}`. Tiene cuatro paneles:

- Panel superior: espectros puros de transmisión para `A0`, `A1`, `A2` y `A3`, con relleno entre cada escenario agrícola y `A0`.
- Paneles inferiores: señales moleculares netas para `N2O`, `NH3` y `H2O`. En cada panel se superpone el residual total `A_j - A0` como línea continua oscura, y se rellena la señal molecular contrafactual del mismo escenario.
- Las etiquetas superiores `N2O` y `NH3` son guías visuales ubicadas sobre regiones donde el diagnóstico contrafactual muestra picos relevantes; no son un ajuste espectroscópico independiente.

La figura se generó con el entorno Ubuntu/Conda `POSEIDON` desde `Transmission_Spectroscopy/notebooks/`, usando las variables de datos externas `POSEIDON_input_data` y `PYSYN_CDBS` apuntando a los directorios locales de opacidades y grillas estelares.

## Validación del reemplazo químico

Para evitar que la señal molecular fuera un artefacto de indexación, el script escribe primero perfiles químicos contrafactuales y luego los vuelve a leer con `read_chem_file`. La tabla `trappist1e_counterfactual_chemistry_validation.csv` registra, para cada combinación `(escenario, molécula)`, la columna reemplazada y varios errores máximos absolutos.

- `loaded_replaced_species_max_abs_error = 0.0` verifica que la especie reemplazada cargada desde disco coincide exactamente con el perfil `A0`.
- `loaded_other_species_max_abs_error = 0.0` verifica que las demás especies explícitas coinciden con el escenario objetivo.
- `loaded_total_max_abs_error = 0.0` verifica que el archivo contrafactual completo cargado por POSEIDON coincide con la composición esperada.
- `source_species_shift_max_abs` no es un error; mide cuánto difería la molécula entre el escenario objetivo y `A0` antes del reemplazo.

## Regla de picos

- Se usa la curva residual rebineada que se grafica en la figura final.
- Se seleccionan los `3` picos de mayor `|residual|` por combinación `(escenario, molécula)`.
- Se impone una separación mínima de `25` bins para evitar duplicar subestructura fina del mismo rasgo espectral.
- Se reporta el residual con signo y su valor absoluto.

## Estimación de S/N instrumental

Se añadió una estimación simple de S/N usando los archivos planos de ruido de `1` tránsito en `synthetic_data/base_1transit/`. Para cada pico se toma el punto instrumental más cercano dentro de la cobertura de `NIRSpec_PRISM` o `MIRI_LRS`. La incertidumbre se expresa en ppm y se escala como `sigma_N = sigma_1 / sqrt(N)` para `N = 1, 10, 100` tránsitos.

Los picos fuera de la cobertura `0.6-12 μm` de esta combinación NIRSpec Prism + MIRI LRS se marcan como `outside_coverage` y no reciben S/N.

## Resumen de picos

### A1

#### N2O

| Pico | Longitud de onda (μm) | Residual (ppm) | |Residual| (ppm) | Instrumento | σ 1 tránsito (ppm) | S/N 1 | S/N 10 | S/N 100 |
| ---: | ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: |
| 1 | 7.651 | 4.272 | 4.272 | MIRI_LRS | 468.67 | 0.009 | 0.029 | 0.091 |
| 2 | 16.972 | 3.220 | 3.220 | outside_coverage |  |  |  |  |
| 3 | 4.465 | 2.899 | 2.899 | NIRSpec_PRISM | 277.33 | 0.010 | 0.033 | 0.105 |

#### NH3

| Pico | Longitud de onda (μm) | Residual (ppm) | |Residual| (ppm) | Instrumento | σ 1 tránsito (ppm) | S/N 1 | S/N 10 | S/N 100 |
| ---: | ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: |
| 1 | 10.353 | 4.400 | 4.400 | MIRI_LRS | 1204.62 | 0.004 | 0.012 | 0.037 |
| 2 | 9.133 | 1.998 | 1.998 | MIRI_LRS | 691.72 | 0.003 | 0.009 | 0.029 |
| 3 | 11.999 | 0.996 | 0.996 | MIRI_LRS | 6698.89 | 0.000 | 0.000 | 0.001 |

#### H2O

| Pico | Longitud de onda (μm) | Residual (ppm) | |Residual| (ppm) | Instrumento | σ 1 tránsito (ppm) | S/N 1 | S/N 10 | S/N 100 |
| ---: | ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: |
| 1 | 5.469 | -0.001 | 0.001 | MIRI_LRS | 246.97 | 0.000 | 0.000 | 0.000 |
| 2 | 1.876 | -0.001 | 0.001 | NIRSpec_PRISM | 92.29 | 0.000 | 0.000 | 0.000 |
| 3 | 6.900 | -0.001 | 0.001 | MIRI_LRS | 374.33 | 0.000 | 0.000 | 0.000 |

### A2

#### N2O

| Pico | Longitud de onda (μm) | Residual (ppm) | |Residual| (ppm) | Instrumento | σ 1 tránsito (ppm) | S/N 1 | S/N 10 | S/N 100 |
| ---: | ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: |
| 1 | 8.641 | 6.745 | 6.745 | MIRI_LRS | 576.87 | 0.012 | 0.037 | 0.117 |
| 2 | 16.972 | 6.238 | 6.238 | outside_coverage |  |  |  |  |
| 3 | 4.465 | 6.098 | 6.098 | NIRSpec_PRISM | 277.33 | 0.022 | 0.070 | 0.220 |

#### NH3

| Pico | Longitud de onda (μm) | Residual (ppm) | |Residual| (ppm) | Instrumento | σ 1 tránsito (ppm) | S/N 1 | S/N 10 | S/N 100 |
| ---: | ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: |
| 1 | 10.742 | 8.319 | 8.319 | MIRI_LRS | 1732.66 | 0.005 | 0.015 | 0.048 |
| 2 | 9.476 | 3.288 | 3.288 | MIRI_LRS | 799.38 | 0.004 | 0.013 | 0.041 |
| 3 | 11.780 | 1.543 | 1.543 | MIRI_LRS | 4639.88 | 0.000 | 0.001 | 0.003 |

#### H2O

| Pico | Longitud de onda (μm) | Residual (ppm) | |Residual| (ppm) | Instrumento | σ 1 tránsito (ppm) | S/N 1 | S/N 10 | S/N 100 |
| ---: | ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: |
| 1 | 5.888 | 0.001 | 0.001 | MIRI_LRS | 255.75 | 0.000 | 0.000 | 0.000 |
| 2 | 1.904 | -0.001 | 0.001 | NIRSpec_PRISM | 88.83 | 0.000 | 0.000 | 0.000 |
| 3 | 1.346 | -0.001 | 0.001 | NIRSpec_PRISM | 77.62 | 0.000 | 0.000 | 0.000 |

### A3

#### N2O

| Pico | Longitud de onda (μm) | Residual (ppm) | |Residual| (ppm) | Instrumento | σ 1 tránsito (ppm) | S/N 1 | S/N 10 | S/N 100 |
| ---: | ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: |
| 1 | 8.641 | 18.954 | 18.954 | MIRI_LRS | 576.87 | 0.033 | 0.104 | 0.329 |
| 2 | 4.514 | 16.231 | 16.231 | NIRSpec_PRISM | 305.36 | 0.053 | 0.168 | 0.532 |
| 3 | 16.972 | 16.074 | 16.074 | outside_coverage |  |  |  |  |

#### NH3

| Pico | Longitud de onda (μm) | Residual (ppm) | |Residual| (ppm) | Instrumento | σ 1 tránsito (ppm) | S/N 1 | S/N 10 | S/N 100 |
| ---: | ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: |
| 1 | 10.742 | 18.976 | 18.976 | MIRI_LRS | 1732.66 | 0.011 | 0.035 | 0.110 |
| 2 | 9.688 | 5.267 | 5.267 | MIRI_LRS | 821.64 | 0.006 | 0.020 | 0.064 |
| 3 | 11.999 | 3.183 | 3.183 | MIRI_LRS | 6698.89 | 0.000 | 0.002 | 0.005 |

#### H2O

| Pico | Longitud de onda (μm) | Residual (ppm) | |Residual| (ppm) | Instrumento | σ 1 tránsito (ppm) | S/N 1 | S/N 10 | S/N 100 |
| ---: | ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: |
| 1 | 5.888 | -17.023 | 17.023 | MIRI_LRS | 255.75 | 0.067 | 0.210 | 0.666 |
| 2 | 6.577 | -15.966 | 15.966 | MIRI_LRS | 349.67 | 0.046 | 0.144 | 0.457 |
| 3 | 2.625 | -12.579 | 12.579 | NIRSpec_PRISM | 126.86 | 0.099 | 0.314 | 0.992 |

## Archivos conservados

- Figura principal v2: `Transmission_Spectroscopy/notebooks/POSEIDON_output/pure_spectra/plots/trappist1e_pure_a0_molecular_residuals_v2.png`
- Figura principal v2 PDF: `Transmission_Spectroscopy/notebooks/POSEIDON_output/pure_spectra/plots/trappist1e_pure_a0_molecular_residuals_v2.pdf`
- Tabla CSV: `Transmission_Spectroscopy/notebooks/POSEIDON_output/pure_spectra/plots/trappist1e_net_molecular_peak_summary.csv`

## Archivos regenerables de auditoría

El script puede volver a escribir los perfiles contrafactuales y la tabla de validación química cuando se ejecuta de nuevo. Estos productos no se conservan como artefactos finales porque son derivados exactos de los perfiles fuente y del código:

- Validación química regenerable: `Transmission_Spectroscopy/notebooks/POSEIDON_output/pure_spectra/plots/trappist1e_counterfactual_chemistry_validation.csv`
- Perfiles contrafactuales regenerables: `Transmission_Spectroscopy/profiles/counterfactual_A0_replacements/*_reset_<mol>_to_A0_chem.txt`
- Figura legacy regenerable con `--include-legacy-v1`: `Transmission_Spectroscopy/notebooks/POSEIDON_output/pure_spectra/plots/trappist1e_pure_a0_difference_mountains.{png,pdf}`
