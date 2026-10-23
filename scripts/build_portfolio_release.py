#!/usr/bin/env python3
"""I12 deterministic local public-baseline manifest; does not publish a release."""
import argparse
import fnmatch
import hashlib
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'data/portfolio/release_manifest.json'
DOCUMENT = 'docs/portfolio_release.md'
PREFIXES = ('data/reforms/', 'data/portfolio/', 'data/cases/', 'data/evidence_requests/',
            'data/pilots/', 'data/adjudications/', 'data/realization/', 'data/priority_cases/',
            'docs/', 'scripts/', 'tests/', '.github/workflows/', 'metadata/')
EXCLUSIONS = {
    MANIFEST: 'Self hash excluded to avoid a circular manifest; manifest is verified by regeneration.',
    DOCUMENT: 'Rendered manifest companion excluded to avoid a circular output dependency.',
    'README.md': 'Generated navigation consumes current status; checked separately by navigation validation.',
    'metadata/current_status.json': 'Generated combined status may consume this manifest; validated separately.',
    'docs/current_status.md': 'Generated combined status may consume this manifest; validated separately.',
    'metadata/project_health.json': 'Generated structural health may consume release controls; validated separately.',
    'docs/project_health.md': 'Generated structural health may consume release controls; validated separately.',
    'metadata/readme_navigation.json': 'Generated navigation receipt may consume combined status; validated separately.',
    'metadata/workflow_execution.json': 'Runtime/orchestration receipt is separate from deterministic artifact identity.',
    'docs/workflow_execution.md': 'Runtime/orchestration receipt is separate from deterministic artifact identity.',
    'data/portfolio/workflow_execution.json': 'Runtime/orchestration receipt is separate from deterministic artifact identity.',
    'docs/portfolio_agent_review.md': 'Separate-agent final review may examine this manifest; excluding avoids review/hash cycle.',
}
REQUIRED = (
    'data/reforms/obligation_schema.json', 'data/reforms/unga80_instruments.json',
    'data/reforms/unga81_instruments.json', 'data/reforms/unga80_actions.json',
    'data/reforms/unga81_actions.json', 'data/reforms/baseline_release.json',
    'data/portfolio/entities.json', 'data/portfolio/dataset_contracts.json',
    'data/portfolio/coverage_matrix.json', 'data/portfolio/financial_baseline.json',
    'data/portfolio/interventions.json', 'data/portfolio/benefit_pools.json',
    'data/portfolio/public_portfolio.json', 'data/portfolio/verified_benefit_ledger.json',
    'data/adjudications/execution_gates.json', 'data/realization/implementation_gates.json',
    'data/pilots/charters.json', 'data/pilots/thresholds.json', 'data/pilots/request_status.json',
    'data/pilots/rehearsal_receipt.json', 'docs/leadership_portfolio_report.md',
    'docs/reform_independent_review.md', 'docs/decision_portfolio.md',
    'docs/secure_evidence_intake.md', 'scripts/build_portfolio_release.py',
    'tests/check_portfolio_release.py', '.github/workflows/reusable_validation.yml',
    'metadata/validation_groups.json',
    'data/priority_cases/progress.json', 'data/priority_cases/research_candidates.json',
    'docs/priority_case_progress.md',
) + tuple(f'data/cases/C{i:02}.json' for i in range(1, 15)) + tuple(f'docs/cases/C{i:02}.md' for i in range(1, 15)) + (
    'data/evidence_requests/E01_rsce.json', 'data/evidence_requests/E02_assets.json',
    'data/evidence_requests/E03_haiti.json', 'data/evidence_requests/E04_ga_directed.json',
    'data/evidence_requests/E05_training.json', 'data/evidence_requests/E06_reporting_owners.json',
)
FORBIDDEN_PARTS = {'private', 'restricted', 'internal', '.git', '.aws', '.codex', '.agents'}
FORBIDDEN_NAMES = ('*.umojaxlsx', '*.internal.*', '*.restricted.*', '*.pem', '*.key', '.env', '.env.*')


def safe_path(path):
    if not isinstance(path, str) or not path or '\\' in path:
        return False
    value = PurePosixPath(path)
    return (not value.is_absolute() and all(p not in ('', '.', '..') for p in path.split('/'))
            and not any(p.lower() in FORBIDDEN_PARTS for p in value.parts)
            and not any(fnmatch.fnmatch(value.name.lower(), pattern) for pattern in FORBIDDEN_NAMES))


