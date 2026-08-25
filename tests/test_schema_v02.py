import copy
import hashlib
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dataset.validate import validate_dataset  # noqa: E402


def synthetic_v02_dataset():
    canonical_prompt = "Final prompt: explain the safe test setup."
    prompt_hash = hashlib.sha256(canonical_prompt.encode("utf-8")).hexdigest()
    turns = [
        {
            "turn_id": "turn-0",
            "sequence": 0,
            "role": "user",
            "content": {
                "text": "This is synthetic context for a validation test.",
                "redaction_status": "not_redacted",
            },
        },
        {
            "turn_id": "turn-1",
            "sequence": 1,
            "role": "user",
            "content": {
                "text": canonical_prompt,
                "redaction_status": "not_redacted",
            },
        },
    ]
    return {
        "schema_version": "0.2.0",
        "dataset_id": "synthetic-schema-v02",
        "dataset_version": "0.2.0",
        "release_profile": "private",
        "evaluation_runs": [],
        "records": [
            {
                "sample_id": "synthetic-mt-001",
                "record_version": "0.2.0",
                "dataset_membership": ["multi_turn"],
                "record_type": "multi_turn",
                "split": "none",
                "sensitivity": "private",
                "source": "original",
                "dataset_version": "0.2.0",
                "conversation_id": "synthetic-conv-001",
                "canonical_final_prompt": canonical_prompt,
                "canonical_final_prompt_sha256": prompt_hash,
                "evaluation_conditions": {
                    "final_prompt_only": {
                        "condition": "final_prompt_only",
                        "prompt": canonical_prompt,
                        "prompt_sha256": prompt_hash,
                    },
                    "full_context": {
                        "condition": "full_context",
                        "turn_ids": ["turn-0", "turn-1"],
                        "final_prompt_turn_id": "turn-1",
                    },
                },
                "expected_context_effect": "context_reduces_ambiguity",
                "model_observed_effect": None,
                "expected_risk_profile": "low",
                "design_confidence": "high",
                "composition_cell": "context_changes_interpretation",
                "context_signal_types": ["intent_clarification"],
                "expected_interpretation": "legitimate_technical",
                "expected_context_effect_rationale": "Synthetic context clarifies the intended safe task.",
                "authoring_method": "researcher_authored",
                "generation_assistance": "none",
                "source_seed": None,
                "researcher_qc": True,
                "external_validation_status": "researcher_reviewed",
                "created_at": "2026-08-14T00:00:00Z",
                "turns": turns,
                "annotations": [],
                "evaluations": [],
            }
        ],
    }


