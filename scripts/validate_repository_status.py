#!/usr/bin/env python3
"""Validate declared repository status snapshots, not evidence truth or authority."""
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path, PurePosixPath
import sys

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "metadata/repository_status_schema.json"
FACETS = ("currency", "research_adoption", "institutional_approval", "implementation", "live_use")
UNCERTAIN = {"UNKNOWN", "UNRESOLVED", "NOT_APPLICABLE"}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def read(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique)


def validate_schema(schema):
    require(isinstance(schema, dict), "schema must be an object")
    require(schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema", "unsupported JSON Schema draft")
    definitions = schema.get("$defs")
    require(isinstance(definitions, dict), "schema definitions missing")
    require(all(f in definitions for f in FACETS), "missing status facet")
    for facet in FACETS:
        values = definitions[facet]["allOf"][1]["properties"]["status"]["enum"]
        require(isinstance(values, list) and values and all(nonempty(v) for v in values), f"invalid {facet} enum")
        require(len(values) == len(set(values)), f"duplicate {facet} status")
    return schema


def validate(payload, schema):
    validate_schema(schema)
    require(isinstance(payload, dict) and set(payload) == {"schema_version", "records"}, "expected schema_version and records")
    require(type(payload["schema_version"]) is int and payload["schema_version"] == 1, "schema_version must be integer 1")
    records = payload["records"]
    require(isinstance(records, list), "records must be an array")
    required = set(schema["$defs"]["record"]["required"])
    index, current = {}, set()
    for row in records:
        require(isinstance(row, dict) and set(row) == required, "record fields do not match contract")
        for field in ("artifact_id", "path", "version", "scope", "role"):
            require(nonempty(row[field]), f"invalid {field}")
        rid = row["artifact_id"]
        require(rid not in index, f"duplicate artifact_id: {rid}")
        index[rid] = row
        path = PurePosixPath(row["path"])
        require(not path.is_absolute() and ".." not in path.parts and "\\" not in row["path"] and path.parts,
                f"{rid}: path must be a relative repository path")
        try:
            as_of, cutoff = (date.fromisoformat(row[k]) for k in ("as_of", "evidence_cutoff"))
        except (ValueError, TypeError):
            raise ValueError(f"{rid}: invalid date") from None
        require(cutoff <= as_of, f"{rid}: evidence cutoff follows snapshot")
        for facet in FACETS:
            entry = row[facet]
            require(isinstance(entry, dict) and set(entry) == {"status", "evidence_refs", "rationale"}, f"{rid}: invalid {facet} fields")
            allowed = schema["$defs"][facet]["allOf"][1]["properties"]["status"]["enum"]
            require(isinstance(entry["status"], str) and entry["status"] in allowed, f"{rid}: invalid {facet} status")
            require(nonempty(entry["rationale"]), f"{rid}: {facet} rationale required")
            refs = entry["evidence_refs"]
            require(isinstance(refs, list) and all(nonempty(v) for v in refs), f"{rid}: invalid evidence references")
            require(len(refs) == len(set(refs)), f"{rid}: duplicate evidence references")
            require(entry["status"] in UNCERTAIN or bool(refs), f"{rid}: definitive {facet} status needs evidence")
        status = row["currency"]["status"]
        target = row["superseded_by"]
        require((status == "SUPERSEDED" and nonempty(target)) or (status != "SUPERSEDED" and target is None), f"{rid}: supersession target/status mismatch")
        if status == "CURRENT":
            slot = (row["scope"], row["role"])
            require(slot not in current, f"conflicting current artifacts for {slot}")
            current.add(slot)
        if row["live_use"]["status"] == "AUTHORIZED":
            require(row["institutional_approval"]["status"] == "APPROVED", f"{rid}: live use requires institutional approval")
    for rid, row in index.items():
        visited = {rid}
        cursor = row
        while cursor["superseded_by"] is not None:
            target = cursor["superseded_by"]
            require(target in index, f"{rid}: replacement {target} absent")
            require(target not in visited, f"{rid}: supersession cycle")
            visited.add(target)
            replacement = index[target]
            require((replacement["scope"], replacement["role"]) == (row["scope"], row["role"]), f"{rid}: replacement scope/role differs")
            require(replacement["currency"]["status"] != "CANDIDATE", f"{rid}: draft cannot supersede an artifact")
            cursor = replacement
    return len(records)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=SCHEMA)
    parser.add_argument("--records", type=Path)
    args = parser.parse_args()
    try:
        schema = validate_schema(read(args.schema))
        count = validate(read(args.records), schema) if args.records else 0
        print(f"PASS: five-facet status schema; {count} supplied snapshot records structurally valid")
        print("No evidence, legal authority, operational implementation or live permission was authenticated.")
        return 0
    except (ValueError, OSError, KeyError, TypeError, IndexError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
