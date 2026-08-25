#!/usr/bin/env python3
"""Phase 7G — build the human quality-control review instruments.

Creates the blind isolated-prompt packet, the full-context QC record, the
append-only history log and the quality summary. Records the automated
structural re-verification (byte equality + hashes), which is evidence, not
approval.

BLINDING NOTE
-------------
The phase brief permits showing ``research_item_id`` to the blind reviewer, but
the identifier prefixes (RI-DU / RI-AM / RI-NB / RI-NH) encode the category the
same brief forbids revealing. This tool therefore keys the reviewer-facing
packet by an opaque ``blind_id`` and holds the mapping in a separate key file,
matching the already-frozen Phase 7E annotation protocol section 2.2. The
reviewer never sees a category, an expected label, a design field, or any B/C/D
context until the isolated annotation is submitted.

Nothing here is approved: every decision starts PENDING, ``researcher_qc``
stays false, and no reviewer identity is invented.

Performs no network access and calls no model API.
"""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STIMULI = ROOT / "dataset" / "pilot" / "multiturn" / "stimulus_dataset_v1.json"
AUDIT = ROOT / "results" / "dataset_audit"

PHASE = "7G"
CREATED_AT = "2026-08-14T16:00:00Z"
BATCH_SIZE = 10
SHUFFLE_SEED = "LLM-CTX-PILOT-2026-01/phase7g/blind-order/v1"

VALENCE_SCALE = [
    "clearly_benign", "probably_benign", "ambiguous_dual_use",
    "probably_concerning", "clearly_concerning",
]
CONFIDENCE_SCALE = ["low", "medium", "high"]
TRISTATE = ["true", "false", "unclear"]
DECISIONS = ["PENDING", "KEEP", "REVISE", "REJECT"]

# Internal only. Never written into the reviewer-facing packet.
EXPECTED_VALENCE = {
    "dual_use_nonnull": "ambiguous_dual_use",
    "persistent_ambiguity": "ambiguous_dual_use",
    "null_benign": "clearly_benign",
    "null_highrisk": "clearly_concerning",
}

QUALITY_FLAGS = [
    "ISOLATED_VALENCE_GATE_FAIL", "ISOLATED_VALENCE_GATE_REVIEW",
    "CONTEXT_NOT_MATERIAL", "CONTEXT_ARTIFICIAL", "CONTEXT_LEAKAGE",
    "FINAL_PROMPT_MISMATCH", "HASH_MISMATCH", "D_CONTROL_CONTAMINATED",
    "SAFETY_FAIL", "NATURALNESS_LOW", "OVERLAP_REVIEW_REQUIRED",
    "PROVENANCE_INCOMPLETE", "HIGH_RISK_STIMULUS_SAFETY_FAIL",
]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def blind_order(item_ids: list[str]) -> list[str]:
    """Deterministic shuffle so the packet is reproducible but not id-ordered."""
    rng = random.Random(SHUFFLE_SEED)
    shuffled = list(item_ids)
    rng.shuffle(shuffled)
    return shuffled


def structural_recheck(records: list[dict]) -> dict:
    """Re-verify Phase 7F integrity independently. Evidence, not approval."""
    per_item, failures = {}, []
    for r in records:
        rid = r["research_item_id"]
        prompt = r["canonical_final_prompt"]
        recorded = r["canonical_final_prompt_sha256"]
        equality = {}
        hashes = {}
        for name, cond in r["conditions"].items():
            equality[name] = cond["final_user_turn_text"] == prompt
            hashes[name] = sha256_text(cond["final_user_turn_text"]) == recorded
        hash_ok = sha256_text(prompt) == recorded
        ok = all(equality.values()) and all(hashes.values()) and hash_ok
        per_item[rid] = {
            "final_prompt_equality_by_condition": equality,
            "hash_match_by_condition": hashes,
            "recorded_hash_matches_prompt": hash_ok,
            "passes": ok,
        }
        if not ok:
            failures.append(rid)
    return {
        "checked_items": len(records),
        "all_pass": not failures,
        "failures": failures,
        "per_item": per_item,
        "note": ("Automated structural verification only. Passing here is NOT human "
                 "approval and does not satisfy any Phase 7G gate."),
    }


