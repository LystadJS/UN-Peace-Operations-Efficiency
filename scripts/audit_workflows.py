#!/usr/bin/env python3
"""Static, non-executing audit of workflows in the frozen A01–A06 scope.

Requires PyYAML (tested with 6.0.3). BaseLoader preserves GitHub's `on` key
without YAML 1.1 boolean coercion. Run commands are inspected, never executed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import itertools
import json
from pathlib import Path
import re
import shlex
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCOPE = 'metadata/repository_audit_scope.json'
OUT = 'metadata/workflow_audit.csv'
OVERLAP = 'metadata/workflow_overlap.csv'
DOC = 'docs/ci_consolidation_plan.md'


class UniqueLoader(yaml.BaseLoader):
    pass


def mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f'duplicate YAML key: {key}')
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)


def parse(body):
    data = yaml.load(body, Loader=UniqueLoader)
    if not isinstance(data, dict) or 'on' not in data or not isinstance(data.get('jobs'), dict):
        raise ValueError('workflow needs literal on and jobs mapping')
    if not isinstance(data['on'], (str, list, dict)):
        raise ValueError('unsupported trigger shape')
    return data


def j(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def triggers(value):
    if isinstance(value, str):
        return {value: {}}
    if isinstance(value, list):
        return {x: {} for x in value}
    return value


def permissions(workflow, job):
    level = 'job' if 'permissions' in job else 'workflow' if 'permissions' in workflow else 'repository_default_unknown'
    raw = job.get('permissions') if 'permissions' in job else workflow.get('permissions')
    if isinstance(raw, dict):
        return {'level': level, 'explicit_scopes': raw, 'other_scopes': 'none'}
    return {'level': level, 'value': raw or 'unknown_repository_or_organization_default'}


def pip_exact_pins(command):
    """Conservatively recognize explicit package==version install arguments."""
    try:
        tokens = shlex.split(command, comments=True)
    except ValueError:
        return False
    if 'install' not in tokens or not any(x == 'pip' or re.fullmatch(r'pip\d*', x) for x in tokens):
        return False
    arguments = tokens[tokens.index('install') + 1:]
    packages = [x for x in arguments if x not in {'--quiet', '-q', '--upgrade', '-U', '--no-deps'}]
    return bool(packages) and all(re.fullmatch(r'[A-Za-z0-9_.-]+(?:\[[A-Za-z0-9_,.-]+\])?==[A-Za-z0-9_.+!-]+', x) for x in packages)


def inspect(path, body, tracked=True):
    data = parse(body)
    runs, actions, installs, effective, scripts, mutations, conditions, artifacts = [], [], [], {}, set(), [], [], []
    for job_id, job in data['jobs'].items():
        effective[job_id] = permissions(data, job)
        if 'uses' in job:
            actions.append({'location': job_id, 'uses': job['uses'], 'kind': 'reusable_workflow'})
        for number, step in enumerate(job.get('steps', []), 1):
            location = f'{job_id}:step{number}'
            if 'uses' in step:
                uses = step['uses']
                ref = uses.rsplit('@', 1)[1] if '@' in uses else ''
                actions.append({'location': location, 'uses': uses, 'pin': 'commit_sha' if re.fullmatch(r'[0-9a-fA-F]{40}', ref) else 'tag_or_branch' if ref else 'local_or_unpinned'})
                if uses.startswith(('actions/upload-artifact@', 'actions/download-artifact@')):
                    artifacts.append({'location': location, 'uses': uses, 'with': step.get('with', {}), 'if': step.get('if', '')})
            run = step.get('run', '')
            if not isinstance(run, str):
                raise ValueError(f'{location}: run is not scalar')
            runs.append(run)
            for line in run.splitlines():
                stripped = line.strip()
                if re.match(r'(?:python\d*(?:\.\d+)?\s+-m\s+pip\s+install|pip\d*\s+install|sudo\s+apt-get\s+(?:install|update))\b', stripped):
                    installs.append({'location': location, 'command': stripped, 'all_python_packages_exactly_pinned': pip_exact_pins(stripped)})
                if re.match(r'git\s+(?:commit|push|pull|rebase|restore|checkout|add)\b', stripped):
                    mutations.append({'location': location, 'command': stripped})
            for match in re.finditer(r'\b(?:python\d*(?:\.\d+)?|Rscript)\s+((?:scripts|tests|reports)/[A-Za-z0-9_./-]+\.(?:py|R))\b', run):
                scripts.add(match.group(1))
            if 'if' in step and run:
                conditions.append({'location': location, 'if': step['if'], 'publishes': bool(re.search(r'^\s*git\s+push\b', run, re.M))})
    whole = '\n'.join(runs)
    trig = triggers(data['on'])
    direct_main = bool(re.search(r'^\s*git\s+push\s+[^\n]*(?:HEAD:main|\bmain\b)', whole, re.M))
    delegates = '.github/workflows/validate.yml' in whole and 'subprocess.run' in whole
    historical_artifact = bool(re.search(r'(?:actions/artifacts/\d+|run-id:\s*\d+)', body))
    return {
        'workflow_path': path, 'name': data.get('name', path),
        'scope_status': 'baseline_tracked' if tracked else 'preexisting_foundation_untracked',
        'sha256': hashlib.sha256(body.encode()).hexdigest(),
        'trigger_events': ';'.join(sorted(trig)), 'trigger_configuration_json': j(trig),
        'scheduled': str('schedule' in trig).lower(), 'manually_dispatchable': str('workflow_dispatch' in trig).lower(),
        'permissions_json': j(effective), 'jobs': ';'.join(data['jobs']),
        'direct_invoked_scripts_json': j(sorted(scripts)),
        'delegates_validate_workflow_run_steps': str(delegates).lower(),
        'mutation_commands_json': j(mutations), 'direct_main_push': str(direct_main).lower(),
        'publication_step_conditions_json': j(conditions),
        'actions_json': j(actions), 'dependency_install_commands_json': j(installs),
        'artifact_actions_json': j(artifacts),
        'concurrency_json': j(data.get('concurrency', {})),
        'hardcoded_capture_artifact_reference': str(historical_artifact).lower(),
        'obsolescence_status': 'review_historical_replay_and_retention_dependencies' if historical_artifact or re.search(r'v[2-9]|2026-10-15', path) else 'not_established',
        'mutation_scope': 'explicit_direct_main_publication' if direct_main else 'explicit_local_git_mutation' if mutations else 'no_explicit_git_publication_detected_script_side_effects_not_excluded',
        'review_recommendation': 'separate_validation_capture_and_explicit_release' if direct_main else 'retain_guards_consolidate_shared_setup_where_parity_proven',
    }


def rows_csv(rows, fields):
    buf = io.StringIO(newline='')
    writer = csv.DictWriter(buf, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def outputs(root=ROOT):
    scope = json.loads((root / SCOPE).read_text())
    rows = []
    for entry in scope['files']:
        path = entry['path']
        if not path.startswith('.github/workflows/'):
            continue
        body = (root / path).read_text()
        if hashlib.sha256(body.encode()).hexdigest() != entry['sha256']:
            raise ValueError(f'frozen workflow changed: {path}')
        rows.append(inspect(path, body, entry['tracked']))
    rows.sort(key=lambda x: x['workflow_path'])
    overlaps = []
    for left, right in itertools.combinations(rows, 2):
        shared = sorted(set(json.loads(left['direct_invoked_scripts_json'])) & set(json.loads(right['direct_invoked_scripts_json'])))
        if shared:
            overlaps.append({'left_workflow': left['workflow_path'], 'right_workflow': right['workflow_path'], 'overlap_type': 'direct_script_reference', 'shared_targets_json': j(shared), 'interpretation': 'shared target; flags inputs modes and release guarantees may differ; not proof either run is redundant'})
        if left['delegates_validate_workflow_run_steps'] == right['delegates_validate_workflow_run_steps'] == 'true':
            overlaps.append({'left_workflow': left['workflow_path'], 'right_workflow': right['workflow_path'], 'overlap_type': 'dynamic_acceptance_suite_delegation', 'shared_targets_json': j(['.github/workflows/validate.yml:jobs.structural-quality-gates.steps[*].run']), 'interpretation': 'runtime acceptance delegation; setup/actions and conditions are not replayed automatically'})
    fields = list(rows[0])
    overlap_fields = ['left_workflow','right_workflow','overlap_type','shared_targets_json','interpretation']
    return {OUT: rows_csv(rows, fields), OVERLAP: rows_csv(overlaps, overlap_fields), DOC: document(rows, overlaps, scope)}


def document(rows, overlaps, scope):
    pubs = [r for r in rows if r['direct_main_push'] == 'true']
    captures = [r for r in rows if r['hardcoded_capture_artifact_reference'] == 'true']
    delegates = [r for r in rows if r['delegates_validate_workflow_run_steps'] == 'true']
    actions = [x for r in rows for x in json.loads(r['actions_json'])]
    pins = sum(x.get('pin') == 'commit_sha' for x in actions)
    event_counts = {e:sum(e in r['trigger_events'].split(';') for r in rows) for e in sorted({e for r in rows for e in r['trigger_events'].split(';')})}
    lines = [
        '# A06 — CI consolidation plan', '',
        f"Static audit of **{len(rows)} frozen workflows** in scope `{scope['scope_id']}` at baseline `{scope['baseline_commit']}`: 27 tracked workflows plus the pre-existing untracked F01–F06 workflow. Counts describe configuration, not GitHub run history or enabled state. No workflows were changed or executed by this audit.", '',
        'The source of truth is [workflow_audit.csv](../metadata/workflow_audit.csv); [workflow_overlap.csv](../metadata/workflow_overlap.csv) records target overlap without declaring either invocation redundant. The [frozen scope](../metadata/repository_audit_scope.json) pins all inspected bytes.', '',
        '## Observed configuration', '',
        f'- Trigger counts: {j(event_counts)}. Multiple triggers can belong to one workflow.',
        f'- {len(pubs)} workflows contain explicit shell pushes to `main`; these mix validation/build and repository publication.',
        f'- {len(delegates)} workflows dynamically replay `validate.yml` run steps through Python subprocess calls. These replay commands, not their setup actions, inherited step conditions, environment or job semantics.',
        f'- {len(captures)} workflows reference fixed capture artifact IDs or fixed run IDs. Availability, retention expiry and current need were not tested; these are replay/retention review candidates, not verified obsolete workflows.',
        f'- {len(actions)} action references were inspected; {pins} use full commit-SHA pins. Tag-based action refs are mutable supply-chain dependencies. Version preservation may require exact tool versions, not indiscriminate upgrades.',
        f'- {len(overlaps)} pairwise overlap observations identify shared direct script references or dynamic acceptance delegation. Script identity alone does not imply matching flags, source inputs, evaluation modes or authority.', '',
        '## Workflow disposition inventory', '',
        '| Workflow | Triggers | Publication | Suggested treatment |',
        '| --- | --- | --- | --- |',
    ]
    for r in rows:
        lines.append(f"| `{Path(r['workflow_path']).name}` | {r['trigger_events']} | {'Direct main push' if r['direct_main_push']=='true' else 'No explicit git publication detected'} | {r['review_recommendation'].replace('_',' ')} |")
    lines.extend([
        '', '## Consolidation design', '',
        '1. **Freeze a parity matrix first.** Each existing check must map to its exact command, interpreter/package environment, flags, input versions, preservation contract, trigger and required-check identity. Keep V8–V13 checksum, first-pass history, closed-live-use and adopted-reference controls explicit. A passing aggregate job must not silently omit source checks.',
        '2. **Separate validation from capture.** Read-only pull-request/push jobs validate retained local sources. Network collection and artifact recovery run only in explicitly named capture workflows and return candidate artifacts with provenance; they cannot promote an evidence claim or restart the paused course watch.',
        '3. **Factor setup and stable test groups.** Reusable workflows or composite actions may provide Python/R setup and stable baseline, finance, census and research-reference suites. Preserve deliberately different PDF-parser versions where independent extraction or historical reproducibility depends on them. Lock unpinned Python packages after validating equivalent outputs.',
        '4. **Replace dynamic YAML command replay.** Maintain an explicit, versioned acceptance runner with named groups and captured commands/environment. Call it from validation and release workflows. Replay must fail closed if a required check is missing; do not treat parsing run strings as full Actions semantics.',
        '5. **Isolate publication.** Explicit release dispatch or a narrowly approved release event consumes an exact tested commit and input/output hashes. Give only the publishing job write access. Prefer a generated-output branch/PR or clearly authorized release procedure to automatic rebase-and-push to main. Record source commit, tested commit, published commit and validation receipt.',
        '6. **Protect branch and release boundaries.** Scope write permissions to jobs, add an exact target-branch/event condition before publishing, use concurrency keyed to release identity, reject unexpected tracked changes and avoid rebase after validation without revalidation. GITHUB_TOKEN normally suppresses most follow-on workflow events; do not infer recursive execution is happening, but validate behavior for the actual token/event arrangement.',
        '7. **Review replay workflows individually.** Fixed artifact IDs, narrow self-file triggers and dated release names indicate historical replay intent. Verify retained artifacts, legal/source preservation requirements, caller relationships and owner intent before archiving. No workflow is proven obsolete by this audit.',
        '8. **Stage migration.** First move one read-only suite on a test branch, compare old/new job outputs and artifact hashes, then migrate remaining validation groups, then capture, then publication. Preserve required-check names until branch rules are updated under the applicable authority.', '',
        '## Priority review items', '',
        '- Direct-main workflows can publish generated README statements based on historical versions. V7 release text describes an active course watch although the current pointer requires it paused. Replaying a historical release must not overwrite current project state or reactivate an external schedule. A text generation command is not itself proof a watch is active.',
        '- Push-only paths that name only a workflow file can be appropriate for historical replay but do not provide routine PR coverage for underlying sources. Routine reference integrity checks should live in read-only CI, including all declared producer and dependency paths.',
        '- Upload/download artifact steps have retention and source-run dependencies. Review exact IDs, artifact names and expected hashes before reusing historical captures; never substitute a new archive silently.',
        '- Requested token permissions are not proof of effective remote authorization. Repository/organization defaults, fork pull-request downgrades, branch protection, secret availability and Actions settings were not inspected.',
        '- Local generation can occur even when no explicit git push is present. Called Python/R scripts and embedded Python are not executed here, so absence of a detected git command does not certify side-effect freedom.', '',
        '## Acceptance criteria for later A12/A13 implementation', '',
        '- Every old check appears in the parity matrix or has a reviewed retirement justification; no loss of substantive preservation coverage.',
        '- Validation jobs are read-only and never publish to main. Capture and release triggers, authority and output boundaries are documented.',
        '- Clean-checkout old/new comparison passes; hashes and relevant R/Python receipts match or differences are explicitly adjudicated.',
        '- Publication uses the exact validated payload and records immutable provenance; unexpected changes and branch movement fail closed.',
        '- No historical release rewrites current statuses; live reporting gates stay closed and the course watch remains paused.',
        '- A rollback exists for every workflow migration. Archive decisions require evidence, not filename age.', '',
        '## Reproduce and limitations', '',
        '```sh', 'python -B scripts/audit_workflows.py --check', 'python -B tests/check_workflow_audit.py', '```', '',
        'The generator requires PyYAML (tested with 6.0.3) and uses BaseLoader with duplicate-key rejection. It preserves the literal `on` key and inspects all frozen YAML configurations. It extracts direct `python`/`Rscript` path invocations and explicit shell git commands, dependency installation lines, action refs, permission inheritance and artifact configuration. Dynamic command construction, aliases, reusable workflow internals, script subprocesses and remote settings remain outside this static extractor; per-row limitations remain in the mutation/obsolescence fields. No network request, source collection, operational test, external message, or GitHub mutation is performed.',
    ])
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = outputs()
    if args.check:
        for path, content in result.items():
            if not (ROOT/path).is_file() or (ROOT/path).read_text() != content:
                raise SystemExit(f'DRIFT: {path}')
        print('PASS: frozen workflow audit and overlap/plan outputs reproduce exactly')
    else:
        for path, content in result.items():
            (ROOT/path).parent.mkdir(parents=True, exist_ok=True)
            (ROOT/path).write_text(content)
        print('Built workflow audit, overlap observations and consolidation plan')


if __name__ == '__main__':
    main()
