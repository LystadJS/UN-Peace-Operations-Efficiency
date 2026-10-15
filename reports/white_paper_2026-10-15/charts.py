"""Build source-backed White Paper figures. Default Matplotlib colors only."""
from pathlib import Path
import json,textwrap
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).parent; OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
x=json.loads((ROOT/'analysis/chart_data.json').read_text());m=x['metrics']
plt.rcParams.update({'font.size':10,'axes.titlesize':12,'axes.labelsize':10,'figure.dpi':120,'savefig.dpi':240,'svg.fonttype':'none'})
def save(name,fig):
 fig.tight_layout(pad=1.15)
 fig.savefig(OUT/(name+'.png'),bbox_inches='tight');fig.savefig(OUT/(name+'.svg'),bbox_inches='tight');plt.close(fig)
def clean(ax):
 ax.spines[['top','right']].set_visible(False);ax.set_axisbelow(True)
labels=['Documented shared structure','Documented joint process','Planned coordination','Candidate overlap','Complementary, different roles','Distinct mandates'];vals=[7,2,7,9,9,5]
f,a=plt.subplots(figsize=(7.0,3.3));yy=np.arange(6);a.barh(yy,vals);a.set_yticks(yy,labels);a.invert_yaxis();a.set_xlim(0,10.4);a.set_xlabel('Paired comparisons in the 39-row crosswalk')
for y,v in enumerate(vals):a.text(v+.15,y,str(v),va='center')
clean(a);save('01_relationships',f)
f,a=plt.subplots(figsize=(7.1,6.0));fam=x['families'];yy=np.arange(len(fam));d=[r['DPPA'] for r in fam];p=[r['DPO'] for r in fam];a.barh(yy,d,label='DPPA / adjacent offices');a.barh(yy,p,left=d,label='DPO');a.set_yticks(yy,[r['family'] for r in fam]);a.invert_yaxis();a.set_xlabel('Inventory entries, not unique operational tasks');a.set_xlim(0,8);a.legend(loc='lower right',fontsize=8)
for i,(u,v) in enumerate(zip(d,p)):a.text(u+v+.12,i,str(u+v),va='center',fontsize=9)
clean(a);save('02_function_inventory',f)
f,a=plt.subplots(figsize=(7,4.2));rs=sorted(x['all_missions'],key=lambda r:float(r['approved_maintenance_usd_thousands']),reverse=True);vals=[float(r['approved_maintenance_usd_thousands'])/1000 for r in rs];bars=a.barh(np.arange(len(rs)),vals)
for b,r in zip(bars,rs):
 if r['in_original_six_mission_crosswalk']=='no':b.set_hatch('///')
a.set_yticks(np.arange(len(rs)),[r['mission_id'] for r in rs]);a.invert_yaxis();a.set_xlim(0,1250);a.set_xlabel('Approved 2026/27 maintenance requirement, US$ million')
for i,v in enumerate(vals):a.text(v+12,i,f'{v:,.1f}',va='center',fontsize=9)
a.text(.98,.025,'Hatched: headline financing coverage only',transform=a.transAxes,ha='right',fontsize=8);clean(a);save('03_mission_financing',f)
f,a=plt.subplots(figsize=(7,3.7));rs=sorted(x['missions'],key=lambda r:float(r['sg_proposal_usd_thousands']),reverse=True);y=np.arange(6);req=np.array([float(r['sg_proposal_usd_thousands'])/1000 for r in rs]);app=np.array([float(r['ga_approved_maintenance_usd_thousands'])/1000 for r in rs]);a.barh(y-.17,req,height=.32,label='SG request');a.barh(y+.17,app,height=.32,label='GA approved maintenance');a.set_yticks(y,[r['mission_id'] for r in rs]);a.invert_yaxis();a.legend(fontsize=9);a.set_xlabel('US$ million; same maintenance perimeter');a.set_xlim(0,1250)
for i,v in enumerate(app):a.text(v+12,i+.17,f'{v:,.1f}',va='center',fontsize=8)
clean(a);save('04_requests_approvals',f)
f,a=plt.subplots(figsize=(7,3.5));labels=['Military and police','Civilian personnel','Operational requirements'];fields=['ga_approved_military_police_usd_thousands','ga_approved_civilian_usd_thousands','ga_approved_operational_usd_thousands'];y=np.arange(6);left=np.zeros(6)
for label,key in zip(labels,fields):
 vals=np.array([float(r[key])/1000 for r in rs]);a.barh(y,vals,left=left,label=label);left+=vals
