# A06 — CI consolidation plan

Static audit of **28 frozen workflows** in scope `A01-A06-2026-10-22` at baseline `32f02e5e689ad9f43e762d5985330df20dda1719`: 27 tracked workflows plus the pre-existing untracked F01–F06 workflow. Counts describe configuration, not GitHub run history or enabled state. No workflows were changed or executed by this audit.

The source of truth is [workflow_audit.csv](../metadata/workflow_audit.csv); [workflow_overlap.csv](../metadata/workflow_overlap.csv) records target overlap without declaring either invocation redundant. The [frozen scope](../metadata/repository_audit_scope.json) pins all inspected bytes.

## Observed configuration

- Trigger counts: {"pull_request":9,"push":28,"workflow_dispatch":7}. Multiple triggers can belong to one workflow.
- 20 workflows contain explicit shell pushes to `main`; these mix validation/build and repository publication.
- 8 workflows dynamically replay `validate.yml` run steps through Python subprocess calls. These replay commands, not their setup actions, inherited step conditions, environment or job semantics.
- 5 workflows reference fixed capture artifact IDs or fixed run IDs. Availability, retention expiry and current need were not tested; these are replay/retention review candidates, not verified obsolete workflows.
- 84 action references were inspected; 0 use full commit-SHA pins. Tag-based action refs are mutable supply-chain dependencies. Version preservation may require exact tool versions, not indiscriminate upgrades.
- 56 pairwise overlap observations identify shared direct script references or dynamic acceptance delegation. Script identity alone does not imply matching flags, source inputs, evaluation modes or authority.

## Workflow disposition inventory

| Workflow | Triggers | Publication | Suggested treatment |
| --- | --- | --- | --- |
| `additional_mission_training_frame.yml` | push;workflow_dispatch | Direct main push | separate validation capture and explicit release |
| `census_v5.yml` | push | Direct main push | separate validation capture and explicit release |
| `census_v5_release.yml` | push | Direct main push | separate validation capture and explicit release |
| `census_v6.yml` | push | No explicit git publication detected | retain guards consolidate shared setup where parity proven |
| `census_v6_release.yml` | push | Direct main push | separate validation capture and explicit release |
| `census_v7_recovery.yml` | push | Direct main push | separate validation capture and explicit release |
| `census_v7_release.yml` | push | Direct main push | separate validation capture and explicit release |
| `deeper_official_archives_v4.yml` | push;workflow_dispatch | Direct main push | separate validation capture and explicit release |
| `foundation_standards.yml` | pull_request;push | No explicit git publication detected | retain guards consolidate shared setup where parity proven |
| `mission_archive_census.yml` | push;workflow_dispatch | Direct main push | separate validation capture and explicit release |
| `owner_review_package.yml` | push | Direct main push | separate validation capture and explicit release |
| `published_census_v2.yml` | push;workflow_dispatch | Direct main push | separate validation capture and explicit release |
| `recover_legacy_notice_dates.yml` | push;workflow_dispatch | Direct main push | separate validation capture and explicit release |
| `systematic_census.yml` | push;workflow_dispatch | Direct main push | separate validation capture and explicit release |
| `systematic_evidence_views.yml` | push;workflow_dispatch | Direct main push | separate validation capture and explicit release |
| `v10_protocol_ci.yml` | pull_request;push | No explicit git publication detected | retain guards consolidate shared setup where parity proven |
| `v10_protocol_release.yml` | push | Direct main push | separate validation capture and explicit release |
| `v11_tabletop.yml` | pull_request;push | Direct main push | separate validation capture and explicit release |
| `v11_validate.yml` | pull_request;push | No explicit git publication detected | retain guards consolidate shared setup where parity proven |
| `v12_reference_patch.yml` | pull_request;push | Direct main push | separate validation capture and explicit release |
| `v13_reference_adoption.yml` | pull_request;push | Direct main push | separate validation capture and explicit release |
| `v8_release.yml` | push | Direct main push | separate validation capture and explicit release |
| `v8_source_capture.yml` | push | No explicit git publication detected | retain guards consolidate shared setup where parity proven |
| `v8_validate.yml` | pull_request;push | No explicit git publication detected | retain guards consolidate shared setup where parity proven |
| `v9_checks.yml` | pull_request;push | No explicit git publication detected | retain guards consolidate shared setup where parity proven |
| `v9_release.yml` | push | Direct main push | separate validation capture and explicit release |
| `validate.yml` | pull_request;push | No explicit git publication detected | retain guards consolidate shared setup where parity proven |
| `white_paper_2026.yml` | push | Direct main push | separate validation capture and explicit release |

