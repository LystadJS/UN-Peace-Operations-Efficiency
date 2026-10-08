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

## Phase 5 — Transaction evidence and matching

All public transaction audit files are **control definitions**, not extracted private ledgers. No row in these files represents a verified invoice/asset movement.

| File | Row identity | Interpretation |
|---|---|---|
| `transaction_validation_cases.csv` | `case_id` | Three bounded reviews, public implementation evidence, 0 matched true transactions and unestimated savings. |
| `transaction_control_baseline.csv` | `control_id` | Twelve published monetary controls and embedded-efficiency IDs; distinguishes proposed spending, internal reimbursement and GA financing. |
| `transaction_offset_reconciliation.csv` | `check_id` | Five nonadditivity identities; do not subtract service scopes that differ. |
| `transaction_sources.csv` | `source_id` | Twelve source references with public evidence level and disclosure limits. |
| `transaction_evidence_requests.csv` | `request_id` | Eighteen internal finance/asset/HR data packages needed for adjudication; do not publish raw records. |
| `rsce_workforce_model_vs_post_actions.csv` | `line_id` | Nine RSCE modeling and staffing observations; FTE models, abolished client posts and transfers are distinct units. |
| `transaction_audit_issues.csv` | `issue_id` | Seven unresolved source/matching blockers and cost-base comparability tests. |
| `scripts/validate_transaction_controls.py` | — | Public source/budget integrity gate, no third-party dependencies. |
| `scripts/audit_transaction_ledger.R` | — | Local one-to-one asset/billing/settlement/chargeback reconciliation, no automatically estimated savings. |
| `tests/fixtures/transaction_ledger_SYNTHETIC.csv` | `record_id` | Engineering-only fixture; not UN invoice or asset evidence. |

Live transaction extracts must be handled in approved restricted locations and must never be accidentally committed to GitHub; `.gitignore` covers `data/private/`, `data/restricted/`, and `output/internal/`.


## Phase 6 — Public evidence and conditional model

The public decision layer does **not** contain operational finance transactions. Monetary amounts are published cost-scope controls (US dollars or US$ thousands as stated), not incremental savings.

| File | Primary key / content |
|---|---|
| [public_opportunity_register.csv](../data/public_opportunity_register.csv) | opportunity_id: 18 classified research options, parent crosswalk ID, source anchor, explicit amount class, legal risk, public action and later private-data gate. |
| [public_release_gates.csv](../data/public_release_gates.csv) | opportunity_id: source scope, implementation status, authority and financial release controls; none currently authorizes a cut. |
| [public_finance_nodes.csv](../data/public_finance_nodes.csv) | finance_id: 24 published control amounts, their fiscal period and funding status. |
| [public_finance_edges.csv](../data/public_finance_edges.csv) | edge_id: 21 parent/subset/alternative-period relations, including complete control sums and nonadditive memorandum efficiency. |
| [public_source_watchlist.csv](../data/public_source_watchlist.csv) | watch_id: nine current or future official review documents; publication confirmation kept separate from actual full-text recommendation extraction. |
| [render_public_decision_board.R](../scripts/render_public_decision_board.R) | Base-R reproducer for public decision board and queue, without restricted records. |
| [evaluate_conditional_options.R](../scripts/evaluate_conditional_options.R) | Scenario input: explicit *eligible recurring cost*, avoidance fraction, residual service cost, one-time implementation cost, year horizon, discount factor and mandate status. Outputs break-even share and assumption-based NPV; no verified savings. |
| [scenarios_SYNTHETIC.csv](../tests/fixtures/scenarios_SYNTHETIC.csv) | Artificial dollar inputs for unit testing only; they are not published UN costs or hypothetical estimates based on mission budgets. |

Source validation: python3 scripts/validate_public_only.py. Engineering tests: Rscript scripts/render_public_decision_board.R . /tmp/peace-public followed by Rscript tests/check_public_board.R /tmp/peace-public; repeat with evaluate_conditional_options.R and tests/check_public_scenarios.R. GitHub Actions executes all release gates.

## Phase 7 — Access-gated ACABQ and deliverable comparisons

| File | Scope |
|---|---|
| `restricted_transaction_request_spec.csv` | 18 requested finance, HR and asset datasets; *specification only*, no internal data. |
| `acabq_2027_report_status.csv` | Three officially indexed 2027 ACABQ reports and Cluster III publication status. Report bodies not retrieved. |
| `acabq_2027_mission_reconciliation.csv` | 36 SPM Secretary-General proposed mission amounts and intentionally empty ACABQ recommended numbers pending full reports. |
| `deliverable_unowas_unoca.csv` | 8 paired planned output types, 2027 activity values and exact Add.4 table locations. |
| `deliverable_unama_unrcca.csv` | 8 comparative planned activities in Afghanistan and Central Asia. |
| `deliverable_dppa_dpo_regional.csv` | 8 regional report, meeting, organization and desk comparisons. |
| `deliverable_training_comparison.csv` | 8 course/workshop and training-related comparisons, retaining distinct learner audiences and mandates. |
| `public_deliverable_crosswalk_2027.csv` | 32 combined source-linked records, with PDF links, numeric/non-numeric values and no-duplication classification. |
| `scripts/validate_phase7.py` | Automated integrity tests for 18 requests, 32 output comparisons, 36 SG mission values and unavailable ACABQ dollar recommendations. |

