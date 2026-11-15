# LIFE Proxima: enriquecimiento respecto a A0 y evidencia de la referencia fija

Fecha: 2026-10-10. Campaña: `a0_fixed_reference_20261010`.

**Auditoría 2026-10-11:** las tres restricciones terminaron con exit 0
(11:30:57 / 11:47:30 / 16:35:01 UTC). Productos primarios, valores fijos,
priors, hashes y evidencias PASS. La finitud estricta falla en desviaciones
derivadas de coordenadas fijas de N₂O/conjunta: `NaN` en stats/summary.
Muestras primarias constantes con varianza centrada exactamente cero.
**Cierre aceptado 2026-10-11 por autorización explícita del usuario:**
`ACCEPTED_WITH_FIXED_MOMENT_SALVEDAD`. Tabla final ln B
`29.440 ± 0.340 / 1.170 ± 0.342 / 31.103 ± 0.336`, sigma calibrado bilateral
`7.96 / 2.12 / 8.17`. Resumen auxiliar estable de siete coordenadas fijas;
52 archivos científicos originales intactos, con finitud estricta false
conservada en la auditoría. Monitor eliminado tras verificar el cierre.
[Informe de auditoría, tabla e interpretación](life_proxima_a3_100h_a0_fixed_audit_2026-10-11.md).
[Síntesis descriptiva de todas las capas y distinguibilidad ExoFarm](life_proxima_exofarm_retrieval_layers_synthesis_2026-10-11.md).

## 1. Pregunta científica y estado

La pregunta es si las observaciones sintéticas LIFE permiten recuperar
abundancias de N₂O y NH₃ superiores a una referencia preagrícola. Se separan
tres resultados: presencia molecular, dirección y magnitud del enriquecimiento,
y preferencia entre abundancias libres y abundancias fijadas en A0. La campaña
[LOO de 36 retrievals](life_proxima_molecular_ablation_loo_2026-10-04.md) responde
a la primera pregunta mediante la ausencia de una molécula. Esta nueva rama
mantiene las moléculas y evalúa valores preagrícolas no nulos.

**Ejecutado y validado:** postproceso de los seis retrievals completos oficiales
A1/A3 × {1, 10, 100 h}, 12 resúmenes marginales y seis conjuntos. Se congeló la
referencia A0 y se implementó el contrato de priors fijos.

**Selección autorizada y lanzada:** exclusivamente A3 a 100 h, con tres
retrievals: N₂O fija, NH₃ fija y ambas fijas. Se reutiliza el completo oficial
A3-100 h; no se ejecutarán las otras quince candidatas A1/1/10 h.
Arranque: `2026-10-11T00:05:21Z` (2026-10-10 19:05 COT), supervisor PID 758.
N₂O y NH₃ individuales arrancaron como MPI6 PID 779/783, con seis ranks cada
uno; el conjunto esperaba una vacante en el arranque. La selección y estado efectivos están en
`selected_scope.json`, `campaign_state.json` y `manifest.csv`.
Los nuevos `ln B` se calcularon tras auditar los productos primarios y la
correspondencia de evidencias, y están aceptados con la salvedad
de finitud derivada documentada arriba. Los PID siguientes describen el
arranque histórico; ya no hay procesos activos de esta campaña.

La primera comprobación posterior al arranque confirmó el supervisor, dos
`mpiexec` y seis ranks activos por corrida. Ambas individuales superaron la
carga de opacidades e iniciaron MultiNest: sus logs registraron 1600
reemplazos y 2032/2026 muestras totales (N₂O/NH₃). Son contadores de progreso;
las evidencias parciales impresas durante el muestreo todavía no se usan para
la comparación de modelos.

**Validación de configuración completada:** los tres prototipos A3-100 h
(N₂O fija, NH₃ fija y ambas fijas), cada uno contra su completo setup-only,
pasaron el contrato de igualdad de priors/dataset/opacidades. Se comprobaron
15 coordenadas declaradas y 13/13/12 efectivamente libres, respectivamente.
Los tres controles unitarios de transformación fija, rechazo de cambios de
dataset/priors y selección exacta A3-100 h pasaron; los módulos modificados
compilan. La validación y los
contratos resueltos quedan en `preflight_progress.json`, `preflight/` y
`resolved/`. Esto no mide convergencia ni evidencia de los nuevos modelos.

