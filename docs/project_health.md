# A14 — Project health

This document is generated from [the machine-readable health receipt](../metadata/project_health.json).

**Structural checks passed; full runtime CI is not asserted by this receipt.**

The receipt checks 586 canonical input-artifact records, 20 designated current roles and 117 migrated issue observations. It validates current-status regeneration, source snapshots, issue identities and migration counts. Source hashes make the result reproducible for unchanged inputs; publishing it does not supply institutional approval or operational evidence.

Cash savings and staff time saved remain **not estimated**. Both reporting live-use gates remain closed, and the course watch remains **paused**. Historical observations, current questions and control constraints are included together in source-observation totals; resolution and gate-status distributions remain separate. None is automatically a verified operational defect.

## Reproduction

```sh
python -B scripts/build_project_health.py --write
python -B scripts/build_project_health.py --check
python -B tests/check_project_health.py
```

The generator contains no network calls, source collection, operational activation or CI execution. A fixed input set produces identical bytes. It hashes neither itself recursively through the output nor the generated guide. Actual CI acceptance requires a separate exact-commit runtime receipt in the pinned Python/R environment.

The retained dataset and dynamic-lineage gaps remain open. See [current status](current_status.md), [the issue migration](issue_migration.md), [CI validation](ci_validation.md) and [publication controls](publication_workflow.md) for their scope and limits.
