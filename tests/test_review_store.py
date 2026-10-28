"""Tests for atomic review store and state/history update recovery (issue #17).

Ensures:
1. Normal commit replaces state atomically, appends history, and preserves pre-call bytes.
2. History append failure rolls back both history (to original size) and state (from snapshot).
3. Partial history append truncates history back to exactly pre-call bytes and restores state.
4. Review lock is exclusive, non-blocking, portable, and removed on success and failure.
5. Snapshot overwrite is refused.
6. Byte identity between atomic state write and existing json formatting.
7. End-to-end writer integration with lock enforcement, --dry-run, and real commits.
"""

from __future__ import annotations

import io
import json
from pathlib import Path
import pytest

from scripts.review_store import (
    HistoryAppendError,
    ReviewLockError,
    SnapshotExistsError,
    commit_state_and_history,
    review_lock,
)
import scripts.apply_phase7e_decisions as p7e
import scripts.apply_phase7g_annotations as p7g


# ---------------------------------------------------------------------------
# Helpers & Fixtures
# ---------------------------------------------------------------------------


def _make_sample_state() -> dict:
    return {
        "status": "REVIEW_IN_PROGRESS",
        "counts": {"total": 2, "pending": 1, "keep": 1, "revise": 0, "reject": 0},
        "items": [
            {"research_item_id": "RI-NB-001", "decision": "KEEP", "notes": "Türkçe test"},
            {"research_item_id": "RI-NB-002", "decision": "PENDING", "notes": None},
        ],
    }


def _make_sample_events() -> list[dict]:
    return [
        {
            "event": "review_decision",
            "research_item_id": "RI-NB-001",
            "decision": "KEEP",
            "reviewer_id": "test_rev",
            "timestamp": "2026-08-14T12:00:00Z",
        }
    ]


# ---------------------------------------------------------------------------
# Unit Tests: review_store primitives
# ---------------------------------------------------------------------------


