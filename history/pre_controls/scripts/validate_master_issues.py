#!/usr/bin/env python3
"""A05 prospective issue contract; source fidelity is distinct from substantive review."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / 'metadata/master_issue_schema.json'
CROSSWALK = ROOT / 'metadata/issue_register_crosswalk.csv'
SCOPE = ROOT / 'metadata/repository_audit_scope.json'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, f'duplicate JSON key: {key}')
            out[key] = value
        return out
    return json.loads(Path(path).read_text(), object_pairs_hook=pairs)


def structural(value, rule, schema, location='$'):
    if '$ref' in rule:
        target = schema
        for token in rule['$ref'].removeprefix('#/').split('/'):
            target = target[token]
        return structural(value, target, schema, location)
    if 'const' in rule:
        require(type(value) is type(rule['const']) and value == rule['const'], f'{location}: invalid constant')
    if 'enum' in rule:
        require(value in rule['enum'], f'{location}: unknown enum')
    kind = ('null' if value is None else 'boolean' if type(value) is bool else
            'object' if isinstance(value, dict) else 'array' if isinstance(value, list) else
            'string' if isinstance(value, str) else 'number' if type(value) in (int, float) else 'invalid')
    if 'type' in rule:
        accepted = rule['type'] if isinstance(rule['type'], list) else [rule['type']]
        require(kind in accepted, f'{location}: invalid type {kind}')
    if kind == 'number':
        require(math.isfinite(value), f'{location}: nonfinite number')
    if kind == 'string':
        require(len(value.strip()) >= rule.get('minLength', 0), f'{location}: empty string')
        if 'pattern' in rule:
            require(re.fullmatch(rule['pattern'], value) is not None, f'{location}: invalid pattern')
    if kind == 'object':
        require(set(rule.get('required', [])) <= value.keys(), f'{location}: missing fields')
        if rule.get('additionalProperties') is False:
            require(value.keys() <= rule.get('properties', {}).keys(), f'{location}: extra fields')
        for key, item in value.items():
            if key in rule.get('properties', {}):
                structural(item, rule['properties'][key], schema, f'{location}.{key}')
    if kind == 'array':
        require(len(value) >= rule.get('minItems', 0), f'{location}: insufficient items')
        if rule.get('uniqueItems'):
            require(len({json.dumps(x, sort_keys=True) for x in value}) == len(value), f'{location}: duplicate items')
        for ix, item in enumerate(value):
            structural(item, rule.get('items', {}), schema, f'{location}[{ix}]')


def present(value):
    return isinstance(value, str) and value.strip().lower() not in {'', 'unknown', 'none', 'null', 'pending', 'n/a', 'not_obtained'}


def validate(payload, schema=None, previous=None):
    schema = schema or read(SCHEMA)
    structural(payload, schema, schema)
    rows = payload['issues']
    ids, source_ids, aliases = set(), set(), set()
    for row in rows:
        iid = row['issue_id']
        require(iid not in ids, f'{iid}: duplicate issue ID')
        ids.add(iid)
        s = row['source_ref']
        key = (s['path'], s['sha256'], s['selector'])
        require(key not in source_ids, f'{iid}: same source row represented twice')
        source_ids.add(key)
        require(s['legacy_id'] in row['aliases'], f'{iid}: legacy alias missing')
        for alias in row['aliases']:
            qualified = (s['path'], alias)
            require(qualified not in aliases, f'{iid}: duplicate qualified alias')
            aliases.add(qualified)
        require(present(row['normalization_receipt']), f'{iid}: normalization receipt required')
        original_severity = s['original_record'].get('severity')
        if original_severity is not None and str(original_severity).upper() != row['severity']:
            require(present(row['severity_change_receipt']), f'{iid}: severity changed without review')
        if row['resolution_state'] in {'RESOLVED', 'SUPERSEDED'}:
            require(present(row['resolution_receipt']), f'{iid}: closure/supersession requires evidence')
        if row['gate_status'] == 'SATISFIED':
            require(row['evidence_state'] == 'VERIFIED' and present(row['resolution_receipt']),
                    f'{iid}: satisfied gate requires verified evidence and receipt')
        if row['gate_status'] == 'BLOCKED':
            require(bool(row['blocking_claims']), f'{iid}: blocked gate needs affected claims')
        if row['response_state'] in {'PARTIAL', 'OBTAINED'}:
            require(bool(row['source_evidence_refs']), f'{iid}: received evidence needs source reference')
        if row['accepted_owner_ref'] is not None:
            require(present(row['accepted_owner_ref']), f'{iid}: owner acceptance cannot be a placeholder')
        claim = row['claim']
        if claim['classification'] == 'NO_MONETARY_CLAIM':
            require(claim['amount'] is None, f'{iid}: no-claim amount must be null')
        elif claim['amount'] is not None:
            require(claim['amount'] >= 0, f'{iid}: negative benefit')
        if claim['classification'] in {'CASHABLE_SAVING', 'REALIZED_SAVING'}:
            require(claim['candidate_state'] in {'FINANCIALLY_VALIDATED', 'IMPLEMENTATION_READY', 'REALIZATION_IN_PROGRESS', 'REALIZED'}, f'{iid}: savings before financial validation')
            require(present(claim['financial_validation_ref']) and type(claim['amount']) in (float, int) and claim['amount'] > 0,
                    f'{iid}: savings need amount and financial gate receipt')
            if claim['classification'] == 'REALIZED_SAVING':
                require(claim['candidate_state'] == 'REALIZED', f'{iid}: realization evidence required')
    by_id = {r['issue_id']: r for r in rows}
    for row in rows:
        seen = {row['issue_id']}
        parent = row['parent_issue_id']
        while parent is not None:
            require(parent in by_id and parent not in seen, f'{row["issue_id"]}: absent/cyclic parent')
            seen.add(parent)
            parent = by_id[parent]['parent_issue_id']
    if previous is not None:
        validate(previous, schema)
        for old in previous['issues']:
            require(old['issue_id'] in by_id, f'{old["issue_id"]}: prior issue deleted')
            current = by_id[old['issue_id']]
            require(old['source_ref'] == current['source_ref'], f'{old["issue_id"]}: immutable source snapshot changed')
            require(set(old['aliases']) <= set(current['aliases']), f'{old["issue_id"]}: legacy alias removed')
    return len(rows)


def check_sources(payload, root=ROOT):
    for row in payload['issues']:
        source = row['source_ref']
        relative = Path(source['path'])
        require(not relative.is_absolute() and '..' not in relative.parts, 'unsafe source path')
        path = root / relative
        require(hashlib.sha256(path.read_bytes()).hexdigest() == source['sha256'], f'{path}: source hash mismatch')
        if source['format'] == 'csv':
            with path.open(newline='') as handle:
                matches = [r for r in csv.DictReader(handle) if r.get(source['id_field']) == source['selector']]
            require(len(matches) == 1, f'{path}: selector not unique')
            selected = matches[0]
        else:
            require(source['id_field'] is None and source['selector'].startswith('/'), 'JSON selector must be pointer')
            selected = read(path)
            for raw in source['selector'][1:].split('/'):
                token = raw.replace('~1', '/').replace('~0', '~')
                selected = selected[int(token)] if isinstance(selected, list) else selected[token]
        require(selected == source['original_record'], f'{path}: source row changed or altered snapshot')


def validate_crosswalk():
    scope = {x['path']: x for x in read(SCOPE)['files']}
    with CROSSWALK.open(newline='') as handle:
        rows = list(csv.DictReader(handle))
    require(bool(rows), 'crosswalk empty')
    keys = set()
    for r in rows:
        require(r['source_path'] in scope, 'crosswalk source outside frozen scope')
        require(r['source_sha256'] == scope[r['source_path']]['sha256'], 'crosswalk source hash drift')
        require(hashlib.sha256((ROOT / r['source_path']).read_bytes()).hexdigest() == r['source_sha256'], 'source bytes drift')
        key = (r['source_path'], r['source_selector'], r['source_field'])
        require(key not in keys, 'duplicate source-field crosswalk')
        keys.add(key)
        require(all(r.values()), 'crosswalk contains missing mapping')
    return len(rows), len({r['source_path'] for r in rows})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--records', type=Path)
    p.add_argument('--previous', type=Path)
    p.add_argument('--check-sources', action='store_true')
    args = p.parse_args()
    try:
        require(not (args.previous or args.check_sources) or args.records is not None, '--previous/--check-sources require --records')
        counts = validate_crosswalk()
        payload = read(args.records) if args.records else {'schema_version': 1, 'issues': []}
        n = validate(payload, previous=read(args.previous) if args.previous else None)
        if args.check_sources:
            check_sources(payload)
        print(f'PASS: {counts[0]} source-field mappings across {counts[1]} source files; {n} supplied issue records')
        print('Model only: no legacy migration, issue closure, substantive verification, or authority granted.')
        return 0
    except (ValueError, OSError, TypeError, KeyError, IndexError) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
