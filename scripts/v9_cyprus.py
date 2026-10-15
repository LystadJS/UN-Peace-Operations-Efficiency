#!/usr/bin/env python3
"""V9 Cyprus source/representation transfer test. No network, live trial, or savings.

--build generates additive views from reviewed_design.json and original PDFs.
--check verifies retained manifests without source re-extraction.
--test re-extracts with two parsers and executes deliberate corruption fixtures.
Requires pypdf==5.9.0; --test additionally uses PyMuPDF==1.26.7.
"""
from __future__ import annotations
import argparse,copy,csv,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data/census_v9'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,obj):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok,msg):
 if not ok:raise ValueError(msg)
def norm(t):return re.sub('[^a-z0-9]','',t.lower())
def csvout(p,rows):
 require(bool(rows),'Empty export');keys=list(dict.fromkeys(k for row in rows for k in row))
 with p.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
  for row in rows:w.writerow({k:json.dumps(v,ensure_ascii=False,sort_keys=True) if isinstance(v,(dict,list)) else v for k,v in row.items()})
def load_sources(d,second=False):
 from pypdf import PdfReader
 result={}
 for s in d['sources']:
  p=ROOT/s['file'];require(sha(p)==s['sha256'],'Source bytes changed '+s['source_id'])
  if second:
   import fitz
   doc=fitz.open(p);pages=[page.get_text() for page in doc]
  else:pages=[page.extract_text() or '' for page in PdfReader(p).pages]
  require(len(pages)==s['pages'],'Page count changed')
  require(norm(s['actual_symbol']) in norm(pages[0]),'Wrong cover symbol')
  require('Original: English' in pages[0],'Wrong language')
  result[s['source_id']]=pages
 return result

def validate(d,texts=None):
 ss={s['source_id']:s for s in d['sources']};cs={c['component_id']:c for c in d['components']}
 require(len(ss)==8 and len(cs)==15 and len(d['observations'])==41,'Declared frame changed')
 require({s['owner'] for s in ss.values()}=={'UNFICYP','Good offices'},'Ownership lost')
 require(len({o['observation_id'] for o in d['observations']})==41,'Duplicate claim identity')
 for o in d['observations']:
  require(o['source_id'] in ss and o['component_id'] in cs,'Orphan observation')
  s=ss[o['source_id']];require(all(1<=p<=s['pages'] for p in o['pages']),'Invalid page')
  if o['attribution_class']=='party_submission_metadata':require(o['reuse_policy']=='party_attribution_only' and not o['values']['secretariat_endorsement'],'Party claim laundering')
  else:require(max(o['pages'])<s['annex_start'],'Annex passed as Secretariat body')
  if texts is not None:
   t=norm(' '.join(texts[s['source_id']][p-1] for p in o['pages']))
   require(all(norm(a) in t for a in o['anchors']),'Anchor failure '+o['observation_id'])
 guard=d['safeguards']
 for k in ('mandated_products','approval_chains','rankings','source_tables'):require(guard[k]=='unchanged','Protected boundary changed')
 for k in ('staff_hours_saved','incremental_net_savings','global_new_event_total'):require(guard[k]=='not_estimated','Unsupported estimate')
 require(guard['course_watch']=='paused_no_checks_run' and guard['live_trial']=='not_run','Activity invented')
 require(next(s for s in ss.values() if s['source_id']=='G0')['actual_symbol']=='S/2025/7/Rev.1','Revision hidden')


def view(d,sid):
 source=next(s for s in d['sources'] if s['source_id']==sid)
 own=[copy.deepcopy(o) for o in d['observations'] if o['source_id']==sid]
 own_components={o['component_id'] for o in own}
 partner=next(s for s in d['sources'] if s['cycle']==source['cycle'] and s['source_id']!=sid)
 context=[copy.deepcopy(o) for o in d['observations'] if o['source_id']==partner['source_id'] and o['component_id'] in own_components and o['reuse_policy'] in {'shared_fact','source_qualified_reference'}]
 trade=[o for o in own+context if o['component_id']=='K06']
 comparators=sorted({o['values']['exports_eur_billion'] for o in trade})
 return dict(product_id=sid,actual_symbol=source['actual_symbol'],owner=source['owner'],cycle=source['cycle'],own_published_observations=own,companion_context_not_published_claims=context,
  mode='retrospective_cycle_view_not_historical_availability_replay',approval='retained_owner_chain_no_new_clearance',
  export_comparator_values_eur_billion=comparators,export_comparator_conflict=len(comparators)>1,trade_ratio_permitted=False,
  staff_hours_saved='not_estimated',incremental_net_savings='not_estimated')

