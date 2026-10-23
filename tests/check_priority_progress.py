#!/usr/bin/env python3
"""Contradiction and preservation tests for the scoped priority update."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import build_priority_progress as p

class Checks(unittest.TestCase):
    def fixture(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);root=Path(tmp.name)
        for name in p.INPUTS+[f'data/cases/{case}.json' for case in p.LEGACY_HASHES]:
            dest=root/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p.ROOT/name,dest)
        for name in p.INPUTS:
            for path, _ in p.explicit_bindings(json.loads((p.ROOT/name).read_text())):
                dest=root/path;dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(p.ROOT/path,dest)
        return root
    def reject(self,path,change):
        root=self.fixture();dest=root/path;value=json.loads(dest.read_text());change(value);dest.write_text(json.dumps(value))
        with self.assertRaises(ValueError):p.build(root)
    def test_actual_counts_are_not_operational_progress(self):
        d=p.build();self.assertEqual(d['actual_operational_audits_completed'],0)
        self.assertEqual(d['benefits'],'NOT_ESTIMATED');self.assertFalse(d['institutional_implementation_authorized'])
        self.assertEqual(d['selected_semantic_datasets'],11);self.assertEqual(d['selected_lineage_expressions'],6)
    def test_original_parent_cannot_be_silently_rewritten(self):
        self.reject('data/cases/C02.json',lambda d:d.update(candidate_state='VALIDATION_READY'))
    def test_unreviewed_source_change_blocks_output(self):
        self.reject('data/priority_cases/C02_public_evidence.json',lambda d:d.update(review_cutoff='2026-10-24'))
    def test_false_dispatch_blocks_output(self):
        self.reject('data/pilots/request_status.json',lambda d:d['counts'].update(requests_sent=1))
    def test_false_operational_completion_blocks_output(self):
        self.reject('data/adjudications/execution_gates.json',lambda d:d.update(actual_operational_audits_completed=1))
    def test_unknown_benefit_cannot_be_zero(self):
        self.reject('data/portfolio/verified_benefit_ledger.json',lambda d:d['reconciliation'].update(headline_realized_savings_usd='0'))
    def test_child_cannot_skip_operational_and_financial_gates(self):
        self.reject('data/priority_cases/research_candidates.json',lambda d:d['candidates'][0].update(current_state='FINANCIALLY_VALIDATED'))
    def test_initial_research_event_is_append_only(self):
        self.reject('data/priority_cases/research_candidates.json',lambda d:d['candidates'][0]['history'][0].update(rationale='REWRITTEN'))
    def test_stale_child_scope_review_blocks_output(self):
        self.reject('data/priority_cases/C02_UF01_readiness_review.json',lambda d:d.update(scope_sha256='0'*64))
    def test_research_state_requires_review_agreement(self):
        self.reject('data/priority_cases/C02_UF01_readiness_review.json',lambda d:d.update(recommended_state='REALIZED'))
    def test_dispatch_detail_cannot_hide_behind_zero_total(self):
        self.reject('data/pilots/request_status.json',lambda d:d['requests'][0].update(dispatch_status='SENT'))
    def test_owner_detail_cannot_hide_behind_zero_total(self):
        self.reject('data/pilots/request_status.json',lambda d:d['requests'][0].update(accepted_owner='Confirmed owner'))
    def test_case_track_cannot_hide_approved_collection(self):
        self.reject('data/pilots/request_status.json',lambda d:d['case_tracks'][0].update(approved_collection=True))
    def test_execution_detail_cannot_hide_behind_zero_total(self):
        self.reject('data/adjudications/execution_gates.json',lambda d:d['records'][0].update(substantive_audit_completed=True))
    def test_execution_detail_cannot_hide_financial_finding(self):
        self.reject('data/adjudications/execution_gates.json',lambda d:d['records'][0].update(financial_finding='Claim'))
    def test_nested_overlay_binding_must_match_source(self):
        self.reject('data/priority_cases/entity_authority_crosswalk.json',lambda d:d['entities'][0]['source_packet'].update(sha256='0'*64))
    def test_base_request_contract_binding_must_match(self):
        self.reject('data/priority_cases/C02_request_addendum.json',lambda d:d.update(extends_contract_sha256='0'*64))
    def test_readiness_requires_summary_and_individual_pass(self):
        self.reject('data/priority_cases/C02_UF01_readiness_review.json',lambda d:d.update(all_seven_required_checks_pass=False))
        self.reject('data/priority_cases/C02_UF01_readiness_review.json',lambda d:d['checks']['bounded_intervention'].update(status='FAIL'))
    def test_readiness_requires_exact_check_names(self):
        self.reject('data/priority_cases/C02_UF01_readiness_review.json',lambda d:d['checks'].update(extra_check={'status':'PASS'}))
    def test_outputs_are_current(self):
        for name,body in p.outputs().items():self.assertEqual((p.ROOT/name).read_text(),body,name)

if __name__=='__main__':unittest.main()
