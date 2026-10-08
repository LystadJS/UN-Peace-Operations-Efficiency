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
