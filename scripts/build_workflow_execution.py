#!/usr/bin/env python3
"""Build a roadmap ledger separating delivered artifacts from substantive execution."""
import argparse
from collections import Counter
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODES = {"DOCUMENTED_STANDARD", "RESEARCH_CONTROL", "PARTIAL_AUTHORITY_BASELINE", "SCREENING_BLOCKED", "DRAFT_UNSENT", "PREPARATION_ONLY", "BLOCKED_NOT_EXECUTED", "PUBLIC_RESEARCH_OUTPUT", "PUBLIC_VALIDATION_BASELINE", "TEMPLATE_NOT_EXECUTED"}

# Each tuple is a bounded one-prompt work definition and its principal result.
CATALOG = {
"F": [
("Define desired end state and portfolio completion criteria", "docs/desired_end_state.md"),
("Define the eight controlled efficiency and benefit terms", "docs/decision_taxonomy.md"),
("Define candidate states and evidence thresholds with a validator", "data/standards/candidate_states.json"),
("Define source authority and claim-specific evidence hierarchy", "docs/source_authority_standard.md"),
("Define financial perimeter, nonadditivity and counterfactual rules", "docs/cost_accounting_standard.md"),
("Define mandate, safety, readiness, quality and transition safeguards", "docs/guardrail_standard.md")],
"A": [
("Inventory and classify every frozen-scope repository file", "metadata/artifact_inventory.csv"),
("Catalog every frozen dataset's grain, keys, period, sources and limits", "metadata/dataset_registry.csv"),
("Define orthogonal repository currency, adoption, approval and implementation states", "metadata/repository_status_schema.json"),
("Map scripts, workflows, sources, tests and generated artifacts", "metadata/lineage_edges.csv"),
("Define one schema for quality issues, gaps, owner questions and release gates", "metadata/master_issue_schema.json"),
("Audit workflow overlap, permissions, publishing and obsolete triggers", "metadata/workflow_audit.csv"),
("Create canonical artifact and release manifests with hashes and supersession", "metadata/canonical_manifest.json"),
("Migrate legacy issue observations losslessly into one register", "data/issues/current_issues.json"),
("Generate authoritative scoped current project status", "docs/current_status.md"),
("Rewrite navigation around Commander's intent, current status and history", "README.md"),
("Test contradictory status, stale current links, lineage and historical marking", "scripts/validate_project_consistency.py"),
("Consolidate routine read-only CI and preserve release-specific checks", "metadata/validation_groups.json"),
("Isolate publication into explicitly triggered provenance-checked workflows", "metadata/publication_policy.json"),
("Generate deterministic structural project-health receipt", "metadata/project_health.json")],
"R": [
("Define obligation schema and authority vocabulary", "data/reforms/obligation_schema.json"),
("Inventory repository UN80, UNGA80/81, ACABQ and reform claims", "metadata/reform_claim_inventory.json"),
("Register official GA80 instruments within declared coverage", "data/reforms/unga80_instruments.json"),
("Register official GA81 instruments at the ongoing-session cutoff", "data/reforms/unga81_instruments.json"),
("Extract supported mandatory actions and qualified operative effects from GA80", "data/reforms/unga80_actions.json"),
("Extract GA81 actions only when adopted operative text is authenticated", "data/reforms/unga81_actions.json"),
("Register ACABQ recommendations separately from adopted authority", "data/reforms/acabq_recommendations.json"),
("Register SG proposals and announced arrangements without assuming approval", "data/reforms/sg_proposals.json"),
("Crosswalk provisions to entities, functions, candidates, dates and gaps", "data/reforms/obligation_crosswalk.json"),
("Reconcile the eleven retained UN80 arrangements and authority status", "data/reforms/un80_arrangement_reconciliation.json"),
("Record implementation evidence and its verification limits", "data/reforms/implementation_evidence.json"),
("Define evidence-qualified reform compliance statuses", "data/reforms/compliance_statuses.json"),
("Define reform efficiency measures and operational guardrails", "data/reforms/reform_metrics.json"),
("Prepare minimum reform evidence requests without dispatch", "data/reforms/evidence_requests.json"),
("Validate authority and implementation declarations", "scripts/validate_reform_baseline.py"),
("Generate executive view of partial reform evidence and compliance gaps", "docs/reform_compliance_view.md"),
("Perform separate-agent review of declared reform source scope", "docs/reform_independent_review.md"),
("Freeze a versioned partial reform research baseline", "data/reforms/baseline_release.json")],
"P": [
("Create canonical identities and explicit unresolved entity references", "data/portfolio/entities.json"),
("Declare dataset contracts without promoting structural profiles to semantic approval", "data/portfolio/dataset_contracts.json"),
("Create a canonical financial baseline with perimeter controls", "data/portfolio/financial_baseline.json"),
("Validate nonadditive financial totals and component relationships", "scripts/validate_financial_nonadditivity.py"),
("Report identity, finance, function, reform and operational coverage separately", "data/portfolio/coverage_matrix.json"),
("Normalize the intervention register and preserve parent-child scope", "data/portfolio/interventions.json"),
("Define nonadditive benefit pools", "data/portfolio/benefit_pools.json"),
("Create standard case dossier template", "data/portfolio/case_dossier_template.json"),
("Define operational metric catalog without invented observations", "data/portfolio/operational_metrics.json"),
("Define service, period and workload comparability adjustments", "data/portfolio/comparability_rules.json"),
("Define full-system cost model including transition and retained cost", "data/portfolio/cost_model.json"),
("Define counterfactual and attribution evidence ladder", "data/portfolio/counterfactual_ladder.json"),
("Define intervention prioritization without fabricated approved rankings", "data/portfolio/prioritization_model.json"),
("Design weight sensitivity analysis and expose unapproved assumptions", "data/portfolio/prioritization_sensitivity.json")],
"E": [
("Prepare minimum RSCE charge, service and retained-work request", "data/evidence_requests/E01_rsce.json"),
("Prepare asset-transfer and avoided-procurement evidence request", "data/evidence_requests/E02_assets.json"),
("Prepare Haiti support service and full-cost request", "data/evidence_requests/E03_haiti.json"),
("Prepare separate translation, transferred-asset, fuel-recovery and medical-control requests", "data/evidence_requests/E04_ga_directed.json"),
("Prepare course-event training administration and procurement request", "data/evidence_requests/E05_training.json"),
("Prepare both-owner review and permitted reporting-workflow evidence request", "data/evidence_requests/E06_reporting_owners.json"),
("Define restricted intake, pseudonymization and public Git exclusion controls", "docs/secure_evidence_intake.md"),
("Validate declared transaction, asset, post, workload and outcome evidence", "scripts/validate_operational_evidence.py"),
("Extend matching for reversals, partial settlement, timing and one-to-many allocation", "scripts/reconcile_evidence_transactions.py"),
("Calculate comparable net-benefit scenarios with operational guardrails", "scripts/calculate_net_benefit.py"),
("Prepare RSCE, UNIFIL and Haiti pilot charters without activation", "data/pilots/charters.json"),
("Define prospective thresholds and stop-rule approval dependencies", "data/pilots/thresholds.json"),
("Create explicitly synthetic data scenarios and analysis templates", "data/pilots/synthetic_scenarios.json"),
("Rehearse public/synthetic method behavior without real-world findings", "data/pilots/rehearsal_receipt.json"),
("Register preparation, dispatch, response and access states separately", "data/pilots/request_status.json")],
"I": [
("Generate public screening portfolio from actual case dispositions", "data/portfolio/public_portfolio.json"),
("Adjudicate authorized restricted evidence and disclose only approved derivatives", "data/portfolio/restricted_adjudication_status.json"),
("Generate overlap graph without adding unverified benefit amounts", "data/portfolio/overlap_graph.json"),
("Create verified-benefit ledger with unknown rather than fabricated zero totals", "data/portfolio/verified_benefit_ledger.json"),
("Reconcile eligible benefit totals and exclude overlaps or embedded baseline effects", "data/portfolio/verified_benefit_ledger.json"),
("Write Commander's decision memo with evidence-qualified next decisions", "docs/commander_decision_memo.md"),
("Write partial reform-to-portfolio decision annex", "docs/reform_portfolio_annex.md"),
("Review portfolio methods and report agent independence boundaries", "data/portfolio/agent_review.json"),
("Publish leadership report on evidence, cases, gaps and actual completion", "docs/leadership_portfolio_report.md"),
("Integrate final roadmap outputs into generated status and README navigation", "metadata/current_status.json"),
("Run full release validation with exact-commit runtime receipts", "data/portfolio/validation_plan.json"),
("Produce an honest versioned public validation release without decision-grade overclaim", "data/portfolio/release_manifest.json")]
}
CASES = ["RSCE charges and retained local work", "UNIFIL–UNSCOL asset reuse", "BINUH–UNSOH support",
         "UNISFA translation", "UNISFA transferred assets", "UNSOS fuel contractor recovery",
         "MONUSCO medical-insurance controls", "UNMISS post changes and service continuity",
         "training administration and procurement", "DPPA–DPO regional functions", "UNOWAS–UNOCA factual support",
         "Cyprus factual support", "UNIFIL residual transition liabilities", "existing joint structures"]