Financial eligibility remains *not estimated* in every deliverable pair. Source counts of planned 2027 activities are **not actual expenditure, staffing, or duplicated work**. Non-enumerated counts are not zeros.


## Phase 8 — ACABQ recommendations and ranked analysis

All `*_usd_thousands` fields are thousands of US dollars. Recommendations are **not General Assembly adopted**. Zero adjustment means ACABQ has recommended the existing amount unchanged *within the reviewed documents*, not that the mandate or resources can be cut.

| Dataset | Content and accounting meaning |
|---|---|
| `acabq_2027_source_manifest.csv` | 3 user-uploaded original PDFs, page counts, SHA-256 and document locators. Original binaries remain outside public GitHub. |
| `acabq_2027_mission_reconciliation.csv` | All 36 SG SPM mission requests, Cluster I/II ACABQ-adjusted recommendations (27 total), and explicit missing status for Cluster III (9). |
| `acabq_2027_cluster_reconciliation.csv` | Cluster I, II, III, RSCE, 27-reviewed subtotal and complete chapeau; **full adjusted SPM total not known**. |
| `acabq_2027_financial_actions.csv` | 12 budget-component recommendations: 4 in Cluster I (net −182.5), 6 under non-SPM Section 3 (net −189.3), 2 under regular Section 5 (net −26.7). |
| `acabq_2027_non_spm_reconciliation.csv` | Main A/81/7 2027 Section 3 excluding SPM and Section 5 SG versus ACABQ recommendation. Do not add these to the SPM cluster proposal. |
| `acabq_2027_qualitative_directives.csv` | 20 evidence-linked recommendations and implementation follow-ups; legal and programme risks. |
| `acabq_2027_ranked_consolidation.csv` | 14 revised **public review priorities**, preserving prior Phase 3 rank; never savings estimates. |
| `ranked_consolidation_validation.csv` | Baseline rank dataset refreshed with new rank, `old_phase3_rank`, 2027 ACABQ evidence and interpretation. |
| `scripts/validate_acabq_2027.py` | Acceptance gate verifying arithmetic across 27 reviewed SPM mission lines, 12 advisories, two non-SPM budget totals, 14 rank records, and source manifest. |

Use `--source-dir` for optional SHA-256 comparison with the three uploaded local PDF files, if available. No internal transactions are needed.


## Phase 9 — Cluster III original SG budgets and ACABQ main-report coverage

Units remain **US$ thousands**, except percent fields. **2027 SG original proposals** are not ACABQ advised amounts or GA appropriations.

| Table | Key, purpose, and financial boundary |
|---|---|
| `acabq_2027_clusterIII_sg_baseline.csv` | `spm_id`: 9 missions, 2026 approved against 2027 SG proposed regular funding, planned personnel and per-mission embedded efficiency IDs. `0.0` paired with `none_separately_identified` means **none listed in Add.4 Table 3**, not evidence of no realized savings. |
| `acabq_2027_main_crosscutting_framework.csv` | `framework_id`: 16 A/81/7 main-report statements classified by normative strength; none is a Cluster III mission-specific dollar adjustment. |
| `acabq_2027_clusterIII_crosscutting_map.csv` | `mapping_id`: 51 source-linked applicability judgments, not direct financial ACABQ recommendations. |
| `acabq_2027_conditional_envelope.csv` | `scenario_id`: original 2027 SG chapeau and purely mechanical **partial-advice carry-forward** (assuming unknown III/RSCE adjustments zero for arithmetic only). Never label second row as ACABQ approved or recommended. |
| `clusterIII_2027_research_priorities.csv` | `spm_id`: nine subordinate mission-level research work packages; rank is evidence readiness, not savings potential. |
| `consolidation_comprehensive_2027.csv` | `hierarchy_id`: 14 umbrella candidates plus nine **overlapping** child rows. **Never sum parent and child budget exposures.** |
| `acabq_2027_unissued_report_scope.csv` | `report_symbol`: missing Add.1 SPM-wide and Add.4 Cluster III advisory reports; provenance and non-inference contract. |

`scripts/validate_phase9_clusterIII.py` independently checks approved 2026 to proposed 2027 mission arithmetic (324549.9 to 325353.9), 19 prebudgeted initiatives summing to 14560.4, staff count changes, all 51 policy mappings, the 23-record hierarchy and the conditional scenario's non-official label.

## Phase 10 — 2025–2026 source-identified outputs and event reuse

All retrospective activity records are **selected published evidence** with actual dates or clearly marked month ranges. Matching evidence does not establish duplicate transaction payments.

