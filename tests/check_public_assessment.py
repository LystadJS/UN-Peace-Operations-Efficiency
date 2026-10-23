#!/usr/bin/env python3
"""Mutation checks for the public-assessment/operational boundary."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build_public_assessment as p


class Checks(unittest.TestCase):
    def fixture(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        paths = {p.PREFIX + 'scope.json', 'data/portfolio/verified_benefit_ledger.json',
                 'data/adjudications/execution_gates.json'}
        for case in p.CASES:
            paths.update({p.PREFIX + case + '.json', f'data/cases/{case}.json'})
            case_data = json.loads((p.ROOT / (p.PREFIX + case + '.json')).read_text())
            paths.update(r['path'] for q in case_data['questions'] for r in q['evidence'])
            paths.update(r['source_path'] for r in case_data['financial_observations'])
        for name in paths:
            dest = root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p.ROOT / name, dest)
        return root

    def change(self, root, path, fn):
        target = root / path
        value = json.loads(target.read_text())
        fn(value)
        target.write_text(json.dumps(value))

    def reject(self, path, fn, reason):
        root = self.fixture()
        self.change(root, path, fn)
        with self.assertRaisesRegex(ValueError, reason):
            p.build(root)

    def review(self, root):
        names = [p.PREFIX + 'scope.json'] + [p.PREFIX + c + '.json' for c in p.CASES]
        value = {'schema_version': 1, 'reviewer_agent': 'priority_access',
                 'review_type': 'AGENT_REVIEW_NOT_INSTITUTIONAL',
                 'reviewed_sources': {n: p.sha(root / n) for n in names}, 'status': 'PASS',
                 'checks': [{'id': f'PA{i:02}', 'status': 'PASS',
                             'rationale': 'Synthetic review for software test only.'} for i in range(1, 10)],
                 'limitations': ['Synthetic test; not a substantive evidence review.']}
        (root / (p.PREFIX + 'peer_review.json')).write_text(json.dumps(value))

    def test_absent_review_never_implies_completion(self):
        value = p.build(self.fixture())
        self.assertFalse(value['public_assessment_complete'])
        self.assertEqual(value['peer_review_status'], 'NOT_OBTAINED')
        self.assertIsNone(value['monetary_headline'])
        self.assertIsNone(value['recognized_benefit'])
        self.assertEqual(value['operational_validations_completed'], 0)
        self.assertEqual(sum(value['disposition_counts'].values()), value['public_question_count'])

    def test_hash_bound_rubric_acceptance_is_separate_from_operations(self):
        root = self.fixture()
        self.review(root)
        value = p.build(root)
        self.assertTrue(value['public_assessment_complete'])
        self.assertEqual(value['public_assessment_status'], 'COMPLETE_WITH_LIMITATIONS')
        self.assertEqual(value['operational_validations_completed'], 0)
        self.assertEqual(p.outputs(root), p.outputs(root))

    def test_false_recognized_benefit_rejected(self):
        self.reject(p.PREFIX + 'C02.json', lambda d: d.update(recognized_benefit=394000), 'recognized benefits')

    def test_stale_evidence_rejected(self):
        self.reject(p.PREFIX + 'C01.json', lambda d: d['questions'][0]['evidence'][0].update(sha256='0' * 64), 'Stale evidence')

    def test_case_omission_rejected(self):
        self.reject(p.PREFIX + 'scope.json', lambda d: d['priority_case_ids'].pop(), 'three-case scope')

    def test_f03_state_is_not_question_disposition(self):
        self.reject(p.PREFIX + 'C03.json', lambda d: d['questions'][0].update(disposition='FINANCIALLY_VALIDATED'), 'Wrong public disposition')

    def test_unclassified_money_rejected(self):
        self.reject(p.PREFIX + 'C02.json', lambda d: d['financial_observations'][0].update(classification='SAVINGS'), 'Unclassified money')

    def test_nonfinite_money_rejected(self):
        self.reject(p.PREFIX + 'C02.json', lambda d: d['financial_observations'][0].update(amount=float('nan')), 'Nonfinite')

    def test_reopening_trigger_required(self):
        self.reject(p.PREFIX + 'C03.json', lambda d: d['questions'][0].pop('reopen_trigger'), 'reopen_trigger')

    def test_duplicate_question_rejected(self):
        self.reject(p.PREFIX + 'C02.json', lambda d: d['questions'].append(d['questions'][0]), 'Duplicate')

    def test_review_cannot_bind_another_population(self):
        root = self.fixture()
        self.review(root)
        self.change(root, p.PREFIX + 'peer_review.json', lambda d: d['reviewed_sources'].update({p.PREFIX + 'C01.json': '0' * 64}))
        with self.assertRaisesRegex(ValueError, 'review source mismatch'):
            p.build(root)

    def test_failed_rubric_cannot_claim_pass(self):
        root = self.fixture()
        self.review(root)
        self.change(root, p.PREFIX + 'peer_review.json', lambda d: d['checks'][0].update(status='FAIL'))
        with self.assertRaisesRegex(ValueError, 'PASS contradicts'):
            p.build(root)

    def test_unknown_ledger_is_not_measured_zero(self):
        self.reject('data/portfolio/verified_benefit_ledger.json',
                    lambda d: d['reconciliation'].update(headline_realized_savings_usd=0), 'ledger')

    def test_operational_facts_cannot_be_silently_reset(self):
        self.reject('data/adjudications/execution_gates.json',
                    lambda d: d.update(actual_operational_audits_completed=1), 'Operational facts changed')

    def test_traversal_receipt_rejected(self):
        self.reject(p.PREFIX + 'C01.json', lambda d: d['questions'][0]['evidence'][0].update(path='../outside.json'), 'Unsafe')


if __name__ == '__main__':
    unittest.main()
