#!/usr/bin/env python3
"""Build a deterministic structural-health receipt; never infer runtime CI success."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = 'metadata/project_health.json'
GUIDE = 'docs/project_health.md'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def summarize(status, manifest, issues, migration):
    require(status['operational_constraints']['cash_savings'] == 'not_estimated',
            'unsupported savings in status input')
    rows = issues['issues']
    require(len(rows) == migration['issue_count'], 'issue migration count mismatch')
    require(len({row['issue_id'] for row in rows}) == len(rows), 'duplicate issue')
    return {
        'manifest_artifacts': len(manifest['artifacts']),
        'current_roles': len(manifest['current_roles']),
        'issue_observations': len(rows),
        'issue_resolution_states': dict(sorted(Counter(row['resolution_state'] for row in rows).items())),
        'issue_gate_states': dict(sorted(Counter(row['gate_status'] for row in rows).items())),
        'live_gates': status['operational_constraints']['live_gates'],
        'course_watch': status['operational_constraints']['course_watch'],
        'cash_savings': status['operational_constraints']['cash_savings'],
        'staff_time_saved': status['operational_constraints']['staff_time_saved'],
    }


def build(root=ROOT):
    import build_canonical_manifest as canonical
    import generate_current_status as current
    import validate_master_issues as issue_rules
    paths = ['metadata/canonical_manifest.json', 'metadata/current_status.json',
             'data/issues/current_issues.json', 'metadata/issue_migration_receipt.json',
             'metadata/frozen_input_archive.json', 'metadata/validation_groups.json',
             'metadata/ci_parity_matrix.csv', 'metadata/publication_policy.json',
             'README.md', 'docs/current_status.md', 'docs/release_history.md',
             'scripts/build_project_health.py', 'scripts/run_validation_suite.py',
             'scripts/publish_release.py', 'scripts/validate_project_consistency.py',
             'scripts/build_canonical_manifest.py', 'scripts/generate_current_status.py',
             'scripts/validate_master_issues.py', 'scripts/frozen_audit_inputs.py',
             'metadata/master_issue_schema.json']
    paths.extend(sorted(path.relative_to(root).as_posix() for path in (root/'.github/workflows').glob('*.yml')))
    loaded = {name: (root/name).read_bytes() for name in paths}
    read = lambda path: json.loads(loaded[path])
    manifest = read('metadata/canonical_manifest.json')
    canonical.validate_manifest(manifest, root)
    status = read('metadata/current_status.json')
    require(current.build(root) == status, 'current status is stale')
    for name, body in current.outputs(root).items():
        expected = body.encode() if isinstance(body, str) else body
        require((root/name).read_bytes() == expected, f'current status rendering drift: {name}')
    issues = read('data/issues/current_issues.json')
    issue_rules.validate(issues)
    issue_rules.check_sources(issues, root)
    migration = read('metadata/issue_migration_receipt.json')
    summary = summarize(status, manifest, issues, migration)
    return {
        'schema_version': 1,
        'receipt_id': 'A14-STRUCTURAL-2026-10-22',
        'control_design_as_of': '2026-10-22',
        'evidence_scope': 'Retained research and finance evidence through source-specific cutoffs; no new UN source review.',
        'status': 'STRUCTURAL_CHECKS_PASSED_RUNTIME_CI_NOT_ASSERTED',
        'summary': summary,
        'checks': {
            'canonical_manifest_hashes': 'PASS',
            'current_status_regeneration': 'PASS',
            'migrated_issue_schema': 'PASS',
            'migrated_source_snapshots': 'PASS',
            'issue_migration_count': 'PASS',
        },
        'source_sha256': {name: hashlib.sha256(loaded[name]).hexdigest() for name in sorted(loaded)},
        'runtime_ci': {
            'status': 'NOT_ATTESTED_BY_THIS_RECEIPT',
            'required_evidence': 'Exact tested commit, pinned Python/R environment, command-group results and unmodified-tree receipt.',
            'reason': 'Deterministic source checks do not execute all historical R/PDF workflows or query GitHub Actions.',
        },
        'limitations': [
            'Issue observations include historical amendments and control constraints; this is not a count of current UN operational defects.',
            'The 287 profile-only datasets and 196 recognized dynamic-lineage expressions remain review gaps from A01-A06.',
            'No owner approvals, live trials, realized savings, or UNGA81 compliance findings are established by this receipt.',
            'This receipt excludes its own bytes and rendered guide from its inputs to prevent self-hash cycles.',
        ],
    }


def render(receipt):
    summary = receipt['summary']
    return f'''# A14 — Project health

This document is generated from [the machine-readable health receipt](../metadata/project_health.json).

**Structural checks passed; full runtime CI is not asserted by this receipt.**

The receipt checks {summary['manifest_artifacts']} canonical input-artifact records, {summary['current_roles']} designated current roles and {summary['issue_observations']} migrated issue observations. It validates current-status regeneration, source snapshots, issue identities and migration counts. Source hashes make the result reproducible for unchanged inputs; publishing it does not supply institutional approval or operational evidence.

Cash savings and staff time saved remain **not estimated**. Both reporting live-use gates remain closed, and the course watch remains **paused**. Historical observations, current questions and control constraints are included together in source-observation totals; resolution and gate-status distributions remain separate. None is automatically a verified operational defect.

## Reproduction

```sh
python -B scripts/build_project_health.py --write
python -B scripts/build_project_health.py --check
python -B tests/check_project_health.py
```

The generator contains no network calls, source collection, operational activation or CI execution. A fixed input set produces identical bytes. It hashes neither itself recursively through the output nor the generated guide. Actual CI acceptance requires a separate exact-commit runtime receipt in the pinned Python/R environment.

The retained dataset and dynamic-lineage gaps remain open. See [current status](current_status.md), [the issue migration](issue_migration.md), [CI validation](ci_validation.md) and [publication controls](publication_workflow.md) for their scope and limits.
'''


def outputs(root=ROOT):
    receipt = build(root)
    return {OUTPUT: json.dumps(receipt, indent=2, sort_keys=True)+'\n', GUIDE: render(receipt)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        for name, body in outputs().items():
            path = ROOT/name
            if args.write:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(body)
            else:
                require(path.is_file() and path.read_text() == body, f'health output drift: {name}')
        print('PASS: deterministic structural-health receipt; runtime CI is not attested')
        return 0
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
