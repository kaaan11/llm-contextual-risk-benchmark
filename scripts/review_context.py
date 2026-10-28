#!/usr/bin/env python3
"""Phase 7G — Interactive Context & Safety Review CLI Wizard.

Displays full multi-turn conversational context (B: legitimating, C: incriminating,
D: filler) for items that have completed blind isolated-prompt review, allowing
the researcher to record context relevance, naturalness, and safety reviews.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from scripts.apply_phase7g_annotations import (
    BLIND,
    HISTORY,
    KEY,
    QC,
    QCError,
    SNAPS,
    _load,
    append_history,
    blind_item_eligible_for_context,
    blind_item_for,
    record_context,
    snapshot,
)
from scripts.review_store import commit_state_and_history, review_lock
from scripts.refresh_phase7g_rollups import main as refresh_rollups

STIMULI_PATH = ROOT / "dataset" / "pilot" / "multiturn" / "stimulus_dataset_v1.json"


def get_stimuli_map() -> dict[str, dict]:
    data = json.loads(STIMULI_PATH.read_text(encoding="utf-8"))
    return {r["research_item_id"]: r for r in data["records"]}


def get_pending_context_items(qc: dict, blind: dict, key: dict) -> list[dict]:
    """Items whose blind record is ADJUDICATED but whose context review is open.

    Same fail-closed bound as the record API (record_context): single-rater,
    pending and unresolved records are never listed. Items with a broken blind
    mapping are skipped here; the validator flags them separately.
    """
    pending = []
    for item in qc.get("items", []):
        rid = item["research_item_id"]
        try:
            blind_item = blind_item_for(blind, key, rid)
        except QCError:
            continue
        eligible, _ = blind_item_eligible_for_context(blind_item)
        if eligible:
            if item.get("context_review", {}).get("status") != "COMPLETE":
                pending.append(item)
    return pending


def format_turns(turns: list[dict]) -> str:
    lines = []
    for t in turns[:-1]:  # preceding turns only
        role = t["role"].upper()
        text = t["content"]["text"]
        lines.append(f"  [{role}]: {text}")
    return "\n".join(lines) if lines else "  (Tek turlu - bağlam yok)"


def run_context_wizard(
    reviewer_id: str,
    reviewer_role: str | None = None,
    limit: int | None = None,
    input_func=input,
) -> int:
    qc = _load(QC)
    blind = _load(BLIND)
    key = _load(KEY)
    stimuli = get_stimuli_map()

    pending = get_pending_context_items(qc, blind, key)
    total = len(pending)

    if total == 0:
        print("✓ Bağlam incelemesi bekleyen (ve kör incelemesi tamamlanmış) madde bulunmamaktadır.")
        return 0

    print("=" * 72)
    print(f"Phase 7G Bağlam ve Güvenlik İnceleme Sihirbazı — İnceleyen: {reviewer_id}")
    print(f"İncelenecek Madde Sayısı: {total}")
    print("=" * 72)
    print("Seçenekler: [1..3] Karar | [q] Çıkış\n")

    recorded_count = 0

    for idx, item in enumerate(pending, start=1):
        if limit is not None and recorded_count >= limit:
            break

        rid = item["research_item_id"]
        stimulus = stimuli.get(rid, {})
        conditions = stimulus.get("conditions", {})

        prompt = stimulus.get("canonical_final_prompt", "")
        b_turns = conditions.get("full_context_legitimating", {}).get("turns", [])
        c_turns = conditions.get("full_context_incriminating", {}).get("turns", [])
        d_turns = conditions.get("neutral_filler", {}).get("turns", [])

        print("\n" + "─" * 72)
        print(f"[{idx}/{total}] ARAŞTIRMA MADDESİ: {rid}")
        print(f"Nihai Prompt (Değişmez):\n\"{prompt}\"\n")

        print("--- [B] MEŞRU BAĞLAM (Legitimating Context) ---")
        print(format_turns(b_turns))

        print("\n--- [C] RİSKLİ/ŞÜPHELİ BAĞLAM (Incriminating Context) ---")
        print(format_turns(c_turns))

        if d_turns:
            print("\n--- [D] NÖTR DOLGU (Filler Context) ---")
            print(format_turns(d_turns))

        print("\n" + "·" * 40)
        # 1. Context Material
        print("1. Bağlam Anlamlı ve İlgili mi? (context_is_material)")
        print("   [1] true (evet) | [2] false (hayır) | [3] unclear (belirsiz)")
        mat_in = None
        while mat_in not in {"1", "2", "3", "q"}:
            mat_in = input_func("Seçim [1-3 veya q]: ").strip().lower()
            if mat_in == "q":
                print("\nOturum kaydedildi ve sonlandırıldı.")
                return recorded_count
        mat_val = {"1": "true", "2": "false", "3": "unclear"}[mat_in]

        # 2. Naturalness
        print("2. Doğallık Düzeyi (naturalness)")
        print("   [1] high (yüksek) | [2] medium (orta) | [3] low (düşük)")
        nat_in = None
        while nat_in not in {"1", "2", "3", "q"}:
            nat_in = input_func("Seçim [1-3 veya q]: ").strip().lower()
            if nat_in == "q":
                print("\nOturum kaydedildi ve sonlandırıldı.")
                return recorded_count
        nat_val = {"1": "high", "2": "medium", "3": "low"}[nat_in]
        nat_notes = None
        if nat_val == "low":
            while not nat_notes:
                nat_notes = input_func("Düşük doğallık gerekçesi (zorunlu): ").strip()

        # 3. Safety Status
        print("3. Güvenlik Durumu (Zararlı operasyonel bilgi, gerçek credential vb. içeriyor mu?)")
        print("   [1] PASS (Güvenli / Zararlı içerik yok) | [2] FAIL (Güvensiz)")
        safe_in = None
        while safe_in not in {"1", "2", "q"}:
            safe_in = input_func("Seçim [1-2 veya q]: ").strip().lower()
            if safe_in == "q":
                print("\nOturum kaydedildi ve sonlandırıldı.")
                return recorded_count
        safe_val = {"1": "PASS", "2": "FAIL"}[safe_in]
        safe_notes = None
        if safe_val == "FAIL":
            while not safe_notes:
                safe_notes = input_func("Güvenlik ihlali açıklaması (zorunlu): ").strip()

        note_in = input_func("Genel İnceleme Notu (isteğe bağlı): ").strip()

        notes_dict = {}
        if mat_val in {"true", "unclear"}:
            notes_dict["context_is_material"] = note_in or "evaluated as material in human qc"

        payload = {
            "research_item_id": rid,
            "context_relevance": {"context_is_material": mat_val},
            "naturalness": nat_val,
            "naturalness_notes": nat_notes,
            "safety_status": safe_val,
            "safety_notes": safe_notes,
            "notes": notes_dict,
        }

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        events = record_context(
            qc,
            blind,
            key,
            [payload],
            reviewer_id=reviewer_id,
            reviewer_role=reviewer_role,
            timestamp=timestamp,
        )

        clean_stamp = timestamp.replace(":", "")
        snap = SNAPS / f"phase7g_human_qc.{clean_stamp}.json"
        commit_state_and_history(QC, qc, HISTORY, events, snap)
        refresh_rollups()
        recorded_count += 1
        print(f"✓ {rid} için bağlam ve güvenlik incelemesi kaydedildi.")

    print(f"\nİşlem tamamlandı: {recorded_count} adet madde incelendi.")
    return recorded_count


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Phase 7G Interactive Context & Safety Review CLI")
    parser.add_argument("--reviewer-id", required=True, help="Unique identifier of the researcher")
    parser.add_argument("--reviewer-role", default="researcher_qc", help="Optional role description")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of items to review this run")

    args = parser.parse_args(argv)
    with review_lock(QC.parent):
        run_context_wizard(args.reviewer_id, args.reviewer_role, limit=args.limit)


if __name__ == "__main__":
    main()
