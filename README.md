# UN Peace Operations Efficiency

**Baseline 0.1 · 8 October 2026 · Research status: screening only**

This repository develops an auditable **mandate–function–deliverable crosswalk** across the United Nations Department of Political and Peacebuilding Affairs (DPPA), Department of Peace Operations (DPO), and related entities. Its purpose is to identify organizational overlap **without equating similar language with duplication**, then test where consolidation or shared service delivery could preserve effectiveness at lower cost.

## First release at a glance

| Dataset | Records | Use |
|:--|--:|:--|
| [Functions](data/functional_inventory.csv) | 59 | Organizational scope and source anchors |
| [Mandates](data/mandate_inventory.csv) | 25 | Shared and distinct legal / policy instruments |
| [Quantified deliverables](data/deliverable_inventory.csv) | 46 | Published 2025 actual and 2027 planned outputs |
| [Paired DPPA–DPO crosswalk](data/crosswalk.csv) | 39 | Classified and reviewable relationships |
| [UN80 / other reform register](data/un80_register.csv) | 11 | Separates explicit consolidations from plans and earlier arrangements |
| [Validation candidates](data/candidate_validation.csv) | 18 | Testable, risk-gated potential reforms |
| [Document evidence links](data/evidence_links.csv) | 218 | One source pointer per inventory item / paired comparison |
| [Negative controls](data/non_overlap_controls.csv) | 6 | False-positive checks for similarity-based matching |
| [Data-quality issues](data/quality_issues.csv) | 7 | Open source discrepancies and scope limitations |
| [Financial guardrails](data/financial_guardrails.csv) | 13 | Budget boundaries; not estimates of savings |

**Read the [initial findings](docs/initial_findings.md) first.** The [methodology](docs/methodology.md) explains how an overlap becomes a savings candidate, and the [data dictionary](docs/data_dictionary.md) specifies column meanings.

### Classification, not savings

The 39 paired records contain **7 documented shared-structure rows**, **2 documented joint-process rows**, **7 planned-coordination rows**, **9 candidate-overlap rows**, **9 complementary-function rows**, and **5 distinct-mandate rows**. These are *rows*, not 39 independent organizational restructurings. The repeated shared-structure rows primarily represent aspects of a smaller number of joint offices.

No assessment in this release establishes waste, abolishable posts, net savings, or the operational completion of a UN80 reform. `high` candidate priority means **high value to investigate**, not high expected savings.

## Primary sources