## 2. Referencia A0: definición, unidades y límites

Se conserva exactamente la referencia del atlas oficial, calculada por
[`retrieval_reference.py`](../Thermal_Emission_Spectroscopy/scripts/retrieval_reference.py)
desde el perfil
[`Proxima_b_A0_PreAgri_chem.txt`](../Transmission_Spectroscopy/profiles/Proxima_b_A0_PreAgri_chem.txt):

\[
X_{0,i}=\frac{\int_{p_{\rm top}}^{p_{\rm bottom}}X_i(p)\,dp}
{p_{\rm bottom}-p_{\rm top}},\qquad x_{0,i}=\log_{10}X_{0,i}.
\]

Las abundancias son fracciones de mezcla por número, adimensionales; la
integración se hace en presión, en bar, con trapecios, entre
`5×10⁻⁸` y `1 bar`. Es un promedio ponderado en presión reproducible;
la ponderación radiativa de las bandas LIFE puede ser distinta. No se ha
demostrado que este promedio sea una abundancia isoquímica radiativamente
equivalente al perfil vertical A0. No es un promedio de `log X`.

| Especie | VMR A0 efectiva | log₁₀(VMR) fijado |
| --- | ---: | ---: |
| N₂O | 1.305192923200922 × 10⁻⁷ | −6.884325289636784 |
| NH₃ | 1.1206595703796514 × 10⁻¹⁰ | −9.950526295665036 |

SHA-256 del perfil:
`ee8e93c76ff4d3bc62cb68cb29679942b7dad1f099c18a6feb3ed304d6798f7b`.
La referencia, su procedencia y sus unidades están congeladas en
[`a0_reference.json`](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a0_fixed_reference_20261010/a0_reference.json).
Se trata como conocida exactamente: este análisis no marginaliza incertidumbre
fotoquímica, diversidad natural ni incertidumbre del promedio A0.

## 3. Estadística posterior de enriquecimiento

Para cada muestra del modelo completo se calcula

\[
\delta_i^{(s)}=\log_{10}X_i^{(s)}-x_{0,i},\qquad
E_i^{(s)}=10^{\delta_i^{(s)}}=X_i^{(s)}/X_{0,i}.
\]

Se reportan la mediana y el intervalo marginal de colas iguales al 95 %
(`q0.025`, `q0.975`) de δ y del factor E. La dirección se cuantifica mediante

\[
P_i^+=P(X_i>X_{0,i}\mid D,M_{\rm libre})
=\int\mathbf1(\delta_i>0)\,p(\theta\mid D,M_{\rm libre})\,d\theta
\approx\frac1N\sum_{s=1}^N\mathbf1(\delta_i^{(s)}>0).
\]

