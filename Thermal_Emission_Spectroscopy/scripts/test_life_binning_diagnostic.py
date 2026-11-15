"""Hand-checkable tests of overlap integration and logarithmic-centre offset."""

import unittest
import numpy as np
from audit_proxima_a3_retrieval_residuals import bin_edges
from diagnose_proxima_life_bin_components import integrate_cells


class BinningDiagnostic(unittest.TestCase):
    def test_constant_field_preserved(self):
        wl=np.linspace(.1,5,1000)
        result=integrate_cells(wl,np.full_like(wl,7),np.array([1,2]),np.array([2,4]))
        np.testing.assert_allclose(result,7,atol=1e-12)

    def test_log_centres_are_not_midpoints(self):
        centres=np.array([1.,2.,4.])
        edges=bin_edges(centres)
        self.assertEqual(edges[1],1.5)
        self.assertEqual(edges[2],3.)
        self.assertEqual((edges[1]+edges[2])/2-centres[1],.25)
        half=(edges[2]-edges[1])/2
        self.assertEqual(centres[1]-half,1.25)
        self.assertEqual(centres[1]+half,2.75)

    def test_uncovered_bin_rejected(self):
        with self.assertRaises(AssertionError):
            integrate_cells(np.array([1.,2.,3.]),np.ones(3),np.array([0.]),np.array([1.]))


if __name__=="__main__":
    unittest.main()
