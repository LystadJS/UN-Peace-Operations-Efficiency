# Source-authority standard — F04

## Purpose and application

This standard governs how subsequent project work describes authorization, requirements, proposals, implementation and results. It supplements the historical [methodology](methodology.md); it does not rewrite historical findings or independently verify the legal status of any cited instrument. Apply it with the [desired end state](desired_end_state.md), [decision taxonomy](decision_taxonomy.md), [candidate advancement rules](candidate_advancement.md), [cost-accounting standard](cost_accounting_standard.md), and [guardrail standard](guardrail_standard.md).

A source must pass two separate assessments: **what authority it carries for the action at issue**, and **how directly and reliably it establishes the factual claim**. Neither assessment substitutes for the other. A duly adopted appropriation can establish authorized resources without establishing actual expenditure. An authenticated invoice can establish a payment without authorizing a mandate change.

## Axis 1: authority for the action

Record the issuing organ, document type, adoption or issuance status, exact operative action, addressee, competence, conditions and period. Assess the instrument in context; do not assign legal effect solely from its title, document symbol, or use of the word “resolution.”

| Source or action | Treatment in this portfolio | Limit on inference |
| --- | --- | --- |
| General Assembly resolution or decision adopted in plenary | Controlling evidence of what the Assembly adopted. Read the operative text, addressee, Charter competence, conditions and related instruments to determine the action's effect. Budgetary, organizational and internal directions may have operative institutional effect; recommendations require their own characterization. | GA resolutions and decisions are forms of action by the same organ. Neither is automatically ranked above the other, and neither makes every accompanying narrative statement a binding obligation. Do not describe every GA recommendation as binding on Member States. |
| Fifth Committee recommendation, report, draft resolution or action | Evidence of the Committee's action and the proposal placed before the Assembly. Preserve committee and plenary dates separately. | Committee approval or recommendation is not proof of plenary adoption. Verify the final adopted text and any changes before reporting a GA decision. |
| ACABQ report or recommendation | Advisory budgetary or administrative assessment. Record the exact recommendation and its relevant baseline. | Does not itself appropriate resources, amend a mandate, abolish a post, or establish Assembly adoption. A later adopting instrument must be separately linked. |
| Secretary-General report, proposed budget or reform proposal | Evidence of a proposal, estimate, management assessment or implementation report, according to the passage cited. | Submission and publication do not establish intergovernmental approval. An implementation narrative remains a reported claim until supported at the grain required for verification. |
| Authorized administrative instrument or delegated decision | Evidence of implementation authority within the issuing official's documented competence and delegation. Record scope, effective date, conditions and approving role. | Cannot override a governing mandate, appropriation condition or reserved decision. Organizational charts and unsigned plans alone do not establish delegated authority. |
| Security Council resolution or decision | Governing source for relevant Council mandate, scope and conditions. Determine the effect of the specific provision in its Charter context and wording. | A Council mandate and GA financing authority answer different questions. A budget line does not silently revise a Council mandate; a mandate does not prove that a particular expenditure occurred. |
| Public operational record or internal administrative record | Potential factual evidence and, where authentic and properly authorized, evidence of a specific administrative act. | Public or internal location alone creates no superior normative authority. Identify the author, competence, record type and underlying act. |

Use explicit classifications such as `GA_ADOPTED`, `COMMITTEE_RECOMMENDATION`, `ACABQ_ADVICE`, `SG_PROPOSAL`, `ADMINISTRATIVE_AUTHORIZATION`, `SC_MANDATE`, `IMPLEMENTATION_REPORTED` and `AUTHORITY_UNRESOLVED`. These describe source treatment, not candidate advancement states.

An `A/80/...` or `A/81/...` symbol identifies a document series; it does not prove adoption, implementation, or relevance to an adopted reform. “UN80,” “UNGA80” and “UNGA81” must be mapped to exact instruments rather than treated as interchangeable authority labels. Describe an option as required by an adopted provision, aligned with a recommendation or proposal, or independently justified, as the evidence warrants.

## Axis 2: directness and reliability of evidence

Evaluate evidence against the particular assertion. Record authenticity, proximity to the event, row grain, coverage, independence, completeness, date and known contradictions. A first-hand record may still be incomplete or erroneous; multiple reports may derive from one underlying source.

