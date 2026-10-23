#!/usr/bin/env python3
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('interventions',ROOT/'scripts/build_intervention_register.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class InterventionTests(unittest.TestCase):
    def setUp(self):
        self.register=module.build_interventions(ROOT)
        self.pools=module.build_pools(self.register)

    def test_source_populations_and_distinct_namespaces(self):
        counts=self.register['source_population_counts']
        self.assertEqual((counts['umbrella_rows'],counts['mission_child_rows'],counts['roadmap_cases']),(14,9,14))
        self.assertEqual(counts['legacy_candidates'],19)
        self.assertEqual(counts['public_opportunities'],18)
        module.validate(self.register,self.pools)

    def test_snapshot_preserves_hierarchy_parent_links(self):
        import csv
        with (ROOT/'data/consolidation_comprehensive_2027.csv').open(newline='') as stream:
            self.assertEqual(self.register['legacy_populations']['hierarchy'],list(csv.DictReader(stream)))

    def test_duplicate_case_rejected(self):
        self.register['interventions'][1]['intervention_id']='CASE01'
        with self.assertRaises(ValueError): module.validate(self.register)

    def test_unsupported_advancement_rejected(self):
        self.register['interventions'][0]['candidate_state']='FINANCIALLY_VALIDATED'
        with self.assertRaises(ValueError): module.validate(self.register)

    def test_monetary_zero_is_not_unknown(self):
        self.register['interventions'][0]['benefit_amount']=0
        with self.assertRaises(ValueError): module.validate(self.register)

    def test_umbrella_total_rejected(self):
        self.register['aggregation_allowed']=True
        with self.assertRaises(ValueError): module.validate(self.register)

    def test_broken_membership_rejected(self):
        self.pools['pools'][0]['intervention_ids']=[]
        with self.assertRaises(ValueError): module.validate(self.register,self.pools)

    def test_unbacked_allocation_rejected(self):
        self.pools['allocation_ledger']=[{'amount':1}]
        with self.assertRaises(ValueError): module.validate(self.register,self.pools)

    def test_lebanon_cases_share_pool(self):
        pool=next(p for p in self.pools['pools'] if p['pool_id']=='LEBANON_TRANSITION')
        self.assertEqual(pool['intervention_ids'],['CASE02','CASE13'])

    def test_outputs_current(self):
        for path,text in module.outputs(ROOT).items():
            self.assertEqual((ROOT/path).read_text(encoding='utf-8'),text,path)

if __name__=='__main__': unittest.main()
