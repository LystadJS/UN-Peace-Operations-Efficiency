#!/usr/bin/env python3
"""Evidence-boundary checks for generated reform views."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("views", ROOT / "scripts/build_reform_views.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.views = module.build(ROOT)

    def test_all_actions_preserved_once(self):
        import json
        expected = {r["obligation_id"] for session in (80, 81) for r in json.loads((ROOT / f"data/reforms/unga{session}_actions.json").read_text())["obligations"]}
        rows = self.views["data/reforms/obligation_crosswalk.json"]["records"]
        self.assertEqual(expected, {r["obligation_id"] for r in rows})
        self.assertEqual(len(expected), len(rows))

    def test_candidate_match_not_applicability(self):
        for row in self.views["data/reforms/obligation_crosswalk.json"]["records"]:
            self.assertEqual(row["candidate_applicability_status"], "NOT_ADJUDICATED")
            self.assertIsNone(row["budget_amount"])
            for match in row["candidate_links"]:
                self.assertGreaterEqual(len(match["matching_terms"]), 2)
                self.assertIsNone(match["applicability_review_receipt"])

    def test_generic_words_cannot_link_cases(self):
        self.assertEqual(module.tokens("United Nations peacekeeping support operations budget review"), set())

    def test_implementation_not_invented(self):
        view = self.views["data/reforms/implementation_evidence.json"]
        self.assertEqual(view["observed_verified_implementation_count"], 0)
        self.assertIn("not zero reforms", view["zero_count_meaning"])
        self.assertTrue(all(r["owner_approval"] == "NOT_ESTABLISHED" for r in view["records"]))

    def test_requests_are_drafts(self):
        view = self.views["data/reforms/evidence_requests.json"]
        self.assertEqual(view["requests_sent"], 0)
        for row in view["requests"]:
            self.assertEqual(row["status"], "DRAFT_NOT_SENT")
            self.assertIsNone(row["sent_at"])
            self.assertFalse(row["custodian_accepted"])

    def test_no_measured_metrics_or_invented_thresholds(self):
        for row in self.views["data/reforms/reform_metrics.json"]["metrics"]:
            self.assertIsNone(row["observed_value"])
            self.assertIsNone(row["target"])
            self.assertTrue(row["guardrail"])

    def test_release_partial_not_certified(self):
        release = self.views["data/reforms/baseline_release.json"]
        self.assertEqual(release["release_class"], "PARTIAL_PUBLIC_RESEARCH_BASELINE")
        self.assertEqual(release["completion_gate"], "NOT_A_COMPLETE_COMPLIANCE_OR_OPERATIONAL_ADJUDICATION")
        self.assertIsNone(release["verified_incremental_savings"])
        self.assertIn("does not certify", release["review_scope_rule"])

    def test_determinism(self):
        self.assertEqual(module.outputs(ROOT), module.outputs(ROOT))


if __name__ == "__main__":
    unittest.main()
