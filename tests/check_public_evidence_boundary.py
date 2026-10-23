#!/usr/bin/env python3
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("boundary", ROOT / "scripts/validate_public_evidence_boundary.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PublicEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.value = json.loads((ROOT / "data/evidence_requests/E01_rsce.json").read_text())

    def test_all_request_contracts(self):
        for request_id, filename in module.REQUESTS.items():
            value = json.loads((ROOT / "data/evidence_requests" / filename).read_text())
            self.assertEqual(module.validate_contract(value, request_id), [])

    def test_actual_records_cannot_be_embedded(self):
        self.value["tables"][0]["records"] = [{"amount":100}]
        self.assertTrue(module.validate_contract(self.value,"E01"))

    def test_approval_and_period_cannot_be_invented(self):
        self.value["request_status"] = "SENT"
        self.value["period_parameters"]["baseline_start"] = "2026-01-01"
        self.assertGreaterEqual(len(module.validate_contract(self.value,"E01")), 2)

    def test_field_examples_are_not_public(self):
        self.value["tables"][0]["fields"][0]["values"] = ["person-token"]
        self.assertTrue(module.validate_contract(self.value,"E01"))

    def test_unnecessary_identifying_fields_rejected(self):
        self.value["tables"][0]["fields"][0]["name"] = "diagnosis"
        self.assertTrue(module.validate_contract(self.value,"E01"))

    def test_known_restricted_paths(self):
        bad = ["data/restricted/example.csv", "private/mapping.json", "output/internal/export.json", "assets/a.restricted.csv", "data/a.umojaxlsx"]
        self.assertEqual(module.forbidden_paths(bad), sorted(bad))
        self.assertEqual(module.forbidden_paths(["docs/secure_evidence_intake.md", "data/evidence_requests/E01_rsce.json"]), [])

    def test_duplicate_keys_or_fields_fail(self):
        self.value["tables"][0]["fields"].append(copy.deepcopy(self.value["tables"][0]["fields"][0]))
        self.assertTrue(module.validate_contract(self.value,"E01"))


if __name__ == "__main__":
    unittest.main()