def scope_files(root):
    files = set()
    for prefix in PREFIXES:
        folder = root / prefix
        if folder.is_symlink():
            raise ValueError('symlink scope directory: ' + prefix)
        if not folder.is_dir():
            raise ValueError('missing declared scope directory: ' + prefix)
        for path in folder.rglob('*'):
            relative = path.relative_to(root).as_posix()
            # Python caches are execution debris, not release candidates.
            if '__pycache__' in path.parts or path.suffix in ('.pyc', '.pyo'):
                continue
            if not safe_path(relative) or path.is_symlink():
                raise ValueError('unsafe or restricted release candidate: ' + relative)
            if path.is_file() and relative not in EXCLUSIONS:
                files.add(relative)
    missing = sorted(set(REQUIRED) - files)
    if missing:
        raise ValueError('missing required release artifacts: ' + ', '.join(missing))
    return sorted(files)


def read(root, path):
    return json.loads((root / path).read_text(encoding='utf-8'))


def check_claim_boundary(root):
    public = read(root, 'data/portfolio/public_portfolio.json')
    if public.get('release_class') != 'PUBLIC_VALIDATION_BASELINE' or public.get('decision_grade_portfolio') != 'BLOCKED':
        raise ValueError('unsupported public release class or decision-grade claim')
    if public.get('substantive_operational_adjudications') != 0:
        raise ValueError('operational adjudication facts changed; release review required')
    gates = public.get('completion_gates', [])
    if len(gates) != 4:
        raise ValueError('missing four completion gates')
    statuses = [g.get('status') for g in gates]
    if statuses != ['PARTIAL', 'PARTIAL', 'BLOCKED', 'BLOCKED']:
        raise ValueError('unsupported completion gate claims')
    ledger = read(root, 'data/portfolio/verified_benefit_ledger.json')
    totals = ledger.get('reconciliation', {})
    if (ledger.get('entries') != [] or totals.get('recognized_records') != 0
            or totals.get('headline_realized_savings_usd') is not None
            or totals.get('cross_class_total') is not None
            or not totals.get('class_totals_usd')
            or any(x is not None for x in totals['class_totals_usd'].values())):
        raise ValueError('unsupported benefit recognition in public validation baseline')
    for i in range(1, 15):
        case = read(root, f'data/cases/C{i:02}.json')
        benefits = case.get('benefits', {})
        categories = ('cashable_saving', 'realized_saving', 'capacity_gain', 'recovery', 'cost_avoidance')
        if (case.get('candidate_state') != 'SCREENING_CANDIDATE'
                or case.get('disposition') != 'BLOCKED_PENDING_EVIDENCE'
                or benefits.get('status') != 'NOT_ESTIMATED'
                or any(k not in benefits or benefits[k] is not None for k in categories)):
            raise ValueError('unsupported case advancement or benefit claim')
    execution = read(root, 'data/adjudications/execution_gates.json')
    if (execution.get('actual_operational_audits_completed') != 0
            or len(execution.get('records', [])) != 21
            or any(row.get('execution_status') != 'BLOCKED_NOT_EXECUTED'
                   or row.get('substantive_audit_completed') is not False
                   or row.get('execution_authorized') is not False
                   for row in execution.get('records', []))):
        raise ValueError('operational execution facts changed; release review required')
    realization = read(root, 'data/realization/implementation_gates.json')
    if (realization.get('approved_interventions') != [] or realization.get('executions') != []
            or realization.get('institutional_approval_obtained') is not False):
        raise ValueError('implementation facts changed; release review required')
    return gates


def build(root=ROOT):
    paths = scope_files(root)
    gates = check_claim_boundary(root)
    return {
        'schema_version': 1, 'release_id': 'UNPO-PUBLIC-VALIDATION-BASELINE-1', 'task_id': 'I12',
        'release_class': 'PUBLIC_VALIDATION_BASELINE', 'decision_grade_portfolio': 'BLOCKED',
        'institutional_approval': 'NOT_OBTAINED', 'publication_action': 'LOCAL_MANIFEST_ONLY',
        'source_cutoffs': {
            'reform_scoped_source_review': '2026-10-23',
            'financial_retained_baseline': read(root, 'data/portfolio/financial_baseline.json')['evidence_cutoff'],
            'historical_research_and_owner_package': '2026-10-15',
            'case_evidence_cutoffs': {f'C{i:02}': read(root, f'data/cases/C{i:02}.json')['evidence_cutoff'] for i in range(1, 15)},
            'interpretation': 'Distinct retained observation/review cutoffs; release assembly does not refresh every source.',
        },
        'completion_gates': gates, 'substantive_operational_adjudications': 0,
        'verified_benefits': 'NOT_ESTIMATED', 'scope_prefixes': list(PREFIXES),
        'population_rule': 'All filesystem files under declared prefixes, including ready untracked files; explicit exclusions and transient Python caches omitted. Not derived from git tracking or current HEAD.',
        'required_core_artifacts': list(REQUIRED), 'exclusions': EXCLUSIONS,
        'transient_exclusions': ['**/__pycache__/**', '*.pyc', '*.pyo'],
        'artifact_count': len(paths),
        'artifacts': [{'path': path, 'sha256': hashlib.sha256((root / path).read_bytes()).hexdigest(),
                       'bytes': (root / path).stat().st_size} for path in paths],
        'runtime_validation': 'NOT_ATTESTED_BY_THIS_MANIFEST; use exact-commit hosted/local validation receipts separately.',
        'privacy_limit': 'Rejects restricted/secret path patterns and symlinks; not a content-level security certification. Approved public derivatives and separate boundary validation remain required.',
        'refresh_rule': 'Rebuild after all source edits and before final validation. Any eligibility/benefit change requires substantive review and a new release policy, not merely updated hashes.',
    }


