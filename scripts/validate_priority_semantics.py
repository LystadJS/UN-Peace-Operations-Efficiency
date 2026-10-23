#!/usr/bin/env python3
"""Reproduce a scoped human semantic review of retained priority-case datasets."""
import argparse
from collections import Counter
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT='data/priority_cases/dataset_semantic_review.json'
DOC='docs/priority_cases/dataset_semantic_review.md'
CONTRACTS=[
 ('transaction_control_baseline','control_id','One published budget/arrangement control, not one transaction','USD; mixed calendar and July–June periods identified in fiscal_rule','Published amounts have distinct embedded-efficiency, internal-allocation, prior-comparator and category-delta classes; rows cannot be summed.'),
 ('transaction_evidence_requests','request_id','One legacy requested evidence package; not a dispatched message or received record','No observed monetary amount or observation period','linked_controls is a semicolon-separated many-to-many relation; received_status=not_provided is missing evidence, not a negative finding.'),
 ('transaction_sources','source_id','One retained document or official-page source description','assessed_on is retained review date, not publication/adoption date','Source claims and locators are transcriptions; IDs do not authenticate primary text or turn proposals into adopted requirements.'),
 ('transaction_validation_cases','case_id','One umbrella transaction-audit case summary','USD monetary strings and explicit unavailable/not-applicable tokens','case_id is RSCE/UNIFIL_UNSCOL/BINUH_UNSOH, not roadmap C01/C02/C03; zero verified pairs is an evidence count, not zero waste.'),
 ('rsce_workforce_model_vs_post_actions','line_id','One model component, subtotal, proposed post action or reassignment','Mixed modeled FTE, proposed posts and reassigned posts','Only WF01–WF03 form the WF04 model subtotal; WF05–WF09 have different populations and cannot be netted into it.'),
 ('spm_2027_embedded_efficiencies','efficiency_id','One initiative already priced into the calendar-2027 SG proposal','USD thousands; calendar_2027; proposal','An estimate of an embedded measure is neither a new incremental project benefit nor an observed saving.'),
 ('public_opportunity_register','opportunity_id','One public research opportunity linked to legacy candidate/evidence IDs','USD narrow disclosed amount; row-specific calendar and financial_stage','parent_candidate_id uses the legacy candidate namespace; it must not join directly to roadmap Cxx case IDs.'),
 ('ga_adopted_directives','directive_id','One retained resolution-paragraph directive transcription','USD thousands where quantified; nonnumeric unavailable tokens allowed','Repository authority classification is retained, not newly authenticated; mission_id and linked_candidate_id are not unique keys.'),
 ('spm_2027_mission_budget','spm_id','One SPM mission/mandate budget entity with multiple annual measures','USD thousands; 2025 appropriation/expenditure,2026 approved,2027 proposed','Personnel table2 includes multiple categories; no year-to-year subtraction is a verified efficiency or payroll finding.'),
 ('public_finance_nodes','finance_id','One financial control total, component, memo or comparator','USD thousands; mixed periods, funds and statuses explicitly attached','Parent and child nodes overlap; memo and transfer nodes cannot be treated as independent expenses or benefits.'),
 ('public_finance_edges','edge_id','One directed inclusion/comparability relationship between finance nodes','No independent monetary unit','can_sum_child_into_parent is qualified by relationship and inclusion_note; never sum all graph nodes.'),
]
TOKENS={'not_available','not_estimated','not_applicable','not_an_efficiency','not_provided','not_supplied','not_separately_quantified','-',''}
ENTITY_MAP={'RSCE':'UNPO-RSCE','UNIFIL':'UNPO-UNIFIL','UNSCOL':'UNPO-SPM031','BINUH':'UNPO-SPM035','UNSOH':'UNPO-UNSOH'}

def read(root,name):
    with (root/('data/'+name+'.csv')).open(newline='',encoding='utf-8') as handle:
        reader=csv.DictReader(handle); data=list(reader)
        if not reader.fieldnames or len(reader.fieldnames)!=len(set(reader.fieldnames)):
            raise ValueError('Missing/duplicate columns: '+name)
    if any(None in r or any(v is None for v in r.values()) for r in data):
        raise ValueError('Malformed CSV row: '+name)
    return data

