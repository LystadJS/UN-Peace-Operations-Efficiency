#!/usr/bin/env python3
"""P04: reject financial perimeter overlap and benefit reclassification."""
import argparse
import json
from decimal import Decimal
from pathlib import Path
from build_financial_baseline import ROOT, TARGET, build


def validate(data, root=ROOT):
    errors = []
    expected = build(root)
    if data != expected:
        errors.append('Baseline differs from exact retained source derivation')
    a = data['amounts']
    d = lambda key: Decimal(a[key]['amount'])
    if d('spm_missions') + d('spm_rsce') != d('spm_total'):
        errors.append('SPM parent differs from mission plus RSCE components')
    members = data['entity_membership']
    if not set(members['six_maintenance']) < set(members['eleven_maintenance']):
        errors.append('Six missions must be a strict subset of eleven entities')
    if any(v is not None for k, v in data['benefits'].items() if k != 'status'):
        errors.append('Retained resource controls cannot become quantified benefits')
    if any(v['savings_finding'] for v in a.values()):
        errors.append('Resource or embedded baseline mislabeled as a savings finding')
    six = {r['mission_id']: r for r in data['source_rows']['six']}
    eleven = {r['mission_id']: r for r in data['source_rows']['eleven']}
    for key, row in six.items():
        if Decimal(row['ga_approved_maintenance_usd_thousands']) != Decimal(eleven[key]['approved_maintenance_usd_thousands']):
            errors.append('Subset value mismatch: ' + key)
        components = sum((Decimal(row[f]) for f in [
            'ga_approved_maintenance_usd_thousands', 'ga_support_account_share_usd_thousands',
            'ga_logistics_base_share_usd_thousands', 'ga_regional_service_centre_share_usd_thousands']), Decimal('0'))
        if components != Decimal(row['ga_appropriation_usd_thousands']):
            errors.append('Inclusive appropriation components mismatch: ' + key)
    return errors


def validate_selection(data, selected):
    """A selection is an arithmetic aggregation request, not a benefit estimate."""
    if len(selected) != len(set(selected)):
        return ['Duplicate amount selected']
    a = data['amounts']
    if any(k not in a for k in selected):
        return ['Unknown amount key']
    for rel in data['nonadditivity_relationships']:
        if rel['child'] in selected and rel['parent'] in selected:
            return ['Overlapping parent and child selected']
    if any(a[k]['role'] != 'RESOURCE_BASELINE' for k in selected):
        return ['Embedded measures or closures cannot be aggregated as incremental benefits']
    perimeters = {(a[k]['period'], a[k]['authority_status'], a[k]['perimeter']) for k in selected}
    if len(selected) > 1 and len(perimeters) != 1:
        return ['Mixed periods, authority versions or financial perimeters require an explicit bridge']
    if len(selected) > 1:
        return ['No disjoint cost-object partition declared for these controls']
    return []


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--records', type=Path, default=ROOT / TARGET)
    parser.add_argument('--aggregate', nargs='+')
    args = parser.parse_args()
    data = json.loads(args.records.read_text())
    errors = validate(data)
    if args.aggregate:
        errors.extend(validate_selection(data, args.aggregate))
    if errors:
        raise SystemExit('\n'.join(errors))
    print('P04 source identities, perimeter and nonadditivity controls passed')


if __name__ == '__main__':
    main()
