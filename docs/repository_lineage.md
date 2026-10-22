# A04 — Repository lineage graph

Scope: `A01-A06-2026-10-22` at commit `32f02e5e689ad9f43e762d5985330df20dda1719`. The frozen population contains 554 files, including F01–F06 inputs. This wave’s generated outputs and ignored files are excluded to avoid a self-changing denominator.

## Outputs and interpretation

- [Nodes](../metadata/lineage_nodes.csv): every one of the 554 frozen files exactly once.
- [Edges](../metadata/lineage_edges.csv): 4151 evidence-bearing static edges.
- Direction is actor/document/manifest → referenced file. `WRITES` indicates a statically resolved output operation; it does not prove execution. `READS` indicates a resolved read or named read-helper call. `IMPORTS`, `INVOKES`, `PRESERVES`, `DOCUMENTS` and `REFERENCES` retain their distinct meanings.
- A documentation mention, hash manifest, workflow artifact upload, or source path is never converted into a producer. `PRESERVES` means a SHA-256 pin is recorded; it does not prove a check ran.
- Source captures and binaries are nodes even when no parser can establish their producers. Sources, tests and generated artifacts are connected only where exact static evidence exists.
- No repository script was imported or executed and no network source was accessed by this extraction.

## Extraction coverage

| Relationship | Edges |
| --- | ---: |
| DOCUMENTS | 538 |
| IMPORTS | 8 |
| INVOKES | 110 |
| PRESERVES | 476 |
| READS | 115 |
| REFERENCES | 2873 |
| VALIDATES | 1 |
| WRITES | 30 |

`VALIDATES` is emitted only when an explicit assertion/guard contains a statically resolved file read or existence check. The assertion condition is retained as evidence; this marks a check relationship, not a claim that it ran or that the checked content is substantively correct. Generic validation helpers and dynamically selected files remain unresolved.

## Key paths inspected

- V13 adoption: `scripts/adopt_v13_reference.py` pins V12 inputs through hash dictionaries; local imports connect its patch helper. Static output methods involving dynamically assembled maps are unresolved rather than inferred from filenames.
- White paper: `reports/white_paper_2026-10-15/analyze.py` reads named financial and research tables; resolved `OUT` write expressions connect metrics, chart data and manifests. The publication workflow explicitly invokes analysis, charting, document construction and validation. These links do not establish fresh legal or operational verification.

## Limits and unresolved dependencies

The Python extractor evaluates only constants, module-level assignments, path joins, `parent`/`parents`, and simple `Path`/`str`/`resolve` expressions. It does not execute helper functions, follow arbitrary loop variables, reconstruct dynamic output maps, resolve glob populations, or perform full data-flow analysis. Named read-helper calls are explicitly lower-confidence. R and embedded Python are scanned only for exact references; R call semantics are not resolved. Workflow invocation extraction uses repository-root semantics only when no `cd` or `working-directory` override is present; overrides are held unresolved. Relative Markdown links use the containing document directory.

52 files have 196 unresolved read/write/invocation or parse expressions. These are extraction gaps, not repository defects. The following list is exhaustive for expressions recognized by this extractor; other dynamic operations may remain undetected.

### `reports/white_paper_2026-10-15/analyze.py`

- Line 11: `READS` — `<dynamic expression>`
- Line 13: `READS` — `<dynamic expression>`
- Line 20: `READS` — `<dynamic expression>`
- Line 47: `READS` — `<dynamic expression>`

### `reports/white_paper_2026-10-15/validate.py`

- Line 8: `READS` — `<dynamic expression>`
- Line 10: `READS` — `<dynamic expression>`
- Line 26: `READS` — `<dynamic expression>`
- Line 39: `READS` — `<dynamic expression>`
- Line 52: `READS` — `<dynamic expression>`

### `scripts/adopt_v13_reference.py`

- Line 49: `READS` — `<dynamic expression>`
- Line 127: `READS` — `<dynamic expression>`
- Line 128: `READS` — `<dynamic expression>`
- Line 129: `READS` — `<dynamic expression>`
- Line 132: `READS` — `<dynamic expression>`
- Line 134: `READS` — `<dynamic expression>`
- Line 136: `READS` — `<dynamic expression>`
- Line 140: `READS` — `<dynamic expression>`
- Line 249: `READS` — `<dynamic expression>`
- Line 257: `WRITES` — `<dynamic expression>`
- Line 259: `READS` — `<dynamic expression>`

