# Pilot preparation and software rehearsal — E11–E15

**Three scoped charter drafts exist; all actual pilots remain blocked.** They cover RSCE service-line work and charges, UNIFIL–UNSCOL asset/procurement reconciliation, and BINUH–UNSOH aviation/support cost. No accepted accountable owner, evidence-access approval, operational authorization or usable actual baseline is recorded. Drafting these documents does not advance their cases beyond screening.

| Task | Principal result | Current meaning |
| --- | --- | --- |
| E11 | [Three pilot charters](../data/pilots/charters.json) | Bounded hypotheses, comparison designs, evidence needs, proposed owner roles and fallback requirements. |
| E12 | [Prospective threshold register](../data/pilots/thresholds.json) | Twenty-four pilot/dimension records with numeric thresholds, margins, sample sizes and observation windows explicitly unknown. |
| E13 | [Synthetic scenarios and analysis templates](../data/pilots/synthetic_scenarios.json) | Ten fictional, executable inputs testing model behavior; no UN transaction or service observations. |
| E14 | [Rehearsal receipt](../data/pilots/rehearsal_receipt.json) | Actual local execution of the synthetic inputs, with input/code hashes and reproduced outputs. |
| E15 | [Request status](../data/pilots/request_status.json) | Six prepared contracts and ten case-specific tracks; zero dispatches, responses, accepted owners or approved collections. |

Numeric operational thresholds are `TBD_BLOCKED`. The relevant competent owners must establish applicable mandate/SLA constraints, baseline distributions, acceptable margins, precision and observation windows before outcome inspection. The design invents no universal tolerances. Mandatory holds cover absent authority or evidence, unauthorized output reduction, critical capability failures, plausible serious safety impact, threatened mandatory deadlines, unmeasured work transfer and evidence/handling failures. A protective stop uses the approved fallback; it does not suspend required service. Restart requires competent approval and a prospective revision where needed.

The ten software scenarios preserve favorable, adverse and zero toy cost differences; null amounts; large internal transfers; missing receiver cost; unbridged periods; unmatched transfer entries; failed safety; and unknown readiness. All monetary quantities, owner receipts, equal-service assertions and scoring weights inside those inputs are fictional. A synthetic `PASS` supplies no actual owner approval. The evaluator always leaves savings unknown and never promotes candidates. The rehearsal receipt deliberately separates reproducible local software behavior from hosted-CI attestation and operational validation.

The request register mirrors E01–E06 contract identities and exact case/table coverage. E04 contains four separate GA-directed case subgroups, while E06 contains two reporting-owner tracks; the total is ten case tracks, not nine. Legacy `REQ01`–`REQ18` entries describe evidence packages and do not establish eighteen sent requests. Preparation does not trigger sending, contact an owner or permit collection of restricted records. No actual requests or records were transmitted as part of this work.

```sh
python scripts/rehearse_portfolio.py --write --check-requests
python scripts/rehearse_portfolio.py --check --check-requests
python tests/check_portfolio_rehearsal.py
```

The checks protect this current blocked-preparation snapshot. If real authority, accepted owners or evidence later become available, preserve this version and create a reviewed successor; do not edit a synthetic receipt into an operational finding. Actual adjudication requires authenticated linked records, comparable full-system cost, guardrail results and independent review under the foundation standards.
