#!/usr/bin/env python3
"""Declare frozen dataset contracts and conservative, separate coverage dimensions."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ["metadata/dataset_registry.csv", "data/ga_approved_all_missions.csv",
          "data/ga_mission_reconciliation.csv", "data/spm_2027_mission_budget.csv",
          "data/mission_function_crosswalk.csv", "data/ga_adopted_directives.csv",
          "data/portfolio/entities.json"]


def rows(root, path):
    with (root / path).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_contracts(root=ROOT):
    registry = rows(root, INPUTS[0])
    contracts = []
    for row in registry:
        reviewed = row["semantic_review"] == "repository_semantics_reviewed"
        contracts.append({
            "dataset_id": row["path"], "path": row["path"],
            "frozen_source_sha256": row["sha256"], "format": row["format"],
            "storage_shape": row["shape"], "stored_row_count": row["row_count"] or None,
            "fields": row["columns"].split("|") if row["columns"] else [],
            "declared_grain": row["grain"], "declared_period": row["period"],
            "key_fields": row["key_columns"].split("|") if row["key_columns"] else [],
            "key_basis": row["key_basis"], "snapshot_key_check": row["key_check"],
            "semantic_review": row["semantic_review"],
            "contract_status": "REPOSITORY_SEMANTICS_REVIEWED_SOURCE_NOT_REAUTHENTICATED" if reviewed else "PROVISIONAL_PROFILE_ONLY",
            "source_fields": row["source_fields"].split("|") if row["source_fields"] else [],
            "source_review": row["source_review"], "evidence_anchors": row["evidence_anchors"],
            "interpretation_limits": row["interpretation_limits"],
            "currency_status": row["repository_role"],
            "refresh_rule": "Frozen audit scope; explicit reviewed revision required before replacing this snapshot.",
            "permitted_use": "Repository-level research within declared grain and period; no source authentication implied." if reviewed else "Artifact discovery and structural profiling only until semantic review.",
            "prohibited_inferences": ["Stored rows are not a verified operational population.", "Unique candidate keys do not establish business grain.", "Budget changes are not incremental savings.", "Coverage does not establish efficiency, waste, implementation or compliance."],
            "semantic_acceptance_gate": "Named reviewer must confirm business grain, units, keys, temporal meaning, source authority, join cardinality, population completeness and permitted uses against underlying evidence.",
            "population_completeness": "NOT_ESTABLISHED", "owner_acceptance": "NOT_OBTAINED",
            "join_contract": {"status": "NOT_CERTIFIED", "cardinality": None, "required_checks": ["identity mapping", "period and unit compatibility", "one-to-many expansion", "unmatched keys", "duplicate amplification"]}
        })
    return {"schema_version": 1, "task_id": "P02", "scope": "All 324 CSV/JSON artifacts in frozen A02 registry; excludes later roadmap outputs and restricted files.",
            "source_registry_sha256": digest(root / INPUTS[0]),
            "counts": {"datasets": len(contracts), "repository_semantics_reviewed": sum(c["semantic_review"] == "repository_semantics_reviewed" for c in contracts), "profile_only_semantics_unreviewed": sum(c["semantic_review"] == "profile_only_semantics_unreviewed" for c in contracts)},
            "contracts": contracts}


def build_coverage(root=ROOT):
    identity = json.loads((root / INPUTS[6]).read_text(encoding="utf-8"))
    def entity_mapping(value, source):
        matches = {a["entity_id"] for a in identity["aliases"] if a["alias"] == value and a["source_path"] == source}
        return next(iter(matches)) if len(matches) == 1 else None
    mission = rows(root, INPUTS[1])
    ga = {r["mission_id"]: r for r in rows(root, INPUTS[2])}
    functions = rows(root, INPUTS[4])
    directives = rows(root, INPUTS[5])
    entities = []
    for row in mission:
        key = row["mission_id"]
        linked_functions = [r["mission_crosswalk_id"] for r in functions if r["mission_id"] == key]
        linked_directives = [r["directive_id"] for r in directives if r["mission_id"] == key]
        entities.append({"source_entity_id": key, "entity_label": key, "entity_population": "ELEVEN_ENTITY_MISSION_BUDGET_REGISTER",
                         "canonical_entity_id": entity_mapping(key, INPUTS[1]),
                         "identity_coverage": "P01_EXACT_SOURCE_ALIAS" if entity_mapping(key, INPUTS[1]) else "IDENTITY_UNRESOLVED",
                         "financial_coverage": "RETAINED_GA_MAINTENANCE_RECONCILIATION" if key in ga else "RETAINED_APPROVED_RESOURCE_NOTE_ONLY",
                         "financial_period": row["fiscal_period"], "financial_authority_note": row["scope_note"],
                         "function_coverage": "REPOSITORY_SCREENING_LINKS" if linked_functions else "NO_LINK_IN_SELECTED_CROSSWALK",
                         "function_record_ids": linked_functions,
                         "reform_coverage": "RETAINED_GA_DIRECTIVE_LINKS_REQUIRE_ACTION_SPECIFIC_REVIEW" if linked_directives else "NO_LINK_IN_SELECTED_DIRECTIVE_TABLE",
                         "reform_record_ids": linked_directives,
                         "operational_evidence_coverage": "NOT_ASSESSED_BY_THIS_MATRIX",
                         "waste_assessed_fraction": None, "savings_validated": "NOT_ESTABLISHED",
                         "source_paths": [INPUTS[1]] + ([INPUTS[2]] if key in ga else [])})
    for row in rows(root, INPUTS[3]):
        entities.append({"source_entity_id": row["spm_id"], "entity_label": row["mission_name"], "entity_population": "THIRTY_SIX_CONTINUING_SPM_PROPOSALS",
                         "canonical_entity_id": entity_mapping(row["spm_id"], INPUTS[3]),
                         "identity_coverage": "P01_EXACT_SOURCE_ALIAS" if entity_mapping(row["spm_id"], INPUTS[3]) else "IDENTITY_UNRESOLVED",
                         "financial_coverage": "RETAINED_PROPOSAL_WITH_PRIOR_YEAR_COLUMNS", "financial_period": row["fiscal_period"],
                         "financial_authority_note": row["budget_status"], "function_coverage": "PROGRAMMED_CATEGORY_ONLY",
                         "programmed_function": row["functional_category"], "function_record_ids": [],
                         "reform_coverage": "NOT_MAPPED_BY_THIS_MATRIX", "reform_record_ids": [],
                         "operational_evidence_coverage": "NOT_ASSESSED_BY_THIS_MATRIX", "waste_assessed_fraction": None,
                         "savings_validated": "NOT_ESTABLISHED", "source_paths": [INPUTS[3]]})
    return {"schema_version": 1, "task_id": "P05", "basis": "Retained repository sources; no new source authentication or financial aggregation.",
            "source_hashes": {p: digest(root / p) for p in INPUTS},
            "counts": {"eleven_entity_budget_register_records": len(mission), "ga_maintenance_reconciliation_records": len(ga), "continuing_spm_proposal_records": len(entities) - len(mission), "matrix_records": len(entities)},
            "denominator_rule": "Two distinct source populations, not a deduplicated count of all UN entities or peace operations; do not sum budgets or treat these counts as worldwide coverage.",
            "dimensions": ["identity_coverage", "financial_coverage", "function_coverage", "reform_coverage", "operational_evidence_coverage"],
            "limits": ["No budget percentage is converted to waste assessed.", "P01 exact source aliases establish declared identity links only; they do not certify grain, joins, lifecycle or mandate status.", "Historical/proposed finance and planned functions do not establish actual operations.", "No total-UN denominator, transaction completeness or function-level costing is available from these tables.", "Reform links refer only to the retained selected directive table, not complete UNGA80/81 obligation coverage.", "An unmapped function or missing link is an evidence gap, not absence of activity or noncompliance."],
            "entities": entities}


def outputs(root=ROOT):
    return {"data/portfolio/dataset_contracts.json": json.dumps(build_contracts(root), indent=2, ensure_ascii=False) + "\n",
            "data/portfolio/coverage_matrix.json": json.dumps(build_coverage(root), indent=2, ensure_ascii=False) + "\n"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = outputs()
    if args.write and args.check:
        parser.error("choose --write or --check")
    if args.write:
        for path, content in result.items():
            target = ROOT / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
    else:
        stale = [p for p, content in result.items() if not (ROOT / p).is_file() or (ROOT / p).read_text(encoding="utf-8") != content]
        if stale:
            raise SystemExit("Stale portfolio outputs: " + ", ".join(stale))
    print("Portfolio dataset contracts and separate coverage dimensions passed.")


if __name__ == "__main__":
    main()
