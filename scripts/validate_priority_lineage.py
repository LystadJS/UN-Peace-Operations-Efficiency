#!/usr/bin/env python3
"""Resolve selected C01–C03 lineage without importing historical producers."""
import argparse
import ast
import csv
from collections import Counter
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = 'data/priority_cases/lineage_review.json'
DOCUMENT = 'docs/priority_cases/lineage_review.md'
SELECTED = (
 ('scripts/validate_transaction_controls.py', 10, 'RESOLVED_STATIC_CALL_SET'),
 ('scripts/validate_phase3.py', 26, 'RESOLVED_STATIC_DICTIONARY_SET'),
 ('scripts/validate_spm_2027.py', 27, 'RESOLVED_STATIC_DICTIONARY_SET'),
 ('reports/white_paper_2026-10-15/analyze.py', 11, 'PARTIAL_SELECTED_FINANCIAL_CALLS'),
 ('scripts/validate_phase3.py', 97, 'EXTERNAL_SOURCE_DIRECTORY_UNRESOLVED'),
 ('scripts/validate_spm_2027.py', 88, 'EXTERNAL_SOURCE_DIRECTORY_UNRESOLVED'),
)

def require(ok, message):
    if not ok:
        raise ValueError(message)

def sha(root, path):
    return hashlib.sha256((root/path).read_bytes()).hexdigest()

def rows(root,path):
    with (root/path).open(newline='',encoding='utf-8-sig') as handle:
        return list(csv.DictReader(handle))

def gap_inventory(text):
    current=None
    result=[]
    for line in text.splitlines():
        heading=re.fullmatch(r'### `([^`]+)`',line)
        if heading: current=heading[1]
        match=re.fullmatch(r'- Line (\d+): `(READS|WRITES|INVOKES|PARSE_ERROR)` — `([^`]+)`',line)
        if match and current:
            result.append((current,int(match[1]),match[2],match[3]))
    return result

def dictionary_names(tree, variable):
    for node in tree.body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id==variable for t in node.targets):
            value=ast.literal_eval(node.value)
            require(isinstance(value,dict) and all(isinstance(k,str) for k in value),'Expected static dictionary')
            return list(value)
    raise ValueError('Missing reviewed dictionary: '+variable)

def literal_calls(tree, function):
    return sorted([(node.lineno,node.args[0].value) for node in ast.walk(tree)
                   if isinstance(node,ast.Call) and isinstance(node.func,ast.Name)
                   and node.func.id==function and node.args and isinstance(node.args[0],ast.Constant)
                   and isinstance(node.args[0].value,str)])

