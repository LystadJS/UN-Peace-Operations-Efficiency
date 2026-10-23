#!/usr/bin/env python3
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('reform_inventory', ROOT / 'scripts/build_reform_claim_inventory.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ReformInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = MODULE.build(ROOT)

    def test_population_exactly_once(self):
        paths = MODULE.git(ROOT, 'ls-tree', '-r', '--name-only', MODULE.BASELINE).decode().splitlines()
        self.assertEqual(sorted(paths), sorted(x['path'] for x in self.inventory['artifacts']))

    def test_counts_and_unique_locators(self):
        rows = self.inventory['claims']
        self.assertEqual(len(rows), sum(a['matched_lines'] for a in self.inventory['artifacts']))
        self.assertEqual(len(rows), len({x['claim_id'] for x in rows}))

    def test_no_symbol_confers_adoption(self):
        for claim in self.inventory['claims']:
            self.assertEqual(claim['authority_status'], 'AUTHORITY_UNRESOLVED')
            self.assertEqual(claim['verification_status'], 'NOT_SEMANTICALLY_ADJUDICATED')

    def test_exact_source_lines(self):
        cache = {}
        for claim in self.inventory['claims']:
            path = claim['path']
            if path not in cache:
                cache[path] = MODULE.git(ROOT, 'show', MODULE.BASELINE + ':' + path).decode().splitlines()
            self.assertEqual(claim['claim_text'], cache[path][claim['line'] - 1])

    def test_binary_exclusion_visible(self):
        excluded = [x for x in self.inventory['artifacts'] if x['scan_status'] == 'BINARY_NOT_TEXT_EXTRACTED']
        self.assertTrue(excluded)
        self.assertTrue(any(x['path'].endswith('.pdf') for x in excluded))

    def test_metadata_and_history_not_current_factual_authority(self):
        manifest = {'artifacts': [], 'current_roles': {}}
        self.assertEqual(MODULE.classify('history/pre_controls/README.md', manifest)[0], 'HISTORICAL')
        self.assertEqual(MODULE.classify('metadata/a.json', manifest)[1], 'control_or_metadata_reference')
        self.assertEqual(MODULE.classify('data/current_approved.json', manifest)[0], 'UNRESOLVED')


if __name__ == '__main__':
    unittest.main()