def validate_manifest(value, root=ROOT):
    if value.get('release_class') != 'PUBLIC_VALIDATION_BASELINE' or value.get('decision_grade_portfolio') != 'BLOCKED':
        raise ValueError('unsupported release declaration')
    actual = value.get('artifacts', [])
    paths = [row.get('path') for row in actual]
    if any(not safe_path(path) for path in paths) or len(paths) != len(set(paths)):
        raise ValueError('unsafe or duplicate manifest paths')
    if any(path in EXCLUSIONS for path in paths):
        raise ValueError('excluded output included in manifest')
    expected = build(root)
    if value != expected:
        raise ValueError('manifest differs from current scoped files or declarations')
    return {'artifact_count': len(actual), 'release_class': value['release_class']}


def render(value):
    return f'''# Public validation baseline release — I12

**PUBLIC_VALIDATION_BASELINE; decision-grade portfolio BLOCKED.** This local release manifest records {value['artifact_count']} filesystem artifacts with byte counts and SHA-256 hashes. It does not create a GitHub release, publish files, authorize operational implementation or attest runtime CI.

The [machine-readable manifest](../data/portfolio/release_manifest.json) declares its directory populations, required core artifacts, source cutoffs and explicit exclusions. It includes ready untracked files so that the final review population does not silently omit work awaiting commit. Root integration must regenerate after all edits, commit the complete reviewed population and validate the exact final commit separately.

All fourteen cases remain screening candidates blocked pending evidence, with zero substantive operational adjudications and unestimated benefits. Foundation and validation-system completion are partial; decision-portfolio and realization gates remain blocked. Read the [leadership report](leadership_portfolio_report.md) and [public portfolio](decision_portfolio.md) for the substantive limits. Scoped reform review is through 2026-10-23; retained financial baseline is through {value['source_cutoffs']['financial_retained_baseline']}; historical research/owner controls retain their 2026-10-15 cutoff. Individual case dates remain explicit.

The manifest and this rendering omit their own hashes. Generated current-status, navigation, project-health and runtime/orchestration outputs are separately checked to avoid dependency cycles; the final agent review is excluded because it can inspect the manifest. The exclusions are not permission to skip their validation. Declared directory hashing includes both new roadmap work and retained control/document dependencies; it is not a claim that all entries are new research or current operational evidence.

Restricted/secret path patterns, path traversal, duplicate paths, symlinks, missing core artifacts, changed hashes and unsupported eligibility or benefit declarations cause failure. These checks do not certify absence of sensitive content; use the separate [public evidence boundary](secure_evidence_intake.md), substantive review and approved derivatives. Synthetic fixtures remain software evidence only.

Run `python -B scripts/build_portfolio_release.py --write` after integration, then `--check` and `python -B tests/check_portfolio_release.py`. No timestamp, current HEAD, self hash or network operation is used. Exact-commit runtime validation is a separate receipt.
'''


def outputs(root=ROOT):
    result = build(root)
    return {MANIFEST: json.dumps(result, indent=2, ensure_ascii=False) + '\n', DOCUMENT: render(result)}


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write', action='store_true')
    mode.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for path, content in outputs().items():
        target = ROOT / path
        if args.write:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding='utf-8')
        elif not target.exists() or target.read_text(encoding='utf-8') != content:
            raise SystemExit('stale portfolio release: ' + path)
    if args.check:
        validate_manifest(read(ROOT, MANIFEST))
    print('PASS local public validation release; decision-grade portfolio remains blocked')


if __name__ == '__main__':
    main()
