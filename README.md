<p align="center">
  <img src="assets/readme-banner.svg" alt="White UN emblem and USUN seal framing the UN Peace Operations Efficiency title" width="100%" />
</p>

<p align="center">
  <a href="docs/methodology.md"><img alt="Source-linked evidence" src="https://img.shields.io/badge/Evidence-source--linked-062135?style=flat-square" /></a>
  <a href="docs/initial_findings.md"><img alt="DPPA and DPO" src="https://img.shields.io/badge/Scope-DPPA%20%2F%20DPO-062135?style=flat-square" /></a>
  <a href="docs/mission_budget_and_un80_audit.md"><img alt="UN80 audit" src="https://img.shields.io/badge/Reform-UN80%20audit-062135?style=flat-square" /></a>
  <a href="docs/appropriation_spm_consolidation_audit.md"><img alt="Phase 3" src="https://img.shields.io/badge/Phase-3%20reconciliation-062135?style=flat-square" /></a>
  <a href="#outputs-review-and-limitations"><img alt="Screening only" src="https://img.shields.io/badge/Status-screening%20only-062135?style=flat-square" /></a>
</p>

<p align="center">
  <a href="data/crosswalk.csv"><img alt="39 paired crosswalk records" src="https://img.shields.io/badge/Crosswalk-39%20pairs-002D74?style=flat-square" /></a>
  <a href="data/deliverable_inventory.csv"><img alt="46 deliverables" src="https://img.shields.io/badge/Deliverables-46-002D74?style=flat-square" /></a>
  <a href="data/mission_budget_register.csv"><img alt="Six mission proposals" src="https://img.shields.io/badge/Missions-6%20proposals-002D74?style=flat-square" /></a>
  <a href="data/un80_implementation_audit.csv"><img alt="11 reviewed arrangements" src="https://img.shields.io/badge/UN80-11%20arrangements-002D74?style=flat-square" /></a>
  <a href="data/ranked_consolidation_validation.csv"><img alt="14 ranked investigations" src="https://img.shields.io/badge/Investigations-14%20ranked-002D74?style=flat-square" /></a>
</p>

<p align="center">
  <a href="docs/systematic_2025_2026_executive_brief.md"><strong>Current systematic census findings</strong></a>
  &nbsp;&middot;&nbsp;
  <a href="docs/mission_budget_and_un80_audit.md">Review mission-budget and UN80 audit</a>
  &nbsp;&middot;&nbsp;
  <a href="docs/appropriation_spm_consolidation_audit.md">Inspect GA / SPM reconciliation</a>
  &nbsp;&middot;&nbsp;
  <a href="docs/initial_findings.md">Initial crosswalk findings</a>
</p>

## Purpose

The United Nations assigns closely related peace and security responsibilities to the Department of Political and Peacebuilding Affairs (DPPA), the Department of Peace Operations (DPO), special political missions, and field operations. Similar mandates, reporting lines, or deliverable descriptions can indicate coordination opportunities, but they do not themselves establish redundant work. **UN Peace Operations Efficiency creates source-linked comparisons of mandates, functions, deliverables, and financing to identify testable opportunities for consolidation without compromising operational effectiveness.** The current evidence covers 2027 departmental and SPM proposals, adopted 2026/27 GA peacekeeping appropriations, UN80 arrangements, and a public-only decision framework. The project does not claim that similar mandates are financially redundant. It is not a census of all UN peace operations.

**The governing rule is simple: every efficiency claim must be connected to its legal mandate, source, actual funding perimeter, and implementation risk.** A published budget reduction, existing shared office, or similar-sounding function is not automatically a new saving.

## Mandate–Function–Deliverable Analysis

The unit of analysis is an operational **function**, not a matching keyword or organizational title. The first crosswalk contains **39 paired DPPA–DPO comparisons**: 7 documented shared-structure rows, 2 documented joint-process rows, 7 planned-coordination rows, 9 candidate-overlap rows, 9 complementary-function rows, and 5 distinct-mandate rows. These are not 39 separate mergers; several rows describe facets of one joint structure.