| Evidence class | Supported use, when authenticated and relevant | Additional qualification |
| --- | --- | --- |
| Primary governing text | Exact adopted, proposed or recommended action | Verify the final version and operative paragraph; assess authority under Axis 1. |
| Primary operational or financial record | A specified transaction, receipt, post action, service event, workload observation or implementation step | Verify identifiers, dates, units, scope and counterpart records where the claim requires them. A matched internal charge does not prove lower total UN cost. |
| Management or programme report | Attributed account of activities, implementation or performance | Record it as reported unless corroboration and completeness meet the claim's verification threshold. |
| Independent audit, evaluation or review | Findings within the review's stated methods, population and period | Independence strengthens review credibility but does not extend its scope or make historical findings current automatically. |
| Public notice, calendar, news item or summary | Evidence of publication, advertisement or attributed account | A scheduled course is not delivered training; an event article is not a complete activity population; a solicitation is not an award or payment. |
| Analytical inference or project-generated result | A reproducible conclusion from specified inputs and methods | Preserve assumptions, limitations and alternative explanations. Successful software checks establish only the properties actually tested. |

Public evidence can support operational or financial verification when it contains sufficiently complete underlying records at the required grain. Internal evidence is not inherently more authoritative or reliable; it must meet the same authentication and claim-support tests. Access restrictions determine handling, not truth. Preserve restricted records in approved storage and publish only permitted findings and non-sensitive evidence references.

## Claim-specific evidence requirements

| Claim | Required controlling evidence |
| --- | --- |
| “The GA adopted this requirement” | Final adopted resolution or decision, adoption record as needed, operative paragraph, addressee and applicable conditions. |
| “This amount was approved” | Applicable adopted appropriation or other competent financial authorization, exact period and inclusion perimeter. Distinguish appropriation from apportionment. |
| “This reform was implemented” | Dated records of the particular organizational, staffing, asset or service change. Define which implementation components were checked; an overall claim requires coverage of all material components. |
| “These activities duplicate one another” | Evidence of actual separately resourced work, substitutable output and need, scope and timing, necessary mandate/control distinctions, and a feasible removal or consolidation test. |
| “This intervention saves money” | The financial validation gate, named cost objects, comparable counterfactual, complete system costs, additionality, service guardrails and review required by F03/F05. |
| “This saving was realized” | Implemented action plus observed financial effects and preserved service over the defined period; reconcile transferred and residual costs. |
| “This obligation is unmet” | Applicable adopted obligation, due date, responsibility and sufficiently complete evidence of nonperformance. Missing or inaccessible evidence ordinarily supports `EVIDENCE_MISSING`, not a finding of noncompliance. |

A claim's wording must match its narrowest substantiated scope. Distinguish authentication of a whole file from semantic review of selected paragraphs, and selected-record verification from population-level conclusions.

## Required source receipt

For each material current claim retain:

1. Claim ID and exact assertion, affected entity/function, period and claim class.
2. Issuing organ or author, document symbol and title, source type, authority classification, adoption/issuance status and relevant date.
3. Exact operative paragraph, table, annex or record identifier; retain printed page and 1-based PDF page separately when they differ.
4. Official locator or approved internal reference, retrieval date, captured version, and checksum where a file is retained.
5. Evidence cutoff, observed event period, known publication lag and review scope.
6. Related corrigenda, revisions, superseding instruments and predecessor records; record whether they alter the specific claim.
7. Method of authentication, directness, limitations, conflicting evidence, reviewer and review date.
8. Information-handling classification and safe public derivative where applicable.

A URL returning successfully or a matching checksum authenticates only the specified retrieval or bytes. It does not verify interpretation, legal effect, implementation, or savings.

## Conflicts, updates and unresolved authority

Use the final adopted text to describe an adopted action. Use the applicable revised or corrected text for the affected factual presentation, while preserving the earlier version and a reasoned supersession link. A later publication does not automatically supersede an earlier instrument with a different scope or authority. Distinguish changes in proposal versions from substantive budget decisions.

Where sources conflict, compare authority for the claim, scope, period, grain, revision status and directness. Document the selected controlling source and the remaining discrepancy. Do not average conflicting values or silently substitute a convenient figure. Seek appropriate legal or substantive review where interpretation could change mandate, authorization, compliance, or a material recommendation.

Every current release must declare an evidence cutoff and the instruments examined through that cutoff. Changes in mandates, financing, organizational arrangements, adopted texts or relevant implementation records trigger reassessment. “Not issued,” “not retrieved,” “not reviewed,” “not yet due” and “not implemented” are distinct statuses. If authority or evidence cannot be established, record the gap and limit the claim; never infer approval from silence or absence of a contrary source.

These standards authorize project analysis only. Research adoption, repository publication and passing validation do not supply institutional approval, operational authority or permission to obtain or disclose restricted evidence.
