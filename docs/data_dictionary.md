# Data dictionary

The files use UTF-8, RFC 4180-style quoting, one header row and an immutable primary key in the first column.

| File | Key | Contents and important fields |
|---|---|---|
| `source_manifest.csv` | `source_id` | `S03` and `S05`; publication date, PDF page count, SHA-256 of supplied files, official locator, scope. |
| `mandate_inventory.csv` | `mandate_id` | Instrument, recorded DPPA/DPO source anchor, `shared_in_sources` versus uniquely recorded; not a full jurisprudential legal analysis. |
| `functional_inventory.csv` | `function_id` | `F...` DPPA or `G...` DPO, named unit, function category, supporting source and 1-based PDF page. |
| `deliverable_inventory.csv` | `deliverable_id` | `D...` DPPA or `P...` DPO, source table/page, counted output, units, **2025 actual**, **2027 planned**. |
| `crosswalk.csv` | `crosswalk_id` | `CW...` functions on both sides, classification, supporting numbered paragraphs/tables and pages, test question, safeguard and evidentiary type. |
| `un80_register.csv` | `reform_id` | `U...` reform, type, both document anchors, exact characterization, unverified implementation and test required. Not every row describes a UN80 reform. |
| `candidate_validation.csv` | `candidate_id` | `C...` initial research priority, linked crosswalk IDs separated by semicolons, test, potential future option, requisite evidence, safeguards. |
| `non_overlap_controls.csv` | `control_id` | `N...` explicit examples of mandate and function distinctions. |
| `quality_issues.csv` | `issue_id` | `Q...` source inconsistencies, budget boundaries and analysis blockers. |
| `financial_guardrails.csv` | `record_id` | `B...` sourced 2027 amounts in USD, at stated accounting perimeters, without any savings interpretation. |
| `evidence_links.csv` | `evidence_id` | `E...` official locator and PDF page for each mandate/function/deliverable and each side of every crosswalk pair. |

## Classification counts (39 comparisons)

`documented_shared_structure` = 7; `documented_joint_process` = 2; `planned_coordination` = 7; `candidate_overlap` = 9; `complementary_different_roles` = 9; `distinct_mandates` = 5.

## Notation and interpretation

- `-`: not applicable, or no identified specific parallel record; **not** missing-at-random quantitative data.
- `pdf_page`: physical 1-based PDF page, not printed internal UN paragraph numbering.
- `3.I.11` and `5.I.9`: paragraphs in the source document, not evidence record identifiers.
- `Table 3.I.4`: reference to published UN table (not local dataset table).
- `implementation_verification`: claim about evidence availability, not a certification that an office functions as proposed.
- `priority`: value of investigative action, not expected cost savings.
- `savings_status = not_estimated`: **unknown**, never zero.
- All monetary values in `financial_guardrails.csv` are exact dollar translations of the source tables reported in **thousands** of USD.

Source links in `evidence_links.csv` are constructed from official UN locators. They may open a document landing page rather than directly selecting a PDF page for platforms that suppress fragment identifiers. When that occurs, use the cited document symbol and page manually.

## Phase 3 research extensions

- **ga_mission_reconciliation.csv:** one mission-to-GA financing decision row with SG request, adoption evidence and an explicit textual placeholder for missing official adopted-dollar amounts. GA authorization **identity** verified; numerical reconciliation intentionally open.
- **spm_2027_addenda.csv:** identifies A/81/6 (Sect.3)/Add.1–4 and available ACABQ linkage, without invented cost allocation.
- **spm_fiscal_boundary.csv:** three separate 2027 SPM source amounts (regular provisional and two conflicting extrabudgetary estimates).
- **historical_transition_audit_cases.csv:** two historical Board of Auditors risk exposures; no assumption of avoidable costs or recovered savings.
- **ranked_consolidation_validation.csv:** ordered research priorities linked to original candidate IDs; the amount is the published *full organizational/funding scope*, if available, not redundant spending or savings. Strings not_costed/not_estimated are NOT zeros.


## GA approved 2026/27 financing (verified source layer)

Amounts are **USD thousands** and cover **1 July 2026–30 June 2027**. **Mission maintenance** is not the same as **GA inclusive appropriation**. The latter includes maintenance + support-account share + UNLB + RSCE.

