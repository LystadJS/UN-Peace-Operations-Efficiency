# Systematic 2025–2026 UN peace-operations evidence census — 12 October snapshot

**As of 12 October 2026 | Public sources only | Financial duplication not established**

## Decision finding

**The Security Council source indexes are now captured systematically; publicly reported field and training activities are not a complete operational census.** The two official annual indexes yield **132 distinct Secretary-General report symbols** and **410 unique formal Security Council meeting IDs** (478 English meeting-record variants including resumptions). The 2025 meeting population of **255** matches the independent Security Council practice report; its **115 informal consultations** are a separate category and must not be counted as missing S/PV records.

A source-frame crawl of six mission/department news sites and prior discovered links yielded **1,708 distinct notice URLs**. **1,051 unique notice bodies were ever successfully downloaded across two archived crawls**, but only **524** were available in the latest, larger attempt; **1,184** article requests received HTTP 403 errors. **171** latest downloaded articles have masthead publication dates within the study window; reprocessing the **earlier 688 authenticated HTML pages** and deduplicating source URLs yields **376 distinct in-window published notices with non-conflicting dates**. Two headline/header year disagreements are flagged. The other notices cannot be treated as events that did not occur. These numbers concern *articles and index entries*, not distinct UN activities, courses, travel missions, attendees, staff workloads or invoice charges.

## Source populations, units and completeness

| Stratum | Observed records | Census unit | Coverage |
|---|---:|---|---|
| Secretary-General reports to Security Council | **132** (84 in 2025, 48 in 2026) | Document symbol | Official annual SG-report index, 2026 only through cutoff; not all Council document types |
| Formal Security Council meetings | **410** (255 in 2025, 155 in 2026) | Base meeting number | **478** S/PV record variants; formal meeting records only |
| Mission/department notice frame | **1,708** | Unique URL across six accessible site archives and prior seeds | 524 fetched in latest run, 688 in earlier run, **1,051 unique ever fetched**; 657 not retrieved in either |
| Machine-located field/meeting/training evidence | **848** | Article paragraph, **not event** | 194 training, 172 field activity, 640 meeting topic hits; categories overlap |
| Curated mission, field and training research records | **61** (55 previously reviewed, six additions) | Research activity/publication entry | 59 in-window or bounded within reporting week, **two exclusions**, not representative of total UN activities |

The complete strata and limitations are versioned in [coverage-by-stream](../data/census_v2/coverage_by_stream.csv). **No source gives a known denominator for all visits, field activities or courses actually delivered by the entities.** Hence this work is an audited *public source-frame census plus curated activity register*, not a certified complete field/training census. The 2025 Council's own [practice highlights](https://main.un.org/securitycouncil/sites/default/files/2026/Highlights_of_Security_Council_Practice_2025_0.pdf) confirm **255 formal meetings and 115 informal consultations**.

### Formal Council reports and meetings remain different deliverables

The [132-row report catalogue](../data/census_v2/council_reports.csv) and [478-record formal meeting variant ledger](../data/census_v2/council_meeting_variants.csv) separate document symbols, issue dates, Council meeting base IDs, resumption variants, topics and official index provenance. A 2025 report and a later Council briefing may use common facts, but they are *two products*: a meeting is not a duplicate SG report, and a resumed meeting record is not another independently convened meeting. Neither a common region, a coincident report date, nor a related agenda creates evidence of separately paid duplicate production.