X_STREAMS = ["RSCE", "UNIFIL–UNSCOL", "BINUH–UNSOH", "best eligible GA-directed case", "training", "UNOWAS–UNOCA", "Cyprus"]
WAVE9 = ["Approve intervention charter", "Approve prospective measurement register", "Freeze authenticated baseline",
         "Execute only the authorized intervention", "Measure complete operational and financial outcomes",
         "Reconcile transferred work and residual cost", "Independently review benefit realization",
         "Decide scale, revise, retain or rollback"]


def entries():
    result = []
    for prefix in ("F","A","R","P","C","E","X","I","W9"):
        if prefix == "C":
            catalog = [("Prepare evidence-qualified case dossier for " + label, f"data/cases/C{i:02}.json") for i,label in enumerate(CASES,1)]
        elif prefix == "X":
            catalog = [(phase + " for " + stream, "data/adjudications/execution_gates.json") for stream in X_STREAMS for phase in ("Reconcile authenticated records", "Assess operational counterfactual", "Substantively adjudicate case")]
        elif prefix == "W9":
            catalog = [(work, "data/realization/implementation_gates.json") for work in WAVE9]
        else:
            catalog = CATALOG[prefix]
        for number, (work, path) in enumerate(catalog,1):
            task_id = f"{prefix}{number:02}"
            mode = "RESEARCH_CONTROL"
            blocker = "Underlying source truth and substantive use remain limited to declared scope; passing structure does not establish institutional approval."
            if prefix == "F":
                mode = "DOCUMENTED_STANDARD"
                blocker = "Application to actual cases still requires source evidence and competent ownership."
            elif prefix == "R":
                mode = "PARTIAL_AUTHORITY_BASELINE"
                blocker = "Complete instrument coverage, applicability, final-text verification where missing and implementation evidence remain unresolved."
            elif prefix == "C":
                mode = "SCREENING_BLOCKED"
                blocker = "Authenticated operational/financial population, accepted owner, authority, comparable baseline and prospective safeguards not obtained."
            elif prefix == "E":
                mode = "DRAFT_UNSENT" if number <= 6 or number == 15 else "PREPARATION_ONLY"
                blocker = "Collection and activation require accepted owners, competent authorization, permitted records and prospective thresholds; requests remain unsent."
            elif prefix == "X":
                mode = "BLOCKED_NOT_EXECUTED"
                blocker = "Authorized complete records, accountable owner and substantive review authority not obtained; earlier audit phases are not executed."
            elif prefix == "I":
                mode = "BLOCKED_NOT_EXECUTED" if number == 2 else "PUBLIC_VALIDATION_BASELINE" if number == 12 else "PUBLIC_RESEARCH_OUTPUT"
                blocker = "Decision-grade completion requires substantive operational and financial adjudications; public artifacts cannot supply missing institutional evidence."
                if number == 11:
                    blocker = "Runtime checks require a separate exact-commit clean-worktree receipt in CI artifacts or approved temporary storage; plan existence is not a passing run."
            elif prefix == "W9":
                mode = "TEMPLATE_NOT_EXECUTED"
                blocker = "No intervention has competent institutional approval; instantiate eight steps per approved intervention only after its evidence and authority gates pass."
            result.append({"task_id":task_id, "one_prompt_task":work, "principal_result":path,
                           "work_product_mode":mode, "blocking_dependency":blocker})
    return result