### `scripts/audit_census_v6.py`

- Line 22: `READS` — `<dynamic expression>`
- Line 24: `READS` — `<dynamic expression>`
- Line 25: `READS` — `<dynamic expression>`
- Line 26: `WRITES` — `<dynamic expression>`
- Line 30: `WRITES` — `<dynamic expression>`
- Line 166: `READS` — `<dynamic expression>`

### `scripts/backfill_census_legacy_dates.py`

- Line 34: `READS` — `<dynamic expression>`
- Line 44: `WRITES` — `<dynamic expression>`
- Line 62: `READS` — `<dynamic expression>`

### `scripts/build_mission_archive_metadata.py`

- Line 87: `WRITES` — `<dynamic expression>`

### `scripts/build_systematic_census.py`

- Line 204: `WRITES` — `<dynamic expression>`
- Line 227: `READS` — `<dynamic expression>`
- Line 294: `WRITES` — `<dynamic expression>`

### `scripts/build_systematic_unified_views.py`

- Line 14: `READS` — `<dynamic expression>`
- Line 22: `WRITES` — `<dynamic expression>`

### `scripts/build_v10_protocol.py`

- Line 48: `READS` — `<dynamic expression>`
- Line 55: `WRITES` — `<dynamic expression>`
- Line 58: `READS` — `<dynamic expression>`
- Line 66: `WRITES` — `<dynamic expression>`
- Line 76: `READS` — `<dynamic expression>`
- Line 194: `READS` — `<dynamic expression>`
- Line 204: `READS` — `<dynamic expression>`
- Line 215: `READS` — `<dynamic expression>`
- Line 225: `READS` — `<dynamic expression>`
- Line 230: `READS` — `<dynamic expression>`
- Line 236: `READS` — `<dynamic expression>`

### `scripts/build_v8_design.py`

- Line 15: `READS` — `<dynamic expression>`
- Line 17: `READS` — `<dynamic expression>`

### `scripts/build_v8_pilot.py`

- Line 19: `READS` — `<dynamic expression>`
- Line 23: `WRITES` — `<dynamic expression>`
- Line 26: `READS` — `<dynamic expression>`
- Line 32: `READS` — `<dynamic expression>`
- Line 37: `WRITES` — `<dynamic expression>`
- Line 56: `READS` — `<dynamic expression>`
- Line 221: `READS` — `<dynamic expression>`

### `scripts/classify_mission_archive_metadata.py`

- Line 28: `READS` — `<dynamic expression>`
- Line 37: `WRITES` — `<dynamic expression>`

### `scripts/collect_census_v5.py`

- Line 33: `READS` — `<dynamic expression>`
- Line 38: `WRITES` — `<dynamic expression>`
- Line 91: `WRITES` — `<dynamic expression>`
- Line 141: `READS` — `<dynamic expression>`

### `scripts/collect_census_v6_sources.py`

- Line 15: `READS` — `<dynamic expression>`
- Line 39: `WRITES` — `<dynamic expression>`
- Line 41: `WRITES` — `<dynamic expression>`

### `scripts/collect_council_index.py`

- Line 93: `READS` — `<dynamic expression>`
- Line 107: `WRITES` — `<dynamic expression>`
- Line 112: `WRITES` — `<dynamic expression>`

### `scripts/collect_deeper_archive_frame_v4.py`

- Line 25: `READS` — `<dynamic expression>`

### `scripts/collect_extended_official_archive.py`

- Line 93: `WRITES` — `<dynamic expression>`
- Line 134: `WRITES` — `<dynamic expression>`

### `scripts/expand_published_census.py`

- Line 40: `READS` — `<dynamic expression>`
- Line 45: `WRITES` — `<dynamic expression>`
- Line 65: `WRITES` — `<dynamic expression>`
- Line 205: `WRITES` — `<dynamic expression>`
- Line 282: `WRITES` — `<dynamic expression>`

