#!/usr/bin/env python3
"""Read-only check of sealed files and the historical append-only audit prefixes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "560c758e787f4acebbbc03f724eb7b9d43dbff373b7331583433b91ff78bf282"
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
    manifest_bytes = (audit / "phase7e_preregistration_hash.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    errors = []
    if sha256(manifest_bytes) != MANIFEST:
        errors.append("frozen integrity manifest mismatch")
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


def check_integrity_flags(root: Path = ROOT) -> dict[str, Any]:
    """Derive Phase 7G quality summary integrity flags from manifest and pins.

    Returns deterministic flag objects with status, checked_files, and basis.
    A missing file or manifest mismatch yields status=False.
    Unmapped datasets without repository pins yield status='unknown'.
    """
    audit = root / "results" / "dataset_audit"
    manifest_file = audit / "phase7e_preregistration_hash.json"

    manifest: dict | None = None
    manifest_valid = False
    if manifest_file.is_file():
        try:
            manifest_bytes = manifest_file.read_bytes()
            if sha256(manifest_bytes) == MANIFEST:
                data = json.loads(manifest_bytes.decode("utf-8"))
                if isinstance(data, dict) and "protocol_files" in data:
                    manifest = data
                    manifest_valid = True
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            manifest_valid = False
            manifest = None

    # 1. phase7d_design_unchanged: compare docs/PHASE_7D_EXPERIMENTAL_DESIGN.md
    # and docs/PHASE_7D_DESIGN_TABLE.md with manifest protocol_files hashes.
    p7d_files = [
        "docs/PHASE_7D_EXPERIMENTAL_DESIGN.md",
        "docs/PHASE_7D_DESIGN_TABLE.md",
    ]
    p7d_ok = manifest_valid
    if p7d_ok and manifest:
        proto_files = manifest.get("protocol_files", {})
        for rel in p7d_files:
            target = root / rel
            if not target.is_file():
                p7d_ok = False
                break
            expected = proto_files.get(rel, {}).get("sha256")
            try:
                if not expected or sha256(target.read_bytes()) != expected:
                    p7d_ok = False
                    break
            except OSError:
                p7d_ok = False
                break
    else:
        p7d_ok = False

    phase7d_flag = {
        "status": p7d_ok,
        "checked_files": p7d_files,
        "basis": (
            f"sha256 matches manifest protocol_files ({MANIFEST})"
            if p7d_ok
            else "File missing, hash mismatch, or manifest invalid against protocol_files"
        ),
    }

    # 2. phase7e_preregistration_unchanged: compare docs/phase7e_preregistration.md,
    # docs/phase7e_annotation_protocol.md and docs/phase7e_pre_evaluation_clarification.md
    # with manifest hashes, plus the composite protocol hash check.
    p7e_files = [
        "docs/phase7e_preregistration.md",
        "docs/phase7e_annotation_protocol.md",
        "docs/phase7e_pre_evaluation_clarification.md",
    ]
    p7e_ok = manifest_valid
    if p7e_ok and manifest:
        proto_files = manifest.get("protocol_files", {})
        for rel in p7e_files:
            target = root / rel
            if not target.is_file():
                p7e_ok = False
                break
            expected = proto_files.get(rel, {}).get("sha256")
            try:
                if not expected or sha256(target.read_bytes()) != expected:
                    p7e_ok = False
                    break
            except OSError:
                p7e_ok = False
                break
        if p7e_ok:
            if manifest.get("composite_protocol_hash") != COMPOSITE:
                p7e_ok = False
            else:
                try:
                    proto_hashes = {p: rec["sha256"] for p, rec in proto_files.items()}
                    computed_composite = sha256(
                        "\n".join(f"{p}:{h}" for p, h in sorted(proto_hashes.items())).encode()
                    )
                    if computed_composite != COMPOSITE:
                        p7e_ok = False
                except (KeyError, TypeError):
                    p7e_ok = False
    else:
        p7e_ok = False

    phase7e_flag = {
        "status": p7e_ok,
        "checked_files": p7e_files,
        "basis": (
            f"sha256 matches manifest protocol_files and composite matches "
            f"COMPOSITE pin ({COMPOSITE})"
            if p7e_ok
            else "File missing, hash mismatch, or composite protocol hash mismatch"
        ),
    }

    # 3. phase7f_stimulus_v1_preserved: compare stimulus_dataset_v1.json with STIMULUS pin.
    p7f_files = ["dataset/pilot/multiturn/stimulus_dataset_v1.json"]
    p7f_ok = False
    stimulus_target = root / p7f_files[0]
    if stimulus_target.is_file():
        try:
            if sha256(stimulus_target.read_bytes()) == STIMULUS:
                p7f_ok = True
        except OSError:
            pass

    phase7f_flag = {
        "status": p7f_ok,
        "checked_files": p7f_files,
        "basis": (
            f"sha256 matches pinned STIMULUS hash ({STIMULUS})"
            if p7f_ok
            else f"File missing or sha256 mismatch against pinned STIMULUS hash ({STIMULUS})"
        ),
    }

    # 4. public_benchmark_unchanged: unmapped without pinned file
    public_flag = {
        "status": "unknown",
        "checked_files": [],
        "basis": "No external public benchmark corpus is vendored or pinned in the repository.",
    }

    # 5. turkish_dataset_unchanged: unmapped without definition in code/docs
    turkish_flag = {
        "status": "unknown",
        "checked_files": [],
        "basis": "No repository file is defined or pinned as the Turkish dataset.",
    }

    return {
        "phase7d_design_unchanged": phase7d_flag,
        "phase7e_preregistration_unchanged": phase7e_flag,
        "phase7f_stimulus_v1_preserved": phase7f_flag,
        "public_benchmark_unchanged": public_flag,
        "turkish_dataset_unchanged": turkish_flag,
        "pre_review_snapshot": "results/dataset_audit/snapshots/phase7f_stimulus.v1.pre_qc.json",
    }


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