- **[A/81/6 (Sect. 3)](https://digitallibrary.un.org/nanna/record/4110936/files/A_81_6_%28Sect._3%29-EN.pdf?registerDownload=1&version=1&withMetadata=0&withWatermark=0)**, *Political affairs*, 8 May 2026, 134 pages. Includes DPPA, related offices and SPM aggregate estimates.
- **[A/81/6 (Sect. 5)](https://docs.un.org/en/A/81/6%20%28Sect.%205%29)**, *Peacekeeping operations*, 17 April 2026, 67 pages. Includes DPO, UNTSO and UNMOGIP, **not** all peacekeeping field-mission budgets.

Both were provided by the project owner and are identified by file SHA-256 in [source_manifest.csv](data/source_manifest.csv). PDF binaries are not republished here. The automated retrieval of the Section 5 symbol-resolver URL was restricted; use the official [Fifth Committee 2027 budget document index](https://www.un.org/en/ga/fifth/81/ppb2027.shtml) if the resolver does not open. Source anchors cite the **uploaded full document**, not the shorter Part A version.

## Evidence standard

1. **Directly documented**: what the proposals expressly state (including proposed changes and joint structures).
2. **Analytical screening**: our inference that separately described products may intersect; requires work plans, recipient lists and cost centres.
3. **Unverified**: staffing implementation, net duplication, transaction-level expenditure, legal authority and savings until independent evidence is obtained.

The dataset distinguishes **planned** 2027 outputs from **actual** 2025 outputs, and treats separate funding streams and entities as non-fungible until documented otherwise. See [financial guardrails](data/financial_guardrails.csv); do not add programme grants into administrative savings.

## Reproduce and inspect

```bash
python3 scripts/validate_crosswalk.py
# Alternatively: Rscript scripts/validate_crosswalk.R
```

GitHub Actions runs the zero-dependency Python validator on every push and pull request. The R validator uses base R only. Both validators check referential integrity and source-page bounds. Neither substitutes for subject-matter validation or external budget audit.

## Next research gate

Acquire detailed SPM addenda, DPO support-account report A/80/631, 2026/27 individual mission budgets, post-level finance/HR data, documented UN80 implementation records, and field-level delivery registers. Then validate [candidates](data/candidate_validation.csv), estimate **net incremental** savings (not gross budget figures), and assess mandate and operational risk.

**A documented shared structure is an existing baseline, never a new saving to be counted again.**

## Phase 2 — Mission budgets and UN80 cost-accounting audit (8 October 2026)

The source-linked [mission-budget and implementation assessment](docs/mission_budget_and_un80_audit.md) extends the original 39 DPPA–DPO comparisons. It adds:

- **6** 2026/27 mission **Secretary-General budget proposals**, broken out into military/police, civilian and operational costs ([financial register](data/mission_budget_register.csv)).
- **18** mission-level pairings linked to baseline crosswalk IDs ([mission function crosswalk](data/mission_function_crosswalk.csv)).
- **11** individually reviewed UN80 arrangements ([implementation status audit](data/un80_implementation_audit.csv)).
- **5** identified DPO support-account allocation lines, totaling **$95.4641m** proposed in 2026/27; this is **the same** DPO other-assessed component shown in Section 5 and must not be added twice.
- **13** budget-perimeter and source reconciliation rules plus **10** identified baseline changes ([cost bridge](data/cost_allocation_bridge.csv), [implementation cases](data/implementation_cases.csv)).
- Primary-source identifiers and links in [mission source extension](data/mission_source_extension.csv).

Mission years (July–June) are **different** from the calendar-year 2027 programme proposals. SG budgets are **not** approved appropriations. Published reductions are **not** proven operational savings. The combined DPO Peacebuilding and Peace Support Office allocation remains **not separately identifiable** in A/80/631.

Validate with `python3 scripts/validate_crosswalk.py && python3 scripts/validate_mission_audit.py`; alternatively run `Rscript scripts/analyze_mission_budgets.R` to reproduce gross proposal comparisons.

## Phase 3: GA appropriations, SPM addenda, and ranked investigations (8 October 2026)

**[Read the GA/SPM cost reconciliation and ranked research audit](docs/appropriation_spm_consolidation_audit.md).** The extension confirms **six** 30 June 2026 General Assembly financing authorities, registers **four** scheduled 2027 SPM addenda, preserves an unresolved **$4.9596m** SPM extrabudgetary conflict, and prioritizes **12** crosswalk-linked investigations.

**Critical limitation:** The adopted mission-level **dollar appropriations have not been independently read** from the operative GA resolutions or from A/C.5/80/20, so approved-versus-requested numerical variances remain explicitly **not calculated (0/6 verified)**. The SPM addenda financial tables remain unextracted (0/4). This is a **partial documentary reconciliation**, not a completed numeric reconciliation.

[GA financing authority CSV](data/ga_mission_reconciliation.csv) · [SPM addenda tracker](data/spm_2027_addenda.csv) · [SPM financial boundaries](data/spm_fiscal_boundary.csv) · [Ranked research priorities](data/ranked_consolidation_validation.csv) · [Auditor transition precedents](data/historical_transition_audit_cases.csv).

Run the standard validation script in the [CI workflow](.github/workflows/validate.yml); no net savings estimates are permitted in these early-stage datasets.
