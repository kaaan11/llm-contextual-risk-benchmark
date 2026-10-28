#!/usr/bin/env python3
"""Phase 7G — QC record validator.

Importable as ``validate(qc, blind, key) -> list[str]`` so the invariants can be
exercised against synthetic violations rather than only against the current
(all-PENDING) state.

Performs no network access and calls no model API.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from apply_phase7g_annotations import (
        blind_item_eligible_for_context,
        keep_gate_blockers,
    )
except ImportError:  # pragma: no cover - package-style import fallback
    from scripts.apply_phase7g_annotations import (
        blind_item_eligible_for_context,
        keep_gate_blockers,
    )

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "results" / "dataset_audit"

DECISIONS = {"PENDING", "KEEP", "REVISE", "REJECT"}
VALENCE_SCALE = {"clearly_benign", "probably_benign", "ambiguous_dual_use",
                 "probably_concerning", "clearly_concerning"}
TRISTATE = {"true", "false", "unclear", None}
NATURALNESS = {"high", "medium", "low", None}

# Content the blind packet must never contain.
BLIND_FORBIDDEN = (
    "RI-DU", "RI-AM", "RI-NB", "RI-NH",
    "dual_use_nonnull", "null_benign", "null_highrisk", "persistent_ambiguity",
    "isolated_prompt_target_valence", "expected_risk_profile",
    "legitimating_context_intent", "incriminating_context_intent",
    "full_context_legitimating", "full_context_incriminating",
    "neutral_filler_control", "d_control_rationale", "context_mechanism",
)


def validate_blind(blind: dict) -> list[str]:
    errors: list[str] = []
    items = blind.get("items", [])
    if len(items) != 50:
        errors.append(f"blind packet must hold 50 items, found {len(items)}")

    ids = [i.get("blind_id") for i in items]
    if len(set(ids)) != len(ids):
        errors.append("duplicate blind_id values")

    # The packet must not leak design information, except inside the declared
    # blinding policy block.
    scrubbed = dict(blind)
    scrubbed.pop("blinding", None)
    blob = json.dumps(scrubbed)
    for term in BLIND_FORBIDDEN:
        if term in blob:
            errors.append(f"blind packet leaks design information: {term!r}")

    for item in items:
        bid = item.get("blind_id", "<unknown>")
        core = {"blind_id", "batch", "canonical_final_prompt", "rater_a",
                "rater_b", "adjudicated_valence", "adjudication_rationale",
                "annotation_status", "gate_result", "gate_flag"}
        # Optional presentation-session tracking, added by the blinding-integrity
        # patch so an anchored presentation can be recorded without becoming an
        # annotation. Carries no design information. `adjudicated_by` records who
        # resolved a two-rater disagreement (two-rater mandate, finding F-06).
        optional = {"presentation_sessions", "requires_fresh_presentation_session",
                    "accepted_in_session", "adjudicated_by"}
        unknown = set(item) - core - optional
        if unknown:
            errors.append(f"{bid}: unexpected field in blind packet item: {sorted(unknown)}")
        if not core.issubset(item):
            errors.append(f"{bid}: missing core field(s): {sorted(core - set(item))}")
        # An invalidated session must not have produced an annotation.
        for session in item.get("presentation_sessions", []):
            if session.get("review_session_invalidated") and session.get("annotation_accepted"):
                errors.append(f"{bid}: invalidated session marked as annotation_accepted")
            if session.get("review_session_invalidated") and any(
                    item[r]["isolated_prompt_valence_observed"] is not None
                    for r in ("rater_a", "rater_b")):
                if item.get("requires_fresh_presentation_session"):
                    errors.append(
                        f"{bid}: annotation exists although a fresh presentation session "
                        f"is still required after invalidation")
        for rater in ("rater_a", "rater_b"):
            v = item[rater]["isolated_prompt_valence_observed"]
            if v is not None and v not in VALENCE_SCALE:
                errors.append(f"{bid}/{rater}: invalid valence {v!r}")
            if v is not None and not (item[rater]["reviewer_id"]
                                      or item[rater]["reviewer_role"]):
                errors.append(f"{bid}/{rater}: annotation without a reviewer")
            if v is not None and not item[rater]["annotated_at"]:
                errors.append(f"{bid}/{rater}: annotation without a timestamp")
            if v is None and item[rater]["reviewer_id"]:
                errors.append(f"{bid}/{rater}: reviewer set without an annotation")
        if item["adjudicated_valence"] and item["adjudicated_valence"] not in VALENCE_SCALE:
            errors.append(f"{bid}: invalid adjudicated_valence")
        if item["gate_result"] and not item["adjudicated_valence"]:
            errors.append(f"{bid}: gate_result set before adjudication")

    # An accepted annotation must be attributed to a non-invalidated session.
    for item in items:
        sess_no = item.get("accepted_in_session")
        if sess_no is None:
            continue
        sess = next((s for s in item.get("presentation_sessions", [])
                     if s.get("session") == sess_no), None)
        if sess is None:
            errors.append(f"{item['blind_id']}: accepted_in_session {sess_no} has no session record")
        elif sess.get("review_session_invalidated"):
            errors.append(f"{item['blind_id']}: annotation attributed to an invalidated session")

    # Two-rater mandate (finding F-06): where reviewer identity is available, the
    # same reviewer may not occupy both rater slots of one item. Where identities
    # are anonymous (role-only), independence stays a documented process-level
    # requirement and is NOT claimed as technically enforced here.
    for item in items:
        ida = item["rater_a"].get("reviewer_id")
        idb = item["rater_b"].get("reviewer_id")
        if ida and idb and ida == idb:
            errors.append(f"{item['blind_id']}: same reviewer_id on both rater slots "
                          f"— independence violated")

    # Status/evidence consistency: a status of ADJUDICATED without the complete
    # two-rater evidence (proven slots with different persistent identities,
    # agreement or recorded adjudication) is a forged or corrupt record and
    # must fail closed here, not only at phase completion.
    for item in items:
        if item.get("annotation_status") == "ADJUDICATED":
            eligible, reason = blind_item_eligible_for_context(item)
            if not eligible:
                errors.append(f"{item['blind_id']}: status ADJUDICATED without "
                              f"complete two-rater evidence ({reason})")

    proto = blind.get("two_rater_protocol", {})
    if proto.get("inter_rater_status") == "not_available":
        if proto.get("percent_agreement") is not None or proto.get("cohens_kappa") is not None:
            errors.append("agreement statistics reported while inter_rater_status "
                          "is not_available — fabricated statistics")
    return errors


def validate(qc: dict, blind: dict, key: dict) -> list[str]:
    errors: list[str] = []
    items = qc.get("items", [])
    if len(items) != 50:
        errors.append(f"expected 50 QC items, found {len(items)}")

    if qc.get("auto_approval_performed"):
        errors.append("auto_approval_performed must be false")
    if qc.get("model_evaluation_performed"):
        errors.append("model_evaluation_performed must be false in Phase 7G")

    blind_by_id = {}
    keymap = {m["research_item_id"]: m["blind_id"] for m in key.get("mapping", [])}
    keycat = {m["research_item_id"]: m.get("category") for m in key.get("mapping", [])}
    for item in blind.get("items", []):
        blind_by_id[item["blind_id"]] = item

    for item in items:
        rid = item.get("research_item_id", "<unknown>")
        decision = item.get("review_decision")
        qc_flag = item.get("researcher_qc")

        if decision not in DECISIONS:
            errors.append(f"{rid}: invalid review_decision {decision!r}")
        if item.get("stimulus_review_status") not in DECISIONS:
            errors.append(f"{rid}: invalid stimulus_review_status")

        # --- approval invariants -------------------------------------------
        if qc_flag:
            if decision != "KEEP":
                errors.append(f"{rid}: researcher_qc true but decision is {decision!r}")
            if not (item.get("reviewer_id") or item.get("reviewer_role")):
                errors.append(f"{rid}: approved without a recorded reviewer")
            if not item.get("review_timestamp"):
                errors.append(f"{rid}: approved without a timestamp")
            if not item["structural_verification"]["passes"]:
                errors.append(f"{rid}: approved despite CRITICAL_STRUCTURAL_FAIL")
            if item["safety_review"]["safety_status"] == "FAIL":
                errors.append(f"{rid}: approved despite safety_status FAIL")
            for section in ("context_review", "safety_review", "naturalness_review"):
                if item[section]["status"] != "COMPLETE":
                    errors.append(f"{rid}: approved with incomplete {section}")
            bid = keymap.get(rid)
            bitem = blind_by_id.get(bid) if bid else None
            for blocker in keep_gate_blockers(bitem, keycat.get(rid)):
                if blocker == "blind_isolated_prompt_review":
                    errors.append(f"{rid}: approved without a blind isolated-prompt annotation")
                elif blocker == "isolated gate FAIL is never waived":
                    errors.append(
                        f"{rid}: approved despite isolated blind gate FAIL — "
                        f"a FAIL is never waived")
                elif blocker.startswith("two-rater mandate"):
                    # Two-rater mandate (finding F-06): one-rater PARTIAL states,
                    # unresolved disagreements and missing provenance cannot
                    # satisfy the final gate.
                    errors.append(
                        f"{rid}: approved while the blind record lacks complete "
                        f"two-rater evidence ({blocker}); two independent "
                        f"ratings with different reviewer identities plus "
                        f"agreement/adjudication (status ADJUDICATED) are required")
                else:
                    errors.append(
                        f"{rid}: approved with an unverifiable blind gate "
                        f"({blocker})")

        if decision in {"REVISE", "REJECT"} and qc_flag:
            errors.append(f"{rid}: {decision} item must not have researcher_qc true")
        if decision == "REVISE" and not item.get("revision_request"):
            errors.append(f"{rid}: REVISE requires a revision_request record")
        if decision == "REJECT" and not item.get("rejection_reason"):
            errors.append(f"{rid}: REJECT requires a recorded reason")
        if decision in {"KEEP", "REVISE", "REJECT"}:
            if not (item.get("reviewer_id") or item.get("reviewer_role")):
                errors.append(f"{rid}: decision {decision} without a reviewer")
            if not item.get("review_timestamp"):
                errors.append(f"{rid}: decision {decision} without a timestamp")
        if decision == "PENDING":
            if qc_flag:
                errors.append(f"{rid}: PENDING item must not be researcher_qc true")
            if item.get("review_timestamp"):
                errors.append(f"{rid}: PENDING item has a review_timestamp")

        # --- blind ordering --------------------------------------------------
        # Any opened context review (beyond NOT_STARTED) requires the full
        # two-rater evidence on the loaded blind record — PENDING, PARTIAL,
        # unresolved disagreement, missing provenance and same-identity slots
        # are all reported, so a state the writer could never produce is
        # caught fail-closed on load.
        bid = keymap.get(rid)
        if item["context_review"]["status"] != "NOT_STARTED":
            bitem = blind_by_id.get(bid) if bid else None
            if bitem is None:
                errors.append(f"{rid}: context review recorded without a blind "
                              f"mapping; context must not be revealed before "
                              f"the blind isolated-prompt annotation")
            else:
                eligible, reason = blind_item_eligible_for_context(bitem)
                if not eligible:
                    errors.append(f"{rid}: context review recorded without complete "
                                  f"blind evidence ({reason}); context must not be "
                                  f"revealed before the blind isolated-prompt "
                                  f"annotation is complete")

        # --- vocabulary ------------------------------------------------------
        for section in ("context_relevance", "context_direction",
                        "context_resolution", "context_leakage"):
            for field, value in item["context_review"][section].items():
                if value not in TRISTATE:
                    errors.append(f"{rid}.{field}: invalid tristate {value!r}")
                if value in {"true", "unclear"} and not item["context_review"][
                        "notes"].get(field):
                    errors.append(f"{rid}.{field}={value} requires a note")
        if item["naturalness_review"]["naturalness"] not in NATURALNESS:
            errors.append(f"{rid}: invalid naturalness value")
        if item["safety_review"]["safety_status"] not in {None, "PASS", "FAIL"}:
            errors.append(f"{rid}: invalid safety_status")

        # --- versioning ------------------------------------------------------
        versions = item.get("versions", [])
        if not versions or versions[0]["stimulus_version"] != 1:
            errors.append(f"{rid}: stimulus version 1 must be preserved")
        for v in versions[1:]:
            if not v.get("revision_reason"):
                errors.append(f"{rid}: version {v.get('stimulus_version')} lacks a reason")
        for flag in item.get("quality_flags", []):
            if flag not in set(qc.get("allowed_quality_flags", [])):
                errors.append(f"{rid}: unknown quality flag {flag!r}")

    # --- declared counts must match reality ---------------------------------
    c = qc.get("counts", {})
    for k, v in (("pending", "PENDING"), ("keep", "KEEP"),
                 ("revise", "REVISE"), ("reject", "REJECT")):
        actual = sum(1 for i in items if i.get("review_decision") == v)
        if c.get(k) != actual:
            errors.append(f"counts.{k} {c.get(k)} != actual {actual}")
    actual_qc = sum(1 for i in items if i.get("researcher_qc"))
    if c.get("researcher_qc_true") != actual_qc:
        errors.append(f"counts.researcher_qc_true {c.get('researcher_qc_true')} "
                      f"!= actual {actual_qc}")
    if qc.get("phase_complete") != (c.get("pending") == 0):
        errors.append("phase_complete does not match the pending count")

    # Two-rater mandate (AGENTS.md R2): the phase can only be complete when
    # every blind record carries complete two-rater evidence — two filled and
    # different persistent human identities, two ratings with timestamps, and
    # agreement or a recorded adjudication. The check is independent of the
    # final decision type (KEEP, REVISE or REJECT all pass through it) and
    # never trusts the status field alone.
    if qc.get("phase_complete"):
        unproven = []
        for i in blind.get("items", []):
            eligible, _reason = blind_item_eligible_for_context(i)
            if not eligible:
                unproven.append(i["blind_id"])
        if unproven:
            errors.append(
                f"phase_complete while {len(unproven)} blind records are not "
                f"ADJUDICATED with complete two-rater evidence "
                f"(two-rater mandate): {unproven[:5]}…")

    return errors


def validate_summary(qc: dict, blind: dict, summary: dict) -> list[str]:
    """F-03 invariant: generated roll-ups must equal a deterministic derivation
    from the canonical live records. Contradictory progress counts are errors."""
    errors: list[str] = []
    items = qc.get("items", [])
    annotated = sum(1 for i in blind.get("items", [])
                    if i["annotation_status"] != "PENDING")
    ipr = summary.get("isolated_prompt_review", {})
    if ipr.get("annotations_submitted") != annotated:
        errors.append("summary.isolated_prompt_review.annotations_submitted "
                      f"{ipr.get('annotations_submitted')} != live {annotated}")
    dist = {}
    for i in blind.get("items", []):
        for rater in ("rater_a", "rater_b"):
            v = i[rater].get("isolated_prompt_valence_observed")
            if v:
                dist[v] = dist.get(v, 0) + 1
    reported = ipr.get("valence_distribution", {})
    for v in set(reported) | set(dist):
        if reported.get(v, 0) != dist.get(v, 0):
            errors.append(f"summary valence_distribution[{v}] "
                          f"{reported.get(v, 0)} != live {dist.get(v, 0)}")
    proto = blind.get("two_rater_protocol", {})
    irs = summary.get("inter_rater", {})
    if irs.get("raters_supplied") != proto.get("raters_supplied"):
        errors.append("summary.inter_rater.raters_supplied differs from the blind packet")
    if irs.get("inter_rater_status") != proto.get("inter_rater_status"):
        errors.append("summary.inter_rater.inter_rater_status differs from the blind packet")
    totals = summary.get("totals", {})
    c = qc.get("counts", {})
    for key in ("total_items", "keep", "revise", "reject", "pending", "researcher_approved"):
        mapped = {"total_items": "total", "researcher_approved": "researcher_qc_true"}.get(key, key)
        want = c.get(mapped)
        if totals.get(key) != want:
            errors.append(f"summary.totals.{key} {totals.get(key)} != counts.{mapped} {want}")
    if summary.get("phase_complete") != qc.get("phase_complete"):
        errors.append("summary.phase_complete differs from the QC record")
    return errors


def validate_history(history_lines: list[str], qc: dict) -> list[str]:
    """Validate the append-only review history against the Phase 7G human QC record."""
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

    # Every item starts at PENDING
    replayed_state: dict[str, str] = {
        item.get("research_item_id"): "PENDING"
        for item in qc.get("items", [])
        if "research_item_id" in item
    }
    seen_events_for_item: set[str] = set()

    for n, e in events:
        event_type = e.get("event")
        if event_type == "review_reinitialised":
            # A logged reinit resets every item; earlier decisions stay in the backup.
            replayed_state = {rid: "PENDING" for rid in replayed_state}
            seen_events_for_item.clear()
        elif event_type == "review_decision":
            rid = e.get("research_item_id")
            for field in ("research_item_id", "previous_decision", "new_decision", "timestamp"):
                if field not in e:
                    errors.append(f"history line {n}: history event for {rid} lacks {field}")
            if e.get("new_decision") not in DECISIONS:
                errors.append(f"history line {n}: history event has invalid decision {e.get('new_decision')!r}")

            current = replayed_state.get(rid, "PENDING")
            prev = e.get("previous_decision")
            if prev != current:
                errors.append(
                    f"history line {n}: {rid} previous_decision {prev!r} does not match replayed state {current!r}"
                )

            if rid:
                replayed_state[rid] = e.get("new_decision")
                seen_events_for_item.add(rid)

    # After replay, each item's review_decision in phase7g_human_qc.json must equal its replayed state
    for item in qc.get("items", []):
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
    qc = json.loads((AUDIT / "phase7g_human_qc.json").read_text(encoding="utf-8"))
    blind = json.loads((AUDIT / "phase7g_blind_review.json").read_text(encoding="utf-8"))
    key = json.loads((AUDIT / "phase7g_blind_key.json").read_text(encoding="utf-8"))

    errors = validate_blind(blind) + validate(qc, blind, key)

    history_path = AUDIT / "phase7g_review_history.jsonl"
    if history_path.exists():
        errors.extend(validate_history(history_path.read_text(encoding="utf-8").splitlines(), qc))
    else:
        errors.append(f"missing {history_path}")

    # F-03: the generated roll-up must agree with the canonical live records.
    summary_path = AUDIT / "phase7g_quality_summary.json"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        errors.extend(validate_summary(qc, blind, summary))

    if errors:
        print(f"INVALID — {len(errors)} violation(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    c = qc["counts"]
    print(f"VALID — {c['total']} items | pending={c['pending']} keep={c['keep']} "
          f"revise={c['revise']} reject={c['reject']} approved={c['researcher_qc_true']}")
    print(f"phase_complete={qc['phase_complete']} | "
          f"inter_rater={blind['two_rater_protocol']['inter_rater_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