The financial extension connects selected functions to field-mission proposals, DPO support-account allocations, and UN80 implementation cases. **A candidate becomes a potential net saving only after confirming that work is substitutable, separately funded, legally movable, and operationally safe to consolidate.** The [methodology and release contract](docs/methodology.md) sets out the evidence hierarchy, negative controls, screening tests, and budget boundaries.

## Choose a workflow

| Workflow | Use it for | Entry point |
| --- | --- | --- |
| **Mandate and deliverable crosswalk** | Compare documented responsibilities; distinguish joint structures, proposed coordination, complementary roles, and overlap hypotheses. | [Initial findings](docs/initial_findings.md) · [Crosswalk CSV](data/crosswalk.csv) |
| **UN80 implementation and cost allocation** | Trace reforms, departmental support funding, six mission proposals, and costs that must not be counted twice. | [Mission-budget audit](docs/mission_budget_and_un80_audit.md) |
| **General Assembly and SPM reconciliation** | Compare proposals with financing authorities, track SPM addenda, and inspect unresolved appropriation evidence. | [GA / SPM audit](docs/appropriation_spm_consolidation_audit.md) · [Transaction validation](docs/transaction_level_validation.md) |
| **Candidate review and reproducibility** | Inspect ranked investigations, source anchors, open validation gates, and machine-checkable datasets. | [Ranked queue](data/ranked_consolidation_validation.csv) · [Data dictionary](docs/data_dictionary.md) |
| **Public-only decisions, no internal ledgers** | Review 18 classified opportunities, GA controls and financing exclusions; compare assumptions using a guarded R model. | **[Executive brief](docs/public_only_executive_brief.md)** · [Full framework](docs/public_only_decision_framework.md) |

## Evidence review workflow — no installation

1. Start with the [initial findings](docs/initial_findings.md) and open a [crosswalk record](data/crosswalk.csv). Its classification describes **what the cited evidence supports**, not whether a cut is warranted.
2. Trace mandates, functions, deliverables, and citations using the [source manifest](data/source_manifest.csv), [evidence links](data/evidence_links.csv), and [data dictionary](docs/data_dictionary.md).
3. Inspect the corresponding [UN80 register](data/un80_implementation_audit.csv), [mission-budget records](data/mission_budget_register.csv), or [GA/SPM reconciliation records](data/ga_mission_reconciliation.csv). Keep calendar-year 2027 programme budgets separate from July–June 2026/27 peacekeeping accounts.
4. Review the [ranked queue](data/ranked_consolidation_validation.csv) and [quality issues](data/quality_issues.csv). Record the staffing, service, contractual, recipient, and appropriation evidence required before advancing a candidate.

This is an inspectable research repository, **not a deployed browser application or an automated cost-cutting system**. GitHub displays the reports and CSVs directly; the existing scripts validate internal dataset relationships, not political or financial conclusions.

## Local Python & R validation

Clone the repository and execute the documented Python validators:

```bash
git clone https://github.com/LystadJS/UN-Peace-Operations-Efficiency.git
cd UN-Peace-Operations-Efficiency

python3 scripts/validate_crosswalk.py
python3 scripts/validate_mission_audit.py
python3 scripts/validate_phase3.py
```

Base-R alternatives support crosswalk validation and reproduction of gross mission proposal comparisons:

```bash
Rscript scripts/validate_crosswalk.R
Rscript scripts/analyze_mission_budgets.R
```

The [GitHub Actions workflow](.github/workflows/validate.yml) defines automated repository checks. **A passing structural validator does not independently verify appropriations, implementation, redundant expenditure, or net savings.**

## How it works

