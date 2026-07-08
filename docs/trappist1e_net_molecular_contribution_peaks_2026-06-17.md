# Picos de contribución molecular neta en TRAPPIST-1e, 2026-06-17

Fecha de generación: `2026-07-02`.

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
- Se definen ventanas espectrales por molécula y se reporta el máximo de `|signal|` dentro de cada ventana.
- Esto evita que un pico global fuera de la región interpretativa domine el resumen de una molécula.
- Se reporta la señal molecular con signo, su valor absoluto, el identificador de ventana y los límites usados.

## Estimación de S/N instrumental

Se añadió una estimación simple de S/N usando los archivos planos de ruido de `1` tránsito en `synthetic_data/base_1transit/`. Los archivos planos almacenan `depth` y `depth_err` como profundidad de tránsito adimensional, es decir `(R_p/R_s)^2`. Para comparar con la figura, tanto la señal molecular como el ruido se expresan en ppm de `(R_p/R_s)^2`: `signal_ppm = signal_(Rp/Rs)^2 * 1e6` y `sigma_1transit_ppm = depth_err * 1e6`. Por tanto, el S/N exportado es adimensional.

Para cada pico se toma el punto instrumental más cercano dentro de la cobertura de `NIRSpec_PRISM` o `MIRI_LRS`. La incertidumbre se escala como `sigma_N = sigma_1 / sqrt(N)` para `N = 1, 10, 100` tránsitos, y el cociente reportado es `S/N_N = |signal_ppm| / sigma_N`.

Los picos fuera de la cobertura `0.6-12 μm` de esta combinación NIRSpec Prism + MIRI LRS se marcan como `outside_coverage` y no reciben S/N.

## Resumen de picos

### A1

#### N2O

| Ventana | Rango (μm) | Pico (μm) | Signal (ppm) | |Signal| (ppm) | Instrumento | σ 1 tránsito (ppm) | S/N 1 | S/N 10 | S/N 100 |
| :--- | :--- | ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: |
| N2O_2p6_3p0 | 2.60-3.00 | 2.857 | 2.214 | 2.214 | NIRSpec_PRISM | 152.86 | 0.014 | 0.046 | 0.145 |
| N2O_4p3_4p8 | 4.30-4.80 | 4.465 | 2.539 | 2.539 | NIRSpec_PRISM | 277.33 | 0.009 | 0.029 | 0.092 |
| N2O_7p5_9p0 | 7.50-9.00 | 8.483 | 2.723 | 2.723 | MIRI_LRS | 587.90 | 0.005 | 0.015 | 0.046 |

#### NH3

| Ventana | Rango (μm) | Pico (μm) | Signal (ppm) | |Signal| (ppm) | Instrumento | σ 1 tránsito (ppm) | S/N 1 | S/N 10 | S/N 100 |
| :--- | :--- | ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: |
| NH3_9p0_10p0 | 9.00-10.00 | 9.688 | 0.862 | 0.862 | MIRI_LRS | 821.64 | 0.001 | 0.003 | 0.010 |
| NH3_10p0_11p2 | 10.00-11.20 | 10.353 | 1.369 | 1.369 | MIRI_LRS | 1204.62 | 0.001 | 0.004 | 0.011 |
| NH3_11p2_12p0 | 11.20-12.00 | 11.479 | 0.898 | 0.898 | MIRI_LRS | 3446.16 | 0.000 | 0.001 | 0.003 |

### A2

#### N2O

| Ventana | Rango (μm) | Pico (μm) | Signal (ppm) | |Signal| (ppm) | Instrumento | σ 1 tránsito (ppm) | S/N 1 | S/N 10 | S/N 100 |
| :--- | :--- | ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: |
| N2O_2p6_3p0 | 2.60-3.00 | 2.857 | 3.672 | 3.672 | NIRSpec_PRISM | 152.86 | 0.024 | 0.076 | 0.240 |
| N2O_4p3_4p8 | 4.30-4.80 | 4.465 | 5.048 | 5.048 | NIRSpec_PRISM | 277.33 | 0.018 | 0.058 | 0.182 |
| N2O_7p5_9p0 | 7.50-9.00 | 8.641 | 6.583 | 6.583 | MIRI_LRS | 576.87 | 0.011 | 0.036 | 0.114 |

