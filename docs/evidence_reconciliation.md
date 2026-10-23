# Operational evidence intake, reconciliation and cost comparison — E08–E10

These prospective tools validate supplied declarations. They neither authenticate documents nor establish institutional approval, implementation, operational equivalence, or financial validation. No real records were supplied, and no monetary finding is generated. Historical R matching remains unchanged; the new contracts are explicitly versioned.

## E08: intake contract

`scripts/validate_operational_evidence.py INPUT.json` requires `schema_version: E08-1.0`, an explicit evidence mode (`SYNTHETIC`, `PUBLIC_RESEARCH`, or `RESTRICTED_APPROVED`) and one to 10,000 records. Each record needs a unique record ID, case, entity, source receipt and exact source locator, period start/end, and a supported record type. Dates use YYYY-MM-DD. Numeric observations are finite nonnegative decimal strings, never binary floats. Unknown required observations cause an invalid receipt; zero is an explicitly supplied observation, not a missing-value default.

| Record type | Additional required observations |
| --- | --- |
| transaction | Unique canonical economic-event ID, cost object, fund, currency, currency-unit basis, payer/provider, event date, event type and amount; reversal target for reversals |
| asset | Asset and movement IDs, release/receipt/disposal action, custodians, condition, event date and positive quantity |
| post | Unique post, establishment/abolition/redeployment/vacancy/occupation action, effective date, fund, FTE and transferred-work receipt |
| workload | Activity, output and pseudonymous worker IDs, unit, measurement method and quantity |
| outcome | Metric, population definition, unit, method, prospective threshold receipt, value and positive denominator |

Asset fields support later release/receipt reconciliation; merely passing intake does not prove custody transfer. Post action does not prove payroll release, and workload does not prove removable capacity. An outcome observation does not establish causal effect or compliance with its threshold. Restricted records belong in approved storage outside public Git; supply only permitted derivatives.

## E09: explicit transaction allocation

`scripts/reconcile_evidence_transactions.py INPUT.json` accepts the E08 envelope with transaction records only, `reconciliation_version: E09-1.0`, a declared integer `timing_tolerance_days` between 0 and 366, and an explicit `allocations` list. An allocation contains `allocation_id`, `claim_id`, `settlement_id`, positive decimal-string `amount`, and an allocation source receipt. Settlement records are typed `PAYMENT` or `CASH_RECEIPT`; a `CLAIM` alone is not cash received.

Many claims can reference one settlement and one claim can reference many settlements. Allocation identity must be unique, repeated claim/settlement edges are rejected, and each side's allocated total cannot exceed its available amount. Claims and settlements must match exactly on case, cost object, fund, currency, unit, service period and counterparties. A supported period bridge requires an upstream reviewed conversion into a new contract; this tool performs no automatic period, fund or currency netting.

`REVERSAL` records reference an existing non-reversal record in the same perimeter and cannot predate it. Their amounts reduce available capacity; over-reversal and an allocation exceeding revised capacity are exceptions. A reversed settlement must have its allocations reconsidered. Partial settlements and unmatched claims remain explicit exceptions. Settlement dates before the claim date or beyond the declared tolerance require review; the tool does not silently assume prepayments or same-year service delivery.

The matcher deliberately performs no subset search or greedy allocation. Equal amounts do not identify a payment. If multiple plausible allocations exist, an evidence-backed allocation is required; supplying no allocations leaves the records unmatched. The reconciliation receipt distinguishes a declared cash receipt from other financial records, without authenticating either. Payer payments and provider receipts must not be supplied as independent economic settlements of the same claim; evidence custodians must reconcile counterpart postings and provide one canonical settlement plus its supporting references before intake. Reconciliation proves only consistency of the supplied declared population, not full ledger coverage or benefit.

## E10: full-system comparison

`scripts/calculate_net_benefit.py INPUT.json` requires `calculator_version: E10-1.0` and delegates cost rules to [the P11 evaluator](../scripts/evaluate_intervention.py) and [cost-model contract](../data/portfolio/cost_model.json). Supply its comparable baseline/intervention frames, full affected-entity and cost-component coverage receipts, frozen feasible counterfactual including prebooked changes, paired internal transfers and operational safeguard declarations. Retained source work, receiving-team work, transition, ongoing compliance and residual liabilities stay in scope. Missing costs, unsupported comparability, unmatched internal transfers or incomplete safeguards withhold the result.

The result is an **unvalidated declared cost difference**, with separate benefit classes and no savings amount, candidate promotion, cashable classification or realization assertion. Public or restricted input labels do not transform declarations into authenticated evidence. Aggregation still requires compatible scenarios and unique benefit-pool allocations. This wrapper does not replace operational/financial adjudication or the [candidate advancement standard](candidate_advancement.md).

Run the three corresponding `tests/check_operational_evidence.py`, `tests/check_evidence_reconciliation.py` and `tests/check_net_benefit.py` scripts. Fixtures are synthetic and test missing inputs, scope separation, partial settlement, reversals, duplicate allocation, timing, one-to-many/many-to-one allocation, full-system costs and guardrail withholding. Passing these tests is software verification only.
