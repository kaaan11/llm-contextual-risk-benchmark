import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.build_pilot_manifest import (  # noqa: E402
    ManifestBlockedError,
    build_manifest,
    normalized_text,
)


AUDIT = ROOT / "results" / "dataset_audit"


class Phase6BAuditTests(unittest.TestCase):
    def test_audit_reports_are_machine_readable_and_blocked(self):
        source_inventory = json.loads((AUDIT / "source_inventory.json").read_text(encoding="utf-8"))
        sampling = json.loads((AUDIT / "sampling_report.json").read_text(encoding="utf-8"))
        overlap = json.loads((AUDIT / "overlap_report.json").read_text(encoding="utf-8"))
        validation = json.loads((AUDIT / "validation_report.json").read_text(encoding="utf-8"))
        self.assertEqual(source_inventory["source_count"], 3)
        self.assertEqual(sampling["selected_counts"]["XSTest"], 0)
        self.assertEqual(sampling["final_manifest_created"], False)
        self.assertEqual(overlap["status"], "preliminary_blocked")
        self.assertEqual(validation["phase6b_manifest"]["created"], False)

    def test_normalized_text_is_deterministic(self):
        self.assertEqual(normalized_text("  A\u00a0B\n"), "a b")

    def test_manifest_builder_refuses_blocked_audit(self):
        blocked = {"status": "preliminary_blocked"}
        candidates = [self._candidate("XSTest", "1")]
        with self.assertRaises(ManifestBlockedError):
            build_manifest(
                candidates,
                targets={"XSTest": 1},
                seed=20260814,
                sampling_report=blocked,
                overlap_report=blocked,
                validation_report=blocked,
                approve_manifest_build=True,
            )

    def test_approved_builder_preserves_required_provenance_and_deduplicates(self):
        approved = {"status": "approved_for_manifest"}
        candidates = [
            self._candidate("XSTest", "1", "First prompt"),
            self._candidate("XSTest", "2", "Second prompt"),
        ]
        manifest = build_manifest(
            candidates,
            targets={"XSTest": 2},
            seed=20260814,
            sampling_report=approved,
            overlap_report=approved,
            validation_report=approved,
            approve_manifest_build=True,
        )
        self.assertEqual(len(manifest["records"]), 2)
        self.assertTrue(all(record["source_sample_id"] for record in manifest["records"]))
        self.assertEqual(manifest["dataset_profile"], "PILOT_EVALUATION")

    @staticmethod
    def _candidate(source, source_id, text="Prompt"):
        return {
            "source_dataset": source,
            "source_sample_id": source_id,
            "source_version": "test-0.1.0",
            "source_url": "https://example.invalid/source",
            "original_label": "safe",
            "mapped_label": "benign",
            "taxonomy_category": "B5",
            "split": "test",
            "selection_reason": "unit test",
            "license": "test",
            "redistribution_status": "metadata_only",
            "text": text,
        }


if __name__ == "__main__":
    unittest.main()
