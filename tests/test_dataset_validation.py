import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dataset.validate import SCHEMA_PATH, validate_dataset  # noqa: E402


def minimal_dataset():
    return {
        "schema_version": "0.1.0",
        "dataset_id": "pilot-empty",
        "dataset_version": "0.1.0",
        "release_profile": "private",
        "evaluation_runs": [],
        "records": [],
        "analysis_runs": [],
    }


def single_turn_record(sample_id="sample-001"):
    return {
        "sample_id": sample_id,
        "record_version": "0.1.0",
        "dataset_membership": ["benign"],
        "record_type": "single_turn",
        "split": "none",
        "sensitivity": "private",
        "turns": [
            {
                "turn_id": "turn-0",
                "sequence": 0,
                "role": "user",
                "content": {
                    "content_ref": "private://sample-001/turn-0",
                    "redaction_status": "reference_only",
                },
            }
        ],
        "annotations": [],
        "evaluations": [],
    }


class DatasetValidationTests(unittest.TestCase):
    def test_schema_is_valid_json(self):
        with SCHEMA_PATH.open("r", encoding="utf-8") as handle:
            schema = json.load(handle)
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertIn("record", schema["$defs"])

    def test_empty_manifest_is_valid(self):
        self.assertEqual(validate_dataset(minimal_dataset()), [])

    def test_single_turn_reference_record_is_valid(self):
        dataset = minimal_dataset()
        dataset["records"] = [single_turn_record()]
        self.assertEqual(validate_dataset(dataset), [])

    def test_duplicate_sample_ids_are_rejected(self):
        dataset = minimal_dataset()
        dataset["records"] = [single_turn_record(), single_turn_record()]
        errors = validate_dataset(dataset)
        self.assertTrue(any("tekrar eden sample_id" in error for error in errors))

    def test_multiturn_requires_membership_and_two_turns(self):
        dataset = minimal_dataset()
        record = single_turn_record()
        record["record_type"] = "multi_turn"
        dataset["records"] = [record]
        errors = validate_dataset(dataset)
        self.assertTrue(any("multi_turn en az iki turn" in error for error in errors))
        self.assertTrue(any("multi_turn membership ve record_type uyumsuz" in error for error in errors))

    def test_evaluation_requires_declared_run(self):
        dataset = minimal_dataset()
        record = single_turn_record()
        record["evaluations"] = [
            {
                "evaluation_id": "evaluation-001",
                "run_id": "run-missing",
                "evaluated_at": "2026-08-14T10:00:00Z",
                "model": {"provider": "openai", "name": "model", "version": "frozen"},
                "configuration": "baseline",
                "context_mode": "current_prompt_only",
                "response": {"content_ref": "private://response/001", "redaction_status": "reference_only"},
                "latency": {"total_ms": 1.0, "measurement_method": "test"},
            }
        ]
        dataset["records"] = [record]
        errors = validate_dataset(dataset)
        self.assertTrue(any("tanımsız run_id" in error for error in errors))

    def test_invalid_input_does_not_mutate_data(self):
        dataset = minimal_dataset()
        dataset["records"] = [single_turn_record()]
        before = copy.deepcopy(dataset)
        validate_dataset(dataset)
        self.assertEqual(dataset, before)


if __name__ == "__main__":
    unittest.main()
