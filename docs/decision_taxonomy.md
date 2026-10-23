# Decision taxonomy

**F02 foundation standard | Version 1.0 | 22 October 2026**

These are project definitions for assessing UN Peace Operations. They establish how subsequent case findings are described; they do not create findings about existing missions, change historical classifications, or establish UN legal or accounting authority. Apply them with the [candidate advancement standard](candidate_advancement.md), [cost-accounting standard](cost_accounting_standard.md), and [operational guardrails](guardrail_standard.md).

## Classification and maturity

A finding has separate fields for its mechanism (such as duplication), effect (such as capacity released), financial treatment, and evidentiary maturity. A duplicated activity can produce a capacity gain without releasing expenditure. A recovery can correct an overpayment without demonstrating an efficiency improvement.

**No monetary finding may be called savings before `FINANCIALLY_VALIDATED`.** Before that gate, quantified scenarios are explicitly assumption-based estimates of potential cost change, with unsupported inputs and uncertainty shown. They are not findings, cashable savings, or portfolio benefits. Passing a software check does not pass a substantive evidence gate.

`FINANCIALLY_VALIDATED` supports a validated cashable-saving opportunity. Only observed implementation and financial results meeting the realization gate support a realized-saving claim. Later operational states must retain the financial-validation receipt for a savings claim; a capacity-only case may advance operationally without one.

The accounting classification is independent of the lifecycle state. Record a monetary effect as one of `CASHABLE_SAVING`, `COST_AVOIDANCE`, `RECOVERY`, or `NET_COST_INCREASE`; use `CAPACITY_GAIN`, `CONTROL_IMPROVEMENT`, or `NO_FINANCIAL_CLAIM` where applicable. Add maturity, period, realization evidence, recurring/one-time treatment, and nonadditivity group separately. `NOT_ESTIMATED`, a measured zero, and `NOT_APPLICABLE` have different meanings.

## Waste

**Definition:** Resources consumed without a necessary operational, legal, safety, or mandate-related benefit, or consumed after that benefit ceased to be required, where the consumption was reasonably preventable under the conditions and information available at the time.

**Minimum evidence:** Identify the actual resource use or expenditure, what was received, the requirement and decision context, the benefit or lack of benefit, and a feasible prevention mechanism. Quantification requires a specific cost object and treatment of termination, remediation, replacement, and transferred costs. State the tested scope and period.

**Falsifiers and limits:** Necessary contingency reserve, mandated separation of duties, reasonable surge capacity, legal obligations, or a defensible decision based on information available at the time can explain apparent waste. Low utilization, a failed initiative, a large budget, or unmeasured benefit alone is insufficient. Waste is not automatically fraud, misconduct, or a recoverable loss.

**Illustrative test:** Payment for an unused license that could have been canceled without impairing service may establish preventable waste. A standby medical asset retained for a required response capability may be necessary despite low routine utilization. Neither example is a finding about a repository case.

## Inefficiency

**Definition:** An operating arrangement uses more total resources than a feasible alternative for equivalent or better required outputs, after accounting for quality, timeliness, readiness, risk, transition cost, and work transferred elsewhere.

**Minimum evidence:** Compare the same service, population, period, demand, and performance requirements; measure the current arrangement and a feasible alternative; include retained and provider-side resources and transition costs. Explain material differences in mandate, security, geography, scale, vacancy, or lifecycle stage.

**Falsifiers and limits:** An alternative that lowers cost by reducing required output or readiness does not establish efficiency. A nominally cheaper arrangement can be infeasible or more costly when transition and receiving-unit work are included. Evidence of inefficiency does not by itself establish cash release or unnecessary activity.

**Illustrative test:** Central processing may reduce rework at equal service quality after receiving-center costs are included. Faster processing with unresolved errors or a larger downstream backlog does not meet the test.

## Duplication

**Definition:** Two or more separately resourced activities produce the same or operationally substitutable output for the same need, beneficiary, period, and decision purpose, and at least one activity can be removed or combined without impairing mandates, independent judgment, controls, readiness, or service quality.

**Minimum evidence:** Establish actual activities and resourcing; compare output, scope, audience, timing, purpose, mandate, workflow, and ownership; test substitutability with responsible programme personnel; identify the activity that could disappear and all remaining work.

