#!/usr/bin/env python3
"""Status-view regression checks use retained-source copies and synthetic controls."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import generate_current_status as g


class CurrentStatusTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        pointer = g.read_json(g.ROOT, 'data/current_research_reference.json')
        for name in g.BASE_INPUTS + [pointer['reference_path']]:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            source = g.ROOT / name
            if source.is_file():
                shutil.copyfile(source, target)
            else:
                synthetic = {'metadata/canonical_manifest.json': {'schema_version': 1, 'current_roles': {
                                role: {'path': path, 'scope': 'SYNTHETIC fixed research scope'}
                                for role, path in [('research_reference', pointer['reference_path']),
                                                   ('research_pointer', 'data/current_research_reference.json'),
                                                   ('issue_register', 'data/issues/current_issues.json'),
                                                   ('current_status', g.OUTPUT_MD)]}},
                             'data/issues/current_issues.json': {'schema_version': 1, 'issues': []},
                             'metadata/issue_migration_receipt.json': {'migration_id': 'SYNTHETIC_TEST_ONLY', 'issue_count': 0, 'state_totals': {}, 'sources': []}}
                target.write_text(json.dumps(synthetic[name]))

    def mutate_json(self, name, change):
        path = self.root / name
        value = json.loads(path.read_text())
        change(value)
        path.write_text(json.dumps(value))

    def reject(self):
        with self.assertRaises(ValueError):
            g.build(self.root)

    def test_retained_controls_and_decimal_totals(self):
        s = g.build(self.root)
        self.assertEqual(s['research']['reference_version'], '13.0')
        self.assertEqual((s['research']['historical_supported'], s['research']['historical_amendment_holds']), (59, 2))
        self.assertEqual(s['operational_constraints']['course_watch'], 'PAUSED')
        self.assertEqual(s['finance']['six_mission_maintenance']['usd_millions'], '4028.1880')
        self.assertEqual(s['finance']['eleven_entity_maintenance']['usd_millions'], '4625.9401')
        self.assertEqual(s['finance']['spm_missions']['usd_millions'], '419.4119')
        self.assertEqual(s['finance']['spm_total_including_rsce']['usd_millions'], '422.6710')
        self.assertEqual(s['finance']['embedded_efficiencies']['usd_millions'], '14.6925')

    def test_output_is_deterministic_and_inputs_have_hashes(self):
        a, b = g.outputs(self.root), g.outputs(self.root)
        self.assertEqual(a, b)
        s = json.loads(a[g.OUTPUT_JSON])
        self.assertEqual(set(s['source_hashes']), set(g.BASE_INPUTS + [s['research']['reference_path']]))
        self.assertNotIn(g.OUTPUT_JSON, s['source_hashes'])
        self.assertNotIn(g.OUTPUT_MD, s['source_hashes'])

    def test_build_date_does_not_replace_evidence_dates(self):
        s = g.build(self.root)
        self.assertEqual(s['design_date'], '2026-10-22')
        self.assertEqual(s['finance']['advisory_coverage']['retained_review_cutoff'], '2026-10-08')
        self.assertEqual(s['research']['review_cutoff'], '2026-10-15')

    def test_reference_hash_drift_fails(self):
        pointer = g.read_json(self.root, 'data/current_research_reference.json')
        (self.root / pointer['reference_path']).write_text('SYNTHETIC DRIFT')
        self.reject()

    def test_research_adoption_cannot_grant_live_authority(self):
        self.mutate_json('data/census_v13/adoption_record.json', lambda x: x['authority'].update(live_use_authorized=True))
        self.reject()

    def test_live_gate_change_requires_rendering_review(self):
        self.mutate_json('data/current_research_reference.json', lambda x: x['live_use_gates'].update(SP08P1='AUTHORIZED'))
        self.reject()

    def test_active_watch_conflicts_with_current_policy(self):
        self.mutate_json('data/census_v13/summary.json', lambda x: x.update(course_watch='active'))
        self.reject()

    def test_first_pass_rewrite_is_rejected(self):
        self.mutate_json('data/census_v13/summary.json', lambda x: x.update(historical_first_pass_supported=61))
        self.reject()

    def test_zero_savings_is_not_unknown(self):
        self.mutate_json('data/census_v13/summary.json', lambda x: x.update(cash_savings=0))
        self.reject()

    def test_obsolete_transcript_gap_cannot_return(self):
        self.mutate_json('data/census_v7/final_summary.json', lambda x: x.update(remaining_transcript_retrieval_gaps=7))
        self.reject()

    def test_spm_proposal_cannot_silently_become_approved(self):
        path = self.root / 'data/spm_2027_mission_budget.csv'
        path.write_text(path.read_text().replace('2027_SG_proposal_not_GA_appropriation', 'GA_approved'))
        self.reject()

    def test_spm_control_mismatch_is_rejected(self):
        path = self.root / 'data/spm_2027_financing_controls.csv'
        path.write_text(path.read_text().replace('422671', '422672'))
        self.reject()

    def test_owner_requests_cannot_be_invented(self):
        path = self.root / 'data/owner_review/evidence_gap_register.csv'
        path.write_text(path.read_text().replace('NOT_SENT', 'SENT'))
        self.reject()

    def test_manifest_current_role_selection_is_explicit(self):
        designated = g.current_manifest_designations({'current_roles': {'x': {'path': 'old_v1.json', 'scope': 'test'}}})
        self.assertEqual(designated, [{'path': 'old_v1.json', 'scope': 'test', 'role': 'x'}])
        self.assertEqual(g.current_manifest_designations({'artifacts': [{'path': 'latest_v99.json'}]}), [])

    def test_issue_receipt_conflicts_are_rejected(self):
        self.mutate_json('metadata/issue_migration_receipt.json', lambda x: x.update(issue_count=-1))
        self.reject()

    def test_canonical_manifest_cannot_point_elsewhere(self):
        self.mutate_json('metadata/canonical_manifest.json', lambda x: x['current_roles']['research_reference'].update(path='data/census_v12/reference_preview.json'))
        self.reject()

    def test_render_keeps_qualifications(self):
        text = g.render(g.build(self.root))
        for required in ('not estimated', 'PAUSED', 'BLOCKED_FOR_LIVE_USE', 'historical first pass',
                         '27/36', 'not a current official publication-status', 'Already embedded',
                         'not a count of unique current operational defects'):
            self.assertIn(required, text)


if __name__ == '__main__':
    unittest.main()
