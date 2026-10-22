# A08 — Canonical issue register migration

The canonical [issue register](../data/issues/current_issues.json) contains **117 source-faithful records** drawn from the 17 specialist CSV/JSON sources mapped in A05. The [migration receipt](../metadata/issue_migration_receipt.json) enumerates every source unit imported or excluded, every JSON leaf's coverage disposition, source hashes, normalization rules, parent links and counts. This migration preserves legacy observations rather than declaring 117 distinct unresolved defects.

## Scope and source fidelity

All rows in the ten CSV sources are reconciled. Fifty-nine supported, unchanged V13 lineage rows are explicitly excluded because they are obligations carried forward, not issues or new substantive rechecks. The two affected lineage rows are retained alongside their V11 requests and V12 correction records. Every legacy identifier remains an alias and every imported row retains its full, exact original source object plus source checksum and selector.

JSON gate objects are selected at exact RFC 6901 pointers. The eight historical gate observations retain all 19 missing activation fields per case and are linked to their V10 case gate. Missing-field strings are not fabricated into separate object-shaped source records. The complete paused-watch root object is retained with the standard empty JSON pointer. A narrow compatibility extension allows that root pointer while continuing to reject empty CSV selectors.

The mixed V6 review container contributes eight unresolved course-delivery questions. Its identity decisions, negative controls, scalar population controls, report interpretations and metadata remain source context rather than being promoted indiscriminately into new problems. The receipt covers every JSON leaf as either represented in an imported original object or excluded context, making this scoped extraction explicit. It is not a fresh search of every report or source capture in the repository.

## Status and cross-version treatment

- Original severity, status, requested remedy and evidence are preserved verbatim inside `source_ref.original_record`. Normalized axes remain separate; an absent request record remains `UNKNOWN`.
- The 16 owner-review questions remain open, requests not sent, responses not obtained. Suggested custodian roles are not accepted institutional ownership.
- The two AM11 amendments are resolved **for research reference 13.0 only**, supported by the adopted-reference pointer, adoption record and affected lineage. The original two first-pass holds remain unchanged. Six source observations describe those two corrections and must not be counted as six independent defects or six repairs.
- Resolved Q08/Q09 and the detailed-chapeau discrepancy retain their original documentary resolution with a normalization receipt. This is not a new verification of UN implementation, financing or operational effect.
- Attendance exclusions and aggregate controls remain `CONTROL_EXCLUSION` records. A record in the master register need not represent a defect; issue-type denominators must be reported.
- Historical gate observations remain blocked; the watch remains paused. No record receives `SATISFIED`, a monetary claim or an accepted-owner reference through this migration.
- Course questions retain the V6 observation cutoff. Elapsed dates are not delivery evidence and the paused course watch has not been executed.

The normalization receipt is evidence of a documented mapping rule. It does not authenticate a source beyond the byte-level checks, certify independent institutional review, or grant authority. Historical observations linked to one parent are not deduplicated; consumers must distinguish source observations from distinct underlying questions.

## Reproduce and validate

```sh
python -B scripts/migrate_master_issues.py
python -B scripts/migrate_master_issues.py --check
python -B scripts/validate_master_issues.py --records data/issues/current_issues.json --check-sources
python -B tests/check_issue_migration.py
python -B tests/check_master_issues.py
```

Generation is deterministic for fixed source bytes. A changed source hash, research-reference version or two-amendment lineage requires explicit mapping review. The register and receipt regenerate together. The schema/validator compatibility changes are limited to exact root-object JSON selection and clearer structural-validation wording; the source schema's previous hash is retained in the receipt.

The [master issue model](master_issue_model.md) remains the contract and field-reference guide. Its A05 statement that no population existed describes that earlier design stage. This A08 register is now the population entry point; legacy sources remain immutable and available to historical consumers.