def build(root=ROOT):
    tasks = entries()
    for task in tasks:
        exists = (root / task["principal_result"]).is_file()
        task["artifact_delivery_status"] = "PRESENT" if exists else "PLANNED"
        task["completion_evidence"] = {"artifact_path":task["principal_result"], "artifact_exists":exists,
                                       "verification_scope":"File existence only in this ledger; source-specific validators, substantive reviews and runtime receipts remain separate.",
                                       "substantive_audit_completed":False}
        if task["task_id"] == "I10":
            current = json.loads((root / task["principal_result"]).read_text()) if exists else {}
            integrated = "portfolio" in current or "portfolio_execution" in current
            task["artifact_delivery_status"] = "PRESENT" if integrated else "PLANNED_INTEGRATION"
            task["completion_evidence"]["integration_detected"] = integrated
        if task["task_id"] == "I11":
            task["completion_evidence"]["runtime_validation_attested_by_this_ledger"] = False
        if task["task_id"] == "I12":
            task["completion_evidence"]["decision_grade_operational_release"] = False
    result = {"schema_version":1, "ledger_id":"WORKFLOW-EXECUTION-1", "as_of":"2026-10-23",
              "scope":"114 fixed roadmap tasks plus eight conditional Wave9 template steps; templates repeat only for institutionally approved interventions.",
              "counts":{"fixed_tasks":114,"conditional_template_steps":8,"total_entries":len(tasks),
                        "artifact_delivery":dict(sorted(Counter(t["artifact_delivery_status"] for t in tasks).items())),
                        "work_product_modes":dict(sorted(Counter(t["work_product_mode"] for t in tasks).items())),
                        "substantive_operational_audits_completed":0,"minimum_required_operational_audits":3,
                        "minimum_service_types":2,"financial_adjudications_completed":0},
              "completion_gates":[{"gate":1,"status":"PARTIAL","reason":"Controls and identities exist; complete lifecycle, mandate, instrument and operational-perimeter coverage remain open."},
                                  {"gate":2,"status":"PARTIAL","reason":"Dossiers, tools and rehearsals exist; actual baselines, accepted owners and prospective numeric thresholds remain missing."},
                                  {"gate":3,"status":"BLOCKED","reason":"Zero substantive operational audits against at least three across two service types, and no financial adjudication."},
                                  {"gate":4,"status":"BLOCKED","reason":"No approved implementation, verified realization or substantively accepted no-change decision."}],
              "claim_boundary":"Artifact delivery, eligibility disposition, synthetic rehearsal and substantive execution are separate. PRESENT never means operationally completed. No commit SHA or runtime CI result is inferred.",
              "tasks":tasks}
    validate(result)
    return result


