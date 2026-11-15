# Diagnóstico de S/N molecular LIFE Proxima A1/A3 a 1, 10 y 100 h

**Fecha:** 2026-10-02  
**Estado:** diagnóstico reproducible a partir de productos clásicos guardados; no se ejecutaron llamadas nuevas a LIFEsim en esta auditoría.

## Pregunta y procedencia

La pregunta es si los niveles de ruido de los datasets de 1, 10 y 100 h siguen el escalado esperado de LIFE clásico y qué S/N integrado implican para las plantillas moleculares de A1 y A3.

Ya se habían realizado llamadas directas a LIFEsim para esta rama. La validación directa archivada registra LIFEsim 0.2.32 y SpectRes 2.1.1, con escenas A0/A3 calculadas a 1, 10, 100, 240, 500 y 1200 h. En esa prueba, la diferencia fraccional máxima de sigma entre la llamada directa y el escalado fue 6.66e-16; la diferencia máxima de las realizaciones emparejadas fue 8.54e-15 sigma. Está documentada en [la auditoría directa del escalado temporal](life_proxima_lifesim_noise_scaling_2026-08-31.md).

Para el diagnóstico A1/A3 actual se reutilizó el producto directo guardado de 10 h, Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/lifesim/life_classic_binned_products.npz. El entorno POSEIDON de WSL disponible durante esta auditoría no encontró el módulo lifesim; por ello no se afirmó haber vuelto a ejecutar LIFEsim. Se usó el ancla de 10 h para calcular los contrastes moleculares y se verificó independientemente que las columnas de incertidumbre de los seis datasets existentes corresponden al escalado esperado. No se generaron realizaciones de ruido nuevas.

## Definición

Para cada especie X se tomó la diferencia entre el espectro completo y el contrafactual donde X se reinicia al valor A0. El S/N diagonal integrado en un conjunto de bins B es:

    SNR_X(B) = sqrt(sum_i en B [(Delta F_X,i / sigma_i)^2])

La cifra principal de la tabla usa los 31 bins LIFE. Como comprobación localizada se calcula también feature_union, la unión de ventanas moleculares configuradas en el script. Es una proyección de plantilla con ruido diagonal; no es una probabilidad de detección ni incorpora covarianza instrumental.

Para ruido fotónico:

    sigma(t) = sigma(10 h) * sqrt(10 h / t)
    SNR(t)   = SNR(10 h) * sqrt(t / 10 h)

Así, respecto a 10 h, sigma debe multiplicarse por 3.1623 a 1 h y por 0.31623 a 100 h.

## S/N integrado en los 31 bins

| Escenario | Molécula | 1 h | 10 h | 100 h |
| --- | --- | ---: | ---: | ---: |
| A1 | N2O | 0.192 | 0.607 | 1.920 |
| A1 | NH3 | 0.037 | 0.115 | 0.365 |
| A3 | N2O | 1.886 | 5.965 | 18.864 |
| A3 | NH3 | 0.486 | 1.536 | 4.857 |

En feature_union, los valores de 100 h son 1.841 (A1 N2O), 0.344 (A1 NH3), 17.582 (A3 N2O) y 4.556 (A3 NH3). La tabla completa para las tres exposiciones y ventanas está en el CSV enlazado abajo.

## Comprobación de los datasets y de la raíz

Se comparó, bin por bin y después de convertir la sigma en fotones a unidades de energía, la incertidumbre de cada dataset con la sigma de 10 h escalada. Las seis entradas A1/A3 × 1/10/100 h tienen 31 bins. La mayor diferencia fraccional es 4.68e-7 y es compatible con el redondeo a seis cifras significativas de los archivos .dat; las razones medianas dataset/esperado son 1.0000000 dentro de esa precisión. Por tanto, los datasets actuales ya usan la raíz cuadrada del tiempo.

Omitir la raíz produciría sigma proporcional a 1/t: frente al escalado correcto, subestimaría S/N por un factor sqrt(10)=3.162 a 1 h y lo sobrestimaría por el mismo factor a 100 h. Por ejemplo, A3 N2O a 100 h pasaría erróneamente de 18.86 a 59.65 en los 31 bins. Ese cambio grande no está presente en los datasets validados.

Los datasets de 100 h son realizaciones independientes de ruido; sus residuos observados pueden diferir de los de 10 h. Esa diferencia no cambia la sigma nominal ni el S/N de plantilla esperado que se calcula aquí. La matriz canónica de retrievals 8/8 permanece intacta; este diagnóstico acompaña la serie oficial A1/A3 de 1/10/100 h sin reetiquetar los archivos de auditoría.

## Artefactos reproducibles

- Script: Thermal_Emission_Spectroscopy/scripts/diagnose_proxima_lifesim_molecular_snr_scaling.py
- Producto directo de 10 h: Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/lifesim/life_classic_binned_products.npz
- CSV S/N: Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/proxima_A1_A3_molecular_snr_direct_vs_scaled_1_10_100h.csv
- Validación de sigma de datasets: Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/proxima_A1_A3_molecular_snr_direct_vs_scaled_1_10_100h_dataset_sigma_validation.csv
- Resumen de auditoría: Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/tables/proxima_A1_A3_molecular_snr_direct_vs_scaled_1_10_100h.json
- [Figura PNG](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/audit/proxima_A1_A3_molecular_snr_direct_vs_scaled_1_10_100h.png) y [PDF](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/plots/audit/proxima_A1_A3_molecular_snr_direct_vs_scaled_1_10_100h.pdf)
- Validación directa previa: [LIFEsim directo frente al escalado temporal](life_proxima_lifesim_noise_scaling_2026-08-31.md)

Para regenerar las tablas y la figura con el Python local de postproceso:

    .venv/Scripts/python.exe Thermal_Emission_Spectroscopy/scripts/diagnose_proxima_lifesim_molecular_snr_scaling.py

La regeneración solo lee el producto directo guardado y los .dat; no llama a LIFEsim, no añade ruido y no modifica datasets, retrievals ni el índice 8/8.

## Lectura

En el diagnóstico integrado, A3 N2O ya tiene S/N esperado cercano a 6 a 10 h y A3 NH3 llega a aproximadamente 4.9 a 100 h. A1 queda por debajo de S/N=2 para ambas plantillas incluso a 100 h. Estas cifras son estimaciones condicionales al forward clásico, los bins y el ruido diagonal empleado. La sensibilidad posterior que muestran retrievals individuales también depende de la realización concreta, de degeneraciones y del perfil químico asumido; el S/N de plantilla no garantiza recuperación ni detección.

LIFEsim clásico aquí caracteriza una cota de ruido diagonal. El análisis no contiene la covarianza temporal/instrumental de LIFEsimMC/PHRINGE.
