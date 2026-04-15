import os
import warnings
from pathlib import Path

import numpy as np
from mpi4py import MPI

# ============================================================
# Ajustes de entorno para MPI / BLAS / backend
# ============================================================
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["CBLAS_NUM_THREADS"] = "1"
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("MPLBACKEND", "Agg")

# Silencia el warning repetitivo de pysynphot
warnings.filterwarnings("ignore", category=UserWarning, module=r"pysynphot")

# ============================================================
# Monkey-patch: shared_memory_array forzando float64
# Debe ir ANTES de importar POSEIDON.core
# ============================================================
import POSEIDON.utility as _U


def _shared_memory_array_force64(node_rank, node_comm, shape):
    """
    Reemplaza POSEIDON.utility.shared_memory_array para forzar
    asignación en float64 compatible con MPI.DOUBLE.
    """
    dtype = np.float64
    itemsize = np.dtype(dtype).itemsize

    # Solo el rank 0 del nodo reserva el bloque
    nbytes = int(np.prod(shape)) * itemsize if node_rank == 0 else 0

    # Ventana de memoria compartida MPI
    win = MPI.Win.Allocate_shared(nbytes, itemsize, comm=node_comm)

    # Obtener el buffer del segmento compartido principal
    buf, _ = win.Shared_query(MPI.PROC_NULL)

    # Construir el ndarray sobre ese buffer
    arr = np.ndarray(buffer=buf, dtype=dtype, shape=shape)

    return arr, win


# Aplicar el parche
_U.shared_memory_array = _shared_memory_array_force64

# ============================================================
# Imports de POSEIDON
# ============================================================
from POSEIDON.constants import R_Sun, R_E, M_E
from POSEIDON.core import (
    create_star,
    create_planet,
    define_model,
    wl_grid_constant_R,
    read_opacities,
    load_data,
    set_priors,
)

# ============================================================
# Configuración física del sistema
# ============================================================
PLANET_NAME = "TRAPPIST-1e"

R_S = 0.11697 * R_Sun
T_S = 2559.0
MET_S = 0.04
LOG_G_S = 5.21

R_P = 0.917985 * R_E
M_P = 0.6356 * M_E
T_EQ = 255.0

# ============================================================
# Configuración del retrieval
# ============================================================
BULK_SPECIES = ["N2"]
PARAM_SPECIES = ["H2O", "CO2", "CH4", "O2", "O3", "N2O", "NH3"]

WL_MIN = 0.5
WL_MAX = 14.0
R_MODEL = 10000

P_MIN = 1.0e-10
P_MAX = 10.0
N_LAYERS = 100
P_REF = 1.0

OPACITY_TREATMENT = "opacity_sampling"
T_FINE_MIN = 100.0
T_FINE_MAX = 500.0
T_FINE_STEP = 10.0

LOG_P_FINE_MIN = -10.0
LOG_P_FINE_MAX = 0.0
LOG_P_FINE_STEP = 0.2

INSTRUMENTS = [
    "JWST_NIRSpec_PRISM",
    "JWST_MIRI_LRS",
]

SCENARIO_LABELS = {
    "A0": "Trappist_A0_PreAgri",
    "A3": "Trappist_A3_Extreme",
}

# Pares de observaciones sintéticas usados en el flujo principal:
# NIRSpec Prism = N tránsitos y MIRI LRS = N tránsitos.
OBSERVATION_TRANSIT_COUNTS = [5, 10, 20]

# Carpeta común con las plantillas de PandExo de 1 tránsito y los
# datasets sintéticos generados para los pares de observaciones.
SYNTHETIC_DATA_DIR = Path(
    "POSEIDON_output/TRAPPIST-1e/synthetic_data/base_1transit"
)

# Prior superior de abundancias libres.
# Si quieres abrir más el espacio, puedes cambiar -1.0 -> 0.0,
# pero -1.0 suele ser una opción más conservadora con 7 especies libres.
LOG_X_LOWER = -10.0
LOG_X_UPPER = -1.0

T_LOWER = 200.0
T_UPPER = 500.0


# ============================================================
# Objetos base
# ============================================================
def create_system():
    star = create_star(
        R_S,
        T_S,
        LOG_G_S,
        MET_S,
        stellar_grid="phoenix",
    )

    planet = create_planet(
        PLANET_NAME,
        R_P,
        mass=M_P,
        T_eq=T_EQ,
    )

    return star, planet


