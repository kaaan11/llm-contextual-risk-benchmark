"""Phase 7F — stimulus dataset structural, textual-integrity and safety tests."""

from __future__ import annotations

import hashlib
import json
import sys
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "dataset" / "pilot" / "multiturn"))

from build_stimulus_dataset import (  # noqa: E402
    SAFETY_PATTERNS, estimate_tokens, normalise, sha256_text, structural_validation,
)

DATA = ROOT / "dataset" / "pilot" / "multiturn" / "stimulus_dataset_v1.json"
JSONL = ROOT / "dataset" / "pilot" / "multiturn" / "stimulus_records.jsonl"
README = ROOT / "dataset" / "pilot" / "multiturn" / "STIMULUS_README.md"
DOC = ROOT / "docs" / "phase7f_stimulus_generation.md"
AUDIT = ROOT / "results" / "dataset_audit"
REVIEW = AUDIT / "phase7e_review.json"

EXPECTED_CATEGORIES = {
    "dual_use_nonnull": 30, "persistent_ambiguity": 7,
    "null_benign": 7, "null_highrisk": 6,
}
CONDITION_NAMES = {
    "final_prompt_only", "full_context_legitimating",
    "full_context_incriminating", "neutral_filler_control",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class DatasetShapeTests(unittest.TestCase):
    def setUp(self):
        self.data = load(DATA)
        self.records = self.data["records"]

    def test_exactly_fifty_research_items(self):
        self.assertEqual(len(self.records), 50)
        self.assertEqual(self.data["record_count"], 50)
        ids = [r["research_item_id"] for r in self.records]
        self.assertEqual(len(set(ids)), 50)

    def test_category_distribution_preserved(self):
        counts = {}
        for r in self.records:
            counts[r["category"]] = counts.get(r["category"], 0) + 1
        self.assertEqual(counts, EXPECTED_CATEGORIES)

    def test_every_item_has_abc(self):
        for r in self.records:
            for name in ("final_prompt_only", "full_context_legitimating",
                         "full_context_incriminating"):
                self.assertIn(name, r["conditions"], r["research_item_id"])

    def test_d_exists_only_where_design_requires_it(self):
        d_count = 0
        for r in self.records:
            has_d = "neutral_filler_control" in r["conditions"]
            self.assertEqual(has_d, r["design"]["control_strategy"] == "N",
                             r["research_item_id"])
            d_count += has_d
        self.assertEqual(d_count, 21)

    def test_condition_names_are_valid(self):
        for r in self.records:
            self.assertTrue(set(r["conditions"]).issubset(CONDITION_NAMES))

    def test_jsonl_matches_json(self):
        lines = [json.loads(l) for l in JSONL.read_text(encoding="utf-8").splitlines() if l.strip()]
        self.assertEqual(len(lines), 50)
        self.assertEqual([l["research_item_id"] for l in lines],
                         [r["research_item_id"] for r in self.records])

    def test_language_is_english_only(self):
        self.assertEqual(self.data["language"], "en")
        for r in self.records:
            self.assertEqual(r["language"], "en")


class TextualIntegrityTests(unittest.TestCase):
    """Section 19: exact string equality and hash agreement."""

    def setUp(self):
        self.records = load(DATA)["records"]

    def test_final_turn_equals_canonical_prompt_in_every_condition(self):
        for r in self.records:
            prompt = r["canonical_final_prompt"]
            for name, cond in r["conditions"].items():
                self.assertEqual(cond["final_user_turn_text"], prompt,
                                 f"{r['research_item_id']}/{name}")
                self.assertEqual(cond["turns"][-1]["content"]["text"], prompt,
                                 f"{r['research_item_id']}/{name}")

    def test_recorded_hash_matches_canonical_prompt(self):
        for r in self.records:
            self.assertEqual(
                r["canonical_final_prompt_sha256"],
                hashlib.sha256(r["canonical_final_prompt"].encode("utf-8")).hexdigest(),
                r["research_item_id"])

    def test_hash_matches_every_applicable_condition(self):
        for r in self.records:
            for name, cond in r["conditions"].items():
                self.assertEqual(
                    sha256_text(cond["final_user_turn_text"]),
                    r["canonical_final_prompt_sha256"],
                    f"{r['research_item_id']}/{name}")

    def test_no_whitespace_or_case_drift_between_conditions(self):
        for r in self.records:
            texts = {c["final_user_turn_text"] for c in r["conditions"].values()}
            self.assertEqual(len(texts), 1, r["research_item_id"])

    def test_a_mismatch_would_fail_validation(self):
        """Negative control: corrupting one condition must be detected."""
        records = load(DATA)["records"]
        target = records[0]["conditions"]["full_context_legitimating"]
        target["final_user_turn_text"] += " "
        target["turns"][-1]["content"]["text"] += " "
        errors = structural_validation(records)
        self.assertTrue(any("differs from canonical prompt" in e for e in errors), errors)

    def test_a_hash_mismatch_would_fail_validation(self):
        records = load(DATA)["records"]
        records[0]["canonical_final_prompt_sha256"] = "0" * 64
        errors = structural_validation(records)
        self.assertTrue(any("hash does not match" in e for e in errors), errors)


class TurnStructureTests(unittest.TestCase):
    def setUp(self):
        self.records = load(DATA)["records"]

    def test_condition_a_is_exactly_one_user_turn(self):
        for r in self.records:
            a = r["conditions"]["final_prompt_only"]
            self.assertEqual(a["turn_count"], 1, r["research_item_id"])
            self.assertEqual(a["turns"][0]["role"], "user")

    def test_context_conditions_have_preceding_turns(self):
        for r in self.records:
            for name in ("full_context_legitimating", "full_context_incriminating"):
                self.assertGreaterEqual(r["conditions"][name]["turn_count"], 3,
                                        f"{r['research_item_id']}/{name}")

    def test_turn_sequences_are_contiguous_and_end_with_user(self):
        for r in self.records:
            for name, cond in r["conditions"].items():
                seqs = [t["sequence"] for t in cond["turns"]]
                self.assertEqual(seqs, list(range(len(seqs))), f"{r['research_item_id']}/{name}")
                self.assertEqual(cond["turns"][-1]["role"], "user")
                self.assertTrue(cond["turns"][-1]["is_canonical_final_prompt"])

    def test_roles_are_restricted_to_user_and_assistant(self):
        for r in self.records:
            for cond in r["conditions"].values():
                for t in cond["turns"]:
                    self.assertIn(t["role"], {"user", "assistant"})

    def test_turn_ids_are_unique_within_an_item(self):
        for r in self.records:
            ids = [t["turn_id"] for c in r["conditions"].values() for t in c["turns"]]
            self.assertEqual(len(ids), len(set(ids)), r["research_item_id"])


class ContextQualityTests(unittest.TestCase):
    def setUp(self):
        self.records = load(DATA)["records"]

    def test_b_and_c_contexts_differ(self):
        for r in self.records:
            b = [t["content"]["text"] for t in
                 r["conditions"]["full_context_legitimating"]["turns"][:-1]]
            c = [t["content"]["text"] for t in
                 r["conditions"]["full_context_incriminating"]["turns"][:-1]]
            self.assertNotEqual(b, c, r["research_item_id"])

    def test_d_context_differs_from_both_b_and_c(self):
        for r in self.records:
            d = r["conditions"].get("neutral_filler_control")
            if not d:
                continue
            dtext = [t["content"]["text"] for t in d["turns"][:-1]]
            for name in ("full_context_legitimating", "full_context_incriminating"):
                other = [t["content"]["text"] for t in r["conditions"][name]["turns"][:-1]]
                self.assertNotEqual(dtext, other, r["research_item_id"])

    def test_every_d_arm_documents_its_rationale(self):
        for r in self.records:
            if "neutral_filler_control" in r["conditions"]:
                self.assertTrue((r["d_control_rationale"] or "").strip(),
                                r["research_item_id"])
            else:
                self.assertIsNone(r["d_control_rationale"], r["research_item_id"])

    def test_self_audit_passed_for_every_item(self):
        for r in self.records:
            for question, result in r["self_audit"].items():
                self.assertTrue(result, f"{r['research_item_id']}: {question}")

    def test_context_length_spread_is_bounded(self):
        for r in self.records:
            self.assertLessEqual(r["context_token_spread"], 40, r["research_item_id"])

    def test_prompts_are_not_duplicated_across_items(self):
        prompts = [r["canonical_final_prompt"] for r in self.records]
        self.assertEqual(len(set(prompts)), 50)

    def test_contexts_are_not_templated_copies(self):
        """Naturalness proxy: no context turn text is reused across items."""
        seen = {}
        for r in self.records:
            for cond in r["conditions"].values():
                for t in cond["turns"][:-1]:
                    key = normalise(t["content"]["text"])
                    if key in seen and seen[key] != r["research_item_id"]:
                        self.fail(f"context text reused across "
                                  f"{seen[key]} and {r['research_item_id']}")
                    seen[key] = r["research_item_id"]


class ValenceLeakageTests(unittest.TestCase):
    """Non-null final prompts must not carry the answer themselves."""

    # Union of the builder gate (scripts/build_stimulus_dataset.py
    # VALENCE_LEAK_TERMS) and this test's original list — remediation F-28 made
    # the test the strictest single source so the two implementations cannot
    # drift apart silently.
    BANNED = (
        "without being detected", "without anyone noticing", "undetected", "evade",
        "evading", "bypass detection", "hide from", "conceal", "conceal from",
        "cover my tracks", "without leaving a trace",
        "i am authorized", "i'm authorized", "i am authorised", "i have permission",
        "for educational purposes", "this is a lab", "i am a security researcher",
        "in my authorized",
    )

    def setUp(self):
        self.records = load(DATA)["records"]

    def test_dual_use_and_ambiguity_prompts_are_clean(self):
        for r in self.records:
            if r["category"] not in {"dual_use_nonnull", "persistent_ambiguity"}:
                continue
            prompt = normalise(r["canonical_final_prompt"])
            for term in self.BANNED:
                self.assertNotIn(term, prompt,
                                 f"{r['research_item_id']} final prompt leaks {term!r}")

    def test_design_labels_do_not_appear_in_any_turn(self):
        labels = ("dual_use_nonnull", "persistent_ambiguity", "null_benign",
                  "null_highrisk", "expected_context_effect", "control_strategy",
                  "legitimating context", "incriminating context", "neutral filler")
        for r in self.records:
            for cond in r["conditions"].values():
                for t in cond["turns"]:
                    norm = normalise(t["content"]["text"])
                    for label in labels:
                        self.assertNotIn(label, norm,
                                         f"{r['research_item_id']} leaks {label!r}")

    def test_expected_effect_text_does_not_leak_into_content(self):
        for r in self.records:
            effect = normalise(r["design"]["expected_context_effect"])
            for cond in r["conditions"].values():
                for t in cond["turns"]:
                    self.assertNotIn(effect, normalise(t["content"]["text"]))


class SafetyTests(unittest.TestCase):
    def setUp(self):
        self.records = load(DATA)["records"]
        self.scan = load(AUDIT / "stimulus_safety_scan.json")

    def test_no_safety_pattern_matches_anywhere(self):
        for r in self.records:
            for cond in r["conditions"].values():
                for t in cond["turns"]:
                    for name, pattern in SAFETY_PATTERNS.items():
                        self.assertIsNone(pattern.search(t["content"]["text"]),
                                          f"{t['turn_id']} matched {name}")

    def test_scan_disclaims_being_human_review(self):
        self.assertIn("does NOT constitute human safety review", self.scan["disclaimer"])
        self.assertTrue(self.scan["human_review_required"])
        self.assertFalse(self.scan["human_review_performed"])

    def test_high_risk_items_contain_no_operational_content(self):
        """Ceiling controls must be requests only: no code, no procedure, no target."""
        forbidden = ("```", "import ", "def ", "#!/", "http://", "https://",
                     "step 1", "first, ", "you can use", "here's how")
        for r in self.records:
            if r["category"] != "null_highrisk":
                continue
            for cond in r["conditions"].values():
                for t in cond["turns"]:
                    low = t["content"]["text"].lower()
                    for term in forbidden:
                        self.assertNotIn(term, low, f"{t['turn_id']} contains {term!r}")

    def test_high_risk_prompts_name_no_real_target(self):
        for r in self.records:
            if r["category"] != "null_highrisk":
                continue
            prompt = r["canonical_final_prompt"]
            self.assertIsNone(SAFETY_PATTERNS["cve_identifier"].search(prompt))
            self.assertIsNone(SAFETY_PATTERNS["hostname_like"].search(prompt))
            self.assertIsNone(SAFETY_PATTERNS["url"].search(prompt))

    def test_high_risk_assistant_turns_do_not_assist(self):
        """The scripted assistant turns must not model compliant harmful behaviour."""
        for r in self.records:
            if r["category"] != "null_highrisk":
                continue
            for cond in r["conditions"].values():
                for t in cond["turns"]:
                    if t["role"] != "assistant":
                        continue
                    self.assertLess(len(t["content"]["text"].split()), 40, t["turn_id"])


class ProvenanceAndGateTests(unittest.TestCase):
    def setUp(self):
        self.data = load(DATA)
        self.records = self.data["records"]

    def test_provenance_fields(self):
        for r in self.records:
            self.assertEqual(r["authoring_method"], "researcher_specified_llm_assisted_draft")
            self.assertEqual(r["generation_assistance"], "drafting_only")
            self.assertEqual(r["source"], "original")
            self.assertIsNone(r["source_seed"])
            self.assertEqual(r["stimulus_version"], 1)
            self.assertEqual(r["dataset_version"], "0.3.0")
            self.assertTrue(r["created_at"])

    def test_no_human_approval_is_claimed(self):
        self.assertFalse(self.data["researcher_qc"])
        self.assertEqual(self.data["stimulus_review_status"], "PENDING")
        for r in self.records:
            self.assertFalse(r["researcher_qc"], r["research_item_id"])
            self.assertEqual(r["stimulus_review_status"], "PENDING")
            self.assertEqual(r["external_validation_status"], "not_reviewed")

    def test_phase7g_annotations_are_absent(self):
        for r in self.records:
            for field in ("isolated_prompt_valence_observed", "adjudicated_valence",
                          "refusal_appropriateness_reference", "model_observed_effect"):
                self.assertIsNone(r[field], f"{r['research_item_id']}.{field}")

    def test_no_model_results_present(self):
        blob = json.dumps(self.data)
        for field in ("model_disposition", "latency_ms", "attack_success",
                      "refusal_rate", "asr", "evaluations", "responses"):
            self.assertNotIn(f'"{field}"', blob)
        self.assertFalse(self.data["model_evaluations_run"])
        self.assertFalse(self.data["blind_review_performed"])

    def test_unit_of_analysis_is_declared_paired(self):
        self.assertEqual(self.data["unit_of_analysis"], "research_item")
        self.assertTrue(self.data["conditions_are_paired_not_independent"])

    def test_design_layer_is_preserved_verbatim(self):
        approved = {i["research_item_id"]: i["versions"][i["current_version"] - 1]["design"]
                    for i in load(REVIEW)["items"]}
        for r in self.records:
            self.assertEqual(r["design"], approved[r["research_item_id"]],
                             f"{r['research_item_id']} design was modified")

    def test_all_items_were_researcher_approved(self):
        for r in self.records:
            self.assertEqual(r["researcher_approval_status"], "KEEP")


class AuditReportTests(unittest.TestCase):
    def test_all_reports_exist_and_are_clean(self):
        val = load(AUDIT / "stimulus_validation.json")
        self.assertTrue(val["structural_valid"])
        self.assertEqual(val["structural_errors"], [])
        self.assertEqual(val["generation_flags"], [])
        self.assertEqual(val["design_leakage_findings"], [])

    def test_statistics_report_is_consistent(self):
        stats = load(AUDIT / "stimulus_statistics.json")
        self.assertEqual(stats["total_research_items"], 50)
        self.assertEqual(stats["condition_availability"],
                         {"A": 50, "B": 50, "C": 50, "D": 21})
        self.assertEqual(stats["category_distribution"], EXPECTED_CATEGORIES)
        self.assertEqual(stats["validation_failures"], 0)
        self.assertEqual(stats["review_status"]["researcher_qc_true"], 0)

    def test_overlap_report_records_no_duplicates(self):
        ov = load(AUDIT / "stimulus_overlap_report.json")
        self.assertEqual(ov["exact_duplicates"], [])
        self.assertEqual(ov["normalised_duplicates"], [])
        self.assertEqual(ov["high_similarity"], [])
        self.assertFalse(ov["public_benchmark_modified"])
        self.assertIn("preliminary_blocked", ov["public_benchmark_note"])

    def test_generation_report_disclaims_evaluation_and_expertise(self):
        rep = load(AUDIT / "stimulus_generation_report.json")
        for flag in ("expert_authorship_claimed", "expert_validation_claimed",
                     "design_modified", "preregistration_modified", "model_api_called",
                     "model_evaluation_performed", "blind_review_performed",
                     "asr_computed", "refusal_rate_computed", "latency_computed",
                     "public_benchmark_modified", "turkish_dataset_modified",
                     "next_phase_started"):
            self.assertFalse(rep[flag], flag)
        self.assertEqual(rep["stimuli_generated"], 50)


class ProtectedDataStillUnchangedTests(unittest.TestCase):
    def test_turkish_and_public_corpora_are_byte_identical(self):
        baseline = load(AUDIT / "phase7e_preregistration_hash.json")["protected_files"]
        for rel, entry in baseline.items():
            actual = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
            self.assertEqual(actual, entry["baseline_sha256"], f"{rel} was modified")

    def test_preregistration_documents_unchanged(self):
        rec = load(AUDIT / "phase7e_preregistration_hash.json")
        for rel, entry in rec["protocol_files"].items():
            actual = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
            self.assertEqual(actual, entry["sha256"], f"{rel} changed during Phase 7F")


class DocumentationTests(unittest.TestCase):
    def test_readme_covers_required_sections(self):
        text = README.read_text(encoding="utf-8")
        for heading in ("Purpose", "Relationship to the research-item design",
                        "Conditions", "canonical final prompt", "Provenance",
                        "AI-assisted drafting", "Limitations", "Safety", "Review status"):
            self.assertIn(heading, text)

    def test_methodology_doc_covers_required_sections(self):
        text = DOC.read_text(encoding="utf-8")
        for heading in ("Generation methodology", "Canonical prompt construction",
                        "Condition construction", "D control construction",
                        "Provenance", "Versioning", "Safety review",
                        "Overlap detection", "Limitations"):
            self.assertIn(heading, text)


class HeuristicTests(unittest.TestCase):
    def test_token_estimate_is_documented_as_a_heuristic(self):
        stats = load(AUDIT / "stimulus_statistics.json")
        self.assertIn("not a tokenizer", stats["estimated_input_tokens"]["method"])
        self.assertEqual(estimate_tokens("one two three four"), 5)

    def test_normalisation_is_unicode_and_case_insensitive(self):
        self.assertEqual(normalise("  Ｈello   WORLD "), "hello world")


if __name__ == "__main__":
    unittest.main()
