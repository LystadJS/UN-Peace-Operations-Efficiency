# V12: Additive reference-correction patch

**AM11-01 and AM11-02 | 15 October 2026 | Prepared candidate, not adopted**

## Decision and status

The patch packages the two source-backed V11 amendment proposals into a reversible, hash-guarded candidate reference. It changes only the assertion text and adds qualified-value fields for **V9:CY028** and **V9:CY041**. It does not edit the original V8, V9, V10 or V11 records, adopt a reference, reopen scoring, or authorize live use.

Baseline repository commit: `2e8d5c6303d677f4c7fd797d6cd679309ce69f9d`.

| Quantity or permission | Preserved state |
|---|---|
| Source inventory / review population / product views | 64 / 61 / 12, unchanged |
| First-pass formulations supported unchanged | 59 |
| First-pass amendment holds | 2, still withheld |
| Candidate content changes | 2 rows; the other 59 row objects are identical |
| Adopted reference amendments / owner approvals / live trials | 0 / 0 / 0 |
| UNOWAS–UNOCA and Cyprus live-use gates | Both `BLOCKED_FOR_LIVE_USE` |
| Course watch | Paused; no checks or reactivation |
| Staff-time savings / cash savings | Not estimated |

The 59/2 split is a historical first-pass result, not a performance rate improved by this patch. No new 61/61 success claim is made. Publishing the patch files is not reference adoption or institutional clearance.

## Exact corrections

### AM11-01: preserve two actions, not just two numbers

**Target:** `V9:CY028`, obligation `OB:V9:CY028`, product `V9:G2`.

**Source:** [S/2026/9](https://documents.un.org/api/symbol/access?j=N2536009&t=pdf&i=S/2026/9_1768322702079), page 3, paragraph 18. The committee exchanged information in 202 instances and separately exchanged three individuals in custody. This corrects the research summary's compression of two actions; it is not an allegation of error in the UN report.

**Candidate assertion:** Through the Joint Contact Rooms, the Technical Committee on Crime and Criminal Matters exchanged information in 202 instances and separately exchanged three individuals in custody. These are different actions and units.

Add `custody_action = "exchange_of_individuals_in_custody"` and `information_exchange_instances = 202`. Preserve the inherited `count = 202`, `custody_exchange_count = 3`, distinct units and reporting period. The new information-count field is an explicit alias of the existing count, not an additional observation or additive count. No combined 205-item total is valid.

### AM11-02: render the strict lower bound and lifetime period

**Target:** `V9:CY041`, obligation `OB:V9:CY041`, product `V9:G3`.

**Source:** [S/2026/551](https://documents.un.org/api/symbol/access?s=S/2026/551&l=en&t=pdf), page 5, paragraph 29. The lifetime figure is strictly greater than EUR1.7 million since inception in 2019. The separately reported period-specific measure is approximately 67% of EUR1.5 million allocated for 2023–2026 as of June 2026.

**Candidate assertion:** Phase two was extended through 2026. By June 2026 approximately 67% of EUR1.5 million allocated for 2023-2026 had been utilized; more than EUR1.7 million had been utilized since inception in 2019. The two amounts have different perimeters and are not savings.

Add `lifetime_utilized_eur_comparator = ">"` and `lifetime_period_start_year = 2019`. Preserve the inherited lower-bound amount, approximate percentage, allocation, period, observation date and null savings field. This strengthens an existing lower-bound representation; it does not replace an allegedly incorrect amount. No exact lifetime amount, cross-perimeter utilization ratio, trend or saving is derived.

[Before/after differences](../data/census_v12/correction_diff.csv) retain the old formulations, proposed formulations, additive fields and before/after row hashes. [Affected support-sheet preview](v12_affected_support_preview.md) displays only the two changed assertions, separately from historical support sheets.

## Patch mechanics and audit trail

The [patch contract](../data/census_v12/patch_contract.json) pins the exact V11 `initial_candidate.json` and amendment-request file. [Forward operations](../data/census_v12/reference_delta.jsonpatch) contain identity, source-hash, old-text and old-values tests before each replacement. This is a JSON Patch test/replace subset; array positions are never trusted without their preconditions.

The generator replays the patch **in memory** and writes a [candidate preview](../data/census_v12/reference_preview.json) only into V12. It has no command that writes into the original reference or records adoption. A separate [inverse patch](../data/census_v12/reference_inverse.jsonpatch) restores the original row objects and exact field strings; it does not promise the original file's whitespace/serialization. Discarding the candidate layer is sufficient rollback because the baseline was never modified.

All original identifiers, locators, source hashes, attribution, required actions, prior qualified values and first-pass dispositions are retained. [First-pass lineage](../data/census_v12/first_pass_lineage.csv) keeps the two scoring holds explicit across all 61 obligations. The new field labels and prose are the only candidate changes; the fixed denominator has not been reselected.

## Verification and limits

The narrow source check uses the two retained original PDFs, matching their frozen hashes, with both PyMuPDF and pypdf extraction. The two relevant pages were also visually inspected during patch preparation. PDF-inserted spaces inside words are ignored only for source-clause location checks; no source text or substantive predicate is edited to make a test pass. Current browser retrieval of S/2026/551 and browser rendering of the first source were unavailable, so retained authenticated originals control the source review.

The tests cover exact change locality, inherited-value preservation, source/identity preconditions, stale and reordered inputs, repeat application, inverse replay, malformed patch operations, unintended rows, strict comparison loss, invalid count aggregation, first-pass lineage and closed activation gates. These checks test code and candidate representation, not independent substantive judgment. The source review remains assistant-conducted with prior exposure, not an owner or independent-human adjudication.

Existing mandates, approval chains, parent/mission rankings and the 20/32 retrospective support count remain unchanged. The nine V10 instruments stay empty. No staff workload, operational benefit, financial effect or real-world trial is measured.

## Reproduction and next boundary

From a checkout containing the pinned inputs:

```bash
python scripts/prepare_v12_patch.py --build --source-check
python scripts/prepare_v12_patch.py --check --source-check
python tests/check_v12_patch.py
```

The source-check option requires PyMuPDF and pypdf. Without that option, checks require only the Python standard library and verify pinned bytes, patch replay and generated outputs. The repository workflow also runs the retained Python/R acceptance suite. Generated outputs carry their own manifest; workflow logs provide the actual test-run evidence.

**Next boundary:** explicit adoption of a new research-reference version, followed by an affected-only recheck. Preserve the original 59/2 first-pass result and report any post-amendment result separately. Neither adoption nor a successful recheck opens a live-use gate. No message is sent to institutional owners by preparing or publishing this package.
