# Ejecución global LPJmL A1 con MPI en otro PC

**Fecha:** 2026-09-06
**Alcance:** primer ejemplo global de Tierra actual (`A1`) con flujos agrícolas
de `N2O` y `NH3`. No intenta todavía reproducir toda la Tabla 3 de Franck et
al. (2011).

## Resultado que se busca

La campaña ejecuta una simulación natural global para producir el restart de
1700 y, a partir de él, una simulación histórica 1901--2005 con uso de suelo,
fertilizante, estiércol, ciclo de N, ríos, embalses, uso de agua e irrigación
limitada. Se conservan los años 1996--2005 y se integran:

```text
N2O-N = n2o_nit_agr + n2o_denit_agr
NH3-N = nh3_agr
```

Las salidas LPJmL están en masa de N por área y año. El posprocesamiento las
integra sobre el área terrestre, informa `TgN yr-1` y, solamente después de
aceptar la cobertura global, convierte a moléculas `cm-2 s-1` sobre
`4 pi R_earth^2`. Para `N2O` divide por dos átomos de N por molécula; para
`NH3`, por uno.

## Decisiones ya congeladas

| Decisión | Elección | Razón |
| --- | --- | --- |
| Versión | LPJmL `v6.0.6`, commit `5af44a1ed023279a23c28d6dfe76945b97aaac57` | Es la versión validada por el piloto; evita deriva con `master`. |
| Entradas | Zenodo 19064225, archivo `lpjml6-0-5_standard_input.tar.gz`, MD5 `682d8b894d7983301313e9d60a49483b` | Conjunto público oficial ya verificado. |
| Primera pregunta global | Tierra actual A1, no potencial de capacidad de carga | Produce un ejemplo físicamente interpretable de flujos agrícolas antes de reconstruir todos los escenarios Franck. |
| Paralelismo | MPI con MPICH, compilación `-DUSE_MPI`; `make -j1` | LPJmL distribuye las celdas, pero la compilación serial evita carreras del sistema de build. |
| Salida NetCDF | Una salida coordinada MPI sobre la malla compacta de celdas terrestres (`global_netcdf=false`) | Evita un cubo global casi vacío y no exige concatenar archivos por proceso. |
| Recuperación | Fases `spinup` y `a1` en el mismo directorio persistente | El restart natural es costoso y debe poder reutilizarse sin repetir el spin-up. |
| Recursos | No fijar el número de ranks desde este PC | Debe elegirse con CPU, RAM y disco medidos en el PC de ejecución. |

## Requisitos del PC

Ruta recomendada: Windows 10/11 con WSL2 y Ubuntu 22.04/24.04, o Linux nativo.
Se recomienda al menos **150 GiB libres** si archivo, extracción, fuente,
restart y resultados estarán en el mismo volumen. El runtime, la fuente de
LPJmL y la campaña deben estar en el sistema de archivos Linux (`$HOME`), no
en `/mnt/c`, para evitar la penalización de I/O de WSL. El archivo de 37.8 GB
puede permanecer en un disco Windows/externo; para velocidad, la extracción de
66.3 GB debería estar en Linux si hay espacio.

Antes de empezar hay que responder en ese PC:

1. ¿Windows con WSL2, o Linux nativo? ¿Qué versión de Ubuntu?
2. ¿Cuántos núcleos físicos/lógicos y cuánta RAM hay?
3. ¿Cuánto espacio libre hay en el volumen Linux?
4. ¿Dónde están el repositorio y el archivo de entrada?
5. ¿Hay red disponible y permiso `sudo` para instalar paquetes?

Si WSL no existe, desde PowerShell como administrador:

```powershell
wsl --install -d Ubuntu
```

Reiniciar Windows cuando se solicite, abrir Ubuntu y terminar la creación del
usuario. Todo lo siguiente se ejecuta **dentro de Ubuntu**.

## 1. Definir rutas sin codificarlas en los scripts

