#!/usr/bin/env python3
"""Synthetic tests only; no legacy issue is migrated or closed."""
import copy
import csv
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import validate_master_issues as v


def fixture():
    original = {'issue_id': 'SYNTHETIC_SOURCE_1', 'severity': 'high', 'status': 'open', 'issue': 'Synthetic issue'}
    return {'schema_version': 1, 'issues': [{
        'issue_id': 'SYNTHETIC:1', 'aliases': ['SYNTHETIC_SOURCE_1'], 'parent_issue_id': None,
        'source_ref': {'path': 'synthetic.csv', 'sha256': 'a' * 64, 'format': 'csv', 'id_field': 'issue_id',
                       'selector': 'SYNTHETIC_SOURCE_1', 'legacy_id': 'SYNTHETIC_SOURCE_1', 'original_record': original},
        'issue_type': 'DATA_QUALITY', 'summary': 'SYNTHETIC test only', 'severity': 'HIGH',
        'severity_change_receipt': None, 'resolution_state': 'OPEN', 'evidence_state': 'NOT_TESTED',
        'request_state': 'NOT_REQUESTED', 'response_state': 'NOT_OBTAINED', 'gate_status': 'BLOCKED',
        'blocking_claims': ['SYNTHETIC savings claim'], 'minimum_evidence': 'SYNTHETIC source reconciliation',
        'closure_rule': 'SYNTHETIC comparison reviewed', 'proposed_owner_role': 'SYNTHETIC custodian',
        'accepted_owner_ref': None, 'normalization_receipt': 'SYNTHETIC:mapping', 'resolution_receipt': None,
        'source_evidence_refs': [], 'claim': {'classification': 'NO_MONETARY_CLAIM', 'amount': None,
                                          'candidate_state': None, 'financial_validation_ref': None}}]}


class IssueTests(unittest.TestCase):
    def reject(self, payload, previous=None):
        with self.assertRaises(ValueError):
            v.validate(payload, previous=previous)

    def test_model_and_open_synthetic_record(self):
        self.assertEqual(v.validate(fixture()), 1)

    def test_empty_model_is_not_migration(self):
        self.assertEqual(v.validate({'schema_version': 1, 'issues': []}), 0)

    def test_unknown_is_not_zero_or_none(self):
        p = fixture()
        p['issues'][0]['severity'] = 'UNKNOWN'
        p['issues'][0]['severity_change_receipt'] = 'SYNTHETIC:preserved-severity-conflict'
        p['issues'][0]['evidence_state'] = 'UNKNOWN'
        self.assertEqual(v.validate(p), 1)
        p['issues'][0]['evidence_state'] = None
        self.reject(p)

    def test_resolution_needs_receipt(self):
        p = fixture()
        p['issues'][0]['resolution_state'] = 'RESOLVED'
        self.reject(p)
        p['issues'][0]['resolution_receipt'] = 'SYNTHETIC:reviewed-resolution'
        self.assertEqual(v.validate(p), 1)

    def test_no_severity_silent_downgrade(self):
        p = fixture()
        p['issues'][0]['severity'] = 'LOW'
        self.reject(p)

    def test_missing_alias_rejected(self):
        p = fixture()
        p['issues'][0]['aliases'] = ['different']
        self.reject(p)

    def test_duplicate_issue_or_source_rejected(self):
        p = fixture()
        p['issues'].append(copy.deepcopy(p['issues'][0]))
        self.reject(p)
        p['issues'][1]['issue_id'] = 'SYNTHETIC:2'
        self.reject(p)

    def test_satisfied_gate_not_implied_by_mapping(self):
        p = fixture()
        p['issues'][0]['gate_status'] = 'SATISFIED'
        self.reject(p)
        p['issues'][0].update(evidence_state='VERIFIED', resolution_receipt='SYNTHETIC:substantive-review')
        self.assertEqual(v.validate(p), 1)

    def test_received_response_needs_reference(self):
        p = fixture()
        p['issues'][0]['response_state'] = 'OBTAINED'
        self.reject(p)

    def test_proposed_owner_is_not_accepted(self):
        p = fixture()
        p['issues'][0]['accepted_owner_ref'] = 'pending'
        self.reject(p)

    def test_savings_before_financial_gate_rejected(self):
        p = fixture()
        p['issues'][0]['claim'].update(classification='CASHABLE_SAVING', amount=10,
                                       candidate_state='SCREENING_CANDIDATE', financial_validation_ref='SYNTHETIC:receipt')
        self.reject(p)
        p['issues'][0]['claim']['candidate_state'] = 'FINANCIALLY_VALIDATED'
        self.assertEqual(v.validate(p), 1)
        p['issues'][0]['claim']['financial_validation_ref'] = None
        self.reject(p)

    def test_realized_claim_requires_realized_state(self):
        p = fixture()
        p['issues'][0]['claim'].update(classification='REALIZED_SAVING', amount=10,
                                       candidate_state='FINANCIALLY_VALIDATED', financial_validation_ref='SYNTHETIC:receipt')
        self.reject(p)

    def test_source_history_preserved(self):
        old = fixture()
        new = copy.deepcopy(old)
        new['issues'][0]['source_ref']['original_record']['status'] = 'resolved'
        self.reject(new, old)
        self.reject({'schema_version': 1, 'issues': []}, old)

    def test_parent_cycles_and_missing_parent_rejected(self):
        p = fixture()
        p['issues'][0]['parent_issue_id'] = 'missing'
        self.reject(p)
        p['issues'][0]['parent_issue_id'] = 'SYNTHETIC:1'
        self.reject(p)

    def test_source_row_identity_and_hash(self):
        p = fixture()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / 'synthetic.csv'
            with path.open('w', newline='') as h:
                writer = csv.DictWriter(h, fieldnames=list(p['issues'][0]['source_ref']['original_record']))
                writer.writeheader()
                writer.writerow(p['issues'][0]['source_ref']['original_record'])
            p['issues'][0]['source_ref']['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
            v.check_sources(p, root)
            p['issues'][0]['source_ref']['original_record']['severity'] = 'low'
            with self.assertRaises(ValueError):
                v.check_sources(p, root)

    def test_json_source_pointer(self):
        p = fixture()
        s = p['issues'][0]['source_ref']
        s.update(path='synthetic.json', format='json', id_field=None, selector='/issues/0')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'synthetic.json'
            path.write_text(json.dumps({'issues': [s['original_record']]}))
            s['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
            v.check_sources(p, Path(tmp))

    def test_root_json_pointer_and_empty_csv_rejection(self):
        p = fixture()
        s = p['issues'][0]['source_ref']
        s.update(path='synthetic.json', format='json', id_field=None, selector='')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'synthetic.json'
            path.write_text(json.dumps(s['original_record']))
            s['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(v.validate(p), 1)
            v.check_sources(p, Path(tmp))
        p = fixture()
        p['issues'][0]['source_ref']['selector'] = ''
        self.reject(p)

    def test_malformed_and_boolean_versions_fail(self):
        for payload in [None, [], {'schema_version': True, 'issues': []}]:
            self.reject(payload)

    def test_crosswalk_sources_still_frozen(self):
        fields, sources = v.validate_crosswalk()
        self.assertEqual(sources, 17)
        self.assertEqual(fields, 140)


if __name__ == '__main__':
    unittest.main()
