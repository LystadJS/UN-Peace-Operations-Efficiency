#!/usr/bin/env python3
"""Rebuild the V8 adjudicated design from retained public sources; no network or live work."""
from pathlib import Path
import json,hashlib,csv
r=Path(__file__).resolve().parents[1];d=r/'data/census_v8';d.mkdir(exist_ok=True)
EXPECTED = {
 'S_2025_187.pdf':'5dff319e54f293f5288311cdd4115efdaa5a04409556a1e83ed17b7bfdefcaf9',
 'S_PV_9890.pdf':'6d536f80dc692dafa029282d65b68fcbf9564fbc7ea174a3629fceb4306c9991',
 'S_2025_342.pdf':'2db6110150595b1701b3404f2a7c76555b8b1a94677c94df240b8c2a282ee0dc',
 'S_PV_9931.pdf':'a8db525e9139e5f25b403f7e55b1877446c7c7d747fddfbc15fde2cea99ddc5b',
 'N01.html':'2c376d2a684e09eeb52c5a3b1e8c0f156d63628e19248995937e30c13f3aa921',
 'N02.html':'4ec04c0c38dbaedf4622ea7cb246dac7ee1d9f91f499302e861116733d176333'}
src=[]
def source(sid,file,title,issued,replay,pages,basis,url):
 if hashlib.sha256((d/'sources'/file).read_bytes()).hexdigest()!=EXPECTED[file]:
  raise ValueError('Frozen V8 source changed: '+file)
 src.append(dict(source_id=sid,file='sources/'+file,title=title,issue_or_publication_date=issued,replay_available_from=replay,availability_basis=basis,pages=pages,sha256=hashlib.sha256((d/'sources'/file).read_bytes()).hexdigest(),official_url=url))
source('R1','S_2025_187.pdf','S/2025/187','2025-03-26','2025-04-02',17,'Printed 020425 production marker used only as conservative replay proxy; not independently verified release timestamp','https://docs.un.org/en/S/2025/187')
source('B1','S_PV_9890.pdf','S/PV.9890','2025-04-03','2025-04-03',21,'Meeting date; statement occurrence known, later PDF publication time unverified','https://docs.un.org/en/S/PV.9890')
source('R2','S_2025_342.pdf','S/2025/342','2025-05-30','2025-06-05',15,'Printed 050625 production marker used only as conservative replay proxy; not independently verified release timestamp','https://docs.un.org/en/S/2025/342')
source('B2','S_PV_9931.pdf','S/PV.9931','2025-06-09','2025-06-09',18,'Meeting date; statement occurrence known, later PDF publication time unverified','https://docs.un.org/en/S/PV.9931')
source('N01','N01.html','Joint Nigeria mission public notice','2025-02-01','2025-02-01',1,'Article masthead publication date; current capture does not prove unchanged historical bytes','https://unowas.unmissions.org/en/news/unoca-and-unowas-renew-their-joint-commitment-to-support-stabilization-and')
source('N02','N02.html','Joint Dakar workshop public notice','2025-02-28','2025-02-28',1,'Article masthead and body date; current capture does not prove unchanged historical bytes','https://unowas.unmissions.org/en/news/west-and-central-africa-unowas-and-unoca-pool-their-efforts-to-strengthen-peaceful')
components=[]
for cid,canonical,title,classification,rule in [
 ('P01','EV001','Joint Nigeria/Bama visit','already_joint_input','Retain disputed source-specific start dates; no new visit or eliminated travel claim.'),
 ('P02','EV002','Governors Forum participation','already_joint_input','Forum is nested within the visit, not another field mission; participation day differs from event duration.'),
 ('P03','EV003','Dakar farmer-herder workshop','already_joint_input','Preserve co-organizer roles, greater-than attendance, and adoption versus implementation of the workplan.'),
 ('P04','EV004','UNOCA-led best-practice collection','distinct_knowledge_product','A publication issued at a workshop is not another workshop; early availability is not inferred from event date.'),
 ('P05',None,'Niger MNJTF withdrawal announcement','attributed_time_specific_update','An announcement is not confirmed legal or operational completion; preserve attribution to the dated briefing.'),
 ('P06',None,'CNMC demarcation side-event','protected_function','Same itinerary does not merge the CNMC legal function into the regional good-offices mandate.'),
 ('P07',None,'8 April bilateral planning exchange','existing_coordination_baseline','Existing agreement on joint activities is baseline; no newly invented coordination meeting or saving.'),
 ('P08',None,'17 December 2024 maritime workshop','prewindow_context_control','2025 document date does not move a December 2024 activity into the 2025 event population.'),
 ('P09',None,'UNOWAS political analysis and recommendations','office_specific_analysis','Political judgments and their clearance are retained by the existing office/SG process.'),
 ('P10',None,'UNOCA political analysis and recommendations','office_specific_analysis','Political judgments and their clearance are retained by the existing office/SG process.')]:
 components.append(dict(component_id=cid,canonical_evidence_id=canonical,title=title,classification=classification,rule=rule))
