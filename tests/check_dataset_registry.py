#!/usr/bin/env python3
"""Meaningful A02 checks: scope, grain safety, keys, duplicates and determinism."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_dataset_registry as b


class RegistryTests(unittest.TestCase):
    def test_exact_frozen_dataset_coverage_and_hashes(self):
        expected = {e['path']: e['sha256'] for e in b.load_json(b.ROOT/b.SCOPE)['files'] if Path(e['path']).suffix in {'.csv','.json'}}
        actual = b.build()
        self.assertEqual(len(actual), len(expected))
        self.assertEqual({r['path']:r['sha256'] for r in actual}, expected)

    def test_repeat_regeneration_is_identical(self):
        self.assertEqual(b.render(b.build()), b.render(b.build()))
        self.assertEqual((b.ROOT/b.OUTPUT).read_text(), b.render(b.build()))

    def test_duplicate_and_empty_declared_keys_do_not_pass(self):
        shape, columns, rows = b.profile_csv(b'id,value\na,1\na,2\n,3\n')
        key, basis, check, dup, empty = b.key_profile(rows, columns, {('id','synthetic_validator')})
        self.assertEqual((basis,check,dup,empty), ('validator_declared','not_unique_or_empty',1,1))

    def test_unique_first_column_is_candidate_not_declared(self):
        self.assertEqual(b.key_profile([{'id':'x'}], ['id'], set())[1], 'first_column_candidate_only')

    def test_json_object_never_becomes_event_row_count(self):
        shape, columns, rows = b.profile_json(b'{"events":10,"metadata":{}}')
        self.assertEqual(shape, 'json_object_not_tabular')
        self.assertIsNone(rows)

    def test_empty_json_array_never_claims_empty_event_population(self):
        self.assertEqual(b.profile_json(b'[]'), ('json_array_not_record_table', [], None))

    def test_header_only_csv_has_no_key_evidence(self):
        self.assertEqual(b.key_profile([], ['id'], set())[2], 'empty_table_no_key_evidence')

    def test_malformed_csv_rejected(self):
        for body in (b'id,id\na,b\n', b'id,value\na\n', b'id\na,b\n'):
            with self.assertRaises(ValueError):
                b.profile_csv(body)

    def test_conflicting_declarations_not_silently_selected(self):
        result=b.key_profile([{'a':'1','b':'1'}],['a','b'],{('a','x'),('b','y')})
        self.assertEqual(result[2], 'not_established')

    def test_current_reference_is_pointer_scoped(self):
        rows={r['path']:r for r in b.build()}
        self.assertEqual(rows['data/census_v13/research_reference.json']['repository_role'], 'current_adopted_research_reference')
        self.assertIn('fixed V8/V9', rows['data/census_v13/research_reference.json']['status_basis'])
        self.assertEqual(rows['data/census_v12/reference_preview.json']['repository_role'], 'versioned_artifact_currency_unresolved')


if __name__ == '__main__':
    unittest.main()