def build(root=ROOT):
    root=Path(root)
    source_paths={'metadata/repository_audit_scope.json','docs/repository_lineage.md',
                  'metadata/validation_groups.json','scripts/build_financial_baseline.py',
                  'scripts/validate_case_dossiers.py'}
    scope=json.loads((root/'metadata/repository_audit_scope.json').read_text())
    frozen={r['path']:r['sha256'] for r in scope['files']}
    inventory=gap_inventory((root/'docs/repository_lineage.md').read_text())
    require(len(inventory)==196,'Frozen recognized-gap inventory changed; review scope first')
    selected=[]
    for path,line,status in SELECTED:
        require(any(p==path and n==line and op=='READS' for p,n,op,_ in inventory),'Selected expression absent from frozen inventory')
        require(sha(root,path)==frozen[path],'Selected frozen script bytes changed: '+path)
        source_paths.add(path)
        text=(root/path).read_text()
        tree=ast.parse(text)
        require(line<=len(text.splitlines()),'Missing expression locator')
        row={'source_file':path,'line':line,'operation':'READS','original_expression':text.splitlines()[line-1].strip(),
             'review_status':status,'method':'Non-executing AST/literal call and source inspection',
             'resolved_repository_paths':[],'call_sites':[], 'confidence':'STATIC_PATH_ONLY_NOT_RUNTIME_OR_SOURCE_AUTHENTICATION'}
        if status=='RESOLVED_STATIC_CALL_SET':
            calls=literal_calls(tree,'load')
            row['resolved_repository_paths']=sorted({'data/'+name+'.csv' for _,name in calls})
            row['call_sites']=[{'line':n,'argument':name} for n,name in calls]
            row['resolution_basis']='The only five load calls have literal dataset stems; helper joins ROOT/data/(name+.csv).'
        elif status=='RESOLVED_STATIC_DICTIONARY_SET':
            variable='DATA' if path.endswith('validate_phase3.py') else 'FILES'
            names=dictionary_names(tree,variable)
            row['resolved_repository_paths']=sorted('data/'+name+'.csv' for name in names)
            row['resolution_basis']=f'{variable} is a literal module dictionary; its keys feed load(name,key) without mutation in the reviewed script.'
            row['call_sites']=[{'line':n.lineno,'expression':ast.get_source_segment(text,n)} for n in ast.walk(tree)
                                if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='load']
        elif status=='PARTIAL_SELECTED_FINANCIAL_CALLS':
            wanted={'data/spm_2027_mission_budget.csv','data/spm_2027_cluster_bridge.csv','data/spm_2027_embedded_efficiencies.csv'}
            calls=[(n,p) for n,p in literal_calls(tree,'rows') if p in wanted]
            require({p for _,p in calls}==wanted,'White-paper selected calls changed')
            row['resolved_repository_paths']=sorted(wanted)
            row['call_sites']=[{'line':n,'argument':p} for n,p in calls]
            row['resolution_basis']='Only the three directly relevant SPM financial calls are resolved here; other financial/research call families remain outside this selected resolution.'
        else:
            row['resolution_basis']='Optional --source-dir input is supplied outside the repository. Filename/hash-manifest checks do not establish that PDF bytes were supplied or checked.'
            row['unresolved_requirements']=['Authorized source directory with expected PDF filenames','Actual supplied-file hashes and successful --source-dir validation receipt']
        for p in row['resolved_repository_paths']:
            require((root/p).is_file(),'Resolved source does not exist: '+p)
            source_paths.add(p)
        selected.append(row)

    control_path='data/transaction_control_baseline.csv'
    controls={r['control_id']:r for r in rows(root,control_path)}
    require(len(controls)==12,'Transaction control identity population changed')
    amounts={k:Decimal(v['published_amount_usd']) for k,v in controls.items()}
    require(amounts['UF01']+amounts['UF02']+amounts['UF03']==Decimal('438100'),'UNSCOL embedded proposal does not reconcile')
    require(amounts['BH03']-amounts['BH04']==amounts['BH01']==Decimal('1400000'),'Haiti aviation proposal comparator changed')
    require(amounts['BH02']==Decimal('4000000'),'Haiti broader support proposal changed')
    require(amounts['RS01']-amounts['RS02']==Decimal('936100'),'RSCE calendar-share proposal comparison changed')
    chains=[]
    specs=[('C01','RSCE_2027_SPM_share',['RS01'],'published_amount','3259100','Proposed internal allocation, calendar 2027; not a transaction or benefit.'),
      ('C01','RSCE_corporate_total',['RS03'],'published_amount','45911600','Fiscal 2026/27 corporate total; differs from calendar SPM-only share.'),
      ('C01','RSCE_mixed_client_share',['RS04'],'published_amount','3443200','Fiscal 2026/27 mixed SPM/observer-client share; not comparable directly to RS01.'),
      ('C01','RSCE_calendar_share_change',['RS01','RS02'],'RS01-RS02','936100','Same calendar-share proposal comparison; not overbilling or savings.'),
      ('C02','UNSCOL_embedded_asset_measures',['UF01','UF02','UF03'],'UF01+UF02+UF03','438100','Already embedded projected vehicle/ICT/consumable measures; not incremental realized benefit.'),
      ('C03','BINUH_aviation_proposal_difference',['BH03','BH04','BH01'],'BH03-BH04=BH01','1400000','Published budget comparator, not a settled aviation invoice.'),
      ('C03','BINUH_broader_support',['BH02'],'published_amount','4000000','Broader support proposal; not additive to a potentially included aviation component.')]
    guard_text=(root/'scripts/validate_transaction_controls.py').read_text().splitlines()
    for case,claim,ids,formula,value,limit in specs:
        computed=(sum((amounts[k] for k in ids),Decimal(0)) if formula=='UF01+UF02+UF03'
                  else amounts['BH03']-amounts['BH04'] if formula=='BH03-BH04=BH01'
                  else amounts['RS01']-amounts['RS02'] if formula=='RS01-RS02'
                  else amounts[ids[0]])
        require(computed==Decimal(value),'Selected claim amount changed: '+claim)
        dossier_path=f'data/cases/{case}.json';source_paths.add(dossier_path)
        dossier=json.loads((root/dossier_path).read_text())
        snapshots=[e for e in dossier['evidence'] if e['path']==control_path and e['source_snapshot'].get('control_id') in ids]
        require({e['source_snapshot']['control_id'] for e in snapshots}==set(ids),'Case source selection changed: '+claim)
        for e in snapshots:
            require(e['source_snapshot']==controls[e['source_snapshot']['control_id']] and e['sha256']==sha(root,control_path),'Case snapshot drift: '+claim)
        lines=[n for n,s in enumerate(guard_text,1) if any('"'+ident+'"' in s for ident in ids) and ('assert' in s or '==amount' in s)]
        require(lines,'No inspected arithmetic/guard locator: '+claim)
        chains.append({'case_id':case,'claim_id':claim,'source':{'path':control_path,'control_ids':ids,'row_origin':'RETAINED_PUBLIC_TRANSCRIPTION_NO_CAPTURED_EXTRACTION_PRODUCER'},
          'transformation':{'script':'scripts/validate_transaction_controls.py','lines':lines,'formula':formula,'amount_usd':value,'role':'ARITHMETIC_AND_DECLARATION_GUARD_NOT_SOURCE_DATA_PRODUCER'},
          'consuming_case':{'path':dossier_path,'evidence_csv_lines':[e['csv_line'] for e in snapshots],'relationship':'EXACT_RETAINED_ROW_SNAPSHOTS'},
          'downstream_finance':{'script':'scripts/build_financial_baseline.py','output':'data/portfolio/financial_baseline.json','relationship':'SEPARATE_AGGREGATE_SOURCE_PERIMETERS_NOT_A_PRODUCER_OF_THE_CASE_CONTROL_ROWS'},
          'limitation':limit,'operational_input_status':'INTERNAL_LINKED_RECORDS_NOT_OBTAINED'})
    source_paths.add(control_path)
    return {'schema_version':1,'review_id':'C01-C03-SELECTED-LINEAGE-2026-10-23','review_date':'2026-10-23',
      'scope':'Consequence-specific supplement over six recognized frozen expressions and seven retained priority-case financial claims. No original graph is rewritten.',
      'frozen_scope_id':scope['scope_id'],'original_recognized_gap_count':196,'selected_expression_count':len(selected),
      'selected_status_counts':dict(sorted(Counter(r['review_status'] for r in selected).items())),
      'selected_expressions':selected,'claim_chains':chains,
      'producer_boundary':'Original transaction-control CSVs are retained transcriptions. Validators consume and guard them; no script/PDF extraction producer is asserted.',
      'global_gap_disposition':'The frozen 196-expression inventory is preserved. This supplement does not subtract scoped resolutions from that historical denominator or imply globally complete lineage.',
      'operational_boundary':'Internal chargeback journals, asset transfers/canceled procurement, aviation flight/billing populations and actual costs remain absent; no actual operational lineage or benefits are certified.',
      'source_sha256':{p:sha(root,p) for p in sorted(source_paths)}}

