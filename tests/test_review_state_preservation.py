"""Tests for review bootstrap state preservation and history replay (issue #11).

Ensures:
1. build_phase7e_review and build_phase7g_review refuse to overwrite existing
   canonical review records by default (exit code 2).
2. --reinit requires --backup-dir, backs up existing files with MANIFEST.json,
   verifies copy hashes, and appends a review_reinitialised event to history.
3. Validators for Phase 7E and Phase 7G replay history sequentially from PENDING,
   verifying previous_decision and matching final state.
4. Phase 7G validator fails when the history file is missing.

All test fixtures use synthetic data in tmp_path only.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_phase7e_review  # noqa: E402
import build_phase7g_review  # noqa: E402
import validate_phase7e_review  # noqa: E402
import validate_phase7g_review  # noqa: E402


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_builder(builder_module, args: list[str]) -> int:
    """Run builder main() with args and catch SystemExit."""
    try:
        ret = builder_module.main(args)
        return 0 if ret is None else ret
    except SystemExit as exc:
        code = exc.code
        return 0 if code is None else int(code)


# ---------------------------------------------------------------------------
# Phase 7E Builder Tests
# ---------------------------------------------------------------------------


def test_phase7e_builder_out_dir_empty_dir_succeeds(tmp_path: Path):
    out_dir = tmp_path / "target"
    code = run_builder(build_phase7e_review, ["--out-dir", str(out_dir)])
    assert code == 0

    review_file = out_dir / "results" / "dataset_audit" / "phase7e_review.json"
    table_file = out_dir / "docs" / "PHASE_7D_DESIGN_TABLE.md"
    assert review_file.is_file()
    assert table_file.is_file()

    review_data = json.loads(review_file.read_text(encoding="utf-8"))
    assert review_data["counts"]["total"] == 50
    assert review_data["counts"]["pending"] == 50
    assert all(item["review_decision"] == "PENDING" for item in review_data["items"])


def test_phase7e_builder_refuses_overwrite(tmp_path: Path, capsys):
    out_dir = tmp_path / "target"
    code1 = run_builder(build_phase7e_review, ["--out-dir", str(out_dir)])
    assert code1 == 0

    review_file = out_dir / "results" / "dataset_audit" / "phase7e_review.json"
    table_file = out_dir / "docs" / "PHASE_7D_DESIGN_TABLE.md"
    hash_rev_before = sha256_file(review_file)
    hash_tbl_before = sha256_file(table_file)

    # Second run without --reinit must refuse (exit code 2)
    code2 = run_builder(build_phase7e_review, ["--out-dir", str(out_dir)])
    assert code2 == 2

    # Check stderr mentioned existing files
    captured = capsys.readouterr()
    assert str(review_file) in captured.err or "phase7e_review.json" in captured.err

    # Check files are byte-identical
    assert sha256_file(review_file) == hash_rev_before
    assert sha256_file(table_file) == hash_tbl_before


def test_phase7e_builder_reinit_without_backup_dir_fails(tmp_path: Path):
    out_dir = tmp_path / "target"
    code1 = run_builder(build_phase7e_review, ["--out-dir", str(out_dir)])
    assert code1 == 0

    # --reinit without --backup-dir is a usage error (exit code 2)
    code2 = run_builder(build_phase7e_review, ["--out-dir", str(out_dir), "--reinit"])
    assert code2 == 2


def test_phase7e_builder_reinit_with_backup_dir(tmp_path: Path):
    out_dir = tmp_path / "target"
    code1 = run_builder(build_phase7e_review, ["--out-dir", str(out_dir)])
    assert code1 == 0

    review_file = out_dir / "results" / "dataset_audit" / "phase7e_review.json"
    table_file = out_dir / "docs" / "PHASE_7D_DESIGN_TABLE.md"
    history_file = out_dir / "results" / "dataset_audit" / "phase7e_review_history.jsonl"

    # Seed history file with an initial event
    init_event = {
        "event": "review_log_initialised",
        "phase": "7E",
        "timestamp": "2026-08-14T00:00:00Z",
        "item_count": 50,
        "initial_decision_for_all_items": "PENDING",
    }
    history_file.parent.mkdir(parents=True, exist_ok=True)
    history_file.write_text(json.dumps(init_event) + "\n", encoding="utf-8")

    orig_rev_hash = sha256_file(review_file)
    orig_tbl_hash = sha256_file(table_file)
    orig_hist_hash = sha256_file(history_file)
    orig_hist_lines = history_file.read_text(encoding="utf-8").splitlines()

    backup_dir = tmp_path / "backups"
    code2 = run_builder(
        build_phase7e_review,
        ["--out-dir", str(out_dir), "--reinit", "--backup-dir", str(backup_dir)],
    )
    assert code2 == 0

    # Backup directory must contain a timestamp directory
    backup_subdirs = [d for d in backup_dir.iterdir() if d.is_dir()]
    assert len(backup_subdirs) == 1
    ts_backup_dir = backup_subdirs[0]

    # Verify backup contents
    manifest_path = ts_backup_dir / "MANIFEST.json"
    assert manifest_path.is_file()
    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_hash = sha256_file(manifest_path)

    assert (ts_backup_dir / review_file.name).is_file()
    assert (ts_backup_dir / table_file.name).is_file()
    assert (ts_backup_dir / history_file.name).is_file()
    assert sha256_file(ts_backup_dir / review_file.name) == orig_rev_hash
    assert sha256_file(ts_backup_dir / table_file.name) == orig_tbl_hash
    assert sha256_file(ts_backup_dir / history_file.name) == orig_hist_hash

    # Verify history file grew by exactly one line
    new_hist_lines = history_file.read_text(encoding="utf-8").splitlines()
    assert len(new_hist_lines) == len(orig_hist_lines) + 1
    assert new_hist_lines[:-1] == orig_hist_lines

    reinit_event = json.loads(new_hist_lines[-1])
    assert reinit_event["event"] == "review_reinitialised"
    assert reinit_event["phase"] == "7E"
    assert "timestamp" in reinit_event
    assert Path(reinit_event["backup_dir"]).resolve() == ts_backup_dir.resolve()
    assert reinit_event["manifest_sha256"] == manifest_hash


# ---------------------------------------------------------------------------
# Phase 7G Builder Tests
# ---------------------------------------------------------------------------


def test_phase7g_builder_out_dir_empty_dir_succeeds(tmp_path: Path):
    out_dir = tmp_path / "target"
    code = run_builder(build_phase7g_review, ["--out-dir", str(out_dir)])
    assert code == 0

    audit_dir = out_dir / "results" / "dataset_audit"
    assert (audit_dir / "phase7g_blind_review.json").is_file()
    assert (audit_dir / "phase7g_blind_key.json").is_file()
    assert (audit_dir / "phase7g_human_qc.json").is_file()
    assert (audit_dir / "phase7g_quality_summary.json").is_file()
    assert (audit_dir / "phase7g_review_history.jsonl").is_file()


def test_phase7g_builder_refuses_overwrite(tmp_path: Path, capsys):
    out_dir = tmp_path / "target"
    code1 = run_builder(build_phase7g_review, ["--out-dir", str(out_dir)])
    assert code1 == 0

    audit_dir = out_dir / "results" / "dataset_audit"
    canonical_files = [
        audit_dir / "phase7g_blind_review.json",
        audit_dir / "phase7g_blind_key.json",
        audit_dir / "phase7g_human_qc.json",
        audit_dir / "phase7g_quality_summary.json",
    ]
    hashes_before = {f: sha256_file(f) for f in canonical_files}

    # Second run without --reinit must refuse (exit code 2)
    code2 = run_builder(build_phase7g_review, ["--out-dir", str(out_dir)])
    assert code2 == 2

    captured = capsys.readouterr()
    assert "phase7g_human_qc.json" in captured.err

    # Check files are byte-identical
    for f in canonical_files:
        assert sha256_file(f) == hashes_before[f]


def test_phase7g_builder_reinit_without_backup_dir_fails(tmp_path: Path):
    out_dir = tmp_path / "target"
    code1 = run_builder(build_phase7g_review, ["--out-dir", str(out_dir)])
    assert code1 == 0

    code2 = run_builder(build_phase7g_review, ["--out-dir", str(out_dir), "--reinit"])
    assert code2 == 2


def test_phase7g_builder_reinit_with_backup_dir(tmp_path: Path):
    out_dir = tmp_path / "target"
    code1 = run_builder(build_phase7g_review, ["--out-dir", str(out_dir)])
    assert code1 == 0

    audit_dir = out_dir / "results" / "dataset_audit"
    history_file = audit_dir / "phase7g_review_history.jsonl"
    canonical_files = [
        audit_dir / "phase7g_blind_review.json",
        audit_dir / "phase7g_blind_key.json",
        audit_dir / "phase7g_human_qc.json",
        audit_dir / "phase7g_quality_summary.json",
    ]
    hashes_before = {f: sha256_file(f) for f in canonical_files}
    hist_hash_before = sha256_file(history_file)
    hist_lines_before = history_file.read_text(encoding="utf-8").splitlines()

    backup_dir = tmp_path / "backups"
    code2 = run_builder(
        build_phase7g_review,
        ["--out-dir", str(out_dir), "--reinit", "--backup-dir", str(backup_dir)],
    )
    assert code2 == 0

    backup_subdirs = [d for d in backup_dir.iterdir() if d.is_dir()]
    assert len(backup_subdirs) == 1
    ts_backup_dir = backup_subdirs[0]

    manifest_path = ts_backup_dir / "MANIFEST.json"
    assert manifest_path.is_file()
    manifest_hash = sha256_file(manifest_path)

    for f in canonical_files:
        backed_f = ts_backup_dir / f.name
        assert backed_f.is_file()
        assert sha256_file(backed_f) == hashes_before[f]

    assert (ts_backup_dir / history_file.name).is_file()
    assert sha256_file(ts_backup_dir / history_file.name) == hist_hash_before

    new_hist_lines = history_file.read_text(encoding="utf-8").splitlines()
    assert len(new_hist_lines) == len(hist_lines_before) + 1
    assert new_hist_lines[:-1] == hist_lines_before

    reinit_event = json.loads(new_hist_lines[-1])
    assert reinit_event["event"] == "review_reinitialised"
    assert reinit_event["phase"] == "7G"
    assert "timestamp" in reinit_event
    assert Path(reinit_event["backup_dir"]).resolve() == ts_backup_dir.resolve()
    assert reinit_event["manifest_sha256"] == manifest_hash


# ---------------------------------------------------------------------------
# Phase 7E Validator History Replay Tests (Synthetic Data Only)
# ---------------------------------------------------------------------------


def make_synthetic_7e_record():
    return {
        "items": [
            {"research_item_id": "SYN-001", "review_decision": "KEEP"},
            {"research_item_id": "SYN-002", "review_decision": "PENDING"},
        ]
    }


def test_phase7e_validator_replay_consistent_synthetic_history():
    record = make_synthetic_7e_record()
    history = [
        json.dumps({
            "event": "review_log_initialised",
            "phase": "7E",
            "timestamp": "2026-08-14T00:00:00Z",
            "item_count": 2,
        }),
        json.dumps({
            "event": "review_decision",
            "research_item_id": "SYN-001",
            "previous_decision": "PENDING",
            "new_decision": "KEEP",
            "reviewer_role": "reviewer",
            "timestamp": "2026-08-14T10:00:00Z",
            "version": 1,
        }),
    ]
    errors = validate_phase7e_review.validate_history(history, record)
    assert errors == []


def test_phase7e_validator_replay_drift_keep_vs_revise_fails():
    record = make_synthetic_7e_record()  # SYN-001 has KEEP in record
    history = [
        json.dumps({
            "event": "review_log_initialised",
            "phase": "7E",
            "timestamp": "2026-08-14T00:00:00Z",
        }),
        json.dumps({
            "event": "review_decision",
            "research_item_id": "SYN-001",
            "previous_decision": "PENDING",
            "new_decision": "REVISE",
            "reviewer_role": "reviewer",
            "timestamp": "2026-08-14T10:00:00Z",
            "version": 1,
        }),
    ]
    errors = validate_phase7e_review.validate_history(history, record)
    assert any("SYN-001" in e and "REVISE" in e and "KEEP" in e for e in errors)


def test_phase7e_validator_replay_drift_pending_vs_keep_fails():
    # Issue #11 scenario: record reset to PENDING while history says KEEP
    record = {
        "items": [
            {"research_item_id": "SYN-001", "review_decision": "PENDING"},
        ]
    }
    history = [
        json.dumps({
            "event": "review_log_initialised",
            "phase": "7E",
            "timestamp": "2026-08-14T00:00:00Z",
        }),
        json.dumps({
            "event": "review_decision",
            "research_item_id": "SYN-001",
            "previous_decision": "PENDING",
            "new_decision": "KEEP",
            "reviewer_role": "reviewer",
            "timestamp": "2026-08-14T10:00:00Z",
            "version": 1,
        }),
    ]
    errors = validate_phase7e_review.validate_history(history, record)
    assert any("SYN-001" in e and "PENDING" in e and "KEEP" in e for e in errors)


def test_phase7e_validator_replay_previous_decision_mismatch_fails():
    record = make_synthetic_7e_record()
    history = [
        json.dumps({
            "event": "review_log_initialised",
            "phase": "7E",
            "timestamp": "2026-08-14T00:00:00Z",
        }),
        json.dumps({
            "event": "review_decision",
            "research_item_id": "SYN-001",
            "previous_decision": "REVISE",  # State is actually PENDING!
            "new_decision": "KEEP",
            "reviewer_role": "reviewer",
            "timestamp": "2026-08-14T10:00:00Z",
            "version": 1,
        }),
    ]
    errors = validate_phase7e_review.validate_history(history, record)
    # Must report error naming line 2
    assert any("line 2" in e and "previous_decision" in e for e in errors)


# ---------------------------------------------------------------------------
# Phase 7G Validator History Replay Tests (Synthetic Data Only)
# ---------------------------------------------------------------------------


def make_synthetic_7g_qc():
    return {
        "items": [
            {"research_item_id": "SYN-001", "review_decision": "KEEP"},
            {"research_item_id": "SYN-002", "review_decision": "PENDING"},
        ]
    }


def test_phase7g_validator_replay_consistent_synthetic_history():
    qc = make_synthetic_7g_qc()
    history = [
        json.dumps({
            "event": "qc_log_initialised",
            "phase": "7G",
            "timestamp": "2026-08-14T16:00:00Z",
        }),
        json.dumps({
            "event": "blind_annotation",
            "blind_id": "BLIND-SYN-1",
            "rater": "rater_a",
            "valence": "probably_benign",
        }),
        json.dumps({
            "event": "review_decision",
            "research_item_id": "SYN-001",
            "previous_decision": "PENDING",
            "new_decision": "KEEP",
            "timestamp": "2026-08-14T20:00:00Z",
        }),
    ]
    errors = validate_phase7g_review.validate_history(history, qc)
    assert errors == []


def test_phase7g_validator_replay_drift_keep_vs_revise_fails():
    qc = make_synthetic_7g_qc()  # SYN-001 has KEEP
    history = [
        json.dumps({
            "event": "qc_log_initialised",
            "phase": "7G",
            "timestamp": "2026-08-14T16:00:00Z",
        }),
        json.dumps({
            "event": "review_decision",
            "research_item_id": "SYN-001",
            "previous_decision": "PENDING",
            "new_decision": "REVISE",
            "timestamp": "2026-08-14T20:00:00Z",
        }),
    ]
    errors = validate_phase7g_review.validate_history(history, qc)
    assert any("SYN-001" in e and "REVISE" in e and "KEEP" in e for e in errors)


def test_phase7g_validator_replay_drift_pending_vs_keep_fails():
    # Issue #11 scenario for 7G
    qc = {
        "items": [
            {"research_item_id": "SYN-001", "review_decision": "PENDING"},
        ]
    }
    history = [
        json.dumps({
            "event": "qc_log_initialised",
            "phase": "7G",
            "timestamp": "2026-08-14T16:00:00Z",
        }),
        json.dumps({
            "event": "review_decision",
            "research_item_id": "SYN-001",
            "previous_decision": "PENDING",
            "new_decision": "KEEP",
            "timestamp": "2026-08-14T20:00:00Z",
        }),
    ]
    errors = validate_phase7g_review.validate_history(history, qc)
    assert any("SYN-001" in e and "PENDING" in e and "KEEP" in e for e in errors)


def test_phase7g_validator_replay_previous_decision_mismatch_fails():
    qc = make_synthetic_7g_qc()
    history = [
        json.dumps({
            "event": "qc_log_initialised",
            "phase": "7G",
            "timestamp": "2026-08-14T16:00:00Z",
        }),
        json.dumps({
            "event": "review_decision",
            "research_item_id": "SYN-001",
            "previous_decision": "REVISE",  # Item is at PENDING!
            "new_decision": "KEEP",
            "timestamp": "2026-08-14T20:00:00Z",
        }),
    ]
    errors = validate_phase7g_review.validate_history(history, qc)
    assert any("line 2" in e and "previous_decision" in e for e in errors)


def test_phase7g_validator_other_events_skipped():
    qc = {
        "items": [
            {"research_item_id": "SYN-001", "review_decision": "PENDING"},
        ]
    }
    history = [
        json.dumps({"event": "qc_log_initialised"}),
        json.dumps({"event": "blind_annotation", "blind_id": "B-1"}),
        json.dumps({"event": "blind_adjudication", "blind_id": "B-1"}),
        json.dumps({"event": "context_review", "research_item_id": "SYN-001"}),
        json.dumps({"event": "review_session_invalidated", "blind_id": "B-1"}),
        json.dumps({"event": "review_reinitialised", "phase": "7G"}),
    ]
    errors = validate_phase7g_review.validate_history(history, qc)
    assert errors == []


def test_phase7g_validator_missing_history_file_fails(tmp_path: Path, monkeypatch, capsys):
    fake_target = tmp_path / "fake_target"
    # Build a fresh set of records into fake_target
    code_build = run_builder(build_phase7g_review, ["--out-dir", str(fake_target)])
    # On e9cc110, builder fails to run; but once builder is implemented, it creates outputs
    audit_dir = fake_target / "results" / "dataset_audit"

    # If the history file was created, remove it to simulate a missing history file
    history_file = audit_dir / "phase7g_review_history.jsonl"
    if history_file.is_file():
        history_file.unlink()

    monkeypatch.setattr(validate_phase7g_review, "AUDIT", audit_dir)

    code = validate_phase7g_review.main()
    assert code == 1

    captured = capsys.readouterr()
    assert "phase7g_review_history.jsonl" in captured.out or "INVALID" in captured.out