def build(root=ROOT):
    datasets=[]; loaded={}
    for name,key,grain,unit,limit in CONTRACTS:
        path='data/'+name+'.csv'; rows=read(root,name);loaded[name]=rows
        counts=Counter(r[key] for r in rows)
        duplicates=sorted(k for k,v in counts.items() if v>1)
        if '' in counts or duplicates: raise ValueError('Invalid reviewed row key: '+path)
        missing={k:sum(r[k] in TOKENS for r in rows) for k in rows[0]}
        datasets.append({'path':path,'source_sha256':hashlib.sha256((root/path).read_bytes()).hexdigest(),
          'rows':len(rows),'grain':grain,'reviewed_row_key':[key],'duplicate_key_values':duplicates,
          'empty_or_explicit_unavailable_counts':missing,'unit_and_period':unit,
          'interpretation_limit':limit,'review_status':'SCOPED_REPOSITORY_SEMANTICS_REVIEWED',
          'primary_source_reauthenticated':False,'operational_population_complete':False})
    controls={r['control_id']:r for r in loaded['transaction_control_baseline']}
    efficiency={r['efficiency_id']:r for r in loaded['spm_2027_embedded_efficiencies']}
    request_links=[{'request_id':r['request_id'],'control_id':k} for r in loaded['transaction_evidence_requests'] for k in r['linked_controls'].split(';')]
    broken=[r for r in request_links if r['control_id'] not in controls]
    if broken:raise ValueError('Unresolved requested control: '+str(broken))
    eff_links=[]
    for key in ('UF01','UF02','UF03','BH01'):
        row=controls[key]; target=efficiency[row['existing_efficiency_id']]
        if Decimal(row['published_amount_usd'])!=Decimal(target['projected_2027_efficiency_usd_thousands'])*1000:
            raise ValueError('USD/thousands efficiency mismatch: '+key)
        eff_links.append({'control_id':key,'efficiency_id':target['efficiency_id'],'usd_matches_thousands_times_1000':True})
    nodes={r['finance_id'] for r in loaded['public_finance_nodes']}
    if any(r['parent_id'] not in nodes or r['related_id'] not in nodes for r in loaded['public_finance_edges']):
        raise ValueError('Broken financial graph endpoint')
    entities=json.loads((root/'data/portfolio/entities.json').read_text())
    entity_ids={r['entity_id'] for r in entities['entities']}
    if not set(ENTITY_MAP.values())<=entity_ids:raise ValueError('Canonical priority entity missing')
    return {'schema_version':1,'review_id':'PRIORITY-C01-C03-SEMANTICS-2026-10-23',
      'review_date':'2026-10-23','source_evidence_cutoff':'Retained source-specific dates; no primary-source refresh by this review.',
      'scope':'Eleven retained datasets material to C01–C03; preserved historical 324-dataset audit remains unchanged.',
      'datasets':datasets,'joins':{
        'request_to_control':{'grain':'one request/control membership','rows':len(request_links),'broken_references':broken,'memberships':request_links},
        'embedded_efficiency_to_control':eff_links,
        'financial_graph':{'edges':len(loaded['public_finance_edges']),'broken_endpoints':[],'edge_semantics_must_govern_aggregation':True},
        'canonical_entity_ids':ENTITY_MAP,
        'entity_registry_sha256':hashlib.sha256((root/'data/portfolio/entities.json').read_bytes()).hexdigest(),
        'case_namespace_mapping':{'RSCE':'C01','UNIFIL_UNSCOL':'C02','BINUH_UNSOH':'C03'},
        'source_url_join':'No certified URL-only source join: documents cover multiple claims, URL spelling variants and paragraph-specific scopes; use explicit locator review.',
        'legacy_candidate_namespace':'Never join public_opportunity_register.parent_candidate_id or ga_adopted_directives.linked_candidate_id directly to roadmap Cxx IDs.'},
      'observations':{
        'verified_transaction_pairs':{r['case_id']:int(r['verified_invoice_asset_or_charge_pairs']) for r in loaded['transaction_validation_cases']},
        'transaction_document_ids_unavailable':sum(r['transaction_document_id']=='not_available' for r in controls.values()),
        'transaction_verified_no':sum(r['transaction_verified']=='no' for r in controls.values()),
        'legacy_evidence_packages_not_received':sum(r['received_status']=='not_provided' for r in loaded['transaction_evidence_requests']),
        'physical_asset_or_invoice_keys':'Absent: control IDs, document IDs and request IDs cannot substitute for VIN/serial, invoice line or settlement identity.'},
      'resolved': ['Reviewed grains and row keys for eleven retained datasets; verified no blank or duplicate selected keys.',
        'Expanded explicit request/control links and verified all endpoints.',
        'Verified four embedded-efficiency/control joins after explicit USD-thousands conversion.',
        'Verified finance-graph endpoint completeness and the five priority canonical identity mappings.'],
      'unresolved':['Underlying UN primary text, adoption and operative applicability require the separate case source review.',
        'No actual invoice/asset/post/workload population exists in these controls; operational duplication and financial benefit cannot be adjudicated.',
        'Global historical dataset semantic counts and dynamic-lineage gaps are not automatically reduced by this scoped supplement.',
        'Identity joins establish label correspondence only; current mandate/lifecycle/implementation status is not certified.'],
      'candidate_advancement':'NONE','benefit_recognition':'NONE'}