```text
UN budget proposals + GA / SPM financing records
                       |
             Source IDs and mandates
                       |
          Functions, deliverables, dates
                       |
         DPPA / DPO crosswalk + controls
                       |
       UN80 reform status + mission context
                       |
         Funding boundaries + cost bridge
                       |
        Candidate validation and ranking
                       |
        Source-linked reports and CSVs
          (unverified items stay open)
```

**Documentary similarity, operational duplication, and recoverable savings are separate findings.** Existing consolidations belong to the baseline; SG requests are not General Assembly appropriations; and net incremental savings require a defensible counterfactual, implementation costs, and risk analysis.

### Implemented evidence layers

| Layer | Available records | Interpretive boundary |
| --- | --- | --- |
| **Departmental baseline** | 59 functions, 25 mandates, 46 quantified deliverables, 39 pairings, and 6 negative controls. | Similar outputs and objectives can reflect complementary mandates, not duplication. |
| **UN80 and mission-budget audit** | 11 reform arrangements, 6 selected SG mission proposals, 18 linked mission-function comparisons, and DPO support-account bridges. | Proposed reorganization is not confirmed implementation; pre-budgeted reductions are not new savings. |
| **GA-approved mission financing** | 6/6 GA financing appropriations reconciled, 11 mission totals and 102 category records. | The 2026/27 assessed accounts are distinct from proposed calendar-2027 SPM financing. |
| **2027 SPM budget reconciliation** | 36 mission proposals, 3 cluster controls, 31 embedded efficiencies, 17 XB finance entries, 16 cross-pillar pairings and 12 audit priorities. | Four addenda reconciled to $422.671m, still proposed; new net savings unverified. |
| **Transaction-level control audit (Phase 5)** | 3 cases, 12 published cost objects, 18 evidence requests, 12 source references, 9 RSCE staffing model entries and tested R matcher. | No signed inventories, invoice pairs, settlement postings or separately proven incremental savings. |
| **Public-only decision framework (Phase 6)** | 18 opportunity rows, 24 finance nodes, 21 inclusion links, 18 explicit release gates, nine official source watches. | 14 public-research cases can proceed; zero additional net savings estimated or authorized. |

[Methodology](docs/methodology.md) · [Mission-budget audit](docs/mission_budget_and_un80_audit.md) · [GA appropriation audit](docs/appropriation_spm_consolidation_audit.md) · **[2027 SPM reconciliation](docs/spm_2027_reconciliation.md)** · **[Transaction evidence audit](docs/transaction_level_validation.md)**

## Phase 5 — Transaction auditing with private ledger evidence

The [transaction-controls audit](docs/transaction_level_validation.md) identifies what can be verified from official published documents and what needs an internal transaction record. It isolates **$438,100 UNIFIL/UNSCOL** and **$1.4m BINUH/UNSOH** already estimated in the 2027 SPM proposal and treats **$3.2591m RSCE SPM share** as financing, not an efficiency. The [source catalogue](data/transaction_sources.csv), [case controls](data/transaction_validation_cases.csv), [evidence requests](data/transaction_evidence_requests.csv), and [RSCE FTE/post reconciliation](data/rsce_workforce_model_vs_post_actions.csv) support follow-on review. **0 of 3 cases has complete independent ledger-level verification**; no new net savings estimates are presented.

For an authorized local ledger extract, run `Rscript scripts/audit_transaction_ledger.R /SECURE_LOCATION/ledger.csv /SECURE_LOCATION/outputs`. Use the explicitly [synthetic fixture](tests/fixtures/transaction_ledger_SYNTHETIC.csv) for software checks only. Never publish real invoices, personnel IDs or sensitive field operations data to a public GitHub repository.

## Phase 6 — Public-source decision framework

**[Read the executive decision brief](docs/public_only_executive_brief.md)** or the [full public-only research plan](docs/public_only_decision_framework.md). The new [18-case opportunity register](data/public_opportunity_register.csv) classifies **14 public-research investigations**, three already-budgeted initiatives to monitor and one mandate/legal negative control. The source-linked [finance nodes](data/public_finance_nodes.csv), [21 inclusion relations](data/public_finance_edges.csv), [release gates](data/public_release_gates.csv), and [official report watchlist](data/public_source_watchlist.csv) prevent reading gross budgets, internal service charges, and prebooked reductions as new savings.