class SchemaV02Tests(unittest.TestCase):
    def assert_invalid(self, dataset, fragment):
        errors = validate_dataset(dataset)
        self.assertTrue(any(fragment in error for error in errors), errors)

    def test_valid_v02_multiturn_record(self):
        self.assertEqual(validate_dataset(synthetic_v02_dataset()), [])

    def test_v01_empty_manifest_remains_valid(self):
        dataset = synthetic_v02_dataset()
        dataset["schema_version"] = "0.1.0"
        dataset["dataset_version"] = "0.1.0"
        dataset["records"] = []
        self.assertEqual(validate_dataset(dataset), [])

    def test_v02_single_turn_does_not_require_multiturn_pair_fields(self):
        dataset = synthetic_v02_dataset()
        record = {
            "sample_id": "synthetic-st-001",
            "record_version": "0.2.0",
            "dataset_membership": ["benign"],
            "record_type": "single_turn",
            "split": "none",
            "sensitivity": "private",
            "turns": [dataset["records"][0]["turns"][0]],
            "annotations": [],
            "evaluations": [],
        }
        dataset["records"] = [record]
        self.assertEqual(validate_dataset(dataset), [])

    def test_missing_conversation_id_is_rejected(self):
        dataset = synthetic_v02_dataset()
        dataset["records"][0].pop("conversation_id")
        self.assert_invalid(dataset, "zorunlu alan eksik: conversation_id")

    def test_duplicate_conversation_id_is_rejected(self):
        dataset = synthetic_v02_dataset()
        second = copy.deepcopy(dataset["records"][0])
        second["sample_id"] = "synthetic-mt-002"
        dataset["records"].append(second)
        self.assert_invalid(dataset, "tekrar eden conversation_id")

    def test_duplicate_sample_id_is_rejected(self):
        dataset = synthetic_v02_dataset()
        dataset["records"].append(copy.deepcopy(dataset["records"][0]))
        self.assert_invalid(dataset, "tekrar eden sample_id")

    def test_missing_canonical_prompt_is_rejected(self):
        dataset = synthetic_v02_dataset()
        dataset["records"][0].pop("canonical_final_prompt")
        self.assert_invalid(dataset, "zorunlu alan eksik: canonical_final_prompt")

    def test_final_prompt_condition_must_match_canonical_prompt(self):
        dataset = synthetic_v02_dataset()
        dataset["records"][0]["evaluation_conditions"]["final_prompt_only"]["prompt"] = "different"
        self.assert_invalid(dataset, "canonical prompt ile aynı olmalı")

    def test_canonical_prompt_hash_is_checked(self):
        dataset = synthetic_v02_dataset()
        dataset["records"][0]["canonical_final_prompt_sha256"] = "0" * 64
        self.assert_invalid(dataset, "canonical prompt ile eşleşmiyor")

    def test_final_turn_must_match_canonical_prompt_exactly(self):
        dataset = synthetic_v02_dataset()
        dataset["records"][0]["turns"][-1]["content"]["text"] = "different"
        self.assert_invalid(dataset, "canonical prompt ile tam olarak aynı olmalı")

        dataset = synthetic_v02_dataset()
        dataset["records"][0]["turns"][-1]["role"] = "assistant"
        self.assert_invalid(dataset, "final prompt turn user rolünde olmalı")

    def test_full_context_condition_must_match_ordered_turns(self):
        dataset = synthetic_v02_dataset()
        dataset["records"][0]["evaluation_conditions"]["full_context"]["turn_ids"] = ["turn-1", "turn-0"]
        self.assert_invalid(dataset, "turns ile aynı sırada olmalı")

    def test_invalid_evaluation_condition_is_rejected(self):
        dataset = synthetic_v02_dataset()
        dataset["records"][0]["evaluation_conditions"]["final_prompt_only"]["condition"] = "full_context"
        self.assert_invalid(dataset, "sabit değer hatalı")

    def test_expected_context_effect_is_required_and_enum_checked(self):
        dataset = synthetic_v02_dataset()
        dataset["records"][0].pop("expected_context_effect")
        self.assert_invalid(dataset, "zorunlu alan eksik: expected_context_effect")

        dataset = synthetic_v02_dataset()
        dataset["records"][0]["expected_context_effect"] = "invented_effect"
        self.assert_invalid(dataset, "expected_context_effect: geçersiz değer")

    def test_observed_effect_cannot_be_filled_before_evaluation(self):
        dataset = synthetic_v02_dataset()
        dataset["records"][0]["model_observed_effect"] = "context_increases_risk"
        self.assert_invalid(dataset, "örnek üretimi aşamasında null olmalı")

        self.assertEqual(
            validate_dataset(dataset, allow_observed_effect=True),
            [],
        )

    def test_provenance_fields_are_validated(self):
        dataset = synthetic_v02_dataset()
        dataset["records"][0]["authoring_method"] = "invented_method"
        self.assert_invalid(dataset, "authoring_method: geçersiz değer")

        dataset = synthetic_v02_dataset()
        dataset["records"][0]["generation_assistance"] = "invented_assistance"
        self.assert_invalid(dataset, "generation_assistance: geçersiz değer")

        dataset = synthetic_v02_dataset()
        dataset["records"][0]["source_seed"] = {"source_dataset": "only-partial"}
        self.assert_invalid(dataset, "source_seed: zorunlu alan eksik")

    def test_expected_risk_profile_and_confidence_are_checked(self):
        dataset = synthetic_v02_dataset()
        dataset["records"][0]["expected_risk_profile"] = "expert_reviewed"
        self.assert_invalid(dataset, "expected_risk_profile: geçersiz değer")

        dataset = synthetic_v02_dataset()
        dataset["records"][0]["design_confidence"] = "certain"
        self.assert_invalid(dataset, "design_confidence: geçersiz değer")

    def test_researcher_qc_must_be_boolean(self):
        dataset = synthetic_v02_dataset()
        dataset["records"][0]["researcher_qc"] = "yes"
        self.assert_invalid(dataset, "researcher_qc: boolean olmalı")

    def test_record_dataset_version_must_match_root(self):
        dataset = synthetic_v02_dataset()
        dataset["records"][0]["dataset_version"] = "0.1.0"
        self.assert_invalid(dataset, "root dataset_version ile aynı olmalı")

    def test_researcher_qc_and_review_status_must_be_consistent(self):
        dataset = synthetic_v02_dataset()
        dataset["records"][0]["researcher_qc"] = True
        dataset["records"][0]["external_validation_status"] = "not_reviewed"
        self.assert_invalid(dataset, "en az researcher_reviewed durumu gerekli")

        dataset = synthetic_v02_dataset()
        dataset["records"][0]["researcher_qc"] = False
        dataset["records"][0]["external_validation_status"] = "researcher_reviewed"
        self.assert_invalid(dataset, "researcher_qc=true gerekli")

    def test_expert_or_external_validation_cannot_be_claimed(self):
        for status in ("expert_reviewed", "externally_validated"):
            dataset = synthetic_v02_dataset()
            dataset["records"][0]["external_validation_status"] = status
            self.assert_invalid(dataset, "uzman veya dış doğrulama iddiası")

        dataset = synthetic_v02_dataset()
        dataset["records"][0]["external_validation_status"] = "expert_reviewed"
        self.assertEqual(validate_dataset(dataset, allow_reviewed_status=True), [])


if __name__ == "__main__":
    unittest.main()
