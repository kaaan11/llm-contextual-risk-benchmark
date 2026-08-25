#!/usr/bin/env python3
"""Phase 7E — record the researcher's human review decisions.

This tool ONLY transcribes decisions a human has explicitly supplied. It never
infers, defaults to, or "helpfully" produces KEEP/REVISE/REJECT. Any item the
researcher does not mention stays PENDING with researcher_approved=false.

Input format (one decision per line)::

    RI-DU-001: KEEP
    RI-DU-002: REVISE — final prompt may still be too explicit
    RI-DU-004: REJECT — scenario is too artificial

The separator between the decision and the note may be an em dash, a hyphen or a
colon. Notes are stored **verbatim**: they are never reworded, summarised, or
turned into a decision.

Usage::

    python scripts/apply_phase7e_decisions.py --decisions FILE --reviewer-id "..." \
        [--reviewer-role "..."] [--timestamp 2026-08-14T12:00:00Z] [--dry-run]

Reviewer identity is REQUIRED and must be supplied by the human; it is never
invented. Performs no network access and calls no model API.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

VALID_DECISIONS = {"PENDING", "KEEP", "REVISE", "REJECT"}
TERMINAL_NEEDING_NOTE = {"REVISE", "REJECT"}

# "RI-XX-000" then a separator then the decision, optionally then a note.
LINE_RE = re.compile(
    r"^\s*(?P<id>RI-[A-Z]{2}-\d{3})\s*[:\-]\s*(?P<decision>[A-Za-z_]+)\s*(?P<rest>.*)$"
)
NOTE_SEP_RE = re.compile(r"^\s*(?:[—–\-:]\s*)?(?P<note>.*)$")


class DecisionError(RuntimeError):
    pass


def parse_decisions(text: str) -> list[dict]:
    """Parse researcher-supplied decision lines. Raises on anything ambiguous."""
    out: list[dict] = []
    seen: set[str] = set()
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = LINE_RE.match(line)
        if not m:
            raise DecisionError(f"line {lineno}: cannot parse decision line: {raw!r}")
        rid = m.group("id")
        decision = m.group("decision").strip().upper()
        if decision not in VALID_DECISIONS:
            raise DecisionError(
                f"line {lineno}: {rid}: invalid decision {decision!r}; "
                f"allowed: {sorted(VALID_DECISIONS)}"
            )
        note = NOTE_SEP_RE.match(m.group("rest")).group("note").strip() or None
        if decision in TERMINAL_NEEDING_NOTE and not note:
            raise DecisionError(
                f"line {lineno}: {rid}: a {decision} decision requires a written reason"
            )
        if rid in seen:
            raise DecisionError(f"line {lineno}: {rid}: duplicate decision for the same item")
        seen.add(rid)
        out.append({"research_item_id": rid, "decision": decision, "note": note})
    if not out:
        raise DecisionError("no decisions found in input")
    return out


def apply_decisions(record: dict, decisions: list[dict], reviewer_id: str | None,
                    reviewer_role: str | None, timestamp: str) -> list[dict]:
    """Mutate ``record`` in place. Returns the history events to append."""
    if not (reviewer_id or reviewer_role):
        raise DecisionError("reviewer identity is required and must be supplied by the human")

    by_id = {i["research_item_id"]: i for i in record["items"]}
    unknown = [d["research_item_id"] for d in decisions if d["research_item_id"] not in by_id]
    if unknown:
        raise DecisionError(f"unknown research_item_id(s): {unknown}")

    events: list[dict] = []
    for d in decisions:
        item = by_id[d["research_item_id"]]
        previous = item["review_decision"]
        decision = d["decision"]
        note = d["note"]

        if previous in {"KEEP", "REVISE", "REJECT"} and item.get("review_timestamp"):
            # A prior human decision exists. Overwriting it silently would destroy
            # review history, so require an explicit re-review path.
            raise DecisionError(
                f"{d['research_item_id']}: already decided as {previous} at "
                f"{item['review_timestamp']}. Re-reviewing an already-decided item is a "
                f"conflict; resolve it explicitly rather than overwriting."
            )

        item["review_decision"] = decision
        item["researcher_notes"] = note  # verbatim, never rewritten
        item["reviewer_id"] = reviewer_id
        item["reviewer_role"] = reviewer_role
        item["review_timestamp"] = timestamp

        if decision == "KEEP":
            # Structural validity is a precondition for approval.
            design = item["versions"][item["current_version"] - 1]["design"]
            missing = [f for f in (
                "research_item_id", "triplet_id", "category", "context_mechanism",
                "canonical_final_prompt_intent", "isolated_prompt_target_valence",
                "legitimating_context_intent", "incriminating_context_intent",
                "expected_context_effect", "expected_risk_profile",
                "intended_turn_count", "control_strategy", "safety_constraints",
            ) if design.get(f) in (None, "")]
            if missing:
                raise DecisionError(
                    f"{d['research_item_id']}: KEEP requested but design fields are "
                    f"missing/invalid: {missing}"
                )
            # An explicit KEEP is the researcher asserting the eight decision rules hold.
            for k in item["decision_rule_checklist"]:
                item["decision_rule_checklist"][k] = True
            item["researcher_approved"] = True
            item["revision_reason"] = None

        elif decision == "REVISE":
            item["researcher_approved"] = False
            item["revision_reason"] = note
            item["revision_status"] = "pending_revision"
            item["revision_required"] = True
            item["revision_request"] = {
                "original_version": item["current_version"],
                "revision_reason": note,
                "revision_status": "pending_revision",
                "requested_at": timestamp,
                "note": ("Version 1 is preserved. A revised version is NOT authored here; "
                         "it requires an explicit researcher instruction, and the revised "
                         "version must then be reviewed again before it can be approved."),
            }

        elif decision == "REJECT":
            item["researcher_approved"] = False
            item["rejection_reason"] = note
            item["rejected_at"] = timestamp
            item["revision_reason"] = None

        else:  # PENDING
            item["researcher_approved"] = False

        events.append({
            "event": "review_decision",
            "research_item_id": d["research_item_id"],
            "previous_decision": previous,
            "new_decision": decision,
            "researcher_approved": item["researcher_approved"],
            "reviewer_id": reviewer_id,
            "reviewer_role": reviewer_role,
            "timestamp": timestamp,
            "notes": note,
            "version": item["current_version"],
        })

    refresh_counts(record, reviewer_id, reviewer_role, timestamp)
    return events


def refresh_counts(record: dict, reviewer_id=None, reviewer_role=None, timestamp=None) -> None:
    items = record["items"]
    counts = record.setdefault("counts", {})
    counts["total"] = len(items)
    for key, val in (("pending", "PENDING"), ("keep", "KEEP"),
                     ("revise", "REVISE"), ("reject", "REJECT")):
        counts[key] = sum(1 for i in items if i["review_decision"] == val)
    counts["approved"] = sum(1 for i in items if i["researcher_approved"])
    counts["revision_records"] = sum(1 for i in items if i.get("revision_request"))

    if timestamp:
        record["last_updated"] = timestamp
    if reviewer_id or reviewer_role:
        registry = record.setdefault("reviewer_registry", [])
        entry = {"reviewer_id": reviewer_id, "reviewer_role": reviewer_role}
        if entry not in registry:
            registry.append(entry)

    decided = counts["keep"] + counts["revise"] + counts["reject"]
    record["review_complete"] = (counts["pending"] == 0)
    record["status"] = (
        "REVIEW_COMPLETE" if counts["pending"] == 0
        else ("REVIEW_IN_PROGRESS" if decided else "AWAITING_HUMAN_REVIEW")
    )


def append_history(path: Path, events: list[dict]) -> None:
    """Append-only. Never rewrites or truncates existing history."""
    with path.open("a", encoding="utf-8") as fh:
        for event in events:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--decisions", required=True, help="file of researcher decision lines")
    ap.add_argument("--reviewer-id", default=None)
    ap.add_argument("--reviewer-role", default=None)
    ap.add_argument("--timestamp", required=True, help="ISO-8601 review timestamp")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    review_path = root / "results" / "dataset_audit" / "phase7e_review.json"
    history_path = root / "results" / "dataset_audit" / "phase7e_review_history.jsonl"
    snap_dir = root / "results" / "dataset_audit" / "snapshots"

    record = json.loads(review_path.read_text(encoding="utf-8"))
    try:
        decisions = parse_decisions(Path(args.decisions).read_text(encoding="utf-8"))
        events = apply_decisions(record, decisions, args.reviewer_id,
                                 args.reviewer_role, args.timestamp)
    except DecisionError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"dry run: {len(events)} decision(s) would be recorded; nothing written")
        for e in events:
            print(f"  {e['research_item_id']}: {e['previous_decision']} -> {e['new_decision']}")
        return 0

    # Snapshot before writing; never destroy a prior state.
    snap_dir.mkdir(parents=True, exist_ok=True)
    snap = snap_dir / f"phase7e_review.{args.timestamp.replace(':', '')}.json"
    if snap.exists():
        print(f"CONFLICT: snapshot {snap.name} already exists; refusing to overwrite",
              file=sys.stderr)
        return 1
    shutil.copy(review_path, snap)

    review_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    append_history(history_path, events)

    c = record["counts"]
    print(f"recorded {len(events)} decision(s); snapshot: {snap.name}")
    print(f"pending={c['pending']} keep={c['keep']} revise={c['revise']} "
          f"reject={c['reject']} approved={c['approved']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
