# A01 — Frozen repository artifact inventory

The [artifact inventory](../metadata/artifact_inventory.csv) contains exactly one row for each of the **554 files** in the [frozen audit scope](../metadata/repository_audit_scope.json): 543 files tracked at baseline commit `32f02e5e689ad9f43e762d5985330df20dda1719`, plus the 11 pre-existing F01–F06 additions. This is exhaustive for that declared input universe, not a claim that the live working tree still contains only 554 files. The scope excludes ignored files, Git internals, scratch work, the scope record itself and outputs created during A01–A06. A later inventory must freeze a new scope rather than silently expanding this denominator.

## Fields and interpretation

Every row retains the frozen file size, SHA-256, tracked status, file format, artifact role, version identity where present, evidence-backed currency, producer association where established, contextual input manifest, retention rule and unresolved-lineage limitation. Classification is deterministic and remains separate from institutional or operational status.

- `file_kind` describes format, not authority.
- `artifact_role` distinguishes executable code, test fixtures, CI configuration, source captures, manifested release outputs, report components, control records and unresolved analytical data.
- `release_identity` identifies a versioned path. It does not establish current, superseded, approved or implemented status.
- `currency_status` is conservative: only the explicit research-reference pointer establishes its scoped current reference, and F01–F06 are identified as prospective project standards. All other currency remains `not_established_by_inventory` pending the status model and claim-specific review.
- `producer_status=release_generator_association` records a declared output prefix and output-manifest membership. It is weaker than proof of a file-specific writer. Unresolved producer fields are deliberately blank and flagged.
- `source_input_manifest` is contextual release lineage. A release-wide frozen input list does not prove every input produces every individual output.
- Source captures and manifested releases receive byte-preservation treatment. Other files remain retained until an explicit reviewed migration. No file deletion or relocation is recommended merely because an artifact is versioned or byte-identical to another.

The inventory does not manufacture canonicality for top-level CSVs or infer historical/superseded state from filenames. A table may be a retained historical release and still provide selected current evidence; a protocol may remain applicable while its worked examples are historical. The A03 status model owns these independent status dimensions. The A04 lineage graph supplies more detailed producer/consumer evidence before consolidation or migration.

## Reproduction

```sh
python -B scripts/build_artifact_inventory.py --write
python -B scripts/build_artifact_inventory.py --check
python -B tests/check_artifact_inventory.py
```

The build rejects changed or missing frozen inputs. Checking compares the complete deterministic CSV against regeneration. Tests confirm exact-once coverage, stable output and protection against current-sounding names or manifest membership being mistaken for current authority. These checks establish inventory and preservation properties only; they do not authenticate UN sources or certify implementation, duplication or savings.