**Falsifiers and limits:** Distinct legal products, necessary independent assessments, deliberate lead-support arrangements, surge or continuity redundancy, specialist audiences, and different service periods can justify apparent overlap. Similar titles, shared facts, a common policy area, cooperation, and cross-references alone do not establish duplication. A duplicate payment is a transaction-control exception with its own identity and settlement test; it need not involve duplicate production.

**Illustrative test:** Two separately commissioned identical services for the same users and period may be duplicative. Two mandated reports using the same source event may still need separate analysis, recipients, and approvals.

## Capacity gain

**Definition:** A measured increase in usable staff time, asset availability, processing capacity, or service throughput attributable to an intervention while required performance and operational guardrails are maintained. Capacity may be released or used to deliver more required output with the same resources.

**Minimum evidence:** Measure comparable tasks, demand, utilization, and outputs before and after the change or against a credible comparator. Show the named burden removed or throughput gained; count failed work, rework, receiving-unit effort, residual parallel processes, setup, and evaluation effort. Record whether capacity is merely available or demonstrably redeployed, and to what purpose.

**Falsifiers and limits:** Faster software execution is not staff time released. Time shifted to another team, hidden overtime, reduced service scope, and an unremoved normal task defeat a claimed release. A parallel shadow can test performance but does not prove displacement. Do not multiply released hours by salary rates and label the result cash savings. An FTE-equivalent is a workload unit, not a post abolished or expenditure released.

**Illustrative test:** Removing a verified recurring reconciliation step may release staff hours for backlog reduction. If salaries and contracts remain unchanged, report the measured capacity effect and redeployment separately from financial benefits.

## Recovery

**Definition:** Cash, an enforceable credit, an asset, or another economic resource returned following an overpayment, loss, nonperformance, settlement, penalty, or correction of an improper charge. Distinguish asserted claim, recognized receivable, agreed settlement, and actual receipt.

**Minimum evidence:** Link the original transaction or loss to the legal/accounting basis, claim, determination or settlement, collection costs, and receipt or applied credit. For assets, verify identity, custody, condition, and valuation. Report gross recovery and collection/legal costs separately and show the net result.

**Falsifiers and limits:** A claim submitted or receivable recorded is not cash recovered. A credit not yet applied is distinct from a reduction in payment. Internal payer-provider cost recovery is an allocation/transfer, not a whole-UN recovery benefit. Historical questioned amounts are not automatically collectible. Recovery does not demonstrate recurrence prevention or recurring efficiency.

**Illustrative test:** A settled contractor claim supported by a posted cash receipt is a realized recovery. A published request for progress on a claim supports follow-up, not a quantified receipt.

## Cost avoidance

**Definition:** A credible future expenditure that would otherwise have occurred is prevented or reduced before it is incurred, while equivalent required capability is preserved. In this portfolio, the avoided amount is reported separately from release of an existing expenditure commitment or funded operating cost.

**Minimum evidence:** Establish a continuing requirement and credible purchase, hiring, renewal, or demand plan; demonstrate that the future expenditure would occur without the intervention; identify the canceled or reduced requirement and intervention mechanism; include transfer, repair, adaptation, installation, replacement, support, and transition costs. A budget request or ceiling alone does not prove the purchase would happen.

**Falsifiers and limits:** A purchase no longer required because a mandate ended is a change in need, not intervention-attributable avoidance. Deferred expenditure is not permanently avoided; record timing and later liabilities. A canceled purchase that creates a service gap fails the guardrails. If an already funded cost is released, apply the cashable-saving definition and prevent the same benefit from also entering cost-avoidance totals.

**Illustrative test:** Receipt of a usable transferred vehicle may avoid an otherwise necessary planned purchase, net of all transfer and support costs. The existing UNIFIL-UNSCOL proposal estimate is baseline material until actual receipt, avoided purchase, costs, and incremental attribution are established.

## Cashable saving

**Definition:** An evidence-supported net reduction in an existing funded or demonstrably unavoidable expenditure that can be released from a specified contract, post, purchase, budget provision, or other cost object while preserving required performance and avoiding cost migration. Financial validation establishes the opportunity; actual realization is assessed separately.

**Minimum evidence:** A named cost object, credible same-scope counterfactual, operational validation, lawful cancellation or release route, budget-owner confirmation, timing, and complete baseline and intervention costs. Include receiving-unit and external-provider costs, retained local work, transition and monitoring costs, stranded commitments, and residual personnel/contract liabilities. Establish that the reduction is incremental to approved and prebooked measures.

