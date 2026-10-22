#!/usr/bin/env python3
"""A02: reproducible dataset profile for the frozen repository audit scope.

Profiles are metadata, not operational observations or savings findings.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import io
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SCOPE = "metadata/repository_audit_scope.json"
OUTPUT = "metadata/dataset_registry.csv"
FIELDS = ["path", "format", "shape", "row_count", "column_count", "columns", "grain", "key_columns", "key_basis", "key_check", "duplicate_key_excess", "empty_key_rows", "exact_duplicate_excess", "period", "temporal_fields", "source_fields", "interpretation_limits", "semantic_review", "source_review", "repository_role", "status_basis", "evidence_anchors", "sha256"]

# Deliberately small curated layer: these meanings were reviewed against the
# repository dictionary, cited methods and validators, not original UN sources.
# All other files remain explicitly profile-only.
SEMANTICS = {
    "data/functional_inventory.csv": ("one source-supported departmental function", "2027 departmental proposals", "functions and organizational descriptions do not prove duplicate work"),
    "data/mandate_inventory.csv": ("one selected governing-instrument comparison", "instrument-specific; no single period", "not a complete legal inventory or legal interpretation"),
    "data/deliverable_inventory.csv": ("one source-table deliverable and unit", "2025 actual versus 2027 planned", "heterogeneous units and planned outputs are nonadditive"),
    "data/crosswalk.csv": ("one paired DPPA-DPO function comparison", "2027 departmental proposals", "similarity and shared structure do not establish operational duplication"),
    "data/candidate_validation.csv": ("one documentary investigation candidate", "repository baseline research; not a realized-benefit period", "priority is investigative utility; no verified saving"),
    "data/un80_register.csv": ("one described reform or organizational arrangement", "2027 proposal context; implementation separately unverified", "proposal and documented structure are not implementation"),
    "data/financial_guardrails.csv": ("one financial-perimeter control", "record-specific 2027 proposal boundaries", "published amounts are financial scopes, not avoidable costs; USD"),
    "data/quality_issues.csv": ("one quality issue or interpretation blocker", "issue-specific; evolving repository record", "resolved data issue does not establish operational improvement"),
    "data/ga_mission_reconciliation.csv": ("one selected mission and financing decision reconciliation", "1 July 2026 to 30 June 2027", "USD thousands; maintenance and inclusive appropriation differ; not expenditure"),
    "data/ga_approved_all_missions.csv": ("one mission-maintenance funding total", "1 July 2026 to 30 June 2027", "USD thousands; high-level presence is not detailed operational coverage"),
    "data/ga_approved_resource_components.csv": ("one mission cost component at an explicit hierarchy level", "1 July 2026 to 30 June 2027", "USD thousands; do not add parent operational amounts and child subcategories"),
    "data/ga_apportionment_schedule.csv": ("one mission apportionment segment", "1 July 2026 to 30 June 2027; segment conditions apply", "USD thousands; conditional assessments are not cash collected"),
    "data/ga_unmiss_abolishments.csv": ("one annex unit/category of approved post abolishments", "2026/27 approved actions", "rows are grouped post counts, not individual posts or realized payroll reductions"),
    "data/ga_adopted_directives.csv": ("one selected GA operative directive", "resolution-specific 80th-session actions", "selected directives do not establish full UNGA80/81 compliance"),
    "data/spm_2027_mission_budget.csv": ("one continuing SPM mission budget comparison", "2025 appropriation/expenditure; 2026 approved; 2027 proposed", "USD thousands; not GA-approved 2027 funding; personnel units defined by source"),
    "data/spm_2027_cluster_bridge.csv": ("one cluster or nonadditive chapeau bridge component", "2026 approved versus calendar-2027 proposal", "USD thousands; mission aggregate and components cannot both be added"),
    "data/spm_2027_embedded_efficiencies.csv": ("one proposed efficiency initiative estimate", "calendar-2027 proposal", "USD thousands; 31 estimates already embedded; not new incremental or realized savings"),
    "data/spm_2027_closure_bridge.csv": ("one discontinued mission baseline", "2026 approved closure baseline versus 2027", "mandate closures are not additional efficiency benefits"),
    "data/spm_2027_extrabudgetary_items.csv": ("one source-specific projected voluntary/cost-recovery item", "calendar-2027 estimates", "USD thousands; voluntary revenue and internal cost recovery differ"),
    "data/spm_2027_extrabudgetary_coverage.csv": ("one mission extrabudgetary disclosure classification", "calendar-2027 estimates", "not reported is distinct from explicit zero"),
    "data/spm_2027_source_discrepancies.csv": ("one recorded source discrepancy", "source-specific versions and financial years", "selected source treatment does not silently resolve conflicting originals"),
    "data/acabq_2027_mission_reconciliation.csv": ("one mission SG-to-ACABQ advisory comparison", "2026 approved versus calendar-2027 proposal/advice", "27 reviewed advisory amounts and nine unavailable Cluster III recommendations; not GA adoption"),
    "data/consolidation_comprehensive_2027.csv": ("one umbrella or linked mission work package", "2027 research hierarchy", "14 parents and nine child packages overlap; do not add exposures"),
    "data/transaction_validation_cases.csv": ("one public-source transaction-control case", "case-specific 2026/27 and 2027 sources", "three public control cases; no actual verified private ledger rows"),
    "data/transaction_control_baseline.csv": ("one published cost or financial-boundary control", "case-specific fiscal/calendar periods", "published controls are not operational transaction records"),
    "data/transaction_evidence_requests.csv": ("one requested internal evidence package", "requested periods specified per package", "request specification only; no evidence received implied"),
    "data/restricted_transaction_request_spec.csv": ("one requested dataset specification", "requested periods specified per row", "public specification; actual restricted records must remain outside Git"),
    "data/rsce_workforce_model_vs_post_actions.csv": ("one staffing/model observation", "source-specific 2026/27 or 2027 comparisons", "FTE model, transferred post and abolished post are different units"),
    "data/public_opportunity_register.csv": ("one public research or monitoring opportunity", "repository research cutoff; budgets vary", "opportunity is not operationally validated waste or savings"),
    "data/public_finance_nodes.csv": ("one published financial amount and perimeter", "record-specific periods", "finance nodes may contain parents, children and alternate periods; not additive"),
    "data/public_finance_edges.csv": ("one inclusion or accounting-boundary relation", "linked-node periods", "relation is metadata and must not be counted as a financial observation"),
    "data/public_release_gates.csv": ("one opportunity release-gate assessment", "research-status cutoff", "a gate record does not provide institutional authorization"),
    "data/owner_review/evidence_gap_register.csv": ("one question or evidence/authority gate", "15 October 2026 owner-review package", "unasked questions are not proven workflow defects; requests not sent"),
    "data/census_v13/research_reference.json": ("one selected research observation object in a fixed reference", "15 October 2026 adopted research version 13.0", "61 obligations; selected sources not complete event population; no live authority"),
    "data/census_v13/reference_lineage.csv": ("one fixed obligation and research-disposition lineage", "historical first pass and V13 adoption", "59 original supports plus two separate rechecks; no fresh 61/61 first-pass score"),
    "data/current_research_reference.json": ("one research-reference pointer object", "15 October 2026 instruction", "pointer governs fixed V8/V9 obligations only; no institutional approval"),
    "data/standards/candidate_states.json": ("one candidate-state dictionary object", "22 October 2026 prospective project standard", "dictionary and structural validation do not promote cases or verify evidence"),
}


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def declared_keys(root, scope):
    """Read literal validator maps, never execute repository code."""
    found = {}
    paths = {f["path"] for f in scope["files"]}
    for entry in scope["files"]:
        p = entry["path"]
        if not (p.startswith("scripts/validate_") and p.endswith(".py")):
            continue
        tree = ast.parse((root / p).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Dict):
                continue
            try:
                mapping = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                continue
            for stem, key in mapping.items():
                if isinstance(stem, str) and isinstance(key, str) and f"data/{stem}.csv" in paths:
                    found.setdefault(f"data/{stem}.csv", set()).add((key, p))
    return found


def profile_csv(body):
    reader = csv.DictReader(io.StringIO(body.decode("utf-8-sig"), newline=""))
    columns = reader.fieldnames or []
    rows = list(reader)
    if len(columns) != len(set(columns)) or any(None in r or any(v is None for v in r.values()) for r in rows):
        raise ValueError("malformed CSV header or row width")
    return "csv_records", columns, rows


def profile_json(body):
    value = json.loads(body)
    if isinstance(value, dict):
        return "json_object_not_tabular", sorted(value), None
    if isinstance(value, list) and value and all(isinstance(r, dict) for r in value):
        return "json_object_array", sorted(set().union(*(r.keys() for r in value))), value
    if isinstance(value, list):
        return "json_array_not_record_table", [], None
    return "json_scalar_not_tabular", [], None


def key_profile(rows, columns, declared):
    candidates = sorted({key for key, _ in declared if key in columns})
    if len(candidates) > 1:
        return "|".join(candidates), "conflicting_validator_declarations", "not_established", "", ""
    key = candidates[0] if candidates else (columns[0] if columns else "")
    if rows is None or not key:
        return "", "not_applicable_non_tabular", "not_applicable", "", ""
    values = [json.dumps(r.get(key), sort_keys=True, ensure_ascii=False) for r in rows]
    empty = sum(r.get(key) is None or str(r.get(key)).strip() == "" for r in rows)
    duplicates = len(values) - len(set(values))
    check = "unique_nonempty_in_snapshot" if rows and not empty and not duplicates else ("empty_table_no_key_evidence" if not rows else "not_unique_or_empty")
    return key, "validator_declared" if candidates else "first_column_candidate_only", check, duplicates, empty


def build(root=ROOT):
    scope = load_json(root / SCOPE)
    key_map = declared_keys(root, scope)
    dictionary_lines = (root / "docs/data_dictionary.md").read_text().splitlines()
    pointer = load_json(root / "data/current_research_reference.json")
    rows = []
    for entry in scope["files"]:
        p = entry["path"]
        if Path(p).suffix not in {".csv", ".json"}:
            continue
        body = (root / p).read_bytes()
        digest = hashlib.sha256(body).hexdigest()
        if digest != entry["sha256"]:
            raise ValueError(f"frozen input hash changed: {p}")
        shape, columns, records = profile_csv(body) if p.endswith(".csv") else profile_json(body)
        key, basis, key_check, duplicate, empty = key_profile(records, columns, key_map.get(p, set()))
        exact = "" if records is None else len(records) - len({json.dumps(r, sort_keys=True, ensure_ascii=False) for r in records})
        semantic = SEMANTICS.get(p)
        anchors = [f"docs/data_dictionary.md:{i}" for i, line in enumerate(dictionary_lines, 1) if Path(p).name in line]
        anchors.extend(sorted({source for _, source in key_map.get(p, set())}))
        role = "currency_unresolved"
        status_basis = "no global current-dataset manifest; classification deferred to A03"
        if p == pointer["reference_path"]:
            role, status_basis = "current_adopted_research_reference", "data/current_research_reference.json:reference_path; restricted to fixed V8/V9 scope"
        elif p in {pointer["current_dispositions_path"], pointer["adoption_record_path"]}:
            role, status_basis = "current_research_support", "data/current_research_reference.json; restricted to V13 lineage/adoption"
        elif p == "data/current_research_reference.json":
            role, status_basis = "current_pointer", "self-described pointer corroborated by docs/v13_reference_adoption.md"
        elif p.startswith("tests/fixtures/"):
            role, status_basis = "engineering_fixture", "fixture location and naming; not operational evidence"
        elif re.search(r"/census_v\d+/", p) or p.startswith("reports/white_paper_"):
            role, status_basis = "versioned_artifact_currency_unresolved", "version identifies provenance; current/historical semantics require supersession review"
        elif p.startswith("data/standards/"):
            role, status_basis = "prospective_standard", "F01-F06 local project framework; not implemented UN evidence"
        count = len(records) if records is not None else ""
        generic_limit = "row count describes stored records only; no event, participant, payment, savings or population count inferred"
        if records is None:
            generic_limit = "JSON object/array structure is metadata or content; blank row_count means not a table, not zero records"
        if len(anchors) > 1:
            generic_limit += "; multiple documentation anchors may describe successive historical versions"
        temporal = [c for c in columns if re.search(r"date|year|period|asof|cutoff|time", c, re.I)]
        sources = [c for c in columns if re.search(r"source|citation|anchor|symbol|url|sha256|official", c, re.I)]
        rows.append(dict(zip(FIELDS, [p, Path(p).suffix[1:], shape, count, len(columns), "|".join(columns), semantic[0] if semantic else "not_semantically_reviewed; stored row/object grain only", key, basis, key_check, duplicate, empty, exact, semantic[1] if semantic else "not_semantically_reviewed; see temporal_fields without inferring event period", "|".join(temporal), "|".join(sources), (semantic[2] + "; " if semantic else "") + generic_limit, "repository_semantics_reviewed" if semantic else "profile_only_semantics_unreviewed", "repository_documentation_only; original_UN_sources_not_reauthenticated", role, status_basis, "|".join(anchors) or "no_dataset_specific_anchor_identified", digest])))
    return rows


def render(rows):
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare existing output without changing it")
    args = parser.parse_args()
    result = build()
    body = render(result)
    target = ROOT / OUTPUT
    if args.check:
        if not target.exists() or target.read_text() != body:
            raise SystemExit("FAIL: dataset registry missing or differs from frozen-input regeneration")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
    print(f"PASS: {len(result)} datasets; {sum(r['semantic_review']=='repository_semantics_reviewed' for r in result)} reviewed repository-semantic definitions; original sources not reauthenticated")


if __name__ == "__main__":
    main()