obs=[]
def ob(c,s,p,loc,anchors,text,**values):
 obs.append(dict(observation_id=f'O{len(obs)+1:02}',component_id=c,source_id=s,pages=p,locator=loc,anchors=anchors,paraphrase=text,values=values))
ob('P01','N01',[1],'body paras 1-2',['27 to 31 January 2025','Bama'],'The two Special Representatives undertook a joint Nigeria mission and visited Bama.',event_start='2025-01-27',event_end='2025-01-31',date_scope='whole_visit',role='joint_participants')
ob('P02','N01',[1],'body para 3',['29 to 31 January 2025','Forum'],'Both representatives participated in the Forum in Maiduguri.',event_start='2025-01-29',event_end='2025-01-31',date_scope='whole_forum',role='participants_not_sole_organizers')
ob('P03','N02',[1],'body paras 1 and 4',['26 to 27 February 2025','More than thirty','work plan'],'The two offices co-organized the Dakar workshop; over 30 participated and a community-of-practice workplan was adopted.',event_start='2025-02-26',event_end='2025-02-27',attendance_lower_bound=30,attendance_comparator='>',workplan_stage='adopted_not_verified_implemented',role='co_organizers')
ob('P01','R1',[11],'para 49',['28 to 31 January','Bama'],'The UNOWAS report records a joint northern Nigeria visit including Bama.',event_start='2025-01-28',event_end='2025-01-31',date_scope='whole_visit',role='joint_participants')
ob('P02','R1',[12,13],'para 54',['Governors','reconciliation'],'The UNOWAS report records joint Forum participation and the introduction of reconciliation and reintegration instruments.',date_scope='during_visit_exact_dates_not_stated',role='participants_not_sole_organizers')
ob('P03','R1',[12],'para 53',['26 and 27 February','more than 30','workplan'],'The report records the joint workshop, over 30 participants, and adoption of a workplan.',event_start='2025-02-26',event_end='2025-02-27',attendance_lower_bound=30,attendance_comparator='>',workplan_stage='adopted_not_verified_implemented',role='co_organizers')
ob('P06','R1',[11,12],'para 50',['30 January','Mixed Commission'],'The UNOWAS head acted in his separate CNMC capacity on a border-demarcation side-event.',event_start='2025-01-30',event_end='2025-01-30',role='CNMC_chair',date_scope='side_event')
ob('P08','R1',[13],'para 57',['17 December','UNODC'],'UNOWAS, UNOCA and UNODC facilitated a maritime technical-review workshop in December 2024.',event_start='2024-12-17',event_end='2024-12-17',event_year=2024)
ob('P09','R1',[15],'paras 66-69',['ECOWAS','Observations and recommendations'],'The SG report contains West Africa-specific political judgments and recommendations.',owner='UNOWAS_existing_clearance')
ob('P01','B1',[2],'briefer opening',['Bama','In January'],'The UNOWAS briefer recounts the joint January visit and Bama stop.',date_scope='month_only',role='joint_participants')
ob('P02','B1',[2],'briefer opening',['Governors Forum','mechanisms'],'The UNOWAS briefer recounts Forum participation and regional mechanisms.',date_scope='month_only',role='participants_not_sole_organizers')
ob('P03','B1',[4],'briefer closing thematic section',['In February','farmers and herders'],'The briefer calls the joint February workshop a conference on farmer-herder dynamics.',date_scope='month_only',role='co_organizers')
ob('P05','B1',[2],'briefer Lake Chad update',['announced its withdrawal','Niger'],'As of the 3 April statement, the Niger had announced withdrawal from the MNJTF.',status='announced',as_of='2025-04-03',role='UNOWAS_briefing_attribution')
ob('P09','B1',[3,4],'briefer regional assessment',['Supporting dialogue','UNOWAS'],'The UNOWAS briefer retains office-specific assessment and good-offices priorities.',owner='UNOWAS_existing_clearance')
ob('P01','R2',[12,13],'para 61',['27 to 31 January','Bama'],'The UNOCA report records the joint Nigeria visit with a different start date from R1.',event_start='2025-01-27',event_end='2025-01-31',date_scope='whole_visit',role='joint_participants')
ob('P02','R2',[13],'para 62',['29 January','S/2025/187'],'UNOCA records its representative attending on 29 January and refers readers to the UNOWAS report.',event_start='2025-01-29',event_end='2025-01-29',date_scope='representative_attendance_day_not_forum_duration',role='participant',explicit_reference='R1')
ob('P03','R2',[13],'para 65 first sentence',['26 and 27 February','S/2025/187'],'UNOCA records the joint Dakar workshop and expressly cross-refers to the UNOWAS report.',event_start='2025-02-26',event_end='2025-02-27',role='co_organizers',explicit_reference='R1')
ob('P04','R2',[13],'para 65 second sentence',['collection of best practices','leadership of UNOCA'],'A best-practice collection compiled under UNOCA leadership was published at the workshop.',product_type='publication_not_course',product_lead='UNOCA',event_date_not_publication_availability=True)
ob('P07','R2',[13],'para 67',['8 April','joint regional activities'],'The offices held a planning exchange on 8 April and agreed on joint initiatives.',event_start='2025-04-08',event_end='2025-04-08',stage='coordination_already_observed')
ob('P08','R2',[13],'para 63',['17 December','S/2025/187'],'UNOCA records the December 2024 maritime workshop and cross-refers to UNOWAS.',event_start='2024-12-17',event_end='2024-12-17',event_year=2024,explicit_reference='R1')
ob('P10','R2',[14],'paras 68-70',['political transition in Chad','Observations and recommendations'],'The SG report retains Central Africa-specific judgments and recommendations.',owner='UNOCA_existing_clearance')
ob('P05','B2',[3],'briefer Lake Chad update',['On 3 April','S/PV.9890','announcement'],'The UNOCA briefer explicitly attributes the withdrawal announcement to the earlier UNOWAS briefing.',status='announced',as_of='2025-06-09',role='UNOCA_refers_to_UNOWAS',explicit_reference='B1')
ob('P10','B2',[3,4],'briefer country assessments',['Cameroon','good offices'],'UNOCA retains country-specific electoral, security and good-offices assessments.',owner='UNOCA_existing_clearance')
products=[]
for s,owner,scope in [('R1','UNOWAS','SG report; stated reporting window 1 December 2024 to 31 March 2025'),('B1','UNOWAS','UNOWAS briefer contribution only; not the Council debate or official transcript production'),('R2','UNOCA','SG report; six-month update since 29 November 2024; separate regional mandate'),('B2','UNOCA','UNOCA briefer contribution only; not the Council debate or official transcript production')]:
 ss=next(x for x in src if x['source_id']==s)
 products.append(dict(product_id=s,symbol=ss['title'],owner=owner,replay_checkpoint=ss['replay_available_from'],scope=scope,components=[x['component_id'] for x in obs if x['source_id']==s],approval='existing_office_and_SG_or_briefing_clearance_not_reassigned',deployment_status='retrospective_demo_not_live'))
