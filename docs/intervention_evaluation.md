# Intervention evaluation design — P08–P14

These prospective research tools define what a bounded case needs before comparison and prioritization. They supply no institutional approval, candidate advancement or monetary finding. The repository's candidate states and financial/operational standards remain controlling. An empty template is deliberately unscorable.

| Task | Principal result | Use |
| --- | --- | --- |
| P08 | [Case dossier template](../data/portfolio/case_dossier_template.json) | Record hypothesis, authority, owners, evidence, counterfactual, safeguards and decision without inventing missing values. |
| P09 | [Operational metric catalog](../data/portfolio/operational_metrics.json) | Define outcome, exposure, workload and guardrail measurements at their actual operational grain. |
| P10 | [Comparability rules](../data/portfolio/comparability_rules.json) | Align population, service, period, status, prices and units before subtraction. |
| P11 | [Full-system cost model](../data/portfolio/cost_model.json) | Retain receiving, residual, transition, compliance and source costs; eliminate matched internal transfers once. |
| P12 | [Counterfactual ladder](../data/portfolio/counterfactual_ladder.json) | Select a feasible authorized design and state what it cannot establish. |
| P13 | [Prioritization model](../data/portfolio/prioritization_model.json) | Evaluate declared evidence-collection preferences after safeguard screening. |
| P14 | [Sensitivity design](../data/portfolio/prioritization_sensitivity.json) | Expose preference-dependent rankings and unresolved inputs. |

## Cost comparison

[The evaluator](../scripts/evaluate_intervention.py) compares `baseline` with `intervention_scenario`; the dossier's `intervention` field is the prose definition. Each scenario carries the same explicit financial/service frame and affected entity set. Financial amounts are finite decimal strings in currency units. The evaluator uses Decimal arithmetic, rejects floats and non-finite values, and retains adverse and zero results. A missing amount blocks the comparison; it is never imputed as zero. Explicit zero costs still require evidence references.

The counterfactual must declare a frozen feasible baseline, confounder review and inclusion of already embedded or approved measures, with receipts. Full-system coverage requires an affirmative scope declaration and no omitted components. Each affected entity needs an external-cost row, including an evidenced zero if appropriate. These declarations make the calculation inspectable; they cannot establish factual completeness by themselves.

Cost rows identify distinct economic components. Parent totals and included children cannot both enter the same calculation. Internal payer charges are positive and provider recoveries negative. Each matched pair must have the same transfer identity, two distinct counterpart entities and equal-and-opposite entries. Both are eliminated; external provider spending remains. An unmatched transfer blocks the consolidated comparison. The model does not multiply annual totals, annualize transitions, discount uncertain horizons or reconcile cash with accrual automatically.

`net_cost_difference` means baseline external cost minus intervention external cost in the aligned frame. It is a hypothetical scenario for synthetic data and an unvalidated declared comparison otherwise. It is never labeled savings. Even a favorable difference does not establish a removable expenditure, cash release, causal attribution, additionality, institutional permission or realization.

Capacity, recovery, avoidance and control effects remain separate observations with separate objects, components, units, periods and benefit pools. The evaluator rejects duplicate economic components across those classes and withholds their aggregate. It does not accept savings benefit classes. Portfolio-wide overlap and shared-cost allocation still need separate reconciliation.

## Safeguards and prioritization

All eight guardrail dimensions must have declared support. `PASS` needs evidence, a prospective threshold receipt and an owner-approval receipt. Inapplicability needs a scoped justification and accepted review. A failed critical safeguard produces `BLOCKED`; missing support or `UNKNOWN` produces `UNSCORABLE`. A favorable financial difference cannot override either result. Receipt references are not authentication of their contents.

There are no approved empirical weights or universal operational thresholds in these files. A declared triage score requires every criterion, a case-specific rubric receipt, a decimal value from zero through one, and an explicitly reviewed weight vector summing exactly to one. Missing values are not replaced with midpoint scores. The score prioritizes research attention only; financial exposure and unvalidated opportunity amounts are not scoring criteria.

The sensitivity function accepts an envelope containing `cases`, `vectors` and an `illustrative` flag. Each vector has an `id` and complete `weights`. A nonillustrative vector also requires its review `receipt`. Illustrative results are explicitly labeled design stress tests, with no assertion of institutional approval. Outputs preserve ties, null ranks for blocked/unscorable cases, each case's best/worst rank, and pairwise reversals across vectors. Preference stability does not establish an intervention's truth or merit.

## Run and validation

```sh
python scripts/evaluate_intervention.py --input data/portfolio/case_dossier_template.json
python scripts/evaluate_intervention.py --input /approved/path/case.json --output /approved/path/scenario-receipt.json
python scripts/evaluate_intervention.py --sensitivity --input /approved/path/preference-design.json
python tests/check_intervention_evaluation.py
```

Keep restricted evidence and outputs in approved storage. Public repository inputs should contain only safe receipts or explicitly synthetic examples. The synthetic tests cover transfers, adverse and zero effects, missing receiving cost, unequal frames, unknown amounts, embedded baselines, duplicated components, safeguards, missing scoring inputs and preference reversals. They verify model behavior, not UN operations.
