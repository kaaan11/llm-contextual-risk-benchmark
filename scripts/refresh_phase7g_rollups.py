#!/usr/bin/env python3
"""Phase 7G — regenerate the quality-summary roll-up from canonical live records.

F-03 remediation: `phase7g_quality_summary.json` is a DERIVED artifact. The only
canonical sources are `phase7g_blind_review.json` (blind annotations) and
`phase7g_human_qc.json` (reviews/decisions). This script deterministically
rebuilds the summary from those two records and stamps the regeneration.

It never mutates the live records, never invents annotations or decisions, and
performs no network access and calls no model API. Run this after any
apply_phase7g_annotations.py invocation; validate_phase7g_review.py fails when
the roll-up drifts from the live records.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_phase7g_review import build_quality_summary  # noqa: E402

AUDIT = ROOT / "results" / "dataset_audit"
SUMMARY = AUDIT / "phase7g_quality_summary.json"


def refresh(audit_dir: Path = AUDIT, summary_path: Path = SUMMARY) -> int:
    blind = json.loads((audit_dir / "phase7g_blind_review.json").read_text(encoding="utf-8"))
    qc = json.loads((audit_dir / "phase7g_human_qc.json").read_text(encoding="utf-8"))

    recheck = qc.get("structural_verification_summary", {})
    summary = build_quality_summary(qc, blind, recheck)

    # --- F-03: replace build-time placeholders with live derivations ---------
    bitems = blind["items"]
    annotated = [i for i in bitems if i["annotation_status"] != "PENDING"]
    dist: dict[str, int] = {}
    for i in bitems:
        for rater in ("rater_a", "rater_b"):
            v = i[rater].get("isolated_prompt_valence_observed")
            if v:
                dist[v] = dist.get(v, 0) + 1
    valence_scale = blind.get("valence_scale") or list(dist)
    summary["isolated_prompt_review"] = {
        "annotations_submitted": len(annotated),
        "valence_distribution": {v: dist.get(v, 0) for v in valence_scale},
        "gate_failures": sorted(i["blind_id"] for i in bitems if i.get("gate_flag") == "ISOLATED_VALENCE_GATE_FAIL"),
        "gate_review_flags": sorted(i["blind_id"] for i in bitems if i.get("gate_flag") == "ISOLATED_VALENCE_GATE_REVIEW"),
        "adjudications": sum(1 for i in bitems if bool(i.get("adjudicated_by"))),
        "note": (
            "Derived from phase7g_blind_review.json."
            if annotated else
            "No blind annotations have been supplied; distribution is necessarily empty."),
    }
    summary["inter_rater"] = blind["two_rater_protocol"]
    summary["phase_complete"] = qc.get("phase_complete", False)
    summary["completion_blocker"] = (
        "Phase 7G is COMPLETE." if qc.get("phase_complete") else
        "Phase 7G requires explicit human review decisions for all research items, "
        "under the two-rater mandate every item needs two independent blind ratings "
        f"and agreement or recorded adjudication before KEEP. Current state: "
        f"{len(annotated)}/{len(bitems)} blind annotations submitted "
        f"({sum(1 for i in bitems if i['annotation_status'] == 'ADJUDICATED')} ADJUDICATED), "
        f"{qc['counts']['pending']} decision(s) PENDING."
    )
    items = qc["items"]
    summary["context_review"] = {
        "completed": sum(1 for i in items if i["context_review"]["status"] == "COMPLETE"),
        "relevance_failures": sorted(i["research_item_id"] for i in items
                                     if "CONTEXT_NOT_MATERIAL" in i.get("quality_flags", [])
                                     or "CONTEXT_ARTIFICIAL" in i.get("quality_flags", [])),
        "leakage_findings": sorted(i["research_item_id"] for i in items
                                   if "CONTEXT_LEAKAGE" in i.get("quality_flags", [])),
    }
    summary["naturalness"] = {
        "completed": sum(1 for i in items if i["naturalness_review"]["status"] == "COMPLETE"),
        "low_flags": sorted(i["research_item_id"] for i in items
                            if "NATURALNESS_LOW" in i.get("quality_flags", [])),
    }
    summary["safety"].update({
        "human_review_completed": sum(1 for i in items
                                      if i["safety_review"]["status"] == "COMPLETE"),
        "human_safety_failures": sorted(i["research_item_id"] for i in items
                                        if "SAFETY_FAIL" in i.get("quality_flags", [])),
    })
    flags: dict[str, int] = {}
    for i in items:
        for f in i.get("quality_flags", []):
            flags[f] = flags.get(f, 0) + 1
    summary["quality_flags_raised"] = dict(sorted(flags.items()))
    revisions = [i for i in items if i.get("revision_request")]
    summary["versioning"] = {
        "revisions_created": len(revisions),
        "items_at_version_2": sum(1 for i in revisions
                                  if i.get("current_stimulus_version", 1) >= 2),
        "re_reviews_required": sum(1 for i in revisions
                                   if i["revision_request"].get("revision_status")
                                   == "pending_revision"),
    }

    summary["generated_at"] = (
        datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )
    summary["regenerated_by"] = "scripts/refresh_phase7g_rollups.py (F-03 remediation)"
    summary["derivation_note"] = (
        "Derived artifact: rebuilt from phase7g_blind_review.json and "
        "phase7g_human_qc.json. Those two files are the canonical sources; a "
        "validator cross-checks this file against them."
    )

    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_content = json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
    summary_bytes = summary_content.encode("utf-8")
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=summary_path.parent,
            prefix=f".{summary_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as tmp:
            tmp_path = Path(tmp.name)
            tmp.write(summary_bytes)
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_path, summary_path)
        tmp_path = None
    finally:
        if tmp_path is not None and tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass

    print(f"regenerated {summary_path.name}: "
          f"annotations_submitted="
          f"{summary['isolated_prompt_review']['annotations_submitted']}, "
          f"pending={summary['totals']['pending']}")
    return 0


def main() -> int:
    try:
        from scripts.review_store import review_lock
    except ModuleNotFoundError:
        from review_store import review_lock

    with review_lock(AUDIT):
        return refresh(AUDIT, SUMMARY)


if __name__ == "__main__":
    raise SystemExit(main())
