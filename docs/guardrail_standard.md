# F06 — Operational guardrail standard

## Purpose and authority

An efficiency intervention may advance only when it preserves the required mandate, safety, readiness and service performance within prospectively authorized limits. A favorable financial result cannot offset a failed critical guardrail. Apply this standard alongside the [candidate advancement standard](candidate_advancement.md) and [cost-accounting standard](cost_accounting_standard.md).

This is a project research standard. Creating a dossier, passing a validator or adopting a research reference grants no institutional permission to change operations, collect staff measurements, access restricted records or conduct a live trial. Required local owners and authorities must approve the precise activity. An owner role suggested by the research team is not an accepted institutional assignment. Existing case-specific controls remain applicable, including the closed live-use gates and paused course watch recorded in the [current research-reference pointer](../data/current_research_reference.json). The [V10 protocol](v10_owner_review_shadow_protocol.md) retains its own activation requirements.

## Guardrail dimensions

| Dimension | Required protection and measures | Hold or stop trigger |
|---|---|---|
| Mandate | Identify the controlling instrument, required outputs, beneficiaries, geographical/language coverage, independent analytical or control duties, and accountable delivery owner. | A required function is removed, materially narrowed or reassigned without authority; the alternative has no feasible delivery owner. |
| Safety and security | Preserve applicable protection, medical, evacuation, force-protection, information-security and duty-of-care standards; monitor incidents, exposure and critical response capability. | An applicable safety requirement is breached; essential response capability is lost; a serious incident is plausibly related to the intervention and requires urgent review. |
| Readiness | Measure required personnel, asset condition and availability, mobility, communications, logistics, surge reserve and receiving-unit capability. | Readiness falls below its approved floor; an essential asset or service is unavailable; the receiver lacks staff, infrastructure, support or delegated authority. |
| Service quality | Measure accuracy, completeness, critical errors, rework, client acceptance and required technical standards. Preserve confidentiality, factual attribution and approval integrity. | A critical error or control failure occurs, or quality exceeds its predeclared deterioration limit. |
| Timeliness | Measure mandated deadlines, ordinary and urgent response times, turnaround distributions, backlog and recovery time. | A mandatory deadline or emergency response limit is threatened or breached; backlog or ordinary delay exceeds the agreed ceiling. |
| Transition | Sequence custody, service acceptance, training, system/data transfer and residual obligations. Demonstrate receiver capability before removing source capability. | Acceptance is incomplete, a critical dependency is unresolved, liabilities are uncosted, or an irreversible action precedes tested handover. |
| Work transfer | Capture work removed at source, added at the receiver, retained locally, repeated in parallel, absorbed through overtime or supplied by contractors. | Claimed removal is actually unmeasured displacement, duplication or an unfunded burden on another entity. |
| Evidence and authority | Preserve a frozen baseline, prospective rules, usable identifiers, full exceptions, approved handling and authentic case-specific authority. | Evidence is materially incomplete or non-comparable, results are selectively excluded, thresholds change retrospectively, or required authority/handling approval is absent. |

An incident during a pilot is not automatically caused by the pilot. Protect affected operations immediately where warranted, then document timing, plausible mechanism, competing explanations and authorized incident review. Do not infer safety from absence of incidents in a small or short observation window.

## Prospective threshold setting

Set thresholds before examining intervention outcomes. Use applicable law and mandate requirements, operational/security standards, contractual service levels, and observed baseline distributions. The relevant authorized owner must approve the threshold and rationale. This standard invents no universal percentage reduction, delay tolerance, staffing reserve or acceptable failure rate.

Distinguish three forms of limit:

1. **Mandatory constraints:** unauthorized mandate reduction, loss of a required critical capability, prohibited disclosure or breach of a legal/safety rule cannot be traded against a financial benefit.
2. **Hard operational floors or ceilings:** case-specific minimum availability, coverage or readiness; maximum emergency response, critical error, backlog or deadline exposure.
3. **Ordinary performance tolerances:** allowed changes in routine turnaround, error/rework, workload and cost, justified from service standards, baseline variation and operational materiality.

If sufficient baseline information is absent, record the threshold as unset and prepare a separately authorized baseline-measurement stage. Do not substitute zero, invent a tolerance or start an intervention that depends on an unresolved critical threshold. A proposed tolerance may be developed during research but does not become an operational limit until accepted by the competent owner.

For a comparison intended to demonstrate equivalent or non-inferior performance, state the acceptable margin, observation window, sampling approach and required precision before testing. Record the number of independent operational units, exposure/demand, clustering and dependencies. Source observations, paragraphs and repeated appearances of the same activity are not independent trials. If sample size, missingness or baseline variation prevents the claimed inference, report descriptive results and withhold the causal or non-inferiority conclusion.