Adapte solo estas variables a la ubicación real del repositorio transferido:

```bash
export EXOFARM_REPO=/mnt/c/ruta/al/ExoFarm_MDwarfs
export LPJ_WORKFLOW="$EXOFARM_REPO/Agricultural_Fluxes_LPJmL/workflows/franck2011_reproduction"
export LPJ_RUNTIME="$HOME/exofarm-lpjml-runtime"
export LPJ_INPUT="$HOME/lpjml-data/public_standard"
export LPJ_ARCHIVE=/mnt/d/lpjml-data/lpjml6-0-5_standard_input.tar.gz
export LPJ_CAMPAIGN="$HOME/exofarm-lpjml-runs/global_a1_001"
```

El repositorio puede leerse desde `/mnt/c`; los binarios y resultados no.

## 2. Instalar y compilar LPJmL con MPI

```bash
bash "$LPJ_WORKFLOW/setup_lpjml_mpi.sh" \
  --runtime-root "$LPJ_RUNTIME" \
  --install-deps
```

El script instala dependencias Ubuntu, clona únicamente la etiqueta `v6.0.6`,
verifica el commit, exige `mpicc`, configura `USE_MPI`, compila `main` y
`utils` con `make -j1`, ejecuta `make test` y escribe
`$LPJ_RUNTIME/lpjml_mpi_installation.txt`. Se detiene si encuentra una carpeta
preexistente con otro commit; no la reemplaza.

Fuente resultante:

```bash
export LPJML_ROOT="$LPJ_RUNTIME/LPJmL-6.0.6"
```

## 3. Obtener y verificar los datos oficiales

La opción preferida es transferir el archivo ya verificado desde el PC actual.
Si hay que descargarlo de nuevo:

```bash
mkdir -p "$(dirname "$LPJ_ARCHIVE")"
curl -L --continue-at - \
  'https://zenodo.org/records/19064225/files/lpjml6-0-5_standard_input.tar.gz?download=1' \
  --output "$LPJ_ARCHIVE"
```

Verificar y extraer sin sobrescribir una carpeta existente:

```bash
bash "$LPJ_WORKFLOW/verify_input_dataset.sh" \
  --archive "$LPJ_ARCHIVE" \
  --input-root "$LPJ_INPUT" \
  --extract
```

Aceptación obligatoria: 37,763,601,476 bytes y el MD5 fijado para el archivo;
76 archivos y 66,338,995,720 bytes tras extracción.

## 4. Auditar recursos y configuración

```bash
bash "$LPJ_WORKFLOW/check_other_pc.sh" \
  --lpjml-root "$LPJML_ROOT" \
  --input-root "$LPJ_INPUT" | tee "$LPJ_RUNTIME/readiness.txt"
```

No continuar si termina con `readiness=FAIL`. Registrar CPU, RAM, sistema de
archivos y espacio libre. Para la primera prueba use como máximo el número de
núcleos físicos; si no se conoce, comenzar conservadoramente con 4 u 8 ranks.
Más procesos no garantizan menor tiempo porque la escritura y el restart tienen
componentes seriales.

## 5. Smoke test MPI real

Este test usa ocho celdas y dos procesos. Ejecuta spin-up, restart, A1 y lectura
de NetCDF. Puede tardar, pero es mucho menor que la campaña global y sus flujos
son deliberadamente **no planetarios**.

```bash
bash "$LPJ_WORKFLOW/run_mpi_smoke.sh" \
  --lpjml-root "$LPJML_ROOT" \
  --input-root "$LPJ_INPUT" \
  --results-dir "$HOME/exofarm-lpjml-runs/mpi_smoke_001" \
  --mpi-ranks 2
```

Aceptar solo si aparece `mpi_smoke=PASS`, ambos escenarios tienen código cero,
el restart no está vacío y el análisis genera `nitrogen_flux_summary.json`.

## 6. Preparar la campaña global sin arrancarla

Elegir ranks después del reporte de recursos. Ejemplo conservador:

