# V13: Research-reference adoption and affected-view recheck

**15 October 2026 | Research reference 13.0 adopted | Live use blocked**

## Decision

AM11-01 and AM11-02 are adopted under the user's explicit 15 October 2026, 20:58:38 UTC instruction. The new research reference contains the exact byte-identical V12 candidate payload; no additional substantive edits are made. The [adoption record](../data/census_v13/adoption_record.json) is the new version's authority and lineage record. This is project research authorization, not UN owner approval.

## Changes and affected views

| Amendment | Corrected reference | Affected view | Result |
|---|---|---|---|
| AM11-01 / V9:CY028 | Keep 202 information-exchange instances distinct from the exchange of three individuals in custody. The added 202 field aliases, rather than adds to, the inherited count. | [V9:G2 / S/2026/9](../data/census_v13/views/V9_G2.md) | Post-amendment rendering check passed. |
| AM11-02 / V9:CY041 | Explicitly retain more than EUR1.7 million since 2019, separately from approximately 67% of EUR1.5 million allocated for 2023-2026 as of June 2026. | [V9:G3 / S/2026/551](../data/census_v13/views/V9_G3.md) | Post-amendment rendering check passed. |

Source support remains the narrow V11/V12 review of S/2026/9 paragraph 18, page 3, and S/2026/551 paragraph 29, page 5. See the [retained source record](../data/census_v12/source_evidence.json) and [prepared patch](v12_reference_correction_patch.md). This adoption checks rendering, inherited qualifications and provenance against that already reviewed patch. It does not claim another source extraction, independent semantic review or whole-document audit.

## First pass versus amended recheck

The historical first pass remains **59 supported unchanged and two amendment holds** out of the fixed 61 obligations. Those historical outcomes are not rewritten. In reference 13.0, both amendments are adopted and their two affected assertions pass the separate post-amendment check. Their current amendment holds are therefore resolved for research use only. There is **no new 61/61 first-pass score**.

All 59 untargeted reference row objects remain identical. Only two affected product-specific sheets are generated: six selected obligations in G2 and eight in G3. Twelve of those assertions are carried forward unchanged, not substantively reassessed. The other ten views are not regenerated. The fixed inventory remains 64 source observations, 61 obligations and 12 product identities.

The [61-row lineage register](../data/census_v13/reference_lineage.csv) separates immutable first-pass dispositions from current research status. The [two-row recheck register](../data/census_v13/affected_recheck.csv) records exactly what was checked. Historical V8-V12 files, candidate-status records and original sources remain unchanged; their earlier statuses describe those historical versions, not the new adopted version.

## Controls and limits

Both SP08P1 and SP09P1 remain **BLOCKED_FOR_LIVE_USE**. Local activation fields remain unset and the nine V10 instruments remain empty. No owner clearance, live trial, staff measurement, course check, task scheduling, operational change or financial estimate is introduced. Mandates, approvals, parent and mission rankings, and the earlier 20/32 support count remain unchanged.

Checks cover exact V12 payload identity, guarded forward/inverse replay, two-row locality, first-pass lineage, action/unit and strict-lower-bound fidelity, rendered provenance and closed activation gates. Input hash checks are preservation controls, not fresh substantive review of unaffected claims. Rechecks are assistant-conducted with prior exposure, not independent human or institutional review.

## Reproduction and handoff

Run `python scripts/adopt_v13_reference.py --check` and `python tests/check_v13_reference.py` from the repository. The build option creates only missing V13 outputs and refuses drift in an existing release. It neither edits nor adopts older reference files. The [summary](../data/census_v13/summary.json) and [output hashes](../data/census_v13/output_manifest.json) describe this bounded release.

This completes the two-amendment research correction. The next substantive boundary is review by the existing workflow owners under the V10 protocol, not another automatic rehearsal or a live start. Neither successful checks nor research-reference adoption supply that authorization.