## Required guardrail record

Each applicable case/dimension must have a versioned record containing:

| Field | Required content |
|---|---|
| Identity and scope | Guardrail ID, intervention ID/version, dimension, exact service/work slice, entities and affected populations. |
| Authority | Controlling mandate or standard with source anchor; proposed owner role, accepted accountable owner and approval receipt distinguished. |
| Metric definition | Numerator, denominator, unit, aggregation, direction, criticality and materiality. |
| Baseline | Values/distribution, period, operating conditions, source, cutoff, record coverage and baseline version. |
| Comparison design | Counterfactual, matching/adjustments, exposure, independent sample size, dependency structure and planned uncertainty treatment. |
| Threshold | Floor/ceiling or permitted deterioration, rationale, mandatory versus discretionary status, approving authority and approval date. |
| Evidence capture | Source/custodian, collection cadence, approved storage, missingness/estimation flags, reviewer and declared prior exposure. |
| Response | Alert threshold, immediate protective action, fallback, stop authority, escalation route, corrective/rollback owner and restart conditions. |
| Assessment | Observed value, uncertainty, incidents/exceptions, transferred work, disposition, evidence receipt and review timestamp. |

An inapplicable dimension requires a documented scope-specific reason and reviewer acceptance. A blank field, unknown value or unavailable source is not a pass. Sensitive signatures, contacts, health details, operational locations and staff-level records remain in approved local storage; the public record may reference a safe receipt.

## Execution and stop rules

**Before activation:** hold the affected test if the intervention or owner is undefined; required authority is absent; critical thresholds are unset; the baseline is not usable; inputs or output requirements are unequal; approved evidence handling is absent; the receiver lacks demonstrated capacity; or the fallback and rollback responsibilities are unassigned. Research preparation can continue within its existing authorization.

**During execution:** the designated local authority stops the affected experimental or transition activity for a mandatory-constraint breach, plausible serious safety impact, critical readiness/quality failure, threatened mandatory deadline, exhausted effort/cost ceiling, unauthorized work transfer or material evidence-integrity failure. Continue required mission delivery through the approved fallback. Stopping a comparison must not suspend required services or delay an authorized correction. A missing or contaminated comparison may invalidate a quantitative conclusion without requiring otherwise safe normal operations to stop.

**After a stop:** preserve all observations, failed/pending tasks, incurred costs and incidents in the original denominator and history. Record what stopped, who acted, protective measures and which conclusions are blocked. Do not retroactively raise a ceiling, remove a failure or restart automatically. Restart requires the competent authority's documented decision, resolution of the trigger and a new prospective version where scope or thresholds change.

**At adjudication:** withhold advancement when the alternative appears cheaper because required output, coverage, reserve or quality declined, or because receiving/retained work and costs are missing. Withhold a cash claim when expenditure release is hypothetical. A supported capacity effect may be recorded under the appropriate claim class. A stopped case can yield a useful adverse finding; it cannot be scored as successful merely because the analysis completed.

**After implementation:** continue monitoring long enough to detect cost migration, seasonal demand, backlog, overtime, contractor substitution and capability deterioration. Define the window from the service cycle and risk rather than one uniform duration. A mandate, threat, demand or financing change triggers reassessment of comparability. Implement corrective or rollback actions only through the authorized owner and approved contingency plan; automatic reversal may itself endanger operations. Prefer reversible pilots and confirm the feasibility and cost of rollback before removing critical capacity.

## Findings and portfolio use

Record each dimension as `PASS`, `FAIL`, `UNKNOWN` or `NOT_APPLICABLE_WITH_JUSTIFICATION`, with evidence and the overall decision linked to the [candidate state](candidate_advancement.md). `UNKNOWN` on a critical condition blocks advancement. Noncritical unresolved issues require an explicit authorized disposition and cannot be silently treated as passed.

Case findings must identify the tested scope, dates, limitations and supported claim. Capacity effects, cost avoidance, recoveries and savings follow the [cost-accounting standard](cost_accounting_standard.md). No monetary finding is called savings before `FINANCIALLY_VALIDATED`. Only observed post-implementation evidence can support realization. Published totals must exclude unresolved or failed claimed savings while retaining their case records and incurred costs in the portfolio's full accounting.

Passing structural checks establishes record completeness and consistency only. Substantive review of authority, actual performance and causal attribution remains necessary. This standard creates no new finding that an existing operation is unsafe, ineffective, inefficient or wasteful.
