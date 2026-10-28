"""Tests for Phase 7G quality summary derived integrity verification."""
from __future__ import annotations

import json
from pathlib import Path
import pytest

from scripts.build_phase7g_review import build_quality_summary
from scripts.check_research_integrity import (
    COMPOSITE,
    MANIFEST,
    ROOT,
    STIMULUS,
    check_integrity_flags,
)

NEEDED_FILES = [
    "results/dataset_audit/phase7e_preregistration_hash.json",
    "docs/PHASE_7D_EXPERIMENTAL_DESIGN.md",
    "docs/PHASE_7D_DESIGN_TABLE.md",
    "docs/phase7e_preregistration.md",
    "docs/phase7e_annotation_protocol.md",
    "docs/phase7e_pre_evaluation_clarification.md",
    "dataset/pilot/multiturn/stimulus_dataset_v1.json",
]


def copy_needed_files(src_root: Path, dst_root: Path) -> None:
    for rel in NEEDED_FILES:
        src = src_root / rel
        dst = dst_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())


def dummy_summary_inputs() -> tuple[dict, dict, dict]:
    qc = {
        "counts": {
            "total": 50,
            "keep": 0,
            "revise": 0,
            "reject": 0,
            "pending": 50,
            "researcher_qc_true": 0,
        }
    }
    blind = {
        "two_rater_protocol": {
            "inter_rater_status": "not_available",
            "raters_supplied": 0,
        }
    }
    recheck = {"all_pass": True, "failures": []}
    return qc, blind, recheck


def test_clean_copy_integrity_flags(tmp_path: Path):
    copy_needed_files(ROOT, tmp_path)
    flags = check_integrity_flags(tmp_path)

    # 3 mapped flags must be True
    assert flags["phase7d_design_unchanged"]["status"] is True
    assert flags["phase7d_design_unchanged"]["checked_files"] == [
        "docs/PHASE_7D_EXPERIMENTAL_DESIGN.md",
        "docs/PHASE_7D_DESIGN_TABLE.md",
    ]
    assert "sha256 matches" in flags["phase7d_design_unchanged"]["basis"]

    assert flags["phase7e_preregistration_unchanged"]["status"] is True
    assert flags["phase7e_preregistration_unchanged"]["checked_files"] == [
        "docs/phase7e_preregistration.md",
        "docs/phase7e_annotation_protocol.md",
        "docs/phase7e_pre_evaluation_clarification.md",
    ]
    assert "sha256 matches" in flags["phase7e_preregistration_unchanged"]["basis"]

    assert flags["phase7f_stimulus_v1_preserved"]["status"] is True
    assert flags["phase7f_stimulus_v1_preserved"]["checked_files"] == [
        "dataset/pilot/multiturn/stimulus_dataset_v1.json"
    ]
    assert "sha256 matches" in flags["phase7f_stimulus_v1_preserved"]["basis"]

    # 2 unmapped flags must be 'unknown'
    assert flags["public_benchmark_unchanged"]["status"] == "unknown"
    assert flags["public_benchmark_unchanged"]["checked_files"] == []
    assert isinstance(flags["public_benchmark_unchanged"]["basis"], str)

    assert flags["turkish_dataset_unchanged"]["status"] == "unknown"
    assert flags["turkish_dataset_unchanged"]["checked_files"] == []
    assert isinstance(flags["turkish_dataset_unchanged"]["basis"], str)

    # pre_review_snapshot preserved
    assert (
        flags["pre_review_snapshot"]
        == "results/dataset_audit/snapshots/phase7f_stimulus.v1.pre_qc.json"
    )


def test_build_quality_summary_uses_derived_integrity(tmp_path: Path):
    copy_needed_files(ROOT, tmp_path)
    qc, blind, recheck = dummy_summary_inputs()
    summary = build_quality_summary(qc, blind, recheck, root=tmp_path)

    integrity = summary["integrity"]
    assert integrity["phase7d_design_unchanged"]["status"] is True
    assert integrity["phase7e_preregistration_unchanged"]["status"] is True
    assert integrity["phase7f_stimulus_v1_preserved"]["status"] is True
    assert integrity["public_benchmark_unchanged"]["status"] == "unknown"
    assert integrity["turkish_dataset_unchanged"]["status"] == "unknown"


