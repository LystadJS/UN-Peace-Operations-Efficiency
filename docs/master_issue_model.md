# A05 — Master issue model and legacy crosswalk

This is a prospective model for unifying specialist issue records. It supplies a [JSON schema](../metadata/master_issue_schema.json), [field crosswalk](../metadata/issue_register_crosswalk.csv), and structural validator. **No master issue population has been created and no legacy issue has been migrated, reclassified, closed, or deduplicated.** Population and downstream consumer migration belong to A08.

## Frozen evidence and coverage

The audit uses the [A01–A06 scope](../metadata/repository_audit_scope.json): 554 files at baseline commit `32f02e5e689ad9f43e762d5985330df20dda1719`, including 11 local F01–F06 files. This model and other wave outputs are outside that frozen input denominator.

The crosswalk contains **140 field mappings across 17 sources**. All CSV columns and the enumerated JSON container fields are retained; mappings are not row-level migration decisions.

| Source family | Sources inspected | Treatment |
| --- | --- | --- |
| Core quality and finance | `quality_issues.csv`, `transaction_audit_issues.csv`, `spm_2027_source_discrepancies.csv` | Preserve issue text, original severity, requested remedy, source anchors, and original status. Source-priority containment differs from complete resolution. |
| Owner questions and release gates | `owner_review/evidence_gap_register.csv`, `public_release_gates.csv` | Separate unanswered questions, request/response state, blockers, financial claims, and authority. An open question is not proof of a workflow defect. |
| Publication and census controls | `census_v2/date_quality_exceptions.csv`, `census_v6/quality_exceptions.csv`, `census_v4/attendance_exclusions_and_aggregates.csv` | Date holds, unresolved qualifications, exclusions, and aggregate controls retain distinct types. An exclusion/control is not automatically an issue requiring remediation. |
| Historical research amendments | `census_v11/amendment_requests.json`, `census_v12/correction_diff.csv`, `census_v13/reference_lineage.csv` | Link original holds to later research adoption. Preserve first-pass outcomes; do not reopen an adopted correction merely because its historical request still says proposed. |
| JSON activation and operational constraints | `census_v10/activation_status.json`, `census_v11/closed_gate_receipt.json`, `census_v12/closed_gate_receipt.json`, `census_v13/closed_gate_receipt.json`, `census_v8/operational_status.json` | Nested live gates and missing-field lists carry constraints outside CSV registers. Expand individual case gates with exact JSON pointers in A08. A paused watch is an instruction, not a resolved defect. |
| Mixed review container | `census_v6/review_decisions.json` | Preserve nested review decisions and controls as provenance; examine individual unresolved questions rather than converting every decision into a new issue. |

Discovery inspected frozen filenames, selected CSV headers/enumerations, nested gate JSON, amendment records, and version lineage. This is a scoped crosswalk of primary issue/constraint sources, not exhaustive semantic extraction from every paragraph, manifest, source capture, or report. Receipt files and review summaries can repeat or contextualize issues; they must not be counted as distinct issues solely because they mention a problem. A08 must reconcile additional embedded issues discovered through the lineage and artifact inventories and document exclusions.

## Common record and independent status axes

Each future record has a namespaced `issue_id`; original aliases; optional parent; immutable source reference including path, checksum, selector, original ID and complete original record; issue type; summary; severity; proposed custodian/owner role; minimum evidence; closure rule; affected claims; and normalization receipt. A safe owner-acceptance reference is separate from a proposed role. Restricted names and records remain in approved storage.

The following axes are independent; no single status implies that the others passed:

| Axis | Allowed values and interpretation |
| --- | --- |
| Resolution | `OPEN`, `DOCUMENTED_CONTAINED`, `RESOLVED`, `SUPERSEDED`, `DEFERRED`, `UNKNOWN`. Containment is not correction. Resolution and supersession need a receipt. |
| Evidence | `NOT_TESTED`, `NOT_ESTABLISHED`, `EVIDENCE_REQUIRED`, `REPORTED`, `VERIFIED`, `UNKNOWN`. Not tested differs from a test that cannot establish the claim. |
| Request | `NOT_REQUESTED`, `REQUESTED`, `NOT_APPLICABLE`, `UNKNOWN`. Existing `NOT_SENT` normalizes only to not requested. |
| Response | `NOT_OBTAINED`, `PARTIAL`, `OBTAINED`, `NOT_APPLICABLE`, `UNKNOWN`. A request can exist without a response; a document can be obtained without a request. |
| Gate | `NOT_ASSESSED`, `BLOCKED`, `SATISFIED`, `NOT_APPLICABLE`, `UNKNOWN`. A satisfied gate requires verified evidence and a receipt. |
| Severity | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `UNKNOWN`. Preserve the original; a normalized change needs an explicit review receipt. Absence is unknown, not low. |

