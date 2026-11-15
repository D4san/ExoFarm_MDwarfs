"""Regression controls for strict fixed-coordinate moment auditing."""

import copy
import math
import tempfile
import unittest
from pathlib import Path

from audit_proxima_a0_fixed_reference import (
    audit_derived_moments,
    check_coordinates,
    validate_fixed_moment_salvedad,
)
from report_proxima_loo_lin_sigma import calibrated_sigma, check_calibration


class TestIndependentAudit(unittest.TestCase):
    def setUp(self):
        # Windows sandbox temp paths may be inaccessible; use the workspace.
        self.directory = tempfile.TemporaryDirectory(
            prefix="exofarm_a0_audit_", dir=Path(__file__).resolve().parent
        )
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.header = [f"parameter_{index}" for index in range(15)]
        self.header[12] = "log_N2O"
        self.row = [0.0] * 62
        self.row[60] = 854.8931804139012

    def write_fixture(self, row=None, stats=""):
        summary = self.root / "summary.txt"
        statistics = self.root / "stats.dat"
        summary.write_text(" ".join(map(str, row or self.row)) + "\n")
        statistics.write_text(stats)
        return summary, statistics

    def test_finite_summary_passes(self):
        result = audit_derived_moments(*self.write_fixture(), self.header, {})
        self.assertEqual(result["issues"], [])
        self.assertEqual(result["shape"], [1, 62])

    def test_fixed_nan_is_recorded_not_accepted_or_replaced(self):
        self.row[27] = math.nan
        paths = self.write_fixture(stats="13 -6.884325289636784 NaN\n")
        original = paths[0].read_bytes()
        result = audit_derived_moments(*paths, self.header, {"N2O": -6.884325289636784})
        self.assertEqual(len(result["issues"]), 2)
        self.assertEqual(result["issues"][0]["column"], 28)
        self.assertEqual(paths[0].read_bytes(), original)

    def test_free_parameter_nan_rejected(self):
        self.row[16] = math.nan
        with self.assertRaisesRegex(ValueError, "free-parameter"):
            audit_derived_moments(*self.write_fixture(), self.header, {"N2O": -6.88})

    def test_nonfinite_evidence_rejected(self):
        self.row[60] = math.inf
        with self.assertRaisesRegex(ValueError, "primary summary"):
            audit_derived_moments(*self.write_fixture(), self.header, {"N2O": -6.88})

    def test_fixed_prior_departure_rejected(self):
        check_coordinates([-6.88], ["log_N2O"], {"log_N2O": [-6.88, -6.88]})
        with self.assertRaisesRegex(ValueError, "outside frozen prior"):
            check_coordinates([-6.87], ["log_N2O"], {"log_N2O": [-6.88, -6.88]})

    def test_calibration_controls_and_unfavourable_na(self):
        check_calibration()
        self.assertEqual(calibrated_sigma(0), (None, None))
        self.assertEqual(calibrated_sigma(-1), (None, None))

    def salvedad_fixture(self):
        audit = {
            "product_sha256": {"original": "frozen"},
            "derived_moment_audit": {"issues": [{
                "parameter": "log_N2O", "quantity": "derived_standard_deviation", "token": "NaN",
            }]},
            "fixed_log10_vmr": {"N2O": -6.88},
            "fixed_coordinate_spreads": {"N2O": {
                "minimum": -6.88, "maximum": -6.88, "centered_second_moment_about_reference": 0,
            }},
        }
        previous = {"primary_products_and_evidence_pass": True,
                    "run_audits": {"run": copy.deepcopy(audit)}}
        return audit, previous

    def test_salvedad_accepts_only_reviewed_zero_spread(self):
        audit, previous = self.salvedad_fixture()
        validate_fixed_moment_salvedad({"run": audit}, previous)

    def test_salvedad_rejects_changed_original(self):
        audit, previous = self.salvedad_fixture()
        audit["product_sha256"]["original"] = "changed"
        with self.assertRaisesRegex(ValueError, "hashes changed"):
            validate_fixed_moment_salvedad({"run": audit}, previous)

    def test_salvedad_rejects_nonzero_fixed_spread(self):
        audit, previous = self.salvedad_fixture()
        audit["fixed_coordinate_spreads"]["N2O"]["maximum"] = -6.87
        with self.assertRaisesRegex(ValueError, "nonzero spread"):
            validate_fixed_moment_salvedad({"run": audit}, previous)

    def test_salvedad_rejects_unreviewed_issue(self):
        audit, previous = self.salvedad_fixture()
        audit["derived_moment_audit"]["issues"][0]["quantity"] = "evidence"
        with self.assertRaisesRegex(ValueError, "issues changed"):
            validate_fixed_moment_salvedad({"run": audit}, previous)


if __name__ == "__main__":
    unittest.main()
