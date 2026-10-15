# Seven transcript gaps recovered; weekly course checks established

**15 October 2026 | Original UN records | Prior census snapshots unchanged**

## Completed

**All seven missing original English Council records are recovered and authenticated: 187 pages.** The effective 14-link register now contains 13 explicit formal-agenda/presentation associations and one retained Council-discussion-only association. This closes document retrieval, not every possible substantive comparison.

| Original record | Meeting date | Paired SG report | Pages |
|---|---|---|---:|
| [S/PV.9931](https://documents.un.org/api/symbol/access?s=S/PV.9931&l=en&t=pdf) | 2025-06-09 | S/2025/342 | 18 |
| [S/PV.9942](https://documents.un.org/api/symbol/access?s=S/PV.9942&l=en&t=pdf) | 2025-06-23 | S/2025/372 | 30 |
| [S/PV.9998](https://documents.un.org/api/symbol/access?s=S/PV.9998&l=en&t=pdf) | 2025-09-17 | S/2025/554 | 28 |
| [S/PV.10060](https://documents.un.org/api/symbol/access?s=S/PV.10060&l=en&t=pdf) | 2025-12-11 | S/2025/772 | 19 |
| [S/PV.10165](https://documents.un.org/api/symbol/access?s=S/PV.10165&l=en&t=pdf) | 2026-06-08 | S/2026/431 | 39 |
| [S/PV.10195](https://documents.un.org/api/symbol/access?s=S/PV.10195&l=en&t=pdf) | 2026-07-14 | S/2026/537 | 22 |
| [S/PV.10223](https://documents.un.org/api/symbol/access?s=S/PV.10223&l=en&t=pdf) | 2026-09-16 | S/2026/724 | 31 |

[Original PDFs](../data/census_v7/originals) · [Recovery manifest](../data/census_v7/transcript_recovery.csv) · [Effective report–briefing links](../data/census_v7/report_briefing_links_effective.csv)

## What the recovered references establish

**Direct presentation:** S/PV.9931, S/PV.10060 and S/PV.10195 explicitly present their paired reports on printed page 2. The other four records explicitly identify their reports in the formal agenda/presidential introduction. These are document-specific links, not topic/date matches.

**Cross-office attribution:** On page 3 of S/PV.9931, the UNOCA briefer refers expressly to the earlier UNOWAS briefing, S/PV.9890, on the Niger withdrawal announcement. This strengthens the case for a shared, attributed regional evidence register while retaining separate regional analysis and Council outputs.

**Versioned updates:** S/PV.10223 page 2 refers both to the earlier briefing S/PV.10165 and to S/2026/724 for Badakhshan detail. S/PV.10165 page 4 also attributes border-closure impacts to S/2026/431. These referrals support shared factual inputs and controlled updates, not merger of the final products.

The earlier S/PV.10116–S/2026/99 relationship remains Council-discussion-only; it is not promoted to proven briefer dependence. [Eleven specified reference checks](../data/census_v7/recovery_content_checks.csv).

## Weekly official-source course watch

**The scheduled task is active for Friday mornings around 08:00 America/New_York, beginning 16 October 2026.** It monitors all eight unresolved cohorts in the frozen V6 register, using official UN and verified official host sources. No future check or new course completion is claimed at setup.

Notifications are conditional on material new completion, commencement, cancellation or rescheduling evidence, a resolved cohort-identity conflict, or a new material access blocker. Unchanged evidence remains silent. Advertised, opened, completed and certified stages remain separate. Korea’s conflicting programme dates must be reconciled; missing completion evidence is not evidence of cancellation.

Material findings are to be appended as dated, source-linked updates, with verified commits when repository writes are available. Frozen V5/V6 tables are not rewritten. [Watch contract and eight-cohort population](../data/census_v7/course_watch_contract.json).

## Recovery and validation

The prior recovery frontier admitted unrelated sidebar PDFs before reaching the symbol-specific viewer links. The revised collector uses exact-symbol official document-viewer links. The first V7 attempt accepted four records and withheld three on cover-text checks; its failure receipts remain under history. Removing extraction whitespace for identifier/date comparisons resolved those three without modifying PDF bytes or accepting wrong symbols.

pypdf verifies every original file, derived page-text hash and full text re-extraction in the recovery check. A second parser, PyMuPDF, independently verifies all seven cover symbols, dates, page counts and extractability across 187 pages. All covers and selected reference pages were visually inspected; not every page received visual or substantive review. [Independent checks](../data/census_v7/independent_pdf_checks.csv) · [Original failed attempt](../data/census_v7/history/first_summary.json).

Recovery is reproducible offline with `python3 scripts/recover_census_v7_layout.py`. Build the effective views with `python3 scripts/finalize_census_v7.py --write`; validate retained views with `python3 scripts/finalize_census_v7.py`.

**Unchanged:** mandated reports and briefings, parent/mission rankings, and 20/32 prior retrospective output-category support. No duplicate paid service or incremental net saving is established. Course completion remains an ongoing official-source verification task.
