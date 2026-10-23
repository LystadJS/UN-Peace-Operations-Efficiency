# F05 — Financial perimeter, nonadditivity, and counterfactual standard

Status: prospective project standard. This document defines treatment of future findings; it does not reclassify historical research, verify implementation, or establish any saving. Apply it with the [decision taxonomy](decision_taxonomy.md), [candidate advancement standard](candidate_advancement.md), [source-authority standard](source_authority_standard.md), and [operational guardrails](guardrail_standard.md).

## 1. Record the financial perimeter before comparing amounts

Every amount must carry the following fields, or an explicit missing-value reason:

| Field | Required treatment |
| --- | --- |
| Record and source identity | Stable record ID, source document/version, exact page/table/paragraph, evidence cutoff, and verification status |
| Entity and ownership | Canonical entity, provider/client role, organizational parent, accountable budget holder, and relevant predecessor/successor |
| Cost object | Unique contract, purchase, asset/lot, post, invoice, service line, or other bounded object; whole budgets identify exposure, not removable cost |
| Funding | Fund, source of funds, assessed/regular/extrabudgetary classification, and material restrictions |
| Period | Start/end dates, calendar or fiscal basis, service period, posting date, and time horizon |
| Amount | Currency, unit, gross/net basis, exchange-rate source/date where relevant, and sign convention |
| Financial status | Requested, recommended, approved, apportioned, obligated, expended, paid, credited, recovered, or realized; preserve separate observations when statuses differ |
| Hierarchy | Parent total, child component, allocation, share, or independent amount, with explicit inclusion links |
| Economic boundary | External UN-system cost, internal charge, provider recovery, or noncash resource use |
| Benefit treatment | Baseline/prebooked measure, eligible incremental effect, recovery, avoidance, capacity, one-time or recurring effect |
| Aggregation control | Benefit-pool ID, nonadditivity group, scenario ID, attribution, and exclusion/eligibility reason |

Unknown amounts remain null with a reason. Zero requires evidence of zero within a specified scope and period. A source discrepancy is retained and resolved through a documented source-priority decision; it is never silently averaged away.

Use the combined affected UN entities as the default economic boundary. A client-budget reduction and a provider-budget increase must both be visible. A narrower client view may be reported alongside the system view if labeled explicitly; it cannot support a system-wide conclusion.

## 2. Establish comparability

Compare the same service, eligible population, output quality, readiness requirement, geographic coverage, risk conditions, and measurement period. Bridge differences explicitly before computing a change. In particular:

- Calendar-year SPM proposals and July–June peacekeeping appropriations remain distinct unless a supported time bridge is available. Do not assume expenditure is uniform and divide an annual total mechanically.
- SG requests, ACABQ advice, GA appropriations, apportionments, obligations, actual expenditure, and payments answer different questions. Compare like statuses or explain the approved reconciliation.
- Normalize currency, units, and price basis transparently. Isolate exchange rates, inflation, vacancy assumptions, demand, security conditions, and mandate changes from the intervention effect.
- Include necessary surge capacity and contingency reserves. Low utilization alone does not demonstrate removable cost.
- A mission closure or mandate reduction changes the service population. Its gross budget decrease is not efficiency. An incremental improvement within the authorized transition can be assessed against a compliant transition counterfactual.

If material differences cannot be bridged, report the amounts separately and withhold the net comparison.

## 3. Prevent duplicate benefit recognition

Give every underlying economic effect a stable benefit-pool ID. Use a nonadditivity group to connect cases that share a cost pool, enable the same effect, overlap in scope, or represent mutually exclusive scenarios. A group records an overlap risk; it does not imply that every member is wholly identical. Record the precise intersection and allocation rule.

Apply these controls before portfolio aggregation:

