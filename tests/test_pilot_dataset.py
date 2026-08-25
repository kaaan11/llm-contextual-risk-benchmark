import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dataset.build_pilot import build_dataset, find_duplicates, write_pilot  # noqa: E402
from dataset.validate import validate_dataset  # noqa: E402


class PilotDatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = build_dataset()

    def test_target_counts_and_unique_ids(self):
        records = self.dataset["records"]
        self.assertEqual(len(records), 300)
        self.assertEqual(len({record["sample_id"] for record in records}), 300)
        self.assertEqual(sum(record["dataset_membership"] == ["benign"] for record in records), 120)
        self.assertEqual(sum(record["dataset_membership"] == ["adversarial"] for record in records), 100)
        self.assertEqual(sum(record["dataset_membership"] == ["multi_turn"] for record in records), 80)

    def test_no_duplicates_are_found(self):
        self.assertEqual(find_duplicates(self.dataset["records"]), [])

    def test_no_expert_annotations_or_evaluations_are_claimed(self):
        self.assertTrue(all(record["annotations"] == [] for record in self.dataset["records"]))
        self.assertTrue(all(record["evaluations"] == [] for record in self.dataset["records"]))
        self.assertEqual(self.dataset["evaluation_runs"], [])
        self.assertEqual(self.dataset["analysis_runs"], [])

    def test_adversarial_content_is_sanitized(self):
        adversarial = [record for record in self.dataset["records"] if record["dataset_membership"] == ["adversarial"]]
        self.assertEqual(len(adversarial), 100)
        for record in adversarial:
            prompt = record["turns"][0]["content"]["text"]
            self.assertIn("REDAKTE EDİLMİŞ", prompt)
            self.assertIn("operasyonel ayrıntılar bu kayıt için çıkarılmıştır", prompt)

    def test_multiturn_structure_and_context_distribution(self):
        multiturn = [record for record in self.dataset["records"] if record["record_type"] == "multi_turn"]
        self.assertEqual(len(multiturn), 80)
        effects = {code: 0 for code in ("C1", "C2", "C3", "C4", "C5")}
        for record in multiturn:
            self.assertGreaterEqual(len(record["turns"]), 2)
            code = record["task_metadata"]["context_effect"]
            effects[code] += 1
        self.assertEqual(effects, {"C1": 16, "C2": 16, "C3": 16, "C4": 16, "C5": 16})

    def test_written_outputs_are_reproducible_and_valid(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = write_pilot(Path(temp_dir))
            with paths["dataset"].open("r", encoding="utf-8") as handle:
                written = json.load(handle)
            self.assertEqual(validate_dataset(written), [])
            self.assertEqual(written, self.dataset)
            self.assertEqual(len(paths["records"].read_text(encoding="utf-8").splitlines()), 300)
            attribution = json.loads(paths["attribution"].read_text(encoding="utf-8"))
            self.assertEqual(attribution["public_benchmark_imports"], [])


if __name__ == "__main__":
    unittest.main()
