#!/usr/bin/env python3
"""P01: source-scoped entity identities; names do not establish operational status."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

SOURCES = [
    'data/spm_2027_mission_budget.csv', 'data/ga_approved_all_missions.csv',
    'data/mission_budget_register.csv', 'data/ga_mission_reconciliation.csv',
    'data/functional_inventory.csv', 'data/support_account_units.csv',
    'data/transaction_control_baseline.csv', 'data/ga_adopted_directives.csv',
    'data/transaction_evidence_requests.csv',
]
SPM_ALIASES = {'SPM028': ['UNOWAS'], 'SPM029': ['UNRCCA'], 'SPM031': ['UNSCOL'],
               'SPM032': ['UNOCA'], 'SPM033': ['UNSMIL'], 'SPM034': ['UNVMC'],
               'SPM035': ['BINUH'], 'SPM036': ['UNAMA']}
NAMES = {'DPPA': 'Department of Political and Peacebuilding Affairs',
         'DPO': 'Department of Peace Operations', 'DOS': 'Department of Operational Support',
         'RSCE': 'Regional Service Centre in Entebbe', 'UNLB': 'United Nations Logistics Base',
         'UNTSO': 'United Nations Truce Supervision Organization',
         'UNMOGIP': 'UN Military Observer Group in India and Pakistan',
         'MINUSMA': 'MINUSMA', 'UNTMIS': 'UNTMIS'}


def stable_unit(department, label):
    return 'UNPO-UNIT-' + hashlib.sha256((department + ':' + label).encode()).hexdigest()[:12].upper()


def build(root):
    entities, aliases, relationships, inputs = {}, [], [], []
    rows = {}
    for path in SOURCES:
        raw = (root / path).read_bytes()
        rows[path] = list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
        inputs.append({'path': path, 'sha256': hashlib.sha256(raw).hexdigest(), 'rows': len(rows[path]),
                       'evidence_cutoff': '2026-10-15', 'cutoff_basis': 'retained project baseline; not freshly verified'})

    def entity(identifier, name, kind, source, locator):
        if identifier not in entities:
            entities[identifier] = {'entity_id': identifier, 'display_name': name, 'entity_type': kind,
                                    'lifecycle_status': 'UNKNOWN_NOT_VERIFIED',
                                    'mandate_status': 'NOT_ADJUDICATED', 'implementation_status': 'NOT_VERIFIED',
                                    'source_references': []}
        reference = {'path': source, 'locator': locator}
        if reference not in entities[identifier]['source_references']:
            entities[identifier]['source_references'].append(reference)
        return identifier

    def alias(value, identifier, source, locator, basis='exact_source_key'):
        record = {'alias': value, 'entity_id': identifier, 'source_path': source, 'source_locator': locator,
                  'mapping_basis': basis}
        if record not in aliases:
            aliases.append(record)

    for index, row in enumerate(rows[SOURCES[0]], 2):
        identifier = 'UNPO-' + row['spm_id']
        locator = f'CSV row {index}; spm_id={row["spm_id"]}'
        entity(identifier, row['mission_name'], 'SPECIAL_POLITICAL_MISSION_OR_MANDATE_BUDGET_ENTITY', SOURCES[0], locator)
        for value in [row['spm_id'], row['mission_name']] + SPM_ALIASES.get(row['spm_id'], []):
            alias(value, identifier, SOURCES[0], locator, 'reviewed_spm_row_identity')

    for path in SOURCES[1:4]:
        for index, row in enumerate(rows[path], 2):
            value = row['mission_id']
            identifier = entity('UNPO-' + value, value, 'PEACEKEEPING_OR_SUPPORT_MISSION', path, f'CSV row {index}; mission_id={value}')
            alias(value, identifier, path, f'CSV row {index}; mission_id={value}')

    # Source columns establish cost-share relationships, not organizational containment.
    for value, kind, source, locator in [
        ('RSCE', 'SHARED_SERVICE_CENTRE', SOURCES[6], 'recipient_entity=RSCE'),
        ('UNLB', 'LOGISTICS_BASE', SOURCES[3], 'ga_logistics_base_share_usd_thousands'),
        ('DOS', 'DEPARTMENT', SOURCES[8], 'request_id=REQ12; request_id=REQ16; proposed custodian requires confirmation'),
        ('MINUSMA', 'HISTORICAL_MISSION_REFERENCE', SOURCES[7], 'directive_id=GA_D10; transferred assets'),
        ('UNTMIS', 'MISSION_REFERENCE', SOURCES[2], 'mission_id=UNSOS; interpretation_guardrail'),
    ]:
        # DOS is a prospective custodian label, not a verified source-derived organizational relationship.
        identifier = entity('UNPO-' + value, NAMES[value], kind, source, locator)
        alias(value, identifier, source, locator, 'reviewed_explicit_reference' if value != 'DOS' else 'prospective_reference_not_verified')

    for index, row in enumerate(rows[SOURCES[3]], 2):
        for target, column in [('UNLB', 'ga_logistics_base_share_usd_thousands'), ('RSCE', 'ga_regional_service_centre_share_usd_thousands')]:
            relationships.append({'from_entity_id': 'UNPO-' + row['mission_id'], 'to_entity_id': 'UNPO-' + target,
                                  'relationship': 'INCLUSIVE_APPROPRIATION_CONTAINS_COST_SHARE',
                                  'source_path': SOURCES[3], 'source_locator': f'CSV row {index}; column={column}',
                                  'period': row['funding_cycle'], 'amount_usd_thousands': row[column],
                                  'interpretation_limit': 'Accounting inclusion only; not an extra additive cost, operational dependency or organizational parentage.'})

    function_path = SOURCES[4]
    for index, row in enumerate(rows[function_path], 2):
        department, unit = row['department'], row['unit']
        locator = f'CSV row {index}; function_id={row["function_id"]}'
        parent = entity('UNPO-' + department, NAMES.get(department, department), 'DEPARTMENT', function_path, locator)
        alias(department, parent, function_path, locator)
        known = {'United Nations Truce Supervision Organization': 'UNTSO', 'UN Military Observer Group in India and Pakistan': 'UNMOGIP'}
        identifier = 'UNPO-' + known[unit] if unit in known else stable_unit(department, unit)
        kind = 'OBSERVER_MISSION' if unit in known else 'SOURCE_FUNCTION_OR_UNIT_LABEL'
        entity(identifier, unit, kind, function_path, locator)
        alias(unit, identifier, function_path, locator, 'exact_department_scoped_label')
        if unit in known:
            alias(known[unit], identifier, function_path, locator, 'reviewed_observer_mission_identity')
        relationships.append({'from_entity_id': identifier, 'to_entity_id': parent, 'relationship': 'DESCRIBED_UNDER_DEPARTMENT_IN_SOURCE',
                              'source_path': function_path, 'source_locator': locator,
                              'interpretation_limit': 'Programme presentation only; not proof of implemented organigram, exclusive ownership or full-cost inclusion.'})

    for index, row in enumerate(rows[SOURCES[5]], 2):
        identifier = 'UNPO-ALLOCATION-' + row['allocation_id']
        locator = f'CSV row {index}; allocation_id={row["allocation_id"]}'
        entity(identifier, row['allocation_scope'], 'COMPOSITE_BUDGET_ALLOCATION_NOT_ORGANIZATION', SOURCES[5], locator)
        alias(row['allocation_id'], identifier, SOURCES[5], locator)
        alias(row['allocation_scope'], identifier, SOURCES[5], locator, 'budget_scope_only_do_not_merge_with_unit')

    # Register transaction participant labels, including aggregates, without silently treating groups as entities.
    known = {a['alias']: a['entity_id'] for a in aliases if a['alias'].isupper()}
    unresolved = []
    for index, row in enumerate(rows[SOURCES[6]], 2):
        for column in ['payer_or_source_entity', 'recipient_entity']:
            value = row[column]
            locator = f'CSV row {index}; control_id={row["control_id"]}; column={column}'
            if value in known:
                alias(value, known[value], SOURCES[6], locator, 'reviewed_existing_exact_acronym')
            else:
                unresolved.append({'source_path': SOURCES[6], 'source_locator': locator, 'raw_value': value,
                                   'status': 'UNRESOLVED_AGGREGATE_OR_ALIAS', 'entity_id': None,
                                   'required_action': 'Identify constituent cost objects and periods; do not allocate to one mission by name similarity.'})

    return {'schema_version': 1, 'task_id': 'P01', 'identity_version': 'P01-1.0',
            'evidence_cutoff': '2026-10-15', 'lifecycle_as_of': None,
            'identity_rule': 'Stable source keys; exact reviewed aliases only. Identity does not establish legal or operational status.',
            'sources': inputs, 'entities': sorted(entities.values(), key=lambda x: x['entity_id']),
            'aliases': sorted(aliases, key=lambda x: (x['source_path'], x['source_locator'], x['alias'])),
            'relationships': relationships, 'unresolved_references': unresolved,
            'limitations': ['Source function labels can denote programmes, offices or cross-cutting activities; they are not all organizations.',
                           'Equivalent shared-office labels in DPPA and DPO remain separately scoped until ownership and identity are verified.',
                           'UNLB is not automatically aliased to UNGSC; broader support configurations require explicit scope verification.',
                           'Lifecycle dates, current mandates and organizational implementation remain unverified.',
                           'DOS is retained as a prospective reference only; no custodian authority or hierarchy is inferred.',
                           'This is the named retained budget/function population, not a complete census of all United Nations entities.']}


def validate(result):
    ids = [x['entity_id'] for x in result['entities']]
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate entity IDs')
    for alias in result['aliases']:
        if alias['entity_id'] not in ids:
            raise ValueError('broken alias target')
    for relationship in result['relationships']:
        if any(relationship[key] not in ids for key in ['from_entity_id', 'to_entity_id']):
            raise ValueError('broken relationship target')
    scoped = {}
    for alias in result['aliases']:
        key = (alias['source_path'], alias['alias'])
        scoped.setdefault(key, set()).add(alias['entity_id'])
    # Department-scoped unit labels can legitimately be ambiguous; never expose an unqualified resolver.
    return {'entity_count': len(ids), 'alias_rows': len(result['aliases']),
            'ambiguous_source_aliases': [{'source_path': k[0], 'alias': k[1], 'entity_ids': sorted(v)} for k, v in sorted(scoped.items()) if len(v) > 1],
            'unresolved_reference_count': len(result['unresolved_references'])}


def outputs(root):
    result = build(root)
    result['validation'] = validate(result)
    doc = f'''# Canonical entity identities — P01

[The registry](../data/portfolio/entities.json) defines {result['validation']['entity_count']} stable identities from nine retained budget, function, directive and transaction sources. It includes all 36 SPM budget entities, the eleven-entity assessed maintenance register, DPPA/DPO function labels, support-account allocation pools, RSCE, UNLB, observer missions and historical transfer references. DOS appears as a proposed evidence custodian whose authority requires verification.

Source keys and exact reviewed aliases are preserved with row/column provenance and input checksums. `UNSCOL` maps to `SPM031`; `BINUH` maps to `SPM035`. The good-offices mission in Cyprus remains distinct from `UNFICYP`. `UNSOH` remains distinct from `UNSOS`. Allocation SA04 remains a combined budget scope rather than two invented office costs.

All lifecycle states remain `UNKNOWN_NOT_VERIFIED`. Source dates and the retained evidence cutoff of 2026-10-15 do not establish present operational status. Shared office labels under DPPA and DPO remain department-scoped where identity is not verified. An ambiguous alias requires a department or source locator; consumers must never pick its first match. Aggregate client labels remain unresolved references with null entity IDs.

Relationships distinguish a source presentation from accounting inclusion. Mission appropriation shares for UNLB and RSCE are already included in the inclusive appropriation; the relationship cannot justify adding those shares again. Programme presentation does not verify operational hierarchy, exclusive ownership or implemented reform. This registry establishes identity for analysis, not legal authority.

Run `python scripts/build_canonical_entities.py --write` to regenerate and `--check` to verify. The generator validates ID uniqueness and alias/relationship targets and reports scoped alias ambiguity explicitly. Additional entity populations and lifecycle verification require a reviewed registry extension.
'''
    return {'data/portfolio/entities.json': json.dumps(result, indent=2, ensure_ascii=False) + '\n', 'docs/canonical_entities.md': doc}


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write', action='store_true')
    mode.add_argument('--check', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    for path, content in outputs(root).items():
        target = root / path
        if args.write:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
        elif not target.exists() or target.read_text() != content:
            raise SystemExit('stale canonical entities: ' + path)
    print('PASS canonical entities')


if __name__ == '__main__':
    main()
