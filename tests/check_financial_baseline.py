#!/usr/bin/env python3
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_financial_baseline import build, encoded, TARGET
from validate_financial_nonadditivity import validate, validate_selection


class FinanceChecks(unittest.TestCase):
    def test_exact_source_baseline(self):
        data = build()
        self.assertEqual(validate(data), [])
        self.assertEqual((ROOT / TARGET).read_text(), encoded())
        self.assertEqual(data['amounts']['six_maintenance']['amount'], '4028188.0')
        self.assertEqual(data['amounts']['eleven_maintenance']['amount'], '4625940.1')
        self.assertEqual(data['amounts']['embedded_measures']['amount'], '14692.5')

    def test_parent_child_double_count_rejected(self):
        data = build()
        for keys in [('six_maintenance', 'eleven_maintenance'), ('spm_total', 'spm_rsce'), ('spm_total', 'spm_missions')]:
            self.assertTrue(validate_selection(data, keys))

    def test_different_versions_periods_rejected(self):
        data = build()
        self.assertTrue(validate_selection(data, ['six_maintenance', 'six_sg_request']))
        self.assertTrue(validate_selection(data, ['eleven_maintenance', 'spm_total']))
        self.assertTrue(validate_selection(data, ['closures_2026']))
        self.assertTrue(validate_selection(data, ['embedded_measures']))

    def test_unknown_benefit_not_zero(self):
        data = build()
        data['benefits']['realized_saving'] = '0'
        self.assertTrue(validate(data))

    def test_component_tamper_detected(self):
        data = build()
        data['amounts']['spm_rsce']['amount'] = '0'
        self.assertTrue(validate(data))

    def test_mislabeled_savings_detected(self):
        data = build()
        data['amounts']['embedded_measures']['savings_finding'] = True
        self.assertTrue(validate(data))

    def test_single_resource_control_allowed(self):
        self.assertEqual(validate_selection(build(), ['spm_total']), [])


if __name__ == '__main__':
    unittest.main()
