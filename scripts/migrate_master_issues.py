#!/usr/bin/env python3
"""Deterministic, source-faithful A08 migration; no new operational findings."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import sys

import validate_master_issues as contract

ROOT = Path(__file__).resolve().parents[1]
REGISTER = 'data/issues/current_issues.json'
RECEIPT = 'metadata/issue_migration_receipt.json'
RULE_VERSION = 'A08-1.0'
CSV_IDS = {
    'data/quality_issues.csv': 'issue_id',
    'data/transaction_audit_issues.csv': 'issue_id',
    'data/spm_2027_source_discrepancies.csv': 'issue_id',
    'data/owner_review/evidence_gap_register.csv': 'gap_id',
    'data/public_release_gates.csv': 'opportunity_id',
    'data/census_v2/date_quality_exceptions.csv': 'exception_id',
    'data/census_v6/quality_exceptions.csv': 'issue_id',
    'data/census_v4/attendance_exclusions_and_aggregates.csv': 'control_id',
    'data/census_v12/correction_diff.csv': 'amendment_id',
    'data/census_v13/reference_lineage.csv': 'obligation_id',
}


def read(root, path):
    return json.loads((root / path).read_text())


def reference(path, selector=''):
    return path + ('#' + selector if selector else '')


def pointer(token):
    return str(token).replace('~', '~0').replace('/', '~1')


def leaves(value, location=''):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from leaves(item, location + '/' + pointer(key))
    elif isinstance(value, list):
        if not value:
            yield location, value
        for ix, item in enumerate(value):
            yield from leaves(item, location + '/' + str(ix))
    else:
        yield location, value


def first(row, *keys, default='Source-qualified record; review the complete original record.'):
    for key in keys:
        if isinstance(row.get(key), str) and row[key].strip():
            return row[key]
    return default


def identifier(path, legacy):
    return 'A08:' + path.removeprefix('data/').replace('/', ':').replace('.', '_') + ':' + legacy


def issue_record(path, digest, fmt, id_field, selector, legacy, raw):
    iid = identifier(path, legacy)
    base = {
        'issue_id': iid, 'aliases': [legacy], 'parent_issue_id': None,
        'source_ref': {'path': path, 'sha256': digest, 'format': fmt, 'id_field': id_field,
                       'selector': selector, 'legacy_id': legacy, 'original_record': raw},
        'issue_type': 'DATA_QUALITY',
        'summary': first(raw, 'issue', 'control_issue', 'topic', 'finding', 'item', 'object', 'reason', 'basis'),
        'severity': str(raw.get('severity', 'UNKNOWN')).upper(), 'severity_change_receipt': None,
        'resolution_state': 'UNKNOWN', 'evidence_state': 'UNKNOWN', 'request_state': 'UNKNOWN',
        'response_state': 'UNKNOWN', 'gate_status': 'NOT_ASSESSED', 'blocking_claims': [],
        'minimum_evidence': first(raw, 'minimum_evidence', 'resolution_required', 'observed_limitation',
                                  'restriction_or_test', 'resolution', 'resolution_note'),
        'closure_rule': first(raw, 'closure_rule', 'resolution_required', 'restriction_or_test',
                             'release_and_additivity_rule', 'resolution_note', 'resolution'),
        'proposed_owner_role': raw.get('evidence_holder_role_not_assignment'), 'accepted_owner_ref': None,
        'normalization_receipt': reference(RECEIPT, '/normalization_receipts/' + pointer(iid)),
        'resolution_receipt': None, 'source_evidence_refs': [reference(path, selector)],
        'claim': {'classification': 'NO_MONETARY_CLAIM', 'amount': None,
                  'candidate_state': None, 'financial_validation_ref': None},
    }
    if base['severity'] not in {'UNKNOWN', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'}:
        base['severity'] = 'UNKNOWN'
        base['severity_change_receipt'] = base['normalization_receipt']
    if raw.get('request_status') == 'NOT_SENT':
        base['request_state'] = 'NOT_REQUESTED'
    if raw.get('owner_response') == 'NOT_OBTAINED' or raw.get('owner_approval') == 'not_obtained':
        base['response_state'] = 'NOT_OBTAINED'
    status = raw.get('status', '')
    if status.startswith('open') or status.startswith('OPEN_'):
        base['resolution_state'] = 'OPEN'
        base['evidence_state'] = 'EVIDENCE_REQUIRED'
    elif status == 'documented_contained':
        base['resolution_state'] = 'DOCUMENTED_CONTAINED'
        base['evidence_state'] = 'REPORTED'
    elif status == 'resolved':
        base['resolution_state'] = 'RESOLVED'
        base['evidence_state'] = 'REPORTED'
        base['resolution_receipt'] = base['normalization_receipt']
    if path.endswith('transaction_audit_issues.csv'):
        base.update(issue_type='TRANSACTION_GAP', gate_status='BLOCKED')
        base['blocking_claims'] = [raw['restriction_or_test']]
    elif path.endswith('spm_2027_source_discrepancies.csv'):
        base.update(issue_type='SOURCE_DISCREPANCY', evidence_state='REPORTED')
        if raw['audit_status'] == 'resolved_by_detailed_chapeau':
            base['resolution_state'] = 'RESOLVED'
            base['resolution_receipt'] = base['normalization_receipt']
        elif raw['audit_status'].startswith('documented_'):
            base['resolution_state'] = 'DOCUMENTED_CONTAINED'
    elif path.endswith('owner_review/evidence_gap_register.csv'):
        base.update(issue_type='OWNER_QUESTION', resolution_state='OPEN', gate_status='BLOCKED')
        base['blocking_claims'] = [raw['consequence_while_open']]
        base['evidence_state'] = {'NOT_TESTED_LATER_GATE': 'NOT_TESTED',
                                  'NOT_ESTABLISHED_LATER_GATE': 'NOT_ESTABLISHED'}.get(status, 'EVIDENCE_REQUIRED')
    elif path.endswith('public_release_gates.csv'):
        base.update(issue_type='RELEASE_GATE', resolution_state='OPEN', evidence_state='EVIDENCE_REQUIRED',
                    gate_status='BLOCKED', blocking_claims=[raw['blocker']])
        base['summary'] = 'Release restrictions for ' + legacy + ': ' + raw['blocker']
        base['minimum_evidence'] = raw['blocker']
        base['closure_rule'] = 'Satisfy the original mandate, implementation and transaction controls; no savings from migration.'
    elif path.endswith('date_quality_exceptions.csv'):
        base.update(issue_type='DATE_EXCEPTION', resolution_state='OPEN', evidence_state='EVIDENCE_REQUIRED')
    elif path.endswith('census_v6/quality_exceptions.csv'):
        base.update(evidence_state='REPORTED', resolution_state='DOCUMENTED_CONTAINED')
        if legacy in {'V6Q01', 'V6Q05', 'V6Q06'}:
            base.update(resolution_state='OPEN', evidence_state='EVIDENCE_REQUIRED')
    elif path.endswith('attendance_exclusions_and_aggregates.csv'):
        base.update(issue_type='CONTROL_EXCLUSION', resolution_state='DOCUMENTED_CONTAINED',
                    evidence_state='REPORTED', gate_status='NOT_APPLICABLE')
    return base


def build(root=ROOT):
    scope = {x['path']: x for x in read(root, 'metadata/repository_audit_scope.json')['files']}
    with (root / 'metadata/issue_register_crosswalk.csv').open(newline='') as handle:
        paths = sorted({r['source_path'] for r in csv.DictReader(handle)})
    pointer_record = read(root, 'data/current_research_reference.json')
    if pointer_record.get('reference_version') != '13.0':
        raise ValueError('Research reference changed; review cross-version resolution rules before migration')
    adopted = read(root, 'data/census_v13/adoption_record.json')
    reference_bytes = (root / pointer_record['reference_path']).read_bytes()
    if (hashlib.sha256(reference_bytes).hexdigest() != pointer_record['reference_sha256']
            or adopted.get('status') != 'adopted_for_research_only'
            or adopted.get('adopted_reference_sha256') != pointer_record['reference_sha256']
            or adopted.get('authority', {}).get('institutional_approval') is not False):
        raise ValueError('Research-adoption dependency changed or cannot be authenticated at byte/status level')
    with (root / 'data/census_v13/reference_lineage.csv').open(newline='') as handle:
        lineage = list(csv.DictReader(handle))
    affected = {r['amendment_id']: r for r in lineage if r['amendment_id']}
    if set(affected) != {'AM11-01', 'AM11-02'} or any(r['current_disposition'] != 'post_amendment_affected_recheck_passed' for r in affected.values()):
        raise ValueError('V13 amendment evidence no longer matches the reviewed two-correction rule')
    issues, source_results, normalizations = [], [], {}
    for path in paths:
        raw_bytes = (root / path).read_bytes()
        digest = hashlib.sha256(raw_bytes).hexdigest()
        if digest != scope[path]['sha256']:
            raise ValueError('Source drift: ' + path)
        imported, excluded = [], []
        obj = None
        if path.endswith('.csv'):
            id_field = CSV_IDS[path]
            units = [(r[id_field], r[id_field], r) for r in csv.DictReader(io.StringIO(raw_bytes.decode('utf-8')))]
        else:
            id_field = None
            obj = json.loads(raw_bytes)
            if path.endswith('activation_status.json'):
                units = [('/' + pointer(k), k, v) for k, v in obj.items()]
            elif path.endswith('closed_gate_receipt.json'):
                units = [('/live_gates/' + pointer(k), k, v) for k, v in obj['live_gates'].items()]
            elif path.endswith('amendment_requests.json'):
                units = [('/' + str(i), r['amendment_id'], r) for i, r in enumerate(obj)]
            elif path.endswith('operational_status.json'):
                units = [('', 'COURSE_WATCH_PAUSE', obj)]
            elif path.endswith('review_decisions.json'):
                units = [('/course_decisions/' + str(i), r['listing_id'], r) for i, r in enumerate(obj['course_decisions'])]
            else:
                raise ValueError('Unreviewed JSON source mapping: ' + path)
        for selector, legacy, original in units:
            if path.endswith('reference_lineage.csv') and not original['amendment_id']:
                excluded.append({'selector': selector, 'reason': 'Carried-forward supported obligation, not an issue or new substantive recheck.'})
                continue
            record = issue_record(path, digest, 'csv' if id_field else 'json', id_field, selector, legacy, original)
            if path.endswith(('amendment_requests.json', 'correction_diff.csv', 'reference_lineage.csv')):
                amendment = original.get('amendment_id')
                if amendment not in affected:
                    raise ValueError('Unexpected amendment identity')
                record.update(issue_type='AMENDMENT', resolution_state='RESOLVED', evidence_state='REPORTED',
                              gate_status='NOT_APPLICABLE',
                              summary=first(original, 'reason', 'after_assertion', default='Research amendment ' + amendment + ' adopted in reference 13.0.'))
                record['resolution_receipt'] = record['normalization_receipt']
                record['source_evidence_refs'] += ['data/current_research_reference.json', 'data/census_v13/adoption_record.json',
                                                   'data/census_v13/reference_lineage.csv#' + affected[amendment]['obligation_id']]
                record['minimum_evidence'] = 'Retain source-qualified amendment, adopted research payload and separate affected recheck; no owner approval inferred.'
                record['closure_rule'] = 'Resolved for the adopted research reference only; historical first-pass hold and institutional approval remain distinct.'
                if not path.endswith('amendment_requests.json'):
                    record['parent_issue_id'] = identifier('data/census_v11/amendment_requests.json', amendment)
            elif id_field is None and 'missing' in original:
                missing = original['missing']
                if original.get('status') != 'BLOCKED_FOR_LIVE_USE' or not isinstance(missing, list):
                    raise ValueError('Unreviewed activation state')
                record.update(issue_type='RELEASE_GATE', summary='Live-use gate ' + legacy,
                              resolution_state='OPEN', evidence_state='EVIDENCE_REQUIRED', gate_status='BLOCKED',
                              blocking_claims=['Live execution for ' + legacy],
                              minimum_evidence='Missing activation fields: ' + '; '.join(missing),
                              closure_rule='Meet every applicable V10 activation requirement and obtain authentic institutional authority; research adoption is insufficient.')
                if not path.endswith('activation_status.json'):
                    record['parent_issue_id'] = identifier('data/census_v10/activation_status.json', legacy)
            elif path.endswith('operational_status.json'):
                if original.get('course_watch') != 'paused' or original.get('reactivation_authorized') is not False:
                    raise ValueError('Paused course-watch constraint changed; explicit review needed')
                record.update(issue_type='CONTROL_EXCLUSION', summary='Course watch remains paused; reactivation unauthorized.',
                              resolution_state='DOCUMENTED_CONTAINED', evidence_state='REPORTED', gate_status='BLOCKED',
                              blocking_claims=['Course-watch execution or reactivation'],
                              minimum_evidence='A separate explicit restart instruction and applicable authority are required.',
                              closure_rule='Retain the pause until an explicit authorized instruction supersedes it; this migration grants none.')
            elif path.endswith('review_decisions.json'):
                record.update(issue_type='OWNER_QUESTION', resolution_state='OPEN', evidence_state='NOT_ESTABLISHED',
                              summary='Exact-cohort delivery/completion evidence for ' + legacy,
                              minimum_evidence='Exact cohort identity and primary completion evidence; ' + original['basis'],
                              closure_rule='Do not infer delivery from an advertisement, elapsed start date or a related programme.')
                # The retained V6 cutoff is historical; do not advance dates to the migration date.
            issues.append(record)
            imported.append({'selector': selector, 'issue_id': record['issue_id']})
            normalizations[record['issue_id']] = {
                'rule_version': RULE_VERSION, 'source_path': path, 'selector': selector,
                'source_status_preserved': True, 'normalization_scope': 'Repository source interpretation; no new UN-source authentication or owner evidence.',
                'resolution_basis': ('Original documented resolution retained; no operational verification implied.' if record['resolution_state'] == 'RESOLVED' else 'No new closure.'),
                'research_amendment_only': record['issue_type'] == 'AMENDMENT',
            }
        leaf_coverage = []
        if obj is not None:
            for leaf, _value in leaves(obj):
                covering = [x for x in imported if x['selector'] == '' or leaf == x['selector'] or leaf.startswith(x['selector'] + '/')]
                leaf_coverage.append({'pointer': leaf, 'disposition': 'REPRESENTED_IN_ORIGINAL_RECORD' if covering else 'EXCLUDED_CONTEXT',
                                      'issue_id': covering[0]['issue_id'] if covering else None,
                                      'reason': 'Full original object retained at exact selector.' if covering else 'Container metadata, existing identity decisions, negative controls or source interpretation; not independently promoted to a new issue.'})
        source_results.append({'path': path, 'sha256': digest, 'candidate_units': len(units),
                               'imported_count': len(imported), 'excluded_count': len(excluded),
                               'imported': imported, 'excluded': excluded, 'json_leaf_coverage': leaf_coverage})
    envelope = {'schema_version': 1, 'issues': sorted(issues, key=lambda r: r['issue_id'])}
    contract.validate(envelope)
    contract.check_sources(envelope, root)
    receipt = {
        'migration_id': RULE_VERSION, 'source_scope_id': 'A01-A06-2026-10-22',
        'basis': 'Retained repository evidence through original source cutoffs; migration does not refresh source or operational status.',
        'legacy_sources_modified': False, 'new_owner_approvals': 0, 'requests_sent': 0,
        'source_count': len(source_results), 'issue_count': len(issues),
        'state_totals': dict(sorted(Counter(r['resolution_state'] for r in issues).items())),
        'issue_type_totals': dict(sorted(Counter(r['issue_type'] for r in issues).items())),
        'sources': source_results, 'normalization_receipts': normalizations,
        'compatibility_extension': {
            'previous_schema_sha256': '577a3f97de8de40ce9c8f9ec2546eb625e2245955f2f695a4e71d46488503496',
            'change': 'Permit the RFC 6901 empty JSON pointer for a root object; empty CSV selectors still rejected.',
            'reason': 'Retain the complete paused-watch object at its exact source identity instead of fabricating a wrapped record.'},
        'reconciliation_dependencies': {
            p: hashlib.sha256((root / p).read_bytes()).hexdigest()
            for p in ('data/current_research_reference.json', 'data/census_v13/adoption_record.json',
                      'data/census_v13/reference_lineage.csv', 'metadata/master_issue_schema.json',
                      'metadata/issue_register_crosswalk.csv')},
        'limitations': ['Sources are observations and constraints, not necessarily distinct problems; parent links preserve repeated historical gate observations.',
                       'Course-decision outcomes retain their V6 cutoff; the paused watch was not run.',
                       'Resolved research amendments do not resolve owner questions or grant live-use permission.',
                       'No quantitative savings, compliance, transaction verification, or accepted institutional ownership is created.'],
    }
    return envelope, receipt


def encoded(value):
    return json.dumps(value, indent=2, ensure_ascii=False) + '\n'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    try:
        envelope, receipt = build()
        for name, value in ((REGISTER, envelope), (RECEIPT, receipt)):
            expected = encoded(value)
            target = ROOT / name
            if args.check:
                if not target.exists() or target.read_text() != expected:
                    raise ValueError('Migration output drift: ' + name)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(expected)
        print(f'PASS: {receipt["issue_count"]} records across {receipt["source_count"]} sources; originals preserved')
        return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print('FAIL: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