Public decision-board generator: Rscript scripts/render_public_decision_board.R . /tmp/peace-public. The optional [conditional break-even engine](scripts/evaluate_conditional_options.R) is assumption-based and includes only clearly [synthetic engineering fixtures](tests/fixtures/scenarios_SYNTHETIC.csv) in this repository. No actual eligible incremental net cost pool has been demonstrated. Private UN transaction records are not required for the public report work and must not be published in GitHub.

## Outputs, review, and limitations

**Verified at the documentary level:** source-paired comparisons, 2027 departmental proposals, selected 2026/27 mission proposals, identified UN80 arrangements, financial boundaries, GA financing-resolution references, and an evidence-based research queue. The primary sources include [A/81/6 (Sect. 3)](https://digitallibrary.un.org/nanna/record/4110936/files/A_81_6_%28Sect._3%29-EN.pdf?registerDownload=1&version=1&withMetadata=0&withWatermark=0), [A/81/6 (Sect. 5)](https://docs.un.org/en/A/81/6%20%28Sect.%205%29), and the [Fifth Committee decisions register](https://www.un.org/en/ga/fifth/80/resdec80.shtml).

**Financial reconciliation:** The six 2026/27 peacekeeping GA-approved mission-maintenance budgets total **$4,028.188m**; their original SG requests totaled **$4,120.9507m**. The four uploaded 2027 SPM addenda now reconcile to a separate, **proposed $422.671m** for 36 continuing missions including **$3.2591m RSCE share**. **31 identified 2027 efficiencies ($14.6925m) are already embedded in the SPM requests**, not additional savings. The SPM extrabudgetary item ledger totals about **$32.977m** in voluntary and cost-recovery estimates; previously reported source figures remain discrepant. See the [SPM reconciliation](docs/spm_2027_reconciliation.md).

**Research status (8 October 2026):** 36 of 36 2027 SPM Secretary-General mission proposals reconciled against 2026 budget baselines, including **all nine Cluster III offices**; financial ACABQ mission advice reconciled **27/36** (Clusters I and II). Main **A/81/7** provides 16 cross-cutting research/good-governance controls mapped 51 times across the nine missions but **no Cluster III-specific ACABQ financial cut**. Cluster III continuing budget **$325.3539m proposed vs $324.5499m approved 2026** (net +$0.8040m), with **$14.5604m already priced 2027 estimated efficiencies**. The user reports **A/81/7/Add.1 and Add.4 not yet issued**; full ACABQ-recommended SPM envelope remains unknown. The revised hierarchy contains **14 parent reviews and nine Cluster III work packages**, with no verified additional net savings.

## Repository guide

| Path | Contents |
| --- | --- |
| [`data/`](data/) | Mandates, functions, deliverables, DPPA–DPO pairings, UN80, mission budgets, cost bridges, GA/SPM records, and ranked investigations |
| [`docs/`](docs/) | Methodology, initial findings, Phase 2 mission/UN80 audit, Phase 3 appropriation/SPM audit, and data dictionary |
| [`scripts/`](scripts/) | Python and base-R validators; reproducible mission-budget calculations |
| [`.github/workflows/`](.github/workflows/) | Repository validation CI |

Start with the [initial findings](docs/initial_findings.md), consult the [data dictionary](docs/data_dictionary.md) for definitions, and use the [2027 SPM audit](docs/spm_2027_reconciliation.md) for the latest regular-budget and shared-service findings. Every figure must retain its source, period, and proposal-versus-approval status.

<sub>Public analyses are decision-support research, not organizational determinations. Verify amounts, mandates, and operational assumptions against underlying UN documents before proposing restructuring or savings.</sub>

## Phase 7 — Documented evidence requests and output comparisons

The [18-dataset transaction request](docs/restricted_transaction_data_request.md) specifies fields and custodians. The [32-pair deliverable crosswalk](data/public_deliverable_crosswalk_2027.csv) compares regional missions, regional desks, and training. Read the [analysis](docs/public_deliverable_overlap_2027.md). The 2027 ACABQ reports have since been partially reconciled: **27 mission-level advisory amounts are now complete**, while **nine Cluster III lines remain pending**. See [reconciled advice and remaining scope](docs/acabq_2027_reconciliation_status.md) and [36-row mission table](data/acabq_2027_mission_reconciliation.csv).

## Phase 8 — 2027 ACABQ advisory recommendations

The three newly uploaded ACABQ PDFs were read and source-verified. [Full reconciliation](docs/acabq_2027_reconciliation_status.md) distinguishes **Cluster I (12 missions, −$182.5k net)**, **Cluster II (15 missions, no further quantified adjustment)**, and **Cluster III (9 missions, no accessible ACABQ Add.4 report)**. [Financial actions](data/acabq_2027_financial_actions.csv) include **12 distinct advisories** covering the SPMs and separate 2027 Section 3/Section 5 regular budgets; [qualitative directives](data/acabq_2027_qualitative_directives.csv) preserve 20 implementation and mandate safeguards. [Revised 14-candidate public research ranking](docs/acabq_2027_ranked_assessment.md) retains previous Phase 3 order. [Source checksum manifest](data/acabq_2027_source_manifest.csv) records three uploaded official PDFs. Use `python3 scripts/validate_acabq_2027.py` for repeatable acceptance tests. These are **ACABQ recommendations, not GA appropriations or incremental net savings**.

## Phase 9 — Nine-mission Cluster III SG reconciliation and cross-cutting ACABQ advice

**[Current executive decision brief](docs/public_only_executive_brief.md)** · [Nine-mission budget and risk report](docs/acabq_2027_clusterIII_review.md) · [Revised comprehensive consolidation ranking](docs/acabq_2027_ranked_assessment.md).

The original [2027 SG Cluster III reconciliation](data/acabq_2027_clusterIII_sg_baseline.csv) resolves **9/9 mission budgets** and staffing comparators. The **cross-cutting A/81/7 framework** comprises [16 sourced considerations](data/acabq_2027_main_crosscutting_framework.csv) and [51 mission-applicability links](data/acabq_2027_clusterIII_crosscutting_map.csv), while **mission-specific ACABQ advisory adjustments remain unknown, not zero**. The $14.5604m of separately itemized 2027 Cluster III efficiency estimates is **already in the SG proposal**, not additional savings. The overall [23-record research hierarchy](data/consolidation_comprehensive_2027.csv) contains 14 umbrellas and nine linked mission work packages, marked nonadditive. [Conditional arithmetic](data/acabq_2027_conditional_envelope.csv) includes an illustrative $422.4885m partial-advice scenario explicitly **not official**. [Automated validation](scripts/validate_phase9_clusterIII.py) gates numeric controls and prevents invented approvals or costs.

## Phase 10 — Actual 2025–2026 deliverable and activity matching

**[Current executive readout](docs/retrospective_2025_2026_executive_brief.md)** · [Full retrospective analysis](docs/retrospective_2025_2026_overlap_audit.md) · [11 ranked reuse and non-duplication assessments](data/retrospective_2025_2026_reuse_decisions.csv).

A purposive official-source review established **42 public-source records**, **38 canonical activities/products** (37 in the 2025–2026 activity window plus one excluded **October 2024** event with a 2025 publication), and **36 source-linked pairing adjudications**. Evidence connects to **19 of the 32 2027 proposed output categories**; remaining unmatched categories are **not shown to be absent**. The sources document joint UNOWAS–UNOCA field activity/workshops, UNAMA–UNRCCA courses, integrated DPPA–DPO Council briefings and policy guidance, and mandated regional reporting that must stay separate.

The [source catalogue](data/retrospective_2025_2026_sources.csv), [canonical activity register](data/retrospective_2025_2026_activities.csv), [match ledger](data/retrospective_2025_2026_matches.csv), [crosswalk with retrospective references](data/public_deliverable_crosswalk_2027.csv) and [four-group summary](data/retrospective_2025_2026_summary.csv) are versioned in GitHub. The [14-candidate research ranking](data/acabq_2027_ranked_consolidation.csv) includes retrospective evidence fields **without changing rank based on a nonrepresentative sample**. No separately paid duplicate service or incremental savings has been financially verified.

Validate with `python3 scripts/validate_retrospective_matches.py`. Generate the current review queue via `Rscript scripts/render_retrospective_board.R . /tmp/peace-retrospective-board`; a base-R acceptance test runs in CI. No confidential finance records are needed for this documentary phase.


## Phase 11 — Systematic 2025–2026 Council and mission-publication census

**[Current executive brief](docs/systematic_2025_2026_executive_brief.md)** · **[Full methodological and reuse report](docs/systematic_2025_2026_census.md)** · [Reproducible source-quality checks](scripts/validate_systematic_census.py).

The official Council annual indexes yield **132 Secretary-General reports** (84 from 2025, 48 from 2026 through 8 October) and **474 meeting-record variants** (296 and 178). **The 255 distinct 2025 formal Council meetings match the annual official total; 2026 currently has 151 distinct meeting IDs**, an incomplete-year snapshot. Resumptions are **not additional meetings**, and the Council's 115 informal 2025 consultations are separately counted in official statistics, not in the formal meeting ledger.

The selected mission/department records now cover **46 canonical activities and outputs**, including one October **2024** event properly excluded from 2025–2026 despite a 2025 publication date. These news/event records are **not an exhaustive site-wide field/training census**. There are **36 earlier adjudicated cases and nine supplementary cases**, plus a [13-case shared-production shortlist](data/systematic_shared_production_options.csv). The source-indexed reports and meeting variants are integrated as [652 nonadditive record views](data/systematic_master_record_views_2025_2026.csv); this is **not** a claim of 652 unique substantive products.

Research inputs: [full Secretary-General report index](data/systematic_sg_reports_2025_2026.csv) · [Council formal-meeting and resumption records](data/systematic_sc_meetings_2025_2026.csv) · [selected field/training events](data/systematic_field_training_activity_2025_2026.csv) · [15 source-pair screening hypotheses](data/systematic_council_report_pair_candidates.csv) · [nine further adjudications](data/systematic_2025_2026_additional_matches.csv) · [coverage status](data/systematic_census_coverage.csv). Run `python3 scripts/validate_systematic_census.py`, or generate a public [R review board](scripts/render_systematic_census.R). **No actual duplicate financial charges or new net savings are supported by these sources.**

## Phase 11 — Scoped 2025–2026 report and activity census

**[Current executive census brief](docs/census_2025_2026_executive_brief.md)** · [Full source and coverage audit](docs/census_2025_2026_public_evidence.md).

The official Security Council Secretary-General report indexes now support a **79-report identity census across 17 selected mission and mandate series**: **46 reports from 2025** and **33 through 8 October 2026**. The distinct [public activity collection](data/census_2025_2026_public_activities.csv) contains **49 records**, including one **October 2024 temporal exclusion**. These meetings, field visits and training events are **selected published activities, not an exhaustive event census**. The [coverage matrix](data/census_2025_2026_coverage_matrix.csv) records that limitation and the [14 report-pair tests](data/census_2025_2026_report_pair_tests.csv) preserve different legal reporting obligations.

Public evidence supports shared event/source identifiers and administrative coordination, not automatically merging different Secretary-General reports or specialist courses. **No separately charged duplicate service or new net cost saving is verified.** Run `python3 scripts/validate_census_2025_2026.py` to check the census bounds.