```bash
export LPJ_RANKS=8
bash "$LPJ_WORKFLOW/run_global_a1_mpi.sh" \
  --lpjml-root "$LPJML_ROOT" \
  --input-root "$LPJ_INPUT" \
  --campaign-dir "$LPJ_CAMPAIGN" \
  --mpi-ranks "$LPJ_RANKS" \
  --phase all \
  --dry-run
```

El dry run verifica commit, ejecutables, MPI, número de CPUs, entradas y genera
las configuraciones resueltas, pero no inicia LPJmL.

## 7. Ejecutar en dos fases recuperables

Evitar suspensión/hibernación del PC. Mantener la terminal en `tmux` si está
disponible. Primero:

```bash
bash "$LPJ_WORKFLOW/run_global_a1_mpi.sh" \
  --lpjml-root "$LPJML_ROOT" \
  --input-root "$LPJ_INPUT" \
  --campaign-dir "$LPJ_CAMPAIGN" \
  --mpi-ranks "$LPJ_RANKS" \
  --phase spinup
```

Comprobar:

```bash
tail -n 50 "$LPJ_CAMPAIGN/spinup_natural/stderr.log"
ls -lh "$LPJ_CAMPAIGN/spinup_natural/restart/restart_1700_nv_stdfire.lpj"
```

Luego A1, reutilizando el restart validado:

```bash
bash "$LPJ_WORKFLOW/run_global_a1_mpi.sh" \
  --lpjml-root "$LPJML_ROOT" \
  --input-root "$LPJ_INPUT" \
  --campaign-dir "$LPJ_CAMPAIGN" \
  --mpi-ranks "$LPJ_RANKS" \
  --phase a1
```

El runner guarda logs, estado temporal y SHA-256 del restart. Si A1 falla, no
se repite el spin-up: se corrige la causa y se relanza únicamente `--phase a1`.
Un spin-up interrumpido no se declara recuperable salvo que LPJmL haya escrito
un checkpoint explícitamente aceptado.

## 8. Integrar N2O y NH3

Después de confirmar que A1 terminó y que existen los NetCDF 1996--2005:

```bash
python3 "$LPJ_WORKFLOW/analyze_n_fluxes.py" \
  --output-dir "$LPJ_CAMPAIGN/a1_2005_n/output" \
  --coverage global
```

Productos:

- `analysis/nitrogen_flux_timeseries.csv`;
- `analysis/nitrogen_flux_summary.json`.

## Criterios de aceptación científica

La campaña no se convierte en forzamiento VULCAN solo porque termine con código
cero. Hay que comprobar:

1. commit, configuración resuelta, dataset y checksum archivados;
2. restart completo y checksum registrado;
3. diez años 1996--2005 en cada flujo anual;
4. unidades `gN/m2/yr`, dimensiones iguales y valores finitos;
5. cobertura de todas las celdas terrestres y área representada plausible;
6. balance de N: fertilización/estiércol frente a uptake, lixiviación y pérdidas;
7. mapas de `N2O`, `NH3` y fracción agrícola sin discontinuidades MPI;
8. comparación del promedio molecular global con el benchmark A1 actualmente
   prescrito en VULCAN, sin sustituirlo automáticamente;
9. informe fechado en `docs/` y registro de campaña en `experiments/README.md`.

Los valores LPJmL y los flujos A1 actuales de VULCAN son construcciones
independientes. Cualquier discrepancia debe investigarse; no se corrige
reescalando LPJmL para que coincidan.

## Lo que queda fuera de esta primera ejecución

No se ejecuta todavía la rama de rendimiento potencial global ni los escenarios
Genghis-Khan, save-forests, Burger o wheat-maize-rice. Para reproducirlos aún
faltan el mapeo CFT moderno, la máscara PNV, el umbral de productividad y la
regla moderna de segunda cosecha. Esta separación permite obtener primero un
ejemplo global actual de `N2O`/`NH3` que sea auditable.
