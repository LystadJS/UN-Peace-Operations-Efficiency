# Public validation baseline release — I12

**PUBLIC_VALIDATION_BASELINE; decision-grade portfolio BLOCKED.** This local release manifest records 413 filesystem artifacts with byte counts and SHA-256 hashes. It does not create a GitHub release, publish files, authorize operational implementation or attest runtime CI.

The [machine-readable manifest](../data/portfolio/release_manifest.json) declares its directory populations, required core artifacts, source cutoffs and explicit exclusions. It includes ready untracked files so that the final review population does not silently omit work awaiting commit. Root integration must regenerate after all edits, commit the complete reviewed population and validate the exact final commit separately.

All fourteen cases remain screening candidates blocked pending evidence, with zero substantive operational adjudications and unestimated benefits. Foundation and validation-system completion are partial; decision-portfolio and realization gates remain blocked. Read the [leadership report](leadership_portfolio_report.md) and [public portfolio](decision_portfolio.md) for the substantive limits. Scoped reform review is through 2026-10-23; retained financial baseline is through 2026-10-08; historical research/owner controls retain their 2026-10-15 cutoff. Individual case dates remain explicit.

The manifest and this rendering omit their own hashes. Generated current-status, navigation, project-health and runtime/orchestration outputs are separately checked to avoid dependency cycles; the final agent review is excluded because it can inspect the manifest. The exclusions are not permission to skip their validation. Declared directory hashing includes both new roadmap work and retained control/document dependencies; it is not a claim that all entries are new research or current operational evidence.

Restricted/secret path patterns, path traversal, duplicate paths, symlinks, missing core artifacts, changed hashes and unsupported eligibility or benefit declarations cause failure. These checks do not certify absence of sensitive content; use the separate [public evidence boundary](secure_evidence_intake.md), substantive review and approved derivatives. Synthetic fixtures remain software evidence only.

Run `python -B scripts/build_portfolio_release.py --write` after integration, then `--check` and `python -B tests/check_portfolio_release.py`. No timestamp, current HEAD, self hash or network operation is used. Exact-commit runtime validation is a separate receipt.
