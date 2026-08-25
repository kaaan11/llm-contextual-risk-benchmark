#!/usr/bin/env python3
"""Phase 7E — pre-registration freeze and integrity record.

Computes SHA-256 over the frozen protocol documents and over the datasets that
Phase 7E must not modify, and writes
``results/dataset_audit/phase7e_preregistration_hash.json``.

Purpose: allow a third party to verify that the analysis protocol was fixed
*before* any model evaluation existed, and that the Turkish exploratory corpus
and the public-benchmark pilot dataset were untouched by this phase.

Performs no network access and calls no model API.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

FROZEN_AT = "2026-08-14T00:00:00Z"
PROTOCOL_ID = "LLM-CTX-PILOT-2026-01"
PROTOCOL_VERSION = "1.0.2"

# Documents whose bytes constitute the frozen protocol.
#
# MANIFEST CORRECTION (v1.0.0 -> v1.0.1, made BEFORE any model evaluation):
# v1.0.0 wrongly included "results/dataset_audit/phase7e_review.json" here. That
# file is the *mutable review state*: Phase 7E exists to record KEEP/REVISE/REJECT
# decisions into it, so freezing it made the review process unrepresentable — the
# first recorded decision would have broken the integrity check.
#
# PRE-EVALUATION CLARIFICATION (v1.0.1 -> v1.0.2, made BEFORE any model
# evaluation): adds docs/phase7e_pre_evaluation_clarification.md to the manifest.
# That document records the researcher's Option-A decision for audit finding F-01
# (construct clarified to whole conversational-context sensitivity; stimuli remain
# byte-unchanged) and corrects the F-02 role-structure wording ambiguity. It
# changes no hypothesis, metric, threshold, decision rule or analysis method.
# The four original protocol documents below remain asserted byte-identical to
# their v1.0.0 hashes (see PROTOCOL_BASELINE_V1_0_0).
PROTOCOL_FILES = (
    "docs/phase7e_preregistration.md",
    "docs/phase7e_annotation_protocol.md",
    "docs/PHASE_7D_EXPERIMENTAL_DESIGN.md",
    "docs/PHASE_7D_DESIGN_TABLE.md",
    "docs/phase7e_pre_evaluation_clarification.md",
    "results/dataset_audit/phase7e_design_snapshot.json",
)

# Per-file hashes recorded under protocol v1.0.0. The four protocol documents must
# still match these exactly; any drift means a rule was edited and is a violation.
PROTOCOL_BASELINE_V1_0_0 = {
    "docs/phase7e_preregistration.md":
        "7d46e0fba94a88beaa27a4c41efa209e3c89619b3f3dd5e96877997aa99bf87c",
    "docs/phase7e_annotation_protocol.md":
        "41c628b801a08d85e52d3f6fe79eb711e9e949b76ad29cdc425356fb742fefa4",
    "docs/PHASE_7D_EXPERIMENTAL_DESIGN.md":
        "e120652648bbec68cca3bed95ce924f0ce27f2f1cc2661334edea62f4fd23688",
    "docs/PHASE_7D_DESIGN_TABLE.md":
        "8bced7f9e42d0d2919192498f2e8e380aeeae820ed02f7cc0e9b7717e7bad366",
}
PRIOR_COMPOSITE_V1_0_0 = (
    "125bdf36dad11bb7242743dc58a97a7bb868ac8a39308156ba3b942962f25a29"
)
# Composite produced by manifest v1.0.1; pinned so the v1.0.2 amendment chain is
# independently verifiable.
PRIOR_COMPOSITE_V1_0_1 = (
    "d945d4419e817e496521afa7ab8bdb2e7005bbe6245ce590418d66184f646819"
)

# Deliberately NOT frozen: Phase 7E mutates these by design.
MUTABLE_FILES = (
    "results/dataset_audit/phase7e_review.json",
    "results/dataset_audit/phase7e_review_history.jsonl",
)

# Datasets Phase 7E must leave byte-identical. Recorded so drift is detectable.
PROTECTED_FILES = (
    "dataset/pilot/multiturn/multiturn_dataset.json",
    "dataset/pilot/multiturn/records.jsonl",
    "dataset/pilot/multiturn/EXPLORATORY_DRAFT_V0.1_TR.json",
    "dataset/pilot/pilot_dataset.json",
    "dataset/pilot/records.jsonl",
    "dataset/pilot/attribution.json",
)

# Baselines captured at Phase 7E start, before any Phase 7E file was written.
PROTECTED_BASELINE = {
    "dataset/pilot/multiturn/multiturn_dataset.json":
        "7ae3b858de57c08417d136a1af5e82a1b94fb747211e5161fa2c8268639b9a86",
    "dataset/pilot/multiturn/records.jsonl":
        "aafb6623a8b675a8396c7e5b361275204c4bdf531100b3bb0bb26bad048d66b4",
    "dataset/pilot/multiturn/EXPLORATORY_DRAFT_V0.1_TR.json":
        "bf2f84392ba5d17f2a505aef8c8bf4ffe0d5b84c151de6129f1ab91af62da172",
    "dataset/pilot/pilot_dataset.json":
        "427e89ea4502d96ccbf867c57617a308dbb9b1afb8ff1f3b16684097a58f7b56",
    "dataset/pilot/records.jsonl":
        "d922b74501e39630494197dddda81e87c8b8270d20534b60a2467480a20f9804",
    "dataset/pilot/attribution.json":
        "7addc4f2da66c67d32e3e62178c1484271671ca2efe115140d1ae74bb60ffc4b",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_record(root: Path) -> dict:
    protocol = {}
    for rel in PROTOCOL_FILES:
        p = root / rel
        protocol[rel] = {
            "sha256": sha256_file(p),
            "bytes": p.stat().st_size,
        }

    # Composite hash: SHA-256 over the sorted "path:hash" lines, so the whole
    # protocol has one verifiable fingerprint.
    joined = "\n".join(f"{rel}:{protocol[rel]['sha256']}" for rel in sorted(protocol))
    composite = hashlib.sha256(joined.encode("utf-8")).hexdigest()

    protected = {}
    for rel in PROTECTED_FILES:
        p = root / rel
        current = sha256_file(p)
        baseline = PROTECTED_BASELINE.get(rel)
        protected[rel] = {
            "sha256": current,
            "baseline_sha256": baseline,
            "unchanged": (baseline is not None and current == baseline),
        }

    # The four protocol documents must be byte-identical to protocol v1.0.0.
    drift = {
        rel: {"expected": want, "actual": protocol[rel]["sha256"]}
        for rel, want in PROTOCOL_BASELINE_V1_0_0.items()
        if protocol.get(rel, {}).get("sha256") != want
    }

    mutable = {}
    for rel in MUTABLE_FILES:
        p = root / rel
        mutable[rel] = {
            "sha256": sha256_file(p) if p.exists() else None,
            "frozen": False,
            "reason": "Phase 7E records researcher decisions into this file by design.",
        }

    amendment_v1_0_1 = {
        "from_version": "1.0.0",
        "to_version": "1.0.1",
        "type": "manifest_scope_correction",
        "made_before_any_model_evaluation": True,
        "rules_changed": False,
        "summary": (
            "v1.0.0 incorrectly listed the mutable review-state file "
            "results/dataset_audit/phase7e_review.json as a frozen protocol file. "
            "Phase 7E must write researcher decisions into that file, so the first "
            "recorded decision would have broken freeze integrity. The manifest now "
            "covers an immutable design snapshot instead. No hypothesis, metric, "
            "threshold, decision rule or analysis method was altered."
        ),
        "prior_composite_protocol_hash": PRIOR_COMPOSITE_V1_0_0,
    }
    amendment = {
        "from_version": "1.0.1",
        "to_version": PROTOCOL_VERSION,
        "type": "pre_evaluation_clarification",
        "made_before_any_model_evaluation": True,
        "rules_changed": False,
        "summary": (
            "Adds docs/phase7e_pre_evaluation_clarification.md to the frozen protocol "
            "manifest. The clarification records the researcher's Option-A decision on "
            "audit finding F-01: stimuli stay byte-unchanged and the estimand is "
            "clarified to whole conversational-context sensitivity, with binding "
            "interpretation constraints (no pure user-context-only causal claims; "
            "assistant-turn-shared vs assistant-turn-differing reporting strata; AM "
            "diagnostic-only; D-arm and NH/NB channel limitations). It also corrects "
            "the preregistration section 5 role wording ambiguity (audit finding F-02): "
            "'user-user only' meant no developer/system arm; the realized structure is "
            "user-assistant-user(/user), exactly as authored in Phase 7F. No hypothesis, "
            "metric, threshold, decision rule or analysis method was altered, and the "
            "four original protocol documents remain byte-identical to v1.0.0."
        ),
        "prior_composite_protocol_hash": PRIOR_COMPOSITE_V1_0_1,
        "clarifies_findings": ["F-01", "F-02"],
        "clarification_document": "docs/phase7e_pre_evaluation_clarification.md",
    }
    return {
        "record_version": "0.2.0",
        "protocol_id": PROTOCOL_ID,
        "protocol_version": PROTOCOL_VERSION,
        "phase": "7E",
        "frozen_at": FROZEN_AT,
        "hash_algorithm": "sha256",
        "composite_protocol_hash": composite,
        "amendment": amendment,
        "prior_amendments": [amendment_v1_0_1],
        "mutable_files": mutable,
        "composite_method": (
            "sha256 over newline-joined '<relative_path>:<sha256>' lines, paths sorted "
            "lexicographically, UTF-8 encoded"
        ),
        "protocol_files": protocol,
        "protected_files": protected,
        "all_protected_unchanged": all(v["unchanged"] for v in protected.values()),
        "protocol_documents_byte_identical_to_v1_0_0": not drift,
        "protocol_document_drift": drift,
        "evaluation_state": {
            "model_evaluation_performed": False,
            "api_calls_made": False,
            "final_prompts_authored": False,
            "results_observed": False,
        },
        "verification_note": (
            "Recompute the per-file hashes and the composite to confirm the analysis protocol "
            "was fixed before any model output existed. Any post-evaluation change to a "
            "protocol file will alter the composite hash and must be reported as a protocol "
            "amendment with a new protocol_version, not as an edit."
        ),
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    record = build_record(root)
    out = root / "results" / "dataset_audit" / "phase7e_preregistration_hash.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    print(f"composite protocol hash: {record['composite_protocol_hash']}")
    print(f"protocol docs byte-identical to v1.0.0: "
          f"{record['protocol_documents_byte_identical_to_v1_0_0']}")
    print(f"protected datasets unchanged: {record['all_protected_unchanged']}")


if __name__ == "__main__":
    main()
