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
  <a href="data/ranked_consolidation_validation.csv"><img alt="14 ranked investigations" src="https://img.shields.io/badge/Investigations-12%20ranked-002D74?style=flat-square" /></a>
</p>

<p align="center">
  <a href="docs/initial_findings.md"><strong>Read initial findings</strong></a>
  &nbsp;&middot;&nbsp;
  <a href="docs/mission_budget_and_un80_audit.md">Review mission-budget and UN80 audit</a>
  &nbsp;&middot;&nbsp;
  <a href="docs/appropriation_spm_consolidation_audit.md">Inspect GA / SPM reconciliation</a>
</p>

## Purpose

The United Nations assigns closely related peace and security responsibilities to the Department of Political and Peacebuilding Affairs (DPPA), the Department of Peace Operations (DPO), special political missions, and field operations. Similar mandates, reporting lines, or deliverable descriptions can indicate coordination opportunities, but they do not themselves establish redundant work. **UN Peace Operations Efficiency creates source-linked comparisons of mandates, functions, deliverables, and financing to identify testable opportunities for consolidation without compromising operational effectiveness.** The current evidence covers departmental 2027 budget proposals, six selected 2026/27 mission proposals, relevant UN80 arrangements, and preliminary General Assembly and special political mission (SPM) budget reconciliation. It is not a census of all UN peace operations.

**The governing rule is simple: every efficiency claim must be connected to its legal mandate, source, actual funding perimeter, and implementation risk.** A published budget reduction, existing shared office, or similar-sounding function is not automatically a new saving.

## Mandate–Function–Deliverable Analysis

The unit of analysis is an operational **function**, not a matching keyword or organizational title. The first crosswalk contains **39 paired DPPA–DPO comparisons**: 7 documented shared-structure rows, 2 documented joint-process rows, 7 planned-coordination rows, 9 candidate-overlap rows, 9 complementary-function rows, and 5 distinct-mandate rows. These are not 39 separate mergers; several rows describe facets of one joint structure.

The financial extension connects selected functions to field-mission proposals, DPO support-account allocations, and UN80 implementation cases. **A candidate becomes a potential net saving only after confirming that work is substitutable, separately funded, legally movable, and operationally safe to consolidate.** The [methodology and release contract](docs/methodology.md) sets out the evidence hierarchy, negative controls, screening tests, and budget boundaries.

## Choose a workflow

| Workflow | Use it for | Entry point |
| --- | --- | --- |
| **Mandate and deliverable crosswalk** | Compare documented responsibilities; distinguish joint structures, proposed coordination, complementary roles, and overlap hypotheses. | [Initial findings](docs/initial_findings.md) · [Crosswalk CSV](data/crosswalk.csv) |
| **UN80 implementation and cost allocation** | Trace reforms, departmental support funding, six mission proposals, and costs that must not be counted twice. | [Mission-budget audit](docs/mission_budget_and_un80_audit.md) |
| **General Assembly and SPM reconciliation** | Compare proposals with financing authorities, track SPM addenda, and inspect unresolved appropriation evidence. | [GA / SPM audit](docs/appropriation_spm_consolidation_audit.md) |
| **Candidate review and reproducibility** | Inspect ranked investigations, source anchors, open validation gates, and machine-checkable datasets. | [Ranked queue](data/ranked_consolidation_validation.csv) · [Data dictionary](docs/data_dictionary.md) |

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
| **GA approvals / SPM documentary reconciliation** | Six adopted mission appropriations reconciled; 11 mission resource totals; 102 approved cost-component records; four SPM addenda tracked; 14 ranked investigations. | GA funding is verified, but SPM financial addenda and actual avoidable costs remain unverified. |

[Methodology](docs/methodology.md) · [Mission-budget audit](docs/mission_budget_and_un80_audit.md) · [GA/SPM audit](docs/appropriation_spm_consolidation_audit.md)

## Outputs, review, and limitations

**Verified at the documentary level:** source-paired comparisons, 2027 departmental proposals, selected 2026/27 mission proposals, identified UN80 arrangements, financial boundaries, GA financing-resolution references, and an evidence-based research queue. The primary sources include [A/81/6 (Sect. 3)](https://digitallibrary.un.org/nanna/record/4110936/files/A_81_6_%28Sect._3%29-EN.pdf?registerDownload=1&version=1&withMetadata=0&withWatermark=0), [A/81/6 (Sect. 5)](https://docs.un.org/en/A/81/6%20%28Sect.%205%29), and the [Fifth Committee decisions register](https://www.un.org/en/ga/fifth/80/resdec80.shtml).

**GA approved budget reconciliation complete (6/6):** The uploaded six operative financing resolutions and A/C.5/80/20 independently confirm **$4,028.188m** in six mission-maintenance appropriations versus **$4,120.9507m** in original requests (**$92.7627m below request**; not savings). The six **inclusive** GA appropriations total **$4,442.1194m** including support account/UNLB/RSCE shares. The **2027 special political mission addenda remain unextracted (0/4)** and their Section 3 extrabudgetary estimates differ by **$4.9596m**. See [GA source reconciliation](docs/appropriation_spm_consolidation_audit.md) and the [seven-file checksum manifest](data/approved_document_manifest.csv).

**Research status (8 October 2026):** Financial approval comparison verified **6/6**, SPM financial addenda pending **0/4**, and **14 source-linked investigations** queued for validation. The GA approved 91 UNMISS civilian abolishments, including 53 electoral positions, and requested UNISFA translation and transferred-asset reviews. **No verified duplicate spending or incremental net savings** has been calculated; research ranks are not estimates of cuts.

## Repository guide

| Path | Contents |
| --- | --- |
| [`data/`](data/) | Mandates, functions, deliverables, DPPA–DPO pairings, UN80, mission budgets, cost bridges, GA/SPM records, and ranked investigations |
| [`docs/`](docs/) | Methodology, initial findings, Phase 2 mission/UN80 audit, Phase 3 appropriation/SPM audit, and data dictionary |
| [`scripts/`](scripts/) | Python and base-R validators; reproducible mission-budget calculations |
| [`.github/workflows/`](.github/workflows/) | Repository validation CI |

Start with the [initial findings](docs/initial_findings.md), consult the [data dictionary](docs/data_dictionary.md) for definitions, and use the [latest audit](docs/appropriation_spm_consolidation_audit.md) to track financial evidence gaps. Every figure must retain its source, period, and proposal-versus-approval status.

<sub>Public analyses are decision-support research, not organizational determinations. Verify amounts, mandates, and operational assumptions against underlying UN documents before proposing restructuring or savings.</sub>
