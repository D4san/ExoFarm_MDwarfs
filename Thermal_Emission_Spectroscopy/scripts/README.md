### LIFE noise curves on molecular signals (2026-10-27)

plot_emission_molecular_residuals.py reproduces the A0–A3 spectra and N₂O/NH₃
counterfactual signals. The --observations option accepts one or more
four-column LIFE datasets; each file adds ±1σ curves to the two lower
molecular-signal panels. The original signal-derived y-limits are fixed before
noise curves are drawn. Color encodes integration time and line style encodes
the sign. The --observations-label option accepts one label per dataset, and
--output-suffix preserves the default figure. Flux and uncertainty are
converted from W m⁻² m⁻¹ to W m⁻² µm⁻¹ by multiplying by 10⁻⁶. The A3 1/10/100 h
variant uses the products and hashes recorded in the
[2026-10-27 report](../../docs/life_proxima_emission_spectra_with_life_data_2026-10-27.md).

`plot_proxima_retrieval_products.py`: tres figuras de retrieval LIFE para la
  matriz canónica Proxima A0--A3 x {10 h, 240 h}. El espectro global y los zooms
  moleculares muestran los extremos A0/A3; el atlas de perfiles/posteriores se
  centra en A3 y lo compara con el perfil VULCAN de A3 y una referencia A0
  efectiva, definida como promedio columnar ponderado en presión. Las curvas
  forward y recuperadas se interpolan a 250 puntos globales y 75 puntos por
  zoom solo para presentación; los datos originales no se alteran. Los
  marcadores observados llevan un contorno gris fino para aumentar el contraste.
La leyenda distingue explícitamente `Retrieved`, `True` y `Observed`, con los
  tonos y marcadores de la figura análoga de transmisión. Los envelopes
  continuos se muestran con `alpha=0.025` (2 sigma) y `alpha=0.05` (1 sigma)
  para mantener protagonistas a los puntos observados; las líneas `Retrieved`
  y `True` también se atenuaron; los marcadores de observación se ampliaron a

El modo opcional `--audit-a1-a3-times` genera una figura de auditoría separada
con filas por tiempo (10, 100 y 240 h), dos columnas moleculares (N2O y NH3) y
una columna P–T. Adapta la cuadrícula compacta, la leyenda de estilos de línea y
los recuadros de métricas de `plot_profiles_posteriors()`; no crea una
composición visual independiente. Cada panel molecular muestra histogramas
marginales A1/A3, barras horizontales asimétricas q16–q84 alrededor de la
mediana, perfiles VULCAN verticales de A1 y A3, referencia A0 efectiva y z
firmados respecto a A0. La incertidumbre isochem se resume con errorbars, no
con una banda vertical ancha. La tercera columna compara P–T posterior
(mediana, bandas 68/95%) con la entrada VULCAN; los recuadros reportan χ²red,
dof y ln Z por dataset. `z` es una distancia condicional descriptiva, distinta
de `ln Z` y no una detección formal; evidencias de datasets distintos no se
comparan como factor de Bayes. La fila de 100 h usa datasets de auditoría
independientes (semillas A1 `460512527`, A3 `129315834`), fuera de 8/8. El
loader valida encabezados, cuantiles, orden y finitud de muestras y perfiles.
El modo deja intactas las figuras y datasets canónicos. Se ejecuta desde la raíz:

```bash
python Thermal_Emission_Spectroscopy/scripts/plot_proxima_retrieval_products.py \
  --audit-a1-a3-times
```
El nombre anterior `--audit-a1-a3-240h` permanece como alias de compatibilidad.