1. **One effect, once:** the same cost object, service period, scenario, and economic effect cannot be recognized in two cases. Multi-year recurring benefits may be reported by year, but annual run rate must not be added to cumulative realized amounts.
2. **Parent or children:** aggregate a parent total or its disjoint children, never both. Reconcile partial child coverage to the parent and disclose the remainder.
3. **Internal transfers:** eliminate matched payer/provider charges and recoveries on consolidation. Retain external provider expenditure. Matching internal entries establishes accounting consistency, not an efficiency.
4. **Common enablers:** allocate a shared implementation cost once using a documented rule. C02/C05/C09 reporting and knowledge-support labels cannot each claim the same removed preparation step.
5. **Alternative scenarios:** select one compatible scenario per portfolio total. Present mutually exclusive alternatives separately; do not add their potential benefits.
6. **Asset and purchase identity:** an asset's accounting value, transfer value, canceled purchase, and avoided replacement can describe the same effect. Select the appropriate economic measure rather than summing them.
7. **Existing reforms:** maintain a separate ledger for already approved or embedded measures. Their eventual realization may be verified, but they cannot be attributed again as additional opportunities generated by this project.
8. **Exclusive benefit classification:** the same dollar cannot enter savings, avoidance, and recovery totals. A case may contain distinct effects in those categories only when their cost objects, periods, and accounting treatment are demonstrably disjoint.

Each portfolio total needs an inclusion/exclusion receipt identifying eligible rows, selected scenarios, eliminated internal entries, allocated shared costs, unresolved overlaps, and the source totals to which it reconciles. Exclude unresolved amounts from certified totals while showing them as unquantified or separately qualified exposure. A total that reconciles arithmetically can still be incomplete or wrongly scoped; publish coverage and exceptions alongside it.

## 4. Freeze a feasible counterfactual

Before inspecting outcome data, record the intervention, comparison period, baseline version, comparator-selection rule, authority, output requirements, confounders, cost boundary, uncertainty method, and operational thresholds. The counterfactual is the feasible arrangement that would operate without this specific intervention, subject to the same mandates and conditions.

The baseline must include already approved changes and efficiencies embedded in the relevant budget. Do not restore an obsolete, more expensive structure merely to enlarge apparent benefit. Where testing realization of an existing reform, reconstruct its original supported counterfactual in a separate baseline-measure ledger; label the result as verification of that reform rather than a new project saving.

A purchase-avoidance counterfactual requires evidence of a continuing requirement and credible procurement path, such as an approved requisition, plan, contract option, or other documented commitment. A canceled purchase that became unnecessary because the mandate ended is not an efficiency benefit. A staffing counterfactual must include vacancies, redeployments, overtime, contractors, and receiving-team work; approved post abolition alone does not prove cash release.

Predeclare sensitivity cases for uncertain demand, utilization, transition duration, unit prices, and remaining liabilities. Record residual limitations. When no valid comparator exists, use a narrower descriptive or control finding and specify what remains untested.

## 5. Calculate full system cost

For an aligned period and an unchanged required service:

```text
Net incremental cost reduction
  = total external UN cost under the feasible baseline
  - total external UN cost under the intervention

Intervention cost includes, once each:
  retained source-unit cost
  + receiving/provider external cost
  + transition and implementation cost
  + continuing operations, compliance, and monitoring cost
  + residual contractual/personnel/closure liabilities attributable to the change
```

Include comparable baseline liabilities on the baseline side. Use nonoverlapping cost components; if a provider's full-cost figure already includes payroll, overhead, or transition expense, do not add those components again. All necessary affected entities belong in both scenarios, including costs that remain unchanged. Allocation of an accounting cost is not proof that it can be removed.

Eliminate internal charges from both consolidated scenarios. Do not subtract an eliminated client charge again after external provider cost is included: that would double-deduct a transfer. Do not assume a transfer is economically free; receiving-unit external cost and residual source cost still count.

Use matched cash-flow schedules for a cashable finding and a consistent resource/accrual view for broader cost-effectiveness analysis. Identify timing differences between obligation, expense, payment, and budget release. Keep the two views separate and reconcile them; depreciation or an asset book-value reduction does not itself release cash.

