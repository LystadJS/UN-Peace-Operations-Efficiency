#!/usr/bin/env python3
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_operational_evidence import row
import reconcile_evidence_transactions as model

def fixture():
    return {'schema_version':'E08-1.0','reconciliation_version':model.VERSION,'evidence_mode':'SYNTHETIC',
        'records':[row(),row('p1','PAYMENT','60'),row('p2','CASH_RECEIPT','40')],
        'timing_tolerance_days':30,'allocations':[
            {'allocation_id':'a1','claim_id':'claim','settlement_id':'p1','amount':'60','source_receipt':'SYNTHETIC'},
            {'allocation_id':'a2','claim_id':'claim','settlement_id':'p2','amount':'40','source_receipt':'SYNTHETIC'}]}

class ReconciliationTests(unittest.TestCase):
    def test_one_to_many(self):
        result=model.reconcile(fixture()); self.assertEqual(result['issues'],[]); self.assertIsNone(result['savings_amount'])
    def test_partial_settlement(self):
        d=fixture(); d['allocations'].pop(); self.assertIn('claim',model.reconcile(d)['unallocated_records'])
    def test_no_automatic_subset_guess(self):
        d=fixture(); d['allocations']=[]; self.assertTrue(model.reconcile(d)['issues'])
    def test_duplicate_allocation_edge(self):
        d=fixture(); a=copy.deepcopy(d['allocations'][0]); a['allocation_id']='third'; d['allocations'].append(a)
        self.assertTrue(model.reconcile(d)['issues'])
    def test_reversal_requires_reallocation(self):
        d=fixture(); r=row('r','REVERSAL','10'); r['reversal_of']='p1'; d['records'].append(r)
        self.assertTrue(any('overallocated' in x for x in model.reconcile(d)['issues']))
    def test_over_reversal(self):
        d=fixture(); r=row('r','REVERSAL','61'); r['reversal_of']='p1'; d['records'].append(r)
        self.assertTrue(any('over-reversed' in x for x in model.reconcile(d)['issues']))
    def test_no_cross_scope_netting(self):
        for key,value in [('fund','OTHER'),('currency','EUR'),('cost_object_id','OTHER'),('period_end','2026-02-01')]:
            d=fixture(); d['records'][1][key]=value; self.assertTrue(model.reconcile(d)['issues'],key)
    def test_timing(self):
        d=fixture(); d['records'][1]['event_date']='2026-06-01'; self.assertTrue(model.reconcile(d)['timing_exceptions'])
    def test_cash_receipt_distinguished(self):
        r=model.reconcile(fixture())['balances']; self.assertEqual(r[1]['interpretation'],'NOT_CASH_RECEIPT_PROOF')
        self.assertEqual(r[2]['interpretation'],'CASH_RECEIPT_DECLARED_NOT_AUTHENTICATED')
    def test_float_allocation(self):
        d=fixture(); d['allocations'][0]['amount']=60.0; self.assertTrue(model.reconcile(d)['issues'])
    def test_same_economic_settlement_cannot_enter_twice(self):
        d=fixture(); d['records'][2]['economic_event_id']=d['records'][1]['economic_event_id']
        self.assertTrue(model.reconcile(d)['issues'])
    def test_many_to_one(self):
        d=fixture(); d['records']=[row('c1','CLAIM','40'),row('c2','CLAIM','60'),row('p','PAYMENT','100')]
        for a,c,amount in zip(d['allocations'],['c1','c2'],['40','60']): a.update(claim_id=c,settlement_id='p',amount=amount)
        self.assertEqual(model.reconcile(d)['issues'],[])

if __name__=='__main__': unittest.main()