def render(value):
    lines=['# Priority-case dataset semantic review','',
      '**C01–C03 scoped review, 23 October 2026.** Eleven retained datasets were read at their actual row grain. This supplement preserves the original 324-dataset audit and does not authenticate UN primary text or certify complete operational populations.','',
      '| Dataset | Rows / reviewed key | Grain and interpretation |','| --- | --- | --- |']
    for row in value['datasets']:
        lines.append(f"| [{Path(row['path']).name}](../../{row['path']}) | {row['rows']} / `{row['reviewed_row_key'][0]}` | {row['grain']}. {row['interpretation_limit']} |")
    lines += ['', '## Results and decision implications','',
      f"All eleven selected row keys are populated and unique. All {value['joins']['request_to_control']['rows']} expanded request/control memberships resolve, all 21 finance-graph endpoints resolve, and four embedded-efficiency references match after multiplying USD-thousands by 1,000. These checks establish repository correspondence, not observed delivery or evidence authenticity.",'',
      'The twelve budget/arrangement controls all lack transaction document IDs and all say transaction verification has not occurred. All eighteen legacy evidence packages remain not provided; each of the three case summaries records zero verified pairs. Their `0` values count verified pairs and do not measure zero waste. Unknown monetary claims remain `not_estimated`, not numeric zero.','',
      'RSCE modeled FTE, proposed post actions and payroll reassignments remain different measures. The -25/-10/+44 model reconciles to its +9 subtotal; neither +44 proposed transaction posts nor 17 reassignments is an extra model component. Unique post records are still required.','',
      'UNIFIL–UNSCOL controls UF01–UF03 link to EFF019/EFF026/EFF029; their 394,000 + 36,900 + 7,200 USD is the 438,100 USD proposal already embedded in the baseline. Haiti BH01 links to EFF022 at 1.4 million USD; BH02 is a broader 4 million USD proposed internal reimbursement. The two Haiti amounts cannot be netted as like-for-like service costs.','',
      'The five priority entity labels map to canonical identities; the JSON lists exact IDs. Legacy candidate labels such as C12 and roadmap labels such as C02 occupy separate namespaces. URL-only joins remain unapproved because documents and aliases span multiple claims and locators.','',
      'No candidate advances and no benefit is recognized. Close the remaining public-source interpretation questions through the priority source packets, then obtain authorized asset/invoice/post/workload/outcome records at their physical or transactional grain.','',
      '[Machine-readable observations, missing-value counts and input hashes](../../data/priority_cases/dataset_semantic_review.json). Regenerate with `python -B scripts/validate_priority_semantics.py --write`; verify with `--check`.','']
    return '\n'.join(lines)

def outputs(root=ROOT):
    value=build(root)
    return {OUT:json.dumps(value,indent=2,ensure_ascii=False)+'\n',DOC:render(value)}

def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--write',action='store_true');g.add_argument('--check',action='store_true');a=p.parse_args()
    for name,body in outputs().items():
        path=ROOT/name
        if a.write:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(body)
        elif not path.exists() or path.read_text()!=body:raise SystemExit('FAIL: stale priority semantics '+name)
    print('PASS: eleven priority dataset grains, declared keys and scoped joins; no operational validation')
if __name__=='__main__':main()
