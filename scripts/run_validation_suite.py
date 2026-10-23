#!/usr/bin/env python3
"""Explicit offline acceptance groups; never replay commands from workflow YAML."""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / 'metadata/validation_groups.json'
PARITY = ROOT / 'metadata/ci_parity_matrix.csv'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read_plan():
    return json.loads(PLAN.read_text())


def remove_install_lines(body):
    return '\n'.join(line for line in body.split('\n')
                     if not line.strip().startswith('python -m pip install'))


def check_plan(plan, root=ROOT, parity=PARITY, require_paths=True):
    require(type(plan.get('schema_version')) is int and plan['schema_version'] == 1, 'invalid plan version')
    groups = plan.get('groups')
    require(isinstance(groups, dict) and bool(groups), 'groups must be a nonempty mapping')
    ids = set()
    by_step = {}
    for group, definition in groups.items():
        require(re.fullmatch(r'[a-z0-9-]+', group) is not None, 'unsafe group name')
        require(type(definition.get('requires_r')) is bool, f'{group}: requires_r must be boolean')
        require(isinstance(definition.get('python_packages'), list), f'{group}: packages missing')
        for package in definition['python_packages']:
            require(re.fullmatch(r'[A-Za-z0-9_-]+==[0-9][A-Za-z0-9.]*', package) is not None, 'package must be exactly pinned')
        require(bool(definition.get('steps')), f'{group}: empty group')
        for step in definition['steps']:
            require(step['id'] not in ids, 'duplicate step ID')
            ids.add(step['id'])
            require(isinstance(step.get('run'), str) and step['run'].strip(), 'missing command')
            require(not re.search(r'\bpip\s+install\b|\bgit\s+(push|commit)\b|yaml\.(safe_)?load', step['run']),
                    f'{group}: setup, publication or dynamic replay in acceptance command')
            for path in re.findall(r'(?:python3?|Rscript)\s+([^\s]+\.(?:py|R))', step['run']):
                require(not Path(path).is_absolute() and '..' not in Path(path).parts, 'unsafe validation path')
                if require_paths:
                    require((root / path).is_file(), f'missing validation script: {path}')
            by_step[(group, step['id'])] = step
        legacy = definition.get('legacy_workflow')
        if legacy:
            old = root / 'history/pre_controls' / legacy
            require(old.is_file(), f'missing archived workflow: {legacy}')
            require(hashlib.sha256(old.read_bytes()).hexdigest() == definition['legacy_sha256'],
                    f'archived workflow hash drift: {legacy}')
    with Path(parity).open(newline='') as handle:
        rows = list(csv.DictReader(handle))
    require(bool(rows), 'empty parity matrix')
    keys = set()
    covered = set()
    for row in rows:
        key = (row['old_workflow'], row['old_job'], row['old_step'])
        require(key not in keys, 'duplicate legacy step mapping')
        keys.add(key)
        disposition = row['disposition']
        require(disposition in {'runner_exact', 'runner_command_with_install_promoted_to_setup',
                                'promoted_to_pinned_setup', 'retained_manual_capture'}, 'unknown parity disposition')
        if disposition.startswith('runner_'):
            target = (row['new_group'], row['new_step_id'])
            require(target in by_step, f'missing mapped step: {target}')
            require(by_step[target]['run'] == remove_install_lines(row['old_run']), 'legacy command changed')
            covered.add(target)
        elif disposition == 'promoted_to_pinned_setup':
            require(not remove_install_lines(row['old_run']).strip(), 'setup disposition discards a command')
    require({key for key in by_step if groups[key[0]].get('legacy_workflow')} == covered,
            'legacy runner step missing from parity matrix')
    return {'groups': len(groups), 'legacy_run_steps': len(rows), 'runner_steps': len(ids)}


def preflight(definition):
    require(sys.version_info[:2] == (3, 12), 'acceptance requires Python 3.12')
    if definition['requires_r']:
        require(shutil.which('Rscript') is not None, 'Rscript unavailable: full group cannot run')
    for pin in definition['python_packages']:
        package, version = pin.split('==')
        try:
            actual = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            raise ValueError(f'{pin} unavailable; install declared CI environment before execution') from None
        require(actual == version, f'{pin} required; found {actual}')


def tracked_hashes(root):
    paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).decode().split('\0')
    return {p: hashlib.sha256((root / p).read_bytes()).hexdigest() if (root / p).is_file() else None
            for p in paths if p}


def require_clean_checkout(root):
    dirty = subprocess.check_output(
        ['git', 'status', '--porcelain'], cwd=root).decode().strip()
    require(not dirty, 'validation requires a clean committed worktree/index with no nonignored untracked files to bind its receipt to HEAD')
    for path in ('scripts/run_validation_suite.py', 'metadata/validation_groups.json'):
        tracked = subprocess.run(['git', 'ls-files', '--error-unmatch', '--', path],
                                 cwd=root, capture_output=True, check=False)
        require(tracked.returncode == 0, f'validation control not committed/tracked: {path}')


def execute_group(group, definition, root=ROOT, run=subprocess.run):
    require_clean_checkout(root)
    preflight(definition)
    before = tracked_hashes(root)
    receipt = {'schema_version': 1, 'group': group, 'status': 'RUNNING', 'passed_steps': 0,
               'tested_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root).decode().strip(),
               'initial_tracked_clean': True,
               'group_plan_sha256': hashlib.sha256(json.dumps(definition, sort_keys=True).encode()).hexdigest(),
               'environment': {'python': sys.version.split()[0],
                               'packages': {p.split('==')[0]: importlib.metadata.version(p.split('==')[0])
                                            for p in definition.get('python_packages', [])},
                               'requires_r': definition.get('requires_r', False)},
               'steps': [], 'results': [], 'limitations': 'Runtime acceptance only; no operational authority or savings finding.'}
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    for step in definition['steps']:
        print(f'[{group}] {step["id"]}: {step["name"]}', flush=True)
        result = run(['/bin/bash', '-euo', 'pipefail', '-c', step['run']], cwd=root, env=env, check=False)
        receipt['results'].append({'id': step['id'], 'name': step['name'], 'exit_code': result.returncode})
        if result.returncode:
            receipt['status'] = 'FAIL'
            return receipt
        receipt['steps'].append(step['name'])
        receipt['passed_steps'] += 1
    after = tracked_hashes(root)
    changed = sorted(p for p in before if before[p] != after.get(p))
    receipt['changed_tracked_files'] = changed
    receipt['status'] = 'FAIL_TRACKED_MUTATION' if changed else 'PASS'
    return receipt


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--group')
    p.add_argument('--list', action='store_true')
    p.add_argument('--check-plan', '--checkplan', dest='check_plan', action='store_true')
    p.add_argument('--receipt', type=Path)
    args = p.parse_args()
    try:
        plan = read_plan()
        if args.receipt:
            require(not args.receipt.resolve().is_relative_to(ROOT.resolve()),
                    'runtime receipt must be outside the repository to preserve read-only execution')
        if args.list:
            print('\n'.join(plan['groups']))
            return 0
        if args.check_plan:
            print(json.dumps({'status': 'PASS_PLAN_STRUCTURE_NOT_RUNTIME', **check_plan(plan)}, indent=2))
            return 0
        require(args.group in plan['groups'], 'choose a known --group or use --list/--check-plan')
        # The full source/command parity check is independently exercised by tests.
        result = execute_group(args.group, plan['groups'][args.group])
        if args.receipt:
            args.receipt.parent.mkdir(parents=True, exist_ok=True)
            args.receipt.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result, indent=2))
        return 0 if result['status'] == 'PASS' else 1
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
