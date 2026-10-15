#!/usr/bin/env python3
"""Build/check the additive V10 owner-review protocol. Offline; never starts a trial.

Only retained public sources are read. Templates stay empty. Successful checks
validate this research package, not institutional authority or operational results.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/census_v10'
BASELINE = '65fa21bfd2605c0372f3626deb25f69d0fee1db4'
ASOF = '2026-10-15'
DESIGNS = {
    'V8': ('data/census_v8/pilot_design.json', '730ee69f7272b4719eafa74ac4e320f3503c1a7ecc4847393460dde61b17b51b'),
    'V9': ('data/census_v9/reviewed_design.json', '4878dbbe77344be458ac948ada7de6124c44c8f575351af2835489ff88262dd7'),
}
TEMPLATES = {
 'batches.csv': ['batch_id','case_id','phase','scope_hash','input_snapshot_hash','normal_output_status','shadow_output_status','normal_time_capture_complete','shadow_time_capture_complete','common_time_capture_complete','source_equivalent','task_equivalent','language_equivalent','review_equivalent','prior_exposure_normal','prior_exposure_shadow','contamination','expected_task_roster_ref'],
 'workload.csv': ['segment_id','batch_id','actor_code','office_code','mode','stage','start_utc','end_utc','active_minutes','record_status','minute_basis','incident_id','note_code'],
 'expected_tasks.csv': ['task_id','batch_id','mode','stage','responsible_role_code','disposition','segment_ids','missing_time_reason'],
 'quality_reviews.csv': ['review_id','batch_id','method','product_id','obligation_id','output_hash','source_observation_ids','expected_action','assessor_code','first_pass_status','materiality','qualification_failures','correction_ref','final_status','adjudication_ref'],
 'update_waves.csv': ['wave_id','case_id','scope_version','input_snapshot_hash','source_observation_ids','receiving_product_id','authorized_release_utc','normal_ack_utc','shadow_ack_utc','normal_accepted_update_utc','shadow_accepted_update_utc','closeout_utc','normal_status','shadow_status','comparability','reason_code'],
 'live_claim_enrollment.csv': ['enrollment_id','case_id','wave_id','product_id','component_family','source_ref','source_hash','source_available_utc','source_availability_basis','publisher_or_speaker_class','event_date_precision','observation_cutoff','unit','qualifier','implementation_stage','revision','required_action','enrolled_utc','scope_hash','disposition','reason_code'],
 'owner_reviews.csv': ['review_id','case_id','normal_workflow_ref','existing_control','specific_gap','proposed_change','owner_role_code','disposition','protected_receipt_ref','review_date','scope_hash'],
 'incidents.csv': ['incident_id','case_id','batch_id','trigger_code','detected_utc','affected_obligation_ids','affected_output_hash','scope_of_hold','fallback_status','protected_incident_ref','resumption_authority_ref','resumption_decision','closed_utc'],
 'amendments.csv': ['amendment_id','case_id','prior_protocol_hash','prior_scope_hash','new_scope_hash','reason_code','requested_utc','owner_receipt_refs','effective_wave_id','outcome_seen','earlier_data_preserved'],
}
REQUIRED_ACTIVATION = [
 'owner_a_authorization_ref','owner_b_authorization_ref','normal_workflow_map_ref',
 'specific_gap_ref','target_product_manifest_ref','scope_sha256','input_snapshot_sha256',
 'language_and_task_contract_ref','preparer_roles_ref','reviewer_arrangement_ref',
 'approved_storage_ref','retention_and_staff_notice_ref','fallback_ref',
 'additional_person_minute_ceiling','deadline_safety_buffer_minutes',
 'required_deadline_manifest_ref','measurement_start_utc','measurement_end_utc',
 'incident_and_resumption_route_ref',
]

def check(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def canon(value) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))

def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False)+'\n', encoding='utf-8')

def read_csv(path: Path):
    with path.open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))

def write_csv(path: Path, rows: list[dict], fields=None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        check(bool(rows), f'Empty export without fields: {path}')
        fields = list(rows[0])
    with path.open('w', encoding='utf-8', newline='') as stream:
        w = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)

def load_designs():
    result = {}
    for version, (name, expected) in DESIGNS.items():
        path = ROOT / name
        check(digest(path) == expected, f'Frozen source design changed: {name}')
        result[version] = json.loads(path.read_text(encoding='utf-8'))
    return result

def derive_registers(designs):
    sources, components, scope, products, obligations = [], [], [], [], []
    for version, design in designs.items():
        case = 'SP08P1' if version == 'V8' else 'SP09P1'
        smap = {s['source_id']:s for s in design['sources']}
        cmap = {c['component_id']:c for c in design['components']}
        pids = {p['product_id'] for p in design['products']} if version == 'V8' else set(smap)
        for source in design['sources']:
            rel = (f'data/census_v8/{source["file"]}' if version == 'V8' else source['file'])
            check(digest(ROOT / rel) == source['sha256'], f'Original source hash changed: {rel}')
            sources.append(dict(source_id=f'{version}:{source["source_id"]}', case_id=case,
                file=rel, sha256=source['sha256'],
                source_symbol=source.get('actual_symbol', source.get('title','')),
                url=source.get('official_url',source.get('url','')),
                availability_basis=source.get('availability_basis',source.get('historical_availability',''))))
        for c in design['components']:
            components.append(dict(component_id=f'{version}:{c["component_id"]}',case_id=case,
                title=c['title'],inherited_class=c.get('classification',c.get('baseline_class','')),
                boundary=c.get('rule',c.get('protected_boundary','')), shared_drafting_authorized='false'))
        if version == 'V8':
            for p in design['products']:
                products.append(dict(product_id=f'{version}:{p["product_id"]}',case_id=case,
                    source_symbol=p['symbol'],owner=p['owner'],reference_cycle='V8_worked_sequence',
                    scope=p['scope'],approval=p['approval'],live_product_id='',live_deadline_utc=''))
        else:
            for s in design['sources']:
                products.append(dict(product_id=f'{version}:{s["source_id"]}',case_id=case,
                    source_symbol=s['actual_symbol'],owner=s['owner'],reference_cycle=s['cycle'],
                    scope='selected written-report obligations only; no oral-briefing transfer',
                    approval='retained_owner_chain_no_new_clearance',live_product_id='',live_deadline_utc=''))
        for o in design['observations']:
            s=smap[o['source_id']]; c=cmap[o['component_id']]
            if version == 'V8':
                action = ('retain_owner_specific_boundary' if o['component_id'] in ('P06','P09','P10') else
                          'retain_prewindow_context' if o['component_id']=='P08' else 'source_qualified_support')
                attribution = 'secretariat_report' if o['source_id'].startswith('R') else ('named_briefing_role' if o['source_id'].startswith('B') else 'official_notice')
            else:
                action=o['reuse_policy'];attribution=o['attribution_class']
            oid=f'{version}:{o["observation_id"]}'
            row=dict(observation_id=oid,case_id=case,component_id=f'{version}:{o["component_id"]}',
                source_id=f'{version}:{o["source_id"]}',source_sha256=s['sha256'],
                locator=o['locator'],pages=canon(o['pages']),source_assertion=o.get('paraphrase',o.get('claim','')),
                qualified_values=canon(o['values']),attribution_class=attribution,expected_action=action,
                original_observation_sha256=hashlib.sha256(canon(o).encode()).hexdigest(),
                live_observation='false')
            scope.append(row)
            if o['source_id'] in pids:
                obligations.append(dict(obligation_id='OB:'+oid,case_id=case,observation_id=oid,
                    product_id=f'{version}:{o["source_id"]}',component_id=row['component_id'],
                    required_action=action,denominator_role='fixed_selected_product_obligation',
                    assessment_status='not_assessed_by_owners'))
    return {'source_scope.csv': sources, 'component_scope.csv':components,
            'fixed_source_scope.csv':scope, 'product_scope.csv':products,
            'product_obligations.csv':obligations}

def activation_status(config):
    missing=[key for key in REQUIRED_ACTIVATION if config.get(key) in (None,'')]
    for key in ('additional_person_minute_ceiling','deadline_safety_buffer_minutes'):
        value=config.get(key)
        if value is not None and (not isinstance(value,(int,float)) or isinstance(value,bool) or value<=0):
            missing.append(key+':positive_numeric_required')
    return dict(status='BLOCKED_FOR_LIVE_USE' if missing else 'STRUCTURALLY_COMPLETE_AUTHORITY_UNVERIFIED',
                missing=missing, institutional_authority_verified=False, live_execution_authorized=False)

def protocol():
    return dict(version='10.0',asof=ASOF,baseline_commit=BASELINE,
      design_status='prepared_for_owner_review', authorization_status='not_authorized_for_live_use',
      reference_scope=dict(source_observations=64,components=25,product_obligations=61,product_views=12,
                           interpretation='selected_correlated_reference_units_not_independent_trials'),
      comparison=dict(phase='non_displacing_shadow_only',randomization='not_implemented',
                      primary_unit='case_product_bundle_input_wave',
                      estimate_label='descriptive_process_contrast_not_time_saved',
                      prospective_manifest='required_before_live_comparison; matched_append_only_update_waves'),
      accounting=dict(modes=['normal','shadow','common','setup','evaluation'],
                      normal_process='normal+common',shadow_process='shadow+common',
                      actual_trial='normal+shadow+common+setup+evaluation',
                      missing_time='unknown_not_zero; suppress_complete_totals_and_contrast',
                      repeated_common_inputs='one_actual_segment; no_additive_double_count'),
      safeguards=dict(course_watch='paused_no_checks_run',mandated_outputs='unchanged',
        approval_chains='unchanged',frozen_rankings='unchanged',retrospective_support='20/32 unchanged',
        live_measurements='none',staff_time_saved='not_estimated',incremental_cash_savings='not_estimated',
        protected_data_in_public_repo=False,automatic_start=False),
      case_activation={case:{key:None for key in REQUIRED_ACTIVATION} for case in ['SP08P1','SP09P1']})

def scenario_cards():
    definitions=[
      ('SC01','V8:O01;V8:O04;V8:O15','Nigeria start-date disagreement','Retain 27/28 January as source-specific alternatives; no majority correction.','conflict_preserved'),
      ('SC02','V8:O03;V8:O06','Attendance and workplan stage','Preserve >30 and adopted, not exact 30 or implemented.','inequality_and_stage_preserved'),
      ('SC03','V8:O07;V8:O08;V8:O18','Protected function, year and output grain','Keep CNMC remit, December 2024 context and publication distinct from workshop.','no_scope_or_event_inflation'),
      ('SC04','V8:O13;V8:O22','Attributed withdrawal announcement','Retain speaker/date and announced status; no completed-withdrawal inference.','attribution_preserved'),
      ('SC05','V9:CY009;V9:CY010','Trade export comparators','Retain EUR4.12bn and EUR2.14bn as attributed alternatives; block common ratio.','ratio_not_computed'),
      ('SC06','V9:CY006;V9:CY024;V9:CY036;V9:CY037','Crossing chronology and scope','Keep planned, commenced and completion evidence separate; no additional-crossing completion.','no_implementation_promotion'),
      ('SC07','V9:CY018;V9:CY019;V9:CY023','Party submissions and revision','Preserve party authorship and January revision; no Secretariat endorsement or earlier-version substitution.','owner_and_version_boundary'),
      ('SC08','V9:CY020;V9:CY030;V9:CY038','Cemetery programme scope change','Do not turn approximately 70 mixed-stage sites into completed sites or add differently scoped totals.','scope_version_retained'),
      ('SC09','V9:CY021;V9:CY031;V9:CY041','Utilization denominators','Keep allocation, phase, period and approximate percentage together; no savings inference.','no_false_efficiency_trend'),
      ('SC10','V9:CY005;V9:CY016;V9:CY017;V9:CY028','Nonadditive activity units','Do not equate committee meetings, activities, parties, people or information exchanges.','units_separated'),
      ('SC11','','Synthetic missing clock and shared meeting','Four 20-minute actor segments equal 80 person-minutes; missing time is not zero; common work counted once.','synthetic_accounting_only'),
      ('SC12','','Synthetic faster shadow with a material error','Do not advance on time alone; quarantine incorrect output and preserve failed effort.','safety_overrides_time'),
    ]
    return [dict(scenario_id=i,reference_observations=o,challenge=t,required_response=r,
                 expected_disposition=e,exercise_status='not_run_by_owners') for i,o,t,r,e in definitions]

def protected_paths():
    names=set()
    for v in (8,9):
        names.update(p for p in (ROOT/f'data/census_v{v}').rglob('*') if p.is_file())
        names.update(ROOT.glob(f'docs/v{v}*.md'))
    names.add(ROOT/'data/acabq_2027_ranked_consolidation.csv')
    return sorted(names)

def build():
    designs=load_designs(); registers=derive_registers(designs)
    OUT.mkdir(parents=True,exist_ok=True)
    input_path=OUT/'input_manifest.json'
    if input_path.exists():
        for rel,h in json.loads(input_path.read_text()).items():
            check(digest(ROOT/rel)==h, f'Prior pinned input changed: {rel}')
    else:
        write_json(input_path,{str(p.relative_to(ROOT)):digest(p) for p in protected_paths()})
    for name, rows in registers.items():
        write_csv(OUT/name,rows)
    write_json(OUT/'protocol.json',protocol())
    for name,fields in TEMPLATES.items():
        path=OUT/'templates'/name
        if path.exists():
            check(not read_csv(path), f'Refusing to overwrite filled instrument: {path}')
        write_csv(path,[],fields)
    write_csv(OUT/'scenario_cards.csv',scenario_cards())
    p=protocol()
    write_json(OUT/'activation_status.json',{c:activation_status(x) for c,x in p['case_activation'].items()})
    write_json(OUT/'scope_receipt.json',dict(
        asof=ASOF,baseline_commit=BASELINE,
        source_observations=len(registers['fixed_source_scope.csv']),
        product_obligations=len(registers['product_obligations.csv']),
        source_files=len(registers['source_scope.csv']), components=len(registers['component_scope.csv']),
        product_views=len(registers['product_scope.csv']),empty_instruments=len(TEMPLATES),
        scenario_cards=len(scenario_cards()),pinned_input_files=len(json.loads(input_path.read_text())),
        live_trials_run=0,measured_staff_segments=0,owner_approvals_obtained=0,
        readiness='protocol_prepared_not_live_authorized'))
    covered=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name not in ('output_manifest.json','validation_receipt.json'))
    covered+=sorted(ROOT.glob('docs/v10*.md'))
    write_json(OUT/'output_manifest.json',{str(p.relative_to(ROOT)):digest(p) for p in covered})

def validate():
    designs=load_designs(); expected=derive_registers(designs)
    for name,rows in expected.items():
        check(read_csv(OUT/name)==[{k:str(v) for k,v in r.items()} for r in rows], f'Fixed register drift: {name}')
    counts={name:len(rows) for name,rows in expected.items()}
    check(counts=={'source_scope.csv':14,'component_scope.csv':25,'fixed_source_scope.csv':64,
                   'product_scope.csv':12,'product_obligations.csv':61},'Reference counts changed')
    for filename in ('input_manifest.json','output_manifest.json'):
        for rel,h in json.loads((OUT/filename).read_text()).items():
            check(digest(ROOT/rel)==h, f'Hash changed: {rel}')
    actual=json.loads((OUT/'protocol.json').read_text())
    check(actual==protocol(),'Protocol/gates changed without versioned review')
    for name,fields in TEMPLATES.items():
        path=OUT/'templates'/name
        with path.open(newline='') as stream:
            r=csv.DictReader(stream)
            check(r.fieldnames==fields,f'Instrument header changed: {name}')
            check(not list(r),f'Public template contains measurement/approval rows: {name}')
    check(read_csv(OUT/'scenario_cards.csv')==scenario_cards(),'Scenario outcomes changed')
    for case,conf in actual['case_activation'].items():
        result=activation_status(conf)
        check(result['status']=='BLOCKED_FOR_LIVE_USE' and not result['live_execution_authorized'],f'Live gate opened: {case}')
    obligations=expected['product_obligations.csv']
    check(len({r['obligation_id'] for r in obligations})==61,'Duplicate obligation')
    check(sum(r['case_id']=='SP08P1' for r in obligations)==20,'V8 obligation denominator changed')
    check(sum(r['case_id']=='SP09P1' for r in obligations)==41,'V9 obligation denominator changed')
    return dict(status='PASS_protocol_integrity_and_closed_live_gates',**counts,
                live_trials_run=0,course_checks_run=0,owner_approvals_obtained=0)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    g=ap.add_mutually_exclusive_group(required=True);g.add_argument('--build',action='store_true');g.add_argument('--check',action='store_true')
    args=ap.parse_args()
    if args.build: build()
    print(json.dumps(validate(),indent=2,sort_keys=True))

if __name__=='__main__': main()
