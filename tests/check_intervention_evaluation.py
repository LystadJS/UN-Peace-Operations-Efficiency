#!/usr/bin/env python3
"""Synthetic corruption and adverse-case checks; no operational evidence."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("intervention", ROOT / "scripts/evaluate_intervention.py")
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


def cost(ident, amount, entity="SOURCE", boundary="EXTERNAL_COST", role="RETAINED_SOURCE", pair=None):
    return {"record_id": ident, "cost_object_id": ident, "component_id": "bounded-component", "entity_id": entity, "role": role, "economic_boundary": boundary, "amount": amount, "source_receipt": "SYNTHETIC_ONLY", "included_in": None, "internal_pair_id": pair, "transfer_id": "SYNTHETIC_TRANSFER" if pair else None}


def fixture():
    frame = {"period_start": "2026-01-01", "period_end": "2026-12-31", "currency": "USD", "unit": "currency_units", "financial_status": "HYPOTHETICAL_COST", "price_basis": "constant-2026", "cost_view": "RESOURCE_ACCRUAL", "service_definition": "same fictional service", "required_output": "same fictional specification", "entity_scope": ["SOURCE", "RECEIVER"], "adjustment_receipts": {x: "SYNTHETIC_REVIEW" for x in model.ADJUSTMENTS}, "coverage": {"all_affected_entities": True, "all_cost_components": True, "receipt": "SYNTHETIC_COVERAGE", "omitted_components": []}}
    baseline, intervention = copy.deepcopy(frame), copy.deepcopy(frame)
    baseline["costs"] = [cost("source", "100"), cost("provider", "30", "RECEIVER", role="RECEIVING_PROVIDER"), cost("payer", "30", pair="transfer", boundary="INTERNAL_CHARGE"), cost("recovery", "-30", "RECEIVER", "INTERNAL_RECOVERY", pair="transfer")]
    intervention["costs"] = [cost("source", "40"), cost("provider", "50", "RECEIVER", role="RECEIVING_PROVIDER"), cost("transition", "20", role="TRANSITION_IMPLEMENTATION"), cost("ongoing", "10", role="ONGOING_COMPLIANCE"), cost("liability", "5", role="RESIDUAL_LIABILITY"), cost("payer", "40", pair="transfer", boundary="INTERNAL_CHARGE"), cost("recovery", "-40", "RECEIVER", "INTERNAL_RECOVERY", pair="transfer")]
    return {"case_id": "SYNTHETIC_A", "evidence_mode": "SYNTHETIC", "baseline": baseline, "intervention_scenario": intervention, "counterfactual": {"frozen": True, "baseline_version": "SYNTHETIC_1", "receipt": "SYNTHETIC_BASELINE", "feasible": True, "confounder_review_receipt": "SYNTHETIC_CONFOUNDERS", "prebooked_included": True, "prebooked_receipt": "SYNTHETIC_PREBOOKED"}, "guards": [{"dimension": x, "status": "PASS", "receipt": "SYNTHETIC_EVIDENCE", "threshold_receipt": "SYNTHETIC_PROSPECTIVE_LIMIT", "owner_approval_receipt": "SYNTHETIC_ONLY_NO_AUTHORITY"} for x in model.GUARDS], "priority_inputs": {"criteria": {x: {"value": "0.5", "receipt": "SYNTHETIC_RUBRIC"} for x in model.CRITERIA}, "weights": {x: "0.2" for x in model.CRITERIA}, "weight_receipt": "SYNTHETIC_ILLUSTRATIVE_ONLY"}, "benefit_effects": []}


class EvaluationTests(unittest.TestCase):
    def test_full_system_cost_and_transfer_elimination(self):
        result = model.evaluate(fixture())
        self.assertEqual(result["cost_comparison"]["baseline_external_cost"], "130")
        self.assertEqual(result["cost_comparison"]["intervention_external_cost"], "125")
        self.assertEqual(result["cost_comparison"]["net_cost_difference"], "5")
        self.assertEqual(result["cost_comparison"]["eliminated_internal_pairs"]["baseline"], ["transfer"])
        self.assertIsNone(result["savings_amount"])
        self.assertFalse(result["candidate_advanced"])

    def test_transfer_increase_does_not_change_external_difference(self):
        value = fixture()
        value["intervention_scenario"]["costs"][-2]["amount"] = "4000000"
        value["intervention_scenario"]["costs"][-1]["amount"] = "-4000000"
        self.assertEqual(model.evaluate(value)["cost_comparison"]["net_cost_difference"], "5")

    def test_unmatched_transfer_withholds_comparison(self):
        value = fixture()
        value["intervention_scenario"]["costs"][-1]["amount"] = "-39"
        self.assertIsNone(model.evaluate(value)["cost_comparison"]["net_cost_difference"])

    def test_transfer_identity_mismatch_is_not_eliminated(self):
        value = fixture()
        value["intervention_scenario"]["costs"][-1]["transfer_id"] = "OTHER_TRANSFER"
        self.assertEqual(model.evaluate(value)["cost_comparison"]["status"], "NOT_COMPUTABLE")

    def test_unknown_is_not_zero(self):
        value = fixture()
        value["intervention_scenario"]["costs"][0].update(amount=None, missing_reason="Not obtained")
        self.assertIsNone(model.evaluate(value)["cost_comparison"]["baseline_external_cost"])

    def test_adverse_cost_difference_is_preserved(self):
        value = fixture()
        value["intervention_scenario"]["costs"][0]["amount"] = "140"
        result = model.evaluate(value)
        self.assertEqual(result["cost_comparison"]["net_cost_difference"], "-95")
        self.assertIsNone(result["savings_amount"])

    def test_observed_zero_requires_explicit_rows_and_receipts(self):
        value = fixture()
        value["intervention_scenario"]["costs"][0]["amount"] = "45"
        self.assertEqual(model.evaluate(value)["cost_comparison"]["net_cost_difference"], "0")
        value["intervention_scenario"]["costs"][0]["source_receipt"] = None
        self.assertIsNone(model.evaluate(value)["cost_comparison"]["net_cost_difference"])

    def test_frames_must_match(self):
        for field, replacement in [("currency", "EUR"), ("period_end", "2027-06-30"), ("unit", "thousands"), ("financial_status", "PAID"), ("service_definition", "reduced service"), ("required_output", "removed output"), ("cost_view", "CASH")]:
            with self.subTest(field=field):
                value = fixture()
                value["intervention_scenario"][field] = replacement
                self.assertIsNone(model.evaluate(value)["cost_comparison"]["net_cost_difference"])

    def test_prebooked_measures_must_be_in_counterfactual(self):
        value = fixture()
        value["counterfactual"]["prebooked_included"] = False
        self.assertIsNone(model.evaluate(value)["cost_comparison"]["net_cost_difference"])

    def test_omitted_receiving_cost_blocks(self):
        value = fixture()
        value["intervention_scenario"]["coverage"]["omitted_components"] = ["receiving staff"]
        self.assertIsNone(model.evaluate(value)["cost_comparison"]["net_cost_difference"])

    def test_transfer_only_receiver_does_not_mean_free_provider(self):
        value = fixture()
        value["intervention_scenario"]["costs"] = [row for row in value["intervention_scenario"]["costs"] if row["record_id"] != "provider"]
        self.assertIsNone(model.evaluate(value)["cost_comparison"]["net_cost_difference"])

    def test_parent_and_child_double_count_rejected(self):
        value = fixture()
        value["baseline"]["costs"][1]["included_in"] = "source"
        self.assertIsNone(model.evaluate(value)["cost_comparison"]["net_cost_difference"])

    def test_duplicate_component_rejected(self):
        value = fixture()
        extra = copy.deepcopy(value["baseline"]["costs"][0])
        extra["record_id"] = "different-row-same-effect"
        value["baseline"]["costs"].append(extra)
        self.assertIsNone(model.evaluate(value)["cost_comparison"]["net_cost_difference"])

    def test_exact_decimal_arithmetic(self):
        value = fixture()
        value["baseline"]["costs"] = [cost("a", "0.1"), cost("b", "0.2", "RECEIVER")]
        value["intervention_scenario"]["costs"] = [cost("c", "0.3"), cost("d", "0", "RECEIVER")]
        self.assertEqual(model.evaluate(value)["cost_comparison"]["net_cost_difference"], "0.0")

    def test_float_nan_and_boolean_rejected(self):
        for bad in [0.1, True, "NaN", "Infinity", "1e3"]:
            with self.subTest(bad=bad):
                value = fixture()
                value["baseline"]["costs"][0]["amount"] = bad
                self.assertIsNone(model.evaluate(value)["cost_comparison"]["net_cost_difference"])

    def test_failed_guard_overrides_favorable_financial_difference(self):
        value = fixture()
        value["guards"][0]["status"] = "FAIL"
        result = model.evaluate(value)
        self.assertEqual(result["cost_comparison"]["net_cost_difference"], "5")
        self.assertEqual(result["prioritization"]["status"], "BLOCKED")
        self.assertIsNone(result["prioritization"]["score"])

    def test_unknown_guard_and_missing_score_are_unscorable(self):
        value = fixture()
        value["guards"][1]["status"] = "UNKNOWN"
        self.assertEqual(model.evaluate(value)["prioritization"]["status"], "UNSCORABLE")
        value = fixture()
        value["priority_inputs"]["criteria"]["evidence_readiness"] = None
        self.assertEqual(model.evaluate(value)["prioritization"]["status"], "UNSCORABLE")

    def test_owner_receipts_and_reviewed_weights_required(self):
        value = fixture()
        value["guards"][0]["owner_approval_receipt"] = None
        self.assertEqual(model.evaluate(value)["prioritization"]["status"], "UNSCORABLE")
        value = fixture()
        value["priority_inputs"]["weights"] = None
        self.assertEqual(model.evaluate(value)["prioritization"]["status"], "UNSCORABLE")

    def test_effect_classes_do_not_add_same_dollar_twice(self):
        value = fixture()
        effect = {"effect_id": "one", "cost_object_id": "purchase", "component_id": "same", "benefit_pool_id": "pool", "period": "2026", "unit": "USD", "source_receipt": "SYNTHETIC", "benefit_class": "COST_AVOIDANCE", "amount": "10"}
        value["benefit_effects"] = [effect, {**effect, "effect_id": "two", "benefit_class": "RECOVERY"}]
        self.assertEqual(model.evaluate(value)["benefits"]["status"], "INVALID")

    def test_unknown_effect_stays_null_and_savings_class_rejected(self):
        value = fixture()
        effect = {"effect_id": "one", "cost_object_id": "purchase", "component_id": "same", "benefit_pool_id": "pool", "period": "2026", "unit": "USD", "source_receipt": "SYNTHETIC", "benefit_class": "COST_AVOIDANCE", "amount": None, "missing_reason": "Not measured"}
        value["benefit_effects"] = [effect]
        self.assertIsNone(model.evaluate(value)["benefits"]["effects"][0]["amount"])
        effect["benefit_class"] = "REALIZED_SAVING"
        self.assertEqual(model.evaluate(value)["benefits"]["status"], "INVALID")

    def test_weight_sensitivity_reversal_and_blocked_case(self):
        a, b, blocked = fixture(), fixture(), fixture()
        b["case_id"], blocked["case_id"] = "SYNTHETIC_B", "SYNTHETIC_BLOCKED"
        a["priority_inputs"]["criteria"]["evidence_readiness"]["value"] = "1"
        a["priority_inputs"]["criteria"]["operational_importance"]["value"] = "0"
        b["priority_inputs"]["criteria"]["evidence_readiness"]["value"] = "0"
        b["priority_inputs"]["criteria"]["operational_importance"]["value"] = "1"
        blocked["guards"][0]["status"] = "FAIL"
        vectors = [{"id": criterion, "weights": {x: "1" if x == criterion else "0" for x in model.CRITERIA}} for criterion in ("evidence_readiness", "operational_importance")]
        result = model.sensitivity({"cases": [a, b, blocked], "vectors": vectors, "illustrative": True})
        self.assertEqual(result["pairwise_reversals"], [["SYNTHETIC_A", "SYNTHETIC_B"]])
        self.assertEqual(result["rank_intervals"]["SYNTHETIC_A"]["worst"], 2)
        self.assertIsNone(result["rank_intervals"]["SYNTHETIC_BLOCKED"]["best"])

    def test_unpopulated_template_is_not_promoted(self):
        template = json.loads((ROOT / "data/portfolio/case_dossier_template.json").read_text())
        result = model.evaluate(template)
        self.assertEqual(result["cost_comparison"]["status"], "NOT_COMPUTABLE")
        self.assertEqual(result["prioritization"]["status"], "UNSCORABLE")
        self.assertFalse(result["candidate_advanced"])


if __name__ == "__main__":
    unittest.main()
