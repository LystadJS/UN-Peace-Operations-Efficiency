#!/usr/bin/env python3
"""A08 real-source reconciliation plus explicitly synthetic corruption tests."""
import copy
import csv
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import migrate_master_issues as m
import validate_master_issues as v


class MigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.envelope, cls.receipt = m.build()

    def test_source_identity_and_contract(self):
        self.assertEqual(v.validate(self.envelope), 117)
        v.check_sources(self.envelope)

    def test_deterministic_retained_outputs(self):
        self.assertEqual((m.ROOT / m.REGISTER).read_text(), m.encoded(self.envelope))
        self.assertEqual((m.ROOT / m.RECEIPT).read_text(), m.encoded(self.receipt))
        self.assertEqual(m.build(), (self.envelope, self.receipt))

    def test_all_seventeen_source_populations_reconcile(self):
        self.assertEqual(len(self.receipt['sources']), 17)
        for source in self.receipt['sources']:
            self.assertEqual(source['candidate_units'], source['imported_count'] + source['excluded_count'])
            selectors = [r['selector'] for r in source['imported'] + source['excluded']]
            self.assertEqual(len(selectors), len(set(selectors)))
            if source['path'].endswith('.csv'):
                with (m.ROOT / source['path']).open(newline='') as handle:
                    rows = list(csv.DictReader(handle))
                self.assertEqual(len(rows), source['candidate_units'])

    def test_core_source_counts_complete(self):
        counts = {s['path']: s['imported_count'] for s in self.receipt['sources']}
        self.assertEqual(counts['data/quality_issues.csv'], 22)
        self.assertEqual(counts['data/transaction_audit_issues.csv'], 7)
        self.assertEqual(counts['data/owner_review/evidence_gap_register.csv'], 16)
        self.assertEqual(counts['data/public_release_gates.csv'], 18)

    def test_no_money_or_owner_authority_created(self):
        for row in self.envelope['issues']:
            self.assertEqual(row['claim']['classification'], 'NO_MONETARY_CLAIM')
            self.assertIsNone(row['claim']['amount'])
            self.assertIsNone(row['accepted_owner_ref'])
            self.assertNotEqual(row['gate_status'], 'SATISFIED')

    def test_owner_questions_stay_open_and_unsent(self):
        rows = [r for r in self.envelope['issues'] if r['source_ref']['path'] == 'data/owner_review/evidence_gap_register.csv']
        self.assertEqual(len(rows), 16)
        for row in rows:
            self.assertEqual(row['resolution_state'], 'OPEN')
            self.assertEqual(row['request_state'], 'NOT_REQUESTED')
            self.assertEqual(row['response_state'], 'NOT_OBTAINED')

    def test_amendments_resolved_only_for_research(self):
        rows = [r for r in self.envelope['issues'] if r['issue_type'] == 'AMENDMENT']
        self.assertEqual(len(rows), 6)
        self.assertEqual({r['source_ref']['original_record'].get('amendment_id') for r in rows}, {'AM11-01', 'AM11-02'})
        for row in rows:
            self.assertEqual(row['resolution_state'], 'RESOLVED')
            self.assertIn('research', row['closure_rule'])
            self.assertIsNotNone(row['resolution_receipt'])
            if row['source_ref']['path'].endswith('amendment_requests.json'):
                self.assertEqual(row['source_ref']['original_record']['status'], 'proposed_source_checked_not_applied_to_frozen_reference')
                self.assertEqual(row['response_state'], 'NOT_OBTAINED')

    def test_supported_lineage_rows_not_new_issues(self):
        source = next(s for s in self.receipt['sources'] if s['path'].endswith('reference_lineage.csv'))
        self.assertEqual(source['excluded_count'], 59)
        self.assertEqual(source['imported_count'], 2)

    def test_nested_missing_fields_and_pause_retained(self):
        gates = [r for r in self.envelope['issues'] if r['source_ref']['format'] == 'json' and 'missing' in r['source_ref']['original_record']]
        self.assertEqual(len(gates), 8)
        for row in gates:
            self.assertEqual(len(row['source_ref']['original_record']['missing']), 19)
            self.assertEqual(row['gate_status'], 'BLOCKED')
        pause = next(r for r in self.envelope['issues'] if r['source_ref']['legacy_id'] == 'COURSE_WATCH_PAUSE')
        self.assertEqual(pause['source_ref']['selector'], '')
        self.assertEqual(pause['source_ref']['original_record']['course_watch'], 'paused')
        self.assertEqual(pause['gate_status'], 'BLOCKED')

    def test_every_json_leaf_has_a_disposition(self):
        for source in self.receipt['sources']:
            if source['path'].endswith('.json'):
                obj = json.loads((m.ROOT / source['path']).read_text())
                self.assertEqual({p for p, _ in m.leaves(obj)}, {r['pointer'] for r in source['json_leaf_coverage']})

    def test_synthetic_unknown_state_stays_unknown(self):
        row = m.issue_record('data/quality_issues.csv', 'a' * 64, 'csv', 'issue_id', 'SYNTHETIC',
                             'SYNTHETIC', {'issue_id': 'SYNTHETIC', 'status': 'unreviewed_new_state', 'issue': 'Synthetic'})
        self.assertEqual(row['resolution_state'], 'UNKNOWN')
        self.assertEqual(row['request_state'], 'UNKNOWN')
        self.assertIsNone(row['resolution_receipt'])

    def test_source_snapshot_corruption_rejected(self):
        altered = copy.deepcopy(self.envelope)
        altered['issues'][0]['source_ref']['original_record']['SYNTHETIC_TAMPER'] = True
        with self.assertRaises(ValueError):
            v.check_sources(altered)


if __name__ == '__main__':
    unittest.main()
