# V8 shared-production assessment
## UNOWAS–UNOCA: one evidence register, separate mandated products

**Assessment date: 15 October 2026 · Worked cycle: January–June 2025 · Public-source reconstruction, not a live operational trial**

## Decision

**Advance a lightweight shared-evidence pilot, not a merger of reporting or a staffing reduction.** The worked example shows how source-qualified facts can support two Secretary-General reports and two office briefings while preserving their different coverage, judgments, dates and approvals. It does not show that the offices currently collect or draft the same material twice. The recommended next operational gate is to compare this design with their existing arrangements before adding any process.

This is one joint implementation test attached to **C09 regional partnerships** and **C02 political reporting**. **C05 knowledge management** is an enabling function, not another additive saving. The existing 14-case ranking is preserved in the [consolidation overlay](../data/census_v8/consolidation_overlay.csv); no mandate, position, appropriation or financial gate is changed. [Updated consolidation brief](v8_consolidation_brief.md).

## 1. What is already shared—and therefore belongs in the baseline

Joint activity is not merely proposed. The public notice published on **1 February 2025** records a joint UNOWAS–UNOCA mission to northern Nigeria and participation in the Lake Chad Basin Governors’ Forum. The **28 February** notice records their jointly organized Dakar workshop, more than thirty participants and adoption of a workplan. The UNOWAS and UNOCA reports subsequently describe those activities; UNOCA expressly refers readers to the UNOWAS report. The UNOCA report also records an **8 April** exchange agreeing joint regional activities. These are existing cooperation, not work V8 can newly claim to eliminate. [Joint mission notice](https://unowas.unmissions.org/en/news/unoca-and-unowas-renew-their-joint-commitment-to-support-stabilization-and), [workshop notice](https://unowas.unmissions.org/en/news/west-and-central-africa-unowas-and-unoca-pool-their-efforts-to-strengthen-peaceful), [S/2025/342, paragraphs 61–67](https://docs.un.org/en/S/2025/342).

The reporting relationship is explicit, but limited. The **3 April UNOWAS briefer** presents S/2025/187. The **9 June UNOCA briefer** refers directly to S/PV.9890 when attributing the Niger withdrawal announcement. A citation demonstrates referral or attribution; it does not reveal the internal collection, drafting, clearance or charging process. The two notices corroborate common events, but no retrieved record establishes that the report authors copied those notices. [S/PV.9890, p. 2](https://docs.un.org/en/S/PV.9890), [S/PV.9931, p. 3](https://docs.un.org/en/S/PV.9931), [typed evidence edges](../data/census_v8/production_edges.csv).

## 2. Bounded evidence and the worked cycle

The pilot uses **six original sources**: four PDFs comprising **71 pages**, plus two official notice bodies. It selects **10 components and 23 source observations**, not every statement in these documents or all work undertaken during the cycle. The four PDF files were hash-checked against retained evidence; two PDF parsers checked the selected locations. Source dates, roles and qualifications remain inspectable in the [source manifest](../data/census_v8/source_manifest.csv) and [claim ledger](../data/census_v8/claim_ledger.csv).

| Output retained | Selected components in its own published contribution | What the support sheet does |
|---|---|---|
| **S/2025/187 — UNOWAS report** | Joint Nigeria visit; Forum; Dakar workshop; CNMC side-event; prior-period maritime context; regional analysis | Attaches earlier public corroboration and retains the visit-date disagreement. |
| **S/PV.9890 — UNOWAS briefing, 3 April** | Joint visit; Forum; workshop; Niger withdrawal announcement; regional assessment | Uses selected earlier facts, distinguishes a new dated announcement, and keeps briefing-specific judgment. |
| **S/2025/342 — UNOCA report** | Joint visit; Forum; workshop; separate knowledge publication; April planning exchange; maritime context; regional analysis | Preserves explicit referrals and records later source additions without backdating availability. |
| **S/PV.9931 — UNOCA briefing, 9 June** | Attributed earlier withdrawal announcement; Central Africa assessment | Retains the explicit prior-briefing link; does **not** insert the three core event blocks merely for symmetry. |

The three core event components—visit, Forum and workshop—appear **nine times** across the selected contributions in the two reports and UNOWAS briefing. This maps nine references to three identities; it is **not six eliminated tasks, a two-thirds workload reduction, or proof of repeated investigation**. The UNOCA briefing supplies a different kind of reuse: an attributed prior statement. [Component matrix](../data/census_v8/source_component_matrix.csv), [worked source-qualified support sheets and drafting examples](v8_worked_reporting_cycle.md).

### Timing and discrepancy controls

A worked replay must not import later knowledge into earlier products. The report issue dates do not establish when their content became available to a briefer. S/2025/187 is dated 26 March, covers through 31 March and prints production marker 020425; S/2025/342 is dated 30 May and prints 050625. The prototype uses **2 April and 5 June solely as declared replay proxies**, not verified publication or internal availability dates. Briefing checkpoints are their meeting dates. Current notice HTML does not establish that the historical bytes were unchanged. This is consequently a retrospective feasibility reconstruction, not proof of the exact real-time information set. [Source metadata](../data/census_v8/pilot_design.json).

The register deliberately preserves:

| Source issue | Handling in V8 | Why a single normalized value would mislead |
|---|---|---|
| Nigeria visit begins **27 January** in the joint notice and UNOCA report, **28 January** in the UNOWAS report. | One identity, both source-specific ranges, unresolved discrepancy flag. | Majority agreement does not establish which itinerary boundary is correct. |
| Forum lasts **29–31 January** in the notice; UNOCA records the representative’s attendance on **29 January**. | Event duration and individual attendance date have different fields. | These describe different units, not necessarily conflicting dates. |
| Workshop attendance is **more than 30**; the workplan was **adopted**. | Preserve the inequality and delivery stage. | Thirty exact attendees or completed implementation would be unsupported. |
| Best-practice collection published during the workshop. | Preserve **EV004**, a distinct knowledge product under UNOCA leadership. | A publication is not an additional course; its mention in a later source is not early availability evidence. |
| Niger **announced** withdrawal; UNOCA cites the earlier briefing. | Retain dated attribution and announcement status. | This pilot does not establish the legal or operational completion of withdrawal. |
| Maritime workshop took place **17 December 2024**. | Keep prior-period context outside the 2025 activity count. | A 2025 report does not change the activity year. |

Locations: [S/2025/187, paragraphs 49–54 and 57](https://docs.un.org/en/S/2025/187), [S/2025/342, paragraphs 61–67](https://docs.un.org/en/S/2025/342), [S/PV.9931, p. 3](https://docs.un.org/en/S/PV.9931). These controls also preserve the separate CNMC boundary-demarcation function despite the shared itinerary.

## 3. The additional production model to test

The proposed addition is a **small controlled register attached to existing storage and clearance**, not a new regional office, shared drafting unit, information portal or coordination meeting. Whether an equivalent internal register already exists is unknown.

```text
Existing joint activity / official sources
                  │
        Canonical component + source observations
        ├─ source version, locator and attribution
        ├─ event time ≠ publication ≠ replay availability
        └─ conflict, access and approval status
                  │
       ┌──────────┴──────────┐
 UNOWAS-selected facts   UNOCA-selected facts
 + own analysis          + own analysis
 + own clearance         + own clearance
       │                       │
 separate SG report      separate SG report
       │                       │
 dated briefing update → attributed later update
       │                       │
 separate briefing       separate briefing
```

| Production step | Proposed shared portion | Portion explicitly retained | Incremental-benefit test |
|---|---|---|---|
| Record the joint activity | Reuse an existing activity identity and source packet; nominate a custodian. | Each office checks the observations relevant to its own output. | Does this replace an actual duplicate request or only add another register? |
| Reconcile dates, roles and counts | Maintain a source-specific discrepancy log; corrections create a version rather than overwrite history. | Disputed wording may be qualified differently by each office with attribution. | Are reconciliation contacts and correction cycles reduced after counting register upkeep? |
| Prepare factual support | Export only the components required by each product and its checkpoint. | Different reporting periods, geographic scope and reader needs. | Is a fact re-keyed or searched again in the actual workflow, and can that step safely disappear? |
| Draft analysis and recommendations | Share approved source references, not automatically transferable political judgments. | Existing office, departmental and SG decision and clearance responsibilities. | No assumption that distinct analysis or review is avoidable. |
| Update for a briefing | Link previous facts and show subsequent changes separately. | Briefer-specific language, political assessment and final approval. | Does the process prevent stale facts without delaying the briefing? |
| Maintain the record | Use existing authorized document management where feasible. | Access restrictions, retention, security review and local business continuity. | Is maintenance lower than the demonstrated benefit? No platform procurement is presumed. |

The observed 8 April planning exchange and already joint visits/workshops stay in the status-quo baseline. There is no proposed duplicate “coordination meeting” to fix a lack of cooperation that the evidence contradicts.

### Proposed ownership and safety rules—not current appointments

A **designated source custodian** would maintain the common factual record; the two offices would each designate a factual reviewer. Existing report owners would select content, retain political analysis and use their existing clearance route. A designated records/security reviewer would confirm where the register may live. These roles may be absorbed into existing responsibilities only after workload review; V8 assigns no staff and authorizes no new posts.

No office should have to wait for the other’s reporting deadline. Freeze a product-specific version, record open discrepancies, and use approved qualified wording or the existing workflow when a joint resolution is not available. A later correction must not silently change an already issued support sheet. The prototype contains public material only; any operational extension needs role-based access, retention rules and controls for confidential interlocutors and assessments. Restricted data do not belong in this public repository.

## 4. What has—and has not—been demonstrated

The software reproduces four separate support sheets, preserves source locators and date qualifications, and rejects deliberately corrupted packets. **57 checks passed**: four valid packet fixtures, 18 deliberately corrupted fixtures rejected, and 35 independent invariants/source-parser checks. Corruptions include fabricated savings, changed ownership, lost attribution, future-source backfill and promoting adoption or announcement to completion. These constructed cases are not a sample from UN operations and yield no operational error-rate estimate. [Acceptance receipt](../data/census_v8/acceptance_receipt.json), [test implementation](../tests/check_v8_pilot.py).

| Claim | Assessment |
|---|---|
| A source-linked, product-specific factual support model is technically representable. | Demonstrated on the selected public corpus. |
| Known source disagreements and temporal/role distinctions can remain visible. | Demonstrated by deterministic views and checks; correctness still depends on source review. |
| Existing offices lack such a mechanism. | Unknown. |
| The mechanism reduces staff work, elapsed clearance time or factual errors. | Not measured; no live comparator. |
| Released cash, fewer required posts or additional net savings follow. | Not established. |
| Separate mandated reports or briefings can be discontinued. | Not proposed or supported. |

## 5. Operational acceptance and measurement gate

Before a live trial, the responsible offices should first show whether their present system already performs these functions. Reuse that system or close the proposal if it does. A shadow cycle may then test a specifically identified missing function without changing the issued products or clearance chain.

The [prospective measurement specification](../data/census_v8/measurement_plan.csv) defines observations rather than invented targets. The [empty workload-log template](../data/census_v8/workload_log_template.csv) contains **no empirical measurements**. Record source acquisition, factual reconciliation, drafting, review, briefing updates and register maintenance across **both** offices. Record consultation and security work too; do not move workload off one office’s books and label it a saving.

For a feasible first trial, log the existing process, run the support register in shadow, and review paired claims against the same source set. A shadow run measures overhead and correctness, **not labor that the live process actually eliminated**. A subsequent authorized substitution trial would be needed to establish avoided steps. Historical or before/after differences remain descriptive unless scope, workload and timing are made comparable; one retrospective pilot provides no causal estimate.

Proposed non-negotiable release rules are unchanged mandated outputs and approvals, no unauthorized disclosures, no unqualified source conflicts, and no unmarked later information. The offices must set tolerances for turnaround and quality **before** the operational comparison. Stop or revert when a mandatory output is delayed, attribution/security is lost, the existing process already solves the problem, or measured maintenance exceeds the actual work it replaces. These are prospective criteria, not assertions that an office has accepted them.

## 6. Financial boundary and conditional decision

Keep capacity and cash distinct. Net staff time would be the measured actual baseline workload minus the total new workload, including source maintenance and retained review. A decrease in staff hours is not automatically recoverable payroll or cash. For a later costed decision over K comparable cycles:

> **Potential incremental net cash = K × (verified cancelable recurring cost avoided − added recurring operating cost) − transition cost.**

No term is populated here. Costs already shared, already budgeted reductions, intra-UN charges, gross office budgets and noncancelable costs cannot be counted as newly avoided expenditure. Double counting C09, C02 and C05 would incorrectly monetize one pilot several times. The [existing financial guardrails](../data/financial_guardrails.csv) and [transaction-control framework](transaction_level_validation.md) remain controlling.

**Recommended disposition:** ready for comparison with existing owner workflows and a scoped shadow demonstration; **not** ready for operational consolidation, staffing changes or monetized savings. Later Cyprus or Lebanon applications are possible follow-on tests, not outcomes of this pilot. The course-completion watch remains paused, and V8 runs no course checks.

## Reproduction and preservation

Build with `python3 scripts/build_v8_design.py` and `python3 scripts/build_v8_pilot.py --build`; run `python3 tests/check_v8_pilot.py --sources --write`. Validate retained outputs with `python3 scripts/build_v8_pilot.py --check`. Build/source checks require the versions listed in the delivery package. The frozen-input manifest protects every selected pre-V8 data, document, script and test file; the output manifest binds the generated V8 evidence. [Pilot summary](../data/census_v8/pilot_summary.json) · [Frozen inputs](../data/census_v8/frozen_input_manifest.json).
