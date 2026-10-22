# A12 — Explicit read-only validation groups

Routine validation is consolidated through [reusable_validation.yml](../.github/workflows/reusable_validation.yml) and an explicit [acceptance runner](../scripts/run_validation_suite.py). It never extracts commands from live workflow YAML. The [group manifest](../metadata/validation_groups.json) defines exact commands, Python 3.12, R requirements, and pinned Python dependencies.

## Command and environment parity

The [parity matrix](../metadata/ci_parity_matrix.csv) maps all 40 original run steps across eight archived workflows. It preserves original workflow, job, step number, step name and full run body. Every routine check maps to an explicit group step; dependency-install lines are promoted to declared setup rather than silently discarded. Multi-command run blocks retain bash fail-fast/pipefail semantics, arguments and output paths. Six adapters preserve their original workflow names and job IDs; their checks now call the reusable job. GitHub's displayed reusable-job check context can differ, so remote required-check settings must be reviewed before merging. No remote branch protection was changed here.

The baseline group retains the earlier GA/SPM/transaction/census arithmetic and preservation checks, R synthetic tests and renderers, and V7 PDF checks. V8 retains both `--check` and `--sources`; V9 retains `--check --test`; V10/V11 keep their separate closed-gate and workload/accounting checks. Foundation validation remains distinct. The new `repository-controls` group checks canonical metadata, issue migration, generated status/navigation, consistency and project health; these are additional controls, not replacements for the financial/research checks.

The legacy baseline installed PyMuPDF 1.26.7 within its last run block; the same package is installed before the baseline group runs. V8 uses that PDF version; V9 uses pypdf 5.9.0 plus PyMuPDF 1.26.7. V11 now explicitly declares those versions because its source checks require both packages. R is provided only for groups that need it. The historical capture-only V6 parser environment remains pypdf 6.1.1/beautifulsoup4 4.13.4 and is not mixed into the routine groups.

An eighth group, `retained-whitepaper`, runs the original White Paper validator against an exact local archive of baseline `32f02e5`. That validator intentionally asserts byte preservation of all earlier files, including the old README and workflows; it cannot fairly be applied to newly authorized navigation/CI edits. The archive is extracted under `/tmp` with a separate temporary Git directory and index. It reads original Git objects through an alternate object store and never changes the live HEAD/index. The original document, figure, arithmetic, source-hash and strict preservation checks remain unchanged. PyMuPDF 1.26.7 and python-docx 1.2.0 are declared for this group. Its success establishes retained-release integrity only; current navigation and metadata are separately checked by `repository-controls`.

The first baseline Python steps previously ran under the hosted runner's initial interpreter, followed by an explicit Python 3.12 setup near the end. The consolidated environment consistently uses 3.12; this is an explicit tightening of setup, not a claim of already observed full runtime equivalence. Parser-dependent and R checks need a pinned CI run to establish runtime parity. No checks have been retired.

## Capture separation

`census_v6.yml` and `v8_source_capture.yml` are network captures rather than routine checks. Their exact run bodies and artifact-retention settings remain intact, but automatic pushes are replaced by `workflow_dispatch`. Checkouts no longer persist credentials. Dispatch is a deliberate capture action; it does not reactivate the paused course watch, approve sources, promote a research finding or publish to main. The 20 historical publishing workflows and controlled release behavior are handled separately in A13.

## Read-only behavior and receipts

Validation workflows request only `contents: read`, do not persist checkout credentials, and contain no commit/push behavior. The explicit runner has no dependency installation, YAML command replay, source capture or publication commands. It executes each group in order and stops on the first failed check. A complete success additionally compares tracked file hashes before and after execution; generators may reproduce identical bytes but cannot silently change a tracked result. Necessary rendered/synthetic outputs retain their existing `/tmp` destinations. Captures remain separate manual workflows.

Receipts record actual passed steps, failure exit codes and tracked mutation status. A preflight failure for missing R or a mismatched package version fails the group instead of skipping checks. Structural plan tests, synthetic runner tests and actual runtime receipts are different evidence. A passing plan check is not an operational or financial finding.

Runtime receipts include the tested commit, group-plan hash and observed Python/package versions. Receipts must be written outside the repository; a historical test receipt is not a statement that the current commit or a different dependency environment passed. The runner has no implicit fallback to a different package version.

Execution requires a clean committed worktree and index at entry, with no nonignored untracked files, and requires the runner and plan to be tracked. This also prevents an untracked script or import helper from being treated as part of the tested commit. Keep scratch files and runtime receipts outside the repository. A dirty checkout cannot produce a commit-bound passing receipt even when no additional mutation occurs during testing. Plan checks and synthetic tests can still be run during implementation. The earlier local foundation rehearsal preceded this clean-entry safeguard and is retained only as an execution observation, not as publication evidence bound to HEAD. Run acceptance again from the completed clean checkout before using a receipt for publication.

```sh
python -B scripts/run_validation_suite.py --list
python -B scripts/run_validation_suite.py --check-plan
python -B scripts/run_validation_suite.py --group foundation --receipt /tmp/foundation-validation.json
python -B scripts/run_validation_suite.py --group baseline --receipt /tmp/baseline-validation.json
python -B scripts/run_validation_suite.py --group retained-whitepaper --receipt /tmp/retained-paper-validation.json
python -B tests/check_validation_suite.py
```

The suite regression tests use PyYAML (6.0.3) only to independently compare all archived run bodies against the matrix and inspect adapters; the runner itself uses the standard library. The reusable workflow installs only the selected group's declared packages. No network capture occurs during normal validation. Historical archives remain byte-preserved for audit; current mutable workflows do not rewrite old parity evidence.

## Verification boundary

Local plan/parity and synthetic execution tests establish command coverage and the specified fail-closed behavior. They do not establish remote Actions health, source availability, institutional authority or full R/PDF runtime parity. A hosted pinned-environment run is required before declaring the CI migration operationally proven. Continue to retain release-specific V8–V13 preservation checks and inspect any changed output hash rather than accepting it as a formatting migration.