El modo oficial `--official-a1-a3-times` genera la V2 oficial, con una fila
por 1/10/100 h y seis
columnas moleculares (H2O, CO2, CH4, O3, N2O, NH3), más P--T. O2 sigue estando
en los retrievals y sus posteriores; se omite solo su panel para dar espacio
a las demás especies. Cada PNG/PDF/SVG tiene ~7.28 in de ancho para página de
dos columnas. Las marginales con medianas e intervalos q16--q84 aparecen en
las tres filas; los perfiles VULCAN de abundancia aparecen también en las
tres, mientras el P--T VULCAN de entrada aparece en la fila superior. Cada
encabezado de especie da una sola vez
`z_0=log10(VMR_A0,eff)`; se define `z_(s|A0)=(q50_s-z_0)/σ68_s`, con
`σ68_s=(q84_s-q16_s)/2`. Esta distancia es descriptiva y condicional, no una
significancia de detección. La columna P--T muestra únicamente los perfiles
recuperados, con bandas 68/95%; χ²red y ln Z por dataset quedan en la tabla del
informe. A1 se representa en verde, A3 en rosa y A0 efectiva con una línea
punta verde oscuro. El prior uniforme común es `log10(VMR)=[-12,-1]`. La V2
oficial ajusta los límites por especie usando perfiles VULCAN y posteriores,
siempre dentro de ese dominio; perfiles fuera de la ventana se recortan solo
en la figura. V1 muestra el prior completo y V3 (límites
basados solo en posteriores) se conservan como alternativas. Las tres se
exportan en PNG, PDF y SVG. Esto no modifica datos, priors ni retrievals. El
render focal anterior de N2O/NH3 sigue preservado como iteración histórica.
Desde la raíz:

```bash
python Thermal_Emission_Spectroscopy/scripts/plot_proxima_retrieval_products.py \
  --official-a1-a3-times
```

El comando estándar `--official-a1-a3-times` regenera V2 bajo el nombre base.
V1 se reproduce con `--official-a1-a3-times-full-prior-xlim`; V3 con
`--official-a1-a3-times-posterior-xlim`. El alias
`--official-a1-a3-times-dynamic-xlim` regenera una copia de V2 bajo el sufijo
`_dynamic_xlim`. Cada modo guarda PNG, PDF y SVG en el directorio de figuras
de la campaña.

El modo `--a1-1h-noise-repeat` genera un suplemento independiente con las dos
realizaciones A1 de 1 h (oficial y ruido nuevo), posteriores N₂O/NH₃, perfiles
VULCAN, referencias efectivas A0/A1 y P–T recuperado. Mantiene intacta la figura
oficial 1/10/100 h. Se ejecuta desde la raíz del repositorio:

```bash
python Thermal_Emission_Spectroscopy/scripts/plot_proxima_retrieval_products.py \
  --a1-1h-noise-repeat
```
  5.8 pt en el panel global y 6.2 pt en los zooms.
  Los puntos son opacos (`alpha=1`) y sus barras de error conservan la
  transparencia del panel.
- `plot_proxima_a3_molecular_posteriors.py`: compara las posteriores
  canónicas y de auditoría de `N2O`/`NH3` para A3 a 10/240 h, con la referencia
  A0 efectiva y `chi^2_red` por integración. Genera PNG/PDF en
  `../outputs/life_proxima_b_earthlike_v1/plots/`; es una figura de auditoría y no
  modifica ni reemplaza el atlas canónico.
- `plot_proxima_a3_10_100_240h_audit.py`: valida productos POSEIDON/MultiNest y
  genera el atlas de auditoría A3 a 10/100/240 h, separando perfiles VULCAN de
  posteriores isochem. Incluye referencias A0/A3 efectivas, z firmados,
  `ln Z`, `chi^2_red`, dof y radio de referencia; el script deja intactas las
  figuras canónicas. Ejecutar con `python plot_proxima_a3_10_100_240h_audit.py`.
- `audit_proxima_a3_retrieval_residuals.py`: compara los 31 bins LIFE A3 con el
  forward sin ruido y las medianas espectrales recuperadas a 10/100/240 h.
  Valida el rebin fotónico frente al producto LIFE guardado y exporta CSV/JSON
  por bin más una figura PNG/PDF en `../outputs/life_proxima_b_earthlike_v1/`.
  Se ejecuta con el `.venv` local; no importa POSEIDON ni lanza retrievals.
- `run_life_retrieval.py` ahora admite `--surface-pressure-mode fixed-black`
  y `--include-o2` para recuperación con superficie explícita y O2. La opción
  `--validate-forward --setup-only` exige que el modelo reproduzca el forward
  A3 con PT/química verdaderas dentro de 0.3 sigma RMS y 1 sigma máximo;
  `R=10000` es necesario para pasar esta prueba en Proxima. El runner evita
  duplicar `model_name` en el `retrieval_name` explícito; POSEIDON concatena
  ambos y raíces largas alcanzaron 100 caracteres, truncando el sufijo de
  MultiNest en las auditorías anteriores.