def check_view(d,v):require(v==view(d,v['product_id']),'View contract changed')

def references(d,texts):
 rows=[]
 for s in d['sources']:
  t=next(t for t in d['sources'] if t['cycle']==s['cycle'] and t['source_id']!=s['source_id'])
  pages=[];count=0
  for i,txt in enumerate(texts[s['source_id']][:s['annex_start']-1],1):
   n=len(re.findall(re.escape(t['requested_symbol'])+r'(?!\d)',re.sub(r'\s+','',txt)))
   if n:pages.append(i);count+=n
  rows.append(dict(from_source=s['source_id'],to_requested_symbol=t['requested_symbol'],reviewed_target_version=t['actual_symbol'],cycle=s['cycle'],occurrences=count,pages=pages,
   edge='explicit_report_referral' if count else 'no_explicit_companion_referral_in_reviewed_main_text',
   editorial_dependency='not_established',duplicate_paid_production='not_established'))
 return rows

def frozen_inputs():
 out=[]
 for folder in ('data','docs','scripts','tests'):
  for p in (ROOT/folder).rglob('*'):
   rel=p.relative_to(ROOT).as_posix()
   if not p.is_file() or '__pycache__' in rel or '/census_v9/' in rel or 'v9_' in p.name:continue
   out.append(dict(path=rel,sha256=sha(p)))
 return sorted(out,key=lambda x:x['path'])

def generated_manifest():
 paths=[p for p in DATA.rglob('*') if p.is_file() and p.name not in {'output_manifest.json','acceptance_receipt.json'}]
 paths += list((ROOT/'docs').glob('v9_*.md'))
 return [dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(paths)]

