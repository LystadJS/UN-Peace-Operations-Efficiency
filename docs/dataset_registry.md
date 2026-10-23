# A02 — Dataset registry

The [dataset registry](../metadata/dataset_registry.csv) catalogs every CSV and JSON artifact in the [frozen A01–A06 scope](../metadata/repository_audit_scope.json), including historical views, source captures, manifests, fixtures and F01–F06 standards. Covering the complete structured-file population avoids silently excluding a dataset whose current status is unresolved. This registry does not declare every file current. New audit-wave outputs and ignored/private files are outside the frozen input universe.

## Evidence and coverage

Each row records the path, exact input hash, storage shape, stored row count where tabular, columns, key declaration or candidate, observed key uniqueness/missingness, exact duplicate excess, period, temporal/source field names, grain, interpretation limits and repository role. Counts represent stored records. They are not counts of unique events, people, delivered courses, verified transactions or opportunities.

The curated semantic layer covers principal departmental, GA, SPM, finance, transaction-control and current V13 research tables. It was checked against [the data dictionary](data_dictionary.md), [Phase 3 validation](../scripts/validate_phase3.py), [SPM validation](../scripts/validate_spm_2027.py), [transaction assessment](transaction_level_validation.md), [V13 adoption](v13_reference_adoption.md) and the [current reference pointer](../data/current_research_reference.json). This is review of repository evidence, not reauthentication of original UN source documents. Remaining rows explicitly say `profile_only_semantics_unreviewed`; inferred column names do not establish their substantive grain or period.

The historical data dictionary contains successive descriptions of the same table, including older open-reconciliation statements alongside later completed-reconciliation sections. All matching line anchors remain visible; they are not merged into an invented source consensus. The semantic overrides use the later detailed financing sections and their corresponding validators. The registry does not refresh legal or financial status beyond the retained sources.

## Keys, shapes and statuses

- `validator_declared` means a literal key declaration was found in a retained validation script and the column exists. It does not mean that script was executed or the declared grain independently confirmed. `key_check` separately reports observed uniqueness and missingness.
- `first_column_candidate_only` is a mechanically tested candidate, never a certified primary key. A unique snapshot column may cease to be unique when new observations arrive. Composite keys are not invented by trial-and-error searching.
- Duplicate counts are excess records beyond distinct values, not the count of all affected rows. Exact row duplicates use all stored columns.
- Empty tables provide no positive key evidence. Non-tabular JSON objects, scalar arrays and empty arrays have a blank `row_count`; object property counts appear only as `column_count` and must not be interpreted as observations.
- `current_adopted_research_reference` is assigned only to the exact path selected by the current pointer. Its adoption/lineage companions are scoped to the same fixed V8/V9 research obligations. Version-folder names alone establish provenance, not current authority or supersession.
- Root datasets without a controlling current manifest remain `currency_unresolved`. This preserves the separate [repository-status model](repository_status_model.md) workstream's authority to define current versus historical. There is no assumption that root location means current.

## Reproduction and limits

Run from the repository root:

```sh
python -B scripts/build_dataset_registry.py
python -B scripts/build_dataset_registry.py --check
python -B tests/check_dataset_registry.py
```

The generator verifies every profiled input against its frozen SHA-256. A changed source requires an explicit new audit scope, rather than silently regenerating a different historical catalog. Generated outputs are deterministic for identical inputs. No raw source, historical release, ranking, research adoption, live-use gate or paused activity is changed.

This registry is an entry point for the next contract-building task. Unreviewed grains, unresolved currency, absent source anchors and nonunique candidate keys are specific follow-up work, not waived defects. It does not establish data completeness, source truth, operational duplication, legal compliance or savings. Financial and status interpretations follow [F01–F06](foundation_standards.md).
