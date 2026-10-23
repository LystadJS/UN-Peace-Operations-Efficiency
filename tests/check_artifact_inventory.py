#!/usr/bin/env python3
"""Focused corruption and classification controls for frozen artifact inventory."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('inventory', ROOT / 'scripts/build_artifact_inventory.py')
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)


class InventoryTests(unittest.TestCase):
    def test_full_frozen_scope_exactly_once(self):
        rows = inventory.build(ROOT)
        self.assertEqual(len(rows), 554)
        self.assertEqual(len({r['path'] for r in rows}), 554)
        self.assertEqual(sum(r['tracked_at_scope'] == 'true' for r in rows), 543)

    def test_current_sounding_name_does_not_establish_currency(self):
        result = inventory.classify('data/current_approved_savings.csv', {}, {})
        self.assertEqual(result[3], 'not_established_by_inventory')

    def test_manifest_membership_does_not_establish_current(self):
        path = 'data/census_v11/summary.json'
        result = inventory.classify(path, {path: ['data/census_v11/output_manifest.json']}, {})
        self.assertEqual(result[0], 'manifested_release_output')
        self.assertEqual(result[3], 'not_established_by_inventory')

    def test_only_designated_pointer_target_is_current_reference(self):
        path = 'data/census_v13/research_reference.json'
        self.assertEqual(inventory.classify(path, {}, {'reference_path': path})[3], 'designated_current_research_reference')
        self.assertEqual(inventory.classify(path, {}, {})[3], 'not_established_by_inventory')

    def test_manifest_shapes_and_invalid_digest(self):
        self.assertEqual(inventory.manifest_paths({'files': {'data/x.csv': 'a'*64}}), ['data/x.csv'])
        self.assertEqual(inventory.manifest_paths([{'path':'data/x.csv','sha256':'a'*64}]), ['data/x.csv'])
        self.assertEqual(inventory.manifest_paths({'path': 'not_a_manifest'}), [])

    def test_deterministic_output(self):
        self.assertEqual(inventory.encode(inventory.build(ROOT)), inventory.encode(inventory.build(ROOT)))


if __name__ == '__main__':
    unittest.main()
