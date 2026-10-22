# A13 — Explicit publication and historical candidate workflows

This change separates candidate production from repository publication. It changes automation controls only; it does not execute a historical collector, restart the paused course watch, grant institutional authority, alter mandates, or certify implementation or savings.

## Historical wrappers

The 20 workflows identified as direct-main publishers in the frozen A06 audit are now **manual `workflow_dispatch` candidate builders**. They have read-only contents/actions permissions, checkout credentials are not persisted, and no step performs git configuration, staging, commit, rebase, pull or push. Existing build, source-authentication, preservation, corruption and release-specific checks remain. Candidate artifacts are retained for review. The [publication policy](../metadata/publication_policy.json) lists the converted workflows and dispositions of the 23 removed publication/README-mutation steps.

Eight dynamic replays of `.github/workflows/validate.yml` are replaced by the explicit `baseline` group in the [validation runner](../scripts/run_validation_suite.py). Version-specific V8–V13 checks remain explicit. Extra V8/V9/V10/V11 commands that followed replay are retained. Validation receipts identify the tested commit, group-plan hash and actual command outcomes. Read-only Actions access is retained because several manual builders retrieve pinned source artifacts; read-only contents alone would not authorize those downloads.

Historical whole-tree assertions in V11/V12 use the hash-verified archived originals for the specifically authorized README/workflow changes. Data, source, result and substantive code checks are not exempted. The historical white-paper builder validates its newly generated report in an isolated tree with those original control files restored, retaining the original validator and all its preservation assertions. No restoration touches the live checkout. These are historical release checks, distinct from current-status consistency checks.

No wrapper generates a historical README banner into current navigation. The original active-watch and unresolved-amendment narratives remain available only in preserved historical files. Changing triggers does not prove remote branch rules, effective token permissions, historical artifact availability or workflow runtime success.

## Dedicated preparation and publication

The [explicit release workflow](../.github/workflows/publish_release.yml) has two manual operations:

1. **Prepare:** run the explicit retained baseline and current repository-control suites at the selected workflow commit, require complete passing receipts for that exact commit from clean tracked inputs, and package selected approved outputs in deterministic `release-bundle.zip`. The current-control suite checks manifest, issue migration, current status, README, consistency and health freshness. The preparation log prints its SHA-256; the artifact is retained as `release-candidate-bundle`.
2. **Publish:** supply the successful preparation run ID, exact source commit, artifact name and printed bundle hash. The script verifies the source repository, successful manual-run provenance, workflow identity, receipt, manifest and file hashes. The tested source must still be the exact `main` head. It creates a new candidate branch and a **draft pull request**. It never updates or merges `main`.

The preparation job is read-only. Only the explicit publication job receives contents/pull-request write and Actions read permissions. Before any API client is constructed, the CLI requires the local controller commit (code and policy) to equal the supplied tested source commit. An older dispatch cannot publish with a different controller under a newer main commit. Inputs enter scripts through environment variables and argument arrays; no user-supplied command is evaluated. Checkout credentials are not persisted. The API client strips authorization on artifact-download redirects to other hosts.

The GitHub artifact download is an outer ZIP containing exactly `release-bundle.zip`; the supplied digest authenticates the inner deterministic bundle. The bundle itself contains `release_manifest.json`, `_release/validation.json`, `_release/controls.json`, and exactly the manifest-listed outputs. All filenames, sizes, modes, hashes and duplicates are checked before any API write. No extraction to the checkout occurs.

## Publication boundaries

The exact current-output allowlist is in `metadata/publication_policy.json`. It permits generated current navigation/status/health products and additive artifacts under `reports/releases/<release-id>/` using approved document/data/image extensions. A new versioned artifact cannot replace an existing path. Historical census releases, raw evidence, scripts, tests, workflow configuration and archived originals are protected from this publisher. Changing those requires an ordinary reviewed code/data change rather than a generated release bundle.

The script uses the combined source/tested commit, output hashes, receipt hash, run/artifact IDs and a fresh branch name `release-candidates/<run-id>-<bundle-hash-prefix>`. If the base moves, the artifact expires, a branch already exists, evidence is incomplete, or a path is outside policy, publication fails rather than rebasing, force-pushing or substituting inputs. The PR body retains provenance. A successful branch creation followed by a denied PR may leave an unmerged candidate branch; the failure must be reviewed, not silently retried with broader permissions.

If every approved current output already matches its base-tree blob, the publisher returns `NO_CHANGES` with zero publication writes. It creates neither a branch nor a PR and does not claim a changed payload or release. Existing versioned release paths remain append-only and are not silently replaced even by an identical proposed artifact.

A valid bundle and a successful CI run establish packaging and tested properties only. They cannot establish institutional approval, legal interpretation, private-data disclosure permission or a substantive operational finding. Candidate PR review and normal merge policy remain applicable. The publisher does not automatically merge, tag an official release, modify branch protection or activate operations.

## Local preparation and verification

After obtaining both exact-commit baseline and repository-controls receipts, an authorized operator can prepare approved outputs:

```sh
python scripts/run_validation_suite.py --group baseline --receipt /tmp/release-validation.json
python scripts/run_validation_suite.py --group repository-controls --receipt /tmp/release-controls.json
python scripts/publish_release.py prepare \
  --validation-receipt /tmp/release-validation.json \
  --controls-receipt /tmp/release-controls.json \
  --source-workflow .github/workflows/publish_release.yml \
  --output /tmp/release-bundle.zip \
  --paths docs/current_status.md metadata/current_status.json
python scripts/publish_release.py verify \
  --bundle /tmp/release-bundle.zip --sha256 PRINTED_SHA256 --source-sha EXACT_TESTED_COMMIT
python -B tests/check_publication_workflow.py
```

The publishing command is invoked only by the explicit workflow or a separately authorized operator with `GH_TOKEN`. It requires `--repository`, numeric `--run-id`, `--artifact-name`, full `--sha256` and full `--source-sha`. These controls do not grant access beyond the token's actual permissions. Repository settings may prohibit job-token PR creation; such a failure remains a concrete blocker, not permission to inject another credential.

Both preparation receipts require `status=PASS`, the correct group (`baseline` or `repository-controls`), exact `tested_commit`, a group-plan SHA-256, a nonempty list of zero-exit command results, a matching passed-step count, literal `initial_tracked_clean=true` and no tracked mutations by the suite. An inspection receipt from a dirty candidate workspace cannot authorize publication. Bundle tests use synthetic records and a fake API; they do not contact GitHub. Workflow structure is checked with the locally available PyYAML parser. Remote dispatch and publication have not been run as part of this implementation.
