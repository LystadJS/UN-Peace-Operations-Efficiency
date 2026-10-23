#!/usr/bin/env python3
"""Publish evidence-qualified public portfolio views; never adjudicate missing records."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASE_LABELS = ['RSCE charging and retained local work', 'UNIFIL–UNSCOL asset transfer',
 'BINUH–UNSOH aviation and support', 'UNISFA translation', 'UNISFA transferred assets',
 'UNSOS fuel contractor recovery', 'MONUSCO medical insurance', 'UNMISS post changes',
 'Course-level training', 'DPPA–DPO regional functions', 'UNOWAS–UNOCA reporting',
 'Cyprus reporting', 'UNIFIL residual transition liabilities', 'Existing joint structures']

def read(root, path):
    return json.loads((root/path).read_text())

def build(root=ROOT):
    paths = ['data/reforms/baseline_release.json', 'data/reforms/unga80_actions.json',
      'data/reforms/unga81_actions.json', 'data/portfolio/entities.json',
      'data/portfolio/dataset_contracts.json', 'data/portfolio/coverage_matrix.json',
      'data/portfolio/financial_baseline.json', 'data/portfolio/interventions.json',
      'data/portfolio/benefit_pools.json', 'data/portfolio/verified_benefit_ledger.json',
      'data/adjudications/execution_gates.json', 'data/realization/implementation_gates.json',
      'data/pilots/charters.json', 'data/pilots/thresholds.json',
      'data/pilots/rehearsal_receipt.json', 'data/pilots/request_status.json']
    paths += [f'data/cases/C{i:02}.json' for i in range(1,15)]
    missing = [p for p in paths if not (root/p).is_file()]
    if missing:
        raise ValueError('Missing portfolio dependencies: '+', '.join(missing))
    cases = []
    for i, label in enumerate(CASE_LABELS, 1):
        path = f'data/cases/C{i:02}.json'
        dossier = read(root,path)
        # Public case dossiers are research packets, never observations of delivery.
        if dossier.get('candidate_state') != 'SCREENING_CANDIDATE' or dossier.get('disposition') != 'BLOCKED_PENDING_EVIDENCE':
            raise ValueError(f'Case disposition changed; substantive release review required: {path}')
        benefits=dossier.get('benefits',{})
        if dossier.get('financial_validation') != 'NOT_PERFORMED' or benefits.get('status') != 'NOT_ESTIMATED' or any(
           key not in benefits or benefits[key] is not None for key in ('cashable_saving','realized_saving','capacity_gain','recovery','cost_avoidance')):
            raise ValueError(f'Case financial facts changed; substantive release review required: {path}')
        if dossier.get('accountable_owner') is not None or dossier.get('owner_confirmation_status') != 'NOT_OBTAINED' or dossier.get('evidence_request_sent') is not False or dossier.get('implementation_authority') != 'NOT_ESTABLISHED_BY_REPOSITORY':
            raise ValueError(f'Case authority facts changed; substantive release review required: {path}')
        cases.append({'case_id': f'C{i:02}', 'label': label, 'dossier': path,
          'candidate_state': 'SCREENING_CANDIDATE', 'disposition': 'BLOCKED_PENDING_EVIDENCE',
          'substantive_adjudication_completed': False, 'verified_benefit': None,
          'next_decision': 'Obtain authorized minimum evidence and predeclare observation thresholds.'})
    executions=read(root,'data/adjudications/execution_gates.json')
    ledger=read(root,'data/portfolio/verified_benefit_ledger.json')
    realization=read(root,'data/realization/implementation_gates.json')
    interventions=read(root,'data/portfolio/interventions.json')
    rehearsal=read(root,'data/pilots/rehearsal_receipt.json')
    requests=read(root,'data/pilots/request_status.json')
    charters=read(root,'data/pilots/charters.json')
    if executions.get('actual_operational_audits_completed') != 0 or any(
       r.get('execution_status') != 'BLOCKED_NOT_EXECUTED' or r.get('substantive_audit_completed') is not False
       for r in executions.get('records',[])) or len(executions.get('records',[])) != 21:
        raise ValueError('Execution facts changed; substantive release review required')
    totals=ledger.get('reconciliation',{})
    if ledger.get('entries') != [] or totals.get('recognized_records') != 0 or totals.get('headline_realized_savings_usd') is not None or any(
       value is not None for value in totals.get('class_totals_usd',{}).values()) or realization.get('approved_interventions') != [] or realization.get('executions') != [] or realization.get('institutional_approval_obtained') is not False:
        raise ValueError('Benefit or implementation facts changed; substantive release review required')
    if len(interventions.get('interventions',[])) != 14 or any(
       r.get('candidate_state') != 'SCREENING_CANDIDATE' or r.get('benefit_amount') is not None or r.get('financial_validation') != 'NOT_PERFORMED'
       for r in interventions.get('interventions',[])) or interventions.get('portfolio_benefit_total') is not None:
        raise ValueError('Normalized intervention facts changed; substantive release review required')
    if any(rehearsal.get(key) != 0 for key in ('actual_financial_validations','actual_operational_trials','actual_owner_approvals')) or rehearsal.get('actual_savings_amount') is not None or any(
       rehearsal.get('actual_preparation_status',{}).get(key) != 0 for key in ('actual_pilots_authorized','actual_pilots_started')):
        raise ValueError('Actual rehearsal boundary changed; substantive release review required')
    if any(requests.get('counts',{}).get(key) != 0 for key in ('requests_sent','responses_obtained','accepted_owners','approved_collections')) or len(requests.get('requests',[])) != 6 or any(
       r.get('dispatch_status') != 'NOT_SENT' or r.get('response_status') != 'NOT_OBTAINED' or r.get('accepted_owner') is not None
       for r in requests.get('requests',[])) or any(r.get('dispatch_status') != 'NOT_SENT' or r.get('response_status') != 'NOT_OBTAINED' or r.get('approved_collection') is not False for r in requests.get('case_tracks',[])):
        raise ValueError('Request facts changed; substantive release review required')
    if charters.get('institutional_approval') is not False or charters.get('live_trial_started') is not False:
        raise ValueError('Pilot authorization changed; substantive release review required')
    return {'schema_version':1, 'release_id':'UNPO-PUBLIC-VALIDATION-BASELINE-2026-10-23',
      'cutoff':'2026-10-23', 'release_class':'PUBLIC_VALIDATION_BASELINE',
      'institutional_approval':'NOT_OBTAINED', 'decision_grade_portfolio':'BLOCKED',
      'cases':cases, 'substantive_operational_adjudications':0,
      'minimum_substantive_operational_adjudications':3,
      'observed_service_types':0, 'minimum_service_types':2,
      'verified_benefits':{'cashable_saving':None,'realized_saving':None,
        'cost_avoidance':None,'recovery':None,'capacity_gain':None,
        'interpretation':'NOT_ESTIMATED; an empty verified ledger does not establish zero waste or zero possible benefit.'},
      'completion_gates':[
        {'gate':1,'status':'PARTIAL','blockers':['Instrument population and applicability review incomplete.',
          'Entity lifecycle, mandate links and accepted ownership not fully verified.']},
        {'gate':2,'status':'PARTIAL','blockers':['Actual baseline-dependent thresholds remain unset.',
          'Evidence intake/authority not obtained; synthetic rehearsals are software tests only.']},
        {'gate':3,'status':'BLOCKED','blockers':['No substantive operational audits completed.',
          'No accepted operational/financial adjudications or independent institutional review.']},
        {'gate':4,'status':'BLOCKED','blockers':['No intervention has institutional approval or observed realization.',
          'No accepted substantive no-change adjudication.']}],
      'constraints':{'SP08P1':'BLOCKED_FOR_LIVE_USE','SP09P1':'BLOCKED_FOR_LIVE_USE',
        'course_watch':'PAUSED','external_requests':'NOT_SENT','operational_execution':'NOT_AUTHORIZED'},
      'source_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in sorted(paths)},
      'limitations':['Public and synthetic work does not replace internal ledgers, workloads, service outcomes or owner authority.',
        'UNGA80 actions are selected provisions; UNGA81 review is bounded and is not an exhaustive legal determination.',
        'Agent review is software/research review, not independent UN institutional or professional audit assurance.']}

def render(data):
    rows='\n'.join(f'| [{r["case_id"]}](cases/{r["case_id"]}.md) | {r["label"]} | Evidence blocked |'
                    for r in data['cases'])
    return f'''# Public decision-portfolio baseline

**23 October 2026 — Validation framework delivered; operational decision portfolio blocked.**

The project can now trace public concerns through authority, cost boundaries, evidence contracts, safeguards and reproducible analytical controls. It has completed **zero substantive operational adjudications**; the required minimum is three across two service types. All fourteen cases remain screening candidates. No verified monetary or capacity benefit is estimated.

The [reform view](reform_compliance_view.md) separates adopted provisions, advice, proposals and management reports. Selected UNGA80 texts were reviewed; UNGA81 coverage remains bounded. Neither an A/81 document symbol nor a management announcement establishes adoption, compliance or realized benefit.

| Case | Decision scope | Disposition |
| --- | --- | --- |
{rows}

## Commander's next decision

Prioritize authorized minimum-data access for RSCE charging, UNIFIL–UNSCOL assets and BINUH–UNSOH aviation/support. Proposed custodian roles are listed in the [request contracts](../data/evidence_requests/). Requests are drafted and **not sent**; no custodian has accepted ownership. Secure handling belongs in approved systems under the [intake rules](secure_evidence_intake.md). Public GitHub is not an evidence dropbox.

Freeze case-specific observation periods and numerical safeguards after baseline assessment and before outcome review. Reconcile each actual baseline; test a feasible alternative; adjudicate the operational and financial evidence separately. Retain an effective process when warranted. Evidence-unavailable closure cannot substitute for these audits.

## Completion and limits

Foundation and validation-system gates are partial. Decision-portfolio and realization gates remain blocked. Known gaps include authoritative instrument-population completeness, entity lifecycle/mandate verification, internal cost objects, actual workloads/outcomes, accepted owners and independent institutional review. The [execution receipts](operational_adjudication_blockers.md) and [realization gates](realization_workflow.md) record downstream steps as blocked, not completed.

The verified-benefit ledger is empty with **unknown amounts**, not a zero-waste conclusion. Embedded efficiencies and closures are baseline effects; internal transfers are not full-system benefits. Cashable savings require financial validation; realized savings require implementation, observation, net-cost reconciliation and acceptance.

Both reporting live-use gates remain closed and the course watch remains paused. Synthetic rehearsals test software behavior only. No operational change, external request or intervention has been executed by this release.

Machine-readable scope, input hashes and completion gates: [portfolio release](../data/portfolio/public_portfolio.json). [Current status](current_status.md) remains the canonical combined readout.
'''

def outputs(root=ROOT):
    data=build(root)
    return {'data/portfolio/public_portfolio.json':json.dumps(data,indent=2,ensure_ascii=False)+'\n',
            'docs/decision_portfolio.md':render(data)}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    if args.write and args.check: parser.error('choose write or check')
    for name,body in outputs().items():
        p=ROOT/name
        if args.write: p.parent.mkdir(parents=True,exist_ok=True);p.write_text(body)
        elif not p.exists() or p.read_text()!=body: raise SystemExit('FAIL: stale '+name)
    print('PASS: public portfolio; zero operational adjudications, unknown benefits, explicit blocked gates')
if __name__=='__main__': main()
