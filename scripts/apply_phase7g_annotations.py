#!/usr/bin/env python3
"""Phase 7G — record human QC annotations and decisions.

Transcribes annotations a human actually supplied. It never infers a valence,
a context judgement, a safety verdict or a review decision, and never invents a
reviewer identity.

The tool enforces the blind ordering from the phase brief section 19: the
context/safety/naturalness review for an item is REFUSED until that item's blind
isolated-prompt annotation has been submitted. A final decision is refused until
the earlier steps exist.

Subcommands
-----------
  blind       record isolated-prompt valence (step 1-2)
  context     record full-context, safety, naturalness review (steps 3-6)
  decide      record the final researcher decision (step 7)
  adjudicate  resolve a two-rater disagreement into the adjudicated valence

Two-rater mandate (researcher decision R2, remediating audit finding F-06): a
research item can only reach the final KEEP gate when its blind isolated-prompt
annotation is ADJUDICATED — i.e. both independent raters submitted and either
agreed or the disagreement was resolved through this tool's recorded
`adjudicate` flow. One-rater completion is not possible.

Every subcommand requires --reviewer-id or --reviewer-role and --timestamp, and
appends to the append-only history log after snapshotting the prior state.

Performs no network access and calls no model API.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "results" / "dataset_audit"
BLIND = AUDIT / "phase7g_blind_review.json"
KEY = AUDIT / "phase7g_blind_key.json"
QC = AUDIT / "phase7g_human_qc.json"
HISTORY = AUDIT / "phase7g_review_history.jsonl"
SNAPS = AUDIT / "snapshots"

VALENCE_SCALE = ["clearly_benign", "probably_benign", "ambiguous_dual_use",
                 "probably_concerning", "clearly_concerning"]
CONFIDENCE = ["low", "medium", "high"]
TRISTATE = {"true", "false", "unclear"}
NATURALNESS = {"high", "medium", "low"}
SAFETY_STATUS = {"PASS", "FAIL"}
DECISIONS = {"PENDING", "KEEP", "REVISE", "REJECT"}

GATE_TARGET = {
    "dual_use_nonnull": "ambiguous_dual_use",
    "persistent_ambiguity": "ambiguous_dual_use",
    "null_benign": "clearly_benign",
    "null_highrisk": "clearly_concerning",
}


class QCError(RuntimeError):
    pass


def _load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _require_reviewer(reviewer_id, reviewer_role):
    if not (reviewer_id or reviewer_role):
        raise QCError("reviewer identity is required and must be supplied by the human")


def evaluate_gate(category: str, valence: str) -> tuple[str, str | None]:
    """Compare an adjudicated valence to the design target. Never rewrites the item."""
    target = GATE_TARGET[category]
    if valence == target:
        return "PASS", None
    if category in {"dual_use_nonnull", "persistent_ambiguity"}:
        if valence in {"clearly_benign", "clearly_concerning"}:
            return "FAIL", "ISOLATED_VALENCE_GATE_FAIL"
        return "REVIEW", "ISOLATED_VALENCE_GATE_REVIEW"
    if category == "null_benign":
        if valence == "probably_benign":
            return "PASS", None
        return "FAIL", "ISOLATED_VALENCE_GATE_FAIL"
    if category == "null_highrisk":
        if valence == "probably_concerning":
            return "PASS", None
        return "FAIL", "ISOLATED_VALENCE_GATE_FAIL"
    return "REVIEW", "ISOLATED_VALENCE_GATE_REVIEW"


def record_blind(blind: dict, key: dict, entries: list[dict],
                 reviewer_id, reviewer_role, timestamp) -> list[dict]:
    _require_reviewer(reviewer_id, reviewer_role)
    by_blind = {i["blind_id"]: i for i in blind["items"]}
    keymap = {m["blind_id"]: m for m in key["mapping"]}
    events = []

    for e in entries:
        bid, rater = e["blind_id"], e["rater"]
        if bid not in by_blind:
            raise QCError(f"unknown blind_id {bid}")
        if rater not in {"rater_a", "rater_b"}:
            raise QCError(f"rater must be rater_a or rater_b, got {rater!r}")
        if e["valence"] not in VALENCE_SCALE:
            raise QCError(f"{bid}: invalid valence {e['valence']!r}")
        if e["confidence"] not in CONFIDENCE:
            raise QCError(f"{bid}: invalid confidence {e['confidence']!r}")

        item = by_blind[bid]
        if item.get("requires_fresh_presentation_session"):
            raise QCError(
                f"{bid}: the last presentation of this item was invalidated "
                f"(anchored/contaminated interface). A fresh presentation session is "
                f"required before any annotation may be accepted. A response given after "
                f"the contaminated presentation must not be reused. Refused.")
        if item[rater]["isolated_prompt_valence_observed"] is not None:
            raise QCError(f"{bid}/{rater}: already annotated at "
                          f"{item[rater]['annotated_at']}; re-annotation is a conflict")

        # Rater independence (F-06): when reviewer identity is available it must
        # differ across the two rater slots of the same item. Where the protocol
        # operates with anonymous roles only, independence remains a process-level
        # requirement and cannot be technically proven from metadata.
        other = "rater_b" if rater == "rater_a" else "rater_a"
        if reviewer_id and item[other].get("reviewer_id") == reviewer_id:
            raise QCError(
                f"{bid}: reviewer_id {reviewer_id!r} already annotated this item as "
                f"{other}; the two ratings must come from two independent raters. Refused.")

        item[rater].update(
            reviewer_id=reviewer_id, reviewer_role=reviewer_role,
            isolated_prompt_valence_observed=e["valence"],
            reviewer_confidence=e["confidence"],
            reviewer_notes=e.get("notes"), annotated_at=timestamp)

        a = item["rater_a"]["isolated_prompt_valence_observed"]
        b = item["rater_b"]["isolated_prompt_valence_observed"]
        if a and b:
            if a == b:
                item["adjudicated_valence"] = a
                item["adjudication_rationale"] = "both raters agreed"
                item["annotation_status"] = "ADJUDICATED"
            else:
                item["annotation_status"] = "DISAGREEMENT_PENDING_ADJUDICATION"
        elif a or b:
            item["annotation_status"] = "PARTIAL_ONE_RATER"

        if item["adjudicated_valence"]:
            cat = keymap[bid]["category"]
            result, flag = evaluate_gate(cat, item["adjudicated_valence"])
            item["gate_result"] = result
            item["gate_flag"] = flag

        events.append({
            "event": "blind_annotation", "blind_id": bid, "rater": rater,
            "valence": e["valence"], "confidence": e["confidence"],
            "notes": e.get("notes"), "reviewer_id": reviewer_id,
            "reviewer_role": reviewer_role, "timestamp": timestamp,
            "annotation_status": item["annotation_status"],
            "gate_result": item["gate_result"],
        })

    refresh_blind_stats(blind)
    return events


def refresh_blind_stats(blind: dict) -> None:
    items = blind["items"]
    a_vals = {i["blind_id"]: i["rater_a"]["isolated_prompt_valence_observed"] for i in items}
    b_vals = {i["blind_id"]: i["rater_b"]["isolated_prompt_valence_observed"] for i in items}
    both = [k for k in a_vals if a_vals[k] and b_vals[k]]

    proto = blind["two_rater_protocol"]
    raters = set()
    for i in items:
        for r in ("rater_a", "rater_b"):
            if i[r]["isolated_prompt_valence_observed"] is not None:
                raters.add(r)
    proto["raters_supplied"] = len(raters)

    if len(both) == 0 or len(raters) < 2:
        proto["inter_rater_status"] = "not_available"
        proto["percent_agreement"] = None
        proto["cohens_kappa"] = None
    else:
        agree = sum(1 for k in both if a_vals[k] == b_vals[k])
        po = agree / len(both)
        cats = set(VALENCE_SCALE)
        pe = sum(
            (sum(1 for k in both if a_vals[k] == c) / len(both))
            * (sum(1 for k in both if b_vals[k] == c) / len(both))
            for c in cats)
        proto["inter_rater_status"] = "available"
        proto["percent_agreement"] = round(po, 4)
        proto["cohens_kappa"] = (None if pe == 1 else round((po - pe) / (1 - pe), 4))
        proto["n_double_annotated"] = len(both)

    submitted = sum(1 for i in items if i["annotation_status"] != "PENDING")
    blind["status"] = ("BLIND_ANNOTATION_COMPLETE"
                       if all(i["annotation_status"] in
                              {"ADJUDICATED", "PARTIAL_ONE_RATER"} for i in items)
                       and submitted == len(items)
                       else ("BLIND_ANNOTATION_IN_PROGRESS" if submitted
                             else "AWAITING_BLIND_ANNOTATION"))


def _blind_submitted_for(blind: dict, key: dict, rid: str) -> bool:
    return _blind_status_for(blind, key, rid) != "PENDING"


def _blind_status_for(blind: dict, key: dict, rid: str) -> str:
    bid = next(m["blind_id"] for m in key["mapping"] if m["research_item_id"] == rid)
    item = next(i for i in blind["items"] if i["blind_id"] == bid)
    return item["annotation_status"]


def record_adjudication(blind: dict, key: dict, entries: list[dict],
                        reviewer_id, reviewer_role, timestamp) -> list[dict]:
    """Resolve a recorded two-rater disagreement (annotation protocol section 4.3).

    Requires both raters to have annotated and the item to sit in
    DISAGREEMENT_PENDING_ADJUDICATION. The adjudicator identity is required and is
    never invented; a written rationale is mandatory. Nothing is auto-chosen.
    """
    _require_reviewer(reviewer_id, reviewer_role)
    by_blind = {i["blind_id"]: i for i in blind["items"]}
    keymap = {m["blind_id"]: m for m in key["mapping"]}
    events = []
    for e in entries:
        bid = e["blind_id"]
        if bid not in by_blind:
            raise QCError(f"unknown blind_id {bid}")
        valence = e.get("adjudicated_valence")
        if valence not in VALENCE_SCALE:
            raise QCError(f"{bid}: invalid adjudicated_valence {valence!r}")
        rationale = e.get("rationale")
        if not rationale:
            raise QCError(f"{bid}: an adjudication requires a written rationale")
        item = by_blind[bid]
        if item["annotation_status"] == "ADJUDICATED":
            raise QCError(f"{bid}: already ADJUDICATED; re-adjudication is a conflict")
        a = item["rater_a"]["isolated_prompt_valence_observed"]
        b = item["rater_b"]["isolated_prompt_valence_observed"]
        if not (a and b):
            raise QCError(
                f"{bid}: adjudication requires two submitted blind ratings "
                f"(two-rater mandate); rater_a={a!r}, rater_b={b!r}. Refused.")
        if a == b:
            raise QCError(
                f"{bid}: raters agree ({a!r}); the recorded agreement already "
                f"constitutes the adjudication. Refused.")
        item["adjudicated_valence"] = valence
        item["adjudication_rationale"] = rationale
        item["adjudicated_by"] = {"reviewer_id": reviewer_id,
                                  "reviewer_role": reviewer_role,
                                  "adjudicated_at": timestamp}
        item["annotation_status"] = "ADJUDICATED"
        result, flag = evaluate_gate(keymap[bid]["category"], item["adjudicated_valence"])
        item["gate_result"] = result
        item["gate_flag"] = flag
        refresh_blind_stats(blind)
        events.append({
            "event": "blind_adjudication", "blind_id": bid,
            "valence_rater_a": a, "valence_rater_b": b,
            "adjudicated_valence": valence, "rationale": rationale,
            "reviewer_id": reviewer_id, "reviewer_role": reviewer_role,
            "timestamp": timestamp, "gate_result": result, "gate_flag": flag,
        })
    return events


def record_context(qc: dict, blind: dict, key: dict, payloads: list[dict],
                   reviewer_id, reviewer_role, timestamp) -> list[dict]:
    """Steps 3-6. Refused until the item's blind annotation exists."""
    _require_reviewer(reviewer_id, reviewer_role)
    by_id = {i["research_item_id"]: i for i in qc["items"]}
    events = []

    for p in payloads:
        rid = p["research_item_id"]
        if rid not in by_id:
            raise QCError(f"unknown research_item_id {rid}")
        if not _blind_submitted_for(blind, key, rid):
            raise QCError(
                f"{rid}: blind isolated-prompt annotation has not been submitted. "
                f"Revealing B/C/D context first would break the blind ordering "
                f"(phase brief section 19). Refused.")

        item = by_id[rid]
        for section, values in (("context_relevance", p.get("context_relevance", {})),
                                ("context_direction", p.get("context_direction", {})),
                                ("context_resolution", p.get("context_resolution", {})),
                                ("context_leakage", p.get("context_leakage", {}))):
            for field, value in values.items():
                if field not in item["context_review"][section]:
                    raise QCError(f"{rid}: unknown {section} field {field!r}")
                if value not in TRISTATE:
                    raise QCError(f"{rid}.{field}: must be one of {sorted(TRISTATE)}")
                if value in {"true", "unclear"} and not p.get("notes", {}).get(field):
                    raise QCError(f"{rid}.{field}={value} requires a note")
                item["context_review"][section][field] = value
        item["context_review"]["notes"].update(p.get("notes", {}))
        item["context_review"]["status"] = "COMPLETE"

        if "naturalness" in p:
            if p["naturalness"] not in NATURALNESS:
                raise QCError(f"{rid}: naturalness must be high/medium/low")
            if p["naturalness"] == "low" and not p.get("naturalness_notes"):
                raise QCError(f"{rid}: naturalness=low requires notes")
            item["naturalness_review"].update(
                status="COMPLETE", naturalness=p["naturalness"],
                naturalness_notes=p.get("naturalness_notes"))

        if "safety_status" in p:
            if p["safety_status"] not in SAFETY_STATUS:
                raise QCError(f"{rid}: safety_status must be PASS or FAIL")
            if p["safety_status"] == "FAIL" and not p.get("safety_notes"):
                raise QCError(f"{rid}: safety_status=FAIL requires notes")
            item["safety_review"].update(
                status="COMPLETE", safety_status=p["safety_status"],
                intent_level_only_confirmed=p.get("intent_level_only_confirmed"),
                notes=p.get("safety_notes"))

        item["reviewer_id"] = reviewer_id
        item["reviewer_role"] = reviewer_role
        recompute_flags(item)
        events.append({"event": "context_review", "research_item_id": rid,
                       "reviewer_id": reviewer_id, "reviewer_role": reviewer_role,
                       "timestamp": timestamp, "flags": item["quality_flags"]})

    refresh_qc_counts(qc)
    return events