def validate(value):
    catalog = {e["task_id"]:e for e in entries()}
    expected = set(catalog)
    actual = [e["task_id"] for e in value["tasks"]]
    if len(actual) != 122 or len(set(actual)) != 122 or set(actual) != expected:
        raise ValueError("Roadmap task population differs from 114 fixed plus eight conditional steps")
    for task in value["tasks"]:
        if task["work_product_mode"] not in MODES or task["artifact_delivery_status"] not in {"PRESENT","PLANNED","PLANNED_INTEGRATION"}:
            raise ValueError("Invalid or falsely closed task state")
        if task["completion_evidence"]["substantive_audit_completed"] is not False:
            raise ValueError("No substantive execution evidence exists for this release")
        if task["work_product_mode"] != catalog[task["task_id"]]["work_product_mode"]:
            raise ValueError("Task mode differs from this evidence-qualified release catalog")
        if task["principal_result"] != catalog[task["task_id"]]["principal_result"]:
            raise ValueError("Task result differs from the explicit artifact catalog")
        if task["task_id"].startswith("X") and task["work_product_mode"] != "BLOCKED_NOT_EXECUTED":
            raise ValueError("Operational execution must remain blocked")
        if task["task_id"].startswith("W9") and task["work_product_mode"] != "TEMPLATE_NOT_EXECUTED":
            raise ValueError("Conditional realization templates were not executed")
        if not task["one_prompt_task"] or not task["principal_result"] or not task["blocking_dependency"]:
            raise ValueError("Task lacks reviewable work or dependency")


