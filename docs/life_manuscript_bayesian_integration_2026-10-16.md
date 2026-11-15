# Integración del análisis bayesiano LIFE en el manuscrito abierto

Fecha: 2026-10-16, America/Bogota. Estado: texto y bibliografía editados en
su ubicación original; compilación integrada bloqueada por una dependencia
preexistente. El usuario autorizó incorporar el análisis discutido y pidió
evitar la palabra «indeterminado» en las tablas.

## Artefactos y cambios

- Manuscrito: `E:/Down/ExoFarms_Photochemistry_v2.tex`.
- Bibliografía: `E:/Down/reference.bib`.
- [Registro de hashes](evidence/life_manuscript_integration_2026-10-16/change_record.json).
- [Diff del manuscrito](evidence/life_manuscript_integration_2026-10-16/ExoFarms_Photochemistry_v2.tex.diff).
- [Diff bibliográfico](evidence/life_manuscript_integration_2026-10-16/reference.bib.diff).

Se reemplazó el pendiente de detección molecular en Atmospheric Retrieval
with LIFE y los párrafos que sobreinterpretaban la separación descriptiva de
NH3. La secuencia ahora presenta desplazamiento, evidencia molecular,
probabilidades de región y odds, magnitud del enriquecimiento y restricciones
A0. Se añadieron cuatro tablas: omisión molecular, regiones ≥ A1, magnitud e
intervalos A3–100 h y contrastes con A0. A1/A3 se intercalan por exposición;
ln B y sigma tienen filas explícitas en la tabla molecular.

Se definieron evidencia, B, ln B, niveles de interpretación y calibración
auxiliar Benneke–Seager, conservando la distinción frente a z descriptivo.
Las regiones individuales y conjunta incorporan probabilidades posteriores,
masas previas nominales, K y ln K. Se explica por qué probabilidad elevada no
implica aprendizaje positivo y por qué las dos cantidades no son pruebas
independientes. Se usan ≈0 % y ≈100 %; los factores dependientes de colas no
muestreadas aparecen con raya y una explicación en el pie de tabla.

El análisis A3–100 h incluye intervalos de NH3, su cola hacia valores bajos,
su apoyo positivo todavía débil y los contrastes entre restricciones A0.
Se conserva un pendiente explícito para incorporar A3–1000 h después de su
análisis y aceptación separados. Se añadió una subsección de Discusión con
los mecanismos nitrogenados, la diferencia entre abundancias y causalidad,
los límites del prior y de recuperación y la discrepancia conocida de
integración espectral. No se generaron nuevos retrievals ni se modificaron
las tablas numéricas de origen.

Se incorporaron a `reference.bib` Benneke & Seager (2013), DOI
10.1088/0004-637X/778/2/153, y Wogan et al. (2026), DOI
10.3847/1538-4357/ae6646. El primero se comprobó en su
[fuente primaria](https://arxiv.org/abs/1306.6325); para Wogan se reutilizó
la lectura verificada del PDF publicado documentada en la nota metodológica.

## Procedencia numérica

- [Comparaciones de omisión y convención sigma](life_proxima_loo_sigma_lin_convention_2026-10-10.md): 36 contrastes sobre seis datasets.
- [Regiones A1 y sensibilidad condicional](life_proxima_a1_posterior_regions_2026-10-15.md): 12 filas marginales y seis conjuntas.
- [Restricciones A0 aceptadas con salvedad](life_proxima_a3_100h_a0_fixed_audit_2026-10-11.md): tres modelos adicionales, mismo dataset A3–100 h.
- [Adaptación de Wogan](life_proxima_wogan_abundance_region_bayes_2026-10-15.md).

La serie histórica conserva su limitación de binning. Los K de región se
etiquetan nominales, pendientes de validar el prior efectivo. Su inserción en
el borrador no implica aceptación científica de una atribución agrícola ni
reemplaza la repetición sobre productos corregidos aceptados.

## Comprobaciones y bloqueo

Se verificaron los hashes guardados, las claves bibliográficas nuevas, las
13 etiquetas añadidas sin duplicación, los pares de entornos y las columnas
de las cuatro tablas. Se preservaron BOM y saltos de línea de los archivos.
Los cambios anteriores al bloque de resultados se limitaron a la aclaración
del z descriptivo y a reemplazar «atlas» por «figure» en el pie correspondiente.

La herramienta integrada `compile_latex_document` se ejecutó antes y después
de guardar. Ambas ejecuciones se detuvieron con:

```text
LaTeX Error: File `aastex701.cls' not found.
No pages of output.
```

No se cambió la clase del manuscrito ni se compiló un PDF alternativo.
No se confirmó la compilación ni se evaluó visualmente la disposición final.
Siguiente paso: disponer de la clase/proyecto necesarios en el compilador
integrado y revisar el PDF del mismo documento; mantener pendientes el prior
efectivo y la incorporación de productos corregidos aceptados.