a.set_yticks(y,[r['mission_id'] for r in rs]);a.invert_yaxis();a.set_xlabel('GA-approved maintenance, US$ million');a.legend(loc='upper center',bbox_to_anchor=(.5,-.17),ncol=3,fontsize=8);clean(a);save('05_cost_mix',f)
f,a=plt.subplots(figsize=(7,3.5));dif=[float(r['adopted_minus_proposed_usd_thousands'])/1000 for r in rs];a.barh(y,dif);a.set_yticks(y,[r['mission_id'] for r in rs]);a.invert_yaxis();a.set_xlim(-100,8);a.set_xlabel('GA maintenance minus SG request, US$ million')
for i,v in enumerate(dif):a.text(v-1.2,i,f'{v:.3f}',va='center',ha='right',fontsize=9)
clean(a);save('06_budget_variances',f)
f,a=plt.subplots(figsize=(7,2.8));sa=sum(float(r['ga_support_account_share_usd_thousands']) for r in rs)/1000;lb=sum(float(r['ga_logistics_base_share_usd_thousands']) for r in rs)/1000;rc=sum(float(r['ga_regional_service_centre_share_usd_thousands']) for r in rs)/1000
a.barh([0,1,2],[4120.9507,4028.188,4028.188],label='Maintenance')
base=4028.188
for val,label in [(sa,'Support account'),(lb,'UNLB'),(rc,'RSCE')]:a.barh(2,val,left=base,label=label);base+=val
a.set_yticks([0,1,2],['SG request','GA maintenance','GA inclusive appropriation']);a.invert_yaxis();a.set_xlim(0,5100);a.set_xlabel('Six studied entities, US$ million')
for i,v in enumerate([4120.9507,4028.188,4442.1194]):a.text(v+40,i,f'{v:,.3f}',va='center',fontsize=9)
a.legend(loc='upper center',bbox_to_anchor=(.5,-.24),ncol=4,fontsize=8);clean(a);save('07_financing_perimeter',f)
f,a=plt.subplots(figsize=(7.2,3.8));amounts=[536.145,-121.4731,7.063,.9361,422.671];bottom=[0,536.145,414.6719,421.7349,0];height=[536.145,-121.4731,7.063,.9361,422.671];bars=a.bar(np.arange(5),height,bottom=bottom)
for i,(b,v) in enumerate(zip(bars,amounts)):
 top=max(bottom[i],bottom[i]+height[i]);a.text(i,top+10,f'{v:+.3f}' if 0<i<4 else f'{v:.3f}',ha='center',fontsize=10)
