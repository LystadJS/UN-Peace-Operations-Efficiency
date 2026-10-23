#!/usr/bin/env python3
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('overlap',ROOT/'scripts/build_overlap_graph.py')
model=importlib.util.module_from_spec(spec); spec.loader.exec_module(model)

class OverlapTests(unittest.TestCase):
    def test_preserve_all_hyperedges_and_singletons(self):
        result=model.build(); pools=json.loads((ROOT/model.INPUTS[1]).read_text())
        self.assertEqual(len(result['hyperedges']),len(pools['pools']))
        self.assertTrue(any(len(e['member_node_ids'])==1 for e in result['hyperedges']))
        self.assertIsNone(result['verified_benefit_total']); self.assertFalse(result['aggregation_allowed'])
    def test_alias_namespaces_do_not_conflate_c02(self):
        nodes={n['node_id']:n for n in model.build()['nodes']}
        aliases=nodes['CASE02']['aliases']
        self.assertIn({'namespace':'ROADMAP_CASE','value':'C02'},aliases)
        self.assertNotIn('C02',[a['value'] for a in aliases if a['namespace']=='LEGACY_CANDIDATE'])
    def test_shared_lebanon_scope_preserved(self):
        edge=next(e for e in model.build()['hyperedges'] if e['pool_id']=='LEBANON_TRANSITION')
        self.assertEqual(edge['member_node_ids'],['CASE02','CASE13'])
        self.assertFalse(edge['actual_duplicate_cost_proven'])
    def test_corrupt_membership_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for path in (*model.INPUTS,'scripts/build_overlap_graph.py'):
                (root/path).parent.mkdir(parents=True,exist_ok=True); (root/path).write_bytes((ROOT/path).read_bytes())
            pools=json.loads((root/model.INPUTS[1]).read_text()); pools['pools'][0]['intervention_ids']=['CASE99']
            (root/model.INPUTS[1]).write_text(json.dumps(pools))
            with self.assertRaises(ValueError): model.build(root)
    def test_current_output(self):
        for path,value in model.outputs().items(): self.assertEqual((ROOT/path).read_text(),value)

if __name__=='__main__': unittest.main()
