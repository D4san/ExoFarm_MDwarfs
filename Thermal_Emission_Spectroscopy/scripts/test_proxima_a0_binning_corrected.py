"""Contract checks for the three corrected A0 runs; never launch MPI."""

import copy
import json
import unittest
from unittest.mock import patch

import launch_proxima_a0_binning_corrected as campaign
import audit_life_operator_source_equivalence as source_audit


class CorrectedA0Contract(unittest.TestCase):
    def test_relaunch_can_use_isolated_campaign_and_scratch_roots(self):
        values = {
            "EXOFARM_A0_BINNING_CAMPAIGN": "/tmp/exofarm-a0-relaunch/campaign",
            "EXOFARM_A0_BINNING_SCRATCH": "/tmp/exofarm-a0-relaunch/scratch",
        }
        with patch.dict(campaign.os.environ, values):
            self.assertEqual(
                str(campaign.configured_path(
                    "EXOFARM_A0_BINNING_CAMPAIGN", campaign.CAMPAIGN)),
                values["EXOFARM_A0_BINNING_CAMPAIGN"],
            )
            self.assertEqual(
                str(campaign.configured_path(
                    "EXOFARM_A0_BINNING_SCRATCH", campaign.SCRATCH)),
                values["EXOFARM_A0_BINNING_SCRATCH"],
            )

    def test_only_three_fresh_MPI5_A3_1000h_models(self):
        self.assertEqual(list(campaign.VARIANTS), ["N2O", "NH3", "joint"])
        for variant in campaign.VARIANTS:
            args = [str(arg) for arg in campaign.arguments(variant)]
            self.assertEqual(args[args.index("-n") + 1], "5")
            self.assertEqual(args[args.index("--hours") + 1], "1000")
            self.assertEqual(args[args.index("--scenario") + 1], "A3")
            self.assertEqual(args[args.index("--wl-min") + 1], "3.0")
            self.assertEqual(args[args.index("--wl-max") + 1], "20.0")
            self.assertIn(str(campaign.RUNNER), args)
            self.assertNotIn("--resume", args)
            self.assertNotIn("--exclude-species", args)
            self.assertEqual(args[args.index("--dataset-file") + 1],
                             str(campaign.base.DATASET.relative_to(campaign.ROOT)))
            name = "proxima_A3_1000h" + args[args.index("--output-tag") + 1]
            root = "POSEIDON_output/proxima_b_earthlike/retrievals/MultiNest_raw/" + name + "-"
            self.assertLess(len(root), 100)

    def test_matched_priors_allow_only_the_selected_constraints(self):
        baseline = json.loads((campaign.BASELINE / "resolved_configuration.json").read_text())
        fixed = {"N2O": -6.884325289636784, "NH3": -9.950526295665036}
        for variant, species in campaign.VARIANTS.items():
            config = copy.deepcopy(baseline)
            case = {"run_id": variant, "fixed_species": species,
                    "fixed_log10_vmr": {name: fixed[name] for name in species},
                    "effective_free_dimension": 14 - len(species),
                    "dataset_sha256": campaign.EXPECTED_HASH}
            config["effective_free_dimension"] = case["effective_free_dimension"]
            for name in species:
                config["prior_ranges"]["log_" + name] = [fixed[name], fixed[name]]
            campaign.verify_matched_configuration(baseline, config, case)
            config["error_inflation"] = "Piette20"
            with self.assertRaises(ValueError):
                campaign.verify_matched_configuration(baseline, config, case)

    def test_process_budget_rejects_unrelated_MPI(self):
        cmd = (f"12 mpiexec {campaign.PREFIX}/bin/mpiexec -n 5 "
               f"{campaign.PREFIX}/bin/python {campaign.RUNNER} --run-dir "
               f"{campaign.SCRATCH}/runs/N2O")
        with patch.object(campaign.subprocess, "check_output", return_value=cmd):
            jobs = campaign.science_jobs()
            self.assertTrue(jobs[0]["allowed"])
        with patch.object(campaign.subprocess, "check_output", return_value=cmd.replace("-n 5", "-n 6")):
            self.assertFalse(campaign.science_jobs()[0]["allowed"])

    def test_duplicate_launch_never_starts_a_child(self):
        with patch.object(campaign.sys, "platform", "linux"), \
                patch.object(campaign.Path, "exists", return_value=True), \
                patch.object(campaign.subprocess, "Popen") as child:
            with self.assertRaisesRegex(RuntimeError, "duplicate refused"):
                campaign.launch()
            child.assert_not_called()

    def test_source_equivalence_recovers_the_exact_frozen_operator(self):
        record = campaign.audit_operator_source(write=False)
        self.assertEqual(record["full_run_source_sha256"], record["reconstructed_source_sha256"])
        self.assertFalse(record["scientific_operator_change"])
        self.assertTrue(record["executable_AST_equal_except_docstrings_and_two_error_messages"])

    def test_source_equivalence_rejects_a_changed_calculation(self):
        original = source_audit.SOURCE.read_bytes()
        altered = original.replace(b"native[selected] / centres[channel]",
                                   b"native[selected] ** 2 / centres[channel]")
        self.assertNotEqual(original, altered)
        with patch.object(source_audit.Path, "read_bytes", return_value=altered):
            with self.assertRaisesRegex(ValueError, "checksum"):
                source_audit.audit(write=False)


if __name__ == "__main__":
    unittest.main()
