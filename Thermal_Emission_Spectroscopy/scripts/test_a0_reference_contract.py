"""Lightweight controls for fixed priors and matched-model acceptance."""

import copy
import unittest

from fixed_abundance_reference import constrain_priors
from run_proxima_a0_reference_campaign import select_cases, verify_matched_configuration


class ReferenceContractTests(unittest.TestCase):
    def test_a3_100h_individual_and_joint_selects_exactly_three(self):
        cases = [dict(run_id=f"{s}_{h}_{v}", scenario=s, hours=h, variant=v)
                 for s in ("A1", "A3") for h in (1, 10, 100)
                 for v in ("N2O", "NH3", "joint")]
        selected = select_cases(cases, "both", ["A3"], [100])
        self.assertEqual({c["run_id"] for c in selected},
                         {"A3_100_N2O", "A3_100_NH3", "A3_100_joint"})
        with self.assertRaises(ValueError):
            select_cases(cases, "both", ["A3", "A3"], [100])
        with self.assertRaises(ValueError):
            select_cases(cases[:-1], "both", ["A3"], [100])

    def test_fixed_unit_cube_transform_and_retained_nuisance(self):
        types = {"a1": "uniform", "log_X": "uniform"}
        ranges = {"a1": [0.02, 2.0], "log_X": [-12, -1]}
        constrain_priors(types, ranges, {"N2O": -6.884325289636784})
        self.assertEqual(ranges["a1"], [0.02, 2.0])
        low, high = ranges["log_N2O"]
        for unit_cube in (0.0, 0.1, 0.5, 0.99, 1.0):
            self.assertEqual(low + unit_cube * (high - low), low)

    def test_matched_contract_rejects_dataset_or_other_prior_change(self):
        full = dict(parameters=["a1", "log_N2O"], declared_dimension=15,
                    effective_free_dimension=14, param_species=["N2O", "NH3"],
                    dataset_sha256="frozen", R=10000, wl_min=3.8, wl_max=19,
                    n_live=800, ev_tol=0.5, surface_pressure_mode="fixed-black",
                    error_inflation="none", x_profile="isochem", likelihood="diagonal",
                    prior_types={"a1": "uniform", "log_N2O": "uniform"},
                    prior_ranges={"a1": [0.02, 2.0], "log_N2O": [-12, -1]})
        case = dict(run_id="test", fixed_species=["N2O"],
                    fixed_log10_vmr={"N2O": -6.8}, effective_free_dimension=13,
                    dataset_sha256="frozen")
        fixed = copy.deepcopy(full)
        fixed["effective_free_dimension"] = 13
        fixed["prior_ranges"]["log_N2O"] = [-6.8, -6.8]
        verify_matched_configuration(full, fixed, case)
        invalid = copy.deepcopy(fixed)
        invalid["prior_ranges"]["a1"] = [0.02, 3.0]
        with self.assertRaises(ValueError):
            verify_matched_configuration(full, invalid, case)
        invalid = copy.deepcopy(fixed)
        invalid["dataset_sha256"] = "other_noise"
        with self.assertRaises(ValueError):
            verify_matched_configuration(full, invalid, case)


if __name__ == "__main__":
    unittest.main()
