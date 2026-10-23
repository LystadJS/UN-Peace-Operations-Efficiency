# ACABQ recommendation register — R07

The [register](../data/reforms/acabq_recommendations.json) consolidates **48 retained advisory records**: 12 financial actions, 20 qualitative directives and 16 crosscutting statements. It preserves every source row, paragraph locator, source-file hash and upstream primary-document receipt. Expectations, observations and actual recommendations remain distinguishable in their original statement fields. These records carry `ACABQ_ADVICE`; GA acceptance and implementation remain unestablished in this corpus.

This is a deterministic repackaging of repository extractions with an **8 October 2026 evidence cutoff**, assembled on 23 October. It is not a fresh legal review or an October 23 publication-status determination. The original PDF bytes are not present in this repository; their retained hashes have not been independently reverified by this step. See the [authority standard](source_authority_standard.md).

The retained numerical advice covers 27 of 36 SPMs: 12 Cluster I and 15 Cluster II. Nine Cluster III mission-specific recommendations, the separate RSCE SPM advice and a complete advice-adjusted SPM total remain unknown. General A/81/7 commentary cannot fill those gaps. Historical observations that Add.1/Add.4 were unavailable must be refreshed before making a current issuance claim.

| Advisory adjustment perimeter | 2027 USD thousands versus SG proposal |
| --- | ---: |
| SPM Cluster I | -182.5 |
| Non-SPM Section 3 | -189.3 |
| Section 5 regular budget | -26.7 |

These component controls are separate from the 36 mission coverage rows and must not be added to them again. The record includes both reductions and a +34.1 increase against the SG proposal; it preserves their signs. Cluster II has no further quantified adjustment in its retained advice, which does not establish efficiency. None of these advisory adjustments is an appropriation, avoided duplication cost, forecast saving or realized saving.

Reproduce with `python -B scripts/build_acabq_register.py --write`; verify with `--check` and `python -B tests/check_acabq_register.py`. The register's source snapshots preserve the historical interpretations for inspection rather than silently upgrading them into adopted obligations. Subsequent official-text verification and GA acceptance crosswalks must be separate evidence records.
