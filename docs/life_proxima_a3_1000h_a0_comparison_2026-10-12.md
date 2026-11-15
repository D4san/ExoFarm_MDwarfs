# LIFE Proxima A3–1000 h: completo y tres referencias A0

**Actualización vigente 2026-10-13:** completo terminado exit0, pendiente
auditoría; tres variantes reanudadas por petición del usuario en MPI5 cada
una, tras validar y respaldar checkpoints. El reparto MPI3 inferior es
histórico; logs actuales en `recovery_20261013_MPI5_R1/`.
[Registro de la migración](life_proxima_a3_1000h_mpi5_resume_2026-10-13.md).

Fecha: 2026-10-12, America/Bogota. Ampliación autorizada explícitamente
por el usuario: cuatro modelos a 1000 h, con ejecución paralela. Sustituye
la restricción previa a un único completo; no amplía escenarios ni tiempos.

## Pregunta, hipótesis y procedencia

Se pregunta si el mismo espectro observado A3–1000 h favorece abundancias
libres respecto a la referencia preagrícola efectiva. Se reutiliza el completo
activo, sin duplicarlo, y se añaden N₂O fija, NH₃ fija y ambas fijas.
Las moléculas y sus opacidades permanecen presentes. No son corridas LOO.

Dataset común: `LIFE_proxima_A3_1000h_O2_fixedBlack1bar_official.dat`,
SHA-256 `5611c5904ef03aa02586bed15f14c0c2560ac5ae6fa9463ef420229311db75fa`.
Se conservan sus 31 canales y la misma realización de ruido. No se genera
otro espectro observado. Integración: 1000 h = 41.6667 días.

La referencia escalar del análisis de 100 h se conserva con su perfil/hash:
log₁₀ X(N₂O) = −6.884325289636784 y log₁₀ X(NH₃) = −9.950526295665036.
Es un promedio ponderado en presión, tratado como exacto; no demuestra
equivalencia radiativa con el perfil vertical A0 ni atribución agrícola.
Véase [metodología A0](life_proxima_a0_enrichment_methodology_2026-10-10.md).

| Modelo | Dimensión declarada / libre | Procesos MPI |
| --- | --- | --- |
| Completo existente | 15 / 14 | 6, conservados |
| N₂O fija a A0 | 15 / 13 | 3 |
| NH₃ fija a A0 | 15 / 13 | 3 |
| Ambas fijas a A0 | 15 / 12 | 3 |

Madhu/isochem, O₂, superficie negra fija a 1 bar, sin inflación, N_live=800,
ev_tol=0.5, R=10000 y rejilla nativa 3–20 μm comunes. Solo cambian los
priors de las especies fijadas a intervalos de anchura cero. El preflight
setup-only contrasta cada configuración con el completo activo y conserva
las opacidades. La identidad del forward nativo fue validada en el completo.

## Ejecución y salvaguardas

Comprobación del equipo: 16 CPU lógicas, aproximadamente 28 GiB disponibles,
swap vacía. Presupuesto global: 15 ranks, cuatro modelos simultáneos;
cada lanzamiento nuevo exige 8 GiB disponibles. Si falta margen, espera en
cola. La topología MPI3 de variantes es una decisión de ejecución, sin
cambiar puntos vivos, tolerancias ni priors. No se promete un tiempo final.

El supervisor nuevo valida las tres configuraciones antes de muestrear,
rechaza directorios existentes y trabajos científicos ajenos, conserva hashes
y registra exit/log/productos separados. Ante fallo detiene nuevos lanzamientos,
preserva workers y productos; no mata ni reinicia automáticamente.

- [Supervisor](../Thermal_Emission_Spectroscopy/scripts/run_proxima_a0_a3_1000h.py).
- [Pruebas de contrato](../Thermal_Emission_Spectroscopy/scripts/test_proxima_a0_1000h.py).
- Campaña nueva: `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a0_fixed_reference_A3_1000h_20261012/`.
- Fuentes: `selected_scope.json`, `campaign_state.json`, `manifest.csv`,
  `preflight_validation.json`, `resolved/`, `logs/` y `supervisor.log`.
- Scratch: `/home/dasan/exofarm_a0ref_A3_1000h_20261012/`.
- Completo conservado: [recuperación R1](life_proxima_a3_1000h_checkpoint_resume_2026-10-12.md).

## Aceptación y comparación pendientes

Exit 0 conduce a COMPLETE_PENDING_VALIDATION. Auditar posterior, espectro,
PT/log_X, MultiNest, finitud, hashes, priors y abundancias fijas en todas las
muestras. La salvedad de momentos NaN aceptada a 100 h no acepta por anticipado
productos nuevos. Conservar originales y documentar cualquier incidencia.

Tras aceptar cada pareja sobre este mismo dataset:

\[
\ln B_i=\ln Z_{\rm completo,1000h}-\ln Z_{i,\rm A0,1000h},\qquad
s_{\ln B_i}=\sqrt{s_{\ln Z_c}^{2}+s_{\ln Z_i}^{2}}.
\]

Error en cuadratura condicionado a estimaciones numéricas independientes.
Usar stats precisas verificadas contra resultados; sigma calibrado bilateral
según [convención Lin](life_proxima_loo_sigma_lin_convention_2026-10-10.md),
N/A cuando ln B≤0. El contraste conjunto pertenece a ambas restricciones;
no asigna su sigma individualmente. La dirección de enriquecimiento requiere
la posterior libre. No comparar evidencias absolutas entre 100 y 1000 h.

Supervisor lanzado a las 23:04:42 UTC / 18:04:42 COT, PID 1139, PREFLIGHT.
Cuatro pruebas de contrato PASS: selección exacta/ejecución MPI3, igualdad del
dataset y rejilla, rechazo de configuración discrepante y trabajos MPI ajenos,
y protección de duplicados simulada sin crear procesos. La prueba real de
relanzamiento fue bloqueada por seguridad y no se ejecutó. Los 35 archivos
protegidos conservan todos sus SHA-256, cero discrepancias.
El completo confirmó continuidad en su log R1: 51 500 reemplazos y 2 693 510
evaluaciones, por encima del checkpoint restaurado de 51 200 / 2 646 212.
**Arranque verificado:** preflight real PASS en las tres configuraciones;
estado RUNNING. MPI N₂O/NH₃/conjunta PID 1208/1238/1271, ranks
1219–1221 / 1249–1251 / 1282–1284. Completo MPI PID 805, ranks 820–825
preservados. Cuatro mpiexec y quince ranks activos; nuevas variantes en
carga de opacidades y completo en muestreo. Memoria disponible ~21 GiB y
swap vacía. La carga inicial no acredita todavía contadores MultiNest nuevos.
Los seis completos previos, 36 LOO, tres A0–100 h y matriz 8/8 se preservan.
