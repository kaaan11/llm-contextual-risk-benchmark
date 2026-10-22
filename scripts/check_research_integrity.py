#!/usr/bin/env python3
"""Read-only check of sealed files and the historical append-only audit prefixes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPOSITE = "47ae3fed4117639ef2575135a6ca63f000f4fcc8c052c629355f6ccf4bbcfc6f"
STIMULUS = "2f78e79e19d844b84b6bc06a0c2bef47e19283cc7c54b91f6ae283e1a74af077"
AUDIT_PREFIXES = {
    "phase7e_review_history.jsonl": (51, "e145afed133bb4f7995d0e1fffb6d169f51fbd29ce9e0b6edbd73c19cf3b866c"),
    "phase7g_review_history.jsonl": (5, "23755e0f2a37db370f9a3532a3a7e495e0f71c33e75dbb73c9e7632b8a550a15"),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify(root: Path = ROOT) -> list[str]:
    """Return violations without changing files or printing blind material."""
    audit = root / "results/dataset_audit"
    manifest = json.loads((audit / "phase7e_preregistration_hash.json").read_text(encoding="utf-8"))
    errors = []
    protocol_hashes = {}
    for section in ("protocol_files", "protected_files"):
        for relative, record in manifest[section].items():
            actual = sha256((root / relative).read_bytes())
            if actual != record["sha256"]:
                errors.append(f"hash mismatch: {relative}")
            if section == "protocol_files":
                protocol_hashes[relative] = actual
    composite = sha256("\n".join(f"{p}:{h}" for p, h in sorted(protocol_hashes.items())).encode())
    if composite != COMPOSITE or manifest["composite_protocol_hash"] != COMPOSITE:
        errors.append("frozen protocol composite mismatch")
    if sha256((root / "dataset/pilot/multiturn/stimulus_dataset_v1.json").read_bytes()) != STIMULUS:
        errors.append("stimulus v1 hash mismatch")
    for name, (count, expected) in AUDIT_PREFIXES.items():
        lines = (audit / name).read_bytes().splitlines(keepends=True)
        if len(lines) < count or sha256(b"".join(lines[:count])) != expected:
            errors.append(f"audit prefix changed: {name}")
    return errors


def main() -> int:
    try:
        errors = verify()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"INVALID: integrity input unreadable ({type(exc).__name__})")
        return 1
    if errors:
        for error in errors:
            print(f"INVALID: {error}")
        return 1
    print("VALID: frozen protocol, protected datasets, stimulus v1 and audit prefixes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
