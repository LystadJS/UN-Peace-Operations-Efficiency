# Extended 2025–2026 mission and training census: official source evidence

**Evidence cutoff: 13 October 2026.** This is a bounded archive-source extension with manually adjudicated public events, published training-course listings, and explicitly incomplete field/training population coverage. It supplements the [12 October Security Council and public-notice census](systematic_2025_2026_census_oct12.md); the earlier validated datasets remain separate and reproducible.

## Executive assessment

The enlarged source frame makes **18 additional distinct activity or delivered-cohort identities** available for source-level investigation, alongside **nine official course offerings or learning-resource listings that do not themselves verify delivery**. The strongest cases for better shared production are an already joint **UNITAR–DPO Integrated Training Service (ITS)** predeployment training-of-trainers course, a **MONUSCO–UNDP** co-financed justice-coordination workshop, **two different MINUSCA–UNDP workshops** on the same day, a **UNISFA–UNMISS** joint policing standards review, and complementary **UNMISS–UNDP** mobile-court support.

Separately, **General Assembly resolution A/RES/80/306**, adopted 3 September 2026, approved integrating UNSSC into UNITAR as UNICLI, targeted to take effect on 1 January 2027. This is **already authorized institutional reform**, not an additional merger idea or proven new saving. Any implementation assessment must retain the roles of DPO ITS, protected specialist training, and the mandates of individual field missions.

**Release conclusion:** More actual joint delivery and opportunities for common administrative production are documented. **No separately financed duplicate service, redundant mandated final output, or independently verified additional net saving was established.**

## Source-frame coverage and limitations

An automated [bounded nine-archive source-index scan](../scripts/collect_extended_official_archive.py) attempted three pages per archive and retained original listing URLs, page-fingerprint SHA-256 hashes and HTTP failures. A URL, card, course page, news notice, training event and unique operational event are **different analytic units**.

| Additional official source | Pages downloaded / attempted | New discovered source URLs |
|---|---:|---:|
| UNISFA news archive | 3 / 3 | 36 |
| UNMISS news archive | 3 / 3 | 36 |
| MONUSCO general news-articles archive | **0 / 3** (404) | 0 |
| MINUSCA news archive | 3 / 3 | 10 |
| UNSSC course catalogue | 3 / 3 | 56 |
| UNSSC events calendar | 3 / 3 | 10 |
| UNITAR news and story archive | 3 / 3 | 30 |
| UNITAR training catalogue | 3 / 3 | 36 |
| UN Climate Security Mechanism news | 3 / 3 | 35 |
| **Total** | **24 / 27** | **249** |

The **249 additional exact source URLs do not overlap** the previously enumerated **1,708 URLs**, giving **1,957 distinct discovered links** across the two source frames. The new 249 are **listing-level records**; their publication year, actual event delivery and exact event dates were not systematically validated by the listing collector. The earlier 1,708-URL exercise recovered **1,051 full notice bodies** and **376 non-conflicting in-window article publication dates** after source recovery. Neither number is a completed-event population denominator.

Specific MONUSCO reports were obtained and adjudicated using separately discoverable official URLs despite the failure of its generic archive; its absence from the new URL frame is **not evidence of no activities**. An additional problem is that archive pagination is bounded at three pages, not exhaustive. The source files are [archive page access](../data/census_v3/archive_page_access.csv), [249 indexed links](../data/census_v3/archive_discovered_url_frame.csv), and [collection summary](../data/census_v3/archive_collection_summary.json). **Do not use source-listing counts as a coverage percentage for actual UN field missions or training.**

## Canonical event/cohort reconciliation

The [18-row new canonical record table](../data/census_v3/extended_canonical_activities.csv) distinguishes event date from publication date, precise organizer/contributor roles, course audience, source URL, and approval/mandate restrictions. Temporal evidence is graded as follows:

| Temporal grade | Records | What the source supports |
|---|---:|---|
| **A — explicit activity day or range** | 7 | Specific day/range explicitly identified; same-day events may still have different identities |
| **B — delivered cohort within 2025 Q1** | 5 | UNITAR quarterly reporting establishes a delivered cohort but not exact teaching days |
| **C — activity bounded by publication date** | 6 | An event was reported, completed or underway by the publication date, but its exact first/last day remains unverified |

These grades do **not** mean all 18 are 18 exact-day completed events. **XEV002** reports UNMISS police training underway in Bor, rather than verifying its completion.

### Publicly documented delivery and non-duplication cases

