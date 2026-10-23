# A01–A06 — Repository control audit

This wave establishes the inventory and design evidence needed before canonicalization, migration or CI consolidation. It does not execute A07–A14, change historical data, designate all datasets canonical, migrate issues, or modify existing workflows.

## Scope

The [frozen scope](../metadata/repository_audit_scope.json) records **554 input files** at baseline commit `32f02e5e689ad9f43e762d5985330df20dda1719`: 543 tracked repository files and 11 pre-existing, untracked F01–F06 additions. It includes **324 CSV/JSON files** and **28 Actions workflows** (the original 27 plus the foundation workflow). The metadata snapshot and A01–A06 outputs are excluded from their own input population. Ignored files, Git internals and scratch work are also excluded. Future additions require a new scope version, rather than a silently changing denominator.

Each input has a SHA-256, byte size and tracked-at-snapshot flag. The integration check verifies the original bytes, exact-once inventory coverage, CSV/JSON registry coverage and workflow coverage. Presence in this scope is not a designation of current analytical authority.

## Products

| ID | Product | Read first | Machine-readable result |
| --- | --- | --- | --- |
| A01 | Artifact inventory | [Inventory guide](artifact_inventory.md) | [All frozen artifacts](../metadata/artifact_inventory.csv) |
| A02 | Dataset registry | [Dataset guide](dataset_registry.md) | [Dataset registry](../metadata/dataset_registry.csv) |
| A03 | Repository status model | [Status model](repository_status_model.md) | [Status schema](../metadata/repository_status_schema.json) |
| A04 | Static lineage graph | [Lineage guide and gaps](repository_lineage.md) | [Nodes](../metadata/lineage_nodes.csv), [edges](../metadata/lineage_edges.csv) |
| A05 | Master issue model | [Issue model](master_issue_model.md) | [Schema](../metadata/master_issue_schema.json), [legacy field crosswalk](../metadata/issue_register_crosswalk.csv) |
| A06 | CI consolidation plan | [CI audit and plan](ci_consolidation_plan.md) | [Workflow inventory](../metadata/workflow_audit.csv), [overlap pairs](../metadata/workflow_overlap.csv) |

## Interpretation and handoff

The artifact and dataset registries retain unresolved semantics explicitly. A filename, version number or manifest membership alone cannot establish currency, institutional approval or implementation. The status model describes these independently from the nine candidate advancement states.

The lineage graph is static and partial. It distinguishes reads, writes, invocations, preservation hashes, references and documentation. An unresolved dynamic expression or a node without a discovered writer is a review queue, not proof that the file has no producer. Do not move or delete artifacts until their consumers have been checked.

The issue crosswalk prepares a future migration. Original rows, status, severity and request/response distinctions remain intact. The workflow plan is a static assessment; a historical filename does not prove obsolescence, and a passing parser does not establish runtime health. No CI behavior has changed in this wave.

Use these products as inputs to the canonical manifest, issue migration, generated status view and eventual CI changes. A03/A05 validators check record structure and declared evidence; they cannot authenticate a source, certify legal interpretation or approve an operational intervention.

## Reproduction and verification

From the repository root, regenerate and compare audit products using the individual guides, then run:

```sh
python -B scripts/build_artifact_inventory.py --check
python -B scripts/build_dataset_registry.py --check
python -B scripts/validate_repository_status.py
python -B scripts/build_repository_lineage.py --check
python -B scripts/validate_master_issues.py
python -B scripts/audit_workflows.py --check
python -B scripts/validate_repository_audit.py
```

The integration preservation and coverage tests run with:

```sh
python -B tests/check_repository_audit.py
```

Each product guide names its own regression tests and limitations. F01–F06 remain documented in the [foundation standards](foundation_standards.md). The original V13 research reference, historical results, paused course watch and closed live-use gates remain governed by their existing controls.

## Validation result and remaining work

The [validation receipt](../metadata/repository_audit_validation.json) records successful reproducibility and preservation checks, **82 new regression tests**, and **37 existing foundation/V13 tests**. All 554 frozen input hashes remain unchanged. The six outputs and integration checks agree on their scope. No existing workflow, source table, historical result or live-use gate was modified. The receipt describes validation before publication; subsequent commits record the publication history separately.

The dataset registry contains 37 repository-semantic reviews and 287 structural profiles whose unresolved grain/period/source meaning remains visible. The lineage graph contains 554 nodes and 4,151 static edges; 196 recognized dynamic expressions across 52 files remain unresolved. The issue model maps 140 source fields across 17 files but migrates no records. The status model defines the five facets but assigns no new actual artifact statuses.

The workflow audit finds 20 explicit direct-main publishers, eight dynamic acceptance-command replay workflows, five fixed artifact/run references and 56 overlap observations. These are configuration findings and review targets; they do not prove runtime failure, duplicate execution or obsolescence. The workflow audit parser uses PyYAML, tested locally at version 6.0.3. The other audit tools use Python's standard library.

The next tasks are to resolve canonicality and semantic gaps through reviewed contracts, populate the canonical manifest and master issue register, generate current status, and implement CI consolidation only after check-by-check parity review. Audit completion does not mean those migrations or operational efficiency findings are complete.
