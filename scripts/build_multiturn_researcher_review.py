"""Phase 7C-REVIEW researcher-friendly review interface builder."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_researcher_design import (  # noqa: E402
    DESIGN_FIELDS,
    validate_design,
)


DEFAULT_DESIGN = ROOT / "dataset" / "pilot" / "multiturn" / "design_specification.json"
DEFAULT_REVIEW = ROOT / "results" / "dataset_audit" / "multiturn_researcher_review.json"
DEFAULT_MARKDOWN = ROOT / "docs" / "multiturn_researcher_review.md"
VALID_DECISIONS = {"PENDING", "KEEP", "REVISE", "REJECT"}


def load_json(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON nesne olmalı: {path}")
    return value


def _design_snapshot(row: dict[str, Any]) -> dict[str, Any]:
    return {field: copy.deepcopy(row[field]) for field in DESIGN_FIELDS}


def build_review_spec(design: dict[str, Any]) -> dict[str, Any]:
    design_validation = validate_design(design)
    if design_validation["status"] != "valid":
        raise ValueError("Design specification geçersiz; review üretilemez")
    entries = []
    for row in design["rows"]:
        snapshot = _design_snapshot(row)
        entries.append({
            "sample_id": row["sample_id"],
            "original_version": design["design_version"],
            "revised_version": None,
            "original_design": snapshot,
            "current_design": copy.deepcopy(snapshot),
            "review_decision": "PENDING",
            "researcher_approved": False,
            "researcher_notes": None,
            "revision_reason": None,
            "researcher_decision": None,
            "revised_review_decision": None,
        })
    category_distribution = Counter(entry["current_design"]["category"] for entry in entries)
    effect_distribution = Counter(entry["current_design"]["expected_context_effect"] for entry in entries)
    return {
        "review_version": "0.1.0",
        "phase": "7C-REVIEW",
        "status": "pending_researcher_review",
        "language": "en",
        "source_design_version": design["design_version"],
        "source_design_path": "dataset/pilot/multiturn/design_specification.json",
        "researcher_approval_required": True,
        "category_distribution": dict(category_distribution),
        "context_effect_distribution": dict(effect_distribution),
        "entries": entries,
        "revision_policy": {
            "preserve_original_design": True,
            "new_version_required_for_revision": True,
            "automatic_approval": False,
            "rejected_requires_new_review": True,
        },
    }


def make_revision_entry(
    entry: dict[str, Any],
    revised_fields: dict[str, Any],
    revision_reason: str,
    revised_version: str,
) -> dict[str, Any]:
    """Create a pending revision while retaining the original design snapshot."""

    if entry.get("review_decision") != "REVISE":
        raise ValueError("Revision yalnızca REVISE kararından sonra oluşturulabilir")
    if not revision_reason.strip() or not revised_version.strip():
        raise ValueError("Revision reason ve revised version gerekli")
    unknown = set(revised_fields) - set(DESIGN_FIELDS)
    if unknown:
        raise ValueError(f"Bilinmeyen revised design alanları: {sorted(unknown)}")
    revised = copy.deepcopy(entry)
    revised["current_design"] = copy.deepcopy(entry["current_design"])
    revised["current_design"].update(copy.deepcopy(revised_fields))
    revised["revised_version"] = revised_version
    revised["revision_reason"] = revision_reason
    revised["review_decision"] = "PENDING"
    revised["researcher_approved"] = False
    revised["researcher_notes"] = None
    revised["researcher_decision"] = None
    revised["revised_review_decision"] = None
    return revised


def validate_review(review: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    entries = review.get("entries")
    if review.get("status") != "pending_researcher_review":
        errors.append("review status researcher review bekliyor olmalı")
    if not isinstance(entries, list) or len(entries) != 50:
        errors.append("review tam olarak 50 entry içermeli")
        entries = entries if isinstance(entries, list) else []
    sample_ids: set[str] = set()
    category_counts: Counter[str] = Counter()
    effect_counts: Counter[str] = Counter()
    pending_count = 0
    approval_count = 0
    for index, entry in enumerate(entries):
        path = f"entries[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{path}: nesne olmalı")
            continue
        sample_id = entry.get("sample_id")
        if not isinstance(sample_id, str) or not sample_id:
            errors.append(f"{path}.sample_id eksik")
        elif sample_id in sample_ids:
            errors.append(f"{path}: duplicate sample_id {sample_id}")
        else:
            sample_ids.add(sample_id)
        decision = entry.get("review_decision")
        if decision not in VALID_DECISIONS:
            errors.append(f"{path}.review_decision geçersiz")
        if decision == "PENDING":
            pending_count += 1
        approved = entry.get("researcher_approved")
        if not isinstance(approved, bool):
            errors.append(f"{path}.researcher_approved boolean olmalı")
        if approved:
            approval_count += 1
            if decision not in {"KEEP", "REVISE"}:
                errors.append(f"{path}: {decision} kararı researcher_approved=true olamaz")
            if entry.get("researcher_decision") != "APPROVED":
                errors.append(f"{path}: approval için researcher_decision APPROVED gerekli")
            if decision == "REVISE" and entry.get("revised_review_decision") != "KEEP":
                errors.append(f"{path}: revised approval için revised_review_decision KEEP gerekli")
        if decision == "REJECT" and approved:
            errors.append(f"{path}: rejected sample otomatik approved olamaz")
        if decision == "REVISE":
            if not isinstance(entry.get("revised_version"), str) or not entry["revised_version"]:
                errors.append(f"{path}: REVISE için revised_version gerekli")
            if not isinstance(entry.get("revision_reason"), str) or not entry["revision_reason"].strip():
                errors.append(f"{path}: REVISE için revision_reason gerekli")
            if entry.get("revised_version") == entry.get("original_version"):
                errors.append(f"{path}: revised_version original_version ile aynı olamaz")
        else:
            if entry.get("revised_version") is not None or entry.get("revision_reason") is not None:
                errors.append(f"{path}: revision metadata yalnızca REVISE için kullanılabilir")
        if entry.get("researcher_notes") is not None and not isinstance(entry["researcher_notes"], str):
            errors.append(f"{path}.researcher_notes string veya null olmalı")
        original = entry.get("original_design")
        current = entry.get("current_design")
        if not isinstance(original, dict) or not isinstance(current, dict):
            errors.append(f"{path}: original_design/current_design gerekli")
            continue
        if set(original) != set(DESIGN_FIELDS) or set(current) != set(DESIGN_FIELDS):
            errors.append(f"{path}: design snapshot alanları hatalı")
        if decision != "REVISE" and original != current:
            errors.append(f"{path}: revision olmadan current_design değişemez")
        category_counts[current.get("category")] += 1
        effect_counts[current.get("expected_context_effect")] += 1
    if pending_count != 50:
        errors.append(f"initial review'da 50 PENDING entry bekleniyor: {pending_count}")
    if approval_count != 0:
        errors.append(f"initial review'da approval olmamalı: {approval_count}")
    if sum(category_counts.values()) != 50:
        errors.append("category toplamı 50 değil")
    if sum(effect_counts.values()) != 50:
        errors.append("context-effect toplamı 50 değil")
    return {
        "phase": "7C-REVIEW",
        "review_validation_version": "0.1.0",
        "status": "valid" if not errors else "invalid",
        "entries_checked": len(entries),
        "unique_sample_ids": len(sample_ids),
        "pending_samples": pending_count,
        "approved_samples": approval_count,
        "category_distribution": dict(category_counts),
        "context_effect_distribution": dict(effect_counts),
        "errors": errors,
        "full_conversations_generated": 0,
        "model_evaluations_run": 0,
    }


def render_markdown(review: dict[str, Any], validation: dict[str, Any]) -> str:
    lines = [
        "# Phase 7C-REVIEW — Researcher-friendly design review",
        "",
        "Bu belge, İngilizce primary multi-turn dataset için 50 AI-proposed design satırının insan tarafından gözden geçirilmesi içindir. Full conversation henüz oluşturulmamıştır.",
        "",
        f"Durum: `{review['status']}` · Validation: `{validation['status']}` · Pending: **{validation['pending_samples']}** · Approved: **{validation['approved_samples']}**",
        "",
        "`CATEGORY` ve `EXPECTED_CONTEXT_EFFECT` farklı eksenlerdir. Category araştırma hücresini; expected context effect ise bağlamın yorum üzerindeki tasarım beklentisini gösterir. Dağılımları birbirine eşit olmak zorunda değildir.",
        "",
        "| sample_id | category | scenario_description | context_mechanism | final_prompt_intent | expected_context_effect | expected_risk_profile | design_confidence | proposed_turn_count | review_decision | researcher_notes |",
        "|---|---|---|---|---|---|---|---|---:|---|---|",
    ]
    for entry in review["entries"]:
        design = entry["current_design"]
        def clean(value: Any) -> str:
            return str(value).replace("|", "\\|").replace("\n", " ")
        notes = "null" if entry["researcher_notes"] is None else clean(entry["researcher_notes"])
        lines.append("| " + " | ".join([
            clean(entry["sample_id"]),
            clean(design["category"]),
            clean(design["scenario_description"]),
            clean(design["context_mechanism"]),
            clean(design["final_prompt_intent"]),
            clean(design["expected_context_effect"]),
            clean(design["expected_risk_profile"]),
            clean(design["design_confidence"]),
            clean(design["intended_turn_count"]),
            clean(entry["review_decision"]),
            notes,
        ]) + " |")
    lines.extend([
        "",
        "## Review kararları",
        "",
        "Her satır için `PENDING`, `KEEP`, `REVISE` veya `REJECT` kullanılabilir. İlk review çıktısında tüm kararlar `PENDING`, notes alanları `null` ve `researcher_approved=false` durumundadır.",
        "",
        "- `KEEP`: Araştırmacı tasarımı onayladıktan sonra approved durumuna geçebilir.",
        "- `REVISE`: Original design korunur; revised version ve revision reason eklenir, ardından yeni review gerekir.",
        "- `REJECT`: Kayıt approved olamaz; yeniden değerlendirme için yeni review/version gerekir.",
        "- `AI_PROPOSED`, `RESEARCHER_APPROVED` ve `MODEL_OBSERVED` birbirinden ayrı aşamalardır.",
    ])
    return "\n".join(lines) + "\n"


def write_outputs(review: dict[str, Any], validation: dict[str, Any]) -> None:
    DEFAULT_REVIEW.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    DEFAULT_MARKDOWN.write_text(render_markdown(review, validation), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Phase 7C researcher review interface")
    parser.add_argument("--design", type=Path, default=DEFAULT_DESIGN)
    args = parser.parse_args()
    design = load_json(args.design)
    review = build_review_spec(design)
    validation = validate_review(review)
    write_outputs(review, validation)
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