The official 2026 SG index includes the anomaly **S/2026/513**, listed under 2026 but bearing **23 June 2025**. The register preserves its printed date and explicit year-mismatch flag rather than silently assigning it to 2026. [2025 official report index](https://main.un.org/securitycouncil/en/content/reports-submitted-transmitted-secretary-general-security-council-2025) · [2026 official report index](https://main.un.org/securitycouncil/en/content/reports-submitted-transmitted-secretary-general-security-council-2026).

## Article source-frame acquisition, recovery and access exceptions

The [news URL frame](../data/census_v2/notice_frame.csv) was assembled by bounded archive pagination from **UNOWAS, UNOCA, UNRCCA, UNAMA, DPPA and DPO**, plus earlier public seed/source URLs. The automatic collector fetched the Council source indexes and stored source-page SHA-256 fingerprints. The article-body acquisition results were:

| Measurement | First archived crawl | Expanded crawl | Combined, nonadditive |
|---|---:|---:|---:|
| Discovered news article URLs | 688 | **1,708** | **1,708** union-frame URLs |
| Successfully downloaded bodies | 688 | **524** | **1,051** distinct ever downloaded |
| Current HTTP 403 article failures | — | **1,184** | These are access failures, not absent events |
| In-window masthead-dated publications | **337** from the authenticated earlier HTML (two date conflicts excluded) | **171** from 524 current downloads (two date conflicts excluded in union) | **376 distinct non-conflicting in-window publications** after URL-level reconciliation |

The [fetch-lineage register](../data/census_v2/fetch_lineage.csv) preserves each URL's first/expanded download flags and SHA-256. The [688-row authenticated legacy date recovery](../data/census_v2/legacy_date_recovery.csv) and [1,708-URL reconciled publication chronology](../data/census_v2/union_dated_notice_coverage.csv) resolve **376** non-conflicting in-window publication dates across the two source sets; earlier and later publication-date evidence is preserved separately when conflicts arise. The [recovery summary](../data/census_v2/legacy_date_recovery_summary.json) documents **337** original in-window publications, **349** pre-window publications, and **two** title/header discrepancies. The [official original HTML artifact](https://github.com/LystadJS/UN-Peace-Operations-Efficiency/actions/runs/38314738551) contains first-crawl public article bodies; current output is from the [expanded crawl](https://github.com/LystadJS/UN-Peace-Operations-Efficiency/actions/runs/38316249220). Source bodies are not silently replaced by failed new requests.

**Publication-date correction.** The UN Drupal news pages generally expose their release dates in the article masthead rather than in machine-readable `article:published_time` elements. The fixed parser accepts the first dated masthead metadata item as a publication date, *never an arbitrary paragraph's event date*. Two **“This Week in DPPA”** pages have 2025 reporting periods in their headlines but 2026 masthead dates. Both exceptions are preserved in [date-quality issues](../data/census_v2/date_quality_exceptions.csv); they are not silently redated or counted as verified 2026 activities. The June/August/October article publication date and the event date remain separate fields wherever reported.

**UNRCCA's general news archive returned 404** during discovery. Prior known UNRCCA public notices remain in the source frame, but its full news history and unpublicized training calendar cannot be certified complete. The expanded site archives found more listing links, yet UNOWAS, UNOCA and UNAMA subsequently returned HTTP 403 on article requests. Thus counts of retrieved bodies are *not* coverage percentages of the true activity universe.

## Six newly adjudicated cooperative activities

Unlike the 848 unreviewed keyword-selected paragraph candidates, these six are manually checked against preserved original UN HTML, with source publication dates, named roles, an original source SHA-256 and bounded event-date precision in [verified joint additions](../data/census_v2/verified_joint_additions.csv).

| Case | Activity | Evidence of actual joint work | Legitimate shared-production question |
|---|---|---|---|
| **CJ001 — 24 July 2025** | UNOWAS/UNOCA/OHCHR civic-space dialogue, *L’Arbre à Palabres* | UNOWAS convened with UNOCA and OHCHR offices; approximately 150 participants | One consent-respecting event log and jointly reusable civic-space observations, regional reports kept distinct |
| **CJ002 — late Nov.–early Dec. 2025** | UNISFA–UNMISS police Strategic Guidance Framework review | Joint three-day workshop reported during DPO Police Adviser's 28 Nov.–1 Dec. Abyei visit; **exact workshop days not separately stated** | Versioned policing guidance and a common training-of-trainers evaluation, separate field policing responsibilities |
| **CJ003 — 25 March 2026** | UNOWAS–UN Verification Mission in Colombia women peacebuilders' virtual dialogue | UNOWAS, DPPA, UN Women, Colombia's embassy and Colombia Verification Mission organized one cross-regional dialogue of over 150 participants | Reusable women's mediation facilitation materials and knowledge-exchange format, adapted to local political contexts |
| **CJ004 — 8 July 2025** | UNRCCA/UNOCT early-warning network briefing, New York | Jointly hosted one Member-State briefing | A versioned common network source packet with time-specific briefing annexes |
| **CJ005 — 30 January 2026** | UNRCCA/UNOCT follow-up early-warning briefing | Jointly convened a second briefing at UN Headquarters | Maintain shared analyses without collapsing two separate consultation cycles |
| **CJ006 — week ending 5 June 2025** | UNRCCA/UNOCT Ashgabat OSINT/AI risk training | Joint course for approximately 30 officials | Reuse reviewed methodological modules and vendor/trainer administration; **actual course days unknown** |

Original dated sources: [DPPA civic-space weekly bulletin](https://dppa.un.org/en/news/this-week-in-dppa-19-25-july-2025), [UN Peacekeeping police workshop](https://peacekeeping.un.org/en/news/un-police-leadership-advances-strategic-guidance-framework-during-joint-unisfa), [UNOWAS women mediator dialogue](https://unowas.unmissions.org/en/news/empowering-peacebuilders-women-west-africa-and-colombia-lead-inter-regional-dialogue), [DPPA July 2025 bulletin](https://dppa.un.org/en/news/this-week-in-dppa-4-11-july-2025), [February 2026 bulletin](https://dppa.un.org/en/news/this-week-in-dppa-31-january-6-february-2026) and [June 2025 bulletin](https://dppa.un.org/en/news/this-week-in-dppa-31-may-5-june-2025).

These examples supplement, but do not duplicate, the previous **55 curated activity/publication items** or imply a statistically complete event population. A co-organizer is not an additional event; an attendee does not become an organizer merely because an entity appears in the same article.

## Prioritized additional shared-production opportunities

The [eight-item candidate register](../data/census_v2/shared_production_shortlist.csv) recommends the following **workflows** to investigate, not a merger of mandate owners:

1. **Joint civic-space and women-peacebuilding practice packets.** UNOWAS, UNOCA, OHCHR, DPPA and Colombia's mission already cooperate in different joint events. A common consent-aware source and participant-action register can serve multiple regions without making their reporting responsibilities identical.
2. **UNISFA–UNMISS policing standards.** One police guidance review was jointly delivered. Reuse vetted learning objectives, doctrine versions and evaluation questions while retaining distinct field, command, safety and readiness requirements.
3. **UNRCCA/UNOCT early-warning coordination.** The July 2025 and January 2026 network briefings and the separately delivered AI/OSINT course provide a controlled common factsheet/trainer-pool hypothesis; different dates, Member-State audiences and protected source material remain distinct.
4. **Shared event source, separate mandated report.** Use one canonical UNOWAS–UNOCA January Nigeria/Dakar event reference and where appropriate common underlying facts, but keep the separately issued S/2025/187 and S/2025/342 products, and different Council meeting records.
5. **Already joint DPPA–DPO guidance.** Preserve one controlled Mission Concept/Plan guidance and one peace-operations review product with traceable issuance, instead of counting each department as independently producing a second copy.

**Source-classification rule:** A common topic is merely a lead; *confirmed joint delivery* means the official dated record names the organizing or co-producing offices and identifies one event/product. *Verified financial duplication* requires two separately financed, legally substitutable cost objects and an independently checked continuation/transition cost. The latter remains **unverified in every case**.

The [32-category 2027 planned deliverable crosswalk](../data/public_deliverable_crosswalk_2027.csv) now includes candidate references to the six new activities. These are *related-workflow leads*, **not direct evidence of 2027 output identity**; the prior **20/32** categories with positively matched selected retrospective examples remain at their earlier accepted level. Neither the 14-parent consolidation rank nor the 23-level mission hierarchy is automatically changed by new topical evidence.

## Reproduction and release safeguards

- Run `python3 scripts/validate_census_v2_release.py` for 132/410 Council populations, 1,708 notice identities, provenance of both crawls, article date/cutoff controls, six curated cases, 32 comparator integrity checks and financial non-invention constraints.
- `scripts/expand_published_census.py` and `tests/check_published_census.py` generate and validate the bounded public-source frame. The first/expanded snapshots are source-frame populations, not certified complete delivered activity counts.
- The existing [retrospective field-training ledger](../data/systematic_field_training_canonical_2025_2026.csv) and [full earlier adjudications](retrospective_2025_2026_overlap_audit.md) remain versioned; existing rank and budget validation gates are unchanged.
- Fiscal and approval protection: SG proposals, ACABQ advice, adopted GA budgets, already priced efficiencies, support-service chargebacks, field activity dates and expenses are different units. No gross budget or expected efficiency is rebooked as new net savings.

**Release verdict:** The formal Council index source census is systematic within its defined report and S/PV boundaries; mission/department news collection is systematic at the **discovered URL frame** but remains incomplete at article-body and event-population levels. Public evidence identifies additional opportunities for shared production; **no separate duplicate paid service or new net financial saving has been established.**