def recompute_flags(item: dict) -> None:
    flags = set(item.get("quality_flags", []))
    cr = item["context_review"]
    if cr["context_relevance"]["context_is_material"] == "false":
        flags.add("CONTEXT_NOT_MATERIAL")
    if cr["context_relevance"]["context_is_realistic"] == "false":
        flags.add("CONTEXT_ARTIFICIAL")
    if cr["context_leakage"]["context_contains_artificial_disclaimer"] == "true":
        flags.add("CONTEXT_ARTIFICIAL")
    for f in ("final_prompt_contains_context_signal", "context_reveals_research_hypothesis",
              "context_contains_unnecessary_risk_language"):
        if cr["context_leakage"][f] == "true":
            flags.add("CONTEXT_LEAKAGE")
    if item["naturalness_review"]["naturalness"] == "low":
        flags.add("NATURALNESS_LOW")
    if item["safety_review"]["safety_status"] == "FAIL":
        flags.add("SAFETY_FAIL")
    if item["length_control_review"].get("d_control_contaminated") == "true":
        flags.add("D_CONTROL_CONTAMINATED")
    if not item["structural_verification"]["passes"]:
        flags.add("FINAL_PROMPT_MISMATCH")
    item["quality_flags"] = sorted(flags)


def record_decision(qc: dict, blind: dict, key: dict, decisions: list[dict],
                    reviewer_id, reviewer_role, timestamp) -> list[dict]:
    _require_reviewer(reviewer_id, reviewer_role)
    by_id = {i["research_item_id"]: i for i in qc["items"]}
    events = []

    for d in decisions:
        rid, decision = d["research_item_id"], d["decision"]
        if rid not in by_id:
            raise QCError(f"unknown research_item_id {rid}")
        if decision not in DECISIONS:
            raise QCError(f"{rid}: invalid decision {decision!r}")
        item = by_id[rid]

        if item["review_decision"] != "PENDING" and item["review_timestamp"]:
            raise QCError(f"{rid}: already decided as {item['review_decision']} at "
                          f"{item['review_timestamp']}; re-deciding is a conflict")

        if decision in {"REVISE", "REJECT"} and not d.get("notes"):
            raise QCError(f"{rid}: a {decision} decision requires a written reason")

        if decision == "KEEP":
            missing = []
            if item["context_review"]["status"] != "COMPLETE":
                missing.append("context_review")
            if item["safety_review"]["status"] != "COMPLETE":
                missing.append("safety_review")
            if item["naturalness_review"]["status"] != "COMPLETE":
                missing.append("naturalness_review")
            blind_status = _blind_status_for(blind, key, rid)
            if blind_status == "PENDING":
                missing.append("blind_isolated_prompt_review")
            elif blind_status != "ADJUDICATED":
                raise QCError(
                    f"{rid}: two-rater mandate — the blind isolated-prompt annotation is "
                    f"{blind_status}, not ADJUDICATED. KEEP requires two independent blind "
                    f"ratings that agree, or a recorded adjudication of their disagreement. "
                    f"Refused.")
            if not item["structural_verification"]["passes"]:
                raise QCError(f"{rid}: CRITICAL_STRUCTURAL_FAIL — cannot be approved")
            if item["safety_review"]["safety_status"] == "FAIL":
                raise QCError(f"{rid}: safety_status is FAIL — cannot be approved")
            if missing:
                raise QCError(f"{rid}: KEEP requires completed {missing}")
            item["researcher_qc"] = True
            item["stimulus_review_status"] = "KEEP"
        elif decision == "REVISE":
            item["researcher_qc"] = False
            item["stimulus_review_status"] = "REVISE"
            item["revision_request"] = {
                "previous_version": item["current_stimulus_version"],
                "new_version": item["current_stimulus_version"] + 1,
                "revision_reason": d["notes"],
                "revised_at": None,
                "revision_status": "pending_revision",
                "requires_blind_rereview_if_prompt_changes": True,
                "note": ("Stimulus version 1 is preserved. No replacement text is "
                         "generated automatically."),
            }
        else:
            item["researcher_qc"] = False
            item["stimulus_review_status"] = decision
            if decision == "REJECT":
                item["rejection_reason"] = d["notes"]
                item["rejected_at"] = timestamp

        previous = item["review_decision"]
        item["review_decision"] = decision
        item["decision_notes"] = d.get("notes")
        item["reviewer_id"] = reviewer_id
        item["reviewer_role"] = reviewer_role
        item["review_timestamp"] = timestamp
        item["suitable_for_model_evaluation"] = (decision == "KEEP")
        recompute_flags(item)

        events.append({"event": "review_decision", "research_item_id": rid,
                       "previous_decision": previous, "new_decision": decision,
                       "researcher_qc": item["researcher_qc"],
                       "reviewer_id": reviewer_id, "reviewer_role": reviewer_role,
                       "timestamp": timestamp, "notes": d.get("notes"),
                       "stimulus_version": item["current_stimulus_version"],
                       "quality_flags": item["quality_flags"]})

    refresh_qc_counts(qc)
    return events


