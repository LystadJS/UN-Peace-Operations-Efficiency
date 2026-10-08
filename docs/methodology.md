# Methodology and release contract

## Purpose and scope

The unit of analysis is a **function** (what a unit is tasked to do), not a phrase, organizational title, or general policy objective. The source corpus consists of the *full* submitted 2027 proposed budget documents A/81/6 (Sect. 3) and A/81/6 (Sect. 5). The first release deliberately includes adjacent offices and field operations when they provide traceable comparisons, and makes no claim of system-wide UN peacekeeping coverage.

## Evidence hierarchy

1. **Direct documentation** — a numbered paragraph, annex, or explicitly labeled deliverables table.
2. **Source-grounded inference** — two directly cited functions appear related but no identity of personnel, outputs or budgets has been shown.
3. **Operationally verified overlap** — requires identical or substitutable activity, same relevant scope and audience, concurrent resourcing, no necessary functional separation, and review by responsible programme personnel. **No such determination is made in this baseline.**
4. **Verified savings opportunity** — requires a funded and legally executable counterfactual, full implementation and recurring costs, lost capabilities assessed, and one-time costs specified. **No such determination is made in this baseline.**

### Crosswalk classes

- `documented_shared_structure`: proposal explicitly identifies one shared unit; do not imply it has been fully implemented or savings realized.
- `documented_joint_process`: sources explicitly identify a joint plan, agreement or implementation procedure.
- `planned_coordination`: planned or described closer links, not a merger.
- `candidate_overlap`: source-grounded similarity with unverified redundancy.
- `complementary_different_roles`: different instruments support a shared objective.
- `distinct_mandates`: clearly separate legal or operational outputs.

The class is *evidentiary*, not a rating of desirability. `direct_documentation` in the crosswalk means the cited source supports the stated organization or responsibility; it is never a substitute for workplace verification. Field activities may complement one another even if they use the same partners or territory.

### UN80 rules

- Reforms must have explicit documentary evidence before they are labelled `explicit_un80_consolidation`.
- Organigram changes, existing shared services and other proposed 2027 restructurings are recorded separately.
- Repeated rows under one reform ID represent **facets of one reform**, not new distinct consolidation opportunities.
- Changes already approved or reflected in prior budgets form the starting counterfactual and must **not** be counted as incremental savings.
- For each reform retain a status that distinguishes proposal wording, implementation, funding and outcome. The current implementation field remains unverified.

## Candidate screening and decision gate

Each candidate must specify:
1. Which `CW...` row(s) motivate the test?
2. What actual products, audience, providers, location and fiscal year are being compared?
3. Is the same work separately resourced or is there a deliberate lead–support arrangement?
4. What legal authority controls each product or appropriation?
5. What work, risk and transition cost would remain if reorganized?
6. Who validates the interpretation and who could authorize the change?

Candidate priority is a **qualitative ordering of research utility**, not a financial potential or severity classification. Negative controls remain in the evidence set to measure false-positive overlap risk.

## Financial methodology (not yet executed)

Do not add `2027 regular`, `other assessed`, `extragbudgetary` or separate mission budgets without verifying perimeters and removing transfers. Distinguish *appropriation*, *expenditure*, *obligation*, *post-funded salaries*, *grants*, and *non-post expenditure*. Sunk changes and already-booked UN80 efficiencies are not new savings.

For an option, estimate separately:
- Gross addressable **recurring** cost directly attached to redundant activities.
- Residual cost of performing necessary tasks after redesign, including contracts, training, field support and compliance.
- Transition and one-time implementation costs.
- Net incremental recurring savings relative to a documented no-change scenario.
- Capability and outcome risks with mitigations, and pessimistic/base/optimistic assumptions.

Until cost ledger and operating evidence are received, savings are **not estimated** (not zero). The 2027 department and subprogramme budgets are financial boundary data, not cost attribution by overlap.

## Traceability model

`source_manifest` → `functional_inventory` and `deliverable_inventory` and `mandate_inventory` → `crosswalk` → `candidate_validation`.

The `evidence_links.csv` materialises one official document URL, page and text anchor per cited item. Page numbers are PDF page indices, 1-based, in the **uploaded full** documents (same as displayed PDF page counters). Section 5 official symbol resolver may prohibit automated access; the document should be searched by its exact symbol at the UN Fifth Committee index if necessary. A URL response is not proof of the underlying analysis.

## Quality controls

`scripts/validate_crosswalk.py` (zero external dependencies) and `scripts/validate_crosswalk.R` (base R) verify:

- All expected CSV files load and have unique, nonempty primary IDs.
- Source IDs, crosswalk function IDs, linked deliverable IDs, candidate IDs and reform IDs exist.
- DPPA/DPO sides are not accidentally reversed and PDF page references are within source bounds.
- Relationship classes and preliminary statuses use controlled vocabulary.
- Every crosswalk row has one DPPA and one DPO evidence pointer.
- All recorded quantitative deliverables have 2025 actual and 2027 planned values; missing estimates are never imputed as zero.
- Candidate savings remain `not_estimated` or `not_applicable`.
- The source-quality issues remain explicit and unresolved where applicable.

These are **structural checks**, not source-text adjudication or legal review. Readers must still inspect citations and mission-level evidence.