Never map an unseen legacy value to resolved, verified, approved, implemented, or zero. Use `UNKNOWN`, retain raw content, and require mapping review. Source-specific mappings in the CSV are recommendations pending A08 row review. `not_estimated` remains an unknown amount, not a measured zero. Narrative fields named `resolution` may prescribe a hold rather than record a completed fix.

## Identity, duplicates, and immutable lineage

The source identity is `(path, sha256, selector)`. For CSV, selector is an exact value of `id_field` and must uniquely select one row. For JSON, use an escaped RFC 6901 pointer selecting an object (for example `/live_gates/SP08P1`). Historical versions have distinct source identities even when local IDs repeat. Every original ID remains an alias qualified by source path.

Do not merge issues based on matching topic or wording. Shared blockers may be linked by a parent or cross-reference while retaining case-specific closure rules. Where two records are confirmed aliases of one issue, A08 must retain all source snapshots and a documented equivalence receipt; this initial contract supports one authoritative source snapshot per record. Until a reviewed multi-source extension exists, represent additional source observations as linked child records rather than losing provenance. Parents must exist in the envelope and cycles are prohibited.

Corrections append reviewed resolution or mapping information. `--previous` prevents deletion of earlier records, removal of aliases, and rewriting of source snapshots. It does not authenticate a source or supply a historical snapshot automatically. Future changes need a migration version and reviewed receipts. Raw issue severity and text remain recoverable from `original_record` even if a normalized summary or classification changes.

## Claim and closure safeguards

Issue closure is not candidate advancement. A closed data discrepancy cannot authorize a live trial, establish UN reform compliance, or certify an operational benefit. Research amendment adoption does not supply institutional approval. Apply [F03](candidate_advancement.md), [F04](source_authority_standard.md), [F05](cost_accounting_standard.md), and [F06](guardrail_standard.md) separately.

The optional claim subrecord is a guard against accidental savings language, not a full benefit ledger. `NO_MONETARY_CLAIM` requires a null amount. Recovery and cost avoidance remain separate categories. Savings require a positive amount, a financial-validation receipt, and a candidate state at or beyond `FINANCIALLY_VALIDATED`; realized savings also require `REALIZED`. A later capacity-only state does not prove a financial gate: the referenced full candidate record must pass F03 before substantive approval. Financial status, period, currency, cost objects and net-benefit calculation remain in the F03/F05 case receipt, not guessed during issue normalization.

A `RESOLVED` or `SUPERSEDED` record requires a resolution receipt even if the legacy source already uses that word. In A08, the receipt can reference reviewed original closure evidence; the migration must not silently convert a label into verification. A source or receipt reference is a declared locator, not proof that a reviewer verified its contents.

## Validation and A08 handoff

```sh
python scripts/validate_master_issues.py
python tests/check_master_issues.py
python scripts/validate_master_issues.py --records /approved/issues.json
python scripts/validate_master_issues.py --records /approved/current.json --previous /approved/prior.json --check-sources
```

Default validation checks the field crosswalk, frozen hashes, and an empty prospective envelope. It deliberately reports zero supplied issue records. `--records` validates new-format records; `--check-sources` verifies hashes and exact row/object snapshots against repository files. Receipt semantics, legal authority, actual resolution, and source completeness require substantive review. Tests use synthetic records only; no legacy issue is promoted or closed.

A08 should first freeze the source inventory and mapping version, populate reviewed rows without overwriting raw records, reconcile counts and aliases per source, review cross-version amendments against the current pointer, and run old/new compatibility checks before switching consumers. Incomplete or ambiguous mappings stay explicit. A05 creates no permission to send requests, access restricted records, reactivate the course watch, or change existing gates.