def render(value):
    lines=['# Priority-case lineage review','',
      'This supplement resolves concrete paths for C01–C03 financial controls while preserving the original frozen A04 graph. It does not authenticate original UN documents or actual transactions.','',
      'Six recognized expressions are selected from the historical 196: three helper call sets are statically resolved; one white-paper helper is resolved only for three selected SPM financial calls; two optional external-PDF-directory branches remain unresolved. The historical denominator remains 196.','',
      '| Source operation | Selected disposition | Scope |','| --- | --- | --- |']
    for r in value['selected_expressions']:
        lines.append(f"| `{r['source_file']}:{r['line']}` | {r['review_status']} | {len(r['resolved_repository_paths'])} repository paths; see exact call sites in the receipt |")
    lines += ['','## Priority financial claim chains','',
      '| Case | Retained claim | USD | Meaning |','| --- | --- | ---: | --- |']
    for c in value['claim_chains']:
        lines.append(f"| {c['case_id']} | {c['claim_id']} | {c['transformation']['amount_usd']} | {c['limitation']} |")
    lines += ['','The path is retained control row → arithmetic/declaration validator → exact case evidence snapshot. `validate_transaction_controls.py` is a consumer and guard, not a data-extraction producer. The original transcription step has no captured executable producer; its authority must be evaluated from the underlying official source. `build_financial_baseline.py` separately computes aggregate financial perimeters and does not produce the individual transaction-control rows.','',
      'The optional `--source-dir` branches in the GA and SPM validators need actual externally supplied PDFs and a successful byte-check receipt. A hash string in a manifest is not evidence that the file was present or checked. Internal invoice, asset, post, flight and workload branches remain unavailable. None of these repository lineage paths proves duplicated expenditure, implementation, owner approval or a benefit.','',
      'The [machine-readable receipt](../../data/priority_cases/lineage_review.json) retains source hashes, expression and call-site lines, selected row identities, formula guard lines and case snapshot locators. Source changes invalidate this supplement until reviewed and regenerated.','',
      'Reproduce with `python -B scripts/validate_priority_lineage.py --check`; use `--write` only after reviewing changed source bytes. Unit tests: `python -B tests/check_priority_lineage.py`.','']
    return '\n'.join(lines)

def outputs(root=ROOT):
    value=build(root)
    return {OUTPUT:json.dumps(value,indent=2,ensure_ascii=False)+'\n',DOCUMENT:render(value)}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--write',action='store_true');mode.add_argument('--check',action='store_true')
    args=parser.parse_args()
    for p,body in outputs().items():
        target=ROOT/p
        if args.write:
            target.parent.mkdir(parents=True,exist_ok=True);target.write_text(body)
        else:require(target.is_file() and target.read_text()==body,'Priority lineage output drift: '+p)
    print('PASS: six selected lineage expressions and seven priority claims; frozen 196 retained')
if __name__=='__main__': main()
