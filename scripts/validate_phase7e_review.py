#!/usr/bin/env python3
"""Phase 7E — review-record validator.

Enforces the review invariants that protect the pre-registration. Importable as
``validate(record) -> list[str]`` so the rules can be exercised against synthetic
violations in the test suite, rather than only against the (currently all-PENDING)
live record.

Performs no network access and calls no model API.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

VALID_DECISIONS = {"PENDING", "KEEP", "REVISE", "REJECT"}
VALID_VALENCE = {
    "clearly_benign", "probably_benign", "ambiguous_dual_use",
    "probably_concerning", "clearly_concerning",
}
VALID_CONTROL = {"T", "N", "F"}
EXPECTED_CATEGORIES = {
    "dual_use_nonnull": 30,
    "persistent_ambiguity": 7,
    "null_benign": 7,
    "null_highrisk": 6,
}
REQUIRED_DESIGN_FIELDS = (
    "research_item_id", "triplet_id", "category", "context_mechanism",
    "canonical_final_prompt_intent", "isolated_prompt_target_valence",
    "legitimating_context_intent", "incriminating_context_intent",
    "expected_context_effect", "expected_risk_profile",
    "intended_turn_count", "control_strategy", "safety_constraints",
)
# Fields that would mean stimulus text or model output leaked into this phase.
FORBIDDEN_FIELDS = (
    "canonical_final_prompt", "canonical_final_prompt_sha256", "final_prompt_text",
    "turns", "evaluation_conditions", "model_disposition", "model_observed_effect",
)
VALENCE_BY_CATEGORY = {
    "dual_use_nonnull": "ambiguous_dual_use",
    "persistent_ambiguity": "ambiguous_dual_use",
    "null_benign": "clearly_benign",
    "null_highrisk": "clearly_concerning",
}


def validate(record: dict) -> list[str]:
    """Return a list of invariant violations. Empty list == valid."""
    errors: list[str] = []
    items = record.get("items", [])

    if len(items) != 50:
        errors.append(f"expected 50 research items, found {len(items)}")

    ids = [i.get("research_item_id") for i in items]
    if len(set(ids)) != len(ids):
        errors.append("duplicate research_item_id values")

    counts: dict[str, int] = {}

    # phase-level gates
    for flag in ("stimulus_generation_permitted", "model_evaluation_permitted",
                 "final_prompts_exist", "auto_approval_performed"):
        if record.get(flag):
            errors.append(f"phase gate {flag} must be false in Phase 7E")

    blob = json.dumps(record)
    for field in FORBIDDEN_FIELDS:
        if f'"{field}"' in blob:
            errors.append(f"forbidden field present in Phase 7E record: {field}")

    for item in items:
        rid = item.get("research_item_id", "<unknown>")
        decision = item.get("review_decision")
        approved = item.get("researcher_approved")

        if decision not in VALID_DECISIONS:
            errors.append(f"{rid}: invalid review_decision {decision!r}")

        # --- approval invariants -------------------------------------------
        if approved:
            if decision != "KEEP":
                errors.append(f"{rid}: approved but review_decision is {decision!r}, not KEEP")
            if not (item.get("reviewer_id") or item.get("reviewer_role")):
                errors.append(f"{rid}: approved without a recorded reviewer")
            if not item.get("review_timestamp"):
                errors.append(f"{rid}: approved without a review_timestamp")
            checklist = item.get("decision_rule_checklist", {})
            unmet = [k for k, v in checklist.items() if v is not True]
            if unmet:
                errors.append(f"{rid}: approved with unmet decision rules: {sorted(unmet)}")

        if decision in {"REJECT", "REVISE"} and approved:
            errors.append(f"{rid}: {decision} item must not be researcher_approved")

        if decision == "REVISE":
            if not item.get("revision_request"):
                errors.append(f"{rid}: REVISE decision requires a revision_request record")
            elif item["revision_request"].get("revision_status") != "pending_revision":
                errors.append(f"{rid}: REVISE revision_status must be 'pending_revision'")
            if item.get("current_version", 1) > 1 and item.get("researcher_approved"):
                errors.append(f"{rid}: a revised version must be re-reviewed before approval")

        if decision == "REJECT" and not item.get("rejection_reason"):
            errors.append(f"{rid}: REJECT decision requires a recorded rejection reason")

        # A decided item must carry reviewer identity and a timestamp.
        if decision in {"KEEP", "REVISE", "REJECT"}:
            if not (item.get("reviewer_id") or item.get("reviewer_role")):
                errors.append(f"{rid}: decision {decision} recorded without a reviewer")
            if not item.get("review_timestamp"):
                errors.append(f"{rid}: decision {decision} recorded without a timestamp")
            if decision in {"REVISE", "REJECT"} and not item.get("researcher_notes"):
                errors.append(f"{rid}: decision {decision} recorded without researcher notes")

        # PENDING items must carry no review residue.
        if decision == "PENDING":
            for field in ("reviewer_id", "reviewer_role", "review_timestamp",
                          "researcher_notes"):
                if item.get(field) is not None:
                    errors.append(f"{rid}: PENDING item has {field} set")

        # --- versioning invariants -----------------------------------------
        versions = item.get("versions", [])
        if not versions:
            errors.append(f"{rid}: no versions recorded")
            continue
        if versions[0].get("version") != 1 or versions[0].get("source_phase") != "7D":
            errors.append(f"{rid}: version 1 must be the immutable Phase 7D design")
        for v in versions[1:]:
            if not v.get("revision_reason"):
                errors.append(f"{rid}: version {v.get('version')} lacks a revision_reason")
            if not v.get("revision_timestamp"):
                errors.append(f"{rid}: version {v.get('version')} lacks a revision_timestamp")
        current = item.get("current_version", 1)
        if not 1 <= current <= len(versions):
            errors.append(f"{rid}: current_version {current} out of range")

        # --- design metadata ------------------------------------------------
        design = versions[current - 1].get("design", {})
        for field in REQUIRED_DESIGN_FIELDS:
            if design.get(field) in (None, ""):
                errors.append(f"{rid}: missing design field {field}")
        cat = design.get("category")
        counts[cat] = counts.get(cat, 0) + 1
        if cat in VALENCE_BY_CATEGORY:
            want = VALENCE_BY_CATEGORY[cat]
            if design.get("isolated_prompt_target_valence") != want:
                errors.append(
                    f"{rid}: category {cat} requires target valence {want}, "
                    f"found {design.get('isolated_prompt_target_valence')!r}"
                )
        if design.get("isolated_prompt_target_valence") not in VALID_VALENCE:
            errors.append(f"{rid}: invalid isolated_prompt_target_valence")
        if design.get("control_strategy") not in VALID_CONTROL:
            errors.append(f"{rid}: invalid control_strategy")
        if cat in {"null_benign", "null_highrisk"} and design.get("control_strategy") != "F":
            errors.append(f"{rid}: null control item must use control_strategy F")

        # --- downstream gates must not be pre-empted ------------------------
        blind = item.get("blind_isolated_prompt_review", {})
        if blind.get("status") != "NOT_STARTED":
            errors.append(f"{rid}: blind isolated-prompt review cannot start before prompts exist")
        if blind.get("gate_result") is not None:
            errors.append(f"{rid}: blind review gate_result set before the review ran")
        ref = item.get("refusal_appropriateness_reference", {})
        if ref.get("status") != "NOT_STARTED":
            errors.append(f"{rid}: refusal-appropriateness references cannot be set in Phase 7E")

    if counts and counts != EXPECTED_CATEGORIES:
        errors.append(f"category distribution {counts} != expected {EXPECTED_CATEGORIES}")

    # --- declared counts must match reality ---------------------------------
    declared = record.get("counts", {})
    actual_pending = sum(1 for i in items if i.get("review_decision") == "PENDING")
    actual_approved = sum(1 for i in items if i.get("researcher_approved"))
    if declared.get("pending") != actual_pending:
        errors.append(f"counts.pending {declared.get('pending')} != actual {actual_pending}")
    if declared.get("approved") != actual_approved:
        errors.append(f"counts.approved {declared.get('approved')} != actual {actual_approved}")
    for key, val in (("keep", "KEEP"), ("revise", "REVISE"), ("reject", "REJECT")):
        actual = sum(1 for i in items if i.get("review_decision") == val)
        if declared.get(key) != actual:
            errors.append(f"counts.{key} {declared.get(key)} != actual {actual}")

    return errors


def validate_history(history_lines: list[str], record: dict) -> list[str]:
    """Validate the append-only review history against the review record."""
    errors: list[str] = []
    events: list[tuple[int, dict]] = []
    for n, line in enumerate(history_lines, start=1):
        line = line.strip()
        if not line:
            continue
        try:
            events.append((n, json.loads(line)))
        except json.JSONDecodeError:
            errors.append(f"history line {n}: not valid JSON")
    if not events:
        errors.append("history log is empty; it must at least record initialisation")
        return errors
    if events[0][1].get("event") != "review_log_initialised":
        errors.append("history log must open with a review_log_initialised event")

    # Every item starts at PENDING
    replayed_state: dict[str, str] = {
        item.get("research_item_id"): "PENDING"
        for item in record.get("items", [])
        if "research_item_id" in item
    }
    seen_events_for_item: set[str] = set()

    for n, e in events:
        if e.get("event") == "review_decision":
            rid = e.get("research_item_id")
            for field in ("research_item_id", "previous_decision", "new_decision",
                          "timestamp", "version"):
                if field not in e:
                    errors.append(f"history line {n}: history event for {rid} lacks {field}")
            if e.get("new_decision") not in VALID_DECISIONS:
                errors.append(f"history line {n}: history event has invalid decision {e.get('new_decision')!r}")
            if e.get("new_decision") in {"KEEP", "REVISE", "REJECT"} and not (
                    e.get("reviewer_id") or e.get("reviewer_role")):
                errors.append(f"history line {n}: history event for {rid} lacks a reviewer")

            current = replayed_state.get(rid, "PENDING")
            prev = e.get("previous_decision")
            if prev != current:
                errors.append(
                    f"history line {n}: {rid} previous_decision {prev!r} does not match replayed state {current!r}"
                )

            if rid:
                replayed_state[rid] = e.get("new_decision")
                seen_events_for_item.add(rid)

    # After replay, each item's review_decision in phase7e_review.json must equal its replayed state
    for item in record.get("items", []):
        rid = item.get("research_item_id")
        actual = item.get("review_decision")
        expected = replayed_state.get(rid, "PENDING")
        if actual != expected:
            if actual != "PENDING" and rid not in seen_events_for_item:
                errors.append(
                    f"{rid}: decided as {actual} but no history event records it"
                )
            else:
                errors.append(
                    f"{rid}: review_decision {actual!r} does not match replayed history state {expected!r}"
                )
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    path = root / "results" / "dataset_audit" / "phase7e_review.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    errors = validate(record)
    history = root / "results" / "dataset_audit" / "phase7e_review_history.jsonl"
    if history.exists():
        errors += validate_history(history.read_text(encoding="utf-8").splitlines(), record)
    else:
        errors.append("missing results/dataset_audit/phase7e_review_history.jsonl")
    if errors:
        print(f"INVALID — {len(errors)} violation(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"VALID — {len(record['items'])} items, "
          f"{record['counts']['pending']} pending, {record['counts']['approved']} approved")
    return 0


if __name__ == "__main__":
    sys.exit(main())
