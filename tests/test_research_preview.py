"""Read-only evidence checks; fixtures change only temporary byte sequences."""
import hashlib
import json
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


def test_integrity_rejects_changed_dataset_with_rewritten_manifest(tmp_path):
    for folder in ("docs", "dataset", "results"):
        shutil.copytree(ROOT / folder, tmp_path / folder)
    manifest_path = tmp_path / "results/dataset_audit/phase7e_preregistration_hash.json"
    manifest = json.loads(manifest_path.read_text())
    relative = next(iter(manifest["protected_files"]))
    dataset_path = tmp_path / relative
    dataset_path.write_bytes(dataset_path.read_bytes() + b"\n")
    manifest["protected_files"][relative]["sha256"] = hashlib.sha256(dataset_path.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest))
    assert "frozen integrity manifest mismatch" in verify(tmp_path)
