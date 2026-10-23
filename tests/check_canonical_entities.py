#!/usr/bin/env python3
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('entities', ROOT / 'scripts/build_canonical_entities.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CanonicalEntityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = MODULE.build(ROOT)

    def resolve(self, alias):
        return {x['entity_id'] for x in self.result['aliases'] if x['alias'] == alias}

    def test_all_spm_rows_have_unique_ids(self):
        self.assertEqual(len([x for x in self.result['entities'] if x['entity_id'].startswith('UNPO-SPM')]), 36)

    def test_similar_names_not_merged(self):
        self.assertNotEqual(self.resolve('UNSOS'), self.resolve('UNSOH'))
        self.assertNotEqual(self.resolve('Good offices in Cyprus'), self.resolve('UNFICYP'))
        self.assertFalse(self.resolve('UNGSC'))

    def test_reviewed_spm_aliases(self):
        self.assertEqual(self.resolve('UNSCOL'), {'UNPO-SPM031'})
        self.assertEqual(self.resolve('BINUH'), {'UNPO-SPM035'})

    def test_lifecycle_not_inferred(self):
        self.assertTrue(all(x['lifecycle_status'] == 'UNKNOWN_NOT_VERIFIED' for x in self.result['entities']))

    def test_aggregate_clients_unresolved(self):
        self.assertTrue(self.result['unresolved_references'])
        self.assertTrue(all(x['entity_id'] is None for x in self.result['unresolved_references']))

    def test_no_split_composite_allocation(self):
        entry = next(x for x in self.result['entities'] if x['entity_id'] == 'UNPO-ALLOCATION-SA04')
        self.assertEqual(entry['entity_type'], 'COMPOSITE_BUDGET_ALLOCATION_NOT_ORGANIZATION')

    def test_broken_alias_and_relationship_rejected(self):
        for collection, key in [('aliases', 'entity_id'), ('relationships', 'to_entity_id')]:
            bad = copy.deepcopy(self.result)
            bad[collection][0][key] = 'MISSING'
            with self.assertRaises(ValueError):
                MODULE.validate(bad)

    def test_duplicate_ids_rejected(self):
        bad = copy.deepcopy(self.result)
        bad['entities'].append(bad['entities'][0])
        with self.assertRaises(ValueError):
            MODULE.validate(bad)

    def test_inclusive_share_count_and_period(self):
        rows = [x for x in self.result['relationships'] if x['relationship'] == 'INCLUSIVE_APPROPRIATION_CONTAINS_COST_SHARE']
        self.assertEqual(len(rows), 12)
        self.assertTrue(all(x['period'] == '2026-07-01_to_2027-06-30' for x in rows))


if __name__ == '__main__':
    unittest.main()
