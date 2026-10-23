#!/usr/bin/env python3
"""Publish the bounded C01–C03 evidence update without rewriting historical cases."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY_HASHES = {
 'C01':'2d0e8dd92b32e7edb7739d87397759398558725859e2a254bef567a1165006f5',
 'C02':'bfe813d34528ee716d62603dafe06331187506a314bf4545d535e3ed8785768e',
 'C03':'85cc95fd2661f575f843aec266a9a760d4326932925069893197067fe088d6ef'}
INPUTS = [f'data/priority_cases/C{i:02}_{kind}.json' for i in range(1,4)
          for kind in ('public_evidence','request_addendum','source_review')]
INPUTS += ['data/priority_cases/dataset_semantic_review.json',
 'data/priority_cases/lineage_review.json', 'data/priority_cases/evidence_access_readiness.json',
 'data/priority_cases/entity_authority_crosswalk.json', 'data/priority_cases/advancement_review.json',
 'data/priority_cases/C01_historical_audit.json', 'data/priority_cases/C02_UF01_research_scope.json',
 'data/priority_cases/C02_UF01_readiness_review.json', 'data/priority_cases/research_candidates.json',
 'data/priority_cases/research_candidates_initial.json',
 'data/pilots/request_status.json', 'data/adjudications/execution_gates.json',
 'data/portfolio/verified_benefit_ledger.json', 'data/standards/candidate_states.json']

def require(ok, message):
    if not ok: raise ValueError(message)

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(root,path): return json.loads((root/path).read_text())

def explicit_bindings(value):
    """Yield only explicit local path/hash pairs; remote document hashes stay distinct."""
    if isinstance(value, dict):
        for key, digest in value.items():
            if key == 'source_sha256' and isinstance(digest, dict):
                yield from digest.items()
            elif key == 'sha256' and digest is not None and 'path' in value:
                yield value['path'], digest
            elif key == 'source_sha256' and isinstance(digest, str) and 'path' in value:
                yield value['path'], digest
            elif key.endswith('_sha256') and isinstance(digest, str):
                stem = key[:-7]
                path = value.get(stem + '_path', value.get(stem))
                if isinstance(path, str) and path.startswith(('data/', 'docs/')):
                    yield path, digest
        for item in value.values():
            yield from explicit_bindings(item)
    elif isinstance(value, list):
        for item in value:
            yield from explicit_bindings(item)


def validate_detail_facts(requests, execution):
    require(requests['counts']['draft_contracts'] == len(requests['requests']) and
            requests['counts']['case_tracks'] == len(requests['case_tracks']),
            'Request population/count disagreement')
    for row in requests['requests']:
        require(row['dispatch_status'] == 'NOT_SENT' and row['response_status'] == 'NOT_OBTAINED'
                and row['collection_status'] == 'NOT_AUTHORIZED' and row['accepted_owner'] is None,
                'Request detail contradicts zero access facts')
        require(all(row[k] is None for k in ('dispatch_receipt', 'requested_at', 'received_at')) and
                row['response_receipts'] == [] and row['access_approval_receipts'] == [],
                'Request evidence contradicts zero access facts')
    for row in requests['case_tracks']:
        require(row['dispatch_status'] == 'NOT_SENT' and row['response_status'] == 'NOT_OBTAINED'
                and row['approved_collection'] is False, 'Case-track detail contradicts zero access facts')
    for row in execution['records']:
        require(row['execution_status'] == 'BLOCKED_NOT_EXECUTED' and
                all(row[k] is False for k in ('substantive_audit_completed', 'evidence_received',
                                              'execution_authorized')) and
                row['accountable_owner'] is None and row['financial_finding'] is None,
                'Execution detail contradicts blocked operational facts')


def build(root=ROOT):
    missing=[p for p in INPUTS if not (root/p).is_file()]
    require(not missing, 'Missing priority inputs: '+', '.join(missing))
    data={p:read(root,p) for p in INPUTS}
    for value in data.values():
        for path, digest in explicit_bindings(value):
            target = root/path
            require(target.is_file() and sha(target) == digest, 'Stale explicit source binding: '+path)
    for i in range(1,4):
        case=f'C{i:02}'
        packet=f'data/priority_cases/{case}_public_evidence.json'
        reviewed=data[f'data/priority_cases/{case}_source_review.json']
        if case=='C03':
            require(reviewed['reviewed_artifact']['path']==packet and
                    reviewed['reviewed_artifact']['sha256']==sha(root/packet), 'Source review hash mismatch: '+case)
        else:
            require(reviewed['reviewed_packet']==packet and
                    reviewed['reviewed_packet_sha256']==sha(root/packet), 'Source review hash mismatch: '+case)
    first_addendum=data['data/priority_cases/C01_request_addendum.json']
    require(first_addendum['public_evidence']['sha256']==sha(root/'data/priority_cases/C01_public_evidence.json'),
            'RSCE request bound to stale public evidence')
    haiti_addendum=data['data/priority_cases/C03_request_addendum.json']
    require(haiti_addendum['source_packet_sha256']==sha(root/'data/priority_cases/C03_public_evidence.json'),
            'Haiti request bound to stale public evidence')
    for case, expected in LEGACY_HASHES.items():
        path=f'data/cases/{case}.json'
        require(sha(root/path)==expected, 'Historical case bytes changed: '+case)
        parent=read(root,path)
        require(parent['candidate_state']=='SCREENING_CANDIDATE' and parent['operational_baseline'] is None,
                'Historical baseline changed; substantive release review required')
        require(parent['accountable_owner'] is None and parent['financial_validation']=='NOT_PERFORMED',
                'Actual owner or financial evidence changed; review required')
    requests=data['data/pilots/request_status.json']
    require(all(requests['counts'][k]==0 for k in ('requests_sent','responses_obtained','accepted_owners','approved_collections')),
            'Access facts changed; review required')
    require(data['data/adjudications/execution_gates.json']['actual_operational_audits_completed']==0,
            'Operational adjudication facts changed; review required')
    validate_detail_facts(requests, data['data/adjudications/execution_gates.json'])
    ledger=data['data/portfolio/verified_benefit_ledger.json']
    require(ledger['entries']==[] and ledger['reconciliation']['headline_realized_savings_usd'] is None,
            'Benefit recognition changed; review required')
    candidates=data['data/priority_cases/research_candidates.json']
    import validate_candidate_advancement as advancement
    # The same F03 validator used for portfolio governance validates child histories.
    require(advancement.validate_records(candidates, data['data/standards/candidate_states.json'],
            data['data/priority_cases/research_candidates_initial.json'])==1,
            'Expected one structurally valid research candidate history')
    rows=candidates['candidates']
    require(len(rows)==1 and rows[0]['candidate_id']=='C02-UF01-RESEARCH', 'Unexpected research-unit population')
    require(rows[0]['current_state'] in ('SCREENING_CANDIDATE','VALIDATION_READY') and
            rows[0]['claim_class']=='NO_FINANCIAL_CLAIM' and rows[0]['savings_amount'] is None,
            'Research readiness cannot assert operational validation or a monetary benefit')
    review=data['data/priority_cases/C02_UF01_readiness_review.json']
    require(review['scope_path']=='data/priority_cases/C02_UF01_research_scope.json' and
            review['scope_sha256']==sha(root/review['scope_path']), 'Readiness review scope hash mismatch')
    require(review['recommended_state']==rows[0]['current_state'], 'Research-state/review disagreement')
    if rows[0]['current_state'] == 'VALIDATION_READY':
        required = set(data['data/standards/candidate_states.json']['states']['VALIDATION_READY']['requires'])
        require(len(required) == 7 and set(review['checks']) == required and
                review['all_seven_required_checks_pass'] is True and
                all(check['status'] == 'PASS' for check in review['checks'].values()),
                'Research readiness requires all seven exact independent checks to pass')
    semantics=data['data/priority_cases/dataset_semantic_review.json']
    lineage=data['data/priority_cases/lineage_review.json']
    return {
      'schema_version':1, 'update_id':'PRIORITY-C01-C03-2026-10-23', 'as_of':'2026-10-23',
      'scope':'Targeted public evidence, research design and selected data/lineage work; historical portfolio preserved.',
      'historical_parent_states':{c:'SCREENING_CANDIDATE' for c in LEGACY_HASHES},
      'historical_parent_sha256':LEGACY_HASHES,
      'child_research_units':[{'candidate_id':r['candidate_id'],'version':r['version'],
         'current_state':r['current_state'],'claim_class':r['claim_class']} for r in rows],
      'public_source_receipt_counts':{f'C{i:02}':len(data[f'data/priority_cases/C{i:02}_public_evidence.json'].get('source_records',
         data[f'data/priority_cases/C{i:02}_public_evidence.json'].get('sources',[]))) for i in range(1,4)},
      'selected_semantic_datasets':len(semantics['datasets']),
      'selected_lineage_expressions':lineage['selected_expression_count'],
      'selected_lineage_dispositions':lineage['selected_status_counts'],
      'global_frozen_audit_counts_changed':False,
      'operational_access_case_selection':'UNDETERMINED_PENDING_CONFIRMED_ACCESS',
      'actual_operational_audits_completed':0,'financial_adjudications_completed':0,
      'requests_sent':0,'accepted_accountable_owners':0,'approved_collections':0,
      'benefits':'NOT_ESTIMATED','institutional_implementation_authorized':False,
      'source_sha256':{p:sha(root/p) for p in sorted(INPUTS)},
      'limitations':['Public reporting and source authentication do not establish actual performance, transfer or net financial effect.',
        'Selected authority review does not complete the global GA80/GA81 instrument population.',
        'F03 research readiness is distinct from evidence access, owner acceptance and operational activation.',
        'Historical OIOS information is not a finding of present waste or proof of recommendation closure.',
        'Original 324-dataset, 94-identity and 196-expression populations remain frozen; supplements have their own scopes.']}

def render(d):
    child=d['child_research_units'][0]
    return f'''# Priority-case evidence progress

**23 October 2026 — Public-source and bounded research work advanced; actual operational adjudications remain zero.**

The three historical parent dossiers remain unchanged screening records. The proposed UF01 six-vehicle cohort has a separately reviewed child research unit, **{child['candidate_id']}**, at **{child['current_state']}**. Research readiness supplies neither collection permission nor institutional implementation authority. [Research scope](priority_cases/C02_UF01_research_scope.md) · [Independent readiness review](priority_cases/C02_UF01_readiness_review.md).

| Priority | Public work resolved or narrowed | Next decisive evidence |
| --- | --- | --- |
| [C01 — RSCE](priority_cases/C01_public_evidence.md) | Final financing text and conditions reviewed; dated handover reports expose unresolved service/client timing differences. Historical audit information supplies a limited service-quality lead. | Client/service cutover bridge, mirrored predecessor/provider charges, retained work and complete service outcomes. |
| [C02 — UNIFIL–UNSCOL assets](priority_cases/C02_public_evidence.md) | Final transition safeguards and UNSCOL founding authority reviewed; generic transfer authority does not designate UNSCOL as recipient. | Specific recipient approval, serialized assets, continuing requirement, procurement disposition and full transfer/residual costs. |
| [C03 — Haiti support](priority_cases/C03_public_evidence.md) | Initial support and BINUH mandates reviewed; selected latest extension provisions have their own stated retrieval limits. Separate quantifiable support compacts are material evidence. | Signed case-specific compact, service acceptance and performance, GSF/BINUH allocation boundaries and matched full costs. |

[Five-entity authority overlay](priority_cases/entity_authority_crosswalk.md) · [Three source reviews](priority_cases/C01_source_review.md) · [C02 review](priority_cases/C02_source_review.md) · [C03 review](priority_cases/C03_source_review.md).

## Data and dependency work

The supplement reviews **{d['selected_semantic_datasets']} consequential datasets** and **{d['selected_lineage_expressions']} selected dynamic expressions**. Selected lineage dispositions are `{json.dumps(d['selected_lineage_dispositions'],sort_keys=True)}`. These are source-scoped supplements, not a subtraction from all original provisional profiles or dynamic gaps. [Semantic review](priority_cases/dataset_semantic_review.md) · [Lineage review](priority_cases/lineage_review.md).

## Immediate next decision

Use the [first-case activation package](priority_cases/first_case_activation.md) and the case-specific [RSCE](priority_cases/C01_request_addendum.md), [asset](priority_cases/C02_request_addendum.md) and [Haiti](priority_cases/C03_request_addendum.md) addenda to confirm whether a custodian can provide one complete decision-relevant slice under approved handling. No operational-access winner is established. Requests remain unsent, accepted owners and approved collections remain zero, and benefits remain unestimated.

The [advancement review](priority_cases/advancement_review.md) distinguishes unfinished research design from internal-access blockers. Complete public applicability and boundary checks where possible; actual baselines, operational guards and financial recognition require their own later gates. The [historical RSCE audit lead](priority_cases/C01_historical_audit.md) retains its older period and retrieval limits.

Input hashes and preserved parent digests are in [the machine-readable update](../data/priority_cases/progress.json). No operational trial, institutional decision or realized result is asserted by this update.
'''

def outputs(root=ROOT):
    d=build(root)
    return {'data/priority_cases/progress.json':json.dumps(d,indent=2,ensure_ascii=False)+'\n',
            'docs/priority_case_progress.md':render(d)}

def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--write',action='store_true');g.add_argument('--check',action='store_true');args=p.parse_args()
    for name,text in outputs().items():
        target=ROOT/name
        if args.write:target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text)
        elif not target.is_file() or target.read_text()!=text:raise SystemExit('Stale priority output: '+name)
    print('PASS: source-qualified priority progress; historical cases and operational gates preserved')

if __name__=='__main__':main()
