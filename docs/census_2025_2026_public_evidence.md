# 2025–2026 scoped UN peace-operations census

**8 October 2026 · Public records only · No verified incremental savings**

## Coverage

The [official Security Council Secretary-General report indexes](https://main.un.org/securitycouncil/en/content/reports-secretary-general) provide **79 unique report symbols for 17 selected peace-operations mandate series**: 46 in 2025, and 33 dated 2026 through 8 October. This is a census of the **selected report series**, not of all Council publications.

The separate [public activity inventory](../data/census_2025_2026_public_activities.csv) contains **49 canonical records**, including one October 2024 event excluded from the 2025–2026 period. It is **not a complete census** of meetings, field visits or training, since UN mission news archives are not a comprehensive activity ledger. See the [collection coverage matrix](../data/census_2025_2026_coverage_matrix.csv).

| Product | Records | Scope and limits |
|---|---:|---|
| [SG report symbol census](../data/census_2025_2026_security_council_reports.csv) | 79 | 17 selected mission/mandate series, identity verified against official yearly indexes; full report texts not all checked |
| [Activity/event collection](../data/census_2025_2026_public_activities.csv) | 49 | Officially published meetings, field visits, trainings and other products; 2024 negative control retained |
| [Council report identity screens](../data/census_2025_2026_report_pair_tests.csv) | 14 | Candidate pairs, preserving different legal mandates; no paragraph-level proof of reused text or duplicate cost |
| [Coverage limitations](../data/census_2025_2026_coverage_matrix.csv) | 5 | Declares source granularity and missing completeness |

Annual primary source indexes: [2025](https://main.un.org/securitycouncil/en/content/reports-submitted-transmitted-secretary-general-security-council-2025) · [2026](https://main.un.org/securitycouncil/en/content/reports-submitted-transmitted-secretary-general-security-council-2026).

## New public evidence

**UNAMA/UNRCCA:** The [28 April 2026 Preventive Diplomacy Academy session](https://unrcca.unmissions.org/en/news/unrcca-and-unama-engage-youth-in-preventive-diplomacy-academy-session-on-regional-peace) was jointly delivered to Central Asian and Afghan participants. It is a strong example for reusing course materials and event administration, **not evidence of two duplicate courses**.

**UNOWAS with external partners:** The [13–20 April 2026 Sierra Leone mission](https://unowas.unmissions.org/en/node/135074) was undertaken with **ECOWAS and the Commonwealth**; there is **no evidence that UNOCA co-led it**. The distinction prevents false overlap attribution from the presence of a shared regional mandate.

**Training attribution negative control:** The [3 December 2025 UNRCCA Academy session](https://unrcca.unmissions.org/en/news/preventive-diplomacy-academy-holds-online-session-intercultural-communication-diplomacy) featured a lecturer previously employed by UNAMA. Former employment **does not make UNAMA a co-organizer**.

## Report identity and reusable work

The 14 report-pair screens retain unique document symbols for Cyprus good offices versus UNFICYP, Lebanon resolution 1701 versus 1559 reporting, DRC regional PSC Framework versus MONUSCO, and UNOWAS versus UNOCA. An identical reporting date or shared geographic issue **does not mean an identical authorized final output**. The earlier [Dakar joint event](retrospective_2025_2026_overlap_audit.md) can provide common evidence to separate regional reports without eliminating either reporting obligation.

**Potentially reusable:** event IDs, safe source fact packets, joint itinerary and procurement administration, authorized common teaching materials, and reporting metadata. **Not yet proven reusable or removable:** protected country reporting, sanctions review, military observation, distinct Council reports, police specialist training, or substantive diplomatic mandates.

## Limitations and next collection

The 79 report entries are **symbol-level**; full bodies were not all downloaded or compared paragraph by paragraph. A complete Council meeting census needs official **S/PV** identities. A full field/workshop census needs audited mission calendars, not just news archives. Training cost savings require matched original event/contract/course IDs and safeguards for curricula and audiences. There are **no verified separately charged duplicate services** and **incremental net savings remain not estimated**.

Next public stage: download full texts for matched report pairs and reconcile 2025–2026 meeting symbols plus mission training/event calendars. Maintain independent legal mandate and no-double-count safeguards.

**Validate:** `python3 scripts/validate_census_2025_2026.py`.