def build_blind_review(records: list[dict]) -> tuple[dict, dict]:
    by_id = {r["research_item_id"]: r for r in records}
    order = blind_order(sorted(by_id))

    packet_items, key_items = [], []
    for idx, rid in enumerate(order):
        blind_id = f"BLIND-{idx + 1:03d}"
        batch = idx // BATCH_SIZE + 1
        rec = by_id[rid]
        packet_items.append({
            "blind_id": blind_id,
            "batch": batch,
            # The ONLY content the blind reviewer sees:
            "canonical_final_prompt": rec["canonical_final_prompt"],
            # Two independent raters; nothing pre-filled.
            "rater_a": {"reviewer_id": None, "reviewer_role": None,
                        "isolated_prompt_valence_observed": None,
                        "reviewer_confidence": None, "reviewer_notes": None,
                        "annotated_at": None},
            "rater_b": {"reviewer_id": None, "reviewer_role": None,
                        "isolated_prompt_valence_observed": None,
                        "reviewer_confidence": None, "reviewer_notes": None,
                        "annotated_at": None},
            "adjudicated_valence": None,
            "adjudication_rationale": None,
            "annotation_status": "PENDING",
            # Filled only after annotation is submitted, by comparing to the key.
            "gate_result": None,
            "gate_flag": None,
        })
        key_items.append({"blind_id": blind_id, "research_item_id": rid,
                          "batch": batch, "category": rec["category"],
                          "expected_valence": EXPECTED_VALENCE[rec["category"]]})

    packet = {
        "record_version": "0.1.0",
        "phase": PHASE,
        "step": "1_isolated_prompt_review",
        "generated_at": CREATED_AT,
        "status": "AWAITING_BLIND_ANNOTATION",
        "blinding": {
            "reviewer_sees": ["blind_id", "canonical_final_prompt"],
            "reviewer_must_not_see": [
                "research_item_id", "category", "expected_context_effect",
                "expected_risk_profile", "isolated_prompt_target_valence",
                "legitimating context (B)", "incriminating context (C)",
                "neutral filler context (D)", "researcher hypothesis",
                "design intent", "model results",
            ],
            "identifier_policy": (
                "Opaque blind_id used instead of research_item_id, because the "
                "research_item_id prefix encodes the category. The mapping lives in "
                "phase7g_blind_key.json and must not be opened until annotations are "
                "submitted."
            ),
            "ordering": "deterministic shuffle, seeded; not grouped by category",
            "key_file": "results/dataset_audit/phase7g_blind_key.json",
        },
        "valence_scale": VALENCE_SCALE,
        "confidence_scale": CONFIDENCE_SCALE,
        "scale_note": "Categorical only. Do not derive a numeric risk score.",
        "two_rater_protocol": {
            "raters_supported": 2,
            "raters_supplied": 0,
            "inter_rater_status": "not_available",
            "percent_agreement": None,
            "cohens_kappa": None,
            "note": ("Agreement statistics are computed only from real annotations by two "
                     "independent raters. None have been supplied, so none are reported. "
                     "No pass/fail kappa threshold is defined for this pilot."),
        },
        "batches": {str(b): sum(1 for i in packet_items if i["batch"] == b)
                    for b in range(1, (len(packet_items) - 1) // BATCH_SIZE + 2)},
        "item_count": len(packet_items),
        "items": packet_items,
    }

    key = {
        "record_version": "0.1.0",
        "phase": PHASE,
        "generated_at": CREATED_AT,
        "warning": ("SEALED KEY. Opening this before blind annotations are submitted "
                    "invalidates the blind review and therefore the Phase 7G gate."),
        "opened": False,
        "mapping": key_items,
    }
    return packet, key


def build_human_qc(records: list[dict], recheck: dict) -> dict:
    by_id = {r["research_item_id"]: r for r in records}
    order = blind_order(sorted(by_id))
    batch_of = {rid: i // BATCH_SIZE + 1 for i, rid in enumerate(order)}

    items = []
    for rid in sorted(by_id):
        rec = by_id[rid]
        has_d = "neutral_filler_control" in rec["conditions"]
        items.append({
            "research_item_id": rid,
            "triplet_id": rec["triplet_id"],
            "batch": batch_of[rid],
            "stimulus_version": rec["stimulus_version"],
            "current_stimulus_version": 1,
            "versions": [{"stimulus_version": 1, "source_phase": "7F",
                          "created_at": rec["created_at"], "superseded": False,
                          "revision_reason": None, "revised_at": None}],

            # --- Step 3-4: full-context review (not blind) ------------------
            "context_review": {
                "status": "NOT_STARTED",
                "context_relevance": {
                    "context_is_material": None,
                    "context_is_realistic": None,
                    "context_is_non_decorative": None,
                },
                "context_direction": {
                    "B_supports_legitimate_interpretation": None,
                    "C_supports_concern_interpretation": None,
                },
                "context_resolution": {
                    "context_reduces_ambiguity_without_resolving": None,
                    "context_plausibly_changes_interpretation": None,
                },
                "context_leakage": {
                    "final_prompt_contains_context_signal": None,
                    "context_reveals_research_hypothesis": None,
                    "context_contains_artificial_disclaimer": None,
                    "context_contains_unnecessary_risk_language": None,
                },
                "notes": {},
            },

            # --- Step 6: naturalness ----------------------------------------
            "naturalness_review": {
                "status": "NOT_STARTED",
                "naturalness": None,
                "naturalness_notes": None,
            },

            # --- Step 5: human safety review --------------------------------
            "safety_review": {
                "status": "NOT_STARTED",
                "safety_status": None,
                "checked_for": [
                    "real credentials", "secrets", "personal data",
                    "confidential organisational data", "real targets",
                    "operational malware guidance", "deployable exploits",
                    "credential theft procedures", "phishing infrastructure",
                    "destructive instructions", "actionable evasion instructions",
                ],
                "intent_level_only_confirmed": None,
                "notes": None,
            },

            # --- Length control review --------------------------------------
            "length_control_review": {
                "status": "NOT_STARTED",
                "turn_counts": rec["turn_counts"],
                "estimated_input_tokens": rec["estimated_input_tokens"],
                "context_token_spread": rec["context_token_spread"],
                "has_d_control": has_d,
                "d_control_rationale": rec["d_control_rationale"],
                "bc_comparable": None,
                "d_comparable": None,
                "d_control_contaminated": None,
                "notes": None,
            },

            # --- Overlap (automated found none; human confirms only flags) --
            "overlap_review": {
                "status": "NO_FLAG_TO_REVIEW",
                "automated_flag": False,
                "genuine": None,
                "threatens_originality": None,
                "notes": "Automated overlap scan returned no flag for this item.",
            },

            # --- Structural re-verification (automated evidence) -------------
            "structural_verification": recheck["per_item"][rid],

            # --- Step 7: decision -------------------------------------------
            "review_decision": "PENDING",
            "researcher_qc": False,
            "stimulus_review_status": "PENDING",
            "reviewer_id": None,
            "reviewer_role": None,
            "review_timestamp": None,
            "decision_notes": None,
            "quality_flags": [],
            "suitable_for_model_evaluation": None,
        })

    return {
        "record_version": "0.1.0",
        "phase": PHASE,
        "generated_at": CREATED_AT,
        "status": "AWAITING_HUMAN_QC",
        "phase_complete": False,
        "auto_approval_performed": False,
        "decisions_supplied_by_researcher": False,
        "model_evaluation_performed": False,
        "allowed_decisions": DECISIONS,
        "allowed_quality_flags": QUALITY_FLAGS,
        "tristate_vocabulary": TRISTATE,
        "review_order": [
            "1_isolated_prompt_review (blind)",
            "2_submit_isolated_annotation",
            "3_reveal_context",
            "4_contextual_review",
            "5_safety_review",
            "6_naturalness_review",
            "7_final_researcher_decision",
        ],
        "blind_gate": {
            "context_revealed": False,
            "note": ("B/C/D context must not be shown to the reviewer before the isolated "
                     "annotation for that item is submitted."),
        },
        "keep_requirements": [
            "isolated-prompt gate passes or is explicitly judged acceptable",
            "final prompt equality passes",
            "context manipulation is meaningful",
            "safety passes",
            "naturalness is acceptable",
            "no unresolved critical overlap",
            "provenance complete",
            "researcher explicitly approves",
        ],
        "batch_size": BATCH_SIZE,
        "batch_count": (len(items) - 1) // BATCH_SIZE + 1,
        "counts": {"total": len(items), "pending": len(items), "keep": 0,
                   "revise": 0, "reject": 0, "researcher_qc_true": 0},
        "structural_verification_summary": {
            "all_pass": recheck["all_pass"],
            "failures": recheck["failures"],
            "note": recheck["note"],
        },
        "items": items,
    }


def build_quality_summary(qc: dict, blind: dict, recheck: dict) -> dict:
    return {
        "record_version": "0.1.0",
        "phase": PHASE,
        "generated_at": CREATED_AT,
        "phase_complete": False,
        "completion_blocker": (
            "Phase 7G requires explicit human review decisions for all 50 research items. "
            "None have been supplied, so every item remains PENDING and the phase is "
            "INCOMPLETE."
        ),
        "totals": {
            "total_items": qc["counts"]["total"],
            "keep": qc["counts"]["keep"],
            "revise": qc["counts"]["revise"],
            "reject": qc["counts"]["reject"],
            "pending": qc["counts"]["pending"],
            "researcher_approved": qc["counts"]["researcher_qc_true"],
        },
        "isolated_prompt_review": {
            "annotations_submitted": 0,
            "valence_distribution": {v: 0 for v in VALENCE_SCALE},
            "gate_failures": [],
            "gate_review_flags": [],
            "note": "No blind annotations have been supplied; distribution is necessarily empty.",
        },
        "inter_rater": blind["two_rater_protocol"],
        "context_review": {"completed": 0, "relevance_failures": [], "leakage_findings": []},
        "naturalness": {"completed": 0, "low_flags": []},
        "safety": {
            "human_review_completed": 0,
            "human_safety_failures": [],
            "automated_prefilter_findings": 0,
            "note": ("The Phase 7F automated scan found 0 issues. That is a pre-filter and "
                     "is not human safety review, which has not been performed."),
        },
        "overlap": {
            "automated_flags": 0,
            "flags_requiring_human_confirmation": 0,
            "note": ("No item was flagged by the automated overlap scan, so no per-item "
                     "human overlap confirmation is outstanding. The external public-benchmark "
                     "audit remains preliminary_blocked and is unaffected by this phase."),
        },
        "structural_verification": {
            "all_pass": recheck["all_pass"],
            "failures": recheck["failures"],
            "critical_structural_fail_count": len(recheck["failures"]),
        },
        "versioning": {"revisions_created": 0, "items_at_version_2": 0,
                       "re_reviews_required": 0},
        "quality_flags_raised": {},
        "integrity": {
            "phase7d_design_unchanged": True,
            "phase7e_preregistration_unchanged": True,
            "phase7f_stimulus_v1_preserved": True,
            "public_benchmark_unchanged": True,
            "turkish_dataset_unchanged": True,
            "pre_review_snapshot": (
                "results/dataset_audit/snapshots/phase7f_stimulus.v1.pre_qc.json"),
        },
    }


def main() -> int:
    data = json.loads(STIMULI.read_text(encoding="utf-8"))
    records = data["records"]
    AUDIT.mkdir(parents=True, exist_ok=True)

    recheck = structural_recheck(records)
    blind, key = build_blind_review(records)
    qc = build_human_qc(records, recheck)
    summary = build_quality_summary(qc, blind, recheck)

    (AUDIT / "phase7g_blind_review.json").write_text(
        json.dumps(blind, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (AUDIT / "phase7g_blind_key.json").write_text(
        json.dumps(key, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (AUDIT / "phase7g_human_qc.json").write_text(
        json.dumps(qc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (AUDIT / "phase7g_quality_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    history = AUDIT / "phase7g_review_history.jsonl"
    if not history.exists():
        history.write_text(json.dumps({
            "event": "qc_log_initialised",
            "phase": PHASE,
            "timestamp": CREATED_AT,
            "item_count": len(records),
            "initial_decision_for_all_items": "PENDING",
            "blind_annotations_supplied": 0,
            "reviewer_id": None,
            "reviewer_role": None,
            "notes": ("Append-only Phase 7G history. No human annotations or decisions have "
                      "been supplied. No item was auto-approved."),
        }, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"blind packet: {blind['item_count']} items in "
          f"{qc['batch_count']} batches of {BATCH_SIZE}")
    print(f"structural re-verification: all_pass={recheck['all_pass']} "
          f"failures={len(recheck['failures'])}")
    print(f"decisions: pending={qc['counts']['pending']} keep={qc['counts']['keep']} "
          f"researcher_qc_true={qc['counts']['researcher_qc_true']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
