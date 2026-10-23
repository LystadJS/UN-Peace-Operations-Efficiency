#!/usr/bin/env python3
"""E10 safe P11 wrapper: unvalidated full-cost scenario difference only."""
import argparse
import json
from evaluate_intervention import evaluate

VERSION='E10-1.0'

def calculate(data):
    if not isinstance(data,dict) or data.get('calculator_version')!=VERSION:
        return {'schema_version':VERSION,'status':'NOT_COMPUTABLE','issues':['calculator_version must be '+VERSION],
            'net_cost_difference':None,'savings_amount':None,'candidate_advanced':False}
    evaluated=evaluate(data)
    comparison=evaluated['cost_comparison']
    result={'schema_version':VERSION,'status':comparison['status'],'cost_comparison':comparison,
        'net_cost_difference':comparison['net_cost_difference'],'guardrails':evaluated['guardrails'],
        'benefit_classes':evaluated['benefits'],'candidate_advanced':False,'savings_amount':None,
        'recognition':'WITHHELD: declared full-cost difference is neither attributed benefit nor cashable/realized saving',
        'limitations':evaluated['limitations']}
    if evaluated['guardrails']['status']!='DECLARED_PASS_NOT_AUTHENTICATED':
        result['status']='WITHHELD_GUARDRAILS'
        result['net_cost_difference']=None
        result['cost_comparison']={**comparison,'status':'WITHHELD_GUARDRAILS','net_cost_difference':None}
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('input'); args=parser.parse_args()
    with open(args.input,encoding='utf-8') as stream: result=calculate(json.load(stream))
    print(json.dumps(result,indent=2)); raise SystemExit(result['status']!='CALCULATED_UNVALIDATED')
