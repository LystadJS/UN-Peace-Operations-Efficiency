#!/usr/bin/env python3
"""Corrupt small synthetic dossier fixtures to test source fidelity checks."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("case_dossiers", ROOT / "scripts/validate_case_dossiers.py")
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


class DossierTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "data/cases").mkdir(parents=True)
        source = self.root / "data/source.csv"
        source.write_text("id,value\nSYNTHETIC,unknown\n")
        self.dossier = {"case_id": "C01", "candidate_state": "SCREENING_CANDIDATE", "disposition": "BLOCKED_PENDING_EVIDENCE", "owner_confirmation_status": "NOT_OBTAINED", "evidence_request_sent": False, "financial_validation": "NOT_PERFORMED", "accountable_owner": None, "operational_baseline": None, "benefits": {**{key: None for key in model.BENEFITS}, "status": "NOT_ESTIMATED"}, "evidence": [{"path": "data/source.csv", "csv_line": 2, "sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "source_snapshot": {"id": "SYNTHETIC", "value": "unknown"}}]}

    def check(self):
        (self.root / "data/cases/C01.json").write_text(json.dumps(self.dossier))
        return model.validate(self.root, ("C01",), 1)

    def test_current_release_population_and_230_snapshots(self):
        actual = model.validate(ROOT)
        self.assertEqual(actual["errors"], [])
        self.assertEqual(actual["csv_snapshots"], 227)
        self.assertEqual(actual["selected_json_snapshots"], 3)

    def test_synthetic_csv_locator_reproduces(self):
        self.assertEqual(self.check()["status"], "PASS")

    def test_changed_source_bytes_fail(self):
        (self.root / "data/source.csv").write_text("id,value\nSYNTHETIC,changed\n")
        self.assertEqual(self.check()["status"], "FAIL")

    def test_snapshot_and_locator_corruption_fail(self):
        self.dossier["evidence"][0]["source_snapshot"]["value"] = "fabricated"
        self.assertEqual(self.check()["status"], "FAIL")
        self.dossier["evidence"][0]["csv_line"] = 3
        self.assertEqual(self.check()["status"], "FAIL")

    def test_unsafe_path_fails(self):
        self.dossier["evidence"][0]["path"] = "../outside.csv"
        self.assertEqual(self.check()["status"], "FAIL")

    def test_invented_financial_claim_fails(self):
        self.dossier["benefits"]["realized_saving"] = "5"
        self.assertEqual(self.check()["status"], "FAIL")

    def test_json_subset_requires_declared_scope_and_exact_fields(self):
        source = self.root / "data/source.json"
        source.write_text(json.dumps({"key": "SYNTHETIC", "other": "retained"}))
        self.dossier["evidence"] = [{"path": "data/source.json", "json_pointer": "", "sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "source_snapshot": {"key": "SYNTHETIC"}, "snapshot_scope": "selected top-level fields, not full document"}]
        self.assertEqual(self.check()["status"], "PASS")
        self.dossier["evidence"][0].pop("snapshot_scope")
        self.assertEqual(self.check()["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
