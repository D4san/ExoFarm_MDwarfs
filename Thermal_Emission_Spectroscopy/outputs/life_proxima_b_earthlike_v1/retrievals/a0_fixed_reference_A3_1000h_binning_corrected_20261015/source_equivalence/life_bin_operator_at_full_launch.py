"""Isolated LIFE generator-compatible energy-flux observation operator.

This module never changes datasets or installed POSEIDON files. The operator
represents the existing centre-derived, photon-space SpectRes convention;
it is not a newly calibrated instrumental response. A process-local binding
allows diagnostics to use the same entry point as POSEIDON's forward model.
"""

from contextlib import contextmanager
from dataclasses import dataclass
import importlib

import numpy as np


def midpoint_edges(centres):
    """Compute SpectRes cell edges from an increasing grid, in microns."""
    centres = np.asarray(centres, dtype=np.float64)
    if (centres.ndim != 1 or centres.size < 2
            or not np.isfinite(centres).all()
            or np.any(centres <= 0) or np.any(np.diff(centres) <= 0)):
        raise ValueError("Expected finite positive increasing centres")
    edges = np.empty(centres.size + 1)
    edges[1:-1] = 0.5 * (centres[:-1] + centres[1:])
    edges[0] = centres[0] - 0.5 * (centres[1] - centres[0])
    edges[-1] = centres[-1] + 0.5 * (centres[-1] - centres[-2])
    if edges[0] <= 0:
        raise ValueError("Wavelength cell edges must remain positive")
    return edges


@dataclass(frozen=True)
class LifePhotonOperator:
    """Precomputed overlap weights for Fp in W m^-2 m^-1.

    hc cancels between native photon conversion and channel energy conversion:
    W[k,i] = overlap[k,i] / width[k] * lambda_native[i] / lambda_channel[k].
    Only nonzero overlaps are retained; bincount avoids a dense matrix.
    """

    native_um: np.ndarray
    centres_um: np.ndarray
    edges_um: np.ndarray
    rows: np.ndarray
    columns: np.ndarray
    weights: np.ndarray

    @classmethod
    def build(cls, native_um, centres_um):
        native = np.array(native_um, dtype=np.float64, copy=True)
        centres = np.array(centres_um, dtype=np.float64, copy=True)
        native_edges = midpoint_edges(native)
        edges = midpoint_edges(centres)
        if edges[0] < native_edges[0] or edges[-1] > native_edges[-1]:
            raise ValueError("Native wavelength cells do not cover LIFE bins")
        rows, columns, weights = [], [], []
        for channel, (left, right) in enumerate(zip(edges[:-1], edges[1:])):
            overlap = np.maximum(
                np.minimum(native_edges[1:], right)
                - np.maximum(native_edges[:-1], left), 0.0,
            )
            width = right - left
            if not np.isclose(overlap.sum(), width, rtol=1e-12, atol=1e-13):
                raise ValueError(f"Incomplete coverage of channel {channel}")
            selected = np.flatnonzero(overlap > 0)
            columns.extend(selected)
            rows.extend(np.full(selected.size, channel, dtype=np.int64))
            weights.extend(overlap[selected] / width
                           * native[selected] / centres[channel])
        arrays = (native, centres, edges, np.asarray(rows, dtype=np.int64),
                  np.asarray(columns, dtype=np.int64), np.asarray(weights))
        for array in arrays:
            array.setflags(write=False)
        return cls(*arrays)

    def apply(self, energy_flux):
        flux = np.asarray(energy_flux, dtype=np.float64)
        if flux.shape != self.native_um.shape or not np.isfinite(flux).all():
            raise ValueError("Expected one finite native Fp spectrum")
        return np.bincount(
            self.rows, weights=self.weights * flux[self.columns],
            minlength=self.centres_um.size,
        )

    def poseidon_entry(self, spectrum, wavelength, data):
        """Reject changed grids/instruments; never fall back silently."""
        if not np.array_equal(wavelength, self.native_um):
            raise ValueError("Diagnostic operator requires its frozen native grid")
        if list(data["instruments"]) != ["LIFE"]:
            raise ValueError("Diagnostic binding accepts only one LIFE dataset")
        centres = np.asarray(data["wl_data"])
        if (centres.shape != self.centres_um.shape
                or not np.allclose(centres, self.centres_um,
                                   rtol=0, atol=5e-6)):
            raise ValueError("Dataset centres differ from the frozen LIFE grid")
        half_width = np.asarray(data["half_bin"])
        expected_half = 0.5 * np.diff(self.edges_um)
        if (half_width.shape != expected_half.shape
                or not np.allclose(half_width, expected_half,
                                   rtol=0, atol=5e-6)):
            raise ValueError("Dataset widths differ from generator provenance")
        return self.apply(spectrum)


@contextmanager
def bind_poseidon_binning(operator, module=None):
    """Temporarily bind the retrieval forward-model global, then restore it.

    For diagnostics only. No MultiNest run is dispatched. The optional module
    permits a dependency-free unit test of restoration, including exceptions.
    """
    if module is None:
        module = importlib.import_module("POSEIDON.retrieval")
    original = module.bin_spectrum_to_data
    module.bin_spectrum_to_data = operator.poseidon_entry
    try:
        yield module
    finally:
        module.bin_spectrum_to_data = original
