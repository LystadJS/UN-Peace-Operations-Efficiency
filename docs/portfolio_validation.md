# Public-portfolio release validation — I11

The [explicit validation plan](../data/portfolio/validation_plan.json) runs 50 offline Python checks, including 26 test scripts, across the reform registers, financial boundaries, case dossiers, evidence contracts, synthetic models, blocked execution gates, benefit ledger, public views and release manifest. Missing scripts or artifacts fail validation; there is no optional-test fallback or dynamic workflow replay. Python 3.11 or later is required. The actual runtime version is recorded rather than described as a pinned patch release. No third-party Python package is required by this suite.

This supplements the retained [A12 validation groups](ci_validation.md). Their historical Python/R/PDF and preservation checks remain separately required; a successful public-portfolio receipt does not imply those groups ran. Full local Git history must be available because frozen-source generators read retained commits.

The final `portfolio_release_validation.yml` runs this superset on pull requests and pushes to `main`. Earlier `reform_validation.yml`, `portfolio_validation.yml` and `evidence_validation.yml` remain explicitly dispatched phase adapters rather than duplicating routine jobs. The six retained legacy research workflows continue their independent checks. The C-phase adapter includes `scripts/validate_case_dossiers.py` and `tests/check_case_dossiers.py`; both are also mandatory in this final suite.

```sh
python -B scripts/run_portfolio_checks.py --check-plan
python -B scripts/run_portfolio_checks.py --receipt /tmp/public-portfolio-runtime.json
python -B tests/check_portfolio_check_runner.py
```

The first command checks plan structure and required paths only. Runtime acceptance requires a clean committed worktree and index, including every nonignored untracked file. The runner and all explicit scripts/inputs must be tracked. Each command runs as an argument vector with the current Python executable, without a shell, installation, network operation or publication action initiated by the runner. The plan permits checks and explicit record inputs; write-mode flags are rejected.

The runtime receipt must be outside the repository under `/tmp` or GitHub's `RUNNER_TEMP`. It records the tested commit and tree, raw plan hash, observed Python environment, start/finish times, every command's exit code and output hashes, passed-step count, tracked-file changes, final worktree status and whether HEAD stayed unchanged. A command failure remains visible while the remaining declared checks run. A timeout is a failure. Tracked mutation, newly created nonignored output or a changed HEAD prevents a passing receipt. A dirty initial checkout produces a preflight-failure receipt with no runtime attestation.

[The case validator](../scripts/validate_case_dossiers.py) checks all fourteen screening dossiers and 230 retained source snapshots: 227 exact CSV records and three explicitly scoped JSON subsets. It checks source-file hashes, locators, snapshot contents, case population and the current unknown-owner/baseline/benefit boundary. Source fidelity does not authenticate the underlying operational assertion or establish transaction completeness. Its [corruption tests](../tests/check_case_dossiers.py) exercise changed source bytes, false snapshots, unsafe paths and invented monetary claims.

[Runner tests](../tests/check_portfolio_check_runner.py) use isolated synthetic Git repositories to verify exact-commit receipts, dirty/untracked/staged rejection, tracked and untracked mutation detection, command failures, required-test coverage and safe receipt paths. These fixture commits do not change the project repository or publish anything.

No acceptance result grants UN operational authority, authenticates a legal interpretation, fills missing records, completes a blocked audit or recognizes a saving. Runtime receipts are software evidence. The portfolio's actual operational and institutional gates remain separately controlled.
