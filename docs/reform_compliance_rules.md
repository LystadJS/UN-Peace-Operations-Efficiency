# Reform compliance states — R12

The [status dictionary](../data/reforms/compliance_statuses.json) keeps governing authority, implementation evidence and compliance assessment separate. Its compliance and implementation vocabularies agree with [R01](reform_obligation_model.md). Candidate maturity remains governed by F03; no reform status substitutes for operational or financial validation.

Use `NOT_ASSESSED` where no assessment has been completed and `AUTHORITY_UNRESOLVED` where the applicable adopted provision or its effect is unresolved. `EVIDENCE_MISSING` records an inability to adjudicate performance. None of these states establishes noncompliance. A null deadline is unknown, not an elapsed deadline.

`NOT_APPLICABLE` needs a source-linked applicability assessment covering entity, action and period. `NOT_YET_DUE` needs an explicit sourced deadline after the evidence cutoff. Neither state asserts completed implementation. A recommendation inside a duly adopted resolution must retain its recommendation character; substantive review must establish what is actually obligatory for the addressee.

Implementation `REPORTED` means an identified source makes the claim. `PARTIALLY_VERIFIED` and `VERIFIED` require separate operational evidence and component coverage. An adoption record, proposal, organizational chart or successful repository check cannot establish the underlying change by itself. Verification must be described within the actual record population and period examined.

`COMPLIANT_VERIFIED` and `NONCOMPLIANT_VERIFIED` require applicable adopted authority, an assessment receipt and coverage evidence. Noncompliance additionally needs an elapsed sourced deadline and evidence adequate to distinguish nonperformance from missing records. Keep unresolved scope, conflicting sources and unverified components visible. The validator checks declarations; reviewers remain responsible for authentication, interpretation and completeness.

Adopting these states does not change any existing case to verified compliance, implementation or savings. Registers containing no extracted qualifying obligations describe an evidence boundary, not zero applicable obligations.

## Baseline declaration checks — R15

Run `python -B scripts/validate_reform_baseline.py` to check the two session action/instrument pairs, retained ACABQ advice, SG proposal/reported-arrangement records and UN80 reconciliation. Missing required registers fail. The check applies the R01 action contract, aligns the dictionaries, requires an explicit meaning for an empty action extraction, cross-references action symbols to registered instruments, and rejects action-specific adoption inferred only from an index. Adopted GA80 instrument receipts and separately reviewed operative actions must agree on authority.

ACABQ advice remains advice, and retained financial adjustments remain explicitly outside savings. SG proposals and reported joint/existing arrangements remain distinct from adopted requirements. Claimed implementation verification requires separate operational evidence; a non-null benefit amount requires the financial gate and review receipt. These are minimum declaration checks and do not inspect receipt contents, establish complete source populations, or replace F03/F05. The synthetic mutation suite is `python -B tests/check_reform_baseline.py`.
