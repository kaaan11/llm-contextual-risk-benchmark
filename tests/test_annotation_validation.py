import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dataset.validate_annotations import validate_annotation_bundle  # noqa: E402


EXAMPLE_PATH = ROOT / "dataset" / "examples" / "synthetic_annotations.json"
SCHEMA_PATH = ROOT / "dataset" / "annotation_schema.json"


def load_examples():
    with EXAMPLE_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class AnnotationValidationTests(unittest.TestCase):
    def test_annotation_schema_and_examples_are_valid_json(self):
        with SCHEMA_PATH.open("r", encoding="utf-8") as handle:
            schema = json.load(handle)
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertIn("annotation_record", schema["$defs"])
        self.assertEqual(validate_annotation_bundle(load_examples()), [])

    def test_synthetic_examples_are_not_expert_annotations(self):
        bundle = load_examples()
        for annotation in bundle["annotations"]:
            self.assertTrue(annotation["is_synthetic_example"])
            self.assertEqual(annotation["annotator_role"], "synthetic_example")
            self.assertNotEqual(annotation["annotator_role"], "expert")

    def test_synthetic_expert_claim_is_rejected(self):
        bundle = load_examples()
        invalid = copy.deepcopy(bundle)
        invalid["annotations"][0]["annotator_role"] = "expert"
        errors = validate_annotation_bundle(invalid)
        self.assertTrue(any("expert anotasyonu" in error for error in errors))

    def test_single_turn_context_score_is_rejected(self):
        bundle = load_examples()
        invalid = copy.deepcopy(bundle)
        label = invalid["annotations"][0]["labels"]["context_dependence"]
        label["status"] = "scored"
        label["score"] = 0
        errors = validate_annotation_bundle(invalid)
        self.assertTrue(any("single_turn" in error and "context_dependence" in error for error in errors))

    def test_ordinal_score_must_be_in_range(self):
        bundle = load_examples()
        invalid = copy.deepcopy(bundle)
        invalid["annotations"][1]["labels"]["expected_risk"]["score"] = 5
        errors = validate_annotation_bundle(invalid)
        self.assertTrue(any("0–4" in error for error in errors))

    def test_validator_does_not_mutate_input(self):
        bundle = load_examples()
        before = copy.deepcopy(bundle)
        validate_annotation_bundle(bundle)
        self.assertEqual(bundle, before)


if __name__ == "__main__":
    unittest.main()
