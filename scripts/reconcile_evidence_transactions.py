#!/usr/bin/env python3
"""E09 explicit many-to-many allocations; never guess subsets or recognize benefits."""
import argparse
import json
from decimal import Decimal, localcontext
from validate_operational_evidence import validate, decimal, date, SCOPE

VERSION='E09-1.0'

def reconcile(data):
    issues=validate(data)
    result={'schema_version':VERSION,'status':'INVALID','issues':issues,'balances':[],
        'unallocated_records':[],'timing_exceptions':[],'candidate_advanced':False,'savings_amount':None}
    if issues: return result
    rows=data['records']
    if any(r['record_type']!='transaction' for r in rows):
        issues.append('transaction records only'); return result
    allocation_input=data.get('allocations')
    if not isinstance(allocation_input,list):
        issues.append('explicit allocations list required; no inferred subset matching'); return result
    if data.get('reconciliation_version') != VERSION:
        issues.append('reconciliation_version must be '+VERSION); return result
    tolerance=data.get('timing_tolerance_days')
    if type(tolerance) is not int or tolerance<0 or tolerance>366:
        issues.append('timing_tolerance_days integer0 through366 required'); return result
    lookup={r['record_id']:r for r in rows}
    def same_scope(a,b): return all(a[k]==b[k] for k in SCOPE)
    with localcontext() as ctx:
        ctx.prec=512
        available={r['record_id']:decimal(r['amount']) for r in rows if r['event_type']!='REVERSAL'}
        reversal_ids={}
        for row in rows:
            if row['event_type']!='REVERSAL': continue
            target=lookup.get(row['reversal_of'])
            if target is None or target['event_type']=='REVERSAL' or not same_scope(row,target):
                issues.append(row['record_id']+':invalid or cross-perimeter reversal'); continue
            if date(row['event_date'])<date(target['event_date']):
                issues.append(row['record_id']+':reversal precedes target'); continue
            available[target['record_id']]-=decimal(row['amount'])
            reversal_ids.setdefault(target['record_id'],[]).append(row['record_id'])
            if available[target['record_id']]<0: issues.append(target['record_id']+':over-reversed')
        used={ident:Decimal(0) for ident in available}
        seen=set(); edges=set()
        for i,allocation in enumerate(allocation_input):
            label=f'allocations[{i}]'
            if not isinstance(allocation,dict): issues.append(label+':object required'); continue
            ident=allocation.get('allocation_id')
            if not isinstance(ident,str) or not ident.strip() or ident in seen:
                issues.append(label+':unique allocation_id required'); continue
            seen.add(ident)
            if not isinstance(allocation.get('claim_id'),str) or not isinstance(allocation.get('settlement_id'),str):
                issues.append(label+':string record references required'); continue
            claim=lookup.get(allocation.get('claim_id')); settlement=lookup.get(allocation.get('settlement_id'))
            if claim is None or settlement is None or claim['event_type']!='CLAIM' or settlement['event_type'] not in ('PAYMENT','CASH_RECEIPT'):
                issues.append(label+':claim and payment/cash-receipt references required'); continue
            if not same_scope(claim,settlement): issues.append(label+':cross-perimeter allocation'); continue
            edge=(claim['record_id'],settlement['record_id'])
            if edge in edges: issues.append(label+':duplicate allocation edge'); continue
            edges.add(edge)
            if not isinstance(allocation.get('source_receipt'),str) or not allocation['source_receipt'].strip():
                issues.append(label+':allocation evidence required'); continue
            try:
                amount=decimal(allocation.get('amount'))
                if amount<=0: raise ValueError()
            except ValueError: issues.append(label+':positive decimal allocation required'); continue
            used[claim['record_id']]+=amount; used[settlement['record_id']]+=amount
            gap=(date(settlement['event_date'])-date(claim['event_date'])).days
            if gap<0 or gap>tolerance:
                result['timing_exceptions'].append({'allocation_id':ident,'days':gap,'status':'REVIEW_REQUIRED'})
                issues.append(label+':timing outside declared tolerance')
        for ident,amount in available.items():
            if used[ident]>amount: issues.append(ident+':overallocated/overpayment or reversed settlement')
            remaining=amount-used[ident]
            if remaining!=0: result['unallocated_records'].append(ident)
            result['balances'].append({'record_id':ident,'event_type':lookup[ident]['event_type'],
                'available':format(amount,'f'),'allocated':format(used[ident],'f'),'remaining':format(remaining,'f'),
                'reversal_ids':reversal_ids.get(ident,[]),
                'interpretation':'CASH_RECEIPT_DECLARED_NOT_AUTHENTICATED' if lookup[ident]['event_type']=='CASH_RECEIPT' else 'NOT_CASH_RECEIPT_PROOF'})
        if result['unallocated_records']: issues.append('unmatched or partially settled records remain')
    result['status']='EXCEPTIONS_REQUIRE_REVIEW' if issues else 'RECONCILED_DECLARED_RECORDS_NOT_BENEFIT'
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('input'); args=parser.parse_args()
    with open(args.input,encoding='utf-8') as stream: result=reconcile(json.load(stream))
    print(json.dumps(result,indent=2)); raise SystemExit(bool(result['issues']))
