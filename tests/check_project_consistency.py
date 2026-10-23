#!/usr/bin/env python3
"""Corrupt current claims, links and historical lineage in synthetic controls."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import validate_project_consistency as checks


def fixture():
    financial = {k: {'usd_millions': v} for k, v in {
        'spm_missions': '419.4119', 'rsce_spm_share': '3.2591', 'spm_total_including_rsce': '422.6710',
        'six_mission_maintenance': '4028.1880', 'eleven_entity_maintenance': '4625.9401'}.items()}
    financial['advisory_coverage'] = {'reviewed': 27, 'unreconciled': 9, 'population': 36}
    pointer = {'reference_version': '13.0', 'live_use_gates': {'SP08P1': 'BLOCKED_FOR_LIVE_USE', 'SP09P1': 'BLOCKED_FOR_LIVE_USE'}}
    status = {'research': {'reference_version': '13.0', 'historical_supported': 59, 'historical_amendment_holds': 2,
                          'fixed_obligations': 61, 'adopted_amendments': 2, 'current_holds_for_adopted_amendments': 0,
                          'fresh_full_corpus_score': 'not_run'},
              'operational_constraints': {'live_gates': copy.deepcopy(pointer['live_use_gates']), 'course_watch': 'PAUSED',
                                          'cash_savings': 'not_estimated', 'staff_time_saved': 'not_estimated'}, 'finance': financial}
    return status, pointer


class ConsistencyTests(unittest.TestCase):
    def test_consistent_claims_pass(self):
        checks.check_status(*fixture())

    def test_stale_research_reference_fails(self):
        status, pointer = fixture()
        status['research']['reference_version'] = '11.0'
        with self.assertRaises(ValueError): checks.check_status(status, pointer)

    def test_historical_holds_cannot_be_rewritten(self):
        status, pointer = fixture()
        status['research']['historical_amendment_holds'] = 0
        with self.assertRaises(ValueError): checks.check_status(status, pointer)

    def test_current_amendments_cannot_stay_on_hold(self):
        status, pointer = fixture()
        status['research']['current_holds_for_adopted_amendments'] = 2
        with self.assertRaises(ValueError): checks.check_status(status, pointer)

    def test_unapproved_live_use_fails(self):
        status, pointer = fixture()
        status['operational_constraints']['live_gates']['SP08P1'] = 'ACTIVE'
        with self.assertRaises(ValueError): checks.check_status(status, pointer)

    def test_paused_watch_cannot_be_active(self):
        status, pointer = fixture()
        status['operational_constraints']['course_watch'] = 'ACTIVE'
        with self.assertRaises(ValueError): checks.check_status(status, pointer)

    def test_unknown_savings_cannot_be_zero(self):
        status, pointer = fixture()
        status['operational_constraints']['cash_savings'] = 0
        with self.assertRaises(ValueError): checks.check_status(status, pointer)

    def test_spm_perimeter_mixing_fails(self):
        status, pointer = fixture()
        status['finance']['spm_total_including_rsce']['usd_millions'] = '419.4119'
        with self.assertRaises(ValueError): checks.check_status(status, pointer)

    def test_broken_current_link_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root/'README.md').write_text('[Current](missing.md)')
            with self.assertRaises(ValueError): checks.check_local_links(root, ['README.md'])

    def test_unmarked_historical_record_fails(self):
        manifest = {'artifacts': [{'path': 'historical.json', 'scope': 'old release',
                                  'designation_basis': 'preserved first pass'}],
                    'generated_artifacts': [], 'current_roles': {}}
        with self.assertRaises(ValueError): checks.check_manifest_labels(manifest)

    def test_current_role_cannot_point_to_historical_record(self):
        manifest = {'artifacts': [{'path': 'old.json', 'currency': 'HISTORICAL',
                                  'scope': 'old release', 'designation_basis': 'preserved'}],
                    'generated_artifacts': [], 'current_roles': {'research': {'path': 'old.json'}}}
        with self.assertRaises(ValueError): checks.check_manifest_labels(manifest)

    def test_stale_canonical_current_link_fails(self):
        manifest = {'artifacts': [], 'generated_artifacts': [],
                    'current_roles': {'research': {'path': 'missing.json'}}}
        with self.assertRaises(ValueError): checks.check_manifest_labels(manifest)

    def test_dangling_lineage_fails(self):
        import csv
        import hashlib
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root/'metadata').mkdir()
            (root/'input.txt').write_text('SYNTHETIC input')
            with (root/'metadata/lineage_nodes.csv').open('w', newline='') as handle:
                writer = csv.DictWriter(handle, fieldnames=['node_id', 'path', 'sha256'])
                writer.writeheader()
                writer.writerow({'node_id': 'input.txt', 'path': 'input.txt',
                                 'sha256': hashlib.sha256((root/'input.txt').read_bytes()).hexdigest()})
            with (root/'metadata/lineage_edges.csv').open('w', newline='') as handle:
                writer = csv.DictWriter(handle, fieldnames=['edge_id', 'source', 'target', 'evidence_file'])
                writer.writeheader()
                writer.writerow({'edge_id': 'SYNTHETIC_1', 'source': 'input.txt', 'target': 'missing.txt', 'evidence_file': 'input.txt'})
            with self.assertRaises(ValueError): checks.check_lineage(root)


if __name__ == '__main__':
    unittest.main()
