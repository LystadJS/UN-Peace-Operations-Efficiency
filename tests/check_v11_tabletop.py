#!/usr/bin/env python3
"""Checks of the retained tabletop, not independent human verification."""
import copy,csv,hashlib,importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'data/census_v11'
spec=importlib.util.spec_from_file_location('v11',ROOT/'scripts/rehearse_v11.py');v11=importlib.util.module_from_spec(spec);spec.loader.exec_module(v11)
class TabletopChecks(unittest.TestCase):
 def test_01_integrity(self):v11.check()
 def test_02_exact_population(self):
  a=v11.read_csv(ROOT/'data/census_v10/product_obligations.csv');b=v11.read_csv(D/'obligation_reviews.csv')
  self.assertEqual({r['obligation_id'] for r in a},{r['obligation_id'] for r in b});self.assertEqual(len(b),61)
 def test_03_first_pass_not_erased(self):
  r={x['observation_id']:x for x in v11.read_csv(D/'obligation_reviews.csv')}
  self.assertEqual(r['V9:CY028']['source_semantics'],'needs_correction');self.assertEqual(r['V9:CY041']['source_semantics'],'supported')
  self.assertEqual(sum(x['first_pass_disposition']=='supported' for x in r.values()),59)
 def test_04_amendments_are_not_reference_edits(self):
  a=json.loads((D/'amendment_requests.json').read_text());self.assertEqual(len(a),2)
  self.assertTrue(all(x['status']=='proposed_source_checked_not_applied_to_frozen_reference' for x in a))
  s={x['observation_id']:x for x in v11.read_csv(ROOT/'data/census_v10/fixed_source_scope.csv')}
  self.assertIn('and three persons in custody',s['V9:CY028']['source_assertion'])
 def test_05_distinct_action_and_explicit_strict_operator(self):
  p={x['observation_id']:x for x in json.loads((D/'proposed_support_records.json').read_text())}
  self.assertEqual(p['V9:CY028']['tabletop_proposed_values']['custody_action'],'exchange_of_individuals_in_custody')
  self.assertEqual(p['V9:CY041']['tabletop_proposed_values']['lifetime_utilized_eur_comparator'],'>')
 def test_06_no_real_measurements_or_authority(self):
  s=json.loads((D/'tabletop_summary.json').read_text())
  for k in ['owner_approvals','owner_tabletop_reviews','live_trials','live_time_records','reference_amendments_adopted']:self.assertEqual(s[k],0)
  self.assertEqual(s['live_gate_status'],'BLOCKED_FOR_LIVE_USE');v11.closed_gates()
 def test_07_all_scenarios_executed_not_owner_claims(self):
  rows=v11.read_csv(D/'scenario_execution.csv');self.assertEqual(len(rows),12)
  self.assertEqual(sum(r['evidence_class']=='synthetic_safety_or_accounting' for r in rows),2)
  self.assertTrue(all(r['execution']=='assistant_tabletop_not_owner_trial' for r in rows))
 def test_08_mutated_inequality_is_rejected(self):
  f=v11.read_csv(ROOT/'data/census_v10/fixed_source_scope.csv');row=next(x for x in f if x['observation_id']=='V8:O06');v=json.loads(row['qualified_values']);v['attendance_comparator']='=';row['qualified_values']=json.dumps(v)
  self.assertFalse(v11.scenario_tests(f)['SC02'])
 def test_09_material_error_overrides_faster(self):
  for faster in [True,False]:self.assertEqual(v11.safety_decision(faster=faster,material_error=True),'do_not_advance')
  self.assertNotEqual(v11.safety_decision(faster=True,material_error=False),'authorized')
 def test_10_all_sources_and_boundary_population(self):
  s=v11.read_csv(D/'source_authentication.csv');self.assertEqual(len(s),14)
  r=v11.read_csv(D/'obligation_reviews.csv');self.assertEqual(sum(x['obligation_class']=='boundary_preservation' for x in r),16)
  self.assertEqual(len(v11.read_csv(D/'anchor_checks.csv')),64)
if __name__=='__main__':unittest.main(verbosity=2)
