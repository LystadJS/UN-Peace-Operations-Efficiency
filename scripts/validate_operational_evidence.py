#!/usr/bin/env python3
"""E08 versioned intake validation; source declarations are not authentication."""
import argparse
import datetime as dt
import json
import re
from decimal import Decimal

VERSION='E08-1.0'
KINDS={'transaction','asset','post','workload','outcome'}
EVENTS={'CLAIM','PAYMENT','CASH_RECEIPT','REVERSAL'}
SCOPE=('case_id','cost_object_id','fund','currency','unit','period_start','period_end','payer_entity','provider_entity')

def present(value):
    return isinstance(value,str) and bool(value.strip())

def decimal(value):
    if not isinstance(value,str) or not re.fullmatch(r'\d+(?:\.\d+)?',value) or len(value)>100:
        raise ValueError('nonnegative finite decimal string required')
    return Decimal(value)

def date(value):
    if not isinstance(value,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):
        raise ValueError('ISO date required')
    return dt.date.fromisoformat(value)

def validate(data):
    errors=[]
    if not isinstance(data,dict) or data.get('schema_version') != VERSION:
        return ['schema_version must be '+VERSION]
    if data.get('evidence_mode') not in ('SYNTHETIC','PUBLIC_RESEARCH','RESTRICTED_APPROVED'):
        errors.append('explicit evidence_mode required')
    rows=data.get('records')
    if not isinstance(rows,list) or not rows or len(rows)>10000:
        return errors+['records must contain1 through10000 objects']
    ids=set()
    economic_events=set()
    for i,row in enumerate(rows):
        label=f'records[{i}]'
        if not isinstance(row,dict):
            errors.append(label+':object required'); continue
        for key in ('record_id','case_id','source_receipt','source_locator','entity_id','period_start','period_end'):
            if not present(row.get(key)): errors.append(label+':missing '+key)
        ident=row.get('record_id')
        if present(ident):
            if ident in ids: errors.append(label+':duplicate record_id')
            ids.add(ident)
        try:
            if date(row.get('period_start'))>date(row.get('period_end')): raise ValueError()
        except (ValueError,TypeError): errors.append(label+':invalid period')
        kind=row.get('record_type')
        if kind not in KINDS: errors.append(label+':unknown record_type'); continue
        fields={'transaction':list(SCOPE)+['event_type','event_date','economic_event_id'],
            'asset':['asset_id','movement_id','movement_type','custodian_from','custodian_to','condition','event_date'],
            'post':['post_id','action','effective_date','fund','work_transfer_receipt'],
            'workload':['activity_id','output_id','worker_token','unit','measurement_method'],
            'outcome':['metric_id','unit','population_definition','measurement_method','guardrail_threshold_receipt']}[kind]
        for key in fields:
            if not present(row.get(key)): errors.append(label+':missing '+key)
        amountfield={'transaction':'amount','asset':'quantity','post':'fte','workload':'quantity','outcome':'value'}[kind]
        try:
            amount=decimal(row.get(amountfield))
            if kind=='asset' and amount<=0: errors.append(label+':asset quantity must be positive')
        except ValueError: errors.append(label+':invalid '+amountfield)
        for field in ('event_date','effective_date'):
            if field in fields:
                try: date(row.get(field))
                except (ValueError,TypeError): errors.append(label+':invalid '+field)
        if kind=='transaction':
            economic_id=row.get('economic_event_id')
            if present(economic_id):
                if economic_id in economic_events: errors.append(label+':duplicate economic event; canonicalize counterpart postings')
                economic_events.add(economic_id)
            if row.get('event_type') not in EVENTS: errors.append(label+':invalid transaction event')
            if not isinstance(row.get('currency'),str) or not re.fullmatch('[A-Z]{3}',row['currency']): errors.append(label+':invalid currency')
            if row.get('unit')!='currency_units': errors.append(label+':amount unit must be currency_units')
            if row.get('payer_entity')==row.get('provider_entity'): errors.append(label+':distinct counterparties required')
            if row.get('event_type')=='REVERSAL' and not present(row.get('reversal_of')): errors.append(label+':reversal target required')
            if row.get('event_type')!='REVERSAL' and row.get('reversal_of') is not None: errors.append(label+':unexpected reversal target')
        if kind=='asset' and row.get('movement_type') not in ('RELEASE','RECEIPT','DISPOSAL'):
            errors.append(label+':invalid movement type')
        if kind=='post' and row.get('action') not in ('ESTABLISH','ABOLISH','REDEPLOY','VACANT','OCCUPIED'):
            errors.append(label+':invalid post action')
        if kind=='outcome':
            try:
                if decimal(row.get('denominator'))<=0: raise ValueError()
            except ValueError: errors.append(label+':explicit denominator required')
    return errors

def receipt(data):
    issues=validate(data)
    return {'schema_version':VERSION,'status':'INVALID' if issues else 'STRUCTURALLY_VALID_NOT_AUTHENTICATED',
        'issues':issues,'candidate_advanced':False,'savings_amount':None}

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('input'); args=parser.parse_args()
    with open(args.input,encoding='utf-8') as stream: result=receipt(json.load(stream))
    print(json.dumps(result,indent=2)); raise SystemExit(bool(result['issues']))
