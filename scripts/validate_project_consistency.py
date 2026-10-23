#!/usr/bin/env python3
"""Cross-check current claims, historical lineage, and generated navigation."""
from __future__ import annotations
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def check_status(status, pointer):
    research = status['research']
    require(str(research['reference_version']) == str(pointer['reference_version']), 'research reference conflict')
    require(research['historical_supported'] == 59 and research['historical_amendment_holds'] == 2,
            'historical first-pass results rewritten')
    require(research['fixed_obligations'] == 61 and research['adopted_amendments'] == 2,
            'research obligation or adoption count conflict')
    require(research['current_holds_for_adopted_amendments'] == 0, 'adopted amendments still shown held')
    require(research['fresh_full_corpus_score'] == 'not_run', 'affected recheck promoted to full rescore')
    constraints = status['operational_constraints']
    require(constraints['live_gates'] == pointer['live_use_gates'], 'live-use gate conflict')
    require(constraints['course_watch'] == 'PAUSED', 'paused course watch presented active')
    require(constraints['cash_savings'] == 'not_estimated' and constraints['staff_time_saved'] == 'not_estimated',
            'unsupported monetary or staff-time claim')
    finance = status['finance']
    amount = lambda key: Decimal(finance[key]['usd_millions'])
    require(amount('spm_missions') + amount('rsce_spm_share') == amount('spm_total_including_rsce'),
            'SPM mission and RSCE perimeter mismatch')
    require(amount('six_mission_maintenance') <= amount('eleven_entity_maintenance'), 'mission coverage mismatch')
    require(finance['advisory_coverage']['reviewed'] + finance['advisory_coverage']['unreconciled'] ==
            finance['advisory_coverage']['population'], 'advisory denominator mismatch')


def check_local_links(root, paths):
    total = 0
    for name in paths:
        path = root / name
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if '://' in target or target.startswith('#'):
                continue
            target = target.split('#', 1)[0]
            require((path.parent / target).is_file(), f'broken current link: {name} -> {target}')
            total += 1
    return total


def check_manifest_labels(manifest):
    rows = manifest['artifacts']
    by_path = {row['path']: row for row in rows}
    require(len(by_path) == len(rows), 'duplicate canonical artifact')
    for row in rows:
        require(row.get('currency') in {'CURRENT', 'HISTORICAL', 'UNRESOLVED'},
                f'unmarked artifact currency: {row["path"]}')
        require(bool(row.get('scope')) and bool(row.get('designation_basis')), 'unscoped artifact designation')
    generated = {row['path'] for row in manifest['generated_artifacts']}
    for role, designation in manifest['current_roles'].items():
        path = designation['path']
        require(path in by_path or path in generated, f'stale current role link: {role}')
        if path in by_path:
            require(by_path[path]['currency'] == 'CURRENT', f'current role points to historical/unresolved artifact: {role}')


def check_lineage(root):
    from frozen_audit_inputs import frozen_source_path
    with (root / 'metadata/lineage_nodes.csv').open(newline='') as handle:
        nodes = list(csv.DictReader(handle))
    by_id = {r['node_id']: r for r in nodes}
    require(len(by_id) == len(nodes), 'duplicate lineage node')
    for row in nodes:
        path = frozen_source_path(root, row['path'])
        require(path.is_file(), f'missing lineage source: {row["path"]}')
        require(hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'], 'historical lineage hash drift')
    with (root / 'metadata/lineage_edges.csv').open(newline='') as handle:
        edges = list(csv.DictReader(handle))
    ids = set()
    for edge in edges:
        require(edge['edge_id'] not in ids, 'duplicate lineage edge')
        ids.add(edge['edge_id'])
        require(edge['source'] in by_id and edge['target'] in by_id, 'dangling lineage edge')
        require(edge['evidence_file'] in by_id, 'lineage evidence missing')
    return len(nodes), len(edges)


def validate(root=ROOT):
    import build_canonical_manifest as canonical
    import generate_current_status as current
    import build_readme_navigation as navigation
    status = current.build(root)
    pointer = json.loads((root / 'data/current_research_reference.json').read_text())
    manifest = json.loads((root / 'metadata/canonical_manifest.json').read_text())
    canonical.validate_manifest(manifest, root)
    check_manifest_labels(manifest)
    check_status(status, pointer)
    for producer in (current, navigation):
        for name, content in producer.outputs(root).items():
            require((root / name).is_file(), f'missing generated artifact: {name}')
            actual = (root / name).read_bytes()
            expected = content.encode() if isinstance(content, str) else content
            require(actual == expected, f'stale or contradictory generated output: {name}')
    for name in ('README.md', 'docs/current_status.md'):
        text = (root / name).read_text()
        require(not re.search(r'watch\s+(?:is\s+)?active|two remain on amendment hold', text, re.I),
                f'stale current status wording: {name}')
    links = check_local_links(root, ('README.md', 'docs/current_status.md', 'docs/release_history.md'))
    nodes, edges = check_lineage(root)
    return {'status': 'PASS_cross_project_consistency', 'current_links': links,
            'historical_lineage_nodes': nodes, 'historical_lineage_edges': edges,
            'limitation': 'Declared source status and static lineage only; no new operational or legal verification.'}


def main():
    try:
        print(json.dumps(validate(), indent=2))
        return 0
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