| Source evidence | Canonical decision | Shared-production relevance |
|---|---|---|
| **MONUSCO–UNDP**, Bunia, 18–19 December 2025 | **XEV006:** jointly organized **and co-financed** justice-support coordination workshop; not a redundant second event | Investigate one procurement/event ledger, existing agreed cost sharing and possible common administrative services; co-financing is **not** proof of two invoices for the same service |
| **MINUSCA–UNDP**, Bangui, 26 November 2025 | **XEV009 and XEV010:** two workshops on international disarmament instruments versus disability-accessible elections; **separate identities despite identical dates** | Consider shared event logistics, not duplicate curricula or pooled participant counts; 25 attendance is reported in aggregate and cannot be assigned independently to each |
| **UNMISS UNPOL**, Warrap/Bor/Leer, 2025–2026 | **XEV001–003 and XEV008:** different county, audience or specialist objective; Bor electoral-security training was only **underway** at publication | Standard competency IDs and shared preparation where appropriate; retain police investigations, electoral security and court-work support as separate outcomes |
| **UNMISS–UNDP**, Bor mobile court, reported December 2025 | **XEV007:** UNDP-backed court support and UNMISS technical assistance, with national judiciary responsible for adjudication | Compare complementary service and travel planning but preserve independent court authority |
| **UNISFA–Concordis**, Abyei, reported February 2025 | **XEV004:** community law-and-order workshop | Reuse eligible community engagement methods; local customs, mandate, and conflict-sensitivity safeguards remain |
| **MONUSCO**, Beni, 17–19 June 2025 | **XEV005:** civilian protection workshop producing one coordination roadmap | Reuse agreed inputs/participant follow-up, not regional protection mandate elimination |
| **UNITAR with DPO ITS/IPSTC**, Nairobi, 2025 Q1 | **XEV012:** delivered Core Pre-Deployment Training Materials ToT (23 participants), distinct from an advertised Seoul offering **CAT001** | One versioned peacekeeping core curriculum and trainer evaluation; DPO ITS retains standards and direction |
| **UNITAR/DPO**, Stockholm corrections training, 2025 Q1; **UNITAR/Swedish Police Authority**, Dodoma women leadership, 2025 Q1 | **XEV013–014:** two separately reported delivered specialist cohorts | Shared training administration where feasible, distinct corrections and women police competencies |
| **UNITAR** special-envoy leadership seminar and Asia-Pacific programme, 2025 Q1 | **XEV017–018:** distinct audiences and programmatic purposes; some DPPA collaboration reported, not automatically cohosting | Reusable anonymized negotiation case materials; preserve confidential good offices |
| **UNSSC/Climate Security Mechanism**, March 2025 | **XEV011:** one data-analytics **module launch**; associated **XOUT002** resource is a distinct publication/learning asset | Single controlled public module with shared generic analytical materials; a launch is not multiple training deliveries |
| **Climate Security Mechanism**, NYC 27 and 29 April 2026 | **XEV015–016:** two different climate/security consultations with different conveners/outcomes within one themed week | Shared factual packets; retain distinct meeting and policy deliverables |

