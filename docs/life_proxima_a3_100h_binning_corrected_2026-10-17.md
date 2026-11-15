# Proxima A3–100 h con binning fotónico corregido

**Fecha:** 2026-10-17 (COT); el supervisor registra tiempos en UTC.  
**Estado al abrir la campaña:** MultiNest iniciado; resultado científico pendiente.  
**Alcance:** una repetición fresca del retrieval completo Proxima A3–100 h, para contrastarla con el producto de 100 h que usó el binning histórico.

## Pregunta y criterio de comparación

Se quiere saber cuánto cambian el ajuste y las posteriores de A3 cuando el espectro de emisión se integra en los canales LIFE con el operador fotónico corregido. La comparación reutiliza la misma realización observada de 100 h, incluidos sus 31 canales y su semilla, y conserva el modelo atmosférico completo. No se reanudan checkpoints del cálculo histórico: cambiaron el operador de observación y el nombre de salida.

La comparación es una prueba de sensibilidad al operador y a la cobertura de la rejilla, no una comparación de hipótesis atmosféricas anidadas. La evidencia `ln Z` se reportará para cada ejecución, pero su diferencia se interpretará como sensibilidad numérica/metodológica del retrieval. La calidad del ajuste, las posteriores y la recuperación del forward sintético también se compararán.

## Datos y configuración congelados

- Datos: `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/life_data/LIFE_proxima_A3_100h.dat`.
- SHA-256: `78662546181a5b74391a14b7b73ae80d879200a74db6a4bc5338e3ce7eee4705`; 31 canales; semilla registrada en el índice de datos: `129315834`.
- Modelo: A3, O₂ incluido, isochemical, retrieval completo; 15 coordenadas declaradas y 14 libres porque `log_P_surf` tiene prior de anchura cero en 1 bar.
- Muestreo: `N_live=800`, tolerancia de evidencia 0.5, `R=10000`; sin inflación de errores; superficie negra explícita fija en 1 bar.
- Ejecución: un proceso Python serial, un hilo de BLAS, sin MPI; corrida nueva (`resume=False`).
- Operador: solapamiento de fotones en los bordes medios de los canales; el flujo integrado se expresa como energía por canal usando la energía del fotón al centro del canal. Se mantiene enlazado al callback real de POSEIDON tanto durante el muestreo como en el postproceso.

## Diferencias respecto del retrieval histórico de 100 h

El informe histórico [A3–100 h, superficie fija y O₂](life_proxima_a3_100h_o2_fixed_surface_audit_2026-09-23.md) registra `ln Z = 884.333304 ± 0.244466`, `χ²_red=4.94` y una mediana de `log_NH3 = −8.2578`. Esos valores son el punto de comparación documentado; no son resultados de esta campaña nueva.

El manifiesto antiguo confirma la misma realización y familia de configuración (especies, número de parámetros, `N_live`, ausencia de inflación, `R`, perfil isochemical, superficie a 1 bar y O₂). No contiene la tabla completa de límites de prior, por lo que no se afirma todavía una igualdad parámetro-a-parámetro de todos los priors. La configuración resuelta de la corrida nueva queda archivada para esa auditoría.

La rejilla nativa cambia de 3.8–19 μm en el retrieval histórico a 3–20 μm en esta repetición. El alcance inicial describió la ampliación como necesaria para cubrir los bordes; el preflight midió estos en 3.9973701512–18.5767776764 μm y verificó que ya cabían dentro de 3.8–19 μm. Se corrigió esa justificación en `selected_scope.json`: 3–20 μm se conserva para seguir el contrato de rejilla del forward corregido, no porque estos canales requirieran la extensión. La nueva rejilla sigue siendo una diferencia del experimento y debe figurar como salvedad al atribuir cambios únicamente al binning. Las comparaciones numéricas finales deben considerar también la fase/discretización de la rejilla de POSEIDON.

## Preflight y lanzamiento observados

El gate del 2026-10-17 pasó antes del muestreo:

- centros y número de canales coinciden con los 31 canales LIFE;
- la rejilla nativa coincide con el forward A3 archivado;
- el callback de binning del forward model real de POSEIDON quedó enlazado durante validación, muestreo y postproceso;
- máximo error relativo de cierre del espectro sintético tras el binning: `2.2648549702353193e-14`;
- el test de forward contra la realización observada dio `χ²=42.3604584023654` (diagnóstico de truth, no `χ²` del retrieval);
- pico de PSS del preflight `6,933,415 KiB`; mínimo `MemAvailable=25,119,396 KiB`, frente a reserva requerida de `11,652,007 KiB`: gate de memoria PASS.

El manifiesto quedó en `RUNNING`, `run_pid=890`, supervisor `722`. El log anunció `POSEIDON now running` y MultiNest creó `live.points`, `resume.dat`, `ev.dat` y `phys_live.points`; los dos archivos de puntos vivos llegaron a 800 filas, la inicialización esperada para `N_live=800`. Aún no se ha confirmado una cuenta de reemplazos, por lo que esto confirma inicialización del sampler, no progreso cuantificado de la cadena.

## Rutas y reproducibilidad

- Estado/manifiesto: `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_100h_binning_corrected_20261017/`.
- Supervisor: `Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1/retrievals/a3_100h_binning_corrected_20261017.supervisor.log` y `.pid`.
- Scratch: `/home/dasan/exofarm_a3_100h_binning_corrected_20261017/`; no se comparte con la repetición A3–1000 h.
- Adaptador: `Thermal_Emission_Spectroscopy/scripts/run_life_retrieval_a3_100h_binning_corrected.py`.
- Lanzador/gates: `Thermal_Emission_Spectroscopy/scripts/launch_proxima_a3_100h_binning_corrected.py`.
- Preflight, configuración resuelta, inputs con hashes, log y manifiesto se conservan dentro del directorio de campaña.

## Qué se comparará al cerrar

Se auditarán exit code, finitud, posterior, espectro, perfil P–T, `log_X`, productos MultiNest, hashes del dataset y del operador, priors y callback activo. Después se presentarán lado a lado el `ln Z`, `χ²`/residuales, mediana e intervalos de N₂O y NH₃ y sus correlaciones relevantes. Cualquier desviación posterior no se atribuirá a la corrección del binning sin mencionar la rejilla 3–20 μm y la limitación del manifiesto de priors históricos. No se publicará una conclusión de detección a partir de esta única realización.

