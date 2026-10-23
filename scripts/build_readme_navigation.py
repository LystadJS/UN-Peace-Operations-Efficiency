#!/usr/bin/env python3
"""Generate concise current navigation while preserving the original README."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys

ROOT = Path(__file__).resolve().parents[1]
NAVIGATION = 'metadata/readme_navigation.json'
ARCHIVE = 'history/pre_controls/README.md'
BASELINE = '32f02e5e689ad9f43e762d5985330df20dda1719'
REQUIRED_ROLES = {'current_project_status', 'canonical_manifest', 'master_issues',
                  'decision_standard', 'repository_audit', 'research_reference'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def safe_path(value):
    require(isinstance(value, str) and bool(value.strip()), 'navigation path required')
    path = PurePosixPath(value)
    require(path.parts and not path.is_absolute() and '..' not in path.parts and '\\' not in value,
            'navigation path must be repository-relative')
    return value


def validate(config):
    require(isinstance(config, dict) and type(config.get('schema_version')) is int
            and config['schema_version'] == 1, 'navigation schema_version must be integer 1')
    require(isinstance(config.get('purpose'), str) and config['purpose'].strip(), 'purpose required')
    roles = config.get('current_roles')
    require(isinstance(roles, list), 'current role list required')
    require(all(isinstance(row, dict) for row in roles), 'current roles must contain objects')
    names = [row.get('role') for row in roles]
    require(len(names) == len(set(names)) and set(names) == REQUIRED_ROLES,
            'current roles must be unique and complete')
    for row in roles:
        safe_path(row['path'])
        require(all(isinstance(row.get(key), str) and row[key].strip()
                    for key in ('label', 'qualification')), 'role label/qualification required')
    history = config.get('history')
    require(isinstance(history, list) and history, 'history entries required')
    require(all(isinstance(row, dict) for row in history), 'history must contain objects')
    ids = [row.get('id') for row in history]
    require(len(ids) == len(set(ids)), 'duplicate history identity')
    require({f'V{x}' for x in range(2,14)} <= set(ids), 'V2–V13 history coverage required')
    for row in history:
        safe_path(row['path'])
        require(all(isinstance(row.get(key), str) and row[key].strip()
                    for key in ('label', 'scope')), 'history label/scope required')
    cases = config.get('priority_cases')
    require(isinstance(cases, list) and len(cases) == 3, 'three initial priority cases required')
    require(all(isinstance(row, dict) and all(isinstance(row.get(key), str) and row[key].strip()
                for key in ('label', 'test')) for row in cases), 'priority case label and test required')
    return config


def verify_archive(root):
    archive = root / ARCHIVE
    require(archive.is_file(), 'A07 README archive is required before navigation publication')
    scope = json.loads((root/'metadata/repository_audit_scope.json').read_text())
    expected = next(row['sha256'] for row in scope['files'] if row['path'] == 'README.md')
    require(hashlib.sha256(archive.read_bytes()).hexdigest() == expected,
            'archived README differs from frozen original')


def render(config, pointer):
    config = validate(config)
    require(pointer.get('reference_version') == '13.0', 'research reference changed; review navigation')
    require(pointer.get('course_watch_policy', '').lower().startswith('keep paused'),
            'watch instruction changed; review navigation')
    require(pointer.get('live_use_gates') == {'SP08P1':'BLOCKED_FOR_LIVE_USE',
                                             'SP09P1':'BLOCKED_FOR_LIVE_USE'},
            'live-use gates changed; review navigation')
    rows = '\n'.join(f'| [{r["label"]}]({r["path"]}) | {r["qualification"]} |'
                     for r in config['current_roles'])
    cases = '\n'.join(f'- **{r["label"]}:** {r["test"]}' for r in config['priority_cases'])
    readme = f'''<p align="center">
  <img src="assets/readme-banner.svg" alt="UN Peace Operations Efficiency" width="100%" />
</p>

# UN Peace Operations Efficiency

{config['purpose']}

## Start here

Read the **[generated current status](docs/current_status.md)** for the controlling project readout, source cutoffs, financial qualifications and unresolved decisions. Current status is generated from canonical records; earlier reports remain available through the [release history](docs/release_history.md).

The [public decision portfolio](docs/decision_portfolio.md) now defines fourteen screening cases, evidence contracts and validation controls. **Zero substantive operational audits are complete; benefits remain unestimated.** Start with the [Commander’s decision memo](docs/commander_decision_memo.md), [leadership report](docs/leadership_portfolio_report.md), [partial reform baseline](docs/reform_compliance_view.md) and [task execution ledger](docs/workflow_execution.md). Internal evidence and accepted operational authority remain prerequisites for the decision-grade end state.

| Resource | Use |
| --- | --- |
{rows}

## Decision focus

The initial operational validation priorities are:

{cases}

The project moves from a bounded concern through evidence, a feasible counterfactual and operational safeguards to an accountable decision. Retaining an effective arrangement and closing an unsupported claim are valid outcomes. Definitions and advancement requirements are in the [foundation standards](docs/foundation_standards.md).

## Current research and operational boundary

Research reference **13.0** incorporates two adopted research corrections. The historical first-pass result remains 59 supported unchanged and two amendment holds; the two affected rechecks are separate results. Both reporting cases remain **blocked for live use**, and the course watch remains **paused** under the [scoped pointer](data/current_research_reference.json).

No additional net savings or duplicate paid service has been established by the retained evidence. A monetary finding cannot be called savings before `FINANCIALLY_VALIDATED`; realized amounts additionally require implementation and observation. Financial proposals, appropriations, internal allocations, recoveries, capacity effects and already embedded efficiencies retain their distinct treatment.

## Evidence and reproducibility

Trace each claim through its source, period, authority, financial perimeter and limitations. Public activity records are not a complete population of delivered services. Structural checks verify only their declared properties; they do not certify legal compliance, operational duplication or savings. Restricted operational, personnel and financial evidence belongs in approved systems.

Use the [repository control audit](docs/repository_audit.md) and [canonical manifest](metadata/canonical_manifest.json) to find producers, consumers and unresolved dependencies. Current validation and publication procedures are documented alongside their scripts and workflows; historical releases retain their original source and preservation requirements.

## Historical research

The [history index](docs/release_history.md) retains access to the financial studies, censuses, V2–V13 releases, owner-review package and 15 October white paper. Those products remain evidence within their declared scope and cutoff. The white paper is a retained synthesis, not a fresh legal-status review or operational census.

This README is generated from [navigation metadata](metadata/readme_navigation.json). Regenerate or check it with `python -B scripts/build_readme_navigation.py --write` or `--check`.
'''
    history_rows = '\n'.join(f'| {r["id"]} | [{r["label"]}](../{r["path"]}) | {r["scope"]} |'
                             for r in config['history'])
    history = f'''# Release and research history

This index is reader navigation. The [canonical manifest](../metadata/canonical_manifest.json) and [release index](../metadata/release_index.csv) control artifact designation and scoped supersession. A version number or later publication does not by itself supersede another product's mandate, financial baseline or evidence.

## Preserved README

The complete pre-controls README remains [byte-preserved locally](../{ARCHIVE}). Its original relative links are preserved as historical bytes and may resolve differently inside the archive directory. For the functional original GitHub rendering and all its historical links, use the [commit-pinned README](https://github.com/LystadJS/UN-Peace-Operations-Efficiency/blob/{BASELINE}/README.md). Source documents remain at their original repository paths and are linked below.

The old README accumulated differently scoped snapshots. In particular, historical V11 amendment holds coexist with V13's adoption of two corrected research assertions; historical V7 watch-creation language does not override the later pause. Read the [generated current status](current_status.md) for the current project designation and the underlying source cutoff for every substantive claim.

## Research layers and retained releases

| Layer | Retained entry point | Scope and interpretation |
| --- | --- | --- |
{history_rows}

## Foundation and repository controls

- [F01–F06 foundation standards](foundation_standards.md) define the prospective decision framework.
- [A01–A06 frozen control audit](repository_audit.md) records the inspected input population and design findings.
- [Current project status](current_status.md) is the current generated readout; it does not refresh underlying UN legal or operational evidence automatically.

Historical record counts must not be added across releases: source URLs, publications, report symbols, meeting variants, canonical research identities, delivered activities and unique people represent different grains. Preserve the historical first-pass denominator and record later amendments or recovery as separately scoped results.

The 15 October white paper remains a project synthesis. Its publication artifacts and validation receipt do not independently certify implementation, legal compliance, complete activity coverage or additional savings.

Generated by `scripts/build_readme_navigation.py` from [navigation metadata](../metadata/readme_navigation.json); historical source files and the archived README are not rewritten.
'''
    return {'README.md': readme, 'docs/release_history.md': history}


def outputs(root=ROOT):
    verify_archive(root)
    config = json.loads((root/NAVIGATION).read_text())
    pointer = json.loads((root/'data/current_research_reference.json').read_text())
    selected = root/safe_path(pointer['reference_path'])
    require(hashlib.sha256(selected.read_bytes()).hexdigest() == pointer['reference_sha256'],
            'selected research-reference bytes differ from pointer')
    result = render(config, pointer)
    for row in config['current_roles'] + config['history']:
        require((root/row['path']).is_file(), f'navigation target absent: {row["path"]}')
    require((root/'metadata/release_index.csv').is_file(), 'release index absent')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        require(not (args.write and args.check), 'choose --write or --check')
        result = outputs()
        for name, content in result.items():
            path = ROOT/name
            if args.write:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
            else:
                require(path.is_file() and path.read_text() == content, f'generated navigation drift: {name}')
        print('PASS: concise README and history navigation; frozen original preserved')
        return 0
    except (ValueError, OSError, KeyError, TypeError, StopIteration) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
