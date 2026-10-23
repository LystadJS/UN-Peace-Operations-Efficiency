#!/usr/bin/env python3
"""Negative controls for scope-limited priority lineage, using isolated copies."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('priority_lineage',ROOT/'scripts/validate_priority_lineage.py')
model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)

class Checks(unittest.TestCase):
    def test_scope_is_not_global_closure(self):
        r=model.build(ROOT)
        self.assertEqual(r['original_recognized_gap_count'],196)
        self.assertEqual(r['selected_expression_count'],6)
        self.assertEqual(len(r['claim_chains']),7)
        self.assertEqual(r['selected_status_counts']['EXTERNAL_SOURCE_DIRECTORY_UNRESOLVED'],2)
        self.assertIn('does not subtract',r['global_gap_disposition'])

    def test_static_paths_have_evidence_and_no_fake_producer(self):
        r=model.build(ROOT)
        for expression in r['selected_expressions']:
            for path in expression['resolved_repository_paths']:
                self.assertIn(path,r['source_sha256'])
        for chain in r['claim_chains']:
            self.assertEqual(chain['transformation']['role'],'ARITHMETIC_AND_DECLARATION_GUARD_NOT_SOURCE_DATA_PRODUCER')
            self.assertTrue(chain['transformation']['lines'])
            self.assertTrue(chain['consuming_case']['evidence_csv_lines'])

    def corruption(self,path,mutate):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for p in model.build(ROOT)['source_sha256']:
                target=root/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/p).read_bytes())
            value=(root/path).read_text();(root/path).write_text(mutate(value))
            with self.assertRaises(ValueError):model.build(root)

    def test_selected_frozen_script_drift_rejected(self):
        self.corruption('scripts/validate_transaction_controls.py',lambda s:s+'\n# changed\n')

    def test_case_source_snapshot_drift_rejected(self):
        def change(s):
            d=json.loads(s)
            for e in d['evidence']:
                if e['path']=='data/transaction_control_baseline.csv':
                    e['source_snapshot']['published_amount_usd']='1';break
            return json.dumps(d)
        self.corruption('data/cases/C02.json',change)

    def test_control_amount_drift_rejected(self):
        self.corruption('data/transaction_control_baseline.csv',lambda s:s.replace('"394000"','"394001"',1))

    def test_frozen_inventory_cannot_shrink(self):
        self.corruption('docs/repository_lineage.md',lambda s:s.replace('- Line 10: `READS` — `<dynamic expression>`','',1))

    def test_current_outputs_reproduce(self):
        for p,body in model.outputs(ROOT).items():self.assertEqual((ROOT/p).read_text(),body,p)

if __name__=='__main__':unittest.main()
