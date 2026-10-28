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


def _load_pinned_manifest(root: Path) -> dict | None:
    """Return the integrity manifest only if its bytes match the MANIFEST pin."""
    try:
        data = (root / "results/dataset_audit/phase7e_preregistration_hash.json").read_bytes()
    except OSError:
        return None
    if sha256(data) != MANIFEST:
        return None
    return json.loads(data)


def _files_match(root: Path, files: list[str], expected: dict[str, str]) -> bool:
    for relative in files:
        try:
            actual = sha256((root / relative).read_bytes())
        except OSError:
            return False
        if actual != expected.get(relative):
            return False
    return True


def _flag(ok: bool, files: list[str], basis: str) -> dict[str, Any]:
    return {"status": ok, "checked_files": files,
            "basis": basis if ok else f"missing file or hash mismatch ({basis})"}


def check_integrity_flags(root: Path = ROOT) -> dict[str, Any]:
    """Derive the Phase 7G summary integrity flags from real hash comparisons.

    A flag is True only after a comparison against a pinned hash, False on a
    missing file or mismatch, and "unknown" when nothing in the repository pins it.
    """
    manifest = _load_pinned_manifest(root)
    protocol = {p: r["sha256"] for p, r in (manifest or {}).get("protocol_files", {}).items()}
    protected = {p: r["sha256"] for p, r in (manifest or {}).get("protected_files", {}).items()}
    composite_ok = manifest is not None and manifest.get("composite_protocol_hash") == COMPOSITE

    design = ["docs/PHASE_7D_EXPERIMENTAL_DESIGN.md", "docs/PHASE_7D_DESIGN_TABLE.md"]
    prereg = ["docs/phase7e_preregistration.md", "docs/phase7e_annotation_protocol.md",
              "docs/phase7e_pre_evaluation_clarification.md"]
    stimulus = ["dataset/pilot/multiturn/stimulus_dataset_v1.json"]
    # docs/PHASE_7D_EXPERIMENTAL_DESIGN.md:154 names the Turkish set EXPLORATORY_DRAFT_V0.1_TR.
    turkish = ["dataset/pilot/multiturn/EXPLORATORY_DRAFT_V0.1_TR.json"]
    basis = f"manifest sha256 {MANIFEST}"
    return {
        "phase7d_design_unchanged": _flag(
            manifest is not None and _files_match(root, design, protocol), design,
            f"protocol_files, {basis}"),
        "phase7e_preregistration_unchanged": _flag(
            composite_ok and _files_match(root, prereg, protocol), prereg,
            f"protocol_files + composite {COMPOSITE}, {basis}"),
        "phase7f_stimulus_v1_preserved": _flag(
            _files_match(root, stimulus, {stimulus[0]: STIMULUS}), stimulus,
            f"STIMULUS pin {STIMULUS}"),
        "public_benchmark_unchanged": {
            "status": "unknown", "checked_files": [],
            "basis": "No public benchmark corpus is vendored or pinned in this repository."},
        "turkish_dataset_unchanged": _flag(
            manifest is not None and _files_match(root, turkish, protected), turkish,
            f"protected_files, {basis}"),
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
