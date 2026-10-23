# A11 — Cross-project consistency controls

The current-source generators, canonical manifest and retained lineage must agree before a release. Run:

```sh
python -B scripts/validate_project_consistency.py
python -B tests/check_project_consistency.py
```

The validator checks canonical artifact labels and scoped current links; manifest hashes; exact regeneration of current status and navigation; research-reference selection; historical first-pass preservation; the two adopted corrections; paused/blocked activity; unknown savings; finance inclusion arithmetic; and all retained lineage endpoints and evidence files.

The 13 synthetic regression controls deliberately introduce contradictory states, a stale research reference, rewritten historical holds, an active watch, unsupported zero savings, mixed financial perimeters, broken links, unmarked historical records, stale canonical links and a dangling lineage endpoint. They must be rejected. Current status remains distinct from the historical records it summarizes.

Frozen inputs resolve through verified archives when an explicitly authorized README or workflow change replaces their live paths. Old inventory and lineage checks continue to test their original source bytes. A static graph remains incomplete for dynamic expressions; lack of an edge is not proof of no dependency.

These tests check structural consistency and the retained evidence contract. They do not supply new UN legal interpretation, institutional approval, operational performance evidence or a savings finding. Legitimate future source changes require a reviewed update to the contract and its tests rather than bypassing a failing check.
