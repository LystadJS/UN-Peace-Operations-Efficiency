#!/usr/bin/env python3
"""Adversarial semantic-key and cross-unit join checks against disposable copies."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('priority_semantics',ROOT/'scripts/validate_priority_semantics.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class Checks(unittest.TestCase):
    def fixture(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);root=Path(temp.name)
        for name,*_ in m.CONTRACTS:
            path='data/'+name+'.csv';(root/path).parent.mkdir(parents=True,exist_ok=True);(root/path).write_bytes((ROOT/path).read_bytes())
        path='data/portfolio/entities.json';(root/path).parent.mkdir(parents=True,exist_ok=True);(root/path).write_bytes((ROOT/path).read_bytes())
        return root
    def test_actual_review_is_scoped(self):
        d=m.build();self.assertEqual(len(d['datasets']),11);self.assertEqual(d['candidate_advancement'],'NONE')
        self.assertTrue(all(not r['primary_source_reauthenticated'] and not r['operational_population_complete'] for r in d['datasets']))
    def test_duplicate_control_rejected(self):
        root=self.fixture();p=root/'data/transaction_control_baseline.csv';s=p.read_text();p.write_text(s.replace('UF02,','UF01,').replace('"UF02",','"UF01",'))
        with self.assertRaises(ValueError):m.build(root)
    def test_missing_request_control_rejected(self):
        root=self.fixture();p=root/'data/transaction_evidence_requests.csv';p.write_text(p.read_text().replace('UF01','MISSING_CONTROL'))
        with self.assertRaises(ValueError):m.build(root)
    def test_dollar_thousand_mismatch_rejected(self):
        root=self.fixture();p=root/'data/transaction_control_baseline.csv';p.write_text(p.read_text().replace('394000','394001'))
        with self.assertRaises(ValueError):m.build(root)
    def test_broken_graph_endpoint_rejected(self):
        root=self.fixture();p=root/'data/public_finance_edges.csv';p.write_text(p.read_text().replace('SPM27_TOTAL','BROKEN_PARENT'))
        with self.assertRaises(ValueError):m.build(root)
    def test_changed_bytes_recorded_even_without_row_change(self):
        root=self.fixture();p=root/'data/transaction_sources.csv';p.write_bytes(p.read_bytes()+b'\n');a=m.build(ROOT);b=m.build(root)
        hashes=lambda x:{r['path']:r['source_sha256'] for r in x['datasets']}
        self.assertNotEqual(hashes(a)['data/transaction_sources.csv'],hashes(b)['data/transaction_sources.csv'])
    def test_unknown_and_zero_are_different(self):
        d=m.build();self.assertEqual(set(d['observations']['verified_transaction_pairs'].values()),{0})
        r=next(x for x in d['datasets'] if x['path'].endswith('transaction_control_baseline.csv'))
        self.assertEqual(r['empty_or_explicit_unavailable_counts']['additional_net_savings_usd'],12)
    def test_generated_outputs_current(self):
        for p,s in m.outputs().items():self.assertEqual((ROOT/p).read_text(),s)
if __name__=='__main__':unittest.main()
