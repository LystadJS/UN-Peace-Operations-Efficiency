#!/usr/bin/env python3
"""Check the frozen audit scope and reconcile A01/A02/A06 coverage.

Run after generating the six independent audit products. This checks coverage
and preservation; it does not establish that inferred semantics are correct.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
from frozen_audit_inputs import frozen_source_path

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_scope(root):
    scope = json.loads((root / 'metadata/repository_audit_scope.json').read_text())
    files = scope['files']
    require(bool(files), 'empty audit scope')
    paths = set()
    for row in files:
        name = row['path']
        path = PurePosixPath(name)
        require(not path.is_absolute() and '..' not in path.parts, f'unsafe scope path: {name}')
        require(name not in paths, f'duplicate scope path: {name}')
        paths.add(name)
        local = frozen_source_path(root, name)
        require(local.is_file() and not local.is_symlink(), f'missing or symlinked scope file: {name}')
        content = local.read_bytes()
        require(len(content) == row['size_bytes'], f'changed input size: {name}')
        require(hashlib.sha256(content).hexdigest() == row['sha256'], f'changed input hash: {name}')
    return scope, paths


def table_paths(root, name, key='path'):
    with (root / name).open(newline='', encoding='utf-8') as handle:
        reader = csv.DictReader(handle)
        require(reader.fieldnames is not None and key in reader.fieldnames,
                f'{name}: missing {key} column')
        rows = list(reader)
    paths = [row[key] for row in rows]
    require(len(paths) == len(set(paths)), f'{name}: duplicate path')
    return set(paths)


def main():
    try:
        scope, paths = validate_scope(ROOT)
        expected = {
            'metadata/artifact_inventory.csv': paths,
            'metadata/dataset_registry.csv': {p for p in paths if Path(p).suffix in {'.csv', '.json'}},
            'metadata/workflow_audit.csv': {p for p in paths if p.startswith('.github/workflows/')},
        }
        for table, wanted in expected.items():
            actual = table_paths(ROOT, table, 'workflow_path' if table.endswith('workflow_audit.csv') else 'path')
            require(actual == wanted,
                    f'{table}: coverage mismatch; missing={sorted(wanted-actual)} extra={sorted(actual-wanted)}')
        print(json.dumps({'status': 'PASS_scope_preservation_and_cross_product_coverage',
                          'scope_id': scope['scope_id'],
                          'frozen_files': len(paths),
                          'tracked_inputs': sum(row['tracked'] for row in scope['files']),
                          'datasets': len(expected['metadata/dataset_registry.csv']),
                          'workflows': len(expected['metadata/workflow_audit.csv']),
                          'limitation': 'Coverage and byte preservation only; semantic and dynamic-lineage gaps remain explicit.'}, indent=2))
        return 0
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