Official primary records include [MONUSCO–UNDP justice workshop](https://monusco.unmissions.org/en/actualites/ituri-la-monusco-et-ses-partenaires-veulent-renforcer-la-lutte-contre-limpunite), [MINUSCA November 2025 Human Rights Division report](https://minusca.unmissions.org/sites/default/files/2026-01/hrd_monthly_report_-_november_2025.pdf), [UNMISS police courses](https://unmiss.unmissions.org/en/news/south-sudan-police-officer-turns-unmiss-training-real-results-victims-crimes-bor), [UNITAR Division for Peace Q1 2025 performance report](https://unitar.org/sites/default/files/media/file/Quarterly%20Report%201%20-%202025%20-%20Division%20for%20Peace%20-%20UNITAR.pdf), [UNSSC module launch](https://www.unssc.org/events/practical-approaches-climate-peace-and-security-programming-repository-launch-new-data), and [Climate Security Mechanism's April 2026 meeting roundup](https://www.un.org/climatesecuritymechanism/en/news/roundup-informal-new-york-climate-peace-and-security-week-27-april-1-may).

### Existing canonical identities verified again — not new events

The [16 adjudicated identity tests](../data/census_v3/reconciled_event_and_course_identities.csv) explicitly map repeated sources to prior event IDs:

- **CJ002:** official UNISFA and DPO descriptions concern the same joint UNISFA–UNMISS police Strategic Guidance Framework review; the workshop's exact days inside the visitor's 28 November–1 December travel window remain unverified.
- **EV037, EV020:** UNSSC records corroborate the earlier Turin climate-security programming course and Ashgabat UNRCCA–UNAMA workshop. Do not count a second event from a second publication.
- **EV036:** UNMISS/UNPOL climate-security policing syllabus is a *published resource*, not an additional delivered police course.
- **EV038:** October **2024** UNOCA/DPPA/DPO/UNSSC Gabon workshop, published in a 2025 practice note, remains explicitly excluded from 2025–2026 **event** counts.
- **EV003:** UNOWAS–UNOCA Dakar workshop remains a single activity supporting separately mandated regional reports.
- Two distinct same-day MINUSCA workshops, or two climate-security meetings inside the same April 2026 themed week, remain two distinct outcomes, **not apparent duplicates**.

## Actual courses versus published calendars

The [nine official UNITAR/UNSSC course and resource listings](../data/census_v3/official_training_calendar_listings.csv) are preserved as **CAT001–CAT009**. They establish advertised training options and resource availability **only**; a registration page alone does not establish that a class occurred, anyone attended or a UN cost centre paid. Examples include the UNITAR Seoul training-of-trainers offering (not a second Nairobi course), advertised MONUSCO predeployment class dates, UNSSC conflict-analysis and data/AI courses, specialist children-and-armed-conflict training, and an open climate-security resource repository.

**CAT003 unresolved date anomaly:** UNITAR's Gako Rwanda catalogue title says **6–7 January 2025** while a date field extends from **6 January to 7 February 2025** despite a listed two-day duration. The records preserve both and do not invent the actual instruction dates. Advertised course fees are **prices**, not UN invoices or avoided expenditure.

Published aggregate statistics also have separate denominators: UNITAR's Q1 2025 report lists **21 training events and 1,593 trained people** across its *entire Division for Peace programme*; its reported Tanzania Peacekeeping Training Centre activities reached **1,494** people across multiple 2025 programmes; MINUSCA's November report describes broader activities; an UNSSC account of a DPO course does not establish its exact event year. See the [four aggregate-protection controls](../data/census_v3/source_population_aggregate_controls.csv). None of these totals may be added to the 18 curated event/cohort cases.

## Authorized reform and updated worksharing decisions

[**A/RES/80/306 and UNICLI baseline**](../data/census_v3/ga_authorized_training_reform.csv) records the **3 September 2026 GA authorization** for the UNSSC–UNITAR merger, targeted for 1 January 2027. That is **pre-existing UN80 reform**, so no project candidate may claim a new merger, a realized post-2027 institutional result, or an independently verified net saving. DPO's Integrated Training Service remains a legally and operationally distinguishable source of peacekeeping training policy and technical standards.

The [12-case ranked production register](../data/census_v3/shared_production_recommendations.csv) prioritizes: (1) UNICLI implementation governance and course identity controls; (2) UNITAR–DPO ITS common predeployment curriculum; (3) MONUSCO–UNDP shared justice-event contracting; (4) MINUSCA–UNDP common logistics for separate workshops; (5) UNISFA–UNMISS shared police guidance; (6) a controlled UNSSC–CSM climate analytics learning library; then complementary UNMISS–UNDP mobile-court support, catalogue-versus-actual course reconciliation, envoy/regional diplomacy learning, local policing course administration, April CPS meeting source reuse, and previously verified UNOWAS–UNOCA shared fact packages.

**Do not conflate** curriculum reuse with identical qualifications; common event facts with interchangeable UNOWAS/UNOCA Security Council reports; joint financing with duplication; existing shared staff with separately paid output; or prior GA-authorized reform with incremental saving. Each recommendation explicitly records **mandate preservation**, **financial duplication not established**, and **incremental savings not estimated**.

The older 32-row [2027 planned deliverable crosswalk](../data/public_deliverable_crosswalk_2027.csv) is annotated with new event IDs but its **20/32 previously supported selected retrospective output categories remain unchanged**. The 14-parent [consolidation ranking](../data/acabq_2027_ranked_consolidation.csv) retains its order because the new source collection is not a representative activity-population survey and has no verified net financial impacts.

## Replication and release boundary

Run `python3 scripts/validate_census_v3_extension.py` for public-source link identities, 24/27 page access, 249 source URLs, 18 temporal-graded canonical records, nine non-delivered catalogue entries, 16 source-to-event checks, the GA-authorized UNICLI state, 32 untouched baseline comparison denominators and 12 mandate/finance-safe options. Rerun the bounded source frame with `python3 scripts/collect_extended_official_archive.py --max-pages 3 --workers 4`; **the live listing source may change**, so compare new outputs with the dated frozen snapshot, not silently overwrite adjudications.

**Unresolved:** MONUSCO generic archive 404, deeper index pagination, public notice dates versus actual course days, enrollment/completion and published curricula, non-public field/training calendars, and unique paid procurement/service records. A full delivered-event denominator is unknown. All 18 new records are documented source cases but **not a complete census of every 2025–2026 UN training, meeting or field operation**. No reductions to mandated products, staff or verified incremental savings can be recommended on the available financial evidence.
