# A03 — Repository status model

This prospective model describes artifact status in a declared scope at an evidence cutoff. It does not migrate existing rows, designate new canonical files, reopen a watch, or confer institutional authority. Use it with the [foundation standards](foundation_standards.md), [source-authority standard](source_authority_standard.md), and [candidate advancement standard](candidate_advancement.md).

## Five independent facets

| Facet | Status | Meaning and required evidence |
| --- | --- | --- |
| Artifact currency | `CURRENT` | The designated controlling artifact for one scope and role at the snapshot date. Requires a designation receipt; recency or filename alone is insufficient. |
| Artifact currency | `HISTORICAL` | A preserved record of an earlier observation, method or result. Historical does not mean false or superseded for every use. |
| Artifact currency | `SUPERSEDED` | Another registered artifact replaces this artifact for the same scope and role. Requires the replacement ID, explicit scope and decision receipt; preserve the old artifact. |
| Artifact currency | `CANDIDATE` | A draft or proposed replacement awaiting designation. It does not displace the current artifact. |
| Artifact currency | `UNRESOLVED` | Currency has not been established, or competing claims remain unresolved. Record the conflict rather than choosing the latest-looking name. |
| Research adoption | `ADOPTED_FOR_RESEARCH` | The authorized project decision selects this artifact for specified research use. This does not grant UN or live-use approval. |
| Research adoption | `NOT_ADOPTED`, `NOT_APPLICABLE`, `UNKNOWN` | Explicit rejection/non-selection, a justified out-of-scope facet, or insufficient evidence, respectively. Absence of an adoption record is `UNKNOWN`, not rejection. |
| Institutional approval | `APPROVED` | The competent authority approved the specified action, scope, period and conditions. Identify the authority and operative decision. A GA proposal or ACABQ recommendation cannot supply this status. |
| Institutional approval | `NOT_APPROVED`, `NOT_APPLICABLE`, `UNKNOWN` | Affirmative evidence of nonapproval, justified inapplicability, or absence of sufficient evidence. Do not infer nonapproval merely because a record is inaccessible. |
| Implementation | `IMPLEMENTED` | Dated operational records substantiate all material components of the declared change. This does not establish benefit realization or continuing live permission. |
| Implementation | `PARTIALLY_IMPLEMENTED`, `REPORTED_NOT_VERIFIED` | Some identified components are substantiated, or implementation is attributed to a report without independent substantiation at the required grain. |
| Implementation | `NOT_IMPLEMENTED`, `NOT_APPLICABLE`, `UNKNOWN` | Positive evidence that the scoped action has not occurred, justified inapplicability, or insufficient evidence. |
| Live use | `BLOCKED` | The proposed live activity cannot proceed under the applicable gate or authority. A valid research reference may remain blocked for live use. |
| Live use | `PAUSED` | A previously arranged or permitted activity is explicitly suspended. Preserve the pause decision and restart authority. The validator does not restart it. |
| Live use | `AUTHORIZED` | Explicit competent permission covers this precise live activity, subject to conditions. Requires institutional approval and its own live-use evidence. |
| Live use | `NOT_APPLICABLE`, `UNKNOWN` | No live activity applies, with explanation, or permission has not been established. |

Each facet carries `status`, `evidence_refs`, and `rationale`. Definitive positive and negative classifications need evidence. Unknown/inapplicable classifications may have empty references, but require an explanation. Authority and implementation remain separate: a past action may have implementation evidence while its authority is unknown; flag that discrepancy without rewriting observed facts. Never turn implementation into retrospective permission.

## Scope, precedence and supersession

Define `scope` narrowly enough to identify the relevant claim or body of work, and `role` to identify its function (for example, selected research reference versus historical first-pass dispositions). `CURRENT` must be unique for each scope/role pair. Two artifacts may both be current when they answer distinct questions. A report's current financial table does not make its old operational assumptions current.

Supersession requires an explicit relation to a registered replacement with the same scope and role. References must resolve and chains must be acyclic. A candidate draft cannot supersede an artifact. Do not infer replacement from numbering, date or matching file hashes. Preserve the original artifact, designation decision, effective scope, old conclusions and correction rationale. A correction of two assertions does not rewrite all earlier first-pass outcomes.

The existing [current-reference pointer](../data/current_research_reference.json) designates research reference 13.0 only for the fixed V8/V9 obligations. It preserves the historical 59-supported/two-held first pass, records both reporting cases as blocked for live use, and keeps the course watch paused. These facts illustrate why a single ordered status field is inadequate; this document neither changes them nor declares a new baseline. A future inventory must cite the pointer and relevant adoption/lineage records when assigning actual statuses.

When current sources conflict, retain an unresolved issue with the competing claims, exact scopes, cutoffs, authority, directness, supersession evidence and blocked conclusion. Use the final adopted instrument for institutional action and direct records for implementation. A later narrative is not automatically a replacement for a more authoritative source. Do not average conflicting statuses or silently close discrepancies.

## Separation from candidate advancement

The nine F03 states describe an intervention's evidence maturity. These five facets describe an artifact or scoped status snapshot. `CANDIDATE` currency is not `SCREENING_CANDIDATE`; `APPROVED` is not `IMPLEMENTATION_READY`; `IMPLEMENTED` is not `REALIZED`; and `CURRENT` is not a verified finding. Keep the fields separate and link by artifact/intervention ID if needed. No savings finding is permitted before the F03 financial gate, regardless of this model's statuses.

## Machine-readable contract and validation

[repository_status_schema.json](../metadata/repository_status_schema.json) is a JSON Schema draft 2020-12 contract. An envelope has `schema_version: 1` and `records`. Each record includes:

- `artifact_id`, `path`, `version`, `scope`, `role`: nonempty strings; IDs are unique and paths are repository-relative without traversal.
- `as_of`, `evidence_cutoff`: ISO dates; the evidence cutoff cannot follow the snapshot.
- `superseded_by`: replacement artifact ID for `SUPERSEDED`, otherwise null.
- All five facet objects, each containing status, distinct evidence-reference strings and a rationale.

Every status needs a declared scope and date. Evidence references may be safe record IDs or public source locators; restricted evidence remains in approved storage. A receipt's presence is not authentication. Snapshot creation cannot change a real activity's state. Corrections create a new snapshot/version and preserve the prior snapshot and reason; append-only preservation requires an independently retained prior snapshot, not a claim made by this validator.

The standard-library validator checks schema vocabulary, required fields, dates, evidence declarations, current-slot conflicts, same-scope supersession, cycles and the approval prerequisite for authorized live use. It does not implement arbitrary external JSON Schema documents: `--schema` selects this contract's vocabulary/structure, and cross-record rules are implemented explicitly. Empty input validates no actual artifact statuses. It does not read or validate a real current-status register by default.

```sh
python scripts/validate_repository_status.py
python tests/check_repository_status.py
python scripts/validate_repository_status.py --records /approved/path/status_snapshot.json
```

Tests use conspicuously synthetic V13-like and paused-watch examples. Passing them establishes record consistency only. Substantive authority, source authentication, dates of actual acts, confidentiality, and implementation claims still need review under F04/F06. Actual status assignment and migration belong to subsequent canonical-manifest and current-status tasks.
