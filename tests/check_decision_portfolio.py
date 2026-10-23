#!/usr/bin/env python3
"""Independent contradiction tests for the public baseline, using disposable copies."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('decision_portfolio',ROOT/'scripts/build_decision_portfolio.py')
model=importlib.util.module_from_spec(spec); spec.loader.exec_module(model)

class DecisionPortfolioTests(unittest.TestCase):
    def test_actual_baseline_is_not_operational_completion(self):
        result=model.build(ROOT)
        self.assertEqual(result['release_class'],'PUBLIC_VALIDATION_BASELINE')
        self.assertEqual(result['decision_grade_portfolio'],'BLOCKED')
        self.assertEqual(result['substantive_operational_adjudications'],0)
        self.assertTrue(all(v is None for k,v in result['verified_benefits'].items() if k!='interpretation'))
        self.assertEqual(len(result['cases']),14)

    def corruption(self,path,mutate):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            baseline=model.build(ROOT)
            for source in baseline['source_sha256']:
                target=root/source; target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes((ROOT/source).read_bytes())
            value=json.loads((root/path).read_text()); mutate(value)
            (root/path).write_text(json.dumps(value))
            with self.assertRaises(ValueError,msg=path): model.build(root)

    def test_changed_case_state_requires_review(self):
        self.corruption('data/cases/C01.json',lambda d:d.update(candidate_state='FINANCIALLY_VALIDATED'))
    def test_changed_case_disposition_requires_review(self):
        self.corruption('data/cases/C01.json',lambda d:d.update(disposition='RETAIN_CURRENT_PROCESS'))
    def test_case_benefit_contradiction_requires_review(self):
        self.corruption('data/cases/C01.json',lambda d:d['benefits'].update(recovery='100'))
    def test_case_financial_validation_requires_review(self):
        self.corruption('data/cases/C01.json',lambda d:d.update(financial_validation='VERIFIED'))
    def test_case_dispatch_contradiction_requires_review(self):
        self.corruption('data/cases/C01.json',lambda d:d.update(evidence_request_sent=True))
    def test_execution_count_requires_review(self):
        self.corruption('data/adjudications/execution_gates.json',lambda d:d.update(actual_operational_audits_completed=1))
    def test_execution_row_requires_review(self):
        self.corruption('data/adjudications/execution_gates.json',lambda d:d['records'][0].update(substantive_audit_completed=True))
    def test_execution_missing_row_requires_review(self):
        self.corruption('data/adjudications/execution_gates.json',lambda d:d['records'].pop())
    def test_nonempty_ledger_requires_review(self):
        self.corruption('data/portfolio/verified_benefit_ledger.json',lambda d:d['entries'].append({'entry_id':'UNREVIEWED'}))
    def test_unbacked_total_requires_review(self):
        self.corruption('data/portfolio/verified_benefit_ledger.json',lambda d:d['reconciliation'].update(headline_realized_savings_usd='100'))
    def test_intervention_state_contradiction_requires_review(self):
        self.corruption('data/portfolio/interventions.json',lambda d:d['interventions'][0].update(candidate_state='REALIZED'))
    def test_intervention_benefit_contradiction_requires_review(self):
        self.corruption('data/portfolio/interventions.json',lambda d:d['interventions'][0].update(benefit_amount='100'))
    def test_reported_trial_contradiction_requires_review(self):
        self.corruption('data/pilots/rehearsal_receipt.json',lambda d:d.update(actual_operational_trials=1))
    def test_reported_approval_contradiction_requires_review(self):
        self.corruption('data/pilots/rehearsal_receipt.json',lambda d:d.update(actual_owner_approvals=1))
    def test_sent_request_count_contradiction_requires_review(self):
        self.corruption('data/pilots/request_status.json',lambda d:d['counts'].update(requests_sent=1))
    def test_sent_request_row_contradiction_requires_review(self):
        self.corruption('data/pilots/request_status.json',lambda d:d['requests'][0].update(dispatch_status='SENT'))
    def test_institutional_approval_contradiction_requires_review(self):
        self.corruption('data/realization/implementation_gates.json',lambda d:d.update(institutional_approval_obtained=True))
    def test_new_approved_intervention_requires_review(self):
        self.corruption('data/realization/implementation_gates.json',lambda d:d['approved_interventions'].append('C01'))
    def test_current_generated_outputs(self):
        for path,value in model.outputs(ROOT).items(): self.assertEqual((ROOT/path).read_text(),value,path)

if __name__=='__main__': unittest.main()
