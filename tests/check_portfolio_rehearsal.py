#!/usr/bin/env python3
"""Check synthetic rehearsal integrity and blocked actual pilot/request states."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


rehearsal = module("portfolio_rehearsal", "scripts/rehearse_portfolio.py")
evaluation = module("portfolio_evaluation", "scripts/evaluate_intervention.py")


def read(path):
    return json.loads((ROOT / path).read_text())


class RehearsalTests(unittest.TestCase):
    def setUp(self):
        self.synthetic = read("data/pilots/synthetic_scenarios.json")
        self.charters = read("data/pilots/charters.json")
        self.thresholds = read("data/pilots/thresholds.json")
        self.requests = read("data/pilots/request_status.json")

    def test_actual_execution_reproduces_receipt(self):
        result = rehearsal.build(ROOT)
        self.assertEqual(result, read("data/pilots/rehearsal_receipt.json"))
        self.assertEqual(result["scenario_count"], 10)
        self.assertEqual(result["actual_operational_trials"], 0)
        self.assertIsNone(result["actual_savings_amount"])

    def test_adverse_null_transfer_and_guard_failure_remain_visible(self):
        rows = {row["scenario_id"]: row["observed"] for row in rehearsal.rehearse(self.synthetic, evaluation.evaluate)}
        self.assertEqual(rows["SYN-ADVERSE"]["net_cost_difference"], "-95")
        self.assertIsNone(rows["SYN-UNKNOWN"]["net_cost_difference"])
        self.assertEqual(rows["SYN-TRANSFER"]["net_cost_difference"], rows["SYN-POSITIVE"]["net_cost_difference"])
        self.assertEqual(rows["SYN-GUARD-FAIL"]["priority_status"], "BLOCKED")
        self.assertEqual(rows["SYN-GUARD-UNKNOWN"]["priority_status"], "UNSCORABLE")

    def test_actual_record_flag_cannot_be_rehearsed_as_synthetic(self):
        self.synthetic["actual_un_records"] = True
        with self.assertRaises(ValueError):
            rehearsal.rehearse(self.synthetic, evaluation.evaluate)

    def test_public_research_input_cannot_hide_inside_synthetic_envelope(self):
        self.synthetic["scenarios"][0]["input"]["evidence_mode"] = "PUBLIC_RESEARCH"
        with self.assertRaises(ValueError):
            rehearsal.rehearse(self.synthetic, evaluation.evaluate)

    def test_expected_behavior_corruption_fails(self):
        self.synthetic["scenarios"][0]["expected"]["net_cost_difference"] = "99999"
        with self.assertRaises(ValueError):
            rehearsal.rehearse(self.synthetic, evaluation.evaluate)

    def test_savings_or_candidate_promotion_is_rejected(self):
        def corrupted(source):
            result = evaluation.evaluate(source)
            result["savings_amount"] = "5"
            return result
        with self.assertRaises(ValueError):
            rehearsal.rehearse(self.synthetic, corrupted)

    def test_duplicate_scenario_cannot_inflate_pass_count(self):
        self.synthetic["scenarios"].append(copy.deepcopy(self.synthetic["scenarios"][0]))
        with self.assertRaises(ValueError):
            rehearsal.rehearse(self.synthetic, evaluation.evaluate)

    def test_three_charters_and_twentyfour_unknown_thresholds(self):
        result = rehearsal.validate_preparation(self.charters, self.thresholds)
        self.assertEqual(result["charters"], 3)
        self.assertEqual(result["threshold_dimensions"], 24)

    def test_rehearsal_does_not_open_actual_trial(self):
        self.charters["live_trial_started"] = True
        with self.assertRaises(ValueError):
            rehearsal.validate_preparation(self.charters, self.thresholds)

    def test_invented_owner_acceptance_fails(self):
        self.charters["charters"][0]["accepted_accountable_owner"] = "assumed-role"
        with self.assertRaises(ValueError):
            rehearsal.validate_preparation(self.charters, self.thresholds)

    def test_invented_numeric_threshold_fails(self):
        self.thresholds["thresholds"][0]["numeric_threshold"] = "0.05"
        with self.assertRaises(ValueError):
            rehearsal.validate_preparation(self.charters, self.thresholds)

    def test_missing_threshold_dimension_fails(self):
        self.thresholds["thresholds"].pop()
        with self.assertRaises(ValueError):
            rehearsal.validate_preparation(self.charters, self.thresholds)

    def test_unmeasured_benefit_is_not_zero(self):
        self.charters["charters"][0]["benefits"]["realized_saving"] = "0"
        with self.assertRaises(ValueError):
            rehearsal.validate_preparation(self.charters, self.thresholds)

    def test_six_contracts_ten_case_tracks_all_unsent(self):
        result = rehearsal.validate_requests(self.requests, ROOT)
        self.assertEqual(result, {"draft_contracts": 6, "case_tracks": 10, "requests_sent": 0, "responses_obtained": 0})

    def test_fabricated_dispatch_is_rejected(self):
        self.requests["requests"][0]["dispatch_status"] = "SENT"
        with self.assertRaises(ValueError):
            rehearsal.validate_requests(self.requests, ROOT)

    def test_prepared_package_counts_are_not_sent_request_counts(self):
        self.requests["counts"]["requests_sent"] = 6
        with self.assertRaises(ValueError):
            rehearsal.validate_requests(self.requests, ROOT)

    def test_four_ga_cases_cannot_be_collapsed(self):
        e04 = next(row for row in self.requests["requests"] if row["request_id"] == "E04")
        e04["case_ids"] = ["C04"]
        with self.assertRaises(ValueError):
            rehearsal.validate_requests(self.requests, ROOT)

    def test_two_reporting_owner_tracks_are_distinct(self):
        self.requests["case_tracks"] = [row for row in self.requests["case_tracks"] if row["track_id"] != "E06-C12"]
        with self.assertRaises(ValueError):
            rehearsal.validate_requests(self.requests, ROOT)


if __name__ == "__main__":
    unittest.main()
