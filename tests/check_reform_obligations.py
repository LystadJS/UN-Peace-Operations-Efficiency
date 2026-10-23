#!/usr/bin/env python3
"""Synthetic declaration mutations; these are not institutional evidence."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("obligations", ROOT / "scripts/validate_reform_obligations.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture():
    return {"schema_version": 1, "obligations": [{
        "obligation_id": "SYNTHETIC-ONLY", "authority_class": "GA_ADOPTED",
        "issuing_organ": "GENERAL_ASSEMBLY", "document_symbol": "SYNTHETIC",
        "session": "80", "evidence_cutoff": "2026-10-23",
        "source": {"official_url": "https://example.invalid/text", "retrieved_at": "2026-10-23", "locator": "operative paragraph 1", "version": "synthetic", "review_scope": "single provision", "limitations": []},
        "adoption": {"status": "ADOPTED_VERIFIED", "date": "2026-01-01", "final_text_receipt": "synthetic-final", "adoption_record_receipt": "synthetic-adoption"},
        "provision": {"action": "Synthetic action", "addressee": "Synthetic role", "entities": [], "functions": [], "period": None, "deadline": "2026-06-30", "deadline_basis": "synthetic paragraph", "conditions": [], "effect": "REQUEST"},
        "competence": {"assessment": "Synthetic institutional request", "review_receipt": "synthetic-review", "mandate_financing_distinction": "No mandate amendment inferred"},
        "implementation": {"status": "EVIDENCE_MISSING", "evidence_receipts": [], "verified_components": [], "unverified_components": ["all"]},
        "compliance": {"status": "EVIDENCE_MISSING", "assessment_receipt": None, "coverage_receipt": None}
    }]}


class Checks(unittest.TestCase):
    def test_complete_declared_adoption(self):
        self.assertEqual(module.validate(fixture()), [])

    def reject(self, mutate):
        data = fixture()
        mutate(data["obligations"][0])
        self.assertTrue(module.validate(data))

    def test_symbol_does_not_prove_adoption(self):
        self.reject(lambda r: r["adoption"].update(status="UNRESOLVED"))

    def test_committee_not_plenary(self):
        self.reject(lambda r: r.update(issuing_organ="FIFTH_COMMITTEE"))

    def test_advice_cannot_adopt(self):
        self.reject(lambda r: r.update(authority_class="ACABQ_ADVICE"))

    def test_missing_final_text(self):
        self.reject(lambda r: r["adoption"].update(final_text_receipt=None))

    def test_missing_adoption_record(self):
        self.reject(lambda r: r["adoption"].update(adoption_record_receipt=None))

    def test_missing_competence(self):
        self.reject(lambda r: r["competence"].update(review_receipt=None))

    def test_implementation_not_from_adoption(self):
        self.reject(lambda r: r["implementation"].update(status="VERIFIED"))

    def test_full_implementation_requires_all_components(self):
        self.reject(lambda r: r["implementation"].update(status="VERIFIED", evidence_receipts=["synthetic-operational"], verified_components=["one"]))

    def test_missing_evidence_not_noncompliance(self):
        self.reject(lambda r: r["compliance"].update(status="NONCOMPLIANT_VERIFIED"))

    def test_noncompliance_not_before_due(self):
        def mutate(r):
            r["compliance"].update(status="NONCOMPLIANT_VERIFIED", assessment_receipt="synthetic-assess", coverage_receipt="synthetic-coverage")
            r["provision"]["deadline"] = "2027-01-01"
        self.reject(mutate)

    def test_unknown_authority_retains_unknown(self):
        data = fixture()
        r = data["obligations"][0]
        r.update(authority_class="AUTHORITY_UNRESOLVED", document_symbol=None, session=None)
        r["adoption"].update(status="UNRESOLVED", date=None, final_text_receipt=None, adoption_record_receipt=None)
        r["source"].update(official_url=None, retrieved_at=None, locator=None)
        r["competence"].update(assessment=None, review_receipt=None)
        r["provision"].update(action=None, addressee=None, deadline=None, deadline_basis=None, effect="UNRESOLVED")
        r["compliance"]["status"] = "AUTHORITY_UNRESOLVED"
        self.assertEqual(module.validate(data), [])

    def test_duplicate_ids(self):
        data = fixture()
        data["obligations"].append(copy.deepcopy(data["obligations"][0]))
        self.assertTrue(module.validate(data))

    def test_invalid_envelope(self):
        for data in (None, [], {}, {"schema_version": 1, "obligations": [None]}):
            self.assertTrue(module.validate(data))

    def test_future_adoption(self):
        self.reject(lambda r: r["adoption"].update(date="2027-01-01"))

    def test_future_retrieval(self):
        self.reject(lambda r: r["source"].update(retrieved_at="2027-01-01"))

    def test_blank_implementation_receipt(self):
        self.reject(lambda r: r["implementation"].update(status="PARTIALLY_VERIFIED", evidence_receipts=[None], verified_components=["one"]))


if __name__ == "__main__":
    unittest.main()
