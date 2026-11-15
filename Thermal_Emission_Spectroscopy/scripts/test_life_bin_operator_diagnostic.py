"""Analytic and safety tests of the isolated LIFE observation operator."""

from types import SimpleNamespace
import unittest

import numpy as np

from life_bin_operator_diagnostic import (
    LifePhotonOperator, bind_poseidon_binning, midpoint_edges,
)


class LifeOperatorTests(unittest.TestCase):
    def setUp(self):
        self.native = np.linspace(0.1, 5.0, 501)
        self.centres = np.array([1.0, 2.0, 4.0])
        self.operator = LifePhotonOperator.build(self.native, self.centres)
        self.data = {
            "instruments": ["LIFE"], "wl_data": self.centres.copy(),
            "half_bin": 0.5 * np.diff(midpoint_edges(self.centres)),
        }

    def test_constant_photon_density(self):
        result = self.operator.apply(7.0 / self.native)
        np.testing.assert_allclose(result, 7.0 / self.centres, rtol=1e-13)

    def test_matches_independent_overlap(self):
        flux = np.sin(self.native) ** 2 + 2.0
        source_edges = midpoint_edges(self.native)
        expected = []
        for i, (lo, hi) in enumerate(zip(self.operator.edges_um[:-1],
                                        self.operator.edges_um[1:])):
            overlap = np.maximum(np.minimum(source_edges[1:], hi)
                                 - np.maximum(source_edges[:-1], lo), 0)
            expected.append(np.dot(overlap, flux * self.native)
                            / (hi - lo) / self.centres[i])
        np.testing.assert_allclose(self.operator.apply(flux), expected,
                                   rtol=1e-13)

    def test_linear_operator(self):
        first, second = self.native ** 2, np.cos(self.native)
        np.testing.assert_allclose(
            self.operator.apply(2 * first + 3 * second),
            2 * self.operator.apply(first) + 3 * self.operator.apply(second),
        )

    def test_log_centres_keep_asymmetric_edges(self):
        np.testing.assert_array_equal(self.operator.edges_um,
                                      [0.5, 1.5, 3.0, 5.0])
        self.assertNotEqual((1.5 + 3.0) / 2, self.centres[1])

    def test_uncovered_channel_rejected(self):
        with self.assertRaises(ValueError):
            LifePhotonOperator.build(np.array([1.0, 2.0]), self.centres)

    def test_invalid_centres_rejected(self):
        for grid in ([1, 1, 2], [2, 1], [1, np.nan], [0, 1]):
            with self.assertRaises(ValueError):
                midpoint_edges(np.array(grid, dtype=float))

    def test_nonfinite_flux_rejected(self):
        invalid = np.ones_like(self.native)
        invalid[0] = np.nan
        with self.assertRaises(ValueError):
            self.operator.apply(invalid)

    def test_retrieval_entry_uses_exact_operator(self):
        flux = self.native ** 2
        np.testing.assert_array_equal(
            self.operator.poseidon_entry(flux, self.native, self.data),
            self.operator.apply(flux),
        )

    def test_changed_native_grid_rejected(self):
        with self.assertRaises(ValueError):
            self.operator.poseidon_entry(self.native, self.native + 1e-5,
                                         self.data)

    def test_changed_dataset_rejected(self):
        changed = dict(self.data, wl_data=self.centres + 0.01)
        with self.assertRaises(ValueError):
            self.operator.poseidon_entry(self.native, self.native, changed)
        changed = dict(self.data, instruments=["MIRI"])
        with self.assertRaises(ValueError):
            self.operator.poseidon_entry(self.native, self.native, changed)

    def test_binding_restored_on_exception(self):
        original = lambda *args: None
        module = SimpleNamespace(bin_spectrum_to_data=original)
        with self.assertRaises(RuntimeError):
            with bind_poseidon_binning(self.operator, module):
                self.assertIsNot(module.bin_spectrum_to_data, original)
                raise RuntimeError("Intentional diagnostic interruption")
        self.assertIs(module.bin_spectrum_to_data, original)

    def test_arrays_are_immutable(self):
        with self.assertRaises(ValueError):
            self.operator.native_um[0] = 1.0


if __name__ == "__main__":
    unittest.main()