Se usan las exportaciones POSEIDON de muestras de igual peso. Con muestras
ponderadas correspondería sumar los pesos normalizados, no contar filas.
La estimación por indicadores es una aplicación del cálculo de expectativas
posteriores descrito en la
[guía de Stan, estimación de probabilidades de eventos](https://mc-stan.org/docs/2_38/stan-users-guide/posterior-prediction.html#estimating-event-probabilities).
Aquí el evento se refiere a los parámetros, sin generar nuevas observaciones.

La probabilidad de enriquecimiento simultáneo se calcula **en las mismas
filas posteriores**, preservando la dependencia entre moléculas:

\[
P_{\rm ambas}^+\approx N^{-1}\sum_s
\mathbf1(\delta_{\rm N_2O}^{(s)}>0)
\mathbf1(\delta_{\rm NH_3}^{(s)}>0).
\]

No se multiplica la probabilidad marginal de cada molécula. También se guarda
la probabilidad del evento «al menos una por encima», mediante la unión.

### Influencia del prior y resolución de las colas

El prior escalar nominal uniforme en `log X ∈ [−12,−1]` ya asigna una masa
por encima de A0 de

\[
P_{i,\rm prior}^{+,\rm nominal}=(-1-x_{0,i})/11.
\]

Resulta **53.494 % para N₂O y 81.368 % para NH₃**. Por ello, una masa posterior
alta de NH₃ puede reflejar en parte el prior. Estos valores son diagnósticos
del prior escalar nominal; no se verificó mediante simulación el prior efectivo
con todas las restricciones físicas del modelo completo.

Si ninguna fila queda por debajo, se informa el conteo `0/N`, sin asignar
certeza absoluta ni inferir una significancia extrema. `1/N` describe la
granularidad de la tabla empírica; no es un límite superior calibrado ni una
estimación del error Monte Carlo. El número de muestras exportadas tampoco
garantiza independencia estadística.

## 4. Resultados directos del postproceso

Cada porcentaje está condicionado a la posterior del modelo completo y a la
referencia escalar fija. Los valores δ están en dex.

| Escenario | h | N₂O: δ mediana [95 %] | P(N₂O > A0) | NH₃: δ mediana [95 %] | P(NH₃ > A0) |
| --- | ---: | --- | ---: | --- | ---: |
| A1 | 1 | −2.316 [−4.922, +0.606] | 8.440 % | +0.270 [−1.895, +2.632] | 56.968 % |
| A1 | 10 | −2.637 [−4.959, −0.069] | 1.903 % | −0.129 [−1.920, +1.906] | 46.688 % |
| A1 | 100 | −0.243 [−3.062, +0.070] | 7.942 % | −0.711 [−1.972, +0.897] | 24.240 % |
| A3 | 1 | −1.828 [−4.892, +1.218] | 19.984 % | +0.198 [−1.905, +2.535] | 54.330 % |
| A3 | 10 | +0.824 [+0.456, +1.090] | 99.957 % | +1.266 [−1.857, +2.422] | 71.586 % |
| A3 | 100 | +0.737 [+0.618, +0.843] | 0/7479 debajo¹ | +1.693 [−0.923, +2.023] | 94.866 % |

¹ Todas las muestras guardadas quedan por encima de A0; la cola inferior no se
resuelve con este conjunto. Para N₂O A3-10 h quedan tres muestras por debajo
entre 6972. Para NH₃ A3-100 h quedan 384 entre 7479.

**Interpretación del proyecto:** A3-10/100 h ofrece separación posterior clara
de N₂O respecto a esta referencia; a 100 h el factor de enriquecimiento
mediano es aproximadamente `5.45`, con intervalo 95 % `[4.15, 6.97]`.
NH₃ A3-100 h presenta preferencia direccional, pero su intervalo 95 % cruza
A0 y conserva una cola importante hacia abundancias inferiores. A3-10 h tiene
una masa NH₃ por encima de A0 inferior al 81.368 % del prior escalar nominal.

La probabilidad conjunta de ambas por encima es `71.558 %` en A3-10 h y
`94.866 %` en A3-100 h. No se atribuye una causa agrícola a estos porcentajes.

**Tensión relevante:** las medianas N₂O de A1 quedan por debajo de A0 efectiva
en los tres tiempos. El resultado requiere revisar la correspondencia entre
el promedio químico y la abundancia isoquímica recuperada, el perfil vertical,
P–T y las degeneraciones; no prueba que el forzamiento A1 sea preagrícola.
No se modifica A0 retrospectivamente para obtener una separación más grande.

## 5. Modelos nulos con valores A0 no nulos

El modelo completo `M_libre` mantiene los priors oficiales. Se proponen:

- `M_A0,N2O`: fija N₂O; NH₃ y los demás parámetros siguen libres.
- `M_A0,NH3`: fija NH₃; N₂O y los demás parámetros siguen libres.
- `M_A0,conjunto`: fija simultáneamente N₂O y NH₃.

Cada familia comprende A1/A3 × {1, 10, 100 h}. Los modelos individuales
permiten atribuir la preferencia a la restricción de cada abundancia; el
conjunto evalúa el patrón combinado, y podría estar dominado por N₂O.
La combinación de las tres familias en la matriz amplia habría sumado
dieciocho retrievals. El usuario restringió la ejecución a **A3-100 h**:
se corren únicamente tres modelos, uno por familia. Las dieciocho
configuraciones preparadas permanecen como historial del diseño; las otras
quince no quedan autorizadas ni en la cola.

Se conservan las opacidades de ambas moléculas. La instalación POSEIDON
inspeccionada implementa para estos priors 1D la transformación
`x = low + u(high−low)`. Fijar ambos extremos en `x0` produce exactamente
`x=x0`; su medida es un punto fijo, sin ancho arbitrario. Se usa el mismo
contrato de ancho cero que la superficie negra a 1 bar del modelo oficial.
Las coordenadas fijas permanecen declaradas en POSEIDON/MultiNest: **15
coordenadas declaradas**, **14 efectivamente libres** en el completo,
**13** al fijar una especie y **12** al fijar ambas. El preflight no demuestra
por sí solo convergencia del muestreo con esas coordenadas inactivas.

El resto de la configuración se conserva: PT Madhu, siete gases incluyendo
O₂, fondo N₂, abundancias isoquímicas, superficie explícita a 1 bar,
`R=10000`, malla `3.8–19 μm`, `N_live=800`, `ev_tol=0.5`, sin `x_tol` ni
inflación de error, likelihood gaussiana diagonal del flujo planetario directo
`Fp` en `W m⁻² m⁻¹`. Cada contraste usa los mismos 31 bins y los mismos bytes
del dataset oficial. No se genera una realización adicional.

## 6. Evidencia, error numérico y sigma calibrado

Para cada dataset, sin mezclar tiempos ni escenarios:

\[
Z_{\rm libre}=\int\mathcal L(D\mid\theta,x)\pi(\theta,x)\,d\theta\,dx,
\qquad
Z_{\rm A0}=\int\mathcal L(D\mid\theta,x=x_0)\pi(\theta\mid M_{\rm A0})\,d\theta,
\]
\[
\ln B_{\rm libre,A0}=\ln Z_{\rm libre}-\ln Z_{\rm A0},\qquad
s_{\ln B}=\sqrt{s_{\ln Z,\rm libre}^2+s_{\ln Z,\rm A0}^2}.
\]

La última expresión presupone errores numéricos no correlacionados. Se
reutiliza la evidencia completa ya auditada y se conserva su archivo/hash.
Las incertidumbres MultiNest describen precisión numérica estimada, no
variabilidad entre realizaciones ni error de especificación del modelo.
La definición e interpretación de la evidencia siguen
[Trotta (2008), Bayes in the sky](https://arxiv.org/abs/0803.4089).

Un `ln B` positivo favorece permitir apartarse de A0, en cualquiera de las dos
direcciones. Para hablar de enriquecimiento se examinan además δ y `P⁺`.
La tabla de evidencia frente a A0 reportará `ln B ± error` y sigma calibrado
según la [convención ya registrada](life_proxima_loo_sigma_lin_convention_2026-10-10.md):

\[
B=-\frac1{e\,p\ln p},\qquad
p=\operatorname{erfc}(\sigma_{\rm cal}/\sqrt2),\quad 0<p<1/e.
\]

Se usa como calibración histórica por igualdad del límite de
[Benneke & Seager (2013)](https://arxiv.org/abs/1306.6325), ecuaciones 8–9,
citado por [Lin et al. (2021)](https://arxiv.org/abs/2105.09319).
Para `ln B ≤ 0` se reportará `N/A`. Aplicar esta convención al contraste
A0 es una decisión de este proyecto: no presupone que Lin et al. fijaran estas
abundancias preagrícolas. El sigma del contraste conjunto se refiere a la
restricción conjunta; no se asigna a cada molécula por separado.
Los porcentajes `P⁺` no se convierten en estos sigma de evidencia.

## 7. Ejecución recuperable y aceptación

Productos existentes:

- [Tabla marginal CSV](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a0_enrichment_posterior_2026-10-10.csv).
- [Tabla conjunta CSV](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a0_enrichment_joint_2026-10-10.csv).
- [Controles y procedencia JSON](../Thermal_Emission_Spectroscopy/final_products/tables/life_proxima_a0_enrichment_posterior_2026-10-10.validation.json).
- [Análisis reproducible](../Thermal_Emission_Spectroscopy/scripts/analyse_proxima_a0_enrichment.py).
- [Preparador/supervisor](../Thermal_Emission_Spectroscopy/scripts/run_proxima_a0_reference_campaign.py),
  [helper de priors](../Thermal_Emission_Spectroscopy/scripts/fixed_abundance_reference.py) y
  [controles del contrato](../Thermal_Emission_Spectroscopy/scripts/test_a0_reference_contract.py).
- [Referencia y configuraciones candidatas](../Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a0_fixed_reference_20261010/README.md).

Desde el entorno Ubuntu `POSEIDON`:

```bash
python Thermal_Emission_Spectroscopy/scripts/analyse_proxima_a0_enrichment.py
python Thermal_Emission_Spectroscopy/scripts/test_a0_reference_contract.py
python Thermal_Emission_Spectroscopy/scripts/run_proxima_a0_reference_campaign.py --prepare
python Thermal_Emission_Spectroscopy/scripts/run_proxima_a0_reference_campaign.py --preflight-prototypes
```

El lanzamiento requiere seleccionar explícitamente `--launch --mode joint`,
`separate` o `both`; no existe un modo de lanzamiento por defecto. La cola
preflight compara todos los priors comunes y cada checksum con su modelo
completo. Límite: dos retrievals simultáneos, seis ranks por uno y un thread
por rank. Scratch separado en `/home/dasan/exofarm_a0ref_20261010` para I/O
MultiNest, archivo posterior bajo la campaña del repositorio. Se rechazan
duplicados y directorios no vacíos; ante fallo se preserva todo y se detienen
nuevos lanzamientos sin matar la otra corrida activa. La recuperación tras
interrupción exige inspeccionar procesos y checkpoints; no hay relanzamiento
automático. `campaign_state.json` y `manifest.csv` se crean al seleccionar y
lanzar una matriz; `campaign_plan.json` y `candidate_manifest.csv` preservan
el diseño candidato inicial. La selección vigente es `selected_scope.json`.

El comando de la cola autorizada es:

```bash
python Thermal_Emission_Spectroscopy/scripts/run_proxima_a0_reference_campaign.py --launch --mode both --scenarios A3 --hours 100
```

El lanzamiento desacoplado se realizó mediante
`launch_proxima_a0_a3_100h.py`, que rechaza PID/log/estado existentes. Log y
PID del supervisor están en el directorio `retrievals` padre, con prefijo
`a0_fixed_reference_20261010.A3_100h.supervisor`. No ejecutar otra copia del
comando si ya existe estado; comprobar primero procesos y checkpoints.

Seguimiento horario histórico: `seguimiento-life-a0-a3-100h-3`, silencioso
ante progreso sano. Monitor eliminado tras verificar el cierre.
No se reinicia ni duplica ninguna corrida. Los valores fijos son log₁₀ N₂O = −6.884325289636784 y
log₁₀ NH₃ = −9.950526295665036, con 13/13/12 parámetros efectivamente libres.

El estado histórico `SAMPLING_COMPLETE_AUDIT_REQUIRED` significó finalización
del muestreo antes de la auditoría; el estado actual es
`VALIDATED_COMPLETE_WITH_SALVEDAD`. Para aceptar las nuevas
evidencias deben verificarse código de salida cero, muestras y espectros
finitos, P–T/log-X, valores fijos en todas las muestras, archivos MultiNest,
concordancia entre `stats` y resultados, y hashes de entradas/priors. Usar el
número efectivamente libre para nuevos diagnósticos de grados de libertad;
preservar el valor histórico de POSEIDON etiquetado como tal. La tabla `ln B`
se genera únicamente después de esa auditoría y por pareja de dataset.

## 8. Alcance de la interpretación condicionada

Una frase defendible, tras la aceptación con salvedad documentada,
es: «Bajo el modelo isoquímico y la referencia A0 efectiva adoptada,
N₂O presenta enriquecimiento posterior y preferencia libre/A0
ln B = 29.440 ± 0.340; NH₃ conserva apoyo limitado
ln B = 1.170 ± 0.342. La restricción conjunta da ln B = 31.103 ± 0.336».
La atribución agrícola requiere descartar explicaciones naturales y contrastar
forzamientos/profiles físicos. Estos modelos no infieren directamente un flujo
agrícola ni la probabilidad de una civilización.

Se conservan las salvedades oficiales: una realización diagonal por dataset,
promoción post hoc A1-1 h, desajuste de perfiles isoquímicos y tensiones de
ajuste a 100 h (`χ²_red` histórico A1/A3 = `3.18/4.94`, 16 dof declarados).
No se amplía esta rama a ruido instrumental correlacionado ni se cambia la
matriz legacy 8/8. Es evidencia intermedia para un artículo, condicionada al
modelo y a los priors, con atribución física aún abierta.
