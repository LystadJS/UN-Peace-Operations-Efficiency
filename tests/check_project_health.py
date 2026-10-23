#!/usr/bin/env python3
"""Synthetic health-summary corruption controls and deterministic rendering."""
import copy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import build_project_health as health


def fixture():
    return ({'operational_constraints': {'cash_savings': 'not_estimated', 'staff_time_saved': 'not_estimated',
              'live_gates': {'SP08P1': 'BLOCKED_FOR_LIVE_USE', 'SP09P1': 'BLOCKED_FOR_LIVE_USE'}, 'course_watch': 'PAUSED'}},
            {'artifacts': [{}, {}], 'current_roles': {'example': {}}},
            {'issues': [{'issue_id': 'SYNTHETIC:1', 'resolution_state': 'OPEN', 'gate_status': 'BLOCKED'}]},
            {'issue_count': 1})


class HealthTests(unittest.TestCase):
    def test_summary_preserves_unknown_financial_result(self):
        self.assertEqual(health.summarize(*fixture())['cash_savings'], 'not_estimated')

    def test_unknown_cannot_be_zero(self):
        data = list(fixture())
        data[0]['operational_constraints']['cash_savings'] = 0
        with self.assertRaises(ValueError): health.summarize(*data)

    def test_migration_counts_reconcile(self):
        data = list(fixture())
        data[3]['issue_count'] = 2
        with self.assertRaises(ValueError): health.summarize(*data)

    def test_duplicate_issues_rejected(self):
        data = list(fixture())
        data[2]['issues'] *= 2
        data[3]['issue_count'] = 2
        with self.assertRaises(ValueError): health.summarize(*data)

    def test_unknown_gate_counts_preserved(self):
        data = list(fixture())
        data[2]['issues'][0]['gate_status'] = 'UNKNOWN'
        self.assertEqual(health.summarize(*data)['issue_gate_states'], {'UNKNOWN': 1})

    def test_fixed_data_render_is_identical(self):
        record = {'summary': health.summarize(*fixture())}
        self.assertEqual(health.render(record), health.render(copy.deepcopy(record)))
        self.assertIn('full runtime CI is not asserted', health.render(record))


if __name__ == '__main__':
    unittest.main()