def create_grids():
    P = np.logspace(np.log10(P_MAX), np.log10(P_MIN), N_LAYERS)
    wl = wl_grid_constant_R(WL_MIN, WL_MAX, R_MODEL)

    T_fine = np.arange(T_FINE_MIN, T_FINE_MAX + T_FINE_STEP, T_FINE_STEP)
    log_P_fine = np.arange(
        LOG_P_FINE_MIN,
        LOG_P_FINE_MAX + LOG_P_FINE_STEP,
        LOG_P_FINE_STEP,
    )

    return P, wl, T_fine, log_P_fine


# ============================================================
# Modelo de retrieval: isotérmico + abundancias constantes
# ============================================================
def make_retrieval_model(scenario_key: str, n_transits: int):
    if scenario_key not in SCENARIO_LABELS:
        raise ValueError(
            f"scenario_key debe ser una de {list(SCENARIO_LABELS.keys())}"
        )

    model_name = (
        f"TRAPPIST1e_{scenario_key}_retrieval_"
        f"isotherm_isochem_{n_transits}transits"
    )

    model = define_model(
        model_name,
        BULK_SPECIES,
        PARAM_SPECIES,
        PT_profile="isotherm",
        X_profile="isochem",
        radius_unit="R_E",
        surface=False,
    )

    return model


def make_opacity(model, wl, T_fine, log_P_fine):
    opac = read_opacities(
        model,
        wl,
        OPACITY_TREATMENT,
        T_fine,
        log_P_fine,
        opacity_database="High-T",
    )
    return opac


# ============================================================
# Datos sintéticos ya generados
# ============================================================
def synthetic_dataset_names(scenario_key: str, n_transits: int):
    label = SCENARIO_LABELS[scenario_key]

    datasets = [
        f"{PLANET_NAME}_SYNTHETIC_JWST_NIRSpec_PRISM_{label}_N_trans_{n_transits}.dat",
        f"{PLANET_NAME}_SYNTHETIC_JWST_MIRI_LRS_{label}_N_trans_{n_transits}.dat",
    ]
    return datasets


def load_synthetic_data(wl, scenario_key: str, n_transits: int):
    datasets = synthetic_dataset_names(scenario_key, n_transits)

    for filename in datasets:
        full_path = SYNTHETIC_DATA_DIR / filename
        if not full_path.exists():
            raise FileNotFoundError(
                f"No encontré {full_path}\n"
                "Primero genera estos sintéticos en "
                "Plot_Transmission_Spectra_TRAPPIST.ipynb con "
                "generate_syn_data_from_file(...)."
            )

    data_new = load_data(
        str(SYNTHETIC_DATA_DIR),
        datasets,
        INSTRUMENTS,
        wl,
        skiprows=1,
        wl_unit="micron",
        bin_width="half",
        spectrum_unit="(Rp/Rs)^2",
    )

    return data_new, datasets


# ============================================================
# Priors
# ============================================================
def make_priors(planet, star, model, data):
    prior_types = {
        "T": "uniform",
        "R_p_ref": "uniform",
        "log_X": "uniform",
    }

    prior_ranges = {
        "T": [T_LOWER, T_UPPER],
        "R_p_ref": [0.9 * R_P, 1.1 * R_P],
        "log_X": [LOG_X_LOWER, LOG_X_UPPER],
    }

    priors = set_priors(
        planet,
        star,
        model,
        data,
        prior_types,
        prior_ranges,
    )

    return priors


# ============================================================
# Empaquetador general
# ============================================================
def setup_retrieval_problem(scenario_key: str, n_transits: int):
    star, planet = create_system()
    P, wl, T_fine, log_P_fine = create_grids()

    model = make_retrieval_model(scenario_key, n_transits)
    opac = make_opacity(model, wl, T_fine, log_P_fine)

    data_new, datasets = load_synthetic_data(wl, scenario_key, n_transits)
    priors = make_priors(planet, star, model, data_new)

    return {
        "scenario_key": scenario_key,
        "scenario_label": SCENARIO_LABELS[scenario_key],
        "n_transits": n_transits,
        "star": star,
        "planet": planet,
        "P": P,
        "P_ref": P_REF,
        "wl": wl,
        "opac": opac,
        "model": model,
        "data_new": data_new,
        "datasets": datasets,
        "priors": priors,
    }