### `scripts/finalize_census_v5.py`

- Line 21: `READS` — `<dynamic expression>`
- Line 26: `WRITES` — `<dynamic expression>`
- Line 37: `READS` — `<dynamic expression>`
- Line 40: `WRITES` — `<dynamic expression>`
- Line 48: `READS` — `<dynamic expression>`
- Line 91: `WRITES` — `<dynamic expression>`
- Line 169: `READS` — `<dynamic expression>`
- Line 173: `WRITES` — `<dynamic expression>`
- Line 175: `READS` — `<dynamic expression>`
- Line 194: `WRITES` — `<dynamic expression>`
- Line 196: `READS` — `<dynamic expression>`
- Line 199: `WRITES` — `<dynamic expression>`

### `scripts/finalize_census_v7.py`

- Line 29: `READS` — `<dynamic expression>`
- Line 33: `WRITES` — `<dynamic expression>`
- Line 36: `READS` — `<dynamic expression>`
- Line 50: `READS` — `<dynamic expression>`
- Line 56: `READS` — `<dynamic expression>`
- Line 166: `WRITES` — `<dynamic expression>`

### `scripts/prepare_v12_patch.py`

- Line 58: `READS` — `<dynamic expression>`
- Line 62: `READS` — `<dynamic expression>`
- Line 77: `READS` — `<dynamic expression>`
- Line 82: `READS` — `<dynamic expression>`
- Line 90: `READS` — `<dynamic expression>`
- Line 98: `READS` — `<dynamic expression>`
- Line 99: `READS` — `<dynamic expression>`
- Line 105: `READS` — `<dynamic expression>`
- Line 181: `READS` — `<dynamic expression>`
- Line 189: `READS` — `<dynamic expression>`
- Line 190: `READS` — `<dynamic expression>`
- Line 200: `READS` — `<dynamic expression>`
- Line 204: `READS` — `<dynamic expression>`
- Line 207: `READS` — `<dynamic expression>`
- Line 235: `READS` — `<dynamic expression>`
- Line 306: `WRITES` — `<dynamic expression>`
- Line 309: `READS` — `<dynamic expression>`

### `scripts/recover_census_v6_sources.py`

- Line 37: `WRITES` — `<dynamic expression>`
- Line 59: `WRITES` — `<dynamic expression>`
- Line 82: `WRITES` — `<dynamic expression>`

### `scripts/recover_census_v7_layout.py`

- Line 39: `WRITES` — `<dynamic expression>`
- Line 43: `WRITES` — `<dynamic expression>`

### `scripts/recover_census_v7_transcripts.py`

- Line 28: `READS` — `<dynamic expression>`
- Line 33: `WRITES` — `<dynamic expression>`
- Line 112: `WRITES` — `<dynamic expression>`
- Line 114: `WRITES` — `<dynamic expression>`
- Line 127: `READS` — `<dynamic expression>`
- Line 158: `READS` — `<dynamic expression>`
- Line 163: `READS` — `<dynamic expression>`

### `scripts/rehearse_v11.py`

- Line 16: `READS` — `<dynamic expression>`
- Line 18: `READS` — `<dynamic expression>`
- Line 19: `WRITES` — `<dynamic expression>`
- Line 22: `WRITES` — `<dynamic expression>`
- Line 40: `READS` — `<dynamic expression>`
- Line 51: `READS` — `<dynamic expression>`
- Line 58: `READS` — `<dynamic expression>`
- Line 64: `READS` — `<dynamic expression>`

### `scripts/v9_cyprus.py`

- Line 13: `READS` — `<dynamic expression>`
- Line 15: `WRITES` — `<dynamic expression>`
- Line 16: `READS` — `<dynamic expression>`
- Line 22: `WRITES` — `<dynamic expression>`
- Line 32: `READS` — `<dynamic expression>`

### `scripts/validate_acabq_2027.py`

- Line 28: `READS` — `<dynamic expression>`
- Line 127: `READS` — `<dynamic expression>`

### `scripts/validate_candidate_advancement.py`

- Line 40: `READS` — `<dynamic expression>`