Report one-time net effect, recurring steady-state annual effect, cumulative effect through a stated date, and any discounted longer-term estimate separately. State discount rate, horizon, price basis, and treatment of terminal liabilities if discounting is used. Never annualize a short transition period without evidence of a sustainable service model.

## 6. Classify financial and operational effects

| Effect | Recognition rule |
| --- | --- |
| Capacity gain | Measured resource availability or throughput improves with preserved outputs; report hours, service units, or capacity. Salary multiplied by released hours is not cash release. |
| Recovery | Record entitlement, assessed claim, collectible balance, settlement, and received cash/credit separately; report collection/legal cost and gross/net values. An internal provider recovery is eliminated from the system total. |
| Cost avoidance | A supported future requirement is met without an otherwise credible expenditure, net of added cost; report separately from reductions in existing cost. |
| Cashable saving | At least `FINANCIALLY_VALIDATED`: unique removable cost objects, feasible full-cost counterfactual, preserved outputs, executable release, timing, and evidence of incrementality. |
| Realized saving | Financial validation plus implemented reduction and observed financial effect over the required window; reconcile migration of cost and verify operational guardrails. |
| Control improvement | A verified improvement in control design or operation; no monetary amount without separate evidence of a financial effect. |

No monetary finding may be called **savings** before `FINANCIALLY_VALIDATED`. An early scenario may contain assumed cost differences for design testing, but must be labeled a hypothetical scenario rather than a savings finding or portfolio opportunity value. Passing transaction matching or structural CI does not satisfy the financial gate. Financial validation establishes an evidenced opportunity; realization requires implementation and observation.

The headline savings ledger contains realized savings only. Publish validated opportunities, avoidance, recoveries, capacity gains, and control improvements in separate ledgers. Recognition of previously embedded measures and attribution of new project effects must also remain separate.

## 7. Apply the known repository boundary examples

These examples reproduce the classifications in existing research; they are not a new review of underlying UN sources or implementation:

- **DPO:** the $95.4641 million support-account allocation appears in two budget presentations. It is one financing amount, not two additive budgets. See the [allocation audit](mission_budget_and_un80_audit.md).
- **RSCE:** the proposed $3.2591 million calendar-2027 SPM share, $3.4432 million mixed-client provision, and $45.9116 million FY2026/27 RSCE total have different populations or periods. They cannot be subtracted to infer overbilling. Obtain the eligible service-line allocation denominator and matched charges first.
- **UNIFIL–UNSCOL:** the $438,100 proposed benefit combines $394,000 vehicles, $36,900 ICT, and $7,200 rations. The components and total describe the same planned effect. Verify receipts, avoided procurement, and full transfer cost before reporting realization; do not add it as a newly generated project opportunity.
- **BINUH–UNSOH:** the $1.4 million proposed aviation change and $4 million broader support reimbursement cover different services. Do not net them mechanically. Reconcile internal charges, actual external aviation cost, client residual cost, and service performance.

The last three cases and their evidence gaps are documented in the [transaction-level assessment](transaction_level_validation.md).

## 8. Required financial finding receipt

Every proposed financial finding must state:

1. Intervention/version, candidate state, benefit class, evidence cutoff, and reviewer.
2. Entity, fund, period, currency/unit, financial status, and economic boundary.
3. Unique cost objects, source anchors, and safe references to restricted evidence.
4. Frozen baseline, feasible alternative, adjustment rules, and counterfactual limitations.
5. Reproducible gross-to-net calculation, transfer elimination, liabilities, sensitivity, and timing.
6. Benefit-pool/nonadditivity IDs, scenario selection, shared-cost allocation, and baseline attribution.
7. Operational guardrail results, authority path, release mechanism, and realization evidence where claimed.
8. Missing evidence, excluded amounts, unresolved exceptions, and permitted conclusion.

If a required item is missing, retain the gap explicitly and withhold the unsupported financial classification. Preserve adverse, zero, negative, and insufficient-evidence findings as well as favorable results.
