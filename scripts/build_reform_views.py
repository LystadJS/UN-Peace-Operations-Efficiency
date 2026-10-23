#!/usr/bin/env python3
"""Build bounded reform views without promoting documentary evidence to outcomes."""
import argparse
import csv
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INPUTS = [f"data/reforms/{name}.json" for name in ("unga80_actions", "unga81_actions", "unga80_instruments", "unga81_instruments", "acabq_recommendations", "sg_proposals", "un80_arrangement_reconciliation")]
INPUTS += ["data/candidate_validation.csv", "data/reforms/compliance_statuses.json", "data/reforms/obligation_schema.json"]


def tokens(text):
    return set(re.findall(r"\b[a-z][a-z0-9]{3,}\b", text.lower())) - {"united", "nations", "support", "operations", "operational", "functions", "mandate", "mandates", "peace", "peacekeeping", "implementation", "effective", "efficiency", "budget", "resources", "service", "services", "system", "review", "shared"}


def build(root=ROOT):
    inputs = {path: json.loads((root / path).read_text()) for path in INPUTS if path.endswith('.json')}
    hashes = {path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in INPUTS}
    obligations = [r for session in (80, 81) for r in inputs[f"data/reforms/unga{session}_actions.json"]["obligations"]]
    proposals = inputs["data/reforms/sg_proposals.json"]["records"]
    with (root/'data/candidate_validation.csv').open(newline='') as handle:
        candidates = list(csv.DictReader(handle))
    common = {"schema_version": 1, "evidence_cutoff": "2026-10-23", "source_hashes": hashes,
              "scope": "Selected extracted provisions and retained proposal/advice records, not exhaustive session or mission compliance coverage.",
              "limitations": ["Selected provisions are not automatically mandatory requirements applicable to every peace operation.", "Documentary adoption and repository publication do not establish implementation, owner approval or financial benefit."]}
    crosswalk = []
    for row in obligations:
        provision = row["provision"]
        terms = tokens(" ".join([provision["action"], provision["addressee"], *provision["entities"], *provision["functions"]]))
        links = []
        for candidate in candidates:
            overlap = sorted(terms & tokens(candidate["name"]))
            if len(overlap) >= 2:
                links.append({"candidate_id": candidate["candidate_id"], "namespace": "LEGACY_CANDIDATE_VALIDATION_NOT_ROADMAP_CASE_ID", "source": "data/candidate_validation.csv", "matching_terms": overlap, "link_status": "PRELIMINARY_TEXT_MATCH_NOT_APPLICABILITY", "applicability_review_receipt": None})
        crosswalk.append({"obligation_id": row["obligation_id"], "instrument": row["document_symbol"], "source_locator": row["source"]["locator"],
            "operative_effect": provision["effect"], "addressee": provision["addressee"], "entities_as_extracted": provision["entities"],
            "functions_as_extracted": provision["functions"], "deadline": provision["deadline"], "deadline_basis": provision["deadline_basis"],
            "conditions": provision["conditions"], "candidate_links": links,
            "candidate_applicability_status": "NOT_ADJUDICATED", "budget_link_status": "NOT_RECONCILED_TO_APPROPRIATION_OR_COST_OBJECTS", "budget_amount": None})
    cross = {**common, "register_id": "R09-OBLIGATION-CROSSWALK-1", "mapping_method": "Preserve extracted scopes; optional case title overlap requires at least two non-generic exact terms. Matches are leads, not legal applicability findings.", "records": crosswalk}
    evidence = []
    for row in obligations:
        evidence.append({"record_id": row["obligation_id"], "record_kind": "EXTRACTED_PROVISION", "authority_class": row["authority_class"], "implementation": row["implementation"], "compliance": row["compliance"], "operational_verification": "NOT_PERFORMED_BY_THIS_VIEW", "owner_approval": "NOT_ESTABLISHED"})
    for row in proposals:
        evidence.append({"record_id": row["proposal_id"], "record_kind": row["source_treatment"], "documentary_claim": row["documentary_claim"], "implementation": row["implementation"], "operational_verification": "NOT_INDEPENDENTLY_VERIFIED", "owner_approval": "NOT_ESTABLISHED", "benefit_amount": None})
    implementation = {**common, "register_id": "R11-IMPLEMENTATION-EVIDENCE-1", "records": evidence, "observed_verified_implementation_count": 0,
        "zero_count_meaning": "No implementation verification established in this view; not zero reforms implemented in the UN."}
    metrics = [
        ("R-M01", "Obligation applicability coverage", "Reviewed applicable provisions / extracted provisions; report excluded and unresolved separately", "Legal/substantive applicability review per action/entity/period", "No global compliance score from a selected corpus"),
        ("R-M02", "Implementation evidence coverage", "Material action components with authenticated implementation evidence / all material components in defined scope", "Dated administrative/operational records with coverage assessment", "Reported and verified evidence remain separate"),
        ("R-M03", "Service continuity", "Completed required outputs and timeliness against prospectively specified baseline and intervention periods", "Workload, service-level, quality, incident and readiness records", "Mandate delivery, safety and readiness must remain within approved thresholds"),
        ("R-M04", "Full-system net cost", "Comparable counterfactual system cost minus intervention system cost, including transition and transferred work", "Matched cost objects, full-system ledger and independent financial review", "No savings designation before FINANCIALLY_VALIDATED; no sum across overlapping pools"),
        ("R-M05", "Capacity released and used", "Observed reusable work hours separated from released payroll or external expenditure", "Time observations, staffing and redeployment records", "Capacity is not a cashable saving; preserve output quality"),
        ("R-M06", "Due-action evidence completeness", "Due applicable actions with adequate performance evidence / due applicable actions", "Sourced deadlines, applicability review and complete performance population", "Missing evidence is not noncompliance")]
    metric_view = {**common, "register_id": "R13-MEASURES-GUARDS-1", "metrics": [{"metric_id": ident, "name": name, "definition": definition, "minimum_evidence": minimum, "guardrail": guard, "observed_value": None, "target": None, "threshold_status": "REQUIRES_OWNER_APPROVED_PROSPECTIVE_SPECIFICATION", "measurement_status": "NOT_MEASURED"} for ident, name, definition, minimum, guard in metrics]}
    requests = []
    for symbol in sorted({r["document_symbol"] for r in obligations}):
        refs = [r["obligation_id"] for r in obligations if r["document_symbol"] == symbol]
        requests.append({"request_id": "R-EVID-" + str(len(requests)+1).zfill(2), "instrument": symbol, "related_provisions": refs,
            "public_evidence_needed": ["Final text/corrigenda completeness refresh and adopted follow-up instruments through release cutoff", "Public Secretary-General implementation reports with paragraph-level attribution"],
            "controlled_evidence_if_authorized": ["Action-specific accountable owner and authorized implementation decision", "Dated implementation records and material component coverage", "Performance population, exceptions and service guardrail records", "Full-system cost records only where a financial effect is claimed"],
            "proposed_custodian_role": "Responsible substantive office and records custodian; exact custodian not yet confirmed",
            "custodian_accepted": False, "status": "DRAFT_NOT_SENT", "sent_at": None, "response_received_at": None,
            "handling": "Do not send automatically or place restricted records in Git; use approved intake after custodian authorization.",
            "minimum_scope_rule": "Request only the applicable action/entity/period; resolve applicability before collecting transaction-level records."})
    requests.append({"request_id": "R-EVID-GA81", "instrument": "GA81_SESSION_CORPUS", "related_provisions": [], "public_evidence_needed": ["Complete adopted resolution/decision inventory through cutoff", "Final operative text of potentially relevant instruments and adoption records"], "controlled_evidence_if_authorized": [], "proposed_custodian_role": "Public official document services", "custodian_accepted": False, "status": "DRAFT_NOT_SENT", "sent_at": None, "response_received_at": None, "handling": "Public-source research only; no presumed missing mandatory actions.", "minimum_scope_rule": "Extract adopted action only after authenticating final text and applicability."})
    request_view = {**common, "register_id": "R14-MINIMUM-EVIDENCE-REQUESTS-1", "requests": requests, "requests_sent": 0, "responses_obtained": 0}
    effects = dict(sorted(Counter(r["provision"]["effect"] for r in obligations).items()))
    states = dict(sorted(Counter(r["compliance"]["status"] for r in obligations).items()))
    release = {**common, "release_id": "R18-PARTIAL-REFORM-BASELINE-1", "release_class": "PARTIAL_PUBLIC_RESEARCH_BASELINE", "extracted_provision_count": len(obligations), "operative_effect_counts": effects,
        "compliance_declarations": states, "verified_compliance_findings": 0, "verified_incremental_savings": None,
        "ga81_action_extraction": inputs["data/reforms/unga81_actions.json"]["extraction_status"],
        "retained_sg_or_arrangement_records": len(proposals), "retained_acabq_recommendations": len(inputs["data/reforms/acabq_recommendations.json"]["recommendations"]),
        "review_receipt": "docs/reform_independent_review.md", "review_scope_rule": "Separate-agent review must state which primary sources were independently inspected; generator does not certify review completion.",
        "supersession_rule": "Refresh requires new source hashes and explicit changed provision/adoption/applicability dispositions; does not supersede institutional instruments.",
        "completion_gate": "NOT_A_COMPLETE_COMPLIANCE_OR_OPERATIONAL_ADJUDICATION"}
    lines = ["# Reform compliance view — R16", "", "This is a partial public research baseline. It does not establish portfolio compliance, implementation or savings.", "",
        f"The selected GA80/GA81 extraction contains **{len(obligations)} provision records**, with operative effects {json.dumps(effects, sort_keys=True)}. These are not {len(obligations)} verified mandatory requirements applicable to every mission. The GA81 extraction remains `{release['ga81_action_extraction']}`; its empty action list does not establish zero applicable obligations.", "",
        f"Declared provision assessment states are {json.dumps(states, sort_keys=True)}. No compliant/noncompliant performance finding has been verified in this view. Deadlines and conditions remain attached to individual provisions; unknown deadlines are not treated as overdue.", "",
        f"The baseline also retains {len(proposals)} proposal/reported-arrangement records and {release['retained_acabq_recommendations']} ACABQ recommendations. Advice, proposals, adopted provisions and implementation evidence remain separate. No incremental saving is estimated.", "",
        "The [crosswalk](../data/reforms/obligation_crosswalk.json) preserves extracted entities/functions, deadlines and conditions. Any candidate text matches are preliminary research leads requiring substantive applicability review. No appropriation or cost-object relationship has been adjudicated.", "",
        "The [implementation view](../data/reforms/implementation_evidence.json) records evidence limits; a zero verification count is not a finding that the UN implemented nothing. The [metric definitions](../data/reforms/reform_metrics.json) specify evidence and safeguards, with observations and prospective thresholds unmeasured or unapproved. The [minimum evidence requests](../data/reforms/evidence_requests.json) are drafts: none has been sent and no owner acceptance is established.", "",
        "Read the [separate-agent review](reform_independent_review.md) for its actual inspection scope and unresolved issues. The [versioned release record](../data/reforms/baseline_release.json) hashes source inputs and labels this release PARTIAL_PUBLIC_RESEARCH_BASELINE. Repository validation authenticates declaration consistency only; it does not certify legal interpretation, complete session coverage, implementation or financial benefit.", ""]
    return {"data/reforms/obligation_crosswalk.json": cross, "data/reforms/implementation_evidence.json": implementation,
            "data/reforms/reform_metrics.json": metric_view, "data/reforms/evidence_requests.json": request_view,
            "data/reforms/baseline_release.json": release, "docs/reform_compliance_view.md": "\n".join(lines)}


def outputs(root=ROOT):
    return {path: value if isinstance(value, str) else json.dumps(value, indent=2, ensure_ascii=False) + "\n" for path, value in build(root).items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    for path, content in outputs().items():
        target = ROOT / path
        if args.write:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
        elif not target.exists() or target.read_text() != content:
            stale.append(path)
    if stale:
        raise SystemExit("Stale reform views: " + ", ".join(stale))
    print("Reform views written." if args.write else "Reform views are deterministic and current; substantive conclusions remain qualified.")


if __name__ == "__main__":
    main()
