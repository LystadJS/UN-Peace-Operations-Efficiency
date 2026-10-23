#!/usr/bin/env python3
"""Normalize retained research rows and bounded case scopes without pricing benefits."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    'candidates': ('data/candidate_validation.csv', 'candidate_id'),
    'hierarchy': ('data/consolidation_comprehensive_2027.csv', 'hierarchy_id'),
    'opportunities': ('data/public_opportunity_register.csv', 'opportunity_id'),
    'transactions': ('data/transaction_validation_cases.csv', 'case_id'),
    'arrangements': ('data/un80_register.csv', 'reform_id'),
}
# Case IDs correspond to roadmap C01–C14, not legacy candidate C01–C19.
CASES = [
 ('CASE01','RSCE client charging, retained local work and workforce',['C16'],['P003','P006'],['RSCE'],[],['RSCE_COST_BASE','HQ_SHARED_SUPPORT']),
 ('CASE02','UNIFIL–UNSCOL asset transfer and avoided procurement',['C12','C07'],['P001'],['UNIFIL_UNSCOL'],[],['LEBANON_TRANSITION']),
 ('CASE03','BINUH–UNSOH aviation and broader support',['C07'],['P002'],['BINUH_UNSOH'],[],['HAITI_SUPPORT']),
 ('CASE04','UNISFA translation routing',['C19'],['P004'],[],[],['UNISFA_LANGUAGE']),
 ('CASE05','UNISFA stewardship of transferred MINUSMA assets',['C19'],['P005'],[],[],['UNISFA_ASSETS']),
 ('CASE06','UNSOS contractor fuel loss recovery',['C08'],['P007'],[],[],['UNSOS_RECOVERY']),
 ('CASE07','MONUSCO medical-insurance integrity',['C07'],['P008'],[],[],['MONUSCO_CLAIMS']),
 ('CASE08','UNMISS approved post removals and output continuity',['C15'],['P009'],[],[],['UNMISS_POST_BASELINE']),
 ('CASE09','Training administration and procurement',['C04'],['P014'],[],['U05'],['TRAINING_DELIVERY','HQ_SHARED_SUPPORT']),
 ('CASE10','DPPA–DPO regional political-operational functions',['C01'],['P013'],[],['U01'],['REGIONAL_WORKFLOW','HQ_SHARED_SUPPORT']),
 ('CASE11','UNOWAS–UNOCA factual support production',['C09','C02'],['P011'],[],[],['REGIONAL_WORKFLOW','REPORT_PRODUCTION']),
 ('CASE12','Cyprus factual support production',['C02'],[],[],[],['REPORT_PRODUCTION']),
 ('CASE13','UNIFIL transition residual costs and liabilities',['C12','C07'],['P001'],[],[],['LEBANON_TRANSITION']),
 ('CASE14','Existing joint structures and retained work',['C16','C03','C18'],['P010'],[],['U02','U03','U09','U10'],['HQ_SHARED_SUPPORT','REGIONAL_WORKFLOW','TRAINING_DELIVERY']),
]
POOLS = {
 'RSCE_COST_BASE': 'RSCE external service costs and matching internal charge pairs; internal AP/AR eliminates once',
 'HQ_SHARED_SUPPORT': 'Shared HQ posts, chargebacks and administration potentially claimed by several interventions',
 'LEBANON_TRANSITION': 'UNIFIL–UNSCOL asset acquisition alternatives, transfer costs and retained transition liabilities',
 'HAITI_SUPPORT': 'BINUH–UNSOH aviation and nonaviation services; broader reimbursement contains subsets',
 'UNISFA_LANGUAGE': 'Identified translation service events, contracts and retained observer coverage',
 'UNISFA_ASSETS': 'Tagged transferred assets, procurement alternatives, maintenance and disposal costs',
 'UNSOS_RECOVERY': 'Contractor fuel claim principal, receipts, enforcement costs and reversals',
 'MONUSCO_CLAIMS': 'Medical claim integrity, lawful recoveries and retained medical service costs',
 'UNMISS_POST_BASELINE': 'Unique approved abolished posts, payroll effects, replacement work and transition liabilities',
 'TRAINING_DELIVERY': 'Course/cohort specific contracts, trainers, attendance, administration and qualifications',
 'REGIONAL_WORKFLOW': 'Joint regional task, product and staff-time cost objects; overlap requires record reconciliation',
 'REPORT_PRODUCTION': 'Source preparation events and staff time reused across distinct mandated final outputs',
}

def load_sources(root):
    tables, receipts = {}, {}
    for label, (path, key) in SOURCES.items():
        raw = (root / path).read_bytes()
        rows = list(csv.DictReader(raw.decode('utf-8').splitlines()))
        if len({r[key] for r in rows}) != len(rows):
            raise ValueError(f'duplicate source IDs: {path}')
        tables[label] = rows
        receipts[label] = {'path': path, 'key': key, 'sha256': hashlib.sha256(raw).hexdigest(), 'row_count': len(rows)}
    return tables, receipts

def build_interventions(root=ROOT):
    tables, receipts = load_sources(root)
    hierarchy = tables['hierarchy']
    if sum(r['level'] == 'umbrella' for r in hierarchy) != 14 or len(hierarchy) != 23:
        raise ValueError('expected retained 14 umbrella and 9 overlapping child rows')
    cases = []
    for ident, title, candidates, opportunities, transactions, arrangements, pools in CASES:
        refs = []
        for label, ids in [('candidates', candidates), ('opportunities', opportunities), ('transactions', transactions), ('arrangements', arrangements)]:
            path, key = SOURCES[label]
            for source_id in ids:
                if not any(r[key] == source_id for r in tables[label]):
                    raise ValueError(f'missing source: {label}/{source_id}')
                refs.append({'path': path, 'key': key, 'value': source_id})
        if ident == 'CASE11':
            refs.append({'path': 'data/census_v8/pilot_summary.json', 'key': None, 'value': None})
        if ident == 'CASE12':
            refs.append({'path': 'data/census_v9/pilot_summary.json', 'key': None, 'value': None})
        for ref in refs:
            if not (root / ref['path']).is_file():
                raise ValueError(f'missing case source: {ref["path"]}')
        cases.append({'intervention_id': ident, 'roadmap_case_id': 'C'+ident[-2:], 'title': title,
            'candidate_state': 'SCREENING_CANDIDATE', 'state_history': [], 'financial_validation': 'NOT_PERFORMED',
            'benefit_amount': None, 'benefit_status': 'NOT_ESTIMATED', 'cost_objects': [],
            'cost_object_identification': 'REQUIRES_UNIQUE_RECORDS', 'benefit_pool_ids': pools,
            'source_refs': refs, 'institutional_authorization': 'NOT_ESTABLISHED_BY_REPOSITORY',
            'next_gate': 'Define comparison and obtain authenticated workload, full-system costs, authority and service safeguards'})
    return {'schema_version': '1.0', 'register_id': 'P06-INTERVENTIONS-1.0', 'evidence_cutoff': '2026-10-23',
        'scope': 'Normalized retained source populations plus14 roadmap case scopes; populations overlap and are not additive',
        'source_receipts': receipts, 'legacy_populations': tables, 'interventions': cases,
        'source_population_counts': {'legacy_candidates': len(tables['candidates']), 'umbrella_rows':14, 'mission_child_rows':9,
            'public_opportunities':len(tables['opportunities']), 'roadmap_cases':14},
        'aggregation_allowed': False, 'portfolio_benefit_total': None,
        'limitations': ['Legacy C identifiers, roadmap C identifiers and CASE identifiers are separate namespaces.',
            'Historical rank/exposure is preserved as a source snapshot, never promoted to benefit.',
            'Cases split and cross-link legacy candidates; counts across populations must not be added.',
            'No internal records, approvals or validated cost objects have been supplied.']}

def build_pools(interventions):
    pools = []
    for key, boundary in POOLS.items():
        members = [r['intervention_id'] for r in interventions['interventions'] if key in r['benefit_pool_ids']]
        pools.append({'pool_id':key, 'boundary':boundary, 'intervention_ids':members,
            'relationship':'POTENTIAL_SHARED_COST_OBJECTS_NOT_PROVEN_IDENTICAL', 'cost_objects':[],
            'verified_benefit':None, 'aggregation_allowed':False,
            'recognition_rule':'Assign a unique cost-object/period/counterfactual/benefit-category key; one recognized allocation across all cases, with sum of allocation shares at most1',
            'mutual_exclusion_rule':'Alternative interventions on the same cost-object and period are mutually exclusive unless independently separable marginal effects are evidenced'})
    return {'schema_version':'1.0','register_id':'P07-BENEFIT-POOLS-1.0','source_register_id':interventions['register_id'],
        'pools':pools,'allocation_ledger':[], 'portfolio_benefit_total':None,
        'rules':['Internal UN charges and corresponding credits eliminate once; measure underlying external resource use.',
            'Parent exposures, child scopes and overlapping cases are never summed.',
            'Already embedded reforms, approved post removals and closures belong in the counterfactual.',
            'Recovery, cost avoidance, capacity gain, cashable saving and realized saving remain separate categories.',
            'Pre-financial-validation monetary context cannot be recognized as a saving.',
            'CASE02 asset effects and CASE13 residual costs require one shared Lebanon full-cost bridge.']}

def validate(interventions, pools=None):
    rows = interventions['interventions']
    ids = [r['intervention_id'] for r in rows]
    if len(ids) !=14 or len(set(ids)) !=14:
        raise ValueError('14 unique case IDs required')
    if interventions['portfolio_benefit_total'] is not None or interventions['aggregation_allowed']:
        raise ValueError('screening portfolio cannot assert benefit totals')
    for r in rows:
        if r['candidate_state'] != 'SCREENING_CANDIDATE' or r['financial_validation'] != 'NOT_PERFORMED' or r['benefit_amount'] is not None:
            raise ValueError('unsupported candidate or financial advancement')
        if r['cost_objects']:
            raise ValueError('initial baseline has no authenticated cost objects')
    if pools is not None:
        indexed = {p['pool_id']:p for p in pools['pools']}
        if len(indexed) !=len(pools['pools']):
            raise ValueError('duplicate pool ID')
        for r in rows:
            for p in r['benefit_pool_ids']:
                if p not in indexed or r['intervention_id'] not in indexed[p]['intervention_ids']:
                    raise ValueError('broken pool membership')
        for p in indexed.values():
            expected = sorted(r['intervention_id'] for r in rows if p['pool_id'] in r['benefit_pool_ids'])
            if sorted(p['intervention_ids']) !=expected or p['verified_benefit'] is not None or p['aggregation_allowed']:
                raise ValueError('invalid pool scope or recognition')
        if pools['allocation_ledger'] or pools['portfolio_benefit_total'] is not None:
            raise ValueError('baseline cannot book allocations or total')

def outputs(root=ROOT):
    interventions = build_interventions(root)
    pools = build_pools(interventions)
    validate(interventions, pools)
    return {'data/portfolio/interventions.json':json.dumps(interventions,indent=2,ensure_ascii=False)+'\n',
        'data/portfolio/benefit_pools.json':json.dumps(pools,indent=2,ensure_ascii=False)+'\n'}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--write',action='store_true')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    for path, content in outputs().items():
        if args.write:
            (ROOT/path).parent.mkdir(parents=True,exist_ok=True)
            (ROOT/path).write_text(content,encoding='utf-8')
        elif not (ROOT/path).is_file() or (ROOT/path).read_text(encoding='utf-8') != content:
            raise SystemExit(f'STALE: {path}')
    print('PASS:14 screening cases,14 parent/9 child source rows,12 nonadditive pools')

if __name__ == '__main__':
    main()