### `scripts/validate_census_2025_2026.py`

- Line 8: `READS` — `<dynamic expression>`

### `scripts/validate_census_v2_release.py`

- Line 22: `READS` — `<dynamic expression>`

### `scripts/validate_census_v3_extension.py`

- Line 18: `READS` — `<dynamic expression>`

### `scripts/validate_census_v4_attendance.py`

- Line 9: `READS` — `<dynamic expression>`

### `scripts/validate_census_v5.py`

- Line 24: `READS` — `<dynamic expression>`
- Line 37: `WRITES` — `<dynamic expression>`
- Line 74: `READS` — `<dynamic expression>`
- Line 167: `READS` — `<dynamic expression>`

### `scripts/validate_crosswalk.py`

- Line 41: `READS` — `<dynamic expression>`
- Line 58: `READS` — `<dynamic expression>`
- Line 74: `READS` — `<dynamic expression>`

### `scripts/validate_mission_archive_candidates.py`

- Line 8: `READS` — `<dynamic expression>`

### `scripts/validate_mission_archive_metadata.py`

- Line 9: `READS` — `<dynamic expression>`

### `scripts/validate_mission_audit.py`

- Line 19: `READS` — `<dynamic expression>`
- Line 35: `READS` — `<dynamic expression>`

### `scripts/validate_owner_review_package.py`

- Line 21: `READS` — `<dynamic expression>`
- Line 24: `READS` — `<dynamic expression>`
- Line 27: `READS` — `<dynamic expression>`
- Line 43: `READS` — `<dynamic expression>`
- Line 44: `READS` — `<dynamic expression>`
- Line 53: `READS` — `<dynamic expression>`
- Line 63: `READS` — `<dynamic expression>`
- Line 105: `READS` — `<dynamic expression>`

### `scripts/validate_phase11_systematic.py`

- Line 16: `READS` — `<dynamic expression>`

### `scripts/validate_phase3.py`

- Line 26: `READS` — `<dynamic expression>`
- Line 97: `READS` — `<dynamic expression>`

### `scripts/validate_phase7.py`

- Line 6: `READS` — `<dynamic expression>`

### `scripts/validate_phase9_clusterIII.py`

- Line 30: `READS` — `<dynamic expression>`

### `scripts/validate_public_only.py`

- Line 22: `READS` — `<dynamic expression>`

### `scripts/validate_retrospective_matches.py`

- Line 26: `READS` — `<dynamic expression>`

### `scripts/validate_spm_2027.py`

- Line 27: `READS` — `<dynamic expression>`
- Line 88: `READS` — `<dynamic expression>`

### `scripts/validate_systematic_census.py`

- Line 20: `READS` — `<dynamic expression>`

### `scripts/validate_transaction_controls.py`

- Line 10: `READS` — `<dynamic expression>`

### `tests/check_published_census.py`

- Line 59: `READS` — `<dynamic expression>`
- Line 60: `READS` — `<dynamic expression>`

### `tests/check_v10_protocol.py`

- Line 18: `READS` — `<dynamic expression>`
- Line 22: `READS` — `<dynamic expression>`
- Line 26: `READS` — `<dynamic expression>`
- Line 36: `READS` — `<dynamic expression>`
- Line 66: `READS` — `<dynamic expression>`
- Line 66: `WRITES` — `<dynamic expression>`
- Line 70: `WRITES` — `<dynamic expression>`
- Line 72: `READS` — `<dynamic expression>`

### `tests/check_v12_patch.py`

- Line 19: `READS` — `<repo>`
- Line 20: `READS` — `<repo>`
- Line 57: `READS` — `<repo>`
- Line 101: `READS` — `<repo>`
- Line 113: `READS` — `<dynamic expression>`
- Line 116: `READS` — `<repo>`
- Line 117: `READS` — `<repo>`

### `tests/check_v13_reference.py`

- Line 19: `READS` — `<dynamic expression>`
- Line 30: `READS` — `<dynamic expression>`
- Line 81: `READS` — `<dynamic expression>`
- Line 96: `READS` — `<dynamic expression>`
- Line 98: `WRITES` — `<dynamic expression>`
- Line 103: `READS` — `<dynamic expression>`

