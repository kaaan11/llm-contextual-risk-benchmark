"""Phase 7E — researcher review, pre-registration and freeze-integrity tests."""

from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_phase7e_review import validate  # noqa: E402

REVIEW = ROOT / "results" / "dataset_audit" / "phase7e_review.json"
HASHREC = ROOT / "results" / "dataset_audit" / "phase7e_preregistration_hash.json"
PREREG = ROOT / "docs" / "phase7e_preregistration.md"
PROTOCOL = ROOT / "docs" / "phase7e_annotation_protocol.md"
REVIEW_DOC = ROOT / "docs" / "phase7e_researcher_review.md"
DESIGN_DOC = ROOT / "docs" / "PHASE_7D_EXPERIMENTAL_DESIGN.md"
DESIGN_TABLE = ROOT / "docs" / "PHASE_7D_DESIGN_TABLE.md"

EXPECTED_CATEGORIES = {
    "dual_use_nonnull": 30,
    "persistent_ambiguity": 7,
    "null_benign": 7,
    "null_highrisk": 6,
}
VALID_DECISIONS = {"PENDING", "KEEP", "REVISE", "REJECT"}
VALID_VALENCE = {
    "clearly_benign", "probably_benign", "ambiguous_dual_use",
    "probably_concerning", "clearly_concerning",
}
VALID_CONTROL = {"T", "N", "F"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class Phase7EFilesExistTests(unittest.TestCase):
    def test_all_phase7e_outputs_exist(self):
        for path in (REVIEW, HASHREC, PREREG, PROTOCOL, REVIEW_DOC, DESIGN_DOC, DESIGN_TABLE):
            self.assertTrue(path.exists(), f"missing Phase 7E output: {path}")


class ReviewRecordTests(unittest.TestCase):
    def setUp(self):
        self.record = load(REVIEW)
        self.items = self.record["items"]

    def test_all_fifty_items_present_and_unique(self):
        self.assertEqual(len(self.items), 50)
        ids = [i["research_item_id"] for i in self.items]
        self.assertEqual(len(set(ids)), 50)

    def test_category_distribution_matches_design(self):
        counts = {}
        for item in self.items:
            cat = item["versions"][0]["design"]["category"]
            counts[cat] = counts.get(cat, 0) + 1
        self.assertEqual(counts, EXPECTED_CATEGORIES)

    def test_every_item_has_a_review_status(self):
        for item in self.items:
            self.assertIn("review_decision", item)
            self.assertIn(item["review_decision"], VALID_DECISIONS)

    def test_nothing_was_auto_approved(self):
        """Approval must trace to an explicit human decision, never to the agent."""
        self.assertFalse(self.record["auto_approval_performed"])
        for item in self.items:
            if item["researcher_approved"]:
                self.assertEqual(item["review_decision"], "KEEP")
                self.assertTrue(item["reviewer_id"] or item["reviewer_role"])
                self.assertTrue(item["review_timestamp"])
        self.assertEqual(self.record["counts"]["approved"],
                         sum(1 for i in self.items if i["researcher_approved"]))

    def test_reviewer_identity_is_not_fabricated(self):
        """No invented reviewer_id. Only what the human actually supplied."""
        for item in self.items:
            self.assertIsNone(item["reviewer_id"],
                              "reviewer_id must stay null unless a human supplied one")
            if item["review_decision"] == "PENDING":
                self.assertIsNone(item["reviewer_role"])
                self.assertIsNone(item["review_timestamp"])
                self.assertIsNone(item["researcher_notes"])
        for entry in self.record["reviewer_registry"]:
            self.assertIsNone(entry["reviewer_id"])
            self.assertTrue(entry["reviewer_role"])

    def test_approved_items_must_carry_valid_metadata(self):
        """Any item claiming approval must have complete, valid design metadata."""
        required = (
            "research_item_id", "triplet_id", "category", "context_mechanism",
            "canonical_final_prompt_intent", "isolated_prompt_target_valence",
            "legitimating_context_intent", "incriminating_context_intent",
            "expected_context_effect", "expected_risk_profile",
            "intended_turn_count", "control_strategy", "safety_constraints",
        )
        for item in self.items:
            if not item["researcher_approved"]:
                continue
            design = item["versions"][item["current_version"] - 1]["design"]
            for field in required:
                self.assertIn(field, design)
                self.assertNotIn(design[field], (None, ""), f"{item['research_item_id']}.{field}")
            self.assertEqual(item["review_decision"], "KEEP")
            self.assertIsNotNone(item["reviewer_id"] or item["reviewer_role"])
            self.assertIsNotNone(item["review_timestamp"])

    def test_rejected_items_cannot_be_approved_without_revision(self):
        for item in self.items:
            if item["review_decision"] == "REJECT":
                self.assertFalse(item["researcher_approved"])
            if item["review_decision"] in {"REJECT", "REVISE"}:
                self.assertFalse(
                    item["researcher_approved"],
                    "an item under REJECT/REVISE must not be approved",
                )
            # approval requires the current version to have been reviewed as KEEP
            if item["researcher_approved"]:
                self.assertEqual(item["review_decision"], "KEEP")

    def test_version_one_is_preserved_and_policy_declared(self):
        policy = self.record["versioning_policy"]
        self.assertTrue(policy["version_1_immutable"])
        self.assertTrue(policy["revise_creates_version_2"])
        self.assertTrue(policy["approval_resets_on_revision"])
        for item in self.items:
            versions = item["versions"]
            self.assertGreaterEqual(len(versions), 1)
            self.assertEqual(versions[0]["version"], 1)
            self.assertEqual(versions[0]["source_phase"], "7D")
            self.assertIn("design", versions[0])
            # a revision must carry a reason and a timestamp
            for v in versions[1:]:
                self.assertIsNotNone(v["revision_reason"])
                self.assertIsNotNone(v["revision_timestamp"])

    def test_design_metadata_is_valid(self):
        for item in self.items:
            design = item["versions"][0]["design"]
            self.assertIn(design["category"], EXPECTED_CATEGORIES)
            self.assertIn(design["isolated_prompt_target_valence"], VALID_VALENCE)
            self.assertIn(design["control_strategy"], VALID_CONTROL)
            self.assertIsInstance(design["intended_turn_count"], int)
            self.assertGreaterEqual(design["intended_turn_count"], 2)
            self.assertTrue(design["safety_constraints"].strip())

    def test_target_valence_matches_category_role(self):
        for item in self.items:
            design = item["versions"][0]["design"]
            cat, valence = design["category"], design["isolated_prompt_target_valence"]
            if cat in {"dual_use_nonnull", "persistent_ambiguity"}:
                self.assertEqual(valence, "ambiguous_dual_use")
            elif cat == "null_benign":
                self.assertEqual(valence, "clearly_benign")
            elif cat == "null_highrisk":
                self.assertEqual(valence, "clearly_concerning")

    def test_null_items_use_the_null_control_strategy(self):
        for item in self.items:
            design = item["versions"][0]["design"]
            if design["category"] in {"null_benign", "null_highrisk"}:
                self.assertEqual(design["control_strategy"], "F")

    def test_downstream_gates_are_not_started(self):
        for item in self.items:
            self.assertEqual(item["blind_isolated_prompt_review"]["status"], "NOT_STARTED")
            self.assertEqual(item["blind_isolated_prompt_review"]["rater_annotations"], [])
            self.assertIsNone(item["blind_isolated_prompt_review"]["gate_result"])
            self.assertEqual(item["refusal_appropriateness_reference"]["status"], "NOT_STARTED")
            for value in item["refusal_appropriateness_reference"]["by_condition"].values():
                self.assertIsNone(value)


class NoStimulusYetTests(unittest.TestCase):
    """Phase 7E must not produce final prompts, conversations or model output."""

    def test_no_final_prompt_fields_exist(self):
        record = load(REVIEW)
        self.assertFalse(record["final_prompts_exist"])
        self.assertFalse(record["stimulus_generation_permitted"])
        self.assertFalse(record["model_evaluation_permitted"])
        banned = (
            "canonical_final_prompt", "canonical_final_prompt_sha256", "final_prompt_text",
            "turns", "evaluation_conditions", "model_disposition", "model_observed_effect",
        )
        blob = json.dumps(record)
        for key in banned:
            self.assertNotIn(f'"{key}"', blob, f"Phase 7E must not contain field {key!r}")

    def test_only_intent_level_prompt_metadata_present(self):
        for item in load(REVIEW)["items"]:
            design = item["versions"][0]["design"]
            self.assertIn("canonical_final_prompt_intent", design)
            self.assertNotIn("canonical_final_prompt", design)

    def test_no_evaluation_results_recorded(self):
        state = load(HASHREC)["evaluation_state"]
        self.assertFalse(state["model_evaluation_performed"])
        self.assertFalse(state["api_calls_made"])
        self.assertFalse(state["final_prompts_authored"])
        self.assertFalse(state["results_observed"])

    def test_phase7e_scripts_make_no_network_calls(self):
        forbidden = ("requests", "urllib", "httpx", "socket", "openai", "anthropic", "aiohttp")
        for name in ("build_phase7e_review.py", "freeze_phase7e_preregistration.py"):
            source = (ROOT / "scripts" / name).read_text(encoding="utf-8")
            imports = re.findall(r"^\s*(?:import|from)\s+([\w\.]+)", source, re.MULTILINE)
            for mod in imports:
                self.assertNotIn(
                    mod.split(".")[0], forbidden,
                    f"{name} imports network-capable module {mod!r}",
                )


class ProtectedDataUnchangedTests(unittest.TestCase):
    def test_turkish_and_public_datasets_are_byte_identical(self):
        record = load(HASHREC)
        self.assertTrue(record["all_protected_unchanged"])
        for rel, entry in record["protected_files"].items():
            path = ROOT / rel
            self.assertTrue(path.exists(), f"protected file vanished: {rel}")
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(actual, entry["baseline_sha256"], f"{rel} was modified")

    def test_turkish_corpus_is_explicitly_out_of_scope(self):
        text = PREREG.read_text(encoding="utf-8")
        self.assertIn("EXPLORATORY_DRAFT_V0.1_TR", text)
        self.assertIn("out of scope", text)


class PreregistrationConsistencyTests(unittest.TestCase):
    def setUp(self):
        self.text = PREREG.read_text(encoding="utf-8")

    def test_all_hypotheses_present(self):
        for h in ("H1", "H2", "H3", "H0a", "H0b", "H0c"):
            self.assertIn(h, self.text, f"pre-registration is missing hypothesis {h}")

    def test_all_falsification_criteria_present(self):
        for f in ("F1", "F2", "F3", "F4", "F5", "F6"):
            self.assertRegex(self.text, rf"\*\*{f}\*\*", f"missing falsification criterion {f}")

    def test_all_metrics_have_definitions(self):
        required_sections = (
            "Response Disposition Rubric",
            "Contextual Interpretation Metric",
            "Refusal-Appropriateness Metric",
            "ASR Scope",
            "Utility / Task-Completion Metric",
            "Latency / Token Metric",
        )
        for section in required_sections:
            self.assertIn(section, self.text, f"metric section missing: {section}")

    def test_disposition_scale_is_fully_specified(self):
        for label in ("full_compliance", "compliance_with_safeguards", "clarification_request",
                      "partial_refusal", "full_refusal"):
            self.assertIn(label, self.text)
            self.assertIn(label, PROTOCOL.read_text(encoding="utf-8"))

    def test_filler_control_states_are_defined_without_a_hard_zero_gate(self):
        for state in ("negligible_filler_movement", "partial_filler_movement",
                      "comparable_filler_movement", "ambiguous_filler_movement"):
            self.assertIn(state, self.text, f"missing D-control state {state}")

    def test_binary_flag_threshold_is_frozen_with_rationale(self):
        self.assertIn("context_effect_observed", self.text)
        self.assertIn("Threshold rationale", self.text)

    def test_handling_rules_present(self):
        for token in ("unscorable_content", "unscorable_unstable", "missing", "api_error"):
            self.assertIn(token, self.text)
        self.assertIn("No imputation", self.text)

    def test_stopping_and_reporting_rules_present(self):
        self.assertIn("Stopping Rules", self.text)
        self.assertIn("Reporting Rules", self.text)
        self.assertIn("no data-dependent early stopping", self.text.lower())

    def test_model_freeze_requirements_present(self):
        for token in ("temperature", "top_p", "max output tokens", "retry policy",
                      "repetition count", "SHA-256"):
            self.assertIn(token, self.text)
        self.assertIn("never silently swapped in", self.text)

    def test_amendment_rule_forbids_post_hoc_changes(self):
        self.assertIn("Amendment rule", self.text)
        self.assertIn("new protocol version", self.text)


class StatisticalPlanTests(unittest.TestCase):
    """Every named test must map to an appropriate data type."""

    def setUp(self):
        self.text = PREREG.read_text(encoding="utf-8")

    def test_paired_and_independent_methods_are_distinguished(self):
        mapping = {
            "McNemar exact test": "paired binary",
            "Wilcoxon signed-rank": "paired ordinal",
            "Clopper–Pearson exact CI": "single proportion",
            "Fisher exact test": "independent 2×2",
            "Ordinal transition matrix": "paired ordinal",
        }
        for test_name, data_type in mapping.items():
            self.assertIn(test_name, self.text, f"missing test {test_name}")
            row = next((ln for ln in self.text.splitlines()
                        if ln.strip().startswith(f"| {test_name}")), None)
            self.assertIsNotNone(row, f"no plan row for {test_name}")
            self.assertIn(data_type, row, f"{test_name} not mapped to {data_type}")

    def test_mcnemar_is_not_used_across_independent_groups(self):
        self.assertIn(
            "McNemar must not be used to compare dual-use items against null items",
            self.text,
        )
        self.assertIn("Fisher", self.text)

    def test_unit_of_analysis_is_the_research_item(self):
        self.assertIn("Statistical unit = research item", self.text)
        self.assertIn("never** treated as independent", self.text)

    def test_small_sample_prohibitions_present(self):
        for phrase in ("No per-cell significance testing",
                       "No bootstrap confidence intervals",
                       "No population prevalence claims"):
            self.assertIn(phrase, self.text)

    def test_wilcoxon_is_supporting_only_and_justified(self):
        flat = " ".join(self.text.split())  # documents are hard-wrapped
        self.assertIn("supporting analysis only", flat)
        self.assertIn("symmetry assumption is weak", flat)
        self.assertIn("ordinal transition matrix is the primary presentation", flat)

    def test_no_composite_score_in_pilot(self):
        self.assertIn("No composite score is computed in the", self.text)


class AnnotationProtocolTests(unittest.TestCase):
    def setUp(self):
        self.text = PROTOCOL.read_text(encoding="utf-8")

    def test_three_layers_are_separated(self):
        for token in ("Design intent", "Human reference", "Model observation"):
            self.assertIn(token, self.text)
        self.assertIn("never** used as ground truth", self.text)

    def test_blind_review_scale_and_gates_present(self):
        for label in VALID_VALENCE:
            self.assertIn(label, self.text)
        self.assertIn("must **not** see", self.text)
        self.assertIn("FAIL", self.text)

    def test_refusal_appropriateness_labels_and_semantics(self):
        for label in ("refusal_appropriate", "refusal_inappropriate", "either_defensible"):
            self.assertIn(label, self.text)
        self.assertIn("never automatically", self.text)
        self.assertIn("Documented edge cases", self.text)

    def test_two_rater_protocol_has_no_hard_kappa_threshold(self):
        self.assertIn("Cohen", self.text)
        self.assertIn("No hard κ pass/fail threshold", self.text)
        self.assertIn("descriptive statistics", self.text)

    def test_lexical_detector_is_only_a_prefilter(self):
        self.assertIn("triage pre-filter", self.text)
        self.assertIn("not the label of record", self.text)

    def test_rubric_has_tie_break_rules(self):
        self.assertIn("Tie-breaks and boundary rules", self.text)
        for boundary in ("1 versus 3", "2 versus 3", "0 versus 1"):
            self.assertIn(boundary, self.text)

    def test_training_examples_are_abstract_only(self):
        self.assertIn("no harmful operational instructions", self.text.lower())


class FreezeIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.record = load(HASHREC)

    def test_protocol_hashes_match_current_files(self):
        for rel, entry in self.record["protocol_files"].items():
            path = ROOT / rel
            self.assertTrue(path.exists(), f"protocol file missing: {rel}")
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(
                actual, entry["sha256"],
                f"{rel} changed after the freeze; re-freeze requires a new protocol_version",
            )

    def test_composite_hash_is_reproducible(self):
        files = self.record["protocol_files"]
        joined = "\n".join(f"{rel}:{files[rel]['sha256']}" for rel in sorted(files))
        expected = hashlib.sha256(joined.encode("utf-8")).hexdigest()
        self.assertEqual(expected, self.record["composite_protocol_hash"])

    def test_freeze_covers_the_documents_that_constrain_analysis(self):
        covered = set(self.record["protocol_files"])
        for required in ("docs/phase7e_preregistration.md",
                         "docs/phase7e_annotation_protocol.md",
                         "docs/PHASE_7D_EXPERIMENTAL_DESIGN.md",
                         "results/dataset_audit/phase7e_design_snapshot.json"):
            self.assertIn(required, covered)
        # The mutable review state must NOT be frozen: Phase 7E writes to it.
        self.assertNotIn("results/dataset_audit/phase7e_review.json", covered)


class ValidatorNegativeControlTests(unittest.TestCase):
    """The approval guards must actually reject violations.

    Every item in the live record is PENDING, so the invariant tests above pass
    vacuously. These tests inject synthetic violations and assert the validator
    catches each one.
    """

    def setUp(self):
        self.record = load(REVIEW)

    def _mutate(self, fn):
        record = copy.deepcopy(self.record)
        fn(record)
        return validate(record)

    def _mutate_pristine(self, fn):
        """Mutate a copy reset to the pre-decision state."""
        record = copy.deepcopy(self.record)
        for item in record["items"]:
            item.update(review_decision="PENDING", researcher_approved=False,
                        researcher_notes=None, reviewer_id=None, reviewer_role=None,
                        review_timestamp=None, revision_reason=None)
            for k in item["decision_rule_checklist"]:
                item["decision_rule_checklist"][k] = None
        refresh_counts(record)
        fn(record)
        return validate(record)

    def test_live_record_is_valid(self):
        self.assertEqual(validate(self.record), [])

    def test_rejects_approval_without_keep_decision(self):
        def bad(r):
            r["items"][0]["researcher_approved"] = True
            r["items"][0]["review_decision"] = "REJECT"
            r["counts"]["reject"] = 1
            r["counts"]["keep"] -= 1
        errors = self._mutate(bad)
        self.assertTrue(any("not KEEP" in e for e in errors), errors)
        self.assertTrue(any("must not be researcher_approved" in e for e in errors), errors)

    def test_rejects_approval_without_reviewer_identity(self):
        def bad(r):
            item = r["items"][0]
            item["review_decision"] = "KEEP"
            item["researcher_approved"] = True
            item["review_timestamp"] = "2026-08-14T10:00:00Z"
            item["reviewer_id"] = None
            item["reviewer_role"] = None
            for k in item["decision_rule_checklist"]:
                item["decision_rule_checklist"][k] = True
            r["counts"]["approved"] = 1
            r["counts"]["keep"] = 1
        errors = self._mutate(bad)
        self.assertTrue(any("without a recorded reviewer" in e for e in errors), errors)

    def test_rejects_approval_with_unmet_decision_rules(self):
        def bad(r):
            item = r["items"][0]
            item["decision_rule_checklist"]["safe_for_controlled_research"] = False
        errors = self._mutate(bad)
        self.assertTrue(any("unmet decision rules" in e for e in errors), errors)

    def test_revise_requires_a_revision_record(self):
        def bad(r):
            item = r["items"][0]
            item.update(review_decision="REVISE", researcher_approved=False,
                        researcher_notes="needs work", reviewer_role="r",
                        review_timestamp=TS)
            r["counts"]["revise"] = 1
            r["counts"]["keep"] = r["counts"]["keep"] - 1 if r["counts"]["keep"] else 0
            r["counts"]["approved"] = sum(1 for i in r["items"] if i["researcher_approved"])
        errors = self._mutate(bad)
        self.assertTrue(any("requires a revision_request" in e for e in errors), errors)

    def test_decided_item_without_reviewer_is_rejected(self):
        def bad(r):
            item = r["items"][0]
            item.update(review_decision="REJECT", researcher_approved=False,
                        rejection_reason="too artificial", researcher_notes="too artificial",
                        reviewer_id=None, reviewer_role=None, review_timestamp=None)
            r["counts"]["pending"] = 49
            r["counts"]["reject"] = 1
        errors = self._mutate_pristine(bad)
        self.assertTrue(any("without a reviewer" in e for e in errors), errors)

    def test_reject_without_a_reason_is_rejected(self):
        def bad(r):
            item = r["items"][0]
            item.update(review_decision="REJECT", researcher_approved=False,
                        reviewer_id="R1", review_timestamp=TS, researcher_notes="n")
            item.pop("rejection_reason", None)
            r["counts"]["reject"] = 1
            r["counts"]["keep"] -= 1
            r["counts"]["approved"] = sum(1 for i in r["items"] if i["researcher_approved"])
        errors = self._mutate(bad)
        self.assertTrue(any("requires a recorded rejection reason" in e for e in errors), errors)

    def test_pending_item_with_review_residue_is_rejected(self):
        errors = self._mutate_pristine(
            lambda r: r["items"][0].__setitem__("reviewer_id", "R1"))
        self.assertTrue(any("PENDING item has reviewer_id set" in e for e in errors), errors)

    def test_revision_must_carry_reason_and_timestamp(self):
        def bad(r):
            item = r["items"][0]
            item.update(review_decision="REVISE", researcher_approved=False,
                        researcher_notes="needs work")
            item["revision_request"] = {"revision_status": "pending_revision"}
            r["counts"]["revise"] = 1
            r["counts"]["keep"] -= 1
            r["counts"]["approved"] = sum(1 for i in r["items"] if i["researcher_approved"])
            item["versions"].append({
                "version": 2, "source_phase": "7E", "created_at": None,
                "design": item["versions"][0]["design"], "superseded": False,
                "revision_reason": None, "revision_timestamp": None,
            })
            item["current_version"] = 2
        errors = self._mutate(bad)
        self.assertTrue(any("lacks a revision_reason" in e for e in errors), errors)
        self.assertTrue(any("lacks a revision_timestamp" in e for e in errors), errors)

    def test_version_one_cannot_be_overwritten(self):
        def bad(r):
            r["items"][0]["versions"][0]["version"] = 2
        errors = self._mutate(bad)
        self.assertTrue(any("version 1 must be the immutable" in e for e in errors), errors)

    def test_rejects_leaked_final_prompt_text(self):
        def bad(r):
            r["items"][0]["versions"][0]["design"]["canonical_final_prompt"] = "some prompt"
        errors = self._mutate(bad)
        self.assertTrue(any("forbidden field" in e for e in errors), errors)

    def test_rejects_leaked_model_output(self):
        def bad(r):
            r["items"][0]["model_disposition"] = 4
        errors = self._mutate(bad)
        self.assertTrue(any("model_disposition" in e for e in errors), errors)

    def test_rejects_premature_blind_review_result(self):
        def bad(r):
            r["items"][0]["blind_isolated_prompt_review"]["status"] = "COMPLETE"
            r["items"][0]["blind_isolated_prompt_review"]["gate_result"] = "PASS"
        errors = self._mutate(bad)
        self.assertTrue(any("cannot start before prompts exist" in e for e in errors), errors)
        self.assertTrue(any("gate_result set before" in e for e in errors), errors)

    def test_rejects_premature_refusal_reference(self):
        def bad(r):
            r["items"][0]["refusal_appropriateness_reference"]["status"] = "COMPLETE"
        errors = self._mutate(bad)
        self.assertTrue(any("cannot be set in Phase 7E" in e for e in errors), errors)

    def test_rejects_valence_that_leaks_the_label(self):
        def bad(r):
            for item in r["items"]:
                if item["versions"][0]["design"]["category"] == "dual_use_nonnull":
                    item["versions"][0]["design"]["isolated_prompt_target_valence"] = "clearly_benign"
                    break
        errors = self._mutate(bad)
        self.assertTrue(any("requires target valence ambiguous_dual_use" in e for e in errors), errors)

    def test_rejects_enabled_phase_gates(self):
        for flag in ("stimulus_generation_permitted", "model_evaluation_permitted",
                     "final_prompts_exist", "auto_approval_performed"):
            errors = self._mutate(lambda r, key=flag: r.__setitem__(key, True))
            self.assertTrue(
                any(flag in err for err in errors),
                f"{flag} not caught: {errors}",
            )

    def test_rejects_count_drift(self):
        errors = self._mutate(lambda r: r["counts"].__setitem__("approved", 7))
        self.assertTrue(any("counts.approved" in e for e in errors), errors)

    def test_rejects_wrong_category_distribution(self):
        def bad(r):
            r["items"][0]["versions"][0]["design"]["category"] = "null_benign"
        errors = self._mutate(bad)
        self.assertTrue(any("category distribution" in e for e in errors), errors)


class ReviewDocumentTests(unittest.TestCase):
    def test_review_document_shows_all_items_as_pending(self):
        text = REVIEW_DOC.read_text(encoding="utf-8")
        self.assertIn("ALL 50 ITEMS ARE `PENDING`", text)
        # count only item rows: a table row whose final cell is the decision
        item_rows = [ln for ln in text.splitlines()
                     if ln.startswith("| RI-") and "| `PENDING` |" in ln]
        self.assertEqual(len(item_rows), 50)
        review_ids = {i["research_item_id"] for i in load(REVIEW)["items"]}
        self.assertEqual({ln.split("|")[1].strip() for ln in item_rows}, review_ids)
        self.assertIn("<not supplied>", text)

    def test_review_document_lists_all_eight_decision_rules(self):
        text = REVIEW_DOC.read_text(encoding="utf-8")
        for rule in load(REVIEW)["decision_rules"]:
            self.assertIn(rule, text)

    def test_design_table_contains_no_prompt_text_column(self):
        text = DESIGN_TABLE.read_text(encoding="utf-8")
        self.assertIn("canonical_final_prompt_intent", text)
        self.assertNotIn("canonical_final_prompt |", text)
        self.assertIn("No final-prompt text", text)


if __name__ == "__main__":
    unittest.main()


# ---------------------------------------------------------------------------
# Phase 7E EXECUTION — recording researcher decisions
# ---------------------------------------------------------------------------

from validate_phase7e_review import validate_history  # noqa: E402
from apply_phase7e_decisions import (  # noqa: E402
    DecisionError, apply_decisions, parse_decisions, refresh_counts,
)

HISTORY = ROOT / "results" / "dataset_audit" / "phase7e_review_history.jsonl"
SNAPSHOT = ROOT / "results" / "dataset_audit" / "phase7e_design_snapshot.json"
TS = "2026-08-14T12:00:00Z"


class DecisionsRecordedTests(unittest.TestCase):
    """The researcher supplied KEEP for all 50 items; the record must reflect that."""

    def setUp(self):
        self.record = load(REVIEW)

    def test_review_is_complete_with_fifty_keeps(self):
        c = self.record["counts"]
        self.assertEqual(c["keep"], 50)
        self.assertEqual(c["approved"], 50)
        self.assertEqual(c["pending"], 0)
        self.assertEqual(c["revise"], 0)
        self.assertEqual(c["reject"], 0)
        self.assertEqual(c["revision_records"], 0)
        self.assertEqual(self.record["status"], "REVIEW_COMPLETE")
        self.assertTrue(self.record["review_complete"])

    def test_every_approval_carries_a_reviewer_and_timestamp(self):
        for item in self.record["items"]:
            self.assertTrue(item["researcher_approved"])
            self.assertTrue(item["reviewer_role"])
            self.assertTrue(item["review_timestamp"])

    def test_decision_rules_are_asserted_only_on_kept_items(self):
        for item in self.record["items"]:
            if item["review_decision"] == "KEEP":
                self.assertTrue(all(item["decision_rule_checklist"].values()))
            else:
                for value in item["decision_rule_checklist"].values():
                    self.assertIsNone(value)


class DecisionParsingTests(unittest.TestCase):
    def test_parses_the_documented_format(self):
        parsed = parse_decisions(
            "RI-DU-001: KEEP\n"
            "RI-DU-002: REVISE — final prompt may still be too explicit\n"
            "RI-DU-004: REJECT — scenario is too artificial\n"
        )
        self.assertEqual([p["decision"] for p in parsed], ["KEEP", "REVISE", "REJECT"])
        self.assertIsNone(parsed[0]["note"])
        self.assertEqual(parsed[1]["note"], "final prompt may still be too explicit")

    def test_notes_are_preserved_verbatim(self):
        note = "  too  artificial; ALSO see  Smith et al. (2024) -- maybe?  "
        parsed = parse_decisions(f"RI-DU-001: REJECT — {note}")
        self.assertEqual(parsed[0]["note"], note.strip())

    def test_rejects_unknown_decision_value(self):
        with self.assertRaises(DecisionError):
            parse_decisions("RI-DU-001: MAYBE")

    def test_rejects_unparseable_line(self):
        with self.assertRaises(DecisionError):
            parse_decisions("this item looks fine to me")

    def test_revise_and_reject_require_a_reason(self):
        for decision in ("REVISE", "REJECT"):
            with self.assertRaises(DecisionError, msg=decision):
                parse_decisions(f"RI-DU-001: {decision}")

    def test_rejects_duplicate_decisions(self):
        with self.assertRaises(DecisionError):
            parse_decisions("RI-DU-001: KEEP\nRI-DU-001: KEEP")

    def test_empty_input_is_refused(self):
        with self.assertRaises(DecisionError):
            parse_decisions("# only a comment\n\n")


class DecisionApplicationTests(unittest.TestCase):
    """Applying decisions must produce a record that still passes validation."""

    def setUp(self):
        self.record = load(REVIEW)

    def _pristine(self):
        """A copy of the record reset to the pre-decision (all PENDING) state."""
        record = copy.deepcopy(self.record)
        for item in record["items"]:
            item.update(review_decision="PENDING", researcher_approved=False,
                        researcher_notes=None, reviewer_id=None, reviewer_role=None,
                        review_timestamp=None, revision_reason=None)
            for k in item["decision_rule_checklist"]:
                item["decision_rule_checklist"][k] = None
            for key in ("revision_request", "revision_status", "revision_required",
                        "rejection_reason", "rejected_at"):
                item.pop(key, None)
        record["reviewer_registry"] = []
        refresh_counts(record)
        return record

    def _apply(self, text, reviewer_id="researcher-1", reviewer_role="principal investigator"):
        record = self._pristine()
        events = apply_decisions(record, parse_decisions(text), reviewer_id, reviewer_role, TS)
        return record, events

    def test_keep_approves_and_stays_valid(self):
        record, events = self._apply("RI-DU-001: KEEP")
        item = record["items"][0]
        self.assertEqual(item["review_decision"], "KEEP")
        self.assertTrue(item["researcher_approved"])
        self.assertEqual(item["reviewer_id"], "researcher-1")
        self.assertEqual(item["review_timestamp"], TS)
        self.assertTrue(all(item["decision_rule_checklist"].values()))
        self.assertEqual(record["counts"]["keep"], 1)
        self.assertEqual(record["counts"]["approved"], 1)
        self.assertEqual(record["counts"]["pending"], 49)
        self.assertEqual(validate(record), [])
        self.assertEqual(events[0]["previous_decision"], "PENDING")
        self.assertEqual(events[0]["new_decision"], "KEEP")

    def test_revise_is_not_approved_and_creates_a_revision_record(self):
        record, _ = self._apply("RI-DU-002: REVISE — still too explicit")
        item = next(i for i in record["items"] if i["research_item_id"] == "RI-DU-002")
        self.assertEqual(item["review_decision"], "REVISE")
        self.assertFalse(item["researcher_approved"])
        self.assertEqual(item["revision_request"]["revision_status"], "pending_revision")
        self.assertEqual(item["revision_request"]["original_version"], 1)
        self.assertEqual(item["researcher_notes"], "still too explicit")
        # version 1 preserved, and no version 2 authored without an explicit request
        self.assertEqual(len(item["versions"]), 1)
        self.assertEqual(item["versions"][0]["version"], 1)
        self.assertEqual(record["counts"]["revision_records"], 1)
        self.assertEqual(validate(record), [])

    def test_reject_preserves_the_record_and_reason(self):
        record, _ = self._apply("RI-DU-004: REJECT — scenario is too artificial")
        item = next(i for i in record["items"] if i["research_item_id"] == "RI-DU-004")
        self.assertEqual(item["review_decision"], "REJECT")
        self.assertFalse(item["researcher_approved"])
        self.assertEqual(item["rejection_reason"], "scenario is too artificial")
        self.assertEqual(item["rejected_at"], TS)
        self.assertIn("design", item["versions"][0])  # not deleted
        self.assertEqual(len(record["items"]), 50)     # nothing removed
        self.assertEqual(validate(record), [])

    def test_unmentioned_items_stay_pending(self):
        record, _ = self._apply("RI-DU-001: KEEP")
        others = [i for i in record["items"] if i["research_item_id"] != "RI-DU-001"]
        self.assertEqual(len(others), 49)
        for item in others:
            self.assertEqual(item["review_decision"], "PENDING")
            self.assertFalse(item["researcher_approved"])
            self.assertIsNone(item["reviewer_id"])

    def test_reviewer_identity_is_required(self):
        with self.assertRaises(DecisionError):
            apply_decisions(self._pristine(), parse_decisions("RI-DU-001: KEEP"),
                            None, None, TS)

    def test_live_record_refuses_redecision(self):
        """The real record is already decided; re-deciding must raise, not overwrite."""
        with self.assertRaises(DecisionError) as ctx:
            apply_decisions(copy.deepcopy(self.record),
                            parse_decisions("RI-DU-001: REJECT — changed my mind"),
                            "researcher-1", None, "2026-08-20T09:00:00Z")
        self.assertIn("already decided", str(ctx.exception))

    def test_redeciding_an_item_is_a_conflict_not_an_overwrite(self):
        record, _ = self._apply("RI-DU-001: KEEP")
        with self.assertRaises(DecisionError) as ctx:
            apply_decisions(record, parse_decisions("RI-DU-001: REJECT — changed my mind"),
                            "researcher-1", None, "2026-08-15T09:00:00Z")
        self.assertIn("already decided", str(ctx.exception))

    def test_unknown_item_id_is_refused(self):
        with self.assertRaises(DecisionError):
            self._apply("RI-ZZ-999: KEEP")

    def test_status_transitions_only_when_all_items_decided(self):
        record, _ = self._apply("RI-DU-001: KEEP")
        self.assertEqual(record["status"], "REVIEW_IN_PROGRESS")
        self.assertFalse(record["review_complete"])
        full = "\n".join(f"{i['research_item_id']}: KEEP" for i in self._pristine()["items"])
        record2, _ = self._apply(full)
        self.assertEqual(record2["status"], "REVIEW_COMPLETE")
        self.assertTrue(record2["review_complete"])
        self.assertEqual(record2["counts"]["approved"], 50)
        self.assertEqual(validate(record2), [])


class ReviewHistoryTests(unittest.TestCase):
    def test_history_exists_and_is_initialised(self):
        self.assertTrue(HISTORY.exists())
        lines = [l for l in HISTORY.read_text(encoding="utf-8").splitlines() if l.strip()]
        self.assertGreaterEqual(len(lines), 1)
        first = json.loads(lines[0])
        self.assertEqual(first["event"], "review_log_initialised")
        self.assertEqual(first["initial_decision_for_all_items"], "PENDING")
        self.assertIsNone(first["reviewer_id"])

    def test_history_validates_against_the_live_record(self):
        lines = HISTORY.read_text(encoding="utf-8").splitlines()
        self.assertEqual(validate_history(lines, load(REVIEW)), [])

    def test_history_must_explain_every_decided_item(self):
        record = load(REVIEW)
        record["items"].append({"research_item_id": "RI-XX-999",
                                "review_decision": "KEEP"})
        lines = HISTORY.read_text(encoding="utf-8").splitlines()
        errors = validate_history(lines, record)
        self.assertTrue(any("no history event records it" in e for e in errors), errors)

    def test_history_records_all_fifty_decisions(self):
        events = [json.loads(l) for l in HISTORY.read_text(encoding="utf-8").splitlines()
                  if l.strip()]
        decisions = [e for e in events if e.get("event") == "review_decision"]
        self.assertEqual(len(decisions), 50)
        self.assertTrue(all(e["new_decision"] == "KEEP" for e in decisions))
        self.assertTrue(all(e["previous_decision"] == "PENDING" for e in decisions))

    def test_history_rejects_a_decision_event_without_a_reviewer(self):
        record = load(REVIEW)
        record["items"][0]["review_decision"] = "KEEP"
        event = {"event": "review_decision", "research_item_id": "RI-DU-001",
                 "previous_decision": "PENDING", "new_decision": "KEEP",
                 "timestamp": TS, "version": 1, "reviewer_id": None, "reviewer_role": None}
        lines = HISTORY.read_text(encoding="utf-8").splitlines() + [json.dumps(event)]
        errors = validate_history(lines, record)
        self.assertTrue(any("lacks a reviewer" in e for e in errors), errors)

    def test_history_append_is_non_destructive(self):
        """Appending must preserve every earlier line byte-for-byte."""
        import tempfile
        from apply_phase7e_decisions import append_history
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "h.jsonl"
            path.write_text(json.dumps({"event": "review_log_initialised"}) + "\n",
                            encoding="utf-8")
            original = path.read_text(encoding="utf-8")
            append_history(path, [{"event": "review_decision", "research_item_id": "RI-DU-001"}])
            after = path.read_text(encoding="utf-8")
            self.assertTrue(after.startswith(original))
            self.assertEqual(len(after.splitlines()), 2)


class DesignSnapshotTests(unittest.TestCase):
    def test_snapshot_holds_all_fifty_version_one_designs(self):
        snap = load(SNAPSHOT)
        self.assertEqual(snap["item_count"], 50)
        self.assertEqual(len(snap["items"]), 50)
        for entry in snap["items"]:
            self.assertEqual(entry["version"], 1)
            self.assertEqual(entry["source_phase"], "7D")

    def test_snapshot_is_decision_free(self):
        blob = json.dumps(load(SNAPSHOT))
        for field in ("review_decision", "researcher_approved", "reviewer_id",
                      "researcher_notes", "model_disposition"):
            self.assertNotIn(f'"{field}"', blob)

    def test_snapshot_matches_the_live_version_one_designs(self):
        snap = {e["design"]["research_item_id"]: e["design"] for e in load(SNAPSHOT)["items"]}
        live = {i["research_item_id"]: i["versions"][0]["design"] for i in load(REVIEW)["items"]}
        self.assertEqual(snap, live)

    def test_pre_execution_backup_exists(self):
        backup = ROOT / "results" / "dataset_audit" / "snapshots" / \
            "phase7e_review.v1.pre_execution.json"
        self.assertTrue(backup.exists())
        self.assertEqual(len(load(backup)["items"]), 50)


class ProtocolAmendmentTests(unittest.TestCase):
    """Amendment-chain invariants.

    REPLACEMENT NOTE (remediation F-01/F-02, researcher decisions R1): the original
    version of this class pinned record.protocol_version == "1.0.1" and asserted the
    v1.0.1 amendment fields on record["amendment"]. The researcher-authorized
    pre-evaluation clarification legitimately advanced the manifest to 1.0.2 and made
    it the latest amendment, so version-pinned constants were replaced with chain
    invariants; every historical value asserted before is still asserted here —
    against its own entry in the recorded chain (prior_amendments[0]) rather than
    against whatever happens to be latest.
    """

    def setUp(self):
        self.record = load(HASHREC)
        self.chain = list(self.record.get("prior_amendments", [])) + [
            self.record["amendment"]
        ]

    def test_chain_versions_are_ordered_and_complete(self):
        self.assertEqual(
            [a["from_version"] for a in self.chain], ["1.0.0", "1.0.1"])
        self.assertEqual([a["to_version"] for a in self.chain], ["1.0.1", "1.0.2"])
        self.assertEqual(self.record["protocol_version"], "1.0.2")
        self.assertEqual(len(self.record["prior_amendments"]), 1)
        self.assertIs(self.chain[-1], self.record["amendment"])

    def test_v1_0_1_manifest_scope_correction_is_preserved_verbatim(self):
        """Historical values from the original ProtocolAmendmentTests, unchanged."""
        amd = self.chain[0]
        self.assertEqual(amd["type"], "manifest_scope_correction")
        self.assertTrue(amd["made_before_any_model_evaluation"])
        self.assertFalse(amd["rules_changed"])
        self.assertEqual(amd["prior_composite_protocol_hash"],
                         "125bdf36dad11bb7242743dc58a97a7bb868ac8a39308156ba3b942962f25a29")

    def test_v1_0_2_clarification_is_pre_evaluation_and_rule_free(self):
        amd = self.chain[-1]
        self.assertEqual(amd["type"], "pre_evaluation_clarification")
        self.assertTrue(amd["made_before_any_model_evaluation"])
        self.assertFalse(amd["rules_changed"])
        self.assertEqual(amd["prior_composite_protocol_hash"],
                         "d945d4419e817e496521afa7ab8bdb2e7005bbe6245ce590418d66184f646819")
        self.assertIn("F-01", amd["clarifies_findings"])
        self.assertIn("F-02", amd["clarifies_findings"])

    def test_protocol_documents_are_byte_identical_to_v1_0_0(self):
        """The actual pre-registration content must not have drifted at all."""
        baseline = {
            "docs/phase7e_preregistration.md":
                "7d46e0fba94a88beaa27a4c41efa209e3c89619b3f3dd5e96877997aa99bf87c",
            "docs/phase7e_annotation_protocol.md":
                "41c628b801a08d85e52d3f6fe79eb711e9e949b76ad29cdc425356fb742fefa4",
            "docs/PHASE_7D_EXPERIMENTAL_DESIGN.md":
                "e120652648bbec68cca3bed95ce924f0ce27f2f1cc2661334edea62f4fd23688",
            "docs/PHASE_7D_DESIGN_TABLE.md":
                "8bced7f9e42d0d2919192498f2e8e380aeeae820ed02f7cc0e9b7717e7bad366",
        }
        for rel, want in baseline.items():
            actual = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
            self.assertEqual(actual, want, f"protocol document {rel} was modified")
        self.assertTrue(self.record["protocol_documents_byte_identical_to_v1_0_0"])
        self.assertEqual(self.record["protocol_document_drift"], {})

    def test_clarification_document_is_a_frozen_member_with_required_content(self):
        rel = "docs/phase7e_pre_evaluation_clarification.md"
        self.assertIn(rel, self.record["protocol_files"])
        entry = self.record["protocol_files"][rel]
        actual = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        self.assertEqual(actual, entry["sha256"])
        text = (ROOT / rel).read_text(encoding="utf-8")
        # Binding interpretation constraints from Decision R1 must be visibly present.
        for marker in (
            "whole conversational-context sensitivity",
            "MUST NOT be presented as identifying a pure causal effect",
            "assistant_turn_shared",
            "assistant_turn_differing",
            "MUST NOT be described as a randomized causal control",
            "control the assistant-stance channel",
        ):
            self.assertIn(marker, text)

    def test_review_state_is_explicitly_mutable_not_frozen(self):
        mutable = self.record["mutable_files"]
        self.assertIn("results/dataset_audit/phase7e_review.json", mutable)
        self.assertIn("results/dataset_audit/phase7e_review_history.jsonl", mutable)
        for entry in mutable.values():
            self.assertFalse(entry["frozen"])
        self.assertNotIn("results/dataset_audit/phase7e_review.json",
                         self.record["protocol_files"])

    def test_design_snapshot_is_frozen_in_place_of_the_review_file(self):
        self.assertIn("results/dataset_audit/phase7e_design_snapshot.json",
                      self.record["protocol_files"])


class Phase7EPostAuditRegressions(unittest.TestCase):
    def test_fresh_bootstrap_then_reinit_history_validates(self):
        """Fresh bootstrap writes history; later reinit appends reinit event; validate_history gives []."""
        import tempfile
        import build_phase7e_review
        from validate_phase7e_review import validate_history

        with tempfile.TemporaryDirectory() as tmp_dir:
            out_dir = Path(tmp_dir) / "out"
            backup_dir = Path(tmp_dir) / "backup"

            # 1. Fresh bootstrap
            ret = build_phase7e_review.main(["--out-dir", str(out_dir)])
            self.assertEqual(ret, 0)

            history_file = out_dir / "results" / "dataset_audit" / "phase7e_review_history.jsonl"
            self.assertTrue(history_file.exists(), "fresh bootstrap did not write history file")

            review_file = out_dir / "results" / "dataset_audit" / "phase7e_review.json"
            record = json.loads(review_file.read_text(encoding="utf-8"))
            lines = history_file.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            init_event = json.loads(lines[0])
            self.assertEqual(init_event["event"], "review_log_initialised")
            self.assertEqual(init_event["timestamp"], build_phase7e_review.FROZEN_AT)
            self.assertEqual(validate_history(lines, record), [])

            # 2. Pre-existence check: if only history exists, refuse with code 2
            out_dir2 = Path(tmp_dir) / "out2"
            hist2 = out_dir2 / "results" / "dataset_audit" / "phase7e_review_history.jsonl"
            hist2.parent.mkdir(parents=True)
            hist2.write_text(lines[0] + "\n", encoding="utf-8")
            ret_refuse = build_phase7e_review.main(["--out-dir", str(out_dir2)])
            self.assertEqual(ret_refuse, 2)

            # 3. Reinit
            ret_reinit = build_phase7e_review.main(
                ["--out-dir", str(out_dir), "--reinit", "--backup-dir", str(backup_dir)]
            )
            self.assertEqual(ret_reinit, 0)
            lines_reinit = history_file.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines_reinit), 2)
            self.assertEqual(json.loads(lines_reinit[0])["event"], "review_log_initialised")
            self.assertEqual(json.loads(lines_reinit[1])["event"], "review_reinitialised")
            record_reinit = json.loads(review_file.read_text(encoding="utf-8"))
            self.assertEqual(validate_history(lines_reinit, record_reinit), [])

    def test_validate_history_rejects_unknown_research_item_id_and_missing_reinit_fields(self):
        """B7: validate_history rejects unknown research_item_id and reinit missing backup fields."""
        from validate_phase7e_review import validate_history

        record = {
            "items": [
                {"research_item_id": "RI-DU-001", "review_decision": "PENDING"}
            ]
        }
        init_line = json.dumps({"event": "review_log_initialised"})

        # Unknown ID
        bad_decision = json.dumps({
            "event": "review_decision",
            "research_item_id": "RI-UNKNOWN-999",
            "previous_decision": "PENDING",
            "new_decision": "KEEP",
            "timestamp": "2026-08-14T12:00:00Z",
            "version": 1,
            "reviewer_id": "r1",
        })
        errors = validate_history([init_line, bad_decision], record)
        self.assertTrue(any("unknown research_item_id" in e for e in errors), errors)

        # Reinit missing backup_dir or manifest_sha256
        reinit_no_backup = json.dumps({
            "event": "review_reinitialised",
            "manifest_sha256": "abcdef",
        })
        reinit_no_sha = json.dumps({
            "event": "review_reinitialised",
            "backup_dir": "/path/to/backup",
        })
        errors_b = validate_history([init_line, reinit_no_backup], record)
        self.assertTrue(any("lacks backup_dir" in e for e in errors_b), errors_b)

        errors_s = validate_history([init_line, reinit_no_sha], record)
        self.assertTrue(any("lacks manifest_sha256" in e for e in errors_s), errors_s)
