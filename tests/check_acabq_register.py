#!/usr/bin/env python3
"""Evidence-scope and nonadditivity checks for the retained advice register."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('acabq_register', ROOT / 'scripts/build_acabq_register.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RegisterChecks(unittest.TestCase):
    def test_deterministic_current(self):
        self.assertEqual((ROOT / module.TARGET).read_text(), module.encoded())

    def test_no_adoption_or_realization_upgrade(self):
        records = module.build()['recommendations']
        self.assertEqual(len(records), 48)
        self.assertEqual(len({r['recommendation_id'] for r in records}), 48)
        for record in records:
            self.assertEqual(record['authority_classification'], 'ACABQ_ADVICE')
            self.assertEqual(record['adoption_status'], 'GA_ACCEPTANCE_NOT_ESTABLISHED_IN_RETAINED_CORPUS')
            self.assertTrue(record['financial_effect']['not_a_savings_finding'])
            self.assertTrue(record['paragraph_locator'])

    def test_unknown_is_not_zero(self):
        data = module.build()
        self.assertEqual(data['coverage']['numerical_advice_reviewed'], 27)
        self.assertEqual(data['coverage']['mission_advice_unreviewed'], 9)
        self.assertIsNone(data['coverage']['full_spm_advice_adjusted_total'])
        self.assertEqual(data['evidence_cutoff'], '2026-10-08')

    def test_sign_and_perimeter_controls(self):
        controls = module.build()['advisory_adjustment_controls']
        self.assertEqual(controls['by_disjoint_perimeter'], {
            'SECTION_3_NON_SPM': '-189.3', 'SECTION_5_REGULAR': '-26.7', 'SPM_CLUSTER_1': '-182.5'})
        self.assertFalse(controls['savings_finding'])

    def test_input_changes_invalidate_snapshot(self):
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for path in module.INPUTS.values():
                (root / path).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / path, root / path)
            before = module.build(root)
            path = root / module.INPUTS['financial']
            path.write_text(path.read_text().replace('-4.8', '-5.8'))
            after = module.build(root)
            self.assertNotEqual(before['source_receipts'], after['source_receipts'])
            self.assertNotEqual(before['advisory_adjustment_controls'], after['advisory_adjustment_controls'])


if __name__ == '__main__':
    unittest.main()
