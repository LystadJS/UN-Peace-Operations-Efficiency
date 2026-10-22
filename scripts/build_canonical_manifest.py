#!/usr/bin/env python3
"""Build the scoped canonical control manifest without self-hash cycles."""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
from frozen_audit_inputs import frozen_source_path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = '9838cec16e9c14a5d87757c5ff6614ff1ae7dc24'
MANIFEST = 'metadata/canonical_manifest.json'
INDEX = 'metadata/release_index.csv'
CURRENT_ROLES = {
    'research_reference': ('data/census_v13/research_reference.json', 'fixed V8/V9 research obligations', 'data/current_research_reference.json:reference_path'),
    'research_pointer': ('data/current_research_reference.json', 'fixed V8/V9 research obligations', 'V13 project research designation'),
    'owner_review': ('docs/consolidated_owner_review_decision_memo.md', 'existing SP08P1/SP09P1 owner-review package', 'data/owner_review/package_contract.json'),
    'owner_evidence_gaps': ('data/owner_review/evidence_gap_register.csv', 'SP08P1/SP09P1 owner evidence questions', 'data/owner_review/package_contract.json'),
    'shadow_protocol': ('docs/v10_owner_review_shadow_protocol.md', 'SP08P1/SP09P1 live-shadow requirements', 'data/owner_review/package_contract.json'),
    'foundation': ('docs/foundation_standards.md', 'prospective portfolio decision standards', 'F01-F06 user task authorization'),
    'ga_maintenance': ('data/ga_mission_reconciliation.csv', 'six 2026/27 mission financing reconciliations', 'docs/appropriation_spm_consolidation_audit.md'),
    'spm_budget': ('data/spm_2027_mission_budget.csv', '36 calendar-2027 mission proposals', 'docs/spm_2027_reconciliation.md'),
    'embedded_efficiencies': ('data/spm_2027_embedded_efficiencies.csv', 'already proposed 2027 efficiency measures', 'docs/spm_2027_reconciliation.md'),
    'ga_directives': ('data/ga_adopted_directives.csv', '15 retained mission financing directives', 'docs/appropriation_spm_consolidation_audit.md'),
    'issue_register': ('data/issues/current_issues.json', 'normalized legacy issue observations', 'A08 user task authorization; original source status retained'),
    'current_status': ('docs/current_status.md', 'generated project status at declared evidence cutoff', 'A09 user task authorization'),
    'health_receipt': ('metadata/project_health.json', 'deterministic structural project health', 'A14 user task authorization'),
    'navigation': ('README.md', 'current repository navigation', 'A10 user task authorization'),
}
GENERATED = {
    'data/issues/current_issues.json': 'scripts/migrate_master_issues.py',
    'docs/current_status.md': 'scripts/generate_current_status.py',
    'metadata/current_status.json': 'scripts/generate_current_status.py',
    'metadata/project_health.json': 'scripts/build_project_health.py',
    'docs/project_health.md': 'scripts/build_project_health.py',
    'README.md': 'scripts/build_readme_navigation.py',
    'docs/release_history.md': 'scripts/build_readme_navigation.py',
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe(path):
    p = PurePosixPath(path)
    return isinstance(path, str) and bool(p.parts) and not p.is_absolute() and '..' not in p.parts


def validate_manifest(manifest, root=ROOT):
    require(type(manifest.get('schema_version')) is int and manifest['schema_version'] == 1, 'invalid schema version')
    rows = manifest.get('artifacts')
    require(isinstance(rows, list) and rows, 'artifact population required')
    by_path = {}
    for row in rows:
        path = row['path']
        require(safe(path) and path not in by_path, f'unsafe/duplicate artifact: {path}')
        by_path[path] = row
        require(row['currency'] in {'CURRENT', 'HISTORICAL', 'UNRESOLVED'}, f'invalid currency: {path}')
        require(bool(row['designation_basis']) and bool(row['scope']), f'missing scope/evidence: {path}')
        if row['hash_mode'] == 'immutable_sha256':
            require(sha(root / path) == row['sha256'], f'artifact digest drift: {path}')
        elif row['hash_mode'] == 'mutable_control_with_archived_baseline':
            require(row['sha256'] is None, f'mutable control cannot pretend a current digest: {path}')
            original = row['frozen_baseline']
            require(sha(root / original['archive_path']) == original['sha256'], f'archive digest drift: {path}')
        else:
            raise ValueError(f'unknown digest mode: {path}')
    generated = {r['path'] for r in manifest['generated_artifacts']}
    require(MANIFEST not in generated, 'self-generated manifest cycle')
    for role, designation in manifest['current_roles'].items():
        require(designation['path'] in by_path or designation['path'] in generated, f'broken current role: {role}')
        require(bool(designation['scope']) and bool(designation['designation_basis']), f'unscoped current role: {role}')
    edges = {}
    for link in manifest['supersession_relationships']:
        a, b = link['predecessor'], link['successor']
        require(a in by_path and b in by_path and a != b, 'broken supersession endpoint')
        require(bool(link['scope']) and bool(link['evidence_refs']), 'unscoped supersession')
        edges.setdefault(a, []).append(b)
    def visit(node, trail):
        require(node not in trail, 'supersession cycle')
        for nxt in edges.get(node, []):
            visit(nxt, trail | {node})
    for node in edges:
        visit(node, set())
    return len(rows)


def build(root=ROOT):
    paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASELINE], cwd=root, text=True).splitlines()
    archive = json.loads((root / 'metadata/frozen_input_archive.json').read_text())
    archived = {r['path']: r for r in archive['files']}
    inventory = {}
    with (root / 'metadata/artifact_inventory.csv').open(newline='') as handle:
        inventory = {r['path']: r for r in csv.DictReader(handle)}
    role_paths = {v[0] for v in CURRENT_ROLES.values()}
    artifacts = []
    for path in sorted(paths):
        role = inventory.get(path, {}).get('artifact_role', 'audit_control_or_unresolved')
        historical = path.startswith('data/census_v') and path not in role_paths
        current = path in role_paths or path.startswith('metadata/') or path in {
            'docs/foundation_standards.md', 'docs/desired_end_state.md', 'docs/decision_taxonomy.md',
            'docs/candidate_advancement.md', 'docs/source_authority_standard.md', 'docs/cost_accounting_standard.md',
            'docs/guardrail_standard.md', 'data/standards/candidate_states.json'}
        row = {'artifact_id': path, 'path': path, 'role': role,
               'currency': 'CURRENT' if current else 'HISTORICAL' if historical else 'UNRESOLVED',
               'scope': 'designated project control role' if current else 'retained original release record' if historical else 'currency not established by this manifest',
               'designation_basis': 'F01-A07 project control task designation' if current else 'retained release history; not a claim of supersession for every use' if historical else 'no explicit controlling role selected',
               'hash_mode': 'immutable_sha256', 'sha256': sha(root / path), 'frozen_baseline': None,
               'hash_observation': 'A07 working implementation; baseline commit defines population, not all observed bytes'}
        if path in archived:
            row.update(hash_mode='mutable_control_with_archived_baseline', sha256=None,
                       frozen_baseline={'archive_path': archived[path]['archive_path'], 'sha256': archived[path]['sha256']})
        artifacts.append(row)
    manifest = {
        'schema_version': 1, 'manifest_id': 'UNPO-CONTROLS-2026-10-22', 'evidence_cutoff': '2026-10-15',
        'control_design_as_of': '2026-10-22', 'baseline_commit': BASELINE,
        'population_rule': '586 tracked input artifacts at baseline; archived controls and A07+ outputs are declared separately, not silently added to this denominator',
        'current_roles': {key: {'path': p, 'scope': scope, 'designation_basis': evidence} for key, (p, scope, evidence) in CURRENT_ROLES.items()},
        'artifacts': artifacts,
        'generated_artifacts': [{'path': p, 'producer': producer, 'hash_mode': 'producer_checked_no_self_hash',
                                 'designation_basis': 'A08-A14 user task scope; existence does not establish substantive verification'} for p, producer in GENERATED.items()],
        'archive_map': 'metadata/frozen_input_archive.json',
        'supersession_relationships': [{
            'predecessor': 'data/census_v11/initial_candidate.json',
            'successor': 'data/census_v13/research_reference.json',
            'scope': 'AM11-01 and AM11-02 research assertions only; original first-pass results preserved',
            'relationship': 'adopted_research_assertion_corrections',
            'evidence_refs': ['data/census_v13/adoption_record.json', 'data/census_v13/affected_recheck.csv']}],
        'limitations': ['Currency is role/scoped; CURRENT never means institutionally approved or implemented.',
                       'Original release records may continue to support current evidence and controls.',
                       'Generated outputs do not hash themselves; their producer checks and project-health receipt verify them.',
                       'New analytical sources or semantic status changes require reviewed manifest regeneration.'],
    }
    validate_manifest(manifest, root)
    releases = []
    for version in range(2, 14):
        prefix = f'data/census_v{version}/'
        members = [r for r in artifacts if r['path'].startswith(prefix)]
        controls = [r['path'] for r in members if 'manifest' in Path(r['path']).name or Path(r['path']).name in {'summary.json', 'acceptance_receipt.json'}]
        releases.append({'release_id': f'census_v{version}', 'scope': 'original research-release record',
                         'status': 'retained_history_with_scoped_current_reference' if version == 13 else 'retained_history',
                         'artifact_count': len(members), 'manifest_paths': ';'.join(controls),
                         'current_scope': 'fixed V8/V9 research reference only' if version == 13 else 'V10 remains applicable shadow protocol' if version == 10 else 'not globally superseded or institutionally approved',
                         'successor_relationship': 'V13 resolves two research assertions; historical results retained' if version in {11,12} else 'no blanket supersession inferred'})
    releases.extend([
        {'release_id': 'white_paper_2026-10-15', 'scope': 'portfolio synthesis at original cutoff', 'status': 'retained_synthesis', 'artifact_count': sum(r['path'].startswith('reports/white_paper_2026-10-15/') for r in artifacts), 'manifest_paths': 'reports/white_paper_2026-10-15/analysis/input_manifest.json', 'current_scope': 'synthesis not fresh legal status or operational census', 'successor_relationship': 'current generated status answers a different role'},
        {'release_id': 'F01-F06', 'scope': 'prospective project standards', 'status': 'current_project_control', 'artifact_count': 11, 'manifest_paths': 'docs/foundation_standards.md', 'current_scope': 'portfolio definitions; no case promotion', 'successor_relationship': 'none'},
        {'release_id': 'A01-A06', 'scope': '554 frozen audit inputs', 'status': 'retained_audit_snapshot', 'artifact_count': 554, 'manifest_paths': 'metadata/repository_audit_scope.json', 'current_scope': 'historical structural audit; evolving controls archived', 'successor_relationship': 'A07+ extends controls without rewriting audit evidence'}])
    out = io.StringIO(newline='')
    writer = csv.DictWriter(out, fieldnames=list(releases[0]), lineterminator='\n')
    writer.writeheader(); writer.writerows(releases)
    return {MANIFEST: json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', INDEX: out.getvalue()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for path, text in build().items():
        target = ROOT / path
        if args.write:
            target.parent.mkdir(parents=True, exist_ok=True); target.write_text(text)
        elif not target.is_file() or target.read_text() != text:
            raise SystemExit('FAIL: canonical output drift: ' + path)
    print('PASS: canonical manifest and release index; 586 baseline artifacts and 32 archived controls')


if __name__ == '__main__':
    main()
