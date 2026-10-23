#!/usr/bin/env python3
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('portfolio_release', ROOT / 'scripts/build_portfolio_release.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PortfolioReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = MODULE.build(ROOT)

    def test_manifest_matches_current_scoped_artifacts(self):
        self.assertEqual(MODULE.validate_manifest(self.value, ROOT)['artifact_count'], len(self.value['artifacts']))

    def test_no_self_cycle_or_generated_combined_outputs(self):
        paths = {x['path'] for x in self.value['artifacts']}
        self.assertFalse(paths.intersection(MODULE.EXCLUSIONS))
        self.assertTrue(set(MODULE.REQUIRED) <= paths)

    def test_dangerous_paths_rejected(self):
        for path in ('../secret', '/tmp/secret', 'data/cases/../x', 'data/restricted/a.json',
                     'docs/a.internal.csv', 'docs/.env', 'scripts/key.pem', 'docs/x\\y'):
            self.assertFalse(MODULE.safe_path(path), path)

    def test_changed_hash_rejected(self):
        value = copy.deepcopy(self.value)
        value['artifacts'][0]['sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            MODULE.validate_manifest(value, ROOT)

    def test_missing_core_and_duplicate_rejected(self):
        for mutation in ('missing', 'duplicate'):
            value = copy.deepcopy(self.value)
            if mutation == 'missing':
                value['artifacts'] = [x for x in value['artifacts'] if x['path'] != MODULE.REQUIRED[0]]
            else:
                value['artifacts'].append(value['artifacts'][0])
            with self.assertRaises(ValueError):
                MODULE.validate_manifest(value, ROOT)

    def test_decision_grade_claim_rejected(self):
        value = copy.deepcopy(self.value)
        value['release_class'] = 'DECISION_GRADE'
        value['decision_grade_portfolio'] = 'COMPLETE'
        with self.assertRaises(ValueError):
            MODULE.validate_manifest(value, ROOT)

    def test_no_runtime_or_institutional_attestation(self):
        self.assertEqual(self.value['institutional_approval'], 'NOT_OBTAINED')
        self.assertIn('NOT_ATTESTED', self.value['runtime_validation'])
        self.assertEqual(self.value['verified_benefits'], 'NOT_ESTIMATED')

    def test_actual_benefit_and_execution_changes_require_review(self):
        original = MODULE.read
        mutations = [
            ('data/portfolio/verified_benefit_ledger.json', lambda value: value['entries'].append({'amount': 100})),
            ('data/cases/C01.json', lambda value: value['benefits'].__setitem__('cashable_saving', 100)),
            ('data/cases/C01.json', lambda value: value.__setitem__('candidate_state', 'REALIZED')),
            ('data/adjudications/execution_gates.json', lambda value: value['records'][0].__setitem__('execution_authorized', True)),
            ('data/realization/implementation_gates.json', lambda value: value['approved_interventions'].append('C01')),
        ]
        for target, change in mutations:
            def altered(root, path):
                value = original(root, path)
                if path == target:
                    change(value)
                return value
            with self.subTest(target=target), patch.object(MODULE, 'read', side_effect=altered):
                with self.assertRaises(ValueError):
                    MODULE.check_claim_boundary(ROOT)

    def test_untracked_and_symlink_candidates_are_not_silently_omitted(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for prefix in MODULE.PREFIXES:
                (root / prefix).mkdir(parents=True, exist_ok=True)
            for path in MODULE.REQUIRED:
                (root / path).parent.mkdir(parents=True, exist_ok=True)
                (root / path).write_text('{}')
            ready = root / 'docs/ready_untracked.md'
            ready.write_text('ready')
            self.assertIn('docs/ready_untracked.md', MODULE.scope_files(root))
            (root / 'docs/link.md').symlink_to(ready)
            with self.assertRaises(ValueError):
                MODULE.scope_files(root)


if __name__ == '__main__':
    unittest.main()