def refresh_qc_counts(qc: dict) -> None:
    items = qc["items"]
    c = qc["counts"]
    c["total"] = len(items)
    for k, v in (("pending", "PENDING"), ("keep", "KEEP"),
                 ("revise", "REVISE"), ("reject", "REJECT")):
        c[k] = sum(1 for i in items if i["review_decision"] == v)
    c["researcher_qc_true"] = sum(1 for i in items if i["researcher_qc"])
    qc["phase_complete"] = c["pending"] == 0
    qc["decisions_supplied_by_researcher"] = c["pending"] < c["total"]
    qc["status"] = ("QC_COMPLETE" if c["pending"] == 0
                    else ("QC_IN_PROGRESS" if c["pending"] < c["total"]
                          else "AWAITING_HUMAN_QC"))


def append_history(events: list[dict]) -> None:
    with HISTORY.open("a", encoding="utf-8") as fh:
        for e in events:
            fh.write(json.dumps(e, ensure_ascii=False) + "\n")


def snapshot(paths: list[Path], stamp: str) -> None:
    SNAPS.mkdir(parents=True, exist_ok=True)
    for p in paths:
        dest = SNAPS / f"{p.stem}.{stamp.replace(':', '')}{p.suffix}"
        if dest.exists():
            raise QCError(f"snapshot {dest.name} already exists; refusing to overwrite")
        shutil.copy(p, dest)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=["blind", "context", "decide", "adjudicate"])
    ap.add_argument("--input", required=True, help="JSON file of human-supplied annotations")
    ap.add_argument("--reviewer-id", default=None)
    ap.add_argument("--reviewer-role", default=None)
    ap.add_argument("--timestamp", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    blind, key, qc = _load(BLIND), _load(KEY), _load(QC)

    try:
        if args.mode == "blind":
            events = record_blind(blind, key, payload, args.reviewer_id,
                                  args.reviewer_role, args.timestamp)
            targets = [BLIND]
        elif args.mode == "context":
            events = record_context(qc, blind, key, payload, args.reviewer_id,
                                    args.reviewer_role, args.timestamp)
            targets = [QC]
        elif args.mode == "adjudicate":
            events = record_adjudication(blind, key, payload, args.reviewer_id,
                                         args.reviewer_role, args.timestamp)
            targets = [BLIND]
        else:
            events = record_decision(qc, blind, key, payload, args.reviewer_id,
                                     args.reviewer_role, args.timestamp)
            targets = [QC]
    except QCError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"dry run: {len(events)} event(s) would be recorded; nothing written")
        return 0

    snapshot(targets, args.timestamp)
    if args.mode in {"blind", "adjudicate"}:
        BLIND.write_text(json.dumps(blind, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8")
    else:
        QC.write_text(json.dumps(qc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    append_history(events)
    print(f"recorded {len(events)} event(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
