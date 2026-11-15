# LIFE Proxima: ln B y sigma con la convención citada por Lin et al.

Fecha del análisis y consulta de fuentes: 2026-10-10. Campaña:
`proxima_a1_a3_molecule_ablation_loo_20261004`; A1/A3 × 1/10/100 h × seis especies.

## Método y trazabilidad bibliográfica

**Hecho de fuente:** [Lin et al. (2021), §5.2, p. 10 del manuscrito](https://arxiv.org/pdf/2105.09319#page=10)
comparan la evidencia del retrieval completo con modelos que excluyen moléculas
y remiten a Benneke & Seager (2013) y MacDonald & Madhusudhan (2017) para la
significancia. Su **tabla 2, p. 11** muestra `N/A` cuando el factor de Bayes
no favorece la presencia de la especie (`B ≲ 1`).

**Reconstrucción metodológica:** Lin et al. no imprimen una ecuación de conversión
ni publican en esa tabla sus Bayes factors. Aquí implementamos la calibración
explícita de su referencia [Benneke & Seager (2013), §2.2, ecuaciones (8)–(9),
tabla 2, p. 5](https://arxiv.org/pdf/1306.6325#page=5), basada en Trotta (2008)
y Sellke et al. (2001). Esto reproduce la convención bibliográfica citada;
no constituye una comprobación del código privado de Lin et al.

Para cada pareja con **el mismo dataset y realización de ruido**:

\[
\ln B=\ln Z_{\rm completo}-\ln Z_{\rm sin\,X},\qquad
\delta_{\rm num}(\ln B)=\sqrt{\delta_{\rm num}(\ln Z_{\rm completo})^2+
\delta_{\rm num}(\ln Z_{\rm sin\,X})^2}.
\]

Para `ln B > 0`, igualamos la calibración de la ecuación (8) e invertimos:

\[
B=\frac{-1}{e\,p\ln p},\quad 0<p<e^{-1},\qquad
p=1-\operatorname{erf}\!\left(\frac{\sigma_{\rm cal}}{\sqrt{2}}\right)
=\operatorname{erfc}\!\left(\frac{\sigma_{\rm cal}}{\sqrt{2}}\right).
\]

Se utiliza la rama `y=-ln p > 1` de `y-ln y=1+ln B`. Es una calibración
**bilateral**. Para `ln B ≤ 0` guardamos `N/A`, conservando el signo y valor de
`ln B`; no aplicamos valor absoluto ni asignamos sigma negativos de detección.
Los valores positivos coinciden con la tabla auxiliar anterior a la precisión
mostrada. La incertidumbre de `ln B` describe el error numérico de MultiNest,
con independencia asumida entre corridas; no es incertidumbre observacional.

**Límite de interpretación:** la ecuación (8) original es una desigualdad.
Su inversión como igualdad es la práctica histórica que se desea reproducir,
no una equivalencia universal ni un p-value medido. Las objeciones posteriores
de [Kipping & Benneke (2025)](https://arxiv.org/abs/2506.05392) y
[Thorngren et al. (2025)](https://arxiv.org/abs/2510.00169) siguen vigentes.
`ln B` es la métrica primaria; la columna sigma se etiqueta como calibrada.

## Tabla guardada

[CSV con precisión completa](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_loo_lnB_sigma_lin_2026-10-10.csv). `N/A` significa que el valor central
del contraste no favorece incluir la molécula; no significa sigma cero.
Las cifras sigma se muestran con dos decimales para lectura.

| Escenario | Exposición | Molécula | ln B ± error numérico | σ calibrado, convención Lin |
| --- | ---: | --- | ---: | ---: |
| A1 | 1 h | H₂O | +11.127 ± 0.238 | 5.09 |
| A1 | 1 h | CO₂ | +469.134 ± 0.290 | 30.75 |
| A1 | 1 h | CH₄ | +9.280 ± 0.238 | 4.69 |
| A1 | 1 h | O₃ | -1.548 ± 0.240 | N/A |
| A1 | 1 h | N₂O | -1.797 ± 0.240 | N/A |
| A1 | 1 h | NH₃ | -1.380 ± 0.242 | N/A |
| A1 | 10 h | H₂O | +229.565 ± 0.298 | 21.57 |
| A1 | 10 h | CO₂ | +4644.255 ± 0.352 | 96.43 |
| A1 | 10 h | CH₄ | +54.680 ± 0.290 | 10.69 |
| A1 | 10 h | O₃ | +0.288 ± 0.292 | 1.47 |
| A1 | 10 h | N₂O | +0.447 ± 0.296 | 1.63 |
| A1 | 10 h | NH₃ | -0.501 ± 0.294 | N/A |
| A1 | 100 h | H₂O | +2289.864 ± 0.351 | 67.74 |
| A1 | 100 h | CO₂ | +41729.861 ± 0.446 | 288.91 |
| A1 | 100 h | CH₄ | +314.093 ± 0.337 | 25.20 |
| A1 | 100 h | O₃ | +38.404 ± 0.336 | 9.03 |
| A1 | 100 h | N₂O | +1.608 ± 0.340 | 2.36 |
| A1 | 100 h | NH₃ | -1.526 ± 0.341 | N/A |
| A3 | 1 h | H₂O | +19.517 ± 0.234 | 6.57 |
| A3 | 1 h | CO₂ | +462.849 ± 0.294 | 30.54 |
| A3 | 1 h | CH₄ | +5.996 ± 0.233 | 3.89 |
| A3 | 1 h | O₃ | -0.359 ± 0.232 | N/A |
| A3 | 1 h | N₂O | +0.047 ± 0.234 | 1.12 |
| A3 | 1 h | NH₃ | -0.629 ± 0.231 | N/A |
| A3 | 10 h | H₂O | +241.513 ± 0.310 | 22.12 |
| A3 | 10 h | CO₂ | +3970.537 ± 0.376 | 89.16 |
| A3 | 10 h | CH₄ | +26.796 ± 0.290 | 7.61 |
| A3 | 10 h | O₃ | -0.381 ± 0.292 | N/A |
| A3 | 10 h | N₂O | +7.388 ± 0.291 | 4.25 |
| A3 | 10 h | NH₃ | -0.734 ± 0.292 | N/A |
| A3 | 100 h | H₂O | +1964.190 ± 0.357 | 62.74 |
| A3 | 100 h | CO₂ | +46592.005 ± 0.430 | 305.28 |
| A3 | 100 h | CH₄ | +272.924 ± 0.335 | 23.50 |
| A3 | 100 h | O₃ | +19.652 ± 0.339 | 6.59 |
| A3 | 100 h | N₂O | +65.550 ± 0.341 | 11.67 |
| A3 | 100 h | NH₃ | +1.506 ± 0.342 | 2.31 |

## Diagnóstico condicionado a la campaña

H₂O, CO₂ y CH₄ favorecen la inclusión en las seis observaciones. O₃ alcanza
9.03σ calibrados en A1-100 h y 6.59σ en A3-100 h. N₂O alcanza 4.25σ y 11.67σ
en A3 a 10 y 100 h; en A1-100 h queda en 2.36σ. NH₃ presenta preferencia
débil solo en A3-100 h (`ln B=1.506 ± 0.342`, 2.31σ calibrados).

Los valores enormes de CO₂ (hasta 305.28σ calibrados) expresan la magnitud de
la comparación dentro de estos modelos. La adecuación absoluta exige atención:
los retrievals completos de 100 h tienen χ² reducido 3.18 (A1) y 4.94 (A3),
con 16 grados de libertad. Se conservan las limitaciones de abundancias
isochem frente a perfiles verticales VULCAN, una realización diagonal por
dataset, sensibilidad a priors y ausencia de covarianza instrumental. A1-1 h
usa la realización NoiseRepeat2 promovida post hoc; no se estima cobertura
con esta campaña. Véase el [informe LOO](life_proxima_molecular_ablation_loo_2026-10-04.md).

## Reproducción y verificación

Se cargaron las 36 parejas del [CSV auditado](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/molecule_ablation_loo_20261004/loo_results_validated_20261010.csv), sin ejecutar
retrievals. Se verificaron cardinalidad y claves únicas, estado de auditoría,
SHA-256 de los seis datasets, resta de evidencias y propagación del error.
SHA-256 del CSV de entrada: `55f46c4e3a2257160e1748e4710c95a9169b360e667e328cdacc8225450c4750`.

El [script de cálculo](../Thermal_Emission_Spectroscopy/scripts/report_proxima_loo_lin_sigma.py) utiliza exclusivamente la biblioteca
estándar de Python y resuelve en logaritmos para evitar overflow de `exp(ln B)`
y underflow de p. Sus controles reproducen a la precisión publicada la tabla 2
de Benneke & Seager (B=2.9, 12, 21, 150 y 43000), prueban `N/A` para B≤1 y
comprueban ambas ecuaciones hasta `ln B=46592.005`.

Desde la raíz del repositorio:

```text
python Thermal_Emission_Spectroscopy/scripts/report_proxima_loo_lin_sigma.py --repo .
```

El CSV auditado anterior conserva su columna firmada como producto histórico.
La tabla de reporte vigente usa `sigma_lin_convention` y `N/A`. Las 36 ablaciones,
los seis retrievals completos, sus datasets y la matriz legacy 8/8 permanecen
intactos. El JSON contiguo al CSV guarda la validación de esta exportación.
