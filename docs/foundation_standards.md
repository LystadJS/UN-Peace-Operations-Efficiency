# Foundation standards: F01–F06

These standards define the prospective decision framework for the UN Peace Operations Efficiency portfolio. They implement the user's F01–F06 task scope and nine candidate states. They are project research standards; they do not establish UN adoption, institutional approval, operational implementation, or a savings finding.

| ID | Standard | Result |
| --- | --- | --- |
| F01 | [Desired end state](desired_end_state.md) | Portfolio capabilities, measurable completion gates, and scope rules |
| F02 | [Decision taxonomy](decision_taxonomy.md) | Definitions and evidence requirements for the eight controlled terms |
| F03 | [Candidate advancement](candidate_advancement.md) | State dictionary, transition rules, evidence gates, and record validation |
| F04 | [Source authority](source_authority_standard.md) | Claim-specific treatment of normative authority and factual evidence |
| F05 | [Cost accounting](cost_accounting_standard.md) | Financial perimeters, nonadditivity, and counterfactual rules |
| F06 | [Guardrails](guardrail_standard.md) | Mandate, safety, readiness, quality, timeliness, and transition safeguards |

## Use and precedence

Use these standards together for new portfolio work. The candidate-state dictionary controls the allowed state vocabulary and machine-checkable gates. The other standards explain what substantive evidence is required. A successful validator checks record structure and declared evidence; it cannot authenticate evidence, decide legal meaning, or certify the substantive truth of a claim.

Historical classifications and releases retain their original meaning. This framework does not silently migrate legacy rows, alter rankings, reopen paused activity, or replace the [current research-reference pointer](../data/current_research_reference.json), whose authority is limited to the fixed V8/V9 research obligations. Record an explicit mapping before using these states in a legacy dataset.

**No monetary finding may be called savings before `FINANCIALLY_VALIDATED`.** A modelled scenario remains a scenario. Forecast, financially validated, and realized amounts must be displayed separately. A case that follows the capacity-only path to implementation or realization does not thereby qualify for a savings claim.

## Verification

From the repository root:

```sh
python scripts/validate_candidate_advancement.py
python tests/check_candidate_advancement.py
```

The [candidate advancement standard](candidate_advancement.md) specifies the optional candidate-record input and the limits of validation. No actual operational case is promoted by installing or running this framework.