**Falsifiers and limits:** An unused appropriation, a request reduced before approval, a vacant post, transferred payroll, budget underspending, and hours multiplied by salary do not by themselves prove cashable savings. A reduction financed by shifting costs to another UN entity is not a consolidated saving. A negative net effect must be recorded as a cost increase, not hidden in a positive gross figure.

**Illustrative test:** Canceling a duplicative external contract can support a validated saving once cancellation rights, residual liabilities, alternative service costs, and protected outputs are established. Until financial validation, it remains a cost-change scenario.

## Realized saving

**Definition:** A financially validated cashable saving that has been authorized, implemented, and observed in reconciled financial records during a defined measurement period, with transferred and continuing costs included and all applicable operational safeguards satisfied.

**Minimum evidence:** Retain the financial-validation receipt; verify approval and implemented cancellation, reduction, or release; reconcile actual expenditure and liabilities to the frozen counterfactual; measure costs across affected entities; complete the predeclared observation period; verify service outcomes and owner acceptance. Material claims require substantive review distinct from the calculation's author, with reviewer role and independence limitations recorded.

**Falsifiers and limits:** Approval, a budget amendment, a proposal estimate, or an unspent balance alone is not realization. Unrelated exchange-rate, vacancy, demand, closure, mandate, price, or timing changes must be isolated. A cost that reappears elsewhere or deferred liability reduces or reverses the result. A short observation window cannot support an unqualified full-year recurring amount.

**Illustrative test:** Reconciled payments fall following a verified contract cancellation, after alternative service and termination costs, while measured performance remains within limits. Only the observed eligible period enters realized totals; future-year extrapolations remain forecasts.

## Calculation and consolidation rules

For an equivalent service and aligned scope/period, calculate:

```text
Net incremental cost change available for validation
  = consolidated baseline external expenditure
  - consolidated intervention external expenditure
```

Each side includes all relevant staff, external supplier, retained, receiving/provider, transition, termination, residual, compliance, and monitoring costs incurred in that scenario. Apply one-time costs to the chosen horizon and disclose recurring steady-state effects separately. Use the [cost-accounting standard](cost_accounting_standard.md) for uncertainty, timing, allocation, and full resource-cost treatment.

Eliminate matched internal payer/provider charges within the same consolidation perimeter before comparing scenarios. Include the provider's underlying external costs once. Do not deduct an internal transfer again as if it were a new external cost, and do not subtract receiving costs twice when already included in consolidated intervention expenditure. Where only one entity is measured, label the result entity-level and withhold a whole-UN claim.

Record noncash resource effects, such as hours or asset availability, alongside external expenditure; do not convert them into expenditure release without a specific cash mechanism. Unobserved or missing material costs make the net result `NOT_ESTIMATED` or a bounded scenario, not zero.

## Mutually exclusive benefit accounting

One economic effect receives one primary financial category, one benefit ID, one period, and one nonadditivity group. Parent investigations, child cases, and enabling changes cannot claim the same effect independently. If one intervention produces distinct cash, capacity, recovery, or avoidance effects, create linked rows with nonoverlapping objects and periods.

Validated cashable opportunities and realized savings are different maturity views of the same benefit and must not be summed. A forecast total and its realized portion must not both enter a portfolio total. A recovery that returns a previously paid amount cannot also enter savings as a second receipt. Released capacity used to achieve a saving cannot be monetized again as an additive benefit.

Maintain separate ledgers for validated cashable opportunities, realized recurring savings, realized one-time savings, cost avoidance (forecast/observed separately), recoveries (claimed/received separately), capacity gains (available/redeployed separately), and control improvements. The headline realized-savings total includes only eligible realized savings, with recurring and one-time components shown. Other benefit categories are presented separately.

Closures, approved abolishments, prebooked efficiencies, and existing shared structures belong in the baseline. Attribute only an additional effect established against that baseline. Whole mission and departmental budgets are financial boundaries, never automatically avoidable-cost pools.

## Finding receipt

Every finding records its intervention/version, definition used, exact tested scope, evidence cutoff, sources and source status, counterfactual, alternative explanations tested, costs and resource units, uncertainty, financial category, lifecycle state, financial-validation reference where applicable, guardrail result, nonadditivity group, reviewer, and limitations. Preserve adverse, null, retained-current-process, and insufficient-evidence results. Correct a finding by appending a superseding version with a reason rather than rewriting the original evidence.

The terms above are prospective project standards. Existing historical source and research outputs retain their original evidence dates and meanings; applying this taxonomy does not reclassify them automatically.
