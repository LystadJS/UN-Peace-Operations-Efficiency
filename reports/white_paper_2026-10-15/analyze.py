"""Recompute White Paper data from the retained repository, without changing sources."""
from pathlib import Path
import csv,json,hashlib
from decimal import Decimal as D
from collections import Counter
ROOT=Path(__file__).parent; REPO=ROOT.parents[1]; OUT=ROOT/'analysis';OUT.mkdir(exist_ok=True)
BASE='5c0fdb60eede8a5bb0e7ede9fd551ad4e3b65fb2'
used=set()
def rows(p):
 used.add(p)
 with (REPO/p).open(encoding='utf-8-sig',newline='') as h:return list(csv.DictReader(h))
def js(p):
 used.add(p);return json.loads((REPO/p).read_text())
def total(rs,k):return sum((D(r[k]) for r in rs),D('0'))
fun=rows('data/functional_inventory.csv');cw=rows('data/crosswalk.csv');dl=rows('data/deliverable_inventory.csv');ranks=rows('data/acabq_2027_ranked_consolidation.csv')
ga=rows('data/ga_mission_reconciliation.csv');allga=rows('data/ga_approved_all_missions.csv');comp=rows('data/ga_approved_resource_components.csv')
spm=rows('data/spm_2027_mission_budget.csv');bridge=rows('data/spm_2027_cluster_bridge.csv');eff=rows('data/spm_2027_embedded_efficiencies.csv');sa=rows('data/support_account_units.csv')
adv=rows('data/acabq_2027_cluster_reconciliation.csv');opp=rows('data/public_opportunity_register.csv');gaps=rows('data/owner_review/evidence_gap_register.csv');ptr=js('data/current_research_reference.json');ref=js('data/census_v13/research_reference.json')
frame=js('data/census_v5/index_refresh_summary.json');dedup=js('data/census_v6/audit_summary.json');p8=js('data/census_v8/pilot_summary.json');p9=js('data/census_v9/pilot_summary.json')
assert hashlib.sha256((REPO/ptr['reference_path']).read_bytes()).hexdigest()==ptr['reference_sha256']=='4059dfffbb370c131a27db760487eb425ae302d530c3509eaf3814e70bce2b65'
assert len(fun)==59 and len(cw)==39 and len(dl)==46 and len(ranks)==14 and len(spm)==36 and len(ga)==6
assert total(ga,'ga_approved_maintenance_usd_thousands')==D('4028188.0')
assert total(allga,'approved_maintenance_usd_thousands')==D('4625940.1')
assert total(ga,'sg_proposal_usd_thousands')==D('4120950.7')
assert total(eff,'projected_2027_efficiency_usd_thousands')==D('14692.5')
assert total(spm,'regular_budget_2027_proposed_usd_thousands')==D('419411.9')
assert total(sa,'proposed_2026_27_usd_thousands')==D('95464.1')
assert all(x['recommend_cut_now']=='no' and x['new_net_savings_USD']=='not_estimated' for x in ranks)
assert set(ptr['live_use_gates'].values())=={'BLOCKED_FOR_LIVE_USE'}
FAMILIES=[('Regional strategy and direction','F01 F02 G01 G02 G26',True),('Mediation and good offices','F03 F22 F23',True),('Council reporting and procedure','F06 G03',True),('Military and ceasefire observation','G05 G23 G25',False),('Police and institutional support','G07 G21',False),('Disarmament and reintegration','F12 G08',False),('Security-sector reform','F13 G09',False),('Justice and corrections','F14 G10',False),('Mine action','G11',False),('Protection of civilians','G16',False),('Gender, youth and disability','F16 F17 F26 G14 G15 G22',False),('Electoral support','F05 G27',False),('Peacebuilding institutions and funds','F10 F11',False),('Mission support and transitions','F04 F28 G04 G24',False),('Regional and financial partnerships','F15 F20 F21 F25 G18 G30',True),('Policy, training and evaluation','F18 F24 G06 G12 G13',False),('Data, knowledge and information','F19 G17 G19 G28 G29',True),('Shared management and services','F27 G20',False),('Distinct adjacent political mandates','F07 F08 F09 F29',False)]
lookup={x['function_id']:x for x in fun};assigned=[];family=[]
for name,ids,pilot in FAMILIES:
 ids=ids.split();assigned+=ids
 family.append(dict(family=name,function_ids=';'.join(ids),DPPA=sum(lookup[k]['department']=='DPPA' for k in ids),DPO=sum(lookup[k]['department']=='DPO' for k in ids),selected_pilot_relevance=pilot,owner_validation=False,additional_savings_verified=False))
