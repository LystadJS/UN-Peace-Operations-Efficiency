# Dataset contracts and coverage — P02 and P05

The [dataset contracts](../data/portfolio/dataset_contracts.json) carry all **324 frozen registry artifacts** forward with their declared grain, keys, period, source fields, interpretation limits and input hashes. Exactly 37 have repository semantic review; 287 remain provisional structural profiles. Neither group has been accepted by an operational owner or authenticated against a complete underlying transaction population. Installing a contract does not resolve its acceptance gate.

Each contract separates observed key checks from certified business identity. Join cardinality remains uncertified until a reviewer verifies identity, periods, units, unmatched keys and duplicate amplification. Frozen input hashes anchor the historical snapshot rather than promise that every path's live contents remain identical after later controls migrations. The scope excludes newer roadmap files and restricted records; future additions need an explicit registry extension.

The [coverage matrix](../data/portfolio/coverage_matrix.json) keeps identity, financial, function, reform and operational evidence coverage separate. It contains the eleven mission-budget-register records and 36 continuing SPM proposal records as distinct source populations. Six of the eleven have retained GA maintenance reconciliations. These are record counts, not a deduplicated universe of UN entities. There is no worldwide budget denominator and no budget-to-waste percentage.

Function links are retained screening crosswalks or programmed categories. Reform links are confined to the selected historical GA-directive table and require action-specific authority review; they are not complete UNGA80/81 compliance coverage. Operational evidence is explicitly not assessed by this matrix. Missing links indicate unmapped evidence, not absent work or noncompliance. Unknown waste coverage is `null`, never a fabricated zero. Exact source-context aliases from the P01 entity registry supply identity links; those links do not certify business grain, lifecycle, mandate status or analytical joins.

Reproduce the declarations and check deterministic consistency from the repository root:

```sh
python -B scripts/build_portfolio_coverage.py --write
python -B scripts/build_portfolio_coverage.py --check
python -B tests/check_portfolio_coverage.py
```

P02 produces the contracts. P05 produces the coverage matrix. The shared generator deliberately reads only explicitly listed retained sources, so unfinished parallel work cannot silently change its population or authority claims.
