# Reform claim discovery inventory — R02

The [machine-readable inventory](../metadata/reform_claim_inventory.json) scans all 656 tracked artifacts at A14 commit `4914e7e41793cbb900bf6d49cd3c6105dd0a6cc9`. It records 1450 matching lines across 159 artifacts. Repeated historical wording and metadata mirrors remain traceable; these counts are discovery records, not unique obligations or verified findings.

The declared patterns cover UN80, UNGA80/81, ACABQ, reform wording, and A/80 or A/81 session symbols. Each record retains exact line text, path, 1-based line, mentioned source symbols, source checksum, manifest currency and any scoped current designation. Every tracked artifact has a scan disposition. Binary files are explicitly listed as not text-extracted. The inventory does not claim exhaustive semantic coverage: wording outside these patterns and scanned PDF contents need separate review.

All records begin `AUTHORITY_UNRESOLVED` and `NOT_SEMANTICALLY_ADJUDICATED`. Under the [authority standard](source_authority_standard.md), a document symbol establishes neither adoption nor implementation. A designated current research source can still contain a proposal or an unverified interpretation. R03–R18 must inspect primary texts and adjudicate these leads independently.

Regenerate with `python scripts/build_reform_claim_inventory.py --write`; verify with `--check`. The frozen commit keeps the denominator stable during concurrent development. A later baseline requires an explicitly reviewed change to `BASELINE`, followed by regeneration. No network retrieval occurs here, and no new source-review date is implied.
