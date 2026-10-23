#!/usr/bin/env python3
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("coverage_builder", ROOT / "scripts/build_portfolio_coverage.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CoverageTests(unittest.TestCase):
    def test_full_registry_and_semantic_boundary(self):
        result = module.build_contracts()
        self.assertEqual(result["counts"], {"datasets":324,"repository_semantics_reviewed":37,"profile_only_semantics_unreviewed":287})
        self.assertEqual(len({r["dataset_id"] for r in result["contracts"]}), 324)

    def test_profile_never_becomes_accepted_semantics(self):
        for contract in module.build_contracts()["contracts"]:
            if contract["semantic_review"] == "profile_only_semantics_unreviewed":
                self.assertEqual(contract["contract_status"], "PROVISIONAL_PROFILE_ONLY")
            self.assertEqual(contract["join_contract"]["status"], "NOT_CERTIFIED")
            self.assertEqual(contract["population_completeness"], "NOT_ESTABLISHED")

    def test_dimensions_do_not_imply_operational_verification(self):
        result = module.build_coverage()
        self.assertEqual(result["counts"]["eleven_entity_budget_register_records"], 11)
        self.assertEqual(result["counts"]["ga_maintenance_reconciliation_records"], 6)
        self.assertEqual(result["counts"]["continuing_spm_proposal_records"], 36)
        for row in result["entities"]:
            for dimension in result["dimensions"]:
                self.assertIn(dimension, row)
            self.assertIsNone(row["waste_assessed_fraction"])
            self.assertEqual(row["operational_evidence_coverage"], "NOT_ASSESSED_BY_THIS_MATRIX")

    def test_outputs_exact_and_deterministic(self):
        self.assertEqual(module.outputs(), module.outputs())
        for path, expected in module.outputs().items():
            self.assertEqual((ROOT/path).read_text(encoding="utf-8"), expected)


if __name__ == "__main__":
    unittest.main()
