#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_intervention_evaluation import fixture
import calculate_net_benefit as model

class NetBenefitTests(unittest.TestCase):
    def data(self):
        d=fixture(); d['calculator_version']=model.VERSION; return d
    def test_full_cost_wrapper(self):
        r=model.calculate(self.data()); self.assertEqual(r['net_cost_difference'],'5'); self.assertIsNone(r['savings_amount']); self.assertFalse(r['candidate_advanced'])
    def test_missing_version(self): self.assertIsNone(model.calculate({})['net_cost_difference'])
    def test_missing_counterfactual(self):
        d=self.data(); del d['counterfactual']; self.assertIsNone(model.calculate(d)['net_cost_difference'])
    def test_failed_guard(self):
        d=self.data(); d['guards'][0]['status']='FAIL'; self.assertIsNone(model.calculate(d)['net_cost_difference'])
    def test_unmatched_transfer(self):
        d=self.data(); d['baseline']['costs'][-1]['amount']='-29'; self.assertIsNone(model.calculate(d)['net_cost_difference'])
    def test_float_cost(self):
        d=self.data(); d['baseline']['costs'][0]['amount']=100.0; self.assertIsNone(model.calculate(d)['net_cost_difference'])
    def test_period_scope(self):
        d=self.data(); d['intervention_scenario']['period_end']='2026-11-30'; self.assertIsNone(model.calculate(d)['net_cost_difference'])
    def test_omitted_cost(self):
        d=self.data(); d['intervention_scenario']['coverage']['omitted_components']=['residual']; self.assertIsNone(model.calculate(d)['net_cost_difference'])

if __name__=='__main__': unittest.main()
