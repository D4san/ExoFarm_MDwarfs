"""Non-executing contract tests for the authorized 1000h comparison."""

import json
import unittest
from unittest.mock import patch

import run_proxima_a0_a3_1000h as campaign


class CampaignContract(unittest.TestCase):
    def test_duplicate_guard_without_launching_processes(self):
        with patch.object(campaign.sys, "platform", "linux"), \
                patch.object(campaign.Path, "exists", return_value=True), \
                patch.object(campaign.subprocess, "Popen") as process:
            with self.assertRaisesRegex(RuntimeError, "duplicate refused"):
                campaign.launch()
            process.assert_not_called()

    def test_exact_three_variants_same_dataset_native_grid(self):
        self.assertEqual(list(campaign.VARIANTS), ["N2O", "NH3", "joint"])
        for variant in campaign.VARIANTS:
            args = [str(x) for x in campaign.arguments(variant)]
            self.assertEqual(args[args.index("-n") + 1], "3")
            self.assertEqual(args[args.index("--hours") + 1], "1000")
            self.assertEqual(args[args.index("--wl-min") + 1], "3.0")
            self.assertEqual(args[args.index("--wl-max") + 1], "20.0")
            self.assertEqual(args[args.index("--dataset-file") + 1],
                             str(campaign.full.DATASET.relative_to(campaign.ROOT)))
            self.assertNotIn("--resume", args)

    def test_fixed_contract_and_reject_changed_noise(self):
        full = json.loads((campaign.full.CAMPAIGN / "resolved_configuration.json").read_text())
        fixed = json.loads(json.dumps(full))
        fixed["effective_free_dimension"] = 13
        value = -6.884325289636784
        fixed["prior_ranges"]["log_N2O"] = [value, value]
        case = {"run_id": "test", "fixed_species": ["N2O"],
                "fixed_log10_vmr": {"N2O": value}, "effective_free_dimension": 13,
                "dataset_sha256": full["dataset_sha256"]}
        campaign.verify_matched_configuration(full, fixed, case)
        fixed["dataset_sha256"] = "different"
        with self.assertRaises(ValueError):
            campaign.verify_matched_configuration(full, fixed, case)

    def test_global_cpu_budget_and_unrelated_job_rejected(self):
        line = "10 /env/bin/mpiexec -n 6 run_life_retrieval.py " + str(campaign.full.SCRATCH / "run")
        with patch.object(campaign.subprocess, "check_output", return_value=line), \
                patch.object(campaign.os, "sched_getaffinity", return_value=set(range(16)), create=True), \
                patch.object(campaign.Path, "read_text", return_value="MemAvailable: 20000000 kB"):
            self.assertEqual(campaign.check_host()["rank_total"], 6)
        with patch.object(campaign.subprocess, "check_output", return_value=line + " unrelated"):
            # Unexpected ranks are refused even if their total fits the CPU count.
            with patch.object(campaign.subprocess, "check_output", return_value=line.replace("-n 6", "-n 7")):
                with self.assertRaises(RuntimeError):
                    campaign.check_host()


if __name__ == "__main__":
    unittest.main()