def test_atomic_write_byte_identity(tmp_path: Path):
    """Atomic write produces bytes identical to existing formatting."""
    state_path = tmp_path / "state.json"
    history_path = tmp_path / "history.jsonl"
    snap_path = tmp_path / "snap.json"

    initial_state = {"initial": True}
    state_path.write_text(
        json.dumps(initial_state, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    new_state = _make_sample_state()
    expected_bytes = (
        json.dumps(new_state, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")

    commit_state_and_history(state_path, new_state, history_path, _make_events := [], snap_path)

    actual_bytes = state_path.read_bytes()
    assert actual_bytes == expected_bytes


def test_normal_commit_preserves_prefix_and_replaces_state(tmp_path: Path):
    """State is replaced, history grows by exact new lines, old history is unchanged prefix."""
    state_path = tmp_path / "state.json"
    history_path = tmp_path / "history.jsonl"
    snap_path = tmp_path / "snapshots" / "state.snap.json"

    initial_state = {"version": 1, "items": []}
    old_state_bytes = (
        json.dumps(initial_state, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    state_path.write_bytes(old_state_bytes)

    initial_event = {"event": "init", "ts": "2026-08-14T00:00:00Z"}
    old_history_bytes = (
        json.dumps(initial_event, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    history_path.write_bytes(old_history_bytes)

    new_state = _make_sample_state()
    new_events = _make_sample_events()

    commit_state_and_history(state_path, new_state, history_path, new_events, snap_path)

    # 1. Snapshot holds old state bytes
    assert snap_path.is_file()
    assert snap_path.read_bytes() == old_state_bytes

    # 2. State holds new state bytes
    expected_state_bytes = (
        json.dumps(new_state, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    assert state_path.read_bytes() == expected_state_bytes

    # 3. History prefix matches exactly, new suffix matches new events
    current_history_bytes = history_path.read_bytes()
    assert current_history_bytes.startswith(old_history_bytes)

    appended_bytes = current_history_bytes[len(old_history_bytes):]
    expected_appended_bytes = "".join(
        json.dumps(e, ensure_ascii=False) + "\n" for e in new_events
    ).encode("utf-8")
    assert appended_bytes == expected_appended_bytes


def test_history_append_fails_rolls_back_state_and_history(tmp_path: Path, monkeypatch):
    """When history append fails, state is restored from snapshot and history is unchanged."""
    state_path = tmp_path / "state.json"
    history_path = tmp_path / "history.jsonl"
    snap_path = tmp_path / "snapshots" / "state.snap.json"

    initial_state = {"state": "initial_before_call"}
    old_state_bytes = (
        json.dumps(initial_state, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    state_path.write_bytes(old_state_bytes)

    old_history_bytes = b'{"event":"initial_history_line"}\n'
    history_path.write_bytes(old_history_bytes)

    new_state = {"state": "updated_should_be_rolled_back"}
    new_events = [{"event": "will_fail"}]

    real_open = open

    def failing_open(file, mode="r", *args, **kwargs):
        if Path(file) == history_path and "a" in mode:
            raise IOError("Simulated disk error opening history for append")
        return real_open(file, mode, *args, **kwargs)

    monkeypatch.setattr("builtins.open", failing_open)

    with pytest.raises(HistoryAppendError) as exc_info:
        commit_state_and_history(state_path, new_state, history_path, new_events, snap_path)

    assert "rolled back" in str(exc_info.value)
    assert "truncated" in str(exc_info.value)

    # State bytes must equal pre-call bytes
    assert state_path.read_bytes() == old_state_bytes
    # History bytes must equal pre-call bytes
    assert history_path.read_bytes() == old_history_bytes


def test_partial_append_truncates_history_to_original_bytes(tmp_path: Path, monkeypatch):
    """When history write partially succeeds before raising, history is truncated to exact original bytes."""
    state_path = tmp_path / "state.json"
    history_path = tmp_path / "history.jsonl"
    snap_path = tmp_path / "snapshots" / "state.snap.json"

    initial_state = {"state": "clean_state"}
    old_state_bytes = (
        json.dumps(initial_state, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    state_path.write_bytes(old_state_bytes)

    old_history_bytes = b'{"event":"line1"}\n{"event":"line2"}\n'
    history_path.write_bytes(old_history_bytes)

    new_state = {"state": "new_state_partial_fail"}
    new_events = [{"event": "partial_event_1"}, {"event": "partial_event_2"}]

    real_open = open

    class PartialWriteFile:
        def __init__(self, raw_fh):
            self._raw = raw_fh

        def write(self, b):
            # Write only first 10 bytes then raise
            self._raw.write(b[:10])
            self._raw.flush()
            raise IOError("Simulated disk full mid-write")

        def flush(self):
            self._raw.flush()

        def fileno(self):
            return self._raw.fileno()

        def close(self):
            self._raw.close()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.close()

    def partial_open(file, mode="r", *args, **kwargs):
        fh = real_open(file, mode, *args, **kwargs)
        if Path(file) == history_path and "a" in mode:
            return PartialWriteFile(fh)
        return fh

    monkeypatch.setattr("builtins.open", partial_open)

    with pytest.raises(HistoryAppendError) as exc_info:
        commit_state_and_history(state_path, new_state, history_path, new_events, snap_path)

    assert "rolled back" in str(exc_info.value)

    # History bytes must equal pre-call bytes exactly (partial 10 bytes truncated away)
    assert history_path.read_bytes() == old_history_bytes
    # State restored to pre-call bytes
    assert state_path.read_bytes() == old_state_bytes


def test_lock_held_raises_and_preserves_state(tmp_path: Path):
    """When lock file already exists, review_lock raises ReviewLockError and leaves paths unchanged."""
    audit_dir = tmp_path / "audit"
    audit_dir.mkdir(parents=True)
    lock_file = audit_dir / ".review.lock"
    lock_file.write_text("99999\n", encoding="utf-8")

    state_path = audit_dir / "state.json"
    state_path.write_text('{"untouched": true}\n', encoding="utf-8")
    before_state = state_path.read_bytes()

    with pytest.raises(ReviewLockError) as exc_info:
        with review_lock(audit_dir):
            pytest.fail("Should not acquire held lock")

    assert ".review.lock" in str(exc_info.value)
    assert "another writer" in str(exc_info.value)

    # Lock file must still exist and was not deleted by the failed acquisition attempt
    assert lock_file.is_file()
    assert lock_file.read_text(encoding="utf-8") == "99999\n"

    # State file untouched
    assert state_path.read_bytes() == before_state


def test_lock_file_removed_after_both_success_and_failure(tmp_path: Path):
    """Lock file exists during context manager and is unlinked on normal exit or exception."""
    audit_dir = tmp_path / "audit"
    lock_file = audit_dir / ".review.lock"

    # 1. Normal exit
    with review_lock(audit_dir):
        assert lock_file.is_file()
    assert not lock_file.exists()

    # 2. Exception exit
    with pytest.raises(RuntimeError):
        with review_lock(audit_dir):
            assert lock_file.is_file()
            raise RuntimeError("something failed inside lock")
    assert not lock_file.exists()


def test_refuse_snapshot_overwrite(tmp_path: Path):
    """Refuse to overwrite an existing snapshot file."""
    state_path = tmp_path / "state.json"
    history_path = tmp_path / "history.jsonl"
    snap_path = tmp_path / "snap.json"

    state_path.write_text('{"state": 1}\n', encoding="utf-8")
    snap_path.write_text('{"prior_snap": true}\n', encoding="utf-8")

    with pytest.raises(SnapshotExistsError):
        commit_state_and_history(state_path, {"state": 2}, history_path, [], snap_path)

    # Prior snapshot and state are untouched
    assert snap_path.read_text(encoding="utf-8") == '{"prior_snap": true}\n'
    assert state_path.read_text(encoding="utf-8") == '{"state": 1}\n'


# ---------------------------------------------------------------------------
# End-to-End Writer Tests (with patched synthetic paths in tmp_path)
# ---------------------------------------------------------------------------


def test_phase7e_writer_end_to_end(tmp_path: Path):
    """Phase 7E writer end-to-end: lock enforcement, dry-run, and real commit."""
    audit_dir = tmp_path / "results" / "dataset_audit"
    audit_dir.mkdir(parents=True)
    snap_dir = audit_dir / "snapshots"

    review_file = audit_dir / "phase7e_review.json"
    history_file = audit_dir / "phase7e_review_history.jsonl"

    design = {
        "research_item_id": "RI-NB-001",
        "triplet_id": "TRP-NB-001",
        "category": "null_benign",
        "context_mechanism": "secure logging",
        "canonical_final_prompt_intent": "checklist",
        "isolated_prompt_target_valence": "clearly_benign",
        "legitimating_context_intent": "benign",
        "incriminating_context_intent": "framing",
        "expected_context_effect": "context_has_no_material_effect",
        "expected_risk_profile": "low",
        "intended_turn_count": 3,
        "control_strategy": "F",
        "safety_constraints": "none",
    }
    initial_record = {
        "status": "AWAITING_HUMAN_REVIEW",
        "review_complete": False,
        "counts": {"total": 1, "pending": 1, "keep": 0, "revise": 0, "reject": 0, "approved": 0},
        "items": [
            {
                "research_item_id": "RI-NB-001",
                "current_version": 1,
                "review_decision": "PENDING",
                "researcher_approved": False,
                "notes": None,
                "versions": [{"version": 1, "source_phase": "7D", "design": design}],
                "decision_rule_checklist": {
                    "represents_intended_construct": False,
                    "final_prompt_can_be_made_ambiguous": False,
                    "bc_differ_semantically_not_by_length": False,
                    "realistic_user_workflow": False,
                    "context_effect_defensible_pre_model": False,
                    "safe_for_controlled_research": False,
                    "not_redundant_with_another_item": False,
                    "control_strategy_appropriate": False,
                },
            }
        ],
        "reviewer_registry": [],
    }
    review_file.write_text(json.dumps(initial_record, indent=2) + "\n", encoding="utf-8")
    history_file.write_text(json.dumps({"event": "review_log_initialised"}) + "\n", encoding="utf-8")

    dec_file = tmp_path / "decisions.txt"
    dec_file.write_text("RI-NB-001: KEEP\n", encoding="utf-8")

    ts = "2026-08-14T12:00:00Z"
    args = [
        "--decisions", str(dec_file),
        "--reviewer-id", "researcher_kaan",
        "--reviewer-role", "lead",
        "--timestamp", ts,
    ]

    # Test 1: Lock enforcement (fails on master if master does not lock!)
    lock_file = audit_dir / ".review.lock"
    lock_file.write_text("88888\n", encoding="utf-8")
    with pytest.raises(ReviewLockError):
        p7e.main(args, root=tmp_path)
    lock_file.unlink()

    # Test 2: Dry-run
    ret_dry = p7e.main(args + ["--dry-run"], root=tmp_path)
    assert ret_dry == 0
    # Nothing changed
    assert json.loads(review_file.read_text(encoding="utf-8"))["counts"]["keep"] == 0
    assert len(list(snap_dir.glob("*.json"))) == 0

    # Test 3: Real run
    ret_real = p7e.main(args, root=tmp_path)
    assert ret_real == 0

    # Verify state updated
    updated = json.loads(review_file.read_text(encoding="utf-8"))
    assert updated["counts"]["keep"] == 1
    assert updated["items"][0]["review_decision"] == "KEEP"

    # Verify snapshot exists
    clean_ts = ts.replace(":", "")
    expected_snap = snap_dir / f"phase7e_review.{clean_ts}.json"
    assert expected_snap.is_file()

    # Verify history appended
    lines = history_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    last_event = json.loads(lines[-1])
    assert last_event["event"] == "review_decision"
    assert last_event["research_item_id"] == "RI-NB-001"
    assert last_event["new_decision"] == "KEEP"

    # Verify lock cleaned up
    assert not lock_file.exists()


def test_phase7g_writer_end_to_end(tmp_path: Path, monkeypatch):
    """Phase 7G writer end-to-end: lock enforcement, dry-run, and real commit."""
    audit_dir = tmp_path / "audit"
    snap_dir = audit_dir / "snapshots"
    audit_dir.mkdir(parents=True)
    snap_dir.mkdir(parents=True)

    blind_file = audit_dir / "phase7g_blind_review.json"
    key_file = audit_dir / "phase7g_blind_key.json"
    qc_file = audit_dir / "phase7g_human_qc.json"
    history_file = audit_dir / "phase7g_review_history.jsonl"

    blind_file.write_text(json.dumps({
        "status": "IN_PROGRESS",
        "two_rater_protocol": {
            "raters_supported": 2,
            "raters_supplied": 0,
            "inter_rater_status": "not_available",
            "percent_agreement": None,
            "cohens_kappa": None,
            "n_double_annotated": 0,
        },
        "items": [
            {
                "blind_id": "B-001",
                "canonical_final_prompt": "test prompt",
                "rater_a": {
                    "reviewer_id": None,
                    "reviewer_role": None,
                    "isolated_prompt_valence_observed": None,
                    "reviewer_confidence": None,
                    "reviewer_notes": None,
                    "annotated_at": None,
                },
                "rater_b": {
                    "reviewer_id": None,
                    "reviewer_role": None,
                    "isolated_prompt_valence_observed": None,
                    "reviewer_confidence": None,
                    "reviewer_notes": None,
                    "annotated_at": None,
                },
                "adjudicated_valence": None,
                "adjudication_rationale": None,
                "annotation_status": "PENDING",
                "gate_result": None,
                "gate_flag": None,
            }
        ]
    }, indent=2) + "\n", encoding="utf-8")

    key_file.write_text(json.dumps({
        "mapping": [
            {"blind_id": "B-001", "research_item_id": "RI-NB-001", "category": "null_benign"}
        ]
    }, indent=2) + "\n", encoding="utf-8")

    qc_file.write_text(json.dumps({"items": []}, indent=2) + "\n", encoding="utf-8")
    history_file.write_text(json.dumps({"event": "init"}) + "\n", encoding="utf-8")

    # Patch module constants
    monkeypatch.setattr(p7g, "AUDIT", audit_dir)
    monkeypatch.setattr(p7g, "BLIND", blind_file)
    monkeypatch.setattr(p7g, "KEY", key_file)
    monkeypatch.setattr(p7g, "QC", qc_file)
    monkeypatch.setattr(p7g, "HISTORY", history_file)
    monkeypatch.setattr(p7g, "SNAPS", snap_dir)

    payload_file = tmp_path / "input.json"
    payload_file.write_text(json.dumps([
        {
            "blind_id": "B-001",
            "rater": "rater_a",
            "valence": "probably_benign",
            "confidence": "high",
            "notes": None,
        }
    ]), encoding="utf-8")

    ts = "2026-08-14T15:00:00Z"
    args = [
        "blind",
        "--input", str(payload_file),
        "--reviewer-id", "rater_user_1",
        "--timestamp", ts,
    ]

    # Test 1: Lock enforcement (fails on master if master does not lock!)
    lock_file = audit_dir / ".review.lock"
    lock_file.write_text("77777\n", encoding="utf-8")
    with pytest.raises(ReviewLockError):
        p7g.main(args)
    lock_file.unlink()

    # Test 2: Dry-run
    ret_dry = p7g.main(args + ["--dry-run"])
    assert ret_dry == 0
    assert json.loads(blind_file.read_text(encoding="utf-8"))["items"][0]["rater_a"]["isolated_prompt_valence_observed"] is None
    assert len(list(snap_dir.glob("*.json"))) == 0

    # Test 3: Real run
    ret_real = p7g.main(args)
    assert ret_real == 0

    # Verify state updated
    updated_blind = json.loads(blind_file.read_text(encoding="utf-8"))
    assert updated_blind["items"][0]["rater_a"]["isolated_prompt_valence_observed"] == "probably_benign"

    # Verify snapshot
    clean_ts = ts.replace(":", "")
    assert (snap_dir / f"phase7g_blind_review.{clean_ts}.json").is_file()

    # Verify history
    lines = history_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[-1])["event"] == "blind_annotation"

    # Verify lock cleaned up
    assert not lock_file.exists()
