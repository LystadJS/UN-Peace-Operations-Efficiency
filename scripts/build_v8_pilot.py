#!/usr/bin/env python3
"""Build/check a retrospective public-source reporting pilot, not a live UN workflow.

Usage: python3 scripts/build_v8_pilot.py --build
       python3 scripts/build_v8_pilot.py --check
Build requires pypdf==5.9.0 and beautifulsoup4==4.14.3. Check is offline/std-lib.
"""
from __future__ import annotations
import argparse, copy, csv, hashlib, json, re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/census_v8'
DOCS=ROOT/'docs'
CORE=('P01','P02','P03')

def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))

def write_json(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def require(ok, reason):
    if not ok: raise ValueError(reason)

def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def write_csv(path,rows):
    require(bool(rows),'Empty output schema')
    keys=list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
        for row in rows:
            w.writerow({k:json.dumps(v,ensure_ascii=False,sort_keys=True) if isinstance(v,(list,dict)) else v for k,v in row.items()})

def norm(text):
    return re.sub(r'[^a-z0-9]','',text.lower())

def load_texts(design):
    from pypdf import PdfReader
    from bs4 import BeautifulSoup
    result={}
    for s in design['sources']:
        path=DATA/s['file'];require(sha(path)==s['sha256'],'Source bytes changed: '+s['source_id'])
        if path.suffix=='.pdf':
            reader=PdfReader(path); pages=[p.extract_text() or '' for p in reader.pages]
            require(len(pages)==s['pages'],'Page-count mismatch')
            require(norm(s['title']) in norm(pages[0]),'Cover symbol mismatch')
        else:
            soup=BeautifulSoup(path.read_bytes(),'html.parser')
            body=soup.select_one('.field--name-body')
            require(body is not None and len(body.get_text())>300,'Challenge/empty HTML is not a notice')
            pages=[body.get_text(' ',strip=True)]
            expected='01 February 2025' if s['source_id']=='N01' else '28 February 2025'
            require(expected in soup.get_text(' ',strip=True),'Notice publication masthead missing')
        result[s['source_id']]=pages
    return result

def validate_design(d,texts=None):
    ss={s['source_id']:s for s in d['sources']}; cc={c['component_id']:c for c in d['components']}
    oo={o['observation_id']:o for o in d['observations']}
    require(len(ss)==6 and len(cc)==10 and len(oo)==23,'Unexpected source/component/observation identities')
    require({p['product_id'] for p in d['products']}=={'R1','B1','R2','B2'},'Distinct products lost')
    for o in oo.values():
        require(o['source_id'] in ss and o['component_id'] in cc,'Orphan evidence link')
        require(all(1<=p<=ss[o['source_id']]['pages'] for p in o['pages']),'Page out of range')
        v=o['values']
        if v.get('event_start') and v.get('event_end'):require(v['event_start']<=v['event_end'],'Reversed activity dates')
        if texts is not None:
            txt=norm(' '.join(texts[o['source_id']][p-1] for p in o['pages']))
            require(all(norm(a) in txt for a in o['anchors']),'Unsupported source anchor: '+o['observation_id'])
    for e in d['edges']:
        require(e['from_source'] in ss and e['to_source'] in ss,'Orphan production edge')
        if texts is not None:
            txt=norm(' '.join(texts[e['to_source']][p-1] for p in e['target_pages']))
            require(all(norm(a) in txt for a in e['anchors']),'Unsupported referral: '+e['edge_id'])
    for p in d['products']:
        require(p['components']==[o['component_id'] for o in oo.values() if o['source_id']==p['product_id']],'Product scope drift')
        require(p['deployment_status']=='retrospective_demo_not_live','Live implementation invented')
    require(d['safeguards']['incremental_net_savings']=='not_estimated','Unsupported savings')
    require(d['safeguards']['staff_hours_saved']=='not_estimated','Unsupported time saving')
    require(d['safeguards']['frozen_rankings']=='unchanged','Frozen ranks altered')

def packet(d,product_id):
    ss={s['source_id']:s for s in d['sources']}
    p=next(x for x in d['products'] if x['product_id']==product_id)
    accepted=[copy.deepcopy(o) for o in d['observations'] if o['component_id'] in p['components'] and ss[o['source_id']]['replay_available_from']<=p['replay_checkpoint']]
    # Source disagreement is retained, never resolved by majority vote.
    start_options=sorted({o['values']['event_start'] for o in accepted if o['component_id']=='P01' and o['values'].get('date_scope')=='whole_visit'})
    return dict(product_id=product_id,owner=p['owner'],checkpoint=p['replay_checkpoint'],approval=p['approval'],
                observations=accepted,date_options=start_options,date_conflict=len(start_options)>1,
                new_global_event_count='not_estimated',staff_hours_saved='not_estimated',incremental_net_savings='not_estimated',
                interpretation='source-qualified retrospective fact sheet; not an issued UN product')

def validate_packet(d,p):
    expected=packet(d,p['product_id'])
    # Enforce lossless, dated, role-qualified exports. This does not independently
    # validate the manual source paraphrases; source anchors and review do that.
    require(set(p)==set(expected),'Unexpected packet fields')
    for key in expected:
        require(p.get(key)==expected[key], 'Packet contract mismatch: '+key)

def baseline_manifest():
    paths=[]
    for folder in ('data','docs','scripts','tests'):
        for p in (ROOT/folder).rglob('*'):
            rel=p.relative_to(ROOT).as_posix()
            if not p.is_file() or '__pycache__' in rel or '/census_v8/' in rel or 'v8_' in p.name:continue
            paths.append(dict(path=rel,sha256=sha(p)))
    return sorted(paths,key=lambda x:x['path'])

def link(s,page=None):
    return '['+s['title']+(f', p. {page}' if page else '')+']('+s['official_url']+')'

def create_outputs(d,texts):
    ss={s['source_id']:s for s in d['sources']}; cc={c['component_id']:c for c in d['components']}
    views=[packet(d,p['product_id']) for p in d['products']]
    for p in views:validate_packet(d,p)
    write_json(DATA/'packet_views.json',views)
    write_csv(DATA/'source_manifest.csv',d['sources'])
    write_csv(DATA/'claim_ledger.csv',d['observations'])
    write_csv(DATA/'production_edges.csv',d['edges'])
    matrix=[]
    for c in d['components']:
        row=dict(c)
        for sid in ['N01','N02','R1','B1','R2','B2']:
            row[sid]=';'.join(o['observation_id'] for o in d['observations'] if o['component_id']==c['component_id'] and o['source_id']==sid) or 'not_selected_observation'
        matrix.append(row)
    write_csv(DATA/'source_component_matrix.csv',matrix)
    write_json(DATA/'source_text.json',texts)
    ranks=read_csv(ROOT/'data/acabq_2027_ranked_consolidation.csv')
    changes={
       'C09':('pilot_1_joint_with_C02','Worked joint-event packet; no additional joint travel or workshop proposed.'),
       'C02':('pilot_1_joint_with_C09','Worked source-to-product views and attributed briefing update; distinct reports retained.'),
       'C05':('enabler_of_pilot_1_not_additional_saving','Use existing controlled storage and versioning; no new platform justified.'),
       'C16':('conditional_extension_not_piloted','Focal-point administration may fit existing shared services; no staffing or charging redesign validated.')}
    overlay=[]
    for row in ranks:
        cid=row['candidate_id'];seq,finding=changes.get(cid,('not_reassessed_in_V8','No V8 source-specific readiness change.'))
        overlay.append(dict(candidate_id=cid,frozen_rank=row['revised_public_rank'],scope=row['scope'],v8_work_sequence=seq,v8_finding=finding,
                            implementation_status='not_authorized_or_validated',financial_status='not_estimated',rank_change='none',
                            distinct_cost_pool='not_established',case_group='SP08P1' if cid in changes else 'not_reassessed'))
    write_csv(DATA/'consolidation_overlay.csv',overlay)
    write_csv(DATA/'product_version_register.csv', [dict(product_id=v['product_id'], checkpoint=v['checkpoint'], packet_sha256=hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest(), owner=v['owner'], clearance='not_newly_obtained') for v in views])
    snapshot=[]
    for p in views:
        own=[o for o in p['observations'] if o['source_id']==p['product_id']]
        prior=[o for o in p['observations'] if o['source_id']!=p['product_id']]
        snapshot.append(dict(product_id=p['product_id'],checkpoint=p['checkpoint'],own_output_observations=len(own),eligible_earlier_observations=len(prior),conflict_flag=p['date_conflict'],approval=p['approval']))
    write_csv(DATA/'replay_results.csv',snapshot)
    summary=dict(version=8,asof=d['asof'],baseline_commit=d['baseline_commit'],source_pdfs=4,source_pdf_pages=sum(s['pages'] for s in d['sources'] if s['file'].endswith('.pdf')),
       source_notices=2,selected_components=len(cc),source_observations=len(d['observations']),distinct_product_views=len(views),
       explicit_reference_edges=sum(e['kind'].startswith('explicit_') for e in d['edges']),corroboration_edges=2,
       core_input_identities=3,core_appearances_in_selected_final_products=sum(o['component_id'] in CORE and o['source_id'] in {'R1','B1','R2','B2'} for o in d['observations']),
       date_discrepancy_groups=1,metadata_replay_proxies=2,validation='source_hashes_covers_pages_anchors_and_packet_contracts_passed',
       live_workflow_test='not_run',productivity_effect='not_estimated',savings='not_estimated',frozen_ranks='unchanged',
       course_watch='paused_by_user; no task execution or new course check',source_design_sha256=sha(DATA/'pilot_design.json'))
    write_json(DATA/'pilot_summary.json',summary)
    write_json(DATA/'operational_status.json',dict(asof=d['asof'],course_watch='paused',basis='User instruction and verified scheduler disablement in prior conversation, 2026-10-15',course_checks_in_V8=0,reactivation_authorized=False))
    # Worked outputs are evidence-support sheets, never fabricated official reports.
    work=['# V8 worked UNOWAS–UNOCA reporting cycle','',
          '**Retrospective reconstruction, January–June 2025. Not a new SG report, speech, mandate or operational implementation.**','',
          '## Shared source model','',
          'A component keeps every source observation, its event/measurement time, publication metadata, role, count qualifier and locator. An office-specific product points to selected observations; it does not inherit all regional material. Public notices corroborate events but the actual editorial path from notice to report is unproven.','',
          '```text\nN01: joint visit / Forum     N02: joint Dakar workshop\n             \\               /\n          source-qualified component register\n             /               \\\n     R1 UNOWAS report       R2 UNOCA report\n             |               |\n     B1 April briefing ----> B2 June briefing\n       new dated update      attributed earlier update\n```','',
          'Solid report/briefing relations represent the explicit links in the edge ledger; the notice-to-register arrows describe the prototype, not verified internal drafting. Council transcript production and other speakers are outside the office briefing workflow.','',
          '## Replay clock and constraints','',
          'The report covers and their reporting windows do not supply verified public-release timestamps. R1 is dated 26 March, covers through 31 March, and prints production marker 020425. R2 is dated 30 May and prints 050625. This demonstration therefore uses 2 April and 5 June as conservative **replay proxies**, not historical release findings. Briefing checkpoints are meeting dates. The notices have 1 February and 28 February mastheads. A current HTML capture cannot prove unchanged 2025 bytes.','']
    for view in views:
        target=next(p for p in d['products'] if p['product_id']==view['product_id'])
        work += ['## '+target['symbol']+' — '+target['owner'], '',target['scope']+'.', '',
                 '**Replay checkpoint:** '+view['checkpoint']+'. **Retained approval:** '+view['approval']+'.', '',
                 '| Component | Published output observation | Earlier support eligible in this replay | Required handling |','|---|---|---|---|']
        for comp in target['components']:
            own=next(o for o in view['observations'] if o['source_id']==view['product_id'] and o['component_id']==comp)
            before=[o for o in view['observations'] if o['source_id']!=view['product_id'] and o['component_id']==comp]
            cites='; '.join(link(ss[o['source_id']],','.join(map(str,o['pages'])))+' ['+o['observation_id']+']' for o in before) or 'None established in the earlier selected corpus; retain as this output’s own addition.'
            work.append('| '+cc[comp]['title']+' | '+own['paraphrase']+' '+link(ss[own['source_id']],','.join(map(str,own['pages'])))+' ['+own['observation_id']+'] | '+cites+' | '+cc[comp]['rule']+' |')
        work += ['', '**Source-qualified drafting example — factual support only:**','']
        if view['product_id'] in {'R1','B1','R2'}:
            work += ['The heads of UNOWAS and UNOCA undertook a joint visit to northern Nigeria, including Bama, in January 2025 and participated in the fifth Lake Chad Basin Governors’ Forum in Maiduguri. The visit start remains source-qualified: the joint notice records 27 January, while the UNOWAS report records 28 January; neither is silently replaced. The two offices also co-organized the Dakar farmer–herder workshop on 26–27 February. These facts can be referenced together without merging the visit, Forum and workshop into one activity. See the cited observations in the table above.','']
            if view['product_id']=='R1':work += ['For the workshop, keep the published **more than 30** qualifier and describe the workplan as adopted, not implemented. Retain the separate CNMC section and the office’s regional assessment. A December 2024 maritime workshop remains prior-period context.','']
            if view['product_id']=='B1':work += ['The April briefing introduces the attributed update that the Niger had **announced** withdrawal from the MNJTF. That is this briefing’s addition in the selected corpus; it is not backfilled into the earlier report or described as a verified completed withdrawal. Political assessment remains with UNOWAS.','']
            if view['product_id']=='R2':work += ['UNOCA’s report adds the separately identifiable best-practice publication and the 8 April planning meeting. Their mention in a later source does not establish their availability to the April 3 briefer. The 29 January representative-attendance date is not substituted for the Forum’s 29–31 January duration. Political assessment remains with UNOCA.','']
        else:
            work += ['In the June 9 briefing, the UNOCA briefer attributes the Niger withdrawal announcement to the UNOWAS briefing of April 3, explicitly referencing S/PV.9890. The packet therefore keeps a link to the dated earlier statement and does not turn the announcement into verified completed withdrawal. UNOCA’s own political assessment and recommendations remain separately prepared and cleared. The three core visit/Forum/workshop blocks are **not inserted** merely because they appear in both reports: they were not selected observations in this briefer’s contribution.','']
        work += ['**Clearance status:** Prototype only. Facts already public are not new joint approval. The source custodian must resolve or authorize qualified wording for disagreements; each office retains final analytical and briefing clearance.','']
    work += ['## What the comparison establishes','',
             'The three core components have nine observed appearances across the two reports and the UNOWAS briefing, not twelve appearances across all four outputs. Mapping those appearances to three canonical IDs is a traceability result, not six eliminated drafting jobs. The UNOCA briefing instead offers a specific cross-briefing attribution. [Component matrix](../data/census_v8/source_component_matrix.csv) · [Evidence ledger](../data/census_v8/claim_ledger.csv) · [Typed edges](../data/census_v8/production_edges.csv).','',
             'The pilot also separates a publication from its launch workshop, a Forum from its containing visit, a dated announcement from legal completion, and shared facts from office-specific judgments. There is no observed staff-time, expenditure, error-rate or service-quality counterfactual.']
    (DOCS/'v8_worked_reporting_cycle.md').write_text('\n'.join(work)+'\n',encoding='utf-8')
    return summary

def check():
    d=read_json(DATA/'pilot_design.json');validate_design(d)
    for s in d['sources']:require(sha(DATA/s['file'])==s['sha256'],'Raw-source hash mismatch')
    for row in read_json(DATA/'frozen_input_manifest.json'):require(sha(ROOT/row['path'])==row['sha256'],'Frozen input changed: '+row['path'])
    views=read_json(DATA/'packet_views.json')
    require({x['product_id'] for x in views}=={'R1','B1','R2','B2'},'View identity mismatch')
    for view in views:validate_packet(d,view)
    require(read_json(DATA/'pilot_summary.json')['source_design_sha256']==sha(DATA/'pilot_design.json'),'Design no longer matches accepted outputs')
    for row in read_json(DATA/'output_manifest.json'):require(sha(ROOT/row['path'])==row['sha256'],'Output hash mismatch: '+row['path'])
    ranks={r['candidate_id']:r['revised_public_rank'] for r in read_csv(ROOT/'data/acabq_2027_ranked_consolidation.csv')}
    overlay=read_csv(DATA/'consolidation_overlay.csv')
    require(len(overlay)==14 and all(r['frozen_rank']==ranks[r['candidate_id']] and r['rank_change']=='none' and r['financial_status']=='not_estimated' for r in overlay),'Rank/finance boundary failed')
    require(read_json(DATA/'operational_status.json')['course_watch']=='paused','Course watch status drift')
    print('V8 OFFLINE CHECK PASSED: six sources; 23 observations; four separate product views; frozen inputs and financial/mandate boundaries intact.')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--build',action='store_true');p.add_argument('--check',action='store_true');args=p.parse_args()
    if args.build:
        d=read_json(DATA/'pilot_design.json');texts=load_texts(d);validate_design(d,texts)
        prior=DATA/'frozen_input_manifest.json'
        if not prior.exists():write_json(prior,baseline_manifest())
        for row in read_json(prior):require(sha(ROOT/row['path'])==row['sha256'],'Frozen input changed before build')
        result=create_outputs(d,texts)
        outputs=[x for x in DATA.rglob('*') if x.is_file() and x.name not in {'output_manifest.json','acceptance_receipt.json'}]
        outputs += sorted(DOCS.glob('v8_*.md'))
        write_json(DATA/'output_manifest.json',[dict(path=x.relative_to(ROOT).as_posix(),sha256=sha(x)) for x in sorted(outputs)])
        print(json.dumps(result,indent=2))
    check()

if __name__=='__main__':main()