for i,end in enumerate([536.145,414.6719,421.7349,422.671]):a.plot([i+.4,i+.6],[end,end],linestyle=':',linewidth=1)
a.set_xticks(np.arange(5),['2026\napproved','Three closure\nbaselines','Continuing\nmission change','RSCE share\nchange','2027 SG\nrequest']);a.set_ylabel('US$ million, calendar-year SPM perimeter');a.set_ylim(0,600);clean(a);save('08_spm_bridge',f)
f,a=plt.subplots(figsize=(7,4));sp=[r for r in x['spm'] if r['cluster_id']=='SPM_CLUSTER_3'];sp.sort(key=lambda r:float(r['regular_budget_2027_proposed_usd_thousands']),reverse=True);names={'UN Special Coordinator for Lebanon (UNSCOL)':'UNSCOL','UN Regional Centre for Preventive Diplomacy in Central Asia':'UNRCCA','Cameroon-Nigeria Mixed Commission':'CNMC','UN Verification Mission in Colombia':'Colombia Verification'};yy=np.arange(9);r26=[float(r['regular_budget_2026_approved_usd_thousands'])/1000 for r in sp];r27=[float(r['regular_budget_2027_proposed_usd_thousands'])/1000 for r in sp];a.scatter(r26,yy-.10,label='2026 approved',s=35);a.scatter(r27,yy+.10,label='2027 SG proposed',s=35);a.set_yticks(yy,[names.get(r['mission_name'],r['mission_name']) for r in sp]);a.invert_yaxis();a.set_xlabel('US$ million; nine continuing Cluster III missions');a.legend(fontsize=9);clean(a);save('09_cluster3',f)
f,a=plt.subplots(figsize=(7,2.5));a.barh(0,27,label='Mission-specific advice reconciled');a.barh(0,9,left=27,label='Not reconciled in project');a.text(13.5,0,'27 missions',ha='center',va='center');a.text(31.5,0,'9',ha='center',va='center');a.set_yticks([0],['36 continuing SPMs']);a.set_xlim(0,36);a.set_xlabel('Coverage of retained Cluster I–III advisory evidence');a.legend(loc='upper center',bbox_to_anchor=(.5,-.27),ncol=2,fontsize=8);clean(a);save('10_advisory_coverage',f)
f,a=plt.subplots(figsize=(7,3.5));names=['UNAMA: staffing measures','UNSMIL: compound contract','Colombia: fixed-wing discontinuation','BINUH: aviation via UNSOH','UNSCOL: UNIFIL assets / supplies','Other embedded measures'];vals=[6.4899,2.63,1.6057,1.4,.4381,14.6925-6.4899-2.63-1.6057-1.4-.4381];a.barh(np.arange(6),vals);a.set_yticks(np.arange(6),names);a.invert_yaxis();a.set_xlabel('US$ million, already included in 2027 SG proposals');a.set_xlim(0,8.3)
for i,v in enumerate(vals):a.text(v+.1,i,f'{v:.4f}',va='center',fontsize=9)
clean(a);save('11_embedded',f)
f,a=plt.subplots(figsize=(7,3.3));names=['Office of the USG','Regional political-operational structure','Office of Military Affairs','Combined mine / police / peace support','Policy, evaluation and training'];vals=[float(r['proposed_2026_27_usd_thousands'])/1000 for r in x['support']];a.barh(np.arange(5),vals);a.set_yticks(np.arange(5),names);a.invert_yaxis();a.set_xlabel('US$ million; DPO support-account allocation only');a.set_xlim(0,34)
for i,v in enumerate(vals):a.text(v+.35,i,f'{v:.3f}',va='center',fontsize=9)
clean(a);save('12_support_allocation',f)
f,a=plt.subplots(figsize=(7,3.1));names=['DPPA political / preventive training','DPO military','DPO police / justice','DPO policy / evaluation / training'];vals=[150,136,50,360];a.barh(np.arange(4),vals);a.set_yticks(np.arange(4),names);a.invert_yaxis();a.set_xlabel('Planned 2027 activity-days, not courses or people');a.set_xlim(0,450)
for i,v in enumerate(vals):a.text(v+5,i,str(v),va='center')
a.text(170,3,'312-day subset\ninside the 360 days',va='center',fontsize=8);clean(a);save('13_training',f)
f,a=plt.subplots(figsize=(7,3.4));vals=[1708,1957,2487,2886];a.bar(np.arange(4),vals);a.set_xticks(np.arange(4),['12 Oct\nframe','13 Oct\nextension','13 Oct\ndeeper frame','15 Oct\nrefresh']);a.set_ylim(0,3300);a.set_ylabel('Exact source URLs, not delivered activities')
for i,v in enumerate(vals):a.text(i,v+50,f'{v:,}',ha='center')
clean(a);save('14_source_frame',f)
f,a=plt.subplots(figsize=(7,2.7));a.barh([0,1],[130,123]);a.set_yticks([0,1],['Local identifiers before reconciliation','Canonical evidence identities']);a.invert_yaxis();a.set_xlim(0,152);a.set_xlabel('Mixed-grain research identities, not event totals');a.text(132,0,'130',va='center');a.text(125,1,'123',va='center');clean(a);save('15_deduplication',f)
f,a=plt.subplots(figsize=(7,2.8));a.barh([0,1],[13,32],label='Factual support / references');a.barh([0,1],[7,9],left=[13,32],label='Boundary preservation');a.set_yticks([0,1],['UNOWAS–UNOCA','Cyprus good offices–UNFICYP']);a.invert_yaxis();a.set_xlim(0,46);a.set_xlabel('Fixed product-specific obligations; not independent samples')
for i,(v,u) in enumerate([(13,7),(32,9)]):a.text(v/2,i,str(v),ha='center',va='center');a.text(v+u/2,i,str(u),ha='center',va='center');a.text(v+u+.7,i,f'{v+u}',va='center')
a.legend(loc='upper center',bbox_to_anchor=(.5,-.24),ncol=2,fontsize=8);clean(a);save('16_pilot_scope',f)
f,a=plt.subplots(figsize=(7,2.8));a.barh([0,1],[4.12,2.14]);a.set_yticks([0,1],['S/2025/447, paragraph 31','S/2025/448, paragraph 24']);a.invert_yaxis();a.set_xlim(0,5.5);a.set_xlabel('Export comparator printed in each report, EUR billion');a.text(4.2,0,'4.12',va='center');a.text(2.22,1,'2.14',va='center');clean(a);save('17_cyprus_comparators',f)
f,a=plt.subplots(figsize=(7,2.8));a.barh(0,59,label='Supported unchanged');a.barh(0,2,left=59,label='Historical amendment holds');a.barh(1,2,label='Separate adopted-version rechecks');a.set_yticks([0,1],['Historical first pass','Post-amendment affected-only check']);a.invert_yaxis();a.set_xlim(0,70);a.set_xlabel('Obligations; distinct review stages, not a new 61/61 score');a.text(30,0,'59',ha='center',va='center');a.text(62,0,'2 held',va='center');a.text(3,1,'2 checked and passed',va='center');a.legend(loc='upper center',bbox_to_anchor=(.5,-.27),ncol=2,fontsize=7.6);clean(a);save('18_reference_history',f)
f,a=plt.subplots(figsize=(7,3.1));labels=['Initial owner review','Before any live shadow','After shadow: substitution authorization','After substitution: cost verification'];vals=[10,4,1,1];a.barh(np.arange(4),vals);a.set_yticks(np.arange(4),labels);a.invert_yaxis();a.set_xlim(0,12);a.set_xlabel('Questions in the 16-entry evidence-gap register')
for i,v in enumerate(vals):a.text(v+.15,i,str(v),va='center')
clean(a);save('19_evidence_gaps',f)
print(f'Created {len(list(OUT.glob("*.png")))} source-backed figures in PNG and SVG.')