| File | Key and meaning |
|---|---|
| `retrospective_2025_2026_sources.csv` | `source_id`: 42 official-source URLs, titles, dates when available, report IDs, precise source limitations and access type. |
| `retrospective_2025_2026_activities.csv` | `activity_id`: 38 analyst canonical event/output identities; one October **2024** workshop is explicitly excluded despite its practice note being published in April 2025. |
| `retrospective_2025_2026_matches.csv` | `match_id`: 36 adjudicated relationships across the four target comparisons. Evidence distinguishes joint event, participant-only, two distinct outputs, common input, and unverified resemblance. |
| `public_deliverable_crosswalk_2027.csv` | `output_pair_id`: original 32 2027 planned comparisons extended with actual 2025–2026 `MX...` references for **19** categories. Missing retrospective samples are not zero outputs. |
| `retrospective_2025_2026_summary.csv` | `pairing`: four descriptive, nonrepresentative group coverage rows; not a population duplication-rate estimator. |
| `retrospective_2025_2026_reuse_decisions.csv` | `case_id`: 11 ranked reuse/process tests, mandate caveats and required financial validation. |
| `retrospective_2025_2026_candidate_updates.csv` | `candidate_id`: seven overarching research candidates with linked selected match IDs, no claims of finance redundancy; ranks deliberately retained. |
| `scripts/validate_retrospective_matches.py` | Referential/temporal/source consistency and financial non-invention checks; standard library only. |
| `scripts/render_retrospective_board.R` | Base R public review queue and summary from current CSV data. `tests/check_retrospective_board.R` validates the generated artifacts. |

**Release restriction:** Published event identity or joint working does **not** certify duplicate cost, staff surplus, mandatory report removal, or net new savings. Source publication year must not replace original event year. Validated monetary savings remain `not_estimated`.


## Phase 11 — Systematic annual Council registry snapshot

**Index window:** 1 January 2025–8 October 2026. **Council report and meeting indexes are comprehensive relative to the published registry snapshot**, but full report texts, meeting transcripts, public field notices and training event population coverage are distinct tasks. Some registry metadata may contain anomalies and are preserved rather than silently corrected.

| File | Record identity and release limitation |
|---|---|
| `systematic_sg_reports_2025_2026.csv` | `document_symbol`: 132 official annual SG report index rows (84 in 2025; 48 in 2026 through as-of). Fields include source-link, mandate family and metadata mismatch flags. |
| `systematic_sc_meetings_2025_2026.csv` | `record_id`: 474 distinct S/PV document variant records, including resumptions. `meeting_base_id` identifies **255 unique 2025** and **151 currently indexed 2026** formal meetings. |
| `systematic_census_source_snapshots.csv` | `source_id`: four source URL/snapshot/digest metadata rows; distinguishes annual Council index content from subsequent edits. |
| `systematic_census_index_totals.csv` and `systematic_census_metadata.json` | Recorded 2025/2026 source totals and completeness; 2025 formal Council count 255, plus 115 **separate informal consultations**. |
| `systematic_council_reports_2025_2026.csv` | `symbol`: 78 **target-family report records** selected for priority DPPA/DPO and mission comparisons; not the full index. |
| `systematic_council_meetings_2025_2026.csv` | `source_id`: ten individually reviewed meetings/briefings (8 numbered and 2 number-unverified). Distinct from full official index. |
| `systematic_master_record_views_2025_2026.csv` | `item_id`: 132 report + 474 meeting-variant + 46 mission-activity **record views**, not independent fiscal or substantive outputs. |
| `systematic_field_training_activity_2025_2026.csv` | `activity_id`: 24 selected field, workshop, analytical and related records from original mission-activity sample; site archives are not exhaustively collected. |
| `systematic_census_coverage.csv` | `stream`: explicit source population and unresolved field/news completeness flags. |
| `systematic_council_meeting_population_benchmark.csv` | `statistic`: 2025 official formal public/private counts and consultations, 2026 missing full-year benchmark. |
| `systematic_council_report_pair_candidates.csv` | `pair_id`: 15 mandated reporting pairs for *actual content matching*; only one has confirmed common underlying source event so far. |
| `systematic_2025_2026_additional_matches.csv` | `match_id`: nine additional role-verified 2025–2026 activity and report/meeting checks; no monetary duplication claims. |
| `systematic_shared_production_options.csv` | `option_id`: 13 ranked, mandate-safe options for sharing inputs, curricula, events, and document provenance. |
| `collect_council_index.py` | Optional official index HTML/HTTPS **staging-only** parser; quarantines mismatched dates/future entries for human review. |
| `validate_systematic_census.py` | Validates source identities, official 2025 count, 2026 snapshot, year anomaly, 652-view registry, and no invented savings. |
| `render_systematic_census.R` | Base-R reproducible census and research-board summaries; engineering fixture tests in GitHub Actions. |

**Critical anomaly:** `S/2026/513` is listed in the 2026 index with an indexed date in **2025**. This is retained and flagged; do not count it as a verified 2026 chronology without inspecting its original document. **Do not combine the 78 target-family report count with 132 full-index records as if disjoint.**
