#!/usr/bin/env python3
"""Build a provenance-preserving register of retained ACABQ advice, not adoption."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from decimal import Decimal
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
TARGET = 'data/reforms/acabq_recommendations.json'
INPUTS = {
    'financial': 'data/acabq_2027_financial_actions.csv',
    'qualitative': 'data/acabq_2027_qualitative_directives.csv',
    'crosscutting': 'data/acabq_2027_main_crosscutting_framework.csv',
    'missions': 'data/acabq_2027_mission_reconciliation.csv',
    'sources': 'data/acabq_2027_source_manifest.csv',
    'reports': 'data/acabq_2027_report_status.csv',
    'unreviewed': 'data/acabq_2027_unissued_report_scope.csv',
}


def build(root=ROOT):
    tables = {}
    receipts = {}
    for kind, path in INPUTS.items():
        payload = (root / path).read_bytes()
        tables[kind] = list(csv.DictReader(payload.decode('utf-8').splitlines()))
        receipts[path] = {'sha256': hashlib.sha256(payload).hexdigest(),
                          'row_count': len(tables[kind])}
    specs = {
        'financial': ('action_id', 'source_document', 'paragraph', 'recommendation_detail', 'entity_id'),
        'qualitative': ('directive_id', 'report_symbol', 'paragraphs', 'committee_position', 'scope_id'),
        'crosscutting': ('framework_id', 'source_document', 'reference_paragraph', 'exact_normative_characterization', 'scope'),
    }
    records = []
    for kind, (key, symbol, paragraph, action, scope) in specs.items():
        for index, row in enumerate(tables[kind], 2):
            records.append({
                'recommendation_id': 'ACABQ-' + row[key],
                'record_kind': kind,
                'authority_classification': 'ACABQ_ADVICE',
                'adoption_status': 'GA_ACCEPTANCE_NOT_ESTABLISHED_IN_RETAINED_CORPUS',
                'implementation_status': 'NOT_VERIFIED',
                'evidence_cutoff': '2026-10-08',
                'source_symbol': row[symbol],
                'official_url': 'https://docs.un.org/en/' + quote(row[symbol], safe='/().'),
                'paragraph_locator': row[paragraph],
                'scope': row[scope],
                'action_paraphrase': row[action],
                'financial_effect': {
                    'classification': 'ADVISORY_BUDGET_ADJUSTMENT' if kind == 'financial' else 'NOT_QUANTIFIED_BY_THIS_RECORD',
                    'amount': row['acabq_minus_sg_usd_thousands'] if kind == 'financial' else None,
                    'unit': 'USD_THOUSANDS' if kind == 'financial' else None,
                    'period': 'CALENDAR_2027',
                    'perimeter': row.get('financial_perimeter'),
                    'not_a_savings_finding': True,
                },
                'provenance': {'path': INPUTS[kind], 'csv_line': index,
                               'row_key': {key: row[key]}, 'source_snapshot': row},
            })
    reviewed = [r for r in tables['missions'] if r['cluster_id'] in ('SPM_CLUSTER_1', 'SPM_CLUSTER_2')]
    totals = {}
    for row in tables['financial']:
        perimeter = row['financial_perimeter']
        totals[perimeter] = totals.get(perimeter, Decimal('0')) + Decimal(row['acabq_minus_sg_usd_thousands'])
    return {
        'schema_version': '1.0',
        'register_id': 'R07-RETAINED-ACABQ-2027',
        'evidence_cutoff': '2026-10-08',
        'assembly_date': '2026-10-23',
        'verification_scope': 'DETERMINISTIC_REPACKAGING_OF_REPOSITORY_EXTRACTIONS_NOT_FRESH_OFFICIAL_TEXT_REVIEW',
        'source_receipts': receipts,
        'coverage': {'mission_population': len(tables['missions']), 'numerical_advice_reviewed': len(reviewed),
                     'mission_advice_unreviewed': len(tables['missions']) - len(reviewed),
                     'rsce_spm_advice': 'NOT_REVIEWED', 'full_spm_advice_adjusted_total': None,
                     'recommendation_records': len(records),
                     'record_kinds': dict(sorted(Counter(r['record_kind'] for r in records).items()))},
        'advisory_adjustment_controls': {
            'unit': 'USD_THOUSANDS', 'period': 'CALENDAR_2027',
            'by_disjoint_perimeter': {key: str(value) for key, value in sorted(totals.items())},
            'controls_are_not_additional_records': True,
            'complete_un_or_peacekeeping_adjustment': False,
            'savings_finding': False,
        },
        'recommendations': records,
        'mission_coverage': [{'path': INPUTS['missions'], 'csv_line': i, 'source_snapshot': row}
                             for i, row in enumerate(tables['missions'], 2)],
        'retained_primary_source_receipts': tables['sources'],
        'retained_report_status_observations': tables['reports'],
        'unreviewed_report_observations': tables['unreviewed'],
        'limitations': [
            'Primary PDF bytes are not held here; retained checksums are upstream provenance claims, not newly verified bytes.',
            'The 2026-10-08 report-availability observations are historical and do not establish publication status on 2026-10-23.',
            'Twenty-seven mission control rows and recommendation records overlap; do not sum controls and components.',
            'Crosscutting statements include expectations and observations, not only recommended actions; preserve statement type in snapshots.',
            'General ACABQ discussion is not nine Cluster III mission-specific financial recommendations.',
            'No subsequent GA adoption or implementation has been established by this register.',
            'Missing advice is unknown, not zero; an unadjusted proposal does not establish operational efficiency.',
        ],
    }


def encoded(root=ROOT):
    return json.dumps(build(root), indent=2, ensure_ascii=False) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write', action='store_true')
    mode.add_argument('--check', action='store_true')
    args = parser.parse_args()
    target = ROOT / TARGET
    expected = encoded()
    if args.write:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(expected, encoding='utf-8')
    elif not target.exists() or target.read_text(encoding='utf-8') != expected:
        raise SystemExit('ACABQ register stale or missing; run --write')
    print('ACABQ register: 48 retained advice records; 27/36 mission advice controls; GA acceptance unestablished')


if __name__ == '__main__':
    main()
