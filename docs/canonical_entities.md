# Canonical entity identities — P01

[The registry](../data/portfolio/entities.json) defines 94 stable identities from nine retained budget, function, directive and transaction sources. It includes all 36 SPM budget entities, the eleven-entity assessed maintenance register, DPPA/DPO function labels, support-account allocation pools, RSCE, UNLB, observer missions and historical transfer references. DOS appears as a proposed evidence custodian whose authority requires verification.

Source keys and exact reviewed aliases are preserved with row/column provenance and input checksums. `UNSCOL` maps to `SPM031`; `BINUH` maps to `SPM035`. The good-offices mission in Cyprus remains distinct from `UNFICYP`. `UNSOH` remains distinct from `UNSOS`. Allocation SA04 remains a combined budget scope rather than two invented office costs.

All lifecycle states remain `UNKNOWN_NOT_VERIFIED`. Source dates and the retained evidence cutoff of 2026-10-15 do not establish present operational status. Shared office labels under DPPA and DPO remain department-scoped where identity is not verified. An ambiguous alias requires a department or source locator; consumers must never pick its first match. Aggregate client labels remain unresolved references with null entity IDs.

Relationships distinguish a source presentation from accounting inclusion. Mission appropriation shares for UNLB and RSCE are already included in the inclusive appropriation; the relationship cannot justify adding those shares again. Programme presentation does not verify operational hierarchy, exclusive ownership or implemented reform. This registry establishes identity for analysis, not legal authority.

Run `python scripts/build_canonical_entities.py --write` to regenerate and `--check` to verify. The generator validates ID uniqueness and alias/relationship targets and reports scoped alias ambiguity explicitly. Additional entity populations and lifecycle verification require a reviewed registry extension.
