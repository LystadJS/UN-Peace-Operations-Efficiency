#!/usr/bin/env python3
"""P03: exact-decimal retained financial perimeter controls."""
import argparse
import csv
import hashlib
import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = 'data/portfolio/financial_baseline.json'
INPUTS = {
 'six': 'data/ga_mission_reconciliation.csv',
 'eleven': 'data/ga_approved_all_missions.csv',
 'spm': 'data/spm_2027_mission_budget.csv',
 'bridge': 'data/spm_2027_cluster_bridge.csv',
 'controls': 'data/spm_2027_financing_controls.csv',
 'embedded': 'data/spm_2027_embedded_efficiencies.csv',
 'closures': 'data/spm_2027_closure_bridge.csv',
}


def build(root=ROOT):
    tables, sources = {}, {}
    for key, path in INPUTS.items():
        raw = (root / path).read_bytes()
        tables[key] = list(csv.DictReader(raw.decode('utf-8').splitlines()))
        sources[path] = {'sha256': hashlib.sha256(raw).hexdigest(), 'rows': len(tables[key])}
    def total(key, field):
        return str(sum((Decimal(r[field]) for r in tables[key]), Decimal('0')))
    bridge = {r['component_id']: r for r in tables['bridge']}
    controls = {r['bridge_id']: r for r in tables['controls']}
    amounts = {}
    def add(key, amount, period, authority, perimeter, source, role='RESOURCE_BASELINE'):
        amounts[key] = {'amount': amount, 'unit': 'USD_THOUSANDS', 'period': period,
                        'authority_status': authority, 'perimeter': perimeter, 'role': role,
                        'source': source, 'savings_finding': False}
    fy = '2026-07-01/2027-06-30'
    cy = 'CALENDAR_2027'
    add('six_maintenance', total('six', 'ga_approved_maintenance_usd_thousands'), fy, 'GA_APPROVED_IN_RETAINED_CORPUS', 'SIX_MISSION_MAINTENANCE_GROSS', INPUTS['six'])
    add('eleven_maintenance', total('eleven', 'approved_maintenance_usd_thousands'), fy, 'APPROVED_RESOURCE_NOTE_IN_RETAINED_CORPUS', 'ELEVEN_ENTITY_MAINTENANCE_GROSS', INPUTS['eleven'])
    add('six_sg_request', total('six', 'sg_proposal_usd_thousands'), fy, 'SG_PROPOSAL', 'SIX_MISSION_MAINTENANCE_GROSS', INPUTS['six'])
    add('six_inclusive_appropriation', total('six', 'ga_appropriation_usd_thousands'), fy, 'GA_APPROVED_IN_RETAINED_CORPUS', 'SIX_MAINTENANCE_PLUS_SUPPORT_UNLB_RSCE_SHARES', INPUTS['six'])
    add('spm_missions', total('spm', 'regular_budget_2027_proposed_usd_thousands'), cy, 'SG_PROPOSAL_NOT_GA_APPROPRIATION', '36_SPM_REGULAR_BUDGET_NET_STAFF_ASSESSMENT', INPUTS['spm'])
    add('spm_rsce', bridge['RSCE_SPM_SHARE']['proposed_2027_usd_thousands'], cy, 'SG_PROPOSAL_NOT_GA_APPROPRIATION', 'SPM_RSCE_SHARE', INPUTS['bridge'])
    add('spm_total', controls['B02']['amount_usd_thousands'], cy, 'SG_PROPOSAL_NOT_GA_APPROPRIATION', '36_SPM_PLUS_RSCE_REGULAR_BUDGET_NET_STAFF_ASSESSMENT', INPUTS['controls'])
    add('embedded_measures', total('embedded', 'projected_2027_efficiency_usd_thousands'), cy, 'SG_PROJECTION_ALREADY_EMBEDDED', '31_MEASURES_ALREADY_IN_SPM_PROPOSAL', INPUTS['embedded'], 'ALREADY_EMBEDDED_NOT_INCREMENTAL')
    add('closures_2026', total('closures', 'approved_2026_usd_thousands'), 'CALENDAR_2026', 'PRIOR_MANDATE_TRANSITIONS_IN_RETAINED_CORPUS', 'THREE_DISCONTINUED_MISSIONS', INPUTS['closures'], 'EXCLUDED_FROM_INCREMENTAL_BENEFITS')
    return {
      'schema_version': '1.0', 'baseline_id': 'P03-RETAINED-FINANCE-1',
      'evidence_cutoff': '2026-10-08', 'assembly_date': '2026-10-23',
      'scope': 'Retained public-source resource controls, not a fresh governing-text or actual-expenditure review.',
      'source_receipts': sources, 'amounts': amounts,
      'entity_membership': {
          'six_maintenance': sorted(r['mission_id'] for r in tables['six']),
          'eleven_maintenance': sorted(r['mission_id'] for r in tables['eleven']),
          'spm_missions': sorted(r['spm_id'] for r in tables['spm'])},
      'nonadditivity_relationships': [
          {'type': 'SUBSET_OF', 'child': 'six_maintenance', 'parent': 'eleven_maintenance'},
          {'type': 'COMPONENT_OF', 'child': 'six_maintenance', 'parent': 'six_inclusive_appropriation'},
          {'type': 'COMPONENT_OF', 'child': 'spm_missions', 'parent': 'spm_total'},
          {'type': 'COMPONENT_OF', 'child': 'spm_rsce', 'parent': 'spm_total'},
          {'type': 'EMBEDDED_BASELINE_NOT_NEW_BENEFIT', 'child': 'embedded_measures', 'parent': 'spm_total'}],
      'benefits': {'cashable_saving': None, 'realized_saving': None, 'capacity_gain': None,
                   'recovery': None, 'cost_avoidance': None, 'status': 'NOT_ESTIMATED'},
      'source_rows': tables,
      'limitations': [
          'Do not add subsets to parent totals, or different proposal/approval versions to each other.',
          'Fiscal peacekeeping gross maintenance and calendar-year net SPM proposals have different time and funding perimeters; no combined UN total is asserted.',
          'Maintenance/request differences and source-version differences are budget changes, not savings.',
          'Shared-service charges are internal allocations; a provider/client reconciliation and full-system counterfactual are required before benefits.',
          'Embedded measures and already mandated closures cannot be claimed again as incremental interventions.',
          'Unknown benefits remain null; zero would be a measured quantity requiring evidence.',
      ],
    }


def encoded(root=ROOT):
    return json.dumps(build(root), indent=2, ensure_ascii=False) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--write', action='store_true')
    group.add_argument('--check', action='store_true')
    args = parser.parse_args()
    target = ROOT / TARGET
    if args.write:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(encoded(), encoding='utf-8')
    elif not target.exists() or target.read_text(encoding='utf-8') != encoded():
        raise SystemExit('financial baseline stale; run --write')
    print('P03 financial baseline verified')


if __name__ == '__main__':
    main()
