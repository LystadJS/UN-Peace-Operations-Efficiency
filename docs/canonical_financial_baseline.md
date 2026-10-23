# Canonical financial baseline — P03 and P04

The [financial baseline](../data/portfolio/financial_baseline.json) derives resource controls with exact decimal arithmetic from seven retained datasets. Its evidence cutoff is 8 October 2026; assembly on 23 October does not refresh underlying governing texts. Full source rows and file hashes preserve the component and authority distinctions.

| Control | USD millions | Status and perimeter |
| --- | ---: | --- |
| Six mission maintenance | 4,028.1880 | 2026/27 GA-approved gross maintenance in retained corpus |
| Eleven entity maintenance | 4,625.9401 | 2026/27 approved-resource note; contains the six |
| 36 continuing SPMs | 419.4119 | Calendar-2027 SG net regular-budget proposal |
| SPM RSCE share | 3.2591 | Already within the next total |
| SPM total including RSCE | 422.6710 | Calendar-2027 SG proposal; not GA appropriation |
| 31 embedded measures | 14.6925 | Already included in proposed baseline; not additional benefits |
| Three discontinued missions | 121.4731 | Calendar-2026 budgets; prior transitions excluded from incremental benefits |

Six inclusive mission appropriations include maintenance plus support account, UNLB and RSCE shares. They are stored separately from maintenance and reconciled per mission. SG requests and adopted maintenance are separate versions, so their difference is a budget decision rather than a saving. The six are a strict subset of the eleven; these populations cannot be added together. The SPM mission total plus its RSCE share reconciles to the inclusive SPM control, and none may be added again to that parent.

P04 checks source-derived identities and rejects aggregation requests that overlap parents and components, mix periods or authority versions, or treat embedded measures and closures as new benefits. The selection validator deliberately requires an explicit disjoint cost-object bridge for any multi-control aggregation. It does not claim that accounting identities prove absence of transaction-level double counting. Shared-service provider and client costs still require a full-system reconciliation before an intervention benefit can be assessed.

Unknown cashable savings, realized savings, capacity gain, recovery and cost avoidance remain `null` with status `NOT_ESTIMATED`. Source budget amounts do not fill those fields. No aggregate peacekeeping-plus-SPM total or operational savings finding is asserted.

Run `python -B scripts/build_financial_baseline.py --write` to regenerate P03, and `--check` to verify freshness. Run `python -B scripts/validate_financial_nonadditivity.py` for P04 and `python -B tests/check_financial_baseline.py` for corruption and overlap tests. Optional `--aggregate spm_total spm_rsce` must fail, showing the prohibited parent/component combination.