#### NH3

| Ventana | Rango (μm) | Pico (μm) | Signal (ppm) | |Signal| (ppm) | Instrumento | σ 1 tránsito (ppm) | S/N 1 | S/N 10 | S/N 100 |
| :--- | :--- | ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: |
| NH3_9p0_10p0 | 9.00-10.00 | 9.905 | 1.557 | 1.557 | MIRI_LRS | 913.22 | 0.002 | 0.005 | 0.017 |
| NH3_10p0_11p2 | 10.00-11.20 | 10.353 | 2.318 | 2.318 | MIRI_LRS | 1204.62 | 0.002 | 0.006 | 0.019 |
| NH3_11p2_12p0 | 11.20-12.00 | 11.479 | 1.122 | 1.122 | MIRI_LRS | 3446.16 | 0.000 | 0.001 | 0.003 |

### A3

#### N2O

| Ventana | Rango (μm) | Pico (μm) | Signal (ppm) | |Signal| (ppm) | Instrumento | σ 1 tránsito (ppm) | S/N 1 | S/N 10 | S/N 100 |
| :--- | :--- | ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: |
| N2O_2p6_3p0 | 2.60-3.00 | 2.889 | 10.866 | 10.866 | NIRSpec_PRISM | 149.49 | 0.073 | 0.230 | 0.727 |
| N2O_4p3_4p8 | 4.30-4.80 | 4.498 | 13.332 | 13.332 | NIRSpec_PRISM | 302.59 | 0.044 | 0.139 | 0.441 |
| N2O_7p5_9p0 | 7.50-9.00 | 8.641 | 17.469 | 17.469 | MIRI_LRS | 576.87 | 0.030 | 0.096 | 0.303 |

#### NH3

| Ventana | Rango (μm) | Pico (μm) | Signal (ppm) | |Signal| (ppm) | Instrumento | σ 1 tránsito (ppm) | S/N 1 | S/N 10 | S/N 100 |
| :--- | :--- | ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: |
| NH3_9p0_10p0 | 9.00-10.00 | 9.688 | 2.654 | 2.654 | MIRI_LRS | 821.64 | 0.003 | 0.010 | 0.032 |
| NH3_10p0_11p2 | 10.00-11.20 | 10.742 | 8.316 | 8.316 | MIRI_LRS | 1732.66 | 0.005 | 0.015 | 0.048 |
| NH3_11p2_12p0 | 11.20-12.00 | 11.479 | 2.251 | 2.251 | MIRI_LRS | 3446.16 | 0.001 | 0.002 | 0.007 |

## Archivos conservados

- Figura principal v2: `Transmission_Spectroscopy/notebooks/POSEIDON_output/pure_spectra/plots/trappist1e_pure_a0_molecular_residuals_v2.png`
- Figura principal v2 PDF: `Transmission_Spectroscopy/notebooks/POSEIDON_output/pure_spectra/plots/trappist1e_pure_a0_molecular_residuals_v2.pdf`
- Tabla CSV: `Transmission_Spectroscopy/notebooks/POSEIDON_output/pure_spectra/plots/trappist1e_net_molecular_peak_summary.csv`

## Archivos regenerables de auditoría

El script puede volver a escribir los perfiles contrafactuales y la tabla de validación química cuando se ejecuta de nuevo. Estos productos no se conservan como artefactos finales porque son derivados exactos de los perfiles fuente y del código:

- Validación química regenerable: `Transmission_Spectroscopy/notebooks/POSEIDON_output/pure_spectra/plots/trappist1e_counterfactual_chemistry_validation.csv`
- Perfiles contrafactuales regenerables: `Transmission_Spectroscopy/profiles/counterfactual_A0_replacements/*_reset_<mol>_to_A0_chem.txt`
- Figura legacy regenerable con `--include-legacy-v1`: `Transmission_Spectroscopy/notebooks/POSEIDON_output/pure_spectra/plots/trappist1e_pure_a0_difference_mountains.{png,pdf}`
