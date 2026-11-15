# Inventario de integridad LIFE Proxima A1/A3 — 2026-10-28

Este inventario identifica el estado local de los productos usados en la serie
A1/A3 a 1, 10 y 100 h. La matriz principal contiene 33 retrievals nuevos
auditados, junto con tres modelos completos A3 de referencia. El
[informe científico](../../life_proxima_a1_a3_corrected_binning_matrix_results_2026-10-28.md)
y el [atlas oficial](../../life_proxima_corrected_binning_full_posteriors_plot_2026-10-28.md)
describen resultados y límites.

## Alcance del inventario

`SHA256SUMS.txt` contiene **979 archivos**, 939 de carpetas de campaña y 40
insumos, scripts, tablas o figuras adicionales: 1.465.319.506 bytes en total.
Incluye:

- la matriz `a1_a3_corrected_binning_matrix_loo_20261021_r01`;
- los completos A3 de referencia en `a3_1_10h_binning_corrected_loo_20261020_r03`
  y `a3_100h_binning_corrected_mpi14_resume_20261018`;
- las ablaciones A3–100 h de NH3/N2O en
  `a3_100h_binning_corrected_loo_20261019`;
- dos intentos anteriores (`a3_100h_binning_corrected_20261017` y
  `a3_1_10h_binning_corrected_loo_20261020_r02`) únicamente como procedencia;
- los seis datasets, los perfiles A0/A1/A3 usados en el atlas, los forwards A1/A3,
  la referencia binned, scripts seleccionados, informes, tablas y figura oficial.

El inventario incluye logs y snapshots dentro de esas carpetas de campaña,
incluso los archivos `.log` que Git ignora por defecto. No incluye el entorno
Conda, las opacidades externas de POSEIDON, scratch fuera de esas carpetas ni
otras campañas del repositorio. Esas dependencias requieren su propia
preservación para reproducir el muestreo completo.

## Captura posterior del entorno

La [lista actual del entorno Conda POSEIDON](conda_POSEIDON_snapshot_2026-10-28.txt)
contiene 240 paquetes y también se copió y verificó en E:. Registra Python
3.10.13, POSEIDON 1.4.0, MultiNest 3.10, PyMultiNest 2.12 y mpi4py 4.1.0.
Su SHA-256 es
`38bfd8da5c3a9ffb601f8161027472668efc2b2a5c2d2667c8d67ece241cc7e1`.
Es una captura posterior al cálculo: no demuestra por sí sola que esas
versiones fueran las utilizadas durante el muestreo ni contiene los binarios,
canales fijados u opacidades. La lista se conserva aparte de las 979 entradas
del inventario original.

## Copia verificada en E:

El 2026-10-28 (America/Bogota) se guardó una copia en
`E:\Respaldos\ExoFarm_MDwarfs\LIFE_Proxima_A1_A3_20261028`, un disco físico
distinto de C:. Los 979 archivos se comprobaron individualmente tras copiarse
y coincidieron con el inventario. El [comprobante](backup_E_2026-10-28.json)
registra destino, alcance, fecha y hash del inventario; el respaldo contiene
también el comprobante, el inventario y esta guía. Las exclusiones indicadas
arriba siguen pendientes para una reproducción completa del entorno.

Se añadieron y verificaron por separado **12 registros de supervisor** situados
fuera de las carpetas de campaña (logs y archivos PID; 4.138 bytes). Sus
huellas están en [SHA256SUPERVISORES.txt](SHA256SUPERVISORES.txt) y la copia
en E: tiene su propio [comprobante](backup_supervisores_E_2026-10-28.json).
El SHA-256 de ese inventario suplementario es
`208dd4a2a26c005def347c1ff07390cc3e2f587a244d4f816531d581a0aa3d8a`.

## Suplemento de análisis integrado — 2026-10-28

El [análisis integrado vigente](../../life_proxima_a1_a3_retrievals_analisis_integrado_2026-10-28.md), sus tablas y script, los índices actualizados y las dos campañas corregidas A3–1000 h con dataset y registros se preservaron aparte en `E:\Respaldos\ExoFarm_MDwarfs\LIFE_Proxima_A1_A3_20261028\suplemento_analisis_integrado_20261028`. Se verificaron **125 archivos** (172,545,532 bytes) y sus SHA-256 se guardaron en [un inventario suplementario](SHA256_ANALISIS_INTEGRADO_2026-10-28.txt). También se releyeron los 474 insumos del análisis.

Antes de copiar se verificaron de nuevo los 979 archivos del inventario original tanto en C: como en E:. El inventario original se conservó intacto. El [comprobante suplementario](backup_analisis_integrado_E_2026-10-28.json) registra las comprobaciones. La aceptación de las fijaciones A0 de 1000 h permanece pendiente y el suplemento mantiene las exclusiones del entorno Conda completo, las opacidades externas y el scratch.

## Suplemento P y K de todos los gases — 2026-10-29

El [informe vigente integrado](../../life_proxima_a1_a3_retrievals_analisis_integrado_2026-10-29.md) amplía las probabilidades y K a los siete gases retenidos; la edición del 28-oct queda preservada como bitácora. La copia suplementaria en `E:\Respaldos\ExoFarm_MDwarfs\LIFE_Proxima_A1_A3_20261028\suplemento_P_K_todas_moleculas_20261029` contiene **28 archivos** y se verificó mediante [SHA-256](SHA256_P_K_TODAS_MOLECULAS_2026-10-29.txt). Los 480 insumos se comprobaron en origen y 477 ya estaban presentes con hash coincidente en los respaldos anteriores. El resto corresponde a fuentes históricas incluidas en el nuevo suplemento. [Comprobante](backup_P_K_todas_moleculas_E_2026-10-29.json).

La comparación histórica se presenta solo como sensibilidad metodológica; el informe vigente conserva como oficiales los resultados corregidos. El inventario original y el suplemento del 28-oct permanecen inalterados. Conda completo, opacidades externas y scratch siguen excluidos.

## Comprobación

Cada línea registra un SHA-256 y una ruta relativa a la raíz del repositorio.
Desde esa raíz, en Linux o WSL, se puede comprobar con:

```bash
sha256sum --check docs/evidence/life_proxima_a1_a3_release_2026-10-28/SHA256SUMS.txt
sha256sum --check docs/evidence/life_proxima_a1_a3_release_2026-10-28/SHA256SUPERVISORES.txt
```

Al crear el inventario se releyeron los 979 archivos: 0 ausentes o distintos.
También coincidieron 52 huellas existentes de datasets, perfiles, muestras,
figuras, operadores, configuraciones y código con los registros de auditoría
y procedencia. La huella del propio inventario es
`39af0fa0982008b15b3b854a25bbcc6a163093eb810329df12b10afce9126e87`.

Una suma de comprobación permite detectar cambios o ausencias; no contiene los
archivos y no sustituye una copia independiente. Para un respaldo, copiar los
archivos enumerados conservando sus rutas y verificar el inventario en el
destino. Si una fuente cambia legítimamente, crear un inventario nuevo con
fecha y documentar el motivo.
