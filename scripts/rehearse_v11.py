#!/usr/bin/env python3
"""Offline public-source tabletop. It never grants authority or starts a live trial.

Build: python scripts/rehearse_v11.py --build
Check: python scripts/rehearse_v11.py --check
The judgment notes are assistant-adjudicated inputs, not an independent gold standard.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, re, unicodedata
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'data/census_v11'
BASE='cf9df9e19448f81ba666f5456245338540c6c681'

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def save_json(p,obj): p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def dump_csv(p,rows):
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        w.writerows({k:json.dumps(v,ensure_ascii=False,sort_keys=True) if isinstance(v,(dict,list)) else v for k,v in row.items()} for row in rows)
def ensure(x,msg):
    if not x:raise AssertionError(msg)
def norm(s):return re.sub(r'[^\w]','',unicodedata.normalize('NFKC',s).casefold())
def candidate():
    fixed={r['observation_id']:r for r in read_csv(ROOT/'data/census_v10/fixed_source_scope.csv')}
    keys=['source_id','source_sha256','locator','pages','source_assertion','qualified_values','attribution_class']
    return [dict(o,**{k:fixed[o['observation_id']][k] for k in keys}) for o in read_csv(ROOT/'data/census_v10/product_obligations.csv')]
def closed_gates():
    p=json.loads((ROOT/'data/census_v10/protocol.json').read_text())
    ensure(p['authorization_status']=='not_authorized_for_live_use','Live-use authorization changed')
    ensure(p['safeguards']['automatic_start'] is False,'Automatic start enabled')
    ensure(all(v is None for a in p['case_activation'].values() for v in a.values()),'A live activation field was populated')
    a=json.loads((ROOT/'data/census_v10/activation_status.json').read_text())
    ensure(all(x['live_execution_authorized'] is False for x in a.values()),'Live gate is open')
    for f in (ROOT/'data/census_v10/templates').glob('*.csv'):
        ensure(read_csv(f)==[],'Frozen/live instrument is no longer empty: '+f.name)
    return a

def sources_and_anchors():
    import fitz
    from pypdf import PdfReader
    from bs4 import BeautifulSoup
    sources=read_csv(ROOT/'data/census_v10/source_scope.csv')
    fixed=read_csv(ROOT/'data/census_v10/fixed_source_scope.csv')
    observations={}
    for v,fn in [(8,'pilot_design.json'),(9,'reviewed_design.json')]:
        design=json.loads((ROOT/f'data/census_v{v}'/fn).read_text())
        for o in design['observations']:observations[f'V{v}:'+o['observation_id']]=o
    parsed={};auth=[];page_rows=[]
    for s in sources:
        path=ROOT/s['file'];ensure(digest(path)==s['sha256'],'Original source hash changed: '+s['source_id'])
        selected=sorted({p for r in fixed if r['source_id']==s['source_id'] for p in json.loads(r['pages'])})
        if path.suffix=='.pdf':
            doc=fitz.open(path);reader=PdfReader(path)
            ensure(len(doc)==len(reader.pages),'Parser page-count disagreement')
            cover=doc[0].get_text();ensure(norm(s['source_symbol']) in norm(cover),'Cover symbol absent')
            texts={p:doc[p-1].get_text() for p in selected}; other={p:reader.pages[p-1].extract_text() or '' for p in selected}
            total=len(doc);method='PyMuPDF_and_pypdf'
        else:
            soup=BeautifulSoup(path.read_bytes(),'html.parser');main=soup.find('main') or soup.find('article')
            ensure(main is not None,'No reviewed HTML body')
            texts={1:main.get_text(' ',strip=True)};other=texts;total=1;method='BeautifulSoup_main_body_single_parser'
        parsed[s['source_id']]=(texts,other)
        auth.append(dict(source_id=s['source_id'],file=s['file'],source_symbol=s['source_symbol'],url=s['url'],sha256=s['sha256'],pages=total,selected_pages=selected,method=method,hash_status='matches_frozen_source'))
        for p,text in texts.items():page_rows.append(dict(source_id=s['source_id'],page=p,normalized_text_sha256=hashlib.sha256(norm(text).encode()).hexdigest(),chars=len(text),purpose='selected_claim_context_not_full_document_review'))
    anchors=[]
    for r in fixed:
        o=observations[r['observation_id']];texts,other=parsed[r['source_id']]
        a=' '.join(texts[p] for p in o['pages']);b=' '.join(other[p] for p in o['pages'])
        failures=[x for x in o['anchors'] if norm(x) not in norm(a)]
        failures2=[x for x in o['anchors'] if norm(x) not in norm(b)]
        ensure(not failures and not failures2,'Anchor missing: '+r['observation_id']+' '+str(failures+failures2))
        anchors.append(dict(observation_id=r['observation_id'],source_id=r['source_id'],pages=o['pages'],anchor_count=len(o['anchors']),primary_anchor_check='pass',secondary_pdf_anchor_check='pass' if r['source_id'] not in ['V8:N01','V8:N02'] else 'not_applicable_HTML',interpretation='retrievability_only_not_semantic_truth'))
    # Separate semantic checks for the two proposed amendments. These do not
    # retroactively convert the assistant review into independent human review.
    ensure(norm('exchanged information on 202 instances and exchanged three individuals in custody') in norm(parsed['V9:G2'][0][3]),'Custody-action evidence missing')
    ensure(norm('Over 1.7 million euros have been utilized') in norm(parsed['V9:G3'][0][5]),'Strict lower-bound evidence missing')
    return auth,page_rows,anchors

def scenario_tests(fixed):
    x={r['observation_id']:json.loads(r['qualified_values']) for r in fixed}
    return {
      'SC01':{x['V8:O04']['event_start'],x['V8:O15']['event_start']}=={'2025-01-27','2025-01-28'},
      'SC02':x['V8:O06']['attendance_comparator']=='>' and x['V8:O06']['workplan_stage']=='adopted_not_verified_implemented',
      'SC03':x['V8:O07']['role']=='CNMC_chair' and x['V8:O08']['event_year']==2024 and x['V8:O18']['product_type']=='publication_not_course',
      'SC04':x['V8:O13']['status']==x['V8:O22']['status']=='announced' and x['V8:O22']['explicit_reference']=='B1',
      'SC05':{x['V9:CY009']['exports_eur_billion'],x['V9:CY010']['exports_eur_billion']}=={4.12,2.14} and x['V9:CY009']['ratio_allowed'] is False and x['V9:CY010']['ratio_allowed'] is False,
      'SC06':x['V9:CY006']['stage']=='planned_start' and x['V9:CY024']['stage']=='commenced' and x['V9:CY036']['actual_completion_date'] is None and x['V9:CY037']['asset']=='additional_crossing_points',
      'SC07':x['V9:CY018']['secretariat_endorsement'] is False and x['V9:CY019']['secretariat_endorsement'] is False and x['V9:CY023']['actual_version']=='S/2025/7/Rev.1',
      'SC08':x['V9:CY020']['scope']!=x['V9:CY038']['scope'] and x['V9:CY038']['stage']=='mixed_completed_ongoing_preparation',
      'SC09':x['V9:CY021']['allocation_eur']==1000000 and x['V9:CY031']['allocation_eur'] is None and x['V9:CY041']['allocation_eur']==1500000,
      'SC10':x['V9:CY005']['unit']!=x['V9:CY016']['unit']!=x['V9:CY017']['unit'] and x['V9:CY028']['unit']!=x['V9:CY028']['custody_unit'],
      'SC11':sum([20,20,20,20])==80 and sum([10,8,80,5,7])==110,
      'SC12':safety_decision(faster=True,material_error=True)=='do_not_advance'
    }
def safety_decision(*,faster:bool,material_error:bool):
    return 'do_not_advance' if material_error else 'owner_review_required_no_automatic_advance'

def build():
    closed_gates();D.mkdir(exist_ok=True)
    decisions=json.loads((D/'review_decisions.json').read_text())
    ensure(decisions['baseline_commit']==BASE,'Wrong baseline')
    c=candidate();payload=json.dumps(c,ensure_ascii=False,indent=2)+'\n'
    ensure(hashlib.sha256(payload.encode()).hexdigest()==decisions['candidate_sha256'],'Candidate differs from frozen initial export')
    (D/'initial_candidate.json').write_text(payload,encoding='utf-8')
    notes={r['observation_id']:r['source_review_note'] for r in decisions['reviews']}
    ensure(set(notes)=={r['observation_id'] for r in c} and len(notes)==61,'Incomplete or extra review scope')
    amendments={a['observation_id']:a for a in decisions['amendments']}
    auth,pages,anchors=sources_and_anchors()
    rows=[];effective=[]
    boundary={'retain_owner_specific_boundary','retain_prewindow_context','owner_only','party_attribution_only'}
    for r in c:
        a=amendments.get(r['observation_id']);sem='needs_correction' if r['observation_id']=='V9:CY028' else 'supported'
        row=dict(obligation_id=r['obligation_id'],case_id=r['case_id'],observation_id=r['observation_id'],product_id=r['product_id'],source_id=r['source_id'],source_sha256=r['source_sha256'],pages=r['pages'],locator=r['locator'],required_action=r['required_action'],obligation_class='boundary_preservation' if r['required_action'] in boundary else 'factual_support_or_reference',source_located='yes',source_semantics=sem,qualification_fidelity='amendment_requested' if a else 'supported_within_selected_scope',first_pass_disposition='amendment_requested_scoring_withheld' if a else 'supported',amendment_id=a['amendment_id'] if a else '',review_note=notes[r['observation_id']],reviewer=decisions['reviewer'],owner_review='not_performed')
        rows.append(row)
        updated=dict(r);updated['tabletop_proposed_assertion']=a['proposed_assertion'] if a else r['source_assertion'];vals=json.loads(r['qualified_values'])
        if a:vals.update(a['value_updates'])
        updated.update(tabletop_proposed_values=vals,amendment_id=row['amendment_id'],reference_change_status='proposed_only_original_unchanged' if a else 'unchanged',post_proposal_source_recheck='supported_by_selected_original_passage' if a else 'not_needed',owner_approval='not_obtained')
        effective.append(updated)
    dump_csv(D/'obligation_reviews.csv',rows);save_json(D/'proposed_support_records.json',effective)
    dump_csv(D/'source_authentication.csv',auth);dump_csv(D/'selected_page_checks.csv',pages);dump_csv(D/'anchor_checks.csv',anchors)
    save_json(D/'amendment_requests.json',decisions['amendments'])
    fixed=read_csv(ROOT/'data/census_v10/fixed_source_scope.csv');checks=scenario_tests(fixed)
    scenarios=[]
    for r in read_csv(ROOT/'data/census_v10/scenario_cards.csv'):
        sid=r['scenario_id'];ensure(checks[sid],sid+' failed')
        scenarios.append(dict(scenario_id=sid,reference_observations=r['reference_observations'],challenge=r['challenge'],tabletop_response=decisions['scenario_answers'][sid],execution='assistant_tabletop_not_owner_trial',assertion_check='pass',evidence_class='synthetic_safety_or_accounting' if sid in ['SC11','SC12'] else 'retained_public_source',open_amendment='AM11-02' if sid=='SC09' else 'AM11-01' if sid=='SC10' else '',disposition='executed_amendment_remains_open' if sid in ['SC09','SC10'] else 'executed_defined_control_preserved'))
    dump_csv(D/'scenario_execution.csv',scenarios)
    summary=dict(version='11.0',asof='2026-10-15',baseline_commit=BASE,scope='public_source_tabletop_known_cases',reviewer=decisions['reviewer'],fixed_source_observations=64,fixed_obligations=61,reviewed_obligations=len(rows),obligations_by_case=dict(Counter(r['case_id'] for r in rows)),boundary_obligations=sum(r['obligation_class']=='boundary_preservation' for r in rows),factual_support_obligations=sum(r['obligation_class']=='factual_support_or_reference' for r in rows),source_located=61,source_semantics_supported=60,semantic_corrections_requested=1,strict_qualifier_hardening_requests=1,unchanged_formulations_supported=sum(not r['amendment_id'] for r in rows),amendment_requests=2,scoring_withheld=2,proposed_corrections_source_checked=2,reference_amendments_adopted=0,original_source_files=len(auth),original_PDFs=sum(a['file'].endswith('.pdf') for a in auth),original_PDF_pages=sum(a['pages'] for a in auth if a['file'].endswith('.pdf')),selected_pdf_pages_checked=sum(a['source_id'] not in ['V8:N01','V8:N02'] for a in pages),scenario_cards_executed=12,source_scenarios=10,synthetic_scenarios=2,owner_tabletop_reviews=0,owner_approvals=0,live_trials=0,live_time_records=0,live_gate_status='BLOCKED_FOR_LIVE_USE',course_watch='paused_no_checks_run',mandates_and_rankings='unchanged',staff_time_saved='not_estimated',cash_savings='not_estimated',operational_effect='not_measured',statistical_inference='not_attempted')
    save_json(D/'tabletop_summary.json',summary)
    protected={str(p.relative_to(ROOT)):digest(p) for folder in ['data/census_v8','data/census_v9','data/census_v10'] for p in sorted((ROOT/folder).rglob('*')) if p.is_file()}
    protected['data/acabq_2027_ranked_consolidation.csv']=digest(ROOT/'data/acabq_2027_ranked_consolidation.csv')
    prior=json.loads((ROOT/'data/census_v10/input_manifest.json').read_text())
    for name,sha in prior.items():ensure(digest(ROOT/name)==sha,'Earlier pinned input changed: '+name)
    save_json(D/'frozen_input_manifest.json',protected)
    save_json(D/'closed_gate_receipt.json',dict(live_gates=closed_gates(),owner_approvals_obtained=0,live_execution=False,reference_amendments_adopted=False))
    render(rows,effective,scenarios,summary,auth)
    paths=[p for p in D.iterdir() if p.is_file() and p.name!='output_manifest.json']+[ROOT/'docs/v11_public_tabletop.md',ROOT/'docs/v11_tabletop_support_sheets.md']
    save_json(D/'output_manifest.json',{str(p.relative_to(ROOT)):digest(p) for p in sorted(paths)})
    check();print(json.dumps(summary,indent=2))

def render(rows,effective,scenarios,s,auth):
    sm={r['source_id']:r for r in auth}
    header=['# V11 public-source tabletop rehearsal','', '**15 October 2026 | Assistant review of fixed V8/V9 obligations | No live activation**','',
      '## Decision','',
      '**Rehearsal completed; two reference formulations require amendment before their scoring can resume.** All 61 fixed obligations were reviewed against retained originals. Sixty have supported substantive interpretations; one has a semantic action-compression error. A second, substantively supported row needs an explicit strict lower-bound qualifier. Consequently 59 formulations are retained without revision and two remain withheld pending reference-amendment disposition. Proposed replacement text is source-checked but is not adopted into V8, V9 or V10.','',
      'The review was performed by the assistant, with prior exposure to the designs. It is not independent human review, an owner tabletop, a blind test, an institutional clearance or an operational effectiveness evaluation.','',
      '## Fixed population and observed dispositions','',
      '| Case | Fixed obligations | Supported unchanged | Amendment requests | Boundary obligations |','|---|---:|---:|---:|---:|']
    for case in ['SP08P1','SP09P1']:
        rr=[r for r in rows if r['case_id']==case]
        header.append(f"| {case} | {len(rr)} | {sum(not r['amendment_id'] for r in rr)} | {sum(bool(r['amendment_id']) for r in rr)} | {sum(r['obligation_class']=='boundary_preservation' for r in rr)} |")
    header+=['','All 64 source observations remain in the source inventory, including three V8 supporting-notice observations that do not add output obligations. The 61 obligations include 45 factual-support/reference duties and 16 boundary-preservation duties. Nothing was excluded after seeing outcomes. Repeated assertions, correlated products and known scenario cards are not independent experimental observations.','',
      '[Complete obligation reviews](../data/census_v11/obligation_reviews.csv) retain the first-pass dispositions, source hashes, locators and individual reasoning notes. [Initial candidate](../data/census_v11/initial_candidate.json) is the exact pre-review projection of the V10 scope, not a newly authored baseline or actual normal-workflow output.','',
      '## Two source-backed amendment requests','',
      '**AM11-01, V9:CY028: separate information exchange from exchange of people in custody.** S/2026/9 paragraph 18, page 3, describes information exchanged in 202 instances and, separately, exchange of three individuals in custody. The inherited prose makes both appear to be information exchange. Its structured custody fields partly preserve the distinction, which is why token/anchor presence alone did not reveal the semantic loss. The proposed wording explicitly names the two actions; 202 and 3 are not added, and no person identities are collected.','',
      '**AM11-02, V9:CY041: make the strict lifetime lower bound explicit.** S/2026/551 paragraph 29, page 5, says more than EUR1.7 million had been utilized since inception in 2019. The inherited data already labels EUR1.7 million a lower bound; the defect is not a demonstrated wrong amount. Its prose omits the strict qualifier and its field lacks an explicit comparison operator. The proposed wording and extra fields preserve greater-than and 2019, separately from approximately 67% of EUR1.5 million allocated for 2023-2026. No efficiency trend or savings is inferred.','',
      'Both passages were freshly extracted with two PDF parsers and visually checked. Their retained original hashes match the frozen manifests. The [amendment requests](../data/census_v11/amendment_requests.json) preserve the original formulations and keep adoption open. The [proposed support records](../data/census_v11/proposed_support_records.json) and [12 support sheets](v11_tabletop_support_sheets.md) display candidate repairs, not silently corrected historical evidence.','',
      '## Scenario execution','',
      '| Card | Actual tabletop response | Status |','|---|---|---|']
    for r in scenarios:header.append(f"| {r['scenario_id']} | {r['tabletop_response']} | {r['disposition']} |")
    header+=['',
      'The ten source scenarios rehearse known dates, units, scope, lifecycle and attribution controls. SC09 and SC10 remain linked to the open amendments. SC11 and SC12 are clearly synthetic arithmetic/safety exercises, not evidence of staff behavior or incident rates. Automated assertions verify retained fields and defined decisions; they do not independently validate the assistant judgments.','',
      '## What the production model must retain','',
      'A reliable support sheet must preserve the **action as well as the number, unit, scope, date, source and attribution**. The custody example demonstrates why matching numbers and keywords is insufficient. A numerical lower-bound field should render its comparison operator explicitly rather than depend on a reader interpreting a column name. These are narrow design improvements, not proof that an operational team currently makes either error.','',
      'Known source disagreements remain qualified: the 27/28 January Nigeria start dates are not resolved by voting, and the EUR4.12 billion/EUR2.14 billion export comparators still block a harmonized ratio. Planned construction, commencement and a completion-marking ceremony remain different stages. Party submissions, operational accounts and office-specific assessments retain their authorship and responsibilities. Existing joint support remains baseline, not a new coordination saving.','',
      '## Workload and live-use gates','',
      'No preparer workload, staff time, clearance latency, owner feedback or operational result was measured. No normal-versus-shadow comparison was run. The frozen V10 workload and owner instruments remain empty. The synthetic four-person meeting contributes 80 person-minutes; adding synthetic normal=10, shadow=8, setup=5 and evaluation=7 yields actual recorded burden 110, alternative process descriptions 90 and 88, and a descriptive contrast of 2. None is time saved. These figures are fixture arithmetic only; the retained R engine is tested separately by the acceptance workflow.','',
      'Both SP08P1 and SP09P1 remain **BLOCKED_FOR_LIVE_USE** with all local activation fields unset. No authorization, contact, personnel data, internal drafts, new platform permission, scheduled task, course check or source-system operational write was introduced. C02/C05 remain nonadditive research roles; parent/mission rankings and 20/32 retrospective support are unchanged.','',
      '## Coverage, reproducibility and next decision','',
      f"The corpus contains {s['original_PDFs']} PDFs ({s['original_PDF_pages']} pages) and two official notices. Fresh extraction covers the {s['selected_pdf_pages_checked']} unique PDF pages referenced by the selected observations, plus the notice bodies. It is not a full substantive review of every page or an audit of annex claims. Source-cover, hash and anchor checks locate evidence; they cannot establish its real-world truth or institutional authority.",'',
      'Direct browser retrieval/screenshot attempts for selected originals were unavailable. The rehearsal therefore uses authenticated retained original bytes, not search snippets or substitute sources. The two amendment passages were visually checked locally. Unrelated search hits were excluded and no new claims or course records entered the fixed population.','',
      'Rebuild: `python scripts/rehearse_v11.py --build`. Verify retained files and closed gates: `python scripts/rehearse_v11.py --check`. The human-readable review notes are adjudicated inputs, not regenerated independent judgments. Original source files remain in their V8/V9 repository locations.','',
      '**Next decision:** independently review AM11-01 and AM11-02 against the cited original paragraphs and decide whether to adopt a new reference version. Preserve the first-pass failures and recheck only affected renderings. Neither a clean technical recheck nor adoption of a research correction opens a live-use gate.','']
    (ROOT/'docs/v11_public_tabletop.md').write_text('\n'.join(header),encoding='utf-8')
    lines=['# V11 tabletop support sheets','', '**Research support sheets only. No issued UN output, institutional clearance, normal-workflow observation or live shadow. Two candidate amendments remain unadopted.**','']
    for pid in dict.fromkeys(r['product_id'] for r in effective):
        src=sm[pid];lines+=['## '+pid+' | '+src['source_symbol'],'',f"Source: [{src['source_symbol']}]({src['url']}). SHA-256: `{src['sha256']}`.",'']
        for r in effective:
            if r['product_id']!=pid:continue
            lines += [f"### {r['obligation_id']}",f"**Required action:** {r['required_action']}. **Locator:** {r['locator']}, pages {r['pages']}.",r['tabletop_proposed_assertion']]
            if r['amendment_id']:lines += [f"**{r['amendment_id']}: proposed repair only; original scoring withheld.** Original: {r['source_assertion']}"]
            lines += ['Qualified fields: `'+json.dumps(r['tabletop_proposed_values'],ensure_ascii=False,sort_keys=True)+'`.','']
    (ROOT/'docs/v11_tabletop_support_sheets.md').write_text('\n'.join(lines),encoding='utf-8')

def check():
    closed_gates()
    for name,sha in json.loads((D/'frozen_input_manifest.json').read_text()).items():ensure(digest(ROOT/name)==sha,'Frozen input changed: '+name)
    for name,sha in json.loads((D/'output_manifest.json').read_text()).items():ensure(digest(ROOT/name)==sha,'Output differs: '+name)
    c=candidate();rows=read_csv(D/'obligation_reviews.csv');s=json.loads((D/'tabletop_summary.json').read_text())
    ensure(len(rows)==61 and {x['obligation_id'] for x in rows}=={x['obligation_id'] for x in c},'Population mismatch')
    ensure(len({r['obligation_id'] for r in rows})==61,'Duplicate obligation')
    ensure(sum(r['first_pass_disposition']=='supported' for r in rows)==59,'First-pass result changed')
    ensure(sum(r['source_semantics']=='supported' for r in rows)==60,'Semantic outcomes changed')
    ensure(sum(r['obligation_class']=='boundary_preservation' for r in rows)==16,'Boundary denominator changed')
    ensure(all(r['owner_review']=='not_performed' for r in rows),'Invented owner review')
    ensure(s['reference_amendments_adopted']==s['owner_approvals']==s['live_trials']==s['live_time_records']==0,'Gate overclaim')
    ensure(s['staff_time_saved']==s['cash_savings']=='not_estimated','Unsupported financial claim')
    ensure(len(read_csv(D/'scenario_execution.csv'))==12,'Scenario omitted')
    print('PASS: 61 obligations accounted for; 59 unchanged supports, 2 amendment holds; live gates closed.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True);g.add_argument('--build',action='store_true');g.add_argument('--check',action='store_true');a=p.parse_args()
    build() if a.build else check()
