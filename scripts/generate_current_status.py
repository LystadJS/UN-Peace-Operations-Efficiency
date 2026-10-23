#!/usr/bin/env python3
"""Generate a scoped project-status view from retained evidence and canonical controls."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON = 'metadata/current_status.json'
OUTPUT_MD = 'docs/current_status.md'
DESIGN_DATE = '2026-10-23'
BASE_INPUTS = [
    'metadata/canonical_manifest.json',
    'data/issues/current_issues.json',
    'metadata/issue_migration_receipt.json',
    'data/current_research_reference.json',
    'data/census_v13/summary.json',
    'data/census_v13/adoption_record.json',
    'data/census_v13/reference_lineage.csv',
    'data/census_v11/obligation_reviews.csv',
    'data/census_v7/final_summary.json',
    'data/owner_review/package_contract.json',
    'data/owner_review/evidence_gap_register.csv',
    'data/ga_mission_reconciliation.csv',
    'data/ga_approved_all_missions.csv',
    'data/spm_2027_mission_budget.csv',
    'data/spm_2027_cluster_bridge.csv',
    'data/spm_2027_financing_controls.csv',
    'data/spm_2027_embedded_efficiencies.csv',
    'data/acabq_2027_mission_reconciliation.csv',
    'data/portfolio/public_portfolio.json',
    'data/reforms/baseline_release.json',
    'data/priority_cases/progress.json',
    'data/public_assessment/portfolio.json',
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(root, path):
    return json.loads((root / path).read_text(encoding='utf-8'))


def read_csv(root, path):
    with (root / path).open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def amount(rows, key):
    try:
        return sum((Decimal(row[key]) for row in rows), Decimal(0))
    except (KeyError, ArithmeticError):
        raise ValueError(f'missing or nonnumeric financial field: {key}') from None


def usd_millions(thousands):
    return format(thousands / Decimal(1000), '.4f')


def current_manifest_designations(manifest):
    """Only read explicit CURRENT currency; never infer it from a version/path."""
    roles = manifest.get('current_roles')
    if isinstance(roles, dict):
        return sorted([{'path': value['path'], 'scope': value['scope'], 'role': role}
                       for role, value in roles.items()], key=lambda row: row['role'])
    records = manifest.get('artifacts', manifest.get('records', []))
    if isinstance(records, dict):
        records = [dict(value, path=key) for key, value in records.items()]
    require(isinstance(records, list), 'canonical manifest artifact collection must be a list/object')
    results = []
    for row in records:
        if not isinstance(row, dict):
            continue
        currency = row.get('currency', row.get('currency_status'))
        if isinstance(currency, dict):
            currency = currency.get('status')
        if currency == 'CURRENT':
            results.append({'path': row.get('path'), 'scope': row.get('scope'), 'role': row.get('role')})
    return sorted(results, key=lambda row: str((row['path'], row['scope'], row['role'])))


def build(root=ROOT):
    assessment = read_json(root, 'data/public_assessment/portfolio.json')
    require(assessment['detailed_case_count'] == 3 and assessment['parent_portfolio_count'] == 14,
            'Public assessment scope changed; review required')
    require(assessment['operational_validations_completed'] == 0 and assessment['recognized_benefit'] is None
            and assessment['monetary_headline'] is None, 'Public completion cannot imply an operational or financial finding')
    require(assessment['public_assessment_complete'] is True and assessment['public_assessment_status'] == 'COMPLETE_WITH_LIMITATIONS'
            and assessment['peer_review_status'] == 'PASS', 'Public acceptance is incomplete or inconsistent')
    priority = read_json(root, 'data/priority_cases/progress.json')
    require(priority['actual_operational_audits_completed'] == 0 and priority['financial_adjudications_completed'] == 0,
            'Priority operational findings changed; substantive status review required')
    require(priority['benefits'] == 'NOT_ESTIMATED' and priority['requests_sent'] == 0 and priority['accepted_accountable_owners'] == 0 and priority['approved_collections'] == 0,
            'Priority benefit/access facts changed; substantive status review required')
    require(all(r['current_state'] in ('SCREENING_CANDIDATE','VALIDATION_READY') and r['claim_class']=='NO_FINANCIAL_CLAIM'
                for r in priority['child_research_units']), 'Priority research state exceeds reviewed design boundary')
    portfolio = read_json(root, 'data/portfolio/public_portfolio.json')
    reforms = read_json(root, 'data/reforms/baseline_release.json')
    require(portfolio['release_class'] == 'PUBLIC_VALIDATION_BASELINE' and portfolio['decision_grade_portfolio'] == 'BLOCKED', 'portfolio release class changed; review status')
    require(portfolio['substantive_operational_adjudications'] == 0 and len(portfolio['cases']) == 14, 'portfolio adjudication facts changed; review status')
    require(all(r['candidate_state'] == 'SCREENING_CANDIDATE' and r['disposition'] == 'BLOCKED_PENDING_EVIDENCE' for r in portfolio['cases']), 'portfolio case states changed; review status')
    require({r['case_id'] for r in portfolio['cases']} == {f'C{i:02}' for i in range(1,15)}, 'portfolio case population changed')
    require(all(value is None for key,value in portfolio['verified_benefits'].items() if key != 'interpretation'), 'portfolio benefits changed; review status')
    manifest = read_json(root, BASE_INPUTS[0])
    issue_envelope = read_json(root, BASE_INPUTS[1])
    migration = read_json(root, BASE_INPUTS[2])
    require(issue_envelope.get('schema_version') == 1 and isinstance(issue_envelope.get('issues'), list),
            'unified issue envelope is unavailable or malformed')
    issues = issue_envelope['issues']
    require(len({row['issue_id'] for row in issues}) == len(issues), 'duplicate unified issue IDs')
    require(migration.get('issue_count') == len(issues), 'migration receipt issue count conflicts')
    issue_states = dict(sorted(Counter(row['resolution_state'] for row in issues).items()))
    require(migration.get('state_totals') == issue_states, 'migration receipt state totals conflict')
    issue_sources = dict(sorted(Counter(row['source_ref']['path'] for row in issues).items()))
    require({row['path']: row['imported_count'] for row in migration.get('sources', [])} == issue_sources,
            'migration receipt imported source populations conflict')
    pointer = read_json(root, 'data/current_research_reference.json')
    summary = read_json(root, 'data/census_v13/summary.json')
    adoption = read_json(root, 'data/census_v13/adoption_record.json')
    reference_path = pointer['reference_path']
    roles = manifest.get('current_roles', {})
    for role, expected_path in [('research_reference', reference_path),
                                ('research_pointer', 'data/current_research_reference.json'),
                                ('issue_register', 'data/issues/current_issues.json'),
                                ('current_status', OUTPUT_MD)]:
        require(roles.get(role, {}).get('path') == expected_path,
                f'canonical role {role} conflicts with the status inputs/output')
    require(not Path(reference_path).is_absolute() and '..' not in Path(reference_path).parts,
            'unsafe selected research-reference path')
    reference_hash = hashlib.sha256((root / reference_path).read_bytes()).hexdigest()
    require(reference_hash == pointer['reference_sha256'] == summary['reference_sha256'] == adoption['adopted_reference_sha256'],
            'selected research-reference hash disagrees with adoption/summary')
    require(pointer['reference_version'] == summary['version'] == adoption['version'],
            'selected research-reference version conflicts')
    require(adoption['status'] == 'adopted_for_research_only', 'research adoption status changed; review status model')
    require(adoption['authority']['institutional_approval'] is False and adoption['authority']['live_use_authorized'] is False,
            'research adoption cannot supply institutional/live approval')
    require(set(pointer['live_use_gates'].values()) == {'BLOCKED_FOR_LIVE_USE'},
            'live-use status changed; current rendering requires prospective review')
    require('paused' in pointer['course_watch_policy'].lower() and summary['course_watch'].startswith('paused'),
            'course-watch policy/summary contradict the paused current view')
    first = read_csv(root, 'data/census_v11/obligation_reviews.csv')
    lineage = read_csv(root, 'data/census_v13/reference_lineage.csv')
    first_counts = Counter(row['first_pass_disposition'] for row in first)
    require(len(first) == len(lineage) == summary['fixed_obligations'], 'fixed research-obligation counts conflict')
    require(first_counts['supported'] == summary['historical_first_pass_supported'], 'historical supported count conflict')
    require(first_counts['amendment_requested_scoring_withheld'] == summary['historical_first_pass_amendment_holds'],
            'historical amendment count conflict')
    require(summary['adopted_amendments'] == len(adoption['amendment_dispositions']) == summary['post_amendment_assertions_passed'],
            'adopted amendment/recheck counts conflict')
    require(summary['first_pass_results_rewritten'] is False and summary['fresh_full_corpus_score'] == 'not_run',
            'first-pass history must remain separate from amended rechecks')
    require(summary['cash_savings'] == 'not_estimated' and summary['staff_time_saved'] == 'not_estimated',
            'new benefit finding requires financial validation and a changed rendering contract')
    recovery = read_json(root, 'data/census_v7/final_summary.json')
    require(recovery['remaining_transcript_retrieval_gaps'] == 0 and recovery['recovered_transcripts'] == 7,
            'transcript-recovery result changed; review scope before publication')
    owner = read_json(root, 'data/owner_review/package_contract.json')
    gaps = read_csv(root, 'data/owner_review/evidence_gap_register.csv')
    require(len(gaps) == owner['gap_rows'], 'owner-gap count conflicts with package')
    require(set(row['request_status'] for row in gaps) == {'NOT_SENT'} and
            set(row['owner_response'] for row in gaps) == {'NOT_OBTAINED'},
            'owner evidence disposition changed; update substantive status treatment')
    require(owner['owner_reviews'] == owner['owner_approvals'] == owner['live_trials'] == 0,
            'owner authority/live trial changed; review scope before publication')
    require(owner['cash_savings'] == 'not_estimated', 'owner package carries an unexpected monetary finding')

    six = read_csv(root, 'data/ga_mission_reconciliation.csv')
    all_missions = read_csv(root, 'data/ga_approved_all_missions.csv')
    spm = read_csv(root, 'data/spm_2027_mission_budget.csv')
    bridge = read_csv(root, 'data/spm_2027_cluster_bridge.csv')
    controls = read_csv(root, 'data/spm_2027_financing_controls.csv')
    embedded = read_csv(root, 'data/spm_2027_embedded_efficiencies.csv')
    advice = read_csv(root, 'data/acabq_2027_mission_reconciliation.csv')
    require(len(six) == 6 and len(all_missions) == 11 and len(spm) == len(advice) == 36, 'financial population changed')
    require({row['ga_adoption_status'] for row in six} == {'verified_in_uploaded_operative_resolution'},
            'GA adoption characterization changed; review rendering contract')
    require({row['funding_cycle'] for row in six} == {'2026-07-01_to_2027-06-30'}, 'six-mission period mismatch')
    require({row['fiscal_period'] for row in all_missions} == {'2026-07-01/2027-06-30'}, '11-entity period mismatch')
    require({row['fiscal_period'] for row in spm} == {'calendar_2027'}, 'SPM period mismatch')
    require({row['budget_status'] for row in spm} == {'2027_SG_proposal_not_GA_appropriation'}, 'SPM proposal status changed')
    require({row['incremental_savings_usd_thousands'] for row in spm} == {'not_estimated'},
            'SPM incremental-savings field changed; review financial gate')
    require({row['status'] for row in embedded} == {'already_embedded_in_2027_SG_proposal'}, 'embedded initiative status changed')
    maintenance = amount(six, 'ga_approved_maintenance_usd_thousands')
    all_total = amount(all_missions, 'approved_maintenance_usd_thousands')
    spm_total = amount(spm, 'regular_budget_2027_proposed_usd_thousands')
    rsce_rows = [row for row in bridge if row['component_id'] == 'RSCE_SPM_SHARE']
    require(len(rsce_rows) == 1, 'missing/duplicate RSCE share')
    rsce = Decimal(rsce_rows[0]['proposed_2027_usd_thousands'])
    chapeau = [row for row in controls if row['bridge_id'] == 'B02']
    require(len(chapeau) == 1 and spm_total + rsce == Decimal(chapeau[0]['amount_usd_thousands']), 'SPM control total does not reconcile')
    reviewed = [row for row in advice if row['status'] == 'ACABQ_2027_advisory_financial_reconciliation_complete']
    pending = [row for row in advice if row not in reviewed]
    advice_cutoffs = sorted(set(row['review_asof'] for row in advice))
    require(len(reviewed) == 27 and len(pending) == 9 and advice_cutoffs == ['2026-10-08'],
            'advisory review population/cutoff changed; review rendering contract')
    require({row['approved_by_ga_2027'] for row in advice} == {'not_approved_in_source_corpus'},
            'advisory/approval status changed')

    finance = {
        'six_mission_maintenance': {'entities': len(six), 'usd_millions': usd_millions(maintenance),
            'period': '2026-07-01/2027-06-30', 'status': 'GA-approved maintenance in retained source corpus',
            'retained_review_cutoff': '2026-10-08', 'source': 'data/ga_mission_reconciliation.csv'},
        'eleven_entity_maintenance': {'entities': len(all_missions), 'usd_millions': usd_millions(all_total),
            'period': '2026-07-01/2027-06-30', 'status': 'approved-resource register, not complete operational audit',
            'retained_review_cutoff': '2026-10-08', 'source': 'data/ga_approved_all_missions.csv'},
        'spm_missions': {'entities': len(spm), 'usd_millions': usd_millions(spm_total),
            'period': 'calendar_2027', 'status': 'SG proposal; not GA appropriation',
            'retained_review_cutoff': '2026-10-08', 'source': 'data/spm_2027_mission_budget.csv'},
        'rsce_spm_share': {'usd_millions': usd_millions(rsce), 'period': 'calendar_2027 SPM proposal share',
            'status': 'component of SPM total, not a saving', 'retained_review_cutoff': '2026-10-08',
            'source': 'data/spm_2027_cluster_bridge.csv'},
        'spm_total_including_rsce': {'usd_millions': usd_millions(spm_total + rsce), 'period': 'calendar_2027',
            'status': 'SG proposal; do not add components again', 'retained_review_cutoff': '2026-10-08',
            'source': 'data/spm_2027_financing_controls.csv'},
        'embedded_efficiencies': {'initiatives': len(embedded), 'usd_millions': usd_millions(amount(embedded, 'projected_2027_efficiency_usd_thousands')),
            'period': 'calendar_2027', 'status': 'already embedded projected efficiencies; no new or realized saving',
            'retained_review_cutoff': '2026-10-08', 'source': 'data/spm_2027_embedded_efficiencies.csv'},
        'advisory_coverage': {'reviewed': len(reviewed), 'population': len(advice), 'unreconciled': len(pending),
            'retained_review_cutoff': advice_cutoffs[0], 'status': 'advice coverage in retained corpus; not current publication certification',
            'source': 'data/acabq_2027_mission_reconciliation.csv'},
    }
    source_paths = sorted(set(BASE_INPUTS + [reference_path]))
    source_hashes = {path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in source_paths}
    return {
        'schema_version': 1,
        'artifact_role': 'generated_authoritative_project_status_for_declared_retained_sources',
        'design_date': DESIGN_DATE,
        'evidence_scope': 'Financial evidence retains its 8 October 2026 cutoff and V8–V13 research its 15 October cutoff. The 23 October selected reform-source review is partial; no new operational evidence or institutional legal/compliance certification.',
        'authority_boundary': 'Project status view only; not a UN institutional determination, operational approval, or current UNGA81 compliance certification.',
        'canonical_manifest': {'path': BASE_INPUTS[0], 'current_designations': current_manifest_designations(manifest)},
        'research': {'reference_id': pointer['reference_id'], 'reference_version': pointer['reference_version'],
            'reference_path': reference_path, 'reference_sha256': reference_hash,
            'scope': pointer['scope_boundary'], 'historical_supported': first_counts['supported'],
            'historical_amendment_holds': first_counts['amendment_requested_scoring_withheld'],
            'fixed_obligations': len(first), 'adopted_amendments': summary['adopted_amendments'],
            'affected_assertions_rechecked': summary['amended_assertions_rechecked'],
            'affected_assertions_passed': summary['post_amendment_assertions_passed'],
            'current_holds_for_adopted_amendments': summary['current_amendment_holds_for_these_two'],
            'fresh_full_corpus_score': summary['fresh_full_corpus_score'],
            'review_cutoff': pointer['instruction_timestamp_utc'][:10]},
        'operational_constraints': {'live_gates': pointer['live_use_gates'], 'course_watch': 'PAUSED',
            'live_trials': owner['live_trials'], 'owner_approvals': owner['owner_approvals'],
            'cash_savings': 'not_estimated', 'staff_time_saved': 'not_estimated'},
        'owner_review': {'questions': len(gaps), 'requests_sent': 0, 'responses_obtained': 0,
            'source': 'data/owner_review/evidence_gap_register.csv', 'retained_review_cutoff': '2026-10-15'},
        'transcript_recovery': {'recovered_transcripts': recovery['recovered_transcripts'],
            'recovered_pages': recovery['recovered_pages'], 'remaining_retrieval_gaps': recovery['remaining_transcript_retrieval_gaps'],
            'source': 'data/census_v7/final_summary.json', 'retained_review_cutoff': recovery['asof'],
            'limitation': 'Retrieval/authentication does not mean exhaustive substantive comparison; V7 recovery supersedes the prior retrieval gap only.'},
        'finance': finance,
        'public_assessment': {'source': 'data/public_assessment/portfolio.json',
            'status': assessment['public_assessment_status'], 'detailed_case_count': assessment['detailed_case_count'],
            'parent_portfolio_count': assessment['parent_portfolio_count'], 'public_question_count': assessment['public_question_count'],
            'disposition_counts': assessment['disposition_counts'], 'peer_review_status': assessment['peer_review_status'],
            'operational_validation_optional': True, 'recognized_benefit': None},
        'priority_followup': {'source': 'data/priority_cases/progress.json',
            'child_research_units': priority['child_research_units'],
            'selected_semantic_datasets': priority['selected_semantic_datasets'],
            'selected_lineage_expressions': priority['selected_lineage_expressions'],
            'access_case_selection': priority['operational_access_case_selection'],
            'actual_operational_audits_completed': priority['actual_operational_audits_completed']},
        'portfolio': {'release_class': portfolio['release_class'], 'decision_grade_portfolio': portfolio['decision_grade_portfolio'], 'cases': len(portfolio['cases']), 'substantive_operational_adjudications': portfolio['substantive_operational_adjudications'], 'completion_gates': portfolio['completion_gates'], 'constraints': portfolio['constraints'], 'verified_benefits': portfolio['verified_benefits'], 'source': 'data/portfolio/public_portfolio.json'},
        'reform_baseline': {'release_class': reforms['release_class'], 'selected_provisions': reforms['extracted_provision_count'], 'ga81_action_extraction': reforms['ga81_action_extraction'], 'verified_compliance_findings': reforms['verified_compliance_findings'], 'source': 'data/reforms/baseline_release.json'},
        'unified_issue_observations': {'records': len(issues),
            'resolution_states': issue_states,
            'source_populations': issue_sources,
            'interpretation': 'Source-linked migrated observations include historical/control rows; counts are not unique current operational defects. Resolution, evidence, requests, responses and gate states are independent.',
            'migration_receipt': BASE_INPUTS[2], 'migration_id': migration['migration_id']},
        'next_decisions': [
            'Use the public-assessment brief and its case-specific dispositions for public research and policy follow-up; preserve source and financial qualifications.',
            'Reopen bounded questions when material public evidence, adopted authority, corrected sources or a documented scope change arrives; the other eleven cases remain visible screening entries.',
            'Extend instrument-population and applicability review beyond the selected UNGA80/81 baseline before asserting broader reform compliance.',
            'If authorized operational access becomes available, resume the retained owner, baseline, safeguards and financial-validation pathway. Live reporting remains blocked and the course watch paused.'],
        'source_hashes': source_hashes,
    }


def render(s):
    r, c, f, o = s['research'], s['operational_constraints'], s['finance'], s['owner_review']
    lines = [
        '# Current project status', '',
        '**Generated project view from retained evidence.** Code/design date: '+s['design_date']+'. '+s['evidence_scope'], '',
        s['authority_boundary'], '',
        'The Commander’s intent is to identify specific peacekeeping inefficiencies and avoidable resource use while protecting mandated operations and linking recommendations to applicable adopted reform requirements.', '',
        '## Portfolio readiness — 23 October', '',
        f"The primary [public-evidence assessment](public_assessment_brief.md) is **{s['public_assessment']['status']}**, covering **{s['public_assessment']['public_question_count']} bounded questions in {s['public_assessment']['detailed_case_count']} detailed cases** within **{s['public_assessment']['parent_portfolio_count']} visible parent screening cases**. Public dispositions: `"+json.dumps(s['public_assessment']['disposition_counts'],sort_keys=True)+'`. The [amended desired end state](desired_end_state.md) and [public completion standard](public_assessment_standard.md) permit qualified unknowns without waiting for inaccessible internal records. [Agent acceptance review](public_assessment_review.md) is separate from institutional or operational validation.', '',
        f"The retained [operational portfolio](decision_portfolio.md) contains **{s['portfolio']['cases']} screening cases** and **{s['portfolio']['substantive_operational_adjudications']} substantive operational adjudications**. Its optional later target remains three across two service types. Those original gates remain partial or blocked; public assessment completion does not fulfill them or establish realized benefits. The eleven cases outside detailed public scope retain their historical screening dispositions.", '',
        'The [priority-case follow-up](priority_case_progress.md) supplements the three preserved parent dossiers with refreshed public authority, targeted request addenda, a five-entity authority overlay and separate bounded research-unit review. Child research units: `'+json.dumps(s['priority_followup']['child_research_units'],sort_keys=True)+'`. Research readiness supplies no collection permission, accepted institutional owner, operational trial or financial finding.', '',
        f"The scoped follow-up reviews **{s['priority_followup']['selected_semantic_datasets']} consequential datasets** and **{s['priority_followup']['selected_lineage_expressions']} selected lineage expressions**. Original audit populations remain frozen. The first operational-access case remains undetermined pending confirmed access.", '',
        f"The [reform baseline](reform_compliance_view.md) contains **{s['reform_baseline']['selected_provisions']} selected provision records**, rather than universally applicable mission obligations. UNGA81 adopted-action extraction remains unresolved within the bounded search. No verified compliance finding is asserted. See the [agent review](portfolio_agent_review.md) for its actual inspection scope and limits.", '',
        'Six new evidence-request contracts cover ten case tracks. All remain unsent, collection remains unauthorized and proposed owners remain unaccepted. Three pilot charters are blocked; their numerical thresholds require actual baseline data. Ten synthetic scenarios test software behavior only. [Commander’s decision memo](commander_decision_memo.md) · [Full execution ledger](workflow_execution.md) · [Leadership report](leadership_portfolio_report.md).', '',
        '## Research reference and operational boundary', '',
        f"Research reference **{r['reference_version']}** is adopted for the fixed V8/V9 research obligations only. The historical first pass remains **{r['historical_supported']} supported and {r['historical_amendment_holds']} amendment holds** out of {r['fixed_obligations']} obligations. Both amendments were adopted; **{r['affected_assertions_passed']} affected assertions** passed separate rechecks. Current holds for those amendments: **{r['current_holds_for_adopted_amendments']}**. A fresh full-corpus score was **not run**.", '',
        '**Course watch: PAUSED.** Both `SP08P1` and `SP09P1` remain `BLOCKED_FOR_LIVE_USE`. Owner approvals and live trials in the retained package are zero. No live task is activated by this status update.', '',
        f"The owner-review package contains **{o['questions']} questions**, **{o['requests_sent']} requests sent**, and **{o['responses_obtained']} responses obtained**. These are unanswered questions, not established workflow defects.", '',
        f"V7 recovered **{s['transcript_recovery']['recovered_transcripts']} transcripts / {s['transcript_recovery']['recovered_pages']} pages**; the retained retrieval-gap count is **{s['transcript_recovery']['remaining_retrieval_gaps']}**. Earlier V6 missing-transcript counts are historical. Recovery does not imply full substantive comparison.", '',
        '**Additional cash savings and staff time saved: not estimated.** Unknown is not zero. No new duplicate-paid-service, redundant-post, realized-saving or operational-benefit finding is introduced.', '',
        '## Financial baseline and coverage', '',
        'Amounts below are USD millions, calculated from retained USD-thousands tables. Financial review cutoff: **8 October 2026**. These figures do not certify subsequent publication, adoption or implementation.', '',
        '| Measure | USD millions | Period and status |', '| --- | ---: | --- |',
    ]
    for key, label in [('six_mission_maintenance','Six detailed maintenance appropriations'),('eleven_entity_maintenance','Eleven-entity maintenance register'),('spm_missions','Thirty-six SPM mission requests'),('rsce_spm_share','RSCE SPM share'),('spm_total_including_rsce','SPM total including RSCE'),('embedded_efficiencies','Already embedded projected efficiencies')]:
        item=f[key]
        lines.append(f"| {label} | {item['usd_millions']} | {item['period']}; {item['status']} |")
    advice=f['advisory_coverage']
    lines.extend(['', f"ACABQ mission advice is reconciled for **{advice['reviewed']}/{advice['population']}** missions; **{advice['unreconciled']}** remain unreconciled in the retained corpus. This is an advice-coverage measure, not a current official publication-status or compliance conclusion.", '',
        'The six-mission amounts are included in the eleven-entity register. The SPM total includes its RSCE share. Parent totals and components must not be added; July–June appropriations and calendar-year proposals remain separate. Already embedded measures are baseline items, not newly identified benefits.', '',
        '## Canonical controls and unresolved work', '',
        f"The unified register contains **{s['unified_issue_observations']['records']} source-linked observations**, including historical and control records. Resolution states: `"+json.dumps(s['unified_issue_observations']['resolution_states'],sort_keys=True)+'`. These are not a count of unique current operational defects.', '',
        'Current artifact designations, source hashes and supersession are governed by the [canonical manifest](../metadata/canonical_manifest.json). The [issue migration receipt](../metadata/issue_migration_receipt.json) reconciles imported/excluded populations. The [machine-readable status](../metadata/current_status.json) records source hashes and cutoffs.', '',
        'Next decisions:', '',
    ])
    lines.extend('- '+item for item in s['next_decisions'])
    lines.extend(['', '## Navigation and reproduction', '',
        '- [Foundation standards](foundation_standards.md)',
        '- [Repository audit and remaining semantic/lineage gaps](repository_audit.md)',
        '- [Canonical manifest and release guide](canonical_manifest.md)',
        '- [Unified issue migration](issue_migration.md)',
        '- [Current research-reference pointer](../data/current_research_reference.json)',
        '- [V13 adoption and preserved historical outcomes](v13_reference_adoption.md)',
        '- [Historical transaction-evidence assessment](transaction_level_validation.md)', '',
        '```sh', 'python -B scripts/generate_current_status.py --write', 'python -B scripts/generate_current_status.py --check', 'python -B tests/check_current_status.py', '```', '',
        'This view is deterministic for its declared input bytes. It does not fetch sources, reset evidence dates to the build date, send requests, restart watches, migrate historical findings or authorize operational change.', ''])
    return '\n'.join(lines)


def outputs(root=ROOT):
    s=build(root)
    return {OUTPUT_JSON: json.dumps(s, indent=2, ensure_ascii=False, sort_keys=True)+'\n', OUTPUT_MD: render(s)}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    mode=p.add_mutually_exclusive_group()
    mode.add_argument('--write',action='store_true')
    mode.add_argument('--check',action='store_true')
    args=p.parse_args()
    try:
        generated=outputs()
        for path,body in generated.items():
            target=ROOT/path
            if args.write:
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_text(body,encoding='utf-8')
            else:
                require(target.exists() and target.read_text(encoding='utf-8')==body, f'status output drift: {path}')
        print('PASS: authoritative project-status view '+('generated' if args.write else 'reproduces exactly')+' from retained evidence')
        print('No new source verification, institutional approval, live activation or savings finding.')
        return 0
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(f'FAIL: {exc}',file=sys.stderr)
        return 1


if __name__=='__main__':
    raise SystemExit(main())
