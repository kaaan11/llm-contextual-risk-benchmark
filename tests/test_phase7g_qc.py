"""Phase 7G — blind review integrity, QC gating and no-fabrication tests."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from apply_phase7g_annotations import (  # noqa: E402
    QCError, evaluate_gate, record_blind, record_context, record_decision,
    refresh_blind_stats,
)
from validate_phase7g_review import validate, validate_blind  # noqa: E402

AUDIT = ROOT / "results" / "dataset_audit"
BLIND = AUDIT / "phase7g_blind_review.json"
KEY = AUDIT / "phase7g_blind_key.json"
QC = AUDIT / "phase7g_human_qc.json"
HISTORY = AUDIT / "phase7g_review_history.jsonl"
SUMMARY = AUDIT / "phase7g_quality_summary.json"
DOC = ROOT / "docs" / "phase7g_human_qc.md"
SNAPSHOT = AUDIT / "snapshots" / "phase7f_stimulus.v1.pre_qc.json"
STIMULI = ROOT / "dataset" / "pilot" / "multiturn" / "stimulus_dataset_v1.json"

TS = "2026-08-14T18:00:00Z"


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


class FilesExistTests(unittest.TestCase):
    def test_all_phase7g_outputs_exist(self):
        for p in (BLIND, KEY, QC, HISTORY, SUMMARY, DOC, SNAPSHOT):
            self.assertTrue(p.exists(), f"missing Phase 7G output: {p}")


class BlindPacketTests(unittest.TestCase):
    def setUp(self):
        self.blind = load(BLIND)
        self.key = load(KEY)

    def test_fifty_items_with_unique_opaque_ids(self):
        items = self.blind["items"]
        self.assertEqual(len(items), 50)
        ids = [i["blind_id"] for i in items]
        self.assertEqual(len(set(ids)), 50)
        for bid in ids:
            self.assertRegex(bid, r"^BLIND-\d{3}$")

    def test_packet_exposes_only_prompt_and_annotation_fields(self):
        core = {"blind_id", "batch", "canonical_final_prompt", "rater_a", "rater_b",
                "adjudicated_valence", "adjudication_rationale",
                "annotation_status", "gate_result", "gate_flag"}
        optional = {"presentation_sessions", "requires_fresh_presentation_session",
                    "accepted_in_session"}
        for item in self.blind["items"]:
            self.assertTrue(core.issubset(item), item["blind_id"])
            self.assertEqual(set(item) - core - optional, set(), item["blind_id"])

    def test_packet_does_not_leak_category_or_design(self):
        scrubbed = dict(self.blind)
        scrubbed.pop("blinding")
        blob = json.dumps(scrubbed)
        for term in ("RI-DU", "RI-AM", "RI-NB", "RI-NH", "research_item_id",
                     "dual_use_nonnull", "persistent_ambiguity", "null_benign",
                     "null_highrisk", "expected_context_effect",
                     "isolated_prompt_target_valence", "context_mechanism",
                     "d_control_rationale"):
            self.assertNotIn(term, blob, f"blind packet leaks {term!r}")

    def test_packet_contains_no_context_turns(self):
        stim = {r["research_item_id"]: r for r in load(STIMULI)["records"]}
        blob = json.dumps(self.blind)
        for rec in stim.values():
            for name, cond in rec["conditions"].items():
                if name == "final_prompt_only":
                    continue
                for turn in cond["turns"][:-1]:
                    self.assertNotIn(turn["content"]["text"], blob,
                                     "B/C/D context leaked into the blind packet")

    def test_prompts_match_the_stimulus_dataset_exactly(self):
        stim = {r["research_item_id"]: r["canonical_final_prompt"]
                for r in load(STIMULI)["records"]}
        keymap = {m["blind_id"]: m["research_item_id"] for m in self.key["mapping"]}
        for item in self.blind["items"]:
            rid = keymap[item["blind_id"]]
            self.assertEqual(item["canonical_final_prompt"], stim[rid])

    def test_order_is_not_grouped_by_category(self):
        keymap = {m["blind_id"]: m["category"] for m in self.key["mapping"]}
        seq = [keymap[i["blind_id"]] for i in self.blind["items"]]
        runs = sum(1 for a, b in zip(seq, seq[1:]) if a != b)
        self.assertGreater(runs, 10, "blind order appears grouped by category")

    def test_key_file_is_sealed_and_complete(self):
        self.assertFalse(self.key["opened"])
        self.assertIn("SEALED KEY", self.key["warning"])
        self.assertEqual(len(self.key["mapping"]), 50)
        rids = {m["research_item_id"] for m in self.key["mapping"]}
        self.assertEqual(len(rids), 50)

    def test_batches_are_ten_items_each(self):
        self.assertEqual(self.blind["batches"], {str(b): 10 for b in range(1, 6)})

    def test_scale_is_categorical_only(self):
        self.assertEqual(self.blind["valence_scale"],
                         ["clearly_benign", "probably_benign", "ambiguous_dual_use",
                          "probably_concerning", "clearly_concerning"])
        self.assertIn("Do not derive a numeric risk score", self.blind["scale_note"])


class AnnotationScopeTests(unittest.TestCase):
    """Only explicitly supplied annotations exist; everything else stays PENDING."""

    def setUp(self):
        self.blind = load(BLIND)
        self.qc = load(QC)

    def test_only_explicitly_annotated_items_carry_a_valence(self):
        # F-03/F-20 remediation: expected count is DERIVED from the append-only
        # history log instead of hard-coding current progress.
        events = [json.loads(l) for l in HISTORY.read_text().splitlines() if l.strip()]
        expected = len({(e["blind_id"], e["rater"])
                        for e in events if e.get("event") == "blind_annotation"})
        annotated = [i for i in self.blind["items"]
                     if i["annotation_status"] != "PENDING"]
        self.assertEqual(len(annotated), expected,
                         "annotation state diverged from the append-only history")
        for item in self.blind["items"]:
            if item["annotation_status"] == "PENDING":
                for rater in ("rater_a", "rater_b"):
                    self.assertIsNone(item[rater]["isolated_prompt_valence_observed"])
                    self.assertIsNone(item[rater]["annotated_at"])
                self.assertIsNone(item["adjudicated_valence"])
                self.assertIsNone(item["gate_result"])

    def test_single_rater_does_not_produce_adjudication_or_gate(self):
        for item in self.blind["items"]:
            if item["annotation_status"] == "PARTIAL_ONE_RATER":
                self.assertIsNone(item["adjudicated_valence"])
                self.assertIsNone(item["gate_result"])
                self.assertIsNone(item["gate_flag"])

    def test_no_reviewer_id_was_invented(self):
        for item in self.blind["items"]:
            for rater in ("rater_a", "rater_b"):
                self.assertIsNone(item[rater]["reviewer_id"])

    def test_no_agreement_statistics_fabricated(self):
        proto = self.blind["two_rater_protocol"]
        self.assertEqual(proto["inter_rater_status"], "not_available")
        self.assertLess(proto["raters_supplied"], 2)
        self.assertIsNone(proto["percent_agreement"])
        self.assertIsNone(proto["cohens_kappa"])

    def test_all_items_pending_and_phase_incomplete(self):
        c = self.qc["counts"]
        self.assertEqual(c["pending"], 50)
        for key in ("keep", "revise", "reject", "researcher_qc_true"):
            self.assertEqual(c[key], 0)
        self.assertFalse(self.qc["phase_complete"])
        self.assertEqual(self.qc["status"], "AWAITING_HUMAN_QC")
        self.assertFalse(self.qc["auto_approval_performed"])

    def test_no_reviewer_identity_invented(self):
        for item in self.qc["items"]:
            self.assertIsNone(item["reviewer_id"])
            self.assertIsNone(item["reviewer_role"])
            self.assertIsNone(item["review_timestamp"])

    def test_review_sections_not_started(self):
        for item in self.qc["items"]:
            for section in ("context_review", "safety_review",
                            "naturalness_review", "length_control_review"):
                self.assertEqual(item[section]["status"], "NOT_STARTED")
            self.assertIsNone(item["safety_review"]["safety_status"])
            self.assertIsNone(item["naturalness_review"]["naturalness"])
            self.assertIsNone(item["suitable_for_model_evaluation"])
            self.assertEqual(item["quality_flags"], [])

    def test_context_was_not_revealed(self):
        self.assertFalse(self.qc["blind_gate"]["context_revealed"])

    def test_summary_matches_live_records(self):
        """REPLACED by F-03 remediation: previously pinned annotations_submitted==0,
        which codified a stale roll-up. The invariant now is derivation equality."""
        s = load(SUMMARY)
        blind = load(BLIND)
        annotated = sum(1 for i in blind["items"]
                        if i["annotation_status"] != "PENDING")
        dist = {}
        for i in blind["items"]:
            for rater in ("rater_a", "rater_b"):
                v = i[rater]["isolated_prompt_valence_observed"]
                if v:
                    dist[v] = dist.get(v, 0) + 1
        self.assertFalse(s["phase_complete"])
        self.assertEqual(s["isolated_prompt_review"]["annotations_submitted"], annotated)
        for v, n in dist.items():
            self.assertEqual(s["isolated_prompt_review"]["valence_distribution"][v], n)
        self.assertEqual(s["inter_rater"]["raters_supplied"],
                         blind["two_rater_protocol"]["raters_supplied"])


class StructuralReverificationTests(unittest.TestCase):
    def setUp(self):
        self.qc = load(QC)

    def test_all_items_pass_independent_recheck(self):
        summary = self.qc["structural_verification_summary"]
        self.assertTrue(summary["all_pass"])
        self.assertEqual(summary["failures"], [])
        self.assertIn("NOT human approval", summary["note"])

    def test_per_item_equality_and_hashes_recorded(self):
        for item in self.qc["items"]:
            sv = item["structural_verification"]
            self.assertTrue(sv["passes"], item["research_item_id"])
            self.assertTrue(sv["recorded_hash_matches_prompt"])
            self.assertTrue(all(sv["final_prompt_equality_by_condition"].values()))
            self.assertTrue(all(sv["hash_match_by_condition"].values()))

    def test_recheck_is_independent_of_phase7f_claims(self):
        """Recompute from the stimulus file rather than trusting recorded flags."""
        for rec in load(STIMULI)["records"]:
            prompt = rec["canonical_final_prompt"]
            digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
            self.assertEqual(digest, rec["canonical_final_prompt_sha256"])
            for cond in rec["conditions"].values():
                self.assertEqual(cond["final_user_turn_text"], prompt)


class GateLogicTests(unittest.TestCase):
    def test_dual_use_gate_outcomes(self):
        self.assertEqual(evaluate_gate("dual_use_nonnull", "ambiguous_dual_use"),
                         ("PASS", None))
        self.assertEqual(evaluate_gate("dual_use_nonnull", "clearly_benign"),
                         ("FAIL", "ISOLATED_VALENCE_GATE_FAIL"))
        self.assertEqual(evaluate_gate("dual_use_nonnull", "clearly_concerning"),
                         ("FAIL", "ISOLATED_VALENCE_GATE_FAIL"))
        self.assertEqual(evaluate_gate("dual_use_nonnull", "probably_benign"),
                         ("REVIEW", "ISOLATED_VALENCE_GATE_REVIEW"))
        self.assertEqual(evaluate_gate("dual_use_nonnull", "probably_concerning"),
                         ("REVIEW", "ISOLATED_VALENCE_GATE_REVIEW"))

    def test_ambiguity_items_use_the_same_target(self):
        self.assertEqual(evaluate_gate("persistent_ambiguity", "ambiguous_dual_use"),
                         ("PASS", None))

    def test_null_gates(self):
        self.assertEqual(evaluate_gate("null_benign", "clearly_benign")[0], "PASS")
        self.assertEqual(evaluate_gate("null_benign", "probably_benign")[0], "PASS")
        self.assertEqual(evaluate_gate("null_benign", "ambiguous_dual_use")[0], "FAIL")
        self.assertEqual(evaluate_gate("null_highrisk", "clearly_concerning")[0], "PASS")
        self.assertEqual(evaluate_gate("null_highrisk", "probably_concerning")[0], "PASS")
        self.assertEqual(evaluate_gate("null_highrisk", "probably_benign")[0], "FAIL")


class BlindOrderingEnforcementTests(unittest.TestCase):
    def setUp(self):
        self.blind = load(BLIND)
        self.key = load(KEY)
        self.qc = load(QC)

    def test_context_review_refused_before_blind_annotation(self):
        with self.assertRaises(QCError) as ctx:
            record_context(copy.deepcopy(self.qc), self.blind, self.key,
                           [{"research_item_id": "RI-DU-001",
                             "context_relevance": {"context_is_material": "true"},
                             "notes": {"context_is_material": "n"}}],
                           None, "researcher_self_review", TS)
        self.assertIn("blind ordering", str(ctx.exception))

    def test_context_review_refused_after_single_rater(self):
        # E2a fail-closed gate: one rating (PARTIAL_ONE_RATER) must NOT open
        # context. The positive path (two independent ratings +
        # agreement/adjudication) is covered by the two-rater tests below;
        # a positive path with real human provenance is reviewer material.
        blind = copy.deepcopy(self.blind)
        qc = copy.deepcopy(self.qc)
        bid = next(m["blind_id"] for m in self.key["mapping"]
                   if m["research_item_id"] == "RI-DU-001")
        record_blind(blind, self.key, [{"blind_id": bid, "rater": "rater_a",
                                        "valence": "ambiguous_dual_use",
                                        "confidence": "high"}],
                     None, "researcher_self_review", TS)
        with self.assertRaises(QCError) as ctx:
            record_context(qc, blind, self.key,
                           [{"research_item_id": "RI-DU-001",
                             "context_relevance": {"context_is_material": "true"},
                             "notes": {"context_is_material": "concrete task detail"}}],
                           None, "researcher_self_review", TS)
        self.assertIn("ADJUDICATED", str(ctx.exception))
        self.assertIn("blind ordering", str(ctx.exception))
        item = next(i for i in qc["items"] if i["research_item_id"] == "RI-DU-001")
        self.assertEqual(item["context_review"]["status"], "NOT_STARTED")


class AnnotationRecordingTests(unittest.TestCase):
    def setUp(self):
        self.blind = load(BLIND)
        self.key = load(KEY)
        self.qc = load(QC)

    def test_reviewer_identity_required(self):
        with self.assertRaises(QCError):
            record_blind(copy.deepcopy(self.blind), self.key,
                         [{"blind_id": "BLIND-001", "rater": "rater_a",
                           "valence": "ambiguous_dual_use", "confidence": "high"}],
                         None, None, TS)

    def test_invalid_scale_values_refused(self):
        for bad in ({"valence": "looks_ok", "confidence": "high"},
                    {"valence": "ambiguous_dual_use", "confidence": "very"}):
            with self.assertRaises(QCError):
                record_blind(copy.deepcopy(self.blind), self.key,
                             [{"blind_id": "BLIND-011", "rater": "rater_a", **bad}],
                             None, "r", TS)

    def test_reannotation_is_a_conflict(self):
        blind = copy.deepcopy(self.blind)
        entry = [{"blind_id": "BLIND-011", "rater": "rater_a",
                  "valence": "ambiguous_dual_use", "confidence": "high"}]
        record_blind(blind, self.key, entry, None, "r", TS)
        with self.assertRaises(QCError) as ctx:
            record_blind(blind, self.key, entry, None, "r", "2026-08-15T09:00:00Z")
        self.assertIn("already annotated", str(ctx.exception))

    def test_two_rater_agreement_computed_only_from_real_annotations(self):
        blind = copy.deepcopy(self.blind)
        for i in range(11, 21):
            bid = f"BLIND-{i:03d}"
            record_blind(blind, self.key,
                         [{"blind_id": bid, "rater": "rater_a",
                           "valence": "ambiguous_dual_use", "confidence": "high"}],
                         None, "rater one", TS)
        proto = blind["two_rater_protocol"]
        self.assertEqual(proto["inter_rater_status"], "not_available")
        self.assertIsNone(proto["cohens_kappa"])

        for i in range(11, 21):
            bid = f"BLIND-{i:03d}"
            valence = "ambiguous_dual_use" if i <= 18 else "probably_benign"
            record_blind(blind, self.key,
                         [{"blind_id": bid, "rater": "rater_b",
                           "valence": valence, "confidence": "medium"}],
                         None, "rater two", TS)
        proto = blind["two_rater_protocol"]
        self.assertEqual(proto["inter_rater_status"], "available")
        self.assertEqual(proto["n_double_annotated"], 10)
        self.assertAlmostEqual(proto["percent_agreement"], 0.8)
        self.assertIsNotNone(proto["cohens_kappa"])
        # E2a-R1: role-only ratings record fine, but ADJUDICATED status on
        # role-only slots is not two-rater evidence — the 8 agreed items must
        # be flagged, while the 2 disagreements stay gate-pending, not errors.
        evidence_errors = [e for e in validate_blind(blind)
                           if "without complete two-rater evidence" in e]
        self.assertEqual(len(evidence_errors), 8)

    def test_disagreement_blocks_adjudication(self):
        blind = copy.deepcopy(self.blind)
        record_blind(blind, self.key, [{"blind_id": "BLIND-011", "rater": "rater_a",
                                        "valence": "ambiguous_dual_use",
                                        "confidence": "high"}], None, "r1", TS)
        record_blind(blind, self.key, [{"blind_id": "BLIND-011", "rater": "rater_b",
                                        "valence": "clearly_benign",
                                        "confidence": "high"}], None, "r2", TS)
        item = next(i for i in blind["items"] if i["blind_id"] == "BLIND-011")
        self.assertEqual(item["annotation_status"], "DISAGREEMENT_PENDING_ADJUDICATION")
        self.assertIsNone(item["adjudicated_valence"])
        self.assertIsNone(item["gate_result"])

    def test_gate_flag_recorded_without_auto_rejection(self):
        blind = copy.deepcopy(self.blind)
        unavailable = {i["blind_id"] for i in self.blind["items"]
                       if i.get("requires_fresh_presentation_session")
                       or i["annotation_status"] != "PENDING"}
        bid = next(m["blind_id"] for m in self.key["mapping"]
                   if m["category"] == "dual_use_nonnull"
                   and m["blind_id"] not in unavailable)
        for rater in ("rater_a", "rater_b"):
            record_blind(blind, self.key, [{"blind_id": bid, "rater": rater,
                                            "valence": "clearly_benign",
                                            "confidence": "high"}], None, "r", TS)
        item = next(i for i in blind["items"] if i["blind_id"] == bid)
        self.assertEqual(item["gate_result"], "FAIL")
        self.assertEqual(item["gate_flag"], "ISOLATED_VALENCE_GATE_FAIL")
        # a failed gate must not rewrite or remove the item
        self.assertEqual(item["canonical_final_prompt"],
                         next(i["canonical_final_prompt"] for i in self.blind["items"]
                              if i["blind_id"] == bid))

    def test_true_and_unclear_context_answers_require_notes(self):
        blind, qc = copy.deepcopy(self.blind), copy.deepcopy(self.qc)
        bid = next(m["blind_id"] for m in self.key["mapping"]
                   if m["research_item_id"] == "RI-DU-001")
        # Two-rater mandate (F-06 remediation): the old single-rater setup could
        # no longer reach KEEP, so the helper now performs both independent
        # ratings; agreement records ADJUDICATED and computes the gate.
        for rater in ("rater_a", "rater_b"):
            record_blind(blind, self.key, [{"blind_id": bid, "rater": rater,
                                            "valence": "ambiguous_dual_use",
                                            "confidence": "high"}], f"ID-{rater}", "r", TS)
        for value in ("true", "unclear"):
            with self.assertRaises(QCError):
                record_context(copy.deepcopy(qc), blind, self.key,
                               [{"research_item_id": "RI-DU-001",
                                 "context_relevance": {"context_is_material": value}}],
                               None, "r", TS)

    def test_low_naturalness_and_safety_fail_require_notes(self):
        blind, qc = copy.deepcopy(self.blind), copy.deepcopy(self.qc)
        bid = next(m["blind_id"] for m in self.key["mapping"]
                   if m["research_item_id"] == "RI-DU-001")
        # Two-rater mandate (F-06 remediation): the old single-rater setup could
        # no longer reach KEEP, so the helper now performs both independent
        # ratings; agreement records ADJUDICATED and computes the gate.
        for rater in ("rater_a", "rater_b"):
            record_blind(blind, self.key, [{"blind_id": bid, "rater": rater,
                                            "valence": "ambiguous_dual_use",
                                            "confidence": "high"}], f"ID-{rater}", "r", TS)
        for payload in ({"naturalness": "low"}, {"safety_status": "FAIL"}):
            with self.assertRaises(QCError):
                record_context(copy.deepcopy(qc), blind, self.key,
                               [{"research_item_id": "RI-DU-001", **payload}],
                               None, "r", TS)


class DecisionGatingTests(unittest.TestCase):
    def setUp(self):
        self.blind = load(BLIND)
        self.key = load(KEY)
        self.qc = load(QC)

    def _fully_review(self, rid="RI-DU-001", safety="PASS", naturalness="high"):
        blind, qc = copy.deepcopy(self.blind), copy.deepcopy(self.qc)
        bid = next(m["blind_id"] for m in self.key["mapping"]
                   if m["research_item_id"] == rid)
        # Two-rater mandate (F-06 remediation): the old single-rater setup could
        # no longer reach KEEP, so the helper now performs both independent
        # ratings; agreement records ADJUDICATED and computes the gate.
        for rater in ("rater_a", "rater_b"):
            record_blind(blind, self.key, [{"blind_id": bid, "rater": rater,
                                            "valence": "ambiguous_dual_use",
                                            "confidence": "high"}], f"ID-{rater}", "r", TS)
        record_context(qc, blind, self.key, [{
            "research_item_id": rid,
            "context_relevance": {"context_is_material": "true"},
            "notes": {"context_is_material": "concrete detail carries the signal"},
            "naturalness": naturalness,
            "naturalness_notes": "reads naturally" if naturalness == "low" else None,
            "safety_status": safety,
            "safety_notes": "issue found" if safety == "FAIL" else None,
        }], None, "researcher_self_review", TS)
        return blind, qc

    def test_keep_refused_without_completed_reviews(self):
        with self.assertRaises(QCError) as ctx:
            record_decision(copy.deepcopy(self.qc), self.blind, self.key,
                            [{"research_item_id": "RI-DU-001", "decision": "KEEP"}],
                            None, "r", TS)
        self.assertIn("KEEP requires completed", str(ctx.exception))

    def test_keep_refused_when_safety_failed(self):
        blind, qc = self._fully_review(safety="FAIL")
        with self.assertRaises(QCError) as ctx:
            record_decision(qc, blind, self.key,
                            [{"research_item_id": "RI-DU-001", "decision": "KEEP"}],
                            None, "r", TS)
        self.assertIn("safety_status is FAIL", str(ctx.exception))

    def test_keep_refused_on_structural_failure(self):
        blind, qc = self._fully_review()
        item = next(i for i in qc["items"] if i["research_item_id"] == "RI-DU-001")
        item["structural_verification"]["passes"] = False
        with self.assertRaises(QCError) as ctx:
            record_decision(qc, blind, self.key,
                            [{"research_item_id": "RI-DU-001", "decision": "KEEP"}],
                            None, "r", TS)
        self.assertIn("CRITICAL_STRUCTURAL_FAIL", str(ctx.exception))

    def test_valid_keep_sets_researcher_qc_and_validates(self):
        blind, qc = self._fully_review()
        record_decision(qc, blind, self.key,
                        [{"research_item_id": "RI-DU-001", "decision": "KEEP"}],
                        None, "researcher_self_review", TS)
        item = next(i for i in qc["items"] if i["research_item_id"] == "RI-DU-001")
        self.assertTrue(item["researcher_qc"])
        self.assertEqual(item["stimulus_review_status"], "KEEP")
        self.assertTrue(item["suitable_for_model_evaluation"])
        self.assertEqual(qc["counts"]["keep"], 1)
        self.assertEqual(qc["counts"]["pending"], 49)
        self.assertFalse(qc["phase_complete"])
        self.assertEqual(validate(qc, blind, self.key), [])

    def test_revise_and_reject_require_reasons(self):
        blind, qc = self._fully_review()
        for decision in ("REVISE", "REJECT"):
            with self.assertRaises(QCError):
                record_decision(copy.deepcopy(qc), blind, self.key,
                                [{"research_item_id": "RI-DU-001",
                                  "decision": decision}], None, "r", TS)

    def test_revise_preserves_version_one_and_opens_version_two(self):
        blind, qc = self._fully_review()
        record_decision(qc, blind, self.key,
                        [{"research_item_id": "RI-DU-001", "decision": "REVISE",
                          "notes": "final prompt still leans benign"}],
                        None, "r", TS)
        item = next(i for i in qc["items"] if i["research_item_id"] == "RI-DU-001")
        self.assertFalse(item["researcher_qc"])
        self.assertEqual(item["versions"][0]["stimulus_version"], 1)
        self.assertEqual(item["revision_request"]["previous_version"], 1)
        self.assertEqual(item["revision_request"]["new_version"], 2)
        self.assertEqual(item["revision_request"]["revision_status"], "pending_revision")
        self.assertTrue(item["revision_request"]["requires_blind_rereview_if_prompt_changes"])
        self.assertEqual(validate(qc, blind, self.key), [])

    def test_reject_preserves_the_record(self):
        blind, qc = self._fully_review()
        record_decision(qc, blind, self.key,
                        [{"research_item_id": "RI-DU-001", "decision": "REJECT",
                          "notes": "scenario is not plausible"}], None, "r", TS)
        item = next(i for i in qc["items"] if i["research_item_id"] == "RI-DU-001")
        self.assertFalse(item["researcher_qc"])
        self.assertEqual(item["rejection_reason"], "scenario is not plausible")
        self.assertEqual(len(qc["items"]), 50)
        self.assertEqual(validate(qc, blind, self.key), [])

    def test_redeciding_is_a_conflict(self):
        blind, qc = self._fully_review()
        record_decision(qc, blind, self.key,
                        [{"research_item_id": "RI-DU-001", "decision": "KEEP"}],
                        None, "r", TS)
        with self.assertRaises(QCError) as ctx:
            record_decision(qc, blind, self.key,
                            [{"research_item_id": "RI-DU-001", "decision": "REJECT",
                              "notes": "changed my mind"}], None, "r",
                            "2026-08-20T09:00:00Z")
        self.assertIn("already decided", str(ctx.exception))

    def test_unreviewed_items_stay_pending(self):
        blind, qc = self._fully_review()
        record_decision(qc, blind, self.key,
                        [{"research_item_id": "RI-DU-001", "decision": "KEEP"}],
                        None, "r", TS)
        others = [i for i in qc["items"] if i["research_item_id"] != "RI-DU-001"]
        self.assertEqual(len(others), 49)
        for item in others:
            self.assertEqual(item["review_decision"], "PENDING")
            self.assertFalse(item["researcher_qc"])
            self.assertIsNone(item["reviewer_id"])


class ValidatorNegativeControlTests(unittest.TestCase):
    def setUp(self):
        self.blind = load(BLIND)
        self.key = load(KEY)
        self.qc = load(QC)

    def test_live_state_is_valid(self):
        self.assertEqual(validate_blind(self.blind), [])
        self.assertEqual(validate(self.qc, self.blind, self.key), [])

    def test_rejects_approval_without_reviews(self):
        qc = copy.deepcopy(self.qc)
        item = qc["items"][0]
        item.update(review_decision="KEEP", researcher_qc=True,
                    reviewer_role="r", review_timestamp=TS,
                    stimulus_review_status="KEEP")
        qc["counts"].update(keep=1, pending=49, researcher_qc_true=1)
        errors = validate(qc, self.blind, self.key)
        self.assertTrue(any("incomplete context_review" in e for e in errors), errors)
        self.assertTrue(any("without a blind isolated-prompt annotation" in e
                            for e in errors), errors)

    def test_rejects_approval_without_reviewer(self):
        qc = copy.deepcopy(self.qc)
        item = qc["items"][0]
        item.update(review_decision="KEEP", researcher_qc=True,
                    stimulus_review_status="KEEP", review_timestamp=None)
        qc["counts"].update(keep=1, pending=49, researcher_qc_true=1)
        errors = validate(qc, self.blind, self.key)
        self.assertTrue(any("without a recorded reviewer" in e for e in errors), errors)

    def test_rejects_fabricated_agreement_statistics(self):
        blind = copy.deepcopy(self.blind)
        blind["two_rater_protocol"]["cohens_kappa"] = 0.81
        errors = validate_blind(blind)
        self.assertTrue(any("fabricated statistics" in e for e in errors), errors)

    def test_rejects_context_review_before_blind_annotation(self):
        qc = copy.deepcopy(self.qc)
        qc["items"][0]["context_review"]["status"] = "COMPLETE"
        errors = validate(qc, self.blind, self.key)
        self.assertTrue(any("before the blind" in e for e in errors), errors)

    def test_rejects_gate_result_without_adjudication(self):
        blind = copy.deepcopy(self.blind)
        blind["items"][0]["gate_result"] = "PASS"
        errors = validate_blind(blind)
        self.assertTrue(any("gate_result set before adjudication" in e
                            for e in errors), errors)

    def test_rejects_leaked_design_field_in_blind_packet(self):
        blind = copy.deepcopy(self.blind)
        blind["items"][0]["category"] = "dual_use_nonnull"
        errors = validate_blind(blind)
        self.assertTrue(any("leaks design information" in e or "unexpected field" in e
                            for e in errors), errors)

    def test_rejects_pending_item_with_approval_residue(self):
        qc = copy.deepcopy(self.qc)
        qc["items"][0]["review_timestamp"] = TS
        errors = validate(qc, self.blind, self.key)
        self.assertTrue(any("PENDING item has a review_timestamp" in e
                            for e in errors), errors)

    def test_rejects_count_drift(self):
        qc = copy.deepcopy(self.qc)
        qc["counts"]["keep"] = 7
        errors = validate(qc, self.blind, self.key)
        self.assertTrue(any("counts.keep" in e for e in errors), errors)

    def test_rejects_model_evaluation_flag(self):
        qc = copy.deepcopy(self.qc)
        qc["model_evaluation_performed"] = True
        errors = validate(qc, self.blind, self.key)
        self.assertTrue(any("model_evaluation_performed" in e for e in errors), errors)


class IntegrityTests(unittest.TestCase):
    def test_phase7f_stimulus_v1_preserved(self):
        current = hashlib.sha256(STIMULI.read_bytes()).hexdigest()
        snapshot = hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest()
        self.assertEqual(current, snapshot,
                         "Phase 7F stimulus v1 changed during Phase 7G")

    def test_preregistration_and_protected_data_unchanged(self):
        rec = load(AUDIT / "phase7e_preregistration_hash.json")
        for rel, entry in rec["protocol_files"].items():
            actual = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
            self.assertEqual(actual, entry["sha256"], f"{rel} changed in Phase 7G")
        for rel, entry in rec["protected_files"].items():
            actual = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
            self.assertEqual(actual, entry["baseline_sha256"], f"{rel} changed")

    def test_phase7e_design_decisions_unchanged(self):
        review = load(AUDIT / "phase7e_review.json")
        self.assertEqual(review["counts"]["keep"], 50)
        self.assertEqual(review["counts"]["approved"], 50)

    def test_history_log_is_initialised_and_append_only(self):
        lines = [l for l in HISTORY.read_text(encoding="utf-8").splitlines() if l.strip()]
        self.assertGreaterEqual(len(lines), 1)
        first = json.loads(lines[0])
        self.assertEqual(first["event"], "qc_log_initialised")
        self.assertEqual(first["blind_annotations_supplied"], 0)
        self.assertIsNone(first["reviewer_id"])

    def test_no_model_results_anywhere(self):
        for path in (QC, BLIND, SUMMARY):
            blob = json.dumps(load(path))
            for field in ("model_disposition", "attack_success", "refusal_rate",
                          "latency_ms", "asr", "model_observed_effect"):
                self.assertNotIn(f'"{field}"', blob, f"{path.name} contains {field}")


class DocumentationTests(unittest.TestCase):
    def setUp(self):
        self.text = DOC.read_text(encoding="utf-8")

    def test_does_not_reveal_expected_labels_per_item(self):
        """The workflow may explain the gates, but must not table expected answers."""
        for term in ("RI-DU-0", "RI-AM-0", "RI-NB-0", "RI-NH-0"):
            self.assertNotIn(term, self.text,
                             "workflow doc maps identifiers the reviewer must not see")

    def test_documents_blinding_conflict_and_resolution(self):
        for phrase in ("blinding conflict", "BLIND-nnn", "sealed",
                       "Do not open the key file"):
            self.assertIn(phrase, self.text)

    def test_documents_review_order_and_batches(self):
        for phrase in ("Review order", "batches", "isolated", "naturalness", "safety"):
            self.assertIn(phrase.lower(), self.text.lower())

    def test_states_phase_is_incomplete(self):
        self.assertIn("INCOMPLETE", self.text)
        self.assertIn("<not supplied>", self.text)

    def test_states_automated_validation_is_not_approval(self):
        self.assertIn("not human approval", self.text.lower())


if __name__ == "__main__":
    unittest.main()


# ---------------------------------------------------------------------------
# Blinding-integrity patch: reviewer-facing examples must not anchor answers
# ---------------------------------------------------------------------------

import re  # noqa: E402

VALENCE_VALUES = ("clearly_benign", "probably_benign", "ambiguous_dual_use",
                  "probably_concerning", "clearly_concerning")


def _code_blocks(text: str) -> list[str]:
    return re.findall(r"```[a-z]*\n(.*?)```", text, re.DOTALL)


class ReviewerExampleContaminationTests(unittest.TestCase):
    """The workflow doc must not show a plausible answer for a real item."""

    def setUp(self):
        self.text = DOC.read_text(encoding="utf-8")
        self.blocks = _code_blocks(self.text)

    def test_document_contains_no_real_blind_identifier(self):
        hits = re.findall(r"BLIND-\d{3}", self.text)
        self.assertEqual(hits, [], f"reviewer doc names real blind items: {set(hits)}")

    def test_document_contains_no_real_research_item_id(self):
        hits = re.findall(r"RI-(?:DU|AM|NB|NH)-\d{3}", self.text)
        self.assertEqual(hits, [], f"reviewer doc names real research items: {set(hits)}")

    def test_examples_contain_no_filled_in_valence(self):
        """A code block may name the scale, but must not pair an item with an answer."""
        for block in self.blocks:
            if "blind_id" not in block and "valence" not in block:
                continue
            for value in VALENCE_VALUES:
                self.assertNotIn(
                    f'"{value}"', block,
                    f"example supplies a concrete valence ({value}) and would anchor")
                self.assertNotIn(
                    f": {value}", block,
                    f"example supplies a concrete valence ({value}) and would anchor")

    def test_examples_use_placeholders(self):
        example = next((b for b in self.blocks if "blind_id" in b), None)
        self.assertIsNotNone(example, "no input-format example found")
        for placeholder in ("<BLIND_ID>", "<RATER_A|RATER_B>", "<LOW|MEDIUM|HIGH>"):
            self.assertIn(placeholder, example)

    def test_examples_contain_no_category_or_expected_label(self):
        for block in self.blocks:
            low = block.lower()
            for term in ("dual_use_nonnull", "persistent_ambiguity", "null_benign",
                         "null_highrisk", "expected", "anti-forensics",
                         "expected_context_effect", "control_strategy"):
                self.assertNotIn(term, low, f"example leaks {term!r}")

    def test_contamination_incident_is_documented(self):
        self.assertIn("review_session_invalidated", self.text)
        self.assertIn("anchoring", self.text.lower())


class ContaminatedSessionProducedNoAnnotationTests(unittest.TestCase):
    """The invalidated session must have contributed nothing to the record."""

    def setUp(self):
        self.blind = load(BLIND)
        self.item = next(i for i in self.blind["items"] if i["blind_id"] == "BLIND-001")

    def test_annotation_is_attributed_to_a_clean_session(self):
        sess_no = self.item["accepted_in_session"]
        sess = next(s for s in self.item["presentation_sessions"]
                    if s["session"] == sess_no)
        self.assertFalse(sess["review_session_invalidated"])
        self.assertFalse(sess["contaminated_example_present"])
        self.assertNotEqual(sess_no, 1)

    def test_invalidated_session_accepted_nothing(self):
        sess = self.item["presentation_sessions"][0]
        self.assertTrue(sess["review_session_invalidated"])
        self.assertFalse(sess["annotation_accepted"])

    def test_superseded_value_was_never_written(self):
        """The value shown in the contaminated interface must not appear anywhere."""
        events = [json.loads(l) for l in HISTORY.read_text(encoding="utf-8").splitlines()
                  if l.strip()]
        annotations = [e for e in events if e.get("event") == "blind_annotation"
                       and e.get("blind_id") == "BLIND-001"]
        self.assertEqual(len(annotations), 1, "more than one annotation was written")
        self.assertNotEqual(annotations[0]["valence"], "ambiguous_dual_use")
        self.assertNotEqual(annotations[0]["confidence"], "medium")
        self.assertEqual(self.item["rater_a"]["isolated_prompt_valence_observed"],
                         annotations[0]["valence"])

    def test_only_one_rater_slot_is_filled(self):
        self.assertIsNotNone(self.item["rater_a"]["isolated_prompt_valence_observed"])
        self.assertIsNone(self.item["rater_b"]["isolated_prompt_valence_observed"])
        self.assertIsNone(self.item["rater_a"]["reviewer_id"])
        self.assertIsNone(self.item["rater_a"]["reviewer_notes"])

    def test_contaminated_session_recorded_as_invalidated(self):
        sessions = self.item["presentation_sessions"]
        self.assertTrue(sessions[0]["review_session_invalidated"])
        self.assertFalse(sessions[0]["annotation_accepted"])

    def test_a_clean_session_superseded_the_contaminated_one(self):
        sessions = self.item["presentation_sessions"]
        self.assertGreaterEqual(len(sessions), 2)
        self.assertFalse(sessions[-1]["review_session_invalidated"])
        self.assertFalse(self.item["requires_fresh_presentation_session"])

    def test_session_events_are_logged_but_are_not_annotations(self):
        events = [json.loads(l) for l in HISTORY.read_text(encoding="utf-8").splitlines()
                  if l.strip()]
        session_events = [e for e in events
                          if e.get("event") in {"review_session_invalidated",
                                                "review_session_opened"}]
        self.assertGreaterEqual(len(session_events), 2)
        for e in session_events:
            self.assertFalse(e["annotation_recorded"])
            self.assertEqual(e["annotation_status_after"], "PENDING")

    def test_invalidation_event_is_logged_and_is_not_an_annotation(self):
        events = [json.loads(l) for l in HISTORY.read_text(encoding="utf-8").splitlines()
                  if l.strip()]
        inv = [e for e in events if e.get("event") == "review_session_invalidated"]
        self.assertEqual(len(inv), 1)
        self.assertFalse(inv[0]["annotation_recorded"])
        self.assertEqual(inv[0]["annotation_status_after"], "PENDING")

    def test_stimulus_and_hash_preserved_for_the_item(self):
        stim = {r["canonical_final_prompt"]: r for r in load(STIMULI)["records"]}
        prompt = self.item["canonical_final_prompt"]
        self.assertIn(prompt, stim, "canonical prompt changed during the patch")
        self.assertEqual(
            hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            stim[prompt]["canonical_final_prompt_sha256"])

    def test_interface_revision_scope_is_text_only(self):
        rev = self.blind["interface_revision"]
        self.assertEqual(rev["scope"], "reviewer-facing instructional text only")
        for flag in ("stimulus_modified", "blind_key_modified",
                     "annotation_schema_modified", "protocol_modified"):
            self.assertFalse(rev[flag], flag)

    def test_blind_key_still_sealed(self):
        self.assertFalse(load(KEY)["opened"])


class InvalidatedSessionRefusalTests(unittest.TestCase):
    """A response given after a contaminated presentation must not be reusable.

    The blocked state is constructed synthetically so the guard is exercised
    regardless of which sessions happen to be open in the live record.
    """

    def setUp(self):
        self.key = load(KEY)
        self.blind = load(BLIND)

    def _blocked(self, bid="BLIND-011"):
        blind = copy.deepcopy(self.blind)
        item = next(i for i in blind["items"] if i["blind_id"] == bid)
        item["presentation_sessions"] = [{
            "session": 1, "presented_at": TS,
            "review_session_invalidated": True,
            "invalidation_reason": "synthetic contamination for test",
            "annotation_accepted": False,
        }]
        item["requires_fresh_presentation_session"] = True
        return blind, item

    def test_annotation_is_refused_until_a_fresh_session(self):
        blind, item = self._blocked()
        with self.assertRaises(QCError) as ctx:
            record_blind(blind, self.key,
                         [{"blind_id": item["blind_id"], "rater": "rater_a",
                           "valence": "ambiguous_dual_use", "confidence": "high"}],
                         None, "researcher_self_review", TS)
        msg = str(ctx.exception)
        self.assertIn("fresh presentation session is required", msg)
        self.assertIn("must not be reused", msg)

    def test_validator_flags_an_annotation_that_bypassed_the_refusal(self):
        blind, item = self._blocked()
        item["rater_a"].update(isolated_prompt_valence_observed="ambiguous_dual_use",
                               reviewer_role="r", annotated_at=TS)
        errors = validate_blind(blind)
        self.assertTrue(any("fresh presentation session is still required" in e
                            for e in errors), errors)

    def test_invalidated_session_cannot_claim_acceptance(self):
        blind, item = self._blocked()
        item["presentation_sessions"][0]["annotation_accepted"] = True
        errors = validate_blind(blind)
        self.assertTrue(any("marked as annotation_accepted" in e for e in errors), errors)

    def test_a_fresh_session_lifts_the_block(self):
        blind, item = self._blocked()
        item["presentation_sessions"].append({
            "session": 2, "presented_at": TS,
            "review_session_invalidated": False, "annotation_accepted": None})
        item["requires_fresh_presentation_session"] = False
        record_blind(blind, self.key,
                     [{"blind_id": item["blind_id"], "rater": "rater_a",
                       "valence": "ambiguous_dual_use", "confidence": "high"}],
                     None, "researcher_self_review", TS)
        self.assertEqual(item["annotation_status"], "PARTIAL_ONE_RATER")
        self.assertEqual(validate_blind(blind), [])

    def test_only_the_affected_item_carries_session_history(self):
        with_sessions = [i for i in self.blind["items"] if "presentation_sessions" in i]
        self.assertEqual(len(with_sessions), 1)
        self.assertEqual(len(self.blind["items"]) - len(with_sessions), 49)