def build():
 d=read(DATA/'reviewed_design.json');texts=load_sources(d);validate(d,texts)
 if not (DATA/'frozen_input_manifest.json').exists():save(DATA/'frozen_input_manifest.json',frozen_inputs())
 vv=[view(d,s['source_id']) for s in d['sources']];rr=references(d,texts)
 for v in vv:check_view(d,v)
 save(DATA/'product_views.json',vv);save(DATA/'source_text.json',texts)
 csvout(DATA/'source_manifest.csv',d['sources']);csvout(DATA/'claim_ledger.csv',d['observations']);csvout(DATA/'explicit_referrals.csv',rr)
 csvout(DATA/'component_matrix.csv',[dict(c,**{s['source_id']:';'.join(o['observation_id'] for o in d['observations'] if o['source_id']==s['source_id'] and o['component_id']==c['component_id']) or 'not_selected' for s in d['sources']}) for c in d['components']])
 ranks=list(csv.DictReader((ROOT/'data/acabq_2027_ranked_consolidation.csv').open(encoding='utf-8-sig')))
 overlay=[]
 for r in ranks:
  cid=r['candidate_id'];status={'C02':'SP09P1_second_context_source_version_test','C05':'SP09P1_existing_system_enabler_not_additive','C09':'SP08P1_UNOWAS_UNOCA_result_retained_not_a_new_Cyprus_regional_case','C16':'existing_support_comparison_only_not_piloted'}.get(cid,'not_reassessed')
  overlay.append(dict(candidate_id=cid,frozen_rank=r['revised_public_rank'],scope=r['scope'],v9_disposition=status,rank_change='none',financial_status='not_estimated',distinct_new_cost_pool='not_established'))
 csvout(DATA/'consolidation_overlay.csv',overlay)
 # Keep existing metric definitions as the comparison backbone, adding only Cyprus-specific controls.
 original=list(csv.DictReader((ROOT/'data/census_v8/measurement_plan.csv').open()))
 csvout(DATA/'measurement_plan.csv',[dict(x,cyprus_application='Protect annex attribution, cycle-specific implementation stages, units and budget denominators; compare against current jointly supported workflow.') for x in original])
 (DATA/'workload_log_template.csv').write_text('cycle,office,component_id,work_step,minutes,process_arm,source_reference,scope_comparable,clearance_status\n')
 summary=dict(version=9,asof=d['asof'],baseline_commit=d['baseline_commit'],original_reports=8,original_pdf_pages=sum(s['pages'] for s in d['sources']),reporting_cycles=4,selected_components=15,source_observations=41,primary_cycle_observations=21,product_views=len(vv),directed_referral_edges=sum(r['occurrences']>0 for r in rr),referral_occurrences=sum(r['occurrences'] for r in rr),reciprocal_cycles=['3'],source_design_sha256=sha(DATA/'reviewed_design.json'),source_coverage='selected main-body claims and annex headings; not full substantive review of all pages',transcript_transfer='not_tested',transfer_result='representation_and_controls_transfer; operational_incremental_benefit_unverified',safeguards=d['safeguards'])
 save(DATA/'pilot_summary.json',summary)
 # Per-output support sheets: companion context never silently becomes a published claim.
 ss={s['source_id']:s for s in d['sources']};lines=['# V9 worked Cyprus reporting-cycle support sheets','','Retrospective reconstruction. These are research support sheets, not issued UN documents or authorized drafts. Same-cycle companion context is shown for review, not presumed available before release. Other cycles are not backfilled.','']
 for v in vv:
  lines += ['## '+v['actual_symbol']+' — '+v['owner'],'','### Selected observations in the published product','']
  for o in v['own_published_observations']:
   s=ss[o['source_id']];lines.append(f"**{o['observation_id']} / {o['component_id']} — {o['locator']}**, pp. {','.join(map(str,o['pages']))}: {o['claim']} [Original]({s['url']}). Values: `{json.dumps(o['values'],ensure_ascii=False,sort_keys=True)}`. Policy: **{o['reuse_policy']}**.")
  lines += ['','### Companion context, not an added published observation','']
  for o in v['companion_context_not_published_claims']:lines.append(f"{o['observation_id']} — {o['claim']} ({ss[o['source_id']]['actual_symbol']}, {o['locator']}).")
  if not v['companion_context_not_published_claims']:lines.append('No eligible selected companion observation is inserted. This is not proof that no other reusable information exists.')
  lines += ['',f"Export comparator conflict: **{v['export_comparator_conflict']}**; values retained: `{v['export_comparator_values_eur_billion']}`; no common ratio released.",'']
 (ROOT/'docs/v9_worked_cyprus_cycle.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 save(DATA/'output_manifest.json',generated_manifest());print(json.dumps(summary,indent=2))

def check():
 d=read(DATA/'reviewed_design.json');validate(d)
 for s in d['sources']:require(sha(ROOT/s['file'])==s['sha256'],'Source hash mismatch')
 for row in read(DATA/'frozen_input_manifest.json'):require(sha(ROOT/row['path'])==row['sha256'],'Earlier file changed: '+row['path'])
 for row in read(DATA/'output_manifest.json'):require(sha(ROOT/row['path'])==row['sha256'],'Output changed: '+row['path'])
 for v in read(DATA/'product_views.json'):check_view(d,v)
 require(len(read(DATA/'product_views.json'))==8,'Output product loss')
 ranks={r['candidate_id']:r['revised_public_rank'] for r in csv.DictReader((ROOT/'data/acabq_2027_ranked_consolidation.csv').open(encoding='utf-8-sig'))}
 overlay=list(csv.DictReader((DATA/'consolidation_overlay.csv').open()))
 require(len(overlay)==14 and all(r['frozen_rank']==ranks[r['candidate_id']] and r['rank_change']=='none' and r['financial_status']=='not_estimated' for r in overlay),'Rank/financial boundary failed')
 print('V9 offline invariants and frozen-file checks PASS')

def test():
 d=read(DATA/'reviewed_design.json');first=load_sources(d);second=load_sources(d,True);validate(d,first);validate(d,second)
 vv={v['product_id']:v for v in read(DATA/'product_views.json')};out=[]
 def good(name,ok):
  require(ok,name);out.append(dict(test=name,status='PASS',kind='independent_assertion'))
 good('8 originals have 146 pages',sum(len(t) for t in second.values())==146)
 good('4 retained report pairs',len(vv)==8 and {v['cycle'] for v in vv.values()}=={'0','1','2','3'})
 good('all 41 claims pass second-parser anchors',len(d['observations'])==41)
 for sid in ('P1','G1'):good(sid+' preserves conflicting export denominators',vv[sid]['export_comparator_values_eur_billion']==[2.14,4.12] and vv[sid]['export_comparator_conflict'])
 for sid,v in vv.items():
  good(sid+' has no later/earlier-cycle claim injection',all(o['source_id'][-1]==v['cycle'] for o in v['own_published_observations']+v['companion_context_not_published_claims']))
  good(sid+' does not import party submissions',all(o['attribution_class']=='secretariat_report' for o in v['companion_context_not_published_claims']))
 def own(sid,component):return next(o for o in vv[sid]['own_published_observations'] if o['component_id']==component)
 good('planned crossing start remains Sept 2025',own('P1','K04')['values']['planned_month']=='2025-09' and own('P1','K04')['values']['actual_start'] is None)
 good('reported actual start remains Dec 2025',own('P2','K04')['values']['actual_start_month']=='2025-12')
 good('February completion-marking event is not an invented exact completion date',own('G3','K04')['values']['completion_marking_event_month']=='2026-02' and own('G3','K04')['values']['actual_completion_date'] is None)
 good('new crossings not inferred from enlargement',own('G3','K05')['values']['stage']=='not_implemented')
 good('expanded cemetery portfolio retains mixed stages',own('G3','K13')['values']['stage']=='mixed_completed_ongoing_preparation')
 good('2025 issue retains 2024 event period',own('G0','K10')['values']['activity_year']==2024)
 good('utilization allocation change is not a performance trend',own('G1','K15')['values']['allocation_eur']==1000000 and own('G3','K15')['values']['allocation_eur']==1500000 and own('G2','K15')['values']['allocation_eur'] is None)
 rr=references(d,second);good('5 directed references and 15 occurrences',sum(r['occurrences']>0 for r in rr)==5 and sum(r['occurrences'] for r in rr)==15)
 good('July 2026 reciprocal referrals',all(next(r for r in rr if r['from_source']==s)['occurrences']==1 for s in ('P3','G3')))
 # Equality-to-contract mutation tests supplement, not replace, independent source assertions above.
 def reject(name,sid,mutate):
  v=copy.deepcopy(vv[sid]);mutate(v)
  try:check_view(d,v)
  except ValueError:out.append(dict(test=name,status='REJECTED_AS_EXPECTED',kind='constructed_corruption'))
  else:raise AssertionError('Unsafe mutation accepted '+name)
 def change(c,key,val):return lambda v:next(o for o in v['own_published_observations'] if o['component_id']==c)['values'].__setitem__(key,val)
 reject('normalize export denominator','G1',change('K06','exports_eur_billion',4.12))
 reject('hide trade conflict','P1',lambda v:v.__setitem__('export_comparator_conflict',False))
 reject('compute unqualified common ratio','G1',lambda v:v.__setitem__('trade_ratio_permitted',True))
 reject('planned crossing becomes completed','P1',change('K04','stage','completed'))
 reject('new crossings inferred open','G3',change('K05','stage','completed'))
 reject('70 mixed sites become 70 completed sites','G3',change('K13','stage','all_completed'))
 reject('130 lower-bound meetings become exact','G1',change('K03','meetings_comparator','='))
 reject('18 parties become 18 persons','G1',change('K07','unit','people'))
 reject('annex statement becomes Secretariat finding','G1',change('K12','secretariat_endorsement',True))
 reject('revision qualifier lost','G0',lambda v:v.__setitem__('actual_symbol','S/2025/7'))
 reject('2024 activity redated to 2025','G0',change('K10','activity_year',2025))
 reject('future completion backfilled','P1',lambda v:v['companion_context_not_published_claims'].append(copy.deepcopy(own('G3','K04'))))
 reject('unknown allocation filled from old budget','G2',change('K15','allocation_eur',1000000))
 reject('separate owner reassigned','P1',lambda v:v.__setitem__('owner','Good offices'))
 reject('common final clearance invented','G1',lambda v:v.__setitem__('approval','joint_final_clearance'))
 reject('savings invented','P1',lambda v:v.__setitem__('incremental_net_savings',100))
 reject('staff hours invented','P1',lambda v:v.__setitem__('staff_hours_saved',2))
 reject('unknown exact completion day invented','G3',change('K04','actual_completion_date','2026-02-01'))
 result=dict(status='PASS',checks=len(out),constructed_corruptions_rejected=sum(x['kind']=='constructed_corruption' for x in out),independent_assertions=sum(x['kind']=='independent_assertion' for x in out),pdf_sources_rechecked=8,source_anchor_observations_checked_by_each_parser=41,results=out,limits='Source/representation checks; not independent human clearance, an operational error rate or productivity/savings evidence.')
 save(DATA/'acceptance_receipt.json',result);print(json.dumps({k:v for k,v in result.items() if k!='results'},indent=2))

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--build',action='store_true');p.add_argument('--check',action='store_true');p.add_argument('--test',action='store_true');args=p.parse_args()
 if args.build:build()
 if args.check:check()
 if args.test:test()
if __name__=='__main__':main()
