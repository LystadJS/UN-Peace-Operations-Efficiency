#!/usr/bin/env python3
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import validate_operational_evidence as model

def row(ident='claim',event='CLAIM',amount='100'):
    return {'record_id':ident,'record_type':'transaction','case_id':'SYNTHETIC',
        'entity_id':'CLIENT','source_receipt':'SYNTHETIC_ONLY','source_locator':'fixture row',
        'cost_object_id':'service1','economic_event_id':'SYNTHETIC-'+ident,'fund':'F1','currency':'USD','unit':'currency_units',
        'period_start':'2026-01-01','period_end':'2026-01-31','event_date':'2026-02-01',
        'payer_entity':'CLIENT','provider_entity':'PROVIDER','event_type':event,'amount':amount}

def fixture(): return {'schema_version':model.VERSION,'evidence_mode':'SYNTHETIC','records':[row()]}

class EvidenceTests(unittest.TestCase):
    def test_structural_only(self):
        result=model.receipt(fixture()); self.assertFalse(result['issues']); self.assertFalse(result['candidate_advanced'])
    def test_missing_unknown(self):
        d=fixture(); d['records'][0]['amount']=None; self.assertTrue(model.validate(d))
    def test_float_rejected(self):
        d=fixture(); d['records'][0]['amount']=0.1; self.assertTrue(model.validate(d))
    def test_duplicate(self):
        d=fixture(); d['records']*=2; self.assertTrue(model.validate(d))
    def test_empty(self):
        d=fixture(); d['records']=[]; self.assertTrue(model.validate(d))
    def test_no_source(self):
        d=fixture(); d['records'][0]['source_receipt']=''; self.assertTrue(model.validate(d))
    def test_invalid_date(self):
        d=fixture(); d['records'][0]['event_date']='2026-02-30'; self.assertTrue(model.validate(d))
    def test_typed_evidence_minimum_fields(self):
        for kind in ('asset','post','workload','outcome'):
            d=fixture(); d['records'][0]['record_type']=kind
            self.assertTrue(model.validate(d),kind)
    def test_valid_specialized_records(self):
        fields={'asset':{'asset_id':'A','movement_id':'M','movement_type':'RECEIPT','custodian_from':'A','custodian_to':'B','condition':'INSPECTED','quantity':'1'},
            'post':{'post_id':'P','action':'ABOLISH','effective_date':'2026-02-01','work_transfer_receipt':'SYNTHETIC','fte':'1'},
            'workload':{'activity_id':'A','output_id':'O','worker_token':'TOKEN','measurement_method':'LOG','quantity':'0'},
            'outcome':{'metric_id':'M','population_definition':'COHORT','measurement_method':'LOG','guardrail_threshold_receipt':'SYNTHETIC','value':'0','denominator':'5'}}
        for kind,extra in fields.items():
            d=fixture(); d['records'][0].update(record_type=kind,**extra)
            self.assertEqual(model.validate(d),[],kind)
    def test_outcome_denominator_must_be_positive_finite(self):
        for value in ('0','-1','NaN','Infinity',None,1.0):
            d=fixture(); d['records'][0].update(record_type='outcome',metric_id='M',
                population_definition='COHORT',measurement_method='LOG',
                guardrail_threshold_receipt='SYNTHETIC',value='0',denominator=value)
            self.assertTrue(model.validate(d),repr(value))
    def test_numerical_observations_reject_negative_and_nonfinite(self):
        for value in ('-1','NaN','Infinity','1e3',True):
            d=fixture(); d['records'][0]['amount']=value
            self.assertTrue(model.validate(d),repr(value))

if __name__=='__main__': unittest.main()
