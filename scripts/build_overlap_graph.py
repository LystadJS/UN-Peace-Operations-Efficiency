#!/usr/bin/env python3
"""I03 preserve analytical pool hyperedges without claiming actual duplicate cost."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INPUTS=('data/portfolio/interventions.json','data/portfolio/benefit_pools.json')

def build(root=ROOT):
    source={p:json.loads((root/p).read_text(encoding='utf-8')) for p in INPUTS}
    register=source[INPUTS[0]]; pools=source[INPUTS[1]]
    if pools.get('source_register_id')!=register.get('register_id'):
        raise ValueError('pool/register identity mismatch')
    rows=register['interventions']
    ids=[r['intervention_id'] for r in rows]
    if len(set(ids))!=len(ids): raise ValueError('duplicate intervention ID')
    nodes=[]
    for row in rows:
        aliases=[{'namespace':'ROADMAP_CASE','value':row['roadmap_case_id']}]
        aliases += [{'namespace':'LEGACY_CANDIDATE','value':r['value'],'source_path':r['path']}
            for r in row['source_refs'] if r['path']=='data/candidate_validation.csv']
        nodes.append({'node_id':row['intervention_id'],'namespace':'NORMALIZED_INTERVENTION',
            'title':row['title'],'aliases':aliases,'source_refs':row['source_refs'],
            'candidate_state':row['candidate_state'],'verified_benefit':None})
    edges=[]; pair_pools={}; seen=set()
    for pool in pools['pools']:
        key=pool['pool_id']; members=pool['intervention_ids']
        if key in seen or len(set(members))!=len(members): raise ValueError('duplicate pool/member')
        seen.add(key)
        if not members or any(m not in ids for m in members): raise ValueError('unknown/empty pool membership')
        expected=sorted(r['intervention_id'] for r in rows if key in r['benefit_pool_ids'])
        if sorted(members)!=expected: raise ValueError('asymmetric pool membership')
        edges.append({'hyperedge_id':'POOL:'+key,'pool_id':key,'member_node_ids':sorted(members),
            'boundary':pool['boundary'],'relationship':pool['relationship'],
            'evidence_class':'POTENTIAL_OVERLAP_REQUIRES_COST_OBJECT_RECONCILIATION',
            'actual_duplicate_cost_proven':False,'verified_benefit':None,
            'recognition_rule':pool['recognition_rule'],'mutual_exclusion_rule':pool['mutual_exclusion_rule']})
        for pair in itertools.combinations(sorted(members),2): pair_pools.setdefault(pair,[]).append(key)
    if any(p not in seen for r in rows for p in r['benefit_pool_ids']): raise ValueError('unresolved pool')
    return {'schema_version':'1.0','graph_id':'I03-OVERLAP-1.0',
        'graph_semantics':'Pool co-membership is potential overlap, not demonstrated duplication or removable cost.',
        'producer':'scripts/build_overlap_graph.py',
        'source_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in INPUTS},
        'producer_sha256':hashlib.sha256((root/'scripts/build_overlap_graph.py').read_bytes()).hexdigest(),
        'nodes':nodes,'hyperedges':edges,
        'pair_projection':[{'node_ids':list(pair),'pool_ids':sorted(keys),
            'interpretation':'DERIVED_CO_MEMBERSHIP_NOT_INDEPENDENT_EVIDENCE'} for pair,keys in sorted(pair_pools.items())],
        'aggregation_allowed':False,'verified_benefit_total':None,
        'limitations':['Singleton pools are preserved, not discarded as isolated edges.',
            'Pair projection does not replace the original pool hyperedges.',
            'Roadmap C aliases and legacy C candidate aliases are separate namespaces; join only explicit source references.',
            'No workload, cost-object, authority or financial adjudication is supplied by this graph.']}

def outputs(root=ROOT):
    return {'data/portfolio/overlap_graph.json':json.dumps(build(root),indent=2,ensure_ascii=False)+'\n'}

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--write',action='store_true'); parser.add_argument('--check',action='store_true'); args=parser.parse_args()
    for path,value in outputs().items():
        if args.write: (ROOT/path).write_text(value,encoding='utf-8')
        elif not (ROOT/path).exists() or (ROOT/path).read_text(encoding='utf-8')!=value: raise SystemExit('STALE:'+path)
    print('PASS:pool hyperedges, explicit namespace aliases and nonadditivity controls')