| Dataset | Key and purpose |
|---|---|
| `ga_mission_reconciliation.csv` | `mission_id`: six approved mission-maintenance budgets and their GA-inclusive appropriations. `adopted_minus_proposed_usd_thousands` compares **GA maintenance** minus **SG original maintenance request**, not inclusive GA appropriations. |
| `ga_approved_resource_components.csv` | `component_id`: 102 components; 3 main maintenance categories, 10 operational *subcategories* (already within the operational parent), 3 corporate shares, and 1 inclusive appropriation for each of 6 missions. **Do not sum across hierarchies**. |
| `ga_approved_all_missions.csv` | `mission_id`: 11 maintenance amounts from the A/C.5/80/20 approved resource note. |
| `ga_apportionment_schedule.csv` | `segment_id`: 11 apportionment segments, including conditional post-extension periods; **not cash collected**. |
| `ga_unmiss_abolishments.csv` | `abolition_record`: 91 GA-approved civilian post/position abolishments including 53 electoral; not prospective savings. |
| `ga_adopted_directives.csv` | `directive_id`: 15 specific GA operative directives supporting activity and risk audits. |
| `approved_document_manifest.csv` | `source_id`: SHA-256 of 7 uploaded UN PDFs with official symbol URLs and source locations. Original PDF binaries are not republished here. |
| `ranked_consolidation_validation.csv` | `candidate_id`: 14 research investigations ranked by audit feasibility/urgency, **not potential savings**. |

Run `python3 scripts/validate_phase3.py` to verify schema, source IDs and financial arithmetic; supply `--source-dir /directory/containing/seven/PDFs` for byte-for-byte SHA validation.

## Phase 4 — 2027 special political missions

The four addenda are **calendar-year 2027 Secretary-General proposals**. All SPM dollar values in CSVs are **US$ thousands, net of staff assessment** except separately identified extrabudgetary revenue estimates. They are not approved 2027 appropriations and must not be summed directly with July–June 2026/27 assessed peacekeeping appropriations.

| Data table | Unit and interpretation |
|---|---|
| `spm_2027_mission_budget.csv` | 36 missions. 2025 appropriation/expenditure, **2026 approved**, **2027 proposed**, proposal change, personnel counts and citation to relevant detailed cluster Table 1 and Table 2. |
| `spm_2027_cluster_bridge.csv` | 3 clusters, discontinued 2026 budget base, and 2027 RSCE SPM share. Sum each top-level component exactly once to $422.671m. |
| `spm_2027_closure_bridge.csv` | UNAMI, UNTMIS and UNMHA 2026 approved funding, mandate closure and recipient of residual functions. Already mandated baseline changes. |
| `spm_2027_financing_controls.csv` | Chapeau accounting boundaries; original preliminary estimate, revised proposal, RSCE support allocation, older XB figures and pre-booked efficiencies. |
| `spm_2027_embedded_efficiencies.csv` | 31 proposed 2027 initiative estimates totaling $14.6925m **already counted within SG proposed funding**; cannot be added to incremental savings. |
| `spm_2027_extrabudgetary_items.csv` | 17 explicitly cited projected voluntary-contribution or cost-recovery rows totaling $32.976673m at published precision. |
| `spm_2027_extrabudgetary_coverage.csv` | 36-mission explicit amount / explicit zero / not separately reported classification. Missing is never zero. |
| `spm_2027_cross_pillar_links.csv` | 16 evidence-anchored SPM-to-SPM/GA-peacekeeping/shared-service relationships with a cost boundary and classification. |
| `spm_2027_validation_sequence.csv` | 12 prioritized document-and-operations audits, not a ranked list of cuts or avoidable cost estimates. |
| `spm_2027_source_manifest.csv` | Four uploaded original PDFs, symbol, page count, SHA-256 and reissue date. |
| `spm_2027_source_discrepancies.csv` | Seven discrepancies maintained transparently, including 2027 UNOWAS, 2026 RSCE and XB amounts. |
| `spm_2027_extrabudgetary_reconciliation.csv` | Derived $32.976673m item sum vs roughly $33m chapeau and original Section 3 figures. |

`scripts/validate_spm_2027.py` verifies financial controls, 36 mission rows, 31 efficiency rows, 17 XB entries, staffing definitions, legal classifications and crosswalk relationships.
