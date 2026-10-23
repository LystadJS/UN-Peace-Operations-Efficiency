#!/usr/bin/env python3
"""Validate declared reform obligations without inferring authority from symbols."""
import argparse
import datetime as dt
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def validate(data, schema=None):
    schema = schema or json.loads((ROOT / "data/reforms/obligation_schema.json").read_text())
    errors = []
    def require(condition, message):
        if not condition:
            errors.append(message)
    def text(value):
        return isinstance(value, str) and bool(value.strip())
    def date(value):
        try:
            dt.date.fromisoformat(value)
            return True
        except (TypeError, ValueError):
            return False
    require(isinstance(data, dict), "Envelope must be an object")
    if not isinstance(data, dict):
        return errors
    require(data.get("schema_version") == 1, "schema_version must be 1")
    rows = data.get("obligations")
    require(isinstance(rows, list), "obligations must be a list")
    if not isinstance(rows, list):
        return errors
    seen = set()
    for i, row in enumerate(rows):
        prefix = f"obligations[{i}]"
        if not isinstance(row, dict):
            errors.append(prefix + " must be an object")
            continue
        for field in schema["required_fields"]:
            require(field in row, f"{prefix}: missing {field}")
        ident = row.get("obligation_id")
        require(text(ident), prefix + ": obligation_id required")
        if isinstance(ident, str):
            require(ident not in seen, prefix + ": duplicate obligation_id")
            seen.add(ident)
        authority = row.get("authority_class")
        require(authority in schema["authority_classes"], prefix + ": invalid authority_class")
        require(text(row.get("issuing_organ")), prefix + ": issuing_organ required")
        for field in ("document_symbol", "session"):
            require(row.get(field) is None or text(row.get(field)), prefix + ": invalid " + field)
        require(date(row.get("evidence_cutoff")), prefix + ": invalid evidence_cutoff")
        sections = {}
        for name in ("source", "adoption", "provision", "competence", "implementation", "compliance"):
            section = row.get(name)
            require(isinstance(section, dict), prefix + ": invalid " + name)
            sections[name] = section if isinstance(section, dict) else {}
            for field in schema[name + "_fields"]:
                require(field in sections[name], f"{prefix}: missing {name}.{field}")
        source, adoption, provision, competence, implementation, compliance = (sections[n] for n in ("source", "adoption", "provision", "competence", "implementation", "compliance"))
        url = source.get("official_url")
        require(url is None or (text(url) and urlparse(url).scheme == "https" and bool(urlparse(url).hostname)), prefix + ": invalid official_url")
        for field in ("retrieved_at",):
            require(source.get(field) is None or date(source.get(field)), prefix + ": invalid " + field)
        if date(source.get("retrieved_at")) and date(row.get("evidence_cutoff")):
            require(source["retrieved_at"] <= row["evidence_cutoff"], prefix + ": retrieval exceeds evidence cutoff")
        require(text(source.get("review_scope")), prefix + ": review_scope required")
        require(isinstance(source.get("limitations"), list), prefix + ": limitations must be a list")
        require(adoption.get("status") in schema["adoption_states"], prefix + ": invalid adoption status")
        require(provision.get("effect") in schema["provision_effects"], prefix + ": invalid provision effect")
        for field in ("entities", "functions", "conditions"):
            require(isinstance(provision.get(field), list), prefix + ": " + field + " must be a list")
        deadline = provision.get("deadline")
        require(deadline is None or date(deadline), prefix + ": invalid deadline")
        if deadline is not None:
            require(text(provision.get("deadline_basis")), prefix + ": deadline requires source basis")
        adopted = adoption.get("status") == "ADOPTED_VERIFIED"
        if authority in ("GA_ADOPTED", "SC_MANDATE"):
            require(adopted, prefix + ": adopted authority requires verified adoption")
            require(row.get("issuing_organ") == ("GENERAL_ASSEMBLY" if authority == "GA_ADOPTED" else "SECURITY_COUNCIL"), prefix + ": organ/authority mismatch")
        if adopted:
            require(authority in ("GA_ADOPTED", "SC_MANDATE"), prefix + ": advice/proposals cannot assert governing adoption")
            for field in ("final_text_receipt", "adoption_record_receipt"):
                require(text(adoption.get(field)), prefix + ": adoption requires " + field)
            require(date(adoption.get("date")), prefix + ": adoption date required")
            if date(adoption.get("date")) and date(row.get("evidence_cutoff")):
                require(adoption["date"] <= row["evidence_cutoff"], prefix + ": adoption exceeds evidence cutoff")
            require(text(source.get("locator")) and text(url), prefix + ": adoption requires official provision locator")
            for field in ("action", "addressee"):
                require(text(provision.get(field)), prefix + ": adopted provision requires " + field)
            require(text(competence.get("assessment")) and text(competence.get("review_receipt")), prefix + ": adoption requires competence review")
            require(text(competence.get("mandate_financing_distinction")), prefix + ": distinguish mandate and financing competence")
        require(implementation.get("status") in schema["implementation_states"], prefix + ": invalid implementation status")
        for field in ("evidence_receipts", "verified_components", "unverified_components"):
            require(isinstance(implementation.get(field), list), prefix + ": implementation " + field + " must be a list")
            if isinstance(implementation.get(field), list):
                require(all(text(item) for item in implementation[field]), prefix + ": implementation " + field + " contains blank/nontext entries")
        if implementation.get("status") in ("PARTIALLY_VERIFIED", "VERIFIED"):
            require(bool(implementation.get("evidence_receipts")), prefix + ": implementation verification requires separate evidence")
            require(bool(implementation.get("verified_components")), prefix + ": implementation verification requires scoped components")
        if implementation.get("status") == "VERIFIED":
            require(implementation.get("unverified_components") == [], prefix + ": full verification has unverified components")
        require(compliance.get("status") in schema["compliance_states"], prefix + ": invalid compliance status")
        if compliance.get("status") in ("COMPLIANT_VERIFIED", "NONCOMPLIANT_VERIFIED"):
            require(adopted, prefix + ": compliance finding requires adopted applicable authority")
            require(text(compliance.get("assessment_receipt")) and text(compliance.get("coverage_receipt")), prefix + ": compliance requires assessment and coverage evidence")
            require(provision.get("effect") in ("DIRECTION", "REQUEST"), prefix + ": compliance requires characterized operative obligation")
        if compliance.get("status") == "NONCOMPLIANT_VERIFIED":
            require(date(deadline) and date(row.get("evidence_cutoff")) and deadline <= row["evidence_cutoff"], prefix + ": noncompliance requires elapsed deadline")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", type=Path)
    args = parser.parse_args()
    schema = json.loads((ROOT / "data/reforms/obligation_schema.json").read_text())
    if args.records:
        errors = validate(json.loads(args.records.read_text()), schema)
        if errors:
            raise SystemExit("\n".join(errors))
        print("Reform obligation declarations passed; substantive authority is not authenticated.")
    else:
        assert len(schema["authority_classes"]) == len(set(schema["authority_classes"]))
        print("Reform obligation vocabulary loaded; no factual records assessed.")


if __name__ == "__main__":
    main()
