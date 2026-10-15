#!/usr/bin/env python3
"""Synthetic corruption tests for the bounded reference preview, not live outcomes."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import prepare_v12_patch as p


class PatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before = p.read_json(ROOT, p.CANDIDATE)
        cls.requests = p.read_json(ROOT, p.REQUESTS)
        cls.ops = p.operations(cls.before, cls.requests)
        cls.after = p.replay(cls.before, cls.ops)
        cls.target = next(i for i, r in enumerate(cls.before) if r['observation_id'] == 'V9:CY028')

    def test_only_two_rows_change(self):
        self.assertEqual([a['observation_id'] for a, b in zip(self.before, self.after) if a != b],
                         ['V9:CY028', 'V9:CY041'])
        p.validate_preview(self.before, self.after, self.ops, self.requests)

    def test_all_old_qualified_values_retained(self):
        for a, b in zip(self.before, self.after):
            old, new = json.loads(a['qualified_values']), json.loads(b['qualified_values'])
            self.assertTrue(all(new[k] == v for k, v in old.items()))

    def test_replay_does_not_mutate_input(self):
        original = copy.deepcopy(self.before)
        p.replay(self.before, self.ops)
        self.assertEqual(self.before, original)

    def test_stale_text_rejected(self):
        bad = copy.deepcopy(self.before)
        bad[self.target]['source_assertion'] += ' stale'
        with self.assertRaises(ValueError): p.replay(bad, self.ops)

    def test_wrong_source_rejected(self):
        bad = copy.deepcopy(self.before)
        bad[self.target]['source_sha256'] = '0' * 64
        with self.assertRaises(ValueError): p.replay(bad, self.ops)

    def test_reordered_input_rejected(self):
        with self.assertRaises(ValueError): p.replay(list(reversed(self.before)), self.ops)

    def test_second_application_rejected(self):
        with self.assertRaises(ValueError): p.replay(self.after, self.ops)

    def test_inverse_restores_exact_row_objects(self):
        inverse = p.read_json(ROOT, p.OUT + 'reference_inverse.jsonpatch')
        self.assertEqual(p.replay(self.after, inverse), self.before)

    def test_identity_edit_rejected(self):
        bad = [{'op': 'replace', 'path': f'/{self.target}/observation_id', 'value': 'fabricated'}]
        with self.assertRaises(ValueError): p.replay(self.before, bad)

    def test_unrelated_row_change_rejected(self):
        bad = copy.deepcopy(self.after)
        bad[0]['source_assertion'] = 'unrelated change'
        with self.assertRaises(ValueError): p.validate_preview(self.before, bad, self.ops, self.requests)

    def test_wrong_comparator_rejected(self):
        bad = copy.deepcopy(self.after)
        row = next(r for r in bad if r['observation_id'] == 'V9:CY041')
        values = json.loads(row['qualified_values']); values['lifetime_utilized_eur_comparator'] = '>='
        row['qualified_values'] = json.dumps(values)
        with self.assertRaises(ValueError): p.validate_preview(self.before, bad, self.ops, self.requests)

    def test_combined_count_rejected(self):
        bad = copy.deepcopy(self.after)
        values = json.loads(bad[self.target]['qualified_values']); values['count'] = 205
        bad[self.target]['qualified_values'] = json.dumps(values)
        with self.assertRaises(ValueError): p.validate_preview(self.before, bad, self.ops, self.requests)

    def test_patch_operation_tampering_rejected(self):
        bad = copy.deepcopy(self.ops); bad[-1]['value'] = '{}'
        with self.assertRaises(ValueError): p.validate_preview(self.before, self.after, bad, self.requests)

    def test_unrequested_amendment_rejected(self):
        bad = copy.deepcopy(self.requests); bad.append(copy.deepcopy(bad[0]))
        with self.assertRaises(ValueError): p.operations(self.before, bad)

    def test_gate_activation_rejected(self):
        original = p.read_json
        def fake(root, name):
            obj = original(root, name)
            if name.endswith('protocol.json'):
                obj['case_activation']['SP08P1']['owner_a_authorization_ref'] = 'invented'
            return obj
        with patch.object(p, 'read_json', side_effect=fake):
            with self.assertRaises(ValueError): p.closed_gates(ROOT)

    def test_missingness_and_gates_preserved(self):
        s = p.read_json(ROOT, p.OUT + 'patch_summary.json')
        self.assertFalse(s['scoring_resumed'])
        self.assertEqual(s['scoring_withheld'], 2)
        self.assertEqual(s['reference_amendments_adopted'], 0)
        self.assertEqual(s['first_pass_supported_unchanged'], 59)
        self.assertEqual(s['live_gate_status'], 'BLOCKED_FOR_LIVE_USE')
        self.assertEqual(s['staff_time_saved'], 'not_estimated')
        self.assertEqual(s['cash_savings'], 'not_estimated')
        p.closed_gates(ROOT)

    def test_every_generated_output_reproducible(self):
        for name, body in p.outputs(ROOT).items():
            self.assertEqual((ROOT / name).read_bytes(), body, name)

    def test_first_pass_lineage_equal(self):
        old = p.read_csv(ROOT, 'data/census_v11/obligation_reviews.csv')
        new = p.read_csv(ROOT, p.OUT + 'first_pass_lineage.csv')
        self.assertEqual({r['obligation_id']: r['first_pass_disposition'] for r in old},
                         {r['obligation_id']: r['first_pass_disposition'] for r in new})


if __name__ == '__main__':
    unittest.main(verbosity=2)
