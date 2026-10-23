#!/usr/bin/env python3
"""Synthetic examples only; none asserts an actual new project designation."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import validate_repository_status as v

S = v.read(v.SCHEMA)


def facet(status):
    return {"status": status, "evidence_refs": ["SYNTHETIC_RECEIPT"], "rationale": "Synthetic test scope only"}


def record(rid="SYNTHETIC_V13"):
    return {"artifact_id": rid, "path": "data/census_v13/research_reference.json", "version": "13.0",
            "scope": "SYNTHETIC_FIXED_V8_V9", "role": "selected_reference", "as_of": "2026-10-22",
            "evidence_cutoff": "2026-10-15", "superseded_by": None, "currency": facet("CURRENT"),
            "research_adoption": facet("ADOPTED_FOR_RESEARCH"), "institutional_approval": facet("NOT_APPROVED"),
            "implementation": facet("NOT_IMPLEMENTED"), "live_use": facet("BLOCKED")}


def envelope(*rows):
    return {"schema_version": 1, "records": list(rows)}


class StatusTests(unittest.TestCase):
    def reject(self, data):
        with self.assertRaises(ValueError):
            v.validate(data, S)

    def test_research_current_can_be_blocked_without_institutional_approval(self):
        self.assertEqual(v.validate(envelope(record()), S), 1)

    def test_paused_watch_does_not_reactivate(self):
        row = record("SYNTHETIC_WATCH")
        row.update(scope="SYNTHETIC_COURSE_WATCH", role="watch_contract")
        row["live_use"] = facet("PAUSED")
        row["research_adoption"] = facet("NOT_APPLICABLE")
        self.assertEqual(v.validate(envelope(row), S), 1)

    def test_research_adoption_does_not_authorize_live_use(self):
        row = record()
        row["live_use"] = facet("AUTHORIZED")
        self.reject(envelope(row))

    def test_explicit_approval_and_live_evidence_can_authorize(self):
        row = record()
        row["live_use"] = facet("AUTHORIZED")
        row["institutional_approval"] = facet("APPROVED")
        self.assertEqual(v.validate(envelope(row), S), 1)

    def test_approval_does_not_require_completed_implementation(self):
        row = record()
        row["institutional_approval"] = facet("APPROVED")
        self.assertEqual(v.validate(envelope(row), S), 1)

    def test_current_is_scoped(self):
        a, b = record(), record("SYNTHETIC_OLD_RESULTS")
        b["role"] = "historical_first_pass_result"
        self.assertEqual(v.validate(envelope(a, b), S), 2)

    def test_conflicting_current_slot_rejected(self):
        self.reject(envelope(record(), record("SYNTHETIC_CONFLICT")))

    def test_duplicate_identity_rejected(self):
        self.reject(envelope(record(), record()))

    def test_missing_facet_rejected(self):
        row = record()
        del row["live_use"]
        self.reject(envelope(row))

    def test_unknown_status_and_candidate_maturity_conflation_rejected(self):
        for status in ("REALIZED", "SCREENING_CANDIDATE", None, []):
            row = record()
            row["currency"]["status"] = status
            self.reject(envelope(row))

    def test_missing_evidence_for_definitive_status_rejected(self):
        row = record()
        row["implementation"] = facet("IMPLEMENTED")
        row["implementation"]["evidence_refs"] = []
        self.reject(envelope(row))

    def test_unknown_is_explicit_not_negative_finding(self):
        row = record()
        row["implementation"] = facet("UNKNOWN")
        row["implementation"]["evidence_refs"] = []
        self.assertEqual(v.validate(envelope(row), S), 1)

    def test_rationale_required_even_when_unknown(self):
        row = record()
        row["implementation"] = facet("UNKNOWN")
        row["implementation"]["rationale"] = " "
        self.reject(envelope(row))

    def test_supersession_requires_registered_same_scope_replacement(self):
        old, new = record("SYNTHETIC_OLD"), record()
        old["currency"] = facet("SUPERSEDED")
        old["superseded_by"] = new["artifact_id"]
        self.assertEqual(v.validate(envelope(old, new), S), 2)
        new["scope"] = "UNRELATED_FINANCIAL_SCOPE"
        self.reject(envelope(old, new))

    def test_missing_replacement_rejected(self):
        old = record()
        old["currency"] = facet("SUPERSEDED")
        old["superseded_by"] = "MISSING"
        self.reject(envelope(old))

    def test_candidate_cannot_supersede(self):
        old, new = record("SYNTHETIC_OLD"), record()
        old["currency"] = facet("SUPERSEDED")
        old["superseded_by"] = new["artifact_id"]
        new["currency"] = facet("CANDIDATE")
        self.reject(envelope(old, new))

    def test_cycle_rejected(self):
        a, b = record("SYNTHETIC_A"), record("SYNTHETIC_B")
        for row, target in ((a,b),(b,a)):
            row["currency"] = facet("SUPERSEDED")
            row["superseded_by"] = target["artifact_id"]
        self.reject(envelope(a,b))

    def test_replacement_without_superseded_status_rejected(self):
        row = record()
        row["superseded_by"] = "SOME_OTHER_ARTIFACT"
        self.reject(envelope(row))

    def test_future_cutoff_and_bad_date_rejected(self):
        for value in ("2027-01-01", "bad", None):
            row = record()
            row["evidence_cutoff"] = value
            self.reject(envelope(row))

    def test_path_traversal_rejected(self):
        for value in ("/secure/x", "../x", "data/../../x", "data\\x"):
            row = record()
            row["path"] = value
            self.reject(envelope(row))

    def test_wrong_schema_type_and_unknown_fields_rejected(self):
        for value in (True, None, "1"):
            data = envelope(record())
            data["schema_version"] = value
            self.reject(data)
        row = record()
        row["approved_because_current"] = True
        self.reject(envelope(row))

    def test_duplicate_evidence_rejected(self):
        row = record()
        row["currency"]["evidence_refs"] *= 2
        self.reject(envelope(row))


if __name__ == "__main__":
    unittest.main()
