# Systematic 2025–2026 public-source census and shared-production audit

**Snapshot:** 8 October 2026 · **Scope:** Council reports and formal meetings indexed by official sources; selected mission news, field activities, and training releases · **No restricted financial transactions.**

## Executive assessment

**The Council-report and meeting indexes can now be reconciled systematically, while public field-activity and training reporting remains incomplete.** The official indexes contain 132 Secretary-General reports and 474 Council record variants across 2025–2026 through the snapshot date. After consolidating meeting record variants and resumptions, these correspond to **255 distinct formal meetings in 2025** and **151 indexed formal meeting IDs in 2026**. The first matches the Council's 2025 annual count, which separately reports **115 informal consultations**; these consultations must not be treated as missing formal meeting records.

The project also preserves **46 analyst-identified mission/department events or outputs**, including one event that took place in **October 2024** but had a practice note published in 2025. Therefore **45** of the event/output records occur in the specified 2025–2026 window. These 45 are **not a census of all UN field visits, meetings, or training events**, because entity sites lack a single comprehensive, stable public archive. The existing **36 adjudicated matches** and **nine supplementary matches** are selected source-supported comparisons, not a statistically representative duplication survey.

| Source stream | 2025 | 2026 through snapshot | Count and release limitation |
|---|---:|---:|---|
| Official Secretary-General report index | **84** | **48** | 132 unique published symbols; bibliography does not prove shared content |
| Security Council record variants, including resumptions | **296** | **178** | 474 record entries, **not** 474 distinct formal meetings |
| Distinct formal Council meeting IDs | **255** | **151** | 2025 official yearly denominator confirmed; 2026 is a partial index |
| Identified mission/department activities or output records | — | — | 46 selected records: 45 in scope, 1 historical 2024 control |
| Additional specifically adjudicated research cases | — | — | 9 new cases beyond the existing 36 selected matches |