edges=[
 dict(edge_id='E01',from_source='R1',to_source='B1',component_id=None,kind='explicit_report_presentation',target_pages=[2],anchors=['present the report','S/2025/187']),
 dict(edge_id='E02',from_source='R1',to_source='R2',component_id='P02',kind='explicit_cross_report_referral',target_pages=[13],anchors=['S/2025/187']),
 dict(edge_id='E03',from_source='R1',to_source='R2',component_id='P03',kind='explicit_cross_report_referral',target_pages=[13],anchors=['S/2025/187']),
 dict(edge_id='E04',from_source='R1',to_source='R2',component_id='P08',kind='explicit_cross_report_referral',target_pages=[13],anchors=['S/2025/187']),
 dict(edge_id='E05',from_source='R2',to_source='B2',component_id=None,kind='explicit_report_agenda_association',target_pages=[2],anchors=['S/2025/342']),
 dict(edge_id='E06',from_source='B1',to_source='B2',component_id='P05',kind='explicit_prior_briefing_attribution',target_pages=[3],anchors=['S/PV.9890']),
 dict(edge_id='E07',from_source='N01',to_source='R1',component_id='P01',kind='same_event_corroboration_editorial_direction_unproven',target_pages=[11],anchors=['Bama']),
 dict(edge_id='E08',from_source='N02',to_source='R1',component_id='P03',kind='same_event_corroboration_editorial_direction_unproven',target_pages=[12],anchors=['26 and 27 February'])]
design=dict(version=8,asof='2026-10-15',baseline_commit='bdfe277893914ab9306af751854fd922d3edc731',capture_run=38755500302,capture_artifact_id=11983426429,capture_artifact_sha256='bb0176740682079f11baf6898e8ce47e424b25c2b256b86f277d0d2d99bcb128',sources=src,components=components,observations=obs,products=products,edges=edges,safeguards=dict(mandated_deliverables='unchanged',frozen_rankings='unchanged',retrospective_2027_support='20/32 unchanged',duplicate_paid_service='not_established',incremental_net_savings='not_estimated',staff_hours_saved='not_estimated',live_implementation='not_performed',course_watch='paused_by_user_2026-10-15_not_executed_or_reenabled'),limitations=['Selected public sources, not internal editorial histories or a complete reporting-cycle workload census.','Replay checkpoints are explicit proxies; first public availability and internal availability are unknown.','Reconstruction and negative controls are development demonstrations, not independent human validation or estimated error rates.'])
(d/'pilot_design.json').write_text(json.dumps(design,ensure_ascii=False,indent=2)+'\n')
print('design',len(obs),'obs',len(components),'components',len(edges),'edges',len((d/'pilot_design.json').read_text()))
