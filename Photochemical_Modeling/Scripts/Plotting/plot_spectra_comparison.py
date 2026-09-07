"""Compare the VULCAN stellar-surface spectra used by the photochemical runs.

The plot keeps the original Sun/TRAPPIST-1 comparison and adds the validated
MUSCLES v22 Proxima Centauri spectrum.  The three input files share VULCAN's
surface-flux convention: wavelength in nm and flux in
erg cm^-2 s^-1 nm^-1.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[3]
SPECTRUM_FILES = {
    "Sun (G2V)": REPO_ROOT / "VULCAN" / "atm" / "stellar_flux" /
                 "Gueymard_solar.txt",
    "TRAPPIST-1 (M8V)": REPO_ROOT / "VULCAN" / "atm" / "stellar_flux" /
                       "TRAPPIST1_surface.txt",
    "Proxima Centauri (M5.5V)": REPO_ROOT / "VULCAN" / "atm" /
                                "stellar_flux" / "ProximaCen_surface.txt",
}
SPECTRUM_COLOURS = {
    "Sun (G2V)": "#E59500",                 # golden_orange
    "TRAPPIST-1 (M8V)": "#840032",          # dark_amaranth
    "Proxima Centauri (M5.5V)": "#002642",  # deep_space_blue
}
OUTPUT_DIRS = (
    REPO_ROOT / "Photochemical_Modeling" / "Results" / "Plots",
    REPO_ROOT / "Photochemical_Modeling" / "final_products" / "figures",
)
OUTPUT_STEM = "stellar_spectra_comparison"
WAVELENGTH_MIN_NM = 10.0
WAVELENGTH_MAX_NM = 3000.0


def read_spectrum(filepath, wavelength_min=WAVELENGTH_MIN_NM,
                  wavelength_max=WAVELENGTH_MAX_NM):
    """Read and validate a two-column VULCAN spectrum in the plotted range."""
    data = np.genfromtxt(filepath, comments="#", dtype=float)
    if data.ndim != 2 or data.shape[1] < 2:
        raise ValueError(f"Expected at least two columns in {filepath}")

    wave = data[:, 0]
    flux = data[:, 1]
    valid = (
        np.isfinite(wave) & np.isfinite(flux) &
        (wave >= wavelength_min) & (wave <= wavelength_max) &
        (wave > 0) & (flux > 0)
    )
    if not np.any(valid):
        raise ValueError(f"No positive samples in the plotting range for {filepath}")
    return wave[valid], flux[valid]


def plot_spectra():
    print("Generating Sun/TRAPPIST-1/Proxima stellar spectra comparison...")

    spectra = {
        label: read_spectrum(path)
        for label, path in SPECTRUM_FILES.items()
    }

    # Create Plot
    fig, ax = plt.subplots(figsize=(10, 6))

    for label, (wave, flux) in spectra.items():
        ax.plot(wave, flux, label=label, color=SPECTRUM_COLOURS[label],
                linewidth=1, alpha=0.55)

    # Formatting
    ax.set_yscale("log")
    ax.set_xscale("log")

    ax.set_xlabel("Wavelength (nm)", fontsize=12)
    ax.set_ylabel(
        "Stellar Surface Flux (erg cm$^{-2}$ s$^{-1}$ nm$^{-1}$)",
        fontsize=12,
    )
    ax.set_title("Stellar Spectra Comparison", fontsize=14, fontweight="bold")

    # Limits - Focus on relevant UV-Vis-IR range for photochemistry
    ax.set_xlim(WAVELENGTH_MIN_NM, WAVELENGTH_MAX_NM)
    ax.set_ylim(1e0, 1e8)

    # Add UV region highlight (important for photochemistry)
    ax.axvspan(
        WAVELENGTH_MIN_NM, 400, alpha=0.18, color="#dddddd",
        label="UV Region (<400 nm)",
    )

    ax.legend(fontsize=10, framealpha=0.78)
    ax.grid(True, which="both", ls="-", alpha=0.15)

    plt.tight_layout()

    for output_dir in OUTPUT_DIRS:
        output_dir.mkdir(parents=True, exist_ok=True)
        for extension in ("png", "pdf"):
            output_path = output_dir / f"{OUTPUT_STEM}.{extension}"
            fig.savefig(output_path, dpi=300, bbox_inches="tight")
            print(f"Plot saved to {output_path.relative_to(REPO_ROOT)}")

    plt.close(fig)


if __name__ == "__main__":
    plot_spectra()