assert len(assigned)==len(set(assigned))==59 and set(assigned)==set(lookup)
with (OUT/'functional_coverage.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(family[0]));w.writeheader();w.writerows(family)
links=rows('data/census_v7/report_briefing_links_effective.csv');assert len(links)==14
metrics=dict(baseline_commit=BASE,reference_version='13.0',functional_entries=59,department_entries=dict(Counter(x['department'] for x in fun)),crosswalk_pairs=39,relationship_counts=dict(Counter(x['classification'] for x in cw)),deliverables=46,parent_candidates=14,mission_child_cases=9,ga_financed_entities=len(allga),ga_studied_entities=len(ga),ga_maintenance_millions=float(total(ga,'ga_approved_maintenance_usd_thousands')/1000),ga_all_register_millions=float(total(allga,'approved_maintenance_usd_thousands')/1000),ga_requested_millions=float(total(ga,'sg_proposal_usd_thousands')/1000),ga_approved_minus_requested_millions=float((total(ga,'ga_approved_maintenance_usd_thousands')-total(ga,'sg_proposal_usd_thousands'))/1000),ga_inclusive_millions=float(total(ga,'ga_appropriation_usd_thousands')/1000),six_share_of_11_pct=float(total(ga,'ga_approved_maintenance_usd_thousands')/total(allga,'approved_maintenance_usd_thousands')*100),spm_mission_request_millions=float(total(spm,'regular_budget_2027_proposed_usd_thousands')/1000),spm_total_request_millions=422.671,embedded_efficiencies_millions=14.6925,embedded_efficiency_items=len(eff),spm_total_prior_millions=536.145,spm_continuing_change_millions=7.063,spm_closures_millions=121.4731,spm_support_change_millions=.9361,opportunity_classes=dict(Counter(x['decision_class'] for x in opp)),advisory_missions_reviewed=27,advisory_missions_unreconciled=9,source_frame=frame,deduplication=dedup,pilot8=p8,pilot9=p9,first_pass_unchanged=59,first_pass_held=2,amendments_adopted=2,affected_rechecks=2,owner_gap_questions=16,live_trials=0,verified_additional_savings='not_estimated',publication_type='project_synthesis_not_fresh_legal_status_or_operational_census')
(OUT/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
chartdata=dict(metrics=metrics,families=family,missions=ga,all_missions=allga,components=[x for x in comp if x['hierarchy']=='maintenance_top_level'],spm=spm,spm_bridge=bridge,embedded=eff,support=sa,ranks=ranks,opportunities=opp,advisory=adv)
(OUT/'chart_data.json').write_text(json.dumps(chartdata,indent=2)+'\n')
for p in ['data/owner_review/package_contract.json','data/census_v13/adoption_record.json','data/census_v13/reference_lineage.csv','data/census_v10/protocol.json','data/census_v10/activation_status.json','data/consolidation_comprehensive_2027.csv','data/clusterIII_2027_research_priorities.csv','data/un80_implementation_audit.csv','data/mission_function_crosswalk.csv','data/spm_2027_extrabudgetary_coverage.csv','data/spm_2027_source_discrepancies.csv','data/acabq_2027_report_status.csv','data/acabq_2027_main_crosscutting_framework.csv','data/acabq_2027_clusterIII_crosscutting_map.csv']:
 if (REPO/p).exists():used.add(p)
for p in (REPO/'docs').glob('*.md'):
 if p.name in ['methodology.md','initial_findings.md','spm_2027_reconciliation.md','appropriation_spm_consolidation_audit.md','public_only_executive_brief.md','acabq_2027_clusterIII_review.md','v8_consolidation_brief.md','v9_consolidation_brief.md','v10_owner_review_shadow_protocol.md','v13_reference_adoption.md','consolidated_owner_review_decision_memo.md']:used.add(str(p.relative_to(REPO)))
manifest={p:hashlib.sha256((REPO/p).read_bytes()).hexdigest() for p in sorted(used)}
(OUT/'input_manifest.json').write_text(json.dumps({'baseline_commit':BASE,'sources':manifest},indent=2)+'\n')
print(json.dumps({k:v for k,v in metrics.items() if not isinstance(v,(list,dict))},indent=2))
