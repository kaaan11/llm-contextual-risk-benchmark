"""Read-only evidence checks; fixtures change only temporary byte sequences."""
import shutil
import socket

import pytest

from scripts.check_research_integrity import AUDIT_PREFIXES, ROOT, verify
from scripts.offline_preview import preview


def test_offline_preview_has_no_empirical_result():
    assert preview() == {
        "attack_success_rate": None, "completed_requests": 1,
        "empirical_result": False, "provider": "mock", "total_requests": 1,
    }


def test_current_frozen_evidence():
    assert verify() == []


def test_integrity_rejects_tampering_but_allows_appending_audit(tmp_path):
    # Copy sealed evidence, never mutate the repository source or create ratings.
    for folder in ("docs", "dataset", "results"):
        shutil.copytree(ROOT / folder, tmp_path / folder)
    assert verify(tmp_path) == []
    path = tmp_path / "results/dataset_audit" / next(iter(AUDIT_PREFIXES))
    path.write_bytes(path.read_bytes() + b'{"event":"integrity-test-only"}\n')
    assert verify(tmp_path) == []
    original = path.read_bytes()
    path.write_bytes(b"X" + original[1:])
    assert any("audit prefix changed" in e for e in verify(tmp_path))
    path.write_bytes(original)
    stimulus = tmp_path / "dataset/pilot/multiturn/stimulus_dataset_v1.json"
    stimulus.write_bytes(stimulus.read_bytes() + b"\n")
    assert "stimulus v1 hash mismatch" in verify(tmp_path)


def test_offline_guard_rejects_network_before_connecting():
    import os
    if os.environ.get("BENCHMARK_TEST_OFFLINE") != "1":
        pytest.skip("offline CI profile only")
    with pytest.raises(AssertionError, match="Network access is disabled"):
        socket.create_connection(("127.0.0.1", 9))