### `tests/check_v8_pilot.py`

- Line 82: `READS` — `<dynamic expression>`

## Files without incoming static references

55 frozen files have no incoming reference. This is an orphan-screening list, not a deletion recommendation; entrypoints, raw sources, and manually produced artifacts may legitimately appear here.

- `.github/workflows/additional_mission_training_frame.yml`
- `.github/workflows/census_v5.yml`
- `.github/workflows/census_v5_release.yml`
- `.github/workflows/census_v6.yml`
- `.github/workflows/census_v6_release.yml`
- `.github/workflows/census_v7_recovery.yml`
- `.github/workflows/census_v7_release.yml`
- `.github/workflows/deeper_official_archives_v4.yml`
- `.github/workflows/foundation_standards.yml`
- `.github/workflows/mission_archive_census.yml`
- `.github/workflows/owner_review_package.yml`
- `.github/workflows/published_census_v2.yml`
- `.github/workflows/systematic_census.yml`
- `.github/workflows/systematic_evidence_views.yml`
- `.github/workflows/v10_protocol_ci.yml`
- `.github/workflows/v10_protocol_release.yml`
- `.github/workflows/v11_tabletop.yml`
- `.github/workflows/v11_validate.yml`
- `.github/workflows/v12_reference_patch.yml`
- `.github/workflows/v13_reference_adoption.yml`
- `.github/workflows/v8_release.yml`
- `.github/workflows/v8_source_capture.yml`
- `.github/workflows/v8_validate.yml`
- `.github/workflows/v9_checks.yml`
- `.github/workflows/v9_release.yml`
- `.github/workflows/white_paper_2026.yml`
- `.gitignore`
- `README.md`
- `data/census_v12/output_manifest.json`
- `data/census_v12/validation_receipt.json`
- `data/census_v13/validation_receipt.json`
- `reports/white_paper_2026-10-15/README.md`
- `reports/white_paper_2026-10-15/deliverables/UN_Peace_Operations_White_Paper_2026-10-15.pdf`
- `reports/white_paper_2026-10-15/figures/01_relationships.svg`
- `reports/white_paper_2026-10-15/figures/02_function_inventory.svg`
- `reports/white_paper_2026-10-15/figures/03_mission_financing.svg`
- `reports/white_paper_2026-10-15/figures/04_requests_approvals.svg`
- `reports/white_paper_2026-10-15/figures/05_cost_mix.svg`
- `reports/white_paper_2026-10-15/figures/06_budget_variances.svg`
- `reports/white_paper_2026-10-15/figures/07_financing_perimeter.svg`
- `reports/white_paper_2026-10-15/figures/08_spm_bridge.svg`
- `reports/white_paper_2026-10-15/figures/09_cluster3.svg`
- `reports/white_paper_2026-10-15/figures/10_advisory_coverage.svg`
- `reports/white_paper_2026-10-15/figures/11_embedded.svg`
- `reports/white_paper_2026-10-15/figures/12_support_allocation.svg`
- `reports/white_paper_2026-10-15/figures/13_training.svg`
- `reports/white_paper_2026-10-15/figures/14_source_frame.svg`
- `reports/white_paper_2026-10-15/figures/15_deduplication.svg`
- `reports/white_paper_2026-10-15/figures/16_pilot_scope.svg`
- `reports/white_paper_2026-10-15/figures/17_cyprus_comparators.svg`
- `reports/white_paper_2026-10-15/figures/18_reference_history.svg`
- `reports/white_paper_2026-10-15/figures/19_evidence_gaps.svg`
- `reports/white_paper_2026-10-15/manuscript/part1.md`
- `reports/white_paper_2026-10-15/manuscript/part2.md`
- `reports/white_paper_2026-10-15/manuscript/part3.md`

## Reproduction and validation

Run `python -B scripts/build_repository_lineage.py` to rebuild, or append `--check` to compare retained outputs without changing them. Run `python -B tests/check_repository_lineage.py` for synthetic extraction controls and scope/graph checks. The generator verifies every frozen input hash and refuses input drift. New files require an explicitly refreshed audit scope, not silent inclusion.
