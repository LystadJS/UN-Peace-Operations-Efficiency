# F03 — Candidate advancement and evidence thresholds

This prospective standard defines evidentiary maturity for a bounded intervention. It does not reclassify historical candidates or activate any live work. [V13](v13_reference_adoption.md) remains a research-reference adoption; its live-use restrictions and the paused course watch remain in force.

Use exactly one current state per intervention version. Keep financial benefit classification separate. **No monetary finding may be called savings before FINANCIALLY_VALIDATED.** An intervention that bypasses that financial gate for a capacity or control improvement cannot acquire a savings claim merely by reaching IMPLEMENTATION_READY or REALIZED.

## States and entry evidence

| State | Entry evidence and permitted conclusion |
| --- | --- |
| `SCREENING_CANDIDATE` | A specific hypothesis and anchored source identify a bounded concern. This supports investigation only. |
| `VALIDATION_READY` | Define the exact intervention, proposed owner role and evidence custodian, mandate/cost perimeter, minimum evidence request, counterfactual design, prospective guardrails, and nonadditivity group. A proposed owner role is not institutional acceptance. |
| `OPERATIONALLY_VALIDATED` | Actual service/workflow evidence establishes a comparable baseline and feasible alternative, accounts for transferred work, and passes applicable operational guardrails. Documentary similarity and software success do not satisfy this gate. |
| `FINANCIALLY_VALIDATED` | Unique cost objects, a same-scope counterfactual, cancelable or released costs, full system net costs, incremental attribution, timing, uncertainty, and financial-review receipt support a financial conclusion. All operational gates must already have passed. |
| `IMPLEMENTATION_READY` | The accepted accountable owner and all required authorities approve the precise scope, frozen baseline, implementation/monitoring plan, and stop/rollback rules. Preparation of a dossier does not grant authority. |
| `REALIZATION_IN_PROGRESS` | The authorized change has started; benefit/guardrail monitoring and capture of deviations and transferred costs are active. Forecast benefits remain forecasts. |
| `REALIZED` | The predeclared observation period is complete; benefits are observed; cost migration is reconciled; continuing guardrails pass; owner acceptance and independent review are recorded. The benefit may be capacity, recovery, avoidance, or savings, with separate accounting. |
| `RETAIN_CURRENT_PROCESS` | Source-linked evaluation supports retaining the arrangement within an explicit tested scope. This is a substantive decision, not an inference from missing evidence. |
| `CLOSED_INSUFFICIENT_EVIDENCE` | The record identifies missing evidence, affected claims, collection attempts/burden, closure rationale, and reopening rule. This does not establish efficiency, waste, compliance, or successful operational adjudication. |

## Transition rules

The ordinary chain is screening → validation ready → operational validation → financial validation → implementation ready → realization in progress → realized. Operationally validated capacity/control cases may proceed directly to implementation ready. An insufficiency closure or retention decision may end screening, validation-ready, or operationally validated work. A financially validated proposal may be retained rather than implemented. Implementation-ready or in-progress work may terminate in retention; in-progress work may return to implementation ready for a documented revision.

`REALIZED`, `RETAIN_CURRENT_PROCESS`, and `CLOSED_INSUFFICIENT_EVIDENCE` are terminal for that intervention version. Reopening or revising a terminal finding requires a successor version preserving the old record. No gates are skipped: preexisting evidence may be entered as successive reviewed events, each with its own checklist and receipt. A new material risk or evidence defect blocks further advancement and requires a recorded issue/hold; adding a hold does not falsely promote or rewrite historical maturity.

Record each event with state, timestamp/timezone, evidence cutoff, actor, rationale, validator version, mandatory checks, and source/decision receipts. Corrections append a successor record; preserve prior events. Dates and receipts describe what was actually reviewed. The validator checks declared references and gate order; it cannot authenticate receipt content, legal interpretation, owner authority, or substantive savings.

## Machine-readable contract

The controlling dictionary is [candidate_states.json](../data/standards/candidate_states.json). It defines all nine states, legal successors, mandatory checks, claim classes, and required record fields. `requires` contains checks that must be literally `true`, each linked to one or more nonempty evidence receipt identifiers. Unknown, pending, unavailable, and null evidence cannot pass a gate. Document inapplicable details inside a reviewed receipt explaining applicability; do not waive an entire mandatory gate with an N/A marker.

An optional records file is a JSON object with `schema_version: 1` and a `candidates` list. Each candidate has:

- `candidate_id` and `version`: nonempty strings, unique together.
- `current_state`: one of the nine states, matching the last event.
- `claim_class`: `NOT_ASSESSED`, `NO_FINANCIAL_CLAIM`, `CAPACITY_GAIN`, `CONTROL_IMPROVEMENT`, `RECOVERY`, `COST_AVOIDANCE`, `CASHABLE_SAVING`, `REALIZED_SAVING`, or `NET_COST_INCREASE`.
- `savings_amount`, `currency`, `period`: null for every non-savings class. Savings require a positive finite amount, three-letter uppercase currency, and explicit measurement period. Amounts are in currency units, not thousands. A zero or adverse financial outcome belongs under a non-savings class, with its detailed financial assessment stored in the linked evidence record.
- `history`: nonempty chronological event list starting at screening. Every event contains `state`, timezone-qualified ISO `recorded_at`, ISO date `evidence_cutoff`, `actor`, `rationale`, `validator_version: "1.0"`, `checks`, and `evidence_receipts`.

For every check named by the event state's `requires`, put `true` in `checks` and a list of safe local evidence receipt references or identifiers in `evidence_receipts`. Real restricted evidence stays in approved storage; a safe receipt identifies the reviewer, scope, result and controlled locator. Synthetic examples in the tests have no operational authority.

Both savings classes require an actual FINANCIALLY_VALIDATED event in the same version's history. `REALIZED_SAVING` additionally requires current state REALIZED. A terminal retention/insufficiency record cannot carry an active savings claim. Keep recovery, avoidance, capacity, and control results outside the savings fields and outside the headline realized-savings total. [Decision taxonomy](decision_taxonomy.md), [cost accounting](cost_accounting_standard.md), and [guardrails](guardrail_standard.md) govern substantive review.

## Validation and limitations

Run from the repository root:

```sh
python3 scripts/validate_candidate_advancement.py
python3 tests/check_candidate_advancement.py
python3 scripts/validate_candidate_advancement.py --records /approved/path/candidates.json
python3 scripts/validate_candidate_advancement.py --records /approved/path/current.json --previous /approved/path/prior.json
```

The default invocation validates only the dictionary and supplies no operational candidate findings. `--records` validates supplied new-format records, not legacy census or ranking tables. `--previous` additionally requires every prior candidate/version to remain present and its history to be an unchanged prefix. Without a trusted prior snapshot, append-only preservation cannot be established. Safe receipt identifiers are references, not proof that a reviewer authenticated their contents. Independent source, financial, institutional, and operational review remains necessary before any substantive gate is approved.