Sources: [official 2025 SG-report index](https://main.un.org/securitycouncil/en/content/reports-submitted-transmitted-secretary-general-security-council-2025), [official 2026 SG-report index](https://main.un.org/securitycouncil/en/content/reports-submitted-transmitted-secretary-general-security-council-2026), [Security Council 2025 Highlights](https://main.un.org/securitycouncil/sites/default/files/2026/Highlights_of_Security_Council_Practice_2025_1.pdf), and official Council meeting record indexes tracked in the [source snapshots](../data/systematic_census_source_snapshots.csv).

**Important data-quality flag:** The 2026 annual SG-report index lists S/2026/513 with a **23 June 2025** date. The project retains the printed date and flags a year mismatch; it does not silently replace that date with 2026 or include it in a verified 2026 chronology.

## Defined scope and data layers

1. [**Council Secretary-General report census**](../data/systematic_sg_reports_2025_2026.csv): all rows extracted from the two official annual indexes at the project snapshot. The source index is a census of that *published registry*, not of every Council document, oral briefing or UN administrative product.
2. [**Council formal-meeting registry**](../data/systematic_sc_meetings_2025_2026.csv): official meeting and resumption records, with both original document symbols and base meeting identifiers. The independent 2025 benchmark is 255 formal meetings; the 115 consultations form a separate category. 2026 is an incomplete-year snapshot.
3. [**Mission activities**](../data/retrospective_2025_2026_activities.csv): published 2025–2026 field visits, workshop events, meetings, reports and guidance from mission/department sites. These are **not a complete site-wide enumeration**. Classification captures organizer, host, presenter and attendee separately wherever public sources support it.
4. [**Unified 652-row record-view registry**](../data/systematic_master_record_views_2025_2026.csv): 132 reports + 474 Council record variants + 46 mission records. **These are overlapping views, not 652 distinct UN substantive outputs or events**. Never sum different record grains as though they represented unique activities.
5. [**Focused research slice**](../data/systematic_council_reports_2025_2026.csv): 78 selected report symbols covering the priority peacekeeping/SPM/regional-office mandate families; [ten verified or partially identified Council briefings](../data/systematic_council_meetings_2025_2026.csv). Their earlier restricted scope must be read alongside, not instead of, the full Council indexes.

The [coverage controls](../data/systematic_census_coverage.csv), [full Council 2025 benchmark](../data/systematic_council_meeting_population_benchmark.csv), and [dated snapshot metadata](../data/systematic_census_metadata.json) prevent a partial field/training capture from being misrepresented as exhaustive.

## Activity identity: reported collaboration, reused material and duplicated work

**A single activity can appear in multiple reports and press releases without being produced twice.** The canonical event ID is anchored to date, place, organizer and event type; report document symbols and Council meeting IDs remain distinct identifiers. A publication date does not replace the underlying event date.

Previously validated examples remain the most defensible:
- **27–31 January 2025** — [UNOWAS/UNOCA joint Nigeria mission](https://unowas.unmissions.org/en/news/unoca-and-unowas-renew-their-joint-commitment-to-support-stabilization-and). The Lake Chad Governors Forum is nested inside the same mission, not a second five-day mission.
- **26–27 February 2025** — [Joint Dakar farmer–herder workshop](https://unowas.unmissions.org/en/news/west-and-central-africa-unowas-and-unoca-pool-their-efforts-to-strengthen-peaceful). Both S/2025/187 and S/2025/342 refer to this shared input, but remain separate mandated regional reports.
- **22 April 2025** and **17–19 February 2026** — joint UNRCCA/UNAMA academy and climate-security training (the latter organized by DPPA and UNSSC in cooperation with UNRCCA and UNAMA). These show existing shared delivery, not separate duplicated courses.
- **2025–2026** — DPPA/DPO joint peace-operations review, common Mission Concept/Plan guidance, and single integrated regional ASG Council briefings.

### New 2026 retrospective observations

- **28 April 2026:** [UNRCCA and UNAMA](https://unrcca.unmissions.org/en/news/unrcca-and-unama-engage-youth-in-preventive-diplomacy-academy-session-on-regional-peace) jointly engaged the 2026 Preventive Diplomacy Academy cohort, one event involving presenters from both offices. The [8 April Academy launch](https://unrcca.unmissions.org/en/news/unrcca-launches-2026-preventive-diplomacy-academy-with-online-opening-session) was a **different event**, even though it belonged to the same programme.
- **23 June 2026:** UNOWAS/UNODC held an emerging-drugs workshop in Dakar, as listed on the UNOWAS website. **UNOCA is not named as a co-organizer**; it must not be counted in the UNOWAS–UNOCA overlap census merely because the topic is regional.
- **6 October 2026:** UNOCA published an [Eastern Chad climate/security assessment](https://unoca.unmissions.org/en/news), a separately identified regional analytic product. No co-authoring by UNOWAS is established.
- **8 June and 16 September 2026:** UNAMA Council meetings **S/PV.10165** and **S/PV.10223** explicitly list reports **S/2026/431** and **S/2026/724** on their agendas. A report can inform a Council meeting, but the report and the official briefing are different deliverables; their content overlap is not separately demonstrated.

[Supplementary 2026 adjudications](../data/systematic_2025_2026_additional_matches.csv) record nine such checks, retaining actual co-organizer roles and distinct dates.

## Source comparisons that remain hypotheses

The [15 same-geography or proximate-report pairs](../data/systematic_council_report_pair_candidates.csv) are **candidates for full-text analysis**, not an assertion of redundancy. Illustrative comparisons:

| Paired mandates or offices | Actual source link | Result supported |
|---|---|---|
| UNOWAS vs UNOCA | S/2025/187 and S/2025/342 | Verified **common Dakar event**, two separate regional Council reports |
| UNFICYP vs Cyprus SG good offices | S/2025/447 vs 448; S/2026/8 vs 9; S/2026/550 vs 551 | Report symbols and sometimes dates coincide; **distinct mandated peacekeeping and political products** |
| MONUSCO vs Great Lakes Special Envoy | S/2025/590 vs 615; S/2026/748 vs 782 | Shared DRC context could support common source material; **no specific reused passage verified** |
| UNIFIL vs Lebanon resolution 1559 reporting | S/2025/460 vs 254; S/2026/160 vs 366 | Similar territory, but separate 1701 and 1559 tasks |
| UNISFA vs UNMISS | S/2025/269 vs 211; S/2026/378 vs 316 | Possible logistics coordination, but field-mission output identity not established |

Only the first pair has positively verified common underlying event reporting in the reviewed public documents. The other entries require actual full report text, paragraph/document references, source-of-fact attributions and compatible time windows before upgrading the evidence classification. Matching by date or geography alone cannot prove repeated work.

## Ranked public shared-production options

[**Thirteen source-linked options**](../data/systematic_shared_production_options.csv) are ranked by ability to examine or implement a **shared administrative/product workflow** without cancelling a mandate:

| Rank | Public review | Current evidence | Feasible reuse, subject to authority |
|---:|---|---|---|
| 1 | UNOWAS/UNOCA joint field work and Dakar event | Directly verified joint delivery | One canonical itinerary, participant registry and event source packet |
| 2 | DPPA/DPO Mission Concept guidance and peace-operations review | Already jointly produced | Common version-control, issuance and implementation tracker |
| 3 | UNRCCA/UNAMA shared academy and climate-security courses | Joint or cooperative training observed | Standard syllabus fragments, participant-role registry and common evaluations |
| 4 | Integrated DPPA/DPO regional Council briefings | One authorized briefing/speaker per event | One meeting-linked briefing/dossier tracker |
| 5 | West/Central Africa shared risk analysis | Active coordination and distinct local products | Controlled transregional source layer, separate final reports |
| 6 | UNRCCA/UNOCT AI–OSINT training series | Similar methods with different national cohorts | Reusable materials, training vendor calendar and trainer pool |
| 7–13 | Regional SG report-input reuse, country report/meeting links, Cyprus/DRC/Lebanon reporting, partner-specific workshops and academy events | Mix of verified, unverified and negative controls | Match unique inputs, **preserve separate formal products**, no monetary saving assumed |

This shortlist is a **work-sharing and future audit agenda**, not a recommendation to remove Council reporting responsibilities, specialized courses, operational mandates or diplomatic offices. The existing [14 broader consolidation investigations](../data/acabq_2027_ranked_consolidation.csv) remain separate and are not reranked merely because a topic-matched registry now contains more documents.

## Reproducibility and expansion

- Run `python3 scripts/validate_systematic_census.py` for the complete SG and meeting registry source snapshots, 2025 official Council meeting benchmark, resumptions, identity constraints, the integrated record views and explicit coverage limits.
- The [optional Council-index parser](../scripts/collect_council_index.py) accepts locally saved official HTML or an official live HTTPS index and writes **staging** rows with anomalies in an exceptions CSV. Staged records must receive human metadata review; they are not silently promoted to final findings. Its [offline synthetic test](../tests/check_council_index_parser.py) checks date mismatch and future-date exclusion.
- Generate a public review board using `Rscript scripts/render_systematic_census.R . /tmp/peace-systematic-census`, then `Rscript tests/check_systematic_census_board.R /tmp/peace-systematic-census`.
- Source data, acceptance tests and progress notes are versioned in GitHub. They do **not** contain restricted Umoja transactions or real-time personal movement information.

### Outstanding collection gaps

**Council SG reports:** annual report index ingestion complete as of snapshot, but full texts for the indexed universe were not paragraph-matched. **Formal Council meetings:** official index through the snapshot is available; the 2026 year is incomplete, and informal consultations are not part of this ledger. **Mission field visits and training:** only selected public mission/department records have been collected; exhaustive paginated searches and source-level inventories remain for future passes. **Cost of reuse:** no original invoice, purchase order, staff activity charge, event procurement payment or separately financed duplicate service was available.

**Release decision:** systematic source-identity census and selected actual-reuse proof strengthened; **no additional paid duplication or incremental net saving has been independently established**.
