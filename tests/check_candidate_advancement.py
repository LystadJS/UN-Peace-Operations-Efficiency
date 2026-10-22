#!/usr/bin/env python3
"""Synthetic corruption controls for evidence gates and savings classifications."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import validate_candidate_advancement as v

D = v.read(v.DICTIONARY)
PATH = ["SCREENING_CANDIDATE", "VALIDATION_READY", "OPERATIONALLY_VALIDATED",
        "FINANCIALLY_VALIDATED", "IMPLEMENTATION_READY", "REALIZATION_IN_PROGRESS", "REALIZED"]


def fixture(states=PATH):
    events = []
    for i, state in enumerate(states):
        checks = D["states"][state]["requires"]
        events.append({"state": state, "recorded_at": f"2026-10-22T12:{i:02d}:00Z",
                       "evidence_cutoff": "2026-10-21", "actor": "SYNTHETIC_REVIEWER",
                       "rationale": "Synthetic test only", "checks": dict.fromkeys(checks, True),
                       "evidence_receipts": {c: ["SYNTHETIC_RECEIPT:" + c] for c in checks},
                       "validator_version": "1.0"})
    return {"schema_version": 1, "candidates": [{"candidate_id": "SYNTHETIC_001", "version": "1",
            "current_state": states[-1], "claim_class": "NO_FINANCIAL_CLAIM", "savings_amount": None,
            "currency": None, "period": None, "history": events}]}


class AdvancementTests(unittest.TestCase):
    def reject(self, payload, previous=None):
        with self.assertRaises(ValueError):
            v.validate_records(payload, D, previous)

    def test_dictionary_and_complete_financial_path(self):
        p = fixture()
        p["candidates"][0].update(claim_class="REALIZED_SAVING", savings_amount=50,
                                   currency="USD", period="2026 calendar year")
        self.assertEqual(v.validate_records(p, D), 1)

    def test_capacity_path_can_bypass_financial_gate(self):
        p = fixture([s for s in PATH if s != "FINANCIALLY_VALIDATED"])
        p["candidates"][0]["claim_class"] = "CAPACITY_GAIN"
        self.assertEqual(v.validate_records(p, D), 1)

    def test_control_improvement_path_can_bypass_financial_gate(self):
        p = fixture([s for s in PATH if s != "FINANCIALLY_VALIDATED"])
        p["candidates"][0]["claim_class"] = "CONTROL_IMPROVEMENT"
        self.assertEqual(v.validate_records(p, D), 1)

    def test_savings_at_screening_rejected(self):
        p = fixture(["SCREENING_CANDIDATE"])
        p["candidates"][0].update(claim_class="CASHABLE_SAVING", savings_amount=50,
                                   currency="USD", period="2027")
        self.reject(p)

    def test_unknown_dictionary_state_rejected(self):
        bad = copy.deepcopy(D)
        bad["states"]["UNKNOWN"] = bad["states"].pop("REALIZED")
        with self.assertRaises(ValueError):
            v.validate_dictionary(bad)

    def test_malformed_dictionary_rejected(self):
        for bad in ([], None, {"schema_version": 1, "states": []}):
            with self.assertRaises(ValueError):
                v.validate_dictionary(bad)
        for value in ([], None):
            bad = copy.deepcopy(D)
            bad["states"]["REALIZED"] = value
            with self.assertRaises(ValueError):
                v.validate_dictionary(bad)

    def test_boolean_schema_version_rejected(self):
        bad = copy.deepcopy(D)
        bad["schema_version"] = True
        with self.assertRaises(ValueError):
            v.validate_dictionary(bad)
        bad = fixture()
        bad["schema_version"] = True
        self.reject(bad)

    def test_capacity_bypass_cannot_claim_savings(self):
        p = fixture([s for s in PATH if s != "FINANCIALLY_VALIDATED"])
        p["candidates"][0].update(claim_class="REALIZED_SAVING", savings_amount=50, currency="USD", period="2026")
        self.reject(p)

    def test_no_skipped_operational_gate(self):
        self.reject(fixture(["SCREENING_CANDIDATE", "VALIDATION_READY", "FINANCIALLY_VALIDATED"]))

    def test_missing_and_unknown_evidence_rejected(self):
        for value in (None, [], ["unknown"], ["pending"]):
            p = fixture()
            p["candidates"][0]["history"][0]["evidence_receipts"]["source_anchor"] = value
            self.reject(p)

    def test_boolean_check_cannot_be_string(self):
        p = fixture()
        p["candidates"][0]["history"][0]["checks"]["source_anchor"] = "true"
        self.reject(p)

    def test_unknown_and_null_state_or_claim(self):
        for field in ("current_state", "claim_class"):
            for value in (None, "unknown", []):
                p = fixture()
                p["candidates"][0][field] = value
                self.reject(p)

    def test_duplicate_candidate_version(self):
        p = fixture()
        p["candidates"].append(copy.deepcopy(p["candidates"][0]))
        self.reject(p)

    def test_terminal_state_cannot_reopen(self):
        self.reject(fixture(["SCREENING_CANDIDATE", "RETAIN_CURRENT_PROCESS", "VALIDATION_READY"]))

    def test_realization_needs_implementation(self):
        self.reject(fixture(PATH[:4] + ["REALIZED"]))

    def test_false_zero_and_nan_savings_rejected(self):
        for amount in (False, 0, float("nan"), float("inf"), "50", None):
            p = fixture()
            p["candidates"][0].update(claim_class="REALIZED_SAVING", savings_amount=amount,
                                       currency="USD", period="2026")
            self.reject(p)

    def test_savings_amount_cannot_hide_under_capacity_class(self):
        p = fixture()
        p["candidates"][0].update(claim_class="CAPACITY_GAIN", savings_amount=50)
        self.reject(p)

    def test_cashable_saving_before_realization_valid(self):
        p = fixture(PATH[:4])
        p["candidates"][0].update(claim_class="CASHABLE_SAVING", savings_amount=50,
                                   currency="USD", period="2027")
        self.assertEqual(v.validate_records(p, D), 1)

    def test_realized_label_before_realization_rejected(self):
        p = fixture(PATH[:4])
        p["candidates"][0].update(claim_class="REALIZED_SAVING", savings_amount=50,
                                   currency="USD", period="2027")
        self.reject(p)

    def test_history_must_match_current_state(self):
        p = fixture()
        p["candidates"][0]["current_state"] = "FINANCIALLY_VALIDATED"
        self.reject(p)

    def test_append_only_comparison(self):
        old = fixture(PATH[:2])
        new = fixture()
        self.assertEqual(v.validate_records(new, D, old), 1)
        new["candidates"][0]["history"][0]["rationale"] = "Rewritten historical rationale"
        self.reject(new, old)

    def test_prior_candidate_cannot_disappear(self):
        self.reject({"schema_version": 1, "candidates": []}, fixture())

    def test_cutoff_and_chronology(self):
        p = fixture()
        p["candidates"][0]["history"][0]["evidence_cutoff"] = "2027-01-01"
        self.reject(p)
        p = fixture()
        p["candidates"][0]["history"][1]["recorded_at"] = p["candidates"][0]["history"][0]["recorded_at"]
        self.reject(p)

    def test_retention_and_insufficient_evidence_are_valid_distinct_outcomes(self):
        for state in ("RETAIN_CURRENT_PROCESS", "CLOSED_INSUFFICIENT_EVIDENCE"):
            self.assertEqual(v.validate_records(fixture(["SCREENING_CANDIDATE", state]), D), 1)


if __name__ == "__main__":
    unittest.main()
