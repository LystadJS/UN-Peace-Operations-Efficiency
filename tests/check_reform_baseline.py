#!/usr/bin/env python3
"""Mutation checks for authority and implementation separation."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("baseline", ROOT / "scripts/validate_reform_baseline.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Checks(unittest.TestCase):
    def test_empty_actions_not_zero_obligations(self):
        row = {"schema_version": 1, "obligations": []}
        self.assertTrue(module.validate_register("unga81_actions.json", row))
        row["zero_count_meaning"] = "No extracted action; not zero applicable obligations"
        self.assertEqual(module.validate_register("unga81_actions.json", row), [])

    def test_index_not_operative_authority(self):
        row = {"instruments": [{"authority_classification": "GA_ADOPTED", "operative_text_status": "NOT_RETRIEVED"}]}
        self.assertTrue(module.validate_register("unga81_instruments.json", row))

    def test_acabq_cannot_adopt(self):
        self.assertTrue(module.validate_register("acabq_recommendations.json", {"recommendations": [{"authority_classification": "GA_ADOPTED"}]}))

    def test_advisory_adjustment_not_savings(self):
        self.assertTrue(module.validate_register("acabq_recommendations.json", {"recommendations": [{"authority_classification": "ACABQ_ADVICE", "financial_effect": {"amount": "100"}}]}))

    def test_proposal_not_implementation(self):
        row = {"source_treatment": "SG_PROPOSAL", "implementation": {"status": "VERIFIED"}}
        self.assertTrue(module.validate_register("sg_proposals.json", {"records": [row]}))

    def test_proposal_not_adoption(self):
        row = {"source_treatment": "SG_PROPOSAL", "ga_adoption": {"status": "ADOPTED_VERIFIED"}}
        self.assertTrue(module.validate_register("sg_proposals.json", {"records": [row]}))

    def test_synthetic_amount_not_financial_validation(self):
        row = {"source_treatment": "SG_PROPOSAL", "realized_benefit": {"amount": 100}}
        self.assertTrue(module.validate_register("sg_proposals.json", {"records": [row]}))

    def test_arrangement_not_verified(self):
        row = {"institutional_implementation_status": "VERIFIED", "supplemental_evidence_refs": []}
        self.assertTrue(module.validate_register("un80_arrangement_reconciliation.json", {"records": [row]}))

    def test_invalid_envelope(self):
        self.assertTrue(module.validate_register("unga81_actions.json", None))


if __name__ == "__main__":
    unittest.main()