def render(value):
    lines = ["# Workflow execution ledger", "", "**The roadmap has 114 fixed tasks and eight conditional realization templates; artifact delivery does not establish substantive completion.** The [machine-readable ledger](../data/portfolio/workflow_execution.json) enumerates all 122 entries with a bounded one-prompt definition, principal result, existence check and unresolved dependency. Repeated Wave9 steps apply only to institutionally approved interventions; none is approved here.", "", "There are zero substantive operational audits against the required minimum three across two service types, and no financial adjudication. All 21 X steps remain blocked and unexecuted. All fourteen C packets remain screening work; I02 is a blocked restricted-evidence disposition, and I12 is a public validation baseline rather than a decision-grade operational release. R03/R04 source work and the wider authority baseline retain explicit partial coverage.", "", "| Completion gate | Status |", "| --- | --- |"]
    lines.extend(f"| {g['gate']} | {g['status']}: {g['reason']} |" for g in value["completion_gates"])
    lines += ["", "A `PRESENT` result means only that its declared file exists. It does not authenticate a source, approve an owner, send a request, execute a pilot or attest a passing runtime check. Planned integration and missing outputs remain visible. Runtime receipts belong to the exact tested commit in CI artifacts or approved temporary storage; this deterministic ledger invents no commit SHA or CI outcome.", "", "| ID | One-prompt task | Principal result | Work-product mode | Delivery |", "| --- | --- | --- | --- | --- |"]
    for task in value["tasks"]:
        lines.append(f"| {task['task_id']} | {task['one_prompt_task']} | [{task['principal_result']}](../{task['principal_result']}) | {task['work_product_mode']} | {task['artifact_delivery_status']} |")
    lines += ["", "The JSON contains each task's completion-evidence boundary and blocking dependency. Regenerate after final artifacts or integration change:", "", "```sh", "python -B scripts/build_workflow_execution.py --write", "python -B scripts/build_workflow_execution.py --check", "python -B tests/check_workflow_execution.py", "```", "", "Advancement beyond this ledger requires actual evidence and competent institutional authority. Honest blocked dispositions preserve the work queue and do not count toward substantive portfolio completion.", ""]
    return "\n".join(lines)


def outputs(root=ROOT):
    value = build(root)
    return {"data/portfolio/workflow_execution.json":json.dumps(value,indent=2,ensure_ascii=False)+"\n", "docs/workflow_execution.md":render(value)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write",action="store_true")
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    if args.write and args.check:
        parser.error("choose --write or --check")
    for path, content in outputs().items():
        target=ROOT/path
        if args.write:
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(content,encoding="utf-8")
        elif not target.exists() or target.read_text(encoding="utf-8") != content:
            raise SystemExit("Stale workflow execution output: "+path)
    print("Workflow task population and artifact/execution boundaries passed.")


if __name__ == "__main__":
    main()
