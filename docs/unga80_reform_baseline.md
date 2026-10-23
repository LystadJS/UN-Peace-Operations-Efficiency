# UNGA80 reform authority baseline — R03 and R05

This is a **scoped, partially verified public-source baseline**, reviewed through 23 October 2026. It identifies two freshly retrieved adopted texts and six retained mission-financing instruments requiring primary-text re-verification. It is not a complete census of the eightieth session. Neither publishing this baseline nor passing its validator establishes institutional approval or operational performance.

The [instrument register](../data/reforms/unga80_instruments.json) records retrieval scope, adoption evidence and remaining coverage gaps. The [action register](../data/reforms/unga80_actions.json) contains 65 provision-level records: 40 selected requests, institutional directions and safeguards from [A/RES/80/251](https://documents.un.org/api/symbol/access?l=en&s=A%2FRES%2F80%2F251&t=pdf), and 25 selected provisions from [A/RES/80/242](https://documents.un.org/api/symbol/access?l=en&s=A%2FRES%2F80%2F242&t=pdf). Short action labels are navigation aids; the complete adopted provision controls its interpretation.

## Competence and application

The review separates Assembly governance and budget directions from requests to the Secretary-General and from recommendations. It does not characterize every Assembly action as legally binding on Member States. Assessment here is a provision-specific research characterization, not an independent legal opinion. Changes to Council mandates require their own competent authority; a budget adjustment does not establish expenditure, reduced system cost or improved operations.

The applicability screen must read the conditions in each record, including the preserved-mandate and stock-review safeguards. Do not infer that UN80 authorizes removing ongoing peace-operation mandates. Retained mission-specific directions in [the original directive table](../data/ga_adopted_directives.csv) remain historical research inputs; they have not been silently promoted into newly authenticated obligations.

## Review and evidence limits

The official UN document service rendered both selected final English PDFs. Adoption dates were checked against their adoption headers and terminal plenary records. No raw PDF bytes were retained, so hashes are explicitly unknown. The register preserves official locators rather than presenting a hash of a project paraphrase as a source-file hash. Search-index discovery helped identify instruments but did not substitute for reviewing an adopted provision.

Attempts to retrieve the six retained mission-financing final texts failed. Those failures mean that this review did not authenticate those texts; they do not establish repeal, non-adoption or absence. Other GA80 support and reimbursement instruments, incorporated ACABQ recommendations, corrigenda, and subsequent amendments remain coverage gaps.

Selected institutional requests and directions are recorded separately from encouragements and calls upon other organs. A deadline expressed as the end of a month is normalized to its final calendar day. Mid-month and session-end deadlines remain unnormalized when an exact date is unspecified. Future deadlines receive `NOT_YET_DUE`; absent delivery evidence otherwise receives `EVIDENCE_MISSING`, never an inferred noncompliance finding. Implementation and results have not been assessed.

## Reproduction

```sh
python scripts/validate_reform_obligations.py --records data/reforms/unga80_actions.json
```

The check tests declarations and evidence references. Substantive source authentication, legal review, institution-wide coverage, implementation verification and financial validation require separate review. Requests for records can be prepared from this register, but are not thereby sent.