## Consolidation design

1. **Freeze a parity matrix first.** Each existing check must map to its exact command, interpreter/package environment, flags, input versions, preservation contract, trigger and required-check identity. Keep V8–V13 checksum, first-pass history, closed-live-use and adopted-reference controls explicit. A passing aggregate job must not silently omit source checks.
2. **Separate validation from capture.** Read-only pull-request/push jobs validate retained local sources. Network collection and artifact recovery run only in explicitly named capture workflows and return candidate artifacts with provenance; they cannot promote an evidence claim or restart the paused course watch.
3. **Factor setup and stable test groups.** Reusable workflows or composite actions may provide Python/R setup and stable baseline, finance, census and research-reference suites. Preserve deliberately different PDF-parser versions where independent extraction or historical reproducibility depends on them. Lock unpinned Python packages after validating equivalent outputs.
4. **Replace dynamic YAML command replay.** Maintain an explicit, versioned acceptance runner with named groups and captured commands/environment. Call it from validation and release workflows. Replay must fail closed if a required check is missing; do not treat parsing run strings as full Actions semantics.
5. **Isolate publication.** Explicit release dispatch or a narrowly approved release event consumes an exact tested commit and input/output hashes. Give only the publishing job write access. Prefer a generated-output branch/PR or clearly authorized release procedure to automatic rebase-and-push to main. Record source commit, tested commit, published commit and validation receipt.
6. **Protect branch and release boundaries.** Scope write permissions to jobs, add an exact target-branch/event condition before publishing, use concurrency keyed to release identity, reject unexpected tracked changes and avoid rebase after validation without revalidation. GITHUB_TOKEN normally suppresses most follow-on workflow events; do not infer recursive execution is happening, but validate behavior for the actual token/event arrangement.
7. **Review replay workflows individually.** Fixed artifact IDs, narrow self-file triggers and dated release names indicate historical replay intent. Verify retained artifacts, legal/source preservation requirements, caller relationships and owner intent before archiving. No workflow is proven obsolete by this audit.
8. **Stage migration.** First move one read-only suite on a test branch, compare old/new job outputs and artifact hashes, then migrate remaining validation groups, then capture, then publication. Preserve required-check names until branch rules are updated under the applicable authority.

## Priority review items

- Direct-main workflows can publish generated README statements based on historical versions. V7 release text describes an active course watch although the current pointer requires it paused. Replaying a historical release must not overwrite current project state or reactivate an external schedule. A text generation command is not itself proof a watch is active.
- Push-only paths that name only a workflow file can be appropriate for historical replay but do not provide routine PR coverage for underlying sources. Routine reference integrity checks should live in read-only CI, including all declared producer and dependency paths.
- Upload/download artifact steps have retention and source-run dependencies. Review exact IDs, artifact names and expected hashes before reusing historical captures; never substitute a new archive silently.
- Requested token permissions are not proof of effective remote authorization. Repository/organization defaults, fork pull-request downgrades, branch protection, secret availability and Actions settings were not inspected.
- Local generation can occur even when no explicit git push is present. Called Python/R scripts and embedded Python are not executed here, so absence of a detected git command does not certify side-effect freedom.

## Acceptance criteria for later A12/A13 implementation

- Every old check appears in the parity matrix or has a reviewed retirement justification; no loss of substantive preservation coverage.
- Validation jobs are read-only and never publish to main. Capture and release triggers, authority and output boundaries are documented.
- Clean-checkout old/new comparison passes; hashes and relevant R/Python receipts match or differences are explicitly adjudicated.
- Publication uses the exact validated payload and records immutable provenance; unexpected changes and branch movement fail closed.
- No historical release rewrites current statuses; live reporting gates stay closed and the course watch remains paused.
- A rollback exists for every workflow migration. Archive decisions require evidence, not filename age.

## Reproduce and limitations

```sh
python -B scripts/audit_workflows.py --check
python -B tests/check_workflow_audit.py
```

The generator requires PyYAML (tested with 6.0.3) and uses BaseLoader with duplicate-key rejection. It preserves the literal `on` key and inspects all frozen YAML configurations. It extracts direct `python`/`Rscript` path invocations and explicit shell git commands, dependency installation lines, action refs, permission inheritance and artifact configuration. Dynamic command construction, aliases, reusable workflow internals, script subprocesses and remote settings remain outside this static extractor; per-row limitations remain in the mutation/obsolescence fields. No network request, source collection, operational test, external message, or GitHub mutation is performed.