def test_change_byte_in_phase7d_design_table(tmp_path: Path):
    copy_needed_files(ROOT, tmp_path)

    # Change one byte in PHASE_7D_DESIGN_TABLE.md
    target = tmp_path / "docs/PHASE_7D_DESIGN_TABLE.md"
    orig = target.read_bytes()
    # Flip one byte
    flipped = bytes([orig[0] ^ 0x01]) + orig[1:]
    target.write_bytes(flipped)

    flags = check_integrity_flags(tmp_path)
    assert flags["phase7d_design_unchanged"]["status"] is False

    # Others must be completely unaffected
    assert flags["phase7e_preregistration_unchanged"]["status"] is True
    assert flags["phase7f_stimulus_v1_preserved"]["status"] is True
    assert flags["public_benchmark_unchanged"]["status"] == "unknown"
    assert flags["turkish_dataset_unchanged"]["status"] == "unknown"


def test_delete_copied_stimulus_file(tmp_path: Path):
    copy_needed_files(ROOT, tmp_path)

    stimulus = tmp_path / "dataset/pilot/multiturn/stimulus_dataset_v1.json"
    stimulus.unlink()

    flags = check_integrity_flags(tmp_path)
    assert flags["phase7f_stimulus_v1_preserved"]["status"] is False
    assert flags["phase7f_stimulus_v1_preserved"]["checked_files"] == [
        "dataset/pilot/multiturn/stimulus_dataset_v1.json"
    ]
    # Others unaffected
    assert flags["phase7d_design_unchanged"]["status"] is True
    assert flags["phase7e_preregistration_unchanged"]["status"] is True
    assert flags["public_benchmark_unchanged"]["status"] == "unknown"
    assert flags["turkish_dataset_unchanged"]["status"] == "unknown"


def test_summary_never_contains_literal_true_for_empty_checked_files(tmp_path: Path):
    copy_needed_files(ROOT, tmp_path)
    qc, blind, recheck = dummy_summary_inputs()
    summary = build_quality_summary(qc, blind, recheck, root=tmp_path)

    for key, val in summary["integrity"].items():
        if key == "pre_review_snapshot":
            continue
        assert isinstance(val, dict), f"{key} should be an object"
        assert "status" in val and "checked_files" in val and "basis" in val
        if len(val["checked_files"]) == 0:
            assert val["status"] is not True
            assert val["status"] != "true"
            assert val["status"] == "unknown"


def test_missing_manifest_fails_closed(tmp_path: Path):
    # Copy files except the manifest
    copy_needed_files(ROOT, tmp_path)
    manifest = tmp_path / "results/dataset_audit/phase7e_preregistration_hash.json"
    manifest.unlink()

    flags = check_integrity_flags(tmp_path)
    assert flags["phase7d_design_unchanged"]["status"] is False
    assert flags["phase7e_preregistration_unchanged"]["status"] is False
    # Stimulus pin does not need the manifest
    assert flags["phase7f_stimulus_v1_preserved"]["status"] is True


def test_tampered_manifest_fails_closed(tmp_path: Path):
    copy_needed_files(ROOT, tmp_path)
    manifest = tmp_path / "results/dataset_audit/phase7e_preregistration_hash.json"
    # Modify manifest content so its sha256 no longer matches MANIFEST
    manifest.write_bytes(manifest.read_bytes() + b" ")

    flags = check_integrity_flags(tmp_path)
    assert flags["phase7d_design_unchanged"]["status"] is False
    assert flags["phase7e_preregistration_unchanged"]["status"] is False


def test_change_phase7e_file_affects_only_phase7e(tmp_path: Path):
    copy_needed_files(ROOT, tmp_path)
    target = tmp_path / "docs/phase7e_preregistration.md"
    orig = target.read_bytes()
    target.write_bytes(orig + b"\n")

    flags = check_integrity_flags(tmp_path)
    assert flags["phase7e_preregistration_unchanged"]["status"] is False
    assert flags["phase7d_design_unchanged"]["status"] is True
    assert flags["phase7f_stimulus_v1_preserved"]["status"] is True


def test_output_is_deterministic(tmp_path: Path):
    copy_needed_files(ROOT, tmp_path)
    qc, blind, recheck = dummy_summary_inputs()
    summary1 = build_quality_summary(qc, blind, recheck, root=tmp_path)
    summary2 = build_quality_summary(qc, blind, recheck, root=tmp_path)

    assert json.dumps(summary1["integrity"], sort_keys=True) == json.dumps(
        summary2["integrity"], sort_keys=True
    )
