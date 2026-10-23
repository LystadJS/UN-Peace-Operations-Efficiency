# Priority-case lineage review

This supplement resolves concrete paths for C01–C03 financial controls while preserving the original frozen A04 graph. It does not authenticate original UN documents or actual transactions.

Six recognized expressions are selected from the historical 196: three helper call sets are statically resolved; one white-paper helper is resolved only for three selected SPM financial calls; two optional external-PDF-directory branches remain unresolved. The historical denominator remains 196.

| Source operation | Selected disposition | Scope |
| --- | --- | --- |
| `scripts/validate_transaction_controls.py:10` | RESOLVED_STATIC_CALL_SET | 5 repository paths; see exact call sites in the receipt |
| `scripts/validate_phase3.py:26` | RESOLVED_STATIC_DICTIONARY_SET | 13 repository paths; see exact call sites in the receipt |
| `scripts/validate_spm_2027.py:27` | RESOLVED_STATIC_DICTIONARY_SET | 15 repository paths; see exact call sites in the receipt |
| `reports/white_paper_2026-10-15/analyze.py:11` | PARTIAL_SELECTED_FINANCIAL_CALLS | 3 repository paths; see exact call sites in the receipt |
| `scripts/validate_phase3.py:97` | EXTERNAL_SOURCE_DIRECTORY_UNRESOLVED | 0 repository paths; see exact call sites in the receipt |
| `scripts/validate_spm_2027.py:88` | EXTERNAL_SOURCE_DIRECTORY_UNRESOLVED | 0 repository paths; see exact call sites in the receipt |

## Priority financial claim chains

| Case | Retained claim | USD | Meaning |
| --- | --- | ---: | --- |
| C01 | RSCE_2027_SPM_share | 3259100 | Proposed internal allocation, calendar 2027; not a transaction or benefit. |
| C01 | RSCE_corporate_total | 45911600 | Fiscal 2026/27 corporate total; differs from calendar SPM-only share. |
| C01 | RSCE_mixed_client_share | 3443200 | Fiscal 2026/27 mixed SPM/observer-client share; not comparable directly to RS01. |
| C01 | RSCE_calendar_share_change | 936100 | Same calendar-share proposal comparison; not overbilling or savings. |
| C02 | UNSCOL_embedded_asset_measures | 438100 | Already embedded projected vehicle/ICT/consumable measures; not incremental realized benefit. |
| C03 | BINUH_aviation_proposal_difference | 1400000 | Published budget comparator, not a settled aviation invoice. |
| C03 | BINUH_broader_support | 4000000 | Broader support proposal; not additive to a potentially included aviation component. |

The path is retained control row → arithmetic/declaration validator → exact case evidence snapshot. `validate_transaction_controls.py` is a consumer and guard, not a data-extraction producer. The original transcription step has no captured executable producer; its authority must be evaluated from the underlying official source. `build_financial_baseline.py` separately computes aggregate financial perimeters and does not produce the individual transaction-control rows.

The optional `--source-dir` branches in the GA and SPM validators need actual externally supplied PDFs and a successful byte-check receipt. A hash string in a manifest is not evidence that the file was present or checked. Internal invoice, asset, post, flight and workload branches remain unavailable. None of these repository lineage paths proves duplicated expenditure, implementation, owner approval or a benefit.

The [machine-readable receipt](../../data/priority_cases/lineage_review.json) retains source hashes, expression and call-site lines, selected row identities, formula guard lines and case snapshot locators. Source changes invalidate this supplement until reviewed and regenerated.

Reproduce with `python -B scripts/validate_priority_lineage.py --check`; use `--write` only after reviewing changed source bytes. Unit tests: `python -B tests/check_priority_lineage.py`.