- `launch_proxima_a3_100h_o2_fixed_surface.sh`: lanzador durable del retrieval
  A3--100 h corregido (`N_live=800`, sin inflación ni `x_tol`, `isochem`,
  O2 incluido, superficie explícita a 1 bar, `R=10000`). Guarda log y PID y
  rehúsa duplicar una corrida existente. No altera la matriz canónica.
- `postprocess_existing_proxima_a3_10h_o2.py`: recupera productos de A3--10 h
  desde las muestras MultiNest ya cerradas. Comprueba hash y dimensiones del
  `.d`, verifica el dataset y conserva el original; crea la copia `.dat` solo
  si falta y exige identidad byte a byte. POSEIDON reconstruye resultados,
  muestras derivadas, espectro, P--T y log-X; no relanza MultiNest ni sus
  evaluaciones de likelihood, aunque calcula espectros forward para los
  productos posteriores. Requiere Ubuntu/conda `POSEIDON`.
- `plot_proxima_a3_o2_fixed_surface_10_100h.py`: compara las posteriores
  corregidas de 10/100 h, referencias efectivas A0/A3 y residuos de mediana en
  los 31 bins propios de cada dataset. Exporta PNG/PDF y resumen JSON / CSV de
  residuos; corre en el `.venv` local, no importa POSEIDON ni lanza MultiNest.
  Requiere `--overwrite` para reemplazar sus propios productos ya generados.
- `diagnose_proxima_a3_forward_swaps.py`: recalcula el forward A3 y prueba,
  sobre los mismos 31 bins, las diferencias de O2, superficie explícita,
  PT, química y radio para 100/240 h. Exporta JSON/CSV por variante, CSV por
  bin y una figura PNG bajo `../outputs/life_proxima_b_earthlike_v1/forward_swap_audit/`.
  Requiere Ubuntu/conda `POSEIDON` y las variables de entorno de opacidades;
  admite `--setup-only`. No ejecuta MultiNest. La auditoría demostró que el
  modo heredado `run_life_retrieval.py --surface-pressure-mode fixed-bottom`
  usa `surface=False`, **no** una superficie negra explícita a 1 bar.

Para revisar juntos los cuatro tiempos de integración disponibles, el script
puede generar una vista de auditoría de cuatro filas (`10 h`, `240 h`, `500 h`
y `1200 h`) sin alterar las tres figuras canónicas:

```bash
python plot_proxima_retrieval_products.py \
  --four-row-audit-output ../outputs/life_proxima_b_earthlike_v1/plots/audit
```

La salida es `retrieval_profiles_posteriors_proxima_4rows_audit` en PNG y PDF.
Las filas de 500/1200 h leen los productos `_robust_lifesim_direct` y la
figura permanece clasificada como auditoría.

La revisión del 2026-08-30 usa títulos directos, etiquetas de moléculas sin
líneas verticales y rellenos sólidos claramente diferenciados para conservar la
lectura de las curvas. La figura conjunta adopta además la composición de tres
paneles del análogo de transmisión, con etiquetas y leyendas equivalentes. La
comparación SNR/proyección mantiene sólo el intervalo útil de 1--1000 h en su
panel inferior y ajusta el rango logarítmico superior a los puntos graficados.
En el atlas de perfiles, el perfil VULCAN A3 usa el tono oscuro de `True`, la
mediana posterior A3 el rosa de `Retrieved` y la referencia A0 efectiva el
verde oscuro de `True`. La leyenda de estas convenciones es horizontal bajo el
título; la fórmula de la distancia firmada aparece aparte y los recuadros
muestran la mediana A3, el valor A0 de referencia y su distancia en sigma.

Las figuras de retrieval conservan el observable directo `F_p` en
`W m^-2 m^-1`, separan espectro forward VULCAN, mediana recuperada, intervalo
del 68 % y bins observados. El perfil A3 se dibuja sólido, su mediana posterior
discontinua y la referencia A0 efectiva punteada; el panel global no lleva grid
y usa marcadores observados ampliados. En los recuadros del atlas se muestran
la mediana A3, el valor A0 de referencia y la distancia en sigma; no se
incorpora el piloto A3--1200 h.
Es un cambio de presentación; no cambia los productos científicos de entrada,
sus unidades ni la matriz de escenarios.
