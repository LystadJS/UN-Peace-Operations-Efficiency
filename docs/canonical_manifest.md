# A07 — Canonical artifact and release manifest

The [manifest](../metadata/canonical_manifest.json) designates controlling project roles for the **586 tracked artifacts** selected at commit `9838cec16e9c14a5d87757c5ff6614ff1ae7dc24`. The commit defines the population; hashes describe the working implementation observed at A07, including explicitly authorized audit-reader adapters. This is not an assertion that the evolving working tree contains only 586 files or that every observed byte equals that baseline commit. The [release index](../metadata/release_index.csv) preserves version scopes. It does not designate every older artifact obsolete or every current artifact institutionally approved.

## Contract

- `current_roles` maps a role to `path`, `scope` and `designation_basis`. Role and scope govern precedence; version-looking filenames alone do not. The V13 research reference controls only the fixed V8/V9 obligations. The V10 shadow protocol remains applicable for its distinct purpose.
- `artifacts` has one row per baseline path, with a declared artifact role, currency, scope, designation basis, digest mode, digest, and any frozen baseline reference. `UNRESOLVED` currency is deliberate when no controlling role was selected. Retained original release records remain `HISTORICAL` in their original-release role even when they provide evidence for current research.
- `immutable_sha256` verifies the current path bytes. `mutable_control_with_archived_baseline` applies only to the README and 28 workflow controls authorized to evolve in A10/A12/A13. Their current digest is null; the archived baseline digest remains mandatory. This avoids presenting a historical workflow hash as its new live hash.
- `generated_artifacts` declares future issue/status/health paths and producers. Their checksums are intentionally excluded from the manifest to prevent circular dependencies: the status may hash its manifest, and the health receipt may hash current controls, without either hashing itself. Producer checks verify generated content.
- `supersession_relationships` requires existing endpoints, explicit scope and evidence. The initial relation is limited to the two AM11 research assertions corrected in V13. It preserves original first-pass dispositions; it does not claim all prior outputs, mandates or financing have been superseded.

## Historical preservation during authorized control changes

The [archive map](../metadata/frozen_input_archive.json) identifies **32 byte-identical prior controls** under `history/pre_controls/`: README plus the 28 workflows in the original audit scope, and three A05 schema/validator/test baselines authorized to evolve for A08 compatibility. The historical A01/A04/A06 generators and cross-product preservation validator now use `scripts/frozen_audit_inputs.py` to resolve their original frozen records. The three A05 compatibility files were outside the 554-file audit population and are preserved from the stated baseline commit. The helper validates a declared archive before returning it; it does not silently substitute changed live bytes.

This lets the frozen A01–A06 audit reproduce after authorized navigation/CI evolution. The historical audit continues to describe old configurations. Current workflow validation and the new consistency suite must assess the live configurations separately. Archived workflows are outside `.github/workflows/` and cannot be executed by GitHub Actions merely because they are preserved.

Raw data, captured sources, historical research outputs, the V13 payload, existing live gates and the paused watch remain unchanged. Archive designation is repository preservation, not legal adoption, implementation evidence or authority to conduct operational trials.

## Reproduction

```sh
python -B scripts/build_canonical_manifest.py --write
python -B scripts/build_canonical_manifest.py --check
python -B tests/check_canonical_manifest.py
```

The generator is deterministic for the declared source population. `--write` is an explicit regeneration after reviewed source changes, not an automatic cure for unexpected drift. `--check` verifies artifact existence, hashes, current-role endpoints, scoped supersession and absence of supersession cycles. It does not inspect private evidence or authenticate the substantive meaning of source receipts. Further artifacts and canonicality designations require a reviewed population/contract update.